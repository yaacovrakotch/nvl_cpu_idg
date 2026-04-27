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
    from setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.uppercase_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestUpperCase(TestCase):

    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = UpperCase_Mod(tpobj)
        obj.main()

        # check results, one fail and one pass

        expect = [{'id': 112,
                   'message': 'Upper Case check failed for Test: '
                   'TPI_PRESI_XXX::CTRL_X_PLISTConfig_K_START_X_X_X_X_DTSPATTENREMOVE',
                   'module': 'CTRL_X_PLISTConfig_K_START_X_X_X_X_DTSPATTENREMOVE'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 39)

    def test_mocked_case(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env')
        data = [('ARR', 'FlowControl'),
                ('ARR', 'TestFail'),
                # ('IP_CPU_BASE', 'WithLowercase'),
                ('Arr', 'TEST2')]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = UpperCase_Mod(tpobj)
            obj.main()
        uniq = set(x['message'] for x in obj.result)
        self.assertEqual(uniq, {'Upper Case check failed for Module: Arr',
                                'Upper Case check failed for Test: ARR::TestFail'})
        self.assertEqual(obj.passed, {(112, 'ARR'): 6,     # 6 is 6 flows * 1 pass (ARR)
                                      (112, 'Arr'): 6})    # 6 is 6 flows * 1 pass (TEST2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
