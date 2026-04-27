#from turtle import pos
from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeShmooTestMethod,PrimeScanSPOFITestMethod, RunCallback, ApexTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig

########################################################################
# ddaudmai ww05'2025 - SORT basic skeleton tryout
# ddaudmai ww13'2025 - CLASS tests, subflows details adjustment to fit class requirement
# ddaudmai ww19'2025 - Added in stuckat for BEGINCPU, mtt atspeed for FI-F4 XCR subflows, all tests in bypassed mode for now.
# ddaudmai ww20'2025 - F5 is added in F5XCRLO (need to check if it really is correct, F5XCR triggers QG-239)  

# local module parameter setting
LOCAL_PARAM_DtsConfiguration = ""
LOCAL_PARAM_PACMON_MaximumFailuresPerPattern = 1500
LOCAL_PARAM_PACMON_MaximumTotalFailures = 15000
LOCAL_PARAM_SHMOO_PrintFormat = "ShmooHub"
LOCAL_PARAM_SHMOO_XAxisParam = "p_mtd_per"
LOCAL_PARAM_SHMOO_YAxisParam = "p_vcccore_spec"
LOCAL_PARAM_SRH_EDGE_TICK = 0
LOCAL_PARAM_SRH_MAX_FAILS = 0
LOCAL_PARAM_THERMAL_PinNames = ""
LOCAL_PARAM_THERMAL_LowerTolerance = ""
LOCAL_PARAM_THERMAL_UpperTolerance = ""
LOCAL_PARAM_VMINTC_EndVoltageLimits_NOM = "0.9"
LOCAL_PARAM_VMINTC_ExecutionMode_SCB = "SearchWithScoreboard"
LOCAL_PARAM_VMINTC_ExecutionMode_SRH = "Search"
LOCAL_PARAM_VMINTC_FailCaptureCount_SCB = 999
LOCAL_PARAM_VMINTC_ForwardingMode_EDC = "Input"
LOCAL_PARAM_VMINTC_ForwardingMode_KILL = "InputOutput"
LOCAL_PARAM_VMINTC_PatternNameMap = "1,2,3,4,5,6,7"
LOCAL_PARAM_VMINTC_StartVoltages_NOM = "0.9"
LOCAL_PARAM_VMINTC_TestMode_SCB = "Scoreboard"
LOCAL_PARAM_VMINTC_TestMode_FUNC = "Functional"
LOCAL_PARAM_VMINTC_TestMode_VMIN = "SingleVmin"
LOCAL_PARAM_VMINTC_VoltageTargets = "CCF"
LOCAL_PARAM_NOM_LevelsTc = ""
LOCAL_PARAM_MIN_LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min"
LOCAL_PARAM_MAX_LevelsTc = ""
LOCAL_PARAM_POR_TimingsTc = "CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100"
LOCAL_PARAM_HVM_DOMAIN = "CPU_TRIALS::FlowDomain.CCF"
LOCAL_PARAM_GCD_FAIL_PORT = 30


MODULE = "SCN_UNCORE_CXPKGS9"  # You can change this as needed
VOLTAGE_DOMAIN = "CCF"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'
#VOLTAGE_DOMAIN = "VCCR" # This triggers Q-gate 239 error - ww20.1, so we went with VCCIA for now.



########################################################################
# INITIALIZE
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(4134, 4140), (4234, 4240), (4734, 4740), (94422889, 94422979), (94472889, 94472979),],
	ctrrangeforbins=(2889 , 2979 ),
    defaultthermalbin=[(97412889, 97412979), (97422889, 97422979), (97472889, 97472979), (97942889, 97942979)], #9097HB17
    defaultresetbin=[(41192889, 41192979), (42192889, 42192979), (47192889, 47192979), (94192889, 94192979)], #90HB1917/90HB1918
    defaultrm2bin = [(99412889, 99412979), (99422889, 99422979), (99472889, 99472979), (99942889, 99942979)], 
    defaultrm1bin = [(98412889, 98412979), (98422889, 98422979), (98472889, 98472979), (98942889, 98942979)],
    basenumrange=(13666, 13999),
)

base_lttc_bin = [(94472000,94473999), (97942000, 97943999), (94192000,94193999)]

#Import ("SCN_UNCORE_CXPKGS9.usrv")
########################################################################
# IMPORT REQUIRED FILES
########################################################################

Import(MODULE + ".usrv")
Import(MODULE + "_Timing.tcg")
Import(MODULE + "_Levels.tcg")

#####################
#   SCREENTC TESTS   #
######################################################################################################
    
def get_test_list_screentc(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_screentc = []	
    sample_test_screentc = \
        ScreenTC(name=f"CTRL_X_SCREEN_K_{flow}_X_X_X_X_RESET_GSDS",
               ScreenTestSet = "",
               ScreenTestsFile = "",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = -41, goto="NEXT")))
    test_listt_screentc.append(sample_test_screentc)
    
    return test_listt_screentc

#####################
#   PATCONFIG TESTS   #
######################################################################################################
    
def get_test_list_patconfig(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_patconfig = []	
    sample_test_patconfig = \
        PrimePatConfigTestMethod(name=f"CTRL_X_PATMOD_K_{flow}_X_X_X_X_RESET_FREQUENCY",
               ConfigurationFile = "",
               SetPoint = "",
               SetPointsPlistMode = "Global",
               SetPointsPreInstance = "",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_patconfig.append(sample_test_patconfig)
    
    return test_listt_patconfig
       
########################################################################
# OCC DEFINITION CREATION
########################################################################

def get_test_list_stuckat_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_occ = []	
    sample_test_stuckat_occ = \
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_X_NOM_X_ALL",
               Patlist = "scn_cdie_begin_atpg_edt_classhvm_all_list",
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = "Scoreboard",
               FailCaptureCount=999,
               ForwardingMode = "None",
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CCF"'),
               FivrCondition = 'NOM_CCF',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
			   SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance =  Spec(f'PSPOST.CLR_{corner}'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_REC"),
               r1=pPass(goto="ATSPEED_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_ALL"),
               r2=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_REC"),
               r3=pPass(goto="ATSPEED_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_ALL"),
               r4=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_REC"),
               r5=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_REC")))
    test_listt_stuckat_occ.append(sample_test_stuckat_occ)
    
    return test_listt_stuckat_occ


###########RECOVERY_STUCKAT###############

def get_test_list_stuckat_rec(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_rec = []	
    sample_test_stuckat_rec = \
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_X_NOM_X_REC",
               Patlist = "scn_cdie_begin_atpg_edt_classhvm_all_list",
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = "Scoreboard",
               FailCaptureCount=999,
               ForwardingMode = "None",
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CCF"'),
               FivrCondition = 'NOM_CCF',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
			   SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance =  Spec(f'PSPOST.CLR_{corner}'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="STUCKAT_UNCORE_SHMOO_E_BEGINCPU_X_CR_NOM_X_F1_SHMOODATA"),
               r1=pPass(goto="ATSPEED_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_ALL"),
               r2=pFail(setbin = -42, goto="STUCKAT_UNCORE_SHMOO_E_BEGINCPU_X_CR_NOM_X_F1_SHMOODATA"),
               r3=pPass(goto="ATSPEED_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_ALL"),
               r4=pFail(setbin = -42, goto="STUCKAT_UNCORE_SHMOO_E_BEGINCPU_X_CR_NOM_X_F1_SHMOODATA"),
               r5=pFail(setbin = -42, goto="STUCKAT_UNCORE_SHMOO_E_BEGINCPU_X_CR_NOM_X_F1_SHMOODATA")))
    test_listt_stuckat_rec.append(sample_test_stuckat_rec)
    
    return test_listt_stuckat_rec

def get_test_list_stuckat_vmax_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_vmax_occ = []	
    sample_test_stuckat_vmax_occ = \
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_MAX_X_ALL",
               Patlist = 'scn_cdie_vmaxxccf_atpg_edt_classhvm_list',
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CCF_VMAX_VALUE'),
               EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CCF_VMAX_VALUE'), 
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               ForwardingMode = 'None',
               PinMap = '',
               #RecoveryMode = "NoRecovery",
               #RecoveryOptions = '',
               #RecoveryTrackingIncoming = '',
               #RecoveryTrackingOutgoing = '',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               #ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
              # FailCaptureCount = 999;
               SetPointsPreInstance = Spec(f'PSPRE.CLR_F1+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_F1_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_F1'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", 1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(ret = 1),
               r1=pPass(ret=1),
               r2=pFail(ret = 1),
               r3=pPass(ret=1),
               r4=pFail(ret = 1),
               r5=pFail(ret = 1)))
    test_listt_stuckat_vmax_occ.append(sample_test_stuckat_vmax_occ)
    
    return test_listt_stuckat_vmax_occ

def get_test_list_atspeed_vmax_occ_mtt (
    flow, 
    corner, 
    testinput,
    FlowMatrix
    
    ):
           
    # decode MTT test name
    test_listt_atspeed_vmax_occ_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_vmax_occ_mtt = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_SB_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_MAX_{frequency_value}_F5_F7",
                # ATSPEED_CORE{dcm}_VMIN_K_F1XCR_X_VCCIA_F1_1200_ALLCORE_MTT - this naming convention passed QG_239 (Q-Gate checker)
                # name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{FlowMatrix}_ALLCORE_MTT", this triggers QG_239 error during PR, so we have to sorta manually code in the freq value
                # ATSPEED_CORE_VMIN_K_F1XCR_X_VCCIA_F1_CR_F1_FREQ_ALLCORE_MTT - expected the freq would be autopopulated by flowmatrix but that's not happening yet in ww20.1 
               exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING_TOP",
                template = VminTC(name = f'"ATSPEED_UNCORE_SB_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_MAX_" + ' + Spec(f"__shared__::Corners.CCF_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}"),
                Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                #CornerIdentifiers = TrialParamSpec(f"__shared__::CornerIdentifiers.CCF_C5"),
                DtsConfiguration = Spec(f'SCN_UNCORE_CXPKGS9_Specs.CCF_VMINTC_DtsConfiguration_VMAX'),
                EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE"),
                ExecutionMode = "SearchWithScoreboard",
                LogLevel = 'Disabled',
                SetPointsPlistMode = "Local",
                FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
                FivrCondition = 'NOM_CCF',
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f'__shared__::FlowMatrixSingular.FlowIndex'),
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                MaskPins = '',
                RecoveryMode = 'NoRecovery',
                RecoveryOptions = 'CLASS_NVL_S52C_12C',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                RecoveryTrackingIncoming = 'SLC0_B,SLC0',
                RecoveryTrackingOutgoing = 'SLC0_B,SLC0',
                PinMap = "UNCORE_SCANB,UNCORE_SCAN",
                ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                #SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FreqValues.CCF_C5")+'"GHz"'),
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_F5+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FreqValues.CCF_C5+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CLR_F5'),
                #StartVoltages = '',
                # = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CCF_VMAX_VALUE'),
                StartVoltagesForRetry =TrialParamSpec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
                StartVoltagesOffset = TrialParamSpec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
               # StartVoltagesForRetry= "",
                #StartVoltagesOffset ='',
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --railconfigurations CDIE_CCF_NBLCTRL CDIE1_CCF_NBLCTRL --expressions "' + f' + DROPOUT.CLR_F5'),
                #VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 1, trialaction = "Exit"), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 1, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -47, ret= 1, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 1, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 1),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 1),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -47, ret= 1),
                            r5 = pFail(setbin= -47, ret= 1)))
    test_listt_atspeed_vmax_occ_mtt.append(sample_test_atspeed_vmax_occ_mtt)

    return test_listt_atspeed_vmax_occ_mtt
    
