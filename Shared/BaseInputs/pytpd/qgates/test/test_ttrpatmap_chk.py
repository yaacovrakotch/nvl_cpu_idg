#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for ttrpatmap_chk.py

"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.ttrpatmap_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import shutil


class TestInstName(TestCase):

    def test_all_fail_case_w_pipe(self):
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
            print("Running test_all_fail_case_w_pipe...")
            obj = TtrPatMap(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 170,
                      'message': 'Test:CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501 '
                                 'uses letters for pattern_name_map on value#2 of '
                                 'pattern_name_map=9,10,11,12,13,14,15|8,9,10,11,12,13,14|9,10,11,12,13,14,16!',
                       'module': 'ARR'},
                      {'id': 182,
                      'message': 'Test:CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501 '
                                 'has a user_defined value on value# 3 of '
                                 'pattern_name_map=9,10,11,12,13,14,15|8,9,10,11,12,13,14|9,10,11,12,13,14,16!',
                       'module': 'ARR'},
                      {'id': 181,
                      'message': 'Test:CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501 '
                                 'uses per_pattern_printing and base# at the same time! '
                                 'patmap=9,10,11,12,13,14,15|8,9,10,11,12,13,14|9,10,11,12,13,14,16 '
                                 'base#=12476,11051,12309',
                       'module': 'ARR'},
                      {'id': 182,
                      'message': 'Test:CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502 '
                                 'has mismatched number of values for patternmap (3) and '
                                 'basenumber (2)',
                       'module': 'ARR'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 0)

    def test_all_fail_case_wo_pipe(self):
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
                PatternNameCounterIndexes = "9,10,11,12,13,14,16";
                BaseNumbers = "12476";
                FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters,per_pattern_printing";
            }

            Test VminTC CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502
            {
                BypassPort = -1;
                TestMode = "SingleVmin";
                LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
                PatternNameCounterIndexes = "0,2,3,4,5,6,7";
                BaseNumbers = "12476, 12345";
                FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters";
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
            print("Running test_all_fail_case_w_pipe...")
            obj = TtrPatMap(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 181,
                      'message': 'Test:CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501 '
                                 'uses per_pattern_printing and base# at the same time! '
                                 'patmap=9,10,11,12,13,14,16 base#=12476',
                       'module': 'ARR'},
                      {'id': 170,
                      'message': 'Test:CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502 '
                                 'uses letters for pattern_name_map=0,2,3,4,5,6,7!',
                       'module': 'ARR'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 0)

    def test_passing_case(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7b'
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
                PatternNameCounterIndexes = "1,2,3,4,5,6,7|9,10,11,12,13,14,15|9,10,11,12,13,14,15";
                BaseNumbers = "12476,11051,12309";
                FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters";
            }

            Test VminTC CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1502
            {
                BypassPort = -1;
                TestMode = "SingleVmin";
                LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
                PatternNameCounterIndexes = "9,10,11,12,13,14,15";
                BaseNumbers = "12476";
                FeatureSwitchSettings = "fivr_mode_on,print_per_target_increments,print_scoreboard_counters";
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
            print("Running test_pass_case...")
            obj = TtrPatMap(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = []
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 4)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
