# PKG TPI Evmin Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import AuxiliaryTC, RenameTp, ScreenTC, RunCallback, PrimeInitializeLibraryTestMethod, CallbacksManager, PrimeSimbaInitTestMethod, PrimeInitializeServicesTestMethod, PlistModificationsBase, \
    PrimeThermalControlSetInitTestMethod, VminForwardingBase, UserCodeTC, FlowControlBase, InitVariablesTC, PowerSequenceHandler, PrimeBinSetterTestMethod, PrimeDeviceStartPackageDatalogTestMethod, \
    PrimeDeviceStartSetupTestMethod, PrimeLotEndDatalogTestMethod, PrimeLotEndFinalizeTestMethod, PrimeLotStartDatalogTestMethod, PrimeLotStartSetupTestMethod, PrimeBinSetterTestMethod, \
    PrimePauseTestMethod, PrimePerformanceProfileTestMethod, PrimePinProfilerTestMethod, PrimeSampleRateTestMethod, TesterScreenTC
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  NativeMultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./TPI_BASE_XXX',  'TPI_BASE_XXX', tosversion="tos4", binrange=(9302, 9302), 
                   defaultrm2bin = [(99931000, 99931999), (99690000, 99690999)], 
                   defaultrm1bin = [(98931000, 98931999), (98690000, 98690999)])

Import("TPI_BASE_XXX.usrv")

#Init tests for TPI_BASE
subflw_init = "INIT"

#TP name update so that udd requirements are met.
rename_tp= RenameTp(
    name = f"CTRL_X_X_K_{subflw_init}_X_X_X_X_RENAMETP",
    SocPathOffset = "../../../..",
    IgnoreFiles = "", 
    DebugUserVar = "RunTimeLibraryVars.DebugRenameTp",
    FileCountLimit = Spec('90000'),
    LogLevel = "Enabled",
    _fitem = Fitem('SAME', r0=pFail(ret = 1))             
    )

#list of screen tests in INIT
scrn_init_test_name = ["BOMGROUP_SETUP", "MTLFILE", "RCS1_SETUP", "SHARED_USRV_PORT", "FACTVARS"]

#screentest parameter for each scrn_init_test_name
screentest_set = {"BOMGROUP_SETUP": "BOMSETUP", "MTLFILE": "DFF_DIEID", "RCS1_SETUP": "RCS1", "SHARED_USRV_PORT": "REPLICATE2SHAREDUSRV", "FACTVARS":"FaCTvarOptype"}
screentest_file = {"BOMGROUP_SETUP": "./InputFiles/TPI_BASE_XXX_ScreenTest.txt", 
                   "MTLFILE": "./InputFiles/DFF_Screen.txt", 
                   "RCS1_SETUP": "./InputFiles/Raw_Class_Setup.txt",  
                   "SHARED_USRV_PORT": "../../../../Shared/BaseInputs/Common/Common_NVL_S28C/shrd_usrv_rplctr.txt", 
                   "FACTVARS": "./InputFiles/TPI_BASE_XXX_ScreenTest.txt"}
screentest_bypass = {"BOMGROUP_SETUP": -1, 
                     "MTLFILE": -1, 
                     "RCS1_SETUP": 1,  
                     "SHARED_USRV_PORT": -1, 
                     "FACTVARS": -1}

scrn_init_test = []  #empty list that will contain the ScreenTC tests in INIT
for init1_test in scrn_init_test_name:
    init1_flow = ScreenTC(
    name = f"CTRL_X_SCREEN_K_{subflw_init}_X_X_X_X_{init1_test}",
    BypassPort = screentest_bypass[init1_test],
    ScreenTestSet = screentest_set[init1_test],
    ScreenTestsFile = screentest_file[init1_test],
    _fitem = Fitem('SAME', r0=pFail(ret = 0), r2=pFail(ret = 0))
     )
    scrn_init_test.append(init1_flow)     

#list of RunCallback tests in INIT
runclbk_init_test_name = ["FLEXBOMSETUP", "SETINITGSDSFAIL"]

#RunCallback parameter for each test in INIT
callback = {"FLEXBOMSETUP": "WriteUserVar", "SETINITGSDSFAIL": "WriteSharedStorage"}
parameters = {"FLEXBOMSETUP": "--uservar __shared__::SCVars.TP_FLEXBOMRECIPE --value __shared__::SCVars.SC_FLEXBOMRECIPE --type String",
              "SETINITGSDSFAIL": "--token G.L.S.INITFLAG --value FAIL"}
result_port = {"FLEXBOMSETUP": "[R]==1?1:0", "SETINITGSDSFAIL": None}
bypass_port = {"FLEXBOMSETUP": None, "SETINITGSDSFAIL": None}

rnclbk_init_test = [] #empty list that will contain RunCallback tests in INIT
for init2_test in runclbk_init_test_name:
    init2_flow = RunCallback(
    name =  f"CTRL_X_RUNCALLBACK_K_{subflw_init}_X_X_X_X_{init2_test}",
    Callback = callback[init2_test],
    Parameters = parameters[init2_test],
    ResultPort = result_port[init2_test],
    BypassPort = bypass_port[init2_test],
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )
    rnclbk_init_test.append(init2_flow)

