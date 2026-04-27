#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for methods
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from pymtpl.core import *
from pymtpl.binctr import BaseBin, BinSSB, BaseCounter, CtrHBSB
import pymtpl.core as core
from main.pymtpl import PyMtplArgs
from pymtpl.test.methods import VminTC
from unittest.mock import patch, MagicMock
from pymtpl.helpers import Compact
from pymtpl.test.test_binctr import TestCommon
import sys
import os
import json


class MyPrimeMethod(BaseMethod):

    def __init__(self,
                 name,
                 PinNames=required,
                 UpperTolerance=optional,
                 traditional=None,
                 someparam=required,
                 **kwargs):
        self._init(name, locals())


class TestPrimeMethod(TestCase):

    def test_integrate(self):
        # integration test
        cmd = f'pymtpl.py {UT_DIR_REPO}/pymtpl/simple3.py'
        with MockVar(sys, "argv", cmd.split()):
            with TempDir(name=True, chdir=True) as tdir:
                PyMtplArgs().main()
                self.assertGoldEqual('Modules/FUN_CCF/fun_ccf.mtpl',
                                     f'{UT_DIR_REPO}/pymtpl/simple3.mtpl.gold')

    @with_(TempDir, chdir=True)
    def test_invalid_port(self):

        with self.assertRaisesRegex(ErrorUser, 'Invalid portid .q1'):
            Fitem('SAME', None, q1=pPass(ret=1))

        with self.assertRaisesRegex(ErrorUser, 'rm0 is not allowed'):
            Fitem('SAME', None, rm0=pPass(ret=1))

        with self.assertRaisesRegex(ErrorUser, 'Unknown portid'):
            BasePort._key2num('q1')

        # string instead of a Port object
        with self.assertRaisesRegex(ErrorUser, 'Expecting pPass'):
            Fitem('SAME', None, r1='something')

    def test_noargs(self):
        # integration test
        cmd = f'pymtpl.py'
        with MockVar(sys, "argv", cmd.split()):
            with self.assertRaises(ErrorInput):
                PyMtplArgs().main()

    @with_(TempDir, chdir=True)
    def test_invalid_fitem(self):

        with self.assertRaisesRegex(ErrorInput, 'expecting Fitem.. object'):

            class PyObj:
                output = Initialize('out', 'FUN')
                test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', pFail(ret=-1))

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.core.BaseMethod.write_lines', MagicMock())
    @with_(TempDir, chdir=True)
    def test_edc_fitem(self):
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, edc=True,
                                 r0=pFail(ctr=45200000, setbin=90454520, goto='Test3_item'),
                                 r1=pPass(ret=1),
                                 r2=pFail(ctr=45200001, setbin=90454520, goto='Test3_item')),
                           Fitem('Test2_item', test2,
                                 r0=pFail(ctr=45200002, setbin=90454520, ret=0)),
                           Fitem('Test3_item', test2, edc=True,
                                 r1=pPass()))
        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1 @EDC
    {
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b90454520_fail_FUN_Instance1;
            IncrementCounters FUN::n45200000_fail_Instance1_0;
            GoTo Test3_item;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b90454520_fail_FUN_Instance1;
            IncrementCounters FUN::n45200001_fail_Instance1_2;
            GoTo Test3_item;
        }
    }

    DUTFlowItem Test2_item Instance2
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90454520_fail_FUN_Instance1_SHARED_BIN;
            IncrementCounters FUN::n45200002_fail_Instance2_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Test3_item;
        }
    }

    DUTFlowItem Test3_item Instance2_1 @EDC
    {
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
    def test_next_fitem(self):

        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            test2 = VminTC(name="Instance2")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(goto="NEXT")),
                           Fitem('SAME', test2, r0=pFail(goto="NEXT")))

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            GoTo Instance2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2
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

    @with_(TempDir, chdir=True)
    def test_headers(self):

        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            test2 = VminTC(name="Instance2")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1),
                           Fitem('SAME', test2))

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC Instance1
{
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)


