#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for torch_mv.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from main.torch_mv import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.disk import Chdir, Allfiles
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from gadget.printmore import Dumper
from tp.testprogram import PgmRules
from unittest.mock import Mock
import sys
import shutil
import main.torch_mv as torch_mv


class TestReplJson(TestCase):

    def test_init(self):
        with TempDir(name=True, delete=True, chdir=True) as tdir:
            code = '''{
  "ff.txt": [

  {"comment": "comment all FORCE_EVMINS lines",
   "search": "FORCE_EVMINS",
   "replace": "# FORCE_EVMINS" }

]
}
'''
            ff_json = File(f'{tdir}/TPConfig/ReplaceJson/mv_evmins.json').touch(code, mkdir=True)

            # repldata check - normal
            bt = ReplJson('mv_evmins')
            self.assertEqual(bt.repldata.keys(), {'ff.txt'})

            # repldata check - with extension
            bt = ReplJson('mv_evmins.json')
            self.assertEqual(bt.repldata.keys(), {'ff.txt'})

            # repldata check - full path
            bt = ReplJson(ff_json.get_name())
            self.assertEqual(bt.repldata.keys(), {'ff.txt'})

            # repldata check - full path
            bt = ReplJson('')
            self.assertEqual(bt.repldata, {})

            # repldata check - full path
            bt = ReplJson('None')
            self.assertEqual(bt.repldata, {})

    def test_apply(self):
        with TempDir(name=True, delete=True, chdir=True) as tdir:
            File(f'{tdir}/UBE/mrobot_a/a.ube').touch(mkdir=True)
            code = '''{
  "ff.txt": [

  {"comment": "comment all FORCE_EVMINS lines",
   "search": "FORCE_EVMINS",
   "replace": "# FORCE_EVMINS" },

  {"comment": "add these two lines",
   "search": "# EVMINS write control",
   "replace": ["# EVMINS write control",
               "bypass_global = 1,   line1",
               "FORCE_EVMINS  = 1,   line2"
               ]
   }

]
}
'''
            File(f'{tdir}/TPConfig/ReplaceJson/mv_evmins.json').touch(code, mkdir=True)
            data = '''
blah

# EVMINS write control
FORCE_EVMINS  = 1,   linex
FORCE_EVMINS  = 0,   liney
'''
            File('ff.txt').touch(data)

            # repldata check - normal
            bt = ReplJson('mv_evmins')
            bt.apply()
            expect = '''
blah

# EVMINS write control
bypass_global = 1,   line1
FORCE_EVMINS  = 1,   line2
# FORCE_EVMINS  = 1,   linex
# FORCE_EVMINS  = 0,   liney
'''
            self.assertTextEqual(File('ff.txt').read(), expect)

            # double
            File('ff.txt').touch(data, newfile=True)
            bt = ReplJson('mv_evmins,mv_evmins')
            bt.apply()
            self.assertTextEqual(File('ff.txt').read(), expect)

            # no data
            bt = ReplJson('')
            bt.apply()
            self.assertEqual(bt.repldata, {})

    def test_apply2(self):
        with TempDir(name=True, delete=True, chdir=True) as tdir:
            code = '''{
  "ff1.txt": [

  {"comment": "comment all FORCE_EVMINS lines",
   "search": "FORCE_EVMINS",
   "replace": "# FORCE_EVMINS" }

]
}
'''
            File(f'{tdir}/TPConfig/ReplaceJson/mv1.json').touch(code, mkdir=True)
            code = '''{
  "ff2.txt": [

  {"comment": "add these two lines",
   "search": "# EVMINS write control",
   "replace": ["# EVMINS write control",
               "bypass_global = 1,   line1",
               "FORCE_EVMINS  = 1,   line2"
               ]
   }

]
}
'''
            File(f'{tdir}/TPConfig/ReplaceJson/mv2.json').touch(code, mkdir=True)
            data = '''
blah

# EVMINS write control
FORCE_EVMINS  = 1,   linex
FORCE_EVMINS  = 0,   liney
'''
            File('ff1.txt').touch(data)
            data = '''
blah

# EVMINS write control
FORCE_EVMINS  = 1,   linex
FORCE_EVMINS  = 0,   liney
'''
            File('ff2.txt').touch(data)

            # repldata check - comma
            bt = ReplJson('mv1,mv2')
            with Chdir(f'{tdir}/TPConfig'):
                bt.apply(tdir)
            expect = '''
blah

# EVMINS write control
# FORCE_EVMINS  = 1,   linex
# FORCE_EVMINS  = 0,   liney
'''
            self.assertTextEqual(File('ff1.txt').read(), expect)
            expect = '''
blah

# EVMINS write control
bypass_global = 1,   line1
FORCE_EVMINS  = 1,   line2
FORCE_EVMINS  = 1,   linex
FORCE_EVMINS  = 0,   liney
'''
            self.assertTextEqual(File('ff2.txt').read(), expect)


