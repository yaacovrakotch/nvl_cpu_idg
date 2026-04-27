#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This will check if DCF file is updated for new BOMs in Bin Matrix.
It will parse Bin Matrix to grab BOM and Devrevstep information, then parse DCF
registry to check if it has 4 columns, separated by comma.
Finally, it will compare BOM groups and their corresponding devrevsteps in Bin
Matrix and DCF Registry files.
It also compares SHA1 of DieIDBinning.xml with SHAs in DCF Registry for each
BOM group.
It logs any BOM groups that are in Bin Matrix but missing in DCF Registry, and
any SHA mismatches.
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
from collections import OrderedDict, Counter, defaultdict
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from gadget.errors import ErrorInput, confirm
import hashlib
import os
import re
import glob


class dcf_check(QGateBase):
    """
    Quality Gate to check DCF status using in NVL TP. This checks if new DCF file is needed.
    This will fail if there is no new DCF file uploaded for new BOMs.
    """

    def binmatrix_boms(self):
        """
        Parse Bin Matrix to grab BOM and Devrevstep information.
        Returns:a dictionary with BOM group names as keys and their Devrevstep lists as values.
        dict: {BOMGroup_name: [Devrevstep1, Devrevstep2, ...]}
        """
        bin_matrix_files = glob.glob(f'{self.tpobj.shareddir}/BaseInputs/Common/Common_Class_*/BinMatrix.flm.usrv')

        if not bin_matrix_files:
            self.add_error(276, 'BASE', f"BinMatrix file not found in any Common_Class directory")
            return {}

        binmatrix_bom_groups = defaultdict(list)

        for bin_matrix_usvr in bin_matrix_files:
            bom_group_match = re.findall(r'SelectorRule\s+BomGroupRule\((\w+)\)', File(bin_matrix_usvr).read())
            if bom_group_match:
                bom_group_name = bom_group_match[0]

            for devrevstep_text in re.findall(r'TorchRulesVars.bom\s+==\s+"(\w+)', File(bin_matrix_usvr).read()):
                binmatrix_bom_groups[bom_group_name].append(devrevstep_text)

        log.info(f'-i- DCF_check: BinMatrix BOM Groups: {dict(binmatrix_bom_groups)}')
        return binmatrix_bom_groups

    def dcf_file(self, bom_group_name):
        """
        To check if DieIDBinning.xml exists in common directory and calculate its SHA1 sum.

        :param bom_group_name: BOM group name used to locate the Common_Class directory.
            Accepts either a bare suffix (e.g. ``NVL_S28C``) or a value with the
            ``CLASS_`` prefix (e.g. ``CLASS_NVL_S28C``); the prefix is stripped
            automatically before constructing the directory path.
        :type bom_group_name: str
        :return: dictionary with file path and SHA1 sum if the file is found, or empty dict if the file is not found
        :rtype: dict
        :raises Exception: if an error occurs while calculating the SHA1 sum
        """
        # BOM group names use CLASS_ prefix (e.g. CLASS_NVL_S28C) but directories
        # use only the suffix (e.g. Common_Class_NVL_S28C), so strip CLASS_ if present
        dir_suffix = bom_group_name.split('CLASS_', 1)[-1] if 'CLASS_' in bom_group_name else bom_group_name
        dcf_file = glob.glob(f'{self.tpobj.shareddir}/BaseInputs/Common/Common_Class_{dir_suffix}/DieIDBinning.xml')

        if len(dcf_file) != 1:
            self.add_error(276, 'BASE', f"should Only have 1 DieIDBinning file for BOM Group {bom_group_name}, but found {len(dcf_file)}")
            return {}

        dcf_file_path = dcf_file[0]
        # Normalize line endings (CRLF -> LF) before hashing to ensure
        # consistent SHA1 values across Windows and Linux checkouts
        with open(dcf_file_path, 'rb') as fh:
            content = fh.read().replace(b'\r\n', b'\n')
        sha1sum = hashlib.sha1(content).hexdigest()
        log.info(f'-i- DCF_check: {dcf_file_path} SHA1: {sha1sum}')

        return {'file': dcf_file_path, 'sha1': sha1sum}

    def dcf_registry_boms(self):
        """
        Parse DCF registry to check if it has 4 columns, separated by comma.
        Returns a tuple containing:
        1. Dictionary with BOM group names as keys and their revision lists as values
        2. Dictionary with BOM group names as keys and their SHA values

        Returns:
            tuple: (dict: {BOMGroup_name: [rev1, rev2, ...]}, dict: {BOMGroup_name: sha})
        """
        registry_file = f'{self.tpobj.tpldir}/Shared/BaseInputs/Common/Common_Files/DCF_Registry.txt'
        dcf_registry_bom_groups = defaultdict(list)
        dcf_registry_bom_sha = {}

        # Parse each line
        for line in File(registry_file).chomp(strip=True, comment='#'):
            # Split by comma
            columns = line.split(',')

            # Check if line has exactly 4 columns
            if len(columns) != 4:
                self.add_error(
                    276, 'BASE',
                    f"File does not have complete data, it should have BOMGroup, "
                    f"Devrevstep, DCF sha and Package/Assembly#: {line}")
                continue

            # Extract BOM group, revision step, and SHA
            bom_group = columns[0].strip()
            rev_step = columns[1].strip()
            dcf_sha = columns[2].strip()

            # Add to BOM-revision mapping (avoid duplicates)
            if rev_step not in dcf_registry_bom_groups[bom_group]:
                dcf_registry_bom_groups[bom_group].append(rev_step)

            # Add to BOM-SHA mapping (store the SHA for each BOM group)
            if dcf_sha and bom_group not in dcf_registry_bom_sha:
                dcf_registry_bom_sha[bom_group] = dcf_sha

        log.info(f'-i- DCF_check: DCF BOM Groups: {dict(dcf_registry_bom_groups)}')
        log.info(f'-i- DCF_check: DCF BOM to SHA mapping: {dcf_registry_bom_sha}')
        return dict(dcf_registry_bom_groups), dcf_registry_bom_sha

    def main(self):
        """
        main checking function that calls the other functions to perform the DCF compliance check.
        """

        log.info('-i- DCF_check: Start checking for DCF Registry compliance')

        # Get BOM data from both sources
        binmatrix_dic = self.binmatrix_boms()
        dcf_registry_dic, dcf_registry_bom_sha = self.dcf_registry_boms()

        # Check if dcf_registry_boms returned empty (file not found or parsing error)
        if not dcf_registry_dic:
            log.info('-i- DCF_check: Failed to retrieve BOM data from DCF Registry file')
            self.add_error(276, 'BASE', 'Failed to retrieve BOM data from DCF Registry file')
            return

        # First check: BinMatrix devrevsteps should be in DCF Registry and SHA should match for each BOM
        for bom_group, devrevsteps in binmatrix_dic.items():

            # Get DCF file and SHA1 for this specific BOM group
            dcf_file = self.dcf_file(bom_group)
            if not dcf_file or 'sha1' not in dcf_file:
                log.info(f'-i- DCF_check: Failed to retrieve SHA1 information from DCF file for BOM Group "{bom_group}"')
                self.add_error(276, 'BASE', f'Failed to retrieve SHA1 information from DCF file for BOM Group "{bom_group}"')
                continue

            calculated_sha = dcf_file['sha1']
            # check if BOMGroup exists in DCF_Registry.txt
            if bom_group not in dcf_registry_dic:
                log.info(f'-i- DCF_check: BOM Group "{bom_group}" not found in DCF Registry')
                self.add_error(276, 'BASE', f'BOM Group "{bom_group}" found in BinMatrix but missing in DCF Registry')
            else:
                # check for each devrestep
                dcf_devrevsteps = dcf_registry_dic[bom_group]

                for devrevstep in devrevsteps:
                    if devrevstep not in dcf_devrevsteps:
                        log.info(
                            f'-i- DCF_check: Devrevstep "{devrevstep}" for BOM '
                            f'"{bom_group}" not found in DCF Registry')
                        self.add_error(
                            276, 'BASE',
                            f'Devrevstep "{devrevstep}" found in BinMatrix but '
                            f'missing in DCF Registry')

                # SHA comparison for this specific BOM group
                if bom_group in dcf_registry_bom_sha:
                    expected_sha = dcf_registry_bom_sha[bom_group]
                    if calculated_sha == expected_sha:
                        log.info(
                            f'-i- DCF_check: SHA1 {calculated_sha} matches for '
                            f'BOM Group "{bom_group}"')
                    else:
                        log.info(
                            f'-i- DCF_check: SHA1 mismatch for BOM Group '
                            f'"{bom_group}". Expected: {expected_sha}, '
                            f'Found: {calculated_sha}')
                        self.add_error(
                            276, 'BASE',
                            f'SHA1 mismatch for BOM Group "{bom_group}". '
                            f'Expected: {expected_sha}, Found: {calculated_sha}')
                else:
                    log.info(f'-i- DCF_check: No SHA found in DCF Registry for BOM Group "{bom_group}"')
                    self.add_error(276, 'BASE', f'No SHA found in DCF Registry for BOM Group "{bom_group}"')

        if not self.result:
            log.info('-i- DCF_check: All BOM Groups, Devrevsteps, and SHAs match')
            self.add_pass(276, 'BASE')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    dcf_check(TestProgram(sys.argv[1]).pickle_init()).run()
