#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
TPI_END has to be the last module in the INIT flow since Prime Init verify in TPI_END module.
It has dependency to Digital modules that already own modular recovery pinmap files,
Prime init Verify must run after these modules in INIT.
"""
import setenv      # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from collections import OrderedDict
import sys
import json


class InitLastModuleCheck(QGateBase):

    def main(self):
        mod_list = OrderedDict()
        init_flow = self.tpobj.mtpl.iter_flows('INIT', bypass=True, edict=True, pdict=True)
        for mod, item, params, ports in init_flow:
            mod_list[mod] = True
        # The checker assumes TP always has at least a module in Init flow.
        last_mod = list(mod_list)[-1]
        if 'TPI_END' in last_mod:
            self.add_pass(229, "BASE")
        else:
            self.add_error(229, last_mod, f'{last_mod} can not be at last of INIT flow, TPI_END need to be at the end.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    InitLastModuleCheck(TestProgram(sys.argv[1]).pickle_init()).run()
