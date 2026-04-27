#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checker for tests that have NO data inside it
NOTE: This check is not applicable for Prime12 since some instances are pure code (no data)
"""
import sys
import setenv

from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint


class EmptyInstance(QGateBase):

    def main(self):
        """Entry point of checker"""
        for module, tname, data, _ in self.tpobj.mtpl.iter_tests():
            s = len(data.keys() - {'TEMPLATE'})
            if s > 0:
                self.add_pass(172, module)
            else:
                self.add_error(172, module, f'{tname} is empty.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    EmptyInstance(TestProgram(sys.argv[1]).pickle_init()).run()
