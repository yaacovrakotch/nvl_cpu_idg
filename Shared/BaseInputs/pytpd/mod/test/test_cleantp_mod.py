#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for cleantp_mod
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock
from gadget.files import TempName, TempDir
from gadget.gizmo import MockVar
from mod.cleantp_mod import *
import mod.cleantp_mod as cleantp_mod
from gadget.errors import ErrorInput, ErrorUser
from gadget.gizmo import with_
from tp.testprogram import TestProgram
from pprint import pformat
from main.cleantp import CleanTPArgs
import sys


class TestIntegration(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/derek_unit_test/Simple6cleantp_noclean_all_en', chdir=True)
    def test_integ_default(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env]):
            CleanTPArgs(desc=__doc__).main()
        self.assertGoldEqual('clean_plist/fuse.plist', f'{UT_DIR}/derek_unit_test/check_files/fuse.cleanplist.gold')
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR}/derek_unit_test/check_files/Shops.cleanplist.gold')
        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR}/derek_unit_test/check_files/cleantp_array.mtpl.gold1.noclean')
        self.assertGoldEqual('Shared/BaseInputs/BaseLevels.tcg',
                             f'{UT_DIR}/derek_unit_test/check_files/cleantp_BaseLevels.tcg.gold1')
        self.assertGoldEqual('POR_TP/TGLH81/Reports/Cleantp.json', f'{UT_DIR}/san_unit_test/check_files/Cleantp.json.gold_totalpat_included')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_noclean_all_en_Plist', chdir=True)
    def test_integ_plist_having_comments_default(self):
        # TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp_noclean_all_en/POR_TP/TGLH81/EnvironmentFile.env', allpats=True).pickle_init()
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env]):
            CleanTPArgs(desc=__doc__).main()
        self.assertGoldEqual('clean_plist/fuse.plist', f'{UT_DIR}/san_unit_test/check_files/fuse.cleanplist.gold')
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR}/san_unit_test/check_files/Shops.cleanplist.gold2')
        self.assertGoldEqual('clean_plist/fun.plist', f'{UT_DIR}/san_unit_test/check_files/fun.cleanplist.gold')
        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR}/san_unit_test/check_files/cleantp_array.mtpl.gold1.clean')
        self.assertGoldEqual('Shared/BaseInputs/BaseLevels.tcg',
                             f'{UT_DIR}/derek_unit_test/check_files/cleantp_BaseLevels.tcg.gold1')
        self.assertGoldEqual('POR_TP/TGLH81/Reports/Cleantp.json', f'{UT_DIR}/san_unit_test/check_files/Cleantp.json.gold5_totalpat_included_retain_one_instance_in_composite')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en', chdir=True)
    def test_integ_instance(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env, '-instance']):
            CleanTPArgs(desc=__doc__).main()
        self.assertFalse(os.path.exists("clean_plist/fuse.plist"))
        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_array.mtpl.gold1.noclean')
        self.assertGoldEqual('Shared/BaseInputs/BaseLevels.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_BaseLevels.tcg.orig')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en', chdir=True)
    def test_integ_plist(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env, '-plist']):
            CleanTPArgs(desc=__doc__).main()
        self.assertGoldEqual('clean_plist/fuse.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/fuse.cleanplist.gold')
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/Shops.cleanplist.gold')
        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en/Modules/ARR/array.mtpl')
        self.assertGoldEqual('Shared/BaseInputs/BaseLevels.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_BaseLevels.tcg.orig')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_unloaded_plist', chdir=True)
    def test_integ_unloaded_plist(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env, '-plist']):
            CleanTPArgs(desc=__doc__).main()
        csv = f'POR_TP/TGLH81/Reports/Cleantp_fullreport.csv'
        with open(csv) as file:
            contents = file.read()
        self.assertFalse("fake_plist_not_loaded" in contents)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en', chdir=True)
    def test_integ_tcg(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env, '-tcg']):
            CleanTPArgs(desc=__doc__).main()
        self.assertFalse(os.path.exists("clean_plist/fuse.plist"))
        self.assertGoldEqual('Modules/ARR/array.mtpl',
                             f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en/Modules/ARR/array.mtpl')
        self.assertGoldEqual('Shared/BaseInputs/BaseLevels.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_BaseLevels.tcg.gold1')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en', chdir=True)
    def test_tcg_multiple_scope(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        base_tcg = f'Shared/BaseInputs/BaseLevels.tcg'
        module_tcg = f'Modules/ARR/array.tcg'
        copy_tcg = '''
TestCondition tc2_lvl
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = aaa;
}
'''
        with open(module_tcg, 'a') as f:
            f.write(copy_tcg)
        # with open(module_tcg,'a') as f:
            # f.write(copy_tcg)
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env, '-tcg']):
            CleanTPArgs(desc=__doc__).main()
        self.assertGoldEqual('Shared/BaseInputs/BaseLevels.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_BaseLevels.tcg.copytcg.gold')
        self.assertGoldEqual('Modules/ARR/array.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/array.tcg.copytcg.gold')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_revert', chdir=True)
    def test_revert_tcg(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env, '-revert']):
            CleanTPArgs(desc=__doc__).main()
        self.assertGoldEqual('Modules/ARR/array.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/array.tcg.notcleaned')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_revert_nocsv', chdir=True)
    def test_revert_nocsv(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, 'argv', ['cleantp.py', '-env', env, '-revert']):
            CleanTPArgs(desc=__doc__).main()
        self.assertGoldEqual('Modules/ARR/array.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/array.tcg.notcleaned')


