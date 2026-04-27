#from turtle import pos
from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig

########################################################################
# ww05'2025 - SORT basic skeleton tryout
# ww13'2025 - CLASS tests, subflows details adjustment to fit class requirement
# ww19'2025 - Added in stuckat for BEGINCPU, mtt atspeed for FI-F4 XCR subflows, all tests in bypassed mode for now.
# ww20'2025 - F5 is added in F5XCRLO (need to check if it really is correct, F5XCR triggers QG-239) 
# ww21'2025 - added speedflow for SCN_UNCORE

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
LOCAL_PARAM_VMINTC_VoltageTargets = "VCCCORE_HC"
LOCAL_PARAM_NOM_LevelsTc = ""
LOCAL_PARAM_MIN_LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min"
LOCAL_PARAM_MAX_LevelsTc = ""
LOCAL_PARAM_POR_TimingsTc = "CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100"
LOCAL_PARAM_HVM_DOMAIN = "CPU_TRIALS::FlowDomain.CORE"
LOCAL_PARAM_GCD_FAIL_PORT = 30

# Define DCM_MODULES based on MODULE #
MODULE = "SCN_UNCORE_CX816"  # You can change this as needed
VOLTAGE_DOMAIN = "VCCIA"
#VOLTAGE_DOMAIN = "VCCR" # This triggers Q-gate 239 error - ww20.1, so we went with VCCIA for now. 


########################################################################
# INITIALIZE
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(4134, 4140), (4234, 4240), (4734, 4740)],
    defaultthermalbin=(90974134, 90974234, 90974734), #9097HB17
    defaultresetbin=(90471934, 90421934, 90411934), #90HB1917/90HB1918
    basenumrange=(3666, 3999),
    #basenumrange = [(23000, 23999), (28000, 28999)]
    #                ^^^ HVM ^^^^^   ^^^^^ EDC ^^^^
)

########################################################################
# IMPORT REQUIRED FILES
########################################################################

