# Import the necessary classes from Pymtpl
from ctypes import SetPointerType
from operator import ge
from tkinter import DISABLED
from pymtpl.por_methods import VminTC, PrimePatConfigTestMethod, RunCallback, ApexTC, DDGShmooTC, DedcLoadConfigTC  # type: ignore
from pymtpl.core import Flow, Fitem, pPass, pFail, NativeMultiTrial, AUTO, InitializeNVLClass, Import, TrialParamSpec, Spec # type: ignore
from pymtpl.binctr import NVLClass8dig # type: ignore

# Define the product name
product = "FUN_ATOM"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'
HPTP = "hptp800"

#################################################################################### APEXTC Params      
def get_test_apextc(flow, corner, FlowMatrix, subflow, hptp, content_list):
     
   test_list_apextcflow = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
      test_list_apextcflow.append(ApexTC(name=f'SBFT_ATOM_APEX_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}_APEX_FMAX',
               InitialMaskBits="",
               DtsConfiguration  = test_parms.get("DtsConfiguration",Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p')), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p)')),
               BypassPort= 1, #Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, -1, BYPASS_PARAMETER.APEXTC_BYPASS, 1)"),
               FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
               Targets= "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
               ForwardingMode="Input" if test_type == "L2_DRAGON" else "None",
               PinMap= "" if test_type in "SLC_DRAGON" else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.PinMap_NONMISR')),
               SetPointsPreInstance = "MCdrv:atomfreq_0:3.2GHz,MCdrv:ringfreq_0:3.1GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz" if test_type in "L2_DRAGON" else "MCdrv:atomfreq_0:3.2GHz,MCdrv:ringfreq_0:3.1GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff",
               #SetPointsPostInstance="MCdrv:R1_SET",
               #SetPointsPreInstance = Spec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.{FlowMatrix}+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))),
               StepSize= 3,
               LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
               TimingsTc="FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
               Patlist= 'IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_list" if test_type in "L2_DRAGON" else 'IPC::fun_cdie_atom_f5xatccf_slc_dragon_list_list',
               PatternNameCounterIndexes= "9,10,11,12,13,14,15",
               RecoveryOptions="",
               RecoveryTracking=(Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in "L2_DRAGON" else ""),
               End=Spec(f'__shared__::FlowMatrixSingular.APEX_ATOM_MIN') if test_type in "L2_DRAGON" else Spec(f'__shared__::FlowMatrixSingular.APEX_CCF_MIN'),
               Start=Spec(f'__shared__::FlowMatrixSingular.APEX_ATOM_MAX') if test_type == "L2_DRAGON" else Spec(f'__shared__::FlowMatrixSingular.APEX_CCF_MAX'),
               FivrCondition="NOM",
               FivrConditionPlistParamName="Patlist",
               VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --overrides ATOM1:1.2,ATOM0:1.2" if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUX CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1 --overrides ATOM1:1.2,ATOM0:1.2" ,
               ExportTokens= "" if test_type in "SLC_DRAGON" else "FXATC1,FXATC0",
               _fitem=Fitem('SAME', edc=test_parms["IS_EDC"],
                            r0=pFail(setbin=-44, goto="NEXT"),
                            r1=pPass(setbin=-44, goto="NEXT"),
                            r2=pFail(setbin=-44, goto="NEXT"),
                            r3=pFail(setbin=-44, goto="NEXT"),
                            r4=pFail(setbin=-44, goto="NEXT"),
                            r5=pFail(setbin=-44, goto="NEXT"))
            )
         )
  
   return test_list_apextcflow

#################################################################################### FMIN
def get_test_list_fmin(flow, corner, FlowMatrix, subflow, content_list):
     
   test_list_funflow = []
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
      test_list_funflow.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM",
         _comment='SpeedFlow F1_F4 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
         BypassPort = 1 if test_type in ["BILBO", "TRUNKDBG"] else test_parms ["Bypass"],
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         TestMode = "SingleVmin" if "SLC_DRAGON" in test_type else "MultiVmin",
         LimitGuardband = "" if (test_parms["IS_EDC"] or (test_type in ["BILBO", "TRUNKDBG"])) else (Spec(f'toString(__shared__::GBVars.FminLimitGuardband)')),         
         ForwardingMode = "None" if test_type in ["BILBO", "TRUNKDBG"] else "Input",
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "cpu_fun_timing_mts400_tstprtclk200_tck50_funatom" if "FMIN" in flow else  "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_list"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS", "SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_list"),         
         BaseNumbers =  -44,
         CornerIdentifiers = f"CCF0@F1" if test_type == "SLC_DRAGON" else f"AT1@F1,AT0@F1",
         VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
         VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL" if test_type == "SLC_DRAGON" else  "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1",
         PatternNameCounterIndexes = "9,10,11,12,13,14,15", 
         DtsConfiguration  = test_parms.get("DtsConfiguration",Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p')), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p)')),
         FivrCondition = "NOM",
         PinMap = "" if test_type in ["BILBO", "TRUNKDBG"] else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
         FivrConditionPlistParamName = "Patlist",
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else Spec(f"__shared__::Recovery_Single.F1F4_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         RecoveryMode = "NoRecovery",
         ScoreboardEdgeTicks= Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
         ExecutionMode = "SearchWithScoreboard",
         MaxFailsNum= Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits = (Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL")) if corner == "F1" else (Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "",
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance=f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_{corner}])*60)),10)))",
         SetPointsPreInstance = TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_FMIN+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_FMIN") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:pwrmux_sel_atom_l2_0:vnnaon,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"')))
            ),# Close the braces for the MTT Template         
         r0=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=2, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=-44, ret=3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r4=pFail(setbin=-44, ret=4, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=-44, ret=5, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r3 = (pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0)),
                        r4 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0),
                        r5 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0))))
  
   return test_list_funflow


#################################################################################### F1-F4 Params
def get_test_list_f1_f4(flow, corner, FlowMatrix, subflow, content_list):
     
   test_list_funflow = []
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
      test_list_funflow.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM",
         _comment='SpeedFlow F1_F4 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , "")'),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , "")'),
         TestMode = "SingleVmin" if "SLC_DRAGON" in test_type else "MultiVmin",
         LimitGuardband = "" if (test_parms["IS_EDC"] or (test_type in ["BILBO", "TRUNKDBG"])) else (Spec(f'toString(__shared__::GBVars.FminLimitGuardband)') if "FMIN" in flow else Spec(f'toString(__shared__::GBVars.LimitGuardband)')),         
         ForwardingMode = "None" if test_type in ["BILBO", "TRUNKDBG"] else ("Input" if test_parms["IS_EDC"] else "InputOutput"),
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "cpu_fun_timing_mts400_tstprtclk200_tck50_funatom" if "FMIN" in flow else  "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS", "SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
         BaseNumbers =  -44,
         CornerIdentifiers = f"CCF0@{corner}" if test_type == "SLC_DRAGON" else f"AT1@{corner},AT0@{corner}",
         VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
         VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --overrides ATOM1:1.2,ATOM0:1.2" if test_type == "SLC_DRAGON" and "F4" in corner else  "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL" if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1",
         PatternNameCounterIndexes = "9,10,11,12,13,14,15", 
         FivrCondition = "NOM",
         PinMap = "" if test_type in ["BILBO", "TRUNKDBG"] else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
         FivrConditionPlistParamName = "Patlist",
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else Spec(f"__shared__::Recovery_Single.F1F4_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         RecoveryMode = "NoRecovery" if test_type in ["BILBO", "TRUNKDBG", "SLC_DRAGON"] else ("RecoveryPort"),
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits = (Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL")) if corner == "F1" else (Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "",
         DtsConfiguration = Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p'), #if "F1" in corner or "F3" in corner and test_type == "L2_LOCKSTEP" else "", #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p)')) if "F4" in corner or "F3" in corner and test_type == "L2_LOCKSTEP" else "",
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         ScoreboardEdgeTicks= Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
         ExecutionMode = "SearchWithScoreboard",
         MaxFailsNum= Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance=f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_{corner}_FREQ])*60)),10)))",
         SetPointsPreInstance = 
         TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_{corner}_FREQ+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.1GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:2.8GHz"' if "L2_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))) if "F1" in corner 
         else TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_{corner}_FREQ+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.6GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.3GHz"'if "L2_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.5GHz"'))) if "F2" in corner
         else TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_{corner}_FREQ+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.9GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.7GHz"'if "L2_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.7GHz"'))) if "F3" in corner
         else  TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_{corner}_FREQ+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:5.1GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.9GHz"'if "L2_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.7GHz"')))
            ),# Close the braces for the MTT Template        
         r0=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=2, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=-44, ret=3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')) if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, ret=3, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=4, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=-44, ret=5, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r3 = (pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0)) if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, goto="NEXT"),
                        r4 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0),
                        r5 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0))))
  
   return test_list_funflow

