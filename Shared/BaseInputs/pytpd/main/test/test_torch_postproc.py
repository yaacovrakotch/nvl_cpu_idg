#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for torch_postproc.py
"""
import os.path

from setenv_unittest import UT_DIR, ROOT_ENV, UT_DIR_REPO, EXIST_PDX_I_DRIVE  # must be first import for unittests
from main.torch_postproc import *
from gadget.errors import ErrorUser
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.disk import Chdir, mkdirs, Allfiles
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from unittest.mock import Mock
from tp.testprogram import Env
from pprint import pprint
import sys
import main.torch_postproc as torch_postproc
import shutil


class TestSingleLevel(TestCase):

    def test_basic(self):
        src = f'{UT_DIR_REPO}/Simple3_singlelevel'
        with TempDir(name=True, startcopy=src, chdir=True, delete=True) as tdir:  # Set delete=False to debug
            tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            countflow = list(tpobj.mtpl.iter_flows())
            sl = SingleLevel(tpobj)
            with CaptureStdoutLog() as p:
                sl.main()

            # check output - this indicates which files are updated
            expect = '''-i- UPDATED: ./Modules/SCNX/InputFiles/something.txt is updated by SingleLevel.mtpl.do_move()
-i- UPDATED: ./Modules/SCNX/scan.mtpl is updated by SingleLevel.mtpl.do_move()
-i- UPDATED: ./POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl is updated by SingleLevel.mtpl.do_move()
-i- UPDATED: ./Modules/ARR/array.mtpl is updated by SingleLevel.mtpl.do_rename()
-i- UPDATED: ./Modules/SCN/InputFiles/something.txt is updated by SingleLevel.mtpl.do_rename()
-i- UPDATED: ./Modules/SCN/scan.mtpl is updated by SingleLevel.mtpl.do_rename()
-i- UPDATED: ./POR_TP/TGLH81/EnvironmentFile.env is updated by SingleLevel.mtpl.do_rename()
-i- UPDATED: ./POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl is updated by SingleLevel.mtpl.do_rename()
'''
            result = '\n'.join(x for x in p.getvalue().split('\n') if 'completed in' not in x)
            self.assertTextEqual(result.replace(tdir, 'PATH'), expect)

            # check stpl
            expect = r'''Version 1.0;

SubTestPlans
{
  ..\..\Modules\ARR\array.mtpl;
  ..\..\Modules\SCN\scan.mtpl;
  ..\..\Modules\PTH\pth.mtpl;

  Final .\ProgramFlowsTestPlan\ProgramFlows.mtpl;
}
'''
            self.assertTextEqual(File('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').read(), expect)

            # check txt file is modified
            expect = r'''
something1: Modules/Team/SCNX              # unchanged
something2: Modules/SCN/InputFiles
something3: Modules\SCN\InputFiles
something4: others
something5: Modules/ARR/InputFiles/blah   # different module
'''
            self.assertTextEqual(File('Modules/SCN/InputFiles/something.txt').read(), expect)

            # check json file
            expect = '''
{
   "ARRX": "ARR",
   "SCNX": "SCN"
}
'''
            self.assertTextEqual(File('POR_TP/TGLH81/InputFiles/old_new_module_map.json').read(), expect)

            # check if everything loads ok, flow is the same
            tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()  # this should pass
            countflow2 = list(tpobj.mtpl.iter_flows())
            self.assertEqual(len(countflow), len(countflow2))

            # check env file
            self.assertGoldEqual('POR_TP/TGLH81/EnvironmentFile.env',
                                 f'{UT_DIR_REPO}/Simple3_singlelevel/POR_TP/TGLH81/EnvironmentFile.env.gold')

            sl = SingleLevel(tpobj)
            File('POR_TP/TGLH81/InputFiles/no_single_level_module.settings.txt').touch()
            self.assertEqual(sl.main(), 2)  # skipped

    def test_skipped(self):
        # No fsm case
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        sl = SingleLevel(tpobj)
        self.assertEqual(sl.main(), 1)  # skipped

    def test_get_shared_modules(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple3_singlelevel/POR_TP/TGLH81/EnvironmentFile.env').init()
        sl = SingleLevel(tpobj)
        data = '''../../Modules/ARR_COMMON_GXX/ARR_COMMON_GXX_CLASS_P68G2.mtpl;
../../Modules/TPI/TPI_DEDCHIST_YXX/TPI_DEDCHIST_YXX.mtpl
./ProgramFlowsTestPlan/ProgramFlows.mtpl
'''.split()
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=data)):
            self.assertEqual(sl._get_shared_modules(),
                             {'Modules/TPI/TPI_DEDCHIST_YXX': 'Modules/TPI_DEDCHIST_YXX'})

    def test_get_modules_2rename(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple3_singlelevel/POR_TP/TGLH81/EnvironmentFile.env').init()
        sl = SingleLevel(tpobj)
        data = '''../../Modules/ARR_COMMON_GXX/ARR_COMMON_GXX_CLASS_P68G2.mtpl
../../Modules/TPI/TPI_DEDCHIST_YXX/TPI_DEDCHIST_YXX.imp
./ProgramFlowsTestPlan/ProgramFlows.mtpl
'''.split()
        with MockVar(tpobj, 'get_all_mtpl_from_stpl', Mock(return_value=data)), \
                MockVar(tpobj, 'get_scope', Mock(return_value='blah')):
            self.assertEqual(sl._get_modules_2rename(),
                             {'Modules/ARR_COMMON_GXX': 'Modules/blah'})


class TestRecipeEdit(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_main(self):
        # case1 - no astra folder
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        self.assertEqual(RecipeEdit(tpobj).main(), 1)

        # case2 - with astra folder but uservar is production
        with TempDir(name=True) as tdir:
            tpobj.tpldir = tdir
            text = r'''
<someline>
<Item name="TP_BASE" desc="Base TP Directory" value="I:\hdmxprogs\MTL\MTLPBX7A0H18H00S213\TPL" />
'''
            File(
                f'{tdir}/astra/astra_hdmx_vc/recipe/MTLPBX7A0H18H00S213/tp_recipe/CLASS_P68G2_MTL_P68G2_HDMT_1_MPS_Universal_TPrecipe_TPL.xml').touch(
                text, mkdir=True)
            self.assertEqual(RecipeEdit(tpobj).main(), 2)

        # case3 - updated file
        with TempDir(name=True) as tdir:
            tpobj.tpldir = tdir
            recipe = f'{tdir}/astra/astra_hdmx_vc/recipe/MTLPBX7A0H18H00S213/tp_recipe/CLASS_P68G2_MTL_P68G2_HDMT_1_MPS_Universal_TPrecipe_TPL.xml'
            text = r'''
<someline>
<Item name="TP_BASE" desc="Base TP Directory" value="I:\hdmxprogs\MTL\MTLPBX7A0H18H0QS213\TPL" />
'''
            File(recipe).touch(text, mkdir=True)
            RecipeEdit(tpobj).main()
            expect = r'''
<someline>
<Item name="TP_BASE" desc="Base TP Directory" value="I:\tpvalidation\hdmxprogs\MTL\MTLPBX7A0H18H0QS213\TPL" />
'''
            self.assertTextEqual(File(recipe).read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_letter_tpname(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            # pass case
            text = r'''
<Item name="TP_BASE" desc="Base TP Directory" value="I:\hdmxprogs\MTL\MTLPBX7A0H18H0QS213\TPL" />
            '''
            fname = f'{tdir}/uservar.xml'
            File(fname).touch(text)
            self.assertEqual(RecipeEdit(tpobj).get_letter_tpname(fname), 'Q')

            text = '''
{
}
            '''
            fname = f'{tdir}/uservar1.xml'
            File(fname).touch(text)
            with self.assertRaisesRegex(ErrorInput, 'Cannot derive testprogramname from'):
                RecipeEdit(tpobj).get_letter_tpname(fname)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_update(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        # This has both case for replaced and non-replaced
        in_list = r'''
<someline>
<Item name="TP_BASE" desc="Base TP Directory" value="I:\tpvalidation\hdmxprogs\MTL\MTLPBX7A0H18H00S213\TPL" />
<Item name="TP_BASE" desc="Base TP Directory" value="I:\hdmxprogs\MTL\MTLPBX7A0H18H00S213\TPL" />
'''.split('\n')
        expect = ['',
                  '<someline>',
                  '<Item name="TP_BASE" desc="Base TP Directory" value="I:\\tpvalidation\\hdmxprogs\\MTL\\MTLPBX7A0H18H00S213\\TPL" '
                  '/>',
                  '<Item name="TP_BASE" desc="Base TP Directory" value="I:\\tpvalidation\\hdmxprogs\\MTL\\MTLPBX7A0H18H00S213\\TPL" />',
                  '']

        self.assertEqual(list(RecipeEdit(tpobj).update(in_list)), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_edit_sc_recipe(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tpobj.tpldir = tdir
            text = r'''
    <SourcePath>M:\recipe\hdmx\prod\MTL\MTLXXXXXXX19K0BSXXX\CLASS_P68G2_MTL_P68G2_HDMT_1_CLASSREBI_MPS_Manifest_3.xml</SourcePath>
  </ComponentRecipe>
    <SourcePath>M:\recipe\hdmx\prod\MTL\MTLXXXXXXX19K0BSXXX\sc_recipe\CLASS_P68G2_CLASSREBI_MPS_SCrecipe.xml</SourcePath>
</MainManifest>'''

            f1 = f'{tdir}/astra/astra_hdmx_vc/recipe/MTLXXXXXXX19K0BSXXX/sc_recipe/MTLXXXXXXX19K0BSXXX_CLASS_P68G2_CLASSREBI_MTL_P68G2_HDMT_1.xml'
            f2 = f'{tdir}/astra/astra_hdmx_vc/recipe/MTLXXXXXXX19K0BSXXX/sc_recipe/MTLXXXXXXX19K0BSXXX_CLASS_P68G2_REBI_MTL_P68G2_HDMT_1.xml'
            f3 = f'{tdir}/astra/astra_hdmx_vc/recipe/MTLXXXXXXX19K0BSXXX/sc_recipe/CLASS_P68G2_REBI_MTL_P68G2_HDMT_1.xml'
            File(f1).touch(text, mkdir=True)
            File(f2).touch(text, mkdir=True)
            File(f3).touch(text, mkdir=True)

            RecipeEdit(tpobj).edit_sc_recipe()
            expect = r'''
    <SourcePath>M:\recipe\hdmx\engr\MTL\MTLXXXXXXX19K0BSXXX\CLASS_P68G2_MTL_P68G2_HDMT_1_CLASSREBI_MPS_Manifest_3.xml</SourcePath>
  </ComponentRecipe>
    <SourcePath>M:\recipe\hdmx\engr\MTL\MTLXXXXXXX19K0BSXXX\sc_recipe\CLASS_P68G2_CLASSREBI_MPS_SCrecipe.xml</SourcePath>
</MainManifest>'''
            self.assertTextEqual(File(f1).read(), expect)
            self.assertTextEqual(File(f2).read(), expect)
            self.assertTextEqual(File(f3).read(), text)


class TestMtplNewLine(TestCase):

    @with_(TempDir, chdir=True, delete=True)
    def test_process(self):
        text = '''
Counters
{
        n90280001_fail_VREFTRIM_LJ_CMEM_K_BEGCPUPKG_X_X_VNOM_400_HVM_4,
        n90280101_fail_IREFTRIM_LJ_CMEM_K_BEGCPUPKG_X_X_VNOM_400_HVM_4,
        last
}
Test abc
{
   param = A(
     '',
     '');
   param2 = A('', '');    #
   param3 = A( \\
     '', \\
     '');
}
'''
        File('a.mtpl').touch(text)
        MtplNewLine(None).process('a.mtpl')
        expect = '''
Counters
{
        n90280001_fail_VREFTRIM_LJ_CMEM_K_BEGCPUPKG_X_X_VNOM_400_HVM_4,
        n90280101_fail_IREFTRIM_LJ_CMEM_K_BEGCPUPKG_X_X_VNOM_400_HVM_4,
        last
}
Test abc
{
   param = A(  \\
     '',  \\
     '');
   param2 = A('', '');    #
   param3 = A( \\
     '', \\
     '');
}
'''
        self.assertTextEqual(File('a.mtpl').read(), expect)


class TestPlistEdit(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True, delete=True)
    def test_process(self):
        text = '''<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.plist.ipxml" />
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="a.plist" />
    <PListFile name="b.plist" />
    <PListFile name="c.plist"/>
  </PList>
</HdmtReferenceFile>
'''
        File('all.plist').touch(text)
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env', allpats=True)
        obj = PlistEdit(tpobj)
        data = ['a.plist', 'c.plist', 'b.plist', 'd.plist']
        expect = '''<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.plist.ipxml" />
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="a.plist" />
    <PListFile name="c.plist" />
    <PListFile name="b.plist" />
  </PList>
</HdmtReferenceFile>
'''
        obj.process('all.plist', data)
        self.assertTextEqual(File('all.plist').read(), expect)

        # rerun - no change
        obj.process('all.plist', data)
        self.assertTextEqual(File('all.plist').read(), expect)

        # this should pass
        data = ['a.plist', 'b.plist', 'd.plist']
        obj.process('all.plist', data)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_sorting(self):
        # assumes .process() works
        # assumes .get_plist_dependent() giving correct value
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env', allpats=True)
        obj = PlistEdit(tpobj)

        # case1: b,c,d,e are all same number
        data = OrderedDict([('c.plist', {'a.plist'}),
                            ('a.plist', set()),
                            ('b.plist', {'a.plist'}),
                            ('d.plist', {'a.plist'}),
                            ('e.plist', {'a.plist'})])
        expect = ['a.plist', 'b.plist', 'c.plist', 'd.plist', 'e.plist']
        with MockVar(obj.tpobj.plists, 'get_plist_dependent', Mock(return_value=data)), \
                MockVar(obj, 'process', Mock()):
            self.assertEqual(obj.main(), expect)

        # case2: none specified
        data = OrderedDict([('c.plist', set()),
                            ('a.plist', set()),
                            ('b.plist', set()),
                            ('d.plist', set()),
                            ('e.plist', set())])
        expect = ['a.plist', 'b.plist', 'c.plist', 'd.plist', 'e.plist']
        with MockVar(obj.tpobj.plists, 'get_plist_dependent', Mock(return_value=data)), \
                MockVar(obj, 'process', Mock()):
            self.assertEqual(obj.main(), expect)

        # case3: two dependency
        data = OrderedDict([('a.plist', {'b.plist', 'c.plist'}),
                            ('c.plist', set()),
                            ('b.plist', set()),
                            ('d.plist', set()),
                            ('e.plist', set())])
        expect = ['b.plist', 'c.plist', 'a.plist', 'd.plist', 'e.plist']
        with MockVar(obj.tpobj.plists, 'get_plist_dependent', Mock(return_value=data)), \
                MockVar(obj, 'process', Mock()):
            self.assertEqual(obj.main(), expect)

    def test_call_sherlock(self):
        src = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, startcopy=src, chdir=True, delete=True):  # Set delete=False to debug
            tpobj = TestProgram(Env.get_envfile())
            obj = TorchPostProc()
            self.assertEqual(obj.call_sherlock(tpobj), 0)

            File('POR_TP/TGLH81/InputFiles/disable_sherlock.txt').touch(mkdir=True)
            self.assertEqual(obj.call_sherlock(tpobj), 1)

    def test_call_plistedit(self):
        src = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, startcopy=src, chdir=True, delete=True):  # Set delete=False to debug

            tpobj = TestProgram(Env.get_envfile())
            obj = TorchPostProc()

            # pass case
            with CaptureStdoutLog() as p:
                obj.call_plistedit(tpobj)
            print(p.getvalue)
            self.assertIn('UPDATED:', p.getvalue())

            # fail case
            def fake_main(*args):
                raise ErrorInput("Ooopsie")

            with MockVar(PlistEdit, "main", fake_main):
                with CaptureStdoutLog() as p:
                    obj.call_plistedit(tpobj)
                    obj.final_status()
                print(p.getvalue())
                self.assertIn('Ooopsie', p.getvalue())


class TestCopyTPConfig(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_main(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tpobj.envfile = f'{tdir}/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env'
            File(tpobj.envfile).touch(mkdir=True)
            File(f'{tdir}/ENG_TP/Class_MTL_P68_DEBUG/targetname.stpl').touch()
            File(f'{tdir}/ENG_TP/Class_MTL_P68_DEBUG/Class_MTL_P68.tpconfig').touch('exist')

            CopyTPConfig(tpobj).main()

            expect = r"""  <TestProgramFiles>
    <BaseTplPath>..\..\BaseTestPlan.tpl</BaseTplPath>
    <ENVPath>EnvironmentFile.env</ENVPath>
    <STPLPath>targetname.stpl</STPLPath>
    <PlistPath>..\..\ENG_TP\Class_MTL_P68_DEBUG\PLIST_ALL_CLASS_P68G2.plist.xml</PlistPath>
    <SOCPath>..\..\Shared\BaseInputs\MTL_P68G2_HDMT_1_STA.soc</SOCPath>
    <RootPath>..\..\</RootPath>
    <TPIESignaturePath>..\..\TPIE.Signature</TPIESignaturePath>
  </TestProgramFiles>
