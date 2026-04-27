#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks for the tname char length, max is 100 chars
DRV_RESET_SXS::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU --> PKG_ must be less than 100char length
IP_CPU::DRV_RESET_CXX::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU --> IP_ must be less than 100char length
"""
import setenv      # must be first in the imports
import re
from os.path import dirname, basename, exists
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


class TestNameLength(QGateBase):

    def main(self, limit=100):
        """
        Checks for the tname char length, max is 100 chars
        DRV_RESET_SXS::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU --> PKG_ must be less than 100char length
        IP_CPU::DRV_RESET_CXX::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU --> IP_ must be less than 100char length
        """
        # BUG: before : if mod not in self.sum_fc:
        ipcpu = set()  # set of ipcpu modules in all stpls
        ippch = set()  # set of ippch modules in all stpls
        ipcpu.update({basename(dirname(x)) for x in self.tpobj.get_all_mtpl_from_stpl('IP_CPU')})  # ipcpu modules
        ippch.update({basename(dirname(x)) for x in self.tpobj.get_all_mtpl_from_stpl('IP_PCH')})  # ippch modules
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if mod in ipcpu:  # IP_CPU test
                nname = 'IP_CPU::%s::%s' % (mod, test)
            elif mod in ippch:  # IP_PCH test
                nname = 'IP_PCH::%s::%s' % (mod, test)
            else:  # PKG test
                nname = '%s::%s' % (mod, test)

            ttl = len(nname)

            if ttl > limit:
                self.add_error(132, mod, f'Test: {nname} length:{ttl} is over the allowed limit:{limit} characters')
            else:
                self.add_pass(132, mod)
        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TestNameLength(TestProgram(sys.argv[1]).pickle_init()).run()