######################################################################### VMAX Params for F1
def get_test_vmax(flow, corner, FlowMatrix, subflow, content_list):
    test_list_vmaxflow = []
    for test_type, test_parms in content_list.items():
        power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
        test_list_vmaxflow.append(
            VminTC(
                name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
                BypassPort=test_parms["Bypass"],
                #StartVoltagesOffset=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                #StartVoltagesForRetry=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                ExecutionMode="SearchWithScoreboard",
                TestMode = "Scoreboard",
                ScoreboardEdgeTicks= Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
                MaxFailsNum= Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
                LimitGuardband="",
                ForwardingMode = "None" if test_type in ["BILBO", "TRUNKDBG"] else ("Input" if test_parms["IS_EDC"] else "InputOutput"),
                FeatureSwitchSettings='disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
                LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
                Patlist=('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_list" if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS", "SLC_DRAGON"] else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_list"),
                BaseNumbers=-44,
                CornerIdentifiers="",
                VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
                VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --overrides ATOM1:1.2,ATOM0:1.2,CCF:1.2" if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1 --overrides ATOM1:1.2,ATOM0:1.2",
                PatternNameCounterIndexes="9,10,11,12,13,14,15",
                DtsConfiguration  = test_parms.get("DtsConfiguration",Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p')), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p)')),
                FivrCondition="NOM",
                PinMap="" if test_type in ["BILBO", "TRUNKDBG"] else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')) if test_type in "L2_LOCKSTEP" else Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_dragon_freq'),
                FivrConditionPlistParamName="Patlist",
                RecoveryTrackingIncoming=(Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS", "L2_LOCKSTEP", "SLC_DRAGON"] else ""),
                StepSize=Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
                RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else Spec(f"__shared__::Recovery_Single.F1F4_recovery_opt_AT"),
                RecoveryTrackingOutgoing=(Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS", "L2_LOCKSTEP", "SLC_DRAGON"] else ""),
                RecoveryMode= "NoRecovery" if test_type in ["BILBO", "TRUNKDBG", "SLC_DRAGON"] else "RecoveryPort", ##As part of VMAXF1 requirements
                FailCaptureCount=Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
                MultiPassMasks = "",
                EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE") if test_type == "SLC_DRAGON" else 
                                 Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
                StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE") if test_type == "SLC_DRAGON" else 
                              Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
                SetPointsPlistParamName="Patlist",
                SetPointsPostInstance="",
                MaxRepetitionCount=0,
                FlowIndex= Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                PreInstance= f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_{corner}_FREQ])*60)),10)))",
                SetPointsPreInstance= 
                
                Spec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_{corner}_FREQ+") +
                '"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.CCF_{corner}_FREQ") +
                ('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"] 
                 else 
                (f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"' 
                if test_type == "SLC_DRAGON" else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))
                ),

                _fitem=Fitem(
                    'SAME',
                    edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"] == True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                    r1=pPass(setbin=-44, goto="NEXT"),
                    r2=pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"] == True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                    r3=(pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0)) if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, goto="NEXT"),
                    r4=pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"] == True) else pFail(setbin=-44, ret=0),
                    r5=pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"] == True) else pFail(setbin=-44, ret=0)
                )
            )
        )
    return test_list_vmaxflow
############################################################################################################################### VMAXF5
def get_test_listvmaxf5(flow, corner, FlowMatrix, corner_id, subflow, content_list):
     
   test_list = [] 
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
      test_list.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING_TOP" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM_TOP",
         _comment='Sample VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_" + ' + Spec(f"__shared__::FreqInMHZ.{corner_id}") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         #StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         #StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         ExecutionMode = "Search" if "XAT" in flow else "SearchWithScoreboard",
         TestMode = "Scoreboard",
         ScoreboardEdgeTicks= Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
         MaxFailsNum= Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
         LimitGuardband = "",         
         ForwardingMode = "None" if test_type in ["BILBO", "TRUNKDBG"] else ("Input" if test_parms["IS_EDC"] else "InputOutput"),
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_list"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS", "SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_list"),         
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         BaseNumbers = -44,
         MultiPassMasks = "", #"0011,1100" if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else "",
         CornerIdentifiers = "",
         VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
         VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --overrides ATOM1:1.2,ATOM0:1.2,CCF:1.2" if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1  --overrides ATOM1:1.2,ATOM0:1.2",
         PinMap="" if test_type in ["BILBO", "TRUNKDBG"] else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')) if test_type in "L2_LOCKSTEP" else Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_dragon_freq'),
         PatternNameCounterIndexes = "9,10,11,12,13,14,15",
         DtsConfiguration = Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p'), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p,FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p)')),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         FivrCondition = "NOM",
         FivrConditionPlistParamName = "Patlist",
	     RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else TrialParamSpec(f"__shared__::Recovery.MTT_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         RecoveryMode = "NoRecovery",
         FlowIndex = "1",
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits =  Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "",
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.AT_C5+")*60)),10)))"') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","BILBO","TRUNKDBG"] else f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_F4_FREQ])*60)),10)))",
         SetPointsPreInstance = TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"] else ('+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"+' + Spec(f"__shared__::FreqValues.AT_C5+") + '"GHz"' if "FMIN" in subflow else ('+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"' if test_type == "SLC_DRAGON" else '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))))
         ),# Close the braces for the MTT Template         
         r0=pFail(setbin=-44, ret=0, trialaction = "Exit"), # Start MTT test port definitions. We will use -44binner here.
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=2, trialaction = "Exit"),
         r3=pFail(setbin=-44, ret=3, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=4, trialaction = "Exit"),
         r5=pFail(setbin=-44, ret=5, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"], # Define the Fitem info. We define the EDC status as an input param for ease of control in the future
                        r0 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r3 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r4 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0),
                        r5 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0))))
  
   return test_list

