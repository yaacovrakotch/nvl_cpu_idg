#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Module Skip routine
"""
from gadget.files import File, basename_delext, check_and_del
from gadget.disk import mkdirs
from gadget.tputil import OtplFile, JsonRead
from gadget.errors import ErrorInput, confirm, ErrorUser
from gadget.dictmore import reverse_set
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.strmore import indent
from os.path import exists, basename, dirname
from tp.testprogram import TestProgram, Env
from pathlib import Path
import glob
import json
import re
import os


class ModuleSkip:
    """Updates ProgramFlowsTestPlan/* and *.stpl to skip modules"""

    is_module_skipped = False      # This is set to True if TP is modified

    def __init__(self, tpobj: TestProgram, modlist=None, onlylist=None, skipfile=False, destdir=None):
        """

        :param tpobj: TestProgram object
        :param modlist: list of testplan_module_name to skip
        :param onlylist: list of testplan_module_name to keep
        :param skipfile: If True: use POR_TP/*/SkipModules/{foldername}.txt to indicate skip. Use for sidebranches.
        """
        self.tpobj = tpobj
        self.modlist = modlist
        self.onlylist = onlylist
        self.plist_remove = set()
        self.cimod2map = self.set_cimod2mod_map()    # This must be assigned early
        self.destdir = destdir
        if skipfile:
            self.modlist = self.proc_skipfile()

    def get_modfolder2mod(self):
        """
        backwards compatibility routine
        Simple1 is not a torch tp and lots of unittest rely on the code
        Thus, manage it here
        """
        if self.tpobj.is_tpie:
            # tpie: 1:1
            return {x: x for x in self.tpobj.mtpl.get_modules()}
        else:
            # Torch
            return self.tpobj.mtpl.get_modfolder2mod()

    def set_cimod2mod_map(self):
        """
        backwards compatibility routine
        Simple1 is not a torch tp and lots of unittest rely on the code
        Thus, manage it here
        """
        if self.tpobj.is_tpie:
            # tpie: fake - unittest only
            return {x: {x} for x in self.tpobj.mtpl.get_modules()}
        else:
            # Torch
            return self.tpobj.plists.get_cimod2mod_map()   # {ci_plist_module: set_of_module}

    def proc_skipfile(self):
        """Return modules with skipfile"""
        if basename(dirname(self.tpobj.envdir)) == 'ENG_TP':
            return []    # Do not run moduleskip on ENG_TP for SkipModules. This is only for POR_TP.

        m2m = self.get_modfolder2mod()
        modskip = set()
        default_path = Path(self.tpobj.envdir)
        dynamic_path = Path(*default_path.parts[-2:])    # Save the BOM group folder path
        common_path = default_path / '../../Shared/' / dynamic_path
        for modfolder in m2m:

            if (exists(f'{self.tpobj.envdir}/SkipModules/{modfolder}.txt') or
                    exists(f'{self.tpobj.envdir}/SkipModules/{modfolder}.permanent') or
                    exists(f'{common_path}/SkipModules/{modfolder}.txt') or
                    exists(f'{common_path}/SkipModules/{modfolder}.permanent')):

                modskip.add(m2m[modfolder])

        return list(modskip)

    def set_plist_remove(self, modskip):
        """
        Return the set of plist to be removed
        :param modskip: set or list of modules to skip
        :return: set of plist names to remove
        """
        # Step1: Create map of module to plist
        mod_plist = self.tpobj.plists.get_mod2plist_map()    # {module: set_of_plist_file}

        # Step2: Create map of plist to module
        plist_mod = reverse_set(mod_plist)                  # {plist: set_modules}

        # Step3: Set of plist names to be removed
        set_modskip = set(modskip)
        remove_set = set()
        for plist, set_modules in plist_mod.items():
            if not (set_modules - set_modskip):
                remove_set.add(plist)

        return remove_set

    def update_plist(self, modskip):
        """Update the plist all"""
        remove_set = {x.lower() for x in self.set_plist_remove(modskip)}
        robj = re.compile('name="([^\"]+)')
        for ff in self.tpobj.plists.get_all_plists():
            # update this plist
            final = []
            for line in File(ff).raw():
                res = robj.search(line)
                if res:
                    if res.group(1).lower() in remove_set:
                        continue
                final.append(line)

            # check if empty
            final = self.empty_plist(final, ff)

            File(self.dest(ff)).rewrite(''.join(final), 'ModuleSkip().update_plist()')

    def empty_plist(self, final, plistfname):
        """Do not allow Empty plist since TOS does not like"""
        text = ''.join(final)
        if 'PListFile name=' in text:
            return final    # ok, no change needed

        fname = f'EmptyPlist_{basename_delext(plistfname)}.plist'
        result = []
        for line in final:
            result.append(line)
            if '<PList>' in line:
                result.append(f'     <PListFile name="{fname}" />\n')

        # Write the empty plist file if not exist
        spath = [f'{self.tpobj.tpldir}/Shared/*/Supersedes/patterns/',
                 f'{self.tpobj.tpldir}/Shared/BaseInputs/Common/*/Supersedes/patterns/']
        spaths = glob.glob(spath[0]) + glob.glob(spath[1])
        confirm(spaths, f'Expecting Supersede folder to exist: {spath}', 'Pls create this folder')

        # Use only first one
        if self.tpobj.is_tos4:
            File(f'{spaths[0]}/{fname}').rewrite('Version 6.0;\n', 'ModuleSkip().empty_plist()')
        else:
            File(f'{spaths[0]}/{fname}').rewrite('Version 5.0;\n', 'ModuleSkip().empty_plist()')

        return result

    def read_json(self):
        """Read the json file"""
        # User specified module list
        if self.modlist:
            result = {}
            # for tpobj in ProgramFamily(self.tpobj.tpldir).init_all_env():
            result[self.tpobj.get_bom()] = self.modlist
            return result

        # Read the config json file
        jsonfile = f'{self.tpobj.envdir}/skip_modules.json'
        if exists(jsonfile):
            with open(jsonfile) as fh:
                data = json.load(fh)
        else:
            data = {}

        # user specified keep list
        if self.onlylist:
            result = {}
            all_mods = set(self.tpobj.mtpl.get_modules())
            skip_mods = all_mods - (set(data.get('BASE_MODULES', [])) | set(self.onlylist))
            result[self.tpobj.get_bom()] = list(sorted(skip_mods))
            return result

        # return json_data
        return {bom: data[bom] for bom in data if bom != 'BASE_MODULES'}

    def read_mtpl(self, fname, all_lines, modset, in_struct=None, subflows=None, removed=None):
        """
        Read mtpl file, remove dutflowitem/flowitem that use this module

        first pass:  modset has value, in_struct is None:   Remove module blocks (Goto not updated yet).
        second pass: modset is empty,  in_struct has value: Update Goto lines.
        third pass:  modset is empty,  in_struct is None:   Remove dutflowitems for subflows.

        :param fname: fname
        :param all_lines: list of lines
        :param modset: set of module names
        :param in_struct: Input structure for replace
        :param subflows: set of subflows to check
        :param removed: set of removed items for .flw
        :return: lines (list), dict {<key>: <dest_return_1}
        """
        name = None
        result = None
        skip = False
        df = None

        lines = []
        struct = {}      # {dfi-name: mtpl-line-of-port-1}

        for lno, line in enumerate(all_lines):
            linestrip = line.strip()

            if linestrip.startswith('}'):
                if result is not None:
                    result = None
                elif name:
                    name = None
                    if skip:
                        skip = False   # Clear it
                        continue       # Do not write "}"

            if linestrip.startswith(('DUTFlow ', 'Flow ')):
                df = linestrip.split()[1]

            if linestrip.startswith(('DUTFlowItem ', 'FlowItem ', 'LoopFlowItem ')):
                assert name is None, f"name {name} is already defined in line#{lno} at {fname}"
                name, loc = linestrip.split()[1:3]

                # module
                tokens = loc.split('::')
                module = '' if len(tokens) == 1 else tokens[-2]
                skip = bool(module in modset)

                # subflow
                if subflows and loc in subflows:
                    skip = True

                if skip:
                    removed.add(f'{df}.{name}')
                    struct[name] = None

            if linestrip.startswith('Result '):
                assert name, f"name is not defined in line#{lno} at {fname}"
                assert result is None, f"Result [{result}] is already defined in line#{lno} at {fname}"
                result = int(linestrip.split()[1])

            if linestrip.startswith(('GoTo', 'Return')) and skip and result == 1:
                struct[name] = line

            if in_struct and linestrip.startswith('GoTo'):      # replace mode
                lines.append(self.find_new_port(line, in_struct))
                continue

            if not skip:
                lines.append(line)

        # Do the check - make sure GoTo or Return is defined in pass port
        for name in struct:
            confirm(struct[name],
                    f'Error in {name}: GoTo or Return is not defined on pass port',
                    f'Pls fix {basename(fname)}')

        return lines, struct

    def read_empty_subflows(self, all_lines):
        """
        remove empty subflows

        :param all_lines: list of lines
        :return: lines (list), set of subflows
        """
        lines = []
        subflows = set()
        skip = False
        for lno, line in enumerate(all_lines):
            linestrip = line.strip()

            if linestrip.startswith((('DUTFlow ', 'Flow '))):
                # assumed check_brackets() is run. That is brackets are in it's own line.
                if all_lines[lno + 1].strip().startswith('{') and all_lines[lno + 2].strip().startswith('}'):
                    subflows.add(linestrip.split()[1])
                    skip = True

                elif all_lines[lno + 1].strip().startswith('{') and all_lines[lno + 3].strip().startswith('}'):
                    subflows.add(linestrip.split()[1])
                    skip = True

            if linestrip.startswith('}') and skip:
                skip = False
                continue

            if not skip:
                lines.append(line)

        return lines, subflows

    def find_new_port(self, line, in_struct):
        """Return the new redirect, given GoTo line, recursively"""
        linestrip = line.strip()
        if not linestrip.startswith('GoTo'):
            return line
        target = linestrip.split()[1].replace(';', '')
        if target in in_struct:
            return self.find_new_port(in_struct[target], in_struct)    # recursive!
        else:
            return line    # No change

    def check_brackets(self, fname, all_lines):
        """
        Make sure that brackets are in next line. Error if not.
        Logic in read_empty-subflows() assume brackets are on independent lines
        """
        o_cnt = c_cnt = 0
        for _, line in OtplFile(fname).readline():
            if line.startswith('{'):
                o_cnt += 1
            if line.startswith('}'):
                c_cnt += 1

        o_expect = c_expect = 0
        for line in all_lines:
            line = line.strip()
            if line.startswith('{'):
                o_expect += 1
            if line.startswith('}'):
                c_expect += 1

        assert o_cnt == o_expect, f'Error: {fname} has non-standard open brackets. {o_cnt} vs {o_expect} count'
        assert c_cnt == c_expect, f'Error: {fname} has non-standard close brackets. {c_cnt} vs {c_expect} count'

    def mtpl_update(self, mtpl_fname, modset, bom):
        """Update one mtpl file (ProgramFlows.mtpl, IP_CONCURRENT.mtpl, etc)"""

        # read the mtpl file
        all_lines = [x for x in File(mtpl_fname).read().split('\n') if x.strip()]

        self.check_brackets(mtpl_fname, all_lines)
        removed = set()

        # pass1: remove DutFlowItem/FlowItem, then store the key->dest in struct
        lines, struct = self.read_mtpl(mtpl_fname, all_lines, modset=modset, removed=removed)

        # pass2: Update the connections
        lines, _ = self.read_mtpl(mtpl_fname, lines, modset=set(), in_struct=struct)

        # pass3: find and remove empty subflows
        lines, subflows = self.read_empty_subflows(lines)

        # pass4: remove dutflowitems
        lines, struct = self.read_mtpl(mtpl_fname, lines, modset=set(), subflows=subflows, removed=removed)

        # pass5: update connections
        lines, _ = self.read_mtpl(mtpl_fname, lines, modset=set(), in_struct=struct)

        # write it
        if bom in mtpl_fname:
            newname = mtpl_fname    # no change in filename
        else:
            newname = mtpl_fname.replace('.mtpl', f'_{bom}.mtpl')

        if all_lines == lines:
            File(mtpl_fname).copy(self.dest(newname))
            log.info(f"{self.dest(newname)} is created - exact copy.")
        else:
            File(self.dest(newname)).rewrite('\n'.join(lines), 'ModuleSkip().mtpl_update()')
            log.info(f"{self.dest(newname)} is generated.")

        self.update_flw(mtpl_fname, newname, removed)
        return newname

    def update_flw(self, fname, newname, removed):
        """
        Updates the flw file

        :param fname: original mtpl
        :param newname: new name mtpl
        :param removed: set of removed
        :return: None
        """
        flw_file = fname.replace('.mtpl', '.flw')
        if not exists(flw_file):
            return

        lines = []
        robj = re.compile('name="Flows::([^"]+)')
        actual = set()
        for line in File(flw_file).chomp():
            res = robj.search(line)
            if res:
                if res.group(1) in removed:
                    actual.add(res.group(1))
                    continue
            lines.append(line)

        msg = f'Warning: {flw_file} update: expect={len(removed)}, removed={len(actual)}. diff={removed-actual}'
        if len(actual) != len(removed):
            log.info(msg)

        lines.append('')   # last line crlf
        new_flw = newname.replace('.mtpl', '.flw')
        File(self.dest(new_flw)).rewrite('\n'.join(lines), 'ModuleSkip().update_flw()')
        log.info(f'{self.dest(new_flw)} is generated.')

    def proc_subbdef(self, modset, flist):
        """
        Given flist, update it by removing modset
        :param modset: modules to remove
        :param flist: list of names
        :return:
        """
        rmod = re.compile(r'/Modules/(\w+)/')
        rmod2 = re.compile(r'/Modules/\w+/(\w+)/')
        m2m = self.get_modfolder2mod()
        for ff in flist:
            if not exists(ff):
                continue    # not exist

            lines = []
            for line in File(ff).raw():
                # module to skip
                res = rmod.search(line)
                if res and m2m.get(res.group(1), res.group(1)) in modset:
                    continue     # skip this module

                # module to skip - submodule
                res = rmod2.search(line)
                if res and m2m.get(res.group(1), res.group(1)) in modset:
                    continue      # skip this module - submodule

                lines.append(line)

            File(ff).rewrite(''.join(lines), 'proc_subbdef()')

    def proc_stpl(self, stpl, pf_file, mod_file_dd, modset):
        """Read stpl file and return updated lines"""
        lines = []
        rmod = re.compile(r'/Modules/(\w+)/'.replace('/', '[/\\\\]'))
        rmod2 = re.compile(r'/Modules/\w+/(\w+)/'.replace('/', '[/\\\\]'))
        rfinal = re.compile(r'^(\s*Final[\s\"]+./ProgramFlowsTestPlan/)ProgramFlows[\w\-\.]+([;"]+)'.replace('/', '[/\\\\]'))
        mmod = re.compile(r'/Modules/\w+/([\w\-\.]+)([";]+)'.replace('/', '[/\\\\]'))
        mmod2 = re.compile(r'^\s*Final[\s\"]+./ProgramFlowsTestPlan/([\w\-\.]+)[";]'.replace('/', '[/\\\\]'))
        finaltag = False
        m2m = self.get_modfolder2mod()

        for line in File(stpl).chomp():
            # module to skip
            res = rmod.search(line)
            if res and m2m.get(res.group(1), res.group(1)) in modset:
                continue      # skip this module!

            # module to skip - submodule
            res = rmod2.search(line)
            if res and m2m.get(res.group(1), res.group(1)) in modset:
                continue      # skip this module - submodule

            # name to replace - tpie
            res = mmod.search(line)
            if res and res.group(1) in mod_file_dd:
                line = line.replace(res.group(1), mod_file_dd[res.group(1)])

            # name to replace - torch
            res = mmod2.search(line)
            if res and res.group(1) in mod_file_dd:
                line = line.replace(res.group(1), mod_file_dd[res.group(1)])

            # final
            res = rfinal.search(line)
            if res:
                lines.append(f'{res.group(1)}{basename(pf_file)}{res.group(2)}')
                finaltag = True
                continue

            lines.append(line)
        assert finaltag, rf"[Final .\ProgramFlowsTestPlan\] is not found in {stpl}"
        return lines

    def proc_env2(self, envfile, modset):
        """
        Remove variable names which has the module folder name
        2nd pass env rewrite

        :param envfile: env file to rewrite
        :param modset: set of testplans name to remove
        :return:
        """
        # get the set of module folder first
        m2m = self.get_modfolder2mod()    # {module_folder: module}
        m2mr = reverse_set(m2m)           # {module: set_of_module_folder}
        modfset = set()                   # set of module folders to skip
        for item in modset:
            modfset.update(m2mr.get(item, {item}))    # sometime module is not in TP since it is module is specified in json file

        robj1 = re.compile('^(%s)_' % '|'.join(modfset))
        robj2 = re.compile('_(%s)_' % '|'.join(modfset))
        envobj = Env(envfile)
        found = False
        for var in list(envobj.get_env_dict()):
            if robj1.search(var) or robj2.search(var):
                found = True
                envobj.del_item(var)

        if found:
            File(envobj.envfile).rewrite(''.join(envobj.rebuild()), f'proc_env2()')

    def proc_env(self, envfile, modset, ut=False):
        """
        Read envfile and strip off lines that match any of the modset
        Assumes one module per line

        :param envfile: input env file
        :param modset: set of testplan names to remove
        :param ut: Set to True for UT
        :return: list of env lines
        """
        # get the set of module folder first
        m2m = self.get_modfolder2mod()    # {module_folder: module}
        m2mr = reverse_set(m2m)           # {module: set_of_module_folder}
        modfset = set()                   # set of module folders to skip
        for item in modset:
            modfset.update(m2mr.get(item, {item}))    # sometime module is not in TP since it is module is specified in json file

        # determine the PATMOD skips
        m2c = reverse_set(self.cimod2map)   # {"ARR" : {"MFus"}}
        allci = set()          # all ci_modules
        keeppatmod = set()     # set of ci_module to keep
        for item in m2c:
            allci.update(m2c[item])
            if item not in modfset:    # keep
                for ci in m2c[item]:
                    keeppatmod.add(ci)

        setpatmod = {'_INITIAL_'}    # Set of patmod to be removed. __INITIAL_ is there so it's guaranteed to be not empty.
        for ci in (allci - keeppatmod):
            setpatmod.add(f'{ci.upper()}_PATMODIFY_PATH')

        # for item in m2c:
        #     if item in modfset:
        #         for skipci in m2c[item]:
        #             setpatmod.add(f'{skipci.upper()}_PATMODIFY_PATH')
        if ut:
            return setpatmod

        # process the env file
        robj = re.compile(r'"[^"]*Modules[^\w](%s)[^\w][^"]+"' % '|'.join(modfset))
        robj1 = re.compile(r'"[^"]*Modules[^\w][\w-]+[^\w](%s)[^\w][^"]+"' % '|'.join(modfset))
        robj2 = re.compile(r'"\$(%s)(_HDST_PLIST_PATH|_HDST_PAT_PATH|_ALEPH_FILES|__PATMODIFY_PATH);?"' % '|'.join(modfset))
        robj3 = re.compile(r'\$include.*/(%s)/' % '|'.join(modfset))
        rpm = re.compile(r'"\$(%s)[^"]*"' % '|'.join(setpatmod))
        rtop = re.compile(r'^(\s*\w+\s*=\s*)""\s*\+\s*$')
        result = []
        varname = ""
        qq = '""'   # two double quotes
        with open(envfile) as fh:
            for line in fh:
                if varname:
                    line = f'{varname}{line.lstrip()}'
                    varname = ''

                line = robj.sub(qq, line)     # replace with empty string if found
                line = robj1.sub(qq, line)    # replace with empty string if found - shared module repo
                line = robj2.sub(qq, line)    # replace with empty string if found - modular env variables
                line = rpm.sub(qq, line)      # replace with empty string if found - PATMODIFY_PATH

                res3 = robj3.search(line)
                if res3:
                    continue   # skip the $include line

                # empty middle line
                if line.strip().replace(' ', '') == f'{qq}+':
                    continue   # skip

                # empty last line
                if line.strip() == f'{qq};':
                    prev = result[-1]    # last line
                    result[-1] = f'{prev.rstrip()[:-1]};'
                    continue    # skip this line

                # empty top line
                res = rtop.search(line)
                if res:
                    assert not varname, "Cockpit logic error! Contact jqdelosr, this should not happen"
                    varname = res.group(1)
                    continue

                result.append(line)

        # remove the extra ;
        for idx in range(len(result)):
            if result[idx].endswith('" ;'):
                result[idx] = result[idx].replace('" ;', '";')
            if result[idx].endswith(';";'):
                result[idx] = result[idx].replace(';";', '";')

        # replace empty ALEPH with just semicolon
        r_aleph = re.compile(r'^\s*\w*ALEPH\w*\s*=\s*"";')
        for idx in range(len(result)):
            if r_aleph.search(result[idx]):
                result[idx] = result[idx].replace(qq, '";"')

        return result

    def get_env_name(self, bom):
        """Return the tp stpl name given bom"""
        res = glob.glob(f'{self.tpobj.envdir}/EnvironmentFile_{bom}*.env')
        if len(res) == 1:
            return res[0]
        elif len(res) == 0:
            if exists(f'{self.tpobj.envdir}/EnvironmentFile.env'):
                return f'{self.tpobj.envdir}/EnvironmentFile.env'
            raise ErrorInput(f'No file found that match: {self.tpobj.envdir}/EnvironmentFile_{bom}*.env',
                             'Pls check above path.')
        else:
            raise ErrorInput('Multiple env file found for the same bom:\n%s' % '\n'.join(res),
                             'Expecting one env file only per Bom')

    def get_stpl_name(self, bom):
        """Return the tp stpl name given bom"""
        tentative = f'{self.tpobj.tpldir}/SubTestPlan_{bom}.stpl'
        if exists(tentative):
            return tentative
        return self.tpobj.get_stpl()    # current stpl file - for Torch

    def process_one_bom(self, bom, modset, programflows):
        """
        Process one bom of the testprogram.
        Calls mtpl_update() and updates the stpl file.

        :param bom: bom name
        :param modset: set of modules
        :param programflows: ProgramFlows.mtpl
        :return: None (for unittest only)
        """
        if not modset:
            return None

        # Get all module names (folders)
        fullset = sorted(self.tpobj.get_module_folder_names())

        # Update plist first
        self.update_plist(modset)

        # ProgramFlows.mtpl
        newname_p = self.mtpl_update(programflows, modset, bom)

        # Special module mtpl to process
        newname_m = {}
        for mtpl in [f'{self.tpobj.moddir}/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS.mtpl',
                     f'{self.tpobj.moddir}/IP_PCH_CONCURRENT_FLOWS/IP_PCH_CONCURRENT_FLOWS.mtpl',
                     f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IPC_FLOWS.mtpl',
                     f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IPG_FLOWS.mtpl',
                     f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IPH_FLOWS.mtpl',
                     f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IPP_FLOWS.mtpl',
                     f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl',
                     f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IP_PCH_CONCURRENT_FLOWS.mtpl',
                     ]:
            if exists(mtpl):
                newname_m[basename(mtpl)] = basename(self.mtpl_update(mtpl, modset, bom))

        # Update the stpl
        stpl = self.get_stpl_name(bom)
        assert exists(stpl), f'{stpl} is expected to exist'
        lines = self.proc_stpl(stpl, newname_p, newname_m, modset)
        File(self.dest(stpl)).rewrite('\n'.join(lines), 'ModuleSkip().process_one_bom()', keep='old')
        log.info(f'{stpl} is updated.')
        ModuleSkip.is_module_skipped = True    # Used to indicate if Module skip was executed

        # update subbdef
        self.proc_subbdef(modset, [f'{self.tpobj.shareddir}/Package_Shared/Modules.imp'])

        # Update the env file
        env = self.get_env_name(bom)
        lines = self.proc_env(env, modset)
        File(self.dest(env)).rewrite(''.join(lines), 'ModuleSkip().process_one_bom()', keep='old')
        self.proc_env2(self.dest(env), modset)

        # Post update the env file for FUS module special request
        self.moduleskip_fus_nvl(self.dest(env), modset, fullset)

        return basename(stpl)

    def dest(self, path):
        """
        Return the final destination of path, given self.destdir
        :param path: Path to file
        :return: A newer path to file
        """
        if not self.destdir:
            return path    # as-is

        mkdirs(self.destdir)

        if 'ProgramFlowsTestPlan' in path:
            mkdirs(f'{self.destdir}/ProgramFlowsTestPlan')
            return f'{self.destdir}/ProgramFlowsTestPlan/{basename(path)}'

        # default
        return f'{self.destdir}/{basename(path)}'

    def delete_folder(self, isdelete):
        """
        Delete all module folders which are not part of modlist
        Reason: PDEs get confused and ask: "The TP is full TP" without looking at stpl file
        """
        if not isdelete:
            print('isdelete = false?')
            return     # Do nothing

        newtpobj = TestProgram(self.tpobj.envfile)
        used_mtpls = newtpobj.get_all_mtpl_from_stpl()       # {full_path_mtpl: boolean}

        # Get modules used by .stpl
        used_mod = {basename(dirname(x)) for x in used_mtpls if "Modules" in x}

        # Get modules in disk
        disk_listing = (glob.glob('Modules/*/*/*.mtpl') +
                        glob.glob('Modules/*/*.mtpl') +
                        glob.glob('Shared/Modules/*/*/*.mtpl') +
                        glob.glob('Shared/Modules/*/*.mtpl'))
        disk_mod = {dirname(x): basename(dirname(x)) for x in disk_listing}    # {module_path: mod_name}

        # delete modules in disk which are not used by stpl
        if 'TPSWITCH2' not in os.environ:
            for mod_path, mod_name in disk_mod.items():
                if mod_name not in used_mod:
                    log.info(f'-i- ModuleSkip() Deleting unused: {mod_path}')
                    check_and_del(mod_path)

    def main(self, isdelete=False):
        """
        Main Entry point - process all boms in json. This works well with tpie, and Torch is simpler one.

        Logic Flow:
        step1. process_one_bom()    # for each bom
        step2. mtpl_update()        # for each mtpl
        step3. delete_folder()      # Delete module folders which skipped
        """
        sw = Elapsed()
        processed_stpl = []       # for unittest
        programflows = self.tpobj.get_final_mtpl()
        jsondata = self.read_json()
        once = set()
        for bom in jsondata:
            stpl = self.get_stpl_name(bom)
            confirm(stpl not in once,
                    f'skip_modules.json has problem, {basename(stpl)} is already processed.',
                    f'Pls make sure json has only one bom inside bom={bom}')
            once.add(stpl)

            # Make sure stpl exist. Reason: They can put more stuff in json and it should be ok!
            confirm(exists(stpl), f'{stpl} does not exist. Where is it?', 'check stpl location')

            # get the correct programflows based on bom
            if basename(programflows) != 'ProgramFlows.mtpl':
                programflows = f'{dirname(programflows)}/ProgramFlows_{bom}.mtpl'
            assert exists(programflows), f"{programflows} does not exist. Where is it?"

            modset = set(jsondata[bom])
            result = self.process_one_bom(bom, modset, programflows)    # mtl_update() and stpl update is here.
            processed_stpl.append(result)

        # Call module folder delete
        self.delete_folder(isdelete)
        log.info(f'-i- ModuleSkip() complete in {sw}. processed stpl: {processed_stpl}')

        return processed_stpl     # for unittest

    @classmethod
    def skipjson_main(cls, env):
        """
        Entry point of script: given env file, will modify all boms and do checks
        """
        tp = TestProgram(env)
        cls(tp).main()    # modify it
        log.info("Checking....")
        tp1 = TestProgram(env)
        result = len(list(tp1.mtpl.iter_flows()))
        log.info(f"Success: total instances={result}.")

    def moduleskip_fus_nvl(self, envfile, skiplist, fulllist):
        """
        Special routine for NVL fus Aleph path update in ENV file.
        3 FUS modules per dielet -> FUS_FLE, FUS_FUSECFG, FUS_UNITINFO
        If all 3 are skipped, then remove FUSE_ROOT_DIR.
        If partial needs removal, then error out with message.
        Process per dielet.

        :param envfile: input env file
        :param skiplist: parse from json/skip module folder getting list modules to skip
        :param fulllist: full list modules from TP
        """

        # To seperate the FUS modules into dielets
        die_indicator = ['C', 'G', 'H', 'P']
        envobj = Env(envfile)

        for item in die_indicator:
            fuse_list = [f'FUS_FUSECFG_{item}', f'FUS_UNITINFO_{item}']

            appendix = item

            # Find if any of above FUS modules are in the skip list.
            found = False
            for keyword in fuse_list:
                for skipitem in skiplist:
                    if keyword in skipitem:
                        found = True
            if not found:
                continue  # Do nothing

            matched_keywords = {
                skipitem
                for keyword in fuse_list
                for skipitem in skiplist
                if keyword in skipitem
            }

            fus_fulllist = {
                fusitem
                for keyword in fuse_list
                for fusitem in fulllist
                if keyword in fusitem
            }

            # Check if all above FUS modules are skipped. If no, raise error.
            missing_keywords = fus_fulllist - matched_keywords
            if missing_keywords:
                raise ErrorUser(f"Can NOT skip only {', '.join(matched_keywords)} module",
                                f"Also need to skip {', '.join(missing_keywords)} module")

            # Remove the "FUSE_ROOT_DIR" lines from the env file.
            envars = envobj.get_env_dict()

            for item in envars:    # item is one var in env file
                if 'ALEPH' not in item:
                    continue    # skip non-aleph

                process_block = envobj.get_item(item, islist=True)

                final = []
                for line in process_block:
                    if f'FUSE_ROOT_DIR_{appendix}' in line:
                        continue           # skip FUSE_ROOT line
                    final.append(line)

                envobj.set_item(item, final)     # set the new data

            File(envobj.envfile).rewrite(''.join(envobj.rebuild()), f'moduleskip_fus_nvl')

        return envobj.rebuild()


class MvJson:

    def read_mv_json(self, tpobj, jsonname):
        """Read the mv json if exist and return a list"""
        # check first if MV_json is given
        if jsonname.startswith(('FULL', 'VALL', 'PARTIAL')):
            return None       # no json file provided

        result = glob.glob(f'TPConfig/MV_Templates/{jsonname}.json') + glob.glob(f'Shared/TPConfig/MV_Templates/{jsonname}.json')
        all_valid = sorted(glob.glob(f'TPConfig/MV_Templates/*.json') + glob.glob(f'Shared/TPConfig/MV_Templates/*.json'))
        confirm(len(result) > 0,
                f'Provided json [{jsonname}.json] does not exist',
                'Pls provide valid json file, Existing list:\n%s' % '\n'.join(all_valid))
        confirm(len(result) == 1,
                f'Provided json [{jsonname}.json] exist in dielet and common: {result}',
                f'json file must be unique across dielet and common. Pls fix repo')
        resultfile = result[0]     # one and only element

        modre = self.process_json(dirname(resultfile), basename(resultfile))
        onlylist = self.get_mv_modules(tpobj, modre)

        # Print out accepted module list.
        modlist_print = indent(3, [f'Accepted: {x}' for x in sorted(onlylist)])
        log.info('-i- List of accepted modules:\n%s' % modlist_print)

        return onlylist

    def get_mv_modules(self, tpobj, modre):
        """
        Return set of TestPlan module names to keep
        :param tpobj: tp object
        :param modre: sorted list of regex module (folder name)
        :return: set of modules (TestPlan) to keep
        """
        # get the modules
        fullpath_mtpl = tpobj.get_all_mtpl_from_stpl()   # {full_path_mtpl: boolean}
        mega = '(%s)' % '|'.join(modre)
        rmega = re.compile(mega)
        set_mod_folder = set()     # module folder name to keep
        for fp in fullpath_mtpl:
            mod = basename(dirname(fp))
            if rmega.search(mod):
                set_mod_folder.add(mod)

        # get the testplan module name, module_skip needs testplan module name
        mm = tpobj.mtpl.get_modfolder2mod()
        return {mm[x] for x in mm if x in set_mod_folder}

    def process_json(self, root, jsonname, jfiles=None):
        """
        Recursive - Return module regex list (folder name)

        :param root: directory where json files are
        :param jsonname: Name inside json to use
        :param jfiles: lower fname mapping
        :return: module (regex) list
        """
        # make sure dir is existing
        confirm(exists(root),
                f'{os.path.realpath(root)} does not exist. cwd: {os.getcwd()}',
                f'Expecting this directory to exist. Pls run torch_mv from source TP repo.')

        if not jfiles:
            jfiles = {x.lower(): x for x in os.listdir(root)}

        # get the fname
        fname = jsonname.lower()
        if not fname.endswith('.json'):
            fname = f'{fname}.json'

        confirm('/' not in fname.replace('\\', '/'),
                f'[{fname}] must be <file>.json and should not include path',
                f'Pls try again and remove the path.')

        confirm(fname in jfiles,
                f'{fname} (case-insensitive filename) does not exist in {root}',
                f'Check {root}')

        jdata = set()
        data = JsonRead(f'{root}/{jfiles[fname]}').load()
        for item in data:
            jdata.update(item['modules'])
            for ff in item['config_imports']:
                jdata.update(self.process_json(root, ff, jfiles))

        # read thru the json
        return sorted(jdata)
