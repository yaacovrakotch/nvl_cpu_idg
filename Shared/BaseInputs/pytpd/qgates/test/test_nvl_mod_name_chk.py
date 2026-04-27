#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_mod_name_chk.py

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests

from qgates.nvl_mod_name_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class ModNameChk(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        data = ['/blah/ARR_VICOY_GK40/a.mtpl',
                '/blah/SCN_AAAAAAAA_PKPKGHX/a.mtpl',
                '/blah/TPI_SHOPS_XXS/a.mtpl',
                '/blah/AA/a.imp',
                '/blah/ProgramFlowsTestPlan/a.imp',
                'Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl"']
        with MockVar(tpobj, "get_all_mtpl_from_stpl", Mock(return_value=data)):
            print("Running basic")
            obj = ModName(tpobj)
            obj.main()
            # pprint(obj.result)
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 3)    # 6 is 6 flows * 1 pass (TEST2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mocked_case(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env')
        data = ['/blah/ARR_VICOY_GK408/a.mtpl',
                '/blah/SCN_AAAAAAAAA_PKGHX/a.mtpl',
                '/blah/TPI_SHOPS_XXY/a.mtpl']
        with MockVar(tpobj, "get_all_mtpl_from_stpl", Mock(return_value=data)):
            print("Running mocked case")
            obj = ModName(tpobj)
            obj.main()
            # pprint(obj.result)
        xpect = [{'id': 217,
                  'message': 'The 3rd field ("_GK408_") of ARR_VICOY_GK408 uses these invalid '
                             'characters 408 (from 3rd char).  Please see wiki for correct '
                             'values',
                  'module': 'ARR_VICOY_GK408'},
                 {'id': 217,
                  'message': 'The 2nd field of SCN_AAAAAAAAA_PKGHX should have a max of 8 '
                             'chars only',
                  'module': 'SCN_AAAAAAAAA_PKGHX'},
                 {'id': 217,
                  'message': 'The 3rd field ("_XXY_") of TPI_SHOPS_XXY uses these invalid '
                             'characters Y (from 3rd char).  Please see wiki for correct '
                             'values',
                  'module': 'TPI_SHOPS_XXY'}]
        pprint(obj.result)
        self.assertEqual(obj.result, xpect)
        self.assertEqual(len(obj.passed), 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mocked_case2(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env')
        dat1 = [('ARR', 'FlowControl'),
                ('SCN_AAAAAAAAA_PKGHX', 'TestFail'),
                ('YBS_AAA_PKGHX_MORE', 'WithLowercase'),
                ('CLK_aaAA_PKGHX', 'WithLowercase'),
                ('CLKKA_AAAA_PKGHX', 'WithLowercase'),
                ('VIC_AAAA_CKPKGHX', 'TestFail'),
                ('FUS_AAAA_CKPKGHXXX', 'TestFail'),
                ('DRV_AAAA_X', 'TestFail'),
                ('DRV_AAAA_XXAX', 'TestFail'),
                ('TPI_SHOPS_XXX', 'TEST2')]
        data = [f'/blah/{x[0]}/a.mtpl' for x in dat1]
        with MockVar(tpobj, "get_all_mtpl_from_stpl", Mock(return_value=data)):
            print("Running mocked case2")
            obj = ModName(tpobj)
            obj.main()
        pprint(obj.result)
        xpect = [{'id': 217,
                  'message': 'ARR contains no other Fields (XXX_XXX_XXX).  Please fix',
                  'module': 'ARR'},
                 {'id': 217,
                  'message': 'The 2nd field of SCN_AAAAAAAAA_PKGHX should have a max of 8 '
                             'chars only',
                  'module': 'SCN_AAAAAAAAA_PKGHX'},
                 {'id': 217,
                  'message': 'YBS_AAA_PKGHX_MORE should have 3 underscore separated fields no '
                             'more no less',
                  'module': 'YBS_AAA_PKGHX_MORE'},
                 {'id': 217,
                  'message': 'CLK_aaAA_PKGHX not following correct naming convention. no lowercase or special char.',
                  'module': 'CLK_aaAA_PKGHX'},
                 {'id': 217,
                  'message': 'The 1st field of CLKKA_AAAA_PKGHX should have a max of 4 chars '
                             'only',
                  'module': 'CLKKA_AAAA_PKGHX'},
                 {'id': 217,
                  'message': 'The 1st field of VIC_AAAA_CKPKGHX not using fixed list of valid '
                             'team. If new please ask TPI to add in valid list',
                  'module': 'VIC_AAAA_CKPKGHX'},
                 {'id': 217,
                  'message': 'The 3rd field of FUS_AAAA_CKPKGHXXX should have a max of 8 chars '
                             'only',
                  'module': 'FUS_AAAA_CKPKGHXXX'},
                 {'id': 217,
                  'message': 'The 3rd field of DRV_AAAA_X "_X_" not following convention. '
                             'Please see wiki',
                  'module': 'DRV_AAAA_X'}]
        self.assertEqual(obj.result, xpect)
        self.assertEqual(len(obj.passed), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