###############################################################################################################################  F5 Params
def get_test_list(flow, corner, FlowMatrix, corner_id, subflow, content_list):
     
   test_list = [] #F5
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
      test_list.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING_TOP" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM_TOP",
         _comment='Sample VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_" + ' + Spec(f"__shared__::Corners.{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.{corner_id}") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , ["","",""])'),
         StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , ["","",""])'),
         TestMode = "SingleVmin" if "SLC_DRAGON" in test_type else "MultiVmin",
         LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)') if not (test_parms.get("IS_EDC", False) or (test_type in ["BILBO", "TRUNKDBG"])) else "",         
         ForwardingMode = "None" if test_type in ["BILBO", "TRUNKDBG"] else ("Input" if test_parms["IS_EDC"] else "InputOutput"),
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS", "SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         BaseNumbers = -44,
         ScoreboardEdgeTicks= Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
         ExecutionMode = "SearchWithScoreboard",
         MaxFailsNum= Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
         MultiPassMasks =  "", #"0011,1100" if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else "",
         CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.{corner_id}")),
         VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
         VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --overrides ATOM1:1.2,ATOM0:1.2" if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1" if "L2" in test_type else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1",
         PinMap = "" if test_type in ["BILBO", "TRUNKDBG"] else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
         PatternNameCounterIndexes = "9,10,11,12,13,14,15",
         DtsConfiguration = Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p'), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p)')),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         FivrCondition = "NOM",
         FivrConditionPlistParamName = "Patlist",
	     RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else TrialParamSpec(f"__shared__::Recovery.MTT_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         RecoveryMode = "NoRecovery" if test_type in ["BILBO", "TRUNKDBG", "SLC_DRAGON"] else ("RecoveryPort"),
         FlowIndex = "1",
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits =  Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "",
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE"),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.AT_C5+")*60)),10)))"') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","BILBO","TRUNKDBG"] else f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_F4_FREQ])*60)),10)))",
         SetPointsPreInstance = TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz"') if test_type in ["BILBO", "TRUNKDBG"]else 
                                TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz,Fun_Atom_RAGN:ratio_modify:4.0GHz"') if test_type in "L2_DRAGON" else
                                TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz,Fun_Atom_RAGN:ratio_modify:4.7GHz"') if test_type in "L2_LOCKSTEP" else
                                TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_F4_FREQ+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz,Fun_Atom_RAGN:ratio_modify:4.1GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"')))))
         ),# Close the braces for the MTT Template         
         r0=pFail(setbin=-44, ret=0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions. We will use -44binner here.
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=2, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r3=pFail(setbin=-44, ret=3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")'))  if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, ret=3, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=4, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         r5=pFail(setbin=-44, ret=5, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"], # Define the Fitem info. We define the EDC status as an input param for ease of control in the future
                        r0 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r3 = (pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0)) if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, goto="NEXT"),
                        r4 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0),
                        r5 = pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=-44, ret=0))))
  
   return test_list
############################################################################################################################### LTTC Params
def get_test_list_LTTC_f1(flow, corner, FlowMatrix, subflow, content_list):
     
   test_list_funflow = []
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
      test_list_funflow.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM",
         _comment='SpeedFlow F1_F4 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , "")'),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , "")'),
         TestMode = "SingleVmin" if "SLC_DRAGON" in test_type else "MultiVmin",
         LimitGuardband = "31mV",
         ForwardingMode = "Input",
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "cpu_fun_timing_mts400_tstprtclk200_tck50_funatom" if "FMIN" in flow else  "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
         Patlist =('IPC::'f"fun_cdie_atom_lttccpu_{test_type.lower()}_{corner.lower()}_list_list"),         
         BaseNumbers =  -44,
         CornerIdentifiers = "",
         VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
         VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL --overrides ATOM1:1.2,ATOM0:1.2" if test_type == "SLC_DRAGON" and "F4" in corner else  "--dlvrpins VCCIA --railconfigurations CDIE_CCF_POWERMUX CDIE_CCF_NBLCTRL" if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1",
         PatternNameCounterIndexes = "9,10,11,12,13,14,15", 
         DtsConfiguration = Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p'), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M("nvl_cpu_all_noctv", "nvl_cpu_all_noctv", "nvl_cpu_all_noctv", "nvl_cpu_all_noctv","nvl_cpu_all_noctv")')),
         FivrCondition = "NOM",
         PinMap = test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_dragon_freq')),
         FivrConditionPlistParamName = "Patlist",
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else Spec(f"__shared__::Recovery_Single.F1F4_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         RecoveryMode = "NoRecovery",
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits = "D.RF1AT",
         StartVoltages = "D.RF1AT",
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "",
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         ScoreboardEdgeTicks= Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
         ExecutionMode = "SearchWithScoreboard",
         MaxFailsNum= Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance=f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_{corner}_FREQ])*60)),10)))",
         SetPointsPreInstance = 
         TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_{corner}_FREQ+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:4.1GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))) 

            ),# Close the braces for the MTT Template         
         r0=pFail(setbin=-44, ret=0, trialaction = "Exit"),
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=2, trialaction = "Exit"),
         r3=pFail(setbin=-44, ret=3, trialaction = "Exit") if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, ret=3, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=4, trialaction = "Exit"),
         r5=pFail(setbin=-44, ret=5, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"],
                        r0 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r3 = (pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0)) if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, goto="NEXT"),
                        r4 = pFail(setbin=9794, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=9794, ret=0),
                        r5 = pFail(setbin=9419, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=9419, ret=0))))
  
   return test_list_funflow
############################################################################################################################### LTTC Params
def get_test_list_LTTC_f5(flow, corner, FlowMatrix, corner_id, subflow, content_list): ##shares both F5 and VMAXX
     
   test_list = [] 
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "AT"
      test_list.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING_TOP" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM_TOP",
         _comment='Sample VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_" + ' + Spec(f"__shared__::Corners.{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.{corner_id}") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner} , ["","",""])') if "VMAX" not in subflow else Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner} , ["","",""])') if "VMAX" not in subflow else Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         TestMode = "MultiVmin" if "VMAX" not in subflow else "Scoreboard",
         LimitGuardband = "31mV",    
         ForwardingMode = "Input",
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
         Patlist =('IPC::'f"fun_cdie_atom_lttccpu_{test_type.lower()}_{corner.lower()}_list_list"),
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         BaseNumbers = -44,
         ScoreboardEdgeTicks=  Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)") if "VMAX" in subflow else Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
         ExecutionMode = "SearchWithScoreboard",
         MaxFailsNum= Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)") if "F5" in corner else Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
         MultiPassMasks =  "", #"0011,1100" if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else "",
         CornerIdentifiers = "",
         VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
         VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1  CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1" if "VMAX" not in subflow else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1  --overrides ATOM3:1.2,ATOM2:1.2,ATOM1:1.2,ATOM0:1.2",
         PinMap = Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_dragon_freq'), 
         PatternNameCounterIndexes = "9,10,11,12,13,14,15",
         DtsConfiguration = Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p'), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p)')),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         FivrCondition = "NOM",
         FivrConditionPlistParamName = "Patlist",
	     RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else TrialParamSpec(f"__shared__::Recovery.MTT_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         RecoveryMode = "NoRecovery",
         FlowIndex = "1",
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits =  TrialParamSpec(f'"D.R"+'+Spec(f"__shared__::Corners.{corner_id}")+'+"AT"'),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "",
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         StartVoltages = TrialParamSpec(f'"D.R"+'+Spec(f"__shared__::Corners.{corner_id}")+'+"AT"'),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.AT_C5+")*60)),10)))"') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","BILBO","TRUNKDBG"] else f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_F4_FREQ])*60)),10)))",
         SetPointsPreInstance = TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz"') if test_type in ["BILBO", "TRUNKDBG"]else 
                                TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"') if test_type in "L2_DRAGON" else
                                TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz,Fun_Atom_RAGN:ratio_modify:4.7GHz"') if test_type in "L2_LOCKSTEP" else
                                TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_F4_FREQ+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz,Fun_Atom_RAGN:ratio_modify:4.1GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"'))))) if "VMAX" not in subflow else TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"] else ('+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"+' + Spec(f"__shared__::FreqValues.AT_C5+") + '"GHz"' if "FMIN" in subflow else ('+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"' if test_type == "SLC_DRAGON" else '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))))
         ),# Close the braces for the MTT Template         
         r0=pFail(setbin=-44, ret=0, trialaction = "Exit"), # Start MTT test port definitions. We will use -44binner here.
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=2, trialaction = "Exit"),
         r3=pFail(setbin=-44, ret=3, trialaction = "Exit")  if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, ret=3, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=4, trialaction = "Exit"),
         r5=pFail(setbin=-44, ret=5, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"], # Define the Fitem info. We define the EDC status as an input param for ease of control in the future
                        r0 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r3 = (pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0)) if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, goto="NEXT"),
                        r4 = pFail(setbin=9794, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=9794, ret=0),
                        r5 = pFail(setbin=9419, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=9419, ret=0))))
  
   return test_list

