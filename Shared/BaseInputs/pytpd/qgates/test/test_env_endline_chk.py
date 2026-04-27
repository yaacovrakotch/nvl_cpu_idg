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

from qgates.env_endline_chk import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import os
from pprint import pformat


class EnvCheckTest(TestCase):

    def test_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple5/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvEndLineCheck(tpobj)
        obj.main()

        # Passing case using Simple5 test program
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 2)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_failing_case(self):
        os.remove('POR_TP/TGLH81/EnvironmentFile.env')
        # Mock-up failing cases Env file with ;" at end of a line.
        # Or split with "; + between values.
        File(f'{UT_DIR_REPO}/envchk_unittest/EnvironmentFileUnitTest.env').copy('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = EnvEndLineCheck(tpobj)
        obj.main()

        expect = r'''
[{'id': 234,
  'message': 'TP_TOS       = "HDMTOS_3.6.1.7_Release;" in ENV file line 10 '
             'should end with ";',
  'module': 'ENV'},
 {'id': 233,
  'message': '"I:\\hdmxpats\\tgl\\MarrMbist\\RevTTR0.3\\p2\\plb\\slim"; + in '
             'ENV file line 15 should spilt with ;" + between values.',
  'module': 'ENV'},
 {'id': 234,
  'message': '"I:\\program\\1274\\eng\\hdmtpats\\tgl\\Mwio\\RevTTR0.0\\p0\\pat\\indv_bin;" '
             'in ENV file line 443 should end with ";',
  'module': 'ENV'}]
'''
        self.assertTextEqual(pformat(obj.result), expect)
        self.assertEqual(len(obj.passed), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
