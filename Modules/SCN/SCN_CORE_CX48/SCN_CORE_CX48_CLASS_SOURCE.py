from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback, ApexTC, PrimeShmooTestMethod
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig
########################################################################
# hyusof ww2.2 - C48 pymtpl trim
########################################################################
# Define DCM_MODULES based on MODULE #
MODULE = "SCN_CORE_CX48"  # You can change this as needed
VOLTAGE_DOMAIN = "CR"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'

# Voltage targets for each module
voltage_targets = {
    "M0": "CORE0",
    "M1": "CORE1"
}

initial_maskbit = {
    "M0": "10",
    "M1": "01"  
}

if MODULE == "SCN_CORE_CX48":
    DCM_MODULES = ["M0", "M1"]
elif MODULE == "SCN_CORE_CX48":
    DCM_MODULES = ["M0", "M1"]
else:
    DCM_MODULES = []  # Default case if MODULE doesn't match any known value

########################################################################
# INITIALIZE
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(4100,4116), (4200, 4216), (4700, 4716)],
    ctrrangeforbins=(2667 , 2777 ),
    basenumrange = (13000,13332),
    defaultthermalbin=[(97412667, 97412777), (97422667, 97422777), (97472667, 97472777)],
    defaultresetbin=[(41192667, 41192777), (42192667, 42192777), (47192667, 47192777)],
    defaultrm2bin=[(99412667, 99412777), (99422667, 99422777), (99472667, 99472777)],
    defaultrm1bin=[(98412667, 98412777), (98422667, 98422777), (98472667, 98472777)]
)

Import ("SCN_CORE_CX48.usrv")
Import ("SCN_CORE_CX48_Timing.tcg")
Import ("SCN_CORE_CX48_Levels.tcg")

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
def get_test_list_patconfig_ratio4(
    flow,
    testinput,
    state
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_patconfig_ratio4 = []	
    sample_test_patconfig_ratio4 = \
        PrimePatConfigTestMethod(name=f"CTRL_X_PATMOD_K_{flow}_X_X_X_X_RESET_RATIO4_{state}",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'".//Modules/SCN/{MODULE}/InputFiles/fmin_ratio4_resetoverride.setpoints.json"'),
               SetPoint = testinput.get("setpoint",""),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_patconfig_ratio4.append(sample_test_patconfig_ratio4)
    
    return test_listt_patconfig_ratio4

def get_test_list_patconfig_ratio4_shmoo(
    flow,
    testinput,
    state
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_patconfig_ratio4_shmoo = []	
    sample_test_patconfig_ratio4_shmoo = \
        PrimePatConfigTestMethod(name=f"CTRL_X_PATMOD_K_BEGINCPU_X_X_X_X_RESET_RATIO4_{flow}_{state}",
               _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
               ConfigurationFile = Spec(MODULEPATH +' + 'f'".//Modules/SCN/{MODULE}/InputFiles/fmin_ratio4_resetoverride.setpoints.json"'),
               SetPoint = testinput.get("setpoint",""),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_patconfig_ratio4_shmoo.append(sample_test_patconfig_ratio4_shmoo)
    
    return test_listt_patconfig_ratio4_shmoo
       
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
        VminTC(name=f"STUCKAT_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_X_{corner}_ALLCORE",
               Patlist = f"scn_cdie_{flow.lower()}_occ_stuckat_ssn400_edt_classhvm_list",
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),               
               LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_max" if "VMAXXCR" in flow else "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",               
               BypassPort = testinput.get("Bypassport", -1),
               EndVoltageLimits = '0.9' if "BEGINCPU" in flow  else Spec(f'__shared__::FlowMatrixSingular.CR_VMAX_VALUE'), 
               ExecutionMode = "SearchWithScoreboard",
               BaseNumbers = AUTO,
               FailCaptureCount = Spec("toInteger(999)"),
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               FivrCondition = 'NOM_CCF_CORE',
               ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
               MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PreInstance = '',
               PostInstance = '',
               PinMap = 'SCN_CORE',
               RecoveryMode = 'RecoveryPort',
               RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
               RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
               RecoveryTrackingOutgoing = Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
               SetPointsPlistMode = 'Local',
               LogLevel = "Disabled",
               SetPointsPlistParamName = 'Patlist',
               SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}') if "BEGINCPU" in flow else Spec(f'PSPOST.CR_{corner}+' f'","+' f'"CORE:nblctrl_core_l2:nblon"'),
               SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"') if "BEGINCPU" in flow else Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz,"' f'+' f'"CORE:nblctrl_core_l2:nbloff"'),
               StartVoltages = '0.9' if "BEGINCPU" in flow  else Spec(f'__shared__::FlowMatrixSingular.CR_VMAX_VALUE'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = 'MultiVmin',
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="NEXT") if "BEGINCPU" in flow  else pFail(setbin = -42, ret= 0),
               r1=pPass(ret=1),
               r2=pFail(setbin = -42, goto="NEXT") if "BEGINCPU" in flow  else pFail(setbin = -42, ret= 0),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, goto="NEXT") if "BEGINCPU" in flow  else pFail(setbin = -42, ret= 0),
               r5=pFail(setbin = -42, goto="NEXT") if "BEGINCPU" in flow  else pFail(setbin = -42, ret= 0)))
    test_listt_stuckat_occ.append(sample_test_stuckat_occ)
    
    return test_listt_stuckat_occ

