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
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.empty_testinstance import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestEmptyInstance(TestCase):

    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env')

        obj = EmptyInstance(tpobj)
        obj.main()

        # check results, one fail and one pass
        self.assertEqual(obj.result, [{'id': 172,
                                       'message': 'unused is empty.',
                                       'module': 'PTH'}])
        self.assertEqual(obj.passed, {(172, 'ARR'): 4,
                                      (172, 'SCN'): 3,
                                      (172, 'PTH'): 3})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
