#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for binctr
UT_DIR var is - /intel/tpvalidation/engtools/tptools/mtl/unittests/
"""
from setenv_unittest import UT_DIR, ROOT_ENV, UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from pymtpl.core import *
from pymtpl.binctr import *
import pymtpl.core as core
import pymtpl.binctr as binctr
from main.pymtpl import PyMtplArgs
from pymtpl.test.methods import VminTC, PrimeThermalSingleMeasurementTestMethod, ApexTC
from unittest.mock import patch, MagicMock
import inspect


class TestBaseBin(TestCase):

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_newbin(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=4400))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=4400)))])

        PyMtpl().main_one(PyObj)
        self.assertEqual(BinSSB.get_new_bin(-1, 100), 4401)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_manual_bin(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=90444400,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=4400,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90444400), r2=pFail(setbin=4400), r4=pFail(setbin=4400), r5=pFail(setbin=4419)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_bindef_file_does_not_exist(self):
        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'bindef', f'{UT_DIR_REPO}/sudheer_unit_test/bindef/Bin.bdefs'):
            with self.assertRaisesRegex(ErrorUser, 'Unable to load bindef file'):
                class PyObj:
                    # Start of the "python mtpl code" ====================
                    output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                    test1 = VminTC(name="Instance1",
                                   _comment="VminTC comment",
                                   EndVoltageLimits="0.9")
                    subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
                    # End of "python mtpl code"

                PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_existing_autobinner_bindef_file(self):
        """Checks for the case when the bin exists in the bindef file but is also in the autobinner json file"""
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000000",
                "r2": "44000001"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'bindef', f'{UT_DIR_REPO}/sudheer_unit_test/bindef/BinDefinitions.bdefs'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000000_fail_FUN_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_2;
            Return 0;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sort_bindef_file_input(self):
        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'bindef', f'{UT_DIR_REPO}/sudheer_unit_test/bindef/BinDefinitions.bdefs'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
            expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000002_fail_FUN_Instance1_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000003_fail_FUN_Instance1_4;
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44190162_fail_FUN_Instance1_5;
            Return 0;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sort_bindef_file_input_9digit_start_w_2(self):
        """Unit test for case when 9 digit bin starts with 2 - Like 244010000"""
        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'bindef', f'{UT_DIR_REPO}/sudheer_unit_test/bindef/BinDefinitions.bdefs'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN', binrange=[(4401, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
            expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99443920_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98443920_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010001_fail_FUN_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010002_fail_FUN_Instance1_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010003_fail_FUN_Instance1_4;
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44193920_fail_FUN_Instance1_5;
            Return 0;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sort_bindef_file_input_9digit_start_w_3(self):
        """Unit test for case when 9 digit bin starts with 3 - Like 344010000"""
        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'bindef', f'{UT_DIR_REPO}/sudheer_unit_test/bindef/BinDefinitions.bdefs'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN', binrange=[(4401, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
            expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99443920_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98443920_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010001_fail_FUN_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010002_fail_FUN_Instance1_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010003_fail_FUN_Instance1_4;
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44193920_fail_FUN_Instance1_5;
            Return 0;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sort_bindef_file_input_9digit_start_w_4(self):
        """Unit test for case when 9 digit bin starts with 4 - Like 444010000"""
        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'bindef', f'{UT_DIR_REPO}/sudheer_unit_test/bindef/BinDefinitions.bdefs'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN', binrange=[(4401, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
            expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99443920_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98443920_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010001_fail_FUN_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010002_fail_FUN_Instance1_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010003_fail_FUN_Instance1_4;
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44193920_fail_FUN_Instance1_5;
            Return 0;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class_bindef_file_input(self):
        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'bindef', f'{UT_DIR_REPO}/sudheer_unit_test/bindef/BinDefinitionsClass.bdefs'), MockVar(core.OPT, 'class90hbsbxx', True):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)])
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
            expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
            Return 0;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_manual_setbinstring(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=90444400,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"),
                               r1=pPass(setbin=4400,
                                        ret=1,
                                        trialaction="Exit"),
                               r4=pFail(setbin=4400,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90444400),
                                             r2=pFail(setbin=4400),
                                             r1=pPass(setbinstring='SoftBins.b10010000_pass_pure', ctr=44001256),
                                             r4=pFail(setbin=4400),
                                             r5=pFail(setbin=4419)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            SetBin SoftBins.b10010000_pass_pure;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_manual_setbinstring_error_no_counter(self):

        with self.assertRaisesRegex(ErrorUser, 'Counter is required when setbinstring is specified'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN')
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90444400),
                                                 r2=pFail(setbin=4400),
                                                 r1=pPass(setbinstring='b10010000'),
                                                 r4=pFail(setbin=4400),
                                                 r5=pFail(setbin=4419)))

    @with_(TempDir, chdir=True)
    def test_manual_setbinstring_error_setbin_and_setbinstring(self):
        with self.assertRaisesRegex(ErrorUser, 'setbin and setbinstring cannot be used'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN')
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90444400),
                                                 r2=pFail(setbin=4400),
                                                 r1=pPass(setbin=90444400, setbinstring='b10010000'),
                                                 r4=pFail(setbin=4400),
                                                 r5=pFail(setbin=4419)))

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90979744_fail_FUN_THERMAL_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_MTTtname;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ignorebin_4dig(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), autobinignorelist=[4400])
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90979744_fail_FUN_THERMAL_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ignorebin_8dig(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, autobinignorelist=[44000000])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000002_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000003_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44190162_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_diff_mtt_nonmtt_bins(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r5=pFail(setbin=4405,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r5=pFail(setbin=4400)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4405_fail_FUN_MTTtname";
            Return 0;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_passport(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r1=pPass(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),)
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r1=pPass(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 0;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ignore_ports_only(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"),
                               r1=pPass(trialaction="Continue"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO, ret=-2), rm1=pFail(setbin=AUTO, ret=-1), r1=pPass(), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Continue;
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90979744_fail_FUN_THERMAL_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_MTTtname;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_negative_ports_only(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_multirange(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)])
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=-44,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=-44,
                                         ret=-1,
                                         trialaction="Exit"),
                               r0=pFail(setbin=-44,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=-44,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=-44,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=-44,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90979744_fail_FUN_THERMAL_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_two_level_multirange(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=[(4400, 4401), (4410, 4415)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Test VminTC Instance3
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Test VminTC Instance4
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444410_fail_FUN_Instance2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    DUTFlowItem Instance3 Instance3
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444411_fail_FUN_Instance3;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance4;
        }
    }

    DUTFlowItem Instance4 Instance4
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_Instance4;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_two_level_multirange_error(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_nonmtldefault(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90979744_fail_FUN_THERMAL_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_MTTtname;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_outofrange(self):
        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4400))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=AUTO),
                                    r2=pFail(setbin=4400))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44)))])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1_SHARED_BIN;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)
        # with self.assertRaisesRegex(ErrorUser, 'All bin range is exhausted'):
        #     PyMtpl().main_one(PyObj)
        #     BinSSB.get_new_bin(-1, 100)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_existing_autobinner(self):
        bindict = {
            "MTTtname": {
                "bin": "4415",
                "r0": "SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname",
                "r2": "SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname"
            },
            "Instance1": {
                "r0": "\"SoftBins.b\" + FlowMatrix.bin + \"4415_fail_FUN_CCF_C68_MTTtname\"",
                "r2": "\"SoftBins.b\" + FlowMatrix.bin + \"4415_fail_FUN_CCF_C68_MTTtname\""
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4415_fail_FUN_CCF_C68_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4415_fail_FUN_CCF_C68_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_autobinner_modified(self):
        bindict = {
            "MTTtname": {
                "bin": "4415",
                "r0": "SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname",
                "r2": "SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname"
            },
            "Instance1": {
                "r0": "\"SoftBins.b\" + FlowMatrix.bin + \"4415_fail_FUN_CCF_C68_MTTtname\"",
                "r2": "\"SoftBins.b\" + FlowMatrix.bin + \"4415_fail_FUN_CCF_C68_MTTtname\""
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        # Run Pymtpl again

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4415_fail_FUN_CCF_C68_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4415_fail_FUN_CCF_C68_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444415_fail_FUN_CCF_C68_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_mtt_setbinstring(self):
        class PyObj:
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=4400,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))

        PyMtpl().main_one(PyObj)
        setbinstring = MTTBinSSB.get_mtt_setbinstring(4400, "MTTtname", [True], "r0")
        self.assertEqual(setbinstring, '"SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname"')

        setbinstring = MTTBinSSB.get_mtt_setbinstring(4400, "MTTtname", [False], "r2")
        self.assertEqual(setbinstring, '"SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname"')

    def test_convert_4digit_to_8digit(self):
        with self.assertRaisesRegex(Exception, 'Implement this in your subclass'):
            BaseBin.convert_4digit_to_8digit('4400')

    def test_convert_8digit_to_4digit(self):
        with self.assertRaisesRegex(Exception, 'Implement this in your subclass'):
            BaseBin.convert_8digit_to_4digit('90440000')

    def test_get_var_name(self):
        with self.assertRaisesRegex(Exception, 'Implement this in your subclass'):
            BaseBin.get_var_name()

    def test_get_new_bin(self):
        with self.assertRaisesRegex(Exception, 'Implement this in your subclass'):
            BaseBin.get_new_bin('4400', 100, set())

    @with_(TempDir, chdir=True)
    def test_get_default_port_bin_counter_start(self):
        # Mock BaseBin.bin_range and BaseBin.all_4digit
        mock_bin_range = [(1000, 2000)]
        mock_all_4digit = {1000, 2000, 3000}

        with patch.object(BaseBin, 'bin_range', mock_bin_range), \
                patch.object(BaseBin, 'all_4digit', mock_all_4digit):
            # Test when bin_range is present
            counter_start = Sort8dig.get_default_port_bin_counter_start()
            self.assertTrue(0 <= counter_start <= 7000, "Counter start should be within the range 0 to 7000")

            # Test when bin_range is not present
            with patch.object(BaseBin, 'bin_range', []):
                counter_start = Sort8dig.get_default_port_bin_counter_start()
                self.assertTrue(0 <= counter_start <= 7000, "Counter start should be within the range 0 to 7000")

    @with_(TempDir, chdir=True)
    def test_convert_4digit_to_8digit_MTTBinSSB(self):
        digit4 = 4400
        expected_digit8 = '90444400'
        self.assertEqual(MTTBinSSB.convert_4digit_to_8digit(digit4), expected_digit8)

        digit4 = 5678
        expected_digit8 = '90565678'
        self.assertEqual(MTTBinSSB.convert_4digit_to_8digit(digit4), expected_digit8)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_load_ignore_bins_invalid(self):
        with self.assertRaisesRegex(ErrorInput, 'Invalid bin value'):
            BaseBin.load_ignore_bins(["1234", ""])
        with self.assertRaisesRegex(ErrorInput, 'Invalid bin value'):
            BaseBin.load_ignore_bins(["1234", "1"])
        with self.assertRaisesRegex(ErrorInput, 'Invalid bin value'):
            BaseBin.load_ignore_bins(["1234", "12"])
        BaseBin.load_ignore_bins(["1234", "123"])  # valid
        BaseBin.load_ignore_bins(["1234", "1234"])  # valid
        with self.assertRaisesRegex(ErrorInput, 'Invalid bin value'):
            BaseBin.load_ignore_bins(["1234", "12345"])
        with self.assertRaisesRegex(ErrorInput, 'Invalid bin value'):
            BaseBin.load_ignore_bins(["1234", "123456"])
        BaseBin.load_ignore_bins(["1234", "1234567"])  # valid
        BaseBin.load_ignore_bins(["1234", "12345678"])  # valid
        with self.assertRaisesRegex(ErrorInput, 'Invalid bin value'):
            BaseBin.load_ignore_bins(["1234", "123456789"])

    def test_getbin2dig(self):
        # test getting the hardbin from 8 digit bin
        self.assertEqual(BaseBin._get_hardbin_match('b90680000'), '68')
        self.assertEqual(BaseBin._get_hardbin_match('b90080001'), '08')
        self.assertEqual(BaseBin._get_hardbin_match('b90909790'), '90')
        self.assertEqual(BaseBin._get_hardbin_match('b90949899'), '94')
        # bins which we don't want to track
        self.assertEqual(BaseBin._get_hardbin_match('b90970000'), None)  # no bin 97
        self.assertEqual(BaseBin._get_hardbin_match('b90980001'), None)  # no bin 98
        self.assertEqual(BaseBin._get_hardbin_match('b90990002'), None)  # no bin 99
        self.assertEqual(BaseBin._get_hardbin_match('b99000001'), None)  # no pass bins

    def test_getbin4dig(self):
        # test getting the softbin from 8 digit bin
        self.assertEqual(BaseBin._get_softbin_match('b90680000'), '6800')
        self.assertEqual(BaseBin._get_softbin_match('b90080100'), '0801')
        self.assertEqual(BaseBin._get_softbin_match('b90909790'), '9097')
        self.assertEqual(BaseBin._get_softbin_match('b90949899'), '9498')
        # bins which we don't want to track
        self.assertEqual(BaseBin._get_softbin_match('b90970000'), None)  # bin 97
        self.assertEqual(BaseBin._get_softbin_match('b90980100'), None)  # bin 98
        self.assertEqual(BaseBin._get_softbin_match('b90990200'), None)  # bin 99
        self.assertEqual(BaseBin._get_softbin_match('b99000001'), None)  # no pass bins

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basebin_error_incorrect_bin_use_autobinner(self):
        # Unit test for bug found in production where a test was moved from manual bin to AUTO and the 8-digit bins were being repeated.
        # First run: one test with autobin, one with manual bin
        # The bin range is restricted to one bin to not allow for new 4-dig bins.
        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4400), (801, 801)])
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-80)))
        with self.assertRaisesRegex(ErrorUser, 'Please check the definition of setbin'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basebin_error_incorrect_5dig_setbin_autobinner(self):
        # Unit test for to check if we can allow a 5 digit setbin value for autobinner
        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4400), (801, 801)])
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44000)))
        with self.assertRaisesRegex(ErrorUser, 'Please check the definition of setbin'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_write_sbdef_file_skips_for_only_98_99(self):
        Initialize.clear_all()
        BaseBin.clear_bins()
        # Only software (98) and clamp (99) bins in sbdef_dict
        BaseBin.sbdef_dict = {
            'b90990101_fail_FAIL_DPS_ALARM': '90990101',
            'b90980101_fail_FAIL_SYSTEM_SOFTWARE': '90980101'
        }
        out = list(BaseBin.write_sbdef_file())
        self.assertEqual(out, [])
        # cleanup
        BaseBin.clear_bins()

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_bin_counter_cross_reference(self):
        """Test that bin strategies check counter sets and vice versa"""

        class PyObj:
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450))
            # Create test instance that will use both bins and counters
            test1 = VminTC(name="Test1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        r0=pFail(setbin=-44),  # Will get auto-assigned bin
                                        r2=pFail(setbin=-44)))  # Will get different bin
            subflow = Flow('SubFlow1', [test1])

        PyMtpl().main_one(PyObj)

        # Verify that bins don't collide with counters
        # The bin strategy should have checked the counter set
        # The counter strategy should have checked the bin set
        # With cross-referencing, we should have unique values across both sets
        all_bins = Initialize.nonmttbinstrategy.all_8digit
        all_counters = Initialize.nonmttctrstrategy.all_8digit_counter

        # Check that there's no overlap between bins and counters
        overlap = all_bins.intersection(all_counters)
        self.assertEqual(len(overlap), 0,
                         f"Found overlapping bins and counters: {overlap}")


class TestClass8dig(TestCase):
    '''
    TODO: Need tests for non VminTC test classes and port 4 port 5
    TODO: Need tests for sbdef file creations
    TODO: Use Auto-bin on ignore ports only to get bin for mtt test
    '''

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_get_newbin(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=90440000))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=90440100)))])

        PyMtpl().main_one(PyObj)
        self.assertEqual(NVLClass8dig.get_new_bin(-1, 100), 4402)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_manual_bin(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=90440000,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=4400,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440000), r2=pFail(setbin=90440000), r4=pFail(setbin=90440000), r5=pFail(setbin=90441900)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_manual_setbinstring(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=90440000),
                                             r1=pPass(setbinstring='b10010000_pass_pure_bin', ctr=0),
                                             r2=pFail(setbin=90440000),
                                             r4=pFail(setbin=90440000),
                                             r5=pFail(setbin=90441900)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            SetBin b10010000_pass_pure_bin;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_Instance1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_kill_to_edc_setbin(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_manual_invalid_bin(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=90440000,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'NVLClass8dig strategy requires 7 or 8-digit bin values'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_shared_bin(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440000)),
                           Fitem('SAME', test2, r0=pFail(setbin=90440000)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1_SHARED_BIN;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1_SHARED_BIN;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_manual_bin_different_bin_for_each_port(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=90440000,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"),
                               r3=pFail(setbin=4400,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440000), r2=pFail(setbin=90440001), r3=pFail(setbin=90440100), r5=pFail(setbin=90441900)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 3
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_MTTtname;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90440100_fail_FUN_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_thermal_reset_only(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            test2 = MultiTrial(name="MTTtname_1",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1_1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

MultiTrialTest MTTtname_1
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1_1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname_1";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname_1";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname_1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

    FlowItem MTTtname_1 MTTtname_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_apextc_thermal_reset_only(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=ApexTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            test2 = MultiTrial(name="MTTtname_1",
                               _comment='I am mtt',
                               template=ApexTC(name="Instance1_1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest ApexTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

MultiTrialTest MTTtname_1
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest ApexTC Instance1_1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname_1";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname_1";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname_1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

    FlowItem MTTtname_1 MTTtname_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_update_nonmtt_bin_on_keyerror(self):
        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=90440100)))])

        PyMtpl().main_one(PyObj)

        setbinstring = NVLClass8dig.get_non_mtt_setbinstring(90440000, "Instance1", [False], "r0", inspect.currentframe().f_lineno)
        self.assertEqual(setbinstring, "b90440000_fail_FUN_Instance1")

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_get_invalid_thermal_reset_bin(self):
        with self.assertRaisesRegex(ValueError, 'Invalid bintype'):
            NVLClass8dig.get_thermal_or_reset_bin(45, 972, "something", "random_name")

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_shared_autobin_NONMTT(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test3 = VminTC(name="Instance1_2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test3, r0=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1_1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_2;
        }
    }

    FlowItem Instance1_2 Instance1_2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440002_fail_FUN_Instance1_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_bin_range_exhaust(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test3 = VminTC(name="Instance1_2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90450000)),
                           Fitem('SAME', test2, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test3, r0=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90450000_fail_FUN_Instance1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1_1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_2;
        }
    }

    FlowItem Instance1_2 Instance1_2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_bin_range_exhaust_multi_bin_range(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4400), (3500, 3500)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test3 = VminTC(name="Instance1_2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test4 = VminTC(name="Instance1_3",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90450000)),
                           Fitem('SAME', test2, r0=pFail(setbin=-44)),
                           Fitem('SAME', test3, r0=pFail(setbin=-35)),
                           Fitem('SAME', test4, r0=pFail(setbin=-44)))
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_3
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90450000_fail_FUN_Instance1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1_1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_2;
        }
    }

    FlowItem Instance1_2 Instance1_2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90350000_fail_FUN_Instance1_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_3;
        }
    }

    FlowItem Instance1_3 Instance1_3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1_3;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_shared_autobin_MTT(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4400))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"))
            test2 = MultiTrial(name="MTTtname_1",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1_2",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
    }
}

MultiTrialTest MTTtname_1
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1 + "_1"
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname_1";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname_1;
        }
    }

    FlowItem MTTtname_1 MTTtname_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_MTTtname_1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_default_thermal_reset_bins(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), defaultthermalbin=90974500, defaultresetbin=90451900)
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974500_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90451900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_default_thermal_reset_bins_multirange(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4450)], defaultthermalbin=(90974400, 90974500), defaultresetbin=(90451900, 90441906))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r4=pFail(setbin=-45), r5=pFail(setbin=-45)),
                           Fitem('SAME', test2, r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974500_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90451900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441906_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}
        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_diff_mtt_nonmtt_bins(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r5=pFail(setbin=4405,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r5=pFail(setbin=90440000)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4405_fail_FUN_MTTtname";
            Return 0;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_passport(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r1=pPass(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),)
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r1=pPass(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 0;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_ignore_ports_only(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"),
                               r1=pPass(trialaction="Continue"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO, ret=-2), rm1=pFail(setbin=AUTO, ret=-1), r1=pPass(), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Continue";
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_negative_ports_only(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_multirange(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=[(4425, 4450), (4475, 4499)])
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               rm2=pFail(setbin=-44,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=-44,
                                         ret=-1,
                                         trialaction="Exit"),
                               r0=pFail(setbin=-44,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=-44,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=-44,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=-44,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4425_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4425_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4425_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4425_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90442500_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90442500_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig__autobin_two_level_multirange(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4401), (4410, 4415)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance3
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance4
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90441000_fail_FUN_Instance2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    FlowItem Instance3 Instance3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90441100_fail_FUN_Instance3;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance4;
        }
    }

    FlowItem Instance4 Instance4
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440100_fail_FUN_Instance4;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_two_level_multirange_error(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_nonVminTC(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=PrimeThermalSingleMeasurementTestMethod(name="Instance1",
                                                                                LowerTolerance=9999,
                                                                                _comment="VminTC comment"),
                               rm2=pFail(setbin=AUTO,
                                         ret=-2,
                                         trialaction="Exit"),
                               rm1=pFail(setbin=AUTO,
                                         ret=-1,
                                         trialaction="Exit"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"),
                               r4=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r5=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest PrimeThermalSingleMeasurementTestMethod Instance1
    {
        # VminTC comment
        LowerTolerance = 9999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
    }

}
'''
# ...existing code...
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    def test_class8dig_auto_bin_existing_autobinner(self):
        bindict = {
            "MTTtname": {
                "bin": "4415",
                "r0": "90441500",
                "r2": "90441500"
            },
            "Instance1": {
                "r0": "4415",
                "r2": "4415"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4415_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4415_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90441500_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90441500_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_get_mtt_setbinstring(self):
        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=4400,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4400,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440000), r2=pFail(setbin=90440000)))

        PyMtpl().main_one(PyObj)
        setbinstring = MTTNVLClass8dig.get_mtt_setbinstring(4400, "MTTtname", [True], "r0")
        self.assertEqual(setbinstring, '"b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname"')

        setbinstring = MTTBinSSB.get_mtt_setbinstring(4400, "MTTtname", [False], "r2")
        self.assertEqual(setbinstring, '"b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname"')

    @with_(TempDir, chdir=True)
    def test_update_autosetbinstring(self):
        # Mock necessary attributes and methods
        mock_setbin = 1234
        mock_id_lno = 10
        mock_portid = 'r0'
        mock_tname = 'TestName'
        mock_updatesetbinstring = [True]
        mock_portobj_type = 'pFail'
        mock_templatename = 'TemplateName'
        mock_mtt_ignore_list = []

        with patch.object(MTTNVLClass8dig, 'mtt_ignore_list', mock_mtt_ignore_list), \
                patch.object(BaseBin, '_get_mtt_autosetbinstring', return_value='1234_fail_TestName'):

            # Test when regex pattern does not match
            with patch.object(MTTNVLClass8dig, '_get_mtt_autosetbinstring', return_value='invalid_string'):
                with self.assertRaisesRegex(ErrorUser, 'Invalid setbinstring value of invalid_string'):
                    MTTNVLClass8dig.update_autosetbinstring(mock_setbin, mock_id_lno, mock_portid, mock_tname, mock_updatesetbinstring, mock_portobj_type, mock_templatename)

    def test_class8dig_convert_4digit_to_8digit_NVLClass8dig(self):
        NVLClass8dig.clear_bins()
        digit4 = 4400
        expected_digit8 = '90440000'
        self.assertEqual(NVLClass8dig.convert_4digit_to_8digit(digit4), expected_digit8)

        digit4 = 4400
        expected_digit8 = '90440001'
        self.assertEqual(NVLClass8dig.convert_4digit_to_8digit(digit4), expected_digit8)

        digit4 = 5678
        expected_digit8 = '90567800'
        self.assertEqual(NVLClass8dig.convert_4digit_to_8digit(digit4), expected_digit8)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_change_repeat_runs(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-44)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-45), r2=pFail(setbin=-45)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n45000000_fail_Instance1_0,
    n45000001_fail_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90450000_fail_FUN_Instance1;
            IncrementCounters FUN::n45000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90450000_fail_FUN_Instance1;
            IncrementCounters FUN::n45000001_fail_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_and_manual_then_repeat_auto(self):
        # Unit test for bug found in production where a test was moved from manual bin to AUTO and the 8-digit bins were being repeated.
        # First run: one test with autobin, one with manual bin
        # The bin range is restricted to one bin to not allow for new 4-dig bins.
        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, edc=True, r0=pFail(setbin=90450100)),
                           Fitem('SAME', test3, r0=pFail(setbin=AUTO))
                           )
        PyMtpl().main_one(PyObj)

        # Second run: move both to AUTO
        class PyObj2:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, edc=True, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test3, r0=pFail(setbin=AUTO))
                           )
        PyMtpl().main_one(PyObj2)
        expect2 = '''
CSharpTest VminTC AutoTest
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC ManualTest
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

CSharpTest VminTC AutoTest2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem AutoTest AutoTest
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_AutoTest;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo ManualTest;
        }
    }

    FlowItem ManualTest ManualTest @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440002_fail_FUN_ManualTest;
            GoTo AutoTest2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo AutoTest2;
        }
    }

    FlowItem AutoTest2 AutoTest2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_AutoTest2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect2)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_4dig_autobin_and_manual_then_repeat_auto(self):
        # Unit test for bug found in production where a test was moved from manual bin to AUTO and the 8-digit bins were being repeated.
        # First run: one test with autobin, one with manual bin
        # The bin range is restricted to one bin to not allow for new 4-dig bins.
        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=-4400)),
                           Fitem('SAME', test3, r0=pFail(setbin=-4400))
                           )
        PyMtpl().main_one(PyObj)

        # Second run: move both to AUTO
        class PyObj2:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=-4400)),
                           Fitem('SAME', test3, r0=pFail(setbin=-4400))
                           )
        PyMtpl().main_one(PyObj2)
        expect2 = '''
CSharpTest VminTC AutoTest
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC AutoTest2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem AutoTest AutoTest
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_AutoTest;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo AutoTest2;
        }
    }

    FlowItem AutoTest2 AutoTest2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_AutoTest2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
        '''
        self.assertTextEqual(File('out.mtpl').read(), expect2)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_3dig_autobin_and_manual_then_repeat_auto(self):
        # Unit test for bug found in production where a test was moved from manual bin to AUTO and the 8-digit bins were being repeated.
        # First run: one test with autobin, one with manual bin
        # The bin range is restricted to one bin to not allow for new 4-dig bins.
        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(801, 801))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=-801)),
                           Fitem('SAME', test3, r0=pFail(setbin=-801))
                           )
        PyMtpl().main_one(PyObj)

        # Second run: move both to AUTO
        class PyObj2:
            output = InitializeNVLClass('out', 'FUN', binrange=(801, 801))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            test3 = VminTC(name="AutoTest2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=-801)),
                           Fitem('SAME', test3, r0=pFail(setbin=-801))
                           )
        PyMtpl().main_one(PyObj2)
        expect2 = '''
CSharpTest VminTC AutoTest
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC AutoTest2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem AutoTest AutoTest
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080100_fail_FUN_AutoTest;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo AutoTest2;
        }
    }

    FlowItem AutoTest2 AutoTest2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080101_fail_FUN_AutoTest2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
        '''
        self.assertTextEqual(File('out.mtpl').read(), expect2)

    @with_(TempDir, chdir=True)
    def test_initialize_bindefovrd(self):
        '''
        Test overriding hardbin and softbin names in bindefdict using bindefovrd param and using bindefdefaults in the NVLdefault class.
        '''

        # Save original state
        original_write_hb = False
        if NVLdefault:
            original_write_hb = NVLdefault.write_hardbins_to_sbdef
            NVLdefault.write_hardbins_to_sbdef = True

        # overriding defaults to test
        try:
            Initialize.clear_all()

            bin_limits = [(9801, 9802), (9901, 9902), (6700, 6700)]

            class PyObj1:
                output = InitializeNVLClass('out', 'FUN', binrange=bin_limits,
                                            bindefovrd={
                                                # overriding hardbin names
                                                "67": "b67_FAIL_ABRITRARY_NAME",
                                                # example softbin override
                                                "9802": "9802_B98_OVERRIDE_NAME",
                                                "6700": "6700_FAIL_ARBITRARY_NAME",
                                                "123929323": "invalid_but_is_ignored"
                                            }
                                            )

                self.assertTextEqual(Initialize.bindefdict["67"], "b67_FAIL_ABRITRARY_NAME")  # changed in bindefovrd
                self.assertTextEqual(Initialize.bindefdict["68"], "b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA")  # unchanged hb
                self.assertTextEqual(Initialize.bindefdict["6700"], "6700_FAIL_ARBITRARY_NAME")  # changed sb in bindefovrd - it even added a key
                self.assertTextEqual(Initialize.bindefdict["9802"], "9802_B98_OVERRIDE_NAME")  # changed sb in bindefovrd - it even added a key

                # Verify that the softbin names are as expected
                self.assertTextEqual(NVLClass8dig._get_softbin_name("9802"), "9802_B98_OVERRIDE_NAME")
                self.assertTextEqual(NVLClass8dig._get_softbin_name("6700"), "6700_FAIL_ARBITRARY_NAME")

                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(r0=pFail(setbin=-67),
                                        ))])

            PyMtpl().main_one(PyObj1)

            # We expect the counters to prevent the same bins from being used
            expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup HardBins
    {
        Bin b67_FAIL_ABRITRARY_NAME    67    : "b67_FAIL_ABRITRARY_NAME",    Fail;
    }

    BinGroup SoftBins
    {
        Bin b6700_FAIL_ARBITRARY_NAME    6700    : "b6700_FAIL_ARBITRARY_NAME",    b67_FAIL_ABRITRARY_NAME;
    }

    BinGroup DataBins
    {
        LeafBin b90670000_fail_FUN_Instance1    90670000    : "b90670000_fail_FUN_Instance1",    b6700_FAIL_ARBITRARY_NAME;
    }

}
'''
            self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), expect)

        finally:
            # Restore original state
            if NVLdefault:
                NVLdefault.write_hardbins_to_sbdef = original_write_hb

    @with_(TempDir, chdir=True)
    def test_sbdef_979899(self):
        '''
        Testing that an sbdef which only has hb 97,98,99 still generates
        '''

        bin_limits = [(9801, 9802), (9901, 9902), (9700, 9700)]

        class PyObj1:
            output = InitializeNVLClass('out', 'PTH_THRSOAK', binrange=bin_limits, edcportctrbinrange=bin_limits)

            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(  # implicitly, bin 99 and 98 for -2 and -1 ports
                            r0=pFail(setbin=-97)
                       ))])

        PyMtpl().main_one(PyObj1)

        # We expect the counters to prevent the same bins from being used
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
    }

    BinGroup DataBins
    {
        LeafBin b90970000_fail_PTH_THRSOAK_Instance1    90970000    : "b90970000_fail_PTH_THRSOAK_Instance1",    b9700;
    }

}
'''

        self.assertTextEqual(File('PTH_THRSOAK_SubBinDefinitions.sbdefs').read(), expect)


class TestServerClass8dig(TestCase):
    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_single_bin_setbin_4dig(self):
        """Test for 4 digit bin counting results in 90HBSBxx combined with other setbin options"""
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=[(6400, 6401), (6420, 6421)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-64),
                           r2=pFail(setbin=90642000),
                           r3=pFail(setbin=-6420),
                           r4=pFail(setbin=-64),
                           r5=pFail(setbin=-6420),
                           r6=pFail(setbin=-6400),
                           r7=pFail(setbin=-64),
                           r8=pFail(setbin=-6400)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90640000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90642000_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90642001_fail_FUN_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90640001_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90642002_fail_FUN_Instance1_5;
        }
        Result 6
        {
            Property PassFail = "Fail";
            SetBin b90640002_fail_FUN_Instance1_6;
        }
        Result 7
        {
            Property PassFail = "Fail";
            SetBin b90640003_fail_FUN_Instance1_7;
        }
        Result 8
        {
            Property PassFail = "Fail";
            SetBin b90640004_fail_FUN_Instance1_8;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_single_bin_setbin_3dig(self):
        """Test for 3 digit bin counting results in 90HBSBxx combined with other setbin options"""
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=[(800, 801), (820, 821)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-8),
                           r2=pFail(setbin=90082000),
                           r3=pFail(setbin=-820),
                           r4=pFail(setbin=-8),
                           r5=pFail(setbin=-820),
                           r6=pFail(setbin=-800),
                           r7=pFail(setbin=-8),
                           r8=pFail(setbin=-800)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90082000_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90082001_fail_FUN_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90080001_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90082002_fail_FUN_Instance1_5;
        }
        Result 6
        {
            Property PassFail = "Fail";
            SetBin b90080002_fail_FUN_Instance1_6;
        }
        Result 7
        {
            Property PassFail = "Fail";
            SetBin b90080003_fail_FUN_Instance1_7;
        }
        Result 8
        {
            Property PassFail = "Fail";
            SetBin b90080004_fail_FUN_Instance1_8;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_dmr_class8dig_manual_setbinstring(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450), edcportctrbinrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             rm2=pFail(),
                                             rm1=pFail(),
                                             r0=pFail(setbin=90440000),
                                             r1=pPass(setbinstring='b10010000_pass_pure_bin', ctr=0),
                                             r2=pFail(setbin=90440001),
                                             r4=pFail(setbin=90440002),
                                             r5=pFail(setbin=90441900)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            SetBin b10010000_pass_pure_bin;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90440002_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_bin_8dig(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=90440000))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=90440001)))])

        PyMtpl().main_one(PyObj)
        self.assertEqual(ServerClass8dig.get_new_bin_8dig(-1, -44), 90440002)  # from hb
        self.assertEqual(ServerClass8dig.get_new_bin_8dig(-1, -1), 90440003)  # auto
        self.assertEqual(ServerClass8dig.get_new_bin_8dig(-1, 0), 90440004)  # auto

    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_bin_8dig_when_full(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4400))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=90440000))),
            ])

        PyMtpl().main_one(PyObj)
        self.assertEqual(ServerClass8dig.get_new_bin_8dig(-1, -44), 90440001)  # from hb
        self.assertEqual(ServerClass8dig.get_new_bin_8dig(-1, -1), 90440002)  # auto

        for i in range(3, 100):
            ServerClass8dig.all_8digit.add(f'904400{i:02d}')
        with self.assertRaisesRegex(ErrorUser, "Unable to find a valid 8-digit bin in the specified range"):
            ServerClass8dig.get_new_bin_8dig(-1, -44)  # from hb

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_two_level_multirange_error(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_34dig_bin_range_error(self):
        # 4 digit same hb bin out of range
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-4402)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj)

        # 4 digit same hb bin in range but not left bound
        class PyObj1:
            output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-4401)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj1)

        # 4 digit different hb out of range
        class PyObj2:
            output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-3900)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj2)

        # 3 digit same hb out of range
        class PyObj3:
            output = InitializeDMRClass('out', 'FUN', binrange=[(800, 801)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-802)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj3)

        # 3 digit same hb in range but not left bound
        class PyObj4:
            output = InitializeDMRClass('out', 'FUN', binrange=[(800, 801)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-801)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj4)

        # 3 digit range, 4 digit different hb out of range
        class PyObj5:
            output = InitializeDMRClass('out', 'FUN', binrange=[(800, 801)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-8000)))
            ])

        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj5)

        # 4 digit range, 3 digit different hb out of range
        class PyObj6:
            output = InitializeDMRClass('out', 'FUN', binrange=[(8000, 8001)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-800)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj6)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_rm12_bin_range_error(self):
        # make sure the error for 98 and 99 ports makes sense
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please make sure bin 98/99 ranges are set"):
            PyMtpl().main_one(PyObj)

        # set port -2 so we don't have an error on it, but don't set port -1
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm2=pFail(setbin=-44), r0=pFail(setbin=-44)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please make sure bin 98/99 ranges are set"):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_setbin_positive_length_error(self):
        # testing that a setbin with a positive length raises an error if it's not 8 digits
        for bin in [443, 4444, 44555, 446666, 4477777]:
            class PyObj1:
                output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
                subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem('SAME', r0=pFail(setbin=bin)))])
            with self.assertRaisesRegex(ErrorUser, "Invalid setbin value"):
                PyMtpl().main_one(PyObj1)

        for bin in [4, 44, 449999999, 4410101010]:
            with self.assertRaisesRegex(ErrorUser, f"Please use a 3-8-digit input setbin"):
                class PyObjN:
                    output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
                    subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem('SAME', r0=pFail(setbin=bin)))])
                PyMtpl().main_one(PyObjN)

    @with_(TempDir, chdir=True)
    def test_setbin_negative_length_error(self):
        # testing that a setbin with a negative length raises an error if it's not 1-4 digits
        for bin in [-44555, -446666, -4477777, -44888888, -449999999, -4410101010]:
            class PyObj1:
                output = InitializeDMRClass('out', 'FUN', binrange=[(4400, 4401)])
                subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem('SAME', r0=pFail(setbin=bin)))])
            with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
                PyMtpl().main_one(PyObj1)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_hb_bin_change_repeat_runs(self):
        # testing that a port set to -HB gets changed
        bin_limits = [(4400, 4450), (4500, 4550), (9800, 9850), (9900, 9950)]

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-44)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-45), r2=pFail(setbin=-45)))

        PyMtpl().main_one(PyObj1)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990000_fail_FUN_Instance1_n2;
            IncrementCounters FUN::n90990000_fail_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980000_fail_FUN_Instance1_n1;
            IncrementCounters FUN::n90980000_fail_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90450000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n90450000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99440000_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90450001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n90450001_fail_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    # testing that a port set to AUTO gets changed when the bin limits change
    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_auto_bin_change_repeat_runs(self):
        bin_limits = [(4400, 4450)]

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeDMRClass('out', 'FUN', binrange=(4500, 4550))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))

        PyMtpl().main_one(PyObj1)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90450000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90450001_fail_FUN_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_kill_to_edc_remove_setbin(self):
        # Move test from kill with setbin to edc with no setbin

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail()))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
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

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    # Test if we can recover from a bin not being in the bin registry
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_missing_setbinstring(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=90440000))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=90440001)))])

        PyMtpl().main_one(PyObj)
        self.assertEqual(ServerClass8dig.get_non_mtt_setbinstring("90440001", "Instance2", None, "r0", inspect.currentframe().f_lineno), "b90440001_fail_FUN_Instance2_0")
        del ServerClass8dig.bin_registry["90440001"]
        self.assertEqual(ServerClass8dig.get_non_mtt_setbinstring("90440001", "Instance2", None, "r0", inspect.currentframe().f_lineno), "b90440001_fail_FUN_Instance2_0")

    @with_(TempDir, chdir=True)
    def test_initialize_bindefovrd(self):
        '''
        Test overriding hardbin and softbin names in bindefdict using bindefovrd param and using bindefdefaults in the DMRdefaults class.
        '''

        # Save original state
        original_bindefdefaults = None
        if DMRdefault and DMRdefault.bindefdefaults is not None:
            original_bindefdefaults = DMRdefault.bindefdefaults.copy()

        # overriding defaults to test
        try:
            Initialize.clear_all()

            bin_limits = [(9801, 9802), (9901, 9902), (6800, 6800), (6700, 6700)]

            class PyObj1:
                output = InitializeDMRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits,
                                            bindefovrd={
                                                # overriding hardbin names
                                                "68": "b68_FAIL_MIO_DDR",
                                                # example softbin override
                                                "9802": "9802_B98_OVERRIDE_NAME",
                                                "6700": "6700_FAIL_ARBITRARY_NAME",
                                                "123929323": "invalid_but_is_ignored"
                                            }
                                            )

                self.assertTextEqual(Initialize.bindefdict["67"], "b67_FAIL_MISSING_VISUAL_ID_2D_MARK")  # unchanged hb
                self.assertTextEqual(Initialize.bindefdict["68"], "b68_FAIL_MIO_DDR")  # changed hb in bindefovrd
                self.assertTextEqual(Initialize.bindefdict["98"], "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN")  # changed hb in defaults
                self.assertTextEqual(Initialize.bindefdict["99"], "b99_FAIL_HARDWARE_ERROR")  # changed hb in defaults
                self.assertTextEqual(Initialize.bindefdict["6700"], "6700_FAIL_ARBITRARY_NAME")  # changed sb in bindefovrd - it even added a key
                self.assertTextEqual(Initialize.bindefdict["9801"], "9801_FAIL_TESTCLASS_EXCEPTION_ERROR")  # changed sb in defaults
                self.assertTextEqual(Initialize.bindefdict["9802"], "9802_B98_OVERRIDE_NAME")  # changed sb in bindefovrd - it even added a key

                # Verify that the softbin names are as expected
                self.assertTextEqual(ServerClass8dig._get_softbin_name("9801"), "9801_FAIL_TESTCLASS_EXCEPTION_ERROR")
                self.assertTextEqual(ServerClass8dig._get_softbin_name("9802"), "9802_B98_OVERRIDE_NAME")
                self.assertTextEqual(ServerClass8dig._get_softbin_name("6700"), "6700_FAIL_ARBITRARY_NAME")

                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', edc=False,
                                        r0=pFail(setbin=-67),
                                        r3=pFail(setbin=-68),
                                        r2=pFail(setbin=-68)))])

            PyMtpl().main_one(PyObj1)

            # We expect the counters to prevent the same bins from being used
            expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup HardBins
    {
        Bin b67_FAIL_MISSING_VISUAL_ID_2D_MARK    67    : "b67_FAIL_MISSING_VISUAL_ID_2D_MARK",    Fail;
        Bin b68_FAIL_MIO_DDR    68    : "b68_FAIL_MIO_DDR",    Fail;
        Bin b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN    98    : "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN",    Fail;
        Bin b99_FAIL_HARDWARE_ERROR    99    : "b99_FAIL_HARDWARE_ERROR",    Fail;
    }

    BinGroup SoftBins
    {
        Bin b6700_FAIL_ARBITRARY_NAME    6700    : "b6700_FAIL_ARBITRARY_NAME",    b67_FAIL_MISSING_VISUAL_ID_2D_MARK;
        Bin b6800_FAIL_MIO_DDR    6800    : "b6800_FAIL_MIO_DDR",    b68_FAIL_MIO_DDR;
        Bin b9801_FAIL_TESTCLASS_EXCEPTION_ERROR    9801    : "b9801_FAIL_TESTCLASS_EXCEPTION_ERROR",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9901_fail_FAIL_DPS_ALARM    9901    : "b9901_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ERROR;
    }

    BinGroup DataBins
    {
        LeafBin b90670000_fail_FUN_Instance1_0    90670000    : "b90670000_fail_FUN_Instance1_0",    b6700_FAIL_ARBITRARY_NAME;
        LeafBin b90680000_fail_FUN_Instance1_2    90680000    : "b90680000_fail_FUN_Instance1_2",    b6800_FAIL_MIO_DDR;
        LeafBin b90680001_fail_FUN_Instance1_3    90680001    : "b90680001_fail_FUN_Instance1_3",    b6800_FAIL_MIO_DDR;
        LeafBin b90980100_fail_FUN_Instance1_n1    90980100    : "b90980100_fail_FUN_Instance1_n1",    b9801_FAIL_TESTCLASS_EXCEPTION_ERROR;
        LeafBin b90990100_fail_FUN_Instance1_n2    90990100    : "b90990100_fail_FUN_Instance1_n2",    b9901_fail_FAIL_DPS_ALARM;
    }

}
'''

            self.assertTextEqual(File('FUN.sbdefs').read(), expect)

        finally:
            DMRdefault.bindefdefaults = original_bindefdefaults  # Restore original state

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_repeat_specific_setbin(self):
        bin_limits = [(800, 804)]

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=90080456),
                                    r3=pFail(setbin=90080123),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080456_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90080123_fail_FUN_Instance1_3;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=90080789),
                                    r3=pFail(setbin=90080123),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080789_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90080123_fail_FUN_Instance1_3;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_repeat_negative_bin(self):
        bin_limits = [(800, 804)]

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-8),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-8),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj1)

        # We expect the counters to prevent the same bins from being used
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080000_fail_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080001_fail_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080002_fail_FUN_Instance1_0;
            IncrementCounters FUN::n90080002_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080000_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080003_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080004_fail_Instance1_3;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_repeat_changed_negative_bin(self):
        bin_limits = [(800, 804), (6800, 6804)]

        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-8),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeDMRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-68),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90680000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
        }
        Result 3
        {
            Property PassFail = "Fail";
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_existing_autobinner_dmrclass(self):
        """Test case where user assigns a 4 digit bin manually and we generate the 8 digit bins and those need to be sticky"""
        bindict = {
            "Instance1": {
                "bin": "90440000",
                "rm2": "90440000",
                "rm1": "90440001",
                "r0": "90440002",
                "r2": "90440004"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            binctr.ServerClass8dig.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=90440001), r0=pFail(setbin=-44), r2=pFail(setbin=-44)))
        PyMtpl().main_one(PyObj)

        mtpl = File('out.mtpl').read()

        self.assertIn("SetBin b90440000_fail_FUN_Instance1_n2", mtpl)
        self.assertIn("SetBin b90440001_fail_FUN_Instance1_n1", mtpl)
        self.assertIn("SetBin b90440002_fail_FUN_Instance1_0", mtpl)
        self.assertIn("SetBin b90440004_fail_FUN_Instance1_2", mtpl)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_different_to_existing_autobinner_dmrclass(self):
        """Test case where user assigns a 4 digit bin manually and the bin extracted from 8 digit bin is different to the user assigned bin.
        Expecting new bins to be assigned and matched to new requested bin."""
        bindict = {
            "Instance1": {
                "bin": "90440025",
                "r0": "90440025",
                "r2": "90440026"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeDMRClass('out', 'FUN', binrange=(4415, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(), rm1=pFail(), r0=pFail(setbin=-4415), r2=pFail(setbin=-4415)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90441500_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90441501_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_3dig_bin_different_to_existing_autobinner_dmrclass(self):
        """Test case where user assigns a 3-digit bin manually and the bin extracted from 8-digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "90080010",
                "rm2": "90990800",
                "r0": "90080010",
                "r2": "90080011"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeDMRClass('out', 'FUN', binrange=[(800, 850), (9908, 9908)])
            binctr.ServerClass8dig.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-9908), rm1=pFail(), r0=pFail(setbin=-800), r2=pFail(setbin=-800)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990800_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080010_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080011_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_different_to_existing_autobinner_rm2_rm1_dmrclass(self):
        """Test case where user assigns a 4 digit bin manually and the bin extracted from 8 digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "90080010",
                "rm2": "90990800",
                "r0": "90080010",
                "r2": "90080011"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeDMRClass('out', 'FUN', binrange=(800, 850))
            binctr.ServerClass8dig.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(), rm1=pFail(setbin=-800), r0=pFail(setbin=-800), r2=pFail(setbin=-800)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90080010_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080011_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    def test_getbin2dig(self):
        # test getting the hardbin from 8 digit bin
        self.assertEqual(ServerClass8dig._get_hardbin_match('b90680000'), '68')
        self.assertEqual(ServerClass8dig._get_hardbin_match('b90080001'), '08')
        self.assertEqual(ServerClass8dig._get_hardbin_match('b90909790'), '90')
        self.assertEqual(ServerClass8dig._get_hardbin_match('b90949899'), '94')
        self.assertEqual(ServerClass8dig._get_hardbin_match('b90970000'), '97')  # bin 97
        self.assertEqual(ServerClass8dig._get_hardbin_match('b90980001'), '98')  # bin 98
        self.assertEqual(ServerClass8dig._get_hardbin_match('b90990002'), '99')  # bin 99
        # bins which we don't want to track
        self.assertEqual(ServerClass8dig._get_hardbin_match('b99000001'), None)  # no pass bins

    def test_getbin4dig(self):
        # test getting the softbin from 8 digit bin
        self.assertEqual(ServerClass8dig._get_softbin_match('b90680000'), '6800')
        self.assertEqual(ServerClass8dig._get_softbin_match('b90080100'), '0801')
        self.assertEqual(ServerClass8dig._get_softbin_match('b90909790'), '9097')
        self.assertEqual(ServerClass8dig._get_softbin_match('b90949899'), '9498')
        self.assertEqual(ServerClass8dig._get_softbin_match('b90970000'), '9700')  # bin 97
        self.assertEqual(ServerClass8dig._get_softbin_match('b90980100'), '9801')  # bin 98
        self.assertEqual(ServerClass8dig._get_softbin_match('b90990200'), '9902')  # bin 99
        # bins which we don't want to track
        self.assertEqual(ServerClass8dig._get_softbin_match('b99000001'), None)  # no pass bins

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_negbin(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = (6400, 6401)

        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-66)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b90996600_fail_FAIL_DPS_ALARM_n2", readout)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_posbin(self):
        """Test for defaultrmXbin with 8 digit positive bin value"""
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin=90981234, defaultrm2bin=90995678)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90981234_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b90995678_fail_FAIL_DPS_ALARM_n2", readout)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_defaultrmbins_directset(self):
        """Test for defaultrmXbin with a direct string set and multiple tests"""
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b90981234_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b90995678_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem()),
                VminTC(name="Instance3", _fitem=Fitem()),
            ])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1", readout)
        self.assertIn("SetBin b90995678_fail_FUN_shared_bin_n2", readout)

        expect = '''
CSharpTest VminTC Instance1
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance3
{
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    FlowItem Instance3 Instance3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(readout, expect)

        # with repeat
        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b90981234_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b90995678_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem()),
                VminTC(name="Instance3", _fitem=Fitem()),
            ])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertTextEqual(readout, expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_defaultrmbins_directset_sbdef(self):
        """Test for defaultrmXbin to make sure the bins show up in the sbdef"""
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b90981234_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b90995678_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem()),
                VminTC(name="Instance3", _fitem=Fitem()),
            ])
        PyMtpl().main_one(PyObj)
        readout = File('FUN.sbdefs').read()
        self.assertIn("b90981234_FAIL_MIO_DDR_SHARED_BIN_n1", readout)
        self.assertIn("b90995678_fail_FUN_shared_bin_n2", readout)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup DataBins
    {
        LeafBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1    90981234    : "b90981234_FAIL_MIO_DDR_SHARED_BIN_n1",    b9812_fail_FAIL_SYSTEM_SOFTWARE;
        LeafBin b90995678_fail_FUN_shared_bin_n2    90995678    : "b90995678_fail_FUN_shared_bin_n2",    b9956_fail_FAIL_DPS_ALARM;
    }

}
'''
        self.assertTextEqual(readout, expect)

    @with_(TempDir, chdir=True)
    def test_sbdef_979899(self):
        '''
        Testing that an sbdef which only has hb 97,98,99 still generates
        '''

        bin_limits = [(9801, 9802), (9901, 9902), (9700, 9700)]

        class PyObj1:
            output = InitializeDMRClass('out', 'PTH_THRSOAK', binrange=bin_limits, edcportctrbinrange=bin_limits)

            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(  # implicitly, bin 99 and 98 for -2 and -1 ports
                            r0=pFail(setbin=-97)
                       ))])

        PyMtpl().main_one(PyObj1)

        # We expect the counters to prevent the same bins from being used
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup HardBins
    {
        Bin b97_FAIL_SORT_CHUCK_HANDLER_TEMP    97    : "b97_FAIL_SORT_CHUCK_HANDLER_TEMP",    Fail;
        Bin b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN    98    : "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN",    Fail;
        Bin b99_FAIL_HARDWARE_ERROR    99    : "b99_FAIL_HARDWARE_ERROR",    Fail;
    }

    BinGroup SoftBins
    {
        Bin b9700_FAIL_SORT_CHUCK_HANDLER_TEMP    9700    : "b9700_FAIL_SORT_CHUCK_HANDLER_TEMP",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        Bin b9801_FAIL_TESTCLASS_EXCEPTION_ERROR    9801    : "b9801_FAIL_TESTCLASS_EXCEPTION_ERROR",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9901_fail_FAIL_DPS_ALARM    9901    : "b9901_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ERROR;
    }

    BinGroup DataBins
    {
        LeafBin b90970000_fail_PTH_THRSOAK_Instance1_0    90970000    : "b90970000_fail_PTH_THRSOAK_Instance1_0",    b9700_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b90980100_fail_PTH_THRSOAK_Instance1_n1    90980100    : "b90980100_fail_PTH_THRSOAK_Instance1_n1",    b9801_FAIL_TESTCLASS_EXCEPTION_ERROR;
        LeafBin b90990100_fail_PTH_THRSOAK_Instance1_n2    90990100    : "b90990100_fail_PTH_THRSOAK_Instance1_n2",    b9901_fail_FAIL_DPS_ALARM;
    }

}
'''

        self.assertTextEqual(File('PTH_THRSOAK.sbdefs').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sbdef_cwf_databins_as_leaf(self):
        """
        Test case when databins are just in the softbins category as leafbins
        """

        bin_limits = [(9700, 9700)]

        class PyObj1:
            output = InitializeCWFClass('out', 'PTH_THRSOAK', binrange=bin_limits)

            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(  # implicitly, bin 99 and 98 for -2 and -1 ports
                            r0=pFail(setbin=-97)
                       ))])

        PyMtpl().main_one(PyObj1)

        # We expect the counters to prevent the same bins from being used
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup HardBins
    {
        Bin b97_FAIL_SORT_CHUCK_HANDLER_TEMP    97    : "b97_FAIL_SORT_CHUCK_HANDLER_TEMP",    Fail;
        Bin b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN    98    : "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN",    Fail;
        Bin b99_FAIL_HARDWARE_ERROR    99    : "b99_FAIL_HARDWARE_ERROR",    Fail;
    }

    BinGroup SoftBins
    {
        LeafBin b9700_FAIL_SORT_CHUCK_HANDLER_TEMP    9700    : "b9700_FAIL_SORT_CHUCK_HANDLER_TEMP",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b9898_fail_FAIL_SYSTEM_SOFTWARE    9898    : "b9898_fail_FAIL_SYSTEM_SOFTWARE",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        LeafBin b9999_fail_FAIL_DPS_ALARM    9999    : "b9999_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ERROR;
        LeafBin b90970000_fail_PTH_THRSOAK_Instance1_0    90970000    : "b90970000_fail_PTH_THRSOAK_Instance1_0",    b9700_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b90989801_fail_FAIL_SYSTEM_SOFTWARE    90989801    : "b90989801_fail_FAIL_SYSTEM_SOFTWARE",    b9898_fail_FAIL_SYSTEM_SOFTWARE;
        LeafBin b90999901_fail_FAIL_DPS_ALARM    90999901    : "b90999901_fail_FAIL_DPS_ALARM",    b9999_fail_FAIL_DPS_ALARM;
    }

}
'''

        self.assertTextEqual(File('PTH_THRSOAK.sbdefs').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_two_digit_port_numbers_ServerClass8dig(self):
        # Test 2-digit port numbers (r63, r78, r86, r97, r102) with ServerClass8dig strategy
        # Validates that port numbers are fully extracted, not just last digit

        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450),
                                        edcportctrbinrange=[(4400, 4450)],
                                        defaultrm1bin=-44,
                                        defaultrm2bin=-44)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        r0=pFail(setbin=AUTO),
                                        r63=pFail(setbin=AUTO),
                                        r78=pFail(setbin=AUTO),
                                        r86=pFail(setbin=AUTO),
                                        r97=pPass(),
                                        r102=pFail(setbin=AUTO)))

            subflow = Flow('SubFlow1', test1)

        PyMtpl().main_one(PyObj)

        # Verify bin and counter strings have full port numbers (63, 78, 86, 97, 102), not just last digit
        mtpl_content = File('out.mtpl').read()

        # Check that counter/bin strings end with full port numbers
        self.assertIn('_Instance1_63', mtpl_content, "Counter/Bin should end with _63, not _3")
        self.assertIn('_Instance1_78', mtpl_content, "Counter/Bin should end with _78, not _8")
        self.assertIn('_Instance1_86', mtpl_content, "Counter/Bin should end with _86, not _6")
        self.assertIn('_Instance1_102', mtpl_content, "Counter/Bin should end with _102, not _2")

        # Verify setbin strings for 2-digit ports
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_63', "SetBin should end with _63")
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_78', "SetBin should end with _78")
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_86', "SetBin should end with _86")
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_102', "SetBin should end with _102")

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90994400_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n90994400_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90984400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n90984400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n90440000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 63
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1_63;
            IncrementCounters FUN::n90440001_fail_Instance1_63;
        }
        Result 78
        {
            Property PassFail = "Fail";
            SetBin b90440002_fail_FUN_Instance1_78;
            IncrementCounters FUN::n90440002_fail_Instance1_78;
        }
        Result 86
        {
            Property PassFail = "Fail";
            SetBin b90440003_fail_FUN_Instance1_86;
            IncrementCounters FUN::n90440003_fail_Instance1_86;
        }
        Result 97
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 102
        {
            Property PassFail = "Fail";
            SetBin b90440004_fail_FUN_Instance1_102;
            IncrementCounters FUN::n90440004_fail_Instance1_102;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_update_nonmtt_bin_already_shared_bin_not_doubled(self):
        # Line 1646: condition evaluates False when registry entry already ends with _SHARED_BIN
        # The entry should not be appended with another _SHARED_BIN suffix
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44)))])
        PyMtpl().main_one(PyObj)
        digit8 = '90440000'
        # Simulate the entry already having been tagged as a shared bin
        ServerClass8dig.bin_registry[digit8] = ServerClass8dig.bin_registry[digit8] + '_SHARED_BIN'
        pre_update_value = ServerClass8dig.bin_registry[digit8]
        # Calling with another test name would normally set _SHARED_BIN, but line 1646 is False since already tagged
        ServerClass8dig._update_nonmtt_bin(int(digit8), 'Instance2', 'r0')
        self.assertEqual(ServerClass8dig.bin_registry[digit8], pre_update_value)

    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_non_mtt_autosetbinstring_setbin_positive_falls_through(self):
        # Line 1709: elif setbin == -1 evaluates False when setbin >= 0 with name in autobindict_internal
        # Neither -HB nor AUTO branch matches, so code falls through to default bin allocation
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44)))])
        PyMtpl().main_one(PyObj)
        # Instance1/r0 is in autobindict_internal; setbin=0 is not -1 and not < -1 so line 1709 is False
        with self.assertRaisesRegex(ErrorUser, 'Please check the definition'):
            ServerClass8dig._get_non_mtt_autosetbinstring(0, 'Instance1', [False], 'r0', 1)

    def test_get_new_bin_8dig_non_negative_origbin_skips_binrange_confirm(self):
        # Line 1769: if origbin < 0 evaluates False - bin_range validation confirm is not triggered
        # A negative origbin with empty bin_range raises "No bin_range"; origbin=0 bypasses that confirm
        ServerClass8dig.bin_range.clear()  # ensure empty bin_range for this test
        with self.assertRaisesRegex(ErrorUser, 'No bin_range specified'):
            ServerClass8dig.get_new_bin_8dig(-44, 1)
        # origbin=0 (line 1769 False): skips the confirm and reaches get_available_8dig_bin instead
        with self.assertRaisesRegex(ErrorUser, 'Please check the definition'):
            ServerClass8dig.get_new_bin_8dig(0, 1)

    @patch('pymtpl.binctr.CtrServerClass8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.DMRdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_available_8dig_bin_positive_origbin_not_matched(self):
        # Line 1793: elif origbin[0] == '-' and bin_str_len in [4, 5] evaluates False
        # Positive origbin has no '-' prefix so neither the -HB nor -HBSB elif is True, usableBinranges stays []
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44)))])
        PyMtpl().main_one(PyObj)
        # origbin[0]='4' so line 1793 elif is False; usableBinranges=[] triggers ErrorUser
        with self.assertRaisesRegex(ErrorUser, 'Please check the definition'):
            ServerClass8dig.get_available_8dig_bin('44000000', 1)


class TestSort8dig(TestCase):

    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_newbin_Sort8dig(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=4400))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=4400)))])

        PyMtpl().main_one(PyObj)
        self.assertEqual(Sort8dig.get_new_bin(-1, 100), 4401)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_kill_to_edc_setbin(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440000_fail_FUN_Instance1;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_kill_to_edc_remove_setbin(self):
        # Move test from kill with setbin to edc with no setbin

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail()))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
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

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_Sort8dig(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000002_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44190162_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_passport_Sort8dig(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, defaultrm2bin=-44, defaultrm1bin=-44, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r1=pPass(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_manualbin_ignore_ports_Sort8dig(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=99440000), rm1=pFail(setbin=98440000), r5=pFail(setbin=44190000)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440000_fail_FUN_Instance1_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44190000_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ignore_ports_only_Sort8dig(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO, ret=-2), rm1=pFail(setbin=AUTO, ret=-1), r1=pPass(), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44190162_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_multirange_Sort8dig(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000002_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44190162_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_two_level_multirange_Sort8dig(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=[(4400, 4401), (4410, 4415)], nonmttbinstrategy=Sort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Test VminTC Instance3
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Test VminTC Instance4
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_2;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44100000_fail_FUN_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    DUTFlowItem Instance3 Instance3
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44110000_fail_FUN_Instance3_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance4;
        }
    }

    DUTFlowItem Instance4 Instance4
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010000_fail_FUN_Instance4_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_two_level_multirange_error_Sort8dig(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=[(4400, 4401)], nonmttbinstrategy=Sort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_nonmtt_setbinstring_Sort8dig(self):
        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400), r3=pFail(setbin=44000000)))

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000002_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000000_fail_FUN_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    def test_get_default_bins_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "Invalid bin_type. Expected 'software', 'clamp' or 'reset'."):
            Sort8dig.get_default_bins(-1, 100, "invalid", "tname", "r2")

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_shared_bin_Sort8dig(self):
        class PyObj:
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400), r3=pFail(setbin=44000000)))

        PyMtpl().main_one(PyObj)
        Sort8dig._update_nonmtt_bin(44000000, "Test2", "r0")
        self.assertEqual(Sort8dig.bin_registry["44000000"], "SoftBins.b44000000_fail_FUN_Instance1_3_SHARED_BIN")

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_existing_autobinner(self):
        bindict = {
            "Instance1": {
                "bin": "4415",
                "rm2": "99440000",
                "r0": "44150000",
                "r2": "44150001"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44150000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44150001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_repeat_existing_autobinner(self):
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000025",
                "r2": "44000026"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000025_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000026_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_change_repeat_runs(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4401), r2=pFail(setbin=4401)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44010001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_change_repeat_runs(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)], nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-44)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)], nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-45), r2=pFail(setbin=-45)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99990162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98980162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b45000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b45000001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

#     @with_(TempDir, chdir=True)
#     @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
#     def test_auto_bin_change_within_ports_repeat_runs(self):

#         class PyObj:
#             # Start of the "python mtpl code" ====================
#             output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)], nonmttbinstrategy=Sort8dig)
#             test1 = VminTC(name="Instance1",
#                            _comment="VminTC comment",
#                            EndVoltageLimits="0.9")
#             subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-45)))
#         PyMtpl().main_one(PyObj)

#         class PyObj1:
#             # Start of the "python mtpl code" ====================
#             output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)], nonmttbinstrategy=Sort8dig)
#             test1 = VminTC(name="Instance1",
#                            _comment="VminTC comment",
#                            EndVoltageLimits="0.9")
#             subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-45), r2=pFail(setbin=-44)))

#         PyMtpl().main_one(PyObj1)
#         expect = '''
# Version 1.0;

# ProgramStyle = Modular;

# TestPlan FUN;

# Import VminTC.xml;

# # VminTC comment
# Test VminTC Instance1
# {
#     EndVoltageLimits = "0.9";
#     FailCaptureCount = 999;
# }

# DUTFlow SubFlow1
# {
#     DUTFlowItem Instance1 Instance1
#     {
#         Result -2
#         {
#             Property PassFail = "Fail";
#             SetBin SoftBins.b99990162_fail_FUN_Instance1_n2;
#             Return -2;
#         }
#         Result -1
#         {
#             Property PassFail = "Fail";
#             SetBin SoftBins.b98980162_fail_FUN_Instance1_n1;
#             Return -1;
#         }
#         Result 0
#         {
#             Property PassFail = "Fail";
#             SetBin SoftBins.b45010000_fail_FUN_Instance1_0;
#         }
#         Result 1
#         {
#             Property PassFail = "Pass";
#             Return 1;
#         }
#         Result 2
#         {
#             Property PassFail = "Fail";
#             SetBin SoftBins.b44010000_fail_FUN_Instance1_2;
#         }
#     }

# }

# '''
#         self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_repeat(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))

        with CaptureStdoutLog() as p:
            PyMtpl().main_one(PyObj1)
        self.assertIn('NO UPDATE: No changes to out.mtpl', p.getvalue())

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_existing_autobinner(self):
        """Test case where user assigns a 4 digit bin manually and we generate the 8 digit bins and those need to be sticky"""
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000025",
                "r2": "44000026"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000025_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000026_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_different_to_existing_autobinner(self):
        """Test case where user assigns a 4 digit bin manually and the bin extracted from 8 digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000025",
                "r2": "44000026"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4415), r2=pFail(setbin=4415)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44150000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44150001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_3dig_bin_different_to_existing_autobinner(self):
        """Test case where user assigns a 3-digit bin manually and the bin extracted from 8-digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "800",
                "rm2": "99080000",
                "r0": "8000010",
                "r2": "8000011"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 850), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=800), r2=pFail(setbin=800)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99080000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98085499_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b8000010_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b8000011_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_different_to_existing_autobinner_rm2_rm1(self):
        """Test case where user assigns a 4 digit bin manually and the bin extracted from 8 digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "800",
                "rm2": "99080000",
                "r0": "8000010",
                "r2": "8000011"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(800, 850), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=9908), rm1=pFail(setbin=800), r0=pFail(setbin=800), r2=pFail(setbin=800)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99080000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b8005499_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b8000010_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b8000011_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_check_autobindict_for_default_ports(self):
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440162",
                "rm1": "98440162",
                "r0": "44000000",
                "r2": "44000001"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        autobindict_file = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        autobin_file_content = File(autobindict_file).read()
        autobin_dict = json.loads(autobin_file_content)
        self.assertDictEqual(autobin_dict, bindict)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_check_autobindict_when_only_default_ports(self):
        bindict = {
            "Instance1": {
                "bin": "NA",
                "rm2": "99440162",
                "rm1": "98440162"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), defaultrm1bin=-44, defaultrm2bin=-44)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
        PyMtpl().main_one(PyObj)
        autobindict_file = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        autobin_file_content = File(autobindict_file).read()
        autobin_dict = json.loads(autobin_file_content)
        self.assertDictEqual(autobin_dict, bindict)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_load_autobin_key_error_autobinner(self):
        bindict = {
            "Instance1": {
                "rm2": "99440030",
                "r0": "44150000",
                "r2": "44150031"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig, tosversion="tos3")
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440030_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44150000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_and_manual_then_repeat_auto(self):
        # Unit test for bug found in production where a test was moved from manual bin to AUTO and the 8-digit bins were being repeated.
        # First run: one test with autobin, one with manual bin
        # The bin range is restricted to one bin to not allow for new 4-dig bins.
        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, edc=True, r0=pFail(setbin=90450100))
                           )
        PyMtpl().main_one(PyObj)

        # Second run: move both to AUTO
        class PyObj2:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, edc=True, r0=pFail(setbin=AUTO))
                           )
        PyMtpl().main_one(PyObj2)
        expect2 = '''
CSharpTest VminTC AutoTest
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC ManualTest
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem AutoTest AutoTest
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_AutoTest_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_AutoTest_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_AutoTest_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo ManualTest;
        }
    }

    FlowItem ManualTest ManualTest @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99900162_fail_FUN_ManualTest_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98900162_fail_FUN_ManualTest_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000001_fail_FUN_ManualTest_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect2)


class TestNVLClassHBSBXXXX(TestCase):
    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_newbin_NVLClassHBSBXXXX(self):

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440000, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=4400))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=4400)))])

        PyMtpl().main_one(PyObj)
        self.assertEqual(NVLClassHBSBXXXX.get_new_bin(-1, 100), 4401)

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_commonport_bin_NVLClassHBSBXXXX(self):

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=4400))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=4400)))])

        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(9944, "rm2", "Dummy"), "99440000")
        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(9844, "rm1", "Dummy"), "98440025")
        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(9744, "r4", "Dummy"), "97440000")
        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(4419, "r5", "Dummy"), "44190000")

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_kill_to_edc_setbin(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_Instance1_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000001_fail_FUN_Instance1_2;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_kill_to_edc_remove_setbin(self):
        # Move test from kill with setbin to edc with no setbin

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail()))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
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

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_3dig_range_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 850), defaultrm2bin=(99080000, 99080100), defaultrm1bin=(98080025, 98080100), defaultresetbin=(8190000, 8190100), defaultthermalbin=(97080000, 97080100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97080000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8190000_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_passport_NVLClassHBSBXXXX(self):
        """
        Test case where user assigns AUTO to a pass port.
        Expect no setbin on the passing port
        """

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r1=pPass(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_manualbin_ignore_ports_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=99440000), rm1=pFail(setbin=98440000), r5=pFail(setbin=44190025)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440000_fail_FUN_Instance1_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190025_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ignore_ports_only_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO, ret=-2), rm1=pFail(setbin=AUTO, ret=-1), r1=pPass(), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_multirange_sameHB_NVLClassHBSBXXXX(self):
        """
        Multi-range unit test in same HB range
        """
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)], defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_multirange_commonbins_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)],
                                                defaultrm2bin=[(99440000, 99440100), (99440500, 99440600)],
                                                defaultrm1bin=[(98440025, 98440100), (98440500, 98440600)],
                                                defaultresetbin=[(44190000, 44190100), (44190500, 44190600)],
                                                defaultthermalbin=[(97440000, 97440100), (97440500, 97440600)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_two_level_multirange_NVLClassHBSBXXXX(self):

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4401), (4410, 4415)],
                                                defaultrm2bin=[(99440000, 99440100), (99440500, 99440600)],
                                                defaultrm1bin=[(98440025, 98440100), (98440500, 98440600)],
                                                defaultresetbin=[(44190000, 44190100), (44190500, 44190600)],
                                                defaultthermalbin=[(97440000, 97440100), (97440500, 97440600)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44),
                                    r4=pFail(setbin=-44),
                                    r5=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance3
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance4
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440001_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440026_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44100000_fail_FUN_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    FlowItem Instance3 Instance3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440002_fail_FUN_Instance3_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440027_fail_FUN_Instance3_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44110000_fail_FUN_Instance3_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance4;
        }
    }

    FlowItem Instance4 Instance4
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440003_fail_FUN_Instance4_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440028_fail_FUN_Instance4_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance4_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_two_level_multirange_error_NVLClassHBSBXXXX(self):

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4401)],
                                                defaultrm2bin=[(99440000, 99440100), (99440500, 99440600)],
                                                defaultrm1bin=[(98440025, 98440100), (98440500, 98440600)],
                                                defaultresetbin=[(44190000, 44190100), (44190500, 44190600)],
                                                defaultthermalbin=[(97440000, 97440100), (97440500, 97440600)])

            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r0=pFail(setbin=-44),
                                    r2=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance3", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-4410))),
                VminTC(name="Instance4", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=-44))),
            ])

        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_nonmtt_setbinstring_NVLClassHBSBXXXX(self):
        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))

            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400), r3=pFail(setbin=44000000)))

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000002_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    def test_get_default_bins_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "Invalid bin_type. Expected 'software', 'clamp'"):
            NVLClassHBSBXXXX.get_default_bins(-1, 100, "invalid", "tname", "r2")

    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_shared_bin_NVLClassHBSBXXXX(self):
        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400), r3=pFail(setbin=44000000)))

        PyMtpl().main_one(PyObj)
        NVLClassHBSBXXXX._update_nonmtt_bin(44000000, "Test2", "r0")
        self.assertEqual(NVLClassHBSBXXXX.bin_registry["44000000"], "b44000000_fail_FUN_Instance1_3_SHARED_BIN")

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_existing_autobinner(self):
        bindict = {
            "Instance1": {
                "bin": "4415",
                "rm2": "99449000",
                "r0": "44150000",
                "r2": "44150001"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99449000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44150000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44150001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_simple_manual_4dig_bins(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44192000, 44193100),
                                                defaultthermalbin=(97442000, 97443100))

            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=4400),
                                             r2=pFail(setbin=4400),
                                             r3=pFail(setbin=4400),
                                             r4=pFail(setbin=9744),
                                             r5=pFail(setbin=4419)))
        PyMtpl().main_one(PyObj)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44000000_fail_Instance1_0,
    n44000001_fail_Instance1_2,
    n44000002_fail_Instance1_3,
    n44192000_fail_Instance1_5,
    n97442000_fail_Instance1_4
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44000002_fail_FUN_Instance1_3;
            IncrementCounters FUN::n44000002_fail_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97442000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97442000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44192000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44192000_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_simple_manual_3dig_bins(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(800, 850),
                                                defaultrm2bin=(99080000, 99080100),
                                                defaultrm1bin=(98080025, 98080100),
                                                defaultresetbin=(8192000, 8193100),
                                                defaultthermalbin=(97082000, 97083100))

            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=800),
                                             r2=pFail(setbin=800),
                                             r3=pFail(setbin=800),
                                             r4=pFail(setbin=9708),
                                             r5=pFail(setbin=819)))
        PyMtpl().main_one(PyObj)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8000000_fail_Instance1_0,
    n8000001_fail_Instance1_2,
    n8000002_fail_Instance1_3,
    n8192000_fail_Instance1_5,
    n97082000_fail_Instance1_4
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n8000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8000001_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b8000002_fail_FUN_Instance1_3;
            IncrementCounters FUN::n8000002_fail_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97082000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97082000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8192000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n8192000_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_repeat_existing_autobinner(self):
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000025",
                "r2": "44000026"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))

            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000025_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000026_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_change_repeat_runs(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4401), r2=pFail(setbin=4401)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44010001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_3dig_change_repeat_runs(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(800, 850),
                                                defaultrm2bin=(99080000, 99080100),
                                                defaultrm1bin=(98080025, 98080100),
                                                defaultresetbin=(8190000, 8190100),
                                                defaultthermalbin=(97080000, 97080100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=800), r2=pFail(setbin=800)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(700, 750),
                                                defaultrm2bin=(99070000, 99070100),
                                                defaultrm1bin=(98070025, 98070100),
                                                defaultresetbin=(7190000, 7190100),
                                                defaultthermalbin=(97070000, 97070100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=700), r2=pFail(setbin=700)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99070000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98070025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b7000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b7000001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_3dig_no_change_repeat_runs(self):
        """
        Test case where -
        setbin = 700
        Run pymtpl
        setbin = 700
        Expect output to be 7000000
        """

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(800, 850),
                                                defaultrm2bin=(99080000, 99080100),
                                                defaultrm1bin=(98080025, 98080100),
                                                defaultresetbin=(8190000, 8190100),
                                                defaultthermalbin=(97080000, 97080100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=800), r2=pFail(setbin=800)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(800, 850),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=800), r2=pFail(setbin=800)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8000001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_change_repeat_runs(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=[(4400, 4450), (4500, 4550)],
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-44)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=[(4400, 4450), (4500, 4550)],
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-45), r2=pFail(setbin=-45)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_repeat(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))

        with CaptureStdoutLog() as p:
            PyMtpl().main_one(PyObj1)
        self.assertIn('NO UPDATE: No changes to out.mtpl', p.getvalue())

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_existing_autobinner(self):
        """Test case where user assigns a 4 digit bin manually and we generate the 8 digit bins and those need to be sticky"""
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99449000",
                "r0": "44000025",
                "r2": "44000026"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99449000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000025_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000026_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_default_ports_existing_autobinner(self):
        """Test case where user assigns a 4 digit bin manually and we generate the 8 digit bins and those need to be sticky"""
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99449000",
                "rm1": "98449000",
                "r4": "97440026"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r4=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99449000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98449000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440026_fail_FUN_Instance1_4;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_different_to_existing_autobinner(self):
        """Test case where user assigns a 4 digit bin manually and the bin extracted from 8 digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000025",
                "r2": "44000026"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4415), r2=pFail(setbin=4415)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44150000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44150001_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_3dig_bin_different_to_existing_autobinner(self):
        """Test case where user assigns a 3-digit bin manually and the bin extracted from 8-digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "700",
                "rm2": "99070000",
                "r0": "7000010",
                "r2": "7000011"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(800, 850),
                                                defaultrm2bin=(99080000, 99080100),
                                                defaultrm1bin=(98080025, 98080100),
                                                defaultresetbin=(8190000, 8190100),
                                                defaultthermalbin=(97080000, 97080100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=800), r2=pFail(setbin=800), r4=pFail(setbin=-8), r5=pFail(setbin=-8)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97080000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8190000_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_manual_bin_different_to_existing_autobinner_rm2_rm1(self):
        """Test case where user assigns a 4 digit bin manually and the bin extracted from 8 digit bin is different to the user assigned bin"""
        bindict = {
            "Instance1": {
                "bin": "800",
                "rm2": "99080000",
                "r0": "8000010",
                "r2": "8000011"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(800, 850),
                                                defaultrm2bin=(99080000, 99080100),
                                                defaultrm1bin=(98080025, 98080100),
                                                defaultresetbin=(8190000, 8190100),
                                                defaultthermalbin=(97080000, 97080100))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=9908), rm1=pFail(setbin=9808), r0=pFail(setbin=800), r2=pFail(setbin=800), r4=pFail(setbin=800), r5=pFail(setbin=800)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8000010_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8000011_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8000001_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_check_autobindict_for_default_ports(self):
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "rm1": "98440025",
                "r0": "44000000",
                "r2": "44000001"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))

            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)

        self.assertDictEqual(binctr.NVLClassHBSBXXXX.autobindict, bindict)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_check_autobindict_when_only_default_ports(self):
        bindict = {
            "Instance1": {
                "bin": "NA",
                "rm2": "99440000",
                "rm1": "98440025"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
        PyMtpl().main_one(PyObj)

        self.assertDictEqual(binctr.NVLClassHBSBXXXX.autobindict, bindict)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_check_autobindict_3dig_bins_when_only_default_ports(self):
        bindict = {
            "Instance1": {
                "bin": "NA",
                "rm2": "99080000",
                "rm1": "98080025"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(800, 850),
                                                defaultrm2bin=(99080000, 99080100),
                                                defaultrm1bin=(98080025, 98080100),
                                                defaultresetbin=(8190000, 8190100),
                                                defaultthermalbin=(97080000, 97080100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
        PyMtpl().main_one(PyObj)

        self.assertDictEqual(binctr.NVLClassHBSBXXXX.autobindict, bindict)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_load_autobin_key_error_autobinner(self):
        bindict = {
            "Instance1": {
                "rm2": "99440030",
                "r0": "44150000",
                "r2": "44150031"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440030_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44150000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseCounter.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_class8dig_autobin_and_manual_then_repeat_auto(self):
        # Unit test for bug found in production where a test was moved from manual bin to AUTO and the 8-digit bins were being repeated.
        # First run: one test with autobin, one with manual bin
        # The bin range is restricted to one bin to not allow for new 4-dig bins.
        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, edc=True, r0=pFail(setbin=90450100))
                           )
        PyMtpl().main_one(PyObj)

        # Second run: move both to AUTO
        class PyObj2:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4400))
            test1 = VminTC(name="AutoTest", EndVoltageLimits="0.9")
            test2 = VminTC(name="ManualTest", EndVoltageLimits="0.8")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, edc=True, r0=pFail(setbin=AUTO))
                           )
        PyMtpl().main_one(PyObj2)
        expect2 = '''
