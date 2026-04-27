from pymtpl.por_methods import (PrimeApplyTestConditionTestMethod, AuxiliaryTC, 
                                 PrimeThermalControlSetTestMethod, PrimeThermalControlSetInitTestMethod,
                                 ScreenTC, PrimeThermalEndOfTestTestMethod,
                                 PrimeThermalSingleMeasurementTestMethod, PrimeThermalUeiStreamTestMethod,
                                 PrimeLogPcsTokensTestMethod, PrimePauseTestMethod, DTSBase,
                                 ULTLoggerTC, PrimeDffReadTestMethod, PTHGetSetGsdsDffTC)
from pymtpl.core import (Flow, Fitem, pPass, pFail, InitializeNVLClass, 
                         Import, Spec, AUTO,optional,required,BaseMethod)

class IntecTC(BaseMethod):
    def __init__(self,
                 name,
                 IntecJson=required,
                 PolarisApp=required,
                 Delay=optional,
                 PolarisTimeOut=optional,
                 FollowingSlope=required,
                 FollowingOffset=optional,
                 Feedback=required,
                 Tolerance=required,
                 Channels=required,
                 BypassPort=optional,
                 SetPoint=optional,
                 Operation=optional,
                 _comment=None,
                 _fitem=None,
                 ):
        self._init(name, locals())

# =============================================================================
# CONFIGURATION
# =============================================================================

MOD_NAME = "PTH_DIODE_XXX"
OUT_DIR = f"./{MOD_NAME}"

# =============================================================================
# INITIALIZATION
# =============================================================================

InitializeNVLClass(OUT_DIR, MOD_NAME, tosversion='tos4',binrange=(9752, 9752),defaultrm2bin=(99970000,99970999), defaultrm1bin=(98970000,98970999))

Import(f"{MOD_NAME}.usrv")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_ports(port_numbers, goto=None, setbin=None, ret=None):
    """Generate multiple ports with flexible configuration."""
    port_dict = {}
    for port_num in port_numbers:
        port_kwargs = {}
        if goto is not None: 
            port_kwargs['goto'] = goto
        if setbin is not None:
            port_kwargs['setbin'] = setbin
        if ret is not None: 
            port_kwargs['ret'] = ret
        port_dict[f"r{port_num}"] = pFail(**port_kwargs)
    return port_dict

# =============================================================================
# TEST DEFINITIONS
# =============================================================================

# Pymtpl marker - INIT
## Pymtpl marker - PrimeThermalControlSetInitTestMethod-cs_tcisetup
cs_tcisetup = PrimeThermalControlSetInitTestMethod(
    name="TD_X_CS_E_INIT_X_X_X_X_TCISETUP",
    TemperatureSetName=Spec('PTH_DIODE_XXX_Rules.PTHControlSetRule("MTL_CC_TCC","MTL_CH_TCC","MTL_FUSE_TCC","MTL_ROOM_TCC")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_tdsetup_init
applytc_tdsetup_init = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_INIT_X_X_X_X_TDSETUP",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.Select_by_BOM_and_LocationSets("TDAU_CAL_TC_S28CH","TDAU_CAL_TC_S52CH","TDAU_CAL_TC_S28CC","TDAU_CAL_TC_S52CC","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S52CPP","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_HX28CC","TDAU_CAL_TC_ROOM_HX28CPP","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_HX28CC","TDAU_CAL_TC_ROOM_HX28CPP","TDAU_CAL_TC_H16CH","TDAU_CAL_TC_H16CC","TDAU_CAL_TC_ROOM_H16CPP","TDAU_CAL_TC_S16CH","TDAU_CAL_TC_S16CC","TDAU_CAL_TC_ROOM_S16CPP","TDAU_CAL_TC_DNLS28CH","TDAU_CAL_TC_DNLS28CC","TDAU_CAL_TC_ROOM_DNLS28CPP","TDAU_CAL_TC_S28CH")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - ScreenTC-screen_btcheck_init
screen_btcheck_init = ScreenTC(
    name="TD_X_SCREEN_E_INIT_X_X_X_X_BTCHECK",
    ScreenTestSet="MTL_CLASS_BT_CHECK",
    ScreenTestsFile="./InputFiles/MTL_CLASS_BT_CHECK.txt",
    _fitem=Fitem("SAME", edc=True,
                 r0=pFail(ret=1),
                 r1=pPass(goto="NEXT"),
                 r2=pFail(ret=1))
)

## Pymtpl marker - IntecTC-intec_init
intec_init = IntecTC(
    name="TD_X_PARDATA_E_INIT_X_X_X_X_INTEC",
    IntecJson="./InputFiles/intec.json",
    PolarisApp="../../../../UserCode/lib/Release/net462/SetTemperature.exe",
    Delay=1,
    PolarisTimeOut=60000,
    FollowingSlope=Spec('__shared__::SCVars.SC_PF_SLOPE'),
    FollowingOffset=0,
    Feedback="PowerFollowing",
    Operation="Both",
    Tolerance=1,
    Channels="0",
    BypassPort=Spec('__shared__::SCVars.SC_INTEC_PF_ENABLED'),
    SetPoint="SC_TEMPERATURE",
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], setbin=AUTO, goto="NEXT"))
)

