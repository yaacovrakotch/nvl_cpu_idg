#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for inst_name_chk.py

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, UT_DIR_REPO, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.nvl_inst_name_chk2 import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock, patch, mock_open
from gadget.gizmo import with_, MockVar
import shutil


ut_blueprint = """BEGCPUMAX BEGGCDMAX BEGHUBMAX BEGIN BEGINCPU BEGINCPUNOM BEGINCPUPKG BEGINGCD BEGINGCDNOM
        BEGINGCDPKG BEGINHUB BEGINHUBNOM BEGINHUBPKG BEGINPCD BEGINPCD1 BEGINPCD2 BEGINPCD3 BEGINPCD4 BEGINPCD5
        BEGINPCD6 BEGINPCDNOM BEGINPCDPKG BEGINPREPRL1 BEGPCDMAX BGEINPREPRL2 CATCLRF1 CATCLRF2 CATCLRF3 CATCLRF4
        CATCLRF4LO CATCLRF5 CATCLRF5LO CATCLRF6 CATCLRF6LO CATCLRFMIN CATF1 CATF2 CATF3 CATF4 CATF4LO CATF5 CATF5LO
        CATF6 CATF6LO CATFMIN CCLRF1 CCLRF2 CCLRF3 CCLRF4 CCLRF4LO CCLRF5 CCLRF5LO CCLRF6 CCLRF6LO CCLRFMIN CCRF1 CCRF2
        CCRF3 CCRF4 CCRF4LO CCRF5 CCRF5LO CCRF6 CCRF6LO CCRFMIN CGTF1 CGTF2 CGTF3 CGTF4 CGTF5 CGTFMIN CSNF1 CSNF2 CSNF3
        CSNFMIN END ENDCPU ENDCPUMAX ENDCPUNOM ENDCPUPKG ENDGCD ENDGCDMAX ENDGCDNOM ENDGCDPKG ENDHUB ENDHUBMAX
        ENDHUBNOM ENDHUBPKG ENDPCD ENDPCDMAX ENDPCDNOM ENDPCDPKG ENDPOSTYBSCPU ENDPOSTYBSGCD ENDPOSTYBSHUB ENDPOSTYBSPCD
        ENDPREPRL0 ENDPREPRL1 ENDPREPRL2 ENDPREPRL3 ENDPREPRL4 ENDYBSCPU ENDYBSGCD ENDYBSHUB ENDYBSPCD EOTRAMP
        F6TEMPDOWN FACT FACTFUSBUILDCPU FACTFUSBUILDGCD FACTFUSBUILDHUB FACTFUSBUILDPCD FACTFUSBURNCPU FACTFUSEBURNGCD
        FACTFUSEBURNHUB FACTFUSEBURNPCD FACTPOSTFUSEBURN FACTPREFUSEBURN FACTPREPRL0 FACTPREPRL1 FINAL HVBICPU
        HVBICPUPKG HVBIGCD HVBIGCDPKG HVBIHUB HVBIHUBPKG HVBIPCD HVBIPCDPKG HVBIPREPRL0 LTTCCOMMON LTTCCPU LTTCCPUMAX
        LTTCCPUPKG LTTCGCD LTTCGCDMAX LTTCGCDPKG LTTCHUB LTTCHUBMAX LTTCHUBPKG LTTCPCD LTTCPCDMAX LTTCPCDPKG LTTCPOST
        LTTCPREPRL0 LTTCPREPRL1 LTTCPREPRL2 LTTCRAMPCHKCPU LTTCRAMPGCD LTTCRAMPHUB LTTCRAMPPCD LTTCRAMPSETCPU MAXATCLRHI
        MAXATCLRLO MAXATHI MAXATLO MAXCLRHI MAXCLRLO MAXCRHI MAXCRLO MAXGT MAXHITEMPDOWN MAXSN PRESRHAT PRESRHCLR
        PRESRHCR PRESRHGT PRESRHSN PSTSRHAT PSTSRHCLR PSTSRHCR PSTSRHGT PSTSRHSN RESUMETEMP SATCLRF1 SATCLRF3 SATCLRF4
        SATCLRF4LO SATCLRF5 SATCLRF5LO SATCLRF6 SATCLRF6LO SATCRLF2 SATF1 SATF2 SATF3 SATF4 SATF4LO SATF5 SATF5LO SATF6
        SATF6LO SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF4LO SCLRF5 SCLRF5LO SCLRF6 SCLRF6LO SCRF1 SCRF2 SCRF3 SCRF4
        SCRF4LO SCRF5 SCRF5LO SCRF6 SCRF6LO SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SHAREDRAILSMAX SHAREDRAILSMAX SHAREDRAILSMIN
        SHAREDRAILSMINLTTC SHAREDRAILSNOM SHAREDRAILSNOMFUSEBURN SPEEDPREPRL0 SPEEDPREPRL1 SPEEDPREPRL2 SPEEDPREPRL3
        SPEEDPREPRL4 SPEEDPREPRL5 SPEEDPREPRL6 SPEEDPREPRL7 SSHDCF1 SSNF1 SSNF2 SSNF3 START STARTANA0CPU STARTANA0GCD
        STARTANA0HUB STARTANA0PCD STARTANA1CPU STARTANA1GCD STARTANA1HUB STARTANA1PCD STARTCPUNOM STARTGCDNOM
        STARTHPTPDRVCPU STARTHPTPDRVGCD STARTHPTPDRVHUB STARTHPTPDRVPCD STARTHUBNOM STARTPATMODS STARTPCDNOM
        STARTPREPRL0 STARTPREPRL1 STARTPREPRL2 STARTPREPRL3 STARTPREPRL4 STARTPWR STARTPWRCPU STARTPWRGCD STARTPWRHUB
        STARTPWRPCD F5TEMPDOWN F4XAT F3XATCCF FMINXCCF BEGINCPUMAX FMAXXCCF F4XATCCF F3XCR FMINXAT F1XCCF FMAXXAT F4XCR
        F4XCCFLO FMINXATCCF F1XAT FMAXXATCCF F4XATLO FMINXCR F1XATCCF FMAXXCR VMAXXCCFLO F4XATCCFLO SPEEDCPUEMPTY0 F1XCR
        VMAXXCCF VMAXXATLO F4XCRLO SPEEDCPUEMPTY1 FMAXXCCFLO VMAXXAT VMAXXATCCFLO F2XCCF SPEEDCPUEMPTY2 FMAXXATLO
        VMAXXATCCF VMAXXCRLO F2XAT FMAXXATCCFLO VMAXXCR F3XCCF F2XATCCF FMAXXCRLO F4XCCF F3XAT F2XCR ALARM BEGINPREPRL0
        LTTCSHAREDRAILSMIN FACTEOTRAMP STARTCPUPATMODSPKG LTTCRAMP STARTSHAREDRAILSNOM ENDSHAREDRAILSMAX
        STARTGCDPATMODSPKG BEGINSHAREDRAILSNOM STARTHUBPATMODSPKG LTTCSHAREDRAILSMIN1 FACTSHAREDRAILSNOM
        STARTPCDPATMODSPKG STARTSHAREDRAILSMIN FACTPREPLRL0 HVBISHAREDRAILSMIN BEGINSHAREDRAILSMAX BEGINPREPRL2
        ENDSHAREDRAILSMIN LTTCSHAREDRAILSMAX FACTPREPLRL1 SPEEDSHAREDRAILSMIN ENDSHAREDRAILSNOM BEGINSHAREDRAILSMIN
        STARTSHAREDRAILSMIN1""".split()


