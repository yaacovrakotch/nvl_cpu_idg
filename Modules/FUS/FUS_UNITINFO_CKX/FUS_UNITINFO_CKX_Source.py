# Import the necessary classes from Pymtpl
import copy
import re, json

from pymtpl.por_methods import PrimePatConfigTestMethod, ScreenTC, AuxiliaryTC, PrimeCtvDecoderTestMethod, PrimeFuseReadMaskUltDecodeTestMethod, PrimeFunctionalTestMethod
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
            'ScreenTestsFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/UNITINFO_CK2X.screen.json","./InputFiles/UNITINFO_CK1X.screen.json")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = ScreenTC(**param)

class PrimePatConfigTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUSECONFIG_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/UNITINFO_CK2X.patConfigSetpoints.json","./InputFiles/UNITINFO_CK1X.patConfigSetpoints.json")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimePatConfigTestMethod(**param)

class PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_ULTREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': f'./InputFiles/UNITINFO_CXX.fuseReadMask.json',
            'SkipPatternExecute': f'DISABLED',
            'DieIdNames': Spec('__shared__::TpRule.If_MICP("__shared__::DFFVars.DIEID_CPU, __shared__::DFFVars.DIEID_CPU1"),"__shared__::DFFVars.DIEID_CPU", '),
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0_MAIN,CPU1_MAIN","CPU0_MAIN")'), 
            'ByPassPort': f'-1'
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
            'ByPassPort': f'-1'
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
            'ByPassPort': f'-1',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/UNITINFO_C2X_PIC8_PrimeCtvDecoderTestMethod.csv","./InputFiles/UNITINFO_C1X_PIC8_PrimeCtvDecoderTestMethod.csv")'),
            'CtvCapturePins': Spec('__shared__::TpRule.If_MICP("IPC::CPU_TDO, IPC::CPU1_TDO","IPC::CPU_TDO")'),
            'Dieid_Rename': f' ' 
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeCtvDecoderTestMethod(**param)



class CDIE_BASE:
    def __init__(self,sort_class):
        self.sort_class = sort_class
        self.LevelsTc = None
        self.TimingsTc = None
        
        
    def bin(self, _bin, _offset=0):
        _bin_str = str(_bin+_offset)
        if len(_bin_str) != 6:
            raise Exception('invalid bin')
        if not _bin_str.startswith('31'):
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


        # tests for INIT / FUSE_CONFIG_PREP
        t['unlock_setup'] = ScreenTC_TestBuilder(name='unlock_setup', ScreenTestSet='LEG_KEY_split_by_32bits_MsbToLsb', BypassPort=-1, **dparams)
        t['legacy_setup_exe_x1'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_setup_exe_x1', SetPoint='LGULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        

        ##Flow Setup
        fuse_config_prep_fitems = []
        fuse_config_prep_fitems.append(t['unlock_setup'].get_fitem(r0=pFail(ret=0)))
        fuse_config_prep_fitems.append(t['legacy_setup_exe_x1'].get_fitem(r0=pFail(ret=0)))
        fuse_config_prep_composite = Flow('FUSE_CONFIG_PREP', *fuse_config_prep_fitems)

        init_fitems = []
        init_fitems.append(Fitem('SAME', fuse_config_prep_composite, r0=pFail(ret=0), r1=pPass(ret=1)))

        Flow(flow_name,*init_fitems)


    def get_start_flow(self, flow_name, module_name='STARTCPUPATMODSPKG', is_edc=False,  bin_offset=0, bin_offset2=0, composite_postfix=None, test_instance_postfix=None):
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


        # tests for STARTCPUPATMODSPKG
        t['lockstatus_check'] =  AuxiliaryTC_TestBuilder(name='lockstatus_check', DataType='String', Expression = "[G.U.S.LCKSTATUS_CPU0]='RDUL_CPU0'", ResultPort = '[R]?1:2', Storage='SharedStorage', **dparams)

        # tests for STARTCPUPATMODSPKG/LEGACY_UNLOCK
        t['unlock_setup'] =  ScreenTC_TestBuilder(name='unlock_setup', ScreenTestSet='LEG_KEY_split_by_32bits_MsbToLsb', **dparams)
        t['legacy_unlock_x1'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock_x1', SetPoint='LGULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        
        # tests for STARTCPUPATMODSPKG/RED_UNLOCK
        t['red_unlock_setup'] =  ScreenTC_TestBuilder(name='red_unlock_setup', ScreenTestSet='RED_KEY_split_by_32bits_MsbToLsb', **dparams)
        t['red_unlock_x1'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock_x1', SetPoint='RDULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        

        ##Flow Setup
        legacy_unlock_fitems = []
        legacy_unlock_fitems.append(t['unlock_setup'].get_fitem(r0=pFail(setbin=self.bin(314850, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(314851, offset), ret=0),
                                                                r3=pFail(setbin=self.bin(314852, offset), ret=0),
                                                                r4=pFail(setbin=self.bin(314853, offset), ret=0)))
        legacy_unlock_fitems.append(t['legacy_unlock_x1'].get_fitem(r0=pFail(setbin=self.bin(314730, offset), ret=0)))
        legacy_unlock_composite = Flow('LEGACY_UNLOCK', *legacy_unlock_fitems)

        

        red_unlock_fitems = []
        red_unlock_fitems.append(t['red_unlock_setup'].get_fitem(r0=pFail(setbin=self.bin(314854, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(314855, offset), ret=0)))
        red_unlock_fitems.append(t['red_unlock_x1'].get_fitem(r0=pFail(setbin=self.bin(314731, offset), ret=0)))
        red_unlock_composite = Flow('RED_UNLOCK', *red_unlock_fitems)

        

        startcpupatmodspkg_fitems = []
        #fact_fitems.append(t['z0_a0_check'].get_fitem(r0=pFail(setbin=self.bin(310058, offset),ret=0), r2=pPass(ret=1)))
        startcpupatmodspkg_fitems.append(t['lockstatus_check'].get_fitem(r0=pFail(setbin=self.bin(314058, offset),ret=0), r1=pPass(goto=red_unlock_composite.name), r2=pPass(goto=legacy_unlock_composite.name)))
        startcpupatmodspkg_fitems.append(Fitem('SAME', red_unlock_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        startcpupatmodspkg_fitems.append(Fitem('SAME', legacy_unlock_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
       
        Flow(flow_name,*startcpupatmodspkg_fitems)

    

class CDIE_816_SORT(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='sort')
        self.LevelsTc = 'BASE::SBF_nom_lvl'
        self.TimingsTc = 'BASE::cpu_ctf_timing_tclk100_hclk100_bclk400'
        self.PrePlist = None

    def initialize(self, name1, name2, rev):
        Import("FUS_UNITINFO_CXX.usrv")
        InitializeNVLSort(name1, name2, defaultrm1bin=-31, defaultrm2bin=-31, binrange=[(3100, 3199)])
        MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        
        # Add the necessary files to import in your mtpl
        

class CDIE_816_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        self.TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100'
        self.PrePlist = ''

    def initialize(self, name1, name2, rev):
        #Import("FUS_UNITINFO_CXX.usrv")
        InitializeNVLClass(name1, name2, defaultrm1bin=(98312000,98313999), defaultrm2bin=(99312000,99313999), binrange=[(3140, 3149)])
        #MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        
rev = 0
bomgroup = 'SD'

#cdie = CDIE_816_SORT()
#cdie.initialize('./FUS_FUSECFG_CXX', 'FUS_FUSECFG_CXX', rev)
#cdie.get_init_flow('FUS_FUSECFG_CXX_INIT')
#cdie.get_start_flow('FUS_FUSECFG_CXX_START')

cdie = CDIE_816_CLASS()
cdie.initialize('./FUS_UNITINFO_CKX', 'FUS_UNITINFO_CKX', rev)
cdie.get_init_flow('FUS_UNITINFO_CKX_INIT')
cdie.get_start_flow('FUS_UNITINFO_CKX_STARTCPUPATMODSPKG')

#cdie = CDIE_816_CLASS()
#cdie.initialize('./FUS_UNITINFO_C1X', 'FUS_UNITINFO_CXX', bomgroup)
#cdie.get_init_flow('FUS_UNITINFO_CXX_INIT')
#cdie.get_start_flow('FUS_UNITINFO_CXX_STARTCPUNOM')
#cdie.get_failflow_flow('FUS_UNITINFO_CXX_CPUIPFF')

#cdie = CDIE_816_CLASS()
#cdie.initialize('./FUS_UNITINFO_C2X', 'FUS_UNITINFO_CXX', bomgroup)
#cdie.get_init_flow('FUS_UNITINFO_CXX_INIT')
#cdie.get_start_flow('FUS_UNITINFO_CXX_STARTCPUNOM')
#cdie.get_failflow_flow('FUS_UNITINFO_CXX_CPUIPFF')