class TestInstanceClean(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_integ_nopt(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        clean.main()
        expect = '''
{'bypassed': 1,
 'connected': 11,
 'everything': 12,
 'floating': 1,
 'no_remove': 0,
 'rewrite_instance_files': 0}
'''
        self.assertTextEqual(pformat(clean.stats), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean', chdir=True)
    def test_integ_opt(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        clean.main()
        expect = '''
{'bypassed': 1,
 'connected': 11,
 'everything': 12,
 'floating': 1,
 'no_remove': 2,
 'rewrite_instance_files': 1}
'''
        self.assertTextEqual(pformat(clean.stats), expect)
        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_array.mtpl.gold1.noclean')

    def test_get_noclean(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        self.assertEqual(clean.get_noclean(),
                         {('ARR', 'CCXfloating'),
                          ('ARR', 'CCA')})

    def test_get_noclean_inst_regex(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_regex/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        self.assertEqual(clean.get_noclean(),
                         {('ARR', 'CCB'),
                          ('ARR', 'CCD')})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/derek_unit_test/Simple6cleantp', chdir=True)
    def test_optin(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        self.assertEqual(CleanTP.init_optin(tpobj),
                         {('ARR')})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp', chdir=True)
    def test_optin_all_modules_testcase(self):
        # NVL test case where all modules optin by default if enabled at TP level
        tpobj = TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp/POR_TP/TGLH81/EnvironmentFile.env')
        # File(f'{UT_DIR}/san_unit_test/Simple6cleantp/Shared/BaseInputs/InputFiles/cleantp_on_default.txt').touch('', newfile=True)
        result = CleanTP.init_optin(tpobj)
        self.assertEqual(len(result), 3)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_env_trigger_missing_evg_dedc_file', chdir=True)
    def test_optin_sort_env(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        self.assertEqual(CleanTP.init_optin(tpobj),
                         {'ARR', 'SCN'})

    def test_get_first_dutflow(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        self.assertEqual(clean.get_first_dutflow(clean.get_everything()),
                         {('ARR', 'CCA'),
                          ('ARR', 'ini1'),
                          ('PTH', 'CCA_1100_blah_1501'),
                          ('PTH', 'ini1'),
                          ('SCN', 'CCA'),
                          ('SCN', 'init1')})

    def test_get_empty_dutflow(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)

        # everything is removed
        self.assertEqual(clean.get_empty_dutflow(clean.get_everything()),
                         {('ARR', 'CCA'),
                          ('ARR', 'ini1'),
                          ('PTH', 'CCA_1100_blah_1501'),
                          ('PTH', 'ini1'),
                          ('SCN', 'CCA'),
                          ('SCN', 'init1')})

        # no empty
        self.assertEqual(clean.get_empty_dutflow(set()), set())

    def test_pgmrules(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        res = clean.get_pgmrules(set())
        self.assertEqual(len(res), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_env_trigger_missing_evg_dedc_file', chdir=True)
    def test_dedc_evg_xml_missing_ut(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        res = clean.get_dedc_evg(set())
        self.assertEqual(len(res), 0)

    def test_dedc_evg(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6cleantp/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)

        dd = {'config_file': f'{UT_DIR_REPO}/misc_files/cleantp_dedc1.xml'}
        with MockVar(tpobj.mtpl, 'iter_flows', Mock(return_value=[(None, None, dd)])):
            res = clean.get_dedc_evg(set())
        self.assertEqual(len(res), 12)

        dd = {'config_file': f'{UT_DIR_REPO}/misc_files/cleantp_dedc2.xml'}
        with MockVar(tpobj.mtpl, 'iter_flows', Mock(return_value=[(None, None, dd)])):
            res = clean.get_dedc_evg(set())
        self.assertEqual(len(res), 1)

    def test_dedc_prime(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6cleantp/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)

        dd1 = {'ConfigFile': f'{UT_DIR_REPO}/misc_files/cleantp_dedc3.xml'}
        dd2 = {'ConfigFile': ''}
        with MockVar(tpobj.mtpl, 'iter_flows', Mock(return_value=[(None, None, dd1),
                                                                  (None, None, dd2)])):
            res = clean.get_dedc_prime(set())
        self.assertEqual(len(res), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_primededc', chdir=True)
    def test_dedc_prime_tos4(self):
        # Test case to remove test template starting with 'CSharpTest' on TOS4 TP
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        res = clean.get_dedc_prime(set())
        self.assertEqual(len(res), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_RunCallBack_ExecutePatConfigSetPoint_PrimePauseTM', chdir=True)
    def test_get_runcallback_With_TOSRule(self):
        # Test case to remove test template starting with 'CSharpTest' on TOS4 TP
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        not_to_remove = clean.get_runcallback({('ARR', 'TOSRule_empty_classback'), ('ARR', 'Test_ExecutePatConfigSetPoint')})
        self.assertEqual(len(not_to_remove), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_runcallback_excluded_from_cleanup', chdir=True)
    def test_get_runcallback(self):
        # Test case to remove test template starting with 'CSharpTest' on TOS4 TP
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        not_to_remove = clean.get_runcallback({('ARR', 'ABCD_1'), ('ARR', 'EFGH'), ('ARR', 'ABCD_2'), ('ARR', 'PQRS'), ('ARR', 'MNOP'), ('ARR', 'YYY')})
        self.assertEqual(len(not_to_remove), 6)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_PrimePatmodConfig_config_json_path_not_resolvable', chdir=True)
    def test_get_prime_pinprofilerTM(self):
        # Test case to remove test template starting with 'CSharpTest' on TOS4 TP
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        not_to_remove = clean.get_prime_pinprofilerTM()
        self.assertEqual(len(not_to_remove), 1)

    @with_(TempDir, chdir=True)
    def test_hardcoded_bypass(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6cleantp/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        res = clean.get_hardcoded_bypassed()

        self.assertEqual(res, {('ARR', 'CCB')})

    def test_module_skip(self):
        # remove a cyclic instance
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        clean = CleanInstance(tpobj)
        self.assertEqual(clean.remove_instances('a.mtpl', 'CLK_XXX', set(), set()), 1)

    @with_(TempDir, chdir=True)
    def test_remove_cyclic(self):
        # remove a cyclic instance
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        clean = CleanInstance(tpobj)
        fname = 'a.mtpl'
        File(fname).touch('''
Version1;

Test vmin ABC {
}
Test vmin GHI {
}
Test vmin DEF {
}
DUTFlow Y {
   DUTFlowItem ABC1 ABC {
       Result 1 {
          GoTo GHI1;
       }
   }
   DUTFlowItem GHI1 GHI {
       Result 1 {
          GoTo ABC1;
       }
   }
   DUTFlowItem DEF1 DEF {
       Result 1 {
          Return 1;
       }
   }
}
''')
        with self.assertRaisesRegex(ErrorCockpit, 'Maximum loops for'):
            clean.remove_instances(fname, 'A', {('A', 'ABC'), ('A', 'GHI')}, set())

    @with_(TempDir, chdir=True)
    def test_remove_first_last(self):
        # remove first and last
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        clean = CleanInstance(tpobj)
        fname = 'a.mtpl'
        File(fname).touch('''
Version1;

Test vmin ABC {
   param1 = 1;
}
Test vmin GHI {
   param1 = 2;
}
MultiTrialTest DEF {
   line1;
   Test bmin GHI {
      param2 = 2;
    } #1
} #2
DUTFlow A {
   DUTFlowItem ABC1 ABC {
       Result 1 {
          GoTo GHI1;
       }
   }
   DUTFlowItem GHI1 GHI {
       Result 1 {
          GoTo DEF1;   # some comment
       }
   }
   DUTFlowItem DEF1 DEF {
       Result 1 {
          Return 1;
       }
   }
}
''')
        clean.remove_instances(fname, 'A', {('A', 'ABC'), ('A', 'DEF'), ('B', 'GHI')}, set())
        expect = '''
Version1;

Test vmin GHI
{
    param1 = 2;
}
DUTFlow A
{
    DUTFlowItem GHI1 GHI
    {
        Result 1
        {
            Return 1;    # some comment
        }
    }
}
'''
        self.assertTextEqual(File(fname).read().replace('\t', '    '), expect)

    @with_(TempDir, chdir=True)
    def test_remove_consecutive(self):
        # remove two consecutive: 2nd and last
        # Same line replacement
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        clean = CleanInstance(tpobj)
        fname = 'a.mtpl'
        File(fname).touch('''
Version1;

Test vmin GHI {
   param1 = 2;
}
DUTFlow A {
   DUTFlowItem ABC1 GHI {
       Result 1 { GoTo GHI1; }
   }
   DUTFlowItem GHI1 ABC {
       Result 1 {
          GoTo DEF1;
       }
   }
   DUTFlowItem DEF1 ABC {
       Result 1 {
          Return 1;
       }
   }
}
''')
        clean.remove_instances(fname, 'A', {('A', 'ABC'), ('A', 'DEF'), ('B', 'GHI')}, set())
        expect = '''
Version1;

Test vmin GHI
{
    param1 = 2;
}
DUTFlow A
{
    DUTFlowItem ABC1 GHI
    {
        Result 1
        {
            Return 1;
        }
    }
}
'''
        self.assertTextEqual(File(fname).read().replace('\t', '    '), expect)

    @with_(TempDir, chdir=True)
    def test_remove_middle(self):
        # remove two consecutive: 2nd and last
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        clean = CleanInstance(tpobj)
        fname = 'a.mtpl'
        File(fname).touch('''
Version1;

Test vmin GHI {
   param1 = 2;
}
DUTFlow A {
   DUTFlowItem ABC1 GHI {
       Result 1 {
          GoTo ABC2;
       }
   }
   DUTFlowItem ABC2 ABC {
       Result 1 {
          GoTo ABC3;
       }
   }
   DUTFlowItem ABC3 ABC {
       Result 1 {
          GoTo ABC4;
       }
   }
   DUTFlowItem ABC4 GHI {
       Result 1 {
          Return 1;
       }
   }
}
''')
        clean.remove_instances(fname, 'A', {('A', 'ABC'), ('A', 'DEF'), ('B', 'GHI')}, set())

        expect = '''
Version1;

Test vmin GHI
{
    param1 = 2;
}
DUTFlow A
{
    DUTFlowItem ABC1 GHI
    {
        Result 1
        {
            GoTo ABC4;
        }
    }
    DUTFlowItem ABC4 GHI
    {
        Result 1
        {
            Return 1;
        }
    }
}
'''
        self.assertTextEqual(File(fname).read().replace('\t', '    '), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4', chdir=True)
    def test_tos4_module_skip(self):
        # Test case to remove test template starting with 'CSharpTest' on TOS4 TP
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        clean.remove_instances(tpobj.mtpl.get_mod2fname()['ARR'], 'ARR', {('ARR', 'CCD')}, {('ARR', 'CCB')})
        self.assertGoldEqual(tpobj.mtpl.get_mod2fname()['ARR'], f'{UT_DIR}/san_unit_test/check_files/array.cleanmtpl_clear_newline.gold')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_floating_test_PrimeHptpTIming_patmod_call', chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests(self):
        # Test explicit instance call: PerPartitionExecution.InstanceNameToExecute
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        result = clean.get_floatingInstance_invoked_by_activeTests({('ARR', 'FLOATING')})
        self.assertEqual(len(result), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/san_unit_test/Simple6_tos4_undiscoverable_jsonpath', chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests_with_jsonrun(self):
        # Test JsonRun handling: retains referenced tests, filters by removable parameter
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        clean = CleanInstance(tpobj)
        result = clean.get_floatingInstance_invoked_by_activeTests({('ARR', 'CCD')})
        self.assertEqual(len(result), 0)

    @staticmethod
    def _make_vmintc_tpobj(post_instance, is_tos4=True, mod2fname=None):
        # Build a lightweight tpobj stub for VminTC PostInstance JsonRun tests.
        if mod2fname is None:
            mod2fname = {'ARR': os.path.abspath('Modules/ARR/array.mtpl')}

        class _MtplStub:
            def iter_tests(self, template_name=None, edict=False):
                if template_name == 'PerPartitionExecution':
                    return []
                if template_name == 'VminTC':
                    return [('ARR', 'ACTIVE_VMIN', {'PostInstance': post_instance}, None)]
                return []

            def get_mod2fname(self):
                return mod2fname

        class _TpObjStub:
            def __init__(self):
                self.is_tos4 = is_tos4
                self.mtpl = _MtplStub()

        return _TpObjStub()

    @staticmethod
    def _make_xpath_mapper(path_map):
        # Normalize slash style so tests can pass regardless of Windows/Unix separators.
        normalized = {str(k).replace('\\', '/'): v for k, v in path_map.items()}

        def _mapper(path):
            key = str(path).replace('\\', '/')
            return normalized.get(key, path)

        return _mapper

    @with_(TempDir, chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests_with_jsonrun_tos4_modules_path(self):
        # Test TOS4 unresolved JsonRun path that must be rewritten from ./Modules to /Modules
        mapped_json = os.path.abspath('mapped_refs.json')
        File(mapped_json).touch('{\n  "Targets": ["ARR::FLOATING_JSON"]\n}\n', newfile=True)

        tpobj = self._make_vmintc_tpobj('JsonRun(./Modules/ARR/InputFiles/floating_refs.json)')
        mock_xpath = self._make_xpath_mapper({
            './Modules/ARR/InputFiles/floating_refs.json': '__unresolved__',
            '/Modules/ARR/InputFiles/floating_refs.json': mapped_json,
        })

        def mock_exists(path):
            return path == mapped_json

        clean = CleanInstance(tpobj)
        with MockVar(cleantp_mod.Env, 'xpath', mock_xpath), \
                MockVar(cleantp_mod, 'exists', mock_exists):
            result = clean.get_floatingInstance_invoked_by_activeTests({('ARR', 'FLOATING_JSON')})

        self.assertEqual(result, {('ARR', 'FLOATING_JSON')})

    @with_(TempDir, chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests_skips_missing_json_file(self):
        # Test missing JsonRun file path after TOS4 path rewriting
        missing_json = os.path.abspath('missing_refs.json')

        tpobj = self._make_vmintc_tpobj('JsonRun(./Modules/ARR/InputFiles/missing_refs.json)')
        mock_xpath = self._make_xpath_mapper({
            './Modules/ARR/InputFiles/missing_refs.json': '__unresolved__',
            '/Modules/ARR/InputFiles/missing_refs.json': missing_json,
        })

        clean = CleanInstance(tpobj)
        with MockVar(cleantp_mod.Env, 'xpath', mock_xpath), \
                MockVar(cleantp_mod, 'exists', lambda path: False):
            result = clean.get_floatingInstance_invoked_by_activeTests({('ARR', 'FLOATING_JSON')})

        self.assertEqual(result, set())

    @with_(TempDir, chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests_with_multiple_jsonrun_files(self):
        # Cover cache read-loop back-edge by resolving two distinct JsonRun files.
        mapped_json_a = os.path.abspath('mapped_refs_a.json')
        mapped_json_b = os.path.abspath('mapped_refs_b.json')
        File(mapped_json_a).touch('{\n  "Targets": ["ARR::FLOATING_JSON_A"]\n}\n', newfile=True)
        File(mapped_json_b).touch('{\n  "Targets": ["ARR::FLOATING_JSON_B"]\n}\n', newfile=True)

        class _MtplStub:
            def iter_tests(self, template_name=None, edict=False):
                if template_name == 'PerPartitionExecution':
                    return []
                if template_name == 'VminTC':
                    return [
                        ('ARR', 'ACTIVE_VMIN_A', {'PostInstance': 'JsonRun(./Modules/ARR/InputFiles/floating_refs_a.json)'}, None),
                        ('ARR', 'ACTIVE_VMIN_B', {'PostInstance': 'JsonRun(./Modules/ARR/InputFiles/floating_refs_b.json)'}, None),
                    ]
                return []

            def get_mod2fname(self):
                return {'ARR': os.path.abspath('Modules/ARR/array.mtpl')}

        class _TpObjStub:
            def __init__(self):
                self.is_tos4 = True
                self.mtpl = _MtplStub()

        mock_xpath = self._make_xpath_mapper({
            './Modules/ARR/InputFiles/floating_refs_a.json': '__unresolved_a__',
            './Modules/ARR/InputFiles/floating_refs_b.json': '__unresolved_b__',
            '/Modules/ARR/InputFiles/floating_refs_a.json': mapped_json_a,
            '/Modules/ARR/InputFiles/floating_refs_b.json': mapped_json_b,
        })

        clean = CleanInstance(_TpObjStub())
        with MockVar(cleantp_mod.Env, 'xpath', mock_xpath), \
                MockVar(cleantp_mod, 'exists', lambda path: path in {mapped_json_a, mapped_json_b}):
            result = clean.get_floatingInstance_invoked_by_activeTests({
                ('ARR', 'FLOATING_JSON_A'),
                ('ARR', 'FLOATING_JSON_B'),
            })

        self.assertEqual(result, {
            ('ARR', 'FLOATING_JSON_A'),
            ('ARR', 'FLOATING_JSON_B'),
        })

    @with_(TempDir, chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests_skips_malformed_extracted_test(self):
        # Force one malformed extracted entry so len(elems) >= 2 is False, then continue loop.
        mapped_json = os.path.abspath('mapped_refs.json')
        File(mapped_json).touch('{\n  "Targets": ["ARR::FLOATING_JSON"]\n}\n', newfile=True)

        tpobj = self._make_vmintc_tpobj('JsonRun(./Modules/ARR/InputFiles/floating_refs.json)')
        mock_xpath = self._make_xpath_mapper({
            './Modules/ARR/InputFiles/floating_refs.json': '__unresolved__',
            '/Modules/ARR/InputFiles/floating_refs.json': mapped_json,
        })

        def mock_findall(_pattern, _content):
            # First token is malformed (no scope separator), second is valid.
            return ['MALFORMED_TOKEN', 'ARR::FLOATING_JSON']

        clean = CleanInstance(tpobj)
        with MockVar(cleantp_mod.Env, 'xpath', mock_xpath), \
                MockVar(cleantp_mod, 'exists', lambda path: path == mapped_json), \
                MockVar(cleantp_mod, 'confirm', lambda *_args, **_kwargs: None), \
                MockVar(cleantp_mod.re, 'findall', mock_findall):
            result = clean.get_floatingInstance_invoked_by_activeTests({('ARR', 'FLOATING_JSON')})

        self.assertEqual(result, {('ARR', 'FLOATING_JSON')})

    @with_(TempDir, chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests_ignores_missing_key(self):
        # Test guard logic: missing PostInstance key is safely skipped without KeyError
        json_path = os.path.abspath('refs.json')
        File(json_path).touch('{\n  "Tests": ["ARR::SOME_TEST"]\n}\n', newfile=True)

        class _MtplStub:
            def __init__(self):
                pass

            def iter_tests(self, template_name=None, edict=False):
                # VminTC without PostInstance key in dd
                return [('ARR', 'ACTIVE', {}, None)]

            def get_mod2fname(self):
                return {'ARR': os.path.abspath('Modules/ARR/array.mtpl')}

        class _TpObjStub:
            def __init__(self):
                self.is_tos4 = False
                self.mtpl = _MtplStub()

        clean = CleanInstance(_TpObjStub())
        # Should not raise KeyError, should return empty set
        result = clean.get_floatingInstance_invoked_by_activeTests({('ARR', 'SOME_TEST')})
        self.assertEqual(result, set())

    @with_(TempDir, chdir=True)
    def test_get_floatingInstance_invoked_by_activeTests_with_relative_inputfiles_path(self):
        # Test TOS4 JsonRun path with relative InputFiles path (lines 573-575: case B)
        # This tests the elif param != '' branch where ConfigFile = "InputFiles/...json"
        input_json = os.path.abspath('InputFiles/relative_refs.json')
        os.makedirs(os.path.dirname(input_json), exist_ok=True)
        File(input_json).touch('{\n  "Targets": ["ARR::RELATIVE_TEST"]\n}\n', newfile=True)

        tpobj = self._make_vmintc_tpobj('JsonRun(InputFiles/relative_refs.json)')
        # Simulate path resolution for relative InputFiles path.
        mock_xpath = self._make_xpath_mapper({
            'InputFiles/relative_refs.json': input_json,
            '/InputFiles/relative_refs.json': input_json,
        })

        def mock_exists(path):
            return path == input_json

        clean = CleanInstance(tpobj)
        with MockVar(cleantp_mod.Env, 'xpath', mock_xpath), \
                MockVar(cleantp_mod, 'exists', mock_exists):
            result = clean.get_floatingInstance_invoked_by_activeTests({('ARR', 'RELATIVE_TEST')})

        # Should find the target from relative InputFiles path
        self.assertEqual(result, {('ARR', 'RELATIVE_TEST')})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_do_instances_with_owner_file(self):
        # Test CleanInstance.do_instances() with owner.txt file containing owner info
        # This covers the missing lines 270-273 where owner file is successfully read
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)

        # Create cleantp_on_default.txt to make all modules optin
        trigger_file = f'{tpobj.tpldir}/Shared/BaseInputs/InputFiles/cleantp_on_default.txt'
        os.makedirs(os.path.dirname(trigger_file), exist_ok=True)
        File(trigger_file).touch('', newfile=True)

        # Create owner.txt file in ARR module directory
        arr_dir = os.path.dirname(tpobj.mtpl.get_mod2fname()['ARR'])
        owner_file = f'{arr_dir}/owner.txt'
        File(owner_file).touch('owner: TestModuleOwner\nemail: test@example.com\n', newfile=True)

        clean = CleanInstance(tpobj)
        clean.main()

        # Verify the CSV report was created (which means owner was processed)
        csv_file = f'{os.path.dirname(tpobj.get_stpl())}/Reports/Cleantp_fullreport.csv'
        self.assertTrue(os.path.exists(csv_file))

        # Verify that the owner was included in the report
        csv_content = File(csv_file).read()
        self.assertIn('TestModuleOwner', csv_content)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_do_instances_with_empty_owner_file(self):
        # Test CleanInstance.do_instances() with empty owner.txt file
        # This covers lines 270-276 where file is opened but loop finds no owner: line
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)

        # Create cleantp_on_default.txt to make all modules optin
        trigger_file = f'{tpobj.tpldir}/Shared/BaseInputs/InputFiles/cleantp_on_default.txt'
        os.makedirs(os.path.dirname(trigger_file), exist_ok=True)
        File(trigger_file).touch('', newfile=True)

        # Create empty owner.txt file in ARR module directory
        arr_dir = os.path.dirname(tpobj.mtpl.get_mod2fname()['ARR'])
        owner_file = f'{arr_dir}/owner.txt'
        File(owner_file).touch('', newfile=True)

        clean = CleanInstance(tpobj)
        clean.main()

        # Verify that the CSV report was created
        csv_file = f'{os.path.dirname(tpobj.get_stpl())}/Reports/Cleantp_fullreport.csv'
        self.assertTrue(os.path.exists(csv_file))

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_do_instances_with_invalid_owner_file(self):
        # Test CleanInstance.do_instances() with owner.txt file lacking owner: keyword
        # This covers lines 271-276 where file has content but no matching owner: line
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)

        # Create cleantp_on_default.txt
        trigger_file = f'{tpobj.tpldir}/Shared/BaseInputs/InputFiles/cleantp_on_default.txt'
        os.makedirs(os.path.dirname(trigger_file), exist_ok=True)
        File(trigger_file).touch('', newfile=True)

        # Create owner.txt with content but no 'owner:' line
        arr_dir = os.path.dirname(tpobj.mtpl.get_mod2fname()['ARR'])
        owner_file = f'{arr_dir}/owner.txt'
        File(owner_file).touch('# Some comments\nemail: test@example.com\nteam: TestTeam\n', newfile=True)

        clean = CleanInstance(tpobj)
        clean.main()

        # Verify the CSV report was created
        csv_file = f'{os.path.dirname(tpobj.get_stpl())}/Reports/Cleantp_fullreport.csv'
        self.assertTrue(os.path.exists(csv_file))

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_do_instances_missing_module_mapping_skips_module(self):
        # Test missing module mapping is skipped without raising, and no instances are removed for that module.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanInstance(tpobj)
        clean.optin = {'ARR'}

        remove_instances_mock = Mock()
        with MockVar(clean, 'remove_instances', remove_instances_mock), \
                MockVar(clean, 'get_everything', Mock(return_value={('ARR', 'CCA')})), \
                MockVar(clean, 'get_connected', Mock(return_value=set())), \
                MockVar(clean, 'get_hardcoded_bypassed', Mock(return_value=set())), \
                MockVar(clean, 'get_dedc_evg', Mock(return_value=set())), \
                MockVar(clean, 'get_dedc_prime', Mock(return_value=set())), \
                MockVar(clean, 'get_pgmrules', Mock(return_value=set())), \
                MockVar(clean, 'get_noclean', Mock(return_value=set())), \
                MockVar(clean, 'get_first_dutflow', Mock(return_value=set())), \
                MockVar(clean, 'get_runcallback', Mock(return_value=set())), \
                MockVar(clean, 'get_prime_pinprofilerTM', Mock(return_value=set())), \
                MockVar(clean, 'get_floatingInstance_invoked_by_activeTests', Mock(return_value=set())), \
                MockVar(clean, 'get_empty_dutflow', Mock(return_value=set())), \
                MockVar(tpobj.mtpl, 'get_mod2fname', Mock(return_value={})):
            clean.do_instances()

        self.assertFalse(remove_instances_mock.called)


class TestPlistClean(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_noclean_all_en_Plist', chdir=True)
    def test_plb_map(self):
        # Integration test for CleanPlist | ARR=OPT, PTH=NOPT, SCN=NOPT --> Shops.plist should be cleaned, fuse.plist should not
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.main()
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR}/san_unit_test/check_files/Shops.cleanplist.gold2')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en', chdir=True)
    def test_all_en_plist(self):
        # Integration test for CleanPlist | ARR=OPT, PTH=NOPT, SCN=NOPT --> Shops.plist should be cleaned, fuse.plist should not
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.main()
        self.assertGoldEqual('clean_plist/fuse.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/fuse.cleanplist.gold')
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/Shops.cleanplist.gold')
        self.assertGoldEqual('POR_TP/TGLH81/EnvironmentFile.env', f'{UT_DIR_REPO}/derek_unit_test/check_files/env.cleanplist_array.gold')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_arr_pth_en', chdir=True)
    def test_mixed_opt(self):
        # Integration test for CleanPlist | ARR=OPT, PTH=OPT, SCN=NOPT --> Same result as above since PTH & SCN share fuse.plist
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.main()
        self.assertGoldEqual('plists/fuse.plist', f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_arr_pth_en/plists/fuse.plist')
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/Shops.cleanplist.gold')
        self.assertGoldEqual('POR_TP/TGLH81/EnvironmentFile.env', f'{UT_DIR_REPO}/derek_unit_test/check_files/env.cleanplist_array.gold')

    @with_(MockVar, cleantp_mod, "IS_UT", False)
    @with_(TempDir, chdir=True)
    def test_path_to_plist_as_comment_check(self):
        # Adding original plist location (taken from env file) as comment in the second line of cleantp plist file
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)
        text = '''
GlobalPList main1 {
    GlobalPList main2 {
        GlobalPList main3 {
            Pat a;
        }
    }
}
'''

        File('a.plist').touch(text, newfile=True)
        expect = '''
# copy from: a.plist
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main3
  {
   Pat a;
  }
 }
}
'''
        with MockVar(cleantp_mod, "IS_UT", False):
            cplist.process_plist('a.plist', {'main2'}, {})
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

        # if original plist location is already there as comment then ignore adding comment again test case
        text = '''
# copy from: a.plist
GlobalPList main1 {
    GlobalPList main2 {
        GlobalPList main3 {
            Pat a;
        }
    }
}
'''

        File('a.plist').touch(text, newfile=True)
        expect = '''
# copy from: a.plist
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main3
  {
   Pat a;
  }
 }
}
'''
        with MockVar(cleantp_mod, "IS_UT", False):
            cplist.process_plist('a.plist', {'main2'}, {})
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_plist', chdir=True)
    def test_noclean_instance_n_plist(self):
        """
        # Example code inside: derek_unit_test/Simple6cleantp_noclean_plist/Modules/ARR/array.mtpl:

        Test iCSimpleScoreboardTest CCA {
           # NOCLEAN
           TimingsTc = "tc1_tim";
        }
        Test  iCFuncTest ini1
        {
           # patlist = "shops_M_list"; # PATLIST_NOCLEAN: bc I don't want to >:(
           user_mode = "DEFAULT_MODE";
        }
        """
        # Integration test for # NOCLEAN tag and # PATLIST_NOCLEAN tag together

        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        clean = CleanInstance(tpobj)
        clean.main()
        cplist = CleanPlist(tpobj)
        cplist.main()
        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_array.mtpl.nocleantags.gold')
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/Shops.cleanplist.gold2')
        self.assertGoldEqual('POR_TP/TGLH81/EnvironmentFile.env', f'{UT_DIR_REPO}/derek_unit_test/check_files/env.cleanplist_array.gold')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_plist', chdir=True)
    def test_noclean_plist(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.main()
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/Shops.cleanplist_noclean.gold')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean', chdir=True)
    def test_non_opt_plist_files(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.optin = CleanTP.init_optin(tpobj)
        self.assertEqual(cplist.non_opt_plist_files(), {'fuse.plist'})

        # case A:
        File('Supersedes/patterns/FUse.plist').touch('''
GlobalPList fff {
   Pat f;
}
GlobalPList ggg {
   PList fff;
   Pat c;
}
GlobalPList hhh {
   Pat c;
}
''', mkdir=True)
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.optin = CleanTP.init_optin(tpobj)
        self.assertEqual(cplist.non_opt_plist_files(), {'fuse.plist'})

    def test_get_plist_noclean(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_plist/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        cplist = CleanPlist(tpobj)
        self.assertEqual(cplist.get_plist_noclean(), {'shops_M_list'})

    def test_get_plist_regex_noclean(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_regex/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        clean = CleanPlist(tpobj)
        self.assertEqual(clean.get_plist_noclean(), {'shops_L_list', 'shops_H_list', 'shops_M_list'})

    def test_get_plist_noclean_with_all_quote_types(self):
        # Test get_plist_noclean with double quotes, single quotes, and no quotes
        # This ensures full coverage of lines 1263-1265 (match extraction branches)
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        cplist = CleanPlist(tpobj)

        # Mock read_comments to return comments with PATLIST_NOCLEAN in different formats
        def mock_read_comments(file):
            comments = {
                'test1': ['# patlist = "my_double_quoted_plist"; # PATLIST_NOCLEAN: reason1'],
                'test2': ["# patlist = 'my_single_quoted_plist'; # PATLIST_NOCLEAN: reason2"],
                'test3': ['# patlist = my_unquoted_plist; # PATLIST_NOCLEAN: reason3'],
            }
            return (comments,)

        # Mock get_plb_map to return some plbs
        def mock_get_plb_map():
            return {'my_double_quoted_plist': 'file1.plist',
                    'my_single_quoted_plist': 'file2.plist',
                    'my_unquoted_plist': 'file3.plist'}

        with MockVar(tpobj.mtpl, 'read_comments', mock_read_comments):
            with MockVar(tpobj.plists, 'get_plb_map', mock_get_plb_map):
                result = cplist.get_plist_noclean()
                self.assertEqual(result, {'my_double_quoted_plist', 'my_single_quoted_plist', 'my_unquoted_plist'})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_get_plist_noclean_empty_match_group(self):
        # Test get_plist_noclean where match exists but all groups are None/empty
        # This covers lines 1263-1265 where plb_name = None
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        cplist = CleanPlist(tpobj)

        # Mock read_comments to return a malformed patlist declaration that matches the tag but has empty value
        def mock_read_comments(file):
            comments = {
                'test1': ['# patlist = ""; # PATLIST_NOCLEAN: testing empty match'],
            }
            return (comments,)

        def mock_get_plb_map():
            return {'valid_plist': 'file1.plist'}

        with MockVar(tpobj.mtpl, 'read_comments', mock_read_comments):
            with MockVar(tpobj.plists, 'get_plb_map', mock_get_plb_map):
                result = cplist.get_plist_noclean()
                # Should return empty set since plb_name is empty string
                self.assertEqual(result, set())

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_get_plist_noclean_plb_not_in_map(self):
        # Test get_plist_noclean where plb_name exists but is not in plb_map
        # This covers the case where plb_name is valid but not in all_plb
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        cplist = CleanPlist(tpobj)

        def mock_read_comments(file):
            comments = {
                'test1': ['# patlist = "nonexistent_plist"; # PATLIST_NOCLEAN: testing'],
            }
            return (comments,)

        def mock_get_plb_map():
            return {'other_plist': 'file1.plist'}

        with MockVar(tpobj.mtpl, 'read_comments', mock_read_comments):
            with MockVar(tpobj.plists, 'get_plb_map', mock_get_plb_map):
                result = cplist.get_plist_noclean()
                # Should return empty set since nonexistent_plist is not in plb_map
                self.assertEqual(result, set())

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_get_plist_noclean_match_then_regex_path(self):
        # Cover arc where PATLIST_NOCLEAN match succeeds, then REGEX_PATLIST_NOCLEAN is also parsed.
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        cplist = CleanPlist(tpobj)

        def mock_read_comments(file):
            comments = {
                'test1': ['# patlist = "shops_M_list"; # PATLIST_NOCLEAN: keep # REGEX_PATLIST_NOCLEAN: shops_.*_list'],
            }
            return (comments,)

        def mock_get_plb_map():
            return {
                'shops_L_list': 'l.plist',
                'shops_M_list': 'm.plist',
                'shops_H_list': 'h.plist',
            }

        with MockVar(tpobj.mtpl, 'read_comments', mock_read_comments):
            with MockVar(tpobj.plists, 'get_plb_map', mock_get_plb_map):
                result = cplist.get_plist_noclean()
                self.assertEqual(result, {'shops_L_list', 'shops_M_list', 'shops_H_list'})

    def test_get_instance_regex(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env', allpats=True).pickle_init()
        cplist = CleanPlist(tpobj)
        data = [(None, None, {'SetPointsRegEx': 'g.*'}, None),
                (None, None, {'SetPointsRegEx': 't.*'}, None),
                ('ARR', 'ABCD', {'SetPointsRegEx': 'g.*'}, None)]
        with MockVar(tpobj.mtpl, 'iter_tests', Mock(return_value=data)):
            keeppats = cplist.get_instance_regex({'g2294511W1466650I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL', 'g2026529W2371469I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m0', 'g2026525W2371465I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_nom', 'g2026531W2371471I_Nt_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m0', 'tgl_pst_W9999993H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0', 'g2026530W2371470I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m1', 'g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1', 'g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom', 'g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH'})
            self.assertEqual(len(keeppats), 9)     # out of 47 total patterns, 9 are actual keep patterns among all the patterns called by mtpl
            result = cplist.keep2dict(keeppats, {'cpu_fuse_write_special_x': 'g2026550W2603626I_g4_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Prog'}, set())
            self.assertEqual(len(result), 26)     # plists

    def test_pat_mregex(self):
        # True unittest
        patlist = ['g0495533C5427906D_FJ_B0FPP25_longreset_cpu_lr_infra_MCfun',
                   'g0014509I4063142B_WD_B0RPPay_longreset_ioe_tapunlock',
                   'g0454998C9219922D_OV_B0F0500_DTSTEMPCFG_MCfun',
                   'g0454997C9219923D_OV_B0F0500_clk_cpu_lnc4_fc_airef',
                   'g0454996C9219922D_OV_B0F0500_clk_cpu_lnc4_fc_axref']

        # case 1 - full regex
        to_match = ['[gd].*',     # full regex
                    'XX.*219922D',  # partial
                    'XX.*(4063142|9219922D).*',
                    'XX.*_clk_cpu_lnc4_fc_(?!.*iref).*',
                    ]
        self.assertEqual(CleanPlist.pat_mregex(to_match, set(patlist)), set(patlist))

        # case 2 - partial regex
        to_match = ['XX[gd].*',     # full regex
                    '.*219922D',    # partial
                    'XX.*(4063142|9219922D).*',
                    'XX.*_clk_cpu_lnc4_fc_(?!.*iref).*',
                    ]
        self.assertEqual(CleanPlist.pat_mregex(to_match, set(patlist)),
                         {patlist[2], patlist[4]})

        # case 3 - with parenthesis
        to_match = ['XX[gd].*',     # full regex
                    'XX.*219922D',    # partial
                    '.*(4063142|9219923D).*',
                    'XX.*_clk_cpu_lnc4_fc_(?!.*iref).*',
                    ]
        self.assertEqual(CleanPlist.pat_mregex(to_match, set(patlist)),
                         {patlist[1], patlist[3]})

        # case 4 - negative regex
        to_match = ['XX[gd].*',     # full regex
                    'XX.*219922D',    # partial
                    'XX.*(4063142|9219923D).*',
                    '.*_clk_cpu_lnc4_fc_(?!.*iref).*',
                    ]
        self.assertEqual(CleanPlist.pat_mregex(to_match, set(patlist)),
                         {patlist[4]})

        # case 5 - mixed exact match, no parenthesis
        to_match = ['^g0454997.*$',
                    f'^{patlist[2]}$',
                    patlist[4]]
        self.assertEqual(CleanPlist.pat_mregex(to_match, set(patlist)),
                         {patlist[2], patlist[3], patlist[4]})

        # case 6 - no match
        to_match = ['0495533.*',
                    '0014509',
                    '.*',   # special - this is ignored
                    'g.*re$']
        self.assertEqual(CleanPlist.pat_mregex(to_match, set(patlist)), set())

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_keep2dict(self):
        tpobj = TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp_noclean_all_en', allpats=True).pickle_init()
        pats = {'g2294347W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_FUN', 'g2294511W1466650I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL', 'g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH'}
        cplist = CleanPlist(tpobj)
        result = cplist.keep2dict(pats, {'cpu_fuse_write_special_x': 'g2294347W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_FUN'}, {'fun.plist'})
        self.assertEqual(len(result), len({'shop_L_list': {'g2294511W1466650I_MD_VTRg2026550W2603626I_g4_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Prog024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL'},
                                           'shop_H_list': {'g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH'},
                                           'cpu_fuse_write_special_x': {'g2026550W2603626I_g4_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Prog'}}))

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_all_en', chdir=True)
    def test_dependent(self):
        File('Supersedes/patterns/fuse.plist').touch('''
GlobalPList fff {
   Pat f;
}
GlobalPList ggg {
   PList fff;
   Pat c;
}
GlobalPList hhh {
   Pat c;
}
GlobalPList cpu_fuse_read_hvm_x {
   PList ggg;
   Pat a;
}
GlobalPList cpu_fuse_read_special_x {
   Pat b;
}
''', mkdir=True)
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.main()
        expect = '''
GlobalPList fff
{
 Pat f;
}
GlobalPList ggg
{
 PList fff;
 Pat c;
}
GlobalPList cpu_fuse_read_hvm_x
{
 PList ggg;
 Pat a;
}
GlobalPList cpu_fuse_read_special_x
{
 Pat b;
}
'''
        self.assertTextEqual(File('clean_plist/fuse.plist').read().replace('\t', ' '), expect)

        # run again - limited iteration - to exhaust the loop (coverage)
        with self.assertRaises(ErrorInput):     # error because of dependent
            cplist.main(_maxiter=0)
        expect = '''
GlobalPList ggg
{
 PList fff;
 Pat c;
}
GlobalPList cpu_fuse_read_hvm_x
{
 PList ggg;
 Pat a;
}
GlobalPList cpu_fuse_read_special_x
{
 Pat b;
}
        '''
        self.assertTextEqual(File('clean_plist/fuse.plist').read().replace('\t', ' '), expect)

    @with_(TempDir, chdir=True)
    def test_process_plist_partial(self):
        # Targetted tests for process_plist()
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList main1 {
    GlobalPList main2 {
        GlobalPList main3 {
            Pat a1;
            Pat a2;
        }
        GlobalPList main4 {
            Pat b;
        }
    }
}
GlobalPList main1a {
    Pat a;
}
'''
        # case1 - main3, main4 is used
        File('a.plist').touch(text, newfile=True)
        cplist.process_plist('a.plist', {'main3', 'main4'}, {'main3': {'a2'}})
        expect = '''
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main3
  {
   Pat a2;
  }
  GlobalPList main4
  {
   Pat b;
  }
 }
}
'''
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

        # case2 - main3 is used
        File('a.plist').touch(text, newfile=True)
        cplist.process_plist('a.plist', {'main3'}, {'main3': {'a2'}})
        expect = '''
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main3
  {
   Pat a2;
  }
 }
}
'''
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

        # case3 - main3 is used, nothing to keep
        File('a.plist').touch(text, newfile=True)
        cplist.process_plist('a.plist', {'main3'}, {'main3': set()})
        expect = '''
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main3
  {
  }
 }
}
'''
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

    @with_(TempDir, chdir=True)
    def test_process_plist(self):
        # Targetted tests for process_plist()
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList main1 {
    GlobalPList main2 {
        GlobalPList main3 {
            Pat a;
        }
        GlobalPList main4 {
            Pat b;
        }
    }
}
GlobalPList main1a {
    Pat a;
}
'''
        # case1 - main3 is used
        File('a.plist').touch(text, newfile=True)
        cplist.process_plist('a.plist', {'main3', 'main5'}, {})
        expect = '''
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main3
  {
   Pat a;
  }
 }
}
'''
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

        # case1a - main4 is used
        cplist.process_plist('a.plist', {'main4'}, {})
        expect = '''
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main4
  {
   Pat b;
  }
 }
}
'''
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

        # case2 - main3, main4 and main1a is used
        expect = '''
GlobalPList main1
{
 GlobalPList main2
 {
  GlobalPList main3
  {
   Pat a;
  }
  GlobalPList main4
  {
   Pat b;
  }
 }
}
GlobalPList main1a
{
 Pat a;
}
'''
        cplist.process_plist('a.plist', {'main3', 'main4', 'main1a'}, {})
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)
        cplist.process_plist('a.plist', {'main2', 'main1a'}, {})
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)
        cplist.process_plist('a.plist', {'main2', 'main4', 'main1a'}, {})
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)
        cplist.process_plist('a.plist', {'main1', 'main1a'}, {})
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

        # case3 - main1a is used
        cplist.process_plist('a.plist', {'main1a'}, {})
        expect = '''
GlobalPList main1a
{
 Pat a;
}
'''
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), expect)

        # case5 - none match, so empty
        cplist.process_plist('a.plist', {'mainx'}, {})
        self.assertTextEqual(File('out/a.plist').read().replace('\t', ' '), '\n')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_process_plist_case_insensitive_owner_lookup(self):
        # Test that owner lookup is case-insensitive for plist filenames
        # This prevents false UnknownModule fallbacks when get_mod2plist_map() returns
        # mixed-case filenames but inputfname uses different casing
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList test_block {
    Pat testpat;
}
GlobalPList unused_block {
    Pat unused;
}
'''
        # Create a plist file with mixed case name
        File('TestFile.plist').touch(text, newfile=True)

        # Mock get_mod2plist_map to return uppercase filename
        orig_get_mod2plist_map = tpobj.plists.get_mod2plist_map

        def mock_get_mod2plist_map():
            result = orig_get_mod2plist_map()
            # Add our test file with uppercase in the map
            result['TestModule'] = {'TESTFILE.PLIST'}
            return result

        # Mock get_mod2fname to include TestModule
        orig_get_mod2fname = tpobj.mtpl.get_mod2fname

        def mock_get_mod2fname():
            result = orig_get_mod2fname()
            result['TestModule'] = 'Modules/TestModule/test.mtpl'
            return result

        with MockVar(tpobj.plists, 'get_mod2plist_map', mock_get_mod2plist_map):
            with MockVar(tpobj.mtpl, 'get_mod2fname', mock_get_mod2fname):
                # Process with lowercase filename - should still find TestModule
                removed = cplist.process_plist('testfile.plist', {'test_block'}, {})

                # Verify that owner was resolved (not 'UnknownModule')
                # The removed set should contain (fname, plb, owner) tuples
                self.assertEqual(len(removed), 1)
                removed_item = list(removed)[0]
                # Owner should be 'TestModule' (fallback when no owner.txt) not 'UnknownModule'
                self.assertEqual(removed_item[2], 'TestModule')
                self.assertEqual(removed_item[1], 'unused_block')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_process_plist_with_owner_file(self):
        # Test process_plist with owner.txt file  containing owner info
        # This covers the missing lines 1346-1350 where owner file is read successfully
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList test_block {
    Pat testpat;
}
GlobalPList unused_block {
    Pat unused;
}
'''
        # Create a plist file
        File('TestFile.plist').touch(text, newfile=True)

        # Create owner.txt with owner: line
        owner_dir = 'Modules/TestOwnerModule'
        mkdirs(owner_dir)
        File(f'{owner_dir}/owner.txt').touch('owner: TestOwner\nemail: test@example.com\n', newfile=True)

        # Mock get_mod2plist_map to return the test file
        orig_get_mod2plist_map = tpobj.plists.get_mod2plist_map

        def mock_get_mod2plist_map():
            result = orig_get_mod2plist_map()
            result['TestOwnerModule'] = {'testfile.plist'}
            return result

        # Mock get_mod2fname to include TestOwnerModule with owner directory
        orig_get_mod2fname = tpobj.mtpl.get_mod2fname

        def mock_get_mod2fname():
            result = orig_get_mod2fname()
            result['TestOwnerModule'] = f'{owner_dir}/test.mtpl'
            return result

        with MockVar(tpobj.plists, 'get_mod2plist_map', mock_get_mod2plist_map):
            with MockVar(tpobj.mtpl, 'get_mod2fname', mock_get_mod2fname):
                removed = cplist.process_plist('testfile.plist', {'test_block'}, {})

                # Verify that owner was resolved from owner.txt
                self.assertEqual(len(removed), 1)
                removed_item = list(removed)[0]
                # Owner should be 'TestOwner' from owner.txt
                self.assertEqual(removed_item[2], 'TestOwner')
                self.assertEqual(removed_item[1], 'unused_block')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_process_plist_with_empty_owner_file(self):
        # Test process_plist with empty owner.txt file
        # This covers lines 1346-1350 where file is opened but loop finds no owner: line
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList test_block {
    Pat testpat;
}
GlobalPList unused_block {
    Pat unused;
}
'''
        # Create a plist file
        File('TestFile.plist').touch(text, newfile=True)

        # Create empty owner.txt
        owner_dir = 'Modules/TestOwnerModule'
        mkdirs(owner_dir)
        File(f'{owner_dir}/owner.txt').touch('', newfile=True)

        orig_get_mod2plist_map = tpobj.plists.get_mod2plist_map

        def mock_get_mod2plist_map():
            result = orig_get_mod2plist_map()
            result['TestOwnerModule'] = {'testfile.plist'}
            return result

        orig_get_mod2fname = tpobj.mtpl.get_mod2fname

        def mock_get_mod2fname():
            result = orig_get_mod2fname()
            result['TestOwnerModule'] = f'{owner_dir}/test.mtpl'
            return result

        with MockVar(tpobj.plists, 'get_mod2plist_map', mock_get_mod2plist_map):
            with MockVar(tpobj.mtpl, 'get_mod2fname', mock_get_mod2fname):
                removed = cplist.process_plist('testfile.plist', {'test_block'}, {})

                # Verify that owner is empty string when owner.txt exists but is empty
                self.assertEqual(len(removed), 1)
                removed_item = list(removed)[0]
                # Owner remains as '' when file exists but has no owner: line
                self.assertEqual(removed_item[2], '')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_process_plist_with_invalid_owner_file(self):
        # Test process_plist with owner.txt file lacking owner: keyword
        # This covers lines 1347-1350 where file has content but no matching owner: line
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList test_block {
    Pat testpat;
}
GlobalPList unused_block {
    Pat unused;
}
'''
        # Create a plist file
        File('TestFile.plist').touch(text, newfile=True)

        # Create owner.txt with content but no 'owner:' line
        owner_dir = 'Modules/TestOwnerModule'
        mkdirs(owner_dir)
        File(f'{owner_dir}/owner.txt').touch('# Comment\nemail: test@example.com\n', newfile=True)

        orig_get_mod2plist_map = tpobj.plists.get_mod2plist_map

        def mock_get_mod2plist_map():
            result = orig_get_mod2plist_map()
            result['TestOwnerModule'] = {'testfile.plist'}
            return result

        orig_get_mod2fname = tpobj.mtpl.get_mod2fname

        def mock_get_mod2fname():
            result = orig_get_mod2fname()
            result['TestOwnerModule'] = f'{owner_dir}/test.mtpl'
            return result

        with MockVar(tpobj.plists, 'get_mod2plist_map', mock_get_mod2plist_map):
            with MockVar(tpobj.mtpl, 'get_mod2fname', mock_get_mod2fname):
                removed = cplist.process_plist('testfile.plist', {'test_block'}, {})

                # Verify that owner is empty string when owner: line not found
                self.assertEqual(len(removed), 1)
                removed_item = list(removed)[0]
                # Owner remains as '' when file exists but has no owner: line
                self.assertEqual(removed_item[2], '')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_process_plist_with_module_path_missing(self):
        # Test process_plist when module exists in mod2plist_map but NOT in mod2fname
        # This covers the else branch on line 1382-1383 where module_path is None
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList test_block {
    Pat testpat;
}
GlobalPList unused_block {
    Pat unused;
}
'''
        # Create a plist file
        File('TestFile.plist').touch(text, newfile=True)

        # Mock get_mod2plist_map to return our test file for MissingModule
        orig_get_mod2plist_map = tpobj.plists.get_mod2plist_map

        def mock_get_mod2plist_map():
            result = orig_get_mod2plist_map()
            # Add mapping for a module that won't exist in mod2fname
            result['MissingModule'] = {'testfile.plist'}
            return result

        # Mock get_mod2fname to NOT include MissingModule
        # (module_path will be None when .get('MissingModule') is called)
        orig_get_mod2fname = tpobj.mtpl.get_mod2fname

        def mock_get_mod2fname():
            result = orig_get_mod2fname()
            # Don't add MissingModule to the mapping - this causes module_path to be None
            return result

        with MockVar(tpobj.plists, 'get_mod2plist_map', mock_get_mod2plist_map):
            with MockVar(tpobj.mtpl, 'get_mod2fname', mock_get_mod2fname):
                removed = cplist.process_plist('testfile.plist', {'test_block'}, {})

                # Verify that owner is set to module name when module_path is None
                self.assertEqual(len(removed), 1)
                removed_item = list(removed)[0]
                # When module_path is None, owner should be MissingModule (the fallback)
                self.assertEqual(removed_item[2], 'MissingModule')
                self.assertEqual(removed_item[1], 'unused_block')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_get_PatternsRegEx(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        result = cplist.get_PatternsRegEx({'FUS_METAL_KEY_0_RATIO8_splitby32_MsbToLsb': 'ARR'}, 'Name')
        self.assertEqual(len(result[0]), 45)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_PatternsRegex', chdir=True)
    def test_get_PatternsRegEx_generic(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        result = cplist.get_PatternsRegEx({'ABC': 'ARR', 'SAMPLE': 'ARR'}, 'Name')
        self.assertEqual(len(result[0]), 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_PatternsRegex_Optimized', chdir=True)
    def test_get_PatternsRegEx_optimized(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        # cplist.pat_mregex_cache = {tuple({".*_DfxSecAgg.*"}):['g2026553W2694949I_6I_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_DfxSecAgg_PartID','g2026532W2371472I_6I_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_DfxSecAgg_Efuse','g2026534W2371473I_6I_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_DfxSecAgg_Status_Csr']}
        cplist.pat_mregex_cache = {tuple({".*_SHOPSL", ".*_SHOPSH"}): ['d2294511W1466650I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL', 'd2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH']}
        result = cplist.get_PatternsRegEx({'ABC': 'ARR', 'SAMPLE': 'ARR', 'SAMPLE_debug': 'ARR', 'DUPLICATE': 'ARR', 'DUPLICATE_debug': 'ARR'}, 'Name')
        self.assertEqual(len(result[0]), 11)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_PatternsRegex_TT_Optimized', chdir=True)
    def test_get_PatternsRegEx_optimized_for_testtime(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        result = cplist.get_PatternsRegEx({'Fuse_HvmData': 'ARR', 'Fuse_HvmData_Read': 'ARR'}, 'Name')
        self.assertEqual(len(result[0]), 5)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4', chdir=True)
    def test_get_pat_regex_from_aleph_env_tos4(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_pat_regex_from_aleph_env('SetPoint')
        self.assertEqual(len(result), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_floating_test_PrimeHptpTIming_patmod_call', chdir=True)
    def test_get_pat_regex_from_mtpl_TimingCalPatmodConfiguration_PrimeHptpTimingCalibration(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_pat_regex_from_aleph_env('SetPoint')
        self.assertEqual(len(result[0]), 3)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_PrimePatmodConfig_config_json_path_not_resolvable', chdir=True)
    def test_get_pat_regex_from_aleph_env_mtpl_jsonpath_not_resolvable(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_pat_regex_from_aleph_env('SetPoint')
        self.assertEqual(len(result), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_RunCallBack_ExecutePatConfigSetPoint_PrimePauseTM', chdir=True)
    def test_get_pat_regex_from_aleph_RunCallBack_PrimePauseTM(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_pat_regex_from_aleph_env({'g2294511W1466650I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL',
                                                      'g2026529W2371469I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m0',
                                                      'g2026525W2371465I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_nom',
                                                      'g2026531W2371471I_Nt_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m0',
                                                      'tgl_pst_W9999993H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0',
                                                      'g2026530W2371470I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m1',
                                                      'g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1',
                                                      'g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom',
                                                      'g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH'}, 'SetPoint')
        self.assertEqual(len(result), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_plb_from_configfile_json', chdir=True)
    def test_get_plb_from_json(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_plb_from_json({'shops_L_list'})
        self.assertEqual(len(result), 3)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_tos4_plb_from_configfile_json', chdir=True)
    def test_get_plb_from_json_sort(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init(light=True)
        cplist = CleanPlist(tpobj)
        cplist.main()
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR}/san_unit_test/check_files/Shops.cleanplist.gold2')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/san_unit_test/Simple6_tos4_undiscoverable_jsonpath', chdir=True)
    def test_get_plb_from_missing_json(self):
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True)
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_plb_from_json({'shops_L_list'})
        self.assertEqual(len(result), 3)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/san_unit_test/Simple6_tos4_undiscoverable_jsonpath', chdir=True)
    def test_get_plb_from_JsonRun_calls(self):
        # Future reference:
        # The fixture contains a malformed JsonRun file (per_array_vmin_bad.json).
        # get_plb_from_JsonRun_calls() now catches ErrorInput from JsonRead.load(), logs it,
        # and continues instead of raising. Valid JsonRun files in the same run still
        # contribute plist values, so the TOS4 result includes the seed used plist plus
        # the two plists discovered from valid callback JSON.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True)
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_plb_from_JsonRun_calls({'shops_L_list'})  # Simple6_tos4_undiscoverable_jsonpath\Modules\ARR\InputFiles\per_array_vmin.json
        self.assertEqual(result, {'shops_L_list', 'arr_L_list', 'fun_cdie_ccrf2_core_low_power_test_list'})

        # In non-TOS4 mode the same JSON files are resolved via Env.xpath (TOS3 path)
        # and the valid ones contribute plists just like TOS4, so result stays at 1.
        tpobj.is_tos4 = False
        cplist = CleanPlist(tpobj)
        result = cplist.get_plb_from_JsonRun_calls({'shops_L_list'})  # Simple6_tos4_undiscoverable_jsonpath\Modules\ARR\InputFiles\per_array_vmin_bad.json.json
        self.assertEqual(len(result), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/san_unit_test/Simple6_tos4_undiscoverable_jsonpath', chdir=True)
    def test_get_plb_from_json_tos4_resolvable_path(self):
        # Test missing config files are skipped while dict-based PLists entries are retained
        existing_json = os.path.abspath('existing_config.json')
        File(existing_json).touch('{"PLists": {"shops_L_list": {}, "new_plb": {}}}', newfile=True)

        class _MtplStub:
            def iter_tests(self, template_name=None, edict=False):
                if template_name == 'MbistRasterRepairTC':
                    return [
                        ('ARR', 'MISS', {'RasterInputFile': 'missing_config.json'}, None),
                        ('ARR', 'HIT', {'RasterInputFile': 'existing_config.json'}, None),
                    ]
                return []

        class _UsrvStub:
            def eval_param(self, param, testplan, is_print=True):
                if param == 'missing_config.json':
                    return os.path.abspath('missing_config.json')
                if param == 'existing_config.json':
                    return existing_json
                return param

        class _TpObjStub:
            def __init__(self):
                self.mtpl = _MtplStub()
                self.usrv = _UsrvStub()

        cplist = CleanPlist.__new__(CleanPlist)
        cplist.tpobj = _TpObjStub()
        result = cplist.get_plb_from_json({'shops_L_list'})

        self.assertIn('shops_L_list', result)
        self.assertIn('new_plb', result)

    @with_(TempDir, chdir=True)
    def test_plist_noclean_patlist_parsing(self):
        # Test exact PATLIST_NOCLEAN parsing plus REGEX_PATLIST_NOCLEAN expansion
        tpobj = TestProgram.__new__(TestProgram)
        tpobj.tpldir = '.'
        tpobj.is_tos4 = False
        tpobj.plists = Mock()
        tpobj.plists.get_plb_map = Mock(return_value={
            'test_plist': 'test.plist',
            'regex_one': 'regex_one.plist',
            'regex_two': 'regex_two.plist'
        })
        tpobj.get_all_mtpl_from_stpl = Mock(return_value=['test.mtpl'])
        tpobj.mtpl = Mock()
        tpobj.mtpl.read_comments = Mock(return_value=({
            'MyTest': [
                'patlist = "test_plist"; # PATLIST_NOCLEAN: reason',
                '# REGEX_PATLIST_NOCLEAN: regex_.*',
            ]
        },))

        cplist = CleanPlist(tpobj)
        result = cplist.get_plist_noclean()
        self.assertEqual(result, {'test_plist', 'regex_one', 'regex_two'})

    @with_(TempDir, chdir=True)
    def test_process_plist_with_partial_block_removal(self):
        # Test nested used block discovery plus partial pattern retention
        plist_content = '''Version 6.0;
GlobalPList parent
{
    GlobalPList child_keep
    {
        GlobalPList nested_keep
        {
            Pat pat_keep;
            Pat pat_drop;
        }
    }
    GlobalPList child_drop
    {
        Pat pat_unused;
    }
}
'''
        File('test.plist').touch(plist_content, newfile=True)

        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        keepdict = {'nested_keep': {'pat_keep'}}
        used = {'child_keep'}

        result = cplist.process_plist('test.plist', used, keepdict)
        self.assertEqual(result, {('test.plist', 'child_drop', '')})
        self.assertTextEqual(File('out/test.plist').read().replace('\t', ' '), '''Version 6.0;
GlobalPList parent
{
 GlobalPList child_keep
 {
  GlobalPList nested_keep
  {
   Pat pat_keep;
  }
 }
}
''')

    @with_(TempDir, chdir=True)
    def test_remove_block_partial_pattern_removal(self):
        # Test full block deletion plus partial pattern retention in a kept block
        raw_lines = [
            'GlobalPList remove_me\n',
            '{\n',
            '    Pat old_pattern;\n',
            '}\n',
            'GlobalPList keep_partial\n',
            '{\n',
            '    Pat pattern_keep;\n',
            '    Pat pattern_remove;\n',
            '}\n'
        ]
        keepdict = {'keep_partial': {'pattern_keep'}}
        removeset = {'remove_me'}

        cplist = CleanPlist.__new__(CleanPlist)
        cplist.globalplist = 'GlobalPList '

        result = cplist.remove_block(raw_lines, removeset, keepdict)
        result_text = ''.join(result)
        self.assertNotIn('remove_me', result_text)
        self.assertIn('pattern_keep', result_text)
        self.assertNotIn('pattern_remove', result_text)

    @with_(TempDir, chdir=True)
    def test_get_plb_from_json_malformed_json(self):
        # get_plb_from_json skips malformed JSON files via ErrorInput handler (lines 1006-1008)
        bad_json = os.path.abspath('bad_raster.json')
        File(bad_json).touch('{ not valid json }', newfile=True)

        class _MtplStub:
            def iter_tests(self, template_name=None, edict=False):
                if template_name == 'MbistRasterRepairTC':
                    return [('ARR', 'INST', {'RasterInputFile': bad_json}, None)]
                return []

        class _UsrvStub:
            def eval_param(self, param, testplan, is_print=True):
                return param

        class _TpObjStub:
            def __init__(self):
                self.mtpl = _MtplStub()
                self.usrv = _UsrvStub()

        cplist = CleanPlist.__new__(CleanPlist)
        cplist.tpobj = _TpObjStub()
        result = cplist.get_plb_from_json({'seed_plb'})
        # Malformed JSON is skipped; seed is returned unchanged
        self.assertEqual(result, {'seed_plb'})

    @with_(TempDir, chdir=True)
    def test_get_PatternsRegEx_malformed_json(self):
        # get_PatternsRegEx skips malformed ALEPH JSON files via ErrorInput handler (lines 1082-1084)
        bad_aleph = os.path.abspath('bad_aleph.json')
        File(bad_aleph).touch('{ invalid aleph json }', newfile=True)

        class _EnvStub:
            def get_contents(self, key, islist):
                return [bad_aleph]

        class _TpObjStub:
            env = _EnvStub()

        cplist = CleanPlist.__new__(CleanPlist)
        cplist.tpobj = _TpObjStub()
        cplist.pat_mregex_cache = {}
        with MockVar(cleantp_mod.Env, 'xpath', lambda x: x):
            result = cplist.get_PatternsRegEx({'config1': 'test_inst'}, set())
        # Malformed JSON skipped; empty patterns and plists returned
        self.assertEqual(result, (set(), set()))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4', chdir=True)
    def test_get_pat_regex_from_aleph_env_malformed_config_json(self):
        # Test that malformed ConfigurationFile JSON in flow is skipped (lines 1200-1202)
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_pat_regex_from_aleph_env('SetPoint')
        # Should handle gracefully and return results
        self.assertEqual(len(result), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/san_unit_test/Simple6_tos4_undiscoverable_jsonpath', chdir=True)
    def test_get_pat_regex_from_aleph_env_malformed_patconfigsetpoints_integration(self):
        # Integration-style fixture test for malformed PatConfigSetpoints handling.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.is_tos4 = True
        cplist = CleanPlist(tpobj)
        result = cplist.get_pat_regex_from_aleph_env('SetPoint')
        # Should handle gracefully and return results
        self.assertEqual(len(result), 2)

    @with_(TempDir, chdir=True)
    def test_get_pat_regex_from_aleph_env_malformed_patconfigsetpoints(self):
        # Verify malformed PatConfigSetpoints JSON is handled gracefully with error_out=False.
        bad_setpoints = os.path.abspath('broken_PatConfigSetpoints.json')
        File(bad_setpoints).touch('{ invalid json ', newfile=True)

        class _MtplStub:
            def iter_flows(self, flow, **kwargs):
                return iter([])

        class _EnvStub:
            def get_contents(self, key, islist=True):
                if key == 'ALEPH_FILES':
                    return [bad_setpoints]
                return []

        class _PlistsStub:
            def get_plbs_usedby_pats(self, pats):
                return {}

        class _TpObjStub:
            def __init__(self):
                self.env = _EnvStub()
                self.mtpl = _MtplStub()
                self.plists = _PlistsStub()

        cplist = CleanPlist.__new__(CleanPlist)
        cplist.tpobj = _TpObjStub()
        cplist.pat_mregex_cache = {}

        with MockVar(cplist, 'get_PatternsRegEx', Mock(return_value=(set(), set()))):
            result = cplist.get_pat_regex_from_aleph_env(set())

        self.assertEqual(dict(result[0]), {})
        self.assertEqual(result[1], set())

    @with_(TempDir, chdir=True)
    def test_process_plist_multiple_module_ownership(self):
        # process_plist with a plist shared by multiple modules sets owner='' (line 1425)
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList keep_one {
    Pat kept_pat;
}
GlobalPList remove_one {
    Pat unused_pat;
}
'''
        File('multi.plist').touch(text, newfile=True)

        def mock_get_mod2plist_map():
            # Two modules share the same plist file
            return {
                'MOD_A': {'multi.plist'},
                'MOD_B': {'multi.plist'},
            }

        with MockVar(tpobj.plists, 'get_mod2plist_map', mock_get_mod2plist_map):
            result = cplist.process_plist('multi.plist', {'keep_one'}, {})
        # MULTIPLE ownership: owner field is empty string
        self.assertEqual(result, {('multi.plist', 'remove_one', '')})

    @with_(TempDir, chdir=True)
    def test_process_plist_module_path_none_fallback(self):
        # process_plist falls back to module name when module_path is None (line 1444)
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        cplist = CleanPlist(tpobj)
        cplist.dest = './out'
        mkdirs(cplist.dest)

        text = '''
GlobalPList used_block {
    Pat good_pat;
}
GlobalPList fat_block {
    Pat bad_pat;
}
'''
        File('orphan.plist').touch(text, newfile=True)

        def mock_get_mod2plist_map():
            # Single module owns the plist (unambiguous)
            return {'GHOST_MOD': {'orphan.plist'}}

        def mock_get_mod2fname():
            # Module is NOT in mod2fname (returns None via .get())
            return {}

        with MockVar(tpobj.plists, 'get_mod2plist_map', mock_get_mod2plist_map), \
                MockVar(tpobj.mtpl, 'get_mod2fname', mock_get_mod2fname):
            result = cplist.process_plist('orphan.plist', {'used_block'}, {})
        # module_path is None: owner falls back to module name
        self.assertEqual(result, {('orphan.plist', 'fat_block', 'GHOST_MOD')})


class TestTCGClean(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_TCG', chdir=True)
    def test_basic(self):
        # Integration test for CleanTCG.
        # This tests start to finish. This checks that the tcg files are updated and correct.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        ctcg = CleanTCG(tpobj)
        result = ctcg.main()

        # these are the blocks that are removed
        self.assertEqual(result, {'ARR': {'atc2_lvl', 'STF_univ_lvl_TCG'},
                                  'BASE': {'tc2_tim'}})
        self.assertGoldEqual('Shared/BaseInputs/BaseTiming.tcg',
                             f'{UT_DIR}/misc_files/cleantp_BaseTiming.tcg.gold1')

    def _make_tcg_noclean_tpobj(self, comments_by_file):
        class MockMtpl:
            def read_comments(self, f):
                return (comments_by_file.get(f, {}),)

        class MockTpobj:
            mtpl = MockMtpl()

            def get_all_mtpl_from_stpl(self):
                return list(comments_by_file.keys())

        return MockTpobj()

    def _build_tcg_owner_test_cleaner(self, tpobj, pth_dir):
        class _TCStub:
            def __init__(self, tc_items):
                self._tc_items = tc_items

            def iter_tc(self):
                return iter(self._tc_items)

            def get_tc_dict(self):
                return {}

        pth_tcg = f'{pth_dir}/pth.tcg'
        File(pth_tcg).touch('timing_test { }\n', newfile=True)

        tpobj.timing = _TCStub(['PTH::test_timing'])
        tpobj.levels = _TCStub(['PTH::test_level'])

        def _get_import_files(ext):
            if ext == 'tcg':
                return [pth_tcg]
            return []

        tpobj.get_import_files = _get_import_files

        ctcg = CleanTCG(tpobj)
        ctcg.get_used = lambda _: set()
        ctcg.remove_blocks = lambda *_: None

        scope_results = [
            {'PTH': {'test_timing'}},
            {'PTH': {'test_level'}},
            {'PTH': {'test_timing', 'test_level'}},
        ]

        def _get_scopedict(*_args, **_kwargs):
            return scope_results.pop(0)

        ctcg.get_scopedict = _get_scopedict
        return ctcg

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_tcg_cleanup_with_owner_file(self):
        # Test that owner.txt content is correctly read and included in the CSV report
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)

        # Create cleantp_on_default.txt to optin all modules
        trigger_file = f'{tpobj.tpldir}/Shared/BaseInputs/InputFiles/cleantp_on_default.txt'
        os.makedirs(os.path.dirname(trigger_file), exist_ok=True)
        File(trigger_file).touch('', newfile=True)

        # Create owner.txt with owner info in PTH module directory
        pth_dir = os.path.dirname(tpobj.mtpl.get_mod2fname()['PTH'])
        owner_file = f'{pth_dir}/owner.txt'
        File(owner_file).touch('owner: TestOwner\n', newfile=True)

        # Run cleanup
        ctcg = self._build_tcg_owner_test_cleaner(tpobj, pth_dir)
        ctcg.main()

        # Observable behavior: owner appears in the CSV report output
        csv_file = f'{os.path.dirname(tpobj.get_stpl())}/Reports/Cleantp_fullreport.csv'
        csv_content = File(csv_file).read()
        self.assertIn('TestOwner', csv_content)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_tcg_cleanup_with_empty_owner_file(self):
        # Test that empty owner.txt results in empty owner field in the CSV report
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)

        # Create cleantp_on_default.txt
        trigger_file = f'{tpobj.tpldir}/Shared/BaseInputs/InputFiles/cleantp_on_default.txt'
        os.makedirs(os.path.dirname(trigger_file), exist_ok=True)
        File(trigger_file).touch('', newfile=True)

        # Create empty owner.txt file in PTH module directory
        pth_dir = os.path.dirname(tpobj.mtpl.get_mod2fname()['PTH'])
        owner_file = f'{pth_dir}/owner.txt'
        File(owner_file).touch('', newfile=True)

        # Run cleanup
        ctcg = self._build_tcg_owner_test_cleaner(tpobj, pth_dir)
        ctcg.main()

        # Observable behavior: CSV report is generated
        csv_file = f'{os.path.dirname(tpobj.get_stpl())}/Reports/Cleantp_fullreport.csv'
        self.assertTrue(os.path.exists(csv_file))

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6cleantp', chdir=True)
    def test_tcg_cleanup_with_invalid_owner_file(self):
        # Test that owner.txt without 'owner:' keyword results in empty owner in CSV
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init(light=True)

        # Create cleantp_on_default.txt
        trigger_file = f'{tpobj.tpldir}/Shared/BaseInputs/InputFiles/cleantp_on_default.txt'
        os.makedirs(os.path.dirname(trigger_file), exist_ok=True)
        File(trigger_file).touch('', newfile=True)

        # Create owner.txt with content but no 'owner:' line
        pth_dir = os.path.dirname(tpobj.mtpl.get_mod2fname()['PTH'])
        owner_file = f'{pth_dir}/owner.txt'
        File(owner_file).touch('# Comments\nemail: test@example.com\n', newfile=True)

        # Run cleanup
        ctcg = self._build_tcg_owner_test_cleaner(tpobj, pth_dir)
        ctcg.main()

        # Observable behavior: CSV report is generated successfully
        csv_file = f'{os.path.dirname(tpobj.get_stpl())}/Reports/Cleantp_fullreport.csv'
        self.assertTrue(os.path.exists(csv_file))

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_tos_rules', chdir=True)
    def test_tos_rules(self):
        # Integration test for CleanTCG.
        # Checks to make sure all levels and timings present in tos rules are kept.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        ctcg = CleanTCG(tpobj)
        result = ctcg.main()

        # these are the blocks that are removed
        self.assertGoldEqual('Modules/PTH/pth.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/pth.tcg.tosrules.gold')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_noclean_tcg', chdir=True)
    def test_get_tcg_noclean(self):
        # Integration test for CleanTCG.
        # Checks to make sure all levels and timings present in tos rules are kept.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        ctcg = CleanTCG(tpobj)
        result = ctcg.main()

        # these are the blocks that are removed
        self.assertGoldEqual('Modules/ARR/array.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/array.tcg_noclean.gold')

    def test_get_tcg_noclean_double_quoted(self):
        # Double-quoted TCG value is extracted correctly
        tpobj = self._make_tcg_noclean_tpobj({'f.mtpl': {'inst1': ['# tcg = "PTH::timings_blah"; # TCG_NOCLEAN: reason']}})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), {'PTH::timings_blah'})

    def test_get_tcg_noclean_single_quoted(self):
        # Single-quoted TCG value is extracted correctly
        tpobj = self._make_tcg_noclean_tpobj({'f.mtpl': {'inst1': ["# tcg = 'PTH::timings_blah'; # TCG_NOCLEAN: reason"]}})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), {'PTH::timings_blah'})

    def test_get_tcg_noclean_unquoted(self):
        # Unquoted TCG value is extracted correctly
        tpobj = self._make_tcg_noclean_tpobj({'f.mtpl': {'inst1': ['# tcg = PTH::timings_blah; # TCG_NOCLEAN: reason']}})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), {'PTH::timings_blah'})

    def test_get_tcg_noclean_tag_case_insensitive(self):
        # TCG_NOCLEAN tag is matched case-insensitively (all-lowercase variant)
        tpobj = self._make_tcg_noclean_tpobj({'f.mtpl': {'inst1': ['# tcg = "MY::tcg_val"; # tcg_noclean: reason']}})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), {'MY::tcg_val'})

    def test_get_tcg_noclean_tag_mixed_case(self):
        # TCG_NOCLEAN tag is matched with arbitrary mixed case
        tpobj = self._make_tcg_noclean_tpobj({'f.mtpl': {'inst1': ['# tcg = "MY::tcg_val"; # Tcg_NoCLean: reason']}})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), {'MY::tcg_val'})

    def test_get_tcg_noclean_no_tag_returns_empty(self):
        # Comment without TCG_NOCLEAN tag yields empty set
        tpobj = self._make_tcg_noclean_tpobj({'f.mtpl': {'inst1': ['# tcg = "MY::tcg_val"; # some_other_comment']}})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), set())

    def test_get_tcg_noclean_multiple_files(self):
        # TCGs collected across multiple files with mixed quote styles
        tpobj = self._make_tcg_noclean_tpobj({
            'a.mtpl': {'inst1': ['# tcg = "BASE::tim1"; # TCG_NOCLEAN: reason1']},
            'b.mtpl': {'inst2': ["# tcg = 'BASE::lvl1'; # TCG_NOCLEAN: reason2"]},
            'c.mtpl': {'inst3': ['# tcg = BASE::lvl2; # TCG_NOCLEAN: reason3']},
        })
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), {'BASE::tim1', 'BASE::lvl1', 'BASE::lvl2'})

    def test_get_tcg_noclean_no_tcg_assignment(self):
        # TCG_NOCLEAN present but no tcg= assignment extracts nothing
        tpobj = self._make_tcg_noclean_tpobj({'f.mtpl': {'inst1': ['# some_param = value; # TCG_NOCLEAN: reason']}})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), set())

    def test_get_tcg_noclean_empty_files_list(self):
        # No mtpl files yields empty set
        tpobj = self._make_tcg_noclean_tpobj({})
        self.assertEqual(CleanTCG(tpobj).get_tcg_noclean(), set())

    def test_get_tcg_noclean_with_all_quote_types(self):
        # Test get_tcg_noclean with various quote formats
        # This ensures complete coverage of lines 1549-1551 (match extraction branches)
        tpobj = self._make_tcg_noclean_tpobj({
            'a.mtpl': {
                'inst1': ['# tcg = "BASE::double_quoted_tcg"; # TCG_NOCLEAN: reason1'],
                'inst2': ["# tcg = 'BASE::single_quoted_tcg'; # TCG_NOCLEAN: reason2"],
                'inst3': ['# tcg = BASE::unquoted_tcg; # TCG_NOCLEAN: reason3'],
            },
        })
        result = CleanTCG(tpobj).get_tcg_noclean()
        self.assertEqual(result, {'BASE::double_quoted_tcg', 'BASE::single_quoted_tcg', 'BASE::unquoted_tcg'})

    @with_(TempDir, chdir=True)
    def test_get_tcg_noclean_empty_match_group(self):
        # Test get_tcg_noclean with malformed tcg assignment where value is whitespace only
        # This covers lines 1549-1551 where tcg regex doesn't match at all
        tpobj = self._make_tcg_noclean_tpobj({
            'a.mtpl': {
                'inst1': ['# tcg ; # TCG_NOCLEAN: testing no assignment'],
            },
        })
        result = CleanTCG(tpobj).get_tcg_noclean()
        # Should return empty set since no tcg= assignment exists
        self.assertEqual(result, set())

    @with_(TempDir, chdir=True)
    def test_get_tcg_noclean_no_value_extracted(self):
        # Test get_tcg_noclean where tag and assignment exist but value has no valid chars after =
        # This tests the case where regex match succeeds but all capture groups are empty
        tpobj = self._make_tcg_noclean_tpobj({
            'a.mtpl': {
                'inst1': ['# tcg = # TCG_NOCLEAN: assignment with no value'],
            },
        })
        result = CleanTCG(tpobj).get_tcg_noclean()
        # Should return empty set since no valid tcg name can be extracted
        self.assertEqual(result, set())

    @with_(TempDir, chdir=True)
    def test_remove_blocks(self):
        ctcg = CleanTCG(None)
        text = '''Version 1.0;
SpecificationSet arr_STF_univ_lvl_BFUNC (aaa, bbb, ccc, ddd) Inherits __main__::STF_univ_lvl_BFUNC
{
        Double tper = 1.1, 2.1, 3.1, 4.1;
}
TestConditionGroup a_STF_univ_lvl_TCG
{
        SpecificationSet = arr_STF_univ_lvl_BFUNC;
        Level = __main__::DDR_univ_lvl_pkg;
}
TestCondition atc1_lvl
{
        TestConditionGroup  = a_STF_univ_lvl_TCG;
        Selector = bbb;
}
'''
        File('a.tcg').touch(text)

        # case1: nothing to remove
        ctcg.remove_blocks('a.tcg', {'blah'})
        self.assertTextEqual('\n'.join(x.strip() for x in File('a.tcg').read().split('\n')),
                             '\n'.join(x.strip() for x in text.split('\n')))

        # case2: remove all but one
        ctcg.remove_blocks('a.tcg', {'arr_STF_univ_lvl_BFUNC', 'atc1_lvl', 'blah'})
        expect = '''
Version 1.0;
TestConditionGroup a_STF_univ_lvl_TCG
{
        SpecificationSet = arr_STF_univ_lvl_BFUNC;
        Level = __main__::DDR_univ_lvl_pkg;
}
'''
        self.assertTextEqual('\n'.join(x.strip() for x in File('a.tcg').read().split('\n')),
                             '\n'.join(x.strip() for x in expect.split('\n')))

        # case3: remove all
        File('a.tcg').touch(text, newfile=True)
        ctcg.remove_blocks('a.tcg', {'arr_STF_univ_lvl_BFUNC', 'atc1_lvl', 'a_STF_univ_lvl_TCG'})
        expect = '''
Version 1.0;
'''
        self.assertTextEqual('\n'.join(x.strip() for x in File('a.tcg').read().split('\n')),
                             '\n'.join(x.strip() for x in expect.split('\n')))

    def test_update_tc_name(self):
        # basic
        data = {'__main__::all_tpi_xiucontinuity_x_x_pkg_level_cat0',
                'BASE::SBF_nom_lvl',
                'IP_CPU::FUN_ATOM_CXX::FUN_ATOM_CXX',
                'FUN_ATOM_CXX::FUN'}
        tc_all = {'BASE::SBF_nom_lvl': None,
                  'FUN_ATOM_CXX::FUN': None}
        self.assertEqual(CleanTCG.update_tc_name(data, tc_all),
                         {'FUN_ATOM_CXX::FUN_ATOM_CXX',
                          'BASE::all_tpi_xiucontinuity_x_x_pkg_level_cat0',
                          'BASE::SBF_nom_lvl',
                          'FUN_ATOM_CXX::FUN'})

        # no scope
        data = {'BASE::all_tpi_xiucontinuity_x_x_pkg_level_cat0',
                'SBF_nom_lvl',
                'FUN',
                'RAND1'}   # not found in tc_all
        self.assertEqual(CleanTCG.update_tc_name(data, tc_all),
                         {'BASE::all_tpi_xiucontinuity_x_x_pkg_level_cat0',
                          'BASE::SBF_nom_lvl',
                          'FUN_ATOM_CXX::FUN',
                          'RAND1'})


