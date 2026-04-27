# Import the necessary classes from Pymtpl
import copy
import re, json

from pymtpl.por_methods import PrimePatConfigTestMethod, ScreenTC, AuxiliaryTC, PrimeCtvDecoderTestMethod, PrimeFuseReadMaskUltDecodeTestMethod, PrimeFunctionalTestMethod, FleISeedGetLotKeys, FleISeedGetUnitKeys
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
            'ScreenTestsFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/UNITINFO_C2X.screen.json","./InputFiles/UNITINFO_C1X.screen.json")'),
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
            'ConfigurationFile': Spec('__shared__::TpRule.If_MICP("./InputFiles/UNITINFO_C2X.patConfigSetpoints.json","./InputFiles/UNITINFO_C1X.patConfigSetpoints.json")'),
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
            'ConfigurationFile': Spec('FUS_UNITINFO_CXX_Rules.FUSEREAD_CfgFile("./InputFiles/UNITINFO_CXX.fuseReadMask.json","./InputFiles/UNITINFO_CXX.fuseReadMask_N2P.json","./InputFiles/UNITINFO_CXX.fuseReadMask_BLLC.json")'),
            'SkipPatternExecute': f'DISABLED',
            'DieIdNames': Spec('__shared__::TpRule.If_MICP("U1.U5,U1.U6","U1.U5")'),
            'RegisterName': Spec('__shared__::TpRule.If_MICP("CPU0,CPU1","CPU0")'), 
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
            'CtvCapturePins': Spec('__shared__::TpRule.If_MICP("IPC::CPU_TDO, IPC::CPU1_TDO", "IPC::CPU_TDO")'),
            'Dieid_Rename': f' ' 
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeCtvDecoderTestMethod(**param)

class FleISeedGetLotKeys_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_ISEED_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'KeysTypeId': Spec('__shared__::TpRule.If_MICP("1600,1599","1600")'),
            'ByPassPort': f'-1',
            'QueryMode': f'ENG' 
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleISeedGetLotKeys(**param)

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
        #t['longreset_strobe_x'] = PrimePatConfigTestMethod_TestBuilder(name='longreset_strobe_x', SetPoint='CPURedTapStrobeX', ConfigurationFile='./InputFiles/redtap_mask_cpu_fuse_setpoint.json', BypassPort=1, **dparams)
        t['unlock_setup'] = ScreenTC_TestBuilder(name='unlock_setup', ScreenTestSet='LEG_KEY_split_by_32bits_MsbToLsb', BypassPort=-1, **dparams)
        t['legacy_setup_exe_x1'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_setup_exe_x1', SetPoint='LGULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        #t['legacy_setup_exe_x2'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_setup_exe_x2', SetPoint='LGULCDIE_RATIO2_splitby32_MsbToLsb', BypassPort=1, **dparams)
        #t['legacy_setup_exe_x4'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_setup_exe_x4', SetPoint='LGULCDIE_RATIO4_splitby32_MsbToLsb', BypassPort=1, **dparams)
        t['check_bomgroup'] = ScreenTC_TestBuilder(name='check_bomgroup', ScreenTestSet='Check_BOMGROUP', ScreenTestsFile='./InputFiles/ISEED.screen.json', BypassPort=-1, **dparams)
        t['getsd'] = FleISeedGetLotKeys_TestBuilder(name='getsd', BypassPort=Spec('__shared__::DieIndic.DieCombo(1,1,1,1,1,1,1,1,1,1,1,-1,1,1,1,1)'), MaxQueryAttempts=1, ReQuerySleep=1, **dparams)
        t['getsd_pcdh'] = FleISeedGetLotKeys_TestBuilder(name='getsd_pcdh', BypassPort=Spec('__shared__::DieIndic.DieCombo(1,1,1,1,1,1,1,1,1,1,1,-1,1,1,1,1)'), MaxQueryAttempts=1, ReQuerySleep=1, **dparams)
       

        ##Flow Setup
        fuse_config_prep_fitems = []
        fuse_config_prep_fitems.append(t['check_bomgroup'].get_fitem(r0=pFail(ret=0),
                                                                     r2=pPass(goto="NEXT"),
                                                                     r3=pPass(goto="FUSE_X_ISEED_K_INIT_X_X_X_X_GETSD_PCDH")))
        fuse_config_prep_fitems.append(t['getsd'].get_fitem(r0=pFail(ret=0),
                                                            r1=pPass(goto="FUSE_X_SCREENTC_K_INIT_X_X_X_X_UNLOCK_SETUP"),
                                                            r2=pFail(ret=0)))
        fuse_config_prep_fitems.append(t['getsd_pcdh'].get_fitem(r0=pFail(ret=0),
                                                                 r2=pFail(ret=0)))
        #fuse_config_prep_fitems.append(t['longreset_strobe_x'].get_fitem(r0=pFail(ret=0)))
        fuse_config_prep_fitems.append(t['unlock_setup'].get_fitem(r0=pFail(ret=0)))
        fuse_config_prep_fitems.append(t['legacy_setup_exe_x1'].get_fitem(r0=pFail(ret=0)))
        #fuse_config_prep_fitems.append(t['legacy_setup_exe_x2'].get_fitem(r0=pFail(ret=0)))
        #fuse_config_prep_fitems.append(t['legacy_setup_exe_x4'].get_fitem(r0=pFail(ret=0)))
        fuse_config_prep_composite = Flow('FUSE_CONFIG_PREP', *fuse_config_prep_fitems)

        init_fitems = []
        init_fitems.append(Fitem('SAME', fuse_config_prep_composite, r0=pFail(ret=0), r1=pPass(ret=1)))

        Flow(flow_name,*init_fitems)


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


        # tests for STARTCPUNOM / PRE_UNLOCK
        t['unlock_setup'] =  ScreenTC_TestBuilder(name='unlock_setup', ScreenTestSet='LEG_KEY_split_by_32bits_MsbToLsb', **dparams)
        t['legacy_unlock_x1'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock_x1', SetPoint='LGULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        #t['legacy_unlock_x2'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock_x2', SetPoint='LGULCDIE_RATIO2_splitby32_MsbToLsb', BypassPort=1, **dparams)
        #t['legacy_unlock_x4'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock_x4', SetPoint='LGULCDIE_RATIO4_splitby32_MsbToLsb', BypassPort=1, **dparams)
        
         
        # tests for STARTCPUNOM / CHECK_DIE_STATUS
        t['tap_status'] = PrimeCtvDecoderTestMethod_TestBuilder(name='tap_status', BypassPort=-1, Patlist='IPC::cpu_dfxagg_read_hvm_status_csr', **dparams)
        t['unit_info_decode'] =  ScreenTC_TestBuilder(name='unit_info_decode', ScreenTestSet='STATUS_SET_PIC8_PrimeCtvDecoderTestMethod', BypassPort=-1, **dparams)
        
        # tests for STARTCPUNOM / RED_UNLOCK
        t['security_get'] = FleISeedGetUnitKeys_TestBuilder(name='security_get',  DieId = 'Pkg', KeysTypeId=Spec('__shared__::TpRule.If_MICP("1600,1599,4604","1600,4604")'), BypassPort=-1, **dparams)
        t['red_unlock_setup'] =  ScreenTC_TestBuilder(name='red_unlock_setup', ScreenTestSet='RED_KEY_split_by_32bits_MsbToLsb', **dparams)
        t['red_unlock_x1'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock_x1', SetPoint='RDULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=-1, **dparams)
        #t['red_unlock_x2'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock_x2', SetPoint='RDULCDIE_RATIO2_splitby32_MsbToLsb', BypassPort=1, **dparams)
        #t['red_unlock_x4'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock_x4', SetPoint='RDULCDIE_RATIO4_splitby32_MsbToLsb', BypassPort=1, **dparams)
        t['efuseread'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuseread', ConfigName='CPU_ULTReadFlow', BypassPort=-1,  PassingMaskName='ULT_UnitInfo', FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', PackageEfuse=Spec('__shared__::TpRule.If_MICP("ALLOW_NO_PKG","")'), **dparams)
        #t['efuseread_cpu1'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuseread_cpu1', ConfigName='CPU_ULTReadFlow', BypassPort=1,  DieIdNames=Spec('__shared__::DFFVars.DIEID_CPU1'), PassingMaskName='ULT_UnitInfo', RegisterName='CPU1', FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT',  **dparams)
        
        # tests for STARTCPUNOM / LEGACY_UNLOCK
        t['main_fuse_read'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='main_fuse_read', ConfigName='CPU_ULTReadFlow', BypassPort=-1, PassingMaskName='ULT_UnitInfo', FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', PackageEfuse=Spec('__shared__::TpRule.If_MICP("ALLOW_NO_PKG","")'), **dparams)
        #t['main_fuse_read_cpu1'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='main_fuse_read_cpu1', ConfigName='CPU_ULTReadFlow', BypassPort=1, DieIdNames=Spec('__shared__::DFFVars.DIEID_CPU1'), PassingMaskName='ULT_UnitInfo', RegisterName='CPU1', FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', **dparams)
       
        # tests for STARTCPUNOM / POST_UNLOCK
        t['tap_status_postunlock'] = PrimeCtvDecoderTestMethod_TestBuilder(name='tap_status_postunlock', BypassPort=-1, Patlist='IPC::cpu_dfxagg_read_hvm_status_csr', **dparams)
        t['unit_info_decode_postunlock'] =  ScreenTC_TestBuilder(name='unit_info_decode_postunlock', ScreenTestSet='UNLOCK_SET_PIC8_PrimeCtvDecoderTestMethod', BypassPort=-1, **dparams)
       
        # tests for STARTCPUNOM / FAIL_FLOW
        t['uinfo_func'] = PrimeFunctionalTestMethod_TestBuilder(name='uinfo_func', BypassPort=-1, Patlist='IPC::cpu_dfxagg_read_hvm_status_csr', **dparams)

        ##Flow Setup
        pre_unlock_fitems = []
        pre_unlock_fitems.append(t['unlock_setup'].get_fitem(r0=pFail(setbin=self.bin(314800, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(314801, offset), ret=0),
                                                                r3=pFail(setbin=self.bin(314802, offset), ret=0),
                                                                r4=pFail(setbin=self.bin(314803, offset), ret=0)))
        pre_unlock_fitems.append(t['legacy_unlock_x1'].get_fitem(r0=pFail(setbin=self.bin(314704, offset), ret=0)))
        #pre_unlock_fitems.append(t['legacy_unlock_x2'].get_fitem(r0=pFail(setbin=self.bin(314705, offset), ret=0)))
        #pre_unlock_fitems.append(t['legacy_unlock_x4'].get_fitem(r0=pFail(setbin=self.bin(314706, offset), ret=0)))
        pre_unlock_composite = Flow('PRE_UNLOCK', *pre_unlock_fitems)

        check_die_status_fitems = []
        check_die_status_fitems.append(t['tap_status'].get_fitem(r0=pFail(setbin=self.bin(314900, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(314901, offset), ret=2),
                                                                r3=pFail(setbin=self.bin(314902, offset), ret=2)))
        check_die_status_fitems.append(t['unit_info_decode'].get_fitem(r0=pFail(setbin=self.bin(314804, offset), ret=0),
                                                                       r3=pPass(ret=3),
                                                                       r2=pFail(setbin=self.bin(314805, offset), ret=2),
                                                                       r4=pFail(setbin=self.bin(314806, offset), ret=2),
                                                                       r6=pFail(setbin=self.bin(314807, offset), ret=0)
                                                                       ))
        check_die_status_composite = Flow('CHECK_DIE_STATUS', *check_die_status_fitems)

        red_unlock_fitems = []
        red_unlock_fitems.append(t['security_get'].get_fitem(r0=pFail(setbin=self.bin(920201, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(920202, offset), ret=0)))
        red_unlock_fitems.append(t['red_unlock_setup'].get_fitem(r0=pFail(setbin=self.bin(314808, offset), ret=0),
                                                                 r2=pFail(setbin=self.bin(314812, offset), ret=0)))
        red_unlock_fitems.append(t['red_unlock_x1'].get_fitem(r0=pFail(setbin=self.bin(314707, offset), ret=0)))
        #red_unlock_fitems.append(t['red_unlock_x2'].get_fitem(r0=pFail(setbin=self.bin(314708, offset), ret=0)))
        #red_unlock_fitems.append(t['red_unlock_x4'].get_fitem(r0=pFail(setbin=self.bin(314709, offset), ret=0)))
        red_unlock_fitems.append(t['efuseread'].get_fitem(r0=pFail(setbin=self.bin(314100, offset), ret=0),
                                                          r2=pFail(setbin=self.bin(314101, offset), ret=2),
                                                          r3=pFail(setbin=self.bin(314102, offset), ret=0)))
        #red_unlock_fitems.append(t['efuseread_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314106, offset), ret=0),
        #                                                 r2=pFail(setbin=self.bin(314107, offset), ret=2),
        #                                                  r3=pFail(setbin=self.bin(314108, offset), ret=0)))
        red_unlock_composite = Flow('RED_UNLOCK', *red_unlock_fitems)

        legacy_unlock_fitems = []
        legacy_unlock_fitems.append(t['main_fuse_read'].get_fitem(r0=pFail(setbin=self.bin(314103, offset), ret=0),
                                                          r2=pFail(setbin=self.bin(314104, offset), ret=2),
                                                          r3=pFail(setbin=self.bin(314105, offset), ret=0)))
        #legacy_unlock_fitems.append(t['main_fuse_read_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314109, offset), ret=0),
        #                                                  r2=pFail(setbin=self.bin(314110, offset), ret=2),
        #                                                  r3=pFail(setbin=self.bin(314111, offset), ret=0)))
        legacy_unlock_composite = Flow('LEGACY_UNLOCK', *legacy_unlock_fitems)

        post_unlock_fitems = []
        post_unlock_fitems.append(t['tap_status_postunlock'].get_fitem(r0=pFail(setbin=self.bin(314903, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(314904, offset), ret=0),
                                                                r3=pFail(setbin=self.bin(314905, offset), ret=0)))
        post_unlock_fitems.append(t['unit_info_decode_postunlock'].get_fitem(r0=pFail(setbin=self.bin(314809, offset), ret=0),
                                                                       r2=pFail(setbin=self.bin(314810, offset), ret=0),
                                                                       r6=pFail(setbin=self.bin(314811, offset), ret=0)
                                                                       ))
        post_unlock_composite = Flow('POST_UNLOCK', *post_unlock_fitems)

        fail_flow_fitems = []
        fail_flow_fitems.append(t['uinfo_func'].get_fitem(r0=pFail(ret=0),
                                                          r4=pFail(ret=0),
                                                          r5=pFail(ret=0)))
        fail_flow_composite = Flow('FAIL_FLOW', *fail_flow_fitems)

        startcpunom_fitems = []
        startcpunom_fitems.append(Fitem('SAME', pre_unlock_composite, r0=pFail(ret=0), r1=pPass(goto=check_die_status_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', check_die_status_composite, r0=pFail(ret=0), r1=pPass(goto=red_unlock_composite.name), r2=pFail(goto=fail_flow_composite.name), r3=pPass(goto=legacy_unlock_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', red_unlock_composite, r0=pFail(ret=0), r1=pPass(goto=post_unlock_composite.name), r2=pFail(goto=fail_flow_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', legacy_unlock_composite, r0=pFail(ret=0), r1=pPass(goto=post_unlock_composite.name), r2=pFail(goto=fail_flow_composite.name)))
        startcpunom_fitems.append(Fitem('SAME', post_unlock_composite, r0=pFail(goto=fail_flow_composite.name), r1=pPass(ret=1)))
        startcpunom_fitems.append(Fitem('SAME', fail_flow_composite, r0=pFail(ret=0), r1=pPass(ret=0)))

        Flow(flow_name,*startcpunom_fitems)

    def get_failflow_flow(self, flow_name, module_name='IPCPUFF', is_edc=False,  bin_offset=0, bin_offset2=0, composite_postfix=None, test_instance_postfix=None):
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


        # tests for FAILFLOW / PRE_UNLOCK
        t['unlock_setup'] =  ScreenTC_TestBuilder(name='unlock_setup', ScreenTestSet='LEG_KEY_split_by_32bits_MsbToLsb', BypassPort=1, **dparams)
        t['legacy_unlock_x1'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock_x1', SetPoint='LGULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=1, **dparams)
        t['legacy_unlock_x2'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock_x2', SetPoint='LGULCDIE_RATIO2_splitby32_MsbToLsb', BypassPort=1, **dparams)
        t['legacy_unlock_x4'] = PrimePatConfigTestMethod_TestBuilder(name='legacy_unlock_x4', SetPoint='LGULCDIE_RATIO4_splitby32_MsbToLsb', BypassPort=1, **dparams)
        
         
        # tests for FAILFLOW / CHECK_DIE_STATUS
        t['tapstatus'] = PrimeCtvDecoderTestMethod_TestBuilder(name='tap_status', BypassPort=1, Patlist='IPC::cpu_dfxagg_read_hvm_status_csr', **dparams)
        t['unit_info_decode'] =  ScreenTC_TestBuilder(name='unit_info_decode', ScreenTestSet='STATUS_SET_PIC8_PrimeCtvDecoderTestMethod', BypassPort=1, **dparams)
        
        # tests for FAILFLOW / RED_UNLOCK
        t['red_unlock_setup'] =  ScreenTC_TestBuilder(name='red_unlock_setup', ScreenTestSet='RED_KEY_split_by_32bits_MsbToLsb', BypassPort=1, **dparams)
        t['red_unlock_x1'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock_x1', SetPoint='RDULCDIE_RATIO1_splitby32_MsbToLsb', BypassPort=1, **dparams)
        t['red_unlock_x2'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock_x2', SetPoint='RDULCDIE_RATIO2_splitby32_MsbToLsb', BypassPort=1, **dparams)
        t['red_unlock_x4'] = PrimePatConfigTestMethod_TestBuilder(name='red_unlock_x4', SetPoint='RDULCDIE_RATIO4_splitby32_MsbToLsb', BypassPort=1, **dparams)
        t['efuseread'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuseread', ConfigName='CPU_ULTReadFlow', BypassPort=1, PassingMaskName='ULT_UnitInfo', FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', **dparams)
        #t['efuseread_cpu1'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='efuseread_cpu1', ConfigName='CPU_ULTReadFlow', BypassPort=1, DieIdNames=Spec('__shared__::DFFVars.DIEID_CPU'), PassingMaskName='ULT_UnitInfo', RegisterName="CPU1_MAIN", FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', **dparams)
        
        # tests for FAILFLOW / LEGACY_UNLOCK
        t['fuseread'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='fuseread', ConfigName='CPU_ULTReadFlow', BypassPort=1, PassingMaskName='ULT_UnitInfo', FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', **dparams)
        #t['fuseread_cpu1'] = PrimeFuseReadMaskUltDecodeTestMethod_TestBuilder(name='fuseread_cpu1', ConfigName='CPU_ULTReadFlow', BypassPort=1, DieIdNames=Spec('__shared__::DFFVars.DIEID_CPU'), PassingMaskName='ULT_UnitInfo', RegisterName="CPU1_MAIN", FailingMaskName='', Patlist='IPC::cpu_fuse_read_hvm_x', FuseGroupToDatalog='ULT', **dparams)
       
        ##Flow Setup
        pre_unlock_fitems = []
        pre_unlock_fitems.append(t['unlock_setup'].get_fitem(r0=pFail(setbin=self.bin(314812, offset), ret=0),
                                                                r2=pFail(setbin=self.bin(314813, offset), ret=0),
                                                                r3=pFail(setbin=self.bin(314814, offset), ret=0),
                                                                r4=pFail(setbin=self.bin(314815, offset), ret=0)))
        pre_unlock_fitems.append(t['legacy_unlock_x1'].get_fitem(r0=pFail(setbin=self.bin(314710, offset), ret=0)))
        pre_unlock_fitems.append(t['legacy_unlock_x2'].get_fitem(r0=pFail(setbin=self.bin(314711, offset), ret=0)))
        pre_unlock_fitems.append(t['legacy_unlock_x4'].get_fitem(r0=pFail(setbin=self.bin(314712, offset), ret=0)))
        pre_unlock_composite = Flow('PRE_UNLOCK_DCFF', *pre_unlock_fitems)

        check_die_status_fitems = []
        check_die_status_fitems.append(t['tapstatus'].get_fitem(r0=pFail(goto='NEXT'),
                                                                r2=pFail(ret=2),
                                                                r3=pFail(ret=2),
                                                                r4=pFail(ret=2)))
        check_die_status_fitems.append(t['unit_info_decode'].get_fitem(r0=pFail(ret=2),
                                                                       r3=pPass(ret=3),
                                                                       r2=pFail(ret=2),
                                                                       r4=pFail(ret=2),
                                                                       r6=pFail(ret=2)
                                                                       ))
        check_die_status_composite = Flow('CHECK_DIE_STATUS_DCFF', *check_die_status_fitems)

        red_unlock_fitems = []
        red_unlock_fitems.append(t['red_unlock_setup'].get_fitem(r0=pFail(setbin=self.bin(314816, offset), ret=0)))
        red_unlock_fitems.append(t['red_unlock_x1'].get_fitem(r0=pFail(goto='NEXT')))
        red_unlock_fitems.append(t['red_unlock_x2'].get_fitem(r0=pFail(goto='NEXT')))
        red_unlock_fitems.append(t['red_unlock_x4'].get_fitem(r0=pFail(goto='NEXT')))
        red_unlock_fitems.append(t['efuseread'].get_fitem(r0=pFail(ret=1),
                                                          r2=pFail(ret=1),
                                                          r4=pFail(ret=1)))
        #red_unlock_fitems.append(t['efuseread_cpu1'].get_fitem(r0=pFail(ret=1),
        #                                                  r2=pFail(ret=1),
        #                                                  r4=pFail(ret=1)))
        red_unlock_composite = Flow('RED_UNLOCK_DCFF', *red_unlock_fitems)

        legacy_unlock_fitems = []
        legacy_unlock_fitems.append(t['fuseread'].get_fitem(r0=pFail(ret=1),
                                                                       r2=pFail(ret=1),
                                                                       r3=pFail(ret=1)))
        #legacy_unlock_fitems.append(t['fuseread_cpu1'].get_fitem(r0=pFail(ret=1),
        #                                                              r2=pFail(ret=1),
        #                                                              r3=pFail(ret=1)))
        legacy_unlock_composite = Flow('LEGACY_UNLOCK_DCFF', *legacy_unlock_fitems)

       

        ipcpuff_fitems = []
        ipcpuff_fitems.append(Fitem('SAME', pre_unlock_composite, r0=pFail(ret=0), r1=pPass(goto=check_die_status_composite.name)))
        ipcpuff_fitems.append(Fitem('SAME', check_die_status_composite, r0=pFail(ret=0), r1=pPass(goto=red_unlock_composite.name), r2=pFail(ret=1), r3=pPass(goto=legacy_unlock_composite.name)))
        ipcpuff_fitems.append(Fitem('SAME', red_unlock_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        ipcpuff_fitems.append(Fitem('SAME', legacy_unlock_composite, r0=pFail(ret=0), r1=pPass(ret=1)))

        Flow(flow_name,*ipcpuff_fitems)

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
        InitializeNVLClass(name1, name2, defaultrm1bin=(98312000,98313999), defaultrm2bin=(99312000,99313999), binrange=[(3140, 3149)])
        #MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        Import("FUS_UNITINFO_CXX.usrv")
        
rev = 0
bomgroup = 'SD'

#cdie = CDIE_816_SORT()
#cdie.initialize('./FUS_FUSECFG_CXX', 'FUS_FUSECFG_CXX', rev)
#cdie.get_init_flow('FUS_FUSECFG_CXX_INIT')
#cdie.get_start_flow('FUS_FUSECFG_CXX_START')

cdie = CDIE_816_CLASS()
cdie.initialize('./FUS_UNITINFO_CXX', 'FUS_UNITINFO_CXX', rev)
cdie.get_init_flow('FUS_UNITINFO_CXX_INIT')
cdie.get_start_flow('FUS_UNITINFO_CXX_STARTCPUNOM')
#cdie.get_failflow_flow('FUS_UNITINFO_CXX_CPUIPFF')

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