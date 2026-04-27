# PKG TPI_DFF Module pymtpl source code.
# Output for prime13 and TOS4.
from email.policy import default
from pymtpl.por_methods import PrimeDffEndOfFlowValidationTestMethod, PrimeDffReadTestMethod, ULTLoggerTC, AuxiliaryTC, ScreenTC
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

##############################################################################################
# UPDATED by Skorlam on 12/30/2025 - To help with move to new Sort like binning at class.
##############################################################################################

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./TPI_DFF_XXX',  'TPI_DFF_XXX', tosversion="tos4", binrange=[(5300, 5310), (9401, 9410)],
                   defaultrm2bin = [(99530500, 99531999), (99940500, 99941999)],
                   defaultrm1bin=[(98530500, 98531999), (98940500, 98941999)])

# Define import header
Import("TPI_DFF_XXX.usrv")

# Define the subflow where the module place at.
subflw = "STARTPREPRL1"
subflw_fin = "FINAL"
#Additional test to switch MTL file and SSID assignment in INIT, moved from TPI_BASE to TPI_DFF

# Define Test Instance and Flowitems for FINAL subflow 
reject_fork= ScreenTC(
    name = f"CTRL_X_SCREEN_K_{subflw_fin}_X_X_X_X_REJECTFORK",
    _comment = """Additional test to switch MTL file and SSID assignment in INIT, moved from TPI_BASE to TPI_DFF improvement: experiment on not having a fork for both KILL/NON-KILL and passing/failing, might need to takeout of TPI_DFF""",
    ScreenTestSet = "RejectFork",
    PreInstance = "EvaluateExpression(--expression GetCurrentSoftBin() --result G.U.S.CurrentSoftBin)",
    PostInstance = "PrintToItuff(--body_type strgval --body_data G.U.S.CurrentSoftBin --tname_suf _CurrentSoftBin)",
	ScreenTestsFile = Spec('"../../../../Shared/BaseInputs/Common/Common_Files/ScreenTest_TP_Knob.txt"'),
    _fitem = Fitem('SAME', r0=pFail(setbin=-94, ret = 0), r2=pPass(ret=2), r3=pFail(setbin=-94, ret = 0), r4=pFail(setbin=-94, ret = 0), r5=pFail(setbin=-94, ret = 0), r6=pFail(setbin=-94, ret = 0), r7=pFail(setbin=-94, ret = 0))
    )

######### Tests not related to DFF and transferred to TPI_BASE ##############
##b69_flag= AuxiliaryTC(
#    name = f"CTRL_X_AUX_K_{subflw_fin}_X_X_X_X_CHK1SET2",
#    _comment = "improvement: b69_flag move out of TPI_DFF since not related to DFF",
#    Expression = "[__shared__::TP_KNOB.Bin69_FLG] + 1",
#    ResultPort = "[R]==2?1:2",
#    Storage = "UserVar",
#    ResultToken = "__shared__::TP_KNOB.Bin69_FLG",
#    DataType = "Integer",
#    _fitem = Fitem('SAME', r0=pFail(setbin=6905, ret = 0), r2=pFail(setbin=6905, ret = 0))                       
#    )
#
#inline_rv= ScreenTC(
#    name = f"CTRL_X_SCREEN_K_{subflw_fin}_X_X_X_X_INLINERV",
#    _comment = "improvement: inlinerv move out of TPI_DFF since not related to DFF",
#    ScreenTestSet = "INLINERVREBIN",
#    ScreenTestsFile = "./InputFiles/TPI_DFF_XXX_ScreenTest.txt",
#    _fitem = Fitem('SAME', r0=pFail(setbin=-94, ret = 0), r2=pFail(setbin=-94, ret = 0), r3=pFail(setbin=8030, ret = 0), r4=pFail(setbin=8040, ret = 0), r5=pFail(setbin=8050, ret = 0), r6=pFail(setbin=8020, ret = 0), r7=pFail(setbin=8080, ret = 0))               
#    )

dffval = PrimeDffEndOfFlowValidationTestMethod(
    name = f"DFFX_X_DFFENDFLOW_K_{subflw_fin}_X_X_X_X_DFFVAL",
    LogLevel = "Disabled",
    BypassPort = Spec('TPI_DFF_XXX_Rules.DFFX_X_DFFENDFLOW_K_FINAL_X_X_X_X_DFFVAL_BypassPort(1,-1,-1,1)'),
    _fitem = Fitem('SAME', rm2 = pFail(setbin=9953), rm1 = pFail(setbin=9853), r0=pFail(setbin=5304, ret = 0))
    )