def get_test_list_atspeed_vmax_occ(
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
      
    # decode MTT test name
    test_listt_atspeed_vmax_occ = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_vmax_occ = \
        NativeMultiTrial(name = f"ATSPEED_CORE_SB_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_MAX_X_{corner.upper()}_FREQ_ALLCORE",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
                template = VminTC(name = f'"ATSPEED_CORE_SB_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_MAX_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.CR_{corner_id}") + f' + "_ALLCORE"',
                Patlist = f"scn_cdie_{flow.lower()}_occ_atspeed_ssn400_edt_classhvm_list",
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),                
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_max",                
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_VMAX_VALUE'),
                ExecutionMode = "SearchWithScoreboard",
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = 'NOM_CCF_CORE',
                ForwardingMode = "Input",
                MaskPins = '',
                PinMap = 'SCN_CORE_AS',
                RecoveryMode = 'NoRecovery',
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
                RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
                RecoveryTrackingOutgoing = Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                #CornerIdentifiers = f"CR3@F1,CR2@F1,CR1@F1,CR0@F1",
                DtsConfiguration = "ALL_CDIE_C48_N2P_CORE",
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f'__shared__::FlowMatrixSingular.FlowIndex'),
                InitialMaskBits = testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
                SetPointsPlistMode = 'Local',
                LogLevel = "Disabled",
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FreqValues.CR_{corner_id}+")+'"GHz,"' f'+' f'"CORE:nblctrl_core_l2:nbloff"') ,
                SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}+' f'","+' f'"CORE:nblctrl_core_l2:nblon"'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_VMAX_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(setbin = -47, ret= 0, trialaction = "Exit"), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 2, trialaction = "Exit"),
                r3 = pPass(ret = 3, trialaction = "Exit"),
                r4 = pFail(setbin= -42, ret= 4, trialaction = "Exit"),
                r5 = pFail(setbin= -47, ret= 5, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(goto = "NEXT"),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(goto = "NEXT"),
                            r4 = pFail(setbin= -42, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
                             
    test_listt_atspeed_vmax_occ.append(sample_test_atspeed_vmax_occ)

    return test_listt_atspeed_vmax_occ
 
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
    NativeMultiTrial(name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_FREQ_ALLCORE",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_ALLCORE"',
                Patlist = f"scn_cdie_{flow.lower()}_occ_atspeed_ssn400_edt_classhvm_list" if "FMINXCR" in flow else f"scn_cdie_{flow.lower()}_occ_atspeed_ssn400_edt_classhvm_list_master",
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),                
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f"CR1@F1,CR0@F1" if "FMINXCR" in flow else Spec(f'__shared__::CornerIdentifiers.CR_{corner_id}'),
                DtsConfiguration = 'ALL_CDIE_C48_N2P_CORE',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL') if "F1XCR" in flow else Spec(f'__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
                ExecutionMode = "SearchWithScoreboard",
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = 'NOM_CCF_CORE',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                ForwardingMode = "Input" if "FMINXCR" in flow else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)') if "FMINXCR" in flow else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'SCN_CORE_AS',
                RecoveryMode = "NoRecovery" if "FMINXCR" in flow else "RecoveryPort",
                RecoveryOptions = "" if "FMINXCR" in flow else Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
                RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
                RecoveryTrackingOutgoing = "" if "FMINXCR" in flow else Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                SetPointsPlistMode = 'Local',
                LogLevel = "Disabled",
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}+")+'"GHz"') if "FMINXCR" in flow else Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                StartVoltages = Spec('__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")') if "FMINXCR" in flow else Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , "")'),
                StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")') if "FMINXCR" in flow else Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , "")'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                TestMode = 'MultiVmin',
                VoltageConverter = Spec(f'"--railconfigurations CDIE_CORE_NBLCTRL1 CDIE_CORE_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 2, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -42, ret= 4, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 5, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, goto= "NEXT") if "FMINXCR" in flow else pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, goto= "NEXT") if "FMINXCR" in flow else pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin = -47, goto= "NEXT") if "FMINXCR" in flow else pFail(setbin= -42, ret= 0),
                            r5 = pFail(setbin = -47, goto= "NEXT") if "FMINXCR" in flow else pFail(setbin= -47, ret= 0)))
            
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
    NativeMultiTrial(name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_FREQ_ALLCORE",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
                template = VminTC(name = f'"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.CR_{corner_id}") + f' + "_ALLCORE"',
                Patlist = f"scn_cdie_{flow.lower()}_occ_atspeed_ssn400_edt_classhvm_list_master",
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),                
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = TrialParamSpec(f'__shared__::CornerIdentifiers.CR_C5'),
                DtsConfiguration = "ALL_CDIE_C48_N2P_CORE",
                EndVoltageLimits = Spec('__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
                ExecutionMode = "SearchWithScoreboard",
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = 'NOM_CCF_CORE',
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f'__shared__::FlowMatrixSingular.FlowIndex'),
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                InitialMaskBits = '',
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                MaskPins = '',
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'SCN_CORE_AS',
                RecoveryMode = 'RecoveryPort', 
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
                RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
                RecoveryTrackingOutgoing = Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                SetPointsPlistMode = 'Local',
                LogLevel = "Disabled",
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FreqValues.CR_{corner_id}+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = TrialParamSpec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
                StartVoltagesOffset = TrialParamSpec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_CORE_NBLCTRL1 CDIE_CORE_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 2, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -42, ret= 4, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 5, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
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
    dcm,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat = []	
    sample_test_stuckat = \
        VminTC(name=f"STUCKAT_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_X_{corner}_M{dcm}",
               Patlist = '',#f'scn_cdie_{flow.lower()}_m{dcm}_allstuckat_ssn400_edt_classhvm_list', 
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'), 
               LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",               
               StartVoltages = '0.9',
               EndVoltageLimits = '0.9',
               ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
               FailCaptureCount = Spec("toInteger(999)"),
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               FivrCondition = 'NOM_CCF_CORE',
               ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
               InitialMaskBits = testinput.get("initialmaskbit", ""),
               MaskPins = '',
               PinMap = 'CORE_SCAN',
               RecoveryMode = 'RecoveryPort',
               RecoveryOptions = 'CLASS_NVL_S28C_6C',
               RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
               RecoveryTrackingOutgoing = Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
               SetPointsPlistMode = 'Local',
               LogLevel = "Disabled",
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
               StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
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
    dcm,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain = []	
    sample_test_chain = \
        VminTC(name=f"CHAIN_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_X_{corner}_M{dcm}",
               Patlist = f"scn_cdie_{flow.lower()}_m{dcm}_allchain_1hot_ssn400_edt_classhvm_list",
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),               
               LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",               
               EndVoltageLimits = '0.9', 
               ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
               FailCaptureCount = Spec("toInteger(999)"),
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               FivrCondition = 'NOM_CCF_CORE',
               ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
               InitialMaskBits = testinput.get("initialmaskbit", ""),
               MaskPins = '',
               PinMap = 'CORE1_SCAN,CORE0_SCAN',
               RecoveryMode = 'RecoveryPort',
               RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
               RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
               RecoveryTrackingOutgoing = Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
               SetPointsPlistMode = 'Local',
               LogLevel = "Disabled",
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
               #StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF1 , "")'),
               #StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               StartVoltages = '0.9',
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
               r1=pPass(ret=0),
               r2=pFail(setbin = -41, ret=0),
               r3=pPass(ret=0),
               r4=pFail(setbin = -42, ret=0),
               r5=pFail(setbin = -41, ret=0)))
    test_listt_chain.append(sample_test_chain)
    
    return test_listt_chain
    
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
        NativeMultiTrial(name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_FREQ_M{dcm}",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_M{dcm}"',
                Patlist = '',#f"scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list" if "FMINXCR" in flow else f"scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list_master",
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),                
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL') if "F1XCR" in flow else Spec(f'__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
                ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = 'NOM_CCF_CORE',
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                MaskPins = '',
                PinMap = 'CORE_SCAN',
                RecoveryMode = "" if "FMINXCR" in flow else "RecoveryPort",
                RecoveryOptions = "" if "FMINXCR" in flow else Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
                RecoveryTrackingIncoming = "" if "FMINXCR" in flow else Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
                RecoveryTrackingOutgoing = "" if "FMINXCR" in flow else Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = Spec(f'__shared__::CornerIdentifiers.CR_{corner_id}'),
                DtsConfiguration = 'ALL_CDIE_S28C' if "F4XCR" in flow else '',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f'__shared__::FlowMatrix.FlowIndex'),
                InitialMaskBits = testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)') if "FMINXCR" in flow else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistMode = 'Local',
                LogLevel = "Disabled",
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_CORE_NBLCTRL3 CDIE_CORE_NBLCTRL2 CDIE_CORE_NBLCTRL1 CDIE_CORE_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 1, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(goto= "NEXT"),
                            r1 = pPass(ret = 1),
                            r2 = pFail(goto= "NEXT"),
                            r3 = pPass(ret = 1),
                            r4 = pFail(goto= "NEXT"),
                            r5 = pFail(goto= "NEXT")))
                             
    test_listt_atspeed_f1f4_mtt.append(sample_test_atspeed_f1f4_mtt)

    return test_listt_atspeed_f1f4_mtt

def get_test_list_atspeed_fmin_mtt(
    flow, 
    corner, 
    dcm, 
    testinput,
    FlowMatrix,
    recoverytestflag=False
    ):
      
    # decode MTT test name
    test_listt_atspeed_fmin_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_fmin_mtt = \
        NativeMultiTrial(name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_FREQ_M{dcm}_MTT",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE",
                template = VminTC(name = f'"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_M{dcm}"',
                Patlist = '',#f"scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list",
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL'),
                ExecutionMode = "SearchWithScoreboard",
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = 'NOM_CCF_CORE',
                ForwardingMode = "Input",
                MaskPins = '',
                PinMap = 'CORE_SCAN',
                RecoveryMode = "NoRecovery",
                RecoveryOptions = "",
                RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
                RecoveryTrackingOutgoing = "" ,
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f"CR3@F1,CR2@F1,CR1@F1,CR0@F1",
                DtsConfiguration = '',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f'__shared__::FlowMatrix.FlowIndex'),
                InitialMaskBits = testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)') if "FMINXCR" in flow else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistMode = 'Local',
                LogLevel = "Disabled",
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_CORE_NBLCTRL3 CDIE_CORE_NBLCTRL2 CDIE_CORE_NBLCTRL1 CDIE_CORE_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 1, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -42, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, goto= "NEXT"),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, goto= "NEXT"),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -42, goto= "NEXT"),
                            r5 = pFail(setbin= -47, goto= "NEXT")))
                             
    test_listt_atspeed_fmin_mtt.append(sample_test_atspeed_fmin_mtt)

    return test_listt_atspeed_fmin_mtt

