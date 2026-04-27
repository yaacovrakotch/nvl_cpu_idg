#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for autocounters.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.helperclass import CaptureStdoutLog
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.disk import Chdir
from main.autocounter import *
from pprint import pformat
from os.path import join, dirname, abspath
import sys


class TestAC(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_cmdline(self):
        # Successful run
        cmd = f'autocounter.py -env POR_TP/TGLH81/EnvironmentFile.env'.split()
        with MockVar(sys, "argv", cmd):
            with CaptureStdoutLog() as p:
                MainArg().main()
            self.assertIn('Success AutoCounter', p.getvalue())

        # No args
        cmd = f'autocounter.py'.split()
        with MockVar(sys, "argv", cmd):
            with CaptureStdoutLog() as p:
                MainArg().main()
            self.assertIn('Success AutoCounter', p.getvalue())

        # Specific module
        cmd = f'autocounter.py Modules/ARR/array.mtpl'.split()
        with MockVar(sys, "argv", cmd):
            with CaptureStdoutLog() as p:
                MainArg().main()
            self.assertIn('Success AutoCounter', p.getvalue())

        # with 2nd TP
        cmd = f'autocounter.py Modules/ARR/array.mtpl -env POR_TP/TGLH81/EnvironmentFile.env -tp POR_TP/TGLH81/EnvironmentFile.env'.split()
        with MockVar(sys, "argv", cmd):
            with CaptureStdoutLog() as p:
                MainArg().main()
            self.assertIn('Success AutoCounter', p.getvalue())

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True)
    def test_read_secondarytp(self):
        File('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').touch(r'''
SubTestPlans
{
        Common ..\..\Shared\a.imp;
        ..\..\Modules\ARR\array.mtpl;
        ..\..\Modules\SCN\scan.mtpl;
        ..\..\Modules\PTH\pth.mtpl;
        ..\..\Modules\TPI_FLWFLGS_XXX\TPI_FLWFLGS_XXX.mtpl;
        ..\..\Modules\TPI_DIESLCT_XXX\TPI_DIESLCT_XXX.mtpl;

        Final .\ProgramFlowsTestPlan\ProgramFlows.mtpl;
}
''', newfile=True)

        envfile = f'POR_TP/TGLH81/EnvironmentFile.env'
        tpobj = TestProgram(envfile)
        ac = AutoCounter(tpobj)
        ac.read_secondarytp(envfile, ['./TPI_FLWFLGS_XXX.mtpl'])
        self.assertEqual(ac.othertp, {'90980001', '90930001', '90930057', '90990001', '90930002'})

    @with_(TempDir, chdir=True)
    def test_read_basic(self):
        # This unittest covers 99% coverage of read_counters() - only the "no SetBin is found" is not covered
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

Test PrimeFlowControlSetTestMethod SetFlowInfo_RF_F3_ATOMC_Flow4
{
    DomainName = "ATOMC";
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        # Two Softbins, Two counter add
        DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
                Result -1 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202080_fail_ARR_blah;
                        Return 0;
                }
        }
        # No softbin, One Counter add
        FlowItem ATOM_LSA_SRH_F5 ATOM_LSA_SRH_F5 {
                Result -1 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n90930057_fail;
                        Return 0;
                }
        }
}
'''
        fname = 'a.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        res = ac.read_counters(fname)
        expect = '''
[('ATOM_LSA_SRH_F6', '0', '90202079', False, 18),
 ('ATOM_LSA_SRH_F6', '2', '90202079', False, 27),
 ('ATOM_LSA_SRH_F5', '0', None, False, 40)]
