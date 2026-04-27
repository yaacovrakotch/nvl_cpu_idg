# Import the necessary classes from Pymtpl
import copy
import re, json

from pymtpl.por_methods import FleGeneratePerDieFuseString, FleGeneratePerDieFuseStringByDies, FleGetDieStatusByDies
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


class FleGeneratePerDieFuseString_TestBuilder(TestConfig):
    def __init__(self, name, module_name, isEDC=False,test_instance_postfix=None, **kwargs):
        TestConfig.__init__(self, is_edc=isEDC)
        param = {
            'name': f'FUSE_X_FLE_{self.is_edc_char}_{module_name.upper()}_X_X_X_X_{name.upper()}',
            'ByPassPort': f'-1',
            'DataLog': f'On', 
            'Register': f'CPU0',
        }

        if test_instance_postfix:
            param['name'] = param['name'] + '_' + test_instance_postfix
        param.update(kwargs)
        self.test = FleGeneratePerDieFuseString(**param)

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


    def get_start_flow(self, flow_name, module_name='FACTFUSBUILDCPUNOM', is_edc=False,  bin_offset=0, bin_offset2=0, composite_postfix=None, test_instance_postfix=None):
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
        t['hvm_fsg_check'] = FleGeneratePerDieFuseStringByDies_TestBuilder(name='hvm_fsg_check', BypassPort=1, **dparams)
        t['hvm_fsg'] = FleGeneratePerDieFuseString_TestBuilder(name='hvm_fsg', Register='CPU0', **dparams)
        t['hvm_fsg_cpu1'] = FleGeneratePerDieFuseString_TestBuilder(name='hvm_fsg_cpu1', Register='CPU1', BypassPort=Spec('__shared__::TpRule.If_MICP(-1,1)'), **dparams)
        t['get_fuse_string_status'] = FleGetDieStatusByDies_TestBuilder(name='get_fuse_string_status', FuseStateUservar='Which_Socket.FuseState', **dparams)
        
       
        ##Flow Setup
        
        
        factfusbuildcpunom_fitems = []
        factfusbuildcpunom_fitems.append(t['hvm_fsg_check'].get_fitem(r0=pFail(setbin=self.bin(315000, offset), ret=0),r2=pFail(setbin=self.bin(315000, offset), ret=0)))
        factfusbuildcpunom_fitems.append(t['hvm_fsg'].get_fitem(r0=pFail(setbin=self.bin(315001, offset), ret=0),r2=pFail(setbin=self.bin(315002, offset), ret=0)))
        factfusbuildcpunom_fitems.append(t['hvm_fsg_cpu1'].get_fitem(r0=pFail(setbin=self.bin(315003, offset), ret=0), r2=pFail(setbin=self.bin(315004, offset),ret=0)))
        factfusbuildcpunom_fitems.append(t['get_fuse_string_status'].get_fitem(r0=pFail(setbin=self.bin(315604, offset), ret=0),
                                                                               r1=pPass(ret=1),
                                                                               r2=pFail(setbin=self.bin(315605, offset), ret=0),
                                                                               r3=pPass(ret=1),
                                                                               r4=pFail(setbin=self.bin(315606, offset), ret=0),
                                                                               r5=pFail(setbin=self.bin(315607, offset), ret=0)
                                                                              ))
        Flow(flow_name,*factfusbuildcpunom_fitems)

    

class CDIE_816_SORT(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='sort')
        self.LevelsTc = 'BASE::SBF_nom_lvl'
        self.TimingsTc = 'BASE::cpu_ctf_timing_tclk100_hclk100_bclk400'
        self.PrePlist = None

    def initialize(self, name1, name2):
        InitializeNVLSort(name1, name2, defaultrm1bin=-31, defaultrm2bin=-31, binrange=[(3100, 3199)])
        #MtplComment("This is a NVL {} mtpl rev {}".format(' '.join(name1.split('_')), rev))
        # Add the necessary files to import in your mtpl
        #Import("FUS_FUSEREAD.usrv")

class CDIE_816_CLASS(CDIE_BASE):
    def __init__(self):
        CDIE_BASE.__init__(self, sort_class='class')
        self.LevelsTc = 'CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom'
        self.TimingsTc = 'CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100'
        self.PrePlist = ''

    def initialize(self, name1, name2):

        InitializeNVLClass(name1, name2, defaultrm1bin=(98312000,98313999), defaultrm2bin=(99312000,99313999), binrange=[(3150, 3159)])


cdie = CDIE_816_CLASS()
cdie.initialize('./FUS_FSG_CXX', 'FUS_FSG_CXX')
cdie.get_start_flow('FUS_FSG_CXX_FACTFUSBUILDCPUNOM')