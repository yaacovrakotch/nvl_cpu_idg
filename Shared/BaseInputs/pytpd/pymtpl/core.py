"""
core classes for pymtpl

A Flow() consist of <list_of_Fitem>
A Fitem() consistem of one Testinstance (BaseMethod) or a Composite (Flow())
A Fitem() also has Ports using r0=Ports() or rm<n>=Ports()
"""
from gadget.pylog import log
from gadget.errors import confirm, ErrorUser, ErrorInput, Check
from gadget.files import File
from gadget.disk import mkdirs
from gadget.helperclass import OPT, IS_UT, NoneLikeClass
from gadget.strmore import sha1, to_list
from gadget.dictmore import DictDot
from gadget.shell import CALLERBIN, SystemCall
from gadget.gizmo import get_caller_lno
from os.path import dirname, exists, basename
from importlib.machinery import SourceFileLoader
from itertools import chain
from functools import partial
from collections import OrderedDict
from pymtpl.bindef_dict import BINDEF_DICT
from tp.testprogram import Env
from tp.testprogram import TestProgram
from pymtpl.uservars import UserVars
import re
import os
import json
import glob
import sys


class PyMtpl:
    """
    pymtpl writer, main wrapper class
    This class is purely classmethods
    """

    @classmethod
    def main(cls):
        """Main Entry point to write the output"""

        # we wait to import until now so that core is fully imported before this is
        # Skip path updater if the option is set
        if not OPT.skip_path_updater:
            from pymtpl.path_updater import PythonPathUpdater
            PythonPathUpdater.write_python_paths_for_VS()

        for pyfile in OPT.all:
            Initialize.clear_all()
            cls.main_one(pyfile)

    @classmethod
    def main_one(cls, pyfile):
        """Process one pyfile"""

        # Import the source code python
        cls._import(pyfile)

        # Write it
        cls.write()

    @classmethod
    def write(cls):
        """Write the output files"""

        # 0 - Write only once
        if Initialize.written:
            log.info('-i- Skipping write() - it is already written')
            return

        Initialize.written = True

        # 1 - Get all the flow lines
        # duplicate any Flow() items that is reused
        # Performance optimization: Cache registry to avoid multiple lookups
        flow_registry = list(Flow.get_registry())
        for flow_obj in flow_registry:
            Initialize.nonmttbinstrategy.populate_internal_bin_trackers(flow_obj)
            Initialize.nonmttctrstrategy.populate_internal_ctr_trackers(flow_obj)
            flow_obj.duplicate_flow_obj()

        # Refresh registry after duplication (new flows may have been added)
        flow_registry = list(Flow.get_registry())

        # 2a - Append import statements to the headers
        hlines = []
        for item in Import.get_import_registry():
            string_quotes = '"' if Initialize.tosversion == "tos4" else ''
            hlines.append(f'Import {string_quotes}{item}{string_quotes};')

        # 2b - Append Mtpl comment statements to the headers
        mtplcommentlines = []
        for item in MtplComment.get_import_registry():
            mtplcommentlines.append(f'# {item}')

        # 3 - Get all flow and testinstance lines
        # Performance optimization: Combine flow line and test instance collection in single iteration
        dlines = []
        ilines = []
        Fitem.print_registry = set()      # clear the registry names
        for flow_obj in flow_registry:
            dlines.extend(flow_obj.write_lines())
            for fitem in flow_obj.get_items():
                ti_obj = fitem.get_instance()
                if isinstance(ti_obj, BaseMethod):       # only write testinstance here, not dutflow or MultiTrial
                    ilines.extend(ti_obj.write_lines(fitem.ti_counter, edc=fitem.edc))
                    if Initialize.tosversion == "tos3" and not str(ti_obj.get_method_name()).startswith('iC'):  # tos3 needs import of xml, but not evergreen templates
                        impline = f'Import {str(ti_obj.get_method_name())}.xml;'
                        if impline not in hlines:
                            hlines.append(impline)

        # 4 - Write to the .mtpl
        # Convert the counter header to a list so that we can enumerate it and also sort it.
        confirm(Initialize.nonmttctrstrategy is not None,
                'nonmttctrstrategy is not defined',
                'Initialize() is not called. Pls call Initialize() as it is required.')
        counterheaders = list(sorted(Initialize.nonmttctrstrategy.ctr_headers))
        all_lines = chain(cls._headers(hlines, counterheaders, mtplcommentlines),
                          ilines,
                          dlines,
                          Initialize.flowdefs.write_lines() if Initialize.flowdefs else [])
        mtpl_file = Initialize.get_outfile()
        mkdirs(dirname(mtpl_file))
        if not File(f'{mtpl_file}.mtpl').rewrite('\n'.join(all_lines), 'PyMtpl().main(mtpl)'):
            log.info(f'-i- NO UPDATE: No changes to {mtpl_file}.mtpl')

        # 5a - Write AutoBin json file
        autobinfilepath = Initialize.nonmttbinstrategy.autobinfilepath
        autobinfilename = os.path.basename(autobinfilepath)
        if Initialize.usebinctrfrommtpl and os.path.exists(autobinfilepath):
            log.info(f'-i- CHANGE: Pymtpl is moving to using mtpl for bin information so {autobinfilename} is no longer needed. It is being removed.')
            os.remove(autobinfilepath)
        elif not Initialize.usebinctrfrommtpl:
            mkdirs(dirname(autobinfilepath))
            with open(autobinfilepath, 'w') as json_file:
                json.dump(Initialize.nonmttbinstrategy.autobindict, json_file, indent=4)

        # 5b - Write sbdef file
        sbdef_lines = []
        sbdef_content = Initialize.nonmttbinstrategy.write_sbdef_file()
        sbdef_lines.extend(sbdef_content)
        output_dir = dirname(mtpl_file) or '.'
        sbdef_file = os.path.join(output_dir, Initialize.default_class.get_subbindef_name(str(Initialize.get_modulename())))

        # sbdef_file = str(Initialize.get_modulename()) + "_SubBinDefinitions.sbdefs"

        if sbdef_lines:
            if not File(f'{sbdef_file}').rewrite('\n'.join(sbdef_lines), 'SBDef_Generator'):
                log.info(f'-i- NO UPDATE: No changes to {sbdef_file}')

        # 6 - Write AutoCounter json file
        autoctrfilepath = Initialize.nonmttctrstrategy.autoctrfilepath
        autoctrfilename = os.path.basename(autoctrfilepath)
        if Initialize.usebinctrfrommtpl and os.path.exists(autoctrfilepath):
            log.info(f'-i- CHANGE: Pymtpl is moving to using mtpl for counters so {autoctrfilename} is no longer needed. It is being removed.')
            os.remove(autoctrfilepath)
        elif not Initialize.usebinctrfrommtpl:
            with open(autoctrfilepath, 'w') as json_file:
                json.dump(Initialize.nonmttctrstrategy.autoctrdict, json_file, indent=4)

        # 7 - Write AutoBasenumber json file if it's not empty
        autobasenumdir = dirname(Initialize.basenumber.autobasenumfilepath)
        if Initialize.basenumber.autobasenumdict:
            # Need to add makedirs to Basenumber as if we use mtpl for bin info, we will not create the PymtplInputfiles folder
            mkdirs(autobasenumdir)
            with open(Initialize.basenumber.autobasenumfilepath, 'w') as json_file:
                json.dump(Initialize.basenumber.autobasenumdict, json_file, indent=4)
        elif os.path.exists(Initialize.basenumber.autobasenumfilepath):
            log.info(f'-i- CHANGE: Basenumber is empty so {os.path.basename(Initialize.basenumber.autobasenumfilepath)} is being removed.')
            os.remove(Initialize.basenumber.autobasenumfilepath)

        # 8 - Remove the pymtplinputfiles folder if exists and is empty - it's always generated in set_outfile
        if os.path.exists(autobasenumdir) and not os.listdir(autobasenumdir):
            os.rmdir(autobasenumdir)

        # 9 - Write mconfig file
        mconfiglines = []
        mconfigfile = os.path.join(dirname(Initialize.get_outfile()), "module.mconfig")
        # If user defined mconfig in their input, generate the file.
        if MConfig.get_mconfig_registry():
            for mconfig_obj in MConfig.get_mconfig_registry():
                mconfiglines.extend(mconfig_obj.write_lines())
            if not File(f'{mconfigfile}').rewrite('\n'.join(mconfiglines), 'PyMtpl().main(mconfig)'):
                log.info(f'-i- NO UPDATE: No changes to {mconfigfile}')

        # 10 - Generate Flow File if user wants it.
        if Initialize.forceflwfilegen or not os.path.exists(f'{mtpl_file}.flw'):
            # Performance optimization: Reuse cached flow_registry instead of calling get_registry() again
            flow_file_lines = list(cls._generate_flow_file(flow_registry))
            File(f'{mtpl_file}.flw').rewrite('\n'.join(flow_file_lines), 'PyMtpl().main(flw)')

        # 11 - Generate the uservars file if the user has one
        if UserVars._uservar_registry:
            UserVars.write_all_uservars(Initialize.get_modulename())

        # 12 - If successful, let PDE know with a log message.
        log.info(f'-i- Successfully ran pymtpl for {mtpl_file}.mtpl')

        # 13 - Print summary of missing setbin warnings if count > 5
        if Initialize.missing_setbin_warning_count > 5:
            log.warning(f'Total of {Initialize.missing_setbin_warning_count} kill test fail ports have no bin assignment (setbin). Only first 5 warnings were shown above.')

    @classmethod
    def _headers(cls, hlines, counterheaders, mtplcommentlines):
        """Iterator or returns list of lines for the mtpl header"""
        yield f'Version 1.0;'
        yield f''
        yield f'ProgramStyle = Modular;'
        yield f''
        yield f'TestPlan {Initialize.get_modulename()};'
        yield f''
        for hline in hlines:
            yield hline
        yield ''
        if counterheaders:
            yield "# Test Counter Definition"
            yield ''
            yield 'Counters'
            yield '{'
            for i, ctr in enumerate(counterheaders):
                if i == len(counterheaders) - 1:
                    yield f'    {ctr}'
                else:
                    yield f'    {ctr},'
            yield '} # End of Test Counter Definition'
            yield f''
        if mtplcommentlines:
            yield '# BEGIN MTPL COMMENT SECTION \n'
            for mtplcommentline in mtplcommentlines:
                yield mtplcommentline
            yield ''
            yield '# END MTPL COMMENT SECTION \n'

    @classmethod
    def _generate_flow_file(cls, flow_registry):
        """Takes flow items and generates the flw file"""
        yield '<?xml version="1.0" encoding="utf-8"?>'
        yield '<!--File is auto-generated, any manual edits can be overwritten.-->'
        yield '<!DOCTYPE HDMTFlowItemCoor []>'
        yield '<HDMTFlowItemCoor>'
        for flow_obj in flow_registry:
            x = 25
            y = 25
            n = 0
            for fitem in flow_obj.get_items():
                yield f'  <FlowItem name="{Initialize.get_modulename()}::{flow_obj.name}.{fitem.get_name()}" X="{x}" Y="{y}" />'
                x = x + 170
                n = n + 1
                # Increment Y co-ordinate every 4th test and reset X co-ordinate
                if n % 4 == 0:
                    y = y + 250
                    x = 25
        yield '</HDMTFlowItemCoor>'

    @classmethod
    def _import(cls, pyfile):
        """
        Import this particular pyfile

        :param pyfile: path to the py file
        :return: base_path, module object
        """
        if isinstance(pyfile, str):
            confirm(exists(pyfile), f'File {pyfile} does not exist', f'Check cwd: {os.getcwd()}')
            obj = SourceFileLoader(sha1(pyfile), pyfile).load_module()
        else:
            obj = pyfile     # Used with unittests

        return obj

    @classmethod
    def run(cls, script_path, env_path):
        """
        Public method to call pymtpl as a SystemCall.
        SystemCall is the recommended way because of ProgramFlows example where we run the same
        py across different dielets, which does not work well with direct python import
        :param script_path: source code path
        :param env_path: env path
        :return: None
        """

        if basename(dirname(CALLERBIN)) == 'main':
            # direct call from pymtpl
            exe = f'{dirname(CALLERBIN)}/pymtpl.py'

        elif basename(dirname(CALLERBIN)) == 'test':
            # from unittest
            exe = f'{dirname(CALLERBIN)}/../../main/pymtpl.py'

        else:
            # from qgates or mod or other folder
            exe = f'{dirname(CALLERBIN)}/../main/pymtpl.py'

        # call it
        cmd = [sys.executable, exe, script_path, '-env', env_path]
        SystemCall(cmd).run(disp=True, exitout='pymtpl failed')


class Flow:
    """Flow object

    Required class in the pymtpl output to ensure a flow shows up in mtpl

    Params:
        name: string, name of the Flow. Required.
        *fitem_list: list of Fitem() or BaseMethod(with _fitem) or Composites (Flow: see below)
        dtag: Flow alias name. e.g. dtag="INIT" results in @INIT

    Examples:
        1) Directly creating test instances in the Flow
            Flow('INIT',
                Fitem(TestInstance1, r0=pFail(...), r1=pPass(...)),
                Fitem(TestInstance2, r0=pFail(...), r1=pPass(...)),
                dtag='INIT')
        2) Creating test instances separately and then using them in the Flow
            end_tests = []
            end_tests.append(Fitem(TestInstance3, r0=pFail(...), r1=pPass(...)))
            Flow('END', *end_tests)
        3) Using Composite (Flow) inside Flow
            sub_flow = Flow('SUBFLOW1', *sub_flow_tests)
            Flow('MAIN',
                 Fitem(sub_flow, r0=pFail(..), r1=pPass(...)),
                 TestInstanceWith_fitem,
                )
    """
    _registry = []         # list of Flow() object in order as they are defined, in one .py file
    _registry_name = []    # list of Flow() names
    # Performance optimization: dict for O(1) name lookups vs O(n) list.index()
    # Improves flow registration performance from O(n²) to O(n) for modules with many flows
    _registry_name_to_idx = {}

    @classmethod
    def clear_registry(cls):
        """Clear the registry"""
        cls._registry = []
        cls._registry_name = []
        cls._registry_name_to_idx = {}

    def __init__(self,
                 name,               # name of the dutflow
                 *fitem_list,        # list of Fitem() or BaseMethod(with _fitem)
                 _orig_name=None,    # Set to original name, used with duplicate_flow_obj
                 dtag=None    # Flow alias name
                 ):
        self.id_lno = get_caller_lno()
        self.name = Check.is_str('name', name, lno=self.id_lno)
        self.fitem_list = list(self._check_fitem(fitem_list))    # list of fitem objects
        self._add_in_registry(_orig_name)
        self.counter = -1      # Called during writing
        self.my_counter = -1   # Called during duplicate
        self.fitem_obj = None  # Composite has fitem_obj defined
        self.dtag = dtag

        # Assign self into Fitem's flow_obj
        for fitem in self.fitem_list:
            fitem.flow_obj = self

    def _check_fitem(self, fitem_list):
        """Check if fitem_list are all Fitem object. If list, expand it"""
        for item in fitem_list:
            if isinstance(item, list):
                for item_in_list in item:
                    yield self._check_one_item(item_in_list)

            else:
                yield self._check_one_item(item)

    def _check_one_item(self, item_in_list):
        """Check one item"""
        if isinstance(item_in_list, Fitem):
            return item_in_list
        elif isinstance(item_in_list, BaseMethod):
            confirm(item_in_list.fitem,
                    f'The Instance in line#{item_in_list.id_lno} has no _fitem',
                    '_fitem is required when specifying Testinstance directly in Flow()')
            return item_in_list.fitem
        else:
            raise ErrorInput(f'Error in line#{self.id_lno}, input is {item_in_list}.',
                             'Pls fix, expecting Fitem() object.  Test Methods and Flows must be wrapped in an Fitem.')

    def _add_in_registry(self, orig_name):
        """Add in registry list just after self"""
        # Performance optimization: Use dict lookup instead of list.index() for O(1) performance
        # Note: Index updates after insertion are O(n), but this is still better than the original
        # O(n) list.index() search. The insertion case (orig_name provided) is rare - most flows
        # are simply appended. For the common case (append), this is O(1).
        if orig_name and orig_name in self._registry_name_to_idx:
            idx = self._registry_name_to_idx[orig_name] + 1
            self._registry.insert(idx, self)
            self._registry_name.insert(idx, self.name)
            # Update indices for all flows after insertion point
            # This is O(n) but insertion is rare (only used for duplicate flows)
            for i in range(idx, len(self._registry_name)):
                self._registry_name_to_idx[self._registry_name[i]] = i
        else:
            # Common case: append to end - O(1) performance
            idx = len(self._registry)
            self._registry.append(self)
            self._registry_name.append(self.name)
            self._registry_name_to_idx[self.name] = idx

    def counter_increment(self):
        """Calling counter for different FlowItems, called by Fitem()"""
        self.counter += 1
        return self.counter

    def get_items(self):
        """Return all fitems"""
        return self.fitem_list

    def write_lines(self):
        """Iterator a list of lines for Flow()"""
        if Initialize.tosversion == "tos4":
            flow_precursor = 'Flow'
        else:
            flow_precursor = 'DUTFlow'

        if self.dtag is not None:
            dtag = f' @{self.dtag}'
        else:
            dtag = ''

        yield f'{flow_precursor} {self.name}{dtag}'
        yield '{'

        uniq = set()
        for idx in range(len(self.fitem_list)):
            fitem = self.fitem_list[idx]

            # check no duplicate DutFlowItems
            confirm(fitem.get_name() not in uniq,
                    f'{fitem.get_name()} is reused inside [{self.name}]. This is not allowed',
                    'Within a DUTFlow block, all names must be unique')
            uniq.add(fitem.get_name())

            if idx == len(self.fitem_list) - 1:
                nextfitem = None
            else:
                nextfitem = self.fitem_list[idx + 1]

            for line in fitem.write_lines(nextfitem):
                yield f'    {line}'

        yield '}'
        yield ''

    def duplicate_flow_obj(self):
        """Duplicate flow_obj if is called multiple times"""
        for item in self.fitem_list:
            obj = item.get_instance()
            if isinstance(obj, Flow):
                obj.my_counter += 1
                if obj.my_counter > 0:

                    # we create a copy of Flow() and all Fitems()
                    fitem_list = [x.duplicate_me() for x in obj.fitem_list]
                    Flow(f'{obj.name}_{obj.my_counter}', fitem_list, _orig_name=obj.name)

    def get_name(self):
        """Return the name"""
        return self.name

    @classmethod
    def get_registry(cls):
        """Return list of Flow() objects, ordered according creation"""
        return cls._registry


