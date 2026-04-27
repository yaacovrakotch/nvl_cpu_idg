#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for cttr_pup_comp.py

"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.cttr_pup_comp import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import shutil


class TestInstName(TestCase):

    def test_fail_case_176(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7b/POR_TP/TGLH81/EnvironmentFile.env').init()
        print("Running test_fail_case_176...")
        obj = CttrPup(tpobj)
        obj.main()
        # pprint(obj.result)

        # check results, one fail and one pass

        expect = [{'id': 176,
                  'message': 'Test:CCA_1100_blah_1501 does not follow speedflow naming',
                   'module': 'PTH'},
                  {'id': 176,
                  'message': 'Test:CCA_1200_blah_1502 does not follow speedflow naming',
                   'module': 'PTH'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    def test_fail_case_177(self):
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
                    bypass_global = "0";
                    base_number = 2160;
            }
            Test iCFuncTest CCB {
                    timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                    level = "BASE::DDR_univ_lvl_nom_lvl";
                    patlist = "shops_H_list";
                    base_number = 2161;
            }
            Test iCFuncTest CCD {
                    timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                    level = "BASE::DDR_univ_lvl_nom_lvl";
                    patlist = "shops_H_list";
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
                LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
            }

            Test VminTC CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502
            {
                BypassPort = -1;
                LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_stf400_min_lvl";
                Patlist = "scn_cmt_x_vccia_f6_vmaxf6_sNs400_cmt_fusa4c_tr_classhvm_list";
                TimingsTc = "SCN_ATOM_CXX::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400_SHARED_BE1D8FA1919C492776060D8F180E14D721A91A7C55072B64CBBF53F2E86EAA00";
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
                        GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                    }
                    Result 1
                    {
                        Property PassFail = "Pass";
                        GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                    }
                    Result 2
                    {
                        Property PassFail = "Fail";
                        IncrementCounters SCN_ATOM_CXX::n15010695_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_2;
                        GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                    }
                    Result 3
                    {
                        Property PassFail = "Fail";
                        IncrementCounters SCN_ATOM_CXX::n15010698_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_ATOM0_VMAX_RECOVERY_3;
                        GoTo SetFlowInfo_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_AT_F6_FREQ_FUSA_RECOVERY_P5_Flow1;
                    }
                    Result 4
                    {
                        Property PassFail = "Fail";
                        IncrementCounters SCN_ATOM_CXX::n15010699_fail_CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_FUSA_VMAX_RECOVERY_4;
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
                DUTFlowItem CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502 CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502
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
            print("Running test_fail_case_177...")
            obj = CttrPup(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 177,
                      'message': 'Test:CA2TF_ATOM_VMAX_K_CATF6_X_VATOM_F5_3800_FUSA_VMAX_RECOVERY_1501 '
                                 'sf=CATF6 and fc=F5 do not match',
                       'module': 'ARR'},
                      {'id': 176,
                      'message': 'Test:CCA_1100_blah_1501 does not follow speedflow naming',
                       'module': 'PTH'},
                      {'id': 176,
                      'message': 'Test:CCA_1200_blah_1502 does not follow speedflow naming',
                       'module': 'PTH'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 2)

    def test_passing_case(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7b'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            pth_mtpl = r'''{
            Version 1.0;
            ProgramStyle = Modular;
            TestPlan PTH;
            Import pth.usrv;

            Test iCSimpleScoreboardTest LSA_ATOM_VMIN_K_SATF6_X_VCCIA_F6_3600_ROM_1501 {
                    timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                    level = "BASE::DDR_univ_lvl_nom_lvl";
                    patlist = "cpu_fuse_read_hvm_x";
                    bypass_global = "BYPASSVars.BYPASS_in_ENGINEERING_MODE";
            }
            Test iCFuncTest SSA_ATOM_SB_K_MAXAT_X_VCCIA_F1_0400_L2C6_1502 {
                    timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                    level = "BASE::DDR_univ_lvl_nom_lvl";
                    patlist = "cpu_fuse_read_special_x";
                    bypass_global = "0";
            }
            Test iCFuncTest ini1
            {
                    user_mode = "DEFAULT_MODE";
            }

            DUTFlow MAIN2  {
                    DUTFlowItem CCA LSA_ATOM_VMIN_K_SATF6_X_VCCIA_F6_3600_ROM_1501 {
                            Result 0 {
                                    GoTo CCA1;
                            }
                            Result 1 {
                                    GoTo CCB;
                                    Return  1;

                    } }
                    DUTFlowItem CCB SSA_ATOM_SB_K_MAXAT_X_VCCIA_F1_0400_L2C6_1502 {
                            Result 1 {
             SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;
                                    Return  1;
                    } }
                    DUTFlowItem CCA1 LSA_ATOM_VMIN_K_SATF6_X_VCCIA_F6_3600_ROM_1501 {
                            Result 1 {
            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                                    Return  1;

                    } }
            }

            DUTFlow INIT2  {
                    DUTFlowItem ini1 ini1 {
                            Result 0 {
                                    Return 0;
             SetBin SoftBins.b90757502_fail_some_common_SHARED_BIN;
                            }
                            Result 1 {
             SetBin SoftBins.b90757501_fail_NSIO;
             SetBin "SoftBins.b90757506_fail_mtt";
                                    Return 1;

                    } }
            }
'''
            File('TPL/Modules/PTH/pth.mtpl').touch(pth_mtpl, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_passing_case...")
            obj = CttrPup(tpobj)
            obj.main()
            pprint(obj.result)
            expect = []
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
