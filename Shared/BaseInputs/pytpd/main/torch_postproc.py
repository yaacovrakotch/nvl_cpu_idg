#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script will perform various Torch postprocess
"""
import setenv  # must be first in the imports
import glob
from os.path import exists, basename, dirname, isdir
from tp.testprogram import TestProgram, Env
from gadget.pylog import log
from gadget.files import File, check_and_del, tempname
from gadget.errors import ErrorCockpit, ErrorInput, confirm
from gadget.gizmo import Elapsed
from gadget.shell import HOSTNAME, SystemCall
from gadget.strmore import curtime
from gadget.tputil import CheckerLog, MtplBlocks
from gadget.disk import Chdir, Allfiles
from mod.prlflow import PrlFlow
from mod.envreorder import EnvReorder
from mod.moduleskip import ModuleSkip
from mod.mtplencode import MtplEncode, NPRTrigger
from mod.tppostproc import BinHack
from main.qgate import QGateExecute
from main.trace_trc_torch import TraceTrc
from main.sherlock import Checkers
from mod.cleantp_mod import CleanTP
from tp.plist import Plists
from tp.pinsoc import PinSoc
from collections import OrderedDict
import re
import os
import sys
import json
import time
import shutil
import zipfile

# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class TorchPostProc:
    """
    Torch postprocess routines
    """
    # Set by set_repo_sha()
    repo_sha = ('none', 'not_available_set_by_torch_mv_or_tpbuild_only')

    def __init__(self):
        self.env_glob = './*TP/*/EnvironmentFile*.env'
        self.envs = [x for x in glob.glob(self.env_glob) if not x.endswith('.g.env')]
        self.start_sw = Elapsed()
        self.warnings = []
        self.sherlock_report = None

    def main(self, bdeffix=True, nprtrigger=True):
        """Main Entry point"""
        if self.is_tos4():
            self.main_tos4(bdeffix, nprtrigger)
        else:
            log.info('-i- ARL postproc')
            self.main_arl(bdeffix, nprtrigger)

    @classmethod
    def is_tos4(cls):
        """Returns True if TP is tos4"""
        return bool(glob.glob('*TP/*/InputFiles/tos4_only.txt'))

    def main_tos4(self, bdeffix, nprtrigger):
        from main.torch_fixer import BdefFix
        self.startup_check()

        tpobjs = [TestProgram(x) for x in self.envs]
        # log.info('-i- START: Binhack()')
        # BinHack(self.env_glob).main()
        # BinHack(self.env_glob).mtpl()

        log.info('-i- START: UservarEdit()')
        UservarEdit(tpobjs).main()
        # if bdeffix:
        #     log.info('-i- START: BdefFix() with Share/unshare bin update')
        #     BdefFix(*tpobjs).main()

        for tpobj in tpobjs:
            env = tpobj.envfile
            log.info(f'-i- Start Process env: {env}')

            log.info(
                f'-i- START: ModuleSkip({tpobj.get_bom()})')  # This is for POR_TP module skip. MV ModuleSkip is done outside of TorchPostProc.
            tpobj.plists.error_out = False
            ModuleSkip(tpobj,
                       skipfile=True).main()  # This must be 2nd, checklock looks at env PLIST_PATH directly, and Moduleskip does not update PLIST_PATH

            # log.info(f'-i- START: SingleLevel({tpobj.get_bom()})')
            # tpobj = TestProgram(env)                  # Reload, since tpobj has changed
            # SingleLevel(tpobj).main()

            tpobj = TestProgram(env, allpats=True)  # Reload obj, since stpl and plist are modified

            # log.info(f'-i- START: MTTExpand({tpobj.get_bom()})')
            # MTTExpand(tpobj).main()

            log.info(f'-i- START: EnvEdit({tpobj.get_bom()})')
            EnvEdit(tpobj).main_tos4()  # various things here

            log.info(f'-i- START: Misc({tpobj.get_bom()})')
            Misc(tpobj).copybat()
            Misc(tpobj).tpshainfo()
            Misc(tpobj).npr_mo_pup_del()
            Misc(tpobj).unzip_PinToChain()

            log.info(f'-i- START: MtplEncode({tpobj.get_bom()})')
            me = MtplEncode(tpobj).read_meta()
            me.do_fsm()
            me.do_ppr()
            me.do_ppr_2nd()

            log.info(f'-i- START: RecipeEdit({tpobj.get_bom()})')
            RecipeEdit(tpobj).main()

            log.info(f'-i- START: EnvReorder({tpobj.get_bom()})')
            EnvReorder(tpobj).main(disp=False, update=True)

            log.info(f'-i- START: MtplNewLine({tpobj.get_bom()})')
            MtplNewLine(tpobj).main()

            # log.info(f'-i- START: PrlFlow({tpobj.get_bom()})')
            # PrlFlow(env).main()

            log.info(f'-i- START: PlistEdit({tpobj.get_bom()})')
            PlistEdit(tpobj).main()  # self.call_plistedit(tpobj)

            log.info(f'-i- START: TPName_sync')
            UservarEdit(tpobj).tpname_sync()

            self.custom_scripts(tpobj.envfile, 'buildpost_*')

            log.info(f'-i- START: NPRTrigger({tpobj.get_bom()})')
            NPRTrigger(tpobj).main(nprtrigger)

            log.info(fr'-i- Delete .git folder, so that transfer to I:\ drive is faster')
            check_and_del('.git')

            # self.call_cleantp(env)

            # ================== time to check, no more edits here
            tpobjfull = TestProgram(env, allpats=True).init()  # Reload obj after cleantp
            log.info(f'-i- START: QGate() checkers')
            QGateExecute(tpobjfull).main()  # Qgate will raise exception on error. Decision is on qgate.

            # self.call_sherlock(tpobjfull)

        # log.info(f'-i- START: call_trc()')
        # self.call_trc()

        # must be last because of message!
        # self.final_status()

    def main_arl(self, bdeffix, nprtrigger):
        from main.torch_fixer import BdefFix
        self.startup_check()

        tpobjs = [TestProgram(x) for x in self.envs]
        log.info('-i- START: Binhack()')
        BinHack(self.env_glob).main()
        BinHack(self.env_glob).mtpl()

        log.info('-i- START: UservarEdit()')
        UservarEdit(tpobjs).main()
        if bdeffix:
            log.info('-i- START: BdefFix() with Share/unshare bin update')
            BdefFix(*tpobjs).main()

        for tpobj in tpobjs:
            env = tpobj.envfile
            log.info(f'-i- Start Process env: {env}')

            log.info(
                f'-i- START: ModuleSkip({tpobj.get_bom()})')  # This is for POR_TP module skip. MV ModuleSkip is done outside of TorchPostProc.
            ModuleSkip(tpobj,
                       skipfile=True).main()  # This must be 2nd, checklock looks at env PLIST_PATH directly, and Moduleskip does not update PLIST_PATH

            log.info(f'-i- START: SingleLevel({tpobj.get_bom()})')
            tpobj = TestProgram(env)  # Reload, since tpobj has changed
            SingleLevel(tpobj).main()

            tpobj = TestProgram(env, allpats=True)  # Reload obj, since stpl and plist are modified

            log.info(f'-i- START: MTTExpand({tpobj.get_bom()})')
            MTTExpand(tpobj).main()

            log.info(f'-i- START: EnvEdit({tpobj.get_bom()})')
            EnvEdit(tpobj).main()  # various things here

            log.info(f'-i- START: Misc({tpobj.get_bom()})')
            Misc(tpobj).copybat()
            Misc(tpobj).tpshainfo()
            Misc(tpobj).npr_mo_pup_del()
            Misc(tpobj).unzip_PinToChain()

            log.info(f'-i- START: MtplEncode({tpobj.get_bom()})')
            me = MtplEncode(tpobj).read_meta()
            me.do_fsm()
            me.do_ppr()
            me.do_ppr_2nd()

            log.info(f'-i- START: RecipeEdit({tpobj.get_bom()})')
            RecipeEdit(tpobj).main()

            log.info(f'-i- START: EnvReorder({tpobj.get_bom()})')
            EnvReorder(tpobj).main(disp=False, update=True)

            log.info(f'-i- START: MtplNewLine({tpobj.get_bom()})')
            MtplNewLine(tpobj).main()

            log.info(f'-i- START: PrlFlow({tpobj.get_bom()})')
            PrlFlow(env).main()

            log.info(f'-i- START: PlistEdit({tpobj.get_bom()})')
            PlistEdit(tpobj).main()  # self.call_plistedit(tpobj)

            log.info(f'-i- START: TPName_sync')
            UservarEdit(tpobj).tpname_sync()

            self.custom_scripts(tpobj.envfile, 'buildpost_*')

            log.info(f'-i- START: NPRTrigger({tpobj.get_bom()})')
            NPRTrigger(tpobj).main(nprtrigger)

            log.info(fr'-i- Delete .git folder, so that transfer to I:\ drive is faster')
            check_and_del('.git')

            self.call_cleantp(env)

            # ================== time to check, no more edits here
            tpobjfull = TestProgram(env, allpats=True).init()  # Reload obj after cleantp
            log.info(f'-i- START: QGate() checkers')
            QGateExecute(tpobjfull).main()  # Qgate will raise exception on error. Decision is on qgate.

            self.call_sherlock(tpobjfull)

        log.info(f'-i- START: call_trc()')
        self.call_trc()

        # must be last because of message!
        self.final_status()

    def call_cleantp(self, env):
        """Call cleantp if Shared/BaseInputs/InputFiles/cleantp_enable.txt exist"""
        en_file = 'Shared/BaseInputs/InputFiles/cleantp_enable.txt'
        if exists(en_file):
            tpobj = TestProgram(env, allpats=True).init()  # Reload obj after all above postprocess
            CleanTP(tpobj).main()
            return 1
        else:
            log.info(f'-i- cleantp is skipped for this TP, {en_file} is not found.')

        return 0

    def call_sherlock(self, tpobjfull):
        """Call sherlock or not. Default is to call sherlock unless it's disabled"""
        if exists(f'{tpobjfull.envdir}/InputFiles/disable_sherlock.txt'):
            log.info('Sherlock is skipped!')
            self.sherlock_report = None
            return 1
        else:
            log.info(f'-i- START: sherlock Checkers()')
            self.sherlock_report = Checkers(
                tpobjfull).main()  # Sherlock will raise exception on error. Decision is in sherlock.
            log.info('============ END of Sherlock messages ==================')
            return 0

    @classmethod
    def custom_scripts(cls, env, which):
        """
        Call custom scripts (python, with first argument as env file)
        Script execution is sorted according to name.

        :param env: envfile
        :param which: "buildpost_*" or "buildpre_*"
        :return: None
        """
        scripts = glob.glob(f'{dirname(env)}/Scripts/{which}')
        for script in sorted(scripts):
            log.info(f'-i- START: Custom Script: {script}')
            # Must be python, takes in first argument as the env file
            code, _ = SystemCall([sys.executable, script, env], disp=True).run_outtxt()
            confirm(not code, f'{script} failed to executed.', 'See message above. Consult script owner.')

    def call_plistedit(self, tpobj):
        """Call plist edit - warning mode"""
        try:
            PlistEdit(tpobj).main()
        except ErrorInput as e:
            log.info(str(e))
            self.warnings.append(
                f'WARNING!!! Auto-plist reorder failed due to some error. Scroll up in [START: PlistEdit({tpobj.get_bom()})] to get details.')

    def call_trc(self):
        """Call TRC checks"""
        postproc_sw = str(self.start_sw)  # postprocess runtime

        trc_status = TraceTrc().main()  # Call TraceTrc

        log.info(f'-i- torch_postproc is done. Runtime: {postproc_sw}, at {HOSTNAME}, {curtime()}')
        if trc_status:
            self.warnings.append(
                'WARNING!!! TRC check was not performed. Pls run trace_trc_torch.py in windows to check!')

    def final_status(self):
        """Display the final status"""
        log.info('====================== END OF POSTPROCESS ==========================')
        log.info('')
        log.info(f"Sherlock REPORT: {self.sherlock_report}")
        if self.warnings:
            for line in self.warnings:
                log.info('')
                log.info(line)
            log.info('')
            log.info('postprocess completed, but there are Warnings. See above. Use proper judgement.')
        else:
            log.info('')
            log.info('################################')
            log.info('#    SUCCESS!                  #')
            log.info('################################')

    def startup_check(self):
        """Make sure environment is ok"""
        self.common_checks(self.envs, self.env_glob)

        confirm(not exists('TPConfig'),
                f'Current working directory is source repo (via existence of TPConfig/ folder).',
                f'torch_postproc.py is meant to be run on the exported TP.')

    @classmethod
    def common_checks(cls, envs, env_glob):
        """
        Common checks across torch_postproc.py and torch_fixer.py
        :param envs: list of env
        :param env_glob: regex string
        :return:
        """
        # correct directory?
        confirm(exists('BaseTestPlan.tpl'),
                f'BaseTestPlan.tpl is not found in current directory: {os.getcwd()}',
                'Please cd to the root directory of testprogram where BaseTestPlan.tpl is.')

        # LC_ALL found?
        confirm('LC_ALL' not in os.environ,
                'Env variable LC_ALL is found. This cause problem in reading testprogram files.',
                "Execute 'unsetenv LC_ALL' in your xterm and rerun script again. ")

        # no env found
        confirm(envs,
                f'No .env found: [{os.getcwd()}/{env_glob}]',
                'This tool only works with torch testprograms.')

    @classmethod
    def set_repo_sha(cls):
        """
        Called  by torch_mv or buildtp, given the repo
        Written by Misc().tpshainfo()
        """
        head = '.git/logs/HEAD'
        if not exists(head):
            cls.repo_sha = ('none', 'not_available_logs_head_not_found')
            return

        lines = [x for x in File(head).raw() if x.strip()]
        rsha = lines[-1].split()[1]  # 2nd element of last line

        head_file = '.git/HEAD'
        confirm(exists(head_file), f'Expecting: {head_file}', 'Contact jqdelosr right away')
        br = File(head_file).read().strip()
        if 'ref: refs/heads/' in br:
            br = br.replace('ref: refs/heads/', '')
        cls.repo_sha = (br, rsha)
        log.info(f'-i- git_ref: {br}')
        log.info(f'-i- git_sha: {rsha}')


