#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for moduleskip
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock, MockVar, is_ut_option
from gadget.helperclass import CaptureStdoutLog
from gadget.printmore import Dumper
from gadget.errors import ErrorUser
from gadget.shell import IS_UNIX, SystemCall
from gadget.disk import Chdir
from gadget.files import TempDir
from gadget.gizmo import with_
from main.torch_postproc import PlistEdit
from mod.moduleskip import *
from tp.testprogram import TestProgram, Env
from pprint import pprint
import shutil
import os


class TestModuleSkip(TestCase):

    def programflows(self):
        return '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem TPI_BASE_CSE TPI_BASE::TPI_BASE_CSE
        {
                Result -2
                {
                        GoTo SCN_GT_CSE1;
                }
                Result -1
                {
                        Return -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE;
                }
        }
        DUTFlowItem SCN_GT_CSE IP_CPU::SCN_GT::SCN_GT_CSE
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE1;
                }
        }
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo ARR1;
                }
        }
        DUTFlowItem ARR1 IP_CPU::ARR::ARR1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''

    def test_basic(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            text = '''
SOME STUFF;
ALEPH_FILES = "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json;" +
              "./Modules/BLAH/InputFiles/csme_PatConfigSetpoints.json;" +
              "./Modules/BLAH/InputFiles/csme_PatConfigSetpoints1.json;"+
              "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json";
'''

            # One module skipped
            File(f'{tp.tpldir}/EnvironmentFile.env').touch(text)
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())

            # No module skip - json missing
            self.assertEqual(ModuleSkip(tp).main(), [])

            # No module to skip
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": [] }', newfile=True)
            self.assertEqual(ModuleSkip(tp).main(), [None])
            self.assertEqual(set(os.listdir(tdir)), {'EnvironmentFile.env',
                                                     'skip_modules.json',
                                                     'ProgramFlows.mtpl',
                                                     'PLIST_ALL.xml',
                                                     'SubTestPlan_CLASS_TGLH81.stpl'})
            self.assertEqual(File(f'{tdir}/ProgramFlows.mtpl').read(), self.programflows())   # no change

            # No matching module, file is still generated
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["BLAH"] }', newfile=True)
            self.assertEqual(ModuleSkip(tp).main(), ['SubTestPlan_CLASS_TGLH81.stpl'])
            self.assertEqual(set(os.listdir(tdir)), {'EnvironmentFile.env',
                                                     'EnvironmentFile.env.old',
                                                     'skip_modules.json',
                                                     'ProgramFlows.mtpl',
                                                     'SubTestPlan_CLASS_TGLH81.stpl',
                                                     'SubTestPlan_CLASS_TGLH81.stpl.old',
                                                     'PLIST_ALL.xml',
                                                     'ProgramFlows_CLASS_TGLH81.mtpl'})
            self.assertEqual(File(f'{tp.tpldir}/ProgramFlows.mtpl').read(),
                             File(f'{tp.tpldir}/ProgramFlows_CLASS_TGLH81.mtpl').read())
            expect = r"""Version 1.0;

SubTestPlans
{
.\Modules\ARR\array.mtpl;
.\Modules\SCN\scan.mtpl;

Final .\ProgramFlowsTestPlan\ProgramFlows_CLASS_TGLH81.mtpl;
}"""
            result = [x.lstrip() for x in File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').read().split('\n')]
            self.assertTextEqual('\n'.join(result), expect)
            expect = '''
SOME STUFF;
ALEPH_FILES = "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json;" +
              "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json";
'''
            self.assertTextEqual(File(os.path.join(tdir, 'EnvironmentFile.env')).read(), expect)

    def test_shared_json(self):
        # MTLM and MTLP are two different base

        with TempDir(name=True) as tdir:
            shutil.copytree(f'{UT_DIR_REPO}/Simple1/TPL', f'{tdir}/TPL')
            if IS_UNIX:
                SystemCall(f'chmod +w -R {tdir}').run_outonly()
            File(f'{UT_DIR_REPO}/Simple1/ProgramFlows.mtpl.fixed').copy(f'{tdir}/TPL/ProgramFlowsTestPlan/ProgramFlows.mtpl')
            tp = TestProgram(f'{tdir}/TPL/EnvironmentFile.env').init()
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())

            # two BOMs in json, one is missing. missing is ignored.
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": [], "BLAH": ["ARR"]}', newfile=True)
            self.assertEqual(ModuleSkip(tp).main(), [None, 'SubTestPlan_CLASS_TGLH81.stpl'])
            self.assertEqual(set(Env.xpath(i) for i in glob.glob(f'{tdir}/TPL/Sub*')), {
                             f'{Env.xpath(tdir + "/TPL/SubTestPlan_CLASS_TGLH81.stpl")}', f'{Env.xpath(tdir + "/TPL/SubTestPlan_CLASS_TGLH81.stpl.old")}'})

    def test_tos4(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            tp.moddir = tdir
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').touch(r'''
Version 1.0;

SubTestPlans
{
        "./Modules/ARR/array.mtpl";
        "./Modules/SCN/scan.mtpl";
        "./Modules/IP_PCH_CONCURRENT_FLOWS/IP_PCH_CONCURRENT_FLOWS.mtpl";
        "./Modules/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS.mtpl";


        Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''')
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())
            File(f'{tdir}/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS.mtpl').touch('''
DUTFlow CSE_SubFlow
{
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo ARR1;
                }
        }
        DUTFlowItem ARR1 IP_CPU::ARR::ARR1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
''', mkdir=True)

            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)

            # execute ============================
            ModuleSkip(tp).main()

            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem TPI_BASE_CSE TPI_BASE::TPI_BASE_CSE
        {
                Result -2
                {
                        GoTo SCN_GT_CSE1;
                }
                Result -1
                {
                        Return -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE;
                }
        }
        DUTFlowItem SCN_GT_CSE IP_CPU::SCN_GT::SCN_GT_CSE
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE1;
                }
        }
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS_CLASS_TGLH81.mtpl').read(),
                                 expect)

            expect = r'''
Version 1.0;

SubTestPlans
{
        "./Modules/SCN/scan.mtpl";
        "./Modules/IP_PCH_CONCURRENT_FLOWS/IP_PCH_CONCURRENT_FLOWS.mtpl";
        "./Modules/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS_CLASS_TGLH81.mtpl";


        Final "./ProgramFlowsTestPlan/ProgramFlows_CLASS_TGLH81.mtpl";
}'''
            self.assertTextEqual(File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').read(), expect)

    def test_ip_mtpl(self):
        # Special IP_CPU_CONCURRENT_FLOWS exist
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            tp.moddir = tdir
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').touch(r'''
Version 1.0;

SubTestPlans
{
        .\Modules\ARR\array.mtpl;
        .\Modules\SCN\scan.mtpl;
        .\Modules\IP_PCH_CONCURRENT_FLOWS\IP_PCH_CONCURRENT_FLOWS.mtpl;
        .\Modules\IP_CPU_CONCURRENT_FLOWS\IP_CPU_CONCURRENT_FLOWS.mtpl;


        Final .\ProgramFlowsTestPlan\ProgramFlows.mtpl;
}
''')
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())
            File(f'{tdir}/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS.mtpl').touch('''
DUTFlow CSE_SubFlow
{
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo ARR1;
                }
        }
        DUTFlowItem ARR1 IP_CPU::ARR::ARR1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
''', mkdir=True)

            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)

            # execute ============================
            ModuleSkip(tp).main()

            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem TPI_BASE_CSE TPI_BASE::TPI_BASE_CSE
        {
                Result -2
                {
                        GoTo SCN_GT_CSE1;
                }
                Result -1
                {
                        Return -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE;
                }
        }
        DUTFlowItem SCN_GT_CSE IP_CPU::SCN_GT::SCN_GT_CSE
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE1;
                }
        }
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS_CLASS_TGLH81.mtpl').read(),
                                 expect)

            expect = r'''
Version 1.0;

SubTestPlans
{
        .\Modules\SCN\scan.mtpl;
        .\Modules\IP_PCH_CONCURRENT_FLOWS\IP_PCH_CONCURRENT_FLOWS.mtpl;
        .\Modules\IP_CPU_CONCURRENT_FLOWS\IP_CPU_CONCURRENT_FLOWS_CLASS_TGLH81.mtpl;


        Final .\ProgramFlowsTestPlan\ProgramFlows_CLASS_TGLH81.mtpl;
}'''
            self.assertTextEqual(File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').read(), expect)

    def test_ip_mtpl_mtl(self):
        # Special IP_CPU_CONCURRENT_FLOWS exist
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            tp.moddir = tdir
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').touch(r'''
Version 1.0;

SubTestPlans
{
        .\Modules\ARR\array.mtpl;
        .\Modules\SCN\scan.mtpl;
        .\Modules\IP_PCH_CONCURRENT_FLOWS\IP_PCH_CONCURRENT_FLOWS.mtpl;
        Final .\ProgramFlowsTestPlan\IP_CPU_CONCURRENT_FLOWS.mtpl;

        Final .\ProgramFlowsTestPlan\ProgramFlows.mtpl;
}
''')
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())
            File(f'{tdir}/ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl').touch('''
