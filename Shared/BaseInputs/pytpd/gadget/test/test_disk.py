#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
disk related libraries
"""
import os.path

import setenv_unittest     # must be first import for unittests
from gadget.disk import _on_rm_error
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.disk import *
from gadget.shell import USERNAME, SystemCall, IS_UNIX, untar, IS_WIN
from gadget.strmore import group
from gadget.files import tempname, TempDir
from gadget.gizmo import MockVar, with_
from gadget.errors import ErrorInput
from unittest.mock import Mock, call, patch
from gadget.helperclass import CaptureStdout
from itertools import repeat
from io import StringIO
import gadget.disk as disk
import sys
from tp.testprogram import Env
import shutil
import time
from types import SimpleNamespace
try:
    import grp
    import pwd
except BaseException:
    pass


class Chmodr_tests(TestCase):

    @unittest.skipIf(IS_WIN, 'unix only due to file permission')
    def test_chmodr(self):
        with TempDir(name=True) as tdir:
            # Create the dir and put several nested files in it
            os.makedirs(join(tdir, 'a', 'b'), 0o777)
            File(join(tdir, 'filea')).touch()
            File(join(tdir, 'a', 'fileb')).touch()
            File(join(tdir, 'a', 'b', 'filec')).touch()

            perm = 0o750
            andval = 0o777
            oct_perm = oct(perm)
            chmodr(tdir, "%s" % oct_perm)
            self.assertEqual(oct(os.stat(tdir).st_mode & andval), oct_perm)
            self.assertEqual(oct(os.stat(join(tdir, 'a')).st_mode & andval), oct_perm)
            self.assertEqual(oct(os.stat(join(tdir, 'a', 'b')).st_mode & andval), oct_perm)
            self.assertEqual(oct(os.stat(join(tdir, 'filea')).st_mode & andval), oct_perm)
            self.assertEqual(oct(os.stat(join(tdir, 'a', 'fileb')).st_mode & andval), oct_perm)
            self.assertEqual(oct(os.stat(join(tdir, 'a', 'b', 'filec')).st_mode & andval), oct_perm)

        # softlink should be skipped
        with TempDir(name=True, delete=True) as tdir:
            File(join(tdir, "aa")).touch()
            File(join(tdir, "subdir", "aa")).touch(mkdir=True)
            os.symlink("aa", join(tdir, "bb"))
            os.symlink("aa", join(tdir, "subdir", "bb"))
            os.symlink("subdir", join(tdir, "cc"))
            with MockVar(disk, "File", Mock()) as m:
                chmodr(tdir, "0750")
                self.assertEqual(m.call_args_list, [call(tdir),
                                                    call(tdir),
                                                    call(join(tdir, "aa")),
                                                    call(join(tdir, "aa")),
                                                    call(join(tdir, "subdir")),
                                                    call(join(tdir, "subdir")),
                                                    call(join(tdir, "subdir", "aa")),
                                                    call(join(tdir, "subdir", "aa"))
                                                    ])


class TestMkdir(TestCase):

    def test_basic(self):
        with TempDir(name=True) as tdir:
            self.assertTrue(exists(tdir))

            # already exist - ignore
            self.assertEqual(mkdirs(tdir), tdir)

            # successful create
            self.assertEqual(mkdirs(join(tdir, "a", "b")), join(tdir, "a", "b"))
            self.assertTrue(isdir(join(tdir, "a", "b")), "Dir must exist")

            # successful create - third dir
            mkdirs(join(tdir, "a", "b", "c"))
            self.assertTrue(isdir(join(tdir, "a", "b", "c")), "Dir must exist")

    @unittest.skipIf(IS_WIN, 'unix only due to file permission')
    def test_mkdirs(self):
        with TempDir(name=True) as tdir:
            # mode check1
            mkdirs(join(tdir, "c"), mode="0500", check_sticky=False)
            self.assertRaises(Exception, File(join(tdir, "c", "newfile")).touch)

            # mode check2
            mkdirs(join(tdir, "d"), mode="0750", check_sticky=False)
            File(join(tdir, "d", "newfile")).touch()
            self.assertTrue(exists(join(tdir, "d", "newfile")), "file must exist")

            # mode check sticky
            with self.assertRaisesRegex(Exception, 'Pls add sticky bit'):
                mkdirs(join(tdir, "e"), mode="0750")

            # set_sticky
            mkdirs(join(tdir, "e"), mode="0750", set_sticky=True)
            self.assertEqual(oct(os.stat(join(tdir, "e")).st_mode & 0o7777).replace('o', ''), "02750")

        # relative path
        with TempDir(chdir=True):
            # already exist - ignore
            mkdirs(join("a", "b", "c"))
            self.assertTrue(isdir(join("a", "b", "c")), "dir must exist")

        # empty string
        self.assertEqual(mkdirs(""), "")

    def test_mkdir_existfile(self):
        with TempName(name=True) as tn:
            File(tn).touch()
            self.assertRaisesRegex(Exception, "cannot make.*directory", mkdirs, tn)

    def test_safemkdirs(self):
        with TempDir(name=True) as tdir:
            # Success case - already exist - ignore
            self.assertTrue(safemkdirs(tdir), "safemkdirs should return True on existing dir")
            # Successful create
            safemkdirs(join(tdir, "a", "b"))
            self.assertTrue(isdir(join(tdir, "a", "b")), "Dir must exist")
        # Fail case - existing file name as dirname
        with TempName(name=True) as tn:
            File(tn).touch()
            self.assertFalse(safemkdirs(tn), "safemkdirs should return false with filename given as dir")

    @unittest.skipIf(IS_WIN, 'unix only due to file permission')
    def test_gid(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            # default groups
            mkdirs(join(tdir, "newdir"))
            res = File(join(tdir, "newdir")).lsltrd()
            self.assertIn('gdlusers', res)

    @unittest.skipIf(IS_WIN, 'unix only due to file permission')
    def test_gid_sticky(self):
        with TempDir(name=True, delete=True) as tdir:
            mkdirs(join(tdir, "newdir"), mode='02770')
            res = File(join(tdir, "newdir")).lsltrd()
            self.assertIn('drwxrws---', res)

    def test_mkdir_parallel(self):
        # tvpvhelp 24968
        with TempDir(name=True) as tdir:
            newdir = join(tdir, 'new')
            disk._mkdir_parallel(newdir)
            self.assertTrue(isdir(newdir))
            disk._mkdir_parallel(newdir)   # should not raise exception!

            newdir = join(tdir, 'file')
            File(newdir).touch()
            with self.assertRaises(OSError):
                disk._mkdir_parallel(newdir)

    def proof_24968(self):
        # To prove problem, execute this test on two different machines at the same time!
        newdir = 'xx'
        if isdir(newdir):
            raise Exception("rmdir %s first" % newdir)
        tt = int(time.time() / 10) * 10 + 10.0
        print("waiting for", tt, "time is", time.time())
        while True:
            print(time.time(), isdir(newdir), tt)
            if time.time() > tt:
                mkdirs(newdir)
                print("Created at", time.time())
                break


class ChdirTest(TestCase):

    def test_chdir(self):
        odir = os.getcwd()
        with TempDir() as t:
            self.assertEqual(odir, os.getcwd())
            with Chdir(t.name()) as od:
                self.assertEqual(od, odir)
                self.assertEqual(t.name(), os.getcwd())   # New directory
                self.assertNotEqual(t.name(), od)

            # Directory is back to normal
            self.assertEqual(odir, os.getcwd())

        # original directory got deleted
        with TempDir(chdir=True) as origdir:
            with TempDir(name=True) as newdir:
                with Chdir(newdir):
                    origdir.close()  # delete it

        # empty string input (aka, '.')
        with TempDir(chdir=True, name=True) as tdir:
            with Chdir(''):
                self.assertEqual(os.getcwd(), tdir)


class get_open_file_handle_tests(TestCase):
    @unittest.skipIf(IS_WIN, 'unix only due to open file handles')
    @unittest.skipIf(*is_ut_option("OPTIONAL", message="Must Run standalone"))
    def test_basic_open_file_handle(self):

        self.assertEqual(get_open_file_handles(), [])
        scriptname = sys.argv[0]
        with open(scriptname) as fh:
            self.assertEqual(len(get_open_file_handles()), 1)
        self.assertEqual(get_open_file_handles(), [])
        cnt = 0
        for line in open(scriptname):
            cnt += 1
        self.assertGreater(cnt, 100)    # number of lines
        self.assertEqual(get_open_file_handles(), [])   # using open will close it


class freeSpaceTests(TestCase):

    def rundf(self, path):
        res = SystemCall(["df", path]).run_outonly()
        if regex(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\%", res):
            # tot=int(group(1))
            free = int(group(3))
            pct = 100 - int(group(4))
            self.assertEqual(get_free_space(path), free)    # free space
            self.assertEqual(get_free_space(path, pct=True), pct)
        else:
            self.fail("df regex failed")

    @unittest.skipIf(not exists(Env.xpath('/intel')), '/intel not exist')
    def test_get_free_diskspace(self):
        self.assertGreater(get_free_diskspace(Env.xpath('/intel')), 1)
        self.assertEqual(get_free_diskspace(Env.xpath('/intel/tpvxalidation')), -1)

    @unittest.skipIf(IS_WIN, 'unix only use df command')
    @unittest.skipIf(*is_ut_option('OPTIONAL', message="Must run in a quiet disk. Do not run in parallel"))
    def test_get_free_space_compare(self):
        self.rundf(".")

    def test_get_disk_stats(self):
        df_res = ""
        disk_path = "some/path"
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, df_res))):
            with self.assertRaisesRegex(ExceptionEnv, "Cannot decode"):
                get_disk_stats(disk_path)

        df_res = 'some bad line'
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, df_res))):
            with self.assertRaisesRegex(ExceptionEnv, "No disk stats available"):
                get_disk_stats(disk_path)

        df_res = """Filesystem                   Size  Used Avail Use% Mounted on
