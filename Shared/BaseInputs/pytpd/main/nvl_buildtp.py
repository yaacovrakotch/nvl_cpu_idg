#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
NVL+RZL version of buildtp

Usage:
   nvl_buildtp.py <BOM> [-out folder]
   nvl_buildtp.py <BOM> -torch
   nvl_buildtp.py None -clone
   nvl_buildtp.py <BOM> -stitch outfolder
   nvl_buildtp.py None|<BOM> -flow [-common] [-tpbot] [-output path]
   nvl_buildtp.py <BOM> -onebomflow [-common] -tpbot -output path -tdir path

Overall flow, See https://wiki.ith.intel.com/display/ITSpdxtp/NVL+one+click+build

Torch fixer strategy:
====================
Requirement: clone+msbuild+load in tester should work
    msbuild is required because of dll, since we don't commit dll (Freddy requirement)

On Torch Fixer: Do we want to call this or not? Answer: No because of above requirement
   -> fix env   -> Alephs + pattern revs in the PATLIST
   -> fix stpl   (do nothing)
   -> Native MTT bins and counters

MO workflow:
    step1: clone
    step2: edit .mtpl
    step3: commit here
    step3: msbuild.py   (Which calls Torch fixer)
    step4: <validate in tester>

Reason why we run "Torch Fixer" in mtl/arl: because we don't want .env conflicts.
But in NVL, we will use modular .env to avoid conflicts.

Summary:
1. update dielet repo msbuild.py to include Torch Fixer code  # Reason: We need msbuild anyway, so add Torch fixer.
2. nvl_buildtp.py: remove Torch Fixer
3. NVL must use Modular Env

ProgramFlows protocol:
* In common repo, the ProgramFlows.py is COMPLETE. This is the True source of programflows.py.
* In common repo, the ProgramFlows.mtpl is also complete. We always commit .py and .mtpl together.
* In CDIE (or any dielet) repo, We don't have ProgramFlows.py committed to avoid confusion
   we only have ProgramFlows.mtpl which contain CDIE only in CDIE repo.
     -> Need a routine to call common's ProgramFlows.py, "reduce it to cdie only", then run pymtpl
"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.helperclass import OPT, IS_UT
from gadget.tputil import CheckerLog, get_modulename, OtplFile, delete_por_tp, JsonRead
from gadget.vepargs import Args, TA_All, TA_StoreTrue, TA_Store
from gadget.dictmore import DictDot, NamedSeq, reverse_keyval
from gadget.errors import confirm, ErrorInput, ErrorUser
from gadget.files import File, glob_one_only, check_and_del, TempDir
from gadget.shell import IS_UNIX, SystemCall, untar, TarAdd, CALLERBIN, IS_WIN
from gadget.pylog import log
from gadget.gizmo import Elapsed, MockVar
from gadget.disk import mkdirs, Chdir, rmtree, get_free_diskspace, check_disk_threshold
from gadget.getgit import GetCmd, GitHub, GitCheckout
from gadget.files import File
from gadget.data_host import DataHost
from gadget.tvpv import TvpvEnv
from main.tprobot import TPRobot
from main.torch_mv import DoMV
from main.torch_postproc import EnvEdit, Misc, RecipeEdit, MtplNewLine, PlistEdit, UservarEdit, TorchPostProc
from main.qgate import QGateExecute
from main.msbuild import MSBuild
from mod.nvl_pr_report import main_pr_integrate
from tp.timlvl import Usrv
from tp.testprogram import TestProgram, Env
from mod.mtplencode import MtplEncode, NPRTrigger
from mod.moduleskip import ModuleSkip, MvJson
from mod.cleantp_mod import CleanTP
from mod.nvl_pr_report import return_report_file
from mod.envreorder import EnvReorder
from mod.tpswitch import TPSwitch2, TPSwitch
from mod.failmodid import FailModuleId
from pyqs import Merge
from os.path import dirname, basename, isdir, join, exists
from collections import OrderedDict, Counter
from pprint import pformat
import glob
import os
import shutil
import re
import json
import sys
import random
import time


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


# TODO: delete unneeded boms in BaseInputs


class NVLBuildTPEntry(Args):

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.clone = TA_StoreTrue('Call clone')
        cfg.torch = TA_StoreTrue('Call Torch build and recipes')
        cfg.output = TA_Store('Specify output directory', metavar='outdir')
        cfg.stitch = TA_Store('Do fulltp Stitcher', metavar='outdir')
        cfg.flow = TA_StoreTrue('Run main flow for yml')
        cfg.common = TA_StoreTrue('Specify common repo. Used with -flow')
        cfg.tpbot = TA_StoreTrue('Specify tpbot run. Used with -flow')
        cfg.tdir = TA_Store('tempdir. Used with -onebomflow', metavar='path')
        cfg.onebomflow = TA_StoreTrue('CMD: Call onebom flow')
        cfg.build = TA_Store('CMD: Build TP', metavar='FULL|mv_json_file')
        cfg.clean = TA_StoreTrue('Do not clean. Used with -build')
        cfg.nolatest = TA_StoreTrue('Do not change sha to latest common. Used with -build')
        cfg.env = TA_Store('Do not use! Used internally for pymtpl')
        return cfg

    def main(self):
        """Main Entry point"""
        # check that bom exist
        confirm(OPT.all, 'Incorrect usage', f'\n{__doc__}')

        # TempDir.cleanup()

        # Assign tpname here (and do checking)
        NVLBuildTP.set_tpname(OPT.output, os.environ.get('IN1', 'FULL'))

        # Set QUICKBUILD mode early - triggered by QUICKBUILD env var
        NVLBuildTP.QUICKBUILD = os.environ.get('QUICKBUILD', 'false').lower() == 'true'
        if NVLBuildTP.QUICKBUILD:
            log.info('-i- QUICKBUILD mode is ENABLED - reduced postprocessing for faster builds')

        self.call_methods(['torch',     # this will call do_torch(), if -torch
                           'clone',     # this will call do_clone(), if -clone
                           'stitch',    # this will call do_stitch(), if -stitch
                           'build',     # this will call do_build(), if -build
                           'flow',      # this will call do_flow(), if -flow
                           'onebomflow',  # this will call do_onebomflow(), if -onebomflow
                           ])

    def do_build(self):
        """
        Build a testprogram - wrapper to yml -flow
        Set the environment vars
        """
        confirm(OPT.output, '[-output <outfolder>] is required', 'Pls fix cmdline')
        porfolder = f'POR_TP/{OPT.all[0]}'
        confirm(isdir(porfolder), f'[{porfolder}] does not exist', 'Pls provide correct BOM name')
        self._check_mvtemplate(OPT.build)

        OPT.output = os.path.abspath(OPT.output)    # make it abspath so relative path will work with TempDir

        os.environ['IN1'] = OPT.build
        os.environ['CLEANTP'] = 'true' if OPT.clean else 'false'

        # os.environ['DIEINDICATOR'] = tbd      # TODO: add code here, use a special file we read in repo - This todo is Done?

        self.do_flow()

    def _check_mvtemplate(self, infile):
        """
        Checks -build <option>
        :param input: FULL or mvtemplate file
        :return:
        """
        if infile == 'FULL':
            return 1
        mvpath = f'TPConfig/MV_Templates/{infile}.json'
        confirm(exists(mvpath), f'{mvpath} does not exist', f'Pls check [-build {infile}]. The json file should exist')
        return 2

    def do_torch(self):
        """
        Torch build, and recipies
        """
        NVLBuildTP(OPT.all[0]).do_torch()

    def do_clone(self):
        """
        Call clone
        """
        Clone(OPT.all[0]).main()

    def do_stitch(self):
        """
        FullTP Stitcher
        """
        Integrate(OPT.all[0]).main(OPT.stitch)

    def do_flow(self):
        """
        Flow run, called from yml
        """
        NVLBuildTP.main_flow(OPT.common, OPT.tpbot, OPT.output, bom=OPT.all[0])

    def do_onebomflow(self):
        """
        Flow onebom run
        """
        # NVLBuildTP.main_flow_onebom(bom, is_common, is_tpbot, outdir, tempdir=tdir)
        NVLBuildTP.main_flow_onebom(OPT.all[0], OPT.common, OPT.tpbot, OPT.output, tempdir=OPT.tdir)

    def do_else(self):
        """
        Main Entry point

        a. moduleskip (do the MV TP, if applicable, and moduleskip feature)
        b. postprocess
            b.1 Move .pin files into BomGroup folder
        c. qgates
        """
        NVLBuildTP(OPT.all[0], outdir=OPT.output).main()