## Pymtpl marker - DTSBase-dtsbase
dtsbase = DTSBase(
    name="DTS_X_DTSBASE_K_INIT_X_X_X_X",
    ConfigurationFile = "./InputFiles/NVL_DTSBase_Config.json",
    _fitem=Fitem("SAME", edc=True,
                 r0=pFail(ret=0),
                 r1=pPass(ret=1))
)

# Pymtpl marker - START
## Pymtpl marker - AuxiliaryTC-aux_disable_sot_start
aux_disable_sot_start = AuxiliaryTC(
    name="TD_X_AUX_E_START_X_X_X_X_DISABLE_SOT",
    Expression="1",
    ResultToken="__shared__::PTHVars.bypass_sot",
    DataType="Integer",
    Storage="UserVar",
    Datalog="Enabled",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - AuxiliaryTC-aux_enable_eot_start
aux_enable_eot_start = AuxiliaryTC(
    name="TD_X_AUX_E_START_X_X_X_X_ENABLE_EOT",
    Expression="-1",
    ResultToken="__shared__::PTHVars.bypass_eot",
    DataType="Integer",
    Storage="UserVar",
    Datalog="Enabled",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_sot_bt_start
tdau_sot_bt_start = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_START_X_X_X_X_SOT_BT",
    BypassPort=Spec("PTH_DIODE_XXX.bypass_benchtop_inv"),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    MeasurementType="SOT",
    PostInstance="DtsStartOfDevice()",
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    UserVarStoreNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas4, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_sot_start
tdau_sot_start = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_K_START_X_X_X_X_SOT",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    ContinuousRead="Enabled",
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30,30,30","30,30,30,30"),__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","15,15,10,15"))'),
    MeasurementType="SOT",
    PostInstance="DtsStartOfDevice()",
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30,30,30","30,30,30,30"),__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","15,15,10,15"))'),
    UserVarStoreNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas4, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2")'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], setbin=AUTO, ret=0))
)

## Pymtpl marker - ScreenTC-screen_sot_set_global_start
screen_sot_set_global_start = ScreenTC(
    name="TD_X_SCREEN_E_START_X_X_X_X_SOT_SET_GLOBAL_USVR",
    ScreenTestSet="NVL_SET_GLOBAL_USERVAR",
    ScreenTestsFile="./InputFiles/NVL_SET_GLOBAL_USERVAR.txt",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - IntecTC-intec_start
intec_start = IntecTC(
    name="TD_X_PARDATA_E_START_X_X_X_X_INTEC",
    IntecJson="./InputFiles/intec.json",
    PolarisApp="../../../../UserCode/lib/Release/net462/SetTemperature.exe",
    Delay=1,
    PolarisTimeOut=60000,
    FollowingSlope=Spec('__shared__::SCVars.SC_PF_SLOPE'),
    FollowingOffset=0,
    Feedback="PowerFollowing",
    Tolerance=1,
    Channels="0",
    BypassPort=Spec('__shared__::SCVars.SC_INTEC_PF_ENABLED'),
    Operation="SetTemperature",
    SetPoint="SC_TEMPERATURE",
    _fitem=Fitem("SAME", edc=False,
                 r0=pFail(ret=0, setbin=AUTO),
                 r1=pPass(ret=1))
)

# Pymtpl marker - BEGIN
## Pymtpl marker - PrimeThermalControlSetTestMethod-cs_test
cs_test = PrimeThermalControlSetTestMethod(
    name="TD_X_CS_E_BEGIN_X_X_X_X_TEST",
    ControlSet="TEST",
    UeiPinName="IPC::UEISLAVE_IPC",
    BypassPort=-1,
    _fitem=Fitem("SAME", edc=True,
                 r0=pFail(ret=1),
                 r1=pPass(ret=1))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-cs_test_cpu
cs_test_cpu = PrimeApplyTestConditionTestMethod(
    name="TD_X_CS_E_BEGIN_X_X_X_X_TEST_CPU",
    BypassPort=1,
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.PTHControlSetRule("TEST_CC_TC","TEST_TC","TEST_RM_TC","TEST_RM_TC")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-cs_test_pch
cs_test_pch = PrimeApplyTestConditionTestMethod(
    name="TD_X_CS_E_BEGIN_X_X_X_X_TEST_PCH",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.PTHControlSetRule("IP_PCH::IP_PCH_BASE::TEST_PCH_CC_TC","IP_PCH::IP_PCH_BASE::TEST_PCH_TC","IP_PCH::IP_PCH_BASE::TEST_PCH_RM_TC","IP_PCH::IP_PCH_BASE::TEST_PCH_RM_TC")'),
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2], ret=1))
)

