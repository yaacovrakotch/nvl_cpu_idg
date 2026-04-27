#Owner: smohmady
#Import the necessary classes from Pymtpl
from pymtpl.por_methods import RunCallback, AuxiliaryTC, DieRecoveryBase, ScreenTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeMTL, Import, TrialParamSpec, Spec, ModuleFlow, InitializeNVLClass

# Initialize the module by defining the output mtpl path and module name
InitializeNVLClass('TPI_DIERCVRY_CXX', 'TPI_DIERCVRY_CXX', binrange=(9310, 9310),
														   defaultrm2bin = (99932000, 99933999),               
														   defaultrm1bin = (98932000, 98933999))

# Add the necessary files to import in your mtpl
Import("TPI_DIERCVRY_CXX.usrv")

DIERCVRY_Bin = 9310

# List of subflows
subflow =["INIT", "BEGINCPU", "ENDCPUPKG"]

#### INIT Flow Tests START ####

INIT_DIERCVRY = DieRecoveryBase(
    name = f"CTRL_X_PRIMEDIERECOVERY_K_{subflow[0]}_X_X_X_X_X",
    LogLevel = "Disabled",
    EnablePreTestCheck = "False",
    RulesFile = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C("./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_S28C.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_S52C.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_HX28C.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_P16C.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_S16C.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_S28C.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_U8C.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecovery_Rules_H16C.json")'),
    SKUFile = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_JF/MODULE/IA_ATOM_Recovery_28C.xml","./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_JF/MODULE/IA_ATOM_Recovery_52C.xml","./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_PG/MB/MODULE/IA_ATOM_Recovery_28C.xml","./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_BA/MODULE/IA_ATOM_Recovery_16C.xml","./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_PG/DT/MODULE/IA_ATOM_Recovery_16C.xml","./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_PG/DT/MODULE/IA_ATOM_Recovery_28C.xml","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/IA_ATOM_Recovery_8C.xml","./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_IDC/NVL_H16C/MODULE/IA_ATOM_Recovery_16C.xml")'),
	TrackerFile = Spec('__shared__::TpRule.If_48("./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecoveryTrackers_NVL_C48.json", __shared__::TpRule.If_C40("./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecoveryTrackers_NVL_C40.json","./Modules/TPI/TPI_DIERCVRY_CXX/InputFiles/DieRecoveryTrackers_NVL.json"))'),
    AllowDefeatures = Spec('TPI_DIERCVRY_CXX_Rules.RecoveryBypass("False","True","True","False","False")'),
    SaveHistory = "True",
	_fitem = Fitem('SAME', r0 = pFail(ret = 0),
                           r1 = pPass(ret = 1), 
						)
)

#### INIT Flow Tests END ####

#### BEGINCPU Flow Tests START ####

# Test for screentest to check TPREV condition and reverse the tracker

