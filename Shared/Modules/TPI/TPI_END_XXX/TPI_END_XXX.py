# PKG TPI END Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import PrimeInitializeInstancesTestMethod, RunCallback, UserCodeTC, AuxiliaryTC, PrimeDeviceEndDatalogTestMethod, PrimeOdeseBinConverterTestMethod, PrimeDeviceEndFinalizeTestMethod, ScreenTC, PrimePauseTestMethod
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

##############################################################################################
# UPDATED by Skorlam on 12/30/2025 - To help with move to new Sort like binning at class.
##############################################################################################

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./TPI_END_XXX',  'TPI_END_XXX', tosversion="tos4", binrange=(9307, 9307),
                    defaultrm2bin=[(99935500, 99935999), (99691000, 99691999)],
                    defaultrm1bin=[(98935500, 98935999), (98691000, 98691999)])

# Define import header
Import("TPI_END_XXX.usrv")

# Init Flow
subflow_init = "INIT"

Prime_Init = PrimeInitializeInstancesTestMethod(
    name = f"CTRL_X_PRIMEINIT_K_{subflow_init}_X_X_X_X_VERIFYALL", 
    VerifyAll = "True",
    PostInstance = "WriteUserVar(--uservar __shared__::SCVars.SC_TDRLOG --value -1 --type String)",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )

Init_Skp = RunCallback(
    name = f"CTRL_X_UF_K_{subflow_init}_X_X_X_X_INITSKIP", 
	Callback = "IsLongInitRequired",
	LogLevel = "Disabled",
	ResultPort = "[R]=='TRUE'?1:0",
    _fitem = Fitem('SAME', r0=pFail(goto='NEXT'))
    )

SaveInit_Info = RunCallback(
    name = f"CTRL_X_UF_K_{subflow_init}_X_X_X_X_SAVEINFO", 
	Callback = "SaveInitPassInformation",
	LogLevel = "Disabled",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )

Init_GSDS = RunCallback(
    name = f"CTRL_X_UF_K_{subflow_init}_X_X_X_X_SETINITGSDSPASS", 
   	Callback = "WriteSharedStorage",
	Parameters = "--token G.L.S.INITFLAG --value PASS",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )
    
# Define above tests in Init Flow
TPI_END_XXX_FLW1 = Flow(f'TPI_END_XXX_{subflow_init}',  Prime_Init, Init_Skp, SaveInit_Info, Init_GSDS)

# FACT Subflow Fork
Bin69_chk = AuxiliaryTC(
    name = "CTRL_X_AUX_K_FACT_X_X_X_X_CHK0SET1_END", 
	Expression = "[__shared__::TP_KNOB.Bin69_FLG] + 1",
	ResultPort = "[R]=1?1:2",
	ResultToken = "__shared__::TP_KNOB.Bin69_FLG",
	Storage = "UserVar",
	DataType = "Integer",
    _fitem = Fitem('SAME', rm2=pFail(setbin=-69, ret=-2), rm1=pFail(setbin=-69, ret=-1), 
                           r0=pFail(setbin=6903, ret = 0), r2=pFail(setbin=6903, ret = 0))
    )

# Define above tests in FACT Flow
TPI_END_XXX_FLW3 = Flow(f'TPI_END_XXX_FACT',  Bin69_chk)

#Tests transferred to TPI_BASE_FINAL
#FINAL Subflow Fork; this test is to accomodate PTH_DIODE at the FINAL subflow. If PTH_DIODE is not needed in FINAL flow before TPI_DFF, this test should be deleted
# as this is a ducplidate of the reject fork in TPI_DFF
#RejectFork = ScreenTC(
#    name = "CTRL_X_SCREEN_K_FINAL_X_X_X_X_REJECTFORK", 
#	ScreenTestSet = "RejectFork",
#	ScreenTestsFile = "../../../../Shared/BaseInputs/Common/Common_NVL_S28C/ScreenTest_TP_KNOB.txt",
#    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO, ret = 0), r2=pPass(ret = 2))
#    )