#Initialize the init controller for the Init flow optimizations
load_prime = PrimeInitializeLibraryTestMethod(
    name = f"CTRL_X_PRIMEINIT_K_{subflw_init}_X_X_X_X_LOADPRIME",
    LogLevel = "Disabled",
	ForceFullInit = "False", #to enable init optimization
	PerformanceCounterSampleRate = 1,
	PerformanceCounterLogLevel = "GlobalOnly",
	GlobalTelemetryLevel = "Debug",
    GlobalSettingsFilePath =  Spec('GetEnvironmentVariable("~HDMT_TPL_DIR") + __shared__::TpRule.If_CLASS_NVL_S28C("/Shared/Modules/TPI/TPI_BASE_XXX/InputFiles/global_S28C.primesettings", "/Shared/Modules/TPI/TPI_BASE_XXX/InputFiles/global.primesettings")'),
    LogLevelEnabledTestMethodNames = "VminTC", # unexpected keyword argument
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
)

#to initialize callback test
clbk_mgr= CallbacksManager(
    name = f"CTRL_X_PRIMECALLBACKSMANAGER_K_{subflw_init}_X_X_X_X_CALLBACKS",
    LogLevel = "Disabled",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))       
    )

maestro = PrimeSimbaInitTestMethod(
    name = f"CTRL_X_PRIMESIMBA_X_{subflw_init}_X_X_X_X_MAESTRO",
    UlatEnableMode = "Enabled",
    UlatFileType = "Lot",
    UnitIdentificationMethod = "Vid",
    BypassPort = Spec('__shared__::TpRule.If_S28_S52_HX28(-1,-1,-1,1)'),
    _fitem = Fitem('SAME', r0=pFail(ret = 0)) 
)

#test that will parse json files in TP
load_aleph = PrimeInitializeServicesTestMethod(
    name = f"CTRL_X_PRIMEINIT_K_{subflw_init}_X_X_X_X_LOADALEPH",
    LogLevel = "Disabled",
	ForceValidateAlephFiles = "False",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
)

#test to initial Vmin forwarding condition
vmin_forwarding = VminForwardingBase(
    name = f"CTRL_X_PRIMEVMINFORWARDING_K_{subflw_init}_X_X_X_X_VMIN",
    # DisablePerCoreOvershoot = '__shared__::QNRTpRuleShared.If_PseudoVminForwarding("True" , "False")',
    DffMappingFile = Spec('__shared__::TpRule.If_CLASS_NVL_S52C("./InputFiles/CLASS_NVL_UpsVminDffMapping_52C.json", __shared__::TpRule.If_CLASS_NVL_U8C("./InputFiles/CLASS_NVL_UpsVminDffMapping_U8C.json","./InputFiles/CLASS_NVL_UpsVminDffMapping.json"))'),
	DffMappingOptype = Spec('TPI_BASE_XXX_Rules.DffMappingOptype("RC_S1","PBIC_DAB")'),
	DffMappingSet = Spec('TPI_BASE_XXX_Rules.DffMappingSet("rt_vmin_dff_token","vmin_dff_token","vmin_dff_token","vmin_dff_token","vmin_dff_token","itd_vmin_dff_token")'),
    EnableHermesMode = "False",
    DisablePerCoreOvershoot = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding("True" , "False")'),
	SearchGuardbandEnable = Spec('TPI_BASE_XXX_Rules.PHMandENG("True","False")'),
	StoreVoltages = Spec('TPI_BASE_XXX_Rules.PHMandENG("False","True")'),
	UseDffAsSource = Spec('TPI_BASE_XXX_Rules.VMINFORWARDING("False","False","False","True","False","False","True")'),
	UseLimitCheck = Spec('TPI_BASE_XXX_Rules.VMINFORWARDING("False","False","False","False","True","False","False")'),
	UseVoltagesSources = Spec('TPI_BASE_XXX_Rules.VMINFORWARDING("True","True","True","False","True","False","False")'),
	VminSinglePointMode = Spec('TPI_BASE_XXX_Rules.VminSinglePointMode("False","False","False","False","False","True")'),
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
)

#test to initialize flow control condition that will be used in MTT tests
flw_control = FlowControlBase(
    name = f"CTRL_X_FLOWCONTROLBASE_K_{subflw_init}_X_X_X_X_FLOWCONTROL",
    AllowDownbins = Spec('__shared__::TpRule.MTT_Rule("True","False")'),
	UseMTT = "True",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
)

#test is bypassed for now, will be enabled if telemetry logs are needed
tp_log = UserCodeTC(
    name = f"CTRL_X_UC_K_{subflw_init}_X_X_X_X_LOGTPINFOTOTELEMETRY",
    InputFile = "./InputFiles/WriteTelemetrySample.cs",
	NamespaceClass = "TPINFO.Telemetry",
    Method = "LogLoadedItems",
    LogLevel = "Enabled",
    BypassPort = 1,
    _fitem = Fitem('SAME', r0=pFail(ret = 1))
)

