#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_buildtp
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock, MagicMock
from gadget.gizmo import MockVar, with_
from gadget.disk import Allfiles
from gadget.helperclass import CaptureStdoutLog
from gadget.errors import ErrorUser
from gadget.shell import IS_UNIX
from mod.tpswitch import TPSwitch
from main.nvl_buildtp import *
import main.nvl_buildtp as nvl_buildtp
from pprint import pprint, pformat
from tp.testprogram import Env, Usrv
from main.runner_botos import RunnerBotOS
from unittest.mock import Mock, patch
import sys
import csv


class TestFlow(TestCase):

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    @with_(MockVar, NVLBuildTP, 'create_dielet_sha', Mock())
    @with_(MockVar, NVLBuildTP, 'update_shared_sha_latest', Mock())
    def test_main_flow_dielet(self):
        # Create .sln file that will be copied to tempdir
        File('NVL_CPU.sln').touch()
        File('POR_TP/TGLH81/dummy.tpproj').touch(mkdir=True)  # do_torch also needs .tpproj

        called = []

        def fake(*args, **kwargs):
            if 'object' in str(args[0]):
                called.append(args[1:])
            else:
                called.append(args)

        with TempDir(name=True) as outdir:

            # ===== dielet TP, no output
            cmd = 'nvl_buildtp.py None -flow'.split()
            with MockVar(MSBuild, 'main', Mock()), \
                    MockVar(RunnerBotOS, 'affected_boms', Mock(return_value=['TGLH81'])), \
                    MockVar(NVLBuildTP, 'do_torch', fake), \
                    MockVar(NVLBuildTP, 'main', fake), \
                    MockVar(sys, "argv", cmd):
                NVLBuildTPEntry().main()
                self.assertEqual(called, [(),  # do_torch(),
                                          ()])  # main()
                self.assertEqual(os.listdir(outdir), [])

            # ===== dielet TP, with output
            cmd = f'nvl_buildtp.py None -flow -out {outdir}/out'.split()
            with MockVar(MSBuild, 'main', Mock()), \
                    MockVar(RunnerBotOS, 'affected_boms', Mock(return_value=['TGLH81'])), \
                    MockVar(NVLBuildTP, 'do_torch', fake), \
                    MockVar(NVLBuildTP, 'main', fake), \
                    MockVar(sys, "argv", cmd):
                NVLBuildTPEntry().main()
                self.assertEqual(os.listdir(outdir), [])  # output is copied by main(), which is mocked

            # ===== dielet TP, tpbot run (do_torch will fail if we dont have tpbot)
            check_and_del(f'{outdir}/out')
            cmd = f'nvl_buildtp.py None -flow -tpbot'.split()
            with MockVar(MSBuild, 'main', Mock()), \
                    MockVar(RunnerBotOS, 'affected_boms', Mock(return_value=['TGLH81'])), \
                    MockVar(NVLBuildTP, 'do_torch', fake), \
                    MockVar(NVLBuildTP, 'main', fake), \
                    MockVar(sys, "argv", cmd):
                File('NVL_CPU.sln').touch()
                NVLBuildTPEntry().main()
                self.assertEqual(os.listdir(outdir), [])

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple_disagg2a')
    def test_main_flow_common(self):
        # test common
        File('nvl_cpu').rename('nvl.cpu')
        File('nvl_gcd').rename('nvl.gcd')
        File('nvl_hub').rename('nvl.hub')
        File('nvl_pcd').rename('nvl.pcd')

        called = []
        dielets = []

        def fake(*args):
            if 'object' in str(args[0]):
                called.append(args[1:])
            else:
                called.append(args)

        def fake_do_torch(slf, **kwargs):
            dielets.append(basename(os.getcwd()))

        with TempDir(name=True) as outdir:

            def fakeintegrate(slf, outx):
                shutil.copytree(f'{UT_DIR_REPO}/SimpleNVL', outx)
                File(f'{outx}/POR_TP/TGLH81').rename('class_nvl_28c')

            # ===== common TP
            cmd = f'nvl_buildtp.py None -flow -common -out {outdir}/out'.split()
            with MockVar(MSBuild, 'main', Mock()), \
                    MockVar(RunnerBotOS, 'affected_boms', Mock(return_value=['class_nvl_28c'])), \
                    MockVar(NVLBuildTP, 'do_torch', fake_do_torch), \
                    MockVar(NVLBuildTP, 'main', fake), \
                    MockVar(NVLBuildTP, 'update_shared_sha_latest', Mock()), \
                    MockVar(sys, "argv", cmd), \
                    MockVar(Integrate, '__init__', MagicMock(return_value=None)), \
                    MockVar(Integrate, 'main', fakeintegrate), \
                    Chdir('_work/com/com'):
                NVLBuildTPEntry().main()
                self.assertEqual(os.listdir(outdir), [])      # main() will do the copying, but it is mocked
                self.assertEqual(dielets, ['nvl.cpu', 'nvl.gcd', 'nvl.pcd', 'nvl.hub'])

            # ===== common TP, tpbot run (do_torch will fail if we dont have tpbot)
            check_and_del(f'{outdir}/out')
            cmd = f'nvl_buildtp.py None -flow -common -out {outdir}/out -tpbot'.split()
            with MockVar(MSBuild, 'main', Mock()), \
                    MockVar(RunnerBotOS, 'affected_boms', Mock(return_value=['class_nvl_28c'])), \
                    MockVar(NVLBuildTP, 'do_torch', fake_do_torch), \
                    MockVar(NVLBuildTP, 'main', fake), \
                    MockVar(NVLBuildTP, 'update_shared_sha_latest', Mock()), \
                    MockVar(sys, "argv", cmd), \
                    MockVar(Integrate, '__init__', MagicMock(return_value=None)), \
                    MockVar(Integrate, 'main', fakeintegrate), \
                    Chdir('_work/com/com'):
                NVLBuildTPEntry().main()
                self.assertEqual(os.listdir(outdir), [])   # main() will do the copying, but it is mocked

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple_disagg2a')
    def test_onebomflow_common(self):
        # test onebomflow_common
        File('nvl_cpu').rename('nvl.cpu')
        File('nvl_gcd').rename('nvl.gcd')
        File('nvl_hub').rename('nvl.hub')
        File('nvl_pcd').rename('nvl.pcd')

        called = []
        dielets = []

        def fake(*args):
            if 'object' in str(args[0]):
                called.append(args[1:])
            else:
                called.append(args)

        def fake_do_torch(slf, **kwargs):
            dielets.append(basename(os.getcwd()))

        with TempDir(name=True) as onebomflow_tdir, TempDir(name=True) as onebomflow_outdir:
            def fakeintegrate(slf, outx):
                shutil.copytree(f'{UT_DIR_REPO}/SimpleNVL', outx)
                File(f'{outx}/POR_TP/TGLH81').rename('class_nvl_28c')

            cmd = f"nvl_buildtp.py class_nvl_28c -onebomflow -common -out {os.path.join(onebomflow_outdir, 'out')} -tdir {onebomflow_tdir}".split()
            with MockVar(MSBuild, 'main', Mock()), \
                    MockVar(NVLBuildTP, 'do_torch', fake_do_torch), \
                    MockVar(NVLBuildTP, 'main', fake), \
                    MockVar(NVLBuildTP, 'update_shared_sha_latest', Mock()), \
                    MockVar(sys, "argv", cmd), \
                    MockVar(Integrate, '__init__', MagicMock(return_value=None)), \
                    MockVar(Integrate, 'main', fakeintegrate), \
                    Chdir('_work/com/com'):
                NVLBuildTPEntry().main()
                self.assertEqual(os.listdir(onebomflow_outdir), [])      # main() will do the copying, but it is mocked
                self.assertEqual(dielets, ['nvl.cpu', 'nvl.gcd', 'nvl.pcd', 'nvl.hub'])

    def test_main_flow_exception(self):

        def fake(*args, **kwargs):
            # just copy the testprogram to tempdir folder
            tdir = kwargs['tempdir']
            os.rmdir(tdir)
            shutil.copytree(f'{UT_DIR_REPO}/SimpleNVL', tdir)
            raise ValueError('blah')       # exception happened

        with TempDir(name=True) as outdir:
            with MockVar(NVLBuildTP, 'main_flow_onebom', fake):
                with self.assertRaises(ValueError):
                    NVLBuildTP.main_flow(False, False, f'{outdir}/out', 'TGLH81')

            self.assertEqual([Env.xpath(x) for x in glob.glob(f'{outdir}/out/*POR*/*/*.env')],
                             [Env.xpath(f'{outdir}/out/POR_TP_FAILED/TGLH81/EnvironmentFile.env')])


class TestZ_BuildCommon(TestCase):

    def test_get_branch(self):
        text = """
some line
   nvl.cpu BRANCH: jdr
some line
"""
        # pass case
        with MockVar(GitHub, 'get_pr_view_output', Mock(return_value=text)):
            self.assertEqual(BuildCommon.get_branch('nvl.cpu', 'def'), 'jdr')

        # default case
        with MockVar(GitHub, 'get_pr_view_output', Mock(return_value=text)):
            self.assertEqual(BuildCommon.get_branch('nvl.qqq', 'def'), 'def')

        # invalid case
        text2 = """
nvl.qqq BRANCH: jdr
"""
        with MockVar(GitHub, 'get_pr_view_output', Mock(return_value=text2)):
            with self.assertRaisesRegex(ErrorUser, 'Invalid repo keyword'):
                BuildCommon.get_branch('nvl.qqq', 'def')


