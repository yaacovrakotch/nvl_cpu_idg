#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Tests Speedflows to ensure that FLowIndex, FlowDomain, VoltageTargets all Match per requirements
"""
import setenv      # must be first in the imports
import re
import glob
from os.path import dirname, basename, exists
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip, get_param, CheckerLog
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from itertools import chain
from collections import defaultdict
import sys
import json


class VminTCFICB(QGateBase):

    def main(self):
        """
        This function checks FlowIndexCallbackName inside CHK speedflow tests in kill
        :param mod: Module Name (ARR_CORE_CXX)
        :param test: EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTC_1001
        :param dd: data = { 'kil': 'KIL', 'cid': 'CR5@F4', etc}
        :return:
        """
        errors = []
        bomflows = self.tpobj.bin_matrix(self.tpobj.get_bom())
        chk_subflows = """CSNF3 CSNF2 CSNF1
        CCRF6 CCRF4 CCRF1
        CCLRF6 CCLRF4 CCLRF1
        CATF6 CATF4 CATF1
        CGTF6 CGTF4 CGTF1
        CCRF2 CCRF3 CCRF5
        CCLRF2 CCLRF3 CCLRF5
        CATF2 CATF3 CATF5
        CGTF2 CGTF3 CGTF5
        CBSF3 CBSF1
        CBSF2
        """.split()  # chk only subflow, scoreboarding here and  guardbanding reqd tests

        flowdomains = {'core': {'name': 'CORE', 'domains': ['CR', 'CRX', 'CRU', 'CRUX']},
                       'atom': {'name': 'ATOMC', 'domains': ['AT', 'ATS']},
                       'ring': {'name': 'RING', 'domains': ['CLR', 'CLRS']},
                       'gt': {'name': 'GT', 'domains': ['GT']},
                       'soc': {'name': 'SOC', 'domains': ['SAQ', 'SAN', 'SACD', 'SAF', 'SAVPU', 'SAME', 'SAPS', 'SAIS', 'SAAT', 'SCDS', 'SVPUS', 'SMES', 'SATS']}
                       }

        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):

            tm = data.get('TEMPLATE')
            mtplobj = self.tpobj.mtpl
            if not tm == 'VminTC':
                continue
            sf = self.gen_subflow(test)
            if sf not in chk_subflows:
                continue
            kil = data.get('_EDCKIL')
            if kil != 'KIL':
                continue

            # TODO: Add checks for static test that have this field populated and error out
            spd = 0  # default set to static test
            if any(test.endswith(ff) for ff in bomflows):
                spd = 1  # test is speedflow format
            if not spd:  # static test exit out
                continue

            fcb = data.get('FlowIndexCallbackName')
            cid = data.get('CornerIdentifiers')
            fli = data.get('FlowIndex')
            vtr = data.get('VoltageTargets')
            soc = flowdomains['soc']['domains']
            flicb = 'FlowIndexCallbackName'

            if cid is None:
                continue
            else:
                insoc = any(sd in cid for sd in soc)

            # assign the test's FlowDomain based on the VoltageTargets value
            if 'CORE' in vtr and 'CR' in cid:
                fd = 'CORE'
            elif 'ATOM' in vtr and 'AT' in cid:
                fd = 'ATOMC'
            elif 'CCF' in vtr and 'CLR' in cid:
                fd = 'RING'
            elif 'VCCGT' in vtr and 'GT' in cid:
                fd = 'GT'
            elif 'VCCSA' in vtr and insoc:
                fd = 'SOC'
            else:  # FlowDomain default setting
                fd = 'NYET'
            efcb = 'CheckFlow(%s)' % fd

            # only tests in chk subflows + speedflow format will pass thru here
            if spd and kil == 'KIL' and efcb == fcb and fli:
                self.add_pass(189, mod)
                continue  # pass!
            byp = mtplobj.is_bypassed(mod, test)
            if fd == 'NYET':
                self.add_error(189, mod, f'Test:{test} Unable to determine FlowDomain with VoltageTargets={vtr} CornerID={cid}; bypass={byp}')
                continue
            # if not byp: self.add_error(189, mod, f'Test:{test} missing/incorrect required data={efcb} on param={
            # flicb}; bypass={byp}')
            else:
                self.add_error(189, mod, f'Test:{test} missing/incorrect required data={efcb} on param={flicb}; bypass={byp}')
        return

    def gen_subflow(self, test):
        """
        This function reads the testname and returns the subflow portion; 5th field
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001
        :return: sf  # returns the subflow part of the testname, ex: SCRF1
        """
        ti_name3 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$')
        ti_name4 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_\w+)?$')
        t3 = ti_name3.search(test)
        t4 = ti_name4.search(test)
        ts = re.compile(r'([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)')  # relaxed SF check
        if t3:
            sf = t3.group(5)
        if t4:
            sf = t4.group(5)
        else:  # relaxed regex to discount tests that have correct subflow but wrong ti_name convention
            f = ts.search(test)
            if f:
                sf = f.group(5)
            else:
                sf = 'NYET'
        return sf


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    VminTCFICB(TestProgram(sys.argv[1]).pickle_init()).run()
