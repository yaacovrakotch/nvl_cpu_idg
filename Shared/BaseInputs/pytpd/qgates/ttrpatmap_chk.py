#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
TTR Patmap check
170: PatternName index will result to getting the Letter as well of the TID instead of just the numbers
171: FeatureSwitchSettings not existing
181: Uses per pattern printing and base number at the same time
182: Catch ALL errors
"""
import setenv      # must be first in the imports
import re
import glob
from os.path import dirname, basename, exists
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip, get_param, CheckerLog
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from itertools import chain
import sys
import json


class TtrPatMap(QGateBase):

    def main(self):
        """
        Checks the the pattern_name_map param has valid range of pattern substr, NUMBERS from pattern only, NO LETTERS
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'pattern_name_map': '1,2,3,4,5,6,7'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'pattern_name_map': '9,10,11,12,13,14,15'}, '')]
        :return:
        """
        op1 = '1,2,3,4,5,6,7'
        op2 = '9,10,11,12,13,14,15'
        srhflows = """SSHDCF1 SSNF1 SSNF2 SSNF3
        SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6
        SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6
        SATF1 SATF2 SATF3 SATF4 SATF5 SATF6
        SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6
        SBSF1 SBSF2 SBSF3
        """.split()  # srh only subflow, no scoreboarding here
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            pnm_list = []
            bnm_list = []
            pnm = data.get('PatternNameCounterIndexes', data.get('PatternNameMap', data.get('pattern_name_map', None)))
            bnm = data.get('ScoreboardBaseNumber', data.get('base_number', data.get('BaseNumbers', None)))
            sf = self.gen_subflow(test)
            fss = data.get('FeatureSwitchSettings')  # has the per_pattern_printing option

            if sf in srhflows:
                if pnm or bnm:
                    # SET AS WARNING IN SHERLOCK
                    # self.add_error(169, mod, f'Test:{test} in SRH flow:{sf}, scoreboard NOT reqd')
                    continue
            if not pnm:
                continue
            pnm = pnm.replace(' ', '')
            if not('|' in pnm):
                # everything else that comes here is not on a SRH subflow and can have base# and pattern_name_map
                if pnm == op1 or pnm == op2:  # pass, best use cases
                    self.add_pass(170, mod)
                    self.add_pass(171, mod)
                    self.add_pass(181, mod)
                    self.add_pass(182, mod)
                    continue
                elif pnm.startswith('0') or pnm.startswith('8'):  # fail, letters in ctr will double count
                    self.add_error(170, mod, f'Test:{test} uses letters for pattern_name_map={pnm}!')

                elif fss:
                    if pnm and not bnm and 'per_pattern_printing' in fss:  # analog use case pass no bnm
                        self.add_pass(181, mod)
                        continue
                    elif pnm and bnm and 'per_pattern_printing' in fss:  # analog use case fail with bnm
                        self.add_error(181, mod, f'Test:{test} uses per_pattern_printing and base# at the '
                                                 f'same time! patmap={pnm} base#={bnm}')
                    else:  # uses fss but without perpattern printing
                        self.add_error(182, mod, f'Test:{test} has user_defined pattern_name_map={pnm}!')
                else:  # !fss & catch all
                    self.add_error(171, mod, f'Test:{test} has no FeatureSwitchSettings defined!')
            else:
                pnm_list = pnm.split('|')
                if not(',' in bnm):
                    self.add_error(182, mod, f'Test:{test} has mismatched number of values for patternmap ({len(pnm_list)}) and basenumber (1)')
                    continue
                bnm_list = bnm.split(',')
                if not(len(pnm_list) == len(bnm_list)):
                    self.add_error(182, mod, f'Test:{test} has mismatched number of values for patternmap ({len(pnm_list)}) and basenumber ({len(bnm_list)})')
                    continue
                status_op = []
                status_fss = 'PASS'
                status181 = []
                status182 = []
                for i in range(len(pnm_list)):
                    pnml = pnm_list[i]
                    bnml = bnm_list[i]

                    if pnml == op1 or pnml == op2:  # pass, best use cases
                        status_op.append('PASS')
                        # continue
                    else:
                        status_op.append('FAIL')
                        if pnml.startswith('0') or pnml.startswith('8'):  # fail, letters in ctr will double count
                            self.add_error(170, mod, f'Test:{test} uses letters for pattern_name_map on value#{i + 1} '
                                                     f'of pattern_name_map={pnm}!')
                            status_op.append('FL')
                        else:
                            self.add_error(182, mod, f'Test:{test} has a user_defined value on value# {i + 1} of '
                                                     f'pattern_name_map={pnm}!')
                            status_op.append('FL')
                    if fss:
                        if pnml and not bnml and 'per_pattern_printing' in fss:  # analog use case pass no bnm
                            status181.append('PASS')
                        elif pnml and bnml and 'per_pattern_printing' in fss:  # analog use case fail with bnm
                            status181.append('FAIL')
                        else:  # uses fss but without perpattern printing
                            status182.append('FAIL')
                    else:  # !fss & catch all
                        status_fss = 'FAIL'

                if not('FAIL' in status_op):
                    self.add_pass(170, mod)
                    self.add_pass(171, mod)
                    self.add_pass(181, mod)
                    self.add_pass(182, mod)

                if status_fss == 'FAIL':
                    self.add_error(171, mod, f'Test:{test} has no FeatureSwitchSettings defined!')
                if 'FAIL' in status181:
                    self.add_error(181, mod, f'Test:{test} uses per_pattern_printing and base# at the same time! '
                                             f'patmap={pnm} base#={bnm}')
                if 'FAIL' in status182 and not('FL' in status_op or 'PASS' in status_op):
                    self.add_error(182, mod, f'VIC: Test:{test} has user_defined pattern_name_map={pnm}!')

                # TODO: check that bnm+pnm < 13 digits
                # TODO: add the execution mode filter for refactor later
                # TODO: add test case when pnm has space eg 9,10,11,12,1 3,14,15 --> '1 3' should be '13'

        return

    def gen_subflow(self, test):
        """
        This function reads the testname and returns the subflow portion; 5th field
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001
        :return: sf  # returns the subflow part of the testname, ex: SCRF1
        """
        ti_name3 = re.compile(r"^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$")
        ti_name4 = re.compile(r"^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_\w+)?$")

        t3 = ti_name3.search(test)
        t4 = ti_name4.search(test)
        ts = re.compile(r"([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)")  # relaxed SF check
        if t3:
            sf = t3.group(5)
        elif t4:
            sf = t4.group(5)
        else:  # relaxed regex to discount tests that have correct subflow but wrong ti_name convention
            f = ts.search(test)
            if f:
                sf = f.group(5)
            else:
                sf = 'NYET'
        return sf


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TtrPatMap(TestProgram(sys.argv[1]).pickle_init()).run()
