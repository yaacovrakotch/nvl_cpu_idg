#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for torch_build_errors_chk.py

"""
import sys

try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests

from qgates.torch_build_errors_chk import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from pprint import pformat
import os
import shutil


class TestEnvPatCase(TestCase):

    def test_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple5a/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = TorchBuildErrors(tpobj)
        obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(obj.passed, {(250, 'SCN'): 1, (250, 'ARR'): 1, (250, 'PTH'): 1,
                                      (250, 'TPI_DIESLCT_XXX'): 1, (250, 'TPI_FLWFLGS_XXX'): 1})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5a', chdir=True, delete=True)
    def test_failing_case(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        os.remove('POR_TP/TGLH81/Reports/build_errors.txt')

        # missing build file check
        obj = TorchBuildErrors(tpobj)
        obj.main()
        self.assertTextEqual(pformat(obj.result, width=100), '[]')

        # Mock-up failing cases Env file with ;" at end of a line.
        # Or split with "; + between values.
        File(f'POR_TP/TGLH81/Reports/build_errors_fail1.txt').copy('POR_TP/TGLH81/Reports/build_errors.txt')
        obj = TorchBuildErrors(tpobj)
        obj.main()
        pprint(obj.result)
        expect = [{'id': 250,
                   'message': 'Please fix: Torch build error on "SSIO_VIXVOX_XXX_Levels.tcg" at '
                              'line number: "12,25,12,37" with error: "Unrecognized '
                              "'uv_lc_vcc_gb'. Use a valid / accessible variable "
                              '[D:\\Github_action_arls68_01\\_work\\class_arls68\\class_arls68\\Modules\\SSIO_VIXVOX_XXX\\SSIO_VIXVOX_XXX.mtproj]"',
                   'module': 'SSIO_VIXVOX_XXX'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 5)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5a', chdir=True, delete=True)
    def test_TP0346_ut(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        File(f'POR_TP/TGLH81/Reports/build_errors_fail1.txt').copy('POR_TP/TGLH81/Reports/build_errors.txt')
        obj = TorchBuildErrors(tpobj)
        obj.main()

        # Not exist
        res = obj.check_TP0346(r"/path/Modules/MIO_D2D_SCM\MIO_D2D_SCM_CLASS_P68G2.mtpl", '10,2', set(), 'blah')
        self.assertEqual(res, f'[{os.getcwd()}/Modules/Modules/MIO_D2D_SCM\\MIO_D2D_SCM_CLASS_P68G2.mtpl] is not found. Build error: blah')

        # Exist, but it is not dutflow
        res = obj.check_TP0346('/path/Modules/Modules/ARR/array.mtpl', '10,2', set(), 'blah')
        self.assertEqual(res, f'line#10 of {os.getcwd()}/Modules/ARR/array.mtpl is not DUTFlowItem: blah')

        # Run again, it should cache; Not exist line
        res = obj.check_TP0346('/path/Modules/Modules/ARR/array.mtpl', '10000,2', set(), 'blah')
        self.assertEqual(res, f'line#10000 of {os.getcwd()}/Modules/ARR/array.mtpl is not FOUND: blah')

    def test_TP0346_fail(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7f'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            arr_mtpl = r'''{
                Version 1.0;
                ProgramStyle = Modular;
                TestPlan ARR;
                Import array.usrv;

                Test iCSimpleScoreboardTest CCA {
                        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                        level = "BASE::DDR_univ_lvl_max_lvl";
                        patlist = "shops_L_list";
                        PatternNameCounterIndexes = "9,10,11,12,13,14,15|8,9,10,11,12,13,14|9,10,11,12,13,14,16";
                        bypass_global = "0";
                        BaseNumbers = "12476,11051,12309";
                        FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters,per_pattern_printing";
                }
                Test iCFuncTest CCB {
                        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                        level = "BASE::DDR_univ_lvl_nom_lvl";
                        patlist = "shops_H_list";
                        PatternNameCounterIndexes = "9,10,11,12,13,14,15|9,10,11,12,13,14,15|9,10,11,12,13,14,15";
                        BaseNumbers = "12476,11051,12309";
                }
                Test iCFuncTest CCD {
                        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                        level = "BASE::DDR_univ_lvl_nom_lvl";
                        patlist = "shops_H_list";
                        PatternNameCounterIndexes = "9,10,11,12,13,14,15|9,10,11,12,13,14,15|9,10,11,12,13,14,15";
                        BaseNumbers = "12476,11051,12309";
                        FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters";
                }
                Test  iCFuncTest CCC1
                {
                        user_mode = "DEFAULT_MODE";
                }
                Test  iCFuncTest ini1
                {
                        user_mode = "DEFAULT_MODE";
                }
                Test VminTC CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501
                {
                    BypassPort = -1;
                    TestMode = "SingleVmin";
                    LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                    Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                    TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
                    PatternNameCounterIndexes = "9,10,11,12,13,14,15|8,9,10,11,12,13,14|9,10,11,12,13,14,16";
                    BaseNumbers = "12476,11051,12309";
                    FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters,per_pattern_printing";
                    FlowIndex = "1";
                    VoltageTargets = "VCF";
                    CornerIdentifiers = "CLR0@F1";
                    FlowIndexCallbackName = "CheckFlow(RING)";
                }

                Test VminTC CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502
                {
                    BypassPort = -1;
                    TestMode = "SingleVmin";
                    LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                    Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                    TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
                    PatternNameCounterIndexes = "9,10,11,12,13,14,15|9,10,11,12,13,14,15|9,10,11,12,13,14,15";
                    #BaseNumbers = "12476,11051,12309";
                    BaseNumbers = "12476,11051";
                    #FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters";
                }
                Test PrimeFlowControlSetTestMethod SetFlowInfo_ATOMC_Flow1
                {
                    DomainName = "ATOMC";
                    DomainValue = 1;
                }
                DUTFlow MAIN1  {
                    DUTFlowItem CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501 CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501
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
                            IncrementCounters SCN_ATOM_CXX::n15010694_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_0;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 1
                        {
                            Property PassFail = "Pass";
                            #GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                            GoTo CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502;
                        }
                        Result 2
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010695_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_2;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 3
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_3;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 4
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010699_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_4;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 5
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_5;
                            IncrementCounters SCN_ATOM_CXX::n90413665_fail_CA2TF_ATOM_VMIN_K_CATF2_X_VATOM_F6_AT_F6_FREQ_ATOM_FUSA_RECOVERY_5;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                    }
                    DUTFlowItem CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502 CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502
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
                            IncrementCounters SCN_ATOM_CXX::n15020694_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_0;
                            Return 0;
                        }
                        Result 1
                        {
                            Property PassFail = "Pass";
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 2
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020695_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_2;
                            Return 0;
                        }
                        Result 3
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_3;
                            Return 0;
                        }
                        Result 4
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020699_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_4;
                            Return 0;
                        }
                        Result 5
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_5;
                            IncrementCounters SCN_ATOM_CXX::n90413665_fail_CA2TF_ATOM_VMIN_K_CATF2_X_VATOM_F6_AT_F6_FREQ_ATOM_FUSA_RECOVERY_5;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                    }
                        DUTFlowItem SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1 SetFlowInfo_ATOMC_Flow1
                    {
                        Result -2
                        {
                            Property PassFail = "Fail";
                            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                            Return -1;
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
                            Return 0;
                        }
                    }
                }
                DUTFlow INIT1  {
                        DUTFlowItem ini1 ini1 {
                                Result 0 {
                 SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;
                                        Return 0;
                                }
                                Result 1 {
                 SetBin "SoftBins.b90757506_fail_mtt";
                                        Return 1;

                        } }
            }
    '''
            File('TPL/Modules/ARR/array.mtpl').touch(arr_mtpl, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            obj = TorchBuildErrors(tpobj)
            obj.main()
            expect = r'''
[{'id': 250,
  'message': 'Please fix: Torch build error on "array.mtpl" at line number: "73,60,73,105" with '
             'error: "Please fix: Missing required port build error on '
             '"CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501" at line number '
             '"73,60,73,105" with error: "Port 5 is missing from FlowItem definition. Add the '
             'missing port definition '
             '[D:\\Github_action_arls68_01\\_work\\class_arls68\\class_arls68\\Modules\\MIO_D2D_SCM\\MIO_D2D_SCM.mtproj]""',
  'module': 'ARR'}]
'''
            self.assertTextEqual(pformat(obj.result, width=100), expect)
            self.assertEqual(len(obj.passed), 3)

    def test_TP0346_pass(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7f'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            arr_mtpl = r'''{
                Version 1.0;
                ProgramStyle = Modular;
                TestPlan ARR;
                Import array.usrv;

                Test iCSimpleScoreboardTest CCA {
                        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                        level = "BASE::DDR_univ_lvl_max_lvl";
                        patlist = "shops_L_list";
                        PatternNameCounterIndexes = "9,10,11,12,13,14,15|8,9,10,11,12,13,14|9,10,11,12,13,14,16";
                        bypass_global = "0";
                        BaseNumbers = "12476,11051,12309";
                        FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters,per_pattern_printing";
                }
                Test iCFuncTest CCB {
                        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                        level = "BASE::DDR_univ_lvl_nom_lvl";
                        patlist = "shops_H_list";
                        PatternNameCounterIndexes = "9,10,11,12,13,14,15|9,10,11,12,13,14,15|9,10,11,12,13,14,15";
                        BaseNumbers = "12476,11051,12309";
                }
                Test iCFuncTest CCD {
                        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                        level = "BASE::DDR_univ_lvl_nom_lvl";
                        patlist = "shops_H_list";
                        PatternNameCounterIndexes = "9,10,11,12,13,14,15|9,10,11,12,13,14,15|9,10,11,12,13,14,15";
                        BaseNumbers = "12476,11051,12309";
                        FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters";
                }
                Test  iCFuncTest CCC1
                {
                        user_mode = "DEFAULT_MODE";
                }
                Test  iCFuncTest ini1
                {
                        user_mode = "DEFAULT_MODE";
                }
                Test iCFuncTest CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501
                {
                    BypassPort = -1;
                    TestMode = "SingleVmin";
                    LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                    Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                    TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
                    PatternNameCounterIndexes = "9,10,11,12,13,14,15|8,9,10,11,12,13,14|9,10,11,12,13,14,16";
                    BaseNumbers = "12476,11051,12309";
                    FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters,per_pattern_printing";
                    FlowIndex = "1";
                    VoltageTargets = "VCF";
                    CornerIdentifiers = "CLR0@F1";
                    FlowIndexCallbackName = "CheckFlow(RING)";
                }

                Test VminTC CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502
                {
                    BypassPort = -1;
                    TestMode = "SingleVmin";
                    LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                    Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                    TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
                    PatternNameCounterIndexes = "9,10,11,12,13,14,15|9,10,11,12,13,14,15|9,10,11,12,13,14,15";
                    #BaseNumbers = "12476,11051,12309";
                    BaseNumbers = "12476,11051";
                    #FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters";
                }
                Test PrimeFlowControlSetTestMethod SetFlowInfo_ATOMC_Flow1
                {
                    DomainName = "ATOMC";
                    DomainValue = 1;
                }
                DUTFlow MAIN1  {
                    DUTFlowItem CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501 CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501
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
                            IncrementCounters SCN_ATOM_CXX::n15010694_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_0;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 1
                        {
                            Property PassFail = "Pass";
                            #GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                            GoTo CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502;
                        }
                        Result 2
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010695_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_2;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 3
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_3;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 4
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010699_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_4;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 5
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15010698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_5;
                            IncrementCounters SCN_ATOM_CXX::n90413665_fail_CA2TF_ATOM_VMIN_K_CATF2_X_VATOM_F6_AT_F6_FREQ_ATOM_FUSA_RECOVERY_5;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                    }
                    DUTFlowItem CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502 CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502
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
                            IncrementCounters SCN_ATOM_CXX::n15020694_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_0;
                            Return 0;
                        }
                        Result 1
                        {
                            Property PassFail = "Pass";
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                        Result 2
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020695_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_2;
                            Return 0;
                        }
                        Result 3
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_3;
                            Return 0;
                        }
                        Result 4
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020699_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_4;
                            Return 0;
                        }
                        Result 5
                        {
                            Property PassFail = "Fail";
                            IncrementCounters SCN_ATOM_CXX::n15020698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_5;
                            IncrementCounters SCN_ATOM_CXX::n90413665_fail_CA2TF_ATOM_VMIN_K_CATF2_X_VATOM_F6_AT_F6_FREQ_ATOM_FUSA_RECOVERY_5;
                            SetBin SoftBins.b90414119_fail_SCN_ATOM_C28_CA1TF_ATOM_SB_K_BEGCPU_X_VATOM_X_0800_ATOM0_SHARED_BIN;
                            GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                        }
                    }
                        DUTFlowItem SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1 SetFlowInfo_ATOMC_Flow1
                    {
                        Result -2
                        {
                            Property PassFail = "Fail";
                            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                            Return -1;
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
                            Return 0;
                        }
                    }
                }
                DUTFlow INIT1  {
                        DUTFlowItem ini1 ini1 {
                                Result 0 {
                 SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;
                                        Return 0;
                                }
                                Result 1 {
                 SetBin "SoftBins.b90757506_fail_mtt";
                                        Return 1;

                        } }
            }
    '''
            File('TPL/Modules/ARR/array.mtpl').touch(arr_mtpl, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            obj = TorchBuildErrors(tpobj)
            obj.main()
            self.assertEqual(obj.result, [])    # no error
            self.assertEqual(len(obj.passed), 3)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
