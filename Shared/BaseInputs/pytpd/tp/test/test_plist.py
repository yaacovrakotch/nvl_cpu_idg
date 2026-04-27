#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for plist.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from tp.plist import *
from tp.testprogram import TestProgram, Env
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.files import File, TempDir
from gadget.dictmore import keys_atlevel
from gadget.errors import ErrorEnv
from pprint import pprint
from unittest.mock import Mock
from os.path import realpath


class TestPlist(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic1(self):
        # With Intradut
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX39A0KSXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = tpobj.plists

        self.assertEqual(len(obj.get_rev_paths()), 70)
        self.assertEqual(len(obj.get_available_plist()), 430)
        self.assertEqual(len(obj.get_plist_list()), 260)
        self.assertEqual(len(obj.get_plb_map()), 15686)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic2(self):
        # Without Intradut
        tpobj = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')

        obj = tpobj.plists
        # self.assertEqual(len(obj.get_rev_paths()), 25)
        # self.assertEqual(len(obj.get_available_plist()), 198)
        self.assertEqual(len(obj.get_plist_list()), 109)
        self.assertEqual(len(obj.get_plb_map()), 10798)

    def test_subplist(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple2/TPL/EnvironmentFile.env').pickle_init()
        self.assertEqual(tp.plists.get_subplists('csi_hs_vix_csireset'),
                         {'csi_hs_vix_csireset', 'csi_hs_vil_csireset', 'csi_hs_vih_csireset'})

    def test_parentplist(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple2/TPL/EnvironmentFile.env').pickle_init()
        self.assertEqual(tp.plists.get_parentplists('csi_hs_vih_csireset'),
                         {'csi_hs_vih_csireset', 'csi_hs_vix_csireset'})

    @with_(TempDir, chdir=True)
    def test_basic_plist(self):
        text = '''
Test iCShmooTest t1 {
patlist="IP_CPU::negative_zbd";
}
Test iCShmooTest t2 {
   patlist = "idv_all_tcss_ipu_soc_reset_list";
}
Test iCShmooTest t2x {
   patlist = "list3";
}
'''
        File("TPL/Modules/TPI_IDV/TPI_SHOPS_CLASS_TGLU42.mtpl").touch(text, mkdir=True)

        text = 'Test iCShmooTest t3 {\n\tpatlist\t=\t"list1";\n}\n'
        File("TPL/Modules/TPI_IDV/TPI_SHOPS_CLASS_TGLY42.mtpl").touch(text, mkdir=True)

        text = '\tpatlist\t=\t"list9";'
        File("TPL/Modules/TPI_IDV/TPI_SHOPS_CLASS_TGLY42.usrv").touch(text, mkdir=True)   # ignored!

        text = 'Test iCShmooTest t4 {\npatlist="list2";\n}\n'
        File("TPL/Modules/MARR_CORE/TPI_SHOPS_CLASS_TGLY42.mtpl").touch(text, mkdir=True)

        text = '\tpatlist\t=\t"listx";'
        File("TPL/Modules/other/TPI_SHOPS_CLASS_TGLU42.mtpl").touch(text, mkdir=True)

        text = ''   # nothing
        File("TPL/Modules/FUS/TPI_SHOPS_CLASS_TGLU42.mtpl").touch(text, mkdir=True)

        File("TPL/a.tpl").touch()   # dummy tpl

        # unittest: _get_all_patlist()

        envfile = join(realpath('./TPL'), 'env.env')
        File(envfile).touch()
        tp = TestProgram(envfile)
        with self.assertRaisesRegex(ErrorInput, 'No .stpl file found in'):
            tp.get_stpl()

        tp = TestProgram(envfile)._ut_write_stpl()
        File("TPL/a.stpl").touch()   # dummy stpl
        tp.mtpl.read_mtpls()
        result = tp.plists._get_all_patlist()
        self.assertEqual(result, {'list1',
                                  'idv_all_tcss_ipu_soc_reset_list',
                                  'negative_zbd',
                                  'list3',
                                  'list2'})

        # basic test
        text = """
HDST_PLIST_PATH = "./Msio/RevTTB0.1/p4/plb;" +
                  "./Mmio/RevTTB0.1/p4/plb;" +
                  "./Supersedes/patterns";
"""
        File("TPL/a.env").touch(text)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/PLIST_ALL.xml").touch(text)

        text = """
GlobalPList list2 {
   Pat somepat;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList list3[Mask] {
   Pat somepat;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)

        tp = TestProgram(join(realpath('./TPL'), 'a.env'))._ut_write_stpl()
        tp.mtpl.read_mtpls()
        obj = tp.plists
        result = obj.get_cipmodules(['MARR_CORE', 'TPI_IDV'])
        self.assertEqual(result, {'Msio'})

        # execute set_plb_map() again - should be no change
        orig = dict(obj._plb_map)
        obj.set_plb_map()
        self.assertEqual(obj._plb_map, orig)

        # empty
        result = obj.get_cipmodules(['FUS'])
        self.assertEqual(result, set())

        # error case, cannot find module
        with self.assertRaisesRegex(ErrorInput, 'Cannot find module name for'):
            obj.get_modname('blah')

        # plb_to_filename
        self.assertEqual(obj.plb_to_filename(['list3', 'list2']),
                         {'sup1.plist', 'abc.plist'})
        result = obj.plb_to_filename(['list2'], fullpath=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(Env.xpath(result.pop()),
                         './Msio/RevTTB0.1/p4/plb/abc.plist')

        with self.assertRaisesRegex(ErrorInput, 'See above ERRORs'):
            obj.plb_to_filename(['listnotfound'])

        # coverage on set_all_revs
        self.assertEqual(tp.plists.get_rev_paths(), {'./Msio/RevTTB0.1/p4/plb'})

    @with_(TempDir, chdir=True)
    def test_setplbmap_cov(self):
        # error case - set_plb_map coverage
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
GlobalPList list1 {
   Pat somepat;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList list1 [Mask] {
   Pat somepat;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        with self.assertRaisesRegex(ErrorInput, 'plb .list1. is both in'):
            tp.plists.get_plb_map()

        tp = TestProgram("TPL/a.env", tpl='')
        File("TPL/a.stpl").unlink()   # dummy stpl
        with self.assertRaisesRegex(ErrorInput, 'Cannot find.*PLIST_ALL.xml'):
            tp.plists.get_plist_list()

        # no error
        File("TPL/a.stpl").touch()   # dummy stpl
        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        tp.plists.set_plb_map(is_error=False)
        self.assertEqual(len(tp.plists._plb_map), 1)
        self.assertEqual(Env.xpath(tp.plists._plb_map['list1']), './Supersedes/patterns/sup1.plist')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, not needed for coverage"))
    def test_set_pat2plb(self):

        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env', allpats=True)
        tp.plists.set_pat2plb()
        self.assertEqual(len(tp.plists._pat2nn), 56464)
        self.assertEqual(len(tp.plists._nn2pat), 56464)
        self.assertEqual(len(tp.plists._plb2n), 10798)
        self.assertEqual(len(tp.plists._n2plb), 10798)
        self.assertEqual(len(tp.plists._plb2pat), 10798)
        self.assertEqual(len(tp.plists._pat2plb), 56464)
        self.assertEqual(len(tp.plists._patheaders), 167)

        result = tp.plists.get_pats_from_plb('list_array_de_hdmt2_tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_274i_Mgt_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fs_0')
        self.assertEqual(result,
                         {'g2180518F3124585I_DZ_VTR023T_Gkna2e4i00AA_a040416xx000221xx1xxxalb_TR1PThTC003J3fs_LJx0A42x0nxx0000_de_array_precat',
                          'tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_274i_Mgt_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fs_0'})

        pat_g21 = 'g2180518F3124585I_DZ_VTR023T_Gkna2e4i00AA_a040416xx000221xx1xxxalb_TR1PThTC003J3fs_LJx0A42x0nxx0000_de_array_precat'
        result = tp.plists.get_plbs_usedby_pat(pat_g21)
        self.assertEqual(len(result), 26)   # This is visually verified. Do not change number
        result = tp.plists.get_plbs_usedby_pats([pat_g21, 'notfound'])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[pat_g21]), 26)

        # specific case
        pat = 'd2243615F2380102I_Ra_VTR023T_Pknm270000da_n040416xx000222xx1xxxalb_TR1PThTC002J3fr_LJx0A42x0nxx0000_de_io_sicc'
        result = tp.plists.get_plbs_usedby_pat(pat)
        self.assertEqual(result, {'sa_de_ipu_sicc', 'de_sicc', 'sa_wde_sicc', 'sa_de_sicc'})
        self.assertEqual(tp.plists.get_pats_from_plb('sa_de_ipu_sicc'),
                         {pat,
                          'g2024008F1208326I_9s_VTR022T_Pknm270000da_n040416xx000222xx1xxxalb_TR1PThTC001J3fr_LJx0A42x0nxx0000_de_pgts_all',
                          'tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_2700_Mpth_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fr_0_de_sicc',
                          'tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_2700_Mpth_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fr_0_sa_de_sicc'})

        self.assertEqual(tp.plists.get_pats_from_plb('sa_de_ipu_sicc', order=True),
                         ['tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_2700_Mpth_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fr_0_sa_de_sicc',
                          pat,
                          'tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_2700_Mpth_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fr_0_de_sicc',
                          'g2024008F1208326I_9s_VTR022T_Pknm270000da_n040416xx000222xx1xxxalb_TR1PThTC001J3fr_LJx0A42x0nxx0000_de_pgts_all',
                          pat])

        # patonly=True
        self.assertEqual(tp.plists.get_pats_from_plb('sa_de_ipu_sicc', patonly=True),
                         {pat,
                          'g2024008F1208326I_9s_VTR022T_Pknm270000da_n040416xx000222xx1xxxalb_TR1PThTC001J3fr_LJx0A42x0nxx0000_de_pgts_all'})
        self.assertEqual(tp.plists.get_pats_from_plb('sa_de_ipu_sicc', order=True, patonly=True),
                         [  # 'tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_2700_Mpth_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fr_0_sa_de_sicc',
            pat,
            # 'tgl_pre_F9999991H_040416xxx10040222xxalb0_T0xx2k_2700_Mpth_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fr_0_de_sicc',
            'g2024008F1208326I_9s_VTR022T_Pknm270000da_n040416xx000222xx1xxxalb_TR1PThTC001J3fr_LJx0A42x0nxx0000_de_pgts_all',
            pat])

        # count all the pats in all globalplists
        total = 0
        for plb in tp.plists._plb2n:
            total += len(tp.plists.get_pats_from_plb(plb))
        self.assertEqual(total, 548261)
        self.assertEqual(len(tp.plists.get_pats_all()), 56464)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_tid_from_pats(self):
        tpobj = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        obj = tpobj.plists
        pats = {'d0011176V0748667X_00_TA0fxR_Gxxx00000000_axx00a0xxxxxxx1xx_TA0XChcP001Jaff_LxJx2A021x0axx000_testname1',
                'd0011176W0748668VB_00_TA0fxR_Gxxx00000000_axx00a0xxxxxxx1xx_TA0XChcP001Jaff_LxJx2A021x0axx000_',
                'd0011176W0748669I_00_VTA0fxR_Gxxx00000000_a102424aa0a1xxxxx1xxxabx_TA0XChcP001Jaff_LJx2A21x0axx0000_testname3',
                'tgl_pre_N9999991A_xxaxx1x20xaxx_T2xxx1x_0000_Mgt_0_vrevTA0X_cmt_hvm_cmt_PXJ_cfaff_1111111111',
                'tgl_pre_N9999992A_xxaxx1x20xaxx_T2xxx1x_0000_Mgt_0_vrevTA0X_cmt_hvm_cmt_PXJ_cfaff_1111111111x'}
        self.assertEqual(obj.get_tid_from_pats(pats), set('0748667_00 0748668_00 0748669_00'.split()))
        self.assertEqual(obj.get_tid_from_pats(pats, istestname=True), {'testname1', 'testname3'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, not needed for coverage"))
    def test_get_modname_map_real(self):
        tpobj = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env').pickle_init()
        self.assertEqual(len(tpobj.plists.get_modname_map()), 3018)

    def test_get_modname2(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        self.assertEqual(tp.plists.get_modname2('/a/fuse.plist'), 'MCclk')
        self.assertEqual(tp.plists.get_modname2('/a/aa.plist'), 'none')

    def test_get_modname_map(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile2.env')
        tp.init()
        self.assertEqual(tp.plists.get_modname_map(),
                         {'cpu_fuse_read_hvm_x': ('SCN', 'CCA'),
                          'cpu_fuse_read_special_x': ('SCN', 'CCB'),
                          'shops_H_list': ('ARR', 'CCB'),
                          'shops_L_list': ('ARR', 'CCA'),
                          'sublist': ('SCN', 'CCB')})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_cimod2mod_map(self):
        tp = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        result = tp.plists.get_cimod2mod_map()
        self.assertEqual(len(result), 67)
        self.assertEqual(len(list(keys_atlevel(result, 1))), 117)
        self.assertEqual(result['MCfus'], {'FUS_FUSEBURN_CXX',
                                           'FUS_FUSEREAD_CXX',
                                           'FUS_UNITINFO_CXX',
                                           'TPI_PUP_XXX'})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6tos4', chdir=True)
    def test_get_mod2plist_map(self):

        # Create .stpl that has a line with non Module (for coverage)
        File('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').touch(r'''Version 1.0;

SubTestPlans
{
   Common ..\..\Shared\a.imp;
   ..\..\Modules\ARR\array.mtpl;
   ..\..\Modules\SCN\scan.mtpl;
   ..\..\Modules\PTH\pth.mtpl;

   Final .\ProgramFlowsTestPlan\ProgramFlows.mtpl;
}''', newfile=True)
        File('Shared/a.imp').touch()

        # Create .mconfig with a .plist that is not found (for converage)
        File('./Modules/ARR/ARR.mconfig').touch('''
<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
        <Patterns>
                <PORRoot IP="IP_CPU" Path="I:\\hdmxpats\\mtl\\MCclk\" Rev="RevTCCXXA1.0" Patch="p2">
                        <PlistFiles>
                                <PlistFile BomGroup="CLASS_TGLH81">Shops.plist</PlistFile>
                                <PlistFile BomGroup="CLASS_TGLH81">Shops1.plist</PlistFile>
                        </PlistFiles>
                </PORRoot>
        </Patterns>
</ModuleConfiguration>
''', newfile=True)

        tp = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        result = tp.plists.get_mod2plist_map()
        self.assertEqual(result, {'ARR': {'Shops.plist'},
                                  'PTH': {'fuse.plist'},
                                  'SCN': {'fuse.plist'}})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6tos4', chdir=True)
    def test_get_mod2plist_map2(self):
        # No result - should not fail

        # Create .stpl that has a line with non Module (for coverage)
        File('POR_TP/TGLH81/SubTestPlan_CLASS_TGLH81.stpl').touch(r'''Version 1.0;

SubTestPlans
{
   Common ..\..\Shared\a.imp;

   Final .\ProgramFlowsTestPlan\ProgramFlows.mtpl;
}''', newfile=True)
        File('Shared/a.imp').touch()

        tp = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        result = tp.plists.get_mod2plist_map()
        self.assertEqual(result, {})
        result = tp.plists.get_cimod2mod_map()
        self.assertEqual(result, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest, not needed for coverage"))
    def test_get_mod2plist_map_bigtp(self):
        tp = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        result = tp.plists.get_mod2plist_map()
        self.assertEqual(len(result), 92)
        self.assertEqual(len(list(keys_atlevel(result, 1))), 340)
        self.assertEqual(result['DRV_RESET_CXX'], {'AAA_drv_cdie_C68_vrevC68P6X_ippkg_class_p68g2.plist',
                                                   'AAA_drv_cdie_C68_vrevC68P6P_class_class_p68g2.plist',
                                                   'drv_cdie_C68_reset_class_p68g2.plist',
                                                   'AAA_drv_cdie_C68_vrevC68P6P_ippkg_class_p68g2.plist',
                                                   'drv_cdie_C68_dfx_class_p68g2.plist',
                                                   'AAA_drv_cdie_C68_vrevC68P6X_class_class_p68g2.plist'})

        tp = TestProgram(f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env')
        result = tp.plists.get_mod2plist_map()
        self.assertEqual(result, {'ARR': {'Shops.plist'},
                                  'PTH': {'fuse.plist'},
                                  'SCN': {'fuse.plist'}})

    def test_get_mod2plist_map_cs(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3c/POR_TP/TGLH81/EnvironmentFile.env')
        result = tp.plists.get_mod2plist_map()
        self.assertEqual(len(result), 3)
        self.assertEqual(len(list(keys_atlevel(result, 1))), 3)

    @with_(TempDir, chdir=True)
    def test_readplist(self):
        # good template: given a plist file, read it
        text = """
GlobalPList list1 {
   Pat somepat7;
   Pat somepat8;
}
"""
        File('abc.plist').touch(text)
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')   # No init needed
        tpobj.plists.read_plist(['abc.plist'])
        self.assertEqual(sorted(tpobj.plists.get_pats_all()), ['somepat7', 'somepat8'])

        # testcase: confirm that it clears it
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').init()
        self.assertEqual(len(tpobj.plists.get_pats_all()), 46)
        tpobj.plists.read_plist('abc.plist')
        self.assertEqual(sorted(tpobj.plists.get_pats_all()), ['somepat7', 'somepat8'])

    @with_(TempDir, chdir=True)
    def test_refplist(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
GlobalPList list1 {
   PList list2;
   Pat somepat2;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList list2 [Mask] {
   Pat somepat1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        self.assertEqual(tp.plists.get_pats_from_plb('list1'), {'somepat2', 'somepat1'})
        self.assertEqual(tp.plists.get_pats_from_plb('list1', ref=False), {'somepat2'})
        self.assertEqual(tp.plists.get_subplists('list1'), {'list2', 'list1'})
        self.assertEqual(tp.plists.get_subplists('list2'), {'list2'})

    @with_(TempDir, chdir=True)
    def test_get_plist_dependent(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="a.plist" />
    <PListFile name="b.plist" />
    <PListFile name="c.plist" />
    <PListFile name="d.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
GlobalPList list1 {
   PList list3;
   Pat somepat1;
}
"""
        File('Msio/RevTTB0.1/p4/plb/a.plist').touch(text, mkdir=True)

        text = """
GlobalPList list2 [PreBurstPList list4] {
   Pat somepat2;
}
GlobalPList list3 {
   Pat somepat3;
}
"""
        File('Msio/RevTTB0.1/p4/plb/b.plist').touch(text, mkdir=True)

        text = """
GlobalPList list5 {
   Pat somepat5;
}
GlobalPList list4 {
   PList list5;
   Pat somepat4;
}
"""
        File('Msio/RevTTB0.1/p4/plb/c.plist').touch(text, mkdir=True)

        # this plist is has no dependency
        text = """
GlobalPList list6 {
   Pat somepat6;
}
"""
        File('Msio/RevTTB0.1/p4/plb/d.plist').touch(text, mkdir=True)

        File("TPL/a.tpl").touch()    # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        result = tp.plists.get_plist_dependent()
        self.assertEqual(result, {'a.plist': {'b.plist'},
                                  'b.plist': {'c.plist'},
                                  'c.plist': set(),
                                  'd.plist': set()
                                  })
        result2 = tp.plists.get_refplist()
        self.assertEqual(result2, {'list1': ['list3'],
                                   'list2': ['list4'],
                                   'list4': ['list5']})

        # check final sorted
        from gadget.tputil import MtplBlocks
        final = MtplBlocks.dependent_values(result)
        self.assertEqual(sorted(final, key=lambda x: (final[x], x)), ['c.plist', 'b.plist', 'd.plist', 'a.plist'])

    @with_(TempDir, chdir=True)
    def test_preburst(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
GlobalPList list1 [PreBurstPList list2] [PostBurstPList list3]{
   Pat somepat2;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList list2 [Mask] {
   Pat somepat1;
}
GlobalPList list3 [Mask] {
   Pat somepat3;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        self.assertEqual(tp.plists.get_pats_from_plb('list1'), {'somepat2', 'somepat1', 'somepat3'})
        self.assertEqual(tp.plists.get_subplists('list1'), {'list2', 'list1', 'list3'})

        self.assertEqual(tp.plists.get_pats_from_plb('list2x', iserror=False), set())
        with self.assertRaisesRegex(ErrorInput, 'is not found in any'):
            tp.plists.get_pats_from_plb('list2x')

    @with_(TempDir, chdir=True)
    def test_tos4_skippreplist(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
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
PList reset1 {
   Pat tgl_pre_0;
}
PList list1 {
   RefPList list2;
   RefPList list3 [SkipPrePListExec];
}
PList list2 {
   Pat main1;
}
PList list3 {
   Pat main2;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)

        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        tp.is_tos4 = True
        tp.plists.set_pat2plb()
        self.assertEqual(tp.plists.get_pats_from_plb('list1'), {'main1', 'main2'})

    @with_(TempDir, chdir=True)
    def test_tos4_set_pat2plb(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
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
PList reset1 {
   Pat tgl_pre_0;
}
PList list1 {
   PreExecRefPList reset1;
   PreExecPat resetpat1;
   Pat main1;
}
PList list2 {
   Pat main1;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)

        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        tp.is_tos4 = True
        tp.plists.set_pat2plb()
        self.assertEqual(sorted(tp.plists.get_plb_map()), ['list1', 'list2', 'reset1'])
        self.assertEqual(sorted(tp.plists.get_pats_all()),
                         ['main1',
                          'resetpat1',
                          'tgl_pre_0'])

        self.assertEqual(tp.plists.get_pats_from_plb('list1'), {'tgl_pre_0', 'resetpat1', 'main1'})
        self.assertEqual(tp.plists.get_pats_from_plb('list1', patonly=True), {'tgl_pre_0', 'main1'})
        self.assertEqual(tp.plists.get_plbs_usedby_pat('main1'), {'list1', 'list2'})

        pprint(tp.plists.get_plbs_usedby_pats({'main1', 'tgl_pre_0'}))
        self.assertEqual(tp.plists.get_plbs_usedby_pats({'main1', 'tgl_pre_0', 'notfound'}),
                         {'main1': {'list2', 'list1'},
                         'tgl_pre_0': {'reset1'}})

    @with_(TempDir, chdir=True)
    def test_tos4_basic(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
PList list1 {
   Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0;
   UserBurstBreak Break_2;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
PList list2 {
   Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        tp.is_tos4 = True
        tp.plists.set_pat2plb()
        self.assertEqual(sorted(tp.plists.get_plb_map()), ['list1', 'list2'])
        pprint(sorted(tp.plists.get_pats_all()))
        self.assertEqual(sorted(tp.plists.get_pats_all()),
                         ['tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0',
                          'tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_1'])

    @with_(TempDir, chdir=True)
    def test_tos4_resetplb(self):
        # found by ctp on nvl by Richelle
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
PList resetplb_808xxxxxxx8mxxxx {
   Pat g0010959H0029393G_Kd_A0Xab00_HA4PHHAAC0509_reset;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
PList list2 {
   PreExecRefPList resetplb_808xxxxxxx8mxxxx;
   Pat g0010958H0029393G_Kd_A0Xab00_HA4PHHAAC0509;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        tp.is_tos4 = True
        tp.plists.set_pat2plb()
        self.assertEqual(sorted(tp.plists.get_pats_from_plb('list2', patonly=True)),
                         ['g0010958H0029393G_Kd_A0Xab00_HA4PHHAAC0509'])

    @with_(TempDir, chdir=True)
    def test_invalidplist(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
GlobalPList list1 {
   PList list2;
   What some;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList list2 [Mask] {
   Pat somepat1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        with self.assertRaisesRegex(ErrorInput, 'Invalid line#4'):
            tp.plists.set_pat2plb()

    @with_(TempDir, chdir=True)
    def test_missingplb(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
GlobalPList list1 {
   PList list3;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList list2 [Mask] {
   Pat somepat1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        data = {'MODA': {'abc.plist', 'sup1.plist'}}
        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        with self.assertRaisesRegex(ErrorInput, 'GlobalPList list3 is not found'):
            with MockVar(tp.plists, 'get_mod2plist_map', Mock(return_value=data)):
                tp.plists.set_pat2plb()

    @with_(TempDir, chdir=True)
    def test_missingplist(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup2.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
GlobalPList list1 {
   PList list3;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        data = {'MODA': {'abc.plist', 'sup1.plist'}}
        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        with self.assertRaisesRegex(ErrorEnv, 'Cannot find'):
                tp.plists.set_plist_list()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_all_plists(self):
        tpobj = TestProgram(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env', allpats=True)
        result = tpobj.plists.get_all_plists()
        self.assertEqual(result, [f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/PLIST_ALL_CLASS_P68G2.plist.xml',
                                  f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/./PLIST_ALL_IP_PCH.plist.ipxml',
                                  f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/./PLIST_ALL_IP_CPU.plist.ipxml'])
        tpobj = TestProgram(f'{UT_DIR}/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tpobj.plists.get_all_plists(), [f'{UT_DIR}/Simple1/TPL/PLIST_ALL.xml'])

    def test_tos4(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6tos4/POR_TP/TGLH81/EnvironmentFile.env')
        tpobj.plists.set_plb_map()   # Read the patterns (pgmrules may change patlist)
        tpobj.plists.set_pat2plb()
        self.assertEqual(len(tpobj.plists.get_plb_map()), 3)
        self.assertEqual(tpobj.plists.get_cimod2mod_map(), {'MCclk': {'PTH', 'ARR', 'SCN'}})


class TestFlat(TestCase):

    def setup_env_xml(self):
        """Common setup"""
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

    @with_(TempDir, chdir=True)
    def test_basic(self):
        # tests the _plbattr
        # tests PrePList
        self.setup_env_xml()

        text = """
GlobalPList listm {
   GlobalPList list1 [PrePList resetplb_a] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 [PreBurstPList resetplb_a] {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list3 [BurstOff] [PreBurstPList resetplb_a] {
      Pat somepat5;
      Pat somepat6;
   }
   GlobalPList list4 {  # no reset
      Pat somepat7;
      PList resetplb_a;
      Pat somepat8;
   }
   GlobalPList list5 [PostPList resetplb_a] {
      Pat somepat9;
      Pat somepat10;
   }
   GlobalPList list6 [PostBurstPList resetplb_a] {
      Pat somepat11;
      Pat somepat12;
   }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()

        # basic
        # result = ['']
        result = tp.plists.get_flat('listm')
        expect = '''
resetplb_a
somepat1
resetplb_a
somepat2
resetplb_a
somepat3
somepat4
resetplb_a
somepat5
resetplb_a
somepat6
somepat7
resetplb_a
somepat8
somepat9
resetplb_a
somepat10
resetplb_a
somepat11
somepat12
resetplb_a'''
        self.assertTextEqual('\n'.join(result), expect)

        # with patterns, one list
        expect = '''resetpat1
resetpat2
somepat5
resetpat1
resetpat2
somepat6'''
        self.assertTextEqual('\n'.join(tp.plists.get_flat('list3', stopat=re.compile('^blah'))),
                             expect)

    @with_(TempDir, chdir=True)
    def test_case2(self):
        # tests PreBurst
        self.setup_env_xml()

        text = """
GlobalPList listm {
   GlobalPList list1 [PrePattern reset1] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 [PreBurst reset1] {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list3 [BurstOff] [PreBurst reset1] {
      Pat somepat5;
      Pat somepat6;
   }
   GlobalPList list4 {  # no reset
      Pat somepat7;
      PList resetplb_a;
      Pat somepat8;
   }
   GlobalPList list5 [PostPattern reset1] {
      Pat somepat9;
      Pat somepat10;
   }
   GlobalPList list6 [PostBurst reset1] {
      Pat somepat11;
      Pat somepat12;
   }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()

        # basic
        result = tp.plists.get_flat('listm', stopat=re.compile('^XXX'))
        expect = '''
reset1
somepat1
reset1
somepat2
reset1
somepat3
somepat4
reset1
somepat5
reset1
somepat6
somepat7
resetpat1
resetpat2
somepat8
somepat9
reset1
somepat10
reset1
somepat11
somepat12
reset1'''
        self.assertTextEqual('\n'.join(result), expect)

        # with patterns, one list
        expect = '''reset1
somepat5
reset1
somepat6'''
        self.assertTextEqual('\n'.join(tp.plists.get_flat('list3')), expect)
        self.assertEqual(tp.plists.get_flat('list3*list4'), ['IGNORED:list3*list4'])

    @with_(TempDir, chdir=True)
    def test_burst(self):
        self.setup_env_xml()

        text = """
GlobalPList listm {
   GlobalPList list1 [PreBurstPList resetplb_a] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 [PreBurstPList resetplb_a] {
      Pat somepat3;
      Pat somepat4;
      Pat resetplb_a;
      Pat somepat5;
   }
}
GlobalPList listy {
   GlobalPList list3 [PreBurst resetplb_a] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list4 [PreBurst resetplb_a] {
      Pat somepat3;
      Pat somepat4;
   }
}
GlobalPList listz {
   GlobalPList list5 [PreBurstPList resetplb_a] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list6 [PreBurstPList resetplb_a] {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list7 [PreBurstPList resetplb_b] {
      Pat somepat5;
      Pat somepat6;
   }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList resetplb_b {
   Pat resetpat1;
   Pat resetpat2
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()

        # 2 PreBurstPlist
        result = tp.plists.get_flat('listm')
        expect = '''
resetplb_a
somepat1
somepat2
somepat3
somepat4
resetplb_a
somepat5
'''
        self.assertTextEqual('\n'.join(result), expect)

        # 2 PreBurst
        result = tp.plists.get_flat('listy')
        expect = '''
resetplb_a
somepat1
somepat2
somepat3
somepat4
'''
        self.assertTextEqual('\n'.join(result), expect)

        # PreBurst different plist
        result = tp.plists.get_flat('listz')
        expect = '''
resetplb_a
somepat1
somepat2
somepat3
somepat4
resetplb_b
somepat5
somepat6
'''
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    def test_toplevel(self):
        self.setup_env_xml()

        text = """
GlobalPList listm [PreBurstPList resetplb_a] {
   GlobalPList list1 {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list3 [PreBurstPList resetplb_b] {
      Pat somepat5;
      Pat somepat6;
   }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList resetplb_b {
   Pat resetpat1;
   Pat resetpat2
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()

        # top level
        result = tp.plists.get_flat('listm')
        expect = '''
resetplb_a
somepat1
somepat2
somepat3
somepat4
resetplb_b
somepat5
somepat6
'''
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    def test_duplevel(self):
        self.setup_env_xml()

        text = """
GlobalPList listm [PreBurstPList resetplb_a] {
  GlobalPList listy [PreBurstPList resetplb_a] {
   GlobalPList list1 [PreBurstPList resetplb_a] [PostPattern pst1] [PostBurstPList dlvr] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 [PreBurstPList resetplb_a] [PostPattern pst1] [PostBurstPList dlvr] {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list3 [PreBurstPList resetplb_b] [PostPattern pst1] [PostBurstPList dlvr] {
      Pat somepat5;
      Pat somepat6;
   }
 }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList resetplb_b {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList dlvr {
   Pat dlvr1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()
        # pprint(tp.plists._plbattr)
        # pprint(tp.plists._plb2any)

        # top level
        result = tp.plists.get_flat('listm')
        expect = '''
resetplb_a
somepat1
pst1
somepat2
pst1
somepat3
pst1
somepat4
pst1
resetplb_b
somepat5
pst1
somepat6
pst1
dlvr1
'''
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    def test_duplevel_burstoff(self):
        self.setup_env_xml()

        text = """
GlobalPList listm [PreBurstPList resetplb_a] {
  GlobalPList listy [PreBurstPList resetplb_a] {
   GlobalPList list1 [PreBurstPList resetplb_a] [PostPattern pst1] [PostBurstPList dlvr] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 [PreBurstPList resetplb_a] [PostPattern pst1] [PostBurstPList dlvr] [BurstOff] {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list3 [PreBurstPList resetplb_b] [PostPattern pst1] [PostBurstPList dlvr] {
      Pat somepat5;
      Pat somepat6;
   }
 }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList resetplb_b {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList dlvr {
   Pat dlvr1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()

        # top level
        result = tp.plists.get_flat('listm')
        expect = '''
resetplb_a
somepat1
pst1
somepat2
pst1
resetplb_a
somepat3
pst1
dlvr1
resetplb_a
somepat4
pst1
dlvr1
resetplb_b
somepat5
pst1
somepat6
pst1
dlvr1
'''
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    def test_duplevel_burstoff2(self):
        self.setup_env_xml()

        text = """
GlobalPList listm [PreBurstPList resetplb_a] {
  GlobalPList listy [PreBurstPList resetplb_a] {
   GlobalPList list1 [PreBurstPList resetplb_a] [PostPattern pst1] [PostBurstPList dlvr] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 [PreBurstPList resetplb_a] [PostPattern pst1] [PostBurst dlvr1] [BurstOff] {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list3 [PreBurstPList resetplb_b] [PostPattern pst1] [PostBurstPList dlvr] {
      Pat somepat5;
      Pat somepat6;
   }
 }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList resetplb_b {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList dlvr {
   Pat dlvr1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()

        # top level
        result = tp.plists.get_flat('listm')
        expect = '''
resetplb_a
somepat1
pst1
somepat2
pst1
resetplb_a
somepat3
pst1
dlvr1
resetplb_a
somepat4
pst1
dlvr1
resetplb_b
somepat5
pst1
somepat6
pst1
dlvr1
'''
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    def test_bugscn(self):
        self.setup_env_xml()

        text = """
GlobalPList listm [PreBurstPList scn_pre] [PostPList dlvr] {
   GlobalPList list1 [PrePattern pre1] {
      Pat somepat1;
      Pat somepat2;
   }
   GlobalPList list2 [PrePattern pre1] {
      Pat somepat3;
      Pat somepat4;
   }
   GlobalPList list3 [PrePattern pre1] {
      Pat somepat5;
      Pat somepat6;
   }
}
GlobalPList scn_pre {
   PList resetplb_a;
   Pat init;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList resetplb_a {
   Pat resetpat1;
   Pat resetpat2
}
GlobalPList dlvr {
   Pat dlvr1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()

        # top level
        result = tp.plists.get_flat('listm')
        # return
        expect = '''
resetplb_a
init
pre1
somepat1
pre1
somepat2
dlvr1
pre1
somepat3
pre1
somepat4
dlvr1
pre1
somepat5
pre1
somepat6
dlvr1
'''
        self.assertTextEqual('\n'.join(result), expect)

    @with_(TempDir, chdir=True)
    def test_get_pats_from_plb_order_true(self):
        self.setup_env_xml()

        text = """
GlobalPList listm {
   PList ref_a;
   GlobalPList list1 {
      Pat somepat1;
      Pat somepat2;
   }
   PList ref_a;
   GlobalPList list2 {
      Pat somepat3;
      Pat somepat4;
   }
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
GlobalPList ref_a {
   Pat refpat1;
   Pat refpat2;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        tp.plists.set_pat2plb()
        result = tp.plists.get_pats_from_plb('listm', order=True)
        expect = [
            'refpat1',
            'refpat2',
            'somepat1',
            'somepat2',
            'refpat1',
            'refpat2',
            'somepat3',
            'somepat4'
        ]

        self.assertEqual(result, expect)


class TestCTags(TestCase):

    def test_ut_get_pat_options(self):
        self.assertEqual(Plists._get_pat_options('Pat ', None, None), (False, []))
        self.assertEqual(Plists._get_pat_options('Pat [oops', re.compile(r'\[(.+)\]'), re.compile(r"\s*;.*")),
                         (False, []))
        self.assertEqual(Plists._get_pat_tags('Pat ', None), (False, []))

    @with_(TempDir, chdir=True)
    def test_tos4_basic(self):
        text = """
HDST_PLIST_PATH = "./Supersedes/patterns;" +
                  "./Msio/RevTTB0.1/p5/plb;" +
                  "./Msio/RevTTB0.1/p4/plb"
"""
        File("TPL/a.env").touch(text, mkdir=True)

        text = """<HdmtReferenceFile>
  <PList>
    <PListFile name="abc.plist" />
    <PListFile name="sup1.plist" />
  </PList>
</HdmtReferenceFile>
"""
        File("TPL/x.xml").touch(text)

        text = """
PList list1 {
   Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0;   #KEEP#
   Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_2 [Skip];
   UserBurstBreak Break_2;
}
"""
        File('Msio/RevTTB0.1/p4/plb/abc.plist').touch(text, mkdir=True)
        text = """
PList list2 {
   Pat tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_1;
}
"""
        File('Supersedes/patterns/sup1.plist').touch(text, mkdir=True)
        File("TPL/a.tpl").touch()   # dummy tpl
        File("TPL/a.stpl").touch()   # dummy stpl

        tp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='')
        tp.is_tos4 = True
        tp.plists.set_pat2plb()
        tp.plists.read_pat_details()
        self.assertEqual(tp.plists.get_pat_details(),
                         ({'list1': {'tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_2': ['Skip']}},
                          {'list1': {'tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0': ['KEEP']}}))

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_cttr_simple_first(self):
        testplist = """
    GlobalPList mainlist {
          Pat somepat1; #KEEP#
          Pat somepat2; #keep#
    }
    """
        epattags = {
            "mainlist": {
                "somepat1": ["KEEP"],
                "somepat2": ["KEEP"]
            }
        }
        epatopts = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_simple_sec(self):
        testplist = """
GlobalPList mainlist {
      Pat somepat1; #SDS,KEEP#
      Pat somepat2; #SIMPLE COMMENT
      Pat somepat3; #KEEP#      #SIMPLE COMMENT POST TAG
      Pat somepat4; # KEEP#      #SIMPLE COMMENT POST TAG
      Pat somepat5; # KEEP #      #SIMPLE COMMENT POST TAG
      Pat somepat6;#KEEP #      #SIMPLE COMMENT POST TAG
      Pat somepat7;
}
        """
        epattags = {
            "mainlist": {
                "somepat1": ["KEEP", "SDS"],
                "somepat3": ["KEEP"],
                "somepat4": ["KEEP"],
                "somepat5": ["KEEP"],
                "somepat6": ["KEEP"]
            }
        }
        epatopts = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_all_patts(self):
        testplist = """
GlobalPList mainlist {
      Pat somepat1; #keep#
      Pat somepat2; #keep#
}
        """
        epattags = {
            "mainlist": {
                "somepat1": ["KEEP"],
                "somepat2": ["KEEP"]
            }
        }
        epatopts = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_rep(self):
        testplist = """
GlobalPList mainlist {
      Pat somepat1;
      Pat somepat2;
      Pat somepat1; #KEEP#
      Pat somepat1; #KEEP#
      Pat somepat1; #SDS#
}
            """
        epattags = {
            "mainlist": {
                "somepat1": ["KEEP", "SDS"]
            }
        }
        epatopts = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_multi_sorted_nest(self):
        testplist = """
GlobalPList mainlist {
    Pat mompat1; #KEEP#
    Pat mompat2 ; #SDS#
    GlobalPList nest1 {
          Pat nestedpat1; #KEEP#
          Pat nestedpat2;
    }
    Pat mompat3; #keep#
    Pat mompat4;
    GlobalPList nest2 {
          Pat nestedpat1; #SDS#
          Pat nestedpat2; #KEEP#
          Pat nestedpat3;
          Pat nestedpat4;
        GlobalPList nest2nest1 {
              Pat nestedpat5; #KEEP#
        }
    }
}
    """
        epattags = {
            "mainlist": {
                "mompat1": ["KEEP"],
                "mompat2": ["SDS"],
                "mompat3": ["KEEP"],
                "nestedpat1": ["KEEP", "SDS"],
                "nestedpat2": ["KEEP"],
                "nestedpat5": ["KEEP"]
            },
            "nest1": {
                "nestedpat1": ["KEEP"]
            },
            "nest2": {
                "nestedpat1": ["SDS"],
                "nestedpat2": ["KEEP"],
                "nestedpat5": ["KEEP"]
            },
            "nest2nest1": {
                "nestedpat5": ["KEEP"]
            },
        }
        epatopts = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    # TODO: TEST FOR TOS4
    def ttr_tp_init_setup(self, testplist):
        """Common setup"""
        text = """
        HDST_PLIST_PATH = "./Supersedes/patterns;" +
                          "./Msio/RevTTB0.1/p5/plb;" +
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

        File('Supersedes/patterns/abc.plist').touch(testplist, mkdir=True)
        File("TPL/a.tpl").touch()  # dummy tpl
        File("TPL/a.stpl").touch()  # dummy stpl
        otp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        return otp


class TestPatOpts(TestCase):

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_simple_first(self):
        testplist = """
GlobalPList mainlist {
      Pat somepat1 [BurstOff];
      Pat somepat2;
}
        """
        epatopts = {
            "mainlist": {
                "somepat1": ["BurstOff"]
            }
        }
        epattags = {}

        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_simple_sec(self):
        testplist = """
GlobalPList mainlist {
      Pat somepat1 ;
      Pat somepat2 [ BurstOff];
}
        """
        epatopts = {
            "mainlist": {
                "somepat2": ["BurstOff"]
            }
        }
        epattags = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_all_patts(self):
        testplist = """
GlobalPList mainlist {
      Pat somepat1 [Mask TDO];
      Pat somepat2 [BurstOff];
}
        """
        epatopts = {
            "mainlist": {
                "somepat1": ["Mask TDO"],
                "somepat2": ["BurstOff"]
            }
        }
        epattags = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_rep(self):
        testplist = """
GlobalPList mainlist {
      Pat somepat1 [Mask TDO];
      Pat somepat2 [BurstOff];
      Pat somepat1 [BurstOff] [Mask DDR];
      Pat somepat1 ;
}
        """
        epatopts = {
            "mainlist": {
                "somepat1": ["BurstOff", "Mask DDR", "Mask TDO"],
                "somepat2": ["BurstOff"]
            }
        }
        epattags = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    @with_(TempDir, chdir=True)
    def test_tos3_read_pat_details_multi_sorted_nest(self):
        testplist = """
GlobalPList mainlist {
    Pat mompat1 [Mask TDO];
    Pat mompat2 [Unmask A] [BurstOff] ;
    GlobalPList nest1 {
          Pat nestedpat1 [Mask TDO];
          Pat nestedpat2 [Unmask A] [BurstOff] ;
    }
    Pat mompat3 [Mask DDR];
    Pat mompat4;
    GlobalPList nest2 {
          Pat nestedpat1 [Mask TDO] [Unmask A] [BurstOff];
          Pat nestedpat2 [Unmask DDR] [BurstOff];
          Pat nestedpat3;
          Pat nestedpat4 [BurstOff];
        GlobalPList nest2nest1 {
              Pat nestedpat5 [Mask TDO];
        }
    }
}
        """
        epatopts = {
            "mainlist": {
                "mompat1": ["Mask TDO"],
                "mompat2": ["BurstOff", "Unmask A"],
                "mompat3": ["Mask DDR"],
                "nestedpat1": ["BurstOff", "Mask TDO", "Unmask A"],
                "nestedpat2": ["BurstOff", "Unmask A", "Unmask DDR"],
                "nestedpat4": ["BurstOff"],
                "nestedpat5": ["Mask TDO"]
            },
            "nest1": {
                "nestedpat1": ["Mask TDO"],
                "nestedpat2": ["BurstOff", "Unmask A"],
            },
            "nest2": {
                "nestedpat1": ["BurstOff", "Mask TDO", "Unmask A"],
                "nestedpat2": ["BurstOff", "Unmask DDR"],
                "nestedpat4": ["BurstOff"],
                "nestedpat5": ["Mask TDO"]
            },
            "nest2nest1": {
                "nestedpat5": ["Mask TDO"]
            },
        }
        epattags = {}
        expected = (epatopts, epattags)
        otp = self.ttr_tp_init_setup(testplist)
        otp.plists.read_pat_details()
        result = otp.plists.get_pat_details()
        self.assertEqual(expected, result)

    # TODO: TEST FOR TOS4
    def ttr_tp_init_setup(self, testplist):
        """Common setup"""
        text = """
        HDST_PLIST_PATH = "./Supersedes/patterns;" +
                          "./Msio/RevTTB0.1/p5/plb;" +
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

        File('Supersedes/patterns/abc.plist').touch(testplist, mkdir=True)
        File("TPL/a.tpl").touch()  # dummy tpl
        File("TPL/a.stpl").touch()  # dummy stpl
        otp = TestProgram("TPL/a.env", allplist="TPL/x.xml", tpl='', allpats=True)
        return otp


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
