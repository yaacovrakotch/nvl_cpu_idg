#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for dupl_env_var.py
"""
import sys

try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests

from qgates.dupl_env_var import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import os
import shutil


class TestDupEnvVar(TestCase):

    def test_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple5/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = DupEnvVar(tpobj)
        obj.main()
        pprint(obj.result)

        # Passing case using Simple5 test program
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    def test_failing_case(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple7c'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(envfile).init()
            print("Running test_failing_case...")
            obj = DupEnvVar(tpobj)
            obj.main()
            expect = [{'id': 206,
                       'message': 'OASIS_TPL_DIR is redefined in env. Cannot redefine.',
                       'module': 'Base'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
