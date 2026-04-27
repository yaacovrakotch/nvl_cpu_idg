from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, PrimeMbistTestMethod, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback, ApexTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig

product_skus = ["CX816"]
product = "ARR_CCF"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'

MODULE = "ARR_CCF_CX816"
#VOLTAGE_DOMAIN = "VCCIA"
VOLTAGE_DOMAIN_1 = "VNNAON"

########################################################################
# INITIALIZE
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(6225,6249), (2125,2140)],
    basenumrange=(2750, 2999),
    defaultthermalbin=(90976225, 90972125), #9097HB17
    defaultresetbin=(90621925, 90211925), #90HB1917/90HB1918
)

#Import(MODULE + "_Timing.tcg")
Import("ARR_CCF_CX816_Specs.usrv")
Import("ARR_CCF_CX816_Timing.tcg")


FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000"
}

frequency_value = FlowMatrixRule["CCF_F2_FREQ_MHz"]

#CBOA KS F? Nom
def get_test_list_begcpunom_lsa_cboa(
    flow,
    testinput
):
    test_list_lsa_cboa = []
    sample_test_lsa_cboa = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_NOM_{frequency_value}_CBOA",
               Patlist=f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_cboa_all_lsa_vccring_ks_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom',
               StartVoltages = Spec("ARR_CCF_Specs.LowSearch"),
               EndVoltageLimits = Spec("ARR_CCF_Specs.HighSearch"),
               VoltageTargets= Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               ##FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers=AUTO,
               StepSize=Spec("toDouble(0.01)"),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               FivrCondition = 'NOM_CCF',
               ForwardingMode='Input',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
			   SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
               SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
                            edc=testinput.get("ISEDC"),
                            r0=pFail(setbin=-21, goto="NEXT"),
                            r1=pPass(goto="NEXT"),
                            r2=pFail(setbin=-21, goto="NEXT"),
                            r3=pFail(setbin=-21, goto="NEXT"),
                            r4=pFail(setbin=-21, goto="NEXT"),
                            r5=pFail(setbin=-21, goto="NEXT")))
    test_list_lsa_cboa.append(sample_test_lsa_cboa)

    return test_list_lsa_cboa

#LLCRF KS F? Nom
def get_test_list_begcpunom_lsa_llcrf(
    flow,
    testinput
    ):
	
    test_list_lsa_llcrf = []	
    sample_test_lsa_llcrf = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_NOM_{frequency_value}_LLCRF",
               Patlist=f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_llcrf_all_lsa_vccring_ks_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom',
               StartVoltages = Spec("ARR_CCF_Specs.LowSearch"),
               EndVoltageLimits = Spec("ARR_CCF_Specs.HighSearch"),
               VoltageTargets= Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               ##FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers=AUTO,
               StepSize=Spec("toDouble(0.01)"),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               FivrCondition = 'NOM_CCF',
               ForwardingMode='Input',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
			   SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
               SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -21, goto="NEXT"),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = -21, goto="NEXT"),
               r3=pFail(setbin = -21, goto="NEXT"),
               r4=pFail(setbin = -21, goto="NEXT"),
               r5=pFail(setbin = -21, goto="NEXT")))
    test_list_lsa_llcrf.append(sample_test_lsa_llcrf)
    
    return test_list_lsa_llcrf

#LLCSRAM KS F? Nom
def get_test_list_begcpunom_ssa_llcsram(
    flow,
    testinput
    ):

    test_list_ssa_llcsram = []	
    sample_test_ssa_llcsram = \
        VminTC(name=f"SSA_CCF_SB_K_{flow}_X_X_NOM_{frequency_value}_LLCSRAM",
               Patlist=f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_llcsram_all_ssa_vccring_ks_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom',
               StartVoltages = Spec("ARR_CCF_Specs.LowSearch"),
               EndVoltageLimits = Spec("ARR_CCF_Specs.HighSearch"),
               VoltageTargets= Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               ##FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers=AUTO,
               StepSize=Spec("toDouble(0.01)"),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               FivrCondition = 'NOM_CCF',
               ForwardingMode='Input',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
			   SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
               SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -62, ret= 1),
               r1=pPass(ret=1),
               r2=pFail(setbin = -62, ret= 1),
               r3=pFail(setbin = -62, ret= 1),
               r4=pFail(setbin = -62, ret= 1),
               r5=pFail(setbin = -62, ret= 1)))
    test_list_ssa_llcsram.append(sample_test_ssa_llcsram)
    
    return test_list_ssa_llcsram


#CBOA F1-F4 Vmin
def get_test_list_lsa_cboa_f1f4_mtt (
    flow, 
    corner,
    testinput,
    FlowMatrix
    ):
           
    test_list_lsa_cboa_f1f4_mtt = []
    
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_lsa_cboa_f1f4_mtt = \
    NativeMultiTrial(
             name=f"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_CBOA_MTT",
             exitaction="Continue",
                _comment = f"KILL LSA CBOA {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING",
                template = VminTC(name = f'"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_CBOA"',
                Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_cboa_all_lsa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets= Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               FivrCondition='NOM_CCF',
               #FivrConditionPlistParamName="Patlist",
               #VoltageConverter=Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
               StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='InputOutput',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
               SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
               SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
                ),
                
                r0 = pFail(setbin = -21, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r3 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r4 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -21, goto= "NEXT"),
                            r1 = pPass(goto= "NEXT"),
                            r2 = pFail(setbin = -21, goto= "NEXT"),
                            r3 = pFail(setbin = -21, goto= "NEXT"),
                            r4 = pFail(setbin= -21, goto= "NEXT"),
                            r5 = pFail(setbin= -21, goto= "NEXT")))
            
    test_list_lsa_cboa_f1f4_mtt.append(sample_test_lsa_cboa_f1f4_mtt)

    return test_list_lsa_cboa_f1f4_mtt

