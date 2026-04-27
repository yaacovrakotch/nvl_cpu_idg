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
LOCAL_PARAM_SHMOO_XAxisParam = "p_all_mts"
LOCAL_PARAM_SHMOO_YAxisParam = "p_vnnaon_spec"
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
LOCAL_PARAM_MIN_LevelsTc = "SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max"
LOCAL_PARAM_MAX_LevelsTc = ""
LOCAL_PARAM_POR_TimingsTc = "IPC::SCN_UNCORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_OVERRIDEPKG"
LOCAL_PARAM_HVM_DOMAIN = "CPU_TRIALS::FlowDomain.RING"
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
MODULE = "SCN_UNCORE_CK48"  # You can change this as needed
VOLTAGE_DOMAIN = "VNNAON"


########################################################################
# INITIALIZE
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(4141, 4149), (4241, 4249), (4741, 4749)],
	ctrrangeforbins=(2980 , 2999 ),
    defaultthermalbin=[(97412980, 97412999), (97422980, 97422999), (97472980, 97472999), (97942980, 97942999)], #9097HB17
    defaultresetbin=[(41192980, 41192999), (42192980, 42192999), (47192980, 47192999), (94192980, 94192999)], #90HB1917/90HB1918
    defaultrm2bin = [(99412980, 99412999), (99422980, 99422999), (99472980, 99472999), (99942980, 99942999)], 
    defaultrm1bin = [(98412980, 98412999), (98422980, 98422999), (98472980, 98472999), (98942980, 98942999)],
    basenumrange=(13666,13999),
    #basenumrange = [(23000, 23999), (28000, 28999)]
    #                ^^^ HVM ^^^^^   ^^^^^ EDC ^^^^
)

########################################################################
# IMPORT REQUIRED FILES
########################################################################

Import(MODULE + ".usrv")
Import(MODULE + "_Levels.tcg")
#Import ("SCN_UNCORE_CX48_Timing.tcg")


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
               r0=pFail(ret =1),
               r1=pPass(ret =1),
               r2=pFail(ret = 1)))
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
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_X_MAX_X_ALL",
               Patlist = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("IPC::scn_cdie_begin_full_atpg_all_edt_classhvm_list","IPC::scn_cdie_begin_atpg_edt_classhvm_all_list","IPC::scn_cdie_begin_full_atpg_all_edt_classhvm_list","IPC::scn_cdie_begin_atpg_edt_classhvm_all_list")'),
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules2'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = "NOM_CCF",
               ForwardingMode = 'None',
               PinMap = '',
               RecoveryMode = 'Default',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               FailCaptureCount= 999,
               RecoveryTrackingOutgoing = '',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = '',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_REC"),
               r1=pPass(goto= "NEXT"),
               r2=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_REC"),
               r3=pPass(goto= "NEXT"),
               r4=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_REC"),
               r5=pFail(setbin = -42, goto="STUCKAT_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_REC")))
    test_listt_stuckat_occ.append(sample_test_stuckat_occ)
    
    return test_listt_stuckat_occ
    
