#from turtle import pos
from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig

########################################################################
# ddaudmai ww05'2025 - SORT basic skeleton tryout
# ddaudmai ww13'2025 - CLASS tests, subflows details adjustment to fit class requirement 

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

# frequency decode for single static test
STATIC_FREQUENCY_CORNERS = {
    "F1" : "400",
    "F2" : "800",
    "F3" : "1100",
    "F4" : "1400",
    "F5" : "1600",
    "F6" : "2100"
    }

# Define DCM_MODULES based on MODULE #
MODULE = "SCN_UNCORE_CK816"  # You can change this as needed
VOLTAGE_DOMAIN = "VNNAON"


########################################################################
# INITIALIZE
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(4141, 4149), (4241, 4249), (4741, 4749)],
    defaultthermalbin=(90974141, 90974241, 90974741), #9097HB17
    defaultresetbin=(90411941, 90421941, 90471941), #90HB1917/90HB1918
    basenumrange=(3000,3332),
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
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_X_NOM_{corner}_ALL",
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
               SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
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
 
def get_test_list_atspeed_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_occ = []
    sample_test_atspeed_occ = \
        VminTC(name=f"ATSPEED_UNCORE_VMIN_K_{flow}_X_X_NOM_{corner}_ALL",
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_atspeed_ssn200_edt_classhvm_list',
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
               SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-47, ret=0),
               r1=pPass(ret=1),
               r2=pFail(setbin = -42, ret=0),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, ret=0),
               r5=pFail(setbin = -42, ret=0)))
    test_listt_atspeed_occ.append(sample_test_atspeed_occ)
    
    return test_listt_atspeed_occ

# MTT vmin search/check test
def get_occ_mtt_kill_test_atspeed (
    flow, 
    corner, 
    testinput,
    BinMatrix
    ):
        
    flag_search_flow = False
    #BinMatrix_Freq = f"CORE_{corner.upper()}_FREQ"
    #BinMatrix_Freq_MHz = BinMatrix
    
    # decode MTT test name
    test_listt_atspeed_occ_mtt = []
    sample_test_atspeed_occ_mtt = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_ALL_MTT",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + CustomBinMatrixSpecs.{BinMatrix}_MHz + "_UNCORE_" + BinMatrix.bin_ALLCORE',
                Patlist = f"scn_cdie_{flow.lower()}_allpar_occ_atspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                LogLevel = '',
                BaseNumbers = "13018",
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = '',
                FeatureSwitchSettings = 'disable_masked_targets',
                FivrCondition = '',
                FlowIndexCallbackName = '',
                FlowIndex = '',
                ForwardingMode = 'Input',
                InitialMaskBits = '',
                LimitGuardband = '',
                MaskPins = '',
                PatternNameCounterIndexes = '',
                PinMap = '',
                RecoveryMode = 'NoRecovery', 
                RecoveryOptions = '',
                RecoveryTrackingIncoming = '',
                RecoveryTrackingOutgoing = '',
                ScoreboardEdgeTicks = Spec("toInteger(0)"),
                MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = '',
                SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
                StartVoltages = '',
                StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0,HC06_03_0P85_VCCCORE1,HC07_03_0P85_VCCCORE2,HC08_03_0P85_VCCCORE3"),
                edc=testinput.get("ISEDC"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = "Next"),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 2, trialaction = "Next"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -47, ret= 4, trialaction = "Next"),
                r5 = pFail(setbin= -47, ret= 5, trialaction = "Next"),
                
                _fitem=Fitem('SAME', r0 = pFail(setbin = -47, ret= 0),
                             r1 = pPass(ret = 1, trialaction = "Exit"),
                             r2 = pFail(setbin= -47, ret= 2, trialaction = "Next"),
                             r3 = pPass(ret = 1, trialaction = "Exit"),
                             r4 = pFail(setbin= -47, ret= 4, trialaction = "Next"),
                             r5 = pFail(setbin= -47, ret= 5, trialaction = "Next")))
            
    test_listt_atspeed_occ_mtt.append(sample_test_atspeed_occ_mtt)

    return test_listt_atspeed_occ_mtt
    
