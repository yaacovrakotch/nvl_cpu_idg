#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for env_pat_case.py
"""
import sys

try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE  # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE  # must be first import for unittests

from qgates.env_pat_case import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import os


class TestEnvPatCase(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR}/Simple5pat/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvPatCase(tpobj)
        obj.main()

        # Passing case using Simple5 test program
        expect = []
        self.assertEqual(obj.result, expect)
        print(obj.passed)
        self.assertEqual(obj.passed, {(314, 'NA'): 25})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/Simple5pat', chdir=True, delete=True)
    def test_failing_case(self):
        os.remove('POR_TP/TGLH81/EnvironmentFile.env')
        # Mock-up failing cases Env file with ;" at end of a line.
        # Or split with "; + between values.
        File(f'{UT_DIR}/envchk_unittest/EnvironmentFilePatCase1a.env').copy('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvPatCase(tpobj)
        obj.main()
        # pprint(obj.result)
        expect = [{'id': 314,
                   'message': '.env file hdmxpats rev case-mismatch for Mclk: RevTTr0.1 does '
                              'not exist. Please fix case name of the rev.',
                   'module': 'NA'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/Simple5pat', chdir=True, delete=True)
    def test_failing_case2(self):
        os.remove('POR_TP/TGLH81/EnvironmentFile.env')
        # Mock-up failing cases Env file with ;" at end of a line.
        # Or split with "; + between values.
        File(f'{UT_DIR}/envchk_unittest/EnvironmentFilePatCase2a.env').copy('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvPatCase(tpobj)
        obj.main()
        pprint(obj.result)
        expect = [{'id': 314,
                   'message': '.env file hdmxpats rev case-mismatch for Mclk: RevTTr0.1 does '
                              'not exist. Please fix case name of the rev.',
                   'module': 'NA'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
