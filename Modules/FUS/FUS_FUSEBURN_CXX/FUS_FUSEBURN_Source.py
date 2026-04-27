# Import the necessary classes from Pymtpl
import copy
import re, json

from pymtpl.por_methods import AuxiliaryTC, ScreenTC, PrimePatConfigTestMethod, PrimeFuseBurnMaskTestMethod, PrimeFuseReadMaskTestMethod, SFMFuseReadMask, PrimeFunctionalTestMethod, FleCompareFuseString, FleCompareFuseStringByDies, FleGenerateLockoutBitsFuseString, FleGenerateLockoutBitsFuseStringByDies, PrimeCtvDecoderTestMethod, SFMDffEfuseCheck, PrimeFuseReadMaskUltDecodeTestMethod, FleComputeFuseHashSignature, FleComputeFuseHashSignatureByDies, FleISeedCapturePartId, FleISeedSetUnitKeys, FleGenerateFuseRepairString, FleGetDieStatus, FleGetDieStatusByDies, FleCheckFusedSspecFusing, FleGeneratePerDieFuseString, FleGeneratePerDieFuseStringAllDies, FleUpdateSpecialAlgInFuseString, FleGeneratePerDieFuseStringByDies, RunCallback
from pymtpl.por_methods import BaseMethod, required, optional
from pymtpl.core import Flow, Fitem, pPass, pFail, InitializeNVLSort, InitializeNVLClass, Spec, AUTO,MtplComment, Import, TrialParamSpec
from collections import OrderedDict

class KEYVALUEPAIR:
    def __init__(self, **kwargs):
        self.d = kwargs

    def update(self, params):
        self.d.update(params.d)

class PARAMS(KEYVALUEPAIR):
    def __init__(self, **kwargs):
        KEYVALUEPAIR.__init__(self, **kwargs)

class TestConfig:
    def __init__(self, is_edc=False):
        self.is_edc = is_edc
        self.is_edc_char = 'E' if is_edc else 'K'
    def get_fitem(self, **kwargs):
        if self.is_edc:
            return Fitem("SAME", self.test, edc=True, **kwargs)
        else:
            return Fitem("SAME", self.test, ** kwargs)

class AuxiliaryTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_AUX_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = AuxiliaryTC(**param)

class ScreenTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False, test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_SCREENTC_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ScreenTestsFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X.screen.json","./InputFiles/FUSEBURN_C1X.screen.json")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = ScreenTC(**param)

class PrimePatConfigTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)

        if name == 'apply_gen_hash':
            file = Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X.PatConfigSetpoints.json","./InputFiles/FUSEBURN_C1X.PatConfigSetpoints.json")')
        elif name == 'tostrigger_patmod':
            file = Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X.PatConfigSetpoints.json","./InputFiles/FUSEBURN_C1X.PatConfigSetpoints.json")')
        else:
            file =  Spec('__shared__::TpRule.If_MICP(GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C2X.patConfigSetpoints.json", GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C1X.patConfigSetpoints.json")')
            

        param = {
            'name': f'FUSE_X_PATCONFIG_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': file,
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimePatConfigTestMethod(**param)

class PrimeFuseBurnMaskTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)

        if 'cpu1' in name:
            vfile = f'./InputFiles/FUSEBURN_C2X.fuseBurnVoltageFile_CPU1.json'
            reg = f'CPU1'
            mpins = f'IPC::CPU_TDO'
            lvl = f'CPU_IP_BASE::cpu1_all_bf_x_x_ipc_lvl_nom'
        else:
            vfile =  Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X.fuseBurnVoltageFile_CPU0.json","./InputFiles/FUSEBURN_C1X.fuseBurnVoltageFile.json")')
            reg = f'CPU0'
            mpins = Spec('__shared__::TpRule.If_MICP("IPC::CPU1_TDO","")')
            lvl = Spec('__shared__::TpRule.If_MICP("CPU_IP_BASE::cpu0_all_bf_x_x_ipc_lvl_nom","CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom")')

        param = {
            'name': f'FUSE_X_FUSEBURN_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('FUS_FUSEBURN_CXX_Rules.FUSEBURN_CfgFile("./InputFiles/FUSEBURN_C2X.fuseMask.json","./InputFiles/FUSEBURN_C2X.fuseMask_BLLC.json","./InputFiles/FUSEBURN_C1X.fuseMask_BLLC.json","./InputFiles/FUSEBURN_C1X.fuseMask.json")'),
            'LogLevel': f'Disabled',
            #Parallel setup
            #'VoltageFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X.fuseBurnVoltageFile.json","./InputFiles/FUSEBURN_C1X.fuseBurnVoltageFile.json")'),
            #'RegisterNames': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'), 
            #Serial setup
            'VoltageFile': vfile,
            'RegisterNames': reg,
            'MaskPins': mpins,
            'LevelsTc': lvl,
            'SkipPatternExecute': f'DISABLED',
            'BypassPort': f'-1'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFuseBurnMaskTestMethod(**param)

class PrimeFuseReadMaskTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUSEREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('FUS_FUSEBURN_CXX_Rules.FUSEREAD_CfgFile("./InputFiles/FUSEBURN_C2X.fuseRead.json","./InputFiles/FUSEBURN_C2X.fuseRead_BLLC.json","./InputFiles/FUSEBURN_C1X.fuseRead_BLLC.json","./InputFiles/FUSEBURN_C1X.fuseRead.json")'),
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
            'SkipPatternExecute': f'DISABLED',
            'BypassPort': f'-1',
            'LevelsTc': f'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFuseReadMaskTestMethod(**param)

class SFMFuseReadMask_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUSEREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X.fuseRead.json","./InputFiles/FUSEBURN_C1X.fuseRead.json")'),
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
            'BypassPort': f'-1',
            'LevelsTc': f'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = SFMFuseReadMask(**param)

class PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_ULTREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X.fuseRead.json","./InputFiles/FUSEBURN_C1X.fuseRead.json")'),
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
            'SkipPatternExecute': f'DISABLED',
            'DieIdNames': Spec('__shared__::TpRule.If_MICP("U1.U5,U1.U6", "U1.U5")'),
            'BypassPort': f'-1',
            'PackageEfuse': Spec('__shared__::TpRule.If_MICP("ALLOW_NO_PKG","")'),
            'LevelsTc': f'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFuseReadMaskUltDecodeTestMethod(**param)

class PrimeFunctionalTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUNC_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'LevelsTc': f'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFunctionalTestMethod(**param)

class PrimeCtvDecoderTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_CTVDECODER_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP(GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C2X_PIC8_PrimeCtvDecoderTestMethod.csv",GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C1X_PIC8_PrimeCtvDecoderTestMethod.csv")'),
            'CtvCapturePins': Spec('__shared__::TpRule.If_MICP("IPC::CPU_TDO, IPC::CPU1_TDO","IPC::CPU_TDO")'),
            'Dieid_Rename': f' ',
            'LevelsTc': f'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeCtvDecoderTestMethod(**param)

class SFMDffEfuseCheck_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'DffFormat': f'Desegregation',
            'UserVarCollection': 'FUSEUFGL',
            'BypassPort': Spec(-1)
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = SFMDffEfuseCheck(**param)

class FleComputeFuseHashSignature_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'FuseReadTokenName': f'FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString',
            'OutputFuseStringLocation': f'Uservar'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleComputeFuseHashSignature(**param)

class FleComputeFuseHashSignatureByDies_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'FuseReadTokenName': f'FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString',
            'OutputFuseStringLocation': f'SharedStorage',
            'Registers': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'), 
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleComputeFuseHashSignatureByDies(**param)

class FleCompareFuseString_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'FuseReadTokenName': f'False',
            'OutputFuseStringLocation': f'Uservar',
            'BypassPort': f'-1'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleCompareFuseString(**param)

class FleCompareFuseStringByDies_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'OutputFuseStringLocation': f'SharedStorage',
            'Registers': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'), 
            'FuseReadTokenNames': Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), 
            'BypassPort': f'-1'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleCompareFuseStringByDies(**param)


class FleGenerateLockoutBitsFuseString_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': Spec(-1)
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGenerateLockoutBitsFuseString(**param)

class FleGenerateLockoutBitsFuseStringByDies_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': Spec(-1),
            'Registers': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGenerateLockoutBitsFuseStringByDies(**param)

class FleISeedSetUnitKeys_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_ISEED_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': Spec('-1'),
            'DieIds': Spec(' __shared__::TpRule.If_MICP("U1.U5,U1.U6","U1.U5")'),
            'KeysTypeId': Spec('__shared__::TpRule.If_MICP("1600,1599","1600")')
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleISeedSetUnitKeys(**param)

class FleISeedCapturePartId_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': Spec('1'),
            'Patlist': f'cpu_dfxagg_read_hvm_partid',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleISeedCapturePartId(**param)

class FleGenerateFuseRepairString_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'1',
            'FuseReadTokenName': f'FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr',
            'OutputFuseStringLocation': f'Uservar',
            'Process': f'7nm',
            #'SplitSpecialRows': f'YES',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGenerateFuseRepairString(**param)

class FleGetDieStatus_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': Spec(-1),
            'FuseStateUservar': f'Which_Socket.FuseState'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGetDieStatus(**param)

class FleGetDieStatusByDies_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': Spec(-1),
            'FuseStateUservar': f'Which_Socket.FuseState',
            'Registers': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
            }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGetDieStatusByDies(**param)

class FleCheckFusedSspecFusing_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': Spec(-1),
            'FuseReadTokenName': f'FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0',
            'Register': f'CPU0',
            'SspecFuseGroupName': f'dfx_agg/qdf_fuse', 
            'OutputFuseStringLocation': f'SharedStorage'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleCheckFusedSspecFusing(**param)

class FleGeneratePerDieFuseString_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'DataLog': f'On', 
            'Register': f'CPU0',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGeneratePerDieFuseString(**param)

class FleGeneratePerDieFuseStringAllDies_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'DataLog': f'On', 
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGeneratePerDieFuseStringAllDies(**param)

class FleGeneratePerDieFuseStringByDies_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'DataLog': f'On', 
            'Registers': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGeneratePerDieFuseStringByDies(**param)

class FleUpdateSpecialAlgInFuseString_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'AlgorithmName': f'CPU0_HIP_HASH', 
            'Register': f'CPU0',
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleUpdateSpecialAlgInFuseString(**param)

class RunCallback_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_RUNCALLBACK_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'Callback': f'WriteSharedStorage', 
            'BypassPort': f'-1',
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = RunCallback(**param)