# MTT RAW vmin search/check test
def get_occ_mtt_kill_test_atspeed_raw(
    flow, 
    corner, 
    testinput
    ):
        
    flag_search_flow = False
    BinMatrix_Freq = f"CORE_{corner.upper()}_FREQ"
    BinMatrix_Freq_MHz = BinMatrix_Freq+"_MHz"
       
    # decode MTT test name
    test_listt_atspeed_occ_mtt_raw = []
    sample_test_atspeed_occ_mtt_raw = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_ALLCORE_MTT_RAW",
                exitaction = "Restore",
                _comment = f"KILL ATSPEED {flow.upper()}_RAW",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_VMIN_E_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + CustomBinMatrixSpecs.{BinMatrix_Freq_MHz} + "_UNCORE_" + BinMatrix.bin_ALLCORE_RAW',
                Patlist = f"scn_cdie_{flow.lower()}_allpar_occ_atspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                LogLevel = '',
                VminResult = '',
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = '',
                FeatureSwitchSettings = 'disable_masked_targets',
                FivrCondition = '',
                ForwardingMode = 'Input',
                InitialMaskBits = '',
                MaskPins = '',
                PatternNameCounterIndexes = '',
                PinMap = '',
                RecoveryMode = 'NoRecovery', 
                RecoveryOptions = '',
                RecoveryTrackingIncoming = '',
                RecoveryTrackingOutgoing = '',
                ScoreboardEdgeTicks = Spec("toInteger(0)"),
                MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = '',
                SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
                StartVoltages = '',
                StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0,HC06_03_0P85_VCCCORE1,HC07_03_0P85_VCCCORE2,HC08_03_0P85_VCCCORE3"),
                edc=testinput.get("ISEDC"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = "Next"),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 2, trialaction = "Next"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -47, ret= 4, trialaction = "Next"),
                r5 = pFail(setbin= -47, ret= 5, trialaction = "Next"),
                
                _fitem=Fitem('SAME', r0 = pFail(setbin = -47, ret= 0),
                             r1 = pPass(ret = 1, trialaction = "Exit"),
                             r2 = pFail(setbin= -47, ret= 2, trialaction = "Next"),
                             r3 = pPass(ret = 1, trialaction = "Exit"),
                             r4 = pFail(setbin= -47, ret= 4, trialaction = "Next"),
                             r5 = pFail(setbin= -47, ret= 5, trialaction = "Next")))
                             
    test_listt_atspeed_occ_mtt_raw.append(sample_test_atspeed_occ_mtt_raw)

    return test_listt_atspeed_occ_mtt_raw
    
#####################
#   SPOFI TESTS OCC  #
###################################################################################################### 
   
def get_test_list_stuckat_spofi_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_spofi_occ = []
    sample_test_stuckat_spofi_occ = \
        PrimeScanSPOFITestMethod(name=f"STUCKAT_UNCORE_SPOFI_K_{flow}_X_X_NOM_ALL",
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_stuckat_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-42, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-42, ret=0)))

    test_listt_stuckat_spofi_occ.append(sample_test_stuckat_spofi_occ)
    
    return test_listt_stuckat_spofi_occ

def get_test_list_atspeed_spofi_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_spofi_occ = []
    sample_test_atspeed_spofi_occ = \
        PrimeScanSPOFITestMethod(name=f"ATSPEED_UNCORE_SPOFI_K_{flow}_X_X_NOM_ALL",
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_atspeed_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-47, ret=0),
               r1=pPass(ret=1),
               r2=pFail(setbin=-47, ret=0)))

    test_listt_atspeed_spofi_occ.append(sample_test_atspeed_spofi_occ)
    
    return test_listt_atspeed_spofi_occ

def get_test_list_chain_spofi_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain_spofi_occ = []
    sample_test_chain_spofi_occ = \
        PrimeScanSPOFITestMethod(name=f"CHAIN_UNCORE_SPOFI_K_{flow}_X_X_NOM_ALL",
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_chain_1hot_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-41, goto=f"PROXY_UNCORE_SPOFI_K_{flow}_X_X_NOM_ALL"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-41, goto=f"PROXY_UNCORE_SPOFI_K_{flow}_X_X_NOM_ALL")))

    test_listt_chain_spofi_occ.append(sample_test_chain_spofi_occ)
    
    return test_listt_chain_spofi_occ

def get_test_list_proxy_spofi_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_proxy_spofi_occ = []
    sample_test_proxy_spofi_occ = \
        PrimeScanSPOFITestMethod(name=f"PROXY_UNCORE_SPOFI_K_{flow}_X_X_NOM_ALL",
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_allchain_proxy_ssn200_edt_classhvm_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-41, ret=0),
               r1=pPass(ret=1),
               r2=pFail(setbin=-41, ret=0)))

    test_listt_proxy_spofi_occ.append(sample_test_proxy_spofi_occ)
    
    return test_listt_proxy_spofi_occ

#####################
#   SHMOO TESTS OCC   #
###################################################################################################### 