def get_test_list_atspeed_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_occ = []	
    sample_test_atspeed_occ = \
        VminTC(name=f"ATSPEED_UNCORE_SB_K_{flow}_X_X_NOM_X_ALL",
               Patlist = 'scn_cdie_begin_trans_edt_classhvm_list',
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               FailCaptureCount=999,
              # ForwardingMode = "None",
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CCF"'),
               ForwardingMode = 'None',
               #ForwardingMode = "None";
              # FailCaptureCount = 999,
               #PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -47, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -47, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -47, goto="NEXT"),
               r5=pFail(setbin = -47, goto="NEXT")))
    test_listt_atspeed_occ.append(sample_test_atspeed_occ)
    
    return test_listt_atspeed_occ
 
# OCC MTT vmin search/check test
def get_test_list_atspeed_occ_f1f4_mtt (
    flow, 
    corner, 
    testinput,
    FlowMatrix
    
    ):
           
    # decode MTT test name
    test_listt_atspeed_occ_f1f4_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_occ_f1f4_mtt = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}",
                # ATSPEED_CORE{dcm}_VMIN_K_F1XCR_X_VCCIA_F1_1200_ALLCORE_MTT - this naming convention passed QG_239 (Q-Gate checker)
                # name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{FlowMatrix}_ALLCORE_MTT", this triggers QG_239 error during PR, so we have to sorta manually code in the freq value
                # ATSPEED_CORE_VMIN_K_F1XCR_X_VCCIA_F1_CR_F1_FREQ_ALLCORE_MTT - expected the freq would be autopopulated by flowmatrix but that's not happening yet in ww20.1 
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING",
                template = VminTC(name = f'"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") ,
                Patlist = f"scn_cdie_{corner.lower()}xccf_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = Spec(f"__shared__::CornerIdentifiers.CCF_C{i}"),
                DtsConfiguration = Spec(f'SCN_UNCORE_CXPKGS9_Specs.CCF_VMINTC_DtsConfiguration_{corner.upper()}'),
                EndVoltageLimits =  testinput.get("EndVoltageLimits"),
                ExecutionMode = "SearchWithScoreboard",
                LogLevel = 'Disabled',
                SetPointsPlistMode = "Local",
                FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
                FivrCondition = 'NOM_CCF',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f'__shared__::FlowMatrix.FlowIndex'),
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                MaskPins = '',
                RecoveryMode = 'NoRecovery',
                RecoveryOptions = 'CLASS_NVL_S52C_12C',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                RecoveryTrackingIncoming = 'SLC0_B,SLC0',
                RecoveryTrackingOutgoing = 'SLC0_B,SLC0',
                PinMap = "UNCORE_SCANB,UNCORE_SCAN",
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
				FailCaptureCount = Spec("toInteger(999)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
                #StartVoltages = '',
                # = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , "")'),
                StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , "")'),
               #StartVoltagesOffset= "",
               #StartVoltagesForRetry = "",
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --railconfigurations CDIE_CCF_NBLCTRL CDIE1_CCF_NBLCTRL --expressions "' + f' + DROPOUT.CLR_{corner}'),
               # VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 1, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -47, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
            
    test_listt_atspeed_occ_f1f4_mtt.append(sample_test_atspeed_occ_f1f4_mtt)

    return test_listt_atspeed_occ_f1f4_mtt

def get_test_list_atspeed_occ_f5f6_mtt (
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id
    ):
           
    # decode MTT test name
    test_listt_atspeed_occ_f5f6_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_occ_f5f6_mtt = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_{frequency_value}",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING_TOP",
                template = VminTC(name = f'"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_"+ ' + Spec(f"__shared__::Corners.CCF_{corner_id}") + '+ "_" + ' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}") ,
                Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = TrialParamSpec(f"__shared__::CornerIdentifiers.CCF_C5"),
                DtsConfiguration = Spec(f'SCN_UNCORE_CXPKGS9_Specs.CCF_VMINTC_DtsConfiguration_{corner.upper()}'),
                EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                ExecutionMode = "SearchWithScoreboard",
                LogLevel = 'Disabled',
                SetPointsPlistMode = "Local",
                FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
                FivrCondition = 'NOM_CCF',
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f'__shared__::FlowMatrixSingular.FlowIndex'),
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                MaskPins = '',
                RecoveryMode = 'NoRecovery',
                RecoveryOptions = 'CLASS_NVL_S52C_12C',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                RecoveryTrackingIncoming = 'SLC0_B,SLC0',
                RecoveryTrackingOutgoing = 'SLC0_B,SLC0',
                PinMap = "UNCORE_SCANB,UNCORE_SCAN",
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                #SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FreqValues.CCF_C5")+'"GHz"'),
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FreqValues.CCF_C5+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
                #StartVoltages = '',
                # = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = TrialParamSpec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
                StartVoltagesOffset = TrialParamSpec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
               # StartVoltagesForRetry= "",
                #StartVoltagesOffset ='',
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --railconfigurations CDIE_CCF_NBLCTRL CDIE1_CCF_NBLCTRL --expressions "' + f' + DROPOUT.CLR_{corner}'),
                #VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 1, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -47, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
            
    test_listt_atspeed_occ_f5f6_mtt.append(sample_test_atspeed_occ_f5f6_mtt)

    return test_listt_atspeed_occ_f5f6_mtt
    
########################################################################
# IO DEFINITION CREATION
########################################################################
def get_test_list_stuckat(
    flow,
    corner,
    dcm,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat = []	
    sample_test_stuckat = \
        VminTC(name=f"STUCKAT_UNCORE{dcm}_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{corner}",
               Patlist = "scn_cdie_begin_atpg_edt_classhvm_list", 
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE', 
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min', 
               ExecutionMode = 'SearchWithScoreboard',
               FailCaptureCount = Spec("toInteger(999)"),
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               #ForwardingMode = 'Input',
               MaskPins = '',
               PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -42, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, goto="NEXT"),
               r5=pFail(setbin = -42, goto="NEXT")))
    test_listt_stuckat.append(sample_test_stuckat)
    
    return test_listt_stuckat

