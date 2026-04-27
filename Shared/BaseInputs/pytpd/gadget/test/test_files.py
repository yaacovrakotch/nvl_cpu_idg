#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Various routines on files and iterating on the contents of the files
"""
import os.path

from setenv_unittest import ROOT_ENV, UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE     # must be first import for unittests
from gadget.files import *     # module being tested
import builtins
from gadget.gizmo import Elapsed, vr, MockVar, with_
from gadget.strmore import md5
from gadget.shell import tmpdir, USERNAME, IS_UNIX, IS_WIN, SystemCall, RsyncerBase
from gadget.disk import Chdir, mkdirs
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.helperclass import CaptureStdoutLog, MultiReturn
from gadget.errors import ErrorUser, check, ErrorConfig
from gadget.data_host import DataHost
from unittest.mock import patch, Mock
from pprint import pprint
import gadget.files as files
import io as StringIO


def _pyname():
    """Returns the name of the module being tested"""
    return "files"


class CheckAndDel_tests(TestCase):

    def test_notexist(self):
        name = "/tmp/surenotexistYYAY"
        self.assertTrue(not exists(name), "File should not exist")
        check_and_del(name)   # should pass

    def test_filedel(self):
        with TempDir(chdir=True):
            name = "newfile"
            with open(name, "w") as fh:
                fh.write("test")
            self.assertEqual(os.listdir('.'), [name])
            check_and_del(name)
            self.assertEqual(os.listdir('.'), [])

    def test_dirdel(self):
        with TempDir(name=True) as name:
            with open(join(name, "newfile"), "w") as fh:
                fh.write("test")
            os.mkdir(join(name, "newdir"))
            self.assertTrue(exists(join(name, "newfile")), "File should exist")
            self.assertTrue(isdir(join(name, "newdir")), "Dir should exist")
            check_and_del(name)
            self.assertTrue(not exists(join(name, "newfile")), "File should exist")
            self.assertTrue(not isdir(join(name, "newdir")), "Dir should exist")

    @unittest.skipIf(IS_WIN, 'unix only support digital file permissions')
    def test_error(self):
        with TempDir(name=True) as tdir:
            File(join(tdir, 'somedir', 'f1')).touch(mkdir=True)
            File(join(tdir, 'somedir')).chmod("0400")

            # will raise exception
            with self.assertRaisesRegex(Exception, 'Permission denied'):
                check_and_del(tdir)

            # Do not raise exception
            check_and_del(tdir, error=False)

            # Successful delete
            File(join(tdir, 'somedir')).chmod("0770")  # put it back so it can be deleted
            check_and_del(tdir, error=False)
            self.assertFalse(isdir(tdir))

    def test_mv_on_error(self):
        with TempDir(name=True) as tdir:
            File(join(tdir, 'somedir', 'f1')).touch(mkdir=True)
            File(join(tdir, 'somedir')).chmod("0400")

            # Rename
            check_and_del(join(tdir, 'somedir'), mv_on_error=True)
            self.assertEqual(os.listdir(tdir), ['somedir.1'])

            # Successful delete
            File(join(tdir, 'somedir.1')).chmod("0770")  # put it back so it can be deleted
            check_and_del(tdir, error=False)
            self.assertFalse(isdir(tdir))


class Tempname_tests(TestCase):

    def test_various_tempname(self):
        t1 = tempname()
        t2 = tempname()
        print("t1=", t1)
        print("t2=", t2)
        self.assertFalse(os.path.exists(t1), "t1 should not exist")
        self.assertFalse(os.path.exists(t2), "t2 should not exist")
        self.assertNotEqual(t1, t2)    # "tempname unique name")
        self.assertTrue(os.path.isdir(os.path.dirname(t1)), "tempname dir exist")

    def test_unique_tempname(self):
        # time is mocked
        with MockVar(time, "time", Mock(return_value=123.1)):
            self.assertNotEqual(tempname(), tempname())
            tn = File(tempname()).touch()
            self.assertNotEqual(tn.get_name(), tempname())
            tn.unlink()

        # make sure time.time() is unique
        for ii in range(100):
            self.assertNotEqual(tempname(), tempname())

        # exception case
        with MockVar(files, "exists", Mock(return_value=True)):
            with self.assertRaisesRegex(Exception, "Cannot get temporary name"):
                tempname()

    def test_withspace(self):
        with MockVar(sys, "argv", ["test.py -m comment"]):
            t1 = tempname()
            self.assertFalse(' ' in t1, "Must not have space")

        with MockVar(sys, "argv", [""]):
            t1 = tempname()
            self.assertIn('none', t1)

    def test_tempname_only(self):
        fname = tempname()
        self.assertTrue('test_tempname_only' in fname, "Correct funcname: " + fname)
        fname = tempname("thisstring")
        self.assertTrue('thisstring' in fname, "Correct funcname: " + fname)

    def test_exe(self):
        code = "print('Thequickbrown')"
        with TempName(exe=code) as t:
            res = SystemCall(t.name(), exe=True).run_outonly()
            self.assertIn('Thequickbrown', res)

    def test_basic(self):
        def create1():
            tobj = TempName()
            fname1 = tobj.name()
            fname2 = tobj.fname()
            print("Name:", fname1)
            print("Name:", fname2)
            with open(fname1, "w") as fh:
                fh.write("text")
            with open(fname2, "w") as fh:
                fh.write("text")

            self.assertEqual(tobj.name(), tobj.get_name())
            if IS_UNIX:    # tmp is unix default tempdir
                self.assertTrue(fname1.startswith('/tmp/tmp'), "Correct tmp name")
            parts = basename(fname1).split('.')
            self.assertEqual(len(parts), 4)     # 4 parts
            self.assertRegex(parts[1], r'\w+')   # userename
            self.assertEqual(parts[2], "test_files")   # name of .py file
            self.assertEqual(parts[3], "create1")
            parts = basename(fname2).split('.')
            self.assertEqual(len(parts), 4)     # 4 parts
            self.assertRegex(parts[1], r'\w+')   # userename
            self.assertEqual(parts[2], "test_files")   # name of .py file
            self.assertEqual(parts[3], "create1")

            self.assertTrue(exists(fname1), "Temp file exist1")
            self.assertTrue(exists(fname2), "Temp file exist2")
            self.assertTrue(fname1 != fname2, "Two file names not equal")
            self.assertEqual(fname1, tobj.name())
            return fname1, fname2

        f1, f2 = create1()
        self.assertTrue(exists(f1))
        self.assertTrue(exists(f2))

    def test_compressed(self):
        with TempName(name=True) as tn:
            File(tn).touch().compress(File.gz)
            self.assertTrue(exists(tn + ".gz"), ".gz temp file exist")
        self.assertTrue(not exists(tn + ".gz"), ".gz temp file does not exist")

    def test_with(self):
        def create2():
            with TempName() as tobj:
                fname1 = tobj.name()
                fname2 = tobj.fname()
                print("Name:", fname1)
                print("Name:", fname2)
                with open(fname1, "w") as fh:
                    fh.write("text")
                with open(fname2, "w") as fh:
                    fh.write("text")
                if IS_UNIX:    # tmp is unix default tmpdir
                    self.assertTrue(fname1.startswith('/tmp/tmp'), "Correct name")
                self.assertTrue('.create2' in fname1, "Correct funcname: " + fname1)
                self.assertTrue('.create2' in fname2, "Correct funcname: " + fname2)
                self.assertTrue(exists(fname1), "Temp file exist1")
                self.assertTrue(exists(fname2), "Temp file exist2")
                self.assertTrue(fname1 != fname2, "Two file names not equal")
            self.assertTrue(not exists(fname1), "Temp file not exist1 after with")
            self.assertTrue(not exists(fname2), "Temp file not exist2 after with")

            return fname1, fname2

        f1, f2 = create2()
        self.assertTrue(not exists(f1), "Temp file not exist1")
        self.assertTrue(not exists(f2), "Temp file not exist2")
        self.assertTrue(len(f1) > 6, "Temp filename1 > 6")
        self.assertTrue(len(f2) > 6, "Temp filename2 > 6")

    def test_with_name(self):
        def create3():
            with TempName(name=True) as fname1:
                print("Name:", fname1)
                with open(fname1, "w") as fh:
                    fh.write("text")

                if IS_UNIX:  # tmp is the unix default tempdir
                    self.assertTrue(fname1.startswith('/tmp/tmp'), "Correct name")
                self.assertTrue('.create3' in fname1, "Correct funcname: " + fname1)
                self.assertTrue(exists(fname1), "Temp file exist1")
            self.assertTrue(not exists(fname1), "Temp file not exist1 after with")

            return fname1

        f1 = create3()
        self.assertTrue(not exists(f1), "Temp file not exist1")
        self.assertTrue(len(f1) > 6, "Temp filename1 > 6")

    def test_PYNODEL(self):
        with MockVar(os.environ, 'PYNODELTMP', "test_PYNODEL", isdict=True):
            with TempName(name=True) as fname1:
                File(fname1).touch()
            with TempName(name=True) as fname2:
                File(fname2).touch()
            self.assertTrue(exists(fname1), "Temp file exist1")
            self.assertTrue(exists(fname2), "Temp file exist1")
        self.assertEqual(TempName._addendprint(None), {fname1, fname2})
        os.unlink(fname1)
        os.unlink(fname2)
        self.assertEqual(TempName._addendprint(None), {fname1, fname2})   # it should not error

        with MockVar(os.environ, 'PYNODELTMP', "test_PYNODELNOTF", isdict=True):
            with TempName(name=True) as fname1:
                File(fname1).touch()
            self.assertTrue(not exists(fname1), "Temp file exist1")

    def test_atexit1(self):
        # test the atexit functionality (delete=False)
        code = '''
import sys
sys.path.append(r'%s')
from gadget.files import TempDir
with TempDir(name=True, delete=False) as tname:
   print(tname)
''' % ROOT_ENV
        with TempName(exe=code, name=True) as tname:
            res = SystemCall(tname, exe=True).run_outonly()
            self.assertTrue(isdir(res), "temporary dir should not be deleted")
            shutil.rmtree(res)

    def test_atexit2(self):
        # test the atexit functionality
        # That is, atexit.register() is called FIRST than __del__ destructor.  (This is good)
        # Confirm that this will fail by commenting the atexit.register line in TempName()
        code = '''
import sys
sys.path.insert(0, r'%s')
from gadget.files import TempDir
obj = TempDir(name=True)
print(obj.name())
circular = {'a':obj}
obj.somedict = circular
''' % ROOT_ENV
        with TempName(exe=code, name=True) as tname:
            res = SystemCall(tname, exe=True).run_outonly()
            print('res', res)
            self.assertTrue(not isdir(res), f"temporary dir {res} should be deleted")

    def test_samename(self):
        expect = "/tmp/%s_ut1" % USERNAME
        with TempName(name=True, samename='ut1') as tn:
            File(tn).touch('hello')
            self.assertEqual(tn, expect)
            self.assertTrue(exists(tn))
        self.assertFalse(exists(tn))


class TempDir_tests(TestCase):       # tests that need a tempfile

    def test_startcopy(self):
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', name=True) as tdir:
            self.assertEqual(len(os.listdir(tdir)), 6)     # exactly 6 files
        self.assertFalse(isdir(tdir))

    @with_(MockVar, TempDir, '_special_infra_folder', Mock())
    def test_TempDir(self):
        tdir = TempDir()
        tname = tdir.name()
        self.assertEqual(tdir.name(), tdir.get_name())
        self.assertTrue(isdir(tname), "Is dir existing")
        if IS_UNIX:    # tmp is the default tmpdir in unix
            self.assertTrue(tname.startswith('/tmp/tmp'), "Correct name")
        self.assertTrue('_test_TempDir' in tname, "Correct funcname: " + tname)
        with open(join(tname, "test"), "w") as fh:
            fh.write("testonly")
        self.assertTrue(exists(join(tname, "test")), "File inside exist")
        self.assertEqual(tname, tdir.name())
        tdir.close()
        self.assertFalse(isdir(tname), "close, dir should not exist")
        self.assertIs(tdir.name(), None)

    def test_contextmanager(self):
        # Context manager
        cwd = os.getcwd()
        with TempDir() as tdir:
            tname = tdir.name()
            self.assertEqual(os.getcwd(), cwd)
            self.assertTrue(isdir(tname), "Is dir existing")
            self.assertTrue('_test_contextmanager' in tname, "Correct funcname: " + tname)
            with open(join(tname, "test"), "w") as f:
                f.write("testonly")
            self.assertTrue(exists(join(tname, "test")), "File inside exist")
        self.assertFalse(isdir(tname), "close, dir should not exist")
        self.assertEqual(os.getcwd(), cwd)

    def test_contextmanager_name(self):
        # Context manager
        cwd = os.getcwd()
        with TempDir(name=True) as tdir:
            self.assertEqual(os.getcwd(), cwd)
            self.assertTrue(isdir(tdir), "Is dir existing")
            self.assertTrue('_test_contextmanager' in tdir, "Correct funcname: " + tdir)
            with open(join(tdir, "test"), "w") as fh:
                fh.write("testonly")
            self.assertTrue(exists(join(tdir, "test")), "File inside exist")
            tpath = tdir
        self.assertFalse(isdir(tpath), "close, dir should not exist")
        self.assertEqual(os.getcwd(), cwd)

    def test_TempDir_chdir(self):
        cwd = os.getcwd()
        with TempDir(chdir=True) as tdir:
            tname = tdir.name()
            self.assertEqual(os.getcwd(), tname)
            self.assertTrue(isdir(tname), "Is dir existing")
            with open(join(tname, "test"), "w") as fh:
                fh.write("testonly")
            self.assertTrue(exists(join(tname, "test")), "File inside exist")
        self.assertFalse(isdir(tname), "close, dir should not exist")
        self.assertEqual(os.getcwd(), cwd)

    def test_TempDir_deletefalse(self):
        with TempDir(delete=False) as tdir:
            tpath = tdir.name()
            self.assertTrue(isdir(tpath), "Is dir existing")
        self.assertTrue(isdir(tpath), "Is dir existing")
        shutil.rmtree(tpath)
        self.assertFalse(isdir(tpath), "after del, dir should be deleted")

    def test_chdir_deleted(self):
        # this test case should pass. Testcase found by Jasjit as a bug.
        with TempDir(chdir=True) as td1:
            with TempDir(chdir=True) as td2:
                td1.close()

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_chdir_deleted2(self):
        # this test case should pass. Testcase found by Jasjit as a bug.
        with TempDir(chdir=True) as td1:
            shutil.rmtree(td1.name())
            with TempDir(chdir=True) as td2:
                td1.close()

    def test_other_dir(self):
        self.assertRaisesRegex(Exception, "not a valid directory", TempDir, otherdir="/qqq")
        with TempDir(name=True) as tdir:
            with TempDir(name=True, otherdir=tdir) as tdir2:
                print()
                print(tdir)
                print(tdir2)

                self.assertTrue(isdir(tdir2))
                self.assertTrue(isdir(tdir))
                self.assertNotEqual(tdir, tdir2)
                self.assertGreater(len(tdir2), len(tdir))

            self.assertFalse(isdir(tdir2))
            self.assertTrue(isdir(tdir))

        self.assertFalse(isdir(tdir2))
        self.assertFalse(isdir(tdir))

        # check that calling twice will result to the same name
        with TempDir() as tdir:
            with TempDir(otherdir=tdir.name()) as tdir2:
                self.assertEqual(tdir.name(), tdir.name())
                self.assertEqual(tdir2.name(), tdir2.name())

    @with_(MockVar, TempDir, '_special_infra_folder', Mock())
    def test_samename(self):
        expect = "/tmp/%s_ut1" % USERNAME
        with TempDir(name=True, samename='ut1') as tn:
            if IS_UNIX:
                self.assertEqual(tn, expect)
            self.assertTrue(isdir(tn))
        self.assertFalse(isdir(tn))

        # Two consecutive samename
        with TempDir(name=True, samename='ut1', delete=False) as tn:
            File(join(tn, 'f1')).touch('hello')
        with TempDir(name=True, samename='ut1') as tn:
            self.assertTrue(exists(join(tn, 'f1')))
        self.assertFalse(isdir(tn))

    def test_fail_delete(self):
        # Do not raise exception if delete fails.
        # This is encountered during cron, "Device or Resource busy"

        with TempDir(name=True) as tdir:
            File(join(tdir, 'somedir', 'f1')).touch(mkdir=True)
            File(join(tdir, 'somedir')).chmod("0400")

        File(join(tdir, 'somedir')).chmod("0770")  # put it back so it can be deleted
        shutil.rmtree(tdir)

    @unittest.skipIf(IS_WIN, 'unix only lsltrd')
    def test_display(self):
        # via set_display
        with MockVar(TempDir, 'set_display', True):
            with CaptureStdoutLog() as p:
                with TempDir(name=True) as tdir:
                    File(join(tdir, 'fileaddme')).touch('something')

            print(p.getvalue())
            self.assertIn('fileaddme', p.getvalue())

        # via display=True
        with CaptureStdoutLog() as p:
            with TempDir(name=True, display=True) as tdir:
                File(join(tdir, 'fileaddme2')).touch('something')

        print(p.getvalue())
        self.assertIn('fileaddme2', p.getvalue())

        # normal case (no display)
        with CaptureStdoutLog() as p:
            with TempDir(name=True) as tdir:
                File(join(tdir, 'fileaddme')).touch('something')
        self.assertNotIn('fileaddme', p.getvalue())

    def test_copydir(self):
        # normal case
        with TempDir(name=True) as dest:
            check_and_del(dest)

            with TempDir(name=True, copydir=dest) as tdir:
                File(f'{tdir}/f1').touch()

            self.assertFalse(isdir(tdir))     # must be deleted
            self.assertEqual(os.listdir(dest), ['f1'])

        # exception case
        with TempDir(name=True) as dest:
            check_and_del(dest)

            with self.assertRaises(Exception):
                with TempDir(name=True, copydir=dest) as tdir:
                    File(f'{tdir}/f1').touch()
                    raise Exception("something went wrong")

            self.assertFalse(isdir(tdir))     # must be deleted
            self.assertEqual(os.listdir(dest), ['f1'])

        # dest exist - error
        with TempDir(name=True) as dest:
            with self.assertRaisesRegex(AssertionError, ' must not exist'):
                with TempDir(name=True, copydir=dest) as tdir:
                    pass

        # exception inside copydir, should not exit out
        print('Start of exception copydir====')
        with TempDir(name=True) as dest:
            with TempDir(name=True, copydir=f'{dest}/nd') as tdir:
                File(f'{dest}/nd/abc').touch(mkdir=True)

    @unittest.skipIf(IS_WIN, 'default check in unix')
    def test_windows_d_drive(self):

        with TempDir() as obj:
            # default unix
            self.assertEqual(obj._windows_d_drive(), 1)

            # windows
            with MockVar(shell, "IS_UNIX", False):
                self.assertEqual(obj._windows_d_drive(), 2)

            # windows and D: drive exist and writable
            with MockVar(shell, "IS_UNIX", False):
                with MockVar(files, 'isdir', Mock(return_value=True)):
                    with MockVar(check, 'is_dir_writable', Mock(return_value=None)):
                        self.assertEqual(obj._windows_d_drive(), 3)
                        self.assertTrue(obj.tname.startswith('D:'))

    def test_windows_d_drive_not_writable(self):
        """
        Test case where D drive exists but is not writable
        """

        with TempDir() as obj:
            # Simulate Windows environment where D: drive exists but is not writable
            with MockVar(shell, "IS_UNIX", False):
                with MockVar(files, 'isdir', Mock(return_value=True)):
                    # Mock check.is_dir_writable to raise ErrorConfig (not writable)
                    with MockVar(check, 'is_dir_writable', Mock(side_effect=ErrorConfig("D drive not writable"))):
                        result = obj._windows_d_drive()
                        self.assertEqual(result, 4, "Should return 4 when D drive is not writable")
                        # Verify that tname was not changed to D: drive
                        if not exists('D:'):
                            self.assertFalse(obj.tname.startswith('D:'), "tname should not start with D: when not writable")

    def test_cleanup(self):
        self.assertEqual(TempDir.cleanup(), -1)

        if IS_UNIX:    # unix default
            with MockVar(files, 'IS_UT', False):
                self.assertEqual(TempDir.cleanup(), -2)

        with MockVar(files, 'IS_UT', False), \
                TempDir(name=True) as tdir, \
                MockVar(TempName, 'name', Mock(return_value=f'{tdir}/somedir')), \
                MockVar(shell, 'IS_UNIX', False):

            File(f'{tdir}/{basename(tdir)}b').touch()
            File(f'{tdir}/{basename(tdir)}a').touch(mtime=time.time() - (86400 * 8))
            File(f'{tdir}/abc').touch(mtime=time.time() - (86400 * 8))

            self.assertEqual(TempDir.cleanup(disponly=True), 1)
            self.assertEqual(len(os.listdir(tdir)), 4)   # original

            self.assertEqual(TempDir.cleanup(), 1)       # Do actual deletion

            pprint(os.listdir(tdir))
            self.assertEqual(len(os.listdir(tdir)), 3)   # b, abc and somedir

    @unittest.skipIf(IS_WIN, 'unix only due to groups')
    @unittest.skipIf(not exists('/infrastructure/p6vector/tmp'), 'special test on a machine')
    def test_special_dir(self):
        obj = TempDir()

        # non unix
        with MockVar(shell, 'IS_UNIX', False):
            self.assertEqual(obj._special_infra_folder(), 1)

        # not-exist
        self.assertEqual(obj._special_infra_folder(_folder='/notexist'), 2)

        # non-temp
        with MockVar(obj, 'name', Mock(return_value='/infrastructure')):
            self.assertEqual(obj._special_infra_folder(), 3)

        # real case
        with TempDir(name=True) as tdir:
            self.assertTrue(os.path.exists(tdir))
            self.assertTrue(tdir.startswith('/infrastructure'))


class Tests(TestCase):

    def test_basename_n(self):
        self.assertEqual(basename_n('/tmp/a/b/c/d', 1), 'd')
        self.assertEqual(basename_n('/tmp/a/b/c/d', 2), os.path.normpath('c/d'))
        self.assertEqual(basename_n('/tmp/a/b/c/d', 3), os.path.normpath('b/c/d'))
        self.assertEqual(basename_n('/tmp/a/b/c/d', 4), os.path.normpath('a/b/c/d'))
        self.assertEqual(basename_n('/tmp/a/b/c/d', 5), os.path.normpath('tmp/a/b/c/d'))
        self.assertEqual(basename_n('/tmp/a/b/c/d', 6), os.path.normpath('tmp/a/b/c/d'))

    def test_glob_one_only(self):
        with TempDir(name=True) as tdir:
            # fail case - no files
            with self.assertRaisesRegex(ErrorUser, 'No file found in'):
                glob_one_only(f'{tdir}/*.txt')

            # pass case - 1 file file
            File(f'{tdir}/a.txt').touch()
            self.assertEqual(glob_one_only(f'{tdir}/*.txt'), os.path.normpath(f'{tdir}/a.txt'))

            # fail case - 2 files
            File(f'{tdir}/b.txt').touch()
            with self.assertRaisesRegex(ErrorUser, 'Multiple files found'):
                glob_one_only(f'{tdir}/*.txt')

    def test_strip(self):
        def func():
            arr = ['a', 'b']
            for i in strip(arr, left=True, right=True):
                pass

        arr = ['a', 'b  ', '  c', '  d  ']
        self.assertEqual([ll for ll in strip(arr)], ['a', 'b', 'c', 'd'])
        self.assertEqual([ll for ll in strip(arr, left=True)], ['a', 'b  ', 'c', 'd  '])
        self.assertEqual([ll for ll in strip(arr, right=True)], ['a', 'b', '  c', '  d'])

        self.assertRaises(Exception, func)

    def test_various_grep(self):

        arr = ["The quick brown fox line1  ",
               "The quick brown fox line2",
               "wierd line",
               "It is not quick brown line3"]

        res = [n for n in grep("quick", arr)]
        print(("basic grep:", res))
        self.assertEqual(len(res), 3)   # basic grep

        res = [n for n in grep("^The", arr)]
        print(("^The:", res))
        self.assertEqual(len(res), 2)   # ^The
        self.assertEqual(res, ['The quick brown fox line1  ', 'The quick brown fox line2'])

        res = [n for n in grep("line$", arr)]
        print(("line$:", res))
        self.assertEqual(len(res), 1)   # line$

        res = [n for n in grep("line1$", arr, strip=True)]
        print(("line1$ w/ strip:", res))
        self.assertEqual(len(res), 1)   # line1$ strip=True

        res = [n for n in grep("line1$", arr, r=True, strip=True)]
        print(("line1$ w/ strip:", res))
        self.assertEqual(len(res), 1)   # line1$ strip=True, r=True

        res = [n for n in grep("line1$", arr)]
        print(("line1$ not found:", res))
        self.assertEqual(len(res), 0)   # line1$ not found

        res = [n for n in grep(r"line\d\d$", arr, r=True)]
        print((r"line\d\d$ not found:", res))
        self.assertEqual(len(res), 0)   # line\d\d$ not found regex

        res = [n for n in grep(r"line\d\s*$", arr, r=True)]
        print((r"line\d\s*$ found:", res))
        self.assertEqual(len(res), 3)   # line\d\s*$ found regex

        res = [n for n in grep("^wierd", arr, r=True)]
        print(("^wierd regex:", res))
        self.assertEqual(len(res), 1)   # ^wierd regex

        res = [n for n in grep("^notfound", arr, r=True)]
        print(("^notfound:", res))
        self.assertEqual(len(res), 0)   # ^notfound regex

        arr2 = list(arr)
        arr2[2] = "    \t\twierd line"
        res = [n for n in grep("^wierd", arr2, strip=True)]
        print(("^wierd found with strip:", res))
        self.assertEqual(len(res), 1)   # ^wierd regex strip=True

    def test_various_grepv(self):

        arr = ["The quick brown fox line1  ",
               "The quick brown fox line2",
               "wierd line",
               "It is not quick brown line3"]

        res = [n for n in grepv("quick", arr)]
        print(("basic grep:", res))
        self.assertEqual(len(res), 1)   # basic grep

        res = [n for n in grepv("^The", arr)]
        print(("^The:", res))
        self.assertEqual(len(res), 2)   # ^The
        self.assertEqual(res, ['wierd line', 'It is not quick brown line3'])

        res = [n for n in grepv("line$", arr)]
        print(("line$:", res))
        self.assertEqual(len(res), 3)   # line$

        res = [n for n in grepv("line1$", arr, strip=True)]
        print(("line1$ w/ strip:", res))
        self.assertEqual(len(res), 3)   # line1$ strip=True

        res = [n for n in grepv("line1$", arr, r=True, strip=True)]
        print(("line1$ w/ strip:", res))
        self.assertEqual(len(res), 3)   # line1$ strip=True, r=True

        res = [n for n in grepv("line1$", arr)]
        print(("line1$ not found:", res))
        self.assertEqual(len(res), 4)   # line1$ not found

        res = [n for n in grepv(r"line\d\d$", arr, r=True)]
        print((r"line\d\d$ not found:", res))
        self.assertEqual(len(res), 4)   # line\d\d$ not found regex

        res = [n for n in grepv(r"line\d\s*$", arr, r=True)]
        print((r"line\d\s*$ found:", res))
        self.assertEqual(len(res), 1)   # line\d\s*$ found regex

        res = [n for n in grepv("^wierd", arr, r=True)]
        print(("^wierd regex:", res))
        self.assertEqual(len(res), 3)   # ^wierd regex

        res = [n for n in grepv("^notfound", arr, r=True)]
        print(("^notfound:", res))
        self.assertEqual(len(res), 4)   # ^notfound regex

        arr2 = list(arr)
        arr2[2] = "    \t\twierd line"
        res = [n for n in grepv("^wierd", arr2, strip=True)]
        print(("^wierd found with strip:", res))
        self.assertEqual(len(res), 3)   # ^wierd regex strip=True

    @unittest.skipIf(*is_ut_option("OPTIONAL", message="Cannot use with coverage"))
    def test_various_greptime(self):  # pragma: no cover
        arr = ["The quick brown fox line1  ",
               "The quick brown fox line2"]
        arr = arr * 1000

        # time diff of compiled vs non-compiled
        sw1 = Elapsed()
        for i in range(10):
            res = [n for n in grep(r"^wi\s+", arr, r=True)]
        res_compile = sw1.elapsed()

        sw2 = Elapsed()
        for i in range(10):
            for line in arr:
                if re.search(r"^wi\s+", line):
                    pass
        res_noncompile = sw2.elapsed()
        print(("compiled is faster by:", res_noncompile / res_compile))
        self.assertTrue(res_compile * 2 < res_noncompile, vr("compile={res_compile}, noncompile={res_noncompile}"))

        # time diff of regex and normal search
        sw3 = Elapsed()
        for i in range(10):
            res = [n for n in grep("^wierd", arr)]
        res_normal = sw3.elapsed()

        sw4 = Elapsed()
        for i in range(10):
            res = [n for n in grep(r"^wierd", arr, r=True)]
        res_search = sw4.elapsed()
        print(("normal is faster by:", res_normal / res_search))
        self.assertTrue(res_normal * 1.2 < res_search, vr("normal={res_normal}, search={res_search}"))

    def test_strmode_to_int(self):
        self.assertEqual(strmode_to_int(oct(0o750)), 0o750)
        self.assertEqual(strmode_to_int("0770"), 0o770)
        self.assertEqual(strmode_to_int("770"), 0o770)
        self.assertEqual(strmode_to_int("02770"), 0o2770)
        self.assertRaisesRegex(Exception, "needs to be a string", strmode_to_int, 0o770)
        self.assertRaisesRegex(Exception, "must start with leading 0", strmode_to_int, "1770")
        self.assertRaisesRegex(Exception, "must start with leading 0", strmode_to_int, "12770")
        self.assertRaisesRegex(Exception, "must be digits", strmode_to_int, "177a")
        self.assertRaisesRegex(Exception, "should be 3", strmode_to_int, "17")

    def test_basename_delext(self):
        self.assertEqual(basename_delext('somefile'), 'somefile')
        self.assertEqual(basename_delext('/somefile'), 'somefile')
        self.assertEqual(basename_delext('somefile.ext'), 'somefile')
        self.assertEqual(basename_delext('somefile.ext.morext'), 'somefile')
        self.assertEqual(basename_delext('/somefile.ext.morext'), 'somefile')
        self.assertEqual(basename_delext('/path/path/path/somefile.ext.morext'), 'somefile')
        self.assertEqual(basename_delext('/path/path/path/somefile'), 'somefile')


class File_tests(TestCase):

    def test_windows_rename(self):
        # Chen's feedback since windows behavior is different
        with TempDir(name=True) as tdir:
            File(f'{tdir}/src.txt').touch("source")
            File(f'{tdir}/dest.txt').touch("destination")

            File(f'{tdir}/src.txt').rename('dest.txt')    # in unix, it will overwrite dest.txt
            self.assertEqual(File(f'{tdir}/dest.txt').read(), "source")

    def test_del_ext(self):
        self.assertEqual(File("abc.gz").del_ext(), "abc")
        self.assertEqual(File("abc.bz2").del_ext(), "abc")
        self.assertEqual(File("abc.gz.bz2").del_ext(), "abc")
        self.assertEqual(File("abc..bz2.gz").del_ext(), "abc.")
        self.assertEqual(File("abc.g").del_ext(), "abc.g")
        self.assertEqual(File("a.pobj").del_ext(['.pobj']), "a")
        self.assertEqual(File("a.pobj").del_ext('.pobj'), "a")
        self.assertEqual(File("a.pobj").del_ext(['.gz', '.pobj']), "a")

        self.assertEqual(File("a.pobj.gz").del_ext("."), "a")
        self.assertEqual(File("a..pobj.gz").del_ext("."), "a")
        self.assertEqual(File("apobj").del_ext("."), "apobj")

    @unittest.skipIf(IS_WIN, 'unix only due backslash')
    def test_del_ext2(self):
        # with ext
        self.assertEqual(File("/tmp/some.a.b/a.d.pobj").del_ext("."), "/tmp/some.a.b/a")
        # no args
        self.assertEqual(File("/tmp/some.a.b/a.d.pobj.gz.bz2").del_ext(), "/tmp/some.a.b/a.d.pobj")
        # no ext
        self.assertEqual(File("/tmp/some.a.b/a").del_ext("."), "/tmp/some.a.b/a")
        self.assertEqual(File("/tmp/some.a.b/a").del_ext(), "/tmp/some.a.b/a")
        self.assertEqual(File("/tmp/some.a.b/a.pobj").del_ext(['.pobj']), "/tmp/some.a.b/a")

    def test_get_ext(self):
        self.assertEqual(File("abc").get_ext(), "")
        self.assertEqual(File("abc").get_ext(nocompress=True), "")

        self.assertEqual(File("abc.gz").get_ext(), ".gz")
        self.assertEqual(File("abc.gz").get_ext(nocompress=True), "")

        self.assertEqual(File("abc.pat.gz").get_ext(), ".pat.gz")
        self.assertEqual(File("abc.pat.gz").get_ext(nocompress=True), ".pat")
        self.assertEqual(File("/somepath.ext.something/p/path/abc.pat.data.gz.bz2").get_ext(nocompress=True),
                         ".pat.data")
        self.assertEqual(File("/somepath.ext.something/p/path/abc.pat.data.gz.bz2").get_ext(nocompress=False),
                         ".pat.data.gz.bz2")

    def test_get_extlast(self):
        # no ext
        self.assertEqual(File("abc").get_extlast(), "")
        self.assertEqual(File("abc").get_extlast(nocompress=True), "")

        # with ext .gz
        self.assertEqual(File("abc.gz").get_extlast(), ".gz")
        self.assertEqual(File("abc.gz").get_extlast(nocompress=True), "")

        # with real extension
        self.assertEqual(File("abc.pat.gz").get_extlast(), ".pat.gz")
        self.assertEqual(File("abc.pat.gz").get_extlast(nocompress=True), ".pat")

        # complicated
        self.assertEqual(File("/somepath.ext.something/p/path/abc.pat.data.gz.bz2").get_extlast(nocompress=True),
                         ".data")
        self.assertEqual(File("/somepath.ext.something/p/path/abc.pat.data.gz.bz2").get_extlast(nocompress=False),
                         ".data.gz.bz2")

    def test_count_lines(self):
        with TempName() as t:
            with open(t.name(), "w") as f:
                f.write("line#1\n\n")
                f.write("line#3\n")
                f.write("line#4\n")
            file = File(t.name())
            self.assertEqual(file.count_lines(), 4)
            self.assertEqual(file.count_lines(ignore_empty_lines=True), 3)
            file.close()

    def test_get_name_temporary(self):
        aa = File()
        self.assertRaisesRegex(IOError, "No such file", aa.get_name, True)
        print("Name", aa.get_name())

    def test_exist_realpath(self):
        aa = File()
        self.assertTrue(not aa.exists(), "tmp file must not exist")
        self.assertTrue(not aa.exists(refresh=True), "tmp file must not exist")

        aa = File(sys.executable)
        self.assertTrue(aa.exists(), "executable must exist")
        self.assertTrue(aa.exists(refresh=True), "executable must exist")
        self.assertEqual(aa.realpath(), realpath(sys.executable))

        # another realpath test
        with TempDir(name=True, chdir=True) as tdir:
            aa = File("abc")
            self.assertEqual(aa.realpath(), join(tdir, "abc"))

        # autofind exist
        with TempDir(name=True, chdir=True) as tdir:
            aa = File("abc")
            self.assertFalse(aa.exists())
            self.assertFalse(aa.exists(autofind=True))

            # uncompressed file
            bb = File("abc").touch("def")
            self.assertTrue(aa.exists())
            self.assertTrue(bb.exists())
            self.assertTrue(File('abc.gz').exists(autofind=True))

            # compressed file
            bb.compress('.gz')
            self.assertTrue(bb.exists())
            self.assertFalse(aa.exists())
            self.assertTrue(aa.exists(autofind=True))

    def test_realname(self):
        with TempDir(chdir=True, name=True) as tdir:
            File('A.txt').touch()
            # as-is, exist
            self.assertEqual(File.realname('A.txt'), 'A.txt')
            self.assertEqual(File.realname(f'{tdir}/A.txt'), f'{tdir}/A.txt')
            # lowercase found
            if IS_UNIX:    # Unix is case-sensitive
                self.assertEqual(File.realname('a.txt'), './A.txt')
                self.assertEqual(File.realname(f'{tdir}/a.txt'), f'{tdir}/A.txt')
            # not found
            self.assertEqual(File.realname('b.txt'), 'b.txt')
            self.assertEqual(File.realname(f'{tdir}/b.txt'), f'{tdir}/b.txt')
            # dir not found
            self.assertEqual(File.realname('/oopsie/b.txt'), '/oopsie/b.txt')

            # using File()
            self.assertEqual(File('A.txt').get_name(), 'A.txt')
            self.assertEqual(File(f'{tdir}/A.txt').get_name(), f'{tdir}/A.txt')
            if IS_UNIX:  # Unix is case-sensitive
                self.assertEqual(File('a.txt').get_name(), './A.txt')
                self.assertEqual(File(f'{tdir}/a.txt').get_name(), f'{tdir}/A.txt')
            self.assertEqual(File('b.txt').get_name(), 'b.txt')
            self.assertEqual(File(f'{tdir}/b.txt').get_name(), f'{tdir}/b.txt')

    def test_exists_remote(self):
        with MockVar(RsyncerBase, 'get_remote_machines', Mock(return_value='plxcabc123')):
            fpath = "/remote/path/file.txt"
            with MockVar(SystemCall, "run", Mock(return_value=0)):
                self.assertTrue(File(fpath).exists_remote('sc'))

            with MockVar(SystemCall, "run", Mock(return_value=1)):
                self.assertFalse(File(fpath).exists_remote('sc'))

    def test_stats_remote(self):
        with MockVar(RsyncerBase, 'get_remote_machines', Mock(return_value='plxcabc123')):
            fpath = "/remote/path/file.txt"
            mock_return = "Filename::sample.itpp;User::userA;" \
                          "Modify::2020-03-31 15:12:20.241098000 -0700 (epoch=1585692740);" \
                          "Access::2020-03-31 15:12:20.241098000 -0700 (epoch=1585692740);" \
                          "Change::2020-03-31 15:12:20.241098000 -0700 (epoch=1585692740);Size::0;" \
                          "Permissions::640/-rw-r-----;Gid::3947/gdlusers;FileType::regular empty file"

            # Passing Case
            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(0, mock_return, ''))):
                stats = File(fpath).stats_remote('sc')
                self.assertEqual(len(stats), 9)
                self.assertEqual(stats['User'], 'userA')
                self.assertEqual(stats['Filename'], 'sample.itpp')

            # Failing Case
            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(1, '', 'Error Msg'))):
                with self.assertRaisesRegex(IOError, 'Error Msg'):
                    File(fpath).stats_remote('sc')

    def test_push_remote(self):
        fpath = "/remote/path/file.txt"
        with TempDir(name=True) as tdir:
            with MockVar(RsyncerBase, "do_rsync", Mock(return_value=True)):
                src = os.path.join(tdir, "file.txt")
                File(src).push_remote(fpath, 'sc')

    def test_another_remote(self):
        fpath = "/remote/path/file.txt"
        with MockVar(RsyncerBase, "do_rsync", Mock(return_value=True)):
            File(fpath).another_remote(fpath, 'pg', 'sc')

    def test_copy_remote(self):
        fpath = "/remote/path/file.txt"
        with TempDir(name=True) as tdir:
            with MockVar(RsyncerBase, "do_rsync", Mock(return_value=True)):
                dest = os.path.join(tdir, "file.txt")
                File(fpath).copy_remote(dest, 'sc')

                # Do it with dir getting created
                dest = os.path.join(tdir, "new_dir", "file.txt")
                File(fpath).copy_remote(dest, 'sc')
                self.assertTrue(isdir(os.path.join(tdir, "new_dir")))

    def test_unlink(self):
        with TempDir(chdir=True):
            # File does not exist
            aa = File()
            aa.unlink()    # Should do nothing since file does not exist

            # File exist
            aa.touch()
            self.assertTrue(aa.exists(), "tmp file must exist")
            aa.unlink()
            self.assertTrue(not aa.exists(), "tmp file must not exist")

    def test_safeunlink(self):
        with TempDir(chdir=True):
            # File does not exist
            aa = File()
            self.assertFalse(aa.safeunlink(), "tmp file shouldn't exist")  # Should do nothing since file does not exist

            # File exist
            aa.touch()
            self.assertTrue(aa.exists(), "tmp file must exist")
            # chmodding to read only
            aa.chmod('0440', ignoreError=False)
            self.assertFalse(aa.safeunlink(), "tmp file should fail to delete due to lack of permissions")
            aa.chmod('0770', ignoreError=False)
            tmpname = aa.name
            aa.name = "YouWillNeverfindMe"
            self.assertFalse(aa.safeunlink(), "tmp file should fail to delete due to illegal name")
            aa.name = tmpname
            aa.touch()
            with patch("gadget.files.File.unlink", Mock(side_effect=Exception('unexpected!'))):
                self.assertFalse(aa.safeunlink(), "tmp file should fail with unexpected exception")

            self.assertTrue(aa.exists(), "tmp file must exist")
            self.assertTrue(aa.safeunlink(), "tmp file should be deleted successfully")
            self.assertTrue(not aa.exists(), "tmp file must not exist")

        # Broken link
        with TempDir(chdir=True):
            os.symlink("notfound", "somelink")
            self.assertTrue(islink("somelink"))
            self.assertFalse(exists("somelink"))
            File("somelink").unlink()
            self.assertFalse(islink("somelink"))

    def test_autofind(self):
        # found file is without compression
        with TempDir(chdir=True):
            File("abc").touch()
            self.assertEqual(File("abc", autofind=True).get_name(), "abc")
            self.assertEqual(File("abc.gz", autofind=True).get_name(), "abc")
            self.assertRaises(IOError, File, "abc.d", autofind=True)

        # found file with compression
        with TempDir(chdir=True):
            File("abc.gz").touch()
            self.assertEqual(File("abc", autofind=True).get_name(), "abc.gz")
            self.assertEqual(File("abc.bz2", autofind=True).get_name(), "abc.gz")
            self.assertEqual(File("abc.gz", autofind=True).get_name(), "abc.gz")
            self.assertEqual(File("abc.bz2.gz", autofind=True).get_name(), "abc.gz")

    def test_autoregex(self):
        # Testing regex works in cwd
        with TempDir(chdir=True):
            File("abc.txt").touch()
            File("bcd.txt.gz").touch()
            File("xyz.tmp").touch()
            self.assertEqual(File(r".tmp", autoregex=True).get_name(), "xyz.tmp")
            self.assertEqual(File(r"abc.", autoregex=True).get_name(), "abc.txt")
            self.assertEqual(File(r".txt$", autoregex=True).get_name(), "abc.txt")
            self.assertEqual(File("bcd", autoregex=True).get_name(), "bcd.txt.gz")
            self.assertRaisesRegex(IOError, "Multiple", File, r".txt", autoregex=True)
            self.assertRaisesRegex(IOError, "No such file", File, r".blah", autoregex=True)

        # Testing regex works with a fullpath
        with TempDir(name=True) as tdir:
            File(join(tdir, "abc.txt")).touch()
            File(join(tdir, "bcd.txt.gz")).touch()
            File(join(tdir, "wxyz.tmp")).touch()
            self.assertEqual(File(join(tdir, r".tmp"), autoregex=True).get_name(), join(tdir, "wxyz.tmp"))
            self.assertRaises(IOError, File, join(tdir, r".txt"), autoregex=True)

    def test_existleaf(self):
        # prev=False
        self.assertEqual(File("/tmp/surenotexist/a/b/c/d").existleaf(), "/tmp")
        with TempDir(name=True) as td:
            self.assertEqual(File(td).existleaf(), td)
            self.assertEqual(File(join(td, "a", "bb", "cc")).existleaf(), td)

        # prev=True
        self.assertEqual(File("/tmp/surenotexist/a/b/c/d").existleaf(prev=True), "/tmp/surenotexist")
        with TempDir(name=True) as td:
            self.assertEqual(File(td).existleaf(prev=True), None)
            self.assertEqual(File(join(td, "a", "bb", "cc")).existleaf(prev=True), join(td, "a"))

        # new=True
        self.assertEqual(File("/tmp/surenotexist/a/b/c/d").existleaf(new=True),
                         ['/tmp/surenotexist/a/b/c/d',
                          '/tmp/surenotexist/a/b/c',
                          '/tmp/surenotexist/a/b',
                          '/tmp/surenotexist/a',
                          '/tmp/surenotexist'])

        # one leaf
        self.assertEqual(File("/tmp").existleaf(new=True), [])
        self.assertEqual(File("/tmpnotexist").existleaf(new=True), ["/tmpnotexist"])
        self.assertEqual(File("/tmpnotexist").existleaf(), '/')
        self.assertEqual(File("/tmpnotexist").existleaf(prev=True), '/tmpnotexist')

        # non relative path
        with Chdir("/"):
            self.assertEqual(File("tmp/surenotexist").existleaf(new=True), ["tmp/surenotexist"])
            self.assertEqual(File("tmp/surenotexist").existleaf(), 'tmp')
            self.assertEqual(File("tmp/surenotexist").existleaf(prev=True), 'tmp/surenotexist')

        # one leaf not exist
        self.assertEqual(File("tmpnotexist").existleaf(new=True), ["tmpnotexist"])
        self.assertEqual(File("tmpnotexist").existleaf(), '')
        self.assertEqual(File("tmpnotexist").existleaf(prev=True), 'tmpnotexist')

    def test_logprint(self):
        with TempDir(chdir=True):
            # intial file
            File("abc").logprint("qwr")
            with open("abc") as fh:
                self.assertRegex(fh.read(), ": qwr")
            with open("abc") as fh:
                self.assertEqual(len(fh.read().split('\n')), 2)

            # multi line
            ll = File("abc")
            ll.logprint("line1")
            ll.logprint("line2")
            ll.logprint("line3")
            ll.close()
            ll.logprint("line4")
            ll.close()
            with open("abc") as fh:
                self.assertEqual(len(fh.read().split('\n')), 6)

            # with compression
            ll.compress(File.gz)
            self.assertRaises(Exception, ll.logprint, "text")

            # opened fh
            with File("abc")as ll:
                ll.touch()
                ll.fh()
                ll.logprint("line1")
                ll.logprint("line2")
                self.assertEqual(len(ll.read().split('\n')), 3)

            # fail - default
            with self.assertRaises(IOError):
                File('/somedir/xx').logprint('text')

            # fail - ignore
            File('/somedir/xx').logprint('text', ignore_err=True)

    def test_age_onceaday(self):
        with TempDir(chdir=True):
            # age
            aa = File("abc").touch()
            self.assertLess(aa.age(), 10)
            self.assertGreater(aa.age(), 0.0)
            with self.assertRaisesRegex(OSError, 'sure_not_found'):
                File("/sure_not_found").age()
            self.assertEqual(File("/sure_not_found").age(error=False), -1)

            # onceaday
            self.assertTrue(aa.onceaday(0), "Must be True since age is zero")
            self.assertFalse(aa.onceaday(), "Must be False since file is recently touched")

            self.assertTrue(File("newfile").onceaday(), "Must be True since new file")
            self.assertFalse(File("newfile").onceaday(), "Must be False since file already exist")

            # onceaweek
            self.assertTrue(aa.onceaweek(0), "Must be True since age is zero")
            self.assertFalse(aa.onceaweek(), "Must be False since file is recently touched")

    def test_get_name(self):
        with TempDir(chdir=True, name=True) as tdir:
            aa = File("abc")
            self.assertEqual(aa.get_name(), "abc")

            # exist check
            self.assertRaises(IOError, aa.get_name, True)
            aa.touch()
            self.assertEqual(aa.get_name(True), "abc")

            # abspath and realpath
            mkdirs("odir")
            os.symlink("odir", "ndir")
            bb = File(join("ndir", "f1")).touch()
            self.assertEqual(bb.get_name(), join("ndir", "f1"))
            self.assertEqual(bb.get_name(abspath=True), os.path.abspath(join("ndir", "f1")))
            self.assertEqual(bb.get_name(realpath=True), os.path.realpath(join("ndir", "f1")))
            self.assertNotEqual(bb.get_name(abspath=True), bb.get_name(realpath=True))

            # dirname and basename
            self.assertEqual(bb.get_name(abspath=True, dirname=True), join(tdir, "ndir"))
            self.assertEqual(bb.get_name(abspath=True, basename=True), "f1")
            self.assertEqual(bb.get_name(realpath=True, dirname=True), join(tdir, "odir"))
            self.assertEqual(bb.get_name(dirname=True), join(tdir, "ndir"))
            self.assertEqual(bb.get_name(), join("ndir", "f1"))  # no change
            self.assertEqual(bb.get_name(basename=True), "f1")
            self.assertEqual(bb.get_name(basename=True, dirname=True), "ndir")
            self.assertEqual(bb.get_name(realpath=True, basename=True, dirname=True), "odir")
            self.assertEqual(bb.get_name(abspath=True, basename=True, dirname=True), "ndir")

            # abspath provided
            fa = join(tdir, "ndir", "f1")
            self.assertEqual(File(fa).get_name(), fa)
            self.assertEqual(File(fa).get_name(abspath=True), fa)
            self.assertEqual(File(fa).get_name(realpath=True), join(tdir, "odir", "f1"))
            self.assertEqual(File(fa).get_name(basename=True), "f1")
            self.assertEqual(File(fa).get_name(dirname=True), join(tdir, "ndir"))
            self.assertEqual(File(fa).get_name(basename=True, dirname=True), "ndir")
            self.assertEqual(File(fa).get_name(realpath=True, basename=True, dirname=True), "odir")

            # basenoext
            self.assertEqual(File(fa + ".gz").get_name(basename=True), "f1.gz")
            self.assertEqual(File(fa + ".gz").get_name(basenoext=True), "f1")
            self.assertEqual(File(fa + ".pat.gz").get_name(basenoext=True), "f1.pat")

            # string representation
            fobj = File(fa)
            self.assertEqual("%s" % fobj, fobj.get_name())

    def test_autofind_func(self):
        with TempDir(chdir=True):
            File("abc.gz").touch()
            self.assertEqual(File("abc").autofind(), "abc.gz")
            self.assertIs(File("abcd").autofind(), None)

    def test_newfile(self):
        with TempDir(chdir=True):
            aa = File("abc")
            self.assertEqual(aa.newfile(), "abc")
            aa.touch()
            self.assertEqual(aa.newfile(), "abc.1")
            File("abc.1").touch()
            self.assertEqual(aa.newfile(), "abc.2")

            with MockVar(files, "exists", Mock(return_value=True)):
                self.assertRaisesRegex(Exception, "exceeded", aa.newfile)

    @unittest.skipIf(IS_WIN, 'unix only because of lsltrd()')
    def test_lsltrd(self):
        with TempDir(chdir=True):
            aa = File("newfile").touch()

            # pass case
            res = aa.lsltrd()
            print(res)
            self.assertIn("newfile", res)

            # fail case
            self.assertIn("is not found", File("newfilenotfound").lsltrd())

    def test_md5(self):
        with TempName(name=True) as tname:
            File(tname).touch(''.join('This is a long text.' for _ in range(10000)))
            self.assertEqual(File(tname).md5(readsize=10000), '2379eba69a9c80b7095fa41e25a58dec')
            self.assertGreater(os.path.getsize(tname) / 10000, 5)   # at least 5 iterations

            # maxiteration error
            with self.assertRaisesRegex(Exception, "maximum iteration"):
                File(tname).md5(readsize=10000, maxiter=3)

    @unittest.skipIf(IS_WIN, 'unix only sha1sum')
    def test_sha1(self):
        inp = realpath(__file__)
        expect = SystemCall('sha1sum %s' % inp).run_outonly().split()[0]
        self.assertEqual(len(expect), 40)
        self.assertEqual(File(inp).sha1(readsize=10000), expect)
        self.assertGreater(os.path.getsize(inp) / 10000, 5)   # at least 5 iterations

        # maxiteration error
        with self.assertRaisesRegex(Exception, "maximum iteration"):
            File(inp).sha1(readsize=10000, maxiter=3)

        # size check
        with TempName(name=True) as tn:
            text = b'1234567890'
            with open(tn, 'wb') as fh:
                fh.write(text)
            self.assertEqual(len(File(tn).read()), 10)
            self.assertEqual(File(tn).sha1(readsize=10), sha1(text))

            text = b'123456789'
            with open(tn, 'wb') as fh:
                fh.write(text)
            self.assertEqual(len(File(tn).read()), 9)
            self.assertEqual(File(tn).sha1(readsize=10), sha1(text))

            text = b'12345678901'
            with open(tn, 'wb') as fh:
                fh.write(text)
            self.assertEqual(len(File(tn).read()), 11)
            self.assertEqual(File(tn).sha1(readsize=10), sha1(text))
            self.assertEqual(File(tn).sha1(readsize=1), sha1(text))
            self.assertEqual(File(tn).sha1(readsize=100), sha1(text))

        # test sha when binary is True/False and file is compressed.
        with TempDir(chdir=True, name=True):
            fobj = File('txt').touch('aaa aaa aaa')
            sha_orig = fobj.sha1()
            fobj.compress(File.gz)
            sha_bin = fobj.sha1()
            sha_txt = fobj.sha1(binary=False)
            self.assertEqual(sha_orig, sha_txt)
            self.assertNotEqual(sha_bin, sha_txt)

    @unittest.skipIf(IS_WIN, 'unix only to use pwd')
    def test_owner_name(self):
        with TempDir(name=True) as tdir:
            aa = File(join(tdir, 'name')).touch()
            self.assertEqual(aa.owner_name(), USERNAME)

    def test_update_printable(self):
        with TempDir(chdir=True):
            ff = File('aa').touch('abc\bdef\rghi klm\n123\b\b\r456\n')
            ff.update_printable()
            ff.update_printable()
            self.assertEqual(ff.read(), 'abcdef\nghi klm\n123\n456\n')
            self.assertEqual(os.listdir('.'), ['aa'])

            ff = File('bb').touch('\r\rabc\b\rdef\r\bghi klm\r\n\r123\b\b\r\r456\n\r\b\r')
            ff.update_printable()
            if IS_UNIX:
                self.assertEqual(ff.read(), '\n\nabc\ndef\nghi klm\n\n123\n\n456\n\n\n')
            else:
                self.assertEqual(ff.read(), '\n\nabc\ndef\nghi klm\n\n\n123\n\n456\n\n\n')

    def test_is_text(self):
        with File(sys.executable) as file:
            self.assertFalse(file.is_text())

        with TempDir(chdir=True):
            # basic
            with File('myfile') as aa:
                aa.touch('\n\n some text \n\nHel~lo\ntab\ttab\bline\nline\n')
                self.assertTrue(aa.is_text())
                aa.compress(aa.gz)
                self.assertTrue(aa.is_text())

            # more special chars
            with File('myfile_m') as aa:
                aa.touch('\n\n some %stext \rHel~lo\ntab\ttab\bline\nline\n' % chr(13))
                self.assertTrue(aa.is_text())

            # non text file
            nontext = '\ntext\nnon%stext\n' % chr(1)
            with File('myfile2') as aa:
                aa.touch(nontext)
                self.assertFalse(aa.is_text())
                aa.compress(aa.gz)
                self.assertFalse(aa.is_text())

            # more than 100 lines, with nontext at end
            with File('myfile3') as aa:
                aa.touch('%s%s' % ('\n'.join('text' for x in range(200)), nontext))
                self.assertTrue(aa.is_text())
                aa.compress(aa.gz)
                self.assertTrue(aa.is_text())

            # less than 100 lines, with nontext at end
            with File('myfile4') as aa:
                aa.touch('%s%s' % ('\n'.join('text' for x in range(50)), nontext))
                self.assertFalse(aa.is_text())
                aa.compress(aa.gz)
                self.assertFalse(aa.is_text())

    def test_get_between(self):
        with TempDir(chdir=True):
            ff = File("aa").touch('''
header
startme
text1
text2
endme
endline
''')
            self.assertEqual(ff.get_between("startme", "endme"), ['text1', 'text2'])
            self.assertEqual(ff.get_between("nonefound", "nonefound"), [])
            self.assertEqual(ff.get_between("endme", "nonfound"), ['endline'])

    def test_open_error_message(self):
        self.assertIn('No such file', File('/notfound').open_error_message())
        with TempName(name=True) as tn:
            self.assertIsNone(File(tn).touch().open_error_message())

    def test_get_size_uncompresed(self):
        with TempDir(name=True) as tdir:
            fname = join(tdir, "f1.gz")
            f1 = File(fname).touch("abcdef")
            raw_size = os.path.getsize(f1.get_name())
            print("raw_size: ", raw_size)
            self.assertEqual(f1.get_size_uncompresed(), 6)
            self.assertNotEqual(raw_size, 6)
            self.assertEqual(f1.get_name(), fname)      # make sure obj did not change

            # uncompress it
            f1.uncompress()
            self.assertEqual(f1.get_size_uncompresed(), 6)
            self.assertEqual(f1.get_name(), fname.replace('.gz', ''))
            self.assertEqual(os.path.getsize(f1.get_name()), 6)

            # bz.gz2
            f2 = File(join(tdir, "f2.gz.bz2")).touch("abcdef")
            self.assertEqual(f2.get_size_uncompresed(), 6)

            # plain file
            f3 = File(join(tdir, "f3")).touch("abcdef")
            self.assertEqual(f3.get_size_uncompresed(), 6)

    def test_size_zero_unlink(self):
        with TempDir(chdir=True):
            # Case 1 - size ==0 and old, should delete
            f1 = File()
            # File exists, size = 0
            f1.touch()
            self.assertTrue(f1.exists(), "tmp file must exist")
            # Mocking age for a stale file - will delete
            with patch("gadget.files.File.age", Mock(return_value=130)):
                self.assertTrue(f1.size_zero_unlink(timeout=120), "file should be unlinked and method return true")
                self.assertFalse(os.path.exists(f1.get_name()), "file should not exist on disk anymore")

            # Case 2 - old age but not size==0, don't delete
            f2 = File()
            f2.touch(appendtxt="BLAH")
            with patch("gadget.files.File.age", Mock(return_value=130)):
                self.assertFalse(f2.size_zero_unlink(timeout=120), "file shouldn't be unlinked, it's not 0")
                self.assertTrue(os.path.exists(f2.get_name()), "file should still exist on disk")

            # Case 2 - not old age but size==0, don't delete
            f3 = File()
            f3.touch()
            self.assertFalse(f3.size_zero_unlink(timeout=200), "file shouldn't be unlinked, it's still fresh!")
            self.assertTrue(os.path.exists(f3.get_name()), "file should still exist on disk")

    def test_tail(self):
        with TempDir(name=True) as tdir:
            # normal file - without EOL char
            f1 = File(join(tdir, 'plain.txt')).touch('''
1
2
3
4
5
6
7''')
            self.assertEqual(f1.tail(3), ['5', '6', '7'])
            self.assertEqual(len(list(f1)), 8)

            # normal file - with EOL char
            f1.touch('\n')
            self.assertEqual(len(list(f1)), 8)
            self.assertEqual(f1.tail(3), ['5', '6', '7'])

            # compressed file
            f1.compress(File.gzbz2)
            self.assertEqual(f1.tail(3), ['5', '6', '7'])

            # large file - without EOL char
            line = 'some large line the quick brown fox jumps over the lazy dog over and over again'
            large = '\n'.join(line for _ in range(10000))
            self.assertEqual(len(large), 799999)
            f2 = File(join(tdir, 'large.txt')).touch(large)
            self.assertEqual(f2.tail(2), [line, line])

            # large file - without EOL char
            f1.touch('\n')
            self.assertEqual(f2.tail(2), [line, line])

            # compressed file
            f2.compress(File.gzbz2)
            self.assertEqual(f2.tail(2), [line, line])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_safeopen(self):
        ff = UT_DIR + '/TGLXXXXRXH35H00S025/TPL/Modules/TPI_IDV/InputFiles/IDV_patmod.txt'
        result = list(File(ff).safeopen())
        self.assertEqual(len(result), 95)
        self.assertEqual(result[0], '## This is an example of pattern modify input file')

    def test_tarfolder(self):
        with TempDir(name=True, chdir=True) as tdir:
            File(f'src/.git/abc').touch(mkdir=True)
            File(f'src/f2').touch(mkdir=True)
            File(f'src/dir1/f1').touch(mkdir=True)
            File(f'src/dir1/.git/abc').touch(mkdir=True)
            TarFolder('src', 'dest/tp.tar.gz')
            DataHost().do_untar('dest/tp.tar.gz')
            self.assertEqual(set(os.listdir('dest')), {'f2', 'dir1'})
            self.assertEqual(os.listdir('dest/dir1'), ['f1'])


class FileChmodChgrpGetmode_tests(TestCase):

    @unittest.skipIf(IS_WIN, 'unix only support digital file permissions')
    def test_chmod_normal_4bits(self):
        with TempName(name=True) as tmp:
            open(tmp, "w").close()
            os.chmod(tmp, 0000)
            File(tmp, fast=True).chmod("0750")
            self.assertEqual(oct(os.stat(tmp).st_mode & 0o777), oct(0o750))
            self.assertEqual(File(tmp).get_mode(), "0750")

    @unittest.skipIf(IS_WIN, 'unix only support digital file permissions')
    def test_chmod_normal_3bits(self):
        with TempName(name=True) as tmp:
            open(tmp, "w").close()
            os.chmod(tmp, 0000)
            File(tmp, fast=True).chmod("750")
            self.assertEqual(oct(os.stat(tmp).st_mode & 0o777), oct(0o750))
            self.assertEqual(File(tmp).get_mode(), "0750")

    @unittest.skipIf(IS_WIN, 'unix only support digital file permissions')
    def test_chmod_normal_3bits_ierror(self):
        with TempName(name=True) as tmp:
            open(tmp, "w").close()
            os.chmod(tmp, 0000)
            File(tmp, fast=True).chmod("750", True)
            self.assertEqual(oct(os.stat(tmp).st_mode & 0o777), oct(0o750))
            self.assertEqual(File(tmp).get_mode(), "0750")

    def test_chmod_not_string(self):
        with TempName(name=True) as tmp:
            open(tmp, "w").close()
            self.assertRaises(Exception, File(tmp, fast=True).chmod, 0o750)

    def test_chmod_wrong_length(self):
        with TempName(name=True) as tmp:
            open(tmp, "w").close()
            self.assertRaises(Exception, File(tmp, fast=True).chmod, "000750")
            self.assertRaises(Exception, File(tmp, fast=True).chmod, "50")
            self.assertRaises(Exception, File(tmp, fast=True).chmod, "")

    def test_chmod_not_digits(self):
        with TempName(name=True) as tmp:
            open(tmp, "w").close()
            self.assertRaises(Exception, File(tmp, fast=True).chmod, "abc")
            self.assertRaises(Exception, File(tmp, fast=True).chmod, "abcd")

    @unittest.skipIf(IS_WIN, 'unix only due to groups')
    @with_(MockVar, TempDir, '_special_infra_folder', Mock())
    def test_chgrp(self):
        with TempDir(chdir=True, name=True) as tdir:
            aa = File("abc").touch()

            # it should do nothing
            with MockVar(os, "chown", Mock(side_effect=Exception)):
                self.assertIs(aa.chgrp(None), aa)

        aa = File(tdir)   # should not exist
        with open(tdir, 'w') as fh:
            pass

        self.assertTrue('gdlusers' not in aa.lsltrd(), aa.lsltrd())
        aa.chgrp('gdlusers')
        self.assertTrue('gdlusers' in aa.lsltrd(), aa.lsltrd())

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_chgrp_keep_permissions(self):
        # chgrp should keep permissions after chgrp
        gdlusers_gid = os.stat('/p/pde/tvpv/mtl').st_gid
        with TempDir(name=True) as tdir:
            targ = join(tdir, 'somedir')
            mkdirs(targ)
            orig_mode = os.stat(targ).st_mode & 0o77777
            File(targ).chgrp(gdlusers_gid)   # this will change permissions
            new_mode = os.stat(targ).st_mode & 0o77777
            self.assertEqual(orig_mode, new_mode)


class FileFH_tests(TestCase):

    def setUp(self):
        self.tmp = tempname()
        print(("Tempname: %s" % self.tmp))

        self.msg = "The quick\n"

        # Create the file
        with open(self.tmp, "w") as fh:
            fh.write(self.msg)

    def tearDown(self):
        if exists(self.tmp):
            os.unlink(self.tmp)
        for ext in ".gz .bz2 .gz.bz2 .bz2.gz".split():
            if exists(self.tmp + ext):
                os.unlink(self.tmp + ext)

    def test_context(self):
        with File(self.tmp) as f:
            res = f.read()

        self.assertEqual(res, self.msg)

    def test_iter(self):
        with TempName(name=True) as tn:
            with open(tn, "w") as fh:
                fh.write('''line1
line2
line3
''')
            # iterate on the file
            ctr = 0
            for line in File(tn):
                ctr = ctr + 1
            self.assertEqual(ctr, 3)

            File(tn).compress(File.gz)
            self.assertTrue(exists(tn + ".gz"), "gz file must exist")

            # iterate on the file - compressed
            ctr = 0
            for line in File(tn, autofind=True):
                ctr = ctr + 1
            self.assertEqual(ctr, 3)
            File(tn, autofind=True).compress(File.none)

            # iterate on the object - two consecutive
            obj = File(tn)
            self.assertEqual(count_iter(obj), 3)
            self.assertEqual(count_iter(obj), 3)

    def test_iter_encoding(self):
        # checks encoding and iterator of all types
        with TempDir(name=True) as tdir:
            ff = File(f'{tdir}/aa').touch('1\n2\n3\n')
            expect = ['1\n', '2\n', '3\n']
            self.assertEqual(list(ff), expect)

            # gz
            self.assertEqual(os.listdir(tdir), ['aa'])
            ff.compress(File.gz)
            self.assertEqual(os.listdir(tdir), ['aa.gz'])
            self.assertEqual(list(ff), expect)
            ff.compress(File.none)

            # bz2
            self.assertEqual(os.listdir(tdir), ['aa'])
            ff.compress(File.bz2)
            self.assertEqual(os.listdir(tdir), ['aa.bz2'])
            self.assertEqual(list(ff), expect)
            ff.compress(File.none)

            # gzbz2
            self.assertEqual(os.listdir(tdir), ['aa'])
            ff.compress(File.gzbz2)
            self.assertEqual(os.listdir(tdir), ['aa.gz.bz2'])
            self.assertEqual(list(ff), expect)
            ff.compress(File.none)

    def test_close(self):
        with TempName(name=True) as tn:
            with open(tn, "w") as fh:
                fh.write('''line1
line2
line3
''')
            obj = File(tn)
            obj.close()
            obj.close()

        # large file
        with TempDir(name=True) as tdir:
            aa = File(join(tdir, "af")).touch('\n'.join(str(x) for x in range(500000)))
            aa.compress(aa.gz)
            for line in aa:
                self.assertEqual(line, '0\n')
                break
            for line in aa.fh():
                self.assertEqual(to_str(line), '0\n')
                break
            for line in aa.chomp():
                self.assertEqual(line, '0')
                break

    @unittest.skipIf(IS_WIN, 'unix only because of lsltrd()')
    def test_close_disp_files(self):
        # Do not show any files - default
        with CaptureStdoutLog() as p:
            with TempDir(name=True) as td2:
                curtime = time.time()
                File(join(td2, "testfile_b1")).touch('\n', mtime=curtime - 10)
                File(join(td2, "testfile_b2")).touch('\n', mtime=curtime - 9)
                File(join(td2, "testfile_b3")).touch('\n', mtime=curtime - 8)

        self.assertEqual(len(p.getvalue().split('\n')), 1)    # newline only

        # multiple files in TempDir - show only 5
        with CaptureStdoutLog() as p,\
                MockVar(TempDir, "set_display", 5):
            with TempDir(name=True) as td2:
                curtime = time.time()
                File(join(td2, "testfile_b1")).touch('\n', mtime=curtime - 10)
                File(join(td2, "testfile_b2")).touch('\n', mtime=curtime - 9)
                File(join(td2, "testfile_b3")).touch('\n', mtime=curtime - 8)
                File(join(td2, "testfile_b4")).touch('\n', mtime=curtime - 7)
                File(join(td2, "testfile_b5")).touch('\n', mtime=curtime - 6)
                File(join(td2, "testfile_b6")).touch('\n', mtime=curtime - 5)
                File(join(td2, "testfile_b7")).touch('\n', mtime=curtime - 4)
                File(join(td2, "testfile_b8")).touch('\n', mtime=curtime - 3)
                File(join(td2, "testfile_b9")).touch('\n', mtime=curtime - 2)

            self.assertFalse("testfile_b1" in p.getvalue())
            self.assertTrue("testfile_b5" in p.getvalue())
            self.assertTrue("testfile_b9" in p.getvalue())
            self.assertEqual(len(p.getvalue().split('\n')), 7)    # 2 extra lines (header and newline)

        # multiple files in TempDir - show all
        with CaptureStdoutLog() as p:
            with TempDir(name=True, display=True) as td3:
                File(join(td3, "testfile_c1")).touch('\n')
                File(join(td3, "testfile_c2")).touch('\n')
                File(join(td3, "testfile_c3")).touch('\n')
                File(join(td3, "testfile_c4")).touch('\n')
                File(join(td3, "testfile_c5")).touch('\n')
                File(join(td3, "testfile_c6")).touch('\n')
                File(join(td3, "testfile_c7")).touch('\n')
                File(join(td3, "testfile_c8")).touch('\n')
                File(join(td3, "testfile_c9")).touch('\n')

            self.assertIn("testfile_c1", p.getvalue())
            self.assertIn("testfile_c5", p.getvalue())
            self.assertIn("testfile_c9", p.getvalue())
            self.assertEqual(len(p.getvalue().split('\n')), 12)    # 3 extra lines (header, total, newline)

    def test_write_gz_direct(self):
        with TempName(name=True) as tn:
            with open(tn, "w") as fh:
                fh.write('''line1
line2
line3
''')
            # Append mode - compressed
            with File(tn) as file:
                file.compress(File.gz)
                self.assertTrue(exists(tn + ".gz"), "gz file must exist")
            with File(tn, autofind=True, mode="a", return_fh=True) as fh:
                fh.write("line4\nline5\n")

            with File(tn, autofind=True) as file:
                file.compress(File.none)
            with File(tn) as file:
                self.assertEqual(file.read(), 'line1\nline2\nline3\nline4\nline5\n')

            # Write mode - new file
            os.unlink(tn)
            self.assertTrue(not exists(tn + ".gz"), "gz file must not exist")
            with File(tn + ".gz", mode="w", return_fh=True) as fh:
                fh.write("line4\nline5\n")
            self.assertTrue(exists(tn + ".gz"), "gz file must exist")

            # Exception when mode=w for compressed file
            # self.assertRaises(Exception, File(tn + ".gz").fh, mode="w")

            # Check the contents
            File(tn, autofind=True).compress(File.none)   # decompress it
            with File(tn) as file:
                self.assertEqual(file.read(), 'line4\nline5\n')

            # Append mode - normal file
            with File(tn, mode="a", return_fh=True) as fh:
                fh.write("line6\n")
            with File(tn) as file:
                self.assertEqual(file.read(), 'line4\nline5\nline6\n')

    def test_rewrite(self):
        text1 = 'line line line line'
        text2 = 'newline newline'
        with TempDir(name=True) as tdir:
            fn = join(tdir, 'aa')
            # new file
            File(fn).rewrite(text1, 'abc')
            with open(fn) as fh:
                self.assertEqual(fh.read(), text1)

            # replace
            File(fn).rewrite(text2, 'abc')
            with open(fn) as fh:
                self.assertEqual(fh.read(), text2)
            self.assertEqual(os.listdir(tdir), ['aa'])

            # replace keep old file name
            File(fn).rewrite(text1, 'abc', keep='orig')
            with open(fn) as fh:
                self.assertEqual(fh.read(), text1)
            with open(f'{fn}.orig') as fh:
                self.assertEqual(fh.read(), text2)
            self.assertEqual(set(os.listdir(tdir)), {'aa', 'aa.orig'})

            # another rewrite()
            text3 = 'newest line'
            File(fn).rewrite(text3, 'abc', keep='orig')
            with open(fn) as fh:
                self.assertEqual(fh.read(), text3)
            with open(f'{fn}.orig') as fh:
                self.assertEqual(fh.read(), text2)
            self.assertEqual(set(os.listdir(tdir)), {'aa', 'aa.orig'})

            # one more
            text4 = 'newest line2'
            self.assertEqual(File(fn).rewrite(text4, 'abc', keep='orig2'), True)
            with open(fn) as fh:
                self.assertEqual(fh.read(), text4)
            with open(f'{fn}.orig') as fh:
                self.assertEqual(fh.read(), text2)
            with open(f'{fn}.orig2') as fh:
                self.assertEqual(fh.read(), text3)
            self.assertEqual(set(os.listdir(tdir)), {'aa', 'aa.orig', 'aa.orig2'})

            # rewrite same file
            self.assertEqual(File(fn).rewrite(text4, 'abc'), False)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_is_win_crlf(self):
        # large file case
        self.assertEqual(File(f'{UT_DIR}/misc_files/EnvironmentFile.unix.txt').is_win_crlf(), False)
        self.assertEqual(File(f'{UT_DIR}/misc_files/EnvironmentFile.win.txt').is_win_crlf(), True)

        # small file case
        with TempDir(name=True) as tdir:
            newfile = f'{tdir}/a.txt'
            File(newfile).touch('a\r\nb\r\nc\r\n', newfile=True)
            self.assertEqual(File(newfile).is_win_crlf(), True)
            File(newfile).touch('a\nb\nc\n', newfile=True)
            self.assertEqual(File(newfile).is_win_crlf(), False)

        # non existent case
        self.assertEqual(File(f'{UT_DIR_REPO}/misc_files/_NOT_EXIST').is_win_crlf(), False)

    @unittest.skipIf(IS_WIN, 'unix coverage only')
    def test_crlf_coverage(self):
        # assume windows, read unix file
        with TempDir(name=True) as tdir:
            with MockVar(shell, 'IS_UNIX', False):
                utunix = f'{UT_DIR_REPO}/misc_files/EnvironmentFile.unix.txt'
                newfile = f'{tdir}/a.txt'
                File(utunix).copy(newfile)
                with open(newfile) as fh:
                    final = list(fh)
                File(newfile).rewrite(''.join(final), 'a', check=False)
                self.assertEqual(File(utunix).sha1(), File(newfile).sha1(), f'Failed for {utunix}')

    def test_rewrite_crlf(self):
        # Purpose: rewrite() must preserve eol line endings
        # This must pass in windows as well: python /i/tpvalidation/jqdelosr/pytpd/gadget/test/test_files.py -v FileFH_tests.test_rewrite_crlf
        def testme(ut):
            with TempDir(name=True) as tdir:
                with open(ut) as fh:
                    final = list(fh)
                newfile = f'{tdir}/a.txt'
                File(ut).copy(newfile)
                File(newfile).rewrite(''.join(final), 'a', check=False)
                self.assertEqual(File(ut).sha1(), File(newfile).sha1(), f'Failed for {ut}')

        # unix line endings
        testme(f'{UT_DIR_REPO}/misc_files/EnvironmentFile.unix.txt')
        # win line endings
        testme(f'{UT_DIR_REPO}/misc_files/EnvironmentFile.win.txt')

    @unittest.skipIf(IS_WIN, 'unix default to check crlf')
    def test_rewrite_crlf_new(self):
        # New file case - use unix line endings, with windows as input
        ut_unix = f'{UT_DIR_REPO}/misc_files/EnvironmentFile.unix.txt'
        ut_win = f'{UT_DIR_REPO}/misc_files/EnvironmentFile.win.txt'
        with TempDir(name=True) as tdir:
            with open(ut_win) as fh:
                final = list(fh)
            newfile = f'{tdir}/a.txt'
            File(newfile).rewrite(''.join(final), 'a', check=False)
            self.assertEqual(File(ut_unix).sha1(), File(newfile).sha1(), f"Sha did not match {ut_unix}")

    def test_write(self):
        text = 'line line line line'
        with TempDir(name=True) as tdir:
            # normal file
            fn = join(tdir, 'aa')
            obj = File(fn, mode='w').write(text)
            self.assertEqual(obj.read(), text)
            self.assertEqual(File(fn).read(), text)   # new object
            with open(fn, 'rb') as fh:
                self.assertEqual(fh.read(), text.encode())     # using native open

            # write again (should not append)
            obj.write(text)
            self.assertEqual(obj.read(), text)

            # write again (should append)
            obj = File(fn, mode='a').write('new')
            self.assertEqual(obj.read(), 'line line line linenew')

            # normal file, no mode
            fn = join(tdir, 'aa')
            obj = File(fn).write(text)
            self.assertEqual(obj.read(), text)
            with open(fn, 'rb') as fh:
                self.assertEqual(fh.read(), text.encode())     # using native open

            # gz file
            fn = join(tdir, 'aa.gz')
            obj = File(fn, mode='w').write(text)
            self.assertEqual(obj.read(), text)
            with open(fn, 'rb') as fh:
                self.assertNotEqual(fh.read(), text.encode())     # using native open

            # bz2 file
            fn = join(tdir, 'aa.bz2')
            obj = File(fn, mode='w').write(text)
            self.assertEqual(obj.read(), text)
            with open(fn, 'rb') as fh:
                self.assertNotEqual(fh.read(), text.encode())     # using native open

            # gz.bz2 file
            fn = join(tdir, 'aa.gz.bz2')
            obj = File(fn, mode='w').write(text)
            self.assertEqual(obj.read(), text)
            with open(fn, 'rb') as fh:
                self.assertNotEqual(fh.read(), text.encode())     # using native open

            # filehandle is used
            fn = join(tdir, 'aa.gz')
            obj = File(fn).write('sometext')
            _ = obj.fh(mode='w')
            obj.write(text)
            self.assertEqual(obj.read(), text)
            with open(fn, 'rb') as fh:
                self.assertNotEqual(fh.read(), text.encode())     # using native open

            # write binary is used
            fn = join(tdir, 'aa.gz')
            obj = File(fn).write(text.encode())
            self.assertEqual(obj.read(), text)
            with open(fn, 'rb') as fh:
                self.assertNotEqual(fh.read(), text.encode())     # using native open

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_gz_brokenpipe(self):     # this test will termine the pipe early
        # Below test will show "broken pipe" if os.popen() is used
        with open(self.tmp, "w") as fh:
            for i in range(10000):
                fh.write("%d This is a line\n" % i)
        os.system("gzip " + self.tmp)
        with File(self.tmp + ".gz", return_fh=True) as f:
            for lno, line in enumerate(f):
                if lno == 2:
                    break
        self.assertEqual(lno, 2)
        self.assertEqual(line, '2 This is a line\n')

        # Large file test
        total = 0
        with File(self.tmp + ".gz", return_fh=True) as f:
            for lno, line in enumerate(f, 1):
                total += len(line)
        self.assertEqual(lno, 10000)   # popen
        self.assertEqual(line, '9999 This is a line\n')   # popen
        self.assertEqual(total, 198890)   # popen, this is the total bytes, >69KB pipe buffer

        # Large file test - small
        total = 0
        with File(self.tmp + ".gz", return_fh=True).fh() as f:
            for lno, line in enumerate(f, 1):
                total += len(line)
        self.assertEqual(lno, 10000)   # builtin
        self.assertEqual(to_str(line), '9999 This is a line\n')   # builtin is bytes
        self.assertEqual(total, 198890)   # builtin, this is the total bytes, >69KB pipe buffer

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_gz(self):
        os.system("gzip " + self.tmp)
        with File(self.tmp + ".gz", return_fh=True) as f:
            res = f.read()
        self.assertEqual(res, self.msg)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_bz2(self):
        os.system("bzip2 " + self.tmp)

        with File(self.tmp + ".bz2", return_fh=True) as f:
            res = f.read()
        self.assertEqual(to_str(res), self.msg)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_gzbz2(self):
        os.system("gzip " + self.tmp)
        os.system("bzip2 " + self.tmp + ".gz")

        with File(self.tmp + ".gz.bz2", return_fh=True) as f:
            res = f.read()
        self.assertEqual(to_str(res), self.msg)

    def test_read(self):
        with TempDir(name=True, chdir=True) as tdir:
            txt = "This is my text. This is my text"
            aa = File("abc").touch(txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)

            aa.compress(File.gz)
            self.assertEqual(aa.get_name(check_exist=True), "abc.gz")
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)

            aa.compress(File.bz2)
            self.assertEqual(aa.get_name(check_exist=True), "abc.bz2")
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)

            aa.compress(File.gzbz2)
            self.assertEqual(aa.get_name(check_exist=True), "abc.gz.bz2")
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)
            self.assertEqual(aa.read(), txt)

    @unittest.skip("not implemented")
    def test_stdin(self):
        # Create an executable that reads stdin
        code = '''#!%(exec)s
import sys
sys.path.insert(0,"%(cwd)s/..")
from %(mod)s import *
with zopen('stdin') as fh:
   for line in fh:
      print "new:"+line.strip()
''' % {'mod': _pyname(),
            'exec': sys.executable,
            'cwd': realpath(dirname(sys.argv[0]))}
        print(code)

        # Create the file
        with open(self.tmp, "w") as fh:
            fh.write(code)
        os.chmod(self.tmp, 0o750)

        # Setup the stdin to stdout
        pr1 = subprocess.Popen(('echo', 'abcdef'), stdout=subprocess.PIPE, stderr=open("/dev/null", "w"))
        pr2 = subprocess.Popen(self.tmp, stdin=pr1.stdout, stdout=subprocess.PIPE, stderr=open("/dev/null", "w"))
        self.assertEqual(pr2.stdout.read(), "new:abcdef\n")

    def test_id_problem_unicode(self):
        # Success case
        File(f'{UT_DIR_REPO}/misc_files/EnvironmentFile.win.txt').id_problem_unicode()

        # Fail case
        with self.assertRaisesRegex(ErrorUser, 'has unknown characters'):
            File(f'{UT_DIR_REPO}/misc_files/unicode_error.mtpl').id_problem_unicode()

        self.assertTrue(File(f'{UT_DIR_REPO}/misc_files/unicode_error.mtpl').is_text())

        # no fail - make sure that print is success
        res = File(f'{UT_DIR_REPO}/misc_files/unicode_error.mtpl').read()
        print("Start case1=====")
        for line in res.split('\n'):
            print(line)

        res = File(f'{UT_DIR_REPO}/misc_files/unicode_error.mtpl').raw()
        print("Start case2=====")
        for line in res:
            print(line)

    @unittest.skipIf(IS_WIN, 'unix file raw check')
    def test_raw(self):
        # make sure no line endings is lost
        orig_obj = File(f'{UT_DIR_REPO}/misc_files/EnvironmentFile.unix.txt')
        alltext = ''.join(orig_obj.raw())
        self.assertEqual(sha1(alltext), orig_obj.sha1())

        alltext2 = orig_obj.read()
        self.assertEqual(sha1(alltext2), orig_obj.sha1())

        alltext = orig_obj.raw(islist=False)
        self.assertEqual(sha1(alltext), orig_obj.sha1())

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_universal_newlines(self):
        # These tests make sures universal_newlines have no effect on different types of files for .gz.bz2
        with TempDir(name=True) as tdir:
            f1_unix = File('/p/pde/tvpv/pylib3a/test_files/unix.txt')
            f2_ucod = File('/p/pde/tvpv/pylib3a/test_files/unicode.html')
            f3_wind = File('/p/pde/tvpv/pylib3a/test_files/dos.txt')
            f4_bina = File('/p/pde/tvpv/pylib3a/test_files/binary.so')

            # copy to tempdir
            f1_unix.copy(tdir).compress(File.gzbz2)
            f2_ucod.copy(tdir).compress(File.gzbz2)
            f3_wind.copy(tdir).compress(File.gzbz2)
            f4_bina.copy(tdir).compress(File.gzbz2)

            # normal unix file - text
            res_f1_fh = f1_unix.fh()
            res_f1 = res_f1_fh.read()
            self.assertEqual(len(res_f1.split('\n')), 28)
            self.assertEqual(sha1(res_f1), '3b31471cc1bfaf2dd2f3cc7ef7a45ddec6c7e3fa')
            f1_unix.close()
            # non-bytes
            res_f1a = f1_unix.read()
            self.assertEqual(len(res_f1a.split('\n')), 28)
            self.assertEqual(sha1(res_f1a), '3b31471cc1bfaf2dd2f3cc7ef7a45ddec6c7e3fa')
            f1_unix.close()

            # windows file
            res_f3_fh = f3_wind.fh()
            res_f3 = res_f3_fh.read()
            self.assertEqual(len(res_f3.split('\n')), 28)
            self.assertEqual(res_f1, res_f3.replace('\r', ''))
            f3_wind.close()
            # non-bytes
            res_f3a = f3_wind.read()
            self.assertEqual(len(res_f3a.split('\n')), 28)
            self.assertEqual(res_f1a, res_f3a.replace('\r', ''))
            f3_wind.close()

            # binary
            res_f4_fh = f4_bina.fh(is_text=False)
            res_f4 = res_f4_fh.read()
            self.assertEqual(sha1(res_f4), '6d2af4489e705287a3a15d18513be921bafa2a64')
            f4_bina.close()

            # unicode file
            res_f2_fh = f2_ucod.fh()
            res_f2 = res_f2_fh.read()
            self.assertEqual(len(res_f2.split('\n')), 335)
            f2_ucod.close()
            # non-bytes
            res_f2a = f2_ucod.read()
            self.assertEqual(len(res_f2a.split('\n')), 335)
            f2_ucod.close()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_binary(self):
        f1_unix = File('/p/pde/tvpv/pylib3a/test_files/unix.txt')
        f4_bina = File('/p/pde/tvpv/pylib3a/test_files/binary.so')
        self.assertTrue(isinstance(f1_unix.read(is_text=False), bytes))
        self.assertTrue(isinstance(f4_bina.read(is_text=False), bytes))
        self.assertEqual(sha1(f4_bina.read(is_text=False)), '6d2af4489e705287a3a15d18513be921bafa2a64')
        self.assertEqual(f4_bina.sha1(), '6d2af4489e705287a3a15d18513be921bafa2a64')
        f1_unix.close()
        f4_bina.close()

    def test_type(self):
        txt = '\n'.join('The quick brown fox' for _ in range(100))

        with TempDir(name=True, chdir=True) as tdir:
            ff = File('aa').touch(txt)
            res = ff.fh(is_text=False).read()
            self.assertTrue(isinstance(res, bytes))  # File.none
            res = ff.fh().read()
            self.assertTrue(isinstance(res, str))    # File.none

            ff.compress(File.gz)
            res = ff.fh(is_text=False).read()
            self.assertTrue(isinstance(res, bytes))  # File.gz
            res = ff.fh().read()
            self.assertTrue(isinstance(res, str))    # File.gz

            ff.compress(File.gzbz2)
            res = ff.fh(is_text=False).read()
            self.assertTrue(isinstance(res, bytes))  # File.gz.bz2
            res = ff.fh().read()
            self.assertTrue(isinstance(res, str))    # File.gz.bz2

            ff.compress(File.bz2)
            res = ff.fh(is_text=False).read()
            self.assertTrue(isinstance(res, bytes))  # File.bz2
            res = ff.fh().read()
            self.assertTrue(isinstance(res, str))    # File.bz2


class FileCompress_tests(TestCase):

    def test_compress(self):
        from io import IOBase
        filetype = IOBase
        txt = "The quick The The\nTheThe"
        with TempDir(chdir=True, name=True) as tdir:
            # compress only
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            aa.compress(File.gz)
            self.assertEqual(os.listdir(tdir), ['aa.gz'])    # must contain one file only
            self.assertEqual(basename(aa.get_name(True)), "aa.gz")
            self.assertTrue(isinstance(aa.fh(), filetype))

            # recompress
            aa.compress(File.gzbz2)
            self.assertEqual(os.listdir(tdir), ['aa.gz.bz2'])    # must contain one file only
            self.assertEqual(basename(aa.get_name(True)), "aa.gz.bz2")
            self.assertTrue(isinstance(aa.fh(), filetype))

            # no change
            aa.compress(File.gzbz2)
            self.assertEqual(os.listdir(tdir), ['aa.gz.bz2'])    # must contain one file only
            self.assertEqual(basename(aa.get_name(True)), "aa.gz.bz2")

            # decompress only
            aa.compress(File.none)
            self.assertEqual(os.listdir(tdir), ['aa'])    # must contain one file only
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)
            self.assertEqual(basename(aa.get_name(True)), "aa")

            # no change
            aa.compress(File.none)
            self.assertEqual(os.listdir(tdir), ['aa'])    # must contain one file only
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)
            self.assertEqual(basename(aa.get_name(True)), "aa")
            self.assertTrue(isinstance(aa.fh(), filetype))

            # Invalid compression type
            self.assertRaisesRegex(Exception, "Input compressiontype", aa.compress, ".tar")

            # recompress
            aa.compress(File.bz2)
            self.assertEqual(os.listdir(tdir), ['aa.bz2'])    # must contain one file only
            self.assertEqual(basename(aa.get_name(True)), "aa.bz2")
            self.assertTrue(isinstance(aa.fh(), filetype))

            aa.close()

    @unittest.skipIf(IS_WIN, 'unix only due chmod')
    def test_compressfail(self):
        txt = "The quick The The\nTheThe"
        with TempDir(chdir=True) as t:
            mkdirs("rodir")
            try:
                # compress
                aa = File(join("rodir", "aa")).touch(txt)
                File("rodir").chmod("0555")
                self.assertRaises(Exception, aa.compress, File.gz)
                self.assertRaises(Exception, aa.compress, File.gzbz2)
                self.assertRaises(Exception, aa.compress, File.bz2)
            finally:
                File("rodir").chmod("0775")

    @unittest.skipIf(IS_WIN, 'unix only due to softlink')
    def test_link_dir(self):
        with TempDir(name=True) as tdir:
            # cannot compress a directory
            with self.assertRaisesRegex(Exception, 'Only files can be compressed'):
                File(tdir).compress(File.gz)

            # cannot compress a softlink
            File(join(tdir, 'src')).touch("abcd")
            os.symlink(join(tdir, 'src'), join(tdir, 'lnk'))
            with self.assertRaisesRegex(Exception, 'Cannot compress/uncompress a softlink'):
                File(join(tdir, 'lnk')).compress(File.gz)

    def test_compress_root(self):
        txt = "The quick The The\nTheThe"
        aa = File("aa")
        compress = aa._compress
        uncompress = aa._uncompress
        with TempDir(chdir=True) as t:
            # gz
            with open("aa", "w") as fh:
                fh.write(txt)
            compress("aa", ".gz")
            self.assertTrue(exists("aa.gz"), "aa.gz must exist")
            uncompress("aa.gz")
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

            # bz2
            with open("aa", "w") as fh:
                fh.write(txt)
            compress("aa", ".bz2")
            self.assertTrue(exists("aa.bz2"), "aa.bz2 must exist")
            uncompress("aa.bz2")
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

            # .gz.bz2
            with open("aa", "w") as fh:
                fh.write(txt)
            compress("aa", ".gz.bz2")
            self.assertTrue(exists("aa.gz.bz2"), "aa.gz.bz2 must exist")
            uncompress("aa.gz.bz2")
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

            # bz2.gz
            # with open("aa", "w") as fh:
            #     fh.write(txt)
            # compress("aa", ".bz2.gz")
            # self.assertTrue(exists("aa.bz2.gz"), "aa.bz2.gz must exist")
            # uncompress("aa.bz2.gz")
            # with open("aa") as fh:
            #     self.assertEqual(fh.read(), txt)

            # unknown type
            with open("aa", "w") as fh:
                fh.write(txt)
            self.assertRaisesRegex(Exception, "Unknown compression type", compress, "aa", ".gdz")

            # directory
            os.mkdir("ab")
            ab = File("ab")
            self.assertRaises(Exception, ab._compress, "ab", ".gz")   # unix vs windows have different error

    def test_overwrite(self):
        # uncompress gz
        with TempDir(chdir=True), \
                File("abc.gz") as aa, \
                File("abc") as abc:
            aa.touch("abcdefg")
            abc.touch("aaa")
            aa.compress(File.none)
            self.assertEqual(aa.read(), "abcdefg")

        # uncompress bz2
        with TempDir(chdir=True), \
                File("abc") as abc:
            aa = File("abc.bz2")
            aa.touch("abcdefg")
            abc.touch("aaa")
            aa.compress(File.none)
            self.assertEqual(aa.read(), "abcdefg")
            aa.close()

        # compress gz
        with TempDir(chdir=True), \
                File("abc.gz") as abc, \
                File("abc") as bb:
            abc.touch("aaa")
            bb.touch("abcdefg")
            bb.compress(File.gz)
            self.assertEqual(bb.read(), "abcdefg")

        # compress bz2
        with TempDir(chdir=True), \
                File("abc.bz2") as aa, \
                File("abc") as bb:
            aa.touch("aaa")
            bb.touch("abcdefg")
            bb.compress(File.bz2)
            self.assertEqual(bb.read(), "abcdefg")

        # compress gzbz2
        with TempDir(chdir=True), \
                File("abc.gz.bz2") as abc_bz, \
                File("abc.gz") as abc_gz, \
                File("abc") as bb:
            abc_bz.touch("aaa")
            abc_gz.touch("aaa")
            bb.touch("abcdefg")
            bb.compress(File.gzbz2)
            self.assertEqual(bb.read(), "abcdefg")

    @unittest.skipIf(IS_WIN, 'unix only due system call')
    def test_uncompress_root(self):
        txt = "The quick The The\nTheThe"
        aa = File("aa")
        with TempDir(chdir=True) as t:
            # gz
            with open("aa", "w") as fh:
                fh.write(txt)
            SystemCall("gzip aa").run()
            self.assertTrue(exists("aa.gz"), "aa.gz must exist")
            aa._uncompress("aa.gz")
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

            # bz2
            with open("aa", "w") as fh:
                fh.write(txt)
            SystemCall("bzip2 aa").run()
            self.assertTrue(exists("aa.bz2"), "aa.bz2 must exist")
            aa._uncompress("aa.bz2")
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

            # .gz.bz2
            with open("aa", "w") as fh:
                fh.write(txt)
            SystemCall("gzip aa").run()
            SystemCall("bzip2 aa.gz").run()
            self.assertTrue(exists("aa.gz.bz2"), "aa.gz.bz2 must exist")
            aa._uncompress("aa.gz.bz2")
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

            # not compressed file
            aa._uncompress("aa")
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

            # corrupted case - gzip
            with open("aa", "w") as fh:
                fh.write(txt)
            os.rename("aa", "aa.gz")
            self.assertRaisesRegex(Exception, "Not a gzipped", aa._uncompress, "aa.gz")

            # corrupted case - bunzip
            with open("aa", "w") as fh:
                fh.write(txt)
            os.rename("aa", "aa.bz2")
            self.assertRaisesRegex(Exception, "data stream", aa._uncompress, "aa.bz2")

    def test_allcombination(self):
        txt = "The quick The The\nTheThe"

        with TempDir(name=True, chdir=True) as tdir:
            aa = File("aa")
            aa.touch(txt, newfile=True)

            # gz ===================
            def check_gz():
                aa.compress(File.gz)
                self.assertEqual(os.listdir('.'), ['aa.gz'])
                self.assertEqual(File('aa.gz').read(), txt)
                self.assertEqual(aa.compression, File.gz)

            # 1. from none
            self.assertEqual(os.listdir('.'), ['aa'])
            check_gz()

            # 2. from gz
            self.assertEqual(os.listdir('.'), ['aa.gz'])
            check_gz()

            # 3. from bz2
            aa.compress(File.bz2)
            self.assertEqual(os.listdir('.'), ['aa.bz2'])
            check_gz()

            # 4. from gzbz2
            aa.compress(File.gzbz2)
            self.assertEqual(os.listdir('.'), ['aa.gz.bz2'])
            check_gz()

            # bz2 ===================
            def check_bz2():
                aa.compress(File.bz2)
                self.assertEqual(os.listdir('.'), ['aa.bz2'])
                self.assertEqual(File('aa.bz2').read(), txt)
                self.assertEqual(aa.compression, File.bz2)

            # 1. from none
            aa.compress(File.none)
            self.assertEqual(os.listdir('.'), ['aa'])
            check_bz2()

            # 2. from gz
            aa.compress(File.gz)
            self.assertEqual(os.listdir('.'), ['aa.gz'])
            check_bz2()

            # 3. from bz2
            aa.compress(File.bz2)
            self.assertEqual(os.listdir('.'), ['aa.bz2'])
            check_bz2()

            # 4. from gzbz2
            aa.compress(File.gzbz2)
            self.assertEqual(os.listdir('.'), ['aa.gz.bz2'])
            check_bz2()

            # gzbz2 ===================
            def check_gzbz2():
                aa.compress(File.gzbz2)
                self.assertEqual(os.listdir('.'), ['aa.gz.bz2'])
                self.assertEqual(File('aa.gz.bz2').read(), txt)
                self.assertEqual(aa.compression, File.gzbz2)

            # 1. from none
            aa.compress(File.none)
            self.assertEqual(os.listdir('.'), ['aa'])
            check_gzbz2()

            # 2. from gz
            aa.compress(File.gz)
            self.assertEqual(os.listdir('.'), ['aa.gz'])
            check_gzbz2()

            # 3. from bz2
            aa.compress(File.bz2)
            self.assertEqual(os.listdir('.'), ['aa.bz2'])
            check_gzbz2()

            # 4. from gzbz2
            aa.compress(File.gzbz2)
            self.assertEqual(os.listdir('.'), ['aa.gz.bz2'])
            check_gzbz2()

            # no compression ===================
            def check_none():
                aa.uncompress()
                self.assertEqual(os.listdir('.'), ['aa'])
                self.assertEqual(File('aa').read(), txt)
                self.assertEqual(aa.compression, File.none)

            # 1. from none
            aa.compress(File.none)
            self.assertEqual(os.listdir('.'), ['aa'])
            check_none()

            # 2. from gz
            aa.compress(File.gz)
            self.assertEqual(os.listdir('.'), ['aa.gz'])
            check_none()

            # 3. from bz2
            aa.compress(File.bz2)
            self.assertEqual(os.listdir('.'), ['aa.bz2'])
            check_none()

            # 4. from gzbz2
            aa.compress(File.gzbz2)
            self.assertEqual(os.listdir('.'), ['aa.gz.bz2'])
            check_none()

    def test_bz2gz(self):
        # Check bz2gz is unsupported
        with TempDir(name=True, chdir=True) as tdir:
            with open('aa.bz2.gz', 'wb') as fh:
                pass

            obj = File('aa.bz2.gz')

            # get filehandle
            with self.assertRaisesRegex(Exception, 'is unsupported'):
                obj.fh()

            # uncompress
            with self.assertRaisesRegex(Exception, 'is unsupported'):
                obj.compress(File.none)

            # compress
            with self.assertRaisesRegex(Exception, 'is unsupported'):
                File('bb').touch().compress(File.bz2gz)

    def test_structure(self):
        # This test confirms that the actual file is compressed in the right format
        txt = '\n'.join('The quick brown fox' for _ in range(1000))

        with TempDir(name=True, chdir=True) as tdir:
            with open('aa', 'w', newline='') as fh:
                fh.write(txt)

            ff = File('aa')
            sha_ref = sha1(txt)
            self.assertGreater(os.path.getsize(ff.get_name()), 19000)

            # raw content
            sha_none = ff.sha1()
            ff.compress(File.gz)
            sha_gz = ff.sha1()
            size_gz = os.path.getsize(ff.get_name())
            self.assertLess(size_gz, 1000)

            ff.compress(File.gzbz2)
            sha_gzbz2 = ff.sha1()
            size_gzbz2 = os.path.getsize(ff.get_name())
            self.assertLess(size_gzbz2, 1000)

            ff.compress(File.bz2)
            sha_bz2 = ff.sha1()
            size_bz2 = os.path.getsize(ff.get_name())
            self.assertLess(size_bz2, 1000)
            self.assertLess(size_bz2, size_gz)

            all_sha = {sha_ref, sha_none, sha_gz, sha_gzbz2, sha_bz2}
            self.assertEqual(len(all_sha), 4)

            # actual content
            ff.compress(File.none)
            sha_none = ff.sha1(binary=False)
            ff.compress(File.gz)
            sha_gz = ff.sha1(binary=False)
            ff.compress(File.gzbz2)
            sha_gzbz2 = ff.sha1(binary=False)
            ff.compress(File.bz2)
            sha_bz2 = ff.sha1(binary=False)
            all_sha = {sha_ref, sha_none, sha_gz, sha_gzbz2, sha_bz2}
            self.assertEqual(len(all_sha), 1)


class FileChomp_tests(TestCase):

    def test_chomp_encoding(self):
        # checks encoding and iterator of all types
        with TempDir(name=True) as tdir:
            ff = File(f'{tdir}/aa').touch('1\n 2\n# 3\n')
            expect1 = ['1', ' 2', '# 3']
            expect2 = ['1', '2', '# 3']
            expect3 = ['1', '2']

            # gz
            self.assertEqual(os.listdir(tdir), ['aa'])
            ff.compress(File.gz)
            self.assertEqual(os.listdir(tdir), ['aa.gz'])
            self.assertEqual(list(ff.chomp()), expect1)
            self.assertEqual(list(ff.chomp(strip=True)), expect2)
            self.assertEqual(list(ff.chomp(comment='#')), expect3)
            ff.compress(File.none)

            # bz2
            self.assertEqual(os.listdir(tdir), ['aa'])
            ff.compress(File.bz2)
            self.assertEqual(os.listdir(tdir), ['aa.bz2'])
            self.assertEqual(list(ff.chomp()), expect1)
            self.assertEqual(list(ff.chomp(strip=True)), expect2)
            self.assertEqual(list(ff.chomp(comment='#')), expect3)
            ff.compress(File.none)

            # gzbz2
            self.assertEqual(os.listdir(tdir), ['aa'])
            ff.compress(File.gzbz2)
            self.assertEqual(os.listdir(tdir), ['aa.gz.bz2'])
            self.assertEqual(list(ff.chomp()), expect1)
            self.assertEqual(list(ff.chomp(strip=True)), expect2)
            self.assertEqual(list(ff.chomp(comment='#')), expect3)
            ff.compress(File.none)

    def test_chomp_basic(self):
        f = StringIO.StringIO()
        f.write("line#1\n\n")
        f.write("line#3\r\n")
        f.write("line#4")
        f.seek(0)
        res = '!'.join(File().chomp(f))
        self.assertEqual(res, "line#1!!line#3!line#4")

        arr = ['line1\n\n\n', 'line2\r\r\n', 'line3', None]
        res = '!'.join(File().chomp(arr))
        self.assertEqual(res, "line1!line2!line3")  # 1

        arr = ['    line1\n\n\n', '  \t\tline2\r\r\n', 'line3', None]
        res = '!'.join(File().chomp(arr, strip=True))
        self.assertEqual(res, "line1!line2!line3")  # 2

        arr = ['    line1\n\n\n', '  \t\tline2\r\r\n', 'line3']
        res = '!'.join(File().chomp(arr, strip=True))
        self.assertEqual(res, "line1!line2!line3")  # 3

    def test_chomp_emptyfile(self):
        with TempName(name=True) as tn:
            File(tn).touch()
            self.assertTrue(exists(tn), "file must exist")
            res = '!'.join(File(tn).chomp())
            self.assertEqual(res, '')    # should be empty

            with open(tn, "w") as fh:
                fh.write('hi')    # one line, no new line
            res = '!'.join(File(tn).chomp())
            self.assertEqual(res, 'hi')

    def test_chomp_consecutive(self):
        with TempName(name=True) as tn:
            text = "This\r\nis \nmulti-line\n"
            aa = File(tn).touch(text)
            # Windows add a blank line when writing
            aa_list = [_aa for _aa in list(aa.chomp()) if _aa]
            self.assertEqual(aa_list, ['This', 'is', 'multi-line'])  # 1st run
            aa_list = [_aa for _aa in list(aa.chomp()) if _aa]
            self.assertEqual(aa_list, ['This', 'is', 'multi-line'])  # 2nd run

    def test_chomp_comment(self):
        arr = ['   \n',
               '  Hello  \n',
               '  #No comment \n',
               '',
               '    \n',
               '  lastline\n']
        self.assertEqual(list(File().chomp(arr, comment="#")), ['Hello', 'lastline'])
        self.assertEqual(list(File().chomp(arr, comment="")), ['Hello', '#No comment', 'lastline'])

        # with attribute error
        arr = ['# comment  \n',
               '  '
               '  Hello  \n',
               None]
        self.assertEqual(list(File().chomp(arr, comment="#")), ['Hello'])


class FileTouch_tests(TestCase):
    @unittest.skipIf(*is_ut_option('SLOW', message="Slowtest bec of sleep"))   # change message to right one
    def test_timecheck(self):
        with TempName(name=True) as tmp:
            File(tmp).touch()
            otime = os.path.getmtime(tmp)
            time.sleep(3)
            File(tmp).touch()
            self.assertNotEqual(otime, os.path.getmtime(tmp))

        with TempName(name=True) as tmp:
            ext = ".gz"
            obj = File(tmp + ext).touch()
            otime = os.path.getmtime(tmp + ext)
            time.sleep(3)
            obj.touch()
            self.assertNotEqual(otime, os.path.getmtime(tmp + ext))
            obj.compress(obj.none)

        with TempName(name=True) as tmp:
            ext = ".gz.bz2"
            obj = File(tmp + ext).touch()
            otime = os.path.getmtime(tmp + ext)
            time.sleep(3)
            obj.touch()
            self.assertNotEqual(otime, os.path.getmtime(tmp + ext))
            obj.compress(obj.none)

    @unittest.skipIf(IS_WIN, 'unix only support digital file permissions')
    def test_failtouch(self):
        # Directory is not writable
        with TempDir(name=True) as tdir:
            File(tdir).chmod("0555")
            with self.assertRaises(IOError):
                File(join(tdir, "newfile")).touch()

        # Directory does not exist
        with self.assertRaises(IOError):
            File(join(tmpdir(), "surenotexist_1_55", "newfile")).touch()

    def test_new_file_created(self):
        with TempName(name=True) as tmp:
            self.assertEqual(File(tmp).touch().get_name(), tmp)
            self.assertTrue(exists(tmp))

        # append
        with TempName(name=True) as tmp:
            self.assertEqual(File(tmp).touch("abc").get_name(), tmp)
            self.assertTrue(exists(tmp))
            with open(tmp) as fh:
                self.assertEqual(fh.read(), "abc")

    def test_old_file_unchanged(self):
        with TempName(name=True) as tmp1:
            with open(tmp1, "w") as fh:
                fh.write("hello")
            File(tmp1).touch()
            with open(tmp1) as fh:
                self.assertEqual(fh.read(), "hello")

        # append
        with TempName(name=True) as tmp1:
            with open(tmp1, "w") as fh:
                fh.write("hello")
            File(tmp1).touch("there")
            with open(tmp1) as fh:
                self.assertEqual(fh.read(), "hellothere")

    def test_compressed_touch(self):
        with TempName(name=True) as tn:
            obj = File(tn + ".gz").touch()
            self.assertGreater(os.path.getsize(tn + ".gz"), 10)
            obj.compress(obj.none)

        with TempName(name=True) as tn:
            obj = File(tn + ".gz.bz2").touch()
            self.assertGreater(os.path.getsize(tn + ".gz.bz2"), 10)
            obj.compress(obj.none)

        # append
        with TempName(name=True) as tn:
            obj = File(tn + ".gz").touch("abc")
            with File(tn + ".gz") as file:
                self.assertEqual(file.read(), "abc")
            obj.compress(obj.none)

        with TempName(name=True) as tn:
            obj = File(tn + ".gz.bz2").touch("abc")
            with File(tn + ".gz.bz2") as file:
                self.assertEqual(file.read(), "abc")
            obj.compress(obj.none)

        # append2
        with TempName(name=True) as tn:
            obj = File(tn + ".gz").touch("abc")
            obj.touch("def")
            obj.touch()
            with File(tn + ".gz") as file:
                self.assertEqual(file.read(), "abcdef")
            obj.compress(obj.none)

        with TempName(name=True) as tn:
            obj = File(tn + ".gz.bz2").touch("abc")
            obj.touch("def")
            obj.touch()
            with File(tn + ".gz.bz2") as file:
                self.assertEqual(file.read(), "abcdef")
            obj.compress(obj.none)

    def test_touchmkdir(self):
        with TempDir(name=True) as tdir:
            # already exist
            File(join(tdir, "abc")).touch(mkdir=True)
            self.assertTrue(exists(join(tdir, "abc")))

            # create dir
            ff = join(tdir, "a", "b", "c", "d", "abc")
            File(ff).touch(mkdir=True)
            self.assertTrue(exists(ff))

            # exception: dir does not exist
            ff = join(tdir, "a", "b", "c", "e", "abc")
            self.assertRaises(IOError, File(ff).touch)

    def test_touch_append(self):
        # NOTE: Do not change this unittest! Changing behavior of touch() would cause several vep2 algo
        # to fail since touch() is meant to append
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'f1')).touch('abc')
            f1.touch('123')
            self.assertEqual(f1.read(), 'abc123')     # DO NOT CHANGE THIS unittest! See docstring above as to why.

            f1.compress(f1.gz)
            f1.touch('789')
            self.assertEqual(f1.read(), 'abc123789')  # DO NOT CHANGE THIS unittest! See docstring above as to why.

    def test_touch_mode(self):
        with TempDir(name=True) as tdir:
            File(f'{tdir}/abc').touch(mode='400')
            with self.assertRaisesRegex(PermissionError, 'Permission denied'):
                File(f'{tdir}/abc').touch('again')      # this should fail because the file is read only

            File(f'{tdir}/def').touch()
            with MockVar(File, 'chgrp', Mock(side_effect=PermissionError)):
                File(f'{tdir}/def').touch()   # should still pass

    def test_touch(self):
        with TempDir(name=True) as tdir:
            # normal case
            f1 = File(join(tdir, 'f1')).touch('abc')
            self.assertLess(f1.age(), 60)

            # mtime change
            f1 = File(join(tdir, 'f1')).touch('abc', mtime=time.time() - 500)
            self.assertGreater(f1.age(), 400)

            # no append
            self.assertEqual(f1.read(), 'abcabc')
            f1 = File(join(tdir, 'f1')).touch('abc', newfile=True)
            self.assertEqual(f1.read(), 'abc')

            # gzip - no append
            f1.compress(f1.gz)
            f1.touch('abcd', newfile=True)
            self.assertEqual(f1.read(), 'abcd')
            self.assertEqual(f1.get_name(basename=True), 'f1.gz')


class FileCpMvRm_tests(TestCase):

    def test_copyfile(self):
        with TempDir(name=True, chdir=True) as tdir:
            # pass case
            txt = "The quick The The\nTheThe"
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa").copy("bb")
            self.assertEqual(basename(aa.get_name()), "bb")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertTrue(aa.opsuccess, "operation successful")

            # copy to same file
            oname2 = aa.get_name()
            aa.copy("bb")
            self.assertEqual(basename(aa.get_name()), "bb")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertEqual(oname2, aa.get_name())
            self.assertFalse(aa.opsuccess, "copy should be skipped")

            # copy overwrite
            with open("cc", "w") as fh:
                fh.write(txt + txt)
            aa.copy("cc")
            self.assertEqual(basename(aa.get_name()), "cc")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            with open("cc") as fh:
                self.assertEqual(fh.read(), txt)

            # no xfer
            aa = File("aa").copy("cc", xfer=False)
            self.assertEqual(basename(aa.get_name()), "aa")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)

            # pass case - same physical dir, different name, same basename
            aa = File("aa")
            aa.copy(join(tdir, "aa"))
            self.assertFalse(aa.opsuccess, "copy should be skipped")

            # error case - different compression
            self.assertRaisesRegex(Exception, "not match compression", aa.copy, "aa.gz")

    def test_copyfile2(self):
        # This tests copy to a different directory
        with TempDir(name=True, chdir=True) as tdir:
            os.mkdir("nd")
            # pass case - xfer True
            txt = "The quick The The\nTheThe"
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa").copy("nd/bb")
            self.assertEqual(aa.get_name(), os.path.normpath("nd/bb"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)
            self.assertTrue(aa.opsuccess, "operation successful")

            # pass case - xfer False
            txt = "The quick The The\nTheThe"
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa").copy("nd/cc", xfer=False)
            self.assertEqual(aa.get_name(), "aa")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            with open("nd/cc") as fh:
                self.assertEqual(fh.read(), txt)
            self.assertTrue(aa.opsuccess, "operation successful")

            # fail case - no such base dir
            self.assertRaisesRegex(Exception, "not exist", aa.copy, "nd/nodir/cc")

            # pass case - same dir, different name
            txt = "The quick The The\nTheThe"
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa").copy(join(tdir, "dd"))
            self.assertEqual(aa.get_name(), join(tdir, "dd"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)
            self.assertTrue(aa.opsuccess, "operation successful")

            # pass case with compression
            aa = File("aa").compress(File.gz).copy("nd/ee.gz")
            self.assertEqual(aa.get_name(), os.path.normpath("nd/ee.gz"))
            with File(aa.get_name()) as file:
                self.assertEqual(file.read(), txt)
            with File("aa.gz") as file:
                self.assertEqual(file.read(), txt)
            self.assertTrue(aa.opsuccess, "operation successful")

            # bug relative dir and same dir
            a1 = File("nd/a1").touch('a1x')
            a1.copy("nd/a2")
            with open("nd/a2") as fh:
                self.assertEqual(fh.read(), 'a1x')

    def test_copytodir(self):
        txt = "The quick The The\nTheThe"
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            # pass case
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            oname = aa.get_name()
            aa.copy(tdir2)
            self.assertEqual(aa.get_name(), join(tdir2, "aa"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertNotEqual(oname, aa.get_name())
            self.assertTrue(exists(oname), "orig file must exist")
            self.assertTrue(aa.opsuccess, "operation successful")

            # copy overwrite
            with open("aa", "w") as fh:
                fh.write(txt + txt)
            aa.copy(tdir)
            self.assertEqual(aa.get_name(), join(tdir, "aa"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            with open("aa") as fh:
                self.assertEqual(fh.read(), txt)

        # no xfer
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            oname = aa.get_name()
            aa.copy(tdir2, xfer=False)
            self.assertEqual(realpath(aa.get_name()), join(tdir, "aa"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertEqual(oname, aa.get_name())

        # copy to same dir
        with TempDir(name=True, chdir=True) as tdir:
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            aa.copy(tdir)
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertTrue(not aa.opsuccess, "copy should be skipped")

    def test_move(self):
        txt = "The quick The The\nTheThe"
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            # pass case
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            oname = aa.get_name()
            aa.move(tdir2)
            self.assertEqual(aa.get_name(), join(tdir2, "aa"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertNotEqual(aa.get_name(), oname)
            self.assertTrue(not exists(oname), "orig file must not exist")
            self.assertTrue(aa.opsuccess, "operation successful")

            # Move to same dir
            oname2 = aa.get_name()
            aa.move(tdir2)
            self.assertEqual(aa.get_name(), join(tdir2, "aa"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertEqual(aa.get_name(), oname2)
            self.assertTrue(not aa.opsuccess, "move should be skipped")

            # Move overwrite - raise exception
            with open("aa", "w") as fh:
                fh.write(txt + txt)
            self.assertRaises(Exception, aa.move, tdir)

            self.assertRaisesRegex(Exception, "must be a valid Dir", aa.move, "/tmp/surenotexisT")

        # overwrite_rename
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            aa = File("aa").touch(txt)
            aa.move(tdir2, overwrite_rename=True)
            self.assertTrue(exists(join(tdir2, "aa")))
            self.assertFalse(exists(join(tdir, "aa")))

            aa = File("aa").touch(txt + txt)
            aa.move(tdir2, overwrite_rename=True)
            with open(join(tdir2, "aa")) as fh:
                self.assertEqual(fh.read(), txt + txt)
            with open(join(tdir2, "aa.1")) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertFalse(exists(join(tdir, "aa")))

            File(join(tdir2, "aa")).compress(File.gz)
            aa = File("aa").touch(txt + txt + txt).compress(File.gz)
            aa.move(tdir2, overwrite_rename=True)
            with File(join(tdir2, "aa.gz")) as file:
                self.assertEqual(file.read(), txt + txt + txt)  # newest
            with open(join(tdir2, "aa.1")) as fh:
                self.assertEqual(fh.read(), txt)  # oldest
            self.assertEqual(File(join(tdir2, "aa.2.gz")).read(), txt + txt)  # 2nd newest
            self.assertFalse(exists(join(tdir, "aa")))

    def test_safecopy(self):
        """ This is just testing the safe wrapper safecopy"""
        txt = 'fun times'
        with TempDir(name=True, chdir=True) as tdir:
            # pass case
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            self.assertTrue(aa.safecopy("bb"), "copy should be successful")
            orig = File("aa")
            self.assertEqual(orig.get_name(abspath=True), join(tdir, "aa"))
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertNotEqual(orig.get_name(abspath=True), aa.get_name(abspath=True))
            self.assertTrue(exists(orig.get_name()), "orig file must exist")
            self.assertTrue(aa.opsuccess, "operation successful")

        with TempDir(name=True, chdir=True) as tdir:
            # fail case bad dir
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            self.assertFalse(aa.safecopy("/down/the/rabbit/hole/"),
                             "safe copy should fails with none-existing dir")
            self.assertTrue(exists(aa.get_name()), "orig file must exist")

    def test_safemove(self):
        """ This is just testing the safe wrapper safemove"""
        txt = 'fun times'
        with TempDir(name=True, chdir=True) as tdir, TempDir(name=True) as tdir2:
            # pass case
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            oname = aa.get_name(abspath=True)
            self.assertTrue(aa.safemove(tdir2), "move should be successful")
            self.assertTrue(not exists(oname), "orig file must not exist")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt, "moved file should be readable")
            self.assertTrue(aa.opsuccess, "operation successful")

        with TempDir(name=True, chdir=True) as tdir:
            # fail case bad dir
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            self.assertFalse(aa.safemove("/down/the/rabbit/hole/"),
                             "safe move should fail with none-existing dir")
            self.assertTrue(exists(aa.get_name()), "orig file must exist")

    def test_rename(self):
        with TempDir(name=True, chdir=True) as tdir:
            # Successful rename
            txt = "The quick The The\nTheThe"
            with open("aa", "w") as fh:
                fh.write(txt)
            aa = File("aa")
            oname = aa.get_name()
            aa.rename("bb")
            self.assertEqual(basename(aa.get_name()), "bb")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertTrue(not exists(oname), "orig file must not exist")
            self.assertTrue(aa.opsuccess, "operation successful")

            # Rename to same name
            oname2 = aa.get_name()
            aa.rename("bb")
            self.assertEqual(basename(aa.get_name()), "bb")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)
            self.assertEqual(aa.get_name(), oname2)
            self.assertTrue(not aa.opsuccess, "rename should be skipped")

            # Rename overwrite
            with open("cc", "w") as fh:
                fh.write(txt + txt)
            aa.rename("cc")
            self.assertEqual(basename(aa.get_name()), "cc")
            with open(aa.get_name()) as fh:
                self.assertEqual(fh.read(), txt)

            # Error cases
            self.assertRaisesRegex(Exception, "must not contain any paths", aa.rename, "/tmp/somepath")

            self.assertRaisesRegex(Exception, "not match compression", aa.rename, "aaa.gz")

    def test_rename_incremental(self):
        with TempDir(name=True, chdir=True):
            # not existing case
            orig = File("filex").rename_incremental()
            self.assertFalse(orig.exists())

            # existing case
            targ = File("filex").touch('one')
            self.assertTrue(orig.exists())
            targ.rename_incremental()
            self.assertFalse(orig.exists())
            self.assertEqual(File("filex.1").read(), "one")

            # several case
            targ = File("filex").touch('two')
            targ.rename_incremental()
            targ = File("filex").touch('three')
            targ.rename_incremental()
            self.assertFalse(orig.exists())
            with File("filex.1") as file:
                self.assertEqual(file.read(), "one")
            with File("filex.2") as file:
                self.assertEqual(file.read(), "two")
            with File("filex.3") as file:
                self.assertEqual(file.read(), "three")
            self.assertEqual(set(os.listdir(".")), {'filex.2', 'filex.1', 'filex.3'})

            # one of the existing file is compressed
            File("filex.3").compress(File.gz)   # "filex.3.gz"
            targ = File("filex").touch('four')
            targ.rename_incremental()
            self.assertEqual(set(os.listdir(".")), {'filex.4', 'filex.2', 'filex.1', 'filex.3.gz'})

            # orig file is compressed
            File("filex.gz").touch()
            self.assertEqual(set(os.listdir(".")), {'filex.gz', 'filex.4', 'filex.2', 'filex.1', 'filex.3.gz'})
            targ = File("filex")
            targ.rename_incremental()
            self.assertEqual(set(os.listdir(".")), {'filex.5.gz', 'filex.4', 'filex.2', 'filex.1', 'filex.3.gz'})

        with TempDir(name=True, chdir=True):
            aa = File("filex").touch().compress(File.gz)
            File("filex.1").touch()
            aa.rename_incremental()
            self.assertEqual(set(os.listdir(".")), {'filex.1', 'filex.2.gz'})

        with TempDir(name=True, chdir=True):
            aa = File("filex").touch().compress(File.gz)
            File("filex.1").touch().compress(File.gz)
            aa.rename_incremental()
            self.assertEqual(set(os.listdir(".")), {'filex.1.gz', 'filex.2.gz'})

        with TempDir(name=True, chdir=True):
            aa = File("filex").touch()
            File("filex.1").touch().compress(File.gz)
            aa.rename_incremental()
            self.assertEqual(set(os.listdir(".")), {'filex.1.gz', 'filex.2'})

    def test_rename_incremental2(self):
        with TempDir(name=True, chdir=True) as tdir:
            # Simple case
            File(f'{tdir}/filex').touch()
            File(f'{tdir}/filex.1').touch()
            File(f'{tdir}/filex').rename_incremental()
            self.assertSetEqual(set(os.listdir(tdir)), {'filex.1', 'filex.2'})

            # bug 4/14/25, found from a very long 2025.1.1.1.1.1.1
            File(f'{tdir}/filex.2').unlink()
            File(f'{tdir}/filex.1').rename_incremental()
            self.assertSetEqual(set(os.listdir(tdir)), {'filex.2'})


class SplitFile_tests(TestCase):

    def test_basic(self):
        with TempDir(chdir=True, name=True) as td:
            # Do setup
            text = 'somestring'.join(str(x) for x in range(1000))
            self.assertEqual(len(text), 12880)   # just so we know the count
            File("input").touch(text)
            orig_md5 = md5(text)
            mkdirs("out")

            # size at 3000
            SplitFile("input", "out", size=3000)
            self.assertEqual(set(os.listdir("out")), {'file.4', 'file.2', 'file.3', 'file.0', 'file.1'})
            SplitFile("out", "result")
            with File("result") as file:
                self.assertEqual(md5(file.read()), orig_md5)

            # max iteration
            with self.assertRaisesRegex(Exception, "Maximum iteration"):
                SplitFile("out", "result2", size=3000, maxiter=3)
            with self.assertRaisesRegex(Exception, "Maximum iteration"):
                SplitFile("input", "out", size=3000, maxiter=3)

            # normal size - one file
            mkdirs("out2")
            SplitFile("input", "out2")
            self.assertEqual(set(os.listdir("out2")), {'file.0'})
            SplitFile("out2", "result2")
            with File("result2") as file:
                self.assertEqual(md5(file.read()), orig_md5)

            # two file split
            mkdirs("out3")
            SplitFile("input", "out3", size=10000)
            self.assertEqual(set(os.listdir("out3")), {'file.0', 'file.1'})
            SplitFile("out3", "result3")
            with File("result3") as file:
                self.assertEqual(md5(file.read()), orig_md5)

    def test_checks(self):
        with TempDir(chdir=True, name=True):
            File("input").touch("sometext")
            mkdirs("out")

            # invalid input
            with self.assertRaisesRegex(Exception, "is not a file"):
                SplitFile("notfound", "result")

            # split, output is not a dir
            with self.assertRaisesRegex(Exception, "is not an existing directory"):
                SplitFile("input", "result")

            # combine, output is a dir
            with self.assertRaisesRegex(Exception, "It must be a file"):
                SplitFile("out", "out")

    def test_twobyte(self):
        # set size at two
        with TempDir(chdir=True, name=True):
            File("input").touch("sometext")
            mkdirs("out")
            SplitFile("input", "out", size=2)
            self.assertEqual(len(os.listdir("out")), 5)
            SplitFile("out", "result")
            with File("result") as file:
                self.assertEqual(file.read(), "sometext")

        with TempDir(chdir=True, name=True):
            File("input").touch("sometexty")
            mkdirs("out")
            SplitFile("input", "out", size=2)
            self.assertEqual(len(os.listdir("out")), 5)
            SplitFile("out", "result")
            with File("result") as file:
                self.assertEqual(file.read(), "sometexty")

        # set size at one
        with TempDir(chdir=True, name=True):
            File("input").touch("sometext")
            mkdirs("out")
            SplitFile("input", "out", size=1)
            self.assertEqual(len(os.listdir("out")), 9)
            SplitFile("out", "result")
            with File("result") as file:
                self.assertEqual(file.read(), "sometext")

        # size at one, gzipped
        with TempDir(chdir=True, name=True):
            File("input").touch("sometext").compress(File.gz)
            mkdirs("out")
            SplitFile("input.gz", "out", size=1)
            self.assertGreater(len(os.listdir("out")), 15)
            SplitFile("out", "result.gz")
            with File("result.gz") as file:
                self.assertEqual(file.read(), "sometext")
                self.assertEqual(file.compression, File.gz)

    def test_binaryfile(self):
        inp = join(dirname(realpath(__file__)), 'files_different_time.tar')
        orig_md5 = File(inp).md5()
        self.assertEqual(len(orig_md5), 32)
        with TempDir(name=True) as td:
            SplitFile(inp, td, size=5000)
            self.assertEqual(len(os.listdir(td)), 5)
            SplitFile(td, join(td, "result"))
            self.assertEqual(File(join(td, "result")).md5(), orig_md5)

    def test_safeCreateFile(self):
        with TempDir(name=True, chdir=True) as tdir:
            # Pass cases
            self.assertTrue(files.safeCreateFile(os.path.join(tdir, "aa"),
                                                 is_text=True,
                                                 text="test text"),
                            "creation should be successful")

            self.assertTrue(files.safeCreateFile(os.path.join(tdir, "bb"),
                                                 is_text=False),
                            "creation should be successful")

            # success case: pre-existing file
            self.assertTrue(files.safeCreateFile(os.path.join(tdir, "aa")),
                            "creation should succeed even on existingfile")

            # Fail case: unexpected exception
            with patch("os.fdopen", Mock(side_effect=Exception('unexpected!'))):
                self.assertFalse(files.safeCreateFile(os.path.join(tdir, "cc")), "tmp file should fail with unexpected exception")

        # Fail case: none-existing dir
        self.assertFalse(files.safeCreateFile("nfs/no/this/doesnt/exist/aa"),
                         "creation should fail with none-existing dir")


class MaxParallel_Test(TestCase):

    def test_basic(self):
        with TempDir(name=True) as tdir:

            # setup
            class MyTest:
                @with_(MaxParallel, tdir, proc_max=1, timeout_sec=60 * 30, iterations=10, sleep=0.01)
                def foo_long(self):
                    return 1

                @with_(MaxParallel, tdir, proc_max=1, timeout_sec=-10, iterations=10, sleep=0.01)
                def foo_short(self):
                    return 2

            obj = MyTest()

            # pass case
            File(os.path.join(tdir, 'somefile1')).touch()
            self.assertEqual(obj.foo_long(), 1)
            self.assertEqual(obj.foo_long(), 1)
            self.assertEqual(len(os.listdir(tdir)), 1)

            # fail case
            File(os.path.join(tdir, 'somefile2')).touch()
            self.assertRaisesRegex(Exception, 'Max number of iterations', obj.foo_long)
            self.assertEqual(len(os.listdir(tdir)), 3)   # including denied.log
            self.assertEqual(len(File(join(tdir, "_denied.log")).read().split('\n')), 2)

            # stale case
            self.assertEqual(obj.foo_short(), 2)
            self.assertEqual(len(os.listdir(tdir)), 1)   # all files deleted except denied.log
            File(os.path.join(tdir, '_denied.log')).unlink()
            self.assertEqual(len(os.listdir(tdir)), 0)   # no more files

            # stale with exception
            File(os.path.join(tdir, 'somefile2')).touch()
            with MockVar(File, "unlink", Mock(side_effect=Exception)):
                # Exception will happen because of the MaxParallel's close() which calls unlink()
                self.assertRaises(Exception, obj.foo_short, 2)
            self.assertEqual(len(os.listdir(tdir)), 2)

            # wait loop
            File(os.path.join(tdir, '_denied.log')).unlink()
            with MockVar(File, 'realname', lambda x, y: y), \
                    MockVar(os, "listdir", MultiReturn([], [1, 1, 1, 1], [1, 1, 1, 1], [1])):
                self.assertEqual(obj.foo_short(), 2)
            print("==== log start")
            print(File(join(tdir, "_denied.log")).read())
            self.assertEqual(len(File(join(tdir, "_denied.log")).read().split('\n')), 2)
            self.assertIn('sleep_seconds: 0.02', File(join(tdir, "_denied.log")).read())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
