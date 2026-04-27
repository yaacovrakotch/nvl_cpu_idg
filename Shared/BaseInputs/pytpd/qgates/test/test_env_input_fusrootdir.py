#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for env_input_fusrootdir.py

Steps:
1. For module qgate, remove "qgates." in "from qgates." since py file and unitest are on the same folder.
2. Replace TestCheckerNameHere to the name of the checker class
3. Run coverage and see what code is not tested
4. To run, execute this file "test_template_common.py -v"

"""
import sys

try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests

from qgates.env_input_fusrootdir import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import os
from pprint import pformat


class EnvInputFusRootDirTest(TestCase):

    def test_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple5/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvInputFusRootDir(tpobj)
        obj.main()

        # Passing case using Simple5 test program
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_failing_case(self):
        os.remove('POR_TP/TGLH81/EnvironmentFile.env')
        # Mock-up failing cases Env file with ;" at end of a line.
        # Or split with "; + between values.
        File(f'{UT_DIR_REPO}/envchk_unittest/EnvironmentFileEnvInputFusRootDirTest.env').copy('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvInputFusRootDir(tpobj)
        obj.main()

        expect = r'''
279 ENV FUSE_ROOT_DIR_CPU_INT: I:/fuse/release/NVL/CPU_Int/CPU_A0_25WW26P0 is missing definition from HDMT_TPL_INPUT_FILES var.
279 ENV FUSE_ROOT_DIR_G64: I:/fuse/release/NVL/PIXE3H_64EU/nvlgcd_a0_24ww46e_presi_25WW12 is missing definition from HDMT_TPL_INPUT_FILES var.
279 ENV FUSE_ROOT_DIR_G32: I:/fuse/release/NVL/PIXE3S_32EU/PIXE3S_A0_25ww25PO_PLL is missing definition from HDMT_TPL_INPUT_FILES var.
(279, 'BASE'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_failing_case1(self):
        os.remove('POR_TP/TGLH81/EnvironmentFile.env')
        # Mock-up special failing cases to filter out ALEPH file.
        File(f'{UT_DIR_REPO}/envchk_unittest/FailCaseEnvInputFusRootDirTest.env').copy('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvInputFusRootDir(tpobj)
        obj.main()

        expect = r'''
279 ENV FUSE_ROOT_DIR_CPU_INT: I:/fuse/release/NVL/CPU_Int/CPU_A0_25WW26P0 is missing definition from HDMT_TPL_INPUT_FILES var.
279 ENV FUSE_ROOT_DIR_G64: I:/fuse/release/NVL/PIXE3H_64EU/nvlgcd_a0_24ww46e_presi_25WW12 is missing definition from HDMT_TPL_INPUT_FILES var.
279 ENV FUSE_ROOT_DIR_G32: I:/fuse/release/NVL/PIXE3S_32EU/PIXE3S_A0_25ww25PO_PLL is missing definition from HDMT_TPL_INPUT_FILES var.
(279, 'BASE'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