def get_test_list_stuckat_vmax(
    flow,
    corner,
    dcm,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_vmax = []	
    sample_test_stuckat_vmax = \
        VminTC(name=f"STUCKAT_UNCORE{dcm}_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_MAX_{corner}",
               Patlist = "scn_cdie_begin_atpg_edt_classhvm_list", 
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE', 
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min', 
               ExecutionMode = 'SearchWithScoreboard',
               FailCaptureCount = Spec("toInteger(999)"),
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               #ForwardingMode = 'Input',
               MaskPins = '',
               PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               MaxFailsNum = Spec("toInteger(20)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, ret = 0),
               r1=pPass(goto = "NEXT"),
               r2=pFail(setbin = -42, ret = 0),
               r3=pPass(goto = "NEXT"),
               r4=pFail(setbin = -42, ret = 0),
               r5=pFail(setbin = -42, ret = 0)))
    test_listt_stuckat_vmax.append(sample_test_stuckat_vmax)
    
    return test_listt_stuckat_vmax

def get_test_list_atspeed_vmax(
    flow,
    corner,
    dcm,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_vmax = []	
    sample_test_atspeed_vmax = \
        VminTC(name=f"ATSPEED_UNCORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_MAX_{corner}",
               Patlist = 'scn_cdie_begin_trans_edt_classhvm_list', 
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE', 
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min', 
               ExecutionMode = 'SearchWithScoreboard',
               FailCaptureCount = Spec("toInteger(999)"),
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               #ForwardingMode = 'Input',
               MaskPins = '',
               PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               MaxFailsNum = Spec("toInteger(20)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -47, ret = 0),
               r1=pPass(goto = "NEXT"), 
               r2=pFail(setbin = -47, ret = 0),
               r3=pPass(goto = "NEXT"),
               r4=pFail(setbin = -47, ret = 0),
               r5=pFail(setbin = -47, ret = 0)))
    test_listt_atspeed_vmax.append(sample_test_atspeed_vmax)
    
    return test_listt_atspeed_vmax

def get_test_list_chain(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain = []	
    sample_test_chain = \
        VminTC(name=f"CHAIN_UNCORE_SB_K_{flow}_X_X_NOM_X_ALL",
               Patlist = 'scn_cdie_begin_chain_edt_classhvm_all_list',
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               EndVoltageLimits = '0.9', 
               ExecutionMode = 'SearchWithScoreboard',
               FailCaptureCount = Spec("toInteger(999)"),
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               #ForwardingMode = 'Input',
               MaskPins = '',
               PinMap = '',
              # RecoveryMode = 'NoRecovery',
               #RecoveryOptions = '',
               #RecoveryTrackingIncoming = '',
               #RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               ForwardingMode = "None",
               #RecoveryMode = "Default",
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance =Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
               StartVoltages = '0.9',
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CCF"'),
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(ret=0),
               r1=pPass(goto="STUCKAT_UNCORE_SPOFI_E_BEGINCPU_X_X_NOM_X"),
               r2=pFail(ret=0),
               r3=pPass(ret=0),
               r4=pFail(ret=0),
               r5=pFail(ret=0),))
    test_listt_chain.append(sample_test_chain)
    
    return test_listt_chain


#FMIN FAILFLOW

def get_test_list_atspeed_fmin_failflow(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_fmin_failflow = []	
    sample_test_atspeed_fmin_failflow = \
        VminTC(name=f"ATSPEED_UNCORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_X_{corner}_FF_SEARCH",
               Patlist = f"scn_cdie_{corner.lower()}xccf_trans_edt_classhvm_list_master",
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               #StartVoltages = '0.9',
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"), 
               FailCaptureCount=999,
              # ForwardingMode = "None",
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --railconfigurations CDIE_CCF_NBLCTRL CDIE1_CCF_NBLCTRL --expressions "' + f' + DROPOUT.CLR_{corner}'),
               ForwardingMode = "Input",
               FlowIndex = Spec (f'__shared__::FlowMatrixSingular.FlowIndex'),
               #ForwardingMode = "None";
              # FailCaptureCount = 999,
               #PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = 'CLASS_NVL_S52C_12C',
               RecoveryTrackingIncoming = 'SLC0_B,SLC0',
               RecoveryTrackingOutgoing = 'SLC0_B,SLC0',
               PinMap = "UNCORE_SCANB,UNCORE_SCAN",
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
               PreInstance = '',
               PostInstance = '',
               StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
               StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               VoltagesOffset = "GBVars.VoltageOffset",
               #LimitGuardband = "GBVars.FminLimitGuardband",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -47, ret=0),
               r1=pPass(ret=0),
               r2=pFail(setbin = -47, ret=0),
               r3=pPass(ret=0),
               r4=pFail(setbin = -47, ret=0),
               r5=pFail(setbin = -47, ret=0)))
    test_listt_atspeed_fmin_failflow.append(sample_test_atspeed_fmin_failflow)
    
    return test_listt_atspeed_fmin_failflow
    
# MTT vmin search/check test
def get_test_list_atspeed_f1f4_mtt(
    flow, 
    corner, 
    dcm, 
    testinput,
    FlowMatrix,
    recoverytestflag=False
    ):
      
    # decode MTT test name
    test_listt_atspeed_f1f4_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_f1f4_mtt = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{frequency_value}_ALL_MTT",    
                # ATSPEED_CORE{dcm}_VMIN_K_F1XCR_X_VCCIA_F1_1200_ALLCORE_MTT - this naming convention passed QG_239 (Q-Gate checker)
                # name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{FlowMatrix}_ALLCORE_MTT", this triggers QG_239 error during PR, so we have to sorta manually code in the freq value
                # ATSPEED_CORE_VMIN_K_F1XCR_X_VCCIA_F1_CR_F1_FREQ_ALLCORE_MTT - expected the freq would be autopopulated by flowmatrix but that's not happening yet in ww20.1 
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_ALL"',
                Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f"CCF@{corner}",
                DtsConfiguration = '',
                #EndVoltageLimits = '',
                ExecutionMode = "Search" if "XCCF" in flow else "SearchWithScoreboard",
                LogLevel = 'Disabled',
                SetPointsPlistMode = "Local",
                FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
                FivrCondition = 'NOM_CCF',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = '',
                MaskPins = '',
                PatternNameCounterIndexes = '',
                PinMap = '',
                RecoveryMode = 'NoRecovery', 
                RecoveryOptions = '',
                RecoveryTrackingIncoming = '',
                RecoveryTrackingOutgoing = '',
                #ScoreboardEdgeTicks = Spec("toInteger(0)"),
                #MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
                #StartVoltages = '',
                EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
                StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, goto= "NEXT"),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, goto= "NEXT"),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -47, goto= "NEXT"),
                            r5 = pFail(setbin= -47, goto= "NEXT")))
                             
    test_listt_atspeed_f1f4_mtt.append(sample_test_atspeed_f1f4_mtt)

    return test_listt_atspeed_f1f4_mtt

def get_test_list_atspeed_f1f4_mtt_edc(
    flow, 
    corner, 
    dcm, 
    testinput,
    FlowMatrix,
    recoverytestflag=False
    ):
      
    # decode MTT test name
    test_listt_atspeed_f1f4_mtt_edc = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_f1f4_mtt_edc = \
        NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_E_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{frequency_value}_MTT",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING",
                template =  VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_ALL"',
                Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                ExecutionMode = testinput.get("executionmode", ""),
                LogLevel = 'Disabled',
                SetPointsPlistMode = "Local",
                FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
                FivrCondition = 'NOM_CCF',
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                MaskPins = '',
                PinMap = '',
                RecoveryMode = 'NoRecovery',
                RecoveryOptions = '',
                RecoveryTrackingIncoming = '',
                RecoveryTrackingOutgoing = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f"CCF@F1" if "FMINXCCF" in flow else f"CCF0@{corner}",
                DtsConfiguration = '',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f'__shared__::FlowMatrix.FlowIndex'),
                InitialMaskBits = '',
                LimitGuardband = 'GBVars.LimitGuardband',
                ScoreboardEdgeTicks = Spec("toInteger(0)"),
                MaxFailsNum = Spec("toInteger(20)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                SetPointsPostInstance =Spec(f'PSPOST.CLR_{corner}'),
                StartVoltages = TrialParamSpec(f'__shared__::FlowMatrix.CCF_LOW_SEARCH_VALUE'),
                StepSize = TrialParamSpec(f'toDouble(__shared__::FlowMatrix.CCF_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -42, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(goto= "NEXT"),
                            r1 = pPass(goto= "NEXT"),
                            r2 = pFail(goto= "NEXT"),
                            r3 = pPass(goto= "NEXT"),
                            r4 = pFail(goto= "NEXT"),
                            r5 = pFail(goto= "NEXT")))
                             
    test_listt_atspeed_f1f4_mtt_edc.append(sample_test_atspeed_f1f4_mtt_edc)

    return test_listt_atspeed_f1f4_mtt_edc

def get_test_list_atspeed_f5f6_mtt(
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
      
    # decode MTT test name
    test_listt_atspeed_f5f6_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_f5f6_mtt = \
        NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{frequency_value}_MTT",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING_TOP",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz"),
                Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                ExecutionMode = "Search" if "XCCF" in flow else "SearchWithScoreboard",
                LogLevel = 'Disabled',
                SetPointsPlistMode = "Local",
                FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
                FivrCondition = 'NOM_CCF',
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                MaskPins = '',
                PinMap = '',
                RecoveryMode = 'NoRecovery',
                RecoveryOptions = '',
                RecoveryTrackingIncoming = '',
                RecoveryTrackingOutgoing = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = testinput.get("corneridentifier", f"CCF@{corner}"),
                DtsConfiguration = '',
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f'__shared__::FlowMatrix.FlowIndex'),
                InitialMaskBits = '',
                LimitGuardband = 'GBVars.LimitGuardband',
                ScoreboardEdgeTicks = Spec("toInteger(0)"),
                MaxFailsNum = Spec("toInteger(20)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FreqValue.CLR_{corner}_FREQ+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
                #StartVoltages = Spec(f'__shared__::FlowMatrix.CCF_LOW_SEARCH_VALUE'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrix.CCF_SEARCH_RESOLUTION'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -42, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, goto = "NEXT"),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, goto = "NEXT"),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -42, goto = "NEXT"),
                            r5 = pFail(setbin= -47, goto = "NEXT")))
                             
    test_listt_atspeed_f5f6_mtt.append(sample_test_atspeed_f5f6_mtt)

    return test_listt_atspeed_f5f6_mtt

