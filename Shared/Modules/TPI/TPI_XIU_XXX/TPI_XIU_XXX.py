# PKG TPI_XIU Module pymtpl source code.
# Output for prime13 and TOS4.
#from pyclbr import Function
#from typing import Any
from pymtpl.por_methods import PowerSequenceHandler, PrimeApplyTestConditionTestMethod, TesterScreenTC, PrimeTiuIdentityTestMethod, PrimeScreenTestTestMethod, PrimeTdrCalibrationTestMethod, RunCallback, PrimeTiuPowerSupplyContinuityTestMethod, PrimeTiuResistanceTestMethod, PrimeTiuSignalPinLeakageTestMethod, PrimeApplyTestConditionTestMethod, UserCodeTC, PrimeFunctionalTestMethod, AuxiliaryTC
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

# Initialize the module by defining the output mtpl path and the module name
# InitializeNVLClass('./TPI_XIU_XXX',  'TPI_XIU_XXX', tosversion="tos4") 
InitializeNVLClass('TPI_XIU_XXX',  'TPI_XIU_XXX', tosversion="tos4")

# Define import header
Import("TPI_XIU_XXX.usrv")
Import ("TPI_XIU_XXX.lvl")
Import ("TPI_XIU_XXX_levels.tcg")

# Define the subflow where the module place at.
subflw_init  = "INIT"

# Define Test Instance and Flowitems for INIT subflow

#XIU bypass for offline
XIU_BYPASS= TesterScreenTC(
    name = f"CTRL_X_TESTERSCREEN_K_{subflw_init}_X_X_X_X_XIUBYPASS",
    #BypassPort = 1,
    #Port 5 goes out if it is OFFLINE, Port 1- 4 goes to next test instance.
    _fitem = Fitem('SAME', r0=pPass(goto = "CTRL_X_XIUIDENTITY_K_INIT_X_X_X_X_XIUNAME"), r1=pPass(goto = "CTRL_X_XIUIDENTITY_K_INIT_X_X_X_X_XIUNAME"), r2=pPass(goto = "CTRL_X_XIUIDENTITY_K_INIT_X_X_X_X_XIUNAME"), r3 =pPass(goto = "CTRL_X_XIUIDENTITY_K_INIT_X_X_X_X_XIUNAME"),r4=pPass(goto = "CTRL_X_XIUIDENTITY_K_INIT_X_X_X_X_XIUNAME"),r5=pPass(ret = 1))                       
    )

#XIU Power Down.
XIU_PWRDWN = PrimeApplyTestConditionTestMethod(
    name = f'CTRL_X_PWRDWN_K_{subflw_init}_X_X_X_X_SET_DEFAULT_RELAY',
    TestConditionCategory = "RELAY",
	TestConditionName = "TPI_XIU_XXX::Rly_set_default_PKG_all_default",
	_fitem = Fitem('SAME', r0=pFail(ret = 0))
    )


#XIU INIT POWERUPTCDC. DC test set power to zero
PWRUP_TCDC= PowerSequenceHandler(
    name = f"CTRL_X_PWR_K_{subflw_init}_X_X_X_X_PWRUPTCDC",
    _comment = "1st test in the flow, power up ",
    ApplyPowerDown = "Always", 
	ApplyPowerOn = "Always", 
    PowerDownTc = "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
	PowerOnTc = "BASE::Power_Up_TC_DC_PKG_force_0V_lvl",
     _fitem = Fitem('SAME', r0=pFail(ret = 0))                       
    )
#list of screen tests in INIT
scrn_init_test_name = ["TIUID", "TIUPACKAGE", "TIUTYPE"]

#screentest parameter for each scrn_init_test_name
screentest_set = {"TIUID": "TIUIDASSIGNMENTS", "TIUPACKAGE": "TIUPACKAGE_S_H_A", "TIUTYPE": "TIU_HVM_DBG"}

scrn_init_test = []  #empty list that will contain the ScreenTC tests in INIT
for init1_test in scrn_init_test_name:
    init1_flow = PrimeScreenTestTestMethod(
    name = f"CTRL_X_SCREEN_K_{subflw_init}_X_X_X_X_{init1_test}",
    ScreenTestSet = screentest_set[init1_test],
    ScreenTestsFile = "./InputFiles/TiuId_ScreenTest.json",
     )
    scrn_init_test.append(init1_flow)     

