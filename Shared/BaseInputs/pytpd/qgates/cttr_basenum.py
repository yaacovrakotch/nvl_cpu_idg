#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Base number compliance checks
Checks if its 5 digits
EdgeTicks should equal to 3
"""
import setenv      # must be first in the imports
import re
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json


class CttrBaseNum(QGateBase):

    def main(self):
        """
        Base number compliance checks
        Checks if its 5 digits
        EdgeTicks should equal to 3
        """
        bomflows = self.tpobj.bin_matrix(self.tpobj.get_bom())
        chk_subflows = """CSNF3 CSNF2 CSNF1
        CCRF6 CCRF4 CCRF1
        CCLRF6 CCLRF4 CCLRF1
        CATF6 CATF4 CATF1
        CGTF6 CGTF4 CGTF1
        CCRF2 CCRF3 CCRF5
        CCLRF2 CCLRF3 CCLRF5
        CATF2 CATF3 CATF5
        CGTF2 CGTF3 CGTF5
        CBSF3 CBSF1
        CBSF2
        """.split()  # chk only subflow, scoreboarding here and  guardbanding reqd tests
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if not any(test.endswith(ff) for ff in bomflows):
                # print("FF:", test)
                continue  # exclude static tests
            tm = data.get('TEMPLATE')
            if not tm == 'VminTC':
                continue  # process only vminTC templates
            sf = self.gen_subflow(test)
            # print(sf)
            # csf = cfg.chk_subflows -> CHECK SUBFLOWS
            # print(csf)
            if sf not in chk_subflows:
                continue  # process only tests inside CHK subflows

            vmn = data.get('TestMode')
            bnm = strvalue(data.get('ScoreboardBaseNumber', data.get('base_number', data.get('BaseNumbers', None))))
            etk = strvalue(data.get('ScoreboardEdgeTicks'))
            smf = strvalue(data.get('ScoreboardMaxFails'))
            kil = data.get('_EDCKIL')

            gbnm = 5
            getk = '3'
            gsmf = '20'

            # print(test, bnm, len(bnm), gbnm)

            if not vmn.endswith('Vmin'):
                continue  # ignore non-VMIN search mode tests

            if not kil == 'KIL':

                continue  # ignore EDC/Floating tests
            # if mod not in sum[self.mtl_cttrchk]:
                # self.sum[self.mtl_cttrchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            if bnm is None or len(bnm) != gbnm:
                self.add_error(200, mod, f'Base#:{bnm} in CHK test:{test} is not eq to 5 digits')
            else:
                self.add_pass(200, mod)
            if etk != getk:
                self.add_error(201, mod, f'EdgeTick:{etk} in CHK test:{test} is not eq to {getk}')
            else:
                self.add_pass(201, mod)
            # if smf != gsmf:
                # elf.add_error(202, mod, f'ScoreboardMaxFails:{smf} in CHK test:{test} is not eq to {gsmf}')
                # scoreboard max fails not equql to 20
            # else:
                # self.add_pass(202, mod)
        return

    def gen_subflow(self, test):
        """
        This function reads the testname and returns the subflow portion; 5th field
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001
        :return: sf  # returns the subflow part of the testname, ex: SCRF1
        """
        # sort&class names is ti_name3 (w/ speedflow) and ti_name4 (w/o speedflow)
        ti_name3 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$')
        ti_name4 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_\w+)?$')
        t3 = ti_name3.search(test)
        t4 = ti_name4.search(test)
        ts = re.compile(r'([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)')  # relaxed SF check
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
    CttrBaseNum(TestProgram(sys.argv[1]).pickle_init()).run()