# Pymtpl marker - FINAL
## Pymtpl marker - AuxiliaryTC-aux_lttc_fork_final
aux_lttc_fork_final = AuxiliaryTC(
    name="TD_X_AUX_E_FINAL_X_X_X_X_LTTC_FORK",
    DataType="String",
    Expression="[__shared__::PTHVars.bypass_lttc]",
    Storage="UserVar",
    ResultPort='[R]==\'-1\'?1:2',
    PreInstance=Spec('__shared__::FlwSkpCollect.if_ahmt("","TimeTrackerReport")'),
    _fitem=Fitem("SAME", edc=True,
                 r0=pFail(goto="NEXT"),
                 r1=pPass(ret=1),
                 r2=pPass(goto="NEXT"))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_measurement_final
tdau_measurement_final = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_FINAL_X_X_X_X",
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    UserVarStoreNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas4, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.eotTempMeas2")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - AuxiliaryTC-aux_disable_eot_final
aux_disable_eot_final = AuxiliaryTC(
    name="TD_X_AUX_E_FINAL_X_X_X_X_DISABLE_EOT",
    Expression="1",
    ResultToken="__shared__::PTHVars.bypass_eot",
    DataType="Integer",
    Storage="UserVar",
    Datalog="Enabled",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalEndOfTestTestMethod-tdau_eot_bt_final
tdau_eot_bt_final = PrimeThermalEndOfTestTestMethod(
    name="TD_X_TDAU_E_FINAL_X_X_X_X_EOT_BT",
    BypassPort=Spec("PTH_DIODE_XXX.bypass_benchtop_inv"),
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PcsDatalogSelector=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("0,1,2,3","0,1,2,3,4","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2")'),
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    PreInstance="WriteSharedStorage(--token G.U.D.PCS_SOT_THERMAL_HEAD_TEMPERATURE_READ --value -6666666 )",
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PostInstance="DtsEndOfDevice()",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalEndOfTestTestMethod-tdau_eot_final
tdau_eot_final = PrimeThermalEndOfTestTestMethod(
    name="TD_X_TDAU_E_FINAL_X_X_X_X_EOT",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PcsDatalogSelector=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("0,1,2,3","0,1,2,3,4","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2")'),
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    PreInstance="WriteSharedStorage(--token G.U.D.PCS_SOT_THERMAL_HEAD_TEMPERATURE_READ --value -6666666 )",
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PostInstance="DtsEndOfDevice()",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2, 3, 4, 5], ret=1))
)

# Pymtpl marker - LTTCPREPRL0
## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_lttcdts_bt
tdau_lttc_bt = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_LTTCPREPRL0_X_X_X_X_LTTCDTS_BT",
    BypassPort=Spec("PTH_DIODE_XXX.bypass_benchtop_inv"),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    MeasurementType="TJ",
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","30, 30, 30")'),
    UserVarStoreNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas4, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_lttcdts
tdau_lttc = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_K_LTTCPREPRL0_X_X_X_X_LTTCDTS",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    ContinuousRead="Enabled",
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30,30,30","30,30,30,30"),__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","15,15,10,15"))'),
    MeasurementType="TJ",
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30,30,30","30,30,30,30"),__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("15,15,10,15","15,15,15,10,15","15,15,15,15","15,15,15,15","15,15,15,15","15,15,10,15","15,15,10,15","15,15,10,15"))'),
    UserVarStoreNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas4, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.LTTCTempMeas2")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - ScreenTC-screen_sot_set_global_lttc
