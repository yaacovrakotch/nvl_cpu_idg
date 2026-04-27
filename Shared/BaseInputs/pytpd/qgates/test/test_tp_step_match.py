#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tp_step_match.py
"""
import sys

try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests

from qgates.tp_step_match import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import os


class TPStepMatchTest(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5a', chdir=True, delete=True)
    def test_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple5a/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = TPStepMatch(tpobj)
        obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_failing_case1(self):
        os.remove('Shared/BaseInputs/UservarDefinitions.usrv')
        # Mock-up failing case1 - TP name is shorter than 19 digits.
        File(f'{UT_DIR_REPO}/envchk_unittest/UservarDefinitions_tp_step_fail1.usrv').copy(
            'Shared/BaseInputs/UservarDefinitions.usrv')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = TPStepMatch(tpobj)
        obj.main()
        expect = [{'id': 240,
                   'message': 'Stepping in RunTimeLibraryVars.iCGL_TpAltName: '
                   'ARLHC27A0H60A00S328 (8th field: "A" ) not matching '
                   'SCVars.SC_STEP: "B"',
                   'module': 'BASE'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5a', chdir=True, delete=True)
    def test_failing_case2(self):
        os.remove('Shared/BaseInputs/UservarDefinitions.usrv')
        # Mock-up failing case2 - TP patch rev is 8 which beyond 7.
        File(f'{UT_DIR_REPO}/envchk_unittest/UservarDefinitions_tp_step_fail2.usrv').copy(
            'Shared/BaseInputs/UservarDefinitions.usrv')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = TPStepMatch(tpobj)
        obj.main()
        expect = [{'id': 240,
                   'message': 'Stepping in RunTimeLibraryVars.iCGL_TpAltName: '
                              'ARLHC27B0H60A00S328 (8th field: "B" ) not matching '
                              'SCVars.SC_STEP: "A"',
                   'module': 'BASE'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
