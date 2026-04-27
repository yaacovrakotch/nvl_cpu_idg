#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Run unnittest for duplicate_bindef.py
"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from unittest.mock import Mock
import os
from qgates.duplicate_bindef import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from gadget.disk import Chdir
from gadget.pylog import log


class DuplicateBindefCheck(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_fail(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = Duplicate_Bindef(tpobj)
        with Chdir(f'{UT_DIR}/subbindef_reduce_test'):
            module_list = glob.glob(f'Modules/*/*.mtpl')
            mtpl_obj = {}
            for item in module_list:
                mtpl_obj[f'XXX_{item}'] = item
            log.info(f"Module list: {mtpl_obj}")
            error_message = [
                {'message': f'Duplicate bindef found: 9028 in [\'CLK_BASE_CX816P\', \'CLK_BASE_HXNVL\']', 'id': 252, 'module': 'CLK_BASE_CX816P'},
                {'message': f'Duplicate bindef found: 90992815 in [\'CLK_BASE_CX816P\', \'CLK_BASE_HXNVL\']', 'id': 252, 'module': 'CLK_BASE_CX816P'}
            ]
            with MockVar(Duplicate_Bindef, "return_mod_fname", Mock(return_value=mtpl_obj)):
                obj.main()
                self.assertEqual(obj.result, error_message)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_pass(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = Duplicate_Bindef(tpobj)
        with Chdir(f'{UT_DIR}/subbindef_reduce3_test'):
            module_list = glob.glob(f'Modules/*/*.mtpl')
            mtpl_obj = {}
            for item in module_list:
                mtpl_obj[f'XXX_{item}'] = item
            log.info(f"Module list: {mtpl_obj}")
            with MockVar(Duplicate_Bindef, "return_mod_fname", Mock(return_value=mtpl_obj)):
                obj.main()
                self.assertEqual(obj.passed, {(252, 'BASE'): 1})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
