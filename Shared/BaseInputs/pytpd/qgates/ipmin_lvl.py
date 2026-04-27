#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks for IP and levels combination to make sure it matches
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
import sys
import json


class IPMinLvl(QGateBase):

    def main(self):
        """
        This function loops in all the mtpl test instances and their levels
        If test uses IP_ scoped subflows then verify if levels used is _min_lvl_
        :return:
        :param stpldata: [('MODULE01', 'TEST1', {'TEMPLATE': 'VminTC', 'Levels': 'something_min_lvl_rtten'}, ''),
                          ('MODULE02', 'TEST2', {'TEMPLATE': 'VminTC', 'PatList': 'sublist_list'}, '')]
        :param ipminflows: ['BEGCPU', 'SCRF1', 'SGTF1', 'etc']
        :param ipcpu: {'ARR_CORE_CXX', 'FUN_CORE_CXX'}
        :param ippch: {'ARR_GT_GXX'}
        :return:
        """

        ipclvl = re.compile('ipcpu_lvl.*min_lvl')
        ipplvl = re.compile('ippch_lvl.*min_lvl')
        ipcpu = []
        ippch = []

        for x in self.tpobj.get_all_mtpl_from_stpl('IP_CPU'):
            split_list = (x.split('/')[-2:])
            module = split_list[0]
            ipcpu.append(module)
        for y in self.tpobj.get_all_mtpl_from_stpl('IP_PCH'):
            split_list = (y.split('/')[-2:])
            module = split_list[0]
            ippch.append(module)
        ipminflows = """BEGCPU SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6 CCRF6 CCRF4 CCRF1
        SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6 CCLRF6 CCLRF4 CCLRF1
        SATF1 SATF2 SATF3 SATF4 SATF5 SATF6 CATF6 CATF4 CATF1
        MAXCR MAXCLR MAXAT EDCCR EDCCLR EDCAT ENDCPU SPKLCPU IPFFCPU
        CCRF2 CCRF3 CCRF5
        CCLRF2 CCLRF3 CCLRF5
        CATF2 CATF3 CATF5
        PREGTSRH SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6 CGTF6 CGTF4 CGTF1 MAXGT EDCGT ENDGT SPKLGT IPFFGT
        BEGBS SBSF1 SBSF2 SBSF3 PSTBSSRH CBSF3 CBSF1 MAXBS EDCBS ENDBS SPKLBS IPFFBS
        BEGIOE BEGIOE2 BEGIOE3  SPKLIOE EDCIOE IPFFIOE
        CGTF2 CGTF3 CGTF5
        CBSF2
        """.split()  # parallel subflows min lvls only, same as srhchk_subflows but without BEGGT, BEGGT runs at nom

        for mod, test, params, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            # TODO: temporary waivers for TPI_PRESI
            if mod.startswith('TPI_PRESI'):
                continue
            # if mod not in self.sum[self.mtl_ipminlvlchk]:
            #    self.sum[self.mtl_ipminlvlchk][mod] = {'e': 0, 'w': 0, 'p': 0}
            lvl = get_param(params, 'level')

            if not lvl:  # everything else that gets pass this means they have a level param
                continue

            # tests with valid levels param will proceed here
            sf = self.gen_subflow(test)
            if not(sf in ipminflows):
                continue
            if mod in ipcpu and ipclvl.search(lvl):
                self.add_pass(154, mod)
                continue
            elif mod in ippch and ipplvl.search(lvl):
                self.add_pass(154, mod)
                continue  # pass: ippch module+test using ippch min lvl
            elif mod in ipcpu and 'IP_CPU' not in lvl:
                self.add_error(154, mod, f'IP_CPU Test:{test} subflow={sf} & lvl={lvl} IP_ combo error. Not using IP_CPU levels')
            elif mod in ippch and 'IP_PCH' not in lvl:
                self.add_error(154, mod, f'IP_PCH Test:{test} subflow={sf} & lvl={lvl} IP_ combo error. Not using IP_PCH levels')
            else:
                self.add_pass(154, mod)
        return

    def gen_subflow(self, test):
        """
        This function reads the testname and returns the subflow portion; 5th field
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001
        :return: sf  # returns the subflow part of the testname, ex: SCRF1
        """
        ti_name3 = re.compile(r"^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$")
        ti_name4 = re.compile(r"^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_\w+)?$")

        t3 = ti_name3.search(test)
        t4 = ti_name4.search(test)
        ts = re.compile(r"([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)")  # relaxed SF check
        if t3:
            sf = t3.group(5)
        elif t4:
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
    IPMinLvl(TestProgram(sys.argv[1]).pickle_init()).run()
