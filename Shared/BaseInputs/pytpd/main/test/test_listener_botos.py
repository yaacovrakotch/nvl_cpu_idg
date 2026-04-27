#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for listener_botos
"""
from datetime import time
import json
import subprocess
from setenv_unittest import UT_DIR, ROOT_ENV, UT_DIR_REPO, EXIST_PDX_I_DRIVE   # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdoutLog
from main.listener_botos import *
import main.listener_botos as listener_botos
from os.path import join, dirname, abspath
import os


class TestListen(TestCase):

    def test_basic(self):
        # There is one job
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2,\
                MockVar(TvpvEnv, 'get_site', Mock(return_value=tdir2)),\
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            BotOS.root = tdir2

            # setup the job
            File(f'{UT_DIR_REPO}/misc_files/job_dummy_D.tar.gz').copy(tdir)
            File(f'{tdir}/occupied.status').touch()   # set a status, it does not matter what it is
            File(f'{tdir}/nvls.package.info').touch()

            obj = ListenerBotOS()
            obj.root = tdir
            with CaptureStdoutLog() as p,\
                    MockVar(sys, 'argv', [sys.argv[0], 'botstart']), \
                    MockVar(obj, 'check_running_process', Mock(return_value=False)):
                obj.main(maxloop=1, sleeptime=0)

            # check load_and_run.py is executed
            self.assertIn('I am running the tester', p.getvalue())
            # check contents of root folder during run
            self.assertEqual(obj._ut, [{'nvls.package.info', 'job_dummy_D.tar.gz', 'running.status'},
                                       f'{obj.tdir}/0'])
            # check final contents of root folder, make sure .tar.gz is deleted
            self.assertEqual(set(os.listdir(tdir)), {'nvls.package.info',
                                                     'idle.status',
                                                     'dummy_D.result.json'})

            # fail case it is already running
            with MockVar(obj, 'check_running_process', Mock(return_value=True)), \
                    MockVar(sys, 'argv', [sys.argv[0], 'botstart']):
                with self.assertRaisesRegex(ErrorInput, 'Listener is already running'):
                    obj.main()

            # exception case
            def fake_error():
                raise ErrorInput('something went wrong', 'yeah')

            with CaptureStdoutLog() as p,\
                    MockVar(sys, 'argv', [sys.argv[0], 'botstart']), \
                    MockVar(obj, 'main_one_run', fake_error), \
                    MockVar(obj, 'check_running_process', Mock(return_value=False)):
                obj.main(maxloop=1, sleeptime=0)

            self.assertIn('something went wrong', p.getvalue())

    def test_multi_folder(self):
        with TempDir(name=True, chdir=True) as tdir,\
                MockVar(BotOS, 'root', tdir):
            # setup the job
            File(f'{UT_DIR_REPO}/misc_files/job_dummy1_B.tar.gz').copy(tdir)
            File(f'{tdir}/occupied.status').touch()   # set a status, it does not matter what it is
            File(f'{tdir}/nvls.package.info').touch()

            obj = ListenerBotOS()
            obj.root = tdir
            with CaptureStdoutLog() as p,\
                    MockVar(sys, 'argv', [sys.argv[0], 'botstart']), \
                    MockVar(obj, 'check_running_process', Mock(return_value=False)):
                obj.main(maxloop=1, sleeptime=0)

            # check load_and_run.py is executed
            self.assertIn('Expecting one folder', p.getvalue())

    # def test_with_options(self):
    #     # There is one job
    #     with TempDir(name=True, chdir=True) as tdir:
    #         # setup the job
    #         File(f'{UT_DIR}/misc_files/job_dummy2_B.tar.gz').copy(tdir)
    #         File(f'{tdir}/occupied.status').touch()   # set a status, it does not matter what it is
    #         File(f'{tdir}/nvls.package.info').touch()
    #
    #         obj = ListenerBotOS()
    #         obj.root = tdir
    #         with CaptureStdoutLog() as p,\
    #                 MockVar(sys, 'argv', [sys.argv[0], 'botstart']), \
    #                 MockVar(obj, 'check_running_process', Mock(return_value=False)):
    #             obj.main(maxloop=1, sleeptime=0)
    #
    #         # check load_and_run.py is executed
    #         self.assertIn('POR_TP/blah/Scripts/load_and_run.py opt1 opt2', p.getvalue())

    def test_missing_loadrun(self):
        # There is one job
        with TempDir(name=True, chdir=True) as tdir, MockVar(BotOS, 'root', tdir):
            # setup the job
            File(f'{UT_DIR_REPO}/misc_files/job_dummy_C.tar.gz').copy(tdir)
            File(f'{tdir}/occupied.status').touch()   # set a status, it does not matter what it is
            File(f'{tdir}/nvls.package.info').touch()

            obj = ListenerBotOS()
            obj.root = tdir
            with CaptureStdoutLog() as p,\
                    MockVar(sys, 'argv', [sys.argv[0], 'botstart']), \
                    MockVar(obj, 'check_running_process', Mock(return_value=False)):
                obj.main(maxloop=1, sleeptime=0)

            # check load_and_run.py is executed
            self.assertIn('Expecting Shared/' + os.path.normpath('POR_TP/blah/Scripts') + '/load_and_run.py', p.getvalue())

    def test_printwait(self):
        # test the print wait, that it will only print once
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2,\
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            BotOS.root = tdir2

            # setup the job
            File(f'{tdir}/occupied.status').touch()   # set a status, it does not matter what it is
            File(f'{tdir}/nvls.package.info').touch()

            obj = ListenerBotOS()
            obj.root = tdir
            with CaptureStdoutLog() as p,\
                    MockVar(sys, 'argv', [sys.argv[0], 'botstart']), \
                    MockVar(obj, "main_one_run", Mock()), \
                    MockVar(obj, 'check_running_process', Mock(return_value=False)):
                obj.main(maxloop=3, sleeptime=0)

            self.assertTrue(p.getvalue().strip().endswith('Waiting and Listening...'))

    def test_tdir(self):
        # tests tdir folder handling
        # good template to copy from
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2,\
                MockVar(BotOS, 'root', tdir2),\
                MockVar(TvpvEnv, 'get_site', Mock(return_value=tdir2)),\
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            File(f'{tdir}/nvls.package.info').touch()    # This file is required
            File(f'{UT_DIR_REPO}/misc_files/job_dummy_A.tar.gz').copy(tdir)

            obj = ListenerBotOS()
            obj.root = tdir    # tester root
            obj.tdir = tdir2   # tp folder

            # execute
            obj.main_one_run()
            self.assertEqual(obj._ut[-1], f'{tdir2}/0')    # default

            # run: no tar file
            obj._ut = []
            obj.main_one_run()
            self.assertEqual(obj._ut, [])

            # run with tar file
            File(f'{UT_DIR_REPO}/misc_files/job_dummy_A.tar.gz').copy(tdir)
            obj.main_one_run()
            self.assertEqual(obj._ut[-1], f'{tdir2}/0')    # should be zero still

            # now something go wrong in rmtree
            File(f'{UT_DIR_REPO}/misc_files/job_dummy_A.tar.gz').copy(tdir)
            with MockVar(shutil, 'rmtree', Mock(side_effect=Exception)):
                obj.main_one_run()
            self.assertEqual(obj._ut[-1], f'{tdir2}/1')    # increment
            self.assertEqual(os.listdir(f'{tdir2}/1'), ['POR_TP'])

    def test_loadrunjson(self):
        # team file writing
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                MockVar(BotOS, 'root', tdir2), \
                MockVar(TvpvEnv, 'get_site', Mock(return_value=tdir2)), \
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            File(f'{tdir}/nvls.package.info').touch()    # This file is required
            File(f'{UT_DIR_REPO}/misc_files/job_dummyjson_D.tar.gz').copy(tdir)

            obj = ListenerBotOS()
            obj.root = tdir    # tester root
            obj.tdir = tdir2   # tp folder

            def fake_inspect(*args, **kwargs):
                expect = {'nvls.package.info', 'job_dummyjson_D.tar.gz', 'running.status', 'TPD.team'}
                self.assertEqual(set(os.listdir(obj.root)), expect)

            # execute
            with MockVar(obj, 'write_result', fake_inspect):
                obj.main_one_run()

            # after run check
            self.assertEqual(set(os.listdir(obj.root)), {'idle.status',
                                                         'nvls.package.info'})
            self.assertEqual(obj.tp_options, {'TEAM': 'TPD'})

    def test_get_tpcwd(self):
        # test mbot
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            mkdirs(f'{tdir}/mbot_rolling')
            obj = ListenerBotOS()

            # normal case
            self.assertEqual(obj.get_tpcwd('8000_1748119774796_E.tar.gz'), f'{tdir}/mbot_rolling/1748119774796_E.0')

            # error case
            mkdirs(f'{tdir}/mbot_rolling/1748119774796_E.0')
            with self.assertRaisesRegex(ErrorCockpit, 'Max iteration exceeded'):
                obj.get_tpcwd('8000_1748119774796_E.tar.gz', _maxiter=1)

        # test tpbot, pass case
        with TempDir(name=True, chdir=True) as tdir:
            obj.tdir = tdir
            self.assertEqual(obj.get_tpcwd('8000_1748119774796_B.tar.gz'), f'{tdir}/0')

    def test_write_result(self):
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                MockVar(TvpvEnv, 'get_site', Mock(return_value=tdir2)):
            BotOS.root = tdir2
            obj = ListenerBotOS()
            obj.logdir = f'{tdir2}/LOGDIR'
            obj.root = tdir       # tester root dir
            File('1_1_B.tar').touch()
            File(f'{tdir2}/logfile/CurrentStatus.txt').touch(mkdir=True)
            File(f'{tdir2}/logfile/CurrentStatus1.txt').touch(mkdir=True)
            File(f'{tdir2}/logfile/ituff_HOT_testunit.txt').touch(mkdir=True)
            File(f'{tdir2}/logfile/ituff_HOT_1_testunit.txt').touch(mkdir=True)
            File(f'{tdir2}/logfile/ituff_HOT_2_testunit.txt').touch(mkdir=True)

            # Case1 - with HardBin and ituff lines
            text = f'''
Stop CLASSHOT Testing Log...
Test Unit log: {tdir2}/logfile/CurrentStatus.txt
Copy ituff file...
Ituff file: {tdir2}/logfile/CurrentStatus1.txt
Test Unit is successful.
DUT: 11] DUT 11: EndTest completed with SUCCESS  SoftBin = 100, HardBin = 1001
'''
            obj.write_result('1_1_B.tar', 0, text)
            deyt = curtime(dateonly=True)
            expect = f'''
{{
    "Ituff file": "{tdir2}/logfile/CurrentStatus1.txt",
    "Test Unit log": "{tdir2}/logfile/CurrentStatus.txt",
    "code": 0,
    "tprolling": "{tdir2}/tp_rolling_botos/1_B",
    "logfile": "{tdir2}/LOGDIR/{deyt}/1_1_B_{HOSTNAME}.txt",
    "site": "{TvpvEnv.get_site()}",
    "command": "done",
    "comment": "DUT: 11] DUT 11: EndTest completed with SUCCESS  SoftBin = 100, HardBin = 1001",
    "tracelot": ""
}}
'''
            self.assertTextEqual(File('1_B.result.json').read(), expect.replace("\\", "\\\\"))
            # check tp_rolling_botos
            self.assertEqual(set(os.listdir(f'{tdir2}/tp_rolling_botos/1_B')),
                             {'1_1_B.tar', 'CurrentStatus1.txt.gz', f'log.{HOSTNAME}.txt.gz', 'CurrentStatus.txt.gz'})

            # case2 - problem
            File('1_1_C.tar').touch()
            obj.write_result('1_1_C.tar', 1, 'Problem with load_and_run.py')
            expect = f'''
{{
    "code": 1,
    "tprolling": "{tdir2}/tp_rolling_botos/1_C",
    "logfile": "{tdir2}/LOGDIR/{deyt}/1_1_C_{HOSTNAME}.txt",
    "site": "{TvpvEnv.get_site()}",
    "command": "done",
    "comment": "No HardBin found. See logs. Lastline: [Problem with load_and_run.py]",
    "tracelot": ""
}}
'''
            self.assertTextEqual(File('1_C.result.json').read(), expect.replace("\\", "\\\\"))

            # Case3 - retest log files
            File('1_1_E.tar').touch()

            text = f'''
Stop CLASSHOT Testing Log...
Test Unit log: {tdir2}/logfile/ituff_HOT_testunit.txt
Test Unit log: {tdir2}/logfile/ituff_HOT_1_testunit.txt
Test Unit log: {tdir2}/logfile/ituff_HOT_2_testunit.txt
Copy ituff file...
Ituff file: {tdir2}/logfile/ituff_HOT_testunit.txt
Ituff file: {tdir2}/logfile/ituff_HOT_1_testunit.txt
Ituff file: {tdir2}/logfile/ituff_HOT_2_testunit.txt
Test Unit is successful.
'''

            called = []

            def fake_traceIT(arg):
                called.append(arg)
                return ['lot1', 'lot2']

            with MockVar(listener_botos, 'traceIT', fake_traceIT):
                obj.write_result('1_1_E.tar', 0, text)
            deyt = curtime(dateonly=True)
            expect = f'''
{{
    "Ituff file": "{tdir2}/logfile/ituff_HOT_testunit.txt",
    "Ituff file 1": "{tdir2}/logfile/ituff_HOT_1_testunit.txt",
    "Ituff file 2": "{tdir2}/logfile/ituff_HOT_2_testunit.txt",
    "Test Unit log": "{tdir2}/logfile/ituff_HOT_testunit.txt",
    "Test Unit log 1": "{tdir2}/logfile/ituff_HOT_1_testunit.txt",
    "Test Unit log 2": "{tdir2}/logfile/ituff_HOT_2_testunit.txt",
    "code": 0,
    "tprolling": "{tdir2}/tp_rolling_botos/1_E",
    "logfile": "{tdir2}/LOGDIR/{deyt}/1_1_E_{HOSTNAME}.txt",
    "site": "{TvpvEnv.get_site()}",
    "command": "done",
    "comment": "No HardBin found. See logs. Lastline: [Test Unit is successful.]",
    "tracelot": "lot1,lot2"
}}
'''
            self.assertTextEqual(File('1_E.result.json').read(), expect.replace("\\", "\\\\"))
            self.assertEqual(len(called), 3)    # 3 ituff files

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_check_running_process(self):
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                MockVar(BotOS, 'root', tdir2):
            obj = ListenerBotOS()
            obj.root = tdir

            # case: unix
            self.assertEqual(obj.check_running_process(check_only=False), 1)

            # case: pass case
            outtxt = f'''
PYTHON3.exe                   {os.getpid()} Console                    1     21,692 K
RSIGuard.exe                 30904 Console                    1     25,952 K
msedgewebview2.exe           35092 Console                    1     21,020 K
'''
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, outtxt))):
                self.assertEqual(obj.check_running_process(check_only=True, is_unix=False), False)
                self.assertEqual(os.listdir(obj.root), [])      # no process id yet
                self.assertEqual(obj.check_running_process(check_only=False, is_unix=False), False)
                self.assertEqual(os.listdir(obj.root), [f'{os.getpid()}.process'])  # expect one file

            # case: fail case - already running
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, outtxt))):
                self.assertEqual(obj.check_running_process(check_only=False, is_unix=False), True)
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, outtxt))):
                self.assertEqual(obj.check_running_process(check_only=True, is_unix=False), True)

            # case: Another processid in folder, it should delete it
            File(f'{os.getpid()}.process').unlink()
            File(f'{obj.root}/0000.process').touch()   # this is a processid that is not running
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, outtxt))):
                self.assertEqual(obj.check_running_process(check_only=False, is_unix=False), False)
                self.assertEqual(os.listdir(obj.root), [f'{os.getpid()}.process'])  # expect one file

    def test_update_expiry(self):
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2, \
                MockVar(BotOS, 'root', tdir2), \
                MockVar(time, 'time', Mock(return_value=100)):
            obj = ListenerBotOS()
            obj.root = tdir
            obj.update_expiry(5)
            self.assertEqual(os.listdir('.'), ['expiry.105.txt'])
            obj.update_expiry(6)
            self.assertEqual(os.listdir('.'), ['expiry.106.txt'])
            obj.update_expiry(2, is_start=False)    # renew
            self.assertEqual(os.listdir('.'), ['expiry.108.txt'])

    def test_teambot_wait(self):
        # unittest definitions
        utargs = dict(timeout_first=0.001, timeout_second=0.01, sleeptime=0.0001, renewtime=0.02, forever=0.1)
        SUCCESS = -3

        with TempDir(name=True, chdir=True) as tdir,\
                MockVar(BotOS, 'root', tdir):
            obj = ListenerBotOS()
            obj.root = tdir
            fname = f'{tdir}/8000_1751137825719_D.tar.gz'

            # case1 - not a teambot job
            self.assertEqual(obj.teambot_wait(f'{tdir}/8000_1751137825719_B.tar.gz', **utargs), -1)

            # case2a - teambot job, but no teambot_wait.txt - backwards compatibility
            self.assertEqual(obj.teambot_wait(fname, **utargs), -5)

            # case2b - No begin file - first timeout
            File('teambot_wait.txt').touch()
            self.assertEqual(obj.teambot_wait(fname, **utargs), -4)
            self.assertFalse(exists('teambot_wait.txt'))
            self.assertEqual(obj._ut, [0.001])

            # case3 - second timeout case - expired
            File('teambot_wait.txt').touch()
            File('begin').touch()
            self.assertEqual(obj.teambot_wait(fname, **utargs), -4)
            self.assertEqual(obj._ut, [0.001, 0.01])

            # case4 - renew case
            File('teambot_wait.txt').touch()
            File('begin').touch()
            File('renew').touch()
            self.assertEqual(obj.teambot_wait(fname, **utargs), -4)
            self.assertFalse(exists('renew'))
            self.assertEqual(obj._ut, [0.001, 0.01, 0.02])

            # case5 - done case
            File('teambot_wait.txt').touch()
            File('begin').touch()
            File('done').touch()
            self.assertEqual(obj.teambot_wait(fname, **utargs), SUCCESS)   # -3
            self.assertEqual(obj._ut, [0.001, 0.01])
            res = glob.glob('expiry.*.txt')
            self.assertEqual(len(res), 1)

    def test_set_status_dashboard(self):
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                MockVar(BotOS, 'root', tdir2):
            obj = ListenerBotOS()
            obj.root = tdir

            File('stop').touch()
            obj.set_status_dashboard()
            self.assertEqual(sorted(os.listdir(tdir)), ['stop', 'stopped.status'])

            File('stop').unlink()
            File('down').touch()
            obj.set_status_dashboard()
            self.assertEqual(sorted(os.listdir(tdir)), ['down', 'down.status'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_other(self):
        # tests the different options

        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                MockVar(BotOS, 'root', tdir2):
            obj = ListenerBotOS()
            obj.root = tdir

            # botstop
            with MockVar(sys, 'argv', [sys.argv[0], 'botstop']):
                self.assertEqual(obj.main(), 0)
                self.assertEqual(os.listdir(tdir), ['stop'])

            # botdown
            with MockVar(sys, 'argv', [sys.argv[0], 'botdown']):
                self.assertEqual(obj.main(), 0)
                self.assertEqual(sorted(os.listdir(tdir)), ['down', 'stop'])

            # botup
            with MockVar(sys, 'argv', [sys.argv[0], 'botup']):
                self.assertEqual(obj.main(), 0)
                self.assertEqual(os.listdir(tdir), [])

            # listener is down
            with MockVar(sys, 'argv', [sys.argv[0], 'botup']),\
                    MockVar(obj, 'check_running_process', Mock(return_value=False)):
                with self.assertRaisesRegex(ErrorInput, 'Listener is not executed yet'):
                    obj.main()

            # begin
            with MockVar(sys, 'argv', [sys.argv[0], 'begin']):
                self.assertEqual(obj.main(), 0)
                self.assertEqual(set(os.listdir(tdir)), {'begin', 'occupied.status'})

            # end - should delete begin
            with MockVar(sys, 'argv', [sys.argv[0], 'end']):
                self.assertEqual(obj.main(), 0)
                self.assertEqual(set(os.listdir(tdir)), {'occupied.status', 'done'})

            # end again
            File(f'{tdir}/done').unlink()
            with MockVar(sys, 'argv', [sys.argv[0], 'end']):
                self.assertEqual(obj.main(), 0)
                self.assertEqual(set(os.listdir(tdir)), {'occupied.status', 'done'})

            # help
            File(f'{tdir}/occupied.status').unlink()
            File(f'{tdir}/done').unlink()
            with MockVar(sys, 'argv', [sys.argv[0], 'help']):
                self.assertEqual(obj.main(), 0)
                self.assertEqual(os.listdir(tdir), [])

            # unknown command
            with MockVar(sys, 'argv', [sys.argv[0], 'unknown']):
                with self.assertRaisesRegex(ErrorUser, 'Given command is'):
                    obj.main()

    def fake_data_host(self, cmd='sendemail', arg='sending email', check=True):
        """ Fake datahost for email testing."""
        result = {'email message': True}
        return result

    def test_sendmail_failed_hardbin(self):
        # test the sendmail function for hardbin error
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2,\
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            BotOS.root = tdir2

            obj = ListenerBotOS()
            obj.root = tdir
            obj.tester = 'JF04TXBT63448A'
            obj.bom = 'Class_NVL_S28C'
            obj.hardBin_list = ['41-713', '41-764', '41-765']  # 3 hardbins the same

            with MockVar(DataHost, 'central', self.fake_data_host):
                msg = obj.send_error_email(error='HardBin Error', repo='unknown', failed_status='unknown')
            msg_gold = {'to_list': ['john.q.delos.reyes@intel.com', 'tai.pham@intel.com', 'erick.a.lang@intel.com', 'sunny.r.ty@intel.com', 'weng.keen.wong@intel.com', 'maroon.maroon@intel.com', 'hai.m.pearson@intel.com'], 'cc_list': 'mpe_ddg_pde_tp_team@intel.com', 'subject': "Tester JF04TXBT63448A encountered 3 consecutive same HardBin 41 for PRs ['713', '764', '765'] for Class_NVL_S28C.", 'message': "Tester JF04TXBT63448A encountered 3 consecutive same HardBin 41 for PRs ['713', '764', '765'] for Class_NVL_S28C.\nPlease check the testers for more details. Additionally, consider to take down the tester for maintenance.\nError: unknown\n", 'html': True}
            self.assertEqual(msg, msg_gold)

    def test_sendmail_failed_tpbot_schedule(self):
        # test the sendmail function for tpbot_schedule
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2,\
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            BotOS.root = tdir2

            obj = ListenerBotOS()
            obj.root = tdir
            obj.tester = 'JF04TXBT63448A'
            obj.bom = 'Class_NVL_S28C'
            obj.hardBin_list = ['41-713', '41-764', '42-765']

            with MockVar(DataHost, 'central', self.fake_data_host):
                msg = obj.send_error_email(error='TPBot_schedule', repo='nvl.common', failed_status='failed-hardbin_41')
            msg_gold = {'to_list': ['john.q.delos.reyes@intel.com', 'tai.pham@intel.com', 'erick.a.lang@intel.com', 'sunny.r.ty@intel.com', 'weng.keen.wong@intel.com', 'maroon.maroon@intel.com', 'hai.m.pearson@intel.com'], 'cc_list': 'mpe_ddg_pde_tp_team@intel.com', 'subject': 'Mainline Full TP is broken for Class_NVL_S28C for JF04TXBT63448A', 'message': 'TPBot schedule error encountered for Class_NVL_S28C for JF04TXBT63448A.\nRepo: nvl.common\nFailed Status: failed-hardbin_41 for Class_NVL_S28C\nPlease check the testers for more details.', 'html': True}
            self.assertEqual(msg, msg_gold)

    def test_tpbot_schedule_failed_sent_email(self):
        # test the sendmail function for tpbot_schedule
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2,\
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            BotOS.root = tdir2

            obj = ListenerBotOS()
            obj.root = tdir
            obj.tester = 'JF04TXBT63448A'
            obj.bom = 'Class_NVL_S28C'
            obj.hardBin_list = ['41-713', '41-764', '42-765']
            line = 'DataBin = 90980401, SoftBin = 9804, HardBin = 98, PassFailBin = 1, ExitPort = -340935982'
            obj.tp_options = {"GITHUB_WORKFLOW": "TPBot_schedule", "GITHUB_REPOSITORY": "intel-restricted/nvl.common"}

            with MockVar(DataHost, 'central', self.fake_data_host):
                msg = obj.workflow_failed_sent_email(line)
            msg_gold = {'to_list': ['john.q.delos.reyes@intel.com', 'tai.pham@intel.com', 'erick.a.lang@intel.com', 'sunny.r.ty@intel.com', 'weng.keen.wong@intel.com', 'maroon.maroon@intel.com', 'hai.m.pearson@intel.com'], 'cc_list': 'mpe_ddg_pde_tp_team@intel.com', 'subject': 'Mainline Full TP is broken for Class_NVL_S28C for JF04TXBT63448A', 'message': 'TPBot schedule error encountered for Class_NVL_S28C for JF04TXBT63448A.\nRepo: intel-restricted/nvl.common\nFailed Status: DataBin = 90980401, SoftBin = 9804, HardBin = 98, PassFailBin = 1, ExitPort = -340935982 for Class_NVL_S28C\nPlease check the testers for more details.', 'html': True}
            self.assertEqual(msg, msg_gold)

    def test_scheduler_init_failed_sent_email(self):
        # test the sendmail function for scheduler_init
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2,\
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            BotOS.root = tdir2

            obj = ListenerBotOS()
            obj.root = tdir
            obj.tester = 'JF04TXBT63448A'
            obj.bom = 'Class_NVL_S28C'
            obj.hardBin_list = ['41-713', '41-764', '42-765']
            line = 'SCHEDULER_INIT workflow detected. Exit 1 after INIT failure.'
            obj.tp_options = {"GITHUB_WORKFLOW": "SCHEDULER_INIT", "GITHUB_REPOSITORY": "intel-restricted/nvl.common"}
            with MockVar(DataHost, 'central', self.fake_data_host):
                msg = obj.workflow_failed_sent_email(line)
            msg_gold = {'to_list': ['john.q.delos.reyes@intel.com', 'tai.pham@intel.com', 'erick.a.lang@intel.com', 'sunny.r.ty@intel.com', 'weng.keen.wong@intel.com', 'maroon.maroon@intel.com', 'hai.m.pearson@intel.com'], 'cc_list': 'mpe_ddg_pde_tp_team@intel.com', 'subject': 'SCHEDULER_INIT failed for 6248_CLASSHOT for Class_NVL_S28C for JF04TXBT63448A', 'message': 'SCHEDULER_INIT failed for 6248_CLASSHOT for Class_NVL_S28C for JF04TXBT63448A.\nRepo: intel-restricted/nvl.common\nFailed Status: SCHEDULER_INIT workflow detected. Exit 1 after INIT failure. for Class_NVL_S28C for 6248_CLASSHOT\nPlease check the SCHEDULER_INIT in intel-restricted/nvl.common workflow for more details.', 'html': True}
            self.assertEqual(msg, msg_gold)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_asis_local(self):
        # There is one job, did not execute
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2, TempDir(name=True) as tdir3, \
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            File(f'{tdir}/nvls.package.info').touch()    # This file is required
            File(f'{UT_DIR}/asis_local/asis_local_E.tar.gz').copy(tdir)

            BotOS.root = tdir3
            mkdirs(f'{BotOS.root}/mbot_rolling')

            obj = ListenerBotOS()
            obj.root = tdir    # tester root
            obj.tdir = tdir2   # tp folder

            with CaptureStdoutLog() as p:
                obj.main_one_run()

            self.assertIn('Loading test program from path: /p/prod/tpvalidation/engtools/tptools/mtl/unittests/absdf_test_test', p.getvalue())

        # There is one job, execute
        print('====Start of CASE2')
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2, TempDir(name=True) as tdir3, \
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            File(f'{tdir}/nvls.package.info').touch()    # This file is required
            File(f'{UT_DIR}/asis_local/asis_local2_E.tar.gz').copy(tdir)
            BotOS.root = tdir3
            mkdirs(f'{BotOS.root}/mbot_rolling')

            obj = ListenerBotOS()
            obj.root = tdir    # tester root
            obj.tdir = tdir2   # tp folder

            with CaptureStdoutLog() as p:
                obj.main_one_run()

            self.assertIn('Loading test program from path: /p/prod/tpvalidation/engtools/tptools/mtl/unittests/bot_os_options', p.getvalue())

        # There is one job, execute, with load_and_run.json
        print('====Start of CASE3')
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2, TempDir(name=True) as tdir3, \
                MockVar(TPBotFail, 'TESTERLOGS', f'{tdir2}/LOGDIR'):
            File(f'{tdir}/nvls.package.info').touch()    # This file is required
            File(f'{UT_DIR}/asis_local/asis_local3_E.tar.gz').copy(tdir)

            BotOS.root = tdir3
            mkdirs(f'{BotOS.root}/mbot_rolling')

            obj = ListenerBotOS()
            obj.root = tdir    # tester root
            obj.tdir = tdir2   # tp folder

            with CaptureStdoutLog() as p:
                obj.main_one_run()

            self.assertIn('Loading test program from path: /p/prod/tpvalidation/engtools/tptools/mtl/unittests/bot_os_options', p.getvalue())

    def test_bot_error_found(self):
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            obj = ListenerBotOS()
            obj.root = tdir
            obj.bom = 'Class_NVL_S28C'
            BotOS.root = tdir2
            obj.tester = 'JF04TXBT63448A'
            obj.hardBin_list = ['41-713', '41-764', '42-765']

            # Case 1: golden_basetp does not exist
            mkdirs(f'{tdir2}/golden_check/golden_fulltp_{obj.bom}')
            with CaptureStdoutLog() as p, \
                    MockVar(obj, 'tester_execute', Mock(return_value='PASSED')):
                obj.bot_error_found()
            self.assertRegex(p.getvalue(), r'golden_basetp.* does not exist. Trigger sending email directly')

        # Case 2: submit a force ticket, but no tool available
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            obj = ListenerBotOS()
            obj.root = tdir
            obj.bom = 'Class_NVL_S28C'
            BotOS.root = tdir2
            obj.tester = 'JF04TXBT63448A'
            obj.hardBin_list = ['41-713', '41-764', '42-765']

            mkdirs(f'{tdir2}/golden_check/golden_basetp_{obj.bom}')
            mkdirs(f'{tdir2}/golden_check/golden_fulltp_{obj.bom}')
            File(f'{tdir}/golden_basetp_failed.log').touch()
            File(f'{tdir}/golden_fulltp_failed.log').touch()
            with CaptureStdoutLog() as p, \
                    MockVar(obj, 'tester_execute', Mock(return_value='PASSED')):
                obj.bot_error_found()

            self.assertRegex(p.getvalue(), r'force-ticket.exe does not exist. Skipping Force Ticket submission')

        # Case 3: submit a force ticket, tool available
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            obj = ListenerBotOS()
            obj.root = tdir
            obj.bom = 'Class_NVL_S28C'
            BotOS.root = tdir2
            obj.tester = 'JF04TXBT63448A'
            obj.hardBin_list = ['41-713', '41-764', '42-765']
            obj.force_ticket_path = f'{tdir2}/force-ticket.exe'

            mkdirs(f'{tdir2}/golden_check/golden_basetp_{obj.bom}')
            mkdirs(f'{tdir2}/golden_check/golden_fulltp_{obj.bom}')
            File(f'{tdir}/golden_basetp_failed.log').touch()
            File(f'{tdir}/golden_fulltp_failed.log').touch()
            File(f'{tdir2}/force-ticket.exe').touch()

            # Mock subprocess.run to return a CompletedProcess-like object
            mock_result = Mock()
            mock_result.stdout = 'Force ticket submitted successfully'
            mock_result.stderr = ''
            mock_result.returncode = 0

            with CaptureStdoutLog() as p, \
                    MockVar(obj, 'tester_execute', Mock(return_value='PASSED')), \
                    MockVar(listener_botos, 'run', Mock(return_value=mock_result)):
                obj.bot_error_found()
            self.assertRegex(p.getvalue(), r'Force Ticket output: Force ticket submitted successfully')

            File(f'{tdir}/golden_basetp_passed.log').touch()
            File(f'{tdir}/golden_fulltp_failed.log').touch()
            with CaptureStdoutLog() as p, \
                    MockVar(obj, 'tester_execute', Mock(return_value='PASSED')), \
                    MockVar(listener_botos, 'run', Mock(return_value=mock_result)):
                obj.bot_error_found()
            self.assertRegex(p.getvalue(), r'golden_basetp passed but golden_fulltp failed for BOM.*. Sending error email to TPI for replacing the unit.')

            File(f'{tdir}/golden_basetp_passed.log').touch()
            File(f'{tdir}/golden_fulltp_passed.log').touch()
            with CaptureStdoutLog() as p, \
                    MockVar(obj, 'tester_execute', Mock(return_value='PASSED')), \
                    MockVar(listener_botos, 'run', Mock(return_value=mock_result)):
                obj.bot_error_found()
            self.assertRegex(p.getvalue(), r'golden_basetp and golden_fulltp both passed for BOM.*. No need to send error email. This could be PR issue')

            File(f'{tdir}/golden_basetp_failed.log').touch()
            File(f'{tdir}/golden_fulltp_passed.log').touch()
            with CaptureStdoutLog() as p, \
                    MockVar(obj, 'tester_execute', Mock(return_value='PASSED')), \
                    MockVar(listener_botos, 'run', Mock(return_value=mock_result)):
                obj.bot_error_found()
            self.assertRegex(p.getvalue(), r'golden_basetp is no longer valid. Sending error email to TPI for replacing the golden_basetp')

    def test_write_result_golden(self):
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            BotOS.root = tdir2
            obj = ListenerBotOS()
            obj.root = tdir       # tester root dir
            tf1 = f'{tdir}/golden_basetp_Class_NVL_S28C'
            tf2 = f'{tdir}/golden_fulltp_Class_NVL_S28C'

            # Case 1 - golden_basetp failed
            obj.write_result_golden(tf1, 1, 'golden_basetp failed')
            self.assertTrue(os.path.exists(f'{tdir}/golden_basetp_failed.log'))

            # Case 2 - golden_fulltp failed
            obj.write_result_golden(tf2, 1, 'golden_fulltp failed')
            self.assertTrue(os.path.exists(f'{tdir}/golden_fulltp_failed.log'))

            # Case 3 - golden_basetp passed
            obj.write_result_golden(tf1, 0, 'golden_basetp passed')
            self.assertTrue(os.path.exists(f'{tdir}/golden_basetp_passed.log'))

            # Case 4 - golden_fulltp passed
            obj.write_result_golden(tf2, 0, 'golden_fulltp passed')
            self.assertTrue(os.path.exists(f'{tdir}/golden_fulltp_passed.log'))

    def test_tpbot_3strike_logic(self):
        # Case 1 test add hardbin to list. Failed bin98
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            BotOS.root = tdir2
            obj = ListenerBotOS()
            obj.root = tdir       # tester root dir
            tf = f'{tdir}/123_golfd_B'
            found = 'DataBin = 90980401, SoftBin = 9804, HardBin = 98, PassFailBin = 1, ExitPort = -340935982'
            obj.hardBin_list = ['98-1234', '98-1235']
            mkdirs(f'{tdir2}/pool/_metadata')
            File(f'{tdir2}/pool/_metadata/golfd_B.json').touch('{"job": "1345"}')

            with CaptureStdoutLog() as p:
                obj.tpbot_3strike_logic(tf, found, 1)

            self.assertIn("HardBin list: ['98-1234', '98-1235', '98-1345']", p.getvalue())
        # Case 2 test passing case common
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            BotOS.root = tdir2
            obj = ListenerBotOS()
            obj.root = tdir       # tester root dir
            obj.bom = 'Class_NVL_S28C'
            tf = f'{tdir}/123_golfd_B'
            found = 'DataBin = 01001001, SoftBin = 1001, HardBin = 1, PassFailBin = 1, ExitPort = 1'
            obj.hardBin_list = ['98-1234', '98-1235']
            mkdirs(f'{tdir2}/pool/_metadata')
            File(f'{tdir2}/pool/_metadata/golfd_B.json').touch('{"job": "1345"}')
            File(f'{tdir}/golfd_B.tar.gz').touch()
            obj.tp_options = {"GITHUB_WORKFLOW": "common_full_tpbot", "GITHUB_REPOSITORY": "intel-restricted/nvl.common"}

            # case 2.1 golden_fulltp does not exist
            with CaptureStdoutLog() as p:
                obj.tpbot_3strike_logic(tf, found, 0)
            self.assertTrue(os.path.exists(f'{tdir2}/golden_check/golden_fulltp_{obj.bom}'))

            # case 2.2 golden_fulltp exists, but less than 12 hours
            mkdirs(f'{tdir2}/golden_check/golden_fulltp_{obj.bom}', mode='02770')
            with CaptureStdoutLog() as p:
                obj.tpbot_3strike_logic(tf, found, 0)
            self.assertIn(f'Skip copying full TP common to central golden FULL TP for {obj.bom} due to golden fulltp is less than 12 hours old.', p.getvalue())

            # case 2.3 golden_fulltp wip.tar.gz exists
            File(f'{tdir2}/golden_check/golden_fulltp_{obj.bom}.wip.tar.gz').touch()
            with CaptureStdoutLog() as p, \
                    MockVar(time, 'time', Mock(return_value=10000000000)), \
                    MockVar(os.path, 'getmtime', Mock(return_value=1000)):
                obj.tpbot_3strike_logic(tf, found, 0)
            self.assertIn(f'Golden fulltp wip tar.gz already exists.', p.getvalue())

            # case 2.4 golden_fulltp exists, more than 12 hours
            os.remove(f'{tdir2}/golden_check/golden_fulltp_{obj.bom}.wip.tar.gz')
            with CaptureStdoutLog() as p, \
                    MockVar(time, 'time', Mock(return_value=10000000000)), \
                    MockVar(os.path, 'getmtime', Mock(return_value=1000)), \
                    MockVar(listener_botos, 'untar', Mock(return_value='abc')), \
                    MockVar(os, 'remove', Mock(return_value='abc')), \
                    MockVar(shutil, 'copyfile', Mock(return_value='destination_path')):
                obj.tpbot_3strike_logic(tf, found, 0)
            self.assertIn(f'Golden fulltp folder is older than 12 hours', p.getvalue())


AutoRestart._is_ut = True    # set AutoRestart to be in client mode always (aka, unittest)
AutoRestart()                # Store the mtimes so AutoRestart() will not fail


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
