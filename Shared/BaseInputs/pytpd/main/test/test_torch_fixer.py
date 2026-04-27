#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for torch_fixer.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from main.torch_fixer import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.disk import Chdir
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from gadget.dictmore import keys_atlevel
from gadget.shell import SystemCall
from gadget.printmore import Dumper
from tp.testprogram import Env
from unittest.mock import Mock
from os.path import join
import sys
import shutil


class TestCompLink(TestCase):

    @with_(TempDir, chdir=True, delete=True)
    def test_case_basic_rerun(self):
        text = '''Version 1.0;

Test method test_t1 {
    patlist = "abc";
    # LINK:two:patlist = "ghi";
}
DUTFlow IOE {
   DUTFlowItem test_t1 test_t1
       { blah; }
}
DUTFlow PTH_POWER_IXX_END {
   DUTFlowItem NEW_LINK IOE
       # find:t1 replace:1:t2
       # linkname: two
       { line NEW_LINK; }
}
'''
        File('PWR_LINK/src_a.mtpl').touch(text, mkdir=True)

        mkdirs('PWR')
        CompLink('PWR_LINK/src_a.mtpl').main()
        expect = '''Version 1.0;

Test method test_t1 {
    patlist = "abc";
    # LINK:two:patlist = "ghi";
}
Test method test_t2 {
    patlist = "ghi";
    # LINK:two:patlist = "ghi";
}
DUTFlow IOE {
   DUTFlowItem test_t1 test_t1
       { blah; }
}
DUTFlow IOE_two {
   DUTFlowItem test_t2 test_t2
       { blah; }
}
DUTFlow PTH_POWER_IXX_END {
    DUTFlowItem NEW_LINK IOE_two
       # find:t1 replace:1:t2
    # status: DONE
       # linkname: two
       { line NEW_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

        # rerun should be ok
        cl = CompLink('PWR_LINK/src_a.mtpl')
        cl.main()
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)
        self.assertEqual(MtplEdit(cl.mb).update_counters(), 1)   # no change

        # someone changed output (checks .orig.txt logic)
        File('PWR/a.mtpl').touch('modified')
        with self.assertRaisesRegex(ErrorUser, 'first before overwriting'):
            CompLink('PWR_LINK/src_a.mtpl').main()

        # method 2 output
        File('PWRX/a.mtpl').touch(text, mkdir=True)
        mkdirs('PWRX')
        cmd = f"torch_fixer.py PWRX/a.mtpl -link"
        with MockVar(sys, "argv", cmd.split()):
            Fixer().main()
        self.assertTextEqual(File('PWRX/a.mtpl').read(), expect)

        # rerun - should be ok
        CompLink('PWRX/a.mtpl').main()
        self.assertTextEqual(File('PWRX/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_subflowname(self):
        # This test subflowname
        # This test change to a comment and remove a comment
        text = r'''
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow SRC {
   DUTFlowItem AA_SDS AA_SDS
   {
       GoTo A;
       # uncomment:GoTo B;
   }
}
DUTFlow SOME_SDS {
   DUTFlowItem SRC SRC
   {}
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE_LINK SRC @EDC
       # find:SDS replace:1:SDT
       # find:(GoTo A;) replace:-1:# $1
       # find:# uncomment: replace:1:NONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        CompLink('PWR/a.mtpl').main()
        expect = r'''
Test method AA_SDS {
    patlist = "abc";
}
Test method AA_SDT {
    patlist = "abc";
}
DUTFlow SRC {
   DUTFlowItem AA_SDS AA_SDS
   {
       GoTo A;
       # uncomment:GoTo B;
   }
}
DUTFlow SOME_SDS {
   DUTFlowItem SRC SRC
   {}
}
DUTFlow SRC_SDT {
   DUTFlowItem AA_SDT AA_SDT
   {
       # GoTo A;
       GoTo B;
   }
}
DUTFlow SOME_SDT {
    DUTFlowItem ONE_LINK SRC_SDT @EDC
       # find:SDS replace:1:SDT
       # find:(GoTo A;) replace:-1:# $1
       # find:# uncomment: replace:1:NONE
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_regname(self):   # good template to use
        # Test regexname
        text = r'''
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow SRC {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   }
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE_LINK SRC @EDC @A
       # find:(\w+)_(SDS) replace:-1:$1_SDT
       # find:SetBin d(\w+); replace:1:NONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        CompLink('PWR/a.mtpl').main()
        expect = r'''
Test method AA_SDS {
    patlist = "abc";
}
Test method AA_SDT {
    patlist = "abc";
}
DUTFlow SRC {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   }
}
DUTFlow SRC_SDT {
   DUTFlowItem X_AA_SDT AA_SDT
   {
   SetBin d;
   }
}
DUTFlow SOME_SDT {
    DUTFlowItem ONE_LINK SRC_SDT @EDC @A
       # find:(\w+)_(SDS) replace:-1:$1_SDT
       # find:SetBin d(\w+); replace:1:NONE
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_dutflow_option(self):
        # Test dutflow option
        text = r'''
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow SRC {

   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;

   # LINK:SDT:SetBin d002;
   # LINK:SDX:SetBin d003;
   }
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE_LINK SRC
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        CompLink('PWR/a.mtpl').main()
        expect = r'''
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow SRC {

   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;

   # LINK:SDT:SetBin d002;
   # LINK:SDX:SetBin d003;
   }
}
DUTFlow SRC_SDT {

   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d002;

   # LINK:SDT:SetBin d002;
   # LINK:SDX:SetBin d003;
   }
}
DUTFlow SOME_SDT {
    DUTFlowItem ONE_LINK SRC_SDT
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_rename_two(self):
        # This test instance auto-rename and two links
        text = '''
Test method AA {
    patlist = "abc";
    # LINK:CORE1:patlist = "def";
    # LINK:CORE2:patlist = "ghi";
}
Test method BB { }
DUTFlow SRC {
   DUTFlowItem BB BB { GoTo AA; }
   DUTFlowItem AA AA
       { GoTo ZAA; }
}
DUTFlow PTH_POWER_IXX_END {
   DUTFlowItem ONE_LINK SRC
       # find:CORE0 replace:1:CORE1
       # linkname: CORE1
       { line ONE_LINK; }
}
DUTFlow PTH_POWER_IXX_BEGIN {
   DUTFlowItem TWO_LINK SRC
       # find:CORE0 replace:1:CORE2
       # linkname: CORE2
       { line TWO_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        CompLink('PWR/a.mtpl').main()

        expect = '''
Test method AA {
    patlist = "abc";
    # LINK:CORE1:patlist = "def";
    # LINK:CORE2:patlist = "ghi";
}
Test method AA_0 {
    patlist = "def";
    # LINK:CORE1:patlist = "def";
    # LINK:CORE2:patlist = "ghi";
}
Test method AA_1 {
    patlist = "ghi";
    # LINK:CORE1:patlist = "def";
    # LINK:CORE2:patlist = "ghi";
}
Test method BB { }
DUTFlow SRC {
   DUTFlowItem BB BB { GoTo AA; }
   DUTFlowItem AA AA
       { GoTo ZAA; }
}
DUTFlow SRC_CORE1 {
   DUTFlowItem BB BB { GoTo AA_0; }
   DUTFlowItem AA_0 AA_0
       { GoTo ZAA; }
}
DUTFlow PTH_POWER_IXX_END {
    DUTFlowItem ONE_LINK SRC_CORE1
       # find:CORE0 replace:1:CORE1
    # status: DONE
       # linkname: CORE1
       { line ONE_LINK; }
}
DUTFlow SRC_CORE2 {
   DUTFlowItem BB BB { GoTo AA_1; }
   DUTFlowItem AA_1 AA_1
       { GoTo ZAA; }
}
DUTFlow PTH_POWER_IXX_BEGIN {
    DUTFlowItem TWO_LINK SRC_CORE2
       # find:CORE0 replace:1:CORE2
    # status: DONE
       # linkname: CORE2
       { line TWO_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_copy(self):
        # SRC composite name replace
        text = '''
Test method AA_CORE0 {
    patlist = "abc";
}
DUTFlow SRC_CORE0 {
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
   DUTFlowItem SRC_CORE1_LINK SRC_CORE0
       # find:CORE0 replace:1:CORE1
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        cl = CompLink('PWR/a.mtpl')
        cl.main()
        expect = '''
Test method AA_CORE0 {
    patlist = "abc";
}
Test method AA_CORE1 {
    patlist = "abc";
}
DUTFlow SRC_CORE0 {
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow SRC_CORE1 {
   DUTFlowItem AA_CORE1 AA_CORE1
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
    DUTFlowItem SRC_CORE1_LINK SRC_CORE1
       # find:CORE0 replace:1:CORE1
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)
        self.assertEqual([x[0] for x in cl.find_comp_links()], ['DUTFlowItem SRC_CORE1_LINK SRC_CORE0'])

    @with_(TempDir, chdir=True, delete=True)
    def test_case_copy2(self):
        # SRC composite name replace, replace name is at middle of string
        text = '''
Test method AA_CORE0 {
    patlist = "abc";
}
DUTFlow SRC_CORE0_A @BEG_Subflow
{
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
   DUTFlowItem SRC_CORE1_LINK SRC_CORE0_A
       # find:CORE0 replace:1:CORE1
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        cl = CompLink('PWR/a.mtpl')
        cl.main()
        expect = '''
Test method AA_CORE0 {
    patlist = "abc";
}
Test method AA_CORE1 {
    patlist = "abc";
}
DUTFlow SRC_CORE0_A @BEG_Subflow
{
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow SRC_CORE1_A @BEG_Subflow
{
   DUTFlowItem AA_CORE1 AA_CORE1
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
    DUTFlowItem SRC_CORE1_LINK SRC_CORE1_A
       # find:CORE0 replace:1:CORE1
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_dutflowrename(self):
        # composite (DUTFlow) got changed inside, auto rename
        text = '''
Test method TT_CORE0 {
    patlist = "abc_SDS_go";
}
DUTFlow AA_CORE0 {
   DUTFlowItem TT_CORE0 TT_CORE0
       { blah; }
}
DUTFlow SRC_CORE0
{
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
   DUTFlowItem SRC_SDT_LINK SRC_CORE0
       # find:SDS replace:1:SDT
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        cl = CompLink('PWR/a.mtpl')
        cl.main()
        expect = '''
Test method TT_CORE0 {
    patlist = "abc_SDS_go";
}
Test method TT_CORE0_0 {
    patlist = "abc_SDT_go";
}
DUTFlow AA_CORE0 {
   DUTFlowItem TT_CORE0 TT_CORE0
       { blah; }
}
DUTFlow AA_CORE0_0 {
   DUTFlowItem TT_CORE0_0 TT_CORE0_0
       { blah; }
}
DUTFlow SRC_CORE0
{
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow SRC_CORE0_SDT
{
   DUTFlowItem AA_CORE0_0 AA_CORE0_0
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
    DUTFlowItem SRC_SDT_LINK SRC_CORE0_SDT
       # find:SDS replace:1:SDT
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_twolink(self):
        # composite (DUTFlow) got changed inside, two links
        text = '''
Test method TT_CORE0 {
    patlist = "abc_SDS_go";
}
DUTFlow AA_CORE0 {
   DUTFlowItem TT_CORE0 TT_CORE0
       { blah; }
}
DUTFlow SRC_CORE0
{
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
   DUTFlowItem SRC_SDT_LINK SRC_CORE0
       # find:SDS replace:1:SDT
       # linkname: SDT
       { line ONE_LINK; }
   DUTFlowItem SRC_SDJ_LINK SRC_CORE0
       # find:SDS replace:1:SDJ
       # linkname: SDJ
       { line ONE_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        cl = CompLink('PWR/a.mtpl')
        cl.main()
        expect = '''
Test method TT_CORE0 {
    patlist = "abc_SDS_go";
}
Test method TT_CORE0_0 {
    patlist = "abc_SDT_go";
}
Test method TT_CORE0_1 {
    patlist = "abc_SDJ_go";
}
DUTFlow AA_CORE0 {
   DUTFlowItem TT_CORE0 TT_CORE0
       { blah; }
}
DUTFlow AA_CORE0_0 {
   DUTFlowItem TT_CORE0_0 TT_CORE0_0
       { blah; }
}
DUTFlow SRC_CORE0
{
   DUTFlowItem AA_CORE0 AA_CORE0
       { blah; }
}
DUTFlow AA_CORE0_1 {
   DUTFlowItem TT_CORE0_1 TT_CORE0_1
       { blah; }
}
DUTFlow SRC_CORE0_SDT
{
   DUTFlowItem AA_CORE0_0 AA_CORE0_0
       { blah; }
}
DUTFlow SRC_CORE0_SDJ
{
   DUTFlowItem AA_CORE0_1 AA_CORE0_1
       { blah; }
}
DUTFlow SOME_flow {
   DUTFlowItem SRC_CORE0 SRC_CORE0
   {
   line;
   }
    DUTFlowItem SRC_SDT_LINK SRC_CORE0_SDT
       # find:SDS replace:1:SDT
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
    DUTFlowItem SRC_SDJ_LINK SRC_CORE0_SDJ
       # find:SDS replace:1:SDJ
    # status: DONE
       # linkname: SDJ
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('PWR/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_case_nolink(self):
        # generic test without any linking
        text = '''Version 1.0;

Test method test_t1 {
    patlist = "abc";
    # LINK:two:patlist = "ghi";
}
DUTFlow IOE {
   DUTFlowItem test_t1 test_t1
       { blah; }
}
DUTFlow PTH_POWER_IXX_END {
   DUTFlowItem NEW IOE
       { line NEW_LINK; }
}
'''
        File('PWR/a.mtpl').touch(text, mkdir=True)

        CompLink('PWR/a.mtpl').main()
        self.assertTextEqual(File('PWR/a.mtpl').read(), text)   # No change
        self.assertEqual(os.listdir('PWR'), ['a.mtpl'])    # no added files

    @with_(TempDir, chdir=True)
    def test_destination(self):
        File('PWR_LINK/a.mtpl').touch(mkdir=True)
        File('PWR_SRC/src_a.mtpl').touch(mkdir=True)
        File('PWR_SRC/a.mtpl').touch(mkdir=True)
        File('PWR/a.flw').touch(mkdir=True)

        # different directory - preprocess
        self.assertEqual(Env.xpath(CompLink('PWR_SRC/a.mtpl').destination()), Env.xpath(abspath('PWR/a.mtpl')))
        self.assertEqual(Env.xpath(CompLink('PWR_SRC/src_a.mtpl').destination()), Env.xpath(abspath('PWR/a.mtpl')))
        self.assertEqual(Env.xpath(CompLink('PWR_LINK/a.mtpl').destination()), Env.xpath(abspath('PWR/a.mtpl')))
        self.assertEqual(set(os.listdir('PWR')), {'a.flw'})

        # same directory - one time
        File('PWR/a.mtpl').touch(mkdir=True)
        self.assertEqual(CompLink('PWR/a.mtpl').destination(), 'PWR/a.mtpl')
        self.assertEqual(set(os.listdir('PWR')), {'a.mtpl', 'a.flw'})

    @with_(TempDir, chdir=True)
    def test_instance_options(self):
        text = '''Test method abc
{
    patlist = "abc";
    # LINK:END:patlist = "def";
    # LINK:STR:patlist = "ghi";
    bypass = 1;
    # LINK:END:bypass = 0;
    # LINK:STR:bypass = -1;
}
'''
        File('a.mtpl').touch(text)
        cl = CompLink('a.mtpl')
        text2 = '''DUTFlow f1
{
    patlist = "abc";
    # LINK:END:patlist = "def";
    # LINK:STR:patlist = "ghi";
}
'''
        result = {'abc': [f'{x}\n' for x in text.split('\n')],
                  'f1': [f'{x}\n' for x in text2.split('\n')]}
        cl.instance_options(result, 'END')
        expect = '''Test method abc
{
    patlist = "def";
    # LINK:END:patlist = "def";
    # LINK:STR:patlist = "ghi";
    bypass = 0;
    # LINK:END:bypass = 0;
    # LINK:STR:bypass = -1;
}

'''
        self.assertTextEqual(''.join(result['abc']), expect)
        self.assertTextEqual(''.join(result['f1']), text2 + '\n')   # No change

        # not found case
        text = '''Test method abc
{
    patlist= "abc";
    # LINK:END:patlist = "def";
    # LINK:STR:patlist = "ghi";
    bypass = 1;
    # LINK:END:bypass = 0;
    # LINK:STR:bypass = -1;
}
'''
        result = {'abc': [f'{x}\n' for x in text.split('\n')]}
        with self.assertRaisesRegex(ErrorUser, 'must be defined'):
            cl.instance_options(result, 'END')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_config_info(self):
        cl = CompLink(f'{UT_DIR}/compositelink/PTH_POWER_IXX.mtpl')
        self.assertEqual(cl.get_config_info('NEW_LINK', 'blah'),
                         {'find': [{'search': 'BEGIOEPKG', 'group': 1, 'replace': 'ZZZ'}],
                          'linkname': 'QQQ',
                          'status': None})

        # multi-find
        with TempDir(name=True, chdir=True):
            File('a.mtpl').touch(r'''
DUTFlow blah {
   DUTFlowItem NEW_LINK IOE
   # find:BEGIOEPKG replace:1:IXX_END
   # find:END replace:2:IXX
   # linkname:IXX
        {
        }
   DUTFlowItem OLD_LINK IOF
   #  find:BEGIOEPKGX replace:1:IXX_ENDX
   # find:something replace:1:NONE
   # find:GoTo A replace:-1:# $1
   #  linkname:YXX
        {
        }
}
''')
            cl = CompLink('a.mtpl')
            res = cl.get_config_info('NEW_LINK', 'blah')
            self.assertEqual(res, {'find': [{'group': 1, 'replace': 'IXX_END', 'search': 'BEGIOEPKG'},
                                            {'group': 2, 'replace': 'IXX', 'search': 'END'}],
                                   'linkname': 'IXX',
                                   'status': None})

            res = cl.get_config_info('OLD_LINK', 'blah')
            self.assertEqual(res, {'find': [{'group': 1, 'replace': 'IXX_ENDX', 'search': 'BEGIOEPKGX'},
                                            {'group': 1, 'replace': '', 'search': 'something'},
                                            {'group': -1, 'replace': '# \\1', 'search': 'GoTo A'}],
                                   'linkname': 'YXX',
                                   'status': None})

    @with_(TempDir, chdir=True)
    def test_replace(self):
        text = '''Test iCScreenTest POWER_X_SCREEN_E_ENDIOEPKG_X_X_X_X_PORTPCALC
{
        screen_custom_file = "./Modules/PTH_POWER_IXX/InputFiles/MTL_CUSTOM_POWER_SCREENTEST.txt";
        screen_custom_setpoint = "ALL";
        screen_test_set = "MTL_CLASS_POWER_SICC_ENDIOEPKG_CALC";
        screen_tests_file = "./Modules/PTH_POWER_IXX/InputFiles/MTL_IOE_CLASS_POWER_SCREENTEST.txt";
}
'''
        File('a.mtpl').touch(text)
        cl = CompLink('a.mtpl')

        # simple case
        cfg = {'find': [{'search': 'ENDIOEPKG', 'group': 1, 'replace': 'NEWNEW'}]}
        result = {'AA': text.split('\n')}
        cl.search_and_replace(result, cfg)
        self.assertTextEqual('\n'.join(result['AA']), text.replace('ENDIOEPKG', 'NEWNEW'))

        # group case
        cfg = {'find': [{'search': '(POWER).*(ENDIOEPKG)', 'group': 2, 'replace': 'NEWNEW'}]}
        result = {'AA': text.split('\n')}
        cl.search_and_replace(result, cfg)
        self.assertTextEqual('\n'.join(result['AA']), text.replace('ENDIOEPKG', 'NEWNEW'))

        # multiple
        cfg = {'find': [{'search': '(POWER).*(ENDIOEPKG)', 'group': 1, 'replace': 'power'},
                        {'search': 'screen_', 'group': 1, 'replace': 'metal_'}]}
        result = {'AA': text.split('\n')}
        cl.search_and_replace(result, cfg)
        expect = '''Test iCScreenTest power_X_SCREEN_E_ENDIOEPKG_X_X_X_X_PORTPCALC
{
        metal_custom_file = "./Modules/PTH_POWER_IXX/InputFiles/MTL_CUSTOM_POWER_SCREENTEST.txt";
        metal_custom_setpoint = "ALL";
        metal_test_set = "MTL_CLASS_power_SICC_ENDIOEPKG_CALC";
        metal_tests_file = "./Modules/PTH_POWER_IXX/InputFiles/MTL_IOE_CLASS_POWER_SCREENTEST.txt";
}
'''
        self.assertTextEqual('\n'.join(result['AA']), expect)

        # renamed
        result = {'POWER_MOD': ['Test POWER_MOD', 'line2'],
                  'POWER_QNR': ['Test POWER_QNR', 'line3']}
        cfg = {'find': [{'search': 'POWER_', 'group': 1, 'replace': 'PWR_'}]}
        cl.search_and_replace(result, cfg)
        self.assertEqual(result, {'PWR_MOD': ['Test PWR_MOD', 'line2'],
                                  'PWR_QNR': ['Test PWR_QNR', 'line3']})

    @with_(TempDir, chdir=True)
    def test_rename_test(self):
        File('a.mtpl').touch('Test Method F1_0 { }\n')
        cl = CompLink('a.mtpl')
        res = {'F1': ['Test blah F1\n',
                      'param = F1\n'],      # This is not replaced. Only the header
               'F1XX': ['DUTFlow blah\n',
                        'DUTF1FlowItem F1 F1\n',
                        'DUTF1FlowItem F1 F1',
                        'F1\n',
                        'F1',
                        'F1A',
                        'DutFlow F1A AF1']}
        cl.rename_test('F1', res)
        self.assertEqual(res, {'F1_1': ['Test blah F1_1\n',
                                        'param = F1\n'],
                               'F1XX': ['DUTFlow blah\n',
                                        'DUTF1FlowItem F1_1 F1_1\n',
                                        'DUTF1FlowItem F1_1 F1_1',
                                        'F1_1\n',
                                        'F1_1',
                                        'F1A',
                                        'DutFlow F1A AF1']})

        # coverage - maximum iter
        with self.assertRaisesRegex(ErrorCockpit, 'Maximum name iteration'):
            cl.rename_test('F1_1', res, _maxiter=0)

        # coverage - maximum replace
        res = {'F1': ['Test blah F1\n',
                      'param = F1\n'],      # This is not replaced. Only the header
               'F1XX': ['F1 F1 F1 F1 F1 F1 F1 F1 F1 F1 F1 F1']}
        with self.assertRaisesRegex(ErrorCockpit, 'Maximum replace iteration'):
            cl.rename_test('F1', res)

    @with_(TempDir, chdir=True, delete=True)
    def test_find_comp_modules(self):
        File('Modules/ARR/a.mtpl').touch(mkdir=True)
        File('Modules/ARR_LINK/a.mtpl').touch(mkdir=True)
        File('Modules/FUN_SRC/b.mtpl').touch(mkdir=True)
        File('Modules/TPI/FUN_SRC/b.mtpl').touch(mkdir=True)
        File('Modules/TPI/FUN/c.mtpl').touch(mkdir=True)
        self.assertEqual([Env.xpath(j) for j in [i for i in CompLink.find_comp_modules('_LINK')]],
                         ['Modules/ARR_LINK/a.mtpl'])
        self.assertEqual([Env.xpath(j) for j in [i for i in CompLink.find_comp_modules('_SRC')]],
                         ['Modules/FUN_SRC/b.mtpl', 'Modules/TPI/FUN_SRC/b.mtpl'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True, delete=True)
    def test_integration(self):
        File(f'{UT_DIR}/compositelink/PTH_POWER_IXX.mtpl').copy('.')
        CompLink('PTH_POWER_IXX.mtpl').main()
        self.assertGoldEqual('PTH_POWER_IXX.mtpl', f'{UT_DIR}/compositelink/PTH_POWER_IXX.mtpl.gold2')
        self.assertGoldEqual('PTH_POWER_IXX.mtpl.source', f'{UT_DIR}/compositelink/PTH_POWER_IXX.mtpl')


class TestStencil(TestCase):

    @with_(TempDir, chdir=True, delete=True)
    def test_basic(self):   # good template to use
        # basic check
        text = r'''
# stencil start: BASIC
# filename: Modules/A/a.mtpl
# find:BEGIN replace:1:END
ProgramStyle = Modular;
Test method AA_SDS {
    patlist = "abc";
    # stencil:BASIC:patlist = "def";
}
DUTFlow BEGIN {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   # stencil:BASIC:SetBin d002;
   }
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE BEGIN
       { line; }
}
'''
        File('Modules/T/t1.mtpl').touch(text, mkdir=True)
        mkdirs('Modules/A')

        Stencil('Modules/T/t1.mtpl').main()
        expect = r'''# BASIC: Total Replaced 2

# stencil start: BASIC
# filename: Modules/A/a.mtpl
# find:BEGIN replace:1:END
ProgramStyle = Modular;
Test method AA_SDS {
    patlist = "def";
    # stencil:BASIC:patlist = "def";
}
DUTFlow END {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d002;
   # stencil:BASIC:SetBin d002;
   }
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE END
       { line; }
}
'''
        self.assertTextEqual(File('Modules/A/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_remove(self):
        # tests remove composite
        # tests two stencils
        # skip if run on output
        text = r'''
# stencil start: BASIC
# filename: Modules/A/a.mtpl
# find:BEGIN replace:1:END

# stencil start: BASIC2
# filename: Modules/A/b.mtpl
# find:BEGIN replace:1:END
# remove: SOME_SDT
ProgramStyle = Modular;
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow BEGIN {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   }
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE BEGIN
       { line; }
}
'''
        File('Modules/T/t1.mtpl').touch(text, mkdir=True)
        mkdirs('Modules/A')

        Stencil('Modules/T/t1.mtpl').main()
        expect = r'''# BASIC: Total Replaced 2

# stencil start: BASIC
# filename: Modules/A/a.mtpl
# find:BEGIN replace:1:END

# stencil start: BASIC2
# filename: Modules/A/b.mtpl
# find:BEGIN replace:1:END
# remove: SOME_SDT
ProgramStyle = Modular;
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow END {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   }
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE END
       { line; }
}
'''
        self.assertTextEqual(File('Modules/A/a.mtpl').read(), expect)
        expect = r'''# BASIC2: Total Replaced 1

# stencil start: BASIC
# filename: Modules/A/a.mtpl
# find:BEGIN replace:1:END

# stencil start: BASIC2
# filename: Modules/A/b.mtpl
# find:BEGIN replace:1:END
# remove: SOME_SDT
ProgramStyle = Modular;
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow END {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   }
}
'''
        self.assertTextEqual(File('Modules/A/b.mtpl').read(), expect)

        # Skip if run on output ===========================================
        with CaptureStdoutLog() as p:
            Stencil('Modules/A/a.mtpl').main()

        print("===== start")
        print(p.getvalue())
        self.assertIn('Skipping Modules/A/a.mtpl', p.getvalue())

    @with_(TempDir, chdir=True, delete=True)
    def test_withcomplink(self):
        # test stencil with complink
        # test call from system
        text = r'''
# stencil start: BASIC
# filename: Modules/A/a.mtpl
# find:SRC_SDT replace:1:SRC_SDJ
ProgramStyle = Modular;
Test method AA_SDS {
    patlist = "abc";
}
DUTFlow SRC {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   }
}
DUTFlow SOME_SDT {
   DUTFlowItem ONE_LINK SRC @EDC @A
       # find:(\w+)_(SDS) replace:-1:$1_SDT
       # find:SetBin d(\w+); replace:1:NONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        File('Modules/T/t1.mtpl').touch(text, mkdir=True)
        mkdirs('Modules/A')

        cmd = f"torch_fixer.py Modules/T/t1.mtpl -stencil"
        with MockVar(sys, "argv", cmd.split()):
            Fixer().main()

        Stencil('Modules/T/t1.mtpl').main()
        expect = r'''# BASIC: Total Replaced 2

# stencil start: BASIC
# filename: Modules/A/a.mtpl
# find:SRC_SDT replace:1:SRC_SDJ
ProgramStyle = Modular;
Test method AA_SDS {
    patlist = "abc";
}
Test method AA_SDT {
    patlist = "abc";
}
DUTFlow SRC {
   DUTFlowItem X_AA_SDS AA_SDS
   {
   SetBin d001;
   }
}
DUTFlow SRC_SDJ {
   DUTFlowItem X_AA_SDT AA_SDT
   {
   SetBin d;
   }
}
DUTFlow SOME_SDT {
    DUTFlowItem ONE_LINK SRC_SDJ @EDC @A
       # find:(\w+)_(SDS) replace:-1:$1_SDT
       # find:SetBin d(\w+); replace:1:NONE
    # status: DONE
       # linkname: SDT
       { line ONE_LINK; }
}
'''
        self.assertTextEqual(File('Modules/A/a.mtpl').read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_get_stencil_info(self):
        text = '''
# stencil start: S1
# filename: out/f1.mtpl
# find: zBEGINz   replace:1: zENDz
# remove: SDT, SDS

# stencil start: S2
# filename: out/f2.mtpl
# find:zBz  replace:-1:NONE

ProgramStyle = Modular;   # end marker
'''
        File('a.mtpl').touch(text)
        ss = Stencil('a.mtpl')
        result = list(ss.get_stencil_info())
        pprint(result)
        self.assertEqual(result, [{'filename': 'out/f1.mtpl', 'name': 'S1', 'remove': ['SDT', 'SDS'],
                                   'find': [{'group': 1, 'replace': ' zENDz', 'search': 'zBEGINz'}]},
                                  {'filename': 'out/f2.mtpl', 'name': 'S2', 'remove': [],
                                   'find': [{'group': -1, 'replace': '', 'search': 'zBz'}]}])

        File('b.mtpl').touch('# stencil start: S1\n')
        with self.assertRaisesRegex(ErrorUser, 'ProgramStyle.*required'):
            list(Stencil('b.mtpl').get_stencil_info())


class TestMtplEdit(TestCase):

    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @with_(TempDir, chdir=True, delete=True)
    def test_removeme_dlvr(self):
        fname = 'PTH_DLVR_CXX_CLASS_P68G2.mtpl'
        File(f'{UT_DIR_REPO}/compositelink/{fname}').copy('.')
        self.assertEqual(len(MtplBlocks(fname).blocks), 456)

        cmd = f"torch_fixer.py {fname} -removeme IREF_TRIM_CORE0 "
        with MockVar(sys, "argv", cmd.split()):
            Fixer().main()
        self.assertEqual(len(MtplBlocks(fname).blocks), 432)

    @with_(TempDir, chdir=True, delete=True)
    def test_removeme(self):
        text = '''Version 1.0;
Test method A {
    IncrementCounters PTH_POWER_IXX::new1;
}
Test method B {
    IncrementCounters new2;
}
DUTFlow C {
   DUTFlowItem A A
       { line NEW_LINK; }
}
DUTFlow D {
   DUTFlowItem A A
       { line NEW_LINK; }
   DUTFlowItem B B
       { line NEW_LINK; }
}
DUTFlow E {
   DUTFlowItem D D
       { line NEW_LINK; }
}
'''
        ff = File('a.mtpl').touch(text, mkdir=True)

        cmd = f"torch_fixer.py {ff.name} -removeme D"
        with MockVar(sys, "argv", cmd.split()):
            Fixer().main()

        expect = '''Version 1.0;
Test method A {
    IncrementCounters PTH_POWER_IXX::new1;
}
DUTFlow C {
   DUTFlowItem A A
       { line NEW_LINK; }
}
DUTFlow E {
   DUTFlowItem D D
       { line NEW_LINK; }
}
'''
        self.assertTextEqual(ff.read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_format(self):
        text = '''Version 1.0;
   Test method A {    # hi

# comment
    Result { SetBin A; Setbin B; }
}
'''
        ff = File('a.mtpl').touch(text, mkdir=True)

        cmd = f"torch_fixer.py {ff.name} -format"
        with MockVar(sys, "argv", cmd.split()):
            Fixer().main()

        expect = '''Version 1.0;
Test method A
{    # hi

\t# comment
\tResult
\t{
\t\tSetBin A;
\t\tSetbin B;
\t}
}

'''
        self.assertTextEqual(ff.read(), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_update_counter(self):
        text = '''Version 1.0;
Counters
{
    a,
}
Test method A {
    IncrementCounters PTH_POWER_IXX::new1;
    IncrementCounters PTH_POWER_IXX::a;
    IncrementCounters PTH_POWER_IXX:: + "new2";
}
Test method B {
    IncrementCounters new2;
    IncrementCounters a;
}
'''
        File('PWR_LINK/a.mtpl').touch(text, mkdir=True)

        cl = MtplEdit(MtplBlocks('PWR_LINK/a.mtpl'))
        cl.update_counters()
        expect = '''Version 1.0;
Counters
{
    new2,
    new1,
    a,
}
'''
        self.assertTextEqual(''.join(cl.mb.head), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_cmd_counters(self):
        text = '''Version 1.0;
Counters
{
        n90180000_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGOFF_ALL_2,
        n90180073_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGON_ALL_2,
}
DUTFlow IOE {
   DUTFlowItem test_t1 test_t1
       {
       IncrementCounters PTH_POWER_IXX::n90180202_new;
       IncrementCounters "A";
       }
}
'''
        File('PWRX/a.mtpl').touch(text, mkdir=True)
        cmd = f"torch_fixer.py PWRX/a.mtpl -counters"
        with MockVar(sys, "argv", cmd.split()):
            Fixer().main()
        expect = '''Version 1.0;
Counters
{
    n90180202_new,
        n90180000_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGOFF_ALL_2,
        n90180073_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGON_ALL_2,
}
DUTFlow IOE {
   DUTFlowItem test_t1 test_t1
       {
       IncrementCounters PTH_POWER_IXX::n90180202_new;
       IncrementCounters "A";
       }
}
'''
        self.assertTextEqual(File('PWRX/a.mtpl').read(), expect)


class TestMultiBom(TestCase):

    def test_compare1(self):
        # success case
        with TempDir(name=True) as tdir1, TempDir(name=True) as tdir2:
            # same files
            File(f'{tdir1}/somedir/a.txt').touch('a', mkdir=True)
            File(f'{tdir2}/somedir/a.txt').touch('a', mkdir=True)
            File(f'{tdir1}/somedir1/b.txt').touch('b', mkdir=True)
            File(f'{tdir2}/somedir1/b.txt').touch('b', mkdir=True)
            # exist in one but not in other
            File(f'{tdir1}/somedir3/c.txt').touch('c1', mkdir=True)
            File(f'{tdir2}/somedir4/c.txt').touch('c2', mkdir=True)
            # exception case
            File(f'{tdir1}/runcard/c.txt').touch('c1', mkdir=True)
            File(f'{tdir2}/runcard/c.txt').touch('c2', mkdir=True)

            MultiBom([tdir1, tdir2]).compare()

    def test_compare2(self):
        # fail case
        with TempDir(name=True) as tdir1, TempDir(name=True) as tdir2:
            # same files
            File(f'{tdir1}/somedir/a.txt').touch('a', mkdir=True)
            File(f'{tdir2}/somedir/a.txt').touch('a1', mkdir=True)

            with self.assertRaisesRegex(ErrorUser, 'to match between'):
                MultiBom([tdir1, tdir2]).compare()

    def test_copy(self):
        # success case
        with TempDir(name=True) as tdir1, TempDir(name=True) as tdir2:
            File(f'{tdir1}/somedir/a1.txt').touch('a1', mkdir=True)
            File(f'{tdir1}/somedir/a2.txt').touch('a2', mkdir=True)
            File(f'{tdir1}/somedir1/b.txt').touch('b', mkdir=True)
            File(f'{tdir1}/somedir3/c.txt').touch('c1', mkdir=True)
            mb = MultiBom([tdir1])
            mb.copy(tdir2)

            # Should be no error
            mb = MultiBom([tdir1, tdir2])
            mb.compare()

            # expect the correct files
            with Chdir(tdir2):
                expect = {'./somedir1/b.txt', './somedir3/c.txt', './somedir/a2.txt', './somedir/a1.txt'}
                self.assertEqual(set(Allfiles('.')), expect)

    def test_runcard(self):
        with TempDir(name=True) as tdir:
            mb = MultiBom([f'{tdir}/tp1', f'{tdir}/tp2'])
            text1 = '''<CorrelationTable>
  <Row Package="X1"
  <Row Package="X2"
</CorrelationTable>
'''
            File(f'{tdir}/tp1/astra/astra_hdmx_vc/runcard/a.xml').touch(text1, mkdir=True)
            File(f'{tdir}/tp1/astra/astra_hdmx_vc/runcard/b.xml').touch(text1, mkdir=True)
            text2 = '''<CorrelationTable>
  <Row Package="X3"
  <Row Package="X4"
</CorrelationTable>
'''
            File(f'{tdir}/tp2/astra/astra_hdmx_vc/runcard/a.xml').touch(text2, mkdir=True)

            outf = File(f'{tdir}/out/astra/astra_hdmx_vc/runcard/a.xml').touch(text1, mkdir=True)
            mb.runcard(f'{tdir}/out')
            expect = '''<CorrelationTable>
  <Row Package="X1"
  <Row Package="X2"
  <Row Package="X3"
  <Row Package="X4"
</CorrelationTable>
'''
            # combined
            self.assertTextEqual(outf.read(), expect)
            # unchanged
            self.assertTextEqual(File(f'{tdir}/out/astra/astra_hdmx_vc/runcard/b.xml').read(), text1)

    def test_basic(self):
        # This is meant for coverage. Single bom only.
        src = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            shutil.copytree(src, f'{tdir}/TPL')           # 3.2 secs for torch_p6828_fixer
            cmd = f"torch_fixer.py {tdir}/TPL -multibom {tdir}/out"
            with Chdir(f'{tdir}/TPL'), \
                    MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                Fixer().main()

            print(p.getvalue())

            # make sure it completed fine
            self.assertIn('MultiBom: Runtime', p.getvalue())
            self.assertIn('SUCCESS via torch_fixer.py', p.getvalue())
            self.assertEqual(len(os.listdir(f'{tdir}/out')), 7)

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="optional - run with -o"))
    def test_integ_mvtp(self):
        src = f'{UT_DIR_REPO}/torch_mvtp_pass'
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            shutil.copytree(src, f'{tdir}/TPL')           # 3.2 secs for torch_p6828_fixer
            File(f'{tdir}/TPL/ENG_TP').rename('POR_TP')
            cmd = f"torch_fixer.py {tdir}/TPL -multibom {tdir}/out"
            with Chdir(f'{tdir}/TPL'), \
                    MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                Fixer().main()

            print(p.getvalue())

            # make sure it completed fine
            self.assertIn('MultiBom: Runtime', p.getvalue())
            self.assertIn('SUCCESS via torch_fixer.py', p.getvalue())
            self.assertEqual(len(os.listdir(f'{tdir}/out')), 12)

    def test_basicfail(self):
        src = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            shutil.copytree(src, f'{tdir}/TPL')           # 3.2 secs for torch_p6828_fixer
            cmd = f"torch_fixer.py {tdir}/TPL -multibom {tdir}/out"
            with Chdir(f'{tdir}/TPL'), \
                    MockVar(sys, "argv", cmd.split()), \
                    MockVar(TorchPostProc, "main", Mock(side_effect=Exception)), \
                    CaptureStdoutLog() as p:
                Fixer().main()

            print(p.getvalue())

            # make sure it completed fine
            self.assertIn('MultiBom: Runtime', p.getvalue())
            self.assertIn('There are ERRORS!', p.getvalue())
            self.assertEqual(len(os.listdir(f'{tdir}/out')), 6)

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="optional - run with -o"))
    def test_integration(self):  # multibom
        src = f'{UT_DIR_REPO}/torch_p6828_multibom'
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            shutil.copytree(src, f'{tdir}/TPL')           # 3.2 secs for torch_p6828_fixer
            cmd = f"torch_fixer.py {tdir}/TPL/MTLXXXXXXX19M0ZSXXX_P28_2 {tdir}/TPL/MTLXXXXXXX19M0ZSXXX_P68_2 -multibom {tdir}/out"
            with MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                Fixer().main()

            print(p.getvalue())

            # make sure it completed fine
            self.assertIn('MultiBom: Runtime', p.getvalue())

            print("Total files P28:", len(list(Allfiles(f'{tdir}/TPL/MTLXXXXXXX19M0ZSXXX_P28_2'))))
            print("Total files P68:", len(list(Allfiles(f'{tdir}/TPL/MTLXXXXXXX19M0ZSXXX_P68_2'))))
            self.assertEqual(len(list(Allfiles(f'{tdir}/out'))), 5639)


class TestBdefFix(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_integ(self):
        tpobj = TestProgram(f'{UT_DIR}/ut_23/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(name=True) as tdir:

            # Using a bdef that is almost empty
            bf = BdefFix(tpobj)
            bf.bdef = f'{tdir}/BinDefinitions.bdefs'
            File(f'{UT_DIR}/ut_23/Shared/BaseInputs/BinDefinitions.bdefs.short').copy(bf.bdef)
            bf.main()
            self.assertGoldEqual(f'{tdir}/BinDefinitions.bdefs',
                                 f'{UT_DIR}/ut_23/Shared/BaseInputs/BinDefinitions.bdefs.short.gold2')

            # Using a bdef that exist
            bf = BdefFix(tpobj)
            bf.bdef = f'{tdir}/BinDefinitions.bdefs'
            File(f'{UT_DIR}/ut_23/Shared/BaseInputs/BinDefinitions.bdefs.long').copy(bf.bdef)
            bf.main()
            self.assertGoldEqual(f'{tdir}/BinDefinitions.bdefs',
                                 f'{UT_DIR}/ut_23/Shared/BaseInputs/BinDefinitions.bdefs.long.gold2')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_proc_setbin(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        bf = BdefFix(tpobj)

        # first line
        bf.proc_setbin('SetBin SoftBins.b12052_fail_ARR_ATO;', 'file1', 1, 'ax')
        self.assertEqual(bf.softbin, {'12052': 'b12052_fail_ARR_ATO'})
        self.assertEqual(bf.src, {'12052': 'ax'})
        self.assertEqual(bf.fix, {})
        # second line - same
        bf.proc_setbin('SetBin SoftBins.b12052_fail_ARR_ATO;', 'file1', 1, 'ax')
        self.assertEqual(bf.softbin, {'12052': 'b12052_fail_ARR_ATO'})
        self.assertEqual(bf.fix, {})
        # third line - same with quotes
        bf.proc_setbin('SetBin "SoftBins.b12052_fail_ARR_ATO";', 'file1', 1, 'ax')
        self.assertEqual(bf.softbin, {'12052': 'b12052_fail_ARR_ATO'})
        self.assertEqual(bf.fix, {})
        # fourth line - different
        bf.proc_setbin('SetBin SoftBins.b12052_fail_ARR_CORE;', 'file2', 2, 'ay')
        self.assertEqual(bf.softbin, {'12052': 'b12052_fail_ARR_ATO'})
        self.assertEqual(bf.fix, {'file2': {(2, '12052')}})

        # get_module_shared
        self.assertEqual(BdefFix.get_module_shared('/p/Modules/FUN_CORE_C68/a.mtpl'), 'FUN_CORE_C')

    def test_mtpl_order(self):
        mtpls = 'ARR_SCN/b TPI_BASE/a FUS_XXX/a SCN_ALL/a'.split()
        self.assertEqual(BdefFix._mtpl_order(mtpls, []),
                         ['FUS_XXX/a', 'TPI_BASE/a', 'ARR_SCN/b', 'SCN_ALL/a'])
        self.assertEqual(BdefFix._mtpl_order(mtpls, ['ARR_SCN']),
                         ['FUS_XXX/a', 'TPI_BASE/a', 'SCN_ALL/a', 'ARR_SCN/b'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_bdef(self):
        tpobj1 = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        bf = BdefFix(tpobj1)
        self.assertEqual(basename(bf.bdef), 'BinDefinitions.bdefs')

        tpobj2 = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with self.assertRaisesRegex(ErrorUser, 'has multiple'):
            BdefFix(tpobj1, tpobj2)

    def test_mtl_softbin(self):
        # something went wrong with proc_softbin
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        with MockVar(bf, 'proc_setbin', Mock(side_effect=Exception)):
            with self.assertRaisesRegex(ErrorInput, 'There are errors in the .mtpl'):
                bf.read_mtl_softbins()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_fix_mtpl(self):
        # something went wrong with proc_softbin test case below. Normal pass testcase is in test_basic()
        tpobj = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        with TempDir(name=True, chdir=True) as tdir:
            text = '''line1
    SetBin SoftBins.b2111_fail_FAIL_SYSTEM_SOFTWARE;
    SetBin SoftBins.b2112_fail_FAIL_SYSTEM_something;
            '''
            fobj = File('a.mtpl').touch(text)
            bf.fix = {'a.mtpl': {(2, '2111')}}   # set_of(lno, softbin_no):
            bf.src = {'2111': ' SetBin NEWLINE\n'}
            bf.fix_mtpl()
            expect = '''line1
 SetBin NEWLINE
    SetBin SoftBins.b2112_fail_FAIL_SYSTEM_something;
'''
            self.assertTextEqual(fobj.read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_update_bdefs(self):
        tpobj = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        with TempDir(name=True, chdir=True) as tdir:
            text = '''
BinDefs
{
        BinGroup PassFailBins
        {
                Bin Pass 0: "Count of Passing Devices";
                Bin Fail 1: "Count of Failing Devices";
        }
        BinGroup HardBins
        {
                Bin b1_PASS_CMTTRAY_1   1   : "b1_PASS_CMTTRAY_1",  Pass;
                Bin b2_PASS_CMTTRAY_2   2   : "b2_PASS_CMTTRAY_2",  Pass;
                Bin b44_FAIL_SBFT   44   : "b44_FAIL_SBFT",  Fail;
                Bin b7_FAIL_SLOW    7    : "b7_FAIL_SLOW", Fail;
        }
        BinGroup SoftBins
        {
            # Start add bins from .mtpl
                LeafBin b0100_pass_pure_SHARED_BIN    0100    : "b0100_pass_pure_SHARED_BIN",    b1_PASS_CMTTRAY_1;
                LeafBin b10039086_as_is     10039086 : "", b1_PASS_CMTTRAY_1;
                LeafBin b10039087_pass_old  10039087 : "", b1_PASS_CMTTRAY_1;
                LeafBin b90444482_fail_old  90444482 : "", b44_FAIL_SBFT;
                LeafBin b730_fail_YBS       730 : "",      b7_FAIL_SLOW
        }
}
            '''
            fobj = File('a.bdefs').touch(text)
            bf.bdef = fobj.get_name()
            bf.softbin = {'10039087': 'b10039087_new1',
                          '90444482': 'b90444482_new2',
                          '730': 'b730_fail_YBS'}
            bf.update_bdefs()
            expect = '''
BinDefs
{
        BinGroup PassFailBins
        {
                Bin Pass 0: "Count of Passing Devices";
                Bin Fail 1: "Count of Failing Devices";
        }
        BinGroup HardBins
        {
                Bin b1_PASS_CMTTRAY_1   1   : "b1_PASS_CMTTRAY_1",  Pass;
                Bin b2_PASS_CMTTRAY_2   2   : "b2_PASS_CMTTRAY_2",  Pass;
                Bin b44_FAIL_SBFT   44   : "b44_FAIL_SBFT",  Fail;
                Bin b7_FAIL_SLOW    7    : "b7_FAIL_SLOW", Fail;
        }
        BinGroup SoftBins
        {
                LeafBin b0100_pass_pure_SHARED_BIN    0100    : "b0100_pass_pure_SHARED_BIN",    b1_PASS_CMTTRAY_1;
                LeafBin b10039086_as_is     10039086 : "", b1_PASS_CMTTRAY_1;
            # Start add bins from .mtpl
            LeafBin b10039087_new1  10039087  : "b10039087_new1",  b1_PASS_CMTTRAY_1;
            LeafBin b730_fail_YBS  730  : "b730_fail_YBS",  b7_FAIL_SLOW;
            LeafBin b90444482_new2  90444482  : "b90444482_new2",  b44_FAIL_SBFT;
        }
}
'''
            self.assertTextEqual(fobj.read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_update_bdefs_fail(self):
        tpobj = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        with TempDir(name=True, chdir=True) as tdir:
            text = '''
BinDefs
{
        BinGroup PassFailBins
        {
                Bin Pass 0: "Count of Passing Devices";
        }
        BinGroup HardBins
        {
                Bin b1_PASS_CMTTRAY_1   1   : "b1_PASS_CMTTRAY_1",  Pass;
        }
        BinGroup SoftBins
        {
                LeafBin b0100_pass_pure_SHARED_BIN    0100    : "b0100_pass_pure_SHARED_BIN",    b1_PASS_CMTTRAY_1;
                LeafBin b2100_pass_pure_SHARED_BIN    0100    : "b0100_pass_pure_SHARED_BIN",    b1_PASS_CMTTRAY_1;
        }
}
            '''
            fobj = File('a.bdefs').touch(text)
            bf.bdef = fobj.get_name()
            bf.softbin = {'2100': 'b2100_unknown'}
            with self.assertRaisesRegex(ErrorUser, 'Expecting 8-digit bin'):
                bf.update_bdefs()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True, delete=True)
    def test_sharedmod(self):
        tdir = os.getcwd()
        shutil.copytree(f'{UT_DIR}/Simple3b', 'TPL')
        tpobj = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        bf.main(shared=False)
        self.assertEqual(bf.modules_wo_shared([]), ['PTH', 'SCN'])
        self.assertEqual(bf.modules_wo_shared(['ARR']), ['ARR'])
        self.assertEqual(bf.shared_modules, {'ARR'})
        pprint(bf.fix)
        self.assertEqual(bf.fix, {f'{tdir}/TPL/Modules/PTH/pth.mtpl': {(55, '90757501')}})
        pprint(bf.softbin)
        self.assertEqual(bf.softbin, {'90757501': 'b90757501_fail_NSIOgitsub',
                                      '90757502': 'b90757502_fail_some_common_SHARED_BIN',
                                      '90757503': 'b90757503_fail_some_common_SHARED_BIN',
                                      '90757504': 'b90757504_fail_some_softbin',
                                      '90757505': 'b90757505_fail_some_softbin_SHARED_BIN',
                                      '90757506': '"b90757506_fail_mtt"',
                                      '90999901': 'b90999901_fail_FAIL_DPS_ALARM'})

        # modules_wo_shared unittest
        with TempDir(name=True, chdir=True) as tdir:
            data = ['Modules/ARR/ARR.mtpl',
                    'Modules/ARR1/ARR1.mtpl',
                    'Modules/TPI/TPI_VCC/TPI_VCC.mtpl',
                    'Modules/TPI/TPI_VCC1/TPI_VCC1.mtpl',
                    'Modules/DRV/DRV1/DRV_RST.mtpl']
            for ff in data:
                File(ff).touch(mkdir=True)
            File('Modules/ARR/.git/a').touch(mkdir=True)
            File('Modules/TPI/.git/a').touch(mkdir=True)

            with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=data)):
                self.assertEqual(bf.modules_wo_shared([]), ['ARR1', 'DRV1'])

    @with_(TempDir, chdir=True, delete=True)
    def test_noshare(self):
        shutil.copytree(f'{UT_DIR_REPO}/Simple3', 'TPL')
        tpobj = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        bf.main(shared=False)
        self.assertEqual(bf.fix, {})
        self.assertEqual(bf.softbin, {'90757501': 'b90757501_fail_NSIO',
                                      '90757502': 'b90757502_fail_some_common_SHARED_BIN',
                                      '90757503': 'b90757503_fail_some_common_SHARED_BIN',
                                      '90757504': 'b90757504_fail_some_softbin',
                                      '90757505': 'b90757505_fail_some_softbin_SHARED_BIN',
                                      '90757506': '"b90757506_fail_mtt"',
                                      '90999901': 'b90999901_fail_FAIL_DPS_ALARM'})

    @with_(TempDir, chdir=True, delete=True)
    def test_unshared_bin(self):
        # both shared and unshared are tested here
        tdir = os.getcwd()
        shutil.copytree(f'{UT_DIR_REPO}/Simple3', 'TPL')
        tpobj = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        bf.main()
        pprint(bf.fix)
        self.assertEqual(bf.fix, {Env.xpath(f'{tdir}/TPL/Modules/ARR/array.mtpl'): {(39, '90757503'),
                                                                                    (72, '90757506'),
                                                                                    (35, '90757501')},
                                  Env.xpath(f'{tdir}/TPL/Modules/PTH/pth.mtpl'): {(52, '90757502'),
                                                                                  (55, '90757501'),
                                                                                  (56, '90757506')}})
        pprint(bf.src)
        self.assertEqual(bf.src, {'90757501': ' SetBin SoftBins.b90757501_fail_NSIO_SHARED_BIN;\n',
                                  '90757502': ' SetBin SoftBins.b90757502_fail_some_common;\n',
                                  '90757503': ' SetBin SoftBins.b90757503_fail_some_common;\n',
                                  '90757504': ' SetBin SoftBins.b90757504_fail_some_softbin;\n',
                                  '90757505': ' SetBin SoftBins.b90757505_fail_some_softbin_SHARED_BIN;\n',
                                  '90757506': ' SetBin "SoftBins.b90757506_fail_mtt_SHARED_BIN";\n',
                                  '90999901': 'SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;\n'})
        pprint(bf.softbin)
        self.assertEqual(bf.softbin, {'90757501': 'b90757501_fail_NSIO_SHARED_BIN',     # shared need fix
                                      '90757502': 'b90757502_fail_some_common',         # common need fix
                                      '90757503': 'b90757503_fail_some_common',         # common need fix
                                      '90757504': 'b90757504_fail_some_softbin',             # unique, nofix
                                      '90757505': 'b90757505_fail_some_softbin_SHARED_BIN',  # shared, nofix
                                      '90757506': '"b90757506_fail_mtt"_SHARED_BIN',     # mtt need fix
                                      '90999901': 'b90999901_fail_FAIL_DPS_ALARM'})      # special bin


class TestInteg(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_get_tpshared(self):
        File('POR_TP/TGLH81/EnvironmentFile.g.env').touch()
        self.assertEqual(len(DoFixer().get_tp_shared()), 1)

    @with_(TempDir, chdir=True, delete=True)
    def test_cmd_reorder(self):
        text = '''Version 1.0;
Counters
{
        n90180000_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGOFF_ALL_2,
        n90180073_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGON_ALL_2,
}
DUTFlow A {
   DUTFlowItem test_t1 B
       {
       IncrementCounters PTH_POWER_IXX::n90180202_new;
       IncrementCounters "A";
       }
}
DUTFlow B {
   DUTFlowItem test_t1 test_t1
       {
       IncrementCounters PTH_POWER_IXX::n90180202_new;
       IncrementCounters "A";
       }
}
Test blah test_t1 {}
'''
        File('PWRX/a.mtpl').touch(text, mkdir=True)
        cmd = f"torch_fixer.py PWRX/a.mtpl -reorder"
        with MockVar(sys, "argv", cmd.split()):
            Fixer().main()
        expect = '''Version 1.0;
Counters
{
        n90180000_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGOFF_ALL_2,
        n90180073_fail_SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGON_ALL_2,
}
Test blah test_t1 {}
DUTFlow B {
   DUTFlowItem test_t1 test_t1
       {
       IncrementCounters PTH_POWER_IXX::n90180202_new;
       IncrementCounters "A";
       }
}
DUTFlow A {
   DUTFlowItem test_t1 B
       {
       IncrementCounters PTH_POWER_IXX::n90180202_new;
       IncrementCounters "A";
       }
}
'''
        self.assertTextEqual(File('PWRX/a.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, os.environ, 'VEP2_ROOT', '/p')
    def test_lockall(self):
        cmd = f'torch_fixer.py -lockall {UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env'
        with MockVar(sys, "argv", cmd.split()):
            unlocked_path = ['/intel/hdmxpats/mtl/MaaaCdrv/RevTCCXXA4.0/p4']
            with MockVar(CheckLock, 'get_pat_patch_unlocked', Mock(return_value=unlocked_path)), \
                    MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, 'ci_plist running. ok'))):
                ff = Fixer()
                expect = 'ci_plist.py -module MaaaCdrv -rev RevTCCXXA4.0p4 -lock -dev -comment Lock_for_tp_integration'
                self.assertEqual(ff.do_lockall(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_nochange(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        bf = BdefFix(tpobj)
        self.assertEqual(len(bf.all_mtpl), 144)
        self.assertEqual(basename(bf.bdef), 'BinDefinitions.bdefs')
        with MockVar(File, "rewrite", Mock()):
            bf.main()
        self.assertEqual(len(bf.bm.bvars), 115)
        self.assertEqual(len(bf.softbin), 1290)
        self.assertEqual(len(bf.fix), 62)   # unshare changes

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @with_(TempDir, chdir=True, delete=True)
    def test_p28p68(self):
        tdir = os.getcwd()
        src = f'{UT_DIR}/torch_p6828_fixer'  # /POR_TP/Class_MTL_P68/EnvironmentFile.env'
        shutil.copytree(src, f'{tdir}/TPL')           # 3.2 secs for torch_p6828_fixer
        # File('TPL/TPConfig/unshared_bin.trigger.txt').touch(mkdir=True)
        tpobj1 = TestProgram(f'{tdir}/TPL/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        tpobj2 = TestProgram(f'{tdir}/TPL/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        bf = BdefFix(tpobj1, tpobj2)
        bf.main()

        # Check data structure
        self.assertEqual(len(bf.bm.bvars), 376)
        self.assertEqual(len(bf.softbin), 4440)
        self.assertEqual(len(bf.src), len(bf.softbin))   # must be
        self.assertEqual(len(bf.fix), 96)     # number of modified mtpl files
        self.assertEqual(len(list(keys_atlevel(bf.fix, 1))), 31567)   # lines to fix, previous: 4951

        # make sure it is correct
        # gold3 is with shared_bin, without unshared_bin
        # gold5 is BdefHack called inside BdefFix
        targ = File(f'{tdir}/TPL/Shared/BaseInputs/BinDefinitions.bdefs')
        gold = File(f'{UT_DIR}/torch_p6828_fixer/BinDefinitions.bdefs.gold6')
        self.assertGoldEqual(targ.get_name(), gold.get_name())

        # make a copy, then rerun.
        targ.copy(f'{tdir}/BinDefinitions.bdefs.orig', xfer=False)
        bf.main()
        self.assertEqual(targ.read(), File(f'{tdir}/BinDefinitions.bdefs.orig').read())

        # make one more copy, then rerun again. This time there should be no change.
        targ.copy(f'{tdir}/BinDefinitions.bdefs.orig2', xfer=False)
        print("#### Rerun start")
        bf.main()
        self.assertEqual(basename(targ.get_name()), 'BinDefinitions.bdefs')
        self.assertEqual(targ.read(), File(f'{tdir}/BinDefinitions.bdefs.orig2').read())   # rerun, should be no change

    def test_basic_simple(self):
        # full run start to finish as executable
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            shutil.copytree(src, f'{tdir}/TPL')
            cmd = "torch_fixer.py"
            with Chdir(f'{tdir}/TPL'), MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
                Fixer().main()
            print(p.getvalue())
            self.assertIn('Fixer: Runtime', p.getvalue())

            # Composite link and Stencil is called
            File(f'{tdir}/TPL/Modules/ARR_LINK/a.mtpl').touch(mkdir=True)
            File(f'{tdir}/TPL/Modules/FUN_SRC/b.mtpl').touch('ProgramStyle a;\n', mkdir=True)
            with Chdir(f'{tdir}/TPL'), MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
                Fixer().main()
            print("==== Case2")
            print(p.getvalue())
            self.assertIn('No composite link found in Modules/ARR_LINK/a.mtpl', Env.xpath(p.getvalue()))
            self.assertIn('No Stencil found in Modules/FUN_SRC/b.mtpl', Env.xpath(p.getvalue()))

    def test_basic_sort(self):
        # full run start to finish as executable
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            shutil.copytree(src, f'{tdir}/TPL')
            cmd = "torch_fixer.py -sort"
            with Chdir(f'{tdir}/TPL'),\
                    MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                Fixer().main()
            print(p.getvalue())
            self.assertIn('Fixer: Runtime', p.getvalue())
        OPT.sort = False

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_basic(self):
        # full run start to finish as executable
        src = f'{UT_DIR}/torch_mvtp'
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            shutil.copytree(src, f'{tdir}/TPL')           # 3.2 secs for torch_p6828_fixer
            File(f'{tdir}/TPL/ENG_TP').rename('POR_TP')
            cmd = "torch_fixer.py"
            bdef = File(f'{tdir}/TPL/Shared/BaseInputs/BinDefinitions.bdefs')
            orig = bdef.read()
            with Chdir(f'{tdir}/TPL'), MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
                Fixer().main()

            print(p.getvalue())

            # make sure it completed fine
            self.assertIn('Fixer: Runtime', p.getvalue())

            # confirm meta is generated
            self.assertIn('meta_info.do_not_commit.log is written', p.getvalue())

            # Confirm bdef has changed
            newbdef = bdef.read()
            self.assertNotEqual(newbdef, orig)

            # rerun
            with Chdir(f'{tdir}/TPL'), MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
                Fixer().main()
            self.assertIn('Fixer: Runtime', p.getvalue())
            self.assertEqual(bdef.read(), newbdef)    # no change

    def test_bin(self):
        with MockVar(BinHack2, 'main', Mock()):
            cmd = f"torch_fixer.py {UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env -bin"
            with MockVar(sys, "argv", cmd.split()):
                Fixer().main()

    def test_tar(self):
        with TempDir(name=True, delete=True) as tdir:     # Set delete=False to debug
            File(f'{tdir}/src/a.txt').touch('sample_text', mkdir=True)
            File(f'{tdir}/src/b/c.txt').touch('sample_text2', mkdir=True)
            cmd = f"torch_fixer.py {join(tdir, 'src')} -tar {join(tdir, 'dest', 'a.tar')}"
            with MockVar(sys, "argv", cmd.split()):
                Fixer().main()

            mkdirs(f'{tdir}/out')
            with Chdir(f'{tdir}/out'):
                with tarfile.open(f'{tdir}/dest/a.tar.gz', "r:gz") as tarfh:
                    tarfh.extractall()
                self.assertEqual(set(Allfiles('.')), {'./b/c.txt', './a.txt'})
                self.assertEqual(File('./b/c.txt').read(), 'sample_text2')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