#LLCRF F1-F4 Vmin
def get_test_list_lsa_llcrf_f1f4_mtt (
    flow, 
    corner, 
    testinput,
    FlowMatrix
    ):
           
    test_list_lsa_llcrf_f1f4_mtt = []
    
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_lsa_llcrf_f1f4_mtt = \
    NativeMultiTrial(name = f"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_LLCRF_MTT",
                exitaction = "Continue",
                _comment = f"KILL LSA LLCRF {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING",
                template = VminTC(name = f'"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_LLCRF"',
                Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_lsa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets= Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               FivrCondition='NOM_CCF',
               #FivrConditionPlistParamName="Patlist",
               #VoltageConverter=Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
               StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='InputOutput',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
               SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
               SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
                ),
                
                r0 = pFail(setbin = -21, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r3 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r4 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -21, goto= "NEXT"),
                            r1 = pPass(goto= "NEXT"),
                            r2 = pFail(setbin = -21, goto= "NEXT"),
                            r3 = pFail(setbin = -21, goto= "NEXT"),
                            r4 = pFail(setbin= -21, goto= "NEXT"),
                            r5 = pFail(setbin= -21, goto= "NEXT")))
            
    test_list_lsa_llcrf_f1f4_mtt.append(sample_test_lsa_llcrf_f1f4_mtt)

    return test_list_lsa_llcrf_f1f4_mtt

#LLCSRAM F1-F4 Vmin
def get_test_list_ssa_llcsram_f1f4_mtt (
    flow, 
    corner, 
    testinput,
    FlowMatrix
    ):
    
    test_list_ssa_llcsram_f1f4_mtt = []
    
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_ssa_llcsram_f1f4_mtt = \
    NativeMultiTrial(name = f"SSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_LLCSRAM_MTT",
                exitaction = "Continue",
                _comment = f"KILL SSA LLCSRAM {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING",
                template = VminTC(name = f'"SSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_LLCSRAM"',
                Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_ssa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets= Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               FivrCondition='NOM_CCF',
               #FivrConditionPlistParamName="Patlist",
               #VoltageConverter=Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CLR_{corner}'),
               StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='InputOutput',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
               SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
               SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
                ),
                
                r0 = pFail(setbin = -62, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                r3 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                r4 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -62, ret= 1),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -62, ret= 1),
                            r3 = pFail(setbin = -62, ret= 1),
                            r4 = pFail(setbin= -62, ret= 1),
                            r5 = pFail(setbin= -62, ret= 1)))
            
    test_list_ssa_llcsram_f1f4_mtt.append(sample_test_ssa_llcsram_f1f4_mtt)

    return test_list_ssa_llcsram_f1f4_mtt

#CBOA F5-F6 Vmin
def get_test_list_lsa_cboa_f5f6_mtt (
    flow, 
    corner, 
    testinput,
    FlowMatrix
    ):

    test_list_lsa_cboa_f5f6_mtt = []
    
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]

    sample_test_lsa_cboa_f5f6_mtt = \
    NativeMultiTrial(name = f"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_CBOA_MTT",
                exitaction = "Continue",
                _comment = f"KILL LSA CBOA {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING_TOP",
                template = VminTC(name = f'"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_CBOA"',
                Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_cboa_all_lsa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               FivrCondition='NOM_CCF',
               StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='InputOutput',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
                ),
                
                r0 = pFail(setbin = -21, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r3 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r4 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -21, goto="NEXT"),
                            r1 = pPass(goto="NEXT"),
                            r2 = pFail(goto="NEXT"),
                            r3 = pFail(goto="NEXT"),
                            r4 = pFail(goto="NEXT"),
                            r5 = pFail(goto="NEXT")))
            
    test_list_lsa_cboa_f5f6_mtt.append(sample_test_lsa_cboa_f5f6_mtt)

    return test_list_lsa_cboa_f5f6_mtt

#LLCRF F5-F6 Vmin
def get_test_list_lsa_llcrf_f5f6_mtt (
    flow, 
    corner, 
    testinput,
    FlowMatrix
    ):

    test_list_lsa_llcrf_f5f6_mtt = []
    
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_lsa_llcrf_f5f6_mtt = \
    NativeMultiTrial(name = f"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_LLCRF_MTT",
                exitaction = "Continue",
                _comment = f"KILL LSA LLCRF {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING_TOP",
                template = VminTC(name = f'"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_LLCRF"',
                Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_lsa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               FivrCondition='NOM_CCF',
               StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='InputOutput',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
                ),
                
                r0 = pFail(setbin = -21, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r3 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r4 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -21, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -21, goto ="NEXT"),
                            r1 = pPass(goto ="NEXT"),
                            r2 = pFail(setbin = -21, goto ="NEXT"),
                            r3 = pFail(setbin = -21, goto ="NEXT"),
                            r4 = pFail(setbin= -21, goto ="NEXT"),
                            r5 = pFail(setbin= -21, goto ="NEXT")))
            
    test_list_lsa_llcrf_f5f6_mtt.append(sample_test_lsa_llcrf_f5f6_mtt)

    return test_list_lsa_llcrf_f5f6_mtt

#LLCSRAM F5-F6 Vmin
def get_test_list_ssa_llcsram_f5f6_mtt (
   flow, 
    corner, 
    testinput,
    FlowMatrix
    ):

    test_list_ssa_llcsram_f5f6_mtt = []
    
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]

    sample_test_ssa_llcsram_f5f6_mtt = \
    NativeMultiTrial(name = f"SSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_LLCSRAM_MTT",
                exitaction = "Continue",
                _comment = f"KILL SSA LLCSRAM {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.RING_TOP",
                template = VminTC(name = f'"SSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_LLCSRAM"',
                Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_ssa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               FivrCondition='NOM_CCF',
               StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='InputOutput',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
                ),
                
                r0 = pFail(setbin = -62, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                r3 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                r4 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                r5 = pFail(setbin= -62, ret= 0, trialaction = "Exit"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -62, ret= 1),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -62, ret= 1),
                            r3 = pFail(setbin = -62, ret= 1),
                            r4 = pFail(setbin= -62, ret= 1),
                            r5 = pFail(setbin= -62, ret= 1)))
            
    test_list_ssa_llcsram_f5f6_mtt.append(sample_test_ssa_llcsram_f5f6_mtt)

    return test_list_ssa_llcsram_f5f6_mtt


FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000"
}

#CBOA Fmin
def get_test_list_fminxccf_lsa_cboa(
    flow,
    corner,
    testinput,
):

    test_list_lsa_cboa_fminxccf = []
    sample_test_lsa_cboa_fminxccf = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_X_X_CBOA",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_cboa_all_lsa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
               FivrCondition='NOM_CCF',
               StepSize=Spec("toDouble(0.01)"),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='Input',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
                            edc=testinput.get("ISEDC"),
                            r0=pFail(setbin=-21, goto="NEXT"),
                            r1=pPass(goto="NEXT"),
                            r2=pFail(setbin=-21, goto="NEXT"),
                            r3=pFail(setbin=-21, goto="NEXT"),
                            r4=pFail(setbin=-21, goto="NEXT"),
                            r5=pFail(setbin=-21, goto="NEXT")))
    test_list_lsa_cboa_fminxccf.append(sample_test_lsa_cboa_fminxccf)

    return test_list_lsa_cboa_fminxccf
    test_list_lsa_cboa_fminxccf.append(sample_test_lsa_cboa_fminxccf)

    return test_list_lsa_cboa_fminxccf

#LLCRF Fmin
def get_test_list_fminxccf_lsa_llcrf(
    flow,
    corner,
    testinput,
):

    test_list_lsa_llcrf_fminxccf = []
    sample_test_lsa_llcrf_fminxccf = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_X_X_LLCRF",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_lsa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
               FivrCondition='NOM_CCF',
               StepSize=Spec("toDouble(0.01)"),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='Input',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
                            edc=testinput.get("ISEDC"),
                            r0=pFail(setbin=-21, goto="NEXT"),
                            r1=pPass(goto="NEXT"),
                            r2=pFail(setbin=-21, goto="NEXT"),
                            r3=pFail(setbin=-21, goto="NEXT"),
                            r4=pFail(setbin=-21, goto="NEXT"),
                            r5=pFail(setbin=-21, goto="NEXT")))
    test_list_lsa_llcrf_fminxccf.append(sample_test_lsa_llcrf_fminxccf)

    return test_list_lsa_llcrf_fminxccf

#LLCSRAM Fmin
def get_test_list_fminxccf_ssa_llcsram(
    flow,
    corner,
    testinput,
):
    
    test_list_ssa_llcsram_fminxccf = []
    sample_test_ssa_llcsram_fminxccf = \
        VminTC(name=f"SSA_CCF_SB_K_{flow}_X_X_X_X_LLSRAM",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_ssa_vccring_limiter_{corner.lower()}_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='SingleVmin',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               CornerIdentifiers = f"CCF0@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
               FivrCondition='NOM_CCF',
               StepSize=Spec("toDouble(0.01)"),
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='Input',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
                            edc=testinput.get("ISEDC"),
                            r0=pFail(setbin = -62, ret=1),
                            r1=pPass(ret=1),
                            r2=pFail(setbin = -62, ret=1),
                            r3=pFail(setbin = -62, ret=1),
                            r4=pFail(setbin = -62, ret=1),
                            r5=pFail(setbin = -62, ret=1)))
    test_list_ssa_llcsram_fminxccf.append(sample_test_ssa_llcsram_fminxccf)

    return test_list_ssa_llcsram_fminxccf


FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000"
}

frequency_value = FlowMatrixRule["CCF_F1_FREQ_MHz"]

#LLCSRAM PMUX
def get_test_list_endcpu_ssa_llcsram_pmux(
    flow,
    corner,
    testinput
    ):

    test_list_ssa_llcsram_pmux = []	
    sample_test_ssa_llcsram_pmux = \
        VminTC(name=f"SSA_CCF_SB_K_{flow}_X_{VOLTAGE_DOMAIN_1.upper()}_NOM_{frequency_value}_LLCSRAM_PMUX",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_llcsram_all_ssa_vnnaon_ks_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               #LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom',
               StartVoltages = Spec("ARR_CCF_Specs.LowSearch"),
               EndVoltageLimits = Spec("ARR_CCF_Specs.HighSearch"),
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               StepSize=Spec("toDouble(0.01)"),
               FivrCondition='NOM_CCF',
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='None',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance_PMUX"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -62, ret=1),
               r1=pPass(ret=1),
               r2=pFail(setbin = -62, ret=1),
               r3=pFail(setbin = -62, ret=1),
               r4=pFail(setbin = -62, ret=1),
               r5=pFail(setbin = -62, ret=1)))
    test_list_ssa_llcsram_pmux.append(sample_test_ssa_llcsram_pmux)
    
    return test_list_ssa_llcsram_pmux

def get_test_callback_pmux(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_list_callback_pmux = []	
    sample_test_callback_pmux = \
        RunCallback(name=f"ARR_CCF_RUNCALLBACK_K_{flow}_X_X_X_X_PMUX",
               Callback = "CalculateFrequencySwitch",
               Parameters = "--target CLR --voltage 0.715 --flow RING --expression MaaaCdrv:ringfreq:[FREQ]Ghz, MCarrPbistCCF:ring_ratio:[FREQ]Ghz --token CLRPMUX",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -62, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_callback_pmux.append(sample_test_callback_pmux)
    
    return test_list_callback_pmux

FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000"
}

frequency_value = FlowMatrixRule["CCF_F1_FREQ_MHz"]

#CBOA F1 Vmax
def get_test_list_vmaxxccf1_lsa_cboa(
    flow,
    corner,
    testinput
):

    test_list_lsa_cboa_vmaxxccf1 = []
    sample_test_lsa_cboa_vmaxxccf1 = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_X_{frequency_value}_CBOA",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_cboa_all_lsa_vccring_ks_vmax_f1_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max',
               StartVoltages = '0.9',
               EndVoltageLimits='0.9',
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               StepSize=Spec("toDouble(0.01)"),
               FivrCondition='NOM_CCF',
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='None',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
                            edc=testinput.get("ISEDC"),
                            r0=pFail(setbin=-21, goto="NEXT"),
                            r1=pPass(goto="NEXT"),
                            r2=pFail(setbin=-21, goto="NEXT"),
                            r3=pFail(setbin=-21, goto="NEXT"),
                            r4=pFail(setbin=-21, goto="NEXT"),
                            r5=pFail(setbin=-21, goto="NEXT")))
    test_list_lsa_cboa_vmaxxccf1.append(sample_test_lsa_cboa_vmaxxccf1)

    return test_list_lsa_cboa_vmaxxccf1

