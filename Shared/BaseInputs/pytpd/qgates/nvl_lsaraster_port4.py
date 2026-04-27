#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
QGate for validating PrimeLSARasterTestMethod template requirements.

This script enforces the following rule for test program flows:
- Any test flow using the 'PrimeLSARasterTestMethod' template must define port 4.
- If port 4 is missing, an error is reported for that module and item.
- If port 4 is present, a pass is recorded.

"""
import setenv      # must be first in the imports
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
import sys
import re


class Binning(QGateBase):

    def main(self):
        bin_dict = {}
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'PrimeLSARasterTestMethod' in params['TEMPLATE']:
                if 4 not in ports.keys():
                    self.add_error(269, mod, f'PrimeLSARasterTestMethod test:{item} does not have a required port 4')
                else:
                    self.add_pass(269, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    Binning(TestProgram(sys.argv[1]).pickle_init()).run()
