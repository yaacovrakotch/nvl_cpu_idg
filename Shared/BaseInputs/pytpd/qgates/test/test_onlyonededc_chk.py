#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for onlyonededc_chk.py, using mocking instead of touching the filesystem.
"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.onlyonededc_chk import *        # replace this with your checker py.
from gadget.files import TempDir
from unittest.mock import Mock
from gadget.ut import TestCase, unittest
from gadget.gizmo import with_, MockVar
from tp.testprogram import TestProgram


class TestOnlyOneDEDC(TestCase):

    def test_no_dedc_case(self):
        obj = OnlyOneDEDC(TestProgram(f'{UT_DIR_REPO}/Simple7/POR_TP/TGLH81/EnvironmentFile.env').init())
        obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True, delete=True)
    def test_one_dedc_in_tpi_case(self):
        testcase = [
            ('TPI_DEDC_XXX', 'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502',
                {'TEMPLATE': 'DedcRVCallbackTC'}, None)]
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = OnlyOneDEDC(tpobj)
            obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True, delete=True)
    def test_one_dedc_not_in_tpi_case(self):
        testcase = [
            ('ARR_CORE_CXX', 'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502',
                {'TEMPLATE': 'DedcRVCallbackTC'}, None)]
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = OnlyOneDEDC(tpobj)
            obj.main()
        expect = [{'id': 254, 'module': 'base',
                  'message': 'Found 1 occurrences of "DedcRVCallbackTC", '
                             'expect only one and exists in TPI module only. '
                             'Remove this TMM in your module if you see this error.'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True, delete=True)
    def test_more_than_one_dedc_case(self):
        testcase = [
            ('ARR_CORE_CXX', 'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502',
                {'TEMPLATE': 'DedcRVCallbackTC'}, None),
            ('TPI_DEDC_XXX', 'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502',
                {'TEMPLATE': 'DedcRVCallbackTC'}, None)]
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=testcase)):
            obj = OnlyOneDEDC(tpobj)
            obj.main()
        expect = [{'id': 254, 'module': 'base',
                  'message': 'Found 2 occurrences of "DedcRVCallbackTC", '
                             'expect only one and exists in TPI module only. '
                             'Remove this TMM in your module if you see this error.'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
