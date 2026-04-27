#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tp_grep.py
"""
from setenv_unittest import UT_DIR_REPO    # must be first import for unittests
from main.tp_grep import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdout, CaptureStdoutLog
from gadget.files import TempDir
import sys


class BTest(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        # Basic test - single file

        text = """
Group abc
    {
    pinx;
    pinabc;
    }
  Group ghi   {
    piny;
    pinabcd;
    pinABC;
  }
"""
        File('a.pin').touch(text)

        # execute
        cmd = "tp_grep.py pinab a.pin"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                BArgs().main()

        print(p.getvalue())
        self.assertEqual(p.getvalue().split('\n'), ['Group abc: pinabc;',
                                                    'Group ghi: pinabcd;',
                                                    ''])

        print("Test case: -i ==================")
        cmd = "tp_grep.py pinab a.pin -i"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                BArgs().main()

        print(p.getvalue())
        self.assertEqual(p.getvalue().split('\n'), ['Group abc: pinabc;',
                                                    'Group ghi: pinabcd;',
                                                    'Group ghi: pinABC;',
                                                    ''])

    @with_(TempDir, chdir=True)
    def test_oddcase(self):

        text = """
a{
bc{
 d {
 e  {
 f
   {
   pinabc;
   }
   }
   }
   }
   }
g { # }comment
h
{  # }comment
i {}
   pinabc;
}
}
pinabc {   # hi
   pinabc;
}
"""
        File('a.pin').touch(text)

        # execute
        cmd = "tp_grep.py pinab a.pin -n"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                print()
                BArgs().main()

        print(p.getvalue())
        expect = '''
#8 a->bc->d->e->f: pinabc;
#18 g->h: pinabc;
#21 : pinabc {
#22 pinabc: pinabc;
'''
        self.assertTextEqual(p.getvalue(), expect)

    @with_(TempDir, chdir=True)
    def test_twofile(self):
        # good template!
        print("Test case: two files ==================")
        text = """
ga
    {
    pinx;
    pinabc;
    }
g{
    piny;
    pinabcd;
    pinABC;
}
"""
        File('a.pin').touch(text)
        text2 = """
Pingroups
{
  Group abcqq
    {
    pinx;
    pinabcxx;
    }
}
"""
        File('b.pin').touch(text2)
        cmd = "tp_grep.py pinab a.pin b.pin"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                print()
                BArgs().main()

        print(p.getvalue())
        expect = '''
a.pin: ga: pinabc;
a.pin: g: pinabcd;
b.pin: Pingroups->Group abcqq: pinabcxx;
'''
        self.assertTextEqual(p.getvalue(), expect)

        print("Test case: no filename ==================")
        cmd = "tp_grep.py pinab a.pin b.pin -f"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                print()
                BArgs().main()

        print(p.getvalue())
        expect = '''
ga: pinabc;
g: pinabcd;
Pingroups->Group abcqq: pinabcxx;
'''
        self.assertTextEqual(p.getvalue(), expect)

    @with_(TempDir, chdir=True)
    def test_regex(self):
        # error case
        File('a.pin').touch('a\n }\n')
        cmd = "tp_grep.py pinab a.pin"
        with MockVar(sys, "argv", cmd.split()):
            obj = BArgs()
            with self.assertRaisesRegex(ErrorUser, 'is found in line#2'):
                obj.main()

        # low level regex test
        r = obj.robj_block
        self.assertEqual(r.search('abc  {').group(1), 'abc')
        self.assertEqual(r.search('ab{').group(1), 'ab')
        self.assertEqual(r.search('abc ghi {').group(1), 'abc ghi')
        self.assertEqual(r.search('{'), None)
        self.assertEqual(r.search('a{').group(1), 'a')
        self.assertEqual(r.search('abc{}'), None)

    def test_link(self):

        cmd = f"tp_grep.py IREF_TRIM_ATOM0 IREF_TRIM_ATOM1 ATOM1:ATOM0 -link {UT_DIR_REPO}/compositelink/PTH_DLVR_CXX_CLASS_P68G2.mtpl".split()
        with MockVar(sys, "argv", cmd):
            with CaptureStdout() as p:
                BArgs().main()

        print(p.getvalue())
        expect = '''Stat: IREF_TRIM_ATOM0:1018 IREF_TRIM_ATOM1:1018
Compare Result ===================
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_recurse(self):

        cmd = f"tp_grep.py IREF_TRIM_ATOM0 {UT_DIR_REPO}/compositelink/PTH_DLVR_CXX_CLASS_P68G2.mtpl -r".split()
        with MockVar(sys, "argv", cmd):
            with CaptureStdout() as p:
                BArgs().main()

        self.assertIn('DUTFlow IREF_TRIM_ATOM0', p.getvalue())

    @with_(TempDir, chdir=True)
    def test_block(self):
        # Basic test - single file

        text = """
Group abc
    {
    pinx;
    pinabc;
    }
  Group ghi   {
    piny;
    pinabcd;
    pinABC;
  }