#LLCRF F1 Vmax
def get_test_list_vmaxxccf1_lsa_llcrf(
    flow,
    corner,
    testinput
    ):
	

    test_list_lsa_llcrf_vmaxxccf1 = []	
    sample_test_lsa_llcrf_vmaxxccf1 = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_X_{frequency_value}_LLCRF",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_llcrf_all_lsa_vccring_ks_vmax_f1_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max',
               StartVoltages = '0.9',
               EndVoltageLimits='0.9',
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               StepSize=Spec("toDouble(0.01)"),
               FivrCondition='NOM_CCF',
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='None',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -21, goto="NEXT"),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = -21, goto="NEXT"),
               r3=pFail(setbin = -21, goto="NEXT"),
               r4=pFail(setbin = -21, goto="NEXT"),
               r5=pFail(setbin = -21, goto="NEXT")))
    test_list_lsa_llcrf_vmaxxccf1.append(sample_test_lsa_llcrf_vmaxxccf1)
    
    return test_list_lsa_llcrf_vmaxxccf1

#LLCSRAM F1 Vmax
def get_test_list_vmaxxccf1_ssa_llcsram(
    flow,
    corner,
    testinput
    ):

    test_list_ssa_llcsram_vmaxxccf1 = []	
    sample_test_ssa_llcsram_vmaxxccf1 = \
        VminTC(name=f"SSA_CCF_SB_K_{flow}_X_X_X_{frequency_value}_LLCSRAM",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_llcsram_all_ssa_vccring_ks_vmax_f1_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max',
               StartVoltages = '0.9',
               EndVoltageLimits='0.9',
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               StepSize=Spec("toDouble(0.01)"),
               FivrCondition='NOM_CCF',
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='None',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -62, ret=1),
               r1=pPass(ret = 1),
               r2=pFail(setbin = -62, ret=1),
               r3=pFail(setbin = -62, ret=1),
               r4=pFail(setbin = -62, ret=1),
               r5=pFail(setbin = -62, ret=1)))
    test_list_ssa_llcsram_vmaxxccf1.append(sample_test_ssa_llcsram_vmaxxccf1)
    
    return test_list_ssa_llcsram_vmaxxccf1

#CBOA F5 Vmax
def get_test_list_vmaxxccf5_lsa_cboa(
    flow,
    corner,
    testinput
):

    test_list_lsa_cboa_vmaxxccf5 = []
    sample_test_lsa_cboa_vmaxxccf5 = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_X_3600_CBOA",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_cboa_all_lsa_vccring_ks_vmax_f6_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max',
               StartVoltages = '0.9',
               EndVoltageLimits='0.9',
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               StepSize=Spec("toDouble(0.01)"),
               FivrCondition='NOM_CCF',
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='None',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
                            edc=testinput.get("ISEDC"),
                            r0=pFail(setbin=-21, goto="NEXT"),
                            r1=pPass(goto="NEXT"),
                            r2=pFail(setbin=-21, goto="NEXT"),
                            r3=pFail(setbin=-21, goto="NEXT"),
                            r4=pFail(setbin=-21, goto="NEXT"),
                            r5=pFail(setbin=-21, goto="NEXT")))
    test_list_lsa_cboa_vmaxxccf5.append(sample_test_lsa_cboa_vmaxxccf5)

    return test_list_lsa_cboa_vmaxxccf5

#LLCRF F5 Vmax
def get_test_list_vmaxxccf5_lsa_llcrf(
    flow,
    corner,
    testinput
    ):
	

    test_list_lsa_llcrf_vmaxxccf5 = []	
    sample_test_lsa_llcrf_vmaxxccf5 = \
        VminTC(name=f"LSA_CCF_SB_K_{flow}_X_X_X_3600_LLCRF",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_llcrf_all_lsa_vccring_ks_vmax_f6_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max',
               StartVoltages = '0.9',
               EndVoltageLimits='0.9',
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               StepSize=Spec("toDouble(0.01)"),
               FivrCondition='NOM_CCF',
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='None',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -21, goto="NEXT"),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = -21, goto="NEXT"),
               r3=pFail(setbin = -21, goto="NEXT"),
               r4=pFail(setbin = -21, goto="NEXT"),
               r5=pFail(setbin = -21, goto="NEXT")))
    test_list_lsa_llcrf_vmaxxccf5.append(sample_test_lsa_llcrf_vmaxxccf5)
    
    return test_list_lsa_llcrf_vmaxxccf5

