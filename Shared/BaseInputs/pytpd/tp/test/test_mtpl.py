#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for mtpl.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE     # must be first import for unittests
from tp.mtpl import *
from tp.testprogram import TestProgram
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.printmore import Dumper
from gadget.gizmo import MockVar, with_
from gadget.files import TempDir
from gadget.dictmore import keys_atlevel
from pprint import pprint, pformat
from unittest.mock import Mock
import os


class MtplTest(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, for fast coverage run"))
    def test_mtpl_realtp(self):
        # stpl - with intradut
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        obj = tp.mtpl
        obj.read_mtpls()
        self.assertEqual(len(list(keys_atlevel(obj.tdata, 0))), 141)   # total modules
        self.assertEqual(len(obj.get_modfolder2mod()), 143)           # includes IP_CPU|PCH_CONCURRENT_FLOWS
        self.assertEqual(len(list(obj.iter_tests())), 11335)     # total testinstances
        self.assertEqual(len(list(keys_atlevel(obj.tdata, 1))), 11335)     # total instances
        self.assertEqual(len(list(keys_atlevel(obj.tdata, 2))), 140027)     # total methods

        obj.read_mtpl_flow()
        self.assertEqual(len(list(keys_atlevel(obj._dutflow, 1))), 17080)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, for fast coverage run"))
    def test_mtpl_realtp2(self):
        # without intradut
        tp = TestProgram(join(UT_DIR, 'TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env'))
        obj = tp.mtpl
        obj.read_mtpls()
        self.assertEqual(len(list(keys_atlevel(obj.tdata, 0))), 80)   # total modules
        self.assertEqual(len(list(obj.iter_tests())), 12665)     # total testinstances
        self.assertEqual(len(list(keys_atlevel(obj.tdata, 2))), 183495)     # total methods

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, for fast coverage run"))
    def test_mtpl_realtp_srh(self):
        tp = TestProgram(join(UT_DIR, 'SRHXXXXAXH00G40S127/EnvironmentFile_CLASS_HBM.env'))
        tp.init(patload=False)
        result = tp.mtpl.dict_flows()
        self.assertEqual(len([x for x in result.values() if x == 'P']), 2494)   # pass case
        self.assertEqual(len([x for x in result.values() if x == 'F']), 861)   # fail case
        self.assertEqual(len(result), 4196)   # all

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, for fast coverage run"))
    def test_specific_mod_realtp(self):
        # specific mtpl
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        obj = tp.mtpl
        obj.read_mtpl_specific(['./Modules/ARR_CCF/ARR_CCF_CLASS_TGLH81.mtpl',
                                UT_DIR + '/TGLXXXXRXH35H00S025/TPL/Modules/ARR_CORE/ARR_CORE_CLASS_TGLH81.mtpl'])
        self.assertEqual(len(list(keys_atlevel(obj.tdata, 0))), 2)   # total modules
        self.assertEqual(len(list(obj.iter_tests(key_name='TEMPLATE'))), 926)     # total testinstances
        self.assertEqual(len(list(keys_atlevel(obj.tdata, 2))), 17571)     # total methods

        # error case
        with self.assertRaisesRegex(AssertionError, 'Data is already populated in mtpl object'):
            obj.read_mtpls(modules=['ARR'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, for fast coverage run"))
    def test_maxrecursion_bug(self):
        # specific tp, postproc is run already
        tp = TestProgram(f'{UT_DIR}/19M0Z_recurse_fail/POR_TP/Class_MTL_P68/EnvironmentFile.env').init()
        result = list(tp.mtpl.iter_flows('MAIN', passonly=False, bypass=True, keyparam='patlist'))
        self.assertEqual(len(result), 8697)

    def test_eval_params(self):
        # good template
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv;
Test iCSimpleScoreboardTest Test1              # w/ space
{
        int1 = 12 ;
        int2 = 12 + var ;
        str1 = "arr_pbist" ;                   # plain string
        str2 = "9,10,11"+",12,13,14,15" ;      # string looks like expression
        str3 = "DIE_RECOVERY!" + ARR.var ;     # string expression
        str4 = ("CPD!DEBUG") ;                 # expression
        str5 = "" ;                            # empty
        str6 = v ;                             # single char var
        str7 = "v" ;                           # single char
        bypass_global = "ARR.byp";             # should evaluate
        _EDCKILL = "1";
}
Test iCSimpleScoreboardTest Test2              # No space
{
        int1=12;
        int2=12 + var;
        str1="arr_pbist";                   # plain string
        str2="9,10,11"+",12,13,14,15";      # string looks like expression
        str3="DIE_RECOVERY!" + ARR.var;     # string expression
        str4=("CPD!DEBUG");                 # expression
        str5="";                            # empty
        str6=v;                             # single char var
        str7="v";                           # single char
        bypass_global="ARR.byp";
        _EDCKILL = "1";
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String var = "CORE5";
    Integer byp = 2;
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

UserVars
{
        Integer var = 5;
        String v = "OneChar";
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(), {'Test1', 'Test2'})
            expect_dict = {'TEMPLATE': 'iCSimpleScoreboardTest',
                           'int1': '12',
                           'int2': '12 + var',
                           'str1': 'arr_pbist',
                           'str2': '"9,10,11"+",12,13,14,15"',
                           'str3': '"DIE_RECOVERY!" + ARR.var',
                           'str4': '("CPD!DEBUG")',
                           'str5': '',
                           'str6': 'v',
                           'str7': 'v',
                           'bypass_global': "ARR.byp",
                           '_EDCKILL': '1',
                           }

            result = obj.get_instance('ARR', 'Test1')
            Dumper(result)
            self.maxDiff = None
            self.assertEqual(result, expect_dict)
            expect_type = {'TEMPLATE': True,
                           '_EDCKILL': True,
                           'int1': False,
                           'int2': False,
                           'str1': True,
                           'str2': False,
                           'str3': False,
                           'str4': False,
                           'str5': True,
                           'str6': False,
                           'str7': True,
                           'bypass_global': True}
            self.assertEqual(obj.ttype['ARR']['Test1'], expect_type)

            # check on Test2
            result = obj.get_instance('ARR', 'Test2')
            self.assertEqual(result, expect_dict)
            self.assertEqual(obj.ttype['ARR']['Test2'], expect_type)

            # evaluate
            obj.eval_params()
            self.assertEqual(obj.edata.keys(), {'ARR'})
            self.assertEqual(obj.edata['ARR'].keys(), {'Test1', 'Test2'})
            expect_eval = {'TEMPLATE': 'iCSimpleScoreboardTest',
                           '_EDCKILL': '1',
                           'int1': 12,
                           'int2': 17,
                           'str1': 'arr_pbist',
                           'str2': '9,10,11,12,13,14,15',
                           'str3': 'DIE_RECOVERY!CORE5',
                           'str4': 'CPD!DEBUG',
                           'str5': '',
                           'str6': 'OneChar',
                           'str7': 'v',
                           'bypass_global': 2}
            self.assertEqual(obj.get_instance('ARR', 'Test1', evaluated=True), expect_eval)
            self.assertEqual(obj.get_instance('ARR', 'Test2', evaluated=True), expect_eval)

            self.assertEqual(obj.get_instance('ARR', 'Test1', both=True), (expect_dict, expect_eval))

    def test_eval_params_torch(self):
        # good template
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv;
Test iCSimpleScoreboardTest Test1              # w/ space
{
        int1 = 12 ;
        str2 = "9,10,11"+",12,13,14,15" ;      # string looks like expression
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String var = "CORE5";
    Integer byp = 2;
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

UserVars
{
        Integer var = 5;
        String v = "OneChar";
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            list(obj.set_instance('ARR', 'Test1', 'str2', 'a/b/c'))    # Need to set an expression
            obj.eval_params()
            expect_dict = {'TEMPLATE': 'iCSimpleScoreboardTest',
                           'int1': 12,
                           'str2': 'a/b/c',
                           }
            result = obj.get_instance('ARR', 'Test1', evaluated=True)
            Dumper(result)
            self.maxDiff = None
            self.assertEqual(result, expect_dict)
            self.assertEqual(obj.get_import_mtpl('ARR'), ['Import bb.usrv;'])

    def test_eval_params_with_mtt_shared(self):
        # Test that _MTT(__shared__) :: is properly removed during eval_params
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv;
Test iCSimpleScoreboardTest Test1
{
        param1 = _MTT(__shared__) :: ARR.var ;
        param2 = _MTT(__shared__) ::ARR.var2 ;
        param3 = ARR.var3 ;
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String var = "VALUE1";
    String var2 = "VALUE2";
    String var3 = "VALUE3";
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

UserVars
{
        Integer dummy = 1;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()

            # Verify raw data before evaluation
            raw_data = obj.get_instance('ARR', 'Test1')
            self.assertEqual(raw_data['param1'], '_MTT(__shared__) :: ARR.var')
            self.assertEqual(raw_data['param2'], '_MTT(__shared__) ::ARR.var2')
            self.assertEqual(raw_data['param3'], 'ARR.var3')

            # Evaluate params
            obj.eval_params()

            # Verify that _MTT(__shared__) :: was removed and params were evaluated
            expect_dict = {'TEMPLATE': 'iCSimpleScoreboardTest',
                           'param1': 'VALUE1',
                           'param2': 'VALUE2',
                           'param3': 'VALUE3'}
            result = obj.get_instance('ARR', 'Test1', evaluated=True)
            Dumper(result)
            self.maxDiff = None
            self.assertEqual(result, expect_dict)

    def test_parse_multiline(self):
        with TempDir(name=True) as tdir:
            backslash = '\\'
            code = f"""
Test iCSimpleScoreboardTest CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST
{{
        fail_process_level = CLK_Rules.LJ( {backslash}
        "", {backslash}
        "","VDAC!SetVDACFromHardwareLevels");    # more comment {backslash}
        level = "BASE::DDR_univ_lvl_nom_{backslash}lvl";
}}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(),
                             {'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST'})
            expect_dict = {'TEMPLATE': 'iCSimpleScoreboardTest',
                           'level': 'BASE::DDR_univ_lvl_nom_\\lvl',
                           'fail_process_level': 'CLK_Rules.LJ( "", "","VDAC!SetVDACFromHardwareLevels")'}

            result = obj.get_instance('ARR', 'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST')
            Dumper(result)
            self.maxDiff = None
            self.assertEqual(result, expect_dict)

    def test_mtpl_read(self):
        with TempDir(name=True) as tdir:
            code = f"""
Test iCSimpleScoreboardTest CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST
{{
    IntegrityLowLimit = 125;  #USER TODO: define value; #USER TODO: define value
    LowerTolerance = "15";
    PinNames = TP_KNOB.Active_TDAUPins;
    UpperTolerance = "15";
}}
"""

            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(),
                             {'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST'})
            expect_dict = {'IntegrityLowLimit': '125',
                           'LowerTolerance': '15',
                           'PinNames': 'TP_KNOB.Active_TDAUPins',
                           'TEMPLATE': 'iCSimpleScoreboardTest',
                           'UpperTolerance': '15'}

            result = obj.get_instance('ARR', 'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST')
            Dumper(result)
            self.maxDiff = None
            self.assertEqual(result, expect_dict)

    def test_mtpl_readmtt(self):
        with TempDir(name=True) as tdir:
            code = """
MultiTrialTest CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF
{
        TrialVariable __main__::FlowDomain.Default;
        TrialVariableExitAction Continue;
        TrialTest VminTC "CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs
        {
                CornerIdentifiers = ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1;
                TrialParam EndVoltageLimits = ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS;
                ExecutionMode = ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB;
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
                TrialResult -1
                {
                        PassFail Fail;
                        TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + FlowMatrix.bin + "0286_fail_";
                        Return -1;
                }
        }
}
"""

            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(),
                             {'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF'})

            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF')
            expect = '''
{'CornerIdentifiers': 'ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1',
 'EndVoltageLimits': '(_MTT(ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS))',
 'ExecutionMode': 'ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB',
 'TEMPLATE': 'VminTC'}
'''
            self.assertTextEqual(pformat(result), expect)

            expect = '''
{'TrialParam': {'EndVoltageLimits'},
 'TrialResult': {-2: {'PassFail': 'Fail',
                      'Return': '-2',
                      'TrialAction': 'Exit'},
                 -1: {'IncrementCounters': '"ARR_ATOM_CXX::n" + FlowMatrix.bin '
                                           '+ "0286_fail_"',
                      'PassFail': 'Fail',
                      'Return': '-1',
                      'TrialAction': 'Exit'}},
 'TrialTest': '"CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs',
 'TrialVariable': '__main__::FlowDomain.Default;',
 'TrialVariableExitAction': 'Continue;'}
'''
            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF', mtt=True)
            self.assertTextEqual(pformat(result), expect)

    def test_mtpl_readmtt_edcsetbin(self):
        with TempDir(name=True) as tdir:
            code = """
MultiTrialTest CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF
{
        TrialVariable __main__::FlowDomain.Default;
        TrialVariableExitAction Continue;
        TrialTest VminTC "CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs
        {
                CornerIdentifiers = ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1;
                TrialParam EndVoltageLimits = ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS;
                ExecutionMode = ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB;
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
                TrialResult -1
                {
                        PassFail Fail;
                        TrialAction Exit;
                        ##EDC## SetBin "SoftBins.b" + FlowMatrix.bin + "4400_fail_FUN_MTTtname";
                        #IncrementCounters "ARR_ATOM_CXX::n" + FlowMatrix.bin + "0286_fail_";
                        Return -1;
                }
        }
}
"""

            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_edc_setbin = True
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(),
                             {'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF'})

            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF')
            expect = '''
{'CornerIdentifiers': 'ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1',
 'EndVoltageLimits': '(_MTT(ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS))',
 'ExecutionMode': 'ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB',
 'TEMPLATE': 'VminTC'}
'''
            self.assertTextEqual(pformat(result), expect)

            expect = '''
{'TrialParam': {'EndVoltageLimits'},
 'TrialResult': {-2: {'PassFail': 'Fail',
                      'Return': '-2',
                      'TrialAction': 'Exit'},
                 -1: {'PassFail': 'Fail',
                      'Return': '-1',
                      'SetBin': '"SoftBins.b" + FlowMatrix.bin + '
                                '"4400_fail_FUN_MTTtname"',
                      'TrialAction': 'Exit'}},
 'TrialTest': '"CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs',
 'TrialVariable': '__main__::FlowDomain.Default;',
 'TrialVariableExitAction': 'Continue;'}
'''
            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF', mtt=True)
            self.assertTextEqual(pformat(result), expect)

    def test_mtpl_readmtt_tos4(self):
        with TempDir(name=True) as tdir:
            code = """
MultiTrialTest CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF
{
        TrialVariable __main__::FlowDomain.Default;
        TrialVariableExitAction Continue;
        CSharpTrialTest VminTC "CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs
        {
                CornerIdentifiers = ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1;
                TrialParam EndVoltageLimits = ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS;
                ExecutionMode = ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB;
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
                TrialResult -1
                {
                        PassFail Fail;
                        TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + FlowMatrix.bin + "0286_fail_";
                        Return -1;
                }
        }
}
"""

            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(),
                             {'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF'})

            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF')
            expect = '''
{'CornerIdentifiers': 'ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1',
 'EndVoltageLimits': '(_MTT(ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS))',
 'ExecutionMode': 'ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB',
 'TEMPLATE': 'VminTC'}
'''
            self.assertTextEqual(pformat(result), expect)

            expect = '''
{'CSharpTrialTest': '"CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + '
                    'CustomFlowMatrixSpecs',
 'TrialParam': {'EndVoltageLimits'},
 'TrialResult': {-2: {'PassFail': 'Fail',
                      'Return': '-2',
                      'TrialAction': 'Exit'},
                 -1: {'IncrementCounters': '"ARR_ATOM_CXX::n" + FlowMatrix.bin '
                                           '+ "0286_fail_"',
                      'PassFail': 'Fail',
                      'Return': '-1',
                      'TrialAction': 'Exit'}},
 'TrialVariable': '__main__::FlowDomain.Default;',
 'TrialVariableExitAction': 'Continue;'}
'''
            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF', mtt=True)
            self.assertTextEqual(pformat(result), expect)

    def test_mtpl_readmtt_param_with_ip(self):
        with TempDir(name=True) as tdir:
            code = """
MultiTrialTest CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF
{
        TrialVariable __main__::FlowDomain.Default;
        TrialVariableExitAction Continue;
        TrialTest VminTC "CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs
        {
                CornerIdentifiers = ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1;
                TrialParam EndVoltageLimits = IP_CPU::IP_CPU_BASE::ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS;
                ExecutionMode = ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB;
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
                TrialResult -1
                {
                        PassFail Fail;
                        TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + FlowMatrix.bin + "0286_fail_";
                        Return -1;
                }
        }
}

MultiTrialTest CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF_4IP
{
        TrialVariable __main__::FlowDomain.Default;
        TrialVariableExitAction Continue;
        TrialTest VminTC "CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs
        {
                CornerIdentifiers = ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1_4IP;
                TrialParam EndVoltageLimits = IP_A::IP_B::IP_C::IP_D::ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS;
                ExecutionMode = ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB;
                TrialResult -2
                {
                        PassFail Fail;
                        TrialAction Exit;
                        Return -2;
                }
                TrialResult -1
                {
                        PassFail Fail;
                        TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + FlowMatrix.bin + "0286_fail_";
                        Return -1;
                }
        }
}
"""

            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(),
                             {'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF',
                              'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF_4IP'})

            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF')
            expect = '''
{'CornerIdentifiers': 'ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1',
 'EndVoltageLimits': '(_MTT(ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS))',
 'ExecutionMode': 'ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB',
 'TEMPLATE': 'VminTC'}
'''
            self.assertTextEqual(pformat(result), expect)

            expect = '''
{'TrialParam': {'EndVoltageLimits'},
 'TrialResult': {-2: {'PassFail': 'Fail',
                      'Return': '-2',
                      'TrialAction': 'Exit'},
                 -1: {'IncrementCounters': '"ARR_ATOM_CXX::n" + FlowMatrix.bin '
                                           '+ "0286_fail_"',
                      'PassFail': 'Fail',
                      'Return': '-1',
                      'TrialAction': 'Exit'}},
 'TrialTest': '"CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs',
 'TrialVariable': '__main__::FlowDomain.Default;',
 'TrialVariableExitAction': 'Continue;'}
'''
            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF', mtt=True)
            self.assertTextEqual(pformat(result), expect)

            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF_4IP')
            expect = '''
{'CornerIdentifiers': 'ARR_ATOM_CXX_Specs.VMIN_ATOM_CORNERID_AT_F1_4IP',
 'EndVoltageLimits': '(_MTT(ARR_ATOM_CXX_Rules.ENDVOLTAGELIMITS))',
 'ExecutionMode': 'ARR_ATOM_CXX_Specs.VMIN_ExecutionMode_SearchSB',
 'TEMPLATE': 'VminTC'}
'''
            self.assertTextEqual(pformat(result), expect)
            expect = '''
{'TrialParam': {'EndVoltageLimits'},
 'TrialResult': {-2: {'PassFail': 'Fail',
                      'Return': '-2',
                      'TrialAction': 'Exit'},
                 -1: {'IncrementCounters': '"ARR_ATOM_CXX::n" + FlowMatrix.bin '
                                           '+ "0286_fail_"',
                      'PassFail': 'Fail',
                      'Return': '-1',
                      'TrialAction': 'Exit'}},
 'TrialTest': '"CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs',
 'TrialVariable': '__main__::FlowDomain.Default;',
 'TrialVariableExitAction': 'Continue;'}
'''
            result = obj.get_instance('ARR', 'CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_AT_F1_FREQ_RF_4IP', mtt=True)
            self.assertTextEqual(pformat(result), expect)

    def test_mtpl_basic(self):
        with TempDir(name=True) as tdir:
            code = """
Test iCSimpleScoreboardTest CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST
{
        base_number = 2160;   # comment
        bypass_global = "1";
        fail_process_level = CLK_Rules.LJ("","","VDAC!SetVDACFromHardwareLevels");    # more comment
        level = "BASE::DDR_univ_lvl_nom_lvl";
        max_fails = 20;

        Patlist = "arr_pbist_uclk_f1_mcip_ccf_byplvrretention_all_list";     # special case - Patlist to patlist
        pattern_name_map = "9,10,11"+",12,13,14,15";
        preinstance ="DIE_RECOVERY!" + ARR.var;
        postinstance = ("CPD!DEBUG");
        execution_mode = "SCOREBOARD" + var;
        scoreboard_number_size = 12;
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
}
        DUTFlowItem FlowControl_SSA_CCF_SCOREBOARD_K_VMAXCLRSSAF6_080816_VUNCORE_F6_4000_LLC_DTP_67 FlowControl
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        IncrementCounters ARR_CCF::n90990002_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -1;
                }
        }

    CSharpTest iCLsaRasterTest LSA_CCF_RASTER_E_BEGIN_X_VRING_F1_0800_LLCRF_HRY_LSARASTER_SLICE2
    {
            config_file_name = "./Modules/ARR_CCF/InputFiles/TGL_A_Step_CCF_LSARaster_Config_Golden_s2.xml";
            execution_mode = "RASTER";
            level = "BASE::DDR_univ_lvl_nom_lvl";
            pin_mapping_set_name = "CCF_SLICE_2";
            prescreen_map_name = "LSA_CCF2_MAP";
            prescreen_print_mode = "FAIL_MODE";
            timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
    }
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(obj.tdata.keys(), {'ARR'})
            self.assertEqual(obj.tdata['ARR'].keys(),
                             {'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST',
                              'LSA_CCF_RASTER_E_BEGIN_X_VRING_F1_0800_LLCRF_HRY_LSARASTER_SLICE2'})
            expect_dict = {'TEMPLATE': 'iCSimpleScoreboardTest',
                           'base_number': '2160',
                           'bypass_global': '1',
                           'execution_mode': '"SCOREBOARD" + var',
                           'fail_process_level': 'CLK_Rules.LJ("","","VDAC!SetVDACFromHardwareLevels")',
                           'level': 'BASE::DDR_univ_lvl_nom_lvl',
                           'max_fails': '20',
                           'patlist': 'arr_pbist_uclk_f1_mcip_ccf_byplvrretention_all_list',
                           'pattern_name_map': '"9,10,11"+",12,13,14,15"',
                           'postinstance': '("CPD!DEBUG")',
                           'preinstance': '"DIE_RECOVERY!" + ARR.var',
                           'scoreboard_number_size': '12',
                           'timings': 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'}

            result = obj.get_instance('ARR', 'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST')
            Dumper(result)
            self.maxDiff = None
            self.assertEqual(result, expect_dict)
            self.assertEqual(obj.get_instance('ARR', 'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST', mtt=True),
                             None)
            with MockVar(obj, "edata", obj.tdata):
                self.assertEqual(obj.is_bypassed('ARR', 'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST'), True)

            with self.assertRaisesRegex(AssertionError, 'TestInstance .NOTEST. is not found in module ARR'):
                obj.get_instance('ARR', 'NOTEST')
            with self.assertRaisesRegex(AssertionError, 'Module .ARRX. for .NOTEST. is not found in'):
                obj.get_instance('ARRX', 'NOTEST')

            # iter_tests()
            result = list(obj.iter_tests('iCSimpleScoreboardTest', edict=False))
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], 'ARR')
            self.assertEqual(result[0][1], 'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST')
            self.assertEqual(result[0][2], expect_dict)
            self.assertEqual(len(list(obj.iter_tests('notfound', edict=False))), 0)   # not found

            result = list(obj.iter_tests(key_name='timings', edict=False))
            self.assertEqual(len(result), 2)
            self.assertEqual(len(result[0]), 4)   # number of elements
            self.assertEqual(len(list(obj.iter_tests(key_name='notfound', edict=False))), 0)
            self.assertEqual(len(list(obj.iter_tests(edict=False))), 2)
            self.assertEqual(obj.get_modules(), ['ARR'])

            # set_instance ====================
            tn1 = 'CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST'
            result = list(obj.set_instance('ARR', tn1, 'bypass_global', '2'))
            self.assertEqual(obj.get_instance('ARR', tn1)['bypass_global'], '2')
            self.assertEqual(result[0][0], '1')

            # assign again
            result = list(obj.set_instance('ARR', tn1, 'bypass_global', '2'))
            self.assertEqual(result[0][0], None)

            # set_instance: special bypass_global handling
            tn = 'LSA_CCF_RASTER_E_BEGIN_X_VRING_F1_0800_LLCRF_HRY_LSARASTER_SLICE2'
            result = list(obj.set_instance('ARR', tn, 'bypass_global', '2'))
            self.assertEqual(obj.get_instance('ARR', tn)['bypass_global'], '2')
            self.assertEqual(result[0][0], '-1')

            # set_instance: regex instance
            tnr = 'LSA_CCF_RASTER_E_BEGIN_X_VRING_F1_0800_LLCRF_HRY_LSARASTER_*2'
            result = list(obj.set_instance('ARR', tnr, 'bypass_global', '3'))
            self.assertEqual(len(result), 1)
            self.assertEqual(obj.get_instance('ARR', tn)['bypass_global'], '3')

            # set_instance: none found
            tnr = 'LSA_CCF_RASTER_E_BEGIN_X_VRING_F1_0800_LLCRF_HRY_LSARASTER_*2222'
            result = list(obj.set_instance('ARR', tnr, 'bypass_global', '3'))
            self.assertEqual(len(result), 0)

            # set instance: regex module
            tnr = '*'
            result = list(obj.set_instance('A*', tnr, 'bypass_global', '4'))
            self.assertEqual(len(result), 2)
            self.assertEqual(obj.get_instance('ARR', tn)['bypass_global'], '4')
            self.assertEqual(obj.get_instance('ARR', tn1)['bypass_global'], '4')

            # set instance: regex module - partial match
            tnr = '*'
            result = list(obj.set_instance('A(X*)?R', tnr, 'bypass_global', '4'))
            self.assertEqual(len(result), 0)

            # set instance: uservar
            tp.usrv._userv = {tp.testplan_base: {'DOWNSTREAM_FORK': 5}}
            tp.usrv.ulocal = {tp.testplan_base: {'DOWNSTREAM_FORK': 5}}
            tn = 'LSA_CCF_RASTER_E_BEGIN_X_VRING_F1_0800_LLCRF_HRY_LSARASTER_SLICE2'
            result = list(obj.set_instance('ARR', tn, 'bypass_global', '_UserVars.DOWNSTREAM_FORK'))
            self.assertEqual(obj.get_instance('ARR', tn)['bypass_global'], '5')
            self.assertEqual(result[0][0], '4')

    def test_two_modules(self):
        # good template
        with TempDir(name=True) as tdir:
            code = """
Test iCSimpleScoreboardTest CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST
{
        base_number = 2160;
        bypass_global = "1";
        execution_mode = "SCOREBOARD";
        fail_process_level = "FULL_FAIL_INFO";
        level = "BASE::DDR_univ_lvl_nom_lvl";
        max_fails = 20;

        patlist = "arr_pbist_uclk_f1_mcip_ccf_byplvrretention_all_list";
        pattern_name_map = "9,10,11,12,13,14,15";
        postinstance = "CPD_DEBUG!DirectPlistExecution arr_post_fivr_shutdown_list";
        preinstance = "DIE_RECOVERY!ExecSequence SetMaskFromTrackingStructure";
        scoreboard_number_size = 12;
        timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
}
"""
            File('%s/Modules/FUN/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
    Test iCLsaRasterTest LSA_CCF_RASTER_E_BEGIN_X_VRING_F1_0800_LLCRF_HRY_LSARASTER_SLICE2
    {
            bypass_global = "";
            config_file_name = "./Modules/ARR_CCF/InputFiles/TGL_A_Step_CCF_LSARaster_Config_Golden_s2.xml";
            execution_mode = "RASTER";
            level = "BASE::DDR_univ_lvl_nom_lvl";
            pin_mapping_set_name = "CCF_SLICE_2";
            prescreen_map_name = "LSA_CCF2_MAP";
            prescreen_print_mode = "FAIL_MODE";
            timings = "BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100";
    }
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls()
            self.assertEqual(sorted(keys_atlevel(obj.tdata, 0)), ['ARR', 'FUN'])

            # specific modules - full path
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_specific(['%s/Modules/ARR/a.mtpl' % tdir])
            self.assertEqual(list(keys_atlevel(obj.tdata, 0)), ['ARR'])

            # specific modules - relative path
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_specific(['./Modules/ARR/a.mtpl'])
            self.assertEqual(list(keys_atlevel(obj.tdata, 0)), ['ARR'])

            # read specific modules - module
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpls(['FUN'])
            self.assertEqual(list(keys_atlevel(obj.tdata, 0)), ['FUN'])

            # not existent input
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            with self.assertRaisesRegex(ErrorUser, 'does not exist'):
                obj.read_mtpl_specific(['./Modules/ARR_CCF/notfound.mtpl'])

            # two same modules
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_specific(['./Modules/ARR/a.mtpl', './Modules/ARR/a.mtpl'])
            self.assertEqual(list(keys_atlevel(obj.tdata, 0)), ['ARR'])

        # with flow
        tp = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env')
        tp.mtpl.read_mtpl_specific([f'{UT_DIR_REPO}/Simple8/TPL/./Modules/ARR/array.mtpl'], readflow=True)
        self.assertEqual(len(tp.mtpl.tdata), 1)
        self.assertEqual(len(tp.mtpl.tdata['ARR']), 3)
        self.assertEqual(len(tp.mtpl.get_dutflow_map()), 2)   # main and init for ARR

    def test_mtpl_read_programflow(self):
        # Reading a ProgramFlows.mtpl should not populate any tdata. Also, needed for coverage.
        tp = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env')
        tp.mtpl.tdata = {}
        tp.mtpl.ttype = {}
        tp.mtpl._modfolder2mod = {}
        tp.mtpl._mod2fname = {}
        tp.mtpl._import = {}
        tp.mtpl._read_mtpl_test(f'{UT_DIR_REPO}/Simple8/TPL/ProgramFlowsTestPlan/ProgramFlows.mtpl', modules=None)
        self.assertEqual(tp.mtpl.tdata, {})
        self.assertEqual(tp.mtpl.ttype, {})
        self.assertEqual(tp.mtpl.get_modfolder2mod(), {'ARR': 'ARR',
                                                       'SCN': 'SCN'})
        self.assertEqual({_mod: os.path.normpath(_path) for _mod, _path in tp.mtpl.get_mod2fname().items()},
                         {'ARR': os.path.normpath(f'{UT_DIR_REPO}/Simple8/TPL/./Modules/ARR/array.mtpl'),
                          'SCN': os.path.normpath(f'{UT_DIR_REPO}/Simple8/TPL/./Modules/SCN/scan.mtpl')})

    def test_param_undefined(self):
        # via pgmrule
        tp = TestProgram(UT_DIR_REPO + '/Simple8/TPL/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tp.init()

            File(join(tdir, 'Modules/SCN/TPIE_pgmRules_SCN.txt')).touch(mkdir=True)
            File(join(tdir, 'Modules/ARR/TPIE_pgmRules_ARR.txt')).touch('''
# undefined param
preinstance1 = "4",   Template,   CCB : *,*,*,*,*,*,*,*,*,*,*,*,ALL
''', mkdir=True)
            tp.pgmrules._pgm_files = {}
            tp.tpldir = tdir
            tp.pgmrules.apply()
            tp.mtpl.eval_params()
            self.assertEqual(tp.mtpl.get_instance('ARR', 'CCB')['preinstance1'], '4')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_is_bypassed(self):
        tp = TestProgram(f'{UT_DIR}/14P_small/TPL/EnvironmentFile.env').pickle_init()
        # bypass case
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'bypass_global': '1'}), True)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': '1'}), True)
        # not bypass case
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'a': 1}), False)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'bypass_global': '-1'}), False)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': '-1'}), False)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'bypass_global': ''}), False)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': ''}), False)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': 1}), True)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': 0}), True)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': 2}), True)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'bypass_global': 0}), False)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': -1}), False)
        self.assertEqual(tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': '-6a'}, safe=False), False)

        # assert cases
        with self.assertRaisesRegex(AssertionError, 'Error on a: .-6a. is not a 1 or -1'):
            tp.mtpl.is_bypassed('a', 'a', dd={'BypassPort': '-6a'})

        # integration
        self.assertEqual(tp.mtpl.is_bypassed('TPI_BASE', 'CTRL_X_PAUS_K_FIVR_FF_X_X_X_X_DELAY'), True)
        self.assertEqual(tp.mtpl.is_bypassed('TPI_BASE', 'CTRL_X_UTIL_K_IOBIN_X_X_X_X_PWRTCSETCPU'), False)

    def test_get_instance_to_subflows(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env').init()
        self.assertEqual(tp.mtpl.get_instance_to_subflows(),
                         {('ARR', 'CCA'): {'ARR::MAIN1', 'MAIN'},
                          ('ARR', 'CCB'): {'ARR::MAIN1', 'MAIN'},
                          ('ARR', 'TPIE_PgmRules'): {'ARR::INIT1', 'ARR::MAIN1', 'INIT', 'MAIN'},
                          ('SCN', 'CCA'): {'MAIN', 'SCN::MAIN2'},
                          ('SCN', 'CCB'): {'MAIN', 'SCN::MAIN2'},
                          ('SCN', 'TPIE_PgmRules'): {'SCN::INIT2', 'INIT'}})
        # parent
        dd = {'B': {'A'},
              'C': {'B'},
              'D': {'C'},
              'E': {'B'}}
        self.assertEqual(tp.mtpl._parents(dd, 'D', set()), {'B', 'C', 'A'})
        self.assertEqual(tp.mtpl._parents(dd, 'E', set()), {'B', 'A'})
        self.assertEqual(tp.mtpl._parents(dd, 'C', set()), {'B', 'A'})
        self.assertEqual(tp.mtpl._parents(dd, 'B', set()), {'A'})

    @with_(TempDir, chdir=True)
    def test_read_comments(self):
        File('a.mtpl').touch('''
# start
Version1.0;

# comment 0

Test iCSimpleScoreboardTest Test1     # comment1
{
        # comment2
        base_number = "2160 # xyz" + "5120 # zzz";    # comment3
        bypass_global = "1";
}

# comment4

MultiTrialTest Test2 {
   TrialTest blah blah {
    PassFail Fail;    # comment5
    TrialParam bypass_global = "1";      # comment6
}
} # comment7
''')
        comment_full, comment_eol = Mtpl.read_comments('a.mtpl')
        self.assertEqual(comment_full, {'Test1': ['# comment1',
                                                  '# comment2'],
                                        'Test2': ['# comment5',
                                                  '# comment7']})

        self.assertEqual(comment_eol, {'Test1': {'base_number': '# comment3'},
                                       'Test2': {'bypass_global': '# comment6'}})

    @with_(TempDir, chdir=True)
    def test_read_dutflow_comments(self):
        File('a.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

# VminTC comment
CSharpTest VminTC Instance1
{
     TrialParam bypass_global = "1";      # comment6
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2    # Comment 3
        {
            Property PassFail = "Fail"; # Comment 1
            ##EDC## SetBin b99440101_fail_FAIL_DPS_ALARM_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE_n1; # Comment 2
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97444400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN_4;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191900_fail_FUN_RESET_PORT5_SHARED_BIN_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}
''')
        comment_full, comment_eol = Mtpl.read_dutflow_comments('a.mtpl')

        pprint(comment_full)
        self.assertEqual(comment_full, {'Instance1': ['# Comment 3',
                                                      '##EDC## SetBin b99440101_fail_FAIL_DPS_ALARM_n2;',
                                                      '##EDC## SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE_n1; # Comment 2',
                                                      '##EDC## SetBin b44000000_fail_FUN_Instance1_0;',
                                                      '##EDC## SetBin b44000001_fail_FUN_Instance1_2;']})

        pprint(comment_eol)
        self.assertEqual(comment_eol, {'Instance1': {'PassFail': '# Comment 1'}})

    def test_mtpl_fail(self):

        with TempDir(name=True) as tdir:
            code = """
Test iCSimpleScoreboardTest CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST
{
        base_number = 2160;
        bypass_global = "1"
}

"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            with self.assertRaisesRegex(ErrorInput, 'Invalid line inside Test block CCF_XXXXX_FUNC_E_END_080812_X_F1_'
                                                    '0800_RETENTION_ALL_TEST'):
                obj.read_mtpls()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_set_minmaxnom(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')

        data = [('FUN', 'a_MAX_1', {'patlist': 'list1',
                                    'level': 'something_NOM_something'}, {}),
                ('AR1', 'a_NOM_1', {'patlist': 'list3a',
                                    'levels': 'something_max_something'}, {}),
                ('AR2', 'something_min_something', {'patlist': 'list3b',
                                                    'timing': 1}, {}),    # missing levels
                ('AR2', 'something_vmin_something2', {'patlist': 'list3b',
                                                      'levels': 'something_something'}, {}),  # levels missing value
                ('MIO', 'test3a', {'patlist': 'list1'}, {}),
                ]

        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=data)):
            tp.mtpl.set_tn_attrib()
            self.assertEqual(tp.mtpl.set_tn_attrib(), 1)    # re-run, should be ignored
            self.assertEqual(tp.mtpl.set_tn_attrib(reset=True), None)

            res = {}
            for md, tn, dd, ports in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=False, keyparam='patlist',
                                                        idict=True):
                res[(md, tn)] = dd['_CORNER']
            self.assertEqual(res, {('FUN', 'a_MAX_1'): 'nom',
                                   ('AR1', 'a_NOM_1'): 'max',
                                   ('AR2', 'something_min_something'): 'min',
                                   ('AR2', 'something_vmin_something2'): 'vmin',
                                   ('MIO', 'test3a'): 'UNK'})

        # unittests
        data = {}
        tp.mtpl._set_minmaxnom('ARR', 'X_X_X_K_X_X_MIN_X_X', data)
        self.assertEqual(data, {'_CORNER': 'MIN'})
        data = {}
        tp.mtpl._set_minmaxnom('ARR', 'X_X_X_K_X_X_X_X_X', data)
        self.assertEqual(data, {'_CORNER': 'UNK'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_set_freq(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')

        data = [('FUN', 'TAP_PCH_X_400_X', {'patlist': 'list1'}, {}),
                ('AR1', 'TAP_PCH_X_4000_X', {'patlist': 'list3a'}, {}),
                ('AR2', 'TAP_PCH_080808_40000_X', {'patlist': 'list3b'}, {}),
                ('MIO', 'TAP_PCH_X_F2_X', {'patlist': 'list1'}, {}),
                ('MIO', 'TAP_PCH_X_4GHZ_X', {'patlist': 'list1'}, {}),
                ('MIO', 'TAP_PCH_X_200mhz_X', {'patlist': 'list1'}, {}),
                ('MIO', 'TAP_PCH_X_10_1000', {'patlist': 'list1'}, {}),
                ('MIO', 'TAP_PCH_F1_4000_1000', {'patlist': 'list1'}, {}),
                ]

        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=data)):
            tp.mtpl.set_tn_attrib()
            res = {}
            for md, tn, dd, ports in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=False, keyparam='patlist',
                                                        idict=True):
                res[(md, tn)] = dd['_FREQ']
            Dumper(res)
            self.assertEqual(res, {('AR1', 'TAP_PCH_X_4000_X'): '4000',
                                   ('AR2', 'TAP_PCH_080808_40000_X'): '40000',
                                   ('FUN', 'TAP_PCH_X_400_X'): '400',
                                   ('MIO', 'TAP_PCH_F1_4000_1000'): '4000',
                                   ('MIO', 'TAP_PCH_X_200mhz_X'): '200mhz',
                                   ('MIO', 'TAP_PCH_X_4GHZ_X'): '4GHZ',
                                   ('MIO', 'TAP_PCH_X_F2_X'): 'F2',
                                   ('MIO', 'TAP_PCH_X_10_1000'): 'NONE'})

        # unittests
        data = {}
        tp.mtpl._set_freq('ARR', 'X_X_X_K_X_X_X_X_1000', data)
        self.assertEqual(data, {'_FREQ': '1000'})

        data = {}
        tp.mtpl._set_freq('ARR', 'X_X_X_K_X_X_X_F1_X', data)
        self.assertEqual(data, {'_FREQ': 'F1'})
        data = {}

        tp.mtpl._set_freq('ARR', 'X_X_X_K_X_X_1000_X_X', data)
        self.assertEqual(data, {'_FREQ': '1000'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_set_edckill(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')

        data = [  # KILL
            ('FUN', 'TAP_PCH_X_400_X', {'patlist': 'list1'},
             {0: {'SetBin': 'SoftBins', 'PassFail': 'Fail'}}),
            # EDC
            ('AR1', 'TAP_PCH_X_4000_X', {'patlist': 'list3a'},
             {0: {'PassFail': 'Fail'}}),
            # no port 0 - EDC
            ('AR2', 'TAP_PCH_080808_40000_X', {'patlist': 'list3b'},
             {2: {'SetBin': 'SoftBins', 'PassFail': 'Fail'}}),
            # no port at all - EDC
            ('MIO', 'TAP_PCH_X_F2_X', {'patlist': 'list1'},
             {}),
            # EDC, no PassFail info
            ('AR1', 'TAPX', {'patlist': 'list3a'},
             {0: {'SetBin': 'Softbins'}}),
            # No patlist
            ('MIO', 'CEP_PCH_X_400_X', {},
             {0: {'SetBin': 'SoftBins', 'PassFail': 'Fail'}}),
        ]

        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=data)):
            tp.mtpl.set_tn_attrib()
            res = {}
            for md, tn, dd, ports in tp.mtpl.iter_flows():
                res[(md, tn)] = dd.get('_EDCKIL', 'NA')
            Dumper(res)
            self.assertEqual(res, {('FUN', 'TAP_PCH_X_400_X'): 'KIL',
                                   ('AR1', 'TAP_PCH_X_4000_X'): 'EDC',
                                   ('AR2', 'TAP_PCH_080808_40000_X'): 'EDC',
                                   ('MIO', 'TAP_PCH_X_F2_X'): 'EDC',
                                   ('AR1', 'TAPX'): 'EDC',
                                   ('MIO', 'CEP_PCH_X_400_X'): 'KIL'})

    def test_set_edckill2(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env')

        # basic case
        tp.mtpl.set_tn_attrib()

        res = {}
        for md, tn, dd in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=False, idict=True):
            res[(md, tn)] = dd.get('_EDCKIL', 'NA')
        self.assertEqual(res, {('ARR', 'CCA'): 'EDC',
                               ('ARR', 'CCB'): 'EDC',
                               ('ARR', 'TPIE_PgmRules'): 'NA',
                               ('SCN', 'CCA'): 'EDC',
                               ('SCN', 'CCB'): 'EDC'})

        # test plan use
        tp.mtpl.set_tn_attrib(reset=True, keyparam=False)
        res = {}
        for md, tn, dd in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=False, idict=True):
            res[(md, tn)] = dd.get('_EDCKIL', 'NA')
        self.assertEqual(res, {('ARR', 'CCA'): 'EDC',
                               ('ARR', 'CCB'): 'EDC',
                               ('ARR', 'TPIE_PgmRules'): 'EDC',
                               ('SCN', 'CCA'): 'EDC',
                               ('SCN', 'CCB'): 'EDC'})

        result = []
        for item in tp.mtpl.iter_flows_multi('MAIN,INIT', passonly=False, bypass=False):
            result.append(item)
        expect = '''
[('ARR', 'CCA'),
 ('ARR', 'CCB'),
 ('ARR', 'TPIE_PgmRules'),
 ('SCN', 'CCA'),
 ('SCN', 'CCB'),
 ('ARR', 'TPIE_PgmRules'),
 ('SCN', 'TPIE_PgmRules')]
'''
        self.assertTextEqual(pformat(result), expect)

    def test_set_tn_attrib(self):
        # make sure tdata and edata are equivalent after set_tn_attrib()
        tp = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env')
        tp.mtpl.init_read()
        tp.mtpl.eval_params()
        self.assertEqual(len(list(iter_levels(tp.mtpl.tdata, 3))), 29)
        self.assertEqual(len(list(iter_levels(tp.mtpl.edata, 3))), 29)
        tp.mtpl.set_tn_attrib()
        self.assertEqual(len(list(iter_levels(tp.mtpl.tdata, 3))), 41)
        self.assertEqual(len(list(iter_levels(tp.mtpl.edata, 3))), 41)

    def test_ituff_tnames(self):
        with TempDir(chdir=True):
            File('a.ituff').touch('''
2_tname_NSIO_CSI_SXM::RTERM_CSI_CMEM_K
2_tname_testtime_NSIO_CSI_SXM::RCOMP_B
2_tname_testtime_IP_CPU::ARR::RCOMP_C
2_tname_testtime_RCOMP_A
2_tname_NSIO_CSI_SXM::RTERM_CSI_CMEM_Y
''')
            self.assertEqual(Mtpl.ituff_tnames(None), set())
            self.assertEqual(Mtpl.ituff_tnames('a.ituff'), {(None, 'RCOMP_A'),
                                                            ('NSIO_CSI_SXM', 'RCOMP_B'),
                                                            ('ARR', 'RCOMP_C')})


class FlowTest(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, not needed for coverage"))
    def test_regress(self):
        res = []
        print('TGL81 start==========')
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        tp.mtpl.read_mtpls()   # Note: This test does not read usrv. Item 3 below is different if usrv is read.
        tp.mtpl.eval_params()
        res.append((1, len(list(tp.mtpl.iter_flows(passonly=True))), 6275))   # total instances
        res.append((2, len(list(tp.mtpl.iter_flows(passonly=True, uniq=False))), 16121))  # total instances in pass flow
        res.append((3, len(list(tp.mtpl.iter_flows(passonly=True, bypass=True))), 4362))  # consider bypass
        res.append((4, len(list(tp.mtpl.iter_flows(passonly=False, uniq=False))), 35044))  # total instances
        res.append((5, len(list(tp.mtpl.iter_flows(passonly=False, uniq=True))), 7611))  # total instances

        print("ICL start==========")
        tp = TestProgram(f'{UT_DIR}/ICLXXXXXXH58G2XS904/TPL/EnvironmentFile_CLASS_ICL_42_U.env',
                         stpl='SubTestPlan_CLASS_ICL_42_U.stpl')
        res.append((6, len(list(tp.mtpl.iter_flows(passonly=True))), 4967))   # total instances in pass flow
        res.append((7, len(list(tp.mtpl.iter_flows(passonly=False))), 6898))   # total instances

        print("ICX start==========")
        tp = TestProgram(f'{UT_DIR}/ICXXXXXAXH10G10S922/EnvironmentFile_CLASS_HCCSP.env')
        res.append((8, len(list(tp.mtpl.iter_flows(passonly=True))), 3358))   # total instances in pass flow
        res.append((9, len(list(tp.mtpl.iter_flows(passonly=False))), 3884))   # total instances

        print('TGL42 start==========')
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        res.append((10, len(list(tp.mtpl.iter_flows(passonly=True))), 6237))  # total instances in pass flow
        res.append((11, len(list(tp.mtpl.iter_flows(passonly=False))), 8500))
        res.append((12, len(list(tp.mtpl.iter_flows(passonly=False, uniq=False))), 33202))   # total instances in pass flow
        res.append((13, len(list(tp.mtpl.iter_flows(flownames=True, passonly=False, uniq=True))), 10924))

        print(f'Total File._ADV_CNT: {OtplFile._ADV_CNT}')

        # build the compare expression
        result = [(x[0], x[1]) for x in res]
        expect = [(x[0], x[2]) for x in res]
        self.assertEqual(result, expect)

    def test_flow_basic(self):
        # This tests parallel flow, bypass, composites

        with TempDir(name=True) as tdir:
            code = """Version 1.0;
ConcurrentFlow PRL4_SubFlow [Parallel] {
        ConcurrentFlowItem              IP_CPU          ARR::PRL1;
        ConcurrentFlowItem              IP_PCH          ARR::PRL2;
        ConcurrentResultTable (IP_CPU, IP_PCH, EffectiveIPResult) {
                1,      *,      IP_PCH;
} }
DUTFlow MAIN {
        DUTFlowItem TPI_BASE_MAIN IP_CPU::ARR::TPI_BASE_MAIN@EDC {
                Result 1
                {
                        Property PassFail = "Pass";
                        GoTo PRL4_SubFlow;
        } }
        DUTFlowItem PRL4_SubFlow PRL4_SubFlow {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo END_SubFlow;
        } }
        DUTFlowItem END_SubFlow END_SubFlow {
                Result 1
                {
                        Property PassFail = "Pass";
                    Return 1;
        } }
}
DUTFlow END_SubFlow {
        DUTFlowItem TPI_BASE_BEGIN ARR::TPI_BASE_BEGIN {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;
} } }
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCA {
        bypass_global = "0";
}
Test iCFuncTest CCB {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCC {
        bypass_global = "1";
}
Test iCSimpleScoreboardTest CCD {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCE {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCF {
        bypass_global = "0";
}
DUTFlow TPI_BASE_MAIN  {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCB;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCF;
                        Return  1;

        } }
        DUTFlowItem CCF CCF {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

        } }
        DUTFlowItem CCB CCB {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;
                        GoTo PRL1;
        } }
        DUTFlowItem PRL1 PRL1 {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

        } }
} } }
DUTFlow TPI_BASE_BEGIN  {
        DUTFlowItem SubFlow1 SubFlow1 {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow SubFlow1  {
        DUTFlowItem CCC CCC {
                Result 2 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL1  {
        DUTFlowItem CCD CCD {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL2  {
        DUTFlowItem CCE CCE @EDC @A {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
"""
            # flow:
            #   A ->   F  ->    D    ->   E    ->      C
            # MAIN   MAIN    IP_CPU    IP_PCH     END_Subflow
            #   v             PRL1      PRL2
            #   B -> D
            #
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()
            self.assertEqual(obj._dutflow['PRL4_SubFlow'],
                             {'IP_CPU': {0: {'Return': '0'}, 1: {'GoTo': 'IP_PCH', 'Return': '1'}, 999: 'ARR::PRL1'},
                              'IP_PCH': {0: {'Return': '0'}, 1: {'Return': '1'}, 999: 'ARR::PRL2'},
                              '_ORDER': ['IP_CPU', 'IP_PCH']})

            # dutflow_order
            dutflow_order = obj.get_dutflow_map(order=True)
            self.assertEqual(list(dutflow_order),
                             ['ARR::TPI_BASE_MAIN',
                              'ARR::TPI_BASE_BEGIN',
                              'ARR::SubFlow1',
                              'ARR::PRL1',
                              'ARR::PRL2',
                              'PRL4_SubFlow',
                              'MAIN',
                              'END_SubFlow'])
            self.assertEqual(dutflow_order['MAIN'], 'DUTFlow')
            # dutflow_at
            dutflow_at = obj.get_dutflow_map(at=True)
            self.assertEqual(dutflow_at, {('MAIN', 'TPI_BASE_MAIN'): '@EDC',
                                          ('ARR::PRL2', 'CCE'): '@EDC @A'})

            # all flows
            self.assertEqual(list(obj.iter_flows(traceinfo=True)),
                             [('ARR', 'CCA', ['MAIN', 'ARR::TPI_BASE_MAIN']),
                              ('ARR', 'CCB', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA']),
                              ('ARR', 'CCD', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA', 'ARR::PRL1']),
                              ('ARR', 'CCF', ['MAIN', 'ARR::TPI_BASE_MAIN']),
                              ('ARR', 'CCE', ['MAIN', 'PRL4_SubFlow', 'ARR::PRL2']),
                              ('ARR', 'CCC', ['MAIN', 'END_SubFlow', 'ARR::TPI_BASE_BEGIN', 'ARR::SubFlow1'])]
                             )

            # pass only
            self.assertEqual(list(obj.iter_flows(passonly=True)),
                             [('ARR', 'CCA'),
                              ('ARR', 'CCF'),    # passonly
                              ('ARR', 'CCD'),
                              ('ARR', 'CCE'),
                              ('ARR', 'CCC')
                              ])

            # pass only, consider bypass
            self.assertEqual(list(obj.iter_flows(passonly=True, bypass=True)),
                             [('ARR', 'CCA'),
                              ('ARR', 'CCF'),    # passonly
                              ('ARR', 'CCD'),
                              ('ARR', 'CCE')
                              ])

            # forced fail specific dutflow
            self.assertEqual(list(obj.iter_flows(passonly={'CCA': 0})),
                             [('ARR', 'CCA'),     # forced fail
                              ('ARR', 'CCB'),
                              ('ARR', 'CCD'),
                              ('ARR', 'CCE'),
                              ('ARR', 'CCC')
                              ])
            self.assertEqual(list(obj.iter_flows(flownames=True, passonly={'CCA': 0}, uniq=True)),
                             [('ARR', 'ARR::TPI_BASE_MAIN', 'CCA'),
                              ('ARR', 'ARR::TPI_BASE_MAIN', 'CCB'),
                              ('ARR', 'ARR::PRL1', 'CCD'),
                              ('ARR', 'ARR::PRL2', 'CCE'),
                              ('ARR', 'ARR::SubFlow1', 'CCC')])
            self.assertEqual(obj.get_flow_ports('ARR::TPI_BASE_MAIN', 'CCA'),
                             {0: {'PassFail': 'Pass', 'GoTo': 'CCB'}, 1: {'PassFail': 'Pass', 'GoTo': 'CCF', 'Return': '1'}})

            # template
            self.assertEqual(list(obj.iter_flows(template='iCSimpleScoreboardTest')),
                             [('ARR', 'CCA'),
                              ('ARR', 'CCD'),
                              ('ARR', 'CCF'),
                              ('ARR', 'CCE'),
                              ('ARR', 'CCC'),
                              ])

            self.assertEqual(len(obj.get_instance_to_subflows()), 6)
            self.assertEqual(len(list(keys_atlevel(obj.get_instance_to_subflows(), 1))), 17)
            self.assertEqual(len(obj.get_subflows(include_composite=True)), 8)
            self.assertEqual(len(obj.get_subflows()), 3)
            self.assertEqual(obj.get_dutflow_map(), obj._dutflow)

    def test_flow_basic_4_IPs_iDUT(self):
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
ConcurrentFlow PRL4_SubFlow [Parallel] {
        ConcurrentFlowItem              IPC          ARR::PRL1;
        ConcurrentFlowItem              IPH          ARR::PRL2;
        ConcurrentFlowItem              IPG          ARR::PRL3;
        ConcurrentFlowItem              IPP          ARR::PRL4;
        ConcurrentResultTable (IPC, IPH, IPG, IPP, EffectiveIPResult) {
                1,      *,      *,      *,      IPC;
                [*:0],      *,      *,      *,      IPH;
                1,      [*:0],      *,      *,      IPG;
                [2:*],      *,      *,      *,      IPP;
                [2:*],      *,      *,      *,      IPC;
} }
DUTFlow MAIN {
        DUTFlowItem TPI_BASE_MAIN IP_CPU::ARR::TPI_BASE_MAIN@EDC {
                Result 1
                {
                        Property PassFail = "Pass";
                        GoTo PRL4_SubFlow;
        } }
        DUTFlowItem PRL4_SubFlow PRL4_SubFlow {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo END_SubFlow;
        } }
        DUTFlowItem END_SubFlow END_SubFlow {
                Result 1
                {
                        Property PassFail = "Pass";
                    Return 1;
        } }
}
DUTFlow END_SubFlow {
        DUTFlowItem TPI_BASE_BEGIN ARR::TPI_BASE_BEGIN {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;
} } }
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCA {
        bypass_global = "0";
}
Test iCFuncTest CCB {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCC {
        bypass_global = "1";
}
Test iCSimpleScoreboardTest CCD {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCE {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCF {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCG {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCH {
        bypass_global = "0";
}
DUTFlow TPI_BASE_MAIN  {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCB;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCF;
                        Return  1;

        } }
        DUTFlowItem CCF CCF {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

        } }
        DUTFlowItem CCB CCB {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;
                        GoTo PRL1;
        } }
        DUTFlowItem PRL1 PRL1 {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

        } }
} } }
DUTFlow TPI_BASE_BEGIN  {
        DUTFlowItem SubFlow1 SubFlow1 {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow SubFlow1  {
        DUTFlowItem CCC CCC {
                Result 2 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL1  {
        DUTFlowItem CCD CCD {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL2  {
        DUTFlowItem CCE CCE @EDC @A {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL3  {
        DUTFlowItem CCG CCG @EDC @A {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL4  {
        DUTFlowItem CCH CCH @EDC @A {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
"""
            # flow:
            #   A ->   F  ->    D    ->   E    ->  F   ->  G    ->      C
            # MAIN   MAIN      IPC       IPH     IPG      IPP     END_Subflow
            #   v             PRL1      PRL2     PRL3     PRL4
            #   B -> D
            #
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()
            self.assertEqual(obj._dutflow['PRL4_SubFlow'],
                             {'IPC': {0: {'Return': '0'}, 1: {'GoTo': 'IPH', 'Return': '1'}, 999: 'ARR::PRL1'},
                              'IPH': {0: {'Return': '0'}, 1: {'GoTo': 'IPG', 'Return': '1'}, 999: 'ARR::PRL2'},
                              'IPG': {0: {'Return': '0'}, 1: {'GoTo': 'IPP', 'Return': '1'}, 999: 'ARR::PRL3'},
                              'IPP': {0: {'Return': '0'}, 1: {'Return': '1'}, 999: 'ARR::PRL4'},
                              '_ORDER': ['IPC', 'IPH', 'IPG', 'IPP']})

    def test_flow_basic2(self):
        # This tests pass/fail/all ports
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
DUTFlow MAIN {
        DUTFlowItem TPI_BASE_MAIN IP_CPU::ARR::TPI_BASE_MAIN {
                Result 1 {
                        Property PassFail = "Pass";
                    Return 1;
                }
        }
}
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCA {
        bypass_global = "0";
}
Test iCFuncTest CCB {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCC {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCD {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCE {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCF {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCG {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCH {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCI {
        bypass_global = "0";
        Result = "something";
}
DUTFlow TPI_BASE_MAIN  {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCF;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCB;
                }
                Result 2 {
                        Property PassFail = "Pass";
                        GoTo CCE;

        } }
        DUTFlowItem CCB CCB {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCC;
        } }
        DUTFlowItem CCE CCE {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCC;
        } }
        DUTFlowItem CCC CCC {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCD;
        } }
        DUTFlowItem CCD CCD {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        GoTo CCI;
        } }
        DUTFlowItem CCF CCF {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCG;
        } }
        DUTFlowItem CCG CCG {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCH;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1 ;     # Do not change space after ;
        } }
        DUTFlowItem CCH CCH {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
        } }
        DUTFlowItem CCI CCI {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
        } }
}
"""
            # flow:
            #   A -->   B  -->    C    ->   D
            #   | \->   E  -/               |
            #   |                           I
            #   F  ->   G
            #           |
            #           H
            #
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()

            # all flows
            result = list(obj.iter_flows(traceinfo=True))
            Dumper(result)
            self.assertEqual(result,
                             [('ARR', 'CCA', ['MAIN', 'ARR::TPI_BASE_MAIN']),
                              ('ARR', 'CCE', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA']),
                              ('ARR', 'CCC', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA']),
                              ('ARR', 'CCD', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA']),
                              ('ARR', 'CCI', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA', 'port=2 of CCD']),
                              ('ARR', 'CCF', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA']),
                              ('ARR', 'CCG', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA']),
                              ('ARR', 'CCH', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA', 'port=0 of CCG']),
                              ('ARR', 'CCB', ['MAIN', 'ARR::TPI_BASE_MAIN'])])

            # pass only
            self.assertEqual(list(obj.iter_flows(passonly=True)),
                             [('ARR', 'CCA'),
                              ('ARR', 'CCE'),
                              ('ARR', 'CCC'),
                              ('ARR', 'CCD'),
                              ('ARR', 'CCB')])

            self.assertEqual(obj.dict_flows(),
                             {('ARR', 'CCA'): 'P',
                              ('ARR', 'CCB'): 'P',
                              ('ARR', 'CCC'): 'P',
                              ('ARR', 'CCD'): 'P',
                              ('ARR', 'CCE'): 'P',
                              ('ARR', 'CCF'): 'F',
                              ('ARR', 'CCG'): 'F',
                              ('ARR', 'CCH'): 'F',
                              ('ARR', 'CCI'): 'F'})

    def test_flow_empty(self):
        # This tests empty DUTFlow - TPI_BASE_MAIN2
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
DUTFlow MAIN {
        DUTFlowItem TPI_BASE_MAIN IP_CPU::ARR::TPI_BASE_MAIN {
                Result 1 {
                        Property PassFail = "Pass";
                    GoTo TPI_BASE_MAIN2;
                }
        }
        DUTFlowItem TPI_BASE_MAIN2 IP_CPU::ARR::TPI_BASE_MAIN2 {
                Result 1 {
                        Property PassFail = "Pass";
                    Return 1;
                }
        }
}
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCA {
        bypass_global = "0";
}
Test iCFuncTest CCB {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCC {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCD {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCE {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCF {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCG {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCH {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCI {
        bypass_global = "0";
        Result = "something";
}
DUTFlow TPI_BASE_MAIN2  {
}
DUTFlow TPI_BASE_MAIN  {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCF;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCB;
                }
                Result 2 {
                        Property PassFail = "Pass";
                        GoTo CCE;

        } }
        DUTFlowItem CCB CCB {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCC;
        } }
        DUTFlowItem CCE CCE {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCC;
        } }
        DUTFlowItem CCC CCC {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCD;
        } }
        DUTFlowItem CCD CCD {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        GoTo CCI;
        } }
        DUTFlowItem CCF CCF {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCG;
        } }
        DUTFlowItem CCG CCG {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCH;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1 ;     # Do not change space after ;
        } }
        DUTFlowItem CCH CCH {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
        } }
        DUTFlowItem CCI CCI {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
        } }
}
"""

            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()

            # all flows
            result = list(obj.iter_flows(traceinfo=True))
            Dumper(result)
            self.assertEqual(result,
                             [('ARR', 'CCA', ['MAIN', 'ARR::TPI_BASE_MAIN']),
                              ('ARR', 'CCE', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA']),
                              ('ARR', 'CCC', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA']),
                              ('ARR', 'CCD', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA']),
                              ('ARR', 'CCI', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=2 of CCA', 'port=2 of CCD']),
                              ('ARR', 'CCF', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA']),
                              ('ARR', 'CCG', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA']),
                              ('ARR', 'CCH', ['MAIN', 'ARR::TPI_BASE_MAIN', 'port=0 of CCA', 'port=0 of CCG']),
                              ('ARR', 'CCB', ['MAIN', 'ARR::TPI_BASE_MAIN'])])

            # pass only
            self.assertEqual(list(obj.iter_flows(passonly=True)),
                             [('ARR', 'CCA'),
                              ('ARR', 'CCE'),
                              ('ARR', 'CCC'),
                              ('ARR', 'CCD'),
                              ('ARR', 'CCB')])

            self.assertEqual(obj.dict_flows(),
                             {('ARR', 'CCA'): 'P',
                              ('ARR', 'CCB'): 'P',
                              ('ARR', 'CCC'): 'P',
                              ('ARR', 'CCD'): 'P',
                              ('ARR', 'CCE'): 'P',
                              ('ARR', 'CCF'): 'F',
                              ('ARR', 'CCG'): 'F',
                              ('ARR', 'CCH'): 'F',
                              ('ARR', 'CCI'): 'F'})

    def test_flow_infinite(self):
        # SRH case of infinite loop
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
DUTFlow MAIN {
        DUTFlowItem TPI_BASE_MAIN IP_CPU::ARR::TPI_BASE_MAIN {
                Result 1 {
                        Property PassFail = "Pass";
                    Return 1;
                }
        }
}
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCA {
        bypass_global = "0";
}
Test iCFuncTest CCB {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCC {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCD {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCE {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCF {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCG {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCH {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCI {
        bypass_global = "0";
}
DUTFlow TPI_BASE_MAIN  {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCF;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCB;
                }
                Result 2 {
                        Property PassFail = "Pass";
                        GoTo CCE;

        } }
        DUTFlowItem CCB CCB {
                Result 2 {
                        Property PassFail = "Pass";
                        GoTo CCC;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCA;
        } }
        DUTFlowItem CCE CCE {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCC;
        } }
        DUTFlowItem CCC CCC {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCD;
        } }
        DUTFlowItem CCD CCD {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        GoTo CCI;
        } }
        DUTFlowItem CCF CCF {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCG;
        } }
        DUTFlowItem CCG CCG {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCH;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1 ;     # Do not change space after ;
        } }
        DUTFlowItem CCH CCH {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
        } }
        DUTFlowItem CCI CCI {
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
        } }
}
"""
            # flow:
            #   A -->   B --> A   C    ->   D
            #   |\        \------/
            #   | \->   E ------/           |
            #   |                           I
            #   F  ->   G
            #           |
            #           H
            #
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()

            # all flows
            result = list(obj.iter_flows(passonly=True))
            self.assertEqual(result, [('ARR', 'CCA'),
                                      ('ARR', 'CCE'),
                                      ('ARR', 'CCC'),
                                      ('ARR', 'CCD'),
                                      ('ARR', 'CCB')])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_iter_flows(self):
        # Also tests get_flow_instance()
        # unittest, Mocked
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        items = [('M1::F1', 'bbb', ['t1']),
                 ('M1::F1', 'ccc', ['t2']),
                 ('M1::F1', 'bbb', ['t3'])]
        idd = {'patlist': 'a'}
        with MockVar(tp.mtpl, '_recurse_flow', Mock(return_value=items)),\
                MockVar(tp.mtpl, 'get_instance', Mock(return_value=(idd, idd))),\
                MockVar(tp.mtpl, 'read_mtpl_flow', Mock()):
            tp.mtpl._dutflow = {'MAIN': {'aaa': {999: 'aaa'}},
                                'M1::F1': {'bbb': {999: 'bbb'},
                                           'ccc': {999: 'SCN::ccc'},
                                           'ddd': {999: 'ddd'}}}

            self.assertEqual(list(tp.mtpl.iter_flows(uniq=False)),
                             [('M1', 'bbb'),
                              ('SCN', 'ccc'),
                              ('M1', 'bbb')])
            self.assertEqual(list(tp.mtpl.iter_flows(uniq=True)), [('M1', 'bbb'), ('SCN', 'ccc')])
            self.assertEqual(list(tp.mtpl.iter_flows(traceinfo=True, uniq=False)),
                             [('M1', 'bbb', ['t1']),
                              ('SCN', 'ccc', ['t2']),
                              ('M1', 'bbb', ['t3'])])
            self.assertEqual(list(tp.mtpl.iter_flows(idict=True, keyparam='patlist', uniq=False)),
                             [('M1', 'bbb', idd),
                              ('SCN', 'ccc', idd),
                              ('M1', 'bbb', idd)])
            self.assertEqual(list(tp.mtpl.iter_flows(keyparam='timings')), [])
            self.assertEqual(list(tp.mtpl.iter_flows(idict=True, pdict=True, keyparam='patlist', uniq=False)),
                             [('M1', 'bbb', idd, {999: 'bbb'}),
                              ('SCN', 'ccc', idd, {999: 'SCN::ccc'}),
                              ('M1', 'bbb', idd, {999: 'bbb'})])
            self.assertEqual(list(tp.mtpl.iter_flows(pdict=True, keyparam='patlist', uniq=False)),
                             [('M1', 'bbb', {999: 'bbb'}),
                              ('SCN', 'ccc', {999: 'SCN::ccc'}),
                              ('M1', 'bbb', {999: 'bbb'})])
            self.assertEqual(list(tp.mtpl.iter_flows(uniq=False, r_mod=re.compile('M1'))),
                             [('M1', 'bbb'),
                              ('M1', 'bbb')])

    def test_iter_flow_evaluated(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple9/TPL/EnvironmentFile.env').init()
        result = list(tp.mtpl.iter_flows(idict=True))
        self.assertEqual(result[0], ('ARR', 'CCA', {'TEMPLATE': 'iCSimpleScoreboardTest',
                                                    'bypass_global': '3',
                                                    'level': '"BASE::"+"DDR_univ_lvl_nom_lvl"',
                                                    'timings': 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'}))
        result = list(tp.mtpl.iter_flows(edict=True))
        self.assertEqual(result[0], ('ARR', 'CCA', {'TEMPLATE': 'iCSimpleScoreboardTest',
                                                    'bypass_global': 3,
                                                    'level': 'BASE::DDR_univ_lvl_nom_lvl',
                                                    'timings': 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'}))
        # iter_tests
        result = list(tp.mtpl.iter_tests('iCSimpleScoreboardTest'))
        self.assertEqual(result[0][2], {'TEMPLATE': 'iCSimpleScoreboardTest',
                                                    'bypass_global': '3',
                                                    'level': '"BASE::"+"DDR_univ_lvl_nom_lvl"',
                                                    'timings': 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'})
        result = list(tp.mtpl.iter_tests('iCSimpleScoreboardTest', edict=True))
        self.assertEqual(result[0][2], {'TEMPLATE': 'iCSimpleScoreboardTest',
                                                    'bypass_global': 3,
                                                    'level': 'BASE::DDR_univ_lvl_nom_lvl',
                                                    'timings': 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'})
        # without init
        tp = TestProgram(f'{UT_DIR_REPO}/Simple9/TPL/EnvironmentFile.env')
        result = list(tp.mtpl.iter_tests('iCSimpleScoreboardTest', edict=True))
        self.assertEqual(result[0][2], {'TEMPLATE': 'iCSimpleScoreboardTest',
                                                    'bypass_global': 0,   # pgmrules are not applied yet
                                                    'level': 'BASE::DDR_univ_lvl_nom_lvl',
                                                    'timings': 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_id_passport(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        # normal case
        dfi = {'aa': {3: 'yeah'}}
        self.assertEqual(tp.mtpl._id_passport(dfi, 'aa', {}), 3)

        # invalid input
        with self.assertRaisesRegex(ErrorInput, 'Specified passonly port=4 does not exist in aa'):
            tp.mtpl._id_passport(dfi, 'aa', {'aa': 4})

        # No valid port at all
        with self.assertRaisesRegex(ErrorCockpit, 'Cannot find any port to go in flowitem=aa'):
            tp.mtpl._id_passport({'aa': {}}, 'aa', {})

    def test_reader_basic(self):
        with TempDir(name=True) as tdir:
            code = """Version 1.0;

ProgramStyle = Modular;
TestPlan Flows;
DUTFlow CHKCPUF1_SubFlow
{
        DUTFlowItem TPI_BASE_CHKCPUF1 TPI_BASE::TPI_BASE_CHKCPUF1
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        Return -1;
                }
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
     DUTFlowItem PTH_DIODE PTH_DIODE_THRSOAK::PTH_DIODE_THRSOAK_START
        {
                Result 0
                {
                        Property PassFail = "Fail";
                        IncrementCounters ARR_CCF::n90971101_fail_SSA;
                        Return 3;
                }
                Result 1
                {
                        Property PassFail = "Pass";
                        IncrementCounters ARR_CCF:: n90971100_fail_SSA;
                        SetBin SoftBins.b90979712_fail_ARR_CCF_LSA_CCF_TDAU_K_END_XXXXXX_VUNCORE_F1_X_0_SHARED_BIN;
                        GoTo TPI_VCC_START;
                }
        }
}  # End of DUTFlow CHKCPUF1_SubFlow
DUTFlow CHKCPUF2_SubFlow
{
        DUTFlowItem TPI_BASE_CHKCPUF2 TPI_BASE::TPI_BASE_CHKCPUF2
        {
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
}
Flow CHKCPUF3_SubFlow
{
        FlowItem TPI_BASE_CHKCPUF3 TPI_BASE::TPI_BASE_CHKCPUF3
        {
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
}
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCF
{
        base_number = 2160;
        bypass_global = "1";
}
DUTFlow ARR1
{
        DUTFlowItem ARR2 ARR2
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        Return -1;
                }
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()
            obj.read_mtpl_flow()  # for coverage
            expect = {'ARR::ARR1': {'ARR2': {-1: {'PassFail': 'Fail', 'Return': '-1'},
                                             0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                             999: 'ARR2'},
                                    '_ORDER': ['ARR2']},
                      'CHKCPUF1_SubFlow': {'PTH_DIODE': {0: {'PassFail': 'Fail', 'Return': '3',
                                                             'IncrementCounters': 'ARR_CCF::n90971101_fail_SSA',
                                                             },
                                                         1: {'GoTo': 'TPI_VCC_START',
                                                             'IncrementCounters': 'ARR_CCF::n90971100_fail_SSA',
                                                             'PassFail': 'Pass',
                                                             'SetBin': 'SoftBins.b90979712_fail_ARR_CCF_LSA_CCF_TDAU_K_END_XXXXXX_VUNCORE_F1_X_0_SHARED_BIN'},
                                                         999: 'PTH_DIODE_THRSOAK::PTH_DIODE_THRSOAK_START'},
                                           'TPI_BASE_CHKCPUF1': {-1: {'PassFail': 'Fail', 'Return': '-1'},
                                                                 0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                                                 999: 'TPI_BASE::TPI_BASE_CHKCPUF1'},
                                           '_ORDER': ['TPI_BASE_CHKCPUF1', 'PTH_DIODE']},
                      'CHKCPUF2_SubFlow': {'TPI_BASE_CHKCPUF2': {0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                                                 999: 'TPI_BASE::TPI_BASE_CHKCPUF2'},
                                           '_ORDER': ['TPI_BASE_CHKCPUF2']},
                      'CHKCPUF3_SubFlow': {'TPI_BASE_CHKCPUF3': {0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                                                 999: 'TPI_BASE::TPI_BASE_CHKCPUF3'},
                                           '_ORDER': ['TPI_BASE_CHKCPUF3']}}

            self.assertEqual(obj._dutflow, expect)

    def test_reader_basic_edc_setbin(self):
        with TempDir(name=True) as tdir:
            code = """Version 1.0;

ProgramStyle = Modular;
TestPlan Flows;
DUTFlow CHKCPUF1_SubFlow
{
        DUTFlowItem TPI_BASE_CHKCPUF1 TPI_BASE::TPI_BASE_CHKCPUF1
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        Return -1;
                }
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
     DUTFlowItem PTH_DIODE PTH_DIODE_THRSOAK::PTH_DIODE_THRSOAK_START
        {
                Result 0
                {
                        Property PassFail = "Fail";
                        #IncrementCounters ARR_CCF::n90971101_fail_SSA;
                        Return 3;
                }
                Result 1
                {
                        Property PassFail = "Pass";
                        IncrementCounters ARR_CCF:: n90971100_fail_SSA;
                        ##EDC## SetBin SoftBins.b90979712_fail_ARR_CCF_LSA_CCF_TDAU_K_END_XXXXXX_VUNCORE_F1_X_0_SHARED_BIN;
                        GoTo TPI_VCC_START;
                }
        }
}  # End of DUTFlow CHKCPUF1_SubFlow
DUTFlow CHKCPUF2_SubFlow
{
        DUTFlowItem TPI_BASE_CHKCPUF2 TPI_BASE::TPI_BASE_CHKCPUF2
        {
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
}
Flow CHKCPUF3_SubFlow
{
        FlowItem TPI_BASE_CHKCPUF3 TPI_BASE::TPI_BASE_CHKCPUF3
        {
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
}
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCF
{
        base_number = 2160;
        bypass_global = "1";
}
DUTFlow ARR1
{
        DUTFlowItem ARR2 ARR2
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        Return -1;
                }
                Result 0
                {
                        Property PassFail = "Pass";
                        GoTo PTH_DIODE;
                }
        }
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_edc_setbin = True
            obj.read_mtpl_flow()
            obj.read_mtpl_flow()  # for coverage
            expect = {'ARR::ARR1': {'ARR2': {-1: {'PassFail': 'Fail', 'Return': '-1'},
                                             0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                             999: 'ARR2'},
                                    '_ORDER': ['ARR2']},
                      'CHKCPUF1_SubFlow': {'PTH_DIODE': {0: {'PassFail': 'Fail', 'Return': '3',
                                                             },
                                                         1: {'GoTo': 'TPI_VCC_START',
                                                             'IncrementCounters': 'ARR_CCF::n90971100_fail_SSA',
                                                             'PassFail': 'Pass',
                                                             'SetBin': 'SoftBins.b90979712_fail_ARR_CCF_LSA_CCF_TDAU_K_END_XXXXXX_VUNCORE_F1_X_0_SHARED_BIN'},
                                                         999: 'PTH_DIODE_THRSOAK::PTH_DIODE_THRSOAK_START'},
                                           'TPI_BASE_CHKCPUF1': {-1: {'PassFail': 'Fail', 'Return': '-1'},
                                                                 0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                                                 999: 'TPI_BASE::TPI_BASE_CHKCPUF1'},
                                           '_ORDER': ['TPI_BASE_CHKCPUF1', 'PTH_DIODE']},
                      'CHKCPUF2_SubFlow': {'TPI_BASE_CHKCPUF2': {0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                                                 999: 'TPI_BASE::TPI_BASE_CHKCPUF2'},
                                           '_ORDER': ['TPI_BASE_CHKCPUF2']},
                      'CHKCPUF3_SubFlow': {'TPI_BASE_CHKCPUF3': {0: {'GoTo': 'PTH_DIODE', 'PassFail': 'Pass'},
                                                                 999: 'TPI_BASE::TPI_BASE_CHKCPUF3'},
                                           '_ORDER': ['TPI_BASE_CHKCPUF3']}}

            self.assertEqual(obj._dutflow, expect)

    def test_reader_invalid(self):
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
TestPlan ARR;
DUTFlow ARR1
{
        DUTFlowItem ARR2 ARR2
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        Return -1;
                        invalid line 3;
                }
        }
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown mtpl flow line'):
                obj.read_mtpl_flow()

    def test_reader_passfail(self):
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
TestPlan ARR;
DUTFlow ARR1 {
        DUTFlowItem ARR2 ARR2 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        Property PassFail="Pass";
                        Return 1;
                }
                Result 2 {
                        PassFail Fail;
                        Return 2;
                }
                Result 3 {
                        PassFail  Pass;
                        Return 3;
                }
        }
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()
            pprint(obj._dutflow)
            expect = {'ARR::ARR1': {'ARR2': {0: {'PassFail': 'Fail', 'Return': '0'},
                                             1: {'PassFail': 'Pass', 'Return': '1'},
                                             2: {'PassFail': 'Fail', 'Return': '2'},
                                             3: {'PassFail': 'Pass', 'Return': '3'},
                                             999: 'ARR2'},
                                    '_ORDER': ['ARR2']}}
            self.assertEqual(obj._dutflow, expect)

    def test_reader_missing_passfail(self):
        # Test that missing PassFail property throws an error
        try:
            TestProgram._unit_test_protocol = 1  # enable checking for passfail property
            with TempDir(name=True) as tdir:
                code = """Version 1.0;
        """
                File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)
                code = """Version 1.0;
                TestPlan ARR;
                DUTFlow ARR1 {
                        DUTFlowItem ARR2 ARR2 {
                                Result 0 {
                                        Property PassFail = "Fail";
                                        Return 0;
                                }
                                Result 1 {
                                        Return 1;
                                }
                        }
                }
        """
                File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
                File('%s/a.stpl' % tdir).touch(code, mkdir=True)
                envfile = '%s/env.env' % tdir
                File(envfile).touch()
                tp = TestProgram(envfile, tpl='')._ut_write_stpl()
                obj = tp.mtpl
                with self.assertRaisesRegex(ErrorUser, 'Result 1.*is missing PassFail property'):
                    obj.read_mtpl_flow()
        finally:
            TestProgram._unit_test_protocol = 0  # reset after test

    def test_reader_valid_passfail_styles(self):
        # Test that both valid PassFail styles work
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
TestPlan ARR;
DUTFlow ARR1 {
        DUTFlowItem ARR2 ARR2 {
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        PassFail Pass;
                        Return 1;
                }
                Result -2 {
                        Property PassFail = "Fail";
                        Return -2;
                }
        }
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()
            # Should succeed without error
            expect = {'ARR::ARR1': {'ARR2': {0: {'PassFail': 'Fail', 'Return': '0'},
                                             1: {'PassFail': 'Pass', 'Return': '1'},
                                             -2: {'PassFail': 'Fail', 'Return': '-2'},
                                             999: 'ARR2'},
                                    '_ORDER': ['ARR2']}}
            self.assertEqual(obj._dutflow, expect)

    def test_reader_bi(self):
        # tests dutflow_info
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
TestPlan ARR;
DUTFlow ARR1 {
        DUTFlowItem ARR2 ARR2 [DUTSync] {
                Result 0 {
                        Property PassFail = "Fail";
                        GoTo ARR3;
                }
        }
        DUTFlowItem ARR3 ARR3 MinLoopDuration 100 {
                BreakLoopOn [-2,-1, 2];
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
        }
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()
            result = obj.get_dutflow_map(info=True)
            pprint(result)
            expect = {('ARR::ARR1', 'ARR2'): {'DUTSync': True},
                      ('ARR::ARR1', 'ARR3'): {'BreakLoopOn': '[-2,-1, 2]',
                                              'MinLoopDuration': '100'}}
            self.assertEqual(result, expect)

    def test_flow_dtag(self):
        # This tests whether the flow's dtag is correctly parsed

        with TempDir(name=True) as tdir:
            code = """Version 1.0;
ConcurrentFlow PRL4_SubFlow [Parallel] {
        ConcurrentFlowItem              IP_CPU          ARR::PRL1;
        ConcurrentFlowItem              IP_PCH          ARR::PRL2;
        ConcurrentResultTable (IP_CPU, IP_PCH, EffectiveIPResult) {
                1,      *,      IP_PCH;
} }
DUTFlow MAIN @EXAMPLE_DTAG {
        DUTFlowItem TPI_BASE_MAIN IP_CPU::ARR::TPI_BASE_MAIN@EDC {
                Result 1
                {
                        Property PassFail = "Pass";
                        GoTo PRL4_SubFlow;
        } }
        DUTFlowItem PRL4_SubFlow PRL4_SubFlow {
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo END_SubFlow;
        } }
        DUTFlowItem END_SubFlow END_SubFlow {
                Result 1
                {
                        Property PassFail = "Pass";
                    Return 1;
        } }
}
DUTFlow END_SubFlow {
        DUTFlowItem TPI_BASE_BEGIN ARR::TPI_BASE_BEGIN {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;
} } }
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            code = """Version 1.0;
TestPlan ARR;
Test iCSimpleScoreboardTest CCA {
        bypass_global = "0";
}
Test iCFuncTest CCB {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCC {
        bypass_global = "1";
}
Test iCSimpleScoreboardTest CCD {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCE {
        bypass_global = "0";
}
Test iCSimpleScoreboardTest CCF {
        bypass_global = "0";
}
DUTFlow TPI_BASE_MAIN  {
        DUTFlowItem CCA CCA {
                Result 0 {
                        Property PassFail = "Pass";
                        GoTo CCB;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        GoTo CCF;
                        Return  1;

        } }
        DUTFlowItem CCF CCF {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

        } }
        DUTFlowItem CCB CCB {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;
                        GoTo PRL1;
        } }
        DUTFlowItem PRL1 PRL1 {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

        } }
} } }
DUTFlow TPI_BASE_BEGIN  {
        DUTFlowItem SubFlow1 SubFlow1 {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow SubFlow1  {
        DUTFlowItem CCC CCC {
                Result 2 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL1  {
        DUTFlowItem CCD CCD {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
DUTFlow PRL2  {
        DUTFlowItem CCE CCE @EDC @A {
                Result 1 {
                        Property PassFail = "Pass";
                        Return  1;

} } }
"""
            # flow:
            #   A ->   F  ->    D    ->   E    ->      C
            # MAIN   MAIN    IP_CPU    IP_PCH     END_Subflow
            #   v             PRL1      PRL2
            #   B -> D
            #
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            File('%s/a.stpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            obj = tp.mtpl
            obj.read_mtpl_flow()
            at_map = tp.mtpl.get_dutflow_map(at=True)
            self.assertEqual(at_map[('MAIN', None)], '@EXAMPLE_DTAG')

    def test_iter_flows_coverage_lines_900_927(self):
        # Test coverage for lines 900 (r_mod filter) and 927 (uniq=False)
        with TempDir(name=True) as tdir:
            # Create a simple flow structure with multiple modules
            code = """Version 1.0;
DUTFlow MAIN {
    DUTFlowItem TEST1 MOD1::TEST1 {
        Result 1 {
            Property PassFail = "Pass";
            GoTo TEST2;
        }
    }
    DUTFlowItem TEST2 MOD2::TEST2 {
        Result 1 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            # Module 1
            code = """Version 1.0;
TestPlan MOD1;
Test iCSimpleScoreboardTest TEST1 {
    bypass_global = "0";
    patlist = "list1";
}
"""
            File('%s/Modules/MOD1/a.mtpl' % tdir).touch(code, mkdir=True)

            # Module 2
            code = """Version 1.0;
TestPlan MOD2;
Test iCSimpleScoreboardTest TEST2 {
    bypass_global = "0";
    patlist = "list2";
}
"""
            File('%s/Modules/MOD2/b.mtpl' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            tp.mtpl.read_mtpl_flow()

            # Test line 900: r_mod filter - should only return MOD1 items
            import re
            result = list(tp.mtpl.iter_flows('MAIN', r_mod=re.compile('MOD1')))
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], 'MOD1')

            # Test that only MOD2 is returned when filtering for MOD2
            result = list(tp.mtpl.iter_flows('MAIN', r_mod=re.compile('MOD2')))
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], 'MOD2')

            # Test filtering with non-matching regex
            result = list(tp.mtpl.iter_flows('MAIN', r_mod=re.compile('MOD3')))
            self.assertEqual(len(result), 0)

            # Test line 927: uniq=False - returns duplicates
            # First with uniq=True (default behavior)
            result_uniq = list(tp.mtpl.iter_flows('MAIN', uniq=True))
            # Then with uniq=False
            result_not_uniq = list(tp.mtpl.iter_flows('MAIN', uniq=False))
            # They should be equal in this case since no duplicates, but uniq=False path is exercised
            self.assertEqual(len(result_uniq), 2)
            self.assertEqual(len(result_not_uniq), 2)

    def test_get_flow_instance_coverage_line_1056(self):
        # Test coverage for line 1056: if ':' in target
        with TempDir(name=True) as tdir:
            code = """Version 1.0;
DUTFlow MAIN {
    DUTFlowItem TEST1 IP::MOD1::TEST1 {
        Result 1 {
            Property PassFail = "Pass";
            GoTo TEST2;
        }
    }
    DUTFlowItem TEST2 TEST2 {
        Result 1 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code, mkdir=True)

            code = """Version 1.0;
TestPlan MOD1;
Test iCSimpleScoreboardTest TEST1 {
    bypass_global = "0";
}
Test iCSimpleScoreboardTest TEST2 {
    bypass_global = "0";
}
"""
            File('%s/Modules/MOD1/a.mtpl' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            try:
                TestProgram._unit_test_protocol = 1  # to check for passfail property
                tp = TestProgram(envfile, tpl='')._ut_write_stpl()
                tp.mtpl.read_mtpl_flow()

                # Test get_flow_instance with target containing ':' (line 1056)
                # Case 1: target with ':' - should extract module and testname
                md, tn = tp.mtpl.get_flow_instance('MAIN', 'TEST1')
                self.assertEqual(md, 'MOD1')
                self.assertEqual(tn, 'TEST1')

                # Case 2: target without ':' - should use dutflow module
                md, tn = tp.mtpl.get_flow_instance('MAIN', 'TEST2')
                self.assertEqual(md, 'BASE')  # Module is 'BASE' from MAIN dutflow
                self.assertEqual(tn, 'TEST2')
            finally:
                TestProgram._unit_test_protocol = 0  # reset after test


class BMTest(TestCase):

    def test_expand(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env')
        bf = BM(tpobj)

        # simple string
        self.assertEqual(list(bf.expand('abc')), ['abc'])    # This will call init()
        bf.bvars['BinMatrix__bin'] = '1 2 3'.split()
        bf.bvars['BinMatrix__qq'] = '4 5 6'.split()

        # expanded
        result = list(bf.expand(' SetBin "SoftBins.b" + BinMatrix.bin + "2052_fail_ARR_ATO" '.strip()))
        self.assertEqual(result, ['SetBin SoftBins.b12052_fail_ARR_ATO',
                                  'SetBin SoftBins.b22052_fail_ARR_ATO',
                                  'SetBin SoftBins.b32052_fail_ARR_ATO'])

        result = list(bf.expand('SetBin "SoftBins.b" + BinMatrix.bin + "20" +BinMatrix.qq+ "_fail_ARR_ATO" '.strip()))
        self.assertEqual(result, ['SetBin SoftBins.b1204_fail_ARR_ATO',
                                  'SetBin SoftBins.b2205_fail_ARR_ATO',
                                  'SetBin SoftBins.b3206_fail_ARR_ATO'])

        # not a valid var
        with self.assertRaisesRegex(ErrorInput, 'BinMatrix.binx. is not found in'):
            list(bf.expand('SetBin "SoftBins.b" + BinMatrix.binx'))

        # not a valid line
        with self.assertRaisesRegex(ErrorInput, 'Invalid line'):
            list(bf.expand('A "SoftBins.b" + BinMatrix.binx'))

        # full line case
        line = '  SetBin "SoftBins.b" + BinMatrix.bin + "20" +BinMatrix.qq+ "_fail_ARR_ATO";  '     # space is added to identify single vs double quote
        result = [''] + list(bf.expand(line.strip())) + ['']
        expect = '''
SetBin SoftBins.b1204_fail_ARR_ATO;
SetBin SoftBins.b2205_fail_ARR_ATO;
SetBin SoftBins.b3206_fail_ARR_ATO;
'''
        self.assertTextEqual('\n'.join(result), expect)

        # full line case
        line = '  SetBin "SoftBins.b" + BinMatrix.bin + "20" +BinMatrix.qq+ "_fail_ARR_ATO";  '     # space is added to identify single vs double quote
        result = [''] + list(bf.expand(line.strip())) + ['']
        expect = '''
SetBin SoftBins.b1204_fail_ARR_ATO;
SetBin SoftBins.b2205_fail_ARR_ATO;
SetBin SoftBins.b3206_fail_ARR_ATO;
'''
        self.assertTextEqual('\n'.join(result), expect)

        # end line case1 - with semicolon
        line = '  SetBin "SoftBins.b" + BinMatrix.bin + "20_fail_ARR_ATO" + BinMatrix.qq;  '     # space is added to identify single vs double quote
        result = [''] + list(bf.expand(line.strip())) + ['']
        expect = '''
SetBin SoftBins.b120_fail_ARR_ATO4;
SetBin SoftBins.b220_fail_ARR_ATO5;
SetBin SoftBins.b320_fail_ARR_ATO6;
'''
        self.assertTextEqual('\n'.join(result), expect)

        # end line case2 - without semicolon
        line = '  TrialTest VminTC "SoftBins.b" + BinMatrix.bin + "20_fail_ARR_ATO" + BinMatrix.qq  '     # space is added to identify single vs double quote
        result = [''] + list(bf.expand(line.strip())) + ['']
        expect = '''
TrialTest VminTC SoftBins.b120_fail_ARR_ATO4
TrialTest VminTC SoftBins.b220_fail_ARR_ATO5
TrialTest VminTC SoftBins.b320_fail_ARR_ATO6
'''
        self.assertTextEqual('\n'.join(result), expect)

        # case2 - all vars
        line = '  TrialTest VminTC BinMatrix.bin + BinMatrix.bin + BinMatrix.qq  '     # space is added to identify single vs double quote
        result = [''] + list(bf.expand(line.strip())) + ['']
        expect = '''
TrialTest VminTC 114
TrialTest VminTC 225
TrialTest VminTC 336
'''
        self.assertTextEqual('\n'.join(result), expect)

        # nothing to expand, no plus
        line = '  TrialTest A "VminTC"; '
        self.assertEqual(list(bf.expand(line.strip())), [line.strip()])

        # it's broken up to strings keep comments
        line = '  TrialTest A "VminTC" + "_" + "abc" + "_" + "ghi";# '
        self.assertEqual(list(bf.expand(line.strip())), ['TrialTest A VminTC_abc_ghi;#'])

        # it's broken up to strings no semicolon
        line = '  TrialTest A "VminTC" + "_" + "abc" + "_" + "ghi"  '
        self.assertEqual(list(bf.expand(line.strip())), ['TrialTest A VminTC_abc_ghi'])

        # some exception
        line = '  TrialTest A "VminTC" / "_" + "abc" + "_" + "ghi"  '
        with self.assertRaisesRegex(ErrorInput, 'Error on eval.*\n.*from ut'):
            list(bf.expand(line.strip(), 'from ut'))

    def test_expand_mixed(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env')
        bf = BM(tpobj)

        # simple string
        self.assertEqual(list(bf.expand('abc')), ['abc'])    # This will call init()
        bf.bvars['BinMatrix__bin'] = '1 2 3'.split()
        bf.bvars['BinMatrix__qq'] = '4'

        # expanded
        result = list(bf.expand('SetBin "SoftBins.b" + BinMatrix.bin + "20" +BinMatrix.qq+ "_fail_ARR_ATO" '.strip()))
        self.assertEqual(result, ['SetBin SoftBins.b1204_fail_ARR_ATO',
                                  'SetBin SoftBins.b2204_fail_ARR_ATO',
                                  'SetBin SoftBins.b3204_fail_ARR_ATO'])

    def test_read_binmatrix(self):
        tpobj1 = TestProgram(f'{UT_DIR_REPO}/Simple8/TPL/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            text = '''
UserVars BinMatrix
{
        Array<String> bin1 = BinMatrixRule.BomGroupRule(["1001", "1002", "1003"]);
        Array<String> bin2=BinMatrixRule.BomGroupRule(["1001", "1002", "1003"], ["1501", "1502", "1503", "1504", "1505", "1506"]);
        String CRU_F1_FREQ = BinMatrixRule.BomGroupRule("0.4");
}
'''
            File(f'{tdir}/Shared/S/BinMatrix.flm.usrv').touch(text, mkdir=True)
            tpobj1.tpldir = tdir
            bf = BM(tpobj1).init()
            self.assertEqual(bf.bvars,
                             {'BinMatrix__CRU_F1_FREQ': "0.4",
                              'BinMatrix__bin1': ['1001', '1002', '1003'],
                              'BinMatrix__bin2': ['1001', '1002', '1003', '1501', '1502', '1503', '1504', '1505', '1506']
                              })

            # invalid
            text = '''
UserVars BinMatrix
{
        Array<String> bin1 = BinMatrixRule.BomGroupRule("1001", "1002", "1003"]);
}
'''
            File(f'{tdir}/Shared/S/BinMatrix.flm.usrv').touch(text, newfile=True)
            bf = BM(tpobj1).init()
            self.assertEqual(bf.bvars, {'BinMatrix__bin1': None})

        # no binmatrix found
        bf = BM(tpobj1).init()
        self.assertEqual(bf.bm_file, None)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple8', chdir=True)
    def test_read_binmatrix2(self):
        tpobj1 = TestProgram(f'TPL/EnvironmentFile.env')
        text = '''
UserVars BinMatrix
{
        Array<String> bin1 = BinMatrixRule.BomGroupRule(["1001", "1002", "1003"]);
        Array<String> bin2 = BinMatrixRule.BomGroupRule(["2001", "2002", "2003"]);
}
UserVars CustomManual
{
        Array<String> SAN_F1 = toString(toInteger(toDouble(BinMatrix.bin1)));
        Array<String> SAN_F2 = toString(toInteger(toDouble(BinMatrix.bin2)));
}
'''
        File(f'TPL/Shared/S/BinMatrix.flm.usrv').touch(text, mkdir=True)

        text = '''
UserVars ARR1
{
        Array<String> myarr = toString(toInteger(toDouble(BinMatrix.bin1)));
}
'''
        File(f'TPL/Modules/ARR/array.usrv').touch(text, mkdir=True)
        bf = BM(tpobj1).init()
        pprint(bf.bvars)
        self.assertEqual(bf.bvars,
                         {'ARR__ARR1__myarr': ['1001', '1002', '1003'],
                          'BinMatrix__bin1': ['1001', '1002', '1003'],
                          'BinMatrix__bin2': ['2001', '2002', '2003'],
                          'CustomManual__SAN_F1': ['1001', '1002', '1003'],
                          'CustomManual__SAN_F2': ['2001', '2002', '2003']})

        bf = BM(tpobj1, readmodules=False).init()
        self.assertEqual(bf.bvars,
                         {'BinMatrix__bin1': ['1001', '1002', '1003'],
                          'BinMatrix__bin2': ['2001', '2002', '2003'],
                          'CustomManual__SAN_F1': ['1001', '1002', '1003'],
                          'CustomManual__SAN_F2': ['2001', '2002', '2003']})

        # invalid BinMatrixSpecs.flm.usrv
        text = '''
UserVars BinMatrix2
{
        Array<String> bin1 = toString(non_found);
}
'''
        File('TPL/Shared/S/BinMatrixSpecs.flm.usrv').touch(text, newfile=True)
        bf = BM(tpobj1).init()
        self.assertEqual(bf.bvars['BinMatrix2__bin1'], None)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
