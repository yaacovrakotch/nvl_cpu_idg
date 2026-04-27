#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks for PUP Speed Flow Naming requirements.
Ensures Frequency Corner (F1, F2...Fn) is reflected correctly in the Subflow Name used in the test instance
Ensures Speedflow test follows speed flow naming convention
Ensures the Frequency used in the Frequency field is using digits
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


class CttrPup(QGateBase):

    def main(self):
        """
        Checks for PUP Speed Flow Naming requirements.
        Ensures Frequency Corner (F1, F2...Fn) is reflected correctly in the Subflow Name used in the test instance
        Ensures Speedflow test follows speed flow naming convention
        Ensures the Frequency used in the Frequency field is using digits
        """
        sccttrflows = """SSHDCF1 SSNF1 SSNF2 SSNF3 CSNF3 CSNF2 CSNF1
        SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6 CCRF6 CCRF4 CCRF1
        SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6 CCLRF6 CCLRF4 CCLRF1
        SATF1 SATF2 SATF3 SATF4 SATF5 SATF6 CATF6 CATF4 CATF1
        CCRF2 CCRF3 CCRF5
        CCLRF2 CCLRF3 CCLRF5
        CATF2 CATF3 CATF5
        SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6 CGTF6 CGTF4 CGTF1
        SBSF1 SBSF2 SBSF3 PSTBSSRH CBSF3 CBSF1
        CGTF2 CGTF3 CGTF5
        CBSF2
        """.split()

        ti_name3 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$')

        bomflows = self.tpobj.bin_matrix(self.tpobj.get_bom())
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            spd = 0  # default set to static test
            if any(test.endswith(ff) for ff in bomflows):
                spd = 1
            if not spd:
                continue

            t3 = ti_name3.search(test)
            if not t3:
                self.add_error(176, mod, f'Test:{test} does not follow speedflow naming')
                continue
            else:
                self.add_pass(176, mod)

            sf = t3.group(5)  # subflow
            fc = t3.group(8)  # freq # corner
            ff = t3.group(9)  # freq value

            if sf not in sccttrflows:
                continue  # skip tests that are not in the srh/chk subflows
            if sf.endswith(fc) and ff.isdigit() and sf in sccttrflows:
                continue  # skip tests that are coded correctly

            # test runs thru here if it fails above
            if not sf.endswith(fc):
                self.add_error(177, mod, f'Test:{test} sf={sf} and fc={fc} do not match')
            else:
                self.add_pass(177, mod)
            if not ff.isdigit():
                self.add_error(178, mod, f'Test:{test} Frequency={ff} should all be digits')
            else:
                self.add_pass(178, mod)

        return

    def gen_subflow(self, test):
        """
        This function reads the testname and returns the subflow portion; 5th field
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001
        :return: sf  # returns the subflow part of the testname, ex: SCRF1
        """
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
    CttrPup(TestProgram(sys.argv[1]).pickle_init()).run()