#This test to validate that the TIU currently installed is the correct TIU intended for the Test Program.
#TiuIdentity Test Method will read the TIU name from tester and match it against the list of Regex specified in ValidTiuRegex parameter. 
# Once the match is found, the test method will load the TIU name to "SCVars.TP_TESTBOARD_ID" uservar.
XIUNAME= PrimeTiuIdentityTestMethod (
    name = f"CTRL_X_XIUIDENTITY_K_{subflw_init}_X_X_X_X_XIUNAME",
     ValidTiuRegex = Spec('__shared__::TpRule.If_CLASS_NVL_HX28C("^BB2T4H1P[0-9]+:NVLHX[a-zA-Z0-9]+[T|F][0-9]+$","^BB2T4H1P[0-9]+:NVL[S|A|W|H][L|B][0-9]+[T|F][0-9]+$")'),
     _comment = 'NVL XIU Name',
	 ValidElastomerSheetRegex = Spec('__shared__::TpRule.If_DS0_DS1_M("I01954L1010E[0-9]*","I01954L1010E[0-9]*","","")'),
	 ValidBottomElastomerSheetRegex = Spec('__shared__::TpRule.If_DS0_DS1_M("I01954L1020E[0-9]*","I01954L1020E[0-9]*","","")'),
    _fitem = Fitem('SAME', r0=pFail(ret = 0))                       
    )

# TIU ID to check if CTA if it is HVM or debug TIU
#TIUID= PrimeScreenTestTestMethod (
#    name =f"CTRL_X_SCREEN_K_{subflw_init}_X_X_X_X_TIUID",
#    ScreenTestSet = "TIUIDASSIGNMENTS",
#    ScreenTestsFile = "./InputFiles/TiuId_ScreenTest.json",
#	_fitem = Fitem('SAME', r0=pFail(ret = 0))
#    )

# Check if load correct TIU

#TIUPACKAGE = PrimeScreenTestTestMethod (
#     name = f" CTRL_X_SCREEN_K_{subflw_init}_X_X_X_X_TIUPACKAGE",
#    ScreenTestSet = "TIUPACKAGE_S_H_A", # if it is S,H or A type of TIU
#    ScreenTestsFile = "./InputFiles/TiuId_ScreenTest.json",
#	_fitem = Fitem('SAME', r0=pFail(ret = 0))
#   )
#Calibration of Time Domain Reflectometry (TDR)
#The test method will do TIU Time-Domain Reflectometry (TDR) Calibration and store it into a calibration file
TDRCAL = PrimeTdrCalibrationTestMethod(
    name = f'CTRL_X_TDRCAL_K_{subflw_init}_X_X_X_X_TDRCLIBRATION',
    #TDR clibration
    PinGroups = "all_tdr",
    TdrHiLimit = "16.2E-9S",
    TdrLoLimit = "2.2E-9S",
    AlwaysExecute = "FALSE",
    #BypassPort = 1,
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )

#TDR LOG
TDRLOG = RunCallback (
name = 	f'CTRL_X_RUNCALLBACK_K_INIT_X_X_X_X_TDRLOG',
#TDR log
    Callback = "LogFile", #USER TODO: define value
    BypassPort = Spec('toInteger(__shared__::SCVars.SC_TDRLOG)'),
    PostInstance = "WriteUserVar(--uservar __shared__::SCVars.SC_TDRLOG --value 1 --type String)",
    Parameters = "--directory D:/Calibration --file TDRFile_BB2T4H1P*.txt --altname TDR",
	_fitem = Fitem('SAME', r0=pFail(ret = 0))

)