class NVLBuildTP:
    tpname = None      # assigned by set_tpname()
    JOBID = None
    QUICKBUILD = False

    def __init__(self, bom, outdir=None):
        self.bom = bom

        which, isval, ispart, export_only = self._which_encoding(os.environ.get('IN1', 'FULL'))
        self.which = which                 # MV_json_file or FULL. Default is FULL
        self.isval = isval                 # True if VALL. False by default
        self.ispart = ispart               # True if PART. False by default
        self.export_only = export_only     # True if export_only

        self.env_glob = f'./*TP/{self.bom}/EnvironmentFile*.env'
        self.envs = glob.glob(self.env_glob)
        confirm(self.envs, f'No .env found: [{os.getcwd()}/{self.env_glob}]', 'Check the folder')
        confirm(len(self.envs) == 1, f'Multiple .env found: [{self.envs}]', 'Expecting only 1')
        self.env = self.envs[0]
        self.tpobj = None
        self.outdir = outdir
        self.root_pobj_cache = Env.xpath('/intel/tpvalidation/engtools/tptools/mtl/infra/torch/pobj_cache_tp')

        # Check if output directory has sufficient disk space
        check_disk_threshold(self.outdir, threshold_gb=2)

        # Check DEST environment variable (user specified destination)
        dest_path = os.environ.get('DEST', '')
        check_disk_threshold(dest_path, threshold_gb=2)

    def main(self):
        """
        Main Entry point for a "built" testprogram.
        Call postprocesses and Qgates
        The testprogram must be formed and dll-ready (aka stitched) before calling this routine.
        """
        # Dispatch to quickbuild if enabled
        if NVLBuildTP.QUICKBUILD:
            return self.main_quickbuild()

        # ===== Startup checks
        CheckerLog.build_checks(self.envs, self.env_glob)
        mkdirs(f'{dirname(self.env)}/Reports')

        # ===== Create the tpobj
        self.tpobj = TestProgram(self.env)
        self.tpobj.plists.error_out = False
        log.info(f'-i- {self.tpobj.get_stpl()} contents:\n%s' % (File(self.tpobj.get_stpl()).read()))

        # ===== Call ModuleSkip
        TarAdd('complete_tp.tar.gz', '.', exclude=['.git', 'temp'])     # We need to create TP snapshot (fulltp) before moduleskip so that qgate 270 will act on a "complete" TP
        self.do_moduleskip()

        # EXPORTONLY feature: "EXPORTONLY:FULL" for as-is, "EXPORTONLY:<mvjson>" for mv
        if self.export_only:
            self.copytp(self.outdir)
            return 1     # Exit right away

        # Since tp is modified, then re-instantiate the tpobj
        self.tpobj = TestProgram(self.env, allpats=True).init()
        self.tpobj.plists.error_out = False

        # ===== Call postprocess

        log.info(f'-i- START: EnvEdit({self.tpobj.get_bom()})')
        EnvEdit(self.tpobj).main_tos4()    # various things here

        log.info(f'-i- START: Misc({self.tpobj.get_bom()})')
        Misc(self.tpobj).copybat()
        Misc(self.tpobj).npr_mo_pup_del()
        Misc(self.tpobj).unzip_PinToChain()

        # FSM automation section
        log.info(f'-i- START: MtplEncode({self.tpobj.get_bom()})')
        MtplEncode(self.tpobj).generate_meta()
        me = MtplEncode(self.tpobj).read_meta()
        fsm_final_path = me.do_fsmpath_assembl(NVLBuildTP.tpname, self.bom, self.isval, self.ispart)
        me.do_fsm(self.bom)
        me.do_fsm_env_copy(fsm_final_path, self.bom)

        log.info(f'-i- START: RecipeEdit({self.tpobj.get_bom()})')
        RecipeEdit(self.tpobj).main()

        log.info(f'-i- START: EnvReorder({self.tpobj.get_bom()})')
        EnvReorder(self.tpobj).main(disp=False, update=True)

        log.info(f'-i- START: MtplNewLine({self.tpobj.get_bom()})')
        MtplNewLine(self.tpobj).main()

        log.info(f'-i- START: PlistEdit({self.tpobj.get_bom()})')
        PlistEdit(self.tpobj).main()     # self.call_plistedit(self.tpobj)

        self.do_tprename()

        self.copy_pobj_cache()           # Do this early on, but after plistedit and envreorder

        log.info(f'-i- START: TPName_sync')
        UservarEdit(self.tpobj).tpname_sync()

        TorchPostProc.custom_scripts(self.tpobj.envfile, 'buildpost_*')

        # remove unused mod-subbindef.sbdefs
        self.subdef_reduce(self.tpobj.tpldir, self.tpobj.mtpl.get_modfolder2mod())

        # fix the 8-digit-bins. This routine has a bug. Contact Tai to enable it again in the future.
        # self.bindef_shared_bin(self.tpobj.mtpl.get_mod2fname())

        # write the dielet indicator for dielet repo
        self.update_dieletindicator()

        TPSwitch.main(self.tpobj.get_bomfolder(), '.', 'post-build')

        self.tpswitch2()

        # remove the fats of the TP
        self.do_cleantp()

        # ===== NPR/PUP trigger
        # This requires execute right before no more modifications line due to send a trimmed version for PUP trigger.
        npr = NPRTrigger(self.tpobj)
        npr.main(True, self.outdir)

        # ===== No more modifications at this point, create the final tpobj
        # Generate the PR report
        previous_tp = os.environ.get('PREVIOUSTP', 'None')
        if previous_tp != 'None':
            self.get_pr_report_file(previous_tp)

        self.tpobj = TestProgram(self.env, allpats=True).init()        # Reload obj after cleantp

        # ===== Call pyqs
        obj = Merge(self.tpobj)
        obj.importall()
        obj.main()
        obj.write_file('final_qs.xml')

        # ===== Call qgate
        log.info(f'-i- START: QGate() checkers')
        QGateExecute(self.tpobj).main()                                # Qgate will raise exception on error. Decision is on qgate.

        # ===== Call failmodid
        if os.environ.get('FAILMODID', 'false').lower() == 'true':    # pragma: no cover
            log.info(f'-i- FAILMODID is set to true. Running test program modification...')
            FailModuleId(os.getcwd()).main()  # update the TP

        # copy if outdir is provided
        File('complete_tp.tar.gz').unlink()
        self.copytp(self.outdir)

        # ===== NPR/PUP trigger check
        npr.wait()

    def get_pr_report_file(self, previous_tp):
        """
        Generate the PR report file.
        :param previous_tp: PREVIOUS TP name
        """
        current_tp = os.path.basename(self.outdir)[10:15]
        dielet_bit = os.path.basename(self.outdir)[15:17]
        main_pr_integrate(current_tp, previous_tp)
        report_file = return_report_file(current_tp, dielet_bit)
        if os.path.exists(report_file):
            log.info(f'-i- PR report generated: {report_file}')
            report_dest_dir = glob.glob(f'./POR*/{self.bom}/Reports')
            if report_dest_dir:
                report_dest_dir = report_dest_dir[0]
                log.info(f'-i- Copying PR report to: {report_dest_dir}')
                log.info(f'-i- Report file: {os.path.join(report_dest_dir, os.path.basename(report_file))}')
                shutil.copy(report_file, os.path.join(report_dest_dir, os.path.basename(report_file)))
            else:
                log.warning(f'-i- PR report generation failed: {report_dest_dir} not found.')
        else:
            log.warning(f'-i- PR report generation failed: {report_file} not found')

    def main_quickbuild(self):
        """
        Reduced main routine for faster builds.
        Triggered by QUICKBUILD environment variable.

        Skips: PR report, FSM automation, RecipeEdit, MtplNewLine, do_tprename,
               copy_pobj_cache, TPName_sync, custom scripts,
               TPSwitch, tpswitch2, do_cleantp,
               final tpobj reload, PyQS merge, QGate checkers, FailModID
        """
        log.info('-i- ===== QUICKBUILD mode: Starting reduced postprocessing =====')

        # ===== Startup checks
        CheckerLog.build_checks(self.envs, self.env_glob)
        mkdirs(f'{dirname(self.env)}/Reports')

        # ===== Create the tpobj
        self.tpobj = TestProgram(self.env)
        self.tpobj.plists.error_out = False
        # Skip STPL logging for Quick build
        # log.info(f'-i- {self.tpobj.get_stpl()} contents:\n%s' % (File(self.tpobj.get_stpl()).read()))

        # ===== Call ModuleSkip (needed for MV support)
        self.do_moduleskip()

        # EXPORTONLY feature: "EXPORTONLY:FULL" for as-is, "EXPORTONLY:<mvjson>" for mv
        if self.export_only:
            self.copytp(self.outdir)
            return 1     # Exit right away

        # Since tp is modified, then re-instantiate the tpobj
        self.tpobj = TestProgram(self.env, allpats=True).init()
        self.tpobj.plists.error_out = False

        # ===== Call postprocess (reduced set)
        log.info(f'-i- START: EnvEdit({self.tpobj.get_bom()})')
        EnvEdit(self.tpobj).main_tos4()

        log.info(f'-i- START: Misc({self.tpobj.get_bom()})')
        misc = Misc(self.tpobj)
        misc.copybat()
        misc.npr_mo_pup_del()
        misc.unzip_PinToChain()

        log.info(f'-i- START: EnvReorder({self.tpobj.get_bom()})')
        EnvReorder(self.tpobj).main(disp=False, update=True)

        log.info(f'-i- START: PlistEdit({self.tpobj.get_bom()})')
        PlistEdit(self.tpobj).main()

        # Remove unused mod-subbindef.sbdefs (needed to avoid load errors for missing modules)
        log.info(f'-i- START: subdef_reduce({self.tpobj.get_bom()})')
        self.subdef_reduce(self.tpobj.tpldir, self.tpobj.mtpl.get_modfolder2mod())

        # Update dielet indicator for dielet repo (needed for DieId/DFF service)
        self.update_dieletindicator()

        # ===== Final copy (use optimized quickbuild copy)
        log.info('-i- ===== QUICKBUILD mode: Skipped FSM, RecipeEdit, MtplNewLine, TPSwitch, QGate, PyQS =====')
        self.copytp(self.outdir, quickbuild=True)

    def _which_encoding(self, which):
        """
        Do some encoding on input IN1
        Return: which, isval, export_only
        """
        # export_only
        export_only = False
        if which.startswith('EXPORTONLY:'):     # very useful for debug and development before postproc
            export_only = True
            which = which.replace('EXPORTONLY:', '')

        # tpname ==========
        # Determine the tpname based on input: FULL68-<Name19Char>
        # This must be upfront so it will fail early on the call
        # isval is True for tpvalidation folder and isval is False for production

        isval = bool(which == 'VALL')
        ispart = bool(which == 'PARTIAL')

        return which, isval, ispart, export_only

    @classmethod
    def is_valid_tpname(cls, tpname):
        """
        Determine if tpname is valid based on spec, very loose so we don't need to keep on updating it
        https://wiki.ith.intel.com/spaces/ITSpdxtp/pages/3676835216/NVL+TP+Naming+Standard

        NVLS956A0H05J0BCX04
        0123456789012345678
        AAACCCCCCABBCCCCCCC    << build your regex based on this

        :param tpname: string
        :return: True if tpname is valid name
        """
        if len(tpname) != 19:
            return False

        regex = r'^[A-Z]{3}[A-Z\d]{6}[A-Z]\d{2}[A-Z\d]{7}$'
        if not re.match(regex, tpname):
            return False

        return True

    @classmethod
    def set_tpname(cls, outdir, which):
        """
        Set the tpname class variable depending on value of outdir which which
        :param outdir: path to output, can be None, '', 'I:\' or "None"
        :param which: FULL, VALL or PARTIAL "-" is now illegal
        :return:
        """
        # check "which" first
        confirm('-' not in which,
                f'[{which}] can only be FULL, VALL or PARTIAL without tpname',
                'The TPname is derived automatically from the output folder name.')

        # outdir processing
        if not outdir:    # None or ''
            return        # do nothing

        tpname = basename(outdir)
        if cls.is_valid_tpname(tpname):

            # Validate FULL TP name requires numeric at position 13 (index 12)
            if which == 'FULL':
                confirm(tpname[14].isdigit(),
                        f'Invalid tpname for FULL I drive TP: [{tpname}]. TP rev {tpname[14]} must be numeric.',
                        f'For FULL build, the 13th character must be a number.')

            # Validate VALL TP name requires alphabet at position 13 (index 12)
            if which == 'VALL':
                confirm(tpname[14].isalpha(),
                        f'Invalid tpname for VALL V drive TP: [{tpname}]. TP rev {tpname[14]} must be alphabetic.',
                        f'For VALL build, the 13th character must be a letter.')

            NVLBuildTP.tpname = tpname

    @classmethod
    def do_tprename(cls):
        """
        Update the env file if it is prod (as identified if tpname is provided in tpbuild form)
        Default is ENGG
        """
        # FULL or VALL with tp name is production
        # otherwise ENGG
        if NVLBuildTP.tpname:
            log.info(f'-i- do_tprename(): tpname={NVLBuildTP.tpname}')
            Usrv.update_usrv(f'Shared/BaseInputs/Common/Common_Files/common.usrv',
                             'iCGL_ProductionEngg', 'PROD')       # Default is ENGG in repo

    def tpswitch2(self):
        """
        Run tpswitch 2
        :return:
        """
        log.info(f'-i- START: TPSwitch2')
        TPSwitch2._set_tpobj(self.tpobj)

        for portp, fname in TPSwitch2._get_por_tps(os.environ.get('ACPY')):
            log.info(f'-i- START: TPSwitch2({portp}, {fname})')
            hvmtmp = f'{dirname(self.tpobj.envdir)}/hvm.{basename(self.tpobj.envdir)}'
            shutil.copytree(self.tpobj.envdir, hvmtmp)
            TPSwitch2._process(fname)

            with MockVar(os.environ, 'ACPY', MockVar.delete), \
                    MockVar(os.environ, 'PREVIOUSTP', MockVar.delete), \
                    MockVar(os.environ, 'TPSWITCH2', 'True'):

                # NVLBuildTP(self.bom).do_torch(genrecipe=False)      # cannot call torch.exe stuff, since torch.exe is dielet. At this point we are fulltp.
                NVLBuildTP(self.bom).main()

            File(f'{self.tpobj.envdir}').rename(portp)
            File(hvmtmp).rename(basename(self.tpobj.envdir))
            log.info(f'-i- END: TPSwitch2({portp})')

    def do_cleantp(self):
        """
        Logic for cleantp:
        CLEANTP env not exist - clean
        CLEANTP env true - clean
        CLEANTP env false - no clean
        """
        if os.environ.get('CLEANTP', 'true').lower() == 'true':
            log.info(f'-i- START: CleanTP')
            CleanTP(self.tpobj).main()
            return 1
        else:
            log.info(f'-i- CleanTP is skipped due to CLEANTP env')
            return 2

    @classmethod
    def update_dieletindicator(cls):
        """
        Update dielet_indicator only for dielet repo
        """
        if 'DIEINDICATOR' in os.environ:          # this is only defined if dielet repo
            Usrv.update_usrv(f'Shared/BaseInputs/Common/Common_Files/TOSRules.usrv',
                             'DIELET_INDICATOR', os.environ['DIEINDICATOR'])

    @classmethod
    def main_flow(cls, is_common, is_tpbot, outdir, bom='none'):
        """
        Main routine called from yml. This is the "main flow"

        :param is_common: Set to True for common. cwd must be common checkout.
        :param is_tpbot: Set to True for tpbot
        :param outdir: destination folder. Set to None for No destination (checkers)
        :param bom: string: set to none for all boms
        :return:
        """
        from main.runner_botos import RunnerBotOS

        for bom in RunnerBotOS.affected_boms(bom):
            with TempDir(name=True) as tdir:
                try:
                    cls.main_flow_onebom(bom, is_common, is_tpbot, outdir, tempdir=tdir)
                except Exception:
                    # copy TP to destination on error (eg. tpbuild runs)
                    if isdir(tdir):     # sometimes isdir does not exist
                        with Chdir(tdir):
                            NVLBuildTP.copytp(outdir, failrename=True)
                    raise       # re-raise exception

    @classmethod
    def main_flow_onebom(cls, bom, is_common, is_tpbot, outdir, tempdir):
        """
        One bom main flow
        Called by runner_botos and main_flow (common routine)

        cwd must be normal github checkout

        :param bom: BOM name
        :param is_common: Set to True for common. cwd must be common checkout.
        :param is_tpbot: Set to True for tpbot
        :param outdir: destination folder - Required for common
        :param tempdir: empty tempdir, for common so it's fast
        :return: None
        """
        log.info(f'-i- ##### main_flow(): bom={bom}, is_common={is_common}, is_tpbot={is_tpbot}')
        CheckerLog.set_repo_sha()    # This is here so that tpbot and checkers has it on the same place.
        swtotal = Elapsed()
        sw = Elapsed()

        # ===== step -1 - change Shared to latest sha (dielet runs)
        cls.update_shared_sha_latest(bom, is_checker=bool('CHECKER_FULLTP' in os.environ))

        # ===== step0 - create workdir in tempdir
        check_and_del(tempdir, mv_on_error=True)
        if is_common or 'CHECKER_FULLTP' in os.environ:
            pass         # Do nothing, workdir is '.'
        else:
            cls.create_dielet_sha()
            shutil.copytree('.', tempdir, ignore=lambda *x: ['temp'])     # workdir is tempdir
        log.info(f'-z- main_flow Step0 create_workdir Elapsed: {sw.elapsed(pretty=True, reset=True)}')

        # ===== step1 - call msbuild + torch fixer. This puts correct Common_Torch/ folder
        if is_common or 'CHECKER_FULLTP' in os.environ:
            with Chdir('../../..'):
                # call msbuild for this specific bom.
                MSBuild().main('nvl.cpu/NVL_CPU.sln', bom, ispostproc=False)
                MSBuild().main('nvl.gcd/NVL_GCD.sln', bom, ispostproc=False)
                MSBuild().main('nvl.hub/NVL_HUB.sln', bom, ispostproc=False)
                MSBuild().main('nvl.pcd/NVL_PCD.sln', bom, ispostproc=False)

        else:
            with Chdir(tempdir):
                MSBuild().main(glob_one_only('NVL_???.sln'), bom, ispostproc=False)
        log.info(f'-z- main_flow Step1 msbuild Elapsed: {sw.elapsed(pretty=True, reset=True)}')

        # Remove unused BOMgroups folders from POR_TP and BaseInputs
        log.info(f'before delete por tp folder tempdir={tempdir}')
        delete_por_tp(tempdir, bom)

        # ===== step2 - Call Torch recipe, reports, etc
        if is_common or 'CHECKER_FULLTP' in os.environ:
            for dielet in ('nvl.cpu nvl.gcd nvl.pcd nvl.hub'.split()):
                log.info(f'Processing {dielet} in step2...')
                delete_por_tp(f'../../../{dielet}', bom)
                with Chdir(f'../../../{dielet}'):
                    NVLBuildTP(bom).do_torch(tpbot=is_tpbot)

        else:
            with Chdir(tempdir):
                NVLBuildTP(bom).do_torch(tpbot=is_tpbot)
        log.info(f'-z- main_flow Step2 torch_recipes Elapsed: {sw.elapsed(pretty=True, reset=True)}')

        # ===== step3 - build the TP
        if is_common or 'CHECKER_FULLTP' in os.environ:
            # call full tp stitcher
            with Chdir('../../..'):
                confirm(outdir, '-output must be provided for common tp stitch', 'Pls provide -output')
                Integrate(bom).main(tempdir)
        else:
            # dielet
            delete_por_tp(tempdir, bom)
            cls.delete_modules_unused(tempdir, bom)         # To match fulltp behavior. Modules are deleted.
        log.info(f'-z- main_flow Step3 full-tp-stitch Elapsed: {sw.elapsed(pretty=True, reset=True)}')

        # ===== step4 - call nvl_buildtp
        with Chdir(tempdir):
            NVLBuildTP(bom, outdir=outdir).main()

        log.info(f'-z- main_flow Step4 nvl_buildtp Elapsed: {sw.elapsed(pretty=True, reset=True)}')

        log.info(f'-z- bom={bom}, Total Elapsed: {swtotal}')

    @classmethod
    def update_shared_sha_latest(cls, bom, is_checker):
        """
        Update the Shared/ folder to latest sha. See wiki: https://wiki.ith.intel.com/x/AjOX_w
        This is only for dielets
        cwd is github checkout

        :param bom: bom name
        :param is_checker: True for checkers
        :return: unittest only
        """
        # Do nothing for common
        if not exists('Shared'):
            log.info('-i- update_shared_sha_latest() is skipped - Shared/ not exist (aka, common repo)')
            return 1      # Do nothing

        # do nothing if -nolatest
        if OPT.nolatest:
            return 5

        # get the PR description branch name
        pr_desc_common = BuildCommon.get_branch('nvl.common', None)     # cwd is repo

        # determine if dielet or fulltp
        if is_checker:
            dielet = basename(os.getcwd())
            wd = f'../../../{dielet}'
            confirm(isdir(wd),
                    f'Error: [{wd}] does not exist! cwd={os.getcwd()}',
                    'Something is wrong with the runner machine.')
        else:
            wd = '.'

        with Chdir(wd):
            before = CheckerLog.get_folder_sha("Shared")

            # Do this only if it is HEAD (aka, do nothing if it's a real branch from user)
            log.info(f'-i- update_shared_sha_latest() is starting. cwd={os.getcwd()}')
            with Chdir('Shared'):
                out = SystemCall(f'git rev-parse --abbrev-ref HEAD', disp=True).run_outonly()
            if out.strip() != 'HEAD':
                log.info(f'-i- update_shared_sha_latest() will not update to latest sha, because output is [{out.strip()}]. Expecting HEAD.')
                return 3

            # update it
            if 'COMMON_Branch' in os.environ:
                brname = os.environ['COMMON_Branch']       # tpbuild
            else:
                if pr_desc_common:
                    brname = pr_desc_common
                    log.info(f'-i- Using nvl.common branch name from PR description: {brname}')
                else:
                    brname = Clone.get_common_brname(bom)

            with Chdir('Shared'):
                GitCheckout().main(brname)

            log.info(f'-i- before sha: {before}')
            log.info(f'-i- after sha:  {CheckerLog.get_folder_sha("Shared")}')

        return 4

    @classmethod
    def delete_modules_unused(cls, tempdir, bom):
        """
        Delete modules not connected in stpl, to match fulltp behavior
        Example, INIT fail due to missing alephs
        """
        log.info('-i- dielet delete_modules_unused()')
        with Chdir(tempdir):
            # get the modules on disk
            found = set()
            for modmtpl in glob.glob('Modules/*/*/*.mtpl') + glob.glob('Modules/*/*.mtpl'):
                modfolder = dirname(modmtpl)
                team = basename(dirname(modfolder))
                mname = basename(modfolder)
                found.add(f'{team}/{mname}')

            # get used modules
            tpobj = TestProgram(bom)
            for mod in tpobj.get_all_mtpl_from_stpl():
                if '../Modules' in mod.replace('\\', '/'):
                    modfolder = dirname(mod)
                    team = basename(dirname(modfolder))
                    mname = basename(modfolder)
                    key = f'{team}/{mname}'
                    if key in found:
                        found.discard(key)
                    else:
                        log.info(f'-w- {key} is not found on disk: {os.getcwd()}')

            # delete
            for key in found:
                log.info(f'-i- Deleting Modules/{key}')
                check_and_del(f'Modules/{key}', mv_on_error=True)

    @classmethod
    def copytp(cls, outdir, failrename=False, quickbuild=False):
        """
        Copy cwd into outdir, if specified

        Note: We tried using robocopy, but the performance is worse than untar.

        :param outdir: destination path
        :param failrename: Set to True to rename POR_TP folder to POR_TP_FAILED
        :param quickbuild: Set to True to use DataHost central untar for faster copy on Unix systems
        :return: unittest only
        """
        if not outdir:
            return 1     # do nothing

        if len(outdir) == 3:    # I:\ or I:/
            return 2     # do nothing

        # Rename POR_TP folder so we know it failed
        if failrename:
            for portp in glob.glob('*_TP'):
                File(portp).rename(f'{portp}_FAILED')

        sw = Elapsed()
        with TempDir(name=True) as tdir:
            TarAdd(f'{tdir}/tp.tar.gz', '.', exclude=['.git', 'temp'])
            log.info(f'-i- copytp(quickbuild={quickbuild}): created tar.gz in tempdir {tdir}, Elapsed {sw}')
            File(outdir).rename_incremental()
            mkdirs(outdir)

            if quickbuild:
                # Move tar.gz to outdir before calling central untar
                log.info("-i- Using copytp(quickbuild=True) via DataHost for faster copy")
                File(f'{tdir}/tp.tar.gz').move(outdir)
                log.info(f'-i- copytp(quickbuild=True): moved tar.gz to outdir {outdir}, Elapsed {sw}')
                tar_dest = f'{outdir}/tp.tar.gz'
                tar_dest_unix = Env.to_unixpath(tar_dest, is_unix=True)
                log.info(f'-i- Site for untar: {TvpvEnv.get_site()}, Untar to: {tar_dest_unix}')
                DataHost().central("untar", tar_dest_unix, check=True, site=TvpvEnv.get_site())
                log.info(f'-i- copytp(quickbuild=True): untar via DataHost central untar completed, Elapsed {sw}')
                check_and_del(f'{outdir}/.git', mv_on_error=True)
            else:
                with Chdir(outdir):
                    untar(f'{tdir}/tp.tar.gz', '.')
                    check_and_del('.git', mv_on_error=True)    # this is empty dir, so just delete it

        log.info(f'-i- copytp() to idrive [{outdir}], Elapsed {sw}')

    def do_moduleskip(self):
        """Module skip routine"""
        log.info(f'-i- START: ModuleSkip({self.bom})')
        onlylist = MvJson().read_mv_json(self.tpobj, self.which)                             # check if mvjson is provided
        self.fulltp_only(onlylist)
        if onlylist:
            ModuleSkip(self.tpobj, onlylist=onlylist).main(isdelete=True)          # MV json, do not use SkipModule folder
        else:
            ModuleSkip(self.tpobj, skipfile=True).main(isdelete=True)              # FULLTP version, use SkipModule folder

    @classmethod
    def subdef_reduce(cls, tpldir, list_of_valid_modules):
        """
        This function will remove the unused/not available module subbindef file.
        Without removing the unavailable subbindef file, we will fail load in fullTP.
        This is the gap between dielet repo and fulltp

        We want to call this routine ONLY if needed, example:
            1. This routine is required for skipmodule and MV TP.
        so that "git clone" will not have this problem and does not require "postprocess"
        """
        if 'TPSWITCH2' in os.environ:
            log.info(f'-i- subdef_reduce() is skipped due to tpswitch2')
            return 1

        # Get the SubBindef.imp file
        subbindef_files = (glob.glob(f'{tpldir}/BaseInputs/*/*_Files/*_SubBindef.imp') +
                           glob.glob(f'{tpldir}/Shared/BaseInputs/Common/Common_Files/*_SubBindef.imp'))
        for item in subbindef_files:
            log.info(f'-i- Checking: {item}')
            with open(item, 'r') as f:
                f_lines = f.readlines()
            with open(item, 'w') as f:
                for line in f_lines:
                    if line.startswith('Import'):
                        mod_path = line.split('\"')[1]
                        mod = os.path.basename(os.path.dirname(mod_path))
                        if mod in list_of_valid_modules:
                            f.write(line)
                        else:
                            log.info(f'-i- Not found {mod}. Removed it from the {item}')
                    else:
                        f.write(line)

    @classmethod
    def bindef_shared_bin(cls, mod_fname):        # pragma: no cover
        """
        This function will check if there is any duplicate bin in a fulltp.
        If there is duplicated bins, we will modify it to shared bin.
        1. Need to get all binID in the bindef file and subbindef file.
        2. Check for duplicated bins.
        3. Asign the duplicated bins to a new unique bin with 1000s
        4. Rewrite the file which has duplicated bins.
        mod_fname: Return {module_test_plan_name: mtpl_file_path}
        """
        log.info('Start bindef_shared_bin post-proc...')
        # 1. Get all the binID in the bindef file and subbindef file
        sub_bdef = []
        for value in mod_fname.values():
            mod_dir = os.path.dirname(value)
            sub_bdef_file = glob.glob(f'{mod_dir}/*.sbdefs')
            if sub_bdef_file:
                sub_bdef.append((sub_bdef_file[0]).split('../')[-1])

        not_allow_bin = []  # These bins are in the common_shared
        common_bindef = (glob.glob('Shared/BaseInputs/Common/Common_Files/*.sbdefs') +
                         glob.glob('Shared/BaseInputs/Common/Common_Files/*.bdefs'))
        for c_bdef in common_bindef:
            f_lines = File(c_bdef).raw()
            for line in f_lines:
                if line.strip().startswith('#'):
                    continue
                if line.strip().startswith('LeafBin'):
                    bin_id = line.split()[2]
                    not_allow_bin.append(bin_id)

        # Get a binID_dict of mod and its binID
        binID_dict = {}
        for bdef_file in sub_bdef:
            binID = []
            f_lines = File(bdef_file).raw()
            for line in f_lines:
                if line.strip().startswith('#'):
                    continue
                if line.strip().startswith('LeafBin'):
                    bin_id = line.split()[2]
                    binID.append(bin_id)
            binID_dict[bdef_file] = binID

        # Flatten all the bin in all_binID and get duplicate bins in dulicates_bin
        all_binID = []
        for bin_item in binID_dict.values():
            all_binID.extend(bin_item)
        # Count occurrences
        counter = Counter(all_binID)
        dulicates_bin = [item for item, count in counter.items() if count > 1]

        # shared_bin_dict to hold the dulicate bins and their modules which have the duplicate bins
        shared_bin_dict = {}
        for bin_item in dulicates_bin:
            if bin_item in not_allow_bin:
                continue
            log.info(f'Bin item: {bin_item}')
            mod_list = []
            for bdef_file, bin_list in binID_dict.items():
                if bin_item in bin_list:
                    log.info(f'Found duplicate Bin {bin_item} in {bdef_file}')
                    mod_list.append(bdef_file)
            shared_bin_dict[bin_item] = mod_list[1:]

        # Reverse the order to become {mod: [duplicate bins]} to write File easier
        shared_mod_bin = {}
        for key, vlist in shared_bin_dict.items():
            for value in vlist:
                shared_mod_bin.setdefault(value, []).append(key)

        # Now write to file and set unique bin for duplicate bins
        for mod, bin_list in shared_mod_bin.items():
            log.info(f'{mod}: {bin_list}')
            # Get module mtpl:
            for value in mod_fname.values():
                if os.path.dirname(mod) in value:
                    mtpl_path = value
                    break

            sbdef_data = File(mod).read()
            mod_data = File(mtpl_path).read()
            for bin_item in bin_list:
                # Given the ranges of 1000 possibilities.
                # If duplicate bins cannot be replaced within 100 first possibilities bin[6:8], increase [4:6] up to 10 possiblities
                for i in range(10):
                    for j in range(100):
                        if j < 10:
                            j = f'0{j}'  # In case of single digit
                        if int(bin_item[4:6]) + i < 10:
                            new_bin_item = f'{bin_item[0:4]}0{str(int(bin_item[4:6])+i)}{j}'  # In case of signle digit for bin[4:6]
                        else:
                            new_bin_item = f'{bin_item[0:4]}{str(int(bin_item[4:6])+i)}{j}'
                        if new_bin_item not in all_binID and new_bin_item not in not_allow_bin:
                            sbdef_data = sbdef_data.replace(bin_item, new_bin_item)
                            mod_data = mod_data.replace(bin_item, new_bin_item)
                            all_binID.append(new_bin_item)
                            break
            File(mod).rewrite(sbdef_data, 'Modify shared bin in sbdef file')
            File(mtpl_path).rewrite(mod_data, 'Modify shared bin in mtpl file')

    # def do_move_pin(self):
    #     """
    #     NOT used anymore!
    #
    #     Why do we need this?
    #         Skyline need .pin files in same folder as .soc file.
    #         The recipe has path to .soc file
    #
    #     We don't want to duplicate .pin file, so it is only in one area:
    #          Shared/BaseInputs/PinSoc/*.pin
    #     The .soc file is in:
    #          Shared/BaseInputs/PinSoc/<bom>/*.soc
    #
    #     :return: None
    #     """
    #     folder = f'Shared/BaseInputs/PinSoc/{self.bom}'
    #     if not isdir(folder):
    #         log.info(f'-i- Target folder [{folder}] does not exist. Cannot copy the .pin files.')
    #         return
    #
    #     for fname in glob.glob('Shared/BaseInputs/PinSoc/*.pin'):
    #         File(fname).copy(folder)

    def fulltp_only(self, onlylist):
        """
        This routine removes list of fulltp only modules (FBIST, Die to Die)
        for partial TP (CPU + GCD only)
        Overall flow:
        section1: check for validity (fulltp and mv json)
        section2: Read the fulltp module list from marker
        section3: write the skip module files: https://wiki.ith.intel.com/display/ITSpdxtp/MTL+Module+Skip
        """
        # Check if MV JSON file is used. Yes, then do nothing. No, continue.
        if onlylist is not None:
            return 1

        # Get current die combo info.
        curent_dielets = Integrate.get_valid_die()

        if len(curent_dielets) == 4:  # meaning full tp
            return 2  # do nothing

        # Get the list of modules in FULLTPONLY.
        config_folder = f'Shared/POR_TP/{self.bom}/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py'
        code = File(config_folder).read()

        testplan_modules = []
        for item in re.findall(r'^#\s+FULLTPONLY:\s+(\w+)', code, re.MULTILINE):
            testplan_modules.append(item)

        # Update skip module folder with the skip module list when TP is partial.
        folder2testplan = self.tpobj.mtpl.get_modfolder2mod()  # Get dict on module_foldername:module_testplanname.
        testplan2folder = reverse_keyval(folder2testplan)  # Reverse the above dict key and value.

        for testplanname in testplan_modules:
            foldername = testplan2folder[testplanname]  # this will raise exception if testplanname is not found
            log.info(f'-i- fulltp_only(): Adding SkipModules/{foldername}.txt')
            File(f'POR_TP/{self.bom}/SkipModules/{foldername}.txt').touch()  # Create skip_module.txt in folder

    def copy_pobj_cache(self):
        """Copy pobj cache to i:/ drive root"""
        if IS_UT:
            return 1
        if not isdir(self.root_pobj_cache):
            return 2     # root folder does not exist
        if not NVLBuildTP.JOBID:
            return 3     # not a botos run

        bomname = self.tpobj.get_bomfolder()
        templateroot = f'{self.root_pobj_cache}/template/{bomname}'
        if not isdir(templateroot):
            log.info(f'-i- pobj_cache is skipped since {templateroot} is missing.')
            return 4

        bomroot = f'{self.root_pobj_cache}/{bomname}/{NVLBuildTP.JOBID}'
        confirm(not isdir(bomroot), f'{bomroot} already exist', 'Pls contact jqdelosr - this should not happen')

        bomrootwip = f'{bomroot}.wip'
        mkdirs(bomrootwip)

        # copy the files
        for ff in (glob.glob(f'{self.tpobj.envdir}/PLIST_ALL*') +
                   glob.glob(f'{self.tpobj.shareddir}/BaseInputs/Common/Common_{bomname}/*.soc')):

            File(ff).copy(bomrootwip)

        # Use the env from template folder
        ktr = []    # keyword to replace
        for keyword in self.tpobj.env.get_env_dict():
            if 'PAT_PATH' in keyword or 'PLIST_PATH' in keyword:
                ktr.append(keyword)

        File(f'{templateroot}/EnvironmentFile.env').copy(bomrootwip)
        obj = Env(f'{bomrootwip}/EnvironmentFile.env')
        obj.set_env()
        for keyword in ktr:
            obj.set_item(keyword, self.tpobj.env.get_item(keyword))
        File(f'{bomrootwip}/EnvironmentFile.env').rewrite(obj.rebuild(), 'copy_pobj_cache()')

        # Done
        File(bomrootwip).rename(basename(bomroot))
        log.info(f'-i- pobj_cache: copied {len(os.listdir(bomroot))} files into {bomroot}')
        return bomroot

    @classmethod
    def create_dielet_sha(cls):
        """Write the dielet TP RepoRev.json"""
        sha_data = {}
        log.info('-i- Repo sha info/reporev (dielet):')
        dielet = basename(os.getcwd())
        sha_data[dielet] = CheckerLog.repo_sha[1]   # assumed populated
        for env_path in glob.glob(f'*_TP/*/EnvironmentFile.env'):
            sha_data['nvl.common'] = CheckerLog.get_folder_sha('Shared')    # This is a git submodule
            sha_data['tool'] = CheckerLog.get_tool_sha()
            mkdirs(f'{dirname(env_path)}/Reports')
            rev_report = f'{dirname(env_path)}/Reports/RepoRev.json'
            with open(rev_report, 'w') as f:
                json.dump(sha_data, f, indent=3)

        log.info(pformat(sha_data))

    @classmethod
    def id_labels(cls, modfiles):
        """
        :param modfiles: list of files
        :return: Set of labels
        """
        r_mod = re.compile(r'([^/]+)/(\w+Files)')
        r_special = re.compile('(BinDefinitions|BinMatrix|Uservar|EnvironmentFile|ProgramFlows)')
        result = set()
        for ff in modfiles:
            if ff.startswith('Modules'):
                res = r_mod.search(ff)     # with shared module
                if res:
                    result.add(res.group(1))
                    continue
                # shared submodule
                if basename(dirname(ff)) == 'Modules':
                    result.add(basename(ff))
                    continue
                # catch all
                result.add(basename(dirname(ff)))
            elif ff.startswith('Shared'):
                res = r_special.search(ff)
                if res:
                    result.add(res.group(1))
                    continue
                result.add('Shared')
            elif ff.startswith('POR_TP'):
                res = r_special.search(ff)
                if res:
                    result.add(res.group(1).replace('EnvironmentFile', 'EnvFile'))
                    continue
                result.add('PORTP')
            elif ff.startswith('.github'):
                result.add('YML')
            elif ff.startswith('TPConfig'):
                result.add('TPConfig')
            elif ff.startswith('UserCode'):
                result.add('UserCode')
            else:
                result.add('Misc')

        # Reduce labels if >4
        if len(result) > 4:
            reduced = set()
            for label in result:
                reduced.add(label.split('_')[0])
            return reduced

        return result

    def _torch_check_unix(self):
        """Error out if unix. This is a unittest hook, so we can mock"""
        confirm(IS_WIN,
                'Cannot run nvl_buildtp.py -torch from unix because it will call Torch api (windows only).',
                'Pls run from windows. ')

    def do_torch(self, genrecipe=True, tpbot=False):
        """
        Torch build, and recipes
        Call this for each dielet repo (common is not run because it is a folder inside dielet)
        """
        self.tpobj = TestProgram(self.env)
        self.tpobj.plists.error_out = False
        bom = self.bom

        # Call TPName1 update to build out correct recipe
        # NVLS356A0H01B00S528    ituff name matches with folder name
        # Temp work around to support per-BOM tpname. Torch and Spark need providing long term solution.
        nonprod_tpname = self.tpobj.usrv.get_var('PerBomTPNameVars.PerBomTPName1', default='NVLS756A0H01A0ZS501')
        if NVLBuildTP.tpname is None:    # This is for MV or standard TPBuild, to put correct TPName
            Usrv.update_usrv(f'Shared/BaseInputs/Common/Common_Files/common.usrv',
                             'TPName1', nonprod_tpname)
        else:
            Usrv.update_usrv(f'Shared/BaseInputs/Common/Common_Files/common.usrv',
                             'TPName1', NVLBuildTP.tpname)

        if tpbot:
            log.info('-i- do_torch(): tpbot=True, skipping Torch build, recipes and reports.')
            return 1

        sln_file = glob_one_only('*.sln')        # This may change if we have multiple .sln per bom
        tpproj_file = glob_one_only(f'POR_TP/{bom}/*.tpproj')

        self._torch_check_unix()

        confirm(sln_file,
                f'No .sln file found in {os.getcwd()}',
                f'This file is required for tp export.')

        # Call Torch build
        sw = Elapsed()
        lang_server = 'I:/tpapps/TORCH/Prod22/LanguageServer'
        cmd = f'{DoMV.get_torch_exe()} build -s {sln_file} -p {tpproj_file} -l {lang_server} --maxParallel 4 --ms "/p:Configuration={bom}"'
        code, sout, serr = SystemCall(cmd, disp=False).run_sout_serr(60 * 5)    # 5 min timeout
        out = f'{sout}\n{serr}'
        edata, wdata, udata = DoMV.build_process_txt(out)

        confirm(tpproj_file.startswith('POR_TP'), f'Expecting {tpproj_file} to start with POR_TP', 'Pls check code!')
        File(f'{dirname(tpproj_file)}/Reports/build_errors.txt').touch(out, newfile=True, mkdir=True)
        log.info(f'TorchBuild exitcode={code}, error={len(edata)}, unknown={len(udata)}, elapsed={sw}')

        # Call Recipe
        if genrecipe and not NVLBuildTP.QUICKBUILD:
            sw = Elapsed()
            cmd = f'{DoMV.get_torch_exe()} create-recipes --sln-config {bom} -s {sln_file} -p {tpproj_file} -d .'
            code, sout, serr = SystemCall(cmd, disp=True).run_sout_serr()
            confirm(not code, f'Recipe Command failed: {cmd}', 'Check output above.')
            log.info(f'recipe is complete in {sw}')

        # Call various reports
        for report in 'create-bin-report create-counter-report create-integration-report create-patlist-instance-report create-ltl-report'.split():
            if NVLBuildTP.QUICKBUILD:
                continue  # Do not generate any report for QUICKBUILD ENABLED STEP
            sw = Elapsed()
            cmd = f'{DoMV.get_torch_exe()} {report} --sln-config {bom} -s {sln_file} -p {tpproj_file} -d .'
            code, sout, serr = SystemCall(cmd, disp=True).run_sout_serr()
            confirm(not code, f'Recipe Command failed: {cmd}', 'Check output above.')
            log.info(f'{report} is complete in {sw}')

        # List of valid commands:
        # Copyright Ac Intel Corporation 2022
        #
        #   fix-tp                            Fix test program errors.
        #
        #   build                             Build Torch test program solution or projects. Requires the Torch language server (see the "install" command).
        #
        #   create-rules-report               Create Rules Report.
        #
        #   create-recipes                    Create recipes.
        #
        #   generate-soc-translated-env       Create new env file(s) with pre translated patterns paths.
        #
        #   create-patlist-instance-report    Create Patlist Instance Report
        #
        #   update-mtt                        Fix update MTT bins and counters for all the mtpl that use info from the flow matrix file.
        #
        #   create-ltl-report                 Generates LTL files
        #
        #   create-integration-report         Create Integration Report.
        #
        #   install                           Install Torch build language server (required before running the "build" command).
        #
        #   export-tp                         Export test program.
        #
        #   duplicate-tp                      Duplicate test program.
        #
        #   create-counter-report             Create Counter Report.
        #
        #   create-bin-report                 Create Binning Report.
        #
        #   publish-mtl                       Publish MTL file.
        #
        #   publish-check                     Publish CHECK file.
        #
        #   import-tokens                     The command will create a tokens json file from a csv file.
        #
        #   export-tokens                     The command will create a csv file from a json token file.
        #
        #   help                              Display more information on a specific command.
        #
        #   version                           Display version information.


