#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures that the mixdetect config file is not using STSORT
"""
import setenv      # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json


class MixDetCfg(QGateBase):

    def main(self):
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'PrimeMixingDetectionTestMethod' in params['TEMPLATE']:
                if 'ConfigurationFilePath' in params:
                    cfg_file = params['ConfigurationFilePath']
                    pathfile = f'{self.tpobj.tpldir}/{cfg_file}'
                    print(pathfile)
                    with open(pathfile, 'r') as cfile:
                        contents = cfile.read()
                        if 'STSORT' in contents:
                            self.add_error(221, mod, f'{mod} is using "STSORT" in DFFTokenList in {cfg_file}. '
                                                     f'Please update to use "SORT"')
                        else:
                            self.add_pass(221, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    MixDetCfg(TestProgram(sys.argv[1]).pickle_init()).run()