#test is change parallel to serial 
ParalleltoSerial = RunCallback(
    name = f"CTRL_X_UF_K_{subflw_init}_X_X_X_X_SETFLOWPARALLELTOSERIAL",
    Callback = "SetConcurrentFlowExecutionModeSerial",
    Parameters = "Flows::BEGINPRL0_SubFlow,Flows::BEGINPRL1_SubFlow,Flows::BEGINPRL2_SubFlow,Flows::ENDPRL0_SubFlow,Flows::ENDPRL1_SubFlow,Flows::ENDPRL2_SubFlow,Flows::ENDPRL3_SubFlow,Flows::ENDPRL4_SubFlow,Flows::FACTPRL0_SubFlow,Flows::FACTPRL1_SubFlow,Flows::SPEEDPRL0_SubFlow,Flows::SPEEDPRL1_SubFlow,Flows::SPEEDPRL2_SubFlow,Flows::SPEEDPRL3_SubFlow,Flows::SPEEDPRL4_SubFlow,Flows::SPEEDPRL5_SubFlow,Flows::STARTPRL0_SubFlow,Flows::STARTPRL1_SubFlow,Flows::STARTPRL2_SubFlow,Flows::STARTPRL3_SubFlow,Flows::STARTPRL4_SubFlow",
    BypassPort = Spec('TPI_BASE_XXX.ParalleltoSerial'),
	_fitem = Fitem('SAME', r0=pFail(ret = 1))
)


# Restore plist modifications at the end of init
RESTORE = PlistModificationsBase(
    name = f"CTRL_X_PLISTMOD_K_{subflw_init}_X_X_X_X_RESTORE",
    OperationMode = "Restore",
    _fitem = Fitem('SAME', r0=pFail(ret=0))
    )

#dummy test to clear START TopFlow flag at initial state
clear_start_topflow_flag = RunCallback(
    name = "CTRL_X_AUX_K_START_X_X_X_X_CLEARSTARTFLAG",
    Callback = "WriteSharedStorage",
    Parameters = "--token G.U.S.StartTopFlowFlag --value FAIL",
    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO,ret = 0))
)

#dummy test to set START TopFlow flag to PASS
set_start_topflow_flag = RunCallback(
    name = "CTRL_X_AUX_K_STARTPOST_X_X_X_X_SETSTARTFLAGPASS",
    Callback = "WriteSharedStorage",
    Parameters = "--token G.U.S.StartTopFlowFlag --value PASS",
    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO, ret = 0))
)

# Define above tests in INIT 
INIT_Subflow = Flow(f'TPI_BASE_XXX_INIT',   scrn_init_test[1], load_prime, tp_log, load_aleph, clbk_mgr, flw_control, rnclbk_init_test[1], scrn_init_test[2], scrn_init_test[0], 
                    vmin_forwarding, scrn_init_test[4], maestro,  rename_tp, ParalleltoSerial, RESTORE)

######################################
# Tests in MAINFLOW and SPECIAL Flow #
######################################

#Auxiliary test list and dicctionary
aux_test_list = ["START_X_X_X_X_SETINITGSDSCHECK", "START_X_X_X_X_SETTPSGSDSCHECK", "START_X_X_X_X_CLEAR69FLAG","FACT_X_X_X_X_LABVFCHK"]
aux_data = {"START_X_X_X_X_SETINITGSDSCHECK": "String", "START_X_X_X_X_SETTPSGSDSCHECK": "String", "START_X_X_X_X_CLEAR69FLAG": "Integer", "FACT_X_X_X_X_LABVFCHK": "String"}
aux_storage = {"START_X_X_X_X_SETINITGSDSCHECK": "SharedStorage", "START_X_X_X_X_SETTPSGSDSCHECK": "SharedStorage", "START_X_X_X_X_CLEAR69FLAG": "UserVar", "FACT_X_X_X_X_LABVFCHK": "UserVar"}
aux_port =  {"START_X_X_X_X_SETINITGSDSCHECK": "[R] == true?1:0", "START_X_X_X_X_SETTPSGSDSCHECK": "[R] == true?1:0", "START_X_X_X_X_CLEAR69FLAG": None, "FACT_X_X_X_X_LABVFCHK": "[R]?2:1"}
aux_post = {"START_X_X_X_X_SETINITGSDSCHECK": "LogUserVarCollection(--collection __shared__::SCVars --writeonce)"},
aux_exprssn = {"START_X_X_X_X_SETINITGSDSCHECK": "[G.L.S.INITFLAG] == 'PASS'", "START_X_X_X_X_SETTPSGSDSCHECK": "[G.U.S.TESTPLANSTARTTFLAG] == 'PASS'", "START_X_X_X_X_CLEAR69FLAG": "1 - 1",
              "FACT_X_X_X_X_LABVFCHK": "Substring([__shared__::SCVars.SC_FACILITYID],0,3) == 'GDL'"}

aux_tests = []  #empty list that will contain the AuxiliaryTC tests
for auxtest in aux_test_list:
    auxtest_flow = AuxiliaryTC(
    name = f"CTRL_X_AUX_K_{auxtest}",
    DataType = aux_data[auxtest],
    Storage = aux_storage[auxtest],
    ResultPort = aux_port[auxtest],
    Expression = aux_exprssn[auxtest],
    PostInstance = "LogUserVarCollection(--collection __shared__::SCVars --writeonce)" if 'SETINITGSDSCHECK' in auxtest else None,
    ResultToken = "__shared__::TP_KNOB.Bin69_FLG" if auxtest == "START_X_X_X_X_CLEAR69FLAG" else None
     )
    aux_tests.append(auxtest_flow)