#LLCSRAM F5 Vmax
def get_test_list_vmaxxccf5_ssa_llcsram(
    flow,
    corner,
    testinput
    ):

    test_list_ssa_llcsram_vmaxxccf5 = []	
    sample_test_ssa_llcsram_vmaxxccf5 = \
        VminTC(name=f"SSA_CCF_SB_K_{flow}_X_X_X_3600_LLCSRAM",
               Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_llcsram_all_ssa_vccring_ks_vmax_f6_x_class_hptp_list',
               TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
               #LevelsTc = 'ARR_CCF::SBF_nom_lvl_VNNAON_LLCSRAM_MIN',
               LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max',
               StartVoltages = '0.9',
               EndVoltageLimits='0.9',
               VoltageTargets=Spec("ARR_CCF_Specs.VCCR_VoltageTarget"),
               ExecutionMode='SearchWithScoreboard',
               #FailCaptureCount=Spec("ARR_CCF_Specs.FailCaptureCount"),
               TestMode='Scoreboard',
               BaseNumbers = None if "SCR" in flow else AUTO,
               #CornerIdentifiers = f"CCF@{corner}",
               FlowIndexCallbackName = '',
               FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),  
               LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
               StepSize=Spec("toDouble(0.01)"),
               FivrCondition='NOM_CCF',
               FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
               ForwardingMode='None',
               #MaxRepetitionCount='1',
               RecoveryMode='NoRecovery',
               PatternNameCounterIndexes=Spec("ARR_CCF_Specs.PatternMap"),
               ScoreboardEdgeTicks = Spec("toInteger(0)"),
               #MaxFailsNum='1',
               SetPointsPlistParamName='Patlist',
	           SetPointsPreInstance = Spec("ARR_CCF_Specs.VCCR_PreInstance"),
	           SetPointsPostInstance = Spec("ARR_CCF_Specs.VCCR_PostInstance"),
               BypassPort=testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -62, ret=1),
               r1=pPass(ret=1),
               r2=pFail(setbin = -62, ret=1),
               r3=pFail(setbin = -62, ret=1),
               r4=pFail(setbin = -62, ret=1),
               r5=pFail(setbin = -62, ret=1)))
    test_list_ssa_llcsram_vmaxxccf5.append(sample_test_ssa_llcsram_vmaxxccf5)
    
    return test_list_ssa_llcsram_vmaxxccf5

#Apex CBOA Fmax
def get_test_list_lsa_cboa_f5f6_mtt_apex(
    flow, 
    testinput,
    corner,
    FlowMatrix
    ):
    """
    Generates a list containing a NativeMultiTrial APEX MTT test for ATSPEED CORE VMIN F5/F6 flows.
    """
    test_list_lsa_cboa_f5f6_mtt_apex = []
    
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_lsa_cboa_f5f6_mtt_apex = NativeMultiTrial(
        name=f"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_CBOA_APEX_MTT",
        exitaction="Restore",
        trialvar="CPU_TRIALS::FlowDomain.RING",
        template=ApexTC(
            name=f'"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_CBOA_APEX"',
            Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_ccf_cboa_all_lsa_vccring_limiter_f5_class_hptp_list',
            #LevelsTc='BASE::SBF_nom_lvl',
            LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom',
            TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
            InitialMaskBits='',
            DtsConfiguration='',
            ForwardingMode='Input',
            PinMap='',
            RecoveryOptions='',
            RecoveryTracking='',
            FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),
            End=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
            Start=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
            SetPointsPreInstance = TrialParamSpec(f'"MCdrv:ringfreq:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
            SetPointsPostInstance='',
            FivrCondition='',
            FivrConditionPlistParamName="Patlist",
            StepSize = Spec("toInteger(1)"),
            VoltageConverter='',
            ExportTokens='FXCCFC3,FXCCF2,FXCCF1,FXCCF0',
            #Targets='CORE3,CORE2,CORE1,CORE0',
            BypassPort=testinput.get("BypassPort", 1),
        ),
        r0=pFail(setbin=-21, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
        r1=pPass(ret=1, trialaction="Exit"),
        r2=pFail(setbin=-21, ret=0, trialaction="Exit"),
        r3=pFail(setbin=-21, ret=0, trialaction="Exit"),
        r4=pFail(setbin=-21, ret=0, trialaction="Exit"),
        r5=pFail(setbin=-21, ret=0, trialaction="Exit"),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(goto="NEXT"),
            r3=pFail(goto="NEXT"),
            r4=pFail(goto="NEXT"),
            r5=pFail(goto="NEXT")
        )
    )
    test_list_lsa_cboa_f5f6_mtt_apex.append(sample_test_lsa_cboa_f5f6_mtt_apex)
    return test_list_lsa_cboa_f5f6_mtt_apex

#Apex LLCRF Fmax
def get_test_list_lsa_llcrf_f5f6_mtt_apex(
    flow, 
    testinput,
    corner,
    FlowMatrix
    ):
    """
    Generates a list containing a NativeMultiTrial APEX MTT test for ATSPEED CORE VMIN F5/F6 flows.
    """

    test_list_lsa_llcrf_f5f6_mtt_apex = []

    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]

    sample_test_lsa_llcrf_f5f6_mtt_apex = NativeMultiTrial(
        name=f"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_LLCRF_APEX_MTT",
        exitaction="Restore",
        trialvar="CPU_TRIALS::FlowDomain.RING",
        template=ApexTC(
            name=f'"LSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_LLCRF_APEX"',
            Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_lsa_vccring_limiter_f5_class_hptp_list',
            #LevelsTc='BASE::SBF_nom_lvl',
            LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom',
            TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
            InitialMaskBits='',
            DtsConfiguration='',
            ForwardingMode='Input',
            PinMap='',
            RecoveryOptions='',
            RecoveryTracking='',
            FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),
            End=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
            Start=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
            SetPointsPreInstance = TrialParamSpec(f'"MCdrv:ringfreq:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
            SetPointsPostInstance='',
            FivrCondition='',
            FivrConditionPlistParamName="Patlist",
            StepSize = Spec("toInteger(1)"),
            VoltageConverter='',
            ExportTokens='FXCCFC3,FXCCF2,FXCCF1,FXCCF0',
            #Targets='CORE3,CORE2,CORE1,CORE0',
            BypassPort=testinput.get("BypassPort", 1),
        ),
        r0=pFail(setbin=-21, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
        r1=pPass(ret=1, trialaction="Exit"),
        r2=pFail(setbin=-21, ret=0, trialaction="Exit"),
        r3=pFail(setbin=-21, ret=0, trialaction="Exit"),
        r4=pFail(setbin=-21, ret=0, trialaction="Exit"),
        r5=pFail(setbin=-21, ret=0, trialaction="Exit"),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(goto="NEXT"),
            r3=pFail(goto="NEXT"),
            r4=pFail(goto="NEXT"),
            r5=pFail(goto="NEXT")
        )
    )
    test_list_lsa_llcrf_f5f6_mtt_apex.append(sample_test_lsa_llcrf_f5f6_mtt_apex)
    return test_list_lsa_llcrf_f5f6_mtt_apex