#Import(MODULE + ".usrv")
#Import(MODULE + "_Timing.tcg")

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
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{corner}_ALL",
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_stuckat_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0,HC06_03_0P85_VCCCORE1,HC07_03_0P85_VCCCORE2,HC08_03_0P85_VCCCORE3"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               FeatureSwitchSettings = 'disable_masked_targets',
               ForwardingMode = 'Input',
               PinMap = '',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = '',
               SetPointsPostInstance = '',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -42, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, goto="NEXT"),
               r5=pFail(setbin = -42, goto="NEXT")))
    test_listt_stuckat_occ.append(sample_test_stuckat_occ)
    
    return test_listt_stuckat_occ
 
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
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{frequency_value}_ALL_MTT",
                # ATSPEED_UNCORE_VMIN_K_F1XCR_X_VCCIA_F1_1200_ALL_MTT - this naming convention passed QG_239 (Q-Gate checker)
                # name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{FlowMatrix}_ALL_MTT", this triggers QG_239 error during PR, so we have to sorta manually code in the freq value
                # ATSPEED_UNCORE_VMIN_K_F1XCR_X_VCCIA_F1_CR_F1_FREQ_ALL_MTT - expected the freq would be autopopulated by flowmatrix but that's not happening yet in ww20.1 
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_ALL"',
                Patlist = f"scn_cdie_{flow.lower()}_allpar_occ_atspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                #LogLevel = '',
                BaseNumbers = "13018",
                CornerIdentifiers = f"CR@{corner}",
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
                FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = '',
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
                SetPointsPreInstance = Spec(f'"MaaaCdrv:corefreq:"+'+Spec(f"__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MaaaCdrv:ringfreq:"+'+Spec(f"__shared__::FlowMatrixSingular.CR_{corner}_FREQ")+f'+"GHz,MCscnCORE:ratio_modify:"+'+Spec(f"__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
                SetPointsPostInstance = '',
                StartVoltages = '',
                #EndVoltageLimits = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0,HC06_03_0P85_VCCCORE1,HC07_03_0P85_VCCCORE2,HC08_03_0P85_VCCCORE3"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -42, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -42, ret= 0),
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
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{frequency_value}_ALL_MTT",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + f' + "_ALL"',
                Patlist = f"scn_cdie_{flow.lower()}_allpar_occ_atspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                #LogLevel = '',
                BaseNumbers = "13018",
                #CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")), # This is a placeholder for the corner identifiers. We will use the TrialParamSpec to define this.
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
                FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = '',
                FlowIndexCallbackName = '',
                #FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixManual.FlowIndex"),
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
                SetPointsPreInstance = TrialParamSpec(f'"MaaaCdrv:corefreq:"+'+Spec(f"__shared__::FreqValues.CR_{corner_id}+")+'"GHz,MaaaCdrv:ringfreq:"+'+Spec(f"__shared__::FreqValues.CR_{corner_id}")+f'+"GHz,MCscnCORE:ratio_modify:"+'+Spec(f"__shared__::FreqValues.CR_{corner_id}+")+'"GHz"'),
                SetPointsPostInstance = '',
                StartVoltages = '',
                #EndVoltageLimits = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0,HC06_03_0P85_VCCCORE1,HC07_03_0P85_VCCCORE2,HC08_03_0P85_VCCCORE3"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -42, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -42, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
            
    test_listt_atspeed_occ_f5f6_mtt.append(sample_test_atspeed_occ_f5f6_mtt)

    return test_listt_atspeed_occ_f5f6_mtt
    
########################################################################
# IO DEFINITION CREATION
########################################################################
def get_test_list_stuckat(
    flow,
    corner,
    
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat = []	
    sample_test_stuckat = \
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{corner}",
               Patlist = f'scn_cdie_{flow.lower()}_allstuckat_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               FeatureSwitchSettings = 'disable_masked_targets',
               ForwardingMode = 'Input',
               PinMap = 'CORE3_SCAN,CORE2_SCAN,CORE1_SCAN,CORE0_SCAN',
               RecoveryMode = 'RecoveryPort',
               RecoveryOptions = 'S816_6C_8A',
               RecoveryTrackingIncoming = 'CR3_M,CR2_M,CR1_M,CR0_M',
               RecoveryTrackingOutgoing = 'CR3,CR2,CR1,CR0',
               ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = testinput.get("Preinstance", ""),
               SetPointsPostInstance = '',
               PreInstance = '',
               PostInstance = '',
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

def get_test_list_chain(
    flow,
    corner,
   
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain = []	
    sample_test_chain = \
        VminTC(name=f"CHAIN_UNCORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{corner}",
               Patlist = f'scn_cdie_{flow.lower()}_allchain_1hot_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               FeatureSwitchSettings = 'disable_masked_targets',
               ForwardingMode = 'Input',
               PinMap = 'CORE3_SCAN,CORE2_SCAN,CORE1_SCAN,CORE0_SCAN',
               RecoveryMode = 'RecoveryPort',
               RecoveryOptions = 'S816_6C_8A',
               RecoveryTrackingIncoming = 'CR3_M,CR2_M,CR1_M,CR0_M',
               RecoveryTrackingOutgoing = 'CR3,CR2,CR1,CR0',
               ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = testinput.get("Preinstance", ""),
               SetPointsPostInstance = '',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -41, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, goto="NEXT"),
               r5=pFail(setbin = -41, goto="NEXT")))
    test_listt_chain.append(sample_test_chain)
    
    return test_listt_chain
    
# MTT vmin search/check test
def get_test_list_atspeed_f1f4_mtt(
    flow, 
    corner, 
  
    testinput,
    FlowMatrix,
    recoverytestflag=False
    ):
      
    # decode MTT test name
    test_listt_atspeed_f1f4_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_f1f4_mtt = \
        NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{frequency_value}_MTT",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + ""',
                Patlist = f"scn_cdie_{flow.lower()}_allatspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                #LogLevel = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f"CR@{corner}",
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
                FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = '',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = '',
                MaskPins = '',
                PatternNameCounterIndexes = '',
                PinMap = 'CORE3_SCAN,CORE2_SCAN,CORE1_SCAN,CORE0_SCAN',
                RecoveryMode = testinput.get("Recovery", ""), 
                RecoveryOptions = 'S816_6C_8A',
                RecoveryTrackingIncoming = 'CR3_M,CR2_M,CR1_M,CR0_M',
                RecoveryTrackingOutgoing = 'CR3,CR2,CR1,CR0',
                #ScoreboardEdgeTicks = '',
                #MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                #SetPointsPreInstance = testinput.get("Preinstance", ""),
                SetPointsPreInstance = Spec(f'"MaaaCdrv:corefreq:"+'+Spec(f"__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MaaaCdrv:ringfreq:"+'+Spec(f"__shared__::FlowMatrixSingular.CR_{corner}_FREQ")+f'+"GHz,MCscnCORE:ratio_modify:"+'+Spec(f"__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
                SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
                StartVoltages = '0.9',
                #EndVoltageLimits = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -42, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -42, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
                             
    test_listt_atspeed_f1f4_mtt.append(sample_test_atspeed_f1f4_mtt)

    return test_listt_atspeed_f1f4_mtt

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
                trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + f' + ""',
                Patlist = f"scn_cdie_{flow.lower()}_allatspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                #LogLevel = '',
                BaseNumbers = AUTO,
                #CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")), # This is a placeholder for the corner identifiers. We will use the TrialParamSpec to define this.
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
                FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = '',
                FlowIndexCallbackName = '',
                #FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixManual.FlowIndex"),
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = '',
                MaskPins = '',
                PatternNameCounterIndexes = '',
                PinMap = 'CORE3_SCAN,CORE2_SCAN,CORE1_SCAN,CORE0_SCAN',
                RecoveryMode = testinput.get("Recovery", ""), 
                RecoveryOptions = 'S816_6C_8A',
                RecoveryTrackingIncoming = 'CR3_M,CR2_M,CR1_M,CR0_M',
                RecoveryTrackingOutgoing = 'CR3,CR2,CR1,CR0',
                #ScoreboardEdgeTicks = '',
                #MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                #SetPointsPreInstance = testinput.get("Preinstance", ""),
                SetPointsPreInstance = TrialParamSpec(f'"MaaaCdrv:corefreq:"+'+Spec(f"__shared__::FreqValues.CR_{corner_id}+")+'"GHz,MaaaCdrv:ringfreq:"+'+Spec(f"__shared__::FreqValues.CR_{corner_id}")+f'+"GHz,MCscnCORE:ratio_modify:"+'+Spec(f"__shared__::FreqValues.CR_{corner_id}+")+'"GHz"'),
                SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
                StartVoltages = '0.9',
                #EndVoltageLimits = Spec(f"__shared__::FlowMatrix.CR_HIGH_SEARCH_VALUE"),
                #StartVoltages = Spec(f"__shared__::FlowMatrix.CR_LOW_SEARCH_VALUE"),
                #StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -42, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -42, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
                             
    test_listt_atspeed_f5f6_mtt.append(sample_test_atspeed_f5f6_mtt)

    return test_listt_atspeed_f5f6_mtt
    
#####################
#   SPOFI TESTS IO  #
###################################################################################################### 
   
def get_test_list_stuckat_spofi(
    flow,
    corner,
    testinput
    ):

   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_spofi = []
    sample_test_stuckat_spofi = \
        PrimeScanSPOFITestMethod(name=f"STUCKAT_UNCORE_SPOFI_K_{flow}_X_X_NOM_{corner}",
               Patlist = f'scn_cdie_{flow.lower()}_allstuckat_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-42, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-42, goto="NEXT")))

    test_listt_stuckat_spofi.append(sample_test_stuckat_spofi)
    
    return test_listt_stuckat_spofi

def get_test_list_atspeed_spofi(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_spofi = []
    sample_test_atspeed_spofi = \
        PrimeScanSPOFITestMethod(name=f"ATSPEED_UNCORE_SPOFI_K_{flow}_X_X_NOM_{corner}",
               Patlist = f'scn_cdie_{flow.lower()}_allatspeed_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-47, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-47, goto="NEXT")))

    test_listt_atspeed_spofi.append(sample_test_atspeed_spofi)
    
    return test_listt_atspeed_spofi

def get_test_list_chain_spofi(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain_spofi = []
    sample_test_chain_spofi = \
        PrimeScanSPOFITestMethod(name=f"CHAIN_UNCORE_SPOFI_K_{flow}_X_X_NOM_{corner}",
               Patlist = f'scn_cdie_{flow.lower()}_allchain_1hot_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-41, goto=f"PROXY_UNCORE_SPOFI_K_{flow}_X_X_NOM_{corner}"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-41, goto=f"PROXY_UNCORE_SPOFI_K_{flow}_X_X_NOM_{corner}")))

    test_listt_chain_spofi.append(sample_test_chain_spofi)
    
    return test_listt_chain_spofi

def get_test_list_proxy_spofi(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_proxy_spofi = []
    sample_test_proxy_spofi = \
        PrimeScanSPOFITestMethod(name=f"PROXY_UNCORE_SPOFI_K_{flow}_X_X_NOM_{corner}",
               Patlist = f'scn_cdie_{flow.lower()}_allchain_proxy_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-41, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-41, goto="NEXT")))

    test_listt_proxy_spofi.append(sample_test_proxy_spofi)
    
    return test_listt_proxy_spofi

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
    sample_test_stuckat_shmoo = DDGShmooTC(name = f"STUCKAT_UNCORE_SHMOO_E_{flow}_X_X_NOM",
                Patlist = f'scn_cdie_{flow.lower()}_allstuckat_ssn200_edt_classhvm_list',
                LevelsTc = LOCAL_PARAM_MIN_LevelsTc,
                TimingsTc = LOCAL_PARAM_POR_TimingsTc,
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = '',
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                XAxisParam = LOCAL_PARAM_SHMOO_XAxisParam,
                XAxisRange = '',
                YAxisType = "SpecSetVariable",
                YAxisParamType = "UserDefined",
                YAxisParam = LOCAL_PARAM_SHMOO_YAxisParam,
                YAxisRange = '',
                LogLevel = '',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-42, goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(setbin=-42, goto="NEXT")))
               
    test_listt_stuckat_shmoo.append(sample_test_stuckat_shmoo)
    
    return test_listt_stuckat_shmoo
    
def get_test_list_atspeed_shmoo(
    flow, 
    corner, 
   
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_atspeed_shmoo = []
    sample_test_atspeed_shmoo = DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{flow}_X_X_NOM",
                Patlist = f'scn_cdie_{flow.lower()}_allatspeed_ssn200_edt_classhvm_list',
                LevelsTc = LOCAL_PARAM_MIN_LevelsTc,
                TimingsTc = LOCAL_PARAM_POR_TimingsTc,
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance = '',
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                XAxisParam = LOCAL_PARAM_SHMOO_XAxisParam,
                XAxisRange = '',
                YAxisType = "SpecSetVariable",
                YAxisParamType = "UserDefined",
                YAxisParam = LOCAL_PARAM_SHMOO_YAxisParam,
                YAxisRange = '',
                LogLevel = '',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-47, goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(setbin=-47, goto="NEXT")))
               
    test_listt_atspeed_shmoo.append(sample_test_atspeed_shmoo)
    
    return test_listt_atspeed_shmoo
    
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
               ConfigurationFile = f"./Modules/{MODULE}/inputfiles/dummy.setpoints.json",
               SetPoint = "scancoredummy",
               SetPointsPlistMode = "Global",
               SetPointsPreInstance = 'MCdrv:corefreq_VAL_0_8GHz',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
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
               Parameters = f"--decoder AnyFailSingleSliceDecoder --file ./Modules/{MODULE}/inputfiles/DieRecoveryPinMaps_IO_NVL_SCNCORE.json",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
               r1=pPass(goto="NEXT")))
    test_listt_callback.append(sample_test_callback)
    
    return test_listt_callback   
    
#################################################################################
#							INIT SUBFLOW
#
#	- INIT flow will have pinmap & dierecovery related tests in 
#
#################################################################################
init_flow = "INIT"

init_patmod_tli = {"Bypassport": 1, "ISEDC": True}
init_patmod = get_test_globalinit_patmod(init_flow, init_patmod_tli)

pinmap_parse_tli = {"Bypassport": 1, "ISEDC": True}
pinmap_parse = get_test_pinmap_parse(init_flow, init_patmod_tli)

#INIT SUBFLOW
INIT_SUBFLOW = Flow(f'{MODULE}_INIT',
                                init_patmod,
                                pinmap_parse,
                              )    


#################################################################################
#							BEGINCPU SUBFLOW
#
#	- BEGINCPU flow will test 10% STUCKAT content 
#	- Fail flow will include CHAIN, & SPOFI 
#
#################################################################################

begincpu_flow = "BEGINCPU"
begincpu_corner = "LFM"

# OCC COMPOSITE TEST LIST
begincpu_vmintc_stuckat_occ_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begincpu_vmintc_stuckat_occ = get_test_list_stuckat_occ(begincpu_flow, begincpu_corner, begincpu_vmintc_stuckat_occ_tli)
begincpu_occ = Flow("BEGINCPU_ALL", begincpu_vmintc_stuckat_occ)

# ScreenTC
begincpu_screentc_tli = {"Bypassport": 1, "ISEDC": True}
begincpu_screentc = get_test_list_screentc(begincpu_flow, begincpu_screentc_tli)

# Patconfig
begincpu_patconfig_tli = {"Bypassport": 1, "ISEDC": True}
begincpu_patconfig = get_test_list_patconfig(begincpu_flow, begincpu_patconfig_tli)

# Function to create test lists and flows for each module
vmintc_stuckat_chain_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True,  "Preinstance": ""}
vmintc_stuckat = get_test_list_stuckat(begincpu_flow, begincpu_corner, vmintc_stuckat_chain_tli)

vmintc_chain = get_test_list_chain(begincpu_flow, begincpu_corner, vmintc_stuckat_chain_tli)
    
spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True}
spofi_stuckat = get_test_list_stuckat_spofi(begincpu_flow, begincpu_corner, spofi_stuckat_tli)

spofi_chain_tli = {"Bypassport": 1, "ISEDC": True}
spofi_chain = get_test_list_chain_spofi(begincpu_flow, begincpu_corner, spofi_chain_tli)

spofi_proxy_tli = {"Bypassport": 1, "ISEDC": True}
spofi_proxy = get_test_list_proxy_spofi(begincpu_flow, begincpu_corner, spofi_proxy_tli)

begincpu_io = Flow(f"BEGINCPU_IO", vmintc_stuckat,  vmintc_chain, spofi_stuckat, spofi_chain, spofi_proxy)

# BEGINCPU SUBFLOW
BEGINCPU_SUBFLOW = Flow(f'{MODULE}_BEGINCPU',
                     Fitem("SAME", begincpu_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     begincpu_screentc,
                     begincpu_patconfig,
                     Fitem("SAME", begincpu_io, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                    )
                     
#################################################################################
#                           F1F4 X CCF SUBFLOW
#
#   - Consists of F1 through F4 corners flow which will test 100% ATSPEED content 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "CCF_F1_FREQ",
    "F2": "CCF_F2_FREQ",
    "F3": "CCF_F3_FREQ",
    "F4": "CCF_F4_FREQ"
}
   
# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix):
        
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    occ = Flow(f"{flow_name}_ALL", vmintc_atspeed_occ)
                    
    # ScreenTC
    screentc_tli = {"Bypassport": 1, "ISEDC": True}
    screentc = get_test_list_screentc(flow_name, screentc_tli)

    # Patconfig
    patconfig_tli = {"Bypassport": 1, "ISEDC": True}
    patconfig = get_test_list_patconfig(flow_name, patconfig_tli)

    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "Scoreboard",
        "Voltagetarget": "",
        "ISEDC": False,
        "Recovery": "RecoveryPort",
        "Preinstance": ""
    }
    
    vmintc_atspeed = get_test_list_atspeed_f1f4_mtt(flow_name, corner, vmintc_atspeed_tli, flow_matrix)
    
    shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    shmoo_atspeed = get_test_list_stuckat_shmoo(flow_name, corner,  shmoo_atspeed_tli) 

    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_atspeed_spofi(flow_name, corner, spofi_atspeed_tli) 

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_stuckat_spofi(flow_name, corner, spofi_stuckat_tli) 

    f1f4_io = Flow(f"{flow_name}_IO", vmintc_atspeed)
    
    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT"), r2=pFail(ret=0), r3=pPass(ret=1), r4=pFail(ret=0), r5=pFail(ret=0)),
                   #screentc,
                   #patconfig,
                   Fitem("SAME", f1f4_io, r0=pFail(ret=0), r1=pPass(goto="NEXT"), r2=pFail(ret=0), r3=pPass(ret=1), r4=pFail(ret=0), r5=pFail(ret=0))),
                      
    return subflow

# Define the subflows
subflows = []
for i in range(1, 5):
    flow_name = f"F{i}XCCF"
    corner = f"F{i}"
    flow_matrix = flow_matrix_definitions[corner]
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix))

#################################################################################
#                           F5F6 X CCF SUBFLOW
#
#   - Consists of F5 & F6 corners flow which will test 100% ATSPEED content in TOP subflow 
#
#################################################################################


    
#################################################################################
#							ENDCPU SUBFLOW
#
#	- ENDCPU flow will test ATSPEED & STUCKAT content 
#	- No Fail flow 
#
#################################################################################
