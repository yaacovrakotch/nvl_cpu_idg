#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
import os
from os.path import join
from time import time

import setenv_unittest
from gadget.files import File, TempDir
from gadget.shell import SystemCall
from gadget.tvpv import TvpvEnv, TraceInfo, TupleDataError
from gadget.ut import TestCase, unittest, MockVar, Mock
from gadget.errors import ErrorInput
import gadget.tvpv as tvpv


if setenv_unittest.EXIST_PDX_I_DRIVE:
    test_get_site_check = TvpvEnv.get_site()
else:
    test_get_site_check = None


class TestTvpvEnv(TestCase):

    def test_site_to_domain(self):
        self.assertEqual(TvpvEnv.site_to_domain('jf'), 'pdx')
        self.assertEqual(TvpvEnv.site_to_domain('JF'), 'pdx')
        self.assertEqual(TvpvEnv.site_to_domain('PDX'), 'pdx')
        self.assertEqual(TvpvEnv.site_to_domain('pdx'), 'pdx')
        self.assertEqual(TvpvEnv.site_to_domain('iil'), 'iil')
        self.assertEqual(TvpvEnv.site_to_domain('IDC'), 'iil')
        self.assertEqual(TvpvEnv.site_to_domain('fm'), 'fm')
        self.assertEqual(TvpvEnv.site_to_domain('pg'), 'png')
        self.assertEqual(TvpvEnv.site_to_domain('ba'), 'iind')
        self.assertEqual(TvpvEnv.site_to_domain(''), 'pdx')

        with self.assertRaisesRegex(ErrorInput, 'does not have mapping'):
            TvpvEnv.site_to_domain('jdr')

    def test_env_type(self):
        # Test the error case
        with MockVar(os, "getenv", Mock(return_value='')):
            with self.assertRaises(EnvironmentError):
                TvpvEnv._get_flash_or_vep()

        with MockVar(os, "getenv", Mock(return_value='/this/is/vep')):
            with MockVar(TvpvEnv, '_is_flash', Mock(return_value=False)):
                self.assertEqual(TvpvEnv._get_flash_or_vep(), 'vep')

            with MockVar(TvpvEnv, '_is_flash', Mock(return_value=True)):
                self.assertEqual(TvpvEnv._get_flash_or_vep(), 'flash')

    def test_get_tvpv_prodcode(self):
        # Nornal unittest mode always returns TST to help when running in a CI/CD pipeline with no VEP/Flash loaded
        self.assertEqual(TvpvEnv.get_tvpv_prodcode(), 'tst')

        with MockVar(tvpv, 'is_ut', Mock(return_value=False)):
            with MockVar(TvpvEnv, "_get_flash_or_vep", Mock(return_value='vep')):
                with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, 'Failed'))):
                    print(f"Checking IS_UT: {tvpv.is_ut()}")
                    self.assertEqual(TvpvEnv.get_tvpv_prodcode(), '')

                with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, 'no product info'))):
                    self.assertEqual(TvpvEnv.get_tvpv_prodcode(), '')

                checkenv_results = """config_env_sites.py is Clean
Environment is Ok!
('tvpvroot:       ', '/p/pde/tvpv/tst')
('Derived Site:   ', 'JF')
('VEP2 Prod Dir:  ', 'TST')
('Product:        ', 'TST3')
('is_rel():       ', True)"""
                with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, checkenv_results))):
                    self.assertEqual(TvpvEnv.get_tvpv_prodcode(), 'tst3')
                    self.assertEqual(TvpvEnv.get_tvpv_prodcode('mtl'), 'mtl')

            with MockVar(TvpvEnv, "_get_flash_or_vep", Mock(return_value='flash')):
                # Find Product from environment
                with MockVar(os, "getenv", Mock(return_value='ftst')):
                    self.assertEqual(TvpvEnv.get_tvpv_prodcode(), 'ftst')
                with MockVar(os, "getenv", Mock(return_value='')):
                    self.assertEqual(TvpvEnv.get_tvpv_prodcode(), '')

    def test_get_tvpv_prodcode_returns_empty_for_unknown_env_type(self):
        with MockVar(tvpv, 'is_ut', Mock(return_value=False)), \
                MockVar(TvpvEnv, "_get_flash_or_vep", Mock(return_value='unknown')), \
                MockVar(SystemCall, 'run_outtxt', Mock(side_effect=AssertionError('unexpected call'))):
            self.assertEqual(TvpvEnv.get_tvpv_prodcode(), '')

    def test_direct_dir_returns_site_code_from_mapping(self):
        with MockVar(tvpv, 'dirname', Mock(return_value='/fake/SC')), \
                MockVar(tvpv, 'basename', Mock(return_value='SC')), \
                MockVar(TvpvEnv, 'site_mapping', {'sc': 'SC'}):
            self.assertEqual(TvpvEnv._direct_dir(), 'sc')

    def test_direct_dir_without_match(self):
        with MockVar(tvpv, 'dirname', Mock(return_value='/fake/UNKNOWN')), \
                MockVar(tvpv, 'basename', Mock(return_value='UNKNOWN')), \
                MockVar(TvpvEnv, 'site_mapping', {'sc': 'SC'}):
            self.assertIsNone(TvpvEnv._direct_dir())

    def test_dns_by_unix_without_host_env(self):
        # Test that _dns_by_unix uses os.popen when HOST env var is missing
        popen_result = Mock(read=Mock(return_value='dns-output\n'))
        with MockVar(os.environ, 'HOST', MockVar.delete), \
                MockVar(tvpv.os, 'popen', Mock(return_value=popen_result)) as popen_mock:
            self.assertEqual(TvpvEnv._dns_by_unix(), 'dns-output')
            self.assertTrue(popen_mock.called)