CSharpTest VminTC AutoTest
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC ManualTest
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem AutoTest AutoTest
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_AutoTest_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_AutoTest_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_AutoTest_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo ManualTest;
        }
    }

    FlowItem ManualTest ManualTest @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99900162_fail_FUN_ManualTest_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98900162_fail_FUN_ManualTest_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000001_fail_FUN_ManualTest_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect2)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_commonbin_defaultrange_NVLClassHBSBXXXX(self):

        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=-44, defaultrm1bin=-44, defaultresetbin=-44, defaultthermalbin=-44)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")

                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99441000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441000_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97441000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97441000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44191000_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_commonbin_defaultrange_list_NVLClassHBSBXXXX(self):

        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 1001), (1110, 2110)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=-44, defaultrm1bin=-44, defaultresetbin=-44, defaultthermalbin=-44)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                test2 = VminTC(name="Instance2",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                test3 = VminTC(name="Instance3",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)), Fitem('SAME', test2, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)), Fitem('SAME', test3, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))

                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance3
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99441000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441000_fail_FUN_Instance1_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97441000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97441000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44191000_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99441001_fail_FUN_Instance2_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441001_fail_FUN_Instance2_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97441001_fail_FUN_Instance2_4;
            IncrementCounters FUN::n97441001_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191001_fail_FUN_Instance2_5;
            IncrementCounters FUN::n44191001_fail_Instance2_5;
        }
    }

    FlowItem Instance3 Instance3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99441110_fail_FUN_Instance3_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441110_fail_FUN_Instance3_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97441110_fail_FUN_Instance3_4;
            IncrementCounters FUN::n97441110_fail_Instance3_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191110_fail_FUN_Instance3_5;
            IncrementCounters FUN::n44191110_fail_Instance3_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_commonbin_nodefaults_in_Initialize_defaultrange_NVLClassHBSBXXXX(self):
        """
        No default bins defined in Initialize
        """

        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450))
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")

                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99441000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441000_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97441000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97441000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44191000_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_SBDef_check_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b4400    4400    : "b4400",    b44_FAIL_SBFT;
        Bin b4419    4419    : "b4419",    b44_FAIL_SBFT;
        Bin b9744    9744    : "b9744",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        Bin b9844    9844    : "b9844",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9944    9944    : "b9944",    b99_FAIL_HARDWARE_ALARM;
    }

    BinGroup DataBins
    {
        LeafBin b44000000_fail_FUN_Instance1_0    44000000    : "b44000000_fail_FUN_Instance1_0",    b4400;
        LeafBin b44000001_fail_FUN_Instance1_2    44000001    : "b44000001_fail_FUN_Instance1_2",    b4400;
        LeafBin b44190000_fail_FUN_Instance1_5    44190000    : "b44190000_fail_FUN_Instance1_5",    b4419;
        LeafBin b97440000_fail_FUN_Instance1_4    97440000    : "b97440000_fail_FUN_Instance1_4",    b9744;
        LeafBin b98440025_fail_FUN_Instance1_n1    98440025    : "b98440025_fail_FUN_Instance1_n1",    b9844;
        LeafBin b99440000_fail_FUN_Instance1_n2    99440000    : "b99440000_fail_FUN_Instance1_n2",    b9944;
    }

}
'''
        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_SBDef_check_3dig_bins_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 850), defaultrm2bin=(99080000, 99080001), defaultrm1bin=(98080000, 98080001), defaultresetbin=(8190000, 8190100), defaultthermalbin=(97080000, 97080100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b800    800    : "b800",    b8_FAIL_VCCCONTINUITY;
        Bin b819    819    : "b819",    b8_FAIL_VCCCONTINUITY;
        Bin b9708    9708    : "b9708",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        Bin b9808    9808    : "b9808",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9908    9908    : "b9908",    b99_FAIL_HARDWARE_ALARM;
    }

    BinGroup DataBins
    {
        LeafBin b8000000_fail_FUN_Instance1_0     8000000    : "b8000000_fail_FUN_Instance1_0",    b800;
        LeafBin b8000001_fail_FUN_Instance1_2     8000001    : "b8000001_fail_FUN_Instance1_2",    b800;
        LeafBin b8190000_fail_FUN_Instance1_5     8190000    : "b8190000_fail_FUN_Instance1_5",    b819;
        LeafBin b97080000_fail_FUN_Instance1_4    97080000    : "b97080000_fail_FUN_Instance1_4",    b9708;
        LeafBin b98080000_fail_FUN_Instance1_n1    98080000    : "b98080000_fail_FUN_Instance1_n1",    b9808;
        LeafBin b99080000_fail_FUN_Instance1_n2    99080000    : "b99080000_fail_FUN_Instance1_n2",    b9908;
    }

}
'''
        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_multirange_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)],
                                                defaultrm2bin=[(99440000, 99440100), (99450000, 99450100)],
                                                defaultrm1bin=[(98440025, 98440100), (98450025, 98450100)],
                                                defaultresetbin=[(44190000, 44190100), (45190000, 45190100)],
                                                defaultthermalbin=[(97440000, 97440100), (97452000, 97452100)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1,
                                 rm2=pFail(setbin=-44),
                                 rm1=pFail(setbin=-44),
                                 r0=pFail(setbin=-44),
                                 r2=pFail(setbin=-44),
                                 r4=pFail(setbin=-44),
                                 r5=pFail(setbin=-44)),
                           Fitem('SAME', test2,
                                 rm2=pFail(setbin=-45),
                                 rm1=pFail(setbin=-45),
                                 r0=pFail(setbin=-45),
                                 r2=pFail(setbin=-45),
                                 r4=pFail(setbin=-45),
                                 r5=pFail(setbin=-45)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97440000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44190000_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99450000_fail_FUN_Instance2_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98450025_fail_FUN_Instance2_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n45000000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance2_2;
            IncrementCounters FUN::n45000001_fail_Instance2_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97452000_fail_FUN_Instance2_4;
            IncrementCounters FUN::n97452000_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b45190000_fail_FUN_Instance2_5;
            IncrementCounters FUN::n45190000_fail_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_multirange_no_match_for_defaultport_NVLClassHBSBXXXX(self):
        """
        Exercise the case where you do not find a usableBinrange for default ports
        Then we error out
        Below case isntance 2 uses -46 but there is no bin range matching that in the defaultbins
        """
        with self.assertRaisesRegex(ErrorUser, "No HB match found for"):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)],
                                                    defaultrm2bin=[(99440000, 99440100), (99450000, 99450100)],
                                                    defaultrm1bin=[(98440025, 98440100), (98450025, 98450100)],
                                                    defaultresetbin=[(44190000, 44190100), (45190000, 45190100)],
                                                    defaultthermalbin=[(97440000, 97440100), (97452000, 97452100)])
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                test2 = VminTC(name="Instance2",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1',
                               Fitem('SAME', test1,
                                     rm2=pFail(setbin=-44),
                                     rm1=pFail(setbin=-44),
                                     r0=pFail(setbin=-44),
                                     r2=pFail(setbin=-44),
                                     r4=pFail(setbin=-44),
                                     r5=pFail(setbin=-44)),
                               Fitem('SAME', test2,
                                     rm2=pFail(setbin=-46),
                                     rm1=pFail(setbin=-46),
                                     r4=pFail(setbin=-46),
                                     r5=pFail(setbin=-46)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_thermalmeasurement_class_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100))
            test1 = PrimeThermalSingleMeasurementTestMethod(name="Instance1",
                                                            _comment="VminTC comment",
                                                            PinNames="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest PrimeThermalSingleMeasurementTestMethod Instance1
{
    # VminTC comment
    PinNames = "0.9";
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b44000002_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44000003_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_multirange_no_match_for_defaultport_thermalmeasurement_class_NVLClassHBSBXXXX(self):
        """
        Non VminTC test case unit test
        Exercise the case where you do not find a usableBinrange for default ports
        Then we error out
        Below case isntance 2 uses -46 but there is no bin range matching that in the defaultbins
        """
        with self.assertRaisesRegex(ErrorUser, "No HB match found for"):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4450), (4500, 4550)],
                                                    defaultrm2bin=[(99440000, 99440100), (99450000, 99450100)],
                                                    defaultrm1bin=[(98440025, 98440100), (98450025, 98450100)],
                                                    defaultresetbin=[(44190000, 44190100), (45190000, 45190100)],
                                                    defaultthermalbin=[(97440000, 97440100), (97452000, 97452100)])
                test1 = PrimeThermalSingleMeasurementTestMethod(name="Instance1",
                                                                _comment="VminTC comment",
                                                                PinNames="0.9")
                test2 = PrimeThermalSingleMeasurementTestMethod(name="Instance2",
                                                                _comment="VminTC comment",
                                                                PinNames="0.9")
                subflow = Flow('SubFlow1',
                               Fitem('SAME', test1,
                                     rm2=pFail(setbin=-44),
                                     rm1=pFail(setbin=-44),
                                     r0=pFail(setbin=-44),
                                     r2=pFail(setbin=-44),
                                     r4=pFail(setbin=-44),
                                     r5=pFail(setbin=-44)),
                               Fitem('SAME', test2,
                                     rm2=pFail(setbin=-46),
                                     rm1=pFail(setbin=-46)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_LTTC_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(94445000, 94446000), (94974400, 94974450)], defaultrm2bin=(99940000, 99940100), defaultrm1bin=(98940025, 98940100), defaultresetbin=(94194400, 94194450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-94), r2=pFail(setbin=-94), r4=pFail(setbin=9497), r5=pFail(setbin=-94)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99940000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98940025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b94445000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b94445001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b94974400_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b94194400_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_singlerange_LTTC_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(94445000, 94446000), defaultrm2bin=(99940000, 99940100), defaultrm1bin=(98940025, 98940100), defaultresetbin=(94194400, 94194450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99940000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98940025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b94445000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b94445001_fail_FUN_Instance1_2;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b94194400_fail_FUN_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_8dig_autobin_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4500, 4510), (44004000, 44005000)], defaultrm2bin=[(99442000, 99443000), (99454000, 99456000)], defaultrm1bin=[(98442000, 98443000), (98454000, 98456000)], defaultresetbin=[(44192000, 44193000), (45194000, 45195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)),
                           Fitem('SAME', test2, r0=pFail(setbin=-45), r2=pFail(setbin=-45), r3=pFail(ret=0), r4=pFail(setbin=-45), r5=pFail(setbin=-45)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99442000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98442000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44004000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44004000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44004001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44004001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97442000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97442000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44192000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44192000_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99454000_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98454000_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n45000000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance2_2;
            IncrementCounters FUN::n45000001_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97454000_fail_FUN_Instance2_4;
            IncrementCounters FUN::n97454000_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b45194000_fail_FUN_Instance2_5;
            IncrementCounters FUN::n45194000_fail_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_3dig_auto_bin_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(810, 810), (9104000, 9105000)], defaultrm2bin=[(99082000, 99083000), (99094000, 99096000)], defaultrm1bin=[(98082000, 98083000), (98094000, 98096000)], defaultresetbin=[(8192000, 8193000), (9194000, 9195000)], defaultthermalbin=[(97082000, 97083000), (97094000, 97096000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-8), r2=pFail(setbin=-8), r4=pFail(setbin=-8), r5=pFail(setbin=-8)),
                           Fitem('SAME', test2, r0=pFail(setbin=-9), r2=pFail(setbin=-9), r3=pFail(ret=0), r4=pFail(setbin=-9), r5=pFail(setbin=-9)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99082000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98082000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8100000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n8100000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8100001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8100001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97082000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97082000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8192000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n8192000_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99094000_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98094000_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b9104000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n9104000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b9104001_fail_FUN_Instance2_2;
            IncrementCounters FUN::n9104001_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97094000_fail_FUN_Instance2_4;
            IncrementCounters FUN::n97094000_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b9194000_fail_FUN_Instance2_5;
            IncrementCounters FUN::n9194000_fail_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_4dig_manual_bin_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4500, 4510), (44004000, 44005000)], defaultrm2bin=[(99442000, 99443000), (99454000, 99456000)], defaultrm1bin=[(98442000, 98443000), (98454000, 98456000)], defaultresetbin=[(44192000, 44193000), (45194000, 45195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400), r4=pFail(setbin=4400), r5=pFail(setbin=4400)),
                           Fitem('SAME', test2, r0=pFail(setbin=4500), r2=pFail(setbin=4500), r3=pFail(ret=0), r4=pFail(setbin=4500), r5=pFail(setbin=4500)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99442000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98442000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44004000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44004000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44004001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44004001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b44004002_fail_FUN_Instance1_4;
            IncrementCounters FUN::n44004002_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44004003_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44004003_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99454000_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98454000_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n45000000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance2_2;
            IncrementCounters FUN::n45000001_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b45000002_fail_FUN_Instance2_4;
            IncrementCounters FUN::n45000002_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b45000003_fail_FUN_Instance2_5;
            IncrementCounters FUN::n45000003_fail_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_3dig_manual_bin_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(810, 810), (9104000, 9105000)], defaultrm2bin=[(99082000, 99083000), (99094000, 99096000)], defaultrm1bin=[(98082000, 98083000), (98094000, 98096000)], defaultresetbin=[(8192000, 8193000), (9194000, 9195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=810), r2=pFail(setbin=810), r4=pFail(setbin=810), r5=pFail(setbin=810)),
                           Fitem('SAME', test2, r0=pFail(setbin=910), r2=pFail(setbin=900), r3=pFail(ret=0), r4=pFail(setbin=900), r5=pFail(setbin=900)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99082000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98082000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8100000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n8100000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8100001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8100001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b8100002_fail_FUN_Instance1_4;
            IncrementCounters FUN::n8100002_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8100003_fail_FUN_Instance1_5;
            IncrementCounters FUN::n8100003_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99094000_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98094000_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b9104000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n9104000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b9000000_fail_FUN_Instance2_2;
            IncrementCounters FUN::n9000000_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b9000001_fail_FUN_Instance2_4;
            IncrementCounters FUN::n9000001_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b9000002_fail_FUN_Instance2_5;
            IncrementCounters FUN::n9000002_fail_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_8dig_autobin_range_error_NVLClassHBSBXXXX(self):

        with self.assertRaisesRegex(ErrorUser, 'Please ensure that the start of the range is less than the end'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4400, 4410), (44008000, 44005000)], defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(94441900, 94441950), defaultthermalbin=(97944400, 97944450))
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")

                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_SBDef_check_w_ignore_bins_NVLClassHBSBXXXX(self):
        """
        Test case where if we end up having ignore bins
        """

        with MockVar(NVLClassHBSBXXXX, 'sbdef_prohibited_databins', ['97', '98', '99']), MockVar(NVLClassHBSBXXXX, 'sbdef_prohibited_hardbins', ['97', '98', '99']):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")

                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b4400    4400    : "b4400",    b44_FAIL_SBFT;
        Bin b4419    4419    : "b4419",    b44_FAIL_SBFT;
    }

    BinGroup DataBins
    {
        LeafBin b44000000_fail_FUN_Instance1_0    44000000    : "b44000000_fail_FUN_Instance1_0",    b4400;
        LeafBin b44000001_fail_FUN_Instance1_2    44000001    : "b44000001_fail_FUN_Instance1_2",    b4400;
        LeafBin b44190000_fail_FUN_Instance1_5    44190000    : "b44190000_fail_FUN_Instance1_5",    b4419;
    }

}
'''
        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_auto_bin_existing_autobinner_nonAUTO_NVLClassHBSBXXXX(self):
        """
        Test case where there is existing autbinner when setbin=-44 and not setbin=AUTO
        """
        bindict = {
            "Instance1": {
                "bin": "4415",
                "rm2": "99449000",
                "r0": "44150000",
                "r4": "97449000",
                "r2": "44150001"
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99449000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44150000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44150001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97449000_fail_FUN_Instance1_4;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_incorrect_rm1_rm2_manual_bin_NVLClassHBSBXXXX(self):
        """
        Test cases where rm1/rm2 manual bin is not 99HB or 98HB
        """
        with self.assertRaisesRegex(ErrorUser, "setbin must start with '99'"):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4500, 4510), (44004000, 44005000)], defaultrm2bin=[(99442000, 99443000), (99454000, 99456000)], defaultrm1bin=[(98442000, 98443000), (98454000, 98456000)], defaultresetbin=[(44192000, 44193000), (45194000, 45195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")

                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=4400)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "setbin must start with '98'"):
            class PyObj1:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4500, 4510), (44004000, 44005000)], defaultrm2bin=[(99442000, 99443000), (99454000, 99456000)], defaultrm1bin=[(98442000, 98443000), (98454000, 98456000)], defaultresetbin=[(44192000, 44193000), (45194000, 45195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")

                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=9944), rm1=pFail(setbin=4400)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj1)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_two_digit_port_numbers_NVLClassHBSBXXXX(self):
        # Test 2-digit port numbers (r63, r78, r86, r97, r102) with NVLClassHBSBXXXX strategy
        # Validates that port numbers are fully extracted, not just last digit

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440000, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        r0=pFail(setbin=AUTO),
                                        r63=pFail(setbin=AUTO),
                                        r78=pFail(setbin=AUTO),
                                        r86=pFail(setbin=AUTO),
                                        r97=pPass(),
                                        r102=pFail(setbin=AUTO)))

            subflow = Flow('SubFlow1', test1)

        PyMtpl().main_one(PyObj)

        # Verify bin and counter strings have full port numbers (63, 78, 86, 97, 102), not just last digit
        mtpl_content = File('out.mtpl').read()

        # Check that counter/bin strings end with full port numbers
        self.assertIn('_Instance1_63', mtpl_content, "Counter should end with _63, not _3")
        self.assertIn('_Instance1_78', mtpl_content, "Counter should end with _78, not _8")
        self.assertIn('_Instance1_86', mtpl_content, "Counter should end with _86, not _6")
        # r97 is pPass() without bin, so it won't have a counter
        self.assertIn('_Instance1_102', mtpl_content, "Counter should end with _102, not _2")

        # Verify setbin strings for 2-digit ports
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_63', "SetBin should end with _63")
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_78', "SetBin should end with _78")
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_86', "SetBin should end with _86")
        self.assertRegex(mtpl_content, r'b\d{8}_fail_FUN_Instance1_102', "SetBin should end with _102")

        # Check auto-generated bins were created correctly
        self.assertIn('44000', mtpl_content)  # First auto-generated bin from HBSB 4400

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 63
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_63;
            IncrementCounters FUN::n44000001_fail_Instance1_63;
        }
        Result 78
        {
            Property PassFail = "Fail";
            SetBin b44000002_fail_FUN_Instance1_78;
            IncrementCounters FUN::n44000002_fail_Instance1_78;
        }
        Result 86
        {
            Property PassFail = "Fail";
            SetBin b44000003_fail_FUN_Instance1_86;
            IncrementCounters FUN::n44000003_fail_Instance1_86;
        }
        Result 97
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 102
        {
            Property PassFail = "Fail";
            SetBin b44000004_fail_FUN_Instance1_102;
            IncrementCounters FUN::n44000004_fail_Instance1_102;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_manual_bin_and_ctr_repeat(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=44000000, ctr=44000000), r2=pFail(setbin=44000001, ctr=44000001)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44190000, 44190100),
                                                defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=44000000, ctr=44000000), r2=pFail(setbin=44000001, ctr=44000001)))

        with CaptureStdoutLog() as p:
            PyMtpl().main_one(PyObj1)
        self.assertIn('NO UPDATE: No changes to out.mtpl', p.getvalue())

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_import_error_hbsbxxxx(self):
        # Test that InitializeNVLClassHBSBXXXX raises error when IS_UT is False
        with MockVar(core, 'IS_UT', False):
            with self.assertRaisesRegex(ErrorUser, 'InitializeNVLClassHBSBXXXX is intended for sandbox test use only.'):
                # Import is allowed, but calling the function should raise error
                from pymtpl.core import InitializeNVLClassHBSBXXXX
                InitializeNVLClassHBSBXXXX()

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_4dig_manualbin_SBDef_gen_NVLClassHBSBXXXX(self):
        """
        Test case to check if we are generating the SBDef file when bins are manually assigned.
        """

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4500, 4510)], defaultrm2bin=[(99442000, 99443000), (99454000, 99456000)], defaultrm1bin=[(98442000, 98443000), (98454000, 98456000)], defaultresetbin=[(44192000, 44193000), (45194000, 45195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400), r4=pFail(setbin=4400), r5=pFail(setbin=4400)),
                           Fitem('SAME', test2, r0=pFail(setbin=4500), r2=pFail(setbin=4500), r3=pFail(ret=0), r4=pFail(setbin=4500), r5=pFail(setbin=4500)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        sbdef_expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b4400    4400    : "b4400",    b44_FAIL_SBFT;
        Bin b4500    4500    : "b4500",    b45_FAIL_FOXTON_TECH_OR_PCU_OR_XAUI;
        Bin b9844    9844    : "b9844",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9845    9845    : "b9845",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9944    9944    : "b9944",    b99_FAIL_HARDWARE_ALARM;
        Bin b9945    9945    : "b9945",    b99_FAIL_HARDWARE_ALARM;
    }

    BinGroup DataBins
    {
        LeafBin b44000000_fail_FUN_Instance1_0    44000000    : "b44000000_fail_FUN_Instance1_0",    b4400;
        LeafBin b44000001_fail_FUN_Instance1_2    44000001    : "b44000001_fail_FUN_Instance1_2",    b4400;
        LeafBin b44000002_fail_FUN_Instance1_4    44000002    : "b44000002_fail_FUN_Instance1_4",    b4400;
        LeafBin b44000003_fail_FUN_Instance1_5    44000003    : "b44000003_fail_FUN_Instance1_5",    b4400;
        LeafBin b45000000_fail_FUN_Instance2_0    45000000    : "b45000000_fail_FUN_Instance2_0",    b4500;
        LeafBin b45000001_fail_FUN_Instance2_2    45000001    : "b45000001_fail_FUN_Instance2_2",    b4500;
        LeafBin b45000002_fail_FUN_Instance2_4    45000002    : "b45000002_fail_FUN_Instance2_4",    b4500;
        LeafBin b45000003_fail_FUN_Instance2_5    45000003    : "b45000003_fail_FUN_Instance2_5",    b4500;
        LeafBin b98442000_fail_FUN_Instance1_n1    98442000    : "b98442000_fail_FUN_Instance1_n1",    b9844;
        LeafBin b98454000_fail_FUN_Instance2_n1    98454000    : "b98454000_fail_FUN_Instance2_n1",    b9845;
        LeafBin b99442000_fail_FUN_Instance1_n2    99442000    : "b99442000_fail_FUN_Instance1_n2",    b9944;
        LeafBin b99454000_fail_FUN_Instance2_n2    99454000    : "b99454000_fail_FUN_Instance2_n2",    b9945;
    }

}
'''

        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), sbdef_expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_4dig_manual_bin_SBDef_gen_existing_mtpl_NVLClassHBSBXXXX(self):
        """
        Test case to check if we are generating the SBDef file when bins are manually assigned and existing mtpl file exists
        """

        # Write an existing mtpl file
        existing_mtpl = '''

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99442000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98442000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b44000002_fail_FUN_Instance1_4;
            IncrementCounters FUN::n44000002_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44000003_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44000003_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99454000_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98454000_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n45000000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance2_2;
            IncrementCounters FUN::n45000001_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b45000002_fail_FUN_Instance2_4;
            IncrementCounters FUN::n45000002_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b45000003_fail_FUN_Instance2_5;
            IncrementCounters FUN::n45000003_fail_Instance2_5;
        }
    }

}
'''
        File('out.mtpl').write(existing_mtpl)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(4500, 4510)], defaultrm2bin=[(99442000, 99443000), (99454000, 99456000)], defaultrm1bin=[(98442000, 98443000), (98454000, 98456000)], defaultresetbin=[(44192000, 44193000), (45194000, 45195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=9944), rm1=pFail(setbin=9844), r0=pFail(setbin=4400), r2=pFail(setbin=4400), r4=pFail(setbin=4400), r5=pFail(setbin=4400)),
                           Fitem('SAME', test2, r0=pFail(setbin=4500), r2=pFail(setbin=4500), r3=pFail(ret=0), r4=pFail(setbin=4500), r5=pFail(setbin=4500)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        sbdef_expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b4400    4400    : "b4400",    b44_FAIL_SBFT;
        Bin b4500    4500    : "b4500",    b45_FAIL_FOXTON_TECH_OR_PCU_OR_XAUI;
        Bin b9844    9844    : "b9844",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9845    9845    : "b9845",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9944    9944    : "b9944",    b99_FAIL_HARDWARE_ALARM;
        Bin b9945    9945    : "b9945",    b99_FAIL_HARDWARE_ALARM;
    }

    BinGroup DataBins
    {
        LeafBin b44000000_fail_FUN_Instance1_0    44000000    : "b44000000_fail_FUN_Instance1_0",    b4400;
        LeafBin b44000001_fail_FUN_Instance1_2    44000001    : "b44000001_fail_FUN_Instance1_2",    b4400;
        LeafBin b44000002_fail_FUN_Instance1_4    44000002    : "b44000002_fail_FUN_Instance1_4",    b4400;
        LeafBin b44000003_fail_FUN_Instance1_5    44000003    : "b44000003_fail_FUN_Instance1_5",    b4400;
        LeafBin b45000000_fail_FUN_Instance2_0    45000000    : "b45000000_fail_FUN_Instance2_0",    b4500;
        LeafBin b45000001_fail_FUN_Instance2_2    45000001    : "b45000001_fail_FUN_Instance2_2",    b4500;
        LeafBin b45000002_fail_FUN_Instance2_4    45000002    : "b45000002_fail_FUN_Instance2_4",    b4500;
        LeafBin b45000003_fail_FUN_Instance2_5    45000003    : "b45000003_fail_FUN_Instance2_5",    b4500;
        LeafBin b98442000_fail_FUN_Instance1_n1    98442000    : "b98442000_fail_FUN_Instance1_n1",    b9844;
        LeafBin b98454000_fail_FUN_Instance2_n1    98454000    : "b98454000_fail_FUN_Instance2_n1",    b9845;
        LeafBin b99442000_fail_FUN_Instance1_n2    99442000    : "b99442000_fail_FUN_Instance1_n2",    b9944;
        LeafBin b99454000_fail_FUN_Instance2_n2    99454000    : "b99454000_fail_FUN_Instance2_n2",    b9945;
    }

}
'''

        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), sbdef_expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_3dig_manualbin_SBDef_gen_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(810, 810), (9104000, 9105000)], defaultrm2bin=[(99082000, 99083000), (99094000, 99096000)], defaultrm1bin=[(98082000, 98083000), (98094000, 98096000)], defaultresetbin=[(8192000, 8193000), (9194000, 9195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=810), r2=pFail(setbin=810), r4=pFail(setbin=810), r5=pFail(setbin=810)),
                           Fitem('SAME', test2, r0=pFail(setbin=910), r2=pFail(setbin=900), r3=pFail(ret=0), r4=pFail(setbin=900), r5=pFail(setbin=900)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        sbdef_expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b810    810    : "b810",    b8_FAIL_VCCCONTINUITY;
        Bin b900    900    : "b900",    b9_FAIL_PIN_LEAKAGE;
        Bin b910    910    : "b910",    b9_FAIL_PIN_LEAKAGE;
        Bin b9808    9808    : "b9808",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9809    9809    : "b9809",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9908    9908    : "b9908",    b99_FAIL_HARDWARE_ALARM;
        Bin b9909    9909    : "b9909",    b99_FAIL_HARDWARE_ALARM;
    }

    BinGroup DataBins
    {
        LeafBin b8100000_fail_FUN_Instance1_0     8100000    : "b8100000_fail_FUN_Instance1_0",    b810;
        LeafBin b8100001_fail_FUN_Instance1_2     8100001    : "b8100001_fail_FUN_Instance1_2",    b810;
        LeafBin b8100002_fail_FUN_Instance1_4     8100002    : "b8100002_fail_FUN_Instance1_4",    b810;
        LeafBin b8100003_fail_FUN_Instance1_5     8100003    : "b8100003_fail_FUN_Instance1_5",    b810;
        LeafBin b9000000_fail_FUN_Instance2_2     9000000    : "b9000000_fail_FUN_Instance2_2",    b900;
        LeafBin b9000001_fail_FUN_Instance2_4     9000001    : "b9000001_fail_FUN_Instance2_4",    b900;
        LeafBin b9000002_fail_FUN_Instance2_5     9000002    : "b9000002_fail_FUN_Instance2_5",    b900;
        LeafBin b9104000_fail_FUN_Instance2_0     9104000    : "b9104000_fail_FUN_Instance2_0",    b910;
        LeafBin b98082000_fail_FUN_Instance1_n1    98082000    : "b98082000_fail_FUN_Instance1_n1",    b9808;
        LeafBin b98094000_fail_FUN_Instance2_n1    98094000    : "b98094000_fail_FUN_Instance2_n1",    b9809;
        LeafBin b99082000_fail_FUN_Instance1_n2    99082000    : "b99082000_fail_FUN_Instance1_n2",    b9908;
        LeafBin b99094000_fail_FUN_Instance2_n2    99094000    : "b99094000_fail_FUN_Instance2_n2",    b9909;
    }

}
'''

        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), sbdef_expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_3dig_manualbin_SBDef_gen_existing_mtpl_NVLClassHBSBXXXX(self):

        # Write existing mtpl
        existing_mtpl = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99082000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98082000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8100000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n8100000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8100001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8100001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b8100002_fail_FUN_Instance1_4;
            IncrementCounters FUN::n8100002_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8100003_fail_FUN_Instance1_5;
            IncrementCounters FUN::n8100003_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99094000_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98094000_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b9104000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n9104000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b9000000_fail_FUN_Instance2_2;
            IncrementCounters FUN::n9000000_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b9000001_fail_FUN_Instance2_4;
            IncrementCounters FUN::n9000001_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b9000002_fail_FUN_Instance2_5;
            IncrementCounters FUN::n9000002_fail_Instance2_5;
        }
    }

}
'''
        File('out.mtpl').write(existing_mtpl)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(810, 810), (9104000, 9105000)], defaultrm2bin=[(99082000, 99083000), (99094000, 99096000)], defaultrm1bin=[(98082000, 98083000), (98094000, 98096000)], defaultresetbin=[(8192000, 8193000), (9194000, 9195000)], defaultthermalbin=[(97442000, 97443000), (97454000, 97456000)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=810), r2=pFail(setbin=810), r4=pFail(setbin=810), r5=pFail(setbin=810)),
                           Fitem('SAME', test2, r0=pFail(setbin=910), r2=pFail(setbin=900), r3=pFail(ret=0), r4=pFail(setbin=900), r5=pFail(setbin=900)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        sbdef_expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b810    810    : "b810",    b8_FAIL_VCCCONTINUITY;
        Bin b900    900    : "b900",    b9_FAIL_PIN_LEAKAGE;
        Bin b910    910    : "b910",    b9_FAIL_PIN_LEAKAGE;
        Bin b9808    9808    : "b9808",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9809    9809    : "b9809",    b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN;
        Bin b9908    9908    : "b9908",    b99_FAIL_HARDWARE_ALARM;
        Bin b9909    9909    : "b9909",    b99_FAIL_HARDWARE_ALARM;
    }

    BinGroup DataBins
    {
        LeafBin b8100000_fail_FUN_Instance1_0     8100000    : "b8100000_fail_FUN_Instance1_0",    b810;
        LeafBin b8100001_fail_FUN_Instance1_2     8100001    : "b8100001_fail_FUN_Instance1_2",    b810;
        LeafBin b8100002_fail_FUN_Instance1_4     8100002    : "b8100002_fail_FUN_Instance1_4",    b810;
        LeafBin b8100003_fail_FUN_Instance1_5     8100003    : "b8100003_fail_FUN_Instance1_5",    b810;
        LeafBin b9000000_fail_FUN_Instance2_2     9000000    : "b9000000_fail_FUN_Instance2_2",    b900;
        LeafBin b9000001_fail_FUN_Instance2_4     9000001    : "b9000001_fail_FUN_Instance2_4",    b900;
        LeafBin b9000002_fail_FUN_Instance2_5     9000002    : "b9000002_fail_FUN_Instance2_5",    b900;
        LeafBin b9104000_fail_FUN_Instance2_0     9104000    : "b9104000_fail_FUN_Instance2_0",    b910;
        LeafBin b98082000_fail_FUN_Instance1_n1    98082000    : "b98082000_fail_FUN_Instance1_n1",    b9808;
        LeafBin b98094000_fail_FUN_Instance2_n1    98094000    : "b98094000_fail_FUN_Instance2_n1",    b9809;
        LeafBin b99082000_fail_FUN_Instance1_n2    99082000    : "b99082000_fail_FUN_Instance1_n2",    b9908;
        LeafBin b99094000_fail_FUN_Instance2_n2    99094000    : "b99094000_fail_FUN_Instance2_n2",    b9909;
    }

}
'''
        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), sbdef_expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_dig4_autobin_cache_check(self):
        # Test case for 4-digit newbin with thermal bin in autobin cache
        # When setbin=-7600 and oldbin is 76000256, we compare 7600 with 7600 (newbin[0:4] with oldbin[0:4])
        bindict = {
            "PCDMIN_DIAGPCD_SLYA_FF_TEST": {
                "bin": "7600",
                "r0": "76000256",
                "r2": "76000257",
                "r4": "97761234",
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(7600, 7650),
                                                defaultrm2bin=(99760000, 99760100),
                                                defaultrm1bin=(98760000, 98760100),
                                                defaultresetbin=(76190000, 76190100),
                                                defaultthermalbin=(97760000, 97760500))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="PCDMIN_DIAGPCD_SLYA_FF_TEST",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-7600, ret=0), r2=pFail(setbin=-7600, ret=0), r1=pPass(ret=0), r4=pFail(setbin=-7600, ret=0)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC PCDMIN_DIAGPCD_SLYA_FF_TEST
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem PCDMIN_DIAGPCD_SLYA_FF_TEST PCDMIN_DIAGPCD_SLYA_FF_TEST
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99760000_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98760000_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b76000256_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 0;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b76000257_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97761234_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_4;
            Return 0;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    def test_dig4_autobin_cache_check_multiple_tests(self):
        # Test case for 4-digit newbin with thermal bin in autobin cache
        # When setbin=-7600 and oldbin is 76000256, we compare 76 with 76 (newbin[0:2] with oldbin[0:2])
        bindict = {
            "PCDMIN_DIAGPCD_SLYA_FF_TEST": {
                "bin": "7600",
                "r0": "76000256",
                "r2": "76000257",
                "r4": "97761234",
            },
            "PCDMIN_DIAGPCD_SLYA_FF_TEST_1": {
                "bin": "7601",
                "r0": "76010256",
                "r2": "76010257",
                "r4": "97761235",
            }
        }

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(7600, 7650),
                                                defaultrm2bin=(99760000, 99760100),
                                                defaultrm1bin=(98760000, 98760100),
                                                defaultresetbin=(76190000, 76190100),
                                                defaultthermalbin=(97760000, 97760500))
            binctr.NVLClassHBSBXXXX.autobindict_internal = bindict
            test1 = VminTC(name="PCDMIN_DIAGPCD_SLYA_FF_TEST",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="PCDMIN_DIAGPCD_SLYA_FF_TEST_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=-7600, ret=0), r2=pFail(setbin=-7600, ret=0), r1=pPass(ret=0), r4=pFail(setbin=-7600, ret=0)),
                           Fitem('SAME', test2, r0=pFail(setbin=-7600, ret=0), r2=pFail(setbin=-7600, ret=0), r1=pPass(ret=0), r4=pFail(setbin=-7600, ret=0)))
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC PCDMIN_DIAGPCD_SLYA_FF_TEST
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC PCDMIN_DIAGPCD_SLYA_FF_TEST_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem PCDMIN_DIAGPCD_SLYA_FF_TEST PCDMIN_DIAGPCD_SLYA_FF_TEST
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99760000_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98760000_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b76000256_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 0;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b76000257_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97761234_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_4;
            Return 0;
        }
    }

    FlowItem PCDMIN_DIAGPCD_SLYA_FF_TEST_1 PCDMIN_DIAGPCD_SLYA_FF_TEST_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99760001_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98760001_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b76010256_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 0;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b76010257_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_1_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97761235_fail_FUN_PCDMIN_DIAGPCD_SLYA_FF_TEST_1_4;
            Return 0;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_commonport_bin_existing_bins_NVLClassHBSBXXXX(self):

        # Write an existing mtpl file
        existing_mtpl = '''

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97440000_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44190000_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99454000_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98454000_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance2_0;
            IncrementCounters FUN::n45000000_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance2_2;
            IncrementCounters FUN::n45000001_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b45000002_fail_FUN_Instance2_4;
            IncrementCounters FUN::n45000002_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b45000003_fail_FUN_Instance2_5;
            IncrementCounters FUN::n45000003_fail_Instance2_5;
        }
    }

}
'''
        File('out.mtpl').write(existing_mtpl)

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    r2=pFail(setbin=4400))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME', r0=pFail(setbin=4400)))])

        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(9944, "rm2", "Dummy"), "99440001")
        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(9844, "rm1", "Dummy"), "98440026")
        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(9744, "r4", "Dummy"), "97440001")
        self.assertEqual(NVLClassHBSBXXXX.convert_4digit_to_8digit_default_ports(4419, "r5", "Dummy"), "44190001")

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ctrrange_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450), ctrrangeforbins=(2000, 2500), defaultrm2bin=(99440000, 99440100), defaultrm1bin=(98440025, 98440100), defaultresetbin=(44190000, 44190100), defaultthermalbin=(97440000, 97440100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44002000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44002001_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440001_fail_FUN_Instance2_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440026_fail_FUN_Instance2_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44012000_fail_FUN_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44012001_fail_FUN_Instance2_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440001_fail_FUN_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190001_fail_FUN_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ctrrange_3dig_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 850), ctrrangeforbins=(56, 2500), defaultrm2bin=(99080000, 99080100), defaultrm1bin=(98080025, 98080100), defaultresetbin=(8190000, 8190100), defaultthermalbin=(97080000, 97080100))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8000056_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8000057_fail_FUN_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97080000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8190000_fail_FUN_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080001_fail_FUN_Instance2_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080026_fail_FUN_Instance2_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8010056_fail_FUN_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8010057_fail_FUN_Instance2_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97080001_fail_FUN_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8190001_fail_FUN_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_ctrrange_multi_bins_NVLClassHBSBXXXX(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=[(800, 850), (4400, 4450)],
                                                ctrrangeforbins=[(56, 56), (58, 2000)],
                                                defaultrm2bin=[(99080000, 99080100), (99440000, 99440100)],
                                                defaultrm1bin=[(98080025, 98080100), (98440000, 98440100)],
                                                defaultresetbin=[(8190000, 8190100), (44190000, 44190100)],
                                                defaultthermalbin=[(97080000, 97080100), (97440000, 97440100)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-8), rm1=pFail(setbin=-8), r0=pFail(setbin=-8), r2=pFail(setbin=-8), r3=pFail(setbin=-8), r4=pFail(setbin=-8), r5=pFail(setbin=-8)),
                           Fitem('SAME', test2, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pFail(setbin=-44)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FUN_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080025_fail_FUN_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8000056_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8000058_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b8000059_fail_FUN_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97080000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b8190000_fail_FUN_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance2_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440000_fail_FUN_Instance2_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000056_fail_FUN_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000058_fail_FUN_Instance2_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_FUN_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_Instance2_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_port1_manual_bins(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClassHBSBXXXX('out', 'FUN',
                                                binrange=(4400, 4450),
                                                defaultrm2bin=(99440000, 99440100),
                                                defaultrm1bin=(98440025, 98440100),
                                                defaultresetbin=(44192000, 44193100),
                                                defaultthermalbin=(97442000, 97443100))

            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=4400),
                                             r1=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440025_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_1;
            IncrementCounters FUN::n44000001_fail_Instance1_1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)