#Apex LLCSRAM Fmax
def get_test_list_ssa_llcsram_f5f6_mtt_apex(
    flow, 
    testinput,
    corner,
    FlowMatrix
    ):
    """
    Generates a list containing a NativeMultiTrial APEX MTT test for ATSPEED CORE VMIN F5/F6 flows.
    """

    test_list_ssa_llcsram_f5f6_mtt_apex = []

    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]

    sample_test_ssa_llcsram_f5f6_mtt_apex = NativeMultiTrial(
        name=f"SSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_{frequency_value}_LLCSRAM_APEX_MTT",
        exitaction="Restore",
        trialvar="CPU_TRIALS::FlowDomain.RING",
        template=ApexTC(
            name=f'"SSA_CCF_VMIN_K_{flow.upper()}_X_X_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_LLCSRAM_APEX"',
            Patlist = f'arr_cdie_{flow.lower()}_mbist_ccf_all_ssa_vccring_limiter_f5_class_hptp_list',
            #LevelsTc='BASE::SBF_nom_lvl',
            LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom',
            TimingsTc='ARR_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_ccfarrmts800',
            InitialMaskBits='',
            DtsConfiguration='',
            ForwardingMode='Input',
            PinMap='',
            RecoveryOptions='',
            RecoveryTracking='',
            FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),
            End=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
            Start=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
            SetPointsPreInstance = TrialParamSpec(f'"MCdrv:ringfreq:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
            SetPointsPostInstance='',
            FivrCondition='',
            FivrConditionPlistParamName="Patlist",
            StepSize = Spec("toInteger(1)"),
            VoltageConverter='',
            ExportTokens='FXCCFC3,FXCCF2,FXCCF1,FXCCF0',
            #Targets='CORE3,CORE2,CORE1,CORE0',
            BypassPort=testinput.get("BypassPort", 1),
        ),
        r0=pFail(setbin=-62, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
        r1=pPass(ret=1, trialaction="Exit"),
        r2=pFail(setbin=-62, ret=0, trialaction="Exit"),
        r3=pFail(setbin=-62, ret=0, trialaction="Exit"),
        r4=pFail(setbin=-62, ret=0, trialaction="Exit"),
        r5=pFail(setbin=-62, ret=0, trialaction="Exit"),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(goto="NEXT"),
            r3=pFail(goto="NEXT"),
            r4=pFail(goto="NEXT"),
            r5=pFail(goto="NEXT")
        )
    )
    test_list_ssa_llcsram_f5f6_mtt_apex.append(sample_test_ssa_llcsram_f5f6_mtt_apex)
    return test_list_ssa_llcsram_f5f6_mtt_apex


#################################################################################
#							BEGINCPUNOM SUBFLOW
#
#	- BEGINCPUNOM flow will test LSA CBO/LLCRF and SSA LLCSRAM content 
#	
#################################################################################

begincpunom_flow = "BEGINCPUNOM"

begincpunom_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
begincpunom_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
begincpunom_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

#testinput = {
#    "Testmode": "Scoreboard",
#    "Bypassport": 1, 
#    "ISEDC": True 
#}

begincpunom_vmintc_lsa_cboa = get_test_list_begcpunom_lsa_cboa(
    begincpunom_flow,
    begincpunom_vmintc_lsa_cboa_tli
)

begincpunom_vmintc_lsa_llcrf = get_test_list_begcpunom_lsa_llcrf(
    begincpunom_flow, 
    begincpunom_vmintc_lsa_llcrf_tli
)

begincpunom_vmintc_ssa_llcsram = get_test_list_begcpunom_ssa_llcsram(
    begincpunom_flow, 
    begincpunom_vmintc_ssa_llcsram_tli
)

BEGINCPUNOM_SUBFLOW = Flow(
    f'{MODULE}_BEGINCPUNOM',
    begincpunom_vmintc_lsa_cboa + begincpunom_vmintc_lsa_llcrf + begincpunom_vmintc_ssa_llcsram
)


#################################################################################
#                           F1F4 X CCF SUBFLOW
#
#   - Consists of F1 through F4 corners flow which take from sort llcsram pmovi
#
#################################################################################

FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000"
    }

flow_matrix_definitions = {
    "F1": "CCF_F1_FREQ",
    "F2": "CCF_F2_FREQ",
    "F3": "CCF_F3_FREQ",
    "F4": "CCF_F4_FREQ"
}


f1xccf_flow = "F1XCCF"

f1xccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
f1xccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
f1xccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

testinputcboa = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

f1xccf_vmintc_lsa_cboa = get_test_list_lsa_cboa_f1f4_mtt(
    f1xccf_flow, 
    corner='F1',
    testinput=testinputcboa,  
    FlowMatrix='CCF_F1_FREQ',
)

f1xccf_vmintc_lsa_llcrf = get_test_list_lsa_llcrf_f1f4_mtt(
    f1xccf_flow, 
    corner='F1',
    testinput=testinputllcrf,
    FlowMatrix='CCF_F1_FREQ'
)

f1xccf_vmintc_ssa_llcsram = get_test_list_ssa_llcsram_f1f4_mtt(
    f1xccf_flow, 
    corner='F1',
    testinput=testinputllcsram,
    FlowMatrix='CCF_F1_FREQ'
)

F1XCCF_SUBFLOW = Flow(
    f'{MODULE}_F1XCCF',
    f1xccf_vmintc_lsa_cboa + f1xccf_vmintc_lsa_llcrf + f1xccf_vmintc_ssa_llcsram

)


f2xccf_flow = "F2XCCF"

f2xccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
f2xccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
f2xccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

testinputcboa = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

f2xccf_vmintc_lsa_cboa = get_test_list_lsa_cboa_f1f4_mtt(
    f2xccf_flow, 
    corner='F2',
    testinput=testinputcboa,
    FlowMatrix='CCF_F2_FREQ'
)

f2xccf_vmintc_lsa_llcrf = get_test_list_lsa_llcrf_f1f4_mtt(
    f2xccf_flow, 
    corner='F2',
    testinput=testinputllcrf,
    FlowMatrix='CCF_F2_FREQ'
)

