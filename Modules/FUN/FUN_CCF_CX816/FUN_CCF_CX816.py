# Import the necessary classes from Pymtpl
from pymtpl.por_methods import VminTC, PrimePatConfigTestMethod, RunCallback, DrngTC, ScreenTC, PatternDelayOptimizer, ApexTC, DedcLoadConfigTC, DDGShmooTC, ImpactStudiesVmin # type: ignore
from pymtpl.core import Flow, Fitem, pPass, pFail, NativeMultiTrial, AUTO, InitializeNVLClass, Import, TrialParamSpec, Spec # type: ignore
from pymtpl.binctr import NVLClass8dig # type: ignore
import re

# Define the product name
product = "FUN_CCF"
hptp_speed = "hptp800"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'
STATUSEDC = "E"

######################################################################
# DRNGTC
######################################################################
def get_test_list_DRNGTC_5p0( flow,corner,content, testinput):
    test_listt_DRNGTC_5p0 = []	
    setbin_override = 4580 if content == "FUSE_DRNG" else AUTO
    sample_test_DRNGTC_5p0 = \
        DrngTC(name=f"DRNG_CCF_FUNC_K_ENDCPU_TAP_X_VNOM_X_CCF_DRNGTC_{content}",
                Patlist = f'fun_cdie_{flow.lower()}_{content.lower()}_list',
                LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100',
                BypassPort = testinput.get("Bypassport", -1),
                CtvCapturePins = "IPC::CPU_TDO",
                DrngVersion = "DRNG_50",
                ExpectedCtvSize = 1060,
                FailuresToCaptureTotal = 1060,
                Mode = "ALL",
                ModeOrder = "COLLISION, FUNCTIONAL_METRICS, METRICS_NOXOR, FUNCTIONAL",
                CollisionDataSize = 256,
                CollisionStart = 260,
                MetricsStart = 0,
                MetricsStart_NOXOR = 772,
               _fitem=Fitem('SAME', edc = False,
               r0=pFail(setbin = setbin_override, ret=0),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = setbin_override, ret=0),
               r3=pFail(setbin = setbin_override, ret=0),
               r4=pFail(setbin = setbin_override, ret=0),
               r5=pFail(setbin = setbin_override, ret=0)))
    test_listt_DRNGTC_5p0.append(sample_test_DRNGTC_5p0)
    
    return test_listt_DRNGTC_5p0

def get_test_list_DRNGTC( flow,corner, content, testinput):
    test_listt_DRNGTC = []	
    sample_test_DRNGTC = \
        DrngTC(name=f"DRNG_CCF_FUNC_K_ENDCPU_TAP_X_VNOM_X_CCF_DRNGTC_{content}",
                Patlist = f'fun_cdie_{flow.lower()}_{content.lower()}_list',
                Mode = testinput.get("Mode", "COLLISION"),
                CtvCapturePins = 'IPC::CPU_TDO',
                ExpectedCtvSize = 256,
                CollisionDataSize = 128,
                TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100',
                LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
                FailuresToCaptureTotal = 1060,
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME', edc = False,
               r0=pFail(setbin = AUTO, ret=0),
               r1=pPass(setbin = AUTO, goto="NEXT"),
               r2=pFail(setbin = AUTO, ret=0),
               r3=pFail(setbin = AUTO, ret=0),
               r4=pFail(setbin = AUTO, ret=0),
               r5=pFail(setbin = AUTO, ret=0)))
    test_listt_DRNGTC.append(sample_test_DRNGTC)
    
    return test_listt_DRNGTC

######################################################################

######################################################################
# DRNG_VMINTC
######################################################################

def get_test_list_drngflow(flow,corner,content,testinput):
	
    test_listt_drngflow = []	
    sample_test_drngflow = \
        VminTC(name=f"DRNG_CCF_FUNC_K_ENDCPU_TAP_X_VNOM_X_CCF_VMINTC_{content}",
               Patlist = f'fun_cdie_{flow.lower()}_{content.lower()}_list',
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100',
               LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
               LogLevel = 'Disabled',
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               VoltageTargets = 'VCCR_HC',
	           PatternNameCounterIndexes = '9,10,11,12,13,14,15',
	           SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'"MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.corefreq+''":')+'0.8GHz,MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+''":')+'0.8GHz,MCfunCCF:ratio_modify:0.8GHz"'),
               BaseNumbers = AUTO,
               TestMode = 'Scoreboard',
               ExecutionMode = testinput.get("ExecutionMode","Search"),
               BypassPort = testinput.get("Bypassport", -1),
               ForwardingMode = 'None',
               RecoveryMode = 'Default',
               FailCaptureCount = 999,
	           PinMap = '',
               ScoreboardEdgeTicks = 1,
	           StepSize = 0.02,
	           MaxRepetitionCount = 2,
               _fitem=Fitem('SAME', edc = False,
               r0=pFail(setbin = AUTO, ret=0),
               r1=pPass(setbin = AUTO, goto="NEXT"),
               r2=pFail(setbin = AUTO, ret=0),
               r3=pFail(setbin = AUTO, ret=0),
               r4=pFail(setbin = AUTO, ret=0),
               r5=pFail(setbin = 4519, ret=0)))
    test_listt_drngflow.append(sample_test_drngflow)
    
    return test_listt_drngflow


######################################################################
# CCFBIST VMINTC
######################################################################

def get_test_list_funflow(status, flow,corner, content,testinput):
	
    test_listt_funflow = []	
    sample_test_funflow = \
        VminTC(name=f"SBFT_CCF_VMIN_{status}_{flow}_X_X_VNOM_X_CCF_{content}",
               Patlist = "fun_cdie_endcpu_ccfbist_test_burstoff_list",
               TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100',
               LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
               LogLevel = 'Disabled',
               EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
               StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
               VoltageTargets = 'CCF',
	           PatternNameCounterIndexes = '9,10,11,12,13,14,15',
	           SetPointsPlistParamName = 'Patlist',
	           SetPointsPreInstance=Spec(f'"MCdrv:" + FUN_CCF_{sku}_SPECS.corefreq + ":0.8GHz,MCdrv:" + FUN_CCF_{sku}_SPECS.ringfreq + ":0.8GHz,CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
               BaseNumbers = AUTO,
               FeatureSwitchSettings = 'fivr_mode_on, disable_masked_targets',
               TestMode = 'Scoreboard',
               ExecutionMode = "SearchWithScoreboard",
               BypassPort = testinput.get("Bypassport", -1),
               ForwardingMode = "None",
               RecoveryMode = "NoRecovery",
               FailCaptureCount = 336,
               FivrCondition="NOM_CCF_CORE",
               RecoveryOptions = '',
               RecoveryTrackingIncoming = '',
               RecoveryTrackingOutgoing = '',
               VminResult = '',
	           PinMap = '',
               ScoreboardEdgeTicks = 1,
	           StepSize = 0.02,
	           MaxRepetitionCount = 1,
	           MaxFailsNum = 10,
               _fitem=Fitem('SAME', edc = False,
               r0=pFail(setbin = AUTO, ret=0),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = AUTO, ret=0),
               r3=pFail(setbin = AUTO, ret=0),
               r4=pFail(setbin = AUTO, ret=0),
               r5=pFail(setbin = AUTO, ret=0)))
    test_listt_funflow.append(sample_test_funflow)
    
    return test_listt_funflow
