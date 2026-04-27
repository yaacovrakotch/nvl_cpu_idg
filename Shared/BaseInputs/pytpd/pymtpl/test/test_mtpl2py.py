#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for methods
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from pymtpl.mtpl2py import *
from main.pymtpl import PyMtplArgs
from unittest.mock import patch, MagicMock
import sys


class TestGenPy(TestCase):
    @with_(TempDir, chdir=True)
    def test_integration(self):
        cmd = f'pymtpl.py -genpy {UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.mtpl -env {UT_DIR_REPO}/sudheer_unit_test/mtpl2py/POR_TP/Class_NVL_H81/EnvironmentFile.env'.split()
        with MockVar(sys, "argv", cmd):
            self.assertEqual(PyMtplArgs().main(), 3)
        self.assertGoldEqual(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.py', f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.gold.py')

    def test_get_tp_dir(self):
        # Test case for getting the TP dir from a given mtpl file.
        print(f'{UT_DIR_REPO}')
        obj1 = GenPy(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/test_SCN_UNCORE_C68C.mtpl')
        self.assertEqual(obj1.tpdir, f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py')

    def test_get_sourcefile_path(self):
        # Test case for getting the source file name from a given input mtpl file
        obj1 = GenPy(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/test_SCN_UNCORE_C68C.mtpl')
        obj1.get_sourcefile_path()
        self.assertEqual(obj1.sourcefile, f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/test_SCN_UNCORE_C68C.py')

    def test_get_sourcefile_path_nonmtpl(self):
        # Test case for getting the source file name from a given input mtpl file
        obj1 = GenPy(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/test_SCN_UNCORE_C68C.txt')
        with self.assertRaisesRegex(ErrorUser, 'not an .mtpl file'):
            obj1.get_sourcefile_path()

    def test_get_dutflow_dict(self):
        # Test case for extracting the dutflow info from the mtpl
        obj1 = GenPy(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/test_SCN_UNCORE_C68C.mtpl')
        obj1.get_dutflow_dict_and_modulename()
        self.assertEqual(len(obj1.df), 4)
        self.assertEqual(len(obj1.df_edckill), 2)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_basic_ut(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest CCA {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
DUTFlow MAIN1 @END {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Fail";
 SetBin SoftBins.b90757501_fail_NSIO;
                        Return 0;
                }
        }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
from pymtpl.por_methods import iCSimpleScoreboardTest
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, Import, TrialParamSpec, Spec
from pymtpl.uservars import UserVars

Initialize('Test_array', 'array')

##############################################################
# UserVars
# region
##############################################################
usrv_BYPASSVars = UserVars('array', setname='BYPASSVars')
usrv_BYPASSVars.bypvar = "arraybyp"
usrv_BYPASSVars.var2 = ('2', str)
usrv_BYPASSVars.bype = ('"okARR_"+bypvar', str)
##############################################################
# endregion UserVars
##############################################################

##############################################################
# MAIN1
# region
##############################################################
MAIN1 = Flow('MAIN1', [
    iCSimpleScoreboardTest(name = 'CCA',
        timings = 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100',
        level = 'BASE::DDR_univ_lvl_max_lvl',
        Patlist = 'shops_L_list',
        bypass_global = '0',
        base_number = 2160,
        _fitem = Fitem(
            r0=pFail(setbin=90757501),
        )
    ),
], dtag='END')
##############################################################
# endregion MAIN1
##############################################################
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_basic(self):
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
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
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
from pymtpl.por_methods import VminTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, Import, TrialParamSpec, Spec
from pymtpl.uservars import UserVars

Initialize('Test_array', 'array')

##############################################################
# UserVars
# region
##############################################################
usrv_BYPASSVars = UserVars('array', setname='BYPASSVars')
usrv_BYPASSVars.bypvar = "arraybyp"
usrv_BYPASSVars.var2 = ('2', str)
usrv_BYPASSVars.bype = ('"okARR_"+bypvar', str)
##############################################################
# endregion UserVars
##############################################################

##############################################################
# SubFlow1
# region
##############################################################
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = TrialParamSpec('FlowMatrix.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        rm2=pFail(ret=-2, trialaction="Exit"),
        rm1=pFail(ret=-1, trialaction="Exit"),
        r0=pFail(ret=0, ctr=1, trialaction="Exit"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            rm2=pFail(ret=-2, setbin=90999901),
            rm1=pFail(ret=-1, setbin=90989801),
            r0=pFail(setbin=90444427, ctr=44270003),
            r1=pPass(),
        )
    ),
])
##############################################################
# endregion SubFlow1
##############################################################
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_mtt_bin(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
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

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = TrialParamSpec('FlowMatrix.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        r0=pFail(ret=0, setbin=4781, ctr=1, trialaction="Exit"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=90444427, ctr=44270003),
            r1=pPass(),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_incorrect_mtt_counter(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n45420001_fail_Instance1_0";
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

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        with self.assertRaisesRegex(ErrorUser, 'Please verify the validity of the counter'):
            obj1.main()

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_goto_string(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            GoTo MTTName_2;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
            GoTo MTTName_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = TrialParamSpec('FlowMatrix.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        r0=pFail(setbin=4781, ctr=1, goto='MTTName_2', trialaction="Exit"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=90444427, ctr=44270003, goto='MTTName_2'),
            r1=pPass(),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_spec_inputs(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        EndVoltageLimits = array.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            GoTo MTTName_2;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
            GoTo MTTName_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = Spec('array.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        r0=pFail(setbin=4781, ctr=1, goto='MTTName_2', trialaction="Exit"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=90444427, ctr=44270003, goto='MTTName_2'),
            r1=pPass(),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_import_lines(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;
Import array.usrv;
Import array_timing.tcg;
Import PvalTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        EndVoltageLimits = array.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            GoTo MTTName_2;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
            GoTo MTTName_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
from pymtpl.por_methods import VminTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, Import, TrialParamSpec, Spec

Initialize('Test_array', 'array')

Import('array.usrv')
Import('array_timing.tcg')
Import('PvalTC.xml')

SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = Spec('array.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        r0=pFail(setbin=4781, ctr=1, goto='MTTName_2', trialaction="Exit"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=90444427, ctr=44270003, goto='MTTName_2'),
            r1=pPass(),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_nonmtt_spec(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest CCA {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "array.shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
DUTFlow MAIN1  {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Fail";
 SetBin SoftBins.b90757501_fail_NSIO;
                        Return 0;
                }
        }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
MAIN1 = Flow('MAIN1', [
    iCSimpleScoreboardTest(name = 'CCA',
        timings = 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100',
        level = 'BASE::DDR_univ_lvl_max_lvl',
        Patlist = 'array.shops_L_list',
        bypass_global = '0',
        base_number = 2160,
        _fitem = Fitem(
            r0=pFail(setbin=90757501),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_no_gotostring_no_retstring(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        EndVoltageLimits = array.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            GoTo MTTName_2;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
            GoTo MTTName_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = Spec('array.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        r0=pFail(setbin=4781, ctr=1, goto='MTTName_2', trialaction="Exit"),
        r1=pPass(trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=90444427, ctr=44270003, goto='MTTName_2'),
            r1=pPass(),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_edcstring(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        EndVoltageLimits = array.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            ## EDC ### SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            GoTo MTTName_2;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
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
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
            GoTo MTTName_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = Spec('array.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        r0=pFail(ctr=1, goto='MTTName_2', trialaction="Exit"),
        r1=pPass(trialaction="Exit"),
        _fitem = Fitem(edc=True,
            r0=pFail(setbin=90444427, ctr=44270003, goto='MTTName_2'),
            r1=pPass(),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dutflowname_testname_different(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        EndVoltageLimits = array.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            ## EDC ### SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            GoTo MTTName_2;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname1 MTTtname @EDC
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
            GoTo MTTName_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = Spec('array.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        r0=pFail(ctr=1, goto='MTTName_2', trialaction="Exit"),
        r1=pPass(trialaction="Exit"),
        _fitem = Fitem('MTTtname1', edc=True,
            r0=pFail(setbin=90444427, ctr=44270003, goto='MTTName_2'),
            r1=pPass(),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_composite(self):
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;
TestPlan array;

Test VminTC STUCKAT_NONCCF_SB_E_BEGCPU_X_VNNAON_X_X_ALL_BCLK
{
    Patlist = "scn_cdie_begcpuf1_nonccf_stuckat_mio200_edt_classhvm_list";
    BypassPort = SCN_UNCORE_C68C_Rules.Fuselocncheck(1, -1);
}

MultiTrialTest ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_CLR_F1_FREQ_CCF
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC "ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_" + CustomFlowMatrixSpecs.CLR_F1_FREQ_MHz + "_CCF_" + FlowMatrix.bin + ""
    {
        Patlist = "scn_cdie_sclrf1_ccf_atspeed_mio200_edt_classhvm_list";
        BypassPort = -1;
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
            TrialAction "Next";
            IncrementCounters "SCN_UNCORE_C68C::n" + FlowMatrix.bin + "7230_fail_ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_X_CCF_0";
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
}
DUTFlow BEGCPU_HVM_NONCCF
{
    DUTFlowItem ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_CLR_F1_FREQ_CCF ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_CLR_F1_FREQ_CCF
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
            IncrementCounters SCN_UNCORE_C68C::n90470015_fail_ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_CLR_F1_FREQ_CCF_0;
            GoTo STUCKAT_NONCCF_SB_E_BEGCPU_X_VNNAON_X_X_ALL_BCLK;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo STUCKAT_NONCCF_SB_E_BEGCPU_X_VNNAON_X_X_ALL_BCLK;
        }
    }
    DUTFlowItem STUCKAT_NONCCF_SB_E_BEGCPU_X_VNNAON_X_X_ALL_BCLK STUCKAT_NONCCF_SB_E_BEGCPU_X_VNNAON_X_X_ALL_BCLK @EDC
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
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
DUTFlow BEGCPU_HVM
{
    DUTFlowItem BEGCPU_HVM_NONCCF BEGCPU_HVM_NONCCF
    {
        Result -2 { Property PassFail = "Fail"; Return -2; }
        Result -1 { Property PassFail = "Fail"; Return -1; }
        Result 0 { Property PassFail = "Fail"; Return 0; }
        Result 1 { Property PassFail = "Pass";
            Return 1; }
    }
}

DUTFlow SCN_UNCORE_C68C_BEGCPU
{
    DUTFlowItem BEGCPU_HVM BEGCPU_HVM1
    {
        Result -2 { Property PassFail = "Fail"; Return -2; }
        Result -1 { Property PassFail = "Fail"; Return -1; }
        Result 0 { Property PassFail = "Fail"; Return 0; }
        Result 1 { Property PassFail = "Pass"; Return 1; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
BEGCPU_HVM_NONCCF = Flow('BEGCPU_HVM_NONCCF', [
    NativeMultiTrial(name = 'ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_CLR_F1_FREQ_CCF',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = '"ATSPEED_CCF_VMIN_K_SCLRF1_X_VCCF_F1_" + CustomFlowMatrixSpecs.CLR_F1_FREQ_MHz + "_CCF_" + FlowMatrix.bin + ""',
            Patlist = 'scn_cdie_sclrf1_ccf_atspeed_mio200_edt_classhvm_list',
            BypassPort = -1,
        ),
        rm2=pFail(ret=-2, trialaction="Exit"),
        rm1=pFail(ret=-1, trialaction="Exit"),
        r0=pFail(ret=0, ctr=7230, trialaction="Next"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            rm2=pFail(ret=-2, setbin=90999901),
            rm1=pFail(ret=-1, setbin=90989801),
            r0=pFail(ctr=90470015, goto='NEXT'),
            r1=pPass(),
        )
    ),
    VminTC(name = 'STUCKAT_NONCCF_SB_E_BEGCPU_X_VNNAON_X_X_ALL_BCLK',
        Patlist = 'scn_cdie_begcpuf1_nonccf_stuckat_mio200_edt_classhvm_list',
        BypassPort = Spec('SCN_UNCORE_C68C_Rules.Fuselocncheck(1, -1)'),
        _fitem = Fitem(edc=True,
            rm2=pFail(ret=-2, setbin=90999901),
            rm1=pFail(ret=-1, setbin=90989801),
            r0=pFail(ret=0),
            r1=pPass(),
        )
    ),
])
BEGCPU_HVM = Flow('BEGCPU_HVM', [
    Fitem('SAME', BEGCPU_HVM_NONCCF,
            rm2=pFail(ret=-2),
            rm1=pFail(ret=-1),
            r0=pFail(),
            r1=pPass(),
    ),
])
SCN_UNCORE_C68C_BEGCPU = Flow('SCN_UNCORE_C68C_BEGCPU', [
    Fitem('BEGCPU_HVM', 'BEGCPU_HVM1',
            rm2=pFail(ret=-2),
            rm1=pFail(ret=-1),
            r0=pFail(),
            r1=pPass(),
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_portinfo_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_testmethod_info_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_flow_items', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_run_twice_does_not_output(self):
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
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
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()

        # run a second time while capturing output
        with CaptureStdoutLog() as cap:
            obj1 = GenPy('./Modules/ARR/array.mtpl')
            obj1.main()  # Run it again to ensure no issues
            output = cap.getvalue()
            self.assertRegex(output, "NO UPDATE")

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_product_none(self):
        from gadget.helperclass import OPT
        orig_product = getattr(OPT, "product", None)
        OPT.product = 'Anything'
        try:
            File('./Modules/ARR/array.mtpl').touch('''
    TestPlan array;

    Import VminTC.xml;
    Import array.usrv;
    Import array_timing.tcg;
    Import PvalTC.xml;

    MultiTrialTest MTTtname
    {
        TrialVariable IP_CPU_BASE::FlowDomain.Default;
        TrialVariableExitAction "Continue";
        CSharpTrialTest VminTC Instance1
        {
            EndVoltageLimits = array.End_Voltage;
            FailCaptureCount = 999;
            Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
            ConfigurationFile = GetEnvironmentVariable('~HDMT_TP_BASE_DIR')+"\\Modules\\ARR\\InputFiles\\IDCODE\\IDCODE_A0.csv"; # path which needs escapes
            TrialResult 0
            {
                PassFail Fail;
                TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
                SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
                IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
                GoTo MTTName_2;
            }
            TrialResult 1
            {
                PassFail Pass;
                TrialAction "Exit";
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
                IncrementCounters FUN::n44270003_fail_MTTtname_0;
                GoTo MTTName_2;
            }
            Result 1
            {
                Property PassFail = "Pass";
                Return 1;
            }
        }

    }
    ''', newfile=True)
            obj1 = GenPy('./Modules/ARR/array.mtpl')
            obj1.main()
            expect = '''
SubFlow1 = Flow('SubFlow1', [
    NativeMultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = "Continue",
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = Spec('array.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
            ConfigurationFile = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"\\\\Modules\\\\ARR\\\\InputFiles\\\\IDCODE\\\\IDCODE_A0.csv"'),
        ),
        r0=pFail(setbin=4781, ctr=1, goto='MTTName_2', trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=90444427, ctr=44270003, goto='MTTName_2'),
            r1=pPass(),
        )
    ),
])
    '''
            self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)
        finally:
            OPT.product = orig_product

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_uservars_lines', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_edcbin(self):
        # Test that we can parse in ##EDC## bins
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan SCN_CORE;


# Test Counter Definition

Counters
{

}

CSharpTest PrimeScoreboardTestMethod ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT
{
    Patlist = "scn_guadi_hdmt_poc_int_dc_full_list";
    LevelsTc = "BASE::lvl_base_STC_setup";
    TimingsTc = "BASE::cbr_tim_dummy_t100_s100";
}

Flow SCN_CORE_END @END
{

   FlowItem ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90992222_fail_FAIL_DUMMY_n2;
            ##INCORRECT## SetBin b90992222_fail_FAIL_DUMMY_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90981111_fail_FAIL_DUMMY_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail"; # ignored comment
            ##EDC## SetBin b90681234_fail_FAIL_DUMMY_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SCN_CORE_END = Flow('SCN_CORE_END', [
    PrimeScoreboardTestMethod(name = 'ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT',
        Patlist = 'scn_guadi_hdmt_poc_int_dc_full_list',
        LevelsTc = 'BASE::lvl_base_STC_setup',
        TimingsTc = 'BASE::cbr_tim_dummy_t100_s100',
        _fitem = Fitem(edc=True,
            rm2=pFail(ret=-2, setbin=90992222),
            rm1=pFail(ret=-1, setbin=90981111),
            r0=pFail(setbin=90681234),
            r1=pPass(),
        )
    ),
], dtag='END')
'''

        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    def test_get_port_info_no_identifier(self):
        self.assertIsNone(GenPy._get_port_info('', 'b90992222_fail_FAIL_DUMMY'))  # missing _n2

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_write_portinfo_mtt_skips_999(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
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

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()

        # Mock an MTT test with a special indicator port 999
        lines = []
        lines.extend(obj1.write_portinfo_lines({999: 'b90992222_fail_FAIL_DUMMY_n2'}, ismtt=True))  # skip 999
        lines.extend(obj1.write_portinfo_lines({999: 'b90992222_fail_FAIL_DUMMY_n2'}, ismtt=False))  # skip 999
        self.assertEqual(lines, ['        )', '    ),'])  # should be empty except for closing parens


class TestGenPyDMR(TestCase):
    # make sure all tests use DMRClass
    def setUp(self):
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        OPT.product = 'DMRClass'

    # reset OPT.product after tests
    def tearDown(self):
        OPT.product = self._orig_product

    @with_(TempDir, chdir=True)
    def test_integration(self):
        cmd = f'pymtpl.py -genpy {UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.mtpl -product DMRClass'.split()
        with MockVar(sys, "argv", cmd):
            self.assertEqual(PyMtplArgs().main(), 3)
        self.assertGoldEqual(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.py', f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.dmr.gold.py')

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_flow_items', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_import_lines(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import "ARR_EXAMPLE.usrv";

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        EndVoltageLimits = array.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            GoTo MTTName_2;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
            GoTo MTTName_2;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
Import('ARR_EXAMPLE.usrv')
'''

        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_escape_paths(self):
        # Test that backslashes in paths are escaped correctly
        # Note that the compare actualy has 4 \ but the actual result only has 2, to make the compare work. it's correct as is.
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

CSharpTest CtvDecoderSpm CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE
{
    BypassPort = -1;
    ConfigurationFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"\\Modules\\SIO_BSCAN_CBB\\InputFiles\\IDCODE\\IDCODE_A0.csv";
    CtvCapturePins = "BT_HVM_TDO_2";
    LevelsTc = "IP_CBB::IP_CBB_BASE::lvl_base_cbb_basic_allps";
    Patlist = "sio_bscan_gpio_fullchain_continuity";
    TimingsTc = "IP_CBB::IP_CBB_BASE::cbb_tim_d11r11_1x_t100_h1400";
    ItuffHRYFailurePrint = "ENABLED";
}

DUTFlow SubFlow1
{
    FlowItem CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90998783_fail_SIO_BSCAN_CBB_CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE_n2;
            IncrementCounters SIO_BSCAN_CBB::n90998783_fail_CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90988783_fail_SIO_BSCAN_CBB_CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE_n1;
            IncrementCounters SIO_BSCAN_CBB::n90988783_fail_CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90250137_fail_SIO_BSCAN_CBB_CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE_0;
            IncrementCounters SIO_BSCAN_CBB::n90250137_fail_CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    CtvDecoderSpm(name = 'CHAIN_X_CTVDEC_K_BGNCBB_TAP_INF_VNOM_X_CDIEIDCODE',
        BypassPort = -1,
        ConfigurationFile = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"\\\\Modules\\\\SIO_BSCAN_CBB\\\\InputFiles\\\\IDCODE\\\\IDCODE_A0.csv"'),
        CtvCapturePins = 'BT_HVM_TDO_2',
        LevelsTc = 'IP_CBB::IP_CBB_BASE::lvl_base_cbb_basic_allps',
        Patlist = 'sio_bscan_gpio_fullchain_continuity',
        TimingsTc = 'IP_CBB::IP_CBB_BASE::cbb_tim_d11r11_1x_t100_h1400',
        ItuffHRYFailurePrint = 'ENABLED',
        _fitem = Fitem(
            r0=pFail(setbin=-25),
        )
    ),
])
'''

        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_branching_via_port1(self):
        # Test that branching via port1 works correctly
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan SCN_CORE;


# Test Counter Definition

Counters
{

}

CSharpTest PrimeScoreboardTestMethod ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT
{
    Patlist = "scn_guadi_hdmt_poc_int_dc_full_list";
    LevelsTc = "BASE::lvl_base_STC_setup";
    TimingsTc = "BASE::cbr_tim_dummy_t100_s100";
}

CSharpTest PrimeScoreboardTestMethod ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_EXT
{
    Patlist = "scn_guadi_hdmt_poc_ext_dc_full_list";
    LevelsTc = "BASE::lvl_base_STC_setup";
    TimingsTc = "BASE::cbr_tim_dummy_t100_s100";
}

CSharpTest PrimeScoreboardTestMethod ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE0
{
    Patlist = "scn_guadi_hdmt_poc_int_dc_die0_full_list";
    LevelsTc = "BASE::lvl_base_STC_setup";
    TimingsTc = "BASE::cbr_tim_dummy_t100_s100";
}

CSharpTest PrimeScoreboardTestMethod ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE1
{
    Patlist = "scn_guadi_hdmt_poc_int_dc_die1_full_list";
    LevelsTc = "BASE::lvl_base_STC_setup";
    TimingsTc = "BASE::cbr_tim_dummy_t100_s100";
}


Flow SCN_CORE_END @END
{

   FlowItem ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT @EDC
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
            Property PassFail = "Pass";
            GoTo ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_EXT;
        }
    }

    FlowItem ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_EXT ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_EXT @EDC
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
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

    FlowItem ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE0 ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE0 @EDC
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
            GoTo ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE1;
        }
    }

    FlowItem ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE1 ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE1 @EDC
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
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SCN_CORE_END = Flow('SCN_CORE_END', [
    PrimeScoreboardTestMethod(name = 'ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT',
        Patlist = 'scn_guadi_hdmt_poc_int_dc_full_list',
        LevelsTc = 'BASE::lvl_base_STC_setup',
        TimingsTc = 'BASE::cbr_tim_dummy_t100_s100',
        _fitem = Fitem(edc=True,
            r0=pPass(goto='ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE0'),
        )
    ),
    PrimeScoreboardTestMethod(name = 'ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_EXT',
        Patlist = 'scn_guadi_hdmt_poc_ext_dc_full_list',
        LevelsTc = 'BASE::lvl_base_STC_setup',
        TimingsTc = 'BASE::cbr_tim_dummy_t100_s100',
        _fitem = Fitem(edc=True,
            r0=pFail(ret=1),
            r1=pPass(ret=1),
        )
    ),
    PrimeScoreboardTestMethod(name = 'ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE0',
        Patlist = 'scn_guadi_hdmt_poc_int_dc_die0_full_list',
        LevelsTc = 'BASE::lvl_base_STC_setup',
        TimingsTc = 'BASE::cbr_tim_dummy_t100_s100',
        _fitem = Fitem(edc=True,
            r0=pFail(),
        )
    ),
    PrimeScoreboardTestMethod(name = 'ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT_DIE1',
        Patlist = 'scn_guadi_hdmt_poc_int_dc_die1_full_list',
        LevelsTc = 'BASE::lvl_base_STC_setup',
        TimingsTc = 'BASE::cbr_tim_dummy_t100_s100',
        _fitem = Fitem(edc=True,
            r0=pFail(),
        )
    ),
], dtag='END')
'''

        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dutflowname_testname_different_DMR(self):
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

CSharpTest PrimeScreenTestTestMethod CTRL_X_SCREEN_E_CHKIMHFIXDIGWF1_X_X_X_F1_RATIO1_MCR_FREQ_UPDATE
{
    ScreenTestSet = "MCR_RATIO_CHANGE_VALUE";
    ScreenTestsFile = "Dummy";
}


DUTFlow SubFlow1
{
    FlowItem ShortName CTRL_X_SCREEN_E_CHKIMHFIXDIGWF1_X_X_X_F1_RATIO1_MCR_FREQ_UPDATE @EDC
    {
      Result 0
      {
          Property PassFail = "Fail";
          IncrementCounters MIO_DDR::n90112131_fail_CTRL_X_SCREEN_E_CHKIMHFIXDIGWF1_X_X_X_F1_RATIO1_MCR_FREQ_UPDATE_0;
          GoTo CTRL_X_PATCFG_E_CHKIMHFIXDIGWF1_TAP_FIXDIG_X_F1_RATIO1_DDR_FREQ_UPDATE;
      }

  }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    PrimeScreenTestTestMethod(name = 'CTRL_X_SCREEN_E_CHKIMHFIXDIGWF1_X_X_X_F1_RATIO1_MCR_FREQ_UPDATE',
        ScreenTestSet = 'MCR_RATIO_CHANGE_VALUE',
        ScreenTestsFile = 'Dummy',
        _fitem = Fitem('ShortName', edc=True,
            r0=pFail(goto='CTRL_X_PATCFG_E_CHKIMHFIXDIGWF1_TAP_FIXDIG_X_F1_RATIO1_DDR_FREQ_UPDATE'),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_edcbin(self):
        # Test that we can parse in ##EDC## bins
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan SCN_CORE;


# Test Counter Definition

Counters
{

}

CSharpTest PrimeScoreboardTestMethod ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT
{
    Patlist = "scn_guadi_hdmt_poc_int_dc_full_list";
    LevelsTc = "BASE::lvl_base_STC_setup";
    TimingsTc = "BASE::cbr_tim_dummy_t100_s100";
}

Flow SCN_CORE_END @END
{

   FlowItem ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT @EDC
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
            ##EDC## SetBin b90681234_fail_FAIL_DUMMY_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SCN_CORE_END = Flow('SCN_CORE_END', [
    PrimeScoreboardTestMethod(name = 'ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT',
        Patlist = 'scn_guadi_hdmt_poc_int_dc_full_list',
        LevelsTc = 'BASE::lvl_base_STC_setup',
        TimingsTc = 'BASE::cbr_tim_dummy_t100_s100',
        _fitem = Fitem(edc=True,
            r0=pFail(setbin=-68),
        )
    ),
], dtag='END')
'''

        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)


class TestGenPyCBR(TestCase):
    # make sure all tests use CBRClass
    def setUp(self):
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        OPT.product = 'CBRClass'

    # reset OPT.product after tests
    def tearDown(self):
        OPT.product = self._orig_product

    @with_(TempDir, chdir=True)
    def test_integration(self):
        cmd = f'pymtpl.py -genpy {UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.mtpl -product CBRClass'.split()
        with MockVar(sys, "argv", cmd):
            self.assertEqual(PyMtplArgs().main(), 3)
        self.assertGoldEqual(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.py', f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.cbr.gold.py')

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_edcbin(self):
        # Test that we can parse in ##EDC## bins
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan SCN_CORE;


# Test Counter Definition

Counters
{

}

CSharpTest PrimeScoreboardTestMethod ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT
{
    Patlist = "scn_guadi_hdmt_poc_int_dc_full_list";
    LevelsTc = "BASE::lvl_base_STC_setup";
    TimingsTc = "BASE::cbr_tim_dummy_t100_s100";
}

Flow SCN_CORE_END @END
{

   FlowItem ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT @EDC
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
            ##EDC## SetBin b90681234_fail_FAIL_DUMMY_0;
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            ##EDC## this should be ignored
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SCN_CORE_END = Flow('SCN_CORE_END', [
    PrimeScoreboardTestMethod(name = 'ATPG_CORE_HRY_E_END_STF_VCCCORE_MIN_LFM_INT',
        Patlist = 'scn_guadi_hdmt_poc_int_dc_full_list',
        LevelsTc = 'BASE::lvl_base_STC_setup',
        TimingsTc = 'BASE::cbr_tim_dummy_t100_s100',
        _fitem = Fitem(edc=True,
            r0=pFail(setbin=-68),
        )
    ),
], dtag='END')
'''

        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)


class TestGenPyCWF(TestCase):
    # make sure all tests use CBRClass
    def setUp(self):
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        OPT.product = 'CWFClass'

    # reset OPT.product after tests
    def tearDown(self):
        OPT.product = self._orig_product

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_basic(self):
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    TrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
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
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
from pymtpl.por_methods import VminTC
from pymtpl.core import Flow, Fitem, pPass, pFail, InitializeCWFClass, MultiTrial, AUTO, Import, TrialParamSpec, Spec
from pymtpl.uservars import UserVars
from pymtpl.helpers import get_bin_limits_from_json

# Importing bin limits from json file for array
bin_limits = get_bin_limits_from_json('array')

InitializeCWFClass('Test_array', 'array', binrange=bin_limits, edcportctrbinrange=bin_limits)

##############################################################
# UserVars
# region
##############################################################
usrv_BYPASSVars = UserVars('array', setname='BYPASSVars')
usrv_BYPASSVars.bypvar = "arraybyp"
usrv_BYPASSVars.var2 = ('2', str)
usrv_BYPASSVars.bype = ('"okARR_"+bypvar', str)
##############################################################
# endregion UserVars
##############################################################

##############################################################
# SubFlow1
# region
##############################################################
SubFlow1 = Flow('SubFlow1', [
    MultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = Spec('"Continue"'),
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = TrialParamSpec('FlowMatrix.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        rm2=pFail(ret=-2, trialaction="Exit"),
        rm1=pFail(ret=-1, trialaction="Exit"),
        r0=pFail(ret=0, trialaction="Exit"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=-44),
        )
    ),
])
##############################################################
# endregion SubFlow1
##############################################################
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    def test_pass_port_with_counter_no_bin(self):
        # Test get_bin_from_counter for pass port with counter but no bin
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

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
            SetBin SoftBins.b90680000_fail_array_Instance1;
            IncrementCounters array::n90680001_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            IncrementCounters array::p99680002_pass_Instance1_1;
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    VminTC(name = 'Instance1',
        EndVoltageLimits = '0.9',
        FailCaptureCount = 999,
        _fitem = Fitem(
            r0=pFail(setbin=-68),
            r1=pPass(setbin=-68),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    def test_mtt_pass_port_with_counter_no_bin(self):
        # Test get_bin_from_counter for MTT pass port with counter but no bin (ismtt=True path)
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    TrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
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
            IncrementCounters "FUN::n" + FlowMatrix.bin + "4427_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            IncrementCounters "FUN::p" + FlowMatrix.bin + "4428_pass_Instance1_1";
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
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
SubFlow1 = Flow('SubFlow1', [
    MultiTrial(name = 'MTTtname',
        trialvar = 'IP_CPU_BASE::FlowDomain.Default',
        exitaction = Spec('"Continue"'),
        template = VminTC(name = 'Instance1',
            EndVoltageLimits = TrialParamSpec('FlowMatrix.End_Voltage'),
            FailCaptureCount = 999,
            Patlist = 'scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list',
        ),
        rm2=pFail(ret=-2, trialaction="Exit"),
        rm1=pFail(ret=-1, trialaction="Exit"),
        r0=pFail(ret=0, trialaction="Exit"),
        r1=pPass(ret=1, trialaction="Exit"),
        _fitem = Fitem(
            r0=pFail(setbin=-44),
        )
    ),
])
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    def test_get_bin_with_use_first_two_digits_flag(self):
        # Test that get_bin extracts first two digits when flag is True
        from pymtpl.mtpl2py import GenPy, JGSClassDefault, DMRClassDefault

        # Test with JGSClassDefault (flag is True)
        obj_jgs = GenPy.__new__(GenPy)
        obj_jgs.defaults = JGSClassDefault

        # For bin b90440101, with flag=True should extract 90, result should be -90
        setbin = obj_jgs.get_bin('SoftBins.b90440101_fail_test', ismtt=False)
        self.assertEqual(setbin, -90)

        # Test with DMRClassDefault (flag is False, default behavior)
        obj_dmr = GenPy.__new__(GenPy)
        obj_dmr.defaults = DMRClassDefault

        # For bin b90440101, with flag=False should extract 44, result should be -44
        setbin = obj_dmr.get_bin('SoftBins.b90440101_fail_test', ismtt=False)
        self.assertEqual(setbin, -44)

    def test_get_bin_from_counter_with_use_first_two_digits_flag(self):
        # Test that get_bin_from_counter extracts first two digits when flag is True
        from pymtpl.mtpl2py import GenPy, JGSClassDefault, DMRClassDefault

        # Test with JGSClassDefault (flag is True)
        obj_jgs = GenPy.__new__(GenPy)
        obj_jgs.defaults = JGSClassDefault

        # For counter n90440101, with flag=True should extract 90, result should be -90
        setbin = obj_jgs.get_bin_from_counter('Module::n90440101_fail_test', ismtt=False)
        self.assertEqual(setbin, -90)

        # Test with DMRClassDefault (flag is False, default behavior)
        obj_dmr = GenPy.__new__(GenPy)
        obj_dmr.defaults = DMRClassDefault

        # For counter n90440101, with flag=False should extract 44, result should be -44
        setbin = obj_dmr.get_bin_from_counter('Module::n90440101_fail_test', ismtt=False)
        self.assertEqual(setbin, -44)


class TestGenPyJGS(TestCase):
    # make sure all tests use JGS
    def setUp(self):
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        OPT.product = 'JGSClass'

    # reset OPT.product after tests
    def tearDown(self):
        OPT.product = self._orig_product

    @with_(TempDir, chdir=True)
    def test_integration(self):
        cmd = f'pymtpl.py -genpy {UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.mtpl -product JGSClass'.split()
        with MockVar(sys, "argv", cmd):
            self.assertEqual(PyMtplArgs().main(), 3)
        self.assertGoldEqual(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.py', f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_SCN_UNCORE_C68C.jgs.gold.py')


class TestGenPyUserVars(TestCase):
    # Test UserVars parsing and generation in mtpl2py

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_basic_uservars(self):
        # Test basic UserVars with simple types
        # Create .usrv file
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
    Integer MyInt = 20;
    Double MyDouble = -99.0;
    String MyString = "Hello";
    Boolean MyBool = True;
}
''', newfile=True)

        # Create MTPL file (without UserVars inside)
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    bypass_global = "0";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90757501_fail_NSIO;
            Return 0;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        result = File('Modules/ARR/array.py').read()

        # Check that UserVars is imported
        self.assertRegex(result, r'from pymtpl\.uservars import UserVars')

        # Check UserVars creation
        self.assertRegex(result, r"usrv = UserVars\('array'\)")

        # Check variable assignments
        self.assertRegex(result, r'usrv\.MyInt = 20')
        self.assertRegex(result, r'usrv\.MyDouble = -99\.0')
        self.assertRegex(result, r'usrv\.MyString = "Hello"')
        self.assertRegex(result, r'usrv\.MyBool = True')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_uservars_with_arrays(self):
        # Test UserVars with array types
        # Create .usrv file
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
    Array<Integer> MyIntArray = [1, 2, 3, 4, 5];
    Array<Double> MyDoubleArray = [1.1, 2.2, 3.3];
    Array<String> MyStringArray = ["A", "B", "C"];
    Array<Boolean> MyBoolArray = [True, False, True];
}
''', newfile=True)

        # Create MTPL file
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        result = File('Modules/ARR/array.py').read()

        # Check array variable assignments
        self.assertRegex(result, r'usrv\.MyIntArray = \[1,2,3,4,5\]')
        self.assertRegex(result, r'usrv\.MyDoubleArray = \[1\.1,2\.2,3\.3\]')
        self.assertRegex(result, r'usrv\.MyStringArray = \["A","B","C"\]')
        self.assertRegex(result, r'usrv\.MyBoolArray = \[True,False,True\]')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_uservars_with_spec_expressions(self):
        # Test UserVars with Spec expressions (module references, unquoted strings)
        # Create .usrv file
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
    Double MySpecDouble = SomeComplexExpression();
    String MyRefString = array.OtherVar;
    Integer MyIntExpr = array.BaseInt + 100;
    String MyUnquotedString = UnquotedValue;
    Boolean MyBoolExpr = array.MySpecDouble > 2.5;
}
''', newfile=True)

        # Create MTPL file
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        result = File('Modules/ARR/array.py').read()

        # Check Spec expressions
        self.assertRegex(result, r"usrv\.MySpecDouble = \('SomeComplexExpression\(\)', float\)")
        self.assertRegex(result, r"usrv\.MyRefString = \('array\.OtherVar', str\)")
        self.assertRegex(result, r"usrv\.MyIntExpr = \('array\.BaseInt\+100', int\)")
        self.assertRegex(result, r"usrv\.MyUnquotedString = \('UnquotedValue', str\)")
        self.assertRegex(result, r"usrv\.MyBoolExpr = \('array\.MySpecDouble>2\.5', bool\)")

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_uservars_with_array_spec_expressions(self):
        # Test UserVars with array Spec expressions
        # Create .usrv file
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
    Array<Integer> MyIntArrayExpr = [1, 2, array.MyInt];
    Array<String> MyStringArrayExpr = [Expression(), "Hello", "World"];
}
''', newfile=True)

        # Create MTPL file
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        result = File('Modules/ARR/array.py').read()

        # Check array Spec expressions
        self.assertRegex(result, r"usrv\.MyIntArrayExpr = \('\[1,2,array\.MyInt\]', \[int\]\)")
        self.assertRegex(result, r"usrv\.MyStringArrayExpr = \('\[Expression\(\),\"Hello\",\"World\"\]', \[str\]\)")

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_multiple_uservars_sets(self):
        # Test multiple UserVars sets in same module (.usrv file can have multiple sets)
        # Create .usrv file with multiple UserVars blocks
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
    Integer Var1 = 10;
}

UserVars Set2
{
    Integer Var2 = 20;
}
''', newfile=True)

        # Create MTPL file
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        result = File('Modules/ARR/array.py').read()

        # Check both UserVars sets
        self.assertRegex(result, r"usrv = UserVars\('array'\)")
        self.assertRegex(result, r"usrv_Set2 = UserVars\('array', setname='Set2'\)")
        self.assertRegex(result, r'usrv\.Var1 = 10')
        self.assertRegex(result, r'usrv_Set2\.Var2 = 20')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_no_uservars(self):
        # Test that code works when no UserVars present
        # delete existing uservars (any .usrv) in this directory
        import glob
        import os
        for f in glob.glob('./Modules/ARR/*.usrv'):
            os.remove(f)
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        result = File('Modules/ARR/array.py').read()

        # Check that UserVars is NOT imported
        self.assertNotRegex(result, r'from pymtpl\.uservars import UserVars')
        # Check no UserVars header
        self.assertNotRegex(result, r'### UserVars')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_empty_uservars_block(self):
        # Test empty UserVars block is handled gracefully
        # Create .usrv file with empty block
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
}
''', newfile=True)

        # Create MTPL file
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        result = File('Modules/ARR/array.py').read()

        # Empty block should not generate UserVars code
        self.assertNotRegex(result, r'from pymtpl\.uservars import UserVars')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_uservars_complete_example(self):
        # Complete integration test with various types
        # Create .usrv file
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
    Integer MyInt = 20;
    Double MyDouble = -99.0;
    String MyString = "Hello";
    Boolean MyBool = True;
    Array<Integer> MyIntArray = [1,2,3];
    Double MySpecDouble = array.BaseVoltage * 1.1;
    String MyRefString = array.PatternName;
    Integer MyExpr = TP_KNOB.SomeValue + 100;
}
''', newfile=True)

        # Create MTPL file
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; SetBin SoftBins.b90757501_fail_test; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''
from pymtpl.por_methods import iCSimpleScoreboardTest
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, Import, TrialParamSpec, Spec
from pymtpl.uservars import UserVars

Initialize('Test_array', 'array')

##############################################################
# UserVars
# region
##############################################################
usrv = UserVars('array')
usrv.MyInt = 20
usrv.MyDouble = -99.0
usrv.MyString = "Hello"
usrv.MyBool = True
usrv.MyIntArray = [1,2,3]
usrv.MySpecDouble = ('array.BaseVoltage*1.1', float)
usrv.MyRefString = ('array.PatternName', str)
usrv.MyExpr = ('TP_KNOB.SomeValue+100', int)
##############################################################
# endregion UserVars
##############################################################

##############################################################
# MAIN1
# region
##############################################################
MAIN1 = Flow('MAIN1', [
    iCSimpleScoreboardTest(name = 'CCA',
        timings = 'BASE::test',
        level = 'BASE::test',
        Patlist = 'test',
        base_number = 2160,
        _fitem = Fitem(
            r0=pFail(setbin=90757501),
        )
    ),
])
##############################################################
# endregion MAIN1
##############################################################
'''
        self.assertTextEqual(File('Modules/ARR/array.py').read(), expect)

    def test_detect_if_needs_spec_integers(self):
        # Test _detect_if_needs_spec for integers
        obj = GenPy.__new__(GenPy)

        # Literal integers don't need Spec
        self.assertFalse(obj._detect_if_needs_spec('Integer', '20', False))
        self.assertFalse(obj._detect_if_needs_spec('Integer', '-99', False))

        # Expressions need Spec
        self.assertTrue(obj._detect_if_needs_spec('Integer', 'Module.Var', False))
        self.assertTrue(obj._detect_if_needs_spec('Integer', 'Module.Var + 100', False))

    def test_detect_if_needs_spec_doubles(self):
        # Test _detect_if_needs_spec for doubles
        obj = GenPy.__new__(GenPy)

        # Literal doubles don't need Spec
        self.assertFalse(obj._detect_if_needs_spec('Double', '20.5', False))
        self.assertFalse(obj._detect_if_needs_spec('Double', '-99.0', False))

        # Expressions need Spec
        self.assertTrue(obj._detect_if_needs_spec('Double', 'Module.Var', False))
        self.assertTrue(obj._detect_if_needs_spec('Double', 'Function()', False))

    def test_detect_if_needs_spec_strings(self):
        # Test _detect_if_needs_spec for strings
        obj = GenPy.__new__(GenPy)

        # Quoted strings don't need Spec
        self.assertFalse(obj._detect_if_needs_spec('String', '"Hello"', False))
        self.assertFalse(obj._detect_if_needs_spec('String', '"Module.Var"', False))

        # Unquoted strings need Spec
        self.assertTrue(obj._detect_if_needs_spec('String', 'Module.Var', False))
        self.assertTrue(obj._detect_if_needs_spec('String', 'UnquotedValue', False))

    def test_detect_if_needs_spec_booleans(self):
        # Test _detect_if_needs_spec for booleans
        obj = GenPy.__new__(GenPy)

        # Literal booleans don't need Spec
        self.assertFalse(obj._detect_if_needs_spec('Boolean', 'True', False))
        self.assertFalse(obj._detect_if_needs_spec('Boolean', 'False', False))

        # Expressions need Spec
        self.assertTrue(obj._detect_if_needs_spec('Boolean', 'Module.Var', False))

    def test_detect_if_needs_spec_arrays(self):
        # Test _detect_if_needs_spec for arrays
        obj = GenPy.__new__(GenPy)

        # Array literals don't need Spec
        self.assertFalse(obj._detect_if_needs_spec('Integer', '[1,2,3]', True))
        self.assertFalse(obj._detect_if_needs_spec('String', '["A","B"]', True))

        # Array expressions need Spec
        self.assertTrue(obj._detect_if_needs_spec('Integer', '[1, Module.Var]', True))
        self.assertTrue(obj._detect_if_needs_spec('String', 'GetArray()', True))

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_extract_uservars_from_usrv_files(self):
        # Test extract_uservars_from_usrv_files method directly
        # Create .usrv file
        File('./Modules/ARR/array.usrv').touch('''
Version 1.0;

UserVars array
{
    Integer MyInt = 20;
    String MyString = "Hello";
}
''', newfile=True)

        # Create MTPL file
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.get_dutflow_dict_and_modulename()

        # Check uservars_data structure
        self.assertEqual(len(obj1.uservars_data), 1)
        self.assertEqual(obj1.uservars_data[0]['setname'], 'array')
        self.assertEqual(len(obj1.uservars_data[0]['variables']), 2)

        # Check first variable
        var1 = obj1.uservars_data[0]['variables'][0]
        self.assertEqual(var1['type'], 'Integer')
        self.assertEqual(var1['name'], 'MyInt')
        self.assertEqual(var1['value'], '20')
        self.assertFalse(var1['is_array'])
        self.assertFalse(var1['needs_spec'])

        # Check second variable
        var2 = obj1.uservars_data[0]['variables'][1]
        self.assertEqual(var2['type'], 'String')
        self.assertEqual(var2['name'], 'MyString')
        self.assertEqual(var2['value'], '"Hello"')
        self.assertFalse(var2['is_array'])
        self.assertFalse(var2['needs_spec'])

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_parse_usrv_file_nonexistent(self):
        # Test that parsing non-existent .usrv file throws
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        with self.assertRaisesRegex(OSError, "No such file"):
            obj1._parse_usrv_file('nonexistent_file.usrv')

    def test_detect_if_needs_spec_arithmetic_expression(self):
        # Test _detect_if_needs_spec for arithmetic expressions without module refs (line 309, 311)
        obj = GenPy.__new__(GenPy)

        # Arithmetic expressions that aren't literals and don't have module refs should need Spec
        self.assertTrue(obj._detect_if_needs_spec('Integer', '10+20', False))
        self.assertTrue(obj._detect_if_needs_spec('Double', '3.14*2', False))
        self.assertTrue(obj._detect_if_needs_spec('Boolean', 'not', False))

    def test_detect_if_needs_spec_default_fallback(self):
        # Test _detect_if_needs_spec default return (line 314)
        # This should not normally be reached for well-formed input, but test edge case
        obj = GenPy.__new__(GenPy)

        # Unknown type with no special patterns
        result = obj._detect_if_needs_spec('UnknownType', 'somevalue', False)
        # Should return False as default
        self.assertFalse(result)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_uservars_setname_starting_with_digit(self):
        # Test UserVars setname sanitization when it starts with a digit (line 389)
        os.makedirs('./Modules/DIG', exist_ok=True)
        File('./Modules/DIG/digit.usrv').touch('''
Version 1.0;

UserVars 123test
{
    Integer TestVar = 10;
}
''', newfile=True)

        File('./Modules/DIG/digit.mtpl').touch('''
Version 1.0;

TestPlan digit;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)

        obj1 = GenPy('./Modules/DIG/digit.mtpl')
        obj1.get_dutflow_dict_and_modulename()

        # Generate the output
        output = '\n'.join(obj1.write_uservars_lines())

        # Should have sanitized the setname to avoid starting with a digit
        self.assertIn("usrv_usrv_123test = UserVars('digit', setname='123test')", output)
        self.assertIn("usrv_usrv_123test.TestVar = 10", output)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_uservars_setname_with_special_chars(self):
        # Test UserVars setname sanitization with special characters (line 386)
        # Note: The regex only captures \w+ for setnames, so we test a setname
        # that doesn't match the module name to trigger the else branch
        os.makedirs('./Modules/SPEC', exist_ok=True)
        File('./Modules/SPEC/special.usrv').touch('''
Version 1.0;

UserVars NotTheModuleName
{
    Integer TestVar = 42;
}
''', newfile=True)

        File('./Modules/SPEC/special.mtpl').touch('''
Version 1.0;

TestPlan special;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::test";
    level = "BASE::test";
    Patlist = "test";
    base_number = 2160;
}

DUTFlow MAIN1 {
    DUTFlowItem CCA CCA {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
''', newfile=True)

        obj1 = GenPy('./Modules/SPEC/special.mtpl')
        obj1.get_dutflow_dict_and_modulename()

        # Generate the output
        output = '\n'.join(obj1.write_uservars_lines())

        # Should create a variable with the setname that doesn't match module name
        self.assertIn("usrv_NotTheModuleName = UserVars('special', setname='NotTheModuleName')", output)
        self.assertIn("usrv_NotTheModuleName.TestVar = 42", output)


class TestGenPyTestChip(TestCase):
    # make sure all tests use TC
    def setUp(self):
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        OPT.product = 'TestChip'

    # reset OPT.product after tests
    def tearDown(self):
        OPT.product = self._orig_product

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_initialize_tc_with_bin_limits(self):
        # Test that InitializeTestChip doesn't import bin limits (importbinlimits=False)
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        EndVoltageLimits = array.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            SetBin "SoftBins.b" + FlowMatrix.bin + "4781_fail_array_MTTtname";
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
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

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90444427_fail_FUN_MTTtname;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # TC should use InitializeTestChip
        self.assertIn('InitializeTestChip', content)
        # TC should NOT import bin limits from json
        self.assertNotIn('get_bin_limits_from_json', content)
        self.assertNotIn('binrange=bin_limits', content)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_uses_first_two_digits_for_hardbin(self):
        # Test that TC uses first two digits for hardbin extraction (use_first_two_digits_for_hardbin=True)
        from pymtpl.mtpl2py import GenPy, TestChipDefault

        obj_tc = GenPy.__new__(GenPy)
        obj_tc.defaults = TestChipDefault

        # For bin b90440101, with flag=True should extract 90, result should be -90
        setbin = obj_tc.get_bin('SoftBins.b90440101_fail_test', ismtt=False)
        self.assertEqual(setbin, -90)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_get_bin_from_counter_with_first_two_digits(self):
        # Test that get_bin_from_counter extracts first two digits when flag is True
        from pymtpl.mtpl2py import GenPy, TestChipDefault

        obj_tc = GenPy.__new__(GenPy)
        obj_tc.defaults = TestChipDefault

        # For counter n90440101, with flag=True should extract 68, result should be -68
        setbin = obj_tc.get_bin_from_counter('Module::n68440101_fail_test', ismtt=False)
        self.assertEqual(setbin, -68)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_autosetbins_enabled(self):
        # Test that TC has autosetbins=True and extracts first two digits
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

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
            SetBin SoftBins.b90680000_fail_array_Instance1;
            IncrementCounters array::n90680001_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # With autosetbins=True and use_first_two_digits_for_hardbin=True, should extract 90
        self.assertIn('r0=pFail(setbin=-90)', content)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_autosetcounters_enabled(self):
        # Test that TC has autosetcounters=True (removes counters from output)
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

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
            SetBin SoftBins.b90680000_fail_array_Instance1;
            IncrementCounters array::n90680001_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # With autosetcounters=True, counters should not be included
        self.assertNotIn('ctr=', content)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_autogeneratestandardports_enabled(self):
        # Test that TC has autogeneratestandardports=True (skip standard ports in _fitem)
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

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
            SetBin SoftBins.b90992222_fail_FAIL_DUMMY_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90981111_fail_FAIL_DUMMY_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b90680000_fail_array_Instance1;
            IncrementCounters array::n90680001_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # With autogeneratestandardports=True, standard ports (rm2, rm1, r1) should be skipped
        self.assertNotIn('rm2=', content)
        self.assertNotIn('rm1=', content)
        # Only r0 (fail port) should be present
        self.assertIn('r0=pFail', content)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_tos_version(self):
        # Test that TC defaults to tos=4
        from pymtpl.mtpl2py import TestChipDefault
        self.assertEqual(TestChipDefault.tos, 4)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_omit_binrange_params_true(self):
        # Test that TC has omit_binrange_params=True and doesn't include binrange/edcportctrbinrange
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

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
            SetBin SoftBins.b90680000_fail_array_Instance1;
            IncrementCounters array::n90680001_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # TC should not include binrange or edcportctrbinrange
        self.assertNotIn('binrange', content)
        self.assertNotIn('edcportctrbinrange', content)
        # TC should not import get_bin_limits_from_json
        self.assertNotIn('get_bin_limits_from_json', content)
        # Should have InitializeTestChip with only test name and module name
        self.assertIn("InitializeTestChip('Test_array', 'array')", content)

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_tc_default_value_omit_binrange_params(self):
        # Test that TestChipDefault.omit_binrange_params is True
        from pymtpl.mtpl2py import TestChipDefault
        self.assertEqual(TestChipDefault.omit_binrange_params, True)


class TestGenPyOmitBinrangeParams(TestCase):
    # Test the omit_binrange_params functionality with different products

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dmr_omit_binrange_params_false(self):
        # Test that DMR has omit_binrange_params=False (default) and includes binrange
        from gadget.helperclass import OPT
        orig_product = getattr(OPT, "product", None)
        try:
            OPT.product = 'DMRClass'
            File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

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
            SetBin SoftBins.b90680000_fail_array_Instance1;
            IncrementCounters array::n90680001_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
            obj1 = GenPy('./Modules/ARR/array.mtpl')
            obj1.main()
            content = File('Modules/ARR/array.py').read()
            # DMR should include binrange and edcportctrbinrange
            self.assertIn('binrange=bin_limits', content)
            self.assertIn('edcportctrbinrange=bin_limits', content)
            # DMR should import get_bin_limits_from_json
            self.assertIn('get_bin_limits_from_json', content)
        finally:
            OPT.product = orig_product

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dmrhd_omit_binrange_params_false(self):
        # Test that JGS has omit_binrange_params=False and includes binrange
        from gadget.helperclass import OPT
        orig_product = getattr(OPT, "product", None)
        try:
            OPT.product = 'JGSClass'
            File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

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
            SetBin SoftBins.b90680000_fail_array_Instance1;
            IncrementCounters array::n90680001_fail_Instance1_0;
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
            obj1 = GenPy('./Modules/ARR/array.mtpl')
            obj1.main()
            content = File('Modules/ARR/array.py').read()
            # JGS should include binrange and edcportctrbinrange
            self.assertIn('binrange=bin_limits', content)
            self.assertIn('edcportctrbinrange=bin_limits', content)
            # JGS should import get_bin_limits_from_json
            self.assertIn('get_bin_limits_from_json', content)
        finally:
            OPT.product = orig_product

    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_base_default_omit_binrange_params_false(self):
        # Test that BaseDefault has omit_binrange_params=False
        from pymtpl.mtpl2py import BaseDefault
        self.assertEqual(BaseDefault.omit_binrange_params, False)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_identify_init_flows(self):
        # Test internal method to identify INIT flows
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest TEST1 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
Test iCSimpleScoreboardTest TEST2 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2161;
}
DUTFlow INIT_FLOW @INIT {
        DUTFlowItem TEST1 TEST1 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
        }
}
DUTFlow MAIN_FLOW @MAIN {
        DUTFlowItem TEST2 TEST2 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
        }
}
''', newfile=True)

        obj = GenPy('./Modules/ARR/array.mtpl')
        obj.main()

        # Test _identify_init_flows after processing
        init_flows = obj._identify_init_flows()
        self.assertEqual(init_flows, {'array::INIT_FLOW'})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_collect_init_flow_tests_nested(self):
        # Test collecting tests from nested INIT flows (2 levels deep)
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest TEST1 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
Test iCSimpleScoreboardTest TEST2 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2161;
}
Test iCSimpleScoreboardTest TEST3 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2162;
}
Test iCSimpleScoreboardTest TEST4 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2163;
}

DUTFlow SUBFLOW {
        DUTFlowItem TEST2 TEST2 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
        }
}

DUTFlow SUBFLOW2 {
        DUTFlowItem TEST3 TEST3 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
        }
}

DUTFlow INIT_FLOW @INIT {
        DUTFlowItem TEST1 TEST1 {
                Result 0 {
                        Property PassFail = "Fail";
                        GoTo NEXT;
                }
        }
        DUTFlowItem SUBFLOW_CALL SUBFLOW {
                Result 0 {
                        Property PassFail = "Fail";
                        GoTo NEXT;
                }
        }
        DUTFlowItem SUBFLOW2_CALL SUBFLOW2 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
        }
}
DUTFlow MAIN_FLOW @MAIN {
        DUTFlowItem TEST4 TEST4 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
        }
}
''', newfile=True)

        obj = GenPy('./Modules/ARR/array.mtpl')
        obj.main()
        init_tests = obj._collect_init_flow_tests()
        # Should include TEST1 (direct), TEST2 (in SUBFLOW), TEST3 (in SUBFLOW2)
        self.assertIn('TEST1', init_tests)
        self.assertIn('TEST2', init_tests)
        self.assertIn('TEST3', init_tests)
        self.assertIn('SUBFLOW_CALL', init_tests)
        self.assertIn('SUBFLOW2_CALL', init_tests)
        # Should not include TEST4 from MAIN
        self.assertNotIn('TEST4', init_tests)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_init_flow_single_level(self):
        # Test single-level INIT flow with no bins/counters
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest TEST1 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
Test iCSimpleScoreboardTest TEST2 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2161;
}
DUTFlow INIT_FLOW @INIT {
        DUTFlowItem TEST1 TEST1 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757501_fail_NSIO;
                        IncrementCounters "ARR::n75750001_fail_TEST1_0";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result -1 {
                        Property PassFail = "Fail";
                        Return -1;
                }
                Result -2 {
                        Property PassFail = "Fail";
                        Return -2;
                }
        }
}
DUTFlow MAIN @MAIN {
        DUTFlowItem TEST2 TEST2 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757501_fail_NSIO;
                        IncrementCounters "ARR::n75750001_fail_TEST1_0";
                        Return 0;
                }
        }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()

        # Verify INIT flow tests have setbin=None and ctr=0
        self.assertIn('r0=pFail(ret=0, setbin=None, ctr=0)', content)
        self.assertIn('rm1=pFail(ret=-1, setbin=None, ctr=0)', content)
        self.assertIn('rm2=pFail(ret=-2, setbin=None, ctr=0)', content)

        # Verify non-INIT flow test has normal bins
        self.assertIn('setbin=90757501', content)
        # Verify INIT flow is marked with dtag
        self.assertIn("dtag='INIT'", content)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_init_flow_nested_two_levels(self):
        # Test nested INIT flow (2 levels deep) with no bins/counters
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest TEST1 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
Test iCSimpleScoreboardTest TEST2 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2161;
}
Test iCSimpleScoreboardTest TEST3 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2162;
}
Test iCSimpleScoreboardTest TEST4 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2162;
}

DUTFlow SUBFLOW1 {
        DUTFlowItem TEST2 TEST2 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757502_fail_NSIO;
                        IncrementCounters "ARR::n75750002_fail_TEST2_0";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo NEXT;
                }
        }
}

DUTFlow SUBFLOW2 {
        DUTFlowItem SF1 SUBFLOW1 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo NEXT;
                }
        }
        DUTFlowItem TEST3 TEST3 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757503_fail_NSIO;
                        IncrementCounters "ARR::n75750003_fail_TEST3_0";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}

DUTFlow INIT_FLOW @INIT {
        DUTFlowItem TEST1 TEST1 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757501_fail_NSIO;
                        IncrementCounters "ARR::n75750001_fail_TEST1_0";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo NEXT;
                }
        }
        DUTFlowItem SF2 SUBFLOW2 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}

DUTFlow MAIN @MAIN {
        DUTFlowItem TEST4 TEST4 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757599_fail_NSIO;
                        IncrementCounters "ARR::n75759901_fail_TEST4_0";
                        Return 0;
                }
        }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()

        # Verify all INIT flow tests (including nested) have setbin=None and ctr=0
        # TEST1 is direct child of INIT flow
        self.assertIn('TEST1', content)
        # TEST2 is in SUBFLOW1 which is called from SUBFLOW2 which is in INIT flow
        self.assertIn('TEST2', content)
        # TEST3 is in SUBFLOW2 which is in INIT flow
        self.assertIn('TEST3', content)

        # Count occurrences of setbin=None and ctr=0 to verify INIT flow tests
        # We expect multiple occurrences since there are nested flows
        init_flow_markers = content.count('setbin=None')
        self.assertGreater(init_flow_markers, 5, "Should have multiple setbin=None for INIT flow tests")

        # Verify non-INIT flow test (TESTX in MAIN) has normal bins
        self.assertIn('setbin=90757599', content)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_init_flow_dmr_product(self):
        # Test INIT flow with DMR product (with autosetbins=True)
        orig_product = OPT.product
        try:
            OPT.product = 'dmrclass'
            File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest TEST1 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
Test iCSimpleScoreboardTest TEST2 {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2161;
}
DUTFlow INIT_FLOW @INIT {
        DUTFlowItem TEST1 TEST1 @EDC {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757501_fail_NSIO;
                        IncrementCounters "ARR::n75750001_fail_TEST1_0";
                        GoTo NEXT;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo NEXT;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757502_fail_NSIO;
                        IncrementCounters "ARR::n75750002_fail_TEST1_2";
                        GoTo NEXT;
                }
                Result -1 {
                        Property PassFail = "Fail";
                        Return -1;
                }
                Result -2 {
                        Property PassFail = "Fail";
                        Return -2;
                }
        }
}
DUTFlow MAIN @MAIN {
        DUTFlowItem TEST2 TEST2 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757510_fail_NSIO;
                        IncrementCounters "ARR::n75751001_fail_TEST2_0";
                        Return 0;
                }
        }
}
''', newfile=True)
            obj1 = GenPy('./Modules/ARR/array.mtpl')
            obj1.main()
            content = File('Modules/ARR/array.py').read()

            # Verify INIT flow test has setbin=None and ctr=0 even with DMR product
            self.assertIn('setbin=None', content)
            self.assertIn('ctr=0', content)

            # Verify EDC marking is preserved
            self.assertIn('edc=True', content)

            # Verify non-INIT flow test (TEST2) has auto-binning (-75 from 90757510)
            self.assertIn('setbin=-75', content)

        finally:
            OPT.product = orig_product

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_init_flow_mtt_test(self):
        # Test INIT flow with MTT test
        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction "Continue";
    CSharpTrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
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
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            SetBin "SoftBins.b" + FlowMatrix.bin + "0001_fail_Instance1_0";
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Next";
        }
    }
}
DUTFlow INITFLOW @INIT
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            PassFail Fail;
            Return -2;
        }
        Result -1
        {
            PassFail Fail;
            Return -1;
        }
        Result 0
        {
            PassFail Fail;
            Return 0;
        }
        Result 1
        {
            PassFail Pass;
            Return 1;
        }
    }
}

DUTFlow MAIN @MAIN
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            PassFail Fail;
            Return -2;
        }
        Result -1
        {
            PassFail Fail;
            Return -1;
        }
        Result 0
        {
            PassFail Fail;
            Return 0;
        }
        Result 1
        {
            PassFail Pass;
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()

        # Verify MTT test in INIT flow has setbin=None and ctr=0 in trial results
        # Check that within INITFLOW section, the MTT has setbin=None
        initflow_section = content[content.find('INITFLOW'):content.find('# endregion INITFLOW')]
        self.assertIn('setbin=None', initflow_section)
        self.assertIn('ctr=0', initflow_section)

        # Verify non-INIT MTT test in MAIN has normal bins
        main_section = content[content.find('# MAIN'):content.find('# endregion MAIN')]
        # The MAIN flow MTT should have setbin extracted from the trial result
        self.assertIn('r0=pFail', main_section)


class TestGenPyNVLClass(TestCase):
    # make sure all tests use NVLClass
    def setUp(self):
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        OPT.product = 'nvlclass'

    # reset OPT.product after tests
    def tearDown(self):
        OPT.product = self._orig_product

    @with_(TempDir, chdir=True)
    def test_integration(self):
        cmd = f'pymtpl.py -genpy {UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_NVLCLASS_SCN_UNCORE_C68C.mtpl -product nvlclass'.split()
        with MockVar(sys, "argv", cmd):
            self.assertEqual(PyMtplArgs().main(), 3)
        self.assertGoldEqual(f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_NVLCLASS_SCN_UNCORE_C68C.py', f'{UT_DIR_REPO}/sudheer_unit_test/mtpl2py/Modules/SCN_UNCORE_C68C/TOS4_NVLCLASS_SCN_UNCORE_C68C.nvl.gold.py')


class TestSetDefaults(TestCase):
    def setUp(self):
        # Save original OPT state before each test
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        self._orig_set_defaults = getattr(OPT, "set_defaults", {})
        OPT.set_defaults = {}

    def tearDown(self):
        # Restore original OPT state after each test
        from gadget.helperclass import OPT
        OPT.product = self._orig_product
        OPT.set_defaults = self._orig_set_defaults

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dmrclass_autosetbins_false_sets_attribute(self):
        # DMRClass with set_defaults autosetbins=False should have autosetbins=False on the instance defaults
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'autosetbins': 'False'}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertFalse(obj.defaults.autosetbins)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dmrclass_autosetcounters_false_sets_attribute(self):
        # DMRClass with set_defaults autosetcounters=False should have autosetcounters=False on the instance defaults
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'autosetcounters': 'False'}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertFalse(obj.defaults.autosetcounters)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dmrclass_autosetbins_and_autosetcounters_false(self):
        # DMRClass with both autosetbins=False and autosetcounters=False should override both
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'autosetbins': 'False', 'autosetcounters': 'False'}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertFalse(obj.defaults.autosetbins)
        self.assertFalse(obj.defaults.autosetcounters)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_dmrclass_without_set_defaults_keeps_autosetbins_true(self):
        # DMRClass without set_defaults should remain autosetbins=True
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertTrue(obj.defaults.autosetbins)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_bool_coercion_true_string(self):
        # set_defaults with bool string 'True' is coerced to Python True
        from gadget.helperclass import OPT
        OPT.product = 'nvlclass'  # nvlclass has autosetbins=False by default
        OPT.set_defaults = {'autosetbins': 'True'}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertTrue(obj.defaults.autosetbins)
        self.assertIs(obj.defaults.autosetbins, True)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_int_coercion_tos(self):
        # set_defaults with int attribute tos=3 is coerced to Python int
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'tos': '3'}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertEqual(obj.defaults.tos, 3)
        self.assertIsInstance(obj.defaults.tos, int)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_string_attribute_passed_through_unchanged(self):
        # When existing attribute is a string (not bool, not int), the value is kept as-is without coercion
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'initialize': 'InitializeCustom'}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertEqual(obj.defaults.initialize, 'InitializeCustom')
        self.assertIsInstance(obj.defaults.initialize, str)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_original_default_class_not_mutated(self):
        # Applying set_defaults must not mutate the original DMRClassDefault class
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'autosetbins': 'False'}
        obj = GenPy('./Modules/ARR/array.mtpl')
        self.assertFalse(obj.defaults.autosetbins)
        self.assertTrue(DMRClassDefault.autosetbins)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_output_uses_full_bins_with_autosetbins_false(self):
        # With DMRClass + autosetbins=False, bins should appear as full 8-digit numbers not negated hardbin
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'autosetbins': 'False'}
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest CCA {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
DUTFlow MAIN1 @END {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757501_fail_NSIO;
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}
''', newfile=True)
        obj = GenPy('./Modules/ARR/array.mtpl')
        obj.main()
        content = File('Modules/ARR/array.py').read()
        # autosetbins=False keeps the full 8-digit soft bin number
        self.assertIn('setbin=90757501', content)
        # should NOT contain the DMR-style negated hardbin (-90)
        self.assertNotIn('setbin=-90', content)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_output_includes_counter_with_autosetcounters_false(self):
        # With DMRClass + autosetcounters=False, counter values should appear in output
        from gadget.helperclass import OPT
        OPT.product = 'DMRClass'
        OPT.set_defaults = {'autosetcounters': 'False'}
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest CCA {
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
        level = "BASE::DDR_univ_lvl_max_lvl";
        Patlist = "shops_L_list";
        bypass_global = "0";
        base_number = 2160;
}
DUTFlow MAIN1 @END {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90757501_fail_NSIO;
                        IncrementCounters FUN::n44270003_fail_CCA_0;
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}
''', newfile=True)
        obj = GenPy('./Modules/ARR/array.mtpl')
        obj.main()
        content = File('Modules/ARR/array.py').read()
        # autosetcounters=False keeps the counter value in the output
        self.assertIn('ctr=44270003', content)


class TestGenPyAutoGenerateStandardPorts(TestCase):
    # Tests for autogeneratestandardports overriding autosetbins/autosetcounters behavior
    # for standard ports (m1, m2, r1).

    def setUp(self):
        # Use NVLClass (autosetbins=False, autosetcounters=False) and override autogeneratestandardports=True
        from gadget.helperclass import OPT
        self._orig_product = getattr(OPT, "product", None)
        self._orig_set_defaults = getattr(OPT, "set_defaults", {})
        OPT.product = 'nvlclass'
        OPT.set_defaults = {'autogeneratestandardports': 'True'}

    def tearDown(self):
        from gadget.helperclass import OPT
        OPT.product = self._orig_product
        OPT.set_defaults = self._orig_set_defaults

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_skips_m1_with_counter_when_autogeneratestandardports_true(self):
        # With autogeneratestandardports=True and autosetcounters=False, a standard m1 port
        # (ret=-1, no goto) must be skipped even though a counter is present on the port.
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::t100";
    level = "BASE::lvl";
    Patlist = "plist";
}
DUTFlow MAIN @END {
    DUTFlowItem CCA CCA {
        Result -1 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_FAIL;
            IncrementCounters FUN::n44270003_fail_CCA_n1;
            Return -1;
        }
        Result 0 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90440101_fail_CCA;
            IncrementCounters FUN::n44010001_fail_CCA_0;
            Return 0;
        }
        Result 1 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # Standard m1 port (ret=-1, no goto) must be omitted
        self.assertNotIn('rm1=', content)
        # Non-standard r0 fail port must still appear
        self.assertIn('r0=pFail', content)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_skips_m2_with_counter_when_autogeneratestandardports_true(self):
        # With autogeneratestandardports=True and autosetcounters=False, a standard m2 port
        # (ret=-2, no goto) must be skipped even though a counter is present on the port.
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::t100";
    level = "BASE::lvl";
    Patlist = "plist";
}
DUTFlow MAIN @END {
    DUTFlowItem CCA CCA {
        Result -2 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_DPS;
            IncrementCounters FUN::n44270003_fail_CCA_n2;
            Return -2;
        }
        Result 0 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90440101_fail_CCA;
            IncrementCounters FUN::n44010001_fail_CCA_0;
            Return 0;
        }
        Result 1 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # Standard m2 port (ret=-2, no goto) must be omitted
        self.assertNotIn('rm2=', content)
        # Non-standard r0 fail port must still appear
        self.assertIn('r0=pFail', content)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_skips_r1_pass_port_going_to_next_when_autogeneratestandardports_true(self):
        # With autogeneratestandardports=True, a standard r1 pass port going to NEXT
        # must be skipped even when autosetcounters=False (which would have preserved the counter).
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest CCA {
    timings = "BASE::t100";
    level = "BASE::lvl";
    Patlist = "plist";
}
Test iCSimpleScoreboardTest CCA2 {
    timings = "BASE::t100";
    level = "BASE::lvl";
    Patlist = "plist2";
}
DUTFlow MAIN @END {
    DUTFlowItem CCA CCA {
        Result 0 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90440101_fail_CCA;
            IncrementCounters FUN::n44010001_fail_CCA_0;
            Return 0;
        }
        Result 1 {
            Property PassFail = "Pass";
            GoTo CCA2;
        }
    }
    DUTFlowItem CCA2 CCA2 {
        Result 0 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90440201_fail_CCA2;
            Return 0;
        }
        Result 1 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # r1 pass port going to next item must be omitted
        self.assertNotIn('r1=pPass', content)
        # r0 fail ports must still appear
        self.assertIn('r0=pFail', content)

    @patch('pymtpl.mtpl2py.GenPy.write_initialize_line', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_import_lines', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_header', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.write_section_footer', Mock(return_value=''))
    @patch('pymtpl.mtpl2py.GenPy.extract_uservars_from_usrv_files', Mock(return_value=''))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_init_flow_tests_still_write_all_ports_despite_autogeneratestandardports(self):
        # INIT flow tests must always write all ports explicitly (with setbin=None, ctr=0)
        # even when autogeneratestandardports=True would otherwise skip standard ports.
        File('./Modules/ARR/array.mtpl').touch('''
TestPlan array;

Test iCSimpleScoreboardTest INIT_TEST {
    timings = "BASE::t100";
    level = "BASE::lvl";
    Patlist = "init_plist";
}
Test iCSimpleScoreboardTest MAIN_TEST {
    timings = "BASE::t100";
    level = "BASE::lvl";
    Patlist = "main_plist";
}
DUTFlow INIT_FLOW @INIT {
    DUTFlowItem INIT_TEST INIT_TEST {
        Result -2 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90999901_fail_DPS;
            IncrementCounters FUN::n44270003_fail_INIT_TEST_n2;
            Return -2;
        }
        Result -1 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_SYS;
            IncrementCounters FUN::n44270003_fail_INIT_TEST_n1;
            Return -1;
        }
        Result 0 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90440101_fail_INIT_TEST;
            IncrementCounters FUN::n44010001_fail_INIT_TEST_0;
            Return 0;
        }
        Result 1 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
DUTFlow MAIN @END {
    DUTFlowItem MAIN_TEST MAIN_TEST {
        Result -1 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90989801_fail_SYS;
            IncrementCounters FUN::n99989801_fail_MAIN_TEST_n1;
            Return -1;
        }
        Result 0 {
            Property PassFail = "Fail";
            SetBin SoftBins.b90440201_fail_MAIN_TEST;
            IncrementCounters FUN::n44020001_fail_MAIN_TEST_0;
            Return 0;
        }
        Result 1 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''', newfile=True)
        obj1 = GenPy('./Modules/ARR/array.mtpl')
        obj1.main()
        content = File('Modules/ARR/array.py').read()
        # INIT flow test: all standard ports must be written explicitly, with setbin=None and ctr=0
        init_section = content[content.find('INIT_FLOW'):content.find('MAIN')]
        self.assertIn('setbin=None', init_section)
        self.assertIn('ctr=0', init_section)
        self.assertIn('rm1=pFail', init_section)
        self.assertIn('rm2=pFail', init_section)
        # MAIN flow test: standard m1 port should be skipped (autogeneratestandardports applies)
        main_section = content[content.find('MAIN ='):]
        self.assertNotIn('rm1=', main_section)


class TestGenPySetDefaults(TestCase):
    # Tests for OPT.set_defaults type coercion and validation in GenPy.__init__

    def setUp(self):
        # Save OPT state and reset set_defaults, product, env for isolation
        from gadget.helperclass import OPT
        self._orig_set_defaults = OPT.set_defaults
        self._orig_product = OPT.product
        self._orig_env = OPT.env
        OPT.set_defaults = None
        OPT.product = None
        OPT.env = None

    def tearDown(self):
        # Restore original OPT state
        from gadget.helperclass import OPT
        OPT.set_defaults = self._orig_set_defaults
        OPT.product = self._orig_product
        OPT.env = self._orig_env

    def _make_genpy(self, mtplfile='/fake/a/b/c/test.mtpl'):
        # Create GenPy with env and TestProgram infrastructure mocked out
        with patch('pymtpl.mtpl2py.Env.get_envfile', return_value='/fake/env.env'), \
                patch('pymtpl.mtpl2py.TestProgram'):
            return GenPy(mtplfile)

    def test_no_set_defaults_uses_base_default(self):
        # When OPT.set_defaults is None, defaults stays as BaseDefault unchanged
        obj = self._make_genpy()
        self.assertIs(obj.defaults, BaseDefault)

    def test_bool_override_true(self):
        # Bool attribute 'autosetbins' overridden with "true" -> becomes bool True
        OPT.set_defaults = {'autosetbins': 'true'}
        obj = self._make_genpy()
        self.assertIs(obj.defaults.autosetbins, True)

    def test_bool_override_false(self):
        # Bool attribute 'autosetbins' overridden with "false" -> becomes bool False
        OPT.set_defaults = {'autosetbins': 'false'}
        obj = self._make_genpy()
        self.assertIs(obj.defaults.autosetbins, False)

    def test_bool_override_case_insensitive(self):
        # Bool coercion is case-insensitive: "TRUE" -> True
        OPT.set_defaults = {'autosetbins': 'TRUE'}
        obj = self._make_genpy()
        self.assertIs(obj.defaults.autosetbins, True)

    def test_int_override_valid(self):
        # Int attribute 'tos' overridden with "3" -> becomes int 3
        OPT.set_defaults = {'tos': '3'}
        obj = self._make_genpy()
        self.assertEqual(obj.defaults.tos, 3)
        self.assertIsInstance(obj.defaults.tos, int)

    def test_string_override(self):
        # String attribute 'initialize' overridden with a new string value
        OPT.set_defaults = {'initialize': 'InitializeCustom'}
        obj = self._make_genpy()
        self.assertEqual(obj.defaults.initialize, 'InitializeCustom')

    def test_unrelated_attrs_unchanged(self):
        # Overriding one key leaves all other attributes at their original values
        OPT.set_defaults = {'tos': '3'}
        obj = self._make_genpy()
        self.assertEqual(obj.defaults.tos, 3)
        self.assertEqual(obj.defaults.initialize, BaseDefault.initialize)
        self.assertIs(obj.defaults.autosetbins, BaseDefault.autosetbins)

    def test_original_defaults_class_not_mutated(self):
        # Overrides create a new derived class; BaseDefault itself is not mutated
        OPT.set_defaults = {'tos': '3'}
        obj = self._make_genpy()
        self.assertEqual(BaseDefault.tos, 4)
        self.assertEqual(obj.defaults.tos, 3)

    def test_multiple_overrides(self):
        # Multiple keys can be overridden in a single set_defaults dict
        OPT.set_defaults = {'tos': '3', 'autosetbins': 'true', 'initialize': 'MyInit'}
        obj = self._make_genpy()
        self.assertEqual(obj.defaults.tos, 3)
        self.assertIs(obj.defaults.autosetbins, True)
        self.assertEqual(obj.defaults.initialize, 'MyInit')

    def test_invalid_key_raises_error_user(self):
        # An unrecognized key raises ErrorUser with the invalid key name in the message
        OPT.set_defaults = {'nonexistentkey': 'true'}
        with self.assertRaisesRegex(ErrorUser, 'nonexistentkey'):
            self._make_genpy()

    def test_invalid_key_suggests_valid_keys(self):
        # ErrorUser for an unrecognized key includes 'Valid keys' in the suggestion
        OPT.set_defaults = {'badkey': 'val'}
        with self.assertRaisesRegex(ErrorUser, 'Valid keys'):
            self._make_genpy()

    def test_bool_non_string_raises_error_user(self):
        # Bool attribute passed a non-string value raises ErrorUser (injection guard)
        OPT.set_defaults = {'autosetbins': True}
        with self.assertRaisesRegex(ErrorUser, 'autosetbins'):
            self._make_genpy()

    def test_int_invalid_string_raises_error_user(self):
        # Int attribute with a non-numeric string raises ErrorUser (ValueError path)
        OPT.set_defaults = {'tos': 'notanumber'}
        with self.assertRaisesRegex(ErrorUser, 'tos'):
            self._make_genpy()

    def test_int_none_raises_error_user(self):
        # Int attribute with None raises ErrorUser (TypeError path)
        OPT.set_defaults = {'tos': None}
        with self.assertRaisesRegex(ErrorUser, 'tos'):
            self._make_genpy()

    def test_uses_product_class_for_type_inference(self):
        # Type inference uses self.defaults (the selected product class), not BaseDefault
        # With DMRClass selected, 'autosetbins' is bool; override "false" coerces to False
        OPT.product = 'dmrclass'
        OPT.set_defaults = {'autosetbins': 'false'}
        obj = self._make_genpy()
        self.assertIs(obj.defaults.autosetbins, False)
        self.assertIsInstance(obj.defaults.autosetbins, bool)

    def test_product_class_with_set_defaults_override(self):
        # set_defaults overrides are applied on top of the product class defaults
        OPT.product = 'dmrclass'
        OPT.set_defaults = {'tos': '3'}
        obj = self._make_genpy()
        # tos is overridden to 3
        self.assertEqual(obj.defaults.tos, 3)
        # other DMRClass attrs like autosetbins remain as DMRClassDefault defines them
        self.assertIs(obj.defaults.autosetbins, DMRClassDefault.autosetbins)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