def get_test_list_atspeed_fmin_mtt(
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):

      # decode MTT test name
    test_listt_atspeed_fmin_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_fmin_mtt = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{frequency_value}_MTT",
                # ATSPEED_CORE{dcm}_VMIN_K_F1XCR_X_VCCIA_F1_1200_ALLCORE_MTT - this naming convention passed QG_239 (Q-Gate checker)
                # name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{FlowMatrix}_ALLCORE_MTT", this triggers QG_239 error during PR, so we have to sorta manually code in the freq value
                # ATSPEED_CORE_VMIN_K_F1XCR_X_VCCIA_F1_CR_F1_FREQ_ALLCORE_MTT - expected the freq would be autopopulated by flowmatrix but that's not happening yet in ww20.1 
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING",
                template = VminTC(name = f'"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") ,
                Patlist = f"scn_cdie_{corner.lower()}xccf_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f"CCF1@F1,CCF0@F1",
                DtsConfiguration = Spec(f'SCN_UNCORE_CXPKGS9_Specs.CCF_VMINTC_DtsConfiguration_{corner.upper()}'),
                EndVoltageLimits =  Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"),
                ExecutionMode = "SearchWithScoreboard",
                LogLevel = 'Disabled',
                SetPointsPlistMode = "Local",
                FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
                FivrCondition = 'NOM_CCF',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f'__shared__::FlowMatrix.FlowIndex'),
                ForwardingMode = "Input",
                InitialMaskBits = '',
                LimitGuardband = "GBVars.FminLimitGuardband",
                MaskPins = '',
                RecoveryMode = 'NoRecovery',
                RecoveryOptions = 'CLASS_NVL_S52C_12C',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                RecoveryTrackingIncoming = 'SLC0_B,SLC0',
                RecoveryTrackingOutgoing = 'SLC0_B,SLC0',
                PinMap = "UNCORE_SCANB,UNCORE_SCAN",
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                FailCaptureCount = Spec("toInteger(999)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
                #StartVoltages = '',
                # = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               #StartVoltagesOffset= "",
               #StartVoltagesForRetry = "",
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --railconfigurations CDIE_CCF_NBLCTRL CDIE1_CCF_NBLCTRL --expressions "' + f' + DROPOUT.CLR_{corner}'),
               # VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 1, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -47, ret= 0, trialaction =Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47,goto = "NEXT"),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, goto = "NEXT"),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -42, goto = "NEXT"),
                            r5 = pFail(setbin= -47,goto = "NEXT")))
            
    test_listt_atspeed_fmin_mtt.append(sample_test_atspeed_fmin_mtt)

    return test_listt_atspeed_fmin_mtt

def get_test_list_atspeed_raw(
    flow,
    corner,
    dcm,
    testinput,
    FlowMatrix
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_raw = []	
    sample_test_atspeed_raw = \
        VminTC(name=f"ATSPEED_UNCORE{dcm}_SB_E_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{corner}_RAW",
               Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master", 
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE', 
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min', 
               ExecutionMode = 'Search',
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               #ForwardingMode = 'Input',
               MaskPins = '',
               PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               MaxFailsNum = Spec("toInteger(20)"),
               CornerIdentifiers = f"CR{dcm}@F1" if "FMINXCCF" in flow else f"CCF0@{corner}",
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", "SingleVmin"),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(ret = 0),
               r1=pPass(ret=0),
               r2=pFail(ret = 0),
               r3=pPass(ret=0),
               r4=pFail(ret = 0),
               r5=pFail(ret = 0)))
    test_listt_atspeed_raw.append(sample_test_atspeed_raw)
    
    return test_listt_atspeed_raw