#Screen test list and dicctionary
#Klotrebin set to bypass for now, NEED TO REVIEW AND ENABLE BACK AGAIN ONCE INFO IS AVAILABLE FOR NVL KLOT
scrn_test_list = ["FACT_X_X_X_X_KLOTREBIN", "FACT_X_X_X_X_FACTFORK", "ALARM_X_X_X_X_BIN", "TESTPLANENDFLOW_X_X_X_X_REJECTFORK", "STARTPREPRL1_X_X_X_X_MPSSKIPUNIT", "STARTPREPRL1_X_X_X_X_FUSETPNAME", "STARTPREPRL1_X_X_X_X_CSETOKEN", "STARTPREPRL1_X_X_X_X_SETDFFDIESLCT"]
scrn_set = {"FACT_X_X_X_X_KLOTREBIN": "KLOTB56", "FACT_X_X_X_X_FACTFORK": "FACTFORK", "ALARM_X_X_X_X_BIN": "ChkAlarm", "TESTPLANENDFLOW_X_X_X_X_REJECTFORK": "RejectFork",
             "STARTPREPRL1_X_X_X_X_MPSSKIPUNIT": Spec('TPI_BASE_XXX_Rules.MPSSKIPUNIT("SPBICS2","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SQAS1","SPBICS2")'),
             "STARTPREPRL1_X_X_X_X_FUSETPNAME": Spec('TPI_BASE_XXX_Rules.FUSETPNAME_screen("FUSE_SHORT_TP_NAME_RC","FUSE_SHORT_TP_NAME")'),
             "STARTPREPRL1_X_X_X_X_CSETOKEN": Spec('TPI_BASE_XXX_Rules.CSETOKEN("SetCSECCDFF","SetCSECCDFFRC","SetCSEPCDFF","SetOLBCC","SetOLBCCRC","SetOLBPC","SetOLBPC","SetCSECCDFF")'), "STARTPREPRL1_X_X_X_X_SETDFFDIESLCT": "SC_DIESLCT" }
scrn_file = {"FACT_X_X_X_X_KLOTREBIN": "./InputFiles/TPI_BASE_XXX_ScreenTest.txt", "FACT_X_X_X_X_FACTFORK": "./InputFiles/TPI_BASE_XXX_ScreenTest.txt",
              "ALARM_X_X_X_X_BIN": "./InputFiles/Check_alarm.txt", "TESTPLANENDFLOW_X_X_X_X_REJECTFORK": "../../../../Shared/BaseInputs/Common/Common_Files/ScreenTest_TP_Knob.txt", "STARTPREPRL1_X_X_X_X_CSETOKEN": "./InputFiles/ScreenTest_SetCSEDFF.txt",
              "STARTPREPRL1_X_X_X_X_MPSSKIPUNIT": "./InputFiles/MPS_Skip_Screen.txt", "STARTPREPRL1_X_X_X_X_FUSETPNAME": "./InputFiles/Fuse_TPName_Screentest.txt", "STARTPREPRL1_X_X_X_X_SETDFFDIESLCT": "./InputFiles/TPI_BASE_XXX_ScreenTest.txt"}
scrn_bypass = {"FACT_X_X_X_X_KLOTREBIN": Spec('TPI_BASE_XXX_Rules.BOM_Klot(-1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)'), "FACT_X_X_X_X_FACTFORK": None,
              "ALARM_X_X_X_X_BIN": None, "TESTPLANENDFLOW_X_X_X_X_REJECTFORK": None, "STARTPREPRL1_X_X_X_X_MPSSKIPUNIT":Spec('TPI_BASE_XXX_Rules.MPSSKIPUNIT(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1)'),
              "STARTPREPRL1_X_X_X_X_FUSETPNAME": Spec('TPI_BASE_XXX_Rules.FUSETPNAME_bypass_global(-1, 1, 1)'),
              "STARTPREPRL1_X_X_X_X_CSETOKEN": Spec('TPI_BASE_XXX_Rules.CSETOKEN(-1, -1, -1, -1, -1, -1, -1, 1)'), "STARTPREPRL1_X_X_X_X_SETDFFDIESLCT": Spec('__shared__::GlobalRule.primaryoptype(-1,-1,1,1,1,1,1,1,1,1)')}
scrn_preinstance = {"FACT_X_X_X_X_KLOTREBIN": None, "FACT_X_X_X_X_FACTFORK": None,
              "ALARM_X_X_X_X_BIN": None, "TESTPLANENDFLOW_X_X_X_X_REJECTFORK": None, "STARTPREPRL1_X_X_X_X_MPSSKIPUNIT": None,
              "STARTPREPRL1_X_X_X_X_FUSETPNAME":None,
              "STARTPREPRL1_X_X_X_X_CSETOKEN": None, "STARTPREPRL1_X_X_X_X_SETDFFDIESLCT": "SetCurrentDieId(PKG)"}

scrn_tests = [] #empty list that will contain the ScreenTC tests
for scrntest in scrn_test_list:
    scrntest_flow = ScreenTC(
    name =  f"CTRL_X_SCREEN_K_{scrntest}",
    ScreenTestSet = scrn_set[scrntest],
    ScreenTestsFile = scrn_file[scrntest],
    BypassPort = scrn_bypass[scrntest],
    PreInstance = scrn_preinstance[scrntest],
    )
    scrn_tests.append(scrntest_flow)

