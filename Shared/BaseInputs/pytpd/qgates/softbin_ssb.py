#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures softbin number: 90HBHBSB, That the first HB match the 2nd HB

Applicable for products that use Super-Short-Binning:
https://wiki.ith.intel.com/display/IntelTPWiki/Sort+8+digit+Binning

QE ticket:
https://hsdes.intel.com/appstore/article/#/15013794580
"""
import sys
try:
    import setenv
except ImportError:    # pragma: no cover
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from gadget.tputil import OtplFile, get_modulename
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import json
import re


class SoftBinSSB(QGateBase):

    def main(self):
        """
        Checks the softbin number: 90HBHBSB, That the first HB match the 2nd HB

        Impact - by Weng Keen Wong
        1.	Mapping wrong binning will lead to different debug direction
        2.	Direct binning issue to wrong ownership
        3.	No follow binning standard https://wiki.ith.intel.com/display/IDCTPWIKI/MTL+Binning+Strategy+-+MTL
        4.	Mislead during TP correlation/Kappa analysis

        https://wiki.ith.intel.com/display/IntelTPWiki/Sort+8+digit+Binning
        """
        if self.tpobj.is_tos4:
            self.main_nvl()
        else:
            self.main_arl()

    def main_nvl(self):
        """ NVL:90HBxxxx """

        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            self.check_nvl(mtpl)

    def check_nvl(self, mtpl):
        """Check one .mtpl file"""
        module = get_modulename(mtpl)
        if not module:
            module = 'BASE'
        robj = re.compile(r'SetBin b(\d{8})(\w+)')
        for lno, line in OtplFile(mtpl).readline():
            res = robj.search(line)
            if res:
                softbin = res.group(1)
                if not (softbin.startswith('1') or softbin.startswith('90')):
                    self.add_error(219, module,
                                   f'{softbin} does not follow SSB convention: 90HBxxxx. b{softbin}{res.group(2)}')
                    continue
                else:
                    self.add_pass(219, module)

    def main_arl(self):
        """ ARL: 90HBHBxx """
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            self.check_arl(mtpl)

    def check_arl(self, mtpl):
        """Check one .mtpl file"""
        module = get_modulename(mtpl)
        if not module:
            module = 'BASE'
        robj = re.compile(r'SoftBins\.b(\d{8})(\w+)')
        found = set()     # Show uniq errors only
        for lno, line in OtplFile(mtpl).readline():
            res = robj.search(line)
            if res:
                softbin = res.group(1)
                first = softbin[2:4]
                second = softbin[4:6]
                if not (softbin.startswith('1') or softbin.startswith('90')):
                    self.add_error(219, module,
                                   f'{softbin} does not follow SSB convention: 90HBHBxx. b{softbin}{res.group(2)}')
                    continue
                if softbin.startswith('90'):
                    if first == second:
                        self.add_pass(219, module)
                    else:
                        msg = f'{softbin} does not follow SSB convention: 90HBHBxx. b{softbin}{res.group(2)}'
                        if msg not in found:
                            self.add_error(219, module, msg)
                            found.add(msg)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    SoftBinSSB(TestProgram(sys.argv[1])).run()
