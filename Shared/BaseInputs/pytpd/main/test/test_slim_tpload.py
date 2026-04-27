#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for slim_tpload
"""
from setenv_unittest import UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.disk import mkdirs
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from main.slim_tpload import *
from unittest.mock import Mock
from tp.testprogram import Env
import sys


class SlimTest(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_patmod_mtpl(self):
        tp = TestProgram('/intel/hdmxprogs/tgl/TGLXXXXBXH13Y00S017/TPL/EnvironmentFile.env', stpl='SubTestPlan_CLASS_TGLU42.stpl')
        # fam = ProgramFamily('/intel/hdmxprogs/tgl/TGLXXXXBXH13Y00S017/TPL').init_manual([tp])
        result = Slim.patmod_mtpl(tp, 'ARR_DE')
        self.assertEqual(len(result), 20)
        self.assertEqual(result['ARR_DE::DEMISC_X_PATMOD_K_BEGIN_X_X_X_X_LVR_ENABLE_CONFIG_2'],
                         ('/intel/hdmxprogs/tgl/TGLXXXXBXH13Y00S017/TPL/Modules/ARR_DE/InputFiles/lvr_patmods_de.txt', 'LVR_CCF_2'))

    def test_keep_pats_reset(self):
        obj = Slim(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        data = {'ARR': {'fuse.plist'},
                'SCN': {'Shops.plist'},
                'PTH': {'fuse.plist', 'Shops.plist'}}
        result = set()
        with MockVar(obj.tpobj.plists, 'get_mod2plist_map', Mock(return_value=data)):
            obj.keep_pats_reset(result, cfg_mod=re.compile('^S'), cfg_plb=re.compile(r"^\w"))
            self.assertEqual(len(result), 2)   # 2 patterns in Shops

        result = set()
        with MockVar(obj.tpobj.plists, 'get_mod2plist_map', Mock(return_value=data)):
            obj.keep_pats_reset(result, cfg_mod=re.compile('^A'), cfg_plb=re.compile(r"^\w"))
            self.assertEqual(len(result), 44)   # 44 patterns in fuse

        result = set()
        with MockVar(obj.tpobj.plists, 'get_mod2plist_map', Mock(return_value=data)):
            obj.keep_pats_reset(result, cfg_mod=re.compile('^P'), cfg_plb=re.compile(r"^\w"))
            self.assertEqual(len(result), 46)   # 46 patterns in total

        result = set()
        with MockVar(obj.tpobj.plists, 'get_mod2plist_map', Mock(return_value=data)):
            obj.keep_pats_reset(result, cfg_mod=re.compile(r"^\w"), cfg_plb=re.compile(r"^\w"))
            self.assertEqual(len(result), 46)   # 46 patterns in total

    @with_(TempDir, chdir=True)
    def test_read_file(self):
        File('a.txt').write('''
g2253269F2445949I_GK_VTR02    g2253270F2445970I_GK_VTR02
g993269F2445949I_GKxxxx_not_valid

g2253271F2445949I_GK_VTR02
''')
        obj = Slim(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(obj._read_file('a.txt'), {'g2253269F2445949I_GK_VTR02',
                                                   'g2253270F2445970I_GK_VTR02',
                                                   'g2253271F2445949I_GK_VTR02'})
        self.assertEqual(obj._read_file('.'), set())

        # glxline
        self.assertEqual(obj.glxline('input_file = "./Modules/ARR_GT1/InputFiles/mgfxcache_sku.patmod",   Template,   ARR_GT1::OTHER_X_PATMOD_K_PRE_X_X_X_X_GTSKU_PATMOD_PRESF : *,*'),
                         ('./Modules/ARR_GT1/InputFiles/mgfxcache_sku.patmod', 'ARR_GT1::OTHER_X_PATMOD_K_PRE_X_X_X_X_GTSKU_PATMOD_PRESF'))
        self.assertEqual(obj.glxline('input_file,   Template,   '),
                         (None, None))

    @with_(TempDir, chdir=True)
    def test_make_slim_plist(self):
        File('a.txt').write('''
GlobalPList shops_L_list {
Pat tgl_pre_F9999991H;
# com
Pat g2294511W1466650I_MD;
Pat g2294512W1466650I_MD;
}
    GlobalPList shops_L_list {
    Pat tgl_pre_F9999991H;
    Pat g2294511W1466650I_MD;
    Pat g2294512W1466650I_MD;
    Pat g2294513W1466650I_MD;
    Pat g2294514W1466650I_MD;
    }
''')

        # execute
        obj = Slim(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        mkdirs('ndir')
        obj.keep_pats.add('g2294514W1466650I_MD')
        obj._make_slim_plist('a.txt', 'ndir')

        expect = '''
GlobalPList shops_L_list {
Pat tgl_pre_F9999991H;
# com
Pat g2294511W1466650I_MD;
}
    GlobalPList shops_L_list {
    Pat tgl_pre_F9999991H;
    Pat g2294511W1466650I_MD;
    Pat g2294514W1466650I_MD;
    }
'''
        self.assertTextEqual(open('ndir/a.txt').read(), expect)

    @with_(TempDir, chdir=True)
    def test_get_cfgs(self):

        File('EnvironmentFile.env').write(r'''
MGARR_PATMODIFY_PATH = "I:\hdmxpats\tglx\MGarr\RevTTR0.0\p5\cfg";

MCLK_PATMODIFY_PATH = "I:\hdmxpats\tglx\Mfake\RevXXB0.3\p5\cfg";
HDST_PLIST_PATH = "I:\hdmxpats\tglx\Mfake\RevXXB0.3\p5\plb";
        ''')

        # test cases are written here ========================================
        File('a.mtpl').write('''
    # existing file
    input_file = "./Modules/FUN_SA/InputFiles/core_mask_patmod_new.txt";

    # existing file, but not valid area
    input_file = "a.mtpl"

    # non existent file (should show in warning)
    ifpm_input_file = "./Modules/FUN_SA/InputFiles/notexist.txt";

    # existing file
input_file = "~MGARR_PATMODIFY_PATH/merged_array_ipu_hdmt2.xml!blah";

    # module not defined in env file
    input_file = "~MTPI_PATMODIFY_PATH/merged_array_ipu_hdmt2.xml";

    # should ignore function_parameter (e.g. fuse modules)
    function_parameter = "~MGARR_PATMODIFY_PATH/intradut_merged_array_ipu_hdmt2.xml";

    ''')

        File('a.tpl').touch()
        File('PLIST_ALL.xml').touch('<HdmtReferenceFile></HdmtReferenceFile>')
        File('a.stpl').touch()
        mkdirs('Modules')
        obj = Slim('./EnvironmentFile.env', noinit=True)

        # existing file
        File('Modules/FUN_SA/InputFiles/core_mask_patmod_new.txt').touch(mkdir=True)

        result = obj._get_cfgs('a.mtpl')
        self.assertEqual({Env.xpath(list(result)[0])}, {'././Modules/FUN_SA/InputFiles/core_mask_patmod_new.txt'})
        self.assertEqual(len(obj.warns), 3)

    def test_full_names(self):
        obj = Slim(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env', noinit=True)
        allpats = {'g1234567W000001abc',
                   'g1234568W000002abc',
                   'g1234569W000003abc',
                   'g1234570W000004abc'}
        obj.keep_pats = {'g1234567W000001abc',
                         'W000002abc',
                         'W000003'}

        self.assertEqual(obj._full_names(allpats), 2)
        expect = {'g1234567W000001abc',
                  'g1234568W000002abc',
                  'g1234569W000003abc'}
        self.assertEqual(obj.keep_pats, expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="Slow test"))
    def test_realtp(self):
        # functional/integration/regression test - realtp
        with TempDir(name=True, delete=True) as tdir:
            cmd = "slim_tpload.py /intel/hdmxprogs/mtl/MTLXXXXAXH19M00S219/POR_TP/Class_MTL_P68/EnvironmentFile.env -out %s" % tdir
            # Mock _full_names - too slow
            with MockVar(sys, "argv", cmd.split()), MockVar(Slim, '_full_names', Mock()):
                sa = SlimArgs()
                obj = sa.do_all()

            # Below are the asserts for set_keep_pats2()
            # self.assertEqual(len(obj.warns), 26)           # total warnings
            # self.assertEqual(len(obj.keep_pats), 1573)     # total keep pats
            # self.assertEqual(len(os.listdir(tdir)), 109)   # total written plist files
            # self.assertEqual(File(join(tdir, 'Mfunsa_class.plist')).sha1(),
            #                  'c290b71f21cf19190248fd0de337c5dc6c582358')

            self.assertEqual(len(obj.keep_pats), 8734)    # prev: 1690   # total keep pats
            self.assertEqual(len(os.listdir(tdir)), 243)   # total written plist files
            self.assertEqual(File(join(tdir, 'fun_atom_class_p68g2.plist')).sha1(),
                             '11fc4d282515e486380861050a5a773e0d5a4ab8')
            self.assertEqual(File(join(tdir, 'clk_cdie_class_p68g2.plist')).sha1(),
                             'b085a3ba6357cc0ebfd8ba0431773ae4e9378c70')

    def test_other(self):
        # help
        with MockVar(sys, "argv", "slim_tpload.py ".split()):
            with self.assertRaises(SystemExit):
                SlimArgs().main()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