screen_sot_set_global_lttc = ScreenTC(
    name="TD_X_SCREEN_E_LTTCPREPRL0_X_X_X_X_SOT_SET_GLOBAL_USVR",
    ScreenTestSet="NVL_SET_GLOBAL_USERVAR_LTTC",
    ScreenTestsFile="./InputFiles/NVL_SET_GLOBAL_USERVAR.txt",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2], ret=1))
)

# Pymtpl marker - TESTPLANENDFLOW
## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_stopcnv
applytc_stopcnv = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_TESTPLANENDFLOW_X_X_X_X_STOPCNV",
    BypassPort=Spec("__shared__::PTHVars.bypass_sot"),
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.Select_by_BOM_and_LocationSets("TDAU_EOT_TC_S28CH","TDAU_EOT_TC_S52CH","TDAU_EOT_TC_S28CC","TDAU_EOT_TC_S52CC","TDAU_EOT_TC_ROOM_S28CPP","TDAU_EOT_TC_ROOM_S52CPP","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_HX28CC","TDAU_EOT_TC_ROOM_HX28CPP","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_HX28CC","TDAU_EOT_TC_ROOM_HX28CPP","TDAU_EOT_TC_H16CH","TDAU_EOT_TC_H16CC","TDAU_EOT_TC_ROOM_H16CPP","TDAU_EOT_TC_S16CH","TDAU_EOT_TC_S16CC","TDAU_EOT_TC_ROOM_S16CPP","TDAU_EOT_TC_DNLS28CH","TDAU_EOT_TC_DNLS28CC","TDAU_EOT_TC_ROOM_DNLS28CPP","TDAU_EOT_TC_S28CH")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)


## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_measurement_tpef
tdau_measurement_tpef = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X",
    BypassPort=Spec("__shared__::PTHVars.bypass_eot"),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalEndOfTestTestMethod-tdau_eot_tpef
tdau_eot_tpef = PrimeThermalEndOfTestTestMethod(
    name="TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_EOT_TPEF",
    BypassPort=Spec("__shared__::PTHVars.bypass_eot"),
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PcsDatalogSelector=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("0,1,2,3","0,1,2,3,4","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2,3","0,1,2")'),
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    PreInstance="WriteSharedStorage(--token G.U.D.PCS_SOT_THERMAL_HEAD_TEMPERATURE_READ --value -6666666 )",
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PostInstance="DtsEndOfDevice()",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - AuxiliaryTC-aux_disable_eot_tpef
aux_disable_eot_tpef = AuxiliaryTC(
    name="TD_X_AUX_E_TESTPLANENDFLOW_X_X_X_X_DISABLE_EOT",
    Expression="1",
    ResultToken="__shared__::PTHVars.bypass_eot",
    DataType="Integer",
    Storage="UserVar",
    Datalog="Enabled",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeLogPcsTokensTestMethod-logpcstokens
logpcstokens = PrimeLogPcsTokensTestMethod(
    name="PTH_DIODE_MEASURE_E_TESTPLANENDFLOW_X_X_X_X_LOGPCSTOKENS",
    BypassPort=-1,
    _fitem=Fitem("SAME", edc=True,
                 r0=pFail(goto="NEXT"),
                 r1=pPass(goto="NEXT"))
)

## Pymtpl marker - PrimeThermalControlSetTestMethod-cs_desoak
cs_desoak = PrimeThermalControlSetTestMethod(
    name="TD_X_CS_E_TESTPLANENDFLOW_X_X_X_X_DESOAK",
    ControlSet="DESOAK",
    UeiPinName="IPC::UEISLAVE_IPC",
    BypassPort=-1,
    _fitem=Fitem("SAME", edc=True,
                 r0=pFail(goto="NEXT"),
                 r1=pPass(goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-cs_desoak_cpu
cs_desoak_cpu = PrimeApplyTestConditionTestMethod(
    name="TD_X_CS_E_TESTPLANENDFLOW_X_X_X_X_DESOAK_CPU",
    BypassPort=1,
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.PTHControlSetRule("SOAK_CC_TC","SOAK_TC","SOAK_RM_TC","SOAK_RM_TC")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-cs_desoak_pch
cs_desoak_pch = PrimeApplyTestConditionTestMethod(
    name="TD_X_CS_E_TESTPLANENDFLOW_X_X_X_X_DESOAK_PCH",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.PTHControlSetRule("IP_PCH::IP_PCH_BASE::SOAK_PCH_CC_TC","IP_PCH::IP_PCH_BASE::SOAK_PCH_TC","IP_PCH::IP_PCH_BASE::SOAK_PCH_RM_TC","IP_PCH::IP_PCH_BASE::SOAK_PCH_RM_TC")'),
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2], ret=1))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_psmstop_cpu
applytc_psmstop_cpu = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_TESTPLANENDFLOW_X_X_X_X_PSMSTOP_CPU",
    TestConditionCategory="THERMAL",
    TestConditionName="PowerSummingStop_TC_CPU",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_psmstop_pch
applytc_psmstop_pch = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_TESTPLANENDFLOW_X_X_X_X_PSMSTOP_PCH",
    TestConditionCategory="THERMAL",
    TestConditionName="PowerSummingStop_TC_PCH",
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2], ret=1))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_measurement_lttc
tdau_measurement_lttc = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_LTTC",
    BypassPort=Spec("__shared__::PTHVars.bypass_eot"),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalEndOfTestTestMethod-tdau_eot_tpef_lttc
tdau_eot_tpef_lttc = PrimeThermalEndOfTestTestMethod(
    name="TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_EOT_TPEF_LTTC",
    BypassPort=Spec("__shared__::PTHVars.bypass_eot"),
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    PcsDatalogSelector=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("4,5,6,7","4,5,6,7,8","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,6,7","4,5,7")'),
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    PreInstance="WriteSharedStorage(--token G.U.D.PCS_SOT_THERMAL_HEAD_TEMPERATURE_READ --value -6666666 )",
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto=aux_disable_eot_tpef.name),
                 **create_ports([0, 2, 3, 4, 5], goto=aux_disable_eot_tpef.name))
)