'''
        self.assertTextEqual(pformat(res), expect)     # pprint.pformat
        self.assertEqual(ac.counter_block, {fname: [3, None]})
        self.assertEqual(ac.first_dig8, {fname: '90202079'})
        self.assertEqual(ac.registry, {})

    @with_(TempDir, chdir=True)
    def test_read_nosetbin(self):
        # Test case with counters and no set bin
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

Counters {
    n90930057_fail
}

Test PrimeFlowControlSetTestMethod SetFlowInfo_RF_F3_ATOMC_Flow4
{
    DomainName = "ATOMC";
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
                Result -1 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
        FlowItem ATOM_LSA_SRH_F5 ATOM_LSA_SRH_F5 {
                Result -1 {
                        Property PassFail = "Fail";
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n90930057_fail;
                        Return 0;
                }
        }
}
'''
        File('a.mtpl').touch(text)
        ac = AutoCounter(tpobj)
        res = ac.read_counters('a.mtpl')
        expect = '''
[('ATOM_LSA_SRH_F6', '0', None, False, 21),
 ('ATOM_LSA_SRH_F5', '-1', None, False, 31)]
'''
        self.assertTextEqual(pformat(res), expect)     # pprint.pformat
        self.assertEqual(ac.counter_block, {'a.mtpl': [4, 6]})
        self.assertEqual(ac.first_dig8, {'a.mtpl': '00010000'})
        self.assertEqual(ac.registry, {'9093': {'0057'}})

        # ignore file
        self.assertEqual(ac.read_counters('ip.imp'), None)

    def test_ut_check_print(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        ac = AutoCounter(tpobj)
        with CaptureStdoutLog() as p:
            ac.check_print(' oldline', 'newline ', 10, '/a/b/newfile', False)
            ac.check_print(' oldline', 'newline ', 101, '/a/b/newfile', False)
            ac.check_print('oldline', 'oldline ', 10, '/a/b/newfile', False)  # should not print
            ac.check_print(' oldline', 'newline ', 1, '/a/c/newfile2', True)
        expect = '''
File: b/newfile
   line#10: oldline
   update : newline
   line#101: oldline
   update  : newline

File: c/newfile2
   line#1: oldline
   append: newline
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_ut_process(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        fname = 'a.mtpl'

        ac = AutoCounter(tpobj)
        ac.counter_block = {fname: 3}
        ac.first_dig8 = {fname: '90202079'}
        ac.counter_block_missing = {fname}
        ac.nocounter[fname] = [('ATOM_LSA_SRH_F5', '0', None, False, 40),
                               ('ATOM_LSA_SRH_F6', '0', '90202079', False, 18),
                               ('ATOM_LSA_SRH_F6', '2', '90202079', False, 27)]

        # ===== case1: basic
        data = ac.process(fname)
        expect = '''
{18: 'n20790010_fail_ATOM_LSA_SRH_F6_0',
 27: 'n20790002_fail_ATOM_LSA_SRH_F6_2',
 40: 'n20790000_fail_ATOM_LSA_SRH_F5_0'}
'''
        self.assertTextEqual(pformat(data), expect)

        # ===== case2: all are exhaused for port 0
        ac.registry = {'2079': {f'{str(x).zfill(3)}0' for x in range(10000)}}
        data = ac.process(fname)

        expect = '''
{18: 'n20790002_fail_ATOM_LSA_SRH_F6_0',
 27: 'n20790012_fail_ATOM_LSA_SRH_F6_2',
 40: 'n20790001_fail_ATOM_LSA_SRH_F5_0'}
'''
        self.assertTextEqual(pformat(data), expect)

        # ===== case3: all are exhausted
        ac.registry = {'2079': {str(x).zfill(4) for x in range(10000)}}

        with self.assertRaisesRegex(ErrorInput, 'All counters are exhausted'):
            ac.process(fname)

        # ===== case4: othertp
        ac.registry = {'2079': {f'{str(x).zfill(3)}0' for x in range(10000)}}
        ac.othertp = {'20790002'}
        data = ac.process(fname)

        expect = '''
{18: 'n20790003_fail_ATOM_LSA_SRH_F6_0',
 27: 'n20790012_fail_ATOM_LSA_SRH_F6_2',
 40: 'n20790001_fail_ATOM_LSA_SRH_F5_0'}
'''
        self.assertTextEqual(pformat(data), expect)

    def test_ut_mtt_ctr(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        ac = AutoCounter(tpobj)

        # first add
        self.assertEqual(ac.new_mtt('3'), '0003')

        # 2nd algo
        ac.mtt_registry = {f'{x:03}0' for x in range(1000)}
        self.assertEqual(ac.new_mtt('0'), '0001')
        self.assertEqual(ac.new_mtt('0'), '0002')

        # all are exhausted
        ac.mtt_registry = {f'{x:04}' for x in range(10000)}
        with self.assertRaisesRegex(ErrorInput, 'counters are exhausted'):
            ac.new_mtt('0')

        # other tp - first part
        ac.mtt_registry = {f'{x:03}0' for x in range(700)}
        ac.othertp = {'10017000', '10017010'}
        self.assertEqual(ac.new_mtt('0'), '7020')

        # other tp - second part
        ac.mtt_registry = {f'{x:03}0' for x in range(1000)}
        ac.othertp = {'10010001', '10010002'}
        self.assertEqual(ac.new_mtt('0'), '0003')

    @with_(TempDir, chdir=True)
    def test_integ1(self):
        # Start to finish flow. No Counter block
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

Test PrimeFlowControlSetTestMethod SetFlowInfo_RF_F3_ATOMC_Flow4
{
    DomainName = "ATOMC";
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        # Two Softbins, Two counter add
        DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
                Result -1 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202080_fail_ARR_blah;
                        Return 0;
                }
        }
        # No softbin, One Counter add
        FlowItem ATOM_LSA_SRH_F5 ATOM_LSA_SRH_F5 {
                Result -1 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n90930057_fail;
                        Return 0;
                }
        }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        tpobj.envdir = '.'
        File(f'{tpobj.envdir}/InputFiles/enable_autocounter.txt').touch(mkdir=True)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            ac.main()
            self.assertGoldEqual('ut.mtpl', f'{UT_DIR_REPO}/misc_files/auto_counter.mtpl.gold2')

            # check mode - should not error out
            AutoCounter(tpobj, is_check=True).main()

            # check mode - error out, new file
            print('==== start of error out')
            File(fname).touch(text, newfile=True)
            with self.assertRaisesRegex(ErrorUser, '3 IncrementCounters need fixing'):
                AutoCounter(tpobj, is_check=True).main()

            # check mode - skipped
            File(f'{tpobj.envdir}/InputFiles/enable_autocounter.txt').unlink()
            res = AutoCounter(tpobj, is_check=True).main()
            self.assertEqual(res, -1)

    @with_(TempDir, chdir=True)
    def test_integ2(self):
        # Start to finish flow. With Counter block
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

Counters
{
        n20790002_fail_ATOM_LSA_SRH_F6_2
}

Test PrimeFlowControlSetTestMethod SetFlowInfo_RF_F3_ATOMC_Flow4
{
    DomainName = "ATOMC";
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        # Two Softbins, Two counter add
        DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
                Result -1 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202080_fail_ARR_blah;
                        Return 0;
                }
        }
        # No softbin, One Counter add
        FlowItem ATOM_LSA_SRH_F5 ATOM_LSA_SRH_F5 {
                Result -1 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0 {
                        Property PassFail = "Fail";
                        Return 0;
                }
                Result 1 {
                        Property PassFail = "Pass";
                        Return 1;
                }
                Result 2 {
                        Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n90930057_fail;
                        Return 0;
                }
        }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl', 'a.imp'])):
            ac.main()
        self.assertGoldEqual('ut.mtpl', f'{UT_DIR_REPO}/misc_files/auto_counter2.mtpl.gold2')

        # run again - There should be no change
        ac = AutoCounter(tpobj)
        flist = ['ut.mtpl', 'a.imp', 'POR_TP/Class_MTL_P28/ProgramFlowsTestPlan/ProgramFlows.mtpl']
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=flist)):
            ac.main()
        self.assertGoldEqual('ut.mtpl', f'{UT_DIR_REPO}/misc_files/auto_counter2.mtpl.gold2')

    def test_integ3_secondarytp(self):
        # Start to finish flow: secondary TP
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple5', name=True) as tdir1, \
                TempDir(startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True):
            # second tp first
            text = '''
TestPlan AA;

Counters
{
        n20790000_fail_ATOM_LSA_SRH_F6_0,
        n20790001_fail_ATOM_LSA_SRH_F6_1
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        DUTFlowItem ATOM_LSA_SRH_F6 AATOM_LSA_SRH_F6 {
                Result 0 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n20790000_fail_ATOM_LSA_SRH_F6_0;
                        Return 0;
                }
                Result 1 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n20790001_fail_ATOM_LSA_SRH_F6_1;
                        Return 1;
                }
        }
}
'''
            File(f'{tdir1}/Modules/aa/aa.mtpl').touch(text, newfile=True, mkdir=True)
            File(f'{tdir1}/Modules/bb/bb.mtpl').touch(text.replace('AA', 'BB'), newfile=True, mkdir=True)
            File(f'{tdir1}/POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').touch(r'''
