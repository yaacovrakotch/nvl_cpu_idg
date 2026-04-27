#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
        CTTR Basenumber per die check
        203: CDIE test not using the correct designated starting  base number
        204: GDIE test not using the correct designated starting  base number
        205: SOC test not using the correct designated starting  base number
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


class CttrPupComp(QGateBase):

    def main(self):
        """
        CTTR Basenumber per die check
        203: CDIE test not using the correct designated starting  base number
        204: GDIE test not using the correct designated starting  base number
        205: SOC test not using the correct designated starting  base number
        """
        socchk_subflows = """CSNF3 CSNF2 CSNF1""".split()  # soc CHK subflows
        gdiechk_subflows = """CGTF6 CGTF4 CGTF1 CGTF2 CGTF3 CGTF5""".split()  # gdie CHK subflows
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
        cdiechk_subflows = """CCRF6 CCRF4 CCRF1 CCLRF6 CCLRF4 CCLRF1
        CATF6 CATF4 CATF1 CCRF2 CCRF3 CCRF5
        CCLRF2 CCLRF3 CCLRF5 CATF2 CATF3 CATF5""".split()  # cdie CHK subflows
        cdiebnmstart = '1'
        gdiebnmstart = '2'
        ioebnmstart = '3'
        socbnmstart = '4'
        admbnmstart = '5'

        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            bnm = data.get('ScoreboardBaseNumber', data.get('base_number', data.get('BaseNumbers', None)))
            gbnm = 5
            sf = self.gen_subflow(test)
            if sf not in chk_subflows:
                continue  # process only tests inside CHK subflows
            if not bnm:
                continue
            if len(bnm) != gbnm:
                continue  # process only tests with 5digit base#

            if sf in cdiechk_subflows:
                if bnm.startswith(cdiebnmstart):
                    self.add_pass(203, mod)
                    continue
                else:
                    self.add_error(203, mod, f'Base#:{bnm} in CDIE CHK test:{test} should start with number:{cdiebnmstart}')

            elif sf in gdiechk_subflows:
                if bnm.startswith(gdiebnmstart):
                    self.add_pass(204, mod)
                    continue
                else:
                    self.add_error(204, mod, f'Base#:{bnm} in GDIE CHK test:{test} should start with number:{gdiebnmstart}')
            elif sf in socchk_subflows:
                if bnm.startswith(socbnmstart):
                    self.add_pass(205, mod)
                    continue
                else:
                    self.add_error(205, mod, f'Base#:{bnm} in SOC CHK test:{test} should start with number:{socbnmstart}')
            # TODO: Add additional scenarios

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
    CttrPupComp(TestProgram(sys.argv[1]).pickle_init()).run()
