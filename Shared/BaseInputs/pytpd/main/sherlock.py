#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script is Sherlock's static TP checkers
"""
import setenv      # must be first in the imports
import os
import re
import glob
import gzip
import time
import json
from os.path import dirname, basename, exists
from collections import defaultdict, OrderedDict
from gadget.errors import ErrorCheck, confirm, ErrorEnv, ErrorUser
from gadget.printmore import PrintAlign
from gadget.tputil import remove_ip, get_param, CheckerLog
from gadget.gizmo import Elapsed
from gadget.helperclass import IS_UT
from gadget.strmore import curtime, strvalue, truncate, to_str
from gadget.disk import mkdirs, Allfiles
from gadget.shell import USERNAME, fullcmdline, HOSTNAME, SystemCall, CALLERBIN
from gadget.files import File
from gadget.dictmore import xmlfunc, find_dot_items
from tp.testprogram import TestProgram, Env
from mod.setting import cfg
from mod.checks import SpecialCharCheck
from gadget.pylog import log
from pprint import pprint
from xml.etree import cElementTree as ElementTree


class Checkers:
    """
    Static checkers for TP quality
    """

    def __init__(self, tpobj=None):
        # state variables
        self.input_tpobj = tpobj
        self.chks = {}  # checks to run
        self.data = {}  # data needed to run a check
        self.skipchks = []  # checks to be skipped
        self.sum = defaultdict(dict)  # {mod1: {'e': 0, 'w': 0, 'p': 0}} generic checker dictionary
        self.ipcpu = set()  # set of ipcpu modules in all stpls
        self.ippch = set()  # set of ippch modules in all stpls
        self.msgstr = []  # loginfo message list dump area
        self.cornerids = []  # per bom cornerid list, gets resets everytime mtl_getvalidcid runs
        self.sw = Elapsed()  # elapsed time
        self.renenv = 0  # self trigger by sherlock to rename env files when there are errors/triggers seen
        self.allerrors = set()    # Final error set
        self.tpobj = None

        # output paths
        self.full_chksumrpt = None   # Full Checkers report with pass/fail data
        self.err_chksumrpt = None    # Errors only report

        # default config data
        self.cfg = {
            'sum_locinfrachk': cfg.socinfra,  # {mod1: {'e': 0, 'w': 0, 'p': 0}} soc infra loc dictionary
            'idutmods': cfg.idutmods,  # idut modules that can be ignored, auto-gen by TPIE
            'idutinfras': cfg.idutinfras,  # TPI base modules used for idut, PKG modules in IP subflows
            'cttrchk_imod': cfg.cttrchk_ignoremods,  # modules that are excluded from cttr check immune
            'vsubflows': cfg.subflows,  # valid subflows based from ITS
            'ipcpuflows': cfg.ipcpu_subflows,  # valid ipcpu subflows from ITS
            'ippchflows': cfg.ippch_subflows,  # valid ippch subflows from ITS
            'pkgflows': cfg.pkg_subflows,  # valid pkg subflows from ITS
            'srhchkflows': cfg.srhchk_subflows,  # valid ip_ srh/chk subflows from ITS
            'ipminflows': cfg.ipmin_subflows,  # valid ip_ subflows that need to have ip min levels
            'srhflows': cfg.srh_subflows,  # valid srh only subflows
            'cdieflows': cfg.cdiesubflows,  # valid cdie subflow, includes ipcpu + pkg subflows
            'sccttrflows': cfg.sccttrflows,  # valid srh/chk cttr subflows
            'reqdfiles': cfg.reqdfiles,  # mandatory files for hvm data upload etc
            'ignore_tests': cfg.ignore_tests,  # tests that can be ignored, auto-gen by TPIE
            'skipbom': cfg.skipbom,  # product boms that sherlock can skip which PDEs agreed on
            'dlvrmodxcare': cfg.dlvrmodxcare,  # modules which have core-less resets
            'dlvrtestxcare': cfg.dlvrtestxcare,  # tests which use core-less resets
            'validvminttstr': cfg.vminttstr,  # truth table strings for vminTC settings
            'prlmvreqtest': cfg.prlmvreqtest,  # must exit DRV reset tests used for parallel MV work
            'prlmvdrvmods': cfg.prlmvdrvmods,  # drv modules containing the "prlmvreqtest"
            'ti_name3': cfg.ti_name3,  # ti_name3 regex
            'ti_name4': cfg.ti_name4,  # ti_name4 regex
            'valid_si': cfg.socinfra,  # valid PKG SOC Infra tests
            'module_si': cfg.simodule,  # valid PKG SOC Infra module
            'fd': cfg.fd  # valid UPS flow domains
        }

        self.set_config()

    def set_config(self):
        """ Configuration overrides for subclasses. """

        # checks to be skipped
        self.skipchks = [
            self.gen_badbuildchk,  # we don't use TPIE
            self.mtl_relaytokenchk,  # we don't program relays in MTL
            self.mtl_reqdrvprlmvchk,  # not doing parallel MV
        ]

        self.read_skip_json()

        # checks to be ran
        self.chks = {
            'glob_initial': [
                # (check routine, errorout)
                (self.gen_spcharchk, True),
                (self.gen_spcharfilechk, True)
            ],
            'per_env': [
                # (check routine, errorout)
                (self.gen_pgmrulechk, True),  # pgmrule checker
                (self.gen_plistchk, True),  # patlist existence checker
                (self.gen_testplacechk, False),  # test to subflow placement checker
                (self.mtl_bannedchk, False),  # bannedchk illegal template/param checker
                (self.gen_badbuildchk, True),  # badbuildchk incorrect/bad build checker
                (self.mtl_relaytokenchk, True),  # evg relay_token usage checker
                (self.mtl_flowdomainchk, True),  # prime bmfc, flow domain checker
                (self.mtl_ipminlvlchk, True),  # ip flows min_lvl usage checker
                (self.mtl_dlvrchk, False),  # dlvr checker
                (self.mtl_ttrpatmapchk, True),  # pattern name map checker
                (self.gen_emptytestchk, True),  # prime bmfc, flow domain checker    ### CONVERTED to QGATE
                (self.mtl_vmintcchk, True),  # vminTC checker
                (self.mtl_vmintcflicbchk, True),  # vminTC checker
                # (self.mtl_ddgshmoochk, False),  # ddgshmoo template checker
                (self.mtl_cttrchk, True),  # cttr/pup compliance checker
                (self.mtl_cttrbnmchk, True),  # cttr/pup compliance checker
                (self.mtl_cttredgechk, True),  # cttr/pup compliance checker
                (self.mtl_cttrbnmdiechk, True),  # cttr/pup compliance checker
                (self.mtl_reqdrvprlmvchk, True),  # required drv parallel tests for MV
                (self.mtl_dedcbbchk, False),  # dedc barebone checker
                (self.gen_edcvskillchk, False),  # edc vs kill checker
                (self.mtl_dup_plist, True),   # checks for duplicate plists within the 3 PLIST_ALL files
            ],
            'per_mtpl_mod': [
                # (check routine, errorout)
                (self.mtl_mfcchk, False)  # module field checker
            ],
            'per_stpl': [
                # (check routine, errorout)
                (self.gen_upchk, True),  # uppercase checker
                (self.gen_fcchk, True),  # testname checker
                (self.gen_sfchk, False),  # subflow checker
                (self.gen_tlchk, True),  # tname length checker
                (self.gen_copycatchk, False),  # copycat checker
                (self.mtl_socinfrachk, False),  # soc infra checker
                (self.mtl_locinfrachk, False),  # log all soc infra tests into sum_locinfrachk {} TODO: maybe not a chk
                (self.mtl_pltscpchk, False),  # PLT scope checker TODO: update to new mechanism
                (self.cttrchk, False),  # cttr checker
                (self.gen_skuchk, True)  # sku checker (error if fail)
            ],
            'glob_final': [
                # (check routine, errorout)
                (self.mtl_ctrlrstchk, False),  # check if DRV*modules are the only ones using the drv patches
                (self.mtl_cntinfrachk, True),  # check if all soc infra tests are present
                (self.gen_reqdfileschk, True),  # check if all mandatory files are present in the TPL
                (self.gen_supercedechk, True),  # check if all Supersedes/code files are documented
                (self.gen_duplicate_envvar, True),   # check for duplicate env var
            ]

        }

    def set_glob_data(self):
        """
        Set up global data for a check
        :return:
        """

        envs = [x for x in glob.glob('./*TP/*/EnvironmentFile*.env') if not x.endswith('.g.env')]
        confirm(len(envs) == 1,
                f'Expecting one Environment file. found: {envs}',
                f'Pls check: {os.getcwd()}')
        modpatch = self.gen_fetchinteg()
        env = envs[0]
        self.full_chksumrpt = f'{dirname(env)}/Reports/FULL_Checkers_Report.txt'   # Full Checkers report with pass/fail data
        self.err_chksumrpt = f'{dirname(env)}/Reports/ERRORS_Checkers_Report.txt'  # Errors only report
        self.tpobj = self.set_tpobj(env)

        bt = self.tpobj.get_buildtype()
        # TODO: jqdelosr Enable this, commented out due to sloooooow!
        badfiles = {}   # SpecialCharCheck('.').main().result  # {<path>/file1: list_of_errors}
        filepaths = Allfiles('.')  # grep all files from TPL down to all the insides of the module folders

        # update data
        self.data.update({
            'modpatch': modpatch,
            'bt': bt,
            'badfiles': badfiles,  # {<path>/file1: list_of_errors}
            'filepaths': filepaths,  # grep all files from TPL down to all the insides of the module folders
            'valid_si': self.cfg['valid_si'],
            'locinfrachk': self.cfg['sum_locinfrachk'],
            'reqdfiles': self.cfg['reqdfiles']
        })

    def set_tpobj(self, env):
        """
        :param env: Envfile
        :return: Testprogram object
        """
        if self.input_tpobj:
            log.info(f'-i- TP from init caller: {env}')
            return self.input_tpobj

        try:
            log.info(f'-i- TP: {env}')
            return TestProgram(env).init()    # Do not pickle, too many files
        except Exception as e:
            msg = 'FATAL ERROR from Sherlock\'s MTPL Parser\n' \
                'Sherlock tpdata parser did not execute correctly!\n' \
                '%s' % e
            with open(self.err_chksumrpt, 'w') as file:
                file.write(msg)
            with open(self.full_chksumrpt, 'w') as file:
                file.write(msg)
            log.info(e)
            raise ErrorEnv('FATAL ERROR from Sherlock\'s MTPL Parser',
                           'Sherlock tpdata parser did not execute correctly!')

    def set_env_data(self):
        """
        Set up env data required for env checks
        :return:
        """

        tp = self.tpobj
        bom = tp.get_bom()
        bmdata = tp.bin_matrix(bom)  # parse bmfc for use in diff functions
        data_tp = sorted(list(tp.mtpl.iter_tests(edict=True)))
        bomplbs = [tp.env.to_unixpath(x) for x in tp.env.get_contents('HDST_PLIST_PATH').split(';')]
        sorted_mods = sorted(tp.mtpl.get_modules())

        # state varaibles update
        self.ipcpu.update({basename(dirname(x)) for x in tp.get_all_mtpl_from_stpl('IP_CPU')})  # ipcpu modules
        self.ippch.update({basename(dirname(x)) for x in tp.get_all_mtpl_from_stpl('IP_PCH')})  # ippch modules
        self.cornerids = self.mtl_getvalidcid(bom)  # get valid corner id per bom, must run before vminTC checker

        testtrace = {}
        for mod, test, trc in tp.mtpl.iter_flows('MAIN', traceinfo=True):
            testtrace[(mod, test)] = trc

        fpgmrule = self.gen_pgmruleprep(data_tp)
        revs = self.gen_preplbchk(bomplbs)
        testinstances = list(tp.mtpl.iter_tests(key_name='patlist', edict=True))
        plbmap = tp.plists.get_plb_map()
        mtplobj = tp.mtpl
        ipcpuflows = self.cfg['ipcpuflows']
        ippchflows = self.cfg['ippchflows']
        pkgflows = self.cfg['pkgflows']
        ipminflows = self.cfg['ipminflows']
        cdieflows = self.cfg['cdieflows']
        srhflows = self.cfg['srhflows']
        bomflows = bmdata.keys()

        # update data
        self.data.update({
            'tp': tp,
            'bom': bom,
            'bmdata': bmdata,
            'stpldata': data_tp,
            'bomplbs': bomplbs,
            'ipcpu': self.ipcpu,
            'ippch': self.ippch,
            'cids': self.cornerids,
            'sorted_mods': sorted_mods,
            'testtrace': testtrace,
            'fpgmrule': fpgmrule,
            'revs': revs,
            'testinstances': testinstances,
            'plbmap': plbmap,
            'mtplobj': mtplobj,
            'ipcpuflows': ipcpuflows,
            'ippchflows': ippchflows,
            'pkgflows': pkgflows,
            'ipminflows': ipminflows,
            'cdieflows': cdieflows,
            'srhflows': srhflows,
            'bomflows': bomflows
        })

    def set_mod_data(self, mod):
        """
        Set up data of an individual module for module checks
        :param mod: ARR_CORE_CXX
        :return:
        """

        # update data
        self.data.update({
            'mod': mod
        })

    def set_stpl_data(self, mod, test, data, tpobj):
        """
        Set up data for stpl checks
        :param: stpl = mod, test, data, tpobj
        :return:
        """

        p = data.get('patlist')
        l = get_param(data, 'level')      # pragma: no pep8 E741
        t = get_param(data, 'timing')
        pr = data.get('PreInstance', data.get('preinstance', None))
        b = data.get('ScoreboardBaseNumber', data.get('base_number', None))

        self.data.update({
            'mod': mod,
            'test': test,
            'data': data,
            'p': p,
            'l': l,
            't': t,
            'pr': pr,
            'b': b
        })

    def main(self):
        """Main entry point"""
        # set up global data
        errored = None
        report = None
        try:
            self.set_glob_data()
            report = self._main()
        except (ErrorEnv, ErrorUser) as e:
            errored = str(e)
            log.info(errored)

        # decide if raise exception or not based on TP and self.allerrors
        self.final_decide_error(errored)
        return report

    def _main(self):
        """
        sherlock lines up all the checker's functions that needs to run
        :return:
        """

        # initial global checks
        for check, errorout in self.chks['glob_initial']:
            self.run_check(check, errorout, **self.data)

        # set up env data
        self.set_env_data()

        # set up mod data
        for mod in self.data['sorted_mods']:
            self.set_mod_data(mod)
            # run per mtpl module checks
            for check, errorout in self.chks['per_mtpl_mod']:
                self.run_check(check, errorout, **self.data)

        # set up stpl data
        for data in self.data['stpldata']:
            self.set_stpl_data(*data)
            # run per stpl checks
            for check, errorout in self.chks['per_stpl']:
                self.run_check(check, errorout, **self.data)

            # This one has to be outside of the initial loop above as we need to know all the SOC infra first
            # TODO: Need to see if we can refactor this down the road to have the for loop inside the function itself
            self.run_check(self.mtl_ioepltscpchk, False, **self.data)

        # run checks per env
        for check, errorout in self.chks['per_env']:
            self.run_check(check, errorout, **self.data)

        # run final checks
        for check, errorout in self.chks['glob_final']:
            self.run_check(check, errorout, **self.data)

        # clean and write reports
        self.gen_writer()  # write and stream data out
        self.gen_badenv(self.renenv)  # rename .env to *CHKFAILED.env
        # self.env_gate_rename()     # env gate
        self.gen_janitor()

        return self.err_chksumrpt

    def final_decide_error(self, errored):
        """
        Decide if raise exception or not based on TP and self.allerrors:

        Phase1: trigger file does not exist
                -> sherlock is 100% report only, even on parsing errors (errored is True)
        Phase2: trigger file exist, with some lines:
                grep -- '-Error' ./POR_TP/Class_MTL_P68/Reports/ERRORS_Checkers_Report.txt > Shared/BaseInputs/sherlock.trigger.txt
                -> sherlock will error out only for new errors
        Phase3: trigger any error: Shared/BaseInputs/sherlock.trigger.txt is empty or reduced
                -> This will also make a per-TP configurable for errors that are not warning yet after the fact

        :param errored: None or string_exception
        :return:
        """
        if errored or self.allerrors:
            # At this point, there are errors
            confirm(exists('Shared'),             # Make sure this folder exist so assumption on "skip" is ok.
                    f'[Shared] is not found. cwd: {os.getcwd()}',
                    'Check cwd above. Shared/ is expected to exist')

            trigfiles = glob.glob('Shared/*/sherlock.trigger.txt') + glob.glob('POR_TP/*/sherlock.trigger.txt')
            if trigfiles:
                # determine existing errors, skip them
                confirm(len(trigfiles) == 1, f'Expecting one only: {trigfiles}', 'Pls fix, one only please.')
                current_errors = set(File(trigfiles[0]).read().split('\n'))
                new_errors = {x for x in self.allerrors if x not in current_errors}
                log.info(f'-i- Existing/Previous errors are in: {trigfiles[0]}')

                # Build the message
                if errored:
                    raise ErrorCheck(f'Sherlock has errors: {errored}',
                                     f'Check report: {self.err_chksumrpt}')
                elif new_errors:
                    log.info(f'-i- New Errors for this TP ({len(new_errors)}):')
                    log.info('\n'.join(sorted(new_errors)))
                    raise ErrorCheck(f'Sherlock has errors: {len(new_errors)} new errors. See above for list.',
                                     f'Full error report: {self.err_chksumrpt}')
                else:
                    log.info("-i- Sherlock gate is successful. No new errors.")

            else:
                log.info('-i- Sherlock gate is skipped for this TP: Missing POR_TP/*/sherlock.trigger.txt')

        else:
            log.info("-i- Sherlock gate is successful. Clean run.")

    # # Helper Functions # #

    def run_check(self, fn, errorout, *args, **kwargs):
        """
        Allows you to call checkers by name as a function call to Checkers class.
        :return: fn # fn that are not skipped
        """
        if fn not in self.skipchks:
            errors = fn(*args, **kwargs)

            if errors:
                for e in errors:
                    # bypass - always warning (errout True or False)
                    if e['type'] == 'bypass':
                        error = 'w'
                    # trigger - always Error
                    elif e['type'] == 'trigger':
                        error = 'e'
                    # non-bypass - Error on errorout=True, Warning on errorout=False
                    else:
                        if errorout:
                            error = 'e'
                        else:
                            error = 'w'

                    # dict special cases
                    if 'cttr' in fn.__name__:
                        fn = self.mtl_cttrchk
                    elif 'vmintc' in fn.__name__:
                        fn = self.mtl_vmintcchk

                    # update dict
                    self.sum[fn][e['module']][error] += 1

                    # msg special cases
                    if 'reqdfiles' in fn.__name__:
                        e['module'] = 'ReqdFile'
                    elif 'plblockchk' in fn.__name__:
                        e['module'] = e['error_header']

                    if error == "e":
                        etype = "Error"
                    else:
                        etype = "Warning"
                    self.msgstr.append(f'{e["module"]} -{etype}{e["id"]}- {e["message"]}')

    def read_skip_json(self):
        """Update skipchks based on InputFiles/sherlock_skip_checks.json file"""
        jfile = glob.glob('POR_TP/*/InputFiles/sherlock_skip_checks.json')
        if not jfile:
            return
        assert len(jfile) == 1, f'Expecting one only: {jfile}'
        with open(jfile[0]) as fh:
            data = json.load(fh)

        for key in data:
            self.skipchks.append(getattr(self, key))
            log.info(f'-skipped!- {key} (from json)')

    def gen_badenv(self, renenv):
        """
        This routine renames envfile if self.renenv==1
        :return:
        """
        if renenv:
            envs = glob.glob('EnvironmentFile*.env')
            for env in envs:
                if 'CHKFAILED' not in env:
                    File(env).rename(env[:-4] + '_CHKFAILED.env')

        return

    def env_gate_rename(self):
        """
        Routine to make env unusable so PDE can fix errors

        :return:
        """
        envs = glob.glob('EnvironmentFile*.env')
        for env in envs:
            if 'TRCFAILED' not in basename(env):    # CHKFAILED or TRCFAILED
                continue    # passing env
            if 'CLASS_P68G2' in basename(env):
                continue    # A4 case

            log.info(f"-i- final env file: {env}")
            # uncomment this to see which test is overwriting the file
            # raise Exception(f'About to write {os.getcwd()}/Reports')

            # copy first
            newname = 'file_%s.bat' % File(env).sha1()[:6]
            File(env).copy(f'Reports/{newname}')

            # empty out the env file
            with open(env, 'w') as fh:
                fh.write('There are errors or triggers in this TP\n')
                fh.write('Check Reports/ folder specifically ERRORS_Checkers_Report.txt for details.\n')
                fh.write('Pls fix these errors/triggers first to get proper .env file.\n')
                fh.write('If there are issues, call John Carlos or Sunny. Do not call any other TPD members pls.\n')
                fh.write('\n')

    def gen_janitor(self):
        """
        Cleans up the TPL folders, relocates the ff files into the
        .stpl.old
        .env.old
        trc_report*
        :return:
        """
        ofs = glob.glob('*.old')
        for f in ofs:
            File(f).move('Reports/', overwrite_rename=True)

        return

    def gen_subflow(self, test):
        """
        This function reads the testname and returns the subflow portion; 5th field
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001
        :return: sf  # returns the subflow part of the testname, ex: SCRF1
        """
        t3 = self.cfg['ti_name3'].search(test)
        t4 = self.cfg['ti_name4'].search(test)
        ts = re.compile(r'([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)')  # relaxed SF check
        if t3:
            sf = t3.group(5)
        elif t4:
            sf = t4.group(5)
        else:  # relaxed regex to discount tests that have correct subflow but wrong ti_name convention
            f = ts.search(test)
            if f:
                sf = f.group(5)
            else:
                sf = 'NYET'

        return sf

    def mtl_locinfrachk(self, mod, test, p, l, t, **kwargs):
        """
        SOC INFRA Check, Log all the SOC INFRA tests and save them in a dictionary, expecting DRV_RESET_SXN here
        :param mod: CLK_VIDWALK_CXXK
        :param test: SOME_TEST_ETC_<etc>_.*
        :return: None
        """
        if mod == self.cfg['module_si']:
            mt = '%s::%s' % (mod, test)
            if mt in self.cfg['valid_si']:
                self.cfg['sum_locinfrachk'][mt]['att'] = 'present'
                self.cfg['sum_locinfrachk'][mt]['p'] = p
                self.cfg['sum_locinfrachk'][mt]['l'] = l
                self.cfg['sum_locinfrachk'][mt]['t'] = t

        return

    def gen_report(self, data):
        """
        Summary reporter for checkers, standard printout of modules' warnings, errors, pass counts
        P = Solid pass
        W = EDC error, fix something non-gating later
        E = Kill error, TP may not load if not fixed
        T = Trigger error, Fix ASAP no questions asked
        :param data: {mod1: {'e': 0, 'w': 0, 'p': 0}, mod2: {'e': 0, 'w': 0, 'p': 0}}
        :return: out = <tabulated report per module>
        """
        pa = PrintAlign(rjust=False)
        pa('Module', '[P]ass', '[W]arning', '[E]rror')
        for mod in sorted(data):
            p = data[mod]['p']
            w = data[mod]['w']
            e = data[mod]['e']
            if w > 0 or e > 0:
                pa(mod, p, w, e)
            if e > 0:
                self.renenv = 1

        out = ''
        for item in pa.get_result():
            out += item + '\n'
        if len(pa.get_result()) == 3:
            out = ': -no errors!-\n'

        return out

    def gen_fetchinteg(self):
        """
        Opens the integration report and parses for buildtype and the module snapshot type
        :return: modpatch = { 'aaadrv': ['DRV_RESET_CXX', 'DRV_RESET_GXX'],
                              'scn': ['SCN_CORE', 'SCN_RING'] }
        """
        # open Integration report, get patch to module mapping
        fpath = '*_TP/*/Reports/Integration_Report.txt'
        irg = glob.glob(fpath)
        confirm(len(irg) == 1,
                f'Expecting one Integration_Report.txt. found: {irg}',
                f'Pls check: {os.getcwd()}/{fpath}')
        ir = irg[0]
        modpatch = {}
        with open(ir, 'rb') as file:
            start = False
            for line in file:
                line = to_str(line).strip()
                if not line or line.startswith('#---'):
                    continue
                elif line.startswith('<Pattern Revs'):
                    start = True
                elif line.startswith(('#', '[')):  # --> "#[* indicates modules" unique anchor in integration report
                    start = False
                elif start:
                    rex = re.search(r'^(\S+)(\s+)(\S+)(\s+)(.*)', line)
                    confirm(rex,
                            f'Unable to parse the plb patch from integration report: [{line}]',
                            f'Check {ir}')
                    _t = rex.group(1)
                    _m = rex.group(5)
                    _mods = _m.replace('*', '').split(',')
                    modpatch[_t] = [x.strip() for x in _mods if x]

        return modpatch

    def mtl_getvalidcid(self, bom):
        """
        This function will read the Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_$BOM_VminForwardingConfiguration.json
        And then store the valid cornerids for vminTC use
        :param bom: current bom that will be used to get the eg CLASS_P68G2, CLASS_P28G2
        :return:
        """
        # get the file first
        fwild = f'Modules/TPI_BASEPRIM_*/InputFiles/*_{bom}_VminForwardingConfiguration.json'
        upsfiles = glob.glob(fwild)
        confirm(upsfiles, f'No files found for {fwild}.', f'Pls check, this is required.')
        confirm(len(upsfiles) == 1 or len(upsfiles) == 2, f'Many files found for {fwild}.', f'Pls check: {upsfiles}')
        if len(upsfiles) == 2:
            confirm(File(upsfiles[0]).read() == File(upsfiles[1]).read(),
                    f'Same file different content: {upsfiles[0]} vs {upsfiles[1]}',
                    f'This is illegal. Fatal error!')
        upsfile = upsfiles[0]

        cornerids = []

        dr = re.compile(r'instances":"(\S+)",')
        nr = re.compile(r'name":"(\S+)",')
        dt = 0
        cr = 0
        with open(upsfile, 'r') as file:
            for line in file:
                line = line.strip()
                if 'instances' in line and not dt and not cr:
                    ins = dr.search(line)
                    if not ins:
                        raise ErrorCheck('Unable to acquire the target ups domain/s from line:%s!' % line,
                                         'Check if upsfile:%s is intact.' % upsfile)
                    dd = ins.group(1)
                    dt = 1
                elif 'corners' in line and dt and not cr:
                    cr = 1
                elif '"name":"F' in line and dt and cr:
                    frs = nr.search(line)
                    if not frs:
                        raise ErrorCheck('Unable to acquire the target freq from line:%s!' % line,
                                         'Check if upsfile:%s is intact.' % upsfile)
                    fd = frs.group(1)
                    for ii in dd.split(','):
                        cc = '%s@%s' % (ii, fd)
                        if cc not in cornerids:
                            cornerids.append(cc)
                        else:
                            raise ErrorCheck('Duplicate cornerid detected:%s from line:%s!' % (cc, line),
                                             'Check if upsfile:%s is intact.' % upsfile)
                elif 'name' in line and dt and cr:
                    dt = 0
                    cr = 0

        return cornerids

    def gen_preplbchk(self, bomplbs):
        """
        Parses env file with TestProgram() help and creates "revs{}" dictionary
        :param bomplbs: ['/intel/hdmxpats/mtl/ARR/RevT123.0/p0/plb', '/intel/hdmxpats/mtl/ARR/RevT123.0/p0/plb/slim',
                         '/intel/hdmxpats/mtl/SCN/RevT324.1/p4/plb']
        :return: revs = ['/intel/hdmxpats/mtl/ARR/RevT123.0/p0/', '/intel/hdmxpats/mtl/SCN/RevT324.1/p4/']
        """
        revs = []
        for d in bomplbs:
            if 'plb' in d and 'slim' not in d:
                revs.append(d.split('plb')[0])  # remove plb dirname from the patch name, then add patch

        return revs

    def gen_pgmruleprep(self, fam, **kwargs):
        """
        This function prepares the fpgmrule dictionary
        fpgmrule = {'ARR_CORE': { 'CORE_TEST': { 'glx': 'Modules/ARR_CORE/Input_Files/pgm.txt', 'bpg': '-1' }},
                    'ARR_RING': { 'RING_TEST': { 'glx': 'Modules/ARR_RING/Input_Files/pgm.txt', 'bpg': None }}}
        :param fam: secret code
        :return: fpgmrule
        """
        fpgmrule = {}
        for mod, test, data, _ in fam:
            if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods']:
                glx = data.get('gl_xpress_file_path')
                bpg = data.get('bypass_global')
                if glx and (bpg is None or int(bpg) != 1):
                    if mod not in fpgmrule:
                        fpgmrule[mod] = defaultdict(str)
                    # guaranteed 1:1, testnames per bom are unique as enforced by TPIE
                    fpgmrule[mod][test] = {'combo': {}, 'glx': '', 'bpg': ''}
                    fpgmrule[mod][test]['glx'] = glx
                    fpgmrule[mod][test]['bpg'] = bpg
                    # print(f'Hey {mod} {test} {bpg}')

        return fpgmrule

    def gen_writer(self):
        """
        Prints report to SUMMARY file and to the console
        :return: None
        """
        test_mapping = OrderedDict([
            (self.mtl_mfcchk, 'ModuleName FieldCount Report'),
            (self.gen_upchk, 'Testname UpperCase Report'),
            (self.gen_fcchk, 'Testname Convention Report'),
            (self.gen_sfchk, 'Testname Subflow Report'),
            (self.gen_tlchk, 'Testname Length Report'),
            (self.gen_copycatchk, 'CopyCat Compliance Report'),
            (self.mtl_pltscpchk, 'PLT iDUT Compliance Report'),
            (self.mtl_ioepltscpchk, 'IOE PLT iDUT Compliance Report'),  # TODO: Remove this when IOE rtcCLK is fixed
            (self.mtl_cntinfrachk, 'SOC INFRA Existence Report'),
            (self.mtl_socinfrachk, 'SOC INFRA Compliance Report'),
            (self.mtl_ipminlvlchk, 'IP_SubFlows IP_MinLevels Report'),
            (self.mtl_reqdrvprlmvchk, 'RESET Tests Existence ParallelMV Report'),
            (self.mtl_relaytokenchk, 'RelayToken Usage Report'),
            (self.gen_plistchk, 'Missing Patlist Report'),
            (self.mtl_ctrlrstchk, 'Central Reset Lockout Report'),
            (self.gen_pgmrulechk, 'PGMRules Compliance Report'),
            (self.gen_spcharchk, 'Weird Char Inside Files Report'),
            (self.gen_spcharfilechk, 'Invalid Char In FileNames Report'),
            (self.mtl_bannedchk, 'Illegal Template/Params Report'),
            (self.gen_badbuildchk, 'Bad TPIE Build Report'),
            (self.gen_emptytestchk, 'EmptyTest Compliance Report'),
            (self.gen_reqdfileschk, 'Required Files Report'),
            (self.gen_supercedechk, 'Supercede Code Compliance Report'),
            (self.gen_duplicate_envvar, 'Duplicate Env Report'),
            (self.mtl_dlvrchk, 'DLVR Callback Compliance Report'),
            (self.gen_testplacechk, 'Test-to-Subflow Placement Report'),
            (self.mtl_flowdomainchk, 'UPS FlowDomain Compliance Report'),
            (self.mtl_vmintcchk, 'VminTC SpeedFlow Compliance Report'),
            (self.mtl_ttrpatmapchk, 'Pattern_Name_Map Compliance Report'),
            (self.mtl_cttrchk, 'CTTR PUP Compliance Report'),
            (self.mtl_dedcbbchk, 'DEDC Barebone Compliance Report'),
            (self.gen_edcvskillchk, 'EDC vs KILL Compliance Report'),
            (self.mtl_vmintcflicbchk, 'FlowIndexCallbackName inside CHK speedflow Report'),
            (self.mtl_cttrbnmchk, 'TTR Base number uniqueness Report'),
            (self.mtl_cttredgechk, 'TTR CHK subflow Report'),
            (self.mtl_cttrbnmdiechk, 'TTR Base number die_number Report'),
            (self.mtl_locinfrachk, 'SOC INFRA Check Report'),
            (self.cttrchk, 'testinstance subflow matches patlist Report'),
            (self.mtl_dup_plist, 'Duplicate Plist Compliance Report'),
            (self.gen_skuchk, 'Recovery SKU TPD vs YBS compare'),
        ])

        # confirm all tests are in
        for cat1 in self.chks:
            for code, _ in self.chks[cat1]:
                confirm(code in test_mapping, f'Error: {code} is not defined in test_mapping!', 'Contact jqdelosr')

        # report table
        sr = ''
        err_sr = ''
        for f, t in test_mapping.items():

            # skiped check condition
            if f in self.skipchks:  # pragma: no cover
                sr += t + ': -skipped!-\n' + '\n'
                continue

            sum = self.sum[f]
            rpt = self.gen_report(sum)      # The entire table
            if 'no errors' in rpt:
                sr += t + rpt + '\n'
            else:
                sr += t + '\n'
                sr += rpt + '\n'
                err_sr += t + '\n'
                err_sr += rpt + '\n'

        # printout
        log.info(sr)  # full report
        log.info('\nError Codes Explained: https://goto.intel.com/errorcheck')
        self.allerrors = {x for x in self.msgstr if '-Error' in x}
        if self.allerrors:
            log.info('\nError Message Stream:')
            log.info(truncate('\n'.join(sorted(self.allerrors))))
        else:
            log.info('\nCLEAN run! No Errors.')

        # write to file
        with open(self.full_chksumrpt, 'w') as file:
            file.write(sr)
            file.write('\n\n\n\nError Codes Explained: https://goto.intel.com/errorcheck\n')
            file.write('\nError Message Stream\n')
            file.write('\n'.join(sorted(self.msgstr)))

        with open(self.err_chksumrpt, 'w') as file:
            file.write(err_sr)
            file.write('\n\n\n\nError Codes Explained: https://goto.intel.com/errorcheck\n')
            if self.allerrors:
                file.write('\nError Message Stream:\n')
                file.write('\n'.join(sorted(self.allerrors)))
                log.info(f'\nError report file: {self.err_chksumrpt}')
            else:
                file.write('\nCLEAN run! No Errors.')

        log.info(f'\nFull report file:  {self.full_chksumrpt}')
        return

    # # Checks # #

    def gen_skuchk(self, mod, test, data, **kwargs):
        """
        Confirm YBS SKU and TPD SKU are the same
        :param stpldata:
        :param mtplobj:
        :return:
        """
        if mod not in self.cfg['ignore_tests'] and mod not in self.cfg['idutmods']:
            if mod not in self.sum[self.gen_skuchk]:  # add module if not in sum
                self.sum[self.gen_skuchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            # start check
            if data['TEMPLATE'] == 'DieRecoveryBase':  # only instance with TEMPLATE = DieRecoveryBase

                # get rules and sku files
                RulesFile = data['RulesFile']  # JSON TP file

                # get SKUs from rules file
                with open(RulesFile) as f:
                    TPD_COPY = set()
                    try:
                        rules = json.load(f)
                    except json.decoder.JSONDecodeError as e:
                        return [{
                            'type': 'bypass',
                            'message': f'Recovery SKU TPD vs YBS compare check failed, RulesFile is invalid or empty: {RulesFile}',
                            'id': '210',
                            'module': mod
                        }]

                    if "ALLSKU" not in rules:  # if "ALLSKU" key does not exits, fail
                        return [{
                            'type': 'bypass',
                            'message': f'Recovery SKU TPD vs YBS compare check failed, make sure RulesFile contains "ALLSKU"',
                            'id': '208',
                            'module': mod
                        }]

                    TPD_COPY.update(rules["ALLSKU"][0]["SKUs"])  # save all SKUs inside TPD_COPY
                    SKUFile = rules["ALLSKU"][0]["Ref"]  # save Ref SKUs file name

                if not exists(SKUFile):
                    return    # Do nothing if file is missing

                # get SKUs from XML file
                with open(SKUFile) as f:
                    tree = ElementTree.parse(f)
                    YBS_COPY = set([sku.get('group') for sku in tree.findall('./Area/SKUs')])

                # check if YBS_COPY are equal and if not error out
                difference = YBS_COPY.symmetric_difference(TPD_COPY)
                if YBS_COPY == TPD_COPY:  # if the files are equal
                    self.sum[self.gen_skuchk][mod]['p'] += 1
                    return
                else:  # if len is not zero, there is a difference
                    return [{
                        'type': 'non_bypass',
                        'message': f'Recovery SKU TPD vs YBS compare check failed for test: {test}, difference: {difference}',
                        'id': '209',
                        'module': mod
                    }]
        return

    def mtl_mfcchk(self, mod, **kwargs):
        """
        Update self.sum_mfc checker count, fields must be 3 in length, otherwise count as error
        :param mod: module name (ex ARR_CORE_CXX)
        :param mfc: field count (ex 3)
        :return: None
        """
        mfc = mod.count('_') + 1

        if mod not in self.cfg['idutmods']:
            self.sum[self.mtl_mfcchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            if mfc != 3:
                return [{
                    'type': 'non_bypass',
                    'message': f'ModuleName FieldCount check failed, must have 3fields',
                    'id': '111',
                    'module': mod
                }]
            else:
                self.sum[self.mtl_mfcchk][mod]['p'] += 1

        return

    def gen_upchk(self, mod, test, **kwargs):
        """
        Update self.sum_up checker count, all characters must be UPPER CASE
        :param mod: module name (ex: ARR_CORE_CXX)
        :param test: testinstance name (ex: EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401)
        :return: None
        """
        if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods']:
            if mod not in self.sum[self.gen_upchk]:
                self.sum[self.gen_upchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            if test.isupper():
                self.sum[self.gen_upchk][mod]['p'] += 1
            else:
                return [{
                    'type': 'non_bypass',
                    'message': f'UpperCase check failed for test: {test}',
                    'id': '112',
                    'module': mod
                }]

        return

    def gen_fcchk(self, mod, test, **kwargs):
        """
        Update self.sum_fc checker count, FieldCount == Testname Convention
        :param mod: module name (ex: ARR_CORE_CXX)
        :param test: testinstance name (ex: EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401)
        :return: None
        """
        if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods']:
            if mod not in self.sum[self.gen_fcchk]:
                self.sum[self.gen_fcchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            t3 = self.cfg['ti_name3'].search(test)
            t4 = self.cfg['ti_name4'].search(test)

            if t3:
                self.sum[self.gen_fcchk][mod]['p'] += 1
            elif t4:
                self.sum[self.gen_fcchk][mod]['p'] += 1
            else:
                return [{
                    'type': 'non_bypass',
                    'message': f'Testname Convention check failed for test: {test}',
                    'id': '113',
                    'module': mod
                }]

        return

    def gen_sfchk(self, mod, test, **kwargs):
        """
        Update self.sum_sf (subflow) checker count, verifies test uses a valid subflow name
        :param mod: module name (ex: ARR_CORE_CXX)
        :param test: testinstance name (ex: EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401)
        :return: None
        """
        """
        Update self.sum_sf (subflow) checker count, verifies test uses a valid subflow name
        """
        if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods']:
            if mod not in self.sum[self.gen_sfchk]:
                self.sum[self.gen_sfchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            sf = self.gen_subflow(test)

            if sf == 'NYET':
                return [{
                    'type': 'non_bypass',
                    'message': f'TestName Convention failed hence unable to parse subflow correctly for test: {test}',
                    'id': '114',
                    'module': mod
                }]
            elif sf != 'NYET' and sf not in self.cfg['vsubflows']:
                return [{
                    'type': 'non_bypass',
                    'message': f'Invalid subflow={sf} from test: {test}',
                    'id': '115',
                    'module': mod
                }]
            else:
                self.sum[self.gen_sfchk][mod]['p'] += 1

        return

    def gen_edcvskillchk(self, stpldata, **kwargs):
        """
        Check testname edc/kill field and compare actual setting, fail if mismatch
        :param stpldata:
        :param mtplobj:
        :return:
        """
        errors = []
        ts = re.compile(r'([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)')  # relaxed tname regex
        for mod, test, data, _ in stpldata:
            error_message = ''
            t = ts.search(test)
            if not t:
                continue
            tnm = t.group(4)

            kil = data.get('_EDCKIL')
            if mod not in self.sum[self.gen_edcvskillchk]:
                self.sum[self.gen_edcvskillchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            if tnm == 'K' and kil == 'KIL':  # valid KILL test
                continue
            elif tnm == 'E' and kil == 'EDC':  # valid EDC test
                continue
            elif tnm == 'K' and kil == 'EDC':  # testname KILL but actual port connections are EDC
                error_num = '195'
                error_message = f'Test:{test} says KILL in tname but port connections are in EDC'
            elif tnm == 'E' and kil == 'KIL':  # testname EDC but actual port connections are KILL
                error_num = '196'
                error_message = f'Test:{test} says EDC in tname but port connections are in KILL'

            if len(error_message) > 0:
                errors.append({
                    'type': 'non_bypass',
                    'message': error_message,
                    'id': error_num,
                    'module': mod
                })

        if len(errors) > 0:
            return errors

        return  # pragma: no cover

    def cttrchk(self, mod, test, p, b, **kwargs):  # TODO update docstring, update the cttr checker update autobase# is ready
        """
        update self.sum_cttr checker count
        Checks testinstance subflow matches patlist subflow
        """
        # this is a relaxed test subflow regex, must get ts.group(5)
        ts = re.compile(r'([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)')
        # this patlist regex matches for any patlist form "IP_CPU::drv_soc_end_ph1a_list" or "drv_soc_end_ph1a_list"
        ps = re.compile(r'([a-z0-9]+)_([a-z0-9]+)_([a-z0-9]+)_([a-z0-9_]+)_list')

        error = False

        if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['cttrchk_imod'] and p and b:
            if mod not in self.sum[self.mtl_cttrchk]:
                self.sum[self.mtl_cttrchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            tf = ts.search(test)
            pf = ps.search(p)
            if tf and pf:
                tsf = tf.group(5).upper()  # testinstance subflow
                psf = pf.group(3).upper()  # patlist subflow
                if tsf == psf:
                    self.sum[self.mtl_cttrchk][mod]['p'] += 1    # patalist subflow == testinstance subflow
                else:  # patlist subflow != testinstance sublow
                    error = True
                    error_message = f'Patlist used in wrong test/subflow, test:{test} subflow:{tsf} != patlist:{p} subflow:{psf}'
                    error_num = '116'
            else:  # unable to parse patlist and/or testinstance
                error = True
                error_message = f'Unable to check cttr compliance for test: {test} patlist:{p} base#:{b}'
                error_num = '117'

        if error:
            return [{
                'type': 'non_bypass',
                'message': error_message,
                'id': error_num,
                'module': mod
            }]

        return

    def mtl_pltscpchk(self, mod, test, p, l, t, ipcpu, ippch, **kwargs):
        """
        PLT Scope Check
        Update self.sum_pltscpchk checker count (PLT scope)
        :param mod: ARR_CORE_CXX
        :param test: EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401
        :param p: IP_CPU::arr_core_end_bist_list
        :param l: ip_levels
        :param t: IP_CPU:IP_CPU_BASE:<timings>
        :param ipcpu: {'DUMMY_CPU', 'ARR_CORE_CXX', 'IP_CPU_BASE'}
        :param ippch: {'DUMMY_PCH', 'ARR_CORE_PXX', 'IP_PCH_BASE'}
        :return: None
        """
        # if not test.startswith(self.ignore_tests) and mod not in self.idutmods and p and l and t:
        #     if self.mtl_pltscpchk not in self.sum:
        #         self.sum[self.mtl_pltscpchk] = {}
        #     if mod not in self.sum_pltscpchk:
        #         self.sum[self.mtl_pltscpchk][mod] = {'e': 0, 'w': 0, 'p': 0}

        error_message = ''
        if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods'] and p and l and t:
            if mod not in self.sum[self.mtl_pltscpchk]:
                self.sum[self.mtl_pltscpchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            ic = 'IP_CPU'
            ip = 'IP_PCH'
            plt = p + l + t
            ia = ipcpu | ippch

            if ic not in plt and ip not in plt and (('_pkg_' in l) or ('_die_' in l)) and mod not in ia:
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1  # sc01/sc04/sc23/sc24 pass
            elif ic not in p and ip not in p and ic in l and ic in t and mod in ipcpu:  # sc02 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic not in p and ip not in p and ip in l and ip in t and mod in ippch:  # sc03 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic in p and ic in l and ic in t and mod in ipcpu:  # sc21 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ip in p and ip in l and ip in t and mod in ippch:  # sc22 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic not in p and ip not in p and mod in l and mod in t and mod in ipcpu:  # sc05 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic not in p and ip not in p and mod in l and mod in t and mod in ippch:  # sc06 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic not in p and ip not in p and ic in l and mod in t and mod in ipcpu:  # sc07 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic not in p and ip not in p and mod in l and ic in t and mod in ipcpu:  # sc08 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic not in p and ip not in p and ip in l and mod in t and mod in ippch:  # sc09 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic not in p and ip not in p and mod in l and ip in t and mod in ippch:  # sc10 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic in p and ic not in l and ip not in l and mod not in l and ic in t and mod not in ia:  # sc11 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ip in p and ic not in l and ip not in l and mod not in l and ip in t and mod not in ia:  # sc12 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic in p and mod in l and (('_pkg_' in l) or ('_die_' in l)) and ic in t and mod not in ia:  # sc13 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ip in p and mod in l and (('_pkg_' in l) or ('_die_' in l)) and ip in t and mod not in ia:  # sc14 pass
                self.sum[self.mtl_pltscpchk][mod]['p'] += 1
            elif ic in p and mod in l and (('_pkg_' not in l) and ('_die_' not in l)) and ic in t and mod not in ia:
                # sc15 fail
                error_message = f'PKG module using IP_CPU::patlist cannot use Levels with overrides test:{test} p={p} l={l} t={t}'
                error_number = '144'
                error_type = 'non_bypass'  # can be error or warning
            elif ip in p and mod in l and (('_pkg_' not in l) and ('_die_' not in l)) and ip in t and mod not in ia:
                # sc16 fail
                error_message = f'PKG module using IP_PCH::patlist cannot use Levels with overrides test:{test} p={p} l={l} t={t}'
                error_number = '145'
                error_type = 'non_bypass'  # can be error or warning
            elif ic in p and ic not in l and ip not in l and mod not in l and mod in t and mod not in ia:  # sc17 fail
                error_message = f'PKG module using IP_CPU::patlist cannot use Timings with overrides test:{test} p={p} l={l} t={t}'
                error_number = '138'
                error_type = 'non_bypass'  # can be error or warning
            elif ip in p and ic not in l and ip not in l and mod not in l and mod in t and mod not in ia:  # sc18 fail
                error_message = f'PKG module using IP_PCH::patlist cannot use Timings with overrides test:{test} p={p} l={l} t={t}'
                error_number = '139'
                error_type = 'non_bypass'
            elif ic in p and ic in l and ic in t and mod not in ia:  # sc19 fail
                error_message = f'PKG module using IP_CPU in these params patlist/timings/levels test:{test} p={p} l={l} t={t}'
                error_number = '142'
                error_type = 'non_bypass'
            elif ip in p and ip in l and ip in t and mod not in ia:  # sc20 fail
                error_message = f'PKG module using IP_PCH in these params patlist/timings/levels test:{test} p={p} l={l} t={t}'
                error_number = '143'
                error_type = 'non_bypass'
            else:
                error_message = f'Patlist/levels/timings are not matching idut scope on test:{test} p={p} l={l} t={t}'
                error_number = '118'
                error_type = 'non_bypass'

        if len(error_message) > 0:
            return [{
                'type': error_type,
                'message': error_message,
                'id': error_number,
                'module': mod
            }]

        return

    def mtl_ioepltscpchk(self, mod, test, p, l, t, ipcpu, ippch, **kwargs):
        """
        PLT Scope Check for IOE modules that are not DRV
        Update self.sum_pltscpchk checker count (PLT scope)
        :param mod: PSCN_SCN_IXX
        :param test: EVMINS_IOE_VMIN_K_BEGIOEPKG_X_VX_F1_X_2401
        :param p: pscn_ioe_begioepkg_cell_list
        :param l: _pkg_levels
        :param t: _ioep_pkg_xtal_timings
        :param ipcpu: {'DUMMY_CPU', 'ARR_CORE_CXX', 'IP_CPU_BASE'}
        :param ippch: {'DUMMY_PCH', 'ARR_CORE_PXX', 'IP_PCH_BASE'}
        :return: None
        """
        error_message = ''
        if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods'] and p and l and t:
            ic = 'IP_CPU'
            ip = 'IP_PCH'
            plt = p + l + t
            ia = ipcpu | ippch

            d = re.search('([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)', mod)
            if not d:  # module not following naming convention, will get flagged at mfcchk()
                return
            die = d.group(3)
            if not die.startswith('I'):  # not an IOE module, skip the check
                return
            if mod.startswith('DRV'):  # IOE module but is DRV, skip the check
                return

            if mod not in self.sum[self.mtl_ioepltscpchk]:
                self.sum[self.mtl_ioepltscpchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            i_t = self.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE']['t']
            i_p = self.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE']['p']
            i_tt = self.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE']['t']
            i_pp = self.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE']['p']
            if ic not in plt and ip not in plt and (('_pkg_' in l) or ('_die_' in l)) and mod not in ia:
                if 'ioep_pkg_xtal' in t or 'ioem_pkg_xtal' in t and p != i_p and p != i_pp:
                    self.sum[self.mtl_ioepltscpchk][mod]['p'] += 1  # right lev/tim and patlist is != to any of the IOE socinfras
                elif p == i_p and t == i_t:  # exact match of patlist+timings IOE only
                    self.sum[self.mtl_ioepltscpchk][mod]['p'] += 1
                elif p == i_pp and t == i_tt:  # exact match of patlist+timings CPU+IOE
                    self.sum[self.mtl_ioepltscpchk][mod]['p'] += 1
                elif p == i_p and t != i_t:  # test is using IOE only socinfra patlist but diff timings
                    error_message = f'IOE PKG module is not using correct pkg timings for Astep test:{test} p={p} l={l} t={t} SOCINFRA_TIM={i_t}'
                    error_number = '155'
                    error_type = 'non_bypass'  # can be either error or warning
                elif p == i_pp and t != i_tt:  # test is using CPU+IOE socinfra patlist but diff timings
                    error_message = f'IOE PKG module is not using correct pkg timings for Astep test:{test} p={p} l={l} t={t} SOCINFRA_TIM={i_tt}'
                    error_number = '158'
                    error_type = 'non_bypass'  # can be either error or warning
                else:  # all pkg params but not correct
                    error_message = f'IOE PKG module is not using correct PLT settings for Astep test:{test} p={p} l={l} t={t}'
                    error_number = '157'
                    error_type = 'non_bypass'  # can be either an error or warning
            else:  # one of the params is IP_ scoped
                error_message = f'IOE PKG module is not using correct PLT settings for Astep test:{test} p={p} l={l} t={t}'
                error_number = '156'
                error_type = 'non_bypass'

        if len(error_message) > 0:
            return [{
                'type': error_type,
                'message': error_message,
                'id': error_number,
                'module': mod
            }]

        return

    def gen_pgmrulechk(self, fpgmrule, **kwargs):
        """
        This function will check each pgmrule combo for "ALL"/"ALL_CLASS" operation as pass, else fail it
        :param fpgmrule: {'ARR_CORE': {'CORE_TEST': {'glx': 'Modules/ARR_CORE/Input_Files/pgm.txt', 'bpg': '-1'}},
                          'ARR_RING': {'RING_TEST': {'glx': 'Modules/ARR_RING/Input_Files/pgm.txt', 'bpg': None}}
                          }
        :return: None
        """
        # print the glx files, compile regex ahead of actual search
        re_pgmdata = re.compile(r'(\S+)\s*=\s*(\S+|\"[^\"]+\")\s*,\s*\w+\s*,\s*(\S+)\s*:\s*(\S+)')

        for mod in fpgmrule:
            for test in fpgmrule[mod]:
                glx = fpgmrule[mod][test]['glx']
                with open(glx, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line.startswith('#'):
                            continue
                        elif not line:
                            continue
                        # parse the data with some gibberish grade4 regex
                        pgmdata = re_pgmdata.search(line)
                        param = pgmdata.group(1)
                        param_data = pgmdata.group(2)
                        param_test = pgmdata.group(3)
                        param_locn = pgmdata.group(4)
                        combo = param + '_' + param_test
                        rules = '_'.join([param, param_data, param_test, param_locn])
                        if 'combo' not in fpgmrule[mod][test]:
                            fpgmrule[mod][test]['combo'] = {}
                        if combo not in fpgmrule[mod][test]['combo']:
                            fpgmrule[mod][test]['combo'][combo] = []
                        fpgmrule[mod][test]['combo'][combo].append(rules)

        allocset = ['ALL', 'ALL_CLASS']
        errors = []
        for mod in fpgmrule:
            if mod not in self.sum[self.gen_pgmrulechk]:
                self.sum[self.gen_pgmrulechk][mod] = {'e': 0, 'w': 0, 'p': 0}
            for test in fpgmrule[mod]:
                for combo in fpgmrule[mod][test]['combo']:
                    locn = []
                    for pgmset in range(len(fpgmrule[mod][test]['combo'][combo])):
                        x = re.search(r'\S+,(\S+)', fpgmrule[mod][test]['combo'][combo][pgmset])
                        locset = x.group(1)
                        if locset not in locn:
                            locn.append(locset)

                    # if match == 0, then ERROR
                    match = [(x, y) for x in locn for y in allocset if (x == y or x.startswith(y) or x.endswith(y))]
                    if len(match) == 0:
                        errors.append({
                            'type': 'non_bypass',
                            'message': f'PGMrule test:{test} with action on param|test combo:{combo} does not have default ALL/ALL_CLASS setting',
                            'id': '120',
                            'module': mod
                        })
                    else:
                        self.sum[self.gen_pgmrulechk][mod]['p'] += 1

        if len(errors) > 0:
            return errors

        return  # pragma: no cover

    def gen_plistchk(self, testinstances, plbmap, bom, mtplobj, **kwargs):
        """
        Uses tp_audit algo to read all plist files from env and grab all valid plb names
        Then check if any plb inside mtpls are not present from master copy of valid plb names
        :param testinstances: [('MOD', 'T1', {'TEMPLATE': 'VminTC', 'LevelsTc': 'lvls', 'patlist': '<plist>', etc, '')]
        :param plbmap: {'socn_lr_phase1a_list': '/path/drv_resetA.plist', 'etc_list': '/path/drv_resetA.plist'}
        :param bom: CLASS_P68G2 etc
        :param mtplobj: mtpl object
        :return: None
        """
        # Uses tp_audit algo to read all plist files from env and grab all valid plb names
        # Then check if any plb inside mtpls are not present from master copy of valid plb names
        errors = []
        for mod, test, dd, _ in testinstances:
            if mod.startswith('TPI_PRESI'):  # TODO: temporary waivers for TPI_PRESI
                continue
            if dd['TEMPLATE'] == 'PlistConfigTC':
                continue    # Cannot check patlist for this template since it is regex
            if mod not in self.sum[self.gen_plistchk]:
                self.sum[self.gen_plistchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            plb = remove_ip(dd['patlist'])
            byp = mtplobj.is_bypassed(mod, test)
            if plb not in plbmap and not byp:  # patlist is missing and test in NOT bypassed
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Patlist:{plb} for test:{test} is missing! Bypass:{byp} BOM:{bom}',
                    'id': '121',
                    'module': mod
                })
            elif plb not in plbmap and byp:
                self.sum[self.gen_plistchk][mod]['p'] += 1  # patlist is missing and test is bypassed
            else:
                self.sum[self.gen_plistchk][mod]['p'] += 1  # patlist is existing

        if len(errors) > 0:
            return errors

        return

    def gen_spcharchk(self, badfiles, **kwargs):
        """
        Report out each file per module/base and save sum of errors
        :param badfiles: { <path>/file1: ['error1', 'error2'], <path>/file2: ['error1]}
        :return: None
        """
        errors = []
        rem = re.compile(r'.\/Modules/(\w+)/.*')
        for f in badfiles:  # process only Modules and BaseTPL files
            if 'Reports' in f:  # ignore Reports folder
                continue
            elif 'trc_report_' in f:  # ignore trc_report*csv from TRACE
                continue
            elif 'YBS_' in f and f.endswith('upload.xml'):  # ignore YBS upload.xml file  # TODO: recheck this with JDR
                continue
            elif 'Modules' in f:
                m = rem.search(f)
                if not m:
                    raise ErrorCheck('Unable to parse the module name from the filename:%s!' % f,
                                     'File path is not using front slash?!')
                mod = m.group(1)
            else:
                mod = 'BaseTPL'

            if mod not in self.sum[self.gen_spcharchk]:
                self.sum[self.gen_spcharchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            for er in badfiles[f]:
                if '.xml' in f:  # XMLreader
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'File: {f} failed XMLreader! XMLreader data: {er}',
                        'id': '122',
                        'module': mod
                    })
                else:  # everything else
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'File: {f} has a weird char! LineInFile: {er}',
                        'id': '123',
                        'module': mod
                    })
            # TODO: When isfile used in TP function is added, add that condition here

        if len(errors) > 0:
            return errors

        return  # pragma: no cover

    def gen_spcharfilechk(self, filepaths, **kwargs):
        """
        This function will review all the file path/names and see if the filenames do not have weird characters in them
        :param filepaths:
        :return:
        """
        errors = []
        fr = re.compile(r'[A-Za-z0-9\/\.\_\-\+]+')  # file spchar regex
        mr = re.compile(r'.\/Modules/(\w+)/.*')  # module grep regex
        for f in filepaths:
            mm = mr.search(f)
            if mm:
                mod = mm.group(1)
            else:
                mod = 'BaseTPL'

            ff = fr.search(f)
            ffd = ff.group(0)
            if f != ffd:
                if mod not in self.sum[self.gen_spcharfilechk]:
                    self.sum[self.gen_spcharfilechk][mod] = {'e': 0, 'w': 0, 'p': 0}
                errors.append({
                    'type': 'trigger',
                    'message': f'File:{f} has an invalid char in the name!',
                    'id': '194',
                    'module': mod
                })

        if len(errors) > 0:
            return errors

        return

    def gen_testplacechk(self, testtrace, ipcpuflows, ippchflows, pkgflows, ipcpu, ippch, **kwargs):
        """
        Read each module+testname and check if testname subflow is matching to the subflow it is placed
        :param testtrace: {('mod', 'testname'): ['data1', 'data2] }
        :param ipcpuflows: ['BEGCPU', 'ENDCPU']
        :param ippchflows: ['BEGGT', 'BEGIOE']
        :param pkgflows: ['MAIN', 'ALARM']
        :param ipcpu: ['ARR_CORE_CXX', 'FUN_CORE_CXX']
        :param ippch: ['PSCN_SCN_IXX']
        :return: None
        """
        # scf = self.srhchkflows  # TODO: Enable this here and in the if-statements below once TPI_DFF has been scoped
        errors = []
        for mod, test in testtrace:
            if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods']:
                if mod not in self.sum[self.gen_testplacechk]:
                    self.sum[self.gen_testplacechk][mod] = {'e': 0, 'w': 0, 'p': 0}
                sf = self.gen_subflow(test)

                target = '%s::%s_%s' % (mod, mod, sf)  # TPIE specific mod::mod_subflow convention
                mod2 = '%s::%s_' % (mod, mod)
                if 'NYET' in target:  # this will get flagged in the _sfchk() routine
                    continue
                elif target in testtrace[mod, test]:  # test subflow param matches subflow placement in tpl
                    if mod in ipcpu and sf in ipcpuflows:  # pass: pure ipcpu
                        continue
                    elif mod in ippch and sf in ippchflows:  # pass: pure ippch
                        continue
                    elif mod not in ipcpu and mod not in ippch and sf in pkgflows:  # pass: pure pkg
                        continue
                    elif mod not in ipcpu and mod not in ippch and mod in self.cfg['idutinfras']:  # and sf not in scf:
                        continue  # valid: TPI_ PKG module in IP subflows ex HVBI*
                    elif mod in ipcpu and sf in pkgflows and mod in self.cfg['idutinfras']:  # and sf not in scf:
                        continue  # valid: TPI_ ipcpu module in PKG subflows
                    elif mod in ippch and sf in pkgflows and mod in self.cfg['idutinfras']:  # and sf not in scf:
                        continue  # valid: TPI_ ippch module in PKG subflows
                    elif mod in ipcpu and sf in pkgflows and mod not in self.cfg['idutinfras']:
                        error_num = '148'
                        error_message = f'Test:{test} is IP_CPU scope but is placed in subflow:{sf} that is for PKG testing'

                    elif mod in ippch and sf in pkgflows and mod not in self.cfg['idutinfras']:
                        error_num = '149'
                        error_message = f'Test:{test} is IP_PCH scope but is placed in subflow:{sf} that is for PKG testing'

                    elif mod in ipcpu and sf in ippchflows:  # fail: ipcpu mod in ippch subflow
                        error_num = '124'
                        error_message = f'Test:{test} is IP_CPU scope but is placed in subflow:{sf} that is for IP_PCH testing'

                    elif mod in ippch and sf in ipcpuflows:  # ippch: mod in ipcpu subflow
                        error_num = '125'
                        error_message = f'Test:{test} is IP_PCH scope but is placed in subflow:{sf} that is for IP_CPU testing'

                    elif mod not in ipcpu and mod not in ippch and sf not in pkgflows:  # pkg: mod in ip_ subflow
                        error_num = '126'
                        error_message = f'Test:{test} is PKG scope but is placed in subflow:{sf} that is not valid for PKG testing'

                    else:  # unlikely scenario: test subflow and current subflow match but subflow is not valid|approved
                        error_num = '127'
                        error_message = f'Test:{test} inside invalid subflow:{sf} that might be currently in use for debug'

                else:  # test subflow param mismatch subflow placement in tpl
                    for i in testtrace[mod, test]:
                        if i.startswith(mod2):
                            cs = i.split(mod2)[1]  # current subflow
                            errors.append({
                                'type': 'trigger',
                                'message': '128',
                                'id': f'Test:{test} with subflow:{sf} in tname is actually placed in subflow:{cs}',
                                'module': mod
                            })
                    continue

                errors.append({
                    'type': 'non_bypass',
                    'message': error_message,
                    'id': error_num,
                    'module': mod
                })

        if len(errors) > 0:
            return errors
        return  # pragma: no cover

    def mtl_socinfrachk(self, mod, test, pr, ipcpu, ippch, p, **kwargs):
        """
        SOC INFRA Check for PKG modules, flags modules that invalid use of SOC INFRA test/param
        :param mod: PKG module (ARR_CORE_CXXK)
        :param test: PKG test (EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST)
        :param pr: ExecuteInstance(--testDRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU)
        :param ipcpu: ip_cpu modules [ARR_CORE_CXX, SCN_CORE_CXX, etc]
        :param ippch: ip_pch modules [PSCN_SCN_IXX]
        :return: None
        """
        error_message = ''
        if not test.startswith(self.cfg['ignore_tests']) and mod not in self.cfg['idutmods'] and pr:
            if mod not in self.sum[self.mtl_socinfrachk]:
                self.sum[self.mtl_socinfrachk][mod] = {'e': 0, 'w': 0, 'p': 0}

            if '--test' in pr and p:
                tr = re.search(r'--test(\s+)(\w+::\w+).*', pr)
                if not tr:
                    raise ErrorCheck('SOC Infra UF was used but unable to parse test from preinstance:%s!' % pr,
                                     'Make sure you typed in the correct SOC INFRA test')
                si = tr.group(2)
                if si not in self.cfg['valid_si']:  # fail if any other test is called via ExecuteInstance
                    error_message = f'Test:{test} preinstance:{pr} is using an invalid SOC INFRA:{si}'
                    error_num = '129'
                else:  # valid soc_infra test, make sure PKG test does the soc_infra call
                    if mod in ipcpu:
                        error_message = f'Test:{test} Invalid call of socinfra, IP_CPU test calling a PKG test:{si}'
                        error_num = '130'
                    elif mod in ippch:
                        error_message = f'Test:{test} Invalid call of socinfra, IP_PCH test calling a PKG test:{si}'
                        error_num = '131'

        if len(error_message) > 0:
            return [{
                'type': 'non_bypass',
                'message': error_message,
                'id': error_num,
                'module': mod
            }]

        # TODO: Add DDGShmoo PrePointExec* param checks

        return

    def mtl_cntinfrachk(self, valid_si, locinfrachk, **kwargs):
        """
        SOC INFRA Check, Verify that all tests exist
        :param valid_si: {'DRV_RESET_SXN::INFCPU': {'att': 'absent', 'p': 'infcpugt_list', 'l': '', 't': ''},
                          'DRV_RESET_SXN::INFGT': {'att': 'absent', 'p': 'infcpugt_list', 'l': '', 't': ''},
                          'DRV_RESET_SXN::INFIOE': {'att': 'absent', 'p': 'infcpuioe_list', 'l': '', 't': ''}}
        :param locinfrachk: {'DRV_RESET_SXN::INFCPU': {'att': 'present', 'p': 'infcpugt_list', 'l': 'lvl', 't': 'tim'},
                             'DRV_RESET_SXN::INFGT': {'att': 'present', 'p': 'infcpugt_list', 'l': 'lvl', 't': 'tim'},
                             'DRV_RESET_SXN::INFIOE': {'att': 'present', 'p': 'infcpuioe_list', 'l': 'lvl', 't': 'tim'}}
        :return: None
        """
        errors = []
        mod = self.cfg['module_si']
        self.sum[self.mtl_cntinfrachk][mod] = {'e': 0, 'w': 0, 'p': 0}
        for test in valid_si:
            if locinfrachk[test]['att'] == 'present':
                self.sum[self.mtl_cntinfrachk][mod]['p'] += 1
            else:
                errors.append({
                    'type': 'trigger',
                    'message': f'SOC INFRA test:{test} is missing',
                    'id': '133',
                    'module': mod
                })

        if len(errors) > 0:
            return errors

        return

    def gen_tlchk(self, mod, test, ipcpu, ippch, **kwargs):
        """
        Checks for the tname char length, max is 100 chars
        DRV_RESET_SXS::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU --> PKG_ must be less than 100char length
        IP_CPU::DRV_RESET_CXX::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU --> IP_ must be less than 100char length
        :param mod: DRV_RESET_SXN
        :param test: RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU
        :param ipcpu: ['ARR_CORE_CXX', 'FUN_CORE_CXX']
        :param ippch: ['PSCN_SCN_IXX']
        :return: None
        """
        # BUG: before : if mod not in self.sum_fc:
        if mod not in self.sum[self.gen_tlchk]:
            self.sum[self.gen_tlchk][mod] = {'e': 0, 'w': 0, 'p': 0}

        mtl = 100  # max testname char length
        if mod in ipcpu:  # IP_CPU test
            nname = 'IP_CPU::%s::%s' % (mod, test)
        elif mod in ippch:  # IP_PCH test
            nname = 'IP_PCH::%s::%s' % (mod, test)
        else:  # PKG test
            nname = '%s::%s' % (mod, test)
        ttl = len(nname)

        if ttl > mtl:
            return [{
                'type': 'non_bypass',
                'message': f'Test: {nname} length:{ttl} is over the allowed limit:{mtl} characters',
                'id': '132',
                'module': mod
            }]

        return

    def mtl_ctrlrstchk(self, modpatch, **kwargs):
        """
        Read modpatch and make sure only DRV_* modules are using *drv* plist patches
        :param modpatch: {'aaadrv': ['DRV_RESET_CXX', 'DRV_RESET_GXX'], 'scn': ['SCN_CORE', 'SCN_RING']}
        :return: None
        """
        errors = []
        for p in modpatch:
            if 'drv' not in p:
                continue
            for m in modpatch[p]:
                if m.startswith('DRV'):
                    continue
                if m not in self.sum[self.mtl_ctrlrstchk]:
                    self.sum[self.mtl_ctrlrstchk][m] = {'e': 0, 'w': 0, 'p': 0}
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Module:{m} is not from DRV but is using a drv patch:{p}!',
                    'id': '134',
                    'module': m
                })

        if len(errors) > 0:
            return errors

        return

    def mtl_bannedchk(self, stpldata, **kwargs):
        """
        Checks for banned templates, test params inside Modules/*.mtpl
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            if mod not in self.sum[self.mtl_bannedchk]:
                self.sum[self.mtl_bannedchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            for x, value in data.items():
                value = strvalue(value)
                error_message = ''
                if 'ifpm' in x:  # TODO: enable kill by Power-ON for everyone except for DRV modules ETA ww38 2022
                    error_message = f'Test:{test} uses illegal ifpm param:{x}={value}!'
                    error_num = '135'

                elif 'VDAC!' in value:
                    error_message = f'Test:{test} has illegal VDAC_UF call in param:{x}={value}!'
                    error_num = '141'
                # TODO check for illegal params inside input files

                elif 'iCShmooTest' in value:
                    error_message = f'Test:{test} uses illegal shmoo template:{value}!'
                    error_num = '136'

                elif 'iCPatternModifyTest' in value:  # TODO: enable kill by Power-ON
                    error_message = f'Test:{test} uses illegal patmod template:{value}!'
                    error_num = '146'

                elif 'iCFASTTest' in value:
                    error_message = f'Test:{test} uses illegal vmin template:{value}!'
                    error_num = '137'

                elif 'iCBinMatrix' in value:
                    error_message = f'Test:{test} uses illegal bmfc template:{value}!'
                    error_num = '140'

                if len(error_message) > 0:
                    errors.append({
                        'type': 'non_bypass',
                        'message': error_message,
                        'id': error_num,
                        'module': mod
                    })

        if len(errors) > 0:
            return errors
        return  # pragma: no cover

    def gen_badbuildchk(self, stpldata, **kwargs):
        """
        Checks for params that are NOT converted by TPIE, which errors during TP load
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')
                          ]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            if mod not in self.sum[self.gen_badbuildchk]:
                self.sum[self.gen_badbuildchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            for param, value in data.items():
                if str(value).startswith("{") and str(value).endswith("}"):
                    errors.append({
                        'type': 'trigger',
                        'message': f'Test:{test} has param:{param}={value} that was not converted by TPIE!',
                        'id': '147',
                        'module': mod
                    })

        if len(errors) > 0:
            return errors
        return

    def mtl_relaytokenchk(self, stpldata, **kwargs):
        """
        Check for instances using relay_token, sherlock will flag if relay_token is used but doesnt 'bang!'
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            if mod not in self.sum[self.mtl_relaytokenchk]:
                self.sum[self.mtl_relaytokenchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            for param, value in data.items():
                if 'relay_token' in param:
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Test:{test} illegal use of relay_token={value}',
                        'id': '150',
                        'module': mod
                    })

        if len(errors) > 0:
            return errors
        return

    def gen_reqdfileschk(self, reqdfiles, **kwargs):
        """
        This function checks for files that are required to load the TP and other DB related functionality
        :return:
        """
        errors = []
        for f in reqdfiles:
            if f not in self.sum[self.gen_reqdfileschk]:
                self.sum[self.gen_reqdfileschk][f] = {'e': 0, 'w': 0, 'p': 0}
            if os.path.isfile(f):
                continue
            else:
                errors.append({
                    'type': 'trigger',
                    'message': f'File:{f} is MISSING! HVM quality is compromised!',
                    'id': '151',
                    'module': f
                })

        if len(errors) > 0:
            return errors

        return

    def mtl_ipminlvlchk(self, stpldata, ipminflows, ipcpu, ippch, **kwargs):
        """
        This function loops in all the mtpl test instances and their levels
        If test uses IP_ scoped subflows then verify if levels used is _min_lvl_
        :return:
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :param ipminflows: ['BEGCPU', 'SCRF1', 'SGTF1', 'etc']
        :param ipcpu: {'ARR_CORE_CXX', 'FUN_CORE_CXX'}
        :param ippch: {'ARR_GT_GXX'}
        :return:
        """

        ipclvl = re.compile('ipcpu_lvl.*min_lvl')
        ipplvl = re.compile('ippch_lvl.*min_lvl')
        errors = []
        for mod, test, data, _ in stpldata:
            # TODO: temporary waivers for TPI_PRESI
            if mod.startswith('TPI_PRESI'):
                continue
            if mod not in self.sum[self.mtl_ipminlvlchk]:
                self.sum[self.mtl_ipminlvlchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            lvl = get_param(data, 'level')
            if not lvl:  # everything else that gets pass this means they have a level param
                continue

            # tests with valid levels param will proceed here
            sf = self.gen_subflow(test)

            if sf not in ipminflows:
                continue
            # process tests with valid srh/chk/ip subflows and valid levels up to this point, else throw away
            if mod in ipcpu and ipclvl.search(lvl):
                continue  # pass: ipcpu module+test using ipcpu min lvl
            elif mod in ippch and ipplvl.search(lvl):
                continue  # pass: ippch module+test using ippch min lvl
            elif mod in ipcpu and not ipclvl.search(lvl):
                tmp_pat = ipclvl.pattern.replace('.*', '_')
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} is not using *{tmp_pat}! (level={lvl})',
                    'id': '152',
                    'module': mod
                })
            elif mod in ippch and not ipplvl.search(lvl):
                tmp_pat = ipplvl.pattern.replace('.*', '_')
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} is not using *{tmp_pat}! (level={lvl})',
                    'id': '153',
                    'module': mod
                })
            else:
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} subflow={sf} & lvl={lvl} IP_ combo error',
                    'id': '154',
                    'module': mod
                })

        if len(errors) > 0:
            return errors

        return

    def mtl_flowdomainchk(self, stpldata, **kwargs):
        """
        Checks for KILL vs EDC speedflow usage, must have a valid flow_domain approved by UPSWG (see wiki UPS ITS)
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')
                          ]
        :param stpldata:
        :return:
        """

        errors = []

        fcd = {}  # flow control dictionary
        for mod, test, data, _ in stpldata:
            pt = data.get('TEMPLATE')

            if pt == 'PrimeFlowControlForkTestMethod':
                if mod not in self.sum[self.mtl_flowdomainchk]:
                    self.sum[self.mtl_flowdomainchk][mod] = {'e': 0, 'w': 0, 'p': 0}
                dn = data.get('DomainName')
                if not dn:
                    errors.append({
                        'type': 'trigger',
                        'message': 'Module uses PMBFC FlowControl without a DomainName!',
                        'id': '159',
                        'module': mod
                    })
                    continue
                if mod not in fcd:
                    fcd[mod] = {}
                if dn not in fcd[mod]:
                    fcd[mod][dn] = {'fc': 'yes', 'sf': ''}
                else:
                    fcd[mod][dn]['fc'] = 'yes'
            elif pt == 'PrimeFlowControlSetTestMethod':
                if mod not in self.sum[self.mtl_flowdomainchk]:
                    self.sum[self.mtl_flowdomainchk][mod] = {'e': 0, 'w': 0, 'p': 0}
                dnn = data.get('DomainName')
                if not dnn:
                    errors.append({
                        'type': 'non_bypass',
                        'message': 'Module uses PMBFC SetFlow without a DomainName!',
                        'id': '160',
                        'module': mod
                    })
                    continue
                if mod not in fcd:
                    fcd[mod] = {}
                if dnn not in fcd[mod]:
                    fcd[mod][dnn] = {'fc': '', 'sf': 'yes'}
                else:
                    fcd[mod][dnn]['sf'] = 'yes'

        # check if modules are using valid DomainName params
        for mod in fcd:
            for dom in fcd[mod]:
                if dom in self.cfg['fd']:
                    fc = fcd[mod][dom]['fc']
                    sf = fcd[mod][dom]['sf']
                    if 'EDC' in dom and fc and sf:  # mtl_vmintcchk will cover this
                        continue
                    elif 'EDC' in dom and fc and not sf:  # mtl_vmintcchk will cover this
                        continue
                    elif 'EDC' not in dom and fc and sf:  # mtl_vmintcchk will cover this
                        continue
                    elif 'EDC' not in dom and fc and not sf:  # mtl_vmintcchk will cover this
                        continue
                    else:  # EDC+!fc+sf or !EDC+!fc+sf, very unlikely scenario as this can only be a TPIE fail scenario
                        errors.append({
                            'type': 'non_bypass',
                            'message': f'DomainName={dom} present in SetFlow but missing in FlowControl',
                            'id': '163',
                            'module': mod
                        })
                else:
                    errors.append({
                        'type': 'trigger',
                        'message': f'Module uses an invalid DomainName={dom}',
                        'id': '164',
                        'module': mod
                    })

        if len(errors) > 0:
            return errors

        return

    def gen_duplicate_envvar(self, **kwargs):
        """
        This routine checks for duplicate env variable
        QE: 22016005321
        :return:
        """
        errors = []
        for item in self.tpobj.env.get_env_dict(stackval=True):
            self.sum[self.gen_duplicate_envvar]['env'] = {'e': 0, 'w': 0, 'p': 0}
            if f'${item}' in self.tpobj.env.get_item(item):
                continue   # ok usage of env_stacked
            errors.append({
                'type': 'trigger',
                'message': f'{item} is redefined in env. Cannot redefine.',
                'id': '206',
                'module': 'env'
            })

        if len(errors) > 0:
            return errors

        return

    def gen_supercedechk(self, **kwargs):
        """
        This routine checks for the supersedes/code directory and reads the readme.txt file and reviews if
        dlls inside the directory are documented/allowed.
        :return:
        """
        errors = []
        dlls = [Env.xpath(p) for p in glob.glob('Supersedes/code/*')]  # grep all the supercede files
        rdme = 'supersedes_code_readme.txt'
        if len(dlls) == 0:
            return

        # read the <TPL>/supersedes_code_readme.txt, exit if missing
        if not os.path.isfile(rdme):
            # add sum error here for missing supersedes_code_readme.txt
            self.sum[self.gen_supercedechk][rdme] = {'e': 0, 'w': 0, 'p': 0}
            return [{
                'type': 'non_bypass',
                'message': f'Missing Supersedes/code documentation:{rdme}',
                'id': '165',
                'module': rdme
            }]
        with open(rdme, 'r') as file:
            rd = file.read()

        for d in dlls:
            dd = d[16:]  # strip Supersedes/code/ to get exact supercede filename
            if dd in rd:  # skip if file in supersedes_code_readme.txt
                continue
            else:
                self.sum[self.gen_supercedechk][dd] = {'e': 0, 'w': 0, 'p': 0}
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Supersedes/code file={d} is not documented in {rdme}',
                    'id': '166',
                    'module': dd
                })
                # TODO: check if dd or d

        if len(errors) > 0:
            return errors

        return

    def gen_copycatchk(self, mod, test, **kwargs):
        """
        Checks if test instance name has _COPY or _COPY_
        :param stpldata:
        :return:
        """

        if '_COPY' in test or '_COPY_' in test:
            if mod not in self.sum[self.gen_copycatchk]:
                self.sum[self.gen_copycatchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            return [{
                'type': 'non_bypass',
                'message': f'Test:{test} has "_COPY", is this a copy/paste error?!',
                'id': '167',
                'module': mod
            }]

        return

    def mtl_dlvrchk(self, stpldata, cdieflows, **kwargs):
        """
        Checks for all vminTC use cases [edc vs kill, single vs multivmin, etc]
        Also checks for dlvr and powermux use cases
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :param ipcpuflows: ['BEGCPU', 'SCRF1', 'etc']
        :return:
        """
        # dlvrpins inside ipcpuflows must exist checker
        errors = []
        dlvr = '--dlvrpins IP_CPU::VCCIA_HC'
        for mod, test, data, _ in stpldata:
            pp = data.get('patlist')
            pvc = data.get('VoltageConverter')
            pr = data.get('PreInstance', data.get('preinstance', None))
            pl = data.get('PrePlist', data.get('preplist', None))
            srhdlvr = str(pvc) + str(pr) + str(pl)

            # TODO: temporary waivers for TPI_PRESI
            if mod.startswith('TPI_PRESI'):
                continue
            if mod in self.cfg['dlvrmodxcare'] and test in self.cfg['dlvrtestxcare']:
                continue

            if mod not in self.sum[self.mtl_dlvrchk]:
                self.sum[self.mtl_dlvrchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            sf = self.gen_subflow(test)
            if sf not in cdieflows:  # process only tests which reside inside ip_cpu subflows, else skip the test
                continue
            if mod.startswith('PTH_') and sf == 'BEGCPUPKG':  # ignore all PTH modules inside BEGCPUPKG subflow
                continue
            if not pp:  # process only tests with patlist in them
                continue
            if 'NONCCF' in test and 'VNNAON' in test:  # ignore case for NONCCF content which do not need dlvrpins call
                continue

            if dlvr in srhdlvr:
                continue
            else:
                errors.append({
                    'type': 'non-bypass',
                    'message': f'Test:{test} in cdie subflow={sf} is missing dlvr call!',
                    'id': '168',
                    'module': mod
                })

        if len(errors) > 0:
            return errors

        return  # pragma: no cover

    def mtl_dup_plist(self, **kwargs):
        """
        Checks for all vminTC use cases [edc vs kill, single vs multivmin, etc]
        Also checks for dlvr and powermux use cases
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :param ipcpuflows: ['BEGCPU', 'SCRF1', 'etc']
        :return:
        """
        tpobj = kwargs['tp']
#        tpobj.get_file_allplist() # contains all the plist files from the PLIST_ALL files
        errors = []

        list_plist = tpobj.get_file_allplist_real()    # contains the PLIST_ALL file names
        found = {}
        self.sum[self.mtl_dup_plist]['env'] = {'e': 0, 'w': 0, 'p': 0}
        for ff in list_plist:
            xmldata = xmlfunc.xml2dict(ff)    # Stores the contents of each PLIST_ALL file into a dictionary
            for plist in find_dot_items(xmldata, 'HdmtReferenceFile.PList.PListFile'):
                if plist not in found:
                    found[plist] = basename(ff)
                else:
                    errors.append({
                        'type': 'non-bypass',
                        'message': f"DUPLICATE: {plist}: {basename(ff)} and {found[plist]}",
                        'id': '207',
                        'module': 'env'
                    })
        if len(errors) > 0:
            return errors
        return  # pragma: no cover

    def mtl_ttrpatmapchk(self, stpldata, srhflows, **kwargs):
        """
        Checks the the pattern_name_map param has valid range of pattern substr, NUMBERS from pattern only, NO LETTERS
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'pattern_name_map': '1,2,3,4,5,6,7'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'pattern_name_map': '9,10,11,12,13,14,15'}, '')]
        :return:
        """
        errors = []
        op1 = '1,2,3,4,5,6,7'
        op2 = '9,10,11,12,13,14,15'
        for mod, test, data, _ in stpldata:
            pnm = data.get('PatternNameMap', data.get('pattern_name_map', None))
            bnm = data.get('ScoreboardBaseNumber', data.get('base_number', None))
            sf = self.gen_subflow(test)
            fss = data.get('FeatureSwitchSettings')  # has the per_pattern_printing option

            if mod not in self.sum[self.mtl_ttrpatmapchk]:
                self.sum[self.mtl_ttrpatmapchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            if sf in srhflows:
                if pnm or bnm:
                    errors.append({
                        'type': 'bypass',
                        'message': f'Test:{test} in SRH flow:{sf}, scoreboard NOT reqd',
                        'id': '169',
                        'module': mod
                    })
                    continue
            if not pnm:
                continue
            pnm = pnm.replace(' ', '')
            # everything else that comes here is not on a SRH subflow and can have base# and pattern_name_map
            if pnm == op1 or pnm == op2:  # pass, best use cases
                continue
            elif pnm.startswith('0') or pnm.startswith('8'):  # fail, letters in ctr will double count
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} uses letters for pattern_name_map={pnm}!',
                    'id': '170',
                    'module': mod
                })
            elif fss:
                if pnm and not bnm and 'per_pattern_printing' in fss:  # analog use case pass no bnm
                    continue
                elif pnm and bnm and 'per_pattern_printing' in fss:  # analog use case fail with bnm
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Test:{test} uses per_pattern_printing and base# at the same time! patmap={pnm} base#={bnm}',
                        'id': '181',
                        'module': mod
                    })
                else:  # uses fss but without perpattern printing
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Test:{test} has user_defined pattern_name_map={pnm}!',
                        'id': '182',
                        'module': mod
                    })
            else:  # !fss & catch all
                errors.append({
                    'type': 'non_bypass',  # TODO: warning, need to further splice this scenario, might need to change to bypass
                    'message': f'Test:{test} has user_defined pattern_name_map={pnm}!',
                    'id': '171',
                    'module': mod
                })

            # TODO: check that bnm+pnm < 13 digits
            # TODO: add the execution mode filter for refactor later
            # TODO: add test case when pnm has space eg 9,10,11,12,1 3,14,15 --> '1 3' should be '13'

        if len(errors) > 0:
            return errors

        return

    def gen_emptytestchk(self, stpldata, **kwargs):
        """
        Checker for tests that have NO data inside it
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            s = len(data.keys() - {'TEMPLATE'})
            if s > 0:
                continue
            # anything that goes thru here gets flagged for missing tpl param data
            if mod not in self.sum[self.gen_emptytestchk]:
                self.sum[self.gen_emptytestchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            errors.append({
                'type': 'non_bypass',
                'message': f'Test:{test} has no parameter settings!',
                'id': '172',
                'module': mod
            })

        if len(errors) > 0:
            return errors
        return

    # TODO
    def mtl_ddgshmoochk(self, stpldata, ipcpu, ippch, **kwargs):  # pragma: no cover
        """
        checker for DDGShmoo template basic/correct usages
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :param ipcpu: {'ARR_CORE_CXX', 'FUN_CORE_CXX'}
        :param ippch: {'ARR_GT_GXX'}
        :return:
        """
        # TODO: WIP pragma for now
        for mod, test, data, _ in stpldata:
            if mod not in ipcpu and mod not in ippch:  # pkg module must have soc infra
                self.sum['sum_ddgshmoochk'][mod] = {'e': 0, 'w': 0, 'p': 0}
            else:
                # module is ip_ but is calling socinfra
                self.sum['sum_ddgshmoochk'][mod] = {'e': 0, 'w': 0, 'p': 0}

        return

    def mtl_vmintcchk(self, stpldata, bomflows, cids, mtplobj, **kwargs):
        """
        Prepares mod::test data for vminTC param analysis
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            tm = data.get('TEMPLATE')
            if not tm == 'VminTC':
                continue
            spd = 0  # default set to static test
            if any(test.endswith(ff) for ff in bomflows):
                spd = 1
            # if not spd:
            #     continue

            # everything that passes here are Speedflow VminTC tests
            dd = defaultdict(str)
            dd['byp'] = mtplobj.is_bypassed(mod, test)
            dd['kil'] = data.get('_EDCKIL')  # 0
            dd['cid'] = data.get('CornerIdentifiers')  # 1
            dd['fmd'] = data.get('ForwardingMode')  # 2
            dd['fli'] = data.get('FlowIndex')  # 3
            dd['rmd'] = data.get('RecoveryMode')  # 4
            dd['rop'] = data.get('RecoveryOptions')  # 5
            dd['rti'] = data.get('RecoveryTrackingIncoming')  # 6
            dd['rto'] = data.get('RecoveryTrackingOutgoing')  # 7
            dd['vmn'] = data.get('TestMode')  # 8
            dd['sf'] = self.gen_subflow(test)  # 9
            dd['vof'] = data.get('VoltagesOffset')  # 10
            dd['lgb'] = data.get('LimitGuardband')  # 11

            if mod not in self.sum[self.mtl_vmintcchk]:
                self.sum[self.mtl_vmintcchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            # vminTC speedflow tests checks
            if spd:
                errors += self.mtl_vmintccmp(mod, test, dd) or []  # edc vs kill checker
                errors += self.mtl_vmintccidchk(mod, test, dd, cids) or []  # valid cornerid checker
                errors += self.mtl_vmintcgbchk(mod, test, dd) or []  # check for CHK instances GB params
            # vminTC static tests checks
            else:
                errors += self.mtl_vmintcstaticchk(mod, test, dd) or []

        if len(errors) > 0:
            return errors

        return

    def mtl_vmintcflicbchk(self, stpldata, bomflows, mtplobj, **kwargs):
        """
        This function checks FlowIndexCallbackName inside CHK speedflow tests in kill
        :param mod: Module Name (ARR_CORE_CXX)
        :param test: EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTC_1001
        :param dd: data = { 'kil': 'KIL', 'cid': 'CR5@F4', etc}
        :return:
        """
        errors = []

        for mod, test, data, _ in stpldata:
            tm = data.get('TEMPLATE')
            if not tm == 'VminTC':
                continue
            sf = self.gen_subflow(test)
            if sf not in cfg.chk_subflows:
                continue
            kil = data.get('_EDCKIL')
            if kil != 'KIL':
                continue

            # TODO: Add checks for static test that have this field populated and error out
            spd = 0  # default set to static test
            if any(test.endswith(ff) for ff in bomflows):
                spd = 1  # test is speedflow format
            if not spd:  # static test exit out
                continue

            fcb = data.get('FlowIndexCallbackName')
            cid = data.get('CornerIdentifiers')
            fli = data.get('FlowIndex')
            vtr = data.get('VoltageTargets')
            soc = cfg.flowdomains['soc']['domains']
            flicb = 'FlowIndexCallbackName'
            insoc = any(sd in cid for sd in soc)

            # assign the test's FlowDomain based on the VoltageTargets value
            if 'CORE' in vtr and 'CR' in cid:
                fd = 'CORE'
            elif 'ATOM' in vtr and 'AT' in cid:
                fd = 'ATOMC'
            elif 'CCF' in vtr and 'CLR' in cid:
                fd = 'RING'
            elif 'VCCGT' in vtr and 'GT' in cid:
                fd = 'GT'
            elif 'VCCSA' in vtr and insoc:
                fd = 'SOC'
            else:  # FlowDomain default setting
                fd = 'NYET'
            efcb = 'CheckFlow(%s)' % fd

            # only tests in chk subflows + speedflow format will pass thru here
            if spd and kil == 'KIL' and efcb == fcb and fli:
                continue  # pass!
            # test will go here if above is not true, eg missing CheckFlow($fd) param value
            if mod not in self.sum[self.mtl_vmintcchk]:
                self.sum[self.mtl_vmintcchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            byp = mtplobj.is_bypassed(mod, test)
            if fd == 'NYET':
                errors.append({
                    'type': 'trigger',
                    'message': f'Test:{test} Unable to determine FlowDomain with VoltageTargets={vtr} CornerID={cid}; bypass={byp}',
                    'id': '189',
                    'module': mod
                })
                continue
            if not byp:
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} missing/incorrect required data={efcb} on param={flicb}; bypass={byp}',
                    'id': '189',
                    'module': mod
                })
            else:
                errors.append({
                    'type': 'bypass',
                    'message': f'Test:{test} missing/incorrect required data={efcb} on param={flicb}; bypass={byp}',
                    'id': '189',
                    'module': mod
                })

        if len(errors) > 0:
            return errors
        return

    def mtl_vmintccidchk(self, mod, test, dd, cornerids, **kwargs):
        """
        This function will check the cornerID+tracking struction sequence correctness
        :param mod: Module Name (ARR_CORE_CXX)
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001
        :param dd: data = { 'kil': 'KIL', 'cid': 'CR5@F4', etc}
        :param cornerids: ['CR5@F1', 'CR4@F1', 'CR3@F1', ... ]
        :return:
        """
        errors = []
        if not dd['cid']:
            return
        for cid in dd['cid'].split(','):
            if cid in cornerids:  # cornerid is valid
                continue
            else:  # cornerid is not valid
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} used an invalid cornerid:{cid}',
                    'id': '183',
                    'module': mod
                })
        if len(errors) > 0:
            return errors
        return

    def mtl_vmintcgbchk(self, mod, test, dd, **kwargs):
        """
        This function will check the cornerID+tracking struction sequence correctness
        :param mod: Module Name (ARR_CORE_CXX)
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001
        :param dd: data = { 'kil': 'KIL', 'cid': 'CR5@F4', etc}
        :return:
        """

        sf = dd['sf']
        vmn = dd['vmn']
        vof = dd['vof']
        lgb = dd['lgb']
        cid = dd['cid']
        vvof = 'GBVars.VoltageOffset'
        vlgb = 'GBVars.LimitGuardband'

        if not (vmn.endswith('Vmin') and sf in cfg.chk_subflows):
            errors = []
            if sf in cfg.srh_subflows and vof:
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} dont need VoltagesOffset value:{vof} when in SRH subflow:{sf}',
                    'id': '184',
                    'module': mod
                })
            if sf in cfg.srh_subflows and lgb:
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} dont need LimitGuardband value:{lgb} when in SRH subflow:{sf}',
                    'id': '185',
                    'module': mod
                })
            if len(errors) > 0:
                return errors
            return

        # anything that runs thru here are vminTC CHK instances
        errors = []
        if vof != vvof and cid:
            errors.append({
                'type': 'non_bypass',  # either error or warning
                'message': f'Test:{test} VoltagesOffset value:{vof} not equal to {vvof}',
                'id': '186',
                'module': mod
            })
        if lgb != vlgb and cid:
            pass
            errors.append({
                'type': 'bypass',  # either error or warning
                'message': f'Test:{test} LimitGuardband value:{lgb} not equal to {vlgb}',
                'id': '187',
                'module': mod
            })

        if len(errors) > 0:
            return errors

        return

    def mtl_vmintcstaticchk(self, mod, test, dd, **kwargs):
        """
        This function checks for static vminTC tests valid settings/params use
        :param mod: Module Name (ARR_CORE_CXX)
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001
        :param dd: data = { 'kil': 'KIL', 'cid': 'CR5@F4', etc}
        :return:
        """
        fli = dd['fli']
        if fli:
            return [{
                'type': 'non_bypass',
                'message': f'Test:{test} Illegal use of FlowIndex={fli} in static vminTC',
                'id': '188',
                'module': mod
            }]
        return

    def mtl_vmintccmp(self, mod, test, dd, **kwargs):
        """
        Checks for all vminTC use cases [edc vs kill, single vs multivmin, etc], uses BM.flowindex
        VminTC Approved use cases: https://wiki.ith.intel.com/display/ITSpdxtp/MTL+VminTC+WG
        :param mod: Module Name (ARR_CORE_CXX)
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001
        :param data: data = { 'kil': 'KIL' etc}
        :return:
        """
        info = 'Bypass:%s KillEdc:%s CornerID=%s ForwardingMode=%s FlowIndex=%s ' \
               'RecMode=%s RecOptions=%s RecTrackIncoming=%s RecTrackOutgoing=%s TestMode:%s Subflow=%s' \
               % (dd['byp'], dd['kil'], dd['cid'], dd['fmd'], dd['fli'],
                  dd['rmd'], dd['rop'], dd['rti'], dd['rto'], dd['vmn'], dd['sf'])

        # early detect floating instances and return back to caller
        if not dd['kil'] and dd['byp']:
            return [{
                'type': 'bypass',  # floating bypassed test
                'message': f'Test:{test} is floating+bypassed! TestInfo={info}',
                'id': '173',
                'module': mod
            }]
        elif not dd['kil'] and not dd['byp']:
            return [{
                'type': 'bypass',  # floating unbypassed test
                'message': f'Test:{test} is floating+unbypassed! TestInfo={info}',
                'id': '174',
                'module': mod
            }]

        # Only non-floating speedflow instances pass thru here dude
        kil = '0'  # f0 0=edc 1=kil
        cid = '0'  # f1 0=false 1=true
        fmd = '0'  # f2 0=None 1=InputOutput 2=Input
        fli = '0'  # f3 0=false 1=true
        rmd = '0'  # f4 0=false 1=true+!NoRecovery 2=true+NoRecovery
        rop = '0'  # f5 0=false 1=true
        rti = '0'  # f6 0=false 1=true
        rto = '0'  # f7 0=false 1=true
        vmn = '0'  # f8 0=point 1=vmin
        sf = '0'   # f9 0:false (not in cdie flow) 1:true (in cdie flow not *CLR*) 2:true (in cdie flow in *CLR*)

        if dd['kil'] == 'KIL':
            kil = '1'
        if dd['cid']:
            cid = '1'
        if dd['fmd'] == 'InputOutput':
            fmd = '1'
        elif dd['fmd'] == 'Input':
            fmd = '2'
        if dd['fli']:
            fli = '1'
        if dd['rmd']:
            if dd['rmd'] == 'NoRecovery':
                rmd = '2'
            else:
                rmd = '1'
        if dd['rop']:
            rop = '1'
        if dd['rti']:
            rti = '1'
        if dd['rto']:
            rto = '1'
        if dd['vmn'].endswith('Vmin'):
            vmn = '1'
        if dd['sf'] in self.cfg['cdieflows'] and 'CLR' not in dd['sf']:
            sf = '1'
        elif dd['sf'] in self.cfg['cdieflows'] and 'CLR' in dd['sf']:
            sf = '2'
        vd = '%s%s%s%s%s%s%s%s%s%s' % (kil, cid, fmd, fli, rmd, rop, rti, rto, vmn, sf)  # magical compare string

        # compare current test vmintc with allowed strings
        if vd in self.cfg['validvminttstr']:
            # print(mod, test, vd, info)  # debug only
            return
        else:
            return [{
                'type': 'bypass',  # warning for now, Hyro feedback on SCN_CORE_C28
                'message': f'Test:{test} wrong speedflow setup! TestInfo=vd:{vd} {info}',
                'id': '175',
                'module': mod
            }]

        return  # pragma: no cover

    def mtl_cttrchk(self, stpldata, bomflows, **kwargs):
        """
        CTTR Checker for Mario's team
        wave1: speedflow name check
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            spd = 0  # default set to static test
            if any(test.endswith(ff) for ff in bomflows):
                spd = 1
            if not spd:
                continue

            if mod not in self.sum[self.mtl_cttrchk]:
                self.sum[self.mtl_cttrchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            t3 = self.cfg['ti_name3'].search(test)
            if not t3:
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} does not follow speedflow naming',
                    'id': '176',
                    'module': mod
                })
                continue

            sf = t3.group(5)  # subflow
            fc = t3.group(8)  # freq # corner
            ff = t3.group(9)  # freq value

            if sf not in self.cfg['sccttrflows']:
                continue  # skip tests that are not in the srh/chk subflows
            if sf.endswith(fc) and ff.isdigit() and sf in self.cfg['sccttrflows']:
                continue  # skip tests that are coded correctly

            # test runs thru here if it fails above
            if not sf.endswith(fc):
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} sf={sf} and fc={fc} do not match',
                    'id': '177',
                    'module': mod
                })
            if not ff.isdigit():
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Test:{test} Frequency={ff} should all be digits',
                    'id': '178',
                    'module': mod
                })

        if len(errors) > 0:
            return errors
        return

    def mtl_cttrbnmchk(self, stpldata, bomflows, **kwargs):
        """
        CTTR Checker for Mario's team
        wave2: Check for base number uniqueness
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        bnmctrl = {}
        errors = []
        for mod, test, data, _ in stpldata:
            if any(test.endswith(ff) for ff in bomflows):
                t3 = self.cfg['ti_name3'].search(test)  # rename the test with generic $FREQ and $FLOWINDEX
                if t3:
                    test = '%s_%s_%s_%s_%s_%s_%s_%s_$FREQ%s_$FLOWINDEX' % (t3.group(1), t3.group(2), t3.group(3),
                                                                           t3.group(4), t3.group(5), t3.group(6),
                                                                           t3.group(7), t3.group(8), t3.group(10))

            if mod not in self.sum[self.mtl_cttrchk]:
                self.sum[self.mtl_cttrchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            bnm = strvalue(data.get('ScoreboardBaseNumber', data.get('base_number', None)))
            if not bnm:
                continue  # skip test that do not have base#
            if bnm == '0':
                continue  # skip test that have base#==0

            if bnm not in bnmctrl:
                bnmctrl[bnm] = {}
            if mod not in bnmctrl[bnm]:
                bnmctrl[bnm][mod] = []
            if test not in bnmctrl[bnm][mod]:
                bnmctrl[bnm][mod].append(test)

        for bnm in bnmctrl:
            mods = list(bnmctrl[bnm].keys())
            if len(mods) > 1:
                for mod in bnmctrl[bnm]:
                    for test in bnmctrl[bnm][mod]:
                        errors.append({
                            'type': 'non_bypass',
                            'message': f'Base#:{bnm} in test:{test} is used across multiple modules:{mods}',
                            'id': '197',
                            'module': mod
                        })
            if len(bnm) != 5:
                for mod in mods:
                    for test in bnmctrl[bnm][mod]:
                        errors.append({
                            'type': 'non_bypass',
                            'message': f'Base#:{bnm} in test:{test} not eq to 5digits inside module:{mods}',  # bnm must be 5digits
                            'id': '198',
                            'module': mod
                        })

        for bnm in bnmctrl:
            for mod in bnmctrl[bnm]:
                tests = bnmctrl[bnm][mod]
                if len(tests) == 1:
                    continue  # len(tests) > 1 means many tests are using the same base number inside a module
                for test in tests:  # print warning for tests sharing base# inside a module
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Test:{test} shares Base#:{bnm} with other tests inside module',  # bnm conflicts in a modules among its tests
                        'id': '199',
                        'module': mod
                    })

        # TODO: CHK subflows, must have all vmin searches on VMIN TC, no point test
        # TODO: CHK if patlist have pgmrules on them

        if len(errors) > 0:
            return errors
        return

    def mtl_cttredgechk(self, stpldata, bomflows, **kwargs):
        """
        CTTR Checker for Mario's team
        wave3: Check for CHK subflow requirements
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            if not any(test.endswith(ff) for ff in bomflows):
                continue  # exclude static tests
            tm = data.get('TEMPLATE')
            if not tm == 'VminTC':
                continue  # process only vminTC templates
            sf = self.gen_subflow(test)
            if sf not in cfg.chk_subflows:
                continue  # process only tests inside CHK subflows

            vmn = data.get('TestMode')
            bnm = strvalue(data.get('ScoreboardBaseNumber', data.get('base_number', data.get('BaseNumbers', None))))
            etk = strvalue(data.get('ScoreboardEdgeTicks'))
            smf = strvalue(data.get('ScoreboardMaxFails'))
            kil = data.get('_EDCKIL')

            gbnm = 5
            getk = '3'
            gsmf = '20'

            if not vmn.endswith('Vmin'):
                continue  # ignore non-VMIN search mode tests
            if not kil == 'KIL':
                continue  # ignore EDC/Floating tests
            if mod not in self.sum[self.mtl_cttrchk]:
                self.sum[self.mtl_cttrchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            if bnm is None or len(bnm) != gbnm:
                errors.append({
                    'type': 'non_bypass',
                    'message': f'Base#:{bnm} in CHK test:{test} is not eq to 5digits',  # bnm in CHK subflow not eq to 5digits
                    'id': '200',
                    'module': mod
                })
            if etk != getk:
                errors.append({
                    'type': 'non_bypass',
                    'message': f'EdgeTick:{etk} in CHK test:{test} is not eq to {getk}',  # Edge ticks in CHK not eq to 3
                    'id': '201',
                    'module': mod
                })
            if smf != gsmf:
                errors.append({
                    'type': 'bypass',
                    'message': f'ScoreboardMaxFails:{smf} in CHK test:{test} is not eq to {gsmf}',  # scoreboard max fails not equql to 20
                    'id': '202',
                    'module': mod
                })

        if len(errors) > 0:
            return errors

        return

    def mtl_cttrbnmdiechk(self, stpldata, bomflows, **kwargs):
        """
        CTTR Checker for Mario's team
        wave4: Base numbers should start with die_number assignments on CHK subflows
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            bnm = data.get('ScoreboardBaseNumber', data.get('base_number', None))
            gbnm = 5
            sf = self.gen_subflow(test)
            if sf not in cfg.chk_subflows:
                continue  # process only tests inside CHK subflows
            if not bnm:
                continue
            if len(bnm) != gbnm:
                continue  # process only tests with 5digit base#

            if mod not in self.sum[self.mtl_cttrchk]:
                self.sum[self.mtl_cttrchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            if sf in cfg.cdiechk_subflows:
                if bnm.startswith(cfg.cdiebnmstart):
                    continue
                else:
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Base#:{bnm} in CDIE CHK test:{test} should start with number:{cfg.cdiebnmstart}',  # bnm in CHK test cdie subflow is wrong
                        'id': '203',
                        'module': mod
                    })
            elif sf in cfg.gdiechk_subflows:
                if bnm.startswith(cfg.gdiebnmstart):
                    continue
                else:
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Base#:{bnm} in GDIE CHK test:{test} should start with number:{cfg.gdiebnmstart}',  # bnm in CHK test gdie subflow is wrong
                        'id': '204',
                        'module': mod
                    })
            elif sf in cfg.socchk_subflows:
                if bnm.startswith(cfg.socbnmstart):
                    continue
                else:
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Base#:{bnm} in SOC CHK test:{test} should start with number:{cfg.socbnmstart}',  # bnm in CHK test soc subflow is wrong
                        'id': '205',
                        'module': mod
                    })

            # TODO: Add additional scenarios

        if len(errors) > 0:
            return errors

        return

    def mtl_reqdrvprlmvchk(self, stpldata, **kwargs):
        """
        Checks to make sure the DRV cpu/gt reset tests used in parallel MV exist in the TP
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        errors = []
        for mod, test, data, _ in stpldata:
            if mod not in cfg.prlmvdrvmods:
                continue
            if mod not in self.sum[self.mtl_reqdrvprlmvchk]:
                self.sum[self.mtl_reqdrvprlmvchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            tt = mod + '::' + test
            if tt not in cfg.prlmvreqtest:
                continue
            self.cfg['prlmvreqtest'][tt]['att'] = 'present'

        for mod in cfg.prlmvdrvmods:
            for ts in self.cfg['prlmvreqtest']:
                if mod not in ts:
                    continue
                if ts.startswith(mod) and mod in self.sum[self.mtl_reqdrvprlmvchk] and self.cfg['prlmvreqtest'][ts]['att'] == 'present':
                    self.sum[self.mtl_reqdrvprlmvchk][mod]['p'] += 1
                    continue
                else:
                    self.sum[self.mtl_reqdrvprlmvchk][mod] = {'e': 0, 'w': 0, 'p': 0}
                    errors.append({
                        'type': 'trigger',
                        'message': f'Parallel MV loop test:{ts} is missing',
                        'id': '179',
                        'module': mod
                    })

        if len(errors) > 0:
            return errors
        return

    def mtl_dedcbbchk(self, stpldata, mtplobj, **kwargs):
        """
        Greps all the iCDEDC instances in the TP and compares the input file with the barebone to see if they match
        Fail if not the same
        """
        dmd = 'TPI_DEDCHIST_YXX'
        dsp = f'{dmd}/InputFiles/DEDC_SHERLOCK_MASTERBAREBONE.txt'
        dsw = (glob.glob(f'./Modules/{dsp}') +
               glob.glob(f'./Modules/*/{dsp}'))

        errors = []
        if not dsw:  # master barebone is missing, exit out as we cannot compare anything w/out this file
            self.sum[self.mtl_dedcbbchk][dmd] = {'e': 0, 'w': 0, 'p': 0}
            return [{
                'type': 'non_bypass',
                'message': f'DEDC MasterBarebone file for comparison checks is missing: {dsp}',
                'id': '190',
                'module': dmd
            }]

        ds = dsw[0]
        with open(ds, 'r') as file:
            dsrc = file.read()
        for mod, test, data, _ in stpldata:
            tm = data.get('TEMPLATE')
            if tm != 'iCDEDCTest':
                continue
            cfg = data.get('config_file')
            byp = mtplobj.is_bypassed(mod, test)
            if cfg and exists(cfg):
                with open(cfg, 'r') as ff:
                    dmod = ff.read()
                if dsrc in dmod:  # pass scenario, exit out if this is true
                    continue
                # everything else down here mismatches the barebone
                if mod not in self.sum[self.mtl_dedcbbchk]:
                    self.sum[self.mtl_dedcbbchk][mod] = {'e': 0, 'w': 0, 'p': 0}
                if dsrc not in dmod and not byp:  # dedc test is unbypassed
                    errors.append({
                        'type': 'non_bypass',
                        'message': f'Test:{test} byp:{byp} dedc file:{cfg} does not match the dedc barebone:{ds}',
                        'id': '191',
                        'module': mod
                    })
                else:
                    errors.append({
                        'type': 'bypass',
                        'message': f'Test:{test} byp:{byp} dedc file:{cfg} does not match the dedc barebone:{ds}',
                        'id': '191',
                        'module': mod
                    })
            else:
                if mod not in self.sum[self.mtl_dedcbbchk]:
                    self.sum[self.mtl_dedcbbchk][mod] = {'e': 0, 'w': 0, 'p': 0}
                if not cfg and not byp:  # test is unbypassed, likely to fail init
                    errors.append({
                        'type': 'trigger',
                        'message': f'Test:{test} uses dedc but does not have cfg file. bypass:{byp}',
                        'id': '192',
                        'module': mod
                    })
                elif not cfg and byp:
                    errors.append({
                        'type': 'bypass',
                        'message': f'Test:{test} uses dedc but does not have cfg file. bypass:{byp}',
                        'id': '192',
                        'module': mod
                    })
                elif cfg and not exists(cfg) and not byp:
                    errors.append({
                        'type': 'trigger',
                        'message': f'Test:{test} uses dedc cfg:{cfg} but file does not exist. bypass:{byp}',
                        'id': '193',
                        'module': mod
                    })
                else:
                    errors.append({
                        'type': 'bypass',
                        'message': f'Test:{test} uses dedc cfg:{cfg} but file does not exist. bypass:{byp}',
                        'id': '193',
                        'module': mod
                    })

        if len(errors) > 0:
            return errors
        return  # pragma: no cover


class CheckersUT(Checkers):
    """
    Default Checker Product
    """

    def set_config(self):
        """ Configuration overrides for subclasses. """

        # checks to be ran
        self.chks = {
            'glob_initial': [
                # (check routine, errorout)
                (self.gen_spcharchk, True),
                (self.gen_spcharfilechk, True)
            ],
            'per_env': [
                # (check routine, errorout)
                (self.gen_pgmrulechk, True),  # pgmrule checker
                (self.gen_plistchk, True),  # patlist existence checker
                (self.gen_testplacechk, True),  # test to subflow placement checker
                (self.mtl_bannedchk, True),  # bannedchk illegal template/param checker
                (self.gen_badbuildchk, True),  # badbuildchk incorrect/bad build checker
                (self.mtl_relaytokenchk, True),  # evg relay_token usage checker
                (self.mtl_flowdomainchk, True),  # prime bmfc, flow domain checker
                (self.mtl_ipminlvlchk, False),  # ip flows min_lvl usage checker
                (self.mtl_dlvrchk, True),  # dlvr checker
                (self.mtl_ttrpatmapchk, True),  # pattern name map checker
                (self.gen_emptytestchk, True),  # prime bmfc, flow domain checker
                (self.mtl_vmintcchk, True),  # vminTC checker
                (self.mtl_vmintcflicbchk, True),  # vminTC checker
                # (self.mtl_ddgshmoochk, False),  # ddgshmoo template checker
                (self.mtl_cttrchk, False),  # cttr/pup compliance checker
                (self.mtl_cttrbnmchk, True),  # cttr/pup compliance checker
                (self.mtl_cttredgechk, True),  # cttr/pup compliance checker
                (self.mtl_cttrbnmdiechk, True),  # cttr/pup compliance checker
                (self.mtl_reqdrvprlmvchk, True),  # required drv parallel tests for MV
                (self.mtl_dedcbbchk, True),  # dedc barebone checker
                (self.gen_edcvskillchk, False),  # edc vs kill checker
                (self.mtl_dup_plist, True)  # duplicate plist checker
            ],
            'per_mtpl_mod': [
                # (check routine, errorout)
                (self.mtl_mfcchk, True)  # module field checker
            ],
            'per_stpl': [
                # (check routine, errorout)
                (self.gen_upchk, True),  # uppercase checker
                (self.gen_fcchk, True),  # testname checker
                (self.gen_sfchk, True),  # subflow checker
                (self.gen_tlchk, True),  # tname length checker
                (self.gen_copycatchk, False),  # copycat checker
                (self.mtl_socinfrachk, True),  # soc infra checker
                (self.mtl_locinfrachk, False),  # log all soc infra tests into sum_locinfrachk {} TODO: maybe not a chk
                (self.mtl_pltscpchk, False),  # PLT scope checker
                (self.cttrchk, False),  # cttr checker
                (self.gen_skuchk, True)  # sku checker (error if fail)
            ],
            'glob_final': [
                # (check routine, errorout)
                (self.mtl_ctrlrstchk, True),  # check if DRV*modules are the only ones using the drv patches
                (self.mtl_cntinfrachk, True),  # check if all soc infra tests are present
                (self.gen_reqdfileschk, True),  # check if all mandatory files are present in the TPL
                (self.gen_supercedechk, True),  # check if all Supersedes/code files are documented
                (self.gen_duplicate_envvar, True),   # check for duplicate env var
            ]

        }


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    obj = Checkers()
    obj.main()
