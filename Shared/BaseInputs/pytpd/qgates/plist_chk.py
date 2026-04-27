#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Invalid plist check between loaded on tester vs calling from .mtpl/inputfiles.
Also can detect any mismatch case in plist name.
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
import sys
import json


class PListCheck(QGateBase):

    def main(self):
        loaded_plist = set()
        mod_plist = {}
        for item in sorted(self.tpobj.plists.get_plist_list()):
            loaded_plist.add(item)
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'patlist' in params and 'PlistConfigTC' not in params['TEMPLATE']:
                file = params['patlist']
                file2 = remove_ip(file)
                if file2:
                    mod_plist[file2] = mod
                else:
                    self.add_error(225, mod, f'{item} has empty patlist')
            if 'Plist' in params and 'PlistConfigTC' not in params['TEMPLATE']:
                file = params['Plist']
                file2 = remove_ip(file)
                if file2:
                    mod_plist[file2] = mod
                else:
                    self.add_error(225, mod, f'{item} has empty Plist')

        plbmap = self.tpobj.plists.get_plb_map()
        for x in sorted(mod_plist):
            if not (x in plbmap):
                y = mod_plist[x]
                self.add_error(225, y, f'{x} is missing')
            else:
                self.add_pass(225, "BASE")

# plist_files = list of plists used by mtpl


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    PListCheck(TestProgram(sys.argv[1]).pickle_init()).run()