class TvpvEnvVepPortTest(TestCase):

    def test_get_sitewindows(self):
        f_path = '\\\\amr\\ec\\proj\\mdl\\jf\\intel\\tpvalidation'
        with MockVar(tvpv, 'realpath', Mock(return_value=f_path)):
            self.assertEqual(TvpvEnv._get_site_windows(), 'JF')

        f_path = '\\\\amr\\ec\\proj\\mdl\\ha\\intel\\tpvalidation'
        with MockVar(tvpv, 'realpath', Mock(return_value=f_path)):
            self.assertEqual(TvpvEnv._get_site_windows(), 'IDC')

        f_path = '\\\\amr\\ec\\proj\\something\\blah'
        with MockVar(tvpv, 'realpath', Mock(return_value=f_path)):
            with self.assertRaisesRegex(ErrorInput, 'Cannot get site from'):
                TvpvEnv._get_site_windows()

    @unittest.skipIf(not setenv_unittest.EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(test_get_site_check != "JF", 'JF only')
    def test_get_site(self):

        # get_site_string()
        self.assertEqual(TvpvEnv._get_sitestring('a.pdx.intel.com somename'), "pdx")
        self.assertEqual(TvpvEnv._get_sitestring('/nfs/pdx/proj'), "pdx")
        self.assertEqual(TvpvEnv._get_sitestring('ra'), "ra")
        self.assertIs(TvpvEnv._get_sitestring('/nfx/pdx/nehalem'), None)
        self.assertIs(TvpvEnv._get_sitestring(None), None)

        # get_site() - all methods raised exception
        with MockVar(TvpvEnv, "_dns_by_unix", Mock(side_effect=Exception)), \
                MockVar(TvpvEnv, "_by_eczone", Mock(side_effect=Exception)), \
                MockVar(TvpvEnv, "_direct_dir", Mock(side_effect=Exception)):
            self.assertRaisesRegex(Exception, "exhausted", TvpvEnv.get_site)

        # get_site() - _direct_dir()
        with MockVar(TvpvEnv, "_dns_by_unix", Mock(side_effect=Exception)), \
                MockVar(TvpvEnv, "_by_eczone", Mock(side_effect=Exception)), \
                MockVar(TvpvEnv, "_direct_dir", Mock(return_value="ra")):
            self.assertEqual(TvpvEnv.get_site(), "RA")

        # get_site() - _by_eczone()
        with MockVar(TvpvEnv, "_dns_by_unix", Mock(side_effect=Exception)), \
                MockVar(os.environ, "EC_ZONE", 'ra'), \
                MockVar(TvpvEnv, "_direct_dir", Mock(side_effect=Exception)):
            self.assertEqual(TvpvEnv.get_site(), "RA")

        # SC1 zone - get_site() - pass case
        with MockVar(TvpvEnv, "get_id_zone", Mock(return_value="sc1")):
            self.assertEqual(TvpvEnv.get_site(), "SC1")

        with MockVar(os.environ, "HOST", 'blah.fedh.intel.com'):
            self.assertEqual(TvpvEnv.get_site(), "HD")
        with MockVar(os.environ, "HOST", MockVar.delete):
            self.assertEqual(TvpvEnv.get_site(), "JF")

    def test_get_site_unix_unknown_site(self):
        with MockVar(TvpvEnv, "_dns_by_unix", Mock(return_value='something.unknown.intel.com')), \
                MockVar(TvpvEnv, "_by_eczone", Mock(return_value="")), \
                MockVar(TvpvEnv, "_direct_dir", Mock(return_value=None)):
            with self.assertRaisesRegex(EnvironmentError, "not registered"):
                TvpvEnv._get_site_unix()

    def test_get_id_zone(self):
        # test get_id_zone()
        env = TvpvEnv()

        # sitestring is None, return None
        self.assertEqual(env.get_id_zone(None), None)

        # sitestring is sc
        with MockVar(os.environ, "EC_ZONE", 'sc1'):
            self.assertEqual(env.get_id_zone('sc'), 'sc1')

        with MockVar(os.environ, "EC_ZONE", 'random'):
            self.assertEqual(env.get_id_zone('sc'), 'sc')

        # sitestring is not sc
        self.assertEqual(TvpvEnv.get_id_zone('random'), "random")


class TraceInfoTest(TestCase):

    def test_basics(self):
        TraceInfo.set_continue_on_error(True)
        self.assertTrue(TraceInfo._continue_on_error)
        TraceInfo.set_continue_on_error(False)
        self.assertFalse(TraceInfo._continue_on_error)

    def test_strtoint(self):
        self.assertFalse(TraceInfo._strtoint('abcdef'))
        self.assertEqual(TraceInfo._strtoint('012345'), 12345)
        self.assertEqual(TraceInfo._strtoint('0012345'), 12345)
        self.assertEqual(TraceInfo._strtoint('i0012345'), 12345)
        self.assertEqual(TraceInfo._strtoint('i0012345V9999_01_abcdxxxxxx'), 12345)

    def test_inttuple(self):
        self.assertEqual(TraceInfo.int_tup(123), 123)
        self.assertEqual(TraceInfo.int_tup("123"), 123)
        self.assertEqual(TraceInfo.int_tup("d123"), 123)
        self.assertEqual(TraceInfo.int_tup(" i123 "), 123)
        self.assertEqual(TraceInfo.int_tup(" 000123 "), 123)
        self.assertEqual(TraceInfo.int_tup("g0862861H8005917"), 862861)
        self.assertEqual(TraceInfo.int_tup("d123 b"), 0)  # Does not convert
        self.assertEqual(TraceInfo.int_tup("I am not a tuple"), 0)  # Does not convert
        self.assertEqual(TraceInfo.int_tup("/p/tvpv/disks/d01/g0862861H8005917/g0862861H8005917_xxxx.itpp"), 862861)
        self.assertEqual(TraceInfo.int_tup("/p/tvpv/disks/d01/g0862861H8005917/some.random.file"), 862861)
        self.assertEqual(TraceInfo.int_tup("/p/tvpv/disks/d01/g0862861H8005917/txt"), 862861)  # ensure doesn't throw

        self.assertRaises(TypeError, TraceInfo.int_tup, {"a": 2})

    def test_get_tuple(self):
        # Error case
        self.assertRaises(TypeError, TraceInfo.get_tuple, 32.5)

        self.assertEqual(TraceInfo.get_tuple('123'), {123})
        self.assertEqual(TraceInfo.get_tuple('123', single_val=True), 123)
        self.assertEqual(TraceInfo.get_tuple([123, 0, None, '234', 'd456', '123', 'I am not a tuple']),
                         {123, 234, 456})

        self.assertEqual(TraceInfo.map_tuples('123'), {'123': 123})
        self.assertEqual(TraceInfo.map_tuples(['123', '000123']), {'123': 123, '000123': 123})
        self.assertEqual(TraceInfo.map_tuples('not_a_tuple'), {'not_a_tuple': 0})

    def test_get_tuple_from_file(self):
        with TempDir(name=True) as tdir:
            fname = join(tdir, 'input')
            File(fname).touch("""
            13
            jdr
            # d000014 comment #1
            d0000015

            # Skipping the Prepattern[] and PostPat[] entries in this test
            GlobalPlist ll PrePattern[d0000010H4958400_B00_aa_0Aff_tname] PostPat[d0000011H4958400_B00_aa_0AAA_tname] {
                Pat d0000016H4958400_B00_aa_0AA1xAAAP01Jaff_C_tname;
                Pattern d0000017H4958400_B00_aa_0AA1xAAAP01Jaff_C_tname;
            }

            // d0000018
            /p/tvpv/disks/d01/g0862861H8005917/g0000019H8005917_xxxx.itpp
            """)
            self.assertEqual(TraceInfo.get_tuples_from_file(fname), [13, 15, 16, 17, 19])
            self.assertEqual(TraceInfo.get_tuple_from_line('   '), 0)

    def test_is_tuple(self):
        self.assertEqual(TraceInfo.is_tuple('g123'), {'g123': True})
        self.assertEqual(TraceInfo.is_tuple('not_a_tuple'), {'not_a_tuple': False})
        self.assertEqual(TraceInfo.is_tuple(['g123', 'not_a_tuple']), {'g123': True, 'not_a_tuple': False})

        # Single Val test
        self.assertEqual(TraceInfo.is_tuple(123, single_val=True), True)

    def test_exists(self):
        TraceInfo.clear_cache()

        with MockVar(TraceInfo, "_query_traces", Mock()) as mock_query:
            self.assertEqual(TraceInfo.exists('g123'), {123: False})
            self.assertTrue(mock_query.called)
            self.assertEqual(TraceInfo.exists(['g123', 2345]), {123: False, 2345: False})

            TraceInfo._datacache[123]['exists'] = True
            self.assertEqual(TraceInfo.exists(['g123', 2345]), {123: True, 2345: False})
            self.assertEqual(TraceInfo.exists(123, single_val=True), True)
            self.assertEqual(TraceInfo.exists(2345, single_val=True), False)
            self.assertEqual(TraceInfo.exists([], single_val=True), False)

    def test_is_remote(self):
        TraceInfo.clear_cache()

        with MockVar(TraceInfo, "_query_traces", Mock()) as mock_query:
            self.assertEqual(TraceInfo.is_remote('g123'), {123: False})
            self.assertTrue(mock_query.called)
            self.assertEqual(TraceInfo.is_remote(['g123', 2345]), {123: False, 2345: False})

            TraceInfo._datacache[123]['remote'] = True
            self.assertEqual(TraceInfo.is_remote(['g123', 2345]), {123: True, 2345: False})
            self.assertEqual(TraceInfo.is_remote(123, single_val=True), True)

    def test_is_valid(self):
        TraceInfo.clear_cache()

        with MockVar(TraceInfo, "_query_traces", Mock()) as mock_query:
            self.assertEqual(TraceInfo.is_valid('g123'), {123: False})
            self.assertTrue(mock_query.called)
            self.assertEqual(TraceInfo.is_valid(['g123', 2345]), {123: False, 2345: False})

            TraceInfo._datacache[123]['exists'] = True
            self.assertEqual(TraceInfo.is_valid(['g123', 2345]), {123: False, 2345: False})
            TraceInfo._datacache[123]['valid'] = True
            self.assertEqual(TraceInfo.is_valid(['g123', 2345]), {123: True, 2345: False})
            self.assertEqual(TraceInfo.is_valid('g123', single_val=True), True)

    def test_get_flash_or_vep(self):
        # Test the error case
        with MockVar(os, "getenv", Mock(return_value='')):
            with self.assertRaises(TupleDataError):
                TraceInfo._get_flash_or_vep()

        with MockVar(os, "getenv", Mock(return_value='/this/is/vep')):
            with MockVar(TraceInfo, '_is_flash', Mock(return_value=False)):
                self.assertEqual(TraceInfo._get_flash_or_vep(), 'vep')

            with MockVar(TraceInfo, '_is_flash', Mock(return_value=True)):
                self.assertEqual(TraceInfo._get_flash_or_vep(), 'flash')

    def test_set_flash_prod(self):
        TraceInfo._flash_prod = ''

        # Error Case
        with MockVar(os, "getenv", Mock(return_value='')):
            with self.assertRaises(EnvironmentError):
                TraceInfo.set_flash_prod()

        # Find Product from environment
        with MockVar(os, "getenv", Mock(return_value='tst')):
            TraceInfo.set_flash_prod()
            self.assertEqual(TraceInfo._flash_prod, 'tst')

        # Future calls don't change anything
        with MockVar(os, "getenv", Mock(return_value='tstA')):
            TraceInfo.set_flash_prod()
            self.assertEqual(TraceInfo._flash_prod, 'tst')

            # Refresh forces change
            TraceInfo.set_flash_prod(refresh=True)
            self.assertEqual(TraceInfo._flash_prod, 'tstA')

            # Override takes priority over everything
            TraceInfo.set_flash_prod('prd')
            self.assertEqual(TraceInfo._flash_prod, 'prd')

    def test_valid_field(self):
        self.assertFalse(TraceInfo.is_valid_info_field('abc'))
        self.assertTrue(TraceInfo.is_valid_info_field('tracepath'))
        self.assertTrue(TraceInfo.is_valid_info_field('tracename'))
        self.assertTrue(TraceInfo.is_valid_info_field('tags'))

    def test_update_cache_and_get_info_bit(self):
        TraceInfo.clear_cache()
        data = {
            123: {'tracepath': '/p/d0/g123V111_xxx', 'tracename': 'g123V111_xxx', 'tags': ['abc', 'def']},
            456: {'tracepath': '/p/d0/g456V111_xxx', 'tracename': 'g456V111_xxx',
                  'tags': ['abc', 'PDE_INVALID'],
                  'disassemble_data': {
                      "bit": {'my_field': 'a'},
                      "full": {'my_field': 'abcdef'}
                  }},
        }
        not_found = [999, 888]
        TraceInfo._update_cache(data, not_found)

        with MockVar(TraceInfo, '_query_traces', Mock()):
            bad_tups = TraceInfo.get_disassemble_errors()
            self.assertEqual(len(bad_tups), 3)
            self.assertIn(123, bad_tups)
            self.assertIn(999, bad_tups)
            self.assertIn(888, bad_tups)

            self.assertEqual(len(TraceInfo._datacache), 4)
            expected = {123: 'g123V111_xxx', 456: 'g456V111_xxx'}
            self.assertEqual(TraceInfo.get_info([123, '456'], 'tracename'), expected)
            expected = {123: 'g123V111_xxx', 999: '', 99889: ''}
            self.assertEqual(TraceInfo.get_info([123, '999', 'g99889'], 'tracename'), expected)
            self.assertIn('my_field', TraceInfo._valid_disassemble_fields)

            # Single Val case
            self.assertEqual(TraceInfo.get_info(123, 'tracename', single_val=True), expected[123])

            # Error Case
            with self.assertRaises(ValueError):
                TraceInfo.get_info([123], 'bad_field')

            # Flash case were 'valid' is directly specified
            data = {
                789: {'tracepath': '/p/d0/g123V111_xxx', 'tracename': 'g123V111_xxx', 'tags': ['abc', 'def'],
                      'valid': False}
            }
            TraceInfo._update_cache(data, [])
            self.assertFalse(TraceInfo.is_valid(789, single_val=True))

    def test_get_bit(self):
        TraceInfo.clear_cache()
        dis_data = {
            123: {'bit': {'module': 'F', 'tuple': '000123', 'traceprefix': 'd', 'myrev': 'a'},
                  'full': {'module': 'MFunc', 'tuple': '000123', 'traceprefix': 'Debug', 'myrev': 'A1'}},
            456: {'bit': {'module': 'S', 'tuple': '000456', 'traceprefix': 'g'},
                  'full': {'module': 'MScn', 'tuple': '000456', 'traceprefix': 'Gold'}}
        }
        # Fill in some disassemble data for lookups
        for tup in dis_data:
            TraceInfo._datacache[tup]['disassemble_data'].update(dis_data[tup])
            for field in list(dis_data[tup]['bit'].keys()) + list(dis_data[tup]['full'].keys()):
                TraceInfo._valid_disassemble_fields.add(field)

        with MockVar(TraceInfo, '_disassemble_traces', Mock()):
            # Error Cases
            tuples = [123, '456']
            with self.assertRaises(ValueError):
                TraceInfo.get_bit(tuples, 'bad_field')

            with self.assertRaises(ValueError):
                TraceInfo.get_bit(tuples, 'traceprefix', 'bad_valtype')

            expected_bits = {123: 'F', 456: 'S'}
            expected_full = {123: 'MFunc', 456: 'MScn'}
            self.assertEqual(TraceInfo.get_bit(tuples, 'module', valtype='bit'), expected_bits)
            self.assertEqual(TraceInfo.get_bit(tuples, 'module'), expected_full)
            self.assertEqual(TraceInfo.get_bit('123', 'module', single_val=True), expected_full[123])

            # Test case where some tups and fields are missing
            tuples = [123, '456', 999]
            expected_bits = {123: 'a', 456: '', 999: ''}
            self.assertEqual(TraceInfo.get_bit(tuples, 'myrev', valtype='bit'), expected_bits)

        # Try a case where a full tracename is passed in, finder can't locate it, but name_disassemble still works.
        dis_data = {
            9999: {'bit': {'module': 'A', 'tuple': '009999', 'traceprefix': 'd'},
                   'full': {'module': 'MArr', 'tuple': '009999', 'traceprefix': 'Debug'}}
        }
        with MockVar(TraceInfo, "_get_flash_or_vep", Mock(return_value='vep')):
            with MockVar(TraceInfo, "_query_vep", Mock(return_value={})), \
                    MockVar(TraceInfo, '_disassemble_vep', Mock(return_value=dis_data)):
                t_name = 'd0009999V999999_xxAxxx_00'
                self.assertEqual(TraceInfo.get_bit(t_name, 'module', 'bit', single_val=True), 'A')
                self.assertEqual(TraceInfo.get_bit(t_name, 'module', single_val=True), 'MArr')
                expected_exist = {9999: False}
                self.assertEqual(TraceInfo.exists(9999), expected_exist)

    def test_query_traces(self):
        TraceInfo.clear_cache()
        query_return_data = {
            123: {'tracepath': '/p/d0/g123V111_xxx', 'tracename': 'g123V111_xxx', 'tags': ['abc', 'def']},
            456: {'tracepath': '/p/d0/g456V111_xxx', 'tracename': 'g456V111_xxx', 'tags': ['abc', 'PDE_INVALID']},
        }
        with MockVar(TraceInfo, "_get_flash_or_vep", Mock(return_value='vep')):
            with MockVar(TraceInfo, "_query_vep", Mock(return_value=query_return_data)) as mock_vep, \
                    MockVar(TraceInfo, "_query_flash", Mock(return_value=query_return_data)) as mock_flash, \
                    MockVar(TraceInfo, "_disassemble_traces", Mock()):
                TraceInfo._query_traces([123, 456, 999])
                self.assertTrue(mock_vep.called)
                self.assertFalse(mock_flash.called)

                self.assertEqual(len(TraceInfo._datacache), 3)
                expected_exists = {123: True, 456: True, 999: False}
                self.assertEqual(TraceInfo.exists(list(expected_exists.keys())), expected_exists)
                expected_valid = {123: True, 456: False, 999: False}
                self.assertEqual(TraceInfo.is_valid(list(expected_valid.keys())), expected_valid)
                expected_remote = {123: False, 456: False, 999: False}
                self.assertEqual(TraceInfo.is_remote(list(expected_remote.keys())), expected_remote)
                expected_names = {123: 'g123V111_xxx', 456: 'g456V111_xxx', 999: ''}
                self.assertEqual(TraceInfo.get_info(list(expected_names.keys()), 'tracename'), expected_names)
                expected_paths = {123: '/p/d0/g123V111_xxx', 456: '/p/d0/g456V111_xxx', 999: ''}
                self.assertEqual(TraceInfo.get_info(list(expected_paths.keys()), 'tracepath'), expected_paths)

        TraceInfo.clear_cache()
        with MockVar(TraceInfo, "_get_flash_or_vep", Mock(return_value='flash')):
            with MockVar(TraceInfo, "_query_vep", Mock(return_value=query_return_data)) as mock_vep, \
                    MockVar(TraceInfo, "_query_flash", Mock(return_value=query_return_data)) as mock_flash, \
                    MockVar(TraceInfo, "_disassemble_traces", Mock()):
                TraceInfo._query_traces([123, 456, 999])

                self.assertFalse(mock_vep.called)
                self.assertTrue(mock_flash.called)
                self.assertEqual(len(TraceInfo._datacache), 3)
                expected_exists = {123: True, 456: True, 999: False}
                self.assertEqual(TraceInfo.exists(list(expected_exists.keys())), expected_exists)

    def test_query_vep(self):
        TraceInfo.clear_cache()
        self.assertEqual(TraceInfo._query_vep([]), {})
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, "Error message"))):
            with self.assertRaises(SystemError):
                TraceInfo._query_vep([999])

        # No Results Found
        finder_txt = """
    INFO: Missing(tuple=000None)
    INFO: No matching entries found

    INFO: Performing auto remote search in remote sites:

"""
        # Finder will return en error code when 0 results returned. Make sure this doesn't throw an error
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, finder_txt))):
            tup_data = TraceInfo._query_vep([123, 456, 789, 999])
            self.assertEqual(len(tup_data), 0)

        # Basic case with results from both local and remote
        finder_txt = """
    INFO: Results from 'SC' :
/p/pde/tvpv/tst/d01/s81/g0000123V11111_00_xxxxxx/g0000123V11111_00_xxxxxx_xxxxx.itpp : [tag1,tag3,tag2,LI_sbftA]

    INFO: Results from local site 'JF' :
/p/pde/tvpv/tst/d11/s81/g0000456V11111_00_xxxxxx/g0000456V11111_00_xxxxxx_xxxxx.itpp : [tag1,tag3,tag2,PDE_INVALID]
/p/pde/tvpv/tst/d11/s81/g0000789V11111_00_xxxxxx/g0000789V11111_00_xxxxxx_xxxxx.itpp : [tag1,tag3,tag2]

some unknown line
some_bad_path : some_other_stuff
"""
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, finder_txt))):
            tup_data = TraceInfo._query_vep([123, 456, 789, 999])
            self.assertEqual(len(tup_data), 3)
            self.assertTrue(123 in tup_data)
            self.assertTrue(456 in tup_data)
            self.assertTrue(789 in tup_data)
            self.assertFalse(999 in tup_data)

            self.assertTrue(tup_data[123]['exists'])
            self.assertTrue(tup_data[123]['valid'])
            self.assertTrue(tup_data[123]['remote'])
            self.assertEqual(tup_data[123]['remote_site'], 'SC')
            self.assertEqual(tup_data[123]['tracename'], 'g0000123V11111_00_xxxxxx_xxxxx.itpp')
            self.assertEqual(tup_data[123]['tracepath'],
                             '/p/pde/tvpv/tst/d01/s81/g0000123V11111_00_xxxxxx/g0000123V11111_00_xxxxxx_xxxxx.itpp')
            self.assertIn('tag1', tup_data[123]['tags'])
            self.assertEqual(tup_data[123]['lineitem'], 'sbftA')

            self.assertTrue(tup_data[456]['exists'])
            self.assertFalse(tup_data[456]['valid'])
            self.assertFalse(tup_data[456]['remote'])
            self.assertEqual(tup_data[456]['remote_site'], '')

            self.assertTrue(tup_data[789]['exists'])
            self.assertTrue(tup_data[789]['valid'])
            self.assertFalse(tup_data[789]['remote'])
            self.assertEqual(tup_data[789]['remote_site'], '')

        # Case where Tuple exists at both remote and local site, ensure Local verions is always reported
        # Finder default: Local site reported last -- Works natuarally!
        finder_txt_default = """
    INFO: Results from 'SC' :
/p/pde/tvpv/tst/d01/s81/g0000123V11111_00_xxxxxx/g0000123V11111_00_xxxxxx_xxxxx.itpp : [tag1,tag3,tag2]

    INFO: Results from local site 'JF' :
/p/pde/tvpv/tst/d11/s81/g0000123V11111_00_xxxxxx/g0000123V11111_00_xxxxxx_xxxxx.itpp : [tag1,tag3,tag2]
"""
        # Case where Tuple exists at both remote and local site, ensure Local verions is always reported
        # Sanity check if Finder ends up reversing order and reporting local first
        finder_txt_local_first = """
    INFO: Results from local site 'JF' :
/p/pde/tvpv/tst/d11/s81/g0000123V11111_00_xxxxxx/g0000123V11111_00_xxxxxx_xxxxx.itpp : [tag1,tag3,tag2]

    INFO: Results from 'SC' :
/p/pde/tvpv/tst/d01/s81/g0000123V11111_00_xxxxxx/g0000123V11111_00_xxxxxx_xxxxx.itpp : [tag1,tag3,tag2]
"""
        for finder_txt in [finder_txt_default, finder_txt_local_first]:
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, finder_txt))):
                tup_data = TraceInfo._query_vep([123, 456, 789, 999])
                self.assertEqual(len(tup_data), 1)
                self.assertFalse(tup_data[123]['remote'])
                self.assertEqual(tup_data[123]['remote_site'], '')
                # Path contains '/d11/' in local ... just to double check
                self.assertEqual(tup_data[123]['tracepath'],
                                 '/p/pde/tvpv/tst/d11/s81/g0000123V11111_00_xxxxxx/g0000123V11111_00_xxxxxx_xxxxx.itpp')

    def test_query_flash(self):
        TraceInfo.clear_cache()
        TraceInfo.set_flash_prod('tst')
        self.assertEqual(TraceInfo._query_flash([]), {})

        with TempDir(name=True) as tdir:
            flash_json = join(tdir, 'flash_out.json')  # To Mock the results from the Flash call
            # Mock the TempDir call in the code so we can provide and output JSON file
            with MockVar(TempDir, "__enter__", Mock(return_value=tdir)):  # Mock __enter__ for context manager usage

                # Error Case
                flash_error = "Error occurred"
                with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, flash_error))):
                    with self.assertRaisesRegex(SystemError, flash_error):
                        TraceInfo._query_flash([999])

                json_content = """[
  {
    "dti": false,
    "lineitem": "Mscan_stf100",
    "name": "d0000123R4884919A_edt_sa_sNs_phase1",
    "path": "/p/pde/tvpv/rpl/flash/rpl/traces/j0/4884919/0169366/d0169366R4884919A_edt_sa_sNs_phase1.itpp.bz2",
    "tag": [
      "htd_ver__soc_rpl_j0_master_21ww51e__eng_2020_ww08a",
      "num_chunk_198_369",
      "LI_Mscan_stf100"
    ],
    "tid": "4884919",
    "tuple": "0000123",
    "valid": true
  },
  {
    "dti": false,
    "lineitem": "Mscan_stf100",
    "name": "d0000234R4884919A_edt_sa_sNs_phase1",
    "path": "/p/pde/tvpv/rpl/flash/rpl/traces/j0/4884919/0169367/d0000234R4884919A_edt_sa_sNs_phase1.itpp.bz2",
    "tag": [
      "htd_ver__soc_rpl_j0_master_21ww51e__eng_2020_ww08a",
      "num_chunk_199_369",
      "LI_Mscan_stf100"
    ],
    "tid": "4884919",
    "tuple": "0000234",
    "valid": false
  }
]"""
                File(flash_json).touch(json_content, newfile=True)
                with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, 'Success'))):
                    data = TraceInfo._query_flash([123, 234, 999])
                    self.assertEqual(len(data), 2)
                    self.assertIn(123, data)
                    self.assertEqual(data[123]['tuple_int'], 123)
                    self.assertEqual(data[123]['tracename'], "d0000123R4884919A_edt_sa_sNs_phase1")
                    self.assertEqual(data[123]['lineitem'], "Mscan_stf100")
                    self.assertEqual(len(data[123]['tags']), 3)
                    self.assertTrue(data[123]['exists'])
                    self.assertTrue(data[123]['valid'])

                    self.assertIn(234, data)
                    self.assertEqual(data[234]['tuple_int'], 234)
                    self.assertEqual(data[234]['tracename'], "d0000234R4884919A_edt_sa_sNs_phase1")
                    self.assertTrue(data[234]['exists'])
                    self.assertFalse(data[234]['valid'])
                    self.assertNotIn(999, data)

    def test_has_disassemble_data(self):
        TraceInfo.clear_cache()
        cache_data = {
            123: {'tracepath': '/path/g0000123.stuff.itpp', 'tracename': 'g0000123',
                  'disassemble_data': {
                      "bit": {'module': 'F', 'traceprefix': 'd'}
                  }},
            456: {'tracepath': '/path/g0000123.stuff.itpp', 'tracename': 'g0000123'},
        }
        TraceInfo._update_cache(cache_data, [555])

        self.assertIn('module', TraceInfo._valid_disassemble_fields)
        is_disassembled = TraceInfo._has_disassemble_data([123, 456, 555, 999, 'sample'])
        expected = {123: True, 456: False, 555: False, 999: False, 'sample': False}
        self.assertEqual(is_disassembled, expected)

    def test_disassemble_traces(self):
        TraceInfo.clear_cache()
        finder_data = {
            123: {'tracepath': '/p/d0/g123V111_xxx', 'tracename': 'g123V111_xxx', 'tags': ['abc', 'def']},
            456: {'tracepath': '/p/d0/g456V111_xxx', 'tracename': 'g456V111_xxx', 'tags': ['abc', 'PDE_INVALID']},
        }
        TraceInfo._update_cache(finder_data, [])

        dis_data = {
            123: {'bit': {'module': 'F', 'tuple': '000123', 'traceprefix': 'd'},
                  'full': {'module': 'MFunc', 'tuple': '000123', 'traceprefix': 'Debug'}},
            456: {'bit': {'module': 'S', 'tuple': '000456', 'traceprefix': 'g'},
                  'full': {'module': 'MScn', 'tuple': '000456', 'traceprefix': 'Gold'}}
        }
        with MockVar(TraceInfo, "_get_flash_or_vep", Mock(return_value='vep')):
            with MockVar(TraceInfo, "_disassemble_vep", Mock(return_value=dis_data)) as mock_vep, \
                    MockVar(TraceInfo, "_disassemble_flash", Mock(return_value=dis_data)) as mock_flash, \
                    MockVar(TraceInfo, "_query_traces", Mock()):
                TraceInfo._disassemble_traces([123, 456, 999, 'something bad'])
                self.assertTrue(mock_vep.called)
                self.assertFalse(mock_flash.called)

                self.assertEqual(len(TraceInfo._datacache), 2)
                self.assertEqual(TraceInfo._datacache[123]['disassemble_data']['bit']['module'], 'F')
                self.assertEqual(TraceInfo._datacache[123]['disassemble_data']['full']['module'], 'MFunc')
                self.assertEqual(TraceInfo._datacache[456]['disassemble_data']['bit']['traceprefix'], 'g')
                self.assertEqual(TraceInfo._datacache[456]['disassemble_data']['full']['traceprefix'], 'Gold')

        with MockVar(TraceInfo, "_get_flash_or_vep", Mock(return_value='flash')):
            with MockVar(TraceInfo, "_disassemble_vep", Mock(return_value=dis_data)) as mock_vep, \
                    MockVar(TraceInfo, "_disassemble_flash", Mock(return_value=dis_data)) as mock_flash, \
                    MockVar(TraceInfo, "_query_traces", Mock()):
                TraceInfo._disassemble_traces([123, 456, 999, 'something bad'])
                self.assertFalse(mock_vep.called)
                self.assertTrue(mock_flash.called)

                self.assertEqual(len(TraceInfo._datacache), 2)
                self.assertEqual(TraceInfo._datacache[123]['disassemble_data']['bit']['module'], 'F')
                self.assertEqual(TraceInfo._datacache[123]['disassemble_data']['full']['module'], 'MFunc')

    def test_disassemble_vep(self):
        TraceInfo.clear_cache()
        # Test Empty case
        self.assertEqual(TraceInfo._disassemble_vep([]), {})

        # Test Error case
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, "Error message"))):
            with self.assertRaises(SystemError):
                TraceInfo._disassemble_vep(['g0000999'])

        # No Results Found
        disassemble_txt = ''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, disassemble_txt))):
            data = TraceInfo._disassemble_vep({'d0001234H0631170'})
            self.assertEqual(data, {})

        # Real Results
        disassemble_txt = """
d0001234H0631170_E00_HA000_0nna0000x00e_xxxxxxxxxxxxxxx_LF_htdval_precat_test,bit,traceprefix=d,tuple=0001234,testfamily=H,tid=0631170,chunknum=01,Revision=E,rapttr=00,product=H,modelstep=A0,modelindex=0,simodeindex=0,mcpbit=0,longresettype=n,shortresettype=n,traceflow=a,resetpair=00,precatpair=00,fabric_init=x,midcatpair=00,testtype=e,xbit=x,simtype=L,module_bit=F,testname=htdval_precat_test,prodstep=e,module=Mft,subver=sub11,full_Trace=d0041685H0631170_E00_HA000_0nna0000x00e_xxxxxxxxxxxxxxx_LF_htdval_precat_test,NameType=Trace,orig_testname=htdval_precat_test,
d0001234H0631170_E00_HA000_0nna0000x00e_xxxxxxxxxxxxxxx_LF_htdval_precat_test,full,traceprefix=Debug,tuple=0001234,testfamily=HSW,tid=0631170,chunknum=01,Revision=E,rapttr=00,product=htdval,modelstep=A0,modelindex=0,simodeindex=0,mcpbit=default,longresettype=no_longreset,shortresettype=no_shortreset,traceflow=precat,resetpair=00,precatpair=00,fabric_init=disabled,midcatpair=00,testtype=precat,xbit=x,simtype=simless,module_bit=Mft,testname=htdval_precat_test,prodstep=e,module=F,subver=sub11,full_Trace=fullname,NameType=NameType,orig_testname=htdval_precat_test,invalid_field

some extra line
"""
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, disassemble_txt))):
            data = TraceInfo._disassemble_vep({'d0001234H0631170'})
            self.assertEqual(len(data), 1)
            self.assertIn(1234, data)
            self.assertIn('bit', data[1234])
            self.assertIn('full', data[1234])
            self.assertEqual(data[1234]['bit']['traceprefix'], 'd')
            self.assertEqual(data[1234]['full']['traceprefix'], 'Debug')
            self.assertEqual(data[1234]['bit']['chunknum'], '01')
            self.assertEqual(data[1234]['full']['chunknum'], 1)

            self.assertIn('traceprefix', TraceInfo._valid_disassemble_fields)
            self.assertIn('tid', TraceInfo._valid_disassemble_fields)
            self.assertNotIn('unknown', TraceInfo._valid_disassemble_fields)

    def test_disassemble_flash(self):
        TraceInfo.clear_cache()
        TraceInfo.set_flash_prod('tst')
        self.assertEqual(TraceInfo._disassemble_flash([]), {})

        with TempDir(name=True) as tdir:
            flash_json = join(tdir, 'flash_out.json')  # To Mock the results from the Flash call
            # Mock the TempDir call in the code so we can provide and output JSON file
            with MockVar(TempDir, "__enter__", Mock(return_value=tdir)):  # Mock __enter__ for context manager usage

                # Error Case
                flash_error = "Error occurred"
                with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, flash_error))):
                    with self.assertRaisesRegex(SystemError, flash_error):
                        TraceInfo._disassemble_flash(['d0000123'])

                json_content = """{
  "d0000123R4884919A_LW_J0S0tdv_RJ0P0Th5C1402_0411616016x_CBOPAIR_edt_sa_sNs_phase1": {
    "traceprefix": {
      "val": "d",
      "desc": "debug"
    },
    "tuple": {
      "val": "0000123",
      "desc": "0000123"
    },
    "product": {
      "val": "R",
      "desc": "RPL"
    },
    "tid": {
      "val": "4884919",
      "desc": "4884919"
    },
    "module": {
      "val": "A",
      "desc": "Marr"
    },
    "underscore_1": {
      "val": "_",
      "desc": "_"
    },
    "chunknum": {
      "val": "02",
      "desc": "02"
    }
  },
  "d0000234R4884919A_LW_J0S0tdv_RJ0P0Th5C1402_0411616016x_CBOPAIR_edt_sa_sNs_phase1": {
    "traceprefix": {
      "val": "d",
      "desc": "debug"
    },
    "tuple": {
      "val": "0000234",
      "desc": "0000234"
    },
    "product": {
      "val": "R",
      "desc": "RPL"
    },
    "tid": {
      "val": "4884919",
      "desc": "4884919"
    },
    "module": {
      "val": "A",
      "desc": "Marr"
    },
    "underscore_1": {
      "val": "_",
      "desc": "_"
    },
    "chunknum": {
      "val": "03",
      "desc": "03"
    }
  },
  "g0000456R2742828A_00000_0n2xcLm0e03n00x030207_arr_arsratmf_mchc_lc_x_s": null
}"""
                File(flash_json).touch(json_content, newfile=True)
                with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, 'Success'))):
                    tracenames = [
                        "d0000123R4884919A_LW_J0S0tdv_RJ0P0Th5C1402_0411616016x_CBOPAIR_edt_sa_sNs_phase1",
                        "d0000234R4884919A_LW_J0S0tdv_RJ0P0Th5C1402_0411616016x_CBOPAIR_edt_sa_sNs_phase1"
                    ]
                    data = TraceInfo._disassemble_flash(tracenames)
                    self.assertEqual(len(data), 2)
                    self.assertIn(123, data)
                    self.assertIn(234, data)
                    self.assertIn('bit', data[123])
                    self.assertIn('full', data[123])
                    self.assertNotIn('underscore_1', data[123]['bit'])  # Skip the underscore separators
                    self.assertEqual(data[123]['bit']['traceprefix'], 'd')
                    self.assertEqual(data[123]['full']['traceprefix'], 'debug')
                    self.assertEqual(data[123]['bit']['chunknum'], '02')
                    self.assertEqual(data[123]['full']['chunknum'], 2)

                    self.assertIn('traceprefix', TraceInfo._valid_disassemble_fields)
                    self.assertIn('tid', TraceInfo._valid_disassemble_fields)
                    self.assertNotIn('unknown', TraceInfo._valid_disassemble_fields)

    def test_wait_to_showup(self):
        TraceInfo.clear_cache()

        with MockVar(TraceInfo, "_query_traces", Mock()):
            # No valid traces provided - no sleep
            start_t = time()
            TraceInfo._wait_to_showup([], timeout=1)
            self.assertLessEqual(time() - start_t, 0.5)  # No sleep happened

            # Everything is local
            start_t = time()
            TraceInfo._update_cache({123: {'remote': False}}, [])
            TraceInfo._wait_to_showup([123], timeout=1)
            self.assertLessEqual(time() - start_t, 0.5)  # No sleep happened

            # Error case where copy doesn't show up before timeout
            start_t = time()
            TraceInfo._update_cache({123: {'remote': True}}, [])
            with self.assertRaises(SystemError):
                TraceInfo._wait_to_showup([123], timeout=0.3, sleep_amt=0.1, report_interval=2)
            self.assertGreaterEqual(time() - start_t, 0.3)  # Sleep did happen

    def test_remote_copy(self):
        with MockVar(TraceInfo, "_wait_to_showup", Mock()), \
                MockVar(TraceInfo, "_remote_copy_vep", Mock()), \
                MockVar(TraceInfo, "_remote_copy_flash", Mock()):
            with MockVar(TraceInfo, "is_remote", Mock(return_value={123: True})):
                with MockVar(TraceInfo, "_get_flash_or_vep", Mock(return_value='vep')):
                    start_t = time()
                    TraceInfo.remote_copy([123])
                    self.assertLessEqual(time() - start_t, 0.3)  # No sleep happened

                with MockVar(TraceInfo, "_get_flash_or_vep", Mock(return_value='flash')):
                    start_t = time()
                    TraceInfo.remote_copy([123])
                    self.assertLessEqual(time() - start_t, 0.3)  # No sleep happened

            # Nothing to do
            with MockVar(TraceInfo, "is_remote", Mock(return_value={123: False})):
                start_t = time()
                TraceInfo.remote_copy([123])
                self.assertLessEqual(time() - start_t, 0.3)  # No sleep happened

    def test_remote_copy_vep(self):
        TraceInfo.clear_cache()
        remote_site_data = {
            123: "SC",
            456: "SC",
            789: "PG",
        }
        with MockVar(TraceInfo, 'get_info', Mock(return_value=remote_site_data)):
            # Passing case
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, 'Everything Passed'))) as mock_copy:
                remote_tups = list(remote_site_data.keys())
                TraceInfo._remote_copy_vep(remote_tups)
                self.assertEqual(mock_copy.call_count, 2)  # Called once for each unique site

            # Error case
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, 'Had an error!'))) as mock_copy:
                remote_tups = list(remote_site_data.keys())
                with self.assertRaises(SystemError):
                    TraceInfo._remote_copy_vep(remote_tups)
                self.assertEqual(mock_copy.call_count, 2)  # Called once for each unique site

            # Rsync Error case
            outtxt = "Everything seems file\nNope there's an problem!\nRSYNC failed. Exiting ...\n"
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, outtxt))) as mock_copy:
                remote_tups = list(remote_site_data.keys())
                with self.assertRaises(SystemError):
                    TraceInfo._remote_copy_vep(remote_tups)
                self.assertEqual(mock_copy.call_count, 2)  # Called once for each unique site

    def test_remote_copy_flash(self):
        TraceInfo.clear_cache()
        TraceInfo._remote_copy_flash([])
        self.assertTrue(True)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
