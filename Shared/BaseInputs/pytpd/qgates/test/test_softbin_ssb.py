#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for softbin_ssb
"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.softbin_ssb import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import qgates.softbin_ssb as softbin_ssb


class TestSoftbinSSB(TestCase):

    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4a/POR_TP/TGLH81/EnvironmentFile.env')
        obj = SoftBinSSB(tpobj)
        obj.main()

        # check results
        print(obj.result)
        self.assertEqual(obj.result, [{'message': '90757604 does not follow SSB convention: 90HBHBxx. b90757604_fail_some_softbin',
                                       'id': 219,
                                       'module': 'ARR'}])
        self.assertEqual(obj.passed, {(219, 'ARR'): 5,
                                      (219, 'PTH'): 5})

    def test_uniq(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4a/POR_TP/TGLH81/EnvironmentFile.env')
        obj = SoftBinSSB(tpobj)
        with TempDir(name=True) as tdir:
            File(f'{tdir}/a.mtpl').touch('''
SetBin SoftBins.b90989801_fail_OK;
SetBin SoftBins.b90989701_fail_INVALID;
SetBin SoftBins.b90989701_fail_INVALID;
SetBin SoftBins.b90989601_fail_INVALID;
SetBin SoftBins.b10989601_fail_INVALID;
''')
            obj.check_arl(f'{tdir}/a.mtpl')

        # check results
        self.assertEqual(len(obj.result), 2)
        self.assertEqual(obj.passed, {(219, 'BASE'): 1})

    def test_basic2(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4b/POR_TP/TGLH81/EnvironmentFile.env')
        obj = SoftBinSSB(tpobj)
        obj.main()
        print(obj.result)

        expect = [{'id': 219,
                   'message': '60757501 does not follow SSB convention: 90HBHBxx. '
                   'b60757501_fail_NSIO',
                   'module': 'ARR'},
                  {'id': 219,
                   'message': '50757503 does not follow SSB convention: 90HBHBxx. '
                   'b50757503_fail_some_common_SHARED_BIN',
                   'module': 'ARR'},
                  {'id': 219,
                   'message': '90757604 does not follow SSB convention: 90HBHBxx. '
                   'b90757604_fail_some_softbin',
                   'module': 'ARR'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 2)

    def test_basic_nvl(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4b/POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        obj = SoftBinSSB(tpobj)
        obj.main()

        with TempDir(name=True) as tdir:
            File(f'{tdir}/a.mtpl').touch('''
        SetBin b60757501_fail_OK;
        SetBin b50757503_fail_INVALID;
        SetBin b90757604_fail_INVALID;
        ''')
            obj.check_nvl(f'{tdir}/a.mtpl')
        # pprint(obj.result)

        expect = [{'id': 219,
                   'message': '60757501 does not follow SSB convention: 90HBxxxx. '
                   'b60757501_fail_OK',
                   'module': 'BASE'},
                  {'id': 219,
                   'message': '50757503 does not follow SSB convention: 90HBxxxx. '
                   'b50757503_fail_INVALID',
                   'module': 'BASE'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
