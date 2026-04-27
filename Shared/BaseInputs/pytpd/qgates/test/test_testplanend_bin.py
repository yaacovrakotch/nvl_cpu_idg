#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for testplanend_bin.py

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.testplanend_bin import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestTPEBin(TestCase):

    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = TestPlaneEndCheck(tpobj)
        obj.main()
        pprint(obj.result)

        # check results, one fail and one pass

        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 5)

    def test_basic_fail(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A_2/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = TestPlaneEndCheck(tpobj)
        obj.main()

        # check results, one fail and one pass

        expect = [{'id': 220,
                   'message': 'Softbin 6905 found in RCSlist, please remove. TestName: '
                              'TPI_BASE_XXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_CHECKFLAG, '
                              'port: 0',
                   'module': 'TPI_BASE_XXX'},
                  {'id': 220,
                   'message': 'Softbin 6905 found in RCSlist, please remove. TestName: '
                              'TPI_BASE_XXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_CHECKFLAG, '
                              'port: 2',
                   'module': 'TPI_BASE_XXX'},
                  {'id': 220,
                   'message': 'Softbin 6905 found in RCSlist, please remove. TestName: '
                              'TPI_BASE_XXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_CHECKFLAG, '
                              'port: 3',
                   'module': 'TPI_BASE_XXX'},
                  {'id': 220,
                   'message': 'Softbin 9428 found in RCSlist, please remove. TestName: '
                              'TPI_BASE_XXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_REJECTFORK, '
                              'port: 0',
                   'module': 'TPI_BASE_XXX'},
                  {'id': 220,
                   'message': 'Softbin 9428 found in RCSlist, please remove. TestName: '
                              'TPI_BASE_XXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_REJECTFORK, '
                              'port: 3',
                   'module': 'TPI_BASE_XXX'},
                  {'id': 220,
                   'message': 'Softbin 9428 found in RCSlist, please remove. TestName: '
                              'TPI_DEDCHIST_YXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_REJECTFORK, '
                              'port: 0',
                   'module': 'TPI_DEDCHIST_YXX'},
                  {'id': 220,
                   'message': 'Softbin 9428 found in RCSlist, please remove. TestName: '
                              'TPI_DEDCHIST_YXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_REJECTFORK, '
                              'port: 3',
                   'module': 'TPI_DEDCHIST_YXX'},
                  {'id': 220,
                   'message': 'Softbin 9383 found in RCSlist, please remove. TestName: '
                              'TPI_IDUTRCS_XXX/CTRL_X_SCREEN_K_TESTPLANENDFLOW_X_X_X_X_DISABLEPARALLEL, '
                              'port: 0',
                   'module': 'TPI_IDUTRCS_XXX'},
                  {'id': 220,
                   'message': 'Softbin 8907 found in RCSlist, please remove. TestName: '
                              'TPI_END_XXX/CTRL_X_BKGND_K_TESTPLANENDFLOW_X_X_X_X_STOPTIME, '
                              'port: -3',
                   'module': 'TPI_END_XXX'},
                  {'id': 220,
                   'message': 'Softbin 9346 found in RCSlist, please remove. TestName: '
                              'TPI_END_XXX/CTRL_X_BKGND_K_TESTPLANENDFLOW_X_X_X_X_STOPTIME, '
                              'port: 0',
                   'module': 'TPI_END_XXX'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 5)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
