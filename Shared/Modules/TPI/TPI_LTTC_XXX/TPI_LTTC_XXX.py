# PKG TPI Evmin Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import AuxiliaryTC, PrimeThermalSingleMeasurementTestMethod, PrimeThermalEndOfTestTestMethod, PrimeThermalControlSetTestMethod, PrimeApplyTestConditionTestMethod, PrimeThermalRampTestMethod, RunCallback
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  NativeMultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./TPI_LTTC_XXX',  'TPI_LTTC_XXX', tosversion="tos4", binrange=(94939700, 94939799),
                   defaultrm2bin=(99949700, 99949799),
                   defaultrm1bin=(98949700, 98949799))

Import("TPI_LTTC_XXX.usrv")

#LTTC subflows
subflw_lttc1 = "LTTCRAMP"
subflw_lttc2 = "LTTCPOST"

##################
# LTTCRAMP tests #
##################

#Auxiliary test list and dicctionary
aux_test_list = ["BENCHTOP_FORK", "DISABLE_EOT", "ENABLE_SOT","DISABLE_SOT", "ENABLE_EOT", "ENABLE_LTTC"]
aux_exprssion = {"BENCHTOP_FORK": "[__shared__::SCVars.SC_BENCHTOP]", "DISABLE_EOT": "1" , "ENABLE_SOT": "-1", "DISABLE_SOT": "1", "ENABLE_EOT": "-1", "ENABLE_LTTC": "-1"}
aux_token = {"BENCHTOP_FORK": None, "DISABLE_EOT": "__shared__::PTHVars.bypass_eot" , "ENABLE_SOT": "__shared__::PTHVars.bypass_sot", "DISABLE_SOT": "__shared__::PTHVars.bypass_sot", "ENABLE_EOT": "__shared__::PTHVars.bypass_eot", "ENABLE_LTTC": "__shared__::PTHVars.bypass_lttc"}
#aux_data = {"BENCHTOP_FORK": "String", "DISABLE_EOT": "Integer" , "ENABLE_SOT": "Integer", "DISABLE_SOT": "Integer", "ENABLE_EOT": "Integer", "ENABLE_LTTC": "Integer"}
#aux_port =  {"BENCHTOP_FORK": "[R]=='1'?1:2", "DISABLE_EOT": None , "ENABLE_SOT": None, "DISABLE_SOT": None, "ENABLE_EOT": None, "ENABLE_LTTC": None}

aux_tests = []  #empty list that will contain the AuxiliaryTC tests
for auxtest in aux_test_list:
    auxtest_flow = AuxiliaryTC(
    name = f"LTTC_X_AUX_E_{subflw_lttc1}_X_X_X_X_{auxtest}",
    DataType = "String" if auxtest == "BENCHTOP_FORK" else "Integer",
    Storage = "UserVar",
    ResultPort = "[R]=='1'?1:2" if auxtest == "BENCHTOP_FORK" else None,
    Expression = aux_exprssion[auxtest],
    ResultToken = aux_token[auxtest],
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)') if auxtest == "BENCHTOP_FORK" else Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1)'),  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
     )
    aux_tests.append(auxtest_flow)

#SingleMeasurementTestMethod
sm_test_list = ["START", "START_SOT", "TJ"]
sm_integhi = {"START":200, "START_SOT": 200, "TJ": 200}
sm_integlo = {"START":130, "START_SOT": 130, "TJ": 130}
sm_lowtolerance = {"START":Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")'), "START_SOT": Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("95,95,95,95","95,95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95","95,95,95,95")'), "TJ": Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")')}
sm_uptolerance  =  {"START": Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")'), "START_SOT": Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("5,5,5,5","5,5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5","5,5,5,5")'), "TJ": Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")')}