# Test Plan End Flow
End_Device = PrimeDeviceEndDatalogTestMethod(
    name = "CTRL_X_DEVICEEND_K_TESTPLANENDFLOW_X_X_X_X_PDETM", 
    LogLevel = "Disabled",
    _fitem = Fitem('SAME', rm2=pFail(setbin=-93, goto='NEXT'), rm1=pFail(setbin=-93, goto='NEXT'), r0=pFail(ret = 0))
    )

Final_Device = PrimeDeviceEndFinalizeTestMethod(
    name = "CTRL_X_DEVICEEND_K_TESTPLANENDFLOW_X_X_X_X_PDEFTM", 
    LogLevel = "Disabled",
    _fitem = Fitem('SAME', rm2=pFail(setbin=-93, goto='NEXT'), rm1=pFail(setbin=-93, goto='NEXT'), r0=pFail(ret = 0))
    )

Odese_Remap = PrimeOdeseBinConverterTestMethod(
    name = "CTRL_X_ODESEBINCONVERTERTC_E_TESTPLANENDFLOW_X_X_X_X_ODESEREMAP", 
    LogLevel = "Disabled",
    BypassPort = 1, #Bypass, no longer need as NVL is TOS4 and supports 8 digit binning
    _fitem = Fitem('SAME', rm2=pFail(setbin=-93, goto='NEXT'), rm1=pFail(setbin=-93, goto='NEXT'), r0=pFail(ret = 1))
    )

    #FINAL tests transferred from TPI_DFF as these are related to Base not DFF check
subflw_fin = "FINAL"

b69_flag= AuxiliaryTC(
    name = f"CTRL_X_AUX_K_{subflw_fin}_X_X_X_X_CHK1SET2",
    _comment = "improvement: b69_flag move out of TPI_DFF since not related to DFF",
    Expression = "[__shared__::TP_KNOB.Bin69_FLG] + 1",
    ResultPort = "[R]==2?1:2",
    Storage = "UserVar",
    ResultToken = "__shared__::TP_KNOB.Bin69_FLG",
    DataType = "Integer",
    _fitem = Fitem('SAME', rm2=pFail(setbin=-69, ret=-2), rm1=pFail(setbin=-69, ret=-1), 
                           r0=pFail(setbin=6905, ret = 0), r2=pFail(setbin=6905, ret = 0))                       
    )

inline_rv = ScreenTC(
    name = f"CTRL_X_SCREEN_K_{subflw_fin}_X_X_X_X_INLINERV",
    _comment = "improvement: inlinerv move out of TPI_DFF since not related to DFF",
    ScreenTestSet = "INLINERVREBIN",
    ScreenTestsFile = "./InputFiles/INLINERV_ScreenTest.txt",
    _fitem = Fitem('SAME', r0=pFail(setbin=AUTO, ret = 0), r2=pFail(setbin=AUTO, ret = 0), r3=pFail(setbin=8030, ret = 0), r4=pFail(setbin=8040, ret = 0), r5=pFail(setbin=8050, ret = 0), r6=pFail(setbin=8020, ret = 0), r7=pFail(setbin=8080, ret = 0))               
    )

        #Define next test instance in DUT flow Instance for static Value 
FLW_GT_STATIC = UserCodeTC(
    name = f"CTRL_X_USERCODETC_K_END_X_X_X_X_GTSTATIC_END", 
    BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_P16C(-1,1)'),
    InputFile = "./InputFiles/GT_STATIC.cs",
	Method = "PoweronGTStaticValue",
	NamespaceClass = "TPIUserCode.TPI",
    _fitem = Fitem('SAME',  r0=pFail(setbin=AUTO, ret = 0))
    )

END_SubFlow_END= Flow(f'TPI_END_XXX_END',  FLW_GT_STATIC)

TPI_END_XXX_FLW8 = Flow(f'TPI_END_XXX_TESTPLANENDFLOW',  End_Device, Final_Device, Odese_Remap)

FINAL_Subflow = Flow(f'TPI_END_XXX_{subflw_fin}', b69_flag, inline_rv)