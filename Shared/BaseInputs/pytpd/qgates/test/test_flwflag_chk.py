#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for template_common.py

Steps:
1. For module qgate, remove "qgates." in "from qgates." since py file and unitest are on the same folder.
2. Replace TestCheckerNameHere to the name of the checker class
3. Run coverage and see what code is not tested
4. To run, execute this file "test_template_common.py -v"

"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.flwflag_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from os.path import dirname
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import qgates.flwflag_chk as flwflag_chk
import shutil


class FlwflagCodeCheck(TestCase):

    def test_mocked_case1(self):
        envfile = f'POR_TP/TGLH81/EnvironmentFile.env'
        flwfile = r'''Version 1.0;

        ProgramStyle = Modular;

        TestPlan Flows;


        DUTFlow HVBIIOE_SubFlow
        {
            DUTFlowItem TPI_FLWFLGS_XXX_HVBIIOE TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_HVBIIOE
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    GoTo TPI_DIESLCT_XXX_HVBIIOE;
                }
                Result 2
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
            DUTFlowItem TPI_DIESLCT_XXX_HVBIIOE TPI_DIESLCT_XXX::TPI_DIESLCT_XXX_HVBIIOE
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
        }

        DUTFlow MAXCRLO_SubFlow
        {
            DUTFlowItem TPI_FLWFLGS_CXX_MAXCRLO IP_CPU::TPI_FLWFLGS_CXX::TPI_FLWFLGS_CXX_MAXCRLO
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    GoTo TPI_BASE_IPCPU_MAXCRLO;
                }
                Result 2
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
          DUTFlowItem TPI_BASE_IPCPU_MAXCRLO IP_CPU::TPI_BASE_IPCPU::TPI_BASE_IPCPU_MAXCRLO
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
                Result 2
                {
                    Property PassFail = "Pass";
                    Return 2;
                }
            }
        }

        DUTFlow MAIN
        {
                DUTFlowItem main1 ARR::MAIN1
                {
                        Result 1
                        {
                                GoTo main2;
                }
                }

                DUTFlowItem main2 SCN::MAIN2
                {
                        Result 1
                        {
                                GoTo main3;
                }
                 }
                DUTFlowItem main3 PTH::MAIN2
                {
                        Result 1
                        {
                                Return 1;
                }
                 }
        }

        DUTFlow INIT
        {
                DUTFlowItem init1 ARR::INIT1
                {
                        Result 1
                        {
                                GoTo init2;
                }
                 }

                DUTFlowItem init2 SCN::INIT2
                {
                        Result 1
                        {
                                GoTo init3;
                }
                 }
                DUTFlowItem init3 PTH::INIT2
                {

                        Result 1
                        {
                                Return 1;
                }
                }
        }

        FlowDefs
        {
                InitFlow = INIT;
                MainFlow = MAIN;
                LotEndFlow = LOTENDFLOW;
                LotStartFlow = LOTSTARTFLOW;
                TestPlanEndFlow = TESTPLANENDFLOW;
                TestPlanStartFlow = TESTPLANSTARTFLOW;
        }'''

        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True), \
                MockVar(flwflag_chk, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl').touch(flwfile, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            tpobj.mtpl.read_mtpl_flow()
            # Mock the passing case.
            obj = FlwflagCheck(tpobj)
            obj.main()
            expect = []
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 2)

    def test_mocked_case2(self):
        envfile = f'POR_TP/TGLH81/EnvironmentFile.env'
        flwfile = r'''Version 1.0;

        ProgramStyle = Modular;

        TestPlan Flows;


        DUTFlow HVBIIOE_SubFlow
        {
            DUTFlowItem TPI_DIESLCT_XXX_HVBIIOE TPI_DIESLCT_XXX::TPI_DIESLCT_XXX_HVBIIOE
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    GoTo TPI_FLWFLGS_XXX_HVBIIOE;
                }
                Result 2
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
            DUTFlowItem TPI_FLWFLGS_XXX_HVBIIOE TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_HVBIIOE
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
        }

        DUTFlow MAXCRLO_SubFlow
        {
            DUTFlowItem TPI_BASE_CXX_MAXCRLO IP_CPU::TPI_BASE_CXX::TPI_BASE_CXX_MAXCRLO
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    GoTo TPI_BASE_IPCPU_MAXCRLO;
                }
                Result 2
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
          DUTFlowItem TPI_BASE_IPCPU_MAXCRLO IP_CPU::TPI_BASE_IPCPU::TPI_BASE_IPCPU_MAXCRLO
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
                Result 2
                {
                    Property PassFail = "Pass";
                    Return 2;
                }
            }
        }

        DUTFlow MAIN
        {
                DUTFlowItem main1 ARR::MAIN1
                {
                        Result 1
                        {
                                GoTo main2;
                }
                }

                DUTFlowItem main2 SCN::MAIN2
                {
                        Result 1
                        {
                                GoTo main3;
                }
                 }
                DUTFlowItem main3 PTH::MAIN2
                {
                        Result 1
                        {
                                Return 1;
                }
                 }
        }

        DUTFlow INIT
        {
                DUTFlowItem init1 ARR::INIT1
                {
                        Result 1
                        {
                                GoTo init2;
                }
                 }

                DUTFlowItem init2 SCN::INIT2
                {
                        Result 1
                        {
                                GoTo init3;
                }
                 }
                DUTFlowItem init3 PTH::INIT2
                {

                        Result 1
                        {
                                Return 1;
                }
                }
        }

        FlowDefs
        {
                InitFlow = INIT;
                MainFlow = MAIN;
                LotEndFlow = LOTENDFLOW;
                LotStartFlow = LOTSTARTFLOW;
                TestPlanEndFlow = TESTPLANENDFLOW;
                TestPlanStartFlow = TESTPLANSTARTFLOW;
        }'''

        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True), \
                MockVar(flwflag_chk, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl').touch(flwfile, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            tpobj.mtpl.read_mtpl_flow()
            # Mock the failing case 227 for condition that no FLW flag module in subflow.
            obj = FlwflagCheck(tpobj)
            obj.main()
            expect = [{'id': 227,
                       'message': 'There is NO Flow "Flag Module" at the beginning of this         '
                                  'DUTFlow HVBIIOE_SubFlow\n'
                                  '.',
                       'module': 'BASE'},
                      {'id': 227,
                       'message': 'There is NO Flow "Flag Module" at the beginning of this         '
                       'DUTFlow MAXCRLO_SubFlow\n'
                       '.',
                       'module': 'BASE'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 1)

    def test_mocked_case3(self):
        envfile = f'POR_TP/TGLH81/EnvironmentFile.env'
        flwfile = r'''Version 1.0;

        ProgramStyle = Modular;

        TestPlan Flows;


        DUTFlow HVBIioe_SubFlow
        {
            DUTFlowItem TPI_FLWFLGS_XXX_HVBIioe TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_HVBIioe
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    GoTo TPI_DIESLCT_XXX_HVBIioe;
                }
                Result 2
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
            DUTFlowItem TPI_DIESLCT_XXX_HVBIioe TPI_DIESLCT_XXX::TPI_DIESLCT_XXX_HVBIioe
            {
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 0;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
        }
        DUTFlow MAIN
        {
            DUTFlowItem HVBIioe_SubFlow HVBIioe_SubFlow
            {
                Result -2
                {
                    Property PassFail = "Fail";
                    Return 1;
                }
                Result -1
                {
                    Property PassFail = "Fail";
                    Return 1;
                }
                Result 0
                {
                    Property PassFail = "Fail";
                    Return 1;
                }
                Result 1
                {
                    Property PassFail = "Pass";
                    Return 1;
                }
            }
        }
        DUTFlow INIT
        {
                DUTFlowItem init1 ARR::INIT1
                {
                        Result 1
                        {
                                GoTo init2;
                }
                 }

                DUTFlowItem init2 SCN::INIT2
                {
                        Result 1
                        {
                                GoTo init3;
                }
                 }
                DUTFlowItem init3 PTH::INIT2
                {

                        Result 1
                        {
                                Return 1;
                }
                }
        }

        FlowDefs
        {
                InitFlow = INIT;
                MainFlow = MAIN;
                LotEndFlow = LOTENDFLOW;
                LotStartFlow = LOTSTARTFLOW;
                TestPlanEndFlow = TESTPLANENDFLOW;
                TestPlanStartFlow = TESTPLANSTARTFLOW;
        }'''

        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True), \
                MockVar(flwflag_chk, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl').touch(flwfile, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            tpobj.mtpl.read_mtpl_flow()
            # Mock the failing case 228 to flag any subflow name is NOT all capital case.
            obj = FlwflagCheck(tpobj)
            obj.main()
            expect = [{'id': 228,
                       'message': 'HVBIioe_SubFlow name is NOT all capital case.',
                       'module': 'BASE'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