def get_test_list_atspeed_f5f6_mtt(
    flow, 
    corner, 
    dcm, 
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
        NativeMultiTrial(name = f"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_FREQ_M{dcm}",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
                template = VminTC(name = f'"ATSPEED_CORE_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::FreqInMHZ.CR_{corner_id}") + f' + "_M{dcm}"',
                Patlist = '',#f"scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list_master",
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500")'),                
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
                ExecutionMode = "Search" if "XCR" in flow else "SearchWithScoreboard",
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                FivrCondition = 'NOM_CCF_CORE',
                ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
                MaskPins = '',
                PinMap = 'CORE_SCAN',
                RecoveryMode = 'RecoveryPort',
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
                RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
                RecoveryTrackingOutgoing = Spec(f'__shared__::RecoveryTracker.OUTGOING_CR'),
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = TrialParamSpec(f'__shared__::CornerIdentifiers.CR_C5'),
                DtsConfiguration = 'ALL_CDIE_S28C',
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f'__shared__::FlowMatrixSingular.FlowIndex'),
                InitialMaskBits = testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistMode = 'Local',
                LogLevel = "Disabled",
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FreqValues.CR_{corner_id}+")+'"GHz"'),
                SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_CORE_NBLCTRL3 CDIE_CORE_NBLCTRL2 CDIE_CORE_NBLCTRL1 CDIE_CORE_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                                                       
                r0 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 1, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(goto = "NEXT"),
                            r1 = pPass(ret = 1),
                            r2 = pFail(goto = "NEXT"),
                            r3 = pPass(ret = 1),
                            r4 = pFail(goto = "NEXT"),
                            r5 = pFail(goto = "NEXT")))
                             
    test_listt_atspeed_f5f6_mtt.append(sample_test_atspeed_f5f6_mtt)

    return test_listt_atspeed_f5f6_mtt

def get_test_list_atspeed_fmin_raw(
    flow,
    corner,
    dcm,
    testinput,
    FlowMatrix
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_fmin_raw = []	
    sample_test_atspeed_fmin_raw = \
        VminTC(name=f"ATSPEED_CORE_SB_E_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_X_{corner}_FF_SEARCH_M{dcm}_RAW",
               Patlist = '',#f'scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list', 
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'), 
               LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",               
               EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL'),
               ExecutionMode = 'Search',
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               FivrCondition = 'NOM_CCF_CORE',
               ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
               InitialMaskBits = testinput.get("initialmaskbit", ""),
               MaskPins = '',
               PinMap = 'CORE_SCAN',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
               RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
               CornerIdentifiers = '',
               SetPointsPlistMode = 'Local',
               LogLevel = "Disabled",
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
               StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
               StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", "MultiVmin"),
               VoltageConverter = Spec(f'"--railconfigurations CDIE_CORE_NBLCTRL3 CDIE_CORE_NBLCTRL2 CDIE_CORE_NBLCTRL1 CDIE_CORE_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
               BypassPort = testinput.get("Bypassport", 1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(ret = 1),
               r1=pPass(ret=1),
               r2=pFail(ret = 1),
               r3=pPass(ret=1),
               r4=pFail(ret = 1),
               r5=pFail(ret = 1)))
    test_listt_atspeed_fmin_raw.append(sample_test_atspeed_fmin_raw)
    
    return test_listt_atspeed_fmin_raw

def get_test_list_atspeed_occ_fmin_raw(
    flow,
    corner,
    testinput,
    FlowMatrix
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_occ_fmin_raw = []	
    sample_test_atspeed_occ_fmin_raw = \
        VminTC(name=f"ATSPEED_CORE_SB_E_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_X_{corner}_FF_SEARCH_ALLCORE_RAW",
               Patlist = f"scn_cdie_{flow.lower()}_occ_atspeed_ssn400_edt_classhvm_list",
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'), 
               LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",     
               DtsConfiguration = 'ALL_CDIE_C48_N2P_CORE',
               EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL'),
               ExecutionMode = 'Search',
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               FivrCondition = 'NOM_CCF_CORE',
               ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
               InitialMaskBits = testinput.get("initialmaskbit", ""),
               MaskPins = '',
               PinMap = 'SCN_CORE_AS',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = Spec(f'__shared__::RecoveryTracker.INCOMING_CR'),
               RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
               CornerIdentifiers = '',
               SetPointsPlistMode = 'Local',
               LogLevel = "Disabled",
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}+")+'"GHz"'),
               SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
               StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
               StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", "MultiVmin"),
               VoltageConverter = Spec(f'"--railconfigurations CDIE_CORE_NBLCTRL1 CDIE_CORE_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CORE1,CORE0"),
               BypassPort = testinput.get("Bypassport", 1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(ret = 0),
               r1=pPass(ret=0),
               r2=pFail(ret = 0),
               r3=pPass(ret=0),
               r4=pFail(ret = 0),
               r5=pFail(ret = 0)))
    test_listt_atspeed_occ_fmin_raw.append(sample_test_atspeed_occ_fmin_raw)
    
    return test_listt_atspeed_occ_fmin_raw

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
        VminTC(name=f"ATSPEED_CORE_SB_E_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_X_{corner}_M{dcm}_RAW",
               Patlist = '',#f'scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list_master', 
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'), 
               LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",               
               EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
               ExecutionMode = 'Search',
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               FivrCondition = 'NOM_CCF_CORE',
               ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
               InitialMaskBits = testinput.get("initialmaskbit", ""),
               MaskPins = '',
               PinMap = 'CORE_SCAN',
               RecoveryMode = 'NoRecovery',
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
               CornerIdentifiers = f"CR{dcm}@F1" if "FMINXCR" in flow else f"CR{dcm}@{corner}",
               SetPointsPlistMode = 'Local',
               LogLevel = "Disabled",
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
               StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
               StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               StepSize = Spec("toDouble(0.01)"),
               TestMode = testinput.get("Testmode", "SingleVmin"),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
               VoltageTargets = testinput.get("Voltagetarget", "CORE0"),
               BypassPort = testinput.get("Bypassport", ""),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(ret = 1),
               r1=pPass(ret=1),
               r2=pFail(ret = 1),
               r3=pPass(ret=1),
               r4=pFail(ret = 1),
               r5=pFail(ret = 1)))
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
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    sample_test_atspeed_f5f6_apexmtt = ApexTC(
        name=f"ATSPEED_CORE_APEX_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_ALLCORE_APEX_FMAX",
        #exitaction="Restore",
        #trialvar="CPU_TRIALS::FlowDomain.Default",
        #template=ApexTC(
            #name=f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + '
                 #+ Spec(f"__shared__::CustomFlowMatrixSpecs.CR_{corner}_FREQ_MHz")+ f' + "_M{dcm}_APEX_MTT"',
            Patlist = f"scn_cdie_f5xcr_fmax_occ_atspeed_ssn400_edt_classhvm_list",
            LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",
            TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),
            #InitialMaskBits = testinput.get("initialmaskbit", ""),
            DtsConfiguration = "ALL_CDIE_C48_N2P_CORE",
            ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
            PinMap ='SCN_CORE_AS',
            RecoveryOptions = '',
            RecoveryTracking = 'CR1,CR0',
            End = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
            Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
            SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.{flow_matrix}+")+'"GHz,"' f'+' f'"CORE:nblctrl_core_l2:nbloff"') ,
            SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}+' f'","+' f'"CORE:nblctrl_core_l2:nblon"'),
            FivrCondition ="NOM_CCF_CORE",
            FivrConditionPlistParamName = "Patlist",
            StepSize = Spec("toInteger(1)"),
            VoltageConverter = Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
            ExportTokens= Spec(f'__shared__::APEX_Tokens.CRToken'),
            Targets= testinput.get("targets", "SCORE1,SCORE0"),
            BypassPort=testinput.get("Bypassport", Spec(f"__shared__::TpRule.If_DS0_DS1_M(1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)")),
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

def get_test_list_atspeed_f5f6_apexmtt_multipass(
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id,
    multipass_id,
    recoverytestflag=False
    ):
    test_listt_atspeed_f5f6_apexmtt_multipass = []
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    sample_test_atspeed_f5f6_apexmtt_multipass = ApexTC(
        name=f"ATSPEED_CORE_APEX_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_{multipass_id}",
        #exitaction="Restore",
        #trialvar="CPU_TRIALS::FlowDomain.Default",
        #template=ApexTC(
            #name=f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + '
                 #+ Spec(f"__shared__::CustomFlowMatrixSpecs.CR_{corner}_FREQ_MHz")+ f' + "_M{dcm}_APEX_MTT"',
            Patlist = f"scn_cdie_f5xcr_fmax_occ_atspeed_ssn400_edt_classhvm_list",
            LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",            
            TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),            
            #InitialMaskBits = testinput.get("initialmaskbit", ""),
            DtsConfiguration = "ALL_CDIE_C48_N2P_CORE",
            ForwardingMode = "Input" if testinput["ISEDC"] else "InputOutput",
            InitialMaskBits = testinput.get("maskbit", ""),
            PinMap ='SCN_CORE_AS',
            RecoveryOptions = '',
            RecoveryTracking = 'CR',
            End = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
            Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
            SetPointsPreInstance = testinput.get("setpointfreq", ""),
            SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}+' f'","+' f'"CORE:nblctrl_core_l2:nblon"'),
            FivrCondition ="NOM_CCF_CORE",
            FivrConditionPlistParamName = "Patlist",
            StepSize = Spec("toInteger(1)"),
            VoltageConverter = Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
            ExportTokens= Spec(f'__shared__::APEX_Tokens.CRToken'),
            Targets= testinput.get("targets", "SCORE1,SCORE0"),
            BypassPort=testinput.get("Bypassport", Spec(f"__shared__::TpRule.If_DS0_DS1_M(1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)")),
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
    test_listt_atspeed_f5f6_apexmtt_multipass.append(sample_test_atspeed_f5f6_apexmtt_multipass)
    return test_listt_atspeed_f5f6_apexmtt_multipass
    
