#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Run unnittest for nvl_shared_main_only.py
"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE      # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from unittest.mock import Mock
import os
from qgates.nvl_shared_main_only import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog


class SharedMainOnlyCheck(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_pass(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = SharedMainOnly(tpobj)
        from_pr = {'FROM_PR': 'True'}
        output = """  origin/FUS/FUSECFG_COMMON/JW
  origin/HEAD -> origin/main
  origin/TPI/level_ww15
  origin/main
"""
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, output))), \
                MockVar(SharedMainOnly, 'return_sha_shared', Mock(return_value="ac5c16d754962b65208aa023b50db28449dc3c4d")), \
                MockVar(os, 'environ', from_pr):
            obj.main()
            self.assertEqual(obj.passed, {(247, 'BASE'): 1})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_real(self):
        tpobj = TestProgram(f'{UT_DIR}/nvl.cpu/POR_TP/Class_NVL_S28C/EnvironmentFile.env')
        with MockVar(os.environ, 'FROM_PR', 'True'):
            QGateExecute.repodir = f'{UT_DIR}/nvl.cpu'
            obj = SharedMainOnly(tpobj)
            obj.main()
            print(obj.result)
            self.assertEqual(obj.result, [{'message': 'Cannot get correct sha of Modules/TPI. Result: []', 'id': 247, 'module': 'BASE'}])

            # coverage
            with TempDir(chdir=True):
                self.assertEqual(list(obj.get_target_folders()), [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_fail(self):
        QGateExecute.repodir = f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed'
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        output = """  origin/FUS/FUSECFG_COMMON/JW
  origin/TPI/level_ww15
"""
        error_message = [{'id': 247, 'message': 'Shared submodule is NOT from the MAIN branch.', 'module': 'BASE'}]
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, output))), \
                MockVar(SharedMainOnly, 'return_sha_shared', Mock(return_value="ac5c16d754962b65208aa023b50db28449dc3c4d")), \
                MockVar(os.environ, 'FROM_PR', 'True'):

            # Fail case
            obj = SharedMainOnly(tpobj)
            obj.main()
            self.assertEqual(obj.result, error_message)

            # Not from PR
            with MockVar(os.environ, 'FROM_PR', 'False'):
                self.assertEqual(obj.main(), 1)

        # not valid sha
        with MockVar(os.environ, 'FROM_PR', 'True'):
            obj = SharedMainOnly(tpobj)
            obj.main()
            print(obj.result)
            self.assertEqual(obj.result, [{'message': 'Cannot get correct sha of Shared. Result: [fatal:]', 'id': 247, 'module': 'BASE'}])

        # (+) sha
        with MockVar(os.environ, 'FROM_PR', 'True'),\
                MockVar(SharedMainOnly, 'return_sha_shared', Mock(return_value="+ac5c16d754962b65208aa023b50db28449dc3c4d")):
            obj = SharedMainOnly(tpobj)
            obj.main()
            print(obj.result)
            self.assertEqual(obj.result, [])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
