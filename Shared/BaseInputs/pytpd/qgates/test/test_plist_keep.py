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
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest/')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.plist_keep import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestPListKeep(TestCase):

    def test_basic(self):
        # Passing case - simple4a's keep tags are as expected
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4a/POR_TP/TGLH81/EnvironmentFile.env').init()
        print(f'{UT_DIR_REPO}')
        obj = PListKeep(tpobj)
        obj.main()
        self.assertEqual(obj.result, [])                     # expected errors added - should be none
        self.assertEqual(obj.passed, {(241, 'ARR'): 3, (241, 'PTH'): 2, (241, 'SCN'): 2, (242, 'ALL'): 2})
        # Failing case - Simple4a's keep tags are messed up - malformed AND some repeating TIDs/patterns
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4a_keep/POR_TP/TGLH81/EnvironmentFile.env').init()
        print(f'{UT_DIR_REPO}')
        obj = PListKeep(tpobj)
        obj.main()
        self.assertEqual(obj.result, [{'message': '#KEEP missing trailing # in cpu_fuse_read_special_x - Pat g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1', 'id': 242, 'module': 'SCN'},
                                      {'message': '#KEEP missing trailing # in cpu_fuse_read_special_x - Pat g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1', 'id': 242, 'module': 'PTH'},
                                      {'message': '#KEEP# TID also appears without keep in cpu_fuse_read_hvm_x - TID 2371433', 'id': 241, 'module': 'PTH'},
                                      {'message': '#KEEP# Pattern also appears without keep in cpu_fuse_read_special_x - Pat g2026526W2371465I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_nom', 'id': 241, 'module': 'SCN'},
                                      {'message': '#KEEP# TID also appears without keep in cpu_fuse_read_special_x - TID 2371465', 'id': 241, 'module': 'PTH'},
                                      {'message': '#KEEP# TID also appears without keep in cpu_fuse_read_special_x - TID 2371465', 'id': 241, 'module': 'PTH'}])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