class Clone:

    def __init__(self, bom='none'):
        self.bom = bom

    def main(self):
        """
        This is for full tp build, called from common repo and dielet repo.
        Call git clone command for all the dielets (except the current dielet if in dielet repo)
        Use token for runner and no token for non-runner (use credentials of user)
        """

        # Determine the root path
        # Normally github do the clone in: D:\nvl_common_vsgatcha_01\actions-runner\_work\nvl.common\nvl.common
        # We want dielet repos in:         D:\nvl_common_vsgatcha_01\actions-runner\nvl.cpu
        log.info('-i- ##### Clone.main()')
        root = '../../../'                 # relative to actions runner path
        from_runner = True
        is_common_repo = bool(not isdir('Shared'))
        if not os.path.isdir(f'{root}/_work'):    # the script was run outside of github
            root = '../'
            from_runner = False

        cwd = os.getcwd()
        log.info(f'-i- current work dir: {cwd}')
        log.info(f'-i- root:             {root}')
        dielets = ['nvl.cpu', 'nvl.hub', 'nvl.gcd', 'nvl.pcd']

        if 'nvl.common' not in cwd:
            # check which dielet repo we are in
            dielet = os.path.basename(cwd)
            if dielet in dielets:
                dielets.remove(dielet)

        with Chdir(root):

            # step1: Clone first
            for dielet in dielets:
                sw = Elapsed()
                # cwd - D:\nvl_common_vsgatcha_01\actions-runner\_work\nvl.common\nvl.common
                # Chdir will place us in D:\nvl_common_vsgatcha_01\actions-runner
                # wordir is - D:\nvl_common_vsgatcha_01\actions-runner\nvl.cpu
                workdir = os.path.join(cwd, root, dielet)
                workdir_abs = os.path.abspath(workdir)
                log.info(f'-i- Checking if {workdir_abs} exists for {dielet}')
                if exists(os.path.join(workdir_abs, '.git')) and exists(os.path.join(workdir_abs, 'Shared', '.git')):
                    log.info(f'-i- {workdir_abs} exists, skip clone of {dielet}')
                    continue    # already cloned
                else:
                    log.info(f'-i- {workdir_abs} does not exist, proceed to clone {dielet}')
                    # remove existing dielet folder if exist
                    check_and_del(dielet, mv_on_error=True)
                    log.info(f'-i- ################ Start clone {dielet}')
                    confirm(dielet in BuildCommon.repomap, f'{dielet} does not exist in repomap', 'Pls fix code')

                    # remove the token from url if non-runner
                    if from_runner:
                        url = BuildCommon.repomap[dielet]
                    else:
                        url = BuildCommon.repomap[dielet].replace(f'{BuildCommon.tok2}@', '')

                    # call the git clone command
                    SystemCall(f'git clone --recurse-submodules {url}').run(disp=True)    # this will create nvl.cpu folder
                    log.info(f'-z- clone Elapsed: {sw}')

            # step2: Make sure it is clean-state
            for dielet in dielets:
                with Chdir(dielet):
                    log.info(f'-i- ################ Start clean-state-check of {dielet}: {os.getcwd()}')
                    tprobot = TPRobot()

                    # set to correct branch in dielet
                    if 'IS_PR_COMMON' in os.environ or 'CHECKER_FULLTP' in os.environ:
                        # PR mode
                        with Chdir(cwd):
                            diebranch = self.get_branch_from_env(dielet, self.bom)
                            tprobot.arg1 = BuildCommon.get_branch(dielet, diebranch)
                    else:
                        # tpbuild mode
                        tprobot.arg1 = self.get_branch_from_env(dielet, self.bom)

                    log.info(f'-i- branch to use for {dielet}: {tprobot.arg1}')
                    tprobot.repo_init_check2()

            # step3: delete the target dielet repo for non-common, and copy from github cwd
            if from_runner and (not is_common_repo):
                dielet = os.path.basename(cwd)
                log.info(f'-i- Deleting {os.getcwd()}/{dielet}')
                check_and_del(dielet, mv_on_error=True)
                log.info(f'-i- Copy {cwd} to {os.getcwd()}/{dielet}')
                shutil.copytree(cwd, dielet, ignore=lambda *x: ['temp'])

                with Chdir(cwd):
                    brname = Clone.get_common_brname(self.bom)
                with Chdir(f'{cwd}/Shared'):
                    SystemCall(f'git checkout {brname}').run(disp=True)
                    SystemCall(f'git fetch').run(disp=True)
                    SystemCall(f'git pull').run(disp=True)
                    log.info(f'-i- {dielet} Shared sha: {CheckerLog.get_folder_sha(".")}')

            # step4: Update Shared/ sha to target common
            for dielet in dielets:
                if is_common_repo:

                    # Copy the _work to Shared, only copy if that is the common repo.
                    log.info(f'-i- {dielet} Shared sha: {CheckerLog.get_folder_sha(cwd)}')
                    with Chdir(dielet):
                        log.info(f'-i- Start copy of _work to Shared {dielet}: {os.getcwd()}')
                        check_and_del('Shared', mv_on_error=True)
                        shutil.copytree(cwd, 'Shared', ignore=lambda *x: ['.git', 'temp'])

                else:
                    with Chdir(dielet):
                        brname = Clone.get_common_brname(self.bom)
                    with Chdir(f'{dielet}/Shared'):
                        SystemCall(f'git checkout {brname}').run(disp=True)
                        SystemCall(f'git fetch').run(disp=True)
                        SystemCall(f'git pull').run(disp=True)
                        log.info(f'-i- {dielet} Shared sha: {CheckerLog.get_folder_sha(".")}')

    @classmethod
    def get_common_brname(cls, bom):
        """
        Return the mainline branch name to use for common

        Strategy:
        1. For "RC" branch, all dielet + common must have same branch names
        2. dielet repo's POR_TP/{bom}/InputFiles/common_main_name.txt will specify which common main to use  (dielet-tp build)
        3. common repo's POR_TP/{bom}/InputFiles/dielet_main_name.txt is used per BOM, used in get_branch_from_env() (full-tp build)
        """

        # Rule for RC branch: all dielet + common must have same main_RC_01B so script knows which common sha (BASE_REF)
        baseref = os.environ.get('BASE_REF', 'main')
        if baseref.startswith('main_RC'):
            return baseref       # return same name as with BASE_REF branch

        # A particular BOM may have different common main (eg. hx)
        target = f'POR_TP/{bom}/InputFiles/common_main_name.txt'     # see docstring for strategy.
        if exists(target):
            log.info(f'-i- Using {target}')
            return File(target).read().strip()
        else:
            return 'main'    # default

    @classmethod
    def get_branch_from_env(cls, dielet, bom):
        """
        Get the branch name for this dielet + bom

        :param dielet: nvl.cpu, etc
        :param bom: bom folder name
        :return: branch name
        """
        # os.environ name (used in yml) to dielet mapping
        mapping = {'nvl.cpu': 'CPU_Branch',
                   'nvl.gcd': 'GCD_Branch',
                   'nvl.pcd': 'PCD_Branch',
                   'nvl.hub': 'HUB_Branch',
                   }

        # main line default names: Strategy: use "main" for active continuous development.
        default = {'nvl.cpu': 'main',
                   'nvl.gcd': 'main',
                   'nvl.pcd': 'main',
                   'nvl.hub': 'main'
                   }

        # step1: check if yml specified os.environ first. Aka, "User input". Used with tpbuild.
        env_name = mapping[dielet]
        if os.environ.get(env_name, 'none') != 'none':
            return os.environ[env_name]

        # step2: rule for RC branch: all dielet + common must have same main_RC_01B so script knows which common sha (BASE_REF)
        baseref = os.environ.get('BASE_REF', 'main')      # This is caller BASE_REF, which is common repo for this case
        if baseref.startswith('main_RC'):
            return baseref       # return same name as with BASE_REF branch

        # step3: check the repo mainline default (used with main_h)
        main_fname = f'POR_TP/{bom}/InputFiles/{dielet}.main_name.txt'
        if exists(main_fname):
            log.info(f'-i- Using {main_fname}')
            return File(main_fname).read().strip()

        # default mainline per repo
        return default[dielet]