class TestHDBIBinning(TestCase):

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_SBDef_check_HDBI(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeHDBI('out', 'FUN', binrange=(4400, 4450), defaultresetbin=(90441900), defaultthermalbin=(90974400))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        LeafBin b4400_fail_FUN_Instance1    4400    : "b4400_fail_FUN_Instance1",    b44_FAIL_SBFT;
        LeafBin b4419_fail_FUN_RESET_PORT5_SHARED_BIN    4419    : "b4419_fail_FUN_RESET_PORT5_SHARED_BIN",    b44_FAIL_SBFT;
        LeafBin b9744_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN    9744    : "b9744_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b90440000_fail_FUN_Instance1    90440000    : "b90440000_fail_FUN_Instance1",    b44_FAIL_SBFT;
        LeafBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN    90441900    : "b90441900_fail_FUN_RESET_PORT5_SHARED_BIN",    b44_FAIL_SBFT;
        LeafBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN    90974400    : "b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
    }

}
'''
        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrSort8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobin_SBDef_check_3dig_bins_HDBI(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeHDBI('out', 'FUN', binrange=(800, 850), defaultresetbin=(90081900), defaultthermalbin=(90970800))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        LeafBin b0800_fail_FUN_Instance1    0800    : "b0800_fail_FUN_Instance1",    b8_FAIL_VCCCONTINUITY;
        LeafBin b0819_fail_FUN_RESET_PORT5_SHARED_BIN    0819    : "b0819_fail_FUN_RESET_PORT5_SHARED_BIN",    b8_FAIL_VCCCONTINUITY;
        LeafBin b9708_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN    9708    : "b9708_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b90080000_fail_FUN_Instance1    90080000    : "b90080000_fail_FUN_Instance1",    b8_FAIL_VCCCONTINUITY;
        LeafBin b90081900_fail_FUN_RESET_PORT5_SHARED_BIN    90081900    : "b90081900_fail_FUN_RESET_PORT5_SHARED_BIN",    b8_FAIL_VCCCONTINUITY;
        LeafBin b90970800_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN    90970800    : "b90970800_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
    }

}
'''
        self.assertTextEqual(File('FUN_SubBinDefinitions.sbdefs').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobin_SBDef_4dig_and_8dig_bins_HDBI(self):
        """Test that HDBI outputs both 4-digit and 8-digit bins in SoftBins section"""

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeHDBI('out', 'PTH_PRESOAK_TD_X', binrange=(9700, 9750))
            test1 = VminTC(name="THERMALRAMP_K_START_X_X_X_X_PRESOAK",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="TDAU_K_START_X_X_X_X_DIEFORCE",
                           _comment="VminTC comment 2",
                           EndVoltageLimits="0.8")

            subflow = Flow('SubFlow1', [
                Fitem('SAME', test1, r0=pFail(setbin=AUTO), r4=pFail(setbin=AUTO)),
                Fitem('SAME', test2, r0=pFail(setbin=AUTO), r4=pFail(setbin=AUTO))
            ])
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        LeafBin b9700_fail_PTH_PRESOAK_TD_X_THERMALRAMP_K_START_X_X_X_X_PRESOAK    9700    : "b9700_fail_PTH_PRESOAK_TD_X_THERMALRAMP_K_START_X_X_X_X_PRESOAK",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b9701_fail_PTH_PRESOAK_TD_X_TDAU_K_START_X_X_X_X_DIEFORCE    9701    : "b9701_fail_PTH_PRESOAK_TD_X_TDAU_K_START_X_X_X_X_DIEFORCE",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b9797_fail_PTH_DTS_XXX_PTH_PRESOAK_TD_X_THERMAL_PORT4_SHARED_BIN    9797    : "b9797_fail_PTH_DTS_XXX_PTH_PRESOAK_TD_X_THERMAL_PORT4_SHARED_BIN",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b90970000_fail_PTH_PRESOAK_TD_X_THERMALRAMP_K_START_X_X_X_X_PRESOAK    90970000    : "b90970000_fail_PTH_PRESOAK_TD_X_THERMALRAMP_K_START_X_X_X_X_PRESOAK",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b90970100_fail_PTH_PRESOAK_TD_X_TDAU_K_START_X_X_X_X_DIEFORCE    90970100    : "b90970100_fail_PTH_PRESOAK_TD_X_TDAU_K_START_X_X_X_X_DIEFORCE",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
        LeafBin b90979700_fail_PTH_DTS_XXX_PTH_PRESOAK_TD_X_THERMAL_PORT4_SHARED_BIN    90979700    : "b90979700_fail_PTH_DTS_XXX_PTH_PRESOAK_TD_X_THERMAL_PORT4_SHARED_BIN",    b97_FAIL_SORT_CHUCK_HANDLER_TEMP;
    }

}
'''
        self.assertTextEqual(File('PTH_PRESOAK_TD_X_SubBinDefinitions.sbdefs').read(), expect)


class TestBaseCounter(TestCase):

    @with_(TempDir, chdir=True)
    def test_same_counter_usererror(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO),
                                    r2=pFail(ctr=44000000, setbin=4400)))])

        with self.assertRaisesRegex(ErrorUser, 'is not unique'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_ctr_format(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=440000, setbin=AUTO),
                                    r2=pFail(ctr=44000000, setbin=4400)))])

        with self.assertRaisesRegex(ErrorUser, 'is in an incorrect format'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_get_counter_for_3dig_bin(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(setbin=801)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n8010001_fail_Instance1_2
} # End of Test Counter Definition

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90080801_fail_FUN_Instance1;
            IncrementCounters FUN::n8010001_fail_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_4dig_counter(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=4400, setbin=AUTO),
                                    r3=pFail(ctr=4400, setbin=AUTO),
                                    r2=pFail(ctr=44000001, setbin=4400)))])
        with self.assertRaisesRegex(ErrorUser, "is in an incorrect format"):
            PyMtpl().main_one(PyObj)

    def test_baseclass_ctr(self):
        # purely for coverage
        with self.assertRaisesRegex(Exception, 'subclass'):
            BaseCounter.convert_4digit_to_8digit('4444')
        with self.assertRaisesRegex(Exception, 'subclass'):
            BaseCounter.get_unique_counter('88888888')

    @with_(TempDir, chdir=True)
    def test_auto_counter(self):
        counterdict = {
            "Instance10": {
                "r0": 44010025
            },
            "Instance1": {
                "r0": 44010001
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance10", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(setbin=AUTO)))])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n44010025_fail_Instance10_0
} # End of Test Counter Definition

Test VminTC Instance10
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance10 Instance10
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance10;
            IncrementCounters FUN::n44010025_fail_Instance10_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_auto_counter_used_counter(self):
        """
        Test case where manual counter is already being used by autocounter
        """
        counterdict = {
            "Instance10": {
                "r0": 44010025
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance10", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44010025)))])
        with self.assertRaisesRegex(ErrorUser, "is already being used by autocounter"):
            PyMtpl().main_one(PyObj)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_sticky_auto_counter(self):
        counterdict = {
            "MTTtname": {
                "r0": 44000001,
                "r2": 44000002
            },
            "Instance1": {
                "r0": 0,
                "r2": 1
            },
            "\"Instance1\" + \"test\"": {
                "r0": 0,
                "r2": 1
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4404))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name='"Instance1" + "test"',
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                test2 = MultiTrial(name="MTTtname1",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))

                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)), Fitem('SAME', test2, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))

            PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n10010000_fail_Instance1_0,
    n10010000_fail_Instance1test_0,
    n10010001_fail_Instance1_2,
    n10010001_fail_Instance1test_2,
    n10020000_fail_Instance1_0,
    n10020000_fail_Instance1test_0,
    n10020001_fail_Instance1_2,
    n10020001_fail_Instance1test_2,
    n10030000_fail_Instance1_0,
    n10030000_fail_Instance1test_0,
    n10030001_fail_Instance1_2,
    n10030001_fail_Instance1test_2,
    n10040000_fail_Instance1_0,
    n10040000_fail_Instance1test_0,
    n10040001_fail_Instance1_2,
    n10040001_fail_Instance1test_2,
    n10050000_fail_Instance1_0,
    n10050000_fail_Instance1test_0,
    n10050001_fail_Instance1_2,
    n10050001_fail_Instance1test_2,
    n44000001_fail_MTTtname_0,
    n44000002_fail_MTTtname_2,
    n44010001_fail_MTTtname1_0,
    n44010002_fail_MTTtname1_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC "Instance1" + "test"
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0000_fail_" + "Instance1" + "test" + "_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_" + "Instance1" + "test" + "_2";
            Return 2;
        }
    }
}

MultiTrialTest MTTtname1
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname1";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0000_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname1";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_2";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000002_fail_MTTtname_2;
        }
    }

    DUTFlowItem MTTtname1 MTTtname1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_MTTtname1;
            IncrementCounters FUN::n44010001_fail_MTTtname1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_MTTtname1;
            IncrementCounters FUN::n44010002_fail_MTTtname1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_auto_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN', binrange=(4400, 4450))
                print(MTTCtrHBSB.mtt_ctr_start)
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n10010000_fail_Instance1_0,
    n10010001_fail_Instance1_2,
    n10020000_fail_Instance1_0,
    n10020001_fail_Instance1_2,
    n10030000_fail_Instance1_0,
    n10030001_fail_Instance1_2,
    n10040000_fail_Instance1_0,
    n10040001_fail_Instance1_2,
    n10050000_fail_Instance1_0,
    n10050001_fail_Instance1_2,
    n44000001_fail_MTTtname_0,
    n44000002_fail_MTTtname_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0000_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_2";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000002_fail_MTTtname_2;
        }
    }

}
    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_auto_counter_speedflow_dfi_name(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name='"Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN"',
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n10010000_fail_Instance10.8_CORE_BEGIN_0,
    n10010001_fail_Instance10.8_CORE_BEGIN_2,
    n10020000_fail_Instance10.8_CORE_BEGIN_0,
    n10020001_fail_Instance10.8_CORE_BEGIN_2,
    n10030000_fail_Instance10.8_CORE_BEGIN_0,
    n10030001_fail_Instance10.8_CORE_BEGIN_2,
    n10040000_fail_Instance10.8_CORE_BEGIN_0,
    n10040001_fail_Instance10.8_CORE_BEGIN_2,
    n10050000_fail_Instance10.8_CORE_BEGIN_0,
    n10050001_fail_Instance10.8_CORE_BEGIN_2,
    n44000001_fail_MTTtname_0,
    n44000002_fail_MTTtname_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC "Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN"
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0000_fail_" + "Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN" + "_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_" + "Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN" + "_2";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000002_fail_MTTtname_2;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_manual_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ctr=2,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            ctr=3,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n10010002_fail_Instance1_0,
    n10010003_fail_Instance1_2,
    n10020002_fail_Instance1_0,
    n10020003_fail_Instance1_2,
    n10030002_fail_Instance1_0,
    n10030003_fail_Instance1_2,
    n10040002_fail_Instance1_0,
    n10040003_fail_Instance1_2,
    n10050002_fail_Instance1_0,
    n10050003_fail_Instance1_2,
    n44000001_fail_MTTtname_0,
    n44000002_fail_MTTtname_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0002_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0003_fail_Instance1_2";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000002_fail_MTTtname_2;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_skip_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(ret=0,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(ret=0)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
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

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_invalid_mtt_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'), self.assertRaisesRegex(ErrorUser, 'is not a valid counter for MTT tests'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ctr=44000001,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            ctr=3,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_reuse_mtt_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'), self.assertRaisesRegex(ErrorUser, 'is not unique as it is being used in'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ctr=1,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            ctr=1,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_force_no_counter(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(setbin=801, ctr=0)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90080801_fail_FUN_Instance1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_force_no_bin_nocounter(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_pass_port_ctr(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pPass(ctr=44000001)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    p44000001_pass_Instance1_2
} # End of Test Counter Definition

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44000001_pass_Instance1_2;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_get_thermal_reset_port_counter_start(self):
        # Mock Initialize.nonmttbinstrategy.bin_range and Initialize.nonmttbinstrategy.all_4digit
        mock_bin_range = [(1000, 2000)]
        mock_all_4digit = {1000, 2000, 3000}

        with patch.object(Initialize, 'nonmttbinstrategy', MagicMock(bin_range=mock_bin_range, all_4digit=mock_all_4digit)):
            # Test when bin_range is present
            counter_start = CtrNVLClass8dig.get_thermal_reset_port_counter_start()
            self.assertTrue(0 <= counter_start <= 7000, "Counter start should be within the range 0 to 7000")

            # Test when bin_range is not present
            with patch.object(Initialize.nonmttbinstrategy, 'bin_range', []):
                counter_start = CtrNVLClass8dig.get_thermal_reset_port_counter_start()
                self.assertTrue(0 <= counter_start <= 7000, "Counter start should be within the range 0 to 7000")

    @with_(TempDir, chdir=True)
    def test_no_unique_counter_available(self):
        # Mock Initialize.edcportctrbinrange to simulate the condition
        mock_edcportctrbinrange = []

        with patch.object(BaseCounter, 'edc_pass_port_ctr_range', mock_edcportctrbinrange):
            with self.assertRaisesRegex(ErrorUser, "No unique counter available in the specified ranges"):
                BaseCounter.get_unique_edc_ctr()

    @with_(TempDir, chdir=True)
    def test_pass_port_ctr_w_auto_setbin(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)


class TestNVLClass8digCounter(TestCase):

    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    @with_(TempDir, chdir=True)
    def test_NVLClass8_same_counter_usererror(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO),
                                    r2=pFail(ctr=44000000, setbin=90440000)))])

        with self.assertRaisesRegex(ErrorUser, 'is not unique'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_get_counter_for_3dig_bin(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(setbin=90080100)))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080100_fail_FUN_Instance1;
            IncrementCounters FUN::n8010000_fail_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), edcportctrbinrange=(4400, 4400))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440000)),
                           Fitem('SAME', test2, r0=pFail(setbin=90440000)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), edcportctrbinrange=(4400, 4400))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440100)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44010000_fail_Instance1_0,
    p44005555_pass_Instance1_1
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440100_fail_FUN_Instance1;
            IncrementCounters FUN::n44010000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44005555_pass_Instance1_1;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_7_digit_counter(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(setbin=90440000, ctr=8000000)))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n8000000_fail_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

#     @with_(TempDir, chdir=True)
#     def test_edc_pass_port_ctr_MTT(self):
#         class PyObj:
#             # Start of the "python mtpl code" ====================
#             InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), edcportctrbinrange=(90440000, 90448888))
#             test1 = MultiTrial(name="MTTtname",
#                                 _comment='I am mtt',
#                                 template=VminTC(name='"Instance1" + "test"',
#                                                 _comment="VminTC comment",
#                                                 EndVoltageLimits="0.9"),
#                                 r0=pFail(setbin=AUTO,
#                                         ret=0,
#                                         trialaction="Exit"),
#                                 r2=pFail(setbin=AUTO,
#                                         ret=2,
#                                         trialaction="Exit"))
#             test2 = MultiTrial(name="MTTtname1",
#                                 _comment='I am mtt',
#                                 template=VminTC(name="Instance1",
#                                                 _comment="VminTC comment",
#                                                 EndVoltageLimits="0.9"),
#                                 r0=pFail(setbin=AUTO,
#                                         ret=0,
#                                         trialaction="Exit"),
#                                 r2=pFail(setbin=AUTO,
#                                         ret=2,
#                                         trialaction="Exit"))
#             subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)),
#                                     Fitem('SAME', test2, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
#         PyMtpl().main_one(PyObj)
#         expect = '''
# '''
#         self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_edc_pass_port_ctr(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), edcportctrbinrange=(4400, 4400))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=AUTO)),
                           Fitem('SAME', test2, r0=pFail(setbin=AUTO)))

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44000000_fail_Instance1_0,
    n44010000_fail_Instance1_1_0,
    p44005555_pass_Instance1_1,
    p44005556_pass_Instance1_1_1
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
            GoTo Instance1_1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44005555_pass_Instance1_1;
            GoTo Instance1_1;
        }
    }

    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440100_fail_FUN_Instance1_1;
            IncrementCounters FUN::n44010000_fail_Instance1_1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44005556_pass_Instance1_1_1;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

