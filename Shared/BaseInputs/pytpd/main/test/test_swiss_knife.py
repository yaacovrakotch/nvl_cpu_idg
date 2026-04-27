#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for swiss_knife.py
"""
from setenv_unittest import UT_DIR    # must be first import for unittests
from main.swiss_knife import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdout
from gadget.files import TempDir
from gadget.disk import mkdirs
import sys
import main.swiss_knife as swiss_knife


class ReplTest(TestCase):

    def _fake_import_module1(self, rule):

        class MyRule:   # This contains the rules
            regex = "text1"

            def replace(self, line, robj, dummy):
                line = line.replace("text", "TEXT")
                return line

        return MyRule()

    def test_repl(self):
        with TempDir(chdir=True):
            File('rule.py').touch()
            File('file1.py').touch('text1\ntext13\n')
            File('file2.py').touch('text2\n')
            File('file3.py').touch('text11\ntext33\n')

            # Preview version
            with CaptureStdoutLog() as p, \
                    MockVar(sys, 'argv', 'py file1.py file2.py file3.py -rule rule.py -prev'.split()), \
                    MockVar(OPT, 'prev', True), \
                    MockVar(SKArgs, '_import_module', self._fake_import_module1):
                pg = SKArgs().main()

            res = p.getvalue()
            expect = '''
file1.py:
From: text1
  To: TEXT1
From: text13
  To: TEXT13

file3.py:
From: text11
  To: TEXT11
'''
            self.assertTextEqual(res, expect)
            self.assertTextEqual(File("file3.py").read(), "text11\ntext33\n")   # no change

            # Actual replace
            log.info("Actual replace========")
            with MockVar(sys, 'argv', 'py file1.py file2.py file3.py -rule rule.py'.split()), \
                    MockVar(OPT, 'prev', True), \
                    MockVar(SKArgs, '_import_module', self._fake_import_module1):
                pg = SKArgs().main()

            self.assertTextEqual(File("file1.py").read(), "TEXT1\nTEXT13\n")
            self.assertTextEqual(File("file2.py").read(), "text2\n")              # unchanged file
            self.assertTextEqual(File("file3.py").read(), "TEXT11\ntext33\n")

    def _fake_import_module2(self, rule):

        class MyRule:   # This contains the rules
            regex = "text1"
            negative = "ignoreme"

            def replace(self, line, robj, dummy):
                line = line.replace("text", "TEXT")
                return line

        return MyRule()

    def test_neg_repl(self):
        with TempDir(chdir=True):
            File('rule.py').touch()
            File('file1.py').touch('text1\ntext13\ntext1 ignoreme\n')
            File('file2.py').touch('text2\nignoreme text1\n')
            File('file3.py').touch('text11\ntext33\n')

            # preview version
            with CaptureStdoutLog() as p, \
                    MockVar(sys, 'argv', 'py file1.py file2.py file3.py -rule rule.py -prev'.split()), \
                    MockVar(OPT, 'prev', True), \
                    MockVar(SKArgs, '_import_module', self._fake_import_module2):
                pg = SKArgs().main()

            expect = '''
file1.py:
From: text1
  To: TEXT1
From: text13
  To: TEXT13

file3.py:
From: text11
  To: TEXT11
'''
            self.assertTextEqual(p.getvalue(), expect)

            # real version
            with MockVar(sys, 'argv', 'py file1.py file2.py file3.py -rule rule.py'.split()), \
                    MockVar(OPT, 'prev', True), \
                    MockVar(SKArgs, '_import_module', self._fake_import_module2):
                pg = SKArgs().main()

            self.assertTextEqual(File("file1.py").read(), 'TEXT1\nTEXT13\ntext1 ignoreme\n')
            self.assertTextEqual(File("file2.py").read(), 'text2\nignoreme text1\n')
            self.assertTextEqual(File("file3.py").read(), "TEXT11\ntext33\n")

    def _fake_import_module3(self, rule):

        class MyRule:   # This contains the rules

            def replace(self, line, robj, dummy):
                line = line.replace("text", "TEXT")
                return line

        return MyRule()

    def test_missing(self):
        with TempDir(chdir=True):
            File('rule.py').touch()
            File('file1.py').touch('text1\ntext13\ntext1 ignoreme\n')

            # Preview version
            with MockVar(sys, 'argv', 'py file1.py -rule rule.py'.split()), \
                    MockVar(OPT, 'prev', True), \
                    MockVar(SKArgs, '_import_module', self._fake_import_module3):
                with self.assertRaisesRegex(Exception, 'does not have'):
                    pg = SKArgs().main()

    def _fake_import_module4(self, rule):

        class MyRule:   # This contains the rules
            regex = "text1"

            def replace(self, line, robj, dummy):
                line = line.replace("text", "text")
                return line

        return MyRule()

    def test_match_no_repl(self):
        with TempDir(chdir=True):
            File('rule.py').touch()
            orig = 'text1\ntext13\ntext1 ignoreme\n'
            File('file1.py').touch(orig)

            # preview version
            with CaptureStdoutLog() as p, \
                    MockVar(sys, 'argv', 'py file1.py -rule rule.py -prev'.split()), \
                    MockVar(OPT, 'prev', True), \
                    MockVar(SKArgs, '_import_module', self._fake_import_module4):
                pg = SKArgs().main()

            expect = '''
'''
            self.assertTextEqual(p.getvalue(), expect)

            # real version
            with MockVar(sys, 'argv', 'py file1.py -rule rule.py'.split()), \
                    MockVar(OPT, 'prev', True), \
                    MockVar(SKArgs, '_import_module', self._fake_import_module4):
                pg = SKArgs().main()

            self.assertTextEqual(File("file1.py").read(), orig)


class SKTest(TestCase):

    @with_(TempDir, chdir=True)
    def test_replace1(self):
        # case: default yml
        File('a.yml').touch('''
- name: Checkers - All BOMs
  run: python -u I:/tpvalidation/engtools/tptools/mtl/beta/gen1/main/nvl_buildtp.py none -flow

- name: More stuff
  run: python -u I:/tpvalidation/engtools/tptools/mtl/beta/gen1/main/nvl_buildtp.py
''')
        File('b.yml').touch('''
hello
''')
        cmd = "swiss_knife.py a.yml b.yml -replace I:/blah"
        with MockVar(sys, "argv", cmd.split()):
            SKArgs().main()

        expect = '''
- name: Checkers - All BOMs
  run: python -u I:/blah/main/nvl_buildtp.py none -flow

- name: More stuff
  run: python -u I:/blah/main/nvl_buildtp.py
'''
        self.assertTextEqual(File('a.yml').read(), expect)
        self.assertTextEqual(File('b.yml').read(), '\nhello\n')

    @with_(TempDir, chdir=True)
    def test_replace2(self):
        # case: any text
        File('a.yml').touch('''
jdr
jdr2
''')
        File('b.yml').touch('''
helljdro
''')
        cmd = "swiss_knife.py a.yml b.yml -replace JDR -src jdr"
        with MockVar(sys, "argv", cmd.split()):
            SKArgs().main()

        expect = '''
JDR
JDR2
'''
        self.assertTextEqual(File('a.yml').read(), expect)
        self.assertTextEqual(File('b.yml').read(), '\nhellJDRo\n')

    @with_(TempDir, chdir=True)
    def test_notebook(self):
        File('a/b/c/Open Notebook.onetoc2').touch(mkdir=True)
        File('a/b/c/a.txt').touch(mkdir=True)
        cmd = "swiss_knife.py -notebook"
        with MockVar(sys, "argv", cmd.split()):
            SKArgs().main()
        self.assertEqual(os.listdir('a/b/c'), ['a.txt'])

    def test_compile(self):
        cmd = "swiss_knife.py -compile"
        with MockVar(sys, "argv", cmd.split()):
            SKArgs().main()

    @with_(TempDir, chdir=True)
    def test_delgit(self):
        File("Modules/DRV_RESET_SXN/ab").touch(mkdir=True)
        cmd = "swiss_knife.py None -delgit"
        with MockVar(sys, "argv", cmd.split()):
            SKArgs().main()
        self.assertFalse(os.path.exists("Modules/DRV_RESET_SXN"))

    @with_(TempDir, chdir=True)
    def test_emptyout(self):
        ff = File('ab').touch('abc')
        cmd = "swiss_knife.py ab -emptyout"
        with MockVar(sys, "argv", cmd.split()):
            SKArgs().main()
        self.assertEqual(ff.read(), '')

        # Run again, check output
        mkdirs('dir1')
        cmd = "swiss_knife.py ab dir1 -emptyout"
        with MockVar(sys, "argv", cmd.split()), CaptureStdout() as p:
            SKArgs().main()
        expect = '''Skipping dir1 - directory
-i- Done. Processed 1 files
'''
        self.assertTextEqual(p.getvalue(), expect)

    @with_(TempDir, chdir=True)
    def test_escape(self):
        ff = File('ab').touch('''
a = re.compile('abc')
b = re.compile(r'abc')
c = re.findall("abc")
if re.search()
''')
        cmd = "swiss_knife.py ab -escape"
        with MockVar(sys, "argv", cmd.split()):
            SKArgs().main()
        expect = '''
a = re.compile(r'abc')
b = re.compile(r'abc')
c = re.findall(r"abc")
if re.search()
'''
        self.assertTextEqual(ff.read(), expect)

    @with_(TempDir, chdir=True)
    def test_basic(self):
        # Basic test - single file

        text = """