class ModuleFlow(Flow):
    """
    Module SubFlow, used in ProgramFlows.

    What is different here?
    1. The DUTFlow() block is not written
    2. The input is just modulename
    """

    def write_lines(self):
        """Nothing to write here"""
        return []

    def get_name(self):
        """
        Return the name, used in the printout.

        Convention:
        name    # auto-ip-name, with module addition
        ~name   # no-ip-name
        $name   # direct add, no module addition
        """
        if self.name.startswith('~'):
            name = self.name[1:]
            ispf = False
        else:
            name = self.name
            ispf = True

        if name.startswith('$'):     # special case: Concurrent flow
            return name[1:]

        if '::' in name or (not self.fitem_obj):       # fitem_obj is "composite"
            return name    # as-is

        # name provided is just module name
        ip = Initialize.get_tpobj().get_mod2ip_map().get(name)
        if ip and ispf:
            return f'{ip}::{name}::{self.fitem_obj.get_name()}'
        elif f'{name}_SubFlow' == self.fitem_obj.get_name():
            # special case for MAIN and parallel item - just print as-is without the Subflow
            return f'{name}_SubFlow'
        else:
            return f'{name}::{self.fitem_obj.get_name()}'


class Floating(Flow):
    """
    Flow-like for Floating instances. Use this to tell the instance object is floating.
    """

    def write_lines(self):
        """Nothing to write for floating instances, just the instances themselves"""
        return []


class ConCurrentFlow(Flow):
    """
    Example:
        ConCurrentFlow('PRL0CPUIOE_SubFlow',
                       IP_CPU='IP_CPU_CONCURRENT_FLOWS::PRL0CPUIOE_IP_CPU_FLOW_SubFlow',
                       IP_PCH='IP_PCH_CONCURRENT_FLOWS::PRL0CPUIOE_IP_PCH_FLOW_SubFlow',
                       result=['IP_CPU, IP_PCH, EffectiveIPResult',
                               '1    ,    1   , IP_CPU',
                               '1    ,  [*:0] , IP_PCH'])
    """

    def __init__(self,
                 name,
                 result,
                 **kwargs):    # These are the IP values
        self.id_lno = get_caller_lno()
        self.name = Check.is_str('name', name, lno=self.id_lno)
        self.result = Check.is_obj('result', result, list, lno=self.id_lno)
        confirm(len(result) >= 2,
                f'Error in line {self.id_lno}, Expecting at least 2 elements for result field.',
                'First element in result is header and subsequent elements are the printed lines.')
        self.cfi = OrderedDict()
        for k, v in kwargs.items():
            self.cfi[k] = v

        self._add_in_registry(None)
        self.fitem_list = []

    def write_lines(self):
        """Write the ConCurrentFlow block"""
        yield f'ConcurrentFlow {self.name} [Parallel]'
        yield '{'

        for ip, value in self.cfi.items():
            yield f'    ConcurrentFlowItem {ip} {value};'

        yield f'    ConcurrentResultTable ({self.result[0]})'
        yield '    {'
        for item in self.result[1:]:
            yield f'        {item};'
        yield '    }'

        yield '}'


class FlowDefs:
    """FlowDefs object - Used with ProgramFlows.mtpl"""

    def __init__(self,
                 InitFlow='INIT',
                 MainFlow='MAIN',
                 LotEndFlow='LOTENDFLOW',
                 LotStartFlow='LOTSTARTFLOW',
                 TestPlanEndFlow='TESTPLANENDFLOW',
                 TestPlanStartFlow='TESTPLANSTARTFLOW',
                 **kwargs):      # future generic

        self.params = OrderedDict()

        dd = locals()
        for kw in 'InitFlow MainFlow LotEndFlow LotStartFlow TestPlanEndFlow TestPlanStartFlow'.split():
            if dd[kw]:
                self.params[kw] = dd[kw]

        self.params.update(kwargs)

        Initialize.flowdefs = self       # assign it

    def write_lines(self):
        """Return list of lines"""
        yield ''
        yield 'FlowDefs'
        yield '{'
        for param in self.params:
            yield f'    {param} = {self.params[param]};'
        yield '}'


class Fitem:
    """Flow Item
    Fitem is a wrapper around TestInstance (BaseMethod) or Composite (Flow)
    Fitem has ports defined using r0=pFail(...), r1=pPass(...), rm1=pFail(...), etc
    Params:
        name: string, name of the Flowitem. If undefined or SAME, then use the TestInstance/Composite name
        edc: True or False. Defaults to False (Kill)
        r0, r1, r2, r3, r4, r5, rm1, rm2: Ports() object
        MinLoopDuration: string, MinLoopDuration expression
        LoopCount: string, LoopCount expression
        BreakLoopOn: string, BreakLoopOn expression
    """
    print_registry = set()           # populated in write_lines(), cleared in PyMtpl.write()

    def __init__(self,
                 name='SAME',        # string, name of the Flowitem
                 ti=None,            # Flow() or BaseMethod() object. If None, it will be populated later
                 goto=None,          # string, goto Fitem name
                 edc=False,           # True or False
                 r0=None, r1=None, r2=None, r3=None, r4=None, r5=None, rm1=None, rm2=None,
                 MinLoopDuration=None,
                 LoopCount=None,
                 BreakLoopOn=None,
                 **kwargs):

        self.id_lno = get_caller_lno()
        # Check if Initialize is defined before proceeding.
        Initialize.is_initialized(self.id_lno)

        self.name = Check.is_str('name', name)
        self.ti = Check.is_obj('ti', ti, (Flow, BaseMethod), oknone=True)
        self.goto = Check.is_str('goto', goto, oknone=True)
        self.edc = Check.is_bool('edc', edc, oknone=True)
        self.MinLoopDuration = Check.is_str('MinLoopDuration', MinLoopDuration, oknone=True)
        self.LoopCount = Check.is_str('LoopCount', LoopCount, oknone=True)
        self.BreakLoopOn = Check.is_str('BreakLoopOn', BreakLoopOn, oknone=True)
        # Check if both LoopCount and MinLoopDuration are defined
        if self.LoopCount and self.MinLoopDuration:
            raise ErrorUser(f'Error in Fitem defined in line#{self.id_lno}: Both LoopCount and MinLoopDuration are defined in the Fitem.',
                            'You can only define one of LoopCount or MinLoopDuration.')

        self.ret_dict = self._process_ret_dict(self.id_lno, kwargs, r0, r1, r2, r3, r4, r5, rm1, rm2, edc=edc, ti=self.ti)      # {r0: portobject}
        self.flow_obj = None
        if self.ti:
            self.ti_counter = self.ti.counter_increment()        # We have to duplicate the object
        else:
            self.ti_counter = None                               # This will be assigned in BaseMethod() init
        # Store all known attribs. This is used as check in duplicate_me()
        self._attribs = 'name ti goto edc MinLoopDuration LoopCount BreakLoopOn'.split()
        self._ignore_attribs = set('id_lno ti_counter ret_dict flow_obj'.split())
        for item in vars(self):
            if item.startswith('_'):
                continue
            if item in self._ignore_attribs:
                continue
            assert item in self._attribs, f'Cockpit Error: {item} is not registered in self._attribs. Pls fix code.'

        # Assign self into the port objects
        for port_obj in self.ret_dict.values():
            port_obj.fitem_obj = self

        # Assign self into ti (Either BaseMethod or Flow)
        if self.ti:
            self.ti.fitem_obj = self

        self.ctr_header = set()

    @classmethod
    def _process_ret_dict(cls, id_lno, kwargs, r0, r1, r2, r3, r4, r5, rm1, rm2, edc, is_mtt=False, ti=None):
        """Process and returns the value of ret_dict"""
        ret_dict = kwargs
        if r0:
            ret_dict['r0'] = r0
        if r1:
            ret_dict['r1'] = r1
        if r2:
            ret_dict['r2'] = r2
        if r3:
            ret_dict['r3'] = r3
        if r4:
            ret_dict['r4'] = r4
        if r5:
            ret_dict['r5'] = r5
        if rm1:
            ret_dict['rm1'] = rm1
        if rm2:
            ret_dict['rm2'] = rm2
        # Check that ret_dict is always r\d or rm\d
        for item, value in ret_dict.items():
            confirm(re.search(r'^(r|rm)\d+$', item),
                    f'Invalid portid [{item}] in line {id_lno}',
                    'Must be r<num> or rm<num>')
            confirm(isinstance(value, BasePort),
                    f'Invalid portid {item}={type(value)} in line {id_lno}',
                    'Expecting pPass() or pFail() object')

        # negative zero is not allowed
        confirm('rm0' not in ret_dict, 'rm0 is not allowed, only r0', 'Pls fix')

        # If r1 is not specified, then add it
        if 'r1' not in ret_dict:
            if is_mtt:
                ret_dict['r1'] = pPass(trialaction='Exit')
            else:
                ret_dict['r1'] = pPass()

        # call custom initializations (if any) for non Flow items so the composites are skipped
        # TODO: Review with JDR for this logic change item #13
        Initialize.default_class.default_ports(ret_dict, is_mtt=is_mtt, id_lno=id_lno, ti=ti)

        # Update routing of undefined ports with best guess
        cls._default_undefined_port_routing(ret_dict, edc, is_mtt=is_mtt, ti=ti)

        return ret_dict

    @classmethod
    def _default_undefined_port_routing(cls, ret_dict, edc, is_mtt=False, ti=None):
        """
        Update routing of unassigned ports with best guess. EDC/Pass ports to Next, Kill Fail ports to 0.
        Args:
            :param ret_dict: dict of ports
            :param edc: bool, if EDC is enabled
            :param is_mtt: bool, if it is a MTT test
            :param ti: TestInstance object
        :return: None
        """

        # since we don't have a good way to detect if MTT tests are in EDC for now, this function will not be run for MTT tests
        # and we skip this when we're running unit tests UNLESS i force it
        if is_mtt or IS_UT:
            return

        for port in ret_dict:
            if ret_dict[port].ret is None and ret_dict[port].goto is None:
                # Negative ports always route to the same
                if port == 'rm2':
                    ret_dict[port].ret = -2
                elif port == 'rm1':
                    ret_dict[port].ret = -1
                # All EDC ports and kill test Pass ports go to next instance
                elif edc or isinstance(ret_dict[port], pPass):
                    ret_dict[port].goto = "NEXT"
                # fail ports on kill tests go to 0
                else:
                    ret_dict[port].ret = 0

    def duplicate_me(self):
        """Return a new Fitem() object that is a copy of self"""
        all_dict = dict(self.ret_dict)
        for item in self._attribs:
            all_dict[item] = getattr(self, item)
        obj = Fitem(**all_dict)
        obj.id_lno = self.id_lno      # Special - use same id_lno
        return obj

    def get_instance(self):
        """Return the test instance object"""
        return self.ti

    def get_name(self):
        """Return the name"""
        if self.name == 'SAME':
            if self.ti_counter == 0:
                return self.ti.name
            else:
                return f'{self.ti.name}_{self.ti_counter}'
        else:
            return self.name

    def write_lines(self, nextfitem):
        """Iterator a list of lines for Fitem()
        DUTFlowItem SBFT_X_VMIN_E_ENDCPU_X_VCCR_X_X_TDAU SBFT_X_VMIN_E_ENDCPU_X_VCCR_X_X_TDAU @EDC
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -2;
                }
        """

        if self.edc:
            edcstring = ' @EDC'
        else:
            edcstring = ''

        if self.MinLoopDuration:
            MinloopDurationstr = f' MinLoopDuration {self.MinLoopDuration}'
        else:
            MinloopDurationstr = ''

        if self.LoopCount:
            LoopCountstr = f' LoopCount {self.LoopCount}'
        else:
            LoopCountstr = ''

        if self.ti_counter == 0:
            ctrstring = ''
        else:
            ctrstring = f'_{self.ti_counter}'

        if Initialize.tosversion == "tos4":
            DUTflow_precursor = 'FlowItem'
        else:
            DUTflow_precursor = 'DUTFlowItem'

        # The DutFlowItem name cannot be duplicated. Testinstance name is ok to "referred to"
        # Reason: The durflowitem name is printed in ituff, and we want every instance to be uniq in name
        confirm(self.get_name() not in Fitem.print_registry,
                f'{self.get_name()} is redefined twice, see line {self.id_lno}. This is not allowed.',
                f'DutFlowItem name must be unique, add an incremental number in dutflow name.')
        Fitem.print_registry.add(self.get_name())

        yield f'{DUTflow_precursor} {self.get_name()} {self.ti.get_name()}{ctrstring}{MinloopDurationstr}{LoopCountstr}{edcstring}'
        yield '{'
        if self.BreakLoopOn:
            yield f'    BreakLoopOn {self.BreakLoopOn};'

        updatesetbinstring = [True]
        # This test name will be used to generate setbin and portctr strings as this is the unique test name with the counter at the end.
        test_name = self.ti.name + ctrstring
        # Identify the name of the test class to apply test class specific binning
        if isinstance(self.get_instance(), BaseMethod):
            test_class = self.ti.template_name
        else:  # If Fitem instance is a composite or Module Flow, there is no template_name
            test_class = None
        for portid, port_obj in sorted(self.ret_dict.items(), key=lambda x: BasePort._key2num(x[0])):
            custom_setbinstring = False
            portobj_type = port_obj.__class__.__name__

            # Get setbinstring for user input bins
            if port_obj.setbin and port_obj.setbin > 0:
                setbinstring = Initialize.nonmttbinstrategy.get_non_mtt_setbinstring(setbin=port_obj.setbin,
                                                                                     name=test_name,
                                                                                     updatesetbinstring=updatesetbinstring,
                                                                                     portid=portid,
                                                                                     lno=port_obj.id_lno,
                                                                                     test_class=test_class
                                                                                     )
            # Get setbinstring for auto-binning when only when EDC = False
            # TODO: JDR review needed for this logic change item #9
            elif port_obj.setbin and port_obj.setbin < 0:
                setbinstring = Initialize.nonmttbinstrategy.update_autosetbinstring(port_obj.setbin, port_obj.id_lno, portid, test_name, updatesetbinstring, portobj_type, test_class)

            # Manage case when user specifies setbinstring directly to use
            elif (port_obj.setbin is None and port_obj.setbinstring is not None):
                setbinstring = port_obj.setbinstring
                custom_setbinstring = True
                # we have to update the sbdef_dict so that it actually writes the custom setbinstring into the sbdef
                # but we don't need to update the autobindict because that will happen automatically via the setbinstring if need be
                Initialize.nonmttbinstrategy.sbdef_dict[setbinstring] = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]

            #  Manage cases where user specifies no setbin
            else:
                setbinstring = ''
                # Warn if this is a kill test fail port with no bin assignment and is BaseMethod since composites should not be binned.
                # Skip warning if 5th field of test name is "INIT"
                if not self.edc and portobj_type == 'pFail' and isinstance(self.get_instance(), BaseMethod):
                    test_name_parts = test_name.split('_')
                    # Check if 5th field (index 4) is NOT "INIT"
                    if len(test_name_parts) < 5 or test_name_parts[4] != 'INIT':
                        Initialize.missing_setbin_warning_count += 1
                        # Only print warning for first 5 occurrences
                        if Initialize.missing_setbin_warning_count <= 5:
                            log.warning(f'Kill test fail port {portid} has no bin assignment (setbin) for test "{test_name}" in line#{port_obj.id_lno}')

            # Counter handling for each port
            # Only assign counter if test is a BaseMethod
            if isinstance(self.ti, BaseMethod):
                # get port 0 setbin if possible
                port0_setbin = self.ret_dict['r0'].setbin if ('r0' in self.ret_dict and self.ret_dict['r0'] is not None) else None
                portctrstring = Initialize.nonmttctrstrategy.get_ctrstring_update_counterdict(portid, test_name, port_obj.ctr, port_obj.id_lno, setbinstring, portobj_type, test_class=test_class, port0_setbin=port0_setbin, custom_setbinstring=custom_setbinstring)
            else:
                portctrstring = ''
            # Now write the port lines
            for line in port_obj.write_lines(portid, test_name, nextfitem, self.edc, setbinstring=setbinstring, portctrstring=portctrstring, ismtt=None, custom_setbinstring=custom_setbinstring):
                yield f'    {line}'

        yield '}'
        yield ''