class TestRoutines(TestCase):

    def test_baseclass_bin(self):
        # purely for coverage
        with self.assertRaisesRegex(Exception, 'subclass'):
            BaseBin.convert_4digit_to_8digit('4444')
        with self.assertRaisesRegex(Exception, 'subclass'):
            BaseBin.convert_8digit_to_4digit('88888888')
        with self.assertRaisesRegex(Exception, 'subclass'):
            BaseBin.get_var_name()
        with self.assertRaisesRegex(Exception, 'subclass'):
            BaseBin.get_new_bin('0', 44, [])

    @with_(TempDir, chdir=True)
    def test_importorder(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            Import('ZZZ.usrv')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Floating('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import ZZZ.usrv;
Import VminTC.xml;

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_import(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            Import("SCN_Uservar.usrv")
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import SCN_Uservar.usrv;
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
    def test_import_fail(self):
        with self.assertRaisesRegex(ErrorUser, 'expecting string'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN')
                Import(1)
                test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_mtpl_comment(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            MtplComment("This is a mtpl comment")
            MtplComment("This is a new mtpl comment")
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# BEGIN MTPL COMMENT SECTION

# This is a mtpl comment
# This is a new mtpl comment

# END MTPL COMMENT SECTION

Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
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
    def test_no_Initialize(self):
        Initialize.clear_all()
        BaseMethod.clear_names()

        with self.assertRaisesRegex(ErrorUser, 'No Initialize statement found'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

    @with_(TempDir, chdir=True)
    def test_initialize_bom(self):
        tdir = os.getcwd()
        File('BaseTestPlan.tpl').touch()
        File('POR_TP/Class_NVL_S52C/EnvironmentFile.env').touch(mkdir=True)
        File('POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)

        # default - first one found
        Initialize.clear_all()
        Initialize('ABC', 'ABC')
        res = Initialize.get_tpobj()
        self.assertEqual(os.path.normpath(res.tpldir), os.path.normpath(f'{tdir}/POR_TP/Class_NVL_S28C'))

        # specified bom - found
        Initialize.clear_all()
        Initialize('ABC', 'ABC', bom='*52*')
        res = Initialize.get_tpobj()
        self.assertEqual(os.path.normpath(res.tpldir), os.path.normpath(f'{tdir}/POR_TP/Class_NVL_S52C'))

        # specified bom - not found - must be exact match if no wildcard
        Initialize.clear_all()
        Initialize('ABC', 'ABC', bom='52')
        with self.assertRaisesRegex(ErrorUser, 'Found 0 env file'):
            Initialize.get_tpobj()

        Initialize.clear_all()   # Clear it for next one

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_run(self):
        File('a.py').touch('''
# Import the necessary classes from Pymtpl
from pymtpl.por_methods import VminTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, MultiTrial, AUTO, MTLdefault, Initialize, Import, TrialParamSpec, Spec

# Initialize the module by defining the output mtpl path and the module name
Initialize('FUN_CCF_C68', 'FUN_CCF_C68')

# Define your test info and flow info
sample_test = VminTC(
    name = "SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X",
    EndVoltageLimits = "0.9",                                          # string (with quotes in output)
    FailCaptureCount = 9999,                                           # number (without quotes in output)
    ScoreboardEdgeTicks = Spec('toInteger(Specs.SCR_EDGE_TICK)'),      # expression (without quotes in output)
    _fitem = Fitem(r0=pFail(setbin=4500, ret=0))
    )

# Call your test in a DUTFlow
Flow('SCLRF1', sample_test)
''')
        # pymtpl direct run
        with MockVar(core, 'CALLERBIN', f'{ROOT_ENV}/main/pymtpl.py'):
            PyMtpl.run('a.py', 'POR_TP/TGLH81/EnvironmentFile.env')
        self.assertEqual(exists('FUN_CCF_C68.mtpl'), True)

        # qgate run
        File('FUN_CCF_C68.mtpl').unlink()
        with MockVar(core, 'CALLERBIN', f'{ROOT_ENV}/qgates/blah.py'):
            PyMtpl.run('a.py', 'POR_TP/TGLH81/EnvironmentFile.env')
        self.assertEqual(exists('FUN_CCF_C68.mtpl'), True)

        # unittest run
        File('FUN_CCF_C68.mtpl').unlink()
        PyMtpl.run('a.py', 'POR_TP/TGLH81/EnvironmentFile.env')
        self.assertEqual(exists('FUN_CCF_C68.mtpl'), True)

    @with_(TempDir, chdir=True)
    def test_initialize_bindefovrd(self):
        # Test overriding hardbin and softbin names in bindefdict using bindefovrd param and using bindefdefaults in the DMRdefaults class.

        # Save original state
        original_bindefdefaults = None
        if NVLdefault and NVLdefault.bindefdefaults is not None:
            original_bindefdefaults = NVLdefault.bindefdefaults.copy()

        # overriding defaults to test
        try:
            NVLdefault.bindefdefaults = {
                # hardbin overrides
                "98": "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN",
                "99": "b99_FAIL_HARDWARE_ERROR",
                # softbin overrides
                "9801": "9801_FAIL_TESTCLASS_EXCEPTION_ERROR"
            }

            Initialize.clear_all()

            bin_limits = [(9801, 9802), (9901, 9902), (6800, 6800), (6700, 6700)]

            class PyObj:
                output = InitializeNVLClass('ABC', 'ABC', defaults=NVLdefault, binrange=bin_limits,
                                            bindefovrd={
                                                # overriding hardbin names
                                                "68": "b68_FAIL_MIO_DDR",
                                                # example softbin override
                                                "9802": "9802_B98_OVERRIDE_NAME",
                                                "6700": "6700_FAIL_ARBITRARY_NAME",
                                                "123929323": "invalid_but_is_ignored"
                                            }
                                            )
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', edc=False,
                                        r0=pFail(setbin=-67),
                                        r3=pFail(setbin=-68),
                                        r2=pFail(setbin=-68)))])

            PyMtpl().main_one(PyObj)

            self.assertTextEqual(Initialize.bindefdict["98"], "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN")  # changed hb in defaults
            self.assertTextEqual(Initialize.bindefdict["99"], "b99_FAIL_HARDWARE_ERROR")  # changed hb in defaults
            self.assertTextEqual(Initialize.bindefdict["9801"], "9801_FAIL_TESTCLASS_EXCEPTION_ERROR")  # changed sb in defaults
            self.assertTextEqual(Initialize.bindefdict["68"], "b68_FAIL_MIO_DDR")  # changed hb in bindefovrd
            self.assertTextEqual(Initialize.bindefdict["9802"], "9802_B98_OVERRIDE_NAME")  # changed sb in bindefovrd - it even added a key
            self.assertTextEqual(Initialize.bindefdict["67"], "b67_FAIL_MISSING_VISUAL_ID_2D_MARK")  # unchanged hb
            self.assertTextEqual(Initialize.bindefdict["6700"], "6700_FAIL_ARBITRARY_NAME")  # changed sb

            expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup SoftBins
    {
        Bin b6700_FAIL_ARBITRARY_NAME    6700    : "b6700_FAIL_ARBITRARY_NAME",    b67_FAIL_MISSING_VISUAL_ID_2D_MARK;
    }

    BinGroup DataBins
    {
        LeafBin b90670000_fail_ABC_Instance1    90670000    : "b90670000_fail_ABC_Instance1",    b6700_FAIL_ARBITRARY_NAME;
    }

}
'''
            # make sure the sbdefs are right
            self.assertTextEqual(File('ABC_SubBinDefinitions.sbdefs').read(), expect)
        finally:
            NVLdefault.bindefdefaults = original_bindefdefaults  # Restore original state


class TestNativeMultiTrial(TestCase):

    def setUp(self):
        Initialize.clear_all()

    @with_(TempDir, chdir=True)
    def test_multitrial_initialization(self):
        # Test initialization of MultiTrial
        with MockVar(core, 'IS_UT', False), self.assertRaisesRegex(ErrorUser, 'TOS4 does not support the use of MultiTrial Test class'):
            class PyObj:
                output = InitializeNVLClass('out', 'FUN')
                print(Initialize.default_class)
                test1 = MultiTrial(name="MTTtname", template=VminTC(name="Instance1"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1))
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_nativemultitrial_write_lines(self):
        # Test write_lines method of MultiTrial
        class PyObj:
            output = InitializeNVLClass('out', 'FUN')
            test1 = NativeMultiTrial(name="MTTtname",
                                     _comment='I am mtt',
                                     template=VminTC(name="Instance1",
                                                     _comment="VminTC comment",
                                                     EndVoltageLimits="0.9"),
                                     r0=pFail(setbin=AUTO,
                                              ret=0,
                                              trialaction="Exit"),
                                     r2=pFail(setbin=4427,
                                              ret=2,
                                              trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90442700), r2=pFail(setbin=90442700)))

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
            SetBin b90442700_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90442700_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270001_fail_MTTtname_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_mismatch_port_mtt(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = NativeMultiTrial(name="MTTtname",
                                     _comment='I am mtt',
                                     template=VminTC(name="Instance1",
                                                     _comment="VminTC comment",
                                                     EndVoltageLimits="0.9"),
                                     r0=pFail(setbin=90444427,
                                              ret=0,
                                              trialaction="Exit"))
            test2 = NativeMultiTrial(name="MTTtname1",
                                     _comment='I am mtt',
                                     edcexitaction='Continue',
                                     template=VminTC(name="Instance2",
                                                     _comment="VminTC comment",
                                                     EndVoltageLimits="0.9"),
                                     r0=pFail(setbin=90444427,
                                              ret=0,
                                              trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True), Fitem('SAME', test2, edc=True, r0=pFail(setbin=90444427)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'do not match the ports'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_mismatch_port_fitem(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = NativeMultiTrial(name="MTTtname",
                                     _comment='I am mtt',
                                     template=VminTC(name="Instance1",
                                                     _comment="VminTC comment",
                                                     EndVoltageLimits="0.9"))
            test2 = NativeMultiTrial(name="MTTtname1",
                                     _comment='I am mtt',
                                     edcexitaction='Continue',
                                     template=VminTC(name="Instance2",
                                                     _comment="VminTC comment",
                                                     EndVoltageLimits="0.9"),
                                     r0=pFail(setbin=4427,
                                              ret=0,
                                              trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True), Fitem('SAME', test2, edc=True, r0=pFail(setbin=90444427), r2=pFail(setbin=90444427)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'do not match the ports'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_mismatch_port_mtt_fitem(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = NativeMultiTrial(name="MTTtname",
                                     _comment='I am mtt',
                                     template=VminTC(name="Instance1",
                                                     _comment="VminTC comment",
                                                     EndVoltageLimits="0.9"))
            test2 = NativeMultiTrial(name="MTTtname1",
                                     _comment='I am mtt',
                                     edcexitaction='Continue',
                                     template=VminTC(name="Instance2",
                                                     _comment="VminTC comment",
                                                     EndVoltageLimits="0.9"),
                                     r0=pFail(setbin=4427,
                                              ret=0,
                                              trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True), Fitem('SAME', test2, edc=True, r2=pFail(setbin=90444427)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'do not match the ports'):
            PyMtpl().main_one(PyObj)


class TestInstance(TestCase):

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_basic(self):
        # test case: blah must be ignored and both optional and required are given
        obj = MyPrimeMethod('tdau_test', PinNames='TDO', UpperTolerance="30", traditional='1', blah="something")
        self.assertEqual(obj.params, {'name': 'tdau_test',
                                      'PinNames': 'TDO',
                                      'UpperTolerance': '30',
                                      'someparam': required,
                                      'traditional': '1'
                                      })

        # test case: optional and required are written
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            obj = MyPrimeMethod('tdau_test2', PinNames='', UpperTolerance='', traditional='', blah='', someparam='')
            subflow = Floating('Floating', Fitem('SAME', obj))
            PyMtpl.write()
            # End of "python mtpl code"

        expect = '''
Test MyPrimeMethod tdau_test2
{
    PinNames = "";
    UpperTolerance = "";
    someparam = "";
    traditional = "";
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        # test case: optional and required are not written
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            obj = MyPrimeMethod('tdau_test2')
            subflow = Floating('Floating', Fitem('SAME', obj))
            PyMtpl.write()
            # End of "python mtpl code"

        expect = '''
Test MyPrimeMethod tdau_test2
{
    someparam = "1";
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_mtt(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4427,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4427), r2=pFail(setbin=4427)))
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
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        # 2nd case - Combined Option, should be same output
        class PyObj2:
            # Start of the "python mtpl code" ====================
            output = Initialize('out2', 'FUN')
            subflow = Flow('SubFlow1', [
                MultiTrial(name="MTTtname",
                           exitaction="Continue",
                           _comment='I am mtt',
                           template=VminTC(name="Instance1",
                                           _comment="VminTC comment",
                                           EndVoltageLimits="0.9"),
                           r0=pFail(setbin=AUTO,
                                    ret=0,
                                    trialaction="Exit"),
                           r2=pFail(setbin=90444427,
                                    ret=2,
                                    trialaction="Exit"),
                           _fitem=Fitem('SAME', r0=pFail(setbin=4427), r2=pFail(setbin=4427)))])
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj2)
        self.assertTextEqual(File('out2.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_mtt_error(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0),
                               r2=pFail(setbin=4427,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4427), r2=pFail(setbin=4427)))
            # End of "python mtpl code"

        with self.assertRaisesRegex(ErrorUser, 'trialaction not defined'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_mtt_port6_and_above(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r6=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r28=pFail(setbin=4427,
                                         ret=2,
                                         trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r6=pFail(setbin=4427), r28=pFail(setbin=4427)))
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
        TrialResult 6
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
            Return 0;
        }
        TrialResult 28
        {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
            Return 2;
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
        Result 6
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
        Result 28
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_mtt_spec_trialaction(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction=Spec('TP_Rule.MTT_Rule("Next", "Exit")')),
                               r2=pFail(setbin=4427,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4427), r2=pFail(setbin=4427)))
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
        TrialResult 0
        {
            PassFail Fail;
            TrialAction TP_Rule.MTT_Rule("Next", "Exit");
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.MTTCtrNVLClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_mtt_NVLDefault(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4427,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90444427), r2=pFail(setbin=90444427)))
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
            SetBin "b" + FlowMatrix.bin + "4444_fail_FUN_MTTtname";
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
            SetBin "b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44440000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44440001_fail_MTTtname_2;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_basic_mtt_NVLDefault_trialvar(self):
        with MockVar(core, 'IS_UT', False), MockVar(core.OPT, 'env', f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/POR_TP/Class_ARL_S68/EnvironmentFile.env'), self.assertRaisesRegex(ErrorUser, 'users to manually define the trialvar value'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = InitializeNVLClass('out', 'FUN')
                test1 = NativeMultiTrial(name="MTTtname",
                                         _comment='I am mtt',
                                         template=VminTC(name="Instance1",
                                                         _comment="VminTC comment",
                                                         EndVoltageLimits="0.9"),
                                         r0=pFail(setbin=AUTO,
                                                  ret=0,
                                                  trialaction="Exit"),
                                         r2=pFail(setbin=4427,
                                                  ret=2,
                                                  trialaction="Exit"))
                subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90444427), r2=pFail(setbin=90444427)))

            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_param_order(self):
        # tests two initialize as well
        Initialize.clear_all()

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1",
                           Patlist='patlist',
                           LevelsTc='IP_PCH_BASE::gcd_all_bf_x_x_ippch_lvl_nom_lvl',
                           TimingsTc='IP_PCH_BASE::gcd_dftring_timing_tclk100_dclk400_cclk400',
                           LogLevel=Spec('blah.LogLevel'),
                           BypassPort=-1)
            subflow = Floating('SubFlow1', Fitem('SAME', test1))

            output = Initialize('out2', 'FUN', paramorder='BypassPort'.split())
            subflow = Floating('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    Patlist = "patlist";
    LevelsTc = "IP_PCH_BASE::gcd_all_bf_x_x_ippch_lvl_nom_lvl";
    TimingsTc = "IP_PCH_BASE::gcd_dftring_timing_tclk100_dclk400_cclk400";
    BypassPort = -1;
    FailCaptureCount = 999;
    LogLevel = blah.LogLevel;
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        expect = '''
Test VminTC Instance1_1
{
    BypassPort = -1;
    FailCaptureCount = 999;
    LevelsTc = "IP_PCH_BASE::gcd_all_bf_x_x_ippch_lvl_nom_lvl";
    LogLevel = blah.LogLevel;
    Patlist = "patlist";
    TimingsTc = "IP_PCH_BASE::gcd_dftring_timing_tclk100_dclk400_cclk400";
}
'''
        self.assertTextEqual(File('out2.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_default_override(self):
        # Override default port
        class PyObj:
            output = InitializeMTL('out', 'FUN')
            test1 = VminTC(name="SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X",
                           _fitem=Fitem(rm2=pPass(ret=2),
                                        rm1=pFail(ret=3)))
            test2 = MultiTrial(name="MTTtname",
                               template=VminTC(name="Instance1"),
                               rm2=pPass(trialaction='Exit', ret=-22),
                               rm1=pPass(trialaction='Exit', ret=-11),
                               _fitem=Fitem()
                               )

            # Call your test in a DUTFlow
            Flow('SCLRF1', test1, test2)

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

Test VminTC SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X
{
    FailCaptureCount = 999;
}

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        FailCaptureCount = 999;
        TrialResult -2
        {
            PassFail Pass;
            TrialAction Exit;
            Return -22;
        }
        TrialResult -1
        {
            PassFail Pass;
            TrialAction Exit;
            Return -11;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
    }
}

DUTFlow SCLRF1
{
    DUTFlowItem SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X
    {
        Result -2
        {
            Property PassFail = "Pass";
            Return 2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            Return 3;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname;
        }
    }

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
        # print(File('out.mtpl').read())
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_default_port_basic_mtt(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out', 'FUN', binrange=(4400, 4450))
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=90444427,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90444427), r2=pFail(setbin=90444427)))
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
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        # 2nd case - Combined Option, should be same output
        class PyObj2:
            # Start of the "python mtpl code" ====================
            output = InitializeMTL('out2', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                MultiTrial(name="MTTtname",
                           exitaction="Continue",
                           _comment='I am mtt',
                           template=VminTC(name="Instance1",
                                           _comment="VminTC comment",
                                           EndVoltageLimits="0.9"),
                           r0=pFail(setbin=AUTO,
                                    ret=0,
                                    trialaction="Exit"),
                           r2=pFail(setbin=90444427,
                                    ret=2,
                                    trialaction="Exit"),
                           _fitem=Fitem('SAME', r0=pFail(setbin=4427), r2=pFail(setbin=4427)))])
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj2)
        self.assertTextEqual(File('out2.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_edc_mtt(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=4427,
                                        ret=0,
                                        trialaction="Exit"))
            test2 = MultiTrial(name="MTTtname1",
                               _comment='I am mtt',
                               edcexitaction='Continue',
                               template=VminTC(name="Instance2",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=4427,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True, r0=pFail(setbin=4427)), Fitem('SAME', test2, edc=True, r0=pFail(setbin=4427)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Restore;
    TrialTest VminTC Instance1
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            ##EDC## SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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

MultiTrialTest MTTtname1
{
    # I am mtt
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance2
    {
        # VminTC comment
        EndVoltageLimits = "0.9";
        FailCaptureCount = 999;
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            ##EDC## SetBin "SoftBins.b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname1";
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
    DUTFlowItem MTTtname MTTtname @EDC
    {
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            GoTo MTTtname1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname1;
        }
    }

    DUTFlowItem MTTtname1 MTTtname1 @EDC
    {
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b90444427_fail_FUN_MTTtname_SHARED_BIN;
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
    @with_(TempDir, chdir=True)
    def test_mismatch_port_mtt(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=90444427,
                                        ret=0,
                                        trialaction="Exit"))
            test2 = MultiTrial(name="MTTtname1",
                               _comment='I am mtt',
                               edcexitaction='Continue',
                               template=VminTC(name="Instance2",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=4427,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True), Fitem('SAME', test2, edc=True, r0=pFail(setbin=4427)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'do not match the ports'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_mismatch_port_fitem(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"))
            test2 = MultiTrial(name="MTTtname1",
                               _comment='I am mtt',
                               edcexitaction='Continue',
                               template=VminTC(name="Instance2",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=4427,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True), Fitem('SAME', test2, edc=True, r0=pFail(setbin=4427), r2=pFail(setbin=4427)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'do not match the ports'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_mismatch_port_mtt_fitem(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"))
            test2 = MultiTrial(name="MTTtname1",
                               _comment='I am mtt',
                               edcexitaction='Continue',
                               template=VminTC(name="Instance2",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=4427,
                                        ret=0,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, edc=True), Fitem('SAME', test2, edc=True, r2=pFail(setbin=4427)))
            # End of "python mtpl code"
        with self.assertRaisesRegex(ErrorUser, 'do not match the ports'):
            PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_basic_mtt_duplicate1(self):
        # The TrialName is not a string with quotes
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               exitaction="Continue",
                               template=VminTC(name="Instance1"),
                               r0=pFail(ret=0, trialaction="Exit"))
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=4427)),
                           Fitem('SAME', test1, r0=pFail(setbin=4427)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
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

MultiTrialTest MTTtname_1
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1 + "_1"
    {
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
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname_1;
        }
    }

    DUTFlowItem MTTtname_1 MTTtname_1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname_SHARED_BIN;
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
    def test_mtt_param_trialparam(self):
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = MultiTrial(name="MTTtname",
                               exitaction="Continue",
                               template=VminTC(name="Instance1",
                                               EndVoltageLimits=TrialParamSpec("BinMatrix.End_Voltage"),
                                               ForwardingMode=Spec('FUN_CORE_C68_Specs.Forwarding_Mode')),
                               r0=pFail(ret=0, trialaction="Exit"))
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, r0=pFail(setbin=4427)),
                           Fitem('SAME', test1, r0=pFail(setbin=4427)))

        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;

Import VminTC.xml;

# Test Counter Definition

Counters
{
    n44270001_fail_MTTtname_0,
    n44270002_fail_MTTtname_1_0
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = BinMatrix.End_Voltage;
        FailCaptureCount = 999;
        ForwardingMode = FUN_CORE_C68_Specs.Forwarding_Mode;
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

MultiTrialTest MTTtname_1
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1 + "_1"
    {
        TrialParam EndVoltageLimits = BinMatrix.End_Voltage;
        FailCaptureCount = 999;
        ForwardingMode = FUN_CORE_C68_Specs.Forwarding_Mode;
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
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270001_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo MTTtname_1;
        }
    }

    DUTFlowItem MTTtname_1 MTTtname_1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname_SHARED_BIN;
            IncrementCounters FUN::n44270002_fail_MTTtname_1_0;
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


class TestPort(TestCase):
    """ Testing port options """

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_goto_next_name_testmethod(self):
        """Verify goto next, name, testmethod"""
        class PyObj:
            output = Initialize('out', 'FUN')
            tests = []
            test1 = VminTC(name="Instance1", _fitem=Fitem())
            test2 = VminTC(name="Instance2", _fitem=Fitem(r0=pFail(goto='NEXT'),  # next instance, which is Instance1
                                                          r1=pFail(goto='Instance1'),  # Instance1 by name
                                                          r2=pFail(goto=test1)  # Instance1 by reference
                                                          ))
            tests.extend([test2, test1])
            subflow = Flow('SubFlow1', *tests)
        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance2
{
    FailCaptureCount = 999;
}

Test VminTC Instance1
{
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance2 Instance2
    {
        Result 0
        {
            Property PassFail = "Fail";
            GoTo Instance1;
        }
        Result 1
        {
            Property PassFail = "Fail";
            GoTo Instance1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            GoTo Instance1;
        }
    }

    DUTFlowItem Instance1 Instance1
    {
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
    @with_(TempDir, chdir=True)
    def test_goto_composite_reference(self):
        """Verify goto next, name, composite reference"""
        class PyObj:
            output = Initialize('out', 'FUN')
            tests = []
            test1 = VminTC(name="Instance1", _fitem=Fitem())
            composite = Fitem('SAME', Flow('CompositeFlow', test1))
            test2 = VminTC(name="Instance2", _fitem=Fitem(r0=pFail(goto='NEXT'),  # next instance, which is composite
                                                          r1=pFail(goto='CompositeFlow'),  # composite by name
                                                          r2=pFail(goto=composite)  # composite by reference (to fitem)
                                                          ))
            tests.extend([test2, composite])
            subflow = Flow('SubFlow1', *tests)
        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    FailCaptureCount = 999;
}

DUTFlow CompositeFlow
{
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

DUTFlow SubFlow1
{
    DUTFlowItem Instance2 Instance2
    {
        Result 0
        {
            Property PassFail = "Fail";
            GoTo CompositeFlow;
        }
        Result 1
        {
            Property PassFail = "Fail";
            GoTo CompositeFlow;
        }
        Result 2
        {
            Property PassFail = "Fail";
            GoTo CompositeFlow;
        }
    }

    DUTFlowItem CompositeFlow CompositeFlow
    {
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
    @with_(TempDir, chdir=True)
    def test_goto_wrong_types(self):
        """Verify goto throws errors when it's the wrong types"""

        for wrong_goto in [1, Flow('AFlow'), 1.0, pFail()]:
            class PyObj:
                output = Initialize('out', 'FUN')
                tests = []
                test1 = VminTC(name="Instance1", _fitem=Fitem())
                test2 = VminTC(name="Instance2", _fitem=Fitem(r0=pFail(goto=wrong_goto)))
                tests.extend([test2, test1])
                subflow = Flow('SubFlow1', *tests)
            with self.assertRaisesRegex(ErrorUser, "goto must be a"):
                PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_goto_wrong_name(self):
        """Verify goto throws errors when it's the wrong name"""

        for wrong_goto in ["Instance3", "Instance", "SAME", '']:
            class PyObj:
                output = Initialize('out', 'FUN')
                tests = []
                test1 = VminTC(name="Instance1", _fitem=Fitem())
                test2 = VminTC(name="Instance2", _fitem=Fitem(r0=pFail(goto=wrong_goto)))
                tests.extend([test2, test1])
                subflow = Flow('SubFlow1', *tests)
            with self.assertRaisesRegex(ErrorUser, "goto Flow Item name"):
                PyMtpl().main_one(PyObj)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_goto_wrong_flow(self):
        """Verify goto throws error when it's an fitem in another flow"""

        # by name
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", _fitem=Fitem())
            subflow = Flow('SubFlow1', test1)
            test2 = VminTC(name="Instance2", _fitem=Fitem(r0=pFail(goto="Instance1")))
            subflow2 = Flow('SubFlow2', test2)
        with self.assertRaisesRegex(ErrorUser, "goto Flow Item name"):
            PyMtpl().main_one(PyObj)

        # by reference
        class PyObj1:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", _fitem=Fitem())
            subflow = Flow('SubFlow1', test1)
            test2 = VminTC(name="Instance2", _fitem=Fitem(r0=pFail(goto=test1)))
            subflow2 = Flow('SubFlow2', test2)
        with self.assertRaisesRegex(ErrorUser, "goto Flow Item name"):
            PyMtpl().main_one(PyObj1)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_passing_port(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r2=pPass()))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
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

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_pfail_comment_appears_after_passfail_property(self):
        # Verify that a _comment on pFail is emitted after the PassFail property line inside Result block
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1",
                           _fitem=Fitem(edc=True,
                                        rm2=pFail(ret=-2,
                                                  _comment='CAKE_EXCLUDE_SOFTBINCHECK_NPORT_THIS_IS_DANGEROUS 2026_06_10 NHH This is deliberate to recover clamps from SDTSTRESS')))
            Flow('MAIN', test1)
        PyMtpl().main_one(PyObj)
        mtpl = File('out.mtpl').read()
        # Extract the specific Result -2 { ... } block to avoid false positives from other Result blocks
        result_block_match = re.search(r'Result -2\s*\{[^}]*\}', mtpl, re.DOTALL)
        self.assertIsNotNone(result_block_match, "Result -2 block not found in mtpl output")
        block = result_block_match.group(0)
        self.assertIn('Property PassFail = "Fail";', block)
        self.assertIn('# CAKE_EXCLUDE_SOFTBINCHECK_NPORT_THIS_IS_DANGEROUS 2026_06_10 NHH This is deliberate to recover clamps from SDTSTRESS', block)
        # Comment must appear after PassFail and before Return within this block
        comment_pos = block.index('# CAKE_EXCLUDE_SOFTBINCHECK_NPORT_THIS_IS_DANGEROUS')
        passfail_pos = block.index('Property PassFail = "Fail";')
        return_pos = block.index('Return -2;')
        self.assertGreater(comment_pos, passfail_pos)
        self.assertLess(comment_pos, return_pos)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_pfail_multiline_comment(self):
        # Verify that a list of comment strings each produce a separate # comment line
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1",
                           _fitem=Fitem(edc=True,
                                        rm2=pFail(ret=-2,
                                                  _comment=['First comment line', 'Second comment line'])))
            Flow('MAIN', test1)
        PyMtpl().main_one(PyObj)
        mtpl = File('out.mtpl').read()
        self.assertIn('# First comment line', mtpl)
        self.assertIn('# Second comment line', mtpl)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_no_comment_produces_no_hash_line(self):
        # Verify that omitting _comment does not produce any spurious # lines in the Result block
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1",
                           _fitem=Fitem(r1=pPass()))
            Flow('MAIN', test1)
        PyMtpl().main_one(PyObj)
        mtpl = File('out.mtpl').read()
        # The only # characters should be none inside a Result block
        import re
        result_block = re.search(r'Result 1\s*\{[^}]*\}', mtpl, re.DOTALL)
        self.assertIsNotNone(result_block)
        self.assertNotIn('#', result_block.group(0))

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_ppass_comment_appears_in_output(self):
        # Verify that _comment on pPass is also emitted correctly
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1",
                           _fitem=Fitem(r1=pPass(_comment='Pass port note')))
            Flow('MAIN', test1)
        PyMtpl().main_one(PyObj)
        mtpl = File('out.mtpl').read()
        self.assertIn('# Pass port note', mtpl)

    def test_comment_invalid_type_raises(self):
        # Verify that passing a non-string/non-list _comment raises an error
        with self.assertRaisesRegex(ErrorUser, "_comment must be a string or sequence of strings"):
            pFail(ret=0, _comment=123)

    @with_(TempDir, chdir=True)
    def test_basic_full(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(ret=0, _comment="Test Comment")))
            # End of "python mtpl code"

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
        Result 0
        {
            Property PassFail = "Fail";
            # Test Comment
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


class TestDefaults(TestCase):
    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    def test_default_sbdef_name(self):
        self.assertEqual(BaseDefault.get_subbindef_name('MIO_DDR'), 'MIO_DDR_SubBinDefinitions.sbdefs')

    @with_(TempDir, chdir=True)
    def test_write_softbins_to_sbdef(self):
        # Test preventing softbins from being written to sbdefs file using write_softbins_to_sbdef=False.

        Initialize.clear_all()
        # Save original state
        orig_write_softbins_to_sbdef = None
        if NVLdefault and NVLdefault.write_softbins_to_sbdef is not None:
            orig_write_softbins_to_sbdef = NVLdefault.write_softbins_to_sbdef
        # overriding defaults to test
        NVLdefault.write_softbins_to_sbdef = False

        try:
            class PyObj:
                output = InitializeNVLClass('ABC', 'ABC', defaults=NVLdefault, binrange=(6700, 6700))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(r0=pFail(setbin=-67)))
                ])

            PyMtpl().main_one(PyObj)

            expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup DataBins
    {
        LeafBin b90670000_fail_ABC_Instance1    90670000    : "b90670000_fail_ABC_Instance1",    b6700;
    }

}
'''
            # make sure the sbdefs are right
            self.assertTextEqual(File('ABC_SubBinDefinitions.sbdefs').read(), expect)
        finally:
            NVLdefault.write_softbins_to_sbdef = orig_write_softbins_to_sbdef  # Restore original state

    @with_(TempDir, chdir=True)
    def test_write_hardbins_to_sbdef(self):
        # Test writing hardbins to sbdefs file using write_hardbins_to_sbdef=True.

        Initialize.clear_all()
        # Save original state
        orig_write_hardbins_to_sbdef = None
        if NVLdefault and NVLdefault.write_hardbins_to_sbdef is not None:
            orig_write_hardbins_to_sbdef = NVLdefault.write_hardbins_to_sbdef
        # overriding defaults to test
        NVLdefault.write_hardbins_to_sbdef = True

        try:
            class PyObj:
                output = InitializeNVLClass('ABC', 'ABC', defaults=NVLdefault, binrange=(6800, 6800))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(r0=pFail(setbin=-68)))
                ])

            PyMtpl().main_one(PyObj)

            expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup HardBins
    {
        Bin b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA    68    : "b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA",    Fail;
    }

    BinGroup SoftBins
    {
        Bin b6800    6800    : "b6800",    b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA;
    }

    BinGroup DataBins
    {
        LeafBin b90680000_fail_ABC_Instance1    90680000    : "b90680000_fail_ABC_Instance1",    b6800;
    }

}
'''
            # make sure the sbdefs are right
            self.assertTextEqual(File('ABC_SubBinDefinitions.sbdefs').read(), expect)
        finally:
            NVLdefault.write_hardbins_to_sbdef = orig_write_hardbins_to_sbdef  # Restore original state

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm1_bin(self):
        with self.assertRaisesRegex(ErrorUser, "does not allow defaultrm1bin to be equal to -98 or -99"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm2_bin(self):
        with self.assertRaisesRegex(ErrorUser, "does not allow defaultrm2bin to be equal to -98 or -99"):
            class PyObj:
                output = InitializeNVLClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)


class TestNVLClassHBSBXXXXDefaults(TestCase):
    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    @with_(TempDir, chdir=True)
    def test_valid_single_tuple(self):
        """Test valid JSON with single tuple (1000, 2000)"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)
        self.assertEqual(result, [1000, 2000])

    @with_(TempDir, chdir=True)
    def test_valid_single_list(self):
        """Test valid JSON with single list [1000, 2000]"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [1000, 2000]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)
        self.assertEqual(result, [1000, 2000])

    @with_(TempDir, chdir=True)
    def test_valid_list_of_tuples(self):
        """Test valid JSON with list of tuples [(1000, 2000), (3000, 4000)]"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 2000), (3000, 4000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)
        self.assertEqual(result, [[1000, 2000], [3000, 4000]])

    @with_(TempDir, chdir=True)
    def test_valid_list_of_lists(self):
        """Test valid JSON with list of lists [[1000, 2000], [3000, 4000]]"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [[1000, 2000], [3000, 4000]]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)
        self.assertEqual(result, [[1000, 2000], [3000, 4000]])

    @with_(TempDir, chdir=True)
    def test_valid_multiple_ranges(self):
        """Test valid JSON with multiple ranges"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 2000), (3000, 4000), (5000, 6000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)
        self.assertEqual(result, [[1000, 2000], [3000, 4000], [5000, 6000]])

    @with_(TempDir, chdir=True)
    def test_missing_default_counter_range_key(self):
        """Test error when Default_Counter_Range key is missing"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Wrong_Key": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'defaultcounters file is missing "Default_Counter_Range" key'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_invalid_type_string(self):
        """Test error when Default_Counter_Range is a string"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": "1000,2000"}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range must be a tuple, list, or list of tuples/lists'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_invalid_type_integer(self):
        """Test error when Default_Counter_Range is an integer"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": 1000}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range must be a tuple, list, or list of tuples/lists'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_tuple_wrong_length_one_element(self):
        """Test error when tuple has only 1 element"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000,)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range must have exactly 2 elements'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_tuple_wrong_length_three_elements(self):
        """Test error when tuple has 3 elements"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000, 3000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range must have exactly 2 elements'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_wrong_length_one_element(self):
        """Test error when list has only 1 element"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [1000]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range must have exactly 2 elements for a single range'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_wrong_length_three_elements(self):
        """Test error when list has 3 elements"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [1000, 2000, 3000]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range must have exactly 2 elements for a single range'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_tuple_non_integer_values_strings(self):
        """Test error when tuple contains string values"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": ("1000", "2000")}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range values must be integers'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_tuple_non_integer_values_floats(self):
        """Test error when tuple contains float values"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000.5, 2000.5)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range values must be integers'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_non_integer_values_strings(self):
        """Test error when list contains string values"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": ["1000", "2000"]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range values must be integers'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_non_integer_mixed_types(self):
        """Test error when list contains mixed types"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [1000, "2000"]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range values must be integers'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_tuple_start_not_less_than_end_equal(self):
        """Test error when start equals end in tuple"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (2000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range start value must be less than end value'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_tuple_start_greater_than_end(self):
        """Test error when start > end in tuple"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (2000, 1000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range start value must be less than end value'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_start_not_less_than_end(self):
        """Test error when start >= end in list"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [3000, 1000]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range start value must be less than end value'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_of_ranges_wrong_length(self):
        """Test error when one range in list has wrong number of elements"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 2000, 3000), (4000, 5000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Each range in Default_Counter_Range must have exactly 2 elements'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_of_ranges_one_element(self):
        """Test error when one range has only 1 element"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000,), (3000, 4000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Each range in Default_Counter_Range must have exactly 2 elements'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_of_ranges_non_integer_values(self):
        """Test error when ranges contain non-integer values"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, "2000"), (3000, 4000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Range 0 values must be integers'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_of_ranges_second_range_non_integer(self):
        """Test error when second range contains non-integer values"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 2000), (3000, 4000.5)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Range 1 values must be integers'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_of_ranges_start_not_less_than_end(self):
        """Test error when start >= end in one of the ranges"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 2000), (4000, 3000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Range 1 start value must be less than end value'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_of_ranges_first_range_invalid(self):
        """Test error when first range has start >= end"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(2000, 2000), (3000, 4000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Range 0 start value must be less than end value'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_empty_list(self):
        """Test error when Default_Counter_Range is an empty list"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": []}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Default_Counter_Range must be a tuple, list, or list of tuples/lists'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_invalid_json_format(self):
        """Test error when JSON file is malformed"""
        file_path = "default_counter_dict.json"
        with open(file_path, 'w') as json_file:
            json_file.write('{"Default_Counter_Range": (1000, 2000')  # Missing closing brace

        with self.assertRaisesRegex(ErrorUser, 'defaultcounters file is not valid JSON'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_invalid_json_syntax(self):
        """Test error when JSON has syntax errors"""
        file_path = "default_counter_dict.json"
        with open(file_path, 'w') as json_file:
            json_file.write('{"Default_Counter_Range": [1000, 2000],}')  # Trailing comma

        with self.assertRaisesRegex(ErrorUser, 'defaultcounters file is not valid JSON'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_not_json_at_all(self):
        """Test error when file is not JSON"""
        file_path = "default_counter_dict.json"
        with open(file_path, 'w') as json_file:
            json_file.write('This is not JSON at all!')

        with self.assertRaisesRegex(ErrorUser, 'defaultcounters file is not valid JSON'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_list_of_ranges_with_invalid_type_in_list(self):
        """Test error when list of ranges contains invalid type"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 2000), "not a range", (5000, 6000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Each range in Default_Counter_Range must have exactly 2 elements'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_nested_list_invalid(self):
        """Test error when list has nested structure beyond expected"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [[(1000, 2000)]]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, 'Each range in Default_Counter_Range must have exactly 2 elements'):
            NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_valid_edge_case_large_numbers(self):
        """Test valid case with large numbers"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (99999999, 100000000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with self.assertRaisesRegex(ErrorUser, "values must be between 0 and 9999"):
            result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    @with_(TempDir, chdir=True)
    def test_valid_edge_case_zero_start(self):
        """Test valid case with zero as start value"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (0, 1000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)
        self.assertEqual(result, [0, 1000])

    @with_(TempDir, chdir=True)
    def test_valid_consecutive_ranges(self):
        """Test valid case with consecutive ranges"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 2000), (2000, 3000), (3000, 4000)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)
        self.assertEqual(result, [[1000, 2000], [2000, 3000], [3000, 4000]])

    @with_(TempDir, chdir=True)
    def test_tuple_negative_values(self):
        """Test error with negative values in tuple"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (-1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with self.assertRaisesRegex(ErrorUser, "values must be between 0 and 9999"):
            result = NVLClassdefaultHBSBXXXX._validate_and_load_default_counters(file_path)

    def test_default_sbdef_name(self):
        self.assertEqual(NVLClassdefaultHBSBXXXX.get_subbindef_name('MIO_DDR'), 'MIO_DDR_SubBinDefinitions.sbdefs')

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm1_bin(self):
        with self.assertRaisesRegex(ErrorUser, "does not allow defaultrm1bin to be equal to -98 or -99"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm2_bin(self):
        with self.assertRaisesRegex(ErrorUser, "does not allow defaultrm2bin to be equal to -98 or -99"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=-99)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_int_bin(self):
        with self.assertRaisesRegex(ErrorUser, "must be a -HB value"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=44)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_no_default_counters(self):
        with self.assertRaisesRegex(ErrorUser, "but defaultcounters to use are not defined"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=-44)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_input_range(self):
        with self.assertRaisesRegex(ErrorUser, "input range must have exactly 2 elements"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=(99441234, 99441235, 99441236))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_input_list_range(self):
        with self.assertRaisesRegex(ErrorUser, "list of ranges with only start and stop defined in the range"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=[(99441234, 99441235, 99441236)])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_bin_prefix(self):
        with self.assertRaisesRegex(ErrorUser, "New NVL Class binning strategy requires bins to be in the form of"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=(98441234, 98441235))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_bin_prefix_list_input(self):
        with self.assertRaisesRegex(ErrorUser, "New NVL Class binning strategy requires bins to be in the form of"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=[(98441234, 98441235)])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_error_bin_start_with_90(self):
        with self.assertRaisesRegex(ErrorUser, "cannot start with"):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultresetbin=(90984412, 90984418))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_input_bin_length_check_range(self):
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            with self.assertRaisesRegex(ErrorUser, "must be a 7 or 8 digit value"):
                class PyObj:
                    output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultresetbin=(819000, 819025))
                    subflow = Flow('SubFlow1', [
                        VminTC(name="Instance1", EndVoltageLimits="0.9",
                               _fitem=Fitem('SAME',
                                            rm1=pFail(),
                                            r0=pFail(setbin=AUTO),
                                            r2=pFail(setbin=801),
                                            r5=pFail(setbin=AUTO)))])

                PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_input_bin_start_less_than_stop_check(self):
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            with self.assertRaisesRegex(ErrorUser, "must be less than the end"):
                class PyObj:
                    output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultresetbin=(8190000, 8180025))
                    subflow = Flow('SubFlow1', [
                        VminTC(name="Instance1", EndVoltageLimits="0.9",
                               _fitem=Fitem('SAME',
                                            rm1=pFail(),
                                            r0=pFail(setbin=AUTO),
                                            r2=pFail(setbin=801),
                                            r5=pFail(setbin=AUTO)))])

                PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_input_bin_format_check(self):
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            with self.assertRaisesRegex(ErrorUser, "defaultresetbin must be a 7 or 8 digit value in the form of HB19XXXX"):
                class PyObj:
                    output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultresetbin=(974400, 974425))
                    subflow = Flow('SubFlow1', [
                        VminTC(name="Instance1", EndVoltageLimits="0.9",
                               _fitem=Fitem('SAME',
                                            rm1=pFail(),
                                            r0=pFail(setbin=AUTO),
                                            r2=pFail(setbin=801),
                                            r5=pFail(setbin=AUTO)))])

                PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_input_bin_same_prefix_range(self):
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            with self.assertRaisesRegex(ErrorUser, "do not share the same first 2 characters"):
                class PyObj:
                    output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultresetbin=(8190000, 9190250))
                    subflow = Flow('SubFlow1', [
                        VminTC(name="Instance1", EndVoltageLimits="0.9",
                               _fitem=Fitem('SAME',
                                            rm1=pFail(),
                                            r0=pFail(setbin=AUTO),
                                            r2=pFail(setbin=801),
                                            r5=pFail(setbin=AUTO)))])

                PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_set_rm1_ports(self):
        """Test error with negative values in tuple"""
        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=-44, defaultrm1bin=-44)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        r2=pFail(setbin=801),
                                        r4=pFail(setbin=AUTO)))])

            PyMtpl().main_one(PyObj)
            expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n8010000_fail_Instance1_2,
    n97081000_fail_Instance1_4
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
            SetBin b99441000_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441000_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b8010000_fail_FUN_Instance1_2;
            IncrementCounters FUN::n8010000_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97081000_fail_FUN_Instance1_4;
            IncrementCounters FUN::n97081000_fail_Instance1_4;
        }
    }

}

        '''
            self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_mtt_param_trialparam(self):

        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": (1000, 2000)}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            class PyObj:
                output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(800, 804), defaultrm2bin=-44, defaultrm1bin=-44)
                test1 = NativeMultiTrial(name="MTTtname",
                                         exitaction="Continue",
                                         template=VminTC(name="Instance1",
                                                         EndVoltageLimits=TrialParamSpec("BinMatrix.End_Voltage"),
                                                         ForwardingMode=Spec('FUN_CORE_C68_Specs.Forwarding_Mode')),
                                         r0=pFail(ret=0, trialaction="Exit"))
                subflow = Flow('SubFlow1',
                               Fitem('SAME', test1, r0=pFail(setbin=4427)),
                               Fitem('SAME', test1, r0=pFail(setbin=4427)))

            PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44270000_fail_MTTtname_0,
    n44270001_fail_MTTtname_1_0
} # End of Test Counter Definition

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = BinMatrix.End_Voltage;
        FailCaptureCount = 999;
        ForwardingMode = FUN_CORE_C68_Specs.Forwarding_Mode;
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

