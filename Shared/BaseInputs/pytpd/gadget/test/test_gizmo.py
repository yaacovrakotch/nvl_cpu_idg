#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for utils.py
"""
from setenv_unittest import ROOT_ENV, EXIST_PDX_I_DRIVE      # must be first import for unittests
from io import StringIO
import re
from gadget.dictmore import DictDot, autoDictDot, TVPVConfigDict, autodict, recurse2dict
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import tempname, TempDir, File
from gadget.gizmo import *
from gadget.strmore import regex
from gadget.shell import CALLERBIN
from gadget.errors import Check
import gadget.gizmo as uu
import gadget.helperclass as helperclass
from unittest.mock import Mock
import datetime

myvarglob = 'somevalue'


def _pyname():
    """Returns the name of the module being tested"""
    return("gizmo")


def someclass1():    # Note: Do not move location of this function. It should be above any class definition.
    self = "abc"
    return super()


def someclass2():    # Note: Do not move location of this function. It should be above any class definition.
    return super()


class Various_tests(TestCase):

    def test_get_caller_lno(self):
        Check.check_get_caller_lno()    # This will raise exception if there is problem

    def test_null(self, abc=NULL):
        self.assertEqual(abc is NULL, True)

    def test_iif(self):
        self.assertEqual(iif(True, 1, 2), 1)
        self.assertEqual(iif(False, 1, 2), 2)

    def test_ifnone(self):
        self.assertEqual(ifnone(1, 2), 1)
        self.assertEqual(ifnone(None, 2), 2)

    def test_raiseif(self):
        raise_if(False, Exception, "message")   # no exception

        class MyExc(Exception):
            pass
        with self.assertRaisesRegex(MyExc, "hello there"):
            raise_if(123, MyExc, "hello there")

    def test_switch(self):
        dd = DictDot()
        dd.a = 61
        dd.b = 95
        dd.c = partial(int, "23")
        self.assertEqual(switch("a", dd), 61)
        self.assertEqual(switch("b", dd), 95)
        self.assertEqual(switch("c", dd), 23)
        self.assertEqual(switch("d", dd), None)
        self.assertEqual(switch("d", dd, default=333), 333)

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="Timing sensitive test. Run from unix commandline."))
    def test_various_elapsed(self):
        swtop = Elapsed(importtime=True)
        sw1 = Elapsed()
        time.sleep(0.01)
        sw2 = Elapsed()
        time.sleep(0.01)

        res = {}
        res['tag1'] = int(sw1.elapsed(reset=True) * 100)
        res['tag1a'] = int(sw1.elapsed() * 100)
        res['tag2'] = int(sw2.elapsed() * 100)
        res['total'] = int(sw1.elapsed(top=True) * 100)
        sw2.reset()
        res['pretty'] = sw2.elapsed(True)
        res['importtime'] = int(swtop.elapsed() * 100)

        print(res)
        self.assertEqual(res['tag1'], 2)
        self.assertEqual(res['tag1a'], 0)
        self.assertEqual(res['tag2'], 1)
        self.assertEqual(res['total'], 2)
        self.assertEqual(res['pretty'], "0.000 Secs")
        self.assertTrue(res['importtime'] > 10, 'must be greater than 10 from the time of import')

    @unittest.skipIf(*is_ut_option('SLOW', message="time delay test"))   # change message to right one
    def test_various_elapsed2(self):
        sw1 = Elapsed()
        time.sleep(1.5)
        res1 = "%s" % sw1
        res2 = "%.3f" % sw1(pretty=False)
        res3 = "%s" % sw1()
        res4 = "%s" % sw1(reset=True)
        res5 = "%s" % sw1(True, reset=True)
        res6 = "%s" % sw1(top=True)
        res7 = "%s" % sw1(lastcall=True)

        self.assertTrue(re.search(r'1.\d+ Secs', res1), res1)
        self.assertTrue(re.search(r'1.\d+', res2), res2)
        self.assertTrue(re.search(r'1.\d+ Secs', res3), res3)
        self.assertTrue(re.search(r'1.\d+ Secs', res4), res4)
        self.assertTrue(re.search(r'0.00\d Secs', res5), res5)
        self.assertTrue(re.search(r'1.\d+ Secs', res6), res6)
        self.assertTrue(re.search(r'0.00\d Secs', res7), res7)

        # importtime
        self.assertGreater(Elapsed(importtime=True).elapsed(), 1)

    def test_various_isany(self):
        self.assertEqual(isany('abc', 'dddeeeb'), True)
        self.assertEqual(isany('abc', 'cddeeef'), True)
        self.assertEqual(isany('abc', 'dddeeef'), False)
        self.assertEqual(isany('a', 'f'), False)
        self.assertEqual(isany({str, int}, {str, int, int, object, None}), True)
        self.assertEqual(isany({int}, {str, object, None}), False)  # long is not supported in py3
        dd = {'mappinglist': 1, "mappingbits": 2, "abc": 3}
        self.assertEqual(isany("mappinglist mappingbits".split(), dd), True)
        self.assertEqual(isany("appinglist appingbits".split(), dd), False)

    def test_gcd(self):
        result = gcd(2, 6)
        self.assertEqual(result, 2)

        result = gcd(10000, 10000)
        self.assertEqual(result, 10000)

    def test_gcdm(self):
        result = gcdm([6, 12, 18, 48])
        self.assertEqual(result, 6)

        result = gcdm([13, 17, 19])
        self.assertEqual(result, 1)

    def test_lcm(self):
        result = lcm(2, 3)
        self.assertEqual(result, 6)

        result = lcm(10000, 10000)
        self.assertEqual(result, 10000)

    def test_lcmm(self):
        result = lcmm([1, 2, 6])
        self.assertEqual(result, 6)

    def test_hex_to_bin(self):
        result = hex_to_bin('0FF15A')
        self.assertEqual(str(result), '000011111111000101011010')
        result = hex_to_bin('0FF 15A')
        self.assertEqual(str(result), '000011111111000101011010')
        result = hex_to_bin('0 F F 1 5 A', 21)
        self.assertEqual(str(result), '011111111000101011010')
        result = hex_to_bin('000000', 21)
        self.assertEqual(str(result), '000000000000000000000')

    def test_get_sec(self):
        self.assertEqual(get_sec("100"), 100)
        self.assertEqual(get_sec("1d"), 24 * 60 * 60)
        self.assertEqual(get_sec("1h"), 60 * 60)
        self.assertEqual(get_sec("2m"), 60 * 2)
        self.assertEqual(get_sec("2s"), 2)
        self.assertEqual(get_sec("1h:1m:1s"), 60 * 60 + 60 + 1)

        # Test Error cases
        self.assertRaises(ValueError, get_sec, '1days')
        self.assertRaises(ValueError, get_sec, '1hds')

    def test_count_iter(self):
        self.assertEqual(count_iter(iter(range(10))), 10)

    def test_consume_iter(self):
        val = [0]

        def foo_iter(v):
            val[0] += v
        consume_iter(foo_iter, range(10))
        self.assertEqual(val[0], 45)

    def test_hashdig(self):
        self.assertEqual(hash_dig(0), "000000000000000000000")
        self.assertEqual(hash_dig(-10), "100000000000000000010")
        self.assertEqual(hash_dig(10), "000000000000000000010")
        self.assertEqual(len(hash_dig("abc")), 21)
        self.assertEqual(len(hash_dig("abcd")), 21)

    def test_uniqlist(self):
        self.assertEqual(uniqlist([]), [])
        self.assertEqual(uniqlist([1]), [1])
        self.assertEqual(uniqlist([3, 5, 1, 4, 2, 1, 2, 3, 4, 5]), [3, 5, 1, 4, 2])
        self.assertEqual(uniqlist([1, 1, 1, 2, 2, 2, 3, 3, 3]), [1, 2, 3])
        self.assertEqual(uniqlist([1, 1, 1, 1, 1]), [1])

    def test_check_slots(self):
        # Pass case ==============================
        class UT_P:
            __slots__ = ["a1"]

            @check_slots
            def __init__(self):
                self.a1 = 0

        oo = UT_P()

        # Fail case - no slots =====================
        class UT_F:
            @check_slots
            def __init__(self):
                self.a1 = 0

        self.assertRaises(Exception, UT_F)

        # Pass case - inherited -------------------
        class UT2P(UT_P):
            __slots__ = ["a1"]

            def myfoo(self):
                self.a1 = 0
        oo = UT2P()

        # Fail case - inherited -------------------
        class UT2F(UT_P):
            def myfoo(self):
                self.a1 = 0
        self.assertRaises(Exception, UT2F)

    def test_send_mail_ut(self):
        # Will not send email because IS_UT is set
        self.assertEqual(send_mail("FROME", "TOLIST", "subj", "message"), ["TOLIST"])

    @with_(MockVar, helperclass, "IS_UT", False)
    def test_send_mail(self):
        class UtSmtp:
            def __init__(self, host):
                pass

            def sendmail(self, from_e, to_, msg):
                print("TYPE:", type(to_))
                print(msg)

            def quit(self):
                pass

        with MockVar(sys, "stdout", StringIO()) as p:
            send_mail("FROME", "TOLIST", "subj", "message", _smtp=UtSmtp)
            for req in [" 'list'>", "text/plain", "message", "Subject: subj", 'To: TOLIST', 'From: FROME']:
                self.assertIn(req, p.getvalue())

        with MockVar(sys, "stdout", StringIO()) as p:
            send_mail("FROME", ["TOLIST"], "subj", "message", _smtp=UtSmtp)
            for req in [" 'list'>", "text/plain", "message", "Subject: subj", 'To: TOLIST', 'From: FROME']:
                self.assertIn(req, p.getvalue())

        with MockVar(sys, "stdout", StringIO()) as p:
            send_mail("FROME", ["TOLIST"], "subj", "message", _smtp=UtSmtp, html=True)
            for req in [" 'list'>", "text/html", "message", "Subject: subj", 'To: TOLIST', 'From: FROME']:
                self.assertIn(req, p.getvalue())

        with MockVar(sys, "stdout", StringIO()) as p:
            send_mail("FROME", [], "subj", "message", _smtp=UtSmtp, html=True)
            self.assertEqual(p.getvalue(), "")

        with MockVar(sys, "stdout", StringIO()) as p, TempDir(name=True) as tdir:
            attachment = join(tdir, "a.txt")
            File(attachment).touch()
            send_mail("FROME", "TOLIST", "subj", "message", _smtp=UtSmtp, text_file_attachment=[attachment])
            for req in ["Content-Disposition", "attachment", "filename", "a.txt"]:
                self.assertIn(req, p.getvalue())

            # check the attachment not exist
            with self.assertRaisesRegex(IOError, "Failed to attach file"):
                send_mail("FROME", "TOLIST", "subj", "message", _smtp=UtSmtp,
                          text_file_attachment=[join(tdir, "b.txt")])

        # send list tests
        self.assertEqual(send_mail('from', ['a', 'b'], 'subj', 'message', _smtp=UtSmtp),
                         ['a', 'b'])
        self.assertEqual(send_mail('from', 'a,b;d e', 'subj', 'message', _smtp=UtSmtp),
                         ['a', 'b', 'd', 'e'])
        self.assertEqual(send_mail('from', 'a@com', 'subj', 'message', _smtp=UtSmtp),
                         ['a@com'])
        self.assertEqual(send_mail('from', 'a@com', 'subj', 'message', _smtp=UtSmtp, cc_list='c@com'),
                         ['a@com', 'c@com'], "CC list appended to the mail")
        self.assertEqual(send_mail('from', 'a@com', 'subj', 'message', _smtp=UtSmtp, cc_list=['c@com']),
                         ['a@com', 'c@com'], "CC list appended to the mail")

        with MockVar(helperclass, "IS_UT", True):
            with MockVar(sys, "stdout", StringIO()) as p:
                result = send_mail("FROME", "TOLIST", "subj", "message", _smtp=UtSmtp)
                self.assertEqual(p.getvalue(), '')   # did not send mail
                self.assertEqual(result, ["TOLIST"])

        # exception happened
        from socket import error

        class UtSmtpError(UtSmtp):
            def quit(self):
                raise error("Oops")

        with self.assertRaisesRegex(error, "Error:"):
            send_mail('from', 'a@com', 'subj', 'message', _smtp=UtSmtpError)

    def test_chunker(self):

        self.assertRaises(Exception, chunker, 'ABC', -1)

        sequence = 'ABCDEF'
        chunk_list = []

        for item in chunker(sequence, 2):
            chunk_list.append(item)

        # Check strings.
        self.assertEqual(chunk_list, ['AB', 'CD', 'EF'])

        # Check lists.
        sequence = [{'A': 1}, {'B': 2}, {'C': 3}, {'D': 4}]
        chunk_list = []

        for item in chunker(sequence, 2):
            chunk_list.append(item)

        self.assertEqual(chunk_list, [[{'A': 1}, {'B': 2}],
                                      [{'C': 3}, {'D': 4}]])

    def test_is_raise(self):
        def foo(arg1):
            raise IOError("some error")

        self.assertFalse(israise(IOError, lambda x: x, 1))
        self.assertTrue(israise(IOError, foo, arg1=21))
        self.assertRaises(IOError, israise, KeyError, foo, 22)

    def test_new_class(self):
        # Simple case
        class One:
            def f1(self):
                return 123

        class Two:
            def f2(self):
                return 456

        listclass = [One, Two]
        Three = new_class("Three", tuple(listclass))
        x1 = Three()
        self.assertEqual(x1.f1(), 123)
        self.assertEqual(x1.f2(), 456)

        class Four(Three):
            def f2(self):
                return Three.f2(self) + 5
        x2 = Four()
        self.assertEqual(x2.f1(), 123)
        self.assertEqual(x2.f2(), 461)

    def test_var_name(self):
        # local var
        myvar = 'abc'
        self.assertEqual(var_name(myvar), 'myvar')
        myvar1 = 567
        self.assertEqual(var_name(myvar1), 'myvar1')

        # global var
        self.assertEqual(var_name(myvarglob), 'myvarglob')

        # not found
        self.assertRaisesRegex(Exception, "Cannot get", var_name, 'somevalue1')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_convert_utc_JF(self):
        t_format = '%Y-%m-%d %H:%M:%S'
        run_date = '2018-12-20 11:44:31'
        expected_date = '2018-12-20 19:44:31'
        self.assertRaises(Exception, convert_to_utc, run_date)

        date = datetime.datetime.strptime(run_date, t_format)
        self.assertEqual(convert_to_utc(date).strftime(t_format), expected_date, "Precalculated dates match")

    @unittest.skip("Run this test in PG.")   # added because of timezones for expected
    def test_convert_utc_PG(self):
        t_format = '%Y-%m-%d %H:%M:%S'
        run_date = '2018-12-21 03:44:31'
        expected_date = '2018-12-20 19:44:31'
        self.assertRaises(Exception, convert_to_utc, run_date)

        date = datetime.datetime.strptime(run_date, t_format)
        self.assertEqual(convert_to_utc(date).strftime(t_format), expected_date, "Precalculated dates match")

    def test_all_except(self):

        class Sample1:
            def __init__(self):
                self.name = 'sample'
                self.value = 123
                self.other = ''
                self.other2 = 0

        class Sample2:
            def __init__(self):
                self.name = 'sample'
                self.value = 456
                self.other = ''
                self.other2 = 1

        s1 = Sample1()
        s2 = Sample2()

        self.assertTrue(all_match_except(s1, s2, equal=['name'], non_equal=['value']))
        self.assertFalse(all_match_except(s1, s2, equal=['value'], non_equal=['other']))
        self.assertTrue(all_match_except(s1, s2, equal=['name', 'other'], non_equal=['value', 'other2']))

    def test_get_free_port(self):
        port = get_free_port()
        self.assertTrue(isinstance(port, int), "Not a valid port id")
        self.assertIn(port, range(65536))

    def test_py2_cmp(self):
        self.assertEqual(py2_cmp(10, 5), 1)
        self.assertEqual(py2_cmp(-5, 0), -1)
        self.assertEqual(py2_cmp(5, 5), 0)
        self.assertEqual(py2_cmp(True, False), 1)
        self.assertEqual(py2_cmp(3.141, 2.963), 1)


class AnyContextTests(TestCase):
    def test_context(self):
        # pass case - positional args
        g_obj = [0]

        def foo(arg):
            g_obj[0] = arg

        try:
            self.assertEqual(g_obj, [0])
        finally:
            foo(123)

        self.assertEqual(g_obj, [123])

        # exception case - keyword args
        g_obj = [0]

        def foo1(arg, yo=None):
            g_obj[0] = yo

        with self.assertRaisesRegex(Exception, "something"):
            try:
                self.assertEqual(g_obj, [0])
                raise Exception("somethinghappened")
                self.fail("This should not be reached")
            finally:
                foo1(111, yo=456)

        self.assertEqual(g_obj, [456])


class UTParent:
    @classmethod
    def _name(cls):
        return cls.__name__


class UTChild(UTParent):
    pass


class MockVarTests(TestCase):

    def test_classmethod(self):
        with MockVar(UTParent, '_name', Mock()):
            pass

        self.assertEqual(UTChild._name(), 'UTChild')
        self.assertEqual(UTParent._name(), 'UTParent')

    def test_mockinside(self):
        self.assertEqual(uu.testonly_func(0), "RESULTA")
        self.assertEqual(uu.testonly_func(1), "RESULTA")
        self.assertEqual(uu.testonly_func(2), 'RESULT0.000 Secs')
        self.assertIs(uu.testonly_func(3), None)

        # Mock the "join" function
        with MockVar(uu, "join", lambda x: "MOCK1"):
            self.assertEqual(uu.testonly_func(0), "RESULTMOCK1")
            self.assertEqual(uu.testonly_func(1), "RESULTA")

        # Mock the "os.path.join" function
        with MockVar(uu.os.path, "join", lambda x: "MOCK2"):
            self.assertEqual(uu.testonly_func(0), "RESULTA")
            self.assertEqual(uu.testonly_func(1), "RESULTMOCK2")

        # Mock the "os.path.join" function
        with MockVar(os.path, "join", lambda x: "MOCK2"):
            self.assertEqual(uu.testonly_func(0), "RESULTA")
            self.assertEqual(uu.testonly_func(1), "RESULTMOCK2")

        # Mock the Elapsed class
        with MockVar(uu, "Elapsed", lambda: "MOCK3"):
            self.assertEqual(uu.testonly_func(2), "RESULTMOCK3")

        # make sure it is back
        self.assertEqual(uu.testonly_func(0), "RESULTA")
        self.assertEqual(uu.testonly_func(1), "RESULTA")
        self.assertEqual(uu.testonly_func(2), 'RESULT0.000 Secs')

    def test_methodmock(self):
        class UT1:
            def foo(self):
                return "orig"

        with MockVar(UT1, "foo", lambda self: "new1"):
            xx = UT1()
            self.assertEqual(xx.foo(), "new1")
        xy = UT1()
        self.assertEqual(xy.foo(), "orig")

    def test_attr(self):
        """
        MockVar using dot (attribute)
        """
        # Setup
        class UT1:
            def __init__(self):
                self.myvar = 123
        vv = UT1()

        # 1. Exist change
        with MockVar(vv, "myvar", 444):
            self.assertEqual(vv.myvar, 444)
        self.assertEqual(vv.myvar, 123)

        # 2. Exist delete
        self.assertTrue(hasattr(vv, "myvar"), "attribute must exist")
        with MockVar(vv, "myvar", MockVar.delete):
            self.assertFalse(hasattr(vv, "myvar"), "attribute must not exist")
        self.assertEqual(vv.myvar, 123)

        # 3. Not existing update
        self.assertFalse(hasattr(vv, "myvar2"), "attribute must not exist")
        with MockVar(vv, "myvar2", 445):
            self.assertEqual(vv.myvar2, 445)
        self.assertFalse(hasattr(vv, "myvar2"), "attribute must not exist")

        # 4. Not exist delete
        self.assertFalse(hasattr(vv, "myvar2"), "attribute must not exist")
        with MockVar(vv, "myvar2", MockVar.delete):
            self.assertFalse(hasattr(vv, "myvar2"), "attribute must not exist")
        self.assertFalse(hasattr(vv, "myvar2"), "attribute must not exist")

        # 5. Forced isattr
        with MockVar(vv, "myvar", 444, isattr=True):
            self.assertEqual(vv.myvar, 444)
        self.assertEqual(vv.myvar, 123)

        # 6. Forced isdict - error
        self.assertRaises(TypeError, MockVar(vv, "myvar", 444, isdict=True).__enter__)

        # 7. invalid var
        self.assertRaisesRegex(ValueError, 'non-alphanumeric', MockVar, vv, "myvar ", 444)

    def test_dict(self):
        """
        MockVar using dictionary (key)
        """
        # setup
        vv = {}
        vv['myvar'] = 123

        # 1. Exist change
        with MockVar(vv, "myvar", 444):
            self.assertEqual(vv['myvar'], 444)
        self.assertEqual(vv['myvar'], 123)

        # 2. Exist delete
        with MockVar(vv, "myvar", MockVar.delete):
            self.assertNotIn('myvar', vv)
        self.assertEqual(vv['myvar'], 123)

        # 3. Not existing update
        with MockVar(vv, "myvar2", 445):
            self.assertEqual(vv['myvar2'], 445)
        self.assertNotIn('myvar2', vv)

        # 4. Not existing delete
        with MockVar(vv, "myvar2", MockVar.delete):
            self.assertNotIn('myvar2', vv)
        self.assertNotIn('myvar2', vv)

        # 5. Forced isdict
        with MockVar(vv, "myvar", 444, isdict=True):
            self.assertEqual(vv['myvar'], 444)
        self.assertEqual(vv['myvar'], 123)

        # 5. Forced isattr - error
        self.assertRaises(AttributeError, MockVar(vv, "myvar", 444, isattr=True).__enter__)

        # 6. os.environ - special case (forced isdict)
        with MockVar(os.environ, "SOMEENV", "TEXT1"):
            self.assertEqual(os.environ['SOMEENV'], "TEXT1")

    def test_bug_delete_notexist(self):
        # dict
        vv = {'myvar': 123}
        with MockVar(vv, "somenew", 456):
            del vv['somenew']
        self.assertEqual(vv, {'myvar': 123})

        # class
        class SomeC:
            pass
        obj = SomeC()
        with MockVar(obj, "somenew", lambda self: 123):
            self.assertTrue(hasattr(obj, 'somenew'))
            delattr(obj, 'somenew')
        self.assertFalse(hasattr(obj, 'somenew'))

    def test_DictDot(self):
        """
        Autodetection
        """
        # DictDot autodetect
        vv = DictDot()
        vv['myvar'] = 123
        with MockVar(vv, "myvar", 444):
            self.assertEqual(vv['myvar'], 444)
            self.assertEqual(vv.myvar, 444)
        self.assertEqual(vv['myvar'], 123)
        self.assertEqual(vv.myvar, 123)

        # DictDot Forced
        with MockVar(vv, "myvar", 444, isdict=True):
            self.assertEqual(vv['myvar'], 444)
            self.assertEqual(vv.myvar, 444)
        self.assertEqual(vv['myvar'], 123)
        self.assertEqual(vv.myvar, 123)

        # Attr Forced
        with MockVar(vv, "myvar", 444, isattr=True):
            self.assertEqual(vv.myvar, 444)
            self.assertEqual(vv['myvar'], 444)
        self.assertEqual(vv['myvar'], 123)
        self.assertEqual(vv.myvar, 123)

        # both dict and attr
        self.assertRaises(Exception, MockVar, vv, "myvar", 444, isattr=True, isdict=True)

    def test_TVPVConfigDict(self):
        """
        Autodetection, AutoVivification object
        """
        vv = TVPVConfigDict()
        # Update
        vv.myvar = 123
        with MockVar(vv, "myvar", 444):
            self.assertEqual(recurse2dict(vv), {'myvar': 444})
            self.assertEqual(vv['myvar'], 444)
            self.assertEqual(vv.myvar, 444)
        self.assertEqual(recurse2dict(vv), {'myvar': 123})
        self.assertEqual(vv['myvar'], 123)
        self.assertEqual(vv.myvar, 123)

        # New key
        with MockVar(vv, "myvar2", 444):
            self.assertEqual(recurse2dict(vv), {'myvar': 123,
                                                'myvar2': 444})
        self.assertEqual(recurse2dict(vv), {'myvar': 123})

    def test_MockvarStdout(self):
        """
        Try to use MockVar to reroute stdout
        """
        with MockVar(sys, "stdout", StringIO()) as p:
            print("Hello")
            print("there")
            x = p
            self.assertEqual(x.getvalue(), "Hello\nthere\n")
        print("This-is-a-normal-print")

        # Check if the print outside the context manager is not added in StringIO()
        self.assertEqual(x.getvalue(), "Hello\nthere\n")
        x.write("more")
        self.assertEqual(x.getvalue(), "Hello\nthere\nmore")

    def test_Mockvar_classmethod(self):
        # This test is created bec MockVar() does not work well with staticmethod.
        # Use classmethod instead of staticmethod.
        class Foo:
            @classmethod
            def bar(cls, arg1):
                return arg1 + 1

        with MockVar(Foo, 'bar', Mock(return_value=22)):
            self.assertEqual(Foo.bar(1), 22)

        self.assertEqual(Foo.bar(2), 3)    # this should not raise exception
        self.assertEqual(Foo().bar(3), 4)

    def test_mockif(self):

        class Foo:
            def run_bar(self, x):
                return self.bar(x)

            def bar(self, x):
                return x + 10

            def run_add(self, x, y):
                return self.add(x, y=y + 1)

            def add(self, x, y=0):
                return x + y

        # positional args
        with MockVar(Foo, "bar", Mock(return_value=99), mockif=lambda s, x: x == 10):
            self.assertEqual(Foo().run_bar(10), 99)   # mocked
            self.assertEqual(Foo().run_bar(11), 21)   # not mocked

        # kwargs
        with MockVar(Foo, "add", Mock(return_value=98), mockif=lambda s, x, y: y == 5):
            self.assertEqual(Foo().run_add(1, y=1), 3)   # not mocked
            self.assertEqual(Foo().run_add(2, y=4), 98)  # mocked


class Stdout_tests(TestCase):

    def test_elapsed(self):
        with MockVar(sys, "stdout", StringIO()) as p:
            sw1 = Elapsed(name='test')
            time.sleep(0.001)
            sw1.disp()
            res = p.getvalue()
            self.assertTrue(regex(r'test: 0.0[01]\d Secs', res), "Result: %r" % res)

        with MockVar(sys, "stdout", StringIO()) as p:
            sw1 = Elapsed()
            time.sleep(0.001)
            sw1.disp()
            res = p.getvalue()
            self.assertTrue(regex(r'0.0[01]\d Secs', res), "Result: %r" % res)

    def test_timethis(self):
        @timethis
        def foo():
            time.sleep(0.05)

        with MockVar(sys, "stdout", StringIO()) as p:
            foo()   # Execute the function
            res = p.getvalue()
            self.assertTrue(regex(r'foo : 0.\d+ Secs', res), "Result: %r" % res)


class Vr_tests(TestCase):

    def test_vr_basic(self):
        def deep2(aa):
            dummy = gb1
            self.assertEqual(vr("{gb1} {aa} aa"), "gbone verydeep aa")  # deep2

        def deep(aa):
            dummy = gb1   # without this line, gb1 is not in global nor local. Adding this line will make it local (readonly)
            self.assertEqual(vr("{gb1}.{aa}"), "gbone.args")  # deep
            dp1 = "deep"
            deep2("verydeep")

        class foo:
            def __init__(self, val):
                self.val = val

        gb1 = "gbone"
        gb2 = "gbtwo"
        self.assertEqual(vr("text {gb1} {gb1}{gb2}"), "text gbone gbonegbtwo")  # local
        self.assertEqual(vrlocal("text {gb1} {gb1}{gb2}"), "text gbone gbonegbtwo")  # local
        deep("args")

        obj = foo("FOOD")
        self.assertEqual(vr("{gb1}={obj.val}{obj.val}"), "gbone=FOODFOOD")   # object attribute (with "." character)
        self.assertEqual(vrlocal("{gb1}={obj.val}{obj.val}"), "gbone=FOODFOOD")   # object attribute (with "." character)

    def test_vr_print1(self):
        with MockVar(sys, "stdout", StringIO()) as p:
            a = 123
            b = 456
            print(vr(str(a)))
            print(vr("a={a} b={b}"))
            self.assertEqual(p.getvalue(), "123\na=123 b=456\n")    # plain vr(), import *

    def test_vr_print2(self):
        import gadget.gizmo as u
        with MockVar(sys, "stdout", StringIO()) as p:
            a = 123
            b = 456
            print(u.vr("a={a} b={b}"))
            self.assertEqual(p.getvalue(), "a=123 b=456\n")    # plain vr(), import gadget

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="From unix commandline only"))
    def test_vr_globbasic(self):
        a = 123
        self.assertEqual(vr("{a} {a} {__name__}"), '123 123 __main__')
        self.assertRaises(KeyError, vrlocal, "{a} {a} {__name__}")


class Pyname_tests(TestCase):
    def init(self, opt):       # good template!
        self.tmp = tempname() + ".py"
        print("Tempname:", self.tmp)

        code = f'''#!%(exec)s
import sys
sys.path.insert(0, r"{ROOT_ENV}/gadget")
import %(mod)s
%(opt)s
''' % {'mod': _pyname(),
            'exec': sys.executable,
            'cwd': os.path.abspath(os.path.dirname(CALLERBIN)),
            'opt': opt}
        print(code)

        # Create the file
        with open(self.tmp, "w") as fh:
            fh.write(code)
        os.chmod(self.tmp, 0o750)

    def tearDown(self):
        if hasattr(self, "tmp") and os.path.exists(self.tmp):
            os.unlink(self.tmp)

    def test_pyname_fromfile(self):
        from gadget.shell import SystemCall
        mod = _pyname()
        self.init(vr("print({mod}._pyname())"))
        out = SystemCall(self.tmp).run_outtxt()[1].strip()
        self.assertEqual(out, mod)

    def test_pyname_basic(self):
        self.assertEqual(_pyname(), "gizmo")    # change "utils" when .py name changes


class With_Test(TestCase):

    def test_basic(self):
        res = []

        class My:
            def __init__(self, aa):
                self.aa = aa

            def __enter__(self):
                res.append('enter %s' % self.aa)

            def __exit__(self, exc_type, exc_value, traceback):
                res.append('exit')

        @with_(My, 2)
        def foo(arg):
            res.append('in foo')
            return arg + 3

        res.append('start')
        self.assertEqual(foo(21), 24)
        res.append("done")
        self.assertEqual(res, ['start', 'enter 2', 'in foo', 'exit', 'done'])

    def test_chdir(self):
        # This tests Chdir(), with no args to foo(), kwargs to context
        with TempDir(name=True, chdir=True) as tdir:

            @with_(TempDir, chdir=True)
            def foo():
                self.assertNotEqual(tdir, os.getcwd())
                return 21

            self.assertEqual(foo(), 21)
            self.assertEqual(tdir, os.getcwd())

    def test_MockVar_multi(self):
        # multiple decorator, kwargs to foo()
        res = {'key': 123, 'more': 111}

        @with_(MockVar, res, 'more', 222)
        @with_(MockVar, res, 'key', 456)
        def foo(arg):
            self.assertEqual(res['key'], arg)
            self.assertEqual(res, {'key': 456, 'more': 222})
            return 22

        self.assertEqual(foo(arg=456), 22)
        self.assertEqual(res, {'key': 123, 'more': 111})

    @with_(MockVar, sys, 'argv', ['someargs'])
    def test_ut1(self):
        # test if unittests work well with @with_
        self.assertEqual(sys.argv, ['someargs'])

    def test_ut2(self):
        # this test must be just-after test_ut1()
        # check if sys.argv goes to original value
        self.assertNotEqual(sys.argv, ['someargs'])


class SingletonTest(TestCase):
    def test_basic(self):
        varg = [0]

        @singleton_instantiate(17, a3=29)    # This will make class name below an instantiated object (singleton)
        class UT1:
            def __init__(self, a1, a2=None, a3=None):
                varg[0] += 1
                self.a1 = a1
                self.a2 = a2
                self.a3 = a3

            def __call__(self):
                self.a1 += 1
                return (self.a1, self.a2, self.a3)

        self.assertEqual(UT1(), (18, None, 29))
        self.assertEqual(UT1(), (19, None, 29))
        self.assertEqual(UT1(), (20, None, 29))
        self.assertEqual(varg[0], 1)

    def test_cases(self):
        # no args
        @singleton_instantiate()    # This will make class name below an instantiated object (singleton)
        class UT1:
            def __init__(self, a1=5, a2=None, a3=None):
                self.a1 = a1
                self.a2 = a2
                self.a3 = a3

            def __call__(self):
                self.a1 += 1
                return (self.a1, self.a2, self.a3)
        self.assertEqual(UT1(), (6, None, None))
        self.assertEqual(UT1(), (7, None, None))

        # error case - missing ()
        with self.assertRaisesRegex(Exception, "singleton decorator must"):
            @singleton_instantiate
            class UT2:
                pass

        # error case - [bec of logic]
        with self.assertRaisesRegex(Exception, "singleton decorator must"):
            @singleton_instantiate(dict)    # This will make class name below an instantiated object (singleton)
            class UT3:
                def __init__(self, cls):
                    pass

        # valid case - input is a class
        @singleton_instantiate(dict, _nocheck=True)    # This will make class name below an instantiated object (singleton)
        class UT4:
            def __init__(self, cls):
                self.cls = cls

            def meth1(self):
                return self.cls
        self.assertIs(UT4.meth1(), dict)

        # inheritance of a singleton class
        class UT5(UT4.__class__):
            def meth2(self):
                return 58
        self.assertIs(UT5(dict).meth1(), dict)
        self.assertEqual(UT5(dict).meth2(), 58)


class FuncLikeTest(TestCase):
    def test_basic(self):
        @funclike
        class UT1:
            def __init__(self, a1, a2=None, a3=None):
                self.a1 = a1
                self.a2 = a2
                self.a3 = a3

            def __call__(self):
                return (self.a1, self.a2, self.a3)

        self.assertEqual(UT1(17, a3=29), (17, None, 29))

    def test_cases(self):
        varg = [0]

        # No args, and check for class garbage-collect self.assertNotEqual(obj, 23)
        @funclike
        class UT1:
            def __init__(self):
                print("I am in init")
                varg[0] += 1
                self.var = id(self)

            def __call__(self):
                return 23

            def __del__(self):
                """In pypy, __del__ may or may not be called"""
                print("I am being destroyed")
                varg[0] -= 1

        print()
        print("First call")
        self.assertEqual(UT1(), 23)
        # self.assertEqual(varg[0], 0)   # will fail in pypy since __del__ may or may not be called
        print("2nd call")
        self.assertEqual(UT1(), 23)
        # self.assertEqual(varg[0], 0)   # will fail in pypy since __del__ may or may not be called

        # inherit the original class ==========================
        class UT2(UT1(returnclass=True)):
            def __del__(self):
                pass

        obj = UT2()   # this is a real object!
        self.assertNotEqual(obj, 23)
        self.assertEqual(obj(), 23)
        self.assertTrue(isinstance(obj, UT2))
        # self.assertEqual(varg[0], 1)

        # class does not have __call__ =================================
        with self.assertRaisesRegex(Exception, "required for funclike"):
            @funclike
            class UT3:
                def __init__(self):
                    pass


class CpuElapsedTest(TestCase):
    def test_basic(self):
        sw = CpuElapsed()
        initial = sw()
        self.assertLess(initial, 0.1)
        for j in range(2000000):
            pass
        self.assertGreater(sw(), 0.001)
        self.assertGreater(sw() - initial, 0.001)

        # 2nd run
        sw = CpuElapsed()
        initial = sw()
        self.assertLess(initial, 0.1)
        for j in range(2000000):
            pass
        self.assertGreater(sw(), 0.001)
        self.assertGreater(sw() - initial, 0.001)

        # reference is provided
        CpuElapsed.reference = None
        sw = CpuElapsed(4.4)
        self.assertEqual(sw.reference, 4.4)


class Test_CacheThis(TestCase):

    def test_CacheThis(self):

        class DummyClass:

            cache = CacheThis()                         # class var to cache double_value calls

            def __init__(self):
                self.called = False                     # flag to track if double_value was called

            @cache                                      # decorator to cache redundant calls
            def double_value(self, num):
                """Set the called flag adn return the given number multiplied by 2"""
                self.called = True
                return num * 2

            @cache
            def concat_strings(self, string1, string2, string3=None):
                """Concat all strings given, string3 is optional"""
                self.called = True
                value = string1 + string2
                if string3:
                    value += string3
                return value

            def clear_called_flag(self):                # clear flag that notes the real function was called
                self.called = False

            def get_called_flag(self):                  # return True if the real function was called
                return self.called

            def clear_cache(self):                      # clear the class method cache of calls
                self.cache.clear_cache()

        num = 5                                         # will call double value with 5
        exp = num * 2                                   # should return 10

        dummy = DummyClass()

        # case: should run the function and set called flag to true
        self.assertEqual(dummy.double_value(num), exp)
        self.assertTrue(dummy.get_called_flag())

        # case: clear called flag and run again, should use cache instead of calling double_value
        dummy.clear_called_flag()
        self.assertEqual(dummy.double_value(num), exp)
        self.assertFalse(dummy.get_called_flag())

        # case: clear cache and run again (should run the real function since cache was cleared)
        dummy.clear_called_flag()
        dummy.clear_cache()
        self.assertEqual(dummy.double_value(num), exp)
        self.assertTrue(dummy.get_called_flag())

        # case: use kwargs instead of args, should run the real function since the kwargs entry does not exist
        dummy.clear_called_flag()
        self.assertEqual(dummy.double_value(num=num), exp)
        self.assertTrue(dummy.get_called_flag())

        # case: another time with kwargs, should not run the real function since cache entry exists
        dummy.clear_called_flag()
        self.assertEqual(dummy.double_value(num=num), exp)
        self.assertFalse(dummy.get_called_flag())

        # case: call concat method, should not use cache
        string1 = "foo,"
        string2 = "bar,"
        exp = "foo,bar,"
        dummy.clear_called_flag()
        self.assertEqual(dummy.concat_strings(string1=string1, string2=string2), exp)
        self.assertTrue(dummy.get_called_flag())

        # case: call concat method, should use cache
        dummy.clear_called_flag()
        self.assertEqual(dummy.concat_strings(string1=string1, string2=string2), exp)
        self.assertFalse(dummy.get_called_flag())

        # case: call concat method with optional third string, should not use cache
        string3 = "done"
        exp = "foo,bar,done"
        dummy.clear_called_flag()
        self.assertEqual(dummy.concat_strings(string1, string2, string3), exp)
        self.assertTrue(dummy.get_called_flag())

        # case: call concat method with optional third string, should use cache
        dummy.clear_called_flag()
        self.assertEqual(dummy.concat_strings(string1, string2, string3), exp)
        self.assertFalse(dummy.get_called_flag())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
    exit(0)
