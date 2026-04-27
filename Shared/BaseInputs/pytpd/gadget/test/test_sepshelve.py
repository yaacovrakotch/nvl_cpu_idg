#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unittest for sepshelve
"""
import setenv_unittest     # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.sepshelve import *
from gadget.files import TempDir
from gadget.shell import RunChild, LAUNCH_CWD
from gadget.gizmo import MockVar, with_, Elapsed
from unittest.mock import Mock, patch
from gadget.dictmore import DictDot
from gadget.helperclass import CaptureStdout
from gadget.shell import IS_UNIX, IS_WIN
from os.path import realpath
import gadget.sepshelve as sepshelve
import random
import multiprocessing


class SqlOperationTest(TestCase):

    def test_seput_basic(self):
        ut = SepUT()
        ut["a"] = 1
        ut["b"] = 2
        self.assertEqual(ut["a"], 1)
        self.assertIn("b", ut)
        self.assertEqual(len(ut), 2)
        self.assertEqual(set(iter(ut)), {"a", "b"})

    @unittest.skipIf(*is_ut_option('SLOW', message="More than 15s execution"))
    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="More than 15s execution"))
    @with_(TempDir, chdir=True)
    def test_frag(self):
        db = SqlDict('f.sqlite', num_keys=True)
        db[1] = {x for x in range(100)}
        self.assertEqual(SqlOperation('f.sqlite').get_frag(), 0)

        # create a testcase with fragmentation
        random.seed(1)
        for i in range(1000):
            db[random.randint(1, 9999999)] = i
        # remove a limited subset of keys to create free pages
        keys = sorted(list(db.keys()))
        for k in keys[:100]:
            del db[k]

        frag_pct = SqlOperation('f.sqlite', disp=True).get_frag()
        self.assertGreaterEqual(int(frag_pct), 1)

    @with_(TempDir, chdir=True)
    def test_journal(self):
        # journal not exist
        db = SqlDict("abc.sqldict")
        self.assertFalse(SqlOperation(db.dbfile()).journal_exist())

        # journal exist
        with db.batch():
            db['new'] = 123
            self.assertTrue(SqlOperation(db.dbfile()).journal_exist())
            db.commit()


# --- SQL tests ---

class SQLDict_tests(TestCase):
    def isgz(self):
        """For this test clsas, set gz to False - no compression"""
        return False

    @with_(TempDir, chdir=True)
    def test_basic(self):
        dd = SqlDict("basic.sql", gz=self.isgz())
        self.assertEqual(len(dd), 0)
        dd['key1'] = "value1"
        dd['key2'] = "value2"
        self.assertEqual(dd['key1'], 'value1')
        self.assertEqual(dd['key2'], 'value2')

        # open another instance of the same sql file
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        self.assertEqual(ff['key1'], 'value1')
        self.assertEqual(ff['key2'], 'value2')

        # update
        dd['key2'] = 'newvalue'
        self.assertEqual(ff['key1'], 'value1')
        self.assertEqual(ff['key2'], 'newvalue')
        self.assertEqual(dd['key1'], 'value1')
        self.assertEqual(dd['key2'], 'newvalue')
        self.assertEqual(len(dd), 2)
        self.assertEqual(len(ff), 2)

        # existence checks
        self.assertTrue('key1' in ff)
        self.assertIn('key2', ff)
        self.assertTrue('key1' in ff)
        with self.assertRaises(KeyError):
            res = ff['key3']

        # other getters
        self.assertEqual(set(ff.keys()), {'key1', 'key2'})
        self.assertEqual(set(ff.values()), {'newvalue', 'value1'})
        self.assertEqual(set(ff.items()), {('key2', 'newvalue'), ('key1', 'value1')})

        # get()
        self.assertEqual(ff.get('key2', 'noval'), 'newvalue')
        self.assertEqual(ff.get('key3', 'noval'), 'noval')

        # iterator
        res = set()
        for item in ff:
            res.add(item)
        self.assertEqual(res, {'key1', 'key2'})
        self.assertEqual(set(ff), {'key1', 'key2'})

    @with_(TempDir, chdir=True)
    @with_(MockVar, SqlDict, "_wait_journal", Mock())
    def test_basic_writeread(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        self.assertEqual(len(dd), 0)
        self.assertEqual(len(ff), 0)

        # update with commit
        dd['key1'] = 'value'
        self.assertEqual(ff['key1'], 'value')
        dd['key2'] = 'value2'
        self.assertEqual(ff['key2'], 'value2')
        self.assertEqual(len(ff), 2)

        # update without commit
        with dd.batch():
            dd['key3'] = 'value'
            self.assertEqual(len(dd), 3)
            self.assertEqual(len(ff), 2)
            dd['key4'] = 'value3'
            self.assertEqual(len(dd), 4)
            self.assertEqual(len(ff), 2)
            dd.commit()
        self.assertEqual(len(dd), 4)
        self.assertEqual(len(ff), 4)
        self.assertEqual(dict(ff), {'key3': 'value', 'key2': 'value2', 'key1': 'value', 'key4': 'value3'})

    @with_(TempDir, chdir=True)
    def test_delitem(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        dd['key1'] = "value1"
        dd['key2'] = "value2"

        # operation
        self.assertEqual(len(ff), 2)
        del dd['key2']

        # checks
        self.assertEqual(len(ff), 1)
        self.assertEqual(ff['key1'], 'value1')
        self.assertTrue('key1' in ff)
        self.assertFalse('key2' in ff)
        self.assertEqual(set(ff.keys()), {'key1'})

        # delete a non-existent key
        with self.assertRaises(KeyError):
            del dd['key2']

    @with_(TempDir, chdir=True)
    def test_key_types(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here

        # Key is None (write and read not allowed)
        with self.assertRaisesRegex(KeyError, 'is not allowed'):
            dd[None] = 'value5'
        with self.assertRaises(KeyError):
            res = dd[None]

        # Key has special chars
        for key in ("with'quote",
                    'with"quote',
                    'with\ttab',
                    '''with
        newline
        '''):
            dd[key] = key + key
            self.assertEqual(dd[key], key + key)

    @with_(TempDir, chdir=True)
    def test_value_types(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        dd["s1"] = "value1"  # string
        dd["s2"] = 123  # number
        dd["s3"] = (123, 456)  # tuple
        dd["s4"] = {123, 456}  # set

        self.assertEqual(ff['s1'], 'value1')
        self.assertEqual(ff['s2'], 123)
        self.assertEqual(ff['s3'], (123, 456))
        self.assertEqual(ff['s4'], {123, 456})

    @with_(TempDir, chdir=True)
    def test_fail_write(self):
        dd = SqlDict("basic.sql", gz=self.isgz())

        m = Mock()
        m.execute.return_value = DictDot(rowcount=2)

        with MockVar(dd, "_conn", m):
            with self.assertRaisesRegex(KeyError, "update to database"):
                dd['key1'] = 45

    @with_(TempDir, chdir=True)
    @with_(MockVar, SqlDict, "_wait_journal", Mock())
    def test_commit(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")
        dd["s1"] = "value1"
        dd["s2"] = 123
        self.assertEqual(len(ff), 2)

        # no commit
        dd._nocommit = True
        dd["s3"] = 1
        dd["s4"] = 2
        self.assertEqual(len(ff), 2)
        self.assertEqual(len(dd), 4)

        dd.commit()
        self.assertEqual(len(ff), 4)
        self.assertEqual(len(dd), 4)
        dd.commit()
        dd.commit()

    @with_(TempDir, chdir=True)
    def test_update_with_lock(self):
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")
        dd.update_withlock("s1", "value1")
        dd.update_withlock("s2", 123)
        self.assertEqual(len(ff), 2)
        self.assertEqual(len(dd), 2)
        self.assertFalse(exists('basic.sql.lock'))

    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    def test_ut_query(self):
        with TempDir(chdir=True) as tdir:
            dd = SqlDict("basic.sql", gz=self.isgz())
            dd['s1'] = 1
            if IS_WIN:
                # Windows: release file handles before deleting tempdir
                dd._conn.close()

        # exception: database is deleted
        with MockVar(sepshelve, "check_lock_wait", Mock), \
                MockVar(sepshelve, "sleep", Mock()):
            if IS_UNIX:
                # Linux: database has been deleted, but still points to a deleted FD
                exp_msg = "attempt to write a readonly database"
            else:
                # Windows: database has been closed and deleted.
                exp_msg = "Cannot operate on a closed database"
            self.assertRaisesRegex(Exception, exp_msg,
                                   dd._query, 'INSERT OR REPLACE INTO dict VALUES ("ab", "cd")')

        # operation error (mocked)
        with TempDir(chdir=True) as tdir:
            dd = SqlDict("basic.sql", gz=self.isgz())

            def func1(args):
                raise sqlite3.OperationalError

            with MockVar(sepshelve, "check_lock_wait", Mock), \
                    MockVar(sepshelve, "sleep", Mock()):
                self.assertRaisesRegex(Exception, "Unable to run",
                                       dd._query, 'SELECT count(key) FROM dict', func=func1)

    @with_(TempDir, chdir=True)
    @with_(MockVar, SqlDict, "_wait_journal", Mock())
    def test_batch_contextmgr(self):
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")
        with dd.batch():
            dd["s1"] = "value1"
            dd["s2"] = 123
            self.assertEqual(len(ff), 0)  # should not be committed yet
            self.assertEqual(len(dd), 2)
            self.assertTrue(exists('basic.sql.lock'))  # lock file exist
            dd.commit()

        self.assertFalse(exists('basic.sql.lock'))
        self.assertEqual(len(ff), 2)  # should be committed yet
        self.assertEqual(len(dd), 2)

        # batch that forgot commit
        with self.assertRaisesRegex(Exception, "Incorrect usage"):
            with dd.batch():
                dd["s1"] = "value2"
                dd["s2"] = 124

        # batch exception occurred - with data
        with self.assertRaisesRegex(Exception, "something failed"):
            with dd.batch():
                dd['snew'] = 126
                raise Exception("something failed")
        self.assertEqual(ff['snew'], 126)  # confirm that commit happened

        # batch exception occurred - no data
        with self.assertRaisesRegex(Exception, "something failed"):
            with dd.batch():
                raise Exception("something failed")

    @with_(TempDir, chdir=True)
    def test_update(self):
        # setup
        dd1 = SqlDict("basic.sql", gz=self.isgz())
        dd2 = SqlDict("basic2.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        dd1['key1'] = "value1"
        dd1['key2'] = "value2"
        dd2['key3'] = "value3"
        dd2['key2'] = "newvalue"

        dd1.update(dd2)
        self.assertEqual(set(ff.items()), {('key2', 'newvalue'),
                                           ('key1', 'value1'),
                                           ('key3', 'value3')})

        normaldict = dict(dd1)
        self.assertEqual(normaldict, {'key2': 'newvalue',
                                      'key1': 'value1',
                                      'key3': 'value3'})

        self.assertIn('newvalue', str(dd1))

    @unittest.skipIf(IS_WIN, 'unix only due to ls -ltr')
    def test_dbfile(self):
        with TempDir(chdir=True, name=True) as tdir:
            dd = SqlDict("basic.sql")
            ff = SqlDict("basic.sql")
            self.assertEqual(dd.dbfile(), join(tdir, "basic.sql"))
            self.assertEqual(dd.get_dbfile(), join(tdir, "basic.sql"))
            self.assertEqual(dd.get_dbdir(), tdir)
            self.assertFalse(dd._isfileexist)
            self.assertTrue(ff._isfileexist)

            # check chmod
            res = File('basic.sql').lsltrd()
            self.assertIn('-rw-rw----', res)

            # compatibility with SqlParDict
            self.assertEqual(len(dd._batchkeys(['k1', 'k2'])), 2)

    @with_(TempDir, chdir=True)
    def test_fetch(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        for i in range(100):
            dd[str(i)] = i + 100

        self.assertEqual(ff.fetch({'1', '2', '3', '4', '5', '6'}),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106})
        self.assertEqual(ff.fetch({'1', '2', '3', '4', '5'}),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104})
        self.assertEqual(ff.fetch({'1', '2', '3', '4', '5', '6', '7'}),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106, '7': 107})

        # large value
        self.assertEqual(len(ff.fetch(range(99))), 99)

        # with None key - None must be ignored
        self.assertEqual(ff.fetch({'1', None}), {'1': 101})

        # special chars on key
        special_keys = ("with'quote",
                        'with"quote',
                        'with\ttab',
                        '''with
        newline
        ''')
        for key in special_keys:
            dd[key] = key + key  # write it to database
        self.assertEqual(ff.fetch(special_keys), {key: key + key for key in special_keys})

        # mixed fetch
        self.assertEqual(ff.fetch({'with"quote', '2', '3'}),
                         {'3': 103, '2': 102, 'with"quote': 'with"quotewith"quote'})

    @with_(TempDir, chdir=True)
    def test_query(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here

        for i in range(100):
            dd[str(i)] = i + 100

        self.assertEqual(ff.query_startswith('7'),
                         {'7': 107, '77': 177, '76': 176, '75': 175,
                          '74': 174, '73': 173, '72': 172, '71': 171,
                          '70': 170, '79': 179, '78': 178})
        self.assertEqual(ff.query_like('7%'),
                         {'7': 107, '77': 177, '76': 176, '75': 175,
                          '74': 174, '73': 173, '72': 172, '71': 171,
                          '70': 170, '79': 179, '78': 178})

    @with_(TempDir, chdir=True)
    def test_numeric_key(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz(), num_keys=True)
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        self.assertTrue(dd._numtype)
        self.assertTrue(ff._numtype)
        for i in range(5):
            dd[i] = i + 100
        self.assertEqual(dict(list(ff.items())), {0: 100, 1: 101, 2: 102, 3: 103, 4: 104})

        # keys are specified as string, but in database, it is integer
        for i in range(5):
            dd[str(i)] = i + 200
        self.assertEqual(dict(list(ff.items())), {0: 200, 1: 201, 2: 202, 3: 203, 4: 204})

        # more method checks
        self.assertEqual(set(ff.keys()), {0, 1, 2, 3, 4})
        self.assertEqual(set(ff.query_startswith('0')), {0})
        self.assertEqual(set(ff.query_like('0%')), {0})
        self.assertEqual(set(ff.fetch([0, 1])), {0, 1})  # fetch non-special key
        self.assertEqual(set(ff.fetch(['0"', 1])), {1})  # fetch special key

    @with_(TempDir, chdir=True)
    def test_non_unicode_key(self):
        # setup
        dd = SqlDict("basic.sql", gz=self.isgz())
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        self.assertFalse(dd._numtype)
        self.assertFalse(ff._numtype)

        # test all the methods and iterate on database:
        dd['k1'] = 'txt1'
        dd['k2'] = 'txt2'
        res = list(ff.items())
        self.assertIs(type(res[0][0]), str)  # key
        self.assertIs(type(res[0][1]), str)  # value

        res = list(ff.keys())
        self.assertIs(type(res[0]), str)

        res = ff.query_startswith('k')
        item = res.popitem()
        self.assertIs(type(item[0]), str)
        self.assertIs(type(item[1]), str)

        res = ff.query_like('k%')
        item = res.popitem()
        self.assertIs(type(item[0]), str)
        self.assertIs(type(item[1]), str)

        res = ff.fetch(['k1'])
        self.assertEqual(res, {'k1': 'txt1'})
        item = res.popitem()
        self.assertIs(type(item[0]), str)
        self.assertIs(type(item[1]), str)

        dd['k"4'] = "txt"
        res = ff.fetch(['k"4'])
        self.assertEqual(res, {'k"4': 'txt'})
        item = res.popitem()
        self.assertIs(type(item[0]), str)
        self.assertIs(type(item[1]), str)


class SQLgz_tests(SQLDict_tests):
    def isgz(self):
        """For this test clsas, set gz to True"""
        return True

    @with_(TempDir, chdir=True)
    def test_basicgz(self):
        dd = SqlDict("basic.sql", gz=True)
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        setsize = 100000
        someset = set(range(setsize))
        dd['key1'] = someset
        self.assertIs(type(someset), set)
        self.assertEqual(len(someset), setsize)
        len1 = len(pickle.dumps(someset))
        self.assertGreater(len1, os.path.getsize("basic.sql"))

        # tests
        self.assertEqual(len(dd['key1']), setsize)
        self.assertEqual(len(ff['key1']), setsize)

        # Incorrect gz for existing file
        with self.assertRaisesRegex(Exception, 'is already set to encoding=PICKLE_GZ.*encoding=PICKLE_NOGZ'):
            gg = SqlDict("basic.sql", gz=False)

        gg = SqlDict("basic.sql", gz=True)
        self.assertEqual(len(gg['key1']), setsize)


class SQLDictOnetime_tests(TestCase):
    """Tests here are not executed for gz version"""

    @with_(TempDir, chdir=True)
    def test_default_encoding(self):
        dd = SqlDict("basic.sql")
        ff = SqlDict("basic.sql")
        self.assertEqual(dd._encoding, 0)  # backwards compatibility test. default encoding is zero.
        self.assertEqual(ff._encoding, 0)

        # unknown encoding
        dd._encoding = 100
        with self.assertRaisesRegex(Exception, 'Unknown encoding'):
            dd._assign_encoding()

        # get dbdir
        self.assertEqual(realpath(dd.get_dbrootdir()), realpath("."))

    @with_(TempDir, chdir=True)
    def test_check_isdir(self):
        # passing a directory as dbfile should raise
        os.mkdir("as_dir")
        with self.assertRaisesRegex(Exception, r"SqlDict\(\) cannot take in directory"):
            SqlDict("as_dir")

        # set_max_read_time
        dd = SqlDict("basic.sql")
        self.assertEqual(dd._cfg.max_read_time, 10 * 60)
        dd.set_max_read_time(42)
        self.assertEqual(dd._cfg.max_read_time, 42)

    @with_(TempDir, chdir=True)
    def test_read_touch_dir(self):
        # mkdirs failure should result in None and no dir
        dd_fail = SqlDict("basic.sql")
        fail_touchdir = join(realpath("."), "READTD_basic.sql")
        with patch("gadget.sepshelve.mkdirs", side_effect=Exception("fail")):
            fail_path = dd_fail._read_touch_dir()
        self.assertIsNone(fail_path)
        self.assertFalse(isdir(fail_touchdir))

        # Ensure read-touch dir gets created and path is returned
        dd = SqlDict("basic.sql")
        path = dd._read_touch_dir()
        touchdir = join(realpath("."), "READTD_basic.sql")
        self.assertIsNotNone(path)
        self.assertTrue(path.startswith(touchdir))
        self.assertTrue(isdir(touchdir))

    @with_(TempDir, chdir=True)
    def test_has_key(self):
        dd = SqlDict("basic.sql")
        dd["k1"] = "v1"
        # To cover has_key, add noqa to suppress PEP8 warning
        self.assertTrue(dd.has_key("k1"))   # noqa: W601
        self.assertFalse(dd.has_key("k2"))  # noqa: W601

        dd["k2"] = "v2"

        # viewkeys
        self.assertTrue(isinstance(dd.viewkeys(), set))
        self.assertEqual(set(dd.viewkeys()), {"k1", "k2"})

        self.assertTrue(isinstance(dd.iterkeys(), list))
        self.assertEqual(set(dd.iterkeys()), {"k1", "k2"})

        self.assertTrue(isinstance(dd.viewitems(), set))
        self.assertEqual(set(dd.viewitems()), {("k1", "v1"), ("k2", "v2")})

        self.assertTrue(isinstance(dd.iteritems(), list))
        self.assertEqual(set(dd.iteritems()), {("k1", "v1"), ("k2", "v2")})

        self.assertTrue(isinstance(dd.viewvalues(), set))
        self.assertEqual(set(dd.viewvalues()), {"v1", "v2"})

        self.assertTrue(isinstance(dd.itervalues(), list))
        self.assertEqual(set(dd.itervalues()), {"v1", "v2"})

    @with_(TempDir, chdir=True, )
    def test_encoding_0(self):
        # 0 is PICKLE_NOGZ
        dd = SqlDict("basic.sql")
        ff = SqlDict("basic.sql")
        self.assertEqual(dd._encoding, 0)
        self.assertEqual(ff._encoding, 0)

        dd['key1'] = [1, (2, 7), 3]
        self.assertEqual(ff['key1'], [1, (2, 7), 3])

        # gz test - no gz
        val = '1'.zfill(100000)
        dd['key1'] = val
        self.assertEqual(ff['key1'], val)
        self.assertLess(len(val), os.path.getsize("basic.sql"))

    @with_(TempDir, chdir=True, )
    def test_encoding_1(self):
        # 1 is PICKLE_GZ
        dd = SqlDict("basic.sql", gz=True)
        ff = SqlDict("basic.sql")
        self.assertEqual(dd._encoding, 1)
        self.assertEqual(ff._encoding, 1)

        dd['key1'] = [1, (2, 7), 3]
        self.assertEqual(ff['key1'], [1, (2, 7), 3])

        # gz test - with gz
        val = '1'.zfill(100000)
        dd['key1'] = val
        self.assertEqual(ff['key1'], val)
        self.assertGreater(len(val), os.path.getsize("basic.sql"))

    @with_(TempDir, chdir=True, )
    def test_encoding_2(self):
        # 2 is TEXT_NOGZ
        dd = SqlDict("basic.sql", text_only=True)
        ff = SqlDict("basic.sql")
        self.assertEqual(dd._encoding, 2)
        self.assertEqual(ff._encoding, 2)

        # gz test - no gz
        val = '1'.zfill(100000)
        dd['key1'] = val
        self.assertEqual(ff['key1'], val)
        self.assertLess(len(val), os.path.getsize("basic.sql"))

        # only text is allowed
        with self.assertRaises(Exception):
            dd['key2'] = [1, 2, 3]

    @with_(TempDir, chdir=True, )
    def test_encoding_3(self):
        # 3 is TEXT_GZ
        dd = SqlDict("basic.sql", gz=True, text_only=True)
        ff = SqlDict("basic.sql")
        self.assertEqual(dd._encoding, 3)
        self.assertEqual(ff._encoding, 3)

        # gz test - with gz
        val = '1'.zfill(100000)
        dd['key1'] = val
        self.assertEqual(ff['key1'], val)
        self.assertGreater(len(val), os.path.getsize("basic.sql"))

        # only text is allowed
        with self.assertRaises(Exception):
            dd['key2'] = [1, 2, 3]

    @with_(TempDir, chdir=True)
    def test_re_no_special_char(self):
        dd = SqlDict("basic.sql")
        self.assertTrue(dd._re_no_special_char.search('abc'))
        self.assertTrue(dd._re_no_special_char.search('a123 (-ok-=24)'))
        self.assertTrue(dd._re_no_special_char.search('a `~!@#$%^&*()_+-={}[]|:;,./<>?'))

        self.assertFalse(dd._re_no_special_char.search('a"'))
        self.assertFalse(dd._re_no_special_char.search("a'"))
        self.assertFalse(dd._re_no_special_char.search('''a
        b'''))
        self.assertFalse(dd._re_no_special_char.search("a\tb"))

    @with_(TempDir, chdir=True)
    def test_fetch_ut_separation(self):
        dd = SqlDict("basic.sql")
        ff = SqlDict("basic.sql")  # Do not specify isgz here

        # Some unittest
        self.assertEqual(dd.fetch({'abc1', "1.3", '1 (-4)', None, "qu'te", 'a\nb'}), dict())
        self.assertEqual(dd._ut_plainset, {'abc1', '1 (-4)', "1.3"})
        self.assertEqual(dd._ut_otherset, {"qu'te", 'a\nb'})

        self.assertEqual(dd.fetch({None, 12, 14}), dict())
        self.assertEqual(dd._ut_plainset, {12, 14})
        self.assertEqual(dd._ut_otherset, set())

        self.assertEqual(dd.fetch({None, "qu'te", 'a\nb'}), dict())
        self.assertEqual(dd._ut_plainset, set())
        self.assertEqual(dd._ut_otherset, {"qu'te", 'a\nb'})

        self.assertEqual(dd.fetch({None, "1", 'abc(2)'}), dict())
        self.assertEqual(dd._ut_plainset, {"1", 'abc(2)'})
        self.assertEqual(dd._ut_otherset, set())

        # unicode
        self.assertEqual(dd.fetch({None, "qu'te", 'a\nb', 'abc(2)'}), dict())
        self.assertEqual(dd._ut_plainset, {'abc(2)'})
        self.assertEqual(dd._ut_otherset, {"qu'te", 'a\nb'})

        # empty input
        self.assertEqual(dd.fetch(set()), dict())

    @with_(TempDir, chdir=True)
    def test_fetch2_ut(self):
        dd = SqlDict("basic.sql")
        ff = SqlDict("basic.sql")  # Do not specify isgz here

        # fetch2 unittests
        with dd.batch():
            for i in range(4500):
                dd[str(i)] = i + 100
            dd.commit()

        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106})
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5'}),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104})
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6', '7'}),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106, '7': 107})

        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=2),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106})
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5'}, _maxn=2),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104})
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6', '7'}, _maxn=2),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106, '7': 107})

        expect_6 = {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106}
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=1), expect_6)
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=2), expect_6)
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=3), expect_6)
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=4), expect_6)
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=5), expect_6)
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=6), expect_6)
        self.assertEqual(ff._fetch2({'1', '2', '3', '4', '5', '6'}, _maxn=7), expect_6)

        # large value
        self.assertEqual(len(ff._fetch2(range(4500))), 4500)
        self.assertEqual(len(ff._fetch2(range(4000))), 4000)

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="Parallel simultaneous writes"))
    def test_parallel_writes(self):
        # Start of test / server ======================================
        with TempDir(name=True) as tdir:
            ready = multiprocessing.Value('i', 0)  # shared variable
            filepath = join(tdir, "basic.sql")
            dd = SqlDict(filepath)
            # do parallel simultaneous writes
            with RunChild(target=child_proc, args=(ready, filepath), timeout=20) as p:
                p.waitready(ready)
                sw = Elapsed()
                for i in range(500):
                    dd.update_withlock('dd%s' % i, i + 1000)
                    # dd['dd%s' % i] = i+1000
                    print("X", end=' ')
                print(sw)  # this must be at least 1 sec

            self.assertEqual(len(dd), 1000)

    @with_(TempDir, chdir=True)
    def test_destroy(self):
        d1 = SqlDict("basic.sql")
        d2 = SqlDict("basic.sql")
        d3 = SqlDict("basic.sql")

        # normal case
        del d1

        # _conn not exist
        delattr(d2, '_conn')
        del d2

        # db is closed
        d3._conn.close()
        del d3

    @with_(TempDir, chdir=True)
    def test_hotjournal(self):
        dd = SqlDict("basic.sql")

        # normal case - not exist
        self.assertEqual(dd._check_hot_journal(dd._dbfile), 3)

        # hot journal case
        with dd.batch():
            dd['somekey'] = 123

            # journal is pretty new
            self.assertEqual(dd._check_hot_journal(dd._dbfile), 1)

            # do a chmod, journal is old
            dd._cfg.lock_maxlock = 0
            self.assertEqual(dd._check_hot_journal(dd._dbfile), 2)

            # exception occurred
            with MockVar(sepshelve, "getmtime", Mock(side_effect=Exception)):
                self.assertEqual(dd._check_hot_journal(dd._dbfile), 0)

            dd.commit()

    @with_(TempDir, chdir=True)
    def test_commit(self):
        dd = SqlDict("basic.sql")

        # pass case
        with dd.batch():
            dd['somekey'] = 123
            self.assertEqual(dd.commit(), 0)

        # fail case
        with dd.batch():
            dd['somekey2'] = 123
            m = Mock()
            m.commit.side_effect = sqlite3.OperationalError
            with MockVar(dd, "_conn", m), \
                    MockVar(sepshelve, "sleep", Mock()):
                with self.assertRaisesRegex(Exception, "Unable to commit data"):
                    dd.commit()

            dd.commit()  # real commit

        # loopcount test
        self.assertEqual(dd._cfg.query_loopcount(), 3000)
        self.assertEqual(dd._cfg.commit_loopcount(), 12)

    @unittest.skipIf(*is_ut_option('SLOW', message="At least 5 sec execution"))
    @with_(TempDir, chdir=True)
    def test_commit2(self):
        # NOTE: This test must complete in ~5 seconds, when run by itself
        class MySql(SqlDict):
            def _set_knobs_config(self):
                cfg = SqlDict._set_knobs_config(self)
                cfg.sqlite_connection_timeout = 1
                cfg.commit_timeout = 5
                return cfg

        dd = MySql("basic.sql")
        ff = SqlDict("basic.sql")
        dd['somekey'] = 123
        with dd.batch():
            # this will block the commit
            res = iter(ff.keys())

            dd['somekey2'] = 456
            with self.assertRaisesRegex(Exception, "Unable to commit data"):
                dd.commit()
            del res
            dd.commit()

    @with_(TempDir, chdir=True)
    @with_(MockVar, SqlDict, "_wait_journal", Mock())
    def test_no_block(self):
        # This tests if the read operations are blocking the write...
        # Note: if there is a blocking operation, then the process must be killed with -9
        dd = SqlDict("basic.sql")
        ff = SqlDict("basic.sql")
        dd['somekey'] = 123
        print()

        print("Starting __getitem__()")
        with dd.batch():
            dd['somekey2'] = 456
            res = ff['somekey']
            dd.commit()

        print("Starting __contains__()")
        with dd.batch():
            dd['somekey2'] = 4567
            res = bool('somekey' in ff)
            dd.commit()

        print("Starting has_key()")
        with dd.batch():
            dd['somekey2'] = 4567
            res = 'somekey' in ff
            dd.commit()

        # print "Starting keys()"
        # with dd.batch():
        #    dd['somekey2'] = 458
        #    res = ff.keys()
        #    dd.commit()

        # print "Starting values()"
        # with dd.batch():
        #    dd['somekey2'] = 459
        #    res = ff.values()
        #    dd.commit()

        # print "Starting items()"
        # with dd.batch():
        #    dd['somekey2'] = 460
        #    res = ff.items()
        #    dd.commit()

        print("Starting keys()")
        with dd.batch():
            dd['somekey2'] = 458
            res = set(ff.keys())
            dd.commit()

        print("Starting values()")
        with dd.batch():
            dd['somekey2'] = 459
            res = set(ff.values())
            dd.commit()

        print("Starting items()")
        with dd.batch():
            dd['somekey2'] = 460
            res = set(ff.items())
            dd.commit()

        print("Starting get()")
        with dd.batch():
            dd['somekey2'] = 461
            res = ff.get('somekey5', 123)
            dd.commit()

        print("Starting len()")
        with dd.batch():
            dd['somekey2'] = 462
            res = len(ff)
            dd.commit()

        print("Starting str()")
        with dd.batch():
            dd['somekey2'] = 463
            res = str(ff)
            dd.commit()

        print("Starting iter()")
        with dd.batch():
            dd['somekey2'] = 465
            res = set(ff)
            dd.commit()

        print("Starting query_startswith()")
        with dd.batch():
            dd['somekey2'] = 466
            res = ff.query_startswith('some')
            dd.commit()

        print("Starting query_like()")
        with dd.batch():
            dd['somekey2'] = 466
            res = ff.query_like('some')
            dd.commit()

        print("Starting fetch()")
        dd['k"k'] = 111
        with dd.batch():
            dd['somekey2'] = 464
            res = ff.fetch(['somekey', 'k"k'])
            dd.commit()

    @with_(TempDir, chdir=True)
    def test_wait_journal(self):

        dd = SqlDict("basic.sql")
        # read case
        self.assertEqual(len(dd), 0)
        self.assertFalse(dd._iswrite)
        self.assertEqual(dd._wait_journal(), 2)

        # write case
        dd['key1'] = "value1"
        self.assertTrue(dd._iswrite)
        self.assertEqual(dd._wait_journal(), 1)

        # timeout case - ut
        ff = SqlDict("basic.sql")
        with dd.batch():
            dd['somekey2'] = 456

            with CaptureStdout() as p:
                log.stdout("INFO")
                # To allow sys.stdout redirection
                self.assertEqual(ff._wait_journal(sleeptime=0.001, timeout=0.1), 3)
            self.assertEqual(p.getvalue(), '')
            dd.commit()

        # timeout case - not ut
        with dd.batch():
            dd['somekey3'] = 456
            with CaptureStdout() as p, \
                    MockVar(sepshelve, "IS_UT", False):
                log.stdout("INFO")
                self.assertEqual(ff._wait_journal(sleeptime=0.001, timeout=0.1), 3)
            self.assertIn('Waiting for', p.getvalue())
            self.assertEqual(len(p.getvalue().split('\n')), 2)
            dd.commit()
        print(p.getvalue())

        # code bug 9/18/18
        ff = SqlDict("basic.sql")
        File("basic.sql-journal_BCK").touch()
        self.assertEqual(ff._wait_journal(sleeptime=0.001, timeout=0.1), 2)

    @with_(TempDir, chdir=True)
    def test_check_and_reconnect(self):
        dd = SqlDict("basic.sql")

        # no reconnect necessary
        self.assertEqual(dd.check_and_connect(), 2)

        # reconnect is made
        dd._cfg.rename_write_sleep = 0
        self.assertEqual(dd.check_and_connect(), 1)

    @with_(TempDir, chdir=True)
    def test_commit_reconnect(self):
        dd = SqlDict("basic.sql")
        self.assertEqual(dd.reconnect(), 2)
        with dd.batch():
            dd['key1'] = 123
            self.assertEqual(dd.reconnect(), 1)  # do not reconnect
            dd.commit()

            # with journal
            self.assertEqual(dd.reconnect(initial=True), 2)

    @with_(TempDir, chdir=True)
    def test_is_exist(self):
        # normal case
        dd = SqlDict("basic.sql")
        self.assertTrue(dd._isexist(dd._dbfile))
        dd._conn.close()

        # not existing
        os.unlink(dd._dbfile)
        self.assertFalse(dd._isexist(dd._dbfile))

        # dir not existing
        self.assertFalse(dd._isexist('/somepath/notexist/abc.sqlite'))

        # empty dir
        with TempDir(name=True) as tdir:
            self.assertFalse(dd._isexist(join(tdir, 'new.sqlite')))
            File(join(tdir, 'new.sqlite.delete')).touch()
            self.assertTrue(dd._isexist(join(tdir, 'new.sqlite')))

    @with_(TempDir, chdir=True)
    def test_query_journal_exist(self):
        # Intentional error during query while journal exist
        dd = SqlDict("basic.sql")
        with dd.batch():
            dd['key'] = 123
            dd._cfg.query_retry_sleep = 0.1
            dd._cfg.query_timeout = 0.3
            with self.assertRaisesRegex(Exception, 'Unable to run query'):
                dd._query('SELECT valuex FROM dict ')
            self.assertTrue(exists(dd._journal))
            dd.commit()

    def bench(self):
        """
        Benchmark test - run implicitely

        Benchmark for basic run of write and read
        Result:
        Write 1.692 Secs Total: 300 (basic write+commit, without lock)
        Read 0.495 Secs Total: 300
        """

        print("\n")

        # on current dir
        dbfile = join(LAUNCH_CWD, 'basic.sql')
        File(dbfile).unlink()
        dd = SqlDict(dbfile, gz=True)
        sw = Elapsed()
        for i in range(300):
            dd[str(i)] = i
            # dd.update_withlock(str(i), i)
        print("Write", sw, "Total:", len(dd))

        sw = Elapsed()
        for i in range(300):
            x = dd[str(i)]
        print("Read", sw, "Total:", len(dd))

    def bench2(self):
        """
        Benchmark test - run implicitely

        dd.batch() benchmark:
        ~20K inserts per sec, gz=True
        ~60K inserts per sec, gz=False
        Performance is almost the same between text_only=True vs False for 200K inserts

        .fetch() benchmark:
        ~40K fetch per sec, gz=False
        ~30K fetch per sec, gz=True
        """
        import random

        os.chdir(LAUNCH_CWD)
        if False:  # write
            File('basic.sql').unlink()  # on current dir
            dd = SqlDict("basic.sql", gz=False)
            sw = Elapsed()
            with dd.batch():
                for i in range(1000000):
                    dd[str(i)] = i
                dd.commit()
            print(sw)
            exit(0)
        else:
            dd = SqlDict("basic.sql")

        ss = set()
        random.seed(1)
        for i in range(50000):
            ss.add(str(random.randrange(1000000)))
        sw = Elapsed()
        res = dd.fetch(ss)
        print(sw, len(res))

    def bench3(self):
        """
        Benchmark test - simultaneous test.
        Run this in 3 different machines at the same time. basic.sql must exist first.
        To create initial basic.sql: run 'view_shelve.py basic.sql -startswith d'
        """
        from gadget.shell import HOSTNAME
        import time

        dd = SqlDict("basic.sql")
        sw = Elapsed()
        for i in range(5000):
            dd.update_withlock(str(i) + HOSTNAME, i)
            print(i, sw)
            time.sleep(0.1)
        print(sw)


class SQLcache_tests(TestCase):
    @with_(TempDir, chdir=True)
    def test_basic(self):
        dd = SqlDictCached("basic.sql")
        ff = SqlDict("basic.sql")
        self.assertEqual(dd._cache, {})
        dd['key1'] = 'value1'
        dd['key2'] = 'value2'
        ff['key2'] = 'newvalue'  # change value of the database, not in cache
        del ff['key1']

        self.assertEqual(dd['key1'], 'value1')
        self.assertEqual(dd['key2'], 'value2')  # still old value
        self.assertEqual(dd._cache, {'key2': 'value2', 'key1': 'value1'})
        self.assertTrue('key1' in dd)

        # fresh copy
        gg = SqlDictCached("basic.sql")
        self.assertEqual(gg['key2'], 'newvalue')
        self.assertFalse('key1' in gg)

        # update
        self.assertEqual(dd._cache, {'key2': 'value2', 'key1': 'value1'})
        dd.update({'key4': 'value4'})
        self.assertEqual(dd._cache, {'key2': 'value2', 'key1': 'value1', 'key4': 'value4'})
        self.assertEqual(dd['key2'], 'value2')
        self.assertEqual(dict(dd), {'key2': 'value2',
                                    'key4': 'value4'})  # key1 does not exist here since this iterates the __dict__ items
        self.assertEqual(dict(gg), {'key2': 'newvalue',
                                    'key4': 'value4'})

    @with_(TempDir, chdir=True)
    def test_del(self):
        dd = SqlDictCached("basic.sql")
        ff = SqlDict("basic.sql")
        dd['key1'] = 'value1'
        dd['key2'] = 'value2'
        dd['key3'] = 'value3'
        del dd['key2']
        self.assertEqual(dd._cache, {'key1': 'value1', 'key3': 'value3'})
        self.assertFalse('key2' in dd)
        self.assertFalse('key2' in ff)
        self.assertTrue('key1' in ff)
        self.assertTrue('key1' in dd)

        # fresh dict
        gg = SqlDictCached("basic.sql")
        del gg['key3']
        self.assertEqual(gg._cache, {})
        self.assertEqual(gg.cache_count(), 0)
        self.assertEqual(dict(gg), {'key1': 'value1'})

    @with_(TempDir, chdir=True)
    def test_fetch(self):
        # setup
        dd = SqlDictCached("basic.sql", gz=True)
        ff = SqlDict("basic.sql")  # Do not specify isgz here
        for i in range(100):
            dd[str(i)] = i + 100

        self.assertEqual(dd.fetch({'1', '2', '3', '4', '5', '6'}),
                         {'1': 101, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106})
        ff['1'] = 999
        self.assertEqual(dd['1'], 101)  # from cache data

        self.assertEqual(dd.fetch({'1', '2', '3', '4', '5', '6'}),
                         {'1': 999, '3': 103, '2': 102, '5': 105, '4': 104, '6': 106})
        self.assertEqual(dd['1'], 999)  # from cache data

        # cache delete
        self.assertEqual(dd.cache_count(), 100)
        self.assertIn('9', dd._cache)
        dd.cache_delete('9')
        self.assertEqual(dd.cache_count(), 99)
        self.assertNotIn('9', dd._cache)
        dd.cache_delete('9')  # delete again
        self.assertEqual(dd.cache_count(), 99)

        # cache clear
        dd.cache_clear()
        self.assertEqual(dd.cache_count(), 0)

    @with_(TempDir, chdir=True)
    def test_cache_preread_or_init(self):
        # setup
        dd = SqlDictCached("basic.sql", gz=True)
        ff = SqlDictCached("basic.sql")  # Do not specify isgz here
        dd['key1'] = 'value1'
        dd['key2'] = 'value2'

        # test dd
        self.assertEqual(dd._cache, {'key2': 'value2', 'key1': 'value1'})
        dd.cache_preread_or_init('key3', 'abc')  # key not found
        self.assertIn('key3', dd)
        self.assertEqual(dd._cache, {'key2': 'value2', 'key1': 'value1', 'key3': 'abc'})

        # test ff
        self.assertEqual(ff._cache, {})
        ff.cache_preread_or_init('key1', 'abc')  # key is found
        self.assertNotIn('key3', ff)
        self.assertEqual(ff._cache, {'key1': 'value1'})


class SpecDictBase(TestCase):
    """Base class Unittesting dictionary-like"""

    def basic1(self, db):
        """Add,Read,Delete"""
        self.assertEqual(len(db), 0)  # intial - should be empty

        # basic add
        with db.batch():
            db['k1'] = {1, 5}
            db['k2'] = {6, 7, 8}
            db['k3'] = {10, 11}
            db.commit()
        self.assertEqual(db['k1'], {1, 5})
        self.assertEqual(db['k2'], {6, 7, 8})
        self.assertEqual(db['k3'], {10, 11})
        self.assertEqual(db.get('k1', 'xx'), {1, 5})
        self.assertEqual(db.get('k5', 'xx'), 'xx')
        self.assertEqual(len(db), 3)
        self.assertEqual(dict(db), {'k3': {10, 11},
                                    'k2': {8, 6, 7},
                                    'k1': {1, 5}})

        # basic update
        res = db['k2']
        res.add(14)
        db['k2'] = res
        res = db['k3']
        res.add(15)
        db.update_withlock('k3', res)
        self.assertEqual(db['k2'], {6, 7, 8, 14})
        self.assertEqual(db['k3'], {10, 11, 15})
        with self.assertRaises(KeyError):
            res = db['k5']

        # basic delete and contains
        del db['k2']
        with self.assertRaises(KeyError):
            res = db['k2']
        self.assertEqual(len(db), 2)
        self.assertTrue('k1' in db)
        self.assertFalse('k2' in db)
        self.assertTrue('k3' in db)
        self.assertTrue('k3' in db)   # pragma: no pep8 W601 - backwards compatibility on product code
        self.assertFalse('k2' in db)  # pragma: no pep8 W601 - backwards compatibility on product code
        with self.assertRaises(KeyError):
            del db['k5']  # Not exist

        # None key not allowed
        with self.assertRaises(KeyError):
            db[None] = 23

        # update
        db.update({'k1': {9, 20}, 'k6': {21, 22}}, 1)
        res = db.fetch({'k1', 'k2', 'k6', 'k5', 'k3', 'k7'})
        self.assertEqual(res, {'k1': {9, 20},
                               'k6': {21, 22},
                               'k3': {10, 11, 15}})

        # haskey
        self.assertTrue('k1' in db)
        self.assertFalse('k2' in db)
        self.assertFalse('k7' in db)
        self.assertEqual(dict(db), {'k1': set([9, 20]), 'k3': set([10, 11, 15]), 'k6': set([21, 22])})
        with self.assertRaises(KeyError):
            res = db['k7']

    def basic1n(self, db):
        """Add,Read,Delete"""
        self.assertEqual(len(db), 0)  # intial - should be empty

        # basic add
        with db.batch():
            db[1] = {1, 5}
            db[2] = {6, 7, 8}
            db[3] = {10, 11}
            db.commit()
        self.assertEqual(db[1], {1, 5})
        self.assertEqual(db[2], {6, 7, 8})
        self.assertEqual(db[3], {10, 11})
        self.assertEqual(db.get(1, 'xx'), {1, 5})
        self.assertEqual(db.get(5, 'xx'), 'xx')
        self.assertEqual(len(db), 3)
        self.assertEqual(dict(db), {3: {10, 11},
                                    2: {8, 6, 7},
                                    1: {1, 5}})

        # basic update
        res = db[2]
        res.add(14)
        db[2] = res
        res = db[3]
        res.add(15)
        db.update_withlock(3, res)
        self.assertEqual(db[2], {6, 7, 8, 14})
        self.assertEqual(db[3], {10, 11, 15})
        with self.assertRaises(KeyError):
            res = db[5]

        # basic delete and contains
        del db[2]
        self.assertEqual(len(db), 2)
        self.assertTrue(1 in db)
        self.assertFalse(2 in db)
        self.assertTrue(3 in db)
        with self.assertRaises(KeyError):
            del db[5]  # Not exist

        # None key not allowed
        with self.assertRaises(KeyError):
            db[None] = 23

        # update
        db.update({1: {9, 20}, 6: {21, 22}})
        res = db.fetch({1, 2, 6, 5, 3})
        self.assertEqual(res, {1: {9, 20},
                               6: {21, 22},
                               3: {10, 11, 15}})

        # haskey
        self.assertTrue(1 in db)
        self.assertFalse(2 in db)
        self.assertEqual(dict(db), {1: set([9, 20]), 3: set([10, 11, 15]), 6: set([21, 22])})

    def basic2(self, db):
        """iter keys,values,items"""
        self.assertEqual(len(db), 0)  # intial - should be empty

        # setup
        db['k1'] = 11
        db['k2'] = 12
        db['k3'] = 13

        # iter
        self.assertEqual(sorted(db), ['k1', 'k2', 'k3'])

        # keys
        self.assertEqual(sorted(db.keys()), ['k1', 'k2', 'k3'])

        # values
        self.assertEqual(sorted(db.values()), [11, 12, 13])

        # items
        self.assertEqual({k: v for k, v in list(db.items())}, {'k1': 11, 'k2': 12, 'k3': 13})

        # fetch
        res = db.fetch({'k1', 'k2'})
        self.assertEqual(res, {'k1': 11, 'k2': 12})
        self.assertEqual(db.fetch({}), {})

        # query_startswith
        self.assertEqual(db.query_startswith('k'), {'k3': 13, 'k2': 12, 'k1': 11})
        # query_like is unsupported!

        # get_dbfile
        self.assertTrue(exists(db.get_dbfile()))
        self.assertTrue(isdir(db.get_dbrootdir()))

    def basic2n(self, db):
        """iter keys,values,items"""
        self.assertEqual(len(db), 0)  # intial - should be empty

        # setup
        db[1] = 11
        db[2] = 12
        db[3] = 13

        # iter
        self.assertEqual(sorted(db), [1, 2, 3])

        # keys
        self.assertEqual(sorted(db.keys()), [1, 2, 3])

        # values
        self.assertEqual(sorted(db.values()), [11, 12, 13])

        # items
        self.assertEqual({k: v for k, v in list(db.items())}, {1: 11, 2: 12, 3: 13})

        # fetch
        res = db.fetch({1, 2})
        self.assertEqual(res, {1: 11, 2: 12})
        self.assertEqual(db.fetch({}), {})

        # query_startswith
        # self.assertEqual(db.query_startswith('k'), {3: 13, 2: 12, 1: 11})
        # query_like is unsupported!

        # get_dbfile
        self.assertTrue(exists(db.get_dbfile()))
        self.assertTrue(isdir(db.get_dbrootdir()))

    def basic_text(self, db):
        """Add,Read,Delete"""
        self.assertEqual(len(db), 0)  # intial - should be empty

        # basic add
        with db.batch():
            db['k1'] = "1"
            db['k2'] = "2"
            db['k3'] = "3"
            db.commit()
        self.assertEqual(db['k1'], "1")
        self.assertEqual(db['k2'], "2")
        self.assertEqual(db['k3'], "3")
        self.assertEqual(db.get('k1', 'xx'), "1")
        self.assertEqual(db.get('k5', 'xx'), 'xx')
        self.assertEqual(len(db), 3)
        self.assertEqual(dict(db), {'k3': "3",
                                    'k2': "2",
                                    'k1': "1"})

        # basic update
        db['k2'] = "22"
        db.update_withlock('k3', "33")
        self.assertEqual(db['k2'], "22")
        self.assertEqual(db['k3'], "33")
        with self.assertRaises(KeyError):
            res = db['k5']

        # basic delete and contains
        del db['k2']
        with self.assertRaises(KeyError):
            res = db['k2']
        self.assertEqual(len(db), 2)
        self.assertTrue('k1' in db)
        self.assertFalse('k2' in db)
        self.assertTrue('k3' in db)
        with self.assertRaises(KeyError):
            del db['k5']  # Not exist

        # None key not allowed
        with self.assertRaises(KeyError):
            db[None] = 23

        # update
        db.update({'k1': "111", 'k6': "66"}, 1)
        res = db.fetch({'k1', 'k2', 'k6', 'k5', 'k3', 'k7'})
        self.assertEqual(res, {'k1': "111",
                               'k6': "66",
                               'k3': "33"})


class SpecTest(SpecDictBase):
    """This tests the SqlDict spec (for use with sqldict and gdbm)"""

    @with_(TempDir, chdir=True)
    def test_sqldict(self):
        f1 = SqlDict("basic1.sql")
        self.basic1(f1)
        f2 = SqlDict("basic2.sql")
        self.basic2(f2)
        f3 = SqlDict("basic3.sql", num_keys=True)
        self.basic1n(f3)
        f4 = SqlDict("basic4.sql", num_keys=True)
        self.basic2n(f4)

    @with_(TempDir, chdir=True)
    def test_sqldictcached(self):
        f1 = SqlDictCached("basic1.sql")
        self.basic1(f1)
        f2 = SqlDictCached("basic2.sql")
        self.basic2(f2)


# Windows uses multiprocessing "spawn", so the process target must be a module-level (pickleable) function
def child_proc(ready, filepath):
    ff = SqlDict(filepath)
    ready.value = 1
    for i in range(500):
        ff.update_withlock('ff%s' % i, i + 1000)
        # ff['ff%s' % i] = i+1000
        print(".", end=' ')
    ready.value = 9  # complete


if __name__ == '__main__':  # pragma: no cover
    log.stdout("INFO")
    unittest.main()