def get_test_list_stuckat_occ_rec(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_occ_rec = []	
    sample_test_stuckat_occ = \
        VminTC(name=f"STUCKAT_UNCORE_SB_K_{flow}_X_X_MAX_X_REC",
               Patlist = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("IPC::scn_cdie_begin_full_atpg_all_edt_classhvm_list","IPC::scn_cdie_begin_atpg_edt_classhvm_all_list","IPC::scn_cdie_begin_full_atpg_all_edt_classhvm_list","IPC::scn_cdie_begin_atpg_edt_classhvm_all_list")'),
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = "NOM_CCF",
               ForwardingMode = 'None',
               PinMap = '',
               RecoveryMode = 'Default',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               FailCaptureCount= 999,
               RecoveryTrackingOutgoing = '',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = '',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r1=pPass(goto= "ATSPEED_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r2=pFail(setbin = -42, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r3=pPass(goto= "ATSPEED_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r4=pFail(setbin = -42, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r5=pFail(setbin = -42, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL")))
    test_listt_stuckat_occ_rec.append(sample_test_stuckat_occ)
    
    return test_listt_stuckat_occ_rec
 
def get_test_list_atspeed_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_occ = []
    sample_test_atspeed_occ = \
        VminTC(name=f"ATSPEED_UNCORE_SB_K_{flow}_X_X_MAX_X_ALL",
               Patlist = 'IPC::scn_cdie_begin_trans_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = "NOM_CCF",
               ForwardingMode = 'None',
               PinMap = '',
               RecoveryMode = 'Default', 
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               FailCaptureCount= 999,
              # ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance =Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'), 
               SetPointsPostInstance = '',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -47, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -47, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -47, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL"),
               r5=pFail(setbin = -47, goto="CHAIN_UNCORE_SB_K_BEGINCPUPKG_X_X_MAX_X_ALL")))
    test_listt_atspeed_occ.append(sample_test_atspeed_occ)
    
    return test_listt_atspeed_occ




def get_test_list_chain_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain_occ = []
    sample_test_chain_occ = \
        VminTC(name=f"CHAIN_UNCORE_SB_K_{flow}_X_X_MAX_X_ALL",
               Patlist = 'IPC::scn_cdie_begin_chain_edt_classhvm_all_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               LogLevel = 'Disabled',
               SetPointsPlistMode = "Local",
               FeatureSwitchSettings = "fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters",
               FivrCondition = "NOM_CCF",
               ForwardingMode = 'None',
               PinMap = '',
               RecoveryMode = 'Default', 
               FailCaptureCount= 999,
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__:: Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__:: Specs.VMX_MAX_FAILS)"),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
              # ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = '',
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(ret=0),
               r1=pPass(ret=0),
               r2=pFail(ret=0),
               r3=pPass(ret=0),
               r4=pFail(ret=0),
               r5=pFail(ret=0)))
    test_listt_chain_occ.append(sample_test_chain_occ)
    
    return test_listt_chain_occ


# MTT vmin search/check test

    
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
                Patlist = f"scn_cdie_{flow.lower()}_allpar_occ_atspeed_edt_classhvm_list",
                LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                PreInstance = '',
                PostInstance = '',
                LogLevel = '',
                VminResult = '',
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = '',
                FeatureSwitchSettings = 'disable_masked_targets',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                ForwardingMode = 'None',
                InitialMaskBits = '',
                MaskPins = '',
                #PatternNameCounterIndexes = '',
                PinMap = '',
                RecoveryMode = 'NoRecovery', 
                RecoveryOptions = '',
                RecoveryTrackingIncoming = '',
                RecoveryTrackingOutgoing = '',
                ScoreboardEdgeTicks = Spec("toInteger(0)"),
                MaxFailsNum = '',
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = '',
                SetPointsPostInstance = '',
                StartVoltages = '',
                StepSize = '',
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = '',
                VoltagesOffset = '',
                VoltageTargets = testinput.get("Voltagetarget", "CCF"),
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
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_stuckat_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_atspeed_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_chain_1hot_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
               Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_allchain_proxy_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
        
    return DDGShmooTC(name = f"STUCKAT_UNCORE_SHMOO_E_{flow}_X_X_NOM_X_ALL",
                _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
                Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_stuckat_edt_classhvm_list',
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
                LogLevel = 'Enabled',
                BypassPort = testinput.get("BypassPort", 1),
                r0=pFail(setbin= -42, ret=0, trialaction = "Exit"),
                r1=pPass(setbin= -42, ret=1, trialaction = "Exit"),
                r2=pFail(setbin= -42, ret=2, trialaction = "Exit"),
                r3=pFail(setbin= -42, ret=3, trialaction = "Exit")
    )

def get_atspeed_shmoo_test_occ(flow, corner, testinput):
        
    return DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{flow}_X_X_NOM_X_ALL",
                _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
                Patlist = f'scn_cdie_{flow.lower()}_allpar_occ_atspeed_edt_classhvm_list',
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
                LogLevel = "Enabled",
                BypassPort = testinput.get("BypassPort", 1),
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
               Patlist = f'scn_cdie_{flow.lower()}_allstuckat_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "CCF"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               FeatureSwitchSettings = 'disable_masked_targets',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               ForwardingMode = 'None',
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               SetPointsPlistParamName = 'Patlist',
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
               Patlist = f'scn_cdie_{flow.lower()}_allatspeed_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9', 
               VoltageTargets = testinput.get("Voltagetarget", "HC05_03_0P85_VCCCORE0"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               FeatureSwitchSettings = 'disable_masked_targets',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               ForwardingMode = 'None',
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #ScoreboardMaxFails = '',
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = testinput.get("Preinstance", ""),
#               SetPointsPostInstance = 'MCdrv:core_disable_0:enable_core_core',
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
                Patlist = f"scn_cdie_{flow.lower()}_allatspeed_edt_classhvm_list",
                LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                PreInstance = '',
                PostInstance = '',
                LogLevel = 'Enabled',
                BaseNumbers = AUTO,
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = '',
                ExecutionMode = 'SearchWithScoreboard',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                FeatureSwitchSettings = 'disable_masked_targets',
                FivrCondition = '',
                FlowIndexCallbackName = '',
                FlowIndex = '',
                ForwardingMode = 'None',
                InitialMaskBits = '',
                LimitGuardband = '',
                MaskPins = '',
               # PatternNameCounterIndexes = '',
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
                SetPointsPostInstance = '',
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
               Patlist = f'scn_cdie_{flow.lower()}_allstuckat_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
               Patlist = f'scn_cdie_{flow.lower()}_allatspeed_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
               Patlist = f'scn_cdie_{flow.lower()}_allchain_1hot_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
               Patlist = f'scn_cdie_{flow.lower()}_allchain_proxy_edt_classhvm_list',
               TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
               LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'),
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
        
    return DDGShmooTC(name = f"STUCKAT_UNCORE_SHMOO_E_{flow}_X_X_NOM_X",
                _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
                Patlist = 'IPC::scn_cdie_begin_full_atpg_all_edt_classhvm_list',
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'), 
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance =Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                XAxisParam =Spec(f'__shared__::TpRule.If_C48_DS_AX_M("all_mts","p_all_mts","all_mts","p_all_mts")'),
                XAxisRange = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("1100e6:100e6:5","600e6:100e6:5","1100e6:100e6:5","600e6:100e6:5")'),
                YAxisType = "SpecSetVariable",
                YAxisParamType = "UserDefined",
                YAxisParam = "p_vnnaon_spec",
                YAxisRange = "1.2:-0.1:10",
                VoltageConverter ="",
                LogLevel = 'Enabled',
                BypassPort = testinput.get("BypassPort", 1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-42, goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(setbin=-42, goto="NEXT")))
    
    
def get_shmoo_test_atspeed(flow, corner, testinput):
      
    return DDGShmooTC(name = f"ATSPEED_UNCORE_SHMOO_E_{flow}_X_X_NOM_X",
                _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
                Patlist = 'IPC::scn_cdie_begin_trans_edt_classhvm_list',
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'), 
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance =Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                XAxisParam =Spec(f'__shared__::TpRule.If_C48_DS_AX_M("all_mts","p_all_mts","all_mts","p_all_mts")'),
                XAxisRange = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("1100e6:100e6:5","600e6:100e6:5","1100e6:100e6:5","600e6:100e6:5")'),
                YAxisType = "SpecSetVariable",
                YAxisParamType = "UserDefined",
                YAxisParam = "p_vnnaon_spec",
                YAxisRange = "1.2:-0.1:10",
                VoltageConverter ="",
                LogLevel = 'Enabled',
                BypassPort = testinput.get("BypassPort", 1),
               _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-42, goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(setbin=-42, goto="NEXT"))
    )
    
def get_shmoo_test_chain(flow, corner, testinput):
      
    return DDGShmooTC(name = f"CHAIN_UNCORE_SHMOO_E_{flow}_X_X_NOM_X",
                _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
                Patlist = 'IPC::scn_cdie_begin_chain_edt_classhvm_list',
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                LevelsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'), 
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance =Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                XAxisParam =Spec(f'__shared__::TpRule.If_C48_DS_AX_M("all_mts","p_all_mts","all_mts","p_all_mts")'),
                XAxisRange = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("1100e6:100e6:5","600e6:100e6:5","1100e6:100e6:5","600e6:100e6:5")'),
                YAxisType = "SpecSetVariable",
                YAxisParamType = "UserDefined",
                YAxisParam = "p_vnnaon_spec",
                YAxisRange = "1.2:-0.1:10",
                VoltageConverter ="",
                LogLevel = 'Enabled',
                BypassPort = testinput.get("BypassPort", 1),
                 _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-42, goto="NEXT"),
                r1=pPass(ret=1),
                r2=pFail(setbin=-42, goto="NEXT"))
    )
    
