#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks if there are .plist file that reside in more than 1 PLIST.xml file
PLIST_ALL, PLIST_IP_CPU or PLIST_IP_PCH

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
from os.path import basename


class DupPlistXml(QGateBase):

    def main(self):
        """Entry point of checker"""
        tpobj = self.tpobj
        list_plist = tpobj.get_file_allplist_real()    # contains the PLIST_ALL file names
        found = {}
        for ff in list_plist:
            xmldata = xmlfunc.xml2dict(ff)    # Stores the contents of each PLIST_ALL file into a dictionary
            for plist in find_dot_items(xmldata, 'HdmtReferenceFile.PList.PListFile'):
                if plist not in found:
                    found[plist] = basename(ff)
                    self.add_pass(207, 'BASE')
                else:
                    self.add_error(207,
                                   'BASE',
                                   f"DUPLICATE: {plist}: {basename(ff)} and {found[plist]}")


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    DupPlistXml(TestProgram(sys.argv[1]).pickle_init()).run()
