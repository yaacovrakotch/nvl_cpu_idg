#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for template_common.py

Steps:
1. For module qgate, remove "qgates." in "from qgates." since py file and unitest are on the same folder.
2. Replace TestCheckerNameHere to the name of the checker class
3. Run coverage and see what code is not tested
4. To run, execute this file "test_template_common.py -v"

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest/')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.cct_qgate import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestCCTSync(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        # passing case - model in UT area should just pass - cfg file exists, mtpl matches sqlite db dict
        tpobj = TestProgram(f'{UT_DIR}/cct_qgate_test/POR_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = CCTSync(tpobj)
        obj.main()
        self.assertEqual(obj.result, [])                     # expected errors added - should be none
        self.assertEqual(obj.passed, {(218, 'xwing_goldsquad - ARR_CCF_C68 - SSA_X_VMIN_K_CCLRF1_080808_VCCR_F1_0400_1501'): 1,
                                      (218, 'xwing_bluesquad - ARR_CCF_C68 - SSA_X_VMIN_K_CCLRF1_080808_VCCR_F1_0400_1501'): 1,
                                      (218, 'xwing_goldsquad - ARR_CCF_C68 - LSA_X_VMIN_K_CCLRF1_080808_VCCR_F1_0400_1501'): 1,
                                      (218, 'xwing_bluesquad - ARR_CCF_C68 - LSA_X_VMIN_K_CCLRF1_080808_VCCR_F1_0400_1501'): 1,
                                      (218, 'xwing_goldsquad - FUN_CORE_C68 - SBFT_X_VMIN_K_CCRF1_X_VCORE_F1_0400_MLC_1501'): 1,
                                      (218, 'xwing_bluesquad - FUN_CORE_C68 - SBFT_X_VMIN_K_CCRF1_X_VCORE_F1_0400_MLC_1501'): 1,
                                      (218, 'xwing_goldsquad - ARR_ATOM_L2CXX - SSA_ATOM_VMIN_K_CATF1_X_VCCIA_F1_0400_L2DATAPMUXON_1501'): 1,
                                      (218, 'xwing_bluesquad - ARR_ATOM_L2CXX - SSA_ATOM_VMIN_K_CATF1_X_VCCIA_F1_0400_L2DATAPMUXON_1501'): 1})     # expected passes added - should be a bunch!
        # failing case - make read_cct_cfg just return true and put nonexistant instance name in cct_list - qgate should add error
        with MockVar(obj, 'read_cct_cfg', Mock(return_value=True)):
            obj.cct_list = [('xwing_goldsquad', 'ARR_CCF_C68', 'FAKEINSTANCENAME')]
            obj.main()
            self.assertEqual(obj.result, [{'id': 218,
                                           'message': 'FAKEINSTANCENAME specified in cct json for xwing_goldsquad - ARR_CCF_C68 not in program! Contact cct module owner for this TP PR.',
                                           'module': 'xwing_goldsquad - ARR_CCF_C68-FAKEINSTANCENAME'}])
        # failing case - make read_cct_cfg just return true and put nonexistant module name in cct_list - qgate should add error
        obj.result = []
        with MockVar(obj, 'read_cct_cfg', Mock(return_value=True)):
            obj.cct_list = [('xwing_goldsquad', 'FAKE_MODULE_C68', 'SSA_X_VMIN_K_CCLRF1_080808_VCCR_F1_0400_1501')]
            obj.main()
            print(obj.result)
            self.assertEqual(obj.result, [{'id': 218,
                                           'message': 'FAKE_MODULE_C68 specified in cct json for xwing_goldsquad - SSA_X_VMIN_K_CCLRF1_080808_VCCR_F1_0400_1501 not in program! Contact cct module owner for this TP PR.',
                                           'module': 'xwing_goldsquad - FAKE_MODULE_C68-SSA_X_VMIN_K_CCLRF1_080808_VCCR_F1_0400_1501'}])
        # TODO -fauling case - config file has a parameter that doesn't exist in the TP - qgate needs update
        # TODO -failing case - value in mtpl differs from what is saved in the dbdict
        # TODO -failing case - dbdict doesn't have a saved value for param added to cfg - cct_qgate_config_bad.json -
        # TODO -failing case - dbdict doesn't have a saved value for instance or module added to cfg - cct_qgate_config_bad.json -


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