####################################################################################
def get_test_apextc(flow, corner, core_corner, FlowMatrix, subflow, content_list):
     
   test_list_apextcflow = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
      test_list_apextcflow.append(ApexTC(name=f'SBFT_CCF_VMIN_K_{flow}_X_X_{corner}_X_{test_type}_APEXTC',
         BypassPort = test_parms["Bypass"],
         Targets = "CCF_FUNCCF",
         InitialMaskBits = "",
         ForwardingMode = "None",
         #FeatureSwitchSettings = 'fivr_mode_on, disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
         DtsConfiguration = "",
         PinMap = "",
         #SetPointsPreInstance = Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
         SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET"'), 
         SetPointsPostInstance=Spec(f'PSPOST.CLR_{corner}+","+"CORE:nblctrl_core_l2:nblon"'),
         PreInstance = Spec(f'FUN_CCF_{sku}_SPECS.UncoreConfigPreinstance'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc=Spec(f'__shared__::TpRule.If_DS0_DS1_M("FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf_n2p","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf")'),
         Patlist = 'IPC::'f"fun_cdie_vccr_sbft_fmax_{test_type.lower()}_{hptp_speed}_burstoff_list",
         PatternNameCounterIndexes = Spec(f'FUN_CCF_{sku}_SPECS.PatNameIndex'),
         RecoveryOptions = "",
         RecoveryTracking = "",
         End = Spec(f'__shared__::FlowMatrixSingular.APEX_CCF_MIN'),
         Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CCF_MAX'),
         StepSize = 3,
         FivrCondition = "NOM_CCF_CORE",
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter=  Spec(f'"--overrides CCF:"+__shared__::FlowMatrixSingular.CCF_VMAX_VALUE+", CORE3:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE2:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE1:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE0:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE"'),
         ExportTokens = "FXCCF",
         _fitem=Fitem('SAME', edc=test_parms["IS_EDC"],
                             r0=pFail(setbin=4551),
                             r1=pPass(setbin=AUTO, goto="NEXT"),
                             r2=pFail(setbin=4551),
                             r3=pFail(setbin=4551),
                             r4=pFail(setbin=-45),
                             r5=pFail(setbin=-45))))
  
   return test_list_apextcflow
####################################################################################
def get_test_list_fmin(flow, corner, core_corner, FlowMatrix, subflow, content_list):
    test_list_funflow = []
    for test_type, test_parms in content_list.items():
        # Force CornerIdentifiers to "CCF0@F1" for FMINXCCF and F1XCCF subflows
        if subflow in ["FMINXCCF", "F1XCCF"]:
            corner_identifier = "CCF0@F1"
        else:
            corner_identifier = f"CCF0@{corner}"
        if subflow == "FMINXCCF":
            limit_guardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)')
        else:
            limit_guardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)')

        test_list_funflow.append(NativeMultiTrial(
            name=f"SBFT_CCF_VMIN_K_{subflow}_X_CCF_{corner}_X_{test_type}",
            exitaction="Restore" if test_parms["IS_EDC"] else "Continue",
            trialvar="CPU_TRIALS::FlowDomain.RING",
            _comment='Sample VminTC test with MTT',
            template=VminTC(
                name=f'"SBFT_CCF_VMIN_K_{subflow}_X_CCF_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
                BypassPort=Spec(test_parms["Bypass"]),
                ExecutionMode="SearchWithScoreboard" if "XCCF" in flow else "SearchWithScoreboard",
                ScoreboardEdgeTicks=Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
                MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
                TestMode="SingleVmin",
                #ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                ForwardingMode="Input" if ("IS_EDC" in test_parms or "FC_DRG" in test_type) else "InputOutput",
                FeatureSwitchSettings='fivr_mode_on, disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                #DtsConfiguration="FUN_CCF_CDIE_S28C",
                DtsConfiguration = Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_CCF_CX816_SPECS.dts_s28c, FUN_CCF_CX816_SPECS.dts_s52cc, FUN_CCF_CX816_SPECS.dts_hx28c, FUN_CCF_CX816_SPECS.dts_default)'),
                LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                TimingsTc="FUN_CCF_CX816::cpu_fun_timing_mts400_tstprtclk200_tck50_i_drv_mul_fmin_fun_CCF",
                Patlist='IPC::'f"fun_cdie_vccr_sbft_{corner.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list" if "FMIN" in corner else 'IPC::'f"fun_cdie_vccr_sbft_{subflow.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list_master",
                BaseNumbers=None if "SCR" in flow else AUTO,
                CornerIdentifiers=f"CCF0@F1",
                EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL") if ("F1" in corner or "FMIN" in corner) else Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
                LimitGuardband=Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
                PinMap="",
                PatternNameCounterIndexes=Spec(f'FUN_CCF_{sku}_SPECS.PatNameIndex'),
                RecoveryMode="NoRecovery",
                RecoveryOptions="",
                RecoveryTrackingIncoming="",
                RecoveryTrackingOutgoing="",
                SetPointsPlistParamName="Patlist",
                StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                VoltageTargets="CCF",
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                FivrCondition="NOM_CCF_CORE",
                FivrConditionPlistParamName="Patlist",
                VoltageConverter=  Spec(f'"--overrides CORE3:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE2:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE1:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE0:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE"'),
                StepSize=Spec(f"toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)"),
                PreInstance = Spec(f'FUN_CCF_{sku}_SPECS.UncoreConfigPreinstance'),
                SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET,"+FUN_CCF_CX816_SPECS.MCfunCCF_FMIN_DRVMASK'),
                SetPointsPostInstance=Spec(f'PSPOST.CLR_{corner}+","+"CORE:nblctrl_core_l2:nblon,"+FUN_CCF_CX816_SPECS.MCfunCCF_FMIN_DRVMASK'),
            ),
            r0=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r1=pPass(setbin=AUTO, ret=1, trialaction="Exit"),
            r2=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r3=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r4=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r5=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1=  pPass(setbin=AUTO),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=AUTO),
                        r5 = pFail(setbin=AUTO))))
    return test_list_funflow

####################################################################################
def get_test_list_fminfailflow(flow, corner, core_corner, FlowMatrix, subflow, content_list):
    test_list_funflow = []
    for test_type, test_parms in content_list.items():
        # Force CornerIdentifiers to "CCF0@F1" for FMINXCCF and F1XCCF subflows
        if subflow in ["FMINXCCF", "F1XCCF"]:
            corner_identifier = "CCF0@F1"
        else:
            corner_identifier = f"CCF0@{corner}"
        if subflow == "FMINXCCF":
            limit_guardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)')
        else:
            limit_guardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)')

        test_list_funflow.append(VminTC(name=f"SBFT_CCF_VMIN_K_{subflow}_X_CCF_{corner}_X_{test_type}_FAILFLOW",
                BypassPort=Spec(test_parms["Bypass"]),
                ExecutionMode="Search" if "XCCF" in flow else "SearchWithScoreboard",
                ScoreboardEdgeTicks=Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
                MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
                TestMode="SingleVmin",
                ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                FeatureSwitchSettings='fivr_mode_on, disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                #DtsConfiguration="FUN_CCF_CDIE_S28C",
                DtsConfiguration = Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_CCF_CX816_SPECS.dts_s28c, FUN_CCF_CX816_SPECS.dts_s52cc, FUN_CCF_CX816_SPECS.dts_hx28c, FUN_CCF_CX816_SPECS.dts_default)'),
                LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                TimingsTc="FUN_CCF_CX816::cpu_fun_timing_mts400_tstprtclk200_tck50_i_drv_mul_fmin_fun_CCF",
                Patlist='IPC::'f"fun_cdie_vccr_sbft_{corner.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list" if "FMIN" in corner else 'IPC::'f"fun_cdie_vccr_sbft_{subflow.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list_master",
                BaseNumbers=None if "SCR" in flow else AUTO,
                #CornerIdentifiers=corner_identifier,
                EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL") if ("F1" in corner or "FMIN" in corner) else Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
                #LimitGuardband="" if test_parms["IS_EDC"] else limit_guardband,
                PinMap="",
                PatternNameCounterIndexes=Spec(f'FUN_CCF_{sku}_SPECS.PatNameIndex'),
                RecoveryMode="NoRecovery",
                RecoveryOptions="",
                RecoveryTrackingIncoming="",
                RecoveryTrackingOutgoing="",
                SetPointsPlistParamName="Patlist",
                StartVoltagesOffset=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StartVoltagesForRetry=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                VoltageTargets="CCF",
                #FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                FivrCondition="NOM_CCF_CORE",
                FivrConditionPlistParamName="Patlist",
                VoltageConverter=Spec(f'"--overrides CORE3:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE2:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE1:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE0:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE"'),
                StepSize=Spec(f"toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)"),
                PreInstance=Spec(f'FUN_CCF_{sku}_SPECS.UncoreConfigPreinstance'),
                SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET,"+FUN_CCF_CX816_SPECS.MCfunCCF_FMIN_DRVMASK'),
                SetPointsPostInstance=Spec(f'PSPOST.CLR_{corner}+","+"CORE:nblctrl_core_l2:nblon,"+FUN_CCF_CX816_SPECS.MCfunCCF_FMIN_DRVMASK'),
                _fitem=Fitem('SAME', edc=test_parms["IS_EDC"],
                             r0=pFail(setbin=AUTO, ret=1),
                             r1=pPass(setbin=AUTO, goto="NEXT"),
                             r2=pFail(setbin=AUTO, ret=1),
                             r3=pFail(setbin=AUTO, ret=1),
                             r4=pFail(setbin=AUTO, ret=1),
                             r5=pFail(setbin=AUTO, ret=1))
            )
        )
    return test_list_funflow

####################################################################################
def get_test_list_f1_f4(flow, corner, core_corner, FlowMatrix, subflow, content_list):
    test_list_funflow = []
    for test_type, test_parms in content_list.items():
        # Force CornerIdentifiers to "CCF0@F1" for FMINXCCF and F1XCCF subflows
        if subflow in ["FMINXCCF", "F1XCCF"]:
            corner_identifier = "CCF0@F1"
        else:
            corner_identifier = f"CCF0@{corner}"
        if subflow == "FMINXCCF":
            limit_guardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)')
        else:
            limit_guardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)')

        test_list_funflow.append(NativeMultiTrial(
            name=f"SBFT_CCF_VMIN_K_{subflow}_X_CCF_{corner}_X_{test_type}",
            exitaction="Restore" if test_parms["IS_EDC"] else "Continue",
            trialvar="CPU_TRIALS::FlowDomain.RING",
            _comment='Sample VminTC test with MTT',
            template=VminTC(
                name=f'"SBFT_CCF_VMIN_K_{subflow}_X_CCF_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
                BypassPort=Spec(test_parms["Bypass"]),
                ExecutionMode="SearchWithScoreboard" if "XCCF" in flow else "SearchWithScoreboard",
                ScoreboardEdgeTicks=Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
                MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
                TestMode="SingleVmin",
                ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                FeatureSwitchSettings='fivr_mode_on, disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                #DtsConfiguration="FUN_CCF_CDIE_S28C",
                DtsConfiguration = Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_CCF_CX816_SPECS.dts_s28c, FUN_CCF_CX816_SPECS.dts_s52cc, FUN_CCF_CX816_SPECS.dts_hx28c, FUN_CCF_CX816_SPECS.dts_default)'),
                LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                TimingsTc=Spec(f'__shared__::TpRule.If_DS0_DS1_M("FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf_n2p","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf")'),
                Patlist='IPC::'f"fun_cdie_vccr_sbft_{corner.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list" if "FMIN" in corner else 'IPC::'f"fun_cdie_vccr_sbft_{subflow.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list_master",
                BaseNumbers=None if "SCR" in flow else AUTO,
                CornerIdentifiers=corner_identifier,
                EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL") if ("F1" in corner or "FMIN" in corner) else Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
                LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                PinMap="",
                PatternNameCounterIndexes=Spec(f'FUN_CCF_{sku}_SPECS.PatNameIndex'),
                RecoveryMode="NoRecovery",
                RecoveryOptions="",
                RecoveryTrackingIncoming="",
                RecoveryTrackingOutgoing="",
                SetPointsPlistParamName="Patlist",
                StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                VoltageTargets="CCF",
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                FivrCondition="NOM_CCF_CORE",
                FivrConditionPlistParamName="Patlist",
                VoltageConverter=  Spec(f'"--overrides CORE3:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE2:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE1:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE0:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE"'),
                StepSize=Spec(f"toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)"),
                PreInstance = Spec(f'FUN_CCF_{sku}_SPECS.UncoreConfigPreinstance'),
                SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET"'), 
                SetPointsPostInstance=Spec(f'PSPOST.CLR_{corner}+","+"CORE:nblctrl_core_l2:nblon"'),
            ),
            r0=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r1=pPass(setbin=AUTO, ret=1, trialaction="Exit"),
            r2=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r3=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r4=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r5=pFail(setbin=AUTO, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=AUTO),
                        r5 = pFail(setbin=AUTO))
        ))
    return test_list_funflow

