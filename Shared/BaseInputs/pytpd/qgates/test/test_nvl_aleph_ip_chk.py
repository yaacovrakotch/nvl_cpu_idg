#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""Run unittest for nvl_aleph_ip_chk.py."""
import sys
import re
from os.path import join

try:
    from setenv_unittest import ROOT_ENV
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import ROOT_ENV

from gadget.files import TempDir, File
from gadget.ut import TestCase, unittest
import qgates.nvl_aleph_ip_chk as aleph_mod
from qgates.nvl_aleph_ip_chk import AlephIpChk


class _DummyEnv:
    def __init__(self):
        self._vals = {}

    def get_env_dict(self):
        return dict(self._vals)

    def get_contents(self, key, islist=False):
        val = self._vals[key]
        if islist:
            return list(val)
        return val


class _DummyMtpl:
    def __init__(self):
        self._modfolder2mod = {}
        self._flows = []

    def get_modfolder2mod(self):
        return dict(self._modfolder2mod)

    def iter_flows(self, *args, **kwargs):
        for row in self._flows:
            yield row


class _DummyPlists:
    def __init__(self):
        self._plist_list = []
        self._plb_map = {}

    def get_plist_list(self):
        return list(self._plist_list)

    def get_plb_map(self):
        return dict(self._plb_map)


class _DummyTp:
    def __init__(self, envdir):
        self.envdir = envdir
        self.envfile = join(envdir, 'EnvironmentFile.env')
        self.env = _DummyEnv()
        self.mtpl = _DummyMtpl()
        self.plists = _DummyPlists()
        self._mtpls = []

    def get_all_mtpl_from_stpl(self):
        return list(self._mtpls)