chk_flag = ScreenTC(
    name =  "CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_CHECKFLAG",
    ScreenTestSet = "CheckFlag",
	ScreenTestsFile = "./InputFiles/TPI_BASE_XXX_ScreenTest.txt",
	PreInstance = "EvaluateExpression(--expression GetCurrentSoftBin() --result G.U.S.CurrentSoftBin)",
	PostInstance = "PrintToItuff(--body_type strgval --body_data G.U.S.CurrentSoftBin --tname_suf _CurrentSoftBin)",
    _fitem = Fitem('SAME', rm2=pFail(setbin=-69, goto="NEXT"), rm1=pFail(setbin=-69, goto="NEXT"), r0=pFail(setbin= 6905, goto='CTRL_X_PWR_K_TESTPLANENDFLOW_X_X_X_X_PWRDWNPKG'),
                   r2=pFail(setbin=6905, goto='CTRL_X_PWR_K_TESTPLANENDFLOW_X_X_X_X_PWRDWNPKG'), r3=pFail(setbin= 6905, goto='CTRL_X_PWR_K_TESTPLANENDFLOW_X_X_X_X_PWRDWNPKG')) 
)

#RunCallback tests list and dictionary
rnclbk_test_list = ["TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGFAIL", "TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGPASS", "START_X_X_X_X_INITGSDS_FLOWPOS", "BEGIN_X_X_X_X_LOADVMIN"]
rnclbk_clbk = {"TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGFAIL":"WriteSharedStorage" , "TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGPASS": "WriteSharedStorage", "START_X_X_X_X_INITGSDS_FLOWPOS": "WriteSharedStorage" ,
               "BEGIN_X_X_X_X_LOADVMIN": "LoadVminFromDFF"}
rnclbk_param = {"TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGFAIL": "--token G.U.S.TESTPLANSTARTTFLAG --value FAIL", "TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGPASS": "--token G.U.S.TESTPLANSTARTTFLAG --value PASS",
                "START_X_X_X_X_INITGSDS_FLOWPOS": "--token G.U.S.FLOWPOS --value VCC_F", "BEGIN_X_X_X_X_LOADVMIN": None}
rnclbk_bypass =  {"TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGFAIL":None , "TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGPASS": None, "START_X_X_X_X_INITGSDS_FLOWPOS": Spec("1") ,
               "BEGIN_X_X_X_X_LOADVMIN": Spec("TPI_BASE_XXX_Rules.VMINFORWARDING(1,1,1,-1,-1,1,-1)")}
rnclbk_tests = [] #empty list that will contain the RunCallback tests
for rnclbktest in rnclbk_test_list:
    rnclbktest_flow = RunCallback(
        name = f"CTRL_X_RUNCALLBACK_K_{rnclbktest}",
        Callback = rnclbk_clbk[rnclbktest],
        Parameters = rnclbk_param[rnclbktest],
        BypassPort = rnclbk_bypass[rnclbktest]
    )
    rnclbk_tests.append(rnclbktest_flow)

#test method that allows to flow fork based on tester configuration
offline_setup = TesterScreenTC(
    name =  "CTRL_X_TSTC_K_START_X_X_X_X_OFFLINE_SETUP",
    LogLevel = "Disabled",
	BypassPort =1,
    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO, ret = 0), r1=pPass(ret = 1), r2=pPass(ret = 1), r3=pPass(ret = 1), r4=pPass(ret = 1), r5=pPass(goto="CTRL_X_INITVTC_K_START_X_X_X_X_GSDS")) 
)


#enable offline GSDS feed for offline validation
offline_gsds = InitVariablesTC(
    name =  "CTRL_X_INITVTC_K_START_X_X_X_X_GSDS",
    ConfigurationFile = "./InputFiles/GSDSInputFile.csv",
	BypassPort =1,
    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO, ret = 0)) 
)

pwr_dwn = PowerSequenceHandler(
    name =  "CTRL_X_PWR_K_TESTPLANENDFLOW_X_X_X_X_PWRDWNPKG",
    ApplyPowerDown = "Always",
	PowerDownTc = "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
    _fitem = Fitem('SAME', rm2=pFail(setbin=-93, ret = 1), rm1=pFail(setbin=-93, ret = 1), r0=pFail(ret = 1), r2=pFail(ret = -1))
)

# to create and log to ituff level 2 and level 3 headers for package mode.
log_ituff = PrimeDeviceStartPackageDatalogTestMethod(
    name =  "CTRL_X_DEVICESTART_K_TESTPLANSTARTFLOW_X_X_X_X_PDSPDTM", 
    LogLevel = "Disabled", 
    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO, ret = 0), r1 = pPass(setbinstring = "b1001000_pass_pure", ctr = 0))
)

#provides a placeholder for Prime activities needed to be executed at the beginning of the Device
# When the uservar _UserVars.ENABLE_PRIME_BRITA exists and is equal to "TRUE", Brita Flow Trace is enabled  
strt_setup = PrimeDeviceStartSetupTestMethod(
    name =  "CTRL_X_DEVICESTART_K_TESTPLANSTARTFLOW_X_X_X_X_PDSSTM",
    LogLevel = "Disabled",
	InstanceSummaryMode = "Disabled",
	SmartTc = "Enabled",
    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO, ret = 0), r1 = pPass(setbinstring = "b1001000_pass_pure", ctr = 0))
)

