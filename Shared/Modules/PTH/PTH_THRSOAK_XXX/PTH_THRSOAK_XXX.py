from pymtpl.por_methods import (PrimeApplyTestConditionTestMethod, 
                                 PrimeThermalControlSetTestMethod,
                                 PrimeTdauParametricDataLoggerTestMethod,
                                 PrimeThermalRampTestMethod,
                                 PrimeThermalSingleMeasurementTestMethod,
                                 PrimeThermalUeiStreamTestMethod,
                                 UserCodeTC, ScreenTC)
from pymtpl.core import (Flow, Fitem, pPass, pFail, InitializeNVLClass, 
                         Import, Spec, AUTO, BaseMethod, optional, required)

# =============================================================================
# CUSTOM TEST CLASS DEFINITION
# =============================================================================
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
MOD_NAME = "PTH_THRSOAK_XXX"
OUT_DIR = f"./{MOD_NAME}"

# =============================================================================
# INITIALIZATION
# =============================================================================
InitializeNVLClass(OUT_DIR, MOD_NAME, tosversion='tos4', binrange=(9771, 9771),defaultrm2bin=(99971000,99971999), defaultrm1bin=(98971000,98971999))
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

# Pymtpl marker - START
## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_psmsetup_cpu
applytc_psmsetup_cpu = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_START_X_X_X_X_PSMSETUP_CPU",
    TestConditionCategory="THERMAL",
    TestConditionName="PowerSumming_TC_CPU",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_psmsetup_pch
