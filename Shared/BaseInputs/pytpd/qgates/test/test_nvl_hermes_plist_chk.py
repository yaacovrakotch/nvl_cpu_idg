#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""Run unittest for nvl_hermes_plist_chk.py."""
import sys
from os.path import basename, dirname, join, exists

try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV

from unittest.mock import Mock

from qgates.nvl_hermes_plist_chk import HermesPlistChk
from tp.testprogram import TestProgram
from gadget.files import TempDir, File
from gadget.ut import TestCase, unittest, MockVar


class TestHermesPlistChk(TestCase):

    def setUp(self):
        # Preserve global switch modified in tests
        self._orig_disable_deep = HermesPlistChk.DISABLE_DEEP_PAT_365

    def tearDown(self):
        # Restore global switch after each test
        HermesPlistChk.DISABLE_DEEP_PAT_365 = self._orig_disable_deep

    @staticmethod
    def _new_mock_tpobj(envdir='C:/tmp/ENV'):
        # Build a minimal tpobj for unit tests
        tpobj = Mock()
        tpobj.envdir = envdir
        tpobj.envfile = join(envdir, 'EnvironmentFile.env')
        tpobj.mtpl = Mock()
        tpobj.plists = Mock()
        tpobj.plists.get_plb_map.return_value = {}
        tpobj.plists.get_rev_paths.return_value = set()
        tpobj.get_all_mtpl_from_stpl.return_value = []
        tpobj.mtpl.get_modfolder2mod.return_value = {}
        tpobj.mtpl.iter_flows.return_value = []
        return tpobj

    def test_simple_helpers(self):
        # Validate simple helper methods
        self.assertEqual(HermesPlistChk._get_first_present({'Patlist': 'A'}, ('Patlist', 'patlist')), 'A')
        self.assertEqual(HermesPlistChk._get_first_present({'patlist': 'B'}, ('Patlist', 'patlist')), 'B')
        self.assertIsNone(HermesPlistChk._get_first_present({}, ('Patlist', 'patlist')))

        self.assertEqual(HermesPlistChk._get_first_present({'TEMPLATE': 'T1'}, ('TEMPLATE', 'Template', 'template')), 'T1')
        self.assertEqual(HermesPlistChk._get_first_present({'Template': 'T2'}, ('TEMPLATE', 'Template', 'template')), 'T2')
        self.assertEqual(HermesPlistChk._get_first_present({'template': 'T3'}, ('TEMPLATE', 'Template', 'template')), 'T3')
        self.assertIsNone(HermesPlistChk._get_first_present({}, ('TEMPLATE', 'Template', 'template')))

        self.assertTrue(HermesPlistChk._is_master_patlist('abc_master'))
        self.assertTrue(HermesPlistChk._is_master_patlist('ABC_MASTER'))
        self.assertFalse(HermesPlistChk._is_master_patlist('abc'))
        self.assertFalse(HermesPlistChk._is_master_patlist(None))

        self.assertEqual(HermesPlistChk._normalize_path(r'A\\B//C'), 'A/B/C')
        self.assertEqual(str('IPX::a_b_master').strip().split('::')[-1], 'a_b_master')
        self.assertEqual(str('single').strip().split('::')[-1], 'single')

        self.assertEqual(HermesPlistChk._normalize_refpair_key('abc_short__0'), 'abc')
        self.assertEqual(HermesPlistChk._normalize_refpair_key('abc_long__1'), 'abc')

        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('pth_cdie_dts_list'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('Pat abc_midcat_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('Pat abc_init_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('Pat abc_reset_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('Pat abc_preburst_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('Pat abc__preburst_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('RefPList abc_reset_xyz'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('RefPList abc_preburst_xyz'))
        self.assertTrue(HermesPlistChk._is_allowed_nonpair_ref('RefPList abc__preburst_xyz'))
        self.assertFalse(HermesPlistChk._is_allowed_nonpair_ref('pth_cdie_temp_list'))

        self.assertTrue(HermesPlistChk._is_allowed_master_pat_line('Pat abc_acm_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_master_pat_line('Pat abc_midcat_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_master_pat_line('Pat abc_init_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_master_pat_line('Pat abc_reset_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_master_pat_line('Pat abc_preburst_xyz;'))
        self.assertTrue(HermesPlistChk._is_allowed_master_pat_line('Pat abc__preburst_xyz;'))
        self.assertFalse(HermesPlistChk._is_allowed_master_pat_line('Pat abc_xyz;'))

        self.assertTrue(HermesPlistChk._is_362_363_exempt_by_testname('X_FFSEARCH_YYY'))
        self.assertTrue(HermesPlistChk._is_362_363_exempt_by_testname('X_RAW_YYY'))
        self.assertFalse(HermesPlistChk._is_362_363_exempt_by_testname('X_NORMAL_YYY'))

        self.assertEqual(HermesPlistChk._extract_speedflow_fn('AAA_VMIN_BB_F1XCC_DD'), '1')
        self.assertEqual(HermesPlistChk._extract_speedflow_fn('AAA_APEX_BB_F5XCC_DD'), '5')
        self.assertIsNone(HermesPlistChk._extract_speedflow_fn('AAA_VMIN_BB_F6XCC_DD'))
        self.assertEqual(HermesPlistChk._extract_speedflow_token('AAA_VMIN_BB_F1XCC_DD'), 'F1XCC')
        self.assertEqual(HermesPlistChk._extract_speedflow_token('AAA_APEX_BB_F5X_DD'), 'F5X')
        self.assertIsNone(HermesPlistChk._extract_speedflow_token('AAA_VMIN_BB_F6XCC_DD'))
        self.assertEqual(HermesPlistChk._get_speedflow_match_tokens('F5XCCFLO'), ['F5XCCFLO', 'F5XCCF'])
        self.assertEqual(HermesPlistChk._get_speedflow_match_tokens('F5X'), ['F5X'])
        self.assertEqual(HermesPlistChk._get_speedflow_display_token([]), '')
        self.assertEqual(HermesPlistChk._get_speedflow_display_token(['F5XCCFLO', 'F5XCCF']), 'F5XCCF')
        self.assertTrue(HermesPlistChk._plist_name_has_fn('plist_f1xcc_master', HermesPlistChk._get_speedflow_match_tokens('F1XCC')))
        self.assertTrue(HermesPlistChk._plist_name_has_fn('abc_f5x__0', HermesPlistChk._get_speedflow_match_tokens('F5X')))
        self.assertTrue(HermesPlistChk._plist_name_has_fn('fun_cdie_f3xcr_mlc_hptp800_list_master', HermesPlistChk._get_speedflow_match_tokens('F3XCR')))
        self.assertTrue(HermesPlistChk._plist_name_has_fn('arr_cdie_f5xccf_master', HermesPlistChk._get_speedflow_match_tokens('F5XCCFLO')))
        self.assertFalse(HermesPlistChk._plist_name_has_fn('plist_f2x_master', HermesPlistChk._get_speedflow_match_tokens('F1X')))
        self.assertFalse(HermesPlistChk._plist_name_has_fn('plist_f13x_master', HermesPlistChk._get_speedflow_match_tokens('F1X')))
        self.assertFalse(HermesPlistChk._plist_name_has_fn('plist_f2xcr_master', HermesPlistChk._get_speedflow_match_tokens('F2X')))

    def test_add_pass_and_add_error_use_hardcoded_codes(self):
        # Validate add_pass/add_error calls in HermesPlistChk use hardcoded integer error codes
        source_path = join(dirname(dirname(__file__)), 'nvl_hermes_plist_chk.py')
        source_text = File(source_path).read()

        self.assertNotRegex(source_text, r'self\.add_pass\(\s*self\.ERR_')
        self.assertNotRegex(source_text, r'self\.add_error\(\s*self\.ERR_')

    def test_is_speedflow(self):
        # Validate speedflow regex matching
        obj = HermesPlistChk(self._new_mock_tpobj())
        self.assertTrue(obj._is_speedflow_test('ABC_VMIN_XX_F1XABC_DEF'))
        self.assertTrue(obj._is_speedflow_test('ABC_APEX_XX_F5XABC_DEF'))
        self.assertFalse(obj._is_speedflow_test('ABC_VMIN_XX_F6XABC_DEF'))
        self.assertFalse(obj._is_speedflow_test('ABC_OTHER_XX_F1XABC_DEF'))

    def test_get_plist_names_from_ipxml_variants(self):
        # Validate xml parse success, regex fallback, and missing-file behavior
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'ENV1')
            File(join(envdir, 'dummy.txt')).touch('', mkdir=True, newfile=True)
            tpobj = self._new_mock_tpobj(envdir=envdir)
            obj = HermesPlistChk(tpobj)

            good_xml = join(envdir, 'PLIST_ALL_IPX.plist.xml')
            File(good_xml).touch('<Root><PListFile name="one.plist"/><PListFile name="two.plist"/></Root>', newfile=True)
            self.assertEqual(obj._get_plist_names_from_ipxml('IPX'), {'one.plist', 'two.plist'})

            File(good_xml).touch('<Root><PListFile name="fallback_a.plist"><BROKEN></Root>', newfile=True)
            self.assertEqual(obj._get_plist_names_from_ipxml('IPX'), {'fallback_a.plist'})

            self.assertEqual(obj._get_plist_names_from_ipxml('IPY'), set())

    def test_build_modinfo_and_find_master(self):
        # Validate mconfig parsing, BOMGROUP selection, and master lookup paths
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'BOM_A')
            File(join(envdir, 'dummy.txt')).touch('', mkdir=True, newfile=True)

            mod_folder = join(tdir, 'X', 'Modules', 'MODFOLDER')
            mtpl_file = join(mod_folder, 'Flow.mtpl')
            mconfig_file = join(mod_folder, 'module.mconfig')

            File(mtpl_file).touch('dummy', mkdir=True, newfile=True)
            File(mconfig_file).touch(
                '<IPName>IPAA</IPName>\n'
                '<PORRoot PATH="C:/PORA" REV="R0" PATCH="P0" BOMGROUP="OTHER"/>\n'
                '<PORRoot PATH="C:/PORB" REV="R1" PATCH="P1" BOMGROUP="BOM_A"/>\n',
                newfile=True
            )

            ipxml = join(envdir, 'PLIST_ALL_IPAA.plist.xml')
            File(ipxml).touch('<Root><PListFile name="my_all.plist"/></Root>', newfile=True)

            tpobj = self._new_mock_tpobj(envdir=envdir)
            tpobj.get_all_mtpl_from_stpl.return_value = [mtpl_file]
            tpobj.mtpl.get_modfolder2mod.return_value = {'MODFOLDER': 'ARR_MOD'}

            obj = HermesPlistChk(tpobj)
            modinfo = obj._build_modinfo()

            self.assertIn('ARR_MOD', modinfo)
            self.assertEqual(modinfo['ARR_MOD']['ipname'], 'IPAA')
            self.assertEqual(modinfo['ARR_MOD']['plb_path'], 'C:/PORB/R1/P1/plb')
            self.assertEqual(modinfo['ARR_MOD']['plist_names'], {'my_all.plist'})

            plb_dir = modinfo['ARR_MOD']['plb_path']
            plist_path = join(plb_dir, 'my_all.plist')
            File(plist_path).touch('PList sample_master {\n}\n', mkdir=True, newfile=True)

            found_without_fallback = obj._find_master_in_plists('sample_master', modinfo['ARR_MOD'], {})
            self.assertIsNone(found_without_fallback)

            tpobj.plists.get_rev_paths.return_value = {plb_dir}
            found_by_fallback = obj._find_master_in_plists('sample_master', modinfo['ARR_MOD'], {'sample_master': plist_path})
            self.assertTrue(str(found_by_fallback).endswith('/my_all.plist'))

    def test_build_modinfo_continue_branches_and_default_por_selection(self):
        # Validate skip/continue branches and fallback to first PORRoot when BOMGROUP does not match
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'ENV_BOM')
            File(join(envdir, 'dummy.txt')).touch('', mkdir=True, newfile=True)

            base_mods = join(tdir, 'X', 'Modules')
            no_modules_mtpl = join(tdir, 'X', 'NoMods', 'ignored.mtpl')
            nomap_mtpl = join(base_mods, 'NOMAP', 'n.mtpl')
            no_mconfig_mtpl = join(base_mods, 'NO_MCONFIG', 'a.mtpl')
            no_ip_mtpl = join(base_mods, 'NO_IP', 'b.mtpl')
            no_por_mtpl = join(base_mods, 'NO_POR', 'c.mtpl')
            default_por_mtpl = join(base_mods, 'DEFAULT_POR', 'd.mtpl')

            for mtpl in [no_modules_mtpl, nomap_mtpl, no_mconfig_mtpl, no_ip_mtpl, no_por_mtpl, default_por_mtpl]:
                File(mtpl).touch('dummy', mkdir=True, newfile=True)

            File(join(base_mods, 'NO_IP', 'module.mconfig')).touch('<PORRoot PATH="C:/X" REV="R" PATCH="P" BOMGROUP="ENV_BOM"/>', newfile=True)
            File(join(base_mods, 'NO_POR', 'module.mconfig')).touch('<IPName>IP_NO_POR</IPName>\n<PORRoot PATH="C:/X" REV="R"/>', newfile=True)
            File(join(base_mods, 'DEFAULT_POR', 'module.mconfig')).touch(
                '<IPName>IP_DEF</IPName>\n'
                '<PORRoot PATH="C:/POR_FIRST" REV="R1" PATCH="P1" BOMGROUP="NO_MATCH"/>\n'
                '<PORRoot PATH="C:/POR_SECOND" REV="R2" PATCH="P2" BOMGROUP="NO_MATCH2"/>\n',
                newfile=True
            )

            tpobj = self._new_mock_tpobj(envdir=envdir)
            tpobj.get_all_mtpl_from_stpl.return_value = [
                no_modules_mtpl,
                nomap_mtpl,
                no_mconfig_mtpl,
                no_ip_mtpl,
                no_por_mtpl,
                default_por_mtpl,
            ]
            tpobj.mtpl.get_modfolder2mod.return_value = {
                'NO_MCONFIG': 'M_NO_MCONFIG',
                'NO_IP': 'M_NO_IP',
                'NO_POR': 'M_NO_POR',
                'DEFAULT_POR': 'M_DEFAULT_POR',
            }

            obj = HermesPlistChk(tpobj)
            modinfo = obj._build_modinfo()

            self.assertEqual(set(modinfo.keys()), {'M_DEFAULT_POR'})
            self.assertEqual(modinfo['M_DEFAULT_POR']['ipname'], 'IP_DEF')
            self.assertEqual(modinfo['M_DEFAULT_POR']['plb_path'], 'C:/POR_FIRST/R1/P1/plb')

    def test_build_modinfo_target_mods_filter_skips_non_target_module(self):
        # Validate _build_modinfo skips modules not present in target_mods
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'ENV_TARGET')
            File(join(envdir, 'dummy.txt')).touch('', mkdir=True, newfile=True)

            mod_folder = join(tdir, 'X', 'Modules', 'FILTERME')
            mtpl_file = join(mod_folder, 'Flow.mtpl')
            mconfig_file = join(mod_folder, 'module.mconfig')

            File(mtpl_file).touch('dummy', mkdir=True, newfile=True)
            File(mconfig_file).touch(
                '<IPName>IP_FILTER</IPName>\n'
                '<PORRoot PATH="C:/PORF" REV="R1" PATCH="P1" BOMGROUP="ENV_TARGET"/>\n',
                newfile=True
            )

            tpobj = self._new_mock_tpobj(envdir=envdir)
            tpobj.get_all_mtpl_from_stpl.return_value = [mtpl_file]
            tpobj.mtpl.get_modfolder2mod.return_value = {'FILTERME': 'MOD_FILTER'}

            obj = HermesPlistChk(tpobj)
            modinfo = obj._build_modinfo(target_mods={'OTHER_MOD'})
            self.assertEqual(modinfo, {})

    def test_find_master_in_plists_missing_files_returns_none(self):
        # Validate scan fallback when files are missing or declaration is absent
        with TempDir(name=True, chdir=True) as tdir:
            plb_dir = join(tdir, 'plb')
            existing_file = join(plb_dir, 'exists.plist')
            File(existing_file).touch('PList another_master {\n}\n', mkdir=True, newfile=True)

            obj = HermesPlistChk(self._new_mock_tpobj())
            result = obj._find_master_in_plists(
                'target_master',
                {'plb_path': plb_dir, 'plist_names': {'missing.plist', 'exists.plist'}},
                {'target_master': join(plb_dir, 'different_name.plist')}
            )
            self.assertIsNone(result)

    def test_find_master_in_plists_returns_normalized_fallback_when_rev_map_misses(self):
        # Validate fallback path is normalized when rev map does not contain plist filename
        obj = HermesPlistChk(self._new_mock_tpobj())
        obj._get_rev_plist_file_map = Mock(return_value={})

        fallback = r'C:\POR\Rev1\p0\plb\my_all.plist'
        result = obj._find_master_in_plists(
            'sample_master',
            {'plist_names': {'my_all.plist'}},
            {'sample_master': fallback}
        )

        self.assertEqual(result, 'C:/POR/Rev1/p0/plb/my_all.plist')

    def test_get_rev_plist_file_map_caches_and_dedups_names(self):
        # Validate rev plist map cache-hit path and duplicate basename dedup behavior
        with TempDir(name=True, chdir=True) as tdir:
            rev1 = join(tdir, 'rev1', 'plb')
            rev2 = join(tdir, 'rev2', 'plb')
            f1 = join(rev1, 'dup.plist')
            f2 = join(rev2, 'dup.plist')
            File(f1).touch('PList a {\n}\n', mkdir=True, newfile=True)
            File(f2).touch('PList b {\n}\n', mkdir=True, newfile=True)

            tpobj = self._new_mock_tpobj()
            tpobj.plists.get_rev_paths.return_value = [rev1, rev2]
            obj = HermesPlistChk(tpobj)

            built = obj._get_rev_plist_file_map()
            self.assertIn('dup.plist', built)
            self.assertEqual(built['dup.plist'], obj._normalize_path(f1))

            obj._rev_plist_file_map = {'cached.plist': '/cached/path/cached.plist'}
            cached = obj._get_rev_plist_file_map()
            self.assertEqual(cached, {'cached.plist': '/cached/path/cached.plist'})

    def test_parse_master_block_sections_uses_plists_helpers(self):
        # Validate master block checks now use tpobj.plists helpers
        tpobj = self._new_mock_tpobj()
        obj = HermesPlistChk(tpobj)

        tpobj.plists.get_refplist.return_value = {
            'm_master': ['alpha_short__0', 'pth_cdie_dts_tempread_list', 'alpha_long__1']
        }
        tpobj.plists.get_plist_dependent.return_value = {'x.plist': set()}
        obj.refplist_map = tpobj.plists.get_refplist.return_value
        obj.plist_dep_map = tpobj.plists.get_plist_dependent.return_value

        found, refs, lines_0, lines_1, refs_0, refs_1 = obj._parse_master_block_sections('/tmp/x.plist', 'm_master')
        self.assertTrue(found)
        self.assertEqual(refs, ['alpha_short__0', 'pth_cdie_dts_tempread_list', 'alpha_long__1'])
        self.assertEqual(refs_0, ['alpha_short__0'])
        self.assertEqual(refs_1, ['alpha_long__1'])
        self.assertEqual(lines_0, [])
        self.assertEqual(lines_1, [])

    def test_parse_plist_block_pat_lines_uses_get_pats_from_plb(self):
        # Validate Pat retrieval uses get_pats_from_plb(order=True)
        tpobj = self._new_mock_tpobj()
        obj = HermesPlistChk(tpobj)

        tpobj.plists.get_pats_from_plb.return_value = ['pat_a', 'pat_b']
        found, pats = obj._parse_plist_block_pat_lines('alpha_short__0')
        self.assertTrue(found)
        self.assertEqual(pats, ['pat_a', 'pat_b'])

        tpobj.plists.get_pats_from_plb.side_effect = Exception('missing plist')
        found_missing, pats_missing = obj._parse_plist_block_pat_lines('missing_block')
        self.assertFalse(found_missing)
        self.assertEqual(pats_missing, [])

    def test_get_plist_names_from_ipxml_secondary_extension(self):
        # Validate .plist.ipxml candidate path is parsed when .plist.xml is absent
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'ENV2')
            File(join(envdir, 'dummy.txt')).touch('', mkdir=True, newfile=True)
            tpobj = self._new_mock_tpobj(envdir=envdir)
            obj = HermesPlistChk(tpobj)

            ipxml = join(envdir, 'PLIST_ALL_IPZ.plist.ipxml')
            File(ipxml).touch('<Root><PListFile name="z_one.plist"/></Root>', newfile=True)
            self.assertEqual(obj._get_plist_names_from_ipxml('IPZ'), {'z_one.plist'})

    def test_get_plist_names_from_ipxml_first_candidate_empty_fallback_then_second(self):
        # Validate first candidate parse exception with no regex names falls through to second candidate
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'ENV3')
            File(join(envdir, 'dummy.txt')).touch('', mkdir=True, newfile=True)
            tpobj = self._new_mock_tpobj(envdir=envdir)
            obj = HermesPlistChk(tpobj)

            xml1 = join(envdir, 'PLIST_ALL_IPW.plist.xml')
            xml2 = join(envdir, 'PLIST_ALL_IPW.plist.ipxml')
            File(xml1).touch('<Root><BROKEN></Root>', newfile=True)
            File(xml2).touch('<Root><PListFile name="w_one.plist"/></Root>', newfile=True)

            self.assertEqual(obj._get_plist_names_from_ipxml('IPW'), {'w_one.plist'})

    def test_parse_master_block_sections_missing_master(self):
        # Validate missing-master case with plist helper routines
        tpobj = self._new_mock_tpobj()
        obj = HermesPlistChk(tpobj)

        tpobj.plists.get_refplist.return_value = {}
        tpobj.plists.get_plist_dependent.return_value = {'x.plist': set()}
        obj.refplist_map = tpobj.plists.get_refplist.return_value
        obj.plist_dep_map = tpobj.plists.get_plist_dependent.return_value

        found, refs, lines_0, lines_1, refs_0, refs_1 = obj._parse_master_block_sections('/tmp/x.plist', 'absent_master')
        self.assertFalse(found)
        self.assertEqual(refs, [])
        self.assertEqual(lines_0, [])
        self.assertEqual(lines_1, [])
        self.assertEqual(refs_0, [])
        self.assertEqual(refs_1, [])

    def test_main_speedflow_and_nonspeedflow_exemption_paths(self):
        # Validate 372/373 template and test-name exemptions in main
        tpobj = self._new_mock_tpobj()
        flows = [
            ('M1', 'AAA_VMIN_BB_F1XCC_DD', {'TEMPLATE': 'CtvTokensTC', 'patlist': 'abc_nomaster'}, {}),
            ('M2', 'AAA_VMIN_BB_F1XCC_FFSEARCH', {'TEMPLATE': 'OtherTC', 'patlist': 'abc_nomaster'}, {}),
            ('M3', 'NOT_SPEED_FFSEARCH', {'TEMPLATE': 'OtherTC', 'patlist': 'abc_master'}, {}),
            ('M4', 'NOT_SPEED_RAW', {'TEMPLATE': 'OtherTC', 'patlist': 'abc_master'}, {}),
            ('M5', 'NOT_SPEED', {'TEMPLATE': 'DDGShmooTC', 'patlist': 'abc_master'}, {}),
            ('M6', 'NOT_SPEED', {'TEMPLATE': 'OtherTC', 'patlist': 'abc_nomaster'}, {}),
            ('M7', 'NOT_SPEED', {'TEMPLATE': 'OtherTC', 'patlist': 'abc_master'}, {}),
            ('M8', 'SKIP_PATLIST', {'TEMPLATE': 'OtherTC'}, {}),
            ('M9', 'AAA_APEX_BB_F5XCC_DD', {'TEMPLATE': 'ApexTC', 'patlist': 'apex_nomaster'}, {}),
            ('M10', 'AAA_APEX_BB_F5XCC_DD', {'TEMPLATE': 'ApexTC', 'patlist': 'apex_master'}, {}),
        ]

        # Ensure iter_flows emits our custom rows
        tpobj.mtpl.iter_flows.return_value = flows
        obj = HermesPlistChk(tpobj)
        obj._build_modinfo = Mock(return_value={})
        obj.main()

        expect = '\n'.join([
            '377 M2 AAA_VMIN_BB_F1XCC_FFSEARCH matches speedflow regex and must use TEMPLATE in [\'ApexTC\', \'CtvTokensTC\', \'DDGShmooTC\', \'VminTC\'], but found "OtherTC"',
            '373 M7 NOT_SPEED does not match speedflow regex but Patlist "abc_master" ends with _master',
            '373 M10 AAA_APEX_BB_F5XCC_DD uses TEMPLATE "ApexTC" and Patlist "apex_master" must not end with _master',
            "(372, 'M1'): 1",
            "(372, 'M2'): 1",
            "(372, 'M9'): 1",
            "(373, 'M6'): 1",
            "(377, 'M1'): 1",
            '',
        ])
        self.assertTextEqual(obj.ut_result(), expect)

    def test_main_master_resolution_and_365_paths(self):
        # Validate deep main branches: 376/374/375 and duplicate-master skip
        tpobj = self._new_mock_tpobj()
        HermesPlistChk.DISABLE_DEEP_PAT_365 = False

        flows = [
            ('A', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mA_f1x_master'}, {}),
            ('A', 'X_VMIN_Y_F1X_Z_DUP', {'TEMPLATE': 'VminTC', 'patlist': 'mA_f1x_master'}, {}),
            ('B', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mB_f1x_master'}, {}),
            ('C', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mC_f1x_master'}, {}),
            ('D', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mD_f1x_master'}, {}),
            ('E', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mE_f1x_master'}, {}),
            ('F', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mF_f1x_master'}, {}),
            ('G', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mG_f1x_master'}, {}),
            ('H', 'X_VMIN_Y_F1X_Z', {'TEMPLATE': 'VminTC', 'patlist': 'mH_f1x_master'}, {}),
        ]
        tpobj.mtpl.iter_flows.return_value = flows

        obj = HermesPlistChk(tpobj)

        obj._build_modinfo = Mock(return_value={
            'A': {'ipname': 'IPA', 'plb_path': '/plb', 'plist_names': {'a.plist'}},
            'C': {'ipname': 'IPC', 'plb_path': '/plb', 'plist_names': {'c.plist'}},
            'D': {'ipname': 'IPD', 'plb_path': '/plb', 'plist_names': {'d.plist'}},
            'E': {'ipname': 'IPE', 'plb_path': '/plb', 'plist_names': {'e.plist'}},
            'F': {'ipname': 'IPF', 'plb_path': '/plb', 'plist_names': {'f.plist'}},
            'G': {'ipname': 'IPG', 'plb_path': '/plb', 'plist_names': {'g.plist'}},
            'H': {'ipname': 'IPH', 'plb_path': '/plb', 'plist_names': {'h.plist'}},
        })

        def fake_find(master_plist, modinfo, plb_map):
            # Simulate lookup failure for module C only
            if master_plist == 'mC_f1x_master':
                return None
            return '/plb/found.plist'

        def fake_parse_master(master_file, master_plist):
            # Simulate parse failure for module D
            if master_plist == 'mD_f1x_master':
                return False, [], [], [], [], []
            # Simulate invalid ref for E
            if master_plist == 'mE_f1x_master':
                return True, ['bad_ref_only'], [], [], [], []
            # Simulate inline/order mismatch for F
            if master_plist == 'mF_f1x_master':
                return True, ['r1_f1x__0', 'r1_f1x__1'], ['line_x'], ['line_y'], ['r1_f1x__0'], ['r1_f1x__1']
            # Simulate deep parser missing block for G
            if master_plist == 'mG_f1x_master':
                return True, ['g1_f1x__0', 'g1_f1x__1'], [], [], ['g1_f1x__0'], ['g1_f1x__1']
            # Simulate deep parser Pat mismatch for H
            if master_plist == 'mH_f1x_master':
                return True, ['h1_f1x__0', 'h1_f1x__1'], [], [], ['h1_f1x__0'], ['h1_f1x__1']
            # Success path for A
            return True, ['a1_f1x__0', 'a1_f1x__1'], [], [], ['a1_f1x__0'], ['a1_f1x__1']

        def fake_parse_pat(plist_name):
            # Missing block case for G
            if plist_name in ('g1_f1x__0', 'g1_f1x__1'):
                if plist_name == 'g1_f1x__0':
                    return False, []
                return True, ['x']
            # Pat mismatch for H
            if plist_name == 'h1_f1x__0':
                return True, ['p0']
            if plist_name == 'h1_f1x__1':
                return True, ['p1']
            # All others equal
            return True, ['ok_pat']

        obj._find_master_in_plists = Mock(side_effect=fake_find)
        obj._parse_master_block_sections = Mock(side_effect=fake_parse_master)
        obj._parse_plist_block_pat_lines = Mock(side_effect=fake_parse_pat)

        obj.main()

        result = obj.ut_result()
        self.assertIn('376 B X_VMIN_Y_F1X_Z cannot validate mB_f1x_master: module.mconfig IP/PORRoot info not found', result)
        self.assertIn('376 C X_VMIN_Y_F1X_Z cannot find mC_f1x_master in /plb for PLIST_ALL_IPC.plist.xml', result)
        self.assertIn('376 D X_VMIN_Y_F1X_Z cannot parse master plist block mD_f1x_master in /plb/found.plist', result)
        self.assertIn('374 E ', result)
        self.assertIn('375 F ', result)
        self.assertIn('375 G ', result)
        self.assertIn('cannot locate referenced RefPList block(s)', result)
        self.assertIn('375 H ', result)
        self.assertIn('Pat contents/order mismatch between', result)

    def test_main_speedflow_template_and_362_error_paths(self):
        # Validate speedflow template-policy error (377) and non-exempt master requirement error (372)
        tpobj = self._new_mock_tpobj()
        flows = [
            ('S1', 'ABC_VMIN_XX_F1XABC_DEF', {'TEMPLATE': 'NotAllowedTC', 'patlist': 'abc_nomaster'}, {}),
            ('S2', 'ABC_APEX_XX_F1XABC_DEF', {'TEMPLATE': 'ApexTC', 'patlist': 'apex_nonmaster'}, {}),
            ('S3', 'ABC_APEX_XX_F1XABC_DEF', {'TEMPLATE': 'ApexTC', 'patlist': 'apex_master'}, {}),
        ]

        tpobj.mtpl.iter_flows.return_value = flows
        obj = HermesPlistChk(tpobj)
        obj._build_modinfo = Mock(return_value={})

        obj.main()

        result = obj.ut_result()
        self.assertIn('377 S1 ABC_VMIN_XX_F1XABC_DEF matches speedflow regex and must use TEMPLATE in [\'ApexTC\', \'CtvTokensTC\', \'DDGShmooTC\', \'VminTC\'], but found "NotAllowedTC"', result)
        self.assertIn('372 S1 ABC_VMIN_XX_F1XABC_DEF matches speedflow regex but Patlist "abc_nomaster" does not end with _master', result)
        self.assertIn('373 S3 ABC_APEX_XX_F1XABC_DEF uses TEMPLATE "ApexTC" and Patlist "apex_master" must not end with _master', result)
        self.assertIn("(372, 'S2'): 1", result)

    @unittest.skipIf(not exists(join(UT_DIR_REPO, 'Simple7', 'POR_TP', 'TGLH81', 'EnvironmentFile.env')),
                     'Simple7 test program is required for this integration-like unittest')
    def test_tempdir_testprogram_pass_and_fail(self):
        # Use TempDir + TestProgram and mock flows to validate pass/fail behavior in one run
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True):
            tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            flows = [
                ('MOD_PASS', 'AAA_VMIN_BB_F1XCC_DD', {'TEMPLATE': 'VminTC', 'patlist': 'mod_pass_f1xcc_master'}, {}),
                ('MOD_FAIL', 'NOT_SPEED_TEST', {'TEMPLATE': 'OtherTC', 'patlist': 'mod_fail_master'}, {}),
            ]

            obj = HermesPlistChk(tpobj)
            obj._build_modinfo = Mock(return_value={
                'MOD_PASS': {'ipname': 'IPP', 'plb_path': '/plb', 'plist_names': {'x.plist'}},
            })
            obj._find_master_in_plists = Mock(return_value='/plb/x.plist')
            obj._parse_master_block_sections = Mock(return_value=(True, ['p0_f1xcc__0', 'p0_f1xcc__1'], [], [], ['p0_f1xcc__0'], ['p0_f1xcc__1']))
            obj._parse_plist_block_pat_lines = Mock(return_value=(True, ['samepat']))

            with MockVar(tpobj.mtpl, 'iter_flows', Mock(return_value=flows)):
                obj.main()

            expect = '''
373 MOD_FAIL NOT_SPEED_TEST does not match speedflow regex but Patlist "mod_fail_master" ends with _master
(372, 'MOD_PASS'): 1
(374, 'MOD_PASS'): 2
(375, 'MOD_PASS'): 1
(376, 'MOD_PASS'): 3
(377, 'MOD_PASS'): 1
'''
            self.assertTextEqual(obj.ut_result(), expect)

    def test_main_365_error_when_fn_does_not_match_plist_names(self):
        # Validate 375 reports both token mismatch and order mismatch without short-circuiting
        tpobj = self._new_mock_tpobj()
        flows = [
            ('FN_MISMATCH', 'AAA_VMIN_BB_F2XCC_DD', {'TEMPLATE': 'VminTC', 'patlist': 'mod_f1_master'}, {}),
        ]
        tpobj.mtpl.iter_flows.return_value = flows

        obj = HermesPlistChk(tpobj)
        obj._build_modinfo = Mock(return_value={
            'FN_MISMATCH': {'ipname': 'IPM', 'plb_path': '/plb', 'plist_names': {'x.plist'}},
        })
        obj._find_master_in_plists = Mock(return_value='/plb/x.plist')
        obj._parse_master_block_sections = Mock(return_value=(
            True,
            ['refa_f1__0', 'refb_f1__1'],
            [],
            [],
            ['refa_f1__0'],
            ['refb_f1__1']
        ))

        obj.main()

        result = obj.ut_result()
        errs_365 = [line for line in result.splitlines() if line.startswith('375 FN_MISMATCH ')]
        self.assertTrue(any('token=F2XCC' in msg for msg in errs_365))
        self.assertTrue(any('RefPList __0 and __1 contents/order mismatch' in msg for msg in errs_365))
        self.assertEqual(len(errs_365), 2)

    def test_main_365_token_mismatch_skips_pass_when_ref_order_is_ok(self):
        # Validate 375 token mismatch keeps has_365_error and skips add_pass on aligned __0/__1 refs
        tpobj = self._new_mock_tpobj()
        flows = [
            ('TOKEN_ONLY', 'AAA_VMIN_BB_F2XCC_DD', {'TEMPLATE': 'VminTC', 'patlist': 'mod_f1_master'}, {}),
        ]
        tpobj.mtpl.iter_flows.return_value = flows

        obj = HermesPlistChk(tpobj)
        obj._build_modinfo = Mock(return_value={
            'TOKEN_ONLY': {'ipname': 'IPM', 'plb_path': '/plb', 'plist_names': {'x.plist'}},
        })
        obj._find_master_in_plists = Mock(return_value='/plb/x.plist')
        obj._parse_master_block_sections = Mock(return_value=(
            True,
            ['shared_f1__0', 'shared_f1__1'],
            [],
            [],
            ['shared_f1__0'],
            ['shared_f1__1']
        ))

        obj.main()

        result = obj.ut_result()
        errs_365 = [line for line in result.splitlines() if line.startswith('375 TOKEN_ONLY ')]
        self.assertEqual(len(errs_365), 1)
        self.assertIn('token=F2XCC', errs_365[0])
        self.assertNotIn("(375, 'TOKEN_ONLY')", result)

    def test_main_364_skips_preexec_refplist_entries(self):
        # Validate QGate374 ignores PreExecRefPList entries when checking non __0/__1 RefPList names
        tpobj = self._new_mock_tpobj()
        flows = [
            ('PREEXEC_OK', 'AAA_VMIN_BB_F2XAT_DD', {'TEMPLATE': 'VminTC', 'patlist': 'preexec_master'}, {}),
        ]
        tpobj.mtpl.iter_flows.return_value = flows

        obj = HermesPlistChk(tpobj)
        obj._build_modinfo = Mock(return_value={
            'PREEXEC_OK': {'ipname': 'IPP', 'plb_path': '/plb', 'plist_names': {'x.plist'}},
        })
        obj._find_master_in_plists = Mock(return_value='/plb/x.plist')
        obj._parse_master_block_sections = Mock(return_value=(
            True,
            ['scn_arw_preplist_hptp1600_12r4t_atspeed_occ_classhvm_list', 'r2_f2xat__0', 'r2_f2xat__1'],
            [],
            [],
            ['r2_f2xat__0'],
            ['r2_f2xat__1']
        ))
        obj._get_preexec_refplist_names = Mock(return_value={'scn_arw_preplist_hptp1600_12r4t_atspeed_occ_classhvm_list'})

        obj.main()

        result = obj.ut_result()
        self.assertNotIn('374 PREEXEC_OK ', result)
        self.assertNotIn('has non __0/__1 RefPList under _master', result)

    def test_get_preexec_refplist_names_from_plists_structures(self):
        # Validate PreExecRefPList extraction uses tpobj.plists parsed structures
        tpobj = self._new_mock_tpobj()
        obj = HermesPlistChk(tpobj)

        tpobj.plists._plb2n = {'target_master': 10, 'single_line_master': 11}
        tpobj.plists._plbattr = {
            10: {'PreExecRefPList': 'preexec_a'},
            11: {},
        }

        preexec_refs = obj._get_preexec_refplist_names('unused.plist', 'target_master')
        self.assertEqual(preexec_refs, {'preexec_a'})

        single_line_refs = obj._get_preexec_refplist_names('unused.plist', 'single_line_master')
        self.assertEqual(single_line_refs, set())

        missing_master_refs = obj._get_preexec_refplist_names('unused.plist', 'missing_master')
        self.assertEqual(missing_master_refs, set())

    def test_get_preexec_refplist_names_missing_data_returns_empty(self):
        # Validate empty/missing plists internals safely return empty preexec ref set
        tpobj = self._new_mock_tpobj()
        obj = HermesPlistChk(tpobj)

        tpobj.plists._plb2n = {}
        tpobj.plists._plbattr = {}
        self.assertEqual(obj._get_preexec_refplist_names('any.plist', 'any_master'), set())

    def test_get_preexec_refplist_names_collection_value(self):
        # Validate iterable PreExecRefPList values are converted to a string set
        tpobj = self._new_mock_tpobj()
        obj = HermesPlistChk(tpobj)

        tpobj.plists._plb2n = {'master_a': 7}
        tpobj.plists._plbattr = {
            7: {'PreExecRefPList': ['pre_a', '', 'pre_b']},
        }

        self.assertEqual(obj._get_preexec_refplist_names('unused.plist', 'master_a'), {'pre_a', 'pre_b'})

    def test_get_preexec_refplist_names_fallback_from_master_file(self):
        # Validate fallback parsing of PreExecRefPList lines from master plist block text
        with TempDir(name=True, chdir=True) as tdir:
            master_file = join(tdir, 'm_all.plist')
            File(master_file).touch(
                'PList my_master {\n'
                '  PreExecRefPList pre_a;\n'
                '  RefPList child__0;\n'
                '  PreExecRefPList pre_b;\n'
                '}\n',
                mkdir=True,
                newfile=True
            )

            tpobj = self._new_mock_tpobj()
            obj = HermesPlistChk(tpobj)
            tpobj.plists._plb2n = {'my_master': 10}
            tpobj.plists._plbattr = {10: {}}

            refs = obj._get_preexec_refplist_names(master_file, 'my_master')
            self.assertEqual(refs, {'pre_a', 'pre_b'})

    def test_get_preexec_refplist_names_fallback_skips_lines_before_master_block(self):
        # Validate fallback parser skips non-matching lines before entering target master block
        with TempDir(name=True, chdir=True) as tdir:
            master_file = join(tdir, 'm_all2.plist')
            File(master_file).touch(
                'PList other_master {\n'
                '  PreExecRefPList other_pre;\n'
                '}\n'
                'PList target_master {\n'
                '  PreExecRefPList target_pre;\n'
                '}\n',
                mkdir=True,
                newfile=True
            )

            tpobj = self._new_mock_tpobj()
            obj = HermesPlistChk(tpobj)
            tpobj.plists._plb2n = {'target_master': 11}
            tpobj.plists._plbattr = {11: {}}

            refs = obj._get_preexec_refplist_names(master_file, 'target_master')
            self.assertEqual(refs, {'target_pre'})

    def test_get_preexec_refplist_names_fallback_returns_empty_when_target_block_missing(self):
        # Validate fallback parser returns empty set when target master block declaration does not exist
        with TempDir(name=True, chdir=True) as tdir:
            master_file = join(tdir, 'm_all3.plist')
            File(master_file).touch(
                'PList other_master {\n'
                '  PreExecRefPList other_pre;\n'
                '}\n',
                mkdir=True,
                newfile=True
            )

            tpobj = self._new_mock_tpobj()
            obj = HermesPlistChk(tpobj)
            tpobj.plists._plb2n = {'target_master': 12}
            tpobj.plists._plbattr = {12: {}}

            refs = obj._get_preexec_refplist_names(master_file, 'target_master')
            self.assertEqual(refs, set())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
