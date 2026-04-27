#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for initlastmodule_chk.py

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
from qgates.initlastmodule_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class InitLastModuleCodeCheck(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = InitLastModuleCheck(tpobj)
        obj.main()
        # Passing case using integ 2A test program
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    def test_failing_case(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple5/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = InitLastModuleCheck(tpobj)
        obj.main()
        # Failing case using simple5 test program
        expect = [{'id': 229,
                   'message': 'PTH can not be at last of INIT flow, TPI_END need to be at the '
                   'end.',
                   'module': 'PTH'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
