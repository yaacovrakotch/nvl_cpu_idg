# Import the necessary classes from Pymtpl
import copy
import re, json

from pymtpl.por_methods import AuxiliaryTC, ScreenTC, PrimePatConfigTestMethod, PrimeFuseReadMaskTestMethod, PrimeFunctionalTestMethod, SFMFuseReadMask, SFMDffEfuseCheck, PrimeFuseReadMaskUltDecodeTestMethod, FleCheckFuseStringStatus, FleCheckFuseStringStatusByDies, FleGetDieStatus, FleISeedGetUnitKeys, SFMCheckEccStatisticsStatus, PrimeFuseReadMarginSweepTestMethod, FleCheckFusedSspecFusing, FlePrintSSPECToItuff
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
            'ScreenTestsFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEREAD_C2X.screen.json","./InputFiles/FUSEREAD_C1X.screen.json")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = ScreenTC(**param)

class PrimePatConfigTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_PATCONFIG_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
           #'ConfigurationFile': Spec('__shared__::TpRule.If_S28_S52_HX28_P16C("./InputFiles/FUSEREAD_C1X_TSMC.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C2X.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C1X.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C1X.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C1X_TSMC.PatConfigSetpoints.json")'),
            'ConfigurationFile': Spec(f'FUS_FUSEREAD_CXX_Rules.FUSE_X_PATCONFIG_K_{module_name.upper()}_X_X_X_X_{name.upper()}_CfgFile("./InputFiles/FUSEREAD_C2X.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C1X_TSMC.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C2X_TSMC.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C1X_TSMC.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C1X.PatConfigSetpoints.json")'),
            'SetPoint': Spec(f'FUS_FUSEREAD_CXX_Rules.FUSE_X_PATCONFIG_K_{module_name.upper()}_X_X_X_X_{name.upper()}_SetPoint("CPU_QA","CPU_QA","CPU_READ")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimePatConfigTestMethod(**param)

class PrimeFuseReadMaskTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUSEREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('FUS_FUSEREAD_CXX_Rules.FUSEREAD_CfgFile("./InputFiles/FUSEREAD_C2X.fuseRead.json","./InputFiles/FUSEREAD_C2X.fuseRead_BLLC.json","./InputFiles/FUSEREAD_C1X.fuseRead_BLLC.json","./InputFiles/FUSEREAD_C1X.fuseRead.json")'),
            'SkipPatternExecute': f'DISABLED',
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'), 
            'SharedStorageKeyToStore': Spec('__shared__::TpRule.If_MICP("FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0,FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1","FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0")'),
            'BypassPort': f'-1'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFuseReadMaskTestMethod(**param)

class PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_ULTREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEREAD_C2X.fuseRead.json","./InputFiles/FUSEREAD_C1X.fuseRead.json")'),
            'SkipPatternExecute': f'DISABLED',
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
            'DieIdNames': Spec('__shared__::TpRule.If_MICP("U1.U5,U1.U6", "U1.U5")'),
            #'SharedStorageKeyToStore': Spec('__shared__::TpRule.If_MICP("FUS_FUSEREAD_FuseReadOutputStr_CPU0,FUS_FUSEREAD_FuseReadOutputStr_CPU1","FUS_FUSEREAD_FuseReadOutputStr_CPU0")'),
            'BypassPort': f'-1'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFuseReadMaskUltDecodeTestMethod(**param)

class PrimeFuseReadMarginSweepTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_ULTREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('FUS_FUSEREAD_CXX_Rules.FUSEREAD_CfgFile("./InputFiles/FUSEREAD_C2X.fuseRead.json","./InputFiles/FUSEREAD_C2X.fuseRead_BLLC.json","./InputFiles/FUSEREAD_C1X.fuseRead_BLLC.json","./InputFiles/FUSEREAD_C1X.fuseRead.json")'),
            'SkipPatternExecute': f'DISABLED',
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
            'BypassPort': f'-1',
            'LevelsTc': Spec("__shared__::TpRule.If_MICP(CPU_IP_BASE::cpu0_all_bf_x_x_ipc_lvl_nom,CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom)"),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFuseReadMarginSweepTestMethod(**param)

class PrimeFunctionalTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUNC_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'FailuresToCaptureTotal': Spec('1'),
            'MaxFailuresToItuff': Spec('1')
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFunctionalTestMethod(**param)

class SFMFuseReadMask_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUSEREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEREAD_C2X.fuseRead.json","./InputFiles/FUSEREAD_C1X.fuseRead.json")'),
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
            'ExpectedPort': f'1',
	        'ExceptionPort': f'2',
            'BypassPort': f'-1',
            'FuseReadGlobal': Spec('__shared__::TpRule.If_MICP("FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0,FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1","FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0")'),
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = SFMFuseReadMask(**param)

class SFMDffEfuseCheck_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'DffFormat': f'Desegregation',
            'UserVarCollection': 'FUSEUFGL',
            'BypassPort': Spec('-1'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = SFMDffEfuseCheck(**param)

class FleCheckFuseStringStatus_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'1',
            'OutputFuseStringLocation': f'Uservar',
            'LockoutBitGroup': f'LockoutBits_00',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleCheckFuseStringStatus(**param)

class FleCheckFuseStringStatusByDies_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'1',
            'FuseReadTokenNames':Spec('__shared__::TpRule.If_MICP("FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0,FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1","FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0")'),
            'OutputFuseStringLocation': f'SharedStorage',
            'LockoutBitGroup': f'LockoutBits_00',
            'Registers': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'),
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleCheckFuseStringStatusByDies(**param)   
		                                          
class FleGetDieStatus_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'1',
            'FuseStateUservar': f'Which_Socket.FuseState',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGetDieStatus(**param)

class FleISeedGetUnitKeys_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_ISEED_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'DieId': f'PKG',
            'KeysTypeId': Spec('__shared__::TpRule.If_MICP("1600,1599","1600")'),
            'QueryMode': f'ENG',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleISeedGetUnitKeys(**param)

class FleCheckFusedSspecFusing_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'1',
            'FuseReadTokenName': f'FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0',
            'OutputFuseStringLocation': f'SharedStorage',
            'SspecFuseGroupName': f'dfx_agg/qdf_fuse'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleCheckFusedSspecFusing(**param)

class FlePrintSSPECToItuff_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'1',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FlePrintSSPECToItuff(**param)

class SFMCheckEccStatisticsStatus_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'1',
            'NumberOfCorrectableError': 0,
            'SetPoint': f'Intel_10nm',
            'CtvCapturePins': Spec('__shared__::TpRule.If_MICP("IPC::CPU_TDO,IPC::CPU1_TDO","IPC::CPU_TDO")')

        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = SFMCheckEccStatisticsStatus(**param)




class Custom_TestBuilder(TestConfig):
    def __init__(self, name, module_name, custom_test_name, custom_testmethod_name, isEDC=False, test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'{custom_test_name.upper()}_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = custom_testmethod_name(**param)

class FleGetDieStatus(BaseMethod):
    def __init__(self,
                 name,
                 FuseStateUservar=required,  # <param>=required|optional,
                 Register=required,
                 _comment=None,  # required, do not omit
                 _fitem=None,  # required, do not omit
                 **kwargs  # required, do not omit
                 ):
        self._init(name, locals())

class CDIE_BASE:
    def __init__(self,sort_class):
        self.sort_class = sort_class
        self.LevelsTc = None
        self.TimingsTc = None
        
        
    def bin(self, _bin, _offset=0):
        _bin_str = str(_bin+_offset)
        if len(_bin_str) != 6:
            raise Exception('invalid bin')
        if not (_bin_str.startswith('31') or _bin_str.startswith('92')):
            raise Exception('invalid bin')
        hard_bin = _bin_str[0:2]
        soft_bin = _bin_str[2:4]
        counter = int(_bin_str[4:6])

        counter_total = counter + int(_offset)
        yyyy = 2000 + counter_total

        final_bin = None
        if self.sort_class == 'sort':
            final_bin = int(f'{hard_bin}{soft_bin}{soft_bin}{counter}')
        else:
            final_bin = int(f'{hard_bin}{soft_bin}{yyyy:04d}')

        return final_bin


    def get_start_flow(self, flow_name, module_name='STARTCPUNOM', is_edc=False,  bin_offset=0, bin_offset2=0, composite_postfix=None, test_instance_postfix=None):
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


        
        # tests for START / PREREAD
        t['all_in_one_fork_cpu'] = ScreenTC_TestBuilder(name='all_in_one_fork_cpu', ScreenTestSet='AllInOneCheck', **dparams)
        
        # tests for START / FUNCTIONAL_TEST
        t['read_strobe'] = PrimeFunctionalTestMethod_TestBuilder(name='read_strobe', BypassPort=-1, Patlist='IPC::cpu_dfxagg_read_hvm_status_csr', **dparams)
        t['lockstatus_check'] =  AuxiliaryTC_TestBuilder(name='lockstatus_check', DataType='String', Expression = "[G.U.S.LCKSTATUS_CPU0]='LGUL_CPU0'", ResultPort = '[R]?1:2', Storage='SharedStorage', **dparams)
        t['canary_read_func'] = PrimeFunctionalTestMethod_TestBuilder(name='canary_read_func', BypassPort=Spec('FUS_FUSEREAD_CXX_Rules.FUSE_X_FUNC_K_STARTCPUNOM_X_X_X_X_CANARY_READ_FUNC_BypassPort(1,1,1,-1)'), Patlist='IPC::cpu_fuse_read_hvm_canary_func', **dparams)

        # tests for START / FUSE_READ
        t['read_margin_set'] = PrimePatConfigTestMethod_TestBuilder(name='read_margin_set', BypassPort=-1, **dparams)
        t['ir'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='ir', ConfigName='FuseReadFlow', BypassPort=-1, PassingMaskName='maskv_CPU_skip', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', PackageEfuse=Spec('__shared__::TpRule.If_MICP("ALLOW_NO_PKG","")'), **dparams)
        #t['ir_cpu1'] = SFMFuseReadMask_TestBuilder(name='ir_cpu1', ConfigName='FuseReadFlow_CPU1', BypassPort=1, ConfigurationFile='./InputFiles/FUSEREAD_C2X.fuseRead.json', PassingMaskName='maskv_CPU_skip', FuseMaskName='maskv_CPU_skip', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', RegisterName="CPU1", FuseReadGlobal="FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FUS_FUSEREAD_FuseReadOutputStr_CPU1", **dparams)
        
        # tests for START / RETEST_EXEC
        t['fuse_string_valid_check'] = FleCheckFuseStringStatusByDies_TestBuilder(name='fuse_string_valid_check', BypassPort=-1,  **dparams)
        #t['fuse_string_valid_check_cpu1'] = FleCheckFuseStringStatus_TestBuilder(name='fuse_string_valid_check_cpu1', BypassPort=Spec('__shared__::TpRule.If_MICP(1,1)'), Register='CPU1', FuseReadTokenName='FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1',**dparams)
        t['socket_mode_check'] = FleGetDieStatus_TestBuilder(name='socket_mode_check', BypassPort=-1, Register='CPU0', **dparams)
        t['get_host_key'] = FleISeedGetUnitKeys_TestBuilder(name='get_host_key', BypassPort=-1, **dparams)
        t['post_process_hostkey'] = ScreenTC_TestBuilder(name='post_process_hostkey_for_hash_setup', ScreenTestSet='HASH_SETUP_CPU', **dparams)
        t['set_hash'] = PrimePatConfigTestMethod_TestBuilder(name='set_hash', ConfigurationFile=Spec('__shared__::TpRule.If_MICP("./InputFiles/FUSEREAD_C2X.PatConfigSetpoints.json","./InputFiles/FUSEREAD_C1X.PatConfigSetpoints.json")'), SetPoint='SET_HASHSIG_CPU', BypassPort=-1, **dparams)
        t['read_hash'] = PrimeFunctionalTestMethod_TestBuilder(name='read_hash', BypassPort=-1, Patlist='IPC::cpu_fuse_hvm_hash', **dparams)
        t['populate_sspec'] = ScreenTC_TestBuilder(name='populate_sspec', ScreenTestSet=Spec('FUS_FUSEREAD_CXX_Rules.FUSE_X_SCREENTC_K_STARTCPUNOM_X_X_X_X_POPULATE_SSPEC_SetPoint("POP_SSPEC_QA","POP_SSPEC")'), BypassPort=Spec('__shared__::TpRule.FuseRetestBypass(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1)'), **dparams)
        t['check_fused_sspec'] = FleCheckFusedSspecFusing_TestBuilder(name='check_fused_sspec', BypassPort=Spec('__shared__::TpRule.FuseRetestBypass(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1)'), Register='CPU0', **dparams)
        t['print_sspec_to_ituff'] = FlePrintSSPECToItuff_TestBuilder(name='print_sspec_to_ituff', BypassPort=Spec('__shared__::TpRule.FuseRetestBypass(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)'), Register='CPU0', **dparams)
       
        # tests for START / QA_FUSED
        t['check_ecc_status'] = SFMCheckEccStatisticsStatus_TestBuilder(name='check_ecc_status', Patlist='IPC::cpu_fuse_read_hvm_ecc_statictics', BypassPort=1,  **dparams)
        t['efuse_read'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuse_read', ConfigName='CXX_EFUSEReadFlow', BypassPort=-1, PassingMaskName='PMaskName_All_ss', FailingMaskName='FMaskName_All_00,FMaskName_All_11,FMaskName_All_01,FMaskName_All_10', Patlist='IPC::cpu_dfxagg_read_hvm_efuse', FuseGroupToDatalog='EFUSE_ULT', RegisterName = Spec('__shared__::TpRule.If_MICP("CPU0_EFUSE,CPU1_EFUSE","CPU0_EFUSE")'), PackageEfuse=Spec('__shared__::TpRule.If_MICP("ALLOW_NO_PKG","")'), **dparams)
        #t['efuse_read_cpu1'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuse_read_cpu1', ConfigName='EFUSEReadFlow_CPU1', BypassPort=1, ConfigurationFile='./InputFiles/FUSEREAD_C2X.fuseRead.json', PassingMaskName='PMaskName_All_ss', FailingMaskName='FMaskName_All_00,FMaskName_All_11,FMaskName_All_01,FMaskName_All_10', Patlist='IPC::cpu_dfxagg_read_hvm_efuse', FuseGroupToDatalog='EFUSE_ULT', DieIdNames='__shared__::DFFVars.DIEID_CPU1', RegisterName = 'CPU1_EFUSE', **dparams)
        t['fuse_efuse_compare'] = ScreenTC_TestBuilder(name='fuse_efuse_compare', ScreenTestSet='EFUSE_CHECK', BypassPort=-1, **dparams)
        t['dff_ult_efuse_compare'] = SFMDffEfuseCheck_TestBuilder(name='dff_ult_efuse_compare', DieIdName=Spec('__shared__::DFFVars.DIEID_CPU'), **dparams)
        t['dff_ult_efuse_compare_cpu1'] = SFMDffEfuseCheck_TestBuilder(name='dff_ult_efuse_compare_cpu1', DieIdName=Spec('__shared__::DFFVars.DIEID_CPU1'), BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), **dparams)
        
        # tests for START / MARGINS_READ
        t['ir_margins'] = PrimeFuseReadMarginSweepTestMethod_TestBuilder(name='ir_margins', ConfigName='MarginFuseReadFlow', BypassPort=-1, Patlist='IPC::cpu_fuse_read_hvm_msw', RegisterName="CPU0", FuseGroupToDatalog='', isEDC=True, **dparams)
        t['ir_margins_cpu1'] = PrimeFuseReadMarginSweepTestMethod_TestBuilder(name='ir_margins_cpu1', ConfigName='MarginFuseReadFlow_CPU1', BypassPort=Spec("__shared__::TpRule.If_MICP(-1,1)"), Patlist='IPC::cpu_fuse_read_hvm_msw', FuseGroupToDatalog='', RegisterName="CPU1", isEDC=True, **dparams)
        
        # tests for START / RESET_FAIL_FLOW
        t['babysteps_tests'] = PrimeFunctionalTestMethod_TestBuilder(name='babysteps_tests', BypassPort=-1, Patlist='IPC::cpu_fuse_debug_babystep_tap_access', isEDC=True, **dparams)
        t['fsm_babysteps_tests'] = PrimeFunctionalTestMethod_TestBuilder(name='fsm_babysteps_tests', BypassPort=-1, Patlist='IPC::cpu_fuse_read_babystep_fsm', isEDC=True, **dparams)
        
       
        ##Flow Setup
        
        preread_fitems = []
        preread_fitems.append(t['all_in_one_fork_cpu'].get_fitem(r0=pFail(setbin=self.bin(314820, offset), ret=0),
                                                                    r1=pPass(ret=1),
                                                                    r2=pFail(setbin=self.bin(314821, offset), ret=0),
                                                                    r3=pPass(ret=3),
                                                                    r4=pFail(setbin=self.bin(314822, offset), ret=0),
                                                                    r5=pFail(setbin=self.bin(314823, offset), ret=0),
                                                                    r6=pFail(setbin=self.bin(314824, offset), ret=0),
                                                                    r7=pFail(setbin=self.bin(314825, offset), ret=0),
                                                                    r8=pFail(setbin=self.bin(314826, offset), ret=0),
                                                                    r9=pFail(setbin=self.bin(314827, offset), ret=0),
                                                                    r10=pFail(setbin=self.bin(314828, offset), ret=0)
                                                                    ))
        preread_composite = Flow('PREREAD', *preread_fitems)

        functional_test_fitems = []
        functional_test_fitems.append(t['read_strobe'].get_fitem(r0=pFail(setbin=self.bin(314906, offset), ret=0),
                                                                 r4=pFail(setbin=self.bin(314907, offset), ret=0),
                                                                 r5=pFail(setbin=self.bin(314908, offset), ret=0)
                                                                 ))
        functional_test_fitems.append(t['lockstatus_check'].get_fitem(r0=pFail(setbin=self.bin(314069, offset),ret=0), r1=pPass(goto='NEXT'), r2=pPass(ret=1)))
        functional_test_fitems.append(t['canary_read_func'].get_fitem(r0=pFail(setbin=self.bin(314000, offset), ret=0),
                                                                      r4=pFail(setbin=self.bin(314001, offset), ret=0),
                                                                      r5=pFail(setbin=self.bin(314002, offset), ret=0)
                                                                      ))
        functional_test_composite = Flow('FUNCTIONAL_TESTS', *functional_test_fitems)

        fuse_read_fitems = []
        fuse_read_fitems.append(t['read_margin_set'].get_fitem(r0=pFail(setbin=self.bin(314713, offset), ret=0)))
        fuse_read_fitems.append(t['ir'].get_fitem(r0=pFail(setbin=self.bin(314132, offset), ret=0),
                                                  r2=pFail(setbin=self.bin(314133, offset), ret=0)))
        #fuse_read_fitems.append(t['ir_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314198, offset), ret=0),
        #                                               r2=pFail(setbin=self.bin(314199, offset), ret=0)))
        fuse_read_composite = Flow('FUSE_READ', *fuse_read_fitems)

        retest_exec_fitems = []
        retest_exec_fitems.append(t['fuse_string_valid_check'].get_fitem(r0=pFail(setbin=self.bin(314400, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(314401, offset), ret=2),
                                                                         r3=pPass(goto='NEXT'),
                                                                         r4=pFail(setbin=self.bin(314402, offset), ret=4),
                                                                         r5=pFail(setbin=self.bin(314403, offset), ret=4),
                                                                         r6=pFail(setbin=self.bin(314404, offset), ret=4),
                                                                         r7=pFail(setbin=self.bin(314405, offset), ret=4)
                                                                         ))
        #retest_exec_fitems.append(t['fuse_string_valid_check_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314408, offset), ret=0),
        #                                                                      r2=pFail(setbin=self.bin(314409, offset), ret=2),
        #                                                                      r3=pPass(goto='NEXT'),
        #                                                                      r4=pFail(setbin=self.bin(314410, offset), ret=4),
        #                                                                      r5=pFail(setbin=self.bin(314411, offset), ret=4),
        #                                                                      r6=pFail(setbin=self.bin(314412, offset), ret=4)
        #                                                                      ))
        retest_exec_fitems.append(t['socket_mode_check'].get_fitem(r0=pFail(setbin=self.bin(314406, offset), ret=0),
                                                                   r1=pPass(ret=1),
                                                                   r2=pFail(setbin=self.bin(314407, offset), ret=2),
                                                                   r3=pPass(goto='NEXT'),
                                                                   r4=pFail(setbin=self.bin(314408, offset), ret=4)
                                                                   ))
        retest_exec_fitems.append(t['get_host_key'].get_fitem(r0=pFail(setbin=self.bin(920203, offset), ret=0)))
        retest_exec_fitems.append(t['post_process_hostkey'].get_fitem(r0=pFail(setbin=self.bin(314830, offset), ret=0),
                                                                      r2=pFail(setbin=self.bin(314831, offset), ret=0),
                                                                      r3=pFail(setbin=self.bin(314832, offset), ret=0),
                                                                      r4=pFail(setbin=self.bin(314833, offset), ret=0),
                                                                      r5=pFail(setbin=self.bin(314834, offset), ret=0),
                                                                      r6=pFail(setbin=self.bin(314835, offset), ret=0),
                                                                      r7=pFail(setbin=self.bin(314836, offset), ret=0),
                                                                      r8=pFail(setbin=self.bin(314837, offset), ret=0),
                                                                      r9=pFail(setbin=self.bin(314838, offset), ret=0),
                                                                      r10=pFail(setbin=self.bin(314839, offset), ret=0)
                                                                      ))
        retest_exec_fitems.append(t['set_hash'].get_fitem(r0=pFail(setbin=self.bin(314714, offset), ret=0)))
        retest_exec_fitems.append(t['read_hash'].get_fitem(r0=pFail(setbin=self.bin(314003, offset), ret=0),
                                                           r4=pFail(setbin=self.bin(314004, offset), ret=0),
                                                           r5=pFail(setbin=self.bin(314005, offset), ret=0)
                                                           ))
        retest_exec_fitems.append(t['populate_sspec'].get_fitem(r0=pFail(setbin=self.bin(314840, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(314841, offset), ret=0),
                                                                r3=pPass(ret=3),
                                                                r4=pFail(setbin=self.bin(314842, offset), ret=0),
                                                                r5=pFail(setbin=self.bin(314843, offset), ret=0),
                                                                r6=pFail(setbin=self.bin(314844, offset), ret=0),
                                                                r7=pFail(setbin=self.bin(314845, offset), ret=0),
                                                                r8=pFail(setbin=self.bin(314846, offset), ret=0),
                                                                r9=pFail(setbin=self.bin(314847, offset), ret=0),
                                                                r10=pFail(setbin=self.bin(314848, offset), ret=0)
                                                                ))
        retest_exec_fitems.append(t['check_fused_sspec'].get_fitem(r0=pFail(setbin=self.bin(314500, offset), ret=0),
                                                                   r2=pFail(setbin=self.bin(314501, offset), ret=0)))
        retest_exec_fitems.append(t['print_sspec_to_ituff'].get_fitem(r0=pFail(setbin=self.bin(314502, offset), ret=0),
                                                                      r1=pPass(ret=3)))
        retest_exec_composite = Flow('RETEST_EXEC', *retest_exec_fitems)
        
        qa_fused_fitems = []
        qa_fused_fitems.append(t['check_ecc_status'].get_fitem(r0=pFail(setbin=self.bin(314300, offset), ret=0),
                                                               r2=pFail(setbin=self.bin(314301, offset), ret=0),
                                                               r3=pFail(setbin=self.bin(314302, offset), ret=0),
                                                               r4=pFail(setbin=self.bin(314303, offset), ret=0),
                                                               r5=pFail(setbin=self.bin(314304, offset), ret=0)
                                                               ))
        qa_fused_fitems.append(t['efuse_read'].get_fitem(r0=pFail(setbin=self.bin(314129, offset), ret=0),
                                                         r2=pFail(setbin=self.bin(314130, offset), ret=0),
                                                         r3=pFail(setbin=self.bin(314131, offset), ret=0)
                                                         ))
        #qa_fused_fitems.append(t['efuse_read_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314195, offset), ret=0),
        #                                                      r2=pFail(setbin=self.bin(314196, offset), ret=0),
        #                                                      r3=pFail(setbin=self.bin(314197, offset), ret=0)
        #                                                      ))
        qa_fused_fitems.append(t['fuse_efuse_compare'].get_fitem(r0=pFail(setbin=self.bin(314112, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(314113, offset), ret=0),
                                                                 r3=pFail(setbin=self.bin(314114, offset), ret=0),
                                                                 r4=pFail(setbin=self.bin(314115, offset), ret=0),
                                                                 r5=pFail(setbin=self.bin(314116, offset), ret=0),
                                                                 r6=pFail(setbin=self.bin(314117, offset), ret=0),
                                                                 r7=pFail(setbin=self.bin(314118, offset), ret=0),
                                                                 r8=pFail(setbin=self.bin(314119, offset), ret=0),
                                                                 r9=pFail(setbin=self.bin(314120, offset), ret=0),
                                                                 r10=pFail(setbin=self.bin(314121, offset), ret=0)
                                                                ))
        qa_fused_fitems.append(t['dff_ult_efuse_compare'].get_fitem(r0=pFail(setbin=self.bin(314305, offset), ret=0),
                                                                    r2=pFail(setbin=self.bin(314306, offset), ret=0)))
        qa_fused_fitems.append(t['dff_ult_efuse_compare_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314307, offset), ret=0),
                                                                         r2=pFail(setbin=self.bin(314308, offset), ret=0)))
        qa_fused_composite = Flow('QA_FUSED', *qa_fused_fitems)
        
        margins_read_fitems = []
        margins_read_fitems.append(t['ir_margins'].get_fitem(r0=pFail(ctr=self.bin(314127, offset),ret=0),
                                                             r1=pPass(goto='NEXT')))
        margins_read_fitems.append(t['ir_margins_cpu1'].get_fitem(r0=pFail(ctr=self.bin(314128, offset),ret=0),
                                                                  r1=pPass(ret=0)))
        margins_read_composite = Flow('MARGINS_READ', *margins_read_fitems)
        
        reset_fail_flow_fitems = []
        reset_fail_flow_fitems.append(t['babysteps_tests'].get_fitem(r0=pFail(ctr=self.bin(314006, offset), goto='NEXT'),
                                                                     r2=pFail(ctr=self.bin(314007, offset), goto='NEXT'),
                                                                     r3=pPass(ctr=self.bin(314008, offset), goto='NEXT'),
                                                                     r4=pFail(ctr=self.bin(314009, offset), goto='NEXT'),
                                                                     r5=pFail(ctr=self.bin(314010, offset), goto='NEXT')
                                                                     ))
        reset_fail_flow_fitems.append(t['fsm_babysteps_tests'].get_fitem(r0=pFail(ctr=self.bin(314011, offset), ret=1),
                                                                         r2=pFail(ctr=self.bin(314012, offset), ret=1),
                                                                         r3=pPass(ctr=self.bin(314013, offset), ret=1),
                                                                         r4=pFail(ctr=self.bin(314014, offset), ret=1),
                                                                         r5=pFail(ctr=self.bin(314015, offset), ret=1)
                                                                         ))
        reset_fail_flow_composite = Flow('RESET_FAIL_FLOW', *reset_fail_flow_fitems)


        startcpunom_fitems = []
        startcpunom_fitems.append(Fitem('SAME', preread_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto=functional_test_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', functional_test_composite, r0=pFail(goto=reset_fail_flow_composite.name), r1=pPass(goto=fuse_read_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', fuse_read_composite, r0=pFail(ret=0), r1=pPass(goto=retest_exec_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', retest_exec_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pFail(goto=reset_fail_flow_composite.name), r3=pPass(goto=qa_fused_composite.name), r4=pFail(goto=margins_read_composite.name)))        
        startcpunom_fitems.append(Fitem('SAME', qa_fused_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pFail(goto=margins_read_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', margins_read_composite, r0=pFail(ret=0), r1=pPass(ret=0)))
        startcpunom_fitems.append(Fitem('SAME', reset_fail_flow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))

        Flow(flow_name,*startcpunom_fitems)

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
        t['read_margin_setup'] = PrimePatConfigTestMethod_TestBuilder(name='read_margin_setup',  BypassPort=-1, **dparams)
        
        ##Flow Setup
        init_fitems = []
        init_fitems.append(t['read_margin_setup'].get_fitem(r0=pFail(ret=0), r1=pPass(ret=1)))

        Flow(flow_name,*init_fitems)


class CDIE_816_SORT(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='sort')
        self.LevelsTc = 'BASE::SBF_nom_lvl'
        self.TimingsTc = 'BASE::cpu_ctf_timing_tclk100_hclk100_bclk400'
        self.PrePlist = None

    def initialize(self, name1, name2, rev):
        #Import("FUS_FUSEREAD_CXX.usrv")
        InitializeNVLSort(name1, name2, defaultrm1bin=-44, defaultrm2bin=-44, binrange=[(4400, 4450)])
        MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        # Add the necessary files to import in your mtpl
        Import("FUS_FUSEREAD.usrv")

class CDIE_816_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        self.TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100'
        self.PrePlist = ''

    def initialize(self, name1, name2, rev):

        InitializeNVLClass(name1, name2, defaultrm1bin=[(98312500,98313999),(98922500,98923999)], defaultrm2bin=[(99312500,99313999),(99922500,99923999)], binrange=[(3140, 9093)])
        MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        Import("FUS_FUSEREAD_CXX.usrv")

rev = '25ww13p2_rev1'

#cdie = CDIE_816_SORT()
#cdie.initialize('./PyMTPL_OUTPUT/CDIE_SORT/FUS_FUSEBURN_CXX', 'FUS_FUSEBURN_CXX', rev)
#cdie.get_fact_flow('FUS_FUSEBURN_CXX_FACT')

cdie = CDIE_816_CLASS()
cdie.initialize('./FUS_FUSEREAD_CXX', 'FUS_FUSEREAD_CXX', rev)
cdie.get_init_flow('FUS_FUSEREAD_CXX_INIT')
cdie.get_start_flow('FUS_FUSEREAD_CXX_STARTCPUNOM')