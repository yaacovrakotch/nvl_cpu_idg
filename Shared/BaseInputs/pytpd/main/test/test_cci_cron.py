#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for cci_cron.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from main.cci_cron import *
from unittest.mock import Mock
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.dictmore import DictDot
from gadget.disk import mkdirs
from pprint import pprint
import main.cci_cron as cci_cron


class CCITest(TestCase):

    def test_process(self):
        # processing logic
        data = {12: {'labels': {'ARR'}},
                13: {'labels': {'PASSED_Chk', 'FAILED'}},
                14: {'labels': {'FAILED_Chk'}},
                15: {'labels': {'ARR', 'AAREADY'}},
                16: {'labels': {'ARR', 'AAREADY', 'TEST_IN_PROGRESS'}},
                }
        self.assertEqual(CCICron.process(data, list(data)),
                         {'open': 5, 'wip': 1, 'ready': 1, 'fail_tester': 1})

    def test_basic(self):
        # test start to finish, but mocked up "CCI"
        with TempDir(name=True) as tdir:
            cron = CCICron()

            def fake_read_repos(slf):
                slf.repos = {1: {'repo': '/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68',
                                 'logfile': f'{tdir}/a.log',
                                 'basebranch': 'TP/37'}}

            def fake_init(slf):
                slf.data = {12: {'openclose': 'open',
                                 'approved': 'Approved',
                                 'update_age': 10,
                                 'labels': {'ARR', 'READY'},
                                 }
                            }

            with MockVar(CCI, 'main_init', fake_init), MockVar(CCICron, 'read_repos', fake_read_repos):
                cron.main(1, 0.1)
                result = File(cron.repos[1]['logfile']).read()
                self.assertIn('open=1 wip=0 ready=1 fail_tester=0', result)
                self.assertEqual(len(result.split('\n')), 2)

            # run again - append
            with MockVar(CCI, 'main_init', fake_init), \
                    MockVar(CCICron, 'read_repos', fake_read_repos), \
                    MockVar(sys, 'argv', ['a.py', '-once']):
                cron.main()
                result = File(cron.repos[1]['logfile']).read()
                self.assertEqual(len(result.split('\n')), 3)

    def test_repo_read(self):
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(CCICron, 'ROOT', tdir):

            # case1 - success
            File('a.json').touch('''
{"repo": "/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68",
"logfile": "/intel/engtools/tptools/mtl/logs/cci_metric/39.log",
"basebranch": 0}
''', newfile=True)
            cron = CCICron()
            expect = {'a.json': {'basebranch': 0,
                                 'logfile': '/intel/engtools/tptools/mtl/logs/cci_metric/39.log',
                                 'repo': '/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68'}}
            self.assertEqual(cron.repos, expect)

            # case2 - fail
            File('a.json').touch('''
{"repo": "/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68",
"logfile": "/intel/engtools/tptools/mtl/logs/cci_metric/39.log",
"basebranch": 'TP/39'}
''', newfile=True)
            cron = CCICron()
            self.assertEqual(cron.repos, {})

            # case3 - invalid key
            File('a.json').touch('''
{"repo": "/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68",
"logfile": "/intel/engtools/tptools/mtl/logs/cci_metric/39.log",
"blah": "blah",
"basebranch": 0}
''', newfile=True)
            cron = CCICron()
            expect["a.json"]["blah"] = "blah"
            self.assertEqual(cron.repos, expect)