f2xccf_vmintc_ssa_llcsram = get_test_list_ssa_llcsram_f1f4_mtt(
    f2xccf_flow, 
    corner='F2',
    testinput=testinputllcsram,
    FlowMatrix='CCF_F2_FREQ'
)

F2XCCF_SUBFLOW = Flow(
    f'{MODULE}_F2XCCF',
    f2xccf_vmintc_lsa_cboa + f2xccf_vmintc_lsa_llcrf + f2xccf_vmintc_ssa_llcsram

)


f3xccf_flow = "F3XCCF"

f3xccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
f3xccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
f3xccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

testinputcboa = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

f3xccf_vmintc_lsa_cboa = get_test_list_lsa_cboa_f1f4_mtt(
    f3xccf_flow, 
    corner='F3',
    testinput=testinputcboa,
    FlowMatrix='CCF_F3_FREQ'
)

f3xccf_vmintc_lsa_llcrf = get_test_list_lsa_llcrf_f1f4_mtt(
    f3xccf_flow, 
    corner='F3',
    testinput=testinputllcrf,
    FlowMatrix='CCF_F3_FREQ'
)

f3xccf_vmintc_ssa_llcsram = get_test_list_ssa_llcsram_f1f4_mtt(
    f3xccf_flow, 
    corner='F3',
    testinput=testinputllcsram,
    FlowMatrix='CCF_F3_FREQ'
)

F3XCCF_SUBFLOW = Flow(
    f'{MODULE}_F3XCCF',
    f3xccf_vmintc_lsa_cboa + f3xccf_vmintc_lsa_llcrf + f3xccf_vmintc_ssa_llcsram

)


f4xccf_flow = "F4XCCF"

f4xccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
f4xccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
f4xccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

testinputcboa = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

f4xccf_vmintc_lsa_cboa = get_test_list_lsa_cboa_f1f4_mtt(
    f4xccf_flow, 
    corner='F4',
    testinput=testinputcboa,
    FlowMatrix='CCF_F4_FREQ'
)

f4xccf_vmintc_lsa_llcrf = get_test_list_lsa_llcrf_f1f4_mtt(
    f4xccf_flow, 
    corner='F4',
    testinput=testinputllcrf,
    FlowMatrix='CCF_F4_FREQ'
)

f4xccf_vmintc_ssa_llcsram = get_test_list_ssa_llcsram_f1f4_mtt(
    f4xccf_flow, 
    corner='F4',
    testinput=testinputllcsram,
    FlowMatrix='CCF_F4_FREQ'
)

F4XCCF_SUBFLOW = Flow(
    f'{MODULE}_F4XCCF',
    f4xccf_vmintc_lsa_cboa + f4xccf_vmintc_lsa_llcrf + f4xccf_vmintc_ssa_llcsram

)


#################################################################################
#                           F5F6 X CCF SUBFLOW
#
#   - Consists of F5 & F6 corners flow which will test content in TOP subflow 
#
#################################################################################

FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000",
    "CCF_F5_FREQ_MHz": "3600",
    "CCF_F6_FREQ_MHz": "4000",
    "CCF_F7_FREQ_MHz": "4300"
}

flow_matrix_definitions = {
    "F1": "CCF_F1_FREQ",
    "F2": "CCF_F2_FREQ",
    "F3": "CCF_F3_FREQ",
    "F4": "CCF_F4_FREQ",   
    "F5": "CCF_F5_FREQ",
    "F6": "CCF_F6_FREQ"
}

f5xccf_flow = "F5XCCF"
 
f5xccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
f5xccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
f5xccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

apextc_tli = {"Bypassport": 1, "ISEDC": True}

testinputcboa = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputcboaapex = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": False
}

testinputllcrfapex = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": False
}

testinputllcsramapex = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": False
}

f5xccf_vmintc_lsa_cboa = get_test_list_lsa_cboa_f5f6_mtt(
    f5xccf_flow, 
    corner='F5',
    testinput=testinputcboa,
    FlowMatrix='CCF_F5_FREQ'
)

f5xccf_vmintc_lsa_llcrf = get_test_list_lsa_llcrf_f5f6_mtt(
    f5xccf_flow, 
    corner='F5',
    testinput=testinputllcrf,
    FlowMatrix='CCF_F5_FREQ'
)

f5xccf_vmintc_ssa_llcsram = get_test_list_ssa_llcsram_f5f6_mtt(
    f5xccf_flow, 
    corner='F5',
    testinput=testinputllcsram,
    FlowMatrix='CCF_F5_FREQ'
)

f5xccf_apex_lsa_cboa = get_test_list_lsa_cboa_f5f6_mtt_apex(
    f5xccf_flow, 
    corner='F5',
    testinput=testinputcboaapex,
    FlowMatrix='CCF_F5_FREQ'
)

f5xccf_apex_lsa_llcrf = get_test_list_lsa_llcrf_f5f6_mtt_apex(
    f5xccf_flow, 
    corner='F5',
    testinput=testinputllcrfapex,
    FlowMatrix='CCF_F5_FREQ'
)

f5xccf_apex_ssa_llcsram = get_test_list_ssa_llcsram_f5f6_mtt_apex(
    f5xccf_flow, 
    corner='F5',
    testinput=testinputllcsramapex,
    FlowMatrix='CCF_F5_FREQ'
)

ARR_CCF_FMAX = Flow("ARR_CCF_FMAX", f5xccf_apex_lsa_cboa, f5xccf_apex_lsa_llcrf, f5xccf_apex_ssa_llcsram)

