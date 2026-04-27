# Import the necessary classes from Pymtpl
import copy
import re, json

from pymtpl.por_methods import PrimePatConfigTestMethod, PrimeVirtualFuseExportToSharedStorageTestMethod, ScreenTC
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

class PrimePatConfigTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUSECONFIG_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/FUS_FUSECFG_C2X.SetPoints.json","./InputFiles/FUS_FUSECFG_C1X.SetPoints.json")'),
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimePatConfigTestMethod(**param)

class ScreenTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False, test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_SCREENTC_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ScreenTestsFile': "./InputFiles/FUSECFG_CKX.screen.json",
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = ScreenTC(**param)
        
class PrimeVirtualFuseExportToSharedStorageTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)

      
        if name == 'set_hcs_fds_cpu1':
            reg = 'CPU1'
        else:
            reg = 'CPU0'

        param = {
            'name': f'FUSE_X_UF_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'Tags': f'',
            'HcsSharedStorageKey': f'{reg}_FUSE_EMB_VFDM_HCS_BINARY',
	        'FdsSharedStorageKey': f'{reg}_FUSE_EMB_VFDM_FDS_BINARY',
	        'FuseDataGap': f'{reg}.VF_Heap_Data_Gap.VF_Heap_Data_Gap',
	        'FuseDescriptorGap': f'{reg}.VF_Heap_Descriptor_Gap.VF_Heap_Descriptor_Gap',


        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeVirtualFuseExportToSharedStorageTestMethod(**param)


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


        # tests for INIT / DIRECT_FUSES
        t['pkg_setpoint_setup'] =  ScreenTC_TestBuilder(name='pkgsetpoint_setup', ScreenTestSet='PKG_SetPoint_Setup', BypassPort=-1, **dparams)
        t['frv_direct_all_exe_x1'] = PrimePatConfigTestMethod_TestBuilder(name='frv_direct_all_exe_x1', SetPoint=Spec('FUS_FUSECFG_CKX::FUS_FUSECFG_CKX.PKG_DF_SETPOINT'), RegEx='[gdx].......C........_.._......._(N...HC|....AF|....AH)......._...C................*', BypassPort=-1, **dparams)
        t['frv_direct_all_exe_x1_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='frv_direct_all_exe_x1_cpu1', SetPoint=Spec('__shared__::TpRule.If_S52_S52CB_DNL52CB("DIRECT_FUSES_CONFIG_RATIO1_S52C_CPU1","DIRECT_FUSES_CONFIG_RATIO1_S52CB_CPU1","DIRECT_FUSES_CONFIG_RATIO1_DNL_S52CB_CPU1","DIRECT_FUSES_CONFIG_RATIO1_S52C_CPU")'), RegEx='[gdx].......C........_.._......._(N...HB|....AF|....AH)......._...C................*', BypassPort=Spec("__shared__::TpRule.If_MICP(-1,1)"), **dparams)
        
        # tests for INIT / VIRTUAL_FUSES
        t['frv_virtual_all_exe_x1'] = PrimePatConfigTestMethod_TestBuilder(name='frv_virtual_all_exe_x1', SetPoint=Spec('FUS_FUSECFG_CKX::FUS_FUSECFG_CKX.PKG_VF_SETPOINT'), RegEx='[gdx].......C........_.._......._(N...HC|....AF|....AH)......._...C................*', BypassPort=-1, **dparams)
        t['frv_virtual_all_exe_x1_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='frv_virtual_all_exe_x1_cpu1', SetPoint=Spec('__shared__::TpRule.If_S52_S52CB_DNL52CB("VIRTUAL_FUSES_CONFIG_RATIO1_S52C_CPU1","VIRTUAL_FUSES_CONFIG_RATIO1_S52CB_CPU1","VIRTUAL_FUSES_CONFIG_RATIO1_DNL_S52CB_CPU1","VIRTUAL_FUSES_CONFIG_RATIO1_S52C_CPU1")'), RegEx='[gdx].......C........_.._......._(N...HB|....AF|....AH)......._...C................*', BypassPort=Spec("__shared__::TpRule.If_MICP(-1,1)"), **dparams)
        
        # tests for INIT / RESET_FUSES
        t['frv_reset_all_exe_x1'] = PrimePatConfigTestMethod_TestBuilder(name='frv_reset_all_exe_x1', SetPoint=Spec('FUS_FUSECFG_CKX::FUS_FUSECFG_CKX.PKG_RF_SETPOINT'), RegEx='[gdx].......C........_.._......._(N...HC|.....AF|....AH)......._...C................*', BypassPort=-1, **dparams)
        t['frv_reset_all_exe_x1_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='frv_reset_all_exe_x1_cpu1', SetPoint=Spec('__shared__::TpRule.If_S52_S52CB_DNL52CB("RESET_FUSES_CONFIG_RATIO1_S52C_CPU1","RESET_FUSES_CONFIG_RATIO1_S52CB_CPU1","RESET_FUSES_CONFIG_RATIO1_DNL_S52CB_CPU1","RESET_FUSES_CONFIG_RATIO1_S52C_CPU1")'), RegEx='[gdx].......C........_.._......._(N...HB|.....AF|....AH)......._...C................*', BypassPort=Spec("__shared__::TpRule.If_MICP(-1,1)"), **dparams)
        

        init_fitems = []
        init_fitems.append(t['pkg_setpoint_setup'].get_fitem(r0=pFail(ret=0),
                                                             r2=pFail(ret=0),
                                                             r3=pFail(ret=0),
                                                             r4=pFail(ret=0),
                                                             r5=pFail(ret=0),
                                                             r6=pFail(ret=0),
                                                             r7=pFail(ret=0),
                                                             r8=pFail(ret=0),
                                                             r9=pFail(ret=0),
                                                             r10=pFail(ret=0)))
        init_fitems.append(t['frv_direct_all_exe_x1'].get_fitem(r0=pFail(ret=0)))
        init_fitems.append(t['frv_direct_all_exe_x1_cpu1'].get_fitem(r0=pFail(ret=0)))
        init_fitems.append(t['frv_virtual_all_exe_x1'].get_fitem(r0=pFail(ret=0)))
        init_fitems.append(t['frv_virtual_all_exe_x1_cpu1'].get_fitem(r0=pFail(ret=0)))
        init_fitems.append(t['frv_reset_all_exe_x1'].get_fitem(r0=pFail(ret=0)))
        init_fitems.append(t['frv_reset_all_exe_x1_cpu1'].get_fitem(r0=pFail(ret=0)))
       
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


        # tests for STARTCPUNOM / VFDM
        t['set_hcs_fds'] =  PrimeVirtualFuseExportToSharedStorageTestMethod_TestBuilder(name='set_hcs_fds', Namespace='CPU0', BypassPort=-1, **dparams)
        t['set_hcs_fds_cpu1'] =  PrimeVirtualFuseExportToSharedStorageTestMethod_TestBuilder(name='set_hcs_fds_cpu1', Namespace='CPU1', BypassPort=Spec("__shared__::TpRule.If_MICP(-1,1)"), **dparams)
         
        # tests for STARTCPUNOM
        t['clear_perunit_reset_x1'] = PrimePatConfigTestMethod_TestBuilder(name='clear_perunit_reset_x1', SetPoint=Spec('FUS_FUSECFG_CKX::FUS_FUSECFG_CKX.PKG_RF_SETPOINT'), RegEx='[gdx].......C........_.._......._(N...HC|....AF|....AH)......._...C................*', BypassPort=-1, **dparams)
        t['clear_perunit_reset_x1_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='clear_perunit_reset_x1_cpu1', SetPoint=Spec('__shared__::TpRule.If_S52_S52CB_DNL52CB("RESET_FUSES_CONFIG_RATIO1_S52C_CPU1","RESET_FUSES_CONFIG_RATIO1_S52CB_CPU1","RESET_FUSES_CONFIG_RATIO1_DNL_S52CB_CPU1","RESET_FUSES_CONFIG_RATIO1_S52C_CPU1")'), RegEx='[gdx].......C........_.._......._(N...HB|....AF|....AH)......._...C................*', BypassPort=Spec("__shared__::TpRule.If_MICP(-1,1)"), **dparams)
        t['clear_perunit_vfdm'] = PrimePatConfigTestMethod_TestBuilder(name='clear_perunit_vfdm', SetPoint='CPU0_APPLY_VFDM', RegEx='[gdx].......C........_.._......._(N...HC|....AF|....AH)......._...C................*', ConfigurationFile=Spec('GetEnvironmentVariable("FUSE_ROOT_DIR_CPU")+"./CSP/array_repair_perunit.PatConfigSetpoints.json"'), BypassPort=-1, **dparams)
        t['clear_perunit_vfdm_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='clear_perunit_vfdm_cpu1', SetPoint='CPU1_APPLY_VFDM', RegEx='[gdx].......C........_.._......._(N...HB|....AF|....AH)......._...C................*', ConfigurationFile=Spec('GetEnvironmentVariable("FUSE_ROOT_DIR_CPU")+"./CSP/array_repair_perunit.PatConfigSetpoints.json"'), BypassPort=Spec("__shared__::TpRule.If_MICP(-1,1)"), **dparams)
       

        ##Flow Setup
        vfdm_fitems = []
        vfdm_fitems.append(t['set_hcs_fds'].get_fitem(r0=pFail(setbin=self.bin(314620, offset), ret=0),
                                                      r2=pFail(setbin=self.bin(314621, offset), ret=0),
                                                      r3=pFail(setbin=self.bin(314622, offset), ret=0)))
        vfdm_fitems.append(t['set_hcs_fds_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314623, offset), ret=0),
                                                      r2=pFail(setbin=self.bin(314624, offset), ret=0),
                                                      r3=pFail(setbin=self.bin(314625, offset), ret=0)))
        vfdm_composite = Flow('VFDM', *vfdm_fitems)

        startcpupatmodspkg_fitems = []
        startcpupatmodspkg_fitems.append(Fitem('SAME', vfdm_composite, r0=pFail(ret=0)))
        startcpupatmodspkg_fitems.append(t['clear_perunit_reset_x1'].get_fitem(r0=pFail(setbin=self.bin(314720, offset), ret=0)))
        startcpupatmodspkg_fitems.append(t['clear_perunit_reset_x1_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314724, offset), ret=0)))
        startcpupatmodspkg_fitems.append(t['clear_perunit_vfdm'].get_fitem(r0=pFail(setbin=self.bin(314721, offset), ret=0)))
        startcpupatmodspkg_fitems.append(t['clear_perunit_vfdm_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314722, offset), ret=0)))
        Flow(flow_name,*startcpupatmodspkg_fitems)

class CDIE_816_SORT(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='sort')
        self.LevelsTc = 'BASE::SBF_nom_lvl'
        self.TimingsTc = 'BASE::cpu_fun_timing_vctr0100MTs_hvmclk100_tck100r1_tstprtclk050r2'
        self.PrePlist = None

    def initialize(self, name1, name2, rev):
        Import("FUS_FUSECFG_CXX.usrv")
        InitializeNVLSort(name1, name2, defaultrm1bin=(98312000,98313999), defaultrm2bin=(99312000,99313999), binrange=[(3100, 3199)])
        MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        
        # Add the necessary files to import in your mtpl
        

class CDIE_816_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min'
        self.TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_vctr0100MTs_hvmclk100_tck100r1_tstprtclk050r2'
        self.PrePlist = ''

    def initialize(self, name1, name2, bomgroup):
        #Import("FUS_FUSECFG_CKX.usrv")
        InitializeNVLClass(name1, name2, defaultrm1bin=-31, defaultrm2bin=-31, binrange=[(3140, 3149)])
        #MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        Import("FUS_FUSECFG_CKX.usrv")
        
#define bomgroup SD - SingleDie, DD - DualDie
bomgroup = 'SD'

#cdie = CDIE_816_SORT()
#cdie.initialize('./FUS_FUSECFG_CXX', 'FUS_FUSECFG_CXX', rev)
#cdie.get_init_flow('FUS_FUSECFG_CXX_INIT')
#cdie.get_start_flow('FUS_FUSECFG_CXX_START')

#cdie = CDIE_816_CLASS()
#cdie.initialize('./FUS_FUSECFG_C2X', 'FUS_FUSECFG_CXX', bomgroup)
#cdie.get_init_flow('FUS_FUSECFG_CXX_INIT')
#cdie.get_start_flow('FUS_FUSECFG_CXX_STARTCPUNOM')

#cdie = CDIE_816_CLASS()
#cdie.initialize('./FUS_FUSECFG_C1X', 'FUS_FUSECFG_CXX', bomgroup)
#cdie.get_init_flow('FUS_FUSECFG_CXX_INIT')
#cdie.get_start_flow('FUS_FUSECFG_CXX_STARTCPUNOM')

cdie = CDIE_816_CLASS()
cdie.initialize('./FUS_FUSECFG_CKX', 'FUS_FUSECFG_CKX', bomgroup)
cdie.get_init_flow('FUS_FUSECFG_CKX_INIT')
cdie.get_start_flow('FUS_FUSECFG_CKX_STARTCPUPATMODSPKG')