MultiTrialTest MTTtname_1
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1 + "_1"
    {
        TrialParam EndVoltageLimits = BinMatrix.End_Voltage;
        FailCaptureCount = 999;
        ForwardingMode = FUN_CORE_C68_Specs.Forwarding_Mode;
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
            SetBin b99441000_fail_FUN_MTTtname_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441000_fail_FUN_MTTtname_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44270000_fail_FUN_MTTtname_0;
            IncrementCounters FUN::n44270000_fail_MTTtname_0;
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
            SetBin b99441001_fail_FUN_MTTtname_1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98441001_fail_FUN_MTTtname_1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44270001_fail_FUN_MTTtname_1_0;
            IncrementCounters FUN::n44270001_fail_MTTtname_1_0;
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


class TestDefaults_Server(TestCase):
    # make sure everything is reset before each test.
    def setUp(self):
        Initialize.clear_all()

    def test_dmr_default_sbdef_name(self):
        self.assertEqual(DMRdefault.get_subbindef_name('MIO_DDR'), 'MIO_DDR.sbdefs')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.MTTCtrNVLClass8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_DMRdefault_default_ports_params(self):
        ret_dict = {}
        DMRdefault.default_ports(ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].setbin, -98)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].setbin, -99)

        ret_dict.clear()
        DMRdefault.default_ports(ret_dict, ti=Flow('Dummy'))
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].setbin, None)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].setbin, None)

        # make sure we don't have any default ports coming in from the base class
        self.assertEqual(DMRdefault.default_params(), {})

    @with_(TempDir, chdir=True)
    def test_dont_write_hardbins_or_softbins_to_sbdef_using_defaults(self):
        # Test NOT writing hardbins or softbins counter to what's in the base defaults
        # Save original state
        orig_write_hardbins_to_sbdef = None
        orig_write_softbins_to_sbdef = None
        if DMRdefault and DMRdefault.write_hardbins_to_sbdef is not None:
            orig_write_hardbins_to_sbdef = DMRdefault.write_hardbins_to_sbdef
        if DMRdefault and DMRdefault.write_softbins_to_sbdef is not None:
            orig_write_softbins_to_sbdef = DMRdefault.write_softbins_to_sbdef
        # overriding defaults to test
        DMRdefault.write_hardbins_to_sbdef = False
        DMRdefault.write_softbins_to_sbdef = False

        try:
            class PyObj:
                output = InitializeDMRClass('ABC', 'ABC', defaults=DMRdefault, binrange=(6800, 6800))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(
                               rm2=pFail(),
                               rm1=pFail(),
                               r0=pFail(setbin=-68),
                           ))
                ])

            PyMtpl().main_one(PyObj)

            expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup DataBins
    {
        LeafBin b90680000_fail_ABC_Instance1_0    90680000    : "b90680000_fail_ABC_Instance1_0",    b6800_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA;
    }

}
'''
            # make sure the sbdefs are right
            self.assertTextEqual(File('ABC.sbdefs').read(), expect)
        finally:
            DMRdefault.write_hardbins_to_sbdef = orig_write_hardbins_to_sbdef  # Restore original state
            DMRdefault.write_softbins_to_sbdef = orig_write_softbins_to_sbdef  # Restore original state

    @with_(TempDir, chdir=True)
    def test_dont_write_hardbins_or_softbins_to_sbdef_using_initialize(self):
        class PyObj:
            output = InitializeDMRClass('ABC', 'ABC', defaults=DMRdefault, binrange=(6800, 6800), writehardbinstosbdef=False, writesoftbinstosbdef=False)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                            rm2=pFail(),
                            rm1=pFail(),
                            r0=pFail(setbin=-68),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup DataBins
    {
        LeafBin b90680000_fail_ABC_Instance1_0    90680000    : "b90680000_fail_ABC_Instance1_0",    b6800_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA;
    }

}
'''
        # make sure the sbdefs are right
        self.assertTextEqual(File('ABC.sbdefs').read(), expect)

    @with_(TempDir, chdir=True)
    def test_write_hardbins_and_softbins_to_sbdef_using_initialize(self):
        class PyObj:
            output = InitializeDMRClass('ABC', 'ABC', defaults=DMRdefault, binrange=(6800, 6800), writehardbinstosbdef=True, writesoftbinstosbdef=True)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                            rm2=pFail(),
                            rm1=pFail(),
                            r0=pFail(setbin=-68),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup HardBins
    {
        Bin b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA    68    : "b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA",    Fail;
    }

    BinGroup SoftBins
    {
        Bin b6800_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA    6800    : "b6800_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA",    b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA;
    }

    BinGroup DataBins
    {
        LeafBin b90680000_fail_ABC_Instance1_0    90680000    : "b90680000_fail_ABC_Instance1_0",    b6800_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA;
    }

}
'''
        # make sure the sbdefs are right
        self.assertTextEqual(File('ABC.sbdefs').read(), expect)

    @with_(TempDir, chdir=True)
    def test_cbr_defaults_no_write_hbsb(self):
        class PyObj:
            output = InitializeCBRClass('ABC', 'ABC', binrange=(6800, 6800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                            rm2=pFail(),
                            rm1=pFail(),
                            r0=pFail(setbin=-68),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup DataBins
    {
        LeafBin b90680000_fail_ABC_Instance1_0    90680000    : "b90680000_fail_ABC_Instance1_0",    b6800_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA;
    }

}
'''
        # make sure the sbdefs are right
        self.assertTextEqual(File('ABC.sbdefs').read(), expect)

    @with_(TempDir, chdir=True)
    def test_CBRdefault_default_ports_params(self):
        ret_dict = {}
        CBRdefault.default_ports(ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].setbin, -98)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].setbin, -99)

        ret_dict.clear()
        CBRdefault.default_ports(ret_dict, ti=Flow('Dummy'))
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].setbin, None)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].setbin, None)

        # make sure we don't have any default ports coming in from the base class
        self.assertEqual(CBRdefault.default_params(), {})

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm1_bin(self):
        with self.assertRaisesRegex(ErrorUser, "equal to -98 or -99 is not allowed"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must be a -HB value"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must be an 8 digit value"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm1bin=98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm1bin='90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm1bin='b90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm2_bin(self):
        with self.assertRaisesRegex(ErrorUser, "equal to -98 or -99 is not allowed"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must be a -HB value"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=-98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must be an 8 digit value"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm2bin='90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm2bin='b90989090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        with self.assertRaisesRegex(ErrorUser, "Please use a valid value for default"):
            class PyObj:
                output = InitializeDMRClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=['test', 'array'])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_negbin(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = (6400, 6401)

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)

        # repeat just in case
        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b90990800_fail_FAIL_DPS_ALARM_n2", readout)
        self.assertIn("IncrementCounters FUN::n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n90990800_fail_FAIL_DPS_ALARM_n2", readout)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_negbin_34dig(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = [(6401, 6401), (805, 806)]

        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-6401, defaultrm2bin=-805)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)

        # repeat just in case
        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-6401, defaultrm2bin=-805)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b90990800_fail_FAIL_DPS_ALARM_n2", readout)
        self.assertIn("IncrementCounters FUN::n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n90990800_fail_FAIL_DPS_ALARM_n2", readout)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_posbin(self):
        """Test for defaultrmXbin with 8 digit positive bin value"""
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin=90981234, defaultrm2bin=90995678)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90981234_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b90995678_fail_FAIL_DPS_ALARM_n2", readout)
        self.assertIn("IncrementCounters FUN::n90981234_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n90995678_fail_FAIL_DPS_ALARM_n2", readout)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_directset(self):
        """Test for defaultrmXbin with a direct string set"""
        class PyObj:
            output = InitializeCBRClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b90981234_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b90995678_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90981234_FAIL_MIO_DDR_SHARED_BIN_n1", readout)
        self.assertIn("SetBin b90995678_fail_FUN_shared_bin_n2", readout)
        self.assertIn("IncrementCounters FUN::n90981234_FAIL_MIO_DDR_SHARED_COUNTER_n1", readout)
        self.assertIn("IncrementCounters FUN::n90995678_fail_FUN_shared_counter_n2", readout)

    @with_(TempDir, chdir=True)
    def test_default_ports_flow_rm1_already_set_not_overwritten(self):
        # Line 1653: 'rm1' not in ret_dict evaluates False - existing rm1 is not overwritten
        existing_rm1 = pFail(ret=-99)
        ret_dict = {'rm1': existing_rm1}
        DMRdefault.default_ports(ret_dict, ti=Flow('Dummy'))
        self.assertIs(ret_dict['rm1'], existing_rm1)
        self.assertIn('rm2', ret_dict)

    @with_(TempDir, chdir=True)
    def test_default_ports_flow_rm2_already_set_not_overwritten(self):
        # Line 1655: 'rm2' not in ret_dict evaluates False - existing rm2 is not overwritten
        existing_rm2 = pFail(ret=-88)
        ret_dict = {'rm2': existing_rm2}
        DMRdefault.default_ports(ret_dict, ti=Flow('Dummy'))
        self.assertIs(ret_dict['rm2'], existing_rm2)
        self.assertIn('rm1', ret_dict)