sm_tests = []  #empty list that will contain the AuxiliaryTC tests
for single_measurement in sm_test_list:
    sm_flow = PrimeThermalSingleMeasurementTestMethod(
    name = f"LTTC_X_TDAU_E_{subflw_lttc1}_X_X_X_X_{single_measurement}",
    IntegrityHighLimit = sm_integhi[single_measurement],
    IntegrityLowLimit = sm_integlo[single_measurement],
    LowerTolerance = sm_lowtolerance[single_measurement],
    PinNames = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance = sm_uptolerance[single_measurement],
    ContinuousRead = "Enabled" if single_measurement == "START_SOT" else None,
    MeasurementType = "SOT" if single_measurement == "START_SOT" else None,
BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)') if single_measurement =="TJ" else Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,1,-1,1,-1,-1,-1,-1,-1,-1,-1,1)'),  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
)
    sm_tests.append(sm_flow)

tdau_start_eot = PrimeThermalEndOfTestTestMethod(
    name =  f"LTTC_X_TDAU_E_{subflw_lttc1}_X_X_X_X_START_EOT",
    LowerTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")'),
    PcsDatalogSelector = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("0,1,2,3","0,1,2,3,4","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3")'),
    PinNames = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0")'),
    PreInstance = "WriteSharedStorage(--token G.U.D.PCS_SOT_THERMAL_HEAD_TEMPERATURE_READ --value -6666666 )", #get NVL values from PTH
    UpperTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")'),
    PostInstance = "DtsEndOfDevice()",
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,1,-1,1,-1,-1,-1,-1,-1,-1,-1,1)'),  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
)

#Thermal Control tests
tc_test_list = ["START_LTTC20", "LTTC20PF"]
tc_cs = {"START_LTTC20": "LTTC20", "LTTC20PF": "LTTC20"}
tc_pin = {"START_LTTC20": "IPC::UEISLAVE_IPC", "LTTC20PF": "IPC::UEISLAVE_IPC"}

tc_tests = [] 
for thermal_control in tc_test_list:
    tc_flow = PrimeThermalControlSetTestMethod(
    name = f"LTTC_X_CS_E_{subflw_lttc1}_X_X_X_X_{thermal_control}",
    ControlSet = tc_cs[thermal_control],
    UeiPinName = tc_pin[thermal_control],
    #PostInstance = "Sleep(10000)" if thermal_control == "START_LTTC20" else None,
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)') if thermal_control == "START_LTTC20" else Spec(1)  ,  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
     )
    tc_tests.append(tc_flow)

#Apply Test Condition tests
applytc_test_list = ["START_STOPCNV", "START_SCOCAL"]
applytc_name = {"START_STOPCNV": Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S52CPP","TDAU_EOT_TC_ROOM_HX28CPP","TDAU_EOT_TC_ROOM_H16CPP","TDAU_EOT_TC_ROOM_HX28CPP","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S28CPP")'), "START_SCOCAL": Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S52CPP","TDAU_SCOC_TC_ROOM_HX28CPP","TDAU_SCOC_TC_ROOM_H16CPP","TDAU_SCOC_TC_ROOM_HX28CPP","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S28CPP")')}

applytc_tests = []  #empty list that will contain the AuxiliaryTC tests
for apply_tc in applytc_test_list:
    applytc_flow = PrimeApplyTestConditionTestMethod(
    name = f"LTTC_X_CS_E_{subflw_lttc1}_X_X_X_X_{apply_tc}",
    TestConditionCategory = "THERMAL",
    TestConditionName = applytc_name[apply_tc],
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(1,-1,1,1,1,1,1,1,1,1,1,1,1)'),
     )
    applytc_tests.append(applytc_flow)

#CSharpTest PrimeThermalRampTestMethod TD_X_SOAK_K_LTTC_X_X_X_X_START_LTTCSOAK
#{
#	IntegrityHighLimit = 200;
#	IntegrityLowLimit = 130;
#	LogPinToken = "5,6,7,8";
#	LowerTolerance = "30,10,10,10";#
#	PinNames = "IP_CPU::TDAU_CH_CORE, IP_PCH::TDAU_CH_GCD, IP_PCH::TDAU_CH_IOE, TDAU_CH_SOC";#
#	RampMode = "Soak";
#	SetPoints = PTHVars.TJSETPOINT_LTTC;
#	Timeout = 60000;
#	UpperTolerance = "30,10,10,10";#
#	#BypassPort = PTH_THRSOAK_XXX_Rules.If_CH_CHVM(-1,1);
#}

