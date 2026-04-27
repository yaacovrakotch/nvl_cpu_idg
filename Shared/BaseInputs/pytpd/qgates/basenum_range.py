#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures basenumbers are unique (for TTR)
"""
import sys

import setenv
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
from os.path import exists
import sys
import json
import glob


class BaseNumRange(QGateBase):

    def main(self):
        """
        Check that the basenumbers of the test instances match the expected ranges from this page:
        https://wiki.ith.intel.com/pages/viewpage.action?spaceKey=ITSpdxtp&title=MTL+Base+Number+Strategy
        Started w/ unique basenum qgate - not sure what the bomflows stuff does so I kept it
        Also verify any test instances using VminTC test template w/ a basenum aren't Functional TestMode
        """
        base_num = {}
        cfgfile = glob.glob(f'{self.tpobj.tpldir}/Shared/*/*/basenum_ranges.json')
        if len(cfgfile) == 0:
            self.add_error(245, 'BASE', 'Shared/*/basenum_ranges.json does not exist. This contains valid basenumber ranges per module.')
            return
        elif len(cfgfile) != 1:
            self.add_error(245, 'BASE', 'Shared/*/basenum_ranges.json returns multiple configs. There can be only one.')
            return
        with open(cfgfile[0]) as fh:
            basenum_range_cfg = json.load(fh)

        expected_range = {mod: range(value['start'], value['end']) for mod, value in basenum_range_cfg.items()}

        bomflows = self.tpobj.bin_matrix(self.tpobj.get_bom())
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            tm = data.get('TEMPLATE')
            if any(test.endswith(ff) for ff in bomflows):
                t3 = cfg['ti_name3'].search(test)  # rename the test with generic $FREQ and $FLOWINDEX
                if t3:
                    test = '%s_%s_%s_%s_%s_%s_%s_%s_$FREQ%s_$FLOWINDEX' % (t3.group(1), t3.group(2), t3.group(3),
                                                                           t3.group(4), t3.group(5), t3.group(6),
                                                                           t3.group(7), t3.group(8), t3.group(10))

            bnm = strvalue(data.get('ScoreboardBaseNumber', data.get('base_number', data.get('BaseNumbers', None))))

            if tm == 'ConcurrentTracesVminTC':
                continue  # Skip tests using ConcurrentTracesVminTC template
            if not bnm:
                continue  # skip test that do not have base#
            if bnm == '0':
                continue  # skip test that have base#==0

            if mod not in base_num:
                # if (mod.split('_')[-1]).startswith('P'): # Added by vsgatcha to exclude PCD Modules
                #    continue
                base_num[mod] = []
            if bnm not in base_num[mod]:
                base_num[mod].append(bnm)
            if tm == 'VminTC':
                if data.get('TestMode') == 'Functional':
                    self.add_error(246, mod, f'Base#: {mod} Test:{test} with VminTC template is not allowed to have a basenumber and have Functional TestMode')
                    # print(f'{mod} Test:{test} with VminTC template is not allowed to have a basenumber and have Functional TestMode')
                else:
                    self.add_pass(246, mod)
                    # print(f'{mod} Test:{test} with VminTC template has basenumber and TestMode is not Functional')
        # Go through all of the basenumbers and compare against the expected range. Log messages for each bnum, and add passes or errors
        for mod, basenums in base_num.items():
            if(mod in expected_range):
                valid_range = expected_range[mod]
                nonpup_range = range(6000, 9500)
                for bnum in basenums:
                    if int(bnum) not in valid_range:
                        if len(bnum) == 5:
                            nonpup = bnum[-4:]
                            # self.add_error(245, mod, f'Base#:{bnum} is not in the expected range {valid_range}')
                            if int(nonpup) not in nonpup_range:
                                self.add_error(245, mod, f'Base#:{bnum} is not in the expected range {valid_range}')
                        # else:
                        #     self.add_error(245, mod, f'Base#:{bnum} does not equal to 5 digits')
                        # print(f'{mod} has basenumber {bnum} not in the expected range {valid_range}')
                    else:
                        self.add_pass(245, mod)
                        # print(f'{mod} has basenumber {bnum} in the expected range {valid_range}')
            else:
                self.add_error(245, mod, f'Base#:{mod} has no defined valid range in input config file')
                # print(f'{mod} not in QGate range definition')

        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    BaseNumRange(TestProgram(sys.argv[1]).pickle_init()).run()
