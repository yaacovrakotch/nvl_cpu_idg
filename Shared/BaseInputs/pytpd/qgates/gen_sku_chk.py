#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures Recovery SKU from TPS matches with YBS
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
import sys
import json


class GenSKUChk(QGateBase):

    def main(self):
        """
        Confirm YBS SKU and TPD SKU are the same
        :param stpldata:
        :param mtplobj:
        :return:
        """
        idutmods = """IP_CPU_BASE IP_PCH_BASE IP_CPU_CONCURRENT_FLOWS IP_PCH_CONCURRENT_FLOWS""".split()
        ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')

        kwargs = dict(bypass=True, idict=False)
        main_flow = self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True)
        init_flow = self.tpobj.mtpl.iter_flows('INIT', bypass=True, edict=True, pdict=True)
        tpd_copy1 = []
        difference = []
        for mod, test, data, _ in chain(main_flow, init_flow):
            if mod not in ignore_tests and mod not in idutmods:
                # start check
                if data['TEMPLATE'] == 'DieRecoveryBase':  # only instance with TEMPLATE = DieRecoveryBase
                    # get rules and sku files
                    rulesfile = data['RulesFile']  # JSON TP file
                    jsonfile = f'{self.tpobj.tpldir}/{rulesfile}'

                    # get SKUs from rules file
                    with open(jsonfile) as f:
                        # tpd_copy = set()
                        try:
                            rules = json.load(f)
                            self.add_pass(210, mod)
                        except json.decoder.JSONDecodeError as e:
                            self.add_error(210, mod, f'Recovery SKU TPD vs YBS compare check failed, '
                                                     f'RulesFile is invalid or empty: {rulesfile}')
                            continue

                        if "ALLSKU" not in rules:  # if "ALLSKU" key does not exist it will use the SKUs instead
                            for keys, values in rules.items():
                                if keys == "Rules":
                                    for obj in values:
                                        if "SKUs" in obj:
                                            skus = obj["SKUs"]
                                            for z in range(len(skus)):
                                                if not(skus[z] in tpd_copy1):
                                                    tpd_copy1.append(skus[z])
                            tpd_copy = set(tpd_copy1)
                            skufile1 = "Modules/YBS_UPSS_YXX/InputFiles/IA_ATOM_Recovery.xml"
                        else:  # MTL with ALLSKU
                            tpd_copy = set()
                            tpd_copy.update(rules["ALLSKU"][0]["SKUs"])  # save all SKUs inside tpd_copy
                            skufile1 = rules["ALLSKU"][0]["Ref"]  # save Ref SKUs file name
                        tpd_copyx = list(tpd_copy)
                        skufile = f'{self.tpobj.tpldir}/{skufile1}'
                    if not exists(skufile):
                        return    # Do nothing if file is missing

                    # get SKUs from XML file
                    with open(skufile) as f:
                        tree = ElementTree.parse(f)
                        ybs_copy1 = set([sku.get('group') for sku in tree.findall('./Area/SKUs')])
                        ybs_copy = list(ybs_copy1)
                    for sk in range(len(tpd_copyx)):
                        if not(tpd_copyx[sk] in ybs_copy):
                            if not(tpd_copyx[sk] in difference):
                                difference.append(tpd_copyx[sk])
                    if len(difference) == 0:
                        self.add_pass(209, mod)
                        return
                    else:  # if len is not zero, there is a difference
                        self.add_error(209, mod, f'Recovery SKU TPD vs YBS compare check failed '
                                                 f'for test: {test}, difference: {sorted(difference)}')

        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    GenSKUChk(TestProgram(sys.argv[1]).pickle_init()).run()
