# PKG TPI END Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import PrimeMixingDetectionTestMethod
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./TPI_MIXDETCT_XXX',  'TPI_MIXDETCT_XXX', tosversion="tos4", binrange=(4900, 4900),
                   defaultrm2bin = (99490000, 99491999),
                   defaultrm1bin = (98490000, 98491999))


# Init Flow
subflow = "STARTPREPRL1"

mixing_detect = PrimeMixingDetectionTestMethod(
    name = f"CTRL_X_MIXDET_K_{subflow}_X_X_X_X_DLCPMIXDET", 
    BypassPort =Spec( '__shared__::DieIndic.DieCombo(-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)'),
    ConfigurationFilePath = Spec('"./Shared/Modules/TPI/TPI_MIXDETCT_XXX/InputFiles/configurationFile_" +__shared__::FlowMatrix.BomGroupName+ "_Pass.mdet.json"'),
    _fitem = Fitem('SAME', r0=pFail(setbin=AUTO, ret = 0), r2=pFail(setbin=AUTO, ret = 0))
    )


STARTPREPRL1_Subflow = Flow(f'TPI_MIXDETCT_XXX_{subflow}', mixing_detect)