class PlistFullTP:
    """Combine the plist to create the fulltp"""

    def __init__(self):
        self.ipplists = OrderedDict()

    def main(self, bom):
        """
        Entry point

        Get all dielet .plist, then put them together, keep the order (CPU->HUB->GDIE->PCD->COMMON)
        Remove duplicate
        Write it

        :return: a dictionary per ip
        """
        plist = {}             # {dielet: {ip|"main": <list_of_plist>}}
        filename = {}          # {dielet: filename}

        # step 1 - get all plist files from dielet
        for dielet in Integrate.get_valid_die() + ['com']:      # in order, last one is primary
            if dielet == 'com' and not Integrate.target_die:
                wildstring = f'_work/*com*/*/POR_TP/{bom}/PLIST_ALL_*.plist.xml'
            elif dielet == 'com' and Integrate.target_die:
                wildstring = f'{Integrate.target_die[0]}/Shared/POR_TP/{bom}/PLIST_ALL_*.plist.xml'
            else:
                wildstring = f'*{dielet}/POR_TP/{bom}/PLIST_ALL_*.plist.xml'
            plistfiles = glob.glob(wildstring)

            if not len(plistfiles):
                continue       # in cases of not all dielets are clones

            # assume 1 .plist per repo
            confirm(len(plistfiles) == 1,
                    f'Expecting 1 PLIST_ALL_*.plist.xml only: {plistfiles}',
                    f'Pls fix: {wildstring}')

            log.info(f'-i- Reading {plistfiles[0]}')
            plist[dielet] = {}
            plist[dielet]["main"], ipplist = self.read_plist(plistfiles[0])
            filename['main'] = basename(plistfiles[0])
            foldername = dirname(plistfiles[0])

            # step 2 - read all the ipplist
            for one_ip in ipplist:
                log.info(f'-i- Reading {one_ip}')
                plist[dielet][one_ip], _ = self.read_plist(ipplist[one_ip], foldername)
                filename[one_ip] = basename(ipplist[one_ip])

            self.ipplists.update(ipplist)

        # step 3 - combine all
        confirm('main' in filename,
                'No valid PLIST_ALL_*.plist.xml found in any of the repos',
                f'Pls check: {os.getcwd()}')
        final = {}      # {main|ip: <full_string>}
        for one_ip in ["main"] + list(self.ipplists):
            final[filename[one_ip]] = '\n'.join(self.merge_plist(plist, one_ip))

        return final

    def merge_plist(self, plist, one_ip):
        """
        Merge all of the plists from plist dict
        :param plist: {dielet: {ip|"main": <list_of_plist>}}
        :param one_ip: which ip
        :return: list of lines
        """
        merged = []
        for dielet in plist:
            if one_ip in plist[dielet]:
                for item in plist[dielet][one_ip]:
                    if item not in merged:
                        merged.append(item)

        result = ['<HdmtReferenceFile>']

        if one_ip == "main":
            for ip in self.ipplists:
                result.append(f'   <IPReference name="{ip}" path="{self.ipplists[ip]}" />')

        result.append('   <PList>')
        for item in merged:
            result.append(f'      <PListFile name="{item}" />')
        result.append('   </PList>')
        result.append('</HdmtReferenceFile>')

        return result

    def read_plist(self, fname, folder=''):
        """
        Read one dielet plist

        :param fname: plist filename
        :return: list of uniq plist
        """
        result = []

        r_ip = re.compile(r'<IPReference name="(\w+)" path="([^"]+)"')
        r_plist = re.compile(r'PListFile name="([^"]+)"')
        ipplists = OrderedDict()
        for line in File(join(folder, fname)).chomp():
            if not line.strip():
                continue     # empty line

            if line.strip() in ('<HdmtReferenceFile>', '<PList>', '</PList>', '</HdmtReferenceFile>'):
                continue     # we ignore this

            res = r_ip.search(line)
            if res:
                ipplists[res.group(1)] = res.group(2).replace('\\', '/')
                continue

            res = r_plist.search(line)
            if res:
                result.append(res.group(1))
                continue

            raise ErrorInput(f'Unknown line: [{line}]', f'Check {fname}')

        return result, ipplists