# in charge of writting the relevant datalog information after a Lot has been run to ituff
end_log = PrimeLotEndDatalogTestMethod(
    name =  "CTRL_X_PRIME_K_LOTENDFLOW_X_X_X_X_PLEDTM", 
    LogLevel = "Disabled", 
    _fitem = Fitem('SAME', rm2 = pFail(setbin=-93, goto = "CTRL_X_PRIME_K_LOTENDFLOW_X_X_X_X_PLEFTM"), rm1 = pFail(setbin=-93, goto = "CTRL_X_PRIME_K_LOTENDFLOW_X_X_X_X_PLEFTM"), r0=pFail(ret = 0))
)

#In charge of doing any necessary actions after a Lot Run.
end_finalize = PrimeLotEndFinalizeTestMethod(
    name =  "CTRL_X_PRIME_K_LOTENDFLOW_X_X_X_X_PLEFTM", 
    LogLevel = "Disabled", 
    _fitem = Fitem('SAME', rm2 = pFail(setbin=-93, ret = 1), rm1 = pFail(setbin=-93, ret = 1), r0=pFail(ret = 0))
)

#create the datalog Lot header for ituff and other outputs
start_log = PrimeLotStartDatalogTestMethod (
    name =  "CTRL_X_PRIMELOTSTART_K_LOTSTARTFLOW_X_X_X_X_PRIMESTARTLOTDATALOG", 
    StreamDestination = "OUTPUT_TO_FILE_AND_PUDL",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
)

#In charge of doing any necessary initialization and validation prior to a Lot Run. This test method is intended to be used before any other Lot test method.
start_setup = PrimeLotStartSetupTestMethod(
    name =  "CTRL_X_PRIMELOTSTART_K_LOTSTARTFLOW_X_X_X_X_PRIMESTARTLOTSETUP", 
    LogLevel = "Disabled", 
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
)

#test that gets the BinSetterPath based on the TRACE program, and uses the data obtained via TOS Flow Trace to filter
#dic for PrimeBinSetterTestMethod
bin_settr = ["FIRST", "LAST"]
bin_settr_tests = []
for bin_settr_test in bin_settr:
    bin_settr_flow = PrimeBinSetterTestMethod(
    name = f"CTRL_X_BINSETTER_E_TESTPLANENDFLOW_X_X_X_X_{bin_settr_test}",
    LogLevel = "Disabled",
	NumberOfFailingPath = 3,
	ReadDirectionSetting = "First" if bin_settr_test == "FIRST" else "Last"
    #_fitem = Fitem('SAME', r0=pFail(goto = "NEXT"), rm2 = pFail(goto = "NEXT"), rm1 = pFail(goto = "NEXT"), r2 = pFail(goto = "NEXT"))
    )
    bin_settr_tests.append(bin_settr_flow)

#when enabled, test will provide capability to perform profiling on the test time on both functions and HdmtApi.
profile_list = ["TESTPLANSTARTFLOW", "TESTPLANENDFLOW"]
profile_tests = []
for profile_test in profile_list:
    profile_test_flow = PrimePerformanceProfileTestMethod(
    name = f"CTRL_X_PRIMEPERFORMACEPROFILETEST_K_{profile_test}_X_X_X_X",
    GlobalInstanceSummaryMode = "Enabled" if profile_test == "TESTPLANSTARTFLOW" else "Disabled",
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )
    profile_tests.append(profile_test_flow)

#provide sampling based on flows defined by the user.
sample_list = ["", "_PINPROFILER"]
sample_tests = []
for sample_test in sample_list:
    sample_test_flow = PrimeSampleRateTestMethod(   
    name = f"CTRL_X_SAMPLERATE_E_TESTPLANSTARTFLOW_X_X_X_X{sample_test}",
    SamplingRateValue = "1" if sample_test == "_PINPROFILER" else Spec('TPI_BASE_XXX_Rules.CTRL_X_SAMPLERATE_K_TESTPLANSTARTFLOW_X_X_X_X_sample_rate("1","1")'),
    SampleOption = "DUT_SAMPLING" if sample_test == "_PINPROFILER" else None,
    BypassPort =  Spec('TPI_BASE_XXX.PinMonitorEnable') if sample_test == "_PINPROFILER" else None,
    )
    sample_tests.append(sample_test_flow)

