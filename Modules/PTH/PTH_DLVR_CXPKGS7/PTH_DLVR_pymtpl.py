#####################This is for PTH_DLVR Module###############################

import copy
import re, json

from pymtpl.por_methods import AnalogDcTC, CtvDecoderSpm, DlvrTrimCalc, PTHGetSetGsdsDffTC, PowerSequenceHandler, PrimeFunctionalTestMethod, PrimePatConfigTestMethod, ScreenTC, VminPass2FailTC, VminTC, BaseMethod, required, optional
from pymtpl.core import Flow, Fitem, pPass, pFail, InitializeNVLClass, NativeMultiTrial, AUTO, Import, TrialParamSpec, Spec
from pymtpl.uservars import UserVars
from pymtpl.helpers import inputfile

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

class CtvDecoderSpm(BaseMethod):
	def __init__(self,
				 name,
				 BypassPort=required,
				 LevelsTc = required,
				 Patlist = required,
				 TimingsTc = required,
				 ConfigurationFile = required,
				 CtvCapturePins = required,
				 ApplyEndSequence = optional,
				 _comment=None,                 # required, do not omit
				 _fitem=None,                   # required, do not omit
				 **kwargs                       # required, do not omit
				 ):
		self._init(name, locals())

class DlvrTrimCalc(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=required,
	             ConfigFile = required,
                 ConfigSet = required,
	             Mode = required,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

class PTHGetSetGsdsDffTC(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=required,
	             ConfigurationFile = required,
                 OPType = required,
	             PreInstance = required,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

class PrimePatConfigTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort = optional,
	             ConfigurationFile = required,
                 SetPoint = required,
	             RegEx = optional,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

class AnalogDcTC(BaseMethod):
	def __init__(self,
				 name,
				 DataBaseFile = required,
				 BypassPort=required,
				 LevelsTc = required,
				 TimingsTc = required,
				 Patlist = required,
				 Pins = required,
				 MeasurementTypes = required,
				 TriggerMapName = required,
				 DatalogLevel = required,
				 FlushLevels = required,
				 ExpectedBits = required,
				 CtvPins = required,
				 ParallelCtvProcessing = 'DISABLED',
				 _comment=None,                 # required, do not omit
				 _fitem=None,                   # required, do not omit
				 **kwargs                       # required, do not omit
				 ):
		self._init(name, locals())

class VminTC(BaseMethod):
    def __init__(self,
                 name,
                 EndVoltageLimits = required,
                 StartVoltages = required,
                 StepSize = required,
	             TestMode = required,
    			 VoltageTargets = required,
                 VminResult = required,
                 LevelsTc = required,
    			 Patlist = required,
                 TimingsTc = required,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

class VminPass2FailTC(BaseMethod):
    def __init__(self,
                 name,
                 EndVoltage = required,
                 FivrCondition = required,
                 StepSize = required,
	             StartVoltage = required,
    			 VoltageTargets = required,
                 VminResult = required,
                 LevelsTc = required,
                 Patlist = required,
                 TimingsTc = required,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

class ScreenTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_SCREEN_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = ScreenTC(**param)

class PrimeFunctionalTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_FUNC_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFunctionalTestMethod(**param)

class CtvDecoderSpm_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_CMEM_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = CtvDecoderSpm(**param)

class DlvrTrimCalc_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_SCREEN_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = DlvrTrimCalc(**param)

class PTHGetSetGsdsDffTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_SCREEN_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PTHGetSetGsdsDffTC(**param)

class PrimePatConfigTestMethodFuseConfig_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_FUSECONFIG_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimePatConfigTestMethod(**param)

class PrimePatConfigTestMethodPatmod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_PATMOD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimePatConfigTestMethod(**param)

class AnalogDcTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_ANAMEAS_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = AnalogDcTC(**param)

class VminTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_VMIN_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = VminTC(**param)

class PowerSequenceHandler_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'CTRL_X_DLVR_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PowerSequenceHandler(**param)

class VminPass2FailTC_TestBuilder(TestConfig):
    def __init__(self, name, module_name, is_edc=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=is_edc)
        param = {
            'name': f'DLVR_X_VMIN_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = VminPass2FailTC(**param)

IPCtiming = 'CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100'
PKGtiming = 'BASE::pkg_cpu_fun_timing_mts100_tstprtclk50_tck100'

class CDIE_BASE:
    def __init__(self,sort_class):
        self.sort_class = sort_class
        self.LevelsTc = None
        self.TimingsTc = None
        self.TimingsTC = None

    def bin(self, _bin, _offset=0):
        _bin_str = str(_bin+_offset)
        if len(_bin_str) != 6:
            raise Exception('invalid bin')
        if not _bin_str.startswith('19') and not _bin_str.startswith('71'):
            raise Exception('invalid bin')
        hard_bin = _bin_str[0:2]
        soft_bin = _bin_str[2:4]
        counter = _bin_str[4:6]

        final_bin = None
        if self.sort_class == 'sort':
            final_bin = int(f'{hard_bin}{soft_bin}{soft_bin}{counter}')
        else:
            final_bin = int(f'90{hard_bin}{soft_bin}{str(counter).zfill(2)}')

        # return AUTO
        return final_bin
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ IPC MODULE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#==============================================================================S28C/HX28C/DNL S28C=====================================================================================================
    def get_816_startana1cpu_flow(self, flow_name, module_name='STARTANA1CPU', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        ctvdecoder = CtvDecoderSpm_TestBuilder
        gsdsdff = PTHGetSetGsdsDffTC_TestBuilder
        patmod = PrimePatConfigTestMethodPatmod_TestBuilder
        fuseconfig = PrimePatConfigTestMethodFuseConfig_TestBuilder
        dlvrtrim = DlvrTrimCalc_TestBuilder
        func = PrimeFunctionalTestMethod_TestBuilder
        screentc = ScreenTC_TestBuilder
        analogdctc = AnalogDcTC_TestBuilder
        vmintc = VminTC_TestBuilder
        vminpass2failtc = VminPass2FailTC_TestBuilder
        power = PowerSequenceHandler_TestBuilder
        dparams = {
            'module_name': module_name,
        }
        ##dparam used for killed test



        ### list of tests
        t['tap2reg_dump'] = ctvdecoder(is_edc=True, name='tap2reg_dump', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_TAP2REG_DUMP.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_regdump_list', TimingsTc=IPCtiming, **dparams)
        t['pwrgood_chk'] = ctvdecoder(is_edc=True, name='pwrgood_chk', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_PWRGOOD_CHK.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_OBS_06', Patlist='pth_dlvr_pwrgood_list', TimingsTc=IPCtiming, **dparams)
        t['regcheck'] = func(is_edc=True, name='regcheck', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_reg_check_list', TimingsTc=IPCtiming, **dparams)
        t['gsds_inject'] = dlvrtrim(is_edc=True, name='gsds_inject', BypassPort= 1, ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='GSDS_INJECT', Mode='IREF_TRIM', **dparams)
        t['setgsds'] = gsdsdff(is_edc=True, name='setgsds', ConfigurationFile = Spec('PTH_DLVR_CXPKGS7_Rules.Select_RCCOLD ("./InputFiles/PTHGSDS_NVL_S28C_DFF2GSDS_RC.json","./InputFiles/PTHGSDS_NVL_S28C_DFF2GSDS.json")'), OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), **dparams)
        t['binconv_prim'] = dlvrtrim(is_edc=True, name='binconv_prim', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='BINCONV_PRIM', Mode='IREF_TRIM', **dparams)
        t['binconv_all'] = dlvrtrim(is_edc=True, name='binconv_all', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='BINCONV_ALL', Mode='IREF_TRIM', **dparams)
        t['default'] = fuseconfig(is_edc=False, name='default', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='DLVR_FUSE_ALL_1', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['open_loop'] = patmod(is_edc=False, name='open_loop', ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_PATMOD.setpoints.json', SetPoint='PS0_0V', **dparams)
        t['voutmeas'] = analogdctc(is_edc=True, name='voutmeas', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_VOUTMEAS.json', Patlist='pth_dlvr_vout_float_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['voutmeas_calc'] = dlvrtrim(is_edc=True, name='voutmeas_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='VOUTMEAS', Mode='IREF_TRIM', **dparams)
        t['cmem_lvr_max_alladc1_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_alladc1_ch1', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ANAPRB_LVR_ADC1_CH1.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_anaprb_bglvr_allch1_adc1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_alladc1_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_alladc1_ch0', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ANAPRB_LVR_ADC1_CH0.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_anaprb_bglvr_allch0_adc1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2dis_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2dis_ch0', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_CH0.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch0_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2dis_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2dis_ch1', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_CH1.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2ena_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2ena_ch0', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_L2EN_CH0.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch0L2en_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2ena_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2ena_ch1', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_L2EN_CH1.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch1L2en_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsadconly_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsadconly_ch1', BypassPort= 1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSBGBUFADC0.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsgbugadc0_list', TimingsTc=IPCtiming, **dparams)
        t['lvr_adc_read'] = dlvrtrim(is_edc=True, name='lvr_adc_read', BypassPort= 1, ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='LVR', Mode='IREF_TRIM', **dparams)
        t['anaprb_mrcsx'] = ctvdecoder(is_edc=True, name='anaprb_mrcsx', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ANAPRB_MRCSX.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_mr_csx_amp_list', TimingsTc=IPCtiming, **dparams)
        t['anaprb_irefgen'] = ctvdecoder(is_edc=True, name='anaprb_irefgen', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ANAPRB_IREFGEN.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_irefgen_list', TimingsTc=IPCtiming, **dparams)
        t['intlvr_sweep'] = ctvdecoder(is_edc=True, name='intlvr_sweep', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_INTLVR_DACSEL_SWEEP.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_intlvr_dacsel_sweep_list', TimingsTc=IPCtiming, **dparams)
        t['anaprb_lvr'] = analogdctc(is_edc=True, name='anaprb_lvr', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_ANAPRB_LVR.json', Patlist='pth_dlvr_anaprb_bglvr_list', Pins='IPC::CPU_OBS_02,IPC::CPU_OBS_03', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('960'), CtvPins='CPU_TDO', **dparams)
        t['anaprb_lvr_calc'] = dlvrtrim(is_edc=True, name='anaprb_lvr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='ANAPRB_LVR', Mode='IREF_TRIM', **dparams)
        t['pod_vih'] = vmintc(is_edc=True, name='pod_vih', EndVoltageLimits='0.7', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_pod_vih_list', StartVoltages='0.3', StepSize=Spec('0.05'), TestMode='SingleVmin', TimingsTc=IPCtiming, VoltageTargets='VCCIA', VminResult='CPU_POD_VIH', **dparams)
        t['pod_vil'] = vminpass2failtc(is_edc=True, name='pod_vil', Patlist='pth_dlvr_pod_vih_list', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P0V_MIN', TimingsTc=IPCtiming, VoltageTargets='VCCIA', FivrCondition='', StartVoltage='0.5', EndVoltage='0.2', StepSize=Spec('-0.05'), VminResult='CPU_POD_VIL', **dparams)
        t['pod'] = dlvrtrim(is_edc=True, name='pod', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='POD', Mode='IREF_TRIM', **dparams)
        t['hvls'] = ctvdecoder(is_edc=True, name='hvls', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_HVLS.csv', CtvCapturePins='CPU_OBS_07', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_hvls_list', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_manual'] = ctvdecoder(is_edc=True, name='iref_pt1_manual', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_MANUAL_IREF_PT1.csv', CtvCapturePins='CPU_OBS_06', Patlist='pth_dlvr_ireftrim_pt1_manual_list', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_manual_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_manual_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='IREFPT1_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['iref_pt1_highr'] = ctvdecoder(is_edc=True, name='iref_pt1_highr', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ireftrim_range3_pt1_list', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_highr_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_highr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("IREF_TRIM_PT1","IREF_TRIM_PT1_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_pt1'] = ctvdecoder(is_edc=True, name='iref_pt1', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ireftrim_pt1_list', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("IREF_TRIM_PT1","IREF_TRIM_PT1_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_pt1_fuse'] = fuseconfig(is_edc=False, name='iref_pt1_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='IREF_PT1', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['adc01_4pt'] = ctvdecoder(is_edc=True, name='adc01_4pt', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ADC01_4PT.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P4V_MIN', Patlist='pth_dlvr_adc01_4pt_list', TimingsTc=IPCtiming, **dparams)
        t['adc01_4pt_calc'] = dlvrtrim(is_edc=True, name='adc01_4pt_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='ADC_4PT', Mode='IREF_TRIM', **dparams)
        t['adc01'] = ctvdecoder(is_edc=True, name='adc01', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ADC01_2PT.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P4V_MIN', Patlist='pth_dlvr_adc01_trim_list', TimingsTc=IPCtiming, **dparams)
        t['adc01_calc'] = dlvrtrim(is_edc=True, name='adc01_calc', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("ADC_2PT","ADC_2PT_CSM")'), Mode='IREF_TRIM', **dparams)
        t['adc01_fuse'] = fuseconfig(is_edc=False, name='adc01_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='ADC_FUSE', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['adc01_chk_post'] = ctvdecoder(is_edc=True, name='adc01_chk_post', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ADC01_CHK_SNDT.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P1V_MIN', Patlist='pth_dlvr_adc01_chk_sndt_list', TimingsTc=IPCtiming, ApplyEndSequence='DISABLED', **dparams)
        t['adc01_chk_post_calc'] = dlvrtrim(is_edc=True, name='adc01_chk_post_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("ADC_CHK","ADC_CHK_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_trim_sweep'] = ctvdecoder(is_edc=True, name='iref_trim_sweep', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_IREFTRIM_SWEEP_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ibias_sweep_extR_list', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['manual_ugb'] = ctvdecoder(is_edc=True, name='manual_ugb', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_MANUAL_UGB.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_ugbtrim_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_ugb_calc'] = dlvrtrim(is_edc=True, name='manual_ugb_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='UGB_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_mr'] = ctvdecoder(is_edc=True, name='manual_mr', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_MANUAL_MR.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_mr_amp_vsxtop_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_mr_calc'] = dlvrtrim(is_edc=True, name='manual_mr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='MR_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_csx'] = ctvdecoder(is_edc=True, name='manual_csx', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_MANUAL_CSX.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_csx_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_csx_calc'] = dlvrtrim(is_edc=True, name='manual_csx_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='CSX_MANUAL', Mode='MANUAL_TRIM', **dparams)
        for rge in ['range0','range1','range2']:
            t[f'dfxtrim_mrcsx_{rge}'] = ctvdecoder(is_edc=True, name=f'dfxtrim_mrcsx_{rge}', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_DFX_MRCSXTRIM.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist=f'pth_dlvr_mrcsxtrim_{rge}_dfx_list', TimingsTc=IPCtiming, **dparams)
            t[f'dfxtrim_mrcsx_{rge}_calc'] = dlvrtrim(is_edc=True, name=f'dfxtrim_mrcsx_{rge}_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("MRCSXTRIM","MRCSXTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_ugb'] = ctvdecoder(is_edc=True, name='dfxtrim_ugb', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_DFX_UGBTRIM.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_ugbtrim_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_ugb_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_ugb_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("UGBTRIM","UGBTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_ugb_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_ugb_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='UGB', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['dfxtrim_mrcsx'] = ctvdecoder(is_edc=True, name='dfxtrim_mrcsx', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_DFX_MRCSXTRIM.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_mrcsxtrim_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_mrcsx_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_mrcsx_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("MRCSXTRIM","MRCSXTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_mrcsx_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_mrcsx_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='MRCSX', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        for CM in ['408','928','1408']:
            t[f'anaprb_ugb_cm{CM}'] = analogdctc(is_edc=True, name=f'anaprb_ugb_cm{CM}', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_ANAPRB_UGB.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist=f'pth_dlvr_anaprb_ugb_{CM}_list', Pins='IPC::CPU_OBS_02,IPC::CPU_OBS_03', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('540'), CtvPins='CPU_TDO', **dparams)
            t[f'anaprb_ugb_cm{CM}_calc'] = dlvrtrim(is_edc=True, name=f'anaprb_ugb_cm{CM}_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='ANAPRB_UGB', Mode='IREF_TRIM', **dparams)
        t['dfxtrim_intcomp'] = ctvdecoder(is_edc=True, name='dfxtrim_intcomp', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_DFX_INTCOMP.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_internal_comp_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_intcomp_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_intcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='INTERNAL_DFX_TRIM', Mode='IREF_TRIM', **dparams)
        t['manual_digcomp'] = ctvdecoder(is_edc=True, name='manual_digcomp', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_MANUAL_DIGCOMP.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_digital_comp_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_digcomp_calc'] = dlvrtrim(is_edc=True, name='manual_digcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='DIGCOMP_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['dfxtrim_digcomp'] = ctvdecoder(is_edc=True, name='dfxtrim_digcomp', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_DFX_DIGCOMP.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_digital_comp_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_digcomp_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_digcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("DIG_DFX_TRIM","DIG_DFX_TRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_digcomp_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_digcomp_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='DIGITAL_COMP', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['clk_gating'] = ctvdecoder(is_edc=True, name='clk_gating', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_CLK_GATING.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_clk_gating_list', TimingsTc=IPCtiming, **dparams)
        t['close_loop'] = patmod(is_edc=False, name='close_loop', ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_PATMOD.setpoints.json', SetPoint='PS0_0P9V', **dparams)
        t['dac_cal'] = analogdctc(is_edc=True, name='dac_cal', BypassPort=1, DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ALL.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('720'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_atomcores'] = analogdctc(is_edc=True, name='dac_cal_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_evencore'] = analogdctc(is_edc=True, name='dac_cal_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE2_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_oddcore'] = analogdctc(is_edc=True, name='dac_cal_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_cal_atom{num}'] = analogdctc(is_edc=True, name=f'dac_cal_atom{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ATOM{num}.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_atom{num}_list', Pins=f'IPC::CPU_ATOM{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_cal_core{num}'] = analogdctc(is_edc=True, name=f'dac_cal_core{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_CORE{num}P.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_core{num}_list', Pins=f'IPC::CPU_CORE{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_ringprim'] = analogdctc(is_edc=True, name='dac_cal_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_calc'] = dlvrtrim(is_edc=True, name='dac_cal_calc', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_DCERROR.json', ConfigSet='DAC_CAL', Mode='DAC_CAL', **dparams)
        t['dac_cal_fuse'] = fuseconfig(is_edc=False, name='dac_cal_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='DVDAC', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['dac_chk'] = analogdctc(is_edc=True, name='dac_chk', BypassPort=1, DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ALL.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('720'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_atomcores'] = analogdctc(is_edc=True, name='dac_chk_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_evencore'] = analogdctc(is_edc=True, name='dac_chk_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE2_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_oddcore'] = analogdctc(is_edc=True, name='dac_chk_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_chk_atom{num}'] = analogdctc(is_edc=True, name=f'dac_chk_atom{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ATOM{num}.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_atom{num}_list', Pins=f'IPC::CPU_ATOM{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_chk_core{num}'] = analogdctc(is_edc=True, name=f'dac_chk_core{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_CORE{num}P.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_core{num}_list', Pins=f'IPC::CPU_CORE{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_ringprim'] = analogdctc(is_edc=True, name='dac_chk_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_calc'] = dlvrtrim(is_edc=True, name='dac_chk_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_DCERROR.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("DAC_CHK","DAC_CHK_CSM")'), Mode='DAC_CAL', **dparams)
        t['preibr_idle'] = analogdctc(is_edc=True, name='preibr_idle', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_PRE_IBR_IDLE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1760'), CtvPins='CPU_TDO', **dparams)
        t['pre_ibr'] = analogdctc(is_edc=False, name='pre_ibr', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_PRE_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_preIBR_HX_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('4325'), CtvPins='CPU_TDO', **dparams)
        t['pre_ibr_calc'] = dlvrtrim(is_edc=True, name='pre_ibr_calc', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='PRE_IBR', Mode='IREF_TRIM', **dparams)
        t['pre_ibr_fuse'] = fuseconfig(is_edc=False, name='pre_ibr_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='DVMRBF', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['post_ibr'] = analogdctc(is_edc=False, name='post_ibr', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_POST_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_postIBR_HX_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('8921'), CtvPins='CPU_TDO', **dparams)
        t['post_ibr_calc'] = dlvrtrim(is_edc=True, name='post_ibr_calc', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='POST_IBR', Mode='IREF_TRIM', **dparams)
        t['post_ibr_csm'] = dlvrtrim(is_edc=True, name='post_ibr_csm', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='POST_IBR_CSM', Mode='IREF_TRIM', **dparams)
        t['gang'] = analogdctc(is_edc=False, name='gang', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_GANG_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_GangedRing_IPB_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1400'), CtvPins='CPU_TDO', **dparams)
        t['gang_calc'] = dlvrtrim(is_edc=True, name='gang_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='GANG', Mode='IREF_TRIM', **dparams)
        t['sds2class_gsds'] = gsdsdff(is_edc=True, name='sds2class_gsds', ConfigurationFile='./InputFiles/PTHGSDS_NVL_S28C_DFF2GSDS_SORT.json', OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), **dparams)
        t['s2cdelta'] = dlvrtrim(is_edc=True, name='s2cdelta', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='S2CDELTA', Mode='IREF_TRIM', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), **dparams)
        t['setdff'] = gsdsdff(is_edc=True, name='setdff', ConfigurationFile=Spec('PTH_DLVR_CXPKGS7_Rules.Select_RCHOT ("./InputFiles/PTHGSDS_NVL_S28C_GSDS2DFF_CLASS_RC.json","./InputFiles/PTHGSDS_NVL_S28C_GSDS2DFF_CLASS.json")'), OPType='GSDS2DFF', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('__shared__::GlobalRule.primaryoptype(-1,-1,1,1,1,1,1,1,1,1)'), **dparams)
        t['fuseconfig_all_x1'] = fuseconfig(is_edc=False, name='fuseconfig_all_x1', ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint='DLVR_FUSE_ALL_1', RegEx='[gdx].......C........_.._......._............._...C............._.1.*', **dparams)
        t['vcciavmin'] = analogdctc(is_edc=True, name='vcciavmin', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_VCCIAVMIN.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_0P6V_MIN', Patlist='pth_dlvr_vcciavmin_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('704'), CtvPins='CPU_TDO', **dparams)
        t['vcciavmin_calc'] = dlvrtrim(is_edc=True, name='vcciavmin_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='VCCIAVMIN', Mode='IREF_TRIM', **dparams)
        t['rampupdef'] = patmod(is_edc=False, name='rampupdef', BypassPort=1, ConfigurationFile='./InputFiles/PATCONFIG_NVL_S28C_PATMOD.setpoints.json', SetPoint='PS0_0P9V', **dparams)
        t['dlvrkillall_failind'] = dlvrtrim(is_edc=True, name='dlvrkillall_failind', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY("DLVR_KILLALL","DLVR_KILLALL_CSM")'), Mode='IREF_TRIM', **dparams)
        t['allkill_failind'] = screentc(is_edc=False, name='allkill_failind', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ScreenTestSet='FAIL_INDICATOR', ScreenTestsFile='./InputFiles/NVL_816_SCREEN_FAIL_INDICATOR.txt', **dparams)
        t['allkill_failind_csm'] = screentc(is_edc=False, name='allkill_failind_csm', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ScreenTestSet='FAIL_INDICATOR_CSM', ScreenTestsFile='./InputFiles/NVL_816_SCREEN_FAIL_INDICATOR.txt', **dparams)
        t['fuseconfig_check'] = ctvdecoder(is_edc=False, name='fuseconfig_check', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_FUSECHK.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_dynamic_fuse_check_list', TimingsTc=IPCtiming, **dparams)
        t['dacflowfork'] = power(is_edc=True, name='dacflowfork', BypassPort=Spec('PTH_DLVR_CXPKGS7_Rules.DLVR_RUNCLASSHOT_ONLY(1,2)'), **dparams)


        ###Debug Flow Composite###
        debug_flow_fitems = list()
        offset = 0
        debug_flow_fitems.append(t['tap2reg_dump'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pwrgood_chk'].test.name)))
        debug_flow_fitems.append(t['pwrgood_chk'].get_fitem(r0=pFail(setbin=AUTO, goto=t['regcheck'].test.name)))
        debug_flow_fitems.append(t['regcheck'].get_fitem(**{**{f"r{i}": pFail(ret=1) for i in range(6)}, "r1": pPass()}))

        debug_flow_name = 'Debug_Flow_STARTANA1CPU'
        if composite_postfix:
            debug_flow_name = 'Debug_Flow_STARTANA1CPU'+ '_' + composite_postfix

        ###LVR_FF_STARTANA1CPU Composite###
        lvrff_fitems = list()
        offset = 0
        lvrff_fitems.append(t['anaprb_mrcsx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['anaprb_irefgen'].test.name)))
        lvrff_fitems.append(t['anaprb_irefgen'].get_fitem(r0=pFail(setbin=AUTO, goto=t['intlvr_sweep'].test.name)))
        lvrff_fitems.append(t['intlvr_sweep'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_alladc1_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_alladc1_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_alladc1_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_alladc1_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2dis_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2dis_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2dis_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2dis_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2ena_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2ena_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2ena_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2ena_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsadconly_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsadconly_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['lvr_adc_read'].test.name)))
        lvrff_fitems.append(t['lvr_adc_read'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        lvr_ff_flow_name = 'LVR_FF_STARTANA1CPU'
        if composite_postfix:
            lvr_ff_flow_name = 'LVR_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###LVR_STARTANA1CPU Composite###
        lvr_fitems = list()
        offset = 0
        lvr_fitems.append(t['anaprb_lvr'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_lvr_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        lvr_fitems.append(t['anaprb_lvr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=lvr_ff_flow_name), r1=pPass(ret=1)))
        lvr_fitems.append(Fitem('SAME', Flow(lvr_ff_flow_name, *lvrff_fitems), r0=pFail(ret=1)))

        lvr_flow_name = 'LVR_STARTANA1CPU'
        if composite_postfix:
            lvr_flow_name = 'LVR_STARTANA1CPU'+ '_' + composite_postfix

        ###IREF_FF_TRIM_STARTANA1CPU Composite ###
        ireftrimff_fitems = list()
        offset = 0
        ireftrimff_fitems.append(t['iref_pt1_manual'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_manual_calc'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_manual_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_highr'].test.name) ))
        ireftrimff_fitems.append(t['iref_pt1_highr'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_highr_calc'].test.name)  ))
        ireftrimff_fitems.append(t['iref_pt1_highr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_trim_sweep'].test.name) ))
        ireftrimff_fitems.append(t['iref_trim_sweep'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        iref_ff_flow_name = 'IREFTRIM_FF_STARTANA1CPU'
        if composite_postfix:
            iref_ff_flow_name = 'IREFTRIM_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###ADC01_FF_STARTANA1CPU Composite ###
        adc01_fitems = list()
        offset = 0
        adc01_fitems.append(t['adc01_4pt'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_4pt_calc'].test.name)))
        adc01_fitems.append(t['adc01_4pt_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        adc01_ff_flow_name = 'ADC01_FF_STARTANA1CPU'
        if composite_postfix:
            adc01_ff_flow_name = 'ADC01_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###IREF_TRIM_STARTANA1CPU Composite ###
        ireftrim_fitems = list()
        offset = 0
        ireftrim_fitems.append(t['iref_pt1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_calc'].test.name)))
        ireftrim_fitems.append(t['iref_pt1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=iref_ff_flow_name)))
        ireftrim_fitems.append(t['iref_pt1_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ireftrim_fitems.append(t['adc01'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_calc'].test.name)))
        ireftrim_fitems.append(t['adc01_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_fuse'].test.name)))
        ireftrim_fitems.append(t['adc01_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ireftrim_fitems.append(t['adc01_chk_post'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_chk_post_calc'].test.name)))
        ireftrim_fitems.append(t['adc01_chk_post_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=adc01_ff_flow_name), r1=pPass(ret=1)))
        ireftrim_fitems.append(Fitem('SAME', Flow(iref_ff_flow_name, *ireftrimff_fitems), r0=pFail(goto=t['adc01'].test.name), r1=pPass(goto=t['adc01'].test.name)))
        ireftrim_fitems.append(Fitem('SAME', Flow(adc01_ff_flow_name, *adc01_fitems), r0=pFail(ret=1)))

        iref_flow_name = 'IREF_TRIM_STARTANA1CPU'
        if composite_postfix:
            iref_flow_name = 'IREF_TRIM_STARTANA1CPU'+ '_' + composite_postfix

        ### UGB_FF_STARTANA1CPU Composite ###
        ugbff_fitems = list()
        offset = 0
        ugbff_fitems.append(t['manual_ugb'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_ugb_calc'].test.name)))
        ugbff_fitems.append(t['manual_ugb_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        ugbff_flow_name = 'UGB_FF_STARTANA1CPU'
        if composite_postfix:
            ugbff_flow_name = 'UGB_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### MRCSX_FF_STARTANA1CPU Composite ###
        mrcsxff_fitems = list()
        offset = 0
        mrcsxff_fitems.append(t['manual_mr'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_mr_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_mr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_csx'].test.name)))
        mrcsxff_fitems.append(t['manual_csx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_csx_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_csx_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range0'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range0_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range0_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range1'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range1_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range2'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range2'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range2_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range2_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        mrcsxff_flow_name = 'MRCSX_FF_STARTANA1CPU'
        if composite_postfix:
            mrcsxff_flow_name = 'MRCSX_FF_STARTANA1CPU'+ '_' + composite_postfix

        ### ANAPRBUGB_FF_STARTANA1CPU Compopsite ####
        anaprbugbff_fitems = list()
        offset = 0
        anaprbugbff_fitems.append(t['anaprb_ugb_cm408'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm408_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm408_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['anaprb_ugb_cm1408'].test.name)))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm1408'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm1408_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm1408_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        anaprbff_flow_name = 'ANAPRBUGB_FF_STARTANA1CPU'
        if composite_postfix:
            anaprbff_flow_name = 'ANAPRBUGB_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### DIGCOMP_FF_STARTANA1CPU Composite ###
        digcompff_fitems = list()
        offset = 0
        digcompff_fitems.append(t['hvls'].get_fitem(r0=pFail(setbin=AUTO, goto=t['clk_gating'].test.name)))
        digcompff_fitems.append(t['clk_gating'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_intcomp'].test.name)))
        digcompff_fitems.append(t['dfxtrim_intcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_intcomp_calc'].test.name)))
        digcompff_fitems.append(t['dfxtrim_intcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_digcomp'].test.name)))
        digcompff_fitems.append(t['manual_digcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_digcomp_calc'].test.name)))
        digcompff_fitems.append(t['manual_digcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        digcompff_flow_name = 'DIGCOMP_FF_STARTANA1CPU'
        if composite_postfix:
            digcompff_flow_name = 'DIGCOMP_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### DFX_TRIM_STARTANA1CPU Composite #######
        dfxtrim_fitems = list()
        offset = 0
        dfxtrim_fitems.append(t['dfxtrim_ugb'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_ugb_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_ugb_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=ugbff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_ugb_fuse'].get_fitem(r0=pFail(setbin=2768)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=mrcsxff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx_fuse'].get_fitem(r0=pFail(setbin=2768)))
        dfxtrim_fitems.append(t['anaprb_ugb_cm928'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm928_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        dfxtrim_fitems.append(t['anaprb_ugb_cm928_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=anaprbff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_digcomp_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=digcompff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp_fuse'].get_fitem(r0=pFail(setbin=2768), r1=pPass(ret=1)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(ugbff_flow_name, *ugbff_fitems), r0=pFail(goto=t['dfxtrim_mrcsx'].test.name), r1=pPass(goto=t['dfxtrim_mrcsx'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(mrcsxff_flow_name, *mrcsxff_fitems), r0=pFail(goto=t['anaprb_ugb_cm928'].test.name), r1=pPass(goto=t['anaprb_ugb_cm928'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(anaprbff_flow_name, *anaprbugbff_fitems), r0=pFail(goto=t['dfxtrim_digcomp'].test.name), r1=pPass(goto=t['dfxtrim_digcomp'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(digcompff_flow_name, *digcompff_fitems), r0=pFail(ret=1)))

        dfxtrim_flow_name = 'DFX_TRIM_STARTANA1CPU'
        if composite_postfix:
            dfxtrim_flow_name = 'DFX_TRIM_STARTANA1CPU'+ '_' + composite_postfix

        ###DAC_CAL_STARTANA1CPU Composite###
        DAC_CAL = list()
        offset = 0
        DAC_CAL.append(t['dac_cal'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atomcores'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core1'].get_fitem(**{**{f"r{i}": pFail(setbin=2741, goto=t['dac_cal_core2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dac_cal_fuse'].test.name)))
        DAC_CAL.append(t['dac_cal_fuse'].get_fitem(r0=pFail(setbin=2768)))

        DAC_CAL_flow_name = 'DAC_CAL_STARTANA1CPU'
        if composite_postfix:
            DAC_CAL_flow_name = 'DAC_CAL_STARTANA1CPU'+ '_' + composite_postfix

        ###DAC_CHK_STARTANA1CPU Composite###
        DAC_CHK = list()
        offset = 0
        DAC_CHK.append(t['dac_chk'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atomcores'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atom0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom0'].get_fitem(**{**{f"r{i}": pFail(setbin=2742, goto=t['dac_chk_atom1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atom2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atom3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        DAC_CHK_flow_name = 'DAC_CHK_STARTANA1CPU'
        if composite_postfix:
            DAC_CHK_flow_name = 'DAC_CHK_STARTANA1CPU'+ '_' + composite_postfix

        ### DAC_STARTANA1CPU Composite ###
        DAC = list()
        DAC.append(t['dacflowfork'].get_fitem(r0=pFail(setbin=AUTO, goto=DAC_CAL_flow_name), r1=pPass(setbin=AUTO, goto=DAC_CAL_flow_name), r2=pPass(setbin=AUTO, goto=DAC_CHK_flow_name)))
        DAC.append(Fitem('SAME', Flow(DAC_CAL_flow_name, *DAC_CAL), r0=pFail(ret=0)))
        DAC.append(Fitem('SAME', Flow(DAC_CHK_flow_name, *DAC_CHK), r0=pFail(ret=1)))

        DAC_flow_name = 'DAC_STARTANA1CPU'
        if composite_postfix:
            DAC_flow_name = 'DAC_STARTANA1CPU'+ '_' + composite_postfix

        ###ICC_PER_BRANCH_STARTANA1CPU Composite###
        ICC_PER_BRANCH = list()
        offset = 0
        ICC_PER_BRANCH.append(t['preibr_idle'].get_fitem(**{**{f"r{i}": pFail(setbin=2765, goto=t['pre_ibr'].test.name) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['pre_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['pre_ibr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pre_ibr_fuse'].test.name)))
        ICC_PER_BRANCH.append(t['pre_ibr_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ICC_PER_BRANCH.append(t['post_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['post_ibr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['post_ibr_csm'].test.name)))
        ICC_PER_BRANCH.append(t['post_ibr_csm'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        ICC_PER_BRANCH_flow_name = 'ICC_PER_BRANCH_STARTANA1CPU'
        if composite_postfix:
            ICC_PER_BRANCH_flow_name = 'ICC_PER_BRANCH_STARTANA1CPU'+ '_' + composite_postfix

        ###GANG_CHK_STARTANA1CPU Composite###
        GANG_CHK = list()
        offset = 0
        GANG_CHK.append(t['gang'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        GANG_CHK.append(t['gang_calc'].get_fitem(r0=pFail(setbin=2765, ret=1)))

        GANG_CHK_flow_name = 'GANG_CHK_STARTANA1CPU'
        if composite_postfix:
            GANG_CHK_flow_name = 'GANG_CHK_STARTANA1CPU'+ '_' + composite_postfix

        ### MAIN PART TO CREATE FLOW ON DLVR###
        hvm_fitems = list()
        hvm_fitems.append(Fitem('SAME', Flow(debug_flow_name, *debug_flow_fitems), r0=pFail(goto=t['gsds_inject'].test.name)))
        hvm_fitems.append(t['gsds_inject'].get_fitem(r0=pFail(setbin=AUTO, goto=t['setgsds'].test.name)))
        hvm_fitems.append(t['setgsds'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['binconv_prim'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['binconv_prim'].get_fitem(r0=pFail(setbin=AUTO, goto=t['binconv_all'].test.name)))
        hvm_fitems.append(t['binconv_all'].get_fitem(r0=pFail(setbin=AUTO, goto=t['default'].test.name)))
        hvm_fitems.append(t['default'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['open_loop'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['voutmeas'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['voutmeas_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        hvm_fitems.append(t['voutmeas_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=lvr_flow_name)))
        hvm_fitems.append(Fitem('SAME', Flow(lvr_flow_name, *lvr_fitems), r0=pFail(goto=t['pod_vil'].test.name)))
        hvm_fitems.append(t['pod_vil'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pod_vih'].test.name), r2=pFail(setbin=AUTO, goto=t['pod_vih'].test.name)))
        hvm_fitems.append(t['pod_vih'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['pod'].test.name) for i in range(8)}, "r1": pPass()}))
        hvm_fitems.append(t['pod'].get_fitem(r0=pFail(setbin=AUTO, goto=iref_flow_name)))
        hvm_fitems.append(Fitem('SAME', Flow(iref_flow_name, *ireftrim_fitems), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(dfxtrim_flow_name, *dfxtrim_fitems), r0=pFail(ret=0)))
        hvm_fitems.append(t['close_loop'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(Fitem('SAME', Flow(DAC_flow_name, *DAC), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(ICC_PER_BRANCH_flow_name, *ICC_PER_BRANCH), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(GANG_CHK_flow_name, *GANG_CHK), r0=pFail(ret=0)))
        hvm_fitems.append(t['vcciavmin'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['vcciavmin_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        hvm_fitems.append(t['vcciavmin_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['rampupdef'].test.name)))
        hvm_fitems.append(t['rampupdef'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['sds2class_gsds'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['s2cdelta'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['s2cdelta'].get_fitem(r0=pFail(setbin=AUTO, goto=t['setdff'].test.name)))
        hvm_fitems.append(t['setdff'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['fuseconfig_all_x1'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['fuseconfig_all_x1'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['dlvrkillall_failind'].get_fitem(r0=pFail(setbin=AUTO, goto=t['allkill_failind'].test.name)))
        hvm_fitems.append(t['allkill_failind'].get_fitem(**{**{f"r{i}": pFail(setbin=b) for i, b in {0:27626289,2:27520035,3:27530250,4:27710144,5:27560155,6:27626290,7:27570956,8:27650404,9:27636307,10:27616193,11:27666613,12:27676722}.items()}, "r1": pPass()}))
        hvm_fitems.append(t['allkill_failind_csm'].get_fitem(**{**{f"r{i}": pFail(setbin=b) for i, b in {0:27626291,2:27520036,3:27530251,4:27710145,5:27560156,6:27626292,7:27570957,8:27650405,9:27636308,10:27616194,11:27666614,12:27676723}.items()}, "r1": pPass()}))
        hvm_fitems.append(t['fuseconfig_check'].get_fitem(r0=pFail(setbin=27676716), r2=pFail(setbin=27676717),r3=pFail(setbin=27676718),r4=pFail(setbin=27676719),r5=pFail(setbin=27676720)))

        Flow(flow_name, *hvm_fitems,  dtag='STARTANA1CPU_SubFlow')

    def get_816_lttccpu_flow(self, flow_name, module_name='LTTCCPU', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        dlvrtrim = DlvrTrimCalc_TestBuilder
        analogdctc = AnalogDcTC_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test

        t['dac_chk_atomcores'] = analogdctc(is_edc=True, name='dac_chk_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_evencore'] = analogdctc(is_edc=True, name='dac_chk_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE2_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_oddcore'] = analogdctc(is_edc=True, name='dac_chk_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_ringprim'] = analogdctc(is_edc=True, name='dac_chk_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk'] = dlvrtrim(is_edc=False, name='dac_chk', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_DCERROR.json', ConfigSet='DAC_CHK_CSM', Mode='DAC_CAL', **dparams)
        t['pre_ibr_idle'] = analogdctc(is_edc=True, name='pre_ibr_idle', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_PRE_IBR_IDLE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['post_ibr'] = analogdctc(is_edc=False, name='post_ibr', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_POST_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS7::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_postIBR_HX_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=8921, CtvPins='CPU_TDO', **dparams)
        t['post_ibr_calc'] = dlvrtrim(is_edc=False, name='post_ibr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S28C_POST_TRIM.json', ConfigSet='POST_IBR_CSM', Mode='IREF_TRIM', **dparams)


        #####DAC_CHK_LTTCCPU Composite####
        dacchk_fitems = list()
        dacchk_fitems.append(t['dac_chk_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk'].get_fitem(r0=pFail(setbin=2757)))

        DACCHK_flow_name = 'DACCHK_LTTCCPU'
        if composite_postfix:
            DACCHK_flow_name = 'DACCHK_LTTCCPU'+ '_' + composite_postfix

        #####ICC_PER_BRANCH_LTTCCPU Composite####
        icc_fitems = list()
        icc_fitems.append(t['pre_ibr_idle'].get_fitem(**{**{f"r{i}": pFail(setbin=2765, goto=t['post_ibr'].test.name) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['post_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['post_ibr_calc'].get_fitem(r0=pFail(setbin=2765)))

        icc_flow_name = 'ICC_PER_BRANCH_LTTCCPU'
        if composite_postfix:
            icc_flow_name = 'ICC_PER_BRANCH_LTTCCPU'+ '_' + composite_postfix

        ###LTTC Main Flow#####
        lttc_fitems = list()
        lttc_fitems.append(Fitem('SAME', Flow(DACCHK_flow_name, *dacchk_fitems), r0=pFail(ret=0)))
        lttc_fitems.append(Fitem('SAME', Flow(icc_flow_name, *icc_fitems), r0=pFail(ret=0)))
        Flow(flow_name, *lttc_fitems, dtag='LTTCCPU_SubFlow')

#==============================================================================S52C=====================================================================================================
    def get_s52c_startana1cpu_flow(self, flow_name, module_name='STARTANA1CPU', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        ctvdecoder = CtvDecoderSpm_TestBuilder
        gsdsdff = PTHGetSetGsdsDffTC_TestBuilder
        patmod = PrimePatConfigTestMethodPatmod_TestBuilder
        fuseconfig = PrimePatConfigTestMethodFuseConfig_TestBuilder
        dlvrtrim = DlvrTrimCalc_TestBuilder
        func = PrimeFunctionalTestMethod_TestBuilder
        screentc = ScreenTC_TestBuilder
        analogdctc = AnalogDcTC_TestBuilder
        vmintc = VminTC_TestBuilder
        vminpass2failtc = VminPass2FailTC_TestBuilder
        power = PowerSequenceHandler_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test



        ### list of tests
        t['tap2reg_dump'] = ctvdecoder(is_edc=True, name='tap2reg_dump', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_TAP2REG_DUMP.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', CtvCapturePins='CPU_TDO,CPU1_TDO', Patlist='pth_dlvr_regdump_list', TimingsTc=IPCtiming, **dparams)
        t['pwrgood_chk'] = ctvdecoder(is_edc=True, name='pwrgood_chk', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_PWRGOOD_CHK.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', CtvCapturePins='CPU_OBS_06,CPU1_OBS_06', Patlist='pth_dlvr_pwrgood_list', TimingsTc=IPCtiming, **dparams)
        t['regcheck'] = func(is_edc=True, name='regcheck', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_reg_check_list', TimingsTc=IPCtiming, **dparams)
        t['gsds_inject'] = dlvrtrim(is_edc=True, name='gsds_inject', BypassPort=1, ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='GSDS_INJECT', Mode='IREF_TRIM', **dparams)
        t['setgsds'] = gsdsdff(is_edc=True, name='setgsds', ConfigurationFile=Spec('PTH_DLVR_CXPKGS9_Rules.Select_RCCOLD ("./InputFiles/PTHGSDS_NVL_S52C_CPU_DFF2GSDS_RC.json","./InputFiles/PTHGSDS_NVL_S52C_CPU_DFF2GSDS.json")'), OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), **dparams)
        t['setgsds_cpu1'] = gsdsdff(is_edc=True, name='setgsds_cpu1', ConfigurationFile=Spec('PTH_DLVR_CXPKGS9_Rules.Select_RCCOLD ("./InputFiles/PTHGSDS_NVL_S52C_DFF2GSDS_RC.json","./InputFiles/PTHGSDS_NVL_S52C_DFF2GSDS.json")'), OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU1+")', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), **dparams)
        t['binconv_prim'] = dlvrtrim(is_edc=True, name='binconv_prim', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='BINCONV_PRIM', Mode='IREF_TRIM', **dparams)
        t['binconv_all'] = dlvrtrim(is_edc=True, name='binconv_all', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='BINCONV_ALL', Mode='IREF_TRIM', **dparams)
        t['default'] = fuseconfig(is_edc=False, name='default', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='DLVR_FUSE_ALL_1', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['open_loop'] = patmod(is_edc=False, name='open_loop', ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_PATMOD.setpoints.json', SetPoint='PS0_0V', **dparams)
        t['voutmeas'] = analogdctc(is_edc=True, name='voutmeas', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_VOUTMEAS.json', Patlist='pth_dlvr_vout_float_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU1_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU1_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU1_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT,IPC::CPU1_CORE3_DLVROUT', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['voutmeas_calc'] = dlvrtrim(is_edc=True, name='voutmeas_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='VOUTMEAS', Mode='IREF_TRIM', **dparams)
        t['cmem_lvr_max_alladc1_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_alladc1_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ANAPRB_LVR_ADC1_CH1.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', CtvCapturePins='CPU_TDO,CPU1_TDO', Patlist='pth_dlvr_anaprb_bglvr_allch1_adc1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_alladc1_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_alladc1_ch0', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_ANAPRB_LVR_ADC1_CH0.csv', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', CtvCapturePins='CPU_TDO,CPU1_TDO', Patlist='pth_dlvr_anaprb_bglvr_allch0_adc1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2dis_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2dis_ch0', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_CH0.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch0_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2dis_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2dis_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_CH1.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2ena_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2ena_ch0', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_L2EN_CH0.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch0L2en_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2ena_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2ena_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSVIEW_L2EN_CH1.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch1L2en_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsadconly_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsadconly_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_AGSBGBUFADC0.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsgbugadc0_list', TimingsTc=IPCtiming, **dparams)
        t['lvr_adc_read'] = dlvrtrim(is_edc=True, name='lvr_adc_read', BypassPort=1, ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='LVR', Mode='IREF_TRIM', **dparams)
        t['anaprb_mrcsx'] = ctvdecoder(is_edc=True, name='anaprb_mrcsx', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_ANAPRB_MRCSX.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_anaprb_mr_csx_amp_list', TimingsTc=IPCtiming, **dparams)
        t['anaprb_irefgen'] = ctvdecoder(is_edc=True, name='anaprb_irefgen', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_ANAPRB_IREFGEN.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_anaprb_irefgen_list', TimingsTc=IPCtiming, **dparams)
        t['intlvr_sweep'] = ctvdecoder(is_edc=True, name='intlvr_sweep', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_INTLVR_DACSEL_SWEEP.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_intlvr_dacsel_sweep_list', TimingsTc=IPCtiming, **dparams)
        t['anaprb_lvr'] = analogdctc(is_edc=True, name='anaprb_lvr', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_ANAPRB_LVR.json', Patlist='pth_dlvr_anaprb_bglvr_list', Pins='IPC::CPU_OBS_02,IPC::CPU1_OBS_02,IPC::CPU_OBS_03,IPC::CPU1_OBS_03', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1020'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['anaprb_lvr_calc'] = dlvrtrim(is_edc=True, name='anaprb_lvr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='ANAPRB_LVR', Mode='IREF_TRIM', **dparams)
        t['pod_vih'] = vmintc(is_edc=True, name='pod_vih', EndVoltageLimits='0.7', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_pod_vih_list', StartVoltages='0.3', StepSize=Spec('0.05'), TestMode='SingleVmin', TimingsTc=IPCtiming, VoltageTargets='VCCIA', VminResult='CPU_POD_VIH', **dparams)
        t['pod_vih_cpu1'] = vmintc(is_edc=True, name='pod_vih_cpu1', EndVoltageLimits='0.7', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_pod_vih_list_cpu1', StartVoltages='0.3', StepSize=Spec('0.05'), TestMode='SingleVmin', TimingsTc=IPCtiming, VoltageTargets='VCCIA', VminResult='CPU1_POD_VIH', **dparams)
        t['pod_vil'] = vminpass2failtc(is_edc=True, name='pod_vil', Patlist='pth_dlvr_pod_vih_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', TimingsTc=IPCtiming, VoltageTargets='VCCIA', FivrCondition='', StartVoltage='0.5', EndVoltage='0.2', StepSize=Spec('-0.05'), VminResult='CPU_POD_VIL', **dparams)
        t['pod_vil_cpu1'] = vminpass2failtc(is_edc=True, name='pod_vil_cpu1', Patlist='pth_dlvr_pod_vih_list_cpu1', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', TimingsTc=IPCtiming, VoltageTargets='VCCIA', FivrCondition='', StartVoltage='0.5', EndVoltage='0.2', StepSize=Spec('-0.05'), VminResult='CPU1_POD_VIL', **dparams)
        t['pod'] = dlvrtrim(is_edc=True, name='pod', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='POD', Mode='IREF_TRIM', **dparams)
        t['hvls'] = ctvdecoder(is_edc=True, name='hvls', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_HVLS.csv', CtvCapturePins='CPU_OBS_07,CPU1_OBS_07', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_hvls_list', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_manual'] = ctvdecoder(is_edc=True, name='iref_pt1_manual', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_MANUAL_IREF_PT1.csv', CtvCapturePins='CPU_OBS_06', Patlist='pth_dlvr_ireftrim_pt1_manual_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_manual_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_manual_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='IREFPT1_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['iref_pt1_manual_cpu1'] = ctvdecoder(is_edc=True, name='iref_pt1_manual_cpu1', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_MANUAL_IREF_PT1.csv', CtvCapturePins='CPU1_OBS_06', Patlist='pth_dlvr_ireftrim_pt1_manual_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_manual_cpu1_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_manual_cpu1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_MANUAL_TRIM.json', ConfigSet='IREFPT1_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['iref_pt1_highr'] = ctvdecoder(is_edc=True, name='iref_pt1_highr', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ireftrim_range3_pt1_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_highr_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_highr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("IREF_TRIM_PT1","IREF_TRIM_PT1_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_pt1_highr_cpu1'] = ctvdecoder(is_edc=True, name='iref_pt1_highr_cpu1', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU1_TDO', Patlist='pth_dlvr_ireftrim_range3_pt1_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1'] = ctvdecoder(is_edc=True, name='iref_pt1', ConfigurationFile='./InputFiles/CTV_NVL_816_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ireftrim_pt1_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("IREF_TRIM_PT1","IREF_TRIM_PT1_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_pt1_cpu1'] = ctvdecoder(is_edc=True, name='iref_pt1_cpu1', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU1_TDO', Patlist='pth_dlvr_ireftrim_pt1_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_fuse'] = fuseconfig(is_edc=False, name='iref_pt1_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='IREF_PT1', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['adc01_4pt'] = ctvdecoder(is_edc=True, name='adc01_4pt', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_ADC01_4PT.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P4V_MIN', Patlist='pth_dlvr_adc01_4pt_list', TimingsTc=IPCtiming, **dparams)
        t['adc01_4pt_calc'] = dlvrtrim(is_edc=True, name='adc01_4pt_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='ADC_4PT', Mode='IREF_TRIM', **dparams)
        t['adc01'] = ctvdecoder(is_edc=True, name='adc01', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_ADC01_2PT.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P4V_MIN', Patlist='pth_dlvr_adc01_trim_list', TimingsTc=IPCtiming, **dparams)
        t['adc01_calc'] = dlvrtrim(is_edc=True, name='adc01_calc', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("ADC_2PT","ADC_2PT_CSM")'), Mode='IREF_TRIM', **dparams)
        t['adc01_fuse'] = fuseconfig(is_edc=False, name='adc01_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='ADC_FUSE', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['adc01_chk_post'] = ctvdecoder(is_edc=True, name='adc01_chk_post', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_ADC01_CHK_SNDT.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P1V_MIN', Patlist='pth_dlvr_adc01_chk_sndt_list', TimingsTc=IPCtiming, ApplyEndSequence='DISABLED', **dparams)
        t['adc01_chk_post_calc'] = dlvrtrim(is_edc=True, name='adc01_chk_post_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='ADC_CHK', Mode='IREF_TRIM', **dparams)
        t['iref_trim_sweep'] = ctvdecoder(is_edc=True, name='iref_trim_sweep', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_IREFTRIM_SWEEP_ALL.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', Patlist='pth_dlvr_ibias_sweep_extR_list', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', TimingsTc=IPCtiming, **dparams)
        t['manual_ugb'] = ctvdecoder(is_edc=True, name='manual_ugb', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_MANUAL_UGB.csv', CtvCapturePins='CPU_OBS_06,CPU1_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_ugbtrim_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_ugb_calc'] = dlvrtrim(is_edc=True, name='manual_ugb_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='UGB_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_ugb_cpu1_calc'] = dlvrtrim(is_edc=True, name='manual_ugb_cpu1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_MANUAL_TRIM.json', ConfigSet='UGB_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_mr'] = ctvdecoder(is_edc=True, name='manual_mr', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_MANUAL_MR.csv', CtvCapturePins='CPU_OBS_06,CPU1_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_mr_amp_vsxtop_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_mr_calc'] = dlvrtrim(is_edc=True, name='manual_mr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='MR_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_mr_cpu1_calc'] = dlvrtrim(is_edc=True, name='manual_mr_cpu1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_MANUAL_TRIM.json', ConfigSet='MR_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_csx'] = ctvdecoder(is_edc=True, name='manual_csx', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_MANUAL_CSX.csv', CtvCapturePins='CPU_OBS_06,CPU1_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_csx_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_csx_calc'] = dlvrtrim(is_edc=True, name='manual_csx_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='CSX_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_csx_cpu1_calc'] = dlvrtrim(is_edc=True, name='manual_csx_cpu1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_MANUAL_TRIM.json', ConfigSet='CSX_MANUAL', Mode='MANUAL_TRIM', **dparams)
        for rge in ['range0','range1','range2']:
            t[f'dfxtrim_mrcsx_{rge}'] = ctvdecoder(is_edc=True, name=f'dfxtrim_mrcsx_{rge}', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_DFX_MRCSXTRIM.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist=f'pth_dlvr_mrcsxtrim_{rge}_dfx_list', TimingsTc=IPCtiming, **dparams)
            t[f'dfxtrim_mrcsx_{rge}_calc'] = dlvrtrim(is_edc=True, name=f'dfxtrim_mrcsx_{rge}_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("MRCSXTRIM","MRCSXTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_ugb'] = ctvdecoder(is_edc=True, name='dfxtrim_ugb', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_DFX_UGBTRIM.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_ugbtrim_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_ugb_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_ugb_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("UGBTRIM","UGBTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_ugb_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_ugb_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='UGB', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['dfxtrim_mrcsx'] = ctvdecoder(is_edc=True, name='dfxtrim_mrcsx', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_DFX_MRCSXTRIM.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_mrcsxtrim_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_mrcsx_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_mrcsx_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("MRCSXTRIM","MRCSXTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_mrcsx_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_mrcsx_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='MRCSX', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        for CM in ['408','928','1408']:
            t[f'anaprb_ugb_cm{CM}'] = analogdctc(is_edc=True, name=f'anaprb_ugb_cm{CM}', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_ANAPRB_UGB.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist=f'pth_dlvr_anaprb_ugb_{CM}_list', Pins='IPC::CPU_OBS_02,IPC::CPU1_OBS_02,IPC::CPU_OBS_03,IPC::CPU1_OBS_03', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('540'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
            t[f'anaprb_ugb_cm{CM}_calc'] = dlvrtrim(is_edc=True, name=f'anaprb_ugb_cm{CM}_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='ANAPRB_UGB', Mode='IREF_TRIM', **dparams)
        t['dfxtrim_intcomp'] = ctvdecoder(is_edc=True, name='dfxtrim_intcomp', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_DFX_INTCOMP.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_internal_comp_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_intcomp_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_intcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='INTERNAL_DFX_TRIM', Mode='IREF_TRIM', **dparams)
        t['manual_digcomp'] = ctvdecoder(is_edc=True, name='manual_digcomp', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_MANUAL_DIGCOMP.csv', CtvCapturePins='CPU_OBS_06,CPU1_OBS_06', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_digital_comp_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_digcomp_calc'] = dlvrtrim(is_edc=True, name='manual_digcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_816_MANUAL_TRIM.json', ConfigSet='DIGCOMP_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_digcomp_cpu1_calc'] = dlvrtrim(is_edc=True, name='manual_digcomp_cpu1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_MANUAL_TRIM.json', ConfigSet='DIGCOMP_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['dfxtrim_digcomp'] = ctvdecoder(is_edc=True, name='dfxtrim_digcomp', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_DFX_DIGCOMP.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_digital_comp_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_digcomp_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_digcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("DIG_DFX_TRIM","DIG_DFX_TRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_digcomp_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_digcomp_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='DIGITAL_COMP', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['clk_gating'] = ctvdecoder(is_edc=True, name='clk_gating', ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_CLK_GATING.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_clk_gating_list', TimingsTc=IPCtiming, **dparams)
        t['close_loop'] = patmod(is_edc=False, name='close_loop', ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_PATMOD.setpoints.json', SetPoint='PS0_0P9V', **dparams)
        t['dac_cal'] = analogdctc(is_edc=True, name='dac_cal', BypassPort=1, DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ALL.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU1_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU1_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU1_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('720'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_cal_atomcores'] = analogdctc(is_edc=True, name='dac_cal_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU1_ATOM3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_cal_evencore'] = analogdctc(is_edc=True, name='dac_cal_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU1_CORE2_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_cal_oddcore'] = analogdctc(is_edc=True, name='dac_cal_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU_CORE3_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        for num in range(4):
            t[f'dac_cal_atom{num}'] = analogdctc(is_edc=True, name=f'dac_cal_atom{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ATOM{num}.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist=f'pth_dlvr_dac_cal_atom{num}_list', Pins=f'IPC::CPU_ATOM{num}_DLVROUT,IPC::CPU1_ATOM{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        for num in range(4):
            t[f'dac_cal_core{num}'] = analogdctc(is_edc=True, name=f'dac_cal_core{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_CORE{num}P.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist=f'pth_dlvr_dac_cal_core{num}_list', Pins=f'IPC::CPU_CORE{num}_DLVROUT,IPC::CPU1_CORE{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_cal_ringprim'] = analogdctc(is_edc=True, name='dac_cal_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU1_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_cal_calc'] = dlvrtrim(is_edc=True, name='dac_cal_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_DCERROR.json', ConfigSet='DAC_CAL', Mode='DAC_CAL', **dparams)
        t['dac_cal_fuse'] = fuseconfig(is_edc=False, name='dac_cal_fuse', ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='DVDAC', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['dac_chk'] = analogdctc(is_edc=True, name='dac_chk', BypassPort=1, DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ALL.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU1_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU1_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU1_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('720'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_atomcores'] = analogdctc(is_edc=True, name='dac_chk_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU1_ATOM3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_evencore'] = analogdctc(is_edc=True, name='dac_chk_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU1_CORE2_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_oddcore'] = analogdctc(is_edc=True, name='dac_chk_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU_CORE3_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        for num in range(4):
            t[f'dac_chk_atom{num}'] = analogdctc(is_edc=True, name=f'dac_chk_atom{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ATOM{num}.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist=f'pth_dlvr_dac_cal_atom{num}_list', Pins=f'IPC::CPU_ATOM{num}_DLVROUT,IPC::CPU1_ATOM{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        for num in range(4):
            t[f'dac_chk_core{num}'] = analogdctc(is_edc=True, name=f'dac_chk_core{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_CORE{num}P.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist=f'pth_dlvr_dac_cal_core{num}_list', Pins=f'IPC::CPU_CORE{num}_DLVROUT,IPC::CPU1_CORE{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_ringprim'] = analogdctc(is_edc=True, name='dac_chk_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU1_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_calc'] = dlvrtrim(is_edc=True, name='dac_chk_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_DCERROR.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("DAC_CHK","DAC_CHK_CSM")'), Mode='DAC_CAL', **dparams)
        t['preibr_idle'] = analogdctc(is_edc=True, name='preibr_idle', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_PRE_IBR_IDLE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1760'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['preibr_idle_cpu1'] = analogdctc(is_edc=True, name='preibr_idle_cpu1', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_PRE_IBR_IDLE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1760'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['pre_ibr'] = analogdctc(is_edc=False, name='pre_ibr', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_PRE_IBR_HX.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_preIBR_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('4109'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['pre_ibr_calc'] = dlvrtrim(is_edc=True, name='pre_ibr_calc', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='PRE_IBR', Mode='IREF_TRIM', **dparams)
        t['pre_ibr_cpu1'] = analogdctc(is_edc=False, name='pre_ibr_cpu1', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_PRE_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_preIBR_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('4109'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['pre_ibr_fuse'] = fuseconfig(is_edc=False, name='pre_ibr_fuse', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='DVMRBF', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['post_ibr'] = analogdctc(is_edc=False, name='post_ibr', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_POST_IBR_HX.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_postIBR_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('8705'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['post_ibr_calc'] = dlvrtrim(is_edc=True, name='post_ibr_calc', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='POST_IBR', Mode='IREF_TRIM', **dparams)
        t['post_ibr_csm'] = dlvrtrim(is_edc=True, name='post_ibr_csm', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='POST_IBR_CSM', Mode='IREF_TRIM', **dparams)
        t['post_ibr_cpu1'] = analogdctc(is_edc=False, name='post_ibr_cpu1', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_POST_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_postIBR_list', Pins='VCCIA,IPC::CPU1_CCF_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU1_ATOM3_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU1_CORE2_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('8705'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['gang'] = analogdctc(is_edc=False, name='gang', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_GANG_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_GangedRing_IPB_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1400'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['gang_cpu1'] = analogdctc(is_edc=False, name='gang_cpu1', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_GANG_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_GangedRing_IPB_list', Pins='VCCIA,IPC::CPU1_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1400'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['gang_calc'] = dlvrtrim(is_edc=True, name='gang_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='GANG', Mode='IREF_TRIM', **dparams)
        t['sds2class_gsds'] = gsdsdff(is_edc=True, name='sds2class_gsds', ConfigurationFile='./InputFiles/PTHGSDS_NVL_S52C_CPU_DFF2GSDS_SORT.json', OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), **dparams)
        t['sds2class_gsds_cpu1'] = gsdsdff(is_edc=True, name='sds2class_gsds_cpu1', ConfigurationFile='./InputFiles/PTHGSDS_NVL_S52C_DFF2GSDS_SORT.json', OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU1+")', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), **dparams)
        t['s2cdelta'] = dlvrtrim(is_edc=True, name='s2cdelta', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='S2CDELTA', Mode='IREF_TRIM', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), **dparams)
        t['setdff'] = gsdsdff(is_edc=True, name='setdff', ConfigurationFile=Spec('PTH_DLVR_CXPKGS9_Rules.Select_RCHOT ("./InputFiles/PTHGSDS_NVL_S52C_CPU_GSDS2DFF_CLASS_RC.json","./InputFiles/PTHGSDS_NVL_S52C_CPU_GSDS2DFF_CLASS.json")'), OPType='GSDS2DFF', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('__shared__::GlobalRule.primaryoptype(-1,-1,1,1,1,1,1,1,1,1)'), **dparams)
        t['setdff_cpu1'] = gsdsdff(is_edc=True, name='setdff_cpu1', ConfigurationFile=Spec('PTH_DLVR_CXPKGS9_Rules.Select_RCHOT ("./InputFiles/PTHGSDS_NVL_S52C_GSDS2DFF_CLASS_RC.json","./InputFiles/PTHGSDS_NVL_S52C_GSDS2DFF_CLASS.json")'), OPType='GSDS2DFF', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU1+")', BypassPort=Spec('__shared__::GlobalRule.primaryoptype(-1,-1,1,1,1,1,1,1,1,1)'), **dparams)
        t['fuseconfig_all_x1'] = fuseconfig(is_edc=False, name='fuseconfig_all_x1', ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint='DLVR_FUSE_ALL_1', RegEx='[gdx].......C........_.._......._............._...C............._.1.*', **dparams)
        t['vcciavmin'] = analogdctc(is_edc=True, name='vcciavmin', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_VCCIAVMIN.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_0P6V_MIN', Patlist='pth_dlvr_vcciavmin_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('704'), CtvPins='CPU_TDO', **dparams)
        t['vcciavmin_cpu1'] = analogdctc(is_edc=True, name='vcciavmin_cpu1', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_VCCIAVMIN.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_0P6V_MIN', Patlist='pth_dlvr_vcciavmin_list', Pins='VCCIA,IPC::CPU1_CCF_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU1_ATOM3_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU1_CORE2_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('704'), CtvPins='CPU1_TDO', **dparams)
        t['vcciavmin_calc'] = dlvrtrim(is_edc=True, name='vcciavmin_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='VCCIAVMIN', Mode='IREF_TRIM', **dparams)
        t['rampupdef'] = patmod(is_edc=False, name='rampupdef', BypassPort=1, ConfigurationFile='./InputFiles/PATCONFIG_NVL_S52C_PATMOD.setpoints.json', SetPoint='PS0_0P9V', **dparams)
        t['dlvrkillall_failind'] = dlvrtrim(is_edc=True, name='dlvrkillall_failind', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY("DLVR_KILLALL","DLVR_KILLALL_CSM")'), Mode='IREF_TRIM', **dparams)
        t['allkill_failind'] = screentc(is_edc=False, name='allkill_failind', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ScreenTestSet='FAIL_INDICATOR_S52C', ScreenTestsFile='./InputFiles/NVL_816_SCREEN_FAIL_INDICATOR.txt', **dparams)
        t['allkill_failind_csm'] = screentc(is_edc=False, name='allkill_failind_csm', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,1)'), ScreenTestSet='FAIL_INDICATOR_S52C_CSM', ScreenTestsFile='./InputFiles/NVL_816_SCREEN_FAIL_INDICATOR.txt', **dparams)
        t['fuseconfig_check'] = ctvdecoder(is_edc=False, name='fuseconfig_check', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/CTV_NVL_S52C_CLASS_FUSECHK.csv', CtvCapturePins='CPU_TDO,CPU1_TDO', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_dynamic_fuse_check_list', TimingsTc=IPCtiming, **dparams)
        t['dacflowfork'] = power(is_edc=True, name='dacflowfork', BypassPort=Spec('PTH_DLVR_CXPKGS9_Rules.DLVR_RUNCLASSHOT_ONLY(1,2)'), **dparams)


        ###Debug Flow Composite###
        debug_flow_fitems = list()
        offset = 0
        debug_flow_fitems.append(t['tap2reg_dump'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pwrgood_chk'].test.name)))
        debug_flow_fitems.append(t['pwrgood_chk'].get_fitem(r0=pFail(setbin=AUTO, goto=t['regcheck'].test.name)))
        debug_flow_fitems.append(t['regcheck'].get_fitem(**{**{f"r{i}": pFail(ret=1) for i in range(6)}, "r1": pPass()}))

        debug_flow_name = 'Debug_Flow_STARTANA1CPU'
        if composite_postfix:
            debug_flow_name = 'Debug_Flow_STARTANA1CPU'+ '_' + composite_postfix

        ###LVR_FF_STARTANA1CPU Composite###
        lvrff_fitems = list()
        offset = 0
        lvrff_fitems.append(t['anaprb_mrcsx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['anaprb_irefgen'].test.name)))
        lvrff_fitems.append(t['anaprb_irefgen'].get_fitem(r0=pFail(setbin=AUTO, goto=t['intlvr_sweep'].test.name)))
        lvrff_fitems.append(t['intlvr_sweep'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_alladc1_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_alladc1_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_alladc1_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_alladc1_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2dis_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2dis_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2dis_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2dis_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2ena_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2ena_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2ena_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2ena_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsadconly_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsadconly_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['lvr_adc_read'].test.name)))
        lvrff_fitems.append(t['lvr_adc_read'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        lvr_ff_flow_name = 'LVR_FF_STARTANA1CPU'
        if composite_postfix:
            lvr_ff_flow_name = 'LVR_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###LVR_STARTANA1CPU Composite###
        lvr_fitems = list()
        offset = 0
        lvr_fitems.append(t['anaprb_lvr'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_lvr_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        lvr_fitems.append(t['anaprb_lvr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=lvr_ff_flow_name), r1=pPass(ret=1)))
        lvr_fitems.append(Fitem('SAME', Flow(lvr_ff_flow_name, *lvrff_fitems), r0=pFail(ret=1)))

        lvr_flow_name = 'LVR_STARTANA1CPU'
        if composite_postfix:
            lvr_flow_name = 'LVR_STARTANA1CPU'+ '_' + composite_postfix

        ###IREF_FF_TRIM_STARTANA1CPU Composite ###
        ireftrimff_fitems = list()
        offset = 0
        ireftrimff_fitems.append(t['iref_pt1_manual'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_manual_calc'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_manual_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_manual_cpu1'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_manual_cpu1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_manual_cpu1_calc'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_manual_cpu1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_highr'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_highr'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_highr_cpu1'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_highr_cpu1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_highr_calc'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_highr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_trim_sweep'].test.name) ))
        ireftrimff_fitems.append(t['iref_trim_sweep'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        iref_ff_flow_name = 'IREFTRIM_FF_STARTANA1CPU'
        if composite_postfix:
            iref_ff_flow_name = 'IREFTRIM_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###ADC01_FF_STARTANA1CPU Composite ###
        adc01_fitems = list()
        offset = 0
        adc01_fitems.append(t['adc01_4pt'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_4pt_calc'].test.name)))
        adc01_fitems.append(t['adc01_4pt_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        adc01_ff_flow_name = 'ADC01_FF_STARTANA1CPU'
        if composite_postfix:
            adc01_ff_flow_name = 'ADC01_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###IREF_TRIM_STARTANA1CPU Composite ###
        ireftrim_fitems = list()
        offset = 0
        ireftrim_fitems.append(t['iref_pt1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_cpu1'].test.name)))
        ireftrim_fitems.append(t['iref_pt1_cpu1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_calc'].test.name)))
        ireftrim_fitems.append(t['iref_pt1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=iref_ff_flow_name)))
        ireftrim_fitems.append(t['iref_pt1_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ireftrim_fitems.append(t['adc01'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_calc'].test.name)))
        ireftrim_fitems.append(t['adc01_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_fuse'].test.name)))
        ireftrim_fitems.append(t['adc01_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ireftrim_fitems.append(t['adc01_chk_post'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_chk_post_calc'].test.name)))
        ireftrim_fitems.append(t['adc01_chk_post_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=adc01_ff_flow_name), r1=pPass(ret=1)))
        ireftrim_fitems.append(Fitem('SAME', Flow(iref_ff_flow_name, *ireftrimff_fitems), r0=pFail(goto=t['adc01'].test.name), r1=pPass(goto=t['adc01'].test.name)))
        ireftrim_fitems.append(Fitem('SAME', Flow(adc01_ff_flow_name, *adc01_fitems), r0=pFail(ret=1)))

        iref_flow_name = 'IREF_TRIM_STARTANA1CPU'
        if composite_postfix:
            iref_flow_name = 'IREF_TRIM_STARTANA1CPU'+ '_' + composite_postfix

        ### UGB_FF_STARTANA1CPU Composite ###
        ugbff_fitems = list()
        offset = 0
        ugbff_fitems.append(t['manual_ugb'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_ugb_calc'].test.name)))
        ugbff_fitems.append(t['manual_ugb_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_ugb_cpu1_calc'].test.name)))
        ugbff_fitems.append(t['manual_ugb_cpu1_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        ugbff_flow_name = 'UGB_FF_STARTANA1CPU'
        if composite_postfix:
            ugbff_flow_name = 'UGB_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### MRCSX_FF_STARTANA1CPU Composite ###
        mrcsxff_fitems = list()
        offset = 0
        mrcsxff_fitems.append(t['manual_mr'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_mr_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_mr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_mr_cpu1_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_mr_cpu1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_csx'].test.name)))
        mrcsxff_fitems.append(t['manual_csx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_csx_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_csx_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_csx_cpu1_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_csx_cpu1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range0'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range0_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range0_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range1'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range1_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range2'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range2'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range2_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range2_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        mrcsxff_flow_name = 'MRCSX_FF_STARTANA1CPU'
        if composite_postfix:
            mrcsxff_flow_name = 'MRCSX_FF_STARTANA1CPU'+ '_' + composite_postfix

        ### ANAPRBUGB_FF_STARTANA1CPU Compopsite ####
        anaprbugbff_fitems = list()
        offset = 0
        anaprbugbff_fitems.append(t['anaprb_ugb_cm408'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm408_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm408_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['anaprb_ugb_cm1408'].test.name)))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm1408'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm1408_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm1408_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        anaprbff_flow_name = 'ANAPRBUGB_FF_STARTANA1CPU'
        if composite_postfix:
            anaprbff_flow_name = 'ANAPRBUGB_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### DIGCOMP_FF_STARTANA1CPU Composite ###
        digcompff_fitems = list()
        offset = 0
        digcompff_fitems.append(t['hvls'].get_fitem(r0=pFail(setbin=AUTO, goto=t['clk_gating'].test.name)))
        digcompff_fitems.append(t['clk_gating'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_intcomp'].test.name)))
        digcompff_fitems.append(t['dfxtrim_intcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_intcomp_calc'].test.name)))
        digcompff_fitems.append(t['dfxtrim_intcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_digcomp'].test.name)))
        digcompff_fitems.append(t['manual_digcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_digcomp_calc'].test.name)))
        digcompff_fitems.append(t['manual_digcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_digcomp_cpu1_calc'].test.name)))
        digcompff_fitems.append(t['manual_digcomp_cpu1_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        digcompff_flow_name = 'DIGCOMP_FF_STARTANA1CPU'
        if composite_postfix:
            digcompff_flow_name = 'DIGCOMP_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### DFX_TRIM_STARTANA1CPU Composite #######
        dfxtrim_fitems = list()
        offset = 0
        dfxtrim_fitems.append(t['dfxtrim_ugb'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_ugb_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_ugb_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=ugbff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_ugb_fuse'].get_fitem(r0=pFail(setbin=2768)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=mrcsxff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx_fuse'].get_fitem(r0=pFail(setbin=2768)))
        dfxtrim_fitems.append(t['anaprb_ugb_cm928'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm928_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        dfxtrim_fitems.append(t['anaprb_ugb_cm928_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=anaprbff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_digcomp_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=digcompff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp_fuse'].get_fitem(r0=pFail(setbin=2768), r1=pPass(ret=1)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(ugbff_flow_name, *ugbff_fitems), r0=pFail(goto=t['dfxtrim_mrcsx'].test.name), r1=pPass(goto=t['dfxtrim_mrcsx'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(mrcsxff_flow_name, *mrcsxff_fitems), r0=pFail(goto=t['anaprb_ugb_cm928'].test.name), r1=pPass(goto=t['anaprb_ugb_cm928'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(anaprbff_flow_name, *anaprbugbff_fitems), r0=pFail(goto=t['dfxtrim_digcomp'].test.name), r1=pPass(goto=t['dfxtrim_digcomp'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(digcompff_flow_name, *digcompff_fitems), r0=pFail(ret=1)))

        dfxtrim_flow_name = 'DFX_TRIM_STARTANA1CPU'
        if composite_postfix:
            dfxtrim_flow_name = 'DFX_TRIM_STARTANA1CPU'+ '_' + composite_postfix

        ###DAC_CAL_STARTANA1CPU Composite###
        DAC_CAL = list()
        offset = 0
        DAC_CAL.append(t['dac_cal'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atomcores'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core1'].get_fitem(**{**{f"r{i}": pFail(setbin=2741, goto=t['dac_cal_core2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dac_cal_fuse'].test.name)))
        DAC_CAL.append(t['dac_cal_fuse'].get_fitem(r0=pFail(setbin=2768)))

        DAC_CAL_flow_name = 'DAC_CAL_STARTANA1CPU'
        if composite_postfix:
            DAC_CAL_flow_name = 'DAC_CAL_STARTANA1CPU'+ '_' + composite_postfix

        ###DAC_CHK_STARTANA1CPU Composite###
        DAC_CHK = list()
        offset = 0
        DAC_CHK.append(t['dac_chk'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atomcores'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atom0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom0'].get_fitem(**{**{f"r{i}": pFail(setbin=2742, goto=t['dac_chk_atom1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atom2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atom3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core2'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core2'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core3'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core3'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        DAC_CHK_flow_name = 'DAC_CHK_STARTANA1CPU'
        if composite_postfix:
            DAC_CHK_flow_name = 'DAC_CHK_STARTANA1CPU'+ '_' + composite_postfix

        ### DAC_STARTANA1CPU Composite ###
        DAC = list()
        DAC.append(t['dacflowfork'].get_fitem(r0=pFail(setbin=AUTO, goto=DAC_CAL_flow_name), r1=pPass(setbin=AUTO, goto=DAC_CAL_flow_name), r2=pPass(setbin=AUTO, goto=DAC_CHK_flow_name)))
        DAC.append(Fitem('SAME', Flow(DAC_CAL_flow_name, *DAC_CAL), r0=pFail(ret=0)))
        DAC.append(Fitem('SAME', Flow(DAC_CHK_flow_name, *DAC_CHK), r0=pFail(ret=1)))

        DAC_flow_name = 'DAC_STARTANA1CPU'
        if composite_postfix:
            DAC_flow_name = 'DAC_STARTANA1CPU'+ '_' + composite_postfix

        ###ICC_PER_BRANCH_STARTANA1CPU Composite###
        ICC_PER_BRANCH = list()
        offset = 0
        ICC_PER_BRANCH.append(t['preibr_idle'].get_fitem(**{**{f"r{i}": pFail(setbin=2765, goto=t['preibr_idle_cpu1'].test.name) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['preibr_idle_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=2765, goto=t['pre_ibr'].test.name) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['pre_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['pre_ibr_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['pre_ibr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pre_ibr_fuse'].test.name)))
        ICC_PER_BRANCH.append(t['pre_ibr_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ICC_PER_BRANCH.append(t['post_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['post_ibr_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['post_ibr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['post_ibr_csm'].test.name)))
        ICC_PER_BRANCH.append(t['post_ibr_csm'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        ICC_PER_BRANCH_flow_name = 'ICC_PER_BRANCH_STARTANA1CPU'
        if composite_postfix:
            ICC_PER_BRANCH_flow_name = 'ICC_PER_BRANCH_STARTANA1CPU'+ '_' + composite_postfix

        ###GANG_CHK_STARTANA1CPU Composite###
        GANG_CHK = list()
        offset = 0
        GANG_CHK.append(t['gang'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        GANG_CHK.append(t['gang_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        GANG_CHK.append(t['gang_calc'].get_fitem(r0=pFail(setbin=2765, ret=1)))

        GANG_CHK_flow_name = 'GANG_CHK_STARTANA1CPU'
        if composite_postfix:
            GANG_CHK_flow_name = 'GANG_CHK_STARTANA1CPU'+ '_' + composite_postfix

        ### MAIN PART TO CREATE FLOW ON DLVR###
        hvm_fitems = list()
        hvm_fitems.append(Fitem('SAME', Flow(debug_flow_name, *debug_flow_fitems), r0=pFail(goto=t['gsds_inject'].test.name)))
        hvm_fitems.append(t['gsds_inject'].get_fitem(r0=pFail(setbin=AUTO, goto=t['setgsds'].test.name)))
        hvm_fitems.append(t['setgsds'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['setgsds_cpu1'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['setgsds_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['binconv_prim'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['binconv_prim'].get_fitem(r0=pFail(setbin=AUTO, goto=t['binconv_all'].test.name)))
        hvm_fitems.append(t['binconv_all'].get_fitem(r0=pFail(setbin=AUTO, goto=t['default'].test.name)))
        hvm_fitems.append(t['default'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['open_loop'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['voutmeas'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['voutmeas_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        hvm_fitems.append(t['voutmeas_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=lvr_flow_name)))
        hvm_fitems.append(Fitem('SAME', Flow(lvr_flow_name, *lvr_fitems), r0=pFail(goto=t['pod_vil'].test.name)))
        hvm_fitems.append(t['pod_vil'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pod_vil_cpu1'].test.name), r2=pFail(setbin=AUTO, goto=t['pod_vil_cpu1'].test.name)))
        hvm_fitems.append(t['pod_vil_cpu1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pod_vih'].test.name), r2=pFail(setbin=AUTO, goto=t['pod_vih'].test.name)))
        hvm_fitems.append(t['pod_vih'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['pod_vih_cpu1'].test.name) for i in range(8)}, "r1": pPass()}))
        hvm_fitems.append(t['pod_vih_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['pod'].test.name) for i in range(8)}, "r1": pPass()}))
        hvm_fitems.append(t['pod'].get_fitem(r0=pFail(setbin=AUTO, goto=iref_flow_name)))
        hvm_fitems.append(Fitem('SAME', Flow(iref_flow_name, *ireftrim_fitems), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(dfxtrim_flow_name, *dfxtrim_fitems), r0=pFail(ret=0)))
        hvm_fitems.append(t['close_loop'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(Fitem('SAME', Flow(DAC_flow_name, *DAC), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(ICC_PER_BRANCH_flow_name, *ICC_PER_BRANCH), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(GANG_CHK_flow_name, *GANG_CHK), r0=pFail(ret=0)))
        hvm_fitems.append(t['vcciavmin'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['vcciavmin_cpu1'].test.name) for i in range(6)}, "r1": pPass()}))
        hvm_fitems.append(t['vcciavmin_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['vcciavmin_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        hvm_fitems.append(t['vcciavmin_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['rampupdef'].test.name)))
        hvm_fitems.append(t['rampupdef'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['sds2class_gsds'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['sds2class_gsds_cpu1'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['sds2class_gsds_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['s2cdelta'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['s2cdelta'].get_fitem(r0=pFail(setbin=AUTO, goto=t['setdff'].test.name)))
        hvm_fitems.append(t['setdff'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['fuseconfig_all_x1'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['setdff_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['fuseconfig_all_x1'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['fuseconfig_all_x1'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['dlvrkillall_failind'].get_fitem(r0=pFail(setbin=AUTO, goto=t['allkill_failind'].test.name)))
        hvm_fitems.append(t['allkill_failind'].get_fitem(**{**{f"r{i}": pFail(setbin=b) for i, b in {0:27620024,2:27520087,3:27530374,4:27710234,5:27560261,6:27620025,7:27571302,8:27650578,9:27636310,10:27610033,11:27666619,12:27676730}.items()}, "r1": pPass()}))
        hvm_fitems.append(t['allkill_failind_csm'].get_fitem(**{**{f"r{i}": pFail(setbin=b) for i, b in {0:27620026,2:27520088,3:27530375,4:27710235,5:27560262,6:27620027,7:27571303,8:27650579,9:27636311,10:27610034,11:27666620,12:27676731}.items()}, "r1": pPass()}))
        hvm_fitems.append(t['fuseconfig_check'].get_fitem(r0=pFail(setbin=27676724), r2=pFail(setbin=27676725),r3=pFail(setbin=27676726),r4=pFail(setbin=27676727),r5=pFail(setbin=27676728)))

        Flow(flow_name, *hvm_fitems,  dtag='STARTANA1CPU_SubFlow')

    def get_s52c_lttccpu_flow(self, flow_name, module_name='LTTCCPU', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        dlvrtrim = DlvrTrimCalc_TestBuilder
        analogdctc = AnalogDcTC_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test

        t['dac_chk_atomcores'] = analogdctc(is_edc=True, name='dac_chk_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU1_ATOM3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_evencore'] = analogdctc(is_edc=True, name='dac_chk_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU1_CORE2_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_oddcore'] = analogdctc(is_edc=True, name='dac_chk_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU_CORE3_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk_ringprim'] = analogdctc(is_edc=True, name='dac_chk_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P3V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU1_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['dac_chk'] = dlvrtrim(is_edc=False, name='dac_chk', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_DCERROR.json', ConfigSet='DAC_CHK_CSM', Mode='DAC_CAL', **dparams)
        t['pre_ibr_idle'] = analogdctc(is_edc=True, name='pre_ibr_idle', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_PRE_IBR_IDLE.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['pre_ibr_idle_cpu1'] = analogdctc(is_edc=True, name='pre_ibr_idle_cpu1', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_PRE_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('4109'), CtvPins='CPU_TDO,CPU1_TDO,CPU1_TDO', **dparams)
        t['post_ibr'] = analogdctc(is_edc=False, name='post_ibr', DataBaseFile='./InputFiles/ANAMEAS_NVL_816_CLASS_POST_IBR_HX.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_postIBR_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_ATOM2_DLVROUT,IPC::CPU_ATOM3_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT,IPC::CPU_CORE2_DLVROUT,IPC::CPU_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=8705, CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['post_ibr_cpu1'] = analogdctc(is_edc=False, name='post_ibr_cpu1', DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_POST_IBR.json', LevelsTc='IPC::PTH_DLVR_CXPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_postIBR_list', Pins='VCCIA,IPC::CPU1_CCF_DLVROUT,IPC::CPU1_ATOM0_DLVROUT,IPC::CPU1_ATOM1_DLVROUT,IPC::CPU1_ATOM2_DLVROUT,IPC::CPU1_ATOM3_DLVROUT,IPC::CPU1_CORE0_DLVROUT,IPC::CPU1_CORE1_DLVROUT,IPC::CPU1_CORE2_DLVROUT,IPC::CPU1_CORE3_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CXPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('8705'), CtvPins='CPU_TDO,CPU1_TDO', **dparams)
        t['post_ibr_calc'] = dlvrtrim(is_edc=False, name='post_ibr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_S52C_POST_TRIM.json', ConfigSet='POST_IBR_CSM', Mode='IREF_TRIM', **dparams)


        #####DAC_CHK_LTTCCPU Composite####
        dacchk_fitems = list()
        dacchk_fitems.append(t['dac_chk_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk'].get_fitem(r0=pFail(setbin=2757)))

        DACCHK_flow_name = 'DACCHK_LTTCCPU'
        if composite_postfix:
            DACCHK_flow_name = 'DACCHK_LTTCCPU'+ '_' + composite_postfix

        #####ICC_PER_BRANCH_LTTCCPU Composite####
        icc_fitems = list()
        icc_fitems.append(t['pre_ibr_idle'].get_fitem(**{**{f"r{i}": pFail(setbin=2765, goto=t['pre_ibr_idle_cpu1'].test.name) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['pre_ibr_idle_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=2765, goto=t['post_ibr'].test.name) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['post_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['post_ibr_cpu1'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['post_ibr_calc'].get_fitem(r0=pFail(setbin=2765)))

        icc_flow_name = 'ICC_PER_BRANCH_LTTCCPU'
        if composite_postfix:
            icc_flow_name = 'ICC_PER_BRANCH_LTTCCPU'+ '_' + composite_postfix

        ###LTTC Main Flow#####
        lttc_fitems = list()
        lttc_fitems.append(Fitem('SAME', Flow(DACCHK_flow_name, *dacchk_fitems), r0=pFail(ret=0)))
        lttc_fitems.append(Fitem('SAME', Flow(icc_flow_name, *icc_fitems), r0=pFail(ret=0)))
        Flow(flow_name, *lttc_fitems, dtag='LTTCCPU_SubFlow')

#==============================================================================H/P/S16C=====================================================================================================
    def get_48_startana1cpu_flow(self, flow_name, module_name='STARTANA1CPU', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        ctvdecoder = CtvDecoderSpm_TestBuilder
        gsdsdff = PTHGetSetGsdsDffTC_TestBuilder
        patmod = PrimePatConfigTestMethodPatmod_TestBuilder
        fuseconfig = PrimePatConfigTestMethodFuseConfig_TestBuilder
        dlvrtrim = DlvrTrimCalc_TestBuilder
        func = PrimeFunctionalTestMethod_TestBuilder
        screentc = ScreenTC_TestBuilder
        analogdctc = AnalogDcTC_TestBuilder
        vmintc = VminTC_TestBuilder
        vminpass2failtc = VminPass2FailTC_TestBuilder
        power = PowerSequenceHandler_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test



        ### list of tests
        t['tap2reg_dump'] = ctvdecoder(is_edc=True, name='tap2reg_dump', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_TAP2REG_DUMP.csv', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_regdump_list', TimingsTc=IPCtiming, **dparams)
        t['pwrgood_chk'] = ctvdecoder(is_edc=True, name='pwrgood_chk', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_PWRGOOD_CHK.csv', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_OBS_06', Patlist='pth_dlvr_pwrgood_list', TimingsTc=IPCtiming, **dparams)
        t['regcheck'] = func(is_edc=True, name='regcheck', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_reg_check_list', TimingsTc=IPCtiming, **dparams)
        t['gsds_inject'] = dlvrtrim(is_edc=True, name='gsds_inject', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='GSDS_INJECT', Mode='IREF_TRIM', **dparams)
        t['setgsds'] = gsdsdff(is_edc=True, name='setgsds', ConfigurationFile=Spec('PTH_DLVR_CX48_Rules.Select_RCCOLD ("./InputFiles/PTHGSDS_NVL_S28C_DFF2GSDS_RC.json","./InputFiles/PTHGSDS_NVL_S28C_DFF2GSDS.json")'), OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), **dparams)
        t['binconv_prim'] = dlvrtrim(is_edc=True, name='binconv_prim', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='BINCONV_PRIM', Mode='IREF_TRIM', **dparams)
        t['binconv_all'] = dlvrtrim(is_edc=True, name='binconv_all', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='BINCONV_ALL', Mode='IREF_TRIM', **dparams)
        t['default'] = fuseconfig(is_edc=False, name='default', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='DLVR_FUSE_ALL_1', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['open_loop'] = patmod(is_edc=False, name='open_loop', ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_PATMOD.setpoints.json', SetPoint='PS0_0V', **dparams)
        t['voutmeas'] = analogdctc(is_edc=True, name='voutmeas', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_VOUTMEAS.json', Patlist='pth_dlvr_vout_float_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['voutmeas_calc'] = dlvrtrim(is_edc=True, name='voutmeas_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='VOUTMEAS', Mode='IREF_TRIM', **dparams)
        t['cmem_lvr_max_alladc1_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_alladc1_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_ANAPRB_LVR_ADC1_CH1.csv', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_anaprb_bglvr_allch1_adc1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_alladc1_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_alladc1_ch0', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_ANAPRB_LVR_ADC1_CH0.csv', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_anaprb_bglvr_allch0_adc1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2dis_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2dis_ch0', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_AGSVIEW_CH0.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch0_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2dis_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2dis_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_AGSVIEW_CH1.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch1_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2ena_ch0'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2ena_ch0', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_AGSVIEW_L2EN_CH0.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch0L2en_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsview2adcl2ena_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsview2adcl2ena_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_AGSVIEW_L2EN_CH1.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsview2adcch1L2en_list', TimingsTc=IPCtiming, **dparams)
        t['cmem_lvr_max_agsadconly_ch1'] = ctvdecoder(is_edc=True, name='cmem_lvr_max_agsadconly_ch1', BypassPort=1, ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_AGSBGBUFADC0.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_bglvr_agsgbugadc0_list', TimingsTc=IPCtiming, **dparams)
        t['lvr_adc_read'] = dlvrtrim(is_edc=True, name='lvr_adc_read', BypassPort=1, ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='LVR', Mode='IREF_TRIM', **dparams)
        t['anaprb_mrcsx'] = ctvdecoder(is_edc=True, name='anaprb_mrcsx', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_ANAPRB_MRCSX.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_mr_csx_amp_list', TimingsTc=IPCtiming, **dparams)
        t['anaprb_irefgen'] = ctvdecoder(is_edc=True, name='anaprb_irefgen', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_ANAPRB_IREFGEN.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_anaprb_irefgen_list', TimingsTc=IPCtiming, **dparams)
        t['intlvr_sweep'] = ctvdecoder(is_edc=True, name='intlvr_sweep', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_INTLVR_DACSEL_SWEEP.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_intlvr_dacsel_sweep_list', TimingsTc=IPCtiming, **dparams)
        t['anaprb_lvr'] = analogdctc(is_edc=True, name='anaprb_lvr', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_ANAPRB_LVR.json', Patlist='pth_dlvr_anaprb_bglvr_list', Pins='IPC::CPU_OBS_02,IPC::CPU_OBS_03', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('480'), CtvPins='CPU_TDO', **dparams)
        t['anaprb_lvr_calc'] = dlvrtrim(is_edc=True, name='anaprb_lvr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='ANAPRB_LVR', Mode='IREF_TRIM', **dparams)
        t['pod_vih'] = vmintc(is_edc=True, name='pod_vih', EndVoltageLimits='0.7', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_pod_vih_list', StartVoltages='0.3', StepSize=Spec('0.05'), TestMode='SingleVmin', TimingsTc=IPCtiming, VoltageTargets='VCCIA', VminResult='CPU_POD_VIH', **dparams)
        t['pod_vil'] = vminpass2failtc(is_edc=True, name='pod_vil', Patlist='pth_dlvr_pod_vih_list', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P0V_MIN', TimingsTc=IPCtiming, VoltageTargets='VCCIA', FivrCondition='', StartVoltage='0.5', EndVoltage='0.2', StepSize=Spec('-0.05'), VminResult='CPU_POD_VIL', **dparams)
        t['pod'] = dlvrtrim(is_edc=True, name='pod', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='POD', Mode='IREF_TRIM', **dparams)
        t['hvls'] = ctvdecoder(is_edc=True, name='hvls', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_HVLS.csv', CtvCapturePins='CPU_OBS_07', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_hvls_list', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_manual'] = ctvdecoder(is_edc=True, name='iref_pt1_manual', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_MANUAL_IREF_PT1.csv', CtvCapturePins='CPU_OBS_06', Patlist='pth_dlvr_ireftrim_pt1_manual_list', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_manual_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_manual_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_MANUAL_TRIM.json', ConfigSet='IREFPT1_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['iref_pt1_highr'] = ctvdecoder(is_edc=True, name='iref_pt1_highr', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ireftrim_range3_pt1_list', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_highr_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_highr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("IREF_TRIM_PT1","IREF_TRIM_PT1_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_pt1'] = ctvdecoder(is_edc=True, name='iref_pt1', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_IREFTRIM_PT1_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ireftrim_pt1_list', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['iref_pt1_calc'] = dlvrtrim(is_edc=True, name='iref_pt1_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("IREF_TRIM_PT1","IREF_TRIM_PT1_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_pt1_fuse'] = fuseconfig(is_edc=False, name='iref_pt1_fuse', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='IREF_PT1', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['adc01_4pt'] = ctvdecoder(is_edc=True, name='adc01_4pt', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_ADC01_4PT.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P4V_MIN', Patlist='pth_dlvr_adc01_4pt_list', TimingsTc=IPCtiming, **dparams)
        t['adc01_4pt_calc'] = dlvrtrim(is_edc=True, name='adc01_4pt_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='ADC_4PT', Mode='IREF_TRIM', **dparams)
        t['adc01'] = ctvdecoder(is_edc=True, name='adc01', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_ADC01_2PT.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P4V_MIN', Patlist='pth_dlvr_adc01_trim_list', TimingsTc=IPCtiming, **dparams)
        t['adc01_calc'] = dlvrtrim(is_edc=True, name='adc01_calc', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("ADC_2PT","ADC_2PT_CSM")'), Mode='IREF_TRIM', **dparams)
        t['adc01_fuse'] = fuseconfig(is_edc=False, name='adc01_fuse', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='ADC_FUSE', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['adc01_chk_post'] = ctvdecoder(is_edc=True, name='adc01_chk_post', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_ADC01_CHK_SNDT.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P1V_MIN', Patlist='pth_dlvr_adc01_chk_sndt_list', TimingsTc=IPCtiming, ApplyEndSequence='DISABLED', **dparams)
        t['adc01_chk_post_calc'] = dlvrtrim(is_edc=True, name='adc01_chk_post_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("ADC_CHK","ADC_CHK_CSM")'), Mode='IREF_TRIM', **dparams)
        t['iref_trim_sweep'] = ctvdecoder(is_edc=True, name='iref_trim_sweep', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_IREFTRIM_SWEEP_ALL.csv', CtvCapturePins='CPU_TDO', Patlist='pth_dlvr_ibias_sweep_extR_list', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', TimingsTc=IPCtiming, **dparams)
        t['manual_ugb'] = ctvdecoder(is_edc=True, name='manual_ugb', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_MANUAL_UGB.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_ugbtrim_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_ugb_calc'] = dlvrtrim(is_edc=True, name='manual_ugb_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_MANUAL_TRIM.json', ConfigSet='UGB_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_mr'] = ctvdecoder(is_edc=True, name='manual_mr', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_MANUAL_MR.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_mr_amp_vsxtop_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_mr_calc'] = dlvrtrim(is_edc=True, name='manual_mr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_MANUAL_TRIM.json', ConfigSet='MR_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['manual_csx'] = ctvdecoder(is_edc=True, name='manual_csx', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_MANUAL_CSX.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_csx_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_csx_calc'] = dlvrtrim(is_edc=True, name='manual_csx_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_MANUAL_TRIM.json', ConfigSet='CSX_MANUAL', Mode='MANUAL_TRIM', **dparams)
        for rge in ['range0','range1','range2']:
            t[f'dfxtrim_mrcsx_{rge}'] = ctvdecoder(is_edc=True, name=f'dfxtrim_mrcsx_{rge}', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_DFX_MRCSXTRIM.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist=f'pth_dlvr_mrcsxtrim_{rge}_dfx_list', TimingsTc=IPCtiming, **dparams)
            t[f'dfxtrim_mrcsx_{rge}_calc'] = dlvrtrim(is_edc=True, name=f'dfxtrim_mrcsx_{rge}_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("MRCSXTRIM","MRCSXTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_ugb'] = ctvdecoder(is_edc=True, name='dfxtrim_ugb', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_DFX_UGBTRIM.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_ugbtrim_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_ugb_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_ugb_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("UGBTRIM","UGBTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_ugb_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_ugb_fuse', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='UGB', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['dfxtrim_mrcsx'] = ctvdecoder(is_edc=True, name='dfxtrim_mrcsx', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_DFX_MRCSXTRIM.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_mrcsxtrim_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_mrcsx_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_mrcsx_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("MRCSXTRIM","MRCSXTRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_mrcsx_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_mrcsx_fuse', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='MRCSX', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        for CM in ['408','928','1408']:
            t[f'anaprb_ugb_cm{CM}'] = analogdctc(is_edc=True, name=f'anaprb_ugb_cm{CM}', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_ANAPRB_UGB.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist=f'pth_dlvr_anaprb_ugb_{CM}_list', Pins='IPC::CPU_OBS_02,IPC::CPU_OBS_03', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('300'), CtvPins='CPU_TDO', **dparams)
            t[f'anaprb_ugb_cm{CM}_calc'] = dlvrtrim(is_edc=True, name=f'anaprb_ugb_cm{CM}_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='ANAPRB_UGB', Mode='IREF_TRIM', **dparams)
        t['dfxtrim_intcomp'] = ctvdecoder(is_edc=True, name='dfxtrim_intcomp', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_DFX_INTCOMP.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_internal_comp_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_intcomp_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_intcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='INTERNAL_DFX_TRIM', Mode='IREF_TRIM', **dparams)
        t['manual_digcomp'] = ctvdecoder(is_edc=True, name='manual_digcomp', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_MANUAL_DIGCOMP.csv', CtvCapturePins='CPU_OBS_06', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_digital_comp_manual_list', TimingsTc=IPCtiming, **dparams)
        t['manual_digcomp_calc'] = dlvrtrim(is_edc=True, name='manual_digcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_MANUAL_TRIM.json', ConfigSet='DIGCOMP_MANUAL', Mode='MANUAL_TRIM', **dparams)
        t['dfxtrim_digcomp'] = ctvdecoder(is_edc=True, name='dfxtrim_digcomp', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_DFX_DIGCOMP.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_digital_comp_dfx_list', TimingsTc=IPCtiming, **dparams)
        t['dfxtrim_digcomp_calc'] = dlvrtrim(is_edc=True, name='dfxtrim_digcomp_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("DIG_DFX_TRIM","DIG_DFX_TRIM_CSM")'), Mode='IREF_TRIM', **dparams)
        t['dfxtrim_digcomp_fuse'] = fuseconfig(is_edc=False, name='dfxtrim_digcomp_fuse', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='DIGITAL_COMP', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['clk_gating'] = ctvdecoder(is_edc=True, name='clk_gating', ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_CLK_GATING.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_clk_gating_list', TimingsTc=IPCtiming, **dparams)
        t['close_loop'] = patmod(is_edc=False, name='close_loop', ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_PATMOD.setpoints.json', SetPoint='PS0_0P9V', **dparams)
        t['dac_cal'] = analogdctc(is_edc=True, name='dac_cal', BypassPort=1, DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ALL.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('720'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_atomcores'] = analogdctc(is_edc=True, name='dac_cal_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_evencore'] = analogdctc(is_edc=True, name='dac_cal_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_oddcore'] = analogdctc(is_edc=True, name='dac_cal_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_cal_atom{num}'] = analogdctc(is_edc=True, name=f'dac_cal_atom{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ATOM{num}.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_atom{num}_list', Pins=f'IPC::CPU_ATOM{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_cal_core{num}'] = analogdctc(is_edc=True, name=f'dac_cal_core{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_CORE{num}P.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_core{num}_list', Pins=f'IPC::CPU_CORE{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_ringprim'] = analogdctc(is_edc=True, name='dac_cal_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_cal_calc'] = dlvrtrim(is_edc=True, name='dac_cal_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_DCERROR.json', ConfigSet='DAC_CAL', Mode='DAC_CAL', **dparams)
        t['dac_cal_fuse'] = fuseconfig(is_edc=False, name='dac_cal_fuse', ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='DVDAC', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['dac_chk'] = analogdctc(is_edc=True, name='dac_chk', BypassPort=1, DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ALL.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_list', Pins='IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('720'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_atomcores'] = analogdctc(is_edc=True, name='dac_chk_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_evencore'] = analogdctc(is_edc=True, name='dac_chk_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_oddcore'] = analogdctc(is_edc=True, name='dac_chk_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_chk_atom{num}'] = analogdctc(is_edc=True, name=f'dac_chk_atom{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ATOM{num}.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_atom{num}_list', Pins=f'IPC::CPU_ATOM{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO', **dparams)
        for num in range(4):
            t[f'dac_chk_core{num}'] = analogdctc(is_edc=True, name=f'dac_chk_core{num}', BypassPort=1, DataBaseFile=f'./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_CORE{num}P.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist=f'pth_dlvr_dac_cal_core{num}_list', Pins=f'IPC::CPU_CORE{num}_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2349'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_ringprim'] = analogdctc(is_edc=True, name='dac_chk_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_calc'] = dlvrtrim(is_edc=True, name='dac_chk_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_DCERROR.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("DAC_CHK","DAC_CHK_CSM")'), Mode='DAC_CAL', **dparams)
        t['preibr_idle'] = analogdctc(is_edc=True, name='preibr_idle', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_PRE_IBR_IDLE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('1760'), CtvPins='CPU_TDO', **dparams)
        t['pre_ibr'] = analogdctc(is_edc=False, name='pre_ibr', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_PRE_IBR.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_preIBR_HX_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('960'), CtvPins='CPU_TDO', **dparams)
        t['pre_ibr_calc'] = dlvrtrim(is_edc=True, name='pre_ibr_calc', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='PRE_IBR', Mode='IREF_TRIM', **dparams)
        t['pre_ibr_fuse'] = fuseconfig(is_edc=False, name='pre_ibr_fuse', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='DVMRBF', RegEx='.*_longreset_fuseoverride_MCpth_MCpthDLVR', **dparams)
        t['post_ibr'] = analogdctc(is_edc=False, name='post_ibr', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_POST_IBR.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_postIBR_HX_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('3460'), CtvPins='CPU_TDO', **dparams)
        t['post_ibr_calc'] = dlvrtrim(is_edc=True, name='post_ibr_calc', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='POST_IBR', Mode='IREF_TRIM', **dparams)
        t['post_ibr_csm'] = dlvrtrim(is_edc=True, name='post_ibr_csm', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='POST_IBR_CSM', Mode='IREF_TRIM', **dparams)
        t['gang'] = analogdctc(is_edc=False, name='gang', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_GANG_IBR.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_GangedRing_IPB_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('400'), CtvPins='CPU_TDO', **dparams)
        t['gang_calc'] = dlvrtrim(is_edc=True, name='gang_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='GANG', Mode='IREF_TRIM', **dparams)
        t['sds2class_gsds'] = gsdsdff(is_edc=True, name='sds2class_gsds', ConfigurationFile='./InputFiles/PTHGSDS_NVL_S28C_DFF2GSDS_SORT.json', OPType='DFF2GSDS', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), **dparams)
        t['s2cdelta'] = dlvrtrim(is_edc=True, name='s2cdelta', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='S2CDELTA', Mode='IREF_TRIM', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), **dparams)
        t['setdff'] = gsdsdff(is_edc=True, name='setdff', ConfigurationFile=Spec('PTH_DLVR_CX48_Rules.Select_RCHOT ("./InputFiles/PTHGSDS_NVL_S28C_GSDS2DFF_CLASS_RC.json","./InputFiles/PTHGSDS_NVL_S28C_GSDS2DFF_CLASS.json")'), OPType='GSDS2DFF', PreInstance='SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")', BypassPort=Spec('__shared__::GlobalRule.primaryoptype(-1,-1,1,1,1,1,1,1,1,1)'), **dparams)
        t['fuseconfig_all_x1'] = fuseconfig(is_edc=False, name='fuseconfig_all_x1', ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint='DLVR_FUSE_ALL_1', RegEx='[gdx].......C........_.._......._............._...C............._.1.*', **dparams)
        t['vcciavmin'] = analogdctc(is_edc=True, name='vcciavmin', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_VCCIAVMIN.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_0P6V_MIN', Patlist='pth_dlvr_vcciavmin_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('352'), CtvPins='CPU_TDO', **dparams)
        t['vcciavmin_calc'] = dlvrtrim(is_edc=True, name='vcciavmin_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='VCCIAVMIN', Mode='IREF_TRIM', **dparams)
        t['rampupdef'] = patmod(is_edc=False, name='rampupdef', BypassPort=1, ConfigurationFile='./InputFiles/PATCONFIG_NVL_48_PATMOD.setpoints.json', SetPoint='PS0_0P9V', **dparams)
        t['dlvrkillall_failind'] = dlvrtrim(is_edc=True, name='dlvrkillall_failind', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY("DLVR_KILLALL","DLVR_KILLALL_CSM")'), Mode='IREF_TRIM', **dparams)
        t['allkill_failind'] = screentc(is_edc=False, name='allkill_failind', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ScreenTestSet='FAIL_INDICATOR', ScreenTestsFile='./InputFiles/NVL_48_SCREEN_FAIL_INDICATOR.txt', **dparams)
        t['allkill_failind_csm'] = screentc(is_edc=False, name='allkill_failind_csm', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(1,-1)'), ScreenTestSet='FAIL_INDICATOR_CSM', ScreenTestsFile='./InputFiles/NVL_48_SCREEN_FAIL_INDICATOR.txt', **dparams)
        t['fuseconfig_check'] = ctvdecoder(is_edc=False, name='fuseconfig_check', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(-1,1)'), ConfigurationFile='./InputFiles/CTV_NVL_48_CLASS_FUSECHK.csv', CtvCapturePins='CPU_TDO', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_dynamic_fuse_check_list', TimingsTc=IPCtiming, **dparams)
        t['dacflowfork'] = power(is_edc=True, name='dacflowfork', BypassPort=Spec('PTH_DLVR_CX48_Rules.DLVR_RUNCLASSHOT_ONLY(1,2)'), **dparams)


        ###Debug Flow Composite###
        debug_flow_fitems = list()
        offset = 0
        debug_flow_fitems.append(t['tap2reg_dump'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pwrgood_chk'].test.name)))
        debug_flow_fitems.append(t['pwrgood_chk'].get_fitem(r0=pFail(setbin=AUTO, goto=t['regcheck'].test.name)))
        debug_flow_fitems.append(t['regcheck'].get_fitem(**{**{f"r{i}": pFail(ret=1) for i in range(6)}, "r1": pPass()}))

        debug_flow_name = 'Debug_Flow_STARTANA1CPU'
        if composite_postfix:
            debug_flow_name = 'Debug_Flow_STARTANA1CPU'+ '_' + composite_postfix

        ###LVR_FF_STARTANA1CPU Composite###
        lvrff_fitems = list()
        offset = 0
        lvrff_fitems.append(t['anaprb_mrcsx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['anaprb_irefgen'].test.name)))
        lvrff_fitems.append(t['anaprb_irefgen'].get_fitem(r0=pFail(setbin=AUTO, goto=t['intlvr_sweep'].test.name)))
        lvrff_fitems.append(t['intlvr_sweep'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_alladc1_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_alladc1_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_alladc1_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_alladc1_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2dis_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2dis_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2dis_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2dis_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2ena_ch0'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2ena_ch0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsview2adcl2ena_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsview2adcl2ena_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['cmem_lvr_max_agsadconly_ch1'].test.name)))
        lvrff_fitems.append(t['cmem_lvr_max_agsadconly_ch1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['lvr_adc_read'].test.name)))
        lvrff_fitems.append(t['lvr_adc_read'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        lvr_ff_flow_name = 'LVR_FF_STARTANA1CPU'
        if composite_postfix:
            lvr_ff_flow_name = 'LVR_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###LVR_STARTANA1CPU Composite###
        lvr_fitems = list()
        offset = 0
        lvr_fitems.append(t['anaprb_lvr'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_lvr_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        lvr_fitems.append(t['anaprb_lvr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=lvr_ff_flow_name), r1=pPass(ret=1)))
        lvr_fitems.append(Fitem('SAME', Flow(lvr_ff_flow_name, *lvrff_fitems), r0=pFail(ret=1)))

        lvr_flow_name = 'LVR_STARTANA1CPU'
        if composite_postfix:
            lvr_flow_name = 'LVR_STARTANA1CPU'+ '_' + composite_postfix

        ###IREF_FF_TRIM_STARTANA1CPU Composite ###
        ireftrimff_fitems = list()
        offset = 0
        ireftrimff_fitems.append(t['iref_pt1_manual'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_manual_calc'].test.name)))
        ireftrimff_fitems.append(t['iref_pt1_manual_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_highr'].test.name) ))
        ireftrimff_fitems.append(t['iref_pt1_highr'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_highr_calc'].test.name)  ))
        ireftrimff_fitems.append(t['iref_pt1_highr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_trim_sweep'].test.name) ))
        ireftrimff_fitems.append(t['iref_trim_sweep'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        iref_ff_flow_name = 'IREFTRIM_FF_STARTANA1CPU'
        if composite_postfix:
            iref_ff_flow_name = 'IREFTRIM_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###ADC01_FF_STARTANA1CPU Composite ###
        adc01_fitems = list()
        offset = 0
        adc01_fitems.append(t['adc01_4pt'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_4pt_calc'].test.name)))
        adc01_fitems.append(t['adc01_4pt_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        adc01_ff_flow_name = 'ADC01_FF_STARTANA1CPU'
        if composite_postfix:
            adc01_ff_flow_name = 'ADC01_FF_STARTANA1CPU'+ '_' + composite_postfix

        ###IREF_TRIM_STARTANA1CPU Composite ###
        ireftrim_fitems = list()
        offset = 0
        ireftrim_fitems.append(t['iref_pt1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['iref_pt1_calc'].test.name)))
        ireftrim_fitems.append(t['iref_pt1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=iref_ff_flow_name)))
        ireftrim_fitems.append(t['iref_pt1_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ireftrim_fitems.append(t['adc01'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_calc'].test.name)))
        ireftrim_fitems.append(t['adc01_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_fuse'].test.name)))
        ireftrim_fitems.append(t['adc01_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ireftrim_fitems.append(t['adc01_chk_post'].get_fitem(r0=pFail(setbin=AUTO, goto=t['adc01_chk_post_calc'].test.name)))
        ireftrim_fitems.append(t['adc01_chk_post_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=adc01_ff_flow_name), r1=pPass(ret=1)))
        ireftrim_fitems.append(Fitem('SAME', Flow(iref_ff_flow_name, *ireftrimff_fitems), r0=pFail(goto=t['adc01'].test.name), r1=pPass(goto=t['adc01'].test.name)))
        ireftrim_fitems.append(Fitem('SAME', Flow(adc01_ff_flow_name, *adc01_fitems), r0=pFail(ret=1)))

        iref_flow_name = 'IREF_TRIM_STARTANA1CPU'
        if composite_postfix:
            iref_flow_name = 'IREF_TRIM_STARTANA1CPU'+ '_' + composite_postfix

        ### UGB_FF_STARTANA1CPU Composite ###
        ugbff_fitems = list()
        offset = 0
        ugbff_fitems.append(t['manual_ugb'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_ugb_calc'].test.name)))
        ugbff_fitems.append(t['manual_ugb_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        ugbff_flow_name = 'UGB_FF_STARTANA1CPU'
        if composite_postfix:
            ugbff_flow_name = 'UGB_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### MRCSX_FF_STARTANA1CPU Composite ###
        mrcsxff_fitems = list()
        offset = 0
        mrcsxff_fitems.append(t['manual_mr'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_mr_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_mr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_csx'].test.name)))
        mrcsxff_fitems.append(t['manual_csx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_csx_calc'].test.name)))
        mrcsxff_fitems.append(t['manual_csx_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range0'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range0'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range0_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range0_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range1'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range1_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range1_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range2'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range2'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_range2_calc'].test.name)))
        mrcsxff_fitems.append(t['dfxtrim_mrcsx_range2_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        mrcsxff_flow_name = 'MRCSX_FF_STARTANA1CPU'
        if composite_postfix:
            mrcsxff_flow_name = 'MRCSX_FF_STARTANA1CPU'+ '_' + composite_postfix

        ### ANAPRBUGB_FF_STARTANA1CPU Compopsite ####
        anaprbugbff_fitems = list()
        offset = 0
        anaprbugbff_fitems.append(t['anaprb_ugb_cm408'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm408_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm408_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['anaprb_ugb_cm1408'].test.name)))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm1408'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm1408_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        anaprbugbff_fitems.append(t['anaprb_ugb_cm1408_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        anaprbff_flow_name = 'ANAPRBUGB_FF_STARTANA1CPU'
        if composite_postfix:
            anaprbff_flow_name = 'ANAPRBUGB_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### DIGCOMP_FF_STARTANA1CPU Composite ###
        digcompff_fitems = list()
        offset = 0
        digcompff_fitems.append(t['hvls'].get_fitem(r0=pFail(setbin=AUTO, goto=t['clk_gating'].test.name)))
        digcompff_fitems.append(t['clk_gating'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_intcomp'].test.name)))
        digcompff_fitems.append(t['dfxtrim_intcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_intcomp_calc'].test.name)))
        digcompff_fitems.append(t['dfxtrim_intcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_digcomp'].test.name)))
        digcompff_fitems.append(t['manual_digcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['manual_digcomp_calc'].test.name)))
        digcompff_fitems.append(t['manual_digcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        digcompff_flow_name = 'DIGCOMP_FF_STARTANA1CPU'
        if composite_postfix:
            digcompff_flow_name = 'DIGCOMP_FF_STARTANA1CPU'+ '_' + composite_postfix


        ### DFX_TRIM_STARTANA1CPU Composite #######
        dfxtrim_fitems = list()
        offset = 0
        dfxtrim_fitems.append(t['dfxtrim_ugb'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_ugb_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_ugb_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=ugbff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_ugb_fuse'].get_fitem(r0=pFail(setbin=2768)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_mrcsx_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=mrcsxff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_mrcsx_fuse'].get_fitem(r0=pFail(setbin=2768)))
        dfxtrim_fitems.append(t['anaprb_ugb_cm928'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['anaprb_ugb_cm928_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        dfxtrim_fitems.append(t['anaprb_ugb_cm928_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=anaprbff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dfxtrim_digcomp_calc'].test.name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=digcompff_flow_name)))
        dfxtrim_fitems.append(t['dfxtrim_digcomp_fuse'].get_fitem(r0=pFail(setbin=2768), r1=pPass(ret=1)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(ugbff_flow_name, *ugbff_fitems), r0=pFail(goto=t['dfxtrim_mrcsx'].test.name), r1=pPass(goto=t['dfxtrim_mrcsx'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(mrcsxff_flow_name, *mrcsxff_fitems), r0=pFail(goto=t['anaprb_ugb_cm928'].test.name), r1=pPass(goto=t['anaprb_ugb_cm928'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(anaprbff_flow_name, *anaprbugbff_fitems), r0=pFail(goto=t['dfxtrim_digcomp'].test.name), r1=pPass(goto=t['dfxtrim_digcomp'].test.name)))
        dfxtrim_fitems.append(Fitem('SAME', Flow(digcompff_flow_name, *digcompff_fitems), r0=pFail(ret=1)))

        dfxtrim_flow_name = 'DFX_TRIM_STARTANA1CPU'
        if composite_postfix:
            dfxtrim_flow_name = 'DFX_TRIM_STARTANA1CPU'+ '_' + composite_postfix

        ###DAC_CAL_STARTANA1CPU Composite###
        DAC_CAL = list()
        offset = 0
        DAC_CAL.append(t['dac_cal'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atomcores'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_atom1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_atom1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_cal_core1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_core1'].get_fitem(**{**{f"r{i}": pFail(setbin=2741, goto=t['dac_cal_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CAL.append(t['dac_cal_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['dac_cal_fuse'].test.name)))
        DAC_CAL.append(t['dac_cal_fuse'].get_fitem(r0=pFail(setbin=2768)))

        DAC_CAL_flow_name = 'DAC_CAL_STARTANA1CPU'
        if composite_postfix:
            DAC_CAL_flow_name = 'DAC_CAL_STARTANA1CPU'+ '_' + composite_postfix

        ###DAC_CHK_STARTANA1CPU Composite###
        DAC_CHK = list()
        offset = 0
        DAC_CHK.append(t['dac_chk'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atomcores'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_atom0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom0'].get_fitem(**{**{f"r{i}": pFail(setbin=2742, goto=t['dac_chk_atom1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_atom1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core0'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core0'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_core1'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_core1'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        DAC_CHK.append(t['dac_chk_calc'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        DAC_CHK_flow_name = 'DAC_CHK_STARTANA1CPU'
        if composite_postfix:
            DAC_CHK_flow_name = 'DAC_CHK_STARTANA1CPU'+ '_' + composite_postfix

        ### DAC_STARTANA1CPU Composite ###
        DAC = list()
        DAC.append(t['dacflowfork'].get_fitem(r0=pFail(setbin=AUTO, goto=DAC_CAL_flow_name), r1=pPass(setbin=AUTO, goto=DAC_CAL_flow_name), r2=pPass(setbin=AUTO, goto=DAC_CHK_flow_name)))
        DAC.append(Fitem('SAME', Flow(DAC_CAL_flow_name, *DAC_CAL), r0=pFail(ret=0)))
        DAC.append(Fitem('SAME', Flow(DAC_CHK_flow_name, *DAC_CHK), r0=pFail(ret=1)))

        DAC_flow_name = 'DAC_STARTANA1CPU'
        if composite_postfix:
            DAC_flow_name = 'DAC_STARTANA1CPU'+ '_' + composite_postfix

        ###ICC_PER_BRANCH_STARTANA1CPU Composite###
        ICC_PER_BRANCH = list()
        offset = 0
        ICC_PER_BRANCH.append(t['preibr_idle'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['pre_ibr'].test.name) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['pre_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['pre_ibr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pre_ibr_fuse'].test.name)))
        ICC_PER_BRANCH.append(t['pre_ibr_fuse'].get_fitem(r0=pFail(setbin=2768)))
        ICC_PER_BRANCH.append(t['post_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO) for i in range(6)}, "r1": pPass()}))
        ICC_PER_BRANCH.append(t['post_ibr_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['post_ibr_csm'].test.name)))
        ICC_PER_BRANCH.append(t['post_ibr_csm'].get_fitem(r0=pFail(setbin=AUTO, ret=1)))

        ICC_PER_BRANCH_flow_name = 'ICC_PER_BRANCH_STARTANA1CPU'
        if composite_postfix:
            ICC_PER_BRANCH_flow_name = 'ICC_PER_BRANCH_STARTANA1CPU'+ '_' + composite_postfix

        ###GANG_CHK_STARTANA1CPU Composite###
        GANG_CHK = list()
        offset = 0
        GANG_CHK.append(t['gang'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        GANG_CHK.append(t['gang_calc'].get_fitem(r0=pFail(setbin=2765, ret=1)))

        GANG_CHK_flow_name = 'GANG_CHK_STARTANA1CPU'
        if composite_postfix:
            GANG_CHK_flow_name = 'GANG_CHK_STARTANA1CPU'+ '_' + composite_postfix

        ### MAIN PART TO CREATE FLOW ON DLVR###
        hvm_fitems = list()
        hvm_fitems.append(Fitem('SAME', Flow(debug_flow_name, *debug_flow_fitems), r0=pFail(goto=t['gsds_inject'].test.name)))
        hvm_fitems.append(t['gsds_inject'].get_fitem(r0=pFail(setbin=AUTO, goto=t['setgsds'].test.name)))
        hvm_fitems.append(t['setgsds'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['binconv_prim'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['binconv_prim'].get_fitem(r0=pFail(setbin=AUTO, goto=t['binconv_all'].test.name)))
        hvm_fitems.append(t['binconv_all'].get_fitem(r0=pFail(setbin=AUTO, goto=t['default'].test.name)))
        hvm_fitems.append(t['default'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['open_loop'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['voutmeas'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['voutmeas_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        hvm_fitems.append(t['voutmeas_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=lvr_flow_name)))
        hvm_fitems.append(Fitem('SAME', Flow(lvr_flow_name, *lvr_fitems), r0=pFail(goto=t['pod_vil'].test.name)))
        hvm_fitems.append(t['pod_vil'].get_fitem(r0=pFail(setbin=AUTO, goto=t['pod_vih'].test.name), r2=pFail(setbin=AUTO, goto=t['pod_vih'].test.name)))
        hvm_fitems.append(t['pod_vih'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['pod'].test.name) for i in range(8)}, "r1": pPass()}))
        hvm_fitems.append(t['pod'].get_fitem(r0=pFail(setbin=AUTO, goto=iref_flow_name)))
        hvm_fitems.append(Fitem('SAME', Flow(iref_flow_name, *ireftrim_fitems), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(dfxtrim_flow_name, *dfxtrim_fitems), r0=pFail(ret=0)))
        hvm_fitems.append(t['close_loop'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(Fitem('SAME', Flow(DAC_flow_name, *DAC), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(ICC_PER_BRANCH_flow_name, *ICC_PER_BRANCH), r0=pFail(ret=0)))
        hvm_fitems.append(Fitem('SAME', Flow(GANG_CHK_flow_name, *GANG_CHK), r0=pFail(ret=0)))
        hvm_fitems.append(t['vcciavmin'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['vcciavmin_calc'].test.name) for i in range(6)}, "r1": pPass()}))
        hvm_fitems.append(t['vcciavmin_calc'].get_fitem(r0=pFail(setbin=AUTO, goto=t['rampupdef'].test.name)))
        hvm_fitems.append(t['rampupdef'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['sds2class_gsds'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['s2cdelta'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['s2cdelta'].get_fitem(r0=pFail(setbin=AUTO, goto=t['setdff'].test.name)))
        hvm_fitems.append(t['setdff'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['fuseconfig_all_x1'].test.name) for i in range(5)}, "r1": pPass()}))
        hvm_fitems.append(t['fuseconfig_all_x1'].get_fitem(r0=pFail(setbin=2768)))
        hvm_fitems.append(t['dlvrkillall_failind'].get_fitem(r0=pFail(setbin=AUTO, goto=t['allkill_failind'].test.name)))
        hvm_fitems.append(t['allkill_failind'].get_fitem(**{**{f"r{i}": pFail(setbin=b) for i, b in {0:27620089,2:27520192,3:27530624,4:27710419,5:27560477,6:27620090,7:27572105,8:27650932,9:27636316,10:27610113,11:27666631,12:27676746}.items()}, "r1": pPass()}))
        hvm_fitems.append(t['allkill_failind_csm'].get_fitem(**{**{f"r{i}": pFail(setbin=b) for i, b in {0:27620091,2:27520193,3:27530625,4:27710420,5:27560478,6:27620092,7:27572106,8:27650933,9:27636317,10:27610114,11:27666632,12:27676747}.items()}, "r1": pPass()}))
        hvm_fitems.append(t['fuseconfig_check'].get_fitem(r0=pFail(setbin=27676740), r2=pFail(setbin=27676741),r3=pFail(setbin=27676742),r4=pFail(setbin=27676743),r5=pFail(setbin=27676744)))

        Flow(flow_name, *hvm_fitems,  dtag='STARTANA1CPU_SubFlow')

    def get_48_lttccpu_flow(self, flow_name, module_name='LTTCCPU', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        dlvrtrim = DlvrTrimCalc_TestBuilder
        analogdctc = AnalogDcTC_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test

        t['dac_chk_atomcores'] = analogdctc(is_edc=True, name='dac_chk_atomcores', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ATOM.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_atom_list', Pins='IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_evencore'] = analogdctc(is_edc=True, name='dac_chk_evencore', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_EVENCORE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_evencore_list', Pins='IPC::CPU_CORE0_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_oddcore'] = analogdctc(is_edc=True, name='dac_chk_oddcore', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_ODDCORE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_oddcore_list', Pins='IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk_ringprim'] = analogdctc(is_edc=True, name='dac_chk_ringprim', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_DAC_RINGPRIM.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P325V_MIN', Patlist='pth_dlvr_dac_cal_ringprim_list', Pins='IPC::CPU_CCF_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('2565'), CtvPins='CPU_TDO', **dparams)
        t['dac_chk'] = dlvrtrim(is_edc=False, name='dac_chk', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_DCERROR.json', ConfigSet='DAC_CHK_CSM', Mode='DAC_CAL', **dparams)
        t['pre_ibr_idle'] = analogdctc(is_edc=True, name='pre_ibr_idle', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_PRE_IBR_IDLE.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_preIBR_IDLE_list', Pins='VCCIA', TimingsTc=IPCtiming, MeasurementTypes='C', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['post_ibr'] = analogdctc(is_edc=False, name='post_ibr', DataBaseFile='./InputFiles/ANAMEAS_NVL_48_CLASS_POST_IBR.json', LevelsTc='IPC::PTH_DLVR_CX48::DLVR_VCCIA_1P025V_MIN', Patlist='pth_dlvr_postIBR_HX_list', Pins='VCCIA,IPC::CPU_CCF_DLVROUT,IPC::CPU_ATOM0_DLVROUT,IPC::CPU_ATOM1_DLVROUT,IPC::CPU_CORE0_DLVROUT,IPC::CPU_CORE1_DLVROUT', TimingsTc=IPCtiming, MeasurementTypes='C,V,V,V,V,V', TriggerMapName='IPC::PTH_DLVR_CX48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', ExpectedBits=Spec('3460'), CtvPins='CPU_TDO', **dparams)
        t['post_ibr_calc'] = dlvrtrim(is_edc=False, name='post_ibr_calc', ConfigFile='./InputFiles/DLVRTRIMCALC_NVL_48_POST_TRIM.json', ConfigSet='POST_IBR_CSM', Mode='IREF_TRIM', **dparams)


        #####DAC_CHK_LTTCCPU Composite####
        dacchk_fitems = list()
        dacchk_fitems.append(t['dac_chk_atomcores'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_evencore'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_evencore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_oddcore'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_oddcore'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk_ringprim'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk_ringprim'].get_fitem(**{**{f"r{i}": pFail(setbin=AUTO, goto=t['dac_chk'].test.name) for i in range(6)}, "r1": pPass()}))
        dacchk_fitems.append(t['dac_chk'].get_fitem(r0=pFail(setbin=2757)))

        DACCHK_flow_name = 'DACCHK_LTTCCPU'
        if composite_postfix:
            DACCHK_flow_name = 'DACCHK_LTTCCPU'+ '_' + composite_postfix

        #####ICC_PER_BRANCH_LTTCCPU Composite####
        icc_fitems = list()
        icc_fitems.append(t['pre_ibr_idle'].get_fitem(**{**{f"r{i}": pFail(setbin=2765, goto=t['post_ibr'].test.name) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['post_ibr'].get_fitem(**{**{f"r{i}": pFail(setbin=2765) for i in range(6)}, "r1": pPass()}))
        icc_fitems.append(t['post_ibr_calc'].get_fitem(r0=pFail(setbin=2765)))

        icc_flow_name = 'ICC_PER_BRANCH_LTTCCPU'
        if composite_postfix:
            icc_flow_name = 'ICC_PER_BRANCH_LTTCCPU'+ '_' + composite_postfix

        ###LTTC Main Flow#####
        lttc_fitems = list()
        lttc_fitems.append(Fitem('SAME', Flow(DACCHK_flow_name, *dacchk_fitems), r0=pFail(ret=0)))
        lttc_fitems.append(Fitem('SAME', Flow(icc_flow_name, *icc_fitems), r0=pFail(ret=0)))
        Flow(flow_name, *lttc_fitems, dtag='LTTCCPU_SubFlow')

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ PKG MODULE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#==============================================================================S28C/HX28C/DNL S28C=====================================================================================================
    def get_pkg816_startcpupatmodspkg_flow(self, flow_name, module_name='STARTCPUPATMODSPKG', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        fuseconfig = PrimePatConfigTestMethodFuseConfig_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test

        t['fuseconfig_all_x1'] = fuseconfig(is_edc=False, name='fuseconfig_all_x1', ConfigurationFile = './InputFiles/PATCONFIG_NVL_S28C_FUSE.setpoints.json', SetPoint = 'DLVR_FUSE_ALL_1', RegEx = '[gdx].......C........_.._......._............._...C............._.1.*', **dparams)

        #####STARTCPUPATMODSPKG Flow####
        cpupatmod_fitems = list()
        cpupatmod_fitems.append(t['fuseconfig_all_x1'].get_fitem(r0=pFail(setbin=2793)))
        Flow(flow_name, *cpupatmod_fitems, dtag='STARTCPUPATMODSPKG_SubFlow')


    def get_pkg816_endcpupkg_flow(self, flow_name, module_name='ENDCPUPKG', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        analogdctc = AnalogDcTC_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test
        t['powerloss'] = analogdctc(is_edc=False, name='powerloss', BypassPort=Spec('__shared__::TpRule.If_POSTFUSED(1,-1)'), DataBaseFile=Spec('__shared__::TpRule.If_M_PKGs("./InputFiles/ANAMEAS_NVL_HX28C_CLASS_PWRLOSS.json","./InputFiles/ANAMEAS_NVL_816_CLASS_PWRLOSS.json")'), LevelsTc='PTH_DLVR_CKPKGS7::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_power_loss_pkg_list', Pins=Spec('__shared__::TpRule.If_M_PKGs("VCCIA,VNNAON,V1P8_FLTRB","VCCIA,VNNAON,V1P8_CPU")'), TimingsTc=PKGtiming, MeasurementTypes='C,C,C', TriggerMapName=Spec('__shared__::TpRule.If_M_PKGs("PTH_DLVR_CKPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap_HX","PTH_DLVR_CKPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap")'), DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['vccio'] = analogdctc(is_edc=True, name='vccio', BypassPort=Spec('__shared__::TpRule.If_POSTFUSED(1,-1)'), DataBaseFile='./InputFiles/ANAMEAS_NVL_CLASS_VCCIO.json', LevelsTc='PTH_DLVR_CKPKGS7::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_vccio_meas_pkg_list', Pins='VCCIA,VCCIO,VCCIO_OUT_SVID', TimingsTc=PKGtiming, MeasurementTypes='V,V,V', TriggerMapName='PTH_DLVR_CKPKGS7::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)

        endcpu_fitems = list()
        endcpu_fitems.append(t['powerloss'].get_fitem(**{**{f"r{i}": pFail(setbin=2772) for i in range(6)}, "r1": pPass()}))
        endcpu_fitems.append(t['vccio'].get_fitem(r0=pFail(setbin=AUTO, ret=1), r2=pFail(setbin=AUTO, ret=1),r3=pFail(setbin=AUTO, ret=1),r4=pFail(setbin=AUTO, ret=1),r5=pFail(setbin=AUTO, ret=1)))
        Flow(flow_name, *endcpu_fitems, dtag='ENDCPUPKG_SubFlow')

#==============================================================================S52C PKG=====================================================================================================

    def get_pkgs52c_startcpupatmodspkg_flow(self, flow_name, module_name='STARTCPUPATMODSPKG', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        fuseconfig = PrimePatConfigTestMethodFuseConfig_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test

        t['fuseconfig_all_x1'] = fuseconfig(is_edc=False, name='fuseconfig_all_x1', ConfigurationFile = './InputFiles/PATCONFIG_NVL_S52C_FUSE.setpoints.json', SetPoint = 'DLVR_FUSE_ALL_1', RegEx = '[gdx].......C........_.._......._....AH......._...C................*', **dparams)

        #####STARTCPUPATMODSPKG Flow####
        cpupatmod_fitems = list()
        cpupatmod_fitems.append(t['fuseconfig_all_x1'].get_fitem(r0=pFail(setbin=2793)))
        Flow(flow_name, *cpupatmod_fitems, dtag='STARTCPUPATMODSPKG_SubFlow')


    def get_pkgs52c_endcpupkg_flow(self, flow_name, module_name='ENDCPUPKG', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        analogdctc = AnalogDcTC_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test
        t['powerloss'] = analogdctc(is_edc=False, name='powerloss', BypassPort=Spec('__shared__::TpRule.If_POSTFUSED(1,-1)'), DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_PWRLOSS.json', LevelsTc='PTH_DLVR_CKPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_power_loss_pkg_list', Pins=Spec('__shared__::TpRule.If_M_PKGs("VCCIA,VNNAON,V1P8_FLTRB","VCCIA,VNNAON,V1P8_CPU")'), TimingsTc=PKGtiming, MeasurementTypes='C,C,C', TriggerMapName='PTH_DLVR_CKPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['powerloss_cpu1'] = analogdctc(is_edc=True, name='powerloss_cpu1', BypassPort=Spec('__shared__::TpRule.If_POSTFUSED(1,-1)'), DataBaseFile='./InputFiles/ANAMEAS_NVL_S52C_CLASS_PWRLOSS.json', LevelsTc='PTH_DLVR_CKPKGS9::DLVR_VCCIA_1P0V_CPU1_MIN', Patlist='pth_dlvr_power_loss_pkg_list', Pins='VCCIA,VNNAON,V1P8_CPU', TimingsTc=PKGtiming, MeasurementTypes='C,C,C', TriggerMapName='PTH_DLVR_CKPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['vccio'] = analogdctc(is_edc=True, name='vccio', BypassPort= 1, DataBaseFile='./InputFiles/ANAMEAS_NVL_CLASS_VCCIO.json', LevelsTc='PTH_DLVR_CKPKGS9::DLVR_VCCIA_1P0V_CPU0_MIN', Patlist='pth_dlvr_vccio_meas_pkg_list', Pins='VCCIA,VCCIO,VCCIO_OUT_SVID', TimingsTc=PKGtiming, MeasurementTypes='V,V,V', TriggerMapName='PTH_DLVR_CKPKGS9::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)

        endcpu_fitems = list()
        endcpu_fitems.append(t['powerloss'].get_fitem(**{**{f"r{i}": pFail(setbin=2772) for i in range(6)}, "r1": pPass()}))
        endcpu_fitems.append(t['powerloss_cpu1'].get_fitem(r0=pFail(setbin=AUTO, goto=t['vccio'].test.name), r2=pFail(setbin=AUTO, goto=t['vccio'].test.name),r3=pFail(setbin=AUTO, goto=t['vccio'].test.name),r4=pFail(setbin=AUTO, goto=t['vccio'].test.name),r5=pFail(setbin=AUTO, goto=t['vccio'].test.name)))
        endcpu_fitems.append(t['vccio'].get_fitem(r0=pFail(setbin=AUTO, ret=1), r2=pFail(setbin=AUTO, ret=1),r3=pFail(setbin=AUTO, ret=1),r4=pFail(setbin=AUTO, ret=1),r5=pFail(setbin=AUTO, ret=1)))
        Flow(flow_name, *endcpu_fitems, dtag='ENDCPUPKG_SubFlow')

#==============================================================================C48 PKG=====================================================================================================

    def get_pkg48_startcpupatmodspkg_flow(self, flow_name, module_name='STARTCPUPATMODSPKG', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        fuseconfig = PrimePatConfigTestMethodFuseConfig_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test

        t['fuseconfig_all_x1'] = fuseconfig(is_edc=False, name='fuseconfig_all_x1', ConfigurationFile = './InputFiles/PATCONFIG_NVL_48_FUSE.setpoints.json', SetPoint = 'DLVR_FUSE_ALL_1', RegEx = '[gdx].......C........_.._......._............._...C............._.1.*', **dparams)

        #####STARTCPUPATMODSPKG Flow####
        cpupatmod_fitems = list()
        cpupatmod_fitems.append(t['fuseconfig_all_x1'].get_fitem(r0=pFail(setbin=2793)))
        Flow(flow_name, *cpupatmod_fitems, dtag='STARTCPUPATMODSPKG_SubFlow')


    def get_pkg48_endcpupkg_flow(self, flow_name, module_name='ENDCPUPKG', is_edc=False,  composite_postfix=None, test_instance_postfix=None):
        t = dict()


        analogdctc = AnalogDcTC_TestBuilder
        dparams = {
            'module_name': module_name,
            }
        ##dparam used for killed test
        t['powerloss'] = analogdctc(is_edc=False, name='powerloss', BypassPort=Spec('__shared__::TpRule.If_POSTFUSED(1,-1)'), DataBaseFile=Spec('__shared__::TpRule.If_M_PKGs("./InputFiles/ANAMEAS_NVL_48_CLASS_PWRLOSS_M.json","./InputFiles/ANAMEAS_NVL_48_CLASS_PWRLOSS_D.json")'), LevelsTc='PTH_DLVR_CK48::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_power_loss_pkg_list', Pins=Spec('__shared__::TpRule.If_M_PKGs("VCCIA,VNNAON,V1P8_FLTRB","VCCIA,VNNAON,V1P8_CPU")'), TimingsTc=PKGtiming, MeasurementTypes='C,C,C', TriggerMapName=Spec('__shared__::TpRule.If_M_PKGs("PTH_DLVR_CK48::DLVR_VINOUT_VIEWPIN_TriggerMap_HX","PTH_DLVR_CK48::DLVR_VINOUT_VIEWPIN_TriggerMap")'), DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)
        t['vccio'] = analogdctc(is_edc=True, name='vccio',  BypassPort=Spec('__shared__::TpRule.If_POSTFUSED(1,-1)'), DataBaseFile='./InputFiles/ANAMEAS_NVL_CLASS_VCCIO.json', LevelsTc='PTH_DLVR_CK48::DLVR_VCCIA_1P0V_MIN', Patlist='pth_dlvr_vccio_meas_pkg_list', Pins='VCCIA,VCCIO,VCCIO_OUT_SVID', TimingsTc=PKGtiming, MeasurementTypes='V,V,V', TriggerMapName='PTH_DLVR_CK48::DLVR_VINOUT_VIEWPIN_TriggerMap', DatalogLevel='PIN_DETAIL', FlushLevels='ENABLED', **dparams)

        endcpu_fitems = list()
        endcpu_fitems.append(t['powerloss'].get_fitem(**{**{f"r{i}": pFail(setbin=2772) for i in range(6)}, "r1": pPass()}))
        endcpu_fitems.append(t['vccio'].get_fitem(r0=pFail(setbin=AUTO, ret=1), r2=pFail(setbin=AUTO, ret=1),r3=pFail(setbin=AUTO, ret=1),r4=pFail(setbin=AUTO, ret=1),r5=pFail(setbin=AUTO, ret=1)))
        Flow(flow_name, *endcpu_fitems, dtag='ENDCPUPKG_SubFlow')


class CDIE_i7_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.PrePlist = None

    def initialize(self, name1, name2):
        #InitializeNVLClass(name1, name2, defaultrm1bin=-27, defaultrm2bin=-27, edcportctrbinrange=[(2700, 2790)], binrange=[(2700, 2790)]) ###Check please not correct
        InitializeNVLClass(name1, name2, defaultrm1bin=(98270000, 98270700), defaultrm2bin=(99270000, 99270700), edcportctrbinrange=[(2700, 2750)], binrange=[(2700, 2750)]) ###Check please not correct
        Import('PTH_DLVR_CXPKGS7.usrv')
        Import('PTH_DLVR_CXPKGS7_LevelsSequences.lvl')
        Import('PTH_DLVR_CXPKGS7_Levels.tcg')
        Import('PTH_DLVR_CXPKGS7_PatternTrigger.ptm')

class CDIE_i9_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.PrePlist = None

    def initialize(self, name1, name2):
        #InitializeNVLClass(name1, name2, defaultrm1bin=-27, defaultrm2bin=-27, edcportctrbinrange=[(2700, 2790)], binrange=[(2700, 2790)]) ###Check please not correct
        InitializeNVLClass(name1, name2, defaultrm1bin=(98270000, 98270700), defaultrm2bin=(99270000, 99270700), edcportctrbinrange=[(2700, 2750)], binrange=[(2700, 2750)]) ###Check please not correct
        Import('PTH_DLVR_CXPKGS9.usrv')
        Import('PTH_DLVR_CXPKGS9_LevelsSequences.lvl')
        Import('PTH_DLVR_CXPKGS9_Levels.tcg')
        Import('PTH_DLVR_CXPKGS9_PatternTrigger.ptm')

class CDIE_48_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.PrePlist = None

    def initialize(self, name1, name2):
        #InitializeNVLClass(name1, name2, defaultrm1bin=-27, defaultrm2bin=-27, edcportctrbinrange=[(2700, 2790)], binrange=[(2700, 2790)]) ###Check please not correct
        InitializeNVLClass(name1, name2, defaultrm1bin=(98270000, 98270700), defaultrm2bin=(99270000, 99270700), edcportctrbinrange=[(2700, 2750)], binrange=[(2700, 2750)]) ###Check please not correct
        Import('PTH_DLVR_CX48.usrv')
        Import('PTH_DLVR_CX48_LevelsSequences.lvl')
        Import('PTH_DLVR_CX48_Levels.tcg')
        Import('PTH_DLVR_CX48_PatternTrigger.ptm')

#+++++++++++++++++++++++++++++PKG +++++++++++++++++++++++++++++++++++++

class CDIEPKG_i7_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.PrePlist = None

    def initialize(self, name1, name2):
        #InitializeNVLClass(name1, name2, defaultrm1bin=-27, defaultrm2bin=-27, edcportctrbinrange=[(2791, 2799)], binrange=[(2791, 2799)]) ###Check please not correct
        InitializeNVLClass(name1, name2, defaultrm1bin=(98270700, 98270999), defaultrm2bin=(99270700, 99270999), edcportctrbinrange=[(2791, 2799)], binrange=[(2791, 2799)]) ###Check please not correct
        Import('PTH_DLVR_CKPKGS7.usrv')
        Import('PTH_DLVR_CKPKGS7_LevelsSequences.lvl')
        Import('PTH_DLVR_CKPKGS7_Levels.tcg')
        Import('PTH_DLVR_CKPKGS7_PatternTrigger.ptm')

class CDIEPKG_i9_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.PrePlist = None


    def initialize(self, name1, name2):
        #InitializeNVLClass(name1, name2, defaultrm1bin=-27, defaultrm2bin=-27, edcportctrbinrange=[(2791, 2799)], binrange=[(2791, 2799)]) ###Check please not correct
        InitializeNVLClass(name1, name2, defaultrm1bin=(98270700, 98270999), defaultrm2bin=(99270700, 99270999), edcportctrbinrange=[(2791, 2799)], binrange=[(2791, 2799)]) ###Check please not correct
        Import('PTH_DLVR_CKPKGS9.usrv')
        Import('PTH_DLVR_CKPKGS9_LevelsSequences.lvl')
        Import('PTH_DLVR_CKPKGS9_Levels.tcg')
        Import('PTH_DLVR_CKPKGS9_PatternTrigger.ptm')

class CDIEPKG_48_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.PrePlist = None

    def initialize(self, name1, name2):
        #InitializeNVLClass(name1, name2, defaultrm1bin=-27, defaultrm2bin=-27, edcportctrbinrange=[(2791, 2799)], binrange=[(2791, 2799)]) ###Check please not correct
        InitializeNVLClass(name1, name2, defaultrm1bin=(98270700, 98270999), defaultrm2bin=(99270700, 99270999), edcportctrbinrange=[(2791, 2799)], binrange=[(2791, 2799)]) ###Check please not correct
        Import('PTH_DLVR_CK48.usrv')
        Import('PTH_DLVR_CK48_LevelsSequences.lvl')
        Import('PTH_DLVR_CK48_Levels.tcg')
        Import('PTH_DLVR_CK48_PatternTrigger.ptm')



cdie = CDIE_i7_CLASS()
cdie.initialize('PTH_DLVR_CXPKGS7','PTH_DLVR_CXPKGS7')
cdie.get_816_startana1cpu_flow('PTH_DLVR_CXPKGS7_STARTANA1CPU', is_edc=False)
cdie.get_816_lttccpu_flow('PTH_DLVR_CXPKGS7_LTTCCPU', is_edc=False)

cdie = CDIE_i9_CLASS()
cdie.initialize('PTH_DLVR_CXPKGS9','PTH_DLVR_CXPKGS9')
cdie.get_s52c_startana1cpu_flow('PTH_DLVR_CXPKGS9_STARTANA1CPU', is_edc=False)
cdie.get_s52c_lttccpu_flow('PTH_DLVR_CXPKGS9_LTTCCPU', is_edc=False)

cdie = CDIE_48_CLASS()
cdie.initialize('PTH_DLVR_CX48','PTH_DLVR_CX48')
cdie.get_48_startana1cpu_flow('PTH_DLVR_CX48_STARTANA1CPU', is_edc=False)
cdie.get_48_lttccpu_flow('PTH_DLVR_CX48_LTTCCPU', is_edc=False)

cdie = CDIEPKG_i7_CLASS()
cdie.initialize('PTH_DLVR_CKPKGS7','PTH_DLVR_CKPKGS7')
cdie.get_pkg816_startcpupatmodspkg_flow('PTH_DLVR_CKPKGS7_STARTCPUPATMODSPKG', is_edc=False)
cdie.get_pkg816_endcpupkg_flow('PTH_DLVR_CKPKGS7_ENDCPUPKG', is_edc=False)

cdie = CDIEPKG_i9_CLASS()
cdie.initialize('PTH_DLVR_CKPKGS9','PTH_DLVR_CKPKGS9')
cdie.get_pkgs52c_startcpupatmodspkg_flow('PTH_DLVR_CKPKGS9_STARTCPUPATMODSPKG', is_edc=False)
cdie.get_pkgs52c_endcpupkg_flow('PTH_DLVR_CKPKGS9_ENDCPUPKG', is_edc=False)

cdie = CDIEPKG_48_CLASS()
cdie.initialize('PTH_DLVR_CK48','PTH_DLVR_CK48')
cdie.get_pkg48_startcpupatmodspkg_flow('PTH_DLVR_CK48_STARTCPUPATMODSPKG', is_edc=False)
cdie.get_pkg48_endcpupkg_flow('PTH_DLVR_CK48_ENDCPUPKG', is_edc=False)