def get_stuckat_shmoo_test_occ(flow, corner, testinput):
        
    return DDGShmooTC(name = f"STUCKAT_UNCORE_SHMOO_E_{flow}_X_X_NOM_ALL",
                Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_stuckat_ssn200_edt_classhvm_list',
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
                BypassPort = testinput.get("BypassPort", -1),
                r0=pFail(setbin= -42, ret=0, trialaction = "Exit"),
                r1=pPass(setbin= -42, ret=1, trialaction = "Exit"),
                r2=pFail(setbin= -42, ret=2, trialaction = "Exit"),
                r3=pFail(setbin= -42, ret=3, trialaction = "Exit")
    )

def get_atspeed_shmoo_test_occ(flow, corner, testinput):
        
    return DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{flow}_X_X_NOM_ALL",
                Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_atspeed_ssn200_edt_classhvm_list',
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
                BypassPort = testinput.get("BypassPort", -1),
                r0=pFail(setbin= -47, ret=0, trialaction = "Exit"),
                r1=pPass(setbin= -47, ret=1, trialaction = "Exit"),
                r2=pFail(setbin= -47, ret=2, trialaction = "Exit"),
                r3=pFail(setbin= -47, ret=3, trialaction = "Exit")
    )
       
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
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_X_NOM_{corner}",
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
               SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
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

def get_test_list_atspeed(
    flow,
    corner,
   
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed = []
    sample_test_atspeed = \
        VminTC(name=f"ATSPEED_UNCORE_VMIN_K_{flow}_X_X_NOM_{corner}",
               Patlist = f'scn_cdie_{flow.lower()}_allatspeed_ssn200_edt_classhvm_list',
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
               RecoveryMode = testinput.get("Recovery", ""), 
               RecoveryOptions = 'S816_6C_8A',
               RecoveryTrackingIncoming = 'CR3_M,CR2_M,CR1_M,CR0_M',
               RecoveryTrackingOutgoing = 'CR3,CR2,CR1,CR0',
               ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = testinput.get("Preinstance", ""),
               SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-47, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -42, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, goto="NEXT"),
               r5=pFail(setbin = -42, goto="NEXT")))
    test_listt_atspeed.append(sample_test_atspeed)
    
    return test_listt_atspeed