DUTFlow CSE_SubFlow
{
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo ARR1;
                }
        }
        DUTFlowItem ARR1 IP_CPU::ARR::ARR1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
''', mkdir=True)

            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)

            # execute ============================
            ModuleSkip(tp).main()

            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem TPI_BASE_CSE TPI_BASE::TPI_BASE_CSE
        {
                Result -2
                {
                        GoTo SCN_GT_CSE1;
                }
                Result -1
                {
                        Return -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE;
                }
        }
        DUTFlowItem SCN_GT_CSE IP_CPU::SCN_GT::SCN_GT_CSE
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE1;
                }
        }
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS_CLASS_TGLH81.mtpl').read(),
                                 expect)

            expect = r'''
Version 1.0;

SubTestPlans
{
        .\Modules\SCN\scan.mtpl;
        .\Modules\IP_PCH_CONCURRENT_FLOWS\IP_PCH_CONCURRENT_FLOWS.mtpl;
        Final .\ProgramFlowsTestPlan\IP_CPU_CONCURRENT_FLOWS_CLASS_TGLH81.mtpl;

        Final .\ProgramFlowsTestPlan\ProgramFlows_CLASS_TGLH81.mtpl;
}'''
            self.assertTextEqual(File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_update_plist(self):
        tp = TestProgram(f'{UT_DIR}/torch_mvtp_pass/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env').pickle_init()
        ms = ModuleSkip(tp)
        with TempDir(name=True) as tdir, \
                MockVar(ms, "set_plist_remove", Mock(return_value={'a_p28.plist', 'B_P28.plist'})), \
                MockVar(tp.plists, "get_all_plists", Mock(return_value=[f'{tdir}/a.xml'])):
            text = '''<HdmtReferenceFile>
  <PList>
    <PListFile name="a_p28.plist" />
    <PListFile name="b_p28.plist" />
    <PListFile name="c.plist" />
  </PList>
</HdmtReferenceFile>
'''
            fobj = File(f'{tdir}/a.xml').touch(text)
            ms.update_plist(None)
            expect = '''<HdmtReferenceFile>
  <PList>
    <PListFile name="c.plist" />
  </PList>
</HdmtReferenceFile>
'''
            self.assertTextEqual(fobj.read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_set_plist_remove(self):
        tp = TestProgram(f'{UT_DIR}/torch_mvtp_pass/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env').pickle_init()
        pprint(tp.plists.get_mod2plist_map())

        ms = ModuleSkip(tp)
        result = ms.set_plist_remove(['DRV_RESET_CXX'])
        print("Start====")
        pprint(result)
        self.assertEqual(result, {'AAA_drv_cdie_C68_vrevC68R0P_class_class_p68g2.plist',
                                  'AAA_drv_cdie_C68_vrevC68R0X_class_class_p68g2.plist',
                                  'drv_cdie_C68_dfx_class_p68g2.plist',
                                  'drv_cdie_C68_reset_class_p68g2.plist'})

        result = ms.set_plist_remove(['DRV_RESET_CXX', 'DRV_RSTCMN_XXX'])
        pprint(result)
        self.assertEqual(result, {'AAA_drv_cdie_C68_vrevC68R0P_class_class_p68g2.plist',
                                  'AAA_drv_cdie_C68_vrevC68R0P_ippkg_class_p68g2.plist',
                                  'AAA_drv_cdie_C68_vrevC68R0X_class_class_p68g2.plist',
                                  'AAA_drv_cdie_C68_vrevC68R0X_ippkg_class_p68g2.plist',
                                  'drv_cdie_C68_dfx_class_p68g2.plist',
                                  'drv_cdie_C68_reset_class_p68g2.plist'})

        # empty_plist() unittest ==============================
        text = '''<HdmtReferenceFile>
  <PList>
  </PList>
</HdmtReferenceFile>
'''
        inlist = [f'{x}\n' for x in text.split('\n')]
        expect = '''<HdmtReferenceFile>
  <PList>
     <PListFile name="EmptyPlist_abc.plist" />
  </PList>
</HdmtReferenceFile>

'''
        self.assertTextEqual(''.join(ms.empty_plist(inlist, '/path/abc.plist.ipxml')), expect)

        # non-empty plist - asis
        text = '''<HdmtReferenceFile>
  <PList>
     <PListFile name="abc.plist" />
  </PList>
</HdmtReferenceFile>
'''
        inlist = [f'{x}\n' for x in text.split('\n')]
        self.assertTextEqual(''.join(ms.empty_plist(inlist, '/path/abc.plist.ipxml')), f'{text}\n')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6tos4', chdir=True, delete=True)
    def test_set_plist_remove_tos4(self):
        tp = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        mkdirs('Shared/BaseInputs/Supersedes/patterns')
        pprint(tp.plists.get_mod2plist_map())

        ms = ModuleSkip(tp)
        result = ms.set_plist_remove(['DRV_RESET_CXX'])
        print("Start====")
        pprint(result)
        self.assertEqual(result, set())

        result = ms.set_plist_remove(['DRV_RESET_CXX', 'DRV_RSTCMN_XXX'])
        pprint(result)
        self.assertEqual(result, set())

        # empty_plist() unittest ==============================
        text = '''<HdmtReferenceFile>
  <PList>
  </PList>
</HdmtReferenceFile>
'''
        inlist = [f'{x}\n' for x in text.split('\n')]
        expect = '''<HdmtReferenceFile>
  <PList>
     <PListFile name="EmptyPlist_abc.plist" />
  </PList>
</HdmtReferenceFile>

'''
        self.assertTextEqual(''.join(ms.empty_plist(inlist, '/path/abc.plist.ipxml')), expect)
        self.assertTextEqual(File('Shared/BaseInputs/Supersedes/patterns/EmptyPlist_abc.plist').read(),
                             'Version 6.0;\n')

    def test_one_skip_and_rerun(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())
            File(f'{tdir}/ProgramFlows.flw').touch('''
<HDMTFlowItemCoor>
  <FlowItem name="Flows::CSE_SubFlow.TPI_BASE_CSE" X="100" Y="20" />
  <FlowItem name="Flows::CSE_SubFlow.ARR1" X="100" Y="20" />
  <FlowItem name="Flows::CSE_SubFlow.SCN_GT_CSE1" X="100" Y="20" />
</HDMTFlowItemCoor>
''')

            # start of testcase
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["SCN_GT"] }', newfile=True)
            ModuleSkip(tp).main()
            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem TPI_BASE_CSE TPI_BASE::TPI_BASE_CSE
        {
                Result -2
                {
                        GoTo ARR1;
                }
                Result -1
                {
                        Return -1;
                }
                Result 1
                {
                        GoTo ARR1;
                }
        }
        DUTFlowItem ARR1 IP_CPU::ARR::ARR1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

            expectflw = '''
<HDMTFlowItemCoor>
  <FlowItem name="Flows::CSE_SubFlow.TPI_BASE_CSE" X="100" Y="20" />
  <FlowItem name="Flows::CSE_SubFlow.ARR1" X="100" Y="20" />
</HDMTFlowItemCoor>
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.flw').read(), expectflw)
            expectfiles = {'ProgramFlows.mtpl',
                           'EnvironmentFile.env',
                           'SubTestPlan_CLASS_TGLH81.stpl.old',
                           'ProgramFlows.flw',
                           'ProgramFlows_CLASS_TGLH81.mtpl',
                           'skip_modules.json',
                           'SubTestPlan_CLASS_TGLH81.stpl',
                           'ProgramFlows_CLASS_TGLH81.flw',
                           'PLIST_ALL.xml'}
            self.assertEqual(set(os.listdir(tdir)), expectfiles)

            # Rerun
            print("Rerun ========")
            with MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl')):
                ModuleSkip(tp).main()
                self.assertEqual(set(os.listdir(tdir)), expectfiles)
                self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)
                self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.flw').read(), expectflw)

    def test_one_skip2(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())

            # start of testcase
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)
            ModuleSkip(tp).main()
            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem TPI_BASE_CSE TPI_BASE::TPI_BASE_CSE
        {
                Result -2
                {
                        GoTo SCN_GT_CSE1;
                }
                Result -1
                {
                        Return -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE;
                }
        }
        DUTFlowItem SCN_GT_CSE IP_CPU::SCN_GT::SCN_GT_CSE
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE1;
                }
        }
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

    def test_one_skip3(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())

            # start of testcase
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["TPI_BASE"] }', newfile=True)
            ModuleSkip(tp).main()
            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem SCN_GT_CSE IP_CPU::SCN_GT::SCN_GT_CSE
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo SCN_GT_CSE1;
                }
        }
        DUTFlowItem SCN_GT_CSE1 IP_CPU::SCN_GT::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo ARR1;
                }
        }
        DUTFlowItem ARR1 IP_CPU::ARR::ARR1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

    def test_two_skip(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())

            # start of testcase
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["SCN_GT", "ARR"] }', newfile=True)
            ModuleSkip(tp).main()
            expect = '''
DUTFlow CSE_SubFlow
{
        DUTFlowItem TPI_BASE_CSE TPI_BASE::TPI_BASE_CSE
        {
                Result -2
                {
                        Return 5;
                }
                Result -1
                {
                        Return -1;
                }
                Result 1
                {
                        Return 5;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

            expect = r"""Version 1.0;

SubTestPlans
{
.\Modules\SCN\scan.mtpl;

Final .\ProgramFlowsTestPlan\ProgramFlows_CLASS_TGLH81.mtpl;
}"""
            result = [x.lstrip() for x in File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').read().split('\n')]
            self.assertTextEqual('\n'.join(result), expect)

    def test_empty_dutflow(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        src = tp.tpldir
        mtpl = '''