def get_test_list_atspeed_f5f6_apexmtt(
    flow, 
    corner,  
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
    """
    Generates a list containing a NativeMultiTrial APEX MTT test for ATSPEED CORE VMIN F5/F6 flows.
    """
    test_listt_atspeed_f5f6_apexmtt = []
    # Get the frequency value from FlowMatrixRule
    #frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    sample_test_atspeed_f5f6_apexmtt = ApexTC(
        name=f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_X_X_{corner.upper()}_APEX_MTT",
        #exitaction="Restore",
        #trialvar="CPU_TRIALS::FlowDomain.RING_TOP",
        #template=ApexTC(
           # name=f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::Corners.CCF_C5") + f' + "_APEX_MTT"',
            Patlist=f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
            LevelsTc='SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
            TimingsTc='SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
            InitialMaskBits='',
            ForwardingMode= "None",
            PinMap='',
            RecoveryOptions= '',
            #RecoveryMode = 'NoRecovery',
            RecoveryTracking='',
            End=Spec(f'__shared__::FlowMatrixSingular.APEX_CCF_MIN'),
            Start=Spec(f'__shared__::FlowMatrixSingular.APEX_CCF_MAX'),
            #CornerIdentifiers = TrialParamSpec(f"__shared__::Corners.CCF_C5"),
            SetPointsPreInstance =  Spec(f'PSPRE.CLR_F5+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_F5_FREQ+")+'"GHz," 'f'+' f'"CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
            SetPointsPostInstance= Spec(f'PSPOST.CLR_F5+' f'","+' f'"CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
            FivrCondition= "NOM_CCF",
            FivrConditionPlistParamName="Patlist",
            StepSize = Spec("toInteger(3)"),
            VoltageConverter= Spec(f'" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner} + ' + f'" --overrides CCF:" + __shared__::FlowMatrixSingular.CCF_VMAX_VALUE'),
            ExportTokens= Spec(f'__shared__::APEX_Tokens.CCFToken'),
            PatternNameCounterIndexes = '1,2,3,4,5,6,7',
            #VoltageTargets = testinput.get("Voltagetarget", "CCF"),
            Targets='SCCF1,SCCF',
            DtsConfiguration = Spec(f'SCN_UNCORE_CXPKGS9_Specs.CCF_VMINTC_DtsConfiguration_APEXTC'),
            BypassPort = Spec('__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)'),
        #),
        #r0=pFail(setbin=-47, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
        #r1=pPass(ret=1, trialaction="Next"),
        #r2=pFail(setbin=-47, ret=0, trialaction="Exit"),
        #r3=pPass(ret=1, trialaction="Next"),
        #r4=pFail(setbin=-42, ret=0, trialaction="Exit"),
        #r5=pFail(setbin=-47, ret=0, trialaction="Exit"),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(goto="NEXT"),
            r5=pFail(goto="NEXT")
        )
    )
    test_listt_atspeed_f5f6_apexmtt.append(sample_test_atspeed_f5f6_apexmtt)
    return test_listt_atspeed_f5f6_apexmtt
    
    
#####################
#   SPOFI TESTS IO  #
###################################################################################################### 

#def get_test_list_spofi(
#    flow,
#    corner,
#    testinput,
   

#    ):
    # Create an empty list that will contain the final list of the test
#    test_list_spofi = []

    # Define the test parameters based on the test type
    #test_params = {
     #   "STUCKAT": {
     #       "name": f"STUCKAT_UNCORE_SPOFI_E_{flow}_X_X_NOM_{corner}_",
      #      "patlist": 'scn_cdie_begin_atpg_edt_classhvm_list',
      #      "setbin": -42
      #  },
        #"ATSPEED": {
        #    "name": f"ATSPEED_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_{corner}_M{dcm}",
        #    "patlist": f'scn_cdie_{flow.lower()}_m{dcm}_allatspeed_edt_classhvm_list',
        #    "setbin": -47
        #},
        #"CHAIN": {
        #    "name": f"CHAIN_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_{corner}_M{dcm}",
        #    "patlist": f'scn_cdie_{flow.lower()}_m{dcm}_allchain_1hot_edt_classhvm_list',
        #    "setbin": -41,
        #    "goto": f"DIAG_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_{corner}_M{dcm}"
        #},
        #"DIAG": {
        #    "name": f"DIAG_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_{corner}_M{dcm}",
        #    "patlist": f'scn_cdie_{flow.lower()}_m{dcm}_allchain_proxy_edt_classhvm_list',
        #    "setbin": -41
        #}
#    }

    # Get the parameters for the specified test type
   # params = test_params.get(test_type)

   # if params:
 #       sample_test_spofi = PrimeScanSPOFITestMethod(
 #           name=params["name"],
 #           Patlist=params["patlist"],
 #           TimingsTc='SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
 ##           LevelsTc='CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
 #           PerPatternFailCaptureCount=1000,
 #           TotalFailCaptureCount=5000,
 #           BypassPort=testinput.get("Bypassport", -1),
 #           _fitem=Fitem('SAME',
 #                        edc=testinput.get("ISEDC"),
 #                        r0=pFail(setbin=params["setbin"], goto=params.get("goto", "NEXT")),
 #                        r1=pPass(ret=1),
 ##                        r2=pFail(setbin=params["setbin"], goto=params.get("goto", "NEXT")))
  #      )

#        test_list_spofi.append(sample_test_spofi)

 #   return test_list_spofi


def get_test_list_stuckat_spofi(
    flow, 
    corner, 
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_stuckat_spofi = []
    sample_test_stuckat_spofi = PrimeScanSPOFITestMethod(name = f"STUCKAT_UNCORE_SPOFI_E_{flow}_X_X_NOM_X",
                Patlist ='scn_cdie_begin_vnn_atpg_parfuse_1hotdbg_list',
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                PerPatternFailCaptureCount=5000,
                TotalFailCaptureCount=5000,
               # LogLevel = 'Enable',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(ret=0),
                r1=pPass(ret=0),
                r2=pFail(ret=0)))
               
    test_listt_stuckat_spofi.append(sample_test_stuckat_spofi)
    
    return test_listt_stuckat_spofi


#####################
#   SHMOO TESTS IO   #
######################################################################################################
def get_test_list_stuckat_shmoo(
    flow, 
    corner, 
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_stuckat_shmoo = []
    sample_test_stuckat_shmoo = DDGShmooTC(name = f"STUCKAT_UNCORE_SHMOO_E_{flow}_X_X_NOM_X",
                Patlist ='scn_cdie_begin_atpg_edt_classhvm_list',
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '1.2:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto="NEXT"),
                r1=pPass(goto="NEXT"),
                r2=pFail(goto="NEXT")))
               
    test_listt_stuckat_shmoo.append(sample_test_stuckat_shmoo)
    
    return test_listt_stuckat_shmoo

######################################################################################################
def get_test_list_stuckat_vccr_shmoo(
    flow, 
    corner, 
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_stuckat_vccr_shmoo = []
    sample_test_stuckat_vccr_shmoo = DDGShmooTC(name = f"STUCKAT_UNCORE_SHMOO_VCCR_E_{flow}_X_NOM_X",
                Patlist ='scn_cdie_begin_atpg_edt_classhvm_list',
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '1.2:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-47, goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(setbin=-47, goto="NEXT")))
               
    test_listt_stuckat_vccr_shmoo.append(sample_test_stuckat_vccr_shmoo)
    
    return test_listt_stuckat_vccr_shmoo
    
def get_test_list_atspeed_shmoo(
    flow, 
    corner, 
    testinput
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_atspeed_shmoo = []
    sample_test_atspeed_shmoo = DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{flow}_X_X_NOM_X",
                Patlist = 'scn_cdie_begin_trans_edt_classhvm_list',
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '1.2:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail( goto="NEXT"),
                r1=pPass(goto="NEXT"),
                r2=pFail (goto="NEXT")))
               
    test_listt_atspeed_shmoo.append(sample_test_atspeed_shmoo)
    
    return test_listt_atspeed_shmoo

def get_test_list_atspeed_shmoodata(
    flow,
    subflow,
    corner, 
    testinput
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_atspeed_shmoo = []
    sample_test_atspeed_shmoo = DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{subflow}_X_X_NOM_X_{corner.upper()}_SHMOODATA",
                Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '1.2:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(goto="NEXT")))
               
    test_listt_atspeed_shmoo.append(sample_test_atspeed_shmoo)
    
    return test_listt_atspeed_shmoo

def get_test_list_atspeed_vmax_shmoodata(
    flow,
    subflow,
    corner, 
    testinput
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_atspeed_vmax_shmoo = []
    sample_test_atspeed_vmax_shmoo = DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{subflow}_X_X_NOM_X_{corner.upper()}_VMAXSHMOODATA",
                Patlist = f"scn_cdie_{flow.lower()}_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '1.2:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(goto="NEXT")))
               
    test_listt_atspeed_vmax_shmoo.append(sample_test_atspeed_vmax_shmoo)
    
    return test_listt_atspeed_vmax_shmoo    

def get_test_list_atspeed_fmin_shmoodata(
    flow,
    subflow,
    corner, 
    testinput
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_atspeed_fmin_shmoo = []
    sample_test_atspeed_fmin_shmoo = DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{subflow}_X_X_NOM_X_{corner.upper()}_SHMOODATA",
                Patlist = f"scn_cdie_fminxccf_trans_edt_classhvm_list_master",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'PSPRE.CLR_FMIN+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_FMIN+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '1.2:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(goto="NEXT")))
               
    test_listt_atspeed_fmin_shmoo.append(sample_test_atspeed_fmin_shmoo)
    
    return test_listt_atspeed_fmin_shmoo

def get_test_list_chain_shmoo(
    flow, 
    corner, 
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_chain_shmoo = []
    sample_test_chain_shmoo = DDGShmooTC(name = f"CHAIN_UNCORE_SHMOO_E_{flow}_X_X_NOM_X",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                Patlist ='scn_cdie_begin_chain_edt_classhvm_list',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '.21:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(goto="NEXT")))
               
    test_listt_chain_shmoo.append(sample_test_chain_shmoo)

    return test_listt_chain_shmoo

def get_test_list_chain_vccr_shmoo(
    flow, 
    corner, 
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_chain_vccr_shmoo = []
    sample_test_chain_vccr_shmoo = DDGShmooTC(name = f"CHAIN_UNCORE_SHMOO_VCCR_E_{flow}_X_X_NOM",
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                Patlist ='scn_cdie_begin_chain_edt_classhvm_list',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                VoltageConverter =Spec(f'"--dlvrpins VCCIA --expressions CCF --fivrcondition NOM_CCF"'),
                XAxisParam ='p_all_mts',
                XAxisRange = '600e6:100e6:5',
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                YAxisParam = "CCF1,CCF",
                YAxisRange = '1.2:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-47, goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(setbin=-47, goto="NEXT")))
               
    test_listt_chain_vccr_shmoo.append(sample_test_chain_vccr_shmoo)
    
    return test_listt_chain_vccr_shmoo
    
######################################################################################################
######################################################################################################
# INIT - DIERECOVERY & PATMOD
######################################################################################################
def get_test_globalinit_patmod(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_initconfig = []	
    sample_test_initconfig = \
        PrimePatConfigTestMethod(name=f"CTRL_X_PATMOD_K_{flow}_X_X_X_X_GLOBAL_INIT",
               ConfigurationFile = f"./Modules/{MODULE}/inputfiles/SCN_UNCORE_INIT.setpoints.json",
               SetPoint = "scanuncorepatmod",
               #SetPointsPlistMode = "Global",
               SetPointsPreInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail (ret=1),
               r1=pPass(goto="NEXT")))
    test_listt_initconfig.append(sample_test_initconfig)
    
    return test_listt_initconfig
    
def get_test_pinmap_parse(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_callback = []	
    sample_test_callback = \
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_PINMAP_SCN_PRIME_DIERECOVERY",
               Callback = "LoadPinMapFile",
               Parameters = f"--decoder AnyFailSingleSliceDecoder --file ./Modules/SCN/{MODULE}/inputfiles/DieRecoveryPinMaps_NVL_SCNUNCORE.json",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
               r1=pPass(goto="NEXT")))
    test_listt_callback.append(sample_test_callback)
    
    return test_listt_callback   

def get_test_apextc_init(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_apextc_init = []	
    sample_test_apextc_init = \
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_SCNUNCORE_APEXTC",
               Callback = "ReadFrequencyPatConfigFile",
               Parameters = Spec(MODULEPATH +' + 'f'"./Modules/SCN/{MODULE}/InputFiles/ApexTC_Input_Config.json"'),
               BypassPort = Spec('__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)'),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
               r1=pPass(goto="NEXT")))
    test_listt_apextc_init.append(sample_test_apextc_init)
    
    return test_listt_apextc_init


############LINE_SHMOO##########################

def get_test_list_stuckat_shmoodata_margincheck(
    flow, 
    corner, 
    testinput 
   
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_stuckat_shmoo_margincheck = []
    sample_test_stuckat_shmoo_margincheck = PrimeShmooTestMethod(name = f"STUCKAT_UNCORE_SHMOO_E_{flow}_X_CR_NOM_X_{corner}_SHMOODATA",
                Patlist = f'scn_cdie_begin_atpg_edt_classhvm_all_list',
                LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
                TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
                #ApplyEndSequence = 'DISABLED',
                #ExecutionMode = 'Allpin',
                #SetPointsPlistParamName = "Patlist",
                #SetPointsPreInstance = Spec(f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
                #SetPointsPlistMode = 'Local',
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE"'),
                #PrintFormat = "ShmooHub",
                #PowerDownBetweenPoints = 'DISABLED',
                #PlotMode = 'Normal',
                #XAxisType = "SpecSetVariable",
                XAxisDatalogPrefix = 'Base',
                XAxisParam = 'p_all_mts',
                XAxisParamType = 'TimingTestCondition',
                XAxisRange = '600e6:100e6:5',
                #YAxisType = 'FIVR',
                #YAxisDatalogPrefix = 'Base',
                #YAxisParam = f'CORE{dcm}',
                #YAxisParamType = "UserDefined",
                #YAxisRange = '1.2:-0.1:10',
                #LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto = "CHAIN_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_ALL"),
                r1=pPass(goto = "CHAIN_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_ALL"),
                r2=pFail(goto = "CHAIN_UNCORE_SB_K_BEGINCPU_X_X_NOM_X_ALL")))
               
    test_listt_stuckat_shmoo_margincheck.append(sample_test_stuckat_shmoo_margincheck)
    
    return test_listt_stuckat_shmoo_margincheck
#######################LTTC##########################

def get_test_list_atspeed_lttc(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_lttc = []	
    sample_test_atspeed_lttc = \
        VminTC(name=f"ATSPEED_UNCORE_SB_K_{flow}_X_X_NOM_X_ALL",
               Patlist = 'scn_cdie_lttc_trans_edt_classhvm_list',
               TimingsTc =  'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               FailCaptureCount=999,
              # ForwardingMode = "None",
               VoltageTargets = testinput.get("Voltagetarget", "CCF1,CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = 'NOM_CCF',
               VoltageConverter = Spec(f'"--railconfigurations CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_F1'),
               ForwardingMode = 'Input',
               #ForwardingMode = "None";
              # FailCaptureCount = 999,
               #PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=9447, ret = 0),
               r1=pPass(ret=1),
               r2=pFail(setbin = 9447, ret = 0),
               r3=pPass(ret=1),
               r4=pFail(setbin = 9794, ret = 0),
               r5=pFail(setbin = 9419, ret = 0)))
    test_listt_atspeed_lttc.append(sample_test_atspeed_lttc)
    
    return test_listt_atspeed_lttc


def get_test_list_stuckat_lttc(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_lttc = []	
    sample_test_stuckat_lttc = \
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_X_NOM_X_ALL",
               Patlist = "scn_cdie_lttc_atpg_edt_classhvm_all_list",
               TimingsTc = 'SCN_UNCORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDE',
               LevelsTc = 'SCN_UNCORE_CXPKGS9::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_nom',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget","CCF1,CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = "Scoreboard",
               FailCaptureCount=999,
               ForwardingMode = "Input",
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               VoltageConverter = Spec(f'"--railconfigurations CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_F1'),
               FivrCondition = 'NOM_CCF',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance =  Spec(f'PSPOST.CLR_{corner}'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = 9442, ret = 0),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = 9442, ret = 0),
               r3=pPass(goto="NEXT"),
               r4=pFail(setbin = 9794, ret = 0),
               r5=pFail(setbin = 9419, ret = 0)))
    test_listt_stuckat_lttc.append(sample_test_stuckat_lttc)
    
    return test_listt_stuckat_lttc
    
#################################################################################
#							INIT SUBFLOW
#
#	- INIT flow will have pinmap & dierecovery related tests in 
#
#################################################################################
init_flow = "INIT"

init_patmod_tli = {"Bypassport": 1, "ISEDC": True}
init_patmod = get_test_globalinit_patmod(init_flow, init_patmod_tli)

pinmap_parse_tli = {"Bypassport": -1, "ISEDC": True}
pinmap_parse = get_test_pinmap_parse(init_flow, pinmap_parse_tli)

apextc_init_tli = {"Bypassport": -1, "ISEDC": True}
apextc_init = get_test_apextc_init(init_flow, apextc_init_tli)

#INIT SUBFLOW
INIT_SUBFLOW = Flow(f'{MODULE}_INIT',
                                init_patmod,
                                pinmap_parse,
                                apextc_init
                                
                                
                              )    


#################################################################################
#							BEGINCPU SUBFLOW
#
#	- BEGINCPU flow will test 10% STUCKAT content 
#	- Fail flow will include CHAIN, & SPOFI 
#
#################################################################################

begincpu_flow = "BEGINCPU"
begincpu_corner = "F1"

# OCC COMPOSITE TEST LIST
begincpu_vmintc_stuckat_occ_tli = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_vmintc_stuckat_occ = get_test_list_stuckat_occ(begincpu_flow, begincpu_corner, begincpu_vmintc_stuckat_occ_tli)
begincpu_vmintc_chain_occ_tli = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_vmintc_chain_occ = get_test_list_chain(begincpu_flow, begincpu_corner, begincpu_vmintc_chain_occ_tli)
begincpu_vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC":False}
begincpu_vmintc_atspeed_occ = get_test_list_atspeed_occ(begincpu_flow, begincpu_corner, begincpu_vmintc_atspeed_occ_tli)

begincpu_vmintc_stuckat_rec_tli = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": False}
begincpu_vmintc_stuckat_rec = get_test_list_stuckat_rec(begincpu_flow, begincpu_corner, begincpu_vmintc_stuckat_rec_tli)

begincpu_shmoo_stuckat_rec_tli =  {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_shmoo_stuckat_rec = get_test_list_stuckat_shmoodata_margincheck(begincpu_flow,begincpu_corner, begincpu_shmoo_stuckat_rec_tli)
begincpu_spofi_stuckat_tli = {"Bypassport": -1, "ISEDC": True}
begincpu_spofi_stuckat = get_test_list_stuckat_spofi(begincpu_flow, begincpu_corner, begincpu_spofi_stuckat_tli,)
begincpu_occ = Flow("BEGINCPU_UNCORE", begincpu_vmintc_stuckat_occ,begincpu_vmintc_stuckat_rec,begincpu_shmoo_stuckat_rec, begincpu_vmintc_atspeed_occ,begincpu_vmintc_chain_occ,begincpu_spofi_stuckat)

# ScreenTC
begincpu_screentc_tli = {"Bypassport": 1, "ISEDC": True}
begincpu_screentc = get_test_list_screentc(begincpu_flow, begincpu_screentc_tli)

# Patconfig
#begincpu_patconfig_tli = {"Bypassport": 1, "ISEDC": True}
#begincpu_patconfig = get_test_list_patconfig(begincpu_flow, begincpu_patconfig_tli)

#SHMOO
begincpu_shmoo_stuckat_tli =  {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_shmoo_stuckat = get_test_list_stuckat_shmoo(begincpu_flow,begincpu_corner, begincpu_shmoo_stuckat_tli)
begincpu_shmoo_stuckat_vccr_tli =  {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_shmoo_stuckat_vccr = get_test_list_stuckat_vccr_shmoo(begincpu_flow,begincpu_corner, begincpu_shmoo_stuckat_vccr_tli)
begincpu_shmoo_atspeed_tli =  {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_shmoo_atspeed = get_test_list_atspeed_shmoo(begincpu_flow,begincpu_corner, begincpu_shmoo_atspeed_tli)
begincpu_shmoo_chain_tli =  {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_shmoo_chain = get_test_list_chain_shmoo(begincpu_flow,begincpu_corner, begincpu_shmoo_chain_tli)
begincpu_shmoo_chain_vccr_tli =  {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_shmoo_chain_vccr = get_test_list_chain_vccr_shmoo(begincpu_flow,begincpu_corner, begincpu_shmoo_chain_tli)
#begincpu_shmoo_occ = Flow("BEGINCPU_SHMOO", begincpu_shmoo_stuckat,begincpu_shmoo_atspeed,begincpu_shmoo_chain)

#SPOFI


#begincpu_spofi_occ = Flow("BEGINCPU_UNCORE_SPOFI", begincpu_spofi_stuckat)


# Function to create test lists and flows for each module
def create_module_flow(module_index, module_name):
   # Define TLI settings for each module
    vmintc_stuckat_chain_tli = {
        "Bypassport": -1,
        "Testmode": "Scoreboard",
        "Voltagetarget": voltage_targets[module_name],
        "ISEDC": False,
        "Preinstance": ""
    }
    
    vmintc_stuckat = get_test_list_stuckat(begincpu_flow, begincpu_corner, module_index, vmintc_stuckat_chain_tli)

    vmintc_chain = get_test_list_chain(begincpu_flow, begincpu_corner, module_index, vmintc_stuckat_chain_tli)
    
   # spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True}
   # spofi_stuckat = get_test_list_spofi(begincpu_flow, begincpu_corner, module_index, spofi_stuckat_tli, "STUCKAT")
    
    return Flow(f"BEGINCPU_{module_name}", vmintc_stuckat,  vmintc_chain, spofi_stuckat)

    #F1
f1xccf_flow = "F1XCCF"
subflow = "BEGINCPU"
f1xccf_corner = "F1"
SHMOO_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_f1 = [
   get_test_list_atspeed_shmoodata(f1xccf_flow,subflow, f1xccf_corner, SHMOO_ATSPEED_TLI)

]
#STUCKAT_CHAIN_ATSPEED_F1 = Flow("F1_SHMOO", begincpu_shmoo_chain_vccr, begincpu_shmoo_stuckat_vccr,)
ATSPEED_F1 = Flow("F1_SHMOO", *atspeed_shmoo_f1)

#F2
f2xccf_flow = "F2XCCF"
subflow = "BEGINCPU"
f2xccf_corner = "F2"
SHMOO_F2_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_f2 = [
   get_test_list_atspeed_shmoodata(f2xccf_flow,subflow, f2xccf_corner,SHMOO_F2_ATSPEED_TLI)

]

ATSPEED_F2 = Flow("F2_SHMOO", *atspeed_shmoo_f2)

#F3
f3xccf_flow = "F3XCCF"
subflow = "BEGINCPU"
f3xccf_corner = "F3"
SHMOO_F3_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_f3 = [
   get_test_list_atspeed_shmoodata(f3xccf_flow,subflow, f3xccf_corner,SHMOO_F3_ATSPEED_TLI)

]

ATSPEED_F3 = Flow("F3_SHMOO", *atspeed_shmoo_f3)

#F4
f4xccf_flow = "F4XCCF"
subflow = "BEGINCPU"
f4xccf_corner = "F4"
SHMOO_F4_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_f4 = [
   get_test_list_atspeed_shmoodata(f4xccf_flow,subflow, f4xccf_corner,SHMOO_F4_ATSPEED_TLI)

]

ATSPEED_F4 = Flow("F4_SHMOO", *atspeed_shmoo_f4)

#F5
f5xccf_flow = "F5XCCF"
subflow = "BEGINCPU"
f5xccf_corner = "F5"
SHMOO_F5_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_f5 = [
   get_test_list_atspeed_shmoodata(f5xccf_flow,subflow, f5xccf_corner,SHMOO_F5_ATSPEED_TLI)

]

ATSPEED_F5 = Flow("F5_SHMOO", *atspeed_shmoo_f5)

#F6
f6xccf_flow = "F5XCCF"
subflow = "BEGINCPU"
f6xccf_corner = "F6"
SHMOO_F6_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_f6 = [
   get_test_list_atspeed_shmoodata(f6xccf_flow,subflow, f6xccf_corner,SHMOO_F6_ATSPEED_TLI)

]

ATSPEED_F6 = Flow("F6_SHMOO", *atspeed_shmoo_f6)

#F7
f7xccf_flow = "F5XCCF"
subflow = "BEGINCPU"
f7xccf_corner = "F7"
SHMOO_F7_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_f7 = [
   get_test_list_atspeed_shmoodata(f7xccf_flow,subflow, f7xccf_corner,SHMOO_F7_ATSPEED_TLI)

]

ATSPEED_F7 = Flow("F7_SHMOO", *atspeed_shmoo_f7)

#FMIN
fminxccf_flow = "FMINXCCF"
subflow = "BEGINCPU"
fminxccf_corner = "FMIN"
SHMOO_FMIN_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_fmin = [
   get_test_list_atspeed_fmin_shmoodata(fminxccf_flow,subflow, fminxccf_corner,SHMOO_FMIN_ATSPEED_TLI)

]

ATSPEED_FMIN = Flow("FMIN_SHMOO", *atspeed_shmoo_fmin)

#VMAX
vmaxxccf_flow = "VMAXXCCF"
subflow = "BEGINCPU"
vmaxxccf_corner = "F5"
SHMOO_VMAX_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
atspeed_shmoo_vmax = [
   get_test_list_atspeed_vmax_shmoodata(vmaxxccf_flow,subflow, vmaxxccf_corner,SHMOO_VMAX_ATSPEED_TLI)

]

ATSPEED_VMAX = Flow("VMAX_SHMOO", *atspeed_shmoo_vmax)


 #BEGINCPU SUBFLOW
#BEGINCPU_SUBFLOW = Flow(f'{MODULE}_BEGINCPU',
                    #Fitem("SAME", begincpu_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                   # begincpu_screentc,
                    #begincpu_patconfig,
                  # Fitem("SAME", begincpu_shmoo_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT"))
                  # )

SHMOO_COMPOSITE = Flow("SHMOO", 
                         #Fitem("SAME", STUCKAT_CHAIN_ATSPEED_F1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_F1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_F2, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_F3, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_F4, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_F5, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_F6, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_F7, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_FMIN, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                           Fitem("SAME", ATSPEED_VMAX, r0=pFail(ret=0), r1=pPass(goto="NEXT")))
  
##SPOFI_COMPOSITE = Flow("SPOFI_COMPOSITE",Fitem("SAME", begincpu_spofi_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")))


# BEGINCPU SUBFLOW
BEGINCPU_SUBFLOW = Flow(f'{MODULE}_BEGINCPU',
                     Fitem("SAME", begincpu_occ, r0=pFail(ret=0), r1=pPass(ret=1)),
                     #begincpu_screentc,
                     #Fitem("SAME", begincpu_patconfig[-1], r0=pFail(ret=0), r1=pPass(ret=1)),
                     #Fitem("SAME", begincpu_shmoo_occ, r0=pFail(ret=0), r1=pPass(ret=1)),
                     Fitem("SAME", SHMOO_COMPOSITE, r0=pFail(ret=0), r1=pPass(ret=0)),
                     #Fitem("SAME", begincpu_spofi_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT"))
                     )
                    





#################################################################################
#                           FMINXCF SUBFLOW
#
#  -Fmin test point using F1 vmin as test point 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "FMIN": "CCF_FMIN"
    }

corner_id_definitions = {
    "FMIN": "CCF_FMIN",
}


# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        "executionmode": "SearchWithScoreboard",
        "Voltagetarget": voltage_targets[module_name],
        "ISEDC": True,
        "Recovery": "RecoveryPort",
        "Preinstance": "",
        "EndVoltageLimits": Spec(f"__shared__::FlowMatrixSingular.CCF_{corner}_VMIN_RAIN_KILL")
    }
    

    
# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_fmin_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix, corner_id)
    vmintc_atspeed_failflow_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": True}
    vmintc_atspeed_failflow = get_test_list_atspeed_fmin_failflow(flow_name, corner, vmintc_atspeed_occ_tli)
    occ = Flow(f"{flow_name}", vmintc_atspeed_occ,vmintc_atspeed_failflow)
    
                    
    # Create flows for each module
#    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix) for i, module in enumerate(DCM_MODULES)]
    


    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                   #Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1))
                   )
    
    return subflow

# Define the subflows
subflows = []
flow_name = "FMINXCCF"
corner = "FMIN"
flow_matrix = flow_matrix_definitions[corner]
corner_id = corner_id_definitions[corner]
subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix))

                     
#################################################################################
#                           F1F4 X CCF SUBFLOW
#
#   - Consists of F1 through F4 corners flow which will test 100% ATSPEED content 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2400",
    "CCF_F4_FREQ_MHz": "3500"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "CCF_F1_FREQ",
    "F2": "CCF_F2_FREQ",
    "F3": "CCF_F3_FREQ",
    "F4": "CCF_F4_FREQ"
}

#end_voltage_limit= {
#    "F1": Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"),
#    "F2": Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
#    "F3": Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
#    "F4": Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE")}

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix):
    # Define TLI settings for each module
     vmintc_atspeed_tli = {
        "Bypassport": -1,
        "Testmode": "SingleVmin",
        "executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        #"initialmaskbit": initial_maskbit[module_name],
        "ISEDC": False,
        "Recovery": "NoRecovery",
        "Preinstance": ""
    }
    
    
   # vmintc_atspeed_edc = get_test_list_atspeed_f1f4_mtt_edc(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix)
    #vmintc_atspeed = get_test_list_atspeed_f1f4_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix)
    
    #raw vmintc
    #vmintc_atspeed_raw_tli = {"ISEDC": True}
    #vmintc_atspeed_raw = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    #shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    #shmoo_atspeed = get_test_list_atspeed_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all. 
    
    #spofi_atspeed_tli = {"Bypassport": -1, "ISEDC": True} 
    #spofi_atspeed = get_test_list_spofi(flow_name, corner, module_index, spofi_atspeed_tli, "ATSPEED")  

    #spofi_stuckat_tli = {"Bypassport": -1, "ISEDC": True} 
    #spofi_stuckat = get_test_list_spofi(flow_name, corner, module_index, spofi_stuckat_tli, "STUCKAT") 
	
    #return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, shmoo_atspeed, spofi_atspeed, spofi_stuckat)
    #return Flow(f"{flow_name}_{module_name}", vmintc_atspeed_edc, vmintc_atspeed, vmintc_atspeed_raw)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix):
    
    # OCC COMPOSITE TEST LIST
   # vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "SingleVmin", "ISEDC": False, }
    #vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    #shmoo_atspeed_occ_tli = {"Bypassport": 1, "ISEDC": True}
    #shmoo_atspeed_occ = get_test_list_atspeed_f1f4_shmoo(flow_name, corner,shmoo_atspeed_tli,flow_matrix)
    #occ = Flow(f"{flow_name}", vmintc_atspeed_occ)
                    
    # Create flows for each module
#    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix) for i, module in enumerate(DCM_MODULES)]

    # Create the subflow
   # subflow = Flow(f'{module_name}_{flow_name}',
    #               Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")))
                  
#                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
 #                  Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)))
    
    return subflow

# Define the subflows
subflows = []
for i in range(1, 5):
    flow_name = f"F{i}XCCF"
    corner = f"F{i}"
    flow_matrix = flow_matrix_definitions[corner]
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    # Set EndVoltageLimits distinctively for F1
    if corner == "F1":
        vmintc_atspeed_occ_tli["EndVoltageLimits"] = Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL")
    else:
        vmintc_atspeed_occ_tli["EndVoltageLimits"] = Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE")
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(
        flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix
    )
    occ = Flow(f"{flow_name}", vmintc_atspeed_occ)
    subflow = Flow(f'{MODULE}_{flow_name}',
                   Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")))
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix))



    
 
#################################################################################
#                           F4XCCFLO SUBFLOW
#
#   - Consists of F5 & F6 corners flow which will test 100% ATSPEED content in TOP subflow 
#
#################################################################################
# FlowMatrixRule Definition
FlowMatrixRule = {
    "CCF_F4_FREQ_MHz": "3500"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F4": "CCF_F4_FREQ"
    }



# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        "executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        #"initialmaskbit": initial_maskbit[module_name],
        "ISEDC": False,
        "Recovery": "NoRecovery",
        "Preinstance": ""
    }
    
    vmintc_atspeed = get_test_list_atspeed_f1f4_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix)
    
    #raw vmintc
    vmintc_atspeed_raw_tli = {"ISEDC": True}
    vmintc_atspeed_raw = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, vmintc_atspeed_raw)

    
# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    occ = Flow(f"{flow_name}", vmintc_atspeed_occ)
    
                    
    # Create flows for each module
 #   module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix) for i, module in enumerate(DCM_MODULES)]
    


    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")))
                  
                   #*[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   #Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)))
    
    return subflow

# Define the subflows
subflows = []
flow_name = "F4XCCFLO"
corner = "F4"
flow_matrix = flow_matrix_definitions[corner]
subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix))

#################################################################################
#                           F5F6 X CCF SUBFLOW
#
#   - Consists of F5 & F6 corners flow which will test 100% ATSPEED content in TOP subflow 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CCF_F5_FREQ_MHz": "3600",
    "CCF_F6_FREQ_MHz": "4000",
    "CCF_F7_FREQ_MHz": "4300"
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CCF_F5_FREQ",
    "F6": "CCF_F6_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
    "F6": "C6",
}

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": -1,
        "Testmode": "SingleVmin",
        "executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        #"initialmaskbit": initial_maskbit[module_name],
        "ISEDC": False,
        "Recovery": "NoRecovery",
        "Preinstance": ""
    }
    
    vmintc_atspeed_tli = {"ISEDC": True}
    vmintc_atspeed = get_test_list_atspeed_f5f6_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id)
    #raw vmintc
    vmintc_atspeed_raw_tli = {"ISEDC": True}
    vmintc_atspeed_raw = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    apextc_tli = {"Bypassport": 1, "ISEDC": True}
    apextc = get_test_list_atspeed_f5f6_apexmtt(flow_name, corner, module_index, apextc_tli, flow_matrix, corner_id)
    
    shmoo_atspeed_tli = {"Bypassport": -1, "ISEDC": True}
    shmoo_atspeed = get_test_list_atspeed_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
    
    spofi_atspeed_tli = {"Bypassport": -1, "ISEDC": True} 
    spofi_atspeed = get_test_list_spofi(flow_name, corner, module_index, spofi_atspeed_tli, "ATSPEED")                                                                                                

    spofi_stuckat_tli = {"Bypassport": -1, "ISEDC": True} 
    spofi_stuckat = get_test_list_spofi(flow_name, corner, module_index, spofi_stuckat_tli, "STUCKAT")                                                                                               
	
	#return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, shmoo_atspeed, spofi_atspeed, spofi_stuckat)
    return Flow(f"{flow_name}_{module_name}", apextc, vmintc_atspeed, vmintc_atspeed_raw)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f5f6_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix, corner_id)
    apextc_occ_tli = {"Bypassport": 1, "ISEDC": True}
    apextc_occ = get_test_list_atspeed_f5f6_apexmtt(flow_name, corner, apextc_occ_tli, flow_matrix, corner_id)
    occ = Flow(f"{flow_name}",apextc_occ, vmintc_atspeed_occ)
                    
    # Create flows for each module