class StplFullTP:
    """Combine the stpl to create the fulltp"""

    def main(self, bom):
        """
        Entry point

        Get all dielet .stpl, then put them together, keep the order (CPU->HUB->GDIE->PCD->COMMON)
        COMMON stpl is the “full-tp-only” only modules… call this like a programflows full tp stpl
        Remove duplicate
        Write it

        :return: the final stpl string ready for writing
        """
        stpls = {}   # {dielet: {ip: {Common|Final|Modules: value }}}

        # step 1 - get all stpl files from dielet
        for dielet in Integrate.get_valid_die() + ['com']:
            if dielet == 'com' and not Integrate.target_die:
                wildstring = f'_work/*com*/*/POR_TP/{bom}/SubTestPlan.stpl'
            elif dielet == 'com' and Integrate.target_die:
                wildstring = f'{Integrate.target_die[0]}/Shared/POR_TP/{bom}/SubTestPlan.stpl'
            else:
                wildstring = f'*{dielet}/POR_TP/{bom}/SubTestPlan.stpl'
            stplfiles = glob.glob(wildstring)

            if not len(stplfiles):
                continue       # in cases of not all dielets are clones

            # assume 1 .stpl per repo
            confirm(len(stplfiles) == 1,
                    f'Expecting 1 SubTestPlan.stpl only: {stplfiles}',
                    f'Pls fix: {wildstring}')

            log.info(f'-i- Reading {stplfiles[0]}')
            stpls[dielet] = self.read_stpl(stplfiles[0])

        # step2 - combine all
        return '\n'.join(self.merge_stpl(stpls))

    def merge_stpl(self, stpls):
        """
        Iterator: Merge stpls together

        :param stpls: dictionary {dielet: {ip: {Common|Final|Modules: value }}}
        :return: final stpl lines
        """
        yield 'Version 1.0;'
        yield ''
        yield 'SubTestPlans'
        yield '{'

        # get all ip first
        allip = set()
        for dielet in stpls:
            for ip in stpls[dielet]:
                allip.add(ip)

        # add all ip in dielets so dict structure is standard
        for ip in allip:
            for dielet in stpls:
                if ip not in stpls[dielet]:
                    stpls[dielet][ip] = {}

        startip = False
        for ip in sorted(allip, key=lambda x: 'zzz' if x is None else x):
            if startip:
                yield '    }'

            startip = True
            if ip is None:
                indent = '    '
            else:
                yield f'    IPName {ip}'
                yield '    {'
                indent = '        '

            # Common line first
            result = set()
            for dielet in stpls:
                if 'Common' in stpls[dielet][ip]:
                    result.add(stpls[dielet][ip]['Common'])
            if result:    # common line is optional
                confirm(len(result) == 1,
                        f'Error: Expecting one Common line only: {result}',
                        f'Pls check .stpl dielets for {ip}')
                yield f'{indent}Common {result.pop()};'

            # Modules line next
            result = set()
            for dielet in stpls:
                if 'Modules' in stpls[dielet][ip]:
                    result.update(stpls[dielet][ip]['Modules'])
            for item in sorted(result, reverse=True):
                yield f'{indent}{item};'

            # Final line first
            result = set()
            for dielet in stpls:
                if 'Final' in stpls[dielet][ip]:
                    result.add(stpls[dielet][ip]['Final'])

            if result:
                confirm(len(result) == 1,
                        f'Error: Expecting one Final line only: {result}',
                        f'Pls check .stpl dielets for {ip}')
                yield f'{indent}Final {result.pop()};'

        yield '}'

    def read_stpl(self, fname):
        """
        Read one bom stpl

        :param fname: stpl
        :return:
        """
        result = {None: {'Modules': []}}   # {ip|None: {'Common|Final|Modules' = value|list}}

        r_ip = re.compile(r'^IPName\s+(\w+)')
        r_comfin = re.compile(r'^(Common|Final)\s+(\S+);')
        r_mtpl = re.compile(r'^(\S+.mtpl\S*);')
        ipname = None
        for lno, line in OtplFile(fname).readline():
            if line.startswith(('Version', '{', 'SubTestPlans')):
                continue

            if line == '}':
                ipname = None
                continue

            # ipname
            res = r_ip.search(line)
            if res:
                ipname = res.group(1)
                result[ipname] = {'Modules': []}
                continue

            # common or final
            res = r_comfin.search(line)
            if res:
                result[ipname][res.group(1)] = res.group(2)
                continue

            # module
            res = r_mtpl.search(line)
            if res:
                result[ipname]['Modules'].append(res.group(1))
                continue

            raise ErrorInput(f'Unknown line: [{line}]', f'Check {fname}')

        return result