# Provides the capability to start and end the profile of the given pins per test instance, for all the test instances between the Start and the Stop of the same tag.
# Prime will datalog the profile for the given pins at the end of every test instance.
pinprofiler_list = ["TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR", "TESTPLANENDFLOW_X_X_X_X_PINPROFILERSTOPMONITOR"]
pinprofiler_tests = []
for pinprofiler_test in pinprofiler_list:
    pinprofiler_test_flow = PrimePinProfilerTestMethod(   
    name = f"CTRL_X_UF_E_{pinprofiler_test}",
    Tag = "TdauTag",
    BypassPort = Spec('TPI_BASE_XXX.PinMonitorEnable') if pinprofiler_test == "TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" else Spec('TPI_BASE_XXX.PinMonitorEnabled') ,
    PostInstance = "WriteUserVar(--uservar TPI_BASE_XXX::TPI_BASE_XXX.PinMonitorEnabled --value -1 --type Integer)" if pinprofiler_test == "TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR"
                    else "WriteUserVar(--uservar TPI_BASE_XXX::TPI_BASE_XXX.PinMonitorEnabled --value 1 --type Integer)" ,
    Mode = "Start" if pinprofiler_test == "TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" else "Stop",
    #PinNames = "IP_CPU::TDAU_CH_CORE, IP_PCH::TDAU_CH_GCD, IP_PCH::TDAU_CH_IOE, TDAU_CH_SOC" if pinprofiler_test == "TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" else None,
    PinNames = "IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0" if pinprofiler_test == "TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" else None,
    SamplingInterval = 4 if pinprofiler_test == "TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" else None,
    LogLevel = "Enabled" if pinprofiler_test == "TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" else None,
    )
    pinprofiler_tests.append(pinprofiler_test_flow)

 # FINAL Subflow Fork; this test is to accomodate PTH_DIODE at the FINAL subflow. If PTH_DIODE is not needed in FINAL flow before TPI_DFF, this test should be deleted
# as this is a ducplidate of the reject fork in TPI_DFF
RejectFork = ScreenTC(
    name = "CTRL_X_SCREEN_K_FINAL_X_X_X_X_REJECTFORK", 
	ScreenTestSet = "RejectFork",
	ScreenTestsFile = Spec('"../../../../Shared/BaseInputs/Common/Common_Files/ScreenTest_TP_Knob.txt"'),
    PostInstance=Spec('__shared__::FlwSkpCollect.if_ahmt("","TimeTrackerStop(FINAL)")'),
    _fitem = Fitem('SAME', r0=pFail(setbin= AUTO, ret = 0), r2=pPass(ret = 2))
    )

#TOS Util Logging
tosutil_list = [
    ["Export_Start", "LOTSTARTFLOW"],
    ["Console_Print", "START"],
    ["Export_Stop", "LOTENDFLOW"]]

tosutil_tests = []
for tosutil_test in tosutil_list:
    test = UserCodeTC(
        name = f"CTRL_X_UC_E_{tosutil_test[1]}_X_X_X_X_{tosutil_test[0].upper()}",
        BypassPort = Spec("__shared__::TpRule.If_FacilityID_GDL(-1,1)"),
        InputFile = "./InputFiles/tos_util.cs",
        Method = tosutil_test[0],
        NamespaceClass = "TosUtil.Logging",
        _fitem = Fitem('SAME', edc=True, r0=pFail(goto="NEXT"))
    )
    tosutil_tests.append(test)

reset_metrics = RunCallback(
    name = "CTRL_X_RUNCALLBACK_K_START_X_X_X_X_RESETMETRICS",
    Callback = "VminResetMetrics",
    LogLevel = "Disabled",
    _fitem = Fitem('SAME', edc=True, r0=pFail(goto="NEXT"))
)

print_metrics = RunCallback(
    name = "CTRL_X_RUNCALLBACK_K_FINAL_X_X_X_X_PRINTMETRICS",
    Callback = "VminPrintMetrics",
    LogLevel = "Disabled",
    _fitem = Fitem('SAME', edc=True, r0=pFail(goto="NEXT"))
)

metricrate_test = PrimeSampleRateTestMethod(
    name = "CTRL_X_SAMPLERATE_E_FINAL_X_X_X_X_METRICRATE",
    SamplingRateValue = Spec('__shared__::TpRule.If_FacilityID_GDL("25","200")'),
    SampleOption = "DUT_SAMPLING"
)


### Special Flows ####
LOTSTARTFLOW_Subflow = Flow('TPI_BASE_XXX_LOTSTARTFLOW', start_setup, start_log, tosutil_tests[0])
LOTENDFLOW_Subflow = Flow('TPI_BASE_XXX_LOTENDFLOW', end_log, end_finalize, tosutil_tests[2])
TESTPLANSTARTFLOW_Subflow = Flow('TPI_BASE_XXX_TESTPLANSTARTFLOW', strt_setup, log_ituff,
                                Fitem("SAME", rnclbk_tests[0],  r0 = pFail(setbin= AUTO, ret = 0),r2 = pFail(setbin= AUTO, ret = 0)),
                                Fitem("SAME", sample_tests[0],  r0 = pFail(goto = "NEXT"),r2 = pPass(goto = "NEXT")),
                                profile_tests[0],
                                Fitem("SAME", sample_tests[1],  r0 = pFail(ret = 0), r2 = pPass(goto = "CTRL_X_RUNCALLBACK_K_TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGPASS"), 
                                r3 = pPass(goto = "CTRL_X_RUNCALLBACK_K_TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGPASS"), r4 = pPass(goto = "CTRL_X_RUNCALLBACK_K_TESTPLANSTARTFLOW_X_X_X_X_TPSFLAGPASS")),
                                Fitem("SAME", pinprofiler_tests[0], edc=True, r0 = pPass(ret = 1)),
                                Fitem("SAME", rnclbk_tests[1],  r0 = pFail(setbin= AUTO, ret = 0),r2 = pFail(setbin= AUTO, ret = 0)) )