## Pymtpl marker - AuxiliaryTC-aux_lttc_fork_tpef
aux_lttc_fork_tpef = AuxiliaryTC(
    name="TD_X_AUX_E_TESTPLANENDFLOW_X_X_X_X_LTTC_FORK",
    DataType="String",
    Expression="[__shared__::PTHVars.bypass_lttc]",
    Storage="UserVar",
    ResultPort='[R]==\'-1\'?1:2',
    _fitem=Fitem("SAME", edc=True,
                 r0=pFail(goto=tdau_measurement_tpef.name),
                 r1=pPass(goto=tdau_measurement_lttc.name),
                 r2=pPass(goto=tdau_measurement_tpef.name))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_sot_tpef
tdau_sot_tpef = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_SOT",
    BypassPort=Spec("PTH_DIODE_XXX.bypass_sot"),
    DffTokens=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("SOTC0, SOTC1, SOTC2, SOTC3","SOTC0, SOTC1, SOTC2, SOTC3, SOTC4","SOTC0, SOTC1, SOTC2, SOTC3","SOTC0, SOTC1, SOTC2, SOTC3","SOTC0, SOTC1, SOTC2, SOTC3","SOTC0, SOTC1, SOTC2, SOTC3","SOTC0, SOTC1, SOTC2, SOTC3","SOTC0, SOTC1, SOTC2")'),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    MeasurementType="SOT",
    PinNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("15,15,10,15","15,15,15,10,15","30,30,30,30","30,30,30,30","30,30,30,30","15,15,10,15","15,15,10,15","30, 30, 30")'),
    UserVarStoreNames=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas4, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas3","PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas0, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas1, PTH_DIODE_XXX::PTH_DIODE_XXX.sotTempMeas2")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2, 3, 4, 5], ret=1))
)

