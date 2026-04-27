from pymtpl.por_methods import PowerSequenceHandler, PrimeApplyTestConditionTestMethod
from pymtpl.core import Flow,  Fitem,  pFail,  InitializeNVLClass,  Spec, AUTO

module_name = 'TPI_PWRCTRL_XXX'

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass(module_name,  module_name,tosversion="tos4", binrange = (9315, 9316),
                   defaultrm2bin=(99933000, 99933999),
                   defaultrm1bin=(98933000, 98933999))

subflw_list_min = ['STARTSHAREDRAILSMIN1','HVBISHAREDRAILSMIN','BEGINSHAREDRAILSMIN','SPEEDSHAREDRAILSMIN','ENDSHAREDRAILSMIN','LTTCSHAREDRAILSMIN1','STARTPREPRL2']
subflw_list_max = ['BEGINSHAREDRAILSMAX','ENDSHAREDRAILSMAX','LTTCSHAREDRAILSMAX']
subflw_list_nom = ['STARTSHAREDRAILSNOM','BEGINSHAREDRAILSNOM','ENDSHAREDRAILSNOM','FACTSHAREDRAILSNOM']

# Define the counter
PWRCTRLCTR = 72500000

DC_Powersequencehandler = PowerSequenceHandler (
    name = f"CTRL_X_PWR_K_START_X_X_X_X_PWRCTRLTCDC",
    ApplyPowerDown = "Always",
	ApplyPowerOn = "Always",
	PowerDownTc = "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
	PowerOnTc = "BASE::Power_Up_TC_DC_PKG_force_0V_lvl",
     _fitem = Fitem('SAME', r0=pFail(setbin=9315, ret = 0))
)

DC_LTTC_Powersequencehandler = PowerSequenceHandler (
    name = f"CTRL_X_PWR_K_LTTCCOMMON_X_X_X_X_PWRCTRLTCDC",
    ApplyPowerDown = "Always",
	ApplyPowerOn = "Always",
	PowerDownTc = "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
	PowerOnTc = "BASE::Power_Up_TC_DC_PKG_force_0V_lvl",
     _fitem = Fitem('SAME', r0=pFail(setbin=9315, ret = 0))
)

SETRAIL_LTTC_Powersequencehandler = PrimeApplyTestConditionTestMethod (
    name = f"CTRL_X_PWR_K_LTTCCOMMON_X_X_X_X_SETRAIL",
    TestConditionCategory = "LEVELS_SETUP",
	TestConditionName = "srails_set_x_x_pkg_lvl_min",
    PostInstance = "Call(WriteUserVar(--uservar __shared__::SharedRailsIPFollower.v1p8 --value __shared__::PowerSpec.v1p8_min --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vnnaon --value __shared__::PowerSpec.vnnaon_min --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vccio --value __shared__::PowerSpec.vccio_min --type Double))",
      _fitem = Fitem('SAME', r0=pFail(setbin=9315, ret = 0))
)

SETPKGPWR_LTTC_Powersequencehandler = PowerSequenceHandler (
    name = f"CTRL_X_PWR_K_LTTCCOMMON_X_X_X_X_PWRCTRLTCPKG",
    ApplyPowerDown = "Always",
	ApplyPowerOn = "Always",
	PowerDownTc = "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
	PowerOnTc = "BASE::Power_Up_TC_PKG_min",
     _fitem = Fitem('SAME', r0=pFail(setbin=9315, ret = 0))
)

PKG_Powersequencehandler = PowerSequenceHandler (
    name = f"CTRL_X_PWR_K_START_X_X_X_X_PWRCTRLTCPKG",
    ApplyPowerDown = "Always",
	ApplyPowerOn = "Always",
	PowerDownTc = "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
	PowerOnTc = "BASE::Power_Up_TC_PKG_min",
     _fitem = Fitem('SAME', r0=pFail(setbin=9315, ret = 0))
)

