#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for dup_tname
"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.dup_tname import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar


class TestDupTestName(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_uniq(self):
        tpobj = (TestProgram(f'{UT_DIR}/SimpleMTL_jning2/POR_TP/Class_MTL_P28/EnvironmentFile.env'))
        obj = DuplicateTestName(tpobj)
        obj.main()

        # check results
        print(obj.result)
        self.assertEqual(obj.result, [{'message': "ARR_ATOM_CXX has duplicated test: {'ALL_ATOM_AUX_E_EDCAT_080808_VATOM_VNOM_0800_VMINREP_FLAGY'}",
                                       'id': 238,
                                       'module': 'ARR_ATOM_CXX'}])
        self.assertEqual(obj.passed, {(238, 'ARR_COMMON_C28'): 1})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
