#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures that the pgm_rule.txt file has the ALL or ALL_CLASS default setting
"""
import sys
import setenv

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from collections import defaultdict, OrderedDict
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from itertools import chain
import json
import re
from gadget.disk import Allfiles, Chdir


class PgmRule(QGateBase):

    def main(self):
        """Entry point of checker"""
        """
        Ensures that the pgm_rule.txt file has the ALL or ALL_CLASS default setting
        """
        fpgmrule = {}
        data = {}
        ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')
        idutmods = """IP_CPU_BASE IP_PCH_BASE IP_CPU_CONCURRENT_FLOWS IP_PCH_CONCURRENT_FLOWS""".split()
        for mod, test, params, ports in self.tpobj.mtpl.iter_flows('INIT', bypass=True, edict=True, pdict=True):
            if not test.startswith(ignore_tests) and mod not in idutmods:
                if params['TEMPLATE'] == 'iCGlXpressTest':
                    glx = params['gl_xpress_file_path']
                    bpg = data.get('bypass_global')
                    if glx and (bpg is None or int(bpg) != 1):
                        if mod not in fpgmrule:
                            fpgmrule[mod] = defaultdict(str)
                        # guaranteed 1:1, testnames per bom are unique as enforced by TPIE
                        fpgmrule[mod][test] = {'combo': {}, 'glx': '', 'bpg': ''}
                        fpgmrule[mod][test]['glx'] = glx
                        fpgmrule[mod][test]['bpg'] = bpg

        re_pgmdata = re.compile(r'(\S+)\s*=\s*(\S+|\"[^\"]+\")\s*,\s*\w+\s*,\s*(\S+)\s*:\s*(\S+)')

        with Chdir(self.tpobj.tpldir):
            for mod in fpgmrule:
                for test in fpgmrule[mod]:
                    glx = fpgmrule[mod][test]['glx']  # get pgm_rule file
                    with open(glx, 'r') as file:
                        for line in file:
                            line = line.strip()
                            if line.startswith('#'):
                                continue
                            elif not line:
                                continue
                            # parse the data with some gibberish grade4 regex
                            pgmdata = re_pgmdata.search(line)
                            # print("PGMDATA: ", pgmdata)
                            param = pgmdata.group(1)
                            # print("Group1", param)
                            param_data = pgmdata.group(2)
                            # print("Group2", param_data)
                            param_test = pgmdata.group(3)
                            # print("Group3", param_test)
                            param_locn = pgmdata.group(4)
                            # print("Group4", param_locn)
                            combo = param + '_' + param_test
                            # print("COMBO:", combo)
                            rules = '_'.join([param, param_data, param_test, param_locn])
                            # print("RULES:", rules)
                            if 'combo' not in fpgmrule[mod][test]:
                                fpgmrule[mod][test]['combo'] = {}
                            if combo not in fpgmrule[mod][test]['combo']:
                                fpgmrule[mod][test]['combo'][combo] = []
                            fpgmrule[mod][test]['combo'][combo].append(rules)
        allocset = ['ALL', 'ALL_CLASS']
        errors = []
        for mod in fpgmrule:
            for test in fpgmrule[mod]:
                for combo in fpgmrule[mod][test]['combo']:
                    locn = []
                    for pgmset in range(len(fpgmrule[mod][test]['combo'][combo])):
                        x = re.search(r'\S+,(\S+)$', fpgmrule[mod][test]['combo'][combo][pgmset])
                        locset = x.group(1)
                        if locset not in locn:
                            locn.append(locset)

                    # if match == 0, then ERROR
                    match = [(x, y) for x in locn for y in allocset if (x == y or x.startswith(y) or x.endswith(y))]
                    if len(match) == 0:
                        self.add_error(120, mod, f'PGMrule test:{test} with action on param|test combo: {combo} does not have default ALL/ALL_CLASS setting')
                    else:
                        self.add_pass(120, mod)

        if len(errors) > 0:
            return errors

        return  # pragma: no cover


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    PgmRule(TestProgram(sys.argv[1]).pickle_init()).run()
