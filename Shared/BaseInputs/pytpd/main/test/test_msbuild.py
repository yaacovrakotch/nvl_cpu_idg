#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for msbuild
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, MockVar, Mock
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.disk import Chdir, mkdirs
from main.msbuild import *
from os.path import join, dirname, abspath


class TestMSBuild(TestCase):

    @with_(MockVar, TPSwitch, 'main', Mock())
    def test_pass_build_dll(self):

        with TempDir(name=True, chdir=True, delete=True):
            mkdirs('abc')
            File('abc/POR_TP/Class_NVL_S28C/a.tpproj').touch(mkdir=True)
            File('abc/UserCode/bin/blah.dll').touch(mkdir=True)
            File('abc/UserCode/lib/blah.dll').touch(mkdir=True)
            File('abc/Shared/BaseInputs/Common/Common_Class_NVL_S28C/EnvironmentFile_Common.env').touch(mkdir=True)
            with MockVar(sys, 'argv', ['script', 'abc/a.sln']), \
                    MockVar(MSBuild, 'choices', ['/tmp']), \
                    MockVar(MSBuild, 'get_user_input', Mock(return_value='Class_NVL_S28C')), \
                    MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, '\n1 Error(s)\nsome-line\n', ''))), \
                    MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):

                obj = MSBuild()
                obj.main()
                self.assertEqual(len(obj._ut_tpproj), 1)

            # No valid choice
            with MockVar(sys, 'argv', ['script', 'abc/a.sln']), \
                    MockVar(MSBuild, 'get_user_input', Mock(return_value='Class_NVL_S28C')):
                with self.assertRaises(SystemExit):
                    MSBuild().main()

    @with_(MockVar, TPSwitch, 'main', Mock())
    @with_(TempDir, chdir=True)
    def test_pass_copy_dll(self):

        # ================== Copy Freddy dll first
        # folder structure: I:/tpapps/userlibs/nvl/prime_v13.2.0-ddg251600/lib/Release/net6.0
        # PRIME_DLL_PATH = "I:/tpapps/userlibs/nvl/prime_v13.2.0-ddg251600"
        # output: Usercode/lib/Release/net6.0

        # ================== Copy custom dll's
        # folder structure: I:/tpapps/userlibs/nvl/modules/prime_v13.2.0/binning/UPS2517_UC1.0_eng/*.dll
        # BINNING_USERCODE_PATH = "binning/UPS2517_UC1.0_eng"
        # PRIME_DLL_PATH = "<freddypath>; I:/tpapps/userlibs/nvl/modules/prime_v13.2.0/$BINNING_USERCODE_PATH
        # output: Usercode/lib/Release/custom/binning/UPS2517_UC1.0_eng/*.dll

        tdir = os.getcwd()
        File('freddy/lib/Release/net6.0/blah.dll').touch(mkdir=True)
        File('binning/UPS2517_UC1.0_eng/ups.dll').touch(mkdir=True)

        File('tp/POR_TP/Class_NVL_S28C/a.tpproj').touch(mkdir=True)
        File('tp/Shared/BaseInputs/Common/Common_Class_NVL_S28C/EnvironmentFile_Common.env').touch(f'''
BINNING_USERCODE_PATH = "binning/UPS2517_UC1.0_eng";
PRIME_DLL_PATH = "{tdir}/freddy; {tdir}/$BINNING_USERCODE_PATH";
''', mkdir=True)

        with MockVar(sys, 'argv', ['script', 'tp/a.sln']), \
                MockVar(MSBuild, 'get_user_input', Mock(return_value='Class_NVL_S28C')), \
                MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, '\n1 Error(s)\nsome-line\n', ''))), \
                MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):

            obj = MSBuild()
            obj.main()

        self.assertEqual(os.listdir('tp/Usercode/lib/Release/custom/binning'), ['UPS2517_UC1.0_eng'])
        self.assertEqual(set(os.listdir('tp/Usercode/lib/Release')), {'custom', 'net6.0'})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_integrate(self):

        File('freddy/lib/Release/net6.0/blah.dll').touch(mkdir=True)
        File('binning/UPS2517_UC1.0_eng/ups.dll').touch(mkdir=True)
        File('Shared/BaseInputs/Common/Common_TGLH81/EnvironmentFile_Common.env').touch(f'''
BINNING_USERCODE_PATH = "binning/UPS2517_UC1.0_eng";
PRIME_DLL_PATH = "./freddy; ./$BINNING_USERCODE_PATH";
''', mkdir=True)

        with MockVar(sys, 'argv', ['script', 'a.sln', 'TGLH81']), \
                MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, '\n1 Error(s)\nsome-line\n', ''))), \
                MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):

            obj = MSBuild()
            obj.main()      # must be success

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_integrate_allbom(self):
        File('freddy/lib/Release/net6.0/blah.dll').touch(mkdir=True)
        File('binning/UPS2517_UC1.0_eng/ups.dll').touch(mkdir=True)
        File('Shared/BaseInputs/Common/Common_Class_NVL_S28C/EnvironmentFile_Common.env').touch(f'''
BINNING_USERCODE_PATH = "binning/UPS2517_UC1.0_eng";
PRIME_DLL_PATH = "./freddy; ./$BINNING_USERCODE_PATH";
''', mkdir=True)

        with MockVar(sys, 'argv', ['script', 'a.sln', 'All']), \
                MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, '\n1 Error(s)\nsome-line\n', ''))), \
                MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            obj = MSBuild()
            obj.main('a.sln', 'All')  # must be success

    @with_(MockVar, TPSwitch, 'main', Mock())
    def test_pass_dot(self):
        # Test root dot path

        with TempDir(name=True, chdir=True, delete=True):
            File('POR_TP/a/a.tpproj').touch(mkdir=True)
            File('UserCode/bin/blah.dll').touch(mkdir=True)
            File('UserCode/lib/blah.dll').touch(mkdir=True)
            File('Shared/BaseInputs/Common/Common_a/EnvironmentFile_Common.env').touch(mkdir=True)
            with MockVar(sys, 'argv', ['script', 'a.sln', 'a']), \
                    MockVar(MSBuild, 'choices', ['/tmp']), \
                    MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, '\n1 Error(s)\nsome-line\n', ''))), \
                    MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):

                obj = MSBuild()
                obj.main()
                self.assertEqual(len(obj._ut_tpproj), 1)

    @with_(MockVar, TPSwitch, 'main', Mock())
    def test_fail(self):

        with TempDir(name=True, chdir=True, delete=True):
            File('abc/POR_TP/a/a.tpproj').touch(mkdir=True)
            File('abc/Shared/BaseInputs/Common/Common_a/EnvironmentFile_Common.env').touch(mkdir=True)
            with MockVar(sys, 'argv', ['script', 'abc/a.sln', 'a']), \
                    MockVar(MSBuild, 'choices', ['/tmp']), \
                    MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, '2 Error(s)', ''))), \
                    MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):

                with self.assertRaises(SystemExit):
                    MSBuild().main()

                # skipbuild - no error
                with MockVar(os.environ, 'SKIPBUILD', 'True'):
                    MSBuild().main()

    def test_get_user_input(self):
        with MockVar(sys, 'argv', ['a.py', 'tpproj']):
            self.assertEqual(MSBuild().get_user_input(None), 'All')

        with MockVar(sys, 'argv', ['a.py', 'tpproj', 'BOM1']):
            self.assertEqual(MSBuild().get_user_input(None), 'BOM1')

        with MockVar(sys, 'argv', ['a.py', 'tpproj', 'BOM1', 'blah']):
            self.assertEqual(MSBuild().get_user_input(None), 'BOM1')
            self.assertEqual(MSBuild().get_user_input('BOM2'), 'BOM2')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_env_reorder(self):
        result = MSBuild().env_reorder('.', ispostproc=True, inputbom='TGLH81')
        self.assertEqual(result, 1)
        self.assertEqual(MSBuild().env_reorder('.', ispostproc=False, inputbom=None), -1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_auto_content_pymtpl(self):
        pyfile = f'ACPY:{UT_DIR_REPO}/misc_files/pymtpl2.py'
        with MockVar(os.environ, 'ACPY', pyfile):
            self.assertEqual(MSBuild.auto_content_pymtpl('TGLH81', '.'), None)
        outfile = File('Modules/FUN_CCF/fun_ccf.mtpl').read()
        self.assertIn('Test VminTC SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X_CCFBIST', outfile)

        with MockVar(os.environ, 'ACPY', 'None'):
            self.assertEqual(MSBuild.auto_content_pymtpl('TGLH81', '.'), 1)
        with MockVar(os.environ, 'ACPY', '100C'):
            self.assertEqual(MSBuild.auto_content_pymtpl('TGLH81', '.'), 2)

    @with_(TempDir, chdir=True)
    def test_ip_trialvars_hack(self):
        obj = MSBuild()

        # case1 - missing file
        self.assertEqual(obj.ip_trialvars_hack('TGLH1', '.'), 1)

        # case2 - dielet TP
        File('Shared/Modules/TPI/TPI_TRIALVAR_CXX/cpu_ip_trials.mtpl').touch(mkdir=True)

        stpl = 'POR_TP/TGLH1/SubTestPlan.stpl'
        File(stpl).touch('''Version 1.0;
SubTestPlans
{
    IPName IPC
    {
        Common "../../BaseInputs/CPU/CPU_Torch/cpu_ip_base.imp";
        "../../Modules/ARR/ARR_ATOM_CX816/ARR_ATOM_CX816.mtpl";
        "../../Modules/ARR/ARR_CCF_CX816/ARR_CCF_CX816.mtpl";
        Final "./ProgramFlowsTestPlan/IPC_FLOWS.mtpl";
    }
    "../../Shared/Modules/TPI/TPI_FLWFLGS_XXX/TPI_FLWFLGS_XXX.mtpl";
    "../../Shared/Modules/TPI/TPI_BASE_XXX/TPI_BASE_XXX.mtpl";
    "../../Shared/Modules/FUS/FUS_ISEED_XXX/FUS_ISEED_XXX.mtpl";
    "../../Shared/Modules/MIO/MIO_D2D_XXX/MIO_D2D_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
''', mkdir=True)
        obj.ip_trialvars_hack('TGLH1', '.')
        expect = '''
Version 1.0;
SubTestPlans
{
    IPName IPC
    {
        Common "../../BaseInputs/CPU/CPU_Torch/cpu_ip_base.imp";
        "../../Shared/Modules/TPI/TPI_TRIALVAR_CXX/cpu_ip_trials.mtpl";
        "../../Modules/ARR/ARR_ATOM_CX816/ARR_ATOM_CX816.mtpl";
        "../../Modules/ARR/ARR_CCF_CX816/ARR_CCF_CX816.mtpl";
        Final "./ProgramFlowsTestPlan/IPC_FLOWS.mtpl";
    }
    IPName IPG
    {
        "../../Shared/Modules/TPI/TPI_TRIALVAR_GXX/gcd_ip_trials.mtpl";
    }
    IPName IPH
    {
        "../../Shared/Modules/TPI/TPI_TRIALVAR_HXX/hub_ip_trials.mtpl";
    }
    IPName IPP
    {
        "../../Shared/Modules/TPI/TPI_TRIALVAR_PXX/pcd_ip_trials.mtpl";
    }
    "../../Shared/Modules/TPI/TPI_FLWFLGS_XXX/TPI_FLWFLGS_XXX.mtpl";
    "../../Shared/Modules/TPI/TPI_BASE_XXX/TPI_BASE_XXX.mtpl";
    "../../Shared/Modules/FUS/FUS_ISEED_XXX/FUS_ISEED_XXX.mtpl";
    "../../Shared/Modules/MIO/MIO_D2D_XXX/MIO_D2D_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
'''
        self.assertTextEqual(File(stpl).read(), expect)

        # case3 - fulltp - just rerun
        obj.ip_trialvars_hack('TGLH1', '.')
        expect = '''
Version 1.0;
SubTestPlans
{
    IPName IPC
    {
        Common "../../BaseInputs/CPU/CPU_Torch/cpu_ip_base.imp";
        "../../Shared/Modules/TPI/TPI_TRIALVAR_CXX/cpu_ip_trials.mtpl";
        "../../Shared/Modules/TPI/TPI_TRIALVAR_CXX/cpu_ip_trials.mtpl";
        "../../Modules/ARR/ARR_ATOM_CX816/ARR_ATOM_CX816.mtpl";
        "../../Modules/ARR/ARR_CCF_CX816/ARR_CCF_CX816.mtpl";
        Final "./ProgramFlowsTestPlan/IPC_FLOWS.mtpl";
    }
    IPName IPG
    {
        "../../Shared/Modules/TPI/TPI_TRIALVAR_GXX/gcd_ip_trials.mtpl";
    }
    IPName IPH
    {
        "../../Shared/Modules/TPI/TPI_TRIALVAR_HXX/hub_ip_trials.mtpl";
    }
    IPName IPP
    {
        "../../Shared/Modules/TPI/TPI_TRIALVAR_PXX/pcd_ip_trials.mtpl";
    }
    "../../Shared/Modules/TPI/TPI_FLWFLGS_XXX/TPI_FLWFLGS_XXX.mtpl";
    "../../Shared/Modules/TPI/TPI_BASE_XXX/TPI_BASE_XXX.mtpl";
    "../../Shared/Modules/FUS/FUS_ISEED_XXX/FUS_ISEED_XXX.mtpl";
    "../../Shared/Modules/MIO/MIO_D2D_XXX/MIO_D2D_XXX.mtpl";
    Final "./ProgramFlowsTestPlan/ProgramFlows.mtpl";
}
'''
        self.assertTextEqual(File(stpl).read(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