class TplFullTP:
    """Combine the tpl to create the fulltp"""

    def main(self, bom):
        """
        Entry point

        Read all .tpl files, put it in a list, Write out the header, then write out uniq import lines
        Then, grab the rest of the lines from common BaseTestPlan.tpl

        Assumption: dielet and common BaseTestPlan.tpl are all the same except import lines.

        :return: the final tpl string ready for writing
        """
        tpls = {}   # {dielet: <list_of_lines>}

        # step 1 - get all stpl files from dielet
        for dielet in Integrate.get_valid_die() + ['com']:
            if dielet == 'com' and not Integrate.target_die:
                wildstring = f'_work/*com*/*/BaseTestPlan.tpl'
            elif dielet == 'com' and Integrate.target_die:
                wildstring = f'{Integrate.target_die[0]}/Shared/BaseTestPlan.tpl'
            else:
                wildstring = f'*{dielet}/BaseTestPlan.tpl'
            tplfiles = glob.glob(wildstring)

            if not len(tplfiles):
                continue       # in cases of not all dielets are clones

            # assume 1 .tpl per repo
            confirm(len(tplfiles) == 1,
                    f'Expecting 1 BaseTestPlan.tpl: {tplfiles}',
                    f'Pls fix: {wildstring}')

            log.info(f'-i- Reading {tplfiles[0]}')
            tpls[dielet] = File(tplfiles[0]).raw()

        # step2 - combine all
        return '\n'.join(self.merge_tpl(tpls))

    def merge_tpl(self, tpls):
        """
        Iterator: Merge tpls together

        Logic: There is a hardcoded header, then yield the import lines uniquely

        :param tpls: dictionary {dielet: <list_of_lines>}
        :return: final tpl lines
        """
        # Header
        yield 'Version 1.0;'
        yield ''
        yield 'ProgramStyle = Modular;'
        yield ''
        yield 'TestPlan BASE;'
        yield ''

        # return all uniq Import lines
        found = set()
        for dielet in ['com'] + list(reversed(Integrate.get_valid_die())):      # this specifies the order
            for line in tpls.get(dielet, []):
                if line.startswith('Import'):
                    if line in found:
                        continue      # it is already written
                    yield line.rstrip()
                    found.add(line)

        # return all the rest of the lines in com
        yield ' '     # empty line separator
        for line in tpls.get('com', []):
            if not line.strip():
                continue    # ignore empty lines
            if line.strip().startswith(('Import', 'Version', 'ProgramStyle', 'TestPlan')):
                continue     # ignore these, we have written already
            yield line.rstrip()