class SingleLevel:
    """
    Make Modules to be single level (move) and
    make PlanName to match folder name (rename)
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj
        self.is_valid = exists(f'{tpobj.envdir}/InputFiles/FSM_Config.csv')
        self.all_files = []  # [{name|old|new: value}]    # 148MB worth of text based on 23 series
        self.cnt_written = 0  # count of written files
        self.oldnew = {}

    def main(self):
        """Main entry point"""
        if not self.is_valid:
            log.info('-i- SingleLevel process is skipped since InputFiles/FSM_Config.csv does not exist')
            return 1

        if exists(f'{self.tpobj.envdir}/InputFiles/no_single_level_module.settings.txt'):
            log.info('-i- SingleLevel process is skipped due to no_single_level_module.settings.txt')
            return 2

        sw = Elapsed()

        # step1 - read all files with "Modules" in it
        self.read_all()

        # step2 - do_move()
        self.do_move()

        # step3 - do_rename()
        self.do_rename()  # This is expecting single level already

        # step4 - write the mapping - so that mvtemplates know what is mapping since mvtemplates are folder name
        targetmap = f'{self.tpobj.envdir}/InputFiles/old_new_module_map.json'
        confirm(not exists(targetmap), f'Error: {targetmap} exist in repo.',
                'This file is not allowed in repo. Pls delete. This is meant to be an output file.')
        with open(targetmap, 'w') as fh:
            json.dump(self.oldnew, fh, indent=3)

        cnt = len(self.all_files)
        mb = sum(len(x['old']) for x in self.all_files) / (1024 * 1024)
        log.info(f'-i- SingleLevel: {cnt} files with "Module", {mb:.2f} MB total size, '
                 f'{self.cnt_written} files written, completed in {sw}')

    def read_all(self):
        """
        Read all files in entire TP with "Modules" in name, store in self.all_files
        This routine takes care of files with unicode
        """
        ignore_extensions = ('.pyc', '.xlsx', '.xlsm', '.dll', '.zip',  # binary
                             '.git', '.cat', '.pdb', '.exe',  # binary
                             '.old', '.bak', '.gold', '.mtproj',  # unused by tester
                             '.py'  # considered code, do not touch
                             )

        confirm(os.path.realpath('.') == os.path.realpath(self.tpobj.tpldir),
                'SingleLevel() incorrect usage',
                'cwd must be tpldir')

        for ff in sorted(Allfiles('.', skipsvn=True)):  # All files in the TP
            if ff.endswith(ignore_extensions):
                continue
            with open(ff, 'rb') as fh:  # use binary to avoid unicode issues
                text = fh.read()
            if b'Module' in text:
                textstr = File(ff).raw(islist=False)  # This will take care of unicode stuff
                self.all_files.append({'name': ff,
                                       'old': textstr,
                                       'new': textstr})

    def do_move(self):
        """move folders"""
        # {old: new}     # { 'Modules/blah/mod1': 'Modules/mod1'}
        to_move = self._get_shared_modules()

        # move
        for old, new in to_move.items():
            shutil.move(old, new)
            for item in self.all_files:
                item['name'] = item['name'].replace(old, new)

        # replace all .mtpls
        self._replace_content(to_move, 'do_move')

        return to_move

    def do_rename(self):
        """rename folders"""
        # {old: new}        # { 'Modules/mod1': 'Modules/mod2'}
        to_rename = self._get_modules_2rename()

        # rename
        for old, new in to_rename.items():
            os.rename(old, new)
            for item in self.all_files:
                item['name'] = item['name'].replace(old, new)

        # replace
        self._replace_content(to_rename, 'do_rename')

        return to_rename

    def _replace_content(self, dd, which):
        """
        Replace content in all of the affected files

        :param dd: dict {old: new}
        :param which: caller
        :return:
        """
        # Do replace of contents
        for item in self.all_files:
            for old, new in dd.items():
                if old != new and which == 'do_rename':
                    self.oldnew[basename(old)] = basename(new)

                old = f'{old}/'
                new = f'{new}/'
                item['new'] = item['new'].replace(old, new)
                item['new'] = item['new'].replace(old.replace('/', '\\'), new.replace('/', '\\'))

        # write the files
        for item in self.all_files:

            # Make sure logic is correct
            confirm(exists(item['name']),
                    f"Cockpit error: {item['name']} does not exist!",
                    f"Contact jqdelosr, this should not happen")

            if item['old'] != item['new']:
                self.cnt_written += 1
                File(item['name']).rewrite(item['new'], f"SingleLevel.mtpl.{which}()")
                item['old'] = item['new']  # This will be reused in next step

    def _get_shared_modules(self):
        """
        Identify shared modules
        :return: {old_folder: new_folder}
        """
        final = {}
        for ff in self.tpobj.get_all_mtpl_from_stpl():
            ff = ff.replace('\\', '/')
            res = re.search(r'(Modules/\w+)/\w+\.mtpl', ff)
            if not res:
                res = re.search(r'(Modules/\w+/\w+)/\w+\.mtpl', ff)
                if res:
                    final[res.group(1)] = f'Modules/{basename(res.group(1))}'

        return final

    def _get_modules_2rename(self):
        """
        Identify modules where folder != Planname
        :return: {Modules/oldname: Modules/newname}
        """
        result = {}
        for ff in self.tpobj.get_all_mtpl_from_stpl():
            if ff.endswith('.imp'):
                continue
            if basename(dirname(ff)) == 'ProgramFlowsTestPlan':
                continue
            plan = self.tpobj.get_scope(ff, 'Base')
            mod = basename(dirname(ff))
            assert basename(dirname(dirname(ff))) == 'Modules', f'Expecting Modules/<name>/*.mtpl: {ff}'
            if mod != plan:
                result[f'Modules/{mod}'] = f'Modules/{plan}'
        return result


class Misc:
    """
    Various independent stuff here
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def copybat(self):
        """Copy the batch file, since Torch does not copy .bat into the solution root"""
        target = self.tpobj.tpldir
        ctr = 0
        for bat in glob.glob(f'{dirname(self.tpobj.envfile)}/*.bat'):
            if not exists(f'{target}/{basename(bat)}'):
                File(bat).copy(target)
                ctr += 1
        return ctr

    def tpshainfo(self):
        """Create ToolsRev.txt in Reports"""
        # write the toolsrev
        sha = CheckerLog.get_tool_sha()
        content = f'pytpd rev1 commit sha id: {sha}\n'
        File(f'{self.tpobj.envdir}/Reports/ToolsRev.txt').touch(content, newfile=True, mkdir=True)
        log.info(f'-i- ToolsRev.txt is written: {sha}')

        # write the reporev
        content = f'''Repo branch ref: {TorchPostProc.repo_sha[0]}
Repo sha id: {TorchPostProc.repo_sha[1]}
'''
        File(f'{self.tpobj.envdir}/Reports/RepoRev.txt').touch(content, newfile=True, mkdir=True)

    def npr_mo_pup_del(self):
        """
        Purpose: So that MV TP will not have issue
        It is expected at TPI will put solution in Shared/BaseInputs/Supersedes/MO_PUP/* during base release
        For POR_TP build, delete files in Shared/BaseInputs/Supersedes/MO_PUP/*, just keep README.
        Do nothing for ENG_TP build.

        :return: unittest code
        """
        pupdir = 'Shared/BaseInputs/Supersedes/MO_PUP'
        if self.tpobj.is_eng_tp():
            return 1  # Do nothing
        if not isdir(pupdir):
            return 2  # Directory not found

        for ff in os.listdir(pupdir):
            if ff == 'readme.txt':  # skip this file
                continue
            target = f'{pupdir}/{ff}'
            log.info(f'-i- npr_mo_pup_del(), Deleting: {target}')
            check_and_del(target)  # use rmtree if dir, unlink if file
        return 3

    def unzip_PinToChain(self):
        """
        Purpose: PinToChainTable.xml is generated by Torch but is inside .zip file.
        PinToChainTable.xml must be in Reports for template to use
        """
        zfile = f'{self.tpobj.envdir}/Reports/LTL_Files.zip'
        if not exists(zfile):
            log.info('-i- PinToChainTable: LTL_Files.zip does not exist in Reports/')
            return
        with zipfile.ZipFile(zfile, 'r') as zh:
            zh.extract('PinToChainTable.xml', dirname(zfile))
        log.info(f'-i- PinToChainTable.xml is extracted in {dirname(zfile)}')

        self.add_ip_PinToChain(f'{dirname(zfile)}/PinToChainTable.xml')

    def add_ip_PinToChain(self, p2c):
        """
        Add IP in PinToChainTable.xml since Torch generated .xml will fail init. It needs IP.
        :param p2c: PinToChainTable.xml file
        """
        pinfile = 'Shared/BaseInputs/PinDefinitions.pin'
        if not exists(pinfile):
            log.info(f'-i- add_ip_PinToChain skip: {pinfile} does not exist')
            return 1

        # Create the pin2ip
        ps = PinSoc(None)
        ps.set_data(pinfile)
        resources = ps.get_resources()
        pin2ip = {}  # {pin: ip}, only for pins needing it
        for res in resources:
            if ':' in res:
                ip = res.split(':')[0]
                for pin in resources[res]:
                    pin2ip[pin] = ip

        # read original file and reprocess it
        robj = re.compile('name=\"([^\"]+)')
        lines = File(p2c).raw()
        final = []
        for line in lines:
            res = robj.search(line)
            if res:
                pin = res.group(1)
                if pin in pin2ip:
                    line = line.replace(pin, f'{pin2ip[pin]}::{pin}')
            final.append(line)

        File(p2c).rewrite(''.join(final), 'add_ip_PinToChain()')