############################################################################################################################### LTTC Params
def get_test_list_LTTC_vmax(flow, corner, FlowMatrix, corner_id, subflow, content_list, test_name): ##shares both F5 and VMAXX
     
   test_list = [] 
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "AT"
      test_list.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}_{test_name}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING_TOP" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM_TOP",
         _comment='Sample VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_" + ' + Spec(f"__shared__::Corners.{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.{corner_id}") + f' + "_{test_type}_{test_name}"',         BypassPort = test_parms["Bypass"],
         #StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         #StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         TestMode = "Scoreboard",
         LimitGuardband = "31mV",    
         ForwardingMode = "Input",
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
         Patlist =('IPC::'f"fun_cdie_atom_lttccpu_{test_type.lower()}_vmax_{corner.lower()}_list_list"),   
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         BaseNumbers = -44,
         ScoreboardEdgeTicks=  Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
         ExecutionMode = "SearchWithScoreboard",
         MaxFailsNum=  Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
         MultiPassMasks =  "", #"0011,1100" if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else "",
         CornerIdentifiers = "",
         VoltageTargets =  "CCF" if test_type == "SLC_DRAGON" else "ATOM1,ATOM0",
         VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1  --overrides ATOM1:1.2,ATOM0:1.2",
         PinMap = test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')) if test_type in "L2_LOCKSTEP" else Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_dragon_freq'), 
         PatternNameCounterIndexes = "9,10,11,12,13,14,15",
         DtsConfiguration = Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S16C_n2p'), #test_parms.get("DtsConfiguration", Spec(f'__shared__::TpRule.If_DS0_DS1_M(FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_S52C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_HX28C_n2p, FUN_ATOM_{sku}_Specs.dtsconfig_noctv_P16C_n2p)')),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         FivrCondition = "NOM",
         FivrConditionPlistParamName = "Patlist",
	     RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG"] else TrialParamSpec(f"__shared__::Recovery.MTT_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","SLC_DRAGON"] else ""),
         RecoveryMode = "NoRecovery",
         FlowIndex = "1",
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits =  TrialParamSpec(f'"D.R"+'+Spec(f"__shared__::Corners.{corner_id}")+'+"AT"'),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "",
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         StartVoltages = TrialParamSpec(f'"D.R"+'+Spec(f"__shared__::Corners.{corner_id}")+'+"AT"'),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.AT_C5+")*60)),10)))"') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","BILBO","TRUNKDBG"] else f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_F4_FREQ])*60)),10)))",
         SetPointsPreInstance = TrialParamSpec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FreqValues.AT_C5+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FreqValues.CCF_C5") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"] else ('+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"+' + Spec(f"__shared__::FreqValues.AT_C5+") + '"GHz"' if "FMIN" in subflow else ('+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"' if test_type == "SLC_DRAGON" else '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))))
         ),# Close the braces for the MTT Template         
         r0=pFail(setbin=-44, ret=0, trialaction = "Exit"), # Start MTT test port definitions. We will use -44binner here.
         r1=pPass(setbin=-44, ret=1, trialaction = "Exit"),
         r2=pFail(setbin=-44, ret=2, trialaction = "Exit"),
         r3=pFail(setbin=-44, ret=3, trialaction = "Exit")  if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, ret=3, trialaction = "Exit"),
         r4=pFail(setbin=-44, ret=4, trialaction = "Exit"),
         r5=pFail(setbin=-44, ret=5, trialaction = "Exit"),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"], # Define the Fitem info. We define the EDC status as an input param for ease of control in the future
                        r0 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r1 = pPass(setbin=-44, goto="NEXT"),
                        r2 = pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0),
                        r3 = (pFail(setbin=test_parms.get("Binning",-44), goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=test_parms.get("Binning",-44), ret=0)) if test_type in ["BILBO", "TRUNKDBG"] else pPass(setbin=-44, goto="NEXT"),
                        r4 = pFail(setbin=9794, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=9794, ret=0),
                        r5 = pFail(setbin=9419, goto="NEXT") if (test_parms["IS_EDC"]==True) else pFail(setbin=9419, ret=0))))
  
   return test_list