class EnvFullTP:
    """Combine the dielet env to create the fulltp"""

    def main(self, bom):
        """
        Entry point, we get all the env here
        Acts on current working directory.

        <cwd>/cpu_repo/<files>
        <cwd>/gdie_repo/<files>
        <cwd>/hub_repo/<files>
        <cwd>/pcd_repo/<files>
        <cwd>/common_repo/POR_TP/*/EnvironmentFile.env              # Used by d2d (fulltp only) and "base-only only TP for future"
        <cwd>/common_repo/BaseInputs/EnvironmentFile_Common.env     # <we still need this for NVL, similar ARL>

        Strategy:
        Read dielet ENV (GDIE->HUB->PCD->CPU), then read common env overwriting the keys,
             but appending the values (prior to last), and no duplicate
        Keep the order
        Code does not know whether it's a single value or multi-value, the variable has to be in common if we expect one value only.
        Write the env (in a string)

        Notes:
        1. original shell tp-disagg .env does not work with Torch (so we don't need stitching)
        2. Q3 tpdisagg POC only have EnvironmentFile.env per dielet, without a common .env file
        3. NVL POR solution is to have a EnvironmentFile.env per dielet + EnvironmentFile_Common.env
           similar to MTL.
           It is not a "tpdisagg" .env per-se, but fulltp stitch will create the full tp .env version.
        TODO: What do we need to put in EnvironmentFile_Common.env for NVL

        Returns the final env string
        """
        env_objs = []

        # check the bom first

        # step 1a - get all env files from dielet
        for dielet in Integrate.get_valid_die() + ['com']:      # process in this order (order matters!)
            if dielet == 'com' and not Integrate.target_die:
                wildstring = f'_work/*com*/*/POR_TP/{bom}/EnvironmentFile.env'
            elif dielet == 'com' and Integrate.target_die:
                wildstring = f'{Integrate.target_die[0]}/Shared/POR_TP/{bom}/EnvironmentFile.env'
            else:
                wildstring = f'*{dielet}/POR_TP/{bom}/EnvironmentFile.env'
            envfiles = glob.glob(wildstring)

            if not len(envfiles):
                continue       # in cases of not all dielets are clones

            # assume 1 .env per repo
            confirm(len(envfiles) == 1,
                    f'Expecting 1 EnvironmentFile.env only: {envfiles}',
                    f'Pls fix: {wildstring}')

            log.info(f'-i- Reading {envfiles[0]}')
            env_objs.append(Env(envfiles[0]))

        # step 1b - get common env, for now, just get it from cdie. common has to be last so it will take it
        #           We commented this since common env is a $include from dielet env. Thus, no "stitch" needed.
        # wildstring = f'_work/BaseInputs/EnvironmentFile_Common.env'
        # envfiles = glob.glob(wildstring)
        # confirm(len(envfiles) == 1,
        #         f'Expecting 1 EnvironmentFile_Common.env only: {envfiles}',
        #         f'Pls fix: {wildstring}')
        # log.info(f'-i- Reading {envfiles[0]}')
        # env_objs.append(Env(envfiles[0]))

        # step2 - process it
        final_env = {}
        for env in env_objs:
            denv = env.get_env_dict()
            for item in denv:
                final_env[item] = self.merge(final_env.get(item, denv[item]), denv[item])

        # step3 - create the final env
        confirm(len(env_objs) >= 2,
                f'Expecting at least two envs, Found: {[x.envfile for x in env_objs]}',
                'Check inputs.')
        env = env_objs[-2]    # Get the 2nd to last object, which is cpu
        for item in final_env:
            env.set_item(item, final_env[item])

        return env.rebuild()     # at this point cpu/POR_TP/*/EnvironmentFile.env is the merged one.

    def merge(self, orig, new):
        """
        Merge the contents of an env file
        Strategy: Any change to common, we update all dielets everytime  [simple]
        Append at 2nd to last item
        """
        origlist = Env.list_or_str(orig, True)
        newlist = Env.list_or_str(new, True)
        # print(f'origlist: {origlist}')
        # print(f'newlist: {newlist}')

        if ';' in orig:        # This identifies if the var is "append" or "override"
            # append
            for item in newlist:
                if item:                            # ignore empty
                    if item not in origlist:
                        origlist.insert(-1, item)
        else:
            # overwrite
            origlist = [new]

        return ';'.join(origlist)


class CSVCombiner:

    def __init__(self, output_file):
        self.output_file = output_file

    def get_csvfile_list(self, bom, csvfile_name):
        # Define a routine to get all csv file from dielet and com repo.
        csv_files = []
        for dielet in Integrate.get_valid_die() + ['com']:  # process in this order (order matters!)
            if dielet == 'com' and not Integrate.target_die:
                wildstring = f'_work/*com*/*/POR_TP/{bom}/Reports/{csvfile_name}.csv'
            elif dielet == 'com' and Integrate.target_die:
                wildstring = f'{Integrate.target_die[0]}/Shared/POR_TP/{bom}/Reports/{csvfile_name}.csv'
            else:
                wildstring = f'*{dielet}/POR_TP/{bom}/Reports/{csvfile_name}.csv'
            csvfiles = glob.glob(wildstring)

            if not len(csvfiles):
                continue  # in cases of not all dielets are cloned, or not a full TP so common's full TP only module won't show up

            # assume 1 .csv per repo
            confirm(len(csvfiles) == 1,
                    f'Expecting 1 Torch report csv file: {csvfiles}',
                    f'Pls fix: {wildstring}')

            log.info(f'-i- Reading {csvfiles[0]}')
            csv_files.append(csvfiles[0])

        return csv_files

    def main(self, bom, csvfile_name):

        # step 1 - get all csv files from dielet and com
        csv_files = self.get_csvfile_list(bom, csvfile_name)

        # step 2 - read all csv files
        header = ''
        lines = set()

        for csvfile in csv_files:
            start = True
            with open(csvfile, newline='', encoding='utf-8') as f:
                for line in f:
                    # make sure header is the same across csv
                    if start:
                        start = False
                        if not header:
                            header = line
                        else:
                            if header != line:
                                raise ErrorUser('header is not the same with previous file')
                    else:
                        lines.add(line)

        # step 3 - write merged csv file
        with open(self.output_file, "w", newline='', encoding='utf-8') as f:
            f.write(header)
            for line in sorted(lines):
                f.write(line)

        log.info(f'-i- Writing into {self.output_file}')

        return 9    # for unittest


class BuildCommon:
    tok1 = '6768705f376f577046573575676758503964697863306e374e7159545a716a6d776331556d67676a'
    tok2 = bytes.fromhex(tok1).decode()
    repomap = {'nvl.cpu': f'https://{tok2}@github.com/intel-restricted/nvl.cpu.git',
               'nvl.gcd': f'https://{tok2}@github.com/intel-restricted/nvl.gcd.git',
               'nvl.pcd': f'https://{tok2}@github.com/intel-restricted/nvl.pcd.git',
               'nvl.hub': f'https://{tok2}@github.com/intel-restricted/nvl.hub.git'}

    @classmethod
    def get_branch(cls, repo, defaultbranch):
        """
        Return the dielet branch to use
        The string keyword in PR description is:
        <repo> BRANCH: <branch_name>

        Example:
        nvl.cpu BRANCH: mybranch
        """
        desc = GitHub.get_pr_view_output()
        validrepos = list(cls.repomap) + ['nvl.common']
        for result in re.findall(rf'^\s*(\S+)\s+BRANCH:\s+(\S+)', desc, re.MULTILINE):
            frepo, branch = result
            valid = ','.join(validrepos)
            confirm(frepo in validrepos,
                    f'Invalid repo keyword: [{frepo} BRANCH:] in PR description',
                    f'Valid repo list: {valid}')
            if frepo == repo:
                return branch

        return defaultbranch


