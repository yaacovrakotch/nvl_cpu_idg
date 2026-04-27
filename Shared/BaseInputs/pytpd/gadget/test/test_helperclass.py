#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for helperclass.py
"""
import re
from setenv_unittest import ROOT_ENV     # must be first import for unittests
from gadget.helperclass import *
from gadget.ut import unittest, is_ut_option, TestCase, trim_traceback_without_code
from gadget.dictmore import TVPVConfigDict, NamedSeq
from gadget.gizmo import MockVar
from gadget.shell import IS_UNIX, IS_WIN
from gadget.errors import ErrorUser
from gadget.shell import SystemCall
from gadget.files import File, TempName, TempDir
from unittest.mock import patch, Mock
from io import StringIO
from os import remove
from pprint import pprint


class TestFlow(TestCase):

    def test_basic(self):

        def r1():
            result.append('r1')

        def r2():
            result.append('r2')

        def r3():
            result.append('r3')

        def r4(ar1, ar2=None):
            result.append(f'r4 {ar1} {ar2}')

        result = []
        flow = Flow(only=[], skip=[], add=[])
        flow.append(r1, '1 one')
        flow.append(r3, '3 three')
        flow.append(r2, '2 two')
        flow.append(r4, '4 four', args=[1], kwargs={'ar2': 2})
        flow.run()
        self.assertEqual(result, ['r1', 'r3', 'r2', 'r4 1 2'])

        # skip
        result = []
        flow = Flow(only=[], skip=['4A'], add=[])
        flow.append(r1, '1 one')
        flow.append(r3, '3 three')
        flow.append(r2, '2 two', skip=True)
        flow.append(r4, '4a four', args=[1], kwargs={'ar2': 2})
        flow.run()
        self.assertEqual(result, ['r1', 'r3'])

        # only
        result = []
        flow = Flow(only=['1'], skip=['4A'], add=[])
        flow.append(r1, '1 one')
        flow.append(r3, '3 three')
        flow.append(r2, '2 two', skip=True)
        flow.append(r4, '4a four', args=[1], kwargs={'ar2': 2})
        flow.run()
        self.assertEqual(result, ['r1'])

        # add
        result = []
        flow = Flow(only=[], skip=['4A', '3'], add=['2'])
        flow.append(r1, '1 one')
        flow.append(r3, '3 three')
        flow.append(r2, '2 two', skip=True)
        flow.append(r4, '4a four', args=[1], kwargs={'ar2': 2})
        flow.run()
        self.assertEqual(result, ['r1', 'r2'])

        # skip with only and add
        result = []
        flow = Flow(only=['1'], skip=[], add=['2'])
        flow.append(r1, '1 one', skip=True)
        flow.append(r3, '3 three', skip=True)
        flow.append(r2, '2 two', skip=True)
        flow.append(r4, '4a four', args=[1], kwargs={'ar2': 2}, skip=True)
        flow.disp_flows(False)
        flow.run(disp=False)
        self.assertEqual(result, ['r1'])

        # display flows
        with CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                flow.disp_flows(True)
        expect = '''Flows in order:
1  - one (Skipped, enable via -add)
3  - three (Skipped, enable via -add)
2  - two (Skipped, enable via -add)
4a - four (Skipped, enable via -add)
'''
        self.assertTextEqual(p.getvalue(), expect)


def privclass_func(obj):
    """
    Test only func, used by unittest _test_privclass
    """
    obj.priv = 1000


class PrivClassExample(PrivClass):
    """
    Test only class, used by unittest _test_privclass
    """

    def __init__(self, v):
        self.priv = v

    def setpriv(self, v):
        self.priv = v

    def illegal(self, obj, v):      # access another obj private
        obj.priv = v


class PrivClassExample2(PrivClass):
    """
    Test only class, used by unittest _test_privclass
    """
    pass


class PrivClass_Test(TestCase):
    def func(self, c):
        c.priv = 456

    def test_basic(self):
        a = PrivClassExample(111)                  # this should pass
        a.setpriv(10)                              # write via method, this should not assert error
        self.assertEqual(a.priv, 10)               # access test
        self.assertRaises(KeyError, self.func, a)  # write test

        b = PrivClassExample(113)
        self.assertRaises(KeyError, b.illegal, a, 155)

        b.illegal(b, 155)                          # Legal
        self.assertEqual(b.priv, 155)

        self.assertRaises(KeyError, privclass_func, b)    # from a func

        # simple assign
        with self.assertRaises(KeyError):
            b.someattr = 30

        # assign using MockVar
        with MockVar(b, "someattr", 25):
            self.assertEqual(b.someattr, 25)

        # assign using patch
        with patch.object(b, "priv", 26):
            self.assertEqual(b.priv, 26)

    def test_kwargs_privclass(self):
        kwobj = PrivClassExample2(myattr="auto_register")
        self.assertEqual(kwobj.myattr, "auto_register", "Test PrivClass default kwargs auto registering")


class somerandom_class_uses_enum:
    def __init__(self, enum):
        enum.newstate_illegal = 56


class EnumType_Test(TestCase):
    def test_basic(self):
        class EnumTypeCustom(EnumType):
            IDLE = hash('IDLE')
            SHIFTIR = hash('SHIFTIR')
            SHIFTDR = hash('SHIFTDR')

        Tap = EnumTypeCustom()
        # Access

        currentstate = Tap.IDLE
        self.assertEqual(currentstate, Tap.IDLE)
        self.assertNotEqual(currentstate, 0)

        # existence
        self.assertTrue('IDLE' in Tap)
        self.assertFalse('IDLEX' in Tap)

        # reversemap
        self.assertEqual(Tap.reverse_mapping[Tap.IDLE], 'IDLE')
        self.assertEqual(Tap.reverse_mapping[Tap.SHIFTIR], 'SHIFTIR')

        # index_name
        self.assertEqual(Tap.index_name(Tap.IDLE), 'IDLE')
        self.assertEqual(Tap.index_name(Tap.SHIFTIR), 'SHIFTIR')
        self.assertRaisesRegex(ValueError, 'is not a valid enum item for EnumTypeCustom', Tap.index_name, 0)

        # get all states indices
        self.assertItemsEqual({x for x in Tap}, set('IDLE SHIFTIR SHIFTDR'.split()))
        self.assertItemsEqual(list(Tap.keys()), set('IDLE SHIFTIR SHIFTDR'.split()))
        self.assertItemsEqual(Tap.indices(), set(hash(x) for x in 'IDLE SHIFTIR SHIFTDR'.split()))

        # internal state
        self.assertEqual(Tap._dict_all_items, {'IDLE': Tap.IDLE,
                                               'SHIFTIR': Tap.SHIFTIR,
                                               'SHIFTDR': Tap.SHIFTDR})
        self.assertEqual(Tap.reverse_mapping, {Tap.IDLE: 'IDLE',
                                               Tap.SHIFTIR: "SHIFTIR",
                                               Tap.SHIFTDR: "SHIFTDR"})

        # Cannot assign attributes
        with self.assertRaisesRegex(Exception, 'cannot set attributes'):
            Tap.NEWSTATE = 5

        # given the name, return the enum
        self.assertEqual(Tap['IDLE'], Tap.IDLE)
        with self.assertRaisesRegex(ValueError, 'is not a valid enum index for EnumTypeCustom'):
            res = Tap['IDLEX']

        # Check valid
        Tap.check_valid(Tap.IDLE)
        self.assertRaisesRegex(Exception, "is not a valid", Tap.check_valid, 0)

        # duplicate entry
        class Tapx(EnumType):
            IDLE = hash('IDLE')
            SHIFTIR = hash('IDLE')
            SHIFTDR = hash('SHIFTDR')
        with self.assertRaisesRegex(Exception, 'has same value'):
            Tapx()

    def test_compatibility(self):
        # previous version
        Tap = Enum(IDLE=hash('IDLE'),
                   SHIFTIR=hash('SHIFTIR'),
                   SHIFTDR=hash('SHIFTDR'))
        self.run_test(Tap)

        # new version
        class EnumTypeCustom(EnumType):
            IDLE = hash('IDLE')
            SHIFTIR = hash('SHIFTIR')
            SHIFTDR = hash('SHIFTDR')
        Tap1 = EnumTypeCustom()

        self.run_test(Tap1)

    def run_test(self, Tap):
        # Access
        currentstate = Tap.IDLE
        self.assertEqual(currentstate, Tap.IDLE)
        self.assertNotEqual(currentstate, 0)

        # existence
        self.assertTrue('IDLE' in Tap)

        # reversemap
        self.assertEqual(Tap.reverse_mapping[Tap.IDLE], 'IDLE')
        self.assertEqual(Tap.reverse_mapping[Tap.SHIFTIR], 'SHIFTIR')

        # indices
        self.assertItemsEqual(list(Tap.keys()), set('IDLE SHIFTIR SHIFTDR'.split()))
        self.assertItemsEqual(Tap.indices(), set(hash(x) for x in 'IDLE SHIFTIR SHIFTDR'.split()))

        self.assertEqual(Tap.reverse_mapping, {Tap.IDLE: 'IDLE',
                                               Tap.SHIFTIR: "SHIFTIR",
                                               Tap.SHIFTDR: "SHIFTDR"})

        # Cannot assign attributes
        with self.assertRaisesRegex(Exception, 'cannot set attributes'):
            Tap.NEWSTATE = 5

        # given the name, return the enum
        self.assertEqual(Tap['IDLE'], Tap.IDLE)

        # Check valid
        Tap.check_valid(Tap.IDLE)
        self.assertRaisesRegex(Exception, "is not a valid", Tap.check_valid, 0)

    def test_EnumElement(self):
        # Make sure it can be used as keys
        aa = EnumElement("aa")
        bb = EnumElement("bb")
        dd = {aa: 'aaa',
              bb: 'bbb'}
        self.assertEqual(dd[aa], 'aaa')

        # equality - These should not equal bec enum should use original definition!
        aa1 = EnumElement("aa1")
        aa2 = EnumElement("aa1")
        self.assertNotEqual(aa1, aa2)
        self.assertEqual(str(aa1), "EnumElement('aa1')")

        # string
        self.assertEqual('%s' % aa1, "EnumElement('aa1')")


class Enum_Test(TestCase):
    def raiseNotExistsAttrError(self, enum):
        """Wrapper for call to assertRaises to access attribute"""
        statename_5 = enum.statename5

    def raiseAssignAttrError(self, enum):
        """Wrapper for call to assertRaises to access attribute"""
        enum.statename0 = 2

    def raiseAssignKeyError(self, enum):
        """Wrapper for call to assertRaises to access attribute"""
        enum.reverse_mapping[1] = "statename7"

    def raiseKeyError(self, enum, key):
        """Wrapper for call to assertRaises to access attribute"""
        enum.reverse_mapping[key]

    def raiseGetItemKeyError(self, enum, key):
        """Wrapper for call to assertRaises to access attribute"""
        enumrslt = enum[key]

    def test_CreateEnumKeyed(self):
        enum = Enum(statename0=0, statename1=1)
        self.assertEqual(enum.statename1, 1, "Enum dictionary test 1")
        self.assertEqual(enum.statename0, 0, "Enum dictionary test 0")
        self.assertEqual(enum.reverse_mapping[0], "statename0", "Enum dictionary test reverse 0")
        self.assertEqual(enum.reverse_mapping[1], "statename1", "Enum dictionary test reverse 1")
        self.assertRaises(AttributeError, self.raiseNotExistsAttrError, enum)
        self.assertRaises(KeyError, self.raiseKeyError, enum, -1)

    def test_CreateEnumAuto(self):
        enum = Enum('statename0', 'statename1')
        self.assertEqual(enum.statename1, "statename1", "Enum dictionary test 1")
        self.assertEqual(enum.statename0, "statename0", "Enum dictionary test 0")
        self.assertEqual(enum.reverse_mapping['statename0'], "statename0", "Enum dictionary test reverse 0")
        self.assertEqual(enum.reverse_mapping['statename1'], "statename1", "Enum dictionary test reverse 1")
        self.assertRaises(AttributeError, self.raiseNotExistsAttrError, enum)
        self.assertRaises(KeyError, self.raiseKeyError, enum, 3)

    def test_CreateEnumMixedArgs(self):
        enum = Enum('statename0', 'statename1', statename2="4")
        self.assertEqual(enum.statename2, "4", "Enum dictionary test 2")
        self.assertEqual(enum.statename0, "statename0", "Enum dictionary test 0")
        self.assertEqual(enum.reverse_mapping["statename0"], "statename0", "Enum dictionary test reverse 0")
        self.assertEqual(enum.reverse_mapping["statename1"], "statename1", "Enum dictionary test reverse 1")
        self.assertRaises(AttributeError, self.raiseNotExistsAttrError, enum)
        self.assertRaises(KeyError, self.raiseKeyError, enum, 3)

    def test_CreateEnumBytes(self):
        """Functional test to demonstrate enum supports bytes indicies (needed for py3)"""
        enum = Enum(b'state0', b'state1', 'state2', b'state3')
        self.assertEqual(enum[b'state0'], b'state0')        # check bytes reverse maps
        self.assertEqual(enum[b'state1'], b'state1')
        self.assertEqual(enum['state2'], 'state2')          # this key is a str, not bytes
        self.assertEqual(enum[b'state3'], b'state3')

        # check dot lookup works in py3 for str lookup of bytes entries by aliasing them as strings
        self.assertEqual(enum.state0, b'state0')            # bytes enum, visible by string dot lookup
        self.assertEqual(enum.state1, b'state1')
        self.assertEqual(enum.state2, 'state2')             # state2 is a string
        self.assertEqual(enum.state3, b'state3')

        # tests only for py3 - bytes and strings are interchangeable in py2, so these lookups are valid in py2
        # in py3 there is a difference between string and bytes, so only the correct lookup should work
        self.assertRaises(KeyError, self.raiseKeyError, enum, 'state0')     # non-bytes lookup of bytes key should fail
        self.assertRaises(KeyError, self.raiseKeyError, enum, b'state2')    # bytes lookup of str key should fail

    def test_CreateEnumMixedArgsDup(self):
        """Duplicate a key name in the kwargs section"""
        self.assertRaises(AttributeError, Enum, 'statename0', 'statename1', statename0=4)

    def test_CreateandChangeFails(self):
        enum = Enum('statename0', 'statename1', statename2=4)
        self.assertRaises(Exception, self.raiseAssignAttrError, enum)
        self.assertRaises(Exception, self.raiseAssignKeyError, enum, 2)

    def test_GetItem(self):
        # Usual usage:   if state == enum.statename0:
        # now, need the [] if the state string is in a variable.
        enum = Enum('statename0', 'statename1', statename2=4)
        var = 'statename1'
        self.assertEqual(enum[var], var, "Enum getitem dictionary test 1")
        self.assertRaises(KeyError, self.raiseGetItemKeyError, enum, 'statename3')

    def test_Contains(self):
        enum = Enum('statename0', 'statename1', statename2=4)
        self.assertIn('statename0', enum, "Enum contains 'statename0'")
        self.assertNotIn('statename3', enum, "Enum does not contains 'statename3'")

    def test_frominit(self):
        enum = Enum('statename0', 'statename1')
        self.assertRaises(Exception, somerandom_class_uses_enum, enum)

    def test_keys(self):
        enum = Enum('statename0', 'statename1')
        self.assertItemsEqual(list(enum.keys()), set(['statename0', 'statename1']))

    def test_indices(self):
        enum = Enum('statename0', 'statename1')
        self.assertSetEqual(enum.indices(), set(["statename0", "statename1"]))

    def test_invalid_key(self):
        self.assertRaises(TypeError, Enum, 123, "456")   # cannot use integer as a key

    def test_check_valid(self):
        enum = Enum(name0=hash("name0"), name1=hash("name1"))
        enum.check_valid(enum.name0)
        enum.check_valid(enum.name1)
        self.assertRaises(Exception, enum.check_valid, "name0")
        self.assertRaises(Exception, enum.check_valid, 22)

        enum = Enum("name0", "name1")
        enum.check_valid(enum.name0)
        enum.check_valid(enum.name1)
        self.assertRaises(Exception, enum.check_valid, 1)


class TagOnce_Test(TestCase):
    def test_once(self):
        ar = [1, 2, 3, 1, 2, 1, 4, 1]
        res = []
        once = TagOnce()
        for i in ar:
            if once(i):
                res.append(i)
        self.assertEqual(res, [1, 2, 3, 4])


class OptArg_Test(TestCase):
    def test_optarg(self):

        # Create a mock object
        class Mock_Parseobj:
            def __init__(self):
                self.arg1 = 123
                self.arg2 = []
                self.arg3 = None

        opt = Mock_Parseobj()
        OPT.initialize(opt)
        self.assertEqual(OPT.arg1, 123)
        self.assertEqual(OPT['arg1'], 123)
        self.assertIs(OPT.arg3, None, "Must be none")
        self.assertTrue(OPT.arg1)
        self.assertFalse(OPT.argxnotex)
        self.assertEqual(dict(OPT), {'arg1': 123, 'arg2': [], 'arg3': None})

    def test_not_in_dict(self):
        self.assertIs(OPT.MissingArgs, None)
        self.assertIs(OPT['MissingArgs'], None)
        self.assertFalse('MissingArgs' in OPT, "should not exist")  # it should not add it

    def test_from_sysargv(self):
        with MockVar(sys, "argv", 'myscript.py -arg1 value2 -arg2'.split()):
            self.assertTrue(OPT.from_sysargv_exist("arg1"))
            self.assertTrue(OPT.from_sysargv_exist("arg2"))
            self.assertFalse(OPT.from_sysargv_exist("arg3"))

            self.assertEqual(OPT.from_sysargv_key("arg1"), 'value2')
            self.assertIs(OPT.from_sysargv_key("arg2"), None)
            self.assertIs(OPT.from_sysargv_key("arg3"), None)

    def test_attr(self):
        opt = OptArgs()
        opt.key1 = 12
        opt['key2'] = 13
        opt.TAOBJ_set('at1', 14)
        opt.TAOBJ_set('at2', 15)
        self.assertEqual(opt, {'key1': 12, 'key2': 13})
        self.assertEqual(opt.TAOBJ_get('at1'), 14)
        self.assertEqual(opt.TAOBJ_get('at2'), 15)
        self.assertIs(opt['at1'], None)
        self.assertIs(opt.at1, None)
        self.assertIs(opt.TAOBJ_get('key1'), None)

        # clear
        opt.clear()
        self.assertEqual(opt, {})
        self.assertIs(opt.TAOBJ_get('at1'), None)
        self.assertIs(opt.TAOBJ_get('at2'), None)

    def test_deepcopy(self):
        opt = OptArgs()
        opt.val1 = "abc"
        opt.val2 = [1, 2]
        opt.val3 = {'a': 123}
        opt2 = opt.OPT_deepcopy()
        opt2.val2.append(3)
        opt2.val3['b'] = 456

        self.assertEqual(opt, {'val3': {'a': 123},
                               'val2': [1, 2],
                               'val1': 'abc'})

        self.assertEqual(opt2, {'val3': {'a': 123,
                                         'b': 456},
                                'val2': [1, 2, 3],
                                'val1': 'abc'})

    def test_check_vmv(self):
        opt = OptArgs()

        # raise exception
        import gadget.shell as shell
        with MockVar(shell, "CALLERBIN", "/path/bin/make_pattern.py"):
            with self.assertRaisesRegex(Exception, "is being accessed but"):
                print(opt.vrev)

        # unittest
        print(opt.vrev)

        opt.something = False
        self.assertIsNone(opt.vrev)

    # Note: Cannot pickle Opt object because of None
#    def test_pickle(self):
#        OPT.myval = 23
#        p = pickle.dumps(OPT, protocol=VEP_PKL_PROTOCOL)  # should not error out
#        cc = pickle.loads(p)               # should not error out
#        self.assertEqual(cc.myval, 23)
#        self.assertEqual(cc['myval'], 23)


class Increment_Test(TestCase):
    def test_increment(self):
        obj = Increment()
        self.assertEqual(obj(), 1)
        self.assertEqual(obj(), 2)
        self.assertEqual(obj(), 3)
        self.assertEqual(obj.val(), 3)

    def test_increment10(self):
        obj = Increment(step=10, start=2)
        self.assertEqual(obj.val(), 2)
        self.assertEqual(obj(), 12)
        self.assertEqual(obj(), 22)
        self.assertEqual(obj(), 32)
        self.assertEqual(obj.val(), 32)


class ConfigAssign_Test(TestCase):

    def test_configassign(self):

        class ValuesDef(ConfigAssign):
            def gd1(self, Values, v):
                Values.traceprefix.d = v('Debug', 'Debug')
                Values.traceprefix.g = v('Golden', 'Golden')

            def prod1(self, Values, v):
                Values.testfamily.H = v('HSW', 'Haswell')
                Values.testfamily.X = v('DBG', 'Debug')
                Values.testfamily.P = v('HSW-PSMI', 'Haswell PMSI')

            def DEFINE(self):
                Values = TVPVConfigDict()
                v = NamedSeq('full', 'HR')
                self.args = [Values, v]

        Values, v = ValuesDef().RUN()
        self.assertEqual(Values.traceprefix.d.full, 'Debug')
        self.assertEqual(Values.traceprefix.g.HR, 'Golden')
        self.assertEqual(Values.testfamily.H.full, 'HSW')
        self.assertEqual(Values.testfamily.P.HR, 'Haswell PMSI')

    def test_error_checks(self):

        class ValuesDef1(ConfigAssign):
            def gd1(self, Values, v):
                Values.traceprefix.d = v('Debug', 'Debug')

        class ValuesDef2(ConfigAssign):
            def gd1(self, Values, v):
                Values.traceprefix.d = v('Debug', 'Debug')

            def DEFINE(self):
                Values = TVPVConfigDict()

        class ValuesDef3(ConfigAssign):
            def gd1(self, Values, v):
                Values.traceprefix.d = v('Debug', 'Debug')

            def DEFINE(self):
                Values = TVPVConfigDict()
                self.args = "string"

        self.assertRaisesRegex(Exception, r"ValuesDef1\(\) class", ValuesDef1)  # DEFINE missing
        self.assertRaisesRegex(Exception, "args attribute is not defined", ValuesDef2)  # self.args missing
        self.assertRaisesRegex(Exception, "args attribute is not a list", ValuesDef3)  # self.args is not a list

    def test_direct_to_var(self):
        # Pass case ===================
        @ConfigAssign.direct_to_var()
        class vrev(ConfigAssign):
            def DEFINE(self):
                self.args = [TVPVConfigDict()]

            def gd_prod_agnostic(self, vrev):
                v = vrev.vrevPQ3
                v.description = '1st silicon vrev'
                v.valid = True

        self.assertEqual(vrev.vrevPQ3.description, '1st silicon vrev')

        # Fail case: user forgot () ====================
        with self.assertRaisesRegex(Exception, "must be called as a function"):
            @ConfigAssign.direct_to_var
            class vrev2(ConfigAssign):
                pass

        # Fail case: user forgot ConfigAssign inherit ====================
        with self.assertRaisesRegex(Exception, "ConfigAssign classes"):
            @ConfigAssign.direct_to_var()
            class vrev3:
                pass

        # Fail case: with arguments 1 ====================
        with self.assertRaisesRegex(Exception, "must not have any arguments"):
            @ConfigAssign.direct_to_var(None)
            class vrev4(ConfigAssign):
                pass

        # Fail case: with arguments 2 ====================
        with self.assertRaisesRegex(Exception, "must not have any arguments"):
            @ConfigAssign.direct_to_var(1, 2)
            class vrev5(ConfigAssign):
                pass

    def test_ConfigAssignDict(self):
        @ConfigAssignDict.direct_to_var()
        class rty(ConfigAssignDict):
            def somevar(self, rty):
                rty.abcd = 123
                rty.ghij = 45

        self.assertEqual(rty.abcd, 123)

        # Confirm auto_off
        with self.assertRaises(AttributeError):
            rty.newk.ppp = 444

    def test_AssignDict(self):
        @AssignDict.direct_to_var()
        class rty(AssignDict):
            def mode1(self, cfg):
                cfg.abcd = 123
                cfg.ghij = 45

            def vectype1(self, cfg):
                cfg.abcd = 221
                cfg.ghi.jkl = 46

        self.assertEqual(rty, {'mode1': {'abcd': 123, 'ghij': 45},
                               'vectype1': {'abcd': 221, 'ghi': {'jkl': 46}},
                               })

        # Confirm auto_off
        with self.assertRaises(AttributeError):
            rty.newk.ppp = 444


class OnceADay_Test(TestCase):
    def test_basic(self):
        # initial false
        aa = OnceADay(3)
        self.assertEqual(aa(2), False)
        self.assertEqual(aa(3), True)
        self.assertEqual(aa(3), False)
        self.assertEqual(aa(3), False)
        self.assertEqual(aa(4), False)
        self.assertEqual(aa(5), False)
        self.assertEqual(aa(3), True)
        self.assertEqual(aa(3), False)

        # initial true
        aa = OnceADay(3)
        self.assertEqual(aa(3), True)
        self.assertEqual(aa(3), False)
        self.assertEqual(aa(3), False)
        self.assertEqual(aa(4), False)
        self.assertEqual(aa(3), True)
        self.assertEqual(aa(3), False)
        self.assertEqual(aa(4), False)

        # > 24 hr elapsed
        aa = OnceADay(3)
        aa.time = time.time() - 95000
        self.assertEqual(aa(5), True)
        self.assertEqual(aa(5), False)
        self.assertEqual(aa(3), True)

        # > 24 hr elapsed
        aa = OnceADay(3)
        aa.time = time.time() - 95000
        self.assertEqual(aa(3), True)
        self.assertEqual(aa(3), False)
        self.assertEqual(aa(3), False)

        # default time
        aa = OnceADay(30)
        self.assertEqual(aa(), False)   # will always be false


class ContextList_Test(TestCase):

    def test_basic(self):
        obj = {'abc': 123, 'ghi': 456}
        c_list = [MockVar(obj, 'abc', 999),
                  MockVar(obj, 'ghi', 888)]
        self.assertEqual(obj, {'abc': 123, 'ghi': 456})
        with ContextList(*c_list):
            self.assertEqual(obj, {'abc': 999, 'ghi': 888})
        self.assertEqual(obj, {'abc': 123, 'ghi': 456})


class ContextLog_Test(TestCase):
    def test_basic(self):
        val = [0]

        class UT1(ContextLog):
            def close(self):
                val[0] = 111

        # normal case
        with UT1():
            val[0] = 222

        self.assertEqual(val[0], 111)   # close must be called

        from gadget.pylog import log
        # This will allow the MockVar(sys, "stdout", StringIO() to work even
        # if veplog is instantiated before. Anywhere else - please use Capture CaptureStdoutLog()
        log.set_log_methods_to_print()
        # exception occurred
        with MockVar(sys, "stdout", StringIO()) as p:
            with self.assertRaisesRegex(Exception, "Hi there"):
                with UT1():
                    raise Exception("Hi there 78")
        self.assertIn("Exception Occurred within UT1 block: Hi there 78", p.getvalue())

        # exit(0)
        with MockVar(sys, "stdout", StringIO()) as p:
            with self.assertRaises(SystemExit):
                with UT1():
                    exit(0)
        self.assertEqual(p.getvalue().strip(), "")   # should be empty

        # class without close
        class UT2(ContextLog):
            pass
        with self.assertRaisesRegex(Exception, "must be implemented"):
            with UT2():
                pass


class Assign_Test(TestCase):
    def test_basic(self):
        aa = TVPVConfigDict()
        with Alias(aa.vrev) as v:
            v.name = "PQ9"
            v.id = 123
            self.assertEqual(aa.vrev.name, "PQ9")
            self.assertEqual(aa.vrev.id, 123)
        self.assertEqual(aa.vrev.name, "PQ9")
        self.assertEqual(v.name, "PQ9")


class EmptyContext_Test(TestCase):
    def test_basic(self):
        with EmptyContext() as e:
            self.assertIsNotNone(e)


@unittest.skipIf(IS_WIN, 'unix only due no SIGALRM in windows')
class Timeout_Tests(TestCase):

    def test_basic(self):
        # value based timeout - template
        def get_tuple(iter):    # a generic routine, say give tuple number
            class MyExcept(Exception):
                pass

            try:
                with Timeout(1, MyExcept):    # handler must raise exception
                    for i in range(iter):   # let's say the code got stuck
                        _ = {i: i}
                    return iter
            except MyExcept:
                return -1

        self.assertEqual(get_tuple(200000000), -1)
        self.assertEqual(get_tuple(100), 100)

    @unittest.skipIf(*is_ut_option('SLOW', message="timeout tests"))   # change message to right one
    def test_alarms(self):
        class MyExcept(Exception):
            pass

        # pass case, alarm will not trigger
        with Timeout(1, Exception):
            for i in range(10):
                pass

        # run again
        with Timeout(1, Exception):
            for i in range(10):
                pass

        # one alarm
        with self.assertRaises(SystemExit):
            with Timeout(1, SystemExit):
                for i in range(200000000):
                    _ = {i: i}
                self.fail("Timeout did not happen (one alarm)")

        # two embedded alarms, outer timeout
        with self.assertRaises(SystemExit):
            with Timeout(4, SystemExit):
                with Timeout(2, MyExcept):
                    for i in range(10):
                        time.sleep(0.1)
                        pass
                for i in range(200000000):
                    time.sleep(1)
                    pass
                self.fail("Timeout did not happen (two embedded alarms, outer timeout)")

        # two emebedded alarms, inner timeout
        with self.assertRaises(SystemExit):
            with Timeout(2, MyExcept):
                with Timeout(1, SystemExit):
                    for i in range(200000000):
                        _ = {i: i}
                self.fail("Timeout did not happen (two emebedded alarms, inner timeout)")


class MultiReturn_Tests(TestCase):

    def test_basic(self):
        class UT1:
            def foo(self, arg):
                return "realvalue %s" % arg

        with MockVar(UT1, "foo", Mock(side_effect=MultiReturn(1, 2))):
            self.assertEqual(UT1().foo(1), 1)
            self.assertEqual(UT1().foo(1), 2)
            self.assertRaisesRegex(ValueError, "exceeded the input values", UT1().foo)

        self.assertEqual(UT1().foo(1), "realvalue 1")

        with MockVar(UT1, "foo", Mock(side_effect=MultiReturn(*range(3)))):
            self.assertEqual(UT1().foo(), 0)
            self.assertEqual(UT1().foo(1, rt=25), 1)
            self.assertEqual(UT1().foo(1), 2)


class Capture_Tests(TestCase):

    def test_stdout(self):
        a = CaptureStdout()
        self.assertEqual(a._obj, sys)
        self.assertEqual(a._attr, "stdout")

        with MockVar(sys, "stdout", StringIO()) as outp:
            print("outside print1")
            with CaptureStdout() as inp:
                print("Hello")
                print("There")
            print("outside print2")

        self.assertEqual(inp.getvalue(), 'Hello\nThere\n')
        self.assertEqual(outp.getvalue(), 'outside print1\noutside print2\n')

    def test_stderr(self):
        a = CaptureStderr()
        self.assertEqual(a._obj, sys)
        self.assertEqual(a._attr, "stderr")

        with MockVar(sys, "stderr", StringIO()) as outp:
            sys.stderr.write("outside print1")
            with CaptureStderr() as inp:
                sys.stderr.write("Hello")
            sys.stderr.write("outside print2")

        self.assertEqual(inp.getvalue(), 'Hello')
        self.assertEqual(outp.getvalue(), 'outside print1outside print2')


class SysExceptionManager_Test(TestCase):

    def test_fake(self):
        with MockVar(sys, "excepthook", Mock()):
            res = []

            def foo(etype, value, tb):
                res.append(1)
            obj = SysExceptionManager()
            obj.register(foo)

            with MockVar(sys, "__excepthook__", Mock()):
                obj.execute_hooks(Exception, [""], None)
                self.assertEqual(res, [1])

            with MockVar(sys, "__excepthook__", Mock()):
                obj.execute_hooks(ErrorUser, [""], None)
                self.assertEqual(res, [1, 1])

    def test_real(self):
        code = f'''
import sys
sys.path.insert(0, r'{ROOT_ENV}')
from gadget.helperclass import vepExceptionManager
def foo1(etype, value, tb):
    print("1_AM_CALLED")
def foo2(etype, value, tb):
    print("2_AM_CALLED")
vepExceptionManager.register(foo1)
vepExceptionManager.register(foo2)
raise ValueError("SOME_MESSAGE")
        '''
        with TempName(exe=code, name=True) as tn, \
                MockVar(os.environ, 'PYTHONPATH', ROOT_ENV):
            ecode, sout, serr = SystemCall(tn, exe=True).run_sout_serr()
            print(serr)
            self.assertIn('1_AM_CALLED', sout)
            self.assertIn('2_AM_CALLED', sout)
            self.assertIn('SOME_MESSAGE', serr)

    def test_newline_end(self):
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV):
            # test newline at end after exception
            cmd = f'''{sys.executable} -c "from gadget.errors import ErrorUser; raise ErrorUser('LINE1', 'LINE2')" '''
            _, out = SystemCall(cmd).run_outtxt()

            expect = ['ErrorUser:    <<< Error Type',
                      '=+',
                      'Error:      LINE1',
                      'Suggestion: LINE2',
                      r'ErrorSig:   \w\w\w \S+ \S+ lno#1',
                      'Rundir:     ',
                      '=+']
            self.assertRegexpEachList(out.split('\n'), expect)

            # test newline at end after exception
            cmd = f'''{sys.executable} -c "from gadget.errors import ErrorInput; raise ErrorInput('LINE1', 'LINE2')" '''
            _, out = SystemCall(cmd).run_outtxt()
            expect = ['Traceback (most recent call last):',
                      r'  File \S+, line 1, in <module>',
                      'ErrorInput:    <<< Error Type',
                      '=+',
                      'Error:      LINE1',
                      'Suggestion: LINE2',
                      r'ErrorSig:   \w\w\w \S+ \S+ lno#1',
                      r'Rundir:\s+\S*',
                      '=+']
            self.assertRegexpEachList(trim_traceback_without_code(out), expect)


class CaptureStdoutLog_Tests(TestCase):

    def test_basic(self):
        """
        Test basic CaptureStdout-like functionality
        """
        a = CaptureStdoutLog()
        self.assertEqual(a._obj, sys)
        self.assertEqual(a._attr, "stdout")

        # disp=False
        with MockVar(sys, "stdout", StringIO()) as outp:
            print("outside print1")
            with CaptureStdoutLog(disp=False) as inp:
                print("Hello")
                print("There")
            print("outside print2")

        self.assertEqual(inp.getvalue(), 'Hello\nThere\n')
        self.assertEqual(outp.getvalue(), 'outside print1\noutside print2\n')

        # disp=True (default)
        with MockVar(sys, "stdout", StringIO()) as outp:
            print("outside print1")
            with CaptureStdoutLog() as inp:
                print("Hello")
                print("There")
            print("outside print2")

        self.assertEqual(inp.getvalue(), 'Hello\nThere\n')
        self.assertEqual(outp.getvalue(), 'outside print1\nHello\nThere\n\noutside print2\n')

        # disp=True, with Exception
        with MockVar(sys, "stdout", StringIO()) as outp:
            print("outside print1")
            with self.assertRaisesRegex(Exception, "Wrong"):
                with CaptureStdoutLog() as inp:
                    print("Hello")
                    raise Exception("SomethingWrong")
                    print("There")
            print("outside print2")

        self.assertEqual(inp.getvalue(), 'Hello\n')
        self.assertEqual(outp.getvalue(), 'outside print1\nHello\n\noutside print2\n')

    def test_stdoutlog(self):
        """
        Test capturing stdout+log stdout output without having to redirect the log in/out
        of the context (normally log.stdout() would redirect the log to p)
        """
        from gadget.pylog import log
        with MockVar(sys, "stdout", StringIO()) as outp:
            # Must be inside Mockvar(..stdout) ...
            log.stdout("DEBUG")
            print("outside print1")
            log.info("inf1")
            with CaptureStdoutLog() as inp:
                log.debug("debug1")
                print("Hello")
                print("There")
            log.info("inf2")
            print("outside print2")
        self.assertIn("Hello\nThere\n", inp.getvalue())
        self.assertIn("debug1", inp.getvalue())
        self.assertNotIn("inf1", inp.getvalue())
        self.assertNotIn("inf2", inp.getvalue())
        self.assertIn('outside print1\n', outp.getvalue())
        self.assertIn('outside print2\n', outp.getvalue())
        self.assertIn('inf1', outp.getvalue())
        self.assertIn('inf2', outp.getvalue())

    def test_filelog(self):
        """
        Test not affecting file redirection
        """
        from gadget.files import tempname
        from gadget.pylog import log
        logfile = tempname()
        with MockVar(sys, "stdout", StringIO()) as outp:
            # Must be inside Mockvar(..stdout) ...
            log.file(logfile, "DEBUG")
            log.s_stdout = False
            print("outside print1")
            log.info("inf1")
            with CaptureStdoutLog() as inp:
                log.debug("debug1")
                print("Hello")
                print("There")
            log.info("inf2")
            print("outside print2")

        log.close()
        logout = File(logfile + ".gz").read()
        # print logout
        print(outp.getvalue())
        print(inp.getvalue())
        self.assertIn("Hello\nThere\n", inp.getvalue())
        self.assertNotIn("debug1", inp.getvalue())
        self.assertNotIn("inf1", inp.getvalue())
        self.assertNotIn("inf2", inp.getvalue())
        self.assertIn('outside print1\n', outp.getvalue())
        self.assertIn('outside print2\n', outp.getvalue())
        self.assertNotIn('inf1', outp.getvalue())
        self.assertNotIn('inf2', outp.getvalue())
        self.assertIn('inf1', logout)
        self.assertIn('inf2', logout)
        remove(logfile + ".gz")


class CheckMounts_Test(TestCase):

    def test_check_pylib(self):
        # fail case - Exception occurred
        with MockVar(os, "listdir", Mock(side_effect=Exception)):
            with self.assertRaises(SystemExit) as cm:
                CheckMounts()
            self.assertEqual(cm.exception.code, 101)

        # fail case numpy does not exist
        with MockVar(os, "listdir", Mock(return_value=[])):
            with self.assertRaises(SystemExit) as cm:
                CheckMounts()
            self.assertEqual(cm.exception.code, 101)


class is_ut_Tests(TestCase):

    def test_basic(self):
        self.assertTrue(IS_UT)

        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV):
            # not unittest case
            cmd = f'''{sys.executable} -c 'from gadget.helperclass import IS_UT; print(IS_UT)' '''
            _, out = SystemCall(cmd).run_outtxt()
            self.assertEqual(out, 'False')

    def test_is_ut_unittest(self):
        # Add test cases here per IDE

        # unix version
        with MockVar(sys, 'argv', ['gadget/test/test_helperclass.py', '-v', '-b', 'is_ut_Tests.test_is_ut_unittest']):
            self.assertEqual(is_ut(), True)

        # windows version
        with MockVar(sys, 'argv', ['C:/Program Files/JetBrains/PyCharm',
                                   '2025.1.1.1/plugins/python-ce/helpers/pycharm/_jb_unittest_runner.py']):
            self.assertEqual(is_ut(), True)

        # pytest version, mock sys to skip unix case
        with MockVar(sys, 'argv', ['gadget/test/fake_test_helperclass.py', '-v', '-b', 'is_ut_Tests.test_is_ut_unittest']):
            with patch.dict(os.environ, {"PYTEST_CURRENT_TEST": "1"}):
                self.assertEqual(is_ut(), True)

        # normal version
        with MockVar(sys, 'argv', ['main/nvl_buildtp.py', 'something']):
            self.assertEqual(is_ut(), False)


class RunLater_Test(TestCase):

    def test_basic(self):
        data = []
        park = RunLater()
        park(data.append, 1)
        park(data.append, 2)
        data.append(3)
        park.run()
        self.assertEqual(data, [3, 1, 2])

    def test_scope(self):
        park = RunLater()
        gdata = []

        def foo():
            data = [1, 2, 3]
            park(data.append, 4)
            park(gdata.extend, data)

        foo()
        park.run()  # at this point, data does not exist anymore
        self.assertEqual(gdata, [1, 2, 3, 4])

    def test_kwargs(self):
        park = RunLater()
        result = []

        def foo(data1=1, data2=2):
            result.append(data1)
            result.append(data2)
        park(foo, 11, 12)
        park(foo, data1=13, data2=14)
        park(foo, 15, data2=16)
        park(foo, data1=17)
        park(foo, data2=18)
        park(foo, 19)
        park.run()
        self.assertEqual(result, [11, 12, 13, 14, 15, 16, 17, 2, 1, 18, 19, 2])


class AutoRestart_Test(TestCase):

    def validation(self):
        # manual validation test of AutoRestart(). Run this in unix and in windows.
        from gadget.helperclass import AutoRestart
        from gadget.strmore import curtime

        print("At top of file")
        AutoRestart('res')    # main call

        # main loop
        print("in main loop")
        for idx in range(1000):
            AutoRestart()
            print(f"{idx} I am sleeping {curtime()}")
            time.sleep(1)
            print(f"{idx} I am sleeping {curtime()}")
            time.sleep(1)
        exit(0)

    def test_get_py_files(self):
        # independent unittest for get_py_files()
        result = list(AutoRestart.get_py_files())
        print("List of imported pytpd modules: ========")
        print(f"Count: {len(result)}")
        pprint(result)
        self.assertGreater(len(result), 15)
        self.assertLess(len(result), 25)            # Inspect result, if this fails
        self.assertEqual(result[0], os.path.abspath(sys.argv[0]))    # special - self

        # unittest case with sys.argv is Mocked
        with MockVar(sys, "argv", [f'{ROOT_ENV}/main/blah.py']):
            result = list(AutoRestart.get_py_files())
        self.assertGreater(len(result), 15)
        self.assertLess(len(result), 25)            # Inspect result, if this fails
        self.assertEqual(result[0], os.path.abspath(sys.argv[0]))    # special - self

    def test_aa_sentinel(self):
        AutoRestart._sleeptime = 0   # So that unittest is fast

        # case1: Call script with output
        envname = 'AUTORS_TEST_HELPERCLASS_PY'
        AutoRestart._flushtime = 0
        self.assertNotIn(envname, os.environ)    # Make sure this does not exist
        with TempDir(name=True) as tdir:
            called = []

            def fake_run(slf):      # This is the child script
                called.append(slf.cmd)
                return ["Hello", "There"]

            with MockVar(SystemCall, 'run_stream', fake_run), \
                    MockVar(os.environ, envname, MockVar.delete), \
                    MockVar(AutoRestart, '_maxloop', 1):
                obj = AutoRestart(f'{tdir}/log.txt')    # Sentinel
                self.assertIn(envname, os.environ)

            # check output
            result = [x for x in File(f'{tdir}/log.txt').chomp() if 'Sentinel version' not in x]
            self.assertEqual('\n'.join(result), 'Hello\nThere')

            print('Called arg')
            print(called)
            self.assertEqual(len(called), 1)
            self.assertEqual(called[0][0], sys.executable)

        # case2: Call script without output
        called = []
        AutoRestart._flushtime = 1
        with MockVar(SystemCall, 'run_stream', fake_run), \
                MockVar(os.environ, envname, MockVar.delete), \
                MockVar(AutoRestart, '_maxloop', 2):
            obj = AutoRestart()    # Sentinel
            self.assertIn(envname, os.environ)

        # check output
        print('Called arg')
        print(called)
        self.assertEqual(len(called), 2)
        self.assertEqual(called[0][0], sys.executable)

    def test_maincaller(self):
        envname = 'AUTORS_TEST_HELPERCLASS_PY'
        self.assertEqual(len(AutoRestart._mtimes), 0)      # must not be initialized

        # case1: no restart
        with MockVar(os.environ, envname, 'somevalue'), \
                MockVar(AutoRestart, 'main_sentinel', Mock(side_effect=Exception)):   # this must not be called
            AutoRestart()    # main call, this calls initialize
            AutoRestart()    # call again - no change
            self.assertGreater(len(AutoRestart._mtimes), 5)

        # case2: with restart, one of the python files were updated
        for item in AutoRestart._mtimes:
            last = item
        AutoRestart._mtimes[last] = 1
        with MockVar(os.environ, envname, 'somevalue'), \
                MockVar(AutoRestart, 'main_sentinel', Mock(side_effect=Exception)):   # this must not be called
            with self.assertRaises(SystemExit):
                AutoRestart()    # main call


class NoneLike_Test(TestCase):

    def test_bool(self):
        nonelike = NoneLikeClass()
        self.assertEqual(bool(nonelike), False)
        self.assertFalse(nonelike)

        if nonelike:
            self.fail('Error: nonelike should be false')

        abc = nonelike
        self.assertTrue(abc is nonelike)

        self.assertTrue(is_none(nonelike))
        self.assertTrue(is_none(abc))
        self.assertTrue(is_none(None))
        self.assertFalse(is_none(''))


class Misc_Tests(TestCase):

    @unittest.skipIf(is_cov(), 'No need for coverage')
    def test_is_cov1(self):
        self.assertFalse(is_cov())

    @unittest.skipIf(not is_cov(), 'CoverageOnly')
    def test_is_cov2(self):
        self.assertTrue(is_cov())


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
