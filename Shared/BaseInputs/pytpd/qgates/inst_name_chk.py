#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks if the test instances are following the approved Test Instance Naming Convention
It is enhanced to include the field that needs correction
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
import sys
import json


class TestNameChk(QGateBase):

    def main(self):
        """
        Checks if the test instances are following the approved Test Instance Naming Convention
        It is enhanced to include the field that needs correction
        """
        ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')
        idutmods = """IP_CPU_BASE IP_PCH_BASE IP_CPU_CONCURRENT_FLOWS IP_PCH_CONCURRENT_FLOWS""".split()
        ti_name3 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_'
            r'(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$')
        ti_name4 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_'
            r'(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_\w+)?$')

        t3_break = re.compile('^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_'
                              '([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)')

        g123567 = re.compile('^([A-Z0-9]+$)')
        g4 = re.compile('^(K|E|X)+$')
        g8 = re.compile(r'^(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)+$')
        g9 = re.compile(r'^(X|[LHT]FM|\d+)$')
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if not test.startswith(ignore_tests) and mod not in idutmods:
                t3 = re.search(ti_name3, test)
                t4 = re.search(ti_name4, test)
                if t3:
                    self.add_pass(113, mod)
                elif t4:
                    self.add_pass(113, mod)
                elif t3 is None and t4 is None:
                    t3bk = re.search(t3_break, test)
                    if t3bk is None:
                        continue
                    grp = 9
                    for i in range(grp):
                        j = i + 1
                        tg = t3bk.group(j)
                        if j == 1 or j == 2 or j == 3 or j == 5 or j == 6 or j == 7:
                            chk = re.search(g123567, tg)
                            if chk is None:
                                self.add_error(113, mod, f'{test} is not following naming convention please fix '
                                                         f'{j}th field currently set as "_{tg}_".'
                                                         f'Please check test instance naming convention wiki')
                        elif j == 4:
                            chk = re.search(g4, tg)
                            if chk is None:
                                self.add_error(113, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". Only accepts "K|E|X"')
                        elif j == 8:
                            chk = re.search(g8, tg)
                            if chk is None:
                                self.add_error(113, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". This is the corner field, '
                                               f'should'
                                               f' be F1|F2|F3..Fn or X')
                        elif j == 9:
                            chk = re.search(g9, tg)
                            if chk is None:
                                self.add_error(113, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_".  This is the freq field, should'
                                               f' be in digits in MHz(for freq e.g. 5000) or "X"')
                        else:
                            pass

        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TestNameChk(TestProgram(sys.argv[1]).pickle_init()).run()