class TestCleanTP(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_main', chdir=True)
    def test_main_integration(self):
        # Integration test for full run
        # This tests start to finish, and checks Test Instances, Plists, and TCGs are removed correctly.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        cleantp = CleanTP(tpobj)
        cleantp.main()
        # Check Cleaned Instances
        self.assertGoldEqual('Modules/ARR/array.mtpl', f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_array.mtpl.nocleantags.gold')
        # Check Cleaned Plists
        self.assertGoldEqual('clean_plist/Shops.plist', f'{UT_DIR_REPO}/derek_unit_test/check_files/Shops.cleanplist_noclean.gold')
        # Check Cleaned TCGs
        self.assertGoldEqual('Shared/BaseInputs/BaseTiming.tcg',
                             f'{UT_DIR_REPO}/misc_files/cleantp_BaseTiming.tcg.gold1')
        self.assertGoldEqual('Shared/BaseInputs/BaseLevels.tcg',
                             f'{UT_DIR_REPO}/derek_unit_test/check_files/cleantp_BaseLevels.tcg.gold1')
        self.assertGoldEqual('Modules/ARR/array.tcg',
                             f'{UT_DIR_REPO}/misc_files/cleantp_array.tcg.gold1')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_main', chdir=True)
    def test_add2report(self):
        # Add2report tests CSV file matches expected when given 2-tuple dataset (no Owner).
        # Validates that the 5-column header is written and Owner column is empty for 2-tuples.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        cleantp = CleanTP(tpobj)
        dataset = [('array', 'instance1'), ('array', 'instance2'), ('array', 'instance3'),
                   ('scan', 'instance1'), ('scan', 'instance2'), ('scan', 'instance3')]
        csv = cleantp.add2fullreport(tpobj, "Instance", "Cleaned", dataset)
        with open(csv) as f:
            actual = f.read()
        expected = (
            'Type, Module, Cleaned/Fat, Name, Owner\n'
            'Instance, array, Cleaned, instance1, \n'
            'Instance, array, Cleaned, instance2, \n'
            'Instance, array, Cleaned, instance3, \n'
            'Instance, scan, Cleaned, instance1, \n'
            'Instance, scan, Cleaned, instance2, \n'
            'Instance, scan, Cleaned, instance3, \n'
        )
        self.assertTextEqual(actual, expected)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_main', chdir=True)
    def test_add2report_with_owner(self):
        # Verify Owner column is populated when 3-tuple (mod, name, owner) dataset is used.
        # Also verifies that a 2-tuple entry still produces an empty Owner field in the same CSV.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        dataset = [('array', 'instance1', 'john_doe'),
                   ('array', 'instance2', 'jane_doe'),
                   ('scan', 'instance1')]
        csv = CleanTP.add2fullreport(tpobj, "Instance", "Cleaned", dataset)
        with open(csv) as f:
            actual = f.read()
        expected = (
            'Type, Module, Cleaned/Fat, Name, Owner\n'
            'Instance, array, Cleaned, instance1, john_doe\n'
            'Instance, array, Cleaned, instance2, jane_doe\n'
            'Instance, scan, Cleaned, instance1, \n'
        )
        self.assertTextEqual(actual, expected)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_main', chdir=True)
    def test_add2report_existing_empty_file(self):
        # Verify an existing but empty report file gets the new 5-column header before append.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        report_dir = f'{os.path.dirname(tpobj.get_stpl())}/Reports'
        csv_file = f'{report_dir}/Cleantp_fullreport.csv'
        File(csv_file).touch('', newfile=True)

        csv = CleanTP.add2fullreport(tpobj, 'Instance', 'Cleaned', [('arr', 'inst1')])
        with open(csv) as f:
            actual = f.read()
        expected = (
            'Type, Module, Cleaned/Fat, Name, Owner\n'
            'Instance, arr, Cleaned, inst1, \n'
        )
        self.assertTextEqual(actual, expected)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/derek_unit_test/Simple6cleantp_tos_rules2', chdir=True)
    def test_get_value_tosrule(self):
        # Test get tosrule function. Expects list of extrapolated params from tosrule.
        # If single param, expects returned single param in list form.
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        tos_param = 'MODULE_CXX_Rules.Select_Some_Rule("MOD::param1", "MOD::param2", "MOD::param3");'
        result_params = CleanTP.get_value_tosrule(tpobj, tos_param, 'PTH')
        expect = ['MOD::param1', 'MOD::param2', 'MOD::param3']
        self.assertListEqual(result_params, expect)
        single_param = "MOD::single_param"
        result_param = CleanTP.get_value_tosrule(tpobj, single_param, 'PTH')
        expect_single = ['MOD::single_param']
        self.assertListEqual(result_param, expect_single)
        tos_param_usrv = 'PTH_DLVR_CXX_Rules.Select_HOT_COLD_Otherwise(BYPASSVars.F2_TimingsTc, BYPASSVars.F2_TimingsTc_Scanout, BYPASSVars.F2_TimingsTc_Scanout);'
        result_eval_param = CleanTP.get_value_tosrule(tpobj, tos_param_usrv, 'PTH')
        expect = ['IP_CPU_BASE::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400', 'FUN_CORE_C2P::FUN_CORE_C2P_F2_FREQ_SCANOUT_TC_tdo2stf_tclk100_sclk400_cclk400',
                  'FUN_CORE_C2P::FUN_CORE_C2P_F2_FREQ_SCANOUT_TC_tdo2stf_tclk100_sclk400_cclk400']
        self.assertListEqual(result_eval_param, expect)
        usrv_single_param = 'BYPASSVars.F2_TimingsTc'
        result_usrv_single = CleanTP.get_value_tosrule(tpobj, usrv_single_param, 'PTH')
        expect = ['IP_CPU_BASE::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400']
        self.assertListEqual(result_usrv_single, expect)
        regex_param = '.*arr_cdie_catf4.*|.*arr_cdie_catf5.*|.*arr_cdie_catf6.*|.*arr_cdie_maxat.*r8.*'
        result_param = CleanTP.get_value_tosrule(tpobj, regex_param, 'PTH')
        expect_regex = ['.*arr_cdie_catf4.*|.*arr_cdie_catf5.*|.*arr_cdie_catf6.*|.*arr_cdie_maxat.*r8.*']
        self.assertListEqual(result_param, expect_regex)

        # unittest on get_value_tosrule()

        def fake(value, dummy, is_print=None):
            return value

        with MockVar(tpobj.usrv, 'eval_param', fake):
            param = '(_MTT(SCNVars.SCNAMXF7plist));'
            result = CleanTP.get_value_tosrule(tpobj, param, None)
            self.assertEqual(result, ['SCNVars.SCNAMXF7plist'])

            param = '(BYPASSVars.F2_TimingsTc);'
            result = CleanTP.get_value_tosrule(tpobj, param, None)
            self.assertEqual(result, ['BYPASSVars.F2_TimingsTc'])


class TestCleanPPR(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp', chdir=True)
    def test_PPR_integ(self):
        tpobj = TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp_PPR/POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        cleanppr = CleanPPR(tpobj)
        cleanppr.dest = './out'
        mkdirs(cleanppr.dest)
        cleanppr.main()
        self.assertGoldEqual('./out/Shops.plist', f'{UT_DIR}/san_unit_test/check_files/Shops.cleanplist.gold')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp', chdir=True)
    def test_read_PPR_config(self):
        tpobj = TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp/POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        cppr = CleanPPR(tpobj)
        ppr = cppr.read_PPR_config()
        self.assertEqual(4, len(ppr))

    @with_(TempDir, chdir=True)
    def test_read_PPR_config_malformed_json(self):
        # Malformed GlobalPPRconfiguration.json should be handled by JsonRead(error_out=False)
        # and return an empty mapping without raising.

        class _MtplStub:
            def get_subflows(self):
                return []

            def iter_flows(self, *args, **kwargs):
                return []

        class _TpobjStub:
            def __init__(self):
                self.tpldir = os.getcwd()
                self.is_tos4 = False
                self.mtpl = _MtplStub()

        malformed = os.path.join('Modules', 'PPR', 'InputFiles', 'GlobalPPRconfiguration.json')
        File(malformed).touch('{"PPRTargetTests": {"ARR::T1": }', mkdir=True, newfile=True)

        cppr = CleanPPR(_TpobjStub())
        ppr = cppr.read_PPR_config()

        self.assertEqual(ppr, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp', chdir=True)
    def test_get_plb_for_PPR_untag(self):
        tpobj = TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp/POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        cppr = CleanPPR(tpobj)
        # case 1:
        ppr = cppr.get_plb_for_PPR_untag({"CCA": "ARR"})
        self.assertEqual(3, len(ppr))

        # case 2:
        ppr = cppr.get_plb_for_PPR_untag({"SBFT_X_VMIN_K_CCRF6_X_VCORE_F6_5400_MLC_1001": "FUN_CORE_C2P", "SBFT_X_VMIN_K_CCLRF6_080808_VCCR_F6_3800_DRAGON_1004": "FUN_CCF_C2P"})
        self.assertEqual(4, len(ppr))

        # case 3: test instance has "DtsConfiguration" but set to empty string ""
        ppr = cppr.get_plb_for_PPR_untag({"CCW": "ARR"})
        self.assertEqual(4, len(ppr))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp', chdir=True)
    def test_PPR_untag_cleanplist(self):
        tpobj = TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp/POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        cppr = CleanPPR(tpobj)
        cppr.dest = './out'
        mkdirs(cppr.dest)

        # case 1:
        cppr.PPR_untag_cleanplist(set(["main3", "main5", "shops_H_list"]))
        self.assertGoldEqual('./out/tos3.plist', f'{UT_DIR}/san_unit_test/check_files/tos3.cleanplist.gold')

        # case 2: empty input - 'no plists to be cleaned up' test case
        cppr.PPR_untag_cleanplist(set())
        self.assertFalse(os.path.exists("./out/tos3_ut1.plist"))

        # case 3: non-empty input but ended up having to do no clean up
        cppr.PPR_untag_cleanplist(set(["mainZ"]))
        self.assertFalse(os.path.exists("./out/tos3_ut1.plist"))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6cleantp_noGlobalPPRConfig', chdir=True)
    def test_flag_for_PPR_cleanup(self):
        tpobj = TestProgram(f'{UT_DIR}/san_unit_test/Simple6cleantp_noGlobalPPRConfig/POR_TP/TGLH81/EnvironmentFile.env', allpats=True).init()
        cppr = CleanPPR(tpobj)
        self.assertTextEqual(str(cppr.flag_for_PPR_cleanup(tpobj)), "False")

    @with_(TempDir, chdir=True)
    def test_PPR_untag_cleanplist_tos4(self):
        text = """
        HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p4/plb"
        """
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
        <PList>
        <PListFile name="abc.plist" />
        </PList>
        </HdmtReferenceFile>
        """
        File("TPL/x.xml").touch(text)

        text = """
Version 6.0;
PList list1
{
Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0;
Pat xyzDTSTEMPREAD;
Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_1;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        tp.is_tos4 = True
        tp.plists.set_pat2plb()
        cppr = CleanPPR(tp)
        cppr.dest = './out'
        mkdirs(cppr.dest)
        with MockVar(CleanTP, 'flag_for_PPR_cleanup', Mock(return_value=True)):
            cppr.PPR_untag_cleanplist(set(["list1"]))
        expect = '''
Version 6.0;
PList list1
{
 Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0;
 Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_1;
}
'''
        self.assertTextEqual(File('./out/abc.plist').read().replace('\t', ' '), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
