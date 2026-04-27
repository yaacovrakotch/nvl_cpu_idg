#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for onlyonededc_chk.py, using mocking instead of touching the filesystem.
"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.bypassrules_chk import *        # replace this with your checker py.
from gadget.files import TempDir
from unittest.mock import Mock
from gadget.ut import TestCase, unittest
from gadget.gizmo import with_, MockVar
from tp.testprogram import TestProgram


class TestBypassRulesChk(TestCase):
    def test_split_args_single_case(self):
        args = BypassRulesChk._split_args("1")
        expect = ['1']
        self.assertEqual(args, expect)

    def test_split_args_simple_case(self):
        args = BypassRulesChk._split_args("-1, 2, 1")
        expect = ['-1', '2', '1']
        self.assertEqual(args, expect)

    def test_split_args_nested_case(self):
        args = BypassRulesChk._split_args("1, If_ENG(If_Cold(-1, 2),1), 1")
        expect = ['1', 'If_ENG(If_Cold(-1, 2),1)', '1']
        self.assertEqual(args, expect)

    def test_is_rule_call_true_case(self):
        Bool = BypassRulesChk._is_rule_call("TpRule.If_ENG(2, 1)")
        self.assertTrue(Bool)

    def test_is_rule_call_false_case(self):
        Bool = BypassRulesChk._is_rule_call("TpRule.If_ENG")
        self.assertFalse(Bool)

    def test_safe_eval_literal_case(self):     # is this needed? bcs literal_eval is python built-in
        value = BypassRulesChk._safe_eval("2")
        self.assertEqual(value, 2)

    def test_safe_eval_non_literal_case(self):     # is this needed? bcs literal_eval is python built-in
        value = BypassRulesChk._safe_eval('SCN_GT_GXX.FORCE_NON_RV_RUN')
        self.assertEqual(value, 'SCN_GT_GXX.FORCE_NON_RV_RUN')

    def test_single_level_rule(self):
        fake_rule_dict = {
            'TpRule.RuleX': ['condA', 'condB']
        }
        fake_call = 'TpRule.RuleX("1", "-1")'
        expected = {
            'condA': "1",
            'condB': "-1"
        }
        result = BypassRulesChk._raw_mapping(fake_call, fake_rule_dict)
        self.assertEqual(result, expected)

    def test_nested_level_rule(self):
        fake_rule_dict = {
            'TpRule.RuleX': ['condA', 'condB'],
            'TpRule.RuleY': ['condC', 'condD']
        }
        fake_call = 'TpRule.RuleX(TpRule.RuleY("1", "-1"), "2")'
        expected = {
            'condC': "1",
            'condD': "-1",
            'condB': "2"
        }
        result = BypassRulesChk._raw_mapping(fake_call, fake_rule_dict)
        self.assertEqual(result, expected)

    def test_final_map_with_locsets_all_and_exclusion(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7/POR_TP/TGLH81/EnvironmentFile.env').init()
        chk = BypassRulesChk(tpobj)
        fake_usrv_map = {
            'LocationSets.ALL_CLASS': '["5274:PHMCOLD","6248:CLASSCOLD"]',
            'LocationSets.PHM': '["5274:PHMCOLD"]',
            'LocationSets.COLD': '["6248:CLASSCOLD"]'
        }
        with MockVar(tpobj.usrv, "get_usrv_map", Mock(return_value=fake_usrv_map)):
            with MockVar(chk, "_extract_zq_locn", Mock(return_value={"inst1": {"PHM": 1, '""': 0}})):
                chk._final_map_with_locsets()

        expected = {"inst1": {'"5274:PHMCOLD"': 1, '"6248:CLASSCOLD"': 0}}
        self.assertDictEqual(chk.final_mapping, expected)

    def test_no_rules_case(self):
        obj = BypassRulesChk(TestProgram(f'{UT_DIR_REPO}/Simple7/POR_TP/TGLH81/EnvironmentFile.env').init())
        obj.main()
        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True, delete=True)
    def test_no_default_condition_in_rule_case(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        fake_src_orig = {
            "XXX_Rules": {
                "XXX_Rule.Fake_Name": [
                    'contains(LocationSets_ZQ_PHM,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]")',
                    'contains(LocationSets_ZQ_COLD,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]")']}}
        fake_iter_test = [('ARR_CORE_CXX',
                           'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502',
                           {'BypassPort': 'XXX_Rule.Fake_Name(1,-1)'},
                           None)]
        fake_usrv_map = {
            'LocationSets.ALL_CLASS': '["5274:PHMCOLD","6248:CLASSCOLD","7820:CLASSHOT"]',
            'LocationSets.PHM': '["5274:PHMCOLD"]',
            'LocationSets.COLD': '["6248:CLASSCOLD"]'
        }
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=fake_iter_test)):
            with MockVar(tpobj.usrv, "_src_orig", fake_src_orig):
                with MockVar(tpobj.usrv, 'get_usrv_map', Mock(return_value=fake_usrv_map)):
                    obj = BypassRulesChk(tpobj)
                    obj.main()
        expect = [{'id': 262, 'module': 'base',
                   'message': 'ARR_CORE_CXX:CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502: '
                              'bypasses PHM/COLD in TosRule, need change to FSM'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True, delete=True)
    def test_bypass_in_PHM_COLD_case(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        fake_src_orig = {
            "XXX_Rules": {
                "XXX_Rule.Fake_Name": [
                    'contains(LocationSets_ZQ_PHM,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]")',
                    '']}}
        fake_iter_test = [('ARR_CORE_CXX', 'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502',
                           {'BypassPort': 'XXX_Rule.Fake_Name(1,-1)'}, None)]
        fake_usrv_map = {
            'LocationSets.ALL_CLASS': '["5274:PHMCOLD","6248:CLASSCOLD"]',
            'LocationSets.PHM': '["5274:PHMCOLD"]',
            'LocationSets.COLD': '["6248:CLASSCOLD"]'
        }
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=fake_iter_test)):
            with MockVar(tpobj.usrv, "_src_orig", fake_src_orig):
                with MockVar(tpobj.usrv, 'get_usrv_map', Mock(return_value=fake_usrv_map)):
                    obj = BypassRulesChk(tpobj)
                    obj.main()
        expect = [{'id': 262, 'module': 'base',
                   'message': 'ARR_CORE_CXX:CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502: '
                              'bypasses PHM/COLD in TosRule, need change to FSM'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True, delete=True)
    def test_bypass_not_in_PHM_COLD_case(self):     # happy path
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
        fake_src_orig = {
            "XXX_Rules": {
                "XXX_Rule.Fake_Name": [
                    'contains(LocationSets_ZQ_PHM,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]")',
                    '']}}
        fake_iter_test = [('ARR_CORE_CXX',
                           'CA2TF_ATOM_VMAX_Y_CPUINIT_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502',
                           {'BypassPort': 'XXX_Rule.Fake_Name(1,-1)'},
                           None)]
        fake_usrv_map = {
            'LocationSets.ALL': '["5274:PHMHOT","6248:CLASSCOLD"]',
            'LocationSets.HOT': '["5274:PHMHOT"]',
            'LocationSets.COLD': '["6248:CLASSCOLD"]'
        }
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=fake_iter_test)):
            with MockVar(tpobj.usrv, "_src_orig", fake_src_orig):
                with MockVar(tpobj.usrv, 'get_usrv_map', Mock(return_value=fake_usrv_map)):
                    obj = BypassRulesChk(tpobj)
                    obj.main()
                    expect = []
                    self.assertEqual(obj.result, expect)
                    self.assertEqual(len(obj.passed), 1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
