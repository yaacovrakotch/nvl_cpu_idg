#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks if the test instances are following the approved Test Instance Naming Convention
It is enhanced to include the field that needs correction
"""
import setenv      # must be first in the imports
import re
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from gadget.disk import Chdir
from gadget.strmore import sha1
from gadget.files import File
from importlib.machinery import SourceFileLoader
from pymtpl.core import Initialize
from os.path import dirname, join, exists, basename, isdir
import sys
import glob
import os


class NVLTestNameChk(QGateBase):

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

            is_init = False
            for line in File(py).chomp():

                line = line.strip()
                if is_init and line.startswith("'''"):
                    is_init = False
                if line.startswith('INIT_code'):
                    is_init = True

                if '_SubFlow' in line or '_TopFlow' in line:
                    elems = line.strip().split()
                    if len(elems) > 1 and elems[1] == '=':
                        continue
                    if line.strip().startswith(('#', '{')):
                        continue
                    if is_init:
                        yield elems[1].replace('_SubFlow', '').replace('_TopFlow', '')
                    else:
                        yield elems[0].replace('_SubFlow', '').replace('_TopFlow', '')

    def read_all_py_slow(self):
        """
        slow version - read the file
        Iterator - yield all subflow names from source code
        """

        bom = basename(dirname(self.tpobj.envfile))
        for py in (glob.glob(f'{self.tpobj.envdir}/ProgramFlowsTestPlan/IP*.py') +
                   glob.glob(f'{self.tpobj.envdir}/ProgramFlowsTestPlan/ProgramFlows*.py') +
                   # glob.glob(f'{self.tpobj.envdir}/../../Shared/POR_TP/*/ProgramFlowsTestPlan/*_Config.py') +
                   glob.glob(f'{self.tpobj.envdir}/../../Shared/POR_TP/{bom}/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py')):      # this is the official location of the shared programflows.py
            # for py in (glob.glob(f'{self.tpobj.envdir}/ProgramFlowsTestPlan/ProgramFlows*.py')):

            Initialize.written = None     # Do not write
            with Chdir(f'{self.tpobj.envdir}/ProgramFlowsTestPlan'):
                print(py)
                pymodule = SourceFileLoader(sha1(py), py).load_module()

            for keyword in 'MAIN_code INIT_code CPUDISAGG_SubFlow HUBDISAGG_SubFlow GCDDISAGG_SubFlow PCDDISAGG_SubFlow'.split():
                if hasattr(pymodule, keyword):
                    text = getattr(pymodule, keyword)
                    for line in text.split('\n'):
                        if not line.strip():
                            continue  # empty
                        if line.strip().startswith('#'):
                            continue
                        if keyword == 'INIT_code':
                            yield line.strip().split()[1].replace('_SubFlow', '').replace('_TopFlow', '')
                        else:
                            yield line.strip().split()[0].replace('_SubFlow', '').replace('_TopFlow', '')

    def report_error(self, mod, test, tg):
        self.add_error(239, mod,
                       f'{test} is not following naming convention please fix '
                       f'5th field currently set as "_{tg}_". It should be one of the valid '
                       f'Subflows in the TPBlueprint.  Please see NVL Test Instance Naming '
                       f'Convention in goto/mtlits')

    def main(self):
        """
        Checks if the test instances are following the approved Test Instance Naming Convention
        It is enhanced to include the field that needs correction
        """

        blueprint = list(set(self.read_all_py()))

        # blueprint2 = list(set(self.read_all_py_slow()))
        # pprint(set(blueprint) - set(blueprint2)); exit(0)

        folderpath = f'{self.tpobj.tpldir}/BaseInputs'
        dirs = os.listdir(folderpath)      # ['CPU', 'GCD', 'HUB', 'PCD']

        # special flows (hardcoded)
        blueprint += "INIT LOTENDFLOW LOTSTARTFLOW TESTPLANENDFLOW TESTPLANSTARTFLOW X".split()

        ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')
        idutmods = """IP_CPU_BASE IP_PCH_BASE IP_CPU_CONCURRENT_FLOWS IP_PCH_CONCURRENT_FLOWS""".split()
        ti_name3 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_(X|T|M|S|D|B|N|H)_(ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X)_'
            r'(X|FBAT|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|LFM|HFM|TFM|\d{4,5})(_[A-Z0-9_]+)?_(\*|\d+)$')
        ti_name4 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_(X|T|M|S|D|B|N|H)_(ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X)_'
            r'(X|FBAT|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|LFM|HFM|TFM|\d{4,5})(_\w+)?$')

        t3_break = re.compile('^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_'
                              '([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)')

        g1235 = re.compile('^([A-Z0-9]+$)')
        g4 = re.compile('^(K|E|X)+$')
        g5 = re.compile('^([A-Z0-9]+$)')
        g6 = re.compile(r'^(X|TAP|[TMSDBNH]I[TMSDBNH]O)+$')
        g7 = re.compile(r'^(AT|ATA|ATB|CCF|CCFA|CCFB|CR|CRA|CRB|CLRA|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X|VNNAON|VCCIA|VCCIO|V1P8A|VCCSA|VDD2H|VCCGT|VCCLPECORE|VDDQ)+$')
        g8 = re.compile(r'^(X|FBAT|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)+$')
        g9 = re.compile(r'^(X|LFM|HFM|TFM|\d{4,5})$')

        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            modl = mtpl.split('/')[-1].split('.')[0]
            with open(mtpl, 'r') as f:
                mt = False
                for file in f:
                    if 'MultiTrialTest' in file:
                        mt = True
                        mtname = file.split()[1]
                    if mt and 'CSharpTrialTest' in file:
                        mt = False
                        fstrip = file.strip()
                        testname = fstrip.split('\"')[1]
                        fieldcount = testname.split('_')
                        for z in range(len(fieldcount) - 1):
                            if z == 3:
                                grp4 = g4.search(fieldcount[z])
                                if not grp4:
                                    self.add_error(239, modl, f'The 4th field of CSharpTrialTest name {testname} used by MultiTrialTest {mtname} should be K|E|X only')
                            if z == 5:
                                grp6 = g6.search(fieldcount[z])
                                if not grp6:
                                    self.add_error(239, modl,
                                                   f'The 6th field of CSharpTrialTest name {testname} used by MultiTrialTest {mtname} should meet this regex (X|TAP|[TMSDBNH]I[TMSDBNH]O)')
                            if z == 6:
                                grp7 = g7.search(fieldcount[z])
                                if not grp7:
                                    self.add_error(239, modl,
                                                   f'The 7th field of CSharpTrialTest name {testname} used by MultiTrialTest {mtname} should meet this '
                                                   f'regex (AT|ATA|ATB|CCF|CCFA|CCFB|CR|CRA|CRB|CLRA|CLRB|GT|SAQ|SAC|SAN'
                                                   f'|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X|VNNAON|VCCIA|VCCIO|V1P8A|'
                                                   f'VCCSA|VDD2H|VCCGT|VCCLPECORE|VDDQ)')
                            if z == 7:
                                grp8 = g8.search(fieldcount[z])
                                if not grp8:
                                    self.add_error(239, modl,
                                                   f'The 8th field of CSharpTrialTest name {testname} used by MultiTrialTest {mtname} should meet '
                                                   f'this regex (X|FBAT|[VF]?MAX|[VF]?MIN|[VF]?NOM|Fn)')

        for mod, test, data, _ in self.tpobj.mtpl.iter_tests():
            fields = test.split('_')

            if not test.isupper() and not (test.startswith(ignore_tests)) and mod not in idutmods:
                self.add_error(239, mod, f'{test} has lower case characters.  Please make it all caps.')
                continue

            if len(fields) < 9 and not(test.startswith(ignore_tests)) and mod not in idutmods:
                self.add_error(239, mod, f'{test} contains {len(fields)} field(s) only.  Should be at least 9 fields')
                continue

            if not test.startswith(ignore_tests) and mod not in idutmods:
                t3 = ti_name3.search(test)
                t4 = ti_name4.search(test)
                if t3 or t4:
                    found = 0
                    t3bk = t3_break.search(test)
                    tg = t3bk.group(5)
                    for i in blueprint:
                        if tg == i:
                            found = 1
                    if found == 0:
                        if len(dirs):
                            for x in range(len(dirs)):
                                if not (dirs[x] in tg):
                                    # if not ('INIT' == tg or 'LOTSTARTFLOW' == tg or 'LOTENDFLOW' == tg or
                                    #         'TESTPLANSTARTFLOW' == tg or 'TESTPLANENDFLOW' == tg):
                                    if not ('CPU' in tg or 'GCD' in tg or 'PCD' in tg or 'HUB' in tg):
                                        self.report_error(mod, test, tg)
                                else:
                                    self.report_error(mod, test, tg)
                        else:
                            self.report_error(mod, test, tg)
                    else:
                        self.add_pass(239, mod)
                if t3 is None and t4 is None:
                    t3bk = t3_break.search(test)
                    if t3bk is None:
                        self.add_error(239, mod, f'Something wrong with {test} name, please double check')
                        continue
                    grp = 9
                    for i in range(grp):
                        j = i + 1
                        tg = t3bk.group(j)

                        if j == 4:
                            if not g4.search(tg):
                                self.add_error(239, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". Only accepts "K|E|X"')

                        elif j == 5:
                            found = 0
                            for i in blueprint:
                                if tg == i:
                                    found = 1
                            if found == 0:
                                if len(dirs):
                                    for x in range(len(dirs)):
                                        if not (dirs[x] in tg):
                                            # if not ('INIT' == tg or 'LOTSTARTFLOW' == tg or 'LOTENDFLOW' == tg or
                                            #         'TESTPLANSTARTFLOW' == tg or 'TESTPLANENDFLOW' == tg):
                                            if not ('CPU' in tg or 'GCD' in tg or 'PCD' in tg or 'HUB' in tg):
                                                self.report_error(mod, test, tg)
                                        else:
                                            self.report_error(mod, test, tg)
                                else:
                                    self.report_error(mod, test, tg)

                        elif j == 6:
                            if not g6.search(tg):
                                self.add_error(239, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". It should be any of these'
                                               f' X|TAP|[TMSDBNH]I[TMSDBNH]O')

                        elif j == 7:
                            if not g7.search(tg):
                                self.add_error(239, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". It should be any of these'
                                               f' AT|ATA|ATB|CCF|CCFA|CCFB|CR|CRA|CRB|CLRA|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|'
                                               f'SAPS|SAAT|X|VNNAON|VCCIA|VCCIO|V1P8A|VCCSA|VDD2H|VCCGT|VCCLPECORE|VDDQ')

                        elif j == 8:
                            if not g8.search(tg):
                                self.add_error(239, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". This is the corner field, '
                                               f'should'
                                               f' be [VF]MAX|[VF]MIN|[VF]NOM||F1|F2|F3..Fn or X')
                        elif j == 9:
                            if not g9.search(tg):
                                self.add_error(239, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_".  This is the freq field, should'
                                               f' be in digits in MHz(for freq e.g. 5000 (min of 4 and max of 5 digits)'
                                               f' or either "HFM", "LFM", "TFM", or "X"')
                        # else:
                        #     pass

        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    NVLTestNameChk(TestProgram(sys.argv[1])).run()
