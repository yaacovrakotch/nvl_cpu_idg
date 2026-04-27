#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures basenumbers are unique (for TTR)
"""
import setenv      # must be first in the imports
import re
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from mod.setting import cfg
import sys
import json


class BaseNumUniq(QGateBase):

    def main(self):
        """
        CTTR Checker for Mario's team
        wave2: Check for base number uniqueness
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :return:
        """
        bnmctrl = {}
        errors = []
        bomflows = self.tpobj.bin_matrix(self.tpobj.get_bom())
        # print(bomflows)
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            tm = data.get('TEMPLATE')
            if any(test.endswith(ff) for ff in bomflows):
                t3 = cfg['ti_name3'].search(test)  # rename the test with generic $FREQ and $FLOWINDEX
                if t3:
                    test = '%s_%s_%s_%s_%s_%s_%s_%s_$FREQ%s_$FLOWINDEX' % (t3.group(1), t3.group(2), t3.group(3),
                                                                           t3.group(4), t3.group(5), t3.group(6),
                                                                           t3.group(7), t3.group(8), t3.group(10))

            # if mod not in self.sum[self.mtl_cttrchk]:
            #     self.sum[self.mtl_cttrchk][mod] = {'e': 0, 'w': 0, 'p': 0}

            # bnm = strvalue(data.get('ScoreboardBaseNumber', data.get('base_number', None)))
            bnm = strvalue(data.get('ScoreboardBaseNumber', data.get('base_number', data.get('BaseNumbers', None))))
            # if not bnm == None:
            #     print('VIC:', mod, test, bnm)
            #     print(tm, bnm)
            if tm == 'ConcurrentTracesVminTC':
                continue  # Skip tests using ConcurrentTracesVminTC template
            if not bnm:
                continue  # skip test that do not have base#
            if bnm == '0':
                continue  # skip test that have base#==0

            if bnm not in bnmctrl:
                bnmctrl[bnm] = {}
            if mod not in bnmctrl[bnm]:
                bnmctrl[bnm][mod] = []
            if test not in bnmctrl[bnm][mod]:
                bnmctrl[bnm][mod].append(test)
        # print(bnmctrl)

        for bnm in bnmctrl:
            mods = list(bnmctrl[bnm].keys())
            if len(bnm) != 5:
                for mod in mods:
                    for test in bnmctrl[bnm][mod]:
                        self.add_error(198, mod, f'Base#:{bnm} in test:{test} not eq to 5digits inside module:{mods}')  # bnm must be 5digits
            else:
                for mdl in mods:
                    module = str(mdl)
                    self.add_pass(198, module)

            if len(mods) > 1:
                for mod in bnmctrl[bnm]:
                    for test in bnmctrl[bnm][mod]:
                        self.add_error(197, mod, f'Base#:{bnm} in test:{test} is used across multiple modules:{mods}')
            else:
                for mdl in mods:
                    module = str(mdl)
                    self.add_pass(197, module)

        for bnm in bnmctrl:
            for mod in bnmctrl[bnm]:
                tests = bnmctrl[bnm][mod]
                if len(tests) == 1:
                    self.add_pass(199, mod)
                    continue  # len(tests) > 1 means many tests are using the same base number inside a module
                for test in tests:  # print warning for tests sharing base# inside a module
                    self.add_error(199, mod, f'Test:{test} shares Base#:{bnm} with other tests inside module')  # bnm conflicts in a modules among its tests

        # TODO: CHK subflows, must have all vmin searches on VMIN TC, no point test
        # TODO: CHK if patlist have pgmrules on them

        self.bnmctrl = bnmctrl
        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    BaseNumUniq(TestProgram(sys.argv[1]).pickle_init()).run()
