#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks the Module names to ensure they follow the proper NVL Module naming convention located here:
    https://wiki.ith.intel.com/display/ITSpdxtp/NVL+Module+Naming+Convention
"""
import sys
import setenv

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename, dirname
from itertools import chain
import json
import re


class ModName(QGateBase):
    IGNORE_TESTS = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules', 'TPIE_PgmRules')

    def main(self):
        """Entry point of checker"""
        kwargs = dict(bypass=True, idict=False)
        modbrk = re.compile('^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)')
        g3 = re.compile(r'^[CHPGX][KCX]([A-Z0-9]{0,6})$')
        valid1st = """ARR CLK DRV FUN FUS MIO PPR PTH QNR SCN SIO TPI YBS""".split()
        validgrp3 = """X 40 48 816 816P 816N 816BLL NVL AX S H P S AX PKGU PKGP PKGH PKGS5 PKGS7 PKGS9 PKGSB PKGHX PKGMB PKGDT""".split()
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            if mtpl.endswith('.imp'):
                continue    # ignore
            mod = basename(dirname(mtpl))
            if mod == 'ProgramFlowsTestPlan':
                continue    # ignore this
            modchk = re.search(modbrk, mod)
            if '_' not in mod:
                self.add_error(217, mod, f'{mod} contains no other Fields (XXX_XXX_XXX).  Please fix')
                continue
            ucount = mod.split('_')
            if len(ucount) != 3:
                self.add_error(217, mod, f'{mod} should have 3 underscore separated fields no more no less')
                continue
            if modchk:
                third = re.search(g3, modchk.group(3))
            if not modchk:
                self.add_error(217, mod, f'{mod} not following correct naming convention. no lowercase or special char.')
                continue
            # if not mod.isupper():
            #    self.add_error(217, mod, f'{mod} has lower case characters. Please make it ALL CAPS')
            #    continue
            if len(modchk.group(1)) > 4:
                self.add_error(217, mod, f'The 1st field of {mod} should have a max of 4 chars only')
                continue
            if modchk.group(1) not in valid1st:
                self.add_error(217, mod, f'The 1st field of {mod} not using fixed list of valid team. '
                                         f'If new please ask TPI to add in valid list')
                continue
            if len(modchk.group(2)) > 8:
                self.add_error(217, mod, f'The 2nd field of {mod} should have a max of 8 chars only')
                continue
            if len(modchk.group(3)) > 8:
                self.add_error(217, mod, f'The 3rd field of {mod} should have a max of 8 chars only')
                continue
            if third is None:
                self.add_error(217, mod, f'The 3rd field of {mod} "_{modchk.group(3)}_" '
                                         f'not following convention. Please see wiki')
                continue
            # if third is not None:
            found = 0
            dtype = third.group(1)
            for i in validgrp3:
                if dtype == i:
                    found = 1
            if found == 0:
                self.add_error(217, mod, f'The 3rd field ("_{modchk.group(3)}_") of {mod} '
                                         f'uses these invalid characters {dtype} (from 3rd char).  '
                                         f'Please see wiki for correct values')
                continue
            self.add_pass(217, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    ModName(TestProgram(sys.argv[1]).pickle_init()).run()