#    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(DCM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")))
                  
#                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   #Fitem("SAME", module_flows[-1], r0=pFail(ret=0), ))
    
    return subflow

# Define the subflows for F5 and F6, only F5 enabled for now
subflows = []
for corner in ["F5"]:
    flow_name = f"{corner}XCCF"
    flow_matrix = flow_matrix_definitions[corner]
    corner_id = corner_id_definitions[corner]
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id))
    
#################################################################################
#                           F5XCCFLO SUBFLOW
#
#   - Consists of F5 & F6 corners flow which will test 100% ATSPEED content in TOP subflow 
#
#################################################################################
# FlowMatrixRule Definition
FlowMatrixRule = {
    "CCF_F5_FREQ_MHz": "3600",
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CCF_F5_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
}

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": -1,
        "Testmode": "SingleVmin",
        "executionmode": "Search",
        "Voltagetarget": voltage_targets[module_name],
        #"initialmaskbit": initial_maskbit[module_name],
        "ISEDC": False,
        "Recovery": "NoRecovery",
        "Preinstance": ""
    }
    
    vmintc_atspeed = get_test_list_atspeed_f5f6_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id)
    #raw vmintc
    vmintc_atspeed_raw_tli = {"ISEDC": True}
    vmintc_atspeed_raw = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    apextc_tli = {"Bypassport": -1, "ISEDC": True}
    apextc = get_test_list_atspeed_f5f6_apexmtt(flow_name, corner, apextc_tli, flow_matrix, corner_id)
    
    shmoo_atspeed_tli = {"Bypassport": -1, "ISEDC": True}
    shmoo_atspeed = get_test_list_atspeed_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
    
    spofi_atspeed_tli = {"Bypassport": -1, "ISEDC": True} 
    spofi_atspeed = get_test_list_spofi(flow_name, corner, module_index, spofi_atspeed_tli, "ATSPEED")                                                                                                

    spofi_stuckat_tli = {"Bypassport": -1, "ISEDC": True} 
    spofi_stuckat = get_test_list_spofi(flow_name, corner, module_index, spofi_stuckat_tli, "STUCKAT")                                                                                               
	
	#return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, shmoo_atspeed, spofi_atspeed, spofi_stuckat)
   # return Flow(f"{flow_name}_{module_name}", apextc, vmintc_atspeed, vmintc_atspeed_raw)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f5f6_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix, corner_id)
    apextc_occ_tli = {"Bypassport": -1, "ISEDC": True}
    apextc_occ = get_test_list_atspeed_f5f6_apexmtt(flow_name, corner, apextc_occ_tli, flow_matrix, corner_id)
    occ = Flow(f"{flow_name}_UNCORE", vmintc_atspeed_occ)
                    
    # Create flows for each module
