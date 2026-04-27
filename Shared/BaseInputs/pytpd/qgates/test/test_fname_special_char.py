#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for fname_special_char.py
"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.fname_special_char import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from pprint import pprint


class TestFnameSpecialChar(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = FnameSpecialChar(tpobj)
        obj.main()

        # check results, one fail and one pass
        self.assertEqual(obj.result, [{'message': 'File: [./Shared/IP_CPU_BASE/IP_CPU_BASE - Backup.ipctproj] has an invalid char in the name!',
                                       'id': 194,
                                       'module': 'BASE'},
                                      {'message': 'File: [./Shared/IP_PCH_BASE/IP_PCH_BASE - Backup.ipctproj] has an invalid char in the name!',
                                       'id': 194,
                                       'module': 'BASE'}])
        self.assertEqual(len(obj.passed), 9)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