applytc_psmsetup_pch = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_START_X_X_X_X_PSMSETUP_PCH",
    TestConditionCategory="THERMAL",
    TestConditionName="PowerSumming_TC_PCH",
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeTdauParametricDataLoggerTestMethod-pardata_logger
pardata_logger = PrimeTdauParametricDataLoggerTestMethod(
    name="TD_X_PARDATA_E_START_X_X_X_X",
    PinNames="IPC::CPU_TDAU0,IPH::HUB_TDAU0,IPG::GCD_TDAU0,IPP::PCD_TDAU0",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - UserCodeTC-usercode_idealitycalc
usercode_idealitycalc = UserCodeTC(
    name="TD_X_PARDATA_E_START_X_X_X_X_IDEALITYCALC",
    InputFile="./InputFiles/TDAU_ideality.cs",
    Method="TDAUIdealityCalc",
    NamespaceClass="TDAU.TDAUIdeality",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - ScreenTC-screen_idealitycalc
screen_idealitycalc = ScreenTC(
    name="TD_X_SCREEN_E_START_X_X_X_X_IDEALITYCALC",
    ScreenTestSet=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("NVL_CLASS_IDEALITY_PRINT_N2P","NVL_CLASS_IDEALITY_S52C_PRINT","NVL_CLASS_IDEALITY_PRINT_N2P","NVL_CLASS_IDEALITY_PRINT_N2P","NVL_CLASS_IDEALITY_PRINT_N2P","NVL_CLASS_IDEALITY_PRINT_N2P","NVL_CLASS_IDEALITY_PRINT_N2P","NVL_CLASS_IDEALITY_PRINT_18A")'),
    ScreenTestsFile="./InputFiles/NVL_CLASS_IDEALITY_PRINT.txt",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_stop
applytc_stop = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_START_X_X_X_X_STOP",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_THRSOAK_XXX_Rules.Select_by_BOM_and_LocationSets("TDAU_EOT_TC_S28CH","TDAU_EOT_TC_S52CH","TDAU_EOT_TC_S28CC","TDAU_EOT_TC_S52CC","TDAU_EOT_TC_S28CH","TDAU_EOT_TC_S52CH","TDAU_EOT_TC_S28CH","TDAU_EOT_TC_S52CH","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_HX28CC","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_HX28CC","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_HX28CH","TDAU_EOT_TC_H16CH","TDAU_EOT_TC_H16CC","TDAU_EOT_TC_H16CH","TDAU_EOT_TC_H16CH","TDAU_EOT_TC_S16CH","TDAU_EOT_TC_S16CC","TDAU_EOT_TC_S16CH","TDAU_EOT_TC_S16CH","TDAU_EOT_TC_DNLS28CH","TDAU_EOT_TC_DNLS28CC","TDAU_EOT_TC_DNLS28CH","TDAU_EOT_TC_DNLS28CH","TDAU_EOT_TC_S28CH")'),
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_cal
applytc_cal = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_START_X_X_X_X_CAL",
    TestConditionCategory="LEVELS_POWER_DOWN",
    TestConditionName=Spec('PTH_THRSOAK_XXX_Rules.Select_by_BOM_and_LocationSets("TDAU_CAL_TC_S28CH_PER","TDAU_CAL_TC_S52CH_PER","TDAU_CAL_TC_S28CC","TDAU_CAL_TC_S52CC","TDAU_CAL_TC_S28CH","TDAU_CAL_TC_S52CH","TDAU_CAL_TC_S28CH","TDAU_CAL_TC_S52CH","TDAU_CAL_TC_HX28CH_PER","TDAU_CAL_TC_HX28CC","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_HX28CH_PER","TDAU_CAL_TC_HX28CC","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_HX28CH","TDAU_CAL_TC_H16CH_PER","TDAU_CAL_TC_H16CC","TDAU_CAL_TC_H16CH","TDAU_CAL_TC_H16CH","TDAU_CAL_TC_S16CH_PER","TDAU_CAL_TC_S16CC","TDAU_CAL_TC_S16CH","TDAU_CAL_TC_S16CH","TDAU_CAL_TC_DNLS28CH_PER","TDAU_CAL_TC_DNLS28CC","TDAU_CAL_TC_DNLS28CH","TDAU_CAL_TC_DNLS28CH","TDAU_CAL_TC_S28CH")'),
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-applytc_scoc
applytc_scoc = PrimeApplyTestConditionTestMethod(
    name="TD_X_APPLYTC_E_START_X_X_X_X_SCOC",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_THRSOAK_XXX_Rules.Select_by_BOM_and_LocationSets("TDAU_SCOC_TC_S28CH_PER","TDAU_SCOC_TC_S52CH_PER","TDAU_SCOC_TC_S28CC","TDAU_SCOC_TC_S52CC","TDAU_SCOC_TC_S28CH","TDAU_SCOC_TC_S52CH","TDAU_SCOC_TC_S28CH","TDAU_SCOC_TC_S52CH","TDAU_SCOC_TC_HX28CH_PER","TDAU_SCOC_TC_HX28CC","TDAU_SCOC_TC_HX28CH","TDAU_SCOC_TC_HX28CH","TDAU_SCOC_TC_HX28CH_PER","TDAU_SCOC_TC_HX28CC","TDAU_SCOC_TC_HX28CH","TDAU_SCOC_TC_HX28CH","TDAU_SCOC_TC_H16CH_PER","TDAU_SCOC_TC_H16CC","TDAU_SCOC_TC_H16CH","TDAU_SCOC_TC_H16CH","TDAU_SCOC_TC_S16CH_PER","TDAU_SCOC_TC_S16CC","TDAU_SCOC_TC_S16CH","TDAU_SCOC_TC_S16CH","TDAU_SCOC_TC_DNLS28CH_PER","TDAU_SCOC_TC_DNLS28CC","TDAU_SCOC_TC_DNLS28CH","TDAU_SCOC_TC_DNLS28CH","TDAU_SCOC_TC_S28CH")'),
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_dieforce
tdau_dieforce = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_K_START_X_X_X_X_DIEFORCE",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("30,30,30,30","30,30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30, 30, 30")'),
    MeasurementType="CHECK_DIE_FORCE",
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("30,30,30,30","30,30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30, 30, 30")'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], setbin=AUTO, ret=0))
)

## Pymtpl marker - PrimeThermalUeiStreamTestMethod-ueistream_startstream
ueistream_startstream = PrimeThermalUeiStreamTestMethod(
    name="TD_X_UEISTREAM_E_START_X_X_X_X_STARTSTREAM",
    ActionType="Start",
    CollectPins=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UeiSlaveType="TCC",
    BypassPort=1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2], goto="NEXT"))
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-cs_diodesot_cpu
cs_diodesot_cpu = PrimeApplyTestConditionTestMethod(
    name="TD_X_CS_E_START_X_X_X_X_DIODESOT_CPU",
    BypassPort=1,
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_THRSOAK_XXX_Rules.PTHControlSetRule("DIODESOT_CC_TC","DIODESOT_TC","DIODESOT_RM_TC","DIODESOT_RM_TC")')
)

## Pymtpl marker - PrimeApplyTestConditionTestMethod-cs_diodesot_pch
cs_diodesot_pch = PrimeApplyTestConditionTestMethod(
    name="TD_X_CS_E_START_X_X_X_X_DIODESOT_PCH",
    TestConditionCategory="THERMAL",
    TestConditionName=Spec('PTH_THRSOAK_XXX_Rules.PTHControlSetRule("IP_PCH::IP_PCH_BASE::DIODESOT_PCH_CC_TC","IP_PCH::IP_PCH_BASE::DIODESOT_PCH_TC","IP_PCH::IP_PCH_BASE::DIODESOT_PCH_RM_TC","IP_PCH::IP_PCH_BASE::DIODESOT_PCH_RM_TC")'),
    BypassPort=1
)

## Pymtpl marker - PrimeThermalControlSetTestMethod-cs_diodesot
cs_diodesot = PrimeThermalControlSetTestMethod(
    name="TD_X_CS_E_START_X_X_X_X_DIODESOT",
    ControlSet="DIODESOT",
    UeiPinName="IPC::UEISLAVE_IPC",
    PostInstance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("","","","","","","","")'),
    BypassPort=-1,
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalRampTestMethod-soak_thrsoak
soak_thrsoak = PrimeThermalRampTestMethod(
    name="TD_X_SOAK_K_START_X_X_X_X_THRSOAK",
    BypassPort=Spec("__shared__::SCVars.SC_BENCHTOP"),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LogPinToken=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("1,2,3,4","1,2,3,4,5","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3,4","1,2,3")'),
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("30,30,30,30","30,30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30"),__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("10,10,3,10","10,10,10,3,10","10,10,3,10","20,10,3,10","20,10,3,10","10,10,3,10","10,10,3,10","10,10,10"))'),
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    RampMode="Soak",
    SetPoints=Spec("__shared__::SCVars.SC_TEMPERATURE"),
    Timeout=60000,
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("30,30,30,30","30,30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30,30","30,30,30"),__shared__::TpRule.If_S28_S52_HX28_P16C_H16C_S16C_DS28C("10,10,3,10","10,10,10,3,10","10,10,3,10","20,10,3,10","20,10,3,10","10,10,3,10","10,10,3,10","10,10,10"))'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(ret=1),
                 **create_ports([0, 2, 3, 4, 5], setbin=AUTO, ret=0))
)