class BasePort:
    """BaseClass for Ports
    This is an abstract class and should not be instantiated directly.
    Sub-classes are pPass and pFail
    """
    ispass = False    # default is fail

    def __init__(self,
                 ctr=None,
                 setbin=None,
                 ret=None,
                 goto=None,
                 trialaction=None,
                 setbinstring=None,
                 _comment=None):

        self.id_lno = get_caller_lno()
        self.ctr = ctr
        self.setbin = Check.is_int('setbin', setbin, oknone=True, lno=self.id_lno)
        if self.setbin and self.setbin > 0:
            confirm((len(str(self.setbin)) in range(3, 9)),
                    f'Setbin ({self.setbin}) was not a 3-8 digit value in line# {self.id_lno}',
                    'Please use a 3-8-digit input setbin (depending on the binning strategy)')
        confirm((self.setbin != 0),
                f'Setbin was set to 0 in line# {self.id_lno}',
                '0 is not allowed for SetBin. Please use AUTO or -HB for Auto-binning')
        self.ret = ret
        self.goto = goto
        self.trialaction = trialaction
        self.fitem_obj = None
        if setbinstring is not None:
            confirm(isinstance(setbinstring, str), 'setbinstring must be a string',
                    f'Please use a string for setbinstring in {self.id_lno}')
            confirm(setbin is None, 'setbin and setbinstring cannot be used at the same time',
                                    f'Please use either setbin or setbin string in {self.id_lno}')
            confirm(ctr is not None or '_SHARED_BIN' in setbinstring,
                    'Counter is required when setbinstring is specified',
                    f'Please specify the 8-digit counter to use in line# {self.id_lno} or use ctr = 0 if you do not want a counter generated')
        self.setbinstring = setbinstring
        if _comment is not None:
            # Normalize _comment to a list using the same contract as BaseMethod._comment
            comment_list = to_list(_comment)
            confirm(all(isinstance(item, str) for item in comment_list),
                    f'_comment must be a string or sequence of strings in line# {self.id_lno}',
                    'Please pass a string or sequence of strings to _comment')
            self._comment = comment_list
        else:
            self._comment = None

    @classmethod
    def _key2num(cls, portid):
        """
        Return the int equivalent of portid

        :param portid: rm2 or r0
        :return: int
        """
        if portid.startswith('rm'):
            return int(portid[2:]) * (-1)
        elif portid.startswith('r'):
            return int(portid[1:])
        else:
            raise ErrorUser(f'Unknown portid: [{portid}]',
                            'This should not happen since portid is checked in Fitem()')

    def write_lines(self, portid, tname=None, nextfitem=None, edc=False, setbinstring=None, portctrstring=None, ismtt=None, custom_setbinstring=None):     # BasePort
        """Iterator a list of lines for BasePort()"""

        default_value_NVL = 'Spec(\'TP_Rule.MTT_Rule("Next", "Exit")\')'

        portclass = self.__class__.__name__
        if self.trialaction is None and ismtt:
            raise ErrorUser(f'trialaction not defined for {tname} port {portid} in line#{self.id_lno}. pls define {portid} = {portclass}(trialaction=..)',
                            f'Available options - {default_value_NVL} - NVL Class only or "Exit" (No downflow/VminTC port 4) or "Next" (Downflow enabled)')

        number = self._key2num(portid)
        string_quotes = '"' if Initialize.tosversion == "tos4" else ''

        if ismtt:
            yield f'TrialResult {number}'
        else:
            yield f'Result {number}'

        yield '{'

        # property
        pass_str = 'Pass' if self.ispass else 'Fail'
        if ismtt:
            yield f'    PassFail {pass_str};'
            if isinstance(self.trialaction, Spec):
                string_quotes = ''
                yield f'    TrialAction {string_quotes}{self.trialaction}{string_quotes};'
            else:
                yield f'    TrialAction {string_quotes}{self.trialaction}{string_quotes};'
        else:
            yield f'    Property PassFail = "{pass_str}";'

        # port-level comment (e.g. CAKE_EXCLUDE directives)
        if self._comment:
            for line in to_list(self._comment):
                yield f'    # {line}'

        # setbin - when we have a setbinstring. Skip passing ports unless it's a custom setbinstring
        if setbinstring != '' and (not self.ispass or custom_setbinstring):
            # Initialize.bin_class.update_bin(self.setbin, tname, ismtt)
            if edc and number >= 0:
                edcstring = '##EDC## '
            else:
                edcstring = ''
            yield f'    {edcstring}SetBin {setbinstring};'

        # counter
        if portctrstring:
            yield f'    {portctrstring};'

        # cannot have return and goto
        confirm(not (self.ret is not None and self.goto is not None),
                f'Cannot define both ret and goto at the same time, in line#{self.id_lno}',
                'Pls fix.')

        # return
        if self.ret is not None:
            yield f'    Return {self.ret};'

        # use specified goto
        elif self.goto is not None and self.goto != "NEXT":
            if isinstance(self.goto, (BaseMethod, Fitem)):
                self._validate_flowitem_name(self.goto.get_name())  # they could have passed a reference to an fitem in another flow
                yield f'    GoTo {self.goto.get_name()};'
            elif isinstance(self.goto, str):
                self._validate_flowitem_name(self.goto)  # fitem could be misspelled
                yield f'    GoTo {self.goto};'
            else:
                raise ErrorUser(f'goto must be a string, TestMethod, or Fitem object. Instead, we see a {type(self.goto)} on line {self.id_lno}',
                                'Please provide goto="NEXT", goto="TEST_NAME", goto=testmethod_var, or goto=fitem_var')

        # default goto (next)
        elif self.ispass or edc or self.goto == "NEXT":
            if nextfitem:
                # we don't need to validate the fitem name here because it's the next fitem in the list
                yield f'    GoTo {nextfitem.get_name()};'
            else:
                yield f'    Return 1;'

        yield '}'

    def _validate_flowitem_name(self, fitemname):
        """
        Validates that the given flow item name exists in the current flow.

        :param fitemname: The name of the flow item to validate.
        :raises ErrorUser: if `fitemname` exactly is not found in the current flow
        """
        # find the fitem we're trying to access
        flow_obj = self.fitem_obj.flow_obj
        for fitem in flow_obj.fitem_list:
            if fitem.get_name() == fitemname:
                return  # success
        # if we get to this point, we didn't find it, so we just fail
        raise ErrorUser(f"goto Flow Item name '{fitemname}' is not defined in Flow '{flow_obj.get_name()}' on line {self.id_lno}",
                        f"Check if '{fitemname}' is misspelled or not defined.")


class pPass(BasePort):
    """Passing port for use in an Fitem.

    Note: Cannot have both ret and goto

    Params:
        setbin: Setbin value, int, or AUTO.
            Use positive values to directly set
            Use AUTO or negative values to automatically set. -68 means automatic bin with hardbin=68
        ctr: Counter value, int
        ret: Return value, int
        goto: Goto value, string of test name, "NEXT", or Flow/TestMethod object.
            If not specified, default is "NEXT"
        trialaction: Trial action, string
        setbinstring: Setbin string, used to directly set the bin name instead of setbin
        _comment: Comment string or list of strings to emit inside the Result block after PassFail.
            Useful for tool directives such as CAKE_EXCLUDE_SOFTBINCHECK_NPORT_THIS_IS_DANGEROUS.
    """
    ispass = True


class pFail(BasePort):
    """Failing port for use in an Fitem.

    Note: Cannot have both ret and goto

    Params:
        setbin: Setbin value, int, or AUTO.
            Use positive values to directly set
            Use AUTO or negative values to automatically set. -68 means automatic bin with hardbin=68
        ctr: Counter value, int
        ret: Return value, int
            If not specified, default is 0 for Kill tests
        goto: Goto value, string of test name, "NEXT", or Flow/TestMethod object.
            If not specified, default is "NEXT" for EDC tests
        trialaction: Trial action, string
        setbinstring: Setbin string, used to directly set the bin name instead of setbin
        _comment: Comment string or list of strings to emit inside the Result block after PassFail.
            Useful for tool directives such as CAKE_EXCLUDE_SOFTBINCHECK_NPORT_THIS_IS_DANGEROUS.
    """
    ispass = False


class BaseMethod:
    """This is a Parent Class of the Test method aka, a testinstance"""
    names = {}

    def _init(self, name, vars_dictionary):
        # dictionary that holds the param and values of the object
        self.id_lno = sys._getframe(2).f_lineno
        self.name = Check.is_str('name', name, lno=self.id_lno)
        self.is_mtt = None
        self._fitem_orig = vars_dictionary.get('_fitem')
        self._comment = vars_dictionary.get('_comment')
        ignore_list = ['self', '_fitem', '_comment', 'kwargs']     # kwargs is meant to be thrown away: reason: what if it is typo.
        self.params = {x: y for x, y in vars_dictionary.items() if x not in ignore_list}
        self.fitem_obj = None
        self._common_init()
        self.template_name = self.__class__.__name__
        self.importname = self.__class__.__name__

    def _common_init(self):
        self.counter = -1
        self.fitem = None
        self.register_name(self.name, self.id_lno)

        # Process _fitem
        if self._fitem_orig:
            fitem_obj = self._fitem_orig
            confirm(fitem_obj, 'Expecting fitem_obj to be not None. It is None.',
                    'Pls contact Sudheer if you see this')
            fitem_obj.ti = self    # assign this object into fitem_obj
            self.counter_increment()
            self.fitem = fitem_obj
            self.fitem.ti_counter = self.counter

    def counter_increment(self):
        """Calling counter for different FlowItems - called by Fitem()"""
        self.counter += 1
        return self.counter

    @classmethod
    def register_name(cls, name, lno):
        """Register the name, make sure it's unique"""
        if name in cls.names:
            raise ErrorUser(f'Test {name} is already used in line# {lno} and line# {cls.names[name]}',
                            'This is not allowed. Test names must be unique')
        cls.names[name] = lno

    def get_method_name(self):
        """Return the name of the test class"""
        return self.importname

    @classmethod
    def clear_names(cls):
        """Clear the names"""
        cls.names = {}

    def get_name(self):
        """Return the name"""
        return self.name

    def write_lines(self, ti_counter, is_mtt=False, edc=False):    # BaseMethod
        """
        Iterator a list of lines for this testinstance
        :param ti_counter: Counter number
        :param is_mtt: Set to True for mtt instance
        :return: lines
        """
        if Initialize.tosversion == "tos4":
            testmethod_precursor = 'CSharp'
        else:
            testmethod_precursor = ''

        if ti_counter == 0:
            tname = self.name
        else:
            if is_mtt:
                tname = f'{self.name} + "_{ti_counter}"'    # In MTT, the testname is an expression
            else:
                tname = f'{self.name}_{ti_counter}'

        templatename = self.__class__.__name__

        if is_mtt:
            yield f'{testmethod_precursor}TrialTest {templatename} {tname}'
        else:
            yield f'{testmethod_precursor}Test {templatename} {tname}'

        yield '{'
        if self._comment:
            for line in to_list(self._comment):
                yield f'    # {line}'
        default_params = Initialize.default_class.default_params()
        for param in self._param_sort(self.params):
            if param in ('name', '_comment'):
                continue    # Do not write this special param
            val = self.params[param]
            if val is None or val is required or val is optional:
                # check for default value
                if templatename in default_params and param in default_params[templatename]:
                    val = default_params[templatename][param]
                else:
                    continue    # Do not write None values

            # Below code handles auto-basenumbering

            if "basenumber" in param.lower():
                # When PDE wants to use auto basenumbering
                if int(val) < 0:
                    val = Initialize.basenumber.get_auto_basenumber(val, self.name, self.id_lno)
                # Update the basenum dict to track basenums
                Initialize.basenumber.update_autobasedict(val, self.name)

            # Below code takes care of TrialParams and Torch based rules so that the output is without strings
            if isinstance(val, Spec):
                yield f'    {param} = {val};'
            elif isinstance(val, TrialParamSpec):
                yield f'    TrialParam {param} = {val};'
            elif isinstance(val, str):
                yield f'    {param} = "{val}";'
            else:
                yield f'    {param} = {val};'

        if not is_mtt:
            yield '}'
            yield ''

    def _param_sort(self, params):
        """return the order of params, PLT first for example, specified in _order"""
        # important first
        for key in Initialize.param_order:
            if key in params:
                yield key

        # the rest of the params sorted
        for key in sorted(params.keys() - set(Initialize.param_order)):
            yield key