srailmin_Powersetup_nombgtrim = PrimeApplyTestConditionTestMethod(
    name = f"CTRL_X_PWR_K_STARTSHAREDRAILSMIN_X_X_X_X_SETSRAIL",
    TestConditionCategory = "LEVELS_SETUP",
	TestConditionName = "srails_set_x_x_pkg_lvl_nombgtrim",
    PostInstance = "Call(WriteUserVar(--uservar __shared__::SharedRailsIPFollower.v1p8 --value __shared__::PowerSpec.v1p8_nom --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vnnaon --value __shared__::PowerSpec.vnnaon_nom --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vccio --value __shared__::PowerSpec.vccio_nom --type Double))",
    _fitem = Fitem('SAME',  r0=pFail(setbin=9315, ret = 0))
)   
for subflw in subflw_list_min:
    # Define next test instance in DUT flow
    srailmin_Powersetup_min = PrimeApplyTestConditionTestMethod(
        name = f'CTRL_X_PWR_K_{subflw}_X_X_X_X_SETSRAIL',
        TestConditionCategory = "LEVELS_SETUP",
	    TestConditionName = "srails_set_x_x_pkg_lvl_min",
        PostInstance = "Call(WriteUserVar(--uservar __shared__::SharedRailsIPFollower.v1p8 --value __shared__::PowerSpec.v1p8_min --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vnnaon --value __shared__::PowerSpec.vnnaon_min --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vccio --value __shared__::PowerSpec.vccio_min --type Double))",
        _fitem = Fitem('SAME',  r0=pFail(setbin=AUTO, ret = 0))
        )                            

     # Define above tests in subflows
    Flow(f'{module_name}_{subflw}', srailmin_Powersetup_min)

for subflw in subflw_list_max:
    # Define next test instance in DUT flow
    srailmin_Powersetup_max = PrimeApplyTestConditionTestMethod(
        name = f'CTRL_X_PWR_K_{subflw}_X_X_X_X_SETSRAIL',
        TestConditionCategory = "LEVELS_SETUP",
	    TestConditionName = "srails_set_x_x_pkg_lvl_max",
        PostInstance = "Call(WriteUserVar(--uservar __shared__::SharedRailsIPFollower.v1p8 --value __shared__::PowerSpec.v1p8_max --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vnnaon --value __shared__::PowerSpec.vnnaon_max --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vccio --value __shared__::PowerSpec.vccio_max --type Double))",
        _fitem = Fitem('SAME',  r0=pFail(setbin=AUTO, ret = 0))
        )                            

     # Define above tests in subflows
    Flow(f'{module_name}_{subflw}', srailmin_Powersetup_max)

for subflw in subflw_list_nom:
    # Define next test instance in DUT flow
    srailmin_Powersetup_nom = PrimeApplyTestConditionTestMethod(
        name = f'CTRL_X_PWR_K_{subflw}_X_X_X_X_SETSRAIL',
        TestConditionCategory = "LEVELS_SETUP",
	    TestConditionName = "srails_set_x_x_pkg_lvl_nom",
        PostInstance = "Call(WriteUserVar(--uservar __shared__::SharedRailsIPFollower.v1p8 --value __shared__::PowerSpec.v1p8_nom --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vnnaon --value __shared__::PowerSpec.vnnaon_nom --type Double) | WriteUserVar(--uservar __shared__::SharedRailsIPFollower.vccio --value __shared__::PowerSpec.vccio_nom --type Double))",
        _fitem = Fitem('SAME',  r0=pFail(setbin=AUTO, ret = 0))
        )                            

     # Define above tests in subflows
    Flow(f'{module_name}_{subflw}', srailmin_Powersetup_nom)

START = Flow(f'{module_name}_PWRCTRLPKG_START',PKG_Powersequencehandler)
START = Flow(f'{module_name}_PWRCTRLDC_START',DC_Powersequencehandler)
LTTCCOMMON = Flow(f'{module_name}_PWRCTRLDC_LTTCCOMMON',DC_LTTC_Powersequencehandler)
LTTCCOMMON = Flow(f'{module_name}_SETRAIL_LTTCCOMMON',SETRAIL_LTTC_Powersequencehandler)
LTTCCOMMON = Flow(f'{module_name}_SETPKGPWR_LTTCCOMMON',SETPKGPWR_LTTC_Powersequencehandler)
STARTSHAREDRAILSMIN = Flow(f'{module_name}_STARTSHAREDRAILSMIN',srailmin_Powersetup_nombgtrim)