SubTestPlans
{
        ..\..\Modules\aa\aa.mtpl;
        ..\..\Modules\bb\bb.mtpl;
        Final .\ProgramFlowsTestPlan\ProgramFlows.mtpl;
}
''', newfile=True)

            # primary tp next
            text = '''
TestPlan AA;

Counters
{
        n90930057_fail_xAA
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        DUTFlowItem ATOM_LSA_SRH_F6 AATOM_LSA_SRH_F6 {
                Result 0 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n90930057_fail_xAA;
                        Return 0;
                }
                Result 1 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n90930057_fail_xAA;
                        Return 1;
                }
        }
}
'''
            File('Modules/aa/aa.mtpl').touch(text, newfile=True, mkdir=True)
            File('Modules/bb/bb.mtpl').touch(text.replace('AA', 'BB'), newfile=True, mkdir=True)
            File(f'{tdir1}/POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').copy('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl')
            tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')

            # Standard no secondary TP
            ac = AutoCounter(tpobj)
            ac.main(['Modules/aa/aa.mtpl'])
            expect = '''
TestPlan AA;

Counters
{
        n20790000_fail_ATOM_LSA_SRH_F6_0,
        n20790001_fail_ATOM_LSA_SRH_F6_1
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        DUTFlowItem ATOM_LSA_SRH_F6 AATOM_LSA_SRH_F6 {
                Result 0 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n20790000_fail_ATOM_LSA_SRH_F6_0;
                        Return 0;
                }
                Result 1 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n20790001_fail_ATOM_LSA_SRH_F6_1;
                        Return 1;
                }
        }
}
'''
            self.assertTextEqual(File('Modules/aa/aa.mtpl').read(), expect)

            # Secondary TP
            File('Modules/aa/aa.mtpl').touch(text, newfile=True, mkdir=True)
            ac = AutoCounter(tpobj)
            ac.main(['Modules/aa/aa.mtpl'], [f'{tdir1}/POR_TP/TGLH81/EnvironmentFile.env'])
            expect = '''