SUBFLOW = Flow(f'{MODULE}_F5XCCF',

                                        Fitem("SAME", ARR_CCF_FMAX, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                                        f5xccf_vmintc_lsa_cboa,
                                        f5xccf_vmintc_lsa_llcrf,
                                        f5xccf_vmintc_ssa_llcsram
                                        )

#################################################################################
#							FMINXCCF SUBFLOW
#	
#################################################################################

FlowMatrixRule = {
    "CCF_FMIN_MHz"   : "0400",
    "CCF_F1_FREQ_MHz": "1200",
    "CCF_F2_FREQ_MHz": "1500",
    "CCF_F3_FREQ_MHz": "2200",
    "CCF_F4_FREQ_MHz": "3000",
    "CCF_F5_FREQ_MHz": "3600",
    "CCF_F6_FREQ_MHz": "4000",
    }

flow_matrix_definitions = {
    "FMIN": "CCF_FMIN",
    "F1": "CCF_F1_FREQ",
    "F2": "CCF_F2_FREQ",
    "F3": "CCF_F3_FREQ",
    "F4": "CCF_F4_FREQ",   
    "F5": "CCF_F5_FREQ",
    "F6": "CCF_F6_FREQ"
}

fminxccf_flow = "FMINXCCF"

fminxccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
fminxccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
fminxccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

testinputcboa = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "SingleVmin",
    "Bypassport": 1,
    "ISEDC": True
}

fminxccf_vmintc_lsa_cboa = get_test_list_fminxccf_lsa_cboa(
    fminxccf_flow, 
    corner='FMIN',  
    testinput=testinputcboa
)

fminxccf_vmintc_lsa_llcrf = get_test_list_fminxccf_lsa_llcrf(
    fminxccf_flow, 
    corner='FMIN',  
    testinput=testinputllcrf
)

fminxccf_vmintc_ssa_llcsram = get_test_list_fminxccf_ssa_llcsram(
    fminxccf_flow, 
    corner='FMIN',  
    testinput=testinputllcsram
)

FMINXCCF_SUBFLOW = Flow(
    f'{MODULE}_FMINXCCF',
    fminxccf_vmintc_lsa_cboa + fminxccf_vmintc_lsa_llcrf + fminxccf_vmintc_ssa_llcsram

)


#################################################################################
#							ENDCPU SUBFLOW
#
#	- ENDCPU flow will test SSA LLCSRAM PMUX content 
#	
#################################################################################

endcpu_flow = "ENDCPU"

endcpu_vmintc_ssa_llcsram_tli_pmux = {"Bypassport": 1, "ISEDC": True}

testinput = {
    "Testmode": "Scoreboard",
    "Bypassport": 1,
    "ISEDC": True
}

endcpu_vmintc_ssa_llcsram_pmux = get_test_list_endcpu_ssa_llcsram_pmux(
    endcpu_flow, 
    endcpu_vmintc_ssa_llcsram_tli_pmux,
    testinput
)

callback_pmux_tli = {"Bypassport": 1, "ISEDC": True}
callback_pmux = get_test_callback_pmux(endcpu_flow, callback_pmux_tli)

ENDCPU_SUBFLOW = Flow(
    f'{MODULE}_ENDCPU',
    callback_pmux,
    endcpu_vmintc_ssa_llcsram_pmux
)


#################################################################################
#							VMAXXCCFLO SUBFLOW
#
#	
#################################################################################

vmaxxccf_flow = "VMAXXCCFLO"

vmaxxccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
vmaxxccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
vmaxxccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}

testinputllccboa = {
    "Testmode": "Scoreboard",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "Scoreboard",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "Scoreboard",
    "Bypassport": 1,
    "ISEDC": True
}

vmaxxccf_vmintc_lsa_cboa = get_test_list_vmaxxccf1_lsa_cboa(
    vmaxxccf_flow,
    vmaxxccf_vmintc_lsa_cboa_tli,
    testinputllccboa
)

vmaxxccf_vmintc_lsa_llcrf = get_test_list_vmaxxccf1_lsa_llcrf(
    vmaxxccf_flow, 
    vmaxxccf_vmintc_lsa_llcrf_tli,
    testinputllcrf
)

vmaxxccf_vmintc_ssa_llcsram = get_test_list_vmaxxccf1_ssa_llcsram(
    vmaxxccf_flow, 
    vmaxxccf_vmintc_ssa_llcsram_tli,
    testinputllcsram
)

VMAXXCCF_SUBFLOW = Flow(
    f'{MODULE}_VMAXXCCFLO',
    vmaxxccf_vmintc_lsa_cboa + vmaxxccf_vmintc_lsa_llcrf + vmaxxccf_vmintc_ssa_llcsram 
)


#################################################################################
#							VMAXXCCF SUBFLOW
#
#	
#################################################################################

vmaxxccf_flow = "VMAXXCCF"

vmaxxccf_vmintc_lsa_cboa_tli = {"Bypassport": 1, "ISEDC": True}
vmaxxccf_vmintc_lsa_llcrf_tli = {"Bypassport": 1, "ISEDC": True}
vmaxxccf_vmintc_ssa_llcsram_tli = {"Bypassport": 1, "ISEDC": True}


testinputllccboa = {
    "Testmode": "Scoreboard",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcrf = {
    "Testmode": "Scoreboard",
    "Bypassport": 1,
    "ISEDC": True
}

testinputllcsram = {
    "Testmode": "Scoreboard",
    "Bypassport": 1,
    "ISEDC": True
}

vmaxxccf5_vmintc_lsa_cboa = get_test_list_vmaxxccf5_lsa_cboa(
    vmaxxccf_flow,
    vmaxxccf_vmintc_lsa_cboa_tli,
    testinputllccboa
)

vmaxxccf5_vmintc_lsa_llcrf = get_test_list_vmaxxccf5_lsa_llcrf(
    vmaxxccf_flow, 
    vmaxxccf_vmintc_lsa_llcrf_tli,
    testinputllcrf
)

vmaxxccf5_vmintc_ssa_llcsram = get_test_list_vmaxxccf5_ssa_llcsram(
    vmaxxccf_flow, 
    vmaxxccf_vmintc_ssa_llcsram_tli,
    testinputllcsram
)

VMAXXCCF_SUBFLOW = Flow(
    f'{MODULE}_VMAXXCCF',
    vmaxxccf5_vmintc_lsa_cboa + vmaxxccf5_vmintc_lsa_llcrf + vmaxxccf5_vmintc_ssa_llcsram
)
