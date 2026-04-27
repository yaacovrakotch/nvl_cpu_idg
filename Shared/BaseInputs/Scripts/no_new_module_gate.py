#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This Qgate is based on post-processing script to clean up format of PROD and ENG EVN files.
Post-processing output Environment file ending line check.
Require only one value of parameter per line.
Each parameter entry in the env file should either end with ;" + (if it's not the end of the param)
or "; (if it's the last entry of the param).
"""
import sys
try:
    import setenv    # must be first in the imports
except ImportError:    # pragma: no cover    - Used when local qgate .py is in tp area
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
import glob
import os


class NoNewModuleGate(QGateBase):

    def main(self):
        # Determine if from PR. This qgate will only apply if it is a PR
        from_pr = (os.environ.get('FROM_PR', 'False')).strip().upper()
        if from_pr != 'TRUE':
            log.info('-i- ProgramFlowChecker is skipped since it is not a PR')
            return 1  # do nothing for tpbuild or mbot

        # Start the Qgate check
        bom = f'{self.tpobj.get_bom()}'
        compath = f'{self.tpobj.tpldir}/Shared/POR_TP/{bom}/SkipModules'
        diepath = f'{self.tpobj.tpldir}/POR_TP/{bom}/SkipModules'

        # get the set of module folder first
        m2m = self.tpobj.mtpl.get_modfolder2mod()  # {module_folder: module}

        filtered_m2m = {key: value for key, value in m2m.items() if
                        '_Torch' not in key and 'ProgramFlowsTestPlan' not in key}

        # Split the dielet and common module
        common_dict = {}
        dielet_dict = {}

        for key, value in filtered_m2m.items():
            if key.startswith(('FUS', 'TPI', 'YBS')) and key.endswith(('_XXX', '_XKPKGDT')):
                common_dict[key] = value
            else:
                dielet_dict[key] = value

        common_list = list(common_dict.keys())
        dielet_list = list(dielet_dict.keys())

        # Parse and get the Common repo first for skip module list.
        com_parse_skip_files = glob.glob(f'{compath}/*.permanent')
        die_parse_skip_files = glob.glob(f'{diepath}/*.permanent')
        com_skip_files_name = [os.path.splitext(os.path.basename(f))[0] for f in com_parse_skip_files]
        die_skip_files_name = [os.path.splitext(os.path.basename(f))[0] for f in die_parse_skip_files]

        # Check which modules are new for the power-on TP
        com_new_mod_found = set(common_list) - set(com_skip_files_name)
        die_new_mod_found = set(dielet_list) - set(die_skip_files_name)

        if all(item.startswith('TPI_') for item in com_new_mod_found) and all(item.startswith('TPI_') for item in die_new_mod_found):
            self.add_pass(288, "BASE")

        else:
            print('Attention: Active modules in Test Program does not match with Skip List!!! Please check to fix for Power-On')
            # Check which modules are new for the power-on TP
            not_com_new_mod = [item for item in com_new_mod_found if not item.startswith('TPI_')]
            if not_com_new_mod:
                message1 = (f'New Module {not_com_new_mod} is not allowed to check-in for NVL power-on time. '
                            f'Gate will be unlocked later.')
                self.add_error(288, "BASE", message1)

            not_die_new_mod = [item for item in die_new_mod_found if not item.startswith('TPI_')]
            if die_new_mod_found:
                message2 = (f'New Module {not_die_new_mod} is not allowed to check-in for NVL power-on time. '
                            f'Gate will be unlocked later.')
                self.add_error(289, "BASE", message2)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    NoNewModuleGate(TestProgram(sys.argv[1]).pickle_init()).run()
