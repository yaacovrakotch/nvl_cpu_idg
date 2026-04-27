#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for printmore
"""
import setenv_unittest     # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.printmore import *
from gadget.gizmo import MockVar, israise
from gadget.dictmore import DictDot, autodict, TVPVConfigDict, autoDictDot
from gadget.helperclass import CaptureStdoutLog
from io import StringIO
import gadget.printmore as printmore
import sys
import argparse
import os
import pprint


class TestDisp(TestCase):     # This must be first because of traceback linenumbers.

    def test_disp(self):
        with CaptureStdoutLog() as p:
            disp('jdr')
        self.assertEqual(p.getvalue(), 'jdr [from lno#23]\n')

        with MockVar(printmore, 'IS_WEB', True):
            with CaptureStdoutLog() as p:
                disp('jdr')
                disp('jdr2')
        self.assertEqual(p.getvalue(), '\n<!--- jdr [from lno#28]-->\n\n<!--- jdr2 [from lno#29]-->\n')


class TestPrintAlign(TestCase):

    def test_case_bug(self):
        aa = list(range(31))
        pa = PrintAlign(rjust=False)
        pa(*aa[:10])
        pa(*aa[10:20])
        pa(*aa[20:30])
        pa(*aa[30:40])
        expect = '''
========================================
 0   1   2   3   4   5   6   7   8   9
 10  11  12  13  14  15  16  17  18  19
 20  21  22  23  24  25  26  27  28  29
 30
========================================
'''
        self.assertTextEqual(pa.string(), expect)

    def test_get_max_length(self):
        print("unittest for get_max_length")
        # array
        print("unittest array")
        aa = [['qq', 'dd', 'kkkk', 'ppp'],
              ['ww', 'www', 'wq', 'qqq'],
              ['wwwwww', 'wqqqqww', 'waaaq', 'qqzzzq']]
        dd = PrintAlign(aa)
        dd.get_max_length()
        self.assertEqual(dd.get_max_length(), [6, 7, 5, 6])

        # array with empty string
        print("unittest array with empty string")
        aa = [['qq', 'dd', 'kkkk', 'ppp'],
              ['ww', 'www', '', 'qqq'],
              ['wwwwww', 'wqqqqww', 'waaaq', 'qqzzzq']]
        dd = PrintAlign(aa)
        dd.get_max_length()
        self.assertEqual(dd.get_max_length(), [6, 7, 5, 6])

        # array with empty string
        print("unittest array with empty string")
        aa = [['qq', 'dd', 'kkkk', 'ppp'],
              ['ww', 'www', 'qqq'],
              ['wwwwww', 'wqqqqww', 'waaaq', 'qqzzzq']]
        dd = PrintAlign(aa)
        dd.get_max_length()
        self.assertEqual(dd.get_max_length(), [6, 7, 5, 6])

        # 1 row
        print("unittest only one row")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", "lll")
        self.assertEqual(kk.get_max_length(), [2, 3, 3, 3])

        # 1 item
        print("unittest only one row")
        aa = "aa bbb ccd eee hjuik"
        kk = PrintAlign(aa)
        self.assertEqual(kk.get_max_length(), [2, 3, 3, 3, 5])

        # many row with same column
        print("unittest for many row with same number of colmun")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", "lll")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "rsssrr", "1lll")
        self.assertEqual(kk.get_max_length(), [4, 6, 6, 4])

        # many row with different column (4,4,3)
        print("unittest many row different column (4,4,3)")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", "lll")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "rsssrr")
        self.assertEqual(kk.get_max_length(), [4, 6, 6, 3])

        # many row with different column (3,4,3)
        print("unittest many row different column (3,4,3)")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "1lll")
        self.assertEqual(kk.get_max_length(), [4, 6, 5, 2])

        # None for a value in column
        print("unittest many row with None in row")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", "ll")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", None, "1ll")
        self.assertEqual(kk.get_max_length(), [4, 6, 5, 3])

        # many row with empty string " "
        print("unittest many row with empty string")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", " ")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "", "1lll")
        self.assertEqual(kk.get_max_length(), [4, 6, 5, 4])

        # specified length
        print("unittest many row with empty string")
        kk = PrintAlign(max_col_len=[-1, -1, 10, -1])
        kk("aa", "ddd", "rrr", " ")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "", "1lll")
        self.assertEqual(kk.get_max_length(), [4, 6, 10, 4])

    def test_disp(self):
        print("unittest for disp()")
        # array
        print("unittest for array")
        aa = [['qq', 'dd', 'kkkk', 'ppp'],
              ['ww', 'www', 'wq', 'qqq'],
              ['wwwwww', 'wqqqqww', 'waaaq', 'qqzzzq']]
        dd = PrintAlign(aa)
        Expected = "================================\n     qq       dd   kkkk     ppp \n     ww      www     wq     qqq \n wwwwww  wqqqqww  waaaq  qqzzzq \n================================\n"
        self.assertEqual(dd.string(), Expected)

        # with header False
        print("unittest with header=False")
        dd = PrintAlign(aa, header=False)
        Expected = "     qq       dd   kkkk     ppp \n     ww      www     wq     qqq \n wwwwww  wqqqqww  waaaq  qqzzzq \n"
        self.assertEqual(dd.string(), Expected)

        # with separator True
        print("unittest with sep=True")
        dd = PrintAlign(aa, sep='|')
        Expected = "====================================\n     qq |      dd |  kkkk |    ppp \n     ww |     www |    wq |    qqq \n wwwwww | wqqqqww | waaaq | qqzzzq \n====================================\n"
        self.assertEqual(dd.string(), Expected)

        # with space=2
        print("unittest with space=2")
        dd = PrintAlign(aa, sep='|', space=2)
        Expected = "============================================\n      qq  |       dd  |   kkkk  |     ppp  \n      ww  |      www  |     wq  |     qqq  \n  wwwwww  |  wqqqqww  |  waaaq  |  qqzzzq  \n============================================\n"
        self.assertEqual(dd.string(), Expected)

        # with space=3
        print("unittest with space=3")
        dd = PrintAlign(aa, sep='|', space=3)
        Expected = "====================================================\n       qq   |        dd   |    kkkk   |      ppp   \n       ww   |       www   |      wq   |      qqq   \n   wwwwww   |   wqqqqww   |   waaaq   |   qqzzzq   \n====================================================\n"
        self.assertEqual(dd.string(), Expected)

        # array with empty string
        print("unittest for array with empty string")
        aa = [['qq', 'dd', 'kkkk', 'ppp'],
              ['ww', 'www', '', 'qqq'],
              ['wwwwww', 'wqqqqww', 'waaaq', 'qqzzzq']]
        dd = PrintAlign(aa)
        Expected = "================================\n     qq       dd   kkkk     ppp \n     ww      www            qqq \n wwwwww  wqqqqww  waaaq  qqzzzq \n================================\n"
        self.assertEqual(dd.string(), Expected)

        # 1 item
        print("unittest only one row")
        aa = "aa bbb ccd eee hjuik"
        kk = PrintAlign(aa)
        Expected = "==========================\n aa  bbb  ccd  eee  hjuik \n==========================\n"
#        kk("aa")
        self.assertEqual(kk.string(), Expected)

#        #empty row
        print("unittest for 0 row")
        kk = PrintAlign()
        Expected = "\n"
        self.assertEqual(kk.string(), Expected)

        # 1 row
        print("unittest with 1 row")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", "lll")
        Expected = "===================\n aa  ddd  rrr  lll \n===================\n"
        self.assertEqual(kk.string(), Expected)

#        #1 row
        print("unittest with 1 row")
        kk = PrintAlign()
        kk("aa bbb ccd eee hjuik")
        Expected = "======================\n aa bbb ccd eee hjuik \n======================\n"
        self.assertEqual(kk.string(), Expected)

        # many row with same column
        print("unittest with many row same column")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", "lll")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "rsssrr", "1lll")
        Expected = "============================\n   aa     ddd     rrr   lll \n aaaa  dsssdd   rssrr    ll \n  aa4      dd  rsssrr  1lll \n============================\n"
        self.assertEqual(kk.string(), Expected)

        print("unittest with miltiple row")
        kk = PrintAlign()
        kk("aa ddd rrr lll")    # this is a list which treat as 1 item only
        kk("aaaa dsssdd rssrr ll")
        kk("aa4 dd rsssrr llll")
        Expected = "======================\n       aa ddd rrr lll \n aaaa dsssdd rssrr ll \n   aa4 dd rsssrr llll \n======================\n"
        self.assertEqual(kk.string(), Expected)

        # many row with different column (4,4,3)
        print("unittest with many row different column (4,4,3)")
        kk = PrintAlign()
        kk("aa", "ddd", "rrr", "lll")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "rsssrr")
        Expected = "===========================\n   aa     ddd     rrr  lll \n aaaa  dsssdd   rssrr   ll \n  aa4      dd  rsssrr      \n===========================\n"
        self.assertEqual(kk.string(), Expected)

        # many row with different column (3,4,3)
        print("unittest with many row different column(3,4,3)")
        kk = PrintAlign(sep='|')
        kk("aa", "ddd", "rrr")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "1lll")
        Expected = "=============================\n   aa |    ddd |   rrr |    \n aaaa | dsssdd | rssrr | ll \n  aa4 |     dd |  1lll |    \n=============================\n"
        self.assertEqual(kk.string(), Expected)

        # None for a value in column
        print("unittest for many row with None")
        kk = PrintAlign(sep='|')
        kk("aa", "ddd", "rrr", "ll")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", None, "1ll")
        Expected = "==============================\n   aa |    ddd |   rrr |  ll \n aaaa | dsssdd | rssrr |  ll \n  aa4 |     dd |       | 1ll \n==============================\n"
        self.assertEqual(kk.string(), Expected)

        # many row with empty string " "
        print("unittest one column")
        kk = PrintAlign(sep='|')
        kk("aa")
        kk.printline("extralinelong")
        kk("aaaa")
        kk("aa4")
        self.assertEqual(kk.get_result(), ['=======',
                                           '   aa ',
                                           'extralinelong',
                                           ' aaaa ',
                                           '  aa4 ',
                                           '======='])

        # many row with empty string " "
        print("unittest for many row with empty string")
        kk = PrintAlign(sep='|')
        kk("aa", "ddd", "rrr", " ")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "", "1lll")
        Expected = "===============================\n   aa |    ddd |   rrr |      \n aaaa | dsssdd | rssrr |   ll \n  aa4 |     dd |       | 1lll \n===============================\n"
        self.assertEqual(kk.string(), Expected)

        # many row with empty string " "
        print("unittest for many row with empty strin11g")
        kk = PrintAlign(sep='|')
        kk("aa", "ddd", "rrr", " ")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "", "1lll")
        Expectedstr = "===============================\n   aa |    ddd |   rrr |      \n aaaa | dsssdd | rssrr |   ll \n  aa4 |     dd |       | 1lll \n===============================\n"
        self.assertEqual(kk.string(), Expectedstr)

        kk = PrintAlign(sep='|')
        kk("aa", "ddd", "rrr", " ")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "", "1lll")
        with MockVar(sys, "stdout", StringIO()) as p:
            kk.disp()
            self.assertEqual(p.getvalue().split('\n'),
                             ['===============================',
                              '   aa |    ddd |   rrr |      ',
                              ' aaaa | dsssdd | rssrr |   ll ',
                              '  aa4 |     dd |       | 1lll ',
                              '===============================',
                              ''])

        with MockVar(sys, "stdout", StringIO()) as p:
            kk.disp(strip=True)
            self.assertEqual(p.getvalue().split('\n'),
                             ['===============================',
                              '   aa |    ddd |   rrr |',
                              ' aaaa | dsssdd | rssrr |   ll',
                              '  aa4 |     dd |       | 1lll',
                              '===============================',
                              ''])

        # col_header=True
        kk = PrintAlign(sep='|', col_header=True)
        kk("aa", "ddd", "rrr", " ")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "", "1lll")
        with MockVar(sys, "stdout", StringIO()) as p:
            kk.disp()
        self.assertEqual(p.getvalue().split('\n'),
                         ['===============================',
                          '   aa |    ddd |   rrr |      ',
                          '===============================',
                          ' aaaa | dsssdd | rssrr |   ll ',
                          '  aa4 |     dd |       | 1lll ',
                          '===============================',
                          ''])

        # divider
        kk = PrintAlign(sep='|')
        kk("Big header")
        kk("{{divider}}")
        kk("Some more line")
        with MockVar(sys, "stdout", StringIO()) as p:
            kk.disp()
        self.assertEqual(p.getvalue().split('\n'),
                         ['=================',
                          '     Big header ',
                          '=================',
                          ' Some more line ',
                          '=================',
                          ''])

    def test_extra_line(self):
        # many row with empty string " "
        kk = PrintAlign(sep='|', header=False)
        kk.printline("some1")
        kk("aa", "ddd", "rrr", " ")
        kk.printline("some2aaa")
        kk.printline("some3")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk.printline("some4")
        kk("aa4", "dd", "", "1lll")
        kk.printline("some5")
        self.assertEqual(kk.get_result(), ['some1',
                                           '   aa |    ddd |   rrr |      ',
                                           'some2aaa',
                                           'some3',
                                           ' aaaa | dsssdd | rssrr |   ll ',
                                           'some4',
                                           '  aa4 |     dd |       | 1lll ',
                                           'some5'])

    def test_rjust(self):
        # many row with empty string " "
        kk = PrintAlign(sep=' ', header=False, rjust=False, space=0)
        kk("aa", "ddd", "rrr", " ")
        kk.printline("some2aaa")
        kk("aaaa", "dsssdd", "rssrr", "ll")
        kk("aa4", "dd", "", "1lll")
        self.assertEqual(kk.get_result(), ['aa   ddd    rrr       ',
                                           'some2aaa',
                                           'aaaa dsssdd rssrr ll  ',
                                           'aa4  dd           1lll'])


class TestPctIndicator(TestCase):
    def test_basic(self):
        # basic test - number is provided
        with MockVar(sys, "stdout", StringIO()) as p:
            with PctIndicator(3, out=sys.stdout) as ind:
                for i in range(4):
                    ind.disp(i)
            self.assertEqual(p.getvalue(), '  0%\r 33%\r 66%\r100%\r     \r')

        # basic test - number is not provided
        with MockVar(sys, "stdout", StringIO()) as p:
            with PctIndicator(3, out=sys.stdout) as ind:
                for i in range(4):
                    ind.disp()
            self.assertEqual(p.getvalue(), '  0%\r 33%\r 66%\r100%\r     \r')

        # more tests
        with MockVar(sys, "stdout", StringIO()) as p:
            ind = PctIndicator(1000, out=sys.stdout)
            for i in range(1000):
                ind.disp(i)
            ind.close()
            ind.close()   # 2nd close occurrence is intentional to check non-active state

            res = p.getvalue()
            self.assertEqual(res.count("%"), 100)
            self.assertEqual("25%" in res, True)
            self.assertEqual("80%" in res, True)
            self.assertEqual(res.endswith("\r"), True)

        # exceeded case
        with MockVar(sys, "stdout", StringIO()) as p:
            with PctIndicator(3, out=sys.stdout) as ind:
                for i in range(10):
                    ind.disp(i)
            res = p.getvalue()
            self.assertTrue("100%" in res, "100% must exist")


class Dumper_tests(TestCase):

    def setUp(self):
        self.stdarr = ['string',
                       {'ky1': 1,
                        'string': {'abc': True, 22: None, 'def': 'string'},
                        'ky3': ['inarr1', 1, False, True, None, 4.1]
                        },
                       'arr3']

    def test_dump_hashofarray(self):
        arr = self.stdarr
        pprint.pprint(Dumper(arr, p=False).raw())
        self.assertEqual(arr, Dumper(arr, p=False).raw())

    def test_dump_deepfalse(self):
        res = Dumper(vars(), dot=True, deep=False, p=False).string()
        print(res)
        self.assertEqual(len(res.split('\n')), 2)

    def test_dump_arrdot(self):
        arr = self.stdarr

        res = Dumper(arr, dot=True, p=False).string()
        print(res)
        self.assertEqual(len(res), 224)

    def test_dump_argparse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-verbose', action='store_true')
        parser.add_argument('-string', action='store')
        parser.add_argument('-strarr', action='append')
        parser.add_argument('-int', action='store', type=int)
        parser.add_argument('all', nargs='*')
        args = parser.parse_args(["a b c"])

        res = Dumper(args, dot=True, p=False).string()
        print(res)
        self.assertEqual(len(res), 91)

    def test_dump_autodict(self):
        hh = autodict()
        hh['abc']['def'] = 23
        hh['ghi']['klm'] = 22

        res = Dumper(hh, dot=True, p=False).string()
        print(res)
        self.assertEqual(len(res), 26)

    # @unittest.skip("skipping, TVPVConfigDict does not exist")    # uncomment this to skip this test
    def test_dump_tvpvdict(self):
        hh = TVPVConfigDict()
        hh.a = 'A'
        hh.b.bb = 'B'
        hh.b.cc.dd.ee.ff = 'C'

        res = Dumper(hh, dot=True, p=False).string()
        print(res)
        self.assertEqual(len(res), 123)

    def test_dumkpat_custom_object(self):
        class _refx:
            def __init__(self, rr, r2):
                self.rr = rr
                self.r10 = rr + 10
                self.o1 = _refx(51, r2) if rr < 50 else "one"
                self.o2 = r2
                self.o3 = r2

        obj1 = _refx(22, None)
        obj2 = _refx(23, obj1)

        res = Dumper(obj2, dot=True, p=False).string()
        print(res)
        print("Test: dot result of custom object with DUPLICATE reference")
        self.assertEqual(len(res), 487)

    @unittest.skipIf(*is_ut_option("OPTIONAL", message="Fails with pypy"))
    def test_dump_module(self):
        res = Dumper(os.path, dot=True, p=False).string()
        print("Test: dump of os.path number of lines.")
        self.assertFalse(len(res.split('\n')) < 1000, "len= " + str(len(res.split('\n'))))

    def test_dump_dict_object(self):
        class obj_list(list):
            pass

        class obj_dict(dict):
            pass
        l1 = [1, 2, 'string']
        s1 = ('str1', 'str2')
        l2 = ['another', s1]
        a = obj_list()
        b = obj_dict()
        a.v1 = 11
        a.v2 = 'string'
        a.b = b
        a.v3 = l2
        b.v1 = a
        b.v2 = None
        b.v3 = 'another string'

        res = Dumper(b, dot=True, p=False).string()
        print(res)
        print("Test: dict object (it has empty items() but vars() exist")
        self.assertEqual(len(res), 190)

    def test_simple(self):
        res = Dumper([1, 2, 3], p=False).string()
        self.assertEqual(res, "[1,\n 2,\n 3]")

    def test_scalar_dot(self):
        aa = 123
        res = Dumper(aa, dot=True, p=False).string()
        self.assertEqual(res, '= 123\n')

    def test_dictfunc(self):
        aa = {'key1': lambda: True,         # lambda
              'key2': israise,             # func
              'key3': self.test_dictfunc   # method
              }
        res = Dumper(aa, dot=True, p=False).string()
        self.assertEqual(len(res.split('\n')), 4)

    def test_dumper_unknow_object(self):
        aa = b"hello"
        res = Dumper(aa, dot=True, p=False).string()
        self.assertIn("Skipped", res)

    def test_duplicate(self):
        aa = {'key1': 1,
              'key2': 2,
              }
        bb = {'keya': aa,
              'keyb': [aa, aa]}
        Dumper(bb, dot=True)
        res = Dumper(bb, dot=True, p=False).string()
        self.assertEqual(res, "keya.key1 = 1\nkeya.key2 = 2\nkeyb.[0] = 'DUPLICATE .keya'\nkeyb.[1] = 'DUPLICATE .keya'\n")

        res = Dumper(bb, dot=True, p=False, dupok=True).string()
        print("With dup====")
        print(res)
        self.assertEqual(res, 'keya.key1 = 1\nkeya.key2 = 2\nkeyb.[0].key1 = 1\nkeyb.[0].key2 = 2\nkeyb.[1].key1 = 1\nkeyb.[1].key2 = 2\n')


class DumperBasic(TestCase):
    def test_types(self):
        # scalar
        v = 12
        self.assertEqual(Dumper(v, dot=True, p=False).string(), '= 12\n')

        # dictionary
        v = {'a': 12, 'b': "rty"}
        self.assertEqual(Dumper(v, dot=True, p=False).string(), "a = 12\nb = 'rty'\n")

        # list
        v = [12, 13, 15]
        self.assertEqual(Dumper(v, dot=True, p=False).string(), '[0] = 12\n[1] = 13\n[2] = 15\n')

        # object
        class UT1:
            def __init__(self):
                self.a = [1, 22]
                self.b = "abc"
                self.c = {'a': 123}
        v = UT1()
        self.assertEqual(Dumper(v, dot=True, p=False).string(),
                         "a.[0] = 1\na.[1] = 22\nb = 'abc'\nc.a = 123\n")

        # dict object
        class UT2(dict):
            def foo(self):
                self.a = 22
        v = UT2()
        v['b'] = 'def'
        v.foo()
        self.assertEqual(Dumper(v, dot=True, p=False).string(), "a = 22\nb = 'def'\n")

    def test_multilevel(self):
        # AutoVivification - dict of dict
        v = autoDictDot()
        v.a.b = 12
        v.a.c = "thirteen"
        v.b.d = {'aa': 99, 'bb': "hdr"}
        v.e = [100, None, 102]
        v.f.g.h = {"x", "y", "z"}   # set
        self.assertEqual(Dumper(v, dot=True, p=False).string().split('\n'),
                         ['a.b = 12',
                          "a.c = 'thirteen'",
                          'b.d.aa = 99',
                          "b.d.bb = 'hdr'",
                          'e.[0] = 100',
                          'e.[1] = 102',
                          'e.[2] = None',
                          "f.g.h.[0] = 'x'",
                          "f.g.h.[1] = 'y'",
                          "f.g.h.[2] = 'z'",
                          ''])

        # list of list
        v = [11, ['a', 'b', 'c'], 12]
        self.assertEqual(Dumper(v, dot=True, p=False).string().split('\n'),
                         ['[0] = 11',
                          '[1] = 12',
                          "[2].[0] = 'a'",
                          "[2].[1] = 'b'",
                          "[2].[2] = 'c'",
                          ''])

        # recursive
        class UT1:
            def __init__(self, inp, whoami):
                self.a = whoami
                self.b = inp
        x = UT1(None, 'x')
        z = UT1(x, 'z')
        v = UT1(z, 'v')
        x.b = v
        self.assertEqual(Dumper(v, dot=True, p=False,).string().split('\n'),
                         ["a = 'v'",
                          "b (obj).a = 'z'",
                          "b (obj).b (obj).a = 'x'",
                          "b (obj).b (obj).b (obj) = 'DUPLICATE '",
                          ''])

    def test_options(self):
        # string output, non-dot
        v = [12, 13, 15]
        self.assertEqual(Dumper(v, p=False).string(), '[12,\n 13,\n 15]')

        # raw output
        v = DictDot()
        v.a = DictDot()
        v.a.b = 12
        v.a.c = "thirteen"
        self.assertEqual(Dumper(v, p=False).raw(), {'a': {'c': 'thirteen',
                                                          'b': 12}})

        # deep is False
        class UT1:
            def __init__(self, inp):
                self.a = 22
                self.b = inp
        x = UT1(None)
        v = UT1(x)
        self.assertRegex(Dumper(v, dot=True, p=False, deep=False).string(),
                         'a = 22\nb \\(obj\\) = (.*) \\w+>\n')
        self.assertEqual(Dumper(v, dot=True, p=False).string(),
                         'a = 22\nb (obj).a = 22\nb (obj).b (obj) = None\n')

    def test_print(self):
        with MockVar(sys, "stdout", StringIO()) as p:
            Dumper([1, 2, 3])
            self.assertEqual(p.getvalue(), "[1,\n 2,\n 3]\n")  # 1

        with MockVar(sys, "stdout", StringIO()) as p:
            Dumper([1, 2, 3], dot=True)
            self.assertEqual(p.getvalue(), '[0] = 1\n[1] = 2\n[2] = 3\n\n')  # 2

    def test_pprint_width(self):
        vault_output_example = {
            'attributes': '1core,2core,north,officer',
            'directives': '',
            'intent': 'feature_ring feature_sa',
            'module': '',
            'owner': 'open',
            'path': 'tests/sbft_fc/cnl_a0/rmarinbe/vaultdeposit/mc_wpq_consumer_counter_mbox.max',
            'plist_directives': '',
            'product': '',
            'purpose': 'feature_ring feature_sa',
            'run_args': 'release_tag=2019.ww14.2.1783  fcs_llc_broadcast_en=1 hvm_test_wait=800000 stream_map=0,1,2,3,4,5,6,7',
            'status': 'prevalidated',
            'step': '',
            'tag': 'sbft',
            'test_id': '0156316',
            'testname': 'mc_wpq_consumer_counter_mbox',
            'testtype': 'sbft_fc'
        }

        # Empty dict (dict width is 2, print width should be 1)
        dd = {}
        self.assertEqual(Dumper(dd, p=False).pprint_width(), 1)

        # Short dict (dict width is 24, print width should be 23)
        dd = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(Dumper(dd, p=False).pprint_width(), 23)

        # Medium dict (dict width is 551, print width should be 550)
        dd = dict(vault_output_example)
        self.assertEqual(Dumper(dd, p=False).pprint_width(), 550)

        # Long dict (dict width is 59900, print width should be 59899)
        dd = {}
        for k, v in list(vault_output_example.items()):
            for i in range(0, 100, 1):
                dd["%s.%02d" % (k, i)] = v
        self.assertEqual(Dumper(dd, p=False).pprint_width(), 59899)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