thermal_ramp= PrimeThermalRampTestMethod(
    name =  f"LTTC_X_TDAU_E_{subflw_lttc1}_X_X_X_X_START_LTTCSOAK",
    IntegrityHighLimit = 200,
    IntegrityLowLimit = 130,
    LogPinToken = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("1,3","1,2,3,4,5","1,2,3,4","1,2,3,4","1,2,3,4","1,3","1,3","1,3","1,3","1,3","1,3","1,3","1,3")'),
    RampMode = "Soak",
    SetPoints = "20",
    Timeout = 60000,
    LowerTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("7,5","30,30,30,8,30","25,25,25,25","7,7,7,7","25,25,25,25","7,5","7,5","25,25","25,25","25,25","25,25","25,25","25,25")'),
    PinNames = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0")'),  # pos3(HX28C),pos4(H16C),pos5(P16C)=4-pin; pos6(DNL) and rest=2-pin same as S28C
    UpperTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("7,5","30,30,30,8,30","25,25,25,25","7,7,7,7","25,25,25,25","7,5","7,5","25,25","25,25","25,25","25,25","25,25","25,25")'),   
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)'),
)

#added for cold ideality
calc_flow = PrimeApplyTestConditionTestMethod(
    name = f"LTTC_X_CS_E_{subflw_lttc1}_X_X_X_X_LTTCCAL",
    TestConditionCategory = "LEVELS_POWER_DOWN",
    TestConditionName =Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S52CPP","TDAU_CAL_TC_ROOM_HX28CPP","TDAU_CAL_TC_ROOM_H16CPP","TDAU_CAL_TC_ROOM_HX28CPP","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S28CPP")'),
	BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(1,-1,1,1,1,1,1,1,1,1,1,1,1)'),
)

#prints tdau ideality
print_ideality = RunCallback(
					name = f"LTTC_X_CS_E_{subflw_lttc1}_X_X_X_X_PRINTIDEALITY",
					Callback = "PrintToItuff",
					Parameters = "--body_type strgval --body_data __shared__::PTHVars.CPU0_TDAU0_IDEALITY_DYNAMIC_Cold,|,__shared__::PTHVars.GCD_TDAU0_IDEALITY_DYNAMIC_Cold,|,__shared__::PTHVars.HUB_TDAU0_IDEALITY_DYNAMIC_Cold --tname_suf CPU_GCD_HUB_Ideality",
					BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,1)'),
					)

