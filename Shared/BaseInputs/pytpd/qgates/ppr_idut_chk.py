#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures that modules that are part of the parallel flows are not enabled for PPR
"""
import re

import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json
import os


class PPRiDUT(QGateBase):

    def main(self):
        class_folder = self.tpobj.envdir
        idut_json = rf'{class_folder}\intradut_flows.json'
        ppr_folder = rf'{self.tpobj.moddir}\PPR\InputFiles\PprConfiguration.json'
        ppr_modules = []
        parallel = []
        full = []
        mod_instance = {}
        fullpar = []
        parallel_mods = {}
        parlmod = []
        enbldtests = set()

        # Checks if the intradut_flows.json and PprConfiguration.json exist. Else exit Qgate
        if not os.path.isfile(ppr_folder):
            return

        if not os.path.isfile(idut_json):
            return
        pattern = r'\"(\S+)::(\S+)\":'

        # Collects all tests that are not Bypassed
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            enbldtests.add(test)

        # Get a list of the Concurrent Flow from the intra_dut.json file
        with open(idut_json, "r") as idut_line:
            for idut_parse in idut_line:
                idut_strip = idut_parse.strip()
                if 'CONCURRENT_FLOWS::' in idut_strip:
                    idutdata = re.match(pattern, idut_strip)
                    param2 = idutdata.group(2)
                    subflow = param2.split('_')[0]
                    full.append(subflow)

        for i in range(0, len(full)):
            for j in range(i + 1, len(full)):
                if full[i] == full[j]:
                    parallel.append(full[j])

        # Final Concurrent Flow list
        # (example: IP_CPU_CONCURRENT_FLOWS::PRL0CPUIOE_IP_CPU_FLOW_SubFlow)
        with open(idut_json, "r") as idut_line:
            for idut_parse in idut_line:
                idut_strip = idut_parse.strip()
                for l in parallel:
                    if l in idut_strip:
                        fullpar.append(idut_strip.split('\"')[1])

        # Get the list of modules::test that are PPR enabled from the PprConfiguration.json file
        with open(ppr_folder, "r") as ppr_line:
            for ppr_parse in ppr_line:
                ppr_strip = ppr_parse.strip()
                if '::' in ppr_strip and '[' in ppr_strip:
                    ppr_modules.append(remove_ip(ppr_strip.split('\"')[1]))

        # Get the module/test to subflow mapping
        list_mod = self.tpobj.mtpl.get_instance_to_subflows()
        for keys, values in list_mod.items():
            v = 0
            modinst = f'{keys[v]}::{keys[v + 1]}'
            mod_instance[modinst] = values

        for k, v in mod_instance.items():
            for fp in range(len(fullpar)):
                if fullpar[fp] in v:
                    parallel_mods[k] = fullpar[fp]

        for k, v in mod_instance.items():
            for pprmod in range(len(ppr_modules)):
                if ppr_modules[pprmod] in k:
                    parlmod.append(k)

        # Check if the the module/test instance is in the parallel flow list.  Also ignores if the test is bypassed
        for mi in range(len(parlmod)):
            if parlmod[mi] in parallel_mods.keys():
                m = parlmod[mi].split('::')[0]
                i = parlmod[mi].split('::')[1]
                if i in enbldtests:
                    flow = parallel_mods[parlmod[mi]]
                    self.add_error(500, m, f'Test {i} in parallel flow {flow} has PPR enabled')
                else:
                    self.add_pass(500, m)
            else:
                m = parlmod[mi].split('::')[0]
                self.add_pass(500, m)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    PPRiDUT(TestProgram(sys.argv[1]).pickle_init()).run()