class MtplNewLine:
    """
    Edit mtpl because of new line character Torch bug (temporary!)
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def main(self):
        for ff in self.tpobj.get_all_mtpl_from_stpl():
            self.process(ff)

    def process(self, ff):
        """Process one mtpl file"""
        final = File(ff).raw()
        start = False
        for idx in range(len(final)):
            line = final[idx]
            if (not start) and line.strip().startswith(('Test ', 'CSharpTest ')):
                start = True
            if start and line.strip().endswith(('(', ',')):
                final[idx] = f'%s  %s\n' % (line.rstrip(), '\\')

        File(ff).rewrite(''.join(final), 'MtplNewLine.process()')


class PlistEdit:
    """
    PLIST_ALL edits:
    1. main(): Update with correct dependency
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def main(self):
        """Edit the plist all so order is correct based on dependency"""
        sw = Elapsed()

        # get the sorted plist dependency
        dependents = self.tpobj.plists.get_plist_dependent()  # {plist: set_of_plist_dependent}
        dep_sortable = MtplBlocks.dependent_values(dependents)  # {plist: number}
        psorted = sorted(dep_sortable, key=lambda x: (dep_sortable[x], x))  # [plist_sorted]

        for plist in self.tpobj.plists.get_all_plists():
            self.process(plist, psorted)

        log.info(f'-i- PlistEdit() is complete in {sw}')
        return psorted  # unittest use

    def process(self, plist, psorted):
        """
        Update plist with correct dependency
        :param plist: input plist file abspath
        :param psorted: [plist_sorted]
        :return:
        """
        # read the file
        robj = re.compile(r'^\s*<PListFile\s+name="([^\"]+)')
        flines = File(plist).raw()
        header = []
        plists = []
        footer = []
        for line in flines:
            res = robj.search(line)
            if res:
                confirm(res.group(1) not in plists,
                        # Need this check since final confirm() will fail if there are duplicate. Mic feedback.
                        f'[{res.group(1)}] is defined twice in {basename(plist)}',
                        f'Define .plist once only.')
                plists.append(res.group(1))
                continue

            if plists:
                footer.append(line)
            else:
                header.append(line)

        # update
        newlist = []
        found = set()
        for item in psorted:
            if item in plists:
                newlist.append(f'    <PListFile name="{item}" />\n')
                found.add(item)

        # add missing items at end
        for item in plists:
            if item not in found:
                newlist.append(f'    <PListFile name="{item}" />\n')

        confirm(len(newlist) == len(plists),
                f'Cockpit Error! mismatch in length: {len(newlist)} != {len(plists)}',
                f'Contact jqdelosr for this safety check. This indicates incorrect algo/logic.')

        # rewrite
        File(plist).rewrite(''.join(header + newlist + footer), 'PlistEdit.main()')