"""
        File('a.pin').touch(text)

        # execute 1
        cmd = ["tp_grep.py", "Group abc", "a.pin", "-b"]
        with MockVar(sys, "argv", cmd):
            with CaptureStdout() as p:
                BArgs().main()

        print(p.getvalue())
        expect = '''Group abc
    {
    pinx;
    pinabc;
    }
'''
        self.assertTextEqual(p.getvalue(), expect)

        # execute 2
        cmd = ["tp_grep.py", "Group", "a.pin", "-b"]
        with MockVar(sys, "argv", cmd):
            with CaptureStdoutLog() as p:
                BArgs().main()

        print(p.getvalue())
        expect = '''Group abc
    {
    pinx;
    pinabc;
    }
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_duprule_many(self):
        root = f'{UT_DIR_REPO}/torch_mvtp/Modules'
        cmd = f"tp_grep.py {root}/TPI_GFXAGG_GXX/TPI_GFXAGG_GXX_CLASS_P68G2.usrv {root}/TPI_PRL_IXP/TPI_PRL_IXP.usrv -duprule"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                BArgs().main()
        expect = f'''count= 13 uniq=  8: {root}/TPI_GFXAGG_GXX/TPI_GFXAGG_GXX_CLASS_P68G2.usrv

Total clean files: 1
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_duprule_single(self):
        root = f'{UT_DIR_REPO}/torch_mvtp/Modules'
        cmd = f"tp_grep.py {root}/TPI_GFXAGG_GXX/TPI_GFXAGG_GXX_CLASS_P68G2.usrv -duprule"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                BArgs().main()
        expect = '''
1. CTRL_X_SCREEN_K_START_X_X_X_X_GFXAGGSETSTOPSKU_screen_tests_file:
   {
   Outcome1 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_P28G2";
   Outcome2 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_M28G1";
   Outcome3;
   }

1. CTRL_X_SCREEN_K_BEGGT_X_X_X_X_SKUCOPY_GSDS_BEGIN_screen_tests_file:
   {
   Outcome1 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_P68G2";
   Outcome2 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_M28G1";
   Outcome3;
   }

1. CTRL_X_SCREEN_K_START_X_X_X_X_GFXAGGSETTAGS_screen_tests_file:
   {
   Outcome1 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_P68G2";
   Outcome2 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_P28G2";
   Outcome3 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_M28G1";
   Outcome4;
   }

1. CTRL_GT_GFXAGG_K_INIT_X_X_X_X_SETUP_eid_config_file:
2. CTRL_GT_GFXAGG_K_INIT_X_X_X_X_SETUP_sku_config_file:
3. CTRL_GT_GFXAGG_K_START_X_X_X_X_STARTOFDEVICE_start_sku:
4. CTRL_X_SCREEN_K_ENDGT_X_X_X_X_SET_DFFCHECK_screen_tests_file:
5. CTRL_X_SCREEN_K_ENDGT_X_X_X_X_SKUCOPY_GSDS_END_screen_tests_file:
   {
   Outcome1 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_P68G2";
   Outcome2;
   }

1. CTRL_X_AUX_K_ENDGT_X_X_X_X_GTDOWNCFGCHK_bypass_global:
   {
   Outcome1 => contains(LocationSets.CHOT,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome2 => SCVars.SC_ENGID == "QP";
   Outcome3 => contains(LocationSets.FUSE,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome4 => contains(LocationSets.RCHOT,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome5;
   }

1. CTRL_X_SCREEN_K_START_X_X_X_X_GFXAGGSETSTOPSKU_bypass_global:
2. CTRL_X_SCREEN_K_START_X_X_X_X_GFXAGGSETTAGS_preinstance:
   {
   Outcome1 => contains(LocationSets.CHOT,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome2 => contains(LocationSets.RCHOT,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome3;
   }

1. CTRL_X_SCREEN_K_ENDGT_X_X_X_X_SET_DFFCHECK_bypass_global:
   {
   Outcome1 => contains(LocationSets.PBIC_DAB,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome2 => contains(LocationSets.RCH_HVM,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome3;
   }

1. CTRL_X_SCREEN_K_ENDGT_X_X_X_X_SET_DFFCHECK_screen_test_set:
   {
   Outcome1 => contains(LocationSets.RCHOT,"[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
   Outcome2;
   }

''' + f'count= 13 uniq=  8: {UT_DIR_REPO}/torch_mvtp/Modules/TPI_GFXAGG_GXX/TPI_GFXAGG_GXX_CLASS_P68G2.usrv' + \
                 '''

Total clean files: 0
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_others(self):
        # no args
        with MockVar(sys, "argv", "tp_grep.py".split()):
            with CaptureStdout() as p:
                with self.assertRaises(SystemExit):
                    BArgs().main()
                self.assertIn("Nothing to do", p.getvalue())

        # incorrect args
        with MockVar(sys, "argv", "tp_grep.py aa".split()):
            with CaptureStdout() as p:
                with self.assertRaisesRegex(ErrorUser, 'Incorrect number of arguments'):
                    BArgs().main()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