DUTFlow CSE_A
{
        DUTFlowItem SCN_GT_CSE IP_CPU::ARR::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 1;
                }
        }
}
DUTFlow CSE_B
{
        DUTFlowItem SCN_GT_CSEB IP_CPU::SCN_GT::SCN_GT_CSE2
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 1;
                }
        }
}
DUTFlow CSE_C
{
        DUTFlowItem SCN_GT_CSEC IP_CPU::SCN_GT::SCN_GT_CSE3
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 1;
                }
        }
}
DUTFlow MAIN
{
        DUTFlowItem CSE_A CSE_A
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo CSE_B;
                }
        }
        DUTFlowItem CSE_B CSE_B
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo CSE_C;
                }
        }
        DUTFlowItem CSE_C CSE_C
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 2;
                }
        }
}
'''
        # CASE1: A->B->C (B and C are empty)
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{src}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir

            File(f'{tdir}/ProgramFlows.mtpl').touch(mtpl)

            # start of testcase
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["SCN_GT"] }', newfile=True)
            ModuleSkip(tp).main()
            expect = '''
DUTFlow CSE_A
{
        DUTFlowItem SCN_GT_CSE IP_CPU::ARR::SCN_GT_CSE1
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 1;
                }
        }
}
DUTFlow MAIN
{
        DUTFlowItem CSE_A CSE_A
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 2;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

        # CASE2: A->B->C (A is empty)
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{src}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{src}/EnvironmentFile.env').copy(tdir)
            File(f'{src}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir

            # A->B->C (B and C are empty)
            File(f'{tdir}/ProgramFlows.mtpl').touch(mtpl)

            # start of testcase
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)
            ModuleSkip(tp).main()
            expect = '''
DUTFlow CSE_B
{
        DUTFlowItem SCN_GT_CSEB IP_CPU::SCN_GT::SCN_GT_CSE2
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 1;
                }
        }
}
DUTFlow CSE_C
{
        DUTFlowItem SCN_GT_CSEC IP_CPU::SCN_GT::SCN_GT_CSE3
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 1;
                }
        }
}
DUTFlow MAIN
{
        DUTFlowItem CSE_B CSE_B
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        GoTo CSE_C;
                }
        }
        DUTFlowItem CSE_C CSE_C
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 2;
                }
        }
}
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

    def test_all_skip(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            File(f'{tp.tpldir}/PLIST_ALL.xml').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            File(f'{tdir}/ProgramFlows.mtpl').touch(self.programflows())

            # start of testcase
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "CLASS_TGLH81": ["SCN_GT", "ARR", "TPI_BASE"] }', newfile=True)
            ModuleSkip(tp).main()
            expect = '''
'''
            self.assertTextEqual(File(f'{tdir}/ProgramFlows_CLASS_TGLH81.mtpl').read(), expect)

    def test_check_brackets(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir:
            text = """
DUTFlow MAIN {
        DUTFlowItem CSE_C CSE_C {
                Result -2 {
                        Return  -1;
                }
                Result 1
                {
                        Return 2;
                }
        }
}
"""
            all_lines = text.split('\n')
            File(f'{tdir}/ProgramFlows.mtpl').touch(text, newfile=True)
            with self.assertRaisesRegex(AssertionError, 'has non-standard open brackets. 4 vs 1 count'):
                ModuleSkip(tp).check_brackets(f'{tdir}/ProgramFlows.mtpl', all_lines)

            text = """
DUTFlow MAIN
{
        DUTFlowItem CSE_C CSE_C
        {
                Result -2
                {
                        Return  -1;
                }
                Result 1
                {
                        Return 2; }
        }
}
"""
            all_lines = text.split('\n')
            File(f'{tdir}/ProgramFlows.mtpl').touch(text, newfile=True)
            with self.assertRaisesRegex(AssertionError, 'has non-standard close brackets. 4 vs 3 count'):
                ModuleSkip(tp).check_brackets(f'{tdir}/ProgramFlows.mtpl', all_lines)

    def test_read_empty_subflows(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        obj = ModuleSkip(tp)
        lines = '''
Flow NotEmpty
{
    FlowItem blah IPG::IPG_FLOWS::BEGINGCD_SubFlow
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
    }
}

Flow Empty
{
}

Flow Empty2
{

}
'''.split('\n')
        res1, res2 = obj.read_empty_subflows(lines)
        expect = '''
Flow NotEmpty
{
    FlowItem blah IPG::IPG_FLOWS::BEGINGCD_SubFlow
    {
        Result -2
        {
            Property PassFail = "Fail";
        }
    }
}


'''
        self.assertTextEqual('\n'.join(res1), expect)
        self.assertEqual(res2, {'Empty', 'Empty2'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_json(self):
        # modlist
        tp = TestProgram(f'{UT_DIR}/mtl_P_integ6_TimIssue/EnvironmentFile_CLASS_P28G2_TRCFAILED.env')
        ms = ModuleSkip(tp, modlist=['A', 'B'])
        self.assertEqual(ms.read_json(), {'CLASS_P28G2': ['A', 'B']})

        with TempDir(name=True) as tdir:
            shutil.copytree(f'{UT_DIR}/Simple1/TPL', f'{tdir}/TPL')
            if IS_UNIX:
                SystemCall(f'chmod +w -R {tdir}').run_outonly()

            tp = TestProgram(f'{tdir}/TPL/EnvironmentFile.env')

            # missing json file
            ms = ModuleSkip(tp)
            self.assertEqual(ms.read_json(), {})

            # onlylist case1
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "BASE_MODULES": ["ARR"], "CLASS_TGLH81": ["C"] }', newfile=True)
            ms = ModuleSkip(tp, onlylist=['A'])
            self.assertEqual(ms.read_json(), {'CLASS_TGLH81': ['SCN'], })

            # onlylist case2
            File(f'{tp.tpldir}/skip_modules.json').touch('{ "BASE_MODULES": ["ARR"], "CLASS_TGLH81": ["C"] }', newfile=True)
            ms = ModuleSkip(tp, onlylist=['SCN'])
            self.assertEqual(ms.read_json(), {'CLASS_TGLH81': []})

            # Normal, should not include "BASE_MODULES"
            ms = ModuleSkip(tp)
            self.assertEqual(ms.read_json(), {'CLASS_TGLH81': ["C"]})

    def test_get_env_name(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            env = File(f'{tp.tpldir}/EnvironmentFile.env').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            ms = ModuleSkip(tp)

            # case1: Default, non-bom
            self.assertEqual(basename(ms.get_env_name('CLASS_TGLH81')), 'EnvironmentFile.env')

            # case2: BOM name
            env.rename('EnvironmentFile_CLASS_TGLH81.env')
            self.assertEqual(basename(ms.get_env_name('CLASS_TGLH81')), 'EnvironmentFile_CLASS_TGLH81.env')

            # case3: BOM name TRCFAIL
            env.rename('EnvironmentFile_CLASS_TGLH81_TRCFAILED.env')
            self.assertEqual(basename(ms.get_env_name('CLASS_TGLH81')), 'EnvironmentFile_CLASS_TGLH81_TRCFAILED.env')

            # case4: none-found
            with self.assertRaisesRegex(ErrorInput, 'No file found that match'):
                ms.get_env_name('CLASS_TGLH82')

            # case5: multiple found
            env.copy(os.path.join(tdir, 'EnvironmentFile_CLASS_TGLH81_TRCFAILED2.env'))
            with self.assertRaisesRegex(ErrorInput, 'Multiple env file found for the same bom'):
                ms.get_env_name('CLASS_TGLH81')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple1', chdir=True, delete=True)
    def test_proc_subbdef(self):
        imp = 'TPL/Package_Shared/Modules.imp'
        File(imp).touch('''
Import "../../Modules/ARR1/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/SKIPME/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/CLK/SKIPME2/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/ARR2/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";
''', mkdir=True)
        tp = TestProgram('TPL/EnvironmentFile.env')
        ms = ModuleSkip(tp)

        modset = {'SKIPME', 'SKIPME2'}
        ms.proc_subbdef(modset, [f'{tp.shareddir}/Package_Shared/Modules.imp'])
        print(f'hey: {tp.shareddir}')
        expect = '''
Import "../../Modules/ARR1/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";
Import "../../Modules/ARR2/FUS_UNITINFO_CXX_SubBinDefinitions.sbdefs";