####################################################################################
def get_test_list_vmax(flow, corner, core_corner, FlowMatrix, subflow, content_list):
    """
    Returns a list of VminTC tests (non-MTT) for the provided arguments.
    """
    test_list_funflow = []
    for test_type, test_parms in content_list.items():
        # Force CornerIdentifiers to "CCF0@F1" for FMINXCCF and F1XCCF subflows
        if subflow in ["FMINXCCF", "F1XCCF"]:
            corner_identifier = "CCF0@F1"
        else:
            corner_identifier = f"CCF0@{corner}"
        if subflow == "FMINXCCF":
            limit_guardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)')
        else:
            limit_guardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)')

        test_list_funflow.append(
            VminTC(
                name=f"SBFT_CCF_VMAX_K_{subflow}_X_CCF_{corner}_X_{test_type}",
                BypassPort=Spec(test_parms["Bypass"]),
                ExecutionMode="SearchWithScoreboard" if "XCCF" in flow else "SearchWithScoreboard",
                ScoreboardEdgeTicks=Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
                MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
                TestMode="Scoreboard",
                ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                FeatureSwitchSettings='fivr_mode_on, disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                #DtsConfiguration="FUN_CCF_CDIE_S28C",
                DtsConfiguration = Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_CCF_CX816_SPECS.dts_s28c, FUN_CCF_CX816_SPECS.dts_s52cc, FUN_CCF_CX816_SPECS.dts_hx28c, FUN_CCF_CX816_SPECS.dts_default)'),
                LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
                TimingsTc=Spec(f'__shared__::TpRule.If_DS0_DS1_M("FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf_n2p","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf")'),
                Patlist='IPC::'f"fun_cdie_vccr_sbft_{flow.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list",
                BaseNumbers= AUTO,
                #CornerIdentifiers=corner_identifier,
                EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE"),
                StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE"),
                LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                PinMap="",
                PatternNameCounterIndexes=Spec(f'FUN_CCF_{sku}_SPECS.PatNameIndex'),
                RecoveryMode="NoRecovery",
                RecoveryOptions="",
                RecoveryTrackingIncoming="",
                RecoveryTrackingOutgoing="",
                SetPointsPlistParamName="Patlist",
                #StartVoltagesOffset=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                #StartVoltagesForRetry=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                VoltageTargets="CCF",
                #FlowIndex=Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                FivrCondition="NOM_CCF_CORE",
                FivrConditionPlistParamName="Patlist",
                VoltageConverter=Spec(f'"--overrides CCF:"+__shared__::FlowMatrixSingular.CCF_VMAX_VALUE+",CORE3:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE2:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE1:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE0:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE"'),
                StepSize=Spec(f"toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)"),
                PreInstance=Spec(f'FUN_CCF_{sku}_SPECS.UncoreConfigPreinstance'),
                SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET"'), 
                SetPointsPostInstance=Spec(f'PSPOST.CLR_{corner}+","+"CORE:nblctrl_core_l2:nblon"'),
                _fitem=Fitem('SAME', edc=test_parms["IS_EDC"],
                             r0=pFail(setbin=AUTO),
                             r1=pPass(setbin=AUTO, goto="NEXT"),
                             r2=pFail(setbin=AUTO),
                             r3=pFail(setbin=AUTO),
                             r4=pFail(setbin=AUTO),
                             r5=pFail(setbin=AUTO))
            )
        )
    return test_list_funflow
####################################################################################

def get_test_list_vmaxF5(flow, corner, core_corner, FlowMatrix, corner_id, subflow, content_list):
    """
    Returns a list of NativeMultiTrial VMAX tests (MTT) for the provided arguments, similar to get_test_list_F5F6F7.
    """
    test_list = []

    for test_type, test_parms in content_list.items():
        limit_guardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)')
        test_list.append(
            NativeMultiTrial(
                name=f"SBFT_CCF_VMAX_K_{subflow}_X_CCF_{corner}_X_{test_type}",
                exitaction="Restore" if test_parms["IS_EDC"] else "Continue",
                trialvar="CPU_TRIALS::FlowDomain.RING_TOP",
                _comment='SpeedFlow F5 VMAXTC with MTT',
                template=VminTC(
                    #name=f'"SBFT_CCF_VMAX_K_{corner}XCCF_X_CCF_" + ' + Spec(f"__shared__::Corners.CCF_{corner_id}") + f' + "_" + ' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}") + f' + "_{test_type}"',
                    name=f'"SBFT_CCF_VMAX_K_VMAXXCCFLO_X_CCF_" + ' + Spec(f"__shared__::Corners.CCF_{corner_id}") + f' + "_" + ' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}") + f' + "_{test_type}"' if ("VMAXXCCFLO" in VMAXXCCF_Subflow) else f'"SBFT_CCF_VMAX_K_VMAXXCCF_X_CCF_" + ' + Spec(f"__shared__::Corners.CCF_{corner_id}") + f' + "_" + ' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}") + f' + "_{test_type}"',
                    BypassPort=Spec(test_parms["Bypass"]),
                    ExecutionMode="SearchWithScoreboard" if "XCCF" in flow else "SearchWithScoreboard",
                    ScoreboardEdgeTicks=Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
                    MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
                    TestMode="Scoreboard",
                    ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                    FeatureSwitchSettings='fivr_mode_on, disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                    #DtsConfiguration="FUN_CCF_CDIE_S28C",
                    DtsConfiguration = Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_CCF_CX816_SPECS.dts_s28c, FUN_CCF_CX816_SPECS.dts_s52cc, FUN_CCF_CX816_SPECS.dts_hx28c, FUN_CCF_CX816_SPECS.dts_default)'),
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
                    TimingsTc=Spec(f'__shared__::TpRule.If_DS0_DS1_M("FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf_n2p","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf")'),
                    Patlist=f'IPC::fun_cdie_vccr_sbft_{subflow.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list',
                    BaseNumbers= AUTO,
                    #CornerIdentifiers=TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CCF_{corner_id}")),
                    EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE"),
                    StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE"),
                    #StartVoltagesOffset=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                    #StartVoltagesForRetry=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                    LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                    PinMap="",
                    FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                    PatternNameCounterIndexes=Spec(f'FUN_CCF_{sku}_SPECS.PatNameIndex'),
                    RecoveryMode="NoRecovery",
                    RecoveryOptions="",
                    RecoveryTrackingIncoming="",
                    RecoveryTrackingOutgoing="",
                    SetPointsPlistParamName="Patlist",
                    VoltageTargets="CCF",
                    FivrCondition="NOM_CCF_CORE",
                    FivrConditionPlistParamName="Patlist",
                    VoltageConverter=Spec(f'"--overrides CCF:"+__shared__::FlowMatrixSingular.CCF_VMAX_VALUE+",CORE3:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE2:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE1:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE0:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE"'),
                    StepSize=Spec(f"toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)"),
                    PreInstance=Spec(f'FUN_CCF_{sku}_SPECS.UncoreConfigPreinstance'),
                    SetPointsPreInstance=TrialParamSpec(Spec(
                        f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +
                        Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":"') +
                        Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +
                        '"GHz,MCdrv:"+' +
                        Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":"') +
                        Spec(f"+ __shared__::FreqValues.CCF_{corner_id}+") +
                        '"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET"'
                    )),
                    SetPointsPostInstance=Spec(f'PSPOST.CLR_{corner}+","+"CORE:nblctrl_core_l2:nblon"'),
                ),
                r0=pFail(setbin=AUTO, ret=0, trialaction="Exit"),
                r1=pPass(setbin=AUTO, ret=1, trialaction="Exit"),
                r2=pFail(setbin=AUTO, ret=0, trialaction="Exit"),
                r3=pFail(setbin=AUTO, ret=0, trialaction="Exit"),
                r4=pFail(setbin=AUTO, ret=0, trialaction="Exit"),
                r5=pFail(setbin=AUTO, ret=0, trialaction="Exit"),
                _fitem=Fitem('SAME', edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=AUTO),
                    r1=pPass(setbin=AUTO, goto="NEXT"),
                    r2=pFail(setbin=AUTO),
                    r3=pFail(setbin=AUTO),
                    r4=pFail(setbin=AUTO),
                    r5=pFail(setbin=AUTO))))

    return test_list