REVERSEDFF = ScreenTC(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_REVERSEDFF",
                    BypassPort = Spec('__shared__::TpRule.If_48_40(1,-1)'),
					ScreenTestSet = "SetDFF2GSDS",
					ScreenTestsFile = "./InputFiles/TPI_DIERCVRY_CXX_ScreenTest.txt",
					PostInstance = "PrintToItuff(--body_type strgval --body_data G.I.S.REVERTCOREREC)",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_CORE0TOTRACKER"),
											r2 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_CORE0TOTRACKERGSDS"),
                                            r3 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

#U1.U6
REVERSEDFF2CDIE = ScreenTC(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_REVERSEDFF2CDIE",
					BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_S52C(-1,1)'),
					ScreenTestSet = Spec('__shared__::TpRule.If_CLASS_NVL_S52C("SetDFF2GSDS_2CDIE","SetDFF2GSDS")'),
					ScreenTestsFile = "./InputFiles/TPI_DIERCVRY_CXX_ScreenTest.txt",
					PostInstance = Spec('__shared__::TpRule.If_CLASS_NVL_S52C("PrintToItuff(--body_type strgval --body_data G.I.S.REVERTCOREREC1)","PrintToItuff(--body_type strgval --body_data G.I.S.REVERTCOREREC)")'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_CORE1TOTRACKER"),
											r2 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_CORE1TOTRACKERGSDS"),
                                            r3 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# End of screentest

# 1CDIE Core0 to tracker
CORE0TOTRACKER = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_CORE0TOTRACKER",
					Callback = "WriteTracker",
					Parameters = Spec('__shared__::TpRule.If_48_40(TPI_DIERCVRY_CXX::BEG_CORE0TOTRACKER.C48_40_Tracker,TPI_DIERCVRY_CXX::BEG_CORE0TOTRACKER.C816_Tracker)'),
					ResultPort = "[R]=='PASS'?1:0",
					PostInstance = Spec('__shared__::TpRule.If_48_40("CopyTracker(--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR3,CR2,CR1,CR0 --gsds G.I.S.CRINIT)","CopyTracker(--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --gsds G.I.S.CRINIT)")'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_REVERSEDFF2CDIE"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# 2CDIE Core1 to tracker
CORE1TOTRACKER = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_CORE1TOTRACKER",
					Callback = "WriteTracker",
					Parameters = Spec('TPI_DIERCVRY_CXX_Rules.RecoveryRule("--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --dff "+__shared__::DFFVars.DIEID_CPU1+":SORT:COREREC","--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --dff "+__shared__::DFFVars.DIEID_CPU1+":SORT:COREREC","--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --dff "+__shared__::DFFVars.DIEID_CPU1+":RC_S1:COREREC","--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --dff "+__shared__::DFFVars.DIEID_CPU1+":PBIC_DAB:COREREC")'),
					ResultPort = "[R]=='PASS'?1:0",
					PostInstance = "CopyTracker(--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B,ACRM3,ACRM2,ACRM1,ACRM0,CR --gsds G.I.S.CRINIT)",
                    BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_S52C(-1,1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_SLICE0TOTRACKER"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# CORETORACKER GSDS
# 1CDIE Core0 to tracker
CORE0TOTRACKERGSDS = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_CORE0TOTRACKERGSDS",
                    BypassPort = Spec('__shared__::TpRule.If_48_40(1,-1)'),
					Callback = "WriteTracker",
					Parameters = Spec('TPI_DIERCVRY_CXX_Rules.RecoveryRule("--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --gsds G.I.S.REVERTCOREREC","--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --gsds G.I.S.REVERTCOREREC","--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --dff "+__shared__::DFFVars.DIEID_CPU+":RC_S1:COREREC","--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --dff "+__shared__::DFFVars.DIEID_CPU+":PBIC_DAB:COREREC")'),
					ResultPort = "[R]=='PASS'?1:0",
					PostInstance = "CopyTracker(--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --gsds G.I.S.CRINIT)",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_REVERSEDFF2CDIE"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# CORETORACKER GSDS
# 2CDIE Core0 to tracker
CORE1TOTRACKERGSDS = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_CORE1TOTRACKERGSDS",
					Callback = "WriteTracker",
					Parameters = Spec('TPI_DIERCVRY_CXX_Rules.RecoveryRule("--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --gsds G.I.S.REVERTCOREREC1","--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --gsds G.I.S.REVERTCOREREC1","--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --dff "+__shared__::DFFVars.DIEID_CPU1+":RC_S1:COREREC","--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --dff "+__shared__::DFFVars.DIEID_CPU1+":PBIC_DAB:COREREC")'),
					ResultPort = "[R]=='PASS'?1:0",
					PostInstance = "CopyTracker(--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B,ACRM3,ACRM2,ACRM1,ACRM0,CR --gsds G.I.S.CRINIT)",
                    BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_S52C(-1,1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_SLICE0TOTRACKER"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# END OF REVERSE DFF

# 1CDIE Slice0 to tracker
SLICE0TOTRACKER = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_SLICE0TOTRACKER",
					Callback = "WriteTracker",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.S28C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.S52C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.HX28C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.P16C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.S16C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.DNLS28C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.U8C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICE0TOTRACKER.H16C_Tracker)'),
					ResultPort = "[R]=='PASS'?1:0",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_SLICE1TOTRACKER"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# 2CDIE Slice1 to tracker
SLICE1TOTRACKER = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_SLICE1TOTRACKER",
					Callback = "WriteTracker",
					Parameters = Spec('TPI_DIERCVRY_CXX_Rules.RecoveryRule("--tracker SLC11_B,SLC10_B,SLC9_B,SLC8_B,SLC7_B,SLC6_B,SLC5_B,SLC4_B,SLC3_B,SLC2_B,SLC1_B,SLC0_B --dff "+__shared__::DFFVars.DIEID_CPU1+":SORT:SLICEREC  --rule CLASS_NVL_S52C_12C","--tracker SLC11_B,SLC10_B,SLC9_B,SLC8_B,SLC7_B,SLC6_B,SLC5_B,SLC4_B,SLC3_B,SLC2_B,SLC1_B,SLC0_B --dff "+__shared__::DFFVars.DIEID_CPU1+":SORT:SLICEREC  --rule CLASS_NVL_S52C_12C","--tracker SLC11_B,SLC10_B,SLC9_B,SLC8_B,SLC7_B,SLC6_B,SLC5_B,SLC4_B,SLC3_B,SLC2_B,SLC1_B,SLC0_B --dff "+__shared__::DFFVars.DIEID_CPU1+":RC_S1:SLICEREC  --rule CLASS_NVL_S52C_12C","--tracker SLC11_B,SLC10_B,SLC9_B,SLC8_B,SLC7_B,SLC6_B,SLC5_B,SLC4_B,SLC3_B,SLC2_B,SLC1_B,SLC0_B --dff "+__shared__::DFFVars.DIEID_CPU1+":PBIC_DAB:SLICEREC  --rule CLASS_NVL_S52C_12C")'),
					ResultPort = "[R]=='PASS'?1:0",
                    BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_S52C(-1,1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_BEGINCPU_X_X_X_X_SLICETOTRACKERGSDS"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

SLICETOTRACKERGSDS = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_SLICETOTRACKERGSDS",
					Callback = "CopyTracker",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.S28C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.S52C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.HX28C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.P16C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.S16C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.DNLS28C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.U8C_Tracker,TPI_DIERCVRY_CXX::BEG_SLICETOTRACKERGSDS.H16C_Tracker)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_BEGINCPU_X_X_X_X_PNC_CORECHECK"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

#### BEGINCPU CORECHECK Flow Tests START ####

PNC_CORECHECK = RunCallback(
					name = f"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_PNC_CORECHECK",
					Callback = "RunRule",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::CR_RULE.S28C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.S52C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.HX28C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.P16C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.S16C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.DNLS28C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.U8C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.H16C_CR_Rule)'),
                    ResultPort = "[R]=='PASS'?1:0",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_BEGINCPU_X_X_X_X_PNC_COREFLOW"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# MTT test PNC_COREFLOW
PNC_COREFLOW = NativeMultiTrial(
					name = f"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_PNC_COREFLOW",
                    trialvar = f"CPU_TRIALS::FlowDomain.CORE",
                    template = RunCallback(
                                name = f'"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_PNC_COREFLOW_" + __shared__::FlowMatrix.bin',
                                Callback = "RunRule",
                                ResultPort = "[R]=='PASS'?1:0",
                                Parameters = TrialParamSpec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C("--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR_B,CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C")')
                                ),
                    r0 = pFail(setbin = DIERCVRY_Bin, ret = 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                    r1 = pPass(trialaction = f'Exit'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_BEGINCPU_X_X_X_X_SLICECHECK"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

#### BEGINCPU CORECHECK Flow Tests END ####


#### BEGINCPU SLICECHECK Flow Tests START ####

SLICECHECK = RunCallback(
					name = f"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_SLICECHECK",
					Callback = "RunRule",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::SLC_RULE.S28C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.S52C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.HX28C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.P16C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.S16C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.DNLS28C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.U8C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.H16C_SLC_Rule)'),
                    ResultPort = "[R]=='PASS'?1:0",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_BEGINCPU_X_X_X_X_SLICEFLOW"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# MTT test SLICEFLOW
SLICEFLOW = NativeMultiTrial(
					name = f"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_SLICEFLOW",
                    trialvar = f"CPU_TRIALS::FlowDomain.RING",
                    template = RunCallback(
                                name = f'"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_SLICEFLOW_" + __shared__::FlowMatrix.bin',
                                Callback = "RunRule",
                                ResultPort = "[R]=='PASS'?1:0",
                                Parameters = TrialParamSpec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C("--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR_B,CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C")')
                                ),
                    r0 = pFail(setbin = DIERCVRY_Bin, ret = 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                    r1 = pPass(trialaction = f'Exit'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_BEGINCPU_X_X_X_X_ARW_CORECHECK"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

#### BEGINCPU SLICECHECK Flow Tests END ####


#### BEGINCPU ARWCHECK Flow Tests START ####

ARW_CORECHECK = RunCallback(
					name = f"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_ARW_CORECHECK",
					Callback = "RunRule",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::ACRM_RULE.S28C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.S52C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.HX28C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.P16C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.S16C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.DNLS28C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.U8C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.H16C_ACRM_Rule)'),
                    ResultPort = "[R]=='PASS'?1:0",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_BEGINCPU_X_X_X_X_ARW_CORE0FLOW"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# MTT test ARW_CORE0FLOW
ARW_CORE0FLOW = NativeMultiTrial(
					name = f"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_ARW_CORE0FLOW",
                    trialvar = f"CPU_TRIALS::FlowDomain.ATOM",
                    template = RunCallback(
                                name = f'"DIERCVRY_X_AUX_K_{subflow[1]}_X_X_X_X_ARW_CORE0FLOW_" + __shared__::FlowMatrix.bin',
                                Callback = "RunRule",
                                #PostInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")',
                                ResultPort = "[R]=='PASS'?1:0",
                                Parameters = TrialParamSpec('__shared__::TpRule.If_CLASS_NVL_S52C("--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,ACRM3,ACRM2,ACRM1,ACRM0 --rule " +__shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.ATOMC_CORE_SELECT + "A","--tracker ACRM3,ACRM2,ACRM1,ACRM0 --rule " +__shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.ATOMC_CORE_SELECT + "A")')
                                ),
                    r0 = pFail(setbin = DIERCVRY_Bin, ret = 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                    r1 = pPass(trialaction = f'Exit'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											#r1 = pPass(goto = "DIERCVRY_X_AUX_K_BEGINCPU_X_X_X_X_ARW_CORE1FLOW"),
											r1 = pPass(ret = 1),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

#### BEGINCPU Flow Tests END ####


#### ENDCPU Flow Tests START ####

PNC_CORECHECKFIN = RunCallback(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_PNC_CORECHECKFIN",
					Callback = "RunRule",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::CR_RULE.S28C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.S52C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.HX28C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.P16C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.S16C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.DNLS28C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.U8C_CR_Rule,TPI_DIERCVRY_CXX::CR_RULE.H16C_CR_Rule)'),
                    ResultPort = "[R]=='PASS'?1:0",
                    PostInstance = "LogTrackerHistory()",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_ENDCPUPKG_X_X_X_X_PNC_COREFLOW"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# MTT test END_PNC_COREFLOW
END_PNC_COREFLOW = NativeMultiTrial(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_PNC_COREFLOW",
                    trialvar = f"CPU_TRIALS::FlowDomain.CORE",
                    template = RunCallback(
                                name = f'"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_PNC_COREFLOW_" + __shared__::FlowMatrix.bin',
                                Callback = "RunRule",
                                ResultPort = "[R]=='PASS'?1:0",
                                Parameters = TrialParamSpec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C("--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR_B,CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C")')
                                ),
                    r0 = pFail(setbin = DIERCVRY_Bin, ret = 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                    r1 = pPass(trialaction = f'Exit', ret = 1),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_ENDCPUPKG_X_X_X_X_SLICECHECKFIN"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

SLICECHECKFIN = RunCallback(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_SLICECHECKFIN",
					Callback = "RunRule",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::SLC_RULE.S28C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.S52C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.HX28C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.P16C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.S16C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.DNLS28C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.U8C_SLC_Rule,TPI_DIERCVRY_CXX::SLC_RULE.H16C_SLC_Rule)'),
                    ResultPort = "[R]=='PASS'?1:0",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_ENDCPUPKG_X_X_X_X_SLICEFLOW"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

# MTT test END_SLICEFLOW
END_SLICEFLOW = NativeMultiTrial(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_SLICEFLOW",
                    trialvar = f"CPU_TRIALS::FlowDomain.RING",
                    template = RunCallback(
                                name = f'"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_SLICEFLOW_" + __shared__::FlowMatrix.bin',
                                Callback = "RunRule",
                                ResultPort = "[R]=='PASS'?1:0",
                                Parameters = TrialParamSpec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C("--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR_B,CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C","--tracker CR3,CR2,CR1,CR0 --rule " + __shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.BIGCORE_CORE_SELECT + "C")')
                                ),
                    r0 = pFail(setbin = DIERCVRY_Bin, ret = 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                    r1 = pPass(trialaction = f'Exit', ret = 1),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_ENDCPUPKG_X_X_X_X_ARW_CORECHECKFIN"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

ARW_CORECHECKFIN = RunCallback(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_ARW_CORECHECKFIN",
					Callback = "RunRule",
					Parameters = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::ACRM_RULE.S28C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.S52C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.HX28C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.P16C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.S16C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.DNLS28C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.U8C_ACRM_Rule,TPI_DIERCVRY_CXX::ACRM_RULE.H16C_ACRM_Rule)'),
                    ResultPort = "[R]=='PASS'?1:0",
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_ENDCPUPKG_X_X_X_X_ARW_CORE0FLOW"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

END_ARW_CORE0FLOW = NativeMultiTrial(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_ARW_CORE0FLOW",
                    trialvar = f"CPU_TRIALS::FlowDomain.ATOM",
                    template = RunCallback(
                                name = f'"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_ARW_CORE0FLOW_" + __shared__::FlowMatrix.bin',
                                Callback = "RunRule",
                                #PostInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")',
                                ResultPort = "[R]=='PASS'?1:0",
                                Parameters = TrialParamSpec('__shared__::TpRule.If_CLASS_NVL_S52C("--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,ACRM3,ACRM2,ACRM1,ACRM0 --rule " +__shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.ATOMC_CORE_SELECT + "A","--tracker ACRM3,ACRM2,ACRM1,ACRM0 --rule " +__shared__::FlowMatrix.BomGroupName + "_" + __shared__::FlowMatrix.ATOMC_CORE_SELECT + "A")')
                                ),
                    r0 = pFail(setbin = DIERCVRY_Bin, ret = 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                    r1 = pPass(trialaction = f'Exit'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_ENDCPUPKG_X_X_X_X_CRFININITCHK"),
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

CRFININITCHK = AuxiliaryTC(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_CRFININITCHK",
                    DataType = "String",
                    Expression = "[G.I.S.CRINIT] == [G.I.S.CRFIN]",
                    PreInstance = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::CRFININITCHK.S28C_ACRMCR_FININIT,TPI_DIERCVRY_CXX::CRFININITCHK.S52C_ACRMCR_FININIT,TPI_DIERCVRY_CXX::CRFININITCHK.HX28C_ACRMCR_FININIT,TPI_DIERCVRY_CXX::CRFININITCHK.P16C_ACRMCR_FININIT,TPI_DIERCVRY_CXX::CRFININITCHK.S16C_ACRMCR_FININIT,TPI_DIERCVRY_CXX::CRFININITCHK.DNLS28C_ACRMCR_FININIT,TPI_DIERCVRY_CXX::CRFININITCHK.U8C_ACRMCR_FININIT,TPI_DIERCVRY_CXX::CRFININITCHK.H16C_ACRMCR_FININIT)'),
                    ResultPort = "[R]=='True'?1:2",
                    BypassPort = Spec('TPI_DIERCVRY_CXX_Rules.RecoveryBypass(-1,1,1,-1,-1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_AUX_K_ENDCPUPKG_X_X_X_X_SLCFININITCHK"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

SLCFININITCHK = AuxiliaryTC(
					name = f"DIERCVRY_X_AUX_K_{subflow[2]}_X_X_X_X_SLCFININITCHK",
                    DataType = "String",
                    Expression = "[G.I.S.SLCINIT] == [G.I.S.SLCFIN]",
                    PreInstance = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::SLCFININITCHK.S28C_SLC_FININIT,TPI_DIERCVRY_CXX::SLCFININITCHK.S52C_SLC_FININIT,TPI_DIERCVRY_CXX::SLCFININITCHK.HX28C_SLC_FININIT,TPI_DIERCVRY_CXX::SLCFININITCHK.P16C_SLC_FININIT,TPI_DIERCVRY_CXX::SLCFININITCHK.S16C_SLC_FININIT,TPI_DIERCVRY_CXX::SLCFININITCHK.DNLS28C_SLC_FININIT,TPI_DIERCVRY_CXX::SLCFININITCHK.U8C_SLC_FININIT,TPI_DIERCVRY_CXX::SLCFININITCHK.H16C_SLC_FININIT)'),
                    ResultPort = "[R]=='True'?1:2",
                    BypassPort = Spec('TPI_DIERCVRY_CXX_Rules.RecoveryBypass(-1,1,1,-1,-1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_ENDCPUPKG_X_X_X_X_TRACKERTOCORE1"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

END_TRACKERTOCORE0 = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[2]}_X_X_X_X_TRACKERTOCORE0",
					Callback = "CopyTracker",
					#PreInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', #will enable this if with real unit it fail to set theh dieid
					Parameters = Spec('__shared__::TpRule.If_48_40("--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR3,CR2,CR1,CR0 --dff "+__shared__::DFFVars.DIEID_CPU+":COREREC","--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --dff "+__shared__::DFFVars.DIEID_CPU+":COREREC")'),
                    BypassPort = Spec('TPI_DIERCVRY_CXX_Rules.Tracker_Bypass(-1,-1,1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_ENDCPUPKG_X_X_X_X_TRACKERTOSLICE0"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

END_TRACKERTOCORE1 = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[2]}_X_X_X_X_TRACKERTOCORE1",
					Callback = "CopyTracker",
					#PreInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU1+")', #will enable this if with real unit it fail to set theh dieid
					Parameters = Spec('"--tracker ACRM3_B,ACRM2_B,ACRM1_B,ACRM0_B,CR_B --dff "+__shared__::DFFVars.DIEID_CPU1+":COREREC"'),
                    BypassPort = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(1,TPI_DIERCVRY_CXX_Rules.Tracker_Bypass(-1,-1,1),1,1,1,1,1,1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_ENDCPUPKG_X_X_X_X_TRACKERTOSLICE1"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

END_TRACKERTOSLICE0 = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[2]}_X_X_X_X_TRACKERTOSLICE0",
					Callback = "CopyTracker",
					Parameters = Spec('"--tracker SLC11,SLC10,SLC9,SLC8,SLC7,SLC6,SLC5,SLC4,SLC3,SLC2,SLC1,SLC0 --dff "+__shared__::DFFVars.DIEID_CPU+":SLICEREC"'),
                    PostInstance = "Call(LogTrackerHistory()|LogVminForwardTableToItuff())",
					BypassPort = Spec('TPI_DIERCVRY_CXX_Rules.Tracker_Bypass(-1,-1,1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "CTRL_X_RUNCALLBACK_K_ENDCPUPKG_X_X_X_X_PRINTTOITUFF_SLICE"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

END_TRACKERTOSLICE1 = RunCallback(
					name = f"DIERCVRY_X_FUNC_K_{subflow[2]}_X_X_X_X_TRACKERTOSLICE1",
					Callback = "CopyTracker",
					Parameters = Spec('"--tracker SLC11_B,SLC10_B,SLC9_B,SLC8_B,SLC7_B,SLC6_B,SLC5_B,SLC4_B,SLC3_B,SLC2_B,SLC1_B,SLC0_B --dff "+__shared__::DFFVars.DIEID_CPU1+":SLICEREC"'),
                    BypassPort = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(1,TPI_DIERCVRY_CXX_Rules.Tracker_Bypass(-1,-1,1),1,1,1,1,1,1)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "DIERCVRY_X_FUNC_K_ENDCPUPKG_X_X_X_X_TRACKERTOCORE0"),
                                            r2 = pFail(setbin = DIERCVRY_Bin, ret = 0)
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

PRINTTOITUFF_SLICE = RunCallback(
					name = f"CTRL_X_RUNCALLBACK_K_{subflow[2]}_X_X_X_X_PRINTTOITUFF_SLICE",
					Callback = "PrintToItuff",
					Parameters = Spec('"--body_type strgval --body_data G.I.S.SLCITUFF --tname_suf _SLICEREC_String"'),
                    PreInstance = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.S28C_SLC_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.S52C_SLC_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.HX28C_SLC_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.P16C_SLC_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.S16C_SLC_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.DNLS28C_SLC_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.U8C_SLC_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_SLICE.H16C_SLC_ITUFF)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(goto = "CTRL_X_RUNCALLBACK_K_ENDCPUPKG_X_X_X_X_PRINTTOITUFF_CORE")
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0))
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

PRINTTOITUFF_CORE = RunCallback(
					name = f"CTRL_X_RUNCALLBACK_K_{subflow[2]}_X_X_X_X_PRINTTOITUFF_CORE",
					Callback = "PrintToItuff",
					Parameters = Spec('"--body_type strgval --body_data G.I.S.COREITUFF --tname_suf _COREREC_String"'),
                    PreInstance = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C_U8C(TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.S28C_ACRMCR_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.S52C_ACRMCR_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.HX28C_ACRMCR_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.P16C_ACRMCR_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.S16C_ACRMCR_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.DNLS28C_ACRMCR_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.U8C_ACRMCR_ITUFF,TPI_DIERCVRY_CXX::PRINTTOITUFF_CORE.H16C_ACRMCR_ITUFF)'),
					_fitem = Fitem('SAME', r0 = pFail(setbin = DIERCVRY_Bin, ret = 0),
											r1 = pPass(ret = 1)
                                            #r2 = pFail(setbin = DIERCVRY_Bin, ret = 0))
											)											
					)		
DIERCVRY_Bin = DIERCVRY_Bin + 1

#### ENDCPU Flow Tests END ####

# Call your test in a DUTFlow
subflow =["INIT", "BEGINCPU", "ENDCPU"]
INIT_Subflow = Flow('TPI_DIERCVRY_CXX_INIT', INIT_DIERCVRY)
BEGINCPU_Subflow = Flow('TPI_DIERCVRY_CXX_BEGINCPU', REVERSEDFF, REVERSEDFF2CDIE, CORE0TOTRACKER, CORE1TOTRACKER, CORE0TOTRACKERGSDS, CORE1TOTRACKERGSDS, SLICE0TOTRACKER, SLICE1TOTRACKER, SLICETOTRACKERGSDS, PNC_CORECHECK, PNC_COREFLOW, SLICECHECK, SLICEFLOW, ARW_CORECHECK, ARW_CORE0FLOW)
ENDCPUPKG_Subflow = Flow('TPI_DIERCVRY_CXX_ENDCPUPKG', PNC_CORECHECKFIN, END_PNC_COREFLOW, SLICECHECKFIN, END_SLICEFLOW, ARW_CORECHECKFIN, END_ARW_CORE0FLOW, CRFININITCHK, SLCFININITCHK, END_TRACKERTOCORE1, END_TRACKERTOSLICE1, END_TRACKERTOCORE0, END_TRACKERTOSLICE0, PRINTTOITUFF_SLICE, PRINTTOITUFF_CORE)