class TestCWFDefaults(TestCase):
    # make sure everything is reset before each test.

    def setUp(self):
        Initialize.clear_all()

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @with_(TempDir, chdir=True)
    def test_cwf_rm_port_counter(self):
        # Test that CWF does not generate counters for rm ports
        class PyObj:
            output = InitializeCWFClass('out', 'FUN', binrange=(6800, 6801))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-68, ctr=0)))])

        PyMtpl().main_one(PyObj)

        # Verify no counters are generated for rm1/rm2
        expect = '''
Test VminTC Instance1
{
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
            SetBin SoftBins.b90680000_fail_FUN_Instance1_0;
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
class TestTPTOS4(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic_tos4(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', tosversion="tos4")
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

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
    def test_basic_InitNVL(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVL('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

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
            SetBin b90999901_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90989801_fail_FAIL_SYSTEM_SOFTWARE;
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
    def test_basic_mtt_tos4(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN', tosversion='tos4')
            test1 = MultiTrial(name="MTTtname",
                               _comment='I am mtt',
                               template=VminTC(name="Instance1",
                                               _comment="VminTC comment",
                                               EndVoltageLimits="0.9"),
                               r0=pFail(setbin=AUTO,
                                        ret=0,
                                        trialaction="Exit"),
                               r2=pFail(setbin=4427,
                                        ret=2,
                                        trialaction="Exit"))
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4427), r2=pFail(setbin=4427)))
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
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
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
            SetBin "b" + FlowMatrix.bin + "4427_fail_FUN_MTTtname";
            Return 2;
        }
    }
}

Flow SubFlow1
{
    FlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90444427_fail_FUN_MTTtname;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90444427_fail_FUN_MTTtname;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)


@patch('pymtpl.core.PyMtpl._headers', MagicMock())
class TestTP(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
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
    def test_basic_flowloop(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, LoopCount="2", BreakLoopOn="[-2:-1]"))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1 LoopCount 2
    {
        BreakLoopOn [-2:-1];
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
    def test_basic_flowloop_edc(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, LoopCount="2", BreakLoopOn="[-2:-1]", edc=True))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1 LoopCount 2 @EDC
    {
        BreakLoopOn [-2:-1];
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
    def test_basic_minloopduration(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, MinLoopDuration="2", BreakLoopOn="[-2:-1]"))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1 MinLoopDuration 2
    {
        BreakLoopOn [-2:-1];
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
    def test_basic_minloopduration_edc(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, MinLoopDuration="2", BreakLoopOn="[-2:-1]", edc=True))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1 MinLoopDuration 2 @EDC
    {
        BreakLoopOn [-2:-1];
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
    def test_basic_minloopdur_error(self):
        # Good template to copy from
        with self.assertRaisesRegex(ErrorUser, 'MinLoopDuration is expecting string'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN')
                test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, MinLoopDuration=2, BreakLoopOn="[-2:-1]"))
                # End of "python mtpl code"
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_basic_both_minloopdur_and_loopct_error(self):
        # Good template to copy from
        with self.assertRaisesRegex(ErrorUser, 'Both LoopCount and MinLoopDuration are defined in the Fitem'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN')
                test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, MinLoopDuration="2", LoopCount="3", BreakLoopOn="[-2:-1]"))
                # End of "python mtpl code"
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_basic_loopcount_error(self):
        # Good template to copy from
        with self.assertRaisesRegex(ErrorUser, 'LoopCount is expecting string'):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN')
                test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, LoopCount=2, BreakLoopOn="[-2:-1]"))
                # End of "python mtpl code"
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_basic_dtag(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1), dtag="INIT")
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1 @INIT
{
    DUTFlowItem Instance1 Instance1
    {
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
    def test_repeat(self):
        # Good template to copy from
        counterdict = {
            "Instance1": {
                "r1": "90440000",
                "r2": "8010001",
                "r0": "44000001"
            },
            "Instance1_1": {
                "r0": "44000002",
                "r1": "90440002"
            }
        }
        os.makedirs("PymtplInputFiles")
        file_path = os.path.join("PymtplInputFiles", "FUN_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(counterdict, json_file, indent=4)

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
            test2 = VminTC(name="Instance1_1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90440000)),
                           Fitem('SAME', test2, r0=pFail(setbin=90440000)))
            # End of "python mtpl code"

        # PyMtpl().main_one(PyObj1)

        with CaptureStdoutLog() as p:
            PyMtpl().main_one(PyObj1)
        self.assertIn('NO UPDATE: No changes to out.mtpl', p.getvalue())

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tpobj(self):
        Initialize.clear_all()

        # via env file
        with MockVar(OPT, "env", 'POR_TP/TGLH81/EnvironmentFile.env'):
            tpobj = Initialize.get_tpobj()
            self.assertEqual(tpobj.envfile, f"{os.getcwd()}{os.path.normpath('/POR_TP/TGLH81/EnvironmentFile.env')}")

            # second time
            tpobj = Initialize.get_tpobj()
            self.assertEqual(tpobj.envfile, f"{os.getcwd()}{os.path.normpath('/POR_TP/TGLH81/EnvironmentFile.env')}")

        # via output
        Initialize.clear_all()
        Initialize('Modules/abc/outfile.py', 'FUN')
        tpobj = Initialize.get_tpobj()
        self.assertEqual(tpobj.envfile, f"{os.getcwd()}{os.path.normpath('/POR_TP/TGLH81/EnvironmentFile.env')}")

        # Error, none found
        with TempDir(chdir=True) as tdir:
            Initialize.clear_all()
            Initialize('Modules/abc/outfile.py', 'FUN')
            with self.assertRaisesRegex(ErrorUser, '0 env'):
                Initialize.get_tpobj()

    @with_(TempDir, chdir=True)
    def test_twomtpl_independent(self):
        # This tests two mtpl in one .py file

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Floating('Floating', Fitem('SAME', test1))

            output = Initialize('out2', 'FUN2')
            test1 = VminTC(name="Instance2", EndVoltageLimits="0.9")
            subflow = Floating('Floating', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)
        self.assertTextEqual(File('out2.mtpl').read(), expect.replace('Instance1', 'Instance2'))

        # check the generated files
        self.assertEqual(set(os.listdir('.')),
                         {'PymtplInputFiles', 'out.mtpl', 'out.flw', 'out2.mtpl', 'out2.flw'})

    @with_(TempDir, chdir=True)
    def test_twomtpl_shared(self):
        # This tests two mtpl in one .py file

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Floating('Floating', Fitem('SAME', test1))

            PyMtpl.write()      # Write out.mtpl

            Initialize.set_outfile('out2')
            # test1.params['EndVoltageLimits'] = '0.8'   # example
            # <more code can be added here>
            PyMtpl.write()      # Write out2.mtpl, however, bins and counters are not reset

            # =========== End of "python mtpl code"

        PyMtpl().main_one(PyObj)

        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)
        self.assertTextEqual(File('out2.mtpl').read(), expect)

        # check the generated files
        self.assertEqual(set(os.listdir('.')),
                         {'PymtplInputFiles', 'out.mtpl', 'out.flw', 'out2.mtpl', 'out2.flw'})

    @with_(TempDir, chdir=True)
    def test_floating(self):
        # test floating
        # test skip writing when it is already written

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Floating('Floating', Fitem('SAME', test1))
            PyMtpl.write()
            # End of "python mtpl code"

        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        with CaptureStdoutLog() as p:
            PyMtpl().main_one(PyObj)
        self.assertIn('-i- Skipping write()', p.getvalue())

    @with_(TempDir, chdir=True)
    def test_concurrentflow(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            ConCurrentFlow('PRL0CPUIOE_SubFlow',
                           IP_CPU='IP_CPU_CONCURRENT_FLOWS::PRL0CPUIOE_IP_CPU_FLOW_SubFlow',
                           IP_PCH='IP_PCH_CONCURRENT_FLOWS::PRL0CPUIOE_IP_PCH_FLOW_SubFlow',
                           result=['IP_CPU, IP_PCH, EffectiveIPResult',
                                   '1    ,    1   , IP_CPU',
                                   '1    ,  [*:0] , IP_PCH'])
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
ConcurrentFlow PRL0CPUIOE_SubFlow [Parallel]
{
    ConcurrentFlowItem IP_CPU IP_CPU_CONCURRENT_FLOWS::PRL0CPUIOE_IP_CPU_FLOW_SubFlow;
    ConcurrentFlowItem IP_PCH IP_PCH_CONCURRENT_FLOWS::PRL0CPUIOE_IP_PCH_FLOW_SubFlow;
    ConcurrentResultTable (IP_CPU, IP_PCH, EffectiveIPResult)
    {
        1    ,    1   , IP_CPU;
        1    ,  [*:0] , IP_PCH;
    }
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_flowdefs(self):
        # This tests FlowDefs default value, set one of default value to None and a new param altogether
        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            FlowDefs(TestPlanEndFlow=None, Blah='blah')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
FlowDefs
{
    InitFlow = INIT;
    MainFlow = MAIN;
    LotEndFlow = LOTENDFLOW;
    LotStartFlow = LOTSTARTFLOW;
    TestPlanStartFlow = TESTPLANSTARTFLOW;
    Blah = blah;
}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, OPT, "env", f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env')
    def test_ModuleFlow(self):
        Initialize.clear_all()

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            LTTCSOC_SubFlow = Flow('LTTCSOC_SubFlow', [
                # normal module
                Fitem('TPI_FLWFLGS_XXX_LTTCSOC', ModuleFlow('TPI_FLWFLGS_XXX'), r0=pFail(), r2=pPass()),
                # direct module
                Fitem('TPI_PWRUP_YXXK_LTTCSOC', ModuleFlow('TPI_PWRUP_YXXK::Y')),
                Fitem('TPI_PWRUP_YXXK_LTTCSOC1', ModuleFlow('$TPI_PWRUP_YXXK::Y')),
                # module with ip
                Fitem('ARR_LTTC', ModuleFlow('ARR')),
                # module with ip on ip
                Fitem('ARR_LTTC2', ModuleFlow('~ARR')),
                # parallel flow
                Fitem('SCN_SubFlow', ModuleFlow('SCN')),
                # special block
                Fitem('PRL_SubFlow', ModuleFlow('$PRL0')),
            ])
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow LTTCSOC_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_LTTCSOC TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_LTTCSOC {
  Result 0 { Property PassFail = "Fail"; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_PWRUP_YXXK_LTTCSOC; }
  Result 2 { Property PassFail = "Pass"; GoTo TPI_PWRUP_YXXK_LTTCSOC; }
 }
 DUTFlowItem TPI_PWRUP_YXXK_LTTCSOC TPI_PWRUP_YXXK::Y {
  Result 1 { Property PassFail = "Pass"; GoTo TPI_PWRUP_YXXK_LTTCSOC1; }
 }
 DUTFlowItem TPI_PWRUP_YXXK_LTTCSOC1 TPI_PWRUP_YXXK::Y {
  Result 1 { Property PassFail = "Pass"; GoTo ARR_LTTC; }
 }
 DUTFlowItem ARR_LTTC IP_CPU::ARR::ARR_LTTC {
  Result 1 { Property PassFail = "Pass"; GoTo ARR_LTTC2; }
 }
 DUTFlowItem ARR_LTTC2 ARR::ARR_LTTC2 {
  Result 1 { Property PassFail = "Pass"; GoTo SCN_SubFlow; }
 }
 DUTFlowItem SCN_SubFlow SCN_SubFlow {
  Result 1 { Property PassFail = "Pass"; GoTo PRL_SubFlow; }
 }
 DUTFlowItem PRL_SubFlow PRL0 {
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    def test_comment(self):

        # single line comment
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9", _comment='This instance is for blah')
            subflow = Flow('SubFlow1', Fitem('SAME', test1))

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # This instance is for blah
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        # multi-line comment
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9", _comment=['line1', 'line2'])
            subflow = Flow('SubFlow1', Fitem('SAME', test1))

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    # line1
    # line2
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
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
    def test_port_sorting(self):
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            return1 = pFail(ret=-1)
            return0 = pPass(ret=0)
            return2 = pFail(goto='Instance2')
            test2 = VminTC(name="Instance2", EndVoltageLimits="0.9", _fitem=Fitem())
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1,
                                 r0=return0,
                                 r1=return0,
                                 r2=return1,
                                 rm1=return1,
                                 rm2=return2,
                                 rm3=return1),
                           test2
                           )

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result -3
        {
            Property PassFail = "Fail";
            Return -1;
        }
        Result -2
        {
            Property PassFail = "Fail";
            GoTo Instance2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Pass";
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
            Return -1;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
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
    def test_combined_option(self):

        class PyObj:
            output = Initialize('out', 'FUN')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem('SAME')),
                VminTC(name="Instance2", EndVoltageLimits="0.8",
                       _fitem=Fitem('SAME'))])

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
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        # reuse of the same instance with _fitem is illegal, aka, incorrect usage
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem('SAME'))
            subflow = Flow('SubFlow1', test1, test1)

        with self.assertRaisesRegex(ErrorUser, 'Instance1 is reused inside'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_twoinstance(self):
        # Two instance specified
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2", EndVoltageLimits="0.8")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1),
                           Fitem('SAME', test2))

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
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
    }

    DUTFlowItem Instance2 Instance2
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

        # Same as above but we put it in a list
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2", EndVoltageLimits="0.8")
            flist = [Fitem('SAME', test1), Fitem('SAME', test2)]
            subflow = Flow('SubFlow1', flist)

        PyMtpl().main_one(PyObj)
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_reuse_error(self):
        # This is a fail unittest: This is illegal since they are using the same name
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = [VminTC(name="Instance1", EndVoltageLimits="0.9",
                            _fitem=Fitem('SAME'))]
            subflow1 = Flow('SubFlow1', test1)
            subflow2 = Flow('SubFlow2', test1)

        with self.assertRaisesRegex(ErrorUser, 'Instance1 is redefined twice.'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_sameinstance(self):
        # forloop testcase
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            f_list = []
            for idx in range(3):
                f_list.append(Fitem('SAME', test1))
            subflow = Flow('SubFlow1', *f_list)

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance1_1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Test VminTC Instance1_2
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    DUTFlowItem Instance1_1 Instance1_1
    {
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_2;
        }
    }

    DUTFlowItem Instance1_2 Instance1_2
    {
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
    def test_sameinstance2(self):

        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            subflow = Flow('SubFlow1',
                           Fitem('item1', test1),
                           Fitem('item2', test1))

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    FailCaptureCount = 999;
}

Test VminTC Instance1_1
{
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem item1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            GoTo item2;
        }
    }

    DUTFlowItem item2 Instance1_1
    {
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
    @patch('pymtpl.core.BaseMethod.write_lines', MagicMock())
    @with_(TempDir, chdir=True)
    def test_port_none(self):
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1,
                                 r0=pFail(),
                                 r1=pPass(),
                                 r2=pPass()),
                           Fitem('SAME', test1,
                                 r0=pFail(),
                                 r1=pPass(),
                                 r2=pPass()))
        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
    }

    DUTFlowItem Instance1_1 Instance1_1
    {
        Result 0
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

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.core.BaseMethod.write_lines', MagicMock())
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_edc_overwrite(self):
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            test2 = VminTC(name="Instance2")
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, edc=True,
                                 r0=pFail(setbin=90454520, goto='FAIL1'),
                                 r1=pPass(),
                                 r2=pPass(goto='FAIL1')),
                           Fitem('SAME', test1, edc=True,
                                 r0=pFail(setbin=4520, ret=0),
                                 r1=pPass(ret=1),
                                 r2=pPass(ret=1)),
                           Fitem('FAIL1', test1,
                                 r0=pFail(),
                                 r1=pPass()),
                           )
        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1 @EDC
    {
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b90454520_fail_FUN_Instance1;
            GoTo FAIL1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance1_1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            GoTo FAIL1;
        }
    }

    DUTFlowItem Instance1_1 Instance1_1 @EDC
    {
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b90454520_fail_FUN_Instance1_SHARED_BIN;
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
            Return 1;
        }
    }

    DUTFlowItem FAIL1 Instance1_2
    {
        Result 0
        {
            Property PassFail = "Fail";
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
    def test_default_goto(self):
        # Default goto test
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2", EndVoltageLimits="0.8")
            return1 = pFail(setbin=90454520, ret=-1)
            return0 = pFail(setbin=90454521, ret=0)
            subflow = Flow('SubFlow1',
                           Fitem('SAME', test1, rm1=return1),
                           Fitem('Instance2_etc', test2, r0=return0),
                           )

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
    DUTFlowItem Instance1 Instance1
    {
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90454520_fail_FUN_Instance1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2_etc;
        }
    }

    DUTFlowItem Instance2_etc Instance2
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90454521_fail_FUN_Instance2;
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

    @with_(TempDir, chdir=True)
    def test_composite(self):

        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            comp1 = Flow('Comp1', Fitem('SAME', test1))
            asubflow = Flow('ASubFlow1', Fitem('SomeComposite', comp1))

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    FailCaptureCount = 999;
}

DUTFlow Comp1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

DUTFlow ASubFlow1
{
    DUTFlowItem SomeComposite Comp1
    {
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
    def test_composite_NVL_Class(self):

        class PyObj:
            output = InitializeNVLClass('out', 'FUN')
            test1 = VminTC(name="Instance1")
            comp1 = Flow('Comp1', Fitem('SAME', test1))
            asubflow = Flow('ASubFlow1', Fitem('SomeComposite', comp1))

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    FailCaptureCount = 999;
}

Flow Comp1
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
            Return 1;
        }
    }

}

Flow ASubFlow1
{
    FlowItem SomeComposite Comp1
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
    def test_composite_NVL_Sort(self):

        class PyObj:
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4401), defaultrm2bin=-44, defaultrm1bin=-44)
            test1 = VminTC(name="Instance1")
            comp1 = Flow('Comp1', Fitem('SAME', test1))
            asubflow = Flow('ASubFlow1', Fitem('SomeComposite', comp1))

        PyMtpl().main_one(PyObj)
        expect = '''