# Pymtpl marker - SPEEDPREPRL1
## Pymtpl marker - PrimeThermalControlSetTestMethod-cs_rampdwn
cs_rampdwn = PrimeThermalControlSetTestMethod(
    name="TD_X_CS_E_SPEEDPREPRL1_X_X_X_X_RAMPDWN",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(-1,1)'),
    ControlSet=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("TEST80","TEST80","TEST80","TEST70","TEST70","TEST80","TEST80","TEST80")'),
    UeiPinName="IPC::UEISLAVE_IPC",
    PostInstance="Sleep(5000)",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalRampTestMethod-soak_rampdwn
soak_rampdwn = PrimeThermalRampTestMethod(
    name="TD_X_SOAK_K_SPEEDPREPRL1_X_X_X_X_RAMPDWN",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(__shared__::SCVars.SC_BENCHTOP,1)'),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LogPinToken=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("1,3","1,2,4","1,3","1,3","1,3","1,3","1,3","1,3")'),
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30","30,30"),__shared__::TpRule.If_CLASS_NVL_S52C("10,10,10", __shared__::TpRule.If_CLASS_NVL_HX28C("20,20","10,10")))'),
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0,IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0")'),
    RampMode="Soak",
    SetPoints=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("80","80","80","70","70","80","80","80")'),
    Timeout=60000,
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30","30,30"),__shared__::TpRule.If_CLASS_NVL_S52C("10,10,10", __shared__::TpRule.If_CLASS_NVL_HX28C("20,20","10,10")))'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], setbin=AUTO, ret=0))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_sot_rampdwn
tdau_sot_rampdwn = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_SPEEDPREPRL1_X_X_X_X_SOT",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(__shared__::SCVars.SC_BENCHTOP,1)'),
    ContinuousRead="Enabled",
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("95,95,95,95","95,95,95,95,95","95,95,95,95","95, 95, 95","95,95,95,95","95,95,95,95","95,95,95,95","95, 95, 95")'),
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("5,5,5,5","5,5,5,5,5","5,5,5,5","5, 5, 5","5,5,5,5","5,5,5,5","5,5,5,5","5, 5, 5")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - IntecTC-intec_rampdwn
intec_rampdwn = IntecTC(
    name="TD_X_PARDATA_E_SPEEDPREPRL1_X_X_X_X_INTEC_2",
    IntecJson="../PTH_DIODE_XXX/InputFiles/intec.json",
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
    SetPoint=Spec('__shared__::SCVars.SC_TEMP_DROP'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(ret=1),
                 **create_ports([0], setbin=AUTO, ret=0))
)

# Pymtpl marker - SPEEDPREPRL2
## Pymtpl marker - PrimeThermalControlSetTestMethod-cs_rampup
cs_rampup = PrimeThermalControlSetTestMethod(
    name="TD_X_CS_E_SPEEDPREPRL2_X_X_X_X_RAMPUP",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(-1,1)'),
    ControlSet="TEST",
    UeiPinName="IPC::UEISLAVE_IPC",
    PostInstance="Sleep(5000)",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalRampTestMethod-soak_rampup
soak_rampup = PrimeThermalRampTestMethod(
    name="TD_X_SOAK_K_SPEEDPREPRL2_X_X_X_X_RAMPUP",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(__shared__::SCVars.SC_BENCHTOP,1)'),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LogPinToken=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("1,3","1,2,4","1,3","1,3","1,3","1,3","1,3","1,3")'),
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30","30,30"),__shared__::TpRule.If_CLASS_NVL_S52C("10,10,10", __shared__::TpRule.If_CLASS_NVL_HX28C("20,20","10,10")))'),
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0,IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0")'),
    RampMode="Soak",
    SetPoints=Spec("__shared__::SCVars.SC_TEMPERATURE"),
    Timeout=60000,
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30","30,30"),__shared__::TpRule.If_CLASS_NVL_S52C("10,10,10", __shared__::TpRule.If_CLASS_NVL_HX28C("20,20","10,10")))'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], setbin=AUTO, ret=0))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_sot_rampup
tdau_sot_rampup = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_SPEEDPREPRL2_X_X_X_X_SOT",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(__shared__::SCVars.SC_BENCHTOP,1)'),
    ContinuousRead="Enabled",
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("95,95,95,95","95,95,95,95,95","95,95,95,95","95, 95, 95","95,95,95,95","95,95,95,95","95,95,95,95","95, 95, 95")'),
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("5,5,5,5","5,5,5,5,5","5,5,5,5","5, 5, 5","5,5,5,5","5,5,5,5","5,5,5,5","5, 5, 5")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - IntecTC-intec_rampup
intec_rampup = IntecTC(
    name="TD_X_PARDATA_E_SPEEDPREPRL2_X_X_X_X_INTEC_3",
    IntecJson="../PTH_DIODE_XXX/InputFiles/intec.json",
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
    SetPoint="SC_TEMPERATURE", # This is the rampup point - So we use SC_TEMPERATURE which is set to the desired temperature in the soak test (soak_rampup)
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(ret=1),
                 **create_ports([0], setbin=AUTO, ret=0))
)

# Pymtpl marker - END
## Pymtpl marker - PrimeThermalControlSetTestMethod-cs_end
cs_end = PrimeThermalControlSetTestMethod(
    name="TD_X_CS_E_END_X_X_X_X_RAMPDWN",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(-1,1)'),
    ControlSet=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("TEST80","TEST80","TEST80","TEST70","TEST70","TEST80","TEST80","TEST80")'),
    UeiPinName="IPC::UEISLAVE_IPC",
    PostInstance="Sleep(5000)",
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0], goto="NEXT"))
)

