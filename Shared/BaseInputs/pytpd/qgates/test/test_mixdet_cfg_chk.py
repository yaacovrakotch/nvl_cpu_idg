#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for mixdet_cfg_chk
"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.mixdet_cfg_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import shutil


class TestMixDetCfg(TestCase):

    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7k/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = MixDetCfg(tpobj)
        obj.main()
        # pprint(obj.result)
        # check results, one fail and one pass

        expect = [{'id': 221,
                   'message': 'SCN is using "STSORT" in DFFTokenList in '
                              './Modules/SCN/InputFiles/configurationFile_P68_Pass.mdet.json. '
                              'Please update to use "SORT"',
                   'module': 'SCN'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    def test_basic2(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7j/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = MixDetCfg(tpobj)
        obj.main()
        # pprint(obj.result)
        # check results, one fail and one pass

        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