CSharpTest VminTC Instance1
{
    FailCaptureCount = 999;
}

Flow Comp1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

Flow ASubFlow1
{
    FlowItem SomeComposite Comp1
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
    def test_samecomposite(self):

        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            comp1 = Flow('Comp1', Fitem('SAME', test1))
            asubflow = Flow('ASubFlow1',
                            Fitem('SomeComposite', comp1),
                            Fitem('SAME', comp1)
                            )

        PyMtpl().main_one(PyObj)
        expect = '''
Test VminTC Instance1
{
    FailCaptureCount = 999;
}

Test VminTC Instance1_1
{
    FailCaptureCount = 999;
}

DUTFlow Comp1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

DUTFlow Comp1_1
{
    DUTFlowItem Instance1_1 Instance1_1
    {
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

DUTFlow ASubFlow1
{
    DUTFlowItem SomeComposite Comp1
    {
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Comp1_1;
        }
    }

    DUTFlowItem Comp1_1 Comp1_1
    {
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
    def test_default_thermal_reset_bin(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLClass('out', 'FUN', binrange=(4400, 4450), defaultresetbin=90441901, defaultthermalbin=90974401)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=AUTO),
                                             r2=pFail(setbin=AUTO),
                                             r3=pFail(setbin=AUTO),
                                             r4=pFail(setbin=AUTO),
                                             r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

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
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90440000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000002_fail_Instance1_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974401_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441901_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_default_rm1_rm2_bin(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=-44, defaultrm1bin=-44)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            test2 = VminTC(name="Instance2", EndVoltageLimits="0.9")
            test3 = VminTC(name="Instance3", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r2=pFail(setbin=AUTO),
                                             r3=pFail(setbin=AUTO),
                                             r4=pFail(setbin=AUTO),
                                             r5=pFail(setbin=AUTO)),
                           Fitem('SAME', test2,
                                 r2=pFail(setbin=AUTO),
                                 r3=pFail(setbin=AUTO),
                                 r4=pFail(setbin=AUTO),
                                 r5=pFail(setbin=AUTO)),
                           Fitem('SAME', test3,
                                 r2=pFail(setbin=AUTO),
                                 r3=pFail(setbin=AUTO),
                                 r4=pFail(setbin=AUTO),
                                 r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
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

CSharpTest VminTC Instance3
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
            SetBin b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance2;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000000_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_3;
            IncrementCounters FUN::n44000001_fail_Instance1_3;
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
            SetBin b44190162_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

    FlowItem Instance2 Instance2
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440163_fail_FUN_Instance2_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440163_fail_FUN_Instance2_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo Instance3;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance2_2;
            IncrementCounters FUN::n44010000_fail_Instance2_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44010001_fail_FUN_Instance2_3;
            IncrementCounters FUN::n44010001_fail_Instance2_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b44010002_fail_FUN_Instance2_4;
            IncrementCounters FUN::n44010002_fail_Instance2_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190163_fail_FUN_Instance2_5;
            IncrementCounters FUN::n44190163_fail_Instance2_5;
        }
    }

    FlowItem Instance3 Instance3
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440164_fail_FUN_Instance3_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440164_fail_FUN_Instance3_n1;
            Return -1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44020000_fail_FUN_Instance3_2;
            IncrementCounters FUN::n44020000_fail_Instance3_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44020001_fail_FUN_Instance3_3;
            IncrementCounters FUN::n44020001_fail_Instance3_3;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b44020002_fail_FUN_Instance3_4;
            IncrementCounters FUN::n44020002_fail_Instance3_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190164_fail_FUN_Instance3_5;
            IncrementCounters FUN::n44190164_fail_Instance3_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_default_rm1_rm2_bin_error(self):
        # Good template to copy from
        ret_dict = {}
        with self.assertRaisesRegex(ErrorUser, 'for each Fitem as the final bin value depends on the HB value'):
            Sortdefault.set_rm_port(ret_dict, 'rm1', None, 30, -1)

    @with_(TempDir, chdir=True)
    def test_default_rm1_rm2_bin_from_port0(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=AUTO),
                                             r2=pFail(setbin=AUTO),
                                             r3=pFail(setbin=AUTO),
                                             r4=pFail(setbin=AUTO),
                                             r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

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
            SetBin b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_n1;
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
            SetBin b44000003_fail_FUN_Instance1_4;
            IncrementCounters FUN::n44000003_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190162_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_default_rm1_rm2_bin_from_manual_port0(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=4500),
                                             r2=pFail(setbin=AUTO),
                                             r3=pFail(setbin=AUTO),
                                             r4=pFail(setbin=AUTO),
                                             r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

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
            SetBin b99450162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98450162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b45000000_fail_FUN_Instance1_0;
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
            SetBin b44000000_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000000_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_3;
            IncrementCounters FUN::n44000001_fail_Instance1_3;
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
            SetBin b44190162_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_default_rm1_rm2_bin_from_manual_port0_3dig_bin(self):
        # Good template to copy from

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1,
                                             r0=pFail(setbin=801),
                                             r2=pFail(setbin=AUTO),
                                             r3=pFail(setbin=AUTO),
                                             r4=pFail(setbin=AUTO),
                                             r5=pFail(setbin=AUTO)))
            # End of "python mtpl code"

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
            SetBin b99080162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98080162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b8010000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n8010000_fail_Instance1_0;
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
            IncrementCounters FUN::n44000000_fail_Instance1_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1_3;
            IncrementCounters FUN::n44000001_fail_Instance1_3;
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
            SetBin b44190162_fail_FUN_Instance1_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

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
    def test_invalid_format_defaultthermal_bin(self):
        with self.assertRaisesRegex(ErrorUser, "defaultthermalbin must be a 8-dig integer or a tuple of 8-dig integers"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), defaultthermalbin=[90974400])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultthermal_bin(self):
        with self.assertRaisesRegex(ErrorUser, "requires defaultthermalbin to start with 9097"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), defaultthermalbin=90440000)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultthermal_bin_range(self):
        with self.assertRaisesRegex(ErrorUser, "requires all defaultthermalbin values to start with 9097"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), defaultthermalbin=(90974400, 90440000))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_invalid_format_defaultreset_bin(self):
        with self.assertRaisesRegex(ErrorUser, "defaultresetbin must be a 8-dig integer or a tuple of 8-dig integers"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), defaultresetbin=[90440000])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultreset_bin(self):
        with self.assertRaisesRegex(ErrorUser, "requires defaultresetbin to start with '90' and have '19' after the HB is defined"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), defaultresetbin=90440000)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultreset_bin_range(self):
        with self.assertRaisesRegex(ErrorUser, "requires defaultresetbin to start with '90' and have '19' after the HB is defined"):
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(800, 804), defaultresetbin=(90441900, 90440000))
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_duplicate(self):

        # case1: duplicate testinstance
        with self.assertRaisesRegex(ErrorUser, 'Test Instance1 is already used in'):
            class PyObj:
                output = Initialize('out', 'FUN')
                test1 = VminTC(name="Instance1")
                test2 = VminTC(name="Instance1")

        # case2: duplicate dutflowitem
        class PyObj:
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1")
            subflow = Flow('SubFlow1', Fitem('item1', test1), Fitem('item1', test1))

        with self.assertRaisesRegex(ErrorUser, 'item1 is reused inside.*SubFlow1'):
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_auto_file_removal_when_usebinctrfrommtpl(self):
        """Test that auto files are removed when usebinctrfrommtpl=True and file exists"""

        basenumberpath = os.path.join('PymtplInputFiles', 'FUN_AutoBasenumber.json')
        binpath = os.path.join('PymtplInputFiles', 'FUN_AutoBinner.json')
        ctrpath = os.path.join('PymtplInputFiles', 'FUN_AutoCounter.json')

        class PyObj:
            output = Initialize('out', 'FUN', usebinctrfrommtpl=False)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90454520)))
        PyMtpl().main_one(PyObj)

        # Verify file exists or not
        self.assertFalse(os.path.exists(basenumberpath))
        self.assertTrue(os.path.exists(binpath))
        self.assertTrue(os.path.exists(ctrpath))

        class PyObj1:
            output = Initialize('out', 'FUN', usebinctrfrommtpl=True)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90454520)))
        PyMtpl().main_one(PyObj1)

        # Verify file was removed
        self.assertFalse(os.path.exists(basenumberpath))
        self.assertFalse(os.path.exists(binpath))
        self.assertFalse(os.path.exists(ctrpath))
        # verify the inputfiles path does not exist
        self.assertFalse(os.path.exists('PymtplInputFiles'))

    @with_(TempDir, chdir=True)
    def test_autobasenumber_removal(self):
        """Test that empty auto base number is removed when usebinctrfrommtpl=True and file exists"""

        basenumberpath = os.path.join('PymtplInputFiles', 'FUN_AutoBasenumber.json')
        # create an empty json file at the basenumberpath
        File(basenumberpath).touch('{}', mkdir=True)

        class PyObj1:
            output = Initialize('out', 'FUN', usebinctrfrommtpl=True)
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=90454520)))
        PyMtpl().main_one(PyObj1)

        # Verify file was removed
        self.assertFalse(os.path.exists(basenumberpath))
        # verify the inputfiles path does not exist
        self.assertFalse(os.path.exists('PymtplInputFiles'))

    @with_(TempDir, chdir=True)
    def test_autobasenumber_creation(self):
        """Test that auto base number is created when usebinctrfrommtpl=True and file does not exist"""

        basenumberpath = os.path.join('PymtplInputFiles', 'FUN_AutoBasenumber.json')

        class PyObj:
            output = Initialize('out', 'FUN', usebinctrfrommtpl=True, basenumrange=(1000, 1100))
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9", Basenumbers=AUTO, _fitem=Fitem(r0=pFail()))
            test2 = VminTC(name="Instance2", EndVoltageLimits="0.9", Basenumbers=1001, _fitem=Fitem(r0=pFail()))
            subflow = Flow('SubFlow1', [test1, test2])
        PyMtpl().main_one(PyObj)

        # Verify file and folder exist
        self.assertTrue(os.path.exists('PymtplInputFiles'))
        self.assertTrue(os.path.exists(basenumberpath))

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseMtplInfo.load_mtpl_dutflow_map', MagicMock())
    @with_(TempDir, chdir=True)
    def test_no_default_counter_processing(self):
        """
        Test case where we have default counter dict file present but no processing on that.
        """

        file_path = "default_counter_dict.json"
        default_counter_dict = {"Default_Counter_Range": [(1000, 1001), (1110, 2110)]}
        with open(file_path, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with MockVar(glob, 'glob', lambda pattern: [file_path] if pattern.endswith('default_counter_dict.json') else []):
            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN', binrange=(4400, 4450))
                test1 = VminTC(name="Instance1",
                               _comment="VminTC comment",
                               EndVoltageLimits="0.9")
                subflow = Flow('SubFlow1', Fitem('SAME', test1, rm2=pFail(setbin=AUTO), rm1=pFail(setbin=AUTO), r4=pFail(setbin=AUTO), r5=pFail(setbin=AUTO)))

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
        Result 4
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90979744_fail_FUN_THERMAL_Instance1;
            IncrementCounters FUN::n97440001_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444419_fail_FUN_Instance1;
            IncrementCounters FUN::n44190001_fail_Instance1_5;
        }
    }

}

'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseMtplInfo.load_mtpl_dutflow_map', MagicMock())
    @with_(TempDir, chdir=True)
    def test_default_counter_dict_discovery_single_file(self):
        # Test that default_counter_dict.json is found 4 levels up
        # Create directory structure: tpdir/BaseInputs/SomeFolder/SomeProduct_Files/default_counter_dict.json
        cwd = os.getcwd()
        os.makedirs(os.path.join(cwd, 'BaseInputs', 'SomeFolder', 'Product_Files'), exist_ok=True)
        cfgfile = os.path.join(cwd, 'BaseInputs', 'SomeFolder', 'Product_Files', 'default_counter_dict.json')
        default_counter_dict = {"Default_Counter_Range": [(1000, 1010), (2000, 2100)]}
        with open(cfgfile, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm1=pFail(setbin=AUTO), rm2=pFail(setbin=AUTO)))

        PyMtpl().main_one(PyObj)
        # Verify that default_counter_range was loaded
        self.assertEqual(Initialize.default_counter_range, [[1000, 1010], [2000, 2100]])

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.BaseMtplInfo.load_mtpl_dutflow_map', MagicMock())
    @with_(TempDir, chdir=True)
    def test_default_counter_dict_discovery_multiple_files(self):
        # Test that when multiple default_counter_dict.json files are found, default_counter_range is set to None
        # Create two matching files in the same directory level
        os.makedirs(os.path.join('BaseInputs', 'Folder1', 'Product_Files'), exist_ok=True)
        os.makedirs(os.path.join('BaseInputs', 'Folder2', 'Product_Files'), exist_ok=True)

        cfgfile1 = os.path.join('BaseInputs', 'Folder1', 'Product_Files', 'default_counter_dict.json')
        cfgfile2 = os.path.join('BaseInputs', 'Folder2', 'Product_Files', 'default_counter_dict.json')

        default_counter_dict = {"Default_Counter_Range": [(1000, 1010)]}
        with open(cfgfile1, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)
        with open(cfgfile2, 'w') as json_file:
            json.dump(default_counter_dict, json_file, indent=4)

        class PyObj:
            output = InitializeNVLClassHBSBXXXX('out', 'FUN', binrange=(4400, 4450))
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, rm1=pFail(setbin=99440000), rm2=pFail(setbin=98440000)))

        with CaptureStdoutLog() as p:
            PyMtpl().main_one(PyObj)

        # Verify that default_counter_range was set to None
        self.assertIsNone(Initialize.default_counter_range)


@patch('pymtpl.core.PyMtpl._headers', MagicMock())
class TestMCONFIG(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic_integration(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            mconfig = MConfig(ip="IP_CPU", path="Test", rev="Some", patch="0.1", plistinfo="Testfile.plst")
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plst</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(File('module.mconfig').read(), expect)

    @with_(TempDir, chdir=True)
    def test_aa_mconfig_noupdate(self):     # This unittest to run first because of initialize
        File('module.mconfig').touch('''<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plst</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>''', newfile=True)

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            mconfig = MConfig(ip="IP_CPU", path="Test", rev="Some", patch="0.1", plistinfo="Testfile.plst")
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"
        with CaptureStdoutLog() as p:
            PyMtpl().main_one(PyObj)

        self.assertIn('-i- NO UPDATE: No changes to module.mconfig', p.getvalue())

    @with_(TempDir, chdir=True)
    def test_mconfig_Initialize_Error(self):
        Initialize.clear_all()

        class PyObj:
            # Start of the "python mtpl code" ====================
            with self.assertRaisesRegex(ErrorUser, 'No Initialize statement found before line'):
                MConfig(ip="IP_CPU", path="Test", rev="Some", patch="0.1", plistinfo="Testfile.plst")
                Initialize('out', 'FUN')
            # test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            # subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        # with self.assertRaisesRegex(ErrorUser, 'No Initialize statement found before line'):
        #     PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_mconfig_plistinfo_Error(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            Initialize('out', 'FUN')
            with self.assertRaisesRegex(ErrorUser, 'Incorrect input for plistinfo'):
                MConfig(ip="IP_CPU", path="Test", rev="Some", patch="0.1", plistinfo=1)

            # test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            # subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

    @with_(TempDir, chdir=True)
    def test_mconfig_aleph_Error(self):

        Initialize('out', 'FUN')
        with self.assertRaisesRegex(ErrorUser, 'Incorrect input for alephfiles'):
            MConfig(ip="IP_CPU", path="Test", rev="Some", patch="0.1", plistinfo="A.plist", alephfiles={'1'})

    @with_(TempDir, chdir=True)
    def test_mconfig_patpaths_Error(self):

        Initialize('out', 'FUN')
        with self.assertRaisesRegex(ErrorUser, ''):
            MConfig(ip="IP_CPU", path="Test", rev="Some", patch="0.1", plistinfo='A.plist', patpaths=1)

    @with_(TempDir, chdir=True)
    def test_mconfig_list(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"])
        mconfig.pattern(path="Test", rev="Some", patch="0.1", rootname='ENGRoot',
                        plistinfo={"sample.plist": "BOM1", 'sample2.plist': None})

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
        <ENGRoot Path="Test">
            <PlistFiles>
                <PlistFile BomGroup="BOM1">sample.plist</PlistFile>
                <PlistFile>sample2.plist</PlistFile>
            </PlistFiles>
        </ENGRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_pattern_aleph_string(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"], alephfiles="1.json")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", rootname='ENGRoot',
                        plistinfo={"sample.plist": "BOM1", 'sample2.plist': None})

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
            <AlephFiles>
                <AlephFile>1.json</AlephFile>
            </AlephFiles>
        </PORRoot>
        <ENGRoot Path="Test">
            <PlistFiles>
                <PlistFile BomGroup="BOM1">sample.plist</PlistFile>
                <PlistFile>sample2.plist</PlistFile>
            </PlistFiles>
        </ENGRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_pattern_aleph_list(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"], alephfiles=["1.json", "2.json"])
        mconfig.pattern(path="Test", rev="Some", patch="0.1", rootname='ENGRoot',
                        plistinfo={"sample.plist": "BOM1", 'sample2.plist': None})

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
            <AlephFiles>
                <AlephFile>1.json</AlephFile>
                <AlephFile>2.json</AlephFile>
            </AlephFiles>
        </PORRoot>
        <ENGRoot Path="Test">
            <PlistFiles>
                <PlistFile BomGroup="BOM1">sample.plist</PlistFile>
                <PlistFile>sample2.plist</PlistFile>
            </PlistFiles>
        </ENGRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_multiple_bom_list(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1",
                        plistinfo={"sample.plist": ["BOM1", "BOM2", "BOM3"], 'sample2.plist': ["BOM4", "BOM5"]}, alephfiles=["1.json", "2.json"])

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile BomGroup="BOM1">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM2">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM3">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM4">sample2.plist</PlistFile>
                <PlistFile BomGroup="BOM5">sample2.plist</PlistFile>
            </PlistFiles>
            <AlephFiles>
                <AlephFile>1.json</AlephFile>
                <AlephFile>2.json</AlephFile>
            </AlephFiles>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_bom_def_error_list(self):
        # case: BOM is defined in the pattern block and in the plist info block
        # This is not allowed
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        with self.assertRaisesRegex(ErrorUser, "BOM is being defined in the pattern block and in the plist info block"):
            mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                            plistinfo={"sample.plist": ["BOM1", "BOM2", "BOM3"], 'sample2.plist': ["BOM4", "BOM5"]}, alephfiles=["1.json", "2.json"])

    @with_(TempDir, chdir=True)
    def test_mconfig_pattern_patpath_string(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"], patpaths=r".\Supersede\Pats\p1")

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
            <PatPaths>
                <PatPath>.\\Supersede\\Pats\\p1</PatPath>
            </PatPaths>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_pattern_patpath_list(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"], patpaths=[r".\Supersede\Pats\p1", r".\Supersede\Pats\p0"])
        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
            <PatPaths>
                <PatPath>.\\Supersede\\Pats\\p1</PatPath>
                <PatPath>.\\Supersede\\Pats\\p0</PatPath>
            </PatPaths>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_aleph(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"])
        mconfig.aleph(alephfiles=["1.json", "2.json"])
        mconfig.aleph(alephfiles="3.json")
        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
    <AlephFiles>
        <AlephFile>1.json</AlephFile>
        <AlephFile>2.json</AlephFile>
        <AlephFile>3.json</AlephFile>
    </AlephFiles>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_modulealeph_error(self):

        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"])
        with self.assertRaisesRegex(ErrorUser, "Incorrect input for alephfiles"):
            mconfig.aleph(alephfiles=1)

    @with_(TempDir, chdir=True)
    def test_mconfig_bom_def_error_aleph(self):
        # case: BOM is defined in the pattern block and in the plist info block
        # This is not allowed
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        with self.assertRaisesRegex(ErrorUser, "BOM is being defined in the pattern block and in the aleph files block"):
            mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                            plistinfo="sample.plist", alephfiles={"1.json": "BOM1", "2.json": "BOM2"})

    @with_(TempDir, chdir=True)
    def test_mconfig_multiple_bom_aleph(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1",
                        plistinfo={"sample.plist": ["BOM1", "BOM2", "BOM3"], 'sample2.plist': ["BOM4", "BOM5"]}, alephfiles={"1.json": "BOM1", "2.json": "BOM2"})

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile BomGroup="BOM1">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM2">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM3">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM4">sample2.plist</PlistFile>
                <PlistFile BomGroup="BOM5">sample2.plist</PlistFile>
            </PlistFiles>
            <AlephFiles>
                <AlephFile BomGroup="BOM1">1.json</AlephFile>
                <AlephFile BomGroup="BOM2">2.json</AlephFile>
            </AlephFiles>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_multiple_bom_aleph_list(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1",
                        plistinfo={"sample.plist": ["BOM1", "BOM2", "BOM3"], 'sample2.plist': ["BOM4", "BOM5"]}, alephfiles={"1.json": ["BOM1", "BOM2", "BOM3"], '2.json': ["BOM4", "BOM5"]})

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile BomGroup="BOM1">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM2">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM3">sample.plist</PlistFile>
                <PlistFile BomGroup="BOM4">sample2.plist</PlistFile>
                <PlistFile BomGroup="BOM5">sample2.plist</PlistFile>
            </PlistFiles>
            <AlephFiles>
                <AlephFile BomGroup="BOM1">1.json</AlephFile>
                <AlephFile BomGroup="BOM2">1.json</AlephFile>
                <AlephFile BomGroup="BOM3">1.json</AlephFile>
                <AlephFile BomGroup="BOM4">2.json</AlephFile>
                <AlephFile BomGroup="BOM5">2.json</AlephFile>
            </AlephFiles>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_aleph_block_bomgroup(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"])
        mconfig.aleph(alephfiles={"1.json": "BOM1", "2.json": "BOM2"})
        mconfig.aleph(alephfiles="3.json")
        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
    <AlephFiles>
        <AlephFile BomGroup="BOM1">1.json</AlephFile>
        <AlephFile BomGroup="BOM2">2.json</AlephFile>
        <AlephFile>3.json</AlephFile>
    </AlephFiles>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_aleph_block_bomgroup_list(self):
        # case: BOM top level
        # case: BOM per plist, including a No BOM case
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.ipname("IP_CPU")
        mconfig.pattern(path="Test", rev="Some", patch="0.1", bom='BOM2',
                        plistinfo=["Testfile.plist", "sample.plist"])
        mconfig.aleph(alephfiles={"1.json": ["BOM1", "BOM2"], "2.json": ["BOM2", "BOM4"]})
        mconfig.aleph(alephfiles="3.json")
        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM2" Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile>Testfile.plist</PlistFile>
                <PlistFile>sample.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
    <AlephFiles>
        <AlephFile BomGroup="BOM1">1.json</AlephFile>
        <AlephFile BomGroup="BOM2">1.json</AlephFile>
        <AlephFile BomGroup="BOM2">2.json</AlephFile>
        <AlephFile BomGroup="BOM4">2.json</AlephFile>
        <AlephFile>3.json</AlephFile>
    </AlephFiles>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_ip_attribute_pattern_method(self):
        # Test IP attribute using pattern() method
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.pattern(path="Test", rev="1.0", patch="0.1",
                        plistinfo="test.plist", ip="IP_CPU")

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot IP="IP_CPU" Path="Test" Rev="1.0" Patch="0.1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_ip_attribute_constructor(self):
        # Test IP attribute using constructor patternip parameter
        Initialize('out', 'FUN')
        mconfig = MConfig(path="Test", rev="1.0", patch="0.1",
                          plistinfo="test.plist", patternip="IP_GPU")

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot IP="IP_GPU" Path="Test" Rev="1.0" Patch="0.1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_ip_attribute_with_engroot(self):
        # Test IP attribute with ENGRoot
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.pattern(path="Test", rev="1.0", patch="0.1",
                        plistinfo="test.plist", rootname="ENGRoot", ip="IP_SOC")

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <ENGRoot IP="IP_SOC" Path="Test">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </ENGRoot>
    </Patterns>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_ip_attribute_with_bomgroup(self):
        # Test IP attribute combined with BomGroup
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.pattern(path="Test", rev="1.0", patch="0.1",
                        plistinfo="test.plist", bom="BOM1", ip="IP_DISPLAY")

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot BomGroup="BOM1" IP="IP_DISPLAY" Path="Test" Rev="1.0" Patch="0.1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_ip_attribute_multiple_patterns(self):
        # Test multiple patterns with different IPs
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.pattern(path="Patterns/CPU", rev="1.0", patch="0",
                        plistinfo="cpu.plist", ip="IP_CPU")
        mconfig.pattern(path="Patterns/GPU", rev="1.0", patch="0",
                        plistinfo="gpu.plist", rootname="ENGRoot", ip="IP_GPU")

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot IP="IP_CPU" Path="Patterns/CPU" Rev="1.0" Patch="0">
            <PlistFiles>
                <PlistFile>cpu.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
        <ENGRoot IP="IP_GPU" Path="Patterns/GPU">
            <PlistFiles>
                <PlistFile>gpu.plist</PlistFile>
            </PlistFiles>
        </ENGRoot>
    </Patterns>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_mconfig_backward_compatibility_no_ip(self):
        # Test backward compatibility - no IP attribute when not specified
        Initialize('out', 'FUN')
        mconfig = MConfig()
        mconfig.pattern(path="Test", rev="1.0", patch="0.1", plistinfo="test.plist")

        out = '\n'.join(mconfig.write_lines())
        # IP attribute should not be present
        self.assertNotIn('IP=', out)
        # Basic structure should still be valid
        self.assertIn('<PORRoot Path="Test"', out)
        self.assertIn('Rev="1.0"', out)
        self.assertIn('Patch="0.1"', out)

    @with_(TempDir, chdir=True)
    def test_mconfig_ip_attribute_with_ipname(self):
        # Test that patternip and ip (for IPName) work together
        Initialize('out', 'FUN')
        mconfig = MConfig(path="Test", rev="1.0", patch="0.1",
                          plistinfo="test.plist", patternip="IP_CPU", ip="IP_CPU")

        out = '\n'.join(mconfig.write_lines())
        expect = '''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot IP="IP_CPU" Path="Test" Rev="1.0" Patch="0.1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(out, expect)


@patch('pymtpl.core.PyMtpl._headers', MagicMock())
class TestFLOW(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic_flow_integration(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1))
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
<?xml version="1.0" encoding="utf-8"?>
<!--File is auto-generated, any manual edits can be overwritten.-->
<!DOCTYPE HDMTFlowItemCoor []>
<HDMTFlowItemCoor>
  <FlowItem name="FUN::SubFlow1.Instance1" X="25" Y="25" />
</HDMTFlowItemCoor>
'''
        self.assertTextEqual(File('out.flw').read(), expect)

    @with_(TempDir, chdir=True)
    def test_basic_flow(self):

        # Start of the "python mtpl code" ====================
        output = Initialize('out', 'FUN')
        test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
        subflow = Flow('SubFlow1', Fitem('SAME', test1))
        flow_registry = []
        flow_registry.append(subflow)
        # End of "python mtpl code"
        out = '\n'.join(PyMtpl()._generate_flow_file(flow_registry))

        expect = '''
<?xml version="1.0" encoding="utf-8"?>
<!--File is auto-generated, any manual edits can be overwritten.-->
<!DOCTYPE HDMTFlowItemCoor []>
<HDMTFlowItemCoor>
  <FlowItem name="FUN::SubFlow1.Instance1" X="25" Y="25" />
</HDMTFlowItemCoor>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_flow_5_tests(self):

        # Start of the "python mtpl code" ====================
        output = Initialize('out', 'FUN')
        test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
        test2 = VminTC(name="Instance2", EndVoltageLimits="0.9")
        test3 = VminTC(name="Instance3", EndVoltageLimits="0.9")
        test4 = VminTC(name="Instance4", EndVoltageLimits="0.9")
        test5 = VminTC(name="Instance5", EndVoltageLimits="0.9")
        test6 = VminTC(name="Instance6", EndVoltageLimits="0.9")
        subflow = Flow('SubFlow1', Fitem('SAME', test1), Fitem('SAME', test2), Fitem('SAME', test3), Fitem('SAME', test4), Fitem('SAME', test5), Fitem('SAME', test6))
        flow_registry = []
        flow_registry.append(subflow)
        # End of "python mtpl code"
        out = '\n'.join(PyMtpl()._generate_flow_file(flow_registry))

        expect = '''
<?xml version="1.0" encoding="utf-8"?>
<!--File is auto-generated, any manual edits can be overwritten.-->
<!DOCTYPE HDMTFlowItemCoor []>
<HDMTFlowItemCoor>
  <FlowItem name="FUN::SubFlow1.Instance1" X="25" Y="25" />
  <FlowItem name="FUN::SubFlow1.Instance2" X="195" Y="25" />
  <FlowItem name="FUN::SubFlow1.Instance3" X="365" Y="25" />
  <FlowItem name="FUN::SubFlow1.Instance4" X="535" Y="25" />
  <FlowItem name="FUN::SubFlow1.Instance5" X="25" Y="275" />
  <FlowItem name="FUN::SubFlow1.Instance6" X="195" Y="275" />
</HDMTFlowItemCoor>
'''
        self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_flow_multiple_subflows(self):

        # Start of the "python mtpl code" ====================
        output = Initialize('out', 'FUN')
        test1 = VminTC(name="Instance1", EndVoltageLimits="0.9")
        test2 = VminTC(name="Instance2", EndVoltageLimits="0.9")
        test3 = VminTC(name="Instance3", EndVoltageLimits="0.9")
        test4 = VminTC(name="Instance4", EndVoltageLimits="0.9")
        test5 = VminTC(name="Instance5", EndVoltageLimits="0.9")
        test6 = VminTC(name="Instance6", EndVoltageLimits="0.9")
        subflow = Flow('SubFlow1', Fitem('SAME', test1), Fitem('SAME', test2), Fitem('SAME', test3), Fitem('SAME', test4))
        subflow2 = Flow('SubFlow2', Fitem('SAME', test5), Fitem('SAME', test6))
        flow_registry = []
        flow_registry.append(subflow)
        flow_registry.append(subflow2)
        # End of "python mtpl code"
        out = '\n'.join(PyMtpl()._generate_flow_file(flow_registry))

        expect = '''
<?xml version="1.0" encoding="utf-8"?>
<!--File is auto-generated, any manual edits can be overwritten.-->
<!DOCTYPE HDMTFlowItemCoor []>
<HDMTFlowItemCoor>
  <FlowItem name="FUN::SubFlow1.Instance1" X="25" Y="25" />
  <FlowItem name="FUN::SubFlow1.Instance2" X="195" Y="25" />
  <FlowItem name="FUN::SubFlow1.Instance3" X="365" Y="25" />
  <FlowItem name="FUN::SubFlow1.Instance4" X="535" Y="25" />
  <FlowItem name="FUN::SubFlow2.Instance5" X="25" Y="25" />
  <FlowItem name="FUN::SubFlow2.Instance6" X="195" Y="25" />
</HDMTFlowItemCoor>
'''
        self.assertTextEqual(out, expect)


class TestPyMtpl(TestCase):
    """Test PyMtpl class functionality"""

    def test_path_updaters(self):
        # Test that PyMtpl.main() skips path updater when skip_path_updater option is True
        with MockVar(OPT, 'skip_path_updater', True), \
                MockVar(OPT, 'all', []), \
                patch('pymtpl.path_updater.PythonPathUpdater.write_python_paths_for_VS') as mock_write:
            PyMtpl.main()
            # Verify that write_python_paths_for_VS was never called
            mock_write.assert_not_called()

        # Test that PyMtpl.main() calls path updater when skip_path_updater option is False
        with MockVar(OPT, 'skip_path_updater', False), \
                MockVar(OPT, 'all', []), \
                patch('pymtpl.path_updater.PythonPathUpdater.write_python_paths_for_VS') as mock_write:
            PyMtpl.main()
            # Verify that write_python_paths_for_VS was called
            mock_write.assert_called_once()

        # Test that PyMtpl.main() calls path updater when skip_path_updater option is not present
        # Ensure skip_path_updater attribute doesn't exist by using getattr in the tested code
        with MockVar(OPT, 'all', []), \
                patch('pymtpl.path_updater.PythonPathUpdater.write_python_paths_for_VS') as mock_write:
            # Make sure the attribute doesn't exist - only delete if it does
            if hasattr(OPT, 'skip_path_updater'):
                try:
                    delattr(OPT, 'skip_path_updater')
                except AttributeError:
                    pass  # Already doesn't exist
            PyMtpl.main()
            # Verify that write_python_paths_for_VS was called (default behavior)
            mock_write.assert_called_once()


class TestKillTestFailPortWarning(TestCase):
    """Test warning for kill test fail ports with no bin assignment"""

    @with_(TempDir, chdir=True)
    def test_warning_for_kill_test_fail_port_no_setbin(self):
        # Test that a warning is issued for a kill test fail port with no setbin
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                test1 = VminTC(name="TEST_A_B_C_D_E_F", EndVoltageLimits="0.9",
                               _fitem=Fitem(edc=False, r0=pFail(ret=0)))  # No setbin
                flow = Flow('MAIN', test1)
            PyMtpl().main_one(PyObj)

        # Check that warning was issued
        log_output = log_capture.getvalue()
        self.assertIn('Kill test fail port r0 has no bin assignment', log_output)
        self.assertIn('TEST_A_B_C_D_E_F', log_output)

    @with_(TempDir, chdir=True)
    def test_no_warning_for_init_test(self):
        # Test that no warning is issued when 5th field is INIT
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                test1 = VminTC(name="TDAU_X_TJ_K_INIT_X_X_X_X", EndVoltageLimits="0.9",
                               _fitem=Fitem(edc=False, r0=pFail(ret=0)))  # No setbin, but INIT test
                flow = Flow('MAIN', test1)
            PyMtpl().main_one(PyObj)

        # Check that warning was NOT issued
        log_output = log_capture.getvalue()
        self.assertNotIn('Kill test fail port', log_output)

    @with_(TempDir, chdir=True)
    def test_no_warning_for_edc_test(self):
        # Test that no warning is issued for EDC tests (edc=True)
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                test1 = VminTC(name="TEST_A_B_C_D_E_F", EndVoltageLimits="0.9",
                               _fitem=Fitem(edc=True, r0=pFail(ret=0)))  # No setbin, but EDC test
                flow = Flow('MAIN', test1)
            PyMtpl().main_one(PyObj)

        # Check that warning was NOT issued
        log_output = log_capture.getvalue()
        self.assertNotIn('Kill test fail port', log_output)

    @with_(TempDir, chdir=True)
    def test_no_warning_when_setbin_specified(self):
        # Test that no warning is issued when setbin is specified
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                test1 = VminTC(name="TEST_A_B_C_D_E_F", EndVoltageLimits="0.9",
                               _fitem=Fitem(edc=False, r0=pFail(setbin=-44, ret=0)))  # Has setbin
                flow = Flow('MAIN', test1)
            PyMtpl().main_one(PyObj)

        # Check that warning was NOT issued
        log_output = log_capture.getvalue()
        self.assertNotIn('Kill test fail port', log_output)

    @with_(TempDir, chdir=True)
    def test_no_warning_for_pass_port(self):
        # Test that no warning is issued for pass ports (pPass)
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                test1 = VminTC(name="TEST_A_B_C_D_E_F", EndVoltageLimits="0.9",
                               _fitem=Fitem(edc=False, r0=pFail(setbin=-44), r1=pPass()))  # r1 has no setbin
                flow = Flow('MAIN', test1)
            PyMtpl().main_one(PyObj)

        # Check that warning was NOT issued for the pass port
        log_output = log_capture.getvalue()
        self.assertNotIn('Kill test fail port r1', log_output)

    @with_(TempDir, chdir=True)
    def test_warning_with_setbinstring(self):
        # Test that no warning is issued when setbinstring is specified (even if setbin is None)
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                test1 = VminTC(name="TEST_A_B_C_D_E_F", EndVoltageLimits="0.9",
                               _fitem=Fitem(edc=False, r0=pFail(setbinstring='SoftBins.b90440101', ctr=44010001, ret=0)))
                flow = Flow('MAIN', test1)
            PyMtpl().main_one(PyObj)

        # Check that warning was NOT issued
        log_output = log_capture.getvalue()
        self.assertNotIn('Kill test fail port', log_output)

    @with_(TempDir, chdir=True)
    def test_warning_for_multiple_fail_ports(self):
        # Test that warnings are issued for multiple fail ports without setbin
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                test1 = VminTC(name="TEST_A_B_C_D_E_F", EndVoltageLimits="0.9",
                               _fitem=Fitem(edc=False, r0=pFail(ret=0), r2=pFail(ret=2)))  # Both without setbin
                flow = Flow('MAIN', test1)
            PyMtpl().main_one(PyObj)

        log_output = log_capture.getvalue()
        # Check that warnings were issued for both ports
        self.assertIn('Kill test fail port r0 has no bin assignment', log_output)
        self.assertIn('Kill test fail port r2 has no bin assignment', log_output)

    @with_(TempDir, chdir=True)
    def test_warning_summary_for_many_ports(self):
        # Test that only first 5 warnings are shown and a summary is printed when > 5
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                # Create 8 tests with missing setbin to trigger summary
                test1 = VminTC(name="TEST1_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                test2 = VminTC(name="TEST2_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                test3 = VminTC(name="TEST3_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                test4 = VminTC(name="TEST4_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                test5 = VminTC(name="TEST5_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                test6 = VminTC(name="TEST6_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                test7 = VminTC(name="TEST7_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                test8 = VminTC(name="TEST8_A_B_C_D_E", EndVoltageLimits="0.9", _fitem=Fitem(edc=False, r0=pFail(ret=0)))
                flow = Flow('MAIN', test1, test2, test3, test4, test5, test6, test7, test8)
            PyMtpl().main_one(PyObj)

        log_output = log_capture.getvalue()
        # Check that first 5 warnings are shown
        self.assertIn('Kill test fail port r0 has no bin assignment (setbin) for test "TEST1_A_B_C_D_E"', log_output)
        self.assertIn('Kill test fail port r0 has no bin assignment (setbin) for test "TEST5_A_B_C_D_E"', log_output)
        # Check that 6th warning is NOT shown
        self.assertNotIn('Kill test fail port r0 has no bin assignment (setbin) for test "TEST6_A_B_C_D_E"', log_output)
        # Check that summary is shown
        self.assertIn('Total of 8 kill test fail ports have no bin assignment', log_output)
        self.assertIn('Only first 5 warnings were shown above', log_output)

    @with_(TempDir, chdir=True)
    def test_no_warning_for_composite_test(self):
        # Test that no warning is issued for composites (Flow objects used in Fitem)
        with CaptureStdoutLog() as log_capture:
            class PyObj:
                output = Initialize('out', 'FUN', binrange=(4400, 4500))
                # Create a test instance for the sub-flow
                test1 = VminTC(name="TEST_A_B_C_D_E_F", EndVoltageLimits="0.9",
                               _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass()))
                # Create a sub-flow (composite)
                subflow = Flow('SUBFLOW', test1)
                # Use the composite in main flow with no setbin - should NOT trigger warning
                # because it's a composite (Flow), not a BaseMethod
                main_flow = Flow('MAIN', Fitem('CompositeItem', subflow, edc=False, r0=pFail(ret=0), r1=pPass()))
            PyMtpl().main_one(PyObj)

        # Check that warning was NOT issued (composites should not trigger the warning)
        log_output = log_capture.getvalue()
        self.assertNotIn('Kill test fail port', log_output)


class TestJGSdefault(TestCase):
    # Unit tests for JGSdefault class
    def setUp(self):
        Initialize.clear_all()

    def test_jgs_default_sbdef_name(self):
        # Test get_subbindef_name method
        self.assertEqual(JGSdefault.get_subbindef_name('MIO_DDR'), 'MIO_DDR.sbdefs')
        self.assertEqual(JGSdefault.get_subbindef_name('TEST_MODULE'), 'TEST_MODULE.sbdefs')

    def test_jgs_default_write_flags(self):
        # Test that write_hardbins_to_sbdef and write_softbins_to_sbdef are False
        self.assertEqual(JGSdefault.write_hardbins_to_sbdef, False)
        self.assertEqual(JGSdefault.write_softbins_to_sbdef, False)

    def test_jgs_default_require_counters(self):
        # Test that require_default_counters is False
        self.assertEqual(JGSdefault.require_default_counters, False)

    def test_jgs_default_bindefdefaults(self):
        # Test bindefdefaults dictionary
        self.assertIn('98', JGSdefault.bindefdefaults)
        self.assertIn('99', JGSdefault.bindefdefaults)
        self.assertIn('9801', JGSdefault.bindefdefaults)
        self.assertEqual(JGSdefault.bindefdefaults['98'], 'b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN')
        self.assertEqual(JGSdefault.bindefdefaults['99'], 'b99_FAIL_HARDWARE_ALARM')
        self.assertEqual(JGSdefault.bindefdefaults['9801'], '9801_FAIL_TESTCLASS_EXCEPTION_ERROR')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_jgs_default_ports_test_instance(self):
        # Test default_ports method for test instances
        ret_dict = {}
        JGSdefault.default_ports(ret_dict)
        # Should have rm1 and rm2 with setbin
        self.assertIn('rm1', ret_dict)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].setbin, -98)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].setbin, -99)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_jgs_default_ports_composite(self):
        # Test default_ports method for composite flows
        ret_dict = {}
        JGSdefault.default_ports(ret_dict, ti=Flow('Dummy'))
        # For composites, rm1/rm2 should not have setbin
        self.assertIn('rm1', ret_dict)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].setbin, None)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].setbin, None)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_jgs_default_ports_mtt(self):
        # Test default_ports method for MTT tests
        ret_dict = {}
        JGSdefault.default_ports(ret_dict, is_mtt=True)
        # For MTT, rm1/rm2 should have trialaction
        self.assertIn('rm1', ret_dict)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].trialaction, 'Exit')
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].trialaction, 'Exit')

    @with_(TempDir, chdir=True)
    def test_jgs_dont_write_hardbins_or_softbins_to_sbdef(self):
        # Test that sbdefs file doesn't contain hardbins or softbins
        class PyObj:
            output = InitializeJGSClass('ABC', 'ABC', binrange=(6800, 6800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-68),
                       ))
            ])
        PyMtpl().main_one(PyObj)

        expect = '''
Version 1.0;

SubBinDefs
{

    BinGroup DataBins
    {
        LeafBin b68000000_fail_ABC_Instance1_0    68000000    : "b68000000_fail_ABC_Instance1_0",    b6800;
    }

}
'''
        # Make sure the sbdefs are right (no HardBins or SoftBins groups)
        self.assertTextEqual(File('ABC.sbdefs').read(), expect)

    @with_(TempDir, chdir=True)
    def test_jgs_set_rm_port_with_default_bins(self):
        # Test set_rm_port method with default bins
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4400, 4450), defaultrm1bin=-44, defaultrm2bin=-44)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # rm1 and rm2 should have bins based on defaultrm1bin/defaultrm2bin
        self.assertIn('Result -1', mtpl_content)
        self.assertIn('Result -2', mtpl_content)

    def test_jgs_default_params(self):
        # Test that default_params returns empty dict
        self.assertEqual(JGSdefault.default_params(), {})

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_negbin(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = (6400, 6401)

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)

        # repeat just in case
        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b90990800_fail_FAIL_DPS_ALARM_n2", readout)
        self.assertIn("IncrementCounters FUN::n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n90990800_fail_FAIL_DPS_ALARM_n2", readout)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_negbin_34dig(self):
        """Test for defaultrmXbin with negative bin values"""
        binrange = [(6401, 6401), (805, 806)]

        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-6401, defaultrm2bin=-805)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)

        # repeat just in case
        class PyObj1:
            output = InitializeCBRClass('out', 'FUN', binrange=binrange, edcportctrbinrange=binrange, defaultrm1bin=-6401, defaultrm2bin=-805)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b90990800_fail_FAIL_DPS_ALARM_n2", readout)
        self.assertIn("IncrementCounters FUN::n90986400_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n90990800_fail_FAIL_DPS_ALARM_n2", readout)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_posbin(self):
        """Test for defaultrmXbin with 8 digit positive bin value"""
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin=98123456, defaultrm2bin=99567890)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b98123456_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("SetBin b99567890_fail_FAIL_DPS_ALARM_n2", readout)
        self.assertIn("IncrementCounters FUN::n98123456_fail_FAIL_SYSTEM_SOFTWARE_n1", readout)
        self.assertIn("IncrementCounters FUN::n99567890_fail_FAIL_DPS_ALARM_n2", readout)

    @with_(TempDir, chdir=True)
    def test_defaultrmbins_directset(self):
        """Test for defaultrmXbin with a direct string set"""
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b98123456_FAIL_MIO_DDR_SHARED_BIN_n1', defaultrm2bin='b99567890_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem())])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        self.assertIn("SetBin b98123456_FAIL_MIO_DDR_SHARED_BIN_n1", readout)
        self.assertIn("SetBin b99567890_fail_FUN_shared_bin_n2", readout)
        self.assertIn("IncrementCounters FUN::n98123456_FAIL_MIO_DDR_SHARED_COUNTER_n1", readout)
        self.assertIn("IncrementCounters FUN::n99567890_fail_FUN_shared_counter_n2", readout)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm1_bin(self):
        with self.assertRaisesRegex(ErrorUser, "equal to -98 or -99 is not allowed"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(rm1=pFail(),
                                        r2=pFail(setbin=801)
                                        )
                           )])

            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be a -HB value"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be an 8 digit value"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm1bin=98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm1bin='90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm1bin='b90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_incorrect_defaultrm2_bin(self):
        with self.assertRaisesRegex(ErrorUser, "equal to -98 or -99 is not allowed"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be a -HB value"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=-98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be an 8 digit value"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm2bin='90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm2bin='b90989090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "is not valid"):
            class PyObj:
                output = InitializeJGSClass('out', 'FUN', binrange=(800, 804), defaultrm2bin=['test', 'array'])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)