## Pymtpl marker - PrimeThermalRampTestMethod-soak_end
soak_end = PrimeThermalRampTestMethod(
    name="TD_X_SOAK_K_END_X_X_X_X_RAMPDWN",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(__shared__::SCVars.SC_BENCHTOP,1)'),
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LogPinToken=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("1,3","1,2,4","1,3","1,3","1,3","1,3","1,3","1,3")'),
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30","30,30"),__shared__::TpRule.If_CLASS_NVL_S52C("10,10,10", __shared__::TpRule.If_CLASS_NVL_HX28C("20,20","10,10")))'),
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0,IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0","IPC::CPU_TDAU0, IPP::PCD_TDAU0")'),
    RampMode="Soak",
    SetPoints=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("80","80","80","70","70","80","80","80")'),
    Timeout=60000,
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.If_FUSE(__shared__::TpRule.If_CLASS_NVL_S52C("30,30,30","30,30"),__shared__::TpRule.If_CLASS_NVL_S52C("10,10,10", __shared__::TpRule.If_CLASS_NVL_HX28C("20,20","10,10")))'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], setbin=AUTO, ret=0))
)

## Pymtpl marker - PrimeThermalSingleMeasurementTestMethod-tdau_sot_end
tdau_sot_end = PrimeThermalSingleMeasurementTestMethod(
    name="TD_X_TDAU_E_END_X_X_X_X_SOT",
    BypassPort=Spec('PTH_THRSOAK_XXX_Rules.If_HOT(__shared__::SCVars.SC_BENCHTOP,1)'),
    ContinuousRead="Enabled",
    IntegrityHighLimit=200,
    IntegrityLowLimit=130,
    LowerTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("95,95,95,95","95,95,95,95,95","95,95,95,95","95, 95, 95","95,95,95,95","95,95,95,95","95,95,95,95","95, 95, 95")'),
    PinNames=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPC::CPU1_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPP::PCD_TDAU0, IPH::HUB_TDAU0","IPC::CPU_TDAU0, IPG::GCD_TDAU0, IPH::HUB_TDAU0")'),
    UpperTolerance=Spec('PTH_THRSOAK_XXX_Rules.Select_S28_S52_Otherwise("5,5,5,5","5,5,5,5,5","5,5,5,5","5, 5, 5","5,5,5,5","5,5,5,5","5,5,5,5","5, 5, 5")'),
    _fitem=Fitem("SAME", edc=True,
                 r1=pPass(goto="NEXT"),
                 **create_ports([0, 2, 3, 4, 5], goto="NEXT"))
)

