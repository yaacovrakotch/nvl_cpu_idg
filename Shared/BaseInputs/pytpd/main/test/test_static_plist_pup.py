#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for test_static_plist_pup
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.gizmo import MockVar, with_
from gadget.ut import Mock
from gadget.helperclass import CaptureStdoutLog
from main.static_plist_pup import *
from os.path import join, dirname, abspath
import os


class TestSPP(TestCase):

    def test_basic(self):
        # without srh flow
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup'):
            fake = {'main1': 'assume this patlist is in SRH flow'}
            with MockVar(StaticPlistPup, 'get_srh_patlist', Mock(return_value=fake)):
                sp = StaticPlistPup('POR_TP/TGLH81/EnvironmentFile.env', './bom1/PAS_PTD.pup.json')
                sp.main()

            # report file is generated
            self.assertItemsEqual(os.listdir('Shared/BaseInputs/Supersedes/POR_PUP'),
                                  ['report.txt', 'orig', 'fuse.plist', 'Shops.plist', 'bom1', 'bom1_g'])

            # Check the revision
            self.assertGoldEqual('Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl.gold')

            # fuse.plist is unchanged
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/fuse.plist',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Supersedes/patterns/fuse.plist.gold')

            # Shops.plist is updated
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/Shops.plist',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Supersedes/patterns/Shops.plist.gold')

            # list of warnings
            expect = '''
-w- [main1] does not have g9999999W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH, but pat is in PTD file
-i- Total of 1 reenabled patlists with single pat
'''
            self.assertTextEqual('\n'.join(x for x in sp.warnings if 'Completed successfully' not in x),
                                 expect)

            # main1 should be removed (main1 is SRH)
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/bom1/PAS_PTD.pup.json',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/bom1/PAS_PTD.pup.json.gold')

            expectnpr = '''
ModelName,PlistName,Ipname
blah,shops_L_list
blah,shops_L_list,IP_CPU
'''
            self.assertTextEqual(File('Shared/BaseInputs/Supersedes/POR_PUP/bom1/NPRInputFile.csv').read(),
                                 expectnpr)   # This should remove main1 as well

            # re-run
            with MockVar(StaticPlistPup, 'get_srh_patlist', Mock(return_value=fake)):
                StaticPlistPup('POR_TP/TGLH81/EnvironmentFile.env', './bom1/PAS_PTD.pup.json').main()
            self.assertItemsEqual(os.listdir('Shared/BaseInputs/Supersedes'),
                                  ['POR_PUP', 'POR_PUP.1'])
            self.assertGoldEqual('Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl.gold')

    def test_basic2(self):
        # main_not_found is in srh flow. main1 is not in srh flow
        # dummy instance is not found
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup'):
            fake = {'main_not_found': 'assume this patlist is in SRH flow'}
            nif = '''
ModelName,PlistName,Ipname
blah,main1,IP_CPU
blah,main1
blah,shops_L_list
blah,shops_L_list,IP_CPU
blah
'''
            File('bom1/NPRInputFile.csv').touch(nif, newfile=True)
            with MockVar(StaticPlistPup, 'get_srh_patlist', Mock(return_value=fake)), \
                    MockVar(StaticPlistPup, 'VERSION_INSTANCE', 'BLAH_NOT_EXIST'):
                sp = StaticPlistPup('POR_TP/TGLH81/EnvironmentFile.env', './bom1/PAS_PTD.pup.json')
                sp.main()

            # list of warnings
            expect = '''
-w- [main_not_found] is not found for this TP
-w- dummy instance is not found [BLAH_NOT_EXIST] for version update
-i- Total of 0 reenabled patlists with single pat
'''
            self.assertTextEqual('\n'.join(x for x in sp.warnings if 'Completed successfully' not in x),
                                 expect)

            # main1 should be removed (main1 is SRH)
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/bom1/PAS_PTD.pup.json',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/bom1/PAS_PTD.pup.json.basic2.gold')

            self.assertTextEqual(File('Shared/BaseInputs/Supersedes/POR_PUP/bom1/NPRInputFile.csv').read(),
                                 nif)    # original

            # fuse.plist is unchanged
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/fuse.plist',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Supersedes/patterns/fuse.plist.gold')

            # Shops.plist is unchanged
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/Shops.plist',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Supersedes/patterns/Shops.plist')

            # mtpl is unchanged
            self.assertGoldEqual('Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl')

    def test_skipmain(self):
        # without srh flow
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup'):
            File('POR_TP/TGLH81/InputFiles/No_Static_Hybrid_Pup').touch(mkdir=True)
            sp = StaticPlistPup('POR_TP/TGLH81/EnvironmentFile.env', './bom1/PAS_PTD.pup.json')
            self.assertEqual(sp.main(), 2)

    def test_emptyplist(self):
        # empty plist case - bug found - must disable disabled list
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup'):
            fake = {'main1': 'assume this patlist is in SRH flow'}
            File('Supersedes/patterns/Shops.plist').touch(File('Supersedes/patterns/Shops.plist.empty').read(),
                                                          newfile=True)
            with MockVar(StaticPlistPup, 'get_srh_patlist', Mock(return_value=fake)):
                sp = StaticPlistPup('POR_TP/TGLH81/EnvironmentFile.env', './bom1/PAS_PTD.pup.json')
                sp.main()

            expect = '''
-w- [main1] does not have g9999999W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH, but pat is in PTD file
-i- Total of 2 reenabled patlists with single pat
'''
            self.assertTextEqual('\n'.join(x for x in sp.warnings if 'Completed successfully' not in x),
                                 expect)

            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/Shops.plist',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Supersedes/patterns/Shops.plist.empty.gold')
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/bom1/PAS_PTD.pup.json',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/bom1/PAS_PTD.pup.json.gold')

    def test_doubleactive(self):
        # double active case
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup'):
            fake = {'main1': 'assume this patlist is in SRH flow',
                    'shops_H1_list': 'SRH flow'}
            File('bom1/PAS_PTD.pup.json').touch(File('bom1/PAS_PTD.pup.json.doubleactive').read(),
                                                newfile=True)
            with MockVar(StaticPlistPup, 'get_srh_patlist', Mock(return_value=fake)):
                sp = StaticPlistPup('POR_TP/TGLH81/EnvironmentFile.env', './bom1/PAS_PTD.pup.json')
                sp.main()

            expect = '''
-w- double active. Ignoring leaf. uniq_in_leaf: 1. leaf: shops_H1_list: 1 -vs- parent: main1 : 1
-i- Total of 0 reenabled patlists with single pat
'''
            self.assertTextEqual('\n'.join(x for x in sp.warnings if 'Completed successfully' not in x),
                                 expect)

            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/Shops.plist',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/Supersedes/patterns/Shops.plist.doubleactive.gold')
            self.assertGoldEqual('Shared/BaseInputs/Supersedes/POR_PUP/bom1/PAS_PTD.pup.json',
                                 f'{UT_DIR_REPO}/Simple4b_staticpup/bom1/PAS_PTD.pup.json.empty.gold')

    def test_doubleactive2(self):
        # double active case
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup'):
            fake = {'main1': 'assume this patlist is in SRH flow',
                    'shops_H1_list': 'SRH flow'}
            File('bom1/PAS_PTD.pup.json').touch(File('bom1/PAS_PTD.pup.json.doubleactive_case2').read(),
                                                newfile=True)
            with MockVar(StaticPlistPup, 'get_srh_patlist', Mock(return_value=fake)):
                sp = StaticPlistPup('POR_TP/TGLH81/EnvironmentFile.env', './bom1/PAS_PTD.pup.json')
                sp.main()

            expect = '''
-i- Total of 0 reenabled patlists with single pat
'''
            self.assertTextEqual('\n'.join(x for x in sp.warnings if 'Completed successfully' not in x),
                                 expect)

    def test_srh_flow(self):
        # default - no SRH subflows
        sp = StaticPlistPup(f'{UT_DIR_REPO}/Simple4b_staticpup/POR_TP/TGLH81/EnvironmentFile.env', 'PAS_PTD.pup.json')
        self.assertEqual(sp.get_srh_patlist(), {})

        # "MAIN" is srh which is all
        with MockVar(StaticPlistPup, 'SUBFLOWS', 'DUTFlow MAIN'):
            self.assertEqual(sp.get_srh_patlist(),
                             {'cpu_fuse_read_hvm_x': "CCA ['MAIN', 'SCN::MAIN2']",
                              'cpu_fuse_read_special_x': "CCB ['MAIN', 'SCN::MAIN2']",
                              'shops_H_list': "CCD ['ARR::MAIN1', 'MAIN']",
                              'shops_L_list': "CCA ['ARR::MAIN1', 'MAIN']"})

        # "PTH::MAIN2" is srh - with cross contamination
        with MockVar(StaticPlistPup, 'SUBFLOWS', 'DUTFlow PTH::MAIN2'):
            self.assertEqual(sp.get_srh_patlist(), {})   # No srh plist found if cross contaminated

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_engtp(self):
        with MockVar(TestProgram, 'init', lambda x: x):
            sp = StaticPlistPup(f'{UT_DIR}/torch_mvtp/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env', 'PAS_PTD.pup.json')
        self.assertEqual(sp.main(), 1)

    def test_copy_parallel(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('ABC/f1').touch(mkdir=True)
            File('ABC/f2').touch(mkdir=True)
            StaticPlistPup.copy_parallel(tdir, 'ABC')
            self.assertItemsEqual(os.listdir(tdir), ['ABC', 'ABC_g'])
            self.assertItemsEqual(os.listdir(f'{tdir}/ABC_g'), ['f1', 'f2'])

        with TempDir(name=True, chdir=True) as tdir:
            File('ABC_g/f1').touch(mkdir=True)
            File('ABC_g/f2').touch(mkdir=True)
            StaticPlistPup.copy_parallel(tdir, 'ABC_g')
            self.assertItemsEqual(os.listdir(tdir), ['ABC', 'ABC_g'])
            self.assertItemsEqual(os.listdir(f'{tdir}/ABC'), ['f1', 'f2'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