######################
#   SPOFI TESTS IO  #
###################################################################################################### 

def get_test_list_spofi(
    flow,
    corner,
    dcm,
    testinput,
    test_type
    ):
    # Create an empty list that will contain the final list of the test
    test_list_spofi = []

    # Define the test parameters based on the test type
    test_params = {
        "STUCKAT": {
            "name": f"STUCKAT_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_X_{corner}_M{dcm}",
            "patlist": '',#f'scn_cdie_{flow.lower()}_m{dcm}_allstuckat_ssn400_edt_classhvm_list',
            "setbin": -42
        },
        "ATSPEED": {
            "name": f"ATSPEED_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_X_{corner}_M{dcm}",
            "patlist": '',#f'scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list',
            "setbin": -47
        },
        "CHAIN": {
            "name": f"CHAIN_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_X_{corner}_M{dcm}",
            "patlist": f'scn_cdie_{flow.lower()}_m{dcm}_allchain_1hot_ssn400_edt_classhvm_list',
            "setbin": -41,
            "goto": f"DIAG_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_{corner}_M{dcm}"
        },
        "DIAG": {
            "name": f"DIAG_CORE{dcm}_SPOFI_E_{flow}_X_X_NOM_X_{corner}_M{dcm}",
            "patlist": '',#f'scn_cdie_{flow.lower()}_m{dcm}_allchain_proxy_ssn400_edt_classhvm_list',
            "setbin": -41
        }
    }

    # Get the parameters for the specified test type
    params = test_params.get(test_type)

    if params:
        sample_test_spofi = PrimeScanSPOFITestMethod(
            name=params["name"],
            Patlist=params["patlist"],
            TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),            
            LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",            
            PerPatternFailCaptureCount=1000,
            TotalFailCaptureCount=5000,
            BypassPort=testinput.get("Bypassport", -1),
            _fitem=Fitem('SAME',
                         edc=testinput.get("ISEDC"),
                         r0=pFail(setbin=params["setbin"], ret=0),
                         r1=pPass(ret=0),
                         r2=pFail(setbin=params["setbin"], ret=0))
        )

        test_list_spofi.append(sample_test_spofi)

    return test_list_spofi


#####################
#   SHMOO TESTS IO   #
######################################################################################################
def get_test_list_IO_shmoodata(
    flow, 
    corner, 
    dcm,
    testype,
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_IO_shmoo = []
    sample_test_IO_shmoo = DDGShmooTC(name = f"{testype}_CORE{dcm}_SHMOO_E_BEGINCPU_X_X_{corner}_X_M{dcm}_{flow}_SHMOODATA",
                _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
                Patlist = testinput.get("pattlist", ""),
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),                
                ApplyEndSequence = 'DISABLED',
                #ExecutionMode = 'Allpin',
                SetPointsPlistParamName = "Patlist",
                SetPointsPreInstance = Spec(f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_FMIN+")+'"GHz"') if "FMINXCR" in flow else Spec(f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
                SetPointsPlistMode = 'Local',
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE"'),
                PrintFormat = "ShmooHub",
                PowerDownBetweenPoints = 'DISABLED',
                #PlotMode = 'Normal',
                XAxisType = "SpecSetVariable",
                XAxisDatalogPrefix = 'Base',
                XAxisParam = 'all_mts',
                XAxisParamType = 'UserDefined',
                XAxisRange = "1100e6:100e6:5",
                YAxisType = 'FIVR',
                YAxisDatalogPrefix = 'Base',
                YAxisParam = f'CORE{dcm}',
                YAxisParamType = "UserDefined",
                YAxisRange = '1.3:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto = "NEXT"),
                r1=pPass(goto = "NEXT"),
                r2=pFail(goto = "NEXT")))      
    test_listt_IO_shmoo.append(sample_test_IO_shmoo)
    
    return test_listt_IO_shmoo

def get_test_list_occ_shmoodata(
    flow, 
    corner,
    testtype,
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_atspeedocc_shmoo = []
    sample_test_atspeedocc_shmoo = DDGShmooTC(name = f"{testtype}_CORE_SHMOO_E_BEGINCPU_X_X_{corner}_X_ALLCORE_{flow}_SHMOODATA",
                _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
                Patlist = testinput.get("pattlist", ""),
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),                
                ApplyEndSequence = 'DISABLED',
                #ExecutionMode = 'Allpin',
                SetPointsPlistParamName = "Patlist",
                SetPointsPreInstance = Spec(f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_FMIN+")+'"GHz"') if "FMINXCR" in flow else Spec(f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
                SetPointsPlistMode = 'Local',
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE"'),
                PrintFormat = "ShmooHub",
                PowerDownBetweenPoints = 'DISABLED',
                #PlotMode = 'Normal',
                XAxisType = "SpecSetVariable",
                XAxisDatalogPrefix = 'Base',
                XAxisParam = 'all_mts',
                XAxisParamType = 'UserDefined',
                XAxisRange = '1100e6:100e6:5',
                YAxisType = 'FIVR',
                YAxisDatalogPrefix = 'Base',
                YAxisParam = f'CORE1,CORE0',
                YAxisParamType = "UserDefined",
                YAxisRange = '1.3:-0.1:10',
                LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto = "NEXT"),
                r1=pPass(goto = "NEXT"),
                r2=pFail(goto = "NEXT")))
               
    test_listt_atspeedocc_shmoo.append(sample_test_atspeedocc_shmoo)
    
    return test_listt_atspeedocc_shmoo
    
def get_test_list_atspeed_shmoo(
    flow, 
    corner, 
    dcm, 
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_atspeed_shmoo = []
    sample_test_atspeed_shmoo = DDGShmooTC(name = f"ATSPEED_CORE{dcm}_SHMOO_E_{flow}_X_X_NOM_M{dcm}",
                Patlist = '',#f'scn_cdie_{flow.lower()}_m{dcm}_allatspeed_ssn400_edt_classhvm_list_master',
                LevelsTc = "SCN_CORE_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNCORE_OVERRIDE_nom",                
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48OVERRIDE1500","SCN_CORE_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_N2P48S16COVERRIDE1500")'),                
                SetPointsPlistParamName = "Patlist",
                SetPointsPreInstance = Spec(f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                PrintFormat = "ShmooHub",
                XAxisType = "SpecSetVariable",
                XAxisDatalogPrefix = 'Nano',
                XAxisParam = 'all_mts',
                XAxisParamType = 'UserDefined',
                XAxisRange = '0.98:0.01:4',
                YAxisType = 'FIVR',
                YAxisParam = f'CORE{dcm}',
                YAxisParamType = "UserDefined",
                YAxisRange = '0.5:0.02:52',
                LogLevel = '',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail( goto = "NEXT"),
                r1=pPass(ret=1),
                r2=pFail(goto = "NEXT")))
               
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
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/SCN/{MODULE}/InputFiles/dummy.setpoints.json"'),
               SetPoint = "scancoredummy",
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
               Parameters = f"--decoder AnyFailSingleSliceDecoder --file ./Modules/SCN/SCN_CORE_CX48/Inputfiles/DieRecoveryPinMaps_IO_NVL_SCNCORE.json",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
               r1=pPass(goto="NEXT")))
    test_listt_callback.append(sample_test_callback)
    
    return test_listt_callback

