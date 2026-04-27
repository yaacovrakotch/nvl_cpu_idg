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
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.pseudo_vmin_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestPseudoVminChecker(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_VminTestWithParamsSetAndNotSet(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        data = [('ARR', 'NOT_A_VMIN_TEST',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: 'some_setting', PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: 'NOT_CORRECT.USERVASRNAME',
                  'config_set': 'some_setting', 'TEMPLATE': 'Shops'}),
                ('ARR', 'VMIN_TEST_IN_SCOREBOARD',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: 'some_setting', PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: 'NOT_CORRECT.USERVASRNAME',
                  'config_set': 'some_setting', 'TestMode': 'FUNC', 'TEMPLATE': 'VminTC'}),
                ('ARR', 'VMIN_TEST_IN_SEARCH_BUT_NOT_USING_VMINFORWARDING',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: 'some_setting', PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: 'NOT_CORRECT.USERVASRNAME',
                  'config_set': 'some_setting', 'TestMode': 'MultiVmin', 'ForwardingMode': 'Output', 'TEMPLATE': 'VminTC'}),
                ('ARR', 'MBISTVMIN_TEST_WITH_PARAMETERS_NOT_SET_CORRECTLY',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: 'some_setting', PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: 'NOT_CORRECT.USERVASRNAME',
                  'config_set': 'some_setting', 'TestMode': 'MultiVmin', 'ForwardingMode': 'InputOutput', 'TEMPLATE': 'MbistVmin'}),
                ('ARR', 'VMIN_TEST_WITH_PARAMETERS_NOT_SET_CORRECTLY',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: 'some_setting', PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: 'NOT_CORRECT.USERVASRNAME',
                  'config_set': 'some_setting', 'TestMode': 'SingleVmin', 'ForwardingMode': 'Input', 'TEMPLATE': 'VminTC'}),
                ('ARR', 'VMIN_TEST_WITH_PARAMETERS_SET_CORRECTLY',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: PseudoVminChecker.START_VOLTAGES_RETRY_VALUE, PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: PseudoVminChecker.START_VOLTAGES_OFFSETS_VALUE,
                  'config_set': 'some_setticd q ng', 'TestMode': 'SingleVmin', 'ForwardingMode': 'InputOutput', 'TEMPLATE': 'VminTC'}),
                ('ARR', 'VMIN_TEST_WITH_PARAMETERS_SET_CORRECTLY_MULTI',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: PseudoVminChecker.START_VOLTAGES_RETRY_VALUE_MULTI, PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: PseudoVminChecker.START_VOLTAGES_OFFSETS_VALUE_MULTI,
                  'config_set': 'some_setticd q ng', 'TestMode': 'SingleVmin', 'ForwardingMode': 'InputOutput', 'TEMPLATE': 'VminTC'}),
                ('ARR', 'VMIN_TEST_WITH_PARAMETERS_SET_CORRECTLY_MO',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: PseudoVminChecker.START_VOLTAGES_RETRY_VALUE_MO, PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: PseudoVminChecker.START_VOLTAGES_OFFSETS_VALUE_MO,
                  'config_set': 'some_setticd q ng', 'TestMode': 'SingleVmin', 'ForwardingMode': 'InputOutput', 'TEMPLATE': 'VminTC'}),
                ('ARR', 'MBISTVMIN_TEST_WITH_PARAMETERS_SET_CORRECTLY_F5',
                 {PseudoVminChecker.START_VOLTAGES_RETRY_PARAM: PseudoVminChecker.START_VOLTAGES_RETRY_VALUE_F5, PseudoVminChecker.START_VOLTAGES_OFFSETS_PARAM: PseudoVminChecker.START_VOLTAGES_OFFSETS_VALUE_F5,
                  'config_set': 'some_setticd q ng', 'TestMode': 'MultiVmin', 'ForwardingMode': 'Input', 'TEMPLATE': 'VminTC'})]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = PseudoVminChecker(tpobj)
            obj.main()

        # check results, one fail and one pass
        print(obj.result)

        result = [{'message': 'MBISTVMIN_TEST_WITH_PARAMETERS_NOT_SET_CORRECTLY needs to set StartVoltagesForRetry to __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "") or with F* added to the end.',
                   'id': 253,
                   'module': 'ARR'},
                  {'message': 'MBISTVMIN_TEST_WITH_PARAMETERS_NOT_SET_CORRECTLY needs to set StartVoltagesOffset to __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "") or with F* added to the end.',
                   'id': 253,
                   'module': 'ARR'},
                  {'message': 'VMIN_TEST_WITH_PARAMETERS_NOT_SET_CORRECTLY needs to set StartVoltagesForRetry to __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "") or with F* added to the end.',
                   'id': 253,
                   'module': 'ARR'},
                  {'message': 'VMIN_TEST_WITH_PARAMETERS_NOT_SET_CORRECTLY needs to set StartVoltagesOffset to __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "") or with F* added to the end.',
                   'id': 253,
                   'module': 'ARR'}]
        print(result)
        self.maxDiff = None
        self.assertEqual(obj.result, result)
        self.assertEqual(obj.passed, {(253, 'ARR'): 8})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