class TestInitializeJGSClass(TestCase):
    # Unit tests for InitializeJGSClass
    def setUp(self):
        Initialize.clear_all()

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_initialize_dmrhd_class_basic(self):
        # Test basic initialization
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-44),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        # Should generate valid MTPL
        mtpl_content = File('out.mtpl').read()
        self.assertIn('CSharpTest VminTC Instance1', mtpl_content)
        self.assertIn('Flow SubFlow1', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_initialize_dmrhd_class_binrange(self):
        # Test with multiple bin ranges
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=[(4400, 4450), (9800, 9850)])
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           rm1=pFail(),
                           r0=pFail(setbin=-44),
                           r2=pFail(setbin=-98),
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # Should have bins from both ranges
        self.assertIn('b44', mtpl_content)
        self.assertIn('b98', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_initialize_dmrhd_class_defaultrm1bin(self):
        # Test with defaultrm1bin parameter
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4400, 4450), defaultrm1bin=-44)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(),
                           r0=pFail(setbin=-44)
                       ))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # rm1 should have a bin
        self.assertIn('Result -1', mtpl_content)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrJGS8dig.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_initialize_dmrhd_class_defaultrm2bin(self):
        # Test with defaultrm2bin parameter
        class PyObj:
            output = InitializeJGSClass('out', 'FUN', binrange=(4400, 4450), defaultrm2bin=-44)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm1=pFail(),
                           r0=pFail(setbin=-44)))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # rm2 should have a bin
        self.assertIn('Result -2', mtpl_content)


