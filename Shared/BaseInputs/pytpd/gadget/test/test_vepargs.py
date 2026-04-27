#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
vepargs_base unittests
"""
import setenv_unittest     # must be first import for unittests
from gadget.vepargs import *
from gadget.ut import TestCase, unittest
from gadget.gizmo import MockVar
from gadget.files import TempDir
from gadget.shell import fullcmdline
from gadget.strmore import to_str
from gadget.dictmore import DictDot, autodict
from unittest.mock import Mock
import gadget.vepargs as vepargs_base
from gadget.helperclass import CaptureStdoutLog, OptArgs
from os.path import join


class mocked_PSRelations1:
    """
    fake process data where the stored cmd line either matches or mismatches
    the expected process structure from PSRelations
    """

    def __init__(self, mytype='bad'):
        self.relatives = autodict()
        self.allprocs = dict()
        self.allprocs[int('100')] = dict()
        self.allprocs[int('100')]['cmd'] = 'not_CALLERBIN'
        if mytype == 'good':
            self.allprocs[int('100')]['cmd'] = basename(CALLERBIN).replace('.py', '')

    def resolve(self, arg):
        return None


class UT_Arg(ArgsBase):
    """unittest arg class"""

    def config(self):
        """Unittest config"""
        cfg = DictDot()
        cfg.list = TA_Store('Store')
        cfg.t = TA_Append('Append', alias=['tuple'])
        cfg.seq = TA_StoreTrue('Seq', alias='-sequential')
        cfg.all = TA_All('helpme')
        cfg.fullpath = TA_Store('Fullpath')
        return cfg

    def main(self):
        pass


class UT_Arg_No_Cfg(ArgsBase):
    """unittest arg class no config"""

    def config(self):
        """Unittest for a missing confg"""
        return None

    def main(self):
        pass

# --- actual tests ---


class TypeArgsTest(TestCase):
    def test_basic(self):
        # Basic stuff via StoreTrue
        aa = TA_StoreTrue("help1")
        self.assertEqual(aa.args(),
                         {'help': 'help1',
                          'action': 'store_true'})
        self.assertEqual(aa.postprocess('a1'), 'a1')
        self.assertIs(vepargs_base._TA_TypeArgs.check_isinstance(aa), aa)
        self.assertRaises(ErrorInput, vepargs_base._TA_TypeArgs.check_isinstance, list())

    def test_storetype(self):
        self.assertTrue(TA_StoreTrue("help1").is_storetype())
        self.assertFalse(TA_Store("help1").is_storetype())
        self.assertFalse(TA_Append("help1").is_storetype())

    def test_args_check(self):
        class UT(vepargs_base._TA_TypeArgs):
            pass

        ut = UT("help")
        with self.assertRaisesRegex(Exception, "must be implemented in sub-class!"):
            ut.args()

        with MockVar(UT, "args", Mock(return_value={"help": "help1"})):
            dd = ut.args()
            self.assertEqual(dd, {"help": "help1"})

    def test_final_check(self):
        # StoreTrue
        res = TA_StoreTrue("help1").final_check(True)    # pass case
        self.assertTrue(res)
        with self.assertRaisesRegex(Exception, "Cannot use choices"):
            TA_StoreTrue("help1", choices=['abc']).final_check(True)
        with self.assertRaisesRegex(Exception, "Cannot use regex"):
            TA_StoreTrue("help1", regex='25').final_check(True)

        # StoreBool
        res = TA_StoreBool("help1").final_check(True)    # pass case
        self.assertTrue(res)
        with self.assertRaisesRegex(Exception, "Cannot use choices"):
            TA_StoreBool("help1", choices=['abc']).final_check(True)
        with self.assertRaisesRegex(Exception, "Cannot use regex"):
            TA_StoreBool("help1", regex='25').final_check(True)

        # Store
        res = TA_Store("help1").final_check('abc')                       # pass case
        self.assertEqual(res, 'abc')
        res = TA_Store("help1", regex=r'\w').final_check('abc')           # pass case
        self.assertEqual(res, 'abc')
        res = TA_Store("help1", regex=r'\w').final_check(['abc', 'def'])   # pass case
        self.assertEqual(res, ['abc', 'def'])
        res = TA_Store("help1", regex=r'\w').final_check(None)            # pass case
        self.assertIs(res, None)
        with self.assertRaisesRegex(Exception, "Cannot use regex"):
            TA_Store("help1", regex=r'\w').final_check(25)
        with self.assertRaisesRegex(Exception, "Cannot use regex"):
            TA_Store("help1", regex=r'\w').final_check([25])
        with self.assertRaisesRegex(Exception, "regex option of"):
            TA_Store("help1", regex=25).final_check([25])
        with self.assertRaisesRegex(SystemExit, "is not a valid value"):
            TA_Store("help1", regex=r'\w').final_check('--')
        with self.assertRaisesRegex(SystemExit, "is not a valid value"):
            TA_Store("help1", regex=r'\w').final_check(['--'])

        # integration test
        class UT1(ArgsBase):
            def config(self):
                """Unittest config"""
                cfg = DictDot()
                cfg.st1 = TA_Store('Store', regex='A')
                cfg.st2 = TA_Store('Store')
                cfg.st3 = TA_AppendSC('Store', regex='A')
                cfg.pl = TA_Tack('Store')
                cfg.q = TA_Tack('Store')
                cfg.verbosity_level = TA_StoreTrue('bool')
                return cfg

            def main(self):
                pass

        # pass case 1
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -st2 BC".split()):
            UT1()
            self.assertEqual(OPT, {'st1': None,
                                   'st2': 'BC',
                                   'st3': [],
                                   'q': [],
                                   'pl': [],
                                   'devdebug': False,
                                   'verbosity_level': False,
                                   'nobulletin': False})

        # pass case 2
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -st1 BAB -st3 CAC,DAD".split()):
            UT1()
            self.assertEqual(OPT, {'st1': 'BAB',
                                   'st2': None,
                                   'st3': ['CAC', 'DAD'],
                                   'q': [],
                                   'pl': [],
                                   'devdebug': False,
                                   'verbosity_level': False,
                                   'nobulletin': False})
        OPT.clear()
        # fail case
        with MockVar(sys, "argv", "/myscript -st1 BAB -st3 CC,DAD".split()):
            with self.assertRaisesRegex(SystemExit, r"\[-st3 CC\].* is not a valid"):
                UT1()
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -st1 BAB -st3 DAD -q asdf".split()):
            with self.assertRaisesRegex(SystemExit, "Error: No end token -- detected for 'q'"):
                UT1()
        OPT.clear()
        # Testing -q variables
        with MockVar(sys, "argv", "/myscript -pl bbb -- -q qqq -- -st3 CAC,DAD -q all -q- -pl all -pl- -q BAB=foo BAC=bar BAD!=foo   BAE>foo BAF<=foo testid path -- -st2 blah".split()):
            original = fullcmdline()
            UT1()
            self.assertEqual(OPT, {'q': ['qqq', 'all', 'BAB=foo', 'BAC=bar', 'BAD!=foo', 'BAE>foo', 'BAF<=foo', 'testid', 'path'],
                                   'st1': None,
                                   'pl': ['bbb', 'all'],
                                   'st2': "blah",
                                   'st3': ['CAC', 'DAD'],
                                   'devdebug': False,
                                   'verbosity_level': False,
                                   'nobulletin': False})
            self.assertEqual(original, fullcmdline())    # sys.arg must be unchanged
        OPT.clear()

    def test_tack(self):

        # setup
        class UT2(ArgsBase):
            def config(self):
                # ""Unittest config""
                cfg = DictDot()
                cfg.all = TA_All('positional args')
                cfg.u = TA_Tack('Tacky')
                return cfg

            def main(self):
                pass

        # alias check
        with MockVar(sys, "argv", "/myscript tu 123 -u abc --".split()):
            original = fullcmdline()
            UT2()
            self.assertDictEqual(OPT, {'all': ['tu', '123'],
                                       'u': ['abc'],
                                       'devdebug': False,
                                       'nobulletin': False,
                                       'verbosity_level': None})
            self.assertEqual(original, fullcmdline())    # sys.arg must be unchanged

        # in the middle
        with MockVar(sys, "argv", "/myscript tu -u abc def -u- 123".split()):
            original = fullcmdline()
            UT2()
            self.assertDictEqual(OPT, {'all': ['tu', '123'],
                                       'u': ['abc', 'def'],
                                       'devdebug': False,
                                       'nobulletin': False,
                                       'verbosity_level': None})
            self.assertEqual(original, fullcmdline())    # sys.arg must be unchanged

        # no tack
        with MockVar(sys, "argv", "/myscript tu 123".split()):
            original = fullcmdline()
            UT2()
            self.assertDictEqual(OPT, {'all': ['tu', '123'],
                                       'u': [],
                                       'devdebug': False,
                                       'nobulletin': False,
                                       'verbosity_level': None})
            self.assertEqual(original, fullcmdline())    # sys.arg must be unchanged

        # help on tack - bug since it is not showing the help
        with MockVar(sys, "argv", "/myscript -h tu -u abc def -u- 123".split()),\
                CaptureStdoutLog() as p,\
                self.assertRaises(SystemExit):
            UT2()
        self.assertDictEqual(OPT, {})
        self.assertIn('Tacky', p.getvalue())

    def test_to_string(self):
        self.assertEqual(TA_Store.to_string("abc", "arg"), "-arg abc")
        self.assertEqual(TA_Append.to_string(["abc", "def"], "arg"), "-arg abc -arg def")
        self.assertEqual(TA_All.to_string(["abc", "def"], "arg"), "abc def")
        self.assertEqual(TA_AllOne.to_string("abc", "arg"), "abc")
        self.assertEqual(TA_StoreTrue.to_string(True, "arg"), "-arg")
        self.assertEqual(TA_StoreTrue.to_string(False, "arg"), "")

    def test_results(self):
        self.assertEqual(TA_Store("help2").args(),
                         {'help': 'help2',
                          'action': 'store',
                          'choices': None})
        self.assertEqual(TA_Store("help2", "mv").args(),
                         {'help': 'help2',
                          'action': 'store',
                          'metavar': 'mv',
                          'choices': None})

        self.assertEqual(TA_Append("help3").args(),
                         {'help': 'help3',
                          'action': 'append',
                          'choices': None})

    def test_default(self):
        aa = TA_StoreTrue("help1", default=12)
        self.assertEqual(aa.args(),
                         {'help': 'help1',
                          'action': 'store_true',
                          'default': 12})

        aa = TA_Store("help1", default=12)
        self.assertEqual(aa.args(),
                         {'help': 'help1',
                          'action': 'store',
                          'default': 12,
                          'choices': None})

    def test_AppendSC(self):
        aa = TA_AppendSC("help1")
        self.assertEqual(aa.postprocess(["abc,def ghi", 'klm']),
                         "abc def ghi klm".split())
        self.assertEqual(aa.postprocess(["abc", 'klm']),
                         "abc klm".split())
        self.assertEqual(aa.postprocess([" a b c,d,e f ", ' g ', ',h,, ']),
                         "a b c d e f g h".split())
        self.assertEqual(aa.postprocess([" a b c,d; e f ", ' g ', ',h,, ']),
                         "a b c d e f g h".split())
        self.assertEqual(aa.postprocess([" a b c,d;e f ", ' g ', ',h;, ']),
                         "a b c d e f g h".split())

    def test_AppendPat(self):
        aa = TA_AppendPat("help1")
        self.assertEqual(aa.postprocess(["/path/path/abc.pobj",
                                         "abc",
                                         "def.pobj"]),
                         "abc abc def".split())

    def test_AppendPatSC(self):
        aa = TA_AppendPatSC("help1")
        self.assertEqual(aa.postprocess(["/path/abc.pobj,/path/path/def.pobj,/path/path/path/ghi.pat",
                                         "qwe,rty,uio",
                                         "xyz.pobj mnb.pobj "]),
                         "abc def ghi qwe rty uio xyz mnb".split())

    def test_KeyVal(self):
        # Simple cases ===================================
        aa = TA_KeyVal("help1")
        self.assertEqual(aa.postprocess(["Mft=00", "Mcache=21=22"]),
                         {'mft': '00',
                          'mcache': '21=22'})
        self.assertEqual(aa.empty(), {})

        self.assertRaisesRegex(SystemExit, "must be.*key.*value", aa.postprocess, ["Mft"])
        self.assertEqual(TA_KeyVal.to_string({'Mft': '000.001', 'Mcache': '010.011'}, 'serev'),
                         '-serev Mcache=010.011 -serev Mft=000.001')

        # validkeys - pass case
        aa = TA_KeyVal("help1", validkeys=['Mft', 'Mcache'])
        self.assertEqual(aa.postprocess(["Mft=00", "Mcache=21=22"]),
                         {'mft': '00',
                          'mcache': '21=22'})

        # validkeys - fail case
        aa = TA_KeyVal("help1", validkeys=['Mft'])
        self.assertRaisesRegex(SystemExit, "is not a valid key",
                               aa.postprocess, ["Mft=00", "Mcache=21=22"])

        # multi-value cases ==============================
        aa = TA_KeyVal("help1")
        self.assertEqual(aa.postprocess(["Mft=01;Mcache='21 23'"]),
                         {'mft': '01',
                          'mcache': '21 23'})
        self.assertRaisesRegex(SystemExit, "must be.*key.*value",
                               aa.postprocess, ["Mft=00;Mcache"])

        # special char case
        self.assertEqual(TA_KeyVal.to_string({'Mft': '0 1', 'Mcache': "a='1'"}, 'serev'),
                         '-serev Mcache="a=\'1\'" -serev Mft=\'0 1\'')

    def test_KeyValSERev(self):
        aa = TA_KeyValSERev("help1")
        self.assertEqual(aa.postprocess(["Mft=00", "Mcache=21", "latest", "skip"]),
                         {'mft': '00',
                          'latest': '00',
                          'skip': '00',
                          'mcache': '21'})

        self.assertRaisesRegex(SystemExit, "must be.*module.*serev", aa.postprocess, ["Mft"])
        self.assertRaisesRegex(SystemExit, "must be a two chars", aa.postprocess, ["Mft=rrx"])

        aa = TA_KeyValSERev("help1")
        self.assertEqual(aa.postprocess(["remove_default", "skip"]), {'remove_default': '00', 'skip': '00'})
        self.assertEqual(aa.postprocess(["remove_default"]), {'remove_default': '00'})
        self.assertEqual(aa.postprocess(["skip", "remove_default"]), {'remove_default': '00', 'skip': '00'})
        self.assertEqual(aa.postprocess(["skip", "remove_default", "latest"]), {'remove_default': '00', 'skip': '00', 'latest': '00'})

    def test_KeyVal_CaseSensitive(self):
        # aa = TA_KeyVal_CaseSensitive("help1")
        # self.assertEqual(aa.postprocess(["cmtsim.a.b='/a/b'", "replay.ENABLE=1"]),
        #                  {'cmtsim.a.b': "'/a/b'", 'replay.ENABLE':'1'})
        #
        # self.assertRaisesRegex(SystemExit, "must be.*key.*value", aa.postprocess, ["Mft"])

        # Simple cases ===================================
        aa = TA_KeyVal_CaseSensitive("help1")
        self.assertEqual(aa.postprocess(["cmtsim.a.b='/a/b'", "replay.ENABLE=1"]),
                         {'cmtsim.a.b': "'/a/b'", 'replay.ENABLE': '1'})
        self.assertEqual(aa.empty(), {})

        self.assertRaisesRegex(SystemExit, "must be.*key.*value", aa.postprocess, ["Mft"])
        self.assertEqual(TA_KeyVal_CaseSensitive.to_string({'Mft': '000.001', 'Mcache': '010.011'}, 'serev'),
                         '-serev Mcache=010.011 -serev Mft=000.001')

        # validkeys - pass case
        aa = TA_KeyVal_CaseSensitive("help1", validkeys=['Mft', 'Mcache'])
        self.assertEqual(aa.postprocess(["Mft=00", "Mcache=21=22"]),
                         {'Mft': '00',
                          'Mcache': '21=22'})

        # validkeys - fail case
        aa = TA_KeyVal_CaseSensitive("help1", validkeys=['Mft'])
        self.assertRaisesRegex(SystemExit, "is not a valid key",
                               aa.postprocess, ["Mft=00", "Mcache=21=22"])

        # multi-value cases ==============================
        aa = TA_KeyVal_CaseSensitive("help1")
        self.assertEqual(aa.postprocess(["Mft=01;Mcache='21 23'"]),
                         {'Mft': '01',
                          'Mcache': '21 23'})
        self.assertRaisesRegex(SystemExit, "must be.*key.*value",
                               aa.postprocess, ["Mft=00;Mcache"])

    def test_StoreBool(self):

        # Create the class first
        class UT1(ArgsBase):
            def config(self):
                """Unittest config"""
                cfg = DictDot()
                cfg.defTrue = TA_StoreBool('Store', default=True)
                cfg.defNone = TA_StoreBool('Store')
                cfg.defFalse = TA_StoreBool('Store', default=False)
                cfg.a = TA_StoreBool('Store')
                cfg.b = TA_StoreBool('Store')
                cfg.c = TA_StoreBool('Store')
                return cfg

            def main(self):
                pass

        # basic check
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -a YES -b falsE -c 1".split()):
            UT1()
            self.assertEqual(OPT, {'defTrue': True,
                                   'defFalse': False,
                                   'defNone': False,
                                   'a': True,
                                   'b': False,
                                   'c': True,
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})
        # clear
        UT1.set_empty_opt()
        self.assertEqual(OPT, {'a': False,
                               'c': False,
                               'b': False,
                               'defNone': False,
                               'defTrue': False,
                               'defFalse': False})

        # invalid case
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -a oops".split()):
            with self.assertRaisesRegex(SystemExit, "is not a valid boolean"):
                UT1()

        # invalid default value
        class UT2(UT1):
            def config(self):
                """Unittest config"""
                cfg = DictDot()
                cfg.defTrue = TA_StoreBool('Store', default=1)
                return cfg
        OPT.clear()
        with MockVar(sys, "argv", "/myscript".split()):
            with self.assertRaisesRegex(SystemExit, "is not a valid boolean"):
                UT2()

    def test_StoreNumber(self):
        aa = TA_StoreNumber("help1")
        self.assertEqual(aa.postprocess("23"), 23)
        self.assertEqual(aa.postprocess("-23"), -23)
        self.assertRaises(SystemExit, aa.postprocess, "23a")

        aa = TA_AppendNumberSC("help1")
        self.assertEqual(aa.postprocess(["1,2", "3 4"]), [1, 2, 3, 4])
        self.assertRaises(SystemExit, aa.postprocess, ["23a"])

    def test_StoreFloat(self):
        aa = TA_StoreFloat("help1")
        self.assertEqual(aa.postprocess("23"), 23.0)
        self.assertEqual(aa.postprocess("-23.1"), -23.1)
        self.assertRaises(SystemExit, aa.postprocess, "23a")

#        aa = TA_AppendFloatSC("help1")
#        self.assertEqual(aa.postprocess(["1.0,2","3.1 4"]), [1.0,2.0,3.1,4.0])
#        self.assertRaises(SystemExit, aa.postprocess, ["23a"])

    def test_StoreFile(self):
        with TempDir(chdir=True, name=True) as tdir:
            f1 = File(join(tdir, "f1")).touch()
            aa = TA_StoreFile("help1")
            self.assertEqual(aa.postprocess("f1"), f1.get_name())
            self.assertRaisesRegex(SystemExit, 'does not exist', aa.postprocess, f1.get_name() + "x")
            self.assertRaisesRegex(SystemExit, 'is a directory', aa.postprocess, tdir)

            f1.compress(f1.gz)
            self.assertEqual(aa.postprocess("f1"), f1.get_name())
            self.assertEqual(aa.postprocess("f1.gz"), f1.get_name())

    def test_StoreDir(self):
        with TempDir(chdir=True, name=True) as tdir:
            aa = TA_StoreDir("help1")
            f1 = File(join(tdir, "f1")).touch()
            self.assertEqual(aa.postprocess(tdir), tdir)
            self.assertEqual(aa.postprocess("."), tdir)
            self.assertRaises(SystemExit, aa.postprocess, f1.get_name())      # is a file
            self.assertRaises(SystemExit, aa.postprocess, f1.get_name() + "x")  # not exist

    def test_StoreFileOrDir(self):
        with TempDir(chdir=True, name=True) as tdir:
            f1 = File(join(tdir, "f1")).touch()
            aa = TA_StoreFileOrDir("help1")
            self.assertEqual(aa.postprocess("f1"), f1.get_name())
            self.assertRaisesRegex(SystemExit, 'file or dir must exist', aa.postprocess, f1.get_name() + 'x')
            self.assertRaisesRegex(SystemExit, 'file or dir must exist', aa.postprocess, tdir + 'x')

            f1.compress(f1.gz)
            self.assertEqual(aa.postprocess("f1"), f1.get_name())
            self.assertEqual(aa.postprocess("f1.gz"), f1.get_name())

    def test_FileOrDirAppendSC(self):
        with TempDir(chdir=True, name=True) as tdir:
            f1 = File(join(tdir, "f1")).touch()
            aa = TA_FileOrDirAppendSC("help1")
            self.assertEqual(aa.postprocess(["f1"]), [f1.get_name()])
            self.assertEqual(aa.postprocess(["f1", "f1"]), [f1.get_name()])  # get the unique
            self.assertRaisesRegex(SystemExit, 'file or dir must exist', aa.postprocess, [f1.get_name() + 'x'])
            self.assertRaisesRegex(SystemExit, 'file or dir must exist', aa.postprocess, [tdir + 'x'])

            f1.compress(f1.gz)
            self.assertEqual(aa.postprocess(["f1", 'f1.gz']), [f1.get_name()])
            self.assertEqual(aa.postprocess(["f1.gz"]), [f1.get_name()])
            self.assertEqual(aa.postprocess([tdir, "f*"]), [tdir, f1.get_name()])

    def test_FileAppendSC(self):
        with TempDir(chdir=True, name=True) as tdir:
            aa = TA_FileAppendSC("help1")
            f1 = File(join(tdir, "f1")).touch()
            f2 = File(join(tdir, "f2")).touch()
            self.assertEqual(aa.postprocess(["f1,f2"]), [f1.get_name(),
                                                         f2.get_name()])
            self.assertEqual(aa.postprocess(["f1", "f1,f2"]), [f1.get_name(),
                                                               f2.get_name()])
            self.assertEqual(aa.postprocess(["f2", "f1,f2"]), [f2.get_name(),
                                                               f1.get_name()])
            self.assertItemsEqual(aa.postprocess(["*"]), [f1.get_name(),
                                                          f2.get_name()])
            self.assertItemsEqual(aa.postprocess(["f?"]), [f1.get_name(),
                                                           f2.get_name()])
            self.assertItemsEqual(aa.postprocess(["%s/f?" % tdir]), [f1.get_name(),
                                                                     f2.get_name()])
            self.assertItemsEqual(aa.postprocess(["f?", "f*,f2"]), [f1.get_name(),
                                                                    f2.get_name()])

            # file not exist
            self.assertRaises(SystemExit, aa.postprocess, ["file_not_exist", "f1"])

            # directory not allowed
            self.assertRaises(SystemExit, aa.postprocess, ["/tmp"])

    def test_DirAppendSC(self):
        with TempDir(chdir=True, name=True) as tdir:
            aa = TA_DirAppendSC("help1")
            f1 = File(join(tdir, "f1")).touch()
            self.assertEqual(aa.postprocess([tdir + "," + tdir]), [tdir, tdir])
            self.assertEqual(aa.postprocess([tdir, tdir + "," + tdir]), [tdir, tdir, tdir])
            self.assertRaises(SystemExit, aa.postprocess, [tdir, "f1"])
            self.assertRaises(SystemExit, aa.postprocess, [tdir + "surenotexist"])

    def test_AllOne(self):
        aa = TA_AllOne("help1")
        self.assertEqual(aa.args(), {'nargs': '?', 'help': 'help1'})
        self.assertEqual(aa.postprocess('abc'), 'abc')   # do nothing

        aa = TA_AllOne("help1", metavar='m1')
        self.assertEqual(aa.args(), {'nargs': '?', 'help': 'help1', 'metavar': 'm1'})


class ArgsTest(TestCase):

    def test_unconfigured_none(self):
        # Spec: unconfigured OPT should return None. Some code in expects that it is None.
        OPT.clear()
        with MockVar(sys, "argv", "/myscript 55".split()):
            UT_Arg()
            self.assertIs(OPT.somenonexist, None)   # DO NOT change or remove this test!
            self.assertFalse('somenonexist' in OPT)

    def test_alias(self):
        class UT1(ArgsBase):
            def config(self):
                """Unittest config"""
                cfg = DictDot()
                cfg.tuple = TA_Append('Store', alias=['t', '-tr'])
                cfg.trace = TA_Store('Append', alias='moretrace')
                return cfg

            def main(self):
                pass

        # alias
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -tuple 10 -t 11 -tr 12 -moretrace abc".split()):
            UT1()
            self.assertEqual(OPT, {'tuple': ["10", "11", "12"],
                                   'trace': 'abc',
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})

    def test_TA_OBJ(self):
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -tuple 22 -t 23 -sequential".split()):
            UT_Arg()
            self.assertEqual(OPT, {'fullpath': None,
                                   'list': None,
                                   'all': [],
                                   'seq': True,
                                   't': ['22', '23'],
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})

            self.assertEqual(OPT.TAOBJ_get('list').name, 'list')

    def test_required(self):
        # Required is missing
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -list 21".split()):
            self.assertRaises(SystemExit, UT_Arg, ["t", "list", "fullpath"],
                              "some txt", 'fullpath'.split(), group=None)

        # Required - pass case1
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -t 21".split()):
            UT_Arg(["t", "list", "fullpath"], "some txt", 't list fullpath'.split(), group=None)

        # Required - pass case2
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -list 21".split()):
            UT_Arg(["t", "list", "fullpath"], "some txt", 't list fullpath'.split(), group=None)

        # Required but not specified in list
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -list 21".split()):
            self.assertRaises(ErrorInput, UT_Arg, ["t", "list"],
                              "some txt", 'fullpath'.split(), group=None)

    def test_required2(self):
        class UT_Arg1(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.list = TA_Store('Store')
                cfg.t = TA_Append('Append')
                cfg.seq = TA_StoreTrue('Seq')
                cfg.all = TA_All('helpme', metavar="rr")
                return cfg

            def main(self):
                pass

        OPT.clear()

        # pass case
        with MockVar(sys, "argv", "/myscript a1".split()):
            UT_Arg1("t list seq all".split(), "some txt", ["all"], group=None)

        # fail case
        with MockVar(sys, "argv", "/myscript".split()):
            self.assertRaises(SystemExit, UT_Arg1, "t list seq all".split(),
                              "some txt", ["all"], group=None)

        # bool is required - must fail
        with MockVar(sys, "argv", "/myscript".split()):
            self.assertRaises(SystemExit, UT_Arg1, "t list seq all".split(),
                              "some txt", ["all", "seq"], group=None)

        # bool is required - pass case
        with MockVar(sys, "argv", "/myscript -seq".split()):
            UT_Arg1("t list seq all".split(), "some txt", ["all", "seq"], group=None)

    def test_required_property(self):
        # one group, two entries
        class UT_Arg1(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.typ = TA_Store('Store', required="grp1")
                cfg.gold = TA_Store('Store', required="grp1")
                cfg.more = TA_Store('Store')
                return cfg

            def main(self):
                pass

        OPT.clear()
        with MockVar(sys, "argv", "/myscript -more abc".split()):
            with self.assertRaisesRegex(SystemExit, "is required"):
                UT_Arg1()
        with MockVar(sys, "argv", "/myscript -typ abc -more abc".split()):
            UT_Arg1()
        with MockVar(sys, "argv", "/myscript -gold abc -more abc".split()):
            UT_Arg1()
        with MockVar(sys, "argv", "/myscript -gold abc -typ def -more ghi".split()):
            UT_Arg1()

        # two groups
        class UT_Arg2(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.typ = TA_Store('Store', required="grp1")
                cfg.gold = TA_Store('Store', required="grp2")
                cfg.more = TA_Store('Store')
                return cfg

            def main(self):
                pass

        OPT.clear()
        with MockVar(sys, "argv", "/myscript -typ abc -more a".split()):
            with self.assertRaisesRegex(SystemExit, "is required"):
                UT_Arg2()
        with MockVar(sys, "argv", "/myscript -gold abc -more a".split()):
            with self.assertRaisesRegex(SystemExit, "is required"):
                UT_Arg2()
        with MockVar(sys, "argv", "/myscript -gold abc -typ abc".split()):
            UT_Arg2()

    def test_mutex(self):
        # fail case
        class UT_Arg1(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.typ = TA_StoreTrue('Store', mutex="grp1")
                cfg.gold = TA_StoreTrue('Store', mutex="grp1")
                return cfg

            def main(self):
                pass

        OPT.clear()
        with MockVar(sys, "argv", "/myscript -typ -gold".split()):
            with self.assertRaisesRegex(SystemExit, "is not allowed with"):
                UT_Arg1()
        with MockVar(sys, "argv", "/myscript -typ".split()):
            UT_Arg1()
            self.assertTrue(OPT.typ)
            self.assertFalse(OPT.gold)

        # pass case 1
        class UT_Arg2(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.typ = TA_StoreTrue('Store', mutex="grp1")
                cfg.gold = TA_StoreTrue('Store', mutex="grp2")
                return cfg

            def main(self):
                pass

        OPT.clear()
        with MockVar(sys, "argv", "/myscript -typ -gold".split()):
            UT_Arg2()

        # pass case 2
        class UT_Arg3(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.typ = TA_StoreTrue('Store')
                cfg.gold = TA_StoreTrue('Store')
                return cfg

            def main(self):
                pass

        OPT.clear()
        with MockVar(sys, "argv", "/myscript -typ -gold".split()):
            UT_Arg3()
            self.assertTrue(OPT.typ)
            self.assertTrue(OPT.gold)

    def test_postprocessing(self):
        class Store2(TA_Store):
            def postprocess(self, obj):
                return "a" + obj

        class Append2(TA_Append):
            def postprocess(self, obj):
                obj.append("99")
                return obj

        class UT_Arg1(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.list = Store2('Store')
                cfg.t = Append2('Append')
                return cfg

            def main(self):
                pass

        # with postprocess
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -list 21 -t a1".split()):
            UT_Arg1("t list".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'list': "a21", 't': ['a1', '99']})

        # argument not specified
        OPT.clear()
        with MockVar(sys, "argv", "/myscript".split()):
            UT_Arg1("t list".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'list': None, 't': []})

    def test_alltypes(self):
        class UT_Arg1(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.list = TA_Store('Store', metavar="mv1")
                cfg.t = TA_Append('Append', metavar="mv2")
                cfg.seq = TA_StoreTrue('Seq')
                cfg.all = TA_All('helpme', metavar="rr")
                return cfg

            def main(self):
                pass

        # No args
        OPT.clear()
        with MockVar(sys, "argv", "/myscript".split()):
            ut = UT_Arg1("t list seq all".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'all': [], 'list': None, 't': [], 'seq': False})
            self.assertTrue(ut.is_upload())

        # With args
        OPT.clear()
        with MockVar(sys, "argv", "/myscript abc def -seq -t a1 -t a2 -list f2".split()):
            UT_Arg1("t list seq all".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'all': ['abc', 'def'],
                                   'list': "f2",
                                   't': ["a1", "a2"],
                                   'seq': True})

    def test_alltypes2(self):
        # without metavar
        OPT.clear()
        with MockVar(sys, "argv", "/myscript".split()):
            UT_Arg("t all".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'all': [], 't': []})

        OPT.clear()
        with MockVar(sys, "argv", "/myscript abc def -t a1".split()):
            UT_Arg("t all".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'all': ['abc', 'def'],
                                   't': ["a1"]})

    def test_alltypes3(self):
        class UT_Arg1(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.list = TA_Store('Store', metavar="mv1")
                cfg.t = TA_Append('Append', metavar="mv2")
                cfg.seq = TA_StoreTrue('Seq')
                cfg.all = TA_AllOne('helpme', metavar="rr")
                return cfg

            def main(self):
                pass

        # No args
        OPT.clear()
        with MockVar(sys, "argv", "/myscript".split()):
            UT_Arg1("t list seq all".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'all': None, 'list': None, 't': [], 'seq': False})

        # With args
        OPT.clear()
        with MockVar(sys, "argv", "/myscript abc -seq -t a1 -t a2 -list f2".split()):
            UT_Arg1("t list seq all".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'all': 'abc',
                                   'list': "f2",
                                   't': ["a1", "a2"],
                                   'seq': True})

    def test_order(self):
        with MockVar(sys, "argv", "/myscript".split()):
            # test one order
            class UT_Arg1(ArgsBase):
                def config(self):
                    cfg = DictDot()
                    cfg.list = TA_Store('Store')
                    cfg.t = TA_Append('Append')
                    cfg.seq = TA_StoreTrue('Seq', group="tool1")
                    cfg.all = TA_All('helpme')
                    return cfg

                def main(self):
                    pass

            aa = UT_Arg1("t list seq all".split(), "some txt", [], group=None)
            self.assertItemsEqual(aa.execute(None, [], "default"), ['list', 't', 'all', 'nobulletin', 'devdebug', 'verbosity_level'])

            # Test another order
            class UT_Arg2(ArgsBase):
                def config(self):
                    cfg = DictDot()
                    cfg.seq = TA_StoreTrue('Seq', group="tool1")
                    cfg.list = TA_Store('Store', group="tool1")
                    cfg.t = TA_Append('Append', group="tool1")
                    cfg.all = TA_All('helpme', metavar="rr")
                    return cfg

                def main(self):
                    pass

            aa = UT_Arg2("t list seq all".split(), "some txt", [], group=None)
            self.assertEqual(aa.execute(None, [], "tool1"), ['seq', 'list', 't'])

    def test_set_empty_opt(self):
        # default
        OPT.clear()
        UT_Arg.set_empty_opt("t list".split())
        self.assertEqual(OPT, {'t': [], 'list': None})

        # All values
        OPT.clear()
        UT_Arg.set_empty_opt()
        self.assertEqual(OPT, {'fullpath': None,
                               'list': None,
                               'all': [],
                               'seq': False,
                               't': []})

        # Invalid value
        self.assertRaises(ErrorInput, UT_Arg.set_empty_opt, ["notfound"])

    def test_empty_cfg(self):
        self.assertRaises(ErrorInput, UT_Arg_No_Cfg)  # verify empty config raises error

    def test_empty_cfg2(self):
        class UTArg1(ArgsBase):
            pass

        with self.assertRaisesRegex(Exception, "must be implemented in sub-class!"):
            ut = UTArg1()
            ut.config()

        class UTArg2(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.list = TA_Store('Store')
                return cfg

        with self.assertRaisesRegex(Exception, "must be implemented in sub-class!"):
            ut = UTArg2(execute=False)
            ut.main()

    def test_call_methods(self):
        class UT1(UT_Arg):
            def do_list(self):
                return "i am list"

            def do_t(self):
                return "i am t"

        with MockVar(sys, "argv", "a.py -list a".split()):
            aa = UT1()
            self.assertEqual(aa.call_methods("list t".split()), "i am list")

        with MockVar(sys, "argv", "a.py -t 22".split()):
            aa = UT1()
            self.assertEqual(aa.call_methods("list t".split()), "i am t")

        # This will display help
        with MockVar(sys, "argv", "a.py -seq".split()):
            aa = UT1()
            with self.assertRaises(SystemExit):
                aa.call_methods("list t".split())

    def test_check_unicode(self):
        # fail case - The goal of this case is to gracefully handle the case where a user copies/pastes from Windows
        # and the characters are not properly recognized.
        data = to_str(b'-list \xe2\x80\x98a b v\xe2\x80\x99')
        with MockVar(sys, 'argv', data):
            aa = UT_Arg(execute=False)
            self.assertRaisesRegex(ErrorUser, 'contain special characters', aa.check_unicode)

        # Fail case - true native Python3 unicode also is detected.
        data = "here is your checkmark: " + '\u2713'
        with MockVar(sys, 'argv', data):
            aa = UT_Arg(execute=False)
            self.assertRaisesRegex(ErrorUser, 'contain special characters', aa.check_unicode)

        # pass case
        with MockVar(sys, 'argv', 's.py -list abc -new 25'.split()):
            aa = UT_Arg(execute=False)
            aa.check_unicode()

    def test_print_help(self):
        with MockVar(sys, "argv", ["script.py"]):
            argobj = UT_Arg()
        with self.assertRaises(SystemExit):
            argobj.print_help()


class DangerArgTest(TestCase):
    """
    For some reason, in Python3 these test cause ArgsTest.test_get_tracepat_from_args to fail if they are executed
    prior to this other test.  It is not clear why, but it appears that the underlying argparse() module is somehow
    causing this when a SystemExit is raised and caught by the unit tests.  This doesn't really make sense, so these
    tests are being moved for now to their own class so they don't cause problems.  To see the error, simply copy
    the test_choices testcase below back into the ArgsTest class.
    """

    def test_arg_processing(self):
        # default
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -t 21".split()):
            UT_Arg()
            self.assertEqual(OPT, {'fullpath': None,
                                   'list': None,
                                   'all': [],
                                   'seq': False,
                                   't': ['21'],
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})

        # Valid non-list
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -t 21".split()):
            UT_Arg("t list".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'list': None, 't': ['21']})

        # Valid list
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -list 21".split()):
            UT_Arg("t list".split(), "some txt", [], group=None)
            self.assertEqual(OPT, {'list': '21', 't': []})

        # Invalid Command
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -list 21".split()):
            self.assertRaises(SystemExit, UT_Arg,
                              ["t"], "some txt", [], group=None)

        # Invalid Option provided
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -t 21".split()):
            self.assertRaises(ErrorCockpit, UT_Arg,
                              "t surenotexist".split(), "some txt", [], group=None)

        # Both list and group is provided
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -t 21".split()):
            self.assertRaises(ErrorInput, UT_Arg,
                              "t list".split(), "some txt", [])

        # normal run, positional args
        OPT.clear()
        with MockVar(sys, "argv", "/myscript 55".split()):
            UT_Arg()
            self.assertEqual(OPT, {'fullpath': None,
                                   'list': None,
                                   'all': ['55'],
                                   'seq': False,
                                   't': [],
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})     # This is Append type

        # alias
        OPT.clear()
        with MockVar(sys, "argv", "/myscript -tuple 22 -sequential".split()):
            UT_Arg()
            self.assertEqual(OPT, {'fullpath': None,
                                   'list': None,
                                   'all': [],
                                   'seq': True,
                                   't': ['22'],
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})

        # verbosity_level
        OPT.clear()
        with MockVar(sys, "argv", "/myscript 55 -verbosity_level INFO".split()):
            UT_Arg()
            self.assertEqual(OPT, {'fullpath': None,
                                   'list': None,
                                   'all': ['55'],
                                   'seq': False,
                                   't': [],
                                   'devdebug': False,
                                   'verbosity_level': 'INFO',
                                   'nobulletin': False})

    def test_choices(self):
        class UT_Arg1(ArgsBase):
            def config(self):
                cfg = DictDot()
                cfg.typ = TA_Store('Store', choices=['TRC', 'PAT'])
                cfg.gold = TA_Store('Store', choices=['GLD', 'DBG'], default='GLD')
                return cfg

            def main(self):
                pass

        OPT.clear()

        # pass case
        with MockVar(sys, "argv", "/myscript -typ TRC".split()):
            UT_Arg1()
            self.assertEqual(OPT, {'typ': 'TRC',
                                   'gold': 'GLD',
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})

        # fail case
        with MockVar(sys, "argv", "/myscript -typ XYZ".split()):
            with self.assertRaises(SystemExit):
                UT_Arg1()

        # No arg
        with MockVar(sys, "argv", "/myscript -gold DBG".split()):
            UT_Arg1()
            self.assertEqual(OPT, {'typ': None,
                                   'gold': 'DBG',
                                   'devdebug': False,
                                   'verbosity_level': None,
                                   'nobulletin': False})


if __name__ == '__main__':
    unittest.main()