class TestNvlAlephIpChk(TestCase):

    def setUp(self):
        # Preserve class/module switches used by branch tests
        self._orig_fallback = AlephIpChk.FALLBACK_TO_GLOBAL_PATTERNS
        self._orig_max_errors = aleph_mod._MAX_ERRORS_PER_ALEPH

    def tearDown(self):
        # Restore switches after each test
        AlephIpChk.FALLBACK_TO_GLOBAL_PATTERNS = self._orig_fallback
        aleph_mod._MAX_ERRORS_PER_ALEPH = self._orig_max_errors

    def test_ip_helper_methods(self):
        # Test IP normalization and env-variable based classifiers
        self.assertEqual(AlephIpChk._normalize_ip('ipc'), 'IPC')
        self.assertEqual(AlephIpChk._normalize_ip('ipg'), 'IPG')
        self.assertEqual(AlephIpChk._normalize_ip('misc'), 'PKG')

        self.assertEqual(AlephIpChk._ip_from_fuse_varname('FUSE_ROOT_DIR_HUB'), 'IPH')
        self.assertEqual(AlephIpChk._ip_from_fuse_varname('FUSE_ROOT_DIR_GCD'), 'IPG')
        self.assertEqual(AlephIpChk._ip_from_fuse_varname('FUSE_ROOT_DIR_PCDABC'), 'IPP')
        self.assertEqual(AlephIpChk._ip_from_fuse_varname('FUSE_ROOT_DIR_CPU'), 'IPC')
        self.assertEqual(AlephIpChk._ip_from_fuse_varname('FUSE_ROOT_DIR_ANY'), 'PKG')
        self.assertIsNone(AlephIpChk._ip_from_fuse_varname('OTHER_VAR'))

        self.assertEqual(AlephIpChk._ip_from_patmodify_varname('MG_PATMODIFY_PATH'), 'IPG')
        self.assertEqual(AlephIpChk._ip_from_patmodify_varname('_MH_PATMODIFY_PATH'), 'IPH')
        self.assertEqual(AlephIpChk._ip_from_patmodify_varname('MN_PATMODIFY_PATH'), 'PKG')
        self.assertIsNone(AlephIpChk._ip_from_patmodify_varname('PATMODIFY_PATH_ONLY'))

        self.assertEqual(AlephIpChk._ip_from_clk_varname('CLK_PLL_G'), 'IPG')
        self.assertEqual(AlephIpChk._ip_from_clk_varname('CLK_PLL_C'), 'IPC')
        self.assertEqual(AlephIpChk._ip_from_clk_varname('CLK_PLL_H'), 'IPH')
        self.assertEqual(AlephIpChk._ip_from_clk_varname('CLK_PLL_P'), 'IPP')
        self.assertIsNone(AlephIpChk._ip_from_clk_varname('ABC_CLK_NO_SUFFIX'))

    def test_get_aleph_match_fields_json_and_fallback(self):
        # Test PatternsRegEx extraction from valid JSON and malformed fallback text
        with TempDir(name=True, chdir=True) as tdir:
            good = join(tdir, 'good.json')
            bad = join(tdir, 'bad.json')
            not_json = join(tdir, 'x.txt')

            File(good).touch('{"Configurations":[{"PatternsRegEx":["a.*","b.*"]}]}')
            File(bad).touch('{"Configurations":[{"PatternsRegEx":["g.*_longreset_hptp.*"]},]}')
            File(not_json).touch('anything')

            got_good = AlephIpChk._get_aleph_match_fields(good)
            got_bad = AlephIpChk._get_aleph_match_fields(bad)
            got_not_json = AlephIpChk._get_aleph_match_fields(not_json)

            self.assertIn('a.*', got_good['PatternsRegEx'])
            self.assertIn('b.*', got_good['PatternsRegEx'])
            self.assertIn('g.*_longreset_hptp.*', got_bad['PatternsRegEx'])
            self.assertEqual(got_not_json, {'PatternsRegEx': set()})

    def test_build_prefix_and_classify_path(self):
        # Test prefix map creation and aleph path classification precedence
        with TempDir(name=True, chdir=True) as tdir:
            tp = _DummyTp(tdir)
            tp.env._vals = {
                'FUSE_ROOT_DIR_GCD': 'C:/ROOT/GCD',
                'MG_PATMODIFY_PATH': 'C:/PATMOD/G',
                'CLK_PLL_H': 'C:/CLK/H',
            }
            obj = AlephIpChk(tp)

            prefix_ip = obj._build_prefix_ip_map()
            self.assertEqual(prefix_ip['C:/ROOT/GCD'], 'IPG')
            self.assertEqual(prefix_ip['C:/PATMOD/G'], 'IPG')
            self.assertEqual(prefix_ip['C:/CLK/H'], 'IPH')

            mod_ip = {'MIO_HPTP_HXX': 'IPH'}
            self.assertEqual(obj._classify_aleph_path('C:/ROOT/GCD/a.json', prefix_ip, mod_ip), 'IPG')
            self.assertEqual(obj._classify_aleph_path('C:/x/Common/a.json', {}, mod_ip), 'PKG')
            self.assertEqual(obj._classify_aleph_path('C:/x/Modules/MIO_HPTP_HXX/AlephFiles/a.json', {}, mod_ip), 'IPH')
            self.assertEqual(obj._classify_aleph_path('C:/x/unknown/a.json', {}, mod_ip), 'PKG')

    def test_build_prefix_module_and_modfolder_map_edge_branches(self):
        # Test helper edge branches with fail-fast env read and modfolder IP map
        with TempDir(name=True, chdir=True) as tdir:
            tp = _DummyTp(tdir)
            tp.env._vals = {
                'UNRELATED_VAR': 'C:/UNUSED',
                'FUSE_ROOT_DIR_GCD': 'C:/ROOT/G1; ;C:/ROOT/G2',
                'CLK_PLL_H': 'C:/CLK/H',
                'FUSE_ROOT_DIR_CPU': 'C:/CPU',
            }

            def _get_contents(key, islist=False):
                if key == 'FUSE_ROOT_DIR_CPU':
                    raise RuntimeError('forced failure')
                val = tp.env._vals[key]
                if islist:
                    return list(val)
                return val

            tp.env.get_contents = _get_contents

            mod1 = join(tdir, 'TPL', 'Modules', 'CATA', 'MOD_A')
            mtpl1 = join(mod1, 'f1.mtpl')
            cfg1 = join(mod1, 'a.mconfig')
            File(mtpl1).touch('x', mkdir=True, newfile=True)
            File(cfg1).touch('<Root><IPName>IPH</IPName></Root>', newfile=True)

            # Duplicate modfolder should be skipped by map builder
            mtpl1_dup = join(mod1, 'f1_dup.mtpl')
            File(mtpl1_dup).touch('x', newfile=True)

            # No mconfig branch
            mod2 = join(tdir, 'TPL', 'Modules', 'CATB', 'MOD_B')
            mtpl2 = join(mod2, 'f2.mtpl')
            File(mtpl2).touch('x', mkdir=True, newfile=True)

            # IPName missing -> PKG
            mod3 = join(tdir, 'TPL', 'Modules', 'CATC', 'MOD_C')
            mtpl3 = join(mod3, 'f3.mtpl')
            cfg3 = join(mod3, 'c.mconfig')
            File(mtpl3).touch('x', mkdir=True, newfile=True)
            File(cfg3).touch('<Root></Root>', newfile=True)

            tp._mtpls = [join(tdir, 'x', 'not_modules.mtpl'), mtpl1, mtpl1_dup, mtpl2, mtpl3]

            obj = AlephIpChk(tp)
            self.assertRaises(RuntimeError, obj._build_prefix_ip_map)

            tp.env.get_contents = lambda key, islist=False: list(tp.env._vals[key]) if islist else tp.env._vals[key]
            prefix_map = obj._build_prefix_ip_map()
            self.assertIn('C:/ROOT/G1', prefix_map)
            self.assertIn('C:/ROOT/G2', prefix_map)
            self.assertIn('C:/CPU', prefix_map)
            self.assertNotIn('C:/UNUSED', prefix_map)

            modfolder_ip = obj._build_modfolder_ip_map()
            self.assertEqual(modfolder_ip['MOD_A'], 'IPH')
            self.assertEqual(modfolder_ip['MOD_C'], 'PKG')
            self.assertNotIn('MOD_B', modfolder_ip)

            modfolder2mod = {'MOD_A': 'M_A'}
            self.assertEqual(obj._get_module_from_path('C:/x/Modules//CATA/MOD_A/Aleph/a.json', modfolder2mod), 'M_A')
            self.assertEqual(obj._get_module_from_path('C:/x/Modules/CATA/NO_MATCH/Aleph/a.json', modfolder2mod), 'BASE')
            self.assertEqual(obj._get_module_from_path('C:/x/no_modules/a.json', modfolder2mod), 'BASE')

            self.assertEqual(obj._classify_aleph_path('C:/x/Modules///UNKNOWN///a.json', {}, {}), 'PKG')

    def test_build_plist_pat_and_module_maps(self):
        # Test plist->IP map, pattern extraction, and module patlist scoping
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'Class_X')
            tp = _DummyTp(envdir)

            ipxml = join(envdir, 'PLIST_ALL_IPG.plist.xml')
            File(ipxml).touch('<Root><PListFile name="A.plist"/></Root>', mkdir=True, newfile=True)

            moddir = join(tdir, 'TPL', 'Modules', 'MIO_HPTP_HXX')
            mtpl = join(moddir, 'Flow.mtpl')
            mconfig = join(moddir, 'module.mconfig')
            File(mtpl).touch('dummy', mkdir=True, newfile=True)
            File(mconfig).touch(
                '<Root><IPName>IPH</IPName>'
                '<PORRoot BomGroup="CLASS_X"><PlistFile>A.plist</PlistFile></PORRoot>'
                '</Root>', newfile=True
            )

            tp._mtpls = [mtpl]
            tp.mtpl._modfolder2mod = {'MIO_HPTP_HXX': 'MIO_HPTP_HXX'}

            plist_a = join(tdir, 'plb', 'A.plist')
            File(plist_a).touch('Pat foo_match;\nPat bar_match;\n', mkdir=True, newfile=True)
            tp.plists._plist_list = [plist_a]
            tp.plists._plb_map = {'plb_hptp': plist_a}
            tp.mtpl._flows = [('MIO_HPTP_HXX', 'TN1', {'patlist': 'plb_hptp'})]

            obj = AlephIpChk(tp)

            plist_ip = obj._build_plist_ip_map()
            self.assertEqual(plist_ip['A.plist'], 'IPG')

            pat_ip = obj._build_pat_ip_map(plist_ip)
            self.assertEqual(pat_ip['foo_match'][0], 'IPG')
            self.assertEqual(pat_ip['foo_match'][1].replace('\\', '/').split('/')[-1], 'A.plist')

            mod_pat = obj._build_module_pat_map(pat_ip)
            self.assertIn('MIO_HPTP_HXX', mod_pat)
            names = {x[0] for x in mod_pat['MIO_HPTP_HXX']}
            self.assertIn('foo_match', names)
            self.assertIn('bar_match', names)

    def test_plist_pat_module_map_edge_branches(self):
        # Test plist/pattern/module map fallback and skip branches
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'CLASS_Y')
            tp = _DummyTp(envdir)

            # Source-1 filename not matching PLIST_ALL_<IP>.plist pattern
            bad_name = join(envdir, 'PLIST_ALL_IP.G.plist.xml')
            File(bad_name).touch('<Root><PListFile name="NOMATCH.plist"/></Root>', mkdir=True, newfile=True)

            # Source-1 malformed xml triggers regex fallback
            bad_xml = join(envdir, 'PLIST_ALL_IPH.plist.xml')
            File(bad_xml).touch('<Root><PListFile name="B.plist"/><PListFile name="B.plist"><Root>', newfile=True)

            good_dup = join(envdir, 'PLIST_ALL_IPG.plist.xml')
            File(good_dup).touch('<Root><PListFile name="G.plist"/><PListFile name="G.plist"/></Root>', newfile=True)

            mod1 = join(tdir, 'TPL', 'Modules', 'M1')
            mtpl1 = join(mod1, 'm1.mtpl')
            cfg1 = join(mod1, 'm1.mconfig')
            File(mtpl1).touch('x', mkdir=True, newfile=True)
            File(cfg1).touch(
                '<Root><IPName>IPG</IPName>'
                '<PORRoot BomGroup="CLASS_Z"><PlistFile>Z.plist</PlistFile></PORRoot>'
                '<PORRoot BomGroup="CLASS_Y"><PlistFile>Y.plist</PlistFile></PORRoot>'
                '</Root>', newfile=True
            )

            # Source-2 parse error branch
            mod2 = join(tdir, 'TPL', 'Modules', 'M2')
            mtpl2 = join(mod2, 'm2.mtpl')
            cfg2 = join(mod2, 'm2.mconfig')
            File(mtpl2).touch('x', mkdir=True, newfile=True)
            File(cfg2).touch('<Root><IPName>IPP</IPName>', newfile=True)

            # Source-2 selected is None (no PORRoot)
            mod3 = join(tdir, 'TPL', 'Modules', 'M3')
            mtpl3 = join(mod3, 'm3.mtpl')
            cfg3 = join(mod3, 'm3.mconfig')
            File(mtpl3).touch('x', mkdir=True, newfile=True)
            File(cfg3).touch('<Root><IPName>IPC</IPName></Root>', newfile=True)

            # Source-2 first PORRoot fallback branch
            mod5 = join(tdir, 'TPL', 'Modules', 'M5')
            mtpl5 = join(mod5, 'm5.mtpl')
            cfg5 = join(mod5, 'm5.mconfig')
            File(mtpl5).touch('x', mkdir=True, newfile=True)
            File(cfg5).touch(
                '<Root><IPName>IPH</IPName>'
                '<PORRoot BomGroup="OTHER"><PlistFile>FIRST.plist</PlistFile></PORRoot>'
                '<PORRoot BomGroup="ANOTHER"><PlistFile>SECOND.plist</PlistFile></PORRoot>'
                '</Root>', newfile=True
            )

            # Source-2 no mconfig
            mod4 = join(tdir, 'TPL', 'Modules', 'M4')
            mtpl4 = join(mod4, 'm4.mtpl')
            File(mtpl4).touch('x', mkdir=True, newfile=True)

            tp._mtpls = [join(tdir, 'no_modules.mtpl'), mtpl1, mtpl2, mtpl3, mtpl4, mtpl5]
            obj = AlephIpChk(tp)

            plist_ip = obj._build_plist_ip_map()
            self.assertEqual(plist_ip['B.plist'], 'IPH')
            self.assertEqual(plist_ip['G.plist'], 'IPG')
            self.assertEqual(plist_ip['Y.plist'], 'IPG')
            self.assertEqual(plist_ip['FIRST.plist'], 'IPH')
            self.assertNotIn('NOMATCH.plist', plist_ip)

            # _get_pats_from_plist_file now propagates missing-file errors
            self.assertRaises(FileNotFoundError, AlephIpChk._get_pats_from_plist_file, join(tdir, 'missing.plist'))

            # Duplicate basename and missing plist name branches in pat map
            dup1 = join(tdir, 'plb1', 'DUP.plist')
            dup2 = join(tdir, 'plb2', 'DUP.plist')
            xplist = join(tdir, 'plb3', 'X.plist')
            File(dup1).touch('Pat same_pat;\nPat only_first;\n', mkdir=True, newfile=True)
            File(dup2).touch('Pat should_not_use;\n', mkdir=True, newfile=True)
            File(xplist).touch('Comment\nPat \nPat same_pat;\nPat extra_pat;\n', mkdir=True, newfile=True)
            tp.plists._plist_list = [dup1, dup2, xplist]

            pat_ip_map = obj._build_pat_ip_map({'DUP.plist': 'IPG', 'X.plist': 'IPH', 'MISSING.plist': 'IPG'})
            self.assertEqual(pat_ip_map['same_pat'][0], 'IPG')
            self.assertIn('extra_pat', pat_ip_map)

            # Module pat-map skip branches: empty patlist, unknown plb, and empty module pattern list
            tp.plists._plb_map = {'known': xplist}
            tp.mtpl._flows = [('M1', 'T1', {'patlist': ''}),
                              ('M1', 'T2', {'patlist': 'unknown'}),
                              ('M2', 'T3', {'patlist': 'known'})]
            module_pat = obj._build_module_pat_map({'zzz': ('IPG', join(tdir, 'other.plist'))})
            self.assertEqual(module_pat, {})

            module_pat2 = obj._build_module_pat_map({'extra_pat': ('IPH', xplist)})
            self.assertIn('M2', module_pat2)

    def test_main_reports_ip_mismatch_and_path(self):
        # Test main() reports cross-IP pattern mismatch and includes context
        with TempDir(name=True, chdir=True) as tdir:
            tp = _DummyTp(tdir)
            tp.mtpl._modfolder2mod = {'MIO_HPTP_HXX': 'MIO_HPTP_HXX'}
            aleph = join(tdir, 'Modules', 'MIO_HPTP_HXX', 'AlephFiles', 'HPTP.patmod.json')
            File(aleph).touch('{"PatternsRegEx":["g.*_longreset_hptp.*"]}', mkdir=True, newfile=True)
            tp.env._vals = {'ALEPH_FILES': [aleph]}

            obj = AlephIpChk(tp)

            obj._build_plist_ip_map = lambda: {'dummy.plist': 'IPG'}
            obj._build_pat_ip_map = lambda _x: {
                'g001_longreset_hptp_init': ('IPG', 'I:/hdmxpats/nvl_gcd/one.plist'),
                'h001_other_init': ('IPH', 'I:/hdmxpats/nvl_hub/two.plist'),
            }
            obj._build_module_pat_map = lambda _x: {}
            obj._build_prefix_ip_map = lambda: {}
            obj._build_modfolder_ip_map = lambda: {'MIO_HPTP_HXX': 'IPH'}

            obj.main()

            self.assertTrue(obj.result)
            self.assertTrue(any('IP mismatch: aleph "HPTP.patmod.json"' in x['message'] for x in obj.result))
            self.assertTrue(any('regex="g.*_longreset_hptp.*"' in x['message'] for x in obj.result))

    def test_main_integ(self):
        # Integration-style main() test using file-based inputs and ut_result text assertion
        with TempDir(name=True, chdir=True) as tdir:
            envdir = join(tdir, 'CLASS_A')
            tp = _DummyTp(envdir)

            moddir = join(tdir, 'TPL', 'Modules', 'MIO_HPTP_HXX')
            mtpl = join(moddir, 'flow.mtpl')
            mconfig = join(moddir, 'module.mconfig')
            File(mtpl).touch('dummy', mkdir=True, newfile=True)
            File(mconfig).touch(
                '<Root><IPName>IPH</IPName>'
                '<PORRoot BomGroup="CLASS_A"><PlistFile>H_GOOD.plist</PlistFile>'
                '<PlistFile>G_BAD.plist</PlistFile></PORRoot>'
                '</Root>', newfile=True
            )
            tp._mtpls = [mtpl]
            tp.mtpl._modfolder2mod = {'MIO_HPTP_HXX': 'MIO_HPTP_HXX'}

            ipxml_h = join(envdir, 'PLIST_ALL_IPH.plist.xml')
            ipxml_g = join(envdir, 'PLIST_ALL_IPG.plist.xml')
            File(ipxml_h).touch('<Root><PListFile name="H_GOOD.plist"/></Root>', mkdir=True, newfile=True)
            File(ipxml_g).touch('<Root><PListFile name="G_BAD.plist"/></Root>', newfile=True)

            h_plist = join(tdir, 'plb', 'H_GOOD.plist')
            g_plist = join(tdir, 'plb', 'G_BAD.plist')
            File(h_plist).touch('Pat h_good_pat;\n', mkdir=True, newfile=True)
            File(g_plist).touch('Pat g_bad_pat;\n', newfile=True)
            tp.plists._plist_list = [h_plist, g_plist]
            tp.plists._plb_map = {'h_good_plb': h_plist, 'g_bad_plb': g_plist}
            tp.mtpl._flows = [('MIO_HPTP_HXX', 'TN_H', {'patlist': 'h_good_plb'}),
                              ('MIO_HPTP_HXX', 'TN_G', {'patlist': 'g_bad_plb'})]

            aleph = join(moddir, 'AlephFiles', 'HPTP.patmod.json')
            File(aleph).touch('{"PatternsRegEx":["^h_good_pat$","^g_bad_pat$"]}', mkdir=True, newfile=True)
            tp.env._vals = {'ALEPH_FILES': [aleph]}

            obj = AlephIpChk(tp)
            obj.main()

            expect = f'''\
378 MIO_HPTP_HXX IP mismatch: aleph "HPTP.patmod.json" (IPH) matched pattern "g_bad_pat" in plist "{g_plist}" IP=IPG; regex="^g_bad_pat$"
(378, 'MIO_HPTP_HXX'): 1
'''
            self.assertTextEqual(obj.ut_result(), expect)

    def test_main_stops_on_first_same_ip_match(self):
        # Test main() stops checking a regex after same-IP match is found
        with TempDir(name=True, chdir=True) as tdir:
            tp = _DummyTp(tdir)
            tp.mtpl._modfolder2mod = {'MIO_HPTP_HXX': 'MIO_HPTP_HXX'}
            aleph = join(tdir, 'Modules', 'MIO_HPTP_HXX', 'AlephFiles', 'HPTP.patmod.json')
            File(aleph).touch('{"PatternsRegEx":["foo.*"]}', mkdir=True, newfile=True)
            tp.env._vals = {'ALEPH_FILES': [aleph]}

            obj = AlephIpChk(tp)
            obj._build_plist_ip_map = lambda: {'dummy.plist': 'IPH'}
            obj._build_pat_ip_map = lambda _x: {
                'foo_good': ('IPH', 'I:/ok.plist'),
                'foo_bad': ('IPG', 'I:/bad.plist'),
            }
            obj._build_module_pat_map = lambda _x: {'MIO_HPTP_HXX': [('foo_good', 'IPH', 'I:/ok.plist'),
                                                                     ('foo_bad', 'IPG', 'I:/bad.plist')]}
            obj._build_prefix_ip_map = lambda: {}
            obj._build_modfolder_ip_map = lambda: {'MIO_HPTP_HXX': 'IPH'}

            obj.main()

            self.assertEqual(len(obj.result), 0)
            self.assertTrue(obj.passed)

    def test_main_early_return_paths(self):
        # Test early-return branches for empty pattern map and fail-fast ALEPH_FILES retrieval
        with TempDir(name=True, chdir=True) as tdir:
            tp = _DummyTp(tdir)
            tp.env._vals = {}
            obj = AlephIpChk(tp)

            obj._build_plist_ip_map = lambda: {'dummy.plist': 'IPG'}
            obj._build_pat_ip_map = lambda _x: {}
            obj.main()
            self.assertEqual(obj.result, [])

            obj2 = AlephIpChk(tp)
            obj2._build_plist_ip_map = lambda: {'dummy.plist': 'IPG'}
            obj2._build_pat_ip_map = lambda _x: {'foo': ('IPG', 'x.plist')}
            obj2._build_module_pat_map = lambda _x: {'M': [('foo', 'IPG', 'x.plist')]}
            obj2._build_prefix_ip_map = lambda: {}
            obj2._build_modfolder_ip_map = lambda: {}
            tp.env.get_contents = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError('no ALEPH_FILES'))
            self.assertRaises(RuntimeError, obj2.main)

    def test_get_aleph_match_fields_branches(self):
        # Test JSON scalar/list parsing and malformed fallback scalar extraction branches
        with TempDir(name=True, chdir=True) as tdir:
            good_scalar = join(tdir, 'scalar.json')
            malformed_scalar = join(tdir, 'mal_scalar.json')
            missing_json = join(tdir, 'missing.json')

            File(good_scalar).touch('{"A":{"PatternsRegEx":"foo.*"},"B":[{"X":"Y"},"STR"],"C":{"PatternsRegEx":["",null,"ok.*"]}}')
            File(malformed_scalar).touch('{"PatternsRegEx":"bar.*",}')

            got1 = AlephIpChk._get_aleph_match_fields(good_scalar)
            got2 = AlephIpChk._get_aleph_match_fields(malformed_scalar)
            got3 = AlephIpChk._get_aleph_match_fields(missing_json)

            self.assertIn('foo.*', got1['PatternsRegEx'])
            self.assertIn('ok.*', got1['PatternsRegEx'])
            self.assertIn('bar.*', got2['PatternsRegEx'])
            self.assertEqual(got3['PatternsRegEx'], set())

    def test_main_branch_edges(self):
        # Test main branch edges: skip non-json/missing/pkg/no-scope/no-regex and fail-fast regex compile
        with TempDir(name=True, chdir=True) as tdir:
            AlephIpChk.FALLBACK_TO_GLOBAL_PATTERNS = False

            tp = _DummyTp(tdir)
            tp.mtpl._modfolder2mod = {'M1': 'M1', 'M2': 'M2'}

            txt = join(tdir, 'Modules', 'M1', 'AlephFiles', 'a.txt')
            miss = join(tdir, 'Modules', 'M1', 'AlephFiles', 'missing.json')
            pkg = join(tdir, 'common', 'pkg.json')
            noscope = join(tdir, 'Modules', 'M2', 'AlephFiles', 'noscope.json')
            empty = join(tdir, 'Modules', 'M1', 'AlephFiles', 'empty.json')
            badrx = join(tdir, 'Modules', 'M1', 'AlephFiles', 'badrx.json')

            File(txt).touch('x', mkdir=True, newfile=True)
            File(pkg).touch('{"PatternsRegEx":["foo.*"]}', mkdir=True, newfile=True)
            File(noscope).touch('{"PatternsRegEx":["foo.*"]}', mkdir=True, newfile=True)
            File(empty).touch('{"PatternsRegEx":[]}', mkdir=True, newfile=True)
            File(badrx).touch('{"PatternsRegEx":["("]}', mkdir=True, newfile=True)

            tp.env._vals = {'ALEPH_FILES': [txt, miss, pkg, noscope, empty, badrx]}

            obj = AlephIpChk(tp)
            obj._build_plist_ip_map = lambda: {'p.plist': 'IPG'}
            obj._build_pat_ip_map = lambda _x: {'foo_ok': ('IPH', 'I:/ok.plist')}
            obj._build_module_pat_map = lambda _x: {'M1': [('foo_ok', 'IPH', 'I:/ok.plist')]}
            obj._build_prefix_ip_map = lambda: {}
            obj._build_modfolder_ip_map = lambda: {'M1': 'IPH', 'M2': 'IPH'}

            self.assertRaises(re.error, obj.main)
            self.assertEqual(obj.result, [])

    def test_main_dedup_limits_and_needs_scan(self):
        # Test main dedup keys, per-aleph cap path, and needs-scan continue branch
        with TempDir(name=True, chdir=True) as tdir:
            AlephIpChk.FALLBACK_TO_GLOBAL_PATTERNS = True
            aleph_mod._MAX_ERRORS_PER_ALEPH = 1

            tp = _DummyTp(tdir)
            tp.mtpl._modfolder2mod = {'M1': 'M1', 'M2': 'M2'}

            a1 = join(tdir, 'Modules', 'M1', 'AlephFiles', 'same.json')
            a2 = join(tdir, 'Modules', 'M2', 'AlephFiles', 'same.json')
            a3 = join(tdir, 'Modules', 'M1', 'AlephFiles', 'pass.json')
            File(a1).touch('{"PatternsRegEx":["foo.*","bar.*"]}', mkdir=True, newfile=True)
            File(a2).touch('{"PatternsRegEx":["foo.*"]}', mkdir=True, newfile=True)
            File(a3).touch('{"PatternsRegEx":["pass.*"]}', mkdir=True, newfile=True)
            tp.env._vals = {'ALEPH_FILES': [a1, a2, a3]}

            obj = AlephIpChk(tp)
            obj._build_plist_ip_map = lambda: {'p.plist': 'IPG'}
            obj._build_pat_ip_map = lambda _x: {
                'foo_bad': ('IPG', 'I:/bad.plist'),
                'bar_bad': ('IPG', 'I:/bad2.plist'),
                'pass_good': ('IPH', 'I:/good.plist'),
                'pass_bad': ('IPG', 'I:/bad3.plist'),
            }
            obj._build_module_pat_map = lambda _x: {'M1': [('pass_good', 'IPH', 'I:/good.plist'),
                                                           ('pass_bad', 'IPG', 'I:/bad3.plist')]}
            obj._build_prefix_ip_map = lambda: {}
            obj._build_modfolder_ip_map = lambda: {'M1': 'IPH', 'M2': 'IPH'}

            # Preserve regex order so the first mismatch consumes per-aleph cap before second regex group.
            def _fields(path):
                if path.endswith('same.json'):
                    if '/M1/' in path.replace('\\', '/'):
                        return {'PatternsRegEx': ['foo.*', 'bar.*']}
                    return {'PatternsRegEx': ['foo.*']}
                return {'PatternsRegEx': ['pass.*']}

            obj._get_aleph_match_fields = _fields
            obj.main()

            self.assertTrue(any('IP mismatch: aleph "same.json"' in x['message'] for x in obj.result))
            self.assertTrue(obj.passed)

    def test_main_remaining_loop_branches(self):
        # Test remaining loop branches: duplicate key dedup, needs_scan continue, and cap-reached mismatch path
        with TempDir(name=True, chdir=True) as tdir:
            AlephIpChk.FALLBACK_TO_GLOBAL_PATTERNS = True
            aleph_mod._MAX_ERRORS_PER_ALEPH = 1

            tp = _DummyTp(tdir)
            tp.mtpl._modfolder2mod = {'M1': 'M1', 'M2': 'M2'}

            a1 = join(tdir, 'Modules', 'M1', 'AlephFiles', 'dup.json')
            a2 = join(tdir, 'Modules', 'M2', 'AlephFiles', 'dup.json')
            File(a1).touch('{"PatternsRegEx":["noop"]}', mkdir=True, newfile=True)
            File(a2).touch('{"PatternsRegEx":["noop"]}', mkdir=True, newfile=True)
            tp.env._vals = {'ALEPH_FILES': [a1, a2]}

            obj = AlephIpChk(tp)
            obj._build_plist_ip_map = lambda: {'p.plist': 'IPG'}
            obj._build_pat_ip_map = lambda _x: {
                'dup_match_1': ('IPG', 'I:/bad1.plist'),
                'dup_match_2': ('IPG', 'I:/bad2.plist'),
                'dup_pass_1': ('IPH', 'I:/good1.plist'),
                'dup_pass_2': ('IPH', 'I:/good2.plist'),
            }
            obj._build_module_pat_map = lambda _x: {'M1': [('dup_pass_1', 'IPH', 'I:/good1.plist'),
                                                           ('dup_pass_2', 'IPH', 'I:/good2.plist')],
                                                    'M2': [('dup_pass_1', 'IPH', 'I:/good1.plist')]}
            obj._build_prefix_ip_map = lambda: {}
            obj._build_modfolder_ip_map = lambda: {'M1': 'IPH', 'M2': 'IPH'}

            def _fields(path):
                if '/M1/' in path.replace('\\', '/'):
                    return {'PatternsRegEx': ['dup.*', 'dup.*', 'dup_bad.*']}
                return {'PatternsRegEx': ['dup.*', 'dup_bad.*']}

            obj._get_aleph_match_fields = _fields
            obj.main()

            self.assertTrue(obj.passed)

    def test_main_needs_scan_continue_and_cap_false_branch(self):
        # Test remaining loop branches for check-needs-scan continue and cap-condition false path
        with TempDir(name=True, chdir=True) as tdir:
            AlephIpChk.FALLBACK_TO_GLOBAL_PATTERNS = True

            tp = _DummyTp(tdir)
            tp.mtpl._modfolder2mod = {'M1': 'M1', 'M2': 'M2'}

            a1 = join(tdir, 'Modules', 'M1', 'AlephFiles', 'a1.json')
            a2 = join(tdir, 'Modules', 'M2', 'AlephFiles', 'a2.json')
            File(a1).touch('{"PatternsRegEx":["mix.*"]}', mkdir=True, newfile=True)
            File(a2).touch('{"PatternsRegEx":["mix.*"]}', mkdir=True, newfile=True)
            tp.env._vals = {'ALEPH_FILES': [a1, a2]}

            obj = AlephIpChk(tp)
            obj._build_plist_ip_map = lambda: {'p.plist': 'IPG'}
            obj._build_pat_ip_map = lambda _x: {
                'mix_first': ('IPG', 'I:/p1.plist'),
                'mix_second': ('IPG', 'I:/p2.plist'),
                'mix_third': ('IPG', 'I:/p3.plist'),
            }
            obj._build_module_pat_map = lambda _x: {}
            obj._build_prefix_ip_map = lambda: {}
            obj._build_modfolder_ip_map = lambda: {'M1': 'IPG', 'M2': 'IPH'}

            # First run: max=2 keeps one check scanning while another is already disabled.
            aleph_mod._MAX_ERRORS_PER_ALEPH = 2
            obj.main()
            self.assertTrue(obj.passed)

            # Second run: NaN max forces condition at mismatch elif to evaluate false path.
            obj2 = AlephIpChk(tp)
            obj2._build_plist_ip_map = obj._build_plist_ip_map
            obj2._build_pat_ip_map = obj._build_pat_ip_map
            obj2._build_module_pat_map = obj._build_module_pat_map
            obj2._build_prefix_ip_map = obj._build_prefix_ip_map
            obj2._build_modfolder_ip_map = obj._build_modfolder_ip_map
            aleph_mod._MAX_ERRORS_PER_ALEPH = float('nan')
            obj2.main()
            self.assertEqual(obj2.result, [])

    def test_main_cap_zero_and_no_all_pats(self):
        # Test branches where mismatch exists but error cap blocks add_error and all_pats can be empty
        with TempDir(name=True, chdir=True) as tdir:
            aleph_mod._MAX_ERRORS_PER_ALEPH = 0

            tp = _DummyTp(tdir)
            tp.mtpl._modfolder2mod = {'M1': 'M1'}
            a1 = join(tdir, 'Modules', 'M1', 'AlephFiles', 'a1.json')
            File(a1).touch('{"PatternsRegEx":["foo.*"]}', mkdir=True, newfile=True)
            tp.env._vals = {'ALEPH_FILES': [a1]}

            obj = AlephIpChk(tp)
            obj._build_plist_ip_map = lambda: {'p.plist': 'IPG'}
            obj._build_pat_ip_map = lambda _x: {'foo_pkg': ('PKG', 'I:/pkg.plist'), 'foo_bad': ('IPG', 'I:/bad.plist')}
            obj._build_module_pat_map = lambda _x: {'M1': [('foo_pkg', 'PKG', 'I:/pkg.plist')]}
            obj._build_prefix_ip_map = lambda: {}
            obj._build_modfolder_ip_map = lambda: {'M1': 'IPH'}
            obj.main()
            self.assertEqual(obj.result, [])

            # Global fallback path with cap=0 drives the else branch of mismatch handling.
            obj2 = AlephIpChk(tp)
            obj2._build_plist_ip_map = lambda: {'p.plist': 'IPG'}
            obj2._build_pat_ip_map = lambda _x: {'foo_bad': ('IPG', 'I:/bad.plist')}
            obj2._build_module_pat_map = lambda _x: {}
            obj2._build_prefix_ip_map = lambda: {}
            obj2._build_modfolder_ip_map = lambda: {'M1': 'IPH'}
            obj2._get_aleph_match_fields = lambda _p: {'PatternsRegEx': ['foo.*']}
            obj2.main()
            self.assertEqual(obj2.result, [])


if __name__ == '__main__':
    unittest.main()