#check XIU CONTINUITY - TIU Power Supple Continuity Test it to validate the digital power supply pins (DPS) on the TIU is in good condition for test to be executed.
#execute DC current measurements on specified pins in the parameter "Pins"
XIU_CONTINUITY = PrimeTiuPowerSupplyContinuityTestMethod(
    name = f'CTRL_X_XIUPOWERSUPPLY_K_{subflw_init}_X_X_X_X_XIUCONTINUITY',
    LevelsTc = "TPI_XIU_XXX::all_tpi_xiucontinuity_x_x_pkg_level_force_0V_lvl", #USER TODO: define value
	HighLimit =Spec('__shared__::TpRule.If_DS0_DS1_M ("0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49", "0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49", "0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49", "0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49,0.49")'),
	LowLimit = Spec('__shared__::TpRule.If_DS0_DS1_M ("-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49", "-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49", "-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49", "-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49,-0.49")'),
	Pins = Spec('__shared__::TpRule.If_DS0_DS1_M(TPI_XIU_XXX::Continuity.s28c_continuity,TPI_XIU_XXX::Continuity.s52c_continuity, TPI_XIU_XXX::Continuity.hx28c_continuity, TPI_XIU_XXX::Continuity.s28c_continuity)'),
     _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )

#XIU RESISTANCE test is to calculate the resistance of specified pins based on DC Test Current Measurement. it is not been used bypassed for now 
#XIU_RESISTANCE = PrimeTiuResistanceTestMethod(
#    name = f'CTRL_X_XIURESISTANCE_K_{subflw_init}_X_X_X_X_XIURESISTANCE',
#    BypassPort = 1,
#	LevelsTc ="TPI_XIU_XXX::all_tpi_xiuleakage_x_s28c_hvm_level_force_0V_lvl" ,
#	Pins = "pkg_dpin_nvl_s28c_hvm_leakage",
#    _fitem = Fitem('SAME', r0=pFail(ret = 0))
#    )
	
	
# check if it is HVM or DBG TIU	
#TIUTYPE = PrimeScreenTestTestMethod (
#     name = f" CTRL_X_SCREEN_K_{subflw_init}_X_X_X_X_TIUTYPE",
#    ScreenTestSet = "TIU_HVM_DBG", # if it is S,H or A type of TIU
#    ScreenTestsFile = "./InputFiles/TiuId_ScreenTest.json",
#	_fitem = Fitem ('SAME', r0=pFail(ret = 0), r1=pPass(goto = "CTRL_X_XIUPINLEAKGE_K_INIT_X_X_X_X_XIUHVMLEAKAGE"), r2=pPass(goto = "CTRL_X_XIUPINLEAKGE_K_INIT_X_X_X_X_XIUDBGLEAKAGE"))
#   )
   
