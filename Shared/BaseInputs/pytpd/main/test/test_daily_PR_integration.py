#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
from main.daily_PR_integration import *
from os.path import join, dirname, abspath


class TestDailyPR(TestCase):

    def test_basic_all(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            output = '''[{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-03T19:37:16Z","number":2402,"title":"updating 3 files TPI_BASE_XXX and uservar to remove FSM","url":"https://github.com/intel-restricted/mtlp68/pull/2402"},
{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-02T23:49:29Z","number":2391,"title":"bypassing hvbigt per 3pm discussion","url":"https://github.com/intel-restricted/mtlp68/pull/2391"},
{"author":{"login":"patrick-hannon-intel"},"mergedAt":"2023-02-02T21:35:20Z","number":2387,"title":"Scn/scngt21fww5v1","url":"https://github.com/intel-restricted/mtlp68/pull/2387"}]
'''
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))):

                main_pr_integrate('13F0A', 'ALL', 'TP/13F', tdir)

                expect = '''PR number: 2402, title: updating 3 files TPI_BASE_XXX and uservar to remove FSM, MergedAt: 2023-02-03 19:37:16, Submitted by: shiv-gourshetty-intel, url: https://github.com/intel-restricted/mtlp68/pull/2402
PR number: 2391, title: bypassing hvbigt per 3pm discussion, MergedAt: 2023-02-02 23:49:29, Submitted by: shiv-gourshetty-intel, url: https://github.com/intel-restricted/mtlp68/pull/2391
PR number: 2387, title: Scn/scngt21fww5v1, MergedAt: 2023-02-02 21:35:20, Submitted by: patrick-hannon-intel, url: https://github.com/intel-restricted/mtlp68/pull/2387
'''
                self.assertTextEqual(File('13F0A.txt').read(), expect)

    def test_empty(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            output = '''[]'''
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))):

                main_pr_integrate('13F0A', 'ALL', 'TP/13F', tdir)

                expect = ''
                self.assertTextEqual(File('13F0A.txt').read(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