class TestTestChipdefault(TestCase):
    # Unit tests for TestChipdefault class
    def setUp(self):
        Initialize.clear_all()

    def test_tc_default_sbdef_name(self):
        # Test get_subbindef_name method
        self.assertEqual(TestChipdefault.get_subbindef_name('TEST_CHIP'), 'TEST_CHIP.sbdefs')
        self.assertEqual(TestChipdefault.get_subbindef_name('MY_MODULE'), 'MY_MODULE.sbdefs')

    def test_tc_default_write_flags(self):
        # Test that write_hardbins_to_sbdef and write_softbins_to_sbdef are False
        self.assertEqual(TestChipdefault.write_hardbins_to_sbdef, False)
        self.assertEqual(TestChipdefault.write_softbins_to_sbdef, False)

    def test_tc_default_require_counters(self):
        # Test that require_default_counters is False
        self.assertEqual(TestChipdefault.require_default_counters, False)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_tc_default_ports_test_instance(self):
        # Test default_ports method for test instances
        ret_dict = {}
        TestChipdefault.default_ports(ret_dict)
        # Should have rm1 and rm2 with setbin
        self.assertIn('rm1', ret_dict)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].goto, None)
        self.assertEqual(ret_dict['rm1'].setbin, None)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].goto, None)
        self.assertEqual(ret_dict['rm2'].setbin, None)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_tc_default_ports_composite(self):
        # Test default_ports method for composite flows
        ret_dict = {}
        TestChipdefault.default_ports(ret_dict, ti=Flow('Dummy'))
        # For composites, rm1/rm2 should not have setbin
        self.assertIn('rm1', ret_dict)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, -1)
        self.assertEqual(ret_dict['rm1'].goto, None)
        self.assertEqual(ret_dict['rm1'].setbin, None)
        self.assertEqual(ret_dict['rm2'].ret, -2)
        self.assertEqual(ret_dict['rm2'].goto, None)
        self.assertEqual(ret_dict['rm2'].setbin, None)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_tc_default_ports_composite_override(self):
        # Test default_ports method for composite flows
        ret_dict = {'rm1': pFail(setbin=-55), 'rm2': pFail(setbin=-66)}
        TestChipdefault.default_ports(ret_dict, ti=Flow('Dummy'))
        # it should NOT override existing rm1/rm2
        self.assertIn('rm1', ret_dict)
        self.assertEqual(ret_dict['rm1'].setbin, -55)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm2'].setbin, -66)

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_tc_default_ports_mtt(self):
        # Test default_ports method for MTT tests
        ret_dict = {}
        TestChipdefault.default_ports(ret_dict, is_mtt=True)
        # For MTT, rm1/rm2 should have trialaction
        self.assertIn('rm1', ret_dict)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm1'].ret, None)
        self.assertEqual(ret_dict['rm1'].trialaction, 'Exit')
        self.assertEqual(ret_dict['rm2'].ret, None)
        self.assertEqual(ret_dict['rm2'].trialaction, 'Exit')

    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    @patch('pymtpl.binctr.CtrTestChip.get_portctrstring', Mock(return_value=''))
    @with_(TempDir, chdir=True)
    def test_tc_default_ports_mtt_specified(self):
        # Test default_ports method for MTT tests
        ret_dict = {'rm1': pFail(setbin=-55), 'rm2': pFail(setbin=-66)}
        TestChipdefault.default_ports(ret_dict, is_mtt=True)
        self.assertIn('rm1', ret_dict)
        self.assertEqual(ret_dict['rm1'].setbin, -55)
        self.assertIn('rm2', ret_dict)
        self.assertEqual(ret_dict['rm2'].setbin, -66)

    @with_(TempDir, chdir=True)
    def test_tc_dont_write_hardbins_or_softbins_to_sbdef(self):
        # Test that TC doesn't write hardbins or softbins to sbdef file
        # TC uses usebinctrfrommtpl=True so sbdefs file is not generated
        class PyObj:
            output = InitializeTestChip('ABC', 'ABC', binrange=(6800, 6800))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(
                           rm2=pFail(setbin=-68),
                           rm1=pFail(setbin=-68),
                           r0=pFail(setbin=-68),
                       ))
            ])
        PyMtpl().main_one(PyObj)

        # TC uses usebinctrfrommtpl=True, so no sbdefs file is generated
        self.assertFalse(os.path.exists('ABC.sbdefs'))

    @with_(TempDir, chdir=True)
    def test_tc_set_rm_port_with_default_bins(self):
        # Test set_rm_port method with default bins
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450), defaultrm1bin=-44, defaultrm2bin=-44)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # rm1 and rm2 should have bins based on defaultrm1bin/defaultrm2bin
        self.assertIn('Result -1', mtpl_content)
        self.assertIn('Result -2', mtpl_content)

    def test_tc_default_params(self):
        # Test that default_params returns empty dict
        self.assertEqual(TestChipdefault.default_params(), {})

    @with_(TempDir, chdir=True)
    def test_tc_defaultrmbins_negbin(self):
        # Test for defaultrmXbin with negative bin values
        # TC uses usebinctrfrommtpl=True so it only generates counters, not SetBin statements
        binrange = (6400, 6401)

        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=binrange, defaultrm1bin=-64, defaultrm2bin=-8)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-64)))])
        PyMtpl().main_one(PyObj)

        readout = File('out.mtpl').read()
        # TC with usebinctrfrommtpl=True uses counter names without SetBin
        self.assertIn("IncrementCounters FUN::fail_Instance1_n1", readout)
        self.assertIn("IncrementCounters FUN::fail_Instance1_n2", readout)
        # Verify rm1 and rm2 ports exist
        self.assertIn("Result -1", readout)
        self.assertIn("Result -2", readout)

    @with_(TempDir, chdir=True)
    def test_tc_defaultrmbins_negbin_34dig(self):
        # Test for defaultrmXbin with negative 3-4 digit bin values
        # TC uses usebinctrfrommtpl=True so it only generates counters, not SetBin statements
        binrange = [(6401, 6401), (805, 806)]

        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=binrange, defaultrm1bin=-6401, defaultrm2bin=-805)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-6401)))])
        PyMtpl().main_one(PyObj)

        readout = File('out.mtpl').read()
        # TC with usebinctrfrommtpl=True uses counter names without SetBin
        self.assertIn("IncrementCounters FUN::fail_Instance1_n1", readout)
        self.assertIn("IncrementCounters FUN::fail_Instance1_n2", readout)
        # Verify rm1 and rm2 ports exist
        self.assertIn("Result -1", readout)
        self.assertIn("Result -2", readout)

    @with_(TempDir, chdir=True)
    def test_tc_defaultrmbins_posbin(self):
        # Test for defaultrmXbin with 8 digit positive bin value
        # TC uses usebinctrfrommtpl=True so it only generates counters, not SetBin statements
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(6400, 6401), defaultrm1bin=98123456, defaultrm2bin=99567890)
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-64)))])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        # TC with usebinctrfrommtpl=True uses counter names without SetBin
        self.assertIn("IncrementCounters FUN::fail_Instance1_n1", readout)
        self.assertIn("IncrementCounters FUN::fail_Instance1_n2", readout)
        # Verify rm1 and rm2 ports exist
        self.assertIn("Result -1", readout)
        self.assertIn("Result -2", readout)

    @with_(TempDir, chdir=True)
    def test_tc_defaultrmbins_directset(self):
        # Test for defaultrmXbin with a direct string set
        # TC uses usebinctrfrommtpl=True so it only generates counters, not SetBin statements
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(6400, 6401), defaultrm1bin='b98123456_FAIL_TC_SHARED_BIN_n1', defaultrm2bin='b99567890_fail_FUN_shared_bin_n2')
            subflow = Flow('SubFlow1', [VminTC(name="Instance1", EndVoltageLimits="0.9", _fitem=Fitem(r0=pFail(setbin=-64)))])
        PyMtpl().main_one(PyObj)
        readout = File('out.mtpl').read()
        # TC with usebinctrfrommtpl=True uses counter names without SetBin
        self.assertIn("IncrementCounters FUN::fail_Instance1_n1", readout)
        self.assertIn("IncrementCounters FUN::fail_Instance1_n2", readout)
        # Verify rm1 and rm2 ports exist
        self.assertIn("Result -1", readout)
        self.assertIn("Result -2", readout)

    @with_(TempDir, chdir=True)
    def test_tc_incorrect_defaultrm1_bin(self):
        # Test that -98 is not allowed for defaultrm1bin
        with self.assertRaisesRegex(ErrorUser, "equal to -98 or -99 is not allowed"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem(rm1=pFail(),
                                        r2=pFail(setbin=801)
                                        )
                           )])

            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be a -HB value"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm1bin=-98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be an 8 digit value"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm1bin=98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm1bin='90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm1bin='b90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

    @with_(TempDir, chdir=True)
    def test_tc_incorrect_defaultrm2_bin(self):
        # Test that -99 is not allowed for defaultrm2bin
        with self.assertRaisesRegex(ErrorUser, "equal to -98 or -99 is not allowed"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm2bin=-99)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME',
                                        rm1=pFail(),
                                        r2=pFail(setbin=801)))])

            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be a -HB value"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm2bin=-98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must be an 8 digit value"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm2bin=98888)
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm2bin='90999090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "must start with b and contain"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm2bin='b98989090_fail')
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)

        Initialize.clear_all()
        with self.assertRaisesRegex(ErrorUser, "is not valid"):
            class PyObj:
                output = InitializeTestChip('out', 'FUN', binrange=(800, 804), defaultrm2bin=['test', 'array'])
                subflow = Flow('SubFlow1', [
                    VminTC(name="Instance1", EndVoltageLimits="0.9",
                           _fitem=Fitem('SAME', rm1=pFail(), r2=pFail(setbin=801)))])
            PyMtpl().main_one(PyObj)


