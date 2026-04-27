#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Template for qgate routine. This works for common or module qgate

Steps to update:
1. Rename (two occurrence) CheckerNameHere to your checker name, CamelCaseNamingConvention
2. Update the code in main() on what your checker algo is
3. Add self.add_error() for error, and there should be corresponding self.add_pass() for passing case
4. Error code should be unique. Goto wiki to get latest number. Update wiki when checker is coded:
   http://goto.intel.com/qgate-checks
5. Update unittest (test/test_template_common.py)
6. Run this script given an exported testprogram to validate, example:
   qgates/template_common.py POR_TP/Class_MTL_P68/EnvironmentFile.env
7. Register this qgate in TP's qgate_config.json file (submit PR).
   For Module qgate, specify path to the py relative to base .tpl folder.
8. Commit this py and submit PR (pytpd repo for common)

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
import json


class CheckerNameHere(QGateBase):

    def main(self):
        """Entry point of checker"""
        all_instances = self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True)
        for module, testname, params, ports in all_instances:
            # put your checker code here. Replace below code!

            # for this template example, error out if testname has 'NONRECOVERY'
            self.check(not ('NONRECOVERY' in testname), 150, module, f'{testname} has NONRECOVERY in name.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    CheckerNameHere(TestProgram(sys.argv[1]).pickle_init()).run()
