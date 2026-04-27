#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures that TESTPLANEND will not set or overwrite any bins, most especially Bin99
"""
import os

import setenv      # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from tp.testprogram import Env
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json
from itertools import chain
from gadget.errors import confirm


class TestPlaneEndCheck(QGateBase):

    def main(self):
        path2 = self.tpobj.envdir
        tpcfg_strip = None
        path2_dirlist = os.listdir(path2)
        for i in range(len(path2_dirlist)):
            if '.tpconfig' in path2_dirlist[i]:
                tpcfg = f'{path2}/{path2_dirlist[i]}'
                print(tpcfg)
                with open(tpcfg, "r") as tpcfg_line:
                    for tpcfg_parse in tpcfg_line:
                        if 'Seeds DirectoryName' in tpcfg_parse:
                            tpcfg_strip = tpcfg_parse.strip().split('"')[1]

        confirm(tpcfg_parse, "Seeds DirectoryName missing in tpconfig file", f'Check the {tpcfg} file')
        seed_dir = os.listdir(Env.xpath(tpcfg_strip))
        found = 0
        binlist = []
        for i in range(len(seed_dir)):
            if 'MPS_ProductConfig.xml' == seed_dir[i]:
                prodcfg = Env.xpath(f'{tpcfg_strip}/{seed_dir[i]}')
                with open(prodcfg, "r") as prodcfg_line:
                    for prodcfg_parse in prodcfg_line:
                        if '<RetestBins>' in prodcfg_parse:
                            found = 1
                        if '</RetestBins>' in prodcfg_parse:
                            found = 0
                        if found == 1 and '<BinGroup>' in prodcfg_parse:
                            binning = prodcfg_parse.strip().split('<BinGroup>')[1].split('</BinGroup>')[0]
                            if '-' in binning:
                                sb = binning.split('-')
                                sb_range = int(sb[1]) + 1
                                for i in range(int(sb[0]), sb_range):
                                    j = str(i)
                                    if j in binlist:
                                        pass
                                    else:
                                        binlist.append(j)
                            else:
                                if binning in binlist:
                                    pass
                                else:
                                    binlist.append(binning)

        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('TESTPLANENDFLOW', bypass=True, edict=True, pdict=True):
            for port, values in ports.items():
                if port == -1 or port == -2 or port == 999:
                    continue
                else:
                    if (ports[port]['PassFail']) == 'Fail' and 'SetBin' in values:
                        softbin = ports[port]['SetBin'].split('.')[1].split('_')[0][-4:]
                        if softbin in binlist:
                            self.add_error(220, mod, f'Softbin {softbin} found in RCSlist, please remove. '
                                                     f'TestName: {mod}/{item}, port: {port}')
                    else:
                        self.add_pass(220, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TestPlaneEndCheck(TestProgram(sys.argv[1]).pickle_init()).run()