TestPlan AA;

Counters
{
        n20790010_fail_ATOM_LSA_SRH_F6_0,
        n20790011_fail_ATOM_LSA_SRH_F6_1
}

DUTFlow ARR_ATOM_CXX_SATF6 {
        DUTFlowItem ATOM_LSA_SRH_F6 AATOM_LSA_SRH_F6 {
                Result 0 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n20790010_fail_ATOM_LSA_SRH_F6_0;
                        Return 0;
                }
                Result 1 {
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        IncrementCounters AA::n20790011_fail_ATOM_LSA_SRH_F6_1;
                        Return 1;
                }
        }
}
'''
            self.assertTextEqual(File('Modules/aa/aa.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_singleline(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -2 { Property PassFail = "Fail"; Return -2; }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            res = ac.main(mtplfiles=['ut.mtpl'])
        self.assertEqual(res, (1, 1))

        expect = '''
TestPlan TPI_DIESLCT_XXX;
Counters
{
        n00000002_fail_ATOM_LSA_SRH_F6_m2
}

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -2 { Property PassFail = "Fail"; IncrementCounters TPI_DIESLCT_XXX::n00000002_fail_ATOM_LSA_SRH_F6_m2; Return -2; }
    }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_onefile(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -2 { Property PassFail = "Fail"; Return -2; }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            res = ac.main(mtplfiles=['ut1.mtpl'])    # incorrect specified file
        self.assertEqual(res, (0, 1))
        self.assertTextEqual(File('ut.mtpl').read(), text)

    @with_(TempDir, chdir=True)
    def test_invalid(self):
        # good template
        # This testcase include duplicated IncrementCounters line
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -3 {
            Property PassFail = "Fail";
            IncrementCounters TPI_DIESLCT_XXX::n0000002_fail_ATOM_LSA_SRH_F6_m2;
            IncrementCounters TPI_DIESLCT_XXX::n00000006_fail_ATOM_LSA_SRH_F6_m3;    # should be ignored, duplicate
        }
        Result -4 {
            Property PassFail = "Fail";
            IncrementCounters TPI_DIESLCT_XXX::fail_ATOM_LSA_SRH_F6_m2;
        }
        Result -5 {
            Property PassFail = "Pass";
            IncrementCounters TPI_DIESLCT_XXX::x;
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            ac.main()

        expect = '''
TestPlan TPI_DIESLCT_XXX;
Counters
{
        n00000003_fail_ATOM_LSA_SRH_F6_m3,
        n00000004_fail_ATOM_LSA_SRH_F6_m4,
        p99000005_pass_ATOM_LSA_SRH_F6_m5
}

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -3 {
            Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n00000003_fail_ATOM_LSA_SRH_F6_m3;


        }
        Result -4 {
            Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n00000004_fail_ATOM_LSA_SRH_F6_m4;

        }
        Result -5 {
            Property PassFail = "Pass";
                        IncrementCounters TPI_DIESLCT_XXX::p99000005_pass_ATOM_LSA_SRH_F6_m5;

        }
    }
}

'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_composite(self):
        # This testcase tests composites
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ARR_ATOM_CXX_SATF6 {
        Result 3 {
            Property PassFail = "Fail";GoTo FBIST_D2D_CMEM_E_BEGCPUPKG_X_X_VMAX_DIAG_S2C_ALL_CC;
        }
        Result 4 {
            Property PassFail = "Fail";Return 1;
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            ac.main()
        self.assertTextEqual(File('ut.mtpl').read(), text)   # no change

    @with_(TempDir, chdir=True)
    def test_sameline(self):
        # This testcase has property and goto on same line
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result 3 {
            Property PassFail = "Fail";GoTo FBIST_D2D_CMEM_E_BEGCPUPKG_X_X_VMAX_DIAG_S2C_ALL_CC;
        }
        Result 4 {
            Property PassFail = "Fail";Return 1;
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            ac.main()

        expect = '''
TestPlan TPI_DIESLCT_XXX;
Counters
{
        n00000003_fail_ATOM_LSA_SRH_F6_3,
        n00000004_fail_ATOM_LSA_SRH_F6_4
}

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result 3 {
            Property PassFail = "Fail"; IncrementCounters TPI_DIESLCT_XXX::n00000003_fail_ATOM_LSA_SRH_F6_3; GoTo FBIST_D2D_CMEM_E_BEGCPUPKG_X_X_VMAX_DIAG_S2C_ALL_CC;
        }
        Result 4 {
            Property PassFail = "Fail"; IncrementCounters TPI_DIESLCT_XXX::n00000004_fail_ATOM_LSA_SRH_F6_4; Return 1;
        }
    }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_noctr(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -3 {
            Property PassFail = "Fail";
            # No IncrementCounters blah
        }
        Result -4 {
            # Other comment
            Property PassFail = "Fail";
        }
        Result -5 {
            Property PassFail = "Pass";
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            ac.main()

        expect = '''
TestPlan TPI_DIESLCT_XXX;
Counters
{
        n00000004_fail_ATOM_LSA_SRH_F6_m4
}

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -3 {
            Property PassFail = "Fail";
            # No IncrementCounters blah
        }
        Result -4 {
            # Other comment
            Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n00000004_fail_ATOM_LSA_SRH_F6_m4;
        }
        Result -5 {
            Property PassFail = "Pass";
        }
    }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_duplicate(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -3 {
            Property PassFail = "Fail";
            IncrementCounters TPI_DIESLCT_XXX::n00000002_fail_ATOM_LSA_SRH_F6_m2;
        }
        Result -4 {
            Property PassFail = "Fail";
            IncrementCounters TPI_DIESLCT_XXX::n00000002_fail_ATOM_LSA_SRH_F6_m2;
        }
        Result -5 {
            Property PassFail = "Fail";
            IncrementCounters TPI_DIESLCT_XXX::n00000006_fail_ATOM_LSA_SRH_F6_m2;
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            ac.main()

        expect = '''
TestPlan TPI_DIESLCT_XXX;
Counters
{
        n00000003_fail_ATOM_LSA_SRH_F6_m3,
        n00000004_fail_ATOM_LSA_SRH_F6_m4,
        n00000006_fail_ATOM_LSA_SRH_F6_m2
}

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result -3 {
            Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n00000003_fail_ATOM_LSA_SRH_F6_m3;
        }
        Result -4 {
            Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n00000004_fail_ATOM_LSA_SRH_F6_m4;
        }
        Result -5 {
            Property PassFail = "Fail";
            IncrementCounters TPI_DIESLCT_XXX::n00000006_fail_ATOM_LSA_SRH_F6_m2;
        }
    }
}

'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_duplicate_pass(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan TPI_DIESLCT_XXX;

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result 0 {
            Property PassFail = "Fail";
            IncrementCounters TPI_DIESLCT_XXX::n00000002_fail_ATOM_LSA_SRH_F6_m2;
            SetBin SoftBins.b90202079_fail_ARR_blah;
        }
        Result -3 {
            Property PassFail = "Pass";
            IncrementCounters TPI_DIESLCT_XXX::n00000002_fail_ATOM_LSA_SRH_F6_m2;
        }
        Result -4 {
            Property PassFail = "Pass";
            IncrementCounters TPI_DIESLCT_XXX::n00000002_fail_ATOM_LSA_SRH_F6_m2;
            SetBin SoftBins.b90202079_fail_ARR_blah;
        }
        Result -5 {
            Property PassFail = "Pass";
            IncrementCounters TPI_DIESLCT_XXX::n00000006_fail_ATOM_LSA_SRH_F6_m2;
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            ac.main()

        expect = '''
TestPlan TPI_DIESLCT_XXX;
Counters
{
        n00000006_fail_ATOM_LSA_SRH_F6_m2,
        n20790000_fail_ATOM_LSA_SRH_F6_0,
        p99200003_pass_ATOM_LSA_SRH_F6_m3,
        p99200004_pass_ATOM_LSA_SRH_F6_m4
}

DUTFlow ARR_ATOM_CXX_SATF6 {
    DUTFlowItem ATOM_LSA_SRH_F6 ATOM_LSA_SRH_F6 {
        Result 0 {
            Property PassFail = "Fail";
                        IncrementCounters TPI_DIESLCT_XXX::n20790000_fail_ATOM_LSA_SRH_F6_0;
            SetBin SoftBins.b90202079_fail_ARR_blah;
        }
        Result -3 {
            Property PassFail = "Pass";
                        IncrementCounters TPI_DIESLCT_XXX::p99200003_pass_ATOM_LSA_SRH_F6_m3;
        }
        Result -4 {
            Property PassFail = "Pass";
                        IncrementCounters TPI_DIESLCT_XXX::p99200004_pass_ATOM_LSA_SRH_F6_m4;
            SetBin SoftBins.b90202079_fail_ARR_blah;
        }
        Result -5 {
            Property PassFail = "Pass";
            IncrementCounters TPI_DIESLCT_XXX::n00000006_fail_ATOM_LSA_SRH_F6_m2;
        }
    }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_mtt_basic(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan ARR_ATOM_CXX;

Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" {
        TrialResult -2 { PassFail Fail; TrialAction Exit; }
        TrialResult 0 { PassFail Fail; TrialAction Exit; }
        TrialResult 1 { PassFail Pass; }
        TrialResult 2 {
            PassFail Fail;
            TrialAction Exit;
            SetBin "SoftBins.b" + BinMatrix.bin + "2052_fail_ARR_ATOM_CXX_CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_0400_RF";
        }
        TrialResult 3 {
            PassFail Fail;
            TrialAction Exit;
            IncrementCounters "FUN_ATOM_CXX::n" + BinMatrix.bin + "0515_fail_xyz";
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            res = ac.main()
        self.assertEqual(res, (1, 2))

        expect = '''
TestPlan ARR_ATOM_CXX;
Counters
{
        n10010000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n10010002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n10010515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n10020000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n10020002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n10020515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n10030000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n10030002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n10030515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n15010000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15010002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n15010515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n15020000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15020002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n15020515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n15030000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15030002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n15030515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n15040000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15040002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n15040515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n15050000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15050002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n15050515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n15060000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15060002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n15060515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3,
        n15070000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15070002_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_2,
        n15070515_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_3
}

Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" {
        TrialResult -2 { PassFail Fail; TrialAction Exit; }
        TrialResult 0 { PassFail Fail; TrialAction Exit; IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0000_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_0"; }
        TrialResult 1 { PassFail Pass; }
        TrialResult 2 {
            PassFail Fail;
            TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0002_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_2";
            SetBin "SoftBins.b" + BinMatrix.bin + "2052_fail_ARR_ATOM_CXX_CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_0400_RF";
        }
        TrialResult 3 {
            PassFail Fail;
            TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0515_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_3";
        }
    }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_mtt_negport(self):
        # Negative port with IncrementCounter must be processed
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan ARR_ATOM_CXX;

Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" {
        TrialResult -2 {
            PassFail Fail;
            TrialAction Exit;
            IncrementCounters "SoftBins.b" + BinMatrix.bin + "0001_fail_blah";
         }
        TrialResult 0 { PassFail Fail; TrialAction Exit; }
        TrialResult 1 { PassFail Pass; }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])):
            res = ac.main()
        self.assertEqual(res, (1, 1))

        expect = '''
TestPlan ARR_ATOM_CXX;
Counters
{
        n10010000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n10010001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n10020000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n10020001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n10030000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n10030001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n15010000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15010001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n15020000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15020001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n15030000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15030001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n15040000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15040001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n15050000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15050001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n15060000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15060001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2,
        n15070000_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_0,
        n15070001_fail_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_m2
}

Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" {
        TrialResult -2 {
            PassFail Fail;
            TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0001_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_m2";
         }
        TrialResult 0 { PassFail Fail; TrialAction Exit; IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0000_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_0"; }
        TrialResult 1 { PassFail Pass; }
    }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_mtt_dup(self):
        # Duplicate case, must replace
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan ARR_ATOM_CXX;

Counters
{
        n10010000_fail_ARR_ATOM_CXX_SATF6_0,
        n10020000_fail_ARR_ATOM_CXX_SATF6_0
}
Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" {
        TrialResult 0 {
            PassFail Fail;
            TrialAction Exit;
        }
        TrialResult 1 { PassFail Pass; }
        TrialResult 2 {
            PassFail Fail;
            TrialAction Exit;
            IncrementCounters "FUN_ATOM_CXX::n" + BinMatrix.bin + "0002_fail";
        }
        TrialResult 3 {
            PassFail Fail;
            TrialAction Exit;
            IncrementCounters "FUN_ATOM_CXX::n" + BinMatrix.bin + "0002_fail";
        }
    }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)

        def fake(slf, item):
            return [f'SetBin {item}']

        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])), \
                MockVar(BM, 'expand', fake):
            res = ac.main()
        self.assertEqual(res, (1, 3))

        expect = '''