def get_test_pinmap_parse_occ_sa(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_callback = []	
    sample_test_callback = \
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_PINMAP_SCN_PRIME_OCCSA_DIERECOVERY",
               Callback = "LoadPinMapFile",
               Parameters = f"--decoder FailDataDecoder --file ./Modules/SCN/SCN_CORE_CX48/InputFiles/DieRecoveryPinMaps_OCC_NVL_SCNCORE_N2P.json",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
               r1=pPass(goto="NEXT")))
    test_listt_callback.append(sample_test_callback)
    
    return test_listt_callback

def get_test_pinmap_parse_occ_as(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_callback = []	
    sample_test_callback = \
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_PINMAP_SCN_PRIME_OCCAS_DIERECOVERY",
               Callback = "LoadPinMapFile",
               Parameters = f"--decoder FailDataDecoder --file ./Modules/SCN/SCN_CORE_CX48/InputFiles/DieRecoveryPinMaps_OCC_NVL_AS_SCNCORE_N2P.json",
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
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_SCNCORE_APEXTC",
               Callback = "ReadFrequencyPatConfigFile",
               Parameters = Spec(f'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/SCN/SCN_CORE_CX48/InputFiles/ApexTC_Input_Config_N2P.json"'),
               BypassPort = testinput.get("Bypassport", Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)")),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, ret=0),
               r1=pPass(goto="NEXT")))
    test_listt_apextc_init.append(sample_test_apextc_init)
    
    return test_listt_apextc_init
    
#################################################################################
#							INIT SUBFLOW
#
#	- INIT flow will have pinmap & dierecovery related tests in 
#
#################################################################################
init_flow = "INIT"

init_patmod_tli = { "ISEDC": True}
init_patmod = get_test_globalinit_patmod(init_flow, init_patmod_tli)

pinmap_parse_tli = {"ISEDC": True}
pinmap_parse = get_test_pinmap_parse(init_flow, pinmap_parse_tli)

pinmap_parse_occsa_tli = {"ISEDC": True}
pinmap_parse_occsa = get_test_pinmap_parse_occ_sa(init_flow, pinmap_parse_occsa_tli)

pinmap_parse_occas_tli = {"ISEDC": True}
pinmap_parse_occas = get_test_pinmap_parse_occ_as(init_flow, pinmap_parse_occas_tli)

apextc_init_tli = {"Bypassport": -1, "ISEDC": True}
apextc_init = get_test_apextc_init(init_flow, apextc_init_tli)

#INIT SUBFLOW
INIT_SUBFLOW = Flow(f'{MODULE}_INIT',
                                init_patmod,
                                pinmap_parse,
                                pinmap_parse_occsa,
                                pinmap_parse_occas,
                                apextc_init,
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
begincpu_vmintc_stuckat_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
begincpu_vmintc_stuckat_occ = get_test_list_stuckat_occ(begincpu_flow, begincpu_corner, begincpu_vmintc_stuckat_occ_tli)

# ScreenTC
begincpu_screentc_tli = {"Bypassport": 1, "ISEDC": True}
begincpu_screentc = get_test_list_screentc(begincpu_flow, begincpu_screentc_tli)


# Function to create test lists and flows for each module
def create_module_flow(module_index, module_name):
   # Define TLI settings for each module
    vmintc_chain_tli = {
        "Bypassport": -1,
        "Testmode": "MultiVmin",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": initial_maskbit[module_name],
        "ISEDC": False,
        "Preinstance": ""
    }
    vmintc_stuckat_tli = {
        "Bypassport": 1,
        "Testmode": "MultiVmin",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": initial_maskbit[module_name],
        "ISEDC": False,
        "Preinstance": ""
    }
    
    vmintc_stuckat = get_test_list_stuckat(begincpu_flow, begincpu_corner, module_index, vmintc_stuckat_tli)

    vmintc_chain = get_test_list_chain(begincpu_flow, begincpu_corner, module_index, vmintc_chain_tli)
    
    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True}
    spofi_stuckat = get_test_list_spofi(begincpu_flow, begincpu_corner, module_index, spofi_stuckat_tli, "STUCKAT")
    
    return Flow(f"BEGINCPU_{module_name}", vmintc_chain)#, spofi_stuckat) #vmintc_stuckat)

# Create flows for each module
module_flows = [create_module_flow(i, module) for i, module in enumerate(DCM_MODULES)]

#shmoo test##
##IOSHMOO
##stuckat shmoo
testype_sa = "STUCKAT"
SHMOO_STUCKAT_TLI = {"Bypassport": 1, "ISEDC": True}
stuckat_shmoo = [
    get_test_list_IO_shmoodata(begincpu_flow, begincpu_corner, dcm, testype_sa, SHMOO_STUCKAT_TLI)
    for dcm in range (2)  
]

#chain shmoo
testype_chain = "CHAIN"
SHMOO_CHAIN_TLI = {"Bypassport": 1, "pattlist": "scn_cdie_begincpu_m0_allchain_1hot_ssn400_edt_classhvm_list", "ISEDC": True}
chain_shmoo = [
    get_test_list_IO_shmoodata(begincpu_flow, begincpu_corner, dcm, testype_chain, SHMOO_CHAIN_TLI)
    for dcm in range (2)
 ]

#atspeed shmoo
#FMIN
fminxcr_flow = "FMINXCR"
testype_as = "ATSPEED"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_fmin_shmoo = [
    get_test_list_IO_shmoodata(fminxcr_flow, begincpu_corner, dcm, testype_as, SHMOO_ATSPEED_TLI)
    for dcm in range (2)
 ]

#F1
f1xcr_flow = "F1XCR"
testype_as = "ATSPEED"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_shmoo = [
    get_test_list_IO_shmoodata(f1xcr_flow, begincpu_corner, dcm, testype_as, SHMOO_ATSPEED_TLI)
    for dcm in range (2)
 ]

STUCKAT_CHAIN_ATSPEED_F1 = Flow("F1_SHMOO", *stuckat_shmoo, *chain_shmoo, *atspeed_shmoo, *atspeed_fmin_shmoo)

#F2
f2xcr_flow = "F2XCR"
f2xcr_corner = "F2"
SHMOO_F2_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_shmoo_f2 = [
    get_test_list_IO_shmoodata(f2xcr_flow, f2xcr_corner, dcm, testype_as, SHMOO_F2_ATSPEED_TLI)
    for dcm in range (2)
 ]

ATSPEED_F2 = Flow("F2_SHMOO", *atspeed_shmoo_f2)

#F3
f3xcr_flow = "F3XCR"
f3xcr_corner = "F3"
SHMOO_F3_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_shmoo_f3 = [
    get_test_list_IO_shmoodata(f3xcr_flow, f3xcr_corner, dcm, testype_as, SHMOO_F3_ATSPEED_TLI)
    for dcm in range (2)
 ]

ATSPEED_F3 = Flow("F3_SHMOO", *atspeed_shmoo_f3)

#F4
f4xcr_flow = "F4XCR"
f4xcr_corner = "F4"
SHMOO_F4_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_shmoo_f4 = [
    get_test_list_IO_shmoodata(f4xcr_flow, f4xcr_corner, dcm, testype_as, SHMOO_F4_ATSPEED_TLI)
    for dcm in range (2)
 ]

ATSPEED_F4 = Flow("F4_SHMOO", *atspeed_shmoo_f4)

#F5
f5xcr_flow = "F5XCR"
f5xcr_corner = "F5"
SHMOO_F5_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_shmoo_f5 = [
    get_test_list_IO_shmoodata(f5xcr_flow, f5xcr_corner, dcm, testype_as, SHMOO_F5_ATSPEED_TLI)
    for dcm in range (2)
 ]

ATSPEED_F5 = Flow("F5_SHMOO", *atspeed_shmoo_f5)

