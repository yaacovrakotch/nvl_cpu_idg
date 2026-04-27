#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for mod/alttc.py
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, MockVar, Mock
from gadget.printmore import Dumper
from mod.alttc import *
from os.path import basename
from tp.testprogram import TestProgram
from gadget.gizmo import with_
from gadget.files import TempDir
from gadget.disk import mkdirs
import os


class TestAL(TestCase):

    def test_nojson(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = ALttc(tpobj)
        self.assertEqual(obj.main(), None)    # There is no json

    def test_check_keys(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        obj = ALttc(tpobj)

        # This should pass
        obj.check_keys({'key1': 123, 'comment': 'blah'}, ['key1'], 'lttc.json')

        # This should fail
        with self.assertRaisesRegex(ErrorInput, 'is not a valid key in lttc'):
            obj.check_keys({'key1': 123, 'comment': 'blah', 'key2': 234}, ['key1'], 'lttc.json')

    def test_update_counter_block(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        obj = ALttc(tpobj)

        # test case for empty counters - do nothing
        self.assertEqual(obj.update_counter_block([], [], 'blah'), 1)

        # normal case
        lines = '''
Counters
{
    blah;
}
'''.split('\n')
        lines = [f'{x}\n' for x in lines]
        obj.update_counter_block(lines, ['counter1'], 'blah')
        expect = '''
Counters
{
        counter1,
    blah;
}

'''
        self.assertTextEqual(''.join(lines), expect)

    def test_read_module_ports(self):
        res1, res2 = ALttc.read_module_ports({'0': 'GoTo t1;',
                                              '1': 'EDC: Return 1'})
        self.assertEqual(res1, {'0': 'GoTo t1;',
                                '1': 'Return 1'})
        self.assertEqual(res2, {1: True})

        res1, res2 = ALttc.read_module_ports({'0': 'GoTo t1;',
                                              '1': 'Return 1'})
        self.assertEqual(res1, {'0': 'GoTo t1;',
                                '1': 'Return 1'})
        self.assertEqual(res2, {})

    def test_process_basenumber(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        orig = '''
Test Vmin ABC {
    bypass_global = "1";
    execution_mode = "VMIN";
    BaseNumbers = "36033";
    BaseNumbers="35";
    high_limit = "0.73";
}'''
        blocks = [f'{x}\n' for x in orig.split('\n')]
        obj = ALttc(tpobj)

        # empty first
        obj.process_basenumber(blocks, 'file.mtpl')
        expect = '''
Test Vmin ABC {
    bypass_global = "1";
    execution_mode = "VMIN";
    BaseNumbers = "96033";
    BaseNumbers="95";
    high_limit = "0.73";
}
'''
        self.assertTextEqual(''.join(blocks), expect)

    def test_process_param(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        orig = '''
Test Vmin ABC {
    bypass_global = "1";
    execution_mode = "VMIN";
    high_limit = "0.73";
}'''
        blocks = [f'{x}\n' for x in orig.split('\n')]
        obj = ALttc(tpobj)

        # empty first
        obj.process_param(blocks, {})
        expect = '''
Test Vmin ABC {
    bypass_global = "1";
    execution_mode = "VMIN";
    high_limit = "0.73";
}

'''
        self.assertTextEqual(''.join(blocks), expect)

        # updated value
        obj.process_param(blocks, {'high_limit': "abc",
                                   'execution_mode': "0.7"})
        expect = '''
Test Vmin ABC {
    bypass_global = "1";
            execution_mode = 0.7;
            high_limit = "abc";
}

'''
        self.assertTextEqual(''.join(blocks), expect)

        # TrialAction hardcode and new param
        orig = '''
Test Vmin ABC {
    bypass_global = "1";
    execution_mode = "VMIN";
    high_limit = "0.73";
    TrialAction Next;
}'''
        blocks = [f'{x}\n' for x in orig.split('\n')]
        obj.process_param(blocks, {'missingparam': "True",
                                   'missingparam2': "25",
                                   'high_limit': "7"})
        expect = '''
Test Vmin ABC {
    missingparam2 = 25;
    missingparam = "True";
    bypass_global = "1";
    execution_mode = "VMIN";
            high_limit = 7;
                        TrialAction Exit;
}

'''
        self.assertTextEqual(''.join(blocks), expect)

        # MultiTrial new param
        orig = '''
MultiTrialTest SBFT_ATOM_VMAX_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO
{
        TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_" + CustomBinMatrixSpecs.AT_F1_FREQ_MHz + "_BILBO_" + BinMatrix.bin
        {
                TrialParam EndVoltageLimits = blah;
                ExecutionMode = "SearchWithScoreboard";
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
        }
}'''
        blocks = [f'{x}\n' for x in orig.split('\n')]
        obj.process_param(blocks, {'missingparam': "True",
                                   'TrialParam EndVoltageLimits': "55"})
        expect = '''
MultiTrialTest SBFT_ATOM_VMAX_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO
{
        TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_" + CustomBinMatrixSpecs.AT_F1_FREQ_MHz + "_BILBO_" + BinMatrix.bin
        {
    missingparam = "True";
            TrialParam EndVoltageLimits = 55;
                ExecutionMode = "SearchWithScoreboard";
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
        }
}
'''
        self.assertTextEqual(''.join(blocks), expect)

    def test_process_trialparam(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')

        # MultiTrial new param
        orig = '''
MultiTrialTest SBFT_ATOM_VMAX_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO
{
        TrialVariableExitAction Continue;
        TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_" + CustomBinMatrixSpecs.AT_F1_FREQ_MHz + "_BILBO_" + BinMatrix.bin
        {
                TrialParam EndVoltageLimits = blah;
                Something = blah;
                ExecutionMode = "SearchWithScoreboard";
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
        }
}'''
        blocks = [f'{x}\n' for x in orig.split('\n')]
        obj = ALttc(tpobj)
        obj.process_param(blocks, {'missingparam': "True",
                                   'EndVoltageLimits': "55",
                                   'TrialVariableExitAction': 'Restore',
                                   'TrialParam Something': "some'var'here"})
        obj.replace_trialtest_name(blocks, 'LTTC')
        expect = '''
MultiTrialTest SBFT_ATOM_VMAX_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO
{
            TrialVariableExitAction Restore;
        TrialTest VminTC "SBFT_ATOM_VMIN_K_LTTC_X_VATOM_F1_" + CustomBinMatrixSpecs.AT_F1_FREQ_MHz + "_BILBO_" + BinMatrix.bin
        {
    missingparam = "True";
            EndVoltageLimits = 55;
            TrialParam Something = some"var"here;
                ExecutionMode = "SearchWithScoreboard";
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
        }
}
'''
        self.assertTextEqual(''.join(blocks), expect)

    def test_update_name(self):
        self.assertEqual(ALttc.update_name('BGCEP_X_SCREEN_K_BEGCPUPKG_X_X_X_X_CEP_DAC_SLOPE_CALC', 'CHICKENWINGS'),
                         'BGCEP_X_SCREEN_K_CHICKENWINGS_X_X_X_X_CEP_DAC_SLOPE_CALC')
        with self.assertRaisesRegex(ErrorUser, 'does not follow naming convention'):
            ALttc.update_name('BGCEP_X_SCREEN_K', 'CHICKENWINGS')

    def test_get_port_dict(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init()

        # empty input
        result = ALttc(tpobj).get_port_dict({})
        self.assertEqual(result, {-2: {'PassFail': 'Fail', 'Return': '-1'},
                                  -1: {'PassFail': 'Fail', 'Return': '-1'},
                                  0: {'PassFail': 'Fail', 'Return': '0'},
                                  1: {'PREVIOUS': True, 'PassFail': 'Pass'}})

        # overwrite
        result = ALttc(tpobj).get_port_dict({"0": "Pass: NEXT",
                                             "1": "Fail: Return 0",
                                             "2": "Pass: GoTo Somewhere"})
        self.assertEqual(result, {-2: {'PassFail': 'Fail', 'Return': '-1'},
                                  -1: {'PassFail': 'Fail', 'Return': '-1'},
                                  0: {'PREVIOUS': True, 'PassFail': 'Pass'},
                                  1: {'PassFail': 'Fail', 'Return': '0'},
                                  2: {'GoTo': 'Somewhere', 'PassFail': 'Pass'}})

        # bad input
        with self.assertRaisesRegex(ErrorUser, 'Invalid syntax'):
            ALttc(tpobj).get_port_dict({"0": "NEXT"})

    def test_get_original_ports(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = ALttc(tpobj)

        # CCC1 is 'Goto <next>;'
        result = obj.get_original_ports('CCC1', {}, 'ARR', 'ARR_Next_TI')
        self.assertEqual(result, {1: {'PassFail': 'Fail',
                                      'finalline': 'GoTo ARR_Next_TI'}})

        # CCD is 'Return 1;'
        result = obj.get_original_ports('CCD', {}, 'ARR', 'ARR_Next_TI')
        self.assertEqual(result, {1: {'PassFail': 'Fail',
                                      'SetBin': 'SoftBins.b90999901_fail_FAIL_DPS_ALARM',
                                      'finalline': 'Return 1'}})

        # test instance is not found
        with self.assertRaisesRegex(ErrorInput, "CCDX is not found in"):
            obj.get_original_ports('CCDX', {}, 'ARR', 'ARR_Next_TI')

    def test_update_orig_port(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = ALttc(tpobj)

        # pass port is a return 1
        origports = {-2: {'PassFail': 'Fail',
                          'Return': '-2',
                          'SetBin': 'SoftBins.b90999901_fail_FAIL_DPS_ALARM'},
                     -1: {'PassFail': 'Fail',
                          'Return': '-1',
                          'SetBin': 'SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE'},
                     0: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270135_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0',
                         'PassFail': 'Fail',
                         'GoTo': 'somewhere',
                         'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF'},
                     1: {'PassFail': 'Pass', 'Return': '1'},
                     2: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270136_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_2',
                         'PassFail': 'Fail',
                         'Return': '0',
                         'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF'},
                     999: 'BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST'}
        result = obj.update_orig_port(origports, {"-1": "NEXT",
                                                  "2": "GoTo my_own_lttc_goto"}, 'next_lttc_ti')
        pprint(result)
        expect = {-2: {'PassFail': 'Fail',
                       'SetBin': 'SoftBins.b90999901_fail_FAIL_DPS_ALARM',
                       'finalline': 'Return -2'},
                  -1: {'PassFail': 'Fail',
                       'finalline': 'GoTo next_lttc_ti'},
                  0: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270135_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0',
                      'PassFail': 'Fail',
                      'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF',
                      'finalline': 'GoTo next_lttc_ti'},
                  1: {'PassFail': 'Pass', 'finalline': 'Return 1'},
                  2: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270136_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_2',
                      'PassFail': 'Fail',
                      'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF',
                      'finalline': 'GoTo my_own_lttc_goto'}}

        self.assertEqual(result, expect)

        # pass port is a goto case
        print('---- new case')
        origports = {-2: {'PassFail': 'Fail',
                          'Return': '-1',
                          'SetBin': 'SoftBins.b90999901_fail_FAIL_DPS_ALARM'},
                     -1: {'PassFail': 'Fail',
                          'Return': '-1',
                          'SetBin': 'SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE'},
                     0: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270135_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0',
                         'PassFail': 'Fail',
                         'GoTo': 'somewhere',
                         'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF'},
                     1: {'PassFail': 'Pass',
                         'GoTo': 'next_instance'},
                     2: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270136_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_2',
                         'PassFail': 'Fail',
                         'Return': '0',
                         'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF'},
                     3: {'PassFail': 'Fail',
                         'GoTo': 'next_instance'},
                     999: 'BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST'}
        result = obj.update_orig_port(origports, {"-1": "NEXT"}, 'next_lttc_ti')
        # pprint(result)
        expect = {-2: {'PassFail': 'Fail', 'finalline': 'Return -1'},
                  -1: {'PassFail': 'Fail', 'finalline': 'GoTo next_lttc_ti'},    # "NEXT" with return
                  0: {'PassFail': 'Fail', 'finalline': 'GoTo next_lttc_ti'},
                  1: {'PassFail': 'Pass', 'finalline': 'GoTo next_lttc_ti'},
                  2: {'PassFail': 'Fail', 'finalline': 'Return 0'},
                  3: {'PassFail': 'Fail', 'finalline': 'GoTo next_lttc_ti'}}
        result2 = {}    # remove SetBin and IncrementCounter in the output
        for port in result:
            result2[port] = {x: y for x, y in result[port].items() if x in ('PassFail', 'finalline')}
        self.assertEqual(result2, expect)

        # This is last instance in the LTTC flow
        result = obj.update_orig_port(origports, {"-1": "NEXT"}, None)
        expect = {-2: {'PassFail': 'Fail', 'finalline': 'Return -1'},
                  -1: {'PassFail': 'Fail', 'finalline': 'Return -1'},    # "NEXT" with return
                  0: {'PassFail': 'Fail', 'finalline': 'Return 0'},
                  1: {'PassFail': 'Pass', 'finalline': 'Return 1'},
                  2: {'PassFail': 'Fail', 'finalline': 'Return 0'},
                  3: {'PassFail': 'Fail', 'finalline': 'Return 0'}}
        pprint(result)
        result2 = {}    # remove SetBin and IncrementCounter in the output
        for port in result:
            result2[port] = {x: y for x, y in result[port].items() if x in ('PassFail', 'finalline')}
        self.assertEqual(result2, expect)

    def test_update_orig_port_next(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = ALttc(tpobj)

        # pass port is a return 1
        origports = {-2: {'PassFail': 'Fail',
                          'Return': '-2'},
                     -1: {'PassFail': 'Fail',
                          'Return': '-1',
                          'SetBin': 'SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE'},
                     0: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270135_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0',
                         'PassFail': 'Fail',
                         'GoTo': 'somewhere',
                         'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF'},
                     1: {'PassFail': 'Pass', 'Return': '1'},
                     2: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270136_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_2',
                         'PassFail': 'Fail',
                         'Return': '0',
                         'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF'},
                     999: 'BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST'}
        result = obj.update_orig_port(origports,
                                      {"2": "NEXT"},
                                      'next_lttc_ti',
                                      {"-2": "SoftBins.b90999901_fail_myown1",
                                       "-1": "SoftBins.b90999901_fail_myown2"})
        pprint(result)
        expect = {-2: {'PassFail': 'Fail',
                       'SetBin': 'SoftBins.b90999901_fail_myown1',
                       'finalline': 'Return -2'},
                  -1: {'PassFail': 'Fail',
                       'finalline': 'Return -1',
                       'SetBin': 'SoftBins.b90999901_fail_myown2'},
                  0: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270135_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0',
                      'PassFail': 'Fail',
                      'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF',
                      'finalline': 'GoTo next_lttc_ti'},
                  1: {'PassFail': 'Pass', 'finalline': 'Return 1'},
                  2: {'IncrementCounters': 'PTH_BGCEP_CXX::n90270136_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_2',
                      'PassFail': 'Fail',
                      'finalline': 'GoTo next_lttc_ti'}}

        self.assertEqual(result, expect)

    def test_derive_setbin(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        obj = ALttc(tpobj)
        dd = {'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POSTDEF'}
        self.assertEqual(obj.derive_setbin(dd, 'PTH_BGCEP', 'my_new_testname'),
                         'SoftBins.b90949427_fail_PTH_BGCEP_my_new_testname')

        dd = {'SetBin': 'SoftBins.b90272723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_SHARED_BIN'}
        self.assertEqual(obj.derive_setbin(dd, 'PTH_BGCEP', 'my_new_testname'),
                         'SoftBins.b90949427_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_SHARED_BIN')

        dd = {'SetBin': 'SoftBins.b9022723_fail_PTH_BGCEP_CXX_BGCEP_X_ANAMEAS_K_SHARED_BIN'}
        with self.assertRaisesRegex(ErrorInput, 'does not follow setbin naming convention'):
            obj.derive_setbin(dd, 'PTH_BGCEP', 'my_new_testname')

        dd = {}
        self.assertEqual(obj.derive_setbin(dd, 'PTH_BGCEP', 'my_new_testname'), None)

    def test_derive_counter(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        obj = ALttc(tpobj)
        dd = {'IncrementCounters': 'PTH_BGCEP_CXX::n90270135_fail_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0'}
        self.assertEqual(obj.derive_counter(dd, 'my_new_testname'),
                         'PTH_BGCEP_CXX::n94902713_fail_my_new_testname')

        dd = {'IncrementCounters': 'PTH_BGCEP_CXX::p90270135_pass_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0'}
        self.assertEqual(obj.derive_counter(dd, 'my_new_testname'),
                         'PTH_BGCEP_CXX::p94902713_pass_my_new_testname')

        dd = {'SetBin': 'blah'}
        self.assertEqual(obj.derive_counter(dd, 'my_new_testname'), None)

        dd = {'IncrementCounters': 'PTH_BGCEP_CXX::p90270135_BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST_0'}
        with self.assertRaisesRegex(ErrorInput, 'does not follow counter naming convention'):
            obj.derive_counter(dd, 'my_new_testname')

    def test_insert_ti(self):
        input_list = '''
    TestPlan A;
    Import line;

    Test blah
    {
       someline
    }'''.split('\n')
        new_block = '''Test vmin ABC
{
    newline
}'''.split('\n')
        ALttc.insert_ti(input_list, new_block, 'unittest')
        expect = '''
    TestPlan A;
    Import line;

Test vmin ABC
{
    newline
}
    Test blah
    {
       someline
    }
'''
        self.assertTextEqual('\n'.join(input_list), expect)

        # no Test found
        input_list = '''
TestPlan A;
Import line;
'''.split('\n')
        with self.assertRaisesRegex(ErrorInput, 'No Test line found'):
            ALttc.insert_ti(input_list, new_block, 'unittest.mtpl')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True, delete=True)
    def test_invalid_registry1(self):
        # Put the unittest files in temp directory
        File(f'POR_TP/TGLH81/InputFiles/ALTTC_registry.json').touch('''
{
"LTTCSOC_SubFlow": [
  "TPI_DFF_XXX_LTTCSOC",
]
''', mkdir=True)

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        obj = ALttc(tpobj)
        with self.assertRaisesRegex(ErrorInput, 'Pls fix registry file'):
            obj.main()

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True, delete=True)
    def test_invalid_registry2(self):
        # Put the unittest files in temp directory
        mkdirs('POR_TP/TGLH81/InputFiles')
        File(f'{UT_DIR_REPO}/alttc_files/ALTTC_registry.json').copy('POR_TP/TGLH81/InputFiles/ALTTC_registry.json')
        File(f'Modules/ARR/InputFiles/lttc_list.json').touch('''
{
"LTTCSOC_SubFlow": [
  "TPI_DFF_XXX_LTTCSOC",
]
''', mkdir=True)

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        obj = ALttc(tpobj)
        with self.assertRaisesRegex(ErrorUser, 'Pls fix Modules/ARR/InputFiles/lttc_list.json'):
            obj.main()

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True, delete=True)
    def test_integ1(self):    # a good template to follow
        # We give a specific .mtpl using Simple6 with all the inputs

        # Put the unittest files in temp directory
        File(f'{UT_DIR_REPO}/alttc_files/PTH_BGCEP_CXX.mtpl').copy('Modules/ARR/array.mtpl')
        mkdirs('POR_TP/TGLH81/InputFiles')
        File(f'{UT_DIR_REPO}/alttc_files/ALTTC_registry.json').copy('POR_TP/TGLH81/InputFiles/ALTTC_registry.json')
        mkdirs('Modules/ARR/InputFiles')
        File(f'{UT_DIR_REPO}/alttc_files/lttc_list_2.json').copy('Modules/ARR/InputFiles/lttc_list.json')
        File(f'{UT_DIR_REPO}/alttc_files/ProgramFlows.mtpl').copy('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl')

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.mtpl.read_mtpls()
        tpobj.mtpl.read_mtpl_flow()

        obj = ALttc(tpobj)
        obj.main()

        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/alttc_files/array.mtpl.gold7')
        self.assertGoldEqual('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl',
                             f'{UT_DIR_REPO}/alttc_files/ProgramFlows.mtpl.gold1')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True, delete=True)
    def test_integ2_scope(self):
        # with scope in program flows, mocked value
        # check .flw correctness as well
        # We give a specific .mtpl using Simple6 with all the inputs

        # Put the unittest files in temp directory
        File(f'{UT_DIR_REPO}/alttc_files/PTH_BGCEP_CXX.mtpl').copy('Modules/ARR/array.mtpl')
        mkdirs('POR_TP/TGLH81/InputFiles')
        File(f'{UT_DIR_REPO}/alttc_files/ALTTC_registry.json').copy('POR_TP/TGLH81/InputFiles/ALTTC_registry.json')
        mkdirs('Modules/ARR/InputFiles')
        File(f'{UT_DIR_REPO}/alttc_files/lttc_list.json').copy('Modules/ARR/InputFiles/lttc_list.json')
        File(f'{UT_DIR_REPO}/alttc_files/ProgramFlows.mtpl').copy('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl')

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')

        with MockVar(TestProgram, 'get_ipname', Mock(return_value='IP_PCH')):
            obj = ALttc(tpobj)
            obj.main()

        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/alttc_files/array.mtpl.gold6')
        self.assertGoldEqual('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl',
                             f'{UT_DIR_REPO}/alttc_files/ProgramFlows.mtpl.gold1A')

        # Make sure .flw is correct
        expect = '''
<?xml version="1.0" encoding="utf-8"?>
<!--File is auto-generated, any manual edits can be overwritten.-->
<!DOCTYPE HDMTFlowItemCoor []>
<HDMTFlowItemCoor>
  <FlowItem name="PTH_BGCEP_CXX::PTH_BGCEP_CXX_LTTCCPUPKG_TEST.BGCEP_X_ANAMEAS_K_LTTCCPUPKG_X_X_X_X_BGR_ANAPRB_POST" X="25" Y="25" />
  <FlowItem name="PTH_BGCEP_CXX::PTH_BGCEP_CXX_LTTCCPUPKG_TEST.BGCEP_X_CMEM_K_LTTCCPUPKG_X_X_X_X_CEP_DAC_CALIBRATION_SWEEP" X="25" Y="25" />
  <FlowItem name="PTH_BGCEP_CXX::PTH_BGCEP_CXX_LTTCCPUPKG_TEST.BGCEP_X_SCREEN_K_LTTCCPUPKG_X_X_X_X_CEP_DAC_SLOPE_CALC" X="25" Y="25" />
  <FlowItem name="ARR::CCA" X="25" Y="25" />
</HDMTFlowItemCoor>
'''
        self.assertTextEqual(File('Modules/ARR/array.flw').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True, delete=True)
    def test_integ3(self):
        # We give a specific .mtpl using Simple6 with all the inputs

        # Put the unittest files in temp directory
        File(f'{UT_DIR_REPO}/alttc_files/ARR_CORE_C68_CLASS_P68G2.mtpl').copy('Modules/ARR/array.mtpl')
        mkdirs('POR_TP/TGLH81/InputFiles')
        File(f'{UT_DIR_REPO}/alttc_files/ALTTC_registry.json').copy('POR_TP/TGLH81/InputFiles/ALTTC_registry.json')
        mkdirs('Modules/ARR/InputFiles')
        File(f'{UT_DIR_REPO}/alttc_files/lttc_list_ARR_CORE.json').copy('Modules/ARR/InputFiles/lttc_list.json')
        File(f'{UT_DIR_REPO}/alttc_files/ProgramFlows.mtpl').copy('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl')

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.mtpl.read_mtpls()
        tpobj.mtpl.read_mtpl_flow()

        obj = ALttc(tpobj)
        obj.main()

        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/alttc_files/array.mtpl.ARR_CORE.gold7')
        self.assertGoldEqual('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl',
                             f'{UT_DIR_REPO}/alttc_files/ProgramFlows.mtpl.ARR_CORE.gold1')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