# MTT vmin search/check test
def get_non_occ_mtt_kill_test_atspeed(
    flow, 
    corner, 
   
    testinput,
    recoverytestflag=False
    ):
        
    flag_search_flow = False
    BinMatrix_Freq = f"CORE_{corner.upper()}_FREQ"
    BinMatrix_Freq_MHz = BinMatrix_Freq+"_MHz"
       
    # decode MTT test name
    test_listt_atspeed_non_occ_mtt = []
    sample_test_atspeed_non_occ_mtt = \
        NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_MTT",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + CustomBinMatrixSpecs.{BinMatrix_Freq_MHz} + "_UNCORE_" + BinMatrix.bin',
                Patlist = f"scn_cdie_{flow.lower()}_allatspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                LogLevel = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = 'SearchWithScoreboard',
                FeatureSwitchSettings = 'disable_masked_targets',
                FivrCondition = '',
                FlowIndexCallbackName = '',
                FlowIndex = '',
                ForwardingMode = 'Input',
                InitialMaskBits = '',
                LimitGuardband = '',
                MaskPins = '',
                PatternNameCounterIndexes = '',
                PinMap = 'CORE3_SCAN,CORE2_SCAN,CORE1_SCAN,CORE0_SCAN',
                RecoveryMode = testinput.get("Recovery", ""), 
                #RecoveryMode = '',
                RecoveryOptions = 'S816_6C_8A',
                RecoveryTrackingIncoming = 'CR3_M,CR2_M,CR1_M,CR0_M',
                RecoveryTrackingOutgoing = 'CR3,CR2,CR1,CR0',
                ScoreboardEdgeTicks = '',
                MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = testinput.get("Preinstance", ""),
                #SetPointsPreInstance = '',
                SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
                StartVoltages = '0.9',
                StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                #TestMode = '',
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0"),
                #VoltageTargets = '',
                edc=testinput.get("ISEDC"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = "Next"),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                r5 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                
                _fitem=Fitem('SAME', r0 = pFail(setbin = -47, ret= 0),
                             r1 = pPass(ret = 1, trialaction = "Exit"),
                             r2 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                             r3 = pPass(ret = 1, trialaction = "Exit"),
                             r4 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                             r5 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next")))
                             
    test_listt_atspeed_non_occ_mtt.append(sample_test_atspeed_non_occ_mtt)

    return test_listt_atspeed_non_occ_mtt

# MTT RAW vmin search/check test
def get_non_occ_mtt_kill_test_atspeed_raw(
    flow, 
    corner, 

    testinput, 
    recoverytestflag=False
    ):
        
    flag_search_flow = False
    BinMatrix_Freq = f"CORE_{corner.upper()}_FREQ"
    BinMatrix_Freq_MHz = BinMatrix_Freq+"_MHz"
    
    # decode MTT test name
    test_listt_atspeed_non_occ_mtt_raw = []
    sample_test_atspeed_non_occ_mtt_raw = \
    NativeMultiTrial(name = f"ATSPEED_UNCORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_MTT_RAW",
                exitaction = "Restore",
                _comment = f"KILL ATSPEED {flow.upper()}_RAW",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + CustomBinMatrixSpecs.{BinMatrix_Freq_MHz} + "_UNCORE_" + BinMatrix.bin_ + _RAW',
                Patlist = f"scn_cdie_{flow.lower()}_allatspeed_ssn200_edt_classhvm_list",
                LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
                PreInstance = '',
                PostInstance = '',
                LogLevel = '',
                VminResult = '',
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = 'SearchWithScoreboard',
                FeatureSwitchSettings = 'disable_masked_targets',
                FivrCondition = '',
                ForwardingMode = 'Input',
                InitialMaskBits = '',
                LimitGuardband = '',
                MaskPins = '',
                PatternNameCounterIndexes = '',
                PinMap = 'CORE3_SCAN,CORE2_SCAN,CORE1_SCAN,CORE0_SCAN',
                RecoveryMode = testinput.get("Recovery", ""),            
                RecoveryOptions = 'S816_6C_8A',
                RecoveryTrackingIncoming = 'CR3_M,CR2_M,CR1_M,CR0_M',
                RecoveryTrackingOutgoing = 'CR3,CR2,CR1,CR0',
                ScoreboardEdgeTicks = '',
                MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = testinput.get("Preinstance", ""),
                SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
                StartVoltages = '0.9',
                StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0"),
                edc=testinput.get("ISEDC"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = "Next"),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                r3 = pPass(ret = 1, trialaction = "Exit"),
                r4 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                r5 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                
                _fitem=Fitem('SAME', r0 = pFail(setbin = -47, ret= 0),
                             r1 = pPass(ret = 1, trialaction = "Exit"),
                             r2 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                             r3 = pPass(ret = 1, trialaction = "Exit"),
                             r4 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next"),
                             r5 = pFail(setbin= -47, goto = "NEXT", trialaction = "Next")))
                             
    test_listt_atspeed_non_occ_mtt_raw.append(sample_test_atspeed_non_occ_mtt_raw)

    return test_listt_atspeed_non_occ_mtt_raw
    
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
    dcm,
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
def get_shmoo_test_stuckat(flow, corner, testinput):
        
    return DDGShmooTC(name = f"STUCKAT_UNCORE_SHMOO_E_{flow}_X_X_NOM",
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
                BypassPort = testinput.get("BypassPort", -1),
                r0=pFail(setbin= -42, ret=0, trialaction = "Exit"),
                r1=pPass(setbin= -42, ret=1, trialaction = "Exit"),
                r2=pFail(setbin= -42, ret=2, trialaction = "Exit"),
                r3=pFail(setbin= -42, ret=3, trialaction = "Exit")
    )
    
def get_shmoo_test_atspeed(flow, corner, testinput):
      
    return DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{flow}_X_X_NOM",
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
                XAxisRange = Spec(f"TpRule.If_RV({MODULE}.SHMOO_XAxisRange_RV,{MODULE}.SHMOO_XAxisRange_HVM)"),
                YAxisType = "SpecSetVariable",
                YAxisParamType = "UserDefined",
                YAxisParam = LOCAL_PARAM_SHMOO_YAxisParam,
                YAxisRange = Spec(f"TpRule.If_RV({MODULE}.SHMOO_YAxisRange_RV,{MODULE}.SHMOO_YAxisRange_HVM)"),
                LogLevel = '',
                BypassPort = testinput.get("BypassPort", -1),
                r0=pFail(setbin= -47, ret=0, trialaction = "Exit"),
                r1=pPass(setbin= -47, ret=1, trialaction = "Exit"),
                r2=pFail(setbin= -47, ret=2, trialaction = "Exit"),
                r3=pFail(setbin= -47, ret=3, trialaction = "Exit")
    )
    
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
               ConfigurationFile = "",
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
               Parameters = "",
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
#INIT_FLOW = "INIT"