####################################################################################
def get_test_list_F5F6F7(flow, corner, core_corner, FlowMatrix, corner_id, subflow, content_list):
    """
    Returns a list of NativeMultiTrial tests based on the provided arguments.
    """
    test_list = []

    for test_type, test_parms in content_list.items():
        # Set TestMode and VoltageTargets based on test_parms or other logic if needed
        if "PMUX" in test_parms and test_parms["PMUX"]:
            TestMode = "SingleVmin"
            VoltageTargets = "CCF"
        else:
            TestMode = "SingleVmin"
            VoltageTargets = "CCF"
        limit_guardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)')
        test_list.append(
            NativeMultiTrial(name=f"SBFT_CCF_VMIN_K_{subflow}_X_CCF_{corner}_X_{test_type}",
                    exitaction="Restore" if test_parms["IS_EDC"] else "Continue",
                    trialvar="CPU_TRIALS::FlowDomain.RING_TOP",
                    _comment='SpeedFlow F5 F6 F7 VminTC with MTT',
                    template=VminTC(
                    #name=f'"SBFT_CCF_VMIN_K_{corner}XCCF_X_CCF_" + ' + Spec(f"__shared__::Corners.CCF_{corner_id}") +f' + "_" + ' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}") + f' + "_{test_type}"',
                    name=f'"SBFT_CCF_VMIN_K_{corner}XCCFLO_X_CCF_" + ' + Spec(f"__shared__::Corners.CCF_{corner_id}") +f' + "_" + ' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}") + f' + "_{test_type}"' if ("F5XCCFLO" in XCCFF5_SubFlow) else f'"SBFT_CCF_VMIN_K_{corner}XCCF_X_CCF_" + ' + Spec(f"__shared__::Corners.CCF_{corner_id}") +f' + "_" + ' + Spec(f"__shared__::FreqInMHZ.CCF_{corner_id}") + f' + "_{test_type}"',
                    BypassPort=Spec(test_parms["Bypass"]),
                    ExecutionMode="SearchWithScoreboard" if "XCCF" in flow else "SearchWithScoreboard",
                    ScoreboardEdgeTicks=Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
                    MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
                    TestMode=TestMode,
                    ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                    FeatureSwitchSettings='fivr_mode_on, disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                    #DtsConfiguration="FUN_CCF_CDIE_S28C",
                    DtsConfiguration = Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_CCF_CX816_SPECS.dts_s28c, FUN_CCF_CX816_SPECS.dts_s52cc, FUN_CCF_CX816_SPECS.dts_hx28c, FUN_CCF_CX816_SPECS.dts_default)'),
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                    TimingsTc=Spec(f'__shared__::TpRule.If_DS0_DS1_M("FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf_n2p","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf")'),
                    Patlist=f'IPC::fun_cdie_vccr_sbft_{subflow.lower()}_{test_type.lower()}_{hptp_speed}_burstoff_list_master',
                    BaseNumbers=None if "SCR" in flow else AUTO,
                    CornerIdentifiers=TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CCF_{corner_id}")),
                    EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"),
                    StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
                    StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                    StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                    LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                    PinMap="",
                    FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                    PatternNameCounterIndexes=Spec(f'FUN_CCF_{sku}_SPECS.PatNameIndex'),
                    RecoveryMode="NoRecovery",
                    RecoveryOptions="",
                    RecoveryTrackingIncoming="",
                    RecoveryTrackingOutgoing="",
                    SetPointsPlistParamName="Patlist",
                    VoltageTargets=VoltageTargets,
                    FivrCondition="NOM_CCF_CORE",
                    FivrConditionPlistParamName="Patlist",
                    VoltageConverter = Spec(f'"--overrides CORE3:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE2:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE1:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+",CORE0:"+FUN_CCF_CX816_SPECS.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE"'),
                    StepSize=Spec(f"toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)"),
                    PreInstance = Spec(f'FUN_CCF_{sku}_SPECS.UncoreConfigPreinstance'),
                    #SetPointsPreInstance = "",
                    #SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CLR_{core_corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz"'),
                    #SetPointsPreInstance = TrialParamSpec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
                    SetPointsPreInstance = TrialParamSpec(Spec(f'PSPRE.CLR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}+")+'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET"')),
                    SetPointsPostInstance=Spec(f'PSPOST.CLR_{corner}+","+"CORE:nblctrl_core_l2:nblon"'),
                ),
                r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
                r2=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r4 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r5 = pFail(setbin=test_parms.get("Binning",AUTO)))

            )
        )

    return test_list

######################################################################
# ScreenTC
######################################################################
def get_test_list_ScreenGSDS(flow,testinput):
    test_listt_ScreenGSDS = []	       
    test_listt_ScreenGSDS.append(
        ScreenTC(name=f"SBFT_CCF_SCREEN_X_{flow}_X_X_X_X_X_X_X_CORE_SCREEN_"+testinput.get("Config",""),
               ScreenTestSet = testinput.get("ScreenTestSet", f"FUN_CCF_SCREEN_{testinput.get('Config','')}"),
	           ScreenTestsFile = f"./InputFiles/SBFT_CCF_Downsku_screen.txt",
               #ScreenTestsFile = Spec(MODULEPATH +' + "./InputFiles/SBFT_CCF_Downsku_screen.txt"'),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4549, goto="NEXT", ctr = 0), ### setbin = AUTO/ setbin = -44
               r1=pPass(goto="NEXT")))
                                 )
    
    return test_listt_ScreenGSDS

def get_test_list_ScreenGSDS_2(flow,testinput):
    test_listt_ScreenGSDS_2 = []	
        
    for test_type, test_parms in testinput.items():
        test_listt_ScreenGSDS_2.append(
            ScreenTC(
                   name=f"SBFT_CCF_SCREEN_X_{flow}_X_X_X_X_CORE_SCREEN_{test_type}",
                   ScreenTestSet = test_parms.get("ScreenTestSet", f"FUN_CCF_SCREEN_{test_type}"),
	               ScreenTestsFile = f"./InputFiles/SBFT_CCF_Downsku_screen.txt",
                   #ScreenTestsFile = Spec(MODULEPATH +' + "./InputFiles/SBFT_CCF_Downsku_screen.txt"'),
                   BypassPort = Spec(test_parms["Bypassport"]),
                   
                   ))
    
    return test_listt_ScreenGSDS_2

def get_test_list_ScreenGSDS_vmax(flow,testinput,suffix):
    get_test_list_ScreenGSDS_vmax = []	
        
    for test_type, test_parms in testinput.items():
        get_test_list_ScreenGSDS_vmax.append(
            ScreenTC(
                   name=f"SBFT_CCF_SCREEN_X_{flow}_X_X_X_X_CORE_SCREEN_{test_type}_{suffix}",
                   ScreenTestSet = test_parms.get("ScreenTestSet", f"FUN_CCF_SCREEN_{test_type}"),
	               ScreenTestsFile = f"./InputFiles/SBFT_CCF_Downsku_screen.txt",
                   #ScreenTestsFile = Spec(MODULEPATH +' + "./InputFiles/SBFT_CCF_Downsku_screen.txt"'),
                   BypassPort = Spec(test_parms["Bypassport"]),
                   
                   ))
    
    return get_test_list_ScreenGSDS_vmax

def get_test_list_ScreenGSDS_3(flow, testinput, cornerid):
    test_listt_ScreenGSDS_3 = []	
    for test_type, test_parms in testinput.items():
        # Special handling for SBFT_CCF_SCREEN_X_F5XCCF_X_X_X_X_CORE_SCREEN_FMAX_SINGLEFLOW
        if (
            flow == "F5XCCF"
            and cornerid == "FMAX"
            and test_type == "SINGLEFLOW"
        ):
            test_listt_ScreenGSDS_3.append(
                ScreenTC(
                    name="SBFT_CCF_SCREEN_X_F5XCCF_X_X_X_X_CORE_SCREEN_FMAX_SINGLEFLOW",
                    ScreenTestSet=test_parms.get("ScreenTestSet", "FUN_CCF_MM_SCREEN_SingleFlow"),
                    ScreenTestsFile="./InputFiles/SBFT_CCF_Downsku_screen.txt",
                    BypassPort=Spec(test_parms["Bypassport"]),
                    _fitem=Fitem(
                        "SAME",
                        edc=test_parms.get("IS_EDC", False),
                        r0=pFail(setbin=4520),  # Only this test gets the new bin
                        r1=pPass(goto="NEXT"),
                        r2=pPass(goto="NEXT"),
                        r3=pPass(goto="NEXT"),
                        r4=pPass(goto="NEXT"),
                        r5=pPass(goto="NEXT"),
                        r6=pPass(goto="NEXT"),
                        r7=pPass(goto="NEXT"),
                        r9=pPass(goto="NEXT"),
                        r10=pPass(goto="NEXT"),
                        r11=pPass(goto="NEXT"),
                        r12=pPass(goto="NEXT"),
                        r13=pPass(goto="NEXT"),
                        r14=pPass(goto="NEXT"),
                        r15=pPass(goto="NEXT"),
                    ),
                )
            )
        else:
            test_listt_ScreenGSDS_3.append(
                ScreenTC(
                    name=f"SBFT_CCF_SCREEN_X_{flow}_X_X_X_X_CORE_SCREEN_{cornerid}_{test_type}",
                    ScreenTestSet=test_parms.get("ScreenTestSet", f"FUN_CCF_MM_SCREEN_{test_type}"),
                    ScreenTestsFile="./InputFiles/SBFT_CCF_Downsku_screen.txt",
                    BypassPort=Spec(test_parms["Bypassport"]),
                    _fitem=Fitem(
                        "SAME",
                        edc=test_parms.get("IS_EDC", False),
                        r0=pFail(setbin=AUTO),
                        r1=pPass(goto="NEXT"),
                        r2=pPass(goto="NEXT"),
                        r3=pPass(goto="NEXT"),
                        r4=pPass(goto="NEXT"),
                        r5=pPass(goto="NEXT"),
                        r6=pPass(goto="NEXT"),
                        r7=pPass(goto="NEXT"),
                        r9=pPass(goto="NEXT"),
                        r10=pPass(goto="NEXT"),
                        r11=pPass(goto="NEXT"),
                        r12=pPass(goto="NEXT"),
                        r13=pPass(goto="NEXT"),
                        r14=pPass(goto="NEXT"),
                        r15=pPass(goto="NEXT"),
                    ),
                )
            )
    return test_listt_ScreenGSDS_3


def get_test_list_ScreenGSDS_APEX(flow,testinput):
    test_listt_ScreenGSDS_APEX = []	
        
    for test_type, test_parms in testinput.items():
        test_listt_ScreenGSDS_APEX.append(
            ScreenTC(
                   name=f"SBFT_CCF_SCREEN_X_{flow}_X_X_X_X_APEX_SCREEN_{test_type}",
                   ScreenTestSet = test_parms.get("ScreenTestSet", f"FUN_CCF_SCREEN_{test_type}"),
	               ScreenTestsFile = f"./InputFiles/SBFT_CCF_Downsku_screen.txt",
                   #ScreenTestsFile = Spec(MODULEPATH +' + "./InputFiles/SBFT_CCF_Downsku_screen.txt"'),
                   BypassPort = Spec(test_parms["Bypassport"]),
                   )
                                     )
    
    return test_listt_ScreenGSDS_APEX
######################################################################

######################################################################
# PrimePatConfigTestMethod Fuse Overrides
######################################################################
def get_init_fuse_list(subflow, corner, content_list):
     
   test_list_init = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
       plist_value = test_parms.get("Plist",f"fun_cdie_vccr_sbft_{test_parms.get('subflow', subflow).lower()}_fc_drg_{test_parms.get('core', 'c1').lower()}_{hptp_speed}_list_master")
       config_file = test_parms.get("ConfigurationFile",Spec(MODULEPATH + ' + ' + f'"./Modules/FUN/FUN_CCF_{sku}/InputFiles/FUN_CCF_Generic.PatConfigSetpoints.json"'))
       setpoint_value = test_parms.get("SetPoint","FUSE_OVERRIDES")
       test_list_init.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_FUSE_{test_type}",
               Plist = plist_value,
               ConfigurationFile = config_file,
               SetPoint = setpoint_value,
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -45, ret=0, ctr = 0),
               r1=pPass(goto="NEXT")
               )
              )
             )
   return test_list_init