# Define Test Instance and Flowitems for START subflow

######### Tests not related to DFF and transferred to TPI_BASE ##############
#cse_token= ScreenTC(
#    name = f"CTRL_X_SCREEN_K_{subflw}_X_X_X_X_CSETOKEN",
#    _comment = "Review if this the proper module for this test",
#    ScreenTestSet = Spec('TPI_DFF_XXX_Rules.CTRL_X_SCREEN_K_START_X_X_X_X_CSETOKEN_screen_test_set_bypass_global("SetCSECCDFF","SetCSECCDFFRC","SetCSEPCDFF","SetOLBCC","SetOLBCCRC","SetOLBPC","SetOLBPC","SetCSECCDFF")'),
#	ScreenTestsFile = "./InputFiles/ScreenTest_SetCSEDFF.txt",
#    BypassPort = Spec('TPI_DFF_XXX_Rules.CTRL_X_SCREEN_K_START_X_X_X_X_CSETOKEN_screen_test_set_bypass_global(-1, -1, -1, -1, -1, -1, -1, 1)'),
#    _fitem = Fitem('SAME', r0=pFail(setbin=-94, ret = 0), r2=pPass(ret = 1))                       
#    )
#
#fuse_tpname= ScreenTC(
#    name = f"CTRL_X_SCREEN_K_{subflw}_X_X_X_X_FUSETPNAME",
#    ScreenTestSet = Spec('TPI_DFF_XXX_Rules.CTRL_X_SCREEN_K_START_X_X_X_X_FUSETPNAME_screen_test_set("FUSE_SHORT_TP_NAME_RC","FUSE_SHORT_TP_NAME")'),
#	ScreenTestsFile = "./InputFiles/Fuse_TPName_Screentest.txt",
#    BypassPort = Spec('TPI_DFF_XXX_Rules.CTRL_X_SCREEN_K_START_X_X_X_X_FUSETPNAME_bypass_global(-1, -1, 1)'),
#    _fitem = Fitem('SAME', r0=pFail(setbin=-94, ret = 0), r2=pFail(setbin=-94, ret = 0), r3=pFail(setbin=-94, ret = 0))                       
#    )
#
#mps_skip= ScreenTC(
#    name = f"CTRL_X_SCREEN_K_{subflw}_X_X_X_X_MPSSKIPUNIT",
#    _comment = "Review if this the proper module for this test",
#    ScreenTestSet = Spec('TPI_DFF_XXX_Rules.CTRL_X_SCREEN_K_START_X_X_X_X_MPSSKIPUNIT_screen_test_set_bypass_global("SPBICS2","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SPBICS2")'),
#	ScreenTestsFile = "./InputFiles/MPS_Skip_Screen.txt",
#    BypassPort = Spec('TPI_DFF_XXX_Rules.CTRL_X_SCREEN_K_START_X_X_X_X_MPSSKIPUNIT_screen_test_set_bypass_global(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1)'),
#    _fitem = Fitem('SAME', r0=pFail(setbin=-94, ret = 0), r2=pFail(setbin=7299, ret = 0))                       
#    )

#Dummy ULT data for non-full TP
dummy_scr = ScreenTC(
    name = f"DFFX_X_SCREEN_K_{subflw}_X_X_X_X_DIESELCTDIE",
    ScreenTestSet = "DIESELECTDIE",
    ScreenTestsFile = "./InputFiles/Dummy_DieSelect.txt",
    _fitem = Fitem('SAME', rm2=pFail(setbin=9953, ret=-2), rm1=pFail(setbin=9853, ret=-1), r0 = pFail(setbin = 5307, ret = 0), r2=pFail(setbin=5307, ret = 0))
    )

