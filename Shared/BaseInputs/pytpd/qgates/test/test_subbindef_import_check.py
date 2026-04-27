#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for programflow_chk.py

"""
import sys
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.subbindef_import_check import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import patch, Mock
from gadget.gizmo import with_, MockVar
from gadget.shell import TarAdd
from tp.testprogram import TestProgram
from gadget.pylog import log
import os
import glob


class SubbindefImportTest(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/nvl_testprogram_release/NVLXXXXAXH01A0BSXXX', chdir=True, delete=True)
    def test_basic(self):

        # Modify the subbindef files for a smaller testcase
        subbindef_files = (glob.glob(f'BaseInputs/*/*_Files/*_SubBindef.imp') +
                           glob.glob(f'/Shared/BaseInputs/Common/Common_Files/*_SubBindef.imp'))
        for file_path in subbindef_files:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Keep only first 4 lines (or create 4 new lines)
            if len(lines) >= 4:
                new_lines = lines[:4]  # Keep first 4 lines
            else:
                new_lines = lines + ['# Additional line\n'] * (4 - len(lines))  # Pad to 4 lines

            with open(file_path, 'w') as f:
                f.writelines(new_lines)

        # Start testing from here
        tpobj = TestProgram(f'POR_TP/Class_NVL_S28C/EnvironmentFile.env')
        obj = SubbindefImportChk(tpobj)
        # case: No complete.tar.gz file
        # Mock the File.read method to return predefined values
        obj.main()
        expect = [{'id': 260, 'message': 'complete_tp.tar.gz does not exist', 'module': 'BASE'}]
        self.assertEqual(obj.result, expect)

        # case: with complete tar, there is diff as expected
        TarAdd('complete_tp.tar.gz', '.', exclude=['.git', 'temp'])
        obj = SubbindefImportChk(tpobj)
        obj.main()

        expect = [{'id': 260,
                   'message': 'SubBindef module TPI_GFXAGG_GXX not found in tpproj file',
                   'module': 'BASE'},
                  {'id': 260,
                   'message': 'SubBindef module TPI_FLWFLGS_GXX not found in tpproj file',
                   'module': 'BASE'},
                  {'id': 260,
                   'message': 'SubBindef module DRV_RESET_HXX not found in tpproj file',
                   'module': 'BASE'},
                  {'id': 260,
                   'message': 'SubBindef module FUS_FUSECFG_HXX not found in tpproj file',
                   'module': 'BASE'},
                  {'id': 260,
                   'message': 'SubBindef module TPI_PWRCTRL_PXX not found in tpproj file',
                   'module': 'BASE'}]
        self.assertEqual(obj.result, expect)

        # Pass case: if the subbindef file is present in the tpproj
        obj = SubbindefImportChk(tpobj)
        File(f'BaseInputs/CPU/CPU_Files/IPC_SubBindef_new.imp').touch('''
Import "../../Modules/DRV_RESET_CXX/DRV_RESET_CXX_SubBinDefinitions.sbdefs";
''', mkdir=True)
        with MockVar(SubbindefImportChk, 'return_subbindef_files', Mock(return_value=[f'{os.getcwd()}/BaseInputs/CPU/CPU_Files/IPC_SubBindef_new.imp'])):
            obj.main()
        expect = {(260, 'BASE'): 1}
        self.assertEqual(obj.passed, expect)


if __name__ == '__main__':
    unittest.main()