"""
            self.assertTextEqual(File(f'{tdir}/ENG_TP/Class_MTL_P68_DEBUG/Class_MTL_P68.tpconfig').read(), expect)

        # POR_TP - no change
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        self.assertEqual(CopyTPConfig(tpobj).main(), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_stpl(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        ctpc = CopyTPConfig(tpobj)
        self.assertEqual(ctpc.get_stpl(['a.stpl']), 'a.stpl')
        self.assertEqual(ctpc.get_stpl(['a.stpl', 'a_g.stpl']), 'a_g.stpl')
        # non found
        with self.assertRaisesRegex(AssertionError, 'Expecting one'):
            ctpc.get_stpl(['a.stpl', 'b.stpl'])
        with self.assertRaisesRegex(AssertionError, 'No stpl found'):
            ctpc.get_stpl([])


class TestMisc(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_copybat(self):
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P28/EnvironmentFile.env')
            tp.tpldir = tdir
            self.assertEqual(Misc(tp).copybat(), 2)
            self.assertEqual(set(os.listdir('.')), {'CachePatterns_MTLP682_new_both.bat', 'CachePatterns_MTLP282.bat'})

            # rerun, should be zero since files is already there
            self.assertEqual(Misc(tp).copybat(), 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True, delete=True)
    def test_npr_mo_pup_del(self):
        tp = TestProgram(f'{UT_DIR}/torch_mvtp/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env')
        self.assertEqual(Misc(tp).npr_mo_pup_del(), 1)  # ENG_TP

        tp = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        self.assertEqual(Misc(tp).npr_mo_pup_del(), 2)  # file not found
        pdir = 'Shared/BaseInputs/Supersedes/MO_PUP'
        File(f'{pdir}/readme.txt').touch(mkdir=True)
        File(f'{pdir}/AA/a.txt').touch(mkdir=True)
        File(f'{pdir}/b.txt').touch(mkdir=True)
        self.assertEqual(Misc(tp).npr_mo_pup_del(), 3)  # success
        self.assertEqual(os.listdir(pdir), ['readme.txt'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tpshainfo(self):
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P28/EnvironmentFile.env')
            tp.envdir = tdir
            data = ('v1', 'v2')
            with MockVar(TorchPostProc, 'repo_sha', data):
                Misc(tp).tpshainfo()
                self.assertEqual(len(File(f'{tdir}/Reports/ToolsRev.txt').read()), 67)

                self.assertEqual(File(f'{tdir}/Reports/RepoRev.txt').read(),
                                 'Repo branch ref: v1\nRepo sha id: v2\n')

    def test_repo_sha(self):
        with TempDir(chdir=True):
            default = ('na', 'na')
            with MockVar(TorchPostProc, 'repo_sha', default):
                # default
                self.assertEqual(TorchPostProc.repo_sha, default)

                # no files
                TorchPostProc.set_repo_sha()
                self.assertEqual(TorchPostProc.repo_sha, ('none', 'not_available_logs_head_not_found'))

                # normal case
                content = '''
f26aa8e3780dd61f303734ee9abc568f979bcfd1 c5e653f82b5c7017dd7daae33dd90368e13e38a8 Delos Reyes, John Q <john.q.delos.reyes@intel.com> 1671331739 -0800   commit: torch_mv [-fast true] enabling, via datahost tar
c5e653f82b5c7017dd7daae33dd90368e13e38a8 720a3e60cba4c4226a15a084615c80629454d8a8 Delos Reyes, John Q <john.q.delos.reyes@intel.com> 1671393425 -0800   commit: generate recipe for full tp
'''
                File('.git/logs/HEAD').touch(content, mkdir=True)
                File('.git/HEAD').touch('ref: refs/heads/JDR/ybs_problem')
                TorchPostProc.set_repo_sha()
                self.assertEqual(TorchPostProc.repo_sha,
                                 ('JDR/ybs_problem', '720a3e60cba4c4226a15a084615c80629454d8a8'))

                # case 2 - specific commit
                File('.git/HEAD').touch('deadbeef', newfile=True)
                TorchPostProc.set_repo_sha()
                self.assertEqual(TorchPostProc.repo_sha, ('deadbeef', '720a3e60cba4c4226a15a084615c80629454d8a8'))

    def test_unzip_PinToChain(self):
        src = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, startcopy=src, chdir=True, delete=True) as tdir:  # Set delete=False to debug
            File(f'{UT_DIR_REPO}/misc_files/LTL_Files.zip').copy('POR_TP/TGLH81/Reports')
            tpobj = TestProgram(Env.get_envfile())
            Misc(tpobj).unzip_PinToChain()
            self.assertTrue(exists('POR_TP/TGLH81/Reports/PinToChainTable.xml'))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_add_ip_PinToChain(self):
        # MTL generate case - real stuff
        with Chdir(f'{UT_DIR}/mtl_torch'):
            with TempDir(name=True) as tdir:
                File('POR_TP/Class_MTL_P68/Reports/PinToChainTable.xml').copy(tdir)
                Misc(None).add_ip_PinToChain(f'{tdir}/PinToChainTable.xml')
                self.assertNotEqual(File(f'{tdir}/PinToChainTable.xml').read(),
                                    File('POR_TP/Class_MTL_P68/Reports/PinToChainTable.xml').read())
                self.assertGoldEqual(f'{tdir}/PinToChainTable.xml',
                                     f'{UT_DIR}/mtl_torch/POR_TP/Class_MTL_P68/Reports/PinToChainTable.xml.gold')

        # Missing PinDefinitions.pin file
        with TempDir(chdir=True):
            self.assertEqual(Misc(None).add_ip_PinToChain(f'{tdir}/PinToChainTable.xml'), 1)


class TestUservar(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_ifengtp(self):
        tp1 = TestProgram(f'{UT_DIR}/torch_mvtp/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env')
        self.assertEqual(UservarEdit([tp1]).ifengtp(), 4)
        tp2 = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        self.assertEqual(UservarEdit([tp2]).ifengtp(), 0)
        self.assertEqual(UservarEdit([tp1, tp2]).ifengtp(), 0)

        with TempDir(chdir=True):
            tp = TestProgram(f'{UT_DIR}/torch_mvtp/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env')
            text = '''
SelectorRule If_ENGTP(yes_mv_tp_value, default)
{
   yes_mv_tp_value => False;
   default;
}
'''
            fs = File('Shared/BaseInputs/UservarDefinitions.usrv').touch(text, mkdir=True)
            tp.shareddir = './Shared'
            self.assertEqual(UservarEdit([tp]).ifengtp(), 101)

            expect = '''
SelectorRule If_ENGTP(yes_mv_tp_value, default)
{
   yes_mv_tp_value => True;
   default;
}
'''
            self.assertTextEqual(fs.read(), expect)

    def test_tpname_sync(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        with TempDir(name=True, chdir=True) as tdir:
            usrv_base = 'Shared/BaseInputs/UservarDefinitions.usrv'
            usrv_package = 'Shared/Package_Shared/UservarDefinitions.usrv'
            text1 = '''
    Const String TPName1 = "basevalue";    # foldername
    Const String blah = "something"
'''
            text2 = '''
    Const String TPName1 = "package";    # foldername
    Const String blah = "something"
'''
            File(usrv_base).touch(text1, mkdir=True)
            File(usrv_package).touch(text2, mkdir=True)
            UservarEdit(tp).tpname_sync()
            self.assertTextEqual(File(usrv_base).read(), text2)


class TestEnv(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_remove_sort_slim(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(chdir=True):
            lines = r"""