#     @with_(TempDir, chdir=True)
#     def test_edc_to_kill_port_ctr(self):

#         class PyObj:
#             # Start of the "python mtpl code" ====================
#             InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), edcportctrbinrange=(90440000, 90448888))
#             test1 = VminTC(name="Instance1",
#                            _comment="VminTC comment",
#                            EndVoltageLimits="0.9")
#             test2 = VminTC(name="Instance1_1",
#                            _comment="VminTC comment",
#                            EndVoltageLimits="0.9")
#             subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=AUTO)),
#                            Fitem('SAME', test2, r0=pFail(setbin=AUTO)))

#         PyMtpl().main_one(PyObj)

#         class PyObj1:
#             # Start of the "python mtpl code" ====================
#             InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), edcportctrbinrange=(90440000, 90448888))
#             test1 = VminTC(name="Instance1",
#                            _comment="VminTC comment",
#                            EndVoltageLimits="0.9")
#             test2 = VminTC(name="Instance1_1",
#                            _comment="VminTC comment",
#                            EndVoltageLimits="0.9")
#             subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=False, r0=pFail(setbin=AUTO)),
#                            Fitem('SAME', test2, r0=pFail(setbin=AUTO)))

#         PyMtpl().main_one(PyObj1)
#         expect = '''