class AutoReadyTest(TestCase):

    def good_rec(self, key, value):
        """Return one good record"""
        rec = {'openclose': 'open',
               'approved': 'Approved',
               'update_age': 2000,
               'labels': {'ARR', 'PASSED_Chk'},
               'title': 'some title'
               }
        rec[key] = value
        return rec

    def test_basic(self):

        def fake_init(slf):
            rec = self.good_rec
            slf.data = {10: rec('openclose', 'open'),
                        11: rec('openclose', 'merged'),       # merged pr
                        12: rec('update_age', 10),            # recent
                        13: rec('approved', 'need_review'),   # not approved
                        14: rec('labels', {'ARR'}),           # no pass chk
                        15: rec('labels', {'ARR', 'PASSED_Chk', 'AAREADY'}),       # with ready label
                        16: rec('labels', {'ARR', 'PASSED_Chk', 'BUNDLE'}),        # bundle case
                        17: rec('labels', {'ARR', 'PASSED_Chk', 'FAILED_Si'}),     # fail case
                        18: rec('labels', {'ARR', 'PASSED_Chk', 'NO_AUTO_RDY'}),   # NO_AUTO_RDY
                        19: rec('labels', {'ARR', 'PASSED_Chk', 'I_AM_TPI_Skip_Bot'}),   # I_AM_TPI_Skip_Bot
                        20: rec('labels', {'ARR', 'PASSED_Chk', 'TEST_IN_PROGRESS'}),   # TEST_IN_PROGRESS
                        21: rec('labels', {'ARR', 'PASSED_Chk', 'PASSED_OFFLINE'}),    # PASSED_OFFLINE
                        }
            return slf.data

        def fake_run(slf):
            result.append(' '.join(slf.cmd))
            return 0, ''

        with MockVar(CCI, 'main_init', fake_init), \
                MockVar(SystemCall, 'run_outtxt', fake_run), \
                MockVar(GetCmd, 'exe', lambda x: x):

            # case1 - basic, without offline
            result = []
            res = AutoReady().main('/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68', 'TP/37')
            self.assertEqual(res, len(fake_init(DictDot())) - 1)
            self.assertEqual(result, [f'{AutoReady.ghexe} pr edit 10 --add-label READY',
                                      f'{AutoReady.ghexe} pr edit 21 --add-label READY'])

            # case2 - autoready disabled
            result = []
            res = AutoReady().main('/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68', 'TP/37', autoready=0)
            self.assertEqual(res, len(fake_init(DictDot())) - 1)
            self.assertEqual(result, [])

            # case3 - offline enabled
            result = []
            res = AutoReady().main('/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68', 'TP/37', offline=1)
            self.assertEqual(res, len(fake_init(DictDot())) - 1)
            self.assertEqual(result, [f'{AutoReady.ghexe} pr edit 21 --add-label READY'])

    def test_basic_nvl(self):

        def fake_init(slf):
            rec = self.good_rec
            slf.data = {30: rec('labels', {'ARR', 'BOMCNT1', 'PASSED_BOM1', 'AAREADY'}),       # with ready label already
                        31: rec('labels', {'ARR', 'BOMCNT1', 'PASSED_BOM1'}),                  # this is ready
                        32: rec('labels', {'ARR', 'BOMCNT2', 'PASSED_BOM1'}),                  # missing one PASS
                        33: rec('labels', {'ARR', 'BOMCNT2', 'PASSED_BOM1', 'PASSED_BOM2'}),   # this is ready
                        }
            return slf.data

        def fake_run(slf):
            result.append(' '.join(slf.cmd))
            return 0, ''

        with MockVar(CCI, 'main_init', fake_init), \
                MockVar(SystemCall, 'run_outtxt', fake_run), \
                MockVar(GetCmd, 'exe', lambda x: x):

            # case1 - basic
            result = []
            res = AutoReady().main('/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68', 'TP/37')
            self.assertEqual(res, len(fake_init(DictDot())))
            self.assertEqual([f'{AutoReady.ghexe} pr edit 31 --add-label READY',
                              f'{AutoReady.ghexe} pr edit 33 --add-label READY'], result)

    def test_basic_bundle(self):

        def fake_init(slf):
            rec = self.good_rec
            slf.data = {14: rec('na', 'na'),
                        11: rec('title', 'bundle of 2: 12 13'),
                        12: rec('na', 'na'),
                        13: rec('na', 'na'),
                        }
            return slf.data

        def fake_run(slf):
            result.append(' '.join(slf.cmd))
            return 0, ''

        result = []
        with MockVar(CCI, 'main_init', fake_init), \
                MockVar(SystemCall, 'run_outtxt', fake_run), \
                MockVar(GetCmd, 'exe', lambda x: x):
            res = AutoReady().main('/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68', 'TP/37')
            self.assertEqual(res, len(fake_init(DictDot())))
        self.assertEqual(result, [f'{AutoReady.ghexe} pr edit 14 --add-label READY'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
