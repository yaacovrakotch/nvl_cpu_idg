#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Mtpl module
"""
from os.path import join, dirname, basename, exists
from collections import defaultdict, OrderedDict
from gadget.files import File
from gadget.errors import ErrorInput, ErrorUser, ErrorCockpit, confirm
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.tputil import noquote, tuple_modname, ti_disassemble, get_param, OtplFile, is_int, remove_ip
from gadget.dictmore import keys_atlevel, iter_levels
from itertools import chain
from pprint import pprint
import re


class Mtpl:
    """
    storage of mtpl data
    parser of mtpl files
    Design: one Mtpl() instance for entire TP
    """

    def __init__(self, tpobj):
        """
        :param tpobj: path to TP env file
        :type tpobj: tp.testprogram.TestProgram
        """
        # note: testinstance_name can be duplicated in different modules
        self.tdata = None           # {module: {testinstance_name: {key: value_string}}}     # raw data - non-evaluated. Always string.
        self.ttype = None           # {module: {testinstance_name: {key: True|False}}}       # True if literal; False for expr
        self.edata = None           # {module: {testinstance_name: {key: value_evaluated}}}. Assigned in eval_params()
        self._modfolder2mod = None  # {ModuleFolderName: module} module is TestPlan name.
        self._mod2fname = None      # {module: mtpl_file_path} module is TestPlan name
        self._mttdata = None        # {module: {mtt_name: {key: value}}}
        self._import = None         # {module: [list_of_import_lines]}
        # self._comment and self._eol     # Call self.read_comments()

        # self._mttdata = {module: {name: {'TrialVariable': 'value',
        #                                  'TrialVariableExitAction': 'value',
        #                                  'TrialTest': 'value_with_template',
        #                                  'TrialResult': {-2: {'Return|TrialAction'}}}
        #                                  'TrialParam': set_of_params,

        # flow data
        # 'module::subflow': {_ORDER : ['list of dutflowitemname'],
        #                     dutflowitemname : {999: <loc|testinstancename>,
        #                                          0:  {'PassFail': <value>}}
        self._dutflow = None
        self._dutflow_order = None    # OrderedDict {subflow: <DUTFlow|Flow|ConcurrentFlow>}. ie, keys of self._dutflow in order
        self._dutflow_at = None       # {(dutflow, dutflowitem): '@<text>'}, if exist
        self._dutflow_info = None     # {(dutflow, dutflowitem): {<attrib>: <value>}, if exist

        self._tn_per_mod = {}   # cache dict for regex: {module: <long_string_testnames>}
        self._is_tn_attrib = False
        self.read_edc_setbin = False

        # the rest of attributes
        self.tpobj = tpobj
        self.envfile = tpobj.envfile

    def init_read(self):
        """Initialize by reading the .mtpl. This is not full init since usrv and eval needs to happen"""
        self.read_mtpls()
        self.read_mtpl_flow()

    def read_mtpls(self, modules=None):
        """
        Read all mtpls from stpls specified in tpobj. Default.
        Populate testinstance_name

        :param modules: List of module names to read (optional)
        """
        assert not (modules and self.tdata), "Data is already populated in mtpl object. Call read_mtpls() at start."
        if self.tdata:
            return
        self.tdata = {}
        self.ttype = {}
        self._mttdata = {}
        self._import = {}
        self._modfolder2mod = {}
        self._mod2fname = {}
        for ff in self.tpobj.get_all_mtpl_from_stpl():
            self._read_mtpl_test(ff, modules)

    def read_mtpl_specific(self, list_mtpl, readflow=False):
        """
        Read given mtpls

        :param list_mtpl: list of mtpl filepaths
        """
        assert not self.tdata, "Data is already populated in mtpl object. Call read_mtpl_specific() at start"
        self.tdata = {}
        self.ttype = {}
        self._mttdata = {}
        self._import = {}
        self._modfolder2mod = {}
        self._mod2fname = {}
        self.init_dutflow()
        for ff in list_mtpl:
            if exists(ff):
                self._read_mtpl_test(ff, None)
                if readflow:
                    self._read_mtpl_flow(ff)
            elif exists(join(self.tpobj.tpldir, ff)):
                self._read_mtpl_test(join(self.tpobj.tpldir, ff), None)
            else:
                raise ErrorUser("Input mtpl [%s] does not exist" % ff,
                                "Pls specify valid mtpl file")

    def _read_mtpl_test(self, mtpl, modules):
        """
        Read one mtpl, put in tdata structure, all Test instances

        :param mtpl: mtpl file
        :param modules: List of module names to read
        """
        name = None
        vdata = None
        vtype = None
        mttdata = None
        is_edc = self.read_edc_setbin
        r_test = re.compile(r'^(CSharpTest|Test)\s+(\S+)\s+(\S+)')
        r_method = re.compile(r'^(\w+)\s*=\s*(\"[^\"]+\"|\S.*)\s*;$')
        r_testplan = re.compile(r'^TestPlan\s+(\S+);')
        r_trialresult = re.compile(r'^(\w+)\s*(.*);')
        module = basename(dirname(mtpl))     # initial value
        mtt = None
        trialresult = None
        oline = None
        import_list = []

        for lno, line in OtplFile(mtpl).readline(comments=is_edc):
            # Logic to ensure we only pass lines that have ##EDC## and not all comment lines
            if is_edc:
                if line.startswith('##EDC##'):
                    line = line.replace('##EDC##', '').lstrip()
                # Ignore line if it is just a regular comment
                elif line.startswith("#"):
                    continue
            # True Module name
            if line.startswith('TestPlan'):
                res = r_testplan.search(line)
                if res:
                    self._modfolder2mod[module] = res.group(1)
                    module = res.group(1)     # True module name
                    self._mod2fname[module] = mtpl

            # inside the block
            if name:
                # trialresult block
                if trialresult is not None and line not in ('}', '{'):
                    res = r_trialresult.search(line)
                    assert res, f'[{line}] is invalid for TrialResult block.'
                    mttdata['TrialResult'][trialresult][res.group(1)] = res.group(2)
                    continue

                # end block
                if line == '}':

                    if trialresult is not None:
                        trialresult = None
                        continue

                    # module init
                    if module not in self.tdata:
                        if modules and module not in modules:
                            return
                        self.tdata[module] = defaultdict(dict)
                        self.ttype[module] = defaultdict(dict)
                        self._mttdata[module] = defaultdict(dict)

                    self.tdata[module][name] = vdata
                    self.ttype[module][name] = vtype
                    self._mttdata[module][name] = mttdata
                    vdata = None
                    vtype = None
                    name = None
                    mtt = None
                    mttdata = None
                    trialresult = None
                    continue

                if line == '{' or line == ';':
                    continue

                if mtt:
                    oline = line
                    if line.startswith('TrialParam '):
                        line = line.replace('TrialParam ', '').lstrip()
                        mttdata['TrialParam'].add(line.split()[0])
                    if line.startswith('TrialResult '):    # end marker, do not process any further
                        trialresult = int(line.split()[1])
                        mttdata['TrialResult'][trialresult] = {}
                        continue

                res = r_method.search(line)
                if res:
                    value = res.group(2).strip()
                    key = res.group(1)

                    # case sensitivity
                    if key == 'Patlist':
                        key = 'patlist'

                    # update mtt lines to include the _MTT() function that return first element only
                    if mtt and oline.startswith('TrialParam '):
                        for _ in range(4):
                            new_value = remove_ip(value)
                            if new_value == value:
                                break
                            value = new_value
                        value = ExprParser.to_mtt(value)

                    noquote_value = noquote(value)
                    vtype[key] = bool(noquote_value != value)   # True for literal; False for expression
                    vdata[key] = noquote_value
                    continue
                else:
                    raise ErrorInput("Invalid line inside Test block %s: %r" % (name, line),
                                     "Pls check %s" % mtpl)

            # outside of block
            res = r_test.search(line)
            if res:
                name = res.group(3)
                vdata = {'TEMPLATE': res.group(2)}
                vtype = {'TEMPLATE': True}
                continue

            # multitrial
            if line.startswith('MultiTrialTest '):
                mtt = line.split()[1]
                mttdata = {'TrialParam': set(),
                           'TrialResult': {}}

            if line.startswith(('TrialVariable ', 'TrialVariableExitAction ')) and mtt:
                k, v = line.split(maxsplit=1)
                mttdata[k] = v

            if line.startswith(('TrialTest ', 'CSharpTrialTest')):
                name = mtt
                elems = line.split()
                vdata = {'TEMPLATE': elems[1]}
                vtype = {'TEMPLATE': True}
                mttdata[elems[0]] = line.split(maxsplit=2)[-1]
                continue

            if line.startswith('Import '):
                import_list.append(line)

        # end of for loop ===========================================
        self._import[module] = import_list

    def eval_params(self, info=True):
        """
        Evaluate all params. Will assign self.edata
        """
        tdata = self.tdata
        ttype = self.ttype
        usrv = self.tpobj.usrv

        sw = Elapsed()
        edata = {}
        ctr = 0
        for mod in tdata:
            edata[mod] = {}
            for tn in tdata[mod]:
                edata[mod][tn] = {}
                for param in tdata[mod][tn]:
                    assert param.startswith('_') or param in ttype[mod][tn], f'Error: param {param} is expected in {mod}::{tn}'
                    if param.startswith('_') or ttype[mod][tn][param]:
                        # assign as_is for literal or special var
                        edata[mod][tn][param] = tdata[mod][tn][param]
                    else:
                        ctr += 1
                        newdata = tdata[mod][tn][param]
                        if '_MTT(__shared__) ::' in tdata[mod][tn][param]:
                            newdata = newdata.replace('_MTT(__shared__) ::', '')
                        edata[mod][tn][param] = usrv.eval_param(newdata, mod, f'{mod} {tn} {param}')

        # special handling
        for mod, tn, param in iter_levels(edata, 3):
            # bypass port, since variables can be inside the literal string
            if param in ('BypassPort', 'bypass_global') and not isinstance(edata[mod][tn][param], int):
                ctr += 1
                edata[mod][tn][param] = usrv.eval_param(edata[mod][tn][param], mod, f'{mod} {tn} {param}')

        self.edata = edata
        log.info(f'-i- Eval TestInstance params count={ctr}, {sw}') if info else None

    def get_import_mtpl(self, module):
        """Return the list of import lines given module"""
        return self._import[module]

    def get_instance(self, module, tn, evaluated=False, both=False, mtt=False, _warn=set()):
        """
        Get one test instance. Note that evaluated|both|mtt are mutex, so choose only one.

        :param module: module name
        :param tn: testname
        :param evaluated: Return evaluated dict
        :param both: Return both raw and evaluated dict
        :param mtt: Set to True to return mtt (These are special params)
        :return: dict {key: value}
        """
        self.read_mtpls() if not self.tdata else None

        if module == 'BASE':  # pragma: no cover     # This is a hack - for hbi - There *should* be no testinstance in ProgramFlows.mtpl
            if tn not in _warn:
                _warn.add(tn)
                log.info(f"-w- {tn} is considered dummy since it is coming outside of Module/ area (ie, unsupported)")
            empty = {'TEMPLATE': ''}
            return (empty, empty) if both else empty

        assert module in self.tdata, f"Module [{module}] for [{tn}] is not found in {self.tpobj.moddir}"
        assert tn in self.tdata[module], f"TestInstance [{tn}] is not found in module {module}"

        ed = self.edata if self.edata else self.tdata        # for unittests, since edata does not exist yet
        if mtt:
            return self._mttdata[module].get(tn)     # returns None for non-mtt
        if both:
            return self.tdata[module][tn], ed[module][tn]
        if evaluated:
            return ed[module][tn]
        return self.tdata[module][tn]

    def set_instance(self, module, tn, param, val):
        """
        Set 1 or more test instance. Iterator
        self.edata is assumed to be called later.
        It is responsibility of set_instance() caller to evaluate the value!

        :param module: module name
        :param tn: testname
        :param param: param
        :param val: value
        :return orig value or None if no change
        """
        self.read_mtpls() if not self.tdata else None

        if '*' in module:
            for found in re.findall(module.replace('*', '.*'), '\n'.join(self.tdata), re.MULTILINE):
                if found in self.tdata:
                    for item in self.set_instance(found, tn, param, val):
                        yield item
            return    # Done

        assert module in self.tdata, f"Module [{module}] for [{tn}] is not found in {self.tpobj.moddir}"

        # if it is a regex
        if '*' in tn:
            if module not in self._tn_per_mod:
                self._tn_per_mod[module] = '\n'.join(self.tdata[module])

            for found in re.findall(tn.replace('*', '.*'), self._tn_per_mod[module], re.MULTILINE):
                if found in self.tdata[module]:
                    for item in self.set_instance(module, found, param, val):
                        yield item

            return   # Done

        # modify one tn
        assert tn in self.tdata[module], f"TestInstance [{tn}] is not found in module {module}"

        # check val, it can be uservar
        if val.startswith('_UserVars.') and param != 'expression':
            val = val.replace('_UserVars.', '')
            val = str(self.tpobj.usrv.get_var(val, testplan=module))

        # special case - bypass global, these param may not exist
        if param in ('bypass_global', 'BypassPort') and param not in self.tdata[module][tn]:
            self.tdata[module][tn][param] = '-1'
            self.ttype[module][tn][param] = True      # literal type

        orig = self.tdata[module][tn].get(param, None)
        if orig != val:
            self.tdata[module][tn][param] = val
            self.ttype[module][tn][param] = True     # Always literal
            yield orig, tn
        else:
            yield None, tn

    def iter_tests(self, template_name=None, key_name=None, edict=False):
        """
        Iterator: Return all testinstances (dictionary), connected or unconnected.
        To get specific templates, set template_name

        :param template_name: if specified, return testinstances with this template_name
        :param key_name: if specified, return testinstances that has key_name
        :param edict: if True, return evaluated value
        :return: (module, testinstance_name, testinstance-dictionary, tpobj)
        :rtype: tuple
        """
        self.read_mtpls()
        if edict:
            if not self.edata:
                self.eval_params()
            src = self.edata
        else:
            src = self.tdata

        for md in src:
            for testinstance in src[md]:
                if template_name and src[md][testinstance]['TEMPLATE'] != template_name:
                    continue
                if key_name and key_name not in src[md][testinstance]:
                    continue

                yield md, testinstance, src[md][testinstance], self.tpobj

    def get_modules(self) -> list:
        """
        Return all modules. This is the TestPlan name, not the Modulename folder.

        :return: sorted modules
        :rtype: list
        """
        self.read_mtpls()
        return sorted(self.tdata)

    def get_modfolder2mod(self) -> dict:
        """
        Return {module_folder_name: module_testplan_name}
        :return: dict
        """
        self.read_mtpls()
        return self._modfolder2mod

    def get_mod2fname(self) -> dict:
        """
        Return {module_test_plan_name: mtpl_file_path}
        :return: dict
        """
        self.read_mtpls()
        return self._mod2fname

    def get_subflows(self, include_composite=False):
        """
        Return set of subflows (and composites) defined in .mtpl (connected or unconnected)

        :param include_composite: If set to True, include all composites
        :return: set
        """
        if include_composite:
            return set(self._dutflow)
        else:
            return {x for x in self._dutflow if '::' not in x}

    def get_dutflow_map(self, order=False, at=False, info=False):
        """Return dutflow mapping dictionary"""
        if at:
            return self._dutflow_at
        elif info:
            return self._dutflow_info
        elif order:
            return self._dutflow_order
        else:
            return self._dutflow

    @classmethod
    def read_comments(cls, mtplfile):
        """
        Read mtplfile and returns:
        comment_dict= {testinstance_name: [list_of_comments]}
        eol_dict = {testinstance_name: {key: eol_comment}}

        :param mtplfile: Input mtpl file
        :return: comment_dict, eol_dict
        """
        close_lno = set()
        start_lno = {}    # {lno: name}
        nest = 0
        name = None

        # Derive the line number of the test blocks
        for lno, line in OtplFile(mtplfile).readline():

            if line == '{':
                nest += 1
            elif line == '}':
                nest -= 1
                if nest == 0:
                    name = None
                    close_lno.add(lno)

            elif line.startswith(('Test ', 'CSharpTest ')):
                name = line.split()[2]
                start_lno[lno] = name
            elif line.startswith('MultiTrialTest '):
                name = line.split()[1]
                start_lno[lno] = name

        # open the file normally
        comment_dict = defaultdict(list)
        eol_dict = defaultdict(dict)
        r_quotes = re.compile(r'("[^"]+")')
        r_eol = re.compile(r'(#.*)$')
        r_param = re.compile(r'^\s*(TrialParam\s+)?(\w+)\s*=')
        raw = File(mtplfile).raw(islist=True)
        for rawlno in range(len(raw)):
            line = raw[rawlno]
            lno = rawlno + 1
            if lno in start_lno:
                name = start_lno[lno]

            if name:
                tmpline = r_quotes.sub('', line)    # remove quotes
                res = r_eol.search(tmpline)
                if line.strip().startswith('#'):
                    comment_dict[name].append(raw[rawlno].strip())
                elif res:
                    res_param = r_param.search(line)
                    if res_param:
                        param = res_param.group(2)
                        eol_dict[name][param] = res.group(1)
                    else:
                        comment_dict[name].append(res.group(1))

            if lno in close_lno:
                name = None

        return comment_dict, eol_dict

    @classmethod
    def read_dutflow_comments(cls, mtplfile):
        """
        Read mtplfile and returns:
        comment_dict= {testinstance_name: [list_of_comments]}
        eol_dict = {testinstance_name: {key: eol_comment}}

        :param mtplfile: Input mtpl file
        :return: comment_dict, eol_dict
        """
        close_lno = set()
        start_lno = {}    # {lno: name}
        nest = 0
        name = None

        # Derive the line number of the test blocks
        for lno, line in OtplFile(mtplfile).readline():
            if line == '{':
                nest += 1
            elif line == '}':
                nest -= 1
                if nest == 0:
                    name = None
                    close_lno.add(lno)

            elif line.startswith(('FlowItem ', 'DUTFlowItem ')):
                name = line.split()[1]
                start_lno[lno] = name

        # open the file normally
        comment_dict = defaultdict(list)
        eol_dict = defaultdict(dict)
        r_quotes = re.compile(r'("[^"]+")')
        r_eol = re.compile(r'(#.*)$')
        r_param = re.compile(r'^\s*(Property\s+)?(\w+)\s*=')
        raw = File(mtplfile).raw(islist=True)

        for rawlno in range(len(raw)):
            line = raw[rawlno]

            lno = rawlno + 1
            if lno in start_lno:
                name = start_lno[lno]
            if name:
                tmpline = r_quotes.sub('', line)    # remove quotes
                res = r_eol.search(tmpline)
                if line.strip().startswith('#'):
                    comment_dict[name].append(raw[rawlno].strip())
                elif res:
                    res_param = r_param.search(line)
                    if res_param:
                        param = res_param.group(2)
                        eol_dict[name][param] = res.group(1)
                    else:
                        comment_dict[name].append(res.group(1))

            if lno in close_lno:
                name = None

        return comment_dict, eol_dict

    def is_bypassed(self, mod, tn, safe=True, dd=None):
        """
        Determine if mod+tn is bypassed or not (evaluated)

        :param mod: module
        :param tn: testname
        :param safe: Set to False to ignore variable bypass
        :param dd: Given dictionary (for performance)
        :return: True if mod+tn is bypassed
        """
        if not dd:
            src = self.edata
            assert mod in src, f'Error: mod=[{mod}] is unknown.'
            assert tn in src[mod], f'Error: testname=[{tn}] is not defined.'
            dd = src[mod][tn]      # use evaluated

        result = dd.get('bypass_global', dd.get('BypassPort', ''))

        # confirm value is ok
        assert isinstance(result, (str, int)), 'Error on %s: [%r] is not a string/int. Expecting string.' % (tn, result)
        assert (not safe) or isinstance(result, int) or is_int(result), \
            f'Error on {tn}: [{result}] is not a 1 or -1. Did you run init()?'

        if result == '':
            return False
        if isinstance(result, str) and (not is_int(result)):
            return False
        if int(result) == 1:
            return True
        if int(result) >= 0 and 'BypassPort' in dd:
            return True
        return False

    def _____flow_methods_below(self):
        """
        Divider only - unused
        :return:
        """

    def init_dutflow(self):
        """Initialize dutflow vars"""
        self._dutflow = {}
        self._dutflow_order = OrderedDict()
        self._dutflow_at = {}
        self._dutflow_info = defaultdict(dict)

    def read_mtpl_flow(self):
        """
        Read mtpl flows
        Design is one stpl only

        :return:
        """
        if self._dutflow:
            return

        self.init_dutflow()

        sw = Elapsed()
        set_mtpls = self.tpobj.get_all_mtpl_from_stpl()
        log.info('-i- Starting to read %s mtpls for flow.' % len(set_mtpls))

        for ff in sorted(set_mtpls):
            self._read_mtpl_flow(ff)

        self._read_mtpl_flow(self.tpobj.get_final_mtpl())
        log.info('-i- Completed flow read. Elapsed=%s' % sw)

    def _read_mtpl_flow(self, fname):
        """
        Read one mtpl file and populate self._dutflow

        # 0.315 sec to read 1.3M lines of mtpl, from /tmp
        # 1.333 Secs 277057 match, using re and groups()
        # 1.029 Secs 277057 match, using .startswith() and split
        #    however, this will not work if there is no space, and performance impact is negligilble, so keeping regex

        :param fname: Input file
        :return:
        """
        dutflow = None
        name = None
        result = None
        dfi = {}
        order = None
        is_edc = self.read_edc_setbin
        r_val = re.compile(r'^(IncrementCounters|SetBin|Return|GoTo)\s+(\S+)\s*;')
        r_coloncolon = re.compile(r'(\w::)\s+(\w)')

        # This works for both:
        #   Property PassFail = "Fail";
        #   PassFail Pass;
        r_pf = re.compile(r'^(Property\s+)?(PassFail)\s*(=\s*\")?(Fail|Pass)')

        # Generic key/value regex
        kvre = re.compile(r'(MinLoopDuration)\s+(\w+)')
        kv_semic = re.compile(r'(BreakLoopOn)\s+(.*);')

        scope = self.tpobj.get_scope(fname, "")

        for lno, line in OtplFile(fname).readline(comments=is_edc):
            # print(f'{lno} {line}')
            # Ignore these
            if line.startswith(('{', 'Version ', 'ProgramStyle ', 'TestPlan Flows')):
                continue

            # closure
            if line == '}':
                if result is not None:
                    # Check that the Result block has a PassFail property
                    if self.tpobj._unit_test_protocol >= 1:
                        confirm('PassFail' in dfi[result],
                                f"Result {result} at line#{lno} of {fname} is missing PassFail property.",
                                f"Expected either 'Property PassFail = \"Pass\";' or 'PassFail Pass;'")
                    result = None
                    continue

                if name:
                    assert name not in self._dutflow[dutflow], "%s already defined in line#%s" % (name, lno)
                    self._dutflow[dutflow][name] = dfi
                    dfi = {}
                    name = None
                    continue

                if dutflow:
                    self._dutflow[dutflow]['_ORDER'] = order
                    dutflow = None
                    order = None
                    continue

                # ignore the rest
                _coverage_only = True
                continue

            if line.startswith(('DUTFlow ', 'Flow ', 'ConcurrentFlow ')):
                assert not dutflow, f"dutflow is already defined in line#{lno} at {fname}"
                assert not name, f"DUTFlowItem is already defined in line#{lno} at {fname}"
                assert result is None, f"Result [{result}] is already defined in line#{lno} at {fname}"
                assert dutflow not in self._dutflow, f"dutflow={dutflow} is already defined in line#{lno} at {fname}"
                dutflow = line.split()[1]
                if scope:
                    dutflow = '%s::%s' % (scope, dutflow)
                self._dutflow[dutflow] = {}
                self._dutflow_order[dutflow] = line.split()[0]
                # parse in the dtag for a flow
                if '@' in line:
                    self._dutflow_at[(dutflow, name)] = line[line.index('@'):]
                order = []
                continue

            if line.startswith(('DUTFlowItem ', 'FlowItem ', 'LoopFlowItem ')):
                assert dutflow, f"dutflow is not defined in line#{lno} at {fname}"
                assert not name, f"DUTFlowItem is already defined in line#{lno} at {fname}"
                assert result is None, f"Result [{result}] is already defined in line#{lno} at {fname}"
                assert not dfi, "dfi is not empty in line#%s" % lno
                name_loc = line.replace('@', ' @').split()[1:3]
                assert len(name_loc) == 2, f"line {name_loc} in line#{lno} at {fname} is invalid, expecting 2 elements"
                name, loc = name_loc
                dfi[999] = loc

                if '@' in line:
                    self._dutflow_at[(dutflow, name)] = line[line.index('@'):]

                if 'MinLoopDuration' in line:
                    mld = kvre.search(line)
                    confirm(mld, f"Invalid line in line#{lno} at {fname}", f"Expecting regex: {kvre.pattern}")
                    self._dutflow_info[(dutflow, name)]['MinLoopDuration'] = mld.group(2)

                if '[DUTSync]' in line:
                    self._dutflow_info[(dutflow, name)]['DUTSync'] = True

                order.append(name)
                continue

            if line.startswith('BreakLoopOn'):
                assert dutflow and name, f"Either name or dutflow is not defined in line#{lno} at {fname}"
                value_breakloopon = kv_semic.search(line)
                confirm(value_breakloopon, f"Invalid line in line#{lno} at {fname}", f"Expecting regex: {kv_semic.pattern}")
                self._dutflow_info[(dutflow, name)]['BreakLoopOn'] = value_breakloopon.group(2)
                continue

            if line.startswith('ConcurrentFlowItem '):
                assert dutflow, f"dutflow is not defined in line#{lno} at {fname}"
                assert not name, f"DUTFlowItem is already defined in line#{lno} at {fname}"
                assert result is None, f"Result [{result}] is already defined in line#{lno} at {fname}"
                assert not dfi, "dfi is not empty in line#%s" % lno
                name, loc = line.split()[1:]
                loc = loc[:-1] if loc.endswith(';') else loc
                # Note: PassFail property check doesn't apply to auto-generated ConcurrentFlowItem results
                dfi = {999: loc,
                       0: {'Return': '0'},
                       1: {'Return': '1'}
                       }
                if order:   # 2nd item
                    self._dutflow[dutflow][order[-1]][1]['GoTo'] = name
                order.append(name)
                self._dutflow[dutflow][name] = dfi
                name = None
                dfi = {}
                continue

            if line.startswith('Result ') and name:
                assert dutflow and name, f"Either name or dutflow is not defined in line#{lno} at {fname}"
                assert result is None, f"Result [{result}] is already defined in line#{lno} at {fname}"
                result = int(line.split()[1])
                assert result != 999, f"Result 999 is reserved for special port. Can this be avoided?"
                dfi[result] = {}
                continue

            if name and dutflow and result is not None:
                # Property PassFail
                res = r_pf.search(line)
                if res:
                    dfi[result][res.group(2)] = res.group(4)
                    continue
                if is_edc:
                    if line.startswith('##EDC##'):
                        line = line.replace('##EDC##', '').lstrip()
                    elif line.startswith('#'):
                        continue
                # IncrementCounters|SetBin|Return|GoTo code block ====================
                res = r_val.search(line)
                if res:
                    dfi[result][res.group(1)] = res.group(2)
                    continue

                line = r_coloncolon.sub(r'\1\2', line)   # ":: " remove space after colon hack (LNL case), then try again

                res = r_val.search(line)
                if res:
                    dfi[result][res.group(1)] = res.group(2)
                    continue
                # end of code block ===================================================

                raise ErrorCockpit(f"Unknown mtpl flow line: [{line}] at line#{lno} of {fname}")

        assert not dutflow, f"Missing close bracket for DutFlow [{dutflow}] in EOF of {fname}"

    def dict_flows(self, keyparam=None, flowitem='MAIN'):
        """Return dictionary {(module, testname): P,F,B}. Pass, Fail or Bypass"""
        result = {}

        # All flows
        for key in self.iter_flows_multi(flowitem, passonly=False, bypass=False, keyparam=keyparam):
            result[key] = 'B'

        # all non-bypass
        for key in self.iter_flows_multi(flowitem, passonly=False, bypass=True, keyparam=keyparam):
            result[key] = 'F'

        # all non-bypass
        for key in self.iter_flows_multi(flowitem, passonly=True, bypass=True, keyparam=keyparam):
            result[key] = 'P'

        return result

    def iter_flows_multi(self, flowitems, **kwargs):
        """Iterate through multiple flows specified as comma-delimited string.

        :param flowitems: comma delimited string of flowitem
        :param kwargs: dict: same arguments as iter_flows
        :return: iter_flow results
        """
        for flowitem in flowitems.split(','):
            for result in self.iter_flows(flowitem, **kwargs):
                yield result

    def iter_flows(self,
                   flowitem='MAIN',   # Starting Subflow
                   keyparam=None,     # Return only instances with keyparam value (eg. keyparam='patlist')
                   template=None,     # Return only template=<name> (eg. template='iCFuncTest')
                   passonly=False,    # Set to True, or dictionary of {dutflowitem: portno} for forced port
                   uniq=True,         # Set to False to return all even duplicate module+testnames (first two elements)
                   bypass=False,      # Set to True to Skip bypass instances.
                   r_mod=None,        # Regex for specific module
                   # control of return values
                   idict=False,       # Set to True to return ti_dict: (md, tn, ti_dict)
                   pdict=False,       # Set to True to return portdict: (md, tn, port_dict)
                   edict=False,       # Set to True to return evaluated ti_dict: (md, tn, ti_dict)
                   flownames=False,   # Set to True to return (md, df, dfi) instead of (md, tn)
                   traceinfo=False):  # Set to True to return traceinfo dict as last element
        """
        Iterator: Traverse the flow, Returns (mod, testins_name)

        Options:
        (mod, testins_name):                           default
        (mod, testins_name, testins_dict):             idict=True
        (mod, testins_name, testins_dict, port_dict):  idict=True, pdict=True
        (mod, df-dutflow, dfi-dutflowitem):            flownames=True
        (mod, df, dfi, testins_dict):                  flownames=True, idict=True
        (mod, df, dfi, testins_dict, port_dict):       flownames=True, idict=True, pdict=True

        Default, it returns all connected flows

        :return: (module, instance_name, [traceinfo|instance_dict])
        :rtype: tuple
        """
        # Performance: total=33202 (uniq=False) ~0.39 Secs (14P all flows)
        self.read_mtpl_flow()
        assert flowitem in self._dutflow, f'[{flowitem}] is not found in any subflows'

        if isinstance(passonly, dict) and passonly:
            passonly_dd = passonly

            # make sure all items exist
            level2 = set(keys_atlevel(self._dutflow, 1))
            for item in passonly:
                assert item in level2, f"Error: input passonly flowitem=[{item}] does not exist."

        elif passonly:
            passonly_dd = {'_PASSONLY': 0}
        else:
            passonly_dd = {}

        seen = set()
        trcinput = [flowitem] if traceinfo else None
        for dutflow, dutflowitem, trc in self._recurse_flow(flowitem, trcinput, '', set(), passonly_dd):
            md, tn = self.get_flow_instance(dutflow, dutflowitem)
            dd, ed = self.get_instance(md, tn, both=True)   # This will raise exception if there is problem on instance

            if keyparam and keyparam not in dd:
                continue

            if template and dd['TEMPLATE'] != template:
                continue

            if bypass and self.is_bypassed(md, tn, dd=ed):
                continue

            if r_mod and (not r_mod.search(md)):
                continue

            # key is used in uniq
            if flownames:
                key = (md, dutflow, dutflowitem)
            else:
                key = (md, tn)       # default

            # ret is the final return value
            ret = key
            if idict or edict:
                if edict:
                    ret = ret + (ed, )
                else:
                    ret = ret + (dd, )
            if pdict:
                ret = ret + (self._dutflow[dutflow][dutflowitem], )
            if traceinfo:
                ret = ret + (trc, )

            # do uniq stuff
            if key not in seen:
                seen.add(key)
                if uniq:
                    yield ret

            if not uniq:
                yield ret

    def _fix_target(self, target, module):
        """Fix target, this is value of dfi[flowitem][999]"""

        # try to add the module_scope, and if it exist use it
        if '::' not in target:
            tryloc = f'{module}::{target}'
            if tryloc in self._dutflow:
                return tryloc

        # remove ipscope, if exist, since this is not in self._dutflow
        if target.count('::') == 2:
            tokens = target.split('::')
            return f'{tokens[1]}::{tokens[2]}'

        return target    # return as-is

    # Performance, 5/29/21, 35H TP
    # Reading: -i- Completed flow read. Elapsed=1.757 Secs
    # All flows: total=35044 0.224 Secs
    def _recurse_flow(self, subflow, trace, md, seen, passonly, flowitem=None):
        """
        Iterator: yield test instances in pass flow
        :param subflow: DutFlow name (first key in self._dutflow)
        :param trace: trace info (list) or None
        :param md: module
        :param seen: set of (subflow, flowitem), to indicate that it is already traversed
        :param passonly: If set, will traverse to passflow only. passonly is a dictionary,
                         so it can be set to specific port.
        :param flowitem: specific flowitem|DutFlowItem to use. Used with traverse all ports
        :return: dutflow, dutflowitem, list_trace_info
        """
        # print(f'subflow={subflow} md={md} flowitem={flowitem} trace={trace}')

        dfi = self._dutflow[subflow]     # dfi: dut_flow_item dictionary
        if not flowitem:
            if not dfi['_ORDER']:
                return      # The DUTFlow block is empty
            flowitem = dfi['_ORDER'][0]
        if (subflow, flowitem) in seen:
            return        # Do nothing if it's already seen, only for ALL flows
        seen.add((subflow, flowitem))

        seenloop = set()
        for ii in range(10000):
            if (subflow, flowitem) in seenloop:
                break
            seenloop.add((subflow, flowitem))
            assert flowitem in dfi, f'[{flowitem}] is called but not defined as a DUTFlowItem. This is syntax error.'
            target = dfi[flowitem][999]
            target = self._fix_target(target, md)   # fix it

            if target in self._dutflow:
                # target is a subflow item, call recursively. ie, this is a composite
                # print(f'{ii} JDR f_item={self._dutflow[target]["_ORDER"][0]} flowitem={flowitem} target=[{target}] {trace}')
                tmod = tuple_modname(target)[0]
                trc = trace + [target] if trace else None
                for item in self._recurse_flow(target, trc, tmod, seen, passonly):
                    yield item

            else:
                # target is an instance
                # When md is empty, it means that instance is from ProgramFlows.mtpl
                # assert md, (f'Error: Empty md! target={target} trace={trace} ii={ii} flowitem={flowitem} '
                #             f'tn={tuple_modname(target)[1]}')
                # print(f'{ii} DEBUGFINAL md={md} tn={tuple_modname(target)} subflow={subflow} flowitem={flowitem} {trace}')

                # yield md, tuple_modname(target)[1], trace
                yield subflow, flowitem, trace

            # recursively goto other ports
            for portno in sorted(dfi[flowitem], reverse=True):
                if portno in (999, 1):            # ignore special target item and pass flow
                    continue

                if passonly:    # empty passonly means traverse to all ports
                    if '_PASSONLY' in passonly:
                        if portno <= 0 or dfi[flowitem][portno].get('PassFail', 'Pass') != 'Pass':
                            continue              # passonly flow, ports 1 and above
                    else:
                        if flowitem in passonly:
                            continue

                port = dfi[flowitem][portno]
                if 'GoTo' in port:
                    trc = trace + [f'port={portno} of {flowitem}'] if trace else None
                    for item in self._recurse_flow(subflow, trc, md, seen, passonly, flowitem=port['GoTo']):
                        yield item

            # pass port - port1
            passport = passonly.get(flowitem, 1)   # Default is 1 PASS port, unless specified in passonly dict
            if passport not in dfi[flowitem]:
                passport = self._id_passport(dfi, flowitem, passonly)
            port = dfi[flowitem][passport]
            if 'GoTo' in port:
                flowitem = port['GoTo']
                assert flowitem in dfi, f'{flowitem} is not found in dfi. target={target} trace={trace}'
            else:
                break   # end

        else:    # pragma: no cover
            raise ErrorCockpit("Max loop in recurse_flow. Pls check logic!")

    def _id_passport(self, dfi: dict, flowitem: str, passonly: dict) -> int:
        """
        Return the passport given dfi, flowitem and passonly dict
        """
        # check passonly first
        if flowitem in passonly:
            raise ErrorInput(f'Specified passonly port={passonly[flowitem]} does not exist in {flowitem}',
                             'Pls check inputs to iter_flows()')
        for port in (2, 3, 4, 5, 6, 7, 8, 9, 0, -1, -2, -3, -4, -5, -6, -7, -8, -9):
            if port in dfi[flowitem]:
                return port
        raise ErrorCockpit(f'Cannot find any port to go in flowitem={flowitem}',
                           'Pls contact jqdelosr. Unexpected testprogram flow.')

    def get_flow_instance(self, dutflow, dutflowitem):
        """Return the (module, instancename) of dutflow and dutflowitem"""
        self.read_mtpl_flow() if not self._dutflow else None
        assert dutflow in self._dutflow, f'[{dutflow}] is not found in any subflows'
        assert dutflowitem in self._dutflow[dutflow], f'[{dutflowitem}] is not found inside {dutflow}'

        target = self._dutflow[dutflow][dutflowitem][999]

        # get md and tn
        md, _ = tuple_modname(dutflow)
        if ':' in target:
            md, tn = tuple_modname(target)
        else:
            tn = target
        return md, tn

    def get_flow_ports(self, dutflow, dutflowitem) -> dict:
        """Return the port dictionary given dutflow and dutflowitem"""
        self.read_mtpl_flow() if not self._dutflow else None
        assert dutflow in self._dutflow, f'[{dutflow}] is not found in any subflows'
        assert dutflowitem in self._dutflow[dutflow], f'[{dutflowitem}] is not found inside {dutflow}'

        target = dict(self._dutflow[dutflow][dutflowitem])
        del target[999]
        return target

    def get_instance_to_subflows(self):
        """
        return instance to set_of_subflows
        :return: dict {(module, instance): set(subflows)}
        """
        assert self._dutflow, 'Pls run init first'

        # First pass, get all child->parent association
        c2p = defaultdict(set)    # {child: set_of_parents}
        df = self._dutflow
        for key in df:
            for dfi in df[key]:
                if dfi == '_ORDER':
                    continue    # skip this
                targ = remove_ip(df[key][dfi][999])
                module = key.split(':')[0]
                if targ in df:
                    c2p[targ].add(key)
                if f'{module}::{targ}' in df:
                    c2p[f'{module}::{targ}'].add(key)

        # Second pass, add all parents (recursive)
        for key in c2p:
            c2p[key].update(self._parents(c2p, key, set()))

        # Final pass, get all instances
        final = defaultdict(set)
        for key in df:
            for dfi in df[key]:
                if dfi == '_ORDER':
                    continue    # skip this
                targ = remove_ip(df[key][dfi][999])
                module = key.split(':')[0]
                if targ in df or f'{module}::{targ}' in df:
                    continue    # composite

                # this is testinstance
                final[(module, targ)].add(key)            # immediate parent
                final[(module, targ)].update(c2p[key])    # all parents

        return final

    def _parents(self, c2p, key, result):
        """
        Recursive sub-function for get_instance_to_subflows
        :param c2p: dict {child: set_of_parents}
        :param key: key
        :param result: set_of_parents
        :return:
        """
        if key not in c2p:
            return result    # Done
        for parent in c2p[key]:
            if parent not in result:
                result.update(self._parents(c2p, parent, result | {parent}))
        return result

    @classmethod
    def ituff_tnames(cls, ituff_file):
        """
        Read ituff (simple way) and return set of (module, tnames)
        :param ituff_file: path to ituff
        :return: set of (module, tnames)
        """
        if not ituff_file:
            return set()
        result = set()
        token = '2_tname_testtime_'
        lentoken = len(token)
        for line in File(ituff_file).chomp():
            if line.startswith(token):
                value = line[lentoken:]
                elems = value.split('::')
                if len(elems) >= 2:
                    result.add((elems[-2], elems[-1]))
                else:
                    result.add((None, elems[-1]))
        return result

    def set_tn_attrib(self, reset=False, keyparam='patlist'):
        """
        Populate various values in instance dictionary

        Performance of iter_flows() is 0.4sec, so consolidate here
        """
        if self._is_tn_attrib and not reset:
            return 1    # Do nothing
        self._is_tn_attrib = True

        for md, tn, data, ports in self.iter_flows('MAIN', passonly=False, bypass=False, keyparam=keyparam, idict=True, pdict=True):
            self._set_minmaxnom(md, tn, data)
            self._set_freq(md, tn, data)
            self._set_edckill(md, tn, data, ports)

        # Copy new keys to edata
        if self.edata:
            for md, tn, param in iter_levels(self.tdata, 3):
                if param not in self.edata[md][tn]:
                    self.edata[md][tn][param] = self.tdata[md][tn][param]

    def _set_edckill(self, md, tn, data, ports, key='_EDCKIL'):
        """Populate '_EDCKIL' in instance dictionary"""
        port = 0    # Look at port 0 only for KILL

        # if port 0 exist and PassFail==Fail and SetBin is set, then set to KILL
        if port in ports and 'SetBin' in ports[port] and ports[port].get('PassFail') == 'Fail':
            assert data.get(key) != 'EDC', f'{md} {tn} is already EDC and is being set to KILL?'
            data[key] = 'KIL'
            return   # Done

        # if it is not kill, then it's EDC. b69 is checked somewhere else
        assert data.get(key) != 'KIL', f'{md} {tn} is already KILL and is being set to EDC?'
        data[key] = 'EDC'

    def _set_minmaxnom(self, md, tn, data,
                       re_lvl=re.compile(r'(nom|min|max)', re.IGNORECASE),
                       re_tnm=re.compile(r'(vmin|nom|min|max)', re.IGNORECASE),
                       key='_CORNER'
                       ):
        """Populate '_CORNER' in instance dictionary, if min, max, nom, unk"""
        # step1: use levels name
        lvl = get_param(data, 'level', '_')
        res = re_lvl.search(lvl)
        if res:
            data[key] = res.group(1).lower()
            return

        # step2: use testinstance voltage_domain
        dd = ti_disassemble(tn, isdict=True)
        if dd and dd['voltage_domain'] != 'X':
            data[key] = dd['voltage_domain']
            return

        # step3: regex on test instance name
        res = re_tnm.search(tn)
        if res:
            data[key] = res.group(1).lower()
            return

        data[key] = 'UNK'   # cannot derive min, max, nom

    def _set_freq(self, md, tn, data,
                  r_obj1=re.compile(r'_(\d\d\d|\d\d\d\d|\d\d\d\d\d|\d+.hz|\d+.HZ)_'),
                  r_obj2=re.compile(r'_(F\d)_'),
                  key='_FREQ'
                  ):
        """Populate '_FREQ' in instance dictionary to indicate freq of test"""

        # step1: use testinstance freq then corner
        dd = ti_disassemble(tn, isdict=True)
        if dd and dd['freq'] != 'X':
            data[key] = dd['freq']
            return
        if dd and dd['corner'] != 'X':
            data[key] = dd['corner']
            return

        # step2: use regex
        res = r_obj1.search(tn) or r_obj2.search(tn)
        if res:
            # print(f'{res.group(1)} {tn}')
            data[key] = res.group(1)
            return

        # print(f'NONE {md} {tn}')
        data[key] = 'NONE'   # cannot derive min, max, nom


class BM:
    """
    Class to read binmatrix and expand an mtpl line based on binmatrix vars
    This is not part of mtpl or TestProgram since this is called independently
    Usage:
        bm = BM(tpobj)
        result = bm.expand(line)
    """

    def __init__(self, tpobj, readmodules=True):
        """Initialize BM with TP object and binmatrix state.

        :param tpobj: TestProgram object providing TP context
        :type tpobj: tp.testprogram.TestProgram
        :param readmodules: If True, read module-level usrv files
        :type readmodules: bool
        """
        self.tpobj = tpobj
        self.bm_file = None
        self.bvars = None  # {varname: [values]} mapping
        self.isinit = False
        self.readmodules = readmodules

    def init(self):
        """Read binmatrix and spec usrv files and populate bvars mapping.

        :return: Self for method chaining
        :rtype: BM
        """
        import glob
        self.isinit = True

        # note: Cannot use Usrv class (TP Library function) to read the .usrv since it will evaluate it to one value
        bm_glob = sorted(glob.glob(f'{self.tpobj.tpldir}/Shared/*/*Matrix.flm.usrv') +                  # legacy structure
                         glob.glob(f'{self.tpobj.tpldir}/Shared/*/*/Common_{self.tpobj.get_bomfolder()}/*Matrix.flm.usrv'))    # NVL structure
        if not bm_glob:
            self.bvars = {}
            return self    # Nothing to process
        bm = bm_glob[0]
        self.bm_file = bm
        self.bvars = {}
        self._read(bm)

        # spec read
        spec_glob = sorted(glob.glob(f'{self.tpobj.tpldir}/Shared/*/BinMatrixSpecs.flm.usrv') +
                           glob.glob(f'{self.tpobj.tpldir}/Shared/*/*/Common_{self.tpobj.get_bomfolder()}/BinMatrixSpecs.flm.usrv'))    # NVL structure
        if spec_glob:
            ff = spec_glob[0]
            self._read(ff)

        # module usrv
        if self.readmodules:
            for modname, mtpl in self.tpobj.mtpl.get_mod2fname().items():
                for ufile in glob.glob(f'{dirname(mtpl)}/*.usrv'):
                    self._read(ufile, modname)

        return self

    def _read(self, bm, modname=None):
        """Read one .usrv file"""
        robj = re.compile(r'(\w+)\s*=.*BomGroupRule\((.*)\);')
        robj2 = re.compile(r'Array\S+\s+(\w+)\s*=\s*(\S.*);')
        block = None
        mscope = f'{modname}__' if modname else ''
        funcvars = {'toString': lambda x: [str(y) for y in x],
                    'toDouble': lambda x: [float(y) for y in x],
                    'toInteger': lambda x: [int(y) for y in x]}
        for lno, line in OtplFile(bm).readline():
            if line.startswith("UserVars "):
                block = line.split()[1]
                avars = dict(self.bvars)
                avars.update(funcvars)

            # Standard binmatrix line
            res = robj.search(line)
            if res:
                assert block, f'Error on line#{lno} of {bm}. No UserVars block found.'
                key = f'{mscope}{block}__{res.group(1)}'
                try:
                    pyres = eval(res.group(2))
                except Exception as e:
                    pyres = None
                    log.info(f'-w- {key} fail_eval: [{res.group(2)}] lno={lno}: [{line}] of {basename(bm)}')

                if isinstance(pyres, str) or pyres is None:
                    self.bvars[key] = pyres
                elif isinstance(pyres[0], list):   # multi-bom
                    self.bvars[key] = list(chain(*pyres))
                else:  # single-bom
                    self.bvars[key] = list(chain(pyres))

                continue

            # Manual line
            res = robj2.search(line)
            if res:
                expr = res.group(2)
                expr = expr.replace('.', '__')
                key = f'{mscope}{block}__{res.group(1)}'
                try:
                    pyres = eval(expr, avars)
                except Exception as e:
                    pyres = None
                    log.info(f'-w- {key} fail_eval: [{expr}] lno={lno}: [{line}] of {basename(bm)}')

                self.bvars[key] = pyres

    def expand(self, line, suggestion='Check tp',
               _robj=re.compile(r'^(\s*SetBin\s+|\s*TrialTest\s+\w+\s+|\s*CSharpTrialTest\s+\w+\s+)')):
        """
        iterator, Expand an expresion line.
        :param line: line
        :param suggestion: Include the module, lineno and file here
        :return:
        """
        if not self.isinit:
            self.init()

        if '+' not in line:
            yield line
            return   # Nothing to do

        res = _robj.search(line)
        if res:
            line = line.replace(res.group(1), '"%s"+' % res.group(1))
        else:
            raise ErrorInput(f"BM.expand(): Invalid line: [{line}], Expecting: {_robj.pattern}",
                             suggestion)

        # expand it ======
        if ';' in line:    # need to remove ; as eval() does not like it
            semicolon = line.index(';')
            foot = line[semicolon:]   # includes semicolon
            line = line[:semicolon]
        else:
            foot = ''

        # variable                     +    \S except + char
        validlistvar = None
        for full, var in re.findall(r'(\+\s*([^\s\+]+))', line):
            if '"' in var:
                continue

            validvar = var.replace('.', '__')
            validvar = validvar.replace('__shared__::', '')     # code does not have __shared__, so remove it
            validvar = validvar.replace('::', '__')
            if validvar in self.bvars:
                if isinstance(self.bvars[validvar], list):
                    line = line.replace(full, '+ %s[idx]' % validvar)
                    validlistvar = validvar
                else:
                    line = line.replace(full, '+ %s' % validvar)
            else:
                # pprint(self.bvars)
                emsg = (f'key=[{validvar}] var=[{var}] is not found in BinMatrix [{self.bm_file}]. '
                        f'Variable count: {len(self.bvars)}. '
                        f'Line: [{line}]')
                raise ErrorInput(emsg, suggestion)

        dd = dict(self.bvars)

        try:
            if validlistvar:
                for idx in range(len(self.bvars[validlistvar])):
                    dd['idx'] = idx
                    yield eval(line, dd) + foot
            else:
                yield eval(line, dd) + foot

        except Exception as e:
            raise ErrorInput(f'Error on eval() of [{line}]: Message: {e}', suggestion)


import tp.testprogram  # used for :type
from tp.timlvl import ExprParser