'''
        self.assertTextEqual(File(imp).read(), expect)

    def test_proc_env(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            text = '''
CASE0 = "hello";

CASE1 = "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json;" +
        "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP/InputFiles/csme_PatConfigSetpoints.json;" +
        "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json";

CASE2 = "./Modules/MOD_SKIP/InputFiles/freq_ifpm_gt_class_patmod.json;" +
        "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_OK/InputFiles/csme_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP/InputFiles/freq_ifpm_gt_class_patmod.json";
'''

            # One module skipped, top and bottom
            File(f'{tp.tpldir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)

            result = ms.proc_env(ms.get_env_name('BLAH'), {'MOD_SKIP'})
            expect = '''
CASE0 = "hello";

CASE1 = "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json;" +
        "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json";

CASE2 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_OK/InputFiles/csme_PatConfigSetpoints.json";'''
            self.assertTextEqual(''.join(result), expect)

            # Two modules skipped, middle
            result = ms.proc_env(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'MOD_SKIP2'})
            expect = '''
CASE0 = "hello";

CASE1 = "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json;" +
        "./Modules/MOD_SKIP/InputFiles/csme_PatConfigSetpoints.json;" +
        "./Modules/MOD_OK/InputFiles/freq_ifpm_gt_class_patmod.json";

CASE2 = "./Modules/MOD_SKIP/InputFiles/freq_ifpm_gt_class_patmod.json;" +
        "./Modules/MOD_OK/InputFiles/csme_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP/InputFiles/freq_ifpm_gt_class_patmod.json";
'''
            self.assertTextEqual(''.join(result), expect)

    def test_proc_env_empty(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            text = '''
CASE0 = "hello";

CASEM = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";
CASE1 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

CASE2 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

CASE3 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

'''

            # One module skipped, top and bottom
            File(f'{tp.tpldir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)

            result = ms.proc_env(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'MOD_SKIP2'})
            expect = '''
CASE0 = "hello";

CASEM = "";
CASE1 = "";

CASE2 = "";

CASE3 = "";

'''
            self.assertTextEqual(''.join(result), expect)

    def test_proc_env_empty_aleph(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir,\
                MockVar(tp, 'get_final_mtpl', Mock(return_value=f'{tdir}/ProgramFlows.mtpl')):
            File(f'{tp.tpldir}/SubTestPlan_CLASS_TGLH81.stpl').copy(tdir)
            tp.envdir = tdir
            tp.tpldir = tdir
            text = '''
ALEPH_0 = "hello";

ALEPH_M = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";
1_ALEPH = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

1_ALEPH_3 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

'''

            # One module skipped, top and bottom
            File(f'{tp.tpldir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)

            result = ms.proc_env(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'MOD_SKIP2'})
            expect = '''
ALEPH_0 = "hello";

ALEPH_M = ";";
1_ALEPH = ";";

ALEPH = ";";

1_ALEPH_3 = ";";

'''
            self.assertTextEqual(''.join(result), expect)

    def test_proc_env_torch(self):
        # tests backslash as well
        # tests shared module structure
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir:
            tp.envdir = tdir
            text = '''
CASE0 = "hello";

CASEM = "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";
CASE1 = "./Modules/t_p-i/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

CASE2 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/tp-i/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

CASE3 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

CASE4 = "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/tp-i/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/tp-i/MOD_SKIP3/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";
'''.replace('/', '\\')

            # One module skipped, top and bottom
            File(f'{tdir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)

            result = ms.proc_env(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'MOD_SKIP2'})
            expect = '''
CASE0 = "hello";

CASEM = "";
CASE1 = "";

CASE2 = "";

CASE3 = "";

CASE4 = "./Modules/tp-i/MOD_SKIP3/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";
'''.replace('/', '\\')
            self.assertTextEqual(''.join(result), expect)

    def test_proc_env_patmod(self):
        # tests patmodify
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir:
            tp.envdir = tdir
            text = '''
CASE0 = "hello";

CASE1 = "$MTPI_PATMODIFY_PATH/blah.json;" +
        "$MFUS_PATMODIFY_PATH/blah.json;" +
        "$MARR_PATMODIFY_PATH/blah.json";
'''.replace('/', '\\')

            # One module skipped, top and bottom
            File(f'{tdir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)

            result = ms.proc_env(f'{tdir}/EnvironmentFile.env', {'ARR'})
            expect = '''
CASE0 = "hello";

CASE1 = "$MFUS_PATMODIFY_PATH/blah.json;" +
        "$MARR_PATMODIFY_PATH/blah.json";
'''.replace('/', '\\')
            self.assertTextEqual(''.join(result), expect)

            # unittest on patmodify
            self.assertEqual(ms.proc_env(f'{tdir}/EnvironmentFile.env', {'ARR', 'NOTFOUND'}, ut=True),
                             {'_INITIAL_', 'MTPI_PATMODIFY_PATH'})
            self.assertEqual(ms.proc_env(f'{tdir}/EnvironmentFile.env', {'ARR', 'SCN'}, ut=True),
                             {'_INITIAL_', 'MTPI_PATMODIFY_PATH'})
            self.assertEqual(ms.proc_env(f'{tdir}/EnvironmentFile.env', {'ARR', 'PTH', 'SCN'}, ut=True),
                             {'_INITIAL_', 'MTPI_PATMODIFY_PATH', 'MFUS_PATMODIFY_PATH'})
            self.assertEqual(ms.proc_env(f'{tdir}/EnvironmentFile.env', {'NOTFOUND'}, ut=True),
                             {'_INITIAL_'})
            self.assertEqual(ms.proc_env(f'{tdir}/EnvironmentFile.env', {'SCN'}, ut=True),
                             {'_INITIAL_'})

    def test_proc_env_modularenv(self):
        # tests modular env
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir:
            tp.envdir = tdir
            text = '''
CASE0 = "hello";

CASE1 = "$ARRX_HDST_PLIST_PATH;" +
        "$ARRX_HDST_PAT_PATH;" +
        "$ARRX_ALEPH_FILES;" +
        "$MFUS_HDST_PAT_PATH;" +
        "$MFUS_ALEPH_FILES";
'''.replace('/', '\\')

            # One module skipped, top and bottom
            File(f'{tdir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)

            result = ms.proc_env(f'{tdir}/EnvironmentFile.env', {'ARR'})
            expect = '''
CASE0 = "hello";

CASE1 = "$MFUS_HDST_PAT_PATH;" +
        "$MFUS_ALEPH_FILES";
'''.replace('/', '\\')
            self.assertTextEqual(''.join(result), expect)

    def test_proc_env_bug(self):
        # bug: The last line is not deleted
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir:
            tp.envdir = tdir
            text = '''
$include "../../keep";
$include "../../ARRX/blah";

ACASE = "$ARRX_ALEPH_FILES;" +
        "MIDDLE;" +
        "$ARRX_ALEPH_FILES";

BCASE = "$MTPI_PATMODIFY_PATH;" +
        "MIDDLE;" +
        "$MTPI_PATMODIFY_PATH";

'''

            # One module skipped, top and bottom
            File(f'{tdir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)

            result = ms.proc_env(f'{tdir}/EnvironmentFile.env', {'ARR'})
            expect = '''
$include "../../keep";

ACASE = "MIDDLE";
BCASE = "MIDDLE";
'''
            self.assertTextEqual(''.join(result), expect)

    def test_dest(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env')

        # Default case
        ms = ModuleSkip(tp)
        self.assertEqual(ms.dest('/path/blah'), '/path/blah')

        with TempDir(name=True) as tdir:
            ms = ModuleSkip(tp, destdir=tdir)
            self.assertEqual(ms.dest('/path/blah'), f'{tdir}/blah')
            self.assertEqual(ms.dest('/path/ProgramFlowsTestPlan/a.txt'), f'{tdir}/ProgramFlowsTestPlan/a.txt')

    def test_proc_skipfile(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env')
        # m2m is {'ARRX': 'ARR', 'SCNX': 'SCN', 'PTH': 'PTH'}

        ms = ModuleSkip(tp)
        with TempDir(chdir=True, name=True) as tdir:
            tp.envdir = f'{tdir}/POR_TP/TGLH81'

            File('POR_TP/TGLH81/EnvironmentFile.env').touch(mkdir=True)
            File('POR_TP/TGLH81/SkipModules/SCNX.txt').touch(mkdir=True)
            File('Shared/POR_TP/TGLH81/SkipModules/ARRX.txt').touch(mkdir=True)

            result = ms.proc_skipfile()
            self.assertEqual(sorted(result), ['ARR', 'SCN'])

    def test_proc_env2(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env')
        ms = ModuleSkip(tp)
        with TempDir(chdir=True, name=True) as tdir:
            code = '''
CLK_BASE_CX816P_ALEPH_FILES = "$TORCH_AUTO_CLK_BASE_CX816P_ALEPH_FILES";
CLK_BASE_GXS_ALEPH_FILES = "$TORCH_AUTO_CLK_BASE_GXS_ALEPH_FILES";
TORCH_AUTO_CLK_BASE_CX816P_ALEPH_FILES = "I:/hdmxpats/nvl_cpu/MCclk/RevTCI8GA0.0/p5/cfg/clk.cpu.CLASS.recipe.all.patmod.json";
TORCH_AUTO_CLK_BASE_CX816P_PAT_PATH = "I:/hdmxpats/nvl_cpu/MCclk/RevTCI8GA0.0/p5/pat/common_files;" +
     "more";
TORCH_AUTO_CLK_BASE_GXS_ALEPH_FILES = "I:/hdmxpats/nvl_gcd/MGclk/RevTG032A0.0/p5/cfg/clk.gcd.CLASS.recipe.all.patmod.json";
TORCH_AUTO_CLK_BASE_GXS_PAT_PATH = "I:/hdmxpats/nvl_gcd/MGclk/RevTG032A0.0/p5/pat/common_files;" +
     "more";
'''
            File('a.env').touch(code)

            # no changes
            with MockVar(ms, 'get_modfolder2mod', Mock(return_value={'CLK_BASE_CX816P': 'CLK_BASE_CXX'})):
                ms.proc_env2('a.env', {'CLK_BASE_CXY'})
            self.assertTextEqual(File('a.env').read(), code)

            # with changes
            with MockVar(ms, 'get_modfolder2mod', Mock(return_value={'CLK_BASE_CX816P': 'CLK_BASE_CXX'})):
                ms.proc_env2('a.env', {'CLK_BASE_CXX'})
            expect = '''
CLK_BASE_GXS_ALEPH_FILES = "$TORCH_AUTO_CLK_BASE_GXS_ALEPH_FILES";

TORCH_AUTO_CLK_BASE_GXS_ALEPH_FILES = "I:/hdmxpats/nvl_gcd/MGclk/RevTG032A0.0/p5/cfg/clk.gcd.CLASS.recipe.all.patmod.json";

TORCH_AUTO_CLK_BASE_GXS_PAT_PATH = "I:/hdmxpats/nvl_gcd/MGclk/RevTG032A0.0/p5/pat/common_files;" +
    "more";
'''
            self.assertTextEqual(File('a.env').read(), expect)


class TestInteg(TestCase):

    def test_skipjson(self):
        # Skip ARR from command line
        tpref = f'{UT_DIR_REPO}/Simple1/TPL'
        with TempDir(name=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            if IS_UNIX:
                SystemCall(f'chmod +w -R {tdir}').run_outonly()
            File(f'{tpref}/../ProgramFlows.mtpl.fixed').copy(f'{tdir}/TPL/ProgramFlowsTestPlan/ProgramFlows.mtpl')
            File(f'{tdir}/TPL/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)
            tpenv = f'{tdir}/TPL/EnvironmentFile.env'

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 5)

            # Do the skip
            ModuleSkip.skipjson_main(tpenv)

            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 2)

    def test_delete_folder(self):
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL3') as tdir:
            # setup first
            tpenv = f'POR_TP/Class_NVL_H81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)
            modules = sorted(glob.glob('Modules/*') + glob.glob('Shared/Modules/*'))
            self.assertEqual(len(modules), 6)

            # Do the skip
            ModuleSkip(tpobj, modlist=['SCN', 'PTH']).main(isdelete=True)

            modules = sorted(glob.glob('Modules/*') + glob.glob('Shared/Modules/*'))
            self.assertEqual([Env.xpath(x) for x in modules], ['Modules/ARR', 'Shared/Modules/ARR'])

    @with_(MockVar, os.environ, 'TPSWITCH2', 'True')
    def test_delete_folder2(self):
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL3') as tdir:
            # setup first
            tpenv = f'POR_TP/Class_NVL_H81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)
            modules = sorted(glob.glob('Modules/*') + glob.glob('Shared/Modules/*'))
            self.assertEqual(len(modules), 6)

            # Do the skip
            ModuleSkip(tpobj, modlist=['SCN', 'PTH']).main(isdelete=True)

            modules = sorted(glob.glob('Modules/*') + glob.glob('Shared/Modules/*'))
            self.assertEqual(len([Env.xpath(x) for x in modules]), 6)

    def test_basic(self):
        # checks output files
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 8)

            # Do the skip
            result = ModuleSkip(tpobj, modlist=['ARR']).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            tpnew = TestProgram(tpenv)
            result = len(list(tpnew.mtpl.iter_flows()))
            self.assertEqual(result, 4)

            # check PLIST_ALL contents
            expect = '''<HdmtReferenceFile>
  <PList>
    <PListFile name="fuse.plist" />
  </PList>
  <PatternConcat>
    <VectorDataFile />
    <PatInfoFile />
    <MSFile />
  </PatternConcat>
</HdmtReferenceFile>
'''
            self.assertTextEqual(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').read(), expect)

            # Check stpl on modulefolder different than module testplan - caught during validation
            expect = r'''Version 1.0;

SubTestPlans
{
  ../../Modules/SCNX/scan.mtpl;
  ../../Modules/PTH/pth.mtpl;

  Final ./ProgramFlowsTestPlan/ProgramFlows_CLASS_TGLH81.mtpl;
}'''
            stpl = File(f'{tdir}/TPL/POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').read().replace('\\', '/')
            self.assertTextEqual(stpl, expect)

            # ALEPH_FILES
            result = tpnew.env.get_item('ALEPH_FILES', islist=True)
            self.assertEqual(result, ['./Modules/PTH/InputFiles/dummy2.txt',
                                      './Modules/SCNX/InputFiles/dummy3.txt',
                                      '$MFUS_PATMODIFY_PATH/dummy.json',
                                      './Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_TGLH81_VminForwardingConfiguration.json'])

    def test_basic5(self):
        # overlap case - SCN and PTH overlap, remove SCN
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)

            # Do the skip
            result = ModuleSkip(tpobj, modlist=['SCN']).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            tpnew = TestProgram(tpenv)

            # check PLIST_ALL contents
            expect = '''<HdmtReferenceFile>
  <PList>
    <PListFile name="fuse.plist" />
    <PListFile name="Shops.plist" />
  </PList>
  <PatternConcat>
    <VectorDataFile />
    <PatInfoFile />
    <MSFile />
  </PatternConcat>
</HdmtReferenceFile>
'''
            self.assertTextEqual(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').read(), expect)

            # Check stpl on modulefolder different than module testplan - caught during validation
            expect = r'''Version 1.0;

SubTestPlans
{
  ../../Modules/ARRX/array.mtpl;
  ../../Modules/PTH/pth.mtpl;

  Final ./ProgramFlowsTestPlan/ProgramFlows_CLASS_TGLH81.mtpl;
}'''
            stpl = File(f'{tdir}/TPL/POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').read().replace('\\', '/')
            self.assertTextEqual(stpl, expect)

            # ALEPH_FILES
            result = tpnew.env.get_item('ALEPH_FILES', islist=True)
            self.assertEqual(result, ['./Modules/ARRX/InputFiles/input1.txt',
                                      './Modules/PTH/InputFiles/dummy2.txt',
                                      '$MFUS_PATMODIFY_PATH/dummy.json',
                                      '$MTPI_PATMODIFY_PATH/dummy.json',
                                      './Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_TGLH81_VminForwardingConfiguration.json'])

    def test_basic5a(self):
        # overlap case - SCN and PTH overlap, remove both
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)

            # Do the skip
            result = ModuleSkip(tpobj, modlist=['SCN', 'PTH']).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            tpnew = TestProgram(tpenv)

            # check PLIST_ALL contents
            expect = '''<HdmtReferenceFile>
  <PList>
    <PListFile name="Shops.plist" />
  </PList>
  <PatternConcat>
    <VectorDataFile />
    <PatInfoFile />
    <MSFile />
  </PatternConcat>
</HdmtReferenceFile>
'''
            self.assertTextEqual(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').read(), expect)

            # Check stpl on modulefolder different than module testplan - caught during validation
            expect = r'''Version 1.0;

SubTestPlans
{
  ../../Modules/ARRX/array.mtpl;

  Final ./ProgramFlowsTestPlan/ProgramFlows_CLASS_TGLH81.mtpl;
}'''
            stpl = File(f'{tdir}/TPL/POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').read().replace('\\', '/')
            self.assertTextEqual(stpl, expect)

            # ALEPH_FILES
            result = tpnew.env.get_item('ALEPH_FILES', islist=True)
            self.assertEqual(result, ['./Modules/ARRX/InputFiles/input1.txt',
                                      '$MTPI_PATMODIFY_PATH/dummy.json',
                                      './Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_TGLH81_VminForwardingConfiguration.json'])

    def test_basic2mv(self):
        # Specified modules - MV usage
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 8)

            # Do the skip
            result = ModuleSkip(tpobj, onlylist='SCN PTH'.split()).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 4)
            self.assertEqual(len(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').raw()), 10)

    def test_basic_sharedmodule(self):
        # MV usage - shared module
        tpref = f'{UT_DIR_REPO}/Simple3d'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 8)

            # Do the skip
            result = ModuleSkip(tpobj, onlylist='SCN PTH'.split()).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 4)
            self.assertEqual(len(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').raw()), 10)
            expect = r'''Version 1.0;

SubTestPlans
{
  ..\..\Modules\SCNX\scan.mtpl;
  ..\..\Modules\PTH\pth.mtpl;

  Final .\ProgramFlowsTestPlan\ProgramFlows_CLASS_TGLH81.mtpl;
}'''
            self.assertTextEqual(File(f'{tdir}/TPL/POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').read(), expect)

    def test_basic3(self):
        # via .json file
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            File(f'{tdir}/TPL/POR_TP/TGLH81/skip_modules.json').touch('{ "default": ["ARR"] }', newfile=True)
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)
            PlistEdit(tpobj).main()

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 8)

            # Do the skip
            result = ModuleSkip(tpobj).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            tpobj = TestProgram(tpenv)
            result = len(list(tpobj.mtpl.iter_flows()))
            self.assertEqual(result, 4)
            PlistEdit(tpobj).main()
            self.assertEqual(len(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').raw()), 10)

    def test_basic4tpi(self):
        # SkipModules - .txt
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            File(f'{tdir}/TPL/POR_TP/TGLH81/SkipModules/ARRX.txt').touch(mkdir=True)
            tpobj = TestProgram(tpenv)

            # Do the skip
            result = ModuleSkip(tpobj, skipfile=True).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            tpobj = TestProgram(tpenv)
            result = len(list(tpobj.mtpl.iter_flows()))
            self.assertEqual(result, 4)
            PlistEdit(tpobj).main()
            self.assertEqual(len(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').raw()), 10)

        # SkipModules - .permanent
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'
            File(f'{tdir}/TPL/POR_TP/TGLH81/SkipModules/ARRX.permanent').touch(mkdir=True)
            tpobj = TestProgram(tpenv)

            # Do the skip
            result = ModuleSkip(tpobj, skipfile=True).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_TGLH81.stpl'])

            tpobj = TestProgram(tpenv)
            result = len(list(tpobj.mtpl.iter_flows()))
            self.assertEqual(result, 4)
            PlistEdit(tpobj).main()
            self.assertEqual(len(File(f'{tdir}/TPL/POR_TP/TGLH81/PLIST_ALL.xml').raw()), 10)

        # ENG_TP version - ModuleSkip to do nothing on ENG_TP. We don't want ModuleSkip to doubly run on MV.
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            File(f'{tdir}/TPL/POR_TP').rename('ENG_TP')
            tpenv = f'{tdir}/TPL/ENG_TP/TGLH81/EnvironmentFile.env'
            File(f'{tdir}/TPL/ENG_TP/TGLH81/SkipModules/ARRX.txt').touch(mkdir=True)
            tpobj = TestProgram(tpenv)

            # Do the skip
            result = ModuleSkip(tpobj, skipfile=True).main()
            self.assertEqual(result, [])

            tpobj = TestProgram(tpenv)
            result = len(list(tpobj.mtpl.iter_flows()))
            self.assertEqual(result, 8)   # no change
            self.assertEqual(len(File(f'{tdir}/TPL/ENG_TP/TGLH81/PLIST_ALL.xml').raw()), 11)   # no change

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_mtlmv(self):
        # MTL mv tp
        tpref = f'{UT_DIR}/torch_mvtp_pass'
        tporig = TestProgram(f'{tpref}/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env').pickle_init()
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            tpenv = f'{tdir}/TPL/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env'
            tpobj = TestProgram(tpenv)

            # Reference first before skip
            result = len(list(tporig.mtpl.iter_flows()))
            self.assertEqual(result, 5259)
            lines = File(f'{tdir}/TPL/ENG_TP/Class_MTL_P68_DEBUG/PLIST_ALL_CLASS_P68G2.plist.xml').raw()
            self.assertEqual(len(lines), 47)
            lines = File(f'{tdir}/TPL/ENG_TP/Class_MTL_P68_DEBUG/PLIST_ALL_IP_CPU.plist.ipxml').raw()
            self.assertEqual(len(lines), 12)
            lines = File(f'{tdir}/TPL/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env').raw()
            self.assertEqual(len(lines), 706)

            # Do the skip
            result = ModuleSkip(tpobj, modlist=['FUN_CORE_C68']).main()
            self.assertEqual(result, ['SubTestPlan_CLASS_P68G2_g.stpl'])

            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 4771)

            lines = File(f'{tdir}/TPL/ENG_TP/Class_MTL_P68_DEBUG/PLIST_ALL_CLASS_P68G2.plist.xml').raw()
            self.assertEqual(len(lines), 47)   # unchanged
            lines = File(f'{tdir}/TPL/ENG_TP/Class_MTL_P68_DEBUG/PLIST_ALL_IP_CPU.plist.ipxml').raw()
            self.assertEqual(len(lines), 11)   # one removed
            lines = File(f'{tdir}/TPL/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env').raw()
            self.assertEqual(len(lines), 684)

            # confirm everything is good
            tpobj = TestProgram(tpenv)
            PlistEdit(tpobj).main()


class TestMvJson(TestCase):

    def test_read_mv_json(self):
        # FULL
        tpobj = TestProgram(f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env')
        result = MvJson().read_mv_json(tpobj, 'FULL')
        self.assertEqual(result, None)

        # specific json
        with Chdir(tpobj.tpldir):
            result = MvJson().read_mv_json(tpobj, 'FUN')
            self.assertEqual(result, {'ARR', 'PTH'})

    def test_get_mv_modules(self):
        # this testcase includes modules not included for this TP and module that is not found
        tpobj = TestProgram(f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env')
        result = MvJson().get_mv_modules(tpobj, ['AR', 'PTH', 'NOTFOUNDXX'])
        self.assertEqual(result, {'ARR', 'PTH'})

    @with_(TempDir, chdir=True, delete=True)
    def test_process_json_ut(self):
        # four json files, 3 levels
        File('p68_scn.txt').touch('''
[
  {
    "name": "P68_SCN",
    "modules": [
      "ARRX_"
    ],
    "config_imports": [
      "P68_BASE"
    ]
  }
]''')

        File('P68_ARR.json').touch('''
[
  {
    "name": "P68_ARR",
    "modules": [
      "ARR_"
    ],
    "config_imports": [
      "P68_BASE"
    ]
  }
]''')
        File('p68_base.json').touch('''
[
  {
    "name": "P68_BASE",
    "modules": [
                "CLK_BASE_CXX",
                "AAA_BASE"
    ],
    "config_imports": [
      "base"
        ]
  }
]''')
        File('base.json').touch('''
[
  {
    "name": "base",
    "modules": [
                "b1",
                "ARR_"
    ],
    "config_imports": [
        ]
  }
]
''')
        result = MvJson().process_json('.', 'P68_ARR')
        self.assertEqual(result, ['AAA_BASE', 'ARR_', 'CLK_BASE_CXX', 'b1'])

        with self.assertRaisesRegex(ErrorUser, 'does not exist in'):
            MvJson().process_json('.', 'P68_SCNX')


class Validation(TestCase):

    def all_modules(self):
        # Print all modules of this testprogram for module skip paste in json
        # Usage: Change TP below, then cut+paste into jon file
        tp = TestProgram('/intel/hdmxprogs/tgl/TGLXXXXBXH14W10S123/TPL/EnvironmentFile.env').pickle_init()
        result = []
        for mod in tp.mtpl.get_modules():
            if 'BASE' in mod:        # Cannot remove base module since concurrent use it
                continue
            if 'CONCURRENT' in mod:  # Cannot remove base module since concurrent use it
                continue
            result.append(mod)
        print(','.join(f'"{mod}"' for mod in result))

    def regress_allmod(self):
        # Try to regress, remove one module at a time, then run iter_flows(). See below.
        # Usage: mod/test/test_moduleskip.py -v Validation.regress_allmod | tee result; then grep for Success
        from gadget.shell import SystemCall
        from gadget.gizmo import Elapsed

        tpref = '/intel/hdmxprogs/tgl/TGLXXXXBXH14W10S123/TPL'
        tp = TestProgram(f'{tpref}/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as orig:
            shutil.copytree(tpref, f'{orig}/TPL')
            SystemCall(f'chmod +w -R {orig}').run_outonly()

            for mod in tp.mtpl.get_modules():
                print(f'Start Process {mod}')
                if 'BASE' in mod:        # Cannot remove base module since concurrent use it
                    continue
                if 'CONCURRENT' in mod:  # Cannot remove base module since concurrent use it
                    continue
                if mod in ['PHTD_RESET_CLASS']:    # concurrent use it
                    continue
                with TempDir(name=True) as tdir:
                    sw = Elapsed()
                    shutil.copytree(f'{orig}/TPL', f'{tdir}/TPL')
                    File(f'{tdir}/TPL/skip_modules.json').touch('{ "CLASS_TGLU42": ["%s"] }' % mod, newfile=True)
                    tp0 = TestProgram(f'{tdir}/TPL/EnvironmentFile.env')
                    ModuleSkip(tp0).main()
                    tp1 = TestProgram(f'{tdir}/TPL/EnvironmentFile.env')
                    result = len(list(tp1.mtpl.iter_flows()))
                    print(f"Success: count={result}, {sw}, {mod} skipped.")

    def test_moduleskip_fus_nvl(self):
        # test to proc ENV file for FUSE module special syntax
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir:
            tp.envdir = tdir
            text = '''
EXAMPLE0 = "hello";

ALEPH_FILES_0 = "hello" +
                "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE1 = "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES_1 = "test_case1_removing_line_at_the_end;" +
                "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
                "$FUSE_ROOT_DIR_G32/CSP/a.df.global.fuseconfig.json";

ALEPH_FILES_2 = "test_case2_removing_line_in_the_middle;" +
                "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
                "$FUSE_ROOT_DIR_G32/CSP/a.df.global.fuseconfig.json;" +
                "$FUSE_ROOT_DIR_CPU_INT/CSP/a.fuseDataLabel.json;" +
                "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE2 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
        "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES = "test_case3_mimic_real_nvl_gcd_env;" +
             #"$FUSE_ROOT_DIR_G32/fuseDef.json;" +
              "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
              "$FUSE_ROOT_DIR_G32/CSP/a.fuseDataLabel.json;" +
              "$FUSE_ROOT_DIR_PCD/CSP_PCD/fuseManager.vfconfigs.json;" +
              "$FUSE_ROOT_DIR_G32/CSP/fuseManager.vfconfigs.json;" +
              "./Modules/tpi/MOD_SKIP3/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
              "$FUSE_ROOT_DIR_G32/CSP/a.xf.reset.fuseconfig.json";
'''

            File(f'{tdir}/EnvironmentFile.env').touch(text)
            ms = ModuleSkip(tp)
            full_tp = {'MOD_SKIP1', 'FUS_FUSECFG_CXX', 'FUS_UNITINFO_CXX', 'FUS_FUSECFG_GXX', 'FUS_UNITINFO_GXX',
                       'FUS_FUSECFG_HXX', 'FUS_UNITINFO_HXX', 'FUS_FUSECFG_PXX', 'FUS_UNITINFO_PXX', 'MOD_SKIP2'}

            # Pass Case 1: No fuse module skipped in json file, return 1
            result = ms.moduleskip_fus_nvl(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'MOD_SKIP2'},
                                           {'MOD_SKIP1', 'MOD_SKIP2'})
            self.assertFalse(result)

            # Pass Case 2: All 2 G die fuse modules are skipped in json file, remove the FUSE_ROOT_DIR on a full tp.
            result2 = ms.moduleskip_fus_nvl(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'MOD_SKIP2', 'FUS_FUSECFG_GXX', 'FUS_UNITINFO_GXX'}, full_tp)

            expect2 = '''
EXAMPLE0 = "hello";

ALEPH_FILES_0 = "hello./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE1 = "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES_1 = "test_case1_removing_line_at_the_end;" +
    "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES_2 = "test_case2_removing_line_in_the_middle;" +
    "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "$FUSE_ROOT_DIR_CPU_INT/CSP/a.fuseDataLabel.json;" +
    "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE2 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES = "test_case3_mimic_real_nvl_gcd_env;" +
    "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "$FUSE_ROOT_DIR_PCD/CSP_PCD/fuseManager.vfconfigs.json;" +
    "./Modules/tpi/MOD_SKIP3/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

#"$FUSE_ROOT_DIR_G32/fuseDef.json;" +
'''
            self.assertTextEqual(result2, expect2)

            # Pass Case 3: All 2 C and G die fuse modules are skipped in json file, remove the FUSE_ROOT_DIR on a full tp.
            result3 = ms.moduleskip_fus_nvl(ms.get_env_name('BLAH'),
                                            {'MOD_SKIP1', 'MOD_SKIP2', 'FUS_FUSECFG_CXX', 'FUS_UNITINFO_CXX', 'FUS_FUSECFG_GXX', 'FUS_UNITINFO_GXX'}, full_tp)

            expect3 = '''
EXAMPLE0 = "hello";

ALEPH_FILES_0 = "hello./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE1 = "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES_1 = "test_case1_removing_line_at_the_end;" +
    "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES_2 = "test_case2_removing_line_in_the_middle;" +
    "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE2 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES = "test_case3_mimic_real_nvl_gcd_env;" +
    "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "$FUSE_ROOT_DIR_PCD/CSP_PCD/fuseManager.vfconfigs.json;" +
    "./Modules/tpi/MOD_SKIP3/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

#"$FUSE_ROOT_DIR_G32/fuseDef.json;" +
'''
            self.assertTextEqual(result3, expect3)

            # Pass Case 4: All 2 C, G, H, P die fuse modules are skipped in json file, remove the FUSE_ROOT_DIR on a full tp.
            result4 = ms.moduleskip_fus_nvl(ms.get_env_name('BLAH'),
                                            {'MOD_SKIP1', 'MOD_SKIP2', 'FUS_FUSECFG_CXX', 'FUS_UNITINFO_CXX',
                                             'FUS_FUSECFG_GXX', 'FUS_UNITINFO_GXX', 'FUS_FUSECFG_HXX', 'FUS_UNITINFO_HXX',
                                             'FUS_FUSECFG_PXX', 'FUS_UNITINFO_PXX'}, full_tp)

            expect4 = '''
EXAMPLE0 = "hello";

ALEPH_FILES_0 = "hello./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE1 = "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES_1 = "test_case1_removing_line_at_the_end;" +
    "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES_2 = "test_case2_removing_line_in_the_middle;" +
    "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

EXAMPLE2 = "./Modules/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "./Modules/tpi/MOD_SKIP2/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

ALEPH_FILES = "test_case3_mimic_real_nvl_gcd_env;" +
    "./Modules/tpi/MOD_SKIP1/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json;" +
    "./Modules/tpi/MOD_SKIP3/InputFiles/freq_ifpm_gt_PatConfigSetpoints.json";

#"$FUSE_ROOT_DIR_G32/fuseDef.json;" +
'''
            self.assertTextEqual(result4, expect4)

            # Fail Case 1: Only one C die fuse module skipped in json file, raise error on a full TP
            with self.assertRaisesRegex(ErrorUser, "Can NOT skip only FUS_FUSECFG_CXX module"):
                ms.moduleskip_fus_nvl(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'FUS_FUSECFG_CXX', 'MOD_SKIP2'}, full_tp)

            # Fail Case 2: G, H die fuse module skipped in json file, raise error on a full TP
            with self.assertRaisesRegex(ErrorUser, "Can NOT skip only FUS_FUSECFG"):
                ms.moduleskip_fus_nvl(ms.get_env_name('BLAH'), {'MOD_SKIP1', 'FUS_FUSECFG_GXX', 'FUS_FUSECFG_HXX', 'MOD_SKIP2'}, full_tp)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

# /intel/hdmxprogs/tgl/TGLXXXXBXH14W10S123/TPL, regress_allmod(), via pypy
# Success: count=8107, 4.581 Secs, ARR_CCF skipped.
# Success: count=8283, 3.393 Secs, ARR_CCF_RAMPDOWN skipped.
# Success: count=8279, 3.254 Secs, ARR_COMMON skipped.
# Success: count=8114, 3.296 Secs, ARR_CORE skipped.
# Success: count=8273, 3.176 Secs, ARR_CORE_CCR skipped.
# Success: count=8259, 3.088 Secs, ARR_CORE_RAMPDOWN skipped.
# Success: count=8134, 3.462 Secs, ARR_DE skipped.
# Success: count=7883, 3.069 Secs, ARR_GT1 skipped.
# Success: count=7968, 3.203 Secs, ARR_IPU skipped.
# Success: count=8213, 3.172 Secs, ARR_MBIST skipped.
# Success: count=8282, 3.447 Secs, ARR_MBIST_VMAX skipped.
# Success: count=8207, 4.159 Secs, CLK_ADPLL_ALL skipped.
# Success: count=8251, 4.180 Secs, CLK_CLKCOMP_ALL skipped.
# Success: count=8262, 4.765 Secs, CLK_CRO_ALL skipped.
# Success: count=8218, 3.502 Secs, CLK_DLCPLL_ALL skipped.
# Success: count=8226, 4.961 Secs, CLK_FLL_ALL skipped.
# Success: count=8205, 4.024 Secs, CLK_LJPLL_ALL skipped.
# Success: count=8110, 3.616 Secs, DRV_RESET skipped.
# Success: count=8276, 3.088 Secs, DRV_RESET_MCP skipped.
# Success: count=8265, 3.175 Secs, FUNC_CORE_CCR skipped.
# Success: count=7689, 3.368 Secs, FUN_CORE skipped.
# Success: count=8230, 3.201 Secs, FUN_DE skipped.
# Success: count=7888, 3.167 Secs, FUN_GT skipped.
# Success: count=8282, 3.052 Secs, FUN_GT_THR skipped.
# Success: count=7839, 3.042 Secs, FUN_SA skipped.
# Success: count=8282, 3.486 Secs, FUS_FACT skipped.
# Success: count=8288, 3.382 Secs, FUS_FLE skipped.
# Success: count=8212, 3.468 Secs, FUS_FUSEBURN skipped.
# Success: count=8281, 3.945 Secs, FUS_FUSECFG skipped.
# Success: count=8261, 3.767 Secs, FUS_FUSEREAD skipped.
# Success: count=8251, 3.239 Secs, FUS_UNITINFO skipped.
# Success: count=8248, 3.173 Secs, MIO_DDR_AC skipped.
# Success: count=8270, 3.233 Secs, MIO_DDR_DC skipped.
# Success: count=8282, 3.343 Secs, MIO_DDR_FUSE skipped.
# Success: count=8240, 3.433 Secs, MIO_POPIO skipped.
# Success: count=8246, 3.192 Secs, PARR_MBISTKS_CLASS skipped.
# Success: count=8233, 3.606 Secs, PCLK_PLL skipped.
# Success: count=8281, 3.273 Secs, PCLK_RTC skipped.
# Success: count=8104, 3.606 Secs, PFUN_CORE skipped.
# Success: count=8231, 3.417 Secs, PFUS_FUSEBURN skipped.
# Success: count=8288, 3.149 Secs, PFUS_FUSECFG skipped.
# Success: count=8271, 3.108 Secs, PFUS_FUSEIFP skipped.
# Success: count=8263, 3.161 Secs, PFUS_FUSEREAD skipped.
# Success: count=8242, 3.791 Secs, PFUS_UNITINFO skipped.
# Success: count=8286, 3.082 Secs, PHTD_RESET_CLASS_PKG skipped.
# Success: count=8287, 3.255 Secs, PHTD_RESET_DFX skipped.
# Success: count=8283, 3.082 Secs, PMIO_POPIO skipped.
# Success: count=8255, 3.404 Secs, PPTH_DTS skipped.
# Success: count=8279, 3.066 Secs, PPTH_FIVR_LVR skipped.
# Success: count=8218, 3.090 Secs, PPTH_FIVR_OPS skipped.
# Success: count=8271, 3.589 Secs, PPTH_FIVR_TRIM skipped.
# Success: count=8258, 3.813 Secs, PPTH_LDO skipped.
# Success: count=8281, 3.790 Secs, PPTH_POWER skipped.
# Success: count=8286, 3.463 Secs, PPTH_POWER_DWN1 skipped.
# Success: count=8286, 3.201 Secs, PPTH_POWER_DWN2 skipped.
# Success: count=8285, 3.128 Secs, PPTH_SCVR_ICCMAX skipped.
# Success: count=8287, 3.433 Secs, PPTH_SCVR_TRIM skipped.
# Success: count=8181, 3.078 Secs, PSCN_SCN_X skipped.
# Success: count=8193, 3.116 Secs, PSIO_BSCAN_ALL1 skipped.
# Success: count=8252, 3.112 Secs, PSIO_CNVI_ALL1 skipped.
# Success: count=8242, 3.207 Secs, PSIO_LEAKAGE_ALL1 skipped.
# Success: count=8186, 3.336 Secs, PSIO_PCIE_ALL1 skipped.
# Success: count=8262, 3.118 Secs, PSIO_PCIE_ALL2 skipped.
# Success: count=8275, 3.147 Secs, PSIO_SATA_ALL1 skipped.
# Success: count=8184, 3.105 Secs, PSIO_USB2_ALL1 skipped.
# Success: count=8252, 3.464 Secs, PSIO_USB3_ALL1 skipped.
# Success: count=8282, 3.131 Secs, PTH_DIODE_DIEFORCE skipped.
# Success: count=8286, 3.148 Secs, PTH_DIODE_PRECHKF6 skipped.
# Success: count=8286, 3.127 Secs, PTH_DIODE_PSTCHKF6 skipped.
# Success: count=8250, 3.213 Secs, PTH_DIODE_SOT skipped.
# Success: count=8282, 3.346 Secs, PTH_DIODE_THRSOAK skipped.
# Success: count=8239, 3.072 Secs, PTH_DTS skipped.
# Success: count=8214, 3.080 Secs, PTH_FIVR_IMON skipped.
# Success: count=8221, 3.119 Secs, PTH_FIVR_OPSC skipped.
# Success: count=8254, 3.365 Secs, PTH_FIVR_TRIMC skipped.
# Success: count=8263, 3.051 Secs, PTH_POWER skipped.
# Success: count=8287, 3.117 Secs, PTH_VDAC_SETUP skipped.
# Success: count=8278, 3.126 Secs, PTH_VREFLDO skipped.
# Success: count=8259, 3.113 Secs, PTPI_SHOPS skipped.
# Success: count=8219, 3.315 Secs, PTPI_VCC skipped.
# Success: count=8284, 3.067 Secs, QNR_CARV skipped.
# Success: count=7959, 3.053 Secs, SCN_CCF skipped.
# Success: count=8098, 3.075 Secs, SCN_CORE skipped.
# Success: count=8088, 3.265 Secs, SCN_DE skipped.
# Success: count=7707, 3.016 Secs, SCN_GT skipped.
# Success: count=7965, 3.327 Secs, SCN_IPU skipped.
# Success: count=8085, 3.092 Secs, SCN_SOC skipped.
# Success: count=8239, 3.241 Secs, SCN_SOC_CCR skipped.
# Success: count=8266, 3.333 Secs, SIO_BSCAN skipped.
# Success: count=8274, 3.131 Secs, SIO_CSI_DC1 skipped.
# Success: count=8255, 3.964 Secs, SIO_CSI_LPBK1 skipped.
# Success: count=8280, 3.403 Secs, SIO_DP_DC1 skipped.
# Success: count=8282, 3.227 Secs, SIO_DP_DC2 skipped.
# Success: count=8273, 3.192 Secs, SIO_DP_LPBK1 skipped.
# Success: count=8264, 3.298 Secs, SIO_DSI_DC1 skipped.
# Success: count=8282, 3.138 Secs, SIO_DSI_DC2 skipped.
# Success: count=8281, 3.159 Secs, SIO_DSI_DC3 skipped.
# Success: count=8270, 3.230 Secs, SIO_DSI_LPBK1 skipped.
# Success: count=8288, 3.589 Secs, SIO_INIT skipped.
# Success: count=8275, 3.907 Secs, SIO_LEAKAGE_X skipped.
# Success: count=8272, 3.226 Secs, SIO_PCIE_DC1 skipped.
# Success: count=8181, 3.461 Secs, SIO_PCIE_LPBK1 skipped.
# Success: count=8178, 3.256 Secs, SIO_TCSS_ALL1 skipped.
# Success: count=8233, 3.397 Secs, SIO_VIXVOX skipped.
# Success: count=8288, 3.218 Secs, TPI_CCR skipped.
# Success: count=8287, 3.076 Secs, TPI_CONTTR skipped.
# Success: count=8288, 3.045 Secs, TPI_DEDC skipped.
# Success: count=8257, 3.131 Secs, TPI_DFF skipped.
# Success: count=8287, 3.460 Secs, TPI_DLCP_MIXDET skipped.
# Success: count=8280, 3.134 Secs, TPI_EDM skipped.
# Success: count=8288, 3.076 Secs, TPI_EXPRESS skipped.
# Success: count=8287, 3.084 Secs, TPI_FACT_FORK skipped.
# Success: count=8263, 3.158 Secs, TPI_GFX_AGG skipped.
# Success: count=8284, 3.428 Secs, TPI_IDUT_FORK skipped.
# Success: count=8287, 3.080 Secs, TPI_IDUT_FORKEND skipped.
# Success: count=8281, 3.309 Secs, TPI_IDV_CLASS skipped.
# Success: count=8273, 3.117 Secs, TPI_IPUFLEXBOM skipped.
# Success: count=8277, 3.406 Secs, TPI_PWR_CTRL skipped.
# Success: count=8279, 3.065 Secs, TPI_SETFLOW skipped.
# Success: count=8250, 3.066 Secs, TPI_SHOPS skipped.
# Success: count=8122, 3.087 Secs, TPI_VCC skipped.
# Success: count=8281, 3.398 Secs, TPI_VCC_MIMS skipped.
# Success: count=8279, 3.437 Secs, TPI_VCC_OPEN skipped.
# Success: count=8287, 3.283 Secs, YBS_FVMIN_UPLOAD skipped.
# Success: count=8287, 3.441 Secs, YBS_INTERP_POST skipped.
# Success: count=8287, 3.708 Secs, YBS_INTERP_PRE skipped.
# Success: count=8288, 3.360 Secs, YBS_LICENSE skipped.
# Success: count=8271, 3.205 Secs, YBS_SELECT_FLOW skipped.
# Success: count=8284, 3.641 Secs, YBS_UPSE skipped.
# Success: count=8286, 3.385 Secs, YBS_UPSS skipped.
# Success: count=8285, 3.855 Secs, YBS_UPSVF_PRINT skipped.
