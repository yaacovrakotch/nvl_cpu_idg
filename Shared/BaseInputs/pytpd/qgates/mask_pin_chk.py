#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Tests missing ports

TODO: failing: /nfs/site/home/jqdelosr/pytpd_rel/unittests/torch_p6828_multibom/MTLXXXXXXX19M0ZSXXX_P68_2
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


class MaskTDOChk(QGateBase):

    def main(self):
        tpl_dir = self.tpobj.tpldir
        all_tdo = ['XXJTAG_TDO', 'XXGPP_H_9_UART0_TXD', 'XXGPP_A_14_ESPI_CS2_B']
        pindef = f'{tpl_dir}/Shared/BaseInputs/PinDefinitions.pin'
        group = 0
        block = 0
        pingroup = {}
        with open(pindef, "r") as pindeflines:
            for pindefparse in pindeflines:
                if ('Group ' in pindefparse):
                    pinstrip = pindefparse.strip()
                    if (pinstrip.split(' ')[1]).islower():
                        pgroup = pinstrip.split(' ')[1]
                        group = 1
                if group == 1 and '{' in pindefparse:
                    block = 1
                if group == 1 and not('{' in pindefparse) and block == 1 and not('}' in pindefparse):
                    pinstrip = pindefparse.strip()
                    if ',' in pinstrip:
                        pinstripx = pinstrip.split(',')[0]
                        pingroup.setdefault(pgroup, []).append(pinstripx)
                    else:
                        pingroup.setdefault(pgroup, []).append(pinstrip)
                if group == 1 and ('}' in pindefparse):
                    group = 0
                    block = 0
        # pprint(pingroup)
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'mask_pins' in params:
                mask = 'mask_pins'
                self.pincompare(all_tdo, mask, params, pingroup, mod, item)
            elif 'MaskPins' in params:
                mask = 'MaskPins'
                self.pincompare(all_tdo, mask, params, pingroup, mod, item)
            else:
                self.add_pass(230, mod)

    def pincompare(self, all_tdo, mask, params, pingroup, mod, item):
        for pin in all_tdo:
            if pin in params[mask]:
                self.add_error(230, mod, f'{item} is masking a TDO pin ({pin}), please mask this pin in the PLIST')
                pass
            else:
                pinlist = params[mask]
                maskpins1 = pinlist.split(',')
                maskedpin = []
                for indvx in maskpins1:
                    indv = indvx.strip()
                    if 'IP_' in indv:
                        # indv = indvx.strip()
                        maskpins = remove_ip(indv)
                        maskedpin.append(maskpins)
                    else:
                        maskpins = indv
                        maskedpin.append(maskpins)
                for v in range(len(maskedpin)):
                    if maskedpin[v].islower():
                        if maskedpin[v] in pingroup.keys():
                            pgm = pingroup[maskedpin[v]]
                            for w in range(len(pgm)):
                                if pin in pgm[w]:
                                    if 'TPI_SHOPS' in mod:
                                        self.add_pass(230, mod)

                                    else:
                                        self.add_error(230, mod, f'{item} is masking a TDO pin ({pin}) '
                                                                 f'from ({maskedpin[v]}) pingroup, please mask this pin in the PLIST')
                            else:
                                self.add_pass(230, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    MaskTDOChk(TestProgram(sys.argv[1]).pickle_init()).run()
