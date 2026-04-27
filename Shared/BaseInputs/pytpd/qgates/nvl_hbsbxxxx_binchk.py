#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Qgate for 8 digit binning with following checks
1. All bins must be unique - dupl_bin_chk.py
2. Each port in a test must have a unique bin (QGATE 284 and 285)
3. Each set bin string must end with _port or _n1 or _n2 (QGATE 282)
4. If there's a SetBin and IncrementCounter, the bin used should match (QGATE 283)

"""
import setenv      # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
import sys
import re


class Binning(QGateBase):

    def main(self):
        bin_dict = {}
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            for keys, values in ports.items():
                if 'SetBin' in values:
                    stbin = values['SetBin'].split('_')[0]
                    if mod in bin_dict:
                        bin_dict[mod].append(stbin)
                    else:
                        bin_dict[mod] = [stbin]
                    lastdig = values['SetBin'].split('_')[-1]
                    if lastdig.startswith('n'):
                        lastdig = re.sub(r'n(\d+)', r'-\1', lastdig)
                    if str(keys) != lastdig:
                        self.add_error(
                            282, mod,
                            f"{item} {values['SetBin']} of port {values['Return']} does not end with \"_<port_number>\" or \"_n1\"/\"_n2\""
                        )
                    else:
                        self.add_pass(282, mod)
                    if 'IncrementCounters' in values:
                        SBin = values['SetBin'].split('_')[0]
                        if '::' in values['IncrementCounters']:
                            ICBin = values['IncrementCounters'].split('::')[1].split('_')[0]
                        else:
                            ICBin = values['IncrementCounters'].split('_')[0]
                        if SBin[1:] == ICBin[1:]:
                            self.add_pass(283, mod)
                        else:
                            self.add_error(
                                283, mod,
                                f"{item} of port {values['Return']} has a SetBin: {SBin} and IncrementCounter: {ICBin} 8 digit bin that do not match"
                            )
        # Check for duplicates within the same key
        for mod, stbin_list in bin_dict.items():
            seen = set()
            has_duplicate = False
            for stbin in stbin_list:
                if stbin in seen:
                    self.add_error(284, mod, f'Duplicate SetBin "{stbin}" found within module {mod}')
                    has_duplicate = True
                else:
                    seen.add(stbin)
            if not has_duplicate:
                self.add_pass(284, mod)

        # Check for duplicates across different keys
        stbin_to_mods = {}
        for mod, stbin_list in bin_dict.items():
            for stbin in stbin_list:
                stbin_to_mods.setdefault(stbin, set()).add(mod)

        for stbin, mods in stbin_to_mods.items():
            if len(mods) > 1:
                sorted_mods = sorted(mods)
                mod_list = ', '.join(sorted_mods)
                for mod in sorted_mods:
                    self.add_error(285, mod, f'SetBin "{stbin}" is used by multiple modules: {mod_list}')
            else:
                mod = next(iter(mods))
                self.add_pass(285, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    Binning(TestProgram(sys.argv[1]).pickle_init()).run()
