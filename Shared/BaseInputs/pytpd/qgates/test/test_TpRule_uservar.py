#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for test_TPRule_uservar.py
"""
import sys
try:
    from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.TpRule_uservar import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from gadget.gizmo import with_


class TestUsrVar(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_failcase(self):

        tpobj = TestProgram(f'{UT_DIR}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        obj = TpRuleUservar(tpobj)
        obj.main()
#        pprint(obj.result)
        self.assertEqual(obj.result, [{'message': 'file /intel/tpvalidation/engtools/tptools/mtl/unittests/Simple6/POR_TP/TGLH81/../../Modules/ARR/array.usrv: '
                                                  'line: 9, SelectorRuleCollection BootUp, has bootup not allowed.',
                                       'id': 232, 'module': 'ARR'},
                                      {'message': 'file /intel/tpvalidation/engtools/tptools/mtl/unittests/Simple6/POR_TP/TGLH81/../../Modules/PTH/pth.usrv: '
                                                  'line: 9, SelectorRuleCollection BootUp, has bootup not allowed.',
                                       'id': 232, 'module': 'PTH'}])
#        pprint(obj.passed)
        self.assertEqual(obj.passed, {})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_basic_passcase(self):
        File('Shared/BaseInputs/UservarDefinitions.usrv').touch('''
SelectorRuleCollection newBootUp
{
        SelectorRule IfBom1(bom1, bom2)
        {
                bom1 => SCVars.SC_DEVICE == "4TXNCV";
                bom2 => SCVars.SC_DEVICE == "4TXNBV";
        }
}
''', newfile=True)

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        obj = TpRuleUservar(tpobj)
        obj.main()
        pprint(obj.result)
        self.assertEqual(obj.result, [])   # no errors
        self.assertEqual(obj.passed, {(232, 'ARR'): 1,
                                      (232, 'PTH'): 1})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_basic_errorcase(self):
        File('Shared/BaseInputs/UservarDefinitions.usrv').touch('''
SelectorRule BootUp
{
        SelectorRule IfBom1(bom1, bom2)
        {
                bom1 => SCVars.SC_DEVICE == "4TXNCV";
                bom2 => SCVars.SC_DEVICE == "4TXNBV";
        }
}
''', newfile=True)

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        obj = TpRuleUservar(tpobj)
        obj.main()
        pprint(obj.result)
        self.assertEqual(obj.result, [])   # no errors
        self.assertEqual(obj.passed, {(232, 'ARR'): 1,
                                      (232, 'PTH'): 1})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