class RecipeEdit:
    """
    Various Recipe edit routines
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def main(self):
        r"""
        Edit the Recipe for correlation runs
        a) Production TP  (numeric 4th char) - no edit needed
        b) Correlation TP (letter 4th char)  - edit the recipe file
        Edit astra_hdmx_vc should point to I:\tpvalidation instead of I:\hdmxpats
        """
        if not exists(f'{self.tpobj.tpldir}/astra/astra_hdmx_vc'):
            log.info(f'-i- Skipping RecipeEdit() since astra/ folder does not exist')
            return 1

        # find the file to modify
        wildcard = f'{self.tpobj.tpldir}/astra/astra_hdmx_vc/recipe/*/tp_recipe/*TPL.xml'
        tfile = glob.glob(wildcard)
        if not len(tfile) == 1:
            log.info(f'RecipeEdit(): {len(tfile)} TP recipe files are found: {wildcard}.')

        # Is this TP correlation?
        letter = self.get_letter_tpname(tfile[0])
        if letter.isnumeric():  # numeric - production, letter - correlation
            log.info(f'-i- Skipping RecipeEdit() since TP is production')
            return 2

        # modify it (line#8)
        for fname in tfile:
            fnew = File(fname)
            flines = fnew.raw()
            final = self.update(flines)
            fnew.rewrite(''.join(final), 'RecipeEdit()')

        # more edit routines
        self.edit_sc_recipe()

    def edit_sc_recipe(self):
        r"""
        Temporary until spark+torch is fixed.
        Edit astra\astra_hdmx_vc\recipe\MTLXXXXXXX19K0BSXXX\sc_recipe/MTL* files
        Update two lines, from prod to engr
        """
        prod_letter = self.tpobj.get_name()[:3].upper()
        wildcard = f'{self.tpobj.tpldir}/astra/astra_hdmx_vc/recipe/*/sc_recipe/{prod_letter}*'
        for ff in glob.glob(wildcard):
            text = File(ff).read()
            text = text.replace('\\prod\\', '\\engr\\')
            File(ff).rewrite(text, 'RecipeEdit.edit_sc_recipe()')

    def get_letter_tpname(self, fname):
        """
        Get the tp letter name
        :param fname: input file
        :return:
        """
        robj = re.compile(r'hdmxprogs\S\w+\S..............(.)')
        for line in File(fname).raw():
            res = robj.search(line)
            if res:
                return res.group(1)
        raise ErrorInput(f'Cannot derive testprogramname from {fname}. Is regex correct on get_letter_tpname()?')

    def update(self, flines):
        """
        Iterator: Return new list of lines
        :param flines: input lines
        :return: list lines
        """
        for line in flines:
            if 'TP_BASE' in line:
                yield line.replace('I:\\hdmxprogs\\', 'I:\\tpvalidation\\hdmxprogs\\')
            else:
                yield line


class CopyTPConfig:
    """
    Copy the TPConfig
    Purpose: ENG_TP TPConfig is copied once during "blankie debug". This routine will make sure that it
    is always up to date with POR_TP so that recipes are correct.
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def main(self):
        """Main entry point"""
        if not self.tpobj.is_eng_tp():
            log.info(f'-i- Skipping CopyTPConfig. Env file is not ENG_TP: {self.tpobj.envfile}')
            return 1

        bom = basename(dirname(self.tpobj.envfile)).replace('_DEBUG', '')
        src_tpconfig = f'{self.tpobj.tpldir}/Modules/TPI_BASE_XXX/InputFiles/{bom}.tpconfig'
        assert exists(src_tpconfig) == 1, f'Expecting {src_tpconfig} to exist'

        # copy the tpconfig file to ENG_TP
        fnew = File(src_tpconfig).copy(dirname(self.tpobj.envfile))
        result = glob.glob(f'{dirname(self.tpobj.envfile)}/*.tpconfig')
        assert len(result) == 1, f'Expecting one .tpconfig only: Found: {result}'

        # read & edit
        stpls = glob.glob(f'{dirname(self.tpobj.envfile)}/*.stpl')
        stpl = basename(self.get_stpl(stpls))
        flines = fnew.raw()
        final = self.update(flines, stpl)
        fnew.rewrite(''.join(final), 'CopyTPConfig()')

    def get_stpl(self, stpls):
        """
        Identify correct stpl
        :param stpls: list of stpls
        :return: stpl file to use
        """
        assert len(stpls) > 0, f'No stpl found in {dirname(self.tpobj.envfile)}'
        if len(stpls) == 1:
            return stpls[0]
        result_g = [x for x in stpls if '_g.stpl' in basename(x)]
        assert len(result_g) == 1, f'Expecting one *_g.stpl in: {stpls}'
        return result_g[0]

    def update(self, flines, stpl):
        """
        Return new list of lines
        :param flines: input lines
        :param stpl: replacement stpl
        :return: list lines
        """
        final = []
        robj = re.compile(r'SubTestPlan.*\.stpl')
        for line in flines:
            res = robj.search(line)
            if res:
                line = robj.sub(stpl, line)
            final.append(line)
        return final


