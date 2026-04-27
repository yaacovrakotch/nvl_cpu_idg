#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for soc_infra_chk

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.soc_infra_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestSocInfra(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_pass_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = SocInfra(tpobj)
        obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_fail(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A_2/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = SocInfra(tpobj)
        obj.main()
        expect = [{'id': 133,
                   'message': 'Required Infra Test '
                              'RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT BYPASSED OR '
                              'NOT FOUND!',
                   'module': 'DRV_RESET_SXN'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