######################################################################
# ApexTC INIT RunCallback
######################################################################
def get_init_apextc_list(content_list):
     
   test_list_apextc_init = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
        test_list_apextc_init.append(RunCallback(name=f"SBFT_CORE_X_K_INIT_X_X_X_X_VMIN_{test_type}",
               Parameters = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CCF_{sku}/InputFiles/ApexTC_Input_Config.json"'),
               Callback = 'ReadFrequencyPatConfigFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -45, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_apextc_init

################# START MTPL FLOW DEFINITON #####################

def get_test_type_from_name(name, content_list):
    for key in content_list:
        if key in name:
            return key
    return None

######################################################################
# DEDC LoadConfig
######################################################################
def get_init_dedc_list(content_list):
     
   test_list_dedc = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
        test_list_dedc.append(DedcLoadConfigTC(name=f"SBFT_CCF_{test_type}_K_INIT_X_X_X_X_CONFIG",
               	BypassPort = 1,
                ConfigFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CCF_{sku}/InputFiles/FUN_CCF_DEDC.json"'),
                Scope = "LOCAL",
                ValidationMode = "SYNTAX_AND_RULES",
                CoreAware = "ENABLE",
                Modules = f"FUN_CCF_{sku}",
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -45, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_dedc

######################################################################
# DEDC DDGSHMOO
######################################################################
def get_shmoo_list(content_list, corner=None, core_corner=None, FlowMatrix=None, sku=None):
    """
    Returns a list of DDGShmooTC tests for the given content_list.
    For the DRG test type, generates a variant for each of FMIN, F1, F2, F3, F4, F5 with the correct Patlist.
    """
    test_list_shmoo = []

    for test_type, test_parms in content_list.items():
        if re.match(r"^DRG", test_type):
            # Generate a variant for each corner
                if test_type == "DRG_FMIN":
                    patlist_value = f"fun_cdie_vccr_sbft_fmin_fc_drg_hptp800_burstoff_list"
                    TimingsTc="FUN_CCF_CX816::cpu_fun_timing_mts400_tstprtclk200_tck50_i_drv_mul_fmin_fun_CCF"
                    XAxisRange="360e6:10e6:12"
                    SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET,"+FUN_CCF_CX816_SPECS.MCfunCCF_FMIN_DRVMASK')
                else:
                    patlist_value = f"fun_cdie_vccr_sbft_{test_parms.get('CORNER').lower()}xccf_fc_drg_hptp800_burstoff_list_master"
                    TimingsTc=Spec(f'__shared__::TpRule.If_DS0_DS1_M("FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf_n2p","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf","FUN_CCF_CX816::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_ccf")')
                    XAxisRange="750e6:10e6:12"
                    SetPointsPreInstance=Spec(f'"MCdrv:"+' + Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{test_parms.get('CORE_FREQ')}+") +'"GHz,MCdrv:"+' + Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":"') +Spec(f"+ __shared__::FlowMatrixSingular.CCF_{test_parms.get('RING_FREQ')}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET"')
                test_list_shmoo.append(
                    DDGShmooTC(
                        name=f"SBFT_CCF_SHMOO_E_FMINXCCF_X_X_X_X_DRG_{test_parms.get('CORNER')}",
                        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                        Patlist=patlist_value,
                        PrintFormat="ECADS",
                        SetPointsPlistParamName="Patlist",
                        SetPointsPreInstance=SetPointsPreInstance,
                        TimingsTc=TimingsTc,
                        VoltageConverter=Spec(f'"--overrides CORE3:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE2:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE1:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE0:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE --fivrcondition NOM_CCF_CORE"'),
                        XAxisParam="p_all_mts",
                        XAxisRange=XAxisRange,
                        XAxisType="SpecSetVariable",
                        XAxisParamType="UserDefined",
                        YAxisParam="CCF",
                        YAxisRange="1.1:-0.05:14",
                        YAxisType="FIVR",
                        YAxisParamType="UserDefined",
                        LogLevel="Enabled",
                        BypassPort=test_parms.get("Bypass", 1),
                        _fitem=Fitem(
                            'SAME',
                            edc=test_parms["IS_EDC"],
                            r0=pFail(setbin=-45),
                            r1=pPass(goto="NEXT"),
                            r2=pPass(goto="NEXT")
                        )
                    )
                )
        else:
            if test_type == "DRNG":
                patlist_value = "fun_cdie_endcpu_drng_list"
                LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom", 
                TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100"
                SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET,"+FUN_CCF_CX816_SPECS.MCfunCCF_FMIN_DRVMASK')
            elif test_type == "CCFBIST":
                patlist_value = test_parms.get("Patlist", "fun_cdie_endcpu_ccfbist_test_burstoff_list")
                VoltageConverter=Spec(f'"--overrides CORE3:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE2:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE1:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE0:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE --fivrcondition NOM_CCF_CORE"')
                SetPointsPreInstance=Spec(f'"MCdrv:" + FUN_CCF_{sku}_SPECS.corefreq + ":0.8GHz,MCdrv:" + FUN_CCF_{sku}_SPECS.ringfreq + ":0.8GHz,CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"')
                LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom", 
                TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100"
            else:
                patlist_value = test_parms.get("Patlist", "IPC::fun_cdie_vccr_sbft_fmin_fc_drg_hptp800_burstoff_list")
                TimingsTc="FUN_CCF_CX816::cpu_fun_timing_mts400_tstprtclk200_tck50_i_drv_mul_fmin_fun_CCF"
                SetPointsPreInstance=Spec(f'PSPRE.CLR_{corner}+","+"MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.corefreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.CR_{core_corner}+") +'"GHz,MCdrv:"+' +Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+":\"') +Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+") +'"GHz,CORE:nblctrl_core_l2:nbloff,MCdrv:R1_SET,"+FUN_CCF_CX816_SPECS.MCfunCCF_FMIN_DRVMASK')
            test_list_shmoo.append(
                DDGShmooTC(
                    name=f"SBFT_CCF_SHMOO_E_FMINXCCF_X_X_X_X_{test_type}",
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                    Patlist=patlist_value,
                    PrintFormat="ECADS",
                    SetPointsPlistParamName="Patlist",
                    SetPointsPreInstance=SetPointsPreInstance,
                    TimingsTc=TimingsTc,
                    VoltageConverter=Spec(f'"--overrides CORE3:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE2:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE1:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE0:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+" --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --dlvrpins VCCIA --expressions CCF_CORE --fivrcondition NOM_CCF_CORE"'),
                    XAxisParam="p_all_mts",
                    XAxisRange="80e6:5e6:8",
                    XAxisType="SpecSetVariable",
                    XAxisParamType="UserDefined",
                    YAxisParam="CCF",
                    YAxisRange="1.1:-0.05:14",
                    YAxisType="FIVR",
                    YAxisParamType="UserDefined",
                    LogLevel="Enabled",
                    BypassPort=test_parms.get("Bypass", 1),
                    _fitem=Fitem(
                        'SAME',
                        edc=test_parms["IS_EDC"],
                        r0=pFail(setbin=-45),
                        r1=pPass(goto="NEXT"),
                        r2=pPass(goto="NEXT")
                    )
                )
            )

    return test_list_shmoo

######################################################################
# ImpactStudiesVmin DRG VVAR
######################################################################
def get_impactstudy_list(flow, corner, core_corner, FlowMatrix, subflow, content_list):
     
   test_list_ImpactStudy = []
  
   for test_type, test_parms in content_list.items():
        test_list_ImpactStudy.append(ImpactStudiesVmin(name=f"SBFT_CCF_VMIN_K_{subflow}_X_CCF_{corner}_X_IMPACTSTUDY_{test_type}",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CCF_{sku}/InputFiles/IS_FUNCCF_MP_Vminconfig.json"'),
               VminForwardOffset = 0,
               LogLevel = "Enabled",
               SetPointsPlistParamName = "Patlist",
               FivrConditionPlistParamName = "Patlist",
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
               r0=pFail(setbin = 4545),
               r1=pPass(goto="NEXT"))))

   return test_list_ImpactStudy

######################################################################
# PrimePatConfigTestMethod TCK
######################################################################
def get_init_tck_list(subflow, hptp, content_list):
     
   test_list_init_tck = []
  
   for test_type, test_parms in content_list.items():
        test_list_init_tck.append(PrimePatConfigTestMethod(name=f"SBFT_CCF_PATMOD_K_INIT_X_X_X_X_TCK_{test_type}",
               Plist = 'IPC::'f"fun_cdie_vccr_sbft_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_burstoff_list_master",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CCF_{sku}/InputFiles/FUN_CCF_Generic.PatConfigSetpoints.json"'),
               SetPoint = 'FCCF_DTS_TCK_Override',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -45, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_init_tck

########################################################################
  
  
product_skus = ["CX816"]
 
for sku in product_skus:                                                    # <<<<<<<< This one
    mtplname = f"{product}_{sku}"
    # Initialize the module by defining the output mtpl path and the module name
    InitializeNVLClass(f'{mtplname}', f'{mtplname}', binrange = (4500, 4599), mttbinstrategy = NVLClass8dig, basenumrange = (11401, 11500), defaultthermalbin = (97452000,97453999),defaultresetbin = (45192000, 45193999), defaultrm2bin = (99452000,99453999), defaultrm1bin = (98452000,98453999))

    #################################################################
    #         
    #                       INIT SUBFLOW                      
    #
    #################################################################
    INIT_SUBFLOW = "F1XCCF"
    INIT_CORNER = "F1"
    # Input
    if sku == "CX816":
        Import(f"FUN_CCF_{sku}.usrv")
        Import(f"FUN_CCF_{sku}_TIMING.tcg")

        INIT_content_FC_DRGlist = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        }
        INIT_content_CCBistlist = {
       "CCFBIST"    : {"Bypass" : -1, "IS_EDC" : False, "Plist": "fun_cdie_endcpu_ccfbist_list"}
        }
        INIT_content_CORESTATE0_MASK = {
       "CORESTATE0_MASK": {"Bypass": -1,"IS_EDC": False, 
       "ConfigurationFile": Spec(MODULEPATH + ' + ' + f'"./Modules/FUN/FUN_CCF_{sku}/InputFiles/FUN_CCF_CORE_STATE_MASK.PatConfigSetPoints.json"'),
       "SetPoint": "FUN_CCF_CORESTATE0_MASK"}
        }
        INIT_content_WAITTIME_DRG = {
       "WAITTIME_DRG"    : {"Bypass" : Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, 1, -1, 1)"),"IS_EDC": False, 
       "ConfigurationFile": Spec(MODULEPATH + ' + ' + f'"./Modules/FUN/FUN_CCF_{sku}/InputFiles/Wait_Time.PatConfigSetPoint.json"'),
       "SetPoint": "UUFC_Wait_Times_MM"}
        }
        ApexcTC_content_list = {
       "APEXTC" :   {"Bypass" : Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)"), "IS_EDC" : False}
        }
        INIT_DEDC_content_list = {
       "DEDC": {"Bypass": -1, "IS_EDC": False}
        }
        INIT_TCK_content_list = {
       "FC_DRG" : {"Bypass" : Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, 1, 1, 1)"), "IS_EDC" : False},
        }
    else:
        {
            }
    
    INIT_FUSE_FC_DRG = get_init_fuse_list(INIT_SUBFLOW, INIT_CORNER, INIT_content_FC_DRGlist)
    INIT_FUSE_CCFBIST = get_init_fuse_list(INIT_SUBFLOW, INIT_CORNER, INIT_content_CCBistlist)
    INIT_FUSE_CORESTATE0_MASK = get_init_fuse_list(INIT_SUBFLOW, INIT_CORNER, INIT_content_CORESTATE0_MASK)
    INIT_content_WAITTIME_DRG = get_init_fuse_list(INIT_SUBFLOW, INIT_CORNER, INIT_content_WAITTIME_DRG)
    INIT_TCK_Tests = get_init_tck_list(INIT_SUBFLOW, hptp_speed, INIT_TCK_content_list)
    INIT_FUSE_COMP = Flow("FUSE_PATMOD", INIT_FUSE_FC_DRG,INIT_FUSE_CCFBIST,INIT_FUSE_CORESTATE0_MASK)
    INIT_PATMOD_COMP = Flow("PATMOD_WAITTIME", INIT_content_WAITTIME_DRG)
    INIT_TCK_COMP = Flow("FUN_CCF_CX816_INIT_TCK", INIT_TCK_Tests)

    APEXTC_INIT_Tests = get_init_apextc_list(ApexcTC_content_list)
    
    INIT_DEDC_TESTS = get_init_dedc_list(INIT_DEDC_content_list)

    
   
 
    INIT_Subflow = Flow(f"FUN_CCF_{sku}_INIT @INIT_SubFlow",
                        Fitem ('SAME', INIT_FUSE_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_PATMOD_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_TCK_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        APEXTC_INIT_Tests,INIT_DEDC_TESTS)


    #################################################################
    #         
    #                       FMAX SUBFLOW                      
    #
    #################################################################
    FMAX_Flow = "F5XCCF"                  # Define the name of your flow
    FMAX_Corner = "FMAX"                        
    FMAX_CORE_Corner = "F3_FREQ"                        
    FMAX_FlowMatrix = "CCF_F5_FREQ"       # Define the FlowMatrix attribute associated with this flow
    FMAX_Subflow = "F5XCCF"
    #FMAX_CORNER_ID = "F5"
   
    # Input
    if sku == "CX816":
        FMAX_apex_content_list = {
            "FC_DRG": {"Bypass": Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)"), "IS_EDC": True}
        }
        FMAX_apex_SCREENTC = {
            "SINGLEFLOW": {"Bypassport": Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)"), "IS_EDC": True}
        }
        
    else:
        {
            }
    
    FMAX_APEXTC_Tests = get_test_apextc(FMAX_Flow, FMAX_Corner, FMAX_CORE_Corner, FMAX_FlowMatrix, FMAX_Subflow, FMAX_apex_content_list)
    FMAX_Screen = get_test_list_ScreenGSDS_3(FMAX_Flow, FMAX_apex_SCREENTC, FMAX_Corner)
    #FMAX_FC_DRG_Subflow = Flow(f"FUN_CCF_{sku}_FC_DRG_FMAX", FMAX_Screen, FMAX_APEXTC_Tests)
    
    

    #################################################################
    #         
    #                       XCCFF5 SUBFLOW                      
    #
    #################################################################
    XCCFF5_Flow = "F5XCCF"                       # Define the name of your flow
    XCCFF5_Corner = "F5"                        # Define the test frequency
    XCRF5_Corner = "F1_FREQ"    
    XCCFF5_FlowMatrix = "CCF_F5_FREQ"            # Define the FlowMatrix attribute associated with this flow
    XCCFF5_CornerID = "C5"
    XCCFF5_SubFlow = "F5XCCF"
  
    # Input
    if sku == "CX816":

        ImpactStudy_content_list = {
       "DRG"    : {"Bypass" : 1, "IS_EDC" : True} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF5_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF5_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "IS_EDC" : True, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
        }
    
    XCCFF5_Tests = get_test_list_F5F6F7(XCCFF5_Flow, XCCFF5_Corner, XCRF5_Corner, XCCFF5_FlowMatrix, XCCFF5_CornerID, XCCFF5_SubFlow, XCCFF5_content_list)
    XCCFF5_Screen = get_test_list_ScreenGSDS_3(XCCFF5_Flow, XCCFF5_SCREENTC, XCCFF5_Corner)

  
# Fix: Unpack NativeMultiTrial lists when passing to Fitem or Flow

# Example for XCCFF5_Subflow (apply this pattern to all similar usages)
    #XCCFF5_FC_DRG_Subflow = Flow(f"FUN_CCF_{sku}_FC_DRG_F5XCCF", XCCFF5_Screen, XCCFF5_Tests)

    ImpactStudy_Tests = get_impactstudy_list(XCCFF5_Flow, XCCFF5_Corner, XCRF5_Corner, XCCFF5_FlowMatrix, XCCFF5_SubFlow, ImpactStudy_content_list)

      #################################################################
    #         
    #                     FMAX AND F5 SUBFLOW                      
    #
    #################################################################
    #XCCFF5_Subflow = Flow(
    #    f"FUN_CCF_{sku}_F5XCCF @F5XCCF_SubFlow",
    #    Fitem ('SAME',FMAX_FC_DRG_Subflow, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
    #    Fitem ('SAME',XCCFF5_FC_DRG_Subflow, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
    #    ImpactStudy_Tests
    #)

        #################################################################
    #         
    #                       FMAXLO SUBFLOW                      
    #
    #################################################################
    FMAX_Flow = "F5XCCFLO"                  # Define the name of your flow
    FMAX_Corner = "FMAX"                        
    FMAX_CORE_Corner = "F3_FREQ"                        
    FMAX_FlowMatrix = "CCF_F5_FREQ"       # Define the FlowMatrix attribute associated with this flow
    FMAX_Subflow = "F5XCCFLO"
    #FMAX_CORNER_ID = "F5"
   
    # Input
    if sku == "CX816":
        FMAX_apex_content_list = {
            "FC_DRG": {"Bypass": Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)"), "IS_EDC": True}
        }
        FMAX_apex_SCREENTC = {
            "SINGLEFLOW": {"Bypassport": Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)"), "IS_EDC": True}
        }
        
    else:
        {
            }
    
    FMAX_APEXTC_Tests = get_test_apextc(FMAX_Flow, FMAX_Corner, FMAX_CORE_Corner, FMAX_FlowMatrix, FMAX_Subflow, FMAX_apex_content_list)
    FMAX_Screen = get_test_list_ScreenGSDS_3(FMAX_Flow, FMAX_apex_SCREENTC, FMAX_Corner)
    FMAX_FC_DRG_Subflow = Flow(f"FUN_CCF_{sku}_FC_DRG_FMAXLO", FMAX_Screen, FMAX_APEXTC_Tests)
    
    

    #################################################################
    #         
    #                       XCCFF5LO SUBFLOW                      
    #
    #################################################################
    XCCFF5_Flow = "F5XCCFLO"                       # Define the name of your flow
    XCCFF5_Corner = "F5"                        # Define the test frequency
    XCRF5_Corner = "F1_FREQ"    
    XCCFF5_FlowMatrix = "CCF_F5_FREQ"            # Define the FlowMatrix attribute associated with this flow
    XCCFF5_CornerID = "C5"
    XCCFF5_SubFlow = "F5XCCFLO"
  
    # Input
    if sku == "CX816":

        ImpactStudy_content_list = {
       "DRG"    : {"Bypass" : 1, "IS_EDC" : True} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF5_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF5_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "IS_EDC" : True, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
        }
    
    XCCFF5_Tests = get_test_list_F5F6F7(XCCFF5_Flow, XCCFF5_Corner, XCRF5_Corner, XCCFF5_FlowMatrix, XCCFF5_CornerID, XCCFF5_SubFlow, XCCFF5_content_list)
    XCCFF5_Screen = get_test_list_ScreenGSDS_3(XCCFF5_Flow, XCCFF5_SCREENTC, XCCFF5_Corner)

  
# Fix: Unpack NativeMultiTrial lists when passing to Fitem or Flow

# Example for XCCFF5_Subflow (apply this pattern to all similar usages)
    XCCFF5_FC_DRG_Subflow = Flow(f"FUN_CCF_{sku}_FC_DRG_F5XCCFLO", XCCFF5_Screen, XCCFF5_Tests)

    ImpactStudy_Tests = get_impactstudy_list(XCCFF5_Flow, XCCFF5_Corner, XCRF5_Corner, XCCFF5_FlowMatrix, XCCFF5_SubFlow, ImpactStudy_content_list)

      #################################################################
    #         
    #                     FMAX LO AND F5 LO SUBFLOW                      
    #
    #################################################################
    XCCFF5_Subflow = Flow(
        f"FUN_CCF_{sku}_F5XCCFLO @F5XCCFLO_SubFlow",
        Fitem ('SAME',FMAX_FC_DRG_Subflow, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
        Fitem ('SAME',XCCFF5_FC_DRG_Subflow, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
        ImpactStudy_Tests
    )

    #################################################################
    #         
    #                       XCCFFMIN SUBFLOW                      
    #
    #################################################################
    XCCFFMIN_Flow = "FMINXCCF"                  # Define the name of your flow
    XCCFFMIN_Corner = "FMIN"
    XCRFMIN_Corner = "FMIN"    
    XCCFFMIN_FlowMatrix = "CCF_FMIN"       # Define the FlowMatrix attribute associated with this flow
    XCCFFMIN_Subflow = "FMINXCCF"
  
   # Input
    if sku == "CX816":

        XCCFFMIN_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFFMIN_FFcontent_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : True} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFFMIN_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
        XCCFFMIN_SHMOO_content_list = {
        "DRNG"       :   {"Bypass" : 1, "IS_EDC" : True},
       "CCFBIST"        :   {"Bypass" : 1, "IS_EDC" : True},
       "DRG_FMIN"       :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "FMIN", "CORE_FREQ": "FMIN", "RING_FREQ": "FMIN"},
       "DRG_F1"         :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "F1", "CORE_FREQ": "F1_FREQ", "RING_FREQ": "F1_FREQ"},
       "DRG_F2"         :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "F2", "CORE_FREQ": "F2_FREQ", "RING_FREQ": "F2_FREQ"},
       "DRG_F3"         :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "F3", "CORE_FREQ": "F3_FREQ", "RING_FREQ": "F3_FREQ"},
       "DRG_F4"         :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "F4", "CORE_FREQ": "F3_FREQ", "RING_FREQ": "F4_FREQ"},
       "DRG_F5"         :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "F5", "CORE_FREQ": "F3_FREQ", "RING_FREQ": "F5_FREQ"},
       "DRG_F6"         :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "F6", "CORE_FREQ": "F3_FREQ", "RING_FREQ": "F6_FREQ"},
       "DRG_F7"         :   {"Bypass" : 1, "IS_EDC" : True,"CORNER": "F7", "CORE_FREQ": "F3_FREQ", "RING_FREQ": "F7_FREQ"},
        }
    else:
        {
            }

    XCCFFMIN_Tests = get_test_list_fmin(XCCFFMIN_Flow, XCCFFMIN_Corner, XCRFMIN_Corner, XCCFFMIN_FlowMatrix, XCCFFMIN_Subflow, XCCFFMIN_content_list)
    XCCFFMIN_Screen = get_test_list_ScreenGSDS_3(XCCFFMIN_Flow, XCCFFMIN_SCREENTC, XCCFFMIN_Corner)
    XCCFFMINFF_Tests = get_test_list_fminfailflow(XCCFFMIN_Flow, XCCFFMIN_Corner, XCRFMIN_Corner, XCCFFMIN_FlowMatrix, XCCFFMIN_Subflow, XCCFFMIN_FFcontent_list)
    SHMOO_Tests = get_shmoo_list(XCCFFMIN_SHMOO_content_list,corner=XCCFFMIN_Corner,core_corner=XCRFMIN_Corner,FlowMatrix=XCCFFMIN_FlowMatrix,sku=sku)
    SHMOO_COMP = Flow("FUN_CCF_CX816_SHMOO", *SHMOO_Tests)

    XCCFFMIN_Subflow = Flow(f"FUN_CCF_{sku}_FMINXCCF @FMINXCCF_SubFlow",XCCFFMIN_Screen,XCCFFMIN_Tests,#XCCFFMINFF_Tests,
        Fitem('SAME', SHMOO_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT"))
    )
    
    
#################################################################
    #         
    #                       VMAX SUBFLOW                      
    #
    #################################################################
    VMAXXCCF_Flow = "VMAXXCCF"                  # Define the name of your flow
    VMAXXCCF_F1Corner = "F1"
    VMAXXCCF_F5Corner = "F5"
    VMAXXCR_F1CoreCorner = "F1_FREQ" 
    VMAXXCR_F5CoreCorner = "F1_FREQ" 
    VMAXXCCF_F1FlowMatrix = "CCF_F1_FREQ"       # Define the FlowMatrix attribute associated with this flow
    VMAXXCCF_F5FlowMatrix = "CCF_F5_FREQ" 
    VMAXXCCF_Subflow = "VMAXXCCF"
  
    # Input
    if sku == "CX816":

        VMAXXCCF_F1_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        VMAXXCCF_F1_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "IS_EDC" : True, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
        VMAXXCCF_F5_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        VMAXXCCF_F5_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "IS_EDC" : True, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
            }

    VMAXXCCF_F1_Test = get_test_list_vmax(VMAXXCCF_Flow, VMAXXCCF_F1Corner, VMAXXCR_F1CoreCorner, VMAXXCCF_F1FlowMatrix, VMAXXCCF_Subflow, VMAXXCCF_F1_content_list)
    VMAXXCCF_F1_Screen = get_test_list_ScreenGSDS_3(VMAXXCCF_Flow, VMAXXCCF_F1_SCREENTC, VMAXXCCF_F1Corner) 
    VMAXXCCF_F5_Test = get_test_list_vmaxF5(VMAXXCCF_Flow,VMAXXCCF_F5Corner,VMAXXCR_F5CoreCorner,VMAXXCCF_F5FlowMatrix,"C5", VMAXXCCF_Subflow,VMAXXCCF_F5_content_list)
    VMAXXCCF_F5_Screen = get_test_list_ScreenGSDS_3(VMAXXCCF_Flow, VMAXXCCF_F5_SCREENTC, VMAXXCCF_F5Corner)
   
    #VMAXF1_COMP = Flow(f"FUN_CCF_{sku}_VMAXXCCF_F1", VMAXXCCF_F1_Screen, VMAXXCCF_F1_Test)
    #VMAXF5_COMP = Flow(f"FUN_CCF_{sku}_VMAXXCCF_F5", VMAXXCCF_F5_Screen, VMAXXCCF_F5_Test)
   
    #VMAX_Subflow = Flow(f"FUN_CCF_{sku}_VMAXXCCF",
    #    Fitem('SAME', VMAXF1_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
    #    Fitem('SAME', VMAXF5_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT"))
    #)
    