#F6
f6xcr_flow = "F6XCR"
f6xcr_corner = "F6"
SHMOO_F6_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_shmoo_f6 = [
    get_test_list_IO_shmoodata(f5xcr_flow, f6xcr_corner, dcm, testype_as, SHMOO_F6_ATSPEED_TLI)
    for dcm in range (2)
 ]

ATSPEED_F6 = Flow("F6_SHMOO", *atspeed_shmoo_f6)

#F7
f7xcr_flow = "F7XCR"
f7xcr_corner = "F7"
SHMOO_F7_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
atspeed_shmoo_f7 = [
    get_test_list_IO_shmoodata(f5xcr_flow, f7xcr_corner, dcm, testype_as, SHMOO_F7_ATSPEED_TLI)
    for dcm in range (2)
 ]

ATSPEED_F7 = Flow("F7_SHMOO", *atspeed_shmoo_f7)

#OCC shmoo block
testtype_sa = "STUCKAT"
SHMOO_F1_STUCKATOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_begincpu_occ_stuckat_ssn400_edt_classhvm_list"}
F1_stuckat = get_test_list_occ_shmoodata(begincpu_flow, begincpu_corner, testtype_sa, SHMOO_F1_STUCKATOCC_TLI)

fminxcr_flow = "FMINXCR"
testtype_as = "ATSPEED"
SHMOO_FMIN_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_fminxcr_occ_atspeed_ssn400_edt_classhvm_list"}
FMIN_atspeed = get_test_list_occ_shmoodata(fminxcr_flow, begincpu_corner, testtype_as, SHMOO_FMIN_ATSPEEDOCC_TLI)

#RATIO4 Patmod
patmod_state_disable = "DISABLEE"
ratio4_disable_tli = {"Bypassport": -1, "setpoint": "enable_fmin_400_throttle_done_detected_core", "ISEDC": True }
patmod_ratio4_disable = get_test_list_patconfig_ratio4_shmoo(fminxcr_flow, ratio4_disable_tli, patmod_state_disable)

patmod_state_enable = "ENABLEE"
ratio4_enable_tli = {"Bypassport": -1, "setpoint": "disable_fmin_400_throttle_done_detected_core", "ISEDC": True }
patmod_ratio4_enable = get_test_list_patconfig_ratio4_shmoo(fminxcr_flow, ratio4_enable_tli, patmod_state_enable)


SHMOO_F1_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_f1xcr_occ_atspeed_ssn400_edt_classhvm_list_master"}
F1_atspeed = get_test_list_occ_shmoodata(f1xcr_flow, begincpu_corner, testtype_as, SHMOO_F1_ATSPEEDOCC_TLI)

SHMOO_F2_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_f2xcr_occ_atspeed_ssn400_edt_classhvm_list_master"}
F2_atspeed = get_test_list_occ_shmoodata(f2xcr_flow, f2xcr_corner, testtype_as, SHMOO_F2_ATSPEEDOCC_TLI)

SHMOO_F3_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_f3xcr_occ_atspeed_ssn400_edt_classhvm_list_master"}
F3_atspeed = get_test_list_occ_shmoodata(f3xcr_flow, f3xcr_corner, testtype_as, SHMOO_F3_ATSPEEDOCC_TLI)

SHMOO_F4_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_f4xcr_occ_atspeed_ssn400_edt_classhvm_list_master"}
F4_atspeed = get_test_list_occ_shmoodata(f4xcr_flow, f4xcr_corner, testtype_as, SHMOO_F4_ATSPEEDOCC_TLI)

SHMOO_F5_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_f5xcr_occ_atspeed_ssn400_edt_classhvm_list_master"}
F5_atspeed = get_test_list_occ_shmoodata(f5xcr_flow, f5xcr_corner, testtype_as, SHMOO_F5_ATSPEEDOCC_TLI)

SHMOO_F6_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_f5xcr_occ_atspeed_ssn400_edt_classhvm_list_master"}
F6_atspeed = get_test_list_occ_shmoodata(f5xcr_flow, f6xcr_corner, testtype_as, SHMOO_F6_ATSPEEDOCC_TLI)

SHMOO_F7_ATSPEEDOCC_TLI = {"Bypassport": 1, "ISEDC": True, "pattlist": "scn_cdie_f5xcr_occ_atspeed_ssn400_edt_classhvm_list_master"}
F7_atspeed = get_test_list_occ_shmoodata(f5xcr_flow, f7xcr_corner, testtype_as, SHMOO_F7_ATSPEEDOCC_TLI)

OCC_SHMOO_block = Flow("OCC_SHMOO", F1_stuckat, patmod_ratio4_disable, FMIN_atspeed, patmod_ratio4_enable, F1_atspeed, F2_atspeed, F3_atspeed, F4_atspeed, F5_atspeed, F6_atspeed, F7_atspeed)


SHMOO_COMPOSITE = Flow("SHMOO", 
                       Fitem("SAME", STUCKAT_CHAIN_ATSPEED_F1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       Fitem("SAME", ATSPEED_F2, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       Fitem("SAME", ATSPEED_F3, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       Fitem("SAME", ATSPEED_F4, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       Fitem("SAME", ATSPEED_F5, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       Fitem("SAME", ATSPEED_F6, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       Fitem("SAME", ATSPEED_F7, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       Fitem("SAME", OCC_SHMOO_block, r0=pFail(ret=0), r1=pPass(goto="NEXT")))

# BEGINCPU SUBFLOW
BEGINCPU_SUBFLOW = Flow(f'{MODULE}_BEGINCPU',
                     begincpu_vmintc_stuckat_occ,
                     #begincpu_vmintc_stuckat_occ_ret,
                     #Fitem("SAME", begincpu_occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     #begincpu_screentc,
                     *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                     Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)),
                     Fitem("SAME", SHMOO_COMPOSITE, r0=pFail(ret=0), r1=pPass(goto="NEXT")))
##Fitem("SAME", SHMOO_COMPOSITE, r0=pFail(ret=0), r1=pPass(goto="NEXT")) --> add this line for shmmo block

#################################################################################
#                           FMINXCR SUBFLOW
#
#  -Fmin test point using F1 vmin as test point 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CR_FMIN_MHz"   : "0400"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "FMIN": "CR_FMIN"
    }

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "MultiVmin",
        "executionmode": "SearchWithScoreboard",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": initial_maskbit[module_name],
        "ISEDC": True,
        "Recovery": "RecoveryPort",
        "Preinstance": ""
    }
    
    vmintc_atspeed = get_test_list_atspeed_fmin_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix)
    
    #raw vmintc
    vmintc_atspeed_raw_tli = {"Bypassport": 1, "initialmaskbit": initial_maskbit[module_name], "ISEDC": True}
    vmintc_atspeed_raw = get_test_list_atspeed_fmin_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed)

    
# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    
    vmintc_atspeed_occ_raw_tli = {"Bypassport": -1, "ISEDC": True}
    vmintc_atspeed_occ_raw = get_test_list_atspeed_occ_fmin_raw(flow_name, corner, vmintc_atspeed_occ_raw_tli, flow_matrix)
    occ = Flow(f"{flow_name}_ALLCORE", vmintc_atspeed_occ, vmintc_atspeed_occ_raw)
    
    #RATIO4 Patmod
    patmod_state_disable = "DISABLE"
    ratio4_disable_tli = {"Bypassport": -1, "setpoint": "enable_fmin_400_throttle_done_detected_core", "ISEDC": True }
    patmod_ratio4_disable = get_test_list_patconfig_ratio4(flow_name, ratio4_disable_tli, patmod_state_disable)

    patmod_state_enable = "ENABLE"
    ratio4_enable_tli = {"Bypassport": -1, "setpoint": "disable_fmin_400_throttle_done_detected_core", "ISEDC": True }
    patmod_ratio4_enable = get_test_list_patconfig_ratio4(flow_name, ratio4_enable_tli, patmod_state_enable)
                    
    # Create flows for each module
    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix) for i, module in enumerate(DCM_MODULES)]
    
    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   patmod_ratio4_disable,
                   Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto=f'CTRL_X_PATMOD_K_FMINXCR_X_X_X_X_RESET_RATIO4_ENABLE')),
                   *[Fitem("SAME", module_flow, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                   patmod_ratio4_enable)
    
    return subflow

# Define the subflows
subflows = []
flow_name = "FMINXCR"
corner = "FMIN"
flow_matrix = flow_matrix_definitions[corner]
subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix))

                     
#################################################################################
#                           F1F4 X CR SUBFLOW
#
#   - Consists of F1 through F4 corners flow which will test 100% ATSPEED content 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CR_F1_FREQ_MHz": "1200",
    "CR_F2_FREQ_MHz": "1500",
    "CR_F3_FREQ_MHz": "2400",
    "CR_F4_FREQ_MHz": "3500"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "CR_F1_FREQ",
    "F2": "CR_F2_FREQ",
    "F3": "CR_F3_FREQ",
    "F4": "CR_F4_FREQ"
}