TESTPLANENDFLOW_Subflow = Flow('TPI_BASE_XXX_TESTPLANENDFLOW',
                               Fitem("SAME", pinprofiler_tests[1], edc=True, r0 = pFail(setbin= AUTO)),
                               chk_flag,
                               Fitem("SAME", scrn_tests[3], rm2 = pFail( setbin=-93, goto = "CTRL_X_PWR_K_TESTPLANENDFLOW_X_X_X_X_PWRDWNPKG"), rm1 = pFail( setbin=-93, goto = "CTRL_X_PWR_K_TESTPLANENDFLOW_X_X_X_X_PWRDWNPKG"),
                               r0 = pFail(setbin = AUTO, goto ="NEXT"), r1= pPass(goto = "CTRL_X_PWR_K_TESTPLANENDFLOW_X_X_X_X_PWRDWNPKG"), r2 = pPass(goto ="NEXT"), r3 = pFail(setbin = AUTO, goto ="NEXT"), r4 = pPass(goto ="NEXT")),
                               Fitem('SAME', bin_settr_tests[0], r0 = pFail(goto = "NEXT"), rm2 = pFail(setbin=-93, goto = "NEXT"), rm1 = pFail(setbin=-93, goto = "NEXT"), r2 = pFail(goto = "NEXT")),  
                               Fitem('SAME', bin_settr_tests[1], r0 = pFail(goto = "NEXT"), rm2 = pFail(setbin=-93, goto = "NEXT"), rm1 = pFail(setbin=-93, goto = "NEXT"), r2 = pFail(goto = "NEXT")),
                               pwr_dwn, 
                               profile_tests[1])                              
                                              
### Main Test Flow ####
START_Subflow = Flow('TPI_BASE_XXX_START', 
                    Fitem("SAME", aux_tests[0], r0 = pFail(setbin= AUTO, ret = 0),r2 = pFail(setbin= AUTO, ret = 0)),
                    reset_metrics,
                    Fitem("SAME", aux_tests[1], r0 = pFail(setbin= AUTO, ret = 0),r2 = pFail(setbin= AUTO, ret = 0)),
                    Fitem("SAME", aux_tests[2], r0 = pFail(setbin= 6905, ret = 0)),
                    clear_start_topflow_flag,
                    tosutil_tests[1],
                    Fitem("SAME", rnclbk_tests[2], r0 = pFail(setbin= AUTO, ret = 0),r2 = pFail(setbin= AUTO, ret = 0)),
                    offline_setup, offline_gsds)

STARTPOST_SubFlow = Flow('TPI_BASE_XXX_STARTPOST', set_start_topflow_flag)

STARTPREPLR1_Subflow = Flow('TPI_BASE_XXX_STARTPREPRL1',
                        Fitem('SAME', scrn_tests[4], r0=pFail(setbin=AUTO, ret = 0), r2=pFail(setbin=7299, ret = 0)),
                        Fitem('SAME', scrn_tests[5], r0=pFail(setbin=AUTO, ret = 0), r2=pFail(setbin=AUTO, ret = 0), r3=pFail(setbin=AUTO, ret = 0)),
                        Fitem('SAME', scrn_tests[6], r0=pFail(setbin=AUTO, ret = 0), r2=pPass(goto = "NEXT")),
                        Fitem("SAME", scrn_tests[7], r0 = pFail(setbin= AUTO, ret = 0), r2=pPass(goto = "NEXT"))
                        )

BEGIN_Subflow = Flow('TPI_BASE_XXX_BEGIN', Fitem("SAME", rnclbk_tests[3], r0 = pFail(setbin= AUTO, ret = 0)))

#commented for now, enable when thermal setup is ready to be included
#LTTC_SubFlow = Flow('TPI_BASE_XXX_LTTC',
#                    Fitem("SAME", aux_tests[4], r0 = pFail(setbin= AUTO, ret = 0),r1 = pPass(ret = 1), r2 = pPass(goto = "NEXT")),
#                    Fitem("SAME", aux_tests[5], r0 = pFail(setbin= AUTO, ret = 0),r2 = pPass(ret = 2)))

FINAL_SubFlow = Flow(f'TPI_BASE_XXX_FINAL',
                    Fitem("SAME", metricrate_test, r1=pPass(goto="CTRL_X_RUNCALLBACK_K_FINAL_X_X_X_X_PRINTMETRICS"), r2=pPass(goto="CTRL_X_SCREEN_K_FINAL_X_X_X_X_REJECTFORK")),
                    print_metrics,
                    RejectFork)

FACT_SubFlow = Flow('TPI_BASE_XXX_FACT',
                    Fitem("SAME", aux_tests[3], r0 = pFail(setbin= AUTO, ret = 0),r2 = pPass(ret = 2)),
                    Fitem("SAME", scrn_tests[0], r0 = pFail(setbin= AUTO, ret = 0),r2 = pFail(setbin= AUTO, ret = 0))
                    )
                    

ALARM_SubFlow = Flow('TPI_BASE_XXX_ALARM', Fitem("SAME", scrn_tests[2], rm2 = pFail(ret = 1), rm1 = pFail(ret = 1), r0 = pFail(setbin= AUTO, ret = 0), r2 = pPass(ret = 1), r3 = pFail(setbin= AUTO, ret = 0)))
                    