class TestBuild(TestCase):

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_integ1(self):
        # First run - basic
        cmd = 'nvl_buildtp.py TGLH81'.split()
        with MockVar(sys, "argv", cmd), \
                CaptureStdoutLog() as p:
            NVLBuildTPEntry().main()      # must be passing

        self.assertEqual('START: QGate() checkers' in p.getvalue(), True)
        self.assertEqual(len(list(File('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').chomp())), 10)   # compare this to test_integ2

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_integ2(self):
        # with PinSoc
        # MV run
        mkdirs('Shared/BaseInputs/PinSoc/TGLH81')
        File('Shared/BaseInputs/PinSoc/somepin.pin').touch()
        modtxt = '''
[
    {
        "name": "ARR1",
        "modules": [
            "ARR"
        ],
        "config_imports": []
    }
]
'''
        File('TPConfig/MV_Templates/ARR1.json').touch(modtxt, mkdir=True)
        cmd = 'nvl_buildtp.py TGLH81'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(os.environ, 'IN1', 'ARR1'):
            NVLBuildTPEntry().main()      # must be passing

        # check that MV is executed
        print('====== stpl contents:')
        print(File('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').read())
        self.assertEqual(len(list(File('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').chomp())), 8)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_integ3(self):
        # test exportonly
        cmd = 'nvl_buildtp.py TGLH81 -output output'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(os.environ, 'IN1', 'EXPORTONLY:FULL'), \
                CaptureStdoutLog() as p:
            NVLBuildTPEntry().main()
        expect = r'copytp\(\) to idrive \[output\], Elapsed [\d.]+ Secs'

        self.assertRegex(p.getvalue(), expect)

    @with_(TempDir, chdir=True, delete=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_integ4(self):
        # test PREVIOUSTP
        with TempDir(name=True, delete=True) as outdir:
            cmd = f'nvl_buildtp.py TGLH81 -output {os.path.realpath(outdir)}'.split()
            with MockVar(sys, "argv", cmd), \
                    MockVar(os.environ, 'PREVIOUSTP', 'PREVIOUSTP'), \
                    MockVar(os.environ, 'DEST', 'MTLXXXXC2H39V00S517'), \
                    MockVar(NVLBuildTP, 'current_tp', 'SimpleNVL'), \
                    patch('main.nvl_buildtp.main_pr_integrate', Mock()), \
                    CaptureStdoutLog() as p:
                NVLBuildTPEntry().main()
        expect = r'QGate total Elapsed: [\d.]+ Secs'
        self.assertRegex(p.getvalue(), expect)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_integ_npr_trigger(self):
        # Integration test: NPRTrigger is constructed (line 338), .main(True, outdir) is called (line 339),
        # and .wait() is called unconditionally after the full pipeline (line 369).
        call_log = []

        def fake_npr_main(self_npr, nprtrigger, outdir=None):
            call_log.append(('main', nprtrigger, outdir))
            return 2   # return 2 = outdir not provided to trigger, fast exit

        def fake_npr_wait(self_npr):
            call_log.append(('wait',))

        with TempDir(name=True) as outdir:
            real_outdir = os.path.realpath(outdir)
            cmd = f'nvl_buildtp.py TGLH81 -output {real_outdir}'.split()
            with MockVar(sys, 'argv', cmd), \
                    MockVar(NPRTrigger, 'main', fake_npr_main), \
                    MockVar(NPRTrigger, 'wait', fake_npr_wait), \
                    CaptureStdoutLog() as p:
                NVLBuildTPEntry().main()

        # Verify NPRTrigger.main(True, outdir) was called — covers lines 338-339
        self.assertIn(('main', True, real_outdir), call_log)

        # Verify NPRTrigger.wait() was called after the full pipeline — covers line 369
        self.assertIn(('wait',), call_log)

        # Verify wait() came AFTER main() in the call sequence
        main_idx = call_log.index(('main', True, real_outdir))
        wait_idx = call_log.index(('wait',))
        self.assertLess(main_idx, wait_idx, 'wait() must be called after main() in the pipeline')

        # Verify the full pipeline ran to completion (QGate confirms wait is truly at the end)
        self.assertRegex(p.getvalue(), r'START: QGate\(\) checkers')

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_quickbuild_mode(self):
        # Test that main_quickbuild is called when QUICKBUILD=true
        cmd = 'nvl_buildtp.py TGLH81 -output output'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(os.environ, 'QUICKBUILD', 'true'), \
                MockVar(DataHost, 'central', Mock(return_value=(0, '', ''))), \
                CaptureStdoutLog() as p:
            NVLBuildTPEntry().main()

        # Verify QUICKBUILD mode was enabled in NVLBuildTPEntry.main()
        self.assertRegex(p.getvalue(), r'QUICKBUILD mode is ENABLED')

        # Verify the quickbuild-specific log messages appear (from main_quickbuild)
        self.assertRegex(p.getvalue(), r'===== QUICKBUILD mode: Starting reduced postprocessing =====')
        self.assertRegex(p.getvalue(), r'===== QUICKBUILD mode: Skipped FSM, RecipeEdit, MtplNewLine, TPSwitch, QGate, PyQS =====')

        # Verify full build steps are NOT executed (these only appear in regular main())
        self.assertNotRegex(p.getvalue(), r'START: QGate\(\) checkers')
        self.assertNotRegex(p.getvalue(), r'START: RecipeEdit')

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_inits(self):
        # tests the init values

        # ===== default, aka "FULL"
        obj = NVLBuildTP('TGLH81')
        self.assertEqual(obj.outdir, None)
        self.assertEqual(obj.which, 'FULL')
        self.assertEqual(obj.tpname, None)
        self.assertEqual(obj.isval, False)
        self.assertEqual(obj.export_only, False)

        # ===== exportonly
        with MockVar(os.environ, 'IN1', 'EXPORTONLY:FULL'):
            obj = NVLBuildTP('TGLH81')
        self.assertEqual(obj.outdir, None)
        self.assertEqual(obj.which, 'FULL')
        self.assertEqual(obj.tpname, None)
        self.assertEqual(obj.isval, False)
        self.assertEqual(obj.export_only, True)

        # ===== exportonly
        with MockVar(os.environ, 'IN1', 'EXPORTONLY:ARR'):
            obj = NVLBuildTP('TGLH81')
        self.assertEqual(obj.outdir, None)
        self.assertEqual(obj.which, 'ARR')
        self.assertEqual(obj.tpname, None)
        self.assertEqual(obj.isval, False)
        self.assertEqual(obj.export_only, True)

        # ===== MV
        with MockVar(os.environ, 'IN1', 'ARR'):
            obj = NVLBuildTP('TGLH81')
        self.assertEqual(obj.outdir, None)
        self.assertEqual(obj.which, 'ARR')
        self.assertEqual(obj.tpname, None)
        self.assertEqual(obj.isval, False)
        self.assertEqual(obj.export_only, False)

        # ===== VALL only, this is treated as "VALL.json" mv
        with MockVar(os.environ, 'IN1', 'VALL'):
            obj = NVLBuildTP('TGLH81')
        self.assertEqual(obj.outdir, None)
        self.assertEqual(obj.which, 'VALL')
        self.assertEqual(obj.tpname, None)
        self.assertEqual(obj.isval, True)
        self.assertEqual(obj.export_only, False)

        # ===== FULL only, this is treated as "VALL.json" mv
        with MockVar(os.environ, 'IN1', 'FULL'):
            obj = NVLBuildTP('TGLH81')
        self.assertEqual(obj.outdir, None)
        self.assertEqual(obj.which, 'FULL')
        self.assertEqual(obj.tpname, None)
        self.assertEqual(obj.isval, False)
        self.assertEqual(obj.export_only, False)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    @with_(MockVar, CleanTP, "main", Mock())
    def test_do_cleantp(self):
        obj = NVLBuildTP('TGLH81')
        # case1 - no env
        self.assertEqual(obj.do_cleantp(), 1)

        # case2 - with env, true
        with MockVar(os.environ, "CLEANTP", 'True'):
            self.assertEqual(obj.do_cleantp(), 1)

        # case3 - with env, true
        with MockVar(os.environ, "CLEANTP", 'False'):
            self.assertEqual(obj.do_cleantp(), 2)

    def test_copytp(self):
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2:
            File('a.file').touch()
            File('.git/abc').touch(mkdir=True)
            File('POR_TP/abc').touch(mkdir=True)
            NVLBuildTP.copytp(f'{tdir2}/out')
            expect = '''
./POR_TP/abc
./a.file
'''
            with Chdir(f'{tdir2}/out'):
                self.assertTextEqual('\n'.join(sorted(Allfiles('.'))), expect)

        # other inputs
        self.assertEqual(NVLBuildTP.copytp(None), 1)
        self.assertEqual(NVLBuildTP.copytp('I:/'), 2)

        # failrename
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2:
            File('a.file').touch()
            File('.git/abc').touch(mkdir=True)
            File('POR_TP/abc').touch(mkdir=True)
            NVLBuildTP.copytp(f'{tdir2}/out', failrename=True)
            expect = '''
./POR_TP_FAILED/abc
./a.file
'''
            with Chdir(f'{tdir2}/out'):
                self.assertTextEqual('\n'.join(sorted(Allfiles('.'))), expect)

    @with_(TempDir, chdir=True)
    def test_update_shared_sha_latest(self):
        called = []
        retval = ['HEAD']

        File('Shared/.git').touch(mkdir=True)
        File('POR_TP/TGLH1/EnvironmentFile.env').touch(mkdir=True)

        def fake_call(slf, *args, **kwargs):
            called.append(slf.cmd + list(args))
            return retval[0]

        def fake_call2(slf, branch):
            called.append(branch)

        with MockVar(SystemCall, 'run_outonly', fake_call), \
                MockVar(SystemCall, 'run', fake_call),\
                MockVar(GitCheckout, 'main', fake_call2), \
                MockVar(CheckerLog, 'get_folder_sha', Mock(return_value='sha1')):

            # Normal case
            called = []
            obj = NVLBuildTP('TGLH1')
            res = obj.update_shared_sha_latest('TGLH1', is_checker=False)
            self.assertEqual(res, 4)
            self.assertEqual(called, [['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                      'main'])

            # PR desc common branch case
            called = []
            with MockVar(GitHub, 'get_pr_view_output', Mock(return_value='nvl.common BRANCH: mainzz')):
                obj = NVLBuildTP('TGLH1')
                res = obj.update_shared_sha_latest('TGLH1', is_checker=False)
                self.assertEqual(res, 4)
                self.assertEqual(called, [['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                          'mainzz'])

            # Common case
            called = []
            with MockVar(os.environ, 'COMMON_Branch', 'mainy'):
                obj = NVLBuildTP('TGLH1')
                res = obj.update_shared_sha_latest('TGLH1', is_checker=False)
                self.assertEqual(res, 4)
                self.assertEqual(called, [['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                          'mainy'])

            # Normal case - special file
            File(f'POR_TP/TGLH1/InputFiles/common_main_name.txt').touch('mainx', mkdir=True)
            called = []
            res = obj.update_shared_sha_latest('TGLH1', is_checker=False)
            self.assertEqual(res, 4)
            self.assertEqual(called, [['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                      'mainx'])

            # RC branch
            with MockVar(os.environ, 'BASE_REF', 'main_RC_QA'):
                called = []
                res = obj.update_shared_sha_latest('TGLH1', is_checker=False)
                self.assertEqual(res, 4)
                self.assertEqual(called, [['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                          'main_RC_QA'])

            # -nolatest
            with MockVar(OPT, 'nolatest', True):
                res = obj.update_shared_sha_latest('TGLH1', is_checker=False)
                self.assertEqual(res, 5)

            # returned git is not HEAD
            retval[0] = 'main'
            res = obj.update_shared_sha_latest('TGLH1', is_checker=False)
            self.assertEqual(res, 3)

            # checker mode
            mkdirs('_work/nvl.cpu/nvl.cpu/Shared')
            mkdirs('nvl.cpu/Shared')
            with Chdir('_work/nvl.cpu/nvl.cpu'):
                res = obj.update_shared_sha_latest('TGLH1', is_checker=True)
                self.assertEqual(res, 3)

            # No Shared folder, aka, common
            mkdirs('common')
            with Chdir('common'):
                res = obj.update_shared_sha_latest('TGLH1', is_checker=True)
                self.assertEqual(res, 1)

    @with_(TempDir, chdir=True)
    @with_(MockVar, NVLBuildTPEntry, 'do_flow', Mock())
    def test_z_do_build(self):

        File('abc.sln').touch()
        File('POR_TP/bom1/a.tpproj').touch(mkdir=True)

        cmd = 'nvl_buildtp.py bom1 -build FULL -output outdir'.split()
        with MockVar(sys, "argv", cmd):
            NVLBuildTPEntry().main()

        self.assertEqual(os.environ['IN1'], 'FULL')
        self.assertEqual(Env.xpath(OPT.output), Env.xpath(f'{os.getcwd()}/outdir'))
        self.assertEqual(os.environ['CLEANTP'], 'false')

        # cleantp and valid json file
        File('TPConfig/MV_Templates/abcd.json').touch(mkdir=True)
        cmd = 'nvl_buildtp.py bom1 -build abcd -output outdir -clean'.split()
        with MockVar(sys, "argv", cmd):
            NVLBuildTPEntry().main()
        self.assertEqual(os.environ['CLEANTP'], 'true')

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    @with_(MockVar, NVLBuildTP, 'tpname', None)     # so that it will be reset to original
    def test_do_torch(self):
        File('abc.sln').touch()
        File('POR_TP/TGLH81/TGLH81.tpproj').touch(mkdir=True)
        modtxt = '''
Version 1.0;

Shared
{

SelectorRuleCollection BootUp
{
    SelectorRule If_ENGTP(yes_mv_tp_value, default)
    {
        yes_mv_tp_value => False;
        default;
    }
}
UserVars TPNameVars
{
    Const String TPName1 = "NVLXXXXXXX01B0ZSXXX";    # Ituffname
}
UserVars BYPASSVars
{
    Integer BYPASS_in_ENGINEERING_MODE = -1;
    Integer BYPASS_tt_DOC = 1;
    Integer BYPASS_tt_EZA = 1;
}

}
'''
        File('Shared/BaseInputs/Common/Common_Files/common.usrv').touch(modtxt, mkdir=True)
        modtxt1 = '''
Version 1.0;

Shared
{

    UserVars TorchRulesVars
{
    String locationCode = "6248";
    String bom = "564AAA2VA";
}

UserVars GlobalBomGroupName
{
    String ActiveBomGroup = "CLASS_NVL_S28C";
}

UserVars PerBomTPNameVars
{
    Const String PerBomTPName1 = "NVLS756A0H01K0ZGX35";    # Ituffname

}

}
        '''
        File('Shared/BaseInputs/UservarDefinitions.usrv').touch(modtxt1, mkdir=True)

        called = []

        def fake_call(slf, *args):
            called.append(slf.cmd + list(args))
            return 0, '', ''

        cmd = 'nvl_buildtp.py TGLH81 -torch'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(nvl_buildtp, 'IS_WIN', True), \
                MockVar(SystemCall, 'run_sout_serr', fake_call), \
                CaptureStdoutLog() as p:
            NVLBuildTPEntry().main()

        expect = '''
I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe build -s abc.sln -p POR_TP/TGLH81/TGLH81.tpproj -l I:/tpapps/TORCH/Prod22/LanguageServer --maxParallel 4 --ms /p:Configuration=TGLH81 300
I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe create-recipes --sln-config TGLH81 -s abc.sln -p POR_TP/TGLH81/TGLH81.tpproj -d .
I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe create-bin-report --sln-config TGLH81 -s abc.sln -p POR_TP/TGLH81/TGLH81.tpproj -d .
I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe create-counter-report --sln-config TGLH81 -s abc.sln -p POR_TP/TGLH81/TGLH81.tpproj -d .
I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe create-integration-report --sln-config TGLH81 -s abc.sln -p POR_TP/TGLH81/TGLH81.tpproj -d .
I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe create-patlist-instance-report --sln-config TGLH81 -s abc.sln -p POR_TP/TGLH81/TGLH81.tpproj -d .
I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe create-ltl-report --sln-config TGLH81 -s abc.sln -p POR_TP/TGLH81/TGLH81.tpproj -d .
'''
        result = []
        for item in called:
            result.append(' '.join(str(x) for x in item))
        self.assertTextEqual('\n'.join(result), expect)

        # TP name check case 1, VALL input
        cmd = 'nvl_buildtp.py TGLH81 -torch -output I:/blah/NVLS356A0H01B0AS528'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(nvl_buildtp, 'IS_WIN', True), \
                MockVar(os.environ, 'IN1', 'VALL'), \
                MockVar(SystemCall, 'run_sout_serr', fake_call), \
                CaptureStdoutLog() as p:
            NVLBuildTPEntry().main()

        expect1 = '''
-i- UPDATED: Shared/BaseInputs/Common/Common_Files/common.usrv is updated by Uservar TPName1 updated with value NVLS356A0H01B0AS528.
'''
        std_output1 = '\n'.join(x for x in p.getvalue().split('\n') if 'completed in' not in x)
        proc_output1 = std_output1.strip().splitlines()
        result1 = [line for line in proc_output1 if line.startswith("-i- UPDATED:")]
        self.assertTextEqual("\n".join(result1), expect1)

        # TP name check case 2, FULL input
        cmd = 'nvl_buildtp.py TGLH81 -torch -output I:/blah/NVLS356A0H01B00S528'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(nvl_buildtp, 'IS_WIN', True), \
                MockVar(os.environ, 'IN1', 'FULL'), \
                MockVar(SystemCall, 'run_sout_serr', fake_call), \
                CaptureStdoutLog() as p:
            NVLBuildTPEntry().main()

        expect2 = '''
-i- UPDATED: Shared/BaseInputs/Common/Common_Files/common.usrv is updated by Uservar TPName1 updated with value NVLS356A0H01B00S528.
        '''
        std_output2 = '\n'.join(x for x in p.getvalue().split('\n') if 'completed in' not in x)
        proc_output2 = std_output2.strip().splitlines()
        result2 = [line for line in proc_output2 if line.startswith("-i- UPDATED:")]
        self.assertTextEqual("\n".join(result2), expect2)

        # TP name check case 1a, VALL input invalid name
        cmd = 'nvl_buildtp.py TGLH81 -torch -output I:/blah/NVLS356A0H01B00S528'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(nvl_buildtp, 'IS_WIN', True), \
                MockVar(os.environ, 'IN1', 'VALL'), \
                MockVar(SystemCall, 'run_sout_serr', fake_call), \
                CaptureStdoutLog() as p:
            with self.assertRaisesRegex(ErrorUser, 'Invalid tpname for VALL V drive TP'):
                NVLBuildTPEntry().main()

        # TP name check case 2a, FULL input invalid name
        cmd = 'nvl_buildtp.py TGLH81 -torch -output I:/blah/NVLS356A0H01B0AS528'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(nvl_buildtp, 'IS_WIN', True), \
                MockVar(os.environ, 'IN1', 'FULL'), \
                MockVar(SystemCall, 'run_sout_serr', fake_call), \
                CaptureStdoutLog() as p:
            with self.assertRaisesRegex(ErrorUser, 'Invalid tpname for FULL I drive TP'):
                NVLBuildTPEntry().main()

        # tpbot=True: TPName1 update runs, but .sln/.tpproj and Windows check are skipped
        # Remove .sln and .tpproj to verify tpbot path does not require them
        check_and_del('abc.sln')
        check_and_del('POR_TP/TGLH81/TGLH81.tpproj')
        result = NVLBuildTP('TGLH81').do_torch(tpbot=True)
        self.assertEqual(result, 1)  # early return from tpbot guard

    def test_get_branch_from_env(self):
        # no env file
        self.assertEqual(Clone.get_branch_from_env('nvl.cpu', 'Class_BOM'), 'main')

        with MockVar(os.environ, 'CPU_Branch', 'none'):
            self.assertEqual(Clone.get_branch_from_env('nvl.cpu', 'Class_BOM'), 'main')

        with MockVar(os.environ, 'CPU_Branch', 'blah'):
            self.assertEqual(Clone.get_branch_from_env('nvl.cpu', 'Class_BOM'), 'blah')

        # RC branch
        with MockVar(os.environ, 'BASE_REF', 'main_RC_xyz'):
            self.assertEqual(Clone.get_branch_from_env('nvl.pcd', 'Class_BOM'), 'main_RC_xyz')

    @with_(TempDir, chdir=True)
    @with_(MockVar, os.environ, 'IS_PR_COMMON', 'True')
    @with_(MockVar, CheckerLog, 'get_folder_sha', Mock(return_value='some_sha'))
    def test_do_clone1(self):
        # from runner, with IS_PR_COMMON
        mkdirs('something/_work/nvl.common/nvl.common')
        mkdirs('something/nvl.cpu/Shared')
        mkdirs('something/nvl.gcd/Shared')
        mkdirs('something/nvl.pcd/Shared')
        os.chdir('something/_work/nvl.common/nvl.common')
        mkdirs('BaseInputs/Common')
        File('abc.sln').touch()
        File('POR_TP/bom1/a.tpproj').touch(mkdir=True)

        called = []

        def fake_call(slf, *args, **kwargs):
            mkdirs('nvl.cpu/Shared')
            mkdirs('nvl.pcd/Shared')
            mkdirs('nvl.hub/Shared')
            mkdirs('nvl.gcd/Shared')
            called.append(slf.cmd + list(args))
            return 0, '', ''

        def fake_call2(slf, *args, **kwargs):
            called.append(slf.cmd + list(args))
            return 0, 'commit 797eef5bb3616b622a4a3037aa3e3d73fd20ac77 (HEAD -> torch_build_errors_chk, origin/torch_build_errors_chk)'

        passmsg = 'Your branch is up to date with main\nnothing to commit, working tree clean\n'
        cmd = 'nvl_buildtp.py bom1 -clone'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(SystemCall, 'run', fake_call),\
                MockVar(SystemCall, 'run_outtxt', fake_call2),\
                MockVar(TPRobot, 'repo_init_check', Mock(return_value=(0, passmsg, ''))):
            NVLBuildTPEntry().main()

        expect = f'''
git clone --recurse-submodules https://{BuildCommon.tok2}@github.com/intel-restricted/nvl.cpu.git
git clone --recurse-submodules https://{BuildCommon.tok2}@github.com/intel-restricted/nvl.hub.git
git clone --recurse-submodules https://{BuildCommon.tok2}@github.com/intel-restricted/nvl.gcd.git
git clone --recurse-submodules https://{BuildCommon.tok2}@github.com/intel-restricted/nvl.pcd.git
gh pr view
'''
        result = []
        for item in called:
            result.append(' '.join(str(x) for x in item))
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, CheckerLog, 'get_folder_sha', Mock(return_value='some_sha'))
    def test_do_clone2(self):
        # from runner, dielet
        mkdirs('something/_work/nvl.cpu/nvl.cpu/Shared')
        mkdirs('something/nvl.gcd/Shared')
        mkdirs('something/nvl.pcd/Shared')
        os.chdir('something/_work/nvl.cpu/nvl.cpu')
        mkdirs('BaseInputs/Common')
        File('abc.sln').touch()
        File('POR_TP/bom1/a.tpproj').touch(mkdir=True)

        called = []

        def fake_call(slf, *args, **kwargs):
            mkdirs('nvl.cpu/Shared')
            mkdirs('nvl.pcd/Shared')
            mkdirs('nvl.hub/Shared')
            mkdirs('nvl.gcd/Shared')
            called.append(slf.cmd + list(args))
            return 0, '', ''

        def fake_call2(slf, *args, **kwargs):
            called.append(slf.cmd + list(args))
            return 0, 'commit 797eef5bb3616b622a4a3037aa3e3d73fd20ac77 (HEAD -> torch_build_errors_chk, origin/torch_build_errors_chk)'

        passmsg = 'Your branch is up to date with main\nnothing to commit, working tree clean\n'
        cmd = 'nvl_buildtp.py bom1 -clone'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(SystemCall, 'run', fake_call),\
                MockVar(SystemCall, 'run_outtxt', fake_call2),\
                MockVar(TPRobot, 'repo_init_check', Mock(return_value=(0, passmsg, ''))):
            NVLBuildTPEntry().main()

        expect = f'''
git clone --recurse-submodules https://{BuildCommon.tok2}@github.com/intel-restricted/nvl.hub.git
git clone --recurse-submodules https://{BuildCommon.tok2}@github.com/intel-restricted/nvl.gcd.git
git clone --recurse-submodules https://{BuildCommon.tok2}@github.com/intel-restricted/nvl.pcd.git
git checkout main
git fetch
git pull
git checkout main
git fetch
git pull
git checkout main
git fetch
git pull
git checkout main
git fetch
git pull
'''
        result = []
        for item in called:
            result.append(' '.join(str(x) for x in item))
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, CheckerLog, 'get_folder_sha', Mock(return_value='some_sha'))
    def test_do_clone3(self):
        # not from runner
        mkdirs('something/_work/Shared')
        mkdirs('something/nvl.cpu/Shared')
        mkdirs('something/nvl.gcd/Shared')
        mkdirs('something/nvl.pcd/Shared')
        os.chdir('something/_work')
        mkdirs('BaseInputs/Common')
        File('abc.sln').touch()
        File('POR_TP/bom1/a.tpproj').touch(mkdir=True)

        called = []

        def fake_call(slf, *args, **kwargs):
            mkdirs('nvl.cpu/Shared')
            mkdirs('nvl.pcd/Shared')
            mkdirs('nvl.hub/Shared')
            mkdirs('nvl.gcd/Shared')
            called.append(slf.cmd + list(args))
            return 0, '', ''

        def fake_call2(slf, *args, **kwargs):
            called.append(slf.cmd + list(args))
            return 0, 'commit 797eef5bb3616b622a4a3037aa3e3d73fd20ac77 (HEAD -> torch_build_errors_chk, origin/torch_build_errors_chk)'

        passmsg = 'Your branch is up to date with main\nnothing to commit, working tree clean\n'
        cmd = 'nvl_buildtp.py bom1 -clone'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(SystemCall, 'run', fake_call),\
                MockVar(SystemCall, 'run_outtxt', fake_call2),\
                MockVar(TPRobot, 'repo_init_check', Mock(return_value=(0, passmsg, ''))):
            NVLBuildTPEntry().main()

        expect = f'''
git clone --recurse-submodules https://github.com/intel-restricted/nvl.cpu.git
git clone --recurse-submodules https://github.com/intel-restricted/nvl.hub.git
git clone --recurse-submodules https://github.com/intel-restricted/nvl.gcd.git
git clone --recurse-submodules https://github.com/intel-restricted/nvl.pcd.git
git checkout main
git fetch
git pull
git checkout main
git fetch
git pull
git checkout main
git fetch
git pull
git checkout main
git fetch
git pull
'''
        result = []
        for item in called:
            result.append(' '.join(str(x) for x in item))
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    def test_update_dieletindicator(self):
        usrv = 'Shared/BaseInputs/Common/Common_Files/TOSRules.usrv'
        orig = '''
String something = "abc";
String DIELET_INDICATOR = "CPU,GCD,HUB,PCD";
'''
        File(usrv).touch(orig, mkdir=True)

        # case: no change bec DIEINDICATOR is not defined
        NVLBuildTP.update_dieletindicator()
        self.assertTextEqual(File(usrv).read(), orig)     # no change

        # case: dielet repo DIEINDICATOR is defined
        with MockVar(os.environ, 'DIEINDICATOR', 'CPU'):
            NVLBuildTP.update_dieletindicator()
        expect = '''
String something = "abc";
String DIELET_INDICATOR = "CPU";
'''
        self.assertTextEqual(File(usrv).read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_create_dielet_sha(self):
        shutil.copytree(f'{UT_DIR}/SimpleNVL', 'nvl.cpu')
        shutil.copytree(f'{UT_DIR}/git_checkout_testing/.git', 'nvl.cpu/.git')
        shutil.copytree(f'{UT_DIR}/git_checkout_testing/.git', 'nvl.cpu/Shared/.git')
        with Chdir('nvl.cpu'):
            CheckerLog.set_repo_sha()
            NVLBuildTP.create_dielet_sha()

            result = JsonRead('POR_TP/TGLH81/Reports/RepoRev.json').load()
            result['tool'] = 'some_sha'
            self.assertEqual(result, {'nvl.common': '066cb933783343ff944c8640874e63ecd960b031',
                                      'nvl.cpu': '066cb933783343ff944c8640874e63ecd960b031',
                                      'tool': 'some_sha'})

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_delete_modules_unused(self):
        check_and_del('Modules')
        File('Modules/SCN/SCN1/a.mtpl').touch(mkdir=True)
        File('Modules/SCN/SCN2/b.mtpl').touch(mkdir=True)
        File('Modules/ARR/ARR1/c.mtpl').touch(mkdir=True)
        mlist = [f'../../Modules/SCN/SCN1/a.mtpl',
                 f'../../Modules/ARR/ARR1/c.mtpl',
                 f'../../Modules/ARRX/ARRX/d.mtpl',           # not found
                 f'../../Shared/Modules/SCN/SCN2/b.mtpl']     # shared are not removed
        with MockVar(TestProgram, 'get_all_mtpl_from_stpl', Mock(return_value=mlist)):
            NVLBuildTP.delete_modules_unused(os.getcwd(), 'TGLH81')
        result = sorted(glob.glob('Modules/*/*'))
        self.assertEqual([Env.xpath(x) for x in result], ['Modules/ARR/ARR1', 'Modules/SCN/SCN1'])

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL3')
    def test_switch2(self):
        obj = NVLBuildTP('Class_NVL_H81')
        obj.tpobj = TestProgram('POR_TP/Class_NVL_H81')
        File('TPConfig/TPSwitch/ahmt.py').touch('''
from mod.tpswitch import TPSwitch2
POR_TP = ['AHMT_{SHORTBOM}']
obj = TPSwitch2('POR_TP')
''', mkdir=True)

        with MockVar(os.environ, 'ACPY', 'ahmt'), \
                MockVar(NVLBuildTP, 'do_torch', Mock()), \
                MockVar(NVLBuildTP, 'do_cleantp', Mock()), \
                MockVar(QGateExecute, 'main', Mock()):

            obj.tpswitch2()

        # confirm
        self.assertEqual([Env.xpath(x) for x in sorted(glob.glob('POR_TP/*/*.env'))],
                         [Env.xpath(x) for x in('POR_TP/AHMT_NVL_H81/EnvironmentFile.env',
                                                'POR_TP/Class_NVL_H81/EnvironmentFile.env')])

    @with_(TempDir, chdir=True)
    def test_do_tprename(self):
        usrvfile = 'Shared/BaseInputs/Common/Common_Files/common.usrv'
        File(usrvfile).touch('''
String iCGL_ProductionEngg = "ENGG";
''', mkdir=True)

        # engg case
        with MockVar(NVLBuildTP, 'tpname', None):
            NVLBuildTP.do_tprename()
            self.assertEqual(File(usrvfile).read(), '\nString iCGL_ProductionEngg = "ENGG";\n')

        # prod case
        with MockVar(NVLBuildTP, 'tpname', 'NVLXXXXA0H05K50S542'):
            NVLBuildTP.do_tprename()
            self.assertEqual(File(usrvfile).read(), '\nString iCGL_ProductionEngg = "PROD";\n')

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_copy_pobj_cache(self):
        obj = NVLBuildTP('TGLH81')
        # os.chdir('/intel/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLXXXXXXX01P0CSXXX')
        # obj = NVLBuildTP('Class_NVL_S28C')

        obj.tpobj = TestProgram(obj.env)

        # case 1 - unittest
        self.assertEqual(obj.copy_pobj_cache(), 1)

        with MockVar(nvl_buildtp, 'IS_UT', False):
            # case 2 - root folder does not exist
            obj.root_pobj_cache = Env.xpath('/tmp_not_exist')
            self.assertEqual(obj.copy_pobj_cache(), 2)

            with TempDir(name=True) as tdir:
                File(f'{tdir}/template/TGLH81/EnvironmentFile.env').touch('''
### Env. File
FUSE_ROOT_DIR = "From_template";

HDST_PLIST_PATH = "~HDMT_TPL_DIR\\Supersedes\\patterns;" +
    "I:\\hdmxpats\tgl\\Mwio\\RevTTR0.0\\p8\\plb";
''', mkdir=True)
                obj.root_pobj_cache = tdir

                # case 3 - no JOB_ID
                self.assertEqual(obj.copy_pobj_cache(), 3)

                # case 4 - template folder not found
                with MockVar(NVLBuildTP, 'JOBID', '123'):
                    with MockVar(obj.tpobj, 'get_bomfolder', Mock(return_value='blah')):
                        self.assertEqual(obj.copy_pobj_cache(), 4)

                # case 5 - real case
                with MockVar(NVLBuildTP, 'JOBID', '123'):
                    bomroot = obj.copy_pobj_cache()
                    pprint(os.listdir(bomroot))
                    self.assertEqual(len(os.listdir(bomroot)), 2)
                    self.assertEqual(len(File(f'{bomroot}/EnvironmentFile.env').read().split('\n')), 436)   # it was updated

    @with_(TempDir, chdir=True)
    def test_z_branchname(self):
        # default
        self.assertEqual(Clone.get_branch_from_env('nvl.pcd', 'Class_BOM'), 'main')
        self.assertEqual(BuildCommon.get_branch('nvl.pcd', 'main'), 'main')

        # specific branch
        File('POR_TP/Class_BOM/InputFiles/nvl.pcd.main_name.txt').touch('mainx', mkdir=True)
        self.assertEqual(Clone.get_branch_from_env('nvl.pcd', 'Class_BOM'), 'mainx')
        self.assertEqual(BuildCommon.get_branch('nvl.pcd', 'main'), 'main')

    def test_id_labels(self):
        self.assertEqual(NVLBuildTP.id_labels(['Modules/tpi']), {'tpi'})   # shared submodule
        self.assertEqual(NVLBuildTP.id_labels(['Modules/tpd/ARR_A/cc.mtpl']), {'ARR_A'})
        self.assertEqual(NVLBuildTP.id_labels(['Modules/tpd/abc/InputFiles/a.xml']), {'abc'})
        self.assertEqual(NVLBuildTP.id_labels(['Modules/tpd/abc/AlephFiles/blah/a.xml']), {'abc'})
        self.assertEqual(NVLBuildTP.id_labels(['Modules/abc/cc']), {'abc'})    # catch all
        self.assertEqual(NVLBuildTP.id_labels(['Modules/abc/InputFiles/a.xml']), {'abc'})
        self.assertEqual(NVLBuildTP.id_labels(['Modules/abc/AlephFiles/a.xml']), {'abc'})
        self.assertEqual(NVLBuildTP.id_labels(['Shared/package/blah.txt']), {'Shared'})
        self.assertEqual(NVLBuildTP.id_labels(['Shared/package/UservarDefinitions.usrv']), {'Uservar'})
        self.assertEqual(NVLBuildTP.id_labels(['POR_TP/blah/blah.txt']), {'PORTP'})
        self.assertEqual(NVLBuildTP.id_labels(['POR_TP/blah/EnvironmentFile.env']), {'EnvFile'})
        self.assertEqual(NVLBuildTP.id_labels(['.github/workflow']), {'YML'})
        self.assertEqual(NVLBuildTP.id_labels(['TPConfig/blah']), {'TPConfig'})
        self.assertEqual(NVLBuildTP.id_labels(['readme.txt']), {'Misc'})
        self.assertEqual(NVLBuildTP.id_labels(['UserCode/dlls/blah.dll']), {'UserCode'})

        # multiple
        self.assertEqual(NVLBuildTP.id_labels(['TPConfig/blah', 'Shared/package', 'Modules/tpd/ARR_A/cc.mtpl']),
                         {'TPConfig', 'Shared', 'ARR_A'})
        # reduced
        self.assertEqual(NVLBuildTP.id_labels(['Modules/ARR_A/cc.mtpl',
                                               'Modules/ARR_B/cc.mtpl',
                                               'Modules/ARR_C/cc.mtpl',
                                               'Modules/SCN_A/cc.mtpl',
                                               'Modules/SCN_B/cc.mtpl',
                                               'Modules/SCN_C/cc.mtpl']),
                         {'ARR', 'SCN'})


class TestFullTP(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_regres_nvlstitch(self):
        # full tp stitch run, with minimal Mocks, up to ModuleSkip (aka, EXPORTONLY flow).
        # Postprocess and qgates are not run

        # To reproduce regres_stitch/ folder:
        # 1. Run tpbuild EXPORTONLY (per dielet).
        #
        #    cd /intel/tpvalidation/engtools/tptools/mtl/unittests/regres_stitch
        #
        # 2. _work is a direct git clone of common
        # 3. untar the complete.tar.gz from dielets, into nvl.<dielet> folder
        # 4. Delete `find . | grep DFF.ube`
        # 5. \rm -rf nvl.???/astra
        #    \rm -rf nvl.???/UserCode/lib
        #    \rm */*/*/*/*/*.tsv
        #    \rm -rf */Modules/*/.source
        # 7. tar --exclude='.git' --exclude=pytpd -z -cvf ../regres_stitch.tar.gz .
        if IS_UNIX:
            fake_exe = 'echo'
        else:
            fake_exe = 'cmd /c echo'

        with TempDir(name=True) as outdir, \
                TempDir(name=True, delete=True) as tdir:
            # tdir = f'{UT_DIR}/regres_stitch_dynamicbom'
            untar(f'{UT_DIR}/regres_stitch_dbom.tar.gz', tdir)    # ~18 secs to untar

            cmd = f'nvl_buildtp.py Class_NVL_S28C -flow -common -output {outdir}'.split()
            with Chdir(f'{tdir}/_work/nvl.common/nvl.common'), \
                    MockVar(sys, "argv", cmd), \
                    MockVar(DoMV, 'get_torch_exe', Mock(return_value=fake_exe)), \
                    MockVar(NVLBuildTP, '_torch_check_unix', Mock()), \
                    MockVar(nvl_buildtp, 'CALLERBIN', f'{ROOT_ENV}/nvl_buildtp.py'), \
                    MockVar(os.environ, 'IN1', 'EXPORTONLY:FULL'), \
                    MockVar(NVLBuildTP, 'copytpx', Mock()), \
                    MockVar(CheckerLog, 'get_folder_sha', Mock(return_value='deadbeef')), \
                    MockVar(MSBuild, 'copy_dll', Mock()):

                # Mocked routines:
                #    copytp(): For fast unittest. No need copy to output
                #    get_folder_sha(): Unittest dir does not have git
                #    copy_dll(): Due to deep env settings

                NVLBuildTPEntry().main()

                # Check that testprogram is ok
                TestProgram(f'{outdir}/POR_TP/Class_NVL_S28C/EnvironmentFile.env').init(light=True)

        check_and_del(f'{outdir}.1')

    @with_(TempDir, chdir=True)
    @with_(MockVar, CheckerLog, 'get_folder_sha', Mock(return_value='some_sha'))
    @with_(MockVar, Usrv, 'get_var', Mock(return_value='Name1'))
    def test_integration_full(self):
        # Mimic 4 dielets repo plus 1 common repo to final integration.
        tdir2cwd = os.getcwd()
        tdir2 = f'{tdir2cwd}/output'
        tdir3 = f'{tdir2cwd}/output_NVLBuild_tpname_test'

        cmd = f'nvl_buildtp.py class_nvl_28c -stitch {tdir2}'.split()
        with MockVar(sys, "argv", cmd), \
                TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple_disagg2a') as tdir:
            File('_work/com/com/BaseInputs/Common/Common_Files/TOSRules.usrv').touch(r'''
Version 1.0;

Shared
{
UserVars DFFVars
{
    String DIEID_BASE = "U1.U1";
    String DIEID_HUB = "U1.U2";
}
UserVars DieletIndicator
{
    String DIELET_INDICATOR = "CPU";
}
}
''', mkdir=True)
            File('nvl_cpu/Shared/BaseInputs/Common/Common_Files/TOSRules.usrv').touch(r'''
Version 1.0;

Shared
{
UserVars DFFVars
{
    String DIEID_BASE = "U1.U1";
    String DIEID_HUB = "U1.U2";
}
UserVars DieletIndicator
{
    String DIELET_INDICATOR = "CPU";
}
}
''', mkdir=True)
            File('nvl_gcd/Shared/BaseInputs/Common/Common_Files/TOSRules.usrv').touch(r'''
Version 1.0;

Shared
{
UserVars DFFVars
{
    String DIEID_BASE = "U1.U1";
    String DIEID_HUB = "U1.U2";
}
UserVars DieletIndicator
{
    String DIELET_INDICATOR = "CPU";
}
}
''', mkdir=True)
            File('nvl_pcd/Shared/BaseInputs/Common/Common_Files/TOSRules.usrv').touch(r'''
Version 1.0;

Shared
{
UserVars DFFVars
{
    String DIEID_BASE = "U1.U1";
    String DIEID_HUB = "U1.U2";
}
UserVars DieletIndicator
{
    String DIELET_INDICATOR = "CPU";
}
}
''', mkdir=True)
            File('nvl_hub/Shared/BaseInputs/Common/Common_Files/TOSRules.usrv').touch(r'''
Version 1.0;

Shared
{
UserVars DFFVars
{
    String DIEID_BASE = "U1.U1";
    String DIEID_HUB = "U1.U2";
}
UserVars DieletIndicator
{
    String DIELET_INDICATOR = "CPU";
}
}
''', mkdir=True)
            File('_work/com/com/BaseInputs/Common/Common_Files/common.usrv').touch(r'''
Version 1.0;

Shared
{

SelectorRuleCollection BootUp
{
    SelectorRule If_ENGTP(yes_mv_tp_value, default)
    {
        yes_mv_tp_value => False;
        default;
    }
}
UserVars TPNameVars
{
    Const String TPName1 = "NVLXXXXXXX01B0ZSXXX";    # Ituffname
}
UserVars BYPASSVars
{
    Integer BYPASS_in_ENGINEERING_MODE = -1;
    Integer BYPASS_tt_DOC = 1;
    Integer BYPASS_tt_EZA = 1;
}

}
''', mkdir=True)

            File('nvl_hub/POR_TP/class_nvl_28c/SkipModules/SCN.txt').touch(mkdir=True)
            File('nvl_gcd/POR_TP/class_nvl_28c/SkipModules/ARR.permanent').touch(mkdir=True)

            with MockVar(SystemCall, 'run', Mock()):
                NVLBuildTPEntry().main()

            mod_parent_path = f'{tdir2}/Modules'
            print('Checking if all 4 dielet modules are integrated into output path.')
            self.assertEqual(set(os.listdir(mod_parent_path)),
                             {'TPI_FLWFLGS_CXX', 'TPI_FLWFLGS_GXX', 'TPI_FLWFLGS_PXX', 'TPI'})

            self.assertEqual(set(os.listdir(f'{mod_parent_path}/TPI')),
                             {'TPI_FLWFLGS_HXX'})

            por_parent_path = f'{tdir2}/POR_TP/class_nvl_28c'
            expect_files = ['EnvironmentFile.env', 'PLIST_ALL_CLASS_NVL_28C.plist.xml', 'PLIST_ALL_IPC.plist.ipxml',
                            'PLIST_ALL_IPG.plist.ipxml', 'PLIST_ALL_IPH.plist.ipxml', 'PLIST_ALL_IPP.plist.ipxml',
                            'SubTestPlan.stpl']
            missing_files = [file for file in expect_files if file not in os.listdir(por_parent_path)]

            print('Checking ENV files, Plist files and Stpl files are integrated into output path.')
            self.assertEqual(missing_files, [], f'ENV Missing: {missing_files}')    # we expect no missing mods

            print('Checking ProgramFlowsTestPlan Folder')
            programflowspath = f'{tdir2}/POR_TP/class_nvl_28c/ProgramFlowsTestPlan'
            expect = '''
['IPC_FLOWS.flw',
 'IPC_FLOWS.mtpl',
 'IPC_FLOWS.py',
 'IPG_FLOWS.flw',
 'IPG_FLOWS.mtpl',
 'IPG_FLOWS.py',
 'IPH_FLOWS.flw',
 'IPH_FLOWS.mtpl',
 'IPH_FLOWS.py',
 'IPP_FLOWS.flw',
 'IPP_FLOWS.mtpl',
 'IPP_FLOWS.py',
 'ProgramFlows.flw',
 'ProgramFlows.mtpl',
 'ProgramFlows.py',
 'ProgramFlowsRev1.py',
 'ProgramFlowsRev1_CDIE.py',
 'ProgramFlowsRev1_GDIE.py',
 'ProgramFlowsRev1_HUB.py',
 'ProgramFlowsRev1_PCD.py',
 'PymtplInputFiles']
'''
            self.assertTextEqual(pformat(sorted(os.listdir(programflowspath))), expect)

            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";

#EndSequence
#{
# Power_dwn_PKG_xxx_pwrd_zerzer
#}
'''
            self.assertTextEqual(File(f'{tdir2}/BaseTestPlan.tpl').read().replace('\t', ' '), expect)

            # Check the .imp files are copied
            expect = '''
BaseInputs
BaseTestPlan.tpl
Modules
POR_TP
Shared
ipc.imp
ipg.imp
'''
            self.assertTextEqual('\n'.join(sorted(os.listdir(tdir2))), expect)

            # Check the BaseInputs are copied
            expect = f'''
{tdir2}/BaseInputs/CPU/a.pin
{tdir2}/BaseInputs/GCD/a.pin
{tdir2}/BaseInputs/extra.txt
'''
            self.assertTextEqual('\n'.join(sorted(Allfiles(f'{tdir2}/BaseInputs'))), expect)

            # Check the Uservar value
            expect = '''
Version 1.0;

Shared
{
UserVars DFFVars
{
    String DIEID_BASE = "U1.U1";
    String DIEID_HUB = "U1.U2";
}
UserVars DieletIndicator
{
    String DIELET_INDICATOR = "GCD,HUB,PCD,CPU";
}
}
'''
            with open(f'{tdir2}/Shared/BaseInputs/Common/Common_Files/TOSRules.usrv', 'r') as file:
                result = file.read()
            self.assertEqual(result, expect)

            self.assertIn('tool', File(f'{tdir2}/POR_TP/class_nvl_28c/Reports/RepoRev.json').read())

            self.assertEqual(set(os.listdir(f'{tdir2}/POR_TP/class_nvl_28c/SkipModules')),
                             {'ARR.permanent', 'SCN.txt'})

            cmd = f'nvl_buildtp.py class_nvl_28c -stitch {tdir3}'.split()
            with MockVar(SystemCall, 'run', Mock()), \
                    MockVar(sys, "argv", cmd), \
                    MockVar(NVLBuildTP, 'tpname', "TPname_test"):
                NVLBuildTPEntry().main()

                self.assertIn('TPname_test', File(f'{tdir3}/Shared/BaseInputs/Common/Common_Files/common.usrv').read())

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_update_tpname(self):
        tpobj = {'CPU': TestProgram('POR_TP/TGLH81/EnvironmentFile.env')}
        usrv = 'Shared/BaseInputs/Common/Common_Files/common.usrv'
        File(usrv).touch('''
UserVars TPNameVars
{
    Const String TPName1 = "NVLS756B0H02A0ZS500";    # Ituffname
}
''', mkdir=True)

        # default case - no tpname given
        Integrate.update_tpname(tpobj, '.')
        expect = '''
UserVars TPNameVars
{
    Const String TPName1 = "NVLS756A0H01A0ZS501";    # Ituffname
}
'''
        self.assertTextEqual(File(usrv).read(), expect)

        # set TPname to something
        with MockVar(NVLBuildTP, 'tpname', 'NVLS756A0H01A0ZS502'):
            Integrate.update_tpname(tpobj, '.')
        expect = '''
UserVars TPNameVars
{
    Const String TPName1 = "NVLS756A0H01A0ZS502";    # Ituffname
}
'''
        self.assertTextEqual(File(usrv).read(), expect)

    def test_dielet_init(self):
        with TempDir(name=True, chdir=True), \
                MockVar(Integrate, 'target_die', []), \
                MockVar(os.environ, 'REPO_DIR', '/path/blah/nvl.cpu'), \
                MockVar(os.environ, 'CHECKER_FULLTP', 'True'):
            File('nvl.cpu/Shared/POR_TP/BOM1/EnvironmentFile.env').touch(mkdir=True)
            File('nvl.cpu/POR_TP/BOM1/EnvironmentFile.env').touch(mkdir=True)
            obj = Integrate('BOM1')
            self.assertEqual(obj.comenv, ['nvl.cpu/Shared/POR_TP/BOM1/EnvironmentFile.env'])

    def test_tpl(self):
        # This testcase is dielets without common BasetestPlan.tpl
        with TempDir(name=True, chdir=True) as tdir:
            File('nvl.cpu/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "Common_BOM.imp";
Import "Cdie.imp";
''', mkdir=True)
            File('nvl.gcd/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "Common_BOM.imp";
Import "Gdie.imp";
Import "SubBindef.imp";
''', mkdir=True)
            File('nvl.hub/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "hub.imp";
Import "Common_BOM.imp";
''', mkdir=True)
            File('_work/nvl.com/nvl.com/Readme').touch('', mkdir=True)    # BaseTestPlan.tpl does not exist here

            # Run it
            res = TplFullTP().main(None)

            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "Common_BOM.imp";
Import "Cdie.imp";
Import "hub.imp";
Import "Gdie.imp";
'''
            self.assertTextEqual(res, expect)

    def test_tpl2(self):
        # This testcase is dielets with common BasetestPlan.tpl which we grab all the lines
        with TempDir(name=True, chdir=True) as tdir:
            File('nvl.cpu/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "Common_BOM.imp";
Import "Cdie.imp";
''', mkdir=True)
            File('nvl.gcd/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "Common_BOM.imp";
Import "Gdie.imp";
Import "SubBindef.imp";
''', mkdir=True)
            File('_work/nvl.com/nvl.com/BaseTestPlan.tpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "hub.imp";
Import "ComOnly.imp";

# some comment
EndSequence
{
    Power_dwn_PKG_xxx_pwrd_zerzer
}
''', mkdir=True)

            # Run it
            res = TplFullTP().main(None)

            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "hub.imp";
Import "ComOnly.imp";
Import "Common_BOM.imp";
Import "Cdie.imp";
Import "Gdie.imp";

# some comment
EndSequence
{
    Power_dwn_PKG_xxx_pwrd_zerzer
}
'''
            self.assertTextEqual(res, expect)

    def test_tpl3(self):
        # This testcase is dielets without common BasetestPlan.tpl and with target_die
        with TempDir(name=True, chdir=True) as tdir:
            File('nvl.cpu/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "Common_BOM.imp";
Import "Cdie.imp";
''', mkdir=True)
            File('nvl.gcd/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "Common_BOM.imp";
Import "Gdie.imp";
Import "SubBindef.imp";
''', mkdir=True)
            File('nvl.hub/BaseTestPlan.tpl').touch('''
#------
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp";
Import "SubBindef.imp";
Import "hub.imp";
Import "Common_BOM.imp";
''', mkdir=True)

            # Shared
            File('nvl.cpu/Shared/BaseTestPlan.tpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp.shared";
Import "SubBindef.imp.shared";
Import "Common_BOM.imp.shared";
Import "Cdie.imp.shared";
''', mkdir=True)
            with MockVar(Integrate, 'target_die', ['nvl.cpu']):
                res = TplFullTP().main(None)

            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "Package.imp.shared";
Import "SubBindef.imp.shared";
Import "Common_BOM.imp.shared";
Import "Cdie.imp.shared";
Import "Package.imp";
Import "SubBindef.imp";
Import "Common_BOM.imp";
Import "Cdie.imp";
Import "hub.imp";
Import "Gdie.imp";
'''
            self.assertTextEqual(res, expect)

    def test_get_die_from_env(self):
        # empty env
        self.assertEqual(Integrate.get_die_from_env(), 'CPU,GCD,HUB,PCD')

        # full tp
        with MockVar(os.environ, 'CPU_Branch', 'main'), \
                MockVar(os.environ, 'GCD_Branch', 'main'), \
                MockVar(os.environ, 'PCD_Branch', 'main'), \
                MockVar(os.environ, 'HUB_Branch', 'main'):

            self.assertEqual(Integrate.get_die_from_env(), 'CPU,GCD,HUB,PCD')

        # partial tp
        with MockVar(os.environ, 'CPU_Branch', 'main'), \
                MockVar(os.environ, 'GCD_Branch', 'none'), \
                MockVar(os.environ, 'PCD_Branch', 'main'), \
                MockVar(os.environ, 'HUB_Branch', 'none'):

            self.assertEqual(Integrate.get_die_from_env(), 'CPU,PCD')

    @with_(TempDir, chdir=True)
    def test_get_dielet_list(self):
        File('_work/com/com/POR_TP/CLASS_BOM1/EnvironmentFile.env').touch(mkdir=True)
        File('nvl.cpu/POR_TP/CLASS_BOM1/EnvironmentFile.env').touch(mkdir=True)
        self.assertEqual([Env.xpath(x) for x in Integrate('CLASS_BOM1').get_dielet_list()], ['nvl.cpu/POR_TP/CLASS_BOM1/EnvironmentFile.env'])

        # cpu+gcd die
        File('nvl.gcd/POR_TP/CLASS_BOM1/EnvironmentFile.env').touch(mkdir=True)
        self.assertEqual(len(Integrate('CLASS_BOM1').get_dielet_list()), 2)
        with MockVar(os.environ, 'CPU_Branch', 'none'):
            self.assertEqual([Env.xpath(x) for x in Integrate('CLASS_BOM1').get_dielet_list()], [Env.xpath('nvl.gcd/POR_TP/CLASS_BOM1/EnvironmentFile.env')])

    def test_error_plist(self):
        # testing case: invalid line shows up in the plist file.
        with TempDir(name=True, chdir=True) as tdir:
            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_a.plist.xml').touch(r'''
<HdmtReferenceFile>
    <IPReference name="IP_PCH" path=".\PLIST_ALL_IP_PCH.plist.ipxml" />
    <IPReference name="IP_CPU" path=".\PLIST_ALL_IP_CPU.plist.ipxml" />
    <PList>
      <EnvFile name="EnvironmentFile.env" />
      <PListFile name="PTH_BGCEP_c28_class_u28g1.plist" />
    </PList>
</HdmtReferenceFile>
''', mkdir=True)

            with self.assertRaisesRegex(ErrorInput, 'Unknown line'):
                PlistFullTP().main('class_s68')

    def test_merge_plist(self):
        # testing case: com plist with only pkg content. 1 main plist file.
        #               cpu and gcd die with only one IP cpu/pch scope. 2 plist files from each repo.
        #               duplicate DRV reset plist in com, cpu, gcd dielet repo.
        #               after merging happen, final has 3 plist files - main, ip_cpu, ip_pch
        with TempDir(name=True, chdir=True) as tdir:
            File('_work/nvl.common/nvl_com/POR_TP/class_s68/PLIST_ALL_com.plist.xml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist" />
    <PListFile name="common_blah_allplist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_cpu.plist.xml').touch('''
<HdmtReferenceFile>
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist" />
    <PListFile name="cpu_blah_allplist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_IP_CPU.plist.ipxml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="cpu_ip_blah_allplist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_gcd/POR_TP/class_s68/PLIST_ALL_gcd.plist.xml').touch('''
<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist" />
    <PListFile name="pch_blah_allplist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_gcd/POR_TP/class_s68/PLIST_ALL_IP_PCH.plist.ipxml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="pch_ip_blah_all_plist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            result = PlistFullTP().main('class_s68')

            expect_main = '''
<HdmtReferenceFile>
   <IPReference name="IP_PCH" path="./PLIST_ALL_IP_PCH.plist.ipxml" />
   <IPReference name="IP_CPU" path="./PLIST_ALL_IP_CPU.plist.ipxml" />
   <PList>
      <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist" />
      <PListFile name="pch_blah_allplist.plist" />
      <PListFile name="cpu_blah_allplist.plist" />
      <PListFile name="common_blah_allplist.plist" />
   </PList>
</HdmtReferenceFile>
'''
            print(result.keys())
            self.assertTextEqual(result['PLIST_ALL_com.plist.xml'], expect_main)

            expect_cpu = '''
<HdmtReferenceFile>
   <PList>
      <PListFile name="cpu_ip_blah_allplist.plist" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_IP_CPU.plist.ipxml'], expect_cpu)

            expect_pch = '''
<HdmtReferenceFile>
   <PList>
      <PListFile name="pch_ip_blah_all_plist.plist" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_IP_PCH.plist.ipxml'], expect_pch)

    def test_merge_plist_with_target_die(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_cpu.plist.xml').touch('''
<HdmtReferenceFile>
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist" />
    <PListFile name="cpu_blah_allplist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_IP_CPU.plist.ipxml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="cpu_ip_blah_allplist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_gcd/POR_TP/class_s68/PLIST_ALL_gcd.plist.xml').touch('''
<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist" />
    <PListFile name="pch_blah_allplist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_gcd/POR_TP/class_s68/PLIST_ALL_IP_PCH.plist.ipxml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="pch_ip_blah_all_plist.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            # Shared
            File('nvl_cpu/Shared/POR_TP/class_s68/PLIST_ALL_cpu.plist.xml').touch('''
<HdmtReferenceFile>
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist.Shared" />
    <PListFile name="cpu_blah_allplist.plist.Shared" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            File('nvl_cpu/Shared/POR_TP/class_s68/PLIST_ALL_IP_CPU.plist.ipxml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="cpu_ip_blah_allplist.plist.Shared" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            # Common will be ignored
            File('_work/nvl.common/nvl_com/POR_TP/class_s68/PLIST_ALL_com.plist.xml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist.Common" />
    <PListFile name="common_blah_allplist.plist.Common" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)

            with MockVar(Integrate, 'target_die', ['nvl_cpu']):
                result = PlistFullTP().main('class_s68')

            expect_main = '''
<HdmtReferenceFile>
   <IPReference name="IP_PCH" path="./PLIST_ALL_IP_PCH.plist.ipxml" />
   <IPReference name="IP_CPU" path="./PLIST_ALL_IP_CPU.plist.ipxml" />
   <PList>
      <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist" />
      <PListFile name="pch_blah_allplist.plist" />
      <PListFile name="cpu_blah_allplist.plist" />
      <PListFile name="AAA_drv_cdie_C69_CA5P_hdmt2ippkg_class_s68g1.plist.Shared" />
      <PListFile name="cpu_blah_allplist.plist.Shared" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_cpu.plist.xml'], expect_main)

            expect_cpu = '''
<HdmtReferenceFile>
   <PList>
      <PListFile name="cpu_ip_blah_allplist.plist" />
      <PListFile name="cpu_ip_blah_allplist.plist.Shared" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_IP_CPU.plist.ipxml'], expect_cpu)

            expect_pch = '''
<HdmtReferenceFile>
   <PList>
      <PListFile name="pch_ip_blah_all_plist.plist" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_IP_PCH.plist.ipxml'], expect_pch)

    def test_read_plist(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_a.plist.xml').touch(r'''
<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\PLIST_ALL_IP_PCH.plist.ipxml" />
  <IPReference name="IP_CPU" path=".\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C28_vrevC28E0P_ippkg_class_u28g1.plist" />
    <PListFile name="PTH_BGCEP_c28_class_u28g1.plist" />
  </PList>
</HdmtReferenceFile>
''', mkdir=True)
            obj = PlistFullTP()
            dd, ipplists = obj.read_plist('nvl_cpu/POR_TP/class_s68/PLIST_ALL_a.plist.xml')
            self.assertEqual(dd,
                             ['AAA_drv_cdie_C28_vrevC28E0P_ippkg_class_u28g1.plist',
                              'PTH_BGCEP_c28_class_u28g1.plist'])
            self.assertEqual(ipplists, {'IP_PCH': r'./PLIST_ALL_IP_PCH.plist.ipxml',
                                        'IP_CPU': r'./PLIST_ALL_IP_CPU.plist.ipxml'})

            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_IP_PCH.plist.ipxml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="pch1.plist" />
  </PList>
</HdmtReferenceFile>
''')

            File('nvl_cpu/POR_TP/class_s68/PLIST_ALL_IP_CPU.plist.ipxml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="cpu1.plist" />
  </PList>
</HdmtReferenceFile>
''')
            result = obj.main('class_s68')

            expect = '''
<HdmtReferenceFile>
   <PList>
      <PListFile name="cpu1.plist" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_IP_CPU.plist.ipxml'], expect)
            expect = '''
<HdmtReferenceFile>
   <PList>
      <PListFile name="pch1.plist" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_IP_PCH.plist.ipxml'], expect)
            expect = '''
<HdmtReferenceFile>
   <IPReference name="IP_PCH" path="./PLIST_ALL_IP_PCH.plist.ipxml" />
   <IPReference name="IP_CPU" path="./PLIST_ALL_IP_CPU.plist.ipxml" />
   <PList>
      <PListFile name="AAA_drv_cdie_C28_vrevC28E0P_ippkg_class_u28g1.plist" />
      <PListFile name="PTH_BGCEP_c28_class_u28g1.plist" />
   </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(result['PLIST_ALL_a.plist.xml'], expect)

    def test_error_stpl(self):
        # case: Invalid line in stpl file.

        with TempDir(name=True, chdir=True) as tdir:
            File('nvl_gcd/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    IPName IP_GCD
    {
        Common "../../Shared/IP_GCD_BASE/IP_GCD.imp";
        "../../GCD/blahblah.txt";
        Final "./ProgramFlowsTestPlan/IP_GCD_CONCURRENT_FLOWS.mtpl";
    }
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_GXX.mtpl";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            with self.assertRaisesRegex(ErrorInput, 'Unknown line'):
                StplFullTP().main('Class_ARL_S68')

    def test_stpl_nofinal(self):
        # no final line - needed for IP only

        with TempDir(name=True, chdir=True) as tdir:
            code = '''
Version 1.0;

SubTestPlans
{
    IPName IP_GCD
    {
        Common "../../Shared/IP_GCD_BASE/IP_GCD.imp";
    }
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_GXX.mtpl";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
'''
            File('nvl_gcd/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch(code, mkdir=True)

            expect = '''
Version 1.0;

SubTestPlans
{
    IPName IP_GCD
    {
        Common "../../Shared/IP_GCD_BASE/IP_GCD.imp";
    }
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_GXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
'''
            result = StplFullTP().main('Class_ARL_S68')
            self.assertTextEqual(result, expect)

    def test_basic_stpl(self):
        # case: 2 dielets HUB and CPU stitch with common
        # case: append - IP_HUB and IP_CPU block append into one file.
        # case: remove duplication - Non-IP block has duplications in 3 files

        with TempDir(name=True, chdir=True) as tdir:
            File('nvl_cpu/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    IPName IP_CPU
    {
        Common "../../Shared/IP_CPU_BASE/IP_CPU.imp";
        "../../Shared/Modules/TPI_BASE_IPCPU/TPI_BASE_IPCPU.mtpl";
        "../../Modules/FUN_ATOM_CPU/FUN_ATOM_CPU.mtpl";
        Final "./ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl";
    }
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            File('nvl_hub/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    IPName IP_HUB
    {
        Common "../../Shared/IP_HUB_BASE/IP_HUB.imp";
        "../../Shared/Modules/TPI_BASE_IPHUB/TPI_BASE_IPHUB.mtpl";
        "../../Modules/FUN_ATOM_HUB/FUN_ATOM_HUB.mtpl";
        Final "./ProgramFlowsTestPlan/IP_HUB_CONCURRENT_FLOWS.mtpl";
    }
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl";
    "../../Modules/HELLO_COM/HELLO_COM.mtpl";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            File('nvl_com/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    "../../Modules/HELLO_COM/HELLO_COM.mtpl";
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            result = StplFullTP().main('Class_ARL_S68')
            expect = '''
Version 1.0;

SubTestPlans
{
    IPName IP_CPU
    {
        Common "../../Shared/IP_CPU_BASE/IP_CPU.imp";
        "../../Shared/Modules/TPI_BASE_IPCPU/TPI_BASE_IPCPU.mtpl";
        "../../Modules/FUN_ATOM_CPU/FUN_ATOM_CPU.mtpl";
        Final "./ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl";
    }
    IPName IP_HUB
    {
        Common "../../Shared/IP_HUB_BASE/IP_HUB.imp";
        "../../Shared/Modules/TPI_BASE_IPHUB/TPI_BASE_IPHUB.mtpl";
        "../../Modules/FUN_ATOM_HUB/FUN_ATOM_HUB.mtpl";
        Final "./ProgramFlowsTestPlan/IP_HUB_CONCURRENT_FLOWS.mtpl";
    }
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    "../../Modules/HELLO_COM/HELLO_COM.mtpl";
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
'''
            self.assertTextEqual(result, expect)

    def test_stpl_with_target_die(self):
        # case: 2 dielets HUB and CPU stitch with common
        # case: append - IP_HUB and IP_CPU block append into one file.
        # case: remove duplication - Non-IP block has duplications in 3 files

        with TempDir(name=True, chdir=True) as tdir:
            File('nvl_cpu/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    IPName IP_CPU
    {
        Common "../../Shared/IP_CPU_BASE/IP_CPU.imp";
        "../../Shared/Modules/TPI_BASE_IPCPU/TPI_BASE_IPCPU.mtpl";
        "../../Modules/FUN_ATOM_CPU/FUN_ATOM_CPU.mtpl";
        Final "./ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl";
    }
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            File('nvl_hub/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    IPName IP_HUB
    {
        Common "../../Shared/IP_HUB_BASE/IP_HUB.imp";
        "../../Shared/Modules/TPI_BASE_IPHUB/TPI_BASE_IPHUB.mtpl";
        "../../Modules/FUN_ATOM_HUB/FUN_ATOM_HUB.mtpl";
        Final "./ProgramFlowsTestPlan/IP_HUB_CONCURRENT_FLOWS.mtpl";
    }
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl";
    "../../Modules/HELLO_COM/HELLO_COM.mtpl";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            # Common will be ignored
            File('nvl_com/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    "../../Modules/HELLO_COM/HELLO_COM.mtpl.Common";
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl.Common";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl.Common";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            # Shared
            File('nvl_cpu/Shared/POR_TP/Class_ARL_S68/SubTestPlan.stpl').touch('''
Version 1.0;

SubTestPlans
{
    IPName IP_CPU
    {
        Common "../../Shared/IP_CPU_BASE/IP_CPU.imp";
        "../../Shared/Modules/TPI_BASE_IPCPU/TPI_BASE_IPCPU.mtpl.Shared";
        "../../Modules/FUN_ATOM_CPU/FUN_ATOM_CPU.mtpl.Shared";
        Final "./ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl";
    }
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl.Shared";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl.Shared";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)

            with MockVar(Integrate, 'target_die', ['nvl_cpu']):
                result = StplFullTP().main('Class_ARL_S68')
            expect = '''
Version 1.0;

SubTestPlans
{
    IPName IP_CPU
    {
        Common "../../Shared/IP_CPU_BASE/IP_CPU.imp";
        "../../Shared/Modules/TPI_BASE_IPCPU/TPI_BASE_IPCPU.mtpl.Shared";
        "../../Shared/Modules/TPI_BASE_IPCPU/TPI_BASE_IPCPU.mtpl";
        "../../Modules/FUN_ATOM_CPU/FUN_ATOM_CPU.mtpl.Shared";
        "../../Modules/FUN_ATOM_CPU/FUN_ATOM_CPU.mtpl";
        Final "./ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl";
    }
    IPName IP_HUB
    {
        Common "../../Shared/IP_HUB_BASE/IP_HUB.imp";
        "../../Shared/Modules/TPI_BASE_IPHUB/TPI_BASE_IPHUB.mtpl";
        "../../Modules/FUN_ATOM_HUB/FUN_ATOM_HUB.mtpl";
        Final "./ProgramFlowsTestPlan/IP_HUB_CONCURRENT_FLOWS.mtpl";
    }
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl.Shared";
    "../../Shared/Modules/TPI_XIU_XXX/TPI_XIU_XXX.mtpl";
    "../../Modules/HELLO_COM/HELLO_COM.mtpl";
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl.Shared";
    "../../Modules/FUS_FUSECFG_CXX/FUS_FUSECFG_CXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
'''
            self.assertTextEqual(result, expect)

    def test_basic_env(self):
        # case: Two dielet stitch with common
        # case: append   - see I:/COM and I:/CPU in P3_PRODUCT_FOLDERS
        # case: override - see PLIST_BURST_OPTION_PXR_CHECK_DISABLE
        # case: remove duplication - see A0_NORTH, A0_SOUTH and B0 items in P3_PRODUCT_FOLDERS
        # case: new key: - see COM_VAR as example

        with TempDir(name=True, chdir=True) as tdir:
            # note: nvl_hub is the first to read
            File('nvl_hub/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
HUB_VAR = "TRUEHUB";

P3_PRODUCT_FOLDERS = "I:/hdmxpats/mtl/blueline_config/CSXS/A0_NORTH;" +
    "I:/hdmxpats/mtl/blueline_config/CSXS/A0_SOUTH;" +
    "I:/hdmxpats/mtl/blueline_config/CGSM/B0";
''', mkdir=True)

            File('nvl_cpu/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";

P3_PRODUCT_FOLDERS = "I:/hdmxpats/mtl/blueline_config/CSXS/A0_NORTH;" +
    "I:/hdmxpats/mtl/blueline_config/CSXS/A0_SOUTH;" +
    "I:/CPU;;" +
    "I:/hdmxpats/mtl/blueline_config/CGSM/B0";
''', mkdir=True)

            # nvl_com is ignored!
            File('nvl_com/BaseInputs/EnvironmentFile_Common.env').touch('''
COM_VAR = "TRUECOM";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "FINAL";

P3_PRODUCT_FOLDERS = "I:/hdmxpats/mtl/blueline_config/CSXS/A0_NORTH;" +
    "I:/hdmxpats/mtl/blueline_config/CSXS/A0_SOUTH;" +
    "I:/COM;" +
    "I:/hdmxpats/mtl/blueline_config/CGSM/B0";
''', mkdir=True)

            result = EnvFullTP().main('Class_ARL_S68')
            expect = '''
HUB_VAR = "TRUEHUB";

P3_PRODUCT_FOLDERS = "I:/hdmxpats/mtl/blueline_config/CSXS/A0_NORTH;" +
    "I:/hdmxpats/mtl/blueline_config/CSXS/A0_SOUTH;" +
    "I:/CPU;" +
    "I:/hdmxpats/mtl/blueline_config/CGSM/B0";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";

'''
            self.assertTextEqual(result, expect)

    def test_env_keeplast(self):
        # Due to supercede, keep the last element

        with TempDir(name=True, chdir=True) as tdir:
            # note: nvl_hub is the first to read
            File('nvl_hub/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "HUBITEM1";

VAR2 = "HUBITEM2;" +
       "HUBITEM3";
''', mkdir=True)

            File('nvl_cpu/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "CPUITEM1";

VAR2 = "CPUITEM2;" +
       "CPUITEM3";
''', mkdir=True)

            # nvl_com is ignored!
            File('_work/nvl.common/nvl.common/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "COMITEM1";

VAR2 = "COMITEM2;" +
       "COMITEM3";
''', mkdir=True)

            result = EnvFullTP().main('Class_ARL_S68')
            expect = '''
VAR1 = "COMITEM1";

VAR2 = "HUBITEM2;" +
    "CPUITEM2;" +
    "CPUITEM3;" +
    "COMITEM2;" +
    "COMITEM3;" +
    "HUBITEM3";
'''
            self.assertTextEqual(result, expect)

    def test_env_fulltp_target_die(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('nvl_hub/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "HUBITEM1";

VAR2 = "HUBITEM2;" +
       "HUBITEM3";
''', mkdir=True)

            File('nvl_cpu/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "CPUITEM1";

VAR2 = "CPUITEM2;" +
       "CPUITEM3";
''', mkdir=True)

            File('nvl_gcd/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "GCDITEM1";

VAR2 = "GCDITEM2;" +
       "GCDITEM3";
''', mkdir=True)

            File('nvl_pcd/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "PCDITEM1";

VAR2 = "PCDITEM2;" +
       "PCDITEM3";
''', mkdir=True)

            # nvl_com is ignored!
            File('_work/nvl_common/nvl_common/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "COMITEM1";

VAR2 = "COMITEM2;" +
       "COMITEM3";
''', mkdir=True)

            # Shared
            File('nvl_hub/Shared/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "HUBITEM1SHARED";

VAR2 = "HUBITEM2SHARED;" +
       "HUBITEM3SHARED";
''', mkdir=True)

            File('nvl_cpu/Shared/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "CPUITEM1SHARED";

VAR2 = "CPUITEM2SHARED;" +
       "CPUITEM3SHARED";
''', mkdir=True)

            File('nvl_gcd/Shared/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "GCDITEM1SHARED";

VAR2 = "GCDITEM2SHARED;" +
       "GCDITEM3SHARED";
''', mkdir=True)

            File('nvl_pcd/Shared/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "PCDITEM1SHARED";

VAR2 = "PCDITEM2SHARED;" +
       "PCDITEM3SHARED";
''', mkdir=True)

            # nvl_com is ignored!
            File('_work/nvl_common/nvl_common/Shared/POR_TP/Class_ARL_S68/EnvironmentFile.env').touch('''
VAR1 = "COMITEM1SHARED";

VAR2 = "COMITEM2SHARED;" +
       "COMITEM3SHARED";
''', mkdir=True)
            with MockVar(Integrate, 'target_die', ['nvl_hub']):
                result = EnvFullTP().main('Class_ARL_S68')

            expect = '''
VAR1 = "HUBITEM1SHARED";

VAR2 = "GCDITEM2;" +
    "HUBITEM2;" +
    "HUBITEM3;" +
    "PCDITEM2;" +
    "PCDITEM3;" +
    "CPUITEM2;" +
    "CPUITEM3;" +
    "HUBITEM2SHARED;" +
    "HUBITEM3SHARED;" +
    "GCDITEM3";
'''
            self.assertTextEqual(result, expect)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_fulltp_only(self):
        # Mock up testing fulltp only routine.

        File('Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py').touch('''
    unit test example
    MAIN_code = """
    # FULLTPONLY: PTH
    # FULLTPONLY: SCN
    START_SubFlow                 TPI_FLWFLGS_XXX                                      rm2fm2 rm1fm1 r0f0 r2p1
    START_SubFlow                 TPI_BASE_XXX                                         {pkg_stdports}
    START_SubFlow                 TPI_PWRUP_XXX::TPI_PWRUP_XXX_PWRUPDC_START           {dc_stdports}
    START_SubFlow                 TPI_VCC_XXX                                          rm2fm2 rm1fm1 r0f0 r2f2
    """
    unit test example
    ''', mkdir=True)

        File('POR_TP/TGLH81/SkipModules/Readme.txt').touch('''
    UNIT_TEST_EXAMPLE
    ''', mkdir=True)

        # case 1: onlylist not empty. Done
        onlylist1 = ['Something']
        result1 = NVLBuildTP.fulltp_only(self, onlylist1)
        self.assertEqual(result1, 1)

        # case 2: onlylist is empty. But Full TP. Done
        onlylist2 = None
        with MockVar(Integrate, 'get_valid_die', Mock(return_value=['cpu', 'gcd', 'hub', 'pcd'])):
            result2 = NVLBuildTP.fulltp_only(self, onlylist2)
        self.assertEqual(result2, 2)

        # case 3: onlylist is empty. Partial TP.
        onlylist3 = None
        self.bom = 'TGLH81'
        env = f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'
        self.tpobj = TestProgram(env).init()
        with MockVar(Integrate, 'get_valid_die', Mock(return_value=['cpu', 'gcd'])):
            result3 = NVLBuildTP.fulltp_only(self, onlylist3)
        self.assertEqual(set(os.listdir('POR_TP/TGLH81/SkipModules')), {'Readme.txt', 'PTH.txt', 'SCN.txt'})

    @with_(MockVar, ModuleSkip, 'is_module_skipped', True)
    def test_subdef_reduce(self):
        # Test bindef_reduce
        module_list = ['DRV_RESET_CXX', 'FUS_UNITINFO_CXX', 'PTH_BGR_CXPKGS7', 'TPI_EDM_XXX', 'TPI_VCC_XXX']
        with TempDir(chdir=True, name=True) as tdir:
            actual_file = f'BaseInputs/CPU/CPU_Files/IPC_SubBindef.imp'
            File(actual_file).touch('''
Version 1.0;

Import "../../Modules/DRV_RESET_CXX/DRV_RESET_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/FUS/FUS_UNITINFO_CXX/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/TPI/BLAHBLAH/BLAH_SubBinDefinitions.sbdefs";
Import "../../Modules/PTH/PTH_BGR_CXPKGS7/PTH_BGR_CXPKGS7_SubBinDefinitions.sbdefs";
''', mkdir=True)
            NVLBuildTP.subdef_reduce(tdir, module_list)

            expect = '''
Version 1.0;

Import "../../Modules/DRV_RESET_CXX/DRV_RESET_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/FUS/FUS_UNITINFO_CXX/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/PTH/PTH_BGR_CXPKGS7/PTH_BGR_CXPKGS7_SubBinDefinitions.sbdefs";
'''
            self.assertTextEqual(File(actual_file).read(), expect)

            # Test bindef_reduce tpswitch2
            with MockVar(os.environ, 'TPSWITCH2', 'True'):
                self.assertEqual(NVLBuildTP.subdef_reduce(tdir, module_list), 1)

    def test_bindef_shared_bin(self):
        # Test bindef_shared_bin
        with TempDir(startcopy=f'{UT_DIR_REPO}/subbindef_reduce2_test', chdir=True):
            module_list = glob.glob(f'Modules/*/*.mtpl')

            mtpl_obj = {}
            for item in module_list:
                mtpl_obj[f'XXX_{item}'] = item

            gold_file = f'{UT_DIR_REPO}/subbindef_reduce2_test/Modules/CLK_BASE_HXNVL/CLK_BASE_HXNVL.mtpl.gold'
            actual_file = f'Modules/CLK_BASE_HXNVL/CLK_BASE_HXNVL.mtpl'
            NVLBuildTP.bindef_shared_bin(mtpl_obj)
            self.assertGoldEqual(actual_file, gold_file)

            gold_file = f'{UT_DIR_REPO}/subbindef_reduce2_test/Modules/CLK_BASE_HXNVL/CLK_BASE_HXNVL_SubBinDefinitions.sbdefs.gold'
            actual_file = f'Modules/CLK_BASE_HXNVL/CLK_BASE_HXNVL_SubBinDefinitions.sbdefs'
            self.assertGoldEqual(actual_file, gold_file)

    def test_copy_to_idrive(self):
        with TempDir(name=True) as tdir, \
                TempDir(name=True) as outdir:
            File(f'{tdir}/dir1/blah.txt').touch(mkdir=True)

            # non-pr
            self.assertEqual(Integrate.copy_to_idrive(tdir), 3)

            # PR, no special keyword
            with MockVar(os.environ, 'FROM_PR', 'TRUE'), \
                    MockVar(os.environ, 'REPO_DIR', tdir), \
                    MockVar(GitHub, 'get_pr_view_output', Mock(return_value='blah')):
                self.assertEqual(Integrate.copy_to_idrive(tdir), 2)
                self.assertEqual(os.listdir(outdir), [])

            # PR, with keyword
            with MockVar(os.environ, 'FROM_PR', 'TRUE'), \
                    MockVar(os.environ, 'REPO_DIR', tdir), \
                    MockVar(GitHub, 'get_pr_view_output', Mock(return_value=f'\nSAVE_TO_IDRIVE: {outdir}/x\n')):
                self.assertEqual(Integrate.copy_to_idrive(tdir), 1)
                self.assertEqual([Env.xpath(x) for x in glob.glob(f'{outdir}/*/*/*')], [Env.xpath(f'{outdir}/x/dir1/blah.txt')])

    def test_get_valid_die(self):
        # default
        self.assertEqual(Integrate.get_valid_die(), ['gcd', 'hub', 'pcd', 'cpu'])

        # partial
        with MockVar(os.environ, 'GCD_Branch', 'none'):
            self.assertEqual(Integrate.get_valid_die(), ['hub', 'pcd', 'cpu'])

        # dielet1
        with MockVar(Integrate, 'target_die', ['nvl.gcd']):
            self.assertEqual(Integrate.get_valid_die(), ['hub', 'pcd', 'cpu', 'gcd'])

        # dielet2
        with MockVar(Integrate, 'target_die', ['nvl.cpu']):
            self.assertEqual(Integrate.get_valid_die(), ['gcd', 'hub', 'pcd', 'cpu'])

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple_disagg1')
    def test_get_csvfile_list(self):
        with TempDir(name=True, chdir=True) as tdir:

            File('nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/gcd/module_instances.csv').copy(
                'nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl.gcd/Shared/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/com/module_instances.csv').copy(
                'nvl.gcd/Shared/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            output_path = f'{tdir}/output/module_instances.csv'
            File(output_path).touch('''blahblah''', mkdir=True)

            # Case 1, in gcd dielet repo
            with MockVar(Integrate, 'target_die', ['nvl.gcd']):
                csvlist_res1 = CSVCombiner(output_path).get_csvfile_list('class_nvl_28c', 'module_instances')
                expect1 = ['nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv',
                           'nvl.gcd/Shared/POR_TP/class_nvl_28c/Reports/module_instances.csv']
                self.assertEqual([Env.xpath(x) for x in csvlist_res1], expect1)

            # Case 2, in com repo, non-full TP hub and gcd die-combo
            File('_work/nvl_common/nvl_common/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/com/module_instances.csv').copy(
                '_work/nvl_common/nvl_common/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/hub/module_instances.csv').copy(
                'nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            csvlist_res2 = CSVCombiner(output_path).get_csvfile_list('class_nvl_28c', 'module_instances')
            expect2 = ['nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv',
                       'nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv',
                       '_work/nvl_common/nvl_common/POR_TP/class_nvl_28c/Reports/module_instances.csv']
            self.assertEqual([Env.xpath(x) for x in csvlist_res2], expect2)

            # Case 3, in com repo, full TP
            File('nvl_cpu/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/cpu/module_instances.csv').copy(
                'nvl_cpu/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_pcd/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/pcd/module_instances.csv').copy(
                'nvl_pcd/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            csvlist_res3 = CSVCombiner(output_path).get_csvfile_list('class_nvl_28c', 'module_instances')
            expect3 = ['nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv',
                       'nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv',
                       'nvl_pcd/POR_TP/class_nvl_28c/Reports/module_instances.csv',
                       'nvl_cpu/POR_TP/class_nvl_28c/Reports/module_instances.csv',
                       '_work/nvl_common/nvl_common/POR_TP/class_nvl_28c/Reports/module_instances.csv']
            self.assertEqual([Env.xpath(x) for x in csvlist_res3], expect3)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple_disagg1')
    def test_csv_merge(self):
        # Check the full TP csv merge feature. above test_get_csvfile_list cover the csv list.
        with TempDir(name=True, chdir=True) as tdir:
            File('_work/nvl_common/nvl_common/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/com/module_instances.csv').copy(
                '_work/nvl_common/nvl_common/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/hub/module_instances.csv').copy(
                'nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/gcd/module_instances.csv').copy(
                'nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_cpu/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/cpu/module_instances.csv').copy(
                'nvl_cpu/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_pcd/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/pcd/module_instances.csv').copy(
                'nvl_pcd/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            output_path = f'{tdir}/output/module_instances.csv'
            File(output_path).touch('''blahblah''', mkdir=True)

            # Check the script reaching end
            result = CSVCombiner(output_path).main('class_nvl_28c', 'module_instances')
            self.assertEqual(result, 9)

            # Read the writing csv file to check.
            with open(output_path, newline='', encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
            expect = [
                {'ipname': '', 'module': 'ARR_CORE_CK816',
                 'instance': 'ALL_X_HRY_E_BEGINCPUPKG_X_VCCIA_X_X_X_ALL_PRESCREEN', 'flow type': 'MainFlow'},
                {'ipname': '', 'module': 'DRV_RESET_PKS', 'instance': 'RESET_PKS_PATMOD_E_INIT_X_X_X_X_MPFUN_DMI',
                 'flow type': 'InitFlow'},
                {'ipname': '', 'module': 'DRV_RESET_XXX', 'instance': 'RESET_X_FUNC_K_BEGIN_X_X_X_X_FBIST_H2G',
                 'flow type': 'MainFlow'},
                {'ipname': '', 'module': 'MIO_D2D_XXX', 'instance': 'FBIST_D2D_FUNC_K_BEGIN_X_X_MIN_X_HUB_CPU_ALL',
                 'flow type': 'MainFlow'},
                {'ipname': '', 'module': 'YBS_UPSS_XXX', 'instance': 'AFORK_X_SCREEN_K_END_X_X_X_X_X',
                 'flow type': 'MainFlow'},
                {'ipname': 'IPC', 'module': 'SCN_ATOM_CX816', 'instance': 'CTRL_X_PATMOD_K_INIT_X_X_X_X_GLOBAL_INIT',
                 'flow type': 'InitFlow'},
                {'ipname': 'IPG', 'module': 'ARR_GT_GXX', 'instance': 'ARR_GT_DEDC_K_INIT_X_X_X_X_CONFIG',
                 'flow type': 'InitFlow'},
                {'ipname': 'IPH', 'module': 'ARR_HUB_HXNVL', 'instance': 'X_HUB_DEDC_K_INIT_X_X_X_X_CONFIG_CONFIG',
                 'flow type': 'InitFlow'},
                {'ipname': 'IPH', 'module': 'FUN_HUB_HKNVL', 'instance': 'FUN_HUB_DEDC_K_INIT_X_X_X_X_DEDC_CFG',
                 'flow type': 'InitFlow'},
                {'ipname': 'IPP', 'module': 'ARR_MBIST_PXS', 'instance': 'CCR_MBIST_SCRB_K_PCDMIN0_X_X_MIN_X',
                 'flow type': 'MainFlow'}]
            self.assertCountEqual(reader, expect)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple_disagg1')
    def test_csv_merge_fail_header(self):
        # Check the full TP csv merge feature. above test_get_csvfile_list cover the csv list.
        with TempDir(name=True, chdir=True) as tdir:
            File('_work/nvl_common/nvl_common/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''ipname,module,instance,wrong header''', mkdir=True)

            File('nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/hub/module_instances.csv').copy(
                'nvl_hub/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/gcd/module_instances.csv').copy(
                'nvl_gcd/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_cpu/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/cpu/module_instances.csv').copy(
                'nvl_cpu/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            File('nvl_pcd/POR_TP/class_nvl_28c/Reports/module_instances.csv').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/pcd/module_instances.csv').copy(
                'nvl_pcd/POR_TP/class_nvl_28c/Reports/module_instances.csv')

            output_path = f'{tdir}/output/module_instances.csv'
            File(output_path).touch('''blahblah''', mkdir=True)

            with self.assertRaisesRegex(Exception, "header is not the same with previous file"):
                CSVCombiner(output_path).main('class_nvl_28c', 'module_instances')

    def test_fulltp_moduleinstance_csv(self):
        with TempDir(chdir=True, startcopy=f'{UT_DIR_REPO}/Simple_disagg2a', name=True) as tdir:
            File(f'{tdir}/output/POR_TP/class_nvl_28c/ProgramFlowsTestPlan/ProgramFlows.mtpl').touch('''blahblah''', mkdir=True)
            File(f'{UT_DIR_REPO}/csvreport_unittest/ProgramFlows.mtpl').copy(
                f'{tdir}/output/POR_TP/class_nvl_28c/ProgramFlowsTestPlan/ProgramFlows.mtpl')

            # case 1 - not full tp
            with MockVar(Integrate, 'get_valid_die', Mock(return_value=['cpu', 'gcd', 'pcd'])):
                result1 = Integrate('class_nvl_28c').fulltp_moduleinstance_csv(f'{tdir}/output')
                self.assertEqual(result1, 8)

            with MockVar(Integrate, 'get_valid_die', Mock(return_value=['cpu', 'gcd', 'hub', 'pcd'])), \
                    MockVar(SystemCall, 'run', Mock()):
                result2 = Integrate('class_nvl_28c').fulltp_moduleinstance_csv(f'{tdir}/output')
                self.assertEqual(result2, 7)

    def test_is_valid_tpname(self):
        # Invalid TP name - only 14 chars
        invalid_tpname_short = 'NVLB0H02A0TS604'
        result1 = NVLBuildTP.is_valid_tpname(invalid_tpname_short)
        self.assertFalse(result1)

        # Invalid TP name - not following pattern
        invalid_tpname_not_match = 'NVLS756B0HPTH0TS604'
        result2 = NVLBuildTP.is_valid_tpname(invalid_tpname_not_match)
        self.assertFalse(result2)

        # Valid TP name
        valid_tpname = 'NVLS756B0H02A0TS604'
        result3 = NVLBuildTP.is_valid_tpname(valid_tpname)
        self.assertTrue(result3)

    def test_get_pr_report_file(self):
        previous_tp = '15W0A'
        with TempDir(name=True, chdir=True) as tdir:
            pr_report_path = f'{tdir}/HX_15W0B.json'
            tp_path = f'{tdir}/NVLS567A0H15W0BHX07'
            final_report_file = f'{tp_path}/POR_TP/Class_NVL_S16C/Reports/HX_15W0B.json'
            mkdirs(f'{tdir}/POR_TP/Class_NVL_S16C/Reports')
            File(pr_report_path).touch('blahblah', mkdir=True)
            with MockVar(NVLBuildTP, 'bom', 'Class_NVL_S16C'), \
                    MockVar(NVLBuildTP, 'outdir', tp_path), \
                    patch('main.nvl_buildtp.NVLBuildTP.__init__', return_value=None), \
                    patch('main.nvl_buildtp.main_pr_integrate', Mock()), \
                    patch('main.nvl_buildtp.return_report_file', Mock(return_value=pr_report_path)), \
                    CaptureStdoutLog() as p:
                NVLBuildTP('Class_NVL_S16C').get_pr_report_file(previous_tp)

            expect = r'Copying PR report to: ./POR_TP/Class_NVL_S16C/Reports'
            self.assertRegex(p.getvalue(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