#################################################################
    #         
    #                       VMAXLO SUBFLOW                      
    #
    #################################################################
    VMAXXCCF_Flow = "VMAXXCCFLO"                  # Define the name of your flow
    VMAXXCCF_F1Corner = "F1"
    VMAXXCCF_F5Corner = "F5"
    VMAXXCR_F1CoreCorner = "F1_FREQ" 
    VMAXXCR_F5CoreCorner = "F1_FREQ" 
    VMAXXCCF_F1FlowMatrix = "CCF_F1_FREQ"       # Define the FlowMatrix attribute associated with this flow
    VMAXXCCF_F5FlowMatrix = "CCF_F5_FREQ" 
    VMAXXCCF_Subflow = "VMAXXCCFLO"
  
    # Input
    if sku == "CX816":

        VMAXXCCF_F1_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        VMAXXCCF_F1_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "IS_EDC" : True, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
        VMAXXCCF_F5_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        VMAXXCCF_F5_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "IS_EDC" : True, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
            }

    VMAXXCCF_F1_Test = get_test_list_vmax(VMAXXCCF_Flow, VMAXXCCF_F1Corner, VMAXXCR_F1CoreCorner, VMAXXCCF_F1FlowMatrix, VMAXXCCF_Subflow, VMAXXCCF_F1_content_list)
    VMAXXCCF_F1_Screen = get_test_list_ScreenGSDS_3(VMAXXCCF_Flow, VMAXXCCF_F1_SCREENTC, VMAXXCCF_F1Corner) 
    VMAXXCCF_F5_Test = get_test_list_vmaxF5(VMAXXCCF_Flow,VMAXXCCF_F5Corner,VMAXXCR_F5CoreCorner,VMAXXCCF_F5FlowMatrix,"C5", VMAXXCCF_Subflow,VMAXXCCF_F5_content_list)
    VMAXXCCF_F5_Screen = get_test_list_ScreenGSDS_3(VMAXXCCF_Flow, VMAXXCCF_F5_SCREENTC, VMAXXCCF_F5Corner)
   
    VMAXF1_COMP = Flow(f"FUN_CCF_{sku}_VMAXXCCFLO_F1", VMAXXCCF_F1_Screen, VMAXXCCF_F1_Test)
    VMAXF5_COMP = Flow(f"FUN_CCF_{sku}_VMAXXCCFLO_F5", VMAXXCCF_F5_Screen, VMAXXCCF_F5_Test)
   
    VMAX_Subflow = Flow(f"FUN_CCF_{sku}_VMAXXCCFLO",
        Fitem('SAME', VMAXF1_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
        Fitem('SAME', VMAXF5_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT"))
    )


    #################################################################
    #         
    #                       XCCFF1 SUBFLOW                      
    #
    #################################################################
    XCCFF1_Flow = "F1XCCF"                  # Define the name of your flow
    XCCFF1_Corner = "F1"
    XCRF1_Corner = "F1_FREQ"    
    XCCFF1_FlowMatrix = "CCF_F1_FREQ"       # Define the FlowMatrix attribute associated with this flow
    XCCFF1_Subflow = "F1XCCF"
  
    # Input
    if sku == "CX816":

        XCCFF1_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF1_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
            }

    XCCFF1_Tests = get_test_list_f1_f4(XCCFF1_Flow, XCCFF1_Corner, XCRF1_Corner, XCCFF1_FlowMatrix, XCCFF1_Subflow, XCCFF1_content_list)
    XCCFF1_Screen = get_test_list_ScreenGSDS_3(XCCFF1_Flow, XCCFF1_SCREENTC, XCCFF1_Corner)


  
# Fix: Unpack NativeMultiTrial lists when passing to Fitem or Flow

# Example for XCCFF1_Subflow (apply this pattern to all similar usages)
    XCCFF1_Subflow = Flow(f"FUN_CCF_{sku}_F1XCCF @F1XCCF_SubFlow", XCCFF1_Screen, XCCFF1_Tests)
    
    #################################################################
    #         
    #                       XCCFF2 SUBFLOW                      
    #
    #################################################################
    XCCFF2_Flow = "F2XCCF"                  # Define the name of your flow
    XCCFF2_Corner = "F2"                        
    XCRF2_Corner = "F1_FREQ"    
    XCCFF2_FlowMatrix = "CCF_F2_FREQ"       # Define the FlowMatrix attribute associated with this flow
    XCCFF2_Subflow = "F2XCCF"
    

    # Input
    if sku == "CX816":

        XCCFF2_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF2_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
            }

    XCCFF2_Tests = get_test_list_f1_f4(XCCFF2_Flow, XCCFF2_Corner, XCRF2_Corner, XCCFF2_FlowMatrix, XCCFF2_Subflow, XCCFF2_content_list)
    XCCFF2_Screen = get_test_list_ScreenGSDS_3(XCCFF2_Flow, XCCFF2_SCREENTC, XCCFF2_Corner)


  