def get_shmoo_test_chain_mul(flow, corner, testinput):
      
    return DDGShmooTC(name = f"CHAIN_UNCORE_SHMOO_E_{flow}_X_X_NOM_X_STB",
                Patlist = 'IPC::scn_cdie_begin_chain_edt_classhvm_list',
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                LevelsTc = Spec(f'__shared__::TpRule.If_DS0_DS1_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'), 
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance =Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                XAxisParam = "cpu_tstprt_o_stb_mul",
                XAxisRange = '1.8:-0.1:12',
                VoltageConverter ="",
                LogLevel = 'Enabled',
                BypassPort = testinput.get("BypassPort", -1),
                 _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-42, goto="NEXT"),
                r1=pPass(goto="NEXT"),
                r2=pFail(setbin=-42, goto="NEXT"))
    )  
def get_shmoo_test_chain_mul2(flow, corner, testinput):
      
    return DDGShmooTC(name = f"CHAIN_UNCORE_SHMOO_E_{flow}_X_X_NOM_X_ICLK",
                Patlist = 'IPC::scn_cdie_begin_chain_edt_classhvm_list',
                TimingsTc = Spec(f'SCN_UNCORE_CK48_Specs.timingRules'),
                LevelsTc = Spec(f'__shared__::TpRule.If_DS0_DS1_M("SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCOREB0_OVERRIDE_max","SCN_UNCORE_CK48::cpu_all_bf_x_x_pkg_lvl_CPU_BFUNC_SCNUNCORE_OVERRIDE_max")'), 
                SetPointsPlistParamName = "Patlist",
                SetPointsPlistMode = "Local",
                SetPointsPreInstance =Spec(f'"MCdrv:ringfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.CCF_{corner}_FREQ+")+'"GHz"'),
                PrintFormat = LOCAL_PARAM_SHMOO_PrintFormat,
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                XAxisParam = "cpu_tstprt_i_clk_mul",
                XAxisRange = '1.8:-0.1:17',
                VoltageConverter ="",
                LogLevel = 'Enabled',
                BypassPort = testinput.get("BypassPort", -1),
                 _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(setbin=-42, goto="NEXT"),
                r1=pPass(goto="NEXT"),
                r2=pFail(setbin=-42, goto="NEXT"))
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
               ConfigurationFile = f"./inputfiles/SCN_UNCORE_INIT.setpoints.json",
               SetPoint = "scanuncorepatmod",
               #SetPointsPlistMode = "Global",
               SetPointsPreInstance = '',
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
INIT_FLOW = "INIT"

INIT_PATMOD_TLI = {"Bypassport": -1, "ISEDC": True}
INIT_PATMOD = get_test_globalinit_patmod(INIT_FLOW, INIT_PATMOD_TLI)

#PINMAP_PARSE_TLI = {"Bypassport": 1, "ISEDC": True}
#PINMAP_PARSE = get_test_pinmap_parse(INIT_FLOW, INIT_PATMOD_TLI)

#INIT SUBFLOW
INIT_SUBFLOW = Flow(f'{MODULE}_INIT',
                                INIT_PATMOD,
                                
                              )    


#################################################################################
#							BEGINCPUPKG SUBFLOW
#
#	- BEGINCPUPKG 
#	- Fail flow will include CHAIN, & SPOFI 
#
#################################################################################

BEGINCPUPKG_FLOW = "BEGINCPUPKG"
BEGINCPUPKG_CORNER = "F1"

# OCC COMPOSITE TEST LIST (HERE IS WHERE YOU CHANGE THE FLOW)
BEGINCPUPKG_VMINTC_STUCKAT_OCC_TLI = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
BEGINCPUPKG_VMINTC_STUCKAT_OCC_REC_TLI = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": False}
BEGINCPUPKG_VMINTC_STUCKAT_OCC = get_test_list_stuckat_occ(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_VMINTC_STUCKAT_OCC_TLI)
BEGINCPUPKG_VMINTC_STUCKAT_OCC_REC = get_test_list_stuckat_occ_rec(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_VMINTC_STUCKAT_OCC_REC_TLI)
BEGINCPUPKG_VMINTC_ATSPEED_OCC_TLI = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": False}
BEGINCPUPKG_VMINTC_ATSPEED_OCC = get_test_list_atspeed_occ(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_VMINTC_ATSPEED_OCC_TLI)
BEGINCPUPKG_VMINTC_CHAIN_OCC_TLI = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
BEGINCPUPKG_VMINTC_CHAIN_OCC = get_test_list_chain_occ(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, BEGINCPUPKG_VMINTC_CHAIN_OCC_TLI)

#SHMOO
begincpupkg_shmoo_stuckat_tli =  {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
begincpupkg_shmoo_stuckat = get_shmoo_test_stuckat(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, begincpupkg_shmoo_stuckat_tli)
begincpupkg_shmoo_atspeed_tli =  {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
begincpupkg_shmoo_atspeed = get_shmoo_test_atspeed(BEGINCPUPKG_FLOW, BEGINCPUPKG_CORNER, begincpupkg_shmoo_atspeed_tli)
begincpupkg_shmoo_chain_tli =  {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True}
begincpupkg_shmoo_chain = get_shmoo_test_chain(BEGINCPUPKG_FLOW,BEGINCPUPKG_CORNER, begincpupkg_shmoo_chain_tli)
begincpupkg_shmoo_chain_mul = get_shmoo_test_chain_mul(BEGINCPUPKG_FLOW,BEGINCPUPKG_CORNER, begincpupkg_shmoo_chain_tli)
begincpupkg_shmoo_chain_mul2 = get_shmoo_test_chain_mul2(BEGINCPUPKG_FLOW,BEGINCPUPKG_CORNER, begincpupkg_shmoo_chain_tli)
begincpupkg_shmoo_occ = Flow("BEGINCPUPKG_SHMOO", begincpupkg_shmoo_stuckat,begincpupkg_shmoo_atspeed,begincpupkg_shmoo_chain)

BEGINCPUPKG_OCC = Flow("BEGINCPUPKG_SCN_UNCORE",begincpupkg_shmoo_chain_mul,begincpupkg_shmoo_chain_mul2, BEGINCPUPKG_VMINTC_STUCKAT_OCC,BEGINCPUPKG_VMINTC_ATSPEED_OCC,BEGINCPUPKG_VMINTC_STUCKAT_OCC_REC, BEGINCPUPKG_VMINTC_CHAIN_OCC )

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

#BEGINCPUPKG_IO = Flow("BEGINCPU_IO", BEGINCPUPKG_VMINTC_STUCKAT, BEGINCPUPKG_SPOFI_STUCKAT, BEGINCPUPKG_SPOFI_CHAIN, BEGINCPUPKG_SPOFI_PROXY,)

#BEGINCPUPKG SUBFLOW
BEGINCPUPKG_SUBFLOW = Flow(f'{MODULE}_BEGINCPUPKG',
                                        Fitem("SAME", BEGINCPUPKG_OCC, r0=pFail(ret=0), r1=pPass(ret=1)),
                                        Fitem("SAME", begincpupkg_shmoo_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT"))
                                        )

                     
#################################################################################
#                           SHMOO SUBFLOW
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