# '''
#         self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_4dig_counter_error(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=4400, setbin=AUTO),
                                    r3=pFail(ctr=4400, setbin=AUTO),
                                    r2=pFail(ctr=44000001, setbin=90440000)))])
        with self.assertRaisesRegex(ErrorUser, "is in an incorrect format"):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_auto_counter(self):
        '''
        Counter is always derived from bins.
        This unit test tests if bin for a test changes, does the counter for that test also change
        We expect the counter to change as well because the bin changes.
        '''
        counterdict = {
            "Instance10": {
                "r0": 44010025
            },
            "Instance1": {
                "r0": 44010001
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance10", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(setbin=AUTO)))])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44000000_fail_Instance10_0
} # End of Test Counter Definition

CSharpTest VminTC Instance10
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance10 Instance10
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance10;
            IncrementCounters FUN::n44000000_fail_Instance10_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_mtt_sticky_auto_counter(self):
        counterdict = {
            "MTTtname": {
                "r0": 44000001,
                "r2": 44000002
            },
            "Instance1": {
                "r0": 0,
                "r2": 1
            },
            "\"Instance1\" + \"test\"": {
                "r0": 0,
                "r2": 1
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4404))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name='"Instance1" + "test"',
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                test2 = MultiTrial(name="MTTtname1",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))

                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)), Fitem('SAME', test2, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC "Instance1" + "test"
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0000_fail_" + "Instance1" + "test" + "_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_" + "Instance1" + "test" + "_2";
            Return 2;
        }
    }
}

MultiTrialTest MTTtname1
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname1";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0000_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4401_fail_FUN_MTTtname1";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000002_fail_MTTtname_2;
        }
    }

    FlowItem MTTtname1 MTTtname1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440100_fail_FUN_MTTtname1;
            IncrementCounters FUN::n44010000_fail_MTTtname1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440100_fail_FUN_MTTtname1;
            IncrementCounters FUN::n44010001_fail_MTTtname1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_auto_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n10013041_fail_Instance1_0,
    n10013042_fail_Instance1_2,
    n10023041_fail_Instance1_0,
    n10023042_fail_Instance1_2,
    n10033041_fail_Instance1_0,
    n10033042_fail_Instance1_2,
    n10043041_fail_Instance1_0,
    n10043042_fail_Instance1_2,
    n10053041_fail_Instance1_0,
    n10053042_fail_Instance1_2,
    n44000000_fail_MTTtname_0,
    n44000001_fail_MTTtname_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "3041_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "3042_fail_Instance1_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_2;
        }
    }

}

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_auto_counter_ARR(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'ARR', binrange=(6000, 6050))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan ARR;


# Test Counter Definition

Counters
{
    n10010356_fail_Instance1_0,
    n10010357_fail_Instance1_2,
    n10020356_fail_Instance1_0,
    n10020357_fail_Instance1_2,
    n10030356_fail_Instance1_0,
    n10030357_fail_Instance1_2,
    n10040356_fail_Instance1_0,
    n10040357_fail_Instance1_2,
    n10050356_fail_Instance1_0,
    n10050357_fail_Instance1_2,
    n60000000_fail_MTTtname_0,
    n60000001_fail_MTTtname_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "6000_fail_ARR_MTTtname";
            IncrementCounters "ARR::n" + FlowMatrix.bin + "0356_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "6000_fail_ARR_MTTtname";
            IncrementCounters "ARR::n" + FlowMatrix.bin + "0357_fail_Instance1_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90600000_fail_ARR_MTTtname;
            IncrementCounters ARR::n60000000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90600000_fail_ARR_MTTtname;
            IncrementCounters ARR::n60000001_fail_MTTtname_2;
        }
    }

}

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_auto_counter_SCN(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'SCN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan SCN;


# Test Counter Definition

Counters
{
    n10016041_fail_Instance1_0,
    n10016042_fail_Instance1_2,
    n10026041_fail_Instance1_0,
    n10026042_fail_Instance1_2,
    n10036041_fail_Instance1_0,
    n10036042_fail_Instance1_2,
    n10046041_fail_Instance1_0,
    n10046042_fail_Instance1_2,
    n10056041_fail_Instance1_0,
    n10056042_fail_Instance1_2,
    n44000000_fail_MTTtname_0,
    n44000001_fail_MTTtname_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_SCN_MTTtname";
            IncrementCounters "SCN::n" + FlowMatrix.bin + "6041_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_SCN_MTTtname";
            IncrementCounters "SCN::n" + FlowMatrix.bin + "6042_fail_Instance1_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_SCN_MTTtname;
            IncrementCounters SCN::n44000000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_SCN_MTTtname;
            IncrementCounters SCN::n44000001_fail_MTTtname_2;
        }
    }

}

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_auto_counter_OTHER(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'DRV', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan DRV;


# Test Counter Definition

Counters
{
    n10019003_fail_Instance1_0,
    n10019004_fail_Instance1_2,
    n10029003_fail_Instance1_0,
    n10029004_fail_Instance1_2,
    n10039003_fail_Instance1_0,
    n10039004_fail_Instance1_2,
    n10049003_fail_Instance1_0,
    n10049004_fail_Instance1_2,
    n10059003_fail_Instance1_0,
    n10059004_fail_Instance1_2,
    n44000000_fail_MTTtname_0,
    n44000001_fail_MTTtname_2
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_DRV_MTTtname";
            IncrementCounters "DRV::n" + FlowMatrix.bin + "9003_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_DRV_MTTtname";
            IncrementCounters "DRV::n" + FlowMatrix.bin + "9004_fail_Instance1_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_DRV_MTTtname;
            IncrementCounters DRV::n44000000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_DRV_MTTtname;
            IncrementCounters DRV::n44000001_fail_MTTtname_2;
        }
    }

}

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_mtt_auto_counter_speedflow_dfi_name(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name='"Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN"',
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC "Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN"
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "3041_fail_" + "Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN" + "_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "3042_fail_" + "Instance1" + FlowMatrix.CLR_F1_FREQ + "_CORE_BEGIN" + "_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_2;
        }
    }

}

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_mtt_manual_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ctr=2,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            ctr=3,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0002_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0003_fail_Instance1_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_2;
        }
    }

}

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_mtt_ctr_for_edc_test(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)
            expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Restore";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            ##EDC## SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "3041_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            ##EDC## SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "3042_fail_Instance1_2";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000000_fail_MTTtname_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440000_fail_FUN_MTTtname;
            IncrementCounters FUN::n44000001_fail_MTTtname_2;
            Return 1;
        }
    }

}

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_mtt_skip_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(ret=0,
                                            ctr=0,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(ret=0)))
            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
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

'''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_invalid_mtt_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'), self.assertRaisesRegex(ErrorUser, 'is not a valid counter for MTT tests'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ctr=44000001,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            ctr=3,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_reuse_mtt_counter(self):
        with MockVar(binctr, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'), self.assertRaisesRegex(ErrorUser, 'is not unique as it is being used in'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450))
                test1 = MultiTrial(name="MTTtname",
                                   _comment='I am mtt',
                                   template=VminTC(name="Instance1",
                                                   _comment="VminTC comment",
                                                   EndVoltageLimits="0.9"),
                                   r0=pFail(setbin=AUTO,
                                            ctr=1,
                                            ret=0,
                                            trialaction="Exit"),
                                   r2=pFail(setbin=AUTO,
                                            ret=2,
                                            ctr=1,
                                            trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_force_no_counter(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(setbin=90080100, ctr=0)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080100_fail_FUN_Instance1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8000000_fail_Instance1_3,
    p8005555_pass_Instance1_1,
    p8005556_pass_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005555_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005556_pass_Instance1_2;
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1;
            IncrementCounters FUN::n8000000_fail_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_force_no_bin_nocounter(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_pass_port_ctr(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pPass(ctr=44000001)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    p44000001_pass_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44000001_pass_Instance1_2;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_pass_port_ctr_w_auto_setbin(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr_nosetbin(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=[(800, 804), (8200, 8254)], edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)

# Removed commented-out test expectation code for clarity and maintainability.
        class PyObj1:
            output = InitializeNVLClass('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8005556_fail_Instance1_2,
    n8005557_fail_Instance1_3,
    n82000000_fail_Instance1_0,
    p8005555_pass_Instance1_1
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90820000_fail_FUN_Instance1;
            IncrementCounters FUN::n82000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005555_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n8005556_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n8005557_fail_Instance1_3;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_two_digit_port_numbers_NVLClass8dig(self):
        # Test 2-digit port numbers (r63, r78, r86, r97, r102) with NVLClass8dig/CtrNVLClass8dig strategy
        # Validates that port numbers are fully extracted, not just last digit

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450),
                                        edcportctrbinrange=[(4400, 4450)])
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        r0=pFail(setbin=AUTO),
                                        r63=pFail(setbin=AUTO),
                                        r78=pFail(setbin=AUTO),
                                        r86=pFail(setbin=AUTO),
                                        r97=pPass(),
                                        r102=pFail(setbin=AUTO)))

            subflow = Flow('SubFlow1', test1)

        PyMtpl().main_one(PyObj)

        # Verify counter strings have full port numbers (63, 78, 86, 97, 102), not just last digit
        mtpl_content = File('out.mtpl').read()

        # Check that counter strings end with full port numbers
        self.assertIn('_Instance1_63', mtpl_content, "Counter should end with _63, not _3")
        self.assertIn('_Instance1_78', mtpl_content, "Counter should end with _78, not _8")
        self.assertIn('_Instance1_86', mtpl_content, "Counter should end with _86, not _6")
        self.assertIn('_Instance1_102', mtpl_content, "Counter should end with _102, not _2")

        # Verify counter strings for 2-digit ports
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_63', "Counter should end with _63")
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_78', "Counter should end with _78")
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_86', "Counter should end with _86")
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_102', "Counter should end with _102")

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44005555_pass_Instance1_1;
            Return 1;
        }
        Result 63
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000001_fail_Instance1_63;
        }
        Result 78
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000002_fail_Instance1_78;
        }
        Result 86
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000003_fail_Instance1_86;
        }
        Result 97
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44005556_pass_Instance1_97;
            Return 1;
        }
        Result 102
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000004_fail_Instance1_102;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)


class TestCtrServerClass8dig(TestCase):
    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    @with_(TempDir, chdir=True)
    def test_same_counter_usererror(self):

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO),
                                    r2=pFail(ctr=44000000, setbin=90440000)))])

        with self.assertRaisesRegex(ErrorUser, 'is not unique'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_get_counter_for_4_and_8dig_bin(self):
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=[(800, 804), (9900, 9999)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(setbin=-99),
                                    rm1=pFail(setbin=-9900),
                                    r2=pFail(setbin=90080100),
                                    r3=pFail(setbin=-800),
                                    r4=pFail(setbin=-8)
                                    )
                       )])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990000_fail_FUN_Instance1_n2;
            IncrementCounters FUN::n90990000_fail_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90990001_fail_FUN_Instance1_n1;
            IncrementCounters FUN::n90990001_fail_Instance1_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080100_fail_FUN_Instance1_2;
            IncrementCounters FUN::n90080100_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n90080000_fail_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90080001_fail_FUN_Instance1_4;
            IncrementCounters FUN::n90080001_fail_Instance1_4;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_auto_counter(self):
        '''
        Counter is always derived from bins.
        This unit test tests if bin for a test changes, does the counter for that test also change
        We expect the counter to change as well because the bin changes.
        '''
        counterdict = {
            "Instance10": {
                "r0": 90440125
            },
            "Instance1": {
                "r0": 90440101
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=[(4400, 4404)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance10", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ret=-2),
                                    rm1=pFail(ret=-1),
                                    r0=pFail(setbin=AUTO)
                                    ))])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n90440000_fail_Instance10_0
} # End of Test Counter Definition

CSharpTest VminTC Instance10
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance10 Instance10
    {
        Result -2
        {
            Property PassFail = "Fail";
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance10_0;
            IncrementCounters FUN::n90440000_fail_Instance10_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat_counter_error(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeCBRClass('out', 'FUN', binrange=[(9800, 9899), (9900, 9999), (4400, 4450)])
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440000)),
                           Fitem('SAME', test2, r0=pFail(setbin=90440000)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'not unique'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_force_no_counter(self):
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r2=pFail(setbin=90080100, ctr=0)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080100_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr(self):

        bin_limits = [(800, 805)]

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r1=pPass(setbin=AUTO),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r1=pPass(setbin=AUTO),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n90080000_fail_Instance1_3,
    p99080000_pass_Instance1_1,
    p99080001_pass_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080000_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080001_pass_Instance1_2;
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n90080000_fail_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_force_no_bin_nocounter(self):
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_force_no_bin_withcounter(self):
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(setbin=-8),
                           rm1=pFail(setbin=None),
                           r2=pFail(),
                       )
                       ),
                VminTC(name="Instance2", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(setbin=None),
                           r2=pFail(setbin=-8)
                       )
                       )
            ]
            )
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n90080000_fail_Instance1_n2,
    n90080001_fail_Instance1_n1,
    n90080002_fail_Instance1_2,
    n90080003_fail_Instance2_n2,
    n90080004_fail_Instance2_n1,
    n90080005_fail_Instance2_2,
    p99080000_pass_Instance1_1,
    p99080001_pass_Instance2_1
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_n2;
            IncrementCounters FUN::n90080000_fail_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080001_fail_Instance1_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080000_pass_Instance1_1;
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080002_fail_Instance1_2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080003_fail_Instance2_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080004_fail_Instance2_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080001_pass_Instance2_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080005_fail_FUN_Instance2_2;
            IncrementCounters FUN::n90080005_fail_Instance2_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_pass_port_ctr_direct(self):

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r2=pPass(ctr=99440001)))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99440001_pass_Instance1_2;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_pass_port_ctr_from_hb(self):
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r2=pPass(setbin=-8)))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080000_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080001_pass_Instance1_2;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr_nosetbin(self):
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=[(800, 804), (8200, 8254)], edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=[(800, 804), (8200, 8254)], edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080000_fail_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080001_fail_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90820000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n90820000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080000_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080002_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080003_fail_Instance1_3;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_no_counter_range_left(self):
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(800, 800), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r2=pFail(setbin=-8),
                                    ))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99080000_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_2;
            IncrementCounters FUN::n90080000_fail_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        self.assertEqual(CtrServerClass8dig.get_unique_edc_ctr("pPass"), "99080001")
        self.assertEqual(CtrServerClass8dig.get_unique_edc_ctr("pPass"), "99080002")

        for i in range(3, 100):
            CtrServerClass8dig.all_8digit_counter.add(f'990800{i:02d}')
        with self.assertRaisesRegex(ErrorUser, "No unique counter available"):
            CtrServerClass8dig.get_unique_edc_ctr("pPass")

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_negbin(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = [(6400, 6401), (801, 801)]

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem()),
                VminTC(name="Instance2", EndVoltageLimits="0.9", _fitem=Fitem())
            ])
        PyMtpl().main_one(PyObj)

        # repeat just in case
        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem()),
                VminTC(name="Instance2", EndVoltageLimits="0.9", _fitem=Fitem())
            ])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn("IncrementCounters FUN::n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n90990800_fail_FAIL_DPS_ALARM_n2", readout)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1,
    n90990800_fail_FAIL_DPS_ALARM_n2,
    p99640000_pass_Instance1_1,
    p99640001_pass_Instance2_1
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990800_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n90990800_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90986400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99640000_pass_Instance1_1;
            GoTo Instance2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990800_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n90990800_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90986400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99640001_pass_Instance2_1;
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(readout, expect)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_posbin(self):
        """Test for defaultrmXbin with 8 digit positive bin value"""
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin=90981234, defaultrm2bin=90995678)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem())
            ])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("IncrementCounters FUN::n90981234_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n90995678_fail_FAIL_DPS_ALARM_n2", readout)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n90981234_fail_FAIL_SYSTEM_SOFTWARE_n1,
    n90995678_fail_FAIL_DPS_ALARM_n2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n90995678_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n90981234_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n90995678_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n90981234_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(readout, expect)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_directset(self):
        """Test for defaultrmXbin with a direct string set and multiple tests"""
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b90981234_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b90995678_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem()),
                VminTC(name="Instance3", _fitem=Fitem()),
            ])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2", readout)
        self.assertIn("IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1", readout)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1,
    n90995678_fail_FUN_shared_counter_n2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance3
{
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    FlowItem Instance3 Instance3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90995678_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(readout, expect)

        # with repeat
        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b90981234_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b90995678_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem()),
                VminTC(name="Instance3", _fitem=Fitem()),
            ])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertTextEqual(readout, expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_two_digit_port_numbers_CtrServerClass8dig(self):
        # Test 2-digit port numbers (r63, r78, r86, r97, r102) with CtrServerClass8dig strategy
        # Validates that port numbers are fully extracted in counter strings, not just last digit

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(4400, 4450),
                                        edcportctrbinrange=[(4400, 4450)],
                                        defaultrm1bin=-44,
                                        defaultrm2bin=-44)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        r0=pFail(setbin=AUTO),
                                        r63=pFail(setbin=AUTO),
                                        r78=pFail(setbin=AUTO),
                                        r86=pFail(setbin=AUTO),
                                        r97=pPass(),
                                        r102=pFail(setbin=AUTO)))

            subflow = Flow('SubFlow1', test1)

        PyMtpl().main_one(PyObj)

        # Verify counter strings have full port numbers (63, 78, 86, 97, 102), not just last digit
        mtpl_content = File('out.mtpl').read()

        # Check that counter strings end with full port numbers
        self.assertIn('_Instance1_63', mtpl_content, "Counter should end with _63, not _3")
        self.assertIn('_Instance1_78', mtpl_content, "Counter should end with _78, not _8")
        self.assertIn('_Instance1_86', mtpl_content, "Counter should end with _86, not _6")
        self.assertIn('_Instance1_102', mtpl_content, "Counter should end with _102, not _2")

        # Verify counter strings for 2-digit ports
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_63', "Counter should end with _63")
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_78', "Counter should end with _78")
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_86', "Counter should end with _86")
        self.assertRegex(mtpl_content, r'n\d{8}_fail_Instance1_102', "Counter should end with _102")

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90994400_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n90994400_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90984400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n90984400_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n90440000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99440000_pass_Instance1_1;
            Return 1;
        }
        Result 63
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1_63;
            IncrementCounters FUN::n90440001_fail_Instance1_63;
        }
        Result 78
        {
            Property PassFail = "Fail";
            SetBin b90440002_fail_FUN_Instance1_78;
            IncrementCounters FUN::n90440002_fail_Instance1_78;
        }
        Result 86
        {
            Property PassFail = "Fail";
            SetBin b90440003_fail_FUN_Instance1_86;
            IncrementCounters FUN::n90440003_fail_Instance1_86;
        }
        Result 97
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p99440001_pass_Instance1_97;
            Return 1;
        }
        Result 102
        {
            Property PassFail = "Fail";
            SetBin b90440004_fail_FUN_Instance1_102;
            IncrementCounters FUN::n90440004_fail_Instance1_102;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    def test_get_non_mtt_portctrstring_ctrpassfail_not_fail_or_pass(self):
        # Line 4368: elif ctrpassfail == "pass" evaluates False when ctrpassfail is neither "fail" nor "pass"
        # Neither if nor elif body sets portctrstring, causing UnboundLocalError on return
        CtrServerClass8dig.autoctrdict['Instance1'] = {'r0': '90440000'}
        with self.assertRaises(UnboundLocalError):
            CtrServerClass8dig._get_non_mtt_portctrstring('90440000', 'Instance1', 1, 'n', 'invalid', 'r0')


class TestCtrDMRClass8dig(TestCase):
    @with_(TempDir, chdir=True)
    def test_force_no_bin_nocounter(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_no_counter_range_left(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(800, 800), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r2=pFail(setbin=-8),
                                    ))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_2;
            IncrementCounters FUN::n90080000_fail_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        for i in range(1, 100):
            CtrServerClass8dig.all_8digit_counter.add(f'900800{i:02d}')
        with self.assertRaisesRegex(ErrorUser, "No unique counter available"):
            CtrServerClass8dig.get_unique_edc_ctr("pFail")

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_pass_port_ctr_from_hb(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r2=pPass(setbin=-8)))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr(self):

        bin_limits = [(800, 805)]

        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r1=pPass(setbin=AUTO),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeDMRClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r1=pPass(setbin=AUTO),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n90080000_fail_Instance1_3
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n90080000_fail_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr_nosetbin(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=[(800, 804), (8200, 8254)], edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r2=pFail(),
                                    r3=pFail(),
                                    r4=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeDMRClass('out', 'FUN', binrange=[(800, 804), (8200, 8254)], edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r2=pFail(),
                                    r3=pFail(),
                                    r4=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080000_fail_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080001_fail_Instance1_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90820000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n90820000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080002_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n90080003_fail_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_no_pass_counter_without_edcbinctrrange(self):
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(setbin=-8),
                                    rm1=pFail(setbin=-8),
                                    r2=pFail(setbin=-8),
                                    r3=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90080000_fail_FUN_Instance1_n2;
            IncrementCounters FUN::n90080000_fail_Instance1_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90080001_fail_FUN_Instance1_n1;
            IncrementCounters FUN::n90080001_fail_Instance1_n1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90080002_fail_FUN_Instance1_2;
            IncrementCounters FUN::n90080002_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_setbinstring_shared_bin_auto_counter(self):
        # Test that setbinstring with _SHARED_BIN automatically derives counter string
        # Expected: counter replaces 'b' with 'n' and '_SHARED_BIN' with '_SHARED_COUNTER'
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(setbinstring='b90984200_fail_SCN_A_CBB_SHARED_BIN_0'),
                                    ))])

        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        # Counter should be derived from setbinstring by replacing b->n and _SHARED_BIN->_SHARED_COUNTER
        self.assertIn('SetBin b90984200_fail_SCN_A_CBB_SHARED_BIN_0', readout)
        self.assertIn('IncrementCounters FUN::n90984200_fail_SCN_A_CBB_SHARED_COUNTER_0', readout)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_setbinstring_shared_bin_auto_counter_multiple_ports(self):
        # Test that multiple ports sharing the same _SHARED_BIN setbinstring generate same counter
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4402))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(setbinstring='b90984200_fail_SCN_A_CBB_SHARED_BIN_0'),
                                    r2=pFail(setbinstring='b90984200_fail_SCN_A_CBB_SHARED_BIN_0'),
                                    ))])

        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        # Both r0 and r2 ports should have the same shared counter
        self.assertEqual(readout.count('IncrementCounters FUN::n90984200_fail_SCN_A_CBB_SHARED_COUNTER_0'), 2)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_setbinstring_no_shared_bin_still_requires_counter(self):
        # Test that setbinstring without _SHARED_BIN still requires explicit counter
        with self.assertRaisesRegex(ErrorUser, 'Counter is required when setbinstring is specified'):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm2=pFail(ctr=0),
                                        rm1=pFail(ctr=0),
                                        r0=pFail(setbinstring='b90984200_fail_SCN_A_CBB_n0'),
                                        ))])

    @with_(TempDir, chdir=True)
    def test_repeat_run_explicit_ctr_bin_not_equal_counter(self):
        # Test that repeat runs succeed when bin != counter (setbinstring with explicit ctr).
        # On first run the counter is added to all_8digit_counter. On second run
        # ctrdictfrommtpl is populated from the existing MTPL and the duplicate check
        # must allow the counter because it matches the previously registered value.
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(ret=0, setbinstring='b12345678_TEST_SHARED_BIN_0', ctr=90998712),
                                    r1=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj)
        first_run_output = File('out.mtpl').read()
        self.assertIn('SetBin b12345678_TEST_SHARED_BIN_0', first_run_output)
        self.assertIn('IncrementCounters FUN::n90998712_fail_Instance1_0', first_run_output)

        # Second run - should not raise "is not unique and is already being used"
        class PyObj1:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(ret=0, setbinstring='b12345678_TEST_SHARED_BIN_0', ctr=90998712),
                                    r1=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj1)
        second_run_output = File('out.mtpl').read()
        self.assertEqual(first_run_output, second_run_output)

    @with_(TempDir, chdir=True)
    def test_repeat_run_explicit_ctr_standard_bin(self):
        # Test that repeat runs also succeed when using a standard auto-bin with an explicit counter.
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(setbin=-44, ctr=90440001),
                                    r1=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj)
        first_run_output = File('out.mtpl').read()
        self.assertIn('IncrementCounters FUN::n90440001_fail_Instance1_0', first_run_output)

        class PyObj1:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(setbin=-44, ctr=90440001),
                                    r1=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj1)
        second_run_output = File('out.mtpl').read()
        self.assertEqual(first_run_output, second_run_output)

    @with_(TempDir, chdir=True)
    def test_repeat_run_new_port_not_in_ctrdictfrommtpl_duplicate_raises_error(self):
        # Test the false branch of `if portid in cls.ctrdictfrommtpl[fitem.get_name()]`
        # in _confirm_no_duplicate_counters.
        # Setup: Instance1 has only r0 on the first run. ctrdictfrommtpl records {Instance1: {r0: ...}}.
        # On second run a new r2 port is added to Instance1 with the same explicit counter as r0.
        # When r2 is validated: Instance1 IS in ctrdictfrommtpl, but 'r2' is NOT (portid check is False),
        # so allow_duplicate stays False. counter 90440001 was already registered by r0 in this run,
        # so the duplicate check fires and raises ErrorUser.
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(setbin=-44, ctr=90440001),
                                    r1=pPass(),
                                    ))])

        PyMtpl().main_one(PyObj)

        # Second run: r2 added with a colliding counter (same as r0).
        # r2 is NOT in ctrdictfrommtpl[Instance1] → portid check is False → allow_duplicate stays False.
        # 90440001 IS already in all_8digit_counter (registered by r0 earlier in this run) → ErrorUser.
        with self.assertRaisesRegex(ErrorUser, 'not unique'):
            class PyObj1:
                output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4401))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm2=pFail(ctr=0),
                                        rm1=pFail(ctr=0),
                                        r0=pFail(setbin=-44, ctr=90440001),
                                        r2=pFail(setbin=-44, ctr=90440001),
                                        r1=pPass(),
                                        ))])
            PyMtpl().main_one(PyObj1)

    @with_(TempDir, chdir=True)
    def test_counter_changed_to_collide_raises_error(self):
        # Test when portid IS in ctrdictfrommtpl (portid check is True),
        # but the counter value has changed so the counter equality check is False.
        # Setup: first run assigns distinct counters to Instance1/r0 and Instance2/r0.
        # ctrdictfrommtpl = {Instance1: {r0: 90440001}, Instance2: {r0: 90440002}}.
        # Second run: both instances use the same new counter 90440099.
        # Instance1/r0=90440099: ctrdictfrommtpl[Instance1][r0]=90440001 ≠ 90440099
        #   → counter equality check is False → allow_duplicate stays False
        #   → 90440099 not yet in all_8digit_counter → passes, 90440099 registered.
        # Instance2/r0=90440099: ctrdictfrommtpl[Instance2][r0]=90440002 ≠ 90440099
        #   → counter equality check is False → allow_duplicate stays False
        #   → 90440099 IS now in all_8digit_counter → ErrorUser.
        class PyObj:
            output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(setbin=-44, ctr=90440001),
                                    r1=pPass())),
                VminTC(name="Instance2", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(ctr=0),
                                    rm1=pFail(ctr=0),
                                    r0=pFail(setbin=-44, ctr=90440002),
                                    r1=pPass()))])

        PyMtpl().main_one(PyObj)

        # Second run: both instances switch to the same counter 90440099.
        # ctrdictfrommtpl has {Instance1: {r0: 90440001}, Instance2: {r0: 90440002}}.
        # Neither stored value matches 90440099 → counter equality check is False for both.
        # Instance2 is checked second, after Instance1 registers 90440099 → ErrorUser.
        with self.assertRaisesRegex(ErrorUser, 'not unique'):
            class PyObj1:
                output = InitializeDMRClass('out', 'FUN', binrange=(4400, 4450))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm2=pFail(ctr=0),
                                        rm1=pFail(ctr=0),
                                        r0=pFail(setbin=-44, ctr=90440099),
                                        r1=pPass())),
                    VminTC(name="Instance2", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm2=pFail(ctr=0),
                                        rm1=pFail(ctr=0),
                                        r0=pFail(setbin=-44, ctr=90440099),
                                        r1=pPass()))])
            PyMtpl().main_one(PyObj1)


class TestCtrSort8dig(TestCase):

    @with_(TempDir, chdir=True)
    def test_get_counter_for_3dig_bin(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804), nonmttbinstrategy=Sort8dig, nonmttctrstrategy=CtrSort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(setbin=801)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n8010000_fail_Instance1_2
} # End of Test Counter Definition

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b8010000_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8010000_fail_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_incorrect_initialize_var_for_ctr(self):
        with self.assertRaisesRegex(ErrorUser, "Pls update Initialize call in your code to define"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), nonmttbinstrategy=Sort8dig, ctrstrategy=CtrSort8dig)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_force_no_counter(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804), nonmttbinstrategy=Sort8dig, nonmttctrstrategy=CtrSort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(setbin=801, ctr=0)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b8010000_fail_FUN_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_4dig_counter(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404), nonmttbinstrategy=Sort8dig, nonmttctrstrategy=CtrSort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=4400, setbin=AUTO),
                                    r2=pFail(ctr=44000001, setbin=4400)))])
        with self.assertRaisesRegex(ErrorUser, "incorrect format"):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_auto_counter(self):
        counterdict = {
            "Instance10": {
                "r0": 44010025
            },
            "Instance1": {
                "r0": 44010001
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4404), nonmttctrstrategy=CtrSort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance10", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=AUTO)))])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44000000_fail_Instance10_0
} # End of Test Counter Definition

CSharpTest VminTC Instance10
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance10 Instance10
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance10_0;
            IncrementCounters FUN::n44000000_fail_Instance10_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_only_counter_no_bin(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804), nonmttbinstrategy=Sort8dig, nonmttctrstrategy=CtrSort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pFail(ctr=44000001)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n44000001_fail_Instance1_2
} # End of Test Counter Definition

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_existing_sticky_auto_counter(self):
        counterdict = {
            "Instance1_1": {
                "r0": "44000000",
                "r2": "44000001"
            },
            "Instance1": {
                "r0": "44010000",
                "r2": "44010001"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4404))
            test1 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            test2 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)), Fitem('SAME', test2, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_1_2;
        }
    }

    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440163_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440163_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44010000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44010001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44010001_fail_Instance1_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_pass_port_ctr(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(800, 804), nonmttbinstrategy=Sort8dig, nonmttctrstrategy=CtrSort8dig)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r2=pPass(ctr=44000001)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    p44000001_pass_Instance1_2
} # End of Test Counter Definition

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44000001_pass_Instance1_2;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_edc_true_ctr(self):

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8000000_fail_Instance1_3,
    p8005555_pass_Instance1_1,
    p8005556_pass_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
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
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005555_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005556_pass_Instance1_2;
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b8000000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n8000000_fail_Instance1_3;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_edc_true_no_ctr(self):

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8000000_fail_Instance1_3
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
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
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b8000000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n8000000_fail_Instance1_3;
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_edc_true_ignore_ports_only(self):

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(),
                                    rm1=pFail()))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
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
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_edc_no_setbin_to_kill_w_setbin_ctr(self):
        '''
        Test for a case where you have no setbin but edcportctrbinrange is defined
        Then user changes the test to kill assigns setbin=AUTO for the same port
        Expect counter to always match bin
        '''

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8000000_fail_Instance1_3,
    p8005555_pass_Instance1_1,
    p8005556_pass_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005555_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005556_pass_Instance1_2;
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n8000000_fail_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_edc_no_setbin_to_kill_w_setbin_ctr_case2(self):

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r2=pPass(),
                                    r3=pFail()))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r2=pPass(),
                                    r3=pFail(setbin=AUTO)))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8000000_fail_Instance1_3,
    p8005555_pass_Instance1_1,
    p8005556_pass_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005555_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005556_pass_Instance1_2;
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n8000000_fail_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr(self):

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=True,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r3=pFail(setbin=AUTO),
                                    r2=pPass(setbin=AUTO)))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8000000_fail_Instance1_3,
    p8005555_pass_Instance1_1,
    p8005556_pass_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005555_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005556_pass_Instance1_2;
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b8000000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n8000000_fail_Instance1_3;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_repeat_edc_true_ctr_nosetbin(self):

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=[(800, 804), (8200, 8254)], edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj)

        # expect = '''
        # '''
        # self.assertTextEqual(File('out.mtpl').read(), expect)
        class PyObj1:
            output = InitializeNVLSort('out', 'FUN', binrange=(800, 804), edcportctrbinrange=(800, 800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME', edc=False,
                                    rm2=pFail(),
                                    rm1=pFail(),
                                    r0=pFail(setbin=-82),
                                    r3=pFail(),
                                    r2=pFail()))])

        PyMtpl().main_one(PyObj1)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8005556_fail_Instance1_2,
    n8005557_fail_Instance1_3,
    n82000000_fail_Instance1_0,
    p8005555_pass_Instance1_1
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b82000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n82000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p8005555_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n8005556_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            IncrementCounters FUN::n8005557_fail_Instance1_3;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_two_digit_port_numbers_Sort8dig(self):
        # Test 2-digit port numbers (r63, r78, r86, r97, r102) with Sort8dig strategy
        # Validates that port numbers are fully extracted, not just last digit

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(44000000, 44999999),
                                       edcportctrbinrange=[(4400, 4450)],
                                       defaultrm1bin=-44,
                                       defaultrm2bin=-44)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        r0=pFail(setbin=44010000),
                                        r63=pFail(setbin=44020000),
                                        r78=pFail(setbin=44030000),
                                        r86=pFail(setbin=44040000),
                                        r97=pPass(),
                                        r102=pFail(setbin=44050000)))

            subflow = Flow('SubFlow1', test1)

        PyMtpl().main_one(PyObj)

        # Verify counter strings have full port numbers (63, 78, 86, 97, 102), not just last digit
        mtpl_content = File('out.mtpl').read()

        # Check that counter strings end with full port numbers
        self.assertIn('_Instance1_63', mtpl_content, "Counter should end with _63, not _3")
        self.assertIn('_Instance1_78', mtpl_content, "Counter should end with _78, not _8")
        self.assertIn('_Instance1_86', mtpl_content, "Counter should end with _86, not _6")
        self.assertIn('_Instance1_97', mtpl_content, "Counter should end with _97, not _7")
        self.assertIn('_Instance1_102', mtpl_content, "Counter should end with _102, not _2")

        # Make sure we DON'T have the wrong single-digit endings
        self.assertNotRegex(mtpl_content, r'_Instance1_3[^0-9]', "Should not have _3 alone (should be _63)")
        self.assertNotRegex(mtpl_content, r'_Instance1_8[^0-9]', "Should not have _8 alone (should be _78 or _86)")
        self.assertNotRegex(mtpl_content, r'_Instance1_6[^0-9]', "Should not have _6 alone (should be _86)")
        # Note: r97 creates _97 so we can't check for _7 alone without false positives

        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99441902_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441902_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44010000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44005555_pass_Instance1_1;
            Return 1;
        }
        Result 63
        {
            Property PassFail = "Fail";
            SetBin b44020000_fail_FUN_Instance1_63;
            IncrementCounters FUN::n44020000_fail_Instance1_63;
        }
        Result 78
        {
            Property PassFail = "Fail";
            SetBin b44030000_fail_FUN_Instance1_78;
            IncrementCounters FUN::n44030000_fail_Instance1_78;
        }
        Result 86
        {
            Property PassFail = "Fail";
            SetBin b44040000_fail_FUN_Instance1_86;
            IncrementCounters FUN::n44040000_fail_Instance1_86;
        }
        Result 97
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p44005556_pass_Instance1_97;
            Return 1;
        }
        Result 102
        {
            Property PassFail = "Fail";
            SetBin b44050000_fail_FUN_Instance1_102;
            IncrementCounters FUN::n44050000_fail_Instance1_102;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)