pdxc14n02a-1:/nehalem.pde.7 157286528 114833696  42452832  74% /nfs/pdx/disks/nehalem.pde.7"""
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, df_res))):
            stats = get_disk_stats(disk_path)
            self.assertEqual(stats['total'], 157286528)
            self.assertEqual(stats['raw'], df_res)
            self.assertEqual(stats['diskroot'], "/nfs/pdx/disks/nehalem.pde.7")
            self.assertEqual(get_percent_used(disk_path), 74)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_get_free_space(self):
        # normal
        self.assertGreater(get_free_space("/tmp"), 1000)

        # debug
        free, raw = get_free_space("/tmp", debug=True)
        self.assertGreater(free, 1000)
        self.assertIn('1024-blocks', raw)

        # pct
        self.assertGreaterEqual(get_free_space("/tmp", pct=True), 0)
        self.assertLessEqual(get_free_space("/tmp", pct=True), 100)


class GetUserDiskThresholdTests(TestCase):

    def test_empty_or_none_path(self):
        # Test empty string
        free_kb, free_gb, is_sufficient = check_disk_threshold("")
        self.assertIsNone(free_kb)

        # Test None
        free_kb, free_gb, is_sufficient = check_disk_threshold(None)
        self.assertIsNone(free_kb)

        # Test empty string - raise mode
        free_kb, free_gb, is_sufficient = check_disk_threshold("", raise_on_insufficient=False)
        self.assertIsNone(free_kb)
        self.assertIsNone(free_gb)
        self.assertTrue(is_sufficient)

        # Test None - raise mode
        free_kb, free_gb, is_sufficient = check_disk_threshold(None, raise_on_insufficient=False)
        self.assertIsNone(free_kb)
        self.assertIsNone(free_gb)
        self.assertTrue(is_sufficient)

        free_kb, free_gb, is_sufficient = check_disk_threshold("C:")
        self.assertIsNone(free_kb)

        # Raise mode
        free_kb, free_gb, is_sufficient = check_disk_threshold("C:", raise_on_insufficient=False)
        self.assertIsNone(free_kb)
        self.assertIsNone(free_gb)
        self.assertTrue(is_sufficient)

        # Test with non-existent path
        with MockVar(disk, 'get_free_diskspace', Mock(return_value=-1)):
            free_kb, free_gb, is_sufficient = check_disk_threshold("/nonexistent/path")
            self.assertIsNone(free_kb)

            free_kb, free_gb, is_sufficient = check_disk_threshold("/nonexistent/path", raise_on_insufficient=False)
            self.assertIsNone(free_kb)
            self.assertIsNone(free_gb)
            self.assertTrue(is_sufficient)

        # Test when disk space cannot be determined
        with TempDir(name=True) as tdir:
            with MockVar(disk, 'get_free_diskspace', Mock(return_value=-1)):
                # Default mode
                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir)
                self.assertIsNone(free_kb)

                # Raise mode
                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, raise_on_insufficient=False)
                self.assertIsNone(free_kb)
                self.assertIsNone(free_gb)
                self.assertTrue(is_sufficient)  # Should not fail when can't determine

    def test_valid_directory_sufficient_space(self):
        # Test with valid directory having sufficient space
        with TempDir(name=True) as tdir:
            with MockVar(disk, 'get_free_diskspace', Mock(return_value=5 * 1024 * 1024)):  # 5GB
                # Default mode
                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=3)
                self.assertTrue(is_sufficient)

                # Raise mode
                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=3, raise_on_insufficient=False)
                self.assertEqual(free_kb, 5 * 1024 * 1024)
                self.assertAlmostEqual(free_gb, 5.0, places=2)
                self.assertTrue(is_sufficient)

    def test_valid_directory_insufficient_space(self):
        # Test with valid directory having insufficient space
        with TempDir(name=True) as tdir:
            with MockVar(disk, 'get_free_diskspace', Mock(return_value=1 * 1024 * 1024)):  # 1GB
                # Default mode
                with self.assertRaises(ErrorInput):
                    check_disk_threshold(tdir, threshold_gb=3)

                # Raise mode
                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=3, raise_on_insufficient=False)
                self.assertEqual(free_kb, 1 * 1024 * 1024)
                self.assertAlmostEqual(free_gb, 1.0, places=2)
                self.assertFalse(is_sufficient)

    def test_file_path_uses_directory(self):
        # Test that file path uses its parent directory
        with TempDir(name=True) as tdir:
            temp_file = join(tdir, 'test_file.txt')
            File(temp_file).touch()

            with MockVar(disk, 'get_free_diskspace', Mock(return_value=4 * 1024 * 1024)) as mock_func:  # 4GB
                ree_kb, free_gb, is_sufficient = check_disk_threshold(temp_file, threshold_gb=3)
                self.assertTrue(is_sufficient)
                # Should be called with the directory, not the file
                mock_func.assert_called_once_with(tdir)

                mock_func.reset_mock()
                free_kb, free_gb, is_sufficient = check_disk_threshold(temp_file, threshold_gb=3, raise_on_insufficient=False)
                self.assertEqual(free_kb, 4 * 1024 * 1024)
                self.assertAlmostEqual(free_gb, 4.0, places=2)
                self.assertTrue(is_sufficient)
                mock_func.assert_called_once_with(tdir)

    def test_custom_threshold(self):
        # Test with custom threshold
        with TempDir(name=True) as tdir:
            with MockVar(disk, 'get_free_diskspace', Mock(return_value=2 * 1024 * 1024)):  # 2GB
                # Test with 1GB threshold (should be sufficient)
                result = check_disk_threshold(tdir, threshold_gb=1)
                self.assertEqual(result, (2097152, 2.0, True))

                # Test with 5GB threshold (should be insufficient)
                with self.assertRaises(ErrorInput):
                    check_disk_threshold(tdir, threshold_gb=5)

                # Test with raise mode
                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=1, raise_on_insufficient=False)
                self.assertTrue(is_sufficient)

                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=5, raise_on_insufficient=False)
                self.assertFalse(is_sufficient)

    def test_boundary_conditions(self):
        # Test boundary conditions
        with TempDir(name=True) as tdir:
            # Test exactly at threshold (3GB = 3 * 1024 * 1024 KB)
            threshold_kb = 3 * 1024 * 1024
            with MockVar(disk, 'get_free_diskspace', Mock(return_value=threshold_kb)):
                # Should be False because we need MORE than threshold (> not >=)
                with self.assertRaises(ErrorInput):
                    check_disk_threshold(tdir, threshold_gb=3)

                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=3, raise_on_insufficient=False)
                self.assertFalse(is_sufficient)

            # Test just above threshold
            with MockVar(disk, 'get_free_diskspace', Mock(return_value=threshold_kb + 1)):
                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=3)
                self.assertTrue(is_sufficient)

                free_kb, free_gb, is_sufficient = check_disk_threshold(tdir, threshold_gb=3, raise_on_insufficient=False)
                self.assertTrue(is_sufficient)


class Allfiles_Test(TestCase):
    def test_allfiles(self):
        with TempDir(chdir=True) as tdir:
            os.mkdir('dir1')
            os.mkdir('.svn')
            open("file1.py", "w").write('text')
            open(join('dir1', "file2.py"), "w").write('text1')
            open(join('dir1', "filedummy.pyc"), "w").write('text')
            open(join('.svn', "file3.py"), "w").write('text2')
            print({Env.xpath(_path) for _path in set(allfiles("."))})
            self.assertEqual({Env.xpath(_path) for _path in set(allfiles("."))},
                             {'./.svn/file3.py', './file1.py', './dir1/file2.py', './dir1/filedummy.pyc'})
            self.assertEqual({Env.xpath(_path) for _path in set(allfiles(".", skipsvn=True))},
                             {'./file1.py', './dir1/file2.py', './dir1/filedummy.pyc'})
            self.assertEqual(len(set(allfiles(tdir.name(), skipsvn=True))), 3)

            # regex
            self.assertEqual({Env.xpath(_path) for _path in set(allfiles(".", skipsvn=True, rx=regex.compile(r"\.py$")))},
                             {'./file1.py', './dir1/file2.py'})

    def test_alldirs(self):
        with TempDir(chdir=True) as tdir:
            os.mkdir('dir1')
            os.mkdir('.svn')
            open("file1.py", "w").write('text')
            open(join('dir1', "file2.py"), "w").write('text1')
            open(join('dir1', "filedummy.pyc"), "w").write('text')
            open(join('.svn', "file3.py"), "w").write('text2')

            self.assertEqual({Env.xpath(_path) for _path in set(alldirs("."))}, {'./dir1', './.svn', '.'})
            self.assertEqual({Env.xpath(_path) for _path in set(alldirs(".", skipsvn=True))},
                             {'./dir1', '.'})
            # regex
            self.assertEqual({Env.xpath(_path) for _path in set(alldirs(".", rx=regex.compile('svn$')))},
                             {'./.svn'})

    def test_allfiles_recurse(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            File(join(tdir, "subdir1/subdir2/subdir3/file1")).touch(mkdir=True)
            File(join(tdir, "subdir1/file2")).touch(mkdir=True)
            File(join(tdir, "subdir1/file3")).touch(mkdir=True)
            File(join(tdir, ".svn/filex")).touch(mkdir=True)
            File(join(tdir, "file5")).touch(mkdir=True)
            File(join(tdir, "file6")).touch(mkdir=True)
            # recursive softlink
            os.symlink(join(tdir), join(tdir, "subdir1/somedir"))  # create a softlink that is recursive
            # empty dir
            os.mkdir(join(tdir, "emptydir"))
            # broken link
            os.symlink("missingfile", join(tdir, "brokenlink"))  # create a softlink that is recursive

            self.assertEqual(set(Allfiles(".")),
                             {'./subdir1/subdir2/subdir3/file1',
                              './subdir1/file3',
                              './subdir1/file2',
                              './.svn/filex',
                              './file6',
                              './file5'})

            # checkexist
            self.assertEqual(set(Allfiles(".", existcheck=False, skipsvn=True)),
                             {'./subdir1/subdir2/subdir3/file1',
                              './subdir1/file3',
                              './subdir1/file2',
                              './file6',
                              './file5',
                              './brokenlink'})

            # dir not found
            self.assertEqual(list(Allfiles(join(tdir, "notexist"))), [])

            # rx search1 - string
            self.assertEqual(set(Allfiles(".", rx="subdir")),
                             {'./subdir1/subdir2/subdir3/file1',
                              './subdir1/file3',
                              './subdir1/file2'})

            # rx search2 - compiled regex, and fullpath
            self.assertEqual(set(Allfiles(".", rx=regex.compile("subdir2"), fullpath=True)),
                             {tdir + '/' + 'subdir1/subdir2/subdir3/file1'
                              })

            # softlink dir
            with TempDir(name=True) as tdir2:
                File(join(tdir2, "filef")).touch()
                os.symlink(tdir2, join(tdir, "softlink1"))
                self.assertEqual(set(Allfiles(".")),
                                 {'./subdir1/subdir2/subdir3/file1',
                                  './subdir1/file3',
                                  './subdir1/file2',
                                  './softlink1/filef',
                                  './.svn/filex',
                                  './file6',
                                  './file5'})

                self.assertEqual(set(Allfiles(".", skiplink=True)),
                                 {'./subdir1/subdir2/subdir3/file1',
                                  './subdir1/file3',
                                  './subdir1/file2',
                                  './.svn/filex',
                                  './file6',
                                  './file5'})

    @unittest.skipIf(IS_WIN, 'unix only due to file permission')
    def test_dir_not_readable(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            File(join(tdir, "subdir1/subdir2/subdir3/file1")).touch(mkdir=True)
            File(join(tdir, "subdir1/file2")).touch(mkdir=True)
            File(join(tdir, "subdir1/file3")).touch(mkdir=True)
            File(join(tdir, "subdir1/subdir2")).chmod("0000")
            try:
                res = set(Allfiles(".", skiplink=True))
            except BaseException:
                res = set()
            File(join(tdir, "subdir1/subdir2")).chmod("0750")
            self.assertEqual(res, {'./subdir1/file3',
                                   './subdir1/file2'})

    def test_size(self):
        with TempDir() as temp_dir:
            f = File(join(temp_dir.name(), "tmp_file"))
            f.touch("aaa")
            all_files_dir = Allfiles(temp_dir.name())
            self.assertEqual(all_files_dir.size(Size.B), 3)
            self.assertEqual(all_files_dir.size(Size.KB), 3. / (1024**1))
            self.assertEqual(all_files_dir.size(Size.MB), 3. / (1024**2))
            self.assertEqual(all_files_dir.size(Size.GB), 3. / (1024**3))
            all_files_file = Allfiles(f.name)
            self.assertEqual(all_files_file.size(Size.B), 3)
            self.assertEqual(all_files_file.size(Size.KB), 3. / (1024 ** 1))
            self.assertEqual(all_files_file.size(Size.MB), 3. / (1024 ** 2))
            self.assertEqual(all_files_file.size(Size.GB), 3. / (1024 ** 3))


class VariousTest(TestCase):

    def test_delete_oldest(self):
        with TempDir(name=True, chdir=True) as tdir:
            today = 1683058853
            File(f'./a').touch(mtime=today - 500)
            File(f'./b').touch(mtime=today - 400)
            File(f'./c').touch(mtime=today - 300)
            File(f'./d').touch(mtime=today - 200)
            File(f'./e').touch(mtime=today - 100)
            self.assertEqual(delete_oldest('.', keep=2, delete=False), ['./a', './b', './c'])
            self.assertEqual(delete_oldest('.', keep=2), ['./a', './b', './c'])
            self.assertEqual(delete_oldest('/notexist'), [])
            self.assertEqual(set(os.listdir(tdir)), {'d', 'e'})
            self.assertEqual(delete_oldest('.', keep=1, message=None), ['./d'])

    def test_delete_oldest_wild(self):
        with TempDir(name=True, chdir=True) as tdir:
            today = 1683058853
            File(f'./a.txt').touch(mtime=today - 500)
            File(f'./b.txt').touch(mtime=today - 400)
            File(f'./c.txt').touch(mtime=today - 300)
            File(f'./d.csv').touch(mtime=today - 200)
            File(f'./e.csv').touch(mtime=today - 100)
            self.assertEqual(delete_oldest('./*.txt', keep=1, delete=False), ['./a.txt', './b.txt'])
            self.assertEqual(delete_oldest('./*.csv', keep=1, delete=False), ['./d.csv'])
            self.assertEqual(delete_oldest('./*', keep=1, delete=False), ['./a.txt', './b.txt', './c.txt', './d.csv'])
            self.assertEqual(delete_oldest('./*.json', keep=1, delete=False), [])   # special case - none found
            self.assertEqual(delete_oldest('.', keep=1, delete=False), ['./a.txt', './b.txt', './c.txt', './d.csv'])

    def test_delete_oldest_age(self):
        with TempDir(name=True, chdir=True) as tdir:
            today = time.time()
            File(f'./a').touch(mtime=today - 500)
            File(f'./b').touch(mtime=today - 400)
            File(f'./c').touch(mtime=today - 300)
            File(f'./d').touch(mtime=today - 200)
            File(f'./e').touch(mtime=today - 100)
            self.assertEqual(delete_oldest_age('.', age=250, delete=False), ['./a', './b', './c'])
            self.assertEqual(delete_oldest_age('.', age=150), ['./a', './b', './c', './d'])
            self.assertEqual(delete_oldest_age('/notexist'), [])
            self.assertEqual(os.listdir(tdir), ['e'])
            self.assertEqual(delete_oldest_age('.', age=0, message=None), ['./e'])

    def test_rmtree(self):
        with TempDir(chdir=True, name=True) as tdir:
            File(f'{tdir}/dir1/ro/a.txt').touch(mkdir=True)
            File(f'{tdir}/dir1/ro/b.txt').touch(mkdir=True)
            File(f'{tdir}/dir1/c.txt').touch(mkdir=True)
            File(f'{tdir}/dir1/ro/a.txt').chmod('02550')

            # This is a windows thing, uncomment below
            if IS_WIN:
                with self.assertRaises(PermissionError):
                    shutil.rmtree(f'{tdir}/dir1')
                print("YES, shutil.rmtree() raised error")

            self.assertTrue(isdir(f'{tdir}/dir1'))
            rmtree(f'{tdir}/dir1')
            self.assertFalse(isdir(f'{tdir}/dir1'))

            # _on_rm_error
            ff = File(f'{tdir}/dir1/ro/a.txt').touch(mkdir=True)
            ff.chmod('02550')
            _on_rm_error(None, ff.get_name(), None)
            self.assertFalse(exists(ff.get_name()))

            # exception case
            File(f'{tdir}/dir1/ro/a.txt').touch(mkdir=True)
            with MockVar(shutil, 'rmtree', Mock(side_effect=Exception)):
                with self.assertRaises(Exception):
                    rmtree(f'{tdir}/dir1')   # Except fail
                rmtree(f'{tdir}/dir1', ignore_error=True)   # no fails

    def test_size_dir(self):
        with TempDir(chdir=True, name=True) as tdir:
            File("file1").touch(''.join(repeat('abcdefghij', 200)))
            File("file2").touch(''.join(repeat('abcdefghij', 300)))
            self.assertEqual(size_dir(tdir), 5000)

        # sizedir with broken link
        with TempDir(chdir=True, name=True) as tdir:
            File("file1").touch(''.join(repeat('abcdefghij', 200)))
            os.symlink('notfound', 'file2')
            self.assertEqual(size_dir(tdir), 2000)

    def test_listdir_noerror(self):
        with TempDir(name=True) as tdir:
            File(join(tdir, "aa")).touch()
            self.assertEqual(listdir_noerror(tdir), ['aa'])
            self.assertEqual(listdir_noerror(tdir + "2"), [])

    @unittest.skipIf(IS_WIN, 'Windows cannot delete a directory in the folder')
    def test_cwd(self):
        with TempDir(chdir=True, name=True) as tdir:
            # directory exist
            self.assertEqual(cwd(), tdir)

            # directory does not exist
            os.mkdir("yay")
            os.chdir("yay")
            os.rmdir(join(tdir, "yay"))
            self.assertEqual(cwd(), "/not_available")

    def test_copy_tree(self):

        with TempDir(chdir=True, name=True) as tdir:
            File(join("dir1", "dir2", "dir3", "file1")).touch("abc", mkdir=True)
            File(join("dir1", "file2")).touch("def", mkdir=True)
            File(join("dir1", "dir2", "file3")).touch("ghi", mkdir=True)
            os.symlink(join("dir2", "dir3", "file1"), join("dir1", "file2link"))

            with TempDir(chdir=True, name=True) as tdir2:
                copy_tree(join(tdir, "dir1"), join(tdir2, "dir1"))
                self.assertEqual(File("dir1/dir2/dir3/file1").fh().read(), "abc")
                self.assertEqual(File("dir1/file2").fh().read(), "def")
                self.assertEqual(File("dir1/dir2/file3").fh().read(), "ghi")
                self.assertFalse(islink("dir1/file2link"))

                # do it again
                copy_tree(join(tdir, "dir1"), join(tdir2, "dir1"))
                self.assertEqual(File("dir1/dir2/dir3/file1").fh().read(), "abc")
                self.assertEqual(File("dir1/file2").fh().read(), "def")
                self.assertEqual(File("dir1/dir2/file3").fh().read(), "ghi")

                # change a file
                with open(join(tdir, "dir1/file2"), "w") as fh:
                    fh.write("new")
                copy_tree(join(tdir, "dir1"), join(tdir2, "dir1"))
                self.assertEqual(File("dir1/dir2/dir3/file1").fh().read(), "abc")
                self.assertEqual(File("dir1/file2").fh().read(), "new")
                self.assertEqual(File("dir1/dir2/file3").fh().read(), "ghi")

            # preserve_synlinks test
            with open(join(tdir, "dir1/file2"), "w") as fh:
                fh.write("def")
            with TempDir(chdir=True, name=True) as tdir2:
                copy_tree(join(tdir, "dir1"), join(tdir2, "dir1"), preserve_symlinks=True, verbose=1)
                self.assertEqual(File("dir1/dir2/dir3/file1").fh().read(), "abc")
                self.assertEqual(File("dir1/file2").fh().read(), "def")
                self.assertEqual(File("dir1/dir2/file3").fh().read(), "ghi")
                self.assertTrue(islink("dir1/file2link"))
                self.assertEqual(File("dir1/file2link").fh().read(), "abc")

                # do it again
                copy_tree(join(tdir, "dir1"), join(tdir2, "dir1"), preserve_symlinks=True)
                self.assertEqual(File("dir1/dir2/dir3/file1").fh().read(), "abc")
                self.assertEqual(File("dir1/file2").fh().read(), "def")
                self.assertEqual(File("dir1/dir2/file3").fh().read(), "ghi")
                self.assertTrue(islink("dir1/file2link"))
                self.assertEqual(File("dir1/file2link").fh().read(), "abc")

                # softlink changed
                os.unlink(join(tdir, "dir1/file2link"))
                os.symlink("file2", join(tdir, "dir1/file2link"))
                copy_tree(join(tdir, "dir1"), join(tdir2, "dir1"), preserve_symlinks=True)
                self.assertEqual(File("dir1/dir2/dir3/file1").fh().read(), "abc")
                self.assertEqual(File("dir1/file2").fh().read(), "def")
                self.assertEqual(File("dir1/dir2/file3").fh().read(), "ghi")
                self.assertTrue(islink("dir1/file2link"))
                self.assertEqual(File("dir1/file2link").fh().read(), "def")

            # error checks
            with TempDir(chdir=True, name=True) as tdir2:
                with self.assertRaisesRegex(Exception, "not a directory"):
                    copy_tree(join(tdir, "dir1A"), join(tdir2), preserve_symlinks=True, verbose=1)

    def test_comparedir(self):

        with TempDir(name=True, chdir=True) as tdir:
            File("d1/subdir/u1").touch(mkdir=True)
            File("d1/subdir/f1").touch("abcd", mkdir=True)
            File("d1/subdir/f2").touch("ghi", mkdir=True)

            File("d2/subdir/u2").touch(mkdir=True)
            File("d2/subdir/f1").touch("abcd", mkdir=True)
            File("d2/subdir/f2").touch("ghij", mkdir=True)

            with MockVar(sys, "stdout", StringIO()) as p:
                comparedir("d1", "d2")
                res = p.getvalue()
                self.assertEqual(len(res.split('\n')), 4)
                self.assertIn('[subdir/u1] not exist in', res)
                self.assertIn('[subdir/u2] not exist in', res)
                self.assertIn('subdir/f2] is different', res)

    def test_is_dir_writeable(self):
        if IS_UNIX:
            self.assertFalse(is_dir_writeable('/'))
        with TempDir(name=True, chdir=True) as tdir:
            self.assertFalse(is_dir_writeable(join(tdir, "notexist")))
            self.assertTrue(is_dir_writeable(tdir))
            self.assertEqual(os.listdir(tdir), [])

    def test_listdir_fullpath(self):
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1")).touch()
            File(join(tdir, "f2")).touch()
            self.assertEqual(set(listdir_fullpath(tdir)), {join(tdir, "f1"), join(tdir, "f2")})

    def test_listdir_nodot(self):
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1")).touch()
            self.assertEqual(listdir_nodot(tdir), ['f1'])
            File(join(tdir, "f2")).touch()
            File(join(tdir, ".f3")).touch()
            File(join(tdir, ".f4")).touch()
            self.assertItemsEqual(listdir_nodot(tdir), ['f1', 'f2'])

        with TempDir(name=True) as tdir:
            File(join(tdir, ".f1")).touch()
            self.assertEqual(listdir_nodot(tdir), [])

    def test_dir_sha1(self):
        id = '2eb9fd568456690b6331822cdac7eb3fe2e3caa5'

        # reference
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1.py")).touch('abcdef')
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertEqual(sha_case1, id)

        # case1 - nothing changed
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1.py")).touch('abcdef')
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertEqual(sha_case1, id)

        # case2 - one file added
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1.py")).touch('abcdef')
            File(join(tdir, "f2.py")).touch('abcdefg')
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertNotEqual(sha_case1, id)

        # case3 - one file deleted
        with TempDir(name=True) as tdir:
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertNotEqual(sha_case1, id)

        # case4 - one file modified
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1.py")).touch('abcdefg')
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertNotEqual(sha_case1, id)

        # case5 - .pyc ignore
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1.py")).touch('abcdef')
            File(join(tdir, "f1.pyc")).touch('abcdef')
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertEqual(sha_case1, id)

        # case6 - .pyo ignore
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1.py")).touch('abcdef')
            File(join(tdir, "f1.pyo")).touch('abcdef')
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertEqual(sha_case1, id)

        # case7 - .svn skipped
        with TempDir(name=True) as tdir:
            File(join(tdir, "f1.py")).touch('abcdef')
            File(join(tdir, ".svn/f1.py")).touch('abcdef', mkdir=True)
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertEqual(sha_case1, id)

        # case8 - file is renamed
        with TempDir(name=True) as tdir:
            File(join(tdir, "f2.py")).touch('abcdef')
            File(join(tdir, "TST/config.py")).touch('abcdefg', mkdir=True)
            sha_case1 = dir_sha1(tdir)
            self.assertNotEqual(sha_case1, id)

    @unittest.skipIf(IS_WIN, 'UNIX only')
    def test_check_tmp(self):
        # pass case
        check_tmp()

        # tmp is full
        with self.assertRaisesRegex(Exception, "is full"):
            check_tmp(1000000000000)

        # tmp is readonly
        with MockVar(disk, 'is_dir_writeable', Mock(return_value=False)):
            with self.assertRaisesRegex(Exception, "is readonly"):
                check_tmp()

        # var/tmp is full
        with CaptureStdout() as p:
            check_tmp(var_limitkb=1000000000000)
            self.assertIn("Need /var/tmp to have some", p.getvalue())

    def test_cmpdir(self):
        # md5 is different
        with TempDir(name=True, chdir=True) as tdir:
            File("d1/subdir/u1").touch(mkdir=True)
            File("d1/subdir/f1").touch("abcd", mkdir=True)
            File("d1/subdir/f2").touch("ghi", mkdir=True)

            File("d2/subdir/u2").touch(mkdir=True)
            File("d2/subdir/f1").touch("abcd", mkdir=True)
            File("d2/subdir/f2").touch("ghj", mkdir=True)

            diffed, added, removed = cmpdir("d1", "d2")
            self.assertEqual(diffed, {'subdir/f2'})
            self.assertEqual(added, {'subdir/u2'})
            self.assertEqual(removed, {'subdir/u1'})

        # size is different
        with TempDir(name=True, chdir=True) as tdir:
            File("d1/subdir/u1").touch(mkdir=True)
            File("d1/subdir/f1").touch("abcd", mkdir=True)
            File("d1/subdir/f2").touch("ghi", mkdir=True)

            File("d2/subdir/u2").touch(mkdir=True)
            File("d2/subdir/f1").touch("abcd", mkdir=True)
            File("d2/subdir/f2").touch("ghij", mkdir=True)

            diffed, added, removed = cmpdir("d1", "d2")
            self.assertEqual(diffed, {'subdir/f2'})
            self.assertEqual(added, {'subdir/u2'})
            self.assertEqual(removed, {'subdir/u1'})

            diffed, added, removed = cmpdir("d2", "d1")
            self.assertEqual(diffed, {'subdir/f2'})
            self.assertEqual(added, {'subdir/u1'})
            self.assertEqual(removed, {'subdir/u2'})

        # compare two exact directories, should be no diff
        with TempDir(name=True, chdir=True) as tdir:
            File("d1/subdir/u1").touch(mkdir=True)
            File("d1/subdir/f1").touch("abcd", mkdir=True)
            File("d1/subdir/f2").touch("ghi", mkdir=True)

            diffed, added, removed = cmpdir("d1", "d1")
            self.assertEqual(diffed, set())
            self.assertEqual(added, set())
            self.assertEqual(removed, set())

        # compare one dir empty
        with TempDir(name=True, chdir=True) as tdir:
            File("d1/subdir/u1").touch(mkdir=True)
            File("d1/subdir/f1").touch("abcd", mkdir=True)
            File("d1/subdir/f2").touch("ghi", mkdir=True)
            mkdirs('empty')

            diffed, added, removed = cmpdir("empty", "d1")
            self.assertEqual(diffed, set())
            self.assertEqual(added, {'subdir/u1', 'subdir/f1', 'subdir/f2'})
            self.assertEqual(removed, set())

            diffed, added, removed = cmpdir("d1", "empty")
            self.assertEqual(diffed, set())
            self.assertEqual(added, set())
            self.assertEqual(removed, {'subdir/u1', 'subdir/f1', 'subdir/f2'})

    def test_exclude_include_path(self):
        # default
        data = ['/path/f1',
                '/path/f2',
                '/path2/g1',
                '/path2/f1']
        self.assertEqual(list(exclude_include_path(data)), data)

        # exclude_dirs
        self.assertEqual(list(exclude_include_path(data, exclude_dirs=regex.compile('path2'))),
                         ['/path/f1',
                          '/path/f2'])

        # exclude_files
        self.assertEqual(list(exclude_include_path(data, exclude_files=regex.compile('^f1$'))),
                         ['/path/f2',
                          '/path2/g1'])

        # include_dirs
        self.assertEqual(list(exclude_include_path(data, include_dirs=regex.compile('path2'))),
                         ['/path2/g1',
                          '/path2/f1'])

        # include_files
        self.assertEqual(list(exclude_include_path(data, include_files=regex.compile('^f1$'))),
                         ['/path/f1',
                          '/path2/f1'])

        # combination
        data = ['/path/f1',
                '/path/f2',
                '/tmp/somefile',
                '/path2/g1',
                '/tmp2/somefile',
                '/path/f1.pyc',
                '/path2/f1']
        self.assertEqual(list(exclude_include_path(data,
                                                   include_dirs=regex.compile('^/path'),
                                                   exclude_dirs=regex.compile('^/tmp2'),
                                                   include_files=regex.compile('f1'),
                                                   exclude_files=regex.compile('f1.pyc'))),

                         ['/path/f1',
                          '/path2/f1'])

    @with_(MockVar, TempDir, '_special_infra_folder', Mock())
    def test_split_paths(self):
        self.assertEqual(split_paths('/a/b/c'), ['/a', '/a' + os.path.normpath('/b'), '/a' + os.path.normpath('/b/c')])
        with TempDir(name=True, chdir=True):
            res = split_paths('.')
            if IS_UNIX:
                self.assertEqual(len(res), 2)
                self.assertEqual(res[0], '/tmp')
            else:
                self.assertEqual(len(res), 3)
                self.assertIn('TempDir', res[1])

    def test_get_diskroot(self):
        dpath = '/nfs/png/proj/pde/tvpv'
        with MockVar(disk, 'realpath', Mock(return_value=dpath)):
            self.assertEqual(get_diskroot(dpath), '/nfs/png/proj/pde')

        dpath = '/nfs/site/home/p6vector'
        with MockVar(disk, 'realpath', Mock(return_value=dpath)):
            self.assertEqual(get_diskroot(dpath), '/nfs/site/home/p6vector')

        dpath = '/nfs/pdx/disks/nehalem.pde.356/tst/tvpv/vep2'
        with MockVar(disk, 'realpath', Mock(return_value=dpath)):
            self.assertEqual(get_diskroot(dpath), '/nfs/pdx/disks/nehalem.pde.356')

        dpath = '/tmp/user/some/path'
        with MockVar(disk, 'realpath', Mock(return_value=dpath)):
            self.assertEqual(get_diskroot(dpath), '/tmp')

        dpath = '/some/unusual/user/path'
        with MockVar(disk, 'realpath', Mock(return_value=dpath)):
            self.assertEqual(get_diskroot(dpath), '/some/unusual/user/path')

        dpath = '/some/unusual/user/path'
        with MockVar(disk, 'realpath', Mock(return_value=dpath)):
            self.assertEqual(get_diskroot(dpath, username='user'), '/some/unusual')

    def test_scandir_mtime(self):
        with TempDir(chdir=True):
            mkdirs('somedir')
            File('f1.txt').touch(mtime=1623033679)
            File('f2.txt').touch(mtime=1623033680)
            File('somedir/f3.txt').touch(mtime=1623033681)
            res = set(scandir_mtime('.'))
            self.assertEqual(res, {('./f1.txt', 1623033679.0),
                                   ('./f2.txt', 1623033680.0),
                                   ('./somedir/f3.txt', 1623033681.0)})


class RecurseChgrp_tests(TestCase):

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='flaky. manual run only', neg=False))
    def test_recurse(self):
        with TempDir(name=True) as tdir:
            # Create the dir and put several nested files in it
            os.makedirs(join(tdir, 'a', 'b'), 0o777)
            File(join(tdir, 'filea')).touch()
            File(join(tdir, 'a', 'fileb')).touch()
            File(join(tdir, 'a', 'b', 'filec')).touch()

            grpname = "gdlusers"
            andval = 0o2777
            perm = 0o2760
            oct_perm = oct(perm)
            oct_permZ = oct(0o760)
            chmodr(tdir, "%s" % oct_perm)

            r = RecurseChgrp("gdlusers", pwd.getpwuid(os.stat(tdir).st_uid).pw_name)
            r.recurse(tdir)

            self.assertEqual(oct(os.stat(tdir).st_mode & andval), oct_perm)
            self.assertEqual(oct(os.stat(join(tdir, 'a')).st_mode & andval), oct_perm)
            self.assertEqual(oct(os.stat(join(tdir, 'a', 'b')).st_mode & andval), oct_perm)

            self.assertEqual(oct(os.stat(join(tdir, 'filea')).st_mode & andval), oct_permZ)
            self.assertEqual(oct(os.stat(join(tdir, 'a', 'fileb')).st_mode & andval), oct_permZ)
            self.assertEqual(oct(os.stat(join(tdir, 'a', 'b', 'filec')).st_mode & andval), oct_permZ)

            self.assertEqual(grp.getgrgid(os.stat(tdir).st_gid).gr_name, grpname)
            self.assertEqual(grp.getgrgid(os.stat(join(tdir, 'a')).st_gid).gr_name, grpname)
            self.assertEqual(grp.getgrgid(os.stat(join(tdir, 'a', 'b')).st_gid).gr_name, grpname)
            self.assertEqual(grp.getgrgid(os.stat(join(tdir, 'filea')).st_gid).gr_name, grpname)
            self.assertEqual(grp.getgrgid(os.stat(join(tdir, 'a', 'fileb')).st_gid).gr_name, grpname)
            self.assertEqual(grp.getgrgid(os.stat(join(tdir, 'a', 'b', 'filec')).st_gid).gr_name, grpname)

    def test_recurse_raise_in_first_try(self):
        with TempDir(name=True) as tdir:
            os.makedirs(join(tdir, 'a'), 0o777)

            r = RecurseChgrp("gdlusers", pwd.getpwuid(os.stat(tdir).st_uid).pw_name)

            with patch("os.stat", side_effect=FileNotFoundError(tdir)), \
                    patch("builtins.print") as m_print:
                r.recurse(tdir)
                m_print.assert_called()
                self.assertTrue(
                    any(tdir in str(args[0]) for args, _ in m_print.call_args_list),
                    "Expected exception message to be printed in first try"
                )

    def test_recurse_raise_in_second_try(self):
        with TempDir(name=True) as tdir:
            File(join(tdir, 'filea')).touch()
            uid = os.stat(tdir).st_uid
            perm = 0o2760

            def stat_side_effect(path):
                stat_ok = SimpleNamespace(st_uid=uid, st_mode=perm)
                if path == join(tdir, 'filea'):
                    raise PermissionError("boom on file stat")
                return stat_ok

            r = RecurseChgrp("gdlusers", pwd.getpwuid(uid).pw_name)

            with patch("os.stat", side_effect=stat_side_effect), \
                    patch("builtins.print") as m_print:
                r.recurse(tdir)
                self.assertTrue(
                    any("boom on file stat" in str(args[0]) for args, _ in m_print.call_args_list),
                    "Expected exception message to be printed in second try"
                )


if __name__ == '__main__':
    unittest.main()
