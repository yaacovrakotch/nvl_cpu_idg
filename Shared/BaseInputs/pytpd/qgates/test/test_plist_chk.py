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
    from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/gen1')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/gen1')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.plist_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class PlistCodeCheck(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_case(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = PListCheck(tpobj)
        obj.main()

        # Passing case using integ 2A test program
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mocked_case1(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        # Mock the case-sensitive failing case.
        data = [('DRV_RESET_GXX', 'RESET_X_FUNC_E_BEGGT_X_INF_X_X_A0_DEBUG_HASH_BYPASS_BBS_PRIME', {'TEMPLATE': 'DDGFunctionalTC', 'patlist': 'drv_GDIE_a0debughashbypass_bbs_list'}, {999: 'n90190020_fail_RESET_X_FUNC_E_BEGGT_X_INF_X_X_A0_DEBUG_HASH_BYPASS_BBS_PRIME_0'})]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = PListCheck(tpobj)
            obj.main()
        expect = [{'id': 225,
                   'message': 'drv_GDIE_a0debughashbypass_bbs_list is missing',
                   'module': 'DRV_RESET_GXX'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mocked_case2(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        # Mock the passing case with .mtpl plist name perfect matching with loaded plist name.
        data = [('DRV_RESET_GXX', 'RESET_X_FUNC_E_BEGGT_X_INF_X_X_A0_DEBUG_HASH_BYPASS_BBS_PRIME', {'TEMPLATE': 'DDGFunctionalTC', 'patlist': 'drv_gdie_a0debughashbypass_bbs_list'}, {999: 'n90190020_fail_RESET_X_FUNC_E_BEGGT_X_INF_X_X_A0_DEBUG_HASH_BYPASS_BBS_PRIME_0'})]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = PListCheck(tpobj)
            obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    def test_mocked_case3(self):
        # test most cases
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7').init()
        # Mock the passing case with .mtpl plist name perfect matching with loaded plist name.
        data = [('DRV_RESET_GXX', 'RESET_1', {'TEMPLATE': 'DDGFunctionalTC', 'patlist': ''}, {999: 'n90190020'}),
                ('DRV_RESET_GXX', 'RESET_2', {'TEMPLATE': 'DDGFunctionalTC', 'Plist': ''}, {999: 'n90190020'}),
                ('DRV_RESET_GXX', 'RESET_3', {'TEMPLATE': 'DDGFunctionalTC', 'patlist': 'shops_L_list'}, {999: 'n90190020'}),
                ('DRV_RESET_GXX', 'RESET_4', {'TEMPLATE': 'DDGFunctionalTC', 'Plist': 'shops_L_list'}, {999: 'n90190020'}),
                ('DRV_RESET_GXX', 'RESET_3', {'TEMPLATE': 'DDGFunctionalTC', 'patlist': 'shops_L_missing1'}, {999: 'n90190020'}),
                ('DRV_RESET_GXX', 'RESET_4', {'TEMPLATE': 'DDGFunctionalTC', 'Plist': 'shops_L_missing2'}, {999: 'n90190020'})]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = PListCheck(tpobj)
            obj.main()
        expect = '''
225 DRV_RESET_GXX RESET_1 has empty patlist
225 DRV_RESET_GXX RESET_2 has empty Plist
225 DRV_RESET_GXX shops_L_missing1 is missing
225 DRV_RESET_GXX shops_L_missing2 is missing
(225, 'BASE'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