## Pymtpl marker - IntecTC-intec_end
intec_end = IntecTC(
    name="TD_X_PARDATA_E_END_X_X_X_X_INTEC_4",
    IntecJson="../PTH_DIODE_XXX/InputFiles/intec.json",
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
    SetPoint=Spec('__shared__::SCVars.SC_TEMP_DROP'),
    _fitem=Fitem("SAME", edc=False,
                 r1=pPass(ret=1),
                 **create_ports([0], setbin=AUTO, ret=0))
)

# =============================================================================
# FLOW DEFINITIONS
# =============================================================================

# Pymtpl marker - Flows
## Pymtpl marker - PTH_THRSOAK_XXX_START
PTH_THRSOAK_XXX_START = Flow("PTH_THRSOAK_XXX_START", [
    applytc_psmsetup_cpu,
    applytc_psmsetup_pch,
    pardata_logger,
    usercode_idealitycalc,
    screen_idealitycalc,
    applytc_stop,
    applytc_cal,
    applytc_scoc,
    tdau_dieforce,
    ueistream_startstream,
    cs_diodesot,
    soak_thrsoak
])

## Pymtpl marker - PTH_THRSOAK_XXX_SPEEDPREPRL1
PTH_THRSOAK_XXX_SPEEDPREPRL1 = Flow("PTH_THRSOAK_XXX_SPEEDPREPRL1", [
    cs_rampdwn,
    soak_rampdwn,
    tdau_sot_rampdwn,
    intec_rampdwn
])

## Pymtpl marker - PTH_THRSOAK_XXX_SPEEDPREPRL2
PTH_THRSOAK_XXX_SPEEDPREPRL2 = Flow("PTH_THRSOAK_XXX_SPEEDPREPRL2", [
    cs_rampup,
    soak_rampup,
    tdau_sot_rampup,
    intec_rampup
])

## Pymtpl marker - PTH_THRSOAK_XXX_END
PTH_THRSOAK_XXX_END = Flow("PTH_THRSOAK_XXX_END", [
    cs_end,
    soak_end,
    tdau_sot_end,
    intec_end
])