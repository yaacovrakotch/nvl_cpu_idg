from pymtpl.por_methods import AnalogDcTC
from pymtpl.core import Flow, Fitem, pPass, pFail, InitializeNVLClass, Import, Spec, AUTO

# =============================================================================
# CONFIGURATION
# =============================================================================
MODULE_NAME = "PTH_XIUCHK_CKX"
OUT_DIR = f"./{MODULE_NAME}"

# =============================================================================
# INITIALIZATION
# =============================================================================
InitializeNVLClass(
    OUT_DIR, 
    MODULE_NAME, 
    tosversion='tos4', 
    binrange=(2751, 2752),
    defaultrm2bin=(99271300, 99271400),
    defaultrm1bin=(98271300, 98271400)
)

# Import required files
Import(f"{MODULE_NAME}_LevelsSequences.lvl")
Import(f"{MODULE_NAME}_Levels.tcg")
Import(f"{MODULE_NAME}_PatternTrigger.ptm")

# =============================================================================
# BASE CONFIGURATION
# =============================================================================
BASE = {
    "TIMINGS": "BASE::pkg_cpu_fun_timing_mts100_tstprtclk50_tck100",
    "LVL_1P0V": f"{MODULE_NAME}::XIUCHK_VCCIA_1P0V_MIN",
    "PINS": "VCCIA,VCCIO,VCCIO_OUT_SVID",
    "MEAS_TYPES": "V,V,V",
    "MAP": f"{MODULE_NAME}::XIUCHK_VINOUT_VIEWPIN_TriggerMap",
    "DLOG": "PIN_DETAIL",
    "FLUSH": "ENABLED"
}

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
            port_kwargs['setbin'] = setbin if isinstance(setbin, str) else AUTO
        if ret is not None:
            port_kwargs['ret'] = ret
        
        if port_num < 0:
            key = f"r_{abs(port_num)}"
        else:
            key = f"r{port_num}"
        port_dict[key] = pFail(**port_kwargs)
    return port_dict

# =============================================================================
# TEST DEFINITIONS
# =============================================================================

# Pymtpl marker - BEGINCPUPKG
## Pymtpl marker - AnalogDcTC-XIUCHK_VCCIO_BEGINCPUPKG
xiuchk_vccio_begincpupkg = AnalogDcTC(
    name="XIUCHK_X_ANAMEAS_K_BEGINCPUPKG_X_X_X_X_VCCIO",
    BypassPort=Spec('__shared__::TpRule.If_POSTFUSED(1,-1)'),
    DataBaseFile="./InputFiles/ANAMEAS_NVL_CLASS_VCCIO.json",
    LevelsTc=BASE["LVL_1P0V"],
    Patlist="pth_dlvr_vccio_meas_pkg_list",
    Pins=BASE["PINS"],
    TimingsTc=BASE["TIMINGS"],
    MeasurementTypes=BASE["MEAS_TYPES"],
    TriggerMapName=BASE["MAP"],
    DatalogLevel=BASE["DLOG"],
    FlushLevels=BASE["FLUSH"],
    _fitem=Fitem("SAME", edc=True,
                 **create_ports([0,2, 3, 4, 5, 6, 7, 8], setbin=AUTO, ret=1))
)

# Pymtpl marker - CPUPKGFF
## Pymtpl marker - AnalogDcTC-XIUCHK_VCCIO_CPUPKGFF
xiuchk_vccio_cpupkgff = AnalogDcTC(
    name="XIUCHK_X_ANAMEAS_K_CPUPKGFF_X_X_X_X_VCCIO",
    BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_HX28C(1, __shared__::TpRule.If_POSTFUSED(1,-1))'),
    DataBaseFile="./InputFiles/ANAMEAS_NVL_CLASS_VCCIO.json",
    LevelsTc=BASE["LVL_1P0V"],
    Patlist="pth_dlvr_vccio_meas_pkg_list",
    Pins=BASE["PINS"],
    TimingsTc=BASE["TIMINGS"],
    MeasurementTypes=BASE["MEAS_TYPES"],
    TriggerMapName=BASE["MAP"],
    DatalogLevel=BASE["DLOG"],
    FlushLevels=BASE["FLUSH"],
    _fitem=Fitem("SAME", edc=True,
                 **create_ports([0,2, 3, 4, 5, 6, 7, 8], setbin=AUTO, ret=1))
)

# =============================================================================
# FLOW DEFINITIONS
# =============================================================================

# Pymtpl marker - Flows
## Pymtpl marker - PTH_XIUCHK_XXX_BEGINCPUPKG
PTH_XIUCHK_XXX_BEGINCPUPKG = Flow(
    f"{MODULE_NAME}_BEGINCPUPKG",
    [xiuchk_vccio_begincpupkg]
)

## Pymtpl marker - PTH_XIUCHK_XXX_CPUPKGFF
PTH_XIUCHK_XXX_CPUPKGFF = Flow(
    f"{MODULE_NAME}_CPUPKGFF",
    [xiuchk_vccio_cpupkgff]
)