def filter(inp):
    """Filter out the ini records"""
    return [x for x in inp if not x['message'].startswith(('init1 has lower case characters',
                                                           'ini1 has lower case characters'))]


class TestInstName(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/Simple7h/POR_TP/TGLH81/EnvironmentFile.env').init()
        print("Running test_basic...")
        obj = NVLTestNameChk(tpobj)
        obj.main()
        # pprint(obj.result)

        self.assertEqual(filter(obj.result), [])      # because of iter_tests()
        self.assertEqual(len(obj.passed), 3)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_basicX(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7l/POR_TP/TGLH81/EnvironmentFile.env').init()
        print("Running test_basicX...")
        obj = NVLTestNameChk(tpobj)
        obj.main()
        # pprint(obj.result)
        expect = [{'id': 239,
                   'message': 'CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1501 '
                   'is not following naming convention please fix 5th field '
                   'currently set as "_MAXAT_". It should be one of the valid '
                   'Subflows in the TPBlueprint.  Please see NVL Test Instance '
                   'Naming Convention in goto/mtlits',
                   'module': 'ARR'},
                  {'id': 239,
                   'message': 'CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1501 '
                   'is not following naming convention please fix 7th field '
                   'currently set as "_VATOM_". It should be any of these '
                   'AT|ATA|ATB|CCF|CCFA|CCFB|CR|CRA|CRB|CLRA|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X|VNNAON|VCCIA|VCCIO|V1P8A|VCCSA|VDD2H|VCCGT|VCCLPECORE|VDDQ',
                   'module': 'ARR'},
                  {'id': 239,
                   'message': 'CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502 '
                   'is not following naming convention please fix 5th field '
                   'currently set as "_MAXAT_". It should be one of the valid '
                   'Subflows in the TPBlueprint.  Please see NVL Test Instance '
                   'Naming Convention in goto/mtlits',
                   'module': 'ARR'},
                  {'id': 239,
                   'message': 'CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502 '
                   'is not following naming convention please fix 7th field '
                   'currently set as "_VATOM_". It should be any of these '
                   'AT|ATA|ATB|CCF|CCFA|CCFB|CR|CRA|CRB|CLRA|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X|VNNAON|VCCIA|VCCIO|V1P8A|VCCSA|VDD2H|VCCGT|VCCLPECORE|VDDQ',
                   'module': 'ARR'},
                  {'id': 239,
                   'message': 'CCA contains 1 field(s) only.  Should be at least 9 fields',
                   'module': 'SCN'},
                  {'id': 239,
                   'message': 'CCB contains 1 field(s) only.  Should be at least 9 fields',
                   'module': 'SCN'},
                  {'id': 239,
                   'message': 'CCA_1100_BLAH_1501 contains 4 field(s) only.  Should be at least '
                   '9 fields',
                   'module': 'PTH'},
                  {'id': 239,
                   'message': 'CCA_1200_BLAH_1502 contains 4 field(s) only.  Should be at least '
                   '9 fields',
                   'module': 'PTH'}]
        self.assertEqual(filter(obj.result), expect)      # because of iter_tests()
        self.assertEqual(len(obj.passed), 0)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7h', chdir=True, delete=True)
    def test_ut_name(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        File('BaseInputs/CPU/blah.txt').touch(mkdir=True)
        File('BaseInputs/GCD/blah.txt').touch(mkdir=True)

        # pass case
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_SHAREDRAILSNOM_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 0)

        # fail case but with CPU in subflow name
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 2)

        # fail case CPU in subflow but CPUINIT not exist in blueprint. Non existent.
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_CPUINIT_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 1)

        # pass case - LOTSTARTFLOW is special
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_LOTSTARTFLOW_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 0)

        # pass case - BEGCPUMAX - This repo is CPU+GCD
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_BEGCPUMAX_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 0)

        # pass case - BEGHUBMAX - This repo is CPU+GCD - In blueprint, not in BaseInputs/CPU
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_BEGHUBMAX_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 0)

        # pass case - BEGINHUBPXG - This repo is CPU+GCD - Not in blueprint, but OK for dielet
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_BEGINHUBPXG_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 0)

        # fail case - BEGINCPUPXG - This repo is CPU+GCD - Fail this is type. Typo case.
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_BEGINCPUPXG_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 1)

        # pass case - VCCSA power domain (7th field).
        testcase = [('ARR', 'CA2TF_ATOM_VMAX_K_BEGINCPU_X_VCCSA_F6_3800_FUSA_VMAX_RECOVERY_1501', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 0)

        # fail case - corner case... double _'s.
        testcase = [('ARR', 'CTRL_X_SCREEN_K_INIT__X_X_X_X_TIUID', None, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = NVLTestNameChk(tpobj)
            obj.main()
            self.assertEqual(len(obj.result), 1)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_basic2(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7i/POR_TP/TGLH81/EnvironmentFile.env').init()
        print("Running test_basic2...")
        obj = NVLTestNameChk(tpobj)
        obj.main()
        # pprint(obj.result)

        # check results, one fail and one pass

        expect = [{'id': 239,
                   'message': 'CA2TF_ATOM_VMAX_K_VICOYCOY_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501 '
                   'is not following naming convention please fix 5th field '
                   'currently set as "_VICOYCOY_". It should be one of the valid '
                   'Subflows in the TPBlueprint.  Please see NVL Test Instance '
                   'Naming Convention in goto/mtlits',
                   'module': 'ARR'},
                  {'id': 239,
                   'message': 'CA2TF_ATOM_VMAX_K_VICOYCOY_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502 '
                   'is not following naming convention please fix 5th field '
                   'currently set as "_VICOYCOY_". It should be one of the valid '
                   'Subflows in the TPBlueprint.  Please see NVL Test Instance '
                   'Naming Convention in goto/mtlits',
                   'module': 'ARR'}]
        # pprint(filter(obj.result))
        self.assertEqual(filter(obj.result), expect)
        self.assertEqual(len(obj.passed), 2)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_7th_5th_field(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7j'
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
            Test VminTC CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_X_3800_FUSA_VMAX_RECOVERY_1501
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
                DUTFlowItem CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_X_3800_FUSA_VMAX_RECOVERY_1501 CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_X_3800_FUSA_VMAX_RECOVERY_1501
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
            print("Running test_7th_5th_field...")
            obj = NVLTestNameChk(tpobj)
            obj.main()
            # pprint(obj.result)
            # pprint(filter(obj.result))
            result = [x for x in obj.result if '5th field' in x['message']]
            self.assertEqual(len(result), 2)
            result = [x for x in obj.result if '7th field' in x['message']]
            self.assertEqual(len(result), 2)
            self.assertEqual(len(obj.passed), 0)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_4th_field(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7g'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            arr_mtpl = r'''{
            Version 1.0;
            ProgramStyle = Modular;
            TestPlan PTH;
            Import pth.usrv;

            Test iCSimpleScoreboardTest CAM_ATOM_VMIN_Y_CATF1_X_ATA_F1_0400_RF_2001
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_hvm_x";
                bypass_global = "BYPASSVars.BYPASS_in_ENGINEERING_MODE";
            }
            Test iCFuncTest CTRL_X_UC_X_START_X_X_X_X_SETTPSGSDSCHECK
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_special_x";
                bypass_global = "0";
            }
            Test iCFuncTest ini1
            {
                user_mode = "DEFAULT_MODE";
            }

            DUTFlow MAIN2
            {
                DUTFlowItem CAM_ATOM_VMIN_Y_CATF1_X_ATA_F1_0400_RF_2001 CAM_ATOM_VMIN_Y_CATF1_X_ATA_F1_0400_RF_2001
                {
                    Result 0
                    {
                        GoTo CTRL_X_UC_X_START_X_X_X_X_SETTPSGSDSCHECK;
                    }
                    Result 1
                    {
                        GoTo CTRL_X_UC_X_START_X_X_X_X_SETTPSGSDSCHECK;
                        Return  1;

                    }
                }
                DUTFlowItem CTRL_X_UC_X_START_X_X_X_X_SETTPSGSDSCHECK CTRL_X_UC_X_START_X_X_X_X_SETTPSGSDSCHECK
                {
                    Result 1
                    {
                        SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;
                        Return  1;
                    }
                }
            }

            DUTFlow INIT2
            {
                DUTFlowItem ini1 ini1
                {
                    Result 0
                    {
                        Return 0;
                        SetBin SoftBins.b90757502_fail_some_common_SHARED_BIN;
                    }
                    Result 1
                    {
                        SetBin SoftBins.b90757501_fail_NSIO;
                        SetBin "SoftBins.b90757506_fail_mtt";
                        Return 1;

                    }
                }
            }

'''
            File('TPL/Modules/PTH/pth.mtpl').touch(arr_mtpl, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_4th_field...")
            obj = NVLTestNameChk(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 239,
                       'message': 'CAM_ATOM_VMIN_Y_CATF1_X_ATA_F1_0400_RF_2001 is not following '
                                  'naming convention please fix 4th field currently set as "_Y_". '
                                  'Only accepts "K|E|X"',
                       'module': 'PTH'}]
            self.assertEqual(filter(obj.result), expect)
            self.assertEqual(len(obj.passed), 3)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_6th_field(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7g'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            arr_mtpl = r'''{
            Version 1.0;
            ProgramStyle = Modular;
            TestPlan PTH;
            Import pth.usrv;

            Test iCSimpleScoreboardTest CAM_ATOM_VMIN_K_CATF1_HIHO_ATA_F1_0400_RF_2001
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_hvm_x";
                bypass_global = "BYPASSVars.BYPASS_in_ENGINEERING_MODE";
            }
            Test iCFuncTest CTRL_X_UC_X_START_V_X_X_X_SETTPSGSDSCHECK
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_special_x";
                bypass_global = "0";
            }
            Test iCFuncTest ini1
            {
                user_mode = "DEFAULT_MODE";
            }

            DUTFlow MAIN2
            {
                DUTFlowItem CAM_ATOM_VMIN_K_CATF1_HIHO_ATA_F1_0400_RF_2001 CAM_ATOM_VMIN_K_CATF1_HIHO_ATA_F1_0400_RF_2001
                {
                    Result 0
                    {
                        GoTo CTRL_X_UC_X_START_V_X_X_X_SETTPSGSDSCHECK;
                    }
                    Result 1
                    {
                        GoTo CTRL_X_UC_X_START_V_X_X_X_SETTPSGSDSCHECK;
                        Return  1;

                    }
                }
                DUTFlowItem CTRL_X_UC_X_START_V_X_X_X_SETTPSGSDSCHECK CTRL_X_UC_X_START_V_X_X_X_SETTPSGSDSCHECK
                {
                    Result 1
                    {
                        SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;
                        Return  1;
                    }
                }
            }

            DUTFlow INIT2
            {
                DUTFlowItem ini1 ini1
                {
                    Result 0
                    {
                        Return 0;
                        SetBin SoftBins.b90757502_fail_some_common_SHARED_BIN;
                    }
                    Result 1
                    {
                        SetBin SoftBins.b90757501_fail_NSIO;
                        SetBin "SoftBins.b90757506_fail_mtt";
                        Return 1;

                    }
                }
            }

'''
            File('TPL/Modules/PTH/pth.mtpl').touch(arr_mtpl, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_6th_field...")
            obj = NVLTestNameChk(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 239,
                       'message': 'CTRL_X_UC_X_START_V_X_X_X_SETTPSGSDSCHECK is not following '
                       'naming convention please fix 6th field currently set as "_V_". '
                       'It should be any of these X|TAP|[TMSDBNH]I[TMSDBNH]O',
                       'module': 'PTH'}]
            self.assertEqual(filter(obj.result), expect)
            # self.assertCountEqual(filter(obj.result), expect)
            self.assertEqual(len(obj.passed), 2)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_8th_field(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7g'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            arr_mtpl = r'''{
            Version 1.0;
            ProgramStyle = Modular;
            TestPlan PTH;
            Import pth.usrv;

            Test iCSimpleScoreboardTest CAM_ATOM_VMIN_K_CATF1_T_ATA_FMIN_0400_RF_2001
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_hvm_x";
                bypass_global = "BYPASSVars.BYPASS_in_ENGINEERING_MODE";
            }
            Test iCFuncTest CTRL_X_UC_X_START_H_X_VIC_X_SETTPSGSDSCHECK
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_special_x";
                bypass_global = "0";
            }
            Test iCFuncTest ini1
            {
                user_mode = "DEFAULT_MODE";
            }

            DUTFlow MAIN2
            {
                DUTFlowItem CAM_ATOM_VMIN_K_CATF1_T_ATA_FMIN_0400_RF_2001 CAM_ATOM_VMIN_K_CATF1_T_ATA_FMIN_0400_RF_2001
                {
                    Result 0
                    {
                        GoTo CTRL_X_UC_X_START_H_X_VIC_X_SETTPSGSDSCHECK;
                    }
                    Result 1
                    {
                        GoTo CTRL_X_UC_X_START_H_X_VIC_X_SETTPSGSDSCHECK;
                        Return  1;

                    }
                }
                DUTFlowItem CTRL_X_UC_X_START_H_X_VIC_X_SETTPSGSDSCHECK CTRL_X_UC_X_START_H_X_VIC_X_SETTPSGSDSCHECK
                {
                    Result 1
                    {
                        SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;
                        Return  1;
                    }
                }
            }

            DUTFlow INIT2
            {
                DUTFlowItem ini1 ini1
                {
                    Result 0
                    {
                        Return 0;
                        SetBin SoftBins.b90757502_fail_some_common_SHARED_BIN;
                    }
                    Result 1
                    {
                        SetBin SoftBins.b90757501_fail_NSIO;
                        SetBin "SoftBins.b90757506_fail_mtt";
                        Return 1;

                    }
                }
            }

'''
            File('TPL/Modules/PTH/pth.mtpl').touch(arr_mtpl, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_8th_field...")
            obj = NVLTestNameChk(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 239,
                       'message': 'CTRL_X_UC_X_START_H_X_VIC_X_SETTPSGSDSCHECK is not following '
                                  'naming convention please fix 6th field currently set as "_H_". '
                                  'It should be any of these X|TAP|[TMSDBNH]I[TMSDBNH]O',
                       'module': 'PTH'},
                      {'id': 239,
                       'message': 'CTRL_X_UC_X_START_H_X_VIC_X_SETTPSGSDSCHECK is not following '
                                  'naming convention please fix 8th field currently set as "_VIC_". '
                                  'This is the corner field, should be '
                                  '[VF]MAX|[VF]MIN|[VF]NOM||F1|F2|F3..Fn or X',
                       'module': 'PTH'}]
            self.assertEqual(filter(obj.result), expect)
            self.assertEqual(len(obj.passed), 3)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_9th_field(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7g'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            arr_mtpl = r'''{
            Version 1.0;
            ProgramStyle = Modular;
            TestPlan PTH;
            Import pth.usrv;

            Test iCSimpleScoreboardTest CAM_aTOM_VMIN_K_CATF1_T_ATA_FMIN_GFM_RF_2001
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_hvm_x";
                bypass_global = "BYPASSVars.BYPASS_in_ENGINEERING_MODE";
            }
            Test iCFuncTest CTRL_X_UC_X_START_VITO_X_F3_123456_SETTPSGSDSCHECK
            {
                timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
                level = "BASE::DDR_univ_lvl_nom_lvl";
                patlist = "cpu_fuse_read_special_x";
                bypass_global = "0";
            }
            Test iCFuncTest ini1
            {
                user_mode = "DEFAULT_MODE";
            }

            DUTFlow MAIN2
            {
                DUTFlowItem CAM_aTOM_VMIN_K_CATF1_T_ATA_FMIN_GFM_RF_2001 CAM_aTOM_VMIN_K_CATF1_T_ATA_FMIN_GFM_RF_2001
                {
                    Result 0
                    {
                        GoTo CTRL_X_UC_X_START_VITO_X_F3_123456_SETTPSGSDSCHECK;
                    }
                    Result 1
                    {
                        GoTo CTRL_X_UC_X_START_VITO_X_F3_123456_SETTPSGSDSCHECK;
                        Return  1;

                    }
                }
                DUTFlowItem CTRL_X_UC_X_START_VITO_X_F3_123456_SETTPSGSDSCHECK CTRL_X_UC_X_START_VITO_X_F3_123456_SETTPSGSDSCHECK
                {
                    Result 1
                    {
                        SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;
                        Return  1;
                    }
                }
            }

            DUTFlow INIT2
            {
                DUTFlowItem ini1 ini1
                {
                    Result 0
                    {
                        Return 0;
                        SetBin SoftBins.b90757502_fail_some_common_SHARED_BIN;
                    }
                    Result 1
                    {
                        SetBin SoftBins.b90757501_fail_NSIO;
                        SetBin "SoftBins.b90757506_fail_mtt";
                        Return 1;

                    }
                }
            }

'''
            File('TPL/Modules/PTH/pth.mtpl').touch(arr_mtpl, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_9th_field...")
            obj = NVLTestNameChk(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 239,
                       'message': 'CAM_aTOM_VMIN_K_CATF1_T_ATA_FMIN_GFM_RF_2001 has lower case '
                       'characters.  Please make it all caps.',
                       'module': 'PTH'},
                      {'id': 239,
                       'message': 'CTRL_X_UC_X_START_VITO_X_F3_123456_SETTPSGSDSCHECK is not '
                       'following naming convention please fix 6th field currently set '
                       'as "_VITO_". It should be any of these '
                       'X|TAP|[TMSDBNH]I[TMSDBNH]O',
                       'module': 'PTH'},
                      {'id': 239,
                       'message': 'CTRL_X_UC_X_START_VITO_X_F3_123456_SETTPSGSDSCHECK is not '
                       'following naming convention please fix 9th field currently set '
                       'as "_123456_".  This is the freq field, should be in digits in '
                       'MHz(for freq e.g. 5000 (min of 4 and max of 5 digits) or either '
                       '"HFM", "LFM", "TFM", or "X"',
                       'module': 'PTH'}]
            self.assertEqual(filter(obj.result), expect)
            self.assertEqual(len(obj.passed), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/Simple7h', chdir=True, delete=True)
    def test_basic_ra(self):
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.py').touch('''
MAIN_code = """
START_SubFlow       ARR_CXX   rm2m2
# SHAREDRAILSNOM    something   this is just a comment
BEGINCPUPKG_TopFlow SCN_CXX   rm2m2
"""
''')
        File('Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows_Config.py').touch('''
''', mkdir=True)
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        print("Running test_basic_RA...")
        obj = NVLTestNameChk(tpobj)
        obj.main()
        # pprint(obj.result)

        self.assertEqual(len(obj.result), 6)
        self.assertEqual(len(obj.passed), 2)     # START_SubFlow and BEGINCPUPKG_TopFlow passing

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_csharp_trialtest_fields(self):
        tpobj = Mock()
        tpobj.get_all_mtpl_from_stpl.return_value = ['dummy.mtpl']
        tpobj.mtpl = Mock()
        tpobj.mtpl.iter_tests.return_value = []

        expect = [{'id': 239,
                   'message': 'The 4th field of CSharpTrialTest name '
                              'TEST_A_B_C_Y_D_X_ATA_X_1234 used by MultiTrialTest MTTest1 '
                              'should be K|E|X only',
                   'module': 'dummy'},
                  {'id': 239,
                   'message': 'The 6th field of CSharpTrialTest name '
                              'TEST_A_B_C_Y_D_X_ATA_X_1234 used by MultiTrialTest MTTest1 '
                              'should meet this regex (X|TAP|[TMSDBNH]I[TMSDBNH]O)',
                   'module': 'dummy'},
                  {'id': 239,
                   'message': 'The 8th field of CSharpTrialTest name '
                              'TEST_A_B_C_Y_D_X_ATA_X_1234 used by MultiTrialTest MTTest1 '
                              'should meet this regex (X|FBAT|[VF]?MAX|[VF]?MIN|[VF]?NOM|Fn)',
                   'module': 'dummy'}]

        mtpl_content = [
            'MultiTrialTest MTTest1\n',
            'CSharpTrialTest "TEST_A_B_C_Y_D_X_ATA_X_1234"\n',
            'CSharpTrialTest "TEST_A_B_C_K_VIHO_ATA_X_1234"\n',
            'CSharpTrialTest "TEST_A_B_C_K_D_X_ATA_X_1234"\n',
        ]
        # Ensure the mock file supports iteration over lines
        m = mock_open(read_data=''.join(mtpl_content))
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        m.return_value.readlines = lambda: mtpl_content

        with patch('builtins.open', m):
            with patch('os.listdir', return_value=['CPU', 'GCD', 'HUB', 'PCD']):
                obj = NVLTestNameChk(tpobj)
                obj.main()
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)

    @with_(MockVar, NVLTestNameChk, 'read_all_py', Mock(return_value=ut_blueprint))
    def test_csharp_7th_fields(self):
        print("TEST_CSHARP_7th")
        tpobj = Mock()
        tpobj.get_all_mtpl_from_stpl.return_value = ['dummy.mtpl']
        tpobj.mtpl = Mock()
        tpobj.mtpl.iter_tests.return_value = []

        expect = [{'id': 239,
                   'message': 'The 4th field of CSharpTrialTest name '
                              'TEST_A_B_C_K_X_VATOM_ATA_X_1234 used by MultiTrialTest MTTest1 '
                              'should be K|E|X only',
                   'module': 'dummy'},
                  {'id': 239,
                   'message': 'The 7th field of CSharpTrialTest name '
                              'TEST_A_B_C_K_X_VATOM_ATA_X_1234 used by MultiTrialTest MTTest1 '
                              'should meet this regex '
                              '(AT|ATA|ATB|CCF|CCFA|CCFB|CR|CRA|CRB|CLRA|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X|VNNAON|VCCIA|VCCIO|V1P8A|VCCSA|VDD2H|VCCGT|VCCLPECORE|VDDQ)',
                   'module': 'dummy'},
                  {'id': 239,
                   'message': 'The 8th field of CSharpTrialTest name '
                              'TEST_A_B_C_K_X_VATOM_ATA_X_1234 used by MultiTrialTest MTTest1 '
                              'should meet this regex (X|FBAT|[VF]?MAX|[VF]?MIN|[VF]?NOM|Fn)',
                   'module': 'dummy'}]

        mtpl_content = [
            'MultiTrialTest MTTest1\n',
            'CSharpTrialTest "TEST_A_B_C_K_X_VATOM_ATA_X_1234"\n',
        ]
        m = mock_open(read_data=''.join(mtpl_content))
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        m.return_value.readlines = lambda: mtpl_content

        with patch('builtins.open', m):
            with patch('os.listdir', return_value=['CPU', 'GCD', 'HUB', 'PCD']):
                obj = NVLTestNameChk(tpobj)
                obj.main()
        self.assertEqual(filter(obj.result), expect)
        self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
