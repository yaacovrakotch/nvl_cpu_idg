#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_dll_check.py
"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.nvl_dll_check import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
import os


class TestDllCheck(TestCase):

    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/SimpleNVL6/POR_TP/Class_NVL_H81/EnvironmentFile.env')
        obj = DllChecker(tpobj)
        with TempDir(name=True, chdir=True) as tdir:
            dll_dir = f'{tdir}/UserCode/lib/Release/net6.0'
            os.makedirs(dll_dir)
            # create 3 dummy dll files
            for i in range(3):
                File(f'{dll_dir}/dummy{i}.dll').touch('')
            obj.main()
            self.assertEqual(obj.passed, {(271, 'DLL Check passes'): 1})

    def test_fail(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/SimpleNVL6/POR_TP/Class_NVL_H81/EnvironmentFile.env')
        obj = DllChecker(tpobj)
        with TempDir(name=True, chdir=True) as tdir:
            dll_dir = f'{tdir}/UserCode/lib/Release/net6.0'
            os.makedirs(dll_dir)
            # create only 2 dummy dll files to trigger failure
            for i in range(2):
                File(f'{dll_dir}/dummy{i}.dll').touch('')
            obj.main()
            self.assertEqual(obj.result, [{'message': 'No dll files found in the UserCode dir. Please re-run TPBuild to ensure fresh copy of the UserCode dir', 'id': 271, 'module': 'DLL Check Fail'}])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