TORCH_AUTO_PLIST_PATH = "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\plb;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\plb\slim;" +
    "I:\program\1227\eng\hdmtpats\mtf\MaaaCdrv\RevTCCXXA4.0\p3\plb;" +
    "I:\program\1227\eng\hdmtpats\mtf\MaaaCdrv\RevTCCXXA4.0\p3\plb\slim;" +
    "I:\hdmxpats\mtl\MaaaGdrv\RevTCGXXA2.0\p7\plb;" +
    "I:\hdmxpats\mtl\MaaaGdrv\RevTCGXXA2.0\p7\plb\slim";
TORCH_AUTO_PAT_PATH = "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\common_files;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\indv_bin;" +
    "I:\program\1227\eng\hdmtpats\mtf\MaaaCdrv\RevTCCXXA4.0\p3\pat\common_files;" +
    "I:\program\1227\eng\hdmtpats\mtf\MaaaCdrv\RevTCCXXA4.0\p3\pat\indv_bin;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p2\pat\indv_bin;" +
    "I:\program\1227\eng\hdmtpats\mtf\MaaaCdrv\RevTCCXXA4.0\p2\pat\indv_bin;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p1\pat\indv_bin";
RANDOM = "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\common_files;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\indv_bin;" +
    "I:\program\1227\eng\hdmtpats\mtf\MaaaCdrv\RevTCCXXA4.0\p3\pat\common_files";