class TestBaseNumber(TestCase):

    @with_(TempDir, chdir=True)
    def test_auto_basenumber(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404), basenumrange=(1000, 1200))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n44000000_fail_Instance1_0
} # End of Test Counter Definition

Test VminTC Instance1
{
    Basenumbers = "1000";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_auto_basenumber_nonelikeclass(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404), basenumrange=(1000, 1200))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO))),
                VminTC(name="Instance2", EndVoltageLimits="0.9", Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000001, setbin=AUTO)))
            ])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n44000000_fail_Instance1_0,
    n44000001_fail_Instance2_0
} # End of Test Counter Definition

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    Basenumbers = "1000";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_Instance2;
            IncrementCounters FUN::n44000001_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_auto_basenumber_multirange(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404), basenumrange=[(10000, 10001), (11005, 11010)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", Basenumbers=-100,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO))),
                VminTC(name="Instance2", EndVoltageLimits="0.9", Basenumbers=-110,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000001, setbin=AUTO))),
                VminTC(name="Instance3", EndVoltageLimits="0.9", Basenumbers=-100,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000002, setbin=AUTO)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n44000000_fail_Instance1_0,
    n44000001_fail_Instance2_0,
    n44000002_fail_Instance3_0
} # End of Test Counter Definition

Test VminTC Instance1
{
    Basenumbers = "10000";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    Basenumbers = "11005";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance3
{
    Basenumbers = "10001";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_Instance2;
            IncrementCounters FUN::n44000001_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    DUTFlowItem Instance3 Instance3
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444402_fail_FUN_Instance3;
            IncrementCounters FUN::n44000002_fail_Instance3_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_incorrect_basenum_call(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404), basenumrange=[(10000, 10001), (11005, 11010)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO))),
                VminTC(name="Instance2", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000001, setbin=AUTO))),
                VminTC(name="Instance3", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000002, setbin=AUTO)))])

        with self.assertRaisesRegex(ErrorUser, 'Cannot use BaseNumbers=AUTO'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_auto_basenum_from_dict(self):
        basenumdict = {
            "Instance1": "1000",
            "Instance2": "1001",
            "Instance3": "1300"
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoBasenumber.json")
        with open(file_path, 'w') as json_file:
            json.dump(basenumdict, json_file, indent=4)

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       Basenumbers="5555",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO))),
                VminTC(name="Instance2", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000001, setbin=AUTO))),
                VminTC(name="Instance3", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000002, setbin=AUTO)))])

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n44000000_fail_Instance1_0,
    n44000001_fail_Instance2_0,
    n44000002_fail_Instance3_0
} # End of Test Counter Definition

Test VminTC Instance1
{
    Basenumbers = "5555";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    Basenumbers = "1001";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance3
{
    Basenumbers = "1300";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444401_fail_FUN_Instance2;
            IncrementCounters FUN::n44000001_fail_Instance2_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    DUTFlowItem Instance3 Instance3
    {
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444402_fail_FUN_Instance3;
            IncrementCounters FUN::n44000002_fail_Instance3_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    def test_basic_mtt_autobasenum(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', binrange=(4400, 4404), basenumrange=(1000, 1100))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9",
                                               Basenumbers=AUTO,),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=AUTO,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        Basenumbers = "1000";
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444400_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_outofrange_basenumber_usererror(self):

        class PyObj:
            output = Initialize('out', 'FUN', binrange=(4400, 4404), basenumrange=(1000, 1001))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000000, setbin=AUTO))),
                VminTC(name="Instance2", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000001, setbin=AUTO))),
                VminTC(name="Instance3", EndVoltageLimits="0.9",
                       Basenumbers=AUTO,
                       _fitem=Fitem('SAME',
                                    rm1=pFail(),
                                    r0=pFail(ctr=44000002, setbin=AUTO)))])

        with self.assertRaisesRegex(ErrorUser, 'All basenumber range is exhausted'):
            PyMtpl().main_one(PyObj)


# This gets imported into test_core for coverage purposes
class TestCommon(TestCase):
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_default_unassigned_routing_kill(self):
        with MockVar(core, 'IS_UT', False):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=-44), rm1=pFail(setbin=-44), r0=pFail(setbin=-44), r2=pFail(setbin=-44), r4=pFail(setbin=-44), r5=pPass(setbin=-44)))
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
            expect = '''
Test VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000000_fail_FUN_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000001_fail_FUN_Instance1_2;
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44000002_fail_FUN_Instance1_4;
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_default_unassigned_routing_edc(self):
        with MockVar(core, 'IS_UT', False):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeMTL('out', 'FUN', binrange=[(4400, 4450), (4475, 4499)], nonmttbinstrategy=Sort8dig)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', edc=True, r0=pFail(setbin=-44), r2=pFail(setbin=-44))),
                    VminTC(name="Instance2", EndVoltageLimits="0.8",
                           _fitem=Fitem('SAME', edc=True, r0=pFail(setbin=-44)))])
                # End of "python mtpl code"

            PyMtpl().main_one(PyObj)
            expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    EndVoltageLimits = "0.8";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99990162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98980162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b44000000_fail_FUN_Instance1_0;
            GoTo Instance2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b44000001_fail_FUN_Instance1_2;
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99990163_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98980163_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b44010000_fail_FUN_Instance2_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
    '''
            self.assertTextEqual(File('out.mtpl').read(), expect)


class TestBinCtrFromNVLSortMtpl(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread(self):

        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_1_2;
        }
    }

    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440163_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440163_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44010000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44010001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44010001_fail_Instance1_2;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect_bindict = {'Instance1_1': {'bin': '4400',
                                          'rm2': '99440162',
                                          'rm1': '98440162',
                                          'r0': '44000000',
                                          'r2': '44000001'},
                          'Instance1': {'bin': '4401',
                                        'rm2': '99440163',
                                        'rm1': '98440163',
                                        'r0': '44010000',
                                        'r2': '44010001'}}

        expect_ctrdict = {'Instance1_1':
                          {'r0': '44000000',
                           'r2': '44000001'},
                          'Instance1':
                          {'r0': '44010000',
                           'r2': '44010001'}}

        self.assertDictEqual(binctr.Sort8dig.bindictfrommtpl, expect_bindict)
        self.assertDictEqual(binctr.CtrSort8dig.ctrdictfrommtpl, expect_ctrdict)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread_edc(self):

        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b98440162_fail_FUN_Instance1_1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_Instance1_1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_1_2;
        }
    }

    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440163_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440163_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44010000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44010001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44010001_fail_Instance1_2;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect_bindict = {'Instance1_1': {'bin': '4400',
                                          'rm2': '99440162',
                                          'rm1': '98440162',
                                          'r0': '44000000',
                                          'r2': '44000001'},
                          'Instance1': {'bin': '4401',
                                        'rm2': '99440163',
                                        'rm1': '98440163',
                                        'r0': '44010000',
                                        'r2': '44010001'}}

        expect_ctrdict = {'Instance1_1':
                          {'r0': '44000000',
                           'r2': '44000001'},
                          'Instance1':
                          {'r0': '44010000',
                           'r2': '44010001'}}

        self.assertDictEqual(binctr.Sort8dig.bindictfrommtpl, expect_bindict)
        self.assertDictEqual(binctr.CtrSort8dig.ctrdictfrommtpl, expect_ctrdict)

    @with_(TempDir, chdir=True)
    def test_basic_mtpl_read_from_pymtpl(self):
        """
        Unit test to generate mtpl from pymtpl
        Edit a line in mtpl - Update a setbin
        Re-run pymtpl to read the updated mtpl
        Verify the updated setbin is read into bindictfrommtpl
        """

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), usebinctrfrommtpl=True)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        file_path = "out.mtpl"
        with open(file_path, 'r') as file:
            content = file.read()

        # Replace the specific line
        old_line = 'SetBin b44000002_fail_FUN_Instance1_4;'
        new_line = 'SetBin b44000044_fail_FUN_Instance1_4;'

        updated_content = content.replace(old_line, new_line)

        # Write back to the file
        with open(file_path, 'w') as file:
            file.write(updated_content)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), usebinctrfrommtpl=True)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)
        expect = {'Instance1':
                  {'bin': '4400',
                   'rm2': '99440162',
                   'rm1': '98440162',
                   'r0': '44000000',
                   'r2': '44000001',
                   'r4': '44000044',
                   'r5': '44190162'}}

        self.assertDictEqual(binctr.Sort8dig.bindictfrommtpl, expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread_7dig_bins(self):

        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99081456_fail_FUN_Instance1_1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98081456_fail_FUN_Instance1_1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8145656_fail_FUN_Instance1_1_0;
            IncrementCounters FUN::n8145656_fail_Instance1_1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8145657_fail_FUN_Instance1_1_2;
            IncrementCounters FUN::n8145657_fail_Instance1_1_2;
        }
    }

    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99081457_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98081457_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8155656_fail_FUN_Instance1_0;
            IncrementCounters FUN::n8155656_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8155657_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8155657_fail_Instance1_2;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect_bindict = {'Instance1_1':
                          {'bin': '814',
                           'rm2': '99081456',
                           'rm1': '98081456',
                           'r0': '8145656',
                           'r2': '8145657'},
                          'Instance1': {'bin': '815',
                                        'rm2': '99081457',
                                        'rm1': '98081457',
                                        'r0': '8155656',
                                        'r2': '8155657'}}

        expect_ctrdict = {'Instance1_1':
                          {'r0': '8145656',
                           'r2': '8145657'},
                          'Instance1':
                          {'r0': '8155656',
                           'r2': '8155657'}}

        self.assertDictEqual(binctr.Sort8dig.bindictfrommtpl, expect_bindict)
        self.assertDictEqual(binctr.CtrSort8dig.ctrdictfrommtpl, expect_ctrdict)