######################################################################
# PrimePatConfigTestMethod Overrides
######################################################################
def get_init_list(subflow, hptp, content_list):
     
   test_list_init = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
        test_list_init.append(PrimePatConfigTestMethod(name=f"SBFT_ATOM_PATMOD_K_INIT_X_X_X_X_{test_type}",
                Plist=('IPC::fun_cdie_atom_f1xatccf_slc_dragon_list_master'if test_type == "SLC_DRAGON" else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"),                
                ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_{test_type.upper()}_patConfigSetPoints.json"'),
                SetPoint=f'FUN_ATOM_{test_type}_R8_Wait_Time',               
                BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_init

######################################################################
# PrimePatConfigTestMethod Debug Counters
######################################################################
#def get_init_debugcounter_list(subflow, hptp, content_list):
     
  # test_list_debugcounter = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   #for test_type, test_parms in content_list.items():
       # test_list_debugcounter.append(PrimePatConfigTestMethod(name=f"SBFT_CORE_PATMOD_K_INIT_X_X_X_X_DEBUG_COUNTER_{test_type}",
               #Plist = 'IPC::'f"fun_cdie_vcore_sbft_{subflow.lower()}_{test_type.lower()}_{hptp.lower()}_list_master",
               #ConfigurationFile = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_CORE_{sku}/InputFiles/Debug_Counter.PatConfigSetPoints.json"'),
               #SetPoint = f'DBGCNTR_{test_type}',
               #BypassPort = test_parms["Bypass"],
               #_fitem=Fitem('SAME',
               #r0=pFail(setbin = -44, ret=0, ctr = 0),
               #r1=pPass(goto="NEXT"))))

   #return test_list_debugcounter

######################################################################
# PrimePatConfigTestMethod Wait Time
######################################################################
def get_init_waittime_list(subflow, hptp, content_list):
     
   test_list_waittime = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
        test_list_waittime.append(PrimePatConfigTestMethod(name=f"SBFT_ATOM_PATMOD_K_INIT_X_X_X_X_WAIT_TIME_{test_type}",
               Plist=('IPC::fun_cdie_atom_f1xatccf_slc_dragon_list_master' if test_type == "SLC_DRAGON" else 'IPC::fun_cdie_atom_full_l2_dragon_list' if test_type == "L2_DRAGON" else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"),              
               ConfigurationFile = test_parms.get ("ConfigurationFile", Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_FILE_patConfigSetPoints.json"')),
               SetPoint=f'FUN_ATOM_{test_type}_R8_Wait_Time',               
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_waittime

######################################################################
# PrimePatConfigTestMethod BurstON Midcat
######################################################################
def get_init_burstonmidcat_list(subflow, hptp, content_list):
     
   test_list_burstonmidcat = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
        test_list_burstonmidcat.append(PrimePatConfigTestMethod(name=f"SBFT_ATOM_PATMOD_K_INIT_X_X_X_X_BURSTON_{test_type}",
               Plist=('IPC::fun_cdie_atom_f1xatccf_slc_dragon_list_master'if test_type == "SLC_DRAGON" else 'IPC::fun_cdie_atom_full_l2_dragon_list' if test_type == "L2_DRAGON" else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"),              
               ConfigurationFile = test_parms.get ("ConfigurationFile", Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/BURSTON_FILE_patConfigSetPoints.json"')),
               SetPoint=f'FUN_ATOM_{test_type}_BURSTON_MIDCAT',               
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_burstonmidcat

######################################################################
# PinMap INIT RunCallback
######################################################################
def get_init_nonmisr_pinmap_list(content_list):
     
   test_list_nonmisr_pinmap_init = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for nonmisr_test, test_parms in content_list.items():
        test_list_nonmisr_pinmap_init.append(RunCallback(name=f"SBFT_ATOM_UF_K_INIT_X_X_X_X_VMIN_PINMAP_{nonmisr_test}",
               Parameters = test_parms.get ("Parameters",Spec(f'"--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_L2_DRAGON_FREQ.json')),
               Callback = 'LoadPinmapFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_nonmisr_pinmap_init

######################################################################
# MISR PinMap INIT RunCallback
######################################################################
def get_init_misr_pinmap_list(content_list):
     
   test_list_misr_pinmap_init = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for misr_test, test_parms in content_list.items():
        test_list_misr_pinmap_init.append(RunCallback(name=f"SBFT_ATOM_UF_K_INIT_X_X_X_X_VMIN_PINMAP_{misr_test}",
               Parameters = f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_SLC_DRAGON_FREQ.json', 
               Callback = 'LoadPinmapFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_misr_pinmap_init

######################################################################
# ApexTC INIT RunCallback
######################################################################
def get_init_apextc_list(content_list):
     
   test_list_apextc_init = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
        test_list_apextc_init.append(RunCallback(name=f"SBFT_ATOM_RUNCALLBACK_K_INIT_X_X_X_X_{test_type}",
               Parameters = Spec(MODULEPATH +' + 'f'"./Modules/FUN/FUN_ATOM_{sku}/InputFiles/ApexTC_Input_Config.json"'),
               Callback = 'ReadFrequencyPatConfigFile',
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_apextc_init

######################################################################
# Thermal RunCallback
######################################################################
def get_thermal_list(subflow,content_list):
     
   test_list_thermal = []
  
   for test_type, test_parms in content_list.items():
        test_list_thermal.append(RunCallback(name=f"SBFT_ATOM_RUNCALLBACK_K_{subflow}_X_X_X_X_{test_type}",
               Parameters = test_parms.get("Parameters", Spec(f'FunThermal.RCT90')),
               Callback = "ApplyControlSetpoint",
               BypassPort = test_parms["Bypass"],
               _fitem=Fitem('SAME',
               r0=pFail(setbin = -44, ret=0),
               r1=pPass(goto="NEXT"))))

   return test_list_thermal

################# START MTPL FLOW DEFINITON #####################
  
product_skus = ["CX48"]
 
for sku in product_skus:                                                    # <<<<<<<< This one
    mtplname = f"{product}_{sku}"
    # Initialize the module by defining the output mtpl path and the module name
    InitializeNVLClass(f'{mtplname}', f'{mtplname}', defaultthermalbin = [(97443000,97443999),(97942334,97942433)], defaultresetbin = [(44193000,44193999),(94192334, 94192433)], binrange = [(44512000,44703999),(94442334, 94442433)], defaultrm2bin = [(99443000, 99443999), (99942334, 99942433)], defaultrm1bin = [(98443000, 98443999), (98942334, 98942433)], mttbinstrategy = NVLClass8dig, basenumrange = (11501, 11700))
    LTTCPORT4 = 9794
    LTTCPORT5 = 9419
    #################################################################
    #         
    #                       INIT SUBFLOW                      
    #
    #################################################################
    INIT_SUBFLOW = "F1XAT"
    INIT_CORNER = "F1"
    # Input
    if sku == "CX48":
        Import(f"FUN_ATOM_{sku}_Specs.usrv")
        Import(f"FUN_ATOM_{sku}_Timing.tcg")

        INIT_content_list = {
       "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True},
       "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True}
        }

        ApexcTC_content_list = {
        "APEXTC" :   {"Bypass" : -1 , "IS_EDC" : True}
        }

        WaiTTime_content_list = {
       "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True,   "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_L2_DRAGON_N2P_patConfigSetPoints.json"' )},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_L2_LOCKSTEP_N2P_patConfigSetPoints.json"' )}, 
       "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True,  "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_SLC_DRAGON_N2P_patConfigSetPoints.json"' )},
        }

        BurstON_Midcat_content_list = {
        "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/BurstON_L2_Dragon_Midcat_N2P_patConfigSetPoints.json"' )},
        "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/BurstON_L2_Lockstep_Midcat_N2P_patConfigSetPoints.json"' )},
        "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/BurstON_SLC_Dragon_Midcat_N2P_patConfigSetPoints.json"' )},
        }

        L2_Pinmap_Content = {
        "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "Parameters" : Spec(f'"--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_L2_DRAGON_FREQ.json"')},
        "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True, "Parameters" : Spec(f'"--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_L2_LOCKSTEP_FREQ.json"')},
        "L2_DRAGON_APEX" : {"Bypass" :-1, "IS_EDC" : True, "Parameters" : Spec(f'"--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_L2_DRAGON.json"')},
        }
        
        SLC_DRAGON_Pinmap_Content = {
       "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "Parameters" : Spec(f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_SLC_DRAGON_FREQ.json"')},
       "SLC_DRAGON_APEX" : {"Bypass" : -1, "IS_EDC" : True, "Parameters" : Spec(f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_SLC_DRAGON.json"')},

       }
    else:
        {
            }

    L2PINMAP_INIT_Tests = get_init_nonmisr_pinmap_list(L2_Pinmap_Content)
    SLCPINMAP_INIT_Tests = get_init_misr_pinmap_list(SLC_DRAGON_Pinmap_Content)
    PINMAP_COMP = Flow ("PINMAP", L2PINMAP_INIT_Tests, SLCPINMAP_INIT_Tests)

    #INIT_DC_Tests = get_init_debugcounter_list(INIT_SUBFLOW, HPTP, DebugCounter_Init_List)
    #INIT_DC_COMP = Flow("DEBUG_COUNTER", INIT_DC_Tests)

    INIT_WT_Tests = get_init_waittime_list(INIT_SUBFLOW, HPTP, WaiTTime_content_list)
    INIT_BURSTON_Midcat = get_init_burstonmidcat_list(INIT_SUBFLOW, HPTP, BurstON_Midcat_content_list)
    INIT_WT_COMP = Flow("WAIT_TIME", INIT_WT_Tests, INIT_BURSTON_Midcat)

    APEXTC_INIT_Tests = get_init_apextc_list(ApexcTC_content_list)
 
    INIT_Subflow = Flow(f"FUN_ATOM_{sku}_INIT",
                        Fitem ('SAME', PINMAP_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                        Fitem ('SAME', INIT_WT_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
                        APEXTC_INIT_Tests)



    #################################################################
    #                       XATF1 SUBFLOW
    #################################################################
    XATF1_Flow = "XATF1"
    XATF1_Corner = "F1"
    XATF1_FlowMatrix = "AT_F1_FREQ"
    XATF1_Subflow = "F1XAT"
    if sku == "CX48":
        if "CCF" in XATF1_Subflow:
            XATF1_content_list = {
                "SLC_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF1_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": 1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_lockstep_freq'),
                    "Binning": 4453
                },
                "BILBO": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4454
                },
                "TRUNKDBG": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4455
                }
            }

    def get_ddg_shmoo_tests_f1(subflow, content_list):
        ddg_shmoo_tests = []
        test_names = [f"SBFT_ATOM_SHMOO_E_{subflow}_X_VCCIA_{XATF1_Corner}_X_{test_type}" for test_type in content_list]
        test_types = list(content_list.keys())
        for idx, test_type in enumerate(test_types):
            test_parms = content_list[test_type]
            name = test_names[idx]
            goto_next = test_names[idx + 1] if idx + 1 < len(test_names) else None
            ddg_shmoo_tests.append(
                DDGShmooTC(
                    name=name,
                    BypassPort= 1,
                    Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS", "SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
                    SetPointsPlistParamName="Patlist",
                    YAxisType ="FIVR",
                    VoltageConverter = "--dlvrpins VCCIA --expressions ATOM --railconfigurations CDIE_CCF_POWERMUX --fivrcondition NOM"  if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --expressions ATOM --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 --fivrcondition NOM",
                    TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
                    LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                    XAxisParam= "p_all_mts",
                    XAxisParamType="UserDefined",
                    XAxisRange= "760e6:10e6:12",
                    YAxisParam="CCF" if test_type == "SLC_DRAGON" else "ATOM3,ATOM2,ATOM1,ATOM0",
                    YAxisParamType="UserDefined",
                    YAxisRange="0.45:0.01:20",
                    PrintFormat="ShmooHub",
                    LogLevel="Enabled",
                    
                    _fitem=Fitem(
                        "SAME",
                        edc=True,
                        r0=pFail(setbin=-44, goto="NEXT"),
                        r1=pPass(setbin=-44, goto="NEXT"),
                        r2=pFail(setbin=-44, goto="NEXT"),
                        r3=pFail(setbin=-44, goto="NEXT"),
                        r4=pFail(setbin=-44, goto="NEXT"),
                        r5=pFail(setbin=-44, goto="NEXT"),
                    ),
                )
            )
        return ddg_shmoo_tests
        # ... rest of your code ...

    for sku in product_skus:
            # ... your setup code ...

        XATF1_Tests = get_test_list_f1_f4(XATF1_Flow, XATF1_Corner, XATF1_FlowMatrix, XATF1_Subflow, XATF1_content_list)
        F1_DDG_SHMOO_Tests = get_ddg_shmoo_tests_f1("F1XAT", XATF1_content_list)
        XATF1_Subflow = Flow(f"FUN_ATOM_{sku}_F1XAT", XATF1_Tests, F1_DDG_SHMOO_Tests)


    #################################################################
    #                       XATF2 SUBFLOW
    #################################################################
    XATF2_Flow = "XATF2"
    XATF2_Corner = "F2"
    XATF2_FlowMatrix = "AT_F2_FREQ"
    XATF2_Subflow = "F2XAT"
    if sku == "CX48":
        if "CCF" in XATF2_Subflow:
            XATF2_content_list = {
                "SLC_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF2_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": 1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_lockstep_freq'),
                    "Binning": 4453
                },
                "BILBO": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4454
                },
                "TRUNKDBG": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4455
                }
            }
    else:
        XATF2_content_list = {}
    XATF2_Tests = get_test_list_f1_f4(XATF2_Flow, XATF2_Corner, XATF2_FlowMatrix, XATF2_Subflow, XATF2_content_list)
    XATF2_Subflow = Flow(f"FUN_ATOM_{sku}_F2XAT", XATF2_Tests)

    #################################################################
    #                       XATF3 SUBFLOW
    #################################################################
    XATF3_Flow = "XATF3"
    XATF3_Corner = "F3"
    XATF3_FlowMatrix = "AT_F3_FREQ"
    XATF3_Subflow = "F3XAT"
    if sku == "CX48":
        if "CCF" in XATF3_Subflow:
            XATF3_content_list = {
                "SLC_DRAGON": {
                    "Bypass": 1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF3_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": 1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_lockstep_freq'),
                    "Binning": 4453
                },
                "BILBO": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4454
                },
                "TRUNKDBG": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4455
                }
            }
    else:
        XATF3_content_list = {}
    XATF3_Tests = get_test_list_f1_f4(XATF3_Flow, XATF3_Corner, XATF3_FlowMatrix, XATF3_Subflow, XATF3_content_list)
    XATF3_Subflow = Flow(f"FUN_ATOM_{sku}_F3XAT", XATF3_Tests)

    #################################################################
    #                       XATF4 SUBFLOW
    #################################################################
    XATF4_Flow = "XATF4"
    XATF4_Corner = "F4"
    XATF4_FlowMatrix = "AT_F4_FREQ"
    XATF4_Subflow = "F4XAT"
    if sku == "CX48":
        if "CCF" in XATF4_Subflow:
            XATF4_content_list = {
                "SLC_DRAGON": {
                    "Bypass": 1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF4_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": 1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_lockstep_freq'),
                    "Binning": 4453
                },
                "BILBO": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4454
                },
                "TRUNKDBG": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4455
                }
            }
    else:
        XATF4_content_list = {}
    XATF4_Tests = get_test_list_f1_f4(XATF4_Flow, XATF4_Corner, XATF4_FlowMatrix, XATF4_Subflow, XATF4_content_list)
    XATF4_Subflow = Flow(f"FUN_ATOM_{sku}_F4XAT", XATF4_Tests)

    #################################################################
    #                       XATF5 SUBFLOW
    #################################################################
    XATF5_Flow = "XATF5"
    XATF5_Corner = "F5"
    XATF5_FlowMatrix = "AT_F5_FREQ"
    XATF5_CornerID = "AT_C5"
    XATF5_SubFlow = "F5XAT"
    
    APEX_Flow = "XATF5"
    APEX_Corner = "F5"
    APEX_FlowMatrix = "AT_F5_FREQ"

    if sku == "CX48":
        if "CCF" in XATF5_SubFlow:
            XATF5_content_list = {
                "SLC_DRAGON": {
                    "Bypass": 1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF5_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": 1,
                    "IS_EDC": True,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_lockstep_freq'),
                    "Binning": 4453
                },
                "BILBO": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4454
                },
                "TRUNKDBG": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "Binning": 4455
                }
            }

            ApexTC_content_list = {
       "L2_DRAGON" : {"Bypass" : 1, "IS_EDC" : True, "PinMap" : Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon')},
       "SLC_DRAGON" : {"Bypass" : 1, "IS_EDC" : True, "PinMap" : Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_slc_dragon')},
    }
    else:
        XATF5_content_list = {}
    XATF5_Tests = get_test_list(XATF5_Flow, XATF5_Corner, XATF5_FlowMatrix, XATF5_CornerID, XATF5_SubFlow, XATF5_content_list)
    APEX_Tests = get_test_apextc(APEX_Flow, APEX_Corner, APEX_FlowMatrix, XATF5_SubFlow, HPTP, ApexTC_content_list)
    APEX_COMP = Flow("FUN_ATOM_CX48_FMAX", APEX_Tests)
    XATF5_SubFlow = Flow(f"FUN_ATOM_{sku}_F5XAT",XATF5_Tests[0],XATF5_Tests[1],Fitem ('SAME', APEX_COMP, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")), *XATF5_Tests[2:])        
    
    
    #################################################################
    #                  ADDITIONAL SUBFLOWS
    #################################################################
    # Define the subflows and their configurations
    new_subflows = [
        {"Flow": "F1XATCCF", "Corner": "F1", "FlowMatrix": "CCF_F1_FREQ", "BinningAppend": "10"}, 
        {"Flow": "F5XATLO", "Corner": "F5", "FlowMatrix": "AT_F5_FREQ", "BinningAppend": "50"},
        {"Flow": "F5XATCCFLO", "Corner": "F5", "FlowMatrix": "CCF_F5_FREQ", "BinningAppend": "50"},
        {"Flow": "F5XATCCF", "Corner": "F5", "FlowMatrix": "CCF_F5_FREQ", "BinningAppend": "50"},
        {"Flow": "F4XATCCF", "Corner": "F4", "FlowMatrix": "CCF_F4_FREQ", "BinningAppend": "40"},
        {"Flow": "F3XATCCF", "Corner": "F3", "FlowMatrix": "CCF_F3_FREQ", "BinningAppend": "30"}, 
        {"Flow": "F4XATLO", "Corner": "F4", "FlowMatrix": "AT_F4_FREQ", "BinningAppend": "40"},
        {"Flow": "F4XATCCFLO", "Corner": "F4", "FlowMatrix": "CCF_F4_FREQ", "BinningAppend": "40"},
        {"Flow": "F2XATCCF", "Corner": "F2", "FlowMatrix": "CCF_F2_FREQ", "BinningAppend": "20"},
        {"Flow": "FMINXAT", "Corner": "FMIN", "FlowMatrix": "AT_FMIN", "BinningAppend": "00"},
        {"Flow": "FMINXATCCF", "Corner": "FMIN", "FlowMatrix": "CCF_FMIN", "BinningAppend": "00"},
    ]

    # Loop through the subflows and create them dynamically
    for subflow in new_subflows:
        flow_name = subflow["Flow"]
        corner = subflow["Corner"]
        flow_matrix = subflow["FlowMatrix"]
        subflow_name = flow_name

        if sku == "CX48":
            if "CCF" in flow_name:
                content_list = {
                    "SLC_DRAGON": {
                        "Bypass": -1 if ("LO" in flow_name) or ("VMAX" in flow_name) else -1,
                        "IS_EDC": False,
                        "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_slc_dragon_freq'),
                        "XAxisType": "SpecSetVariable",
                        "YAxisType": "FIVR",
                        "XAxisRange": "8.5e-9:0.5e-9:8",
                        "YAxisRange": "0.45:0.01:60",
                        "VoltageOverridesSLCHigh": "--overrides ATOM1:1.2,ATOM0:1.2" if "F5" in corner else "",
                        "Binning": 4456
                    }
                }
            else:
                content_list = {
                    "L2_DRAGON": {
                        "Bypass": -1 if "LO" in flow_name else -1,
                        "IS_EDC": False,
                        "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                        "Binning": 4452
                    },
                    "L2_DRAGON_IS": {
                        "Bypass": 1,    
                        "IS_EDC": True,
                        "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_dragon_freq'),
                        "Binning": 4452
                    },
                    "L2_LOCKSTEP": {
                        "Bypass": -1 if "LO" in flow_name else -1, #Spec(f"__shared__::TpRule.If_DS0_DS1_M(-1, 1, 1, 1)") if "FMIN" in corner
                        "IS_EDC": True if "FMIN" in corner else False,
                        "PinMap": Spec(f'FUN_ATOM_CX48_Specs.recov_pinmap_l2_lockstep_freq'),
                        "Binning": 4453
                    },
                    "BILBO": {
                        "Bypass": -1 if "LO" in flow_name else -1,
                        "IS_EDC": False,
                        "Binning": 4454
                    },
                    "TRUNKDBG": {
                        "Bypass": -1 if "LO" in flow_name else -1,
                        "IS_EDC": False,
                        "Binning": 4455
                    }
                }
        else:
            content_list = {}

        if flow_name in ["FMINXAT", "FMINXATCCF"]:
            tests = get_test_list_fmin(flow_name, corner, flow_matrix, subflow_name, content_list)
        elif flow_name in ["F5XAT", "F5XATLO"]:
            tests = get_test_list(flow_name, corner, flow_matrix, "AT_C5", subflow_name, content_list)
        elif flow_name in ["F5XATCCFLO", "F5XATCCF"]:
            tests = get_test_list(flow_name, corner, flow_matrix, "CCF_C5", subflow_name, content_list)

        else:
            tests = get_test_list_f1_f4(flow_name, corner, flow_matrix, subflow_name, content_list)
        # --- Insert RCT90 RunCallback for F4XATCCFLO at the front ---
        if flow_name == "F4XATCCFLO":
            rct90_callback = RunCallback(
                name=f"SBFT_ATOM_RUNCALLBACK_K_{subflow_name}_X_X_X_X_SLC_DRAGON_RCT85",
                Parameters=Spec(f'FUN_ATOM_CX48_Rules.If_HOT(FunThermal.RCT85,FunThermal.RCT80,"")'),
                Callback="ApplyControlSetpoint",
                BypassPort = Spec(f'FUN_ATOM_CX48_Rules.If_HOT(-1,-1,1)'),
                _fitem=Fitem('SAME',
                    r0=pFail(setbin=-44, ret=0),
                    r1=pPass(goto="NEXT"))
                        )
            rct100_callback = RunCallback(
                name=f"SBFT_ATOM_RUNCALLBACK_K_{subflow_name}_X_X_X_X_SLC_DRAGON_RCT100",
                Parameters=Spec(f'FUN_ATOM_CX48_Rules.If_HOT(FunThermal.RCT100,FunThermal.RCT90,"")'),
                Callback="ApplyControlSetpoint",
                BypassPort = Spec(f'FUN_ATOM_CX48_Rules.If_HOT(-1,-1,1)'),
                _fitem=Fitem('SAME',
                    r0=pFail(setbin=-44, ret=0),
                    r1=pPass(goto="NEXT"))
            )
            tests = [rct90_callback] + tests + [rct100_callback]

        # --- Insert RCT90 and RCT100 RunCallbacks for F5XATCCFLO ---
        if flow_name == "F5XATCCFLO":
            rct90_callback = RunCallback(
                name=f"SBFT_ATOM_RUNCALLBACK_K_{subflow_name}_X_X_X_X_SLC_DRAGON_RCT85",
                Parameters=Spec(f'FUN_ATOM_CX48_Rules.If_HOT(FunThermal.RCT85,FunThermal.RCT80,"")'),
                Callback="ApplyControlSetpoint",
                BypassPort = Spec(f'FUN_ATOM_CX48_Rules.If_HOT(-1,-1,1)'),
                _fitem=Fitem('SAME',
                    r0=pFail(setbin=-44, ret=0),
                    r1=pPass(goto="NEXT"))
            )
            rct100_callback = RunCallback(
                name=f"SBFT_ATOM_RUNCALLBACK_K_{subflow_name}_X_X_X_X_SLC_DRAGON_RCT100",
                Parameters=Spec(f'FUN_ATOM_CX48_Rules.If_HOT(FunThermal.RCT100,FunThermal.RCT90,"")'),
                Callback="ApplyControlSetpoint",
                BypassPort = Spec(f'FUN_ATOM_CX48_Rules.If_HOT(-1,-1,1)'),
                _fitem=Fitem('SAME',
                    r0=pFail(setbin=-44, ret=0),
                    r1=pPass(goto="NEXT"))
            )
            tests = [rct90_callback] + tests + [rct100_callback]

        if flow_name == "F1XATCCF":
            ddg_shmoo_tests = get_ddg_shmoo_tests_f1(flow_name, content_list)
            tests += ddg_shmoo_tests

        subflow_instance = Flow(f"FUN_ATOM_{sku}_{subflow_name}", tests)

        print(f"Created subflow: {subflow_name}")
#################################################################
#                       VMAX SUBFLOW
#################################################################
VMAX_Flow = "VMAX"
VMAX_Corner = "F1"
VMAX_FlowMatrix = "AT_F1_FREQ"
VMAX_Subflow = "VMAXXAT"

if sku == "CX48":
    # VMAXXAT SUBFLOW
    VMAX_F1_Flow = "VMAX"
    VMAX_F1_Corner = "F1"
    VMAX_F1_FlowMatrix = "AT_F1_FREQ"
    VMAX_F1_content_list = {
        "L2_DRAGON": {"Bypass": 1, "IS_EDC": False, "Binning": 4452},
        "L2_LOCKSTEP": {"Bypass": -1, "IS_EDC": False, "Binning": 4453},
        "BILBO": {"Bypass": -1, "IS_EDC": False, "Binning": 4454},
        "TRUNKDBG": {"Bypass": -1, "IS_EDC": False, "Binning": 4455},
    }
    VMAX_F1_Tests = get_test_vmax(VMAX_F1_Flow, VMAX_F1_Corner, VMAX_F1_FlowMatrix, VMAX_Subflow, VMAX_F1_content_list)

    VMAX_F5_Flow = "VMAX"
    VMAX_F5_Corner = "F5"
    VMAX_F5_FlowMatrix = "AT_F5_FREQ"
    VMAX_F5_CornerID = "AT_C5"
    VMAX_F5_Subflow = "VMAXXAT"
    VMAX_F5_content_list = {
        "L2_DRAGON": {"Bypass": 1, "IS_EDC": False, "Binning": 4452},
        "L2_LOCKSTEP": {"Bypass": -1, "IS_EDC": False, "Binning": 4453},
        "BILBO": {"Bypass": -1, "IS_EDC": False, "Binning": 4454},
        "TRUNKDBG": {"Bypass": -1, "IS_EDC": False, "Binning": 4455},
    }
    VMAX_F5_Tests = get_test_listvmaxf5(VMAX_F5_Flow, VMAX_F5_Corner, VMAX_F5_FlowMatrix, VMAX_F5_CornerID, VMAX_F5_Subflow, VMAX_F5_content_list)

    VMAX_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXAT", VMAX_F1_Tests, VMAX_F5_Tests)

    # VMAXXATLO SUBFLOW
    VMAXXATLO_F1_Flow = "VMAXXATLO"
    VMAXXATLO_F1_Corner = "F1"
    VMAXXATLO_F1_FlowMatrix = "AT_F1_FREQ"
    VMAXXATLO_F5_Corner = "F5"
    VMAXXATLO_F5_FlowMatrix = "AT_F5_FREQ"
    VMAXXATLO_F5_CornerID = "AT_C5"
    VMAXXATLO_Subflow = "VMAXXATLO"
    VMAXXATLO_content_list = {
        "L2_DRAGON": {"Bypass": 1, "IS_EDC": False, "Binning": 4452}, 
        "L2_LOCKSTEP": {"Bypass": -1, "IS_EDC": False, "Binning": 4453},
        "BILBO": {"Bypass": -1, "IS_EDC": False, "Binning": 4454},
        "TRUNKDBG": {"Bypass": -1, "IS_EDC": False, "Binning": 4455},
    }
    VMAXXATLO_F1_Tests = get_test_vmax(VMAXXATLO_F1_Flow, VMAXXATLO_F1_Corner, VMAXXATLO_F1_FlowMatrix, VMAXXATLO_Subflow, VMAXXATLO_content_list)
    VMAXXATLO_F5_Tests = get_test_listvmaxf5(VMAXXATLO_F1_Flow, VMAXXATLO_F5_Corner, VMAXXATLO_F5_FlowMatrix, VMAXXATLO_F5_CornerID, VMAXXATLO_Subflow, VMAXXATLO_content_list)
    VMAXXATLO_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXATLO", VMAXXATLO_F1_Tests, VMAXXATLO_F5_Tests)

    # VMAXXATCCF SUBFLOW
    VMAXXATCCF_F1_Flow = "VMAXXATCCF"
    VMAXXATCCF_F1_Corner = "F1"
    VMAXXATCCF_F1_FlowMatrix = "CCF_F1_FREQ"
    VMAXXATCCF_F5_Corner = "F5"
    VMAXXATCCF_F5_FlowMatrix = "CCF_F5_FREQ"
    VMAXXATCCF_F5_CornerID = "CCF_C5"
    VMAXXATCCF_Subflow = "VMAXXATCCF"
    VMAXXATCCF_F1_content_list = {
        "SLC_DRAGON": {"Bypass": 1, "IS_EDC": False, "Binning": 4456}
    }
    VMAXXATCCF_F5_content_list = {
        "SLC_DRAGON": {"Bypass": 1, "IS_EDC": False, "Binning": 4456}
    }
    VMAXXATCCF_F1_Tests = get_test_vmax(VMAXXATCCF_F1_Flow, VMAXXATCCF_F1_Corner, VMAXXATCCF_F1_FlowMatrix, VMAXXATCCF_Subflow, VMAXXATCCF_F1_content_list)
    VMAXXATCCF_F5_Tests = get_test_listvmaxf5(VMAXXATCCF_F1_Flow, VMAXXATCCF_F5_Corner, VMAXXATCCF_F5_FlowMatrix, VMAXXATCCF_F5_CornerID, VMAXXATCCF_Subflow, VMAXXATCCF_F5_content_list)
    VMAXXATCCF_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXATCCF", VMAXXATCCF_F1_Tests, VMAXXATCCF_F5_Tests)

    # VMAXXATCCFLO SUBFLOW
    VMAXXATCCFLO_F1_Flow = "VMAXXATCCFLO"
    VMAXXATCCFLO_F1_Corner = "F1"
    VMAXXATCCFLO_F1_FlowMatrix = "CCF_F1_FREQ"
    VMAXXATCCFLO_F5_Corner = "F5"
    VMAXXATCCFLO_F5_FlowMatrix = "CCF_F5_FREQ"
    VMAXXATCCFLO_F5_CornerID = "CCF_C5"
    VMAXXATCCFLO_Subflow = "VMAXXATCCFLO"
    VMAXXATCCFLO_content_list = {
        "SLC_DRAGON": {"Bypass": 1, "IS_EDC": False, "Binning": 4456},
    }
    VMAXXATCCFLO_F1_Tests = get_test_vmax(VMAXXATCCFLO_F1_Flow, VMAXXATCCFLO_F1_Corner, VMAXXATCCFLO_F1_FlowMatrix, VMAXXATCCFLO_Subflow, VMAXXATCCFLO_content_list)
    VMAXXATCCFLO_F5_Tests = get_test_listvmaxf5(VMAXXATCCFLO_F1_Flow, VMAXXATCCFLO_F5_Corner, VMAXXATCCFLO_F5_FlowMatrix, VMAXXATCCFLO_F5_CornerID, VMAXXATCCFLO_Subflow, VMAXXATCCFLO_content_list)
    VMAXXATCCFLO_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXATCCFLO", VMAXXATCCFLO_F1_Tests, VMAXXATCCFLO_F5_Tests)

else:
    VMAX_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXAT")

    #################################################################
    #                       LTTC SUBFLOW
    #################################################################
   
LTTC_Flow = "LTTC"
LTTC_Corner = "F1"
LTTC_FlowMatrix = "AT_F1_FREQ"
LTTC_Subflow = "LTTCCPU"


if sku == "CX48":
    # LTTCXAT SUBFLOW
    LTTC_F1_Flow = "LTTC"
    LTTC_F1_Corner = "F1"
    LTTC_F1_FlowMatrix = "AT_F1_FREQ"
    LTTC_F1_content_list = {
        "L2_DRAGON": {"Bypass": -1, "IS_EDC": True, "Binning": 9444},
    }
    LTTC_F1_Tests = get_test_list_LTTC_f1(LTTC_F1_Flow, LTTC_F1_Corner, LTTC_F1_FlowMatrix, LTTC_Subflow, LTTC_F1_content_list)

    LTTC_F5_Flow = "LTTC"
    LTTC_F5_Corner = "F5"
    LTTC_F5_FlowMatrix = "AT_F5_FREQ"
    LTTC_F5_CornerID = "AT_C5"
    LTTC_F5_Subflow = "LTTCCPU"
    LTTC_F5_content_list = {
        "L2_DRAGON": {"Bypass": -1, "IS_EDC": True, "Binning": 9444},
    }
    LTTC_F5_Tests = get_test_list_LTTC_f5(LTTC_F5_Flow, LTTC_F5_Corner, LTTC_F5_FlowMatrix, LTTC_F5_CornerID, LTTC_F5_Subflow, LTTC_F5_content_list)

    VMAX_F5_Flow = "VMAX_LTTC"
    VMAX_F5_Corner = "F5"
    VMAX_F5_FlowMatrix = "AT_F5_FREQ"
    VMAX_F5_CornerID = "AT_C5"
    VMAX_F5_Subflow = "LTTCCPU"
    VMAX_F5_Test_Name = "VMAX"
    VMAX_F5_content_list = {
        "L2_DRAGON": {"Bypass": -1, "IS_EDC": True, "Binning": 9444},
        "L2_LOCKSTEP": {"Bypass": -1, "IS_EDC": True, "Binning": 9444},

    }
    VMAX_F5_Tests = get_test_list_LTTC_vmax(VMAX_F5_Flow, VMAX_F5_Corner, VMAX_F5_FlowMatrix, VMAX_F5_CornerID, VMAX_F5_Subflow, VMAX_F5_content_list,VMAX_F5_Test_Name)

    LTTC_Subflow = Flow(f"FUN_ATOM_{sku}_LTTCCPU", LTTC_F1_Tests, LTTC_F5_Tests,VMAX_F5_Tests )