class UservarEdit:
    """
    Various Uservar Edits for Torch
    """

    def __init__(self, tpobjs):
        self.tpobjs = tpobjs

    def main(self):
        """Main Entry point of uservar edits"""
        self.ifengtp()

    def ifengtp(self):
        """Modify variable if this tp is ENG_TP"""
        # Do nothing if POR_TP
        for tpobj in self.tpobjs:
            if not tpobj.is_eng_tp():
                log.info('-i- ifengtp() is skipped due to POR_TP')
                return 0

        ctr = 0
        keyword = 'yes_mv_tp_value => False'
        for usrv in glob.glob(f'{tpobj.shareddir}/*/Use*.usrv'):
            ctr += 1
            text = ''.join(File(usrv).raw())
            if keyword in text:
                ctr += 100  # indicator of modification
                text = text.replace(keyword, keyword.replace('False', 'True'))
                File(usrv).rewrite(text, f'UservarEdit().ifengtp')

        log.info(f'-i- ifengtp() done, count={ctr}')
        return ctr

    def tpname_sync(self):
        """
        Modify Shared/BaseInputs/UservarDefinitions.usrv TPName value to match package shared.
        Why? Because spark does not work if TPName1 has different value between baseinputs and packageshared.
        We have to keep PUP tooling happy as well (thus, we can't change TPName1 to TPName2 for one of them)
        BaseInput is only used during recipe creation. This routine must be called after export when recipe
        generation is done already.
        """
        # Assign the usrv. Proceed only if these files exist
        usrv_base = 'Shared/BaseInputs/UservarDefinitions.usrv'
        usrv_package = 'Shared/Package_Shared/UservarDefinitions.usrv'
        if not (exists(usrv_base) and exists(usrv_package)):
            log.info(f'Either {usrv_base} or {usrv_package} not exist. tpname_sync() is ignored.')
            return

        name = self.get_tpname()
        data = File(usrv_base).raw()
        final = []
        robj = re.compile(r'(\sTPName1\s*=\s*.*")(\w+)')
        found = False
        for line in data:
            if robj.search(line):
                final.append(robj.sub(r'\1' + name, line))
                found = True
            else:
                final.append(line)
        confirm(found, f'TPName1 is not found in {usrv_base}', 'Pls check, this is expected')

        File(usrv_base).rewrite(''.join(final), f'UservarEdit().tpname_sync')

    @classmethod
    def get_tpname(cls, var='TPName1'):
        """Return simple value of var from .usrv"""
        usrv = 'Shared/Package_Shared/UservarDefinitions.usrv'  # Cannot use tpobj.usrv since value will be datalog value, not folder
        confirm(exists(usrv), f'Expecting {usrv}', f'Pls check: cwd: {os.getcwd()}')
        alltext = File(usrv).read()

        res = re.search(fr'{var}\s*=\s*.*"(\w+)', alltext)
        confirm(res,
                f'{var} = "<value>" is not found in {usrv}',
                'Check usrv file. This is required for PUP.')
        return res.group(1)


