# PKG TPI PUP Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import PrimeCallbacksRegistrarTestMethod, PrimePUPTestMethod, PlistConfigTC
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./TPI_PUP_XXX',  'TPI_PUP_XXX', tosversion="tos4", binrange=(9312, 9312),
				   defaultrm2bin = (99936500, 99936999),
				   defaultrm1bin = (98936500, 98936999))

# Define import header
Import("TPI_PUP_XXX.usrv")


# Define the subflow where the module place at.
subflw_init  = "INIT"


PUP_Setup = PrimeCallbacksRegistrarTestMethod(
    name = f"CTRL_X_CALLBACKS_K_{subflw_init}_X_X_X_X_PUP",
    LogLevel = "Disabled",	
   _fitem = Fitem('SAME', r0=pFail(ret = 0))
    )


SKIP_SHORT = PlistConfigTC(
    name = f"CTRL_X_PLISTCONFIG_E_{subflw_init}_X_X_X_X_SKIPSHORT",
    ConfigMode = "PATLIST",
    RecursiveMode = "True",
    OptionName = "Skip",
    OptionValue = Spec('__shared__::PUPHERMESRules.PUPSupportedOperation("False", "True", "True", "False")'),
    PatlistRegex = ".*",
    ElementRegex = "__0",
    BypassPort = 1,
    _fitem = Fitem('SAME', r0=pFail(ret=0))
    )


SKIP_LONG = PlistConfigTC(
    name = f"CTRL_X_PLISTCONFIG_E_{subflw_init}_X_X_X_X_SKIPLONG",
    ConfigMode = "PATLIST",
    RecursiveMode = "True",
    OptionName = "Skip",
    OptionValue = Spec('__shared__::PUPHERMESRules.PUPSupportedOperation("False", "True", "True", "False")'),
    PatlistRegex = ".*",
    ElementRegex = "__1",
    BypassPort = 1,
    _fitem = Fitem('SAME', r0=pFail(ret=0))
    )


# Define above tests in INIT 
INIT = Flow (f'TPI_PUP_XXX_{subflw_init}', PUP_Setup, SKIP_SHORT, SKIP_LONG)

### Special Flows ####
subflow = "TESTPLANENDFLOW"

PRINTITUFF = PrimePUPTestMethod (
	name = f"CTRL_X_PUP_K_{subflow}_X_X_X_X_PRINTITUFF",
	LogLevel = "Disabled",
	PupMatchMode = "VidAndEfuseBoth",
	MonitorLoopNum = 3,
	PatternsFilePath ="$PUP_PATTERNS_DIR\\\\@LATEST_REV@\\\\PAS_PTD.pup.json",
	PupDebugMode = "Disabled",
	Mode = "Disabled",
	_fitem = Fitem('SAME', r0=pFail(setbin=AUTO, ret = 0), r1=pPass(ret = 1))
	)


TESTPLANENDFLOW_Subflow = Flow(f'TPI_PUP_XXX_{subflow}', PRINTITUFF)