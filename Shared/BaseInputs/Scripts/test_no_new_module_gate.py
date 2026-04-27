#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for no_new_module_gate.py

Steps:
1. For module qgate, remove "qgates." in "from qgates." since py file and unitest are on the same folder.
2. Replace TestCheckerNameHere to the name of the checker class
3. Run coverage and see what code is not tested
4. To run, execute this file "test_template_common.py -v"

"""
import sys

try:
    from setenv_unittest import UT_DIR, ROOT_ENV  # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV  # must be first import for unittests

from qgates.no_new_module_gate import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from gadget.disk import mkdirs
from unittest.mock import Mock, patch
import os
from pprint import pformat


class NoNewModTest(TestCase):

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR}/Simple5')
    def test_passing_case(self):
        mkdirs('Shared/POR_TP/CLASS_TGLH81/SkipModules')
        File('Shared/POR_TP/CLASS_TGLH81/SkipModules/TPI_FLWFLGS_XXX.permanent').touch(mkdir=True)
        File('Shared/POR_TP/CLASS_TGLH81/SkipModules/TPI_DIESLCT_XXX.permanent').touch(mkdir=True)
        mkdirs('POR_TP/CLASS_TGLH81/SkipModules')
        File('POR_TP/CLASS_TGLH81/SkipModules/ARR.permanent').touch(mkdir=True)
        File('POR_TP/CLASS_TGLH81/SkipModules/SCN.permanent').touch(mkdir=True)
        File('POR_TP/CLASS_TGLH81/SkipModules/PTH.permanent').touch(mkdir=True)

        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = NoNewModuleGate(tpobj)
        obj.main()

        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR}/Simple5')
    def test_failing_case_die(self):
        mkdirs('Shared/POR_TP/CLASS_TGLH81/SkipModules')
        File('Shared/POR_TP/CLASS_TGLH81/SkipModules/TPI_FLWFLGS_XXX.permanent').touch(mkdir=True)
        File('Shared/POR_TP/CLASS_TGLH81/SkipModules/TPI_DIESLCT_XXX.permanent').touch(mkdir=True)
        mkdirs('POR_TP/CLASS_TGLH81/SkipModules')
        File('POR_TP/CLASS_TGLH81/SkipModules/ARR.permanent').touch(mkdir=True)
        File('POR_TP/CLASS_TGLH81/SkipModules/PTH.permanent').touch(mkdir=True)

        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = NoNewModuleGate(tpobj)
        obj.main()

        expect = r'''
[{'id': 289,
  'message': "New Module ['SCN'] is not allowed to check-in for NVL power-on "
             'time. Gate will be unlocked later.',
  'module': 'BASE'}]
'''
        self.assertTextEqual(pformat(obj.result), expect)

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR}/Simple5')
    def test_passing_case_tpi(self):
        mkdirs('Shared/POR_TP/CLASS_TGLH81/SkipModules')
        File('Shared/POR_TP/CLASS_TGLH81/SkipModules/TPI_DIESLCT_XXX.permanent').touch(mkdir=True)
        mkdirs('POR_TP/CLASS_TGLH81/SkipModules')
        File('POR_TP/CLASS_TGLH81/SkipModules/ARR.permanent').touch(mkdir=True)
        File('POR_TP/CLASS_TGLH81/SkipModules/SCN.permanent').touch(mkdir=True)
        File('POR_TP/CLASS_TGLH81/SkipModules/PTH.permanent').touch(mkdir=True)

        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = NoNewModuleGate(tpobj)
        obj.main()

        expect = []
        self.assertEqual(obj.result, expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