class MultiTrial(BaseMethod):
    """This is the test class for MTT tests used at Class"""

    def __init__(self, name, template, trialvar=None, exitaction='Continue', edcexitaction='Restore', _comment=None, _fitem=None, r0=None, r1=None, r2=None, r3=None, r4=None, r5=None, rm1=None, rm2=None, **kwargs):
        self.id_lno = get_caller_lno()
        self.exitaction = Check.is_str('exitaction', exitaction, lno=self.id_lno)

        if IS_UT:
            trialvar = 'IP_CPU_BASE::FlowDomain.Default'
        else:
            if Initialize.tosversion == "tos4" and self.__class__.__name__ != 'NativeMultiTrial':
                raise ErrorUser(f"TOS4 does not support the use of MultiTrial Test class and instead uses NativeMultiTrial()",
                                f"Please import the NativeMultiTrial class and replace the MultiTrial() class in line no. {self.id_lno} with NativeMultiTrial()")

            confirm(trialvar is not None,
                    f"Jan'25 release of Pymtpl requires users to manually define the trialvar value for MTT tests.",
                    f"Please define trialvar in the MTT test {name}. Ex- MultiTrial(name={name}, trialvar=__common__::FlowDomain.GT/CORE)")

        self.trialvar = trialvar
        self.edcexitaction = Check.is_str('edcexitaction', edcexitaction, lno=self.id_lno)
        self.name = Check.is_str('name', name, lno=self.id_lno)
        self.template = Check.is_obj('template', template, BaseMethod, lno=self.id_lno)
        self.ret_dict = Fitem._process_ret_dict(self.id_lno, kwargs, r0, r1, r2, r3, r4, r5, rm1, rm2, edc=False, is_mtt=True)
        self._comment = _comment
        self.is_mtt = True
        self.fitem_obj = None
        self._fitem_orig = _fitem
        self.template_name = self.template.__class__.__name__
        self.importname = self.template.__class__.__name__
        self.params = {}    # This is only used for _fitem, because _common_init() needs it
        if _fitem:
            self.params['_fitem'] = _fitem
        self._common_init()

    def get_method_name(self):
        """Return the name of the test class"""
        return self.importname

    def write_lines(self, ti_counter, edc=False):    # MultiTrial
        """
        Iterator a list of lines for this testinstance
        :param ti_counter: Counter number
        :return: lines
        """
        string_quotes = '"' if Initialize.tosversion == "tos4" else ''
        if ti_counter == 0:
            mttname = self.name
        else:
            mttname = f'{self.name}_{ti_counter}'

        if self._fitem_orig:
            fitemdict = self._fitem_orig.ret_dict
            fitem_lno = self._fitem_orig.id_lno
        elif self.fitem_obj:
            fitemdict = self.fitem_obj.ret_dict
            fitem_lno = self.fitem_obj.id_lno

        keys_missing_in_fitem = set(self.ret_dict.keys()) - set(fitemdict.keys())
        keys_missing_in_mtt = set(fitemdict.keys()) - set(self.ret_dict.keys())

        # If we have a missing port Fitem that is defined in MTT.
        if keys_missing_in_fitem and not keys_missing_in_mtt:
            raise ErrorUser(f"Test ports for {self.name} in line# {self.id_lno} do not match the ports for the Fitem in line# {fitem_lno}.",
                            f"Missing port {keys_missing_in_fitem} in Fitem def. Pls add the necessary ports.")

        # If we have missing port in MTT that is defined in Fitem
        elif not keys_missing_in_fitem and keys_missing_in_mtt:
            raise ErrorUser(f"Test ports for {self.name} in line# {self.id_lno} do not match the ports for the Fitem in line# {fitem_lno}.",
                            f"Missing port {keys_missing_in_mtt} in MTT def. Pls add the necessary ports.")

        # If we have missing ports in both Fitem and MTT.
        elif keys_missing_in_fitem and keys_missing_in_mtt:
            raise ErrorUser(f"Test ports for {self.name} in line# {self.id_lno} do not match the ports for the Fitem in line# {fitem_lno}.",
                            f"Missing port {keys_missing_in_mtt} in MTT definition and {keys_missing_in_fitem} in Fitem definition. Pls add the necessary ports.")

        yield f'MultiTrialTest {mttname}'
        yield '{'
        if self._comment:
            for line in to_list(self._comment):
                yield f'    # {line}'
        yield f'    TrialVariable {self.trialvar};'
        # yield f'    TrialVariableExitAction {self.edcexitaction}'
        if edc:
            yield f'    TrialVariableExitAction {string_quotes}{self.edcexitaction}{string_quotes};'
        else:
            yield f'    TrialVariableExitAction {string_quotes}{self.exitaction}{string_quotes};'

        # Call the BaseMethod write_lines()
        for line in self.template.write_lines(ti_counter, is_mtt=True):
            yield f'    {line}'

        updatesetbinstring = [True]

        # Call the BasePort write_lines() to write the MTT test port information
        for portid, port_obj in sorted(self.ret_dict.items(), key=lambda x: BasePort._key2num(x[0])):
            portobj_type = port_obj.__class__.__name__

            # If MTT item and Flow Item are separate entities and MTT setbin is set to AUTO
            if self._fitem_orig and port_obj.setbin == -1:
                mttsetbin = self._fitem_orig.ret_dict[portid].setbin
            # If MTT item and Flow Item are defined together and MTT setbin is set to AUTO
            elif self.fitem_obj and port_obj.setbin == -1:
                mttsetbin = self.fitem_obj.ret_dict[portid].setbin
            # If MTT setbin is anything other than AUTO we just use that
            else:
                mttsetbin = port_obj.setbin

            # Get setbinstring for auto-binning
            if mttsetbin and mttsetbin > 0:
                # Get setbinstring for auto-binning
                setbinstring = Initialize.mttbinstrategy.get_mtt_setbinstring(setbin=mttsetbin,
                                                                              name=mttname,
                                                                              updatesetbinstring=updatesetbinstring,
                                                                              portid=portid)

            elif mttsetbin and mttsetbin < 0:
                setbinstring = Initialize.mttbinstrategy.update_autosetbinstring(mttsetbin, port_obj.id_lno, portid, mttname, updatesetbinstring, portobj_type, templatename=self.template.name)

            else:
                setbinstring = ''

            # Counter handling for each port
            portctrstring = Initialize.mttctrstrategy.get_ctrstring_update_counterdict(portid, self.template.name, port_obj.ctr, port_obj.id_lno, setbinstring, portobj_type)

            # Now write the port lines
            for line in port_obj.write_lines(portid, mttname, edc=edc, setbinstring=setbinstring, portctrstring=portctrstring, ismtt=True):
                yield f'        {line}'

        yield '    }'
        yield '}'
        yield ''


class NativeMultiTrial(MultiTrial):
    """This is the test class for Native MTT tests used at Class"""

    def write_lines(self, ti_counter, edc=False):    # MultiTrial
        """
        Iterator a list of lines for this testinstance
        :param ti_counter: Counter number
        :return: lines
        """
        string_quotes = '"' if Initialize.tosversion == "tos4" else ''
        if ti_counter == 0:
            mttname = self.name
        else:
            mttname = f'{self.name}_{ti_counter}'

        if self._fitem_orig:
            fitemdict = self._fitem_orig.ret_dict
            fitem_lno = self._fitem_orig.id_lno
        elif self.fitem_obj:
            fitemdict = self.fitem_obj.ret_dict
            fitem_lno = self.fitem_obj.id_lno

        keys_missing_in_fitem = set(self.ret_dict.keys()) - set(fitemdict.keys())
        keys_missing_in_mtt = set(fitemdict.keys()) - set(self.ret_dict.keys())

        # If we have a missing port Fitem that is defined in MTT.
        if keys_missing_in_fitem and not keys_missing_in_mtt:
            raise ErrorUser(f"Test ports for {self.name} in line# {self.id_lno} do not match the ports for the Fitem in line# {fitem_lno}.",
                            f"Missing port {keys_missing_in_fitem} in Fitem def. Pls add the necessary ports.")

        # If we have missing port in MTT that is defined in Fitem
        elif not keys_missing_in_fitem and keys_missing_in_mtt:
            raise ErrorUser(f"Test ports for {self.name} in line# {self.id_lno} do not match the ports for the Fitem in line# {fitem_lno}.",
                            f"Missing port {keys_missing_in_mtt} in MTT def. Pls add the necessary ports.")

        # If we have missing ports in both Fitem and MTT.
        elif keys_missing_in_fitem and keys_missing_in_mtt:
            raise ErrorUser(f"Test ports for {self.name} in line# {self.id_lno} do not match the ports for the Fitem in line# {fitem_lno}.",
                            f"Missing port {keys_missing_in_mtt} in MTT definition and {keys_missing_in_fitem} in Fitem definition. Pls add the necessary ports.")

        yield f'MultiTrialTest {mttname}'
        yield '{'
        if self._comment:
            for line in to_list(self._comment):
                yield f'    # {line}'
        yield f'    TrialVariable {self.trialvar};'
        # yield f'    TrialVariableExitAction {self.edcexitaction}'
        if edc:
            yield f'    TrialVariableExitAction {string_quotes}{self.edcexitaction}{string_quotes};'
        else:
            yield f'    TrialVariableExitAction {string_quotes}{self.exitaction}{string_quotes};'

        # Call the BaseMethod write_lines()
        for line in self.template.write_lines(ti_counter, is_mtt=True):
            yield f'    {line}'

        # Call the BasePort write_lines() to write the MTT test port information
        for portid, port_obj in sorted(self.ret_dict.items(), key=lambda x: BasePort._key2num(x[0])):
            # Native MTT test class does not need setbinstrings and counterstrings
            setbinstring = ''
            portctrstring = ''
            # Now write the port lines
            for line in port_obj.write_lines(portid, mttname, edc=edc, setbinstring=setbinstring, portctrstring=portctrstring, ismtt=True):
                yield f'        {line}'

        yield '    }'
        yield '}'
        yield ''


class BaseDefault:
    """Base class for defaults"""

    # Can be used to override default hardbin and softbin names to be used in bindef files
    bindefdefaults = None

    # Whether hardbins should be written to the sbdef
    write_hardbins_to_sbdef = False
    # Whether softbins should be written to the sbdef
    write_softbins_to_sbdef = True
    # whether databins should be written to the softbin category (false means put them in the databins category)
    leafbins_are_softbins = False
    # additional default binranges to add
    additional_binranges = None
    # HDBI
    is_hdbi = False

    @classmethod
    def default_ports(cls, ret_dict, is_mtt=False, id_lno=None, ti=None):
        pass   # Doing nothing, no default

    @classmethod
    def default_params(cls):
        """
        Return a dictionary per testmethod on default values
        :return: dict
        """
        return {'MyPrimeMethod': {'someparam': '1'}       # used in unittest as default value
                }

    @classmethod
    def get_subbindef_name(cls, module_name):
        """
        Return the subbindef name for the module

        :param module_name: Module name
        :return: str
        """
        return f'{module_name}_SubBinDefinitions.sbdefs'

    @classmethod
    def validate_defaultrmbin(cls, bin, name):
        """Validate the defaultrm1/2bin only allowing -HB"""
        """Set the default thermal and reset bins"""
        if bin is not None:
            confirm(int(bin) < 0 and len(str(bin)) < 4,
                    f'{name} must be a -HB value',
                    f'Please define {name} = -HB value in the Initialize call')
        confirm(bin != -98 and bin != -99,
                f'Pymtpl does not allow {name} to be equal to -98 or -99',
                f'{name} should be equal to your module HB value like -44 or -42 etc.')
        return bin

    @classmethod
    def validate_default_thermal_reset_bins(cls, defaultthermalbin=None, defaultresetbin=None):
        """Set the default thermal and reset bins"""
        if defaultresetbin is not None:
            if isinstance(defaultresetbin, int):
                confirm(len(str(defaultresetbin)) == 8,
                        'defaultresetbin must be an 8 digit value',
                        'Please define an 8-digit value for defaultresetbin')
                confirm(str(defaultresetbin).startswith("90") and str(defaultresetbin)[4:6] == "19",
                        "Mar'25 Release of Pymtpl requires defaultresetbin to start with '90' and have '19' after the HB is defined",
                        'Please define defaultresetbin in the format 90HB19XX')
            elif isinstance(defaultresetbin, tuple):
                for resetbin in defaultresetbin:
                    confirm(len(str(resetbin)) == 8,
                            'defaultresetbin must be an 8 digit value',
                            f'Please define an 8-digit value for {resetbin}')
                    confirm(str(resetbin).startswith("90") and str(resetbin)[4:6] == "19",
                            "Mar'25 Release of Pymtpl requires defaultresetbin to start with '90' and have '19' after the HB is defined",
                            f'Please define {resetbin} in the format 90HB19XX')
            else:
                raise ErrorUser(f"Invalid defaultresetbin value {defaultresetbin}",
                                "defaultresetbin must be a 8-dig integer or a tuple of 8-dig integers - Ex - (90441901, 90451901)")
        cls.defaultresetbin = defaultresetbin

        if defaultthermalbin is not None:
            if isinstance(defaultthermalbin, int):
                confirm(len(str(defaultthermalbin)) == 8,
                        'defaultthermalbin must be an 8 digit value',
                        'Please define an 8-digit value for defaultresetbin')
                confirm(str(defaultthermalbin).startswith("9097"), "Mar'25 Release of Pymtpl requires defaultthermalbin to start with 9097",
                        f"Pls fix defaultthermalbin param in your Initialize call {defaultthermalbin} to be a bin starting with 9097")
            elif isinstance(defaultthermalbin, tuple):
                for thermalbin in defaultthermalbin:
                    confirm(len(str(thermalbin)) == 8,
                            'defaultthermalbin must be an 8 digit value',
                            f'Please define an 8-digit value for {thermalbin}')
                    confirm(str(thermalbin).startswith("9097"), "Mar'25 Release of Pymtpl requires all defaultthermalbin values to start with 9097",
                            f"Pls fix defaultthermalbin param in your Initialize call {thermalbin} to be a bin starting with 9097")
            else:
                raise ErrorUser(f"Invalid defaultthermalbin value {defaultthermalbin}",
                                "defaultthermalbin must be a 8-dig integer or a tuple of 8-dig integers - Ex - (90974401, 90974501)")
        cls.defaultthermalbin = defaultthermalbin

    @classmethod
    def _validate_and_load_default_counters(cls, cfgfile=None):
        """Define in your own defaults class if you want to have default counters"""
        pass  # Do nothing, no default


