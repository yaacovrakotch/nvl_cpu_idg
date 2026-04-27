#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
QGate - Quality Gate

Documentation: https://wiki.ith.intel.com/display/ITSpdxtp/QGate

Design:
1. Each individual qugate can be run as independent script.
2. Each individual qugate can easily be deployed to other products. They can mix and choose.
3. Module owners can code their own qugate and commit for their module..
4. qugate.py will call of these qugates and summarize them and hook in github pipeline.
5. Move product specific checker in TP repo and generic checker in a generic repo.

Spec:
1. Every qgate checker is an inherited class from QGate, with main() as the calling point
2. Errors are accumulated in self.result of the class, must use the same mechanism
3. Module owners can code their own qgate routine and put them in Modules/*/InputFiles/qgate_missing_ports.py
4. The list of checks is in the tp repo: POR_TP/Class_MTL_P68/InputFiles/qgate_config.json
   -> This file tells which check, and if they are error or warning
   -> format:   "Gate" or "Warning" or "Off"
   { "missing_ports.py":  {"211": "Gate",    "212": "Warning"},
     "min_lvl.py":        {"152": "Warning", "153": "Warning", "154": "Off"},
     "Modules/ARR_FUN/InputFiles/qgate_missing_ports.py":  {}
   }
4a. Error number not defined is considered "Gate".
4b. Empty is OK, all codes is "Gate"

5. The name, eg "MissingPorts" is the class names. This has to be unique across all.
   naming convention is no underscore, camelcase.
6. qgate_waivers.txt is still needed for temporary "waiving".
   This is exactly the same as sherlock.trigger.txt.
   Why? For new products implementing a new check.
        For new gates implemented in a product but some modules are failing.

Process of writing module qgate check:
1. Write your own, unittest is recommended
2. If this routine is applicable to more than one product, then we promote the routine to pytpd.
3. unittest is required on pytpd.

Process update:
1. MO will update qgate_waivers.txt in their own PR if needed without TPI approval (MO owns their quality)

Usage:
qgate.py <path_to_env>          # This will run all the checks, with pickle
qgate.py <path_to_env> -toc     # This will list all error numbers, name and location of .py file. This will just "grep" for self.add_error
qgate.py <path_to_env> -runner  # This will run all the checks, but no pickle
qgate.py -next                  # This will next unused id

Error Classification:
   Gate:    If True, then error out. Will error out on MV or TPBuild also.
   Warning: No error out, but print it out
   Off:     No error
   NewOnly: If True, and module is part of PR (modified_files), then error out.
            Do not error on MV or TPBuild.

NewOnly strategy:
   Purpose: Transitional errors, so we don't have to put in waiver trigger file.
         These are errors which we want to implement, but will only trigger when module owner makes PR.
         Example: Incorrect Module name in bin definition
                  softbin_ssb.py
                  missingports.py .cs and .py errors
   Flow: Start as NewOnly, then change this to Gate, once the TP is clean.

    1. When run qgate.py and PR, determine modified files.
        If qgate error is part of modified files, then error
        If not part of modified files, no error
    2. When run as indepedent checker, then error always (development mode)
    3. When run qgate.py, but no modified files: no error
       -> Qgate will not ERROR on MV or TPBuild

TODO:
0. Thus, error out if qgate_config is {}, or if a number is not registered!
   qgate to open the .py file and determine the error number codes and see if there are clashing numbers.
   If qgate_config is {}, then duplicate is not checked.
1. A process to figure out reminder of "waivers" and cleaning up of waivers to get to empty.
2. Update release note script to put the list of waivers (publish)
3. qgate to check that all numbers are unique (via grep of .py files)
4. pickle_init not working for qgate because of new file generated
"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.vepargs import Args, TA_All, TA_Store, TA_StoreTrue
from gadget.dictmore import DictDot, reverse_keyval
from gadget.pylog import log
from gadget.files import File, basename_n
from gadget.gizmo import Elapsed
from gadget.strmore import sha1
from gadget.printmore import PrintAlign
from gadget.tputil import CheckerLog
from gadget.errors import ErrorInput, confirm, ErrorUser, ErrorCockpit
from gadget.helperclass import OPT
from gadget.shell import CALLERBIN
from gadget.getgit import GitHub
from gadget.disk import Chdir
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from os.path import dirname, exists, basename, isdir
from collections import defaultdict
from importlib.machinery import SourceFileLoader
import json
import re
import os
import glob


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class QGateArgs(Args):

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.cfg = TA_Store('Specify cfg file')
        cfg.toc = TA_StoreTrue('List TOC - Table of Contents')
        cfg.next = TA_StoreTrue('Give the next available id')
        cfg.runner = TA_StoreTrue('runner mode - without pickle')
        cfg.light = TA_StoreTrue('Light initialize (used with -runner only)')
        cfg.verbose = TA_StoreTrue('Print pass and warnings in console. Used in independent yml.')
        cfg.allpats = TA_StoreTrue('Set allpats=True on TestProgram object')
        return cfg

    def main(self):
        """Main Entry point"""
        if OPT.next:
            self.do_next()
            return

        assert len(OPT.all) == 1, 'Usage Error!\n\nPls specify .env file as first args'
        if OPT.runner:
            tpobj = TestProgram(OPT.all[0], allpats=OPT.allpats).init(light=OPT.light)
        else:
            tpobj = TestProgram(OPT.all[0], allpats=OPT.allpats).pickle_init()

        with Chdir(tpobj.tpldir):
            QGateExecute(tpobj, cfg=OPT.cfg).main()

    def do_next(self, maxlimit=999):
        """Read all .py qgate and give the next available id starting 200"""
        allqgate = glob.glob(f'{ROOT_ENV}/qgates/*.py')
        robj1 = re.compile(r'self\.(add_error|add_pass)\((\d+)')
        robj2 = re.compile(r'self\.check\(.+?\, (\d+)')
        found = set()

        for fname in allqgate:
            text = File(fname).read()
            for code, idno in robj1.findall(text):
                found.add(int(idno))
            for idno in robj2.findall(text):
                found.add(int(idno))

        print()
        for idx in range(200, maxlimit):
            if idx not in found:
                print(f"Next available free: {idx}")
                return

        print(f"No available free id from 200 to {maxlimit}")


class QGateExecute:
    _modfiles = []         # list of modified files, assigned by buildtp.py
    repodir = os.environ.get('REPO_DIR', os.getcwd())

    def __init__(self, tpobj, cfg=None):
        self.tpobj = tpobj
        self.envfile = tpobj.envfile
        self.qcfg = None         # {'module': {id: Warning|Gate|Off}}
        self.oew = None          # {id: 0|1|2|3)   # 0 is off, 1 is error, 2 is warning, 3 is newonly
        self.qcls = []
        self.error = []          # list of errors: (module, id, message)
        self.warning = []        # list of warnings: (module, id, message)
        self.passed = defaultdict(int)      # (n, mod): count
        self.cls2id = {}         # {cls: id_no}
        self.fname2id = {}       # {fname: id_no}
        self.cfg = self._get_config(cfg)

    def _get_config(self, cfg):
        """Return the cfg to use"""

        # own config for dev work
        if cfg:
            return cfg

        # Return shared folder if exist - priority
        shared = f'{self.tpobj.shareddir}/POR_TP/{self.tpobj.get_bomfolder()}/InputFiles/qgate_config.json'
        if exists(shared):
            return shared

        return f'{dirname(self.envfile)}/InputFiles/qgate_config.json'     # default

    def main(self):
        """Main Entry"""
        sw = Elapsed()

        # For standalone call
        self.standalone_calls()

        # Read the config first
        confirm(not self._read_config(), f'Missing {self.cfg}', 'This is required')

        log.info(f"-i- QGate is starting.")
        log.info(f"-i- REPO_DIR: {QGateExecute.repodir}")
        log.info(f"-i- Modified File count: {len(self._modfiles)}")

        # Read all the qgate modules
        self._read_modules()

        # call all the routines
        self._all_routines()

        # process qgate_waivers.txt
        self._waivers()

        # print the output
        self._summary()
        log.info(f'-i- QGate total Elapsed: {sw}')

        # delete fulltp temp
        if QGateBase.fulltp_tempdir:
            QGateBase.fulltp_tempdir.close()
            QGateBase.fulltpobj = None            # so that it will be reinitialized
            QGateBase.fulltp_tempdir = None

        if self.error:
            log.info('')
            raise ErrorUser("There are Quality Errors! Gating Testprogram.",
                            "Pls fix these errors. Refer to summary and messages above for details.")

    def standalone_calls(self):
        """Call the routines called in buildtp.py for standalone qgate runs"""
        if self._modfiles:
            return    # Do nothing, it is already initialized

        with Chdir(QGateExecute.repodir):
            if isdir('.git'):    # it is a repo
                self.set_repo_dir()

                # call gh
                if 'https_proxy' not in os.environ:
                    log.info("Qgate(): https_proxy is not found in environment. Cannot call gh. Skipping mod files")
                    return

                try:
                    self.set_modfiles(GitHub.get_modfiles())
                except ErrorUser:
                    pass

    def _waivers(self):
        """
        Process waivers.
        Move self.error items into self.warning for lines that exist in qgate_waivers.txt
        """
        # Do nothing if there is no error
        if not self.error:
            return

        # Do nothing if waiver file is not found
        # Return shared folder if exist - priority
        waiverfile = f'{self.tpobj.shareddir}/POR_TP/{self.tpobj.get_bomfolder()}/InputFiles/qgate_waivers.txt'
        if not exists(waiverfile):
            waiverfile = f'{dirname(self.envfile)}/InputFiles/qgate_waivers.txt'     # default
        log.info(f'-i- Waiver file: {waiverfile}')
        if not exists(waiverfile):
            log.info(f'-i- Waiver file not found: {waiverfile}')
            return

        # Read all the waiver lines and put them in a set for easy search
        with open(waiverfile) as fh:
            allwaivers = {x.strip() for x in fh if x.strip()}

        # Update the error list
        finalerror = []
        for item in self.error:
            line = self.get_error_line(item)
            if line.strip() in allwaivers:
                self.warning.append(self._update_item(item, 'Waived'))
            else:
                finalerror.append(item)

        self.error = finalerror

    def _summary(self):
        """
        Print and write to file: Reports/QGate_report.txt'
        """
        outlines = []

        # passing stats first, only on output file
        outlines.append("PASSING:")
        id_total = defaultdict(int)
        for (id, _), cnt in self.passed.items():
            id_total[id] += cnt
        for id in sorted(id_total):
            outlines.append(f'Qgate#{id}: pass count={id_total[id]}')
        outlines.append('')

        if OPT.verbose:
            for line in outlines:
                log.info(line)

        # Generate the table
        table_warning = self._gen_table(self.warning, "WA")
        table_error = self._gen_table(self.error, "QG")
        log.info("WARNING:")
        log.info(table_warning)
        log.info("")
        log.info("ERRORS:")
        log.info(table_error)
        log.info("")

        outlines.append("WARNING:")
        outlines.append(table_warning)
        outlines.append("")
        outlines.append("ERROR:")
        outlines.append(table_error)

        # print warning - console
        if self.warning:
            log.info(f'There are total of {len(self.warning)} warnings. Refer to Reports/QGate_report.txt')
            log.info('')

        # print error
        outlines.append(f"Below are list of errors ({len(self.error)}):")
        log.info(outlines[-1])
        if self.error:
            for item in self.error:
                line = self.get_error_line(item)
                log.info(line)
                outlines.append(line)
        else:
            log.info("No Errors")
            outlines.append("No Errors")

        # print warning - file only
        if self.warning:
            warns = []
            warns.append('')
            warns.append(f'Below are list of warnings ({len(self.warning)}):')
            for mod, idn, msg in self.warning:
                line = f'{mod} -Warning{idn}- {msg}'
                warns.append(line)
            outlines.extend(warns)

            if OPT.verbose:
                for line in warns:
                    log.info(line)

        self._write_file(outlines)

    @classmethod
    def get_error_line(cls, item):
        """
        Return the standard error line. item is from self.error.
        This routine is also used in qgate_waivers.txt

        :param item: tuple (mod, idn, msg)
        :return: standard output line
        """
        mod, idn, msg = item
        return f'{mod} -QGate{idn}- {msg}'

    def _update_item(self, item, kind):
        """
        Add "(Waived)" in the msg of the item
        :param item: tuple (mod, idn, msg)
        :param kind: Message to write
        :return: tuple (mod, idn, msg)
        """
        mod, idn, msg = item
        msg = f'{msg} ({kind})'
        return mod, idn, msg

    def _write_file(self, outlines):
        """Write to the file"""
        outlines.append('')
        outfile = f'{dirname(self.envfile)}/Reports/QGate_report.txt'
        File(outfile).touch('\n'.join(outlines), mkdir=True, newfile=True)
        log.info('')
        log.info(f'-i- QGate Report File: {outfile}')

    def _gen_table(self, dd, prefix):
        """
        :param dd: list of (mod, id, msg)
        :param prefix: Two letter prefix
        :return: a long string of table
        """
        if not dd:
            return 'None'
        # get all id first
        allid = set()
        for mod, idn, msg in dd:
            allid.add(idn)
        head = sorted(allid)

        # summarize the counts
        cnt = {}
        for mod, idn, msg in dd:
            if mod not in cnt:
                cnt[mod] = defaultdict(int)
            cnt[mod][idn] += 1

        # Create the table
        pa = PrintAlign(sep='|', col_header=True)

        # create the header
        data = ['Module']
        for idn in head:
            data.append(f'{prefix}_{idn}')
        pa(*data)

        # create the data
        for mod in cnt:
            data = [mod]
            for idn in head:
                if idn in cnt[mod]:
                    data.append(cnt[mod][idn])
                else:
                    data.append("")
            pa(*data)

        return pa.string()

    def _all_routines(self):
        """Execute all routines"""

        for item in self.qcls:
            log.info(f"-i- Executing: {item.__name__}")
            sw = Elapsed()
            obj = item(self.tpobj)

            try:
                obj.main()
            except Exception as e:
                item_key = ('BASE', self.cls2id[item], str(e))
                self.error.append(item_key)
            except SystemExit as e:
                item_key = ('BASE', self.cls2id[item], f'SystemExit {e}')
                self.error.append(item_key)

            log.info(f"-i- Completed  {item.__name__} in {sw}")

            # collect the result
            for item in obj.result:
                item_key = (item["module"], item["id"], item["message"])
                if self.oew.get(item["id"], 1) == 1:
                    self.error.append(item_key)

                elif self.oew[item["id"]] == 2:
                    self.warning.append(item_key)

                elif self.oew[item["id"]] == 3:      # NewOnly

                    if self._is_modified(item["module"]):
                        self.error.append(item_key)
                    else:
                        self.warning.append(self._update_item(item_key, 'NewOnly'))

                elif self.oew[item["id"]] == 0:
                    pass    # do nothing

                else:     # pragma: no cover    # safety check only!
                    raise ErrorCockpit(f'Unknown value of oew: [{self.oew[item["id"]]}]: {item_key}')

            for item, cnt in obj.passed.items():
                self.passed[item] += cnt

    def _read_config(self):
        """
        Read the cfg
        :return: True if missing cfg
        """
        if not exists(self.cfg):
            return True
        with open(self.cfg) as fh:
            self.qcfg = json.load(fh)

        self.oew = {}    # off,err,warning  {error_id: 0,1,2}
        for item, val in self.qcfg.items():
            for id, setting in val.items():
                key = int(id)
                self.fname2id[item] = key

                # check first that key is not duplicate
                if key in self.oew:
                    raise ErrorInput(f'Qgate#{key} is defined twice by {item}')

                if setting.lower() == 'off':
                    self.oew[key] = 0
                elif setting.lower() == 'gate':
                    self.oew[key] = 1
                elif setting.lower() == 'warning':
                    self.oew[key] = 2
                elif setting.lower() == 'newonly':
                    self.oew[key] = 3
                else:
                    raise ErrorInput(f'setting [{setting}] is invalid for {item}')

        self.check_250()

        return False

    def check_250(self):
        """
        Routine to check 250 (torch_build) check whether it is:
        a) it is warning   << not allowed
        b) it is missing   << not allowed if 250_qgate_required.txt exist in the same folder as qgate_config
        """
        if 250 in self.oew:
            # check the warning
            confirm(self.oew[250] == 1,
                    'Qgate 250 (torch_build error check) is not a gate. This is required to be a gate',
                    'Pls put back to gate, and change .editorconfig or add waivers instead')
        else:
            if exists(f'{dirname(self.cfg)}/250_qgate_required.txt'):
                raise ErrorInput('Qgate 250 is missing in qgate config. This is not allowed',
                                 'Pls put back to gate, and change .editorconfig or add waivers instead for Torch build errors')

    def _read_toc(self, fname, cfg):
        """Read the qgate input file and print all error items"""
        robj = re.compile(r'self.add_error\((\d+)')
        for line in File(fname).chomp():
            res = robj.search(line)
            if res:
                classification = cfg.get(res.group(1), 'Gate')
                hname = basename_n(fname.replace(ROOT_ENV, ''), 3)
                print(f'QGate{res.group(1)}: {classification:7} {hname}')

    def _read_modules(self):
        """Read all the qgate .py files"""
        for item in self.qcfg:

            # add full path for pytpd qgate
            if '/' in item:
                fpitem = f'{self.tpobj.tpldir}/{item}'
            else:
                root_py = dirname(dirname(__file__))
                fpitem = f'{root_py}/qgates/{item}'

            if OPT.toc:
                self._read_toc(fpitem, self.qcfg[item])

            # import it
            log.info(f'-i- Importing {fpitem}')
            pymodule = SourceFileLoader(sha1(fpitem), fpitem).load_module()

            # find all qgate objects
            for obj in dir(pymodule):
                cls = getattr(pymodule, obj)
                if isinstance(cls, type(object)) and issubclass(cls, QGateBase) and obj != 'QGateBase':
                    self.qcls.append(cls)
                    self.cls2id[cls] = self.fname2id.get(item, 101)     # qgate id 101 if undefined

        if OPT.toc:
            exit(0)   # Done

    @classmethod
    def set_repo_dir(cls):
        """Assign the repo dir. Normal cwd of qgate is exported TP"""
        QGateExecute.repodir = os.getcwd()

    @classmethod
    def set_modfiles(cls, modfiles):
        """Assign the modified files"""
        cls._modfiles = modfiles

    def _is_modified(self, module):
        """Return True if module is part of modified files"""
        # caseA: As individual executable - it should display error
        if basename(CALLERBIN) in ('nvl_buildtp.py', 'runner_botos.py',
                                   'qgate.py', 'buildtp.py', 'torch_mv', 'torch_mv.py', 'torch_postproc.py'):
            pass             # continue as normal
        else:
            return True      # Always modified (aka, qgate individual run)

        # caseB: As qgate.py or TorchPostProcess - considered no modified files - default case

        # case1: BASE means any file without Modules
        if module == 'BASE':
            for item in self._modfiles:
                if 'Modules' not in item:
                    return True
            return False

        # case2: module match any of the modified file
        rmodulefolder = re.compile(r'\bModules\b')     # Module Folder
        for item in self._modfiles:
            if module in item and rmodulefolder.search(item):
                return True

        # case3: translation of testplan to module
        f2p = self.tpobj.mtpl.get_modfolder2mod()   # folder-to-plan: {module_folder_name: module_testplan_name}
        p2f = reverse_keyval(f2p)     # plan-to-folder: {module_testplan_name: module_folder_name}
        mod_fname = p2f.get(module, '_NOTFOUND')
        for item in self._modfiles:
            if mod_fname in item and rmodulefolder.search(item):
                return True

        return False


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    obj_qg = QGateArgs()
    obj_qg.main()