corner_id_definitions = {
    "F1": "C1",
    "F2": "C2",
    "F3": "C3",
    "F4": "C4",
}

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "MultiVmin",
        "executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": initial_maskbit[module_name],
        "ISEDC": True,
        "Recovery": "RecoveryPort",
        "Preinstance": ""
    }
    
    vmintc_atspeed_edc_tli = {"Bypassport": 1, "initialmaskbit": initial_maskbit[module_name], "ISEDC": True}
    
    vmintc_atspeed = get_test_list_atspeed_f1f4_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id)
    
    #raw vmintc
    vmintc_atspeed_raw_tli = {"Bypassport": 1, "initialmaskbit": initial_maskbit[module_name], "ISEDC": True}
    vmintc_atspeed_raw = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    shmoo_atspeed = get_test_list_atspeed_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all. 
    
    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_spofi(flow_name, corner, module_index, spofi_atspeed_tli, "ATSPEED")  

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_spofi(flow_name, corner, module_index, spofi_stuckat_tli, "STUCKAT") 
	
    #return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, shmoo_atspeed, spofi_atspeed, spofi_stuckat)
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, vmintc_atspeed_raw)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    #occ = Flow(f"{flow_name}_ALLCORE", vmintc_atspeed_occ)
                    
    # Create flows for each module
    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(DCM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   #Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                   vmintc_atspeed_occ,
                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)))
    return subflow

# Define the subflows
subflows = []
for i in range(1, 4):
    flow_name = f"F{i}XCR"
    corner = f"F{i}"
    flow_matrix = flow_matrix_definitions[corner]
    corner_id = corner_id_definitions[corner]
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id))

#################################################################################
#                           F4 X CRLO SUBFLOW
#
#   - Consists of F4 corners flow which will test 100% ATSPEED content 100c
#
#################################################################################
# FlowMatrixRule Definition
FlowMatrixRule = {
    "CR_F1_FREQ_MHz": "1200",
    "CR_F2_FREQ_MHz": "1500",
    "CR_F3_FREQ_MHz": "2400",
    "CR_F4_FREQ_MHz": "3500"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "CR_F1_FREQ",
    "F2": "CR_F2_FREQ",
    "F3": "CR_F3_FREQ",
    "F4": "CR_F4_FREQ"
}

corner_id_definitions = {
    "F1": "C1",
    "F2": "C2",
    "F3": "C3",
    "F4": "C4",
}

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli_f4xcrlo = {
        "Bypassport": 1,
        "Testmode": "MultiVmin",
        "executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": initial_maskbit[module_name],
        "ISEDC": True,
        "Recovery": "RecoveryPort",
        "Preinstance": ""
    }
    
    vmintc_atspeed_edc_tli_f4xcrlo = {"Bypassport": 1, "initialmaskbit": initial_maskbit[module_name], "ISEDC": True}
    
    vmintc_atspeed_f4xcrlo = get_test_list_atspeed_f1f4_mtt(flow_name, corner, module_index, vmintc_atspeed_tli_f4xcrlo, flow_matrix, corner_id)
    
    #raw vmintc
    vmintc_atspeed_raw_tli_f4xcrlo = {"Bypassport": 1, "initialmaskbit": initial_maskbit[module_name], "ISEDC": True}
    vmintc_atspeed_raw_f4xcrlo = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli_f4xcrlo, flow_matrix)
    
    shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    shmoo_atspeed = get_test_list_atspeed_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all. 
    
    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_spofi(flow_name, corner, module_index, spofi_atspeed_tli, "ATSPEED")  

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_spofi(flow_name, corner, module_index, spofi_stuckat_tli, "STUCKAT") 
	
    #return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, shmoo_atspeed, spofi_atspeed, spofi_stuckat)
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed_f4xcrlo, vmintc_atspeed_raw_f4xcrlo)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli_f4xcrlo = {"Bypassport": -1, "ISEDC": False}
    vmintc_atspeed_occ_f4xcrlo = get_test_list_atspeed_occ_f1f4_mtt(flow_name, corner, vmintc_atspeed_occ_tli_f4xcrlo, flow_matrix)
    #occ = Flow(f"{flow_name}_ALLCORE", vmintc_atspeed_occ_f4xcrlo)
                    
    # Create flows for each module
    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(DCM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   #Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                   vmintc_atspeed_occ_f4xcrlo,
                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)))
    return subflow

# Define the subflows
subflows = []
flow_name = "F4XCRLO"
corner = "F4"
flow_matrix = flow_matrix_definitions[corner]
corner_id = corner_id_definitions[corner]
subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id))


#################################################################################
#                           F5F6 X CR SUBFLOW
#
#   - Consists of F5 & F6 corners flow which will test 100% ATSPEED content in TOP subflow 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CR_F5_FREQ_MHz": "3600",
    "CR_F6_FREQ_MHz": "4000",
    "CR_F7_FREQ_MHz": "4300"
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CR_F5_FREQ",
    "F6": "CR_F6_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
    "F6": "C6",
}

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "MultiVmin",
        "executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": initial_maskbit[module_name],
        "ISEDC": True,
        "Recovery": "RecoveryPort",
        "Preinstance": ""
    }
    
    vmintc_atspeed = get_test_list_atspeed_f5f6_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id)
    #raw vmintc
    vmintc_atspeed_raw_tli = {"Bypassport": 1, "initialmaskbit": initial_maskbit[module_name], "ISEDC": True}
    vmintc_atspeed_raw = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    shmoo_atspeed = get_test_list_atspeed_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
    
    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_spofi(flow_name, corner, module_index, spofi_atspeed_tli, "ATSPEED")                                                                                                

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_spofi(flow_name, corner, module_index, spofi_stuckat_tli, "STUCKAT")                                                                                               
	
	#return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, shmoo_atspeed, spofi_atspeed, spofi_stuckat)
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, vmintc_atspeed_raw)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f5f6_mtt(flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix, corner_id)
    #occ = Flow(f"{flow_name}_ALLCORE", vmintc_atspeed_occ)

    apextc_tli = {"Bypassport": 1, "ISEDC": True}
    apextc = get_test_list_atspeed_f5f6_apexmtt(flow_name, corner, apextc_tli, flow_matrix, corner_id)

    m0m1 = "X_ALLCORE_1100_APEX_FMAX"
    apextc_1100_tli = {"Bypassport": 1, "maskbit":"1100", "setpointfreq": Spec(f"SCN_CORE_CX816_apexsetpoint_Specs.apexsetpoint_1100"), "ISEDC": True}
    apextc_1100 = get_test_list_atspeed_f5f6_apexmtt_multipass(flow_name, corner, apextc_1100_tli, flow_matrix, corner_id, m0m1)

    m2m3 = "X_ALLCORE_0011_APEX_FMAX"
    apextc_0011_tli = {"Bypassport": 1, "maskbit":"0011", "setpointfreq": Spec(f"SCN_CORE_CX816_apexsetpoint_Specs.apexsetpoint_0011"), "ISEDC": True}
    apextc_0011 = get_test_list_atspeed_f5f6_apexmtt_multipass(flow_name, corner, apextc_0011_tli, flow_matrix, corner_id, m2m3)

    #apextc_multipass_composite = Flow("FMAX_MULTIPASS_F5XCRLO", apextc_1100, apextc_0011)
          
    # Create flows for each module
    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(DCM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   #Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                   #apextc,
                   #Fitem("SAME", apextc_multipass_composite, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                   #vmintc_atspeed_occ,
                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(ret=0), ))
    
    return subflow