class TestBinCtrFromNVLClassMtpl(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread_nonmtt(self):

        File('out.mtpl').touch('''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1_1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_2;
        }
    }

    FlowItem Instance1_2 Instance1_2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440002_fail_FUN_Instance1_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect_bindict = {'Instance1':
                          {'bin': '4400',
                           'rm2': '90990101',
                           'rm1': '90980101',
                           'r0': '90440000'},
                          'Instance1_1':
                          {'bin': '4400',
                           'rm2': '90990101',
                           'rm1': '90980101',
                           'r0': '90440001'},
                          'Instance1_2':
                          {'bin': '4400',
                           'rm2': '90990101',
                           'rm1': '90980101',
                           'r0': '90440002'}}

        expect_ctrdict = {'Instance1': {'r0': '44000000'}}

        self.assertDictEqual(binctr.NVLClass8dig.bindictfrommtpl, expect_bindict)
        self.assertDictEqual(binctr.CtrNVLClass8dig.ctrdictfrommtpl, expect_ctrdict)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread_edc_nonmtt(self):

        File('out.mtpl').touch('''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1_2
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90440001_fail_FUN_Instance1_1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_2;
        }
    }

    FlowItem Instance1_2 Instance1_2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440002_fail_FUN_Instance1_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect_bindict = {'Instance1':
                          {'bin': '4400',
                           'rm2': '90990101',
                           'rm1': '90980101',
                           'r0': '90440000'},
                          'Instance1_1':
                          {'bin': '4400',
                           'rm2': '90990101',
                           'rm1': '90980101',
                           'r0': '90440001'},
                          'Instance1_2':
                          {'bin': '4400',
                           'rm2': '90990101',
                           'rm1': '90980101',
                           'r0': '90440002'}}

        expect_ctrdict = {'Instance1': {'r0': '44000000'}}

        self.assertDictEqual(binctr.NVLClass8dig.bindictfrommtpl, expect_bindict)
        self.assertDictEqual(binctr.CtrNVLClass8dig.ctrdictfrommtpl, expect_ctrdict)

    @with_(TempDir, chdir=True)
    def test_basic_mtpl_nonmtt_read_from_pymtpl(self):
        """
        Unit test to generate mtpl from pymtpl
        Edit a line in mtpl - Update a setbin
        Re-run pymtpl to read the updated mtpl
        Verify the updated setbin is read into bindictfrommtpl
        """

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), usebinctrfrommtpl=True)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        file_path = "out.mtpl"
        with open(file_path, 'r') as file:
            content = file.read()

        # Replace the specific line
        old_line = 'SetBin b90440000_fail_FUN_Instance1;'
        new_line = 'SetBin b90440002_fail_FUN_Instance1;'

        updated_content = content.replace(old_line, new_line)

        # Write back to the file
        with open(file_path, 'w') as file:
            file.write(updated_content)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), usebinctrfrommtpl=True)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")

            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)
        expect = {'Instance1':
                  {'bin': '4400',
                   'rm2': '90990101',
                   'rm1': '90980101',
                   'r0': '90440002',
                   'r2': '90440002',
                   'r4': '90974400',
                   'r5': '90441900'}}

        self.assertDictEqual(binctr.NVLClass8dig.bindictfrommtpl, expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread_mtt(self):

        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect = {'MTTtname': {'bin': '4400', 'rm2': '90990101', 'rm1': '90980101', 'r0': '90440000', 'r2': '90440000', 'r4': '90974400', 'r5': '90441900'},
                  'Instance1': {'r0': '4400', 'r2': '4400', 'r4': '4400', 'r5': '4400'}}
        self.assertDictEqual(binctr.NVLClass8dig.bindictfrommtpl, expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread_edc_mtt(self):

        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            ##EDC## SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_MTTtname;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLClass('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect = {'MTTtname': {'bin': '4400', 'rm2': '90990101', 'rm1': '90980101', 'r0': '90440000', 'r2': '90440000', 'r4': '90974400', 'r5': '90441900'},
                  'Instance1': {'r0': '4400', 'r2': '4400', 'r4': '4400', 'r5': '4400'}}
        self.assertDictEqual(binctr.NVLClass8dig.bindictfrommtpl, expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_mtplread_7dig_bins(self):

        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

CSharpTest VminTC Instance1_1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1_1 Instance1_1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99081456_fail_FUN_Instance1_1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98081456_fail_FUN_Instance1_1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8145656_fail_FUN_Instance1_1_0;
            IncrementCounters FUN::n8145656_fail_Instance1_1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8145657_fail_FUN_Instance1_1_2;
            IncrementCounters FUN::n8145657_fail_Instance1_1_2;
        }
    }

    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99081457_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98081457_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8155656_fail_FUN_Instance1_0;
            IncrementCounters FUN::n8155656_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8155657_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8155657_fail_Instance1_2;
        }
    }

}
''', newfile=True)

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', usebinctrfrommtpl=True)

        PyMtpl().main_one(PyObj)
        expect_bindict = {'Instance1_1':
                          {'bin': '814',
                           'rm2': '99081456',
                           'rm1': '98081456',
                           'r0': '8145656',
                           'r2': '8145657'},
                          'Instance1': {'bin': '815',
                                        'rm2': '99081457',
                                        'rm1': '98081457',
                                        'r0': '8155656',
                                        'r2': '8155657'}}

        expect_ctrdict = {'Instance1_1':
                          {'r0': '8145656',
                           'r2': '8145657'},
                          'Instance1':
                          {'r0': '8155656',
                           'r2': '8155657'}}

        self.assertDictEqual(binctr.NVLClassHBSBXXXX.bindictfrommtpl, expect_bindict)
        self.assertDictEqual(binctr.CtrSort8dig.ctrdictfrommtpl, expect_ctrdict)


class TestJGSClass(TestCase):
    # Unit tests for JGSClass binning strategy
    def setUp(self):
        Initialize.clear_all()

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_mixed_bins(self):
        # Test basic 4-digit bin counting with -HB format (e.g., -64)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401), (9900, 9900), (9800, 9800), (912, 912), (70512, 70512)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-9),
                           r1=pFail(setbin=-64),
                           r2=pFail(setbin=-7),
                           r3=pFail(setbin=-64),
                           r4=pPass(setbin=-64),
                           r5=pFail(setbin=-64),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b09120000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Fail";
            SetBin b64000000_fail_FUN_Instance1_1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b07051200_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b64000001_fail_FUN_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b64000003_fail_FUN_Instance1_5;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_4dig_bin_hb_format(self):
        # Test basic 4-digit bin counting with -HB format (e.g., -64)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r1=pPass(setbin=-64),
                           r0=pFail(setbin=-64),
                           r2=pFail(setbin=-64),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b64000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b64000002_fail_FUN_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_4dig_bin_hbsb_format(self):
        # Test 4-digit bin counting with -HBSB format (e.g., -6420)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401), (6420, 6421)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-6400),
                           r2=pFail(setbin=64200000),
                           r3=pFail(setbin=-6420),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b64000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b64200000_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b64200001_fail_FUN_Instance1_3;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_4dig_bin_hbsb_format_error(self):
        # Test 4-digit bin counting with -HBSBXX format (e.g., -642000)
        with self.assertRaisesRegex(ErrorUser, 'definition of setbin'):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401)])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(
                               rm2=pFail(),
                               rm1=pFail(),
                               r0=pFail(setbin=-642000),
                           ))
                ])
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_468dig_bin_range_handling(self):
        # Test mixed 4-digit and 8-digit bin range handling
        # JGSClass supports both formats in get_available_8dig_bin
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6800, 6802), (640002, 640099), (68030009, 68030011)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=68010000),
                           rm2=pFail(setbin=68020000),
                           r0=pFail(setbin=-6800),
                           r2=pFail(setbin=-68),
                           r3=pFail(setbin=-64),
                           r4=pFail(setbin=-6400),
                           r5=pFail(setbin=-640002),
                           r6=pFail(setbin=-6803),
                           r7=pFail(setbin=-680300),
                           r8=pFail(setbin=68030011),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Should generate bins from both 4-digit and 8-digit ranges
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b68010000', mtpl_content)  # From 4-digit range
        self.assertIn('b68020000', mtpl_content)  # From 4-digit range
        self.assertIn('b68000000', mtpl_content)  # From 4-digit range
        self.assertIn('b68000001', mtpl_content)  # From 4-digit range
        self.assertIn('b64000200', mtpl_content)  # From 6-digit range
        self.assertIn('b64000201', mtpl_content)  # From 6-digit range
        self.assertIn('b64000202', mtpl_content)  # From 6-digit range
        self.assertIn('b68030009_', mtpl_content)  # From 8-digit range (_ to make sure length is right)
        self.assertIn('b68030010_', mtpl_content)  # From 8-digit range
        self.assertIn('b68030011_', mtpl_content)  # From 8-digit range

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_468dig_bin_range_handling_reverse(self):
        # Test mixed 4-digit and 8-digit bin range handling making sure we get the right range in various cases
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(68030009, 68030013), (680002, 680099), (6800, 6802)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=68010000),
                           rm2=pFail(setbin=68020000),
                           r0=pFail(setbin=-6800),
                           r2=pFail(setbin=-68),
                           r3=pFail(setbin=-68),
                           r4=pFail(setbin=-6800),
                           r5=pFail(setbin=-680002),
                           r6=pFail(setbin=-6803),
                           r7=pFail(setbin=-680300),
                           r8=pFail(setbin=68030011),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Should generate bins from both 4-digit and 8-digit ranges
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b68010000', mtpl_content)  # From 4-digit range
        self.assertIn('b68020000', mtpl_content)  # From 4-digit range
        self.assertIn('b68000200', mtpl_content)  # From 4-digit range
        self.assertIn('b68030009_', mtpl_content)  # From 8-digit range (_ to make sure length is right)
        self.assertIn('b68030010', mtpl_content)  # From 6-digit range
        self.assertIn('b68000201', mtpl_content)  # From 6-digit range
        self.assertIn('b68000202', mtpl_content)  # From 6-digit range
        self.assertIn('b68030011_', mtpl_content)  # From 8-digit range
        self.assertIn('b68030012_', mtpl_content)  # From 8-digit range
        self.assertIn('b68030013', mtpl_content)  # From 8-digit range

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_357dig_bin_range_handling(self):
        # Test mixed range handling with hardbins less than 10
        # JGSClass supports both formats in get_available_8dig_bin
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(800, 802), (90002, 90099), (8030009, 8030011)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=8010000),
                           rm2=pFail(setbin=8020000),
                           r0=pFail(setbin=-800),
                           r2=pFail(setbin=-8),
                           r3=pFail(setbin=-9),
                           r4=pFail(setbin=-900),
                           r5=pFail(setbin=-90002),
                           r6=pFail(setbin=-803),
                           r7=pFail(setbin=-80300),
                           r8=pFail(setbin=8030011),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Should generate bins from both 4-digit and 8-digit ranges
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b08010000', mtpl_content)  # From 4-digit range
        self.assertIn('b08020000', mtpl_content)  # From 4-digit range
        self.assertIn('b08000000', mtpl_content)  # From 4-digit range
        self.assertIn('b08000001', mtpl_content)  # From 4-digit range
        self.assertIn('b09000200', mtpl_content)  # From 6-digit range
        self.assertIn('b09000201', mtpl_content)  # From 6-digit range
        self.assertIn('b09000202', mtpl_content)  # From 6-digit range
        self.assertIn('b08030009_', mtpl_content)  # From 8-digit range (_ to make sure length is right)
        self.assertIn('b08030010_', mtpl_content)  # From 8-digit range
        self.assertIn('b08030011_', mtpl_content)  # From 8-digit range

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_manual_8dig_setbin(self):
        # Test manual 8-digit setbin values
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             rm2=pFail(),
                                             rm1=pFail(),
                                             r0=pFail(setbin=44000000),
                                             r2=pFail(setbin=44000001)))
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_available_8dig_bin(self):
        # Test get_available_8dig_bin method
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450), (9800, 9850)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(setbin=-98),
                                    rm2=pFail(setbin=-98),
                                    r0=pFail(setbin=44000000))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME',
                                    rm1=pFail(setbin=-98),
                                    rm2=pFail(setbin=-98),
                                    r0=pFail(setbin=44000001)))
            ])
        PyMtpl().main_one(PyObj)
        # Test that get_available_8dig_bin returns correct values
        self.assertEqual(JGSClass.get_available_8dig_bin('-44', 1), '44000002')
        self.assertEqual(JGSClass.get_available_8dig_bin('-4400', 1), '44000003')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_ignore_list_r1_r5(self):
        # Test that r1 and r5 ports are in ignore_list
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-44),
                           r1=pPass(),  # Should not get a bin
                           r2=pFail(setbin=-44),
                           r5=pFail(),  # Should not get a bin (in ignore_list)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # r1 should return 1 and not have SetBin
        mtpl_content = File('out.mtpl').read()
        self.assertIn('Result 1', mtpl_content)
        self.assertIn('Return 1', mtpl_content)
        # r5 is in ignore_list, but since default_thermal_reset_test_classes is empty,
        # it will still appear in output (just without SetBin)
        self.assertIn('Result 5', mtpl_content)
        # Verify r5 doesn't have SetBin
        result_5_section = mtpl_content.split('Result 5')[1].split('Result')[0] if 'Result 5' in mtpl_content else ''
        self.assertNotIn('SetBin', result_5_section)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_bin_range_error_out_of_range(self):
        # Test error when setbin is out of range
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-4500)))  # Out of range
            ])
        with self.assertRaisesRegex(ErrorUser, "Please check the definition of setbin"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_bin_range_error_98_99(self):
        # Test error message for bins 98/99 when not in range
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        with self.assertRaisesRegex(ErrorUser, "Please make sure bin 98/99 ranges are set"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_portstring_method(self):
        # Test _get_portstring method
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-44),
                           rm2=pFail(setbin=-44),
                           r0=pFail(setbin=-44),
                           r2=pFail(setbin=-44),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Verify portstrings in generated bins
        mtpl_content = File('out.mtpl').read()
        self.assertIn('_n1', mtpl_content)  # rm1 -> n1
        self.assertIn('_n2', mtpl_content)  # rm2 -> n2
        self.assertIn('_0', mtpl_content)   # r0 -> 0
        self.assertIn('_2', mtpl_content)   # r2 -> 2

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sbdef_prohibited_lists_empty(self):
        # Test that sbdef_prohibited_hardbins and sbdef_prohibited_databins are empty
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(9800, 9801)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-98),
                           rm2=pFail(setbin=-98),
                           r0=pFail(setbin=-98),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Should not raise error - 98 is allowed in DMR-HD
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b98', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_bin_capacity_hbsbxxxx(self):
        # Test that HBSBXXXX format provides unique 8-digit bins (4-digit HBSB + 4-digit unique)
        # Just verify we can create multiple bins without error
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4400)])
            # Create 10 tests with explicit rm1/rm2 to avoid default 98/99 issue
            instances = []
            for i in range(10):
                instances.append(VminTC(name=f"Instance{i}", EndVoltageLimits="0.9",
                                        _fitem=Fitem(
                                            rm1=pFail(setbin=44010000 + i),
                                            rm2=pFail(setbin=44020000 + i),
                                            r0=pFail(setbin=-44))))
            subflow = Flow('SubFlow1', instances)

        # Should succeed
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Verify bins are being created in HBSBXXXX format
        self.assertIn('b44000000', mtpl_content)
        self.assertIn('b44000009', mtpl_content)  # Last instance

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_3dig_bin_format(self):
        # Test 3-digit bin format (e.g., -800)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(800, 801)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-8),
                           r2=pFail(setbin=-800),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
        Result -1
        {
            Property PassFail = "Fail";
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b08000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b08000001_fail_FUN_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_bin_positive_origbin(self):
        # Test get_new_bin with positive origbin (manual 8-digit bin)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=44000000),
                           r2=pFail(setbin=44000001)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Test that get_new_bin handles positive (manual) bins correctly
        # These should pass through without modification
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b44000000_fail_FUN_Instance1_0', mtpl_content)
        self.assertIn('b44000001_fail_FUN_Instance1_2', mtpl_content)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_bin_origbin_minus_one(self):
        # Test get_new_bin with origbin == -1 (AUTO)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=AUTO),  # AUTO = -1
                           r2=pFail(setbin=-1)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # AUTO should assign bins from the single bin range
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b44000000', mtpl_content)
        self.assertIn('b44000001', mtpl_content)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_bin_origbin_minus_one_multi_range_error(self):
        # Test that get_new_bin with origbin == -1 (AUTO) fails with multiple bin ranges
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450), (9800, 9850)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=AUTO)  # Should fail with multiple ranges
                       ))
            ])
        with self.assertRaisesRegex(ErrorUser, "Cannot use setbin=AUTO.*multiple bin_range"):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_available_8dig_bin_positive_hb(self):
        # Test get_available_8dig_bin with positive HB (no leading minus)
        # Note: Positive 7 or 8 digit only
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),  # Use -44 instead
                           r2=pFail(setbin=-4400),  # Use -4400 instead
                           r3=pFail(setbin=44600000)  # Use -4400 instead # this should be an error!!!
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Should auto-convert and assign bins
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b44000000', mtpl_content)
        self.assertIn('b44000001', mtpl_content)
        self.assertIn('b44600000', mtpl_content)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_available_8dig_bin_positive_error(self):
        # Note: Positive 7 or 8 digit only

        for setbin in [123456, 12345, 1234, 123]:
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=[(1234, 1234)])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(
                               rm2=pFail(setbin=setbin),
                               rm1=pFail(setbin=setbin)
                           ))
                ])
            with self.assertRaisesRegex(ErrorUser, "Expected positive setbin to be 7 or 8-digit"):
                PyMtpl().main_one(PyObj)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_available_8dig_bin_positive_hbsb(self):
        # Test get_available_8dig_bin with positive HBSB values
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401), (6420, 6421)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=64000000),
                           rm2=pFail(setbin=64000001),
                           r0=pFail(setbin=-6400),  # negative HBSB
                           r2=pFail(setbin=-6420)   # negative HBSB
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b64000002', mtpl_content)  # From 6400
        self.assertIn('b64200000', mtpl_content)  # From 6420

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_available_8dig_bin_origbin_minus_one_single_range(self):
        # Test get_available_8dig_bin with origbin == -1 (AUTO) and single range
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-1),
                           r2=pFail(setbin=AUTO)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Should assign bins from first available in range
        mtpl_content = File('out.mtpl').read()
        self.assertIn('b44000000', mtpl_content)
        self.assertIn('b44000001', mtpl_content)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobindict_sticky_bins_reuse(self):
        # Test that _get_non_mtt_autosetbinstring respects autobindict when HB matches
        # For JGSClass, the autobindict should be loaded and bins should be sticky
        os.makedirs("PymtplInputFiles", exist_ok=True)

        # First run - generate bins
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),
                           r2=pFail(setbin=-44)
                       ))
            ])
        PyMtpl().main_one(PyObj1)
        mtpl_content1 = File('out.mtpl').read()

        # Extract the bins that were generated
        import re
        bin_r0_match = re.search(r'b(44\d{6})_fail_FUN_Instance1_0', mtpl_content1)
        bin_r2_match = re.search(r'b(44\d{6})_fail_FUN_Instance1_2', mtpl_content1)
        self.assertIsNotNone(bin_r0_match, "r0 bin should be generated")
        self.assertIsNotNone(bin_r2_match, "r2 bin should be generated")
        bin_r0 = bin_r0_match.group(1)
        bin_r2 = bin_r2_match.group(1)

        # Second run - should reuse the same bins
        Initialize.clear_all()

        class PyObj2:
            output = InitializeJGSClass('out2', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),  # Should reuse same bin
                           r2=pFail(setbin=-44)   # Should reuse same bin
                       ))
            ])
        PyMtpl().main_one(PyObj2)
        mtpl_content2 = File('out2.mtpl').read()

        # Verify the same bins are reused
        self.assertIn(f'b{bin_r0}_fail_FUN_Instance1_0', mtpl_content2, "r0 bin should be reused")
        self.assertIn(f'b{bin_r2}_fail_FUN_Instance1_2', mtpl_content2, "r2 bin should be reused")

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobindict_sticky_bins_hbsb_reuse(self):
        # Test autobindict reuse with HBSB format
        os.makedirs("PymtplInputFiles", exist_ok=True)

        # First run - generate bins
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401), (6420, 6421)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=64000000),
                           rm2=pFail(setbin=64000001),
                           r0=pFail(setbin=-6420),
                           r2=pFail(setbin=-6420)
                       ))
            ])
        PyMtpl().main_one(PyObj1)
        mtpl_content1 = File('out.mtpl').read()

        # Extract the bins that were generated
        import re
        bin_r0_match = re.search(r'b(642\d{5})_fail_FUN_Instance1_0', mtpl_content1)
        bin_r2_match = re.search(r'b(642\d{5})_fail_FUN_Instance1_2', mtpl_content1)
        self.assertIsNotNone(bin_r0_match, "r0 bin should be generated")
        self.assertIsNotNone(bin_r2_match, "r2 bin should be generated")
        bin_r0 = bin_r0_match.group(1)
        bin_r2 = bin_r2_match.group(1)

        # Second run - should reuse the same bins
        Initialize.clear_all()

        class PyObj2:
            output = InitializeJGSClass('out2', 'FUN', binrange=[(6400, 6401), (6420, 6421)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=64000000),
                           rm2=pFail(setbin=64000001),
                           r0=pFail(setbin=-6420),  # Should reuse same bin
                           r2=pFail(setbin=-6420)   # Should reuse same bin
                       ))
            ])
        PyMtpl().main_one(PyObj2)
        mtpl_content2 = File('out2.mtpl').read()

        # Verify the same bins are reused
        self.assertIn(f'b{bin_r0}_fail_FUN_Instance1_0', mtpl_content2, "r0 bin should be reused")
        self.assertIn(f'b{bin_r2}_fail_FUN_Instance1_2', mtpl_content2, "r2 bin should be reused")

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_autobindict_auto_reuse(self):
        # Test that autobindict reuses for AUTO (-1) bins across runs
        os.makedirs("PymtplInputFiles", exist_ok=True)

        # First run - generate bins with AUTO
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=AUTO),
                           r2=pFail(setbin=-1)
                       ))
            ])
        PyMtpl().main_one(PyObj1)
        mtpl_content1 = File('out.mtpl').read()

        # Extract the bins that were generated
        import re
        bin_r0_match = re.search(r'b(44\d{6})_fail_FUN_Instance1_0', mtpl_content1)
        bin_r2_match = re.search(r'b(44\d{6})_fail_FUN_Instance1_2', mtpl_content1)
        self.assertIsNotNone(bin_r0_match, "r0 bin should be generated")
        self.assertIsNotNone(bin_r2_match, "r2 bin should be generated")
        bin_r0 = bin_r0_match.group(1)
        bin_r2 = bin_r2_match.group(1)

        # Second run - should reuse the same bins
        Initialize.clear_all()

        class PyObj2:
            output = InitializeJGSClass('out2', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=AUTO),  # Should reuse same bin
                           r2=pFail(setbin=-1)     # Should reuse same bin
                       ))
            ])
        PyMtpl().main_one(PyObj2)
        mtpl_content2 = File('out2.mtpl').read()

        # Verify the same bins are reused
        self.assertIn(f'b{bin_r0}_fail_FUN_Instance1_0', mtpl_content2, "r0 bin should be reused")
        self.assertIn(f'b{bin_r2}_fail_FUN_Instance1_2', mtpl_content2, "r2 bin should be reused")

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_update_autosetbinstring_ppass(self):
        # Test that update_autosetbinstring returns empty string for pPass
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),
                           r1=pPass(setbin=-44),  # Pass port - should work even if we set a bin
                           r2=pFail(setbin=-44)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # r1 should be Pass with Return 1, no SetBin
        result_1_section = mtpl_content.split('Result 1')[1].split('Result')[0]
        self.assertIn('Pass', result_1_section)
        self.assertIn('Return 1', result_1_section)
        self.assertNotIn('SetBin', result_1_section)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_update_autosetbinstring_pfail(self):
        # Test that update_autosetbinstring works correctly for pFail
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),  # Fail port - should get bin
                           r2=pFail(setbin=-44)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # r0 and r2 should have SetBin
        self.assertIn('SetBin b44000000_fail_FUN_Instance1_0', mtpl_content)
        self.assertIn('SetBin b44000001_fail_FUN_Instance1_2', mtpl_content)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_bin_8dig_when_full(self):
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4400, 4400))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r2=pFail(setbin=44000000))),
            ])

        PyMtpl().main_one(PyObj)
        self.assertEqual(JGSClass.get_new_bin(-1, -44), '44000001')  # from hb
        self.assertEqual(JGSClass.get_new_bin(-1, -1), '44000002')  # auto

        for i in range(3, 10000):
            JGSClass.all_8digit.add(f'4400{i:04d}')
        with self.assertRaisesRegex(ErrorUser, "Unable to find a valid 8-digit bin in the specified range"):
            JGSClass.get_new_bin(-1, -44)  # from hb

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_auto_bin_same_repeat_runs(self):
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4500, 4550))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=(4500, 4550))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))

        PyMtpl().main_one(PyObj1)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    # testing that a port set to AUTO gets changed when the bin limits change
    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_auto_bin_change_repeat_runs(self):
        bin_limits = [(4400, 4450)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=(4500, 4550))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO), r2=pFail(setbin=AUTO)))

        PyMtpl().main_one(PyObj1)
        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b45000001_fail_FUN_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_kill_to_edc_remove_setbin(self):
        # Move test from kill with setbin to edc with no setbin

        class PyObj:
            # Start of the "python mtpl code" ====================
            InitializeJGSClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        class PyObj1:
            # Start of the "python mtpl code" ====================
            InitializeJGSClass('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail()))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj1)

        expect = '''
CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1 @EDC
    {
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

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_autobindict_misc(self):
        # testing out autobindict functionality
        bin_limits = [(4400, 4450), (900, 950)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=44001234),
                                             r2=pFail(setbin=-44),
                                             r3=pFail(setbin=-4400),
                                             r4=pFail(setbin=-9),
                                             r5=pFail(setbin=-900),
                                             r6=pFail(setbin=-44),
                                             ))
        PyMtpl().main_one(PyObj)

        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=44001234),
                                             r2=pFail(setbin=-44),
                                             r3=pFail(setbin=-4400),
                                             r4=pFail(setbin=-9),
                                             r5=pFail(setbin=-900),
                                             r6=pFail(setbin=-9),
                                             ))

        PyMtpl().main_one(PyObj1)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44001234_fail_FUN_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b09000000_fail_FUN_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b09000001_fail_FUN_Instance1_5;
        }
        Result 6
        {
            Property PassFail = "Fail";
            SetBin b09000002_fail_FUN_Instance1_6;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_hbsbxx_bin_range(self):
        # Test 6-digit HBSBXX bin range format for 100-bin specificity
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(680055, 680099)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-68),
                           r2=pFail(setbin=-68),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Bins should be in range 68000055-68009999 (6-digit prefix + 2-digit suffix)
        self.assertIn('b68005500_fail_FUN_Instance1_0', mtpl_content)
        self.assertIn('b68005501_fail_FUN_Instance1_2', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_hbsbxx_limited_range(self):
        # Test 6-digit HBSBXX with single value (only 100 bins available)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(680000, 680000)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-680000),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Should allocate bin in range 68000000-68000099
        self.assertIn('b68000000_fail_FUN_Instance1_0', mtpl_content)
        # Verify the bin is 8 digits
        import re
        bins = re.findall(r'b(\d{8})_fail_FUN_Instance1_0', mtpl_content)
        self.assertEqual(len(bins), 1)
        bin_value = int(bins[0])
        self.assertTrue(68000000 <= bin_value <= 68000099, f"Bin {bin_value} not in expected range [68000000, 68000099]")

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_hbsbxx_for_bins_98_99(self):
        # Test 6-digit HBSBXX format for bins 98 and 99
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(986800, 986849), (996800, 996849)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-986800),
                           r2=pFail(setbin=-996800),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Bin 98 should be in range 98680000-98684999
        self.assertIn('b98680000_fail_FUN_Instance1_0', mtpl_content)
        # Bin 99 should be in range 99680000-99684999
        self.assertIn('b99680000_fail_FUN_Instance1_2', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_vs_4digit_bin_allocation(self):
        # Test that 6-digit and 4-digit ranges produce different bin allocation patterns
        # 4-digit: (6800, 6800) gives 68000000-68009999 (10,000 bins)
        # 6-digit: (680000, 680000) gives 68000000-68000099 (100 bins)

        # Test 4-digit
        class PyObj4:
            output = InitializeJGSClass('out4', 'FUN', binrange=[(6800, 6800)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-68),
                       ))
            ])
        PyMtpl().main_one(PyObj4)
        mtpl_4digit = File('out4.mtpl').read()

        # Test 6-digit
        Initialize.clear_all()

        class PyObj6:
            output = InitializeJGSClass('out6', 'FUN', binrange=[(680000, 680000)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-680000),
                       ))
            ])
        PyMtpl().main_one(PyObj6)
        mtpl_6digit = File('out6.mtpl').read()

        # Both should allocate 68000000 as first bin
        self.assertIn('b68000000_fail_FUN_Instance1_0', mtpl_4digit)
        self.assertIn('b68000000_fail_FUN_Instance1_0', mtpl_6digit)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_hbsbxx_multiple_allocations(self):
        # Test multiple bin allocations from 6-digit range spanning multiple HBSBXX values
        # The range (680000, 680001) allows 200 bins total (100 from 680000 + 100 from 680001)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(680000, 680001)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-680000),
                           r2=pFail(setbin=-680000),
                           r3=pFail(setbin=-680000),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # First 100 bins come from 680000 range, next from 680001 range
        self.assertIn('b68000000_fail_FUN_Instance1_0', mtpl_content)
        self.assertIn('b68000001_fail_FUN_Instance1_2', mtpl_content)
        self.assertIn('b68000002_fail_FUN_Instance1_3', mtpl_content)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_setbin_matching(self):
        # Test that 6-digit setbin values correctly match bin ranges
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(680000, 680099)]
        CtrJGS8dig.all_8digit_counter = set()

        # Should successfully allocate with 6-digit setbin
        bin1 = JGSClass.get_available_8dig_bin('-680000', 1)
        self.assertEqual(bin1, '68000000')

        # Multiple allocations should increment properly
        bin2 = JGSClass.get_available_8dig_bin('-680000', 1)
        self.assertEqual(bin2, '68000001')

    @with_(TempDir, chdir=True)
    def test_6digit_setbin_invalid_format(self):
        # Test that invalid 6-digit setbin values raise appropriate errors
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(680000, 680099)]
        CtrJGS8dig.all_8digit_counter = set()

        # Should raise error for mismatched setbin
        with self.assertRaisesRegex(ErrorUser, 'Either the binrange or setbin are incorrect'):
            JGSClass.get_available_8dig_bin('-690000', 1)

        with self.assertRaisesRegex(ErrorUser, 'Invalid setbin value'):
            JGSClass.get_available_8dig_bin('-123456789', 1)

    @with_(TempDir, chdir=True)
    def test_6digit_range_exhaustion(self):
        # Test behavior when 6-digit bin range is exhausted
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(680000, 680000)]  # Only 100 bins available
        CtrJGS8dig.all_8digit_counter = set()

        # Allocate all 100 bins
        allocated_bins = []
        for i in range(100):
            bin = JGSClass.get_available_8dig_bin('-680000', 1)
            allocated_bins.append(bin)

        # All bins should be unique and in expected range
        self.assertEqual(len(set(allocated_bins)), 100)
        for bin in allocated_bins:
            bin_int = int(bin)
            self.assertTrue(68000000 <= bin_int <= 68000099, f"Bin {bin} out of range")

        # Next allocation should fail
        with self.assertRaisesRegex(ErrorUser, 'Unable to find a valid 8-digit bin'):
            JGSClass.get_available_8dig_bin('-680000', 1)

    @with_(TempDir, chdir=True)
    def test_enhanced_setbin_matching(self):
        # Test the enhanced setbin matching logic where setbin must match
        # the left-aligned digits of binrange, with masking based on setbin specificity

        # Test 1: -68 should match multiple ranges
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig

        # -68 should match (6800, 6899)
        JGSClass.bin_range = [(6800, 6899)]
        CtrJGS8dig.all_8digit_counter = set()
        bin1 = JGSClass.get_available_8dig_bin('-68', 1)
        self.assertEqual(bin1, '68000000')

        # -68 should also match (6849, 6850)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(6849, 6850)]
        CtrJGS8dig.all_8digit_counter = set()
        bin2 = JGSClass.get_available_8dig_bin('-68', 1)
        self.assertEqual(bin2, '68490000')

        # -68 should also match (684912, 684912)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(684912, 684912)]
        CtrJGS8dig.all_8digit_counter = set()
        bin3 = JGSClass.get_available_8dig_bin('-68', 1)
        self.assertEqual(bin3, '68491200')

        # Test 2: -6849 should match some ranges but not others
        # -6849 should match (6849, 6850)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(6849, 6850)]
        CtrJGS8dig.all_8digit_counter = set()
        bin4 = JGSClass.get_available_8dig_bin('-6849', 1)
        self.assertEqual(bin4, '68490000')

        # -6849 should match (684912, 684912)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(684912, 684912)]
        CtrJGS8dig.all_8digit_counter = set()
        bin5 = JGSClass.get_available_8dig_bin('-6849', 1)
        self.assertEqual(bin5, '68491200')

        # -6849 should NOT match (6800, 6899)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(6800, 6899)]
        CtrJGS8dig.all_8digit_counter = set()
        with self.assertRaisesRegex(ErrorUser, 'Either the binrange or setbin are incorrect'):
            JGSClass.get_available_8dig_bin('-6849', 1)

        # Test 3: -684912 should only match very specific ranges
        # -684912 should match (684912, 684912)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(684912, 684912)]
        CtrJGS8dig.all_8digit_counter = set()
        bin6 = JGSClass.get_available_8dig_bin('-684912', 1)
        self.assertEqual(bin6, '68491200')

        # -684912 should NOT match (6800, 6899)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(6800, 6899)]
        CtrJGS8dig.all_8digit_counter = set()
        with self.assertRaisesRegex(ErrorUser, 'Either the binrange or setbin are incorrect'):
            JGSClass.get_available_8dig_bin('-684912', 1)

        # -684912 should NOT match (6849, 6850)
        Initialize.clear_all()
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()
        Initialize.nonmttctrstrategy = CtrJGS8dig
        JGSClass.bin_range = [(6849, 6850)]
        CtrJGS8dig.all_8digit_counter = set()
        with self.assertRaisesRegex(ErrorUser, 'Either the binrange or setbin are incorrect'):
            JGSClass.get_available_8dig_bin('-684912', 1)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_duplicate_fullbin_allocation(self):
        # Test get_available_8dig_bin with positive HB (no leading minus)
        # Note: Positive 7 or 8 digit only

        for setbin in [44010000, 44491234, 44509999]:
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(
                               rm1=pFail(setbin=setbin),
                               rm2=pFail(setbin=setbin),
                           ))
                ])
            with self.assertRaisesRegex(ErrorUser, "Duplicate direct setbin"):
                PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sbdef_bin_number_no_leading_zero_autobin(self):
        # Bug fix: auto-bin '01000000' (HB < 10) must appear as integer 1000000 in the
        # sbdefs LeafBin NUMBER field, not as the string '01000000' with a leading zero.
        # binrange (100, 100) produces 8-digit bin '01000000' (leading zero because HB=01).
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(100, 100)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=10000000),
                           rm2=pFail(setbin=20000000),
                           r0=pFail(setbin=-1),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        sbdef_content = File('FUN.sbdefs').read()
        # Bin NAME b01000000_... is correct (8 chars with leading zero)
        self.assertIn('LeafBin b01000000_fail_FUN_Instance1_0', sbdef_content)
        # Bin NUMBER must be the integer 1000000 (no leading zero), right-justified to 8 chars with spaces
        self.assertIn('     1000000    ', sbdef_content)
        self.assertNotIn('    01000000    ', sbdef_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_sbdef_bin_number_no_leading_zero_direct_setbin(self):
        # Bug fix: direct 7-digit setbin 1000000 is normalised to '01000000' internally;
        # the sbdefs LeafBin NUMBER must still be the integer 1000000 (no leading zero).
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(100, 199)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=10000000),
                           rm2=pFail(setbin=20000000),
                           r0=pFail(setbin=1000000),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        sbdef_content = File('FUN.sbdefs').read()
        self.assertIn('LeafBin b01000000_fail_FUN_Instance1_0', sbdef_content)
        self.assertIn('     1000000    ', sbdef_content)
        self.assertNotIn('    01000000    ', sbdef_content)


class TestCtrJGS8dig(TestCase):
    # Unit tests for CtrJGS8dig counter strategy
    def setUp(self):
        Initialize.clear_all()

    def tearDown(self):
        JGSClass.clear_bins()
        CtrJGS8dig.clear_nonmtt_ctrs()  # This clears edc ctr range

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_mixed_bins(self):
        # Test basic 4-digit bin counting with -HB format (e.g., -64)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401), (9900, 9900), (9800, 9800), (912, 912), (70512, 70512)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           r0=pFail(setbin=-9),
                           r1=pPass(setbin=-9),
                           r2=pFail(setbin=-7),
                           r3=pFail(setbin=-64),
                           r4=pPass(setbin=-9),
                           r5=pFail(setbin=-7),
                           r6=pPass(setbin=-64),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99000000_fail_FUN_Instance1_n2;
            IncrementCounters FUN::n99000000_fail_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98000000_fail_FUN_Instance1_n1;
            IncrementCounters FUN::n98000000_fail_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b09120000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n09120000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p09120001_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b07051200_fail_FUN_Instance1_2;
            IncrementCounters FUN::n07051200_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b64000000_fail_FUN_Instance1_3;
            IncrementCounters FUN::n64000000_fail_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p09120002_pass_Instance1_4;
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b07051201_fail_FUN_Instance1_5;
            IncrementCounters FUN::n07051201_fail_Instance1_5;
        }
        Result 6
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p64000001_pass_Instance1_6;
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_ignore_ctr_list_empty(self):
        # Test that ignore_ctr_list is empty (counters on rm1, rm2)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-44),
                           rm2=pFail(setbin=-44),
                           r0=pFail(setbin=-44),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Verify counters are generated for rm1 and rm2
        mtpl_content = File('out.mtpl').read()
        self.assertIn('IncrementCounters FUN::', mtpl_content)
        # Should have counters for rm1 (n1), rm2 (n2), and r0 (0)
        counter_lines = [line for line in mtpl_content.split('\n') if 'IncrementCounters' in line]
        self.assertGreaterEqual(len(counter_lines), 3)  # At least 3 ports with counters

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_ctr_start_offset_zero(self):
        # Test that ctr_start_offset is 0 (pass counters fill all available space)
        self.assertEqual(CtrJGS8dig.ctr_start_offset, 0)

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),
                           r1=pPass(),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # With ctr_start_offset = 0, counter should match bin
        self.assertIn('n44000000_fail_Instance1_0', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_counter_equals_bin(self):
        # Test that counter equals bin (inheritance from CtrSort8dig)
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=44000000),
                           r2=pFail(setbin=44000001),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Counter should equal bin value
        self.assertIn('n44000000_fail_Instance1_0', mtpl_content)
        self.assertIn('n44000001_fail_Instance1_2', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_manual_counter(self):
        # Test manual counter specification
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=44000000, ctr=99000000),
                           r2=pFail(ctr=0),
                           r3=pFail(ctr=44123456),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Manual counter should be used
        self.assertIn('n99000000_fail_Instance1_0', mtpl_content)
        self.assertIn('n44123456_fail_Instance1_3', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_counter_stickiness(self):
        # Test that counters are saved in autoctrdict for reuse
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=44000000))),
            ])
        PyMtpl().main_one(PyObj)

        # Verify that counter dict was populated
        self.assertIn('Instance1', CtrJGS8dig.autoctrdict)
        self.assertIn('r0', CtrJGS8dig.autoctrdict['Instance1'])
        # Counter should match the bin value
        self.assertEqual(CtrJGS8dig.autoctrdict['Instance1']['r0'], '44000000')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_port_number_extraction(self):
        # Test that _extract_port_number works correctly
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-44),
                           rm2=pFail(setbin=-44),
                           r0=pFail(setbin=-44),
                           r10=pFail(setbin=-44),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Verify port numbers in counter names
        self.assertIn('_n1', mtpl_content)   # rm1
        self.assertIn('_n2', mtpl_content)   # rm2
        self.assertIn('_0', mtpl_content)    # r0
        self.assertIn('_10', mtpl_content)   # r10

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_get_ctrstring_update_counterdict_ppass(self):
        # Test get_ctrstring_update_counterdict with pPass port
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),
                           r1=pPass(),  # Pass port
                           r2=pFail(setbin=-44)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Pass port should have counter based on bin
        # CtrJGS8dig has skip_pass_counters = False, so pass ports get counters
        self.assertIn('IncrementCounters FUN::', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_skip_pass_counters_false(self):
        # Test that skip_pass_counters is False (pass ports get counters)
        self.assertEqual(CtrJGS8dig.skip_pass_counters, False)

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=44010000),
                           rm2=pFail(setbin=44020000),
                           r0=pFail(setbin=-44),
                           r1=pPass(),  # Should get counter
                           r2=pFail(setbin=-44)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Count IncrementCounters lines - should have counters for all ports with bins
        counter_lines = [line for line in mtpl_content.split('\n') if 'IncrementCounters' in line]
        # r0, r2, rm1, rm2 should all have counters
        self.assertGreaterEqual(len(counter_lines), 4)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_negbin(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = [(6400, 6401), (801, 801)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem()),
                VminTC(name="Instance2", EndVoltageLimits="0.9", _fitem=Fitem())
            ])
        PyMtpl().main_one(PyObj)

        # repeat just in case
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem()),
                VminTC(name="Instance2", EndVoltageLimits="0.9", _fitem=Fitem())
            ])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn("IncrementCounters FUN::n98640000_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n99080000_fail_FAIL_DPS_ALARM_n2", readout)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n98640000_fail_FAIL_SYSTEM_SOFTWARE_n1,
    n99080000_fail_FAIL_DPS_ALARM_n2,
    p64000000_pass_Instance1_1,
    p64000001_pass_Instance2_1
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n99080000_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98640000_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n98640000_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p64000000_pass_Instance1_1;
            GoTo Instance2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99080000_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n99080000_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98640000_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n98640000_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p64000001_pass_Instance2_1;
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(readout, expect)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_posbin(self):
        """Test for defaultrmXbin with 8 digit positive bin value"""
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin=98123456, defaultrm2bin=99567890)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem())
            ])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("IncrementCounters FUN::n98123456_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n99567890_fail_FAIL_DPS_ALARM_n2", readout)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n98123456_fail_FAIL_SYSTEM_SOFTWARE_n1,
    n99567890_fail_FAIL_DPS_ALARM_n2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99567890_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n99567890_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98123456_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n98123456_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99567890_fail_FAIL_DPS_ALARM_n2;
            IncrementCounters FUN::n99567890_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98123456_fail_FAIL_SYSTEM_SOFTWARE_n1;
            IncrementCounters FUN::n98123456_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