LTTCRAMP_SubFlow = Flow('TPI_LTTC_XXX_LTTCRAMP',
                    Fitem("SAME", aux_tests[0], edc = True, r0 = pFail(setbin= AUTO), r1 = pPass (ret = 1), r2 = pPass(goto="NEXT")),
                    Fitem("SAME", sm_tests[0], edc = True,  r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO), r3 = pFail(setbin= AUTO), r4 = pFail(setbin= AUTO), r5 = pFail(setbin= AUTO)),
                    Fitem("SAME", aux_tests[1], edc = True, r0 = pFail(setbin= AUTO), r2 = pPass(goto="NEXT")),
                    Fitem("SAME", tdau_start_eot, edc = True,  r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO), r3 = pFail(setbin= AUTO), r4 = pFail(setbin= AUTO), r5 = pFail(setbin= AUTO)),
                    Fitem("SAME", applytc_tests[0], edc = True, r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO)),
                    Fitem("SAME", print_ideality, edc = True, r0 = pFail(setbin= AUTO)),
                    Fitem("SAME", calc_flow, edc = True, r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO)),
                    Fitem("SAME", applytc_tests[1], edc = True, r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO)),
                    Fitem("SAME", tc_tests[0], edc = True, r0 = pFail(setbin= AUTO)),
                    Fitem("SAME", thermal_ramp, r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO), r3 = pFail(setbin= AUTO), r4 = pFail(setbin= AUTO), r5 = pFail(setbin= AUTO)),                   
                    Fitem("SAME", aux_tests[2], edc = True, r0 = pFail(setbin= AUTO),r2 = pPass(goto="NEXT")),
                    Fitem("SAME", sm_tests[1],  edc = True, r0 = pFail(setbin= AUTO), r2 = pFail(goto= "LTTC_X_AUX_E_LTTCRAMP_X_X_X_X_ENABLE_LTTC"), r3 = pFail(goto="LTTC_X_AUX_E_LTTCRAMP_X_X_X_X_ENABLE_LTTC"), r4 = pFail(goto="LTTC_X_AUX_E_LTTCRAMP_X_X_X_X_ENABLE_LTTC"), r5 = pFail(goto="LTTC_X_AUX_E_LTTCRAMP_X_X_X_X_ENABLE_LTTC")),
                    Fitem("SAME", aux_tests[3], edc = True, r0 = pFail(setbin= AUTO),r2 = pPass(goto="NEXT")),
                    Fitem("SAME", aux_tests[4], edc = True, r0 = pFail(setbin= AUTO), r2 = pPass(goto="NEXT")),
                    Fitem("SAME", aux_tests[5], edc = True, r0 = pFail(setbin= AUTO), r2 = pPass(goto="NEXT")),
                    Fitem("SAME", tc_tests[1], edc = True, r0 = pFail(setbin= AUTO)),
                    Fitem("SAME", sm_tests[2], edc = True, r0 = pFail(setbin= AUTO), r2= pFail(ret = 1) , r3 = pFail(ret = 1) , r4 = pFail(ret = 1) , r5 = pFail(ret = 1) ),
                    )

##################
# LTTCPOST tests #
##################

#Auxiliary test list and dicctionary
aux_test_list2 = ["BENCHTOP_FORK", "DISABLE_EOT", "ENABLE_LTTC"]
aux_exprssion2 = {"BENCHTOP_FORK":"[__shared__::SCVars.SC_BENCHTOP]", "DISABLE_EOT": "1", "ENABLE_LTTC": "-1"}
aux_token2 = {"BENCHTOP_FORK": None, "DISABLE_EOT": "__shared__::PTHVars.bypass_eot", "ENABLE_LTTC": "__shared__::PTHVars.bypass_lttc"}
#aux_data = {}
#aux_port =  {}

aux_tests2 = []  #empty list that will contain the AuxiliaryTC tests
for auxtest2 in aux_test_list2:
    auxtest_flow2 = AuxiliaryTC(
    name = f"LTTC_X_AUX_E_{subflw_lttc2}_X_X_X_X_{auxtest2}",
    DataType = "String" if auxtest2 == "BENCHTOP_FORK" else "Integer",
    Storage = "UserVar",
    ResultPort = "[R]=='1'?1:2" if auxtest2 == "BENCHTOP_FORK" else None,
    Expression = aux_exprssion2[auxtest2],
    ResultToken = aux_token2[auxtest2],
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)') if auxtest2 == "BENCHTOP_FORK" else Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1)')   ,  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
     )
    aux_tests2.append(auxtest_flow2)

sm_test2 = PrimeThermalSingleMeasurementTestMethod(
    name =  f"LTTC_X_TDAU_E_{subflw_lttc2}_X_X_X_X_FINAL",
    IntegrityHighLimit = 200,
    IntegrityLowLimit = 130,
    LowerTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")'), #get NVL values from PTH
    PinNames = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")'),
    UserVarStoreNames = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas4, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3")'),
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)'),  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
    )

