# Import the necessary classes from Pymtpl
from ctypes import SetPointerType
from operator import ge
from tkinter import DISABLED
from pymtpl.por_methods import VminTC, PrimePatConfigTestMethod, RunCallback, ApexTC, DDGShmooTC, DedcLoadConfigTC,ScreenTC  # type: ignore
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
               DtsConfiguration= (Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv')),
               BypassPort= -1,
               FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
               Targets= "CCF1,CCF" if test_type == "SLC_DRAGON" else "ATOM31,ATOM21,ATOM11,ATOM01,ATOM3,ATOM2,ATOM1,ATOM0",
               ForwardingMode="Input" if test_type == "L2_DRAGON" else "None",
               PinMap= "" if test_type in "SLC_DRAGON" else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.PinMap_NONMISR')),
               SetPointsPreInstance = "MCdrv:atomfreq_0:3.2GHz,MCdrv:ringfreq_0:3.1GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz" if test_type in "L2_DRAGON" else "MCdrv:atomfreq_0:3.2GHz,MCdrv:ringfreq_0:3.1GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff",
               #SetPointsPostInstance="MCdrv:R1_SET",
               #SetPointsPreInstance = Spec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.{FlowMatrix}+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz"'))),
               StepSize= 3,
               LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
               TimingsTc="FUN_ATOM_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
               Patlist = (
                    f'IPC::fun_cdie_atom_{subflow.lower()}ccf_slc_dragon_list_master'
                    if test_type == "SLC_DRAGON"
                    else f'IPC::fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master'
                ),               
               PatternNameCounterIndexes= "9,10,11,12,13,14,15",
               RecoveryOptions="",
               RecoveryTracking=(Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In') if test_type in "L2_DRAGON" else ""),
               End=Spec(f'__shared__::FlowMatrixSingular.APEX_ATOM_MIN'),
               Start=Spec(f'__shared__::FlowMatrixSingular.APEX_ATOM_MAX'),
               FivrCondition="NOM",
               FivrConditionPlistParamName="Patlist",
               VoltageConverter = "--dlvrpins VCCIA --railconfigurations CDIE_CCF_NBLCTRL CDIE1_CCF_NBLCTRL --overrides  ATOM31:1.1,ATOM21:1.1,ATOM11:1.1,ATOM01:1.1,ATOM3:1.1,ATOM2:1.1,ATOM1:1.1,ATOM0:1.1 " if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --railconfigurations CDIE_ATOM_POWERMUX CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL2 CDIE_L2_NBLCTRL3 --overrides ATOM3:1.1,ATOM2:1.1,ATOM1:1.1,ATOM0:1.1" ,
               ExportTokens= "" if test_type in "SLC_DRAGON" else "FXATC7,FXATC6,FXATC5,FXATC4,FXATC3,FXATC2,FXATC1,FXATC0",
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
         BypassPort = 1 if test_type in ["BILBO", "TRUNKDBG"] else -1,
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         ExecutionMode = "SearchWithScoreboard" if "XAT" in flow else "Search",
         TestMode = "MultiVmin" if "SLC_DRAGON" in test_type else "MultiVmin",
         LimitGuardband = "" if test_type in ["BILBO", "TRUNKDBG"] else (Spec(f'toString(__shared__::GBVars.FminLimitGuardband)')),         
         ForwardingMode = ("None" if test_type in ["BILBO", "TRUNKDBG"]else "Input" if test_type == "SLC_DRAGON" else "Input" if test_parms["IS_EDC"]else "Input"),
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "cpu_fun_timing_mts400_tstprtclk200_tck50_funatom" if "FMIN" in flow else  "FUN_ATOM_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS","SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
         BaseNumbers =  -44,
         CornerIdentifiers = Spec(f"__shared__::CornerIdentifiers.CCF_{corner_id}") if test_type == "SLC_DRAGON" else f"AT7@{corner},AT6@{corner},AT5@{corner},AT4@{corner},AT3@{corner},AT2@{corner},AT1@{corner},AT0@{corner}",
         VoltageTargets =  "CCF1,CCF" if test_type == "SLC_DRAGON" else "ATOM31,ATOM21,ATOM11,ATOM01,ATOM3,ATOM2,ATOM1,ATOM0",
         VoltageConverter = test_parms.get("VoltageConverter",Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NBLRailAtom + DROPOUT.AT_{corner}') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else (Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NBLRailCCF + DROPOUT.CLR_{corner}') if test_type == "SLC_DRAGON" else Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NoNBLRail + DROPOUT.AT_{corner}'))),
         PatternNameCounterIndexes = "9,10,11,12,13,14,15", 
         DtsConfiguration = "",
         FivrCondition = "NOM",
         PinMap =  "" if test_type in ["BILBO", "TRUNKDBG"]else "FATOM_CX816_SLC_Dragon_Pinmap_Dummy" if test_type == "SLC_DRAGON" else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
         FivrConditionPlistParamName = "Patlist",
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In')if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"]else (Spec(f'FUN_ATOM_{sku}_Specs.SLC_Recovery_Tracking_In') if test_type == "SLC_DRAGON" else "")),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG","SLC_DRAGON"] else Spec(f"__shared__::Recovery_Single.F1F4_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else ""),
         RecoveryMode = "NoRecovery",
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits = (Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL")) if corner == "F1" else (Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = Spec(f'PSPOST.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPOST.AT_{corner}'),
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance= (Spec(f'FUN_ATOM_{sku}_Specs.AtomConfigPreinstance')) if test_type == "SLC_DRAGON" else f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_{corner}_FREQ])*60)),10)))",
         SetPointsPreInstance = TrialParamSpec(
            (
                f'PSPRE.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPRE.AT_{corner}'
            ) +
            '+",MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_FMIN+") +'"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_FMIN") +('+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]else (f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:R1_SET"' if "SLC_DRAGON" in test_type else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"' if "FMIN" in subflow else f'+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz"')))
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
def get_test_list_f1_f4(flow, corner,corner_id, FlowMatrix, subflow, content_list):
     
   test_list_funflow = []
  
   for test_type, test_parms in content_list.items():
      power_domain_name = "CCF" if test_type == "SLC_DRAGON" else "AT"
      test_list_funflow.append(NativeMultiTrial(name=f"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_X_{FlowMatrix}_{test_type}",
         exitaction="Continue",
         trialvar = "CPU_TRIALS::FlowDomain.RING" if test_type in "SLC_DRAGON" else "CPU_TRIALS::FlowDomain.ATOM",
         _comment='SpeedFlow F1_F4 VminTC test with MTT',
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         ExecutionMode = "SearchWithScoreboard" if "XAT" in flow else "Search",
         TestMode = "MultiVmin" if "SLC_DRAGON" in test_type else "MultiVmin",
         LimitGuardband = "" if (test_parms["IS_EDC"] or (test_type in ["BILBO", "TRUNKDBG"])) else (Spec(f'toString(__shared__::GBVars.FminLimitGuardband)') if "FMIN" in flow else Spec(f'toString(__shared__::GBVars.LimitGuardband)')),         
         ForwardingMode = ("None" if test_type in ["BILBO", "TRUNKDBG"]else "InputOutput" if test_type == "SLC_DRAGON" else "Input" if test_parms["IS_EDC"]else "InputOutput"),
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "cpu_fun_timing_mts400_tstprtclk200_tck50_funatom" if "FMIN" in flow else  "FUN_ATOM_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS","SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
         BaseNumbers =  -44,
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         CornerIdentifiers = Spec(f"__shared__::CornerIdentifiers.CCF_{corner_id}") if test_type == "SLC_DRAGON" else Spec(f"__shared__::CornerIdentifiers.AT_{corner_id}"),
         VoltageConverter = test_parms.get( "VoltageConverter",Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NBLRailAtom + DROPOUT.AT_{corner}') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NBLRailF4CCF + DROPOUT.CLR_{corner}') if test_type == "SLC_DRAGON" and corner == "F4" else (Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NBLRailCCF + DROPOUT.CLR_{corner}') if test_type == "SLC_DRAGON" else Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NoNBLRail + DROPOUT.AT_{corner}'))),         
         VoltageTargets =  "CCF1,CCF" if test_type == "SLC_DRAGON" else "ATOM31,ATOM21,ATOM11,ATOM01,ATOM3,ATOM2,ATOM1,ATOM0",
         PatternNameCounterIndexes = "9,10,11,12,13,14,15", 
         DtsConfiguration = (Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv')) if "F4" in corner else "",       
         MultiPassMasks = (
            "" if test_type in ["BILBO", "TRUNKDBG", "SLC_DRAGON"]
            else "00110011,11001100" if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] and corner == "F4"
            else ""
            ),       
         FivrCondition = "NOM",
         PinMap =  "" if test_type in ["BILBO", "TRUNKDBG"]else "FATOM_CX816_SLC_Dragon_Pinmap_Dummy" if test_type == "SLC_DRAGON" else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
         FivrConditionPlistParamName = "Patlist",
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In')if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"]else (Spec(f'FUN_ATOM_{sku}_Specs.SLC_Recovery_Tracking_In') if test_type == "SLC_DRAGON" else "")),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG","SLC_DRAGON"] else Spec(f"__shared__::Recovery_Single.F1F4_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else ""),
         RecoveryMode = "NoRecovery" if test_type in ["BILBO", "TRUNKDBG", "SLC_DRAGON"] else ("RecoveryPort"),
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits = (Spec(f"__shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL")) if corner == "F1" else (Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE")),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = (
            Spec(f'PSPOST.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPOST.AT_{corner}')
            if corner in ["F1", "F2", "F3"]
            else ""
         ),         
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
         PreInstance= (Spec(f'FUN_ATOM_{sku}_Specs.AtomConfigPreinstance'))  if test_type == "SLC_DRAGON" else f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_{corner}_FREQ])*60)),10)))",
         SetPointsPreInstance = TrialParamSpec(
                (
                    f'PSPRE.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPRE.AT_{corner}'
                ) +
                '+",MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrix.AT_{corner}_FREQ+") +
                '"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrix.CCF_{corner}_FREQ") +
                (
                    '+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]
                    else (
                        '+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET"'
                        if "FMIN" in subflow
                        else '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET"'
                    )
                )
            )         
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
                StartVoltagesOffset=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StartVoltagesForRetry=Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                TestMode="Scoreboard" if test_type == "SLC_DRAGON" else "Scoreboard",
                #LimitGuardband=Spec(f'toString(__s hared__::GBVars.LimitGuardband)') if not (test_parms.get("IS_EDC", False) or (test_type in ["BILBO", "TRUNKDBG"])) else "",
                ForwardingMode = ("None" if test_type in ["BILBO", "TRUNKDBG"]else "Input" if test_type == "SLC_DRAGON"else "Input" if test_parms["IS_EDC"]else "Input"),
                FeatureSwitchSettings='disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
                LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",
                Patlist=('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master" if test_type in ["L2_LOCKSTEP", "L2_DRAGON", "SLC_DRAGON"] else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),
                ExecutionMode = "SearchWithScoreboard",
                BaseNumbers=-44,
                CornerIdentifiers="",
                VoltageTargets =  "CCF1,CCF" if test_type == "SLC_DRAGON" else "ATOM31,ATOM21,ATOM11,ATOM01,ATOM3,ATOM2,ATOM1,ATOM0", 
                VoltageConverter = Spec(f'" --dlvrpins VCCIA  --overrides  ATOM31:1.1,ATOM21:1.1,ATOM11:1.1,ATOM01:1.1,ATOM3:1.1,ATOM2:1.1,ATOM1:1.1,ATOM0:1.1  "' +  Spec(f' + DROPOUT.CLR_{corner}')) if test_type == "SLC_DRAGON" else Spec (f'"--dlvrpins VCCIA --overrides  ATOM31:1.1,ATOM21:1.1,ATOM11:1.1,ATOM01:1.1,ATOM3:1.1,ATOM2:1.1,ATOM1:1.1,ATOM0:1.1  "' +  Spec(f' + DROPOUT.AT_{corner}')),                
                PatternNameCounterIndexes="9,10,11,12,13,14,15",
                DtsConfiguration="",
                ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
                MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
                FivrCondition="NOM",
                PinMap =  "" if test_type in ["BILBO", "TRUNKDBG"]else "FATOM_CX816_SLC_Dragon_Pinmap_Dummy" if test_type == "SLC_DRAGON" else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
                FivrConditionPlistParamName="Patlist",
                RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In')if test_type in ["L2_DRAGON", "L2_LOCKSTEP"]else (Spec(f'FUN_ATOM_{sku}_Specs.SLC_Recovery_Tracking_In') if test_type == "SLC_DRAGON" else "")),
                StepSize=Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
                RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG","SLC_DRAGON"] else Spec(f"__shared__::Recovery_Single.F1F4_recovery_opt_AT"),
                RecoveryTrackingOutgoing= (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON", "L2_LOCKSTEP"] else ""),
                RecoveryMode= "NoRecovery" if test_type in ["BILBO", "TRUNKDBG", "SLC_DRAGON"] else "RecoveryPort", ##As part of VMAXF1 requirements
                FailCaptureCount=Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
                MultiPassMasks = "",
                EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE") if test_type == "SLC_DRAGON" else 
                                 Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
                StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE") if test_type == "SLC_DRAGON" else 
                              Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
                SetPointsPlistParamName="Patlist",
                SetPointsPostInstance = (
                    Spec(
                        f'PSPOST.CLR_{corner}+",CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'
                        if test_type == "SLC_DRAGON"
                        else (
                            f'PSPOST.AT_{corner}+",CDIE_ATOM:nblctrl_cdie_atom_l2:nblon,CDIE_ATOM:nblctrl1_cdie_atom_l2:nblon"'
                            if test_type in ["L2_DRAGON", "L2_LOCKSTEP"]
                            else f'PSPOST.AT_{corner}'))),                            
               MaxRepetitionCount=0,
                FlowIndex= Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                PreInstance= (Spec(f'FUN_ATOM_{sku}_Specs.AtomConfigPreinstance')) if test_type == "SLC_DRAGON" else f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_{corner}_FREQ])*60)),10)))",
                SetPointsPreInstance = Spec(
                    (
                        f'PSPRE.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPRE.AT_{corner}'
                    ) +
                    '+",MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_{corner}_FREQ+") +
                    '"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.CCF_{corner}_FREQ") +
                    (
                        '+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]
                        else (
                            '+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff,CDIE_ATOM:nblctrl1_cdie_atom_l2:nbloff"'
                            if "FMIN" in subflow
                            else (
                                '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'
                                if "CCF" in subflow
                                else '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff,CDIE_ATOM:nblctrl1_cdie_atom_l2:nbloff"'
                )
                )
                )
                ),                
                _fitem=Fitem(
                    'SAME',
                    edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"] == True) else pFail(setbin=-44, ret=0),
                    r1=pPass(setbin=-44, goto="NEXT"),
                    r2=pFail(setbin=-44, goto="NEXT") if (test_parms["IS_EDC"] == True) else pFail(setbin=-44, ret=0),
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
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         TestMode = "Scoreboard" if "SLC_DRAGON" in test_type else "Scoreboard",
         #LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)') if not (test_parms.get("IS_EDC", False) or (test_type in ["BILBO", "TRUNKDBG"])) else "",         
         ForwardingMode = ("None" if test_type in ["BILBO", "TRUNKDBG"]else "Input" if test_type == "SLC_DRAGON"else "Input" if test_parms["IS_EDC"]else "Input"),
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON", "SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In')if test_type in ["L2_DRAGON", "L2_LOCKSTEP"]else (Spec(f'FUN_ATOM_{sku}_Specs.SLC_Recovery_Tracking_In') if test_type == "SLC_DRAGON" else "")),
         BaseNumbers = -44,
         MultiPassMasks =  "00110011,11001100" if test_type in ["L2_DRAGON","L2_LOCKSTEP"] else "",
         CornerIdentifiers = "",
         VoltageTargets =  "CCF1,CCF" if test_type == "SLC_DRAGON" else "ATOM31,ATOM21,ATOM11,ATOM01,ATOM3,ATOM2,ATOM1,ATOM0",  
         VoltageConverter = (Spec(f'"--dlvrpins VCCIA --overrides  ATOM31:1.1,ATOM21:1.1,ATOM11:1.1,ATOM01:1.1,ATOM3:1.1,ATOM2:1.1,ATOM1:1.1,ATOM0:1.1,CCF1:1.1,CCF:1.1 "' + Spec(f' + DROPOUT.CLR_{corner}')) if test_type == "SLC_DRAGON" else Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NoNBLRailVmax + DROPOUT.AT_{corner}') if test_type in ["BILBO", "TRUNKDBG"] else Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NoNBLRailVmax + DROPOUT.AT_{corner}')),       
         PinMap =  "" if test_type in ["BILBO", "TRUNKDBG"]else "FATOM_CX816_SLC_Dragon_Pinmap_Dummy" if test_type == "SLC_DRAGON" else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
         PatternNameCounterIndexes = "9,10,11,12,13,14,15",
         DtsConfiguration = (Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv')),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         ExecutionMode = "SearchWithScoreboard",
         FivrCondition = "NOM",
         FivrConditionPlistParamName = "Patlist",
	     RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG","SLC_DRAGON"] else TrialParamSpec(f"__shared__::Recovery.MTT_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_LOCKSTEP"] else ""),
         RecoveryMode = "NoRecovery",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.VMX_EDGE_TICK)'),
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.VMX_MAX_FAILS)'),
         FlowIndex = "1",
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits =  Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance ="", #(Spec(f'"CCF:nblctrl_ccf:ccfnblon,CCF:nblctrl1_ccf:ccfnblon"'if test_type == "SLC_DRAGON"else (f'"CDIE_ATOM:nblctrl_cdie_atom_l2:nblon,CDIE_ATOM:nblctrl1_cdie_atom_l2:nblon"'if test_type in ["L2_DRAGON", "L2_LOCKSTEP"]else f'PSPOST.AT_{corner}'))),  
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE"),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.AT_C5+")*60)),10)))"') if test_type in ["L2_DRAGON","L2_LOCKSTEP","BILBO","TRUNKDBG"] else (Spec(f'FUN_ATOM_{sku}_Specs.AtomConfigPreinstance')),#f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_F4_FREQ])*60)),10)))",
         SetPointsPreInstance = (
         TrialParamSpec(
            (
                f'PSPRE.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPRE.AT_{corner}'
            )
            + '+",MCdrv:atomfreq_0:"+' 
            + (Spec(f"__shared__::FlowMatrixSingular.AT_F4_FREQ+") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FreqValues.AT_C5+"))
            + '"GHz,MCdrv:ringfreq_0:"+' 
            + Spec(f"__shared__::FreqValues.CCF_C5")
            + (
            '+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]
            else (
                '+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'
                if test_type == "SLC_DRAGON" and "FMIN" in subflow
                else (
                    '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'
                    if test_type == "SLC_DRAGON"
                    else (
                        '+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff,CDIE_ATOM:nblctrl1_cdie_atom_l2:nbloff"'
                        if "FMIN" in subflow
                        else '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff,CDIE_ATOM:nblctrl1_cdie_atom_l2:nbloff"'
      )
      )
      )
      )
    )
    )        
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
         template=VminTC(name=f'"SBFT_ATOM_VMIN_K_{subflow}_X_{power_domain_name}_{corner}_" + ' + Spec(f"__shared__::Corners.{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.{corner_id}") + f' + "_{test_type}"',
         BypassPort = test_parms["Bypass"],
         StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
         StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
         ExecutionMode = "SearchWithScoreboard" if "XAT" in flow else "Search",
         TestMode = "MultiVmin" if "SLC_DRAGON" in test_type else "MultiVmin",
         LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)') if not (test_parms.get("IS_EDC", False) or (test_type in ["BILBO", "TRUNKDBG"])) else "",         
         ForwardingMode = ("None" if test_type in ["BILBO", "TRUNKDBG"]else "InputOutput" if test_type == "SLC_DRAGON"else "Input" if test_parms["IS_EDC"]else "InputOutput"),
         FeatureSwitchSettings = 'disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
         TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
         Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON","L2_DRAGON_IS","SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
         RecoveryTrackingIncoming = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_In')if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"]else (Spec(f'FUN_ATOM_{sku}_Specs.SLC_Recovery_Tracking_In') if test_type == "SLC_DRAGON" else "")),
         BaseNumbers = -44,
         MultiPassMasks =  "00110011,11001100" if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else "",
         CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.{corner_id}")),
         VoltageTargets =  "CCF1,CCF" if test_type == "SLC_DRAGON" else "ATOM31,ATOM21,ATOM11,ATOM01,ATOM3,ATOM2,ATOM1,ATOM0",
         VoltageConverter = (Spec(f'"--dlvrpins VCCIA --railconfigurations CDIE_CCF_NBLCTRL CDIE1_CCF_NBLCTRL --overrides  ATOM31:1.1,ATOM21:1.1,ATOM11:1.1,ATOM01:1.1,ATOM3:1.1,ATOM2:1.1,ATOM1:1.1,ATOM0:1.1 "' + Spec(f' + DROPOUT.CLR_{corner}')) if test_type == "SLC_DRAGON" else Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NoNBLRail + DROPOUT.AT_{corner}') if test_type in ["BILBO", "TRUNKDBG"] else Spec(f'FUN_ATOM_{sku}_Specs.VoltageConverter_NBLRailAtom + DROPOUT.AT_{corner}')),       
         PinMap =  "" if test_type in ["BILBO", "TRUNKDBG"]else "FATOM_CX816_SLC_Dragon_Pinmap_Dummy" if test_type == "SLC_DRAGON" else test_parms.get("PinMap", Spec(f'FUN_ATOM_{sku}_Specs.recov_pinmap_l2_lockstep_freq')),
         PatternNameCounterIndexes = "9,10,11,12,13,14,15",
         DtsConfiguration = (Spec(f'FUN_ATOM_{sku}_Specs.dtsconfig_noctv')),
         StepSize = Spec(f'FUN_ATOM_{sku}_Specs.StepSize'),
         FivrCondition = "NOM",
         FivrConditionPlistParamName = "Patlist",
	     RecoveryOptions = "" if test_type in ["BILBO", "TRUNKDBG","SLC_DRAGON"] else TrialParamSpec(f"__shared__::Recovery.MTT_recovery_opt_AT"),
         RecoveryTrackingOutgoing = (Spec(f'FUN_ATOM_{sku}_Specs.L2_Recovery_Tracking_Out') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP"] else ""),
         RecoveryMode = "NoRecovery" if test_type in ["BILBO", "TRUNKDBG", "SLC_DRAGON"] else ("RecoveryPort"),
         FlowIndex = "1",
         ScoreboardEdgeTicks = Spec(f'toInteger(__shared__::Specs.CHK_EDGE_TICK)'),
         MaxFailsNum = Spec(f'toInteger(__shared__::Specs.CHK_MAX_FAILS)'),
         FailCaptureCount = Spec(f'FUN_ATOM_{sku}_Specs.Fail_Capture_Count'),
         EndVoltageLimits =  Spec(f"__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE"),
         SetPointsPlistParamName = "Patlist",
         SetPointsPostInstance = "", #Spec(f'PSPOST.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPOST.AT_{corner}'), 
         MaxRepetitionCount = 0, #2 if test_type == "SLC_DRAGON" else 0,
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE"),
         PreInstance= TrialParamSpec(f'"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble("+__shared__::FreqValues.AT_C5+")*60)),10)))"') if test_type in ["L2_DRAGON","L2_DRAGON_IS","L2_LOCKSTEP","BILBO","TRUNKDBG"] else (Spec(f'FUN_ATOM_{sku}_Specs.AtomConfigPreinstance')), #f"EvaluateExpression(--result G.U.S.FUNATOM_DYN_FREQ_BINARY --storagetype gsds --datatype string --expression Reverse(Dec2Bin(ToInt32(Ceiling(ToDouble([__shared__::FlowMatrixSingular.AT_F4_FREQ])*60)),10)))",
         SetPointsPreInstance = (
            TrialParamSpec(
                (
                    f'PSPRE.CLR_{corner}' if test_type == "SLC_DRAGON" else f'PSPRE.AT_{corner}'
                )
                + '+",MCdrv:atomfreq_0:"+' 
                + (Spec(f"__shared__::FlowMatrixSingular.AT_F4_FREQ+") if test_type == "SLC_DRAGON" else Spec(f"__shared__::FreqValues.AT_C5+"))
                + '"GHz,MCdrv:ringfreq_0:"+' 
                + Spec(f"__shared__::FreqValues.CCF_C5")
                + (
                    '+"GHz"' if test_type in ["BILBO", "TRUNKDBG"]
                    else (
                        '+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'
                        if test_type == "SLC_DRAGON" and "FMIN" in subflow
                        else (
                            '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CCF:nblctrl_ccf:ccfnbloff,CCF:nblctrl1_ccf:ccfnbloff"'
                            if test_type == "SLC_DRAGON"
                            else (
                                '+"GHz,Fun_Atom_RAGN:ratio_modify:0.4GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff,CDIE_ATOM:nblctrl1_cdie_atom_l2:nbloff"'
                                if "FMIN" in subflow
                                else '+"GHz,Fun_Atom_RAGN:ratio_modify:0.8GHz,MCdrv:pwrmux_sel_atom_l2_0:vcclogic,MCdrv:pwrmux_sel_ccf_0:vcclogic,MCdrv:R1_SET,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff,CDIE_ATOM:nblctrl1_cdie_atom_l2:nbloff"'
                            )
                        )
                    )
                )
            )
        )         
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


def get_test_list_ScreenGSDS_3(flow, testinput, cornerid):
    """
    For each CCF subflow, insert a screen test at the beginning of the test flow.
    The screen test is added for any flow containing 'CCF' in its name.
    Additionally:
    - If called for the F5XAT / FMAX context, return a ScreenTC intended to be
      inserted into the FMAX composite before the SLC_DRAGON ApexTC test.
    """
    test_listt_ScreenGSDS_3 = []
    for test_type, test_parms in testinput.items():
        # Add a screen test at the beginning of each CCF subflow
        if "CCF" in flow:
            screen_test_name = f"SBFT_CCF_SCREEN_X_{flow}_X_X_X_X_CCF_SCREEN_{cornerid}_{test_type}".replace("_FMAX_", "_X_")          
            test_listt_ScreenGSDS_3.append(
                ScreenTC(
                    name=screen_test_name,
                    ScreenTestSet=test_parms.get("ScreenTestSet", "FUN_ATOM_SCREEN_SingleFlow"),
                    ScreenTestsFile="./InputFiles/SBFT_ATOM_Downsku_screen.txt",
                    BypassPort=Spec(test_parms.get("Bypass", -1)),
                    _fitem=Fitem(
                        "SAME",
                        edc=test_parms.get("IS_EDC", False),
                        r0=pFail(setbin=4455),
                        r1=pPass(goto="NEXT"),
                        r2=pPass(goto="NEXT"),
                        #r3=pPass(goto="NEXT"),
                        #r4=pPass(goto="NEXT"),
                        #r5=pPass(goto="NEXT"),
                        #r6=pPass(goto="NEXT"),
                        #r7=pPass(goto="NEXT"),
                        #r9=pPass(goto="NEXT"),
                        #r10=pPass(goto="NEXT"),
                        #r11=pPass(goto="NEXT"),
                        #r12=pPass(goto="NEXT"),
                        #r13=pPass(goto="NEXT"),
                        #r14=pPass(goto="NEXT"),
                        #r15=pPass(goto="NEXT"),
                    ),
                )
            )

    # Special-case: provide a ScreenTC for the F5XAT FMAX composite so it can be
    # inserted before the SLC_DRAGON ApexTC inside the FMAX composite.
    # This function returns the ScreenTC(s); caller is responsible for inserting
    # them into the APEX composite (before the SLC_DRAGON test).
    if flow == "F5XAT":
        # build a screen for each SLC_DRAGON entry (if present in testinput)
        for test_type, test_parms in testinput.items():
            if test_type == "SLC_DRAGON":
                # name indicates this is intended for the FMAX composite of F5XAT
                apex_screen_name = f"SBFT_CCF_SCREEN_X_{flow}_FMAX_X_X_X_X_CCF_SCREEN_{cornerid}_{test_type}".replace("_FMAX_", "_X_")                
                test_listt_ScreenGSDS_3.append(
                    ScreenTC(
                        name=apex_screen_name,
                        ScreenTestSet=test_parms.get("ScreenTestSet", "FUN_ATOM_SCREEN_SingleFlow"),
                        ScreenTestsFile="./InputFiles/SBFT_ATOM_Downsku_screen.txt",
                        BypassPort=Spec(test_parms.get("Bypass", -1)),
                        _fitem=Fitem(
                            "SAME",
                            edc=test_parms.get("IS_EDC", False),
                            # Use a distinct setbin for FMAX-apex screen to make debugging clearer.
                            r0=pFail(setbin=4455),
                            r1=pPass(goto="NEXT"),
                            r2=pPass(goto="NEXT"),
                        ),
                    )
                )

    return test_listt_ScreenGSDS_3
 
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
               Plist=('IPC::fun_cdie_atom_f1xatccf_slc_dragon_list_master'if test_type == "SLC_DRAGON" else 'IPC::'f"fun_cdie_atom_full_{test_type.lower()}_list" if test_type in "L2_DRAGON" else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"),              
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
               Plist=('IPC::fun_cdie_atom_f1xatccf_slc_dragon_list_master'if test_type == "SLC_DRAGON" else 'IPC::'f"fun_cdie_atom_full_{test_type.lower()}_list" if test_type in "L2_DRAGON" else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"),          
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
               Parameters = f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_SLC_DRAGON_DUMMY.json',
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
               BypassPort = -1,
               _fitem=Fitem('SAME',
               edc = test_parms["IS_EDC"],
               r0=pFail(setbin = -44, ret=0, ctr = 0),
               r1=pPass(goto="NEXT"))))

   return test_list_apextc_init

################# START MTPL FLOW DEFINITON #####################
  
product_skus = ["CXPKGS9"]
 
for sku in product_skus:                                                    # <<<<<<<< This one
    mtplname = f"{product}_{sku}"
    # Initialize the module by defining the output mtpl path and the module name
    InitializeNVLClass(f'{mtplname}', f'{mtplname}', defaultthermalbin = (97443000,97443999), defaultresetbin = (44193000,44193999), binrange = [(44513000,44703999)],defaultrm2bin = [(99443000,99443999),(99453500,99453999)], defaultrm1bin = [(98443000,98443999),(98453500,98453999)], mttbinstrategy = NVLClass8dig, basenumrange = (11501, 11700))
   
    #################################################################
    #         
    #                       INIT SUBFLOW                      
    #
    #################################################################
    INIT_SUBFLOW = "F1XAT"
    INIT_CORNER = "F1"
    # Input
    if sku == "CXPKGS9":
        Import(f"FUN_ATOM_{sku}_Specs.usrv")
        Import(f"FUN_ATOM_{sku}_Timing.tcg")

        INIT_content_list = {
       "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True},
       "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True}
        }

        ApexcTC_content_list = {
        "APEXTC" :   {"Bypass" : 1, "IS_EDC" : True}
        }

        WaiTTime_content_list = {
       "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True,   "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_L2_DRAGON_patConfigSetPoints.json"' )},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
       "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_L2_LOCKSTEP_patConfigSetPoints.json"' )}, 
       "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True,  "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/WTO_SLC_DRAGON_patConfigSetPoints.json"' )},
        }

        BurstON_Midcat_content_list = {
        "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/BurstON_L2_Dragon_Midcat_patConfigSetPoints.json"' )},
        "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/BurstON_L2_Lockstep_Midcat_patConfigSetPoints.json"' )},
        "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "ConfigurationFile": Spec(MODULEPATH +' + 'f'"/Modules/FUN/FUN_ATOM_{sku}/InputFiles/BurstON_SLC_Dragon_Midcat_patConfigSetPoints.json"' )},
        }

        L2_Pinmap_Content = {
        "L2_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "Parameters" : Spec(f'"--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_L2_DRAGON_FREQ.json"')},
        "L2_LOCKSTEP" : {"Bypass" : -1, "IS_EDC" : True, "Parameters" : Spec(f'"--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_L2_LOCKSTEP_FREQ.json"')},
        }
        
        SLC_DRAGON_Pinmap_Content = {
       "SLC_DRAGON" : {"Bypass" : -1, "IS_EDC" : True, "Parameters" : Spec(f'--decoder FailDataDecoder --file ./Modules/FUN/FUN_ATOM_{sku}/InputFiles/DieRecoveryPinMaps_atom_sbft_SLC_DRAGON_FREQ.json"')},
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
    XATF1_CornerID="C1"
    XATF1_Subflow = "F1XAT"

    if sku == "CXPKGS9":
        if "CCF" in XATF1_Subflow:
            XATF1_content_list = {
                "SLC_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF1_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),
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
                    Patlist = ('IPC::'f"fun_cdie_atom_{subflow.lower()}_{test_type.lower()}_list_master"if test_type in ["L2_LOCKSTEP", "L2_DRAGON", "L2_DRAGON_IS", "SLC_DRAGON"]else 'IPC::'f"fun_cdie_atom_{subflow.lower()}_tap_{test_type.lower()}_list_master"),         
                    SetPointsPlistParamName="Patlist",
                    YAxisType ="FIVR",
                    VoltageConverter = "--dlvrpins VCCIA --expressions ATOM --railconfigurations CDIE_CCF_POWERMUX --fivrcondition NOM"  if test_type == "SLC_DRAGON" else "--dlvrpins VCCIA --expressions ATOM --railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_ATOM_POWERMUXM2 CDIE_ATOM_POWERMUXM3 --fivrcondition NOM",
                    TimingsTc =  "CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100" if test_type in ["BILBO", "TRUNKDBG"] else "FUN_ATOM_CXPKGS9::cpu_fun_timing_mts800_tstprtclk400_tck100_funatom",         
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
        XATF1_Tests = get_test_list_f1_f4(XATF1_Flow, XATF1_Corner, XATF1_CornerID, XATF1_FlowMatrix, XATF1_Subflow, XATF1_content_list)
        F1_DDG_SHMOO_Tests = get_ddg_shmoo_tests_f1("F1XAT", XATF1_content_list)
        XATF1_Subflow = Flow(f"FUN_ATOM_{sku}_F1XAT", XATF1_Tests, F1_DDG_SHMOO_Tests)


    #################################################################
    #                       XATF2 SUBFLOW
    #################################################################
    XATF2_Flow = "XATF2"
    XATF2_Corner = "F2"
    XATF2_FlowMatrix = "AT_F2_FREQ"
    XATF2_CornerID="C2"
    XATF2_Subflow = "F2XAT"

    if sku == "CXPKGS9":
        if "CCF" in XATF2_Subflow:
            XATF2_content_list = {
                "SLC_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF2_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),
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
    XATF2_Tests = get_test_list_f1_f4(XATF2_Flow, XATF2_Corner,XATF2_CornerID, XATF2_FlowMatrix,XATF2_Subflow, XATF2_content_list)
    XATF2_Subflow = Flow(f"FUN_ATOM_{sku}_F2XAT", XATF2_Tests)

    #################################################################
    #                       XATF3 SUBFLOW
    #################################################################
    XATF3_Flow = "XATF3"
    XATF3_Corner = "F3"
    XATF3_FlowMatrix = "AT_F3_FREQ"
    XATF3_CornerID = "C3"
    XATF3_Subflow = "F3XAT"


    if sku == "CXPKGS9":
        if "CCF" in XATF3_Subflow:
            XATF3_content_list = {
                "SLC_DRAGON": {
                    "Bypass": 1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF3_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),
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
    XATF3_Tests = get_test_list_f1_f4(XATF3_Flow, XATF3_Corner, XATF3_CornerID, XATF3_FlowMatrix, XATF3_Subflow, XATF3_content_list)
    XATF3_Subflow = Flow(f"FUN_ATOM_{sku}_F3XAT", XATF3_Tests)

    #################################################################
    #                       XATF4 SUBFLOW
    #################################################################
    XATF4_Flow = "XATF4"
    XATF4_Corner = "F4"
    XATF4_FlowMatrix = "AT_F4_FREQ"
    XATF4_CornerID= "C4"
    XATF4_Subflow = "F4XAT"
    

    if sku == "CXPKGS9":
        if "CCF" in XATF4_Subflow:
            XATF4_content_list = {
                "SLC_DRAGON": {
                    "Bypass": 1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF4_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),
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
    XATF4_Tests = get_test_list_f1_f4(XATF4_Flow, XATF4_Corner,XATF4_CornerID, XATF4_FlowMatrix,  XATF4_Subflow, XATF4_content_list)
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

    if sku == "CXPKGS9":
        if "CCF" in XATF5_SubFlow:
            XATF5_content_list = {
                "SLC_DRAGON": {
                    "Bypass": 1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_slc_dragon_freq')
                }
            }
        else:
            XATF5_content_list = {
                "L2_DRAGON": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_DRAGON_IS": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                    "Binning": 4452
                },
                "L2_LOCKSTEP": {
                    "Bypass": -1,
                    "IS_EDC": False,
                    "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),
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
       "L2_DRAGON" : {"Bypass" : 1, "IS_EDC" : True, "PinMap" : Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq')},
       "SLC_DRAGON" : {"Bypass" : 1, "IS_EDC" : True, "PinMap" : Spec(f'FUN_ATOM_CX816_Specs.recov_pinmap_slc_dragon')},
    }
    else:
        XATF5_content_list = {}
    XATF5_Tests = get_test_list(XATF5_Flow, XATF5_Corner, XATF5_FlowMatrix, XATF5_CornerID, XATF5_SubFlow, XATF5_content_list)
    APEX_Tests = get_test_apextc(APEX_Flow, APEX_Corner, APEX_FlowMatrix, XATF5_SubFlow, HPTP, ApexTC_content_list)
        
    # Insert ScreenTC(s) into the FMAX composite before the SLC_DRAGON ApexTC if any
    apex_screens = get_test_list_ScreenGSDS_3(
            "F5XAT",
            {k: dict(v, **{"Bypass": -1}) for k, v in ApexTC_content_list.items()},
            "CCF_C5"
        )
    if apex_screens:
        # Insert each screen test before the first occurrence of SLC_DRAGON ApexTC.
        # If SLC_DRAGON not found, prepend to the beginning of the APEX_Tests list.
        for screen in reversed(apex_screens):
            inserted = False
            for idx, t in enumerate(APEX_Tests):
                t_name = getattr(t, "name", "")
                if "SLC_DRAGON" in t_name:
                    APEX_Tests.insert(idx, screen)
                    inserted = True
                    break
            if not inserted:
                APEX_Tests.insert(0, screen)

    APEX_COMP = Flow("FUN_ATOM_CXPKGS9_FMAX", APEX_Tests)
    # Place this code immediately after you build XATF5_Tests and before you create XATF5_SubFlow

    # Insert FMAX composite (APEX_COMP) after L2_LOCKSTEP in XATF5_Tests
    l2_lockstep_idx = None
    for idx, test in enumerate(XATF5_Tests):
        if hasattr(test, "name") and "L2_LOCKSTEP" in test.name:
            l2_lockstep_idx = idx
            break

    if l2_lockstep_idx is not None:
        XATF5_Tests.insert(
            l2_lockstep_idx + 1,
            Fitem('SAME', APEX_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT"))
        )
        XATF5_SubFlow = Flow(f"FUN_ATOM_{sku}_F5XAT", XATF5_Tests)
    else:
        XATF5_SubFlow = Flow(
            f"FUN_ATOM_{sku}_F5XAT",
            Fitem('SAME', APEX_COMP, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT")),
            XATF5_Tests
        )

        XATF5_SubFlow = Flow(f"FUN_ATOM_{sku}_F5XAT",Fitem ('SAME', APEX_COMP, r0=pFail(goto="NEXT" ), r1=pPass(goto="NEXT")), XATF5_Tests)        
    
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
        {"Flow": "FMINXAT", "Corner": "F1", "FlowMatrix": "AT_F1_FREQ", "BinningAppend": "00"},
        {"Flow": "FMINXATCCF", "Corner": "F1", "FlowMatrix": "CCF_F1_FREQ", "BinningAppend": "00"}
    ]

    # Loop through the subflows and create them dynamically
    for subflow in new_subflows:
        flow_name = subflow["Flow"]
        corner = subflow["Corner"]
        flow_matrix = subflow["FlowMatrix"]
        corner_id = f"C{corner[1:]}" if "CCF" in flow_name else f"C{corner[1:]}"
        subflow_name = flow_name

        if sku == "CXPKGS9":
            if "CCF" in flow_name:
                content_list = {
                    "SLC_DRAGON": {
                        "Bypass": 1 if ("LO" in flow_name) or ("VMAX" in flow_name) else -1,
                        "IS_EDC": True if "LO" in flow_name else False,
                        "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_slc_dragon_freq'),
                        "Preinstance": "FUN_ATOM_CXPKGS9_Specs.recov_preinstance_slc_dragon_freq",
                        "XAxisType": "SpecSetVariable",
                        "YAxisType": "FIVR",
                        "XAxisRange": "8.5e-9:0.5e-9:8",
                        "YAxisRange": "0.45:0.01:60",
                        "VoltageOverridesSLCHigh": "--overrides ATOM3:1.1,ATOM2:1.1,ATOM1:1.1,ATOM0:1.1" if "F5" in corner else "",
                        "Binning": 4456
                    }
                }
            else:
                content_list = {
                    "L2_DRAGON": {
                        "Bypass": 1 if "LO" in flow_name else -1,
                        "IS_EDC": False, #False if not "FMIN" in flow_name else True,
                        "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                        "Binning": 4452
                    },
                    "L2_DRAGON_IS": {
                        "Bypass": 1,    
                        "IS_EDC": False,
                        "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),
                        "Binning": 4452
                    },
                    "L2_LOCKSTEP": {
                        "Bypass": 1 if "LO" in flow_name else -1,
                        "IS_EDC": False, #False if not "FMIN" in flow_name else True,
                        "PinMap": Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),
                        "Binning": 4453
                    },
                    "BILBO": {
                        "Bypass": 1 if "LO" in flow_name else -1,
                        "IS_EDC": False, #False if not "FMIN" in flow_name else True,
                        "Binning": 4454
                    },
                    "TRUNKDBG": {
                        "Bypass": 1 if "LO" in flow_name else -1,
                        "IS_EDC": False, #False if not "FMIN" in flow_name else True,
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
            tests = get_test_list_f1_f4(flow_name, corner,corner_id, flow_matrix, subflow_name, content_list)

            # Only prepend screen tests for CCF subflows that are NOT LO subflows
        if "CCF" in flow_name and "LO" not in flow_name:
            screen_tests = get_test_list_ScreenGSDS_3(flow_name, content_list, corner_id)
            tests = screen_tests + tests

            # Add DDG Shmoo tests for F1XATCCF
        if flow_name == "F1XATCCF":
            ddg_shmoo_tests = get_ddg_shmoo_tests_f1(flow_name, content_list)
            #tests += ddg_shmoo_tests

        subflow_instance = Flow(f"FUN_ATOM_{sku}_{subflow_name}", tests)

        print(f"Created subflow: {subflow_name}")

#################################################################
#                       VMAX SUBFLOW
#################################################################
VMAX_Flow = "VMAX"
VMAX_Corner = "F1"
VMAX_FlowMatrix = "AT_F1_FREQ"
VMAX_Subflow = "VMAXXAT"

if sku == "CXPKGS9":
    # VMAXXAT SUBFLOW
    VMAX_F1_Flow = "VMAX"
    VMAX_F1_Corner = "F1"
    VMAX_F1_FlowMatrix = "AT_F1_FREQ"
    VMAX_F1_content_list = {
        "L2_DRAGON": {"Bypass": -1, "IS_EDC": False ,"PinMap":Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),},
        "L2_LOCKSTEP": {"Bypass": -1, "IS_EDC": False,"PinMap":Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),},
        "BILBO": {"Bypass": -1, "IS_EDC": False},
        "TRUNKDBG": {"Bypass": -1, "IS_EDC": False},
    }
    VMAX_F1_Tests = get_test_vmax(VMAX_F1_Flow, VMAX_F1_Corner, VMAX_F1_FlowMatrix, VMAX_Subflow, VMAX_F1_content_list)

    VMAX_F5_Flow = "VMAX"
    VMAX_F5_Corner = "F5"
    VMAX_F5_FlowMatrix = "AT_F5_FREQ"
    VMAX_F5_CornerID = "AT_C5"
    VMAX_F5_Subflow = "VMAXXAT"
    VMAX_F5_content_list = {
        "L2_DRAGON": {"Bypass": -1, "IS_EDC": False ,"PinMap":Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),},
        "L2_LOCKSTEP": {"Bypass": -1, "IS_EDC": False,"PinMap":Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),},
        "BILBO": {"Bypass": -1, "IS_EDC": False},
        "TRUNKDBG": {"Bypass": -1, "IS_EDC": False},
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
        "L2_DRAGON": {"Bypass": 1, "IS_EDC": True ,"PinMap":Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_dragon_freq'),},
        "L2_LOCKSTEP": {"Bypass": 1, "IS_EDC": True,"PinMap":Spec(f'FUN_ATOM_CXPKGS9_Specs.recov_pinmap_l2_lockstep_freq'),},
        "BILBO": {"Bypass": 1, "IS_EDC": True},
        "TRUNKDBG": {"Bypass": 1, "IS_EDC": True},
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
    VMAXXATCCF_content_list = {
        "SLC_DRAGON": {"Bypass": -1, "IS_EDC": False},
    }
    # Add screen test as the first test for VMAXXATCCF subflow (only if not LO)
    if "LO" not in VMAXXATCCF_Subflow:
        VMAXXATCCF_screen_test = ScreenTC(
            name="SBFT_CCF_SCREEN_X_VMAXXATCCF_X_X_X_X_CCF_SCREEN_C1_SLC_DRAGON",
            ScreenTestSet="FUN_ATOM_SCREEN_SingleFlow",
            ScreenTestsFile="./InputFiles/SBFT_ATOM_Downsku_screen.txt",
            BypassPort=Spec(VMAXXATCCF_content_list["SLC_DRAGON"].get("Bypass", -1)),
            _fitem=Fitem(
                "SAME",
                edc=VMAXXATCCF_content_list["SLC_DRAGON"].get("IS_EDC", True),
                r0=pFail(setbin=4555),
                r1=pPass(goto="NEXT"),
                r2=pPass(goto="NEXT"),
            ),
        )
        VMAXXATCCF_F1_Tests = get_test_vmax(VMAXXATCCF_F1_Flow, VMAXXATCCF_F1_Corner, VMAXXATCCF_F1_FlowMatrix, VMAXXATCCF_Subflow, VMAXXATCCF_content_list)
        VMAXXATCCF_F5_Tests = get_test_listvmaxf5(VMAXXATCCF_F1_Flow, VMAXXATCCF_F5_Corner, VMAXXATCCF_F5_FlowMatrix, VMAXXATCCF_F5_CornerID, VMAXXATCCF_Subflow, VMAXXATCCF_content_list)
        VMAXXATCCF_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXATCCF", VMAXXATCCF_screen_test, VMAXXATCCF_F1_Tests, VMAXXATCCF_F5_Tests)
    else:
        VMAXXATCCF_F1_Tests = get_test_vmax(VMAXXATCCF_F1_Flow, VMAXXATCCF_F1_Corner, VMAXXATCCF_F1_FlowMatrix, VMAXXATCCF_Subflow, VMAXXATCCF_content_list)
        VMAXXATCCF_F5_Tests = get_test_listvmaxf5(VMAXXATCCF_F1_Flow, VMAXXATCCF_F5_Corner, VMAXXATCCF_F5_FlowMatrix, VMAXXATCCF_F5_CornerID, VMAXXATCCF_Subflow, VMAXXATCCF_content_list)
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
        "SLC_DRAGON": {"Bypass": 1, "IS_EDC": True},
    }

    # Do not add screen test for LO subflow
    VMAXXATCCFLO_F1_Tests = get_test_vmax(VMAXXATCCFLO_F1_Flow, VMAXXATCCFLO_F1_Corner, VMAXXATCCFLO_F1_FlowMatrix, VMAXXATCCFLO_Subflow, VMAXXATCCFLO_content_list)
    VMAXXATCCFLO_F5_Tests = get_test_listvmaxf5(VMAXXATCCFLO_F1_Flow, VMAXXATCCFLO_F5_Corner, VMAXXATCCFLO_F5_FlowMatrix, VMAXXATCCFLO_F5_CornerID, VMAXXATCCFLO_Subflow, VMAXXATCCFLO_content_list)
    VMAXXATCCFLO_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXATCCFLO", VMAXXATCCFLO_F1_Tests, VMAXXATCCFLO_F5_Tests)
    #VMAX_Subflow = Flow(f"FUN_ATOM_{sku}_VMAXXAT")