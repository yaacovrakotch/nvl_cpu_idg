#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for pgmrule_chk.py

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.pgmrule_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestPGMRule(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = PgmRule(tpobj)
        obj.main()
        pprint(obj.result)

        # check results, one fail and one pass

        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_fail(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A_2/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = PgmRule(tpobj)
        obj.main()
        # pprint(obj.result)

        # check results, one fail and one pass

        expect = [{'id': 120,
                   'message': 'PGMrule test:CTRL_X_GLX_K_INIT_X_X_X_X_BASEPGMRULE with action '
                   'on param|test combo: PRIMARY_OPTYPE__UserVars does not have '
                   'default ALL/ALL_CLASS setting',
                   'module': 'TPI_BASE_XXX'},
                  {'id': 120,
                   'message': 'PGMrule test:SHOPS_X_GLX_K_INIT_X_X_X_X_LIMITS with action on '
                   'param|test combo: '
                   'pins_TPI_SHOPS_XXX::SHOPS_X_SHOPSDC_K_START_X_X_X_X_PKGUPPERDIODEP '
                   'does not have default ALL/ALL_CLASS setting',
                   'module': 'TPI_SHOPS_XXX'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
