#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This function will check if there is any duplicate bin in a fulltp.
    If there is duplicated bins, we will flag it as qgate error.
    1. Need to get all binID in the bindef file and subbindef file.
    2. Check for duplicated bins.
    3. Flag qgate if there is duplicate bin.
    mod_fname: Return {module_test_plan_name: mtpl_file_path}
"""

import sys
import setenv

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.shell import SystemCall
from gadget.getgit import GetCmd
from gadget.disk import Chdir
from gadget.files import File
from main.qgate import QGateExecute
from collections import OrderedDict, Counter
from pprint import pprint
import os
import glob


class Duplicate_Bindef(QGateBase):
    """
    This Qgate will check for the duplicate bindef in the bindef and subbindef file.
    Reason: duplicate bindef will cause the fulltp to fail to load.
    """

    def return_mod_fname(self):
        """
        Return the module test plan name and its file path.
        :return: {module_test_plan_name: mtpl_file_path}
        """
        mod_fname = self.tpobj.mtpl.get_mod2fname()
        return mod_fname

    def get_common_bin(self):
        """
        Get the common bindef from the common shared folder.
        :return: list of common bin
        """
        not_allow_bin = []  # These bins are in the common_shared
        common_bindef = glob.glob('Shared/BaseInputs/Common/Common_Files/*.bdefs')
        for c_bdef in common_bindef:
            f_lines = File(c_bdef).raw()
            for line in f_lines:
                if line.strip().startswith('#'):
                    continue
                if line.strip().startswith('LeafBin') or line.strip().startswith('Bin '):
                    bin_id = "||".join(line.split('#')[0].split())
                    not_allow_bin.append(bin_id)
        return not_allow_bin

    def get_subbindef_bin(self, sub_bdef):
        """
        Get the binID from the subbindef file.
        :param sub_bdef: subbindef file path
        :return: dictionary of {subbindef_file: [binID1, binID2, ...]}
        """
        binID_dict = {}
        for bdef_file in sub_bdef:
            binID = []
            f_lines = File(bdef_file).raw()
            for line in f_lines:
                if line.strip().startswith('#'):
                    continue
                if line.strip().startswith('LeafBin') or line.strip().startswith('Bin '):
                    bin_id = "||".join(line.split('#')[0].split())
                    binID.append(bin_id)
            binID_dict[bdef_file] = binID
        return binID_dict

    def main(self):
        """Entry point of checker"""
        log.info('-i- Duplicate_Bindef: Start checking for duplicate bindef')
        mod_fname = self.return_mod_fname()

        # 1. Get all the binID in the bindef file and subbindef file
        sub_bdef = []
        for value in mod_fname.values():
            mod_dir = os.path.dirname(value)
            sub_bdef_file = glob.glob(f'{mod_dir}/*.sbdefs')
            if sub_bdef_file:
                sub_bdef.append((sub_bdef_file[0]).split('../')[-1])

        common_bin = self.get_common_bin()  # These bins are in the common_shared

        # Get a binID_dict of mod and its binID
        binID_dict = self.get_subbindef_bin(sub_bdef)

        # Flatten all the bin in all_binID and get duplicate bins in dulicates_bin
        all_binID = []
        for bin_item in binID_dict.values():
            all_binID.extend(bin_item)

        # all_binID will combine both bindef and subbindef and only keep the unique binID
        all_binID = all_binID + common_bin
        all_binID = list(set(all_binID))

        # Get the bin number from all_binID
        new_binID = []
        for bin_item in all_binID:
            temp_bin = bin_item.split('||')[2]
            if f'b{temp_bin}_PASS' in bin_item:
                log.info(f'-i- Duplicate_Bindef: Skipping bin {temp_bin} as it is a PASS bin')
            else:
                new_binID.append(temp_bin)

        # Count occurrences
        counter = Counter(new_binID)
        dulicates_bin = []
        dulicates_bin = [item for item, count in counter.items() if count > 1]

        # Check if there is any duplicate bin
        if dulicates_bin:
            shared_bin_dict = {}
            for bin_item in dulicates_bin:
                mod_list = []
                log.info(f'-i- Duplicate_Bindef: Found duplicate binID: {bin_item}')
                for bdef_file, bin_list in binID_dict.items():
                    if any(bin_item == s.split('||')[2] for s in bin_list):
                        mod_list.append(bdef_file)
                shared_bin_dict[bin_item] = mod_list
            for key, value in sorted(shared_bin_dict.items()):
                log.info(f'-i- Duplicate_Bindef: {key} is duplicated in {value}')
                list_of_mods = []
                for item in sorted(value):
                    mod_name = os.path.basename(os.path.dirname(item))
                    list_of_mods.append(mod_name)
                self.add_error(252, f'{list_of_mods[0]}', f'Duplicate bindef found: {key} in {list_of_mods}')
        else:
            log.info('-i- Duplicate_Bindef: No duplicate bindef found')
            self.add_pass(252, 'BASE')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    Duplicate_Bindef(TestProgram(sys.argv[1]).pickle_init()).run()
