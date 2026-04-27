# Import the necessary classes from Pymtpl
import copy
import re, json

from pymtpl.por_methods import PrimePatConfigTestMethod, ScreenTC, AuxiliaryTC, PrimeFuseReadMaskTestMethod, PrimeSetDffTestMethod, PrimeSharedStorageInserterTestMethod, PrimeGetDffTestMethod, PrimeCtvDecoderTestMethod, PrimeFunctionalTestMethod, FleGetDieStatus, FleCheckFuseStringStatus, FleCheckFuseStringStatusByDies
from pymtpl.por_methods import BaseMethod, required, optional
from pymtpl.core import Flow, Fitem, pPass, pFail, InitializeNVLSort, InitializeNVLClass, Spec, AUTO, MtplComment, Import, TrialParamSpec
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
            'ScreenTestsFile': f'./InputFiles/VLD.screentest.json'
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
            'ConfigurationFile': Spec('__shared__::TpRule.If_CLASS_NVL_S52C("./InputFiles/VLD_C2X.setpoints.json","./InputFiles/VLD_C1X.setpoints.json")'),
            
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimePatConfigTestMethod(**param)

class PrimeFuseReadMaskTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        if 'vld_uv' in name:
            file = './InputFiles/VLD_UV.fuseReadVoltageFile.json'
        else:
            file = './InputFiles/VLD_OV.fuseReadVoltageFile.json'
        param = {
            'name': f'FUSE_X_FUSEREAD_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ConfigurationFile': Spec('__shared__::TpRule.If_CLASS_NVL_S52C("./InputFiles/VLD_C2X.fuseread.json","./InputFiles/VLD_C1X.fuseread.json")'),
            'RegisterName': Spec('__shared__::TpRule.If_CLASS_NVL_S52C("CPU0_VLD,CPU1_VLD","CPU0_VLD")'), 
            'VoltageFile': file,
            'BypassPort': f'-1'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeFuseReadMaskTestMethod(**param)

class PrimeFunctionalTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FUNC_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1'
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
            'ConfigurationFile': Spec('__shared__::TpRule.If_CLASS_NVL_S52C(GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C2X_PIC8_PrimeCtvDecoderTestMethod.csv", GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/FUS/FUS_UNITINFO_CXX/InputFiles/UNITINFO_C1X_PIC8_PrimeCtvDecoderTestMethod.csv")'),
            'Dieid_Rename': f' ' 
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeCtvDecoderTestMethod(**param)

class PrimeSetDffTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_X_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'TokenName': f'FUVLD,FOVLD',
            'TokenValue': f'Storage.UVLD_VALUE, Storage:OVLD_VALUE', 
            'DieId': Spec('__shared__::TpRule.If_CLASS_NVL_S52C("__shared__::DFFVars.DIEID_CPU, __shared__::DFFVars.DIEID_CPU1","__shared__::DFFVars.DIEID_CPU")')
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeSetDffTestMethod(**param)
        
class PrimeSharedStorageInserterTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_X_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'Path': f'./InputFiles/VLD_SharedStorage_03.json'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeSharedStorageInserterTestMethod(**param)
        
class PrimeGetDffTestMethod_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_X_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ByPassPort': f'-1',
            'TokenName': f'FUVLD',
            'Storage': 'CPU_UNDERVOLTVALUE_NORESENSE',
            'DieId' : Spec('__shared__::TpRule.If_CLASS_NVL_S52C("__shared__::DFFVars.DIEID_CPU, __shared__::DFFVars.DIEID_CPU1","__shared__::DFFVars.DIEID_CPU")'),
            'OpType': f'SORT',
            'PostInstance': f'EvaluateExpression(--result G.U.S.CPU0_UV_NORESENSE_PATCONFIG --storagetype gsds --datatype string --expression Reverse([FUVLD]))',
            'PreInstance': f'WriteSharedStorage(--token G.U.S.CPU0_UNDERVOLTVALUE_BW --value 10)'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = PrimeGetDffTestMethod(**param)

class FleGetDieStatus_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'BypassPort': f'-1',
            'FuseStateUservar': f'Which_Socket.FuseState'
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGetDieStatus(**param)

class FleCheckFuseStringStatus_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'OutputFuseStringLocation': 'Uservar',
            'LockoutBitGroup': f'LockoutBits_00',
            'ByPassPort': f'-1'
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
            'FuseReadTokenNames':Spec('__shared__::TpRule.If_CLASS_NVL_S52C("FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0,FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1","FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU0")'),
            'OutputFuseStringLocation': f'SharedStorage',
            'LockoutBitGroup': f'LockoutBits_00',
            'Registers': Spec('__shared__::TpRule.If_CLASS_NVL_S52C("CPU0,CPU1","CPU0")'),
        }
        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleCheckFuseStringStatusByDies(**param)


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


    def get_start_flow(self, flow_name, module_name='START', is_edc=True,  bin_offset=0, bin_offset2=0, composite_postfix=None, test_instance_postfix=None):
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


        # tests for START / VLD_TRIM / OVLD_STRICT
        t['vld_ovolt_trim_strict'] = PrimePatConfigTestMethod_TestBuilder(name='vld_ovolt_trim_strict', SetPoint='Overvolt_Strict', BypassPort=1, **dparams)
        t['vld_ovolt_trim_strict_vmax'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ovolt_trim_strict_vmax', ConfigName='VLDReadFlow', BypassPort=-1, RegisterNames='VLD', PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_vld_ovolt_strict', FuseGroupToDatalog='', **dparams)
        t['ovolt_strict'] = AuxiliaryTC_TestBuilder(name='ovolt_strict', DataType='String', Expression='Dec2Bin(8,4)', ResultToken='G.U.S.OVLD_VALUE', Storage='SharedStorage', **dparams)

        # tests for START / VLD_TRIM / OVLD_MODERATE
        t['vld_ovolt_trim_moderate'] = PrimePatConfigTestMethod_TestBuilder(name='vld_ovolt_trim_moderate', SetPoint='Overvolt_Moderate', BypassPort=1, **dparams)
        t['vld_ovolt_trim_moderate_vmax'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ovolt_trim_moderate_vmax', ConfigName='VLDReadFlow', BypassPort=-1, RegisterNames='VLD', PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_vld_ovolt_moderate', FuseGroupToDatalog='', **dparams)
        t['ovolt_moderate'] = AuxiliaryTC_TestBuilder(name='ovolt_moderate', DataType='String', Expression='Dec2Bin(8,4)', ResultToken='G.U.S.OVLD_VALUE', Storage='SharedStorage', **dparams)
       
        # tests for START / VLD_TRIM / OVLD_RELAXED
        t['vld_ovolt_trim_relaxed'] = PrimePatConfigTestMethod_TestBuilder(name='vld_ovolt_trim_relaxed', SetPoint='Overvolt_Relaxed', BypassPort=1, **dparams)
        t['vld_ovolt_trim_relaxed_vmax'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ovolt_trim_relaxed_vmax', ConfigName='VLDReadFlow', BypassPort=-1, RegisterNames='VLD', PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_vld_ovolt_relaxed', FuseGroupToDatalog='', **dparams)
        t['ovolt_relaxed'] = AuxiliaryTC_TestBuilder(name='ovolt_relaxed', DataType='String', Expression='Dec2Bin(8,4)', ResultToken='G.U.S.OVLD_VALUE', Storage='SharedStorage', **dparams)

        # tests for START / VLD_TRIM / UVLD_STRICT
        t['vld_uvolt_trim_strict'] = PrimePatConfigTestMethod_TestBuilder(name='vld_uvolt_trim_strict', SetPoint='Undervolt_Strict', BypassPort=1, **dparams)
        t['vld_uvolt_trim_strict_vmax'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uvolt_trim_strict_vmax', ConfigName='VLDReadFlow', BypassPort=-1, RegisterNames='VLD', PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_vld_uvolt_strict', FuseGroupToDatalog='', **dparams)
        t['uvolt_strict'] = AuxiliaryTC_TestBuilder(name='uvolt_strict', DataType='String', Expression='Dec2Bin(8,4)', ResultToken='G.U.S.UVLD_VALUE', Storage='SharedStorage', **dparams)

        # tests for START / VLD_TRIM / UVLD_MODERATE
        t['vld_uvolt_trim_moderate'] = PrimePatConfigTestMethod_TestBuilder(name='vld_uvolt_trim_moderate', SetPoint='Undervolt_Moderate', BypassPort=1, **dparams)
        t['vld_uvolt_trim_moderate_vmax'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uvolt_trim_moderate_vmax', ConfigName='VLDReadFlow', BypassPort=-1, RegisterNames='VLD', PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_vld_uvolt_moderate', FuseGroupToDatalog='', **dparams)
        t['uvolt_moderate'] = AuxiliaryTC_TestBuilder(name='uvolt_moderate', DataType='String', Expression='Dec2Bin(8,4)', ResultToken='G.U.S.UVLD_VALUE', Storage='SharedStorage', **dparams)
       
        # tests for START / VLD_TRIM / UVLD_RELAXED
        t['vld_uvolt_trim_relaxed'] = PrimePatConfigTestMethod_TestBuilder(name='vld_uvolt_trim_relaxed', SetPoint='Undervolt_Relaxed', BypassPort=1, **dparams)
        t['vld_uvolt_trim_relaxed_vmax'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uvolt_trim_relaxed_vmax', ConfigName='VLDReadFlow', BypassPort=-1, RegisterNames='VLD', PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_vld_uvolt_relaxed', FuseGroupToDatalog='', **dparams)
        t['uvolt_relaxed'] = AuxiliaryTC_TestBuilder(name='uvolt_relaxed', DataType='String', Expression='Dec2Bin(8,4)', ResultToken='G.U.S.UVLD_VALUE', Storage='SharedStorage', **dparams)

        # tests for START / VLD_TRIM
        t['perdie_state_init_vld'] = ScreenTC_TestBuilder(name='perdie_state_init_vld', ScreenTestName='PerDieValuesInitVLD', **dparams)
        t['setdff_vld'] = PrimeSetDffTestMethod_TestBuilder(name='setdff_vld', TokenName='FUVLD0,FOVLD0', TokenValue='Storage.UVLD_VALUE, Storage:OVLD_VALUE', BypassPort=-1, **dparams)
        
        

        ##Flow Setup
        ovld_strict_fitems = []
        ovld_strict_fitems.append(t['vld_ovolt_trim_strict'].get_fitem(r0=pFail(ret=0)))
        ovld_strict_fitems.append(t['vld_ovolt_trim_strict_vmax'].get_fitem(r0=pFail(setbin=self.bin(315000, offset), ret=0),
                                                                            r2=pFail(setbin=self.bin(315001, offset), ret=0),
                                                                            r3=pPass(ret=3)))
        ovld_strict_fitems.append(t['ovolt_strict'].get_fitem(r0=pFail(ret=0)))
        ovld_strict_composite = Flow('OVLD_STRICT', *ovld_strict_fitems)

        ovld_moderate_fitems = []
        ovld_moderate_fitems.append(t['vld_ovolt_trim_moderate'].get_fitem(r0=pFail(ret=0)))
        ovld_moderate_fitems.append(t['vld_ovolt_trim_moderate_vmax'].get_fitem(r0=pFail(ret=0),
                                                                            r2=pFail(setbin=self.bin(315002, offset), ret=0),
                                                                            r3=pPass(setbin=self.bin(315003, offset), ret=3)))
        ovld_moderate_fitems.append(t['ovolt_moderate'].get_fitem(r0=pFail(ret=0)))
        ovld_moderate_composite = Flow('OVLD_MODERATE', *ovld_moderate_fitems)

        ovld_relaxed_fitems = []
        ovld_relaxed_fitems.append(t['vld_ovolt_trim_relaxed'].get_fitem(r0=pFail(setbin=self.bin(314700, offset), ret=0)))
        ovld_relaxed_fitems.append(t['vld_ovolt_trim_relaxed_vmax'].get_fitem(r0=pFail(ret=0),
                                                                            r2=pFail(setbin=self.bin(315004, offset), ret=0),
                                                                            r3=pPass(setbin=self.bin(315005, offset), ret=3)))
        ovld_relaxed_fitems.append(t['ovolt_relaxed'].get_fitem(r0=pFail(setbin=self.bin(319000, offset), ret=0)))
        ovld_relaxed_composite = Flow('OVLD_RELAXED', *ovld_relaxed_fitems)

        uvld_strict_fitems = []
        uvld_strict_fitems.append(t['vld_uvolt_trim_strict'].get_fitem(r0=pFail(ret=0)))
        uvld_strict_fitems.append(t['vld_uvolt_trim_strict_vmax'].get_fitem(r0=pFail(setbin=self.bin(314000, offset), ret=0),
                                                                            r2=pFail(setbin=self.bin(314001, offset), ret=0),
                                                                            r3=pPass(ret=3)))
        uvld_strict_fitems.append(t['uvolt_strict'].get_fitem(r0=pFail(ret=0)))
        uvld_strict_composite = Flow('UVLD_STRICT', *uvld_strict_fitems)

        uvld_moderate_fitems = []
        uvld_moderate_fitems.append(t['vld_uvolt_trim_moderate'].get_fitem(r0=pFail(ret=0)))
        uvld_moderate_fitems.append(t['vld_uvolt_trim_moderate_vmax'].get_fitem(r0=pFail(ret=0),
                                                                            r2=pFail(setbin=self.bin(314002, offset), ret=0),
                                                                            r3=pPass(setbin=self.bin(314003, offset), ret=3)))
        uvld_moderate_fitems.append(t['uvolt_moderate'].get_fitem(r0=pFail(ret=0)))
        uvld_moderate_composite = Flow('UVLD_MODERATE', *uvld_moderate_fitems)

        uvld_relaxed_fitems = []
        uvld_relaxed_fitems.append(t['vld_uvolt_trim_relaxed'].get_fitem(r0=pFail(setbin=self.bin(314701, offset), ret=0)))
        uvld_relaxed_fitems.append(t['vld_uvolt_trim_relaxed_vmax'].get_fitem(r0=pFail(ret=0),
                                                                            r2=pFail(setbin=self.bin(314004, offset), ret=0),
                                                                            r3=pPass(setbin=self.bin(314005, offset), ret=3)))
        uvld_relaxed_fitems.append(t['uvolt_relaxed'].get_fitem(r0=pFail(setbin=self.bin(319001, offset), ret=0)))
        uvld_relaxed_composite = Flow('UVLD_RELAXED', *uvld_relaxed_fitems)

        vld_trim_fitems = []
        vld_trim_fitems.append(Fitem('SAME', ovld_strict_composite, r0=pFail(ret=0), r1=pPass(goto=uvld_strict_composite.name), r3=pPass(goto=ovld_moderate_composite.name)))
        vld_trim_fitems.append(Fitem('SAME', ovld_moderate_composite, r0=pFail(ret=0), r1=pPass(goto=uvld_strict_composite.name), r3=pPass(goto=ovld_relaxed_composite.name)))
        vld_trim_fitems.append(Fitem('SAME', ovld_relaxed_composite, r0=pFail(ret=0), r1=pPass(goto=uvld_strict_composite.name), r3=pFail(ret=0)))
        vld_trim_fitems.append(Fitem('SAME', uvld_strict_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto=uvld_moderate_composite.name)))
        vld_trim_fitems.append(Fitem('SAME', uvld_moderate_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pPass(goto=uvld_relaxed_composite.name)))
        vld_trim_fitems.append(Fitem('SAME', uvld_relaxed_composite, r0=pFail(ret=0), r1=pPass(ret=1), r3=pFail(ret=0)))

        vld_trim_composite = Flow('VLD_TRIM', *vld_trim_fitems)

        start_fitems = []
        start_fitems.append(t['perdie_state_init_vld'].get_fitem(r0=pFail(setbin=self.bin(319003, offset),ret=0), r1=pPass(goto=vld_trim_composite.name), r2=pFail(setbin=self.bin(319004, offset),ret=0)))
        start_fitems.append(Fitem('SAME', vld_trim_composite, r0=pFail(ret=1), r1=pPass(goto='NEXT')))
        start_fitems.append(t['setdff_vld'].get_fitem(r0=pFail(setbin=self.bin(319005, offset),ret=0), r1=pPass(ret=1)))
        Flow(flow_name,*start_fitems)


    def get_begincpupkg_flow(self, flow_name, module_name='BEGINCPUPKG', is_edc=False,  bin_offset=0, bin_offset2=0, composite_postfix=None, test_instance_postfix=None):
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

        t['if_18ap'] = AuxiliaryTC_TestBuilder(name='if_18ap', BypassPort=-1, Expression="IsMatch([_UserVars.IF_18AP], 'YES')", DataType='String', Storage='UserVar', ResultPort='[R]?1:2', **dparams)
        t['all_in_one_fork_cpu'] = ScreenTC_TestBuilder(name='all_in_one_fork_cpu', ScreenTestSet='CXX_VLD_PERDUTINIT', **dparams)
        t['fuse_string_valid_check'] = FleCheckFuseStringStatusByDies_TestBuilder(name='fuse_string_valid_check', BypassPort=-1, **dparams)
        #t['fuse_string_valid_check_cpu1'] = FleCheckFuseStringStatus_TestBuilder(name='fuse_string_valid_check_cpu1', FuseReadTokenName='IPC::FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX.FuseReadOutputStr_CPU1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S28C(1,1)'), **dparams)
        t['socket_mode_check'] = FleGetDieStatus_TestBuilder(name='socket_mode_check', FuseStateUservar='Which_Socket.FuseState', Register='CPU0', BypassPort=-1, **dparams)
        t['set_default_dff'] = ScreenTC_TestBuilder(name='set_default_dff', ScreenTestSet='CXX_VLD_SET_DEFAULT', **dparams)
       
        ###### CPU0 #####
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_09
        #t['vld_09_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_09_uv', SetPoint='CXX_Undervolt09', BypassPort=-1, **dparams)
        #t['vld_uv_09'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_09', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage09'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage09', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_09.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_08
        #t['vld_08_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_08_uv', SetPoint='CXX_Undervolt08', BypassPort=-1, **dparams)
        #t['vld_uv_08'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_08', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage08'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage08', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_08.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_07
        #t['vld_07_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_07_uv', SetPoint='CXX_Undervolt07', BypassPort=-1, **dparams)
        #t['vld_uv_07'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_07', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage07'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage07', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_07.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_06
        #t['vld_06_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_06_uv', SetPoint='CXX_Undervolt06', BypassPort=-1, **dparams)
        #t['vld_uv_06'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_06', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage06'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage06', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_06.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_05
        #t['vld_05_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_05_uv', SetPoint='CXX_Undervolt05', BypassPort=-1, **dparams)
        #t['vld_uv_05'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_05', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage05'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage05', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_05.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_04
        #t['vld_04_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_04_uv', SetPoint='CXX_Undervolt04', BypassPort=-1, **dparams)
        #t['vld_uv_04'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_04', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage04'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage04', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_04.json', **dparams)
        
        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_STRICT
        t['vld_03_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_03_uv', SetPoint='CXX_Undervolt03', BypassPort=-1, **dparams)
        t['vld_uv_03'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_03', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['vld_setsharedstorage03'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage03', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_03.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_MODERATE
        t['vld_02_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_02_uv', SetPoint='CXX_Undervolt02', BypassPort=-1, **dparams)
        t['vld_uv_02'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_02', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['vld_setsharedstorage02'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage02', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_02.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_RELAXED
        t['vld_01_uv'] = PrimePatConfigTestMethod_TestBuilder(name='vld_01_uv', SetPoint='CXX_Undervolt01', BypassPort=-1, **dparams)
        t['vld_uv_01'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_01', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['vld_setsharedstorage01'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage01', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_01.json', **dparams)

        # tests for BEGIN / VLD_TRIM
        t['uvldsetdff'] = PrimeSetDffTestMethod_TestBuilder(name='uvldsetdff', DieId=Spec('__shared__::DFFVars.DIEID_CPU'), TokenName='FUVLDC0,FUVLDC1,FUBWVLD0,FUBWVLD1', TokenValue='Storage.CXX_UNDERVOLTVALUE_NORESENSE,Storage.CXX_UNDERVOLTVALUE_NORESENSE,Storage.CXX_UNDERVOLTVALUE_BW,Storage.CXX_UNDERVOLTVALUE_BW', BypassPort=Spec("FUS_FUSEVLD_CKX_Rules.FUSE_X_X_K_BEGINCPUPKG_X_X_X_X_UVLDSETDFF_BypassPort(-1,1)"), **dparams)
        
        #tests for BEGIN / OVLD_REGISTER_METHOD / OV_10
        #t['vld_10_ov'] = PrimePatConfigTestMethod_TestBuilder(name='vld_10_ov', SetPoint='CXX_Overvolt10', BypassPort=-1, **dparams)
        #t['vld_ov_10'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_10', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['ovld_setsharedstorage10'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage10', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_10.json', **dparams)

        #tests for BEGIN / OVLD_REGISTER_METHOD / OVLD_STRICT
        t['vld_09_ov'] = PrimePatConfigTestMethod_TestBuilder(name='vld_09_ov', SetPoint='CXX_Overvolt09', BypassPort=-1, **dparams)
        t['vld_ov_09'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_09', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['ovld_setsharedstorage09'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage09', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_09.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_MODERATE
        t['vld_08_ov'] = PrimePatConfigTestMethod_TestBuilder(name='vld_08_ov', SetPoint='CXX_Overvolt08', BypassPort=-1, **dparams)
        t['vld_ov_08'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_08', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['ovld_setsharedstorage08'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage08', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_08.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_RELAXED
        t['vld_07_ov'] = PrimePatConfigTestMethod_TestBuilder(name='vld_07_ov', SetPoint='CXX_Overvolt07', BypassPort=-1, **dparams)
        t['vld_ov_07'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_07', ConfigName='VLDReadFlow', BypassPort=-1, PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['ovld_setsharedstorage07'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage07', BypassPort=-1, Path='./InputFiles/VLD_SharedStorage_07.json', **dparams)

        # tests for BEGIN / VLD_TRIM
        t['ovldsetdff'] = PrimeSetDffTestMethod_TestBuilder(name='ovldsetdff', DieId=Spec('__shared__::DFFVars.DIEID_CPU'), TokenName='FOVLDC0,FOVLDC1,FOBWVLD0,FOBWVLD1', TokenValue='Storage.CXX_OVERVOLTVALUE_NORESENSE,Storage.CXX_OVERVOLTVALUE_NORESENSE,Storage.CXX_OVERVOLTVALUE_BW,Storage.CXX_OVERVOLTVALUE_BW', BypassPort=Spec("FUS_FUSEVLD_CKX_Rules.FUSE_X_X_K_BEGINCPUPKG_X_X_X_X_OVLDSETDFF_BypassPort(-1,1)"), **dparams)

        ###### CPU1 #####
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_09
        #t['vld_09_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_09_uv_cpu1', SetPoint='CXX_Undervolt09', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        #t['vld_uv_09_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_09_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage09_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage09_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_09.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_08
        #t['vld_08_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_08_uv_cpu1', SetPoint='CXX_Undervolt08', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        #t['vld_uv_08_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_08_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage08_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage08_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_08.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_07
        #t['vld_07_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_07_uv_cpu1', SetPoint='CXX_Undervolt07', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        #t['vld_uv_07_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_07_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage07_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage07_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_07.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_06
        #t['vld_06_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_06_uv_cpu1', SetPoint='CXX_Undervolt06', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        #t['vld_uv_06_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_06_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage06_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage06_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_06.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_05
        #t['vld_05_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_05_uv_cpu1', SetPoint='CXX_Undervolt05', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        #t['vld_uv_05_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_05_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage05_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage05_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_05.json', **dparams)
        # tests for BEGIN / UVLD_REGISTER_METHOD / UV_04
        #t['vld_04_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_04_uv_cpu1', SetPoint='CXX_Undervolt04', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        #t['vld_uv_04_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_04_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['vld_setsharedstorage04_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage04_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_04.json', **dparams)
        
        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_STRICT
        t['vld_03_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_03_uv_cpu1', SetPoint='CXX_Undervolt03', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        t['vld_uv_03_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_03_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['vld_setsharedstorage03_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage03_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_03.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_MODERATE
        t['vld_02_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_02_uv_cpu1', SetPoint='CXX_Undervolt02', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        t['vld_uv_02_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_02_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['vld_setsharedstorage02_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage02_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_02.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_RELAXED
        t['vld_01_uv_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_01_uv_cpu1', SetPoint='CXX_Undervolt01', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        t['vld_uv_01_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_uv_01_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Undervolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['vld_setsharedstorage01_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='vld_setsharedstorage01_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_01.json', **dparams)

        # tests for BEGIN / VLD_TRIM
        t['uvldsetdff_cpu1'] = PrimeSetDffTestMethod_TestBuilder(name='uvldsetdff_cpu1', DieId=Spec('__shared__::DFFVars.DIEID_CPU1'), TokenName='FUVLDC0,FUVLDC1,FUBWVLD0,FUBWVLD1', TokenValue='Storage.CXX_UNDERVOLTVALUE_NORESENSE,Storage.CXX_UNDERVOLTVALUE_NORESENSE,Storage.CXX_UNDERVOLTVALUE_BW,Storage.CXX_UNDERVOLTVALUE_BW', BypassPort=Spec("FUS_FUSEVLD_CKX_Rules.FUSE_X_X_K_BEGINCPUPKG_X_X_X_X_UVLDSETDFF_CPU1_BypassPort(-1,1)"), **dparams)
        
        #tests for BEGIN / OVLD_REGISTER_METHOD / OV_10
        #t['vld_10_ov_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_10_ov_cpu1', SetPoint='CXX_Overvolt10', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        #t['vld_ov_10_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_10_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        #t['ovld_setsharedstorage10_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage10_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_10.json', **dparams)

        #tests for BEGIN / OVLD_REGISTER_METHOD / OVLD_STRICT
        t['vld_09_ov_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_09_ov_cpu1', SetPoint='CXX_Overvolt09', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        t['vld_ov_09_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_09_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['ovld_setsharedstorage09_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage09_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_09.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_MODERATE
        t['vld_08_ov_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_08_ov_cpu1', SetPoint='CXX_Overvolt08', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        t['vld_ov_08_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_08_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['ovld_setsharedstorage08_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage08_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_08.json', **dparams)

        # tests for BEGIN / UVLD_REGISTER_METHOD / UVLD_RELAXED
        t['vld_07_ov_cpu1'] = PrimePatConfigTestMethod_TestBuilder(name='vld_07_ov_cpu1', SetPoint='CXX_Overvolt07', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), **dparams)
        t['vld_ov_07_cpu1'] = PrimeFuseReadMaskTestMethod_TestBuilder(name='vld_ov_07_cpu1', ConfigName='VLDReadFlow', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), PassingMaskName='Overvolt_VLD', FailingMaskName='Short_VLD,Open_VLD', Patlist='cpu_fuse_hvm_vld_vbump', FuseGroupToDatalog='', **dparams)
        t['ovld_setsharedstorage07_cpu1'] = PrimeSharedStorageInserterTestMethod_TestBuilder(name='ovld_setsharedstorage07_cpu1', BypassPort=Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'), Path='./InputFiles/VLD_SharedStorage_07.json', **dparams)

        # tests for BEGIN / VLD_TRIM
        t['ovldsetdff_cpu1'] = PrimeSetDffTestMethod_TestBuilder(name='ovldsetdff_cpu1', DieId=Spec('__shared__::DFFVars.DIEID_CPU1'), TokenName='FOVLDC0,FOVLDC1,FOBWVLD0,FOBWVLD1', TokenValue='Storage.CXX_OVERVOLTVALUE_NORESENSE,Storage.CXX_OVERVOLTVALUE_NORESENSE,Storage.CXX_OVERVOLTVALUE_BW,Storage.CXX_OVERVOLTVALUE_BW', BypassPort=Spec("FUS_FUSEVLD_CKX_Rules.FUSE_X_X_K_BEGINCPUPKG_X_X_X_X_OVLDSETDFF_CPU1_BypassPort(-1,1)"), **dparams)

        #default vld dff
        t['setdff'] = PrimeSetDffTestMethod_TestBuilder(name='setdff', DieId=Spec('__shared__::DFFVars.DIEID_CPU'), TokenName='FOBWVLD0,FOBWVLD1,FUBWVLD0,FUBWVLD1', TokenValue='Storage.CXX_OVERVOLTVALUE_BW,Storage.CXX_OVERVOLTVALUE_BW,Storage.CXX_UNDERVOLTVALUE_BW,Storage.CXX_UNDERVOLTVALUE_BW', BypassPort=Spec("FUS_FUSEVLD_CKX_Rules.FUSE_X_X_K_BEGINCPUPKG_X_X_X_X_SETDFF_BypassPort(-1,1)"), **dparams)
        t['setdff_cpu1'] = PrimeSetDffTestMethod_TestBuilder(name='setdff_cpu1', DieId=Spec('__shared__::DFFVars.DIEID_CPU1'), TokenName='FOBWVLD0,FOBWVLD1,FUBWVLD0,FUBWVLD1', TokenValue='Storage.CXX_OVERVOLTVALUE_BW,Storage.CXX_OVERVOLTVALUE_BW,Storage.CXX_UNDERVOLTVALUE_BW,Storage.CXX_UNDERVOLTVALUE_BW', BypassPort=Spec("FUS_FUSEVLD_CKX_Rules.FUSE_X_X_K_BEGINCPUPKG_X_X_X_X_SETDFF_CPU1_BypassPort(-1,1)"), **dparams)


        #uvld_09_fitems = []
        #uvld_09_fitems.append(t['vld_09_uv'].get_fitem(r0=pFail(setbin=self.bin(314746, offset), ret=0)))
        #uvld_09_fitems.append(t['vld_uv_09'].get_fitem(r0=pFail(setbin=self.bin(314022, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314023, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #uvld_09_fitems.append(t['vld_setsharedstorage09'].get_fitem(r0=pFail(setbin=self.bin(314876, offset), ret=0)))
        #uvld_09_composite = Flow('UV_09', *uvld_09_fitems)
        
        #uvld_08_fitems = []
        #uvld_08_fitems.append(t['vld_08_uv'].get_fitem(r0=pFail(setbin=self.bin(314747, offset), ret=0)))
        #uvld_08_fitems.append(t['vld_uv_08'].get_fitem(r0=pFail(setbin=self.bin(314024, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314025, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #uvld_08_fitems.append(t['vld_setsharedstorage08'].get_fitem(r0=pFail(setbin=self.bin(314877, offset), ret=0)))
        #uvld_08_composite = Flow('UV_08', *uvld_08_fitems)
        
        #uvld_07_fitems = []
        #uvld_07_fitems.append(t['vld_07_uv'].get_fitem(r0=pFail(setbin=self.bin(314722, offset), ret=0)))
        #uvld_07_fitems.append(t['vld_uv_07'].get_fitem(r0=pFail(setbin=self.bin(314026, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314027, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #uvld_07_fitems.append(t['vld_setsharedstorage07'].get_fitem(r0=pFail(setbin=self.bin(314878, offset), ret=0)))
        #uvld_07_composite = Flow('UV_07', *uvld_07_fitems)
        
        #uvld_06_fitems = []
        #uvld_06_fitems.append(t['vld_06_uv'].get_fitem(r0=pFail(setbin=self.bin(314723, offset), ret=0)))
        #uvld_06_fitems.append(t['vld_uv_06'].get_fitem(r0=pFail(setbin=self.bin(314028, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314029, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #uvld_06_fitems.append(t['vld_setsharedstorage06'].get_fitem(r0=pFail(setbin=self.bin(314879, offset), ret=0)))
        #uvld_06_composite = Flow('UV_06', *uvld_06_fitems)
        
        #uvld_05_fitems = []
        #uvld_05_fitems.append(t['vld_05_uv'].get_fitem(r0=pFail(setbin=self.bin(314724, offset), ret=0)))
        #uvld_05_fitems.append(t['vld_uv_05'].get_fitem(r0=pFail(setbin=self.bin(314030, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314031, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #uvld_05_fitems.append(t['vld_setsharedstorage05'].get_fitem(r0=pFail(setbin=self.bin(314880, offset), ret=0)))
        #uvld_05_composite = Flow('UV_05', *uvld_05_fitems)
        
        #uvld_04_fitems = []
        #uvld_04_fitems.append(t['vld_04_uv'].get_fitem(r0=pFail(setbin=self.bin(314725, offset), ret=0)))
        #uvld_04_fitems.append(t['vld_uv_04'].get_fitem(r0=pFail(setbin=self.bin(314032, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314033, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #uvld_04_fitems.append(t['vld_setsharedstorage04'].get_fitem(r0=pFail(setbin=self.bin(314855, offset), ret=0)))
        #uvld_04_composite = Flow('UV_04', *uvld_04_fitems)
        
        uvld_strict_fitems = []
        uvld_strict_fitems.append(t['vld_03_uv'].get_fitem(r0=pFail(setbin=self.bin(314726, offset), ret=0)))
        uvld_strict_fitems.append(t['vld_uv_03'].get_fitem(r0=pFail(setbin=self.bin(314070, offset), ret=0),
                                                           r2=pPass(ret=2),
                                                           r3=pFail(setbin=self.bin(314071, offset), ret=0),
                                                           r4=pPass(ret=2)))
        uvld_strict_fitems.append(t['vld_setsharedstorage03'].get_fitem(r0=pFail(setbin=self.bin(314856, offset), ret=0)))
        uvld_strict_composite = Flow('UV_03', *uvld_strict_fitems)

        uvld_moderate_fitems = []
        uvld_moderate_fitems.append(t['vld_02_uv'].get_fitem(r0=pFail(setbin=self.bin(314727, offset), ret=0)))
        uvld_moderate_fitems.append(t['vld_uv_02'].get_fitem(r0=pFail(setbin=self.bin(314065, offset), ret=0),
                                                             r2=pPass(ret=2),
                                                             r3=pFail(setbin=self.bin(314066, offset), ret=0),
                                                             r4=pPass(ret=2)))
        uvld_moderate_fitems.append(t['vld_setsharedstorage02'].get_fitem(r0=pFail(setbin=self.bin(314857, offset), ret=0)))
        uvld_moderate_composite = Flow('UV_02', *uvld_moderate_fitems)

        uvld_relaxed_fitems = []
        uvld_relaxed_fitems.append(t['vld_01_uv'].get_fitem(r0=pFail(setbin=self.bin(314728, offset), ret=0)))
        uvld_relaxed_fitems.append(t['vld_uv_01'].get_fitem(r0=pFail(setbin=self.bin(314006, offset), ret=0),
                                                            r2=pFail(setbin=self.bin(314007, offset), ret=0),
                                                            r3=pFail(setbin=self.bin(314008, offset), ret=0),
                                                            r4=pFail(setbin=self.bin(314009, offset), ret=0)))
        uvld_relaxed_fitems.append(t['vld_setsharedstorage01'].get_fitem(r0=pFail(setbin=self.bin(314858, offset), ret=0)))
        uvld_relaxed_composite = Flow('UV_01', *uvld_relaxed_fitems)
        
        uvld_register_method_fitems = []
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_sort_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_strict_composite.name)))
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_09_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_08_composite.name)))
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_08_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_07_composite.name)))
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_07_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_06_composite.name)))
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_06_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_05_composite.name)))
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_05_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_04_composite.name)))
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_04_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_strict_composite.name)))      
        uvld_register_method_fitems.append(Fitem('SAME', uvld_strict_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_moderate_composite.name)))
        uvld_register_method_fitems.append(Fitem('SAME', uvld_moderate_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_relaxed_composite.name)))
        uvld_register_method_fitems.append(Fitem('SAME', uvld_relaxed_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        uvld_register_method_composite = Flow('UVLD_REGISTER_METHOD', uvld_register_method_fitems)
        
        #ovld_10_fitems = []
        #ovld_10_fitems.append(t['vld_10_ov'].get_fitem(r0=pFail(setbin=self.bin(314729, offset), ret=0)))
        #ovld_10_fitems.append(t['vld_ov_10'].get_fitem(r0=pFail(setbin=self.bin(314020, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314021, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #ovld_10_fitems.append(t['ovld_setsharedstorage10'].get_fitem(r0=pFail(setbin=self.bin(314859, offset), ret=0)))
        #ovld_10_composite = Flow('OV_10', *ovld_10_fitems)
        
        ovld_strict_fitems = []
        ovld_strict_fitems.append(t['vld_09_ov'].get_fitem(r0=pFail(setbin=self.bin(314748, offset), ret=0)))
        ovld_strict_fitems.append(t['vld_ov_09'].get_fitem(r0=pFail(setbin=self.bin(314012, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(314013, offset), ret=0),
                                                           r3=pPass(ret=2),
                                                           r4=pPass(ret=2)))
        ovld_strict_fitems.append(t['ovld_setsharedstorage09'].get_fitem(r0=pFail(setbin=self.bin(314860, offset), ret=0)))
        ovld_strict_composite = Flow('OV_09', *ovld_strict_fitems)

        ovld_moderate_fitems = []
        ovld_moderate_fitems.append(t['vld_08_ov'].get_fitem(r0=pFail(setbin=self.bin(314749, offset), ret=0)))
        ovld_moderate_fitems.append(t['vld_ov_08'].get_fitem(r0=pFail(setbin=self.bin(314014, offset), ret=0),
                                                             r2=pFail(setbin=self.bin(314015, offset), ret=0),
                                                             r3=pPass(ret=2),
                                                             r4=pPass(ret=2)))
        ovld_moderate_fitems.append(t['ovld_setsharedstorage08'].get_fitem(r0=pFail(setbin=self.bin(314861, offset), ret=0)))
        ovld_moderate_composite = Flow('OV_08', *ovld_moderate_fitems)

        ovld_relaxed_fitems = []
        ovld_relaxed_fitems.append(t['vld_07_ov'].get_fitem(r0=pFail(setbin=self.bin(314732, offset), ret=0)))
        ovld_relaxed_fitems.append(t['vld_ov_07'].get_fitem(r0=pFail(setbin=self.bin(314016, offset), ret=0),
                                                            r2=pFail(setbin=self.bin(314017, offset), ret=0),
                                                            r3=pFail(setbin=self.bin(314018, offset), ret=0),
                                                            r4=pFail(setbin=self.bin(314019, offset), ret=0)))
        ovld_relaxed_fitems.append(t['ovld_setsharedstorage07'].get_fitem(r0=pFail(setbin=self.bin(314862, offset), ret=0)))
        ovld_relaxed_composite = Flow('OV_07', *ovld_relaxed_fitems)

        ovld_register_method_fitems = []
        #ovld_register_method_fitems.append(Fitem('SAME', ovld_10_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=ovld_strict_composite.name)))
        ovld_register_method_fitems.append(Fitem('SAME', ovld_strict_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=ovld_moderate_composite.name)))
        ovld_register_method_fitems.append(Fitem('SAME', ovld_moderate_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=ovld_relaxed_composite.name)))
        ovld_register_method_fitems.append(Fitem('SAME', ovld_relaxed_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        ovld_register_method_composite = Flow('OVLD_REGISTER_METHOD', *ovld_register_method_fitems)

        ##CPU1
        #cpu1_uvld_09_fitems = []
        #cpu1_uvld_09_fitems.append(t['vld_09_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314733, offset), ret=0)))
        #cpu1_uvld_09_fitems.append(t['vld_uv_09_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314034, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314035, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #cpu1_uvld_09_fitems.append(t['vld_setsharedstorage09_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314863, offset), ret=0)))
        #cpu1_uvld_09_composite = Flow('UV_09_CPU1', *cpu1_uvld_09_fitems)
        
        #cpu1_uvld_08_fitems = []
        #cpu1_uvld_08_fitems.append(t['vld_08_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314734, offset), ret=0)))
        #cpu1_uvld_08_fitems.append(t['vld_uv_08_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314036, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314037, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #cpu1_uvld_08_fitems.append(t['vld_setsharedstorage08_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314864, offset), ret=0)))
        #cpu1_uvld_08_composite = Flow('UV_08_CPU1', *cpu1_uvld_08_fitems)
        
        #cpu1_uvld_07_fitems = []
        #cpu1_uvld_07_fitems.append(t['vld_07_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314735, offset), ret=0)))
        #cpu1_uvld_07_fitems.append(t['vld_uv_07_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314038, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314039, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #cpu1_uvld_07_fitems.append(t['vld_setsharedstorage07_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314865, offset), ret=0)))
        #cpu1_uvld_07_composite = Flow('UV_07_CPU1', *cpu1_uvld_07_fitems)
        
        #cpu1_uvld_06_fitems = []
        #cpu1_uvld_06_fitems.append(t['vld_06_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314736, offset), ret=0)))
        #cpu1_uvld_06_fitems.append(t['vld_uv_06_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314040, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314041, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #cpu1_uvld_06_fitems.append(t['vld_setsharedstorage06_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314866, offset), ret=0)))
        #cpu1_uvld_06_composite = Flow('UV_06_CPU1', *cpu1_uvld_06_fitems)
        
        #cpu1_uvld_05_fitems = []
        #cpu1_uvld_05_fitems.append(t['vld_05_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314737, offset), ret=0)))
        #cpu1_uvld_05_fitems.append(t['vld_uv_05_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314042, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314043, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #cpu1_uvld_05_fitems.append(t['vld_setsharedstorage05_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314867, offset), ret=0)))
        #cpu1_uvld_05_composite = Flow('UV_05_CPU1', *cpu1_uvld_05_fitems)
        
        #cpu1_uvld_04_fitems = []
        #cpu1_uvld_04_fitems.append(t['vld_04_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314738, offset), ret=0)))
        #cpu1_uvld_04_fitems.append(t['vld_uv_04_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314044, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314045, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #cpu1_uvld_04_fitems.append(t['vld_setsharedstorage04_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314868, offset), ret=0)))
        #cpu1_uvld_04_composite = Flow('UV_04_CPU1', *cpu1_uvld_04_fitems)
        
        cpu1_uvld_strict_fitems = []
        cpu1_uvld_strict_fitems.append(t['vld_03_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314739, offset), ret=0)))
        cpu1_uvld_strict_fitems.append(t['vld_uv_03_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314046, offset), ret=0),
                                                           r2=pPass(ret=2),
                                                           r3=pFail(setbin=self.bin(314047, offset), ret=0),
                                                           r4=pPass(ret=2)))
        cpu1_uvld_strict_fitems.append(t['vld_setsharedstorage03_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314869, offset), ret=0)))
        cpu1_uvld_strict_composite = Flow('UV_03_CPU1', *cpu1_uvld_strict_fitems)

        cpu1_uvld_moderate_fitems = []
        cpu1_uvld_moderate_fitems.append(t['vld_02_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314740, offset), ret=0)))
        cpu1_uvld_moderate_fitems.append(t['vld_uv_02_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314048, offset), ret=0),
                                                             r2=pPass(ret=2),
                                                             r3=pFail(setbin=self.bin(314049, offset), ret=0),
                                                             r4=pPass(ret=2)))
        cpu1_uvld_moderate_fitems.append(t['vld_setsharedstorage02_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314870, offset), ret=0)))
        cpu1_uvld_moderate_composite = Flow('UV_02_CPU1', *cpu1_uvld_moderate_fitems)

        cpu1_uvld_relaxed_fitems = []
        cpu1_uvld_relaxed_fitems.append(t['vld_01_uv_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314741, offset), ret=0)))
        cpu1_uvld_relaxed_fitems.append(t['vld_uv_01_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314050, offset), ret=0),
                                                            r2=pFail(setbin=self.bin(314051, offset), ret=0),
                                                            r3=pFail(setbin=self.bin(314052, offset), ret=0),
                                                            r4=pFail(setbin=self.bin(314053, offset), ret=0)))
        cpu1_uvld_relaxed_fitems.append(t['vld_setsharedstorage01_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314871, offset), ret=0)))
        cpu1_uvld_relaxed_composite = Flow('UV_01_CPU1', *cpu1_uvld_relaxed_fitems)
        
        cpu1_uvld_register_method_fitems = []
        #uvld_register_method_fitems.append(Fitem('SAME', uvld_sort_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=uvld_strict_composite.name)))
        #cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_09_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_08_composite.name)))
        #cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_08_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_07_composite.name)))
        #cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_07_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_06_composite.name)))
        #cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_06_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_05_composite.name)))
        #cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_05_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_04_composite.name)))
        #cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_04_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_strict_composite.name)))      
        cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_strict_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_moderate_composite.name)))
        cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_moderate_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_uvld_relaxed_composite.name)))
        cpu1_uvld_register_method_fitems.append(Fitem('SAME', cpu1_uvld_relaxed_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        cpu1_uvld_register_method_composite = Flow('CPU1_UVLD_REGISTER_METHOD', cpu1_uvld_register_method_fitems)
        
        #cpu1_ovld_10_fitems = []
        #cpu1_ovld_10_fitems.append(t['vld_10_ov_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314742, offset), ret=0)))
        #cpu1_ovld_10_fitems.append(t['vld_ov_10_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314054, offset), ret=0),
        #                                                   r2=pPass(ret=2),
        #                                                   r3=pFail(setbin=self.bin(314055, offset), ret=0),
        #                                                   r4=pPass(ret=2)))
        #cpu1_ovld_10_fitems.append(t['ovld_setsharedstorage10_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314872, offset), ret=0)))
        #cpu1_ovld_10_composite = Flow('OV_10_CPU1', *cpu1_ovld_10_fitems)
        
        cpu1_ovld_strict_fitems = []
        cpu1_ovld_strict_fitems.append(t['vld_09_ov_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314743, offset), ret=0)))
        cpu1_ovld_strict_fitems.append(t['vld_ov_09_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314056, offset), ret=0),
                                                           r2=pFail(setbin=self.bin(314057, offset), ret=0),
                                                           r3=pPass(ret=2),
                                                           r4=pPass(ret=2)))
        cpu1_ovld_strict_fitems.append(t['ovld_setsharedstorage09_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314873, offset), ret=0)))
        cpu1_ovld_strict_composite = Flow('OV_09_CPU1', *cpu1_ovld_strict_fitems)

        cpu1_ovld_moderate_fitems = []
        cpu1_ovld_moderate_fitems.append(t['vld_08_ov_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314744, offset), ret=0)))
        cpu1_ovld_moderate_fitems.append(t['vld_ov_08_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314068, offset), ret=0),
                                                             r2=pFail(setbin=self.bin(314059, offset), ret=0),
                                                             r3=pPass(ret=2),
                                                             r4=pPass(ret=2)))
        cpu1_ovld_moderate_fitems.append(t['ovld_setsharedstorage08_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314874, offset), ret=0)))
        cpu1_ovld_moderate_composite = Flow('OV_08_CPU1', *cpu1_ovld_moderate_fitems)

        cpu1_ovld_relaxed_fitems = []
        cpu1_ovld_relaxed_fitems.append(t['vld_07_ov_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314745, offset), ret=0)))
        cpu1_ovld_relaxed_fitems.append(t['vld_ov_07_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314060, offset), ret=0),
                                                            r2=pFail(setbin=self.bin(314061, offset), ret=0),
                                                            r3=pFail(setbin=self.bin(314062, offset), ret=0),
                                                            r4=pFail(setbin=self.bin(314063, offset), ret=0)))
        cpu1_ovld_relaxed_fitems.append(t['ovld_setsharedstorage07_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314875, offset), ret=0)))
        cpu1_ovld_relaxed_composite = Flow('OV_07_CPU1', *cpu1_ovld_relaxed_fitems)

        cpu1_ovld_register_method_fitems = []
        #cpu1_ovld_register_method_fitems.append(Fitem('SAME', cpu1_ovld_10_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_ovld_strict_composite.name)))
        cpu1_ovld_register_method_fitems.append(Fitem('SAME', cpu1_ovld_strict_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_ovld_moderate_composite.name)))
        cpu1_ovld_register_method_fitems.append(Fitem('SAME', cpu1_ovld_moderate_composite, r0=pFail(ret=0), r1=pPass(ret=1), r2=pPass(goto=cpu1_ovld_relaxed_composite.name)))
        cpu1_ovld_register_method_fitems.append(Fitem('SAME', cpu1_ovld_relaxed_composite, r0=pFail(ret=0), r1=pPass(ret=1)))
        cpu1_ovld_register_method_composite = Flow('CPU1_OVLD_REGISTER_METHOD', *cpu1_ovld_register_method_fitems)
        
        begincpupkg_fitems = []
        begincpupkg_fitems.append(t['if_18ap'].get_fitem(r0=pFail(setbin=self.bin(314895, offset), ret=0),
                                                         r2=pPass(ret=1)
                                                         ))
        begincpupkg_fitems.append(t['fuse_string_valid_check'].get_fitem(r0=pFail(setbin=self.bin(314880, offset), ret=0), 
                                                                         r1=pPass(goto='NEXT'), 
                                                                         r2=pFail(setbin=self.bin(314881, offset), ret=0), 
                                                                         r3=pPass(goto='NEXT'),
                                                                         r4=pFail(setbin=self.bin(314882, offset), ret=0), 
                                                                         r5=pFail(setbin=self.bin(314883, offset), ret=0), 
                                                                         r6=pFail(setbin=self.bin(314884, offset), ret=0),
                                                                         r7=pFail(setbin=self.bin(314885, offset), ret=0)
                                                                         ))
        #begincpupkg_fitems.append(t['fuse_string_valid_check_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314895, offset), ret=0), 
        #                                                                      r1=pPass(goto='NEXT'),
        #                                                                      r2=pFail(setbin=self.bin(314895, offset), ret=0), 
        #                                                                      r3=pPass(goto='NEXT'),
        #                                                                      r4=pFail(setbin=self.bin(314895, offset), ret=0), 
        #                                                                      r5=pFail(setbin=self.bin(314895, offset), ret=0), 
        #                                                                      r6=pFail(setbin=self.bin(314895, offset), ret=0)
        #                                                                      ))                                                                      
        begincpupkg_fitems.append(t['socket_mode_check'].get_fitem(r0=pFail(setbin=self.bin(314886, offset), ret=0), 
                                                                   r1=pPass(goto='NEXT'),
                                                                   r2=pFail(setbin=self.bin(314887, offset), ret=0), 
                                                                   r3=pPass(goto='FUSE_X_SCREENTC_K_BEGINCPUPKG_X_X_X_X_SET_DEFAULT_DFF'),
                                                                   r4=pFail(setbin=self.bin(314888, offset), ret=0)
                                                                   ))
        begincpupkg_fitems.append(t['all_in_one_fork_cpu'].get_fitem(r0=pFail(setbin=self.bin(314876, offset), ret=0), 
                                                                   r1=pPass(goto='NEXT'),
                                                                   r2=pFail(setbin=self.bin(314877, offset), ret=0), 
                                                                   r3=pFail(setbin=self.bin(314878, offset), ret=0),
                                                                   r4=pFail(setbin=self.bin(314879, offset), ret=0)
                                                                   ))
        begincpupkg_fitems.append(Fitem('SAME', ovld_register_method_composite, r0=pFail(ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(t['ovldsetdff'].get_fitem(r0=pFail(setbin=self.bin(314891, offset), ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(Fitem('SAME', uvld_register_method_composite, r0=pFail(ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(t['uvldsetdff'].get_fitem(r0=pFail(setbin=self.bin(314890, offset), ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(Fitem('SAME', cpu1_ovld_register_method_composite, r0=pFail(ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(t['ovldsetdff_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314893, offset), ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(Fitem('SAME', cpu1_uvld_register_method_composite, r0=pFail(ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(t['uvldsetdff_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314892, offset), ret=0), r1=pPass(ret=1)))
        begincpupkg_fitems.append(t['set_default_dff'].get_fitem(r0=pFail(setbin=self.bin(314896, offset), ret=0), 
                                                                   r1=pPass(goto='NEXT'),
                                                                   r2=pPass(ret=1), 
                                                                   r3=pFail(setbin=self.bin(314897, offset), ret=0),
                                                                   r4=pFail(setbin=self.bin(314898, offset), ret=0)
                                                                   ))
        begincpupkg_fitems.append(t['setdff'].get_fitem(r0=pFail(setbin=self.bin(314899, offset), ret=0), r1=pPass(goto='NEXT')))
        begincpupkg_fitems.append(t['setdff_cpu1'].get_fitem(r0=pFail(setbin=self.bin(314863, offset), ret=0), r1=pPass(ret=1)))

        Flow(flow_name,*begincpupkg_fitems)
        
    

    

class CDIE_816_SORT(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='sort')
        self.LevelsTc = 'BASE::SBF_nom_lvl'
        self.TimingsTc = 'BASE::cpu_fun_timing_vctr0200MTs_hvmclk100_tck100r2_tstprtclk100r2'
        self.PrePlist = None

    def initialize(self, name1, name2, rev):
        Import("FUS_FUSEUVLD_CXX.usrv")
        InitializeNVLSort(name1, name2, defaultrm1bin=-31, defaultrm2bin=-31, binrange=[(3100, 3199)])
        MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        
        # Add the necessary files to import in your mtpl
        

class CDIE_816_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.LevelsTc = 'BASE::cpu_all_bf_x_x_pkg_lvl_nom'
        self.TimingsTc = 'BASE::pkg_cpu_fun_timing_mts100_tstprtclk50_tck100'
        self.PrePlist = ''

    def initialize(self, name1, name2, rev):
        #Import("FUS_FUSEVLD_CXX.usrv")
        InitializeNVLClass(name1, name2, defaultrm1bin=(98312000,98313999), defaultrm2bin=(99312000,99313999), binrange=[(3140, 3159)])
        Import("FUS_FUSEVLD_CKX.usrv")
        #MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        

rev = '25ww13p2_rev1'

#cdie = CDIE_816_SORT()
#cdie.initialize('./FUS_FUSEVLD', 'FUS_FUSEVLD', rev)
#cdie.get_start_flow('FUS_FUSEVLD_START')

cdie = CDIE_816_CLASS()
cdie.initialize('./FUS_FUSEVLD_CKX', 'FUS_FUSEVLD_CKX', rev)
cdie.get_begincpupkg_flow('FUS_FUSEVLD_CKX_BEGINCPUPKG')
#cdie.get_begincpumax_flow('FUS_FUSEVLD_CKX_BEGINCPUMAX')