# Define the subflows for F5 and F6, only F5 enabled for now
subflows = []
for corner in ["F5"]:
    flow_name = f"{corner}XCR"
    flow_matrix = flow_matrix_definitions[corner]
    corner_id = corner_id_definitions[corner]
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id))

#################################################################################
#                           F5F6 X CRLO SUBFLOW
#
#   - Consists of F5 & F6 corners flow which will test 100% ATSPEED content in TOP subflow 100c
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CR_F5_FREQ_MHz": "3600",
    "CR_F6_FREQ_MHz": "4000",
    "CR_F7_FREQ_MHz": "4300"
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CR_F5_FREQ",
    "F6": "CR_F6_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
    "F6": "C6",
}

# Function to create test lists and flows for each module
def create_module_flow(flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "MultiVmin",
        "executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": initial_maskbit[module_name],
        "ISEDC": True,
        "Recovery": "RecoveryPort",
        "Preinstance": ""
    }
    
    vmintc_atspeed = get_test_list_atspeed_f5f6_mtt(flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id)
    #raw vmintc
    vmintc_atspeed_raw_tli = {"Bypassport": 1, "initialmaskbit": initial_maskbit[module_name], "ISEDC": True}
    vmintc_atspeed_raw = get_test_list_atspeed_raw(flow_name, corner, module_index, vmintc_atspeed_raw_tli, flow_matrix)
    
    shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    shmoo_atspeed = get_test_list_atspeed_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
    
    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_spofi(flow_name, corner, module_index, spofi_atspeed_tli, "ATSPEED")                                                                                                

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_spofi(flow_name, corner, module_index, spofi_stuckat_tli, "STUCKAT")                                                                                               
	
	#return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, shmoo_atspeed, spofi_atspeed, spofi_stuckat)
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed, vmintc_atspeed_raw)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli_f5xcrlo = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ_f5xcrlo = get_test_list_atspeed_occ_f5f6_mtt(flow_name, corner, vmintc_atspeed_occ_tli_f5xcrlo, flow_matrix, corner_id)
    #occ = Flow(f"{flow_name}_ALLCORE", vmintc_atspeed_occ)

    apextc_tli_f5xcrlo = {"Bypassport": 1, "ISEDC": True}
    apextc_f5xcrlo = get_test_list_atspeed_f5f6_apexmtt(flow_name, corner, apextc_tli_f5xcrlo, flow_matrix, corner_id)

    m0m1_f5xcrlo = "X_ALLCORE_1100_APEX_FMAX"
    apextc_1100_tli_f5xcrlo = {"Bypassport": 1, "maskbit":"1100", "setpointfreq": Spec(f"SCN_CORE_CX816_apexsetpoint_Specs.apexsetpoint_1100"), "ISEDC": True}
    apextc_1100_f5xcrlo = get_test_list_atspeed_f5f6_apexmtt_multipass(flow_name, corner, apextc_1100_tli_f5xcrlo, flow_matrix, corner_id, m0m1_f5xcrlo)

    m2m3_f5xcrlo = "X_ALLCORE_0011_APEX_FMAX"
    apextc_0011_tli_f5xcrlo = {"Bypassport": 1, "maskbit":"0011", "setpointfreq": Spec(f"SCN_CORE_CX816_apexsetpoint_Specs.apexsetpoint_0011"), "ISEDC": True}
    apextc_0011_f5xcrlo = get_test_list_atspeed_f5f6_apexmtt_multipass(flow_name, corner, apextc_0011_tli_f5xcrlo, flow_matrix, corner_id, m2m3_f5xcrlo)

    apextc_multipass_composite_f5xcrlo = Flow("FMAX_MULTIPASS", apextc_1100_f5xcrlo, apextc_0011_f5xcrlo)
          
    # Create flows for each module
    module_flows = [create_module_flow(flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(DCM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   #Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                   apextc_f5xcrlo,
                   Fitem("SAME", apextc_multipass_composite_f5xcrlo, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                   vmintc_atspeed_occ_f5xcrlo,
                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(ret=0), ))
    
    return subflow

# Define the subflows for F5 and F6, only F5 enabled for now
subflows = []
for corner in ["F5"]:
    flow_name = f"{corner}XCRLO"
    flow_matrix = flow_matrix_definitions[corner]
    corner_id = corner_id_definitions[corner]
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id))

#################################################################################
#							VMAXXCR SUBFLOW
#
#	- ENDCPU flow will test ATSPEED & STUCKAT content 
#	- No Fail flow 
#
#################################################################################
vmaxxcr_flow = "VMAXXCR"
stuckat_vmaxxcr_corner = "F1"
atspeed_vmaxxcr_corner = "F5"

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CR_F5_FREQ_MHz": "3600"
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CR_F5_FREQ"
}

corner_id_definitions = {
    "F5": "C5"
}

#STUCKAT_F1 test list
vmaxxcr_vmintc_stuckat_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
vmaxxcr_vmintc_stuckat_occ = get_test_list_stuckat_occ(vmaxxcr_flow, stuckat_vmaxxcr_corner, vmaxxcr_vmintc_stuckat_occ_tli)
vmaxxcr_f1 = Flow("VMAXXCR_F1", vmaxxcr_vmintc_stuckat_occ)#vmintc_stuckat_0, vmintc_stuckat_1, vmintc_stuckat_2, vmintc_stuckat_3, 

#ATSPEED_F5 test list
vmaxxcr_vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
vmaxxcr_vmintc_atspeed_occ = get_test_list_atspeed_vmax_occ(vmaxxcr_flow, atspeed_vmaxxcr_corner, vmaxxcr_vmintc_atspeed_occ_tli, flow_matrix, corner_id)
vmaxxcr_f5 = Flow("VMAXXCR_F5", vmaxxcr_vmintc_atspeed_occ)#vmintc_atspeed_0, vmintc_atspeed_1, vmintc_atspeed_2, vmintc_atspeed_3, )

# VMAXXCR SUBFLOW
VMAXXCR_SUBFLOW = Flow(f'{MODULE}_VMAXXCR',
                     Fitem("SAME", vmaxxcr_f1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     Fitem("SAME", vmaxxcr_f5, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     )

#################################################################################
#							VMAXXCRLO SUBFLOW
#
#	- ENDCPU flow will test ATSPEED & STUCKAT content at 100c
#	- No Fail flow 
#
#################################################################################
vmaxxcrlo_flow = "VMAXXCRLO"
stuckat_vmaxxcrlo_corner = "F1"
atspeed_vmaxxcrlo_corner = "F5"

# FlowMatrixRule Definition
FlowMatrixRule = {
    "CR_F5_FREQ_MHz": "3600"
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "CR_F5_FREQ"
}

corner_id_definitions = {
    "F5": "C5"
}

#STUCKAT_F1 test list
vmaxxcrlo_vmintc_stuckat_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
vmaxxcrlo_vmintc_stuckat_occ = get_test_list_stuckat_occ(vmaxxcrlo_flow, stuckat_vmaxxcrlo_corner, vmaxxcrlo_vmintc_stuckat_occ_tli)
vmaxxcrlo_f1 = Flow("VMAXXCRLO_F1", vmaxxcrlo_vmintc_stuckat_occ)#vmintc_stuckat_0, vmintc_stuckat_1, vmintc_stuckat_2, vmintc_stuckat_3, 

#ATSPEED_F5 test list
vmaxxcrlo_vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
vmaxxcrlo_vmintc_atspeed_occ = get_test_list_atspeed_vmax_occ(vmaxxcrlo_flow, atspeed_vmaxxcrlo_corner, vmaxxcrlo_vmintc_atspeed_occ_tli, flow_matrix, corner_id)
vmaxxcrlo_f5 = Flow("VMAXXCRLO_F5", vmaxxcrlo_vmintc_atspeed_occ)#vmintc_atspeed_0, vmintc_atspeed_1, vmintc_atspeed_2, vmintc_atspeed_3, )

# VMAXXCR SUBFLOW
VMAXXCRLO_SUBFLOW = Flow(f'{MODULE}_VMAXXCRLO',
                     Fitem("SAME", vmaxxcrlo_f1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     Fitem("SAME", vmaxxcrlo_f5, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     )