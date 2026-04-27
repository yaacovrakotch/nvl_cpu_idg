# Import the necessary classes from Pymtpl
from decimal import ROUND_05UP
from pymtpl.por_methods import VminTC, PrimePatConfigTestMethod, RunCallback, ApexTC, DedcLoadConfigTC, DDGShmooTC, PatternDelayOptimizer, ImpactStudiesVmin
from pymtpl.core import Flow, Fitem, pPass, pFail, NativeMultiTrial, AUTO, InitializeNVLClass, Import, TrialParamSpec, Spec
from pymtpl.binctr import NVLClass8dig

# Define the product name
product = "FUN_CORE"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'
HPTP = "hptp800"
PORT4 = -44
PORT5 = -44
#defaultthermalbin = 9744, defaultresetbin = 4419
LTTCPORT4 = 9794
LTTCPORT5 = 9419

####################################################################################
def get_test_pattern_wto(content_list):
     
   test_list_pattern_wto = []
  
   for test_type, test_parms in content_list.items():
      test_list_pattern_wto.append(PatternDelayOptimizer(name=f'SBFT_CORE_VMIN_E_FMINXCR_X_CR_F1_X_MLC_WTO',
	     OverwriteOutput = "False",
	     PatmodConfig = "MLC_WaitTime_10X",
	     PatmodInputFile =  Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/Wait_Time.patmod.json"'),
	     PatmodOutputFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/MLC_wait_time_final.patmod.json"'),
	     PrePlist = "VoltageConverter(--dlvrpins VCCIA --expressions --fivrcondition NOM_CCF_CORE)",
	     SearchValueMin = 20,
	     SearchValueResolution = 10,
	     SummaryOutputFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/MLC_wait_time_final.patmod.json"'),
         BypassPort = test_parms["Bypass"],
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_fminxcr_mlc_hptp800_list"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_F1_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff"')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=-44),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=-44),
                        r3 = pFail(setbin=-44),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_pattern_wto

####################################################################################
def get_test_apextc_all(corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_apextcflowall = []
  
   for test_type, test_parms in content_list.items():
      test_list_apextcflowall.append(ApexTC(name=f'SBFT_CORE_VMIN_E_{subflow}_X_CR_{corner}_X_{test_type}_APEX_FMAX',
         StepSize = 1,
         #InitialMaskBits = "1100",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')),
         BypassPort = test_parms["Bypass"],
         Targets = "FCORE1,FCORE0",
         ForwardingMode = "Input",
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR_APEX')),
         #SetPointsPostInstance = "MCdrv:R1_SET",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:FMAX,MCfun:ratio_modify:"'+f'+FUN_CORE_{sku}_Specs.{test_type}_FMAX')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon"')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_fmax_{test_type.lower()}_{hptp.lower()}_list"),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryOptions = "",
         RecoveryTracking = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         End = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
         Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
         FivrCondition = "NOM_CCF_CORE",
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         ExportTokens = Spec(f'__shared__::APEX_Tokens.CRToken'),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",-44)),
                        r1 = pPass(setbin=-44),
                        r2 = pFail(setbin=test_parms.get("Binning",-44)),
                        r3 = pFail(setbin=test_parms.get("Binning",-44)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_apextcflowall

####################################################################################

####################################################################################
def get_test_list_fmin(flow, corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_fminflow = []
  
   for test_type, test_parms in content_list.items():
      test_list_fminflow.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_X_{test_type}",
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE",
         _comment='FMIN VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         #ExecutionMode = "Search" if test_parms["IS_EDC"] else "SearchWithScoreboard",
         ExecutionMode = "SearchWithScoreboard",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         CornerIdentifiers = f"CR1@F1,CR0@F1",
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "Input",
         FeatureSwitchSettings = test_parms.get("FeatureSwitchSettings", Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = test_parms.get("TimingsTC", "FUN_CORE_CX48::cpu_fun_timing_mts400_tstprtclk200_tck50_i_drv_mul_fun_CORE"),
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list"),
         #BaseNumbers = None if test_parms["IS_EDC"] else AUTO,
         BaseNumbers = AUTO,
         DtsConfiguration = Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         #LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
         LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_NoRec'),
         #RecoveryOptions = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryOptions_MTT'),
         RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         #RecoveryTrackingOutgoing = Spec(f"__shared__::RecoveryTracker.OUTGOING_CR"),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget1C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount')),
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRail' + f' + DROPOUT.CR_{corner}')),
         VminResult = Spec(f'"SBFT_{test_type}_CR1_FMIN_FF_SEARCH,SBFT_{test_type}_CR0_FMIN_FF_SEARCH"'),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         #PreInstance=Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.{FlowMatrix}+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}")+f'+"GHz,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.{test_type}_FMIN+",MCfun:DBGCNTR:FMIN,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR'))),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR'))),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r4=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=-44),
                        r1 = pPass(setbin=-44),
                        r2 = pFail(setbin=-44),
                        r3 = pFail(setbin=-44),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_fminflow

####################################################################################

####################################################################################
def get_test_list_f1_f4(flow, corner, corner_id, FlowMatrix, subflow, hptp, content_list):
     
   test_list_funflow = []
  
   for test_type, test_parms in content_list.items():
      test_list_funflow.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_X_{test_type}",
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE",
         _comment='SpeedFlow F1_F4 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         #MultiPassMasks = test_parms.get(#"MultiPassMasks", "" if corner in ["F1", "F2", "F3", "F4"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48')),
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = test_parms.get("FeatureSwitchSettings", Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         #CornerIdentifiers = f"CR1@{corner},CR0@{corner}",
         CornerIdentifiers = Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}"),
         EndVoltageLimits = test_parms.get("EndVoltageLimits", Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , "")'),
         #StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         #StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         RecoveryTrackingOutgoing = Spec(f"__shared__::RecoveryTracker.OUTGOING_CR"),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget1C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount')),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48') if corner in ["F1", "F2", "F3", "F4", "F5"] else "",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRail' + f' + DROPOUT.CR_{corner}')),
         VminResult = test_parms.get("VminResult", ""),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance= test_parms.get("PreInstance",  ""),
         PostInstance= test_parms.get("PostInstance",  ""),
         #PreInstance=Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.{FlowMatrix}+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz,MCfun:DBGCNTR:{corner}"')),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,MCfun:DBGCNTR:{corner},MCfun:ratio_modify:"'+f'+FUN_CORE_{sku}_Specs.{test_type}_{corner}')),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":')+f'0.8GHz,'+f'MCfun:DBGCNTR:{corner},MCfun:ratio_modify:"'+f'+FUN_CORE_{sku}_Specs.{test_type}_{corner}')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r4=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=-44),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=-44),
                        r3 = pFail(setbin=-44),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_funflow

####################################################################################

####################################################################################

def get_test_list(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list = []
  
   for test_type, test_parms in content_list.items():
      test_list.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{FlowMatrix}_X_{test_type}", 
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
         _comment='SpeedFlow F5_F7 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.CR_{corner_id}") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         #MultiPassMasks = test_parms.get(#"MultiPassMasks", "" if corner in ["F1", "F2", "F3", "F4"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48')),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = test_parms.get("FeatureSwitchSettings", Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         #TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         TimingsTc = Spec(f'__shared__::TpRule.If_PHMHOT("FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2pphm","FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p")'),
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = TrialParamSpec(Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , ["","",""])')),
         StartVoltagesOffset = TrialParamSpec(Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , ["","",""])')),
         #StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         #StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         #LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'__shared__::TpRule.If_PHMHOT("",toString(__shared__::GBVars.LimitGuardband))'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         RecoveryTrackingOutgoing = Spec(f"__shared__::RecoveryTracker.OUTGOING_CR"),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget1C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount')),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration",Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRail' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         PreInstance= test_parms.get("PreInstance",  ""),
         PostInstance= test_parms.get("PostInstance",  ""),
         #PreInstance = TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.CR_C5+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{corner_id}"))),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":1.2GHz,MCfun:DBGCNTR:"')+Spec(f"+ __shared__::Corners.CR_{corner_id}"+f'+",MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.{test_type}_{corner_id}"))),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":0.8GHz,MCfun:DBGCNTR:"')+Spec(f"+ __shared__::Corners.CR_{corner_id}"+f'+",MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.{test_type}_{corner_id}"))),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r4=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=-44),
                        r1 = pPass(setbin=-44),
                        r2 = pFail(setbin=-44),
                        r3 = pFail(setbin=-44),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list
####################################################################################

####################################################################################

def get_test_vmax(flow, corner, FlowMatrix, subflow, hptp, content_list, freq):
     
   test_list_vmaxflow = []
  
   for test_type, test_parms in content_list.items():
      test_list_vmaxflow.append(VminTC(name=f'SBFT_CORE_VMAX_K_{subflow}_X_CR_{corner}_X_{test_type}_{freq}',
         BypassPort = test_parms["Bypass"],
         #MultiPassMasks = "",
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         TestMode = "Scoreboard",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
         ForwardingMode = "Input",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
         FeatureSwitchSettings = test_parms.get("FeatureSwitchSettings", Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
         TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         #LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         #RecoveryMode = "NoRecovery",
         #RecoveryOptions = "",
         #RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         #RecoveryTrackingOutgoing = "",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         RecoveryTrackingOutgoing = Spec(f"__shared__::RecoveryTracker.OUTGOING_CR"),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget1C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount')),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         PreInstance= test_parms.get("PreInstance",  ""),
         PostInstance= test_parms.get("PostInstance",  ""),
         #PreInstance=Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.{FlowMatrix}_FREQ+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:{freq}"')),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:{freq},MCfun:ratio_modify:"'+f'+FUN_CORE_{sku}_Specs.{test_type}_{freq}')),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":0.8GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:{freq},MCfun:ratio_modify:"')+f'+FUN_CORE_{sku}_Specs.{test_type}_{freq}')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon"')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=-44),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=-44),
                        r3 = pFail(setbin=-44),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_vmaxflow

####################################################################################

####################################################################################

def get_test_vmaxf5(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list_vmaxflowf5 = []
  
   for test_type, test_parms in content_list.items():
      test_list_vmaxflowf5.append(NativeMultiTrial(name=f'SBFT_CORE_VMAX_K_{subflow}_X_CR_{FlowMatrix}_{test_type}_ALL',
		
		 exitaction="Continue",
		 trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
		 _comment='VMAX F5_F7 VminTC test with MTT',
		 template=VminTC(name=f'"SBFT_CORE_VMAX_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.CR_{corner_id}") + f' + "_{test_type}_ALL"',
         BypassPort = test_parms["Bypass"],
         #MultiPassMasks = test_parms.get(#"MultiPassMasks", "" if corner in ["F1", "F2", "F3", "F4"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48')),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         FlowIndex = TrialParamSpec(f"FUN_CORE_CX48_Specs.FlowIndex"),
         TestMode = "Scoreboard",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
         ForwardingMode = "Input",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
         #InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM0M1'),
         FeatureSwitchSettings = test_parms.get("FeatureSwitchSettings", Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
         TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         #LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = "NoRecovery",
         RecoveryOptions = "",
         RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         RecoveryTrackingOutgoing = "",
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget1C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration",Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         PreInstance= test_parms.get("PreInstance",  ""),
         PostInstance= test_parms.get("PostInstance",  ""),
         #PreInstance = TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.CR_C5+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),
         #PreInstance = Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F5_FREQ+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{corner_id}"))),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{corner_id}"+f'+",MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.{test_type}_{corner_id}"))),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+__shared__::FlowMatrixSingular.CR_F5_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:F5,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.{test_type}_{corner}"))),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+__shared__::FlowMatrixSingular.CR_F5_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":0.8GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:F5,MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.{test_type}_{corner}"))),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon"')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=-44),
                        r1 = pPass(setbin=-44),
                        r2 = pFail(setbin=-44),
                        r3 = pFail(setbin=-44),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_vmaxflowf5

####################################################################################

####################################################################################

def get_test_list_LTTC(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list_LTTC = []
  
   for test_type, test_parms in content_list.items():
      test_list_LTTC.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{FlowMatrix}_X_{test_type}_ALL", 
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
         _comment='SpeedFlow F5_F7 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.CR_{corner_id}") + f' + "_{test_type}_ALL"',
         BypassPort = test_parms["Bypass"],
         #MultiPassMasks = test_parms.get(#"MultiPassMasks", "" if corner in ["F1", "F2", "F3", "F4"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48')),
         #InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM0M1'),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         ForwardingMode = "Input",
         FeatureSwitchSettings = test_parms.get("FeatureSwitchSettings", Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         #CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
         CornerIdentifiers = "",
         EndVoltageLimits = TrialParamSpec(f'"D.R"+'+Spec(f"__shared__::Corners.CR_{corner_id}")+'+"CR"'),
         StartVoltages = TrialParamSpec(f'"D.R"+'+Spec(f"__shared__::Corners.CR_{corner_id}")+'+"CR"'),
         StartVoltagesForRetry = TrialParamSpec(Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , ["","",""])')),
         StartVoltagesOffset = TrialParamSpec(Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , ["","",""])')),
         #StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         #StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         #LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(FUN_CORE_{sku}_Specs.LTTC_LimitGB)'),
         LimitGuardband = '31mV',
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = "NoRecovery",
         #RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         #RecoveryTrackingOutgoing = Spec(f"__shared__::RecoveryTracker.OUTGOING_CR"),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget1C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount')),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration",Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRail' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         #PreInstance = TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.CR_C5+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),
         #SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{corner_id}"))),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":0.8GHz,MCfun:DBGCNTR:"')+Spec(f"+ __shared__::Corners.CR_{corner_id}")+f'+",MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.{test_type}_{corner_id}"))),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",-44)),
                        r1 = pPass(setbin=-44),
                        r2 = pFail(setbin=test_parms.get("Binning",-44)),
                        r3 = pFail(setbin=test_parms.get("Binning",-44)),
                        r4 = pFail(setbin=LTTCPORT4),
                        r5 = pFail(setbin=LTTCPORT5))))
  
   return test_list_LTTC
####################################################################################

####################################################################################
def get_test_list_misr(flow, corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_misr = []
  
   for test_type, test_parms in content_list.items():
      test_list_misr.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_X_{test_type}",
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE",
         _comment='SpeedFlow MISR VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         #MultiPassMasks = test_parms.get(#"MultiPassMasks", "" if corner in ["F1", "F2", "F3", "F4"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48')),
         ExecutionMode = "Search" if "SCR" in flow else "Search",
         TestMode = "Functional",
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_CTV'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         #BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = f"CR1@{corner},CR0@{corner}",
         EndVoltageLimits = test_parms.get("EndVoltageLimits", Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_MISR')),
         CtvPins = "IPC::CPU_TDO",
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_NoRec'),
         #RecoveryOptions = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryOptions_MTT'),
         RecoveryTrackingIncoming = Spec(f"__shared__::RecoveryTracker.INCOMING_CR"),
         #RecoveryTrackingOutgoing = Spec(f"__shared__::RecoveryTracker.OUTGOING_CR"),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget1C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = test_parms.get("FailCaptureCount", Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount')),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", ""),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRail' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         #PreInstance=Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Replace(Replace(Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.{FlowMatrix}+")*60)),10)),0,'+f"'00000000'),1,'11111111')"+f')"'),

         SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz,MCfun:DBGCNTR:{corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.{test_type}_{corner}'),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",-44)),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44)),
                        r3 = pFail(setbin=test_parms.get("Binning",-44)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_misr

####################################################################################

######################################################################
# PrimePatConfigTestMethod Fuse Overrides
######################################################################
def get_init_fuse_list(subflow, hptp, content_list):
     
   test_list_init = []
  
   for test_type, test_parms in content_list.items():
        test_list_init.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_FUSE_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/FUN_CORE_Generic.PatConfigSetpoints.json"'),
               SetPoint = 'FUSE_OVERRIDES_ALL',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_init

######################################################################
# PrimePatConfigTestMethod TCK
######################################################################
def get_init_tck_list(subflow, hptp, content_list):
     
   test_list_init_tck = []
  
   for test_type, test_parms in content_list.items():
        test_list_init_tck.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_TCK_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/FUN_CORE_Generic.PatConfigSetpoints.json"'),
               SetPoint =  test_parms.get("SetPoint", "TCK_Override"),
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = test_parms.get("Binning", -44), ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_init_tck

######################################################################
# PrimePatConfigTestMethod DTS Configuration
######################################################################
def get_init_dts_list(subflow, hptp, content_list):

   test_list_init_dts = []

   for test_type, test_parms in content_list.items():
        test_list_init_dts.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_DTS_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/FUN_CORE_Generic.PatConfigSetpoints.json"'),
               SetPoint = 'DTS',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_init_dts

######################################################################
# PrimePatConfigTestMethod Debug Counters
######################################################################
def get_init_debugcounter_list(subflow, hptp, content_list):
     
   test_list_debugcounter = []
  
   for test_type, test_parms in content_list.items():
        test_list_debugcounter.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_DEBUG_COUNTER_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/Debug_Counter.PatConfigSetPoints.json"'),
               SetPoint = test_parms.get("SetPoint", f'DBGCNTR_{test_type}'),
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_debugcounter

######################################################################
# PrimePatConfigTestMethod Wait Time
######################################################################
def get_init_waittime_list(subflow, hptp, content_list):
     
   test_list_waittime = []
  
   for test_type, test_parms in content_list.items():
        test_list_waittime.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_WAIT_TIME_{test_type}",
               Plist = test_parms.get("Plist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list"),
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/Wait_Time.PatConfigSetPoint.json"'),
               SetPoint = test_parms.get ("SetPoint", f'{test_type}_Wait_Times_MM'),
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_waittime

######################################################################
# PinMap INIT RunCallback
######################################################################
def get_init_nonmisr_pinmap_list(content_list):
     
   test_list_nonmisr_pinmap_init = []
  
   for nonmisr_test, test_parms in content_list.items():
        test_list_nonmisr_pinmap_init.append(RunCallback(name=f"SBFT_CORE_UF_K_INIT_X_X_X_X_VMIN_PINMAP_{nonmisr_test}",
               Parameters = f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_CORE_{sku}/InputFiles/DieRecoveryPinMaps_FREQ_FUN_CORE.json',
               Callback = 'LoadPinmapFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_nonmisr_pinmap_init

######################################################################
# PinMap APEX INIT RunCallback
######################################################################
def get_init_nonmisr_apex_pinmap_list(content_list):
     
   test_list_nonmisr_apex_pinmap_init = []
  
   for nonmisr_apex_test, test_parms in content_list.items():
        test_list_nonmisr_apex_pinmap_init.append(RunCallback(name=f"SBFT_CORE_UF_K_INIT_X_X_X_X_VMIN_PINMAP_{nonmisr_apex_test}",
               Parameters = f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_CORE_{sku}/InputFiles/DieRecoveryPinMaps_FREQ_FUN_CORE_APEX.json',
               Callback = 'LoadPinmapFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_nonmisr_apex_pinmap_init

######################################################################
# MISR PinMap INIT RunCallback
######################################################################
def get_init_misr_pinmap_list(content_list):
     
   test_list_misr_pinmap_init = []
  
   for misr_test, test_parms in content_list.items():
        test_list_misr_pinmap_init.append(RunCallback(name=f"SBFT_CORE_UF_K_INIT_X_X_X_X_VMIN_PINMAP_{misr_test}",
               Parameters = f'--decoder RegisterCompareDecoder --file ./Modules/FUN/FUN_CORE_{sku}/InputFiles/DieRecoveryPinMaps_FREQ_MISR_FUN_CORE.json',
               Callback = 'LoadPinmapFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_misr_pinmap_init

######################################################################
# ApexTC INIT RunCallback
######################################################################
def get_init_apextc_list(content_list):
     
   test_list_apextc_init = []
  
   for test_type, test_parms in content_list.items():
        test_list_apextc_init.append(RunCallback(name=f"SBFT_CORE_RUNCALLBACK_K_INIT_X_X_X_X_{test_type}",
               Parameters = Spec(f'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUN/FUN_CORE_CX48/InputFiles/ApexTC_Input_Config.json"'),
               Callback = 'ReadFrequencyPatConfigFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_apextc_init

######################################################################
# DEDC LoadConfig
######################################################################
def get_init_dedc_list(content_list):
     
   test_list_dedc = []
  
   for test_type, test_parms in content_list.items():
        test_list_dedc.append(DedcLoadConfigTC(name=f"SBFT_CORE_{test_type}_K_INIT_X_X_X_X_CONFIG",
               	BypassPort = test_parms["Bypass"],
                ConfigFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/FUN_CORE_DEDC.json"'),
                Scope = "LOCAL",
                ValidationMode = "SYNTAX_AND_RULES",
                CoreAware = "ENABLE",
                Modules = f"FUN_CORE_{sku}",
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_dedc

######################################################################
# DEDC DDGSHMOO
######################################################################
def get_shmoo_list(corner, content_list):
     
   test_list_shmoo = []
  
   for test_type, test_parms in content_list.items():
        test_list_shmoo.append(DDGShmooTC(name=f"SBFT_CORE_SHMOO_E_FMINXCR_X_CR_X_X_{test_type}_{corner}",
               	LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                Patlist = test_parms.get("Patlist", f"IPC::fun_cdie_fminxcr_{test_type.lower()}_hptp800_list"),
                PrintFormat = "ECADS",
                SetPointsPlistParamName = "Patlist",
                PreInstance = "Call(EvaluateExpression(--expression 'MOV 0,R1' --result G.U.S.R1_SET_OPERAND --datatype string --storagetype gsds))",
                SetPointsPreInstance = Spec(f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz,MCdrv:R1_SET,MCfun:DBGCNTR:{corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.{test_type}_{corner}'),
                TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
                VoltageConverter = test_parms.get("VoltageConverter", "--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE"),
                XAxisParam = "p_all_mts",
                XAxisRange = "750e6:10e6:12",
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                YAxisParam = "CORE1,CORE0",
                YAxisRange = "1:-0.05:12" if corner in ["F1", "F2", "F3"] else "1.25:-0.05:12",
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                LogLevel ="Enabled",
                BypassPort = test_parms.get("Bypass", 1),
               _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44),
               r1=pPass(goto="NEXT"),
               r2=pPass(goto="NEXT"))))

   return test_list_shmoo

######################################################################
# RATIO DDGSHMOO
######################################################################
def get_shmoo_ratio_list(corner, content_list):
     
   test_list_shmoo_ratio = []
  
   for test_type, test_parms in content_list.items():
        test_list_shmoo_ratio.append(DDGShmooTC(name=f"SBFT_CORE_SHMOO_E_FMINXCR_X_CR_X_X_{test_type}_FREQ",
               	LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                Patlist = test_parms.get("Patlist", f"IPC::fun_cdie_fminxcr_{test_type.lower()}_hptp800_list"),
                PrintFormat = "ECADS",
                SetPointsPlistParamName = "Patlist",
                PreInstance = "Call(EvaluateExpression(--expression 'MOV 0,R1' --result G.U.S.R1_SET_OPERAND --datatype string --storagetype gsds))",
                SetPointsPreInstance = Spec(f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz,MCdrv:R1_SET,MCfun:DBGCNTR:F7"'),
                TimingsTc = "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p",
                VoltageConverter = test_parms.get("VoltageConverter", "--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE"),
                XAxisParam = "MCfun:funcore_corefreq0",
                XAxisRange = "1.2GHz,1.3GHz,1.4GHz,1.5GHz,1.6GHz,1.7GHz,1.8GHz,1.9GHz,2.0GHz,2.1GHz,2.2GHz,2.3GHz,2.4GHz,2.5GHz,2.6GHz,2.7GHz,2.8GHz,2.9GHz,3.0GHz,3.1GHz,3.2GHz,3.3GHz,3.4GHz,3.5GHz,3.6GHz,3.7GHz,3.8GHz,3.9GHz,4.0GHz,4.1GHz,4.2GHz,4.3GHz,4.4GHz,4.5GHz,4.6GHz,4.7GHz",
                XAxisType = "PatConfigSetPoint",
                XAxisParamType = "PatConfigSetPoint",
                YAxisParam = "CORE0",
                YAxisRange = "1.15:-0.05:12",
                YAxisType = "FIVR",
                YAxisParamType = "UserDefined",
                LogLevel ="Enabled",
                BypassPort = test_parms.get("Bypass", 1),
               _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44),
               r1=pPass(goto="NEXT"),
               r2=pPass(goto="NEXT"))))

   return test_list_shmoo_ratio

######################################################################
# PrimePatConfigTestMethod DRG VVAR
######################################################################
def get_init_drg_vvar_list(subflow, hptp, content_list):
     
   test_list_vvar = []
  
   for test_type, test_parms in content_list.items():
        test_list_vvar.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_DRG_VVAR_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/DRG_VVAR.PatConfigSetPoints.json"'),
               SetPoint = test_parms.get("SetPoint", f'VVAR_{test_type}'),
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_vvar

######################################################################
# ImpactStudiesVmin DRG VVAR
######################################################################
def get_impactstudy_list(flow, corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_ImpactStudy = []
  
   for test_type, test_parms in content_list.items():
        test_list_ImpactStudy.append(ImpactStudiesVmin(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{FlowMatrix}_X_IMPACTSTUDY_{test_type}",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/IS_FUNCORE_MP_Vminconfig.json"'),
               VminForwardOffset = 0,
               LogLevel = "Enabled",
               SetPointsPlistParamName = "Patlist",
               FivrConditionPlistParamName = "Patlist",
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44),
               r1=pPass(goto="NEXT"))))

   return test_list_ImpactStudy

######################################################################
# Thermal RunCallback
######################################################################
def get_thermal_list(subflow,content_list):
     
   test_list_thermal = []
  
   for test_type, test_parms in content_list.items():
        test_list_thermal.append(RunCallback(name=f"SBFT_CORE_RUNCALLBACK_K_{subflow}_X_X_X_X_{test_type}",
               Parameters = test_parms.get("Parameters", Spec(f'FunThermal.RCT90')),
               Callback = "ApplyControlSetpoint",
               BypassPort = test_parms.get("Bypass", Spec(f'FUN_CORE_CX48_Rules.If_HOT(-1,-1,1)')),
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_thermal

################# START MTPL FLOW DEFINITON #####################
  
product_skus = ["CX48"]
 
for sku in product_skus:                                                    # <<<<<<<< This one
    mtplname = f"{product}_{sku}"
    # Initialize the module by defining the output mtpl path and the module name
    InitializeNVLClass(f'{mtplname}', f'{mtplname}', binrange = [(44002000, 44502999), (94442434, 94442533)], mttbinstrategy = NVLClass8dig, basenumrange = (11101, 11300), defaultthermalbin = [(97442000, 97442999),(97942434, 97942533)], defaultresetbin =[(44192000, 44192999), (94192434, 94192533)], defaultrm2bin=[(99442000, 99442999), (99942434, 99942533)], defaultrm1bin=[(98442000, 98442999), (98942434, 98942533)])
    
    #################################################################
    #         
    #                       INIT SUBFLOW                      
    #
    #################################################################
    INIT_SUBFLOW = "VMAXXCR"
    INIT_CORNER = "F1"
    # Input
    if sku == "CX48":
        Import(f"FUN_CORE_{sku}.usrv")
        Import(f"FUN_CORE_{sku}_TIMING.tcg")

        INIT_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False}
        }

        ApexcTC_content_list = {
        "APEXTC" :   {"Bypass" : 1, "IS_EDC" : False}
        }

        DebugCounter_Init_List = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False, "SetPoint" : f'DBGCNTR_SLC_DRG'},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False}
        }

        WaiTTime_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False, "SetPoint" : "MLC_Wait_Times_MM_N2P"},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False}, #"SetPoint" : "MLC_LS_WTO_FINAL"},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
	   "SetPoint" : "MLC_DRG_IS_Wait_Times_MM_N2P"},
       "MLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : False},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
	   "SetPoint" : "SLC_DRG_IS_Wait_Times_MM_N2P"},
       "SLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : False}
        }

        NonMisr_Pinmap_Content = {
       "NONMISR" : {"Bypass" : -1, "IS_EDC" : False}
        }

        NonMisrApex_Pinmap_Content = {
       "NONMISR_APEX" : {"Bypass" : -1, "IS_EDC" : False}
        }

        Misr_Pinmap_Content = {
       "MISR" : {"Bypass" : -1, "IS_EDC" : False}
        }

        DEDC_Content = {
       "DEDC" : {"Bypass" : -1, "IS_EDC" : False}
        }

        DRG_VVAR_list = {
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : False}
        }

        INIT_TCK_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False, "SetPoint" : "TCK_Override_V0_SLC"},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False, "SetPoint" : "TCK_Override_V0", "Binning" : -44},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False, "SetPoint" : "TCK_Override_V0_SLCDRG", "Binning" : -44},
       "MLC_DRG_IS" : {"Bypass" : 1, "IS_EDC" : False, "SetPoint" : "TCK_Override_V0", "Binning" : -44},
       "SLC_DRG_IS" : {"Bypass" : 1, "IS_EDC" : False, "SetPoint" : "TCK_Override_V0_SLCDRG", "Binning" : -44},
        }

        INIT_DTS_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False},
        }

    else:
        {
            }

    NONMISRPINMAP_INIT_Tests = get_init_nonmisr_pinmap_list(NonMisr_Pinmap_Content)

    NONMISRPINMAP_APEX_INIT_Tests = get_init_nonmisr_apex_pinmap_list(NonMisrApex_Pinmap_Content)

    MISRPINMAP_INIT_Tests = get_init_misr_pinmap_list(Misr_Pinmap_Content)
    
    PINMAP_COMP = Flow ("FUN_CORE_CX48_INIT_PINMAP", NONMISRPINMAP_INIT_Tests, MISRPINMAP_INIT_Tests, NONMISRPINMAP_APEX_INIT_Tests)

    INIT_FUSE_Tests = get_init_fuse_list(INIT_SUBFLOW, HPTP, INIT_content_list)
    INIT_TEST_COMP = Flow("FUN_CORE_CX48_INIT_FUSE_PATMOD", INIT_FUSE_Tests)

    INIT_DC_Tests = get_init_debugcounter_list(INIT_SUBFLOW, HPTP, DebugCounter_Init_List)
    INIT_DC_COMP = Flow("FUN_CORE_CX48_INIT_DEBUG_COUNTER", INIT_DC_Tests)

    INIT_WT_Tests = get_init_waittime_list(INIT_SUBFLOW, HPTP, WaiTTime_content_list)
    INIT_WT_COMP = Flow("FUN_CORE_CX48_INIT_WAIT_TIME", INIT_WT_Tests)

    APEXTC_INIT_Tests = get_init_apextc_list(ApexcTC_content_list)

    DEDC_INIT = get_init_dedc_list(DEDC_Content)

    INIT_VVAR_Tests = get_init_drg_vvar_list(INIT_SUBFLOW, HPTP, DRG_VVAR_list)
    INIT_VVAR_COMP = Flow("FUN_CORE_CX48_INIT_DRG_VVAR", INIT_VVAR_Tests)

    TCK_INIT_Tests = get_init_tck_list(INIT_SUBFLOW, HPTP, INIT_TCK_content_list)
    INIT_TCK_COMP = Flow("FUN_CORE_CX48_INIT_TCK", TCK_INIT_Tests)

    DTS_INIT_Tests = get_init_dts_list(INIT_SUBFLOW, HPTP, INIT_DTS_content_list)

    INIT_Subflow = Flow(f"FUN_CORE_{sku}_INIT",
                        Fitem ('SAME', PINMAP_COMP, r0=pFail(ret=0 ), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_TEST_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_DC_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_WT_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_VVAR_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_TCK_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        DTS_INIT_Tests, APEXTC_INIT_Tests, DEDC_INIT)
    #################################################################
    #         
    #                       XCRF5 SUBFLOW                      
    #
    #################################################################
    XCRF5_Flow = "XCRF5"
    XCRF5_Corner = "F5"
    XCRF5_FlowMatrix = "F5_X_FREQ"
    XCRF5_CornerID = "C5"
    XCRF5_SubFlow = "F5XCR"

    APEX_Flow = "XCRF5"
    APEX_Corner = "F5"                        
    APEX_FlowMatrix = "CR_F5_FREQ"
  
    # Input
    if sku == "CX48":

        XCRF5_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : True,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                   "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_{XCRF5_CornerID}")+f'+",MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{XCRF5_CornerID}")),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF5_Corner}')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5'),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF5_CornerID}")+f'+",MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{XCRF5_CornerID}")),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF5_Corner}')}
        }
        XCRF5MLC_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')}
       }
        XCRF5MLCLS_content_list = {
       "MLC_LS" : {"Bypass" : Spec(f'__shared__::TpRule.If_DS0_DS1_M(-1, 1, 1, 1)'), "IS_EDC" : True,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                   "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')}
       }
        XCRF5MLCDRG_content_list = {
       "MLC_DRG" : {"Bypass" : Spec(f'__shared__::TpRule.If_DS0_DS1_M(-1, 1, 1, 1)'), "IS_EDC" : True,
                    "PreInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal70DRG,FunThermal.Thermal70DRG,"")'),
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5')}
       }
        XCRF5SLC_content_list = {
       "SLC" : {"Bypass" : 1, "IS_EDC" : False,
                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_{XCRF5_CornerID}")+f'+",MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{XCRF5_CornerID}")),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF5_Corner}')}
       }
        XCRF5SLCDRG_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5'),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF5_CornerID}")+f'+",MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{XCRF5_CornerID}")),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF5_Corner}')}
        }

        ApexTC_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_hptp800_burstoff_list",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:FMAX,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_FMAX'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                },
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_drg_hptp800_burstoff_list",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:FMAX,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_FMAX'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                    }
        }
        
        ImpactStudy_content_list = {
       "DRG" : {"Bypass" : 1, "IS_EDC" : True},
       }
       
        XCRF5_Thermal90 = {
       "F5T90" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT90,FunThermal.RCT85,"")')},
       }
        XCRF5_Thermal80 = {
       "F5T80" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT80,FunThermal.RCT75,"")')},
       }
        XCRF5_ThermalTH80 = {
       "F5TH80" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT80,FunThermal.RCT75,"")')},
       }
        XCRF5_Thermal70 = {
       "F5T70" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT70,FunThermal.RCT70,"")')},
       }
        XCRF5_ThermalTH70 = {
       "F5TH70" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT70,FunThermal.RCT70,"")')},
       }
        XCRF5_ThermalT75 = {
       "F5T75" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT75,FunThermal.RCT70,"")')},
       }
        XCRF5_ThermalT85 = {
       "F5T85" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT85,FunThermal.RCT80,"")')},
       }
    else:
        {
            }
    
    #XCRF5_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5_content_list)
    XCRF5MLC_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5MLC_content_list)
    XCRF5MLCLS_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5MLCLS_content_list)
    XCRF5MLCDRG_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5MLCDRG_content_list)
    XCRF5SLC_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5SLC_content_list)
    XCRF5SLCDRG_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5SLCDRG_content_list)

    XCRF5_T80 = get_thermal_list(XCRF5_SubFlow, XCRF5_Thermal80)
    XCRF5_TH80 = get_thermal_list(XCRF5_SubFlow, XCRF5_ThermalTH80)
    XCRF5_T70 = get_thermal_list(XCRF5_SubFlow, XCRF5_Thermal70)
    XCRF5_TH70 = get_thermal_list(XCRF5_SubFlow, XCRF5_ThermalTH70)
    XCRF5_T75 = get_thermal_list(XCRF5_SubFlow, XCRF5_ThermalT75)
    XCRF5_T85 = get_thermal_list(XCRF5_SubFlow, XCRF5_ThermalT85)
    XCRF5_T90 = get_thermal_list(XCRF5_SubFlow, XCRF5_Thermal90)

    APEXTC_Tests = get_test_apextc_all(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTC_content_list)

    APEX_COMP = Flow("FUN_CORE_CX48_FMAX",
                     APEXTC_Tests)

    ImpactStudy_Tests = get_impactstudy_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_SubFlow, HPTP, ImpactStudy_content_list)
  
    XCRF5_Subflow = Flow(f"FUN_CORE_{sku}_F5XCR", 
                         Fitem ('SAME', APEX_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                         #XCRF5_Tests,
                         XCRF5_T75, XCRF5MLC_Tests, XCRF5MLCLS_Tests, XCRF5MLCDRG_Tests,
                         XCRF5_T85, XCRF5SLC_Tests, XCRF5SLCDRG_Tests,
                         XCRF5_TH70,
                         ImpactStudy_Tests)

    #XCRF5_Subflow = Flow(f"FUN_CORE_{sku}_F5XCR", XCRF5_Tests)
    #################################################################
    #         
    #                       XCRLOF5 SUBFLOW                      
    #
    #################################################################
    XCRLOF5_Flow = "XCRLOF5"
    XCRLOF5_Corner = "F5"
    XCRLOF5_FlowMatrix = "F5_X_FREQ"
    XCRLOF5_CornerID = "C5"
    XCRLOF5_SubFlow = "F5XCRLO"

    # Input
    if sku == "CX48":

        XCRLOF5_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True, "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF5_SubFlow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRLOF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRLOF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRLOF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{XCRLOF5_CornerID}")),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRLOF5_Corner}')},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRLOF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRLOF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRLOF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{XCRLOF5_CornerID}")),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRLOF5_Corner}')},
       }
        XCRLOF5SLC_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCountF5'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRLOF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRLOF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRLOF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_{XCRLOF5_CornerID}")+f'+",MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{XCRLOF5_CornerID}")),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRLOF5_Corner}')}
       }
    else:
        {
            }
    
    #XCRLOF5_Tests = get_test_list(XCRLOF5_Flow, XCRLOF5_Corner, XCRLOF5_FlowMatrix, XCRLOF5_CornerID, XCRLOF5_SubFlow, HPTP, XCRLOF5_content_list)
    XCRLOF5SLC_Tests = get_test_list(XCRLOF5_Flow, XCRLOF5_Corner, XCRLOF5_FlowMatrix, XCRLOF5_CornerID, XCRLOF5_SubFlow, HPTP, XCRLOF5SLC_content_list)

  
    XCRLOF5_Subflow = Flow(f"FUN_CORE_{sku}_F5XCRLO", XCRLOF5SLC_Tests)

    #################################################################
    #         
    #                       XCRF1 SUBFLOW                      
    #
    #################################################################
    XCRF1_Flow = "XCRF1"
    XCRF1_Corner = "F1"                        
    XCRF1_FlowMatrix = "CR_F1_FREQ"
    XCRF1_Subflow = "F1XCR"
    XCRLF1_CornerID = "C1"
  
    # Input
    if sku == "CX48":
        XCRF1_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "EndVoltageLimits" : Spec(f"__shared__::TpRule.If_CHOT(__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE)")},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "EndVoltageLimits" : Spec(f"__shared__::TpRule.If_CHOT(__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE)")},
       "MLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True, 
                                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                                "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS'),
                                "EndVoltageLimits" : Spec(f"__shared__::TpRule.If_CHOT(__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE)")},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   "EndVoltageLimits" : Spec(f"__shared__::TpRule.If_CHOT(__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE)"),
                   "VminResult": "SBFT_MLCLS_F1CR1_MISR_SEARCH,SBFT_MLCLS_F1CR0_MISR_SEARCH"},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "EndVoltageLimits" : Spec(f"__shared__::TpRule.If_CHOT(__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE)"),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF1_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF1_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF1_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF1_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF1_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_{XCRF1_Corner}'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF1_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF1_Corner}')},
       "SLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True,
                     "EndVoltageLimits" : Spec(f"__shared__::TpRule.If_CHOT(__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE)"),
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                    "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS'),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF1_Subflow.lower()}_slc_drg_impactstudy_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF1_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF1_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF1_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF1_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF1_Corner}'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF1_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF1_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                 "EndVoltageLimits" : Spec(f"__shared__::TpRule.If_CHOT(__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE)"),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF1_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF1_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF1_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF1_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF1_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_{XCRF1_Corner}'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF1_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF1_Corner}')},
       }
        XCRF1_misr_list = {
       "MLC_LS_MISR" : {"Bypass" : 1, "IS_EDC" : True, "Binning" : -44},
        }
    else:
        {
            }
    
    XCRF1_Tests = get_test_list_f1_f4(XCRF1_Flow, XCRF1_Corner, XCRLF1_CornerID, XCRF1_FlowMatrix, XCRF1_Subflow, HPTP, XCRF1_content_list)
    
    XCRF1_MISR_Tests = get_test_list_misr(XCRF1_Flow, XCRF1_Corner, XCRF1_FlowMatrix, XCRF1_Subflow, HPTP, XCRF1_misr_list)
  
    XCRF1_Subflow = Flow(f"FUN_CORE_{sku}_F1XCR", XCRF1_Tests,XCRF1_MISR_Tests)

    #################################################################
    #         
    #                       XCRF2 SUBFLOW                      
    #
    #################################################################
    XCRF2_Flow = "XCRF2"
    XCRF2_Corner = "F2"                        
    XCRF2_FlowMatrix = "CR_F2_FREQ"
    XCRF2_Subflow = "F2XCR"
    XCRF2_CornerID = "C2"
    

    # Input
    if sku == "CX48":
        XCRF2_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_Stagger')},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True, 
                                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                                "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS')},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF2_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF2_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF2_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF2_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF2_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF2_Corner}'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF2_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF2_Corner}')},
       "SLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF2_Subflow.lower()}_slc_drg_impactstudy_hptp800_burstoff_list_master",
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                    "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF2_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF2_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF2_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF2_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF2_Corner}'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF2_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF2_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF2_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF2_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF2_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF2_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF2_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_{XCRF2_Corner}'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF2_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF2_Corner}')},
       }
    else:
        {
            }
    
    XCRF2_Tests = get_test_list_f1_f4(XCRF2_Flow, XCRF2_Corner, XCRF2_CornerID, XCRF2_FlowMatrix, XCRF2_Subflow, HPTP, XCRF2_content_list)
  
    XCRF2_Subflow = Flow(f"FUN_CORE_{sku}_F2XCR", XCRF2_Tests)

    #################################################################
    #         
    #                       XCRF3 SUBFLOW                      
    #
    #################################################################
    XCRF3_Flow = "XCRF3"
    XCRF3_Corner = "F3"                        
    XCRF3_FlowMatrix = "CR_F3_FREQ"
    XCRF3_Subflow = "F3XCR"
    XCRF3_CornerID = "C3"
  
    # Input
    if sku == "CX48":
        XCRF3_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    #"MultiPassMasks" : Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48'),
                    "PreInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal90,FunThermal.Thermal85,"")'),
                    "PostInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal100,FunThermal.Thermal90,"")'),
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_Stagger'),
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')},
       "MLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True, 
                                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                                "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS')},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF3_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF3_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF3_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF3_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF3_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF3_Corner}'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF3_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF3_Corner}')},
       "SLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF3_Subflow.lower()}_slc_drg_impactstudy_hptp800_burstoff_list_master",
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                    "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF3_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF3_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF3_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF3_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF3_Corner}'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF3_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF3_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF3_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF3_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF3_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF3_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF3_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_{XCRF3_Corner}'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF3_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF3_Corner}')},
       }
        XCRF3_misr_list = {
       "MLC_LS_MISR" : {"Bypass" : 1, "IS_EDC" : True, "Binning" : -44, "EndVoltageLimits" : Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE")},
        }
    else:
        {
            }
    
    XCRF3_Tests = get_test_list_f1_f4(XCRF3_Flow, XCRF3_Corner, XCRF3_CornerID, XCRF3_FlowMatrix, XCRF3_Subflow, HPTP, XCRF3_content_list)

    XCRF3_MISR_Tests = get_test_list_misr(XCRF3_Flow, XCRF3_Corner, XCRF3_FlowMatrix, XCRF3_Subflow, HPTP, XCRF3_misr_list)
  
    XCRF3_Subflow = Flow(f"FUN_CORE_{sku}_F3XCR", XCRF3_Tests,XCRF3_MISR_Tests)

    #################################################################
    #         
    #                       XCRF4 SUBFLOW                      
    #
    #################################################################
    XCRF4_Flow = "XCRF4"
    XCRF4_Corner = "F4"                        
    XCRF4_FlowMatrix = "CR_F4_FREQ"
    XCRF4_Subflow = "F4XCR"
    XCRF4_CornerID = "C4"
  
    # Input
    if sku == "CX48":
        XCRF4_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "PreInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal90,FunThermal.Thermal85,"")'),
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_Stagger')
                },
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    #"MultiPassMasks" : Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48'),
                    "PreInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal70,FunThermal.Thermal70,"")'),
					"DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_Stagger')
                    },
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   #"MultiPassMasks" : Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48'),
                   "PreInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal90,FunThermal.Thermal85,"")'),
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                   "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_Stagger')
                   },
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    #"MultiPassMasks" : Spec(f'FUN_CORE_{sku}_Specs.MultiPass_CX48'),
                    "PostInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal70,FunThermal.Thermal70,"")'),
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF4_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF4_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_{XCRF4_Corner}'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF4_Corner}')},
       "SLC" : {"Bypass" : 1, "IS_EDC" : False,
                "PostInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal70,FunThermal.Thermal70,"")'),
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF4_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRF4_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_{XCRF4_Corner}'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRF4_Corner}')},
       }

    else:
        {
            }
    
    XCRF4_Tests = get_test_list_f1_f4(XCRF4_Flow, XCRF4_Corner, XCRF4_CornerID, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_content_list)
  
    XCRF4_Subflow = Flow(f"FUN_CORE_{sku}_F4XCR",
                         XCRF4_Tests)

    #################################################################
    #         
    #                       XCRLOF4 SUBFLOW                      
    #
    #################################################################
    XCRLOF4_Flow = "XCRLOF4"
    XCRLOF4_Corner = "F4"                        
    XCRLOF4_FlowMatrix = "CR_F4_FREQ"
    XCRLOF4_Subflow = "F4XCRLO"
    XCRLOF4_CornerID = "C4"
  
    # Input
    if sku == "CX48":
        XCRLOF4_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                #"PostInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal70,FunThermal.Thermal70,"")'),
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_cx48'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF4_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRLOF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRLOF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRLOF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{XCRLOF4_Corner},MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_{XCRLOF4_Corner}'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{XCRLOF4_Corner}')},
       }
    else:
        {
            }
    
    XCRLOF4_Tests = get_test_list_f1_f4(XCRLOF4_Flow, XCRLOF4_Corner, XCRLOF4_CornerID, XCRLOF4_FlowMatrix, XCRLOF4_Subflow, HPTP, XCRLOF4_content_list)
  
    XCRLOF4_Subflow = Flow(f"FUN_CORE_{sku}_F4XCRLO", XCRLOF4_Tests)

    #################################################################
    #         
    #                       FMIN SUBFLOW                      
    #
    #################################################################
    FMIN_Flow = "FMIN"
    FMIN_Corner = "FMIN"                        
    FMIN_FlowMatrix = "CR_FMIN"
    FMIN_Subflow = "FMINXCR"
    FMIN_FREQ = "0400"
    shmoo_cornerf1 = "F1"
    shmoo_cornerf2 = "F2"
    shmoo_cornerf3 = "F3"
    shmoo_cornerf4 = "F4"
    shmoo_cornerf5 = "F5"
    shmoo_cornerf6 = "F6"
    shmoo_cornerf7 = "F7"
  
    # Input
    if sku == "CX48":

        FMIN_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : True},
       "MLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True, 
                                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                                "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_FMIN+",MCfun:DBGCNTR:FMIN,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon"'), 
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{FMIN_Corner}')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_FMIN+",MCfun:DBGCNTR:FMIN,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{FMIN_Corner}')}
        }
        FMIN_MLC_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False, "TimingsTC" : "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p"},
       }
        FMIN_MLCLS_content_list = {
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False, "TimingsTC" : "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p"},
       }
        FMIN_MLCDRG_content_list = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False, "TimingsTC" : "FUN_CORE_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core_n2p"},
       "MLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True, 
                                "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                                "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS')},
       }
        FMIN_SLC_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list",
                 "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_FMIN+",MCfun:DBGCNTR:FMIN,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon"'), 
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{FMIN_Corner}')},
       }

        FMIN_SLCDRG_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_FMIN+",MCfun:DBGCNTR:FMIN,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{FMIN_Corner}')},
       "SLC_DRG_IMPACTSTUDY" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_impactstudy_hptp800_burstoff_list",
                    "FailCaptureCount" : Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount_DRG_IS'), 
                    "FeatureSwitchSettings" : Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_DRG_IS'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_FMIN+",MCfun:DBGCNTR:FMIN,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCF') + f' + DROPOUT.CR_{FMIN_Corner}')}
        }

        SHMOO_content_list = {
       "DEDC" : {"Bypass" : 1, "IS_EDC" : True, "Patlist" : f"IPC::fun_cdie_fminxcr_mlc_hptp800_list"},
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True, 
                "VoltageConverter" : "--overrides CCF:1.1 --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list",},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True, 
                     "VoltageConverter" : "--overrides CCF:1.1 --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                     "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list",},
        }

        SHMOO_content_list_f2_f5 = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True, 
                "VoltageConverter" : "--overrides CCF:1.1 --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list",},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True, 
                    "VoltageConverter" : "--overrides CCF:1.1 --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list",},
        }

        RATIOSHMOO_content_list = {
       "RATIO" : {"Bypass" : 1, "IS_EDC" : True, "Patlist" : f"IPC::fun_cdie_fminxcr_mlc_hptp800_list"}
        }

        WTO_MLC_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       }
       
    else:
        {
            }
    
    SHMOO_TestsF1 = get_shmoo_list(shmoo_cornerf1,SHMOO_content_list)
    SHMOO_TestsF2 = get_shmoo_list(shmoo_cornerf2,SHMOO_content_list_f2_f5)
    SHMOO_TestsF3 = get_shmoo_list(shmoo_cornerf3,SHMOO_content_list_f2_f5)
    SHMOO_TestsF4 = get_shmoo_list(shmoo_cornerf4,SHMOO_content_list_f2_f5)
    SHMOO_TestsF5 = get_shmoo_list(shmoo_cornerf5,SHMOO_content_list_f2_f5)
    SHMOO_TestsF6 = get_shmoo_list(shmoo_cornerf6,SHMOO_content_list_f2_f5)
    SHMOO_TestsF7 = get_shmoo_list(shmoo_cornerf7,SHMOO_content_list_f2_f5)
    RATIOSHMOO_TEST = get_shmoo_ratio_list(shmoo_cornerf1,RATIOSHMOO_content_list)

    SHMOO_COMPF1 = Flow("FUN_CORE_CX48_SHMOO_F1", SHMOO_TestsF1)
    SHMOO_COMPF2 = Flow("FUN_CORE_CX48_SHMOO_F2", SHMOO_TestsF2)
    SHMOO_COMPF3 = Flow("FUN_CORE_CX48_SHMOO_F3", SHMOO_TestsF3)
    SHMOO_COMPF4 = Flow("FUN_CORE_CX48_SHMOO_F4", SHMOO_TestsF4)
    SHMOO_COMPF5 = Flow("FUN_CORE_CX48_SHMOO_F5", SHMOO_TestsF5)
    SHMOO_COMPF6 = Flow("FUN_CORE_CX48_SHMOO_F6", SHMOO_TestsF6)
    SHMOO_COMPF7 = Flow("FUN_CORE_CX48_SHMOO_F7", SHMOO_TestsF7)

    SHMOO_TEST = Flow("FUN_CORE_CX48_SHMOO",
                      Fitem ('SAME', SHMOO_COMPF1, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF2, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF3, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF4, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF5, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF6, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF7, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      RATIOSHMOO_TEST)

    FMIN_MLC_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_MLC_content_list)
    FMIN_MLCLS_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_MLCLS_content_list)
    FMIN_MLCDRG_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_MLCDRG_content_list)
    FMIN_SLC_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_SLC_content_list)
    FMIN_SLCDRG_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_SLCDRG_content_list)
    
    WTO_MLC_Tests = get_test_pattern_wto(WTO_MLC_content_list)

    FMIN_Subflow = Flow(f"FUN_CORE_{sku}_FMINXCR", FMIN_MLC_Tests, FMIN_MLCLS_Tests, FMIN_MLCDRG_Tests, FMIN_SLC_Tests, FMIN_SLCDRG_Tests,
                         Fitem ('SAME', SHMOO_TEST, r0=pFail(ret=1), r1=pPass(goto="NEXT")), WTO_MLC_Tests)

    #################################################################
    #         
    #                       VMAX SUBFLOW                      
    #
    #################################################################
    VMAX_Flow = "VMAX"
    VMAX_Corner = "MAX"                        
    #VMAXF5_FlowMatrix = "CR_F5"
    VMAXF1_FlowMatrix = "CR_F1"
    VMAX_Subflow = "VMAXXCR"
    FREQF5 = "F5"
    FREQF1 = "F1"
    VMAXXCRF5_Flow = "XCRF5"
    VMAXXCRF5_Corner = "F5"
    VMAXF5_FlowMatrix = "F5_X_FREQ"
    VMAXXCRF5_CornerID = "C5"
    VMAXXCRF5_SubFlow = "F5XCR"
  
    if sku == "CX48":
        VMAXF5_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_LS" : {"Bypass" :  Spec(f'__shared__::TpRule.If_DS0_DS1_M(-1, 1, 1, 1)'), "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" :  1, "IS_EDC" : True},
       "SLC" : {"Bypass" :  -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_hptp800_burstoff_list",
                #"SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{VMAXXCRF5_CornerID}"+f'+",MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.SLC_{VMAXXCRF5_CornerID}")),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_F5_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:F5,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_{VMAXXCRF5_Corner}")),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
       "SLC_DRG" : {"Bypass" :  1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_drg_hptp800_burstoff_list",
                    #"SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{VMAXXCRF5_CornerID}"+f'+",MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.SLC_DRG_{VMAXXCRF5_CornerID}")),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_F5_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:F5,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_DRG_{VMAXXCRF5_Corner}")),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
        }
        VMAXF5MLC_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False}
        }
        VMAXF5MLCLS_content_list = {
       "MLC_LS" : {"Bypass" :  Spec(f'__shared__::TpRule.If_DS0_DS1_M(-1, 1, 1, 1)'), "IS_EDC" : True}
       }
        VMAXF5MLCDRG_content_list = {
       "MLC_DRG" : {"Bypass" :  1, "IS_EDC" : True}
       }
        VMAXF5SLC_content_list = {
       "SLC" : {"Bypass" :  -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_hptp800_burstoff_list",
                #"SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{VMAXXCRF5_CornerID}"+f'+",MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.SLC_{VMAXXCRF5_CornerID}")),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_F5_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:F5,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_{VMAXXCRF5_Corner}")),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')}
       }
        VMAXF5SLCDRG_content_list = {
       "SLC_DRG" : {"Bypass" :  1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_drg_hptp800_burstoff_list",
                    #"SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:"'+Spec(f"+ __shared__::Corners.CR_{VMAXXCRF5_CornerID}"+f'+",MCfun:ratio_modify:"')+Spec(f"+FUN_CORE_{sku}_Specs.SLC_DRG_{VMAXXCRF5_CornerID}")),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_F5_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:F5,MCfun:ratio_modify:"'+Spec(f"+FUN_CORE_{sku}_Specs.SLC_DRG_{VMAXXCRF5_Corner}")),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
        }
        VMAXF1_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "PreInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal90,FunThermal.Thermal85,"")'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":0.8GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:F1,MCfun:ratio_modify:"')+f'+FUN_CORE_{sku}_Specs.MLC_F1'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                "PostInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal70,FunThermal.Thermal70,"")'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":0.8GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:F1,MCfun:ratio_modify:"')+f'+FUN_CORE_{sku}_Specs.MLC_LS_F1'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : False,
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":0.8GHz,CORE:nblctrl_core_l2:nbloff,MCfun:DBGCNTR:F1,MCfun:ratio_modify:"')+f'+FUN_CORE_{sku}_Specs.MLC_DRG_F1'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "SLC" : {"Bypass" : 1, "IS_EDC" : False,
                "PostInstance" :  Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.Thermal70,FunThermal.Thermal70,"")'),
                "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_hptp800_burstoff_list",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:F1,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_F1'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_drg_hptp800_burstoff_list",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:F1,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_DRG_F1'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
        }
        MAXCRF5_Thermal90 = {
       "MAXF5T90" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT90,FunThermal.RCT85,"")')},
       }
        MAXCRF5_Thermal80 = {
       "MAXF5T80" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT80,FunThermal.RCT75,"")')},
       }
        MAXCRF5_Thermal70 = {
       "MAXF5T70" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT70,FunThermal.RCT70,"")')},
       }
        MAXCRF5_ThermalTH70 = {
       "MAXF5TH70" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT70,FunThermal.RCT70,"")')},
       }
        MAXCRF5_Thermal75 = {
       "MAXF5T75" : {"Parameters" : Spec(f'FUN_CORE_CX48_Rules.If_HOT(FunThermal.RCT75,FunThermal.RCT70,"")')},
       }
    else:
       {
           }

    #VMAXF5_Tests = get_test_vmaxf5(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_content_list)
    VMAXF5MLC_Tests = get_test_vmaxf5(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5MLC_content_list)
    VMAXF5MLCLS_Tests = get_test_vmaxf5(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5MLCLS_content_list)
    VMAXF5MLCDRG_Tests = get_test_vmaxf5(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5MLCDRG_content_list)
    VMAXF5SLC_Tests = get_test_vmaxf5(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5SLC_content_list)
    VMAXF5SLCDRG_Tests = get_test_vmaxf5(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5SLCDRG_content_list)
    VMAXF1_Tests = get_test_vmax(VMAX_Flow, VMAX_Corner, VMAXF1_FlowMatrix, VMAX_Subflow, HPTP, VMAXF1_content_list, FREQF1)

    VMAXF5_T90 = get_thermal_list(VMAX_Subflow, MAXCRF5_Thermal90)
    VMAXF5_T80 = get_thermal_list(VMAX_Subflow, MAXCRF5_Thermal80)
    VMAXF5_T70 = get_thermal_list(VMAX_Subflow, MAXCRF5_Thermal70)
    VMAXF5_TH70 = get_thermal_list(VMAX_Subflow, MAXCRF5_ThermalTH70)
    VMAXF5_T75 = get_thermal_list(VMAX_Subflow, MAXCRF5_Thermal75)

    VMAXF5_COMP = Flow("FUN_CORE_CX48_VMAXXCR_F5", VMAXF5_T75, VMAXF5MLC_Tests, VMAXF5MLCLS_Tests, VMAXF5MLCDRG_Tests, VMAXF5_T90, VMAXF5SLC_Tests, VMAXF5SLCDRG_Tests, VMAXF5_TH70)
    VMAXF1_COMP = Flow("FUN_CORE_CX48_VMAXXCR_F1", VMAXF1_Tests)
  
    VMAX_Subflow = Flow(f"FUN_CORE_{sku}_VMAXXCR",
                        Fitem ('SAME', VMAXF1_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', VMAXF5_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")))

    #################################################################
    #         
    #                       VMAXXCRLO SUBFLOW                      
    #
    #################################################################
    VMAXXCRLO_Flow = "VMAX"
    VMAXXCRLO_Corner = "MAX"                        
    VMAXXCRLOF5_FlowMatrix = "CR_F5"
    VMAXXCRLOF1_FlowMatrix = "CR_F1" 
    VMAXXCRLO_Subflow = "VMAXXCRLO"
  
    if sku == "CX48":
        VMAXXCRLOF5_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAXXCRLO_Subflow.lower()}_slc_hptp800_burstoff_list",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXXCRLOF5_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{FREQF5}"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAXXCRLO_Subflow.lower()}_slc_drg_hptp800_burstoff_list",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXXCRLOF5_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:{FREQF5}"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')}
        }
        VMAXXCRLOF1_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAXXCRLO_Subflow.lower()}_slc_hptp800_burstoff_list",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXXCRLOF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,MCfun:DBGCNTR:F1,MCfun:ratio_modify:"+FUN_CORE_{sku}_Specs.SLC_F1'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --railconfigurations CDIE_CCF_POWERMUX --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       }
    else:
       {
           }
    
    VMAXXCRLOF5_Tests = get_test_vmax(VMAXXCRLO_Flow, VMAXXCRLO_Corner, VMAXXCRLOF5_FlowMatrix, VMAXXCRLO_Subflow, HPTP, VMAXXCRLOF5_content_list, FREQF5)
    VMAXXCRLOF1_Tests = get_test_vmax(VMAXXCRLO_Flow, VMAXXCRLO_Corner, VMAXXCRLOF1_FlowMatrix, VMAXXCRLO_Subflow, HPTP, VMAXXCRLOF1_content_list, FREQF1)

    VMAXCRLOF5_COMP = Flow("FUN_CORE_CX48_VMAXXCRLO_F5", VMAXXCRLOF5_Tests)
    VMAXCRLOF1_COMP = Flow("FUN_CORE_CX48_VMAXXCRLO_F1", VMAXXCRLOF1_Tests)
  
    VMAXXCRLO_Subflow = Flow(f"FUN_CORE_{sku}_VMAXXCRLO",
                        Fitem ('SAME', VMAXCRLOF1_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', VMAXCRLOF5_COMP, r0=pFail(ret=1), r1=pPass(goto="NEXT")))

    #################################################################
    #         
    #                       LTTCCPU SUBFLOW                      
    #
    #################################################################
    LTTC_XCRF5_Flow = "XCRF5"
    LTTC_XCRF5_Corner = "F5"
    LTTC_XCRF5_FlowMatrix = "F5_X_FREQ"
    LTTC_XCRF5_CornerID = "C5"
    LTTC_XCRF5_SubFlow = "LTTCCPU"
   
    if sku == "CX48":
        LTTC_XCRF5_ALL_content_list = {
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True, "Binning" : -94,}
       }
    else:
        {
            }

    LTTC_ALL_Tests = get_test_list_LTTC(LTTC_XCRF5_Flow, LTTC_XCRF5_Corner, LTTC_XCRF5_FlowMatrix, LTTC_XCRF5_CornerID, LTTC_XCRF5_SubFlow, HPTP, LTTC_XCRF5_ALL_content_list)

    LTTC_XCRF5_Subflow = Flow(f"FUN_CORE_{sku}_LTTCCPU", 
                         LTTC_ALL_Tests)