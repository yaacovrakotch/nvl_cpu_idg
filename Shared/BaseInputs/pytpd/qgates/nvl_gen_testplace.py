#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks if the test instances are placed in the correct SubFlows
Checks if SubFlows are following proper naming convention
"""
import setenv      # must be first in the imports
import re
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from gadget.strmore import sha1
from gadget.files import File
from importlib.machinery import SourceFileLoader
from gadget.disk import Chdir
from os.path import dirname, join, exists, basename, isdir
from pymtpl.core import Initialize
import sys
import glob
import os


class NVLTestPlace(QGateBase):

    def read_all_py(self):
        """
        fast version - parse the file
        Iterator - yield all subflow names from source code
        """

        bom = basename(dirname(self.tpobj.envfile))
        for py in (glob.glob(f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IP*.py') +
                   glob.glob(f'{self.tpobj.envdir}/ProgramFlowsTestPlan/ProgramFlows*.py') +
                   # glob.glob(f'{self.tpobj.envdir}/../../Shared/POR_TP/*/ProgramFlowsTestPlan/*_Config.py') +
                   glob.glob(f'{self.tpobj.envdir}/../../Shared/POR_TP/{bom}/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py')):      # this is the official location of the shared programflows.py

            # for py in (glob.glob(f'{self.tpobj.envdir}/ProgramFlowsTestPlan/ProgramFlows*.py')):

            for line in File(py).chomp():

                line = line.strip()

                if '_SubFlow' in line or '_TopFlow' in line:
                    columns = line.strip().split()
                    if len(columns) > 1 and columns[1] == '=':
                        continue
                    if line.strip().startswith(('#', '{', 'from ')):
                        continue

                    if "_SubFlow" not in columns[0] and "TopFlow" not in columns[0]:
                        if "PRL" in columns[0]:
                            if "_SubFlow" not in columns[1] and "TopFlow" not in columns[1]:
                                self.add_error(243, "BASE", f'{columns[0]}::{columns[1]} should have either "_SubFlow or "_TopFlow')
                            else:
                                self.add_pass(243, "BASE")
                        else:
                            if 'MAIN' != columns[0] and 'INIT' != columns[0]:
                                self.add_error(243, "BASE", f'{columns[0]} should be either "{columns[0]}_SubFlow" or "{columns[0]}_TopFlow')
                    yield line.strip().split()[0].replace('_SubFlow', '').replace('_TopFlow', '')

    def main(self):
        """
        Checks if the test instances are following the approved Test Instance Naming Convention
        It is enhanced to include the field that needs correction
        """
        dd = self.tpobj.mtpl.get_instance_to_subflows()
        folderpath = f'{self.tpobj.tpldir}/BaseInputs'
        dirs = [x for x in os.listdir(folderpath) if 'onetoc2' not in x]

        blueprint = list(set(self.read_all_py()))

        # blueprint2 = list(set(self.read_all_py_slow()))
        # pprint(set(blueprint) - set(blueprint2)); exit(0)

        blueprint += "INIT LOTENDFLOW LOTSTARTFLOW TESTPLANENDFLOW TESTPLANSTARTFLOW X".split()

        ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')
        idutmods = """IPC_BASE IPP_BASE IPH_BASE IPG_BASE IPC_CONCURRENT_FLOWS IPH_CONCURRENT_FLOWS
        IPP_CONCURRENT_FLOWS IPG_CONCURRENT_FLOWS""".split()
        ti_name3 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_(X|T|M|S|D|B|N|H)_(ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X)_'
            r'(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|LFM|HFM|TFM|\d{4,5})(_[A-Z0-9_]+)?_(\*|\d+)$')
        ti_name4 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_(X|T|M|S|D|B|N|H)_(ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X)_'
            r'(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|LFM|HFM|TFM|\d{4,5})(_\w+)?$')

        t3_break = re.compile('^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_'
                              '([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)')

        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=False, edict=True, pdict=True):
            if not test.startswith(ignore_tests) and mod not in idutmods:
                t3 = re.search(ti_name3, test)
                t4 = re.search(ti_name4, test)
                if t3 or t4:
                    t3bk = re.search(t3_break, test)
                    tg = t3bk.group(5)
                    # if ('INIT' == tg or 'LOTSTARTFLOW' == tg or 'LOTENDFLOW' == tg or
                    #        'TESTPLANSTARTFLOW' == tg or 'TESTPLANENDFLOW' == tg):
                    #    continue
                    for module_instance, subflows in dd.items():
                        if test in module_instance:
                            tgsf = f'{tg}_SubFlow'
                            # print(tgsf, test)
                            # tgtf = f'{tg}_TopFlow'

                            # if (tg == 'INIT' or tg == 'MAIN' or tg == 'TESTPLANSTARTFLOW' or
                            #         tg == 'TESTPLANENDFLOW' or tg == 'LOTSTARTFLOW' or tg == 'LOTENDFLOW'):
                            #     continue

                            # if any(tgsf in item or tgtf in item for item in subflows):
                            if any(tgsf in item for item in subflows):
                                self.add_pass(244, mod)
                                # print(test)

                            else:
                                for j in range(len(dirs)):
                                    if not(dirs[j] in tg):
                                        if not('INIT' == tg or 'LOTSTARTFLOW' == tg or 'LOTENDFLOW' == tg or
                                               'TESTPLANSTARTFLOW' == tg or 'TESTPLANENDFLOW' == tg):
                                            if not('CPU' in tg or 'GCD' in tg or 'PCD' in tg or 'HUB' in tg):
                                                self.add_error(244, mod, f'{test} is using _{tg}_ but does not exist as SubFlow or TopFlow in the ProgramFlows')
                                    else:
                                        self.add_error(244, mod, f'{test} is using _{tg}_ but does not exist as SubFlow or TopFlow in the ProgramFlows')
        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    NVLTestPlace(TestProgram(sys.argv[1]).pickle_init()).run()