#XIU LEAKAGE test is to validate the signal pins on the TIU is in good condition for test to be executed. 
# check socket integrity and debris -apply 1V to all DPings and DPSs.
#XIU_HVMLEAKAGE= PrimeTiuSignalPinLeakageTestMethod(
#    name = f"CTRL_X_XIUPINLEAKGE_K_{subflw_init}_X_X_X_X_XIUHVMLEAKAGE",
#    LevelsTc = Spec(' __shared__::TpRule.If_DS0_DS1_M("TPI_XIU_XXX::all_tpi_xiuleakage_x_s28c_hvm_level_force_0V_lvl","TPI_XIU_XXX::all_tpi_xiuleakage_x_s52c_hvm_level_force_0V_lvl","TPI_XIU_XXX::all_tpi_xiuleakage_x_hx28c_hvm_level_force_0V_lvl","TPI_XIU_XXX::all_tpi_xiuleakage_x_s28c_hvm_level_force_0V_lvl")'),
#	Pins = Spec('__shared__::TpRule.If_DS0_DS1_M(TPI_XIU_XXX::HVM_Leakage.s28c_hvmleakage,TPI_XIU_XXX::HVM_Leakage.s52c_hvmleakage, TPI_XIU_XXX::HVM_Leakage.hx28c_hvmleakage, TPI_XIU_XXX::HVM_Leakage.s28c_hvmleakage)'), 
#	HighLimit = Spec('__shared__::TpRule.If_DS0_DS1_M("0.000069","0.000069","0.000069","0.000069")'),
#	LowLimit = Spec('__shared__::TpRule.If_DS0_DS1_M("-0.00000489","-0.00000489","-0.00000489","-0.00000489")'),
#    BypassPort = Spec( '__shared__::TpRule.If_DS0_DS1_M (-1,1,1,1)'),
#    _fitem = Fitem('SAME', r0=pFail(ret = 0), r1=pPass(goto = "CTRL_X_USERCODE_K_INIT_X_X_X_X_CLKCHIPINIT"))                       
#    )
#
##XIU LEAKAGE test is to validate the signal pins on the TIU is in good condition for test to be executed. 
## check socket integrity and debris -apply 1V to all DPings and DPSs.
#XIU_DBGLEAKAGE= PrimeTiuSignalPinLeakageTestMethod(
#    name = f"CTRL_X_XIUPINLEAKGE_K_{subflw_init}_X_X_X_X_XIUDBGLEAKAGE",
#    LevelsTc = Spec('__shared__::TpRule.If_DS0_DS1_M("TPI_XIU_XXX::all_tpi_xiuleakage_x_s28c_dbg_level_force_0V_lvl","TPI_XIU_XXX::all_tpi_xiuleakage_x_s52c_dbg_level_force_0V_lvl","TPI_XIU_XXX::all_tpi_xiuleakage_x_hx28c_dbg_level_force_0V_lvl","TPI_XIU_XXX::all_tpi_xiuleakage_x_s28c_dbg_level_force_0V_lvl")'),
#	Pins =Spec( '__shared__::TpRule.If_DS0_DS1_M(TPI_XIU_XXX::DBG_Leakage.s28c_dbgleakage,TPI_XIU_XXX::DBG_Leakage.s52c_dbgleakage, TPI_XIU_XXX::DBG_Leakage.hx28c_dbgleakage, TPI_XIU_XXX::DBG_Leakage.s28c_dbgleakage)'), 
#	HighLimit = Spec('__shared__::TpRule.If_DS0_DS1_M("0.000069","0.000069","0.000069","0.000069")'),
#	LowLimit = Spec('__shared__::TpRule.If_DS0_DS1_M("-0.00000489","-0.00000489","-0.00000489","-0.00000489")'),
#    BypassPort =  Spec('__shared__::TpRule.If_DS0_DS1_M (-1,1,1,1)'),
#    _fitem = Fitem('SAME', r0=pFail(ret = 0),r1=pPass(goto = "CTRL_X_USERCODE_K_INIT_X_X_X_X_CLKCHIPINIT"))                       
#    )

#PO no rules to apply yet
XIU_HVMLEAKAGE= PrimeTiuSignalPinLeakageTestMethod(
    name = f"CTRL_X_XIUPINLEAKGE_K_{subflw_init}_X_X_X_X_XIUHVMLEAKAGE",
    LevelsTc = 'TPI_XIU_XXX::all_tpi_xiuleakage_x_s28c_hvm_level_force_0V_lvl',
	Pins = Spec('__shared__::TpRule.If_DS0_DS1_M("pkg_dpin_nvl_s28c_hvm_leakage","pkg_dpin_nvl_s52c_hvm_leakage", "pkg_dpin_nvl_hx28c_hvm_leakage", "pkg_dpin_nvl_s28c_hvm_leakage")'), 
	HighLimit = '0.0000069',
	LowLimit = '-0.00000489',
    BypassPort = Spec( '__shared__::TpRule.If_DS0_DS1_M (-1,1,-1,1)'),
    _fitem = Fitem('SAME', r0=pFail(ret = 0), r1=pPass(goto = "CTRL_X_USERCODE_K_INIT_X_X_X_X_CLKCHIPINIT"))                       
    )

