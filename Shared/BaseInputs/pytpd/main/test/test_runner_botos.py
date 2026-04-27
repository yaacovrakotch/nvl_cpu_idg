#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for runner_botos
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from unittest.mock import MagicMock
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from main.nvl_buildtp import NVLBuildTP
from main.runner_botos import *
from main.msbuild import MSBuild
import main.runner_botos as runner_botos
from os.path import join, dirname, abspath
from pprint import pprint
import os
import json


class TestRunner(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        called = []

        def fakebuild(slf, yy, xx):
            File(f'{xx}/this_is_my_tp.tpl').touch()
            File(f'{xx}/Module/ARR/arr.mtpl').touch(mkdir=True)

        def fakelabel(input):
            called.append(input)

        # assume do_nvl2_build works
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            File('POR_TP/Class_MTL_P28').touch(mkdir=True)
            mkdirs(f'{tdir}/completed')
            with MockVar(sys, "argv", ['runner_botos.py', 'nvl2_tpbot.nvls28c.nvl_cpu']), \
                    MockVar(RunnerBotOS, 'get_timestamp_msec', Mock(return_value=111)), \
                    MockVar(RunnerBotOS, 'do_nvl2_build', Mock()):
                obj = RunnerBotOS()
                obj.root = tdir
                text = '''{
"site": "JF",
"logfile": "/blah/11-17-28/1_1_B.txt",
"INIT log": "/blah/11-17-28/loadlog_11_17.txt",
"tprolling": "/tprol",
"code": _E_
}'''
                File(f'{tdir}/completed/111_B.json').touch(text.replace('_E_', '0'))

                # case: pass
                pr_view = 'number: 3\nauthor: jdr\n'
                with MockVar(GitHub, 'add_labels', fakelabel), \
                        MockVar(GitHub, 'pr_view_output', pr_view),\
                        CaptureStdoutLog() as p:
                    obj.main()

                result = glob.glob(f'{tdir}/*/*/*')
                pprint(result)
                self.assertEqual(set(result), {f'{tdir}/staging/nvlp28/8000_111_B.tar.gz',
                                               f'{tdir}/staging/_metadata/111_B.json'})
                self.assertEqual(called, [])     # [{'PASSED_Si'}])

                # check contents of metadata
                expect = f'''
{{
    "job": "3",
    "repo": "nvl_cpu",
    "url": "",
    "author": "jdr",
    "pkg": "nvlp28",
    "email": "",
    "site": "JF",
    "team": "",
    "tester": "Any"
}}
'''
                self.assertTextEqual(File(f'{tdir}/staging/_metadata/111_B.json').read(), expect)

                expect = f'''
-i- affected_boms(): ['Class_MTL_P28']
-i- encoded_bom: Class_MTL_P28
-i- final_cmd:   nvl2_tpbot.Class_MTL_P28.nvl_cpu
-i- Starting TP Build
-i- Starting TP tar
-i- Written Class_MTL_P28: {tdir}/staging/nvlp28/8000_111_B.tar.gz
{{'author': 'jdr',
 'email': '',
 'job': '3',
 'pkg': 'nvlp28',
 'repo': 'nvl_cpu',
 'site': 'JF',
 'team': '',
 'tester': 'Any',
 'url': ''}}

Summary: ===============
-i- Written Class_MTL_P28: {tdir}/staging/nvlp28/8000_111_B.tar.gz

-i- Will wait for botos to finish: completed/111_B
######### 111_B.json (Class_MTL_P28):
INIT log:
   Path:        /tprol/loadlog_11_17.txt
   Direct link: https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./11-17-28/loadlog_11_17.txt
listener (script) log file:
   Path:        /blah/11-17-28/1_1_B.txt
   Direct link: https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./11-17-28/1_1_B.txt
trace lot#s: None
exit code:   0
Result:      None
'''
                result = '\n'.join(x for x in p.getvalue().split('\n') if '-z-' not in x)
                self.assertTextEqual(result, expect)

                # case: fail si case
                File(f'{tdir}/completed/111_B.json').touch(text.replace('_E_', '1'), newfile=True)
                called = []
                obj = RunnerBotOS()
                obj.root = tdir
                with MockVar(GitHub, 'add_labels', fakelabel):
                    with self.assertRaises(SystemExit):
                        obj.main()
                self.assertEqual(called, [{'FAILED_MP28'}])

                # case: timeout and single print
                RunnerBotOS.SLEEP_SEC = 0.001
                RunnerBotOS.MAX_WAIT_SECS = 0.01
                obj = RunnerBotOS()
                obj.root = tdir
                File(f'{tdir}/completed/111_B.json').unlink()
                with MockVar(GitHub, 'add_labels', fakelabel), \
                        self.assertRaisesRegex(ErrorUser, 'Timeout occurred while waiting'), \
                        CaptureStdoutLog() as p:
                    obj.main()

                result = [line for line in p.getvalue().split('\n') if 'Waiting for' in line]
                self.assertEqual(len(result), 1)

                # case - multi print
                obj = RunnerBotOS()
                obj.root = tdir
                with MockVar(GitHub, 'add_labels', fakelabel), \
                    self.assertRaisesRegex(ErrorUser, 'Timeout occurred while waiting'), \
                        MockVar(RunnerBotOS, 'PRINT_EVERY_SEC', 0), \
                        CaptureStdoutLog() as p:
                    obj.main()

                result = [line for line in p.getvalue().split('\n') if 'Waiting for' in line]
                self.assertGreater(len(result), 7)

                # add_tpbot_wait check
                obj.metafnames = {}
                obj.add_tpbot_wait('B', 'abc', 'BOM1')
                self.assertEqual(obj.metafnames, {'abc': 'BOM1'})
                obj.add_tpbot_wait('E', 'def', 'BOM1')
                self.assertEqual(obj.metafnames, {'abc': 'BOM1'})
                obj.add_tpbot_wait('D', 'ghi', 'BOM1')
                self.assertEqual(obj.metafnames, {'abc': 'BOM1'})

    @with_(TempDir, chdir=True)
    def test_affected_boms_pr(self):
        File('POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
        File('POR_TP/Class_NVL_S52C/EnvironmentFile.env').touch(mkdir=True)
        File('POR_TP/Class_NVL_HX28C/EnvironmentFile.env').touch(mkdir=True)

        # one affected bom
        with MockVar(os.environ, 'REPO_DIR', '.'), \
                MockVar(AffectedBom, '_get_modified_files', Mock(return_value=[])), \
                MockVar(AffectedBom, 'main', Mock(return_value=['Class_NVL_HX28C'])):
            self.assertEqual(RunnerBotOS.affected_boms(), ['Class_NVL_HX28C'])

        # affected bom does not match
        with MockVar(os.environ, 'REPO_DIR', '.'), \
                MockVar(AffectedBom, '_get_modified_files', Mock(return_value=[])), \
                MockVar(AffectedBom, 'main', Mock(return_value=['Class_NVL_AX'])):
            self.assertEqual(RunnerBotOS.affected_boms(), [])

        # reference baseline
        self.assertEqual(RunnerBotOS.affected_boms(),
                         ['Class_NVL_HX28C', 'Class_NVL_S28C', 'Class_NVL_S52C'])

        # cmd
        with MockVar(os.environ, 'TARGETBOM', 'Class_NVL_S28C'):
            with MockVar(os.environ, 'REPO_DIR', '.'), \
                    MockVar(AffectedBom, '_get_modified_files', Mock(return_value=[])), \
                    MockVar(AffectedBom, 'main', Mock(return_value=['Class_NVL_S28C'])):
                self.assertEqual(RunnerBotOS.affected_boms(cmd='nvl2_mbot._ALL_.nvl_dielet'),
                                 ['nvl2_mbot.nvls28c.Class_NVL_S28C'])

        with MockVar(os.environ, 'TARGETBOM', 'Class_NVL_S28C'):
            with MockVar(os.environ, 'REPO_DIR', '.'), \
                    MockVar(AffectedBom, '_get_modified_files', Mock(return_value=[])), \
                    MockVar(AffectedBom, 'main', Mock(return_value=['Class_NVL_AX'])):
                self.assertEqual(RunnerBotOS.affected_boms(cmd='nvl2_mbot._ALL_.nvl_dielet'),
                                 [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_affected_boms(self):
        with Chdir(f'{UT_DIR}/MTLXXXXXXX19M0KSXXX'):
            # non-NVL
            self.assertEqual(RunnerBotOS.affected_boms(), ['Class_MTL_P28', 'Class_MTL_P68'])
            self.assertEqual(RunnerBotOS.affected_boms(is_tpbot=True), ['Class_MTL_P28', 'Class_MTL_P68'])
            self.assertEqual(RunnerBotOS.affected_boms('None'), ['Class_MTL_P28', 'Class_MTL_P68'])
            self.assertEqual(RunnerBotOS.affected_boms('ABC'), ['ABC'])

            # TARGETBOM (mbot runs)
            with MockVar(os.environ, 'TARGETBOM', 'Class_MTL_P28'):
                self.assertEqual(RunnerBotOS.affected_boms(cmd='nvl2_mbot._ALL_.nvl_dielet'),
                                 ['nvl2_mbot.mtlp28.Class_MTL_P28'])
            with MockVar(os.environ, 'TARGETBOM', 'Class_MTL_P28'):
                self.assertEqual(RunnerBotOS.affected_boms(cmd='nvl2_mbot._ALL_.nvl_dielet.nvls28'),
                                 ['nvl2_mbot.nvls28.Class_MTL_P28'])
            with MockVar(os.environ, 'TARGETBOM', 'ALL'):
                self.assertEqual(RunnerBotOS.affected_boms(cmd='nvl2_mbot._ALL_.nvl_dielet'),
                                 ['nvl2_mbot.mtlp28.Class_MTL_P28', 'nvl2_mbot.mtlp68.Class_MTL_P68'])
            with MockVar(os.environ, 'TARGETBOM', 'BLAH'):
                with self.assertRaisesRegex(ErrorUser, 'Input BOM .BLAH. is invalid'):
                    RunnerBotOS.affected_boms()

        # NVL - without bots file
        with TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
            File('POR_TP/Class_NVL_S52C/EnvironmentFile.env').touch(mkdir=True)
            File('POR_TP/Class_NVL_HX28C/EnvironmentFile.env').touch(mkdir=True)
            self.assertEqual(RunnerBotOS.affected_boms(),
                             ['Class_NVL_HX28C', 'Class_NVL_S28C', 'Class_NVL_S52C'])
            self.assertEqual(RunnerBotOS.affected_boms(is_tpbot=True),
                             ['Class_NVL_HX28C', 'Class_NVL_S28C', 'Class_NVL_S52C'])

        # NVL - with bots file
        with TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/Class_NVL_S28C/InputFiles/bot.aa.nvls28c').touch(mkdir=True)
            File('POR_TP/Class_NVL_S28C/InputFiles/bot.bb.nvls28c').touch(mkdir=True)
            File('POR_TP/Class_NVL_S52C/InputFiles/bot.aa.nvls28c').touch(mkdir=True)
            File('POR_TP/Class_NVL_HX28C/InputFiles/bot.cc.nvls28c').touch(mkdir=True)
            self.assertEqual(RunnerBotOS.affected_boms(),
                             ['Class_NVL_HX28C', 'Class_NVL_S28C', 'Class_NVL_S52C'])
            self.assertEqual(RunnerBotOS.affected_boms(is_tpbot=True),
                             ['cc.nvls28c.Class_NVL_HX28C',
                              'aa.nvls28c.Class_NVL_S28C',
                              'bb.nvls28c.Class_NVL_S28C',
                              'aa.nvls28c.Class_NVL_S52C'])

    def test_copy_tp(self):
        self.assertEqual(RunnerBotOS.copy_tp(None, "", ''), 1)
        self.assertEqual(RunnerBotOS.copy_tp(None, "I:/", ''), 1)

        # dest exist
        with TempDir(name=True) as tdir:
            RunnerBotOS.copy_tp(f'{UT_DIR_REPO}/misc_files/job_dummy.tar.gz', tdir, '')
            self.assertEqual(set(os.listdir(tdir)), {'POR_TP'})
            self.assertTrue(isdir(f'{tdir}.1'))
            os.rmdir(f'{tdir}.1')

            # dest does not exist
            RunnerBotOS.copy_tp(f'{UT_DIR_REPO}/misc_files/job_dummy.tar.gz', f'{tdir}/out', '')
            self.assertEqual(set(os.listdir(tdir)), {'POR_TP', 'out'})
            self.assertEqual(set(os.listdir(f'{tdir}/out')), {'POR_TP'})

            # ASIS
            self.assertEqual(RunnerBotOS.copy_tp(f'{UT_DIR_REPO}/misc_files/job_dummy.tar.gz', f'{tdir}/out', 'ASIS'), 2)

    def inc_metafname(self):
        self.assertEqual(RunnerBotOS._incmeta('12345_E'), '12346_E')

    def test_tpbot_wait_retest(self):
        # tester retest cases

        called = []
        RunnerBotOS.SLEEP_SEC = 0.001
        RunnerBotOS.MAX_WAIT_SECS = 0.01

        def fakelabel(input):
            called.append(input)

        pr_view = 'number: 3\nauthor: jdr\n'
        with TempDir(name=True) as tdir, \
                TempDir(name=True) as tdir2a, \
                TempDir(name=True) as tdir3, \
                MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']), \
                MockVar(GitHub, 'add_labels', fakelabel), \
                MockVar(GitHub, 'pr_view_output', pr_view):
            obj = RunnerBotOS()
            obj.root = tdir
            mkdirs(f'{obj.root}/staging/_metadata')

            text = '''{
"site": "JF",
"logfile": "/blah/11-17-28/1_1_B.txt",
"INIT log": "/blah/11-17-28/loadlog_11_17.txt",
"tprolling": "/tprol",
"tester": "JF: tester1",
"code": _E_
}'''
            data = json.loads(text.replace('_E_', '1'))
            del data['tester']
            del data['code']
            File(f'{tdir}/tpbot_count/tglpkg').touch('2\n', mkdir=True)
            tdir2 = f'{tdir2a}/tglpkg'       # staging area
            mkdirs(tdir2)

            # case1: basic retest pass case ======================
            # setup first
            File(f'{tdir}/completed/111_B.json').touch(text.replace('_E_', '1'), mkdir=True)
            File(f'{tdir}/completed/112_B.json').touch(text.replace('_E_', '0'), mkdir=True)
            t_tarpath = f'{tdir3}/111.tar.wip.gz'
            File(t_tarpath).touch()

            obj.metafnames = {'111_B': 'BOM1'}
            obj.meta2tar = {'111_B': (tdir2, t_tarpath)}
            obj.meta2meta = {'111_B': data}     # no tester here since this is not yet complete

            # run it
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir empty before tpbot
            obj.tpbot_wait()
            self.assertEqual(called, [])     # [{'PASSED_Si'}])
            self.assertEqual(os.listdir(tdir2), ['7000_112_B.tar.gz'])        # staging dir
            self.assertEqual(os.listdir(tdir3), ['7000_112_B.tar.gz'])        # tempobj dir

            # check new metadata, that it has negative tester
            expect = '''
{
    "site": "JF",
    "logfile": "/blah/11-17-28/1_1_B.txt",
    "INIT log": "/blah/11-17-28/loadlog_11_17.txt",
    "tprolling": "/tprol",
    "tester": "!tester1"
}
'''
            self.assertTextEqual(File(f'{obj.root}/staging/_metadata/112_B.json').read(), expect)

            # case2: 2nd run is failing =======================
            # setup first
            File(f'{tdir}/completed/112_B.json').touch(text.replace('_E_', '1'), mkdir=True, newfile=True)
            File(f'{tdir2}/7000_112_B.tar.gz').unlink()
            File(f'{tdir3}/7000_112_B.tar.gz').unlink()
            File(t_tarpath).touch()
            called = []

            obj = RunnerBotOS()
            obj.root = tdir
            File(t_tarpath).touch()
            obj.metafnames = {'111_B': 'BOM1'}
            obj.meta2tar = {'111_B': (tdir2, t_tarpath)}
            obj.meta2meta = {'111_B': data}

            # runit
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir empty before tpbot
            with self.assertRaises(SystemExit):
                obj.tpbot_wait()
            self.assertEqual(os.listdir(tdir2), ['7000_112_B.tar.gz'])        # staging dir
            self.assertEqual(os.listdir(tdir3), ['7000_112_B.tar.gz'])        # tempobj dir
            self.assertEqual(called, [{'FAILED_BOM1'}])

            # case3: no completed on 2nd run - timeout ===================
            # setup first
            File(f'{tdir}/completed/112_B.json').unlink()
            File(f'{tdir2}/7000_112_B.tar.gz').unlink()
            File(f'{tdir3}/7000_112_B.tar.gz').unlink()
            File(t_tarpath).touch()
            called = []

            obj = RunnerBotOS()
            obj.root = tdir
            File(t_tarpath).touch()
            obj.metafnames = {'111_B': 'BOM1'}
            obj.meta2tar = {'111_B': (tdir2, t_tarpath)}
            obj.meta2meta = {'111_B': data}

            # runit
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir empty before tpbot
            with self.assertRaisesRegex(ErrorUser, 'Timeout occurred'):
                obj.tpbot_wait()
            self.assertEqual(os.listdir(tdir2), ['7000_112_B.tar.gz'])      # staging dir
            self.assertEqual(os.listdir(tdir3), ['7000_112_B.tar.gz'])       # tempobj dir
            self.assertEqual(called, [{'FAILED'}])

            # case4: 1st run is pass, no retest ===================
            # setup first
            File(f'{tdir}/tpbot_count/tglpkg').touch('1\n', mkdir=True, newfile=True)
            File(f'{tdir}/completed/111_B.json').touch(text.replace('_E_', '0'), mkdir=True, newfile=True)
            File(f'{tdir2}/7000_112_B.tar.gz').unlink()
            File(f'{tdir3}/7000_112_B.tar.gz').unlink()
            File(t_tarpath).touch()
            called = []

            obj = RunnerBotOS()
            obj.root = tdir
            File(t_tarpath).touch()
            obj.metafnames = {'111_B': 'BOM1'}
            obj.meta2tar = {'111_B': (tdir2, t_tarpath)}
            obj.meta2meta = {'111_B': data}

            # runit
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir empty before tpbot
            obj.tpbot_wait()
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir
            self.assertEqual(os.listdir(tdir3), ['111.tar.wip.gz'])          # tempobj dir
            self.assertEqual(called, [])    # [{'PASSED_Si'}])

            # case5: missing tpbot cnt file ==========================
            # setup first
            File(f'{tdir}/tpbot_count/tglpkg').unlink()
            File(f'{tdir}/completed/111_B.json').touch(text.replace('_E_', '1'), mkdir=True, newfile=True)
            File(f'{tdir2}/7000_112_B.tar.gz').unlink()
            File(f'{tdir3}/7000_112_B.tar.gz').unlink()
            File(t_tarpath).touch()
            called = []

            obj = RunnerBotOS()
            obj.root = tdir
            File(t_tarpath).touch()
            obj.metafnames = {'111_B': 'BOM1'}
            obj.meta2tar = {'111_B': (tdir2, t_tarpath)}
            obj.meta2meta = {'111_B': data}

            # runit
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir empty before tpbot
            with self.assertRaises(SystemExit):
                obj.tpbot_wait()
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir
            self.assertEqual(os.listdir(tdir3), ['111.tar.wip.gz'])          # tempobj dir
            self.assertEqual(called, [{'FAILED_BOM1'}])

            # case6: not enough tpbot testers ========================
            # setup first
            File(f'{tdir}/tpbot_count/tglpkg').touch('1\n', mkdir=True, newfile=True)
            File(f'{tdir}/completed/111_B.json').touch(text.replace('_E_', '1'), mkdir=True, newfile=True)
            File(f'{tdir2}/7000_112_B.tar.gz').unlink()
            File(f'{tdir3}/7000_112_B.tar.gz').unlink()
            File(t_tarpath).touch()
            called = []

            obj = RunnerBotOS()
            obj.root = tdir
            File(t_tarpath).touch()
            obj.metafnames = {'111_B': 'BOM1'}
            obj.meta2tar = {'111_B': (tdir2, t_tarpath)}
            obj.meta2meta = {'111_B': data}

            # runit
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir empty before tpbot
            with self.assertRaises(SystemExit):
                obj.tpbot_wait()
            self.assertEqual(os.listdir(tdir2), [])                          # staging dir
            self.assertEqual(os.listdir(tdir3), ['111.tar.wip.gz'])          # tempobj dir
            self.assertEqual(called, [{'FAILED_BOM1'}])

    def test_tpbot_wait(self):
        # multiple metafnames
        called = []
        RunnerBotOS.SLEEP_SEC = 0.001
        RunnerBotOS.MAX_WAIT_SECS = 0.01

        def fakelabel(input):
            called.append(input)

        print('\n================= case pass\n')
        pr_view = 'number: 3\nauthor: jdr\n'
        with TempDir(name=True) as tdir, \
                MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']), \
                MockVar(GitHub, 'add_labels', fakelabel), \
                MockVar(GitHub, 'pr_view_output', pr_view):
            obj = RunnerBotOS()
            obj.root = tdir

            text = '''{
"site": "JF",
"logfile": "/blah/11-17-28/1_1_B.txt",
"INIT log": "/blah/11-17-28/loadlog_11_17.txt",
"tprolling": "/tprol",
"code": _E_
}'''
            File(f'{tdir}/completed/111.json').touch(text.replace('_E_', '0'), mkdir=True)
            File(f'{tdir}/completed/112.json').touch(text.replace('_E_', '0'), mkdir=True)
            obj.metafnames = {'111': 'BOM1', '112': 'BOM2'}
            obj.tpbot_wait()
            self.assertEqual(called, [])    # [{'PASSED_Si'}])

        # one of them failed
        called = []
        print('\n================= case one fail\n')
        with TempDir(name=True) as tdir, \
                MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']), \
                MockVar(GitHub, 'add_labels', fakelabel), \
                MockVar(GitHub, 'pr_view_output', pr_view):
            obj = RunnerBotOS()
            obj.root = tdir
            File(f'{tdir}/completed/111.json').touch(text.replace('_E_', '0'), mkdir=True)
            File(f'{tdir}/completed/112.json').touch(text.replace('_E_', '1'), mkdir=True)
            obj.metafnames = {'111': 'BOM1', '112': 'BOM2'}
            with self.assertRaises(SystemExit):
                obj.tpbot_wait()
            self.assertEqual(called, [{'FAILED_BOM2'}])

        # one of them is missing
        called = []
        print('\n================= case timeout\n')
        with TempDir(name=True) as tdir, \
                MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']), \
                MockVar(GitHub, 'add_labels', fakelabel), \
                MockVar(GitHub, 'pr_view_output', pr_view):
            obj = RunnerBotOS()
            obj.root = tdir
            File(f'{tdir}/completed/111.json').touch(text.replace('_E_', '0'), mkdir=True)
            obj.metafnames = {'111': 'BOM1', '112': 'BOM2'}
            with self.assertRaisesRegex(ErrorUser, 'Timeout occurred'):
                obj.tpbot_wait()
            self.assertEqual(called, [{'FAILED'}])

        # non-tpbot run
        print('\n================= case pass non-tpbot\n')
        called = []
        pr_view = 'number: 3\nauthor: jdr\n'
        with TempDir(name=True) as tdir, \
                MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']), \
                MockVar(GitHub, 'add_labels', fakelabel), \
                MockVar(GitHub, 'pr_view_output', pr_view):
            obj = RunnerBotOS()
            obj.root = tdir

            text = '''{
"site": "JF",
"logfile": "/blah/11-17-28/1_1_B.txt",
"INIT log": "/blah/11-17-28/loadlog_11_17.txt",
"tprolling": "/tprol",
"code": _E_
}'''
            File(f'{tdir}/completed/111.json').touch(text.replace('_E_', '0'), mkdir=True)
            File(f'{tdir}/completed/112.json').touch(text.replace('_E_', '0'), mkdir=True)
            obj.metafnames = {}
            obj.tpbot_wait()
            self.assertEqual(called, [])

    def test_misc(self):
        # test get_timestamp_msec()
        # test http_link()
        with MockVar(time, "time", Mock(return_value=1731882339.7173405)):
            self.assertEqual(RunnerBotOS.get_timestamp_msec(), 1731882339717)

        # test I_AM_TPI_Skip_Bot
        with MockVar(GitHub, 'get_labels', Mock(return_value={'I_AM_TPI_Skip_Bot'})):
            with MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']):
                self.assertEqual(RunnerBotOS().main(), 1)

        # get_metabom
        with MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']):
            obj = RunnerBotOS()
        obj.metafnames = {'1758943008732_B': 'nvl2_tpbot.nvlhx28c.Class_NVL_HX28C'}

        self.assertEqual(obj.get_metabom('blah'), 'NoBOM')
        self.assertEqual(obj.get_metabom('1758943008732_B'), 'Class_NVL_HX28C')
        self.assertEqual(obj.get_metabom('1758943008732_B.json'), 'Class_NVL_HX28C')
        self.assertEqual(obj.get_metabom('1758943008732_B', short=True), 'HX28C')

        # Test non-NVL products (should return first letter + last part)
        obj.metafnames = {'1758943008733_B': 'nvl2_tpbot.dnls28c.Class_DNL_S28C'}
        self.assertEqual(obj.get_metabom('1758943008733_B', short=True), 'DS28C')  # DNL case: D + S28C

        # Test edge cases
        obj.metafnames = {'1758943008735_B': 'nvl2_tpbot.simple.Simple_Product'}
        self.assertEqual(obj.get_metabom('1758943008735_B', short=True), 'Product')  # Non-NVL with only 2 parts

    # def test_nvl_get_job_type(self):
    #     with TempDir(name=True) as tdir:
    #         with TempDir(chdir=True, name=True) as tdir_src:
    #             File(f'{tdir_src}/a.tpl').touch()
    #             RunnerBotOS.get_job_type('nvl_simtpbot.nvls28c.nvl_cpu', tdir)
    #             self.assertEqual(os.listdir(tdir), ['a.tpl'])    # This src folder is copied

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    @with_(MockVar, NVLBuildTP, 'create_dielet_sha', Mock())
    @with_(MockVar, NVLBuildTP, 'update_shared_sha_latest', Mock())
    @with_(MockVar, CheckerLog, 'get_folder_sha', Mock(return_value='utonly'))
    @with_(MockVar, os.environ, 'SKIPBUILD', 'True')
    def test_nvl2_build(self):
        # basic via dielet TP
        def mock_nvl_main(slf):
            # Mock NVLBuildTP.main to create some files in outdir
            if slf.outdir:
                from gadget.disk import mkdirs
                mkdirs(slf.outdir)
                for i in range(6):
                    File(f'{slf.outdir}/file{i}.txt').touch()

        with TempDir(name=True) as tdir, \
                MockVar(MSBuild, 'main', Mock()), \
                MockVar(NVLBuildTP, 'do_torch', Mock()), \
                MockVar(NVLBuildTP, 'main', mock_nvl_main):
            File('NVL_CPU.sln').touch()
            File('POR_TP/TGLH81/dummy.tpproj').touch(mkdir=True)
            RunnerBotOS.do_nvl2_build(tdir, 'TGLH81', 'nvl_dielet', '', '')
            self.assertGreater(len(os.listdir(tdir)), 5)

        # ASIS
        File(f'src/a').touch(mkdir=True)
        File(f'src/b').touch(mkdir=True)
        with TempDir(name=True) as tdir, \
                MockVar(os.environ, 'DEST', f'{os.getcwd()}/src'), \
                MockVar(MSBuild, 'main', Mock()):
            File('NVL_CPU.sln').touch()
            RunnerBotOS.do_nvl2_build(tdir, 'TGLH81', 'nvl_dielet', '', 'ASIS')
            self.assertEqual(len(os.listdir(tdir)), 2)

        # ASIS_LOCAL
        with TempDir(name=True) as tdir, \
                MockVar(os.environ, 'DEST', f'{os.getcwd()}/src'), \
                MockVar(MSBuild, 'main', Mock()):
            File('NVL_CPU.sln').touch()
            RunnerBotOS.do_nvl2_build(tdir, 'TGLH81', 'nvl_dielet', '', 'ASIS_LOCAL')
            self.assertEqual(len(os.listdir(tdir)), 1)

    def test_nvl2_get_job_type(self):
        with MockVar(RunnerBotOS, 'do_nvl2_build', Mock()):

            # case mbot
            result = RunnerBotOS.get_job_type('nvl2_simmbot._ALL_.nvl_dielet', None)
            self.assertEqual(result, ('E', 'sim', 'nvl_dielet'))

            # case: tpbot
            result = RunnerBotOS.get_job_type('nvl2_simtpbot._ALL_.nvl_dielet', None)
            self.assertEqual(result, ('B', 'sim', 'nvl_dielet'))

            # case: invalid
            with self.assertRaisesRegex(ErrorUser, 'Invalid nvl2 command'):
                RunnerBotOS.get_job_type('nvl2_random._ALL_.nvl_dielet', None)

            # case: teambot encoded
            result = RunnerBotOS.get_job_type('nvl2_teambot.Class_NVL_S28C.nvl_dielet.nvlhx', None)
            self.assertEqual(result, ('D', 'nvlhx', 'nvl_dielet'))

            # case: teambot auto-derive
            result = RunnerBotOS.get_job_type('nvl2_teambot.Class_NVL_S28C.nvl_dielet', None)
            self.assertEqual(result, ('D', 'nvls28c', 'nvl_dielet'))

    def test_decode_cmd(self):
        self.assertEqual(RunnerBotOS._decode_cmd('aa.bb.cc', 'TGLH1'), 'aa.TGLH1.cc')
        self.assertEqual(RunnerBotOS._decode_cmd('aa.bb.cc.dd', 'TGLH1'), 'aa.TGLH1.cc.dd')
        self.assertEqual(RunnerBotOS._decode_cmd('aa._ALL_.cc', 'TGLH1'), 'aa.TGLH1.cc')
        self.assertEqual(RunnerBotOS._decode_cmd('aa._ALL_.cc', 'nn.tgl1.TGLH1'), 'nn.TGLH1.cc.tgl1')

        # yml specified sim
        self.assertEqual(RunnerBotOS._decode_cmd('nvl2_teambot._ALL_.nvl_dielet.sim',
                                                 'nvl2_teambot1.nvls28c.Class_NVL_S28C'),
                         'nvl2_teambot1.Class_NVL_S28C.nvl_dielet.sim')

        # yml specifies no pkginfo
        self.assertEqual(RunnerBotOS._decode_cmd('nvl2_teambot._ALL_.nvl_dielet',
                                                 'nvl2_teambot1.nvls28c.Class_NVL_S28C'),
                         'nvl2_teambot1.Class_NVL_S28C.nvl_dielet.nvls28c')

        self.assertEqual(RunnerBotOS._decode_cmd('nvl2_teambot._ALL_.nvl_dielet',
                                                 'Class_NVL_S28C'),
                         'nvl2_teambot.Class_NVL_S28C.nvl_dielet')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_special_asis(self):
        # no set
        with MockVar(os.environ, 'IN1', 'blah'):
            RunnerBotOS.special_asis()
            self.assertEqual(os.environ['IN1'], 'blah')

        # NOLOAD
        with MockVar(os.environ, 'IN1', 'NOLOAD'):
            RunnerBotOS.special_asis()
            self.assertEqual(os.environ['IN1'], 'ASIS')
            self.assertEqual(os.environ['DEST'], '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/special_asis/NOLOAD')

        # folder not found
        with MockVar(os.environ, 'IN1', 'NOLOAD'), MockVar(Env, 'xpath', Mock(return_value='/blah')):
            RunnerBotOS.special_asis()
            self.assertEqual(os.environ['IN1'], 'NOLOAD')

    def test_write_bot_options(self, tdir=f'{UT_DIR_REPO}/bot_os_options'):
        # Test write bot options
        fake_bot_vars = {'BOT_BATFILE': 'None', 'BOT_CSM': 'true', 'BOT_PROCESS_STEPS': 'None', 'BOT_PUP': 'false', 'BOT_SKIPLTTC': 'false', 'BOT_TYPE': 'mbot'}
        actual_file = f'{tdir}/POR_TP/CLASS_ARL_U28/Scripts/load_and_run.json'
        gold_file = f'{tdir}/POR_TP/CLASS_ARL_U28/Scripts/load_and_run.gold.json'

        with MockVar(sys, "argv", ['runner_botos.py', 'arl_tpbot']):
            obj = RunnerBotOS()
            with MockVar(os, 'environ', fake_bot_vars):
                obj.write_bot_options(tdir)
                self.assertGoldEqual(actual_file, gold_file)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