#    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(DCM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")))
                  
 #                  *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   #Fitem("SAME", module_flows[-1], r0=pFail(ret=0), ))
    
    return subflow

# Define the subflows for F5 and F6, only F5 enabled for now
subflows = []
for corner in ["F5"]:
    flow_name = f"{corner}XCCFLO"
    flow_matrix = flow_matrix_definitions[corner]
    corner_id = corner_id_definitions[corner]
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id))

#################################################################################
#							VMAXXCCF SUBFLOW
#
#	- ENDCPU flow will test ATSPEED & STUCKAT content 
#	- No Fail flow 
#
#################################################################################
vmaxxccf_flow = "VMAXXCCF"
stuckat_vmaxxccf_corner = "FMAX"
atspeed_vmaxxccf_corner = "FMAX"
PRE_POST_corner = "FMAX"

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CCF_F5_FREQ_MHz": "3600",
    "CCF_F6_FREQ_MHz": "4000",
    "CCF_F7_FREQ_MHz": "4300"
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CCF_F5_FREQ",
    "F6": "CCF_F6_FREQ",
}

corner_id_definitions = {
    "TFM": "C5",
    "F6": "C6",
}

#STUCKAT_F1 test list
vmaxxccf_vmintc_stuckat_occ_tli = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
vmaxxccf_vmintc_stuckat_occ = get_test_list_stuckat_vmax_occ(vmaxxccf_flow, stuckat_vmaxxccf_corner, vmaxxccf_vmintc_stuckat_occ_tli)


vmaxxccf_f1 = Flow("VMAXXCCF_F1",vmaxxccf_vmintc_stuckat_occ)


#ATSPEED_F5 test list
vmaxxccf_vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": True}
vmaxxccf_vmintc_atspeed_occ = get_test_list_atspeed_vmax_occ_mtt(vmaxxccf_flow, atspeed_vmaxxccf_corner, vmaxxccf_vmintc_atspeed_occ_tli,flow_matrix)
apextc_occ_tli = {"Bypassport": -1, "ISEDC": True}
apextc_occ = get_test_list_atspeed_f5f6_apexmtt(vmaxxccf_flow, atspeed_vmaxxccf_corner, apextc_occ_tli, flow_matrix, corner_id= "VMAX")


vmaxxccf_f5 = Flow("VMAXXCCF_F5",vmaxxccf_vmintc_atspeed_occ)


# VMAXXCCF SUBFLOW
VMAXXCCF_SUBFLOW = Flow(f'{MODULE}_VMAXXCCF',
                     Fitem("SAME", vmaxxccf_f1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     Fitem("SAME", vmaxxccf_f5, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     )

#################################################################################
#							VMAXXCCFLO SUBFLOW
#
#	- ENDCPU flow will test ATSPEED & STUCKAT content 
#	- No Fail flow 
#
#################################################################################
vmaxxccflo_flow = "VMAXXCCFLO"
stuckat_vmaxxccf_corner = "VMAX_VALUE"
atspeed_vmaxxccf_corner = "VMAX_VALUE"
PRE_POST_corner = "FMAX"

FlowMatrixRule = {
    "CCF_F5_FREQ_MHz": "3600",
    "CCF_F6_FREQ_MHz": "4000",
    "CCF_F7_FREQ_MHz": "4300"
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CCF_F5_FREQ",
    "F6": "CCF_F6_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
    "F6": "C6",
}
#STUCKAT_F1 test list
vmaxxccf_vmintc_stuckat_occ_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
vmaxxccf_vmintc_stuckat_occ = get_test_list_stuckat_vmax_occ(vmaxxccflo_flow, stuckat_vmaxxccf_corner, vmaxxccf_vmintc_stuckat_occ_tli)


vmaxxccflo_f1 = Flow("VMAXXRLO_F1",vmaxxccf_vmintc_stuckat_occ)


#ATSPEED_F5 test list
vmaxxccf_vmintc_atspeed_occ_tli = {"Bypassport": 1, "Testmode": "MultiVmin", "ISEDC": True}
vmaxxccf_vmintc_atspeed_occ = get_test_list_atspeed_vmax_occ_mtt(vmaxxccflo_flow, atspeed_vmaxxccf_corner, vmaxxccf_vmintc_atspeed_occ_tli,flow_matrix)


vmaxxccflo_f5 = Flow("VMAXXCCFLO_F5", vmaxxccf_vmintc_atspeed_occ)



# VMAXXCCF SUBFLOW
VMAXXCCFLO_SUBFLOW = Flow(f'{MODULE}_VMAXXCCFLO',
                     Fitem("SAME", vmaxxccflo_f1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     Fitem("SAME", vmaxxccflo_f5, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     )

#################################################################################
#							ENDCPU SUBFLOW
#
#	- ENDCPU flow will test ATSPEED & STUCKAT content 
#	- No Fail flow 
#
#################################################################################
#################################################################################
#							LTTCCPU SUBFLOW
#
#	- LTTCCPU flow will test  STUCKAT content 
#	- No Fail flow 
#
#################################################################################


lttccpu_flow = "LTTCCPU"
lttccpu_corner = "F1"

# OCC COMPOSITE TEST LIST

lttccpu_vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC":False}
lttccpu_vmintc_atspeed_occ = get_test_list_atspeed_lttc(lttccpu_flow, lttccpu_corner, lttccpu_vmintc_atspeed_occ_tli)

lttccpu_vmintc_stuckat_occ_tli = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC":False}
lttccpu_vmintc_stuckat_occ = get_test_list_stuckat_lttc(lttccpu_flow, lttccpu_corner, lttccpu_vmintc_stuckat_occ_tli)

lttccpu_occ = Flow("LTTCCPU_UNCORE",lttccpu_vmintc_stuckat_occ,lttccpu_vmintc_atspeed_occ)

LTTCCPU_SUBFLOW = Flow(f'{MODULE}_LTTCCPU',
                     Fitem("SAME", lttccpu_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     
                     )