class CDIE_BASE:
    def __init__(self, sort_class):
        self.sort_class = sort_class
        self.LevelsTc = None
        self.TimingsTc = None
        # Track every final bin generated in this session (as integers)
        self._seen_final_bins = set()

    def _validate_and_parse(self, bin_int: int):
        """
        Validate a 6-digit integer and parse into hard_bin, soft_bin, counter_base.
        """
        if not isinstance(bin_int, int):
            raise ValueError("BIN must be a 6-digit integer (e.g., 315502).")
        if bin_int < 0 or bin_int > 999999:
            raise ValueError("invalid bin")
        s = f"{bin_int:06d}"  # normalize to 6 digits
        if not s.startswith("31"):
            raise ValueError("invalid bin")
        hard_bin = s[0:2]         # '31'
        soft_bin = s[2:4]         # e.g., '55'
        counter_base = int(s[4:6])  # e.g., 2 for '02'
        return hard_bin, soft_bin, counter_base

    def bin(self, _bin: int, _offset: int = 0, enforce_unique: bool = True, max_tries: int = 1000):
        """
        Generate the final bin from a 6-digit integer BIN (HHSSCC) and ensure uniqueness.

        Rules:
        - Input must be a 6-digit integer starting with '31' (HH=31).
        - softbin (SS) is digits 3-4; counter (CC) is digits 5-6.
        - _offset applies ONLY to the counter: counter_total = CC + _offset (no wrap).
        - For sort_class != 'sort': final = HH SS (2000 + counter_total)  --> HHSSYYYY
        - For sort_class == 'sort': final = HH SS SS CC'                 --> HHSSSSCC'
          where CC' = counter_total % 100 to keep it two-digit.

        Uniqueness:
        - If enforce_unique=True and the computed final bin already exists in this session,
          the method increases counter_total by +1 until a unique final is found (bounded by max_tries).

        Returns:
        - final bin as int (matches your original behavior).
        """
        hard_bin, soft_bin, counter_base = self._validate_and_parse(_bin)

        # Apply offset only to the counter
        counter_total = counter_base + int(_offset)

        tries = 0
        while True:
            if tries > max_tries:
                raise RuntimeError("Unable to generate a unique final bin within max_tries.")

            if self.sort_class == "sort":
                # Output needs a 2-digit counter, so modulo 100
                counter_out = counter_total % 100
                counter_str = f"{counter_out:02d}"
                final_bin_str = f"{hard_bin}{soft_bin}{soft_bin}{counter_str}"  # HHSSSSCC'
            else:
                # Non-'sort' ? YYYY = 2000 + counter_total (no wrap)
                yyyy = 2000 + counter_total
                final_bin_str = f"{hard_bin}{soft_bin}{yyyy:04d}"               # HHSSYYYY

            final_bin_int = int(final_bin_str)

            # Enforce uniqueness
            if not enforce_unique or final_bin_int not in self._seen_final_bins:
                self._seen_final_bins.add(final_bin_int)
                return final_bin_int

            # Collision ? bump and try again
            counter_total += 1           
            tries += 1

    def reset_session(self):
        """Clear the seen-bin registry (optional helper)."""





    def get_init_flow(self, flow_name, module_name='INIT', is_edc=False,  bin_offset=0, bin_offset2=0, composite_postfix=None, test_instance_postfix=None):
        t = dict()

        offset=bin_offset
        offset2=bin_offset2
        dparams = {

            'module_name': module_name,
            'test_instance_postfix': test_instance_postfix,
            'is_edc': is_edc,
            'LevelsTc': self.LevelsTc,
            'TimingsTc': self.TimingsTc,
        }

        # tests for INIT
        t['perdiestateinitlot'] = ScreenTC_TestBuilder(name='perdiestateinitlot', ScreenTestSet='PerDieValuesInit_LOT', BypassPort=-1, **dparams)
        t['tostrigger_patmod'] = PrimePatConfigTestMethod_TestBuilder(name='tostrigger_patmod', SetPoint='TOSTrigger_Parallel', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), **dparams)
        
        ##Flow Setup
        init_fitems = []
        init_fitems.append(t['perdiestateinitlot'].get_fitem(r0=pFail(ret=0),
                                                             r2=pFail(ret=0),
                                                             r3=pFail(ret=0),
                                                             r4=pFail(ret=0),
                                                             r5=pFail(ret=0),
                                                             r6=pFail(ret=0),
                                                             r7=pFail(ret=0),
                                                             r8=pFail(ret=0),
                                                             r9=pFail(ret=0),
                                                             r10=pFail(ret=0)
                                                             ))
        init_fitems.append(t['tostrigger_patmod'].get_fitem(r0=pFail(ret=0),
                                                            r2=pFail(ret=0)))

        Flow(flow_name,*init_fitems)

    def get_fact_flow(self, flow_name, module_name='FACTFUSBURNCPUNOM', is_edc=False,  bin_offset=0, bin_offset2=300, composite_postfix=None, test_instance_postfix=None):
        t = dict()

        offset=bin_offset
        offset2=bin_offset2
        dparams = {

            'module_name': module_name,
            'test_instance_postfix': test_instance_postfix,
            'is_edc': is_edc,
            #'LevelsTc': self.LevelsTc,
            'TimingsTc': self.TimingsTc,
        }


        # tests for FACT root
        t['s52c_check'] = AuxiliaryTC_TestBuilder(name='s52c_check', DataType='String', Expression='[E.BOMGROUP]==\'CLASS_NVL_S52C\' or [E.BOMGROUP]==\'CLASS_NVL_S52CB\' or [E.BOMGROUP]==\'CLASS_DNL_S52CB\'', ResultPort='[R]?2:1', Storage='SharedStorage', **dparams)
        
        # tests for FACT / BURN_SETUP root
        t['all_in_one_fork_cpu'] = ScreenTC_TestBuilder(name='all_in_one_fork_cpu', ScreenTestSet='AllInOneCheck', **dparams)
        t['perdie_state_init'] = ScreenTC_TestBuilder(name='perdie_state_init', ScreenTestSet='PerDieValuesInit_DUT', **dparams)
        #t['set_margins'] = PrimePatConfigTestMethod_TestBuilder(name='set_margins', SetPoint='ROOM_MARGIN', BypassPort=1, **dparams)
        
        # tests for FACT / BURN_SETUP / RETEST root
        t['get_fuse_string_status'] = FleGetDieStatusByDies_TestBuilder(name='get_fuse_string_status', FuseStateUservar='Which_Socket.FuseState', **dparams)
        #t['get_fuse_string_status_cpu1'] = FleGetDieStatus_TestBuilder(name='get_fuse_string_status_cpu1', FuseStateUservar='Which_Socket.FuseState', Register='CPU1', BypassPort=1, **dparams)
        t['check_fused_sspec'] = FleCheckFusedSspecFusing_TestBuilder(name='check_fused_sspec', Register='CPU0', **dparams)
        
        # test for FACT/ DATA_PROG
        t['hvm_fsg'] = FleGeneratePerDieFuseString_TestBuilder(name='hvm_fsg', Register='CPU0', BypassPort=1, **dparams)
        t['hvm_fsg_cpu1'] = FleGeneratePerDieFuseString_TestBuilder(name='hvm_fsg_cpu1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), **dparams)
        t['if_18ap'] = AuxiliaryTC_TestBuilder(name='if_18ap', BypassPort=-1, Expression="IsMatch([_UserVars.IF_18AP], 'YES')", DataType='String', Storage='UserVar', ResultPort='[R]?1:2', **dparams)
        t['hip_hash'] = FleUpdateSpecialAlgInFuseString_TestBuilder(name='hip_hash', Register='CPU0', **dparams)
        t['hip_hash_cpu1'] = FleUpdateSpecialAlgInFuseString_TestBuilder(name='hip_hash_cpu1', Register='CPU1', AlgorithmName="CPU1_HIP_HASH", BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'),**dparams)
        t['validation_fork'] = ScreenTC_TestBuilder(name='validation_fork', ScreenTestSet='ValForkTest', **dparams)
        t['check_facilityid_tpfuseenable'] = ScreenTC_TestBuilder(name='check_facilityid_tpfuseenable', ScreenTestSet='CheckFacilityID_TP_FUSE_Enabled', BypassPort=1, **dparams)

        #parallel setup
        #t['hvm_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn', ConfigName='FuseBurnFlow', BypassPort=-1, MaskNames='fle_str', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_hvm_data_x","IPC::cpu_fuse_write_hvm_data_mm")'), SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0,FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1","FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0")'),**dparams)
        #serial setup
        t['hvm_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn', ConfigName='FuseBurnFlow', BypassPort=-1, MaskNames='fle_str', Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_write_hvm_data_mm","IPC::cpu_fuse_write_hvm_all_mm")'), SharedStorageKeyToRead='FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0',**dparams)
        t['hvm_burn_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn_cpu1', ConfigName='FuseBurnFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), RegisterNames='CPU1', MaskNames='fle_str', Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_write_hvm_data_mm","IPC::cpu_fuse_write_hvm_all_mm")'), SharedStorageKeyToRead='FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1', **dparams)
        t['hvm_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='hvm_rap', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'),**dparams)
        t['hvm_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='hvm_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', ExpectedPort='2', ExceptionPort='1', FuseReadGlobal='FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1', FuseGroupToDatalog='', **dparams)
        t['hvm_flecompare'] = FleCompareFuseStringByDies_TestBuilder(name='hvm_flecompare', Category='MAIN_ARRAY_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        t['hvm_flecompare_cpu1'] = FleCompareFuseString_TestBuilder(name='hvm_flecompare_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1', **dparams)
       
        #tests for FACT / QUAL_PROG
        t['checkbom'] = AuxiliaryTC_TestBuilder(name='checkbom', DataType='String', Expression="IsMatch([_UserVars.IF_ProcessType], 'INT')", ResultPort='[R]?2:1', Storage='UserVar', **dparams)
        t['qual_prog'] = AuxiliaryTC_TestBuilder(name='qual_prog', DataType='String', Expression='[FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.QualProgBypass]==\'-1\' and [E.BOMGROUP]==\'CLASS_NVL_S28C\'', ResultPort='[R]?1:2', Storage='UserVar', **dparams)
        t['cmp_string_update'] = ScreenTC_TestBuilder(name='cmp_string_update', ScreenTestsFile="./InputFiles/FUSEBURN_ScreenQual.json", ScreenTestSet='UPDATE_STRING_TO_COMPARE', **dparams)
        t['ecc_status_preburn'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status_preburn', BypassPort=-1, ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_CXX_QUAL_ECC_CHK.csv")'), Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_read_hvm_ecc_statictics","IPC::cpu_fuse_shim_debug_status")'), PostInstance='PrintToItuff(--body_type mrslt --body_data G.U.D.Fuse_Voltage_VCCFPRGx_Prog_0_CPU0 --tname_suf _PRINT_VOLTAGE_NOM)', **dparams)
        t['qual_burn_row6'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='qual_burn_row6', isEDC=True, ConfigName='QualClassBurnFlow', BypassPort=-1, MaskNames='ClassQualBurn_Row_6_data_mask', Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_write_hvm_data_mm","IPC::cpu_fuse_write_hvm_all_mm")'), SharedStorageKeyToRead='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0',**dparams)
        t['logituff_failburn_row6'] = ScreenTC_TestBuilder(name='logituff_failburn_row6', ScreenTestsFile="./InputFiles/FUSEBURN_ScreenQual.json", ScreenTestSet='LOG_ITUFF_FAILBURN_ROW6', **dparams)
        t['perdie_high_init'] = ScreenTC_TestBuilder(name='perdie_high_init', ScreenTestsFile="./InputFiles/FUSEBURN_ScreenQual.json", ScreenTestSet='QualBurnVoltage_HIGH_DUT', **dparams)
        t['qual_burn_row78'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='qual_burn_row7_8', isEDC=True, ConfigName='QualClassBurnFlow', BypassPort=-1, MaskNames='ClassQualBurn_Row_7_8_data_mask', Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_write_hvm_data_mm","IPC::cpu_fuse_write_hvm_all_mm")'), SharedStorageKeyToRead='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0',**dparams)
        t['logituff_failburn_row78'] = ScreenTC_TestBuilder(name='logituff_failburn_row7_8', ScreenTestsFile="./InputFiles/FUSEBURN_ScreenQual.json", ScreenTestSet='LOG_ITUFF_FAILBURN_ROW7_8', **dparams)
        t['perdie_low_init'] = ScreenTC_TestBuilder(name='perdie_low_init', ScreenTestsFile="./InputFiles/FUSEBURN_ScreenQual.json", ScreenTestSet='QualBurnVoltage_LOW_DUT', **dparams)
        t['qual_burn_row910'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='qual_burn_row9_10', isEDC=True, ConfigName='QualClassBurnFlow', BypassPort=-1, MaskNames='ClassQualBurn_Row_9_10_data_mask', Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_write_hvm_data_mm","IPC::cpu_fuse_write_hvm_all_mm")'), SharedStorageKeyToRead='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0',**dparams)
        t['logituff_failburn_row910'] = ScreenTC_TestBuilder(name='logituff_failburn_row9_10', ScreenTestsFile="./InputFiles/FUSEBURN_ScreenQual.json", ScreenTestSet='LOG_ITUFF_FAILBURN_ROW9_10', **dparams)
        t['qual_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='qual_rap', ConfigName='QualClass_Row_6to10_RAP', isEDC=True, BypassPort=-1, PassingMaskName='mask_QualClass_Row_6to10_check', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'),**dparams)
        t['logituff_failrap'] = ScreenTC_TestBuilder(name='logituff_failrap', ScreenTestsFile="./InputFiles/FUSEBURN_ScreenQual.json", ScreenTestSet='LOG_ITUFF_FAIL_RAP', **dparams)
        t['ecc_status_postburn'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status_postburn', BypassPort=-1, ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_CXX_QUAL_ECC_CHK.csv")'), Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_read_hvm_ecc_statictics","IPC::cpu_fuse_shim_debug_status")'), **dparams)
        t['ecc_status_row6'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status_row6', BypassPort=-1, ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_CXX_QUAL_ECC_CHK_PER_ROW.csv")'), Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_read_hvm_ecc_statictics","IPC::cpu_fuse_shim_debug_status3_mfgrow6")'), **dparams)
        t['ecc_status_row7'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status_row7', BypassPort=-1, ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_CXX_QUAL_ECC_CHK_PER_ROW.csv")'), Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_read_hvm_ecc_statictics","IPC::cpu_fuse_shim_debug_status3_mfgrow7")'), **dparams)
        t['ecc_status_row8'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status_row8', BypassPort=-1, ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_CXX_QUAL_ECC_CHK_PER_ROW.csv")'), Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_read_hvm_ecc_statictics","IPC::cpu_fuse_shim_debug_status3_mfgrow8")'), **dparams)
        t['ecc_status_row9'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status_row9', BypassPort=-1, ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_CXX_QUAL_ECC_CHK_PER_ROW.csv")'), Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_read_hvm_ecc_statictics","IPC::cpu_fuse_shim_debug_status3_mfgrow9")'), **dparams)
        t['ecc_status_row10'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status_row10', BypassPort=-1, ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_CXX_QUAL_ECC_CHK_PER_ROW.csv")'), Patlist=Spec('__shared__::TpRule.If_18AP("IPC::cpu_fuse_read_hvm_ecc_statictics","IPC::cpu_fuse_shim_debug_status3_mfgrow10")'), **dparams)
        t['perdie_nom_init'] = ScreenTC_TestBuilder(name='perdie_nom_init', ScreenTestSet='PerDieValuesInit_DUT', **dparams)
              
        #tests for FACT / ECC_PROG / ECC_SPECIAL_ROW_IR
        t['ecc_ir'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_ir', ConfigName='FusingFlowSpecialIR', BypassPort=-1, RegisterNames=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), PassingMaskName='virgin_sprow_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
        t['ecc_ir_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_ir_cpu1', ConfigName='FusingFlowSpecialIR_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), RegisterName='SPROWD1', PassingMaskName='virgin_sprow_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
       
        #tests for FACT / ECC_PROG / ECC_STRING_GEN 
        t['ecc_fle_fsg'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg', FuseChassis='CH4', BypassPort=-1, Process='10nm', Register='CPU0', **dparams)
        t['ecc_fle_fsg_cpu1'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg_cpu1', FuseChassis='CH4', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), Process='10nm', Register='CPU1', **dparams)
        
        #tests for FACT / ECC_PROG / ECC_ROW_PROG
        #Parallel setup
        #t['ecc_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data', ConfigName='FuseECCFlow', BypassPort=-1, MaskNames='data_for_ecc_mask', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_hvm_ecc_x","IPC::cpu_fuse_write_hvm_ecc_mm")'), SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #Serial setup
        t['ecc_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data', ConfigName='FuseECCFlow', BypassPort=-1, MaskNames='data_for_ecc_mask', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_hvm_ecc_x","IPC::cpu_fuse_write_hvm_ecc_mm")'), SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0", **dparams)
        t['ecc_fuseburn_data_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data_cpu1', ConfigName='FuseECCFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), MaskNames='data_for_ecc_mask', Patlist='IPC::cpu_fuse_write_hvm_ecc_x', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1",**dparams)
        
        #tests for FACT / ECC_PROG / ECC_RAP
        t['ecc_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0")'), **dparams)
        #t['ecc_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='ecc_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', ExpectedPort='2', ExceptionPort='1', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', FuseReadGlobal="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1", **dparams)
        t['ecc_rap_flecompare'] = FleCompareFuseStringByDies_TestBuilder(name='ecc_rap_flecompare', Category='MAIN_ARRAY_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0")'), **dparams)
        t['ecc_rap_flecompare_cpu1'] = FleCompareFuseString_TestBuilder(name='ecc_rap_flecompare_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1', **dparams)
       
        #tests for FACT / ECC_PROG / ECC_FAILFLOW
        t['ecc_check_func'] = PrimeFunctionalTestMethod_TestBuilder(name='ecc_check_func', BypassPort=1, Patlist='IPC::cpu_fuse_read_hvm_ecc_status', **dparams)

        #tests for FACT / LOCKOUT_PROG / TAP_UNLOCK
        t['tap_status'] = PrimeCtvDecoderTestMethod_TestBuilder(name='tap_status', BypassPort=-1, Patlist='IPC::cpu_dfxagg_read_hvm_status_csr', **dparams)
        t['unit_info_decode'] = ScreenTC_TestBuilder(name='unit_info_decode', ScreenTestsFile=Spec('__shared__::TpRule.If_MICP(GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C2X.screen.json",GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C1X.screen.json")'), ScreenTestSet='STATUS_SET_PIC8_PrimeCtvDecoderTestMethod', **dparams)
        t['screen_red_unlock'] = ScreenTC_TestBuilder(name='red_unlock', ScreenTestsFile=Spec('__shared__::TpRule.If_MICP(GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C2X.screen.json",GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C1X.screen.json")'), ScreenTestSet='RED_KEY_split_by_32bits_MsbToLsb', **dparams)
        t['red_unlock'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock',  SetPoint='RDULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        t['legacy_unlock'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock',  SetPoint='LGULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        
        #tests for FACT / LOCKOUT_PROG
        t['lockbit_fsg'] = FleGenerateLockoutBitsFuseStringByDies_TestBuilder(name='lockbit_fsg', **dparams)
        t['lockbit_fsg_cpu1'] = FleGenerateLockoutBitsFuseString_TestBuilder(name='lockbit_fsg_cpu1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), **dparams)
        #Parallel setup
        #t['lockbit_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='lockbit_burn', ConfigName='FuseBurnLockoutFlow', BypassPort=-1, MaskNames='fle_lockout_str', Patlist='IPC::cpu_fuse_write_hvm_lockout', SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #Serial setup
        t['lockbit_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='lockbit_burn', ConfigName='FuseBurnLockoutFlow', BypassPort=-1, MaskNames='fle_lockout_str', Patlist='IPC::cpu_fuse_write_hvm_lockout', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0", **dparams)
        t['lockbit_burn_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='lockbit_burn_cpu1', ConfigName='FuseBurnLockoutFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), MaskNames='fle_lockout_str', Patlist='IPC::cpu_fuse_write_hvm_lockout', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1", **dparams)
        t['lockbit_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='lockbit_rap', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0")'), **dparams)
        #t['lockbit_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='lockbit_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', ExpectedPort='2', ExceptionPort='1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', FuseReadGlobal="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1", **dparams)
        t['lockbit_rap_flecompare'] = FleCompareFuseStringByDies_TestBuilder(name='lockbit_rap_flecompare', Category='LOCKOUTBIT_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0")'), **dparams)
        t['lockbit_rap_flecompare_cpu1'] = FleCompareFuseString_TestBuilder(name='lockbit_rap_flecompare_cpu1', Category='LOCKOUTBIT_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1', **dparams)
       
        #tests for FACT / ECC_SET
        #t['ecc_set_arr0'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_set_arr0', ConfigName='FuseECCFlow', BypassPort=1, MaskNames='ECC_Set_Arr0_mask', Patlist='IPC::cpu_fuse_write_special_eccset', **dparams)
        #t['ecc_set_arr0_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_set_arr0_cpu1', ConfigName='FuseECCFlow_CPU1', BypassPort=1, RegisterNames='SPROWD1', MaskNames='ECC_Set_Arr0_mask', Patlist='IPC::cpu_fuse_write_special_eccset', **dparams)
        #t['ecc_rap_arr0'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_arr0', ConfigName='FusingFlowECCRead', BypassPort=1, PassingMaskName='ECC_ARR0_check_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
        #t['ecc_rap_arr0_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_arr0_cpu1', ConfigName='FusingFlowECCRead_CPU1', BypassPort=1, RegisterName='SPROWD1', PassingMaskName='ECC_ARR0_check_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
        t['ecc_status'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status', BypassPort=-1, ConfigurationFile=Spec('FUS_FUSEBURN_CXX_Rules.FUSEBURN_CtvFile("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_C1X_ECC_Check.csv","./InputFiles/FUSEBURN_C2X_TSMC_ECC_Check.csv","./InputFiles/FUSEBURN_C1X_TSMC_ECC_Check.csv","./InputFiles/FUSEBURN_C1X_TSMC_ECC_Check.csv")'), Patlist='IPC::cpu_fuse_read_hvm_ecc_statictics', **dparams)
        t['ecc_preamble_func'] = PrimeFunctionalTestMethod_TestBuilder(name='ecc_preamble_func', isEDC=True, BypassPort=-1, Patlist='IPC::cpu_fuse_read_hvm_ecc_statictics', **dparams)

        #tests for FACT / RETEST_STORE / EFUSE_READ
        t['efuse_read'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuse_read', ConfigName='CXX_EFUSEReadFlow', BypassPort=-1, RegisterName=Spec('__shared__::TpRule.If_MICP("CPU0_EFUSE,CPU1_EFUSE","CPU0_EFUSE")'), PassingMaskName='PMaskName_All_ss', FailingMaskName='FMaskName_All_00,FMaskName_All_11,FMaskName_All_01,FMaskName_All_10', Patlist='IPC::cpu_dfxagg_read_hvm_efuse', FuseGroupToDatalog='EFUSE_ULT', PrintUltDataPerDieIdToItuff='DISABLED', **dparams)
        #t['efuse_read_cpu1'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuse_read_cpu1', ConfigName='EFUSEReadFlow_cpu1', BypassPort=1, RegisterName='CPU1_EFUSE', PassingMaskName='PMaskName_All_ss', FailingMaskName='FMaskName_All_00,FMaskName_All_11,FMaskName_All_01,FMaskName_All_10', Patlist='IPC::cpu_dfxagg_read_hvm_efuse', FuseGroupToDatalog='EFUSE_ULT', DieIdNames=Spec('__shared__::DFFVars.DIEID_CPU1'), **dparams)
        t['fuse_efuse_compare'] = ScreenTC_TestBuilder(name='fuse_efuse_compare', ScreenTestSet='EFUSE_CHECK', **dparams)
        t['dff_ult_efuse_compare'] = SFMDffEfuseCheck_TestBuilder(name='dff_ult_efuse_compare', DieIdName=Spec('__shared__::DFFVars.DIEID_CPU'), **dparams)
        t['dff_ult_efuse_compare_cpu1'] = SFMDffEfuseCheck_TestBuilder(name='dff_ult_efuse_compare_cpu1', DieIdName=Spec('__shared__::DFFVars.DIEID_CPU1'), BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), **dparams)
        
        #tests for FACT / RETEST_STORE
        t['security_key_hashgen'] = FleComputeFuseHashSignatureByDies_TestBuilder(name='security_key_hashgen', FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0")'), **dparams)
        t['security_key_hashgen_cpu1'] = FleComputeFuseHashSignature_TestBuilder(name='security_key_hashgen_cpu1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1', **dparams)
        t['post_process_hostkey'] = ScreenTC_TestBuilder(name='post_process_hostkey_for_hash_setup', ScreenTestSet='HASH_SETUP_CPU', **dparams)
        t['apply_gen_hash'] = PrimePatConfigTestMethod_TestBuilder(name='apply_gen_hash', SetPoint='SET_HASHSIG_CPU', BypassPort=-1, **dparams)
        t['read_hash_status'] = PrimeFunctionalTestMethod_TestBuilder(name='read_hash_status', BypassPort=-1, Patlist='IPC::cpu_fuse_hvm_hash', **dparams)

        #test for FACT / FEEDBACK
        t['security_set'] = FleISeedSetUnitKeys_TestBuilder(name='security_set', **dparams)
        t['post_fuse_confirm'] = RunCallback_TestBuilder(name='post_fuse_confirm', BypassPort=-1, Parameters='--token G.U.S.CLASSFUSED_CPU0 --value 1', **dparams)
        #t['extract_partid_feedback'] = FleISeedCapturePartId_TestBuilder(name='extract_partid_feedback', CtvCapturePins=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("IPC::CPU_TDO","IPC::CPU_TDO, IPC::CPU1_TDO")'), BypassPort=Spec('__shared__::TpRule.If_MICP(1,-1)'), **dparams)

        #test for FACT / FEEDBACK_FAIL
        t['security_set_ff'] = FleISeedSetUnitKeys_TestBuilder(name='security_set_ff', **dparams)
        #t['extract_partid_feedback_failflow'] = FleISeedCapturePartId_TestBuilder(name='extract_partid_feedback_failflow', CtvCapturePins=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("IPC::CPU_TDO","IPC::CPU_TDO, IPC::CPU1_TDO")'), BypassPort=Spec('__shared__::TpRule.If_MICP(1,-1)'), **dparams)

        #test for FACT/ REPAIR_PROG
        t['if_18ap_repair'] = AuxiliaryTC_TestBuilder(name='if_18ap_repair', BypassPort=-1, Expression="IsMatch([_UserVars.IF_18AP], 'YES')", DataType='String', Storage='UserVar', ResultPort='[R]?1:2', **dparams)
        
        #test for FACT/ REPAIR_PROG / SPECIAL_ROW_IR
        t['repair_ir'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='repair_ir', ConfigName='FusingFlowSpecialIR', BypassPort=Spec('__shared__::TpRule.If_18AP(-1,1)'), RegisterName=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), PassingMaskName='virgin_sprow_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0")'), **dparams)
        #t['repair_ir_cpu1'] = SFMFuseReadMask_TestBuilder(name='repair_ir_cpu1', ConfigName='FusingFlowSpecialIR_CPU1', BypassPort=1, RegisterName='SPROWD1', FuseMaskName='virgin_sprow_mask', PassingMaskName='virgin_sprow_mask', ExpectedPort='1', ExceptionPort='2', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', FuseReadGlobal='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1', **dparams)

        #test for FACT/ REPAIR_PROG / REPAIR_STRING_GEN
        t['repair_fle_fsg'] = FleGenerateFuseRepairString_TestBuilder(name='repair_fle_fsg', FuseChassis='CH4', BypassPort=-1, Process='7nm', Register='CPU0', FuseReadTokenName = "FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0", **dparams)
        t['repair_fle_fsg_cpu1'] = FleGenerateFuseRepairString_TestBuilder(name='repair_fle_fsg_cpu1', FuseChassis='CH4', _comment=["NOCLEAN"], BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), Process='7nm', Register='CPU1', FuseReadTokenName = "FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1",**dparams)
        
        #test for FACT/ REPAIR_PROG / SPECIAL_ROW_PROG
        #Parallel setup
        #t['repair_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_data', ConfigName='FuseRepairDataFlow', BypassPort=-1, RegisterNames=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), MaskNames='sprow_data_mask', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_special_data_x","IPC::cpu_fuse_write_special_data_mm")'), SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0")'), **dparams)
        #Serial setup
        t['repair_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_data', ConfigName='FuseRepairDataFlow', BypassPort=Spec('__shared__::TpRule.If_18AP(-1,1)'), RegisterNames="SPROWD0", MaskNames='sprow_data_mask', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_special_data_x","IPC::cpu_fuse_write_special_data_mm")'), SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0", **dparams)
        t['repair_fuseburn_data_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_data_cpu1', ConfigName='FuseRepairDataFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), RegisterNames='SPROWD1', MaskNames='sprow_data_mask', Patlist='IPC::cpu_fuse_write_special_data_x', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1", **dparams)
        #t['repair_fuseburn_cfg'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_cfg', ConfigName='FuseRepairCfgFlow', BypassPort=Spec('__shared__::TpRule.If_MICP(1,-1)'), RegisterNames=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("SPROWD0","SPROWD0,SPROWD1")'), MaskNames='sprow_cfg_mask', Patlist='IPC::cpu_fuse_write_special_data_x', **dparams)
        #t['repair_fuseburn_cfg_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_cfg_cpu1', ConfigName='FuseRepairCfgFlow_CPU1', BypassPort=1, RegisterNames='SPROWD1', MaskNames='sprow_cfg_mask', Patlist='IPC::cpu_fuse_write_special_data_x', **dparams)
        
        #test for FACT/ REPAIR_PROG / DATA_RAP
        t['repair_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='repair_rap', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #t['repair_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='repair_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', ExpectedPort='2', ExceptionPort='1', FuseGroupToDatalog='', FuseReadGlobal='FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1', **dparams)
        t['repair_rap_compfle'] = FleCompareFuseStringByDies_TestBuilder(name='repair_rap_compfle', Category='MAIN_ARRAY_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #t['repair_rap_compfle_cpu1'] = FleCompareFuseString_TestBuilder(name='repair_rap_compfle_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutpuStr', **dparams)
       
        #test for FACT/ REPAIR_PROG / ECC_STRING_GEN_REPAIRED
        #t['ecc_fle_fsg_repaired'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg_repaired', FuseChassis='CH4', BypassPort=-1, Process='7nm', Register='CPU0', **dparams)
        #t['ecc_fle_fsg_repaired_cpu1'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg_repaired_cpu1', FuseChassis='CH4', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Process='7nm', Register='CPU1', **dparams)
        
        #test for FACT/ REPAIR_PROG / ECC_SPECIAL_ROW_PROG_REPAIRED
        #t['ecc_fuseburn_data_repaired'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data_repaired', ConfigName='FuseRepairDataFlow', BypassPort=-1, RegisterNames=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("SPROWD0","SPROWD0,SPROWD1")'), MaskNames='sprow_data_mask', Patlist='cpu_fuse_write_special_data_x', **dparams)
        #t['ecc_fuseburn_data_repaired_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data_repaired_cpu1', ConfigName='FuseRepairDataFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), RegisterNames='SPROWD1', MaskNames='sprow_data_mask', Patlist='cpu_fuse_write_special_data_x', **dparams)
       
        #test for FACT/ REPAIR_PROG / ECC_RAP_REPAIRED
        #t['ecc_rap_repaired'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_repaired', ConfigName='FuseFlowDataRAP', BypassPort=-1, PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', **dparams)
        #t['ecc_rap_repaired_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_repaired_cpu1', ConfigName='FuseFlowDataRAP', BypassPort=1, RegisterName='CPU1', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', **dparams)
        #t['ecc_rap_compfle_repaired'] = FleCompareFuseString_TestBuilder(name='ecc_rap_compfle_repaired', Category='MAIN_ARRAY_CAT', BypassPort=-1, Register='CPU0', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutpuStr', **dparams)
        #t['ecc_rap_compfle_repaired_cpu1'] = FleCompareFuseString_TestBuilder(name='ecc_rap_compfle_repaired_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutpuStr', **dparams)
       
        #test for FACT/ REPAIR_PROG / REPAIR_FAILFLOW
        t['sr_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='sr_rap', ConfigName='FusingFlowSpecialRAP', BypassPort=1, RegisterName=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), PassingMaskName='mask_REPAIR_ARR0_check', Patlist='cpu_fuse_read_special_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU0,FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU1","FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU0")'), **dparams)
        #t['sr_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='sr_rap_cpu1', ConfigName='FusingFlowSpecialRAP_CPU1', BypassPort=1, RegisterName='SPROWD1', FuseMaskName='mask_REPAIR_ARR0_check', Patlist='cpu_fuse_read_special_x', ExpectedPort='1', ExceptionPort='2', FuseGroupToDatalog='', FuseReadGlobal='FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU1', **dparams)
        #t['srdata_compfle'] = FleCompareFuseString_TestBuilder(name='repairff_srdata_compfle', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=-1, Register='SPROWD0', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        #t['srdata_compfle_cpu1'] = FleCompareFuseString_TestBuilder(name='repairff_srdata_compfle_cpu1', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Register='SPROWD1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        #t['srcfg_compfle'] = FleCompareFuseString_TestBuilder(name='repairff_srcfg_compfle', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=-1, Register='SPROWD0', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        #t['srcfg_compfle_cpu1'] = FleCompareFuseString_TestBuilder(name='repairff_srcfg_compfle_cpu1', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Register='SPROWD1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        t['repair_ecccheck_func'] = PrimeFunctionalTestMethod_TestBuilder(name='repair_ecccheck_func', _comment=["NOCLEAN"], BypassPort=1, Patlist='IPC::cpu_fuse_read_hvm_ecc_status', **dparams)

       




        ##Flow Setup
        burn_setup_retest_fitems = []
        burn_setup_retest_fitems.append(t['get_fuse_string_status'].get_fitem(r0=pFail(setbin=self.bin(315600, offset), ret=0),
                                                                              r1=pPass(ret=3),
                                                                              r2=pFail(setbin=self.bin(315601, offset), ret=0),
                                                                              r3=pPass(goto='NEXT'),
                                                                              r4=pFail(setbin=self.bin(315602, offset), ret=0),
                                                                              r5=pFail(setbin=self.bin(315603, offset), ret=0)
                                                                              ))
        #burn_setup_retest_fitems.append(t['get_fuse_string_status_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315697, offset), ret=0),
        #                                                                      r1=pPass(ret=3),
        #                                                                      r2=pFail(setbin=self.bin(315698, offset), ret=0),
        #                                                                      r3=pPass(goto='NEXT'),
        #                                                                      r4=pFail(setbin=self.bin(315699, offset), ret=0)
        #                                                                      ))
        burn_setup_retest_fitems.append(t['check_fused_sspec'].get_fitem(r0=pFail(setbin=self.bin(315500, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315501, offset), ret=0)))
        burn_setup_retest_composite = Flow('RETEST', *burn_setup_retest_fitems)

        burn_setup_fitems = []
        burn_setup_fitems.append(t['all_in_one_fork_cpu'].get_fitem(r0=pFail(setbin=self.bin(315800, offset), ret=0),
                                                                    r1=pPass(ret=1),
                                                                    r2=pFail(setbin=self.bin(315801, offset), ret=0),
                                                                    r3=pPass(goto='NEXT'),
                                                                    r4=pFail(setbin=self.bin(315802, offset), ret=0),
                                                                    r5=pFail(setbin=self.bin(315803, offset), ret=0),
                                                                    r6=pFail(setbin=self.bin(315804, offset), ret=0),
                                                                    r7=pFail(setbin=self.bin(315805, offset), ret=0),
                                                                    r8=pFail(setbin=self.bin(315806, offset), ret=0),
                                                                    r9=pFail(setbin=self.bin(315807, offset), ret=0),
                                                                    r10=pFail(setbin=self.bin(315808, offset), ret=0)
                                                                    ))
        burn_setup_fitems.append(Fitem('SAME', burn_setup_retest_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto="NEXT")))
        burn_setup_fitems.append(t['perdie_state_init'].get_fitem(r0=pFail(setbin=self.bin(315810, offset), ret=0),
                                                                  r1=pPass(ret=3),
                                                                  r2=pFail(setbin=self.bin(315811, offset), ret=0),
                                                                  r3=pFail(setbin=self.bin(315812, offset), ret=0),
                                                                  r4=pFail(setbin=self.bin(315813, offset), ret=0),
                                                                  r5=pFail(setbin=self.bin(315814, offset), ret=0),
                                                                  r6=pFail(setbin=self.bin(315815, offset), ret=0),
                                                                  r7=pFail(setbin=self.bin(315816, offset), ret=0),
                                                                  r8=pFail(setbin=self.bin(315817, offset), ret=0),
                                                                  r9=pFail(setbin=self.bin(315818, offset), ret=0),
                                                                  r10=pFail(setbin=self.bin(315819, offset), ret=0)
                                                                  ))
        #burn_setup_fitems.append(t['set_margins'].get_fitem(r0=pFail(setbin=self.bin(315700, offset), ret=0)))
        burn_setup_composite = Flow('BURN_SETUP', *burn_setup_fitems)

        data_prog_fitems = []
        data_prog_fitems.append(t['hvm_fsg'].get_fitem(r0=pFail(setbin=self.bin(315006, offset),ret=0), r2=pFail(setbin=self.bin(315007, offset), ret=0)))
        data_prog_fitems.append(t['hvm_fsg_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315098, offset), ret=0), r2=pFail(setbin=self.bin(315099, offset), ret=0)))
        data_prog_fitems.append(t['if_18ap'].get_fitem(r0=pFail(setbin=self.bin(315401, offset), ret=0),
                                                       r2=pPass(goto='FUSE_X_SCREENTC_K_FACTFUSBURNCPUNOM_X_X_X_X_VALIDATION_FORK')))
        data_prog_fitems.append(t['hip_hash'].get_fitem(r0=pFail(setbin=self.bin(315006, offset),ret=0), r2=pPass(goto="NEXT")))
        data_prog_fitems.append(t['hip_hash_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315007, offset), ret=0), r2=pPass(goto="NEXT")))
        data_prog_fitems.append(t['validation_fork'].get_fitem(r0=pFail(setbin=self.bin(315820, offset), ret=0),
                                                               r2=pPass(ret=1),
                                                               r3=pFail(setbin=self.bin(315821, offset), ret=0),
                                                               r4=pFail(setbin=self.bin(315822, offset), ret=0),
                                                               r5=pFail(setbin=self.bin(315823, offset), ret=0),
                                                               r6=pFail(setbin=self.bin(315824, offset), ret=0),
                                                               r7=pFail(setbin=self.bin(315825, offset), ret=0),
                                                               r8=pFail(setbin=self.bin(315826, offset), ret=0),
                                                               r9=pFail(setbin=self.bin(315827, offset), ret=0),
                                                               r10=pFail(setbin=self.bin(315828, offset), ret=0),

                                                               ))
        data_prog_fitems.append(t['check_facilityid_tpfuseenable'].get_fitem(r0=pFail(setbin=self.bin(315830, offset), ret=0),
                                                                             r2=pPass(ret=1),
                                                                             r3=pFail(setbin=self.bin(315831, offset), ret=0),
                                                                             r4=pFail(setbin=self.bin(315832, offset), ret=0),
                                                                             r5=pFail(setbin=self.bin(315833, offset), ret=0),
                                                                             r6=pFail(setbin=self.bin(315834, offset), ret=0),
                                                                             r7=pFail(setbin=self.bin(315835, offset), ret=0),
                                                                             r8=pFail(setbin=self.bin(315836, offset), ret=0),
                                                                             r9=pFail(setbin=self.bin(315837, offset), ret=0),
                                                                             r10=pFail(setbin=self.bin(315838, offset), ret=0),

                                                               ))
        data_prog_fitems.append(t['hvm_burn'].get_fitem(r0=pFail(setbin=self.bin(315200, offset), ret=0),
                                                        r2=pFail(setbin=self.bin(315201, offset), ret=0)))
        data_prog_fitems.append(t['hvm_burn_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315202, offset), ret=0),
                                                             r2=pFail(setbin=self.bin(315203, offset), ret=0)))
        data_prog_fitems.append(t['hvm_rap'].get_fitem(r0=pFail(setbin=self.bin(315100, offset), ret=0),
                                                       r2=pPass(goto='NEXT')))
        data_prog_fitems.append(t['hvm_flecompare'].get_fitem(r0=pFail(setbin=self.bin(315101, offset), ret=0),
                                                              r1=pPass(ret=3),
                                                              r2=pPass(ret=4)))
        #data_prog_fitems.append(t['hvm_rap_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315100, offset), ret=0),
        #                                                   r2=pPass(goto='NEXT')))
        #data_prog_fitems.append(t['hvm_flecompare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315101, offset), ret=0),
        #                                                           r1=pPass(ret=3),
        #                                                           r2=pPass(ret=4)))
        data_prog_composite = Flow('DATA_PROG', *data_prog_fitems)

        qual_prog_fitems = []
        qual_prog_fitems.append(t['checkbom'].get_fitem(r0=pFail(setbin=self.bin(315403, offset), ret=0),
                                                         r2=pPass(ret=2)))
        qual_prog_fitems.append(t['qual_prog'].get_fitem(r0=pFail(setbin=self.bin(315402, offset), ret=0),
                                                         r2=pPass(ret=1)))
        qual_prog_fitems.append(t['cmp_string_update'].get_fitem(r0=pFail(setbin=self.bin(315840, offset2), ret=0),                                                            
                                                                 r1=pPass(goto="NEXT"),
                                                                 r2=pFail(setbin=self.bin(315841, offset2), ret=0),
                                                                 r3=pFail(setbin=self.bin(315842, offset2), ret=0),
                                                                 r4=pFail(setbin=self.bin(315843, offset2), ret=0),
                                                                 r5=pFail(setbin=self.bin(315844, offset2), ret=0),
                                                                 r6=pFail(setbin=self.bin(315845, offset2), ret=0),
                                                                 r7=pFail(setbin=self.bin(315846, offset2), ret=0),
                                                                 r8=pFail(setbin=self.bin(315847, offset2), ret=0),
                                                                 r9=pFail(setbin=self.bin(315848, offset2), ret=0),
                                                                 r10=pFail(setbin=self.bin(315849, offset2), ret=0)
                                                             ))
        qual_prog_fitems.append(t['ecc_status_preburn'].get_fitem(r0=pFail(setbin=self.bin(315905, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315906, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(315907, offset), ret=0),
                                                         r4=pFail(setbin=self.bin(315908, offset), ret=0),
                                                         r5=pFail(setbin=self.bin(315909, offset), ret=0),
                                                         ))
        qual_prog_fitems.append(t['qual_burn_row6'].get_fitem(r0=pFail(setbin=self.bin(315216, offset), goto='NEXT'),
                                                              r1=pPass(goto="FUSE_X_SCREENTC_K_FACTFUSBURNCPUNOM_X_X_X_X_PERDIE_HIGH_INIT"),
                                                              r2=pFail(setbin=self.bin(315217, offset), goto='NEXT')))
        qual_prog_fitems.append(t['logituff_failburn_row6'].get_fitem(r0=pFail(setbin=self.bin(315800, offset2), ret=0),                                                            
                                                             r1=pPass(goto="FUSE_X_SCREENTC_K_FACTFUSBURNCPUNOM_X_X_X_X_PERDIE_HIGH_INIT"),
                                                             r2=pFail(setbin=self.bin(315801, offset2), ret=0),
                                                             r3=pFail(setbin=self.bin(315802, offset2), ret=0),
                                                             r4=pFail(setbin=self.bin(315803, offset2), ret=0),
                                                             r5=pFail(setbin=self.bin(315804, offset2), ret=0),
                                                             r6=pFail(setbin=self.bin(315805, offset2), ret=0),
                                                             r7=pFail(setbin=self.bin(315806, offset2), ret=0),
                                                             r8=pFail(setbin=self.bin(315807, offset2), ret=0),
                                                             r9=pFail(setbin=self.bin(315808, offset2), ret=0),
                                                             r10=pFail(setbin=self.bin(315809, offset2), ret=0)
                                                             ))
        qual_prog_fitems.append(t['perdie_high_init'].get_fitem(r0=pFail(setbin=self.bin(315870, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(315871, offset), ret=0),
                                                                r3=pFail(setbin=self.bin(315872, offset), ret=0),
                                                                r4=pFail(setbin=self.bin(315873, offset), ret=0),
                                                                r5=pFail(setbin=self.bin(315874, offset), ret=0),
                                                                r6=pFail(setbin=self.bin(315875, offset), ret=0),
                                                                r7=pFail(setbin=self.bin(315876, offset), ret=0),
                                                                r8=pFail(setbin=self.bin(315877, offset), ret=0),
                                                                r9=pFail(setbin=self.bin(315878, offset), ret=0),
                                                                r10=pFail(setbin=self.bin(315879, offset), ret=0)
                                                                ))
        qual_prog_fitems.append(t['qual_burn_row78'].get_fitem(r0=pFail(setbin=self.bin(315218, offset), goto='NEXT'),
                                                               r1=pPass(goto="FUSE_X_SCREENTC_K_FACTFUSBURNCPUNOM_X_X_X_X_PERDIE_LOW_INIT"),
                                                               r2=pFail(setbin=self.bin(315219, offset), goto='NEXT')))
        qual_prog_fitems.append(t['logituff_failburn_row78'].get_fitem(r0=pFail(setbin=self.bin(315810, offset2), ret=0),                                                            
                                                              r1=pPass(goto="FUSE_X_SCREENTC_K_FACTFUSBURNCPUNOM_X_X_X_X_PERDIE_LOW_INIT"),
                                                              r2=pFail(setbin=self.bin(315811, offset2), ret=0),
                                                              r3=pFail(setbin=self.bin(315812, offset2), ret=0),
                                                              r4=pFail(setbin=self.bin(315813, offset2), ret=0),
                                                              r5=pFail(setbin=self.bin(315814, offset2), ret=0),
                                                              r6=pFail(setbin=self.bin(315815, offset2), ret=0),
                                                              r7=pFail(setbin=self.bin(315816, offset2), ret=0),
                                                              r8=pFail(setbin=self.bin(315817, offset2), ret=0),
                                                              r9=pFail(setbin=self.bin(315818, offset2), ret=0),
                                                              r10=pFail(setbin=self.bin(315819, offset2), ret=0)
                                                              ))
        qual_prog_fitems.append(t['perdie_low_init'].get_fitem(r0=pFail(setbin=self.bin(315880, offset), ret=0),
                                                               r2=pFail(setbin=self.bin(315881, offset), ret=0),
                                                               r3=pFail(setbin=self.bin(315882, offset), ret=0),
                                                               r4=pFail(setbin=self.bin(315883, offset), ret=0),
                                                               r5=pFail(setbin=self.bin(315884, offset), ret=0),
                                                               r6=pFail(setbin=self.bin(315885, offset), ret=0),
                                                               r7=pFail(setbin=self.bin(315886, offset), ret=0),
                                                               r8=pFail(setbin=self.bin(315887, offset), ret=0),
                                                               r9=pFail(setbin=self.bin(315888, offset), ret=0),
                                                               r10=pFail(setbin=self.bin(315889, offset), ret=0)
                                                                  ))
        qual_prog_fitems.append(t['qual_burn_row910'].get_fitem(r0=pFail(setbin=self.bin(315220, offset), goto='NEXT'),
                                                                r1=pPass(goto="FUSE_X_FUSEREAD_E_FACTFUSBURNCPUNOM_X_X_X_X_QUAL_RAP"),
                                                                r2=pFail(setbin=self.bin(315221, offset), goto='NEXT')))
        qual_prog_fitems.append(t['logituff_failburn_row910'].get_fitem(r0=pFail(setbin=self.bin(315820, offset2), ret=0),                                                            
                                                               r1=pPass(goto="FUSE_X_FUSEREAD_E_FACTFUSBURNCPUNOM_X_X_X_X_QUAL_RAP"),
                                                               r2=pFail(setbin=self.bin(315821, offset2), ret=0),
                                                               r3=pFail(setbin=self.bin(315822, offset2), ret=0),
                                                               r4=pFail(setbin=self.bin(315823, offset2), ret=0),
                                                               r5=pFail(setbin=self.bin(315824, offset2), ret=0),
                                                               r6=pFail(setbin=self.bin(315825, offset2), ret=0),
                                                               r7=pFail(setbin=self.bin(315826, offset2), ret=0),
                                                               r8=pFail(setbin=self.bin(315827, offset2), ret=0),
                                                               r9=pFail(setbin=self.bin(315828, offset2), ret=0),
                                                               r10=pFail(setbin=self.bin(315829, offset2), ret=0)
                                                               ))
        qual_prog_fitems.append(t['qual_rap'].get_fitem(r0=pFail(setbin=self.bin(315138, offset), goto='NEXT'),
                                                        r1=pPass(goto="FUSE_X_CTVDECODER_K_FACTFUSBURNCPUNOM_X_X_X_X_ECC_STATUS_POSTBURN"),
                                                        r2=pFail(setbin=self.bin(315139, offset), goto='NEXT')))
        qual_prog_fitems.append(t['logituff_failrap'].get_fitem(r0=pFail(setbin=self.bin(315830, offset2), ret=0),                                                            
                                                              r1=pPass(goto="FUSE_X_CTVDECODER_K_FACTFUSBURNCPUNOM_X_X_X_X_ECC_STATUS_POSTBURN"),
                                                              r2=pFail(setbin=self.bin(315831, offset2), ret=0),
                                                              r3=pFail(setbin=self.bin(315832, offset2), ret=0),
                                                              r4=pFail(setbin=self.bin(315833, offset2), ret=0),
                                                              r5=pFail(setbin=self.bin(315834, offset2), ret=0),
                                                              r6=pFail(setbin=self.bin(315835, offset2), ret=0),
                                                              r7=pFail(setbin=self.bin(315836, offset2), ret=0),
                                                              r8=pFail(setbin=self.bin(315837, offset2), ret=0),
                                                              r9=pFail(setbin=self.bin(315838, offset2), ret=0),
                                                              r10=pFail(setbin=self.bin(315839, offset2), ret=0)
                                                              ))
        qual_prog_fitems.append(t['ecc_status_postburn'].get_fitem(r0=pFail(setbin=self.bin(315910, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315911, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(315912, offset), ret=0),
                                                         r4=pFail(setbin=self.bin(315913, offset), ret=0),
                                                         r5=pFail(setbin=self.bin(315914, offset), ret=0),
                                                         ))
        qual_prog_fitems.append(t['ecc_status_row6'].get_fitem(r0=pFail(setbin=self.bin(315915, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315916, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(315917, offset), ret=0),
                                                         r4=pFail(setbin=self.bin(315918, offset), ret=0),
                                                         r5=pFail(setbin=self.bin(315919, offset), ret=0),
                                                         ))
        qual_prog_fitems.append(t['ecc_status_row7'].get_fitem(r0=pFail(setbin=self.bin(315920, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315921, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(315922, offset), ret=0),
                                                         r4=pFail(setbin=self.bin(315923, offset), ret=0),
                                                         r5=pFail(setbin=self.bin(315924, offset), ret=0),
                                                         ))
        qual_prog_fitems.append(t['ecc_status_row8'].get_fitem(r0=pFail(setbin=self.bin(315925, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315926, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(315927, offset), ret=0),
                                                         r4=pFail(setbin=self.bin(315928, offset), ret=0),
                                                         r5=pFail(setbin=self.bin(315929, offset), ret=0),
                                                         ))
        qual_prog_fitems.append(t['ecc_status_row9'].get_fitem(r0=pFail(setbin=self.bin(315930, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315931, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(315932, offset), ret=0),
                                                         r4=pFail(setbin=self.bin(315933, offset), ret=0),
                                                         r5=pFail(setbin=self.bin(315934, offset), ret=0),
                                                         ))
        qual_prog_fitems.append(t['ecc_status_row10'].get_fitem(r0=pFail(setbin=self.bin(315935, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315936, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(315937, offset), ret=0),
                                                         r4=pFail(setbin=self.bin(315938, offset), ret=0),
                                                         r5=pFail(setbin=self.bin(315939, offset), ret=0),
                                                         ))
        qual_prog_fitems.append(t['perdie_nom_init'].get_fitem(r0=pFail(setbin=self.bin(315850, offset2), ret=0),                                                            
                                                              r1=pPass(ret=1),
                                                              r2=pFail(setbin=self.bin(315851, offset2), ret=0),
                                                              r3=pFail(setbin=self.bin(315852, offset2), ret=0),
                                                              r4=pFail(setbin=self.bin(315853, offset2), ret=0),
                                                              r5=pFail(setbin=self.bin(315854, offset2), ret=0),
                                                              r6=pFail(setbin=self.bin(315855, offset2), ret=0),
                                                              r7=pFail(setbin=self.bin(315856, offset2), ret=0),
                                                              r8=pFail(setbin=self.bin(315857, offset2), ret=0),
                                                              r9=pFail(setbin=self.bin(315858, offset2), ret=0),
                                                              r10=pFail(setbin=self.bin(315859, offset2), ret=0)
                                                              ))
        qual_prog_composite = Flow('QUAL_PROG', *qual_prog_fitems)

        special_row_ir_fitems = []
        special_row_ir_fitems.append(t['repair_ir'].get_fitem(r0=pFail(setbin=self.bin(315102, offset), ret=0),
                                                              r2=pFail(setbin=self.bin(315103, offset), ret=0)))
        #special_row_ir_fitems.append(t['repair_ir_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315122, offset), ret=0),
        #                                                           r2=pFail(setbin=self.bin(315123, offset), ret=0)))
        special_row_ir_composite = Flow('SPECIAL_ROW_IR', *special_row_ir_fitems)
        
        repair_string_gen_fitems = []
        repair_string_gen_fitems.append(t['repair_fle_fsg'].get_fitem(r0=pFail(setbin=self.bin(315008, offset), ret=0),
                                                                      r1=pPass(ret=3),
                                                                      r2=pFail(setbin=self.bin(315009, offset), ret=0),
                                                                      r3=pPass(ret=1),
                                                                      r4=pFail(setbin=self.bin(315010, offset), ret=0),
                                                                      ))
        repair_string_gen_fitems.append(t['repair_fle_fsg_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315095, offset), ret=0),
                                                                           r1=pPass(ret=3),
                                                                           r2=pFail(setbin=self.bin(315096, offset), ret=0),
                                                                           r3=pPass(ret=1),
                                                                           r4=pFail(setbin=self.bin(315097, offset), ret=0),
                                                                      ))
        repair_string_gen_composite = Flow('REPAIR_STRING_GEN', *repair_string_gen_fitems)
        
        special_row_prog_fitems = []
        special_row_prog_fitems.append(t['repair_fuseburn_data'].get_fitem(r0=pFail(setbin=self.bin(315204, offset), ret=0),
                                                                           r2=pFail(setbin=self.bin(315205, offset), ret=0)))
        special_row_prog_fitems.append(t['repair_fuseburn_data_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315206, offset), ret=0),
                                                                                r2=pFail(setbin=self.bin(315207, offset), ret=0)))
        special_row_prog_composite = Flow('SPECIAL_ROW_PROG', *special_row_prog_fitems)
        
        data_rap_fitems = []
        data_rap_fitems.append(t['repair_rap'].get_fitem(r0=pFail(setbin=self.bin(315104, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315105, offset), ret=0)))
        data_rap_fitems.append(t['repair_rap_compfle'].get_fitem(r0=pFail(setbin=self.bin(315106, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(315107, offset), ret=2)))
        data_rap_composite = Flow('DATA_RAP', *data_rap_fitems)
        

        repair_failflow_fitems = []
        repair_failflow_fitems.append(t['sr_rap'].get_fitem(r0=pFail(ret=0),
                                                                     r2=pFail(goto='FUSE_X_FUNC_K_FACTFUSBURNCPUNOM_X_X_X_X_REPAIR_ECCCHECK_FUNC')))
        #repair_failflow_fitems.append(t['sr_rap_cpu1'].get_fitem(r0=pFail(ret=0),
        #                                                                  r2=pFail(goto='FUSE_X_FUNC_K_FACTFUSBURNCPUNOM_X_X_X_X_REPAIR_ECCCHECK_FUNC')))
        repair_failflow_fitems.append(t['repair_ecccheck_func'].get_fitem(r0=pFail(setbin=self.bin(315011, offset), ret=1),
                                                                          r2=pFail(setbin=self.bin(315012, offset), ret=1),
                                                                          r3=pFail(setbin=self.bin(315013, offset), ret=1),
                                                                          r4=pFail(setbin=self.bin(315014, offset), ret=1),
                                                                          r5=pFail(setbin=self.bin(315015, offset), ret=1)
                                                                          ))
        repair_failflow_composite = Flow('REPAIR_FAILFLOW', *repair_failflow_fitems)

        repair_prog_fitems = []
        repair_prog_fitems.append(t['if_18ap_repair'].get_fitem(r0=pFail(setbin=self.bin(315403, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(315404, offset), ret=0)))
        repair_prog_fitems.append(Fitem('SAME', special_row_ir_composite, r0=pFail(ret=0))) 
        repair_prog_fitems.append(Fitem('SAME', repair_string_gen_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto='NEXT'))) 
        repair_prog_fitems.append(Fitem('SAME', special_row_prog_composite, r0=pFail(ret=0)))
        repair_prog_fitems.append(Fitem('SAME', data_rap_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pFail(goto=repair_failflow_composite.name)))
        repair_prog_fitems.append(Fitem('SAME', repair_failflow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))
        repair_prog_composite = Flow('REPAIR_PROG', *repair_prog_fitems)

        
        ecc_row_prog_fitems = []
        ecc_row_prog_fitems.append(t['ecc_fuseburn_data'].get_fitem(r0=pFail(setbin=self.bin(315208, offset), ret=0),
                                                                    r2=pFail(setbin=self.bin(315209, offset), ret=0)))
        ecc_row_prog_fitems.append(t['ecc_fuseburn_data_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315210, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315211, offset), ret=0)))
        ecc_row_prog_composite = Flow('ECC_ROW_PROG', *ecc_row_prog_fitems)

        ecc_rap_fitems = []
        ecc_rap_fitems.append(t['ecc_rap'].get_fitem(r0=pFail(setbin=self.bin(315108, offset), ret=0),
                                                     r2=pFail(setbin=self.bin(315109, offset), ret=2)))
        ecc_rap_fitems.append(t['ecc_rap_flecompare'].get_fitem(r0=pFail(setbin=self.bin(315110, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(315111, offset), ret=2)))
        #ecc_rap_fitems.append(t['ecc_rap_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315196, offset), ret=0),
        #                                                  r2=pFail(setbin=self.bin(315197, offset), ret=2)))
        ecc_rap_fitems.append(t['ecc_rap_flecompare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315198, offset), ret=0),
                                                                     r2=pFail(setbin=self.bin(315199, offset), ret=2)))
        ecc_rap_composite = Flow('ECC_RAP', *ecc_rap_fitems)

        ecc_failflow_fitems = []
        ecc_failflow_fitems.append(t['ecc_check_func'].get_fitem(r0=pFail(setbin=self.bin(315016, offset), ret=1),
                                                                 r1=pPass(ret=1),
                                                                 r2=pFail(setbin=self.bin(315017, offset), ret=1),
                                                                 r3=pFail(setbin=self.bin(315018, offset), ret=1),
                                                                 r4=pFail(setbin=self.bin(315019, offset), ret=1),
                                                                 r5=pFail(setbin=self.bin(315020, offset), ret=1)))
        ecc_failflow_composite = Flow('ECC_FAILFLOW', *ecc_failflow_fitems)

        ecc_prog_fitems = []
        #ecc_prog_fitems.append(Fitem('SAME', ecc_special_row_ir_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_string_gen_composite.name)))
        #ecc_prog_fitems.append(Fitem('SAME', ecc_string_gen_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_row_prog_composite.name)))
        ecc_prog_fitems.append(Fitem('SAME', ecc_row_prog_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_rap_composite.name)))
        ecc_prog_fitems.append(Fitem('SAME', ecc_rap_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pFail(goto=ecc_failflow_composite.name)))
        ecc_prog_fitems.append(Fitem('SAME', ecc_failflow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))
        ecc_prog_composite = Flow('ECC_PROG', *ecc_prog_fitems)

        tap_unlock_fitems = []
        tap_unlock_fitems.append(t['tap_status'].get_fitem(r0=pFail(setbin=self.bin(315900, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(315901, offset), ret=0),
                                                           r3=pFail(setbin=self.bin(315902, offset), ret=0),
                                                           r4=pFail(setbin=self.bin(315903, offset), ret=0),
                                                           r5=pFail(setbin=self.bin(315904, offset), ret=0),
                                                            ))
        tap_unlock_fitems.append(t['unit_info_decode'].get_fitem(r0=pFail(setbin=self.bin(315840, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(315841, offset), ret=0),
                                                                 r3=pPass(goto='FUSE_X_PATCONFIG_K_FACTFUSBURNCPUNOM_X_X_X_X_LEGACY_UNLOCK'),
                                                                 r4=pFail(setbin=self.bin(315842, offset), ret=0),
                                                                 r5=pFail(setbin=self.bin(315843, offset), ret=0),
                                                                 r6=pFail(setbin=self.bin(315844, offset), ret=0),
                                                                 r7=pFail(setbin=self.bin(315845, offset), ret=0),
                                                                 r8=pFail(setbin=self.bin(315846, offset), ret=0),
                                                                 r9=pFail(setbin=self.bin(315847, offset), ret=0),
                                                                 r10=pFail(setbin=self.bin(315848, offset), ret=0),
                                                                 ))
        tap_unlock_fitems.append(t['screen_red_unlock'].get_fitem(r0=pFail(setbin=self.bin(315850, offset), ret=0),
                                                                  r2=pFail(setbin=self.bin(315851, offset), ret=0),
                                                                  r3=pFail(setbin=self.bin(315852, offset), ret=0),
                                                                  r4=pFail(setbin=self.bin(315853, offset), ret=0),
                                                                  r5=pFail(setbin=self.bin(315854, offset), ret=0),
                                                                  r6=pFail(setbin=self.bin(315855, offset), ret=0),
                                                                  r7=pFail(setbin=self.bin(315856, offset), ret=0),
                                                                  r8=pFail(setbin=self.bin(315857, offset), ret=0),
                                                                  r9=pFail(setbin=self.bin(315858, offset), ret=0),
                                                                  r10=pFail(setbin=self.bin(315859, offset), ret=0),
                                                                 ))
        tap_unlock_fitems.append(t['red_unlock'].get_fitem(r0=pFail(setbin=self.bin(315701, offset), ret=0),
                                                           r1=pPass(ret=1)
                                                           ))
        tap_unlock_fitems.append(t['legacy_unlock'].get_fitem(r0=pFail(setbin=self.bin(315702, offset), ret=0)))
        tap_unlock_composite = Flow('TAP_UNLOCK', *tap_unlock_fitems)

        lockout_prog_fitems = []
        lockout_prog_fitems.append(t['lockbit_fsg'].get_fitem(r0=pFail(setbin=self.bin(315021, offset), ret=0)))
        lockout_prog_fitems.append(t['lockbit_fsg_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315094, offset), ret=0)))
        lockout_prog_fitems.append(t['lockbit_burn'].get_fitem(r0=pFail(setbin=self.bin(315212, offset), ret=0),
                                                               r2=pFail(setbin=self.bin(315213, offset), ret=0)))
        lockout_prog_fitems.append(t['lockbit_burn_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315214, offset), ret=0),
                                                               r2=pFail(setbin=self.bin(315215, offset), ret=0)))
        lockout_prog_fitems.append(Fitem('SAME', tap_unlock_composite, r0=pFail(ret=0)))
        lockout_prog_fitems.append(t['lockbit_rap'].get_fitem(r0=pFail(setbin=self.bin(315112, offset), ret=0),
                                                              r2=pPass(goto='NEXT')
                                                                ))
        lockout_prog_fitems.append(t['lockbit_rap_flecompare'].get_fitem(r0=pFail(setbin=self.bin(315113, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315114, offset), ret=2)
                                                                         ))
        #lockout_prog_fitems.append(t['lockbit_rap_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315195, offset), ret=0),
        #                                                      r2=pPass(goto='NEXT')
        #                                                        ))
        lockout_prog_fitems.append(t['lockbit_rap_flecompare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315193, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315194, offset), ret=2)
                                                                         ))
        lockout_prog_composite = Flow('LOCKOUT_PROG', *lockout_prog_fitems)

        ecc_set_fitems = []
        ecc_set_fitems.append(t['ecc_status'].get_fitem(r0=pFail(setbin=self.bin(315300, offset), ret=0),
                                                        r1=pPass(ret=1),
                                                        r2=pFail(setbin=self.bin(315301, offset), goto='NEXT'),
                                                        r3=pFail(setbin=self.bin(315302, offset), ret=0),
                                                        r4=pFail(setbin=self.bin(315303, offset), ret=0)
                                                        ))
        ecc_set_fitems.append(t['ecc_preamble_func'].get_fitem(r0=pFail(setbin=self.bin(315022, offset), ret=2),
                                                               r1=pPass(ret=2),
                                                               r2=pFail(setbin=self.bin(315023, offset), ret=2),
                                                               r3=pFail(setbin=self.bin(315024, offset), ret=2),
                                                               r4=pFail(setbin=self.bin(315025, offset), ret=2),
                                                               r5=pFail(setbin=self.bin(315026, offset), ret=2),
                                                               ))
        ecc_set_composite = Flow('ECC_SET', *ecc_set_fitems)


        efuse_read_fitems = []
        efuse_read_fitems.append(t['efuse_read'].get_fitem(r0=pFail(setbin=self.bin(315115, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(315116, offset), ret=2),
                                                           r3=pFail(setbin=self.bin(315117, offset), ret=2),
                                                           ))
        #efuse_read_fitems.append(t['efuse_read_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315190, offset), ret=0),
        #                                                   r2=pFail(setbin=self.bin(315191, offset), ret=2),
        #                                                   r3=pFail(setbin=self.bin(315192, offset), ret=2),
        #                                                   ))
        efuse_read_fitems.append(t['fuse_efuse_compare'].get_fitem(r0=pFail(setbin=self.bin(315120, offset), ret=0),
                                                                   r2=pFail(setbin=self.bin(315121, offset), ret=0),
                                                                   r3=pFail(setbin=self.bin(315122, offset), ret=0),
                                                                   r4=pFail(setbin=self.bin(315123, offset), ret=0),
                                                                   r5=pFail(setbin=self.bin(315124, offset), ret=0),
                                                                   r6=pFail(setbin=self.bin(315125, offset), ret=0),
                                                                   r7=pFail(setbin=self.bin(315126, offset), ret=0),
                                                                   r8=pFail(setbin=self.bin(315127, offset), ret=0),
                                                                   r9=pFail(setbin=self.bin(315128, offset), ret=0),
                                                                   r10=pFail(setbin=self.bin(315129, offset), ret=0),
                                                                  ))
        efuse_read_fitems.append(t['dff_ult_efuse_compare'].get_fitem(r0=pFail(setbin=self.bin(315130, offset), ret=0),
                                                                      r2=pFail(setbin=self.bin(315131, offset), ret=0)))
        efuse_read_fitems.append(t['dff_ult_efuse_compare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315132, offset), ret=0),
                                                                      r2=pFail(setbin=self.bin(315133, offset), ret=0)))
        efuse_read_composite = Flow('EFUSE_READ', *efuse_read_fitems)

        retest_store_fitems = []
        retest_store_fitems.append(Fitem('SAME', efuse_read_composite, r0=pFail(ret=0),
                                                                       r2=pFail(ret=2)
                                                                       ))
        retest_store_fitems.append(t['security_key_hashgen'].get_fitem(r0=pFail(setbin=self.bin(315027, offset), ret=2),
                                                                       r2=pFail(setbin=self.bin(315028, offset), ret=2)
                                                                       ))
        retest_store_fitems.append(t['security_key_hashgen_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315088, offset), ret=2),
                                                                            r2=pFail(setbin=self.bin(315089, offset), ret=2)
                                                                       ))
        retest_store_fitems.append(t['post_process_hostkey'].get_fitem(r0=pFail(setbin=self.bin(315860, offset), ret=0),
                                                                       r2=pFail(setbin=self.bin(315861, offset), ret=0),
                                                                       r3=pFail(setbin=self.bin(315862, offset), ret=0),
                                                                       r4=pFail(setbin=self.bin(315863, offset), ret=0),
                                                                       r5=pFail(setbin=self.bin(315864, offset), ret=0),
                                                                       r6=pFail(setbin=self.bin(315865, offset), ret=0),
                                                                       r7=pFail(setbin=self.bin(315866, offset), ret=0),
                                                                       r8=pFail(setbin=self.bin(315867, offset), ret=0),
                                                                       r9=pFail(setbin=self.bin(315868, offset), ret=0),
                                                                       r10=pFail(setbin=self.bin(315869, offset), ret=0),
                                                                       ))
        retest_store_fitems.append(t['apply_gen_hash'].get_fitem(r0=pFail(setbin=self.bin(315703, offset), ret=2)))
        retest_store_fitems.append(t['read_hash_status'].get_fitem(r0=pFail(setbin=self.bin(315029, offset), ret=0),
                                                                   r2=pFail(setbin=self.bin(315030, offset), ret=0),
                                                                   r3=pFail(setbin=self.bin(315031, offset), ret=0),
                                                                   r4=pFail(setbin=self.bin(315032, offset), ret=0),
                                                                   r5=pFail(setbin=self.bin(315033, offset), ret=0),
                                                                       ))
        retest_store_composite = Flow('RETEST_STORE', *retest_store_fitems)

        feedback_fitems = []
        feedback_fitems.append(t['security_set'].get_fitem(r0=pFail(setbin=self.bin(315134, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(315135, offset), ret=0)))
        feedback_fitems.append(t['post_fuse_confirm'].get_fitem(r0=pFail(setbin=self.bin(315406, offset), ret=0)))
        feedback_composite = Flow('FEEDBACK', *feedback_fitems)

        feedback_failflow_fitems = []
        feedback_failflow_fitems.append(t['security_set_ff'].get_fitem(r0=pFail(setbin=self.bin(315136, offset), ret=0),
                                                                       r2=pFail(setbin=self.bin(315137, offset), ret=0)))
        feedback_failflow_composite = Flow('FEEDBACK_FAIL', *feedback_failflow_fitems)


        fact_fitems = []
        fact_fitems.append(t['s52c_check'].get_fitem(r0=pFail(setbin=self.bin(315400, offset),ret=0), r2=pPass(ret=1)))
        fact_fitems.append(Fitem('SAME', burn_setup_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto=data_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', data_prog_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto=qual_prog_composite.name), r4=pPass(goto=repair_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', qual_prog_composite, r0=pFail(ret=0), r1=pPass(goto=lockout_prog_composite.name), r2=pPass(goto=ecc_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', ecc_prog_composite, r0=pFail(ret=0), r1=pPass(goto=lockout_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', repair_prog_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', lockout_prog_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_set_composite.name), r2=pFail(goto=feedback_failflow_composite.name)))
        fact_fitems.append(Fitem('SAME', ecc_set_composite, r0=pFail(ret=0), r1=pPass(goto=retest_store_composite.name), r2=pFail(goto=feedback_failflow_composite.name)))
        fact_fitems.append(Fitem('SAME', retest_store_composite, r0=pFail(ret=0), r1=pPass(goto=feedback_composite.name), r2=pFail(goto=feedback_failflow_composite.name)))
        fact_fitems.append(Fitem('SAME', feedback_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        fact_fitems.append(Fitem('SAME', feedback_failflow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))

        Flow(flow_name,*fact_fitems)

    def get_fact52c_flow(self, flow_name, module_name='FACTFUSBUILDCPUNOM', bin_offset=100, bin_offset2=150, composite_postfix=None, test_instance_postfix=None):
        t = dict()

        offset=bin_offset
        offset2=bin_offset2
        dparams = {

            'module_name': module_name,
            'test_instance_postfix': test_instance_postfix,
            #'is_edc': is_edc,
            #'LevelsTc': self.LevelsTc,
            'TimingsTc': self.TimingsTc,
        }


        # tests for FACT root
        t['s52c_check'] = AuxiliaryTC_TestBuilder(name='s52c_check', DataType='String', Expression='[E.BOMGROUP]==\'CLASS_NVL_S52C\'', ResultPort='[R]?1:2', Storage='SharedStorage', **dparams)
    
        # tests for FACT / BURN_SETUP root
        t['all_in_one_fork_cpu'] = ScreenTC_TestBuilder(name='all_in_one_fork_cpu', ScreenTestSet='AllInOneCheck', **dparams)
        t['perdie_state_init'] = ScreenTC_TestBuilder(name='perdie_state_init', ScreenTestSet='PerDieValuesInit_DUT', **dparams)
        #t['set_margins'] = PrimePatConfigTestMethod_TestBuilder(name='set_margins', SetPoint='ROOM_MARGIN', BypassPort=1, **dparams)
    
        # tests for FACT / BURN_SETUP / RETEST root
        t['get_fuse_string_status'] = FleGetDieStatusByDies_TestBuilder(name='get_fuse_string_status', FuseStateUservar='Which_Socket.FuseState', **dparams)
        #t['get_fuse_string_status_cpu1'] = FleGetDieStatus_TestBuilder(name='get_fuse_string_status_cpu1', FuseStateUservar='Which_Socket.FuseState', Register='CPU1', BypassPort=1, **dparams)
        t['check_fused_sspec'] = FleCheckFusedSspecFusing_TestBuilder(name='check_fused_sspec', Register='CPU0', **dparams)
    
        # test for FACT/ DATA_PROG
        t['hvm_fsg'] = FleGeneratePerDieFuseString_TestBuilder(name='hvm_fsg', Register='CPU0', BypassPort=1, **dparams)
        t['hvm_fsg_cpu1'] = FleGeneratePerDieFuseString_TestBuilder(name='hvm_fsg_cpu1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), **dparams)
        t['hip_hash'] = FleUpdateSpecialAlgInFuseString_TestBuilder(name='hip_hash', Register='CPU0', **dparams)
        t['hip_hash_cpu1'] = FleUpdateSpecialAlgInFuseString_TestBuilder(name='hip_hash_cpu1', Register='CPU1', AlgorithmName="CPU1_HIP_HASH", BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'),**dparams)
        t['validation_fork'] = ScreenTC_TestBuilder(name='validation_fork', ScreenTestSet='ValForkTest', **dparams)
        t['check_facilityid_tpfuseenable'] = ScreenTC_TestBuilder(name='check_facilityid_tpfuseenable', ScreenTestSet='CheckFacilityID_TP_FUSE_Enabled', BypassPort=Spec('__shared__::TpRule.If_FacilityID_GDL(-1,1)'), **dparams)
        #parallel setup
        #t['hvm_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn', ConfigName='FuseBurnFlow', BypassPort=-1, MaskNames='fle_str', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_hvm_data_x","IPC::cpu_fuse_write_hvm_data_mm")'), SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0,FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1","FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0")'),**dparams)
        #serial setup
        t['hvm_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn', ConfigName='FuseBurnFlow', BypassPort=-1, MaskNames='fle_str', Patlist="IPC::cpu_fuse_write_hvm_data_mm", SharedStorageKeyToRead='FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0',**dparams)
        t['hvm_burn_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn_cpu1', ConfigName='FuseBurnFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), RegisterNames='CPU1', MaskNames='fle_str', Patlist='IPC::cpu_fuse_write_hvm_data_mm', SharedStorageKeyToRead='FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1', **dparams)
        t['hvm_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='hvm_rap', is_edc=True, ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'),**dparams)
        t['hvm_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='hvm_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', ExpectedPort='2', ExceptionPort='1', FuseReadGlobal='FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1', FuseGroupToDatalog='', **dparams)
        t['hvm_flecompare'] = FleCompareFuseStringByDies_TestBuilder(name='hvm_flecompare', Category='MAIN_ARRAY_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        t['hvm_flecompare_cpu1'] = FleCompareFuseString_TestBuilder(name='hvm_flecompare_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1', **dparams)
   
        t['hvm_burn_rec'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn_rec', ConfigName='FuseBurnFlow', BypassPort=-1, MaskNames='fle_str', Patlist='IPC::cpu_fuse_write_hvm_data_mm', SharedStorageKeyToRead='FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0',**dparams)
        t['hvm_burn_cpu1_rec'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='hvm_burn_cpu1_rec', ConfigName='FuseBurnFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), RegisterNames='CPU1', MaskNames='fle_str', Patlist='IPC::cpu_fuse_write_hvm_data_mm', SharedStorageKeyToRead='FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1', **dparams)
        t['hvm_rap_rec'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='hvm_rap_rec', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'),**dparams)
        t['hvm_flecompare_rec'] = FleCompareFuseStringByDies_TestBuilder(name='hvm_flecompare_rec', Category='MAIN_ARRAY_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        
        #tests for FACT / QUAL_PROG
        t['qual_prog'] = AuxiliaryTC_TestBuilder(name='qual_prog', DataType='String', Expression='[FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.QualProgBypass]==\'1\'', ResultPort='[R]?2:1', Storage='UserVar', **dparams)
        
        #tests for FACT / ECC_PROG / ECC_SPECIAL_ROW_IR
        t['ecc_ir'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_ir', ConfigName='FusingFlowSpecialIR', BypassPort=-1, RegisterNames=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), PassingMaskName='virgin_sprow_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
        t['ecc_ir_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_ir_cpu1', ConfigName='FusingFlowSpecialIR_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), RegisterName='SPROWD1', PassingMaskName='virgin_sprow_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
   
        #tests for FACT / ECC_PROG / ECC_STRING_GEN 
        t['ecc_fle_fsg'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg', FuseChassis='CH4', BypassPort=-1, Process='10nm', Register='CPU0', **dparams)
        t['ecc_fle_fsg_cpu1'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg_cpu1', FuseChassis='CH4', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), Process='10nm', Register='CPU1', **dparams)
    
        #tests for FACT / ECC_PROG / ECC_ROW_PROG
        #Parallel setup
        #t['ecc_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data', ConfigName='FuseECCFlow', BypassPort=-1, MaskNames='data_for_ecc_mask', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_hvm_ecc_x","IPC::cpu_fuse_write_hvm_ecc_mm")'), SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #Serial setup
        t['ecc_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data', ConfigName='FuseECCFlow', BypassPort=-1, MaskNames='data_for_ecc_mask', Patlist="IPC::cpu_fuse_write_hvm_ecc_mm", SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0", **dparams)
        t['ecc_fuseburn_data_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data_cpu1', ConfigName='FuseECCFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), MaskNames='data_for_ecc_mask', Patlist='IPC::cpu_fuse_write_hvm_ecc_mm', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1",**dparams)
    
        #tests for FACT / ECC_PROG / ECC_RAP
        t['ecc_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0")'), **dparams)
        #t['ecc_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='ecc_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', ExpectedPort='2', ExceptionPort='1', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', FuseReadGlobal="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1", **dparams)
        t['ecc_rap_flecompare'] = FleCompareFuseStringByDies_TestBuilder(name='ecc_rap_flecompare', Category='MAIN_ARRAY_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU0")'), **dparams)
        t['ecc_rap_flecompare_cpu1'] = FleCompareFuseString_TestBuilder(name='ecc_rap_flecompare_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStrAfterECC_CPU1', **dparams)
   
        #tests for FACT / ECC_PROG / ECC_FAILFLOW
        t['ecc_check_func'] = PrimeFunctionalTestMethod_TestBuilder(name='ecc_check_func', BypassPort=1, Patlist='IPC::cpu_fuse_read_hvm_ecc_status', **dparams)

        #tests for FACT / LOCKOUT_PROG / TAP_UNLOCK
        t['tap_status'] = PrimeCtvDecoderTestMethod_TestBuilder(name='tap_status', BypassPort=-1, Patlist='IPC::cpu_dfxagg_read_hvm_status_csr', **dparams)
        t['unit_info_decode'] = ScreenTC_TestBuilder(name='unit_info_decode', ScreenTestsFile=Spec('__shared__::TpRule.If_MICP(GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C2X.screen.json",GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C1X.screen.json")'), ScreenTestSet='STATUS_SET_PIC8_PrimeCtvDecoderTestMethod', **dparams)
        t['screen_red_unlock'] = ScreenTC_TestBuilder(name='red_unlock', ScreenTestsFile=Spec('__shared__::TpRule.If_MICP(GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C2X.screen.json",GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C1X.screen.json")'), ScreenTestSet='RED_KEY_split_by_32bits_MsbToLsb', **dparams)
        t['red_unlock'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock',  SetPoint='RDULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        t['legacy_unlock'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock',  SetPoint='LGULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
    
        #tests for FACT / LOCKOUT_PROG
        t['lockbit_fsg'] = FleGenerateLockoutBitsFuseStringByDies_TestBuilder(name='lockbit_fsg', **dparams)
        t['lockbit_fsg_cpu1'] = FleGenerateLockoutBitsFuseString_TestBuilder(name='lockbit_fsg_cpu1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), **dparams)
        #Parallel setup
        #t['lockbit_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='lockbit_burn', ConfigName='FuseBurnLockoutFlow', BypassPort=-1, MaskNames='fle_lockout_str', Patlist='IPC::cpu_fuse_write_hvm_lockout', SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #Serial setup
        t['lockbit_burn'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='lockbit_burn', ConfigName='FuseBurnLockoutFlow', BypassPort=-1, MaskNames='fle_lockout_str', Patlist='IPC::cpu_fuse_write_hvm_lockout', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0", **dparams)
        t['lockbit_burn_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='lockbit_burn_cpu1', ConfigName='FuseBurnLockoutFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), MaskNames='fle_lockout_str', Patlist='IPC::cpu_fuse_write_hvm_lockout', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1", **dparams)
        t['lockbit_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='lockbit_rap', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0")'), **dparams)
        #t['lockbit_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='lockbit_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', ExpectedPort='2', ExceptionPort='1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', FuseReadGlobal="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1", **dparams)
        t['lockbit_rap_flecompare'] = FleCompareFuseStringByDies_TestBuilder(name='lockbit_rap_flecompare', Category='LOCKOUTBIT_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0")'), **dparams)
        t['lockbit_rap_flecompare_cpu1'] = FleCompareFuseString_TestBuilder(name='lockbit_rap_flecompare_cpu1', Category='LOCKOUTBIT_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1', **dparams)
   
        #tests for FACT / ECC_SET
        #t['ecc_set_arr0'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_set_arr0', ConfigName='FuseECCFlow', BypassPort=1, MaskNames='ECC_Set_Arr0_mask', Patlist='IPC::cpu_fuse_write_special_eccset', **dparams)
        #t['ecc_set_arr0_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_set_arr0_cpu1', ConfigName='FuseECCFlow_CPU1', BypassPort=1, RegisterNames='SPROWD1', MaskNames='ECC_Set_Arr0_mask', Patlist='IPC::cpu_fuse_write_special_eccset', **dparams)
        #t['ecc_rap_arr0'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_arr0', ConfigName='FusingFlowECCRead', BypassPort=1, PassingMaskName='ECC_ARR0_check_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
        #t['ecc_rap_arr0_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_arr0_cpu1', ConfigName='FusingFlowECCRead_CPU1', BypassPort=1, RegisterName='SPROWD1', PassingMaskName='ECC_ARR0_check_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', **dparams)
        t['ecc_status'] = PrimeCtvDecoderTestMethod_TestBuilder(name='ecc_status', BypassPort=-1, ConfigurationFile=Spec('FUS_FUSEBURN_CXX_Rules.FUSEBURN_CfgFile("./InputFiles/FUSEBURN_C2X_ECC_Check.csv","./InputFiles/FUSEBURN_C2X_TSMC_ECC_Check.csv","./InputFiles/FUSEBURN_C1X_TSMC_ECC_Check.csv","./InputFiles/FUSEBURN_C1X_ECC_Check.csv")'), Patlist='IPC::cpu_fuse_read_hvm_ecc_statictics', **dparams)
        t['ecc_preamble_func'] = PrimeFunctionalTestMethod_TestBuilder(name='ecc_preamble_func', isEDC=True, BypassPort=-1, Patlist='IPC::cpu_fuse_read_hvm_ecc_statictics', **dparams)

        #tests for FACT / RETEST_STORE / EFUSE_READ
        t['efuse_read'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuse_read', ConfigName='CXX_EFUSEReadFlow', BypassPort=-1, RegisterName=Spec('__shared__::TpRule.If_MICP("CPU0_EFUSE,CPU1_EFUSE","CPU0_EFUSE")'), PassingMaskName='PMaskName_All_ss', FailingMaskName='FMaskName_All_00,FMaskName_All_11,FMaskName_All_01,FMaskName_All_10', Patlist='IPC::cpu_dfxagg_read_hvm_efuse', FuseGroupToDatalog='EFUSE_ULT', PrintUltDataPerDieIdToItuff='DISABLED', **dparams)
        #t['efuse_read_cpu1'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuse_read_cpu1', ConfigName='EFUSEReadFlow_cpu1', BypassPort=1, RegisterName='CPU1_EFUSE', PassingMaskName='PMaskName_All_ss', FailingMaskName='FMaskName_All_00,FMaskName_All_11,FMaskName_All_01,FMaskName_All_10', Patlist='IPC::cpu_dfxagg_read_hvm_efuse', FuseGroupToDatalog='EFUSE_ULT', DieIdNames=Spec('__shared__::DFFVars.DIEID_CPU1'), **dparams)
        t['fuse_efuse_compare'] = ScreenTC_TestBuilder(name='fuse_efuse_compare', ScreenTestSet='EFUSE_CHECK', **dparams)
        t['dff_ult_efuse_compare'] = SFMDffEfuseCheck_TestBuilder(name='dff_ult_efuse_compare', DieIdName=Spec('__shared__::DFFVars.DIEID_CPU'), **dparams)
        t['dff_ult_efuse_compare_cpu1'] = SFMDffEfuseCheck_TestBuilder(name='dff_ult_efuse_compare_cpu1', DieIdName=Spec('__shared__::DFFVars.DIEID_CPU1'), BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), **dparams)
    
        #tests for FACT / RETEST_STORE
        t['security_key_hashgen'] = FleComputeFuseHashSignatureByDies_TestBuilder(name='security_key_hashgen', FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU0")'), **dparams)
        t['security_key_hashgen_cpu1'] = FleComputeFuseHashSignature_TestBuilder(name='security_key_hashgen_cpu1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadLockBitsString_CPU1', **dparams)
        t['post_process_hostkey'] = ScreenTC_TestBuilder(name='post_process_hostkey_for_hash_setup', ScreenTestSet='HASH_SETUP_CPU', **dparams)
        t['apply_gen_hash'] = PrimePatConfigTestMethod_TestBuilder(name='apply_gen_hash', SetPoint='SET_HASHSIG_CPU', BypassPort=-1, **dparams)
        t['read_hash_status'] = PrimeFunctionalTestMethod_TestBuilder(name='read_hash_status', BypassPort=-1, Patlist='IPC::cpu_fuse_hvm_hash', **dparams)

        #test for FACT / FEEDBACK
        t['security_set'] = FleISeedSetUnitKeys_TestBuilder(name='security_set', **dparams)
        t['post_fuse_confirm'] = RunCallback_TestBuilder(name='post_fuse_confirm', BypassPort=-1, Parameters='--token G.U.S.CLASSFUSED_CPU0 --value 1', **dparams)
        #t['extract_partid_feedback'] = FleISeedCapturePartId_TestBuilder(name='extract_partid_feedback', CtvCapturePins=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("IPC::CPU_TDO","IPC::CPU_TDO, IPC::CPU1_TDO")'), BypassPort=Spec('__shared__::TpRule.If_MICP(1,-1)'), **dparams)

        #test for FACT / FEEDBACK_FAIL
        t['security_set_ff'] = FleISeedSetUnitKeys_TestBuilder(name='security_set_ff', **dparams)
        #t['extract_partid_feedback_failflow'] = FleISeedCapturePartId_TestBuilder(name='extract_partid_feedback_failflow', CtvCapturePins=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("IPC::CPU_TDO","IPC::CPU_TDO, IPC::CPU1_TDO")'), BypassPort=Spec('__shared__::TpRule.If_MICP(1,-1)'), **dparams)

        #test for FACT/ REPAIR_PROG / SPECIAL_ROW_IR
        t['repair_ir'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='repair_ir', ConfigName='FusingFlowSpecialIR', BypassPort=-1, RegisterName=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), PassingMaskName='virgin_sprow_mask', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0")'), **dparams)
        #t['repair_ir_cpu1'] = SFMFuseReadMask_TestBuilder(name='repair_ir_cpu1', ConfigName='FusingFlowSpecialIR_CPU1', BypassPort=1, RegisterName='SPROWD1', FuseMaskName='virgin_sprow_mask', PassingMaskName='virgin_sprow_mask', ExpectedPort='1', ExceptionPort='2', Patlist='IPC::cpu_fuse_read_special_x', FuseGroupToDatalog='', FuseReadGlobal='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1', **dparams)

        #test for FACT/ REPAIR_PROG / REPAIR_STRING_GEN
        t['repair_fle_fsg'] = FleGenerateFuseRepairString_TestBuilder(name='repair_fle_fsg', FuseChassis='CH4', BypassPort=-1, Process='7nm', Register='CPU0', FuseReadTokenName = "FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0", **dparams)
        t['repair_fle_fsg_cpu1'] = FleGenerateFuseRepairString_TestBuilder(name='repair_fle_fsg_cpu1', FuseChassis='CH4', _comment=["NOCLEAN"], BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), Process='7nm', Register='CPU1', FuseReadTokenName = "FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1",**dparams)
    
        #test for FACT/ REPAIR_PROG / SPECIAL_ROW_PROG
        #Parallel setup
        #t['repair_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_data', ConfigName='FuseRepairDataFlow', BypassPort=-1, RegisterNames=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), MaskNames='sprow_data_mask', Patlist=Spec('__shared__::TpRule.If_MICP("IPC::cpu_fuse_write_special_data_x","IPC::cpu_fuse_write_special_data_mm")'), SharedStorageKeyToRead=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0")'), **dparams)
        #Serial setup
        t['repair_fuseburn_data'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_data', ConfigName='FuseRepairDataFlow', BypassPort=Spec('__shared__::TpRule.If_18AP(-1,1)'), RegisterNames="SPROWD0", MaskNames='sprow_data_mask', Patlist="IPC::cpu_fuse_write_special_data_mm", SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD0", **dparams)
        t['repair_fuseburn_data_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_data_cpu1', ConfigName='FuseRepairDataFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), RegisterNames='SPROWD1', MaskNames='sprow_data_mask', Patlist='IPC::cpu_fuse_write_special_data_mm', SharedStorageKeyToRead="FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadSPROWD1", **dparams)
        #t['repair_fuseburn_cfg'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_cfg', ConfigName='FuseRepairCfgFlow', BypassPort=Spec('__shared__::TpRule.If_MICP(1,-1)'), RegisterNames=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("SPROWD0","SPROWD0,SPROWD1")'), MaskNames='sprow_cfg_mask', Patlist='IPC::cpu_fuse_write_special_data_x', **dparams)
        #t['repair_fuseburn_cfg_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='repair_fuseburn_cfg_cpu1', ConfigName='FuseRepairCfgFlow_CPU1', BypassPort=1, RegisterNames='SPROWD1', MaskNames='sprow_cfg_mask', Patlist='IPC::cpu_fuse_write_special_data_x', **dparams)
    
        #test for FACT/ REPAIR_PROG / DATA_RAP
        t['repair_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='repair_rap', ConfigName='FusingFlowDataRAP', BypassPort=-1, FailingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #t['repair_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='repair_rap_cpu1', ConfigName='FusingFlowDataRAP_CPU1', BypassPort=1, RegisterName='CPU1', FuseMaskName='mask_open_socket', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', ExpectedPort='2', ExceptionPort='1', FuseGroupToDatalog='', FuseReadGlobal='FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1', **dparams)
        t['repair_rap_compfle'] = FleCompareFuseStringByDies_TestBuilder(name='repair_rap_compfle', Category='MAIN_ARRAY_CAT', BypassPort=-1, FuseReadTokenNames=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0,FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU1","FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutputStr_CPU0")'), **dparams)
        #t['repair_rap_compfle_cpu1'] = FleCompareFuseString_TestBuilder(name='repair_rap_compfle_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutpuStr', **dparams)
   
        #test for FACT/ REPAIR_PROG / ECC_STRING_GEN_REPAIRED
        #t['ecc_fle_fsg_repaired'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg_repaired', FuseChassis='CH4', BypassPort=-1, Process='7nm', Register='CPU0', **dparams)
        #t['ecc_fle_fsg_repaired_cpu1'] = FleGenerateFuseRepairString_TestBuilder(name='ecc_fle_fsg_repaired_cpu1', FuseChassis='CH4', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Process='7nm', Register='CPU1', **dparams)
    
        #test for FACT/ REPAIR_PROG / ECC_SPECIAL_ROW_PROG_REPAIRED
        #t['ecc_fuseburn_data_repaired'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data_repaired', ConfigName='FuseRepairDataFlow', BypassPort=-1, RegisterNames=Spec('__shared__::TpRule.If_CLASS_NVL_S28C("SPROWD0","SPROWD0,SPROWD1")'), MaskNames='sprow_data_mask', Patlist='cpu_fuse_write_special_data_x', **dparams)
        #t['ecc_fuseburn_data_repaired_cpu1'] = PrimeFuseBurnMaskTestMethod_TestBuilder(name='ecc_fuseburn_data_repaired_cpu1', ConfigName='FuseRepairDataFlow_CPU1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), RegisterNames='SPROWD1', MaskNames='sprow_data_mask', Patlist='cpu_fuse_write_special_data_x', **dparams)
   
        #test for FACT/ REPAIR_PROG / ECC_RAP_REPAIRED
        #t['ecc_rap_repaired'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_repaired', ConfigName='FuseFlowDataRAP', BypassPort=-1, PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', **dparams)
        #t['ecc_rap_repaired_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ecc_rap_repaired_cpu1', ConfigName='FuseFlowDataRAP', BypassPort=1, RegisterName='CPU1', PassingMaskName='mask_open_socket', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='', **dparams)
        #t['ecc_rap_compfle_repaired'] = FleCompareFuseString_TestBuilder(name='ecc_rap_compfle_repaired', Category='MAIN_ARRAY_CAT', BypassPort=-1, Register='CPU0', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutpuStr', **dparams)
        #t['ecc_rap_compfle_repaired_cpu1'] = FleCompareFuseString_TestBuilder(name='ecc_rap_compfle_repaired_cpu1', Category='MAIN_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadOutpuStr', **dparams)
   
        #test for FACT/ REPAIR_PROG / REPAIR_FAILFLOW
        t['sr_rap'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='sr_rap', ConfigName='FusingFlowSpecialRAP', BypassPort=1, RegisterName=Spec('__shared__::TpRule.If_MICP("SPROWD0,SPROWD1","SPROWD0")'), PassingMaskName='mask_REPAIR_ARR0_check', Patlist='cpu_fuse_read_special_x', FuseGroupToDatalog='', SharedStorageKeyToStore=Spec('__shared__::TpRule.If_MICP("FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU0,FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU1","FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU0")'), **dparams)
        #t['sr_rap_cpu1'] = SFMFuseReadMask_TestBuilder(name='sr_rap_cpu1', ConfigName='FusingFlowSpecialRAP_CPU1', BypassPort=1, RegisterName='SPROWD1', FuseMaskName='mask_REPAIR_ARR0_check', Patlist='cpu_fuse_read_special_x', ExpectedPort='1', ExceptionPort='2', FuseGroupToDatalog='', FuseReadGlobal='FUS_FUSEBURN_CXX:FUS_FUSEBURN_CXX.FuseReadRepair_CPU1', **dparams)
        #t['srdata_compfle'] = FleCompareFuseString_TestBuilder(name='repairff_srdata_compfle', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=-1, Register='SPROWD0', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        #t['srdata_compfle_cpu1'] = FleCompareFuseString_TestBuilder(name='repairff_srdata_compfle_cpu1', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Register='SPROWD1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        #t['srcfg_compfle'] = FleCompareFuseString_TestBuilder(name='repairff_srcfg_compfle', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=-1, Register='SPROWD0', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        #t['srcfg_compfle_cpu1'] = FleCompareFuseString_TestBuilder(name='repairff_srcfg_compfle_cpu1', Category='REPAIR_CONFIG_ARRAY_CAT', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), Register='SPROWD1', FuseReadTokenName='FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX.FuseReadRepair', **dparams)
        t['repair_ecccheck_func'] = PrimeFunctionalTestMethod_TestBuilder(name='repair_ecccheck_func', _comment=["NOCLEAN"], BypassPort=1, Patlist='IPC::cpu_fuse_read_hvm_ecc_status', **dparams)

   




        ##Flow Setup
        burn_setup_retest_fitems = []
        burn_setup_retest_fitems.append(t['get_fuse_string_status'].get_fitem(r0=pFail(setbin=self.bin(315600, offset), ret=0),
                                                                              r1=pPass(ret=3),
                                                                              r2=pFail(setbin=self.bin(315601, offset), ret=0),
                                                                              r3=pPass(goto='NEXT'),
                                                                              r4=pFail(setbin=self.bin(315602, offset), ret=0),
                                                                              r5=pFail(setbin=self.bin(315603, offset), ret=0)
                                                                              ))
        #burn_setup_retest_fitems.append(t['get_fuse_string_status_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315697, offset), ret=0),
        #                                                                      r1=pPass(ret=3),
        #                                                                      r2=pFail(setbin=self.bin(315698, offset), ret=0),
        #                                                                      r3=pPass(goto='NEXT'),
        #                                                                      r4=pFail(setbin=self.bin(315699, offset), ret=0)
        #                                                                      ))
        burn_setup_retest_fitems.append(t['check_fused_sspec'].get_fitem(r0=pFail(setbin=self.bin(315500, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315501, offset), ret=0)))
        burn_setup_retest_composite = Flow('RETEST_S52C', *burn_setup_retest_fitems)

        burn_setup_fitems = []
        burn_setup_fitems.append(t['all_in_one_fork_cpu'].get_fitem(r0=pFail(setbin=self.bin(315800, offset2), ret=0),
                                                                    r1=pPass(ret=1),
                                                                    r2=pFail(setbin=self.bin(315801, offset), ret=0),
                                                                    r3=pPass(goto='NEXT'),
                                                                    r4=pFail(setbin=self.bin(315802, offset), ret=0),
                                                                    r5=pFail(setbin=self.bin(315803, offset), ret=0),
                                                                    r6=pFail(setbin=self.bin(315804, offset), ret=0),
                                                                    r7=pFail(setbin=self.bin(315805, offset), ret=0),
                                                                    r8=pFail(setbin=self.bin(315806, offset), ret=0),
                                                                    r9=pFail(setbin=self.bin(315807, offset), ret=0),
                                                                    r10=pFail(setbin=self.bin(315808, offset), ret=0)
                                                                    ))
        burn_setup_fitems.append(Fitem('SAME', burn_setup_retest_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto="NEXT")))
        burn_setup_fitems.append(t['perdie_state_init'].get_fitem(r0=pFail(setbin=self.bin(315810, offset), ret=0),
                                                                  r1=pPass(ret=3),
                                                                  r2=pFail(setbin=self.bin(315811, offset), ret=0),
                                                                  r3=pFail(setbin=self.bin(315812, offset), ret=0),
                                                                  r4=pFail(setbin=self.bin(315813, offset), ret=0),
                                                                  r5=pFail(setbin=self.bin(315814, offset), ret=0),
                                                                  r6=pFail(setbin=self.bin(315815, offset), ret=0),
                                                                  r7=pFail(setbin=self.bin(315816, offset), ret=0),
                                                                  r8=pFail(setbin=self.bin(315817, offset), ret=0),
                                                                  r9=pFail(setbin=self.bin(315818, offset), ret=0),
                                                                  r10=pFail(setbin=self.bin(315819, offset), ret=0)
                                                                  ))
        burn_setup_composite = Flow('BURN_SETUP_S52C', *burn_setup_fitems)

        data_prog_fitems = []
        data_prog_fitems.append(t['hvm_fsg'].get_fitem(r0=pFail(setbin=self.bin(315006, offset),ret=0), r2=pFail(setbin=self.bin(315007, offset), ret=0)))
        data_prog_fitems.append(t['hvm_fsg_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315098, offset), ret=0), r2=pFail(setbin=self.bin(315099, offset), ret=0)))
        data_prog_fitems.append(t['hip_hash'].get_fitem(r0=pFail(setbin=self.bin(315000, offset),ret=0), r2=pPass(goto="NEXT")))
        data_prog_fitems.append(t['hip_hash_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315001, offset), ret=0), r2=pPass(goto="NEXT")))
        data_prog_fitems.append(t['validation_fork'].get_fitem(r0=pFail(setbin=self.bin(315820, offset), ret=0),
                                                               r2=pPass(ret=1),
                                                               r3=pFail(setbin=self.bin(315821, offset), ret=0),
                                                               r4=pFail(setbin=self.bin(315822, offset), ret=0),
                                                               r5=pFail(setbin=self.bin(315823, offset), ret=0),
                                                               r6=pFail(setbin=self.bin(315824, offset), ret=0),
                                                               r7=pFail(setbin=self.bin(315825, offset), ret=0),
                                                               r8=pFail(setbin=self.bin(315826, offset), ret=0),
                                                               r9=pFail(setbin=self.bin(315827, offset), ret=0),
                                                               r10=pFail(setbin=self.bin(315828, offset), ret=0),

                                                               ))
        data_prog_fitems.append(t['check_facilityid_tpfuseenable'].get_fitem(r0=pFail(setbin=self.bin(315830, offset), ret=0),
                                                                             r2=pPass(ret=1),
                                                                             r3=pFail(setbin=self.bin(315831, offset), ret=0),
                                                                             r4=pFail(setbin=self.bin(315832, offset), ret=0),
                                                                             r5=pFail(setbin=self.bin(315833, offset), ret=0),
                                                                             r6=pFail(setbin=self.bin(315834, offset), ret=0),
                                                                             r7=pFail(setbin=self.bin(315835, offset), ret=0),
                                                                             r8=pFail(setbin=self.bin(315836, offset), ret=0),
                                                                             r9=pFail(setbin=self.bin(315837, offset), ret=0),
                                                                             r10=pFail(setbin=self.bin(315838, offset), ret=0),

                                                               ))
        data_prog_fitems.append(t['hvm_burn'].get_fitem(r0=pFail(setbin=self.bin(315200, offset), ret=0),
                                                        r2=pFail(setbin=self.bin(315201, offset), ret=0)))
        data_prog_fitems.append(t['hvm_burn_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315202, offset), ret=0),
                                                             r2=pFail(setbin=self.bin(315203, offset), ret=0)))
        data_prog_fitems.append(t['hvm_rap'].get_fitem(r0=pFail(ctr=self.bin(315100, offset), goto="FUSE_X_FUSEBURN_K_FACTFUSBUILDCPUNOM_X_X_X_X_HVM_BURN_REC"),
                                                       r2=pPass(goto='NEXT')))
        data_prog_fitems.append(t['hvm_flecompare'].get_fitem(r0=pFail(setbin=self.bin(315101, offset), ret=0),
                                                              r1=pPass(ret=3),
                                                              r2=pPass(goto='NEXT')))
        data_prog_fitems.append(t['hvm_burn_rec'].get_fitem(r0=pFail(setbin=self.bin(315220, offset), ret=0),
                                                            r2=pFail(setbin=self.bin(315221, offset), ret=0)))
        data_prog_fitems.append(t['hvm_burn_cpu1_rec'].get_fitem(r0=pFail(setbin=self.bin(315222, offset2), ret=0),
                                                                 r2=pFail(setbin=self.bin(315223, offset2), ret=0)))
        data_prog_fitems.append(t['hvm_rap_rec'].get_fitem(r0=pFail(setbin=self.bin(315140, offset), ret=0),
                                                           r2=pPass(goto='NEXT')))
        data_prog_fitems.append(t['hvm_flecompare_rec'].get_fitem(r0=pFail(setbin=self.bin(315141, offset), ret=0),
                                                                  r1=pPass(ret=3),
                                                                  r2=pPass(ret=4)))
        data_prog_composite = Flow('DATA_PROG_S52C', *data_prog_fitems)

        qual_prog_fitems = []
        qual_prog_fitems.append(t['qual_prog'].get_fitem(r0=pFail(setbin=self.bin(315402, offset), ret=0),
                                                         r2=pPass(ret=2)))
        qual_prog_composite = Flow('QUAL_PROG_S52C', *qual_prog_fitems)

        special_row_ir_fitems = []
        special_row_ir_fitems.append(t['repair_ir'].get_fitem(r0=pFail(setbin=self.bin(315102, offset), ret=0),
                                                              r2=pFail(setbin=self.bin(315103, offset), ret=0)))
        #special_row_ir_fitems.append(t['repair_ir_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315102, offset), ret=0),
        #                                                           r2=pFail(setbin=self.bin(315103, offset), ret=0)))
        special_row_ir_composite = Flow('SPECIAL_ROW_IR_S52C', *special_row_ir_fitems)
    
        repair_string_gen_fitems = []
        repair_string_gen_fitems.append(t['repair_fle_fsg'].get_fitem(r0=pFail(setbin=self.bin(315008, offset), ret=0),
                                                                      r1=pPass(ret=3),
                                                                      r2=pFail(setbin=self.bin(315009, offset), ret=0),
                                                                      r3=pPass(ret=1),
                                                                      r4=pFail(setbin=self.bin(315010, offset), ret=0),
                                                                      ))
        repair_string_gen_fitems.append(t['repair_fle_fsg_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315095, offset), ret=0),
                                                                           r1=pPass(ret=3),
                                                                           r2=pFail(setbin=self.bin(315096, offset), ret=0),
                                                                           r3=pPass(ret=1),
                                                                           r4=pFail(setbin=self.bin(315097, offset), ret=0),
                                                                      ))
        repair_string_gen_composite = Flow('REPAIR_STRING_GEN_S52C', *repair_string_gen_fitems)
    
        special_row_prog_fitems = []
        special_row_prog_fitems.append(t['repair_fuseburn_data'].get_fitem(r0=pFail(setbin=self.bin(315204, offset), ret=0),
                                                                           r2=pFail(setbin=self.bin(315205, offset), ret=0)))
        special_row_prog_fitems.append(t['repair_fuseburn_data_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315206, offset), ret=0),
                                                                                r2=pFail(setbin=self.bin(315207, offset), ret=0)))
        special_row_prog_composite = Flow('SPECIAL_ROW_PROG_S52C', *special_row_prog_fitems)
    
        data_rap_fitems = []
        data_rap_fitems.append(t['repair_rap'].get_fitem(r0=pFail(setbin=self.bin(315104, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(315105, offset), ret=0)))
        data_rap_fitems.append(t['repair_rap_compfle'].get_fitem(r0=pFail(setbin=self.bin(315106, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(315107, offset), ret=2)))
        data_rap_composite = Flow('DATA_RAP_S52C', *data_rap_fitems)
    

        repair_failflow_fitems = []
        repair_failflow_fitems.append(t['sr_rap'].get_fitem(r0=pFail(ret=0),
                                                                     r2=pFail(goto='FUSE_X_FUNC_K_FACTFUSBUILDCPUNOM_X_X_X_X_REPAIR_ECCCHECK_FUNC')))
        #repair_failflow_fitems.append(t['sr_rap_cpu1'].get_fitem(r0=pFail(ret=0),
        #                                                                  r2=pFail(goto='FUSE_X_FUNC_K_FACTFUSBUILDCPUNOM_X_X_X_X_REPAIR_ECCCHECK_FUNC')))
        repair_failflow_fitems.append(t['repair_ecccheck_func'].get_fitem(r0=pFail(setbin=self.bin(315011, offset), ret=1),
                                                                          r2=pFail(setbin=self.bin(315012, offset), ret=1),
                                                                          r3=pFail(setbin=self.bin(315013, offset), ret=1),
                                                                          r4=pFail(setbin=self.bin(315014, offset), ret=1),
                                                                          r5=pFail(setbin=self.bin(315015, offset), ret=1)
                                                                          ))
        repair_failflow_composite = Flow('REPAIR_FAILFLOW_S52C', *repair_failflow_fitems)

        repair_prog_fitems = []
        repair_prog_fitems.append(Fitem('SAME', special_row_ir_composite, r0=pFail(ret=0))) 
        repair_prog_fitems.append(Fitem('SAME', repair_string_gen_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto='NEXT'))) 
        repair_prog_fitems.append(Fitem('SAME', special_row_prog_composite, r0=pFail(ret=0)))
        repair_prog_fitems.append(Fitem('SAME', data_rap_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pFail(goto=repair_failflow_composite.name)))
        repair_prog_fitems.append(Fitem('SAME', repair_failflow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))
        repair_prog_composite = Flow('REPAIR_PROG_S52C', *repair_prog_fitems)

    
        ecc_row_prog_fitems = []
        ecc_row_prog_fitems.append(t['ecc_fuseburn_data'].get_fitem(r0=pFail(setbin=self.bin(315208, offset), ret=0),
                                                                    r2=pFail(setbin=self.bin(315209, offset), ret=0)))
        ecc_row_prog_fitems.append(t['ecc_fuseburn_data_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315210, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315211, offset), ret=0)))
        ecc_row_prog_composite = Flow('ECC_ROW_PROG_S52C', *ecc_row_prog_fitems)

        ecc_rap_fitems = []
        ecc_rap_fitems.append(t['ecc_rap'].get_fitem(r0=pFail(setbin=self.bin(315108, offset), ret=0),
                                                     r2=pFail(setbin=self.bin(315109, offset), ret=2)))
        ecc_rap_fitems.append(t['ecc_rap_flecompare'].get_fitem(r0=pFail(setbin=self.bin(315110, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(315111, offset), ret=2)))
        #ecc_rap_fitems.append(t['ecc_rap_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315196, offset), ret=0),
        #                                                  r2=pFail(setbin=self.bin(315197, offset), ret=2)))
        ecc_rap_fitems.append(t['ecc_rap_flecompare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315198, offset), ret=0),
                                                                     r2=pFail(setbin=self.bin(315199, offset), ret=2)))
        ecc_rap_composite = Flow('ECC_RAP_S52C', *ecc_rap_fitems)

        ecc_failflow_fitems = []
        ecc_failflow_fitems.append(t['ecc_check_func'].get_fitem(r0=pFail(setbin=self.bin(315016, offset), ret=1),
                                                                 r1=pPass(ret=1),
                                                                 r2=pFail(setbin=self.bin(315017, offset), ret=1),
                                                                 r3=pFail(setbin=self.bin(315018, offset), ret=1),
                                                                 r4=pFail(setbin=self.bin(315019, offset), ret=1),
                                                                 r5=pFail(setbin=self.bin(315020, offset), ret=1)))
        ecc_failflow_composite = Flow('ECC_FAILFLOW_S52C', *ecc_failflow_fitems)

        ecc_prog_fitems = []
        #ecc_prog_fitems.append(Fitem('SAME', ecc_special_row_ir_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_string_gen_composite.name)))
        #ecc_prog_fitems.append(Fitem('SAME', ecc_string_gen_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_row_prog_composite.name)))
        ecc_prog_fitems.append(Fitem('SAME', ecc_row_prog_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_rap_composite.name)))
        ecc_prog_fitems.append(Fitem('SAME', ecc_rap_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pFail(goto=ecc_failflow_composite.name)))
        ecc_prog_fitems.append(Fitem('SAME', ecc_failflow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))
        ecc_prog_composite = Flow('ECC_PROG_S52C', *ecc_prog_fitems)

        tap_unlock_fitems = []
        tap_unlock_fitems.append(t['tap_status'].get_fitem(r0=pFail(setbin=self.bin(315900, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(315901, offset), ret=0),
                                                           r3=pFail(setbin=self.bin(315902, offset), ret=0),
                                                           r4=pFail(setbin=self.bin(315903, offset), ret=0),
                                                           r5=pFail(setbin=self.bin(315904, offset), ret=0),
                                                            ))
        tap_unlock_fitems.append(t['unit_info_decode'].get_fitem(r0=pFail(setbin=self.bin(315840, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(315841, offset), ret=0),
                                                                 r3=pPass(goto='FUSE_X_PATCONFIG_K_FACTFUSBUILDCPUNOM_X_X_X_X_LEGACY_UNLOCK'),
                                                                 r4=pFail(setbin=self.bin(315842, offset), ret=0),
                                                                 r5=pFail(setbin=self.bin(315843, offset), ret=0),
                                                                 r6=pFail(setbin=self.bin(315844, offset), ret=0),
                                                                 r7=pFail(setbin=self.bin(315845, offset), ret=0),
                                                                 r8=pFail(setbin=self.bin(315846, offset), ret=0),
                                                                 r9=pFail(setbin=self.bin(315847, offset), ret=0),
                                                                 r10=pFail(setbin=self.bin(315848, offset), ret=0),
                                                                 ))
        tap_unlock_fitems.append(t['screen_red_unlock'].get_fitem(r0=pFail(setbin=self.bin(315850, offset), ret=0),
                                                                  r2=pFail(setbin=self.bin(315851, offset), ret=0),
                                                                  r3=pFail(setbin=self.bin(315852, offset), ret=0),
                                                                  r4=pFail(setbin=self.bin(315853, offset), ret=0),
                                                                  r5=pFail(setbin=self.bin(315854, offset), ret=0),
                                                                  r6=pFail(setbin=self.bin(315855, offset), ret=0),
                                                                  r7=pFail(setbin=self.bin(315856, offset), ret=0),
                                                                  r8=pFail(setbin=self.bin(315857, offset), ret=0),
                                                                  r9=pFail(setbin=self.bin(315858, offset), ret=0),
                                                                  r10=pFail(setbin=self.bin(315859, offset), ret=0),
                                                                 ))
        tap_unlock_fitems.append(t['red_unlock'].get_fitem(r0=pFail(setbin=self.bin(315701, offset), ret=0),
                                                           r1=pPass(ret=1)
                                                           ))
        tap_unlock_fitems.append(t['legacy_unlock'].get_fitem(r0=pFail(setbin=self.bin(315702, offset), ret=0)))
        tap_unlock_composite = Flow('TAP_UNLOCK_S52C', *tap_unlock_fitems)

        lockout_prog_fitems = []
        lockout_prog_fitems.append(t['lockbit_fsg'].get_fitem(r0=pFail(setbin=self.bin(315021, offset), ret=0)))
        lockout_prog_fitems.append(t['lockbit_fsg_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315094, offset), ret=0)))
        lockout_prog_fitems.append(t['lockbit_burn'].get_fitem(r0=pFail(setbin=self.bin(315212, offset), ret=0),
                                                               r2=pFail(setbin=self.bin(315213, offset), ret=0)))
        lockout_prog_fitems.append(t['lockbit_burn_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315214, offset), ret=0),
                                                               r2=pFail(setbin=self.bin(315215, offset), ret=0)))
        lockout_prog_fitems.append(Fitem('SAME', tap_unlock_composite, r0=pFail(ret=0)))
        lockout_prog_fitems.append(t['lockbit_rap'].get_fitem(r0=pFail(setbin=self.bin(315112, offset), ret=0),
                                                              r2=pPass(goto='NEXT')
                                                                ))
        lockout_prog_fitems.append(t['lockbit_rap_flecompare'].get_fitem(r0=pFail(setbin=self.bin(315113, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315114, offset), ret=2)
                                                                         ))
        #lockout_prog_fitems.append(t['lockbit_rap_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315195, offset), ret=0),
        #                                                      r2=pPass(goto='NEXT')
        #                                                        ))
        lockout_prog_fitems.append(t['lockbit_rap_flecompare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315193, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(315194, offset), ret=2)
                                                                         ))
        lockout_prog_composite = Flow('LOCKOUT_PROG_S52C', *lockout_prog_fitems)

        ecc_set_fitems = []
        ecc_set_fitems.append(t['ecc_status'].get_fitem(r0=pFail(setbin=self.bin(315300, offset), ret=0),
                                                        r1=pPass(ret=1),
                                                        r2=pFail(setbin=self.bin(315301, offset), goto='NEXT'),
                                                        r3=pFail(setbin=self.bin(315302, offset), ret=0),
                                                        r4=pFail(setbin=self.bin(315303, offset), ret=0)
                                                        ))
        ecc_set_fitems.append(t['ecc_preamble_func'].get_fitem(r0=pFail(setbin=self.bin(315022, offset), ret=2),
                                                               r1=pPass(ret=2),
                                                               r2=pFail(setbin=self.bin(315023, offset), ret=2),
                                                               r3=pFail(setbin=self.bin(315024, offset), ret=2),
                                                               r4=pFail(setbin=self.bin(315025, offset), ret=2),
                                                               r5=pFail(setbin=self.bin(315026, offset), ret=2),
                                                               ))
        ecc_set_composite = Flow('ECC_SET_S52C', *ecc_set_fitems)


        efuse_read_fitems = []
        efuse_read_fitems.append(t['efuse_read'].get_fitem(r0=pFail(setbin=self.bin(315115, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(315116, offset), ret=2),
                                                           r3=pFail(setbin=self.bin(315117, offset), ret=2),
                                                           ))
        #efuse_read_fitems.append(t['efuse_read_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315190, offset), ret=0),
        #                                                   r2=pFail(setbin=self.bin(315191, offset), ret=2),
        #                                                   r3=pFail(setbin=self.bin(315192, offset), ret=2),
        #                                                   ))
        efuse_read_fitems.append(t['fuse_efuse_compare'].get_fitem(r0=pFail(setbin=self.bin(315120, offset), ret=0),
                                                                   r2=pFail(setbin=self.bin(315121, offset), ret=0),
                                                                   r3=pFail(setbin=self.bin(315122, offset), ret=0),
                                                                   r4=pFail(setbin=self.bin(315123, offset), ret=0),
                                                                   r5=pFail(setbin=self.bin(315124, offset), ret=0),
                                                                   r6=pFail(setbin=self.bin(315125, offset), ret=0),
                                                                   r7=pFail(setbin=self.bin(315126, offset), ret=0),
                                                                   r8=pFail(setbin=self.bin(315127, offset), ret=0),
                                                                   r9=pFail(setbin=self.bin(315128, offset), ret=0),
                                                                   r10=pFail(setbin=self.bin(315129, offset), ret=0),
                                                                  ))
        efuse_read_fitems.append(t['dff_ult_efuse_compare'].get_fitem(r0=pFail(setbin=self.bin(315130, offset), ret=0),
                                                                      r2=pFail(setbin=self.bin(315131, offset), ret=0)))
        efuse_read_fitems.append(t['dff_ult_efuse_compare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315132, offset), ret=0),
                                                                      r2=pFail(setbin=self.bin(315133, offset), ret=0)))
        efuse_read_composite = Flow('EFUSE_READ_S52C', *efuse_read_fitems)

        retest_store_fitems = []
        retest_store_fitems.append(Fitem('SAME', efuse_read_composite, r0=pFail(ret=0),
                                                                       r2=pFail(ret=2)
                                                                       ))
        retest_store_fitems.append(t['security_key_hashgen'].get_fitem(r0=pFail(setbin=self.bin(315027, offset), ret=2),
                                                                       r2=pFail(setbin=self.bin(315028, offset), ret=2)
                                                                       ))
        retest_store_fitems.append(t['security_key_hashgen_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315088, offset), ret=2),
                                                                            r2=pFail(setbin=self.bin(315089, offset), ret=2)
                                                                       ))
        retest_store_fitems.append(t['post_process_hostkey'].get_fitem(r0=pFail(setbin=self.bin(315860, offset), ret=0),
                                                                       r2=pFail(setbin=self.bin(315861, offset), ret=0),
                                                                       r3=pFail(setbin=self.bin(315862, offset), ret=0),
                                                                       r4=pFail(setbin=self.bin(315863, offset), ret=0),
                                                                       r5=pFail(setbin=self.bin(315864, offset), ret=0),
                                                                       r6=pFail(setbin=self.bin(315865, offset), ret=0),
                                                                       r7=pFail(setbin=self.bin(315866, offset), ret=0),
                                                                       r8=pFail(setbin=self.bin(315867, offset), ret=0),
                                                                       r9=pFail(setbin=self.bin(315868, offset), ret=0),
                                                                       r10=pFail(setbin=self.bin(315869, offset), ret=0),
                                                                       ))
        retest_store_fitems.append(t['apply_gen_hash'].get_fitem(r0=pFail(setbin=self.bin(315703, offset), ret=2)))
        retest_store_fitems.append(t['read_hash_status'].get_fitem(r0=pFail(setbin=self.bin(315029, offset), ret=0),
                                                                   r2=pFail(setbin=self.bin(315030, offset), ret=0),
                                                                   r3=pFail(setbin=self.bin(315031, offset), ret=0),
                                                                   r4=pFail(setbin=self.bin(315032, offset), ret=0),
                                                                   r5=pFail(setbin=self.bin(315033, offset), ret=0),
                                                                       ))
        retest_store_composite = Flow('RETEST_STORE_S52C', *retest_store_fitems)

        feedback_fitems = []
        feedback_fitems.append(t['security_set'].get_fitem(r0=pFail(setbin=self.bin(315134, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(315135, offset), ret=0)))
        feedback_fitems.append(t['post_fuse_confirm'].get_fitem(r0=pFail(setbin=self.bin(315406, offset), ret=0)))
        feedback_composite = Flow('FEEDBACK_S52C', *feedback_fitems)

        feedback_failflow_fitems = []
        feedback_failflow_fitems.append(t['security_set_ff'].get_fitem(r0=pFail(setbin=self.bin(315136, offset), ret=0),
                                                                       r2=pFail(setbin=self.bin(315137, offset), ret=0)))
        feedback_failflow_composite = Flow('FEEDBACK_FAIL_S52C', *feedback_failflow_fitems)


        fact_fitems = []
        fact_fitems.append(t['s52c_check'].get_fitem(r0=pFail(setbin=self.bin(315400, offset),ret=0), r2=pPass(ret=1)))
        fact_fitems.append(Fitem('SAME', burn_setup_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto=data_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', data_prog_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto=qual_prog_composite.name), r4=pPass(goto=repair_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', qual_prog_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_prog_composite.name), r2=pPass(goto=ecc_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', ecc_prog_composite, r0=pFail(ret=0), r1=pPass(goto=lockout_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', repair_prog_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_prog_composite.name)))
        fact_fitems.append(Fitem('SAME', lockout_prog_composite, r0=pFail(ret=0), r1=pPass(goto=ecc_set_composite.name), r2=pFail(goto=feedback_failflow_composite.name)))
        fact_fitems.append(Fitem('SAME', ecc_set_composite, r0=pFail(ret=0), r1=pPass(goto=retest_store_composite.name), r2=pFail(goto=feedback_failflow_composite.name)))
        fact_fitems.append(Fitem('SAME', retest_store_composite, r0=pFail(ret=0), r1=pPass(goto=feedback_composite.name), r2=pFail(goto=feedback_failflow_composite.name)))
        fact_fitems.append(Fitem('SAME', feedback_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        fact_fitems.append(Fitem('SAME', feedback_failflow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))

        Flow(flow_name,*fact_fitems)


class CDIE_816_SORT(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='sort')
        self.LevelsTc = 'BASE::SBF_nom_lvl'
        self.TimingsTc = 'BASE::cpu_ctf_timing_tclk100_hclk100_bclk400'
        self.PrePlist = None

    def initialize(self, name1, name2, rev):
        Import("FUS_FUSEBURN_CXX.usrv")
        InitializeNVLSort(name1, name2, defaultrm1bin=-31, defaultrm2bin=-31, binrange=[(3150, 3159)])
        MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        # Add the necessary files to import in your mtpl
        Import("FUS_FUSEBURN_CXX.usrv")


class CDIE_816_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        #self.LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        self.TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100'
        self.PrePlist = ''

    def initialize(self, name1, name2, rev):

        InitializeNVLClass(name1, name2, defaultrm1bin=(98312000,98313999), defaultrm2bin=(99312000,99313999), binrange=[(3150, 3159)])
        #MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        Import("FUS_FUSEBURN_CXX.usrv")


rev = '25ww13p2_rev1'

#cdie = CDIE_816_SORT()
#cdie.initialize('./PyMTPL_OUTPUT/CDIE_SORT/FUS_FUSEBURN_CXX', 'FUS_FUSEBURN_CXX', rev)
#cdie.get_fact_flow('FUS_FUSEBURN_CXX_FACT')

cdie = CDIE_816_CLASS()
cdie.initialize('./FUS_FUSEBURN_CXX', 'FUS_FUSEBURN_CXX', rev)
cdie.get_init_flow('FUS_FUSEBURN_CXX_INIT')
cdie.get_fact_flow('FUS_FUSEBURN_CXX_FACTFUSBURNCPUNOM')
cdie.get_fact52c_flow('FUS_FUSEBURN_CXX_FACTFUSBUILDCPUNOM')