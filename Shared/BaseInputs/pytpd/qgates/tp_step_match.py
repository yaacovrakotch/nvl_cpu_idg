#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks if the stepping in the TP name (8th field) matches the stepping in SCVars.SC_STEP
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
import sys


class TPStepMatch(QGateBase):
    def main(self):
        altname = self.tpobj.usrv.get_var('RunTimeLibraryVars.iCGL_TpAltName', default='9999999999')
        scstep = self.tpobj.usrv.get_var('SCVars.SC_STEP', default='8')
        if scstep == altname[7]:
            self.add_pass(240, "BASE")
        else:
            self.add_error(240, "BASE", f'Stepping in RunTimeLibraryVars.iCGL_TpAltName: {altname} '
                                        f'(8th field: "{altname[7]}" ) not matching SCVars.SC_STEP: "{scstep}"')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TPStepMatch(TestProgram(sys.argv[1]).pickle_init()).run()