"""
            fname = 'a.env'
            File(fname).touch(lines)
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            ee = EnvEdit(tpobj)
            ee.localtp = tpobj

            ee.remove_sort_slim()
            expect = r"""TORCH_AUTO_PLIST_PATH = "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\plb;" +
    "I:\hdmxpats\mtl\MaaaGdrv\RevTCGXXA2.0\p7\plb";

TORCH_AUTO_PAT_PATH = "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\common_files;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\indv_bin;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p2\pat\indv_bin;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p1\pat\indv_bin";

RANDOM = "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\common_files;" +
    "I:\hdmxpats\mtl\MaaaCdrv\RevTCCXXA4.0\p3\pat\indv_bin;" +
    "I:\program\1227\eng\hdmtpats\mtf\MaaaCdrv\RevTCCXXA4.0\p3\pat\common_files";
"""
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_pobj_soc_sha(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(chdir=True):
            lines = r"""
HDST_PAT_PATH =
 "I:\hdmxpats\mtl\Mtvpv\RevTCCXXA0.0\p1\pat\35cde96480bc;"+
 "I:\program\1227\eng\hdmtpats\mtf\Mtvpv\RevTCCXXA0.0\p1\pat\35cde96480bc;"+
 "I:\hdmxpats\mtl\Mtvpv\RevTCCXXA0.0\p1\pat\common_files;"+
 "I:\program\1227\eng\hdmtpats\mtf\Mtvpv\RevTCCXXA0.0\p1\pat\common_files;"+
 "I:\hdmxpats\mtl\Mtvpv\RevTCCXXA0.0\p1\pat\indv_bin;"+
 "I:\hdmxpats\mtl\Mtvpv\RevTCCXXA0.0\p0\pat\indv_bin;"+
 "I:\program\1227\eng\hdmtpats\mtf\Mtvpv\RevTCCXXA0.0\p1\pat\indv_bin;"+
 "I:\program\1227\eng\hdmtpats\mtf\Mtvpv\RevTCCXXA0.0\p0\pat\indv_bin";
   OTHER = "other";
"""
            fname = 'a.env'
            File(fname).touch(lines)
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            ee = EnvEdit(tpobj)
            ee.localtp = tpobj

            ee.pobj_soc_sha()
            expect = r"""HDST_PAT_PATH = "I:\hdmxpats\mtl\Mtvpv\RevTCCXXA0.0\p1\pat\common_files;" +
    "I:\program\1227\eng\hdmtpats\mtf\Mtvpv\RevTCCXXA0.0\p1\pat\common_files;" +
    "I:\hdmxpats\mtl\Mtvpv\RevTCCXXA0.0\p1\pat\indv_bin;" +
    "I:\hdmxpats\mtl\Mtvpv\RevTCCXXA0.0\p0\pat\indv_bin;" +
    "I:\program\1227\eng\hdmtpats\mtf\Mtvpv\RevTCCXXA0.0\p1\pat\indv_bin;" +
    "I:\program\1227\eng\hdmtpats\mtf\Mtvpv\RevTCCXXA0.0\p0\pat\indv_bin";

OTHER = "other";
"""
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_npr(self):
        # special case: NPR_FOLDER_PATH
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(chdir=True):
            lines = r"""
NPR_FOLDER_PATH = "~HDMT_TPL_DIR\Shared\BaseInputs\Supersedes\MO_PUP\;" +
     "I:\ulat\pup\release\mtl\MTLXXA2H19M\";
ABC = "a;b;c";
"""
            fname = 'a.env'
            File(fname).touch(lines)
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            ee = EnvEdit(tpobj)
            ee.localtp = tpobj

            expect = r"""NPR_FOLDER_PATH = "~HDMT_TPL_DIR\Shared\BaseInputs\Supersedes\MO_PUP\;I:\ulat\pup\release\mtl\MTLXXA2H19M\";

ABC = "a;" +
    "b;" +
    "c";
"""
            self.assertTextEqual(ee.rebuild(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_delete_var(self):
        with TempDir(chdir=True):
            lines = """
    CASE1 = "path1" + "path2";
    CASE2 =
          "path3";
"""
            fname = 'POR_TP/something/a.env'
            File(fname).touch(lines, newfile=True, mkdir=True)
            tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            ee = EnvEdit(tpobj)
            ee.localtp = tpobj

            # success case
            self.assertEqual(ee.delete_var('CASE1', 'POR_TP'), 3)
            expect = """CASE2 = "path3";
"""
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

            # incorrect TP case
            tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            ee = EnvEdit(tpobj)
            ee.localtp = tpobj
            File(fname).touch(lines, newfile=True, mkdir=True)
            self.assertEqual(ee.delete_var('CASE1', 'ENG_TP'), 1)
            expect = """CASE1 = "path1path2";

CASE2 = "path3";
"""
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

            # var not found
            self.assertEqual(ee.delete_var('CASE3', 'POR_TP'), 2)
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_remove_auto(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(chdir=True):
            lines = """
    CASE1 =
          "path_case1";
    HDST_CASE1_PATH = "$CASE1";

    CASE2 =
          "path_case1;" +
          "path_case2";
    HDST_CASE2_PATH =
             "$CASE2";

"""
            fname = 'a.env'
            File(fname).touch(lines)
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            ee = EnvEdit(tpobj)
            ee.localtp = tpobj

            ee.remove_auto('CASE1')
            ee.remove_auto('CASE2')
            expect = """HDST_CASE1_PATH = "path_case1";

HDST_CASE2_PATH = "path_case1;" +
    "path_case2";
"""
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(chdir=True):
            lines = """
CASE1 = "path_case1";
HDST_CASE1_PATH = "path;" +
                "$CASE1";

CASE2 = "path1;" +
        "path2";
HDST_CASE2_PATH = "path;" +
                "$CASE2";

# something

CASE3 = "single_line1";
HDST_CASE3_PATH = "$CASE3";

CASE4 = "path1a;" +
        "path2a";
HDST_CASE4_PATH = "$CASE4";
"""
            fname = 'a.env'
            File(fname).touch(lines)
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            ee = EnvEdit(tpobj)
            ee.localtp = tpobj

            ee.remove_auto('CASE1')
            ee.remove_auto('CASE2')
            ee.remove_auto('CASE3')
            ee.remove_auto('CASE4')

            expect = """HDST_CASE1_PATH = "path;" +
    "path_case1";

