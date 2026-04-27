#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for env_endline_chk.py

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

from qgates.tppatch_rev_chk import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import os


class TPPatchRevChkTest(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_passing_case(self):
        os.remove('Shared/BaseInputs/UservarDefinitions.usrv')
        # Mock-up passing case using Simple5 test program
        File(f'{UT_DIR_REPO}/envchk_unittest/UservarDefinitions.usrv').copy('Shared/BaseInputs/UservarDefinitions.usrv')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = TPPatchRevCheck(tpobj)
        obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_failing_case1(self):
        os.remove('Shared/BaseInputs/UservarDefinitions.usrv')
        # Mock-up failing case1 - TP name is shorter than 19 digits.
        File(f'{UT_DIR_REPO}/envchk_unittest/UservarDefinitions_short.usrv').copy(
            'Shared/BaseInputs/UservarDefinitions.usrv')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = TPPatchRevCheck(tpobj)
        obj.main()
        expect = [{'id': 235,
                   'message': 'Current Test Program name ARLHC27A0H60A0S328 does NOT follow 19 '
                              'characters standard naming convention.',
                   'module': 'BASE'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_failing_case2(self):
        os.remove('Shared/BaseInputs/UservarDefinitions.usrv')
        # Mock-up failing case2 - TP patch rev is 8 which beyond 7.
        File(f'{UT_DIR_REPO}/envchk_unittest/UservarDefinitions_patch8.usrv').copy(
            'Shared/BaseInputs/UservarDefinitions.usrv')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = TPPatchRevCheck(tpobj)
        obj.main()
        expect = [{'id': 235,
                   'message': 'Current Test Program patch rev is 8 which CAN NOT beyond 7.',
                   'module': 'BASE'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
