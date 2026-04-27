#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
from gadget.getgit import GitHub
from mod.nvl_pr_report import *
import mod.nvl_pr_report as prreport
from os.path import join, dirname, abspath
import os


class TestDailyPR(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_all(self):
        expect = '''{
    "nvl.common": {
        "Branch": "Built from branch: commonbranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        },
        "2391": {
            "title": "bypassing hvbigt per 3pm discussion",
            "MergedAt": "2023-02-02 23:49:29",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2391"
        }
    },
    "nvl.cpu": {
        "Branch": "Built from branch: cpubranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        },
        "2391": {
            "title": "bypassing hvbigt per 3pm discussion",
            "MergedAt": "2023-02-02 23:49:29",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2391"
        }
    },
    "nvl.gcd": {
        "Branch": "Built from branch: gcdbranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        },
        "2391": {
            "title": "bypassing hvbigt per 3pm discussion",
            "MergedAt": "2023-02-02 23:49:29",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2391"
        }
    },
    "nvl.pcd": {
        "Branch": "Built from branch: pcdbranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        },
        "2391": {
            "title": "bypassing hvbigt per 3pm discussion",
            "MergedAt": "2023-02-02 23:49:29",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2391"
        }
    },
    "nvl.hub": {
        "Branch": "Built from branch: hubbranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        },
        "2391": {
            "title": "bypassing hvbigt per 3pm discussion",
            "MergedAt": "2023-02-02 23:49:29",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2391"
        }
    }
}'''
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            output = '''[{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-03T19:37:16Z","number":2402,"title":"updating 3 files TPI_BASE_XXX and uservar to remove FSM","url":"https://github.com/intel-restricted/mtlp68/pull/2402"},
{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-02T23:49:29Z","number":2391,"title":"bypassing hvbigt per 3pm discussion","url":"https://github.com/intel-restricted/mtlp68/pull/2391"},
{"author":{"login":"patrick-hannon-intel"},"mergedAt":"2023-02-02T21:35:20Z","number":2387,"title":"Scn/scngt21fww5v1","url":"https://github.com/intel-restricted/mtlp68/pull/2387"}]'''
            report_file = f'{tdir}/01A0B.json'
            File(report_file).write(expect)
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))), \
                    MockVar(os.environ, 'IS_PR_COMMON', 'True'), \
                    MockVar(os.environ, 'DEST', 'bla/bla/NVLXXXXXXX01A0BSXXX'), \
                    MockVar(os.environ, 'CPU_Branch', 'cpubranch'), \
                    MockVar(os.environ, 'GCD_Branch', 'gcdbranch'), \
                    MockVar(os.environ, 'PCD_Branch', 'pcdbranch'), \
                    MockVar(os.environ, 'HUB_Branch', 'hubbranch'), \
                    MockVar(os.environ, 'CURRENT_BRANCH', 'commonbranch'), \
                    MockVar(GitHub, 'get_all_branches', Mock(return_value=['commonbranch', 'cpubranch', 'gcdbranch', 'pcdbranch', 'hubbranch'])), \
                    MockVar(prreport, 'get_input_timestamp', Mock(return_value='Fri Aug 1 22:12:41 2025 +0800')), \
                    MockVar(prreport, 'return_report_file', Mock(return_value=report_file)), \
                    MockVar(prreport, 'get_prno', Mock(return_value=[2387])):
                    main_pr_integrate('01A0B', '01A0A', tdir)
                    self.assertTextEqual(File('01A0B.json').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_empty(self):
        expect = '''{
    "nvl.common": {
        "Branch": "Built from branch: commonbranch"
    },
    "nvl.cpu": {
        "Branch": "Built from branch: cpubranch"
    },
    "nvl.gcd": {
        "Branch": "Built from branch: gcdbranch"
    },
    "nvl.pcd": {
        "Branch": "Built from branch: pcdbranch"
    },
    "nvl.hub": {
        "Branch": "Built from branch: hubbranch"
    }
}'''
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            output = '{}'
            report_file = f'{tdir}/01A0B.json'
            File(report_file).write(expect)
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))), \
                    MockVar(os.environ, 'IS_PR_COMMON', 'True'), \
                    MockVar(os.environ, 'DEST', 'bla/bla/NVLXXXXXXX01A0BSXXX'), \
                    MockVar(os.environ, 'CPU_Branch', 'cpubranch'), \
                    MockVar(os.environ, 'GCD_Branch', 'gcdbranch'), \
                    MockVar(os.environ, 'PCD_Branch', 'pcdbranch'), \
                    MockVar(os.environ, 'HUB_Branch', 'hubbranch'), \
                    MockVar(os.environ, 'CURRENT_BRANCH', 'commonbranch'), \
                    MockVar(GitHub, 'get_all_branches', Mock(return_value=['commonbranch', 'cpubranch', 'gcdbranch', 'pcdbranch', 'hubbranch'])), \
                    MockVar(prreport, 'return_report_file', Mock(return_value=report_file)), \
                    MockVar(prreport, 'get_prno', Mock(return_value=[])):
                    main_pr_integrate('01A0B', '01A0A', tdir)

                    self.assertTextEqual(File('01A0B.json').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_cpu(self):
        expect = '''{
    "nvl.common": {
        "Branch": "Built from branch: commonbranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        }
    },
    "nvl.cpu": {
        "Branch": "Built from branch: cpubranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        }
    }
}'''
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            output = '''[{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-03T19:37:16Z","number":2402,"title":"updating 3 files TPI_BASE_XXX and uservar to remove FSM","url":"https://github.com/intel-restricted/mtlp68/pull/2402"},
{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-02T23:49:29Z","number":2391,"title":"bypassing hvbigt per 3pm discussion","url":"https://github.com/intel-restricted/mtlp68/pull/2391"}]'''
            report_file = f'{tdir}/CX_01A0B.json'
            File(report_file).write(expect)
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))), \
                    MockVar(os.environ, 'DIEINDICATOR', 'CPU'), \
                    MockVar(os.environ, 'DEST', 'bla/bla/NVLXXXXXXX01A0BCX40'), \
                    MockVar(os.environ, 'COMMON_Branch', 'commonbranch'), \
                    MockVar(os.environ, 'CURRENT_BRANCH', 'cpubranch'), \
                    MockVar(GitHub, 'get_all_branches', Mock(return_value=['commonbranch', 'cpubranch'])), \
                    MockVar(prreport, 'return_report_file', Mock(return_value=report_file)), \
                    MockVar(prreport, 'get_prno', Mock(return_value=[2391])):
                    main_pr_integrate('01A0B', '01A0A', tdir)
                    self.assertTextEqual(File('CX_01A0B.json').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_not_branch(self):
        expect = '''{
    "nvl.common": {
        "TAG": "Built from TAG: blablabla -- Timestamp: Fri Aug 1 22:12:41 2025 +0800"
    },
    "nvl.cpu": {
        "Branch": "Built from branch: cpubranch",
        "2402": {
            "title": "updating 3 files TPI_BASE_XXX and uservar to remove FSM",
            "MergedAt": "2023-02-03 19:37:16",
            "Submitted by": "shiv-gourshetty-intel",
            "url": "https://github.com/intel-restricted/mtlp68/pull/2402"
        }
    }
}'''
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            output = '''[{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-03T19:37:16Z","number":2402,"title":"updating 3 files TPI_BASE_XXX and uservar to remove FSM","url":"https://github.com/intel-restricted/mtlp68/pull/2402"},
{"author":{"login":"shiv-gourshetty-intel"},"mergedAt":"2023-02-02T23:49:29Z","number":2391,"title":"bypassing hvbigt per 3pm discussion","url":"https://github.com/intel-restricted/mtlp68/pull/2391"}]'''
            report_file = f'{tdir}/CX_01A0B.json'
            File(report_file).write(expect)
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))), \
                    MockVar(os.environ, 'DIEINDICATOR', 'CPU'), \
                    MockVar(os.environ, 'DEST', 'bla/bla/NVLXXXXXXX01A0BCX40'), \
                    MockVar(os.environ, 'COMMON_Branch', 'blablabla'), \
                    MockVar(os.environ, 'CURRENT_BRANCH', 'cpubranch'), \
                    MockVar(GitHub, 'get_all_branches', Mock(return_value=['cpubranch'])), \
                    MockVar(prreport, 'get_input_timestamp', Mock(return_value='Fri Aug 1 22:12:41 2025 +0800')), \
                    MockVar(prreport, 'return_report_file', Mock(return_value=report_file)), \
                    MockVar(prreport, 'get_prno', Mock(return_value=[2391])):
                    main_pr_integrate('01A0B', '01A0A', tdir)
                    self.assertTextEqual(File('CX_01A0B.json').read(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
