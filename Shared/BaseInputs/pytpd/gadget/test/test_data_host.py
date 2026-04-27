#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for datahost
"""
from setenv_unittest import ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
import sys
from gadget.data_host import *
from gadget.ut import TestCase, unittest, MockVar, is_ut_option
from gadget.files import TempDir, File
from gadget.disk import mkdirs, Chdir, rmtree
from gadget.gizmo import Elapsed
from gadget.shell import IS_WIN
from unittest.mock import Mock, mock_open, patch
from main.manager_botos import BotOS
from gadget.shell import SystemCall
from gadget.helperclass import is_cov
import gadget.data_host as data_host
import tarfile


class DHTest(TestCase):
    """Unittest for Datahost"""

    def test_sendmail(self):
        import gadget.gizmo as gizmo
        called = []

        def fake(*args, **kwargs):
            called.append(args)
            called.append(kwargs)

        with MockVar(gizmo, 'send_mail', fake):
            # case1 - tuple
            DataHost().do_sendmail(('address1', 'subject1', 'message1'))
            self.assertEqual(called, [(), {'to_list': 'address1',
                                           'fromemail': 'frombot',
                                           'subject': 'subject1',
                                           'message': 'message1'}])

            # case2 - dict
            called = []
            DataHost().do_sendmail({'to_list': 'address2',
                                    'subject': 'subject2',
                                    'message': 'message2'})
            self.assertEqual(called, [(), {'to_list': 'address2',
                                           'fromemail': 'frombot',
                                           'subject': 'subject2',
                                           'message': 'message2'}])

            # case3 - dict with fromemail
            called = []
            DataHost().do_sendmail({'to_list': 'address2',
                                    'fromemail': 'blah',
                                    'subject': 'subject3',
                                    'html': True,
                                    'message': 'message2'})
            self.assertEqual(called, [(), {'to_list': 'address2',
                                           'fromemail': 'blah',
                                           'subject': 'subject3',
                                           'html': True,
                                           'message': 'message2'}])

    def test_write_file(self):
        with TempDir(name=True, chdir=True) as tdir:
            DataHost().do_write_file((f'{tdir}/a.txt', '123', False))
            self.assertEqual(File(f'{tdir}/a.txt').read(), '123')
            DataHost().do_write_file((f'{tdir}/bb/a.txt', '456', True))
            self.assertEqual(File(f'{tdir}/bb/a.txt').read(), '456')

    def test_writeread_json(self):
        with TempDir(name=True, chdir=True) as tdir:
            data = ({'1': 123}, 'abc.json', tdir)
            DataHost().do_write_json(data)
            DataHost().do_write_json(data)  # file exists

            result = DataHost().do_read_json(f'{tdir}/abc.json')
            self.assertEqual(result, {'1': 123})

    def test_read_completed(self):
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(BotOS, 'root', tdir):
                File(f'{tdir}/completed/a.json').touch('{"key": 1}', mkdir=True)
                File(f'{tdir}/completed/a.txt').touch()
                result = DataHost().do_read_completed(None)
                self.assertEqual(result, {'a.json': {'key': 1}})

    def test_movejob(self):
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(BotOS, 'root', tdir):
                File(f'{tdir}/staging/NVLU/somejob.tar.gz').touch(mkdir=True)
                self.assertEqual(DataHost().do_move_job(('NVLU', 'somejob.tar.gz', 'tester1')), True)
                self.assertEqual(os.listdir(f'{tdir}/testers/tester1'), ['somejob.tar.gz'])
                self.assertEqual(os.listdir(f'{tdir}/staging/NVLU'), [])
                self.assertEqual(DataHost().do_move_job(('NVLU', 'somejob_notfound.tar.gz', 'tester1')), False)

    def test_get_files(self):
        import time
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(BotOS, 'root', tdir):
                with MockVar(time, "time", Mock(return_value=1726020530)):
                    File('testers/testera/nvlu.package.info').touch(mtime=1726020529, mkdir=True)
                    self.assertEqual(DataHost().do_get_files(None),
                                     {'testera': {'nvlu.package.info': 1.0}})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_do_path_exists(self):
        self.assertEqual(DataHost().do_path_exists(['/notfound', '/intel', 'I:/hdmxprogs']),
                         {'/notfound': False, '/intel': True, 'I:/hdmxprogs': True})

    def test_delete_files(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('f1').touch()
            expect = '''
Deleted: f1
For delete but not found: f2
'''
            self.assertTextEqual(DataHost().do_delete_files(['f1', 'f2']), expect)
            self.assertEqual(os.listdir('.'), [])

    def test_cleanup_dir(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('d1/f').touch(mkdir=True)
            File('d2/f').touch(mkdir=True)
            self.assertEqual(len(DataHost().do_cleanup_dir({tdir: 1})), 1)
            self.assertEqual(len(os.listdir(tdir)), 1)

    def test_do_get_meta_content(self):
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(BotOS, 'root', tdir):
                File('staging/_metadata/joba.json').touch('{"key": "value1"}', mkdir=True)
                File('staging/_metadata/jobb.txt').touch()
                self.assertEqual(DataHost().do_get_meta_content(""), {'joba.json': {'key': 'value1'}})

    def test_do_test1(self):
        self.assertEqual(DataHost().do_test1(100), 300)

    def test_do_test2(self):
        value = 3
        arr = [value] * 46
        result = DataHost().do_test2(arr)
        arr[45] = None
        self.assertEqual(result, arr)

    def test_do_test3(self):
        large = {f'Some_testname_large_text_{k}': k + 1000 for k in range(100002)}
        with TempDir(name=True) as tdir:
            sha = '123'
            mkdirs(f'{tdir}/{sha}')
            with MockVar(Chunk, "TMPDIR", tdir):
                self.assertIsInstance(DataHost().do_test3(large), Chunk)

    def test_do_get_chunk(self):
        large = {f'Some_testname_large_text_{k}': k + 1000 for k in range(10002)}
        with MockVar(Chunk, "CHUNK_LIMIT", 10000), TempDir(name=True) as tdir:
            sha = '123'
            mkdirs(f'{tdir}/{sha}')
            with MockVar(Chunk, "TMPDIR", tdir):
                chunk = Chunk.process(large)
                self.assertIsInstance(chunk, Chunk)

                chunks = []
                for piece_n in range(chunk.length):
                    chunks.append(DataHost().do_get_chunk((chunk.sha, piece_n)))
                blob = b"".join(chunks)
                self.assertEqual(pickle.loads(blob), large)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_do_ulat_copy(self):
        with TempDir(name=True, chdir=True) as tdir:

            # case1 - missing product folder
            data = ('nvl/CLASS_S58C/05D00/FullSkipModelInput.csv', 'blah')
            with self.assertRaisesRegex(AssertionError, 'does not exist'):
                DataHost().do_ulat_copy(data, _root=tdir)

            # case2 - success run
            mkdirs('nvl')
            DataHost().do_ulat_copy(data, _root=tdir)

            # check that it created one file
            self.assertEqual(os.listdir(f'{tdir}/nvl/CLASS_S58C/05D00'), ['FullSkipModelInput.csv'])
            # check the contents inside
            self.assertEqual(File(f'{tdir}/nvl/CLASS_S58C/05D00/FullSkipModelInput.csv').read(), 'blah')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_do_ulatmv_copy(self):
        with TempDir(name=True, chdir=True) as tdir:
            # case1 - missing product folder
            data = ('nvl/ulat_mv/fsm/1767926227.7767265/FullSkipModelInput.csv', 'blah')
            with self.assertRaisesRegex(AssertionError, 'does not exist'):
                DataHost().do_ulatmv_copy(data, _root=tdir)

            # case2 - success run
            mkdirs('nvl')
            DataHost().do_ulatmv_copy(data, _root=tdir)

            # check that it created one file
            self.assertEqual(os.listdir(f'{tdir}/nvl/ulat_mv/fsm/1767926227.7767265'), ['FullSkipModelInput.csv'])
            # check the contents inside
            self.assertEqual(File(f'{tdir}/nvl/ulat_mv/fsm/1767926227.7767265/FullSkipModelInput.csv').read(), 'blah')

    def test_do_getinfo(self):
        self.assertIn(1001, DataHost().do_getinfo(1))

    def test_basic(self):
        result = DataHost().central("getinfo", 1, check=True)
        self.assertEqual(result[5], 1001)

        sw = Elapsed()
        ok, result = DataHost().central("getinfo", 1, check=False)
        self.assertEqual(result[5], 1001)
        self.assertEqual(ok, 'Ok')
        print(f"Elapsed for one call: {sw}")

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Actual site test", neg=False))
    def test_sites(self):
        # real connection
        res = DataHost().central("getinfo", 1, check=True)
        self.assertEqual(res[0], 'plxs1579')

        res = DataHost().central("getinfo", 1, check=True, site='PG')
        self.assertEqual(res[0], 'pgweb11')

        res = DataHost().central("getinfo", 1, check=True, site='FM')
        self.assertEqual(res[0], 'fmy0107')

    @unittest.skipIf(*is_ut_option('SLOW', message="will fail on coverage. This test is fast. Pls run."))
    def test_py10_real(self):
        # newer python version check
        code = 'from gadget.data_host import DataHost; print(DataHost().central("getinfo", 1, check=True)[5])'

        cmd = ['/usr/intel/pkgs/python3/3.12.3/bin/python3', '-c', code]
        _, out = SystemCall(cmd).run_outtxt()
        self.assertEqual(out, '1001')

        # old python check
        cmd = ['/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston', '-c', code]
        _, out = SystemCall(cmd).run_outtxt()
        self.assertEqual(out, '1001')

    @unittest.skipIf(is_cov(), 'No need for coverage since it fails from pipeline')
    def test_chunk(self):
        # real connection
        large = {f'Some_testname_large_text_{k}': k + 1000 for k in range(10002)}
        result = DataHost().central("test3", large, check=True)
        self.assertEqual(len(result), 10002)

    def test_chunk_mock(self):
        # mock connection
        def fake_send(data):
            command, root, prod, data = data
            if command == 'test3':
                data = DataHost().do_test3(data)
                return ('Ok', data)
            elif command == 'get_chunk':
                sha, n = data
                data = Chunk.get_piece(sha, n)
                return ('Ok', data)
            else:
                return ('Unknown command')

        large = {f'Some_testname_large_text_{k}': k + 1000 for k in range(10002)}
        with MockVar(CgiConnect2, 'send', Mock(side_effect=fake_send)):
            result = DataHost().central("test3", large, check=True)
            self.assertEqual(len(result), 10002)

    def test_chunk_process(self):
        large = {f'Some_testname_large_text_{k}': k + 1000 for k in range(10002)}
        with TempDir(name=True) as tdir:
            sha = '123'
            mkdirs(f'{tdir}/{sha}')
            with MockVar(Chunk, "TMPDIR", tdir):
                with MockVar(Chunk, "CHUNK_LIMIT", 50000):
                    result = Chunk.process(large, compress=True)    # nothing to do return
                    self.assertEqual(result, large)
                with MockVar(Chunk, "CHUNK_LIMIT", 10000):
                    chunk = Chunk.process(large)
                    self.assertIsInstance(chunk, Chunk)

    def test_chunk_get_piece_exception(self):
        with TempDir(name=True) as tdir:
            sha = '123'
            mkdirs(f'{tdir}/{sha}')
            with MockVar(Chunk, "TMPDIR", tdir):
                with self.assertRaisesRegex(Exception, 'does not exist on server'):
                    Chunk.get_piece('123', 1)

    def test_chunk_assemble_exception(self):
        large = {f'Some_testname_large_text_{k}': k + 1000 for k in range(10002)}
        with TempDir(name=True) as tdir:
            sha = '123'
            mkdirs(f'{tdir}/{sha}')
            with MockVar(Chunk, "TMPDIR", tdir), MockVar(Chunk, "CHUNK_LIMIT", 10000):
                chunk = Chunk.process(large)
                self.assertIsInstance(chunk, Chunk)
                with TempDir(name=True) as tdir:
                    with self.assertRaisesRegex(Exception, r'Chunk\(\): data image was not transferred correctly'):
                        chunk.assemble(tdir)

    def test_check_destdir(self):
        # True check is in test_torch_mv.py
        with TempDir(name=True) as tdir:
            self.assertEqual(DataHost().do_check_destdir(tdir), f'Success check: {tdir}')

    def test_untar(self):
        # True check is in test_torch_mv.py
        with TempDir(name=True) as tdir:
            # setup
            File(f'{tdir}/SRC/a.txt').touch(mkdir=True)
            File(f'{tdir}/SRC/b.txt').touch(mkdir=True)
            mkdirs(f'{tdir}/DST')

            # create tarfile
            tmptar = f'{tdir}/DST/tp.tar.gz'
            with tarfile.open(tmptar, "w:gz") as tarfh:
                with Chdir(f'{tdir}/SRC'):
                    tarfh.add('.')

            # run
            DataHost().do_untar(tmptar)
            self.assertItemsEqual(os.listdir(f'{tdir}/DST'), ['a.txt', 'b.txt'])

    @unittest.skipIf(is_cov(), 'No need for coverage since it fails from pipeline')
    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(not is_py_10new, r'This unittest needs python 3.10+')
    def test_do_invokellm(self):
        class Response:
            pass
        Response.content = 'return content'

        # TO USE: bytes.fromhex(fake_key).decode()
        # TO ENCODE: key.encode().hex()
        fake_key = bytes.fromhex('736b2d4c4c4d39583270516641335437754b31625a347157386d43307652734465466748694a6b4c6d4e6f50715274').decode()     # fake key

        sys.path.insert(0, '/intel/tpvalidation/engtools/tptools/mtl/tools/py3genai')
        from langchain_openai import ChatOpenAI

        with patch("builtins.open", mock_open(read_data=fake_key.encode("utf-8").hex())):
            with MockVar(ChatOpenAI, 'invoke', Mock(return_value=Response)):
                self.assertEqual(DataHost().do_invokellm({}), 'return content')

        with patch("builtins.open", side_effect=Exception):
            self.assertRegex(DataHost().do_invokellm({}), 'Failed to get API key')

        with MockVar(ChatOpenAI, 'invoke', Mock(side_effect=Exception)):
            self.assertRegex(DataHost().do_invokellm({'api_key': fake_key}), 'Error invoking LLM model')

    def test_receive_chunk(self):
        def fake_send(data):
            _, _, _, (sha, n) = data
            data = Chunk.get_piece(sha, n)
            return ('Ok', data)

        # case: base
        with MockVar(data_host, 'is_py_10new', True):
            conn, root, prod = DataHost._process_urp(None, 'JF')
            obj = {f'Some_testname_large_text_{k}': k + 1000 for k in range(10002)}
            with MockVar(Chunk, "CHUNK_LIMIT", 10000), TempDir(name=True) as tdir:
                sha = '123'
                mkdirs(f'{tdir}/{sha}')
                with MockVar(Chunk, "TMPDIR", tdir):
                    chunk = Chunk.process(obj)
                    with MockVar(CgiConnect2, 'send', Mock(side_effect=fake_send)):
                        DataHost()._receive_chunk(root, prod, chunk, conn)

        # case: exception
        with MockVar(data_host, 'is_py_10new', True):
            conn, root, prod = DataHost._process_urp(None, 'JF')
            self.assertTrue(isinstance(conn, CgiConnect2))
            large = {f'Some_testname_large_text_{k}': k + 1000 for k in range(10002)}
            with MockVar(Chunk, "CHUNK_LIMIT", 10000), TempDir(name=True) as tdir:
                sha = '123'
                mkdirs(f'{tdir}/{sha}')
                with MockVar(Chunk, "TMPDIR", tdir):
                    data = Chunk.process(large)
                    with MockVar(CgiConnect2, 'send', Mock(return_value='failed')):
                        with self.assertRaisesRegex(Exception, r'DataHost \[get_chunk\]: failed'):
                            DataHost()._receive_chunk(root, prod, data, conn)

    def test_process_urp(self):
        # case: older python, default
        with MockVar(data_host, 'is_py_10new', False):
            result = DataHost._process_urp(None, 'JF')
        self.assertEqual(result[1:], ('/intel/tpvalidation/engtools/tptools/mtl/beta/gen1', 'tgl.py'))
        self.assertEqual(result[0].url, 'https://tvpv.pdx.intel.com/cgi-bin/pytpdhost.cgi')
        self.assertTrue(isinstance(result[0], CgiConnect))

        # case: older python, urp
        with MockVar(data_host, 'is_py_10new', False):
            result = DataHost._process_urp(('http:/blah/pytpdhost.cgi', 'root', 'prod1'), 'JF')
        self.assertEqual(result[1:], ('root', 'prod1'))
        self.assertEqual(result[0].url, 'http:/blah/pytpdhost.cgi')
        self.assertTrue(isinstance(result[0], CgiConnect))

        # case: newer python, default
        with MockVar(data_host, 'is_py_10new', True):
            result = DataHost._process_urp(None, 'JF')
        self.assertEqual(result[1:], ('/intel/tpvalidation/engtools/tptools/mtl/beta/gen1', 'tgl.py'))
        self.assertEqual(result[0].url, 'https://tvpv.pdx.intel.com/cgi-bin/pytpdhost2.cgi')
        self.assertTrue(isinstance(result[0], CgiConnect2))

        # case: newer python, urp
        with MockVar(data_host, 'is_py_10new', True):
            result = DataHost._process_urp(('http:/blah/pytpdhost.cgi', 'root', 'prod1'), 'JF')
        self.assertEqual(result[1:], ('root', 'prod1'))
        self.assertEqual(result[0].url, 'http:/blah/pytpdhost2.cgi')
        self.assertTrue(isinstance(result[0], CgiConnect2))

        # _process_urp may have modified http.client.HTTPSConnection, so it needs to be reset.
        import http.client
        import importlib
        importlib.reload(http.client)

    def test_central_exception(self):
        with MockVar(data_host, 'is_py_10new', True):
            with MockVar(CgiConnect2, 'send', Mock(return_value='failed')):
                with self.assertRaisesRegex(Exception, r"DataHost \[getinfo\]"):
                    DataHost().central("getinfo", 1, check=True)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_gitpull(self):
        with TempDir(name=True) as tdir:
            result = DataHost().do_gitpull(tdir, _cmd={'gitpull': 'echo gitpull',
                                                       'gitlog': 'echo gitlog'})
            result['machine'] = 'blah'
            self.assertEqual(result, {'out_pull': 'gitpull',
                                      'err_pull': '',
                                      'out_log': 'gitlog',
                                      'err_log': '',
                                      'machine': 'blah',
                                      'cwd': tdir})


class BaseNumber_Analysis(TestCase):

    def tgl(self):
        # Base number analysis, using: TGLUTH6B0H14P00S109
        # n keys=2763    # total instances with "base_number"
        # data1 pickle=159534 bytes    # raw size of pickle protocol=4
        # data2 zlib=19973 bytes       # zlib data size
        #
        # TGLHAQ2R0H36D10S116:
        # n keys=3669
        # data1 pickle=215004 bytes
        # data2 zlib=25185 bytes

        from gadget.strmore import zlib_compress
        from tp.testprogram import TestProgram
        import pickle
        tp = TestProgram('/intel/hdmxprogs/tgl/TGLXXXXRXH36D10S116/TPL/EnvironmentFile.env').pickle_init()
        names = set()
        for mod, item in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=False, keyparam='base_number'):
            names.add(item)
        print(f'n keys={len(names)}')
        data1 = pickle.dumps(names, protocol=4)
        data2 = zlib_compress(data1)
        print(f'data1 pickle={len(data1)}')
        print(f'data2 zlib={len(data2)}')

    def size_limit(self):
        # pdx limit check

        # from windows, jdr laptop vnc from home
        # data1 pickle=559112 bytes
        # data2 zlib=302823 bytes
        # Success: Elapsed 0.903 Secs     # datahost roundtrip
        # Length: 10003

        # data1 pickle=1699305 bytes
        # data2 zlib=914856 bytes
        # Success: Elapsed 1.869 Secs     # datahost roundtrip
        # Length: 30003

        # data1 pickle=35765939 bytes
        # data2 zlib=18481078 bytes       # 18M of compressed data still works!
        # Success: Elapsed 20.624 Secs
        # Length: 600001

        # from unix: data2 zlib=92605609 bytes still works! (92M data being sent)
        # Length: 3000000

        # Do cache first
        DataHost().central("getinfo", 1, check=False)
        large = {f'Some_{sha1(str(k))}_{k}': k + 1000 for k in range(3000000)}
        data1 = pickle.dumps(large, protocol=4)
        data2 = zlib_compress(data1)
        print(f'data1 pickle={len(data1)} bytes')
        print(f'data2 zlib={len(data2)} bytes')

        sw = Elapsed()
        result = DataHost().central("test2", large, check=True)
        print(f"Success: Elapsed {sw}")
        print(f"Length: {len(result)}")


class ProxyManagerTests(TestCase):

    def setUp(self):
        """Set up test environment"""
        # Clear any existing proxy settings for clean test state
        self.original_http = os.environ.get('http_proxy')
        self.original_https = os.environ.get('https_proxy')
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

    def tearDown(self):
        """Clean up after tests"""
        # Restore original proxy settings
        if self.original_http is not None:
            os.environ['http_proxy'] = self.original_http
        else:
            os.environ.pop('http_proxy', None)

        if self.original_https is not None:
            os.environ['https_proxy'] = self.original_https
        else:
            os.environ.pop('https_proxy', None)

    def test_intel_proxy_sets_environment(self):
        """Test that intel_proxy sets correct proxy environment variables"""
        # Ensure no proxy is set initially
        self.assertNotIn('http_proxy', os.environ)
        self.assertNotIn('https_proxy', os.environ)

        with ProxyManager.intel_proxy():
            # Check that proxy values are set correctly
            self.assertEqual(os.environ['http_proxy'], 'http://proxy-dmz.intel.com:911')
            self.assertEqual(os.environ['https_proxy'], 'http://proxy-dmz.intel.com:912')

        # Check that proxy values are removed after exiting context
        self.assertNotIn('http_proxy', os.environ)
        self.assertNotIn('https_proxy', os.environ)

    def test_intel_proxy_restores_original_values(self):
        """Test that intel_proxy restores original proxy values"""
        # Set initial proxy values
        os.environ['http_proxy'] = 'http://original-proxy.com:8080'
        os.environ['https_proxy'] = 'http://original-proxy.com:8443'

        with ProxyManager.intel_proxy():
            # Check that Intel proxy values are set
            self.assertEqual(os.environ['http_proxy'], 'http://proxy-dmz.intel.com:911')
            self.assertEqual(os.environ['https_proxy'], 'http://proxy-dmz.intel.com:912')

        # Check that original values are restored
        self.assertEqual(os.environ['http_proxy'], 'http://original-proxy.com:8080')
        self.assertEqual(os.environ['https_proxy'], 'http://original-proxy.com:8443')

    def test_intel_proxy_handles_exception(self):
        """Test that intel_proxy restores values even when exception occurs"""
        # Set initial proxy values
        os.environ['http_proxy'] = 'http://original-proxy.com:8080'
        os.environ['https_proxy'] = 'http://original-proxy.com:8443'

        try:
            with ProxyManager.intel_proxy():
                # Check that Intel proxy values are set
                self.assertEqual(os.environ['http_proxy'], 'http://proxy-dmz.intel.com:911')
                self.assertEqual(os.environ['https_proxy'], 'http://proxy-dmz.intel.com:912')
                # Raise an exception to test cleanup
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Check that original values are restored even after exception
        self.assertEqual(os.environ['http_proxy'], 'http://original-proxy.com:8080')
        self.assertEqual(os.environ['https_proxy'], 'http://original-proxy.com:8443')

    def test_no_proxy_removes_environment(self):
        """Test that no_proxy removes proxy environment variables"""
        # Set proxy values
        os.environ['http_proxy'] = 'http://some-proxy.com:8080'
        os.environ['https_proxy'] = 'http://some-proxy.com:8443'

        with ProxyManager.no_proxy():
            # Check that proxy values are removed
            self.assertNotIn('http_proxy', os.environ)
            self.assertNotIn('https_proxy', os.environ)

        # Check that original values are restored
        self.assertEqual(os.environ['http_proxy'], 'http://some-proxy.com:8080')
        self.assertEqual(os.environ['https_proxy'], 'http://some-proxy.com:8443')

    def test_no_proxy_handles_no_initial_proxy(self):
        """Test that no_proxy works when no proxy is initially set"""
        # Ensure no proxy is set initially
        self.assertNotIn('http_proxy', os.environ)
        self.assertNotIn('https_proxy', os.environ)

        with ProxyManager.no_proxy():
            # Should still not have proxy values
            self.assertNotIn('http_proxy', os.environ)
            self.assertNotIn('https_proxy', os.environ)

        # Should still not have proxy values after exiting
        self.assertNotIn('http_proxy', os.environ)
        self.assertNotIn('https_proxy', os.environ)

    def test_no_proxy_handles_exception(self):
        """Test that no_proxy restores values even when exception occurs"""
        # Set initial proxy values
        os.environ['http_proxy'] = 'http://original-proxy.com:8080'
        os.environ['https_proxy'] = 'http://original-proxy.com:8443'

        try:
            with ProxyManager.no_proxy():
                # Check that proxy values are removed
                self.assertNotIn('http_proxy', os.environ)
                self.assertNotIn('https_proxy', os.environ)
                # Raise an exception to test cleanup
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Check that original values are restored even after exception
        self.assertEqual(os.environ['http_proxy'], 'http://original-proxy.com:8080')
        self.assertEqual(os.environ['https_proxy'], 'http://original-proxy.com:8443')

    def test_no_proxy_partial_environment(self):
        """Test no_proxy when only one proxy variable is set"""
        # Set only http_proxy
        os.environ['http_proxy'] = 'http://some-proxy.com:8080'
        self.assertNotIn('https_proxy', os.environ)

        with ProxyManager.no_proxy():
            # Both should be removed
            self.assertNotIn('http_proxy', os.environ)
            self.assertNotIn('https_proxy', os.environ)

        # Only http_proxy should be restored
        self.assertEqual(os.environ['http_proxy'], 'http://some-proxy.com:8080')
        self.assertNotIn('https_proxy', os.environ)

    def test_intel_proxy_partial_environment(self):
        """Test intel_proxy when only one proxy variable is initially set"""
        # Set only https_proxy
        os.environ['https_proxy'] = 'http://original-proxy.com:8443'
        self.assertNotIn('http_proxy', os.environ)

        with ProxyManager.intel_proxy():
            # Both should be set to Intel values
            self.assertEqual(os.environ['http_proxy'], 'http://proxy-dmz.intel.com:911')
            self.assertEqual(os.environ['https_proxy'], 'http://proxy-dmz.intel.com:912')

        # http_proxy should be removed, https_proxy should be restored
        self.assertNotIn('http_proxy', os.environ)
        self.assertEqual(os.environ['https_proxy'], 'http://original-proxy.com:8443')

    def test_nested_context_managers(self):
        """Test nested usage of both context managers"""
        # Set initial values
        os.environ['http_proxy'] = 'http://original-proxy.com:8080'
        os.environ['https_proxy'] = 'http://original-proxy.com:8443'

        with ProxyManager.intel_proxy():
            # Should have Intel proxy values
            self.assertEqual(os.environ['http_proxy'], 'http://proxy-dmz.intel.com:911')
            self.assertEqual(os.environ['https_proxy'], 'http://proxy-dmz.intel.com:912')

            with ProxyManager.no_proxy():
                # Should have no proxy values
                self.assertNotIn('http_proxy', os.environ)
                self.assertNotIn('https_proxy', os.environ)

            # Should restore Intel proxy values
            self.assertEqual(os.environ['http_proxy'], 'http://proxy-dmz.intel.com:911')
            self.assertEqual(os.environ['https_proxy'], 'http://proxy-dmz.intel.com:912')

        # Should restore original values
        self.assertEqual(os.environ['http_proxy'], 'http://original-proxy.com:8080')
        self.assertEqual(os.environ['https_proxy'], 'http://original-proxy.com:8443')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
