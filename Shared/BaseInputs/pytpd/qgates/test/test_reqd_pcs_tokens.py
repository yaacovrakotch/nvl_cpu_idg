#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for reqd_pcs_tokens.py

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
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests

from qgates.reqd_pcs_tokens import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestReqdPcsToken(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_eng_tp_skipped(self):
        tpobj = TestProgram(f'{UT_DIR}/torch_mvtp/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env')
        obj = ReqPCSTokens(tpobj)
        self.assertEqual(obj.main(), 1)    # skipped

    def test_basic_fail(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4a/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = ReqPCSTokens(tpobj)
        self.assertEqual(obj.main(), 2)

        # check results, one fail and one pass
        print(obj.result)
        expect = [{'message': 'PTH module missing PrimeThermalSingleMeasurementTestMethod template to generate PCS_SOT, PCS_TJRISE, PSC_TJDROOP and PCS_DTSMAX required tokens',
                   'id': 214,
                   'module': 'BASE'},
                  {'message': 'PTH module missing PrimeLogPcsTokensTestMethod template to generate PCS_SKTCN and PCS_SKTRP required tokens',
                   'id': 215,
                   'module': 'BASE'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(obj.passed, {})   # no passing

    def test_basic_pass(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4a/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = ReqPCSTokens(tpobj)
        data = [('PTH_DTS_CXX', 'test_instance1', {'TEMPLATE': 'PrimeThermalSingleMeasurementTestMethod'}),
                ('ARR', 'test_instance2', {'TEMPLATE': 'VMinTC'}),
                ('PTH_DTS_CXX', 'test_instance3', {'TEMPLATE': 'PrimeLogPcsTokensTestMethod'})]

        with MockVar(tpobj.mtpl, 'iter_flows', Mock(return_value=data)):
            obj.main()

        # check results, one fail and one pass
        print(obj.result)
        self.assertEqual(obj.result, [])
        self.assertEqual(obj.passed, {(214, 'BASE'): 2,
                                      (215, 'BASE'): 2})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