'''
        self.assertTextEqual(readout, expect)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_directset(self):
        """Test for defaultrmXbin with a direct string set and multiple tests"""
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b98123456_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b99567890_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem()),
                VminTC(name="Instance3", _fitem=Fitem()),
            ])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("IncrementCounters FUN::n99567890_fail_FUN_shared_counter_n2", readout)
        self.assertIn("IncrementCounters FUN::n98123456_FAIL_MIO_DDR_SHARED_COUNTER_n1", readout)

        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n98123456_FAIL_MIO_DDR_SHARED_COUNTER_n1,
    n99567890_fail_FUN_shared_counter_n2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance2
{
    FailCaptureCount = 999;
}

CSharpTest VminTC Instance3
{
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99567890_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n99567890_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98123456_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n98123456_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99567890_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n99567890_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98123456_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n98123456_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
    }

    FlowItem Instance3 Instance3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99567890_fail_FUN_shared_bin_n2;
            IncrementCounters FUN::n99567890_fail_FUN_shared_counter_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98123456_FAIL_MIO_DDR_SHARED_BIN_n1;
            IncrementCounters FUN::n98123456_FAIL_MIO_DDR_SHARED_COUNTER_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(readout, expect)

        # with repeat
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b98123456_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b99567890_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", _fitem=Fitem()),
                VminTC(name="Instance2", _fitem=Fitem()),
                VminTC(name="Instance3", _fitem=Fitem()),
            ])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertTextEqual(readout, expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_port1_follow_port0(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = [(6800, 6801), (6400, 6401)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(
                    r0=pFail(setbin=-64),
                    r1=pPass(),
                    r2=pPass(),
                )),
            ])
        PyMtpl().main_one(PyObj)

        readout = File('out.mtpl').read()
        expect = '''
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b64000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n64000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p64000001_pass_Instance1_1;
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            IncrementCounters FUN::p64000002_pass_Instance1_2;
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(readout, expect)

    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_edc_counter_when_full(self):
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4400, 4400))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r2=pFail(setbin=44000000))),
            ])

        PyMtpl().main_one(PyObj)
        self.assertEqual(JGSClass.get_new_bin(-1, -44), '44000001')  # from hb
        self.assertEqual(JGSClass.get_new_bin(-1, -1), '44000002')  # auto
        # we fill up a couple bins then the rest are counters

        for i in range(3, 10000):
            CtrJGS8dig.all_8digit_counter.add(f'4400{i:04d}')
        with self.assertRaisesRegex(ErrorUser, "No unique counter available"):
            CtrJGS8dig.get_unique_edc_ctr()

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_edc_counter_when_one_range_full(self):
        binrange = [(4400, 4400), (4600, 4600)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=44000000), r1=pPass(ctr=0))),
            ])

        PyMtpl().main_one(PyObj)
        self.assertEqual(JGSClass.get_new_bin(-44, 0), '44000001')  # from hb
        self.assertEqual(JGSClass.get_new_bin(-4400, 0), '44000002')  # hbsb
        # we fill up a couple bins then the rest are counters

        for i in range(3, 10000):
            CtrJGS8dig.all_8digit_counter.add(f'4400{i:04d}')
        # now that the 44 is full, it should use 46
        self.assertEqual(CtrJGS8dig.get_unique_edc_ctr(), '46000000')

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_edcportctrbinrange_accepted(self):
        # Test that 6-digit edcportctrbinrange values are accepted without error
        bin_limits = [(992900, 992999), (982900, 982999), (902900, 902999), (532900, 532999), (2900, 2999)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-29), r1=pPass())),
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        self.assertIn('IncrementCounters FUN::', mtpl_content)

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_edc_counter_range_produces_8digit_counter(self):
        # Test that a 6-digit edcportctrbinrange generates correct 8-digit counters
        bin_limits = [(992900, 992999)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-99), r1=pPass())),
            ])
        PyMtpl().main_one(PyObj)
        # 6-digit range (992900,992999) should produce counters in 99290000-99299999
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertEqual(len(counter), 8)
        self.assertTrue(int(counter) >= 99290000 and int(counter) <= 99299999,
                        f"Counter {counter} should be in range 99290000-99299999")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_mixed_4digit_and_6digit_edcportctrbinrange(self):
        # Test that a mix of 4-digit and 6-digit ranges in edcportctrbinrange works correctly
        bin_limits = [(992900, 992999), (2900, 2999)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-29), r1=pPass())),
                VminTC(name="Instance2", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-29), r1=pPass())),
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        counter_lines = [line for line in mtpl_content.split('\n') if 'IncrementCounters FUN::' in line]
        self.assertGreaterEqual(len(counter_lines), 2)

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_edc_counter_when_6digit_range_full(self):
        # Test that when 6-digit range is full, it raises ErrorUser
        bin_limits = [(992900, 992900)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-99), r1=pPass())),
            ])
        PyMtpl().main_one(PyObj)
        # Fill up counters in the 6-digit range 992900 (99290000-99290099)
        for i in range(100):
            CtrJGS8dig.all_8digit_counter.add(f'9929{i:04d}')
        with self.assertRaisesRegex(ErrorUser, "No unique counter available"):
            CtrJGS8dig.get_unique_edc_ctr()

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_range_falls_through_to_4digit_range(self):
        # Test that when 6-digit range is full, it falls through to the 4-digit range
        bin_limits = [(992900, 992900), (4400, 4400)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-99), r1=pPass())),
            ])
        PyMtpl().main_one(PyObj)
        # Fill up counters in the 6-digit range 992900 (99290000-99290099)
        for i in range(100):
            CtrJGS8dig.all_8digit_counter.add(f'9929{i:04d}')
        # Now counter should fall through to 4-digit range starting at 44000000
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertTrue(counter.startswith('4400'), f"Expected counter to start with 4400, got {counter}")

    def test_set_edc_pass_port_ctr_range_rejects_2digit(self):
        # Test that 2-digit values are rejected with an error
        with self.assertRaises(Exception):
            CtrJGS8dig.set_edc_pass_port_ctr_range((44, 44))

    def test_set_edc_pass_port_ctr_range_accepts_3digit(self):
        # Test that 3-digit values are accepted
        CtrJGS8dig.edc_pass_port_ctr_range.clear()
        CtrJGS8dig.set_edc_pass_port_ctr_range((900, 999))
        self.assertIn((900, 999), CtrJGS8dig.edc_pass_port_ctr_range)
        CtrJGS8dig.edc_pass_port_ctr_range.clear()

    def test_set_edc_pass_port_ctr_range_accepts_6digit(self):
        # Test that 6-digit values are accepted
        CtrJGS8dig.edc_pass_port_ctr_range.clear()
        CtrJGS8dig.set_edc_pass_port_ctr_range((992900, 992999))
        self.assertIn((992900, 992999), CtrJGS8dig.edc_pass_port_ctr_range)
        CtrJGS8dig.edc_pass_port_ctr_range.clear()

    def test_set_edc_pass_port_ctr_range_accepts_mixed_list(self):
        # Test that a list with both 4-digit and 6-digit values is accepted
        CtrJGS8dig.edc_pass_port_ctr_range.clear()
        mixed_list = [(992900, 992999), (982900, 982999), (2900, 2999), (4400, 4450)]
        CtrJGS8dig.set_edc_pass_port_ctr_range(mixed_list)
        for item in mixed_list:
            self.assertIn(item, CtrJGS8dig.edc_pass_port_ctr_range)
        CtrJGS8dig.edc_pass_port_ctr_range.clear()

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_3digit_edc_counter_range_produces_0HSBxxxx(self):
        # 3-digit range (HSB where HB < 10) should produce counters in 0HSBxxxx format.
        # e.g. range (900, 900) represents HB=9,SB=00 and should yield 09000000-09009999.
        bin_limits = [(900, 900)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-9), r1=pPass())),
            ])
        PyMtpl().main_one(PyObj)
        # 3-digit range (900, 900) should produce counters in 09000000-09009999
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertEqual(len(counter), 8)
        self.assertTrue(counter.startswith('0900'),
                        f"Counter {counter} should start with '0900' for 3-digit range 900")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_3digit_edc_counter_range_exhaustion(self):
        # 3-digit range (900, 900) has 10000 counters (09000000-09009999).
        # After filling all of them, the next call should raise ErrorUser.
        bin_limits = [(900, 900)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-9), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        # Fill all 10000 counters in the 3-digit range (09000000-09009999)
        for i in range(10000):
            CtrJGS8dig.all_8digit_counter.add(f'0900{i:04d}')
        with self.assertRaisesRegex(ErrorUser, "No unique counter available"):
            CtrJGS8dig.get_unique_edc_ctr()

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_4digit_edc_counter_range_produces_HBSBxxxx(self):
        # 4-digit range (HBSB) should produce counters in HBSBxxxx format.
        # e.g. range (4400, 4400) should yield 44000000-44009999.
        bin_limits = [(4400, 4400)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertEqual(len(counter), 8)
        self.assertTrue(counter.startswith('4400'),
                        f"Counter {counter} should start with '4400' for 4-digit range 4400")
        self.assertFalse(counter.startswith('0'),
                         f"Counter {counter} for 4-digit range should not have a leading zero")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_5digit_edc_counter_range_produces_0HSByyxx(self):
        # 5-digit range (HSByy where HB < 10) should produce counters in 0HSByyxx format.
        # e.g. range (90050, 90050) represents HB=9,SB=00,yy=50 and should yield 09005000-09005099.
        bin_limits = [(90050, 90050)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-9), r1=pPass())),
            ])
        PyMtpl().main_one(PyObj)
        # 5-digit range (90050, 90050) should produce counters in 09005000-09005099
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertEqual(len(counter), 8)
        self.assertTrue(counter.startswith('090050'),
                        f"Counter {counter} should start with '090050' for 5-digit range 90050")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_5digit_edc_counter_range_exhaustion(self):
        # 5-digit range (90050, 90050) has 100 counters (09005000-09005099).
        # After filling all of them, the next call should raise ErrorUser.
        bin_limits = [(90050, 90050)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-9), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        # Fill all 100 counters in the 5-digit range (09005000-09005099)
        for i in range(100):
            CtrJGS8dig.all_8digit_counter.add(f'090050{i:02d}')
        with self.assertRaisesRegex(ErrorUser, "No unique counter available"):
            CtrJGS8dig.get_unique_edc_ctr()

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_6digit_edc_counter_range_produces_HBSByyxx(self):
        # 6-digit range (HBSByy) should produce counters in HBSByyxx format.
        # e.g. range (440050, 440050) should yield 44005000-44005099.
        bin_limits = [(440050, 440050)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4400)], edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertEqual(len(counter), 8)
        self.assertTrue(counter.startswith('440050'),
                        f"Counter {counter} should start with '440050' for 6-digit range 440050")
        self.assertFalse(counter.startswith('0'),
                         f"Counter {counter} for 6-digit range should not have a leading zero")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_3digit_range_falls_through_to_4digit_range(self):
        # When 3-digit range is exhausted, should fall through to 4-digit range.
        bin_limits = [(900, 900), (4400, 4400)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=bin_limits, edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-9), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        # Fill all 10000 counters in the 3-digit range (09000000-09009999)
        for i in range(10000):
            CtrJGS8dig.all_8digit_counter.add(f'0900{i:04d}')
        # Should fall through to 4-digit range starting at 44000000
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertTrue(counter.startswith('4400'),
                        f"Expected counter to start with '4400' after 3-digit range exhaustion, got {counter}")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_5digit_range_falls_through_to_6digit_range(self):
        # When 5-digit range is exhausted, should fall through to 6-digit range.
        bin_limits = [(90050, 90050), (440050, 440050)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4400)], edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        # Fill all 100 counters in the 5-digit range (09005000-09005099)
        for i in range(100):
            CtrJGS8dig.all_8digit_counter.add(f'090050{i:02d}')
        # Should fall through to 6-digit range starting at 44005000
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertTrue(counter.startswith('440050'),
                        f"Expected counter to start with '440050' after 5-digit range exhaustion, got {counter}")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_7digit_edc_counter_range_produces_8digit_counter(self):
        # 7-digit range uses pad_len=8 and suffix_len=0 (else branch), producing a single padded 8-digit counter.
        # e.g. range (4400000, 4400000) -> str(4400000).zfill(8) = '04400000', no suffix appended.
        bin_limits = [(4400000, 4400000)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4400)], edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertEqual(counter, '04400000',
                         f"7-digit range (4400000,4400000) should produce counter '04400000', got {counter}")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_8digit_edc_counter_range_produces_exact_counter(self):
        # 8-digit range uses pad_len=8 and suffix_len=0 (else branch), producing the exact 8-digit counter.
        # e.g. range (44500000, 44500000) -> str(44500000).zfill(8) = '44500000', no suffix appended.
        bin_limits = [(44500000, 44500000)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4400)], edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        counter = CtrJGS8dig.get_unique_edc_ctr()
        self.assertEqual(counter, '44500000',
                         f"8-digit range (44500000,44500000) should produce counter '44500000', got {counter}")

    @patch('pymtpl.core.JGSdefault.default_ports', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_7digit_edc_counter_range_exhaustion(self):
        # A 7-digit range with a single value has exactly 1 counter (suffix_len=0).
        # After it is used, the next call should raise ErrorUser.
        bin_limits = [(4400000, 4400000)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4400)], edcportctrbinrange=bin_limits)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass(ctr=0))),
            ])
        PyMtpl().main_one(PyObj)
        CtrJGS8dig.all_8digit_counter.add('04400000')
        with self.assertRaisesRegex(ErrorUser, "No unique counter available"):
            CtrJGS8dig.get_unique_edc_ctr()

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_manual_counter_padded_to_8_digits(self):
        # Bug fix: a manually-specified 7-digit counter (e.g. ctr=1000000) must be
        # zero-padded to 8 digits in the IncrementCounters line:
        #   p01000000_pass_...   NOT   p1000000_pass_...
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(6400, 6401)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=98640000),
                           rm2=pFail(setbin=99640000),
                           r0=pFail(setbin=-64),
                           r1=pPass(setbinstring='b01000000_pass_TPI_BASE_SETBIN_X_PAUSE_K_FACT_X_X_X_X_PASS_1',
                                    ctr=1000000),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Counter must be padded to 8 digits: p01000000_pass_... not p1000000_pass_...
        self.assertIn('p01000000_pass_', mtpl_content)
        self.assertNotIn('p1000000_pass_', mtpl_content)

    def test_get_non_mtt_portctrstring_fail_same_bin(self):
        # ctrpassfail=="fail" and previous_bin==new_bin → reuses autoctrdict counter
        CtrJGS8dig.autoctrdict['Instance1'] = {'r0': '44000000'}
        Initialize.module_name = 'FUN'
        result = CtrJGS8dig._get_non_mtt_portctrstring('44000000', 'Instance1', 1, 'n', 'fail', 'r0')
        self.assertEqual(result, 'IncrementCounters FUN::n44000000_fail_Instance1_0')

    def test_get_non_mtt_portctrstring_fail_different_bin(self):
        # ctrpassfail=="fail" and previous_bin!=new_bin → uses new ctr value
        CtrJGS8dig.autoctrdict['Instance1'] = {'r0': '44000099'}
        Initialize.module_name = 'FUN'
        result = CtrJGS8dig._get_non_mtt_portctrstring('44000000', 'Instance1', 1, 'n', 'fail', 'r0')
        self.assertEqual(result, 'IncrementCounters FUN::n44000000_fail_Instance1_0')

    def test_update_non_mtt_ctr_duplicate_raises(self):
        # digit8 already in ctr_registry raises ErrorUser for duplicate counter
        CtrJGS8dig.ctr_registry['44000000'] = 'IncrementCounters FUN::n44000000_fail_Instance1_0'
        with self.assertRaisesRegex(ErrorUser, 'not unique'):
            CtrJGS8dig._update_non_mtt_ctr('44000000', 'Instance1', 1, 'r0', 'n', 'fail')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_setbinstring_shared_bin_auto_counter(self):
        # custom_setbinstring with _SHARED_BIN auto-derives counter via _get_counter_from_defaultrm12bin
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(9000, 9001)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(),
                           rm2=pFail(),
                           r0=pFail(setbinstring='b90984200_fail_SCN_A_CBB_SHARED_BIN_0'),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn('SetBin b90984200_fail_SCN_A_CBB_SHARED_BIN_0', readout)
        self.assertIn('IncrementCounters FUN::n90984200_fail_SCN_A_CBB_SHARED_COUNTER_0', readout)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_defaultrm1bin_rm2bin_allow_duplicate_counter(self):
        # Test that allow_duplicate = True is set when portid is rm1 or rm2
        # and defaultrm1bin/defaultrm2bin is set on Initialize.
        # populate_internal_ctr_trackers calls _confirm_no_duplicate_counters only when
        # port_obj.ctr > 0, so we set explicit ctr values on rm1/rm2.
        # Both instances use the same explicit counter on rm1 and rm2.
        # Without allow_duplicate=True the second fitem would raise "not unique" because
        # 98010001 was already added to all_8digit_counter by Instance1.
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401),
                                        defaultrm1bin=98010000, defaultrm2bin=99010000)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(ctr=98010001), rm2=pFail(ctr=99010001),
                                    r0=pFail(setbin=-64), r1=pPass())),
                VminTC(name="Instance2", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(ctr=98010001), rm2=pFail(ctr=99010001),
                                    r0=pFail(setbin=-64), r1=pPass())),
            ])

        # allow_duplicate=True suppresses the "not unique" error for rm1/rm2.
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertEqual(readout.count('IncrementCounters FUN::n98010001_fail_Instance1_n1'), 1)
        self.assertEqual(readout.count('IncrementCounters FUN::n98010001_fail_Instance2_n1'), 1)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_repeat_run_explicit_ctr_allows_duplicate_via_ctrdictfrommtpl(self):
        # Test that allow_duplicate = True is set via ctrdictfrommtpl on a repeat run.
        # Scenario: portid is r0 (not rm1/rm2), so the rm1/rm2 shortcut does not apply.
        # On the second run ctrdictfrommtpl is populated from the MTPL written by the first run.
        # Because the same explicit counter (64000001) is used on Instance1/r0 in both runs,
        # ctrdictfrommtpl[Instance1][r0] matches port_obj.ctr → allow_duplicate = True → no error.
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(), rm2=pFail(),
                                    r0=pFail(setbin=-64, ctr=64000001), r1=pPass()))])

        PyMtpl().main_one(PyObj)
        first_run_output = File('out.mtpl').read()
        self.assertIn('IncrementCounters FUN::n64000001_fail_Instance1_0', first_run_output)

        # Second run: same counter on same port. ctrdictfrommtpl is loaded from the MTPL.
        # r0 IS in ctrdictfrommtpl[Instance1] and counter matches the stored value
        # (64000001 == 64000001) → allow_duplicate=True is set → no ErrorUser raised.
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(), rm2=pFail(),
                                    r0=pFail(setbin=-64, ctr=64000001), r1=pPass()))])

        PyMtpl().main_one(PyObj1)
        self.assertEqual(File('out.mtpl').read(), first_run_output)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_new_port_not_in_ctrdictfrommtpl_unique_counter_succeeds(self):
        # Test that the portid-in-ctrdictfrommtpl check evaluates to False for a new port.
        # First run: Instance1 has only r0. ctrdictfrommtpl = {Instance1: {r0: 64000001}}.
        # Second run: r2 is added with a unique counter. When _confirm_no_duplicate_counters
        # runs for r2: Instance1 IS in ctrdictfrommtpl, but r2 is NOT in
        # ctrdictfrommtpl[Instance1] → portid check is False → allow_duplicate stays False.
        # Counter 64000002 is unique → confirm passes → no error, output updated.
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(), rm2=pFail(),
                                    r0=pFail(setbin=-64, ctr=64000001), r1=pPass()))])

        PyMtpl().main_one(PyObj)

        # Second run: r2 is a new port not recorded in ctrdictfrommtpl → portid check is False.
        # 64000002 is unique so the run succeeds and both counters appear in the output.
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(), rm2=pFail(),
                                    r0=pFail(setbin=-64, ctr=64000001),
                                    r2=pFail(setbin=-64, ctr=64000002),
                                    r1=pPass()))])

        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn('IncrementCounters FUN::n64000001_fail_Instance1_0', readout)
        self.assertIn('IncrementCounters FUN::n64000002_fail_Instance1_2', readout)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_counter_changed_to_unique_value_succeeds(self):
        # Test that the counter equality check evaluates to False when the counter value changes.
        # First run: Instance1 r0=ctr=64000001. ctrdictfrommtpl = {Instance1: {r0: 64000001}}.
        # Second run: counter changed to 64000099. In _confirm_no_duplicate_counters:
        # Instance1 IS in ctrdictfrommtpl, portid check is True (r0 IS in it),
        # but counter equality check is False (64000099 != 64000001) → allow_duplicate stays False.
        # 64000099 is unique → confirm passes → no error, output updated with new counter.
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(), rm2=pFail(),
                                    r0=pFail(setbin=-64, ctr=64000001), r1=pPass()))])

        PyMtpl().main_one(PyObj)
        self.assertIn('IncrementCounters FUN::n64000001_fail_Instance1_0', File('out.mtpl').read())

        # Second run: counter on r0 changed to 64000099. Counter equality check is False.
        # 64000099 is not yet in all_8digit_counter → confirm passes → output updated.
        class PyObj1:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(rm1=pFail(), rm2=pFail(),
                                    r0=pFail(setbin=-64, ctr=64000099), r1=pPass()))])

        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn('IncrementCounters FUN::n64000099_fail_Instance1_0', readout)
        self.assertNotIn('n64000001', readout)


class TestTestChipNonMTTBin(TestCase):
    # Unit tests for TestChipNonMTTBin binning strategy
    def setUp(self):
        Initialize.clear_all()

    def test_ignore_list_empty(self):
        # Test that ignore_list is empty for TC
        self.assertEqual(TestChipNonMTTBin.ignore_list, [])

    def test_default_thermal_reset_test_classes_empty(self):
        # Test that default_thermal_reset_test_classes is empty
        self.assertEqual(TestChipNonMTTBin.default_thermal_reset_test_classes, [])

    def test_sbdef_prohibited_lists_empty(self):
        # Test that sbdef_prohibited lists are empty (all bins allowed)
        self.assertEqual(TestChipNonMTTBin.sbdef_prohibited_hardbins, [])
        self.assertEqual(TestChipNonMTTBin.sbdef_prohibited_databins, [])

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_update_autosetbinstring_returns_empty(self):
        # Test that update_autosetbinstring returns empty string
        result = TestChipNonMTTBin.update_autosetbinstring(-44, 100, 'r0', 'TestName', True, 'pFail')
        self.assertEqual(result, '')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_non_mtt_autosetbinstring_returns_empty(self):
        # Test that _get_non_mtt_autosetbinstring returns empty string
        result = TestChipNonMTTBin._get_non_mtt_autosetbinstring(-44, 'TestName', True, 'r0', 100)
        self.assertEqual(result, '')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_get_new_bin_returns_0000(self):
        # Test that get_new_bin returns '0000' (TC does not need binning)
        result = TestChipNonMTTBin.get_new_bin(-44, 100)
        self.assertEqual(result, '0000')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_tc_with_initializetc_no_bins_generated(self):
        # Test that TC initialization with TestChipNonMTTBin doesn't generate bin statements
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(setbin=-44),
                           rm1=pFail(setbin=-44),
                           r0=pFail(setbin=-44),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # TC doesn't generate SetBin statements
        self.assertNotIn('SetBin', mtpl_content)
        # But should still have counters
        self.assertIn('IncrementCounters', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_tc_multiple_tests_no_bins(self):
        # Test that multiple tests with TC don't generate bins
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem(r0=pFail(setbin=-44))),
                VminTC(name="Instance3", EndVoltageLimits="0.7",
                       _fitem=Fitem(r0=pFail(setbin=-44))),
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Verify no SetBin statements
        self.assertNotIn('SetBin', mtpl_content)
        # Verify all instances are present
        self.assertIn('Instance1', mtpl_content)
        self.assertIn('Instance2', mtpl_content)
        self.assertIn('Instance3', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_tc_inheritance_from_dmrhdclass(self):
        # Test that TestChipNonMTTBin inherits from JGSClass correctly
        self.assertTrue(issubclass(TestChipNonMTTBin, JGSClass))
        # Test that parent class methods are available but overridden
        self.assertTrue(hasattr(TestChipNonMTTBin, 'get_new_bin'))
        self.assertTrue(hasattr(TestChipNonMTTBin, 'update_autosetbinstring'))

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_tc_manual_setbin_properly_handled(self):
        # Test that TC with manual setbin=12345678 generates proper SetBin with manual value
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(setbin=-44),
                           rm1=pFail(setbin=-44),
                           r0=pFail(setbin=12345678),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Manual setbin should generate SetBin statement with the manual value
        self.assertIn('SetBin b12345678_fail_FUN_Instance1_0', mtpl_content)
        # Should also have counters
        self.assertIn('IncrementCounters', mtpl_content)
        self.assertIn('fail_Instance1_0', mtpl_content)


class TestCtrTestChip(TestCase):
    # Unit tests for CtrTestChip counter strategy
    def setUp(self):
        Initialize.clear_all()

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_get_portstring_rm_ports(self):
        # Test _get_portstring for rm1 and rm2 ports
        self.assertEqual(CtrTestChip._get_portstring('rm1'), 'n1')
        self.assertEqual(CtrTestChip._get_portstring('rm2'), 'n2')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_get_portstring_r_ports(self):
        # Test _get_portstring for regular r ports
        self.assertEqual(CtrTestChip._get_portstring('r0'), '0')
        self.assertEqual(CtrTestChip._get_portstring('r1'), '1')
        self.assertEqual(CtrTestChip._get_portstring('r10'), '10')
        self.assertEqual(CtrTestChip._get_portstring('r63'), '63')
        self.assertEqual(CtrTestChip._get_portstring('r102'), '102')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_counter_format_without_manual_ctr(self):
        # Test counter format: fail_MODULENAME_TESTNAME_PORTNUM
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-44),
                           rm2=pFail(setbin=-44),
                           r0=pFail(setbin=-44),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Check counter format: fail_Instance1_n1, fail_Instance1_n2, fail_Instance1_0
        self.assertIn('fail_Instance1_n1', mtpl_content)
        self.assertIn('fail_Instance1_n2', mtpl_content)
        self.assertIn('fail_Instance1_0', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_counter_format_with_pass_port(self):
        # Test counter format for pass port: pass_MODULENAME_TESTNAME_PORTNUM
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           r0=pFail(setbin=-44),
                           r1=pPass(),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Check pass counter format
        self.assertIn('pass_Instance1_1', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_multiple_ports_different_counters(self):
        # Test that different ports get different counters
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-44),
                           rm2=pFail(setbin=-44),
                           r0=pFail(setbin=-44),
                           r2=pFail(setbin=-44),
                           r10=pFail(setbin=-44),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Verify all ports have unique counters
        self.assertIn('fail_Instance1_n1', mtpl_content)
        self.assertIn('fail_Instance1_n2', mtpl_content)
        self.assertIn('fail_Instance1_0', mtpl_content)
        self.assertIn('fail_Instance1_2', mtpl_content)
        self.assertIn('fail_Instance1_10', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_multiple_tests_separate_counters(self):
        # Test that different tests get separate counters
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44))),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem(r0=pFail(setbin=-44))),
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Each test should have its own counter
        self.assertIn('fail_Instance1_0', mtpl_content)
        self.assertIn('fail_Instance2_0', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_get_new_bin_returns_zeros(self):
        # Test that get_new_bin returns '00000000' (TC does not need binning)
        result = CtrTestChip.get_new_bin(-44, 100)
        self.assertEqual(result, '00000000')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_inheritance_from_ctrdmrhd8dig(self):
        # Test that CtrTestChip inherits from CtrJGS8dig
        self.assertTrue(issubclass(CtrTestChip, CtrJGS8dig))

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_counter_format_complete_mtpl(self):
        # Test complete MTPL generation with TC counter format
        class PyObj:
            output = InitializeTestChip('out', 'TestChip', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="VminTest", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-44),
                           rm2=pFail(setbin=-44),
                           r0=pFail(setbin=-44),
                           r1=pPass(),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()

        # Verify counter format in output
        self.assertIn('IncrementCounters TestChip::fail_VminTest_n1', mtpl_content)
        self.assertIn('IncrementCounters TestChip::fail_VminTest_n2', mtpl_content)
        self.assertIn('IncrementCounters TestChip::fail_VminTest_0', mtpl_content)
        self.assertIn('IncrementCounters TestChip::pass_VminTest_1', mtpl_content)

        # Verify no SetBin statements (TC doesn't use bins)
        self.assertNotIn('SetBin', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_counter_in_counter_definition_section(self):
        # Test that counters appear in the flow (TC with usebinctrfrommtpl doesn't generate Counter Definition section)
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           r0=pFail(setbin=-44),
                           r1=pPass(),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()

        # TC with usebinctrfrommtpl doesn't generate Counter Definition section
        # but counters should still be used in IncrementCounters statements
        self.assertIn('IncrementCounters', mtpl_content)
        self.assertIn('fail_Instance1_0', mtpl_content)
        self.assertIn('pass_Instance1_1', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_extract_port_number_inherited(self):
        # Test that _extract_port_number is inherited from BaseCounter
        self.assertTrue(hasattr(CtrTestChip, '_extract_port_number'))
        # Verify functionality through _get_portstring which uses it
        self.assertEqual(CtrTestChip._get_portstring('rm1'), 'n1')
        self.assertEqual(CtrTestChip._get_portstring('r63'), '63')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_manual_counter_format(self):
        # Test counter format with manual ctr=12345678
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(setbin=-44),
                           rm2=pFail(setbin=-44),
                           r0=pFail(setbin=-44, ctr=12345678),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Manual counter should be used with proper format
        self.assertIn('n12345678_fail_Instance1_0', mtpl_content)
        # Verify no SetBin statements (TC doesn't use bins)
        self.assertNotIn('SetBin', mtpl_content)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