#INIT_PATMOD_TLI = {"Bypassport": 1, "ISEDC": True}
#INIT_PATMOD = get_test_globalinit_patmod(INIT_FLOW, INIT_PATMOD_TLI)

#PINMAP_PARSE_TLI = {"Bypassport": 1, "ISEDC": True}
#PINMAP_PARSE = get_test_pinmap_parse(INIT_FLOW, INIT_PATMOD_TLI)

#INIT SUBFLOW
#INIT_SUBFLOW = Flow(f'{MODULE}_INIT',
#                                INIT_PATMOD,
#                                PINMAP_PARSE,
#                              )    


#################################################################################
#							BEGINCPUPKG SUBFLOW
#
#	- BEGINCPUPKG 
#	- Fail flow will include CHAIN, & SPOFI 
#
#################################################################################

BEGINCPUPKG_FLOW = "BEGINCPUPKG"
BEGINCPUPKG_CORNER = "LFM"

# OCC COMPOSITE TEST LIST
BEGINCPUPKG_VMINTC_STUCKAT_OCC_TLI = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
BEGINCPUPKG_VMINTC_STUCKAT_OCC = get_test_list_stuckat_occ(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_VMINTC_STUCKAT_OCC_TLI)
BEGINCPUPKG_OCC = Flow("BEGINCPUPKG_SCN_UNCORE", BEGINCPUPKG_VMINTC_STUCKAT_OCC)

# ScreenTC
BEGINCPUPKG_SCREENTC_TLI = {"Bypassport": 1, "ISEDC": True}
BEGINCPUPKG_SCREENTC = get_test_list_screentc(BEGINCPUPKG_FLOW, BEGINCPUPKG_SCREENTC_TLI)

# Patconfig
BEGINCPUPKG_PATCONFIG_TLI = {"Bypassport": 1, "ISEDC": True}
BEGINCPUPKG_PATCONFIG = get_test_list_patconfig(BEGINCPUPKG_FLOW, BEGINCPUPKG_PATCONFIG_TLI)

#IO 
BEGINCPUPKG_VMINTC_STUCKAT_TLI = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True, "Preinstance": "MCdrv:corefreq_VAL_0_8GHz,MCdrv:core0_disable_0:enable_core,MCdrv:core1_disable_0:disable_core,MCdrv:core2_disable_0:disable_core,MCdrv:core3_disable_0:disable_core"}
BEGINCPUPKG_VMINTC_STUCKAT = get_test_list_stuckat(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER,BEGINCPUPKG_VMINTC_STUCKAT_TLI)

BEGINCPUPKG_SPOFI_STUCKAT_TLI = {"Bypassport": 1, "ISEDC": True}
BEGINCPUPKG_SPOFI_STUCKAT = get_test_list_stuckat_spofi(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_SPOFI_STUCKAT_TLI)

BEGINCPUPKG_SPOFI_CHAIN_TLI ={"Bypassport": 1, "ISEDC": True}
BEGINCPUPKG_SPOFI_CHAIN = get_test_list_chain_spofi(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_SPOFI_CHAIN_TLI)

BEGINCPUPKG_SPOFI_PROXY_TLI = {"Bypassport": 1, "ISEDC": True}
BEGINCPUPKG_SPOFI_PROXY = get_test_list_proxy_spofi(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_SPOFI_PROXY_TLI)

BEGINCPUPKG_IO = Flow("BEGINCPU_IO", BEGINCPUPKG_VMINTC_STUCKAT, BEGINCPUPKG_SPOFI_STUCKAT, BEGINCPUPKG_SPOFI_CHAIN, BEGINCPUPKG_SPOFI_PROXY,)

#BEGINCPUPKG SUBFLOW
BEGINCPUPKG_SUBFLOW = Flow(f'{MODULE}_BEGINCPUPKG',
                                        Fitem("SAME", BEGINCPUPKG_OCC, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                                        BEGINCPUPKG_SCREENTC,
                                        BEGINCPUPKG_PATCONFIG,
                                        Fitem("SAME", BEGINCPUPKG_IO, r0=pFail(ret=0), r1=pPass(ret=1)),
                                        )

                     
#################################################################################
#                           F X CR SUBFLOW
#
#   - CHECK flow will test 80% ATSPEED content 
#
#################################################################################



#################################################################################
#							ENDCPU SUBFLOW
#
#	- ENDCPU flow will test ATSPEED & STUCKAT content 
#	- No Fail flow 
#
#################################################################################