class TestInitializeTestChip(TestCase):
    # Unit tests for InitializeTestChip function
    def setUp(self):
        Initialize.clear_all()

    @with_(TempDir, chdir=True)
    def test_initializetc_basic(self):
        # Test basic InitializeTestChip usage
        class PyObj:
            output = InitializeTestChip('out', 'TestModule', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        PyMtpl().main_one(PyObj)
        self.assertTrue(os.path.exists('out.mtpl'))

    @with_(TempDir, chdir=True)
    def test_initializetc_with_defaultrmbins(self):
        # Test InitializeTestChip with defaultrm1bin and defaultrm2bin
        # TC uses usebinctrfrommtpl=True so it only generates counters, not SetBin statements
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450), defaultrm1bin=-44, defaultrm2bin=-45)
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # TC with usebinctrfrommtpl=True uses counter names without SetBin
        self.assertIn('fail_Instance1_n1', mtpl_content)
        self.assertIn('fail_Instance1_n2', mtpl_content)
        # Verify rm1 and rm2 ports exist
        self.assertIn('Result -1', mtpl_content)
        self.assertIn('Result -2', mtpl_content)

    @with_(TempDir, chdir=True)
    def test_initializetc_usebinctrfrommtpl(self):
        # Test that InitializeTestChip uses usebinctrfrommtpl=True by default
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        PyMtpl().main_one(PyObj)
        # Verify that it runs successfully with usebinctrfrommtpl=True
        self.assertTrue(os.path.exists('out.mtpl'))

    @with_(TempDir, chdir=True)
    def test_initializetc_tosversion(self):
        # Test that InitializeTestChip uses TOS4 by default
        class PyObj:
            output = InitializeTestChip('out', 'FUN', binrange=(4400, 4450))
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(r0=pFail(setbin=-44)))
            ])
        PyMtpl().main_one(PyObj)
        mtpl_content = File('out.mtpl').read()
        # TOS4 uses different syntax - check for tos4 specific elements
        self.assertIn('Flow SubFlow1', mtpl_content)
        self.assertIn('CSharpTest', mtpl_content)

    @with_(TempDir, chdir=True)
    def test_initializetc_edcportctrbinrange(self):
        # Test that InitializeTestChip has default edcportctrbinrange=(9900,9999)
        class PyObj:
            output = InitializeTestChip('out', 'FUN')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(edc=True))
            ])
        PyMtpl().main_one(PyObj)
        # Verify that EDC tests work with the default range
        self.assertTrue(os.path.exists('out.mtpl'))
        mtpl_content = File('out.mtpl').read()
        self.assertIn('fail_Instance1_n1', mtpl_content)
        self.assertIn('fail_Instance1_n2', mtpl_content)
        self.assertIn('fail_Instance1_0', mtpl_content)
        self.assertIn('pass_Instance1_1', mtpl_content)

    @with_(TempDir, chdir=True)
    def test_initializetc_canbeoverridden(self):
        # Test that InitializeTestChip has default edcportctrbinrange=(9900,9999)
        class PyObj:
            output = InitializeTestChip('out', 'FUN')
            subflow = Flow('SubFlow1', [
                VminTC(name="Instance1", EndVoltageLimits="0.9",
                       _fitem=Fitem(edc=True,
                                    rm1=pPass(),
                                    r2=pFail(),
                                    r3=pFail(setbin=12345678),
                                    ))
            ])
        PyMtpl().main_one(PyObj)
        # Verify that EDC tests work with the default range
        self.assertTrue(os.path.exists('out.mtpl'))
        mtpl_content = File('out.mtpl').read()
        self.assertIn('pass_Instance1_n1', mtpl_content)
        self.assertIn('fail_Instance1_n2', mtpl_content)
        self.assertIn('fail_Instance1_0', mtpl_content)
        self.assertIn('pass_Instance1_1', mtpl_content)
        self.assertIn('fail_Instance1_2', mtpl_content)
        self.assertIn('fail_Instance1_3', mtpl_content)
        self.assertIn('SetBin b12345678_fail_FUN_Instance1_3', mtpl_content)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
