# PKG TPI END Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import DedcRVCallbackTC
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./TPI_DEDC_XXX',  'TPI_DEDC_XXX', tosversion="tos4", binrange=(9300, 9300),
                   defaultrm2bin = (99937500, 99937999), 
                   defaultrm1bin = (98937500, 98937999))

# Define import header
Import('TPI_DEDC_XXX.usrv')

# Define the counter
DEDCCTR = 93005480

# Init Flow
subflow = "INIT"

dedc = DedcRVCallbackTC(
    name = f"CTRL_X_DEDCRV_E_{subflow}_X_X_X_X_CALLBACK",
    Mode = Spec('TPI_DEDC_XXX_Rules.RegisterDEDC("REGISTER","REGISTER","REGISTER","REGISTER","REGISTER","REGISTER","REGISTER","REGISTER","REGISTER","UNREGISTER")'),
	ForceFlow = Spec('TPI_DEDC_XXX_Rules.RegisterFORCEFLOW("ENABLE","DISABLE")'),
	TestTimeSoftCap = Spec('TPI_DEDC_XXX_Rules.RegisterDEDC(3000000,3000000,3000000,3000000,3000000,3000000,3000000,3000000,3000000,3000000)'),
    UseLegacyBinning = "DISABLE",
    _fitem = Fitem('SAME', edc=True, r0=pFail(ctr=DEDCCTR, ret = 1))
    )


INIT_Subflow = Flow(f'TPI_DEDC_XXX_{subflow}', dedc)