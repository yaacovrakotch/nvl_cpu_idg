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
from gadget.strmore import sha1
from importlib.machinery import SourceFileLoader
from pymtpl.core import Initialize
import sys
import glob


class NVLTestNameChk(QGateBase):

    def read_all_py(self):
        """
        Iterator - yield all subflow names from source code
        """
        for py in (glob.glob(f'{self.tpobj.envdir}/ProgramFlowsTestPlan/*.py') +
                   glob.glob(f'Shared/POR_TP/*.py')):      # this is the official location of the shared programflows.py
            Initialize.written = None     # Do not write
            pymodule = SourceFileLoader(sha1(py), py).load_module()
            if hasattr(pymodule, 'flow_code'):
                text = getattr(pymodule, 'flow_code')
                for line in text.split('\n'):
                    if not line.strip():
                        continue   # empty
                    if line.strip().startswith('#'):
                        continue
                    yield line.strip().split()[0].replace('_SubFlow', '').replace('_TopFlow', '')

    def main(self):
        """
        Checks if the test instances are following the approved Test Instance Naming Convention
        It is enhanced to include the field that needs correction
        """
        blueprint = list(set(self.read_all_py()))
        blueprint += "INIT LOTENDFLOW LOTSTARTFLOW TESTPLANENDFLOW TESTPLANSTARTFLOW X".split()

        ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')
        idutmods = """IP_CPU_BASE IP_PCH_BASE IP_CPU_CONCURRENT_FLOWS IP_PCH_CONCURRENT_FLOWS""".split()
        ti_name3 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_(X|T|M|S|D|B|N|H)_(ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X)_'
            r'(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|LFM|HFM|TFM|\d{4,5})(_[A-Z0-9_]+)?_(\*|\d+)$')
        ti_name4 = re.compile(
            '^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_(X|T|M|S|D|B|N|H)_(ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X)_'
            r'(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|LFM|HFM|TFM|\d{4,5})(_\w+)?$')

        t3_break = re.compile('^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_'
                              '([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)')

        g1235 = re.compile('^([A-Z0-9]+$)')
        g4 = re.compile('^(K|E|X)+$')
        g5 = re.compile('^([A-Z0-9]+$)')
        g6 = re.compile(r'^(X|T|M|S|D|B|N|H)+$')
        g7 = re.compile(r'^(ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|SAIS|SAPS|SAAT|X)+$')
        g8 = re.compile(r'^(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)+$')
        g9 = re.compile(r'^(X|LFM|HFM|TFM|\d{4,5})$')
        for mod, test, data, _ in self.tpobj.mtpl.iter_tests():
            fields = test.split('_')
            if not test.isupper() and not (test.startswith(ignore_tests)) and mod not in idutmods:
                self.add_error(216, mod, f'{test} has lower case characters.  Please make it all caps.')
                continue
            if len(fields) < 9 and not(test.startswith(ignore_tests)) and mod not in idutmods:
                self.add_error(216, mod, f'{test} contains {len(fields)} field(s) only.  Should be at least 9 fields')
                continue
            if not test.startswith(ignore_tests) and mod not in idutmods:
                t3 = re.search(ti_name3, test)
                t4 = re.search(ti_name4, test)
                if t3 or t4:
                    found = 0
                    t3bk = re.search(t3_break, test)
                    tg = t3bk.group(5)
                    for i in blueprint:
                        if tg == i:
                            found = 1
                    if found == 0:
                        self.add_error(216, mod,
                                       f'{test} is not following naming convention please fix '
                                       f'5th field currently set as "_{tg}_". It should be one of the valid '
                                       f'Subflows in the TPBlueprint.  Please see NVL Test Instance Naming '
                                       f'Convention in goto/nvl.its')
                    else:
                        self.add_pass(216, mod)
                if t3 is None and t4 is None:
                    t3bk = re.search(t3_break, test)
                    # if t3bk is None:
                    #      continue
                    grp = 9
                    for i in range(grp):
                        j = i + 1
                        tg = t3bk.group(j)
                        # if j == 1 or j == 2 or j == 3 or j == 5:
                        #     chk = re.search(g1235, tg)
                        #     if chk is None:
                        #         self.add_error(216, mod, f'{test} is not following naming convention please fix '
                        #                                  f'{j}th field currently set as "_{tg}_".'
                        #                                  f'Please check test instance naming convention wiki')
                        if j == 4:
                            chk = re.search(g4, tg)
                            if chk is None:
                                self.add_error(216, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". Only accepts "K|E|X"')

                        elif j == 5:
                            found = 0
                            for i in blueprint:
                                if tg == i:
                                    found = 1
                            if found == 0:
                                self.add_error(216, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'5th field currently set as "_{tg}_". It should be one of the valid '
                                               f'Subflows in the TPBlueprint.  Please see NVL Test Instance Naming '
                                               f'Convention in goto/mtlits')

                        elif j == 6:
                            chk = re.search(g6, tg)
                            if chk is None:
                                self.add_error(216, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". It should be any of these'
                                               f' X|T|M|S|D|B|N|H')

                        elif j == 7:
                            chk = re.search(g7, tg)
                            if chk is None:
                                self.add_error(216, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". It should be any of these'
                                               f' ATA|CRA|CLRA|ATB|CRB|CLRB|GT|SAQ|SAC|SAN|SACD|SANPU|SAME|SAIOC|'
                                               f'SAIS|SAPS|SAAT|X')

                        elif j == 8:
                            chk = re.search(g8, tg)
                            if chk is None:
                                self.add_error(216, mod,
                                               f'{test} is not following naming convention please fix '
                                               f'{j}th field currently set as "_{tg}_". This is the corner field, '
                                               f'should'
                                               f' be [VF]MAX|[VF]MIN|[VF]NOM||F1|F2|F3..Fn or X')
                        elif j == 9:
                            chk = re.search(g9, tg)
                            if chk is None:
                                self.add_error(216, mod,
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