dummy_ult = ULTLoggerTC(
    name = f"DFFX_X_PRIMEULT_K_{subflw}_X_X_X_X_DUMMYULT",
    DieId = Spec('__shared__::TpRule.If_CLASS_NVL_S52C(__shared__::DieIndic.DieCombo("NA", __shared__::DFFVars.DIEID_PCD,__shared__::DFFVars.DIEID_GPU, __shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+ __shared__::DFFVars.DIEID_CPU1, __shared__::DFFVars.DIEID_HUB+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+ __shared__::DFFVars.DIEID_CPU1+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_CPU+","+ __shared__::DFFVars.DIEID_CPU1+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+ __shared__::DFFVars.DIEID_CPU1+","+__shared__::DFFVars.DIEID_GPU, __shared__::DFFVars.DIEID_PCD+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+ __shared__::DFFVars.DIEID_CPU1+","+__shared__::DFFVars.DIEID_PCD+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+ __shared__::DFFVars.DIEID_CPU1+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_CPU+","+ __shared__::DFFVars.DIEID_CPU1+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_HUB, "NA"),(__shared__::DieIndic.DieCombo("NA", __shared__::DFFVars.DIEID_PCD,__shared__::DFFVars.DIEID_GPU, __shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU, __shared__::DFFVars.DIEID_HUB+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_GPU, __shared__::DFFVars.DIEID_PCD+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_PCD+","+__shared__::DFFVars.DIEID_HUB, __shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_PCD, __shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_HUB, "NA")))'),
    LogLevel = "Disabled",
    SetUltDataPerDieId = "ENABLED",
    ValueExpression = Spec('__shared__::TpRule.If_CLASS_NVL_S52C(__shared__::DieIndic.DieCombo("NA", __shared__::DFFVars.DIEID_PCD_IDENTIFIER,__shared__::DFFVars.DIEID_GPU_IDENTIFIER, __shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+ __shared__::DFFVars.DIEID_CPU1_IDENTIFIER, __shared__::DFFVars.DIEID_HUB_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+ __shared__::DFFVars.DIEID_CPU1_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+ __shared__::DFFVars.DIEID_CPU1_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+ __shared__::DFFVars.DIEID_CPU1_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER, __shared__::DFFVars.DIEID_PCD_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+ __shared__::DFFVars.DIEID_CPU1_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+ __shared__::DFFVars.DIEID_CPU1_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+ __shared__::DFFVars.DIEID_CPU1_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, "NA"),(__shared__::DieIndic.DieCombo("NA", __shared__::DFFVars.DIEID_PCD_IDENTIFIER,__shared__::DFFVars.DIEID_GPU_IDENTIFIER, __shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU, __shared__::DFFVars.DIEID_HUB_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER, __shared__::DFFVars.DIEID_PCD_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER, __shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER, "NA")))'),
    BypassPort = Spec('__shared__::DieIndic.DieCombo(1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)'),
    _fitem = Fitem('SAME', r0 = pFail(setbin = 5308, ret = 0))
    )

dffread= PrimeDffReadTestMethod(
    name = f"DFFX_X_DFFREAD_K_{subflw}_X_X_X_X_DFFREAD",
    EnabledModules = Spec('__shared__::TpRule.If_CLASS_NVL_S28C(__shared__::DieIndic.AllDie("NONKILL","NONKILL"),"NONKILL")'),
    _comment = 'for POR KILL setup switch EnabledModules = GlobalRule.If_ENGTP("NONKILL",TPI_DFF_XXX_Rules.DFFKILL("ALLKILL","ALLKILL","ALLKILL","NONKILL"))',
    _fitem = Fitem('SAME', r0=pFail(setbin=5301, ret = 0), r2=pFail(setbin=5302, ret = 0))                       
    )

ultlogger = ULTLoggerTC(
    name = f'DFFX_X_PRIMEULT_K_{subflw}_X_X_X_X_BASEULT',
    DieId = Spec('__shared__::DFFVars.DIEID_BASE'),
    LogLevel = "Disabled",
    SetUltDataPerDieId = "DISABLED",
    ValueExpression = Spec('__shared__::DFFVars.DIEID_BAS_IDENTIFIER'),
	BypassPort = Spec('TPI_DFF_XXX_Rules.If_P16C_Z0(1, TPI_DFF_XXX_Rules.BASEULT(1,-1,-1))'),
    _fitem = Fitem('SAME', r0=pFail(setbin=5306, ret = 0))
    )

# Define above tests in FINAL Flow
FINAL_Subflow = Flow(f'TPI_DFF_XXX_{subflw_fin}', reject_fork, dffval)

# Define above tests in START Flow
STARTPREPRL1_Subflow = Flow(f'TPI_DFF_XXX_{subflw}', dummy_scr, dummy_ult, ultlogger, dffread)