class Integrate:
    """
    Strategy:

        On dielet fulltp:
           <root>/nvl.cpu   << target die repo is copied into this folder, during Clone
           <root>/nvl.gcd
           <root>/nvl.pcd
           <root>/nvl.hub
           Shared/ is copied from target die repo

        On common fulltp:
           <root>/nvl.cpu
           <root>/nvl.gcd
           <root>/nvl.pcd
           <root>/nvl.hub
           Shared/ is copied from common die repo
    """

    target_die = []      # default empty - common

    def __init__(self, bom):
        self.bom = bom
        self.set_target_die()
        self.die_env_list = self.get_dielet_list()
        log.info(f'-i- Valid die list: {self.get_valid_die()}')
        confirm(self.die_env_list, f"No env found in {os.getcwd()} for bom={bom}",
                "check bom and/or the nvl repo checkout folders")

        # get comrepo
        if Integrate.target_die:
            # we are in a dielet repo checkout, so get the common env file from Shared
            log.info(f'-i- current work dir: {os.getcwd()} target_die={Integrate.target_die[0]}')
            wildstring = f'{Integrate.target_die[0]}/Shared/POR_TP/{self.bom}/EnvironmentFile.env'
            self.comenv = glob.glob(wildstring)
        else:
            # we are in a common repo checkout
            wildstring = f'_work/*com*/*/POR_TP/{self.bom}/EnvironmentFile.env'
            self.comenv = glob.glob(wildstring)

        confirm(len(self.comenv) == 1,
                f'Expecting 1 EnvironmentFile.env only: {self.comenv}',
                f'Pls check: {wildstring}')

    def main(self, outpath):
        """
        Main routine to stitch dielet TP together and output the files
        """
        sw = Elapsed()
        swtotal = Elapsed()

        # output folder must not exist
        confirm(not os.path.isdir(outpath),
                f'[{outpath}] already exist',
                'Pls make sure this path does not exist as it will be created')

        # Assumption: common + dielet msbuild is called prior to calling fulltp.py

        # step0 - get sha of repos
        log.info(f'cwd: {os.getcwd()}')
        log.info(f'comenv: {self.comenv[0]}')
        log.info(f'die_env_list: {self.die_env_list}')
        sha_repos = {'nvl.common': CheckerLog.get_folder_sha(self.diename(self.comenv[0])),
                     'tool': CheckerLog.get_tool_sha()}
        for dielet in self.die_env_list:
            sha_repos[basename(self.diename(dielet))] = CheckerLog.get_folder_sha(self.diename(dielet))
        log.info('-i- Repo sha info/reporev (fulltp):\n%s' % pformat(sha_repos))

        # step1 - copy initial/starting point: the first dielet into output
        log.info(f'-z- Step0 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        first_dielet = self.diename(self.die_env_list[-1])     # CPU dielet
        log.info(f"-i- Step1: Copying {first_dielet} first...")
        shutil.copytree(first_dielet, outpath, ignore=lambda *x: ['.git', 'temp'])
        shutil.rmtree(f'{outpath}/Modules')     # Delete Modules folder
        mkdirs(f'{outpath}/Modules')

        tpobj = {}
        for dielet in self.die_env_list:
            tpobj[dielet] = TestProgram(dielet)

        # step2a - Copy the Modules/ folder. We read the .stpl for module folder
        #          We error on overlap (guaranteed unique)
        log.info(f'-z- Step1 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        self.copy_modules(tpobj, outpath)

        # step2b - Copy the *.imp files
        log.info(f'-z- Step2a Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        for dielet in self.die_env_list[:-1]:
            for impfile in glob.glob(f'{tpobj[dielet].tpldir}/*.imp'):
                File(impfile).copy(outpath)

        # step2c - Copy the SkipModule files
        log.info(f'-z- Step2b Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        for dielet in self.die_env_list[:-1]:
            for skipfile in glob.glob(f'{tpobj[dielet].tpldir}/POR_TP/{self.bom}/SkipModules/*'):
                mkdirs(f'{outpath}/POR_TP/{self.bom}/SkipModules')
                File(skipfile).copy(f'{outpath}/POR_TP/{self.bom}/SkipModules')

        # step2d - Copy the BaseInput dielet
        log.info(f'-z- Step2c Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        for dielet in self.die_env_list[:-1]:
            for folder in glob.glob(f'{tpobj[dielet].tpldir}/BaseInputs/*'):
                if not isdir(folder):
                    continue       # Ignore non-folders
                shutil.copytree(folder, f'{outpath}/BaseInputs/{basename(folder)}')

        # step3 - Delete output/Shared (This is from step1)
        #         copy the com repo files into the output/Shared folder
        log.info(f'-z- Step2b+2c Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        compath = self.diename(self.comenv[0])
        log.info(f"-i- Step3: Copying {compath} to Shared")
        check_and_del(f'{outpath}/Shared', mv_on_error=True)
        shutil.copytree(compath, f'{outpath}/Shared', ignore=lambda *x: ['.git', 'temp'])
        rmtree(f'{outpath}/.git', ignore_error=True)    # Delete git folder

        # step3a: Create sha report
        for env_path in glob.glob(f'{outpath}/*/*/EnvironmentFile.env'):
            mkdirs(f'{dirname(env_path)}/Reports')
            with open(f'{dirname(env_path)}/Reports/RepoRev.json', 'w') as fh:
                json.dump(sha_repos, fh, indent=3)

        # step4 - Merge env file
        log.info(f'-z- Step3 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        envstring = EnvFullTP().main(self.bom)
        bomfolder = basename(dirname(self.comenv[0]))      # use the folder name from common
        File(f'{outpath}/POR_TP/{bomfolder}/EnvironmentFile.env').rewrite(envstring, 'Integrate.main()')

        # step5a - Merge stpl file
        log.info(f'-z- Step4 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        stplstring = StplFullTP().main(self.bom)
        File(f'{outpath}/POR_TP/{bomfolder}/SubTestPlan.stpl').rewrite(stplstring, 'Integrate.main()')

        # step5b - Merge tpl file
        log.info(f'-z- Step5a Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        tplstring = TplFullTP().main(self.bom)
        File(f'{outpath}/BaseTestPlan.tpl').rewrite(tplstring, 'Integrate.main()')

        # step6 - Update Dielet Indicator value for stitched TP
        log.info(f'-z- Step5b Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        Usrv.update_usrv(f'{outpath}/Shared/BaseInputs/Common/Common_Files/TOSRules.usrv',
                         'DIELET_INDICATOR',
                         ','.join([item.upper() for item in self.get_valid_die()]))

        # step7 - Merge plist files
        log.info(f'-z- Step6 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        plistdict = PlistFullTP().main(self.bom)
        for ip in plistdict:
            File(f'{outpath}/POR_TP/{bomfolder}/{ip}').rewrite(plistdict[ip], 'Integrate.main()')

        # step8 - Copy each ProgramFlowsTestPlan
        log.info(f'-z- Step7 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        for dielet in self.die_env_list + self.comenv:
            pfpath = f'{dirname(dielet)}/ProgramFlowsTestPlan'
            for fname in os.listdir(pfpath):
                if isdir(f'{pfpath}/{fname}'):    # ignore folders
                    continue
                File(f'{pfpath}/{fname}').copy(f'{outpath}/POR_TP/{bomfolder}/ProgramFlowsTestPlan')

        # step9 - Update TP name back to user input match ituff name.
        # Temp work around to support per-BOM tpname. Torch and Spark need providing long term solution.
        log.info(f'-z- Step9 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        self.update_tpname(tpobj, outpath)

        # step10 - execute Programflow after TP stitch
        with Chdir(f'{outpath}/POR_TP/{bomfolder}/ProgramFlowsTestPlan'):

            os.environ['DIE_LIST'] = self.get_die_from_env()
            log.info(f"-i- DIE_LIST={os.environ['DIE_LIST']}")

            # Command: I:/tpvalidation/engtools/tptools/mtl/beta/latest/main/pymtpl.py ../../../Shared/POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/ProgramFlows.py -env ../EnvironmentFile.env"
            log.info(f'-i- cwd: {os.getcwd()}')
            cmd = [f'{sys.executable}',
                   f'{dirname(CALLERBIN)}/pymtpl.py',
                   f'../../../Shared/POR_TP/{bomfolder}/ProgramFlowsTestPlan/ProgramFlows.py',
                   f'-env',
                   f'../EnvironmentFile.env']
            SystemCall(cmd).run(disp=True, exitout='pymtpl ProgramFlows.py failed')        # Cannot use Pymtpl() call here because of import issues on different BOMs

        # step11 - call csv stitching
        log.info(f'-z- Step11 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        # torch module_instances.csv
        csvfile_name_list = ['module_instances', 'patlist_instances']
        self.fulltp_moduleinstance_csv(outpath)    # generate report for fulltp-only module
        # stitch the csv files from list-csvfile_name together
        for csvfile in csvfile_name_list:
            CSVCombiner(f'{outpath}/POR_TP/{bomfolder}/Reports/{csvfile}.csv').main(bomfolder, csvfile)

        # step12 - delete unneeded POR_TP
        log.info(f'-z- Step12 Elapsed: {sw.elapsed(pretty=True, reset=True)}')
        delete_por_tp(outpath, bomfolder)

        # copy the TP to i:\drive if specified
        self.copy_to_idrive(outpath)

        log.info(f'-z- Integrate.main() fulltp stitch total Elapsed: {swtotal}')

    def copy_modules(self, tpobj, outpath):
        """
        Copy all Modules/<module>

        :param tpobj: tpobj dictionary
        :param outpath: output path
        :return:
        """
        for dielet in self.die_env_list:
            for mod in tpobj[dielet].get_all_mtpl_from_stpl():
                if '../Modules' in mod.replace('\\', '/'):
                    modfolder = dirname(mod)
                    log.info(f'-i- Step2: Copying Module {modfolder}')

                    if basename(dirname(modfolder)) == 'Modules':
                        shutil.copytree(modfolder, f'{outpath}/Modules/{basename(modfolder)}')
                    elif basename(dirname(dirname(modfolder))) == 'Modules':    # submodule with Team.
                        team = basename(dirname(modfolder))
                        mkdirs(f'{outpath}/Modules/{team}')
                        shutil.copytree(modfolder, f'{outpath}/Modules/{team}/{basename(modfolder)}')
                    else:   # pragma: no cover    - This block is a "catch" all for safety, no need to unittest this
                        raise ErrorInput(f'Unknown Modules/folder structure: {modfolder}',
                                         'Script only allows one level Module/')

    @classmethod
    def copy_to_idrive(cls, outpath):
        """
        Copy to idrive if specified in PR
        """
        if 'FROM_PR' in os.environ:
            with Chdir(os.environ['REPO_DIR']):
                desc = GitHub.get_pr_view_output()
            res = re.search(r'SAVE_TO_IDRIVE:\s+(\S+)', desc)
            if res:
                idrive = res.group(1)
                log.info('-i- Start copy to I: drive')
                log.info(f'-i- output={outpath}')
                log.info(f'-i- idrive={idrive}')
                with Chdir(outpath):
                    NVLBuildTP.copytp(idrive)
                return 1

            return 2

        return 3

    @classmethod
    def update_tpname(cls, tpobj, outpath):
        """Update the tpname"""
        firstdieletkey = sorted(tpobj)[0]
        nonprod_tpname = tpobj[firstdieletkey].usrv.get_var('PerBomTPNameVars.PerBomTPName1', default='NVLS756A0H01A0ZS501')
        if NVLBuildTP.tpname is None:    # This is for MV or standard TPBuild, to put correct TPName
            Usrv.update_usrv(f'{outpath}/Shared/BaseInputs/Common/Common_Files/common.usrv',
                             'TPName1', nonprod_tpname)
        else:
            Usrv.update_usrv(f'{outpath}/Shared/BaseInputs/Common/Common_Files/common.usrv',
                             'TPName1', NVLBuildTP.tpname)

    def fulltp_moduleinstance_csv(self, outpath):
        """
        Special routine for Torch to generate module instances/patlist report for common full TP only modules
        """
        # step 1 - Get current die combo info, if not full tp, do nothing
        curent_dielets = Integrate.get_valid_die()

        if not len(curent_dielets) == 4:  # meaning not full tp
            return 8  # do nothing

        # step 2 - copy fulltp programflows.mtpl from the dielet POR_TP to common POR_TP
        dielet_pfmtpl = f'{outpath}/POR_TP/{self.bom}/ProgramFlowsTestPlan/ProgramFlows.mtpl'
        pat_pfmtpl = f'_work/*com*/*/POR_TP/{self.bom}/ProgramFlowsTestPlan'
        com_pfmtpl = glob.glob(pat_pfmtpl)
        for pfmtpl in com_pfmtpl:
            shutil.copy2(dielet_pfmtpl, pfmtpl)

        # step 3 - Run Torch to generate the .csv file.
        pat_dir = f'_work/*com*/*'
        com_dir = glob.glob(pat_dir)
        for dir in com_dir:
            with Chdir(dir):
                # Command: I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe create-patlist-instance-report -s NVL_Common.sln -p POR_TP/Class_NVL_S28C/Class_NVL_S28C.tpproj -d .
                cmd = (f'{DoMV.get_torch_exe()} create-patlist-instance-report --sln-config {self.bom} -s '
                       f'NVL_Common.sln -p POR_TP/{self.bom}/{self.bom}.tpproj -d .')
                SystemCall(cmd).run(disp=True)    # exitout='Common repo Torch report generation failed')

        return 7

    @classmethod
    def set_target_die(cls):
        """Set the target die - None for common, repo die for dielet"""
        confirm(not Integrate.target_die, 'Expecting target_die to be empty. Cannot call this twice', 'Cockpit error')

        if 'CHECKER_FULLTP' in os.environ:      # This is only set for dielet tp
            Integrate.target_die.append(basename(os.environ['REPO_DIR']))

    @classmethod
    def get_valid_die(cls):
        """Return list of valid die"""
        valid_die_list = cls.get_die_from_env()
        result = []

        original = "gcd hub pcd cpu".split()      # Do not change this order! last one will override same-filenames from previous.

        if Integrate.target_die:

            target = Integrate.target_die[0].split('.')[-1]
            die_order = []
            for dielet in original:
                if dielet != target:
                    die_order.append(dielet)

            # target is last, since this is the copy
            die_order.append(target)

        else:
            die_order = original

        for dielet in die_order:
            if dielet.upper() not in valid_die_list:
                continue      # This die is not valid
            result.append(dielet)

        return result

    def get_dielet_list(self):
        """Return list of dielet env files"""
        result = []
        for dielet in self.get_valid_die():
            wildstring = f'*{dielet}/POR_TP/{self.bom}/EnvironmentFile.env'
            envfiles = glob.glob(wildstring)

            if not len(envfiles):
                continue       # in cases of not all dielets are clones

            # assume 1 .env per repo
            confirm(len(envfiles) == 1,
                    f'Expecting 1 EnvironmentFile.env only: {envfiles}',
                    f'Pls check: {wildstring}')

            result.append(envfiles[0])

        return result

    def diename(self, path):
        """Return the root die repo path"""
        return dirname(dirname(dirname(path)))      # /path/nvl.cpu

    @classmethod
    def get_die_from_env(cls):
        """Return the CPU,GCD,HUB,PCD based on env var"""
        mapping = {'CPU_Branch': 'CPU',
                   'GCD_Branch': 'GCD',
                   'PCD_Branch': 'PCD',
                   'HUB_Branch': 'HUB'
                   }

        result = []
        for envname in sorted(mapping):
            if os.environ.get(envname, 'main') != 'none':
                result.append(mapping[envname])
        return ','.join(result)


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    NVLBuildTPEntry(desc=__doc__).main()


# Status as of Feb 21:
# Torch fixer: failed due to Error: Object reference not set to an instance of an object.
# Recipe:  2nd repo recipe failed Error: Invalid bom group configuration found. Does not contain {FuseRootDir} replacement value
# Various reports: Class_NVL_28C.tpconfig(2,1): error MSB4068: The element <Configuration> is unrecognized, or not supported in this context
