#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks the Module and test names should be ALL CAPS
"""
import sys
import setenv

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from itertools import chain
import json


class UpperCase_Mod(QGateBase):
    IGNORE_TESTS = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules', 'TPIE_PgmRules')

    def main(self):
        """Entry point of checker"""
        kwargs = dict(bypass=True, idict=False)
        main_flow = self.tpobj.mtpl.iter_flows('MAIN', **kwargs)
        init_flow = self.tpobj.mtpl.iter_flows('INIT', **kwargs)
        lotend_flow = self.tpobj.mtpl.iter_flows('LOTENDFLOW', **kwargs)
        lotstart_flow = self.tpobj.mtpl.iter_flows('LOTSTARTFLOW', **kwargs)
        testplanstart = self.tpobj.mtpl.iter_flows('TESTPLANSTARTFLOW', **kwargs)
        testplanend = self.tpobj.mtpl.iter_flows('TESTPLANENDFLOW', **kwargs)
        for mod, inst in chain(main_flow, init_flow, lotend_flow, lotstart_flow, testplanend, testplanstart):
            if not inst.startswith(self.IGNORE_TESTS):
                if mod.isupper():
                    self.add_pass(112, mod)
                else:
                    self.add_error(112, mod, f'Upper Case check failed for Module: {mod}')

                if inst.isupper():
                    self.add_pass(112, mod)
                else:
                    self.add_error(112, inst, f'Upper Case check failed for Test: {mod}::{inst}')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    UpperCase_Mod(TestProgram(sys.argv[1]).pickle_init()).run()
