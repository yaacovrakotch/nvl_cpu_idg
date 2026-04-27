#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This Qgate is checking the TP patch rev cannot go beyond 7.
Due to the Fuse File bits only allocate 3 bits for the TP Patch.
The patch rev can only go from 000 (0) to 111 (7)which cannot beyond p7.
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
import sys


class TPPatchRevCheck(QGateBase):
    def main(self):
        tpname = self.tpobj.usrv.get_var('TPNameVars.TPName1', default='CLASSHOT')
        patch_rev = int(tpname[13])
        if len(tpname) == 19:
            if 0 <= int(tpname[13]) <= 7:
                self.add_pass(235, "BASE")
            else:

                message1 = f'Current Test Program patch rev is {patch_rev} which CAN NOT beyond 7.'
                self.add_error(235, "BASE", message1)
        else:
            message2 = f'Current Test Program name {tpname} does NOT follow 19 characters standard naming convention.'
            self.add_error(235, "BASE", message2)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TPPatchRevCheck(TestProgram(sys.argv[1]).pickle_init()).run()
