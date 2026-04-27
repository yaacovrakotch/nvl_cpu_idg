#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Run unnittest for b69_validator.py
Checking simple pass and fail cases.

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.b69_validator import *        # replace this with your checker py.
# import qgates.base_specs_chk as base_specs
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class B69Check(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_pass(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        b69_tool = '/intel/engineering/dev/team_classtp/torch/validators/Bin69/Bin69.exe'
        obj = Bin69Validator(tpobj)
        output = "BASE                      pass count=1"
        return_df = {"TPI_BASE_XXX::TPI_BASE_XXX_ALARM": {'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN': {999: 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN',
                                                                                                -2: {'PassFail': 'Fail', 'SetBin': 'b90990101_fail_FAIL_DPS_ALARM', 'Return': '1'},
                                                                                                -1: {'PassFail': 'Fail', 'SetBin': 'b90980101_fail_FAIL_SYSTEM_SOFTWARE', 'Return': '1'},
                                                                                                0: {'PassFail': 'Fail', 'SetBin': 'b90930115_fail_TPI_BASE_XXX_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE_XXX::n93010023_fail_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN_0', 'Return': '0'},
                                                                                                1: {'PassFail': 'Pass', 'Return': '1'},
                                                                                                2: {'PassFail': 'Pass', 'Return': '1'},
                                                                                                3: {'PassFail': 'Fail', 'SetBin': 'b90930115_fail_TPI_BASE_XXX_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE_XXX::n93010024_fail_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN_3', 'Return': '0'}},
                                                          '_ORDER': ['CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN']}}
        with MockVar(Bin69Validator, "bin69_tool", Mock(return_value=b69_tool)), \
                MockVar(Bin69Validator, "return_dutflow", Mock(return_value=return_df)), \
                MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))):
            obj.main()
            self.assertEqual(obj.passed, {(281, 'BASE'): 1})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_fail(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = Bin69Validator(tpobj)
        b69_tool = '/intel/engineering/dev/team_classtp/torch/validators/Bin69/Bin69.exe'
        output = "Bin 69 - The Module passes units with a bad bin assignment. The route starts at 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN'"
        return_df = {"TPI_BASE_XXX::TPI_BASE_XXX_ALARM": {'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN': {999: 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN',
                                                                                                -2: {'PassFail': 'Fail', 'SetBin': 'b90990101_fail_FAIL_DPS_ALARM', 'Return': '1'},
                                                                                                -1: {'PassFail': 'Fail', 'SetBin': 'b90980101_fail_FAIL_SYSTEM_SOFTWARE', 'Return': '1'},
                                                                                                0: {'PassFail': 'Fail', 'SetBin': 'b90930115_fail_TPI_BASE_XXX_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE_XXX::n93010023_fail_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN_0', 'Return': '0'},
                                                                                                1: {'PassFail': 'Pass', 'Return': '1'},
                                                                                                2: {'PassFail': 'Pass', 'Return': '1'},
                                                                                                3: {'PassFail': 'Fail', 'SetBin': 'b90930115_fail_TPI_BASE_XXX_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE_XXX::n93010024_fail_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN_3', 'Return': '0'}},
                                                          '_ORDER': ['CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN']}}
        with MockVar(Bin69Validator, "bin69_tool", Mock(return_value=b69_tool)), \
                MockVar(Bin69Validator, "return_dutflow", Mock(return_value=return_df)), \
                MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, output))):
            obj.main()
            error_message = [
                {'message': 'Bin 69 - The Module passes units with a bad bin assignment. The route starts at \'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN\'', 'id': 281, 'module': 'TPI_BASE_XXX'}
            ]
            self.assertEqual(obj.result, error_message)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_fail_system(self):
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        b69_tool = '/intel/engineering/dev/team_classtp/torch/validators/Bin69/Bin69.exe'
        obj = Bin69Validator(tpobj)
        output = "There are issues with running B69 Validator. Please check with TPI."
        return_df = {"TPI_BASE_XXX::TPI_BASE_XXX_ALARM": {'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN': {999: 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN',
                                                                                                -2: {'PassFail': 'Fail', 'SetBin': 'b90990101_fail_FAIL_DPS_ALARM', 'Return': '1'},
                                                                                                -1: {'PassFail': 'Fail', 'SetBin': 'b90980101_fail_FAIL_SYSTEM_SOFTWARE', 'Return': '1'},
                                                                                                0: {'PassFail': 'Fail', 'SetBin': 'b90930115_fail_TPI_BASE_XXX_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE_XXX::n93010023_fail_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN_0', 'Return': '0'},
                                                                                                1: {'PassFail': 'Pass', 'Return': '1'},
                                                                                                2: {'PassFail': 'Pass', 'Return': '1'},
                                                                                                3: {'PassFail': 'Fail', 'SetBin': 'b90930115_fail_TPI_BASE_XXX_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE_XXX::n93010024_fail_CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN_3', 'Return': '0'}},
                                                          '_ORDER': ['CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN']}}
        with MockVar(Bin69Validator, "bin69_tool", Mock(return_value=b69_tool)), \
                MockVar(Bin69Validator, "return_dutflow", Mock(return_value=return_df)), \
                MockVar(SystemCall, 'run_outtxt', Mock(return_value=(32154875, output))):
            obj.main()
            error_message = [
                {'message': 'There are issues with running B69 Validator. Please check with TPI.', 'id': 248, 'module': 'BASE'}
            ]
            self.assertEqual(obj.result, error_message)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
