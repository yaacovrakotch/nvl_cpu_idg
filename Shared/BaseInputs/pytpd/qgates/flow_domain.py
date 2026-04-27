#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Flow Domain Compliance checks
159: PBMFC Flow Control without Domain Name
160: PBMFC SetFlow without a Domain Name
163: Domain name present in SetFlow but Missing in FlowCOntrol
164: Invalid Domain Name
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


class FlowDomain(QGateBase):

    def main(self):
        """
        Checks for KILL vs EDC speedflow usage, must have a valid flow_domain approved by UPSWG (see wiki UPS ITS)
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')
                          ]
        :param stpldata:
        :return:
        """

        errors = []
        fd_kill = """CORE ATOMC RING GT SOC""".split()
        fd_edc = """CORE_EDC ATOMC_EDC RING_EDC GT_EDC SOC_EDC""".split()
        fd = []
        fd.extend(fd_kill)
        fd.extend(fd_edc)

        fcd = {}  # flow control dictionary
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            pt = data.get('TEMPLATE')

            if pt == 'PrimeFlowControlForkTestMethod':
                dn = data.get('DomainName')
                if not dn:
                    self.add_error(159, mod, f'Module uses PMBFC FlowControl without a DomainName!')
                    continue
                else:
                    self.add_pass(159, mod)
                if mod not in fcd:
                    fcd[mod] = {}
                if dn not in fcd[mod]:
                    fcd[mod][dn] = {'fc': 'yes', 'sf': ''}
                else:
                    fcd[mod][dn]['fc'] = 'yes'
            elif pt == 'PrimeFlowControlSetTestMethod':
                dnn = data.get('DomainName')
                if not dnn:
                    self.add_error(160, mod, f'Module uses PMBFC SetFlow without a DomainName!')
                    continue
                else:
                    self.add_pass(160, mod)
                if mod not in fcd:
                    fcd[mod] = {}
                if dnn not in fcd[mod]:
                    fcd[mod][dnn] = {'fc': '', 'sf': 'yes'}
                else:
                    fcd[mod][dnn]['sf'] = 'yes'

        # check if modules are using valid DomainName params
        for mod in fcd:
            for dom in fcd[mod]:
                if dom in fd:
                    fc = fcd[mod][dom]['fc']
                    sf = fcd[mod][dom]['sf']
                    self.add_pass(164, mod)
                    if ('EDC' in dom and fc and sf) or ('EDC' in dom and fc and not sf) or \
                            ('EDC' not in dom and fc and sf) or ('EDC' not in dom and fc and not sf):  # mtl_vmintcchk will cover this
                        self.add_pass(163, mod)
                        continue
                    #elif 'EDC' in dom and fc and not sf:  # mtl_vmintcchk will cover this
                    #    continue
                    #elif 'EDC' not in dom and fc and sf:  # mtl_vmintcchk will cover this
                    #    continue
                    #elif 'EDC' not in dom and fc and not sf:  # mtl_vmintcchk will cover this
                    #    continue
                    else:  # EDC+!fc+sf or !EDC+!fc+sf, very unlikely scenario as this can only be a TPIE fail scenario
                        if 'YBS' not in mod:
                            self.add_error(163, mod, f'DomainName={dom} present in SetFlow but missing in FlowControl')
                        else:
                            self.add_pass(163, mod)
                else:
                    self.add_error(164, mod, f'Module uses an invalid DomainName={dom}')

        if len(errors) > 0:
            return errors

        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    FlowDomain(TestProgram(sys.argv[1]).pickle_init()).run()