TestPlan ARR_ATOM_CXX;

Counters
{
        n" + BinMatrix.bin + "0000_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_0",
        n" + BinMatrix.bin + "0003_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_3",
        n" + BinMatrix.bin + "0012_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_2"
}
Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" {
        TrialResult 0 {
            PassFail Fail;
            TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0000_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_0";
        }
        TrialResult 1 { PassFail Pass; }
        TrialResult 2 {
            PassFail Fail;
            TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0012_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_2";
        }
        TrialResult 3 {
            PassFail Fail;
            TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + BinMatrix.bin + "0003_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1" + "_3";
        }
    }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_mtt_dfi(self):
        # Do not add counter on MTT instance
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        text = '''
TestPlan ARR_ATOM_CXX;

Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_" {
        TrialResult 0 {
            PassFail Fail;
            TrialAction Exit;
        }
    }
}
DUTFlow ARR_ATOM_CXX_S {
        DUTFlowItem ARR_ATOM_CXX_SATF6 ARR_ATOM_CXX_SATF6 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
         }
        DUTFlowItem A A {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
         }
        DUTFlowItem ARR_ATOM_CXX_SATF5 ARR_ATOM_CXX_SATF6 {
                Result 0 {
                        Property PassFail = "Fail";
                        IncrementCounters ARR_ATOM_CXX::n20790009_fail_A_1;
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
         }
}
'''
        fname = 'ut.mtpl'
        File(fname).touch(text)

        def fake(slf, item):
            return [f'SetBin {item}']

        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=['ut.mtpl'])), \
                MockVar(BM, 'expand', fake):
            res = ac.main()
        self.assertEqual(res, (1, 2))

        expect = '''
TestPlan ARR_ATOM_CXX;
Counters
{
        n" + FlowMatrix.bin + "0000_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_" + "_0",
        n20790000_fail_A_0
}

Test A A { }
MultiTrialTest ARR_ATOM_CXX_SATF6 {
    TrialTest VminTC "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_" {
        TrialResult 0 {
            PassFail Fail;
            TrialAction Exit;
                        IncrementCounters "ARR_ATOM_CXX::n" + FlowMatrix.bin + "0000_fail_" + "SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_" + "_0";
        }
    }
}
DUTFlow ARR_ATOM_CXX_S {
        DUTFlowItem ARR_ATOM_CXX_SATF6 ARR_ATOM_CXX_SATF6 {
                Result 0 {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
         }
        DUTFlowItem A A {
                Result 0 {
                        Property PassFail = "Fail";
                        IncrementCounters ARR_ATOM_CXX::n20790000_fail_A_0;
                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
         }
        DUTFlowItem ARR_ATOM_CXX_SATF5 ARR_ATOM_CXX_SATF6 {
                Result 0 {
                        Property PassFail = "Fail";

                        SetBin SoftBins.b90202079_fail_ARR_blah;
                        Return 0;
                }
         }
}
'''
        self.assertTextEqual(File('ut.mtpl').read(), expect)

    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @with_(TempDir, chdir=True, delete=True)
    def test_mtt_real(self):
        # adhoc run only, given specific .mtpl
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        fname = 'arr_atom_cxx_auto_counter.mtpl'
        File(f'{UT_DIR_REPO}/misc_files/{fname}').copy('.')
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=[fname])):
            res = ac.main()
        self.assertEqual(res, (1, 424))
        self.assertGoldEqual(fname, f'{UT_DIR_REPO}/misc_files/{fname}.gold4')

        # rerun - should be no change
        ac = AutoCounter(tpobj)
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=[fname])):
            res = ac.main()
        self.assertEqual(res, (0, 0))
        self.assertGoldEqual(fname, f'{UT_DIR_REPO}/misc_files/{fname}.gold4')   # no change

    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/MTLXXXXXXX39A0KSXXX', chdir=True)
    def test_fulltp(self):
        # This unittest is to check the entire TP that it works ok
        # checks for counters updated and number of files
        # Makes sure that rerun would be zero changes
        tpobj = TestProgram(f'POR_TP/Class_MTL_P28/EnvironmentFile.env')
        ac = AutoCounter(tpobj)
        res = ac.main()
        self.assertEqual(res, (168, 49486))

        # rerun - should be zero
        tpobj = TestProgram(f'POR_TP/Class_MTL_P28/EnvironmentFile.env')
        ac = AutoCounter(tpobj)
        res = ac.main()
        self.assertEqual(res, (0, 0))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()


# Validation prior to release:
# 1. Run autocounter.py (assuming clean branch) -> there should be no updates
# 2. Remove one IncrementCounter line -> It should update one file only (it should add counter)
# 3. Put two same counters in two different files -> It should update both files
# 4. Put two same counters in two different files but specify mtpl in commandline -> It should update one file only
# 5. Add a "# No IncrementCounters" -> It should not add counter