class MTLdefault(BaseDefault):
    """This class is for DDG default values"""

    @classmethod
    def default_ports(cls, ret_dict, is_mtt=False, id_lno=None, ti=None):
        """
        Set the default ports

        :param ret_dict: port dictionary
        :param is_mtt: True for mtt
        :return:
        """

        if is_mtt:
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(trialaction='Exit', ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(trialaction='Exit', ret=-2)

        else:
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(setbin=-98, ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(setbin=-99, ret=-2)

    @classmethod
    def default_params(cls):
        """
        Return a dictionary per testmethod on default values
        :return: dict
        """
        return {}


class NVLdefault(BaseDefault):
    """This class is for DDG default values on NVL"""

    @classmethod
    def default_ports(cls, ret_dict, is_mtt=False, id_lno=None, ti=None):
        """
        Set the default ports

        :param ret_dict: port dictionary
        :param is_mtt: True for mtt
        :return:
        """

        if is_mtt:
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(trialaction='Exit', ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(trialaction='Exit', ret=-2)

        else:
            if isinstance(ti, Flow):
                # For composite, you do not need setbin and just assign return values
                if 'rm1' not in ret_dict:
                    ret_dict['rm1'] = pFail(ret=-1)
                if 'rm2' not in ret_dict:
                    ret_dict['rm2'] = pFail(ret=-2)
            else:
                if 'rm1' not in ret_dict:
                    ret_dict['rm1'] = pFail(setbin=-98, ret=-1)
                if 'rm2' not in ret_dict:
                    ret_dict['rm2'] = pFail(setbin=-99, ret=-2)

    @classmethod
    def default_params(cls):
        """
        Return a dictionary per testmethod on default values
        :return: dict
        """
        return {}


class DMRdefault(BaseDefault):
    """This class is for DCAI default values on DMR """

    write_hardbins_to_sbdef = True
    write_softbins_to_sbdef = True
    bindefdefaults = {
        # hardbin overrides
        "98": "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN",
        "99": "b99_FAIL_HARDWARE_ERROR",
        # softbin overrides
        "9801": "9801_FAIL_TESTCLASS_EXCEPTION_ERROR"
    }
    product_defaultrm1bin = None
    product_defaultrm2bin = None

    @classmethod
    def default_params(cls):
        """
        Return a dictionary per testmethod on default values
        :return: dict
        """
        return {}

    @classmethod
    def get_subbindef_name(cls, module_name):
        """
        Return the subbindef name for the module

        :param module_name: Module name
        :return: str
        """
        return f'{module_name}.sbdefs'

    @classmethod
    def default_ports(cls, ret_dict, is_mtt=False, id_lno=None, ti=None):
        """
        Set the default ports

        :param ret_dict: port dictionary
        :param is_mtt: True for mtt
        :return:
        """

        if isinstance(ti, Flow):  # For composite, you do not need setbin and just assign return values
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(ret=-2)
        else:  # test instances
            cls.set_rm_port(ret_dict, 'rm1', id_lno, Initialize.defaultrm1bin if Initialize.defaultrm1bin is not None else cls.product_defaultrm1bin)
            cls.set_rm_port(ret_dict, 'rm2', id_lno, Initialize.defaultrm2bin if Initialize.defaultrm2bin is not None else cls.product_defaultrm2bin)

    @classmethod
    def validate_defaultrmbin(cls, bin, name):
        """Validate the defaultrm1/2bin without having long duplicated code"""
        if bin is not None:
            # negative numbers must be -HB values
            if (isinstance(bin, int) and bin < 0):
                confirm(bin < 0 and len(str(bin)) <= 5,  # up to -HBSB
                        f'Negative {bin} must be a -HB value',
                        f'Please define {name}=-HB value in the Initialize call')
                confirm(bin != -98 and bin != -99,
                        f'{name} equal to -98 or -99 is not allowed',
                        f'{name} should be equal to your module HB value like -44 or -42 etc.')
            # positive numbers must be 8 digit values
            elif (isinstance(bin, int) and bin >= 0):
                confirm(len(str(bin)) == 8,
                        f'Positive integer {name} must be an 8 digit value',
                        f'Please define an 8-digit value for {name}')
            # If it is a string, it must be a valid bin name
            elif (isinstance(bin, str)):
                binToCheck = '98' if name == 'defaultrm1bin' else '99'
                confirm(bin.startswith("b") and binToCheck in bin,
                        f'Direct set bin {name} must start with b and contain {binToCheck}',
                        f'Please define a bin like b9098123_fail_MIO_DDR_SHARED_BIN_n1')
        # should now be valid
        return bin

    @classmethod
    def set_rm_port(cls, ret_dict, port, id_lno, default):

        # already defined, skip
        if port in ret_dict:  # and default is None: # TODO: implement tuple of default indexed by setbin
            return

        # TODO: Go back and implement tuple of default indexed by setbin
        # r0setbin = None
        # if 'r0' in ret_dict:
        #    r0setbin = ret_dict['r0'].setbin

        setbin = -98 if port == 'rm1' else -99
        ret = -1 if port == 'rm1' else -2
        setbinstring = None
        ctr = None

        if default is not None:
            setbin = None  # this must be none in order for setbinstring to work
            if isinstance(default, int) and int(default) < 0:  # interpret from negative
                setbinstring = cls.hb_or_hbsb_to_rm_setbinstring(default, port, id_lno)
            elif isinstance(default, int) and int(default) > 0:  # direct set 8 dig
                setbinstring = cls.rm_8dig_to_binstring(default, port, id_lno)
            elif isinstance(default, str):
                setbinstring = default
            else:
                raise ErrorUser(f'Invalid value for default{port}bin in line# {id_lno}',
                                'Please use a valid value for default, either a negative hb, 8 digit positive number, or a string')
            ctr = cls.rm_port_counter(port, setbinstring)  # extract counter number from setbinstring
        ret_dict[port] = pFail(setbin=setbin, ret=ret, setbinstring=setbinstring, ctr=ctr)

    @classmethod
    def rm_port_counter(cls, port, setbinstring):
        """Extract counter from setbinstring for rm1 or rm2"""
        confirm(setbinstring.startswith('b90'),
                f'Invalid setbinstring {setbinstring} for {port}',
                f'Please use a valid setbinstring for {port}, starting with b90')
        return int(setbinstring[1:9])  # extract counter number from setbinstring

    # Extract hardbin from setbin, return 909XHB00
    @classmethod
    def hb_or_hbsb_to_rm_setbinstring(cls, hbsb, port, id_lno):
        hbsb_str = str(abs(int(hbsb)))  # make it positive string from a negative int
        hbsb_str_len = len(hbsb_str)

        # make sure we have a valid length
        confirm(hbsb_str_len in (1, 2, 3, 4),
                f"Invalid length of hbsb {hbsb_str_len} for {port} in line# {id_lno}",
                f'Please use a valid value for default{port}bin, either a negative hb, 8 digit positive number, or a string')

        # we can have anywhere from 1 to 4 digits here for HB or HBSB, e.g. 8, 68, 800, 6800
        # ensure len_newbin rounds up to 2 or 4 digits
        if hbsb_str_len == 1:
            hbsb_str = hbsb_str.zfill(2)
        elif hbsb_str_len == 3:
            hbsb_str = hbsb_str.zfill(4)

        bin = '9098' if port == 'rm1' else '9099'
        bin += hbsb_str[:2]  # first two digits, whether 2 or 4 length
        bin += '00'  # last two always 0
        return cls.rm_8dig_to_binstring(bin, port, id_lno)

    @classmethod
    def rm_8dig_to_binstring(cls, bin, port, id_lno):
        confirm(len(str(bin)) == 8 and str(bin).isdigit() and int(bin) > 0,
                f'Invalid value for default{port}bin in line# {id_lno}',
                'Please use a valid value for default, either a negative hb, 8 digit positive number, or a string')
        binstring = 'b' + str(bin) + '_fail_FAIL_'  # by convention
        binstring += 'SYSTEM_SOFTWARE_n1' if port == 'rm1' else 'DPS_ALARM_n2'
        return binstring


class CBRdefault(DMRdefault):
    """This class is for DCAI default values on CBR - AN TPI team"""

    # this should be the only delta from DMR
    write_hardbins_to_sbdef = False
    write_softbins_to_sbdef = False


class CWFdefault(DMRdefault):
    """This class is for default values on CWF - CR TPI team"""

    product_defaultrm1bin = 'SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE'
    product_defaultrm2bin = 'SoftBins.b90999901_fail_FAIL_DPS_ALARM'
    additional_binranges = [(9898, 9898), (9999, 9999)]  # add these so the above always works without having to specify
    leafbins_are_softbins = True

    @classmethod
    def rm_port_counter(cls, port, setbinstring):
        """we don't want counters here for cwf"""
        return 0


class Sortdefault(BaseDefault):
    """This class is for DDG default values on Sort"""

    product_defaultrm1bin = None  # this sets a product-level default rm1 bin, which can be overridden in init
    product_defaultrm2bin = None  # this sets a product-level default rm2 bin, which can be overridden in init

    @classmethod
    def default_ports(cls, ret_dict, is_mtt=False, id_lno=None, ti=None):
        """

        Set default return ports in the ret_dict with appropriate setbin values.

        This method checks if 'rm1' and 'rm2' are present in ret_dict. If not, it sets them using the setbin value
        from 'r0' or a default value. For composite flows, it assigns return values without setbin.

        :param ret_dict: Dictionary containing port information.
        :param is_mtt: Boolean flag indicating if MTT is used.
        :param id_lno: Line number for error reporting.
        :param ti: Test instance or flow.
        """
        if isinstance(ti, Flow):
            # For composite, you do not need setbin and just assign return values
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(ret=-2)
        else:
            cls.set_rm_port(ret_dict, 'rm1', Initialize.defaultrm1bin if Initialize.defaultrm1bin is not None else cls.product_defaultrm1bin, id_lno, -1)
            cls.set_rm_port(ret_dict, 'rm2', Initialize.defaultrm2bin if Initialize.defaultrm2bin is not None else cls.product_defaultrm2bin, id_lno, -2)

    @classmethod
    def set_rm_port(cls, ret_dict, port, default_bin, id_lno, ret_value):
        """
        Set the return port in the ret_dict with the appropriate setbin value.

        This method checks if the specified port is present in ret_dict. If not, it attempts to set the port
        using the setbin value from 'r0' or a default value. If neither is available, it raises an ErrorUser.

        :param ret_dict: Dictionary containing port information.
        :param port: The port to be set in ret_dict.
        :param default_bin: The default setbin value to use if 'r0' is not available.
        :param id_lno: Line number for error reporting.
        :raises ErrorUser: If the port cannot be set due to missing values.
        """

        if port not in ret_dict:
            if 'r0' in ret_dict and ret_dict['r0'].setbin is not None:
                setbin_value = cls.get_setbin_value(ret_dict['r0'].setbin, port)
                ret_dict[port] = pFail(setbin=setbin_value, ret=ret_value)
            elif default_bin is not None:
                ret_dict[port] = pFail(setbin=default_bin, ret=ret_value)
            else:
                raise ErrorUser(f"Jan'25 release of Pymtpl requires {port} for each Fitem as the final bin value depends on the HB value",
                                f"Please define {port}=pFail(...) in line no# {id_lno} or set the param default{port}bin=-HB in Initialize call to use a default value")

    @classmethod
    def get_setbin_value(cls, setbin, port):
        """
        Get the setbin value based on the provided setbin.

        If the setbin value is negative, it returns the setbin as is.
        If the setbin value is positive, it converts the first two digits to a negative integer.

        :param setbin: The setbin value to process.
        :return: The processed setbin value.
        """
        if setbin < 0:
            return setbin
        elif port == 'rm1':
            return int("98" + cls.extract_and_zfill(str(setbin)))
        elif port == 'rm2':
            return int("99" + cls.extract_and_zfill(str(setbin)))

    @classmethod
    def extract_and_zfill(cls, bin_str):
        length = len(bin_str)
        if length in [4, 8]:
            return bin_str[:2].zfill(2)
        elif length in [3, 7]:
            return bin_str[:1].zfill(2)
        return bin_str

    @classmethod
    def default_params(cls):
        """
        Return a dictionary per testmethod on default values
        :return: dict
        """
        return {}


class ClassHBSBXXXXdefault(Sortdefault):
    """This class is for default values on Class using HBSBXXXX binning"""
    require_default_counters = True

    @classmethod
    def default_ports(cls, ret_dict, is_mtt=False, id_lno=None, ti=None):
        """

        Set default return ports in the ret_dict with appropriate setbin values.

        This method checks if 'rm1' and 'rm2' are present in ret_dict. If not, it sets them using the setbin value
        from 'r0' or a default value. For composite flows, it assigns return values without setbin.

        :param ret_dict: Dictionary containing port information.
        :param is_mtt: Boolean flag indicating if MTT is used.
        :param id_lno: Line number for error reporting.
        :param ti: Test instance or flow.
        """

        if isinstance(ti, Flow):
            # For composite, you do not need setbin and just assign return values
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(ret=-2)
        elif is_mtt:
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(trialaction='Exit', ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(trialaction='Exit', ret=-2)
        else:
            cls.set_rm_port(ret_dict, 'rm1', Initialize.defaultrm1bin, id_lno, -1)
            cls.set_rm_port(ret_dict, 'rm2', Initialize.defaultrm2bin, id_lno, -2)

    @classmethod
    def _validate_and_load_default_counters(cls, cfgfile):
        """Validate the defaultcounters JSON file for correct format"""
        try:
            with open(cfgfile, 'r') as f:
                counter_data = json.load(f)

            confirm('Default_Counter_Range' in counter_data,
                    f'defaultcounters file is missing "Default_Counter_Range" key',
                    f'The JSON file should contain {{"Default_Counter_Range": (XXXX, YYYY)}} or {{"Default_Counter_Range": [(XXXX, YYYY), ...]}}')

            counter_range = counter_data['Default_Counter_Range']

            # Check if it's a single tuple/list or a list of tuples/lists
            if isinstance(counter_range, list) and len(counter_range) > 0:
                # Check if first element is a list/tuple (list of ranges) or int (single range)
                if isinstance(counter_range[0], (list, tuple)):
                    # List of ranges
                    for idx, range_item in enumerate(counter_range):
                        confirm(isinstance(range_item, (list, tuple)) and len(range_item) == 2,
                                f'Each range in Default_Counter_Range must have exactly 2 elements, range {idx} has {len(range_item) if isinstance(range_item, (list, tuple)) else "invalid type"}',
                                f'Expected format: {{"Default_Counter_Range": [(XXXX, YYYY), (ZZZZ, AAAA)]}} with integer pairs')

                        confirm(all(isinstance(x, int) for x in range_item),
                                f'Range {idx} values must be integers, got {range_item}',
                                f'Expected format: {{"Default_Counter_Range": [(1000, 2000), (3000, 4000)]}} with integer values')

                        confirm(all(0 <= x <= 9999 for x in range_item),
                                f'Range {idx} values must be between 0 and 9999, got {range_item}',
                                f'Expected format: {{"Default_Counter_Range": [(1000, 2000), (3000, 4000)]}} with values between 0 and 9999')

                        confirm(range_item[0] < range_item[1],
                                f'Range {idx} start value must be less than end value, got {range_item}',
                                f'Expected format where start < end in each (start, end) pair')
                else:
                    # Single range as a list [XXXX, YYYY]
                    confirm(len(counter_range) == 2,
                            f'Default_Counter_Range must have exactly 2 elements for a single range, got {len(counter_range)}',
                            f'Expected format: {{"Default_Counter_Range": (XXXX, YYYY)}} or {{"Default_Counter_Range": [XXXX, YYYY]}}')

                    confirm(all(isinstance(x, int) for x in counter_range),
                            f'Default_Counter_Range values must be integers, got {counter_range}',
                            f'Expected format: {{"Default_Counter_Range": (1000, 2000)}} with integer values')

                    confirm(all(0 <= x <= 9999 for x in counter_range),
                            f'Default_Counter_Range values must be between 0 and 9999, got {counter_range}',
                            f'Expected format: {{"Default_Counter_Range": (1000, 2000)}} with values between 0 and 9999')

                    confirm(counter_range[0] < counter_range[1],
                            f'Default_Counter_Range start value must be less than end value, got {counter_range}',
                            f'Expected format where XXXX < YYYY in (XXXX, YYYY)')
            elif isinstance(counter_range, tuple):
                # Single range as a tuple (XXXX, YYYY)
                confirm(len(counter_range) == 2,
                        f'Default_Counter_Range must have exactly 2 elements, got {len(counter_range)}',
                        f'Expected format: {{"Default_Counter_Range": (XXXX, YYYY)}}')

                confirm(all(isinstance(x, int) for x in counter_range),
                        f'Default_Counter_Range values must be integers, got {counter_range}',
                        f'Expected format: {{"Default_Counter_Range": (1000, 2000)}} with integer values')

                confirm(all(0 <= x <= 9999 for x in counter_range),
                        f'Default_Counter_Range values must be between 0 and 9999, got {counter_range}',
                        f'Expected format: {{"Default_Counter_Range": (1000, 2000)}} with values between 0 and 9999')

                confirm(counter_range[0] < counter_range[1],
                        f'Default_Counter_Range start value must be less than end value, got {counter_range}',
                        f'Expected format where XXXX < YYYY in (XXXX, YYYY)')
            else:
                raise ErrorUser(
                    f'Default_Counter_Range must be a tuple, list, or list of tuples/lists, got {type(counter_range)}',
                    f'Expected format: {{"Default_Counter_Range": (XXXX, YYYY)}} or {{"Default_Counter_Range": [(XXXX, YYYY), (ZZZZ, AAAA)]}}')

        except json.JSONDecodeError as e:
            raise ErrorUser(f'defaultcounters file is not valid JSON: {str(e)}',
                            'Please ensure the file contains valid JSON in the expected format')

        return counter_data['Default_Counter_Range']

    @classmethod
    def _confirm_tuple_same_prefix(cls, input_tuple, prefix_len=2, name='value'):
        """Confirm tuple has exactly two items and both share same first prefix_len chars"""
        range_start, range_end = str(input_tuple[0]), str(input_tuple[1])
        confirm(range_start[:prefix_len] == range_end[:prefix_len],
                f"{name} elements {input_tuple} do not share the same first {prefix_len} characters",
                f"New NVL Class requires {name} to be a range of 8-digit bins. Please provide {name} values with the same leading {prefix_len} characters")

        confirm(int(range_start) < int(range_end),
                f"Invalid {name} range",
                f"The start of the range {range_start} must be less than the end {range_end}.")

    @classmethod
    def _validate_negative_int_with_counters(cls, value, param_name):
        """Validate that an integer is negative and defaultcounters is defined"""
        confirm(value != -98 and value != -99,
                f'Pymtpl does not allow {param_name} to be equal to -98 or -99',
                f'{param_name} should be equal to your module HB value like -44 or -42 etc.')
        confirm(value < 0,
                f'{param_name}, {value} must be a -HB value',
                f'Please define {param_name} = -HB as the value in the Initialize call')
        confirm(Initialize.default_counter_range is not None or not cls.require_default_counters,
                f'{param_name} is set to a negative -HB value, but defaultcounters to use are not defined',
                f'Please contact the Pymtpl support team to set this file up correctly in the repo')

    @classmethod
    def _validate_bin_length(cls, binvalue, expected_lengths, param_name, bin_format):
        """Validate that a bin value has the expected length"""
        actual_length = len(str(binvalue))
        if actual_length not in expected_lengths:
            if len(expected_lengths) == 1:
                msg = f'{param_name} must be {expected_lengths[0]} digit value in the form of {bin_format}'
            else:
                msg = f'Start and Stop values for {param_name} must be a {expected_lengths[0]} or {expected_lengths[-1]} digit value in the form of {bin_format}'
            confirm(False, msg, f'Please define a {expected_lengths[0]} or {expected_lengths[-1]}-digit range value for {param_name}')

    @classmethod
    def _validate_bin_prefix(cls, binvalue, required_prefix, param_name, error_format):
        """Validate that a bin value starts with one of the required prefixes"""
        # Allow required_prefix to be a string or a tuple/list of strings
        prefixes = required_prefix if isinstance(required_prefix, (tuple, list)) else (required_prefix,)
        if not any(str(binvalue).startswith(prefix) for prefix in prefixes):
            raise ErrorUser(
                f"Invalid {param_name} value {binvalue} - New NVL Class binning strategy requires bins to be in the form of {error_format}",
                f"{param_name} must start with one of: {', '.join(prefixes)}")

    @classmethod
    def _validate_negative_prefix(cls, binvalue, negative_prefix, param_name):
        """Validate that a bin value does NOT start with a negative prefix (like '90')"""
        if str(binvalue).startswith(negative_prefix):
            raise ErrorUser(
                f"Invalid {param_name} value {binvalue} - New NVL Class binning strategy requires bins to be in the form of HB19XXXX",
                f"{param_name} cannot start with {negative_prefix}. Please correct that.")

    @classmethod
    def _validate_tuple_of_bins(cls, bin_tuple, config, param_name):
        """Validate a tuple of bin values"""

        confirm(len(bin_tuple) == 2,
                f'{param_name} input range must have exactly 2 elements (start, stop), got {len(bin_tuple)}',
                f'Please provide {param_name} as a 2-value range like (start, stop) with start < stop')

        for binvalue in bin_tuple:
            cls._validate_bin_length(binvalue, config['lengths'], param_name, config['format'])

            # Check for negative prefix (bins that should NOT start with certain values)
            if config.get('negative_prefix'):
                cls._validate_negative_prefix(binvalue, config['negative_prefix'], param_name)
            # Check for required prefix (bins that MUST start with certain values)
            elif config.get('required_prefix'):
                cls._validate_bin_prefix(binvalue, config['required_prefix'], param_name, config['format'])

        cls._confirm_tuple_same_prefix(bin_tuple, name=param_name)

    @classmethod
    def _validate_list_of_bin_ranges(cls, bin_list, config, param_name):
        """Validate a list of bin ranges"""
        for binrange in bin_list:
            confirm(isinstance(binrange, tuple) and len(binrange) == 2,
                    f'{param_name} must be a range of 8-dig integers or a list of ranges with only start and stop defined in the range',
                    f'Please define {param_name} in the form of a range or list of ranges like (start, stop) or [(start1, stop1), (start2, stop2)]')
            cls._validate_tuple_of_bins(binrange, config, param_name)

    @classmethod
    def _validate_bin_parameter(cls, bin_value, param_name, config):
        """Generic validator for bin parameters"""
        if isinstance(bin_value, int):
            cls._validate_negative_int_with_counters(bin_value, param_name)

        elif isinstance(bin_value, tuple):
            cls._validate_tuple_of_bins(bin_value, config, param_name)

        elif isinstance(bin_value, list):
            cls._validate_list_of_bin_ranges(bin_value, config, param_name)

    @classmethod
    def validate_default_thermal_reset_bins(cls, defaultthermalbin=None, defaultresetbin=None):
        """Set the default thermal and reset bins"""

        # Define configurations for each bin type
        reset_config = {
            'lengths': [7, 8],
            'format': 'HB19XXXX',
            'negative_prefix': '90'  # Cannot start with 90
        }

        thermal_config = {
            'lengths': [8],
            'format': '97HBXXXX',
            'required_prefix': ['97', '94']  # Must start with 97 or 94
        }

        # Validate reset bin
        if defaultresetbin is not None:
            cls._validate_bin_parameter(defaultresetbin, 'defaultresetbin', reset_config)
        cls.defaultresetbin = defaultresetbin

        # Validate thermal bin
        if defaultthermalbin is not None:
            cls._validate_bin_parameter(defaultthermalbin, 'defaultthermalbin', thermal_config)
        cls.defaultthermalbin = defaultthermalbin

    @classmethod
    def validate_defaultrmbin(cls, bin, name):
        """Validate the defaultrm1/2bin only allowing -HB"""
        bin_precursor = "98" if name == "defaultrm1bin" else "99"

        if name not in ["defaultrm1bin", "defaultrm2bin"]:
            raise ErrorUser(
                f"Internal error in validate_defaultrmbin for NVLClassdefaultHBSBXXXX with name {name}",
                "Pls contact the Pymtpl team if you see this error")

        rm_config = {
            'lengths': [8],
            'format': f'{bin_precursor}HBXXXX',
            'required_prefix': bin_precursor
        }

        if bin is not None:
            cls._validate_bin_parameter(bin, name, rm_config)

        return bin

    @classmethod
    def set_rm_port(cls, ret_dict, port, default_bin, id_lno, ret_value):
        """
        Set the return port in the ret_dict with the appropriate setbin value.
        """
        # Extract HB from default_bin based on type
        if isinstance(default_bin, tuple):
            default_bin = -int(str(default_bin[0])[2:4])  # take the first value in the range
        elif isinstance(default_bin, list):
            default_bin = -int(str(default_bin[0][0])[2:4])  # take the first value in the first range
        elif isinstance(default_bin, int):
            pass  # already negative HB value

        if port not in ret_dict:
            if 'r0' in ret_dict and ret_dict['r0'].setbin is not None:
                setbin_value = cls.get_setbin_value(ret_dict['r0'].setbin, port)
                ret_dict[port] = pFail(setbin=setbin_value, ret=ret_value)
            elif default_bin is not None:
                ret_dict[port] = pFail(setbin=default_bin, ret=ret_value)
            else:
                raise ErrorUser(
                    f"Unable to extract bin to assign to {port} - New NVL Class binning strategy requires every test to have setbin defined for ports -2 and -1",
                    f"Please define {port}=pFail(...) in line no# {id_lno} or set the param default{port}bin=-HB in Initialize call to use a default value")


class NVLClassdefaultHBSBXXXX(ClassHBSBXXXXdefault):
    """This class is for DDG default values on NVL using HBSBXXXX binning"""
    require_default_counters = True  # require the default_counters.json


class JGSdefault(ClassHBSBXXXXdefault):
    """This class is for DCAI default values on JGS (Jaguar Shores) using HBSBXXXX binning"""
    # TODO: Set up 99HBxxxx in set_rm_port from port 0 once niran enables a solution
    require_default_counters = False
    write_hardbins_to_sbdef = False
    write_softbins_to_sbdef = False
    bindefdefaults = {
        # hardbin overrides
        "98": "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN",
        "99": "b99_FAIL_HARDWARE_ALARM",
        # softbin overrides
        "9801": "9801_FAIL_TESTCLASS_EXCEPTION_ERROR"
    }
    product_defaultrm1bin = None
    product_defaultrm2bin = None

    @classmethod
    def get_subbindef_name(cls, module_name):
        """
        Return the subbindef name for the module

        :param module_name: Module name
        :return: str
        """
        return f'{module_name}.sbdefs'

    @classmethod
    def set_rm_port(cls, ret_dict, port, default_bin, id_lno, ret_value):

        # already defined, skip
        if port in ret_dict:
            return

        # TODO: define setbin as -98HB or -99HB once Niran is ready
        # if 'r0' in ret_dict:
        #    r0setbin = ret_dict['r0'].setbin

        setbin = -98 if port == 'rm1' else -99
        ret = ret_value
        setbinstring = None
        ctr = None

        if default_bin is not None:
            setbin = None  # this must be none in order for setbinstring to work
            if isinstance(default_bin, int) and int(default_bin) < 0:  # interpret from negative
                setbinstring = cls.hb_or_hbsb_to_rm_setbinstring(default_bin, port, id_lno)
            elif isinstance(default_bin, int) and int(default_bin) > 0:  # direct set 8 dig
                setbinstring = cls.rm_8dig_to_binstring(default_bin, port, id_lno)
            else:  # must be string
                confirm(isinstance(default_bin, str),
                        f'Invalid value for default{port}bin in line# {id_lno}',
                        'Please use a valid value for default, either a negative hb, 8 digit positive number, or a string')
                setbinstring = default_bin
            ctr = cls.rm_port_counter(port, setbinstring)  # extract counter number from setbinstring
        ret_dict[port] = pFail(setbin=setbin, ret=ret, setbinstring=setbinstring, ctr=ctr)

    @classmethod
    def rm_port_counter(cls, port, setbinstring):
        """Extract counter from setbinstring for rm1 or rm2"""
        confirm((port == 'rm1' and setbinstring.startswith('b98')) or (port == 'rm2' and setbinstring.startswith('b99')),
                f'Invalid setbinstring {setbinstring} for {port}',
                f'Please use a valid setbinstring for {port}, starting with b9x')
        return int(setbinstring[1:9])  # extract counter number from setbinstring

    @classmethod
    def hb_or_hbsb_to_rm_setbinstring(cls, hbsb, port, id_lno):
        # Extract hardbin from setbin, return 9XHB0000
        hbsb_str = str(abs(int(hbsb)))  # make it positive string from a negative int
        hbsb_str_len = len(hbsb_str)

        # make sure we have a valid length
        confirm(hbsb_str_len in (1, 2, 3, 4),
                f"Invalid length of hbsb {hbsb_str_len} for {port} in line# {id_lno}",
                f'Please use a valid value for default{port}bin, either a negative hb, 8 digit positive number, or a string')

        # we can have anywhere from 1 to 4 digits here for HB or HBSB, e.g. 8, 68, 800, 6800
        # ensure len_newbin rounds up to 2 or 4 digits
        if hbsb_str_len == 1:
            hbsb_str = hbsb_str.zfill(2)
        elif hbsb_str_len == 3:
            hbsb_str = hbsb_str.zfill(4)

        bin = '98' if port == 'rm1' else '99'
        bin += hbsb_str[:2]  # first two digits, whether 2 or 4 length
        bin += '0000'  # last four always 0
        return cls.rm_8dig_to_binstring(bin, port, id_lno)

    @classmethod
    def rm_8dig_to_binstring(cls, bin, port, id_lno):
        confirm(len(str(bin)) == 8 and str(bin).isdigit() and int(bin) > 0,
                f'Invalid value for default{port}bin in line# {id_lno}',
                'Please use a valid value for default, either a negative hb, 8 digit positive number, or a string')
        binstring = 'b' + str(bin) + '_fail_FAIL_'  # by convention
        binstring += 'SYSTEM_SOFTWARE_n1' if port == 'rm1' else 'DPS_ALARM_n2'
        return binstring

    @classmethod
    def validate_defaultrmbin(cls, bin, name):
        """Validate the defaultrm1/2bin without having long duplicated code"""
        if bin is not None:
            # negative numbers must be -HB values
            if (isinstance(bin, int) and bin < 0):
                confirm(bin < 0 and len(str(bin)) <= 5,  # up to -HBSB
                        f'Negative {bin} must be a -HB value',
                        f'Please define {name}=-HB value in the Initialize call')
                confirm(bin != -98 and bin != -99,
                        f'{name} equal to -98 or -99 is not allowed',
                        f'{name} should be equal to your module HB value like -44 or -42 etc.')
            # positive numbers must be 8 digit values
            elif (isinstance(bin, int) and bin >= 0):
                confirm(len(str(bin)) == 8,
                        f'Positive integer {name} must be an 8 digit value',
                        f'Please define an 8-digit value for {name}')
            # If it is a string, it must be a valid bin name
            elif (isinstance(bin, str)):
                binToCheck = '98' if name == 'defaultrm1bin' else '99'
                confirm(bin.startswith("b") and binToCheck in bin,
                        f'Direct set bin {name} must start with b and contain {binToCheck}',
                        f'Please define a bin like b98123456_fail_MIO_DDR_SHARED_BIN_n1')
            else:  # broken
                raise ErrorUser(f"Error, default rm1/2bin {bin} is not valid. Expecting -HB, 8 digit positive number, or a string starting with b98/b99")
        # should now be valid
        return bin


class TestChipdefault(ClassHBSBXXXXdefault):
    """Default configuration for Test Chip product initialization.

    Simplified binning/counter strategy for Test Chip products. Does not require default_counters.json,
    does not write bins to .sbdefs, and auto-populates rm1/rm2 ports with -98/-99 defaults.

    :cvar require_default_counters: Does not require default_counters.json (False)
    :cvar write_hardbins_to_sbdef: Skip writing hardbins to .sbdefs (False)
    :cvar write_softbins_to_sbdef: Skip writing softbins to .sbdefs (False)
    :cvar product_defaultrm1bin: No product-level rm1 default (None)
    :cvar product_defaultrm2bin: No product-level rm2 default (None)
    """
    require_default_counters = False
    write_hardbins_to_sbdef = False
    write_softbins_to_sbdef = False
    product_defaultrm1bin = None
    product_defaultrm2bin = None

    @classmethod
    def get_subbindef_name(cls, module_name):
        """
        Return the subbindef name for the module

        :param module_name: Module name
        :return: str
        """
        return f'{module_name}.sbdefs'

    @classmethod
    def validate_defaultrmbin(cls, bin, name):
        """Validate the defaultrm1/2bin without having long duplicated code"""
        if bin is not None:
            # negative numbers must be -HB values
            if (isinstance(bin, int) and bin < 0):
                confirm(bin < 0 and len(str(bin)) <= 5,  # up to -HBSB
                        f'Negative {bin} must be a -HB value',
                        f'Please define {name}=-HB value in the Initialize call')
                confirm(bin != -98 and bin != -99,
                        f'{name} equal to -98 or -99 is not allowed',
                        f'{name} should be equal to your module HB value like -44 or -42 etc.')
            # positive numbers must be 8 digit values
            elif (isinstance(bin, int) and bin >= 0):
                confirm(len(str(bin)) == 8,
                        f'Positive integer {name} must be an 8 digit value',
                        f'Please define an 8-digit value for {name}')
            # If it is a string, it must be a valid bin name
            elif (isinstance(bin, str)):
                binToCheck = '98' if name == 'defaultrm1bin' else '99'
                confirm(bin.startswith("b") and binToCheck in bin,
                        f'Direct set bin {name} must start with b and contain {binToCheck}',
                        f'Please define a bin like b98123456_fail_MIO_DDR_SHARED_BIN_n1')
            else:  # broken
                raise ErrorUser(f"Error, default rm1/2bin {bin} is not valid. Expecting -HB, 8 digit positive number, or a string starting with b98/b99")
        # should now be valid
        return bin

    @classmethod
    def default_ports(cls, ret_dict, is_mtt=False, id_lno=None, ti=None):
        """

        Set default return ports in the ret_dict with appropriate setbin values.

        This method checks if 'rm1' and 'rm2' are present in ret_dict. If not, it sets them using the setbin value
        from 'r0' or a default value. For composite flows, it assigns return values without setbin.

        :param ret_dict: Dictionary containing port information.
        :param is_mtt: Boolean flag indicating if MTT is used.
        :param id_lno: Line number for error reporting.
        :param ti: Test instance or flow.
        """

        if isinstance(ti, Flow):
            # For composite, you do not need setbin and just assign return values
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(ret=-2)
        elif is_mtt:
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(trialaction='Exit', goto='NEXT')
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(trialaction='Exit', goto='NEXT')
        else:
            if 'rm1' not in ret_dict:
                ret_dict['rm1'] = pFail(ret=-1)
            if 'rm2' not in ret_dict:
                ret_dict['rm2'] = pFail(ret=-2)
            if 'r0' not in ret_dict:
                ret_dict['r0'] = pFail(goto='NEXT')


class HDBIDefault(NVLdefault):
    """This class is for HDBI default values on HDbi"""

    # Can be used to override default hardbin and softbin names to be used in bindef files
    bindefdefaults = None
    # Whether hardbins should be written to the sbdef
    write_hardbins_to_sbdef = False
    # Whether softbins should be written to the sbdef
    write_softbins_to_sbdef = True
    # whether databins should be written to the softbin category (false means put them in the databins category)
    leafbins_are_softbins = True
    # additional default binranges to add
    additional_binranges = None
    # HDBI
    is_hdbi = True


class Spec(str):
    """
    This class is used to output params without quotes.
    - Useful for uservars or any other non-integer value you want without quotes.
    - For example, Spec('TP_KNOB.Active_TDAUPins') will output TP_KNOB.Active_TDAUPins without quotes.
    """
    pass


class TrialParamSpec(str):
    pass


class Import:
    """Import is used to import files or test classes
    Uses quotes for TOS4 products, no quotes for TOS3.
    Example:
    - Import('PTH_DTS.usrv') translates to Import "PTH_DTS.usrv"; in the output mtpl
    """

    _import_registry_name = []    # list of Import() names

    def __init__(self,
                 name,               # name of the Import
                 ):
        self.id_lno = get_caller_lno()
        self.name = Check.is_str('name', name, lno=self.id_lno)
        self._import_registry_name.append(self.name)

    @classmethod
    def get_import_registry(cls):
        return cls._import_registry_name

    @classmethod
    def clear_registry(cls):
        cls._import_registry_name.clear()


class MtplComment:

    """MtplComment object"""
    _mtpl_comment_registry_name = []    # list of MtplComment() names

    def __init__(self,
                 name,               # name of the MtplComment
                 ):
        self.id_lno = get_caller_lno()
        self.name = Check.is_str('name', name, lno=self.id_lno)
        self._mtpl_comment_registry_name.append(self.name)

    @classmethod
    def get_import_registry(cls):
        return cls._mtpl_comment_registry_name

    @classmethod
    def clear_registry(cls):
        cls._mtpl_comment_registry_name.clear()


class MConfig:
    """Helps generate the mconfig file in the output dir"""

    _mconfig_registry = []

    def __init__(self,
                 path=None,         # Path to the pattern folder
                 rev=None,          # Pattern revision folder
                 patch=None,        # Pattern patch folder
                 plistinfo=None,    # Plistinfo - Can be a string, list or dict -
                                    #       Dict in the form of {'plist':'bom'} or {'plist1':['bom1', 'bom3'], 'plist2':'bom2'}
                 rootname=None,     # Rootname - PORRoot or ENGRoot
                 alephfiles=None,   # Aleph files - Can be a string or list or dict -
                                    #       Dict in the form of {'aleph':'bom'} or {'aleph1':['bom1', 'bom3'], 'aleph2':'bom2'}
                 patpaths=None,     # Patpaths - Can be a string or list
                 bom=None,          # Bom group
                 patternip=None,    # IP attribute for pattern block (PORRoot/ENGRoot)
                 ip=None):          # ipblock for IPName tag

        self.id_lno = get_caller_lno()
        self._add_to_mconfig_registry()
        # Check to ensure Initialize statement is defined before MConfig is defined.
        # MConfig registries are clearead during Initialize call. Calling Initialize after MConfig clears MConfig definitions.
        # So need Initialize defined before this.
        Initialize.is_initialized(self.id_lno)

        self.patdata = []      # This is list of patdata blocks
        self.ipdata = []       # This is list of ip
        self.alephdata = []       # This is list of ip

        if path:
            self.pattern(path, rev, patch, plistinfo, rootname, alephfiles, patpaths, bom, patternip)
        if ip:
            self.ipname(ip)

    def _add_to_mconfig_registry(self):
        """Add in registry list just after self"""
        self._mconfig_registry.append(self)

    @classmethod
    def get_mconfig_registry(cls):
        """Gets list of Mconfig items"""
        return cls._mconfig_registry

    @classmethod
    def clear_registry(cls):
        """Clear the registry"""
        cls._mconfig_registry = []

    def ipname(self, ip):
        """ipblock"""
        self.ipdata.append({'ip': ip})

    def pattern(self, path, rev, patch, plistinfo, rootname=None, alephfiles=None, patpaths=None, bom=None, ip=None):
        """Pattern block"""
        block = {'path': path,
                 'rev': rev,
                 'patch': patch,
                 'plistinfo': plistinfo,
                 'alephfiles': alephfiles,
                 'patpaths': patpaths,
                 'bom': bom,
                 'ip': ip,
                 'rootname': rootname if rootname else 'PORRoot'}

        if not isinstance(plistinfo, (str, list, dict)):
            raise ErrorUser(f"Incorrect input for plistinfo",
                            f"Plistinfo is always needed and must be either a plist string, list or a dict in the form of {{'plist':'bom'}}."
                            f"Ex - A.plist or ['A.plist', 'B.plist'] or {{'A.plist': 'A'}}")

        if isinstance(plistinfo, dict):
            confirm(bom is None,
                    f"BOM is being defined in the pattern block and in the plist info block. This is not allowed.",
                    f"Pls remove bom {bom} from MConfig pattern block in line# {self.id_lno}")

        if alephfiles and not (isinstance(alephfiles, (str, list, dict))):
            raise ErrorUser(f"Incorrect input for alephfiles",
                            f"Input must be either a  string or a list of Aleph files. Ex - file1.json or ['file1.json', 'file2.json'] or {{'file.json':'bom'}}")

        if isinstance(alephfiles, dict):
            confirm(bom is None,
                    f"BOM is being defined in the pattern block and in the aleph files block. This is not allowed.",
                    f"Pls remove bom {bom} from MConfig pattern block in line# {self.id_lno}")

        if patpaths and not (isinstance(patpaths, (str, list))):
            raise ErrorUser(f"Incorrect input for patpaths",
                            f"Input must be either a  string or a list of patpaths. Ex - '/path/folder' n or ['/path/folder1', '/path/folder2']")

        self.patdata.append(block)

    def aleph(self, alephfiles=None):
        """Aleph file block outside the pattern block - These are aleph files defined relative to module"""
        alephblock = {'alephfiles': alephfiles}
        if alephfiles and not (isinstance(alephfiles, (str, list, dict))):
            raise ErrorUser(f"Incorrect input for alephfiles",
                            f"Input must be either a  string or a list of Aleph files. Ex - file1.json or ['file1.json', 'file2.json'] or {{'file.json':'bom'}}")

        self.alephdata.append(alephblock)

    def write_lines(self):
        """Iterator for the entire file"""
        yield '<?xml version="1.0" encoding="UTF-8"?>'
        yield '<ModuleConfiguration>'

        # Patterns block
        if self.patdata:
            yield '    <Patterns>'
            for _block in self.patdata:
                block = DictDot(_block)
                bm = f'BomGroup="{block.bom}" ' if block.bom else ''
                ip_attr = f'IP="{block.ip}" ' if block.ip else ''
                if block.rootname == 'ENGRoot':
                    yield f'        <{block.rootname} {bm}{ip_attr}Path="{block.path}">'
                else:
                    yield f'        <{block.rootname} {bm}{ip_attr}Path="{block.path}" Rev="{block.rev}" Patch="{block.patch}">'
                yield '            <PlistFiles>'
                if isinstance(block.plistinfo, str):
                    yield f'                <PlistFile>{block.plistinfo}</PlistFile>'
                elif isinstance(block.plistinfo, list):
                    for plist in block.plistinfo:
                        yield f'                <PlistFile>{plist}</PlistFile>'
                elif isinstance(block.plistinfo, dict):
                    for plist in block.plistinfo:
                        if block.plistinfo[plist]:
                            if isinstance(block.plistinfo[plist], list):
                                for bomgroup in block.plistinfo[plist]:
                                    yield f'                <PlistFile BomGroup="{bomgroup}">{plist}</PlistFile>'
                            else:
                                yield f'                <PlistFile BomGroup="{block.plistinfo[plist]}">{plist}</PlistFile>'
                        else:
                            yield f'                <PlistFile>{plist}</PlistFile>'
                yield '            </PlistFiles>'

                if block.alephfiles:
                    yield '            <AlephFiles>'
                    if isinstance(block.alephfiles, str):
                        yield f'                <AlephFile>{block.alephfiles}</AlephFile>'
                    elif isinstance(block.alephfiles, list):
                        for alephfile in block.alephfiles:
                            if isinstance(alephfile, str):
                                yield f'                <AlephFile>{alephfile}</AlephFile>'
                    elif isinstance(block.alephfiles, dict):
                        for alephfile in block.alephfiles:
                            if block.alephfiles[alephfile]:
                                if isinstance(block.alephfiles[alephfile], list):
                                    for bomgroup in block.alephfiles[alephfile]:
                                        yield f'                <AlephFile BomGroup="{bomgroup}">{alephfile}</AlephFile>'
                                else:
                                    yield f'                <AlephFile BomGroup="{block.alephfiles[alephfile]}">{alephfile}</AlephFile>'
                            else:
                                yield f'                <AlephFile>{alephfile}</AlephFile>'
                    yield '            </AlephFiles>'

                if block.patpaths:
                    yield '            <PatPaths>'
                    if isinstance(block.patpaths, str):
                        yield f'                <PatPath>{block.patpaths}</PatPath>'
                    elif isinstance(block.patpaths, list):
                        for patpath in block.patpaths:
                            if isinstance(patpath, str):
                                yield f'                <PatPath>{patpath}</PatPath>'
                    yield '            </PatPaths>'
                yield f'        </{block.rootname}>'

            yield '    </Patterns>'

        # AlephFiles block
        if self.alephdata:
            yield '    <AlephFiles>'
            for _alephblock in self.alephdata:
                alephblock = DictDot(_alephblock)
                if isinstance(alephblock.alephfiles, str):
                    yield f'        <AlephFile>{alephblock.alephfiles}</AlephFile>'
                elif isinstance(alephblock.alephfiles, list):
                    for alephfile in alephblock.alephfiles:
                        if isinstance(alephfile, str):
                            yield f'        <AlephFile>{alephfile}</AlephFile>'
                elif isinstance(alephblock.alephfiles, dict):
                    for alephfile in alephblock.alephfiles:
                        if alephblock.alephfiles[alephfile]:
                            if isinstance(alephblock.alephfiles[alephfile], list):
                                for bomgroup in alephblock.alephfiles[alephfile]:
                                    yield f'        <AlephFile BomGroup="{bomgroup}">{alephfile}</AlephFile>'
                            else:
                                yield f'        <AlephFile BomGroup="{alephblock.alephfiles[alephfile]}">{alephfile}</AlephFile>'
                        else:
                            yield f'        <AlephFile>{alephfile}</AlephFile>'
            yield '    </AlephFiles>'

        # IPName block
        if self.ipdata:
            for block in self.ipdata:
                yield f'    <IPName>{block["ip"]}</IPName>'

        yield '</ModuleConfiguration>'


class Initialize:
    """
    Set and Clears stuff at the start of the py file
    This class is used as a class method.
    During __init__, all the class attributes are cleared.
    """
    outfile = None             # Path to the output mtpl file
    module_name = None         # TestPlan name
    default_class = None       # class for defaults
    flowdefs = None            # flowdefs object
    written = None             # Flag for write. None on very first, False for not Written.
    tosversion = None          # value of tosversion
    basenumber = None
    ctrstrategy = None
    nonmttbinstrategy = None
    mttbinstrategy = None
    nonmttctrstrategy = None
    mttctrstrategy = None
    tos_softbinstr = None
    tpobj = None
    _param_order_default = 'Patlist LevelsTc TimingsTc'.split()      # Default order
    param_order = _param_order_default
    defaultthermalbin = None
    defaultresetbin = None
    defaultrm1bin = None
    defaultrm2bin = None
    autobinignorelist = None
    bom = None
    bindefdict = None
    write_hardbins_to_sbdef = None
    write_softbins_to_sbdef = None
    leafbins_are_softbins = None
    missing_setbin_warning_count = 0  # Counter for missing setbin warnings

    def __init__(self,
                 outfile,
                 module_name,
                 binrange=[],
                 nonmttbinstrategy=None,
                 mttbinstrategy=None,
                 ctrstrategy=None,
                 nonmttctrstrategy=None,
                 mttctrstrategy=None,
                 defaults=BaseDefault,
                 basenumrange=[],
                 forceflwfilegen=False,
                 basenumberstrategy=None,
                 paramorder=None,
                 tosversion="tos3",
                 defaultthermalbin=None,
                 defaultresetbin=None,
                 defaultrm1bin=None,
                 defaultrm2bin=None,
                 edcportctrbinrange=[],
                 autobinignorelist=None,
                 deprecation_warning=False,
                 bom=None,
                 bindefovrd=None,
                 writehardbinstosbdef=None,
                 writesoftbinstosbdef=None,
                 leafbinsaresoftbins=None,
                 usebinctrfrommtpl=False,
                 ctrrangeforbins=[]
                 ):
        """
        :param outfile: Path to the output mtpl file
        :param module_name: module name string that go into TestPlan
        :param binrange: range of bins for this module
        :param nonmttbinstrategy: The binning class to use for assigning bins to non mtt tests
        :param mttbinstrategy: The binning class to use for assigning bins to mtt tests
        :param ctrstrategy: Deprecated param left over to allow users to switch to new params
        :param nonmttctrstrategy: The counter class to use for assigning unique counters to non mtt tests
        :param mttctrstrategy: The counter class to use for assigning counters to mtt tests
        :param defaults: Specify the defaults class to use
        :param basenumrange: range of basenums for this module
        :param forceflwfilegen: bool for forcing flow file gen or not for this module.
        :param paramorder: param to allow users to specify the order of the test method output params.
        :param tosversion: Sets the TOS version. Supported values are 'tos3' and 'tos4'.
        :param defaultthermalbin: Default thermal bin for the module in the form of 90HBSBXX
        :param defaultresetbin: Default reset bin for the module in the form of 90HBSBXX
        :param defaultrm1bin: Default software bin for rm1 in the format of -HB, 8 digit bin, or string full bin name
        :param defaultrm2bin: Default clamp bin for port -2 in the format of -HB, 8 digit bin, or string full bin name
        :param bindefovrd: Dictionary of string to string which allows bin name overrides
        :param writehardbinstosbdef: Whether hardbins should be written to the sbdef. Overrides product setting.
        :param writesoftbinstosbdef: Whether softbins should be written to the sbdef. Overrides product setting.
        :param leafbinsaresoftbins: Whether leaf bins are considered soft bins (True) or data bins (False). Overrides product setting.
        :param usebinctrfrommtpl: Whether to use bins and counters from MTPL rather than Autobinner or Autocounter files
        :param ctrrangeforbins: Counter range to use for bins when users want to specify specific counter ranges for bins.
        """

        # Issue a warning if using deprecated defaults
        if not IS_UT:
            if defaults == MTLdefault and deprecation_warning:
                print('======================================================================================\n',
                      '-i- Info: If you are working on NVL, pls use InitializeNVLClass or InitializeNVLSort.\n',
                      '-i- Suggestion : Please perform a one time deletion of the PymtplInputfiles folder\n',
                      '                 before using InitializeNVLClass or InitializeNVLSort.\n',
                      '=====================================================================================')
            # Issue a error if using deprecated defaults
            if defaults == NVLdefault and deprecation_warning:
                raise ErrorUser("The InitializeNVL call has been deprecated and replaced.",
                                "Please import InitializeNVLClass or InitializeNVLSort in your import and use them instead.")

        if ctrstrategy is not None:
            raise ErrorUser("The Jan'25 Pymtpl release replaced the 'ctrstrategy' Initialize parameter with 'mttctrstrategy' and 'nonmttctrstrategy'.",
                            "Pls update Initialize call in your code to define 'mttctrstrategy' and 'nonmttctrstrategy'.")

        cls = self.__class__

        # Write first if it is not written yet
        if cls.written is False:
            PyMtpl.write()

        # Initialize
        cls.flowdefs = None
        cls.nonmttbinstrategy = BinSSB if not nonmttbinstrategy else nonmttbinstrategy
        cls.mttbinstrategy = MTTBinSSB if not mttbinstrategy else mttbinstrategy
        cls.nonmttctrstrategy = CtrHBSB if not nonmttctrstrategy else nonmttctrstrategy
        cls.mttctrstrategy = MTTCtrHBSB if not mttctrstrategy else mttctrstrategy
        cls.basenumber = BaseNumber if not basenumberstrategy else basenumberstrategy
        cls.default_class = defaults
        cls.forceflwfilegen = forceflwfilegen
        cls.module_name = module_name
        cls.bom = bom
        cls.param_order = cls._param_order_default if not paramorder else paramorder

        # By default, take the BINDEF_DICT, but then allow for overriding at the Defaults and Initialize levels
        cls.bindefdict = BINDEF_DICT.copy()
        if cls.default_class.bindefdefaults is not None:
            cls.bindefdict.update(cls.default_class.bindefdefaults)
        if bindefovrd is not None:
            cls.bindefdict.update(bindefovrd)

        # Defaults for writing bins to sbdef. Priority is User > Product Defaults > Base Defaults
        cls.write_hardbins_to_sbdef = writehardbinstosbdef if writehardbinstosbdef is not None else cls.default_class.write_hardbins_to_sbdef
        cls.write_softbins_to_sbdef = writesoftbinstosbdef if writesoftbinstosbdef is not None else cls.default_class.write_softbins_to_sbdef
        cls.leafbins_are_softbins = leafbinsaresoftbins if leafbinsaresoftbins is not None else cls.default_class.leafbins_are_softbins

        # Defaults for using mtpl for bin and counter information.
        cls.usebinctrfrommtpl = usebinctrfrommtpl

        self.set_outfile(outfile)
        tpdir = os.path.realpath(cls.get_outfile())
        for _ in range(6):  # 4 levels up
            cfgfile = glob.glob(os.path.join(tpdir, 'BaseInputs', '*', '*_Files', 'default_counter_dict.json'))
            if cfgfile:
                if len(cfgfile) == 1:
                    cls.default_counter_range = cls.default_class._validate_and_load_default_counters(cfgfile[0])
                    break
                else:
                    # Skip if multiple config files found
                    log.warning(f'Multiple default_counter_dict.json files found: {cfgfile}. Setting default_counter_range to None.')
                    cls.default_counter_range = None
                    break
            tpdir = os.path.dirname(tpdir)
        else:
            cls.default_counter_range = None
        self.set_tosversion(tosversion)
        self.set_thermal_reset_bins(defaultthermalbin, defaultresetbin)
        self.set_default_clamp_software_bins(defaultrm1bin, defaultrm2bin)

        Flow.clear_registry()
        MConfig.clear_registry()
        Import.clear_registry()
        MtplComment.clear_registry()
        BaseMethod.clear_names()
        UserVars.clear_registry()
        cls.missing_setbin_warning_count = 0  # Reset warning counter

        # Start reading the mtpl to load information about bin and counters
        BaseMtplInfo.clear_base_mtpl_dutflowinfo()
        BaseMtplInfo.load_mtpl_dutflow_map()

        # Use BaseBin because autobindict is shared between MTT and non-MTT.
        cls.nonmttbinstrategy.clear_bins()
        cls.set_binrange(binrange)
        if ctrrangeforbins:
            cls.set_ctrrange_for_bins(ctrrangeforbins)
        cls.nonmttbinstrategy.separate_bin_ranges()  # NEW: separate 4-dig and 8-dig ranges
        cls.nonmttbinstrategy.load_8dig_bins_from_common_bindef()
        cls.nonmttbinstrategy.load_ignore_bins(autobinignorelist)
        cls.nonmttbinstrategy.load_autobininfo_from_mtpl()
        cls.nonmttbinstrategy.load_autobinfile()
        cls.nonmttbinstrategy.set_default_thermal_reset_bins()

        cls.nonmttctrstrategy.clear_nonmtt_ctrs()
        cls.mttctrstrategy.clear_mtt_ctrs()
        cls.nonmttctrstrategy.set_edc_pass_port_ctr_range(edcportctrbinrange)
        cls.nonmttctrstrategy.load_autoctrinfo_from_mtpl()
        cls.nonmttctrstrategy.load_autoctrfile()
        cls.mttctrstrategy.init()

        cls.basenumber.clear_base_numbers()
        cls.basenumber.init(basenumrange)
        cls.basenumber.load_autobasenumfile()

        # Do some checks
        confirm(isinstance(cls.param_order, list),
                'param_order=%r. Expecting list' % cls.param_order, 'Pls fix Initialize()')

    @classmethod
    def set_binrange(cls, binrange):
        """if we have additional bin ranges, combine into one list then pass to nonmttbinstrategy"""
        binrange_list = []
        if cls.default_class.additional_binranges:
            binrange_list.extend(cls.default_class.additional_binranges)
        if isinstance(binrange, tuple):
            binrange_list.append(binrange)
        else:
            binrange_list.extend(binrange)
        cls.nonmttbinstrategy.set_bin_range(binrange_list)

    @classmethod
    def set_ctrrange_for_bins(cls, ctrrangeforbins):
        """Set counter ranges for 8-digit bin generation.

        Configures the counter ranges used when generating 8-digit bins in HBSBXXXX format.
        This allows users to constrain the XXXX counter portion to specific numeric ranges
        instead of using the default unlimited counter.

        :param ctrrangeforbins: Single tuple (start, end) or list of tuples defining counter ranges

        If the default_class defines additional_binranges, those are combined with the
        user-specified ranges before passing to the binning strategy.

        Example:
            ctrrangeforbins=(0, 2000) → Counters will be allocated from 0-2000
            ctrrangeforbins=[(0,1000), (2000,3000)] → Multiple ranges available
        """
        ctrrange_list = []
        if cls.default_class.additional_binranges:
            ctrrange_list.extend(cls.default_class.additional_binranges)
        if isinstance(ctrrangeforbins, tuple):
            ctrrange_list.append(ctrrangeforbins)
        else:
            ctrrange_list.extend(ctrrangeforbins)
        cls.nonmttbinstrategy.set_ctr_range_for_bins(ctrrange_list)

    @classmethod
    def set_outfile(cls, outfile):
        """Set the outfile"""
        cls.outfile = outfile
        cls.written = False

        # Create a new folder for the pymtpl input files
        input_folder = os.path.join(os.path.dirname(outfile), 'PymtplInputFiles')
        mkdirs(input_folder)

    @classmethod
    def set_thermal_reset_bins(cls, defaultthermalbin, defaultresetbin):
        """Set the default thermal and reset bins"""
        cls.default_class.validate_default_thermal_reset_bins(defaultthermalbin, defaultresetbin)
        cls.defaultthermalbin = cls.default_class.defaultthermalbin
        cls.defaultresetbin = cls.default_class.defaultresetbin

    @classmethod
    def set_default_clamp_software_bins(cls, defaultrm1bin, defaultrm2bin):
        """Set the default thermal and reset bins"""
        cls.defaultrm1bin = cls.default_class.validate_defaultrmbin(defaultrm1bin, 'defaultrm1bin')
        cls.defaultrm2bin = cls.default_class.validate_defaultrmbin(defaultrm2bin, 'defaultrm2bin')

    @classmethod
    def set_tosversion(cls, tosversion):
        """Set the TOS Version switch in the initialization call"""
        confirm(tosversion in ('tos3', 'tos4'),
                f'Tos version given {tosversion} which is unknown',
                'Valid choices are tos3 or tos4')
        cls.tosversion = tosversion
        cls.tos_softbinstr = 'SoftBins.'
        if tosversion == 'tos4':
            cls.tos_softbinstr = ''

    @classmethod
    def get_outfile(cls):
        """Get the outfile"""
        confirm(cls.outfile,
                'Initialize() is not called. No outfile defined',
                'Pls call Initialize() at the top of the source code.')
        return cls.outfile

    @classmethod
    def get_modulename(cls):
        """Get the outfile"""
        confirm(cls.module_name,
                'Initialize() is not called correctly. No module name defined',
                'Pls call Initialize() at the top of the source code and ensure there is a module name.')
        return cls.module_name

    @classmethod
    def is_initialized(cls, id_lno):
        if not cls.outfile:
            raise ErrorUser(f"No Initialize statement found before line #{id_lno}",
                            "Ensure the Initialize statement is defined before defining MConfig or Fitems")

    @classmethod
    def clear_all(cls):
        """Used for unittest to set the state of all the class vars to None"""
        for item in dir(cls):
            if item.startswith('_'):                 # ignore builtins
                continue
            if callable(getattr(cls, item)):         # ignore methods/functions
                continue
            setattr(cls, item, None)

        cls.param_order = cls._param_order_default
        cls.missing_setbin_warning_count = 0

    @classmethod
    def get_tpobj(cls):
        """Returns tpobj"""
        if cls.tpobj:
            return cls.tpobj

        if OPT.env:
            # If user specified env file in the input variable, use that
            envfile = OPT.env
            cls.tpobj = TestProgram(envfile)
            return cls.tpobj

        elif cls.bom:
            tpdir = os.path.realpath(cls.get_outfile())
            for _ in range(3):
                tpdir = os.path.dirname(tpdir)
                envs = glob.glob(f'POR_TP/{cls.bom}/*.env')
                confirm(len(envs) <= 1,
                        f'Expecting 1 .env file only: Found multiple: {envs}',
                        f'Pls fix bom={cls.bom} so it only matches one.')
                if len(envs) == 1:
                    cls.tpobj = TestProgram(envs[0])
                    return cls.tpobj

        else:
            # If user specifies no Env file, extract TP Dir from path of the output file.
            # Assumption is that MOs are running this from their module dirs and the outfile is also in their moduledir.
            # Mtpls are usually 3 folders deep in the TP dir structure.
            tpdir = os.path.realpath(cls.get_outfile())
            for _ in range(3):
                tpdir = os.path.dirname(tpdir)
                try:
                    envfile = Env.get_envfile(tpdir, firstonly=True)
                    cls.tpobj = TestProgram(envfile)
                    return cls.tpobj
                except ErrorUser:
                    pass

        # If no env file found, raise an error.
        raise ErrorUser(f"Found 0 env file(s): {os.getcwd()}",
                        f"Pls check the folder or run pymtpl with the path to a env file specified")


# Create a "default" Initialize for MTL using python's partial
InitializeMTL = partial(Initialize, defaults=MTLdefault, deprecation_warning=True)
InitializeNVL = partial(Initialize, defaults=NVLdefault, tosversion="tos4", deprecation_warning=True)

required = NoneLikeClass()       # None like class used in por_method params to indicate required
optional = NoneLikeClass()       # None like class used in por_method params to indicate optional

# Special value for AUTO bin that does not need source code replace
AUTO = -1
from pymtpl.binctr import BaseMtplInfo, BinSSB, MTTBinSSB, CtrHBSB, BaseNumber, MTTCtrHBSB, CtrServerClass8dig, CtrDMRClass8dig
from pymtpl.binctr import NVLClass8dig, MTTNVLClass8dig, CtrNVLClass8dig, MTTCtrNVLClass8dig, ServerClass8dig, TestChipNonMTTBin
from pymtpl.binctr import Sort8dig, CtrSort8dig
from pymtpl.binctr import NVLClassHBSBXXXX, JGSClass, CtrJGS8dig, CtrTestChip

# Base initializer for original NVLClass (8-digit binning)
_InitializeNVLClass = partial(Initialize, defaults=NVLdefault, nonmttbinstrategy=NVLClass8dig, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrNVLClass8dig, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos4")

# Base initializer for HBSBXXXX binning
_InitializeNVLClassHBSBXXXX = partial(Initialize, defaults=NVLClassdefaultHBSBXXXX, nonmttbinstrategy=NVLClassHBSBXXXX, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrSort8dig, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos4", usebinctrfrommtpl=True)


def InitializeNVLClass(*args, **kwargs):
    """
    Smart wrapper for NVL Class initialization that checks for OPT switch to determine binning strategy.

    If OPT switch 'class90hbsbxx' is present, uses the current 8-digit binning strategy (NVLClass8dig).
    If OPT switch 'class90hbsbxx' is NOT present, defaults to HBSBXXXX binning strategy.
    In unit tests (IS_UT=True), defaults to 8-digit binning for backward compatibility.

    :param args: Positional arguments to pass through to Initialize()
    :param kwargs: Keyword arguments to pass through to Initialize()
    :return: Initialize object
    """

    if OPT.class90hbsbxx or IS_UT:
        # Use the current 8-digit binning strategy (OPT switch takes priority)
        return _InitializeNVLClass(*args, **kwargs)
    else:
        # In production without OPT switch, default to HBSBXXXX binning strategy
        return _InitializeNVLClassHBSBXXXX(*args, **kwargs)


# Temporary code below -
# TODO: Remove the function below and replace all InitializeNVLClassHBSBXXXX in unit tests to use _InitializeNVLClassHBSBXXXX

def InitializeNVLClassHBSBXXXX(*args, **kwargs):
    """
    Direct initializer for NVL Class with HBSBXXXX binning strategy.
    This is primarily for unit test use only.

    :param args: Positional arguments to pass through to Initialize()
    :param kwargs: Keyword arguments to pass through to Initialize()
    :return: Initialize object
    """
    if IS_UT:
        # For unit test use only - HBSBXXXX binning
        # Revert to using _InitializeNVLClassHBSBXXXX in all unit tests
        # Splitting changes to make sure we get incremental changes merged in.
        return _InitializeNVLClassHBSBXXXX(*args, **kwargs)
    else:
        raise ErrorUser("InitializeNVLClassHBSBXXXX is intended for sandbox test use only.",
                        "Pls import InitializeNVLClass and use that for production code.")


# BI Specific
InitializeHDBI = partial(Initialize, defaults=HDBIDefault, nonmttbinstrategy=NVLClass8dig, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrNVLClass8dig, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos3")

InitializeNVLSort = partial(Initialize, defaults=Sortdefault, nonmttbinstrategy=Sort8dig, nonmttctrstrategy=CtrSort8dig, tosversion="tos4")

InitializeDMRClass = partial(Initialize, defaults=DMRdefault, nonmttbinstrategy=ServerClass8dig, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrDMRClass8dig, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos4", usebinctrfrommtpl=True)
InitializeJGSClass = partial(Initialize, defaults=JGSdefault, nonmttbinstrategy=JGSClass, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrJGS8dig, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos4", usebinctrfrommtpl=True)
InitializeCBRClass = partial(Initialize, defaults=CBRdefault, nonmttbinstrategy=ServerClass8dig, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrServerClass8dig, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos4", usebinctrfrommtpl=True)
InitializeCWFClass = partial(Initialize, defaults=CWFdefault, nonmttbinstrategy=ServerClass8dig, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrDMRClass8dig, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos3", usebinctrfrommtpl=True)

# Test Chips
InitializeTestChip = partial(Initialize, defaults=TestChipdefault, nonmttbinstrategy=TestChipNonMTTBin, mttbinstrategy=MTTNVLClass8dig, nonmttctrstrategy=CtrTestChip, mttctrstrategy=MTTCtrNVLClass8dig, tosversion="tos4", usebinctrfrommtpl=True, edcportctrbinrange=[(9900, 9999)])
