#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This Qgate is based on post-processing script to clean up format of PROD and ENG EVN files.
Post-processing output Environment file ending line check.
Require only one value of parameter per line.
Each parameter entry in the env file should either end with ;" + (if it's not the end of the param)
or "; (if it's the last entry of the param).
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
import sys


class EnvEndLineCheck(QGateBase):
    def main(self):
        envpath = self.tpobj.envdir
        # Input envfile's path
        envfile = envpath + '/EnvironmentFile.env'
        env_perline = dict()
        key = None
        value = None
        # Parsing ENV file in to a dictionary.
        with open(envfile, "r") as openfile:
            for lno, line in enumerate(openfile):
                line = line.strip()
                # remove empty line
                if not line:
                    continue
                # remove comment out line
                if line.startswith('#'):
                    continue
                if '+' in line:
                    # Check line split with ;" + between values.
                    if line.endswith(';" +'):
                        self.add_pass(233, "BASE")
                    else:
                        message1 = f'{line} in ENV file line {lno + 1} should spilt with ;" + between values.'
                        self.add_error(233, "ENV", message1)
                else:
                    # Check line ends with ";.
                    if line.endswith('";'):
                        self.add_pass(234, "BASE")
                    else:
                        message2 = f'{line} in ENV file line {lno + 1} should end with ";'
                        self.add_error(234, "ENV", message2)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    EnvEndLineCheck(TestProgram(sys.argv[1]).pickle_init()).run()
