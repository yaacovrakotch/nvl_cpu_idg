#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for update_mtpl
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock, is_ut_option
from gadget.files import TempName, TempDir
from gadget.gizmo import MockVar, with_
from mod.tpswitch import *
from tp.testprogram import TestProgram
from gadget.errors import ErrorUser
from unittest.mock import patch
from pprint import pprint


class TestTPSwitch(TestCase):

    @with_(TempDir, chdir=True)
    def test_overwrite(self):
        File('a.txt').touch('''
TestPlan BASE;

Import Package.imp;
Import cpu.imp;
Import gcd.imp;
''')
        File('new.txt').touch('hi\nthere\n')
        TPSwitch('a.txt').overwrite_with('new.txt')

        self.assertEqual(File('a.txt').read(), 'hi\nthere\n')

        # not exist file - should write it
        TPSwitch('aa.txt').overwrite_with('new.txt')
        self.assertTrue(exists('aa.txt'))

        # not exist folder
        TPSwitch('newfolder/aa.txt').overwrite_with('new.txt')
        self.assertTrue(not exists('newfolder/aa.txt'))

    def test_overwrite_tp(self):
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', name=True) as tdir:
            File(f'{tdir}/a.txt').touch('''
TestPlan BASE;

Import Package.imp;
Import cpu.imp;
Import gcd.imp;
''')
            File(f'{tdir}/new.txt').touch('hi\nthere\n')

            TPSwitch._set_tpobj(TestProgram(f'{tdir}/POR_TP/TGLH81/EnvironmentFile.env'))
            obj = TPSwitch('a.txt')
            obj.overwrite_with('new.txt')

            self.assertEqual(File(f'{tdir}/a.txt').read(), 'hi\nthere\n')
            TPSwitch._set_tpobj(None)
            obj._check_written()    # must pass

            obj.search_replace('aaa', 'bbb')
            with self.assertRaisesRegex(ErrorUser, 'has missing'):
                obj._check_written()

    def test_main(self):
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', name=True, chdir=True) as tdir:
            tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
            TPSwitch.main(tpobj.get_bomfolder(), '.', 'unittest')   # should do nothing

            # check fname with INPUTBOM
            obj = TPSwitch('POR_TP/{INPUTBOM}/a.stpl')
            self.assertEqual(obj.fname, f'{tdir}/POR_TP/TGLH81/a.stpl')

        # Put back
        TPSwitch._set_tpobj(None)

    @with_(TempDir, chdir=True)
    def test_replace_basic(self):
        # case: two search_and_replace calls
        # case: first occurrence
        File('a.txt').touch('''
TestPlan BASE;

Import Package.imp;
Import cpu.imp;
Import gcd.imp;
''')
        obj = TPSwitch('a.txt')
        obj.search_replace('.imp', '.txt')
        obj.search_replace('Import', 'Export', n=1)
        obj.write()

        expect = '''
TestPlan BASE;

Export Package.txt;
Import cpu.txt;
Import gcd.txt;
'''
        self.assertTextEqual(File('a.txt').read(), expect)

        # not exist
        obj = TPSwitch('aa.txt')
        obj.search_replace('.imp', '.txt')
        obj.write()
        self.assertTrue(not exists('aa.txt'))

    @with_(TempDir, chdir=True)
    def test_replace_regex(self):
        # regex and marker
        File('a.txt').touch('''
TestPlan BASE;

Import Package.imp;
Import cpu.imp;
Import gcd.imp;
''')
        obj = TPSwitch('*.txt')
        obj.search_replace(r"\.i\w+", '.TXT', isregex=True)
        obj.search_replace('Import', 'Export', marker='Package')
        obj.write()

        expect = '''
TestPlan BASE;

Export Package.TXT;
Import cpu.TXT;
Import gcd.TXT;
'''
        self.assertTextEqual(File('a.txt').read(), expect)

    @with_(TempDir, chdir=True)
    def test_block_replace(self):
        File('a.txt').touch('''
CSharpTest RunCallback Test1 {
   BypassPort = -1;
 }
CSharpTest RunCallback Test2 {
   BypassPort = -1;
 }
''')
        obj = TPSwitch('*.txt')
        obj.block_replace('BypassPort = -1;', 'BypassPort = X;', name="CSharpTest.*Test3")   # none found
        obj.block_replace('BypassPort = -1;', 'BypassPort = 1;', name="CSharpTest.*Test2")
        obj.write()

        expect = '''
CSharpTest RunCallback Test1 {
   BypassPort = -1;
 }
CSharpTest RunCallback Test2 {
   BypassPort = 1;
 }
'''
        self.assertTextEqual(File('a.txt').read(), expect)

        # not found case
        obj = TPSwitch('a.txt1')
        obj.block_replace('BypassPort = 1;', 'BypassPort = 2;', name="CSharpTest.*Test2")
        obj.write()
        self.assertTextEqual(File('a.txt').read(), expect)

    @with_(TempDir, chdir=True)
    def test_process(self):
        called = []

        def fake(arg):
            called.append(arg)

        # with patch('mod.tpswitch.TPSwitch._read', fake):
        with MockVar(TPSwitch, '_read', fake):
            self.assertEqual(TPSwitch._process(''), 1)
            self.assertEqual(TPSwitch._process('None'), 2)
            self.assertEqual(TPSwitch._process('ACPY:1'), 3)

            File('TPConfig/TPSwitch/abc.py').touch(mkdir=True)
            File('Shared/TPConfig/TPSwitch/ghi.py').touch(mkdir=True)
            TPSwitch._process('/tmp')                       # abspath case
            TPSwitch._process('abc,ghi.py,notfound')        # TPConfig case
            self.assertEqual(called, ['/tmp',
                                      './TPConfig/TPSwitch/abc.py',
                                      './Shared/TPConfig/TPSwitch/ghi.py'])

    @with_(TempDir, chdir=True)
    def test_process2(self):
        called = []

        def fake(arg):
            called.append(arg)

        # with patch('mod.tpswitch.TPSwitch._read', fake):
        with MockVar(TPSwitch, '_read', fake), \
                TempDir(name=True) as tdir:
            File(f'{tdir}/TPConfig/TPSwitch/abc.py').touch(mkdir=True)
            File(f'{tdir}/Shared/TPConfig/TPSwitch/ghi.py').touch(mkdir=True)
            TPSwitch._process('abc,ghi.py,notfound', root=tdir)
            self.assertEqual(called, [f'{tdir}/TPConfig/TPSwitch/abc.py',
                                      f'{tdir}/Shared/TPConfig/TPSwitch/ghi.py'])

    @with_(TempDir, chdir=True)
    def test_read(self):
        File('switch1.py').touch('obj = TPSwitch(None)')
        File('switch2.py').touch('obj = TPSwitch2(None)')

        with MockVar(TPSwitch, '_import', Mock()):
            obj = TPSwitch('a')
            self.assertEqual(obj._read('switch1.py'), 1)
            self.assertEqual(obj._read('switch2.py'), 0)

            obj = TPSwitch2('a')
            self.assertEqual(obj._read('switch1.py'), 0)
            self.assertEqual(obj._read('switch2.py'), 1)

    @with_(TempDir, chdir=True)
    def test_copy_dir(self):
        File('somedir/abc').touch(mkdir=True)
        File('src/def').touch(mkdir=True)
        obj = TPSwitch('somedir')
        obj.copy_dir('src')
        self.assertTrue(exists('somedir/def'))
        shutil.rmtree('somedir')
        obj.copy_dir('src')
        self.assertTrue(exists('somedir/def'))

        obj = TPSwitch('somedir/def')
        obj.delete()
        self.assertFalse(exists('somedir/def'))

        # not exist
        obj = TPSwitch('somedir1')
        obj.copy_dir('src1')
        self.assertFalse(exists('somedir1'))
        obj.delete()
        self.assertFalse(exists('somedir1'))

    @with_(TempDir, chdir=True)
    def test_copy_dir_fullpath(self):
        # full path
        File('somedir/abc').touch(mkdir=True)
        File('src/def').touch(mkdir=True)
        cwd = os.getcwd()
        obj = TPSwitch('somedir')
        obj.copy_dir(f'{cwd}/src')
        self.assertTrue(exists('somedir/def'))

    @with_(TempDir, chdir=True)
    def test_get_por_tps(self):
        File('TPConfig/TPSwitch/abc.py').touch('''
POR_TP = ['AHMT_{SHORTBOM}']
obj = TPSwitch2()
''', mkdir=True)

        File('TPConfig/TPSwitch/abc2.py').touch('''
POR_TP = ['AHMTF_{SHORTBOM}']
obj = TPSwitch2()
''', mkdir=True)

        File('fail1.py').touch('''
obj = TPSwitch2()
''')
        File('sw1.py').touch('''
obj = TPSwitch()
''')

        with MockVar(TPSwitch, 'tpobj', [TestProgram(f'{UT_DIR_REPO}/SimpleNVL3')]):
            # short bom
            self.assertEqual(TPSwitch2._get_short_bom(), 'NVL_H81')

            # pass case
            self.assertEqual(list(TPSwitch2._get_por_tps('abc,abc2')),
                             [('AHMT_NVL_H81', './TPConfig/TPSwitch/abc.py'),
                              ('AHMTF_NVL_H81', './TPConfig/TPSwitch/abc2.py')])

            # fail case
            with self.assertRaisesRegex(ErrorUser, 'is found in'):
                list(TPSwitch2._get_por_tps('fail1.py'))

            # not a switch2 file
            self.assertEqual(list(TPSwitch2._get_por_tps('sw1.py')), [])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