#XIU LEAKAGE test is to validate the signal pins on the TIU is in good condition for test to be executed. 
# check socket integrity and debris -apply 1V to all DPings and DPSs.
XIU_DBGLEAKAGE= PrimeTiuSignalPinLeakageTestMethod(
    name = f"CTRL_X_XIUPINLEAKGE_K_{subflw_init}_X_X_X_X_XIUDBGLEAKAGE",
    LevelsTc = 'TPI_XIU_XXX::all_tpi_xiuleakage_x_s28c_dbg_level_force_0V_lvl',
	Pins =Spec( '__shared__::TpRule.If_DS0_DS1_M("pkg_dpin_nvl_s28c_dbg_leakage","pkg_dpin_nvl_s52c_dbg_leakage", "pkg_dpin_nvl_hx28c_dbg_leakage", "pkg_dpin_nvl_s28c_dbg_leakage")'), 
	HighLimit = '0.0000069',
	LowLimit = '-0.00000489',
    BypassPort =  Spec('__shared__::TpRule.If_DS0_DS1_M (-1,1,-1,1)'),
    _fitem = Fitem('SAME', r0=pFail(ret = 0),r1=pPass(goto = "CTRL_X_USERCODE_K_INIT_X_X_X_X_CLKCHIPINIT"))                       
    )

#CLKCHIP Setting
CLKCHIPINIT = UserCodeTC(
	name = f'CTRL_X_USERCODE_K_{subflw_init}_X_X_X_X_CLKCHIPINIT',
	InputFile = "./InputFiles/ClkChipInit.cs",
	Method = "Main",
	NamespaceClass = "TPI.ClkChipInit",
	#BypassPort = 1, ## REMOVE THIS LATER ONCE TIUCHECK is ENABLED
	_fitem = Fitem('SAME', r0=pFail(ret = 0))
)


# Define above tests in INIT Flow

INIT = Flow(f'TPI_XIU_XXX_INIT', XIU_PWRDWN, PWRUP_TCDC, XIU_BYPASS, XIUNAME, 
            Fitem("SAME", scrn_init_test[0], r0=pFail(ret = 0)),Fitem("SAME", scrn_init_test[1], r0=pFail(ret = 0)), TDRCAL, TDRLOG, XIU_CONTINUITY,\
		    Fitem("SAME", scrn_init_test[2], r0=pFail(ret = 0),r1=pPass(goto = "CTRL_X_XIUPINLEAKGE_K_INIT_X_X_X_X_XIUHVMLEAKAGE"),r2 = pPass(goto = "CTRL_X_XIUPINLEAKGE_K_INIT_X_X_X_X_XIUDBGLEAKAGE")),XIU_HVMLEAKAGE, XIU_DBGLEAKAGE,CLKCHIPINIT)



#################################
########### FFPKG FLOW ##########
#################################

CLKCHIP_READ = PrimeFunctionalTestMethod(
    name = f'CTRL_X_USERCODE_K_PKGFF_X_X_X_X_CLKCHIPREAD',
    Patlist = f'IPP::mtpi_rtc_clkchip_val_hvm_list',
    TimingsTc = f'IPP::PCD_IP_BASE::pcd_fun_timing_mts800_tstprtclk400_tck100',
    LevelsTc = f'IPP::PCD_IP_BASE::pcd_all_bf_x_x_ipp_lvl_min',
    FailuresToCaptureTotal = Spec('10'),
    FailuresToCapturePerPattern = Spec('10'),
    MaxFailuresToItuff = Spec('10'),
    MaxFailuresPerPatternToItuff = Spec('10'),
    ProcessFailuresPlugin = f'Prime.Plugins.Functional.FailuresToDatalog',
    FunctionalTestPlugin = f'FrequencyMeasurePlugin',
    FunctionalTestPluginInput = Spec('GetEnvironmentVariable("~HDMT_TPL_DIR")+ "/Shared/Modules/TPI/TPI_XIU_XXX/InputFiles/ClkChipFreqMeasure.json"'),
    LogLevel = f'Enabled',
    BypassPort = 1,
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
    
)

CLKCHIP_CHECK = AuxiliaryTC(
    name = f'CTRL_X_USERCODE_K_PKGFF_X_X_X_X_CLKCHIPCHECK',
    DataType = f'Double',
    Datalog = f'Enabled',
    Expression = f'[G.U.D.PCD_ClkChipOutputMonitor_FREQ]',
    ResultPort = f'[R]<3.9 || [R]>4.1 ? 0 : 1',
    Storage = f'SharedStorage',
    BypassPort = 1,
    _fitem = Fitem('SAME', r0=pFail(ret = 0))
)

PKGFF = Flow(f'TPI_XIU_XXX_PKGFF', CLKCHIP_READ, CLKCHIP_CHECK)