# Pymtpl marker - TESTPLANSTARTFLOW
## Pymtpl marker - ULTLoggerTC-ultlogger
ultlogger = ULTLoggerTC(
    name="SOT_X_ULTLOGGER_K_TESTPLANSTARTFLOW_X_X_X_X_DFFIDEALITY",
    DieId=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("U1.U2,U1.U4","U1.U2,U1.U4,U1.U5,U1.U6","U1.U2,U1.U4,U1.U5","U1.U2,U1.U4,U1.U5","U1.U2,U1.U4,U1.U5","U1.U2,U1.U4","U1.U2,U1.U4","U1.U2,U1.U4,U1.U5")'),
    ValueExpression=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("MDPOSITION=U1.U2,MDPOSITION=U1.U4","MDPOSITION=U1.U2,MDPOSITION=U1.U4,MDPOSITION=U1.U5,MDPOSITION=U1.U6","MDPOSITION=U1.U2,MDPOSITION=U1.U4,MDPOSITION=U1.U5","MDPOSITION=U1.U2,MDPOSITION=U1.U4,MDPOSITION=U1.U5","MDPOSITION=U1.U2,MDPOSITION=U1.U4,MDPOSITION=U1.U5","MDPOSITION=U1.U2,MDPOSITION=U1.U4","MDPOSITION=U1.U2,MDPOSITION=U1.U4","MDPOSITION=U1.U2,MDPOSITION=U1.U4,MDPOSITION=U1.U5")'),
    IsInlineDff="ENABLED",
    LogLevel="Disabled",
    SetUltDataPerDieId="ENABLED",
    PrintUlt="ENABLED",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 r3=pPass(goto="NEXT"),
                 r4=pPass(goto="NEXT"),
                 r5=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeDffReadTestMethod-dffread
dffread = PrimeDffReadTestMethod(
    name="SOT_X_DFFREAD_K_TESTPLANSTARTFLOW_X_X_X_X_DFFREAD",
    LogLevel="Disabled",
    EnabledModules="NOKILL",
    LogIndividualTokens="DISABLED",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 r3=pPass(goto="NEXT"),
                 r4=pPass(goto="NEXT"),
                 r5=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PTHGetSetGsdsDffTC-dff_hub
dff_hub = PTHGetSetGsdsDffTC(
    name="SOT_X_DFF_K_TESTPLANSTARTFLOW_X_X_X_X_IDEALITYHUB",
    ConfigurationFile="./InputFiles/DFF_HUB.json",
    OPType="DFF2GSDS",
    PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_HUB+")',
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 r3=pPass(goto="NEXT"),
                 r4=pPass(goto="NEXT"),
                 r5=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PTHGetSetGsdsDffTC-dff_gcd
dff_gcd = PTHGetSetGsdsDffTC(
    name="SOT_X_DFF_K_TESTPLANSTARTFLOW_X_X_X_X_IDEALITYGCD",
    ConfigurationFile="./InputFiles/DFF_GCD.json",
    OPType="DFF2GSDS",
    PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_GPU+")',
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 r3=pPass(goto="NEXT"),
                 r4=pPass(goto="NEXT"),
                 r5=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PTHGetSetGsdsDffTC-dff_cpu
dff_cpu = PTHGetSetGsdsDffTC(
    name="SOT_X_DFF_K_TESTPLANSTARTFLOW_X_X_X_X_IDEALITYCPU",
    ConfigurationFile="./InputFiles/DFF_CPU.json",
    OPType="DFF2GSDS",
    PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")',
    BypassPort=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise(1,__shared__::SCVars.SC_BENCHTOP,1,__shared__::SCVars.SC_BENCHTOP,__shared__::SCVars.SC_BENCHTOP,1,1,__shared__::SCVars.SC_BENCHTOP)'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 r3=pPass(goto="NEXT"),
                 r4=pPass(goto="NEXT"),
                 r5=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PTHGetSetGsdsDffTC-dff_cpu1
dff_cpu1 = PTHGetSetGsdsDffTC(
    name="SOT_X_DFF_K_TESTPLANSTARTFLOW_X_X_X_X_IDEALITYCPU1",
    ConfigurationFile="./InputFiles/DFF_CPU1.json",
    OPType="DFF2GSDS",
    PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU1+")',
    BypassPort=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise(1,__shared__::SCVars.SC_BENCHTOP,1,1,1,1,1,1)'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 r3=pPass(goto="NEXT"),
                 r4=pPass(goto="NEXT"),
                 r5=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - ScreenTC-screen_ideality
screen_ideality = ScreenTC(
    name="SOT_X_SCREEN_E_TESTPLANSTARTFLOW_X_X_X_X_IDEALITY",
    ScreenTestSet=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IDEALITY_N2P","IDEALITY_S52C","IDEALITY_N2P","IDEALITY_N2P","IDEALITY_N2P","IDEALITY_N2P","IDEALITY_N2P","IDEALITY_18A")'),
    ScreenTestsFile="./InputFiles/NVL_PER_PART_IDEALITY.txt",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimePauseTestMethod-pause
pause = PrimePauseTestMethod(
    name="TD_X_PAUSE_E_TESTPLANSTARTFLOW_X_X_X_X_PUC",
    BypassPort=1,
    SleepTime=1000,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 r3=pPass(goto="NEXT"),
                 r4=pPass(goto="NEXT"),
                 r5=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_tdsetup_tpsf
applytc_tdsetup_tpsf = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_TESTPLANSTARTFLOW_X_X_X_X_TDSETUP",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.Select_by_BOM_and_LocationSets("TDAU_CAL_TC_S28CH","TDAU_CAL_TC_S52CH","TDAU_CAL_TC_S28CC","TDAU_CAL_TC_S52CC","TDAU_CAL_TC_ROOM_S28CPP","TDAU_CAL_TC_ROOM_S52CPP","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_HX28CC","TDAU_CAL_TC_ROOM_HX28CPP","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_HX28CC","TDAU_CAL_TC_ROOM_HX28CPP","TDAU_CAL_TC_H16CH","TDAU_CAL_TC_H16CC","TDAU_CAL_TC_ROOM_H16CPP","TDAU_CAL_TC_S16CH","TDAU_CAL_TC_S16CC","TDAU_CAL_TC_ROOM_S16CPP","TDAU_CAL_TC_DNLS28CH","TDAU_CAL_TC_DNLS28CC","TDAU_CAL_TC_ROOM_DNLS28CPP","TDAU_CAL_TC_S28CH")'),
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_scocal
applytc_scocal = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_TESTPLANSTARTFLOW_X_X_X_X_SCOCAL",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_DIODE_XXX_Rules.Select_by_BOM_and_LocationSets("TDAU_SCOC_TC_S28CH","TDAU_SCOC_TC_S52CH","TDAU_SCOC_TC_S28CC","TDAU_SCOC_TC_S52CC","TDAU_SCOC_TC_ROOM_S28CPP","TDAU_SCOC_TC_ROOM_S52CPP","TDAU_SCOC_TC_HX28CH","TDAU_SCOC_TC_HX28CC","TDAU_SCOC_TC_ROOM_HX28CPP","TDAU_SCOC_TC_HX28CH","TDAU_SCOC_TC_HX28CC","TDAU_SCOC_TC_ROOM_HX28CPP","TDAU_SCOC_TC_H16CH","TDAU_SCOC_TC_H16CC","TDAU_SCOC_TC_ROOM_H16CPP","TDAU_SCOC_TC_S16CH","TDAU_SCOC_TC_S16CC","TDAU_SCOC_TC_ROOM_S16CPP","TDAU_SCOC_TC_DNLS28CH","TDAU_SCOC_TC_DNLS28CC","TDAU_SCOC_TC_ROOM_DNLS28CPP","TDAU_SCOC_TC_S28CH")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - AuxiliaryTC-aux_disable_eot_tpsf
aux_disable_eot_tpsf = AuxiliaryTC(
    name="TD_X_AUX_E_TESTPLANSTARTFLOW_X_X_X_X_DISABLE_EOT",
    Expression="1",
    ResultToken="__shared__::PTHVars.bypass_eot",
    DataType="Integer",
    Storage="UserVar",
    Datalog="Enabled",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - AuxiliaryTC-aux_disable_fact
aux_disable_fact = AuxiliaryTC(
    name="TD_X_AUX_E_TESTPLANSTARTFLOW_X_X_X_X_DISABLE_FACT",
    Expression="1",
    ResultToken="__shared__::PTHVars.bypass_lttc",
    DataType="Integer",
    Storage="UserVar",
    Datalog="Enabled",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - AuxiliaryTC-aux_enable_sot_tpsf
aux_enable_sot_tpsf = AuxiliaryTC(
    name="TD_X_AUX_E_TESTPLANSTARTFLOW_X_X_X_X_ENABLE_SOT",
    Expression="-1",
    ResultToken="__shared__::PTHVars.bypass_sot",
    DataType="Integer",
    Storage="UserVar",
    Datalog="Enabled",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 r2=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - ScreenTC-screen_btcheck_tpsf
screen_btcheck_tpsf = ScreenTC(
    name="TD_X_SCREEN_E_TESTPLANSTARTFLOW_X_X_X_X_BTCHECK_1",
    ScreenTestSet="MTL_CLASS_BT_CHECK",
    ScreenTestsFile="./InputFiles/MTL_CLASS_BT_CHECK.txt",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2], ret=1))
)

# Pymtpl marker - LOTSTARTFLOW
## Pymtpl marker - PrimeThermalUeiStreamTestMethod-ueistream_start
ueistream_start = PrimeThermalUeiStreamTestMethod(
    name="TD_X_UEISTREAM_E_LOTSTARTFLOW_X_X_X_X_START",
    ActionType="Start",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    CollectPins=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0,IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UeiSlaveType="TCC",
    PowerPins="IPC::TDYN_9_IPC",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2], ret=1))
)

# Pymtpl marker - LOTENDFLOW
## Pymtpl marker - PrimeThermalUeiStreamTestMethod-ueistream_stop
ueistream_stop = PrimeThermalUeiStreamTestMethod(
    name="TD_X_UEISTREAM_E_LOTENDFLOW_X_X_X_X_STOP",
    ActionType="Stop",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    CollectPins=Spec('PTH_DIODE_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0,IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UeiSlaveType="TCC",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(ret=1),
                 **create_ports([0, 2], ret=1))
)

# =============================================================================
# FLOW DEFINITIONS
# =============================================================================

# Pymtpl marker - Flows
## Pymtpl marker - PTH_DIODE_XXX_LTTCPREPRL0
PTH_DIODE_XXX_LTTCPREPRL0 = Flow("PTH_DIODE_XXX_LTTCPREPRL0", [
    tdau_lttc_bt,
    tdau_lttc,
    screen_sot_set_global_lttc
])

## Pymtpl marker - PTH_DIODE_XXX_BEGIN
PTH_DIODE_XXX_BEGIN = Flow("PTH_DIODE_XXX_BEGIN", [
    cs_test,
    cs_test_cpu,
    cs_test_pch
])

## Pymtpl marker - PTH_DIODE_XXX_FINAL
PTH_DIODE_XXX_FINAL = Flow("PTH_DIODE_XXX_FINAL", [
    aux_lttc_fork_final,
    tdau_measurement_final,
    aux_disable_eot_final,
    tdau_eot_bt_final,
    tdau_eot_final
])

## Pymtpl marker - PTH_DIODE_XXX_INIT
PTH_DIODE_XXX_INIT = Flow("PTH_DIODE_XXX_INIT", [
    cs_tcisetup,
    applytc_tdsetup_init,
    screen_btcheck_init,
    intec_init,
    dtsbase
])

## Pymtpl marker - PTH_DIODE_XXX_LOTENDFLOW
PTH_DIODE_XXX_LOTENDFLOW = Flow("PTH_DIODE_XXX_LOTENDFLOW", [
    ueistream_stop
])

## Pymtpl marker - PTH_DIODE_XXX_LOTSTARTFLOW
PTH_DIODE_XXX_LOTSTARTFLOW = Flow("PTH_DIODE_XXX_LOTSTARTFLOW", [
    ueistream_start
])

## Pymtpl marker - PTH_DIODE_XXX_START
PTH_DIODE_XXX_START = Flow("PTH_DIODE_XXX_START", [
    aux_disable_sot_start,
    aux_enable_eot_start,
    tdau_sot_bt_start,
    tdau_sot_start,
    screen_sot_set_global_start,
    intec_start
])

## Pymtpl marker - PTH_DIODE_XXX_TESTPLANENDFLOW
PTH_DIODE_XXX_TESTPLANENDFLOW = Flow("PTH_DIODE_XXX_TESTPLANENDFLOW", [
    applytc_stopcnv,
    aux_lttc_fork_tpef,
    tdau_measurement_lttc,
    tdau_eot_tpef_lttc,
    tdau_measurement_tpef,
    tdau_eot_tpef,
    aux_disable_eot_tpef,
    logpcstokens,
    cs_desoak,
    applytc_psmstop_cpu,
    applytc_psmstop_pch,
    cs_desoak_cpu,
    cs_desoak_pch,
    tdau_sot_tpef
])

## Pymtpl marker - PTH_DIODE_XXX_TESTPLANSTARTFLOW
PTH_DIODE_XXX_TESTPLANSTARTFLOW = Flow("PTH_DIODE_XXX_TESTPLANSTARTFLOW", [
    ultlogger,
    dffread,
    dff_hub,
    dff_gcd,
    dff_cpu,
    dff_cpu1,
    screen_ideality,
    pause,
    applytc_tdsetup_tpsf,
    applytc_scocal,
    aux_disable_eot_tpsf,
    aux_disable_fact,
    aux_enable_sot_tpsf,
    screen_btcheck_tpsf
])