class TestMV(TestCase):

    def test_process_json_mtl(self):
        result = DoMV().process_json(f'{UT_DIR_REPO}/torch_p6828_fixer/TPConfig/MV_Templates', 'P68_ARR')
        self.assertEqual(len(result), 63)

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
        result = DoMV().process_json('.', 'P68_ARR')
        self.assertEqual(result, ['AAA_BASE', 'ARR_', 'CLK_BASE_CXX', 'b1'])

        with self.assertRaisesRegex(ErrorUser, 'does not exist in'):
            DoMV().process_json('.', 'P68_SCNX')

    @with_(TempDir, chdir=True, delete=True)
    def test_process_json_uterr(self):
        # bad json file
        File('P68_ARR.json').touch('''
[
  {
    "name": "ARR"
    "modules": [
      "ARR_"
    ],
    "config_imports": [
      "P68_BASE"
    ]
  }
]''')

        with self.assertRaisesRegex(ErrorInput, 'P68_ARR.json'):
            DoMV().process_json('.', 'P68_ARR')

    def test_json_load(self):
        # pass case
        with TempDir(chdir=True, delete=True):
            File(f'p68_arr.json').touch('''
    [ { "name": "P68_ARR",
        "modules": [ "ARRX"
         ],
        "config_imports": [ ]
      }
    ]''')
            self.assertEqual(DoMV().process_json('.', 'p68_arR.json'), ['ARRX'])

        # with fix case
        with TempDir(chdir=True, delete=True):
            File(f'p68_arr.json').touch('''
    [ { "name": "P68_ARR",
        "modules": [ "ARRX",
         ],
        "config_imports": [ ]
      }
    ]''')
            self.assertEqual(DoMV().process_json('.', 'P68_ARR'), ['ARRX'])

        # problematic case
        with TempDir(chdir=True, delete=True):
            File(f'p68_ar.json').touch('''
    [ { "name": "P68_ARR",
        "modules": [ "ARRX",     # comment not supported
         ],
        "config_imports": [ ]
      }
    ]''')
            with self.assertRaisesRegex(ErrorUser, 'does not exist'):
                DoMV().process_json('.', 'P68_ARR')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_mv_modules(self):
        # this testcase includes modules not included for this TP and module that is not found
        tp = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        result = DoMV().get_mv_modules(tp, ['ARR_CORE', 'TPI_BASEPRIM_Y68K', 'TPI_BASEPRIM_Y28K', 'NOTFOUNDXX'])
        self.assertEqual(result, {'ARR_CORE_C68K', 'ARR_CORE_C68', 'TPI_BASEPRIM_XXX'})

    @with_(TempDir, chdir=True, delete=True)
    def test_delete_folder(self):

        f1 = File('Modules/ABC/abc.mtpl').touch(mkdir=True)
        f2 = File('Modules/GHI/abc.mtpl').touch(mkdir=True)
        f3 = File('Shared/JKL/abc.mtpl').touch(mkdir=True)
        f4 = File('ProgramFlowsTestPlan/ProgramFlows.mtpl').touch(mkdir=True)
        f5 = File('Unknown/a.mtpl').touch(mkdir=True)

        mv = DoMV()
        mv.fullpath_mtpl = {f1.get_name(): True,
                            f2.get_name(): True,
                            f3.get_name(): True,
                            f4.get_name(): True,
                            f5.get_name(): True,
                            }
        mv.mod_folder_keep = {'ABC'}
        mv.delete_folder()
        self.assertEqual(sorted(Allfiles('.')),
                         ['./Modules/ABC/abc.mtpl',
                          './ProgramFlowsTestPlan/ProgramFlows.mtpl',
                          './Shared/JKL/abc.mtpl',
                          './Unknown/a.mtpl'])

    def test_build_process(self):
        out = r'''
'Build Test Program' started.
/blah/Modules/FUN_CORE_C2P/FUN_CORE_C2P_CLASS_P28G1.usrv(6203,50,6203,85): TPL/MTPL warning TP0346: Port 4 is missing from FlowItem definition. Add the missing port definition [C:\Users\jqdelosr\source\MTLP68\Modules\ARR_MBIST_PMSXM\ARR_MBIST_PMSXM.mtproj]
/blah/Modules/FUN_CORE_C2P/FUN_CORE_C2P_CLASS_P28G1.usrv(6203,50,6203,85): TPL/MTPL error TP0346: another error
/blah/Modules/FUN_CORE_C2P/FUN_CORE_C2P_CLASS_P28G1.mtpl(13311,20,13311,87): TPL/MTPL error TP0054: Bin 'b90444403_fail_FUN_CORE_C2P_SBFT_X_VMIN_K_SCRF5_X_VCORE_F5_3600_MLC' is not recognized (are you missing a bin definition or an import statement?) [C:\Users\jqdelosr\source\MTLP68\Modules\FUN_CORE_C2P\FUN_CORE_C2P.mtproj]
Failed to 'Build Test Program'.
hey
'Build Test Program' finished successfully.
'''
        edata = [{'file': '/blah/Modules/FUN_CORE_C2P/FUN_CORE_C2P_CLASS_P28G1.usrv',
                  'module': 'FUN_CORE_C2P',
                  'lno': '6203,50,6203,85',
                  'code': 'TP0346',
                  'msg': "another error"},
                 {'file': '/blah/Modules/FUN_CORE_C2P/FUN_CORE_C2P_CLASS_P28G1.mtpl',
                  'module': 'FUN_CORE_C2P',
                  'lno': '13311,20,13311,87',
                  'code': 'TP0054',
                  'msg': "Bin 'b90444403_fail_FUN_CORE_C2P_SBFT_X_VMIN_K_SCRF5_X_VCORE_F5_3600_MLC' is not recognized (are you missing a bin definition or an import statement?) [C:\\Users\\jqdelosr\\source\\MTLP68\\Modules\\FUN_CORE_C2P\\FUN_CORE_C2P.mtproj]"}
                 ]
        wdata = [{'file': '/blah/Modules/FUN_CORE_C2P/FUN_CORE_C2P_CLASS_P28G1.usrv',
                  'module': 'FUN_CORE_C2P',
                  'lno': '6203,50,6203,85',
                  'code': 'TP0346',
                  'msg': 'Port 4 is missing from FlowItem definition. Add the missing port definition [C:\\Users\\jqdelosr\\source\\MTLP68\\Modules\\ARR_MBIST_PMSXM\\ARR_MBIST_PMSXM.mtproj]'}]
        self.assertEqual(DoMV.build_process_txt(out), (edata, wdata, ['hey']))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tpexport(self):
        # Derive sln and tpproj ==============================
        with Chdir(f'{UT_DIR}/torch_exported'):
            mv = DoMV()
            mv.jsonname = 'P68'
            sln_file, tpproj_file = mv.tpexport(None)
        self.assertEqual(sln_file, 'Meteorlake_P68.sln')
        self.assertEqual(tpproj_file, 'POR_TP/Class_MTL_P68/Class_MTL_P68.tpproj')

        # check commandlines are correct ===========================
        result = ['']

        def fake_run_outtxt(slf, *args):
            result.append(' '.join(slf.cmd))
            return 0, 'success'

        def fake_run_sout_serr(slf, *args):
            result.append(' '.join(slf.cmd))
            return 0, 'success', ''

        with TempDir(name=True, chdir=True), \
                MockVar(DoFixer, "main", Mock()), \
                MockVar(torch_mv, 'IS_WIN', True), \
                MockVar(SystemCall, 'run_sout_serr', fake_run_sout_serr), \
                MockVar(SystemCall, 'run_outtxt', fake_run_outtxt):
            mv = DoMV()
            mv.jsonname = 'P68'
            mkdirs(mv.root_templates)
            File('POR_TP/blah/a.tpproj').touch(mkdir=True)
            File('a.sln').touch(mkdir=True)
            File('POR_TP/blah/a.env').touch()

            # execute
            mv.tpexport(None)

            expect = f'''
{DoMV.get_torch_exe()} fix-tp -s a.sln -p POR_TP/blah/a.tpproj
{DoMV.get_torch_exe()} export-tp -s a.sln -p POR_TP/blah/a.tpproj -i -c -l -d None
{DoMV.get_torch_exe()} build -s a.sln -p POR_TP/blah/a.tpproj -l I:/tpapps/TORCH/Prod22/LanguageServer --maxParallel -1
'''
            result.append('')    # expect beautify
            self.assertTextEqual('\n'.join(result), expect)

            # recipe check
            mv = DoMV(recipe=True)
            result = ['']
            mv.tpexport(None)

            expect = f'''
{DoMV.get_torch_exe()} fix-tp -s a.sln -p POR_TP/blah/a.tpproj
{DoMV.get_torch_exe()} export-tp -s a.sln -p POR_TP/blah/a.tpproj -i -c -l -b -r -d None
{DoMV.get_torch_exe()} build -s a.sln -p POR_TP/blah/a.tpproj -l I:/tpapps/TORCH/Prod22/LanguageServer --maxParallel -1
'''
            result.append('')    # expect beautify
            self.assertTextEqual('\n'.join(result), expect)

            # no build (torch_build() is tested here)
            mv = DoMV(nobuild=True)
            result = ['']
            mv.tpexport(None)

            expect = f'''
{DoMV.get_torch_exe()} fix-tp -s a.sln -p POR_TP/blah/a.tpproj
{DoMV.get_torch_exe()} export-tp -s a.sln -p POR_TP/blah/a.tpproj -i -c -l -d None
'''
            result.append('')    # expect beautify
            self.assertTextEqual('\n'.join(result), expect)

            # no build by env
            mv = DoMV()
            result = ['']
            with MockVar(os.environ, 'SKIP_TORCHBUILD', 'True'):
                mv.tpexport(None)

            result.append('')    # expect beautify
            self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_derive_sln(self):
        mv = DoMV()

        # none found
        self.assertEqual(mv.derive_sln(), None)

        # 1 .sln case
        File('Meteorlake_P68.sln').touch()
        self.assertEqual(mv.derive_sln(), 'Meteorlake_P68.sln')

        # 2 .sln case
        File('Meteorlake_P68.debug.sln').touch()
        self.assertEqual(mv.derive_sln(), 'Meteorlake_P68.sln')

        # debug only
        File('Meteorlake_P68.sln').unlink()
        self.assertEqual(mv.derive_sln(), 'Meteorlake_P68.debug.sln')

        # 2 debug
        File('Meteorlake_P28.debug.sln').touch()
        with self.assertRaisesRegex(ErrorUser, 'Expecting one .sln'):
            mv.derive_sln()

        # 2 POR
        File('Meteorlake_P28.debug.sln').unlink()
        File('Meteorlake_P68.debug.sln').unlink()
        File('Meteorlake_P68.sln').touch()
        File('Meteorlake_P28.sln').touch()
        with self.assertRaisesRegex(ErrorUser, 'Expecting one .sln'):
            mv.derive_sln()

    @with_(TempDir, chdir=True, delete=True)
    def test_derive_tpproj_file(self):
        mv = DoMV()
        mv.jsonname = 'P68'

        # none found
        with self.assertRaisesRegex(ErrorUser, 'Expecting at least one .tpproj'):
            mv.derive_tpproj_file()

        # one found
        fn = 'POR_TP/Class_MTL_P68/abc.tpproj'
        File(fn).touch(mkdir=True)
        self.assertEqual(Env.xpath(mv.derive_tpproj_file()), fn)

        # two found
        fn2 = 'POR_TP/Class_MTL_P28/abc.tpproj'
        File(fn2).touch(mkdir=True)
        self.assertEqual(Env.xpath(mv.derive_tpproj_file()), fn)

        # jsonname vague
        mv.jsonname = 'P'
        with self.assertRaisesRegex(ErrorUser, 'There are multiple POR_TP'):
            mv.derive_tpproj_file()

        # jsonname vague
        mv.jsonname = 'JDR'
        with self.assertRaisesRegex(ErrorUser, 'There are multiple POR_TP'):
            mv.derive_tpproj_file()

        # via tpfolder
        mv.tpfolder = 'POR_TP/Class_MTL_P28'
        self.assertEqual(Env.xpath(mv.derive_tpproj_file()), fn2)
        mv.tpfolder = 'Class_MTL_P28'
        self.assertEqual(Env.xpath(mv.derive_tpproj_file()), fn2)
        mv.tpfolder = 'Class_MTL_P'
        with self.assertRaisesRegex(ErrorUser, 'Expecting one .tpproj in'):
            mv.derive_tpproj_file()

    def test_replace_portp_engtp_recipe(self):
        with TempDir(name=True, chdir=True) as tdir:
            mv = DoMV()
            self.assertEqual(mv.replace_portp_engtp_recipe(), 1)
            mkdirs('ENG_TP')
            frecipe = 'astra/astra_hdmx_vf/recipe/MTLXXXXXXX21E0BSXXX/tp_recipe/CLASS_P68G2_MTL_P68G2_HDMT_1_MPS_Universal_TPrecipe_TPL.xml'
            File(frecipe).touch('<Item POR_TP/blah\nsomething POR_TP/blah\n', mkdir=True)
            mv.replace_portp_engtp_recipe()
            self.assertEqual(File(frecipe).read(), '<Item ENG_TP/blah\nsomething ENG_TP/blah\n')

    def test_noargs(self):
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            File(f'{tdir}/SRC/TPConfig/MV_Templates/p68_arr.json').touch('''
[ { "name": "P68_ARR",
    "modules": [ "ARRX"
     ],
    "config_imports": [ ]
  }
]''', mkdir=True)

            cmd = f'torch_mv.py'     # SRC/ folder is the "postprocessed" version already
            with Chdir(f'{tdir}/SRC'), \
                    MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:

                with self.assertRaises(SystemExit):
                    MVArg().main()

            expect = '''List of json files:
p68_arr.json
'''
            self.assertTextEqual(p.getvalue(), expect)

    def test_defaultargs(self):
        with TempDir(name=True, chdir=True):
            obj = DoMV()
            self.assertEqual(obj.tpfolder, None)
            self.assertEqual(obj.fast, False)
            self.assertEqual(obj.nprtrigger, True)
            self.assertEqual(obj.recipe, False)
            self.assertEqual(obj.nodel, False)

    def test_get_torch_exe(self):
        # default
        DoMV.my_cache.clear_cache()
        default = 'I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe'
        self.assertEqual(DoMV.get_torch_exe(), default)

        # User input provides the torch version.
        DoMV.my_cache.clear_cache()
        userinput = 'I:/tpapps/TORCH/Prod22/CLI/Torch.exe'
        with MockVar(os.environ, 'TORCH_VERSION', userinput):
            self.assertEqual(DoMV.get_torch_exe(), userinput)

        # -exever
        DoMV.my_cache.clear_cache()
        with MockVar(OPT, 'exever', 'latest'):
            self.assertEqual(DoMV.get_torch_exe(), 'I:/tpapps/TORCH/Prod22/CLI/Torch.exe')
        DoMV.my_cache.clear_cache()
        with MockVar(OPT, 'exever', 'v2'):
            self.assertEqual(DoMV.get_torch_exe(), 'I:/tpapps/TORCH/Prod22/CLI/v2/Torch.exe')

        # config based - always
        DoMV.my_cache.clear_cache()
        with TempDir(chdir=True):
            File('POR_TP/Class_MTL_P68/InputFiles/torch_exe_version.txt').touch('/abc/def', mkdir=True)
            self.assertEqual(DoMV.get_torch_exe(), '/abc/def')

        # config based - always - cache
        DoMV.my_cache.clear_cache()
        with TempDir(chdir=True):
            File('Shared/POR_TP/Class_MTL_P68/InputFiles/torch_exe_version.txt').touch('/abc/def2', mkdir=True)
            self.assertEqual(DoMV.get_torch_exe(), '/abc/def2')
            File('Shared/POR_TP/Class_MTL_P68/InputFiles/torch_exe_version.txt').touch('/abc/def3', mkdir=True, newfile=True)
            self.assertEqual(DoMV.get_torch_exe(), '/abc/def2')    # cached

        # shared common
        DoMV.my_cache.clear_cache()
        with TempDir(chdir=True):
            File('Shared/BaseInputs/Inputs/torch_exe_version.txt').touch('/abc/def2', mkdir=True)
            self.assertEqual(DoMV.get_torch_exe(), '/abc/def2')
            DoMV.my_cache.clear_cache()
            File('Shared/POR_TP/Class_MTL_P68/InputFiles/torch_exe_version.txt').touch('/abc/def3', mkdir=True)
            self.assertEqual(DoMV.get_torch_exe(), '/abc/def3')    # return the override

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True, delete=True)
    def test_no_dup_env_keys(self):
        # fail case - real
        with self.assertRaisesRegex(ErrorUser, 'is defined twice'):
            DoMV.no_dup_env_keys(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P28/a.tpproj')

        # no found case
        with self.assertRaisesRegex(ErrorUser, 'Cannot find any'):
            DoMV.no_dup_env_keys(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P28')

        # pass case
        text = '''
VAR1 = "somevalue";
VAR2="somvevalue" +
     VAR2;
# VAR2=comment
'''
        File('POR_TP/68/EnvironmentFile.env').touch(text, mkdir=True)
        self.assertEqual(DoMV.no_dup_env_keys('POR_TP/68/a.tpproj'), 2)

        # fail case
        text = '''
VAR1 = "somevalue";
VAR2="somvevalue" +
     VAR2;
VAR2   =SOMEVAR;
'''
        File('POR_TP/68/EnvironmentFile.env').touch(text, mkdir=True, newfile=True)
        with self.assertRaisesRegex(ErrorUser, 'VAR2. is defined twice'):
            DoMV.no_dup_env_keys('POR_TP/68/a.tpproj')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        # start to finish integration test
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/SRC')

            File(f'{tdir}/SRC/TPConfig/MV_Templates/p68_arr.json').touch('''
[ { "name": "P68_ARR",
    "modules": [ "ARRX"
     ],
    "config_imports": [ ]
  }
]''', mkdir=True)

            def fake_export(_, dst):
                os.rmdir(dst)
                shutil.copytree(f'{tdir}/SRC', dst)
                rmtree(f'{dst}/TPConfig')

            cmd = f'torch_mv.py P68_ARR {tdir}/DST -fast false'     # SRC/ folder is the "postprocessed" version already
            with Chdir(f'{tdir}/SRC'), \
                    MockVar(sys, "argv", cmd.split()), \
                    MockVar(PgmRules, 'apply', Mock()), \
                    MockVar(DoMV, 'tpexport', fake_export):
                mv = MVArg()
                mv.main()

            tpenv = f'{tdir}/DST/ENG_TP/TGLH81/EnvironmentFile.env'
            self.assertEqual(len(list(TestProgram(tpenv).mtpl.iter_flows())), 4)
            self.assertEqual(len(File(f'{tdir}/DST/ENG_TP/TGLH81/PLIST_ALL.xml').raw()), 10)
            self.assertItemsEqual(os.listdir(f'{tdir}/DST/Modules'), ['ARRX', 'TPI_BASEPRIM_XXX'])
            self.assertEqual(mv.utobj[0].nprtrigger, True)

    def test_basicfailcopy(self):
        # start to finish integration test - some exception occurred in TorchPostProc
        MVArg.utobj = [None]
        tpref = f'{UT_DIR_REPO}/Simple3a'
        with TempDir(name=True, delete=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/SRC')

            File(f'{tdir}/SRC/TPConfig/MV_Templates/p68_arr.json').touch('''
[ { "name": "P68_ARR",
    "modules": [ "ARRX"
     ],
    "config_imports": [ ]
  }
]''', mkdir=True)

            def fake_export(_, dst):
                os.rmdir(dst)
                shutil.copytree(f'{tdir}/SRC', dst)
                rmtree(f'{dst}/TPConfig')

            class MyException(Exception):
                pass

            cmd = f'torch_mv.py P68_ARR {tdir}/DST -fast false'     # SRC/ folder is the "postprocessed" version already
            with Chdir(f'{tdir}/SRC'), \
                    MockVar(sys, "argv", cmd.split()), \
                    MockVar(PgmRules, 'apply', Mock()), \
                    MockVar(TorchPostProc, 'main', Mock(side_effect=MyException)), \
                    MockVar(DoMV, 'tpexport', fake_export):
                mv = MVArg()
                self.assertRaises(MyException, mv.main)

            tpenv = f'{tdir}/DST/ENG_TP/TGLH81/EnvironmentFile.env'
            self.assertEqual(len(list(TestProgram(tpenv).mtpl.iter_flows())), 4)
            self.assertEqual(len(File(f'{tdir}/DST/ENG_TP/TGLH81/PLIST_ALL.xml').raw()), 10)
            self.assertItemsEqual(os.listdir(f'{tdir}/DST/Modules'), ['ARRX', 'TPI_BASEPRIM_XXX'])
            self.assertEqual(mv.utobj, [None])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_datahost(self):
        # start to finish integration test
        tpref = f'{UT_DIR}/Simple3a'
        with TempDir(name=True, delete=True, otherdir='/intel/tpvalidation/engtools/tptools/mtl/unittests/tempdir') as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/SRC')

            File(f'{tdir}/SRC/TPConfig/MV_Templates/p68_arr.json').touch('''
[ { "name": "P68_ARR",
    "modules": [ "ARRX"
     ],
    "config_imports": [ ]
  }
]''', mkdir=True)

            def fake_export(_, dst):
                os.rmdir(dst)
                shutil.copytree(f'{tdir}/SRC', dst)
                rmtree(f'{dst}/TPConfig')

            cmd = f'torch_mv.py P68_ARR {tdir}/DST -fast true'     # SRC/ folder is the "postprocessed" version already
            with Chdir(f'{tdir}/SRC'), \
                    MockVar(sys, "argv", cmd.split()), \
                    MockVar(PgmRules, 'apply', Mock()), \
                    MockVar(DoMV, 'tpexport', fake_export):
                MVArg().main()

            tpenv = f'{tdir}/DST/ENG_TP/TGLH81/EnvironmentFile.env'
            self.assertEqual(len(list(TestProgram(tpenv).mtpl.iter_flows())), 4)
            self.assertEqual(len(File(f'{tdir}/DST/ENG_TP/TGLH81/PLIST_ALL.xml').raw()), 10)
            self.assertItemsEqual(os.listdir(f'{tdir}/DST/Modules'), ['ARRX', 'TPI_BASEPRIM_XXX'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