tdau_final_eot = PrimeThermalEndOfTestTestMethod(
    name =  f"LTTC_X_TDAU_E_{subflw_lttc2}_X_X_X_X_FINAL_EOT",
    LowerTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("80,80,80,80","80,80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80","80,80,80,80")'),
    PcsDatalogSelector = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("4,5,6,7","4,5,6,7,8","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7")'),
    PinNames = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0")'),
    PreInstance =  "WriteSharedStorage(--token G.U.D.PCS_SOT_THERMAL_HEAD_TEMPERATURE_READ --value -6666666 )", #get NVL values from PTH
    UpperTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("30,30,30,30","30,30,30,30,30","30,30,30,30","60,60,60,60","60,60,60,60","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30")'),
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(__shared__::PTHVars.bypass_eot,1,1,1,1,__shared__::PTHVars.bypass_eot,__shared__::PTHVars.bypass_eot,__shared__::PTHVars.bypass_eot,__shared__::PTHVars.bypass_eot,__shared__::PTHVars.bypass_eot,__shared__::PTHVars.bypass_eot,__shared__::PTHVars.bypass_eot,1)'),  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
    )

tc_test2 = PrimeThermalControlSetTestMethod(
    name = f"LTTC_X_CS_E_{subflw_lttc2}_X_X_X_X_FACT",
    ControlSet = "FACT",
    UeiPinName = "IPC::UEISLAVE_IPC",
    BypassPort = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1)'),  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
    )

#not needed as this test will wait to meet temp setup. Fact subflow can run while temp is ramping up
temp_ramp2 = PrimeThermalRampTestMethod(
    name = f"LTTC_X_CS_E_{subflw_lttc2}_X_X_X_X_FACTSOAK",
    IntegrityHighLimit = 200,
	IntegrityLowLimit = 130,
	LogPinToken = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("1,2,3,4","1,2,3,4,5","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4")'),
	LowerTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("10,10,10,10","10,10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10")'),
	PinNames = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0")'),  # pos6 (CLASS_DNL_S28C) aligned to CLASS_NVL_S28C
    RampMode = "Soak",
	SetPoints = Spec("__shared__::PTHVars.TJSETPOINT_FACT"),
	Timeout = 60000,
	UpperTolerance = Spec('TPI_LTTC_XXX_Rules.Select_BOM_default("10,10,10,10","10,10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10","10,10,10,10")'),  # pos6=CLASS_DNL_S28C same as CLASS_NVL_S28C
    BypassPort = 1,
    )

LTTCPOST_SubFlow = Flow('TPI_LTTC_XXX_LTTCPOST',
                   Fitem("SAME", aux_tests2[0], edc = True, r0 = pFail(setbin= AUTO), r1 = pPass (ret = 1), r2 = pPass(goto="NEXT")),
                   Fitem("SAME", sm_test2, edc = True,  r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO, goto="NEXT"), r3 = pFail(setbin= AUTO, goto="NEXT"), r4 = pFail(setbin= AUTO, goto="NEXT"), r5 = pFail(setbin= AUTO, goto="NEXT")),
                   Fitem("SAME", aux_tests2[2], edc = True, r0 = pFail(setbin= AUTO), r2 = pPass(goto="NEXT")),
                   Fitem("SAME", tdau_final_eot, edc = True, r0 = pFail(setbin= AUTO), r2 = pFail(goto="NEXT"), r3 = pFail(goto="NEXT"), r4 = pFail(goto="NEXT"), r5 = pFail(goto="NEXT")),
                   Fitem("SAME", aux_tests2[1], edc = True, r0 = pFail(setbin= AUTO),r2 = pPass(goto="NEXT")),                   
                   Fitem("SAME", tc_test2, edc = True, r0 = pFail(setbin= AUTO)),
                   Fitem("SAME", temp_ramp2, edc = True,  r0 = pFail(setbin= AUTO), r2 = pFail(setbin= AUTO), r3 = pFail(setbin= AUTO), r4 = pFail(setbin= AUTO), r5 = pFail(setbin= AUTO)),
                   )