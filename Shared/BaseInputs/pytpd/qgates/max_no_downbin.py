#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensure no downbinning allowed on VMAX tests...Except for FUN_CORE MLC and AVX
Error code 330
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
import os
import re


class MaxNoDownBin(QGateBase):

    def main(self):
        bin_num_list = []
        # COVERS ARL and MTL BinMatrix/FlowMatrix files
        try1 = f'{self.tpobj.tpldir}/Shared/BaseInputs/BinMatrix.flm.usrv'
        try2 = f'{self.tpobj.tpldir}/Shared/Package_Shared/BinMatrix.flm.usrv'
        try3 = f'{self.tpobj.tpldir}/Shared/Package_Shared/FlowMatrix.flm.usrv'

        if os.path.isfile(try1):
            binning = try1
        elif os.path.isfile(try2):
            binning = try2
        else:
            binning = try3

        with open(binning, "r") as bin_find:
            for bin_parse in bin_find:
                if 'Array<String> bin = BinMatrixRule.BomGroupRule' in bin_parse:
                    binlist = bin_parse.split('[')[1].split(']')[0].split(',')
                    for i in range(len(binlist)):
                        bin_num = binlist[i].split('\"')[1]
                        bin_num_list.append(bin_num)
        ts = re.compile('([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_'
                        r'(X|V?MAX|V?MIN|V?NOM|F\d)_(X|[LHT]FM|\d+)_([A-Z0-9_]+)?')  # REGEX for the test instance names

        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'VminTC' == params['TEMPLATE']:
                if 'VMAX' in item:
                    last4 = item[-4:]
                    if last4.isdigit():
                        if not(last4 in bin_num_list):
                            continue
                        gnx = item[:-5]
                        gn = re.search(ts, gnx)
                        if not gn:
                            continue
                        genname = f'{gn.group(1)}_{gn.group(2)}_{gn.group(3)}_{gn.group(4)}_{gn.group(5)}_{gn.group(6)}_{gn.group(7)}_{gn.group(8)}_{gn.group(10)}'
                        mode = 'pass'
                        for port, bin in ports.items():
                            if port not in (0,2,3,4,5):
                                continue
                            if 'GoTo' not in bin:
                                continue
                            goto = ports[port]['GoTo']
                            nlast4 = goto[-4:]
                            if nlast4.isdigit():
                                ng = goto[:-5]
                                if re.search(ts, ng):
                                    ngn = re.search(ts, ng)
                                    ngenname = f'{ngn.group(1)}_{ngn.group(2)}_{ngn.group(3)}_{ngn.group(4)}_{ngn.group(5)}_{ngn.group(6)}_{ngn.group(7)}_{ngn.group(8)}_{ngn.group(10)}'
                                    if genname == ngenname:
                                        if 'FUN_CORE' in mod and 'MLC' in ngenname or 'AVX' in ngenname:
                                            # Exception for FUN_CORE MLC and AVX
                                            mode = 'pass'
                                        else:
                                            self.add_error(330, mod, f'VMAX test {item} port{port} is '
                                                                 f'downbinning to {goto}.'
                                                                 f'  VMAX Downbins are not allowed')
                                            mode = 'fail'
                        if mode == 'pass':
                            self.add_pass(330, mod)
                    else:
                        self.add_pass(330, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    MaxNoDownBin(TestProgram(sys.argv[1]).pickle_init()).run()
