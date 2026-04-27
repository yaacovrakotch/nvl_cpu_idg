#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_supersedes_readme_chk.py
This will check if there are any DLL files in the supersede folder.
"""
import sys
from setenv_unittest import UT_DIR_REPO, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.nvl_supersedes_readme_chk import *
from gadget.ut import TestCase, unittest
from gadget.gizmo import with_
from gadget.files import TempDir
from unittest.mock import Mock, patch
from tp.testprogram import TestProgram
import os


class TestNvlSupersedesReadmeChk(TestCase):

    def test_main_dll_count_zero_pass(self):  # Test main() DLL count check passes when no DLLs exist
        tpobj = Mock()
        tpobj.shareddir = '/fake/shared'
        obj = SuperSedesReadmeChk(tpobj)

        with patch('glob.glob', return_value=[]):  # No DLLs
            obj.main()

        # QGate275 should pass with 0 DLLs
        self.assertIn((275, 'BASE'), obj.passed)

    def test_main_dll_count_zero_fail(self):  # Test main() DLL count check fails when any DLL exists
        tpobj = Mock()
        tpobj.shareddir = '/fake/shared'
        obj = SuperSedesReadmeChk(tpobj)

        with patch('glob.glob', return_value=['/fake/shared/First.dll']):
            obj.main()

        error_found = any('maximum allowed is 0' in err['message'] and err['id'] == 275 for err in obj.result)
        self.assertTrue(error_found)

    def test_main_dll_count_multiple_dlls(self):  # Test main() DLL count check fails when multiple DLLs exist
        tpobj = Mock()
        tpobj.shareddir = '/fake/shared'
        obj = SuperSedesReadmeChk(tpobj)

        with patch('glob.glob', return_value=['/fake/shared/First.dll', '/fake/shared/Second.dll', '/fake/shared/Third.dll']):
            obj.main()

        error_found = any('Found 3 supersede DLLs' in err['message'] and err['id'] == 275 for err in obj.result)
        self.assertTrue(error_found)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_main_integration(self):  # Integration test for main() method
        test_env = f'POR_TP/TGLH81/EnvironmentFile.env'

        tpobj = TestProgram(test_env)
        obj = SuperSedesReadmeChk(tpobj)
        obj.main()

        # Verify that main produced results
        expect = '''
(275, 'BASE'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