# Fix: Unpack NativeMultiTrial lists when passing to Fitem or Flow

# Example for XCCFF2_Subflow (apply this pattern to all similar usages)
    XCCFF2_Subflow = Flow(f"FUN_CCF_{sku}_F2XCCF @F2XCCF_SubFlow", XCCFF2_Screen, XCCFF2_Tests)


    #################################################################
    #         
    #                       XCCFF3 SUBFLOW                      
    #
    #################################################################
    XCCFF3_Flow = "F3XCCF"                  # Define the name of your flow
    XCCFF3_Corner = "F3"                        
    XCRF3_Corner = "F1_FREQ"    
    XCCFF3_FlowMatrix = "CCF_F3_FREQ"       # Define the FlowMatrix attribute associated with this flow
    XCCFF3_Subflow = "F3XCCF"
  
    # Input
    if sku == "CX816":

        XCCFF3_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF3_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
            }

    XCCFF3_Tests = get_test_list_f1_f4(XCCFF3_Flow, XCCFF3_Corner, XCRF3_Corner, XCCFF3_FlowMatrix, XCCFF3_Subflow, XCCFF3_content_list)
    XCCFF3_Screen = get_test_list_ScreenGSDS_3(XCCFF3_Flow, XCCFF3_SCREENTC, XCCFF3_Corner)

  
