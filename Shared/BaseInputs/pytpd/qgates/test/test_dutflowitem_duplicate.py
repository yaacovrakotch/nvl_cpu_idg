#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for dutflowitem_duplicate.py

"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.dutflowitem_duplicate import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from pprint import pprint
import shutil


class TestDFI(TestCase):

    def test_basic(self):

        with TempDir(name=True, chdir=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple3'
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpobj = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')

            text = '''
DUTFlow MAIN1  {
        DUTFlowItem CCA CCA {
                Result 0 { }
        }
        DUTFlowItem CCB CCB {
                Result 0 { }
        }
        DUTFlowItem CCB CCB1 {
                Result 0 { }
        }
        #   DUTFlowItem CCC CCB1 {
        #        Result 0 { }
        # }
}
'''
            File('TPL/Modules/ARR/array.mtpl').touch(text, mkdir=True, newfile=True)
            obj = DFIDup(tpobj)
            obj.main()

        # check results, one fail and one pass
        self.assertEqual(obj.result, [{'id': 222,
                                       'message': 'DUTFlowItem CCB is duplicated!',
                                       'module': 'ARR'},
                                      {'id': 223,
                                       'message': 'Commented DUTFlowItem is not allowed: [#   DUTFlowItem CCC CCB1 {]',
                                       'module': 'ARR'}])
        self.assertEqual(obj.passed, {(222, 'ARR'): 2,
                                      (222, 'PTH'): 4,
                                      (222, 'SCN'): 4,
                                      (223, 'PTH'): 1,
                                      (223, 'SCN'): 1})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
