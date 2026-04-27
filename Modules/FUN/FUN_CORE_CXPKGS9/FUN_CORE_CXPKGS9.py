# Import the necessary classes from Pymtpl
from decimal import ROUND_05UP
from pymtpl.por_methods import VminTC, PrimePatConfigTestMethod, RunCallback, ApexTC, DedcLoadConfigTC, DDGShmooTC, PatternDelayOptimizer
from pymtpl.core import Flow, Fitem, pPass, pFail, NativeMultiTrial, AUTO, InitializeNVLClass, Import, TrialParamSpec, Spec
from pymtpl.binctr import NVLClass8dig

# Define the product name
product = "FUN_CORE"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'
HPTP = "hptp800"
PORT4 = -44
PORT5 = -44
#defaultthermalbin = 9744, defaultresetbin = 4419

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
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_fminxcr_mlc_hptp800_list_master"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_F1_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_pattern_wto

####################################################################################
def get_test_apextc_1100R1(corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_apextcflow1100R1 = []
  
   for test_type, test_parms in content_list.items():
      test_list_apextcflow1100R1.append(ApexTC(name=f'SBFT_CORE_VMIN_E_{subflow}_X_CR_{corner}_1100_{test_type}_APEX_FMAX_R1',
         #InitialMaskBits = TrialParamSpec(f'FUN_CORE_{sku}_Specs.Apex_Multipass'),
         #InitialMaskBits = "11001100",
         StepSize = 3,
         InitialMaskBits = "11111100" if test_type in ["SLC"] else "11111100",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfigS52C')),
         BypassPort = test_parms["Bypass"],
         Targets = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_Targets'),
         ForwardingMode = "Input",
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR_APEX')),
         #SetPointsPostInstance = "MCdrv:R1_SET",
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_fmax_{test_type.lower()}_{hptp.lower()}_list_master"),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryOptions = "",
         RecoveryTracking = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         End = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
         Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
         FivrCondition = "NOM_CCF_CORE",
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         ExportTokens = Spec(f'__shared__::APEX_Tokens.CRToken'),
         #ExportTokens = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_ExportTokens'),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_apextcflow1100R1

####################################################################################

####################################################################################
def get_test_apextc_1100R2(corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_apextcflow1100R2 = []
  
   for test_type, test_parms in content_list.items():
      test_list_apextcflow1100R2.append(ApexTC(name=f'SBFT_CORE_VMIN_E_{subflow}_X_CR_{corner}_1100_{test_type}_APEX_FMAX_R2',
         #InitialMaskBits = TrialParamSpec(f'FUN_CORE_{sku}_Specs.Apex_Multipass'),
         #InitialMaskBits = "11001100",
         StepSize = 3,
         InitialMaskBits = "11001111" if test_type in ["SLC"] else "11001111",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfigS52C')),
         BypassPort = test_parms["Bypass"],
         Targets = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_Targets'),
         ForwardingMode = "Input",
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR_APEX')),
         #SetPointsPostInstance = "MCdrv:R1_SET",
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_fmax_{test_type.lower()}_{hptp.lower()}_list_master"),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryOptions = "",
         RecoveryTracking = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         End = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
         Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
         FivrCondition = "NOM_CCF_CORE",
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         ExportTokens = Spec(f'__shared__::APEX_Tokens.CRToken'),
         #ExportTokens = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_ExportTokens'),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_apextcflow1100R2

####################################################################################
def get_test_apextc_0011R1(corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_apextcflow0011R1 = []
  
   for test_type, test_parms in content_list.items():
      test_list_apextcflow0011R1.append(ApexTC(name=f'SBFT_CORE_VMIN_E_{subflow}_X_CR_{corner}_0011_{test_type}_APEX_FMAX_R1',
         #InitialMaskBits = TrialParamSpec(f'FUN_CORE_{sku}_Specs.Apex_Multipass'),
         #InitialMaskBits = "00110011",
         StepSize = 3,
         InitialMaskBits = "11110011" if test_type in ["SLC"] else "11110011",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfigS52C')),
         BypassPort = test_parms["Bypass"],
         Targets = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_Targets'),
         ForwardingMode = "Input",
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR_APEX')),
         #SetPointsPostInstance = "MCdrv:R1_SET",
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_fmax_{test_type.lower()}_{hptp.lower()}_list_master"),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryOptions = "",
         RecoveryTracking = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         End = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
         Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
         FivrCondition = "NOM_CCF_CORE",
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         ExportTokens = Spec(f'__shared__::APEX_Tokens.CRToken'),
         #ExportTokens = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_ExportTokens'),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_apextcflow0011R1

####################################################################################
def get_test_apextc_0011R2(corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_apextcflow0011R2 = []
  
   for test_type, test_parms in content_list.items():
      test_list_apextcflow0011R2.append(ApexTC(name=f'SBFT_CORE_VMIN_E_{subflow}_X_CR_{corner}_0011_{test_type}_APEX_FMAX_R2',
         #InitialMaskBits = TrialParamSpec(f'FUN_CORE_{sku}_Specs.Apex_Multipass'),
         #InitialMaskBits = "00110011",
         StepSize = 3,
         InitialMaskBits = "00111111" if test_type in ["SLC"] else "00111111",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfigS52C')),
         BypassPort = test_parms["Bypass"],
         Targets = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_Targets'),
         ForwardingMode = "Input",
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR_APEX')),
         #SetPointsPostInstance = "MCdrv:R1_SET",
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_fmax_{test_type.lower()}_{hptp.lower()}_list_master"),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryOptions = "",
         RecoveryTracking = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         End = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
         Start = Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
         FivrCondition = "NOM_CCF_CORE",
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         ExportTokens = Spec(f'__shared__::APEX_Tokens.CRToken'),
         #ExportTokens = Spec(f'FUN_CORE_{sku}_Specs.ApexTC_2CDIE_ExportTokens'),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_apextcflow0011R2
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
         CornerIdentifiers = f"CR7@F1,CR6@F1,CR5@F1,CR4@F1,CR3@F1,CR2@F1,CR1@F1,CR0@F1",
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "Input",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts400_tstprtclk200_tck50_i_drv_mul_fun_CORE",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         #BaseNumbers = None if test_parms["IS_EDC"] else AUTO,
         BaseNumbers = AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         #LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
         LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
         #LimitGuardband = Spec('__shared__::TpRule.If_QRE("",toString(__shared__::GBVars.FminLimitGuardband))'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_NoRec'),
         #RecoveryOptions = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryOptions_MTT'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         #RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         VminResult = Spec(f'"SBFT_{test_type}_CR7_FMIN_FF_SEARCH,SBFT_{test_type}_CR6_FMIN_FF_SEARCH,SBFT_{test_type}_CR5_FMIN_FF_SEARCH,SBFT_{test_type}_CR4_FMIN_FF_SEARCH,SBFT_{test_type}_CR3_FMIN_FF_SEARCH,SBFT_{test_type}_CR2_FMIN_FF_SEARCH,SBFT_{test_type}_CR1_FMIN_FF_SEARCH,SBFT_{test_type}_CR0_FMIN_FF_SEARCH"'),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance= Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.{FlowMatrix}+")*60)),9)))"'),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}")+f'+"GHz,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR'))),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR'))),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r4=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_fminflow

####################################################################################

####################################################################################
def get_test_list_fminfailflow(flow, corner, FlowMatrix, subflow, hptp, freq, content_list):
     
   test_list_fminfailflow = []
  
   for test_type, test_parms in content_list.items():
      test_list_fminfailflow.append(VminTC(name=f'SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_{freq}_{test_type}_FMIN_FF_SEARCH',
         BypassPort = test_parms["Bypass"],
         #ExecutionMode = "Search" if test_parms["IS_EDC"] else "SearchWithScoreboard",
         ExecutionMode = "SearchWithScoreboard",
         TestMode = "MultiVmin",
         #CornerIdentifiers = f"CR7@F1,CR6@F1,CR5@F1,CR4@F1,CR3@F1,CR2@F1,CR1@F1,CR0@F1",
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "Input",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts400_tstprtclk200_tck50_i_drv_mul_fun_CORE",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         #BaseNumbers = None if test_parms["IS_EDC"] else AUTO,
         BaseNumbers = AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_NoRec'),
         #RecoveryOptions = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryOptions_MTT'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         #RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         VminResult = Spec(f'"SBFT_{test_type}_CR7_FMIN_FF_SEARCH,SBFT_{test_type}_CR6_FMIN_FF_SEARCH,SBFT_{test_type}_CR5_FMIN_FF_SEARCH,SBFT_{test_type}_CR4_FMIN_FF_SEARCH,SBFT_{test_type}_CR3_FMIN_FF_SEARCH,SBFT_{test_type}_CR2_FMIN_FF_SEARCH,SBFT_{test_type}_CR1_FMIN_FF_SEARCH,SBFT_{test_type}_CR0_FMIN_FF_SEARCH"'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         PreInstance= Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.{FlowMatrix}+")*60)),9)))"'),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}")+f'+"GHz,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR'))),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR'))),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_fminfailflow

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
         MultiPassMasks = "" if corner in ["F1", "F2"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_2CDIESLC') if test_type in ["SLC"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_2CDIE'),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         #CornerIdentifiers = f"CR7@{corner},CR6@{corner},CR5@{corner},CR4@{corner},CR3@{corner},CR2@{corner},CR1@{corner},CR0@{corner}",
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
         #RecoveryMode = "NoRecovery",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", ""),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance= test_parms.get("PreInstance", ""),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r4=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_funflow

####################################################################################

####################################################################################
def get_test_list_f4M0M1(flow, corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_funflowf4M0M1 = []
  
   for test_type, test_parms in content_list.items():
      test_list_funflowf4M0M1.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_X_{test_type}_M0M1",
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE",
         _comment='SpeedFlow F1_F4 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}_M0M1"',
         BypassPort = test_parms["Bypass"],
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM0M1'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = f"CR7@{corner},CR6@{corner},CR5@{corner},CR4@{corner},CR3@{corner},CR2@{corner},CR1@{corner},CR0@{corner}",
         EndVoltageLimits = test_parms.get("EndVoltageLimits", Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         #RecoveryMode = "NoRecovery",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", ""),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_funflowf4M0M1

####################################################################################

####################################################################################
def get_test_list_f4M2M3(flow, corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_funflowf4M2M3 = []
  
   for test_type, test_parms in content_list.items():
      test_list_funflowf4M2M3.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_X_{test_type}_M2M3",
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE",
         _comment='SpeedFlow F1_F4 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}_M2M3"',
         BypassPort = test_parms["Bypass"],
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM2M3'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = f"CR7@{corner},CR6@{corner},CR5@{corner},CR4@{corner},CR3@{corner},CR2@{corner},CR1@{corner},CR0@{corner}",
         EndVoltageLimits = test_parms.get("EndVoltageLimits", Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         #RecoveryMode = "NoRecovery",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", ""),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_funflowf4M2M3

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
         MultiPassMasks = Spec(f'FUN_CORE_{sku}_Specs.MultiPass_2CDIESLC') if test_type in ["SLC"] else Spec(f'FUN_CORE_{sku}_Specs.MultiPass_2CDIE'),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = TrialParamSpec(Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , ["","",""])')),
         StartVoltagesOffset = TrialParamSpec(Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , ["","",""])')),
         #StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         #StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         #RecoveryMode = "NoRecovery",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.CR_C5+")*60)),9)))"'),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r4=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list
####################################################################################

####################################################################################

def get_test_listM0M1(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list_M0M1 = []
  
   for test_type, test_parms in content_list.items():
      test_list_M0M1.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{FlowMatrix}_X_{test_type}_M0M1", 
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
         _comment='SpeedFlow F5_F7 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + f' + "_X_{test_type}_M0M1"',
         BypassPort = test_parms["Bypass"],
         #MultiPassMasks = Spec(f'FUN_CORE_{sku}_Specs.MultiPass'),
         InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM0M1'),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         #RecoveryMode = "NoRecovery",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_M0M1
####################################################################################

####################################################################################

def get_test_listM2M3(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list_M2M3 = []
  
   for test_type, test_parms in content_list.items():
      test_list_M2M3.append(NativeMultiTrial(name=f"SBFT_CORE_VMIN_K_{subflow}_X_CR_{FlowMatrix}_X_{test_type}_M2M3", 
           
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
         _comment='SpeedFlow F5_F7 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + f' + "_X_{test_type}_M2M3"',
         BypassPort = test_parms["Bypass"],
         #MultiPassMasks = Spec(f'FUN_CORE_{sku}_Specs.MultiPass'),
         InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM2M3'),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         ScoreboardEdgeTicks = "" if "SCR" in flow else Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         TestMode = "MultiVmin",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         #RecoveryMode = "NoRecovery",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Next"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_M2M3
####################################################################################

def get_test_vmax(flow, corner, FlowMatrix, subflow, hptp, content_list, freq):
     
   test_list_vmaxflow = []
  
   for test_type, test_parms in content_list.items():
      test_list_vmaxflow.append(VminTC(name=f'SBFT_CORE_VMAX_K_{subflow}_X_CR_{corner}_X_{test_type}_{freq}',
         BypassPort = test_parms["Bypass"],
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         TestMode = "Scoreboard",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
         ForwardingMode = "Input",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         #LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         #RecoveryMode = "NoRecovery",
         #RecoveryOptions = "",
         #RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         #RecoveryTrackingOutgoing = "",
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_MTT'),
         RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_CR'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         #DtsConfiguration = Spec(f'FUN_CORE_{sku}_Specs.dtsconfig'),
         PreInstance= test_parms.get("PreInstance", ""),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_vmaxflow

####################################################################################

####################################################################################

def get_test_vmaxf5MP(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list_vmaxflowf5MP = []
  
   for test_type, test_parms in content_list.items():
      test_list_vmaxflowf5MP.append(NativeMultiTrial(name=f'SBFT_CORE_VMAX_K_{subflow}_X_CR_{FlowMatrix}_{test_type}_MP',
		
		 exitaction="Continue",
		 trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
		 _comment='SpeedFlow F5_F7 VminTC test with MTT',
		 template=VminTC(name=f'"SBFT_CORE_VMAX_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.CR_{corner_id}") + f' + "_{test_type}_MP"',
         BypassPort = test_parms["Bypass"],
         MultiPassMasks = Spec(f'FUN_CORE_{sku}_Specs.MultiPass_2CDIE_4Pass'),
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         TestMode = "Scoreboard",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
         ForwardingMode = "Input",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
         #InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM0M1'),
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         #LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = "NoRecovery",
         RecoveryOptions = "",
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = "",
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfigS52C')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.CR_C5+")*60)),9)))"'),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_vmaxflowf5MP

####################################################################################

####################################################################################

def get_test_vmaxf5M0M1(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list_vmaxflowf5M0M1 = []
  
   for test_type, test_parms in content_list.items():
      test_list_vmaxflowf5M0M1.append(NativeMultiTrial(name=f'SBFT_CORE_VMAX_K_{subflow}_X_CR_{FlowMatrix}_{test_type}_M0M1',
		
		 exitaction="Continue",
		 trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
		 _comment='SpeedFlow F5_F7 VminTC test with MTT',
		 template=VminTC(name=f'"SBFT_CORE_VMAX_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + f' + "_X_{test_type}_M0M1"',
         BypassPort = test_parms["Bypass"],
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         TestMode = "Scoreboard",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
         ForwardingMode = "Input",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
         InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM0M1'),
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         #LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = "NoRecovery",
         RecoveryOptions = "",
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = "",
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_vmaxflowf5M0M1

####################################################################################

####################################################################################

def get_test_vmaxf5M2M3(flow, corner, FlowMatrix, corner_id, subflow, hptp, content_list):
     
   test_list_vmaxflowf5M2M3 = []
  
   for test_type, test_parms in content_list.items():
      test_list_vmaxflowf5M2M3.append(NativeMultiTrial(name=f'SBFT_CORE_VMAX_K_{subflow}_X_CR_{FlowMatrix}_{test_type}_M2M3',
		
		 exitaction="Continue",
		 trialvar = "CPU_TRIALS::FlowDomain.CORE_TOP",
		 _comment='SpeedFlow F5_F7 VminTC test with MTT',
		 template=VminTC(name=f'"SBFT_CORE_VMAX_K_{subflow}_X_CR_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + f' + "_X_{test_type}_M2M3"',
         BypassPort = test_parms["Bypass"],
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard",
         FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
         TestMode = "Scoreboard",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
         ForwardingMode = "Input",
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
         InitialMaskBits = Spec(f'FUN_CORE_{sku}_Specs.InitialMaskEnM2M3'),
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE"),
         #LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_NONMISR')),
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = "NoRecovery",
         RecoveryOptions = "",
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         RecoveryTrackingOutgoing = "",
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv')),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         SetPointsPreInstance = test_parms.get("SetPointsPreInstance", TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"')),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=AUTO),
                        r1 = pPass(setbin=AUTO),
                        r2 = pFail(setbin=AUTO),
                        r3 = pFail(setbin=AUTO),
                        r4 = pFail(setbin=PORT4),
                        r5 = pFail(setbin=PORT5))))
  
   return test_list_vmaxflowf5M2M3

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
         ExecutionMode = "Search" if "SCR" in flow else "Search",
         TestMode = "Functional",
         ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
         FeatureSwitchSettings = Spec(f'FUN_CORE_{sku}_Specs.FeatureSwitchSettings_CTV'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
         Patlist = test_parms.get("Patlist", 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master"),
         #BaseNumbers = None if "SCR" in flow else AUTO,
         CornerIdentifiers = f"CR7@{corner},CR6@{corner},CR5@{corner},CR4@{corner},CR3@{corner},CR2@{corner},CR1@{corner},CR0@{corner}",
         EndVoltageLimits = test_parms.get("EndVoltageLimits", Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         LimitGuardband = "" if test_parms["IS_EDC"] else Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
         PinMap = test_parms.get("PinMap", Spec(f'FUN_CORE_{sku}_Specs.PinMap_FREQ_MISR')),
         CtvPins = "IPC::CPU_TDO,IPC::CPU1_TDO",
         PatternNameCounterIndexes = Spec(f'FUN_CORE_{sku}_Specs.PatNameIndex'),
         RecoveryMode = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryMode_NoRec'),
         #RecoveryOptions = Spec(f'FUN_CORE_{sku}_Specs.CORE_RecoveryOptions_MTT'),
         RecoveryTrackingIncoming = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         #RecoveryTrackingOutgoing = Spec(f'FUN_CORE_{sku}_Specs.CDIE1_CDIE0_Recovery_Tracking'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'FUN_CORE_{sku}_Specs.VoltageTarget2C'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec(f'FUN_CORE_{sku}_Specs.FailCaptureCount'),
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = test_parms.get("DtsConfiguration", ""),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailS52C' + f' + DROPOUT.CR_{corner}')),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance= test_parms.get("PreInstance", ""),
         SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz"'),
         SetPointsPostInstance = test_parms.get("SetPointsPostInstance", Spec(f'PSPOST.CR_{corner}')),
                        ), # Close the braces for the MTT Template
         r0=pFail(setbin=AUTO, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r3=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r4=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         r5=pFail(setbin=AUTO, ret=0, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r1 = pPass(setbin=AUTO, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",AUTO)),
                        r3 = pFail(setbin=test_parms.get("Binning",AUTO)),
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
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/FUN_CORE_Generic.PatConfigSetpoints.json"'),
               SetPoint = 'FUSE_OVERRIDES_ALL',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_init

######################################################################
# PrimePatConfigTestMethod RAGN
######################################################################
def get_init_ragn(subflow, hptp, content_list):
     
   test_list_init_ragn = []
  
   for test_type, test_parms in content_list.items():
        test_list_init_ragn.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_RAGN_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/RAGN.PatConfigSetpoints.json"'),
               SetPoint = 'RAGN_PATMOD',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_init_ragn

######################################################################
# PrimePatConfigTestMethod Debug Counters
######################################################################
def get_init_debugcounter_list(subflow, hptp, content_list):
     
   test_list_debugcounter = []
  
   for test_type, test_parms in content_list.items():
        test_list_debugcounter.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_DEBUG_COUNTER_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/Debug_Counter.PatConfigSetPoints.json"'),
               SetPoint = test_parms.get("SetPoint", f'DBGCNTR_{test_type}'),
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_debugcounter

######################################################################
# PrimePatConfigTestMethod Wait Time
######################################################################
def get_init_waittime_list(subflow, hptp, content_list):
     
   test_list_waittime = []
  
   for test_type, test_parms in content_list.items():
        test_list_waittime.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_WAIT_TIME_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/Wait_Time.PatConfigSetPoint.json"'),
               #SetPoint = test_parms.get ("SetPoint", f'{test_type}_Wait_Times_10X'),
               SetPoint = test_parms.get ("SetPoint", f'{test_type}_Wait_Times_MM'),
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_waittime

######################################################################
# PrimePatConfigTestMethod SLC MASK
######################################################################
def get_init_slcmask(subflow, hptp, content_list):
     
   test_list_slcmask = []
  
   for test_type, test_parms in content_list.items():
        test_list_slcmask.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_X_{test_type}_CORE1MASK",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/FUN_CORE_SLC_mask.PatConfigSetPoints.json"'),
               SetPoint = 'SLC_CORE1_MASK',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_slcmask

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
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_nonmisr_pinmap_init

######################################################################
# PinMap APEX INIT RunCallback
######################################################################
def get_init_nonmisr_pinmap_apex_list(content_list):
     
   test_list_nonmisr_pinmap_apex_init = []
  
   for nonmisr_test, test_parms in content_list.items():
        test_list_nonmisr_pinmap_apex_init.append(RunCallback(name=f"SBFT_CORE_UF_K_INIT_X_X_X_X_VMIN_PINMAP_{nonmisr_test}_APEX",
               Parameters = f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_CORE_{sku}/InputFiles/DieRecoveryPinMaps_FREQ_FUN_CORE_APEX.json',
               Callback = 'LoadPinmapFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_nonmisr_pinmap_apex_init

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
               r0=pFail(setbin = 4400, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_misr_pinmap_init

######################################################################
# ApexTC INIT RunCallback
######################################################################
def get_init_apextc_list(content_list):
     
   test_list_apextc_init = []
  
   for test_type, test_parms in content_list.items():
        test_list_apextc_init.append(RunCallback(name=f"SBFT_CORE_RUNCALLBACK_K_INIT_X_X_X_X_{test_type}",
               Parameters = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/ApexTC_Input_Config.json"'),
               Callback = 'ReadFrequencyPatConfigFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4400, ret=0),
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
               r0=pFail(setbin = 4400, ret=0),
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
                Patlist = test_parms.get("Patlist", f"IPC::fun_cdie_fminxcr_{test_type.lower()}_hptp800_list_master"),
                PrintFormat = "ECADS",
                SetPointsPlistParamName = "Patlist",
                PreInstance = Spec(f'FUN_CORE_{sku}_Specs.PreInstanceShmoo'),
                SetPointsPreInstance = Spec(f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz,MCdrv:R1_SET"'),
                TimingsTc = "FUN_CORE_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_fun_core",
                VoltageConverter = test_parms.get("VoltageConverter", "--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE"),
                XAxisParam = "p_all_mts",
                XAxisRange = "750e6:10e6:12",
                XAxisType = "SpecSetVariable",
                XAxisParamType = "UserDefined",
                YAxisParam = "CORE31,CORE21,CORE11,CORE01,CORE3,CORE2,CORE1,CORE0",
                YAxisRange = "1:-0.05:12" if corner in ["F1", "F2", "F3"] else "1.15:-0.05:12",
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
# PrimePatConfigTestMethod DRG VVAR
######################################################################
def get_init_drg_vvar_list(subflow, hptp, content_list):
     
   test_list_vvar = []
  
   for test_type, test_parms in content_list.items():
        test_list_vvar.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_DRG_VVAR_{test_type}",
               Plist = 'IPC::'f"fun_cdie_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master",
               ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/DRG_VVAR.PatConfigSetPoints.json"'),
               SetPoint = test_parms.get("SetPoint", f'VVAR_{test_type}'),
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = 4444, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_vvar

################# START MTPL FLOW DEFINITON #####################
  
product_skus = ["CXPKGS9"]
 
for sku in product_skus:                                                    # <<<<<<<< This one
    mtplname = f"{product}_{sku}"
    # Initialize the module by defining the output mtpl path and the module name
    InitializeNVLClass(f'{mtplname}', f'{mtplname}', binrange = (44002000, 44502999), mttbinstrategy = NVLClass8dig, basenumrange = (11101, 11300), defaultthermalbin = (97442000, 97442999), defaultresetbin = (44192000, 44192999), defaultrm2bin=(99442000, 99442999), defaultrm1bin=(98442000,98442999))

    #################################################################
    #         
    #                       INIT SUBFLOW                      
    #
    #################################################################
    INIT_SUBFLOW = "F1XCR"
    INIT_CORNER = "F1"
    # Input
    if sku == "CXPKGS9":
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
        "APEXTC" :   {"Bypass" : -1, "IS_EDC" : False}
        }

        DebugCounter_Init_List = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False, "SetPoint" : f'DBGCNTR_SLC_DRG'},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False}
        }

        WaiTTime_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False}, #"SetPoint" : "MLC_LS_WTO_FINAL"},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False}
        }

        NonMisr_Pinmap_Content = {
       "NONMISR" : {"Bypass" : -1, "IS_EDC" : False}
        }

        Misr_Pinmap_Content = {
       "MISR" : {"Bypass" : -1, "IS_EDC" : False}
        }

        DEDC_Content = {
       "DEDC" : {"Bypass" : -1, "IS_EDC" : False}
        }

        SLCMASK_Content = {
       "SLC" : {"Bypass" : 1, "IS_EDC" : False}
        }

        INIT_RAGN_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : False},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : False},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : False},
       "SLC" : {"Bypass" : 1, "IS_EDC" : False},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : False}
        }

        DRG_VVAR_list = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False}
        }
    else:
        {
            }

    NONMISRPINMAP_INIT_Tests = get_init_nonmisr_pinmap_list(NonMisr_Pinmap_Content)

    APEX_NONMISRPINMAP_INIT_Tests = get_init_nonmisr_pinmap_apex_list(NonMisr_Pinmap_Content)

    MISRPINMAP_INIT_Tests = get_init_misr_pinmap_list(Misr_Pinmap_Content)
    
    PINMAP_COMP = Flow ("FUN_CORE_CXPKGS9_INIT_PINMAP", NONMISRPINMAP_INIT_Tests, MISRPINMAP_INIT_Tests, APEX_NONMISRPINMAP_INIT_Tests)

    INIT_FUSE_Tests = get_init_fuse_list(INIT_SUBFLOW, HPTP, INIT_content_list)
    INIT_TEST_COMP = Flow("FUN_CORE_CXPKGS9_INIT_FUSE_PATMOD", INIT_FUSE_Tests)

    INIT_DC_Tests = get_init_debugcounter_list(INIT_SUBFLOW, HPTP, DebugCounter_Init_List)
    INIT_DC_COMP = Flow("FUN_CORE_CXPKGS9_INIT_DEBUG_COUNTER", INIT_DC_Tests)

    INIT_WT_Tests = get_init_waittime_list(INIT_SUBFLOW, HPTP, WaiTTime_content_list)
    INIT_WT_COMP = Flow("FUN_CORE_CXPKGS9_INIT_WAIT_TIME", INIT_WT_Tests)

    APEXTC_INIT_Tests = get_init_apextc_list(ApexcTC_content_list)

    DEDC_INIT = get_init_dedc_list(DEDC_Content)

    SLCMASK_INIT = get_init_slcmask(INIT_SUBFLOW, HPTP,SLCMASK_Content)

    INIT_RAGN_Tests = get_init_ragn(INIT_SUBFLOW, HPTP, INIT_RAGN_content_list)
    INIT_RAGN_COMP = Flow("FUN_CORE_CXPKGS9_INIT_RAGN_PATMOD", INIT_RAGN_Tests)
 
    INIT_VVAR_Tests = get_init_drg_vvar_list(INIT_SUBFLOW, HPTP, DRG_VVAR_list)
    INIT_VVAR_COMP = Flow("FUN_CORE_CXPKGS9_INIT_DRG_VVAR", INIT_VVAR_Tests)
 
    INIT_Subflow = Flow(f"FUN_CORE_{sku}_INIT",
                        Fitem ('SAME', PINMAP_COMP, r0=pFail(ret=0 ), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_TEST_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_DC_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_WT_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_RAGN_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_VVAR_COMP, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                        SLCMASK_INIT,APEXTC_INIT_Tests, DEDC_INIT)
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
    APEX_FlowMatrix = "CR_F1_FREQ"
  
    # Input
    if sku == "CXPKGS9":

        XCRF5_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF5_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF5_Corner}')},
       }

        ApexTC_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True}
        }
        ApexTCMLC1100_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : True, "Binning" : 4450}
        }
        ApexTCMLC0011_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : True, "Binning" : 4450}
        }

        ApexTCMLCLS1100_content_list = {
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : True, "Binning" : 4450}
        }
        ApexTCMLCLS0011_content_list = {
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : True, "Binning" : 4450}
        }

        ApexTCMLCDRG1100_content_list = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : True, "Binning" : 4450}
        }
        ApexTCMLCDRG0011_content_list = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : True, "Binning" : 4450}
        }

        ApexTCSLC1100R1_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                "Binning" : 4450}
        }
        ApexTCSLC1100R2_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                "Binning" : 4450}
        }
        ApexTCSLC0011R1_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                "Binning" : 4450},
        }
        ApexTCSLC0011R2_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                "Binning" : 4450},
        }

        ApexTCSLCDRG1100R1_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                    "Binning" : 4450}
        }
        ApexTCSLCDRG1100R2_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                    "Binning" : 4450}
        }
        ApexTCSLCDRG0011R1_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                    "Binning" : 4450}
        }
        ApexTCSLCDRG0011R2_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_fmax_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{APEX_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5'),
                    "Binning" : 4450}
        }
        XCRF5M0M1_MLC_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }
        XCRF5M2M3_MLC_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }

        XCRF5M0M1_MLC_LS_content_list = {
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }
        XCRF5M2M3_MLC_LS_content_list = {
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }

        XCRF5M0M1_MLC_DRG_content_list = {
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,}
       }

        XCRF5M2M3_MLC_DRG_content_list = {
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,}
       }

        XCRF5M0M1_SLC_content_list = {
       "SLC" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF5_Corner}')}
       }
        XCRF5M2M3_SLC_content_list = {
      "SLC" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF5_Corner}')}
       }
        XCRF5M0M1_SLC_DRG_content_list = {
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF5_Corner}')}
        }
        XCRF5M2M3_SLC_DRG_content_list = {
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : False, "Binning" : 4450,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF5_SubFlow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF5_Corner}')}
        }
    else:
        {
            }
    
    XCRF5_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5_content_list)

    R1APEXMLC_1100_Tests = get_test_apextc_1100R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLC1100_content_list)
    R1APEXMLC_0011_Tests = get_test_apextc_0011R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLC0011_content_list)
    R1FMAX_MLC = Flow("FMAX_MLC_R1", R1APEXMLC_1100_Tests, R1APEXMLC_0011_Tests)

    R1APEXMLCLS_1100_Tests = get_test_apextc_1100R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCLS1100_content_list)
    R1APEXMLCLS_0011_Tests = get_test_apextc_0011R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCLS0011_content_list)
    R1FMAX_MLCLS = Flow("FMAX_MLCLS_R1", R1APEXMLCLS_1100_Tests, R1APEXMLCLS_0011_Tests)

    R1APEXMLCDRG_1100_Tests = get_test_apextc_1100R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCDRG1100_content_list)
    R1APEXMLCDRG_0011_Tests = get_test_apextc_0011R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCDRG0011_content_list)
    R1FMAX_MLCDRG = Flow("FMAX_MLCDRG_R1", R1APEXMLCDRG_1100_Tests, R1APEXMLCDRG_0011_Tests)

    R1APEXSLC_1100_Tests = get_test_apextc_1100R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLC1100R1_content_list)
    R1APEXSLC_0011_Tests = get_test_apextc_0011R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLC0011R1_content_list)
    R1FMAX_SLC = Flow("FMAX_SLC_R1", R1APEXSLC_1100_Tests, R1APEXSLC_0011_Tests)

    R1APEXSLCDRG_1100_Tests = get_test_apextc_1100R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLCDRG1100R1_content_list)
    R1APEXSLCDRG_0011_Tests = get_test_apextc_0011R1(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLCDRG0011R1_content_list)
    R1FMAX_SLCDRG = Flow("FMAX_SLCDRG_R1", R1APEXSLCDRG_1100_Tests, R1APEXSLCDRG_0011_Tests)

    R2APEXMLC_1100_Tests = get_test_apextc_1100R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLC1100_content_list)
    R2APEXMLC_0011_Tests = get_test_apextc_0011R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLC0011_content_list)
    R2FMAX_MLC = Flow("FMAX_MLC_R2", R2APEXMLC_1100_Tests, R2APEXMLC_0011_Tests)

    R2APEXMLCLS_1100_Tests = get_test_apextc_1100R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCLS1100_content_list)
    R2APEXMLCLS_0011_Tests = get_test_apextc_0011R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCLS0011_content_list)
    R2FMAX_MLCLS = Flow("FMAX_MLCLS_R2", R2APEXMLCLS_1100_Tests, R2APEXMLCLS_0011_Tests)

    R2APEXMLCDRG_1100_Tests = get_test_apextc_1100R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCDRG1100_content_list)
    R2APEXMLCDRG_0011_Tests = get_test_apextc_0011R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCMLCDRG0011_content_list)
    R2FMAX_MLCDRG = Flow("FMAX_MLCDRG_R2", R2APEXMLCDRG_1100_Tests, R2APEXMLCDRG_0011_Tests)

    R2APEXSLC_1100_Tests = get_test_apextc_1100R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLC1100R2_content_list)
    R2APEXSLC_0011_Tests = get_test_apextc_0011R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLC0011R2_content_list)
    R2FMAX_SLC = Flow("FMAX_SLC_R2", R2APEXSLC_1100_Tests, R2APEXSLC_0011_Tests)

    R2APEXSLCDRG_1100_Tests = get_test_apextc_1100R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLCDRG1100R2_content_list)
    R2APEXSLCDRG_0011_Tests = get_test_apextc_0011R2(APEX_Corner, APEX_FlowMatrix, XCRF5_SubFlow, HPTP, ApexTCSLCDRG0011R2_content_list)
    R2FMAX_SLCDRG = Flow("FMAX_SLCDRG_R2", R2APEXSLCDRG_1100_Tests, R2APEXSLCDRG_0011_Tests)

    APEX_COMP = Flow("FUN_CORE_CXPKGS9_FMAX",
                     Fitem ('SAME', R1FMAX_MLC, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R2FMAX_MLC, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R1FMAX_MLCLS, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R2FMAX_MLCLS, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R1FMAX_MLCDRG, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R2FMAX_MLCDRG, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R1FMAX_SLC, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R2FMAX_SLC, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R1FMAX_SLCDRG, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")),
                     Fitem ('SAME', R2FMAX_SLCDRG, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")))

    XCRF5M0M1_MLC_Tests = get_test_listM0M1(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M0M1_MLC_content_list)
    XCRF5M2M3_MLC_Tests = get_test_listM2M3(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M2M3_MLC_content_list)
    #F5XCRMLC = Flow("F5XCR_SBFT_MLC", XCRF5M0M1_MLC_Tests, XCRF5M2M3_MLC_Tests)

    XCRF5M0M1_MLCLS_Tests = get_test_listM0M1(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M0M1_MLC_LS_content_list)
    XCRF5M2M3_MLCLS_Tests = get_test_listM2M3(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M2M3_MLC_LS_content_list)
    #F5XCRMLCLS = Flow("F5XCR_SBFT_MLCLS", XCRF5M0M1_MLCLS_Tests, XCRF5M2M3_MLCLS_Tests)

    XCRF5M0M1_MLCDRG_Tests = get_test_listM0M1(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M0M1_MLC_DRG_content_list)
    XCRF5M2M3_MLCDRG_Tests = get_test_listM2M3(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M2M3_MLC_DRG_content_list)
    #F5XCRMLCDRG = Flow("F5XCR_SBFT_MLCDRG", XCRF5M0M1_MLCDRG_Tests, XCRF5M2M3_MLCDRG_Tests)

    XCRF5M0M1_SLC_Tests = get_test_listM0M1(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M0M1_SLC_content_list)
    XCRF5M2M3_SLC_Tests = get_test_listM2M3(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M2M3_SLC_content_list)
    #F5XCRSLC = Flow("F5XCR_SBFT_SLC", XCRF5M0M1_SLC_Tests, XCRF5M2M3_SLC_Tests)

    XCRF5M0M1_SLCDRG_Tests = get_test_listM0M1(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M0M1_SLC_DRG_content_list)
    XCRF5M2M3_SLCDRG_Tests = get_test_listM2M3(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5M2M3_SLC_DRG_content_list)
    #F5XCRSLCDRG = Flow("F5XCR_SBFT_SLCDRG", XCRF5M0M1_SLCDRG_Tests, XCRF5M2M3_SLCDRG_Tests)
  
    #XCRF5_Subflow = Flow(f"FUN_CORE_{sku}_F5XCR", 
                         #Fitem ('SAME', APEX_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                         #XCRF5_Tests,
                         #Fitem ('SAME', F5XCRMLC, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F5XCRMLCLS, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F5XCRMLCDRG, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F5XCRSLC, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F5XCRSLCDRG, r0=pFail(ret=0),r1=pPass(goto="NEXT")))

    XCRF5_Subflow = Flow(f"FUN_CORE_{sku}_F5XCR",
                         Fitem ('SAME', APEX_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                         XCRF5_Tests)
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
    if sku == "CXPKGS9":

        XCRLOF5_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True, "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF5_SubFlow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRLOF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRLOF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRLOF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRLOF5_Corner}')},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF5_SubFlow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{XCRLOF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{XCRLOF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{XCRLOF5_CornerID}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF5_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRLOF5_Corner}')},
       }
    else:
        {
            }
    
    XCRLOF5_Tests = get_test_list(XCRLOF5_Flow, XCRLOF5_Corner, XCRLOF5_FlowMatrix, XCRLOF5_CornerID, XCRLOF5_SubFlow, HPTP, XCRLOF5_content_list)

  
    XCRLOF5_Subflow = Flow(f"FUN_CORE_{sku}_F5XCRLO", XCRLOF5_Tests)

    #################################################################
    #         
    #                       XCRF1 SUBFLOW                      
    #
    #################################################################
    XCRF1_Flow = "XCRF1"
    XCRF1_Corner = "F1"                        
    XCRF1_FlowMatrix = "CR_F1_FREQ"
    XCRF1_Subflow = "F1XCR"
    XCRF1_CornerID = "C1"
  
    # Input
    if sku == "CXPKGS9":
        XCRF1_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                "EndVoltageLimits" : Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL")},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                    "EndVoltageLimits" : Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL")},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                   "EndVoltageLimits" : Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL")},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "EndVoltageLimits" : Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF1_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF1_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF1_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF1_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF1_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF1_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "EndVoltageLimits" : Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL"),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF1_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF1_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF1_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF1_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF1_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF1_Corner}')},
       }
        XCRF1_misr_list = {
       "MLC_LS_MISR" : {"Bypass" : 1, "IS_EDC" : True, 
                        "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                        "Binning" : 4450},
        }
    else:
        {
            }
    
    XCRF1_Tests = get_test_list_f1_f4(XCRF1_Flow, XCRF1_Corner, XCRF1_CornerID, XCRF1_FlowMatrix, XCRF1_Subflow, HPTP, XCRF1_content_list)
    
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
    if sku == "CXPKGS9":
        XCRF2_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F2_FREQ+")*60)),9)))"')},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F2_FREQ+")*60)),9)))"')},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F2_FREQ+")*60)),9)))"')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF2_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F2_FREQ+")*60)),9)))"'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF2_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF2_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF2_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF2_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF2_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF2_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F2_FREQ+")*60)),9)))"'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF2_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF2_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF2_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF2_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF2_Corner}')},
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
    if sku == "CXPKGS9":
        XCRF3_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F3_FREQ+")*60)),9)))"')
                },
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F3_FREQ+")*60)),9)))"')
                    },
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F3_FREQ+")*60)),9)))"')
                   },
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF3_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F3_FREQ+")*60)),9)))"'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF3_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF3_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF3_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF3_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF3_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF3_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F3_FREQ+")*60)),9)))"'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF3_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF3_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF3_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF3_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF3_Corner}')},
        }
        XCRF3_misr_list = {
       "MLC_LS_MISR" : {"Bypass" : 1, "IS_EDC" : True,
                        "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F3_FREQ+")*60)),9)))"'),
                        "Binning" : 4450},
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
    if sku == "CXPKGS9":
        XCRF4_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv'),
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F4_FREQ+")*60)),9)))"')},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv'),
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F4_FREQ+")*60)),9)))"')},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv'),
                   "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F4_FREQ+")*60)),9)))"')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv'),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF4_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F4_FREQ+")*60)),9)))"'),
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF4_Corner}')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF4_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F4_FREQ+")*60)),9)))"'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF4_Corner}')},
        }

        XCRF4_MLC_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : False,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }
        XCRF4_MLC_LS_content_list = {
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : False,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }
        XCRF4_MLC_DRG_content_list = {
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : False,
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv')},
      }
        XCRF4_SLC_content_list = {
       "SLC" : {"Bypass" : 1, "IS_EDC" : False,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRF4_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF4_Corner}')},
       }
        XCRF4_SLC_DRG_content_list = {
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : False,
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv'),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRF4_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRF4_Corner}')},
        }
    else:
        {
            }
    
    XCRF4_Tests = get_test_list_f1_f4(XCRF4_Flow, XCRF4_Corner, XCRF4_CornerID, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_content_list)

    XCRF4M0M1_MLC_Tests = get_test_list_f4M0M1(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_MLC_content_list)
    XCRF4M2M3_MLC_Tests = get_test_list_f4M2M3(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_MLC_content_list)
    #F4XCRMLC = Flow("F4XCR_SBFT_MLC", XCRF4M0M1_MLC_Tests, XCRF4M2M3_MLC_Tests)

    XCRF4M0M1_MLC_LS_Tests = get_test_list_f4M0M1(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_MLC_LS_content_list)
    XCRF4M2M3_MLC_LS_Tests = get_test_list_f4M2M3(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_MLC_LS_content_list)
    #F4XCRMLCLS = Flow("F4XCR_SBFT_MLCLS", XCRF4M0M1_MLC_LS_Tests, XCRF4M2M3_MLC_LS_Tests)

    XCRF4M0M1_MLC_DRG_Tests = get_test_list_f4M0M1(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_MLC_DRG_content_list)
    XCRF4M2M3_MLC_DRG_Tests = get_test_list_f4M2M3(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_MLC_DRG_content_list)
    #F4XCRMLCDRG = Flow("F4XCR_SBFT_MLCDRG", XCRF4M0M1_MLC_DRG_Tests, XCRF4M2M3_MLC_DRG_Tests)

    XCRF4M0M1_SLC_Tests = get_test_list_f4M0M1(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_SLC_content_list)
    XCRF4M2M3_SLC_Tests = get_test_list_f4M2M3(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_SLC_content_list)
    #F4XCRSLC = Flow("F4XCR_SBFT_SLC", XCRF4M0M1_SLC_Tests, XCRF4M2M3_SLC_Tests)

    XCRF4M0M1_SLC_DRG_Tests = get_test_list_f4M0M1(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_SLC_DRG_content_list)
    XCRF4M2M3_SLC_DRG_Tests = get_test_list_f4M2M3(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, HPTP, XCRF4_SLC_DRG_content_list)
    #F4XCRSLCDRG = Flow("F4XCR_SBFT_SLCDRG", XCRF4M0M1_SLC_DRG_Tests, XCRF4M2M3_SLC_DRG_Tests)
  
    XCRF4_Subflow = Flow(f"FUN_CORE_{sku}_F4XCR",
                         XCRF4_Tests
                         #Fitem ('SAME', F4XCRMLC, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F4XCRMLCLS, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F4XCRMLCDRG, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F4XCRSLC, r0=pFail(ret=0),r1=pPass(goto="NEXT")),
                         #Fitem ('SAME', F4XCRSLCDRG, r0=pFail(ret=0),r1=pPass(goto="NEXT"))
                         )

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
    if sku == "CXPKGS9":
        XCRLOF4_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv')},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv'),
                    "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF4_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRLOF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRLOF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRLOF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRLOF4_Corner}')},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_noctv'),
                "Patlist" : 'IPC::'f"fun_cdie_{XCRLOF4_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{XCRLOF4_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{XCRLOF4_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{XCRLOF4_Corner}_FREQ")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{XCRLOF4_Corner}+''",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'), 
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{XCRLOF4_Corner}')},
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
    if sku == "CXPKGS9":

        FMIN_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'), 
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{FMIN_Corner}')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{FMIN_Corner}')}
        }
        FMIN_MLC_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : False},
       }
        FMIN_MLCLS_content_list = {
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : False},
       }
        FMIN_MLCDRG_content_list = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : False},
       }
        FMIN_SLC_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : False,
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'), 
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{FMIN_Corner}')},
       }

        FMIN_SLCDRG_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : False,
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{FMIN_Corner}')}
        }

        FMIN_MLC_FAIL_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : True},
       }
        FMIN_MLCLS_FAIL_content_list = {
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : True},
       }
        FMIN_MLCDRG_FAIL_content_list = {
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : True},
       }
        FMIN_SLC_FAIL_content_list = {
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'), 
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{FMIN_Corner}')},
       }

        FMIN_SLCDRG_FAIL_content_list = {
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_{FMIN_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FMIN_FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{FMIN_Corner}")+f'+"GHz,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff,"+'+Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_MASK_CR')),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_{FMIN_Corner}+' f'","+' +Spec(f'FUN_CORE_{sku}_Specs.MCfun_FMIN_UNMASK_CR')+'+",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f' + ' +Spec(f'FUN_CORE_{sku}_Specs.VoltageConverter_NBLRailCCFS52C') + f' + DROPOUT.CR_{FMIN_Corner}')}
        }

        SHMOO_content_list = {
       "DEDC" : {"Bypass" : 1, "IS_EDC" : True, "Patlist" : f"IPC::fun_cdie_fminxcr_mlc_hptp800_list_master"},
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True, 
                "VoltageConverter" : "--overrides CCF1:1.1,CCF:1.1 --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list_master",},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True, 
                     "VoltageConverter" : "--overrides CCF1:1.1,CCF:1.1 --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                     "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",},
        }

        SHMOO_content_list_f2_f5 = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True, 
                "VoltageConverter" : "--overrides CCF1:1.1,CCF:1.1 --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_hptp800_burstoff_list_master",},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True, 
                    "VoltageConverter" : "--overrides CCF1:1.1,CCF:1.1 --dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE",
                    "Patlist" : 'IPC::'f"fun_cdie_{FMIN_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",},
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

    SHMOO_COMPF1 = Flow("FUN_CORE_CXPKGS9_SHMOO_F1", SHMOO_TestsF1)
    SHMOO_COMPF2 = Flow("FUN_CORE_CXPKGS9_SHMOO_F2", SHMOO_TestsF2)
    SHMOO_COMPF3 = Flow("FUN_CORE_CXPKGS9_SHMOO_F3", SHMOO_TestsF3)
    SHMOO_COMPF4 = Flow("FUN_CORE_CXPKGS9_SHMOO_F4", SHMOO_TestsF4)
    SHMOO_COMPF5 = Flow("FUN_CORE_CXPKGS9_SHMOO_F5", SHMOO_TestsF5)
    SHMOO_COMPF6 = Flow("FUN_CORE_CXPKGS9_SHMOO_F6", SHMOO_TestsF6)
    SHMOO_COMPF7 = Flow("FUN_CORE_CXPKGS9_SHMOO_F7", SHMOO_TestsF7)

    SHMOO_TEST = Flow("FUN_CORE_CXPKGS9_SHMOO",
                      Fitem ('SAME', SHMOO_COMPF1, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF2, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF3, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF4, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF5, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF6, r0=pFail(ret=1), r1=pPass(goto="NEXT")),
                      Fitem ('SAME', SHMOO_COMPF7, r0=pFail(ret=1), r1=pPass(goto="NEXT")))

    FMIN_MLC_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_MLC_content_list)
    #FMINFAIL_MLC_Tests = get_test_list_fminfailflow(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_FREQ, FMIN_MLC_FAIL_content_list)
    #FMIN_MLC = Flow("FMIN_SBFT_MLC", FMIN_MLC_Tests)#, FMINFAIL_MLC_Tests)

    FMIN_MLCLS_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_MLCLS_content_list)
    #FMINFAIL_MLCLS_Tests = get_test_list_fminfailflow(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_FREQ, FMIN_MLCLS_FAIL_content_list)
    #FMIN_MLCLS = Flow("FMIN_SBFT_MLCLS", FMIN_MLCLS_Tests)#, FMINFAIL_MLCLS_Tests)

    FMIN_MLCDRG_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_MLCDRG_content_list)
    #FMINFAIL_MLCDRG_Tests = get_test_list_fminfailflow(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_FREQ, FMIN_MLCDRG_FAIL_content_list)
    #FMIN_MLCDRG = Flow("FMIN_SBFT_MLCDRG", FMIN_MLCDRG_Tests)#, FMINFAIL_MLCDRG_Tests)

    FMIN_SLC_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_SLC_content_list)
    #FMINFAIL_SLC_Tests = get_test_list_fminfailflow(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_FREQ, FMIN_SLC_FAIL_content_list)
    #FMIN_SLC = Flow("FMIN_SBFT_SLC", FMIN_SLC_Tests)#, FMINFAIL_SLC_Tests)

    FMIN_SLCDRG_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_SLCDRG_content_list)
    #FMINFAIL_SLCDRG_Tests = get_test_list_fminfailflow(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, HPTP, FMIN_FREQ, FMIN_SLCDRG_FAIL_content_list)
    #FMIN_SLCDRG = Flow("FMIN_SBFT_SLCDRG", FMIN_SLCDRG_Tests)#, FMINFAIL_SLCDRG_Tests)

    WTO_MLC_Tests = get_test_pattern_wto(WTO_MLC_content_list)

    FMIN_Subflow = Flow(f"FUN_CORE_{sku}_FMINXCR", FMIN_MLC_Tests, FMIN_MLCLS_Tests, FMIN_MLCDRG_Tests, FMIN_SLC_Tests, FMIN_SLCDRG_Tests,
                        #Fitem ("SAME", FMIN_MLC, r0=pFail(goto="NEXT"), r1 = pPass(goto="NEXT")),
                        #Fitem ("SAME", FMIN_MLCLS, r0=pFail(goto="NEXT"), r1 = pPass(goto="NEXT")),
                        #Fitem ("SAME", FMIN_MLCDRG, r0=pFail(goto="NEXT"), r1 = pPass(goto="NEXT")),
                        #Fitem ("SAME", FMIN_SLC, r0=pFail(goto="NEXT"), r1 = pPass(goto="NEXT")),
                        #Fitem ("SAME", FMIN_SLCDRG, r0=pFail(goto="NEXT"), r1 = pPass(goto="NEXT")),
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
  
    if sku == "CXPKGS9":
        VMAXF5_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : True},
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
        }
        VMAXF1_content_list = {
       "MLC" : {"Bypass" : -1, "IS_EDC" : True,
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "MLC_LS" : {"Bypass" : -1, "IS_EDC" : True,
                   "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "MLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "SLC" : {"Bypass" : -1, "IS_EDC" : True,
                "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
       "SLC_DRG" : {"Bypass" : -1, "IS_EDC" : True,
                    "PreInstance" : Spec(f'"EvaluateExpression(--result G.U.S.FUNCORE_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FlowMatrixSingular.CR_F1_FREQ+")*60)),9)))"'),
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F1+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F1+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F1')},
        }
        VMAXF5_MLC_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True,
                "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }
        VMAXF5_MLC_LS_content_list = {
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True,
                   "DtsConfiguration" : Spec(f'FUN_CORE_{sku}_Specs.dtsconfig_ctv')}
       }
        VMAXF5_MLC_DRG_content_list = {
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True}
       }
        VMAXF5_SLC_content_list = {
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
       }
        VMAXF5_SLC_DRG_content_list = {
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAX_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : TrialParamSpec(f'PSPRE.CR_{VMAXXCRF5_Corner}+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{VMAXXCRF5_CornerID}+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{VMAXXCRF5_CornerID}")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CORE31:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE21:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE11:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE01:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
        }
    else:
       {
           }

    #VMAXF5_Tests = get_test_vmax(VMAX_Flow, VMAX_Corner, VMAXF5_FlowMatrix, VMAX_Subflow, HPTP, VMAXF5_content_list, FREQF5)
    VMAXF5MP_Tests = get_test_vmaxf5MP(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_content_list)

    VMAXF1_Tests = get_test_vmax(VMAX_Flow, VMAX_Corner, VMAXF1_FlowMatrix, VMAX_Subflow, HPTP, VMAXF1_content_list, FREQF1)

    ##XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_SubFlow, HPTP, XCRF5_content_list

    VMAXF5M0M1_MLC_Tests = get_test_vmaxf5M0M1(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_MLC_content_list)
    VMAXF5M2M3_MLC_Tests = get_test_vmaxf5M2M3(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_MLC_content_list)

    VMAXF5M0M1_MLC_LS_Tests = get_test_vmaxf5M0M1(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_MLC_LS_content_list)
    VMAXF5M2M3_MLC_LS_Tests = get_test_vmaxf5M2M3(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_MLC_LS_content_list)

    VMAXF5M0M1_MLC_DRG_Tests = get_test_vmaxf5M0M1(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_MLC_DRG_content_list)
    VMAXF5M2M3_MLC_DRG_Tests = get_test_vmaxf5M2M3(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_MLC_DRG_content_list)

    VMAXF5M0M1_SLC_Tests = get_test_vmaxf5M0M1(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_SLC_content_list)
    VMAXF5M2M3_SLC_Tests = get_test_vmaxf5M2M3(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_SLC_content_list)

    VMAXF5M0M1_SLC_DRG_Tests = get_test_vmaxf5M0M1(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_SLC_DRG_content_list)
    VMAXF5M2M3_SLC_DRG_Tests = get_test_vmaxf5M2M3(VMAX_Flow, VMAXXCRF5_Corner, VMAXF5_FlowMatrix, VMAXXCRF5_CornerID, VMAX_Subflow, HPTP, VMAXF5_SLC_DRG_content_list)

    
    #VMAXF5_MLC_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F5_MLC", VMAXF5M0M1_MLC_Tests, VMAXF5M2M3_MLC_Tests)
    #VMAXF5_MLC_LS_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F5_MLC_LS", VMAXF5M0M1_MLC_LS_Tests, VMAXF5M2M3_MLC_LS_Tests)
    #VMAXF5_MLC_DRG_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F5_MLC_DRG", VMAXF5M0M1_MLC_DRG_Tests, VMAXF5M2M3_MLC_DRG_Tests)
    #VMAXF5_SLC_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F5_SLC", VMAXF5M0M1_SLC_Tests, VMAXF5M2M3_SLC_Tests)
    #VMAXF5_SLC_DRG_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F5_SLC_DRG", VMAXF5M0M1_SLC_DRG_Tests, VMAXF5M2M3_SLC_DRG_Tests)

    VMAXF5_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F5", VMAXF5MP_Tests)
    #VMAXF5_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F5",
                       #Fitem ('SAME', VMAXF5_MLC_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                          #Fitem ('SAME', VMAXF5_MLC_LS_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                            #Fitem ('SAME', VMAXF5_MLC_DRG_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                            #Fitem ('SAME', VMAXF5_SLC_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                            #Fitem ('SAME', VMAXF5_SLC_DRG_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")))

    VMAXF1_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCR_F1", VMAXF1_Tests)
  
    VMAX_Subflow = Flow(f"FUN_CORE_{sku}_VMAXXCR",
                        Fitem ('SAME', VMAXF1_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', VMAXF5_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")))

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
  
    if sku == "CXPKGS9":
        VMAXXCRLOF5_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAXXCRLO_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXXCRLOF5_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAXXCRLO_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXXCRLOF5_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')}
        }
        VMAXXCRLOF1_content_list = {
       "MLC" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_LS" : {"Bypass" : 1, "IS_EDC" : True},
       "MLC_DRG" : {"Bypass" : 1, "IS_EDC" : True},
       "SLC" : {"Bypass" : 1, "IS_EDC" : True,
                "Patlist" : 'IPC::'f"fun_cdie_{VMAXXCRLO_Subflow.lower()}_slc_hptp800_burstoff_list_master",
                "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXXCRLOF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')},
       "SLC_DRG" : {"Bypass" : 1, "IS_EDC" : True,
                    "Patlist" : 'IPC::'f"fun_cdie_{VMAXXCRLO_Subflow.lower()}_slc_drg_hptp800_burstoff_list_master",
                    "SetPointsPreInstance" : Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{VMAXXCRLOF1_FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'FUN_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F1_FREQ")+f'+"GHz,CORE:nblctrl_core_l2:nbloff,CORE:nblctrl1_core_l2:nbloff,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'),
                    "SetPointsPostInstance" : Spec(f'PSPOST.CR_F5+''",CORE:nblctrl_core_l2:nblon,CORE:nblctrl1_core_l2:nblon,CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'),
                    "VoltageConverter" : Spec(f'"--overrides CCF1:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+",CCF:"+' +Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")+ f'+" --dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')}
        }
    else:
       {
           }
    
    VMAXXCRLOF5_Tests = get_test_vmax(VMAXXCRLO_Flow, VMAXXCRLO_Corner, VMAXXCRLOF5_FlowMatrix, VMAXXCRLO_Subflow, HPTP, VMAXXCRLOF5_content_list, FREQF5)
    VMAXXCRLOF1_Tests = get_test_vmax(VMAXXCRLO_Flow, VMAXXCRLO_Corner, VMAXXCRLOF1_FlowMatrix, VMAXXCRLO_Subflow, HPTP, VMAXXCRLOF1_content_list, FREQF1)

    VMAXCRLOF5_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCRLO_F5", VMAXXCRLOF5_Tests)
    VMAXCRLOF1_COMP = Flow("FUN_CORE_CXPKGS9_VMAXXCRLO_F1", VMAXXCRLOF1_Tests)
  
    VMAXXCRLO_Subflow = Flow(f"FUN_CORE_{sku}_VMAXXCRLO",
                             Fitem ('SAME', VMAXCRLOF1_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                             Fitem ('SAME', VMAXCRLOF5_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")))