HDST_CASE2_PATH = "path;" +
    "path1;" +
    "path2";

# something
HDST_CASE3_PATH = "single_line1";

HDST_CASE4_PATH = "path1a;" +
    "path2a";
"""
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

            # no change case
            self.assertTextEqual(ee.localtp.env.rebuild(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_remove_aleph_integ(self):
        # Test Strategy of "remove_aleph"
        # 1. test_integration: Confirms that routine is called
        # 2. test_remove_aleph_integ: Confirms that full TP is unedited and mv TP is edited
        # 3. test_remove_aleph_ut: Confirms that it is doing the intended thing (True unittest)

        # Unittest (since we are not reading or writing .env file), but full run
        # full tp
        tp = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        tp.env.set_env()
        ee = EnvEdit(tp)
        self.assertEqual(len(ee.localtp.env.get_item('ALEPH_FILES', islist=True)), 155)
        ee.remove_aleph()
        self.assertEqual(len(ee.localtp.env.get_item('ALEPH_FILES', islist=True)), 155)  # no edits

        # mv tp
        tp = TestProgram(f'{UT_DIR}/torch_mvtp/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env')
        tp.env.set_env()
        ee = EnvEdit(tp)
        self.assertEqual(len(ee.localtp.env.get_item('ALEPH_FILES', islist=True)), 119)
        ee.remove_aleph()
        self.assertEqual(len(ee.localtp.env.get_item('ALEPH_FILES', islist=True)), 62)  # with edits

    def test_pup_module_input(self):
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True, chdir=True):
            shutil.copytree(src, f'./TPL')
            text = r'''
NPR_FOLDER_PATH = "~HDMT_TPL_DIR\Shared\BaseInputs\Supersedes\MO_PUP\;I:\ulat\pup\release\mtl\<ULAT_PUP_TPNAME_REV>\";
PUP_MODULE_INPUTS = ".\\Supersedes\\MO_PUP\\CLASS_P68G2\\PAS_PTD.pup.json";
'''
            File(f'TPL/POR_TP/TGLH81/EnvironmentFile.env').touch(text)
            ee = EnvEdit(TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env'))

            fn1 = 'Modules/TPI_PUP_XXX/a.mtpl'  # 1st bom
            fn2 = 'Modules/TPI_PUP_XXX/b.mtpl'  # 2nd bom
            orig = 'a = "~PUP_MODULE_INPUTS";\nsomeline;\n'
            File(fn1).touch(orig, mkdir=True)
            File(fn2).touch('none;\n', mkdir=True)
            ee.pup_module_input()
            expect = r'''a = ".\\Supersedes\\MO_PUP\\CLASS_P68G2\\PAS_PTD.pup.json";
someline;
'''
            self.assertTextEqual(File(fn1).read(), expect)
            self.assertTextEqual(File(fn2).read(), 'none;\n')

    def test_pup_ulat_tpname(self):
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True, chdir=True):
            shutil.copytree(src, f'./TPL')
            # env file
            text = '''
PUP_PATTERNS_DIR = "blah/<ULAT_PUP_TPNAME_REV>/bro";
NPR_FOLDER_PATH = "/p/<ULAT_PUP_TPNAME_REV>/<ULAT_PUP_TPNAME_REV>";
HASH_PATH = "blah/HASH_<ULAT_PUP_TPNAME_REV>/bro";
AB = "no change";
'''
            env = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            File(env).touch(text, newfile=True)
            # usrv file
            text = '''
UserVars TPNameVars
{
    String TPName1 = TpRule.TpNames("MTLPBX7A6H20C00S224","MTLPCX7A6H20C00S224");
}
'''
            File('Shared/Package_Shared/UservarDefinitions.usrv').touch(text, mkdir=True)
            ee = EnvEdit(TestProgram(env))
            ee.pup_ulat_tpname()
            dd = ee.localtp.env.get_env_dict()
            self.assertTextEqual(dd['PUP_PATTERNS_DIR'], 'blah/MTLXXA6H20C00/bro')
            self.assertTextEqual(dd['NPR_FOLDER_PATH'], '/p/MTLXXA6H20C00/MTLXXA6H20C00')
            self.assertTextEqual(dd['HASH_PATH'], 'blah/HASH_MTLXXA6H20C00/bro')

    @unittest.skip("Not needed")
    def test_pup_ulat_tpname2(self):
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True, chdir=True):
            shutil.copytree(src, f'./TPL')
            # env file
            text = '''
PUP_PATTERNS_DIR = "blah/<ULAT_PUP_TPNAME_REV>/bro";
NPR_FOLDER_PATH = "/p/<ULAT_PUP_TPNAME_REV>/<ULAT_PUP_TPNAME_REV>";
AB = "no change";
'''
            env = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            File(env).touch(text, newfile=True)
            # usrv file
            text = '''
UserVars TPNameVars
{
    String TPName2 = TpRule.TpNames("MTLPBX7A6H20C00S224","MTLPCX7A6H20C00S224");
}
'''
            File('Shared/Package_Shared/UservarDefinitions.usrv').touch(text, mkdir=True)
            ee = EnvEdit(TestProgram(env))
            ee.pup_ulat_tpname()
            dd = ee.localtp.env.get_env_dict()
            self.assertTextEqual(dd['PUP_PATTERNS_DIR'], 'blah/MTLXXA6H20C00/bro')
            self.assertTextEqual(dd['NPR_FOLDER_PATH'], '/p/MTLXXA6H20C00/MTLXXA6H20C00')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_pup_engg_fulltp(self):
        with TempDir(name=True, chdir=True) as tdir:
            ee = EnvEdit(TestProgram(f'{UT_DIR}/Simple3/POR_TP/TGLH81/EnvironmentFile.env'))
            ez = EnvEdit(TestProgram(f'{UT_DIR}/torch_mvtp_pass/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env'))
            # non exist case
            self.assertEqual(ee._pup_engg_fulltp('38C0Z', path=tdir), '38C0Z')

            # exist case
            File('38C0A').touch()
            File('38C0B').touch()
            File('38C0Z').touch()
            self.assertEqual(ee._pup_engg_fulltp('38C0Z', path=tdir), '38C0B')
            self.assertEqual(ee._pup_engg_fulltp('38C0C', path=tdir), '38C0C')
            self.assertEqual(ez._pup_engg_fulltp('38C0Z', path=tdir), '38C0B')

        with TempDir(name=True, chdir=True) as tdir:
            File('38C0Z').touch()
            self.assertEqual(ee._pup_engg_fulltp('38C0Z', path=tdir), '38C0Z')
            self.assertEqual(ee._pup_engg_fulltp('38C0C', path=tdir), '38C0C')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_remove_aleph_ut(self):
        # _is_valid_patmodify_path()
        tp = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        tp.env.set_env()
        ee = EnvEdit(tp)
        ee._map_cm = {'mdrv': {'MODA', 'MODB'},
                      'mscn': {'MODC', 'MODD'},
                      'marr': {'MODE', 'MODF'}}
        # both modules are in
        self.assertEqual(ee._is_valid_patmodify_path('/mtl/mdrv/RevA/p3', {'MODA', 'MODB'}), True)
        # one module is in
        self.assertEqual(ee._is_valid_patmodify_path('/mtl/mdrv/RevA/p3', {'MODA'}), True)
        # no module is in
        self.assertEqual(ee._is_valid_patmodify_path('/mtl/mdrv/RevA/p3', {'MODC', 'MODD'}), False)

        # remove aleph()
        mods_in_tp = ['MODA', 'MODB']
        aleph = ('.\\Modules\\MODA\\InputFiles\\a.json;'
                 '.\\Modules\\Shared\\MODB\\AlephFiles\\b.json;'
                 '.\\Modules\\MODC\\InputFiles\\c.json;'
                 '.\\Modules\\Shared\\MODD\\AlephFiles\\d.json;'
                 '$A_PATMODIFY_PATH\\keep;'
                 '$C_PATMODIFY_PATH\\keep'
                 )
        ee.localtp.env._env_dict = {'ALEPH_FILES': aleph,
                                    'RANDOM': aleph,
                                    'A_PATMODIFY_PATH': '/mtl/mdrv/RevA/p3',
                                    'C_PATMODIFY_PATH': '/mtl/mscn/RevA/p3'}
        with MockVar(ee.tpobj, 'get_module_folder_names', Mock(return_value=mods_in_tp)):
            ee.remove_aleph()
        pprint(ee.localtp.env._env_dict)
        expect = {
            'ALEPH_FILES': '.\\Modules\\MODA\\InputFiles\\a.json;.\\Modules\\Shared\\MODB\\AlephFiles\\b.json;$A_PATMODIFY_PATH\\keep',
            'A_PATMODIFY_PATH': '/mtl/mdrv/RevA/p3',
            'C_PATMODIFY_PATH': '/mtl/mscn/RevA/p3',
            'RANDOM': aleph}  # unedited
        self.assertEqual(ee.localtp.env._env_dict, expect)


class TestPostProc(TestCase):

    def test_basic(self):
        src = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, startcopy=src, chdir=True, delete=True) as tdir:  # Set delete=False to debug
            with CaptureStdoutLog() as p:
                TorchPostProc().main()
            print(p.getvalue())

            # CopyTPConfig is called
            # self.assertIn('-i- Skipping CopyTPConfig', p.getvalue())
            # EnvReorder is called
            self.assertIn('for latest subroutine order', p.getvalue())
            # parallel flow is called
            self.assertIn('-i- intradut_flows.json', p.getvalue())
            # BinHack is called
            self.assertIn('is updated by BinHack', p.getvalue())
            # remove_aleph is called
            self.assertIn('Starting Env Edit for unneeded aleph lines', p.getvalue())
            # ifengtp is called
            self.assertIn('ifengtp() is skipped due to POR_TP', p.getvalue())
            # pup_module_input is called
            self.assertIn('PUP_MODULE_INPUTS is', p.getvalue())
            self.assertIn('PUP_PATTERNS_DIR is not found in env', p.getvalue())
            # sherlock is called
            self.assertIn('END of Sherlock messages', p.getvalue())
            # bdeffix is called
            self.assertIn('BdefFix() with Share/unshare bin update', p.getvalue())
            # ToolsRev.txt is created
            self.assertEqual(len(File('POR_TP/TGLH81/Reports/ToolsRev.txt').read().strip()), 66)
            # NPRTrigger is called
            self.assertIn('NPRTrigger is skipped', p.getvalue())

            print("Rerunning====================")
            with CaptureStdoutLog() as p:
                TorchPostProc().main(bdeffix=False)

            # Don't call bdef fix
            self.assertNotIn('BdefFix() with Share/unshare bin update', p.getvalue())

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @with_(MockVar, UservarEdit, 'tpname_sync', Mock())
    def test_integration(self):
        # Tests MTT expand
        # Checks if postprocess routines are called
        # Other postprocess output are not checked here
        src = f'{UT_DIR}/mtt_tp'
        with TempDir(name=True, startcopy=src, chdir=True, delete=True) as tdir:  # Set delete=False to debug
            with CaptureStdoutLog() as p:
                TorchPostProc().main()

            # two domain case
            target1 = 'Modules/FUN_ATOM_CXX/FUN_ATOM_CXX_CLASS_P68G2_CLASS_P68G2_g.mtpl'
            expect1 = f'{UT_DIR}/mtt_tp/{target1}.gold4'
            self.assertGoldEqual(target1, expect1)

            # EDC unused case
            target = 'Modules/SCN_CCF_C68/SCN_CCF_C68_CLASS_P68G2_CLASS_P68G2_g.mtpl'
            self.assertGoldEqual(target, f'{UT_DIR}/mtt_tp/{target}.gold5')

            # with EDC case
            target = 'Modules/SCN_CORE_C68/SCN_CORE_C68_CLASS_P68G2_CLASS_P68G2_g.mtpl'
            self.assertGoldEqual(target, f'{UT_DIR}/mtt_tp/{target}.gold5')

            # plist ordering
            target = 'POR_TP/Class_MTL_P68/PLIST_ALL_CLASS_P68G2.plist.xml'
            self.assertGoldEqual(target, f'{UT_DIR}/mtt_tp/{target}.gold2')

            # env file
            target2 = 'POR_TP/Class_MTL_P68/EnvironmentFile.env'
            expect2 = f'{UT_DIR}/mtt_tp/{target2}.gold6'
            self.assertGoldEqual(target2, expect2)

            # rerun =================================
            print("Rerunning====================")
            with CaptureStdoutLog() as p:
                TorchPostProc().main(bdeffix=False)
            self.assertGoldEqual(target1, expect1)  # FUN_ATOM_CXX
            self.assertGoldEqual(target2, expect2)  # EnvironmentFile.env

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_integration_mv(self):
        # Checks if MV (ENG_TP) is success.
        # Below unittest directory can be modified further if there are required postprocess outputs
        src = f'{UT_DIR}/torch_mvtp_pass'
        with TempDir(name=True, delete=True) as tdir:
            shutil.copytree(src, f'{tdir}/tp')
            with Chdir(f'{tdir}/tp'), CaptureStdoutLog() as p:
                TorchPostProc().main()
            print(p.getvalue())

            # Make sure it completed successfully
            self.assertIn('torch_postproc is done', p.getvalue())
            # Make sure sherlock message output
            self.assertIn('Sherlock REPORT: ./ENG_TP/Class_MTL_P68_DEBUG/Reports/ERRORS_Checkers_Report.txt',
                          p.getvalue())

    def test_startup_check(self):
        with TempDir(name=True, chdir=True) as tdir:
            # first check
            with self.assertRaisesRegex(ErrorUser, 'BaseTestPlan.tpl is not found'):
                TorchPostProc().main()

            File('BaseTestPlan.tpl').touch()
            with MockVar(os.environ, "LC_ALL", "C"):
                with self.assertRaisesRegex(ErrorUser, 'unsetenv LC_ALL'):
                    TorchPostProc().main()

            with self.assertRaisesRegex(ErrorUser, 'only works with torch testprograms'):
                TorchPostProc().main()

            # call_trc - pass
            obj = TorchPostProc()
            with MockVar(TraceTrc, "main", Mock(return_value=False)):
                with CaptureStdoutLog() as p:
                    obj.call_trc()
                    obj.final_status()
                print(p.getvalue())
                self.assertIn('SUCCESS', p.getvalue())

            # call_trc - fail
            obj = TorchPostProc()
            with MockVar(TraceTrc, "main", Mock(return_value=True)):
                with CaptureStdoutLog() as p:
                    obj.call_trc()
                    obj.final_status()
                print(p.getvalue())
                self.assertIn('TRC check was not performed', p.getvalue())

    def test_custom_scripts(self):
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                obj = TorchPostProc()
                tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')

                # without script
                with CaptureStdoutLog() as p:
                    obj.custom_scripts(tpobj.envfile, 'buildpost_*')
                self.assertEqual(p.getvalue(), '')

                # with script
                code = r"""#!{exe} -u