class EnvEdit:
    """
    Various env edits for Torch
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj
        self.localtp = TestProgram(tpobj.envfile)  # This localtp has modified env dictionary
        self.localtp.env.set_env()
        self._map_cm = {}  # See _is_valid_patmodify_path

    def main(self):
        """
        Main entry point of env edits
        """
        # Remove these auto variables and insert directly in main variable.
        # Why? we see weird init issues when this exist during VPO runs:
        # After full flush of SysC and testers, still fails as follows:
        #   Error in instance=[TPI_BASEPRIM_XXX::CTRL_X_PRIMEINIT_K_INIT_X_X_X_X_X]: |
        #   Prime.Base.Exceptions.FatalException occured :
        #   Error in section 'module'=[MaaaCdrv] does not exist in patConfigService.
        self.remove_auto('TORCH_AUTO_TPL_INPUT_FILES')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_H68G2')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_P68G2')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_P28G2')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_P28G1')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_M28G1')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_S68G1')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_ARLS8161_LGA')
        self.remove_auto('TORCH_AUTO_ALEPH_FILES_CLASS_ARLS8161_BGA')

        # Need this removed due to subroutine reorder
        self.remove_auto('TORCH_AUTO_PAT_PATH')

        # MV vs POR_TP difference
        self.delete_var('P3_PRODUCT_FOLDERS', 'POR_TP')

        # Remove sort and slim paths - For faster loadtime (22min to 15 mins)
        self.remove_sort_slim()

        # Remove the module aleph files. Why? Because of Torch ticket 60754
        self.remove_aleph()

        # PUP related
        self.pup_module_input()
        self.pup_ulat_tpname()

        # Sophia pobj soc sha
        self.pobj_soc_sha()

        # Lastly, replace the file
        File(self.localtp.envfile).rewrite(self.rebuild(), f'EnvEdit().torch_auto()')

    def main_tos4(self):
        """
        Main entry point of env edits
        """
        # Need this removed due to subroutine reorder
        self.remove_auto('TORCH_AUTO_PAT_PATH')

        # MV vs POR_TP difference
        self.delete_var('P3_PRODUCT_FOLDERS', 'POR_TP')

        # Remove sort and slim paths - For faster loadtime (22min to 15 mins)
        self.remove_sort_slim()

        # Remove the module aleph files. Why? Because of Torch ticket 60754
        # self.remove_aleph()      # not needed, Chen's feedback 7/17/24

        # PUP related
        self.pup_module_input()
        self.pup_ulat_tpname()

        # Sophia pobj soc sha
        self.pobj_soc_sha()

        # Lastly, replace the file
        File(self.localtp.envfile).rewrite(self.rebuild(), f'EnvEdit().torch_auto()')

    def rebuild(self):
        """
        Yet another exception: NPR_FOLDER_PATH must be on the same line
        """
        return ''.join(self.localtp.env.rebuild())

    def pobj_soc_sha(self):
        """
        Remove all soc sha in HDST_PAT_PATH
        1. The soc sha is in env.env
        2. labs will copy the .pobj into local area
        3. TP env does not need the soc sha

        Original Sophia's algo
        1. copy to a new env file .pobjcache
        2. remove the path with sha (production)
        3. get the sha of .soc
        4. remove lines that does not match sha (.pobjcache)

        :return: None
        """
        env = self.localtp.env
        allvars = env.get_env_dict()
        key = 'HDST_PAT_PATH'
        confirm(key in allvars, f'Expecting {key} in .env file', 'Pls check env file')

        val = env.get_item(key, islist=True)
        robj = re.compile(r'\b[0-9a-f]{12}$')
        result = []
        for item in val:
            if robj.search(item):
                continue  # skip
            result.append(item)
        env.set_item(key, result)  # set it

    def pup_ulat_tpname(self):
        """
        So that TPI will not manually edit env
        """
        env = self.localtp.env
        allvars = env.get_env_dict()
        if 'PUP_PATTERNS_DIR' not in allvars:
            log.info('-i- PUP_PATTERNS_DIR is not found in env. skipping pup_ULAT_PUP_TPNAME_REV()')
            return
        confirm('NPR_FOLDER_PATH' in allvars,
                'Expecting NPR_FOLDER_PATH since PUP_PATTERNS_DIR exist.',
                'Check env file')
        # grab TPName1
        tpn = UservarEdit.get_tpname()
        tpname = f'{tpn[:3]}XX{tpn[7:15]}'  # based on 'MTL NPR' wiki, dated 06/26/23
        tpname = self._pup_engg_fulltp(tpname)

        if 'HASH_PATH' not in allvars:
            for key in 'PUP_PATTERNS_DIR NPR_FOLDER_PATH'.split():
                env.set_item(key, allvars[key].replace(f'<ULAT_PUP_TPNAME_REV>', tpname))
        else:
            for key in 'PUP_PATTERNS_DIR NPR_FOLDER_PATH HASH_PATH'.split():
                env.set_item(key, allvars[key].replace(f'<ULAT_PUP_TPNAME_REV>', tpname))

    def _pup_engg_fulltp(self, tpname, path='I:/ulat/pup/release/mtl'):
        """
        If tpname ends with "Z", check ulat folder for latest TP and use that instead.
        Reason, for example:
        main-line TPNAME is 38C0Z
        mon: 38C0A is released
        tue: 38C0B is released
        wed: 38C0C is released
        If MO creates full TP, the built tp is still 38C0Z since that is the main line value.
        init will fail since 80C0Z solution will be used. We want solution to be 38C0C (latast).
        This function will return 38C0C is tpname ends with 'Z'
        :return: New tpname
        """
        if not tpname.endswith('Z'):
            return tpname

        # 01/08/24: Both full TP engg and MV TP, so that TPI doesn't need to push *0Z version anymore
        #           Commenting below for MV TP, since full TP engg is already using ulat latest TP
        # if self.tpobj.get_buildtype() == 'ENG_TP':
        #     return tpname

        # TODO: add a config in InputFiles, so 'path' is configurable
        tpath = f'{Env.xpath(path)}/{tpname[:-1]}?'
        allnames = glob.glob(tpath)
        if len(allnames) == 0:
            log.info(f'-i- _pup_engg_fulltp: None found: {tpath}')
            return tpname

        basenameonly = sorted(basename(x) for x in allnames)
        prefinal = [x for x in basenameonly if not x.endswith('Z')]
        if not prefinal:
            log.info(f'-i- _pup_engg_fulltp: None found, Z only')
            return tpname
        final = prefinal[-1]

        log.info(f'-i- _pup_engg_fulltp: replace {tpname} to {final}')
        return final

    def pup_module_input(self):
        """
        https://wiki.ith.intel.com/display/ITSpdxtp/MTL+NPR
        This is needed because of a TOS bug
        """
        # get the value of PUP_MODULE_INPUTS
        allvars = self.localtp.env.get_env_dict()
        if 'PUP_MODULE_INPUTS' not in allvars:
            log.info('-i- PUP_MODULE_INPUTS is not found in env. skipping pup_module_input()')
            return

        # replace it in TPI_PUP_XXX module
        pup_path = 'Modules/TPI_PUP_XXX/*.mtpl'
        mtpls = glob.glob(pup_path)
        confirm(mtpls, f'Expecting mtpl in {pup_path}', 'Pls check.')
        for mtpl in mtpls:
            found = False
            lines = File(mtpl).raw()
            for idx in range(len(lines)):
                if '~PUP_MODULE_INPUTS' in lines[idx]:
                    found = True
                    lines[idx] = lines[idx].replace('~PUP_MODULE_INPUTS', allvars['PUP_MODULE_INPUTS'])

            if found:
                File(mtpl).rewrite(''.join(lines), 'pup_module_input()')
            else:
                log.info(f'-i- {mtpl} does not have ~PUP_MODULE_INPUTS. Skipping.')

    def delete_var(self, name, tptype):
        """
        Delete the variable name if tptype is true.
        Note: Code can remove, it cannot uncomment

        :param name: name of variable
        :param tptype: env type
        :return: None
        """
        actualtype = self.tpobj.get_buildtype()
        if actualtype != tptype:
            log.info(f'-i- delete_var({name}) is skipped because env is [{actualtype}]')
            return 1

        env = self.localtp.env
        allvars = env.get_env_dict()
        if name not in allvars:
            log.info(f'-i- delete_var({name}) is skipped because it does not exist in env')
            return 2

        env.del_item(name)
        return 3

    def remove_aleph(self):
        """Remove unneeded aleph lines"""
        log.info('-i- Starting Env Edit for unneeded aleph lines...')
        mods = set(self.tpobj.get_module_folder_names())  # Use original tp object
        robj = re.compile(r'Modules.*/(\w+)/\w+Files')  # works with shared modules
        robj_pp = re.compile(r'\$(\w+_PATMODIFY_PATH)')
        env = self.localtp.env
        allvars = env.get_env_dict()
        for key in allvars:
            if not key.startswith('ALEPH_FILES'):
                continue
            result = []
            for item in env.get_item(key, islist=True):
                # Standard /Modules/ line
                res = robj.search(item.replace('\\', '/'))
                if res:
                    mod = res.group(1)
                    if mod not in mods:
                        print(f'-i- Env: Removing [{item}] in {key}')
                        continue  # skip this line!

                # PATMODIFY_PATH
                res = robj_pp.search(item)
                if res:
                    if not self._is_valid_patmodify_path(env.get_item(res.group(1)), mods):
                        print(f'-i- Env: Removing [{item}] in {key}')
                        continue  # skip this line!

                result.append(item)

            env.set_item(key, result)  # overwrite

    def _is_valid_patmodify_path(self, ppval, mods):
        """
        Returns True if patmodify_path is valid for this tp

        :param ppvar: <VAR>_PATMODIFY_PATH
        :param mods: set of modules
        :return: bool
        """
        # 1. read mconfig, create _map_cm = {ci_plist_module: set_of_module} map
        if not self._map_cm:
            self._map_cm = self.tpobj.plists.get_cimod2mod_map()

        # get ci_plist_module in PATMODIFY_PATH value, if all set_of_module is non-existent in mods, then remove
        ci = Plists.get_modname(ppval)
        ci_all = self._map_cm.get(ci, set())
        return bool(len(ci_all - mods) != len(ci_all))  # not equal means this PATMODIFY is used.

    def remove_sort_slim(self):
        """Remove sort paths and slim paths"""
        env = self.localtp.env
        allvars = env.get_env_dict()
        for key in allvars:
            # remove slim
            if key.endswith('_PLIST_PATH'):
                val = env.get_item(key, islist=True)
                result = []
                for item in val:
                    if not item.endswith('slim'):
                        result.append(item)
                env.set_item(key, result)  # set it

            # remove sort
            if key.endswith(('_PLIST_PATH', '_PAT_PATH')):
                val = env.get_item(key, islist=True)
                result = []
                for item in val:
                    if not item.startswith('I:\\program\\'):
                        result.append(item)
                env.set_item(key, result)  # overwrite

    def remove_auto(self, var):
        """
        Remove var in the env file and replace the caller

        :param flines:
        :param var:
        :return: new flines
        """
        env = self.localtp.env
        allvars = env.get_env_dict()
        if var not in allvars:
            log.info(f'-w- Env does not have [{var}]. Skipping removal of this')
            return

        for key in allvars:
            value = env.get_item(key, islist=True)
            result = []
            updated = False
            for item in value:
                if item == f'${var}':
                    result.extend(env.get_item(var, islist=True))
                    updated = True
                else:
                    result.append(item)
            if updated:
                env.set_item(key, result)

        env.del_item(var)


class MTTExpand:
    """
    MTT Expand replace
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj
        self.nflows = None
        self.map_remove = self.set_map_remove()
        self.mapping = self.set_mapping()

    def set_mapping(self):
        """
        Set the mapping structure - configurable per TP

        :return: set of (module, domain)
        """
        # default - initial for backwards compatibility before looking up TP area
        # NOTE: Do not edit mapping below starting 10/1! Instead ask module owner to put
        #       /intel/tpvalidation/jqdelosr/temp/mtt_mapping.json in their branch and make modifications
        #       there. The json there is equivalent to below mapping
        mapping = [('FUN_ATOM_CXX', {'ATOMC': '!_VCC',
                                     'RING': '_VCC'}),
                   ('SCN_CCF_C68', {'RING': '!_EDC$',
                                    'RING_EDC': '_EDC$'}),  # RING_EDC is unused, so test_* will pass
                   ('SCN_CCF_C28', {'RING': '!_EDC$',
                                    'RING_EDC': '_EDC$'}),  # RING_EDC is unused, so test_* will pass
                   # ('SCN_SOC_SXXK', {'SOC': '!_EDC$',
                   #                   'SOC_EDC': '_EDC$'}),
                   # ('SCN_ATOM_CXX', {'ATOMC': '!_EDC$',
                   #                   'ATOMC_EDC': '_EDC$'}),
                   # ('SCN_GT_GXX', {'GT': '.*'}
                   #                 'GT_EDC': '_EDC$'}),
                   ('SCN_CORE_C68', {'CORE': '!_EDC$',
                                     'CORE_EDC': '_EDC$'}),
                   ('SCN_CORE_C28', {'CORE': '!_EDC$',
                                     'CORE_EDC': '_EDC$'}),
                   ('ARR_ATOM_SXN', {'SOC_EDC': '.*'}),
                   ('ARR_ATOM_L2SXN', {'SOC_EDC': '.*'}),
                   ('ARR_MBIST_PMSXM', {'SOC': '!_EDC$',
                                        'SOC_EDC': '_EDC$'}),
                   ('PTH_DLVR_CXX', {'ATOMC': '_ATOMCORES_',
                                     'CORE': '_CORES_'}),
                   ('_SX', {'SOC': '.*'}),
                   ('_L2SX', {'SOC': '.*'}),
                   ('_ATOM_', {'ATOMC': '.*'}),
                   ('_CCF_', {'RING': '.*'}),
                   ('_CORE_', {'CORE': '.*'}),
                   ('_GT_', {'GT': '.*'}),
                   ]

        cfgfile = 'Shared/BaseInputs/mtt_mapping.json'
        if exists(cfgfile):
            with open(cfgfile) as fh:
                mapping = json.load(fh)

        return OrderedDict(mapping)

    def main(self):
        """Main Entry point"""
        if exists(f'{self.tpobj.envdir}/InputFiles/no_mtt_expand.settings.txt'):
            return 2

        # iterate to all mtpl
        log.info("-i- Running MTTExpand()")
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            self._main_one_mtpl(mtpl)

    def _main_one_mtpl(self, mtpl):
        """Process one mtpl"""
        # log.info(f'-i- Processing {basename(dirname(mtpl))}/{basename(mtpl)} ...')
        domains = self.get_domains(mtpl)
        if domains:
            # read the file
            flines = File(mtpl).raw()

            self.edc_domains(flines, domains)

            # add the blocks
            flines, added = self.add_blocks(flines, domains, mtpl)
            flines = self.replace_dutflowitems(flines, added, basename(dirname(mtpl)), domains)
            flines = list(self.remove_evg_blocks(flines))
            flines = self.add_import_line(flines, basename(mtpl))
            flines = self.replace_return_1_only(flines)

            # replace the file
            File(mtpl).rewrite(''.join(flines), f'MTTExpand().main()')

    @classmethod
    def replace_return_1_only(cls, flines):
        """
        Replace all "DUTFlowItem FlowControl_" and "DUTFlowItem SetFlowInfo_" to Return 1
        :param flines:
        :return:
        """
        result = []
        start = 0
        for line in flines:
            if line.strip().startswith(('DUTFlowItem FlowControl_', 'DUTFlowItem SetFlowInfo_')):
                start = 1
            if start == 1 and line.strip().startswith('Result -2'):
                start = 2
            if start == 2 and line.strip().startswith('Return -2'):
                result.append(line.replace('-2', '-1'))
                continue
            if line.strip() == '}':
                start = 0

            result.append(line)
        return result

    @classmethod
    def remove_evg_blocks(cls, flines):
        """
        Iterator: remove Test iCBinMatrixFlowControlTest blocks
        :param flines: list of lines
        :return: list of lines
        """
        start = False
        for line in flines:
            if line.strip().startswith('Test iCBinMatrixFlowControlTest '):
                start = True
                continue
            if start and line.strip().startswith('}'):
                start = False
                continue
            if start:
                continue
            yield line

    @classmethod
    def add_import_line(cls, flines, which_mtpl):
        """
        Add the PrimeControl Import line

        :param flines: list of lines
        :param which_mtpl: mtpl filename for info only
        :return: list of lines
        """
        robj1 = re.compile('^Import PrimeFlowControlForkTestMethod.xml', re.MULTILINE)
        robj2 = re.compile('^Import PrimeFlowControlSetTestMethod.xml', re.MULTILINE)
        res1 = robj1.findall(''.join(flines))
        res2 = robj2.findall(''.join(flines))

        if res1 and res2:
            return flines  # no change

        # Add the import line
        log.info(f"-i- MttExpand.add_import_line({which_mtpl})")
        result = []
        start = True
        for line in flines:
            if line.startswith('Import ') and start:
                result.append('Import PrimeFlowControlForkTestMethod.xml;\n')
                result.append('Import PrimeFlowControlSetTestMethod.xml;\n')
                start = False
            if line.startswith(
                    ('Import PrimeFlowControlForkTestMethod.xml', 'Import PrimeFlowControlSetTestMethod.xml')):
                continue  # no duplicate
            result.append(line)

        return result

    def set_nflows(self, flines, mtpl):
        """
        Update self.nflows if not set
        :param flines: which lines
        :param mtpl: file
        :return:
        """
        if self.nflows:
            return

        result = set()
        robj = re.compile(r'\bSetFlowInfo\w+Flow(\d)')
        for line in flines:
            res = robj.search(line)
            if res:
                result.add(res.group(1))

        confirm(result, f'Cannot find any SetFlowInfo* items in {mtpl}', 'Contact jqdelosr')
        self.nflows = sorted(result)

    def set_map_remove(self):
        """
        Set the map_remove structure - configurable per TP

        :return: set of (module, domain)
        """
        # default mapping - initial for backwards compatibility before looking up TP area
        data = {('FUN_ATOM_CXX', 'RING'),
                ('SCN_CCF_C68', 'RING_EDC'),
                ('SCN_CCF_C28', 'RING_EDC'),
                ('SCN_CORE_C68', 'CORE_EDC'),
                ('SCN_CORE_C28', 'CORE_EDC')
                }

        cfgfile = 'Shared/BaseInputs/mtt_map_remove.json'
        if exists(cfgfile):
            with open(cfgfile) as fh:
                data = json.load(fh)
            data = set(tuple(x) for x in data)

        return data

    def add_blocks(self, flines, domains, mtpl):
        """
        Add new FlowControl and SetFlowInfo blocks
        :param flines: mtpl lines with EOL char
        :param domains: set of domains
        :param mtpl: mtpl name
        :return:
        """
        initial = True
        result = []
        added = {'fc': set(),
                 'sf': set()}

        self.set_nflows(flines, mtpl)
        for line in flines:
            if initial and line.strip().startswith('DUTFlow'):
                initial = False
                for dom in sorted(domains):
                    added['fc'].add(f'FlowControl_{dom}')
                    result.append(f'Test PrimeFlowControlForkTestMethod FlowControl_{dom}\n')
                    result.append(f'{{\n')
                    result.append(f'    DomainName = "{dom}";\n')
                    result.append(f'}}\n')

                    for flow in self.nflows:

                        # Ly says that 19J works if SetFlowInfo_RING_Flow* is removed.
                        # TPIE program has this though, Ly asked Freddy and Freddy says "tos bug and have the check fail randomly"
                        modname = basename(dirname(mtpl))
                        if (modname, dom) in self.map_remove:
                            continue

                        added['sf'].add(f'SetFlowInfo_{dom}_Flow')
                        result.append(f'Test PrimeFlowControlSetTestMethod SetFlowInfo_{dom}_Flow{flow}\n')
                        result.append(f'{{\n')
                        result.append(f'    DomainName = "{dom}";\n')
                        result.append(f'    DomainValue = {flow};\n')
                        result.append(f'}}\n')

            # The rest of the lines
            result.append(line)
        return result, added

    def re_with_not(self, restr, text):
        """
        Executes normal regex for restr, with special "!" in front for not.
        :param restr: regex with ! in front for not
        :param text: any string
        :return: True if match
        """
        if restr.startswith('!'):
            return not re.search(restr[1:], text)
        return re.search(restr, text)

    def replace_dutflowitems(self, flines, added, modname, domains):
        """
        Replace dutflowitems for added blocks
        :param flines: mtpl lines with EOL char
        :param added: set of added instances
        :param modname: module name
        :param domains: dictionary of domains
        :return: flines
        """
        result = []
        for line in flines:
            if line.strip().startswith('DUTFlowItem'):
                elems = line.strip().split()

                # FlowControl first
                if elems[2] == 'FlowControl':

                    # get newname
                    if len(added['fc']) == 1:
                        newname = list(added['fc'])[0]
                    else:
                        for dom, dom_re in domains.items():
                            if self.re_with_not(dom_re, elems[1]):
                                newname = f'FlowControl_{dom}'
                                break
                        else:
                            raise ErrorInput(f'Cannot determine domain for {elems[1]}')

                    result.append(f'        {elems[0]} {elems[1]} {newname}\n')
                    continue  # replace this line

                # SetFlowInfo next
                if elems[2].startswith('SetFlowInfo_Flow'):
                    for dom, dom_re in domains.items():
                        if self.re_with_not(dom_re, elems[1]):
                            newname = f'SetFlowInfo_{dom}_Flow'
                            break
                    else:
                        raise ErrorInput(f'Cannot determine domain for {elems[1]}')

                    newname = elems[2].replace('SetFlowInfo_Flow', newname)
                    result.append(f'        {elems[0]} {elems[1]} {newname}\n')
                    continue  # replace this line

            # the rest of the lines
            result.append(line)
        return result

    @classmethod
    def edc_domains(cls, flines, domains):
        """
        Add the EDC if it exist in domains
        :param flines: lines
        :param domains: assume one only
        :return: None
        """
        for domain in domains:
            if 'EDC' in domain:
                return  # Do nothing

        for line in flines:
            if line.strip().startswith('DUTFlowItem'):
                if cls.is_edc_line(line):
                    confirm(len(domains) == 1,
                            f'domains={domains.keys()}. expecting 1 only.',
                            'Contact jqdelosr')
                    ref = list(domains)[0]
                    domains[f'{ref}_EDC'] = '_EDC$'
                    domains[ref] = '!_EDC$'
                    return

    @classmethod
    def is_edc_line(cls, line):
        """

        :param line:
        :return: True if line is edc
        """
        elems = line.strip().split()
        if elems[2].startswith('FlowControl') and elems[1].endswith('EDC'):
            return True
        if elems[1] == 'FlowControl_BGFBIST_X_VMIN_K_ENDGT_X_VCCGT_F1_100':
            return True
        return False

    def get_domains(self, mtpl, check_only=False):
        """
        Get domain name string given mtpl.
        Logic: Find first occurrence of below regex in mtpl
        Guaranteed via test_get_domains

        :param mtpl: filename of mtpl
        :param check_only: Set to True if check_only
        :return: dict of domain name
        """
        result = None
        for key, val in self.mapping.items():
            if key in basename(mtpl):
                result = val
                break

        # check if mapping is incorrect, by opening the file
        robj = re.compile(r'^\s*Test iCBinMatrixFlowControlTest ', re.MULTILINE)
        all_res = robj.findall(File(mtpl).read())
        if all_res and (not result):
            raise ErrorCockpit(f'{mtpl} has iCBinMatrixFlowControlTest, but no mapping defined in MTTExpand()',
                               f'Define [{basename(mtpl)}] in Shared/BaseInputs/mtt_mapping.json')

        if check_only:
            return result

        # Check if rerun (aka, no more iCBinMatrixFlowControlTest)
        if not all_res:
            return None  # No need to process

        return result


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    obj = TorchPostProc()
    obj.main()