# Fix: Unpack NativeMultiTrial lists when passing to Fitem or Flow

# Example for XCCFF3_Subflow (apply this pattern to all similar usages)
    XCCFF3_Subflow = Flow(f"FUN_CCF_{sku}_F3XCCF @F3XCCF_SubFlow", XCCFF3_Screen, XCCFF3_Tests)

    #################################################################
    #         
    #                       XCCFF4 SUBFLOW                      
    #
    #################################################################
    XCCFF4_Flow = "F4XCCF"                  # Define the name of your flow
    XCCFF4_Corner = "F4"                        
    XCRF4_Corner = "F1_FREQ"    
    XCCFF4_FlowMatrix = "CCF_F4_FREQ"       # Define the FlowMatrix attribute associated with this flow
    XCCFF4_Subflow = "F4XCCF"
  
    # Input
    if sku == "CX816":

        XCCFF4_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF4_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
            }

    XCCFF4_Tests = get_test_list_f1_f4(XCCFF4_Flow, XCCFF4_Corner, XCRF4_Corner, XCCFF4_FlowMatrix, XCCFF4_Subflow, XCCFF4_content_list)
    XCCFF4_Screen = get_test_list_ScreenGSDS_3(XCCFF4_Flow, XCCFF4_SCREENTC, XCCFF4_Corner)

  
# Fix: Unpack NativeMultiTrial lists when passing to Fitem or Flow

# Example for XCCFF4_Subflow (apply this pattern to all similar usages)
    #XCCFF4_Subflow = Flow(f"FUN_CCF_{sku}_F4XCCF @F4XCCF_SubFlow", XCCFF4_Screen, XCCFF4_Tests)

    
    #################################################################
    #         
    #                       XCCFF4LO SUBFLOW                      
    #
    #################################################################
    XCCFF4_Flow = "F4XCCFLO"                  # Define the name of your flow
    XCCFF4_Corner = "F4"                        
    XCRF4_Corner = "F1_FREQ"    
    XCCFF4_FlowMatrix = "CCF_F4_FREQ"       # Define the FlowMatrix attribute associated with this flow
    XCCFF4_Subflow = "F4XCCFLO"
  
    # Input
    if sku == "CX816":

        XCCFF4_content_list = {
       "FC_DRG"    : {"Bypass" : -1, "IS_EDC" : False} # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       }
        XCCFF4_SCREENTC = {
       "SINGLEFLOW"     :{"Bypassport": -1, "ScreenTestSet":"FUN_CCF_MM_SCREEN_SingleFlow"}
       }
    else:
        {
            }

    XCCFF4_Tests = get_test_list_f1_f4(XCCFF4_Flow, XCCFF4_Corner, XCRF4_Corner, XCCFF4_FlowMatrix, XCCFF4_Subflow, XCCFF4_content_list)
    XCCFF4_Screen = get_test_list_ScreenGSDS_3(XCCFF4_Flow, XCCFF4_SCREENTC, XCCFF4_Corner)

  
# Fix: Unpack NativeMultiTrial lists when passing to Fitem or Flow

# Example for XCCFF4_Subflow (apply this pattern to all similar usages)
    XCCFF4_Subflow = Flow(f"FUN_CCF_{sku}_F4XCCFLO @F4XCCFLO_SubFlow", XCCFF4_Screen, XCCFF4_Tests)



    
    ######################### END_FLOW ##################################
    END_FLOW = "ENDCPU"
    END_CORNER = "F1"
    CCF_BIST = "CCFBIST"
    #END UUFC TEST LIST
    END_VMINTC_UUFC_TLI = {"Bypassport": -1, "Testmode": "Scoreboard", "RecoveryMode": "RecoveryPort", "SetPointsPreInstance": Spec(f'"MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.corefreq+''":')+'0.8GHz,MCdrv:"+'+Spec(f'FUN_CCF_{sku}_SPECS.ringfreq+''":')+'0.8GHz,MCfunCCF:ratio_modify:0.8GHz"'),"edc": True}
    END_VMINTC_UUFC_TEST = get_test_list_funflow(STATUSEDC, END_FLOW, END_CORNER, CCF_BIST, END_VMINTC_UUFC_TLI)
    
    #END DRNG BIST TEST LIST
    DRNG_UNCORE_BIST = "DRNG"
    END_VMINTC_DRNGBIST_TLI = {"Bypassport": -1, "edc": False}
    END_VMINTC_DRNGBIST_TEST = get_test_list_DRNGTC_5p0(END_FLOW, END_CORNER, DRNG_UNCORE_BIST, END_VMINTC_DRNGBIST_TLI)
    
    #END DRNG BIST TEST LIST
    DRNG_FUSE_BIST = "FUSE_DRNG"
    END_VMINTC_FUSEDRNGBIST_TLI = {"Bypassport": -1, "edc": False}
    END_VMINTC_FUSEDRNGBIST_TEST = get_test_list_DRNGTC_5p0(END_FLOW, END_CORNER, DRNG_FUSE_BIST, END_VMINTC_FUSEDRNGBIST_TLI)
    
    # #END DRNGTC TEST LIST
    # DRNG_COL = "UNCORE_COLLISION"
    # END_DRNGTC_COL_TLI = {"Mode": "COLLISION", "Bypassport": -1, "edc": True}
    # END_DRNGTC_COL_TEST = get_test_list_DRNGTC(END_FLOW, END_CORNER, DRNG_COL, END_DRNGTC_COL_TLI)
    # 
    # #END DRNGTC TEST LIST
    # DRNG_MC = "UNCORE_MODECHANGE"
    # END_DRNGTC_MC_TLI = {"Mode": "FUNCTIONAL", "Bypassport": -1, "edc": True}
    # END_DRNGTC_MC_TEST = get_test_list_DRNGTC(END_FLOW, END_CORNER, DRNG_MC, END_DRNGTC_MC_TLI)
    # 
    # #END DRNGTC TEST LIST
    # DRNG_MET = "UNCORE_METRICS"
    # END_DRNGTC_MET_TLI = {"Mode": "METRICS", "Bypassport": -1, "edc": True}
    # END_DRNGTC_MET_TEST = get_test_list_DRNGTC(END_FLOW, END_CORNER, DRNG_MET, END_DRNGTC_MET_TLI)
    # 
    # #END FUSEDRNGTC TEST LIST
    # FUSEDRNG_COL = "FUSE_COLLISION"
    # END_FUSEDRNGTC_COL_TLI = {"Mode": "COLLISION", "Bypassport": -1, "edc": True}
    # END_FUSEDRNGTC_COL_TEST = get_test_list_DRNGTC(END_FLOW, END_CORNER, FUSEDRNG_COL, END_FUSEDRNGTC_COL_TLI)
    # 
    # #END FUSEDRNGTC TEST LIST
    # FUSEDRNG_MC = "FUSE_MODECHANGE"
    # END_FUSEDRNGTC_MC_TLI = {"Mode": "FUNCTIONAL", "Bypassport": -1, "edc": True}
    # END_FUSEDRNGTC_MC_TEST = get_test_list_DRNGTC(END_FLOW, END_CORNER, FUSEDRNG_MC, END_FUSEDRNGTC_MC_TLI)
    # 
    # #END FUSEDRNGTC TEST LIST
    # FUSEDRNG_MET = "FUSE_METRICS"
    # END_FUSEDRNGTC_MET_TLI = {"Mode": "METRICS", "Bypassport": -1, "edc": True}
    # END_FUSEDRNGTC_MET_TEST = get_test_list_DRNGTC(END_FLOW, END_CORNER, FUSEDRNG_MET, END_FUSEDRNGTC_MET_TLI)
    
    #DRNG COMPOSITE TEST LIST
    #FCSBFT_DRNG_TEST = Flow('FCSBFT_DRNG', END_VMINTC_DRNGBIST_TEST, END_VMINTC_FUSEDRNGBIST_TEST, END_DRNGTC_COL_TEST, END_FUSEDRNGTC_COL_TEST, END_DRNGTC_MC_TEST, END_FUSEDRNGTC_MC_TEST, END_DRNGTC_MET_TEST, END_FUSEDRNGTC_MET_TEST)
    FCSBFT_DRNG_TEST = Flow('FCSBFT_DRNG', END_VMINTC_DRNGBIST_TEST, END_VMINTC_FUSEDRNGBIST_TEST)
    
    END_SUBFLOW = Flow('FUN_CCF_CX816_ENDCPU @END_SubFlow', END_VMINTC_UUFC_TEST,
                                                 Fitem ('SAME', FCSBFT_DRNG_TEST, 
                                                        r0=pFail(ret=0), 
                                                        r1=pPass(goto="NEXT")),
    )
    
    ######################################################################