from gadget.strmore import curtime, zlib_compress, zlib_uncompress, to_bytes, to_str
    from gadget.strmore import curtime, zlib_compress
    # from gadget.strmore import curtime, zlib_compress
"""
        File('a.py').touch(text)

        text = """
from gadget.strmore import to_bytes, to_str
from gadget.dictmore import zlib_compress
"""
        File('mod/b.py').touch(text, mkdir=True)
        File('.git/c.py').touch(text, mkdir=True)        # skip git files
        File('mod/test/d.py').touch(text, mkdir=True)    # skip test files

        # execute
        cmd = "swiss_knife.py gadget.strmore -imp"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p, MockVar(swiss_knife, "ROOT_ENV", '.'):
                print()
                SKArgs().main()
        expect = """
./a.py                         from gadget.strmore import curtime, zlib_compress, zlib_uncompress, to_bytes, to_str
./a.py                         from gadget.strmore import curtime, zlib_compress
./mod/b.py                     from gadget.strmore import to_bytes, to_str

  2  curtime
  2  zlib_compress
  2  to_bytes
  2  to_str
  1  zlib_uncompress
"""
        self.assertTextEqual(p.getvalue(), expect)

    def test_noarg(self):
        # self.fail("oops")
        cmd = "swiss_knife.py"
        with MockVar(sys, "argv", cmd.split()), CaptureStdout() as p:
            with self.assertRaises(SystemExit):
                SKArgs().main()
            self.assertIn('-imp', p.getvalue())

    def test_envchecks(self):
        # Cannot really check correctness of "source sourceme.rc" from unittest
        # To validate, do the following in xterm:
        # case1: pytpd_path added in $PATH (first time run sourceme.rc)
        # case2: pytpd_path not added in $PATH (rerun sourceme.rc)
        # case3: $PATH not exist. run sourceme.rc

        # -checkenv
        cmd = "swiss_knife.py -checkenv"
        with MockVar(sys, "argv", cmd.split()), CaptureStdout() as p:
            SKArgs().main()
        self.assertIn('Success!', p.getvalue())

        # add path
        cmd = "swiss_knife.py -path"
        with MockVar(sys, "argv", cmd.split()), CaptureStdout() as p:
            with MockVar(os.environ, 'PATH', 'abc'):
                SKArgs().main()
        result = p.getvalue().strip().rsplit(':', 1)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1], 'abc')
        cpath = result[0]

        # No path
        with MockVar(sys, "argv", cmd.split()), CaptureStdout() as p:
            with MockVar(os.environ, 'PATH', MockVar.delete):
                SKArgs().main()
        self.assertEqual(p.getvalue().strip(), f'{cpath}:.')

        # path already existing, no change
        with MockVar(sys, "argv", cmd.split()), CaptureStdout() as p:
            with MockVar(os.environ, 'PATH', cpath):
                SKArgs().main()
        self.assertEqual(p.getvalue().strip(), cpath)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
