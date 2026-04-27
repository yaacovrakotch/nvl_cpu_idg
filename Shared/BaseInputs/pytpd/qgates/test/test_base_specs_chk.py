#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for template_common.py

Steps:
1. For module qgate, remove "qgates." in "from qgates." since py file and unitest are on the same folder.
2. Replace TestCheckerNameHere to the name of the checker class
3. Run coverage and see what code is not tested
4. To run, execute this file "test_template_common.py -v"

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.base_specs_chk import *        # replace this with your checker py.
# import qgates.base_specs_chk as base_specs
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestCheckerNameHere(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_return_dict_value(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        base_specs_file = f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test/Shared/Package_Shared/BaseSpecs.usrv'
        obj = BaseSpecChecker(tpobj)
        test_dict_value = obj.get_spec_vars(base_specs_file)
        self.assertEqual(test_dict_value, {'GT_F5_FREQ_Max': '1.8', 'GT_F6_FREQ_Max': '2.2', 'GT_F5_FREQ_Min': '1.8', 'GT_F6_FREQ_Last': '2.2', 'CR_F6_FREQ_First': '4.1'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_pass(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = BaseSpecChecker(tpobj)
        obj.main()
        self.assertEqual(obj.passed, {(226, 'BASE'): 4})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_fail(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = BaseSpecChecker(tpobj)
        obj.main()
        error_message = [{'message': 'In /intel/tpvalidation/engtools/tptools/mtl/unittests/Qgate_base_specs_chk/ARL_60B_test/Shared/Package_Shared/BaseSpecs.usrv, GT_F5_FREQ_Min has value of 1.8 which does NOT meet the Min value of GT_F5_FREQ in /intel/tpvalidation/engtools/tptools/mtl/unittests/Qgate_base_specs_chk/ARL_60B_test/Shared/Package_Shared/BinMatrix.flm.usrv.', 'id': 226, 'module': 'BASE'},
                         {'message': 'In /intel/tpvalidation/engtools/tptools/mtl/unittests/Qgate_base_specs_chk/ARL_60B_test/Shared/Package_Shared/BaseSpecs.usrv, GT_F6_FREQ_Last has value of 2.2 which does NOT meet the Last value of GT_F6_FREQ in /intel/tpvalidation/engtools/tptools/mtl/unittests/Qgate_base_specs_chk/ARL_60B_test/Shared/Package_Shared/BinMatrix.flm.usrv.', 'id': 226, 'module': 'BASE'},
                         {'message': 'In /intel/tpvalidation/engtools/tptools/mtl/unittests/Qgate_base_specs_chk/ARL_60B_test/Shared/Package_Shared/BaseSpecs.usrv, CR_F6_FREQ_First has value of 4.1 which does NOT meet the First value of CR_F6_FREQ in /intel/tpvalidation/engtools/tptools/mtl/unittests/Qgate_base_specs_chk/ARL_60B_test/Shared/Package_Shared/BinMatrix.flm.usrv.', 'id': 226, 'module': 'BASE'}]
        self.assertEqual(obj.result, error_message)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
