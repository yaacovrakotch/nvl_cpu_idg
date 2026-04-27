#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for manager_botos
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from main.manager_botos import *
from os.path import join, dirname, abspath
from functools import partial
import main.manager_botos as manager_botos
import os
from pprint import pprint, pformat


class TestScenario(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case1(self):
        # Full run, case1: 2 jobs local, 2 jobs remote, 2 testers local
        # The 2 local jobs submitted to 2 local tester, so pool is left with 2 remote jobs
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/staging/nvlu/8000_1726189854_E.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/nvlu/8001_1726189853_F.tar.gz').touch()
            File(f'{tdir}/staging/nvlu/blah.txt').touch()
            File(f'{tdir}/staging/_metadata/1726189854_E.json').touch('{"site": "JF"}', mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189853_F.json').touch('{"site": "JF"}')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch(mkdir=True)
            File(f'{tdir}/testers/testerb/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testerb/idle.status').touch(mkdir=True)
            mkdirs(f'{tdir}/completed')

            remote_staging = {'nvlu': {'8002_9726189852_F.tar.gz': 1,
                                       'blah.txt': 2},
                              'nvls': {'8002_9726189853_F.tar.gz': 1}}
            tester_files = {}
            metafiles = {'9726189852_F.json': {'site': 'PG'},
                         '9726189853_F.json': {'site': 'PG'}}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # Expects- Check the staging, tester and pool
            self.assertEqual(obj.job_count, 2)
            self.assertEqual(set(os.listdir(f'{tdir}/completed')), set())
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), ['blah.txt'])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status', '8000_1726189854_E.tar.gz'})

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testerb')),
                             {'nvlu.package.info', 'idle.status', '8001_1726189853_F.tar.gz'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'),
                             ['8002_9726189852_F.tar.gz.remote'])

            self.assertEqual(os.listdir(f'{tdir}/pool/nvls'),
                             ['8002_9726189853_F.tar.gz.remote'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'1726189854_E.json',
                              '1726189853_F.json',
                              '9726189852_F.json',
                              '9726189853_F.json'
                              })

            expect = '''
{
    "site": "JF",
    "tester": "JF: testera"
}
'''
            self.assertTextEqual(File(f'{tdir}/pool/_metadata/1726189854_E.json').read(), expect)

            # 2nd run - complete
            remote_staging = {}
            tester_files = {}
            metafiles = {}
            File(f'{tdir}/testers/testera/1726189854_E.result.json').touch('{"code": 0}')
            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()
            self.assertEqual(set(os.listdir(f'{tdir}/completed')), {'1726189854_E.json'})
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status', '8000_1726189854_E.tar.gz'})

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testerb')),
                             {'nvlu.package.info', 'idle.status', '8001_1726189853_F.tar.gz'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'),
                             ['8002_9726189852_F.tar.gz.remote'])

            self.assertEqual(os.listdir(f'{tdir}/pool/nvls'),
                             ['8002_9726189853_F.tar.gz.remote'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'9726189852_F.json',
                              '9726189853_F.json',
                              '1726189853_F.json'     # this is not complete
                              })

            expect = '''
{
    "code": 0,
    "pkg": "",
    "email": "",
    "tester": "JF: testera",
    "url": ""
}'''
            self.assertTextEqual(File(f'{tdir}/completed/1726189854_E.json').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case2_complete_nometa(self):
        # case2 completed job, but no metadata
        with TempDir(name=True, chdir=True, delete=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            mkdirs(f'{tdir}/staging/_metadata')
            mkdirs(f'{tdir}/completed')
            File(f'{tdir}/completed/9726189853_F.json').touch()      # coverage fix
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)

            remote_staging = {'nvlu': {},
                              'nvls': {}}
            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'idle.status': 1,
                                        '9726189852_F.result.json': 1},
                            'testerb': {'nvls.package.info': 1,
                                        'idle.status': 1,
                                        '9726189853_F.result.json': 1}}
            metafiles = {}

            called = []
            call_arg = defaultdict(list)     # {cmd: [<list_args>]}

            def fake_data_host(slf, cmd, arg, check, urp):
                called.append(cmd)
                call_arg[cmd].append(arg)
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                if cmd == 'read_json':
                    return {'code': 0, 'command': 'done'}
                if cmd == 'write_json':
                    return None
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # expects
            self.assertEqual(obj.job_count, 0)    # nothing gets send
            self.assertEqual(called, ['get_files',
                                      'get_files',
                                      'get_meta_content',
                                      'read_json',
                                      'read_json',
                                      'delete_files'])

            self.assertEqual(os.listdir(f'{tdir}/staging'), ['_metadata'])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(tdir)), {'staging', 'testers', 'pool', 'completed', 'teams', 'tpbot_count'})

            self.assertEqual(set(os.listdir(f'{tdir}/pool')),
                             {'nvlu', '_metadata', 'blah.txt', 'nvls'})

            self.assertEqual(set(os.listdir(f'{tdir}/pool/nvlu')), set())

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')), set())
            self.assertEqual(set(os.listdir(f'{tdir}/completed')), {'9726189853_F.json',
                                                                    '9726189852_F.json'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case2_no_tester(self):
        # case2, 2 jobs same package, no available tester
        with TempDir(name=True, chdir=True, delete=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            mkdirs(f'{tdir}/staging/_metadata')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)

            remote_staging = {'nvlu': {'8002_9726189852_F.tar.gz': 1,
                                       '8002_9726189853_F.tar.gz': 1}}
            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'running.status': 1}}
            metafiles = {'9726189852_F.json': {'site': 'PG'},
                         '9726189853_F.json': {'site': 'PG'}}

            called = []
            call_arg = defaultdict(list)     # {cmd: [<list_args>]}

            def fake_data_host(slf, cmd, arg, check, urp):
                called.append(cmd)
                call_arg[cmd].append(arg)
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                if cmd == 'read_json':
                    return {'code': 0, 'command': 'done'}
                if cmd == 'write_json':
                    return None
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # expects
            self.assertEqual(obj.job_count, 0)    # nothing gets send
            self.assertEqual(called, ['get_files',
                                      'get_files',
                                      'get_meta_content',
                                      'get_files',
                                      'get_files',
                                      'get_meta_content'])

            self.assertEqual(os.listdir(f'{tdir}/staging'), ['_metadata'])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(tdir)), {'staging', 'testers', 'pool', 'teams', 'tpbot_count'})

            self.assertEqual(set(os.listdir(f'{tdir}/pool')),
                             {'nvlu', '_metadata', 'blah.txt'})

            self.assertEqual(set(os.listdir(f'{tdir}/pool/nvlu')),
                             {'8002_9726189852_F.tar.gz.remote',
                              '8002_9726189853_F.tar.gz.remote'})

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'9726189852_F.json',
                              '9726189853_F.json'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case2(self):
        # full run, case2 (2 remote jobs), with 2 testers remote (same site runner and remote)
        # this test case includes deletion of metadata (botos called twice)
        with TempDir(name=True, chdir=True, delete=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            mkdirs(f'{tdir}/staging/_metadata')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)

            remote_staging = {'nvlu': {'8002_9726189852_F.tar.gz': 1,
                                       'blah.txt': 2},
                              'nvls': {'8002_9726189853_F.tar.gz': 1}}
            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'idle.status': 1},
                            'testerb': {'nvls.package.info': 1,
                                        'idle.status': 1}}
            metafiles = {'9726189852_F.json': {'site': 'PG'},
                         '9726189853_F.json': {'site': 'PG'}}

            called = []
            call_arg = defaultdict(list)     # {cmd: [<list_args>]}

            def fake_data_host(slf, cmd, arg, check, urp):
                called.append(cmd)
                call_arg[cmd].append(arg)
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                if cmd == 'read_json':
                    return {'code': 0, 'command': 'done'}
                if cmd == 'write_json':
                    return None
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # expects
            self.assertEqual(obj.job_count, 2)
            self.assertEqual(called, ['get_files',
                                      'get_files',
                                      'get_meta_content',
                                      'move_job',
                                      'delete_files',     # this is staging/_metadata/.json
                                      'move_job',
                                      'delete_files',     # this is staging/_metadata/.json
                                      ])

            expect = {'delete_files': [[f'{tdir}/staging/_metadata/9726189853_F.json'],
                                       [f'{tdir}/staging/_metadata/9726189852_F.json']],
                      'get_files': [True, False],
                      'get_meta_content': [None],
                      'move_job': [('nvls', '8002_9726189853_F.tar.gz', 'testerb'),
                                   ('nvlu', '8002_9726189852_F.tar.gz', 'testera')]}
            self.assertEqual(call_arg, expect)

            self.assertEqual(os.listdir(f'{tdir}/staging'), ['_metadata'])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(tdir)), {'staging', 'testers', 'pool', 'teams', 'tpbot_count'})

            self.assertEqual(set(os.listdir(f'{tdir}/pool')),
                             {'nvlu', '_metadata', 'blah.txt', 'nvls'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/pool/nvls'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'9726189852_F.json',
                              '9726189853_F.json'})

            # at this point, the job is to the tester and the tester is running
            # let see if it deletes the _metadata

            remote_staging = {'nvlu': {},
                              'nvls': {}}
            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'idle.status': 1,
                                        '9726189852_F.result.json': 1},
                            'testerb': {'nvls.package.info': 1,
                                        'idle.status': 1,
                                        '9726189853_F.result.json': 1}}
            metafiles = {}

            with MockVar(DataHost, 'central', fake_data_host):
                called = []
                call_arg = defaultdict(list)
                obj.job_count = 0
                obj.main_one_run()

            self.assertEqual(obj.job_count, 0)
            self.assertEqual(called, ['get_files',
                                      'get_files',
                                      'get_meta_content',
                                      'read_json',   # first tester
                                      'write_json',
                                      'read_json',   # second tester
                                      'write_json',
                                      'delete_files'])

            # make sure _metadata folder is empty
            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')), set())

            # print(pformat(call_arg).replace(tdir, '{tdir}'))
            expect = {'get_files': [True, False],
                      'get_meta_content': [None],
                      'delete_files': [[f'{tdir}/testers/testera/9726189852_F.result.json',
                                        f'{tdir}/testers/testerb/9726189853_F.result.json']],
                      'read_json': [f'{tdir}/testers/testera/9726189852_F.result.json',
                                    f'{tdir}/testers/testerb/9726189853_F.result.json'],
                      'write_json': [({'code': 0, 'command': 'done', 'email': '', 'pkg': '', 'tester': 'PG: testera', 'url': ''},
                                      '9726189852_F.json',
                                      f'{tdir}/completed'),
                                     ({'code': 0, 'command': 'done', 'email': '', 'pkg': '', 'tester': 'PG: testerb', 'url': ''},
                                      '9726189853_F.json',
                                      f'{tdir}/completed')]}
            # pprint(call_arg)
            self.assertEqual(call_arg, expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case5(self):
        # 1 folsom tester and 1 penang runner
        # run twice
        two_sites = {'PG': 'Some penang stuff',
                     'FM': 'Some folsom stuff'}
        with TempDir(name=True, chdir=True, delete=True) as tdir, \
                MockVar(Remote, '_SITES', two_sites), \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            mkdirs(f'{tdir}/staging/_metadata')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)

            remote_staging_pg = {'nvlu': {'8002_9726189852_F.tar.gz': 1}}
            tester_files_fm = {'testera': {'nvlu.package.info': 1,
                                           'idle.status': 1}}
            metafiles_pg = {'9726189852_F.json': {'blahkey1': 'blahvalue1'}}

            called = []

            def fake_data_host(slf, cmd, arg, check, urp):
                if urp == 'Some penang stuff':
                    if cmd == 'get_files' and arg:
                        called.append('get_files_with_arg pg')
                        return remote_staging_pg
                    if cmd == 'get_files' and (not arg):
                        called.append('get_files_no_arg pg')
                        return {}
                    if cmd == 'get_meta_content':
                        called.append('get_meta_content pg')
                        return metafiles_pg
                    if cmd == 'delete_files':
                        called.append('delete_files pg')
                        return 'datahost says Success'
                else:
                    # FM at this point
                    if cmd == 'get_files' and arg:
                        called.append('get_files_with_arg fm')
                        return {}
                    if cmd == 'get_files' and (not arg):
                        called.append('get_files_no_arg fm')
                        return tester_files_fm
                    if cmd == 'get_meta_content':
                        called.append('get_meta_content fm')
                        return {}
                    if cmd == 'delete_files':
                        called.append('delete_files fm')
                        return 'datahost says Success'

                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            def fake_file(command, *args, **kwargs):
                called.append(command)

            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 1)

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])
            self.assertEqual(called, ['get_files_with_arg pg', 'get_files_with_arg fm',
                                      'get_files_no_arg pg', 'get_files_no_arg fm',
                                      'get_meta_content pg', 'get_meta_content fm',
                                      'another_remote', 'delete_files pg'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')), {'9726189852_F.json'})

            # run again - should be same set of files
            called = []
            obj.job_count = 0
            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 1)

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])
            self.assertEqual(called, ['get_files_with_arg pg', 'get_files_with_arg fm',
                                      'get_files_no_arg pg', 'get_files_no_arg fm',
                                      'get_meta_content pg', 'get_meta_content fm',
                                      'another_remote', 'delete_files pg'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')), {'9726189852_F.json'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case1and2(self):
        # full run, case1 and case2:
        # 1 job local, 1 job remote, 2 testers: one remote, one local
        # The local job goto local tester, remote job goto remote tester
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/staging/nvlu/8000_1726189854_E.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189854_E.json').touch('{"site": "PG"}', mkdir=True)
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch(mkdir=True)

            remote_staging = {'nvlu': {'8002_9726189852_F.tar.gz': 1}}
            tester_files = {'testerb': {'nvlu.package.info': 1,
                                        'idle.status': 1}}
            metafiles = {'9726189852_F.json': {'site': 'PG'}}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                if cmd == 'read_json':
                    return {'code': 0, 'command': 'done'}
                if cmd == 'write_json':
                    return None
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 2)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status', '8000_1726189854_E.tar.gz'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'1726189854_E.json',
                              '9726189852_F.json'
                              })

            # let see if it deletes the _metadata, once both testers are done
            File(f'{tdir}/testers/testera/8000_1726189854_E.tar.gz').unlink()
            File(f'{tdir}/testers/testera/1726189854_E.result.json').touch('{}')
            remote_staging = {'nvlu': {}}
            tester_files = {'testerb': {'nvlu.package.info': 1,
                                        'idle.status': 1,
                                        '9726189852_F.result.json': 1}}
            metafiles = {}

            # Run again to get the result.json and delete it
            with MockVar(DataHost, 'central', fake_data_host):
                obj.job_count = 0
                obj.main_one_run()

            self.assertEqual(obj.job_count, 0)
            # make sure _metadata folder is empty
            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')), set())
            # make sure tester's result.json is deleted
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')), {'nvlu.package.info', 'idle.status'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case4(self):
        # 2 job remote, 2 testers local
        # first try is send() fail, then do 2nd try

        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch(mkdir=True)
            File(f'{tdir}/testers/testerb/nvls.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testerb/idle.status').touch(mkdir=True)
            mkdirs(f'{tdir}/staging/_metadata')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)

            remote_staging = {'nvlu': {'8002_9726189852_F.tar.gz': 1},
                              'nvls': {'8002_9726189853_F.tar.gz': 1}}
            tester_files = {}
            metafiles = {'9726189852_F.json': {'blahkey1': 'blahvalue1'},
                         '9726189853_F.json': {'blahkey2': 'blahvalue2'}}
            called = []

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            def fake_file(command, *args, **kwargs):
                called.append(command)

            # first try - send failed
            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')), \
                    MockVar(obj, 'send', Mock(side_effect=Exception)):
                obj.main_one_run()

            # second try - success
            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 2)
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status'})    # the tar file is here, but we mocked it
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testerb')),
                             {'nvls.package.info', 'idle.status'})    # the tar file is here, but we mocked it

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/pool/nvls'), [])

            self.assertEqual(called, ['copy_remote', 'copy_remote'])    # because there are 2 jobs

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'9726189853_F.json',
                              '9726189852_F.json'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case3(self):
        # 2 jobs local, 2 testers remote, send only, no complete-proccessing

        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/staging/nvlu/8000_1726189860_E.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/nvlu/8000_1726189853_F.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189860_E.json').touch('{}', mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189853_F.json').touch('{}')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)

            remote_staging = {}
            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'idle.status': 1},
                            'testerb': {'nvlu.package.info': 1,
                                        'idle.status': 1}}
            metafiles = {'1726189860_E.json': {'blahkey1': 'blahvalue1'},
                         '1726189853_F.json': {'blahkey2': 'blahvalue2'}}
            called = []

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            def fake_file(command, *args, **kwargs):
                called.append(command)

            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 2)
            self.assertEqual(os.listdir(f'{tdir}/staging'), ['nvlu', '_metadata'])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(tdir)), {'staging', 'testers', 'pool', 'teams', 'tpbot_count'})
            self.assertEqual(set(os.listdir(f'{tdir}/pool')),
                             {'nvlu', '_metadata', 'blah.txt'})

            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'idle.status': 1,
                                        '9726189852_F.result.json': 1},
                            'testerb': {'nvlu.package.info': 1,
                                        'idle.status': 1,
                                        '1726189853_F.json': 1}}

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])

            self.assertEqual(called, ['push_remote', 'push_remote'])    # there are 2 jobs

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'1726189860_E.json',
                              '1726189853_F.json'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case3a(self):
        # 1 jobs local, 1 tester remote, send and complete-processing
        # good template to copy
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # local files
            File(f'{tdir}/staging/nvlu/8000_1726189860_E.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189860_E.json').touch('{"site": "JF"}', mkdir=True)
            mkdirs(f'{tdir}/pool')
            mkdirs(f'{tdir}/completed')

            # data host result
            remote_staging = {}
            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'idle.status': 1}}
            metafiles = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                called_dh.append((cmd, arg))
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                if cmd == 'read_json':
                    return {'code': 0, 'command': 'done'}
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            def fake_file(command, *args, **kwargs):
                called.append(command)

            called = []
            called_dh = []
            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 1)
            self.assertEqual(os.listdir(f'{tdir}/staging'), ['nvlu', '_metadata'])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(tdir)), {'staging', 'testers', 'pool', 'completed', 'teams', 'tpbot_count'})
            self.assertEqual(set(os.listdir(f'{tdir}/pool')), {'nvlu', '_metadata'})
            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])
            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')), {'1726189860_E.json'})
            self.assertEqual(called, ['push_remote'])
            self.assertEqual(called_dh, [('get_files', True),
                                         ('get_files', False),
                                         ('get_meta_content', None)])

            tester_files = {'testera': {'nvlu.package.info': 1,
                                        'idle.status': 1,
                                        '1726189860_E.result.json': 1}}

            # 2nd run, completed
            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                called = []
                called_dh = []
                obj.job_count = 0
                obj.main_one_run()

            self.assertEqual(obj.job_count, 0)
            self.assertEqual(called, [])
            self.assertEqual(called_dh, [('get_files', True),
                                         ('get_files', False),
                                         ('get_meta_content', None),
                                         ('read_json', f'{tdir}/testers/testera/1726189860_E.result.json'),
                                         ('delete_files', [f'{tdir}/testers/testera/1726189860_E.result.json'])])
            self.assertEqual(os.listdir(f'{tdir}/completed'), ['1726189860_E.json'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case4a(self):
        # 1 jobs remote, 1 tester local, send and complete-processing
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # local files
            mkdirs(f'{tdir}/staging/nvlu')
            mkdirs(f'{tdir}/staging/_metadata')
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch(mkdir=True)
            mkdirs(f'{tdir}/pool')
            mkdirs(f'{tdir}/completed')

            # data host result
            remote_staging = {'nvlu': {'8002_9726189852_F.tar.gz': 1}}
            tester_files = {}
            metafiles = {'9726189852_F.json': {'site': 'PG'}}

            def fake_data_host(slf, cmd, arg, check, urp):
                called_dh.append((cmd, arg))
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                if cmd == 'move_job':
                    return True
                if cmd == 'delete_files':
                    return 'datahost says Success'
                if cmd == 'write_json':
                    return
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            def fake_file(command, *args, **kwargs):
                called.append(command)

            called = []
            called_dh = []
            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 1)
            self.assertEqual(os.listdir(f'{tdir}/staging'), ['nvlu', '_metadata'])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(tdir)), {'staging', 'testers', 'pool', 'completed', 'teams', 'tpbot_count'})
            self.assertEqual(set(os.listdir(f'{tdir}/pool')), {'nvlu', '_metadata'})
            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])
            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')), {'9726189852_F.json'})
            self.assertEqual(called, ['copy_remote'])
            self.assertEqual(called_dh, [('get_files', True),
                                         ('get_files', False),
                                         ('get_meta_content', None),
                                         ('delete_files', [f'{tdir}/staging/nvlu/8002_9726189852_F.tar.gz',
                                                           f'{tdir}/staging/_metadata/9726189852_F.json'])])

            # 2nd run, completed
            remote_staging = {}
            tester_files = {}
            metafiles = {}
            File(f'{tdir}/testers/testera/9726189852_F.result.json').touch('{"code": 0}')
            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'push_remote', partial(fake_file, 'push_remote')), \
                    MockVar(File, 'copy_remote', partial(fake_file, 'copy_remote')), \
                    MockVar(File, 'another_remote', partial(fake_file, 'another_remote')):
                called = []
                called_dh = []
                obj.job_count = 0
                obj.main_one_run()

            self.assertEqual(obj.job_count, 0)
            self.assertEqual(called, [])
            self.assertEqual(called_dh, [('get_files', True),
                                         ('get_files', False),
                                         ('get_meta_content', None),
                                         ('write_json', ({'code': 0, 'email': '', 'pkg': '', 'tester': 'JF: testera', 'url': ''},
                                                         '9726189852_F.json',
                                                         f'{tdir}/completed'))])
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status'})
            self.assertEqual(os.listdir(f'{tdir}/completed'), [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case1a(self):
        # case: 2 jobs local, 2 testers local and 1 tester is running (busy), so pool is left with 1 local job
        # case: remote tar.gz but no metadata, will not be added in pool
        # case: a file in staging/ instead of a folder
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/staging/nvlu/8000_1726189854_E.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/nvlu/8001_1726189853_F.tar.gz').touch()
            File(f'{tdir}/staging/blah.txt').touch()
            File(f'{tdir}/staging/_metadata/1726189854_E.json').touch('{}', mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189853_F.json').touch('{}')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch()
            File(f'{tdir}/testers/testera/type1.info').touch()
            File(f'{tdir}/testers/testerb/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testerb/running.status').touch()
            File(f'{tdir}/testers/testerb/type1.info').touch()

            remote_staging = {'nvls': {'8002_9726189853_F.tar.gz': 1}}
            tester_files = {}
            metafiles = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # Expects- Check the staging, tester and pool
            self.assertEqual(obj.job_count, 1)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status', '8000_1726189854_E.tar.gz', 'type1.info'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'),
                             ['8001_1726189853_F.tar.gz'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'1726189854_E.json',
                              '1726189853_F.json'
                              })

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case1b(self):
        # Full run, case1b:
        # 2 jobs local, 1 local tester, but not available: The 2 local jobs are in the queue in the pool
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/staging/nvlu/8000_1726189854_E.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/nvlu/8001_1726189853_F.tar.gz').touch()
            File(f'{tdir}/staging/_metadata/1726189854_E.json').touch('{}', mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189853_F.json').touch('{}')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/running.status').touch()
            File(f'{tdir}/testers/testera/8003_1726189890_E.tar.gz').touch()

            remote_staging = {}
            tester_files = {}
            metafiles = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # Expects- Check the staging, tester and pool
            self.assertEqual(obj.job_count, 0)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'running.status', '8003_1726189890_E.tar.gz'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'),
                             ['8000_1726189854_E.tar.gz',
                              '8001_1726189853_F.tar.gz'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'1726189854_E.json',
                              '1726189853_F.json'
                              })

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case1c(self):
        # case: teambots only tester
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/staging/nvlu/8000_1726189854_D.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/nvlu/8001_1726189853_D.tar.gz').touch()
            File(f'{tdir}/staging/nvlu/7999_1726189855_B.tar.gz').touch()
            File(f'{tdir}/staging/blah.txt').touch()
            File(f'{tdir}/staging/_metadata/1726189854_D.json').touch('{}', mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189853_D.json').touch('{}')
            File(f'{tdir}/staging/_metadata/1726189855_B.json').touch('{}')
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch()
            File(f'{tdir}/testers/testera/teambotonly.info').touch()
            File(f'{tdir}/testers/testerb/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testerb/idle.status').touch()
            File(f'{tdir}/testers/testerb/type1.info').touch()

            remote_staging = {'nvls': {'8002_9726189853_E.tar.gz': 1}}
            tester_files = {}
            metafiles = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # Expects- Check the staging, tester and pool
            self.assertEqual(obj.job_count, 2)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status', '8000_1726189854_D.tar.gz', 'teambotonly.info'})
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testerb')),
                             {'nvlu.package.info', 'idle.status', '7999_1726189855_B.tar.gz', 'type1.info'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'),
                             ['8001_1726189853_D.tar.gz'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'1726189854_D.json',
                              '1726189853_D.json',
                              '1726189855_B.json'
                              })

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_type1(self):
        # case1 with a type1 tester and a teambots jobs, job should not be submitted
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            File(f'{tdir}/staging/nvlu/8000_1726189854_D.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189854_D.json').touch('{}', mkdir=True)
            File(f'{tdir}/pool/blah.txt').touch(mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch()
            File(f'{tdir}/testers/testera/type1.info').touch()

            remote_staging = {'nvls': {'8002_9726189853_D.tar.gz': 1}}
            tester_files = {}
            metafiles = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            # Expects- Check the staging, tester and pool
            self.assertEqual(obj.job_count, 0)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/staging/_metadata'), [])

            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status', 'type1.info'})

            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'),
                             ['8000_1726189854_D.tar.gz'])

            self.assertEqual(set(os.listdir(f'{tdir}/pool/_metadata')),
                             {'1726189854_D.json'
                              })

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_ut_send_email_teambot(self):
        # check send_email_teambot() for remote case
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            for_delete = {'JF': []}
            with MockVar(obj, 'email_now', Mock()):
                obj.send_email_teambot('email1.8000_1726189890_E.json', False, ('JF', 'tester1'), for_delete)
                self.assertEqual(for_delete, {'JF': [f'{tdir}/testers/tester1/email1.8000_1726189890_E.json']})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case_email_mbot(self):
        # checks the email mbot
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            mkdirs(f'{tdir}/staging')
            mkdirs(f'{tdir}/completed')
            File(f'{tdir}/pool/_metadata/1726189890_E.json').touch('{"email": "jdr@intel"}', mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/running.status').touch()
            File(f'{tdir}/testers/testera/1726189890_E.result.json').touch('''{
"site": "JF",
"logfile": "/blah/11-17-28/1_1_B.txt",
"INIT log": "/blah/11-17-28/loadlog_11_17.txt",
"tprolling": "/tprol",
"code": 0
}
''')

            remote_staging = {}
            tester_files = {}
            metafiles = {}
            called = []

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            def fake_email(*args):
                called.append(args)

            with MockVar(DataHost, 'central', fake_data_host),\
                    MockVar(ManagerBotOS, '_is_ut_email', False),\
                    MockVar(manager_botos, 'send_mail', fake_email):
                obj.main_one_run()

            print('From:', called[0][0])
            print('To:', called[0][1])
            print('Subject:', called[0][2])
            print('Text:\n', called[0][3])
            self.assertEqual(called[0][1], 'jdr@intel')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_case_email_teambot(self):
        # checks the email teambot
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # inputs
            mkdirs(f'{tdir}/staging')
            mkdirs(f'{tdir}/completed')
            File(f'{tdir}/pool/_metadata/1726189890_E.json').touch('{"email": "jdr@intel"}', mkdir=True)
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/running.status').touch()
            File(f'{tdir}/testers/testera/email1.1726189890_E.command').touch()

            remote_staging = {}
            tester_files = {}
            metafiles = {}
            called = []

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return metafiles
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            def fake_email(*args):
                called.append(args)

            with MockVar(DataHost, 'central', fake_data_host),\
                    MockVar(ManagerBotOS, '_is_ut_email', False),\
                    MockVar(manager_botos, 'send_mail', fake_email):
                obj.main_one_run()

            print('From:', called[0][0])
            print('To:', called[0][1])
            print('Subject:', called[0][2])
            print('Text:\n', called[0][3])
            self.assertEqual(called[0][0:3], ('frombot',
                                              'jdr@intel',
                                              'teambot job is ready: 1726189890_E'))


class TestManager(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mainentry(self):
        with MockVar(sys, 'argv', ['.py', 'start']):
            with MockVar(CheckerLog, 'setup', Mock()):
                with MockVar(ManagerBotOS, 'main', Mock()):
                    res = ManagerEntry().main()
        self.assertEqual(res, 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_maincheck(self):
        with MockVar(sys, 'argv', ['.py', '-check', 'JF']):
            with self.assertRaisesRegex(ValueError, 'too many values to unpack'):
                ManagerEntry().main()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_quit(self):
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()
            File(f'{tdir}/pool/_metadata/quit').touch(mkdir=True)
            with self.assertRaises(SystemExit):
                obj.check_quit()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_exception_metadata(self):
        # Exception occurred during metadata copy
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # setups
            File(f'{tdir}/staging/nvlu/8000_1726189854_E.tar.gz').touch(mkdir=True)
            File(f'{tdir}/staging/_metadata/1726189854_E.json').touch('{}', mkdir=True)
            mkdirs(f'{tdir}/pool/nvlu')
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch(mkdir=True)

            remote_staging = {}
            tester_files = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return {}
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host), \
                    MockVar(File, 'copy', Mock(side_effect=Exception)):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 1)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), [])
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status', '8000_1726189854_E.tar.gz'})
            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_missing_metadata1(self):
        # missing metadata in staging
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # setups
            File(f'{tdir}/staging/nvlu/8000_1726189854_E.tar.gz').touch(mkdir=True)
            mkdirs(f'{tdir}/pool/nvlu')
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch(mkdir=True)

            remote_staging = {}
            tester_files = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return {}
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 0)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), ['8000_1726189854_E.tar.gz'])
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status'})
            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_missing_metadata2(self):
        # missing metadata during tester run
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # setups
            File(f'{tdir}/staging/nvlu/readme').touch(mkdir=True)
            mkdirs(f'{tdir}/pool/nvlu')
            mkdirs(f'{tdir}/completed')
            File(f'{tdir}/testers/testera/nvlu.package.info').touch(mkdir=True)
            File(f'{tdir}/testers/testera/idle.status').touch(mkdir=True)
            File(f'{tdir}/testers/testera/1726189854_E.result.json').touch('{"code": 0}')

            remote_staging = {}
            tester_files = {}

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'get_files' and arg:
                    return remote_staging
                if cmd == 'get_files' and (not arg):
                    return tester_files
                if cmd == 'get_meta_content':
                    return {}
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.main_one_run()

            self.assertEqual(obj.job_count, 0)
            self.assertEqual(os.listdir(f'{tdir}/staging/nvlu'), ['readme'])
            self.assertEqual(set(os.listdir(f'{tdir}/testers/testera')),
                             {'nvlu.package.info', 'idle.status'})
            self.assertEqual(os.listdir(f'{tdir}/pool/nvlu'), [])
            self.assertEqual(os.listdir(f'{tdir}/completed'), ['1726189854_E.json'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_process_available(self):
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            data = {'testera': {'nvlu.package.info': 1,     # idle - ok
                                'idle.status': 1},
                    'testerb': {'nvlu.package.info': 1,     # busy
                                'running.status': 1,
                                'arr.team': 1},
                    'testerc': {'nvlS.package.info': 1,     # wrong package
                                'idle.status': 1},
                    'testerd': {'nvlu.package.info': 1,     # too much idle
                                'idle.status': 1000},
                    'testere': {'nvlu.package.info': 1,     # with tar.gz
                                'idle.status': 1,
                                'abc.tar.gz': 1},
                    'testerf': {'nvlu.package.info': 1,     # idle - ok
                                'idle.status': 1},
                    'testerg': {'nvlu.package.info': 1,     # stop
                                'stop': 1,
                                'idle.status': 1},
                    'testerh': {'nvlu.package.info': 1,     # down
                                'down': 1,
                                'idle.status': 1},
                    'testerk': {'nvlu.package.info': 1,     # reserved
                                'reserved': 1,
                                'idle.status': 1},
                    'testerm': {'nvlu.package.info': 1,     # tpbot type
                                'type1.info': 1,
                                'idle.status': 1},
                    'testern': {'nvlu.package.info': 1,     # teambot type
                                'teambotonly.info': 1,
                                'idle.status': 1}
                    }

            available = {'existing': 1}
            physical = {}
            obj._process_available(available, True, 'nvlu', data, physical)
            pprint(available)
            self.assertEqual(available, {'existing': 1,
                                         (True, 'testera'): 2,
                                         (True, 'testerf'): 2,
                                         (True, 'testerm'): 1,
                                         (True, 'testern'): 3})
            pprint(physical)
            self.assertEqual(physical, {('JF', 'nvlu'): {'testera': '',
                                                         'testerb': 'arr',
                                                         'testere': '',
                                                         'testerf': '',
                                                         'testerm': 'tpbot',
                                                         'testern': ''}})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_sorted_top_job_teambot(self):

        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir
            pkg = 'aa'
            mkdirs(f'{tdir}/pool/{pkg}')
            File(f'{tdir}/pool/{pkg}/8000_1725545090_D.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545087_D.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/7980_1725545088_D.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545089_D.tar.gz.remote').touch()

            # normal case
            obj.all_meta = {'1725545087_D.json': {'team': 'arr'},
                            '1725545088_D.json': {'team': 'scn'}}

            # job match team
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='abc', team='arr'),
                             '8000_1725545087_D.tar.gz')   # arr job

            # tester is empty
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='abc', team=''),
                             '7980_1725545088_D.tar.gz')   # top job

            # top job match team
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='abc', team='scn'),
                             '7980_1725545088_D.tar.gz')   # top job

            # job has no team
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='abc', team='fun'),
                             '8000_1725545089_D.tar.gz.remote')

            # no empty
            obj.all_meta = {'1725545087_D.json': {'team': 'arr'},
                            '1725545088_D.json': {'team': 'scn'},
                            '1725545089_D.json': {'team': 'fun'},
                            '1725545090_D.json': {'team': 'tpi'},
                            }
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='abc', team='fun'),
                             '8000_1725545089_D.tar.gz.remote')    # matched
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='abc', team='tpi'),
                             '8000_1725545090_D.tar.gz')   # matched
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='abc', team=''),
                             '7980_1725545088_D.tar.gz')   # top job

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_sorted_top_job_tester(self):

        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir
            pkg = 'aa'
            mkdirs(f'{tdir}/pool/{pkg}')
            File(f'{tdir}/pool/{pkg}/8000_1725545090_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545087_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/7980_1725545088_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545089_A.tar.gz.remote').touch()
            File(f'{tdir}/pool/{pkg}/blah.txt').touch()

            # normal case
            obj.all_meta = {}
            self.assertEqual(obj.sorted_top_job(pkg, tester='abc'), '7980_1725545088_A.tar.gz')   # top job

            # tester does not match a job
            obj.all_meta = {'1725545087_A.json': {'tester': 'ABC'}}
            self.assertEqual(obj.sorted_top_job(pkg, tester='GHI'), '7980_1725545088_A.tar.gz')   # top job
            self.assertEqual(obj.sorted_top_job(pkg, tester='abc'), '8000_1725545087_A.tar.gz')   # tester match a job

            # top job has a tester - not match
            obj.all_meta = {'1725545088_A.json': {'tester': 'ABC'}}
            self.assertEqual(obj.sorted_top_job(pkg, tester='GHI'), '8000_1725545087_A.tar.gz')
            self.assertEqual(obj.sorted_top_job(pkg, tester='abc'), '7980_1725545088_A.tar.gz')    # top job

            # top job has a tester - remote
            obj.all_meta = {'1725545088_A.json': {'tester': 'ABC'}}
            self.assertEqual(obj.sorted_top_job(pkg, tester=(None, 'GHI')), '8000_1725545087_A.tar.gz')
            self.assertEqual(obj.sorted_top_job(pkg, tester=(None, 'abc')), '7980_1725545088_A.tar.gz')   # top job

            # top job has a negative tester
            obj.all_meta = {'1725545088_A.json': {'tester': '!ABC'}}
            self.assertEqual(obj.sorted_top_job(pkg, tester='abc'), '8000_1725545087_A.tar.gz')
            self.assertEqual(obj.sorted_top_job(pkg, tester='ghi'), '7980_1725545088_A.tar.gz')    # top job

            # top job has a tester
            File(f'{tdir}/pool/{pkg}/7980_1725545091_D.tar.gz').touch()
            obj.all_meta = {'1725545091_D.json': {'tester': 'ABC'}}
            self.assertEqual(obj.sorted_top_job(pkg, tester='ABC'), '7980_1725545091_D.tar.gz')
            self.assertEqual(obj.sorted_top_job(pkg, testertype=1, tester='ABC'), '7980_1725545088_A.tar.gz')
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='ABC'), '7980_1725545091_D.tar.gz')

            # two top jobs cannot be picked since tester is a type1
            obj.all_meta = {'1725545088_A.json': {'tester': '!ABC'}}
            self.assertEqual(obj.sorted_top_job(pkg, testertype=1, tester='ABC'), '8000_1725545087_A.tar.gz')
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='ABC'), '7980_1725545091_D.tar.gz')

            # tester type 3
            File(f'{tdir}/pool/{pkg}/7980_1725545091_D.tar.gz').unlink()
            File(f'{tdir}/pool/{pkg}/7980_1725545091_B.tar.gz').touch()
            obj.all_meta = {'1725545091_B.json': {'tester': 'ABC'}}
            self.assertEqual(obj.sorted_top_job(pkg, tester='ABC'), '7980_1725545091_B.tar.gz')
            self.assertEqual(obj.sorted_top_job(pkg, testertype=3, tester='ABC'), None)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_sorted_top_job(self):
        # timestamp case
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir
            pkg = 'aa'
            mkdirs(f'{tdir}/pool/{pkg}')
            File(f'{tdir}/pool/{pkg}/8000_1725545090_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545087_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/7980_1725545088_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545089_A.tar.gz.remote').touch()
            File(f'{tdir}/pool/{pkg}/blah.txt').touch()

            # Test the sort routine
            result = list(sorted(os.listdir(f'{obj.root}/pool/{pkg}'), key=partial(obj._sort_routine, 2)))
            self.assertEqual(result, ['7980_1725545088_A.tar.gz',
                                      '8000_1725545087_A.tar.gz',
                                      '8000_1725545089_A.tar.gz.remote',
                                      '8000_1725545090_A.tar.gz',
                                      'blah.txt'])

            job = obj.sorted_top_job(pkg)
            self.assertEqual(job, '7980_1725545088_A.tar.gz')

            job = obj.sorted_top_job(pkg, testertype=3)
            self.assertEqual(job, None)     # no match since testertype 3 is teambot

        # empty cases
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir
            pkg = 'aa'
            mkdirs(f'{tdir}/pool/{pkg}')
            self.assertEqual(obj.sorted_top_job(pkg), None)    # No job

            File(f'{tdir}/pool/{pkg}/blah.txt').touch()
            self.assertEqual(obj.sorted_top_job(pkg), None)    # junk only

        # letter case
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir
            pkg = 'aa'
            mkdirs(f'{tdir}/pool/{pkg}')
            File(f'{tdir}/pool/{pkg}/8000_1725545090_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545092_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/7990_1725545093_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545090_D.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545090_B.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545091_A.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545090_C.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/7980_1725545091_B.tar.gz').touch()

            # type 2
            result = list(sorted(os.listdir(f'{obj.root}/pool/{pkg}'), key=partial(obj._sort_routine, 2)))
            self.assertEqual(result, ['8000_1725545090_D.tar.gz',
                                      '7990_1725545093_A.tar.gz',
                                      '8000_1725545090_A.tar.gz',
                                      '8000_1725545091_A.tar.gz',
                                      '8000_1725545092_A.tar.gz',
                                      '7980_1725545091_B.tar.gz',
                                      '8000_1725545090_B.tar.gz',
                                      '8000_1725545090_C.tar.gz',
                                      ])
            self.assertEqual(obj.sorted_top_job(pkg, 2), '8000_1725545090_D.tar.gz')

            # type 1
            result = list(sorted(os.listdir(f'{obj.root}/pool/{pkg}'), key=partial(obj._sort_routine, 1)))
            self.assertEqual(result, ['7990_1725545093_A.tar.gz',
                                      '8000_1725545090_A.tar.gz',
                                      '8000_1725545091_A.tar.gz',
                                      '8000_1725545092_A.tar.gz',
                                      '7980_1725545091_B.tar.gz',
                                      '8000_1725545090_B.tar.gz',
                                      '8000_1725545090_C.tar.gz',
                                      '8000_1725545090_D.tar.gz',
                                      ])
            self.assertEqual(obj.sorted_top_job(pkg, 1), '7990_1725545093_A.tar.gz')

        # type 1, ignore the D
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir
            pkg = 'aa'
            mkdirs(f'{tdir}/pool/{pkg}')
            File(f'{tdir}/pool/{pkg}/8000_1725545090_E.tar.gz').touch()
            File(f'{tdir}/pool/{pkg}/8000_1725545090_D.tar.gz').touch()

            result = list(sorted(os.listdir(f'{obj.root}/pool/{pkg}'), key=partial(obj._sort_routine, 1)))
            self.assertEqual(result, ['8000_1725545090_D.tar.gz',
                                      '8000_1725545090_E.tar.gz',
                                      ])
            self.assertEqual(obj.sorted_top_job(pkg, 1), '8000_1725545090_E.tar.gz')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_main(self):

        def fake():
            obj.job_count += 1

        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            with MockVar(sys, 'argv', ['.py', 'start']):
                with MockVar(obj, 'main_one_run', Mock()):
                    obj.main(maxloop=2, sleeptime=.0001)

                File(f'{obj.root}/{obj.idfile}').unlink()
                with MockVar(obj, 'main_one_run', fake):
                    obj.main(maxloop=2, sleeptime=.0001)

                # check that it fails if id already exist
                with MockVar(obj, 'main_one_run', fake):
                    with self.assertRaisesRegex(ErrorUser, 'already exist. manager seems to be running.'):
                        obj.main(maxloop=1, sleeptime=.0001)

            with MockVar(OPT, 'force', True):
                with MockVar(obj, 'main_one_run', fake):
                    obj.main(maxloop=1, sleeptime=.0001)

            # No args, print help
            # with MockVar(sys, 'argv', ['.py']):
            #     self.assertEqual(obj.main(), 0)

            # something went wrong
            File(f'{obj.root}/{obj.idfile}').unlink()
            with MockVar(sys, 'argv', ['.py', 'start']):
                with MockVar(obj, 'main_one_run', Mock(side_effect=Exception)):
                    self.assertEqual(obj.main(1, 0), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_move_job(self):
        with TempDir(name=True, chdir=True) as tdir:
            infile = f'{tdir}/pool/nvlS/realfile.tar.gz.remote'
            File(infile).touch('PG nvlS realfile.tar.gz', mkdir=True)
            with MockVar(DataHost, 'central', Mock()):
                self.assertEqual(Remote().move_job(infile, 'testera'), ('PG', 'nvlS', 'realfile.tar.gz'))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_cleanup(self):
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            def fake_data_host(slf, cmd, arg, check, urp):
                if cmd == 'cleanup_dir' and arg:
                    return ['hey']
                raise Exception(f'Unknown command in fake_data_host: {cmd}')

            with MockVar(DataHost, 'central', fake_data_host):
                obj.cleanup_last = 0
                result = obj.cleanup()

            self.assertEqual(result, ['PG hey'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_send_other(self):
        # job is None
        # job_pkg != pkg on case2
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            pkg = 'nvlu'
            job = '1_121_F.tar.gz.remote'

            # setup
            File(f'{obj.root}/pool/{pkg}/{job}').touch('PG nvlS realfile.tar.gz', mkdir=True)
            mkdirs(f'{obj.root}/testers/testera')

            local_tester = (False, ('PG', 'testera'))
            with MockVar(obj.remote, 'move_job', Mock()), \
                    MockVar(obj.remote, 'delete_files', Mock()):
                self.assertEqual(obj.send(None, local_tester, pkg), None)
                obj.send(job, local_tester, pkg)

            self.assertEqual(os.listdir(f'{obj.root}/testers/testera'), [])
            self.assertEqual(os.listdir(f'{obj.root}/pool/{pkg}'), [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_send_case1(self):
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            pkg = 'nvlu'
            job = 'a.tar.gz'

            # setup
            File(f'{obj.root}/pool/{pkg}/{job}').touch(mkdir=True)
            mkdirs(f'{obj.root}/testers/testera')

            local_tester = (True, 'testera')
            obj.send(job, local_tester, pkg)

            self.assertEqual(os.listdir(f'{obj.root}/testers/testera'), [job])
            self.assertEqual(os.listdir(f'{obj.root}/pool/{pkg}'), [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_send_case2(self):
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            pkg = 'nvlu'
            job = '1_121_F.tar.gz.remote'

            # setup
            File(f'{obj.root}/pool/{pkg}/{job}').touch('PG nvlu 1_121_F.tar.gz', mkdir=True)
            mkdirs(f'{obj.root}/testers/testera')

            local_tester = (False, ('PG', 'testera'))
            with MockVar(obj.remote, 'move_job', Mock()),\
                    MockVar(obj.remote, 'delete_files', Mock()):
                obj.send(job, local_tester, pkg)

            self.assertEqual(os.listdir(f'{obj.root}/testers/testera'), [])
            self.assertEqual(os.listdir(f'{obj.root}/pool/{pkg}'), [])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_send_case3(self):
        # tester is remote, runner is local
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            pkg = 'nvlu'
            job = 'a.tar.gz'

            # setup
            File(f'{obj.root}/pool/{pkg}/{job}').touch(mkdir=True)

            local_tester = (False, ('PG', 'testera'))
            called = []

            def fake(*args):
                called.append(args)

            with MockVar(File, 'push_remote', fake):
                obj.send(job, local_tester, pkg)

            self.assertEqual(os.listdir(f'{obj.root}/pool/{pkg}'), [])
            self.assertEqual(len(called), 1)     # push_remote is called once

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_send_case4(self):
        # tester is local, runner is remote site
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            pkg = 'nvlu'
            job = '1_121_F.tar.gz.remote'

            # setup
            File(f'{obj.root}/pool/{pkg}/{job}').touch('PG nvlu 1_121_F.tar.gz', mkdir=True)
            mkdirs(f'{obj.root}/testers/testera')

            local_tester = (True, 'testera')
            called = []

            def fake(*args, **kwargs):
                called.append(args)
                return ''

            with MockVar(File, 'copy_remote', fake), \
                    MockVar(DataHost, 'central', fake):
                obj.send(job, local_tester, pkg)

            self.assertEqual(os.listdir(f'{obj.root}/pool/{pkg}'), [])
            self.assertEqual(len(called), 2)     # copy_remote and Datahost is called

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_send_case5(self):
        # tester FM is remote site, runner is remote site PG (different site)
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            pkg = 'nvlu'
            job = '1_121_F.tar.gz.remote'

            # setup
            File(f'{obj.root}/pool/{pkg}/{job}').touch('PG nvlu 1_121_F.tar.gz', mkdir=True)

            local_tester = (False, ('FM', 'testera'))
            called = []

            def fake(*args, **kwargs):
                called.append(args)
                return ''

            with MockVar(File, 'another_remote', fake), \
                    MockVar(DataHost, 'central', fake):
                obj.send(job, local_tester, pkg)

            self.assertEqual(os.listdir(f'{obj.root}/pool/{pkg}'), [])
            self.assertEqual(len(called), 2)     # copy_remote and Datahost is called

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_write_tpbot_count(self):
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            # success case
            file0 = {'idle.status': 1,
                     'pkg1.package.info': 1,
                     'type1.info': 1}
            file1 = {'idle.status': 1,
                     'pkg2.package.info': 1,
                     'type1.info': 1}
            file2 = {'idle.status': 1,
                     'pkg1.package.info': 1}
            file3 = {'occupied.status': 1,
                     'pkg1.package.info': 1,
                     'type1.info': 1}
            file4 = {'idle.status': 100000,
                     'pkg1.package.info': 1,
                     'type1.info': 1}
            file5 = {'idle.status': 1,
                     'pkg1.package.info': 1,
                     'type1.info': 1,
                     'down': 1}
            file6 = {'idle.status': 1,
                     'pkg1.package.info': 1,
                     'type1.info': 1,
                     'reserved': 1}
            res = obj.write_tpbot_count('pkg1', {}, {'tester0': file0,
                                                     'tester1': file1,
                                                     'tester2': file2,
                                                     'tester3': file3,
                                                     'tester4': file4,
                                                     'tester5': file5,
                                                     'tester6': file6
                                                     })
            self.assertEqual(File(f'{tdir}/tpbot_count/pkg1').read(), '1\n')
            self.assertEqual(res, -1)

            # 2nd run
            res = obj.write_tpbot_count('pkg1', {}, {'tester0': file0})
            self.assertEqual(res, 1)

            # exception case
            File(f'{tdir}/tpbot_count/pkg1').touch('', newfile=True)
            res = obj.write_tpbot_count('pkg1', {}, {'tester0': file0})
            self.assertEqual(res, -1)
            self.assertEqual(File(f'{tdir}/tpbot_count/pkg1').read().strip(), '1')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_all_metadata(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('a.json').touch('{ "key": 1}')
            File('b.json').touch('{ "key": 2}')
            File('c.txt').touch('blah')

            obj = ManagerBotOS()

            # initial read
            cnt = obj.read_all_metadata(tdir)
            self.assertEqual(cnt, 2)
            self.assertEqual(obj.all_meta, {'a.json': {'key': 1}, 'b.json': {'key': 2}})

            # read again
            cnt = obj.read_all_metadata(tdir)
            self.assertEqual(cnt, 0)
            self.assertEqual(obj.all_meta, {'a.json': {'key': 1}, 'b.json': {'key': 2}})

            # json got deleted
            File('a.json').unlink()
            cnt = obj.read_all_metadata(tdir)
            self.assertEqual(cnt, 0)
            self.assertEqual(obj.all_meta, {'b.json': {'key': 2}})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_teamweight(self):
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir
            File(f'{tdir}/teams/arr.1.txt').touch(mkdir=True)
            File(f'{tdir}/teams/scn.2.txt').touch()
            File(f'{tdir}/teams/pth.txt').touch()
            File(f'{tdir}/teams/unknown.ppt').touch()
            obj.read_teamweight()
            self.assertEqual(obj.teamweight, {'arr': 1, 'scn': 2})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_sorted_tester_teams(self):
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            testers = {(True, 'tester1'): 1,
                       (False, 'tester2'): 1,
                       (True, 'tester3'): 1,
                       (False, 'tester4'): 1,
                       (True, 'tester5'): 1,
                       (False, 'tester6'): 1}

            physical = {(1, 1): {'tester1': '',
                                 'tester3': '',
                                 'tester4': 'arr',
                                 'tester6': 'fun'},
                        (2, 2): {'tester2': '',
                                 'tester5': 'scn'
                                 }}

            self.assertTextEqual(pformat(obj.sorted_tester_teams(testers, physical)), """
[(True, 'tester5'),
 (True, 'tester1'),
 (True, 'tester3'),
 (False, 'tester6'),
 (False, 'tester4'),
 (False, 'tester2')]
""")

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_testerteam(self):
        with TempDir(name=True, chdir=True) as tdir:
            obj = ManagerBotOS()
            obj.root = tdir

            # Basic
            obj.teamweight = {'ARR': 1, 'SCN': 2, 'FUN': 3}
            site_pkg = ('JF', 'nvls')
            physical = {site_pkg: {f'tester{x}': '' for x in range(6)}}
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(True, 'tester0'): 'arr',
 (True, 'tester1'): 'fun',
 (True, 'tester2'): 'fun',
 (True, 'tester3'): 'fun',
 (True, 'tester4'): 'scn',
 (True, 'tester5'): 'scn'}
""")

            # Basic
            site_pkg = ('JF', 'nvls')
            physical = {site_pkg: {f'tester{x}': '' for x in range(7)}}
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(True, 'tester0'): 'arr',
 (True, 'tester1'): 'fun',
 (True, 'tester2'): 'fun',
 (True, 'tester3'): 'fun',
 (True, 'tester4'): 'scn',
 (True, 'tester5'): 'scn',
 (True, 'tester6'): ''}
""")

            # Basic with tester has team
            physical[site_pkg]['tester1'] = 'arr'
            physical[site_pkg]['tester5'] = 'arr'
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(True, 'tester0'): 'fun',
 (True, 'tester1'): 'arr',
 (True, 'tester2'): 'fun',
 (True, 'tester3'): 'fun',
 (True, 'tester4'): 'scn',
 (True, 'tester5'): 'arr',
 (True, 'tester6'): 'scn'}
""")

            # All testers are used by a team
            physical = {site_pkg: {f'tester{x}': 'Arr' for x in range(7)}}
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(True, 'tester0'): 'arr',
 (True, 'tester1'): 'arr',
 (True, 'tester2'): 'arr',
 (True, 'tester3'): 'arr',
 (True, 'tester4'): 'arr',
 (True, 'tester5'): 'arr',
 (True, 'tester6'): 'arr'}
""")

            # Two sites
            physical = {site_pkg: {f'tester{x}': '' for x in [1, 2, 5, 6]}}
            site_pkg2 = ('PG', 'nvls')
            physical[site_pkg2] = {f'tester{x}': '' for x in [0, 3, 4]}
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(False, ('PG', 'tester0')): 'fun',
 (False, ('PG', 'tester3')): 'scn',
 (False, ('PG', 'tester4')): '',
 (True, 'tester1'): 'fun',
 (True, 'tester2'): 'fun',
 (True, 'tester5'): 'scn',
 (True, 'tester6'): ''}
""")

            # one tester only
            obj.teamweight = {'ARR': 1, 'SCN': 2, 'FUN': 3}
            site_pkg = ('JF', 'nvls')
            physical = {site_pkg: {f'tester{x}': '' for x in range(1)}}
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(True, 'tester0'): ''}
""")

            # tpbot
            obj.teamweight = {'ARR': 1, 'SCN': 2, 'FUN': 3}
            site_pkg = ('JF', 'nvls')
            physical = {site_pkg: {f'tester{x}': '' for x in range(6)}}
            physical[site_pkg]['tester0'] = 'tpbot'
            physical[site_pkg]['tester1'] = 'tpbot'
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(True, 'tester0'): 'tpbot',
 (True, 'tester1'): 'tpbot',
 (True, 'tester2'): 'fun',
 (True, 'tester3'): 'fun',
 (True, 'tester4'): 'scn',
 (True, 'tester5'): ''}
""")

            # unknown
            obj.teamweight = {'ARR': 1, 'SCN': 2, 'FUN': 3}
            site_pkg = ('JF', 'nvls')
            physical = {site_pkg: {f'tester{x}': '' for x in range(6)}}
            physical[site_pkg]['tester0'] = 'unknown'
            physical[site_pkg]['tester1'] = 'unknown'
            result = obj.get_testerteam({}, physical)
            self.assertTextEqual(pformat(result), """
{(True, 'tester0'): 'unknown',
 (True, 'tester1'): 'unknown',
 (True, 'tester2'): 'fun',
 (True, 'tester3'): 'fun',
 (True, 'tester4'): 'scn',
 (True, 'tester5'): ''}
""")

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_delete_old_teambot_jobs(self):
        with TempDir(name=True, chdir=True) as tdir, \
                MockVar(BotOS, 'root', tdir):
            obj = ManagerBotOS()

            # this job is not a teambot (do not delete)
            File('pool/nvls28c/8000_1758566404052_E.tar.gz').touch(mkdir=True, mtime=time.time() - 3600)
            File('pool/_metadata/1758566404052_E.json').touch(mkdir=True, mtime=time.time() - 3600)

            # this job is teambot (delete it)
            File('pool/nvls28c/8000_1758566404053_D.tar.gz').touch(mkdir=True, mtime=time.time() - 3600)
            File('pool/_metadata/1758566404053_D.json').touch(mkdir=True, mtime=time.time() - 3600)

            # this job is new
            File('pool/nvls28c/8000_1758566404054_D.tar.gz').touch(mkdir=True)
            File('pool/_metadata/1758566404054_D.json').touch(mkdir=True)

            obj.delete_old_teambot_jobs('nvls28c', _max=1000)

            self.assertEqual(set(os.listdir('pool/nvls28c')), {'8000_1758566404052_E.tar.gz',
                                                               '8000_1758566404054_D.tar.gz'})
            self.assertEqual(set(os.listdir('pool/_metadata')), {'1758566404052_E.json',
                                                                 '1758566404054_D.json'})


class TestRemote(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_nosite(self):
        obj = Remote()

        # move_job
        File('a.txt.remote').touch('PH pkg job')
        with CaptureStdoutLog() as p:
            obj.move_job('a.txt.remote', 'tester')
        self.assertEqual(p.getvalue().strip(), '-i- remote move_job() site not exist: PH pkg job')

        # delete_files
        with CaptureStdoutLog() as p:
            obj.delete_files({'PH': ['/blah']})
        self.assertEqual(p.getvalue().strip(), "-i- remote delete_files() site not exist: PH: ['/blah']")

        # write_json
        with CaptureStdoutLog() as p:
            obj.write_json('PH', 'data', 'nrf', 'folder')
        self.assertEqual(p.getvalue().strip(), '-i- remote write_json() site not exist: PH nrf folder')

        # read_json
        with CaptureStdoutLog() as p:
            obj.read_json('PH', 'folder', 'tester', 'fname')
        self.assertEqual(p.getvalue().strip(), '-i- remote read_json() site not exist: PH folder tester fname')

        # Remote() manual run
        with MockVar(Remote, '_check_sites', Mock(side_effect=TypeError)):
            with self.assertRaises(TypeError):
                Remote(check=True)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_initial_stm(self):
        # initial_stm exception case. For passing case, test_case1 will check it
        obj = Remote()
        self.assertNotEqual(obj.sites, {})   # with Valid Sites

        with MockVar(DataHost, 'central', Mock(side_effect=Exception)):
            result = obj.initial_stm()
        self.assertEqual(result, ({}, {}, {}))
        self.assertEqual(obj.sites, {})   # no valid site

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_check_sites(self):
        obj = Remote()
        # default case - do nothing
        self.assertEqual(obj._check_sites(True), 1)   # should match

        # sites have changed
        obj.sites = {'PH': None}
        with MockVar(DataHost, 'central', Mock(side_effect=Exception)):
            obj._check_sites(True)
        self.assertEqual(obj.sites, {})   # no valid site

        # ispass=False
        with MockVar(DataHost, 'central', Mock()):
            obj._check_sites(False)
        self.assertEqual(obj.sites, obj._origsites)   # back to original

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_write_files(self):
        obj = Remote()
        self.assertEqual(obj.write_files('/blah', 'nothing'), 0)

        with MockVar(DataHost, 'central', Mock()), \
                MockVar(manager_botos, 'IS_UT', False):
            self.assertEqual(obj.write_files('/blah', 'nothing'), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_completed(self):
        obj = Remote()

        # Test case 1: Normal case with multiple sites
        def fake_data_host(slf, cmd, arg, check, urp):
            if cmd == 'read_completed':
                # Determine which site based on the urp parameter
                if urp == Remote._SITES['PG']:
                    return {'job1.json': {'key': 1, 'status': 'completed'},
                            'job2.json': {'key': 2, 'status': 'failed'}}
            return {}

        with MockVar(DataHost, 'central', fake_data_host):
            result = obj.read_completed()

        # Since Remote constructor excludes 'JF' (selfsite), only 'PG' should be in result
        expected = {
            'PG': {'job1.json': {'key': 1, 'status': 'completed'},
                   'job2.json': {'key': 2, 'status': 'failed'}}
        }
        self.assertEqual(result, expected)

        # Test case 2: Empty result
        def fake_data_host_empty(slf, cmd, arg, check, urp):
            if cmd == 'read_completed':
                return {}
            return {}

        with MockVar(DataHost, 'central', fake_data_host_empty):
            result = obj.read_completed()
        self.assertEqual(result, {'PG': {}})

        # Test case 3: No sites available
        obj.sites = {}
        result = obj.read_completed()
        self.assertEqual(result, {})


class TestBotos(TestCase):

    def test_json(self):

        with TempDir(name=True, chdir=True) as tdir:

            # basic
            data = {'key': 2}
            BotOS.json.dump(f'{tdir}/a.json', data)
            result = BotOS.json.load(f'{tdir}/a.json', 'ut()')
            self.assertEqual(result, {'key': 2})

            # rewrite same filename
            data = {'key': 3}
            BotOS.json.dump(f'{tdir}/a.json', data)
            result = BotOS.json.load(f'{tdir}/a.json', 'ut()')
            self.assertEqual(result, {'key': 3})

            # Empty
            File(f'{tdir}/b.json').touch()
            result = BotOS.json.load(f'{tdir}/b.json', 'ut()')
            self.assertEqual(result, {})
            self.assertEqual(exists(f'{tdir}/b.json'), False)

            # Failure
            File(f'{tdir}/c.json').touch('{"A": 2')
            with self.assertRaises(json.decoder.JSONDecodeError):
                BotOS.json.load(f'{tdir}/c.json', 'ut()')

    def test_get_files_local(self):
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(BotOS, 'root', tdir):

                File('testers/testera/nvlu.package.info').touch(mtime=1726020529, mkdir=True)
                File('testers/testera/idle.status').touch(mtime=1726020529)
                File('testers/testera/subfolder/aaa').touch(mtime=1726020569, mkdir=True)
                File('testers/testerb/nvlu.package.info').touch(mtime=1726020539, mkdir=True)
                File('testers/somefile').touch(mtime=1726020539, mkdir=True)     # should be ignored
                File('staging/blah').touch(mtime=1726020539, mkdir=True)
                File('randomfile').touch(mtime=1726020529)

                self.assertEqual(BotOS.get_files_local(1726020570),
                                 {'testera': {'nvlu.package.info': 41,
                                              'idle.status': 41,
                                              'aaa': 1},
                                  'testerb': {'nvlu.package.info': 31}})

    def test_get_files_staging(self):
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(BotOS, 'root', tdir):

                File('staging/testera/nvlu.package.info').touch(mtime=1726020529, mkdir=True)
                File('staging/testera/idle.status').touch(mtime=1726020529)
                File('staging/testera/subfolder/aaa').touch(mtime=1726020569, mkdir=True)
                File('staging/testerb/nvlu.package.info').touch(mtime=1726020539, mkdir=True)
                File('testera/blah').touch(mtime=1726020539, mkdir=True)
                File('randomfile').touch(mtime=1726020529)

                self.assertEqual(BotOS.get_files_local(1726020570, is_staging=True),
                                 {'testera': {'nvlu.package.info': 41,
                                              'idle.status': 41,
                                              'aaa': 1},
                                  'testerb': {'nvlu.package.info': 31}})

    def test_get_meta_content(self):
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(BotOS, 'root', tdir):

                File('staging/_metadata/joba.json').touch('{"key": "value1"}', mkdir=True)
                File('staging/_metadata/jobb.txt').touch()

                self.assertEqual(BotOS.get_meta_content(), {'joba.json': {'key': 'value1'}})

    def test_get_metafname(self):
        self.assertEqual(BotOS.get_metafname('8000_1726798252_E.tar.gz'), '1726798252_E')
        self.assertEqual(BotOS.get_metafname('1726798252_E.tar.gz'), '1726798252_E')
        self.assertEqual(BotOS.http_link('jf', '/blah/2011-12/abc.gz'),
                         'https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./2011-12/abc.gz')
        self.assertEqual(BotOS.http_link('ba', '/blah/2011-12/abc.gz'),
                         'https://tvpv1.iind.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./2011-12/abc.gz')
        self.assertEqual(BotOS.http_link(None, '/blah/2011-12/abc.gz'), '<no http link>')

    def test_get_timesecs(self):
        self.assertEqual(BotOS.get_timesecs('1762304238822_E.json'), 1762304238)
        self.assertEqual(BotOS.get_timesecs('1762304238822_E'), 1762304238)
        self.assertEqual(BotOS.get_timesecs('8000_1762304238822_E.tar.gz'), 1762304238)
        self.assertEqual(BotOS.get_timesecs('8000'), 0)

    def test_message_results(self):
        """Test message_results to ensure all log versions are included."""

        # Case 1 - Ideal Case No Retest
        mock_data_case1 = {
            "tprolling": "/mock/tprolling",
            "site": "PG",
            "Ituff file": "/mock/path/ituff_0.txt",
            "Test Unit log": "/mock/path/testunit_0.txt",
            "logfile": "/mock/path/logfile.txt",
            "code": 0,
            "comment": "Test completed successfully."
        }

        expected_output_case1 = '''
Ituff file:
   Path:        /mock/tprolling/ituff_0.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/ituff_0.txt
Test Unit log:
   Path:        /mock/tprolling/testunit_0.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/testunit_0.txt
listener (script) log file:
   Path:        /mock/path/logfile.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/logfile.txt
trace lot#s: None
exit code:   0
Result:      Test completed successfully.
'''

        result_case1 = list(BotOS.message_results(mock_data_case1))
        self.assertTextEqual('\n'.join(result_case1), expected_output_case1)

        # Case 2 - Problem
        mock_data_case2 = {
            "tprolling": "/mock/tprolling",
            "site": "PG",
            "logfile": "/mock/path/logfile.txt",
            "code": 1,
            "comment": "No HardBin found. Refer to logs."
        }

        expected_output_case2 = '''
listener (script) log file:
   Path:        /mock/path/logfile.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/logfile.txt
trace lot#s: None
exit code:   1
Result:      No HardBin found. Refer to logs.
'''

        result_case2 = list(BotOS.message_results(mock_data_case2))
        self.assertTextEqual('\n'.join(result_case2), expected_output_case2)

        # Case 3 - With Retest Log
        mock_data_case3 = {
            "tprolling": "/mock/tprolling",
            "site": "PG",
            "Ituff file": "/mock/path/ituff_0.txt",
            "Ituff file 1": "/mock/path/ituff_1.txt",
            "Ituff file 2": "/mock/path/ituff_2.txt",
            "Test Unit log": "/mock/path/testunit_0.txt",
            "Test Unit log 1": "/mock/path/testunit_1.txt",
            "Test Unit log 2": "/mock/path/testunit_2.txt",
            "logfile": "/mock/path/logfile.txt",
            "code": 0,
            "comment": "Test completed successfully."
        }

        expected_output_case3 = '''
Ituff file:
   Path:        /mock/tprolling/ituff_0.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/ituff_0.txt
Ituff file 1:
   Path:        /mock/tprolling/ituff_1.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/ituff_1.txt
Ituff file 2:
   Path:        /mock/tprolling/ituff_2.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/ituff_2.txt
Test Unit log:
   Path:        /mock/tprolling/testunit_0.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/testunit_0.txt
Test Unit log 1:
   Path:        /mock/tprolling/testunit_1.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/testunit_1.txt
Test Unit log 2:
   Path:        /mock/tprolling/testunit_2.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/testunit_2.txt
listener (script) log file:
   Path:        /mock/path/logfile.txt
   Direct link: https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./path/logfile.txt
trace lot#s: None
exit code:   0
Result:      Test completed successfully.
'''
        result_case3 = list(BotOS.message_results(mock_data_case3, _max=3))
        self.assertTextEqual('\n'.join(result_case3), expected_output_case3)


# Unittests are assumed there are only two sites
Remote._SITES = {'JF': 'some_data_structure_we_dont_need',
                 'PG': 'some_data_structure_we_dont_need'}

AutoRestart._is_ut = True    # set AutoRestart to be in client mode always (aka, unittest)
AutoRestart()                # Store the mtimes so AutoRestart() will not fail


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