print("Success")
""".format(exe=sys.executable)
                File(f'POR_TP/TGLH81/Scripts/buildpost_a.py').touch(code, mkdir=True).chmod('02775')
                with CaptureStdoutLog() as p:
                    obj.custom_scripts(tpobj.envfile, 'buildpost_*')

                result = p.getvalue().replace(tdir, '')
                expect = f"""-i- START: Custom Script: /TPL/POR_TP/TGLH81/Scripts/buildpost_a.py
CMD: {sys.executable} /TPL/POR_TP/TGLH81/Scripts/buildpost_a.py /TPL/POR_TP/TGLH81/EnvironmentFile.env
===== Stdout+Stderr:
Success
===end of stdout+stderr===
"""
                self.assertTextEqual(result.replace("\\", "/"), expect.replace("\\", "/"))

    def test_cleantp_call(self):
        # unittest to cover a called cleantp
        env = f'{UT_DIR_REPO}/Simple3a_mtt/POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(name=True, chdir=True), MockVar(CleanTP, 'main', Mock()):
            obj = TorchPostProc()
            File('Shared/BaseInputs/InputFiles/cleantp_enable.txt').touch(mkdir=True)
            self.assertEqual(obj.call_cleantp(env), 1)


class TestMTT(TestCase):

    def test_basic(self):
        src = f'{UT_DIR_REPO}/Simple3a_mtt'
        with TempDir(name=True, startcopy=src, chdir=True, delete=True) as tdir:  # Set delete=False to debug
            tp = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
            MTTExpand(tp).main()

            target1 = 'Modules/ARRX/FUN_ATOM_CXX.mtpl'
            expect1 = f'{UT_DIR_REPO}/Simple3a_mtt/{target1}.gold'
            self.assertGoldEqual(target1, expect1)

            target1 = 'Modules/SCNX/FUN_CCF_C68.mtpl'
            expect1 = f'{UT_DIR_REPO}/Simple3a_mtt/{target1}.gold'
            self.assertGoldEqual(target1, expect1)

            File('POR_TP/TGLH81/InputFiles/no_mtt_expand.settings.txt').touch(mkdir=True)
            self.assertEqual(MTTExpand(tp).main(), 2)

    def test_add_blocks(self):
        me = MTTExpand(None)
        lines = '''Version 1;
some block {
   blah
}
DUTFlow SBFT_VMAX_F1
{
    blah
}
'''
        flines = [f'{x}\n' for x in lines.split('\n')]
        me.nflows = '1 2'.split()
        alines, adom = me.add_blocks(flines, {'CORE', 'RING'}, 'ARR')
        self.assertEqual(adom, {'fc': {'FlowControl_RING', 'FlowControl_CORE'},
                                'sf': {'SetFlowInfo_CORE_Flow', 'SetFlowInfo_RING_Flow'}})
        result = ''.join(alines)

        expect = '''Version 1;
some block {
   blah
}
Test PrimeFlowControlForkTestMethod FlowControl_CORE
{
    DomainName = "CORE";
}
Test PrimeFlowControlSetTestMethod SetFlowInfo_CORE_Flow1
{
    DomainName = "CORE";
    DomainValue = 1;
}
Test PrimeFlowControlSetTestMethod SetFlowInfo_CORE_Flow2
{
    DomainName = "CORE";
    DomainValue = 2;
}
Test PrimeFlowControlForkTestMethod FlowControl_RING
{
    DomainName = "RING";
}
Test PrimeFlowControlSetTestMethod SetFlowInfo_RING_Flow1
{
    DomainName = "RING";
    DomainValue = 1;
}
Test PrimeFlowControlSetTestMethod SetFlowInfo_RING_Flow2
{
    DomainName = "RING";
    DomainValue = 2;
}
DUTFlow SBFT_VMAX_F1
{
    blah
}

'''
        self.assertTextEqual(result, expect)

        # FUN_ATOM_CXX
        alines, adom = me.add_blocks(flines, {'CORE', 'RING'}, 'FUN_ATOM_CXX/FUN_ATOM_CXX.mtpl')
        self.assertEqual(adom, {'fc': {'FlowControl_RING', 'FlowControl_CORE'},
                                'sf': {'SetFlowInfo_CORE_Flow'}})
        result = ''.join(alines)

        expect = '''Version 1;
some block {
   blah
}
Test PrimeFlowControlForkTestMethod FlowControl_CORE
{
    DomainName = "CORE";
}
Test PrimeFlowControlSetTestMethod SetFlowInfo_CORE_Flow1
{
    DomainName = "CORE";
    DomainValue = 1;
}
Test PrimeFlowControlSetTestMethod SetFlowInfo_CORE_Flow2
{
    DomainName = "CORE";
    DomainValue = 2;
}
Test PrimeFlowControlForkTestMethod FlowControl_RING
{
    DomainName = "RING";
}
DUTFlow SBFT_VMAX_F1
{
    blah
}

'''
        self.assertTextEqual(result, expect)

        # SCN_CCF_C68
        alines, adom = me.add_blocks(flines, {'RING', 'RING_EDC'}, 'SCN_CCF_C68/SCN_CCF_C68.mtpl')
        self.assertEqual(adom, {'fc': {'FlowControl_RING', 'FlowControl_RING_EDC'},
                                'sf': {'SetFlowInfo_RING_Flow'}})
        result = ''.join(alines)
        self.assertTextEqual(result, expect.replace('RING', 'RING_EDC').replace('CORE', 'RING'))

    def test_set_map_remove(self):
        with TempDir(name=True, chdir=True):
            fname = 'Shared/BaseInputs/mtt_map_remove.json'
            text = '''[
["SCN_CORE_C68", "CORE_EDC"],
["SCN_CORE_C28", "CORE_EDC"]
]
'''
            File(fname).touch(text, mkdir=True)
            me = MTTExpand(None)
            self.assertEqual(me.map_remove, {('SCN_CORE_C28', 'CORE_EDC'), ('SCN_CORE_C68', 'CORE_EDC')})

    def test_set_mapping(self):
        with TempDir(name=True, chdir=True):
            fname = 'Shared/BaseInputs/mtt_mapping.json'
            text = '''[
["FUN_ATOM_CXX", {"ATOMC": "!_VCC",
                  "RING": "_VCC"}],
["SCN_CCF_C68", {"RING": "!_EDC$",
                 "RING_EDC": "_EDC$"}]
]
'''
            File(fname).touch(text, mkdir=True)
            me = MTTExpand(None)
            pprint(me.mapping)
            self.assertEqual(me.mapping, OrderedDict([('FUN_ATOM_CXX', {'ATOMC': '!_VCC', 'RING': '_VCC'}),
                                                      ('SCN_CCF_C68', {'RING': '!_EDC$', 'RING_EDC': '_EDC$'})]))

    def test_replace_return_1_only(self):
        me = MTTExpand(None)
        lines = '''
        DUTFlowItem SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO FlowControl_ATOMC
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90990001_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -2;
                }
        }
        DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO FlowControl_ATOMC
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90990001_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -2;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90980001_fail_FAIL_SYSTEM_SOFTWARE;
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -2;
                }
        }
        DUTFlowItem SetFlowInfo_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO FlowControl_ATOMC
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90990001_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -2;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90980001_fail_FAIL_SYSTEM_SOFTWARE;
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -2;
                }
        }
'''
        expect = '''
        DUTFlowItem SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO FlowControl_ATOMC
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90990001_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -2;
                }
        }
        DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO FlowControl_ATOMC
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90990001_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -1;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90980001_fail_FAIL_SYSTEM_SOFTWARE;
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -2;
                }
        }
        DUTFlowItem SetFlowInfo_SBFT_ATOM_VMIN_K_MAXAT_X_VATOM_F1_AT_F1_FREQ_BILBO FlowControl_ATOMC
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90990001_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -1;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        IncrementCounters FUN_ATOM_CXX::n90980001_fail_FAIL_SYSTEM_SOFTWARE;
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -2;
                }
        }

'''
        flines = [f'{x}\n' for x in lines.split('\n')]
        self.assertTextEqual(''.join(me.replace_return_1_only(flines)), expect)

    def test_is_edc_line(self):
        me = MTTExpand(None)
        self.assertEqual(
            me.is_edc_line('DUTFlowItem FlowControl_TATPG_CORE_VMIN_E_SCRF6_X_VCORE_F6_X_CORE1_EDC FlowControl'),
            True)
        self.assertEqual(
            me.is_edc_line('DUTFlowItem FlowControl_TATPG_CORE_VMIN_E_SCRF6_X_VCORE_F6_X_CORE1 FlowControl'),
            False)
        self.assertEqual(me.is_edc_line('DUTFlowItem FlowControl_BGFBIST_X_VMIN_K_ENDGT_X_VCCGT_F1_100 FlowControl'),
                         True)

    def test_replace_dutflowitems(self):
        me = MTTExpand(None)
        lines = '''Version 1;

  DUTFlowItem SetFlowInfo_TATPG_CORE_VMIN_K_SCRF6_X_VCORE_F6_X_CORE5_P5_Flow2 SetFlowInfo_Flow2
  DUTFlowItem FlowControl_TATPG_CORE_VMIN_E_SCRF6_X_VCORE_F6_X_CORE1_EDC FlowControl

  DUTFlowItem CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS
'''
        flines = [f'{x}\n' for x in lines.split('\n')]
        adom = {'fc': {'FlowControl_RING'},
                'sf': {'SetFlowInfo_RING_Flow'}}
        domains = {'ATOMC': '_VCC', 'RING': '!_VCC'}
        alines = me.replace_dutflowitems(flines, adom, '/na/na/na.mtpl', domains)
        result = ''.join(alines)

        expect = '''Version 1;

        DUTFlowItem SetFlowInfo_TATPG_CORE_VMIN_K_SCRF6_X_VCORE_F6_X_CORE5_P5_Flow2 SetFlowInfo_RING_Flow2
        DUTFlowItem FlowControl_TATPG_CORE_VMIN_E_SCRF6_X_VCORE_F6_X_CORE1_EDC FlowControl_RING

  DUTFlowItem CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS

'''
        self.assertTextEqual(result, expect)

    def test_replace_dutflowitems2(self):
        me = MTTExpand(None)
        lines = '''Version 1;

  DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_SATF3_X_VATOM_F3_1400_L2_LEGACY FlowControl
  DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_SATF3_X_VCCF_F3_1400_L2_LEGACY FlowControl

  DUTFlowItem CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS
'''
        flines = [f'{x}\n' for x in lines.split('\n')]
        adom = {'fc': {'FlowControl_RING', 'FlowControl_ATOMC'},
                'sf': {'SetFlowInfo_RING_Flow', 'SetFlowInfo_ATOMC_Flow'}}
        domains = {'ATOMC': '!_VCC', 'RING': '_VCC'}
        alines = me.replace_dutflowitems(flines, adom, '/na/FUN_ATOM_CXX/na.mtpl', domains)
        result = ''.join(alines)

        expect = '''Version 1;

        DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_SATF3_X_VATOM_F3_1400_L2_LEGACY FlowControl_ATOMC
        DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_SATF3_X_VCCF_F3_1400_L2_LEGACY FlowControl_RING

  DUTFlowItem CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS

'''
        self.assertTextEqual(result, expect)

    def test_replace_dutflowitems3(self):
        me = MTTExpand(None)
        # FlowControl
        lines = '''Version 1;

  DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_SATF3_X_VATOM_F3_1400_L2_LEGACY FlowControl
  DUTFlowItem FlowControl_SBFT_ATOM_VMIN_K_SATF3_X_VCCF_F3_1400_L2_LEGACY FlowControl

  DUTFlowItem CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS
'''
        flines = [f'{x}\n' for x in lines.split('\n')]
        adom = {'fc': {'FlowControl_RING', 'FlowControl_ATOMC'},
                'sf': {'SetFlowInfo_RING_Flow', 'SetFlowInfo_ATOMC_Flow'}}
        domains = {'ATOMC': 'BLAHBLAH', 'RING': 'BLAHBLAH'}
        with self.assertRaisesRegex(ErrorInput, 'Cannot determine'):
            me.replace_dutflowitems(flines, adom, '/na/NA/na.mtpl', domains)

        # SetFlowInfo
        lines = '''Version 1;

  DUTFlowItem SetFlowInfo_TATPG_CORE_VMIN_K_SCRF6_X_VCORE_F6_X_CORE5_P5_Flow2 SetFlowInfo_Flow2
  DUTFlowItem CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS CTRL_X_AUX_E_SCRF4_X_X_X_X_BYPASS
'''
        flines = [f'{x}\n' for x in lines.split('\n')]
        with self.assertRaisesRegex(ErrorInput, 'Cannot determine'):
            me.replace_dutflowitems(flines, adom, '/na/NA/na.mtpl', domains)

    def test_get_domains(self):
        with TempDir(name=True) as tdir:
            text = 'Version1;\n\n\n'

            # not found in mapping
            File(f'{tdir}/blah.mtpl').touch(text)
            self.assertEqual(MTTExpand(None).get_domains(f'{tdir}/blah.mtpl'), None)

            # found in mapping, but no instance
            File(f'{tdir}/FUN_ATOM_CXX.mtpl').touch(text)
            self.assertEqual(MTTExpand(None).get_domains(f'{tdir}/FUN_ATOM_CXX.mtpl'), None)
            self.assertEqual(set(MTTExpand(None).get_domains(f'{tdir}/FUN_ATOM_CXX.mtpl', check_only=True)),
                             {'ATOMC', 'RING'})

            # no mapping, w/ instance
            text = 'Version1;\n Test iCBinMatrixFlowControlTest something\n\n'
            File(f'{tdir}/blah.mtpl').touch(text, newfile=True)
            with self.assertRaisesRegex(ErrorCockpit, 'but no mapping defined'):
                MTTExpand(None).get_domains(f'{tdir}/blah.mtpl')

            # w/ mapping, w/ isntance
            File(f'{tdir}/FUN_ATOM_CXX.mtpl').touch(text, newfile=True)
            self.assertEqual(set(MTTExpand(None).get_domains(f'{tdir}/FUN_ATOM_CXX.mtpl')),
                             {'ATOMC', 'RING'})

    def test_get_domains_check_reftp(self):
        orig = {}
        new = {}
        robj = re.compile(r'DomainName = "(\w+)"', re.MULTILINE)
        # tp_reference = '/intel/hdmxprogs/mtl/MTLXXXXAXH18B00S208/TPL/Modules/*/*P68*.mtpl'
        tp_reference = '/intel/hdmxprogs/mtl/MTLXXXXAXH19G00S217/TPL/Modules/*/*P68*.mtpl'
        for mtpl in glob.glob(tp_reference):
            print(f'Processing {mtpl}')
            alldom = set(robj.findall(File(mtpl).read()))
            mname = basename(dirname(mtpl))
            if mname.startswith(
                    ('TPI_EVMINS_', 'TPI_PBMFC_', 'TPI_BASEPRIM')):  # special, there is no mapping for these
                continue
            if mname.startswith(('SCN_GT_GXX', 'SCN_ATOM_CXX')):  # special according to Patrick
                continue

            if alldom:
                orig[mname] = alldom

                # torch
                with open(mtpl) as fh:
                    flines = list(fh)

                domains = MTTExpand(None).get_domains(mtpl, check_only=True)
                if domains:
                    MTTExpand.edc_domains(flines, domains)
                    new[mname] = set(domains)

        self.maxDiff = None
        self.assertEqual(orig, new)

    def test_remove_evg_blocks(self):
        text = '''
Test abc {
  123
}

Test iCBinMatrixFlowControlTest SetFlowInfo_Flow1
{
        active_bingroup_uservar = "BOMGroups.CLASS_P68G2";
        operating_mode = "SET_FLOW_INFO";
}

Test ghi {
  123
}

Test iCBinMatrixFlowControlTest SetFlowInfo_Flow1
{
        active_bingroup_uservar = "BOMGroups.CLASS_P68G2";
        operating_mode = "SET_FLOW_INFO";
}
'''.split('\n')
        result = list(MTTExpand.remove_evg_blocks(text))
        expect = '''
Test abc {
  123
}


Test ghi {
  123
}

'''
        self.assertTextEqual('\n'.join(result), expect)

    def test_add_import_line(self):
        # as-is
        text = '''
Import blah1;
Import PrimeFlowControlForkTestMethod.xml;
Import PrimeFlowControlSetTestMethod.xml;
end;
'''
        flines = [f'{x}\n' for x in text.split('\n')]
        result = list(MTTExpand.add_import_line(flines, 'test1'))
        self.assertTextEqual(''.join(result), ''.join(flines))

        # Both missing
        text = '''
Import blah1;
end;
'''
        flines = [f'{x}\n' for x in text.split('\n')]
        result = list(MTTExpand.add_import_line(flines, 'test1'))
        expect = '''
Import PrimeFlowControlForkTestMethod.xml;
Import PrimeFlowControlSetTestMethod.xml;
Import blah1;
end;

'''
        self.assertTextEqual(''.join(result), expect)

        # One missing
        text = '''
Import blah1;
Import PrimeFlowControlSetTestMethod.xml;
end;
'''
        flines = [f'{x}\n' for x in text.split('\n')]
        result = list(MTTExpand.add_import_line(flines, 'test1'))
        expect = '''
Import PrimeFlowControlForkTestMethod.xml;
Import PrimeFlowControlSetTestMethod.xml;
Import blah1;
end;

'''
        self.assertTextEqual(''.join(result), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
