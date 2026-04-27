#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for dictmore.py
"""
import setenv_unittest     # must be first import for unittests
from gadget.dictmore import *
from gadget.ut import TestCase, unittest
from gadget.files import TempName, TempDir, File
from collections import OrderedDict
from configparser import MissingSectionHeaderError
from os.path import join
import pickle as pickle
import marshal
import gadget.dictmore as dictmore
from xml.etree import cElementTree as ElementTree


class DictConfig_tests(TestCase):

    def test_init(self):
        d = DictConfig(int)
        d.a += 1
        self.assertEqual(d['a'], 1)

    def test_basic1(self):
        d = TVPVConfigDict()
        d.c = 123
        d['d'] = 456

        self.assertEqual(d['c'], 123)
        self.assertEqual(d.c, 123)
        self.assertEqual(d.d, 456)
        self.assertEqual(d['d'], 456)

    def test_basic2(self):
        d = TVPVConfigDict()
        d.c.cc.ccc = ['KU', 'KUKU']
        d.c.cc.ccc.append('KUKUKU')
        d['b'] = 'KU'

        self.assertEqual(len(list(d.items())), 2)
        self.assertEqual(len(d.c.cc.ccc), 3)
        self.assertEqual(len(d['c']['cc']['ccc']), 3)
        self.assertEqual(list(d.keys()), ['c', 'b'])

    def test_AUTO_OFF(self):
        d = TVPVConfigDict()
        d.c.cc.ccc = ['KU', 'KUKU']
        d.AUTO_OFF()
        self.assertRaises(AttributeError, lambda x: x.d.more, d)    # immediate node
        self.assertRaises(AttributeError, lambda x: x.c.cc.ddd, d)  # deep node

        # re-execute
        d.AUTO_OFF()
        self.assertRaises(AttributeError, lambda x: x.d.more, d)    # immediate node

        d = TVPVConfigDict()
        d.a.aa.aaa = 123
        d.b.bb.bbb = "123"
        d.AUTO_OFF()
        self.assertRaises(AttributeError, lambda x: x.b.cc, d)
        self.assertEqual(d.a.aa.aaa, 123)

        # reassign - must still fail
        def foo(darg):
            darg.a.aa.aaa = 456
        self.assertRaises(KeyError, foo, d)

    def test_dupok(self):
        d = TVPVConfigDict()
        d.c.cc.ccc = ['KU', 'KUKU']
        d.c.cc.ccc.append('KUKUKU')
        d['b'] = 'KU'
        d['b'] = 'KU1'   # this is ok
        d['b'] = 'KU1'
        d.b = 'KU1'
        self.assertEqual(list(d.keys()), ['c', 'b'])

    def test_repr(self):
        d = TVPVConfigDict()
        d.a = 123
        d.b = '456'
        d.c.a = [1, 2]
        d.c.b = {3, 4}
        print(d)
        self.assertEqual(d.PRETTY(), "a = 123\nb = '456'\nc.a = [1, 2]\nc.b = {3, 4}")
        self.assertEqual(d, {'a': 123, 'c': {'a': [1, 2], 'b': {3, 4}}, 'b': '456'})
        self.assertEqual(eval(repr(d)), {'a': 123, 'c': {'a': [1, 2], 'b': {3, 4}}, 'b': '456'})

        d = TVPVConfigDict()
        d.a = {'y': 123}
        d.b = '456'
        d.c.a.z = [1, 2]
        d.c.b = {3, 4}
        print(d)
        self.assertEqual(d.PRETTY(), "a = {'y': 123}\nb = '456'\nc.a.z = [1, 2]\nc.b = {3, 4}")
        self.assertEqual(d, {'a': {'y': 123}, 'c': {'a': {'z': [1, 2]}, 'b': set([3, 4])}, 'b': '456'})
        self.assertEqual(eval(repr(d)), {'a': {'y': 123}, 'c': {'a': {'z': [1, 2]}, 'b': set([3, 4])}, 'b': '456'})

        self.assertEqual(sorted(x[0] for x in d._recursedict()), ['a', 'b', 'c.a.z', 'c.b'])
        self.assertEqual(sorted(repr(x[1]) for x in d._recursedict()), ["'456'", '[1, 2]', "{'y': 123}", '{3, 4}'])

    def test_ErrorReassign(self):
        def shoulderror1():
            d = TVPVConfigDict()
            d.vrevPA1.mode = 123
            d.vrevPA1.mode = 456    # reassign

        def shoulderror2():
            d = TVPVConfigDict()
            d.vrevPA1.mode = {1, 2, 3}
            d.vrevPA1.vectype = 123
            d.vrevPA1.mode = 456    # reassign

        # Below testcase cannot be caught by reassign-check, since _config is not set at .vrevPA1
        def noerror3():
            d = TVPVConfigDict()
            d.vrevPA1.mode = 123
            d.vrevPA1 = 'overwrite'  # reassign

        def shoulderror4():
            z = TVPVConfigDict()
            z.vrevPA1.vectype = 123
            z.vrevPA1.mode = {1, 2, 3}

            d = TVPVConfigDict()
            d.vrevPA1.vectype = 123
            d.vrevPA1.mode = [z.vrevPA1, z.vrevPA1.mode]
            d.vrevPA2.SAME_AS(d.vrevPA1)
            d.vrevPA1.mode = [z.vrevPA1, z.vrevPA1.vectype]

        self.assertRaises(KeyError, shoulderror1)
        self.assertRaises(KeyError, shoulderror2)
        noerror3()
        self.assertRaises(KeyError, shoulderror4)

    def test_inquiry_noerror(self):
        d = TVPVConfigDict()
        d.vrevPA1 = 123
        res = len(d.vrevPA2)
        self.assertEqual(res, 0)
        d.vrevPA2 = "abc"
        self.assertEqual(d.vrevPA2, "abc")

        d.vrevPA2 = "abc"   # should not error, same value

    def test_SAME_AS_basic(self):
        VREV = TVPVConfigDict()
        VREV.vrevPA0.vectype.sdr = 1
        VREV.vrevPA0.vectype.tbm = 2
        VREV.vrevPA0.vectype.ddr = 3
        VREV.vrevPA1.prune = 'PA1 prune'
        VREV.vrevPA1.mode = {"8m2m", "misc"}
        VREV.vrevPA1.vectype.SAME_AS(VREV.vrevPA0.vectype)
        VREV.vrevPA2.SAME_AS(VREV.vrevPA1)
        VREV.vrevPA2.mode = {"newmode"}
        VREV.vrevPA3.SAME_AS(VREV.vrevPA2)
        VREV.vrevPA3.bb = 'A'
        VREV.vrevPA4.SAME_AS(VREV.vrevPA3)

        vrevPA4 = VREV.vrevPA4
        print(vrevPA4)
        self.assertEqual(vrevPA4.PRETTY(), "bb = 'A'\nmode = {'newmode'}\nprune = 'PA1 prune'\nvectype.ddr = 3\nvectype.sdr = 1\nvectype.tbm = 2")

    def test_SAME_AS_more(self):
        VREV = TVPVConfigDict()
        VREV.vrevPA0.vectype.sdr = [0, 1, 2]
        VREV.vrevPA1.vectype.SAME_AS(VREV.vrevPA0.vectype)
        self.assertEqual(recurse2dict(VREV.vrevPA1), {'vectype': {'sdr': [0, 1, 2]}})  # 2nd level

        VREV = TVPVConfigDict()
        VREV.vrevPA0.vectype.sdr = [0, 1, 2]
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        self.assertEqual(recurse2dict(VREV.vrevPA1), {'vectype': {'sdr': [0, 1, 2]}})  # top level
        self.assertEqual(recurse2dict(VREV.vrevPA0), {'vectype': {'sdr': [0, 1, 2]}})  # no SAME_AS

        VREV = TVPVConfigDict()
        VREV.vrevPA0.vectype.sdr = [0, 1, 2]
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0.vectype)
        self.assertEqual(recurse2dict(VREV.vrevPA1), {'sdr': [0, 1, 2]})     # different level

        VREV = TVPVConfigDict()
        VREV.vrevPA0.vectype.sdr = 123
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        VREV.vrevPA1.vectype.sdr = 456
        self.assertEqual(VREV.vrevPA1.vectype.sdr, 456)       # override

        VREV = TVPVConfigDict()
        VREV.vrevPA0.vectype.sdr = 123
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        VREV.vrevPA1.vectype2.sdr = 456
        self.assertEqual(VREV.vrevPA1.vectype.sdr, 123)        # normal1
        self.assertEqual(VREV.vrevPA1.vectype2.sdr, 456)       # normal2

        VREV = TVPVConfigDict()
        VREV.vrevPA0.vectype.sdr = 123
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        VREV.vrevPA1.vectype.sdr2 = 456
        self.assertEqual(VREV.vrevPA1.vectype.sdr, 123)       # normal3
        self.assertEqual(VREV.vrevPA1.vectype.sdr2, 456)       # normal3

        VREV = TVPVConfigDict()
        VREV.vrevPA0.sdr1 = 123
        VREV.vrevPA0.sdr2 = 456
        VREV.vrevPA0.sdr3 = 789
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        VREV.vrevPA1.sdr3 = 334
        VREV.vrevPA1.sdr4 = 457
        self.assertEqual(recurse2dict(VREV.vrevPA1), {'sdr3': 334, 'sdr2': 456, 'sdr1': 123, 'sdr4': 457})       # normal4a
        self.assertEqual(recurse2dict(VREV.vrevPA0), {'sdr3': 789, 'sdr2': 456, 'sdr1': 123})       # normal4b

    def test_SAME_AS_types(self):
        VREV = TVPVConfigDict()
        VREV.vrevPA0.Astr = "str"
        VREV.vrevPA0.Aint = 123
        VREV.vrevPA0.Alist = [1, 2, 3]
        VREV.vrevPA0.Adict = {'A': 1, 'B': 2}
        VREV.vrevPA0.another.newlist = [5, 6]
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        self.assertEqual(recurse2dict(VREV.vrevPA0), recurse2dict(VREV.vrevPA1))
        VREV.vrevPA1.Aint = 456
        self.assertNotEqual(recurse2dict(VREV.vrevPA0), recurse2dict(VREV.vrevPA1))
        VREV.vrevPA0['Aint'] = 456
        self.assertEqual(recurse2dict(VREV.vrevPA0), recurse2dict(VREV.vrevPA1))

        # list
        VREV = TVPVConfigDict()
        VREV.vrevPA0.Alist = [1, 2, 3]
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        VREV.vrevPA0.Alist[0] = 9
        self.assertEqual(recurse2dict(VREV),
                         {'vrevPA1': {'Alist': [1, 2, 3]},
                          'vrevPA0': {'Alist': [9, 2, 3]}})

        # random object value
        someobj = object()
        VREV1 = TVPVConfigDict()
        VREV1.RevA.Convention = someobj
        VREV1.RevB.Convention = "string1"
        VREV2 = TVPVConfigDict()
        VREV2.SAME_AS(VREV1)
        self.assertEqual(VREV1, {'RevA': {'Convention': someobj},
                                 'RevB': {'Convention': 'string1'}})
        self.assertEqual(recurse2dict(VREV1),
                         {'RevA': {'Convention': someobj},
                          'RevB': {'Convention': 'string1'}})

        VREV2.RevA.Convention = someobj   # Need to set to the same object, since deepcopy was performed
        self.assertEqual(VREV2, {'RevA': {'Convention': someobj},
                                 'RevB': {'Convention': 'string1'}})
        self.assertEqual(VREV1, VREV2)
        self.assertEqual(recurse2dict(VREV1), recurse2dict(VREV2))

    def test_SAME_AS_list(self):
        MODE = TVPVConfigDict()
        MODE.m8.name = "8m2m"
        MODE.m6.name = "6g8m"
        VREV = TVPVConfigDict()
        VREV.vrevPA0.Astr = "str"
        VREV.vrevPA0.Aint = 123
        VREV.vrevPA0.Alist = [1, 2, 3]
        VREV.vrevPA0.Adict = {'A': 1, 'B': 2}
        VREV.vrevPA0.another.newlist = [MODE.m8m2m, MODE.m6]
        VREV.vrevPA1.SAME_AS(VREV.vrevPA0)
        self.assertListEqual(VREV.vrevPA0.another.newlist, VREV.vrevPA1.another.newlist)
        self.assertIsNot(VREV.vrevPA0.another.newlist, VREV.vrevPA1.another.newlist, "Must be different objects")

    def test_SAME_AS_update1(self):
        # two level test
        admin = TVPVConfigDict()
        admin.admin1.uniq = 1
        admin.admin1.overwrite1 = 2
        admin.admin1.overwrite2 = 3

        common = TVPVConfigDict()
        common.common1.uniq = 4
        common.common1.overwrite1 = 5
        common.common1.overwrite2 = 6

        site = TVPVConfigDict()
        site.uniq1 = 7
        site.admin1.overwrite2 = 8
        site.common1.overwrite2 = 9
        site.overwrite1 = 10

        loc = TVPVConfigDict()
        loc.SAME_AS(admin)
        loc.SAME_AS(common)
        loc.uniq2 = 11
        loc.overwrite1 = 12
        loc.admin1.overwrite1 = 13
        loc.common1.overwrite1 = 14
        loc.SAME_AS(site)

        self.assertEqual(recurse2dict(loc), {'admin1': {'uniq': 1,
                                                        'overwrite2': 8,
                                                        'overwrite1': 13},
                                             'uniq1': 7,
                                             'uniq2': 11,
                                             'overwrite1': 10,
                                             'common1': {'uniq': 4,
                                                         'overwrite2': 9,
                                                         'overwrite1': 14}})

        with self.assertRaises(KeyError):
            loc.admin1.overwrite1 = 12

    def test_SAME_AS_update2(self):
        # single level test
        admin = TVPVConfigDict()
        admin.uniq1 = 1
        admin.overwrite1a = 2
        admin.overwrite2a = 3

        common = TVPVConfigDict()
        common.uniq2 = 4
        common.overwrite1c = 5
        common.overwrite2c = 6

        site = TVPVConfigDict()
        site.uniq3 = 7
        site.overwrite2a = 8
        site.overwrite2c = 9

        loc = TVPVConfigDict()
        loc.SAME_AS(admin)
        loc.SAME_AS(common)
        loc.uniq3 = 11
        loc.overwrite1a = 10
        loc.overwrite1c = 11
        loc.SAME_AS(site)

        self.assertEqual(recurse2dict(loc), {'overwrite1c': 11,
                                             'overwrite1a': 10,
                                             'uniq1': 1,
                                             'uniq2': 4,
                                             'uniq3': 7,
                                             'overwrite2c': 9,
                                             'overwrite2a': 8})

    def test_SAME_AS_update_dict(self):
        admin = {'uniq1': 1,
                 'overwrite1a': 2,
                 'overwrite2a': 3}

        common = {'uniq2': 4,
                  'overwrite1c': 5,
                  'overwrite2c': 6
                  }

        site = {'uniq3': 7,
                'overwrite2a': 8,
                'overwrite2c': 9}

        loc = TVPVConfigDict()
        loc.SAME_AS(admin)
        loc.SAME_AS(common)
        loc.uniq3 = 11
        loc.overwrite1a = 10
        loc.overwrite1c = 11
        loc.SAME_AS(site)

        self.assertEqual(recurse2dict(loc), {'overwrite1c': 11,
                                             'overwrite1a': 10,
                                             'uniq1': 1,
                                             'uniq2': 4,
                                             'uniq3': 7,
                                             'overwrite2c': 9,
                                             'overwrite2a': 8})

        with self.assertRaises(KeyError):
            loc.overwrite1a = 12

    def test_getlevel(self):
        VREV = TVPVConfigDict()
        VREV.vrevPA0.mode.Astr = "str"
        VREV.vrevPA0.mode.Aint = 123
        VREV.vrevPA0.mode.Alist = [1, 2, 3]
        self.assertEqual(recurse2dict(VREV.GETLEVEL("vrevPA0.mode")), recurse2dict(VREV.vrevPA0.mode))
        self.assertRaises(KeyError, VREV.GETLEVEL, "vrevPA1.mode")

        VREV.vrevPA0.mode.OVERRIDE('Aint', 456)
        self.assertEqual(VREV.vrevPA0.mode.Aint, 456)

    def test_pickle(self):
        VREV = TVPVConfigDict()
        VREV.vrevPA0 = "str"
        VREV.vrevPA1 = 123
        VREV['vrevPA2'] = [1, 2, 3]
        c = pickle.dumps(VREV)
        vv = pickle.loads(c)
        self.assertDictEqual(recurse2dict(VREV), recurse2dict(vv))

    def test_merge(self):
        v = TVPVConfigDict()
        v._800.DDR._1CH.memory = 100
        v._800.DDR._2CH.memory = 50
        v._250.DDR._1CH.memory = 200
        v._250.DDR._2CH.memory = 150
        v._600.DDR._1CH.memory = 600     # new level

        x = TVPVConfigDict()
        x._800.DDR._4CH.memory = 500     # different 3rd level
        x._250.DDR._4CH.memory = 550     # different 3rd level
        x._250.DDR._2CH.memory = 151     # override same value
        x._100.DDR._1CH.memory = 231     # new first level
        orig = copy_configdict(x)
        v.merge(x)

        self.assertEqual(v, {'_800': {'DDR': {'_1CH': {'memory': 100},
                                              '_4CH': {'memory': 500},
                                              '_2CH': {'memory': 50}}},
                             '_600': {'DDR': {'_1CH': {'memory': 600}}},
                             '_100': {'DDR': {'_1CH': {'memory': 231}}},
                             '_250': {'DDR': {'_1CH': {'memory': 200},
                                              '_4CH': {'memory': 550},
                                              '_2CH': {'memory': 151}}}})
        self.assertEqual(x, orig)  # we should not be destroying the source


class XML_tests(TestCase):

    def test_remove_wierd_char(self):
        # as-is
        self.assertEqual(xmlfunc._remove_wierd_char('012345678012<a'), '012345678012<a')
        self.assertEqual(xmlfunc._remove_wierd_char('<012345'), '<012345')
        # truncated
        self.assertEqual(xmlfunc._remove_wierd_char(' <012345'), '<012345')
        self.assertEqual(xmlfunc._remove_wierd_char('   <012345'), '<012345')
        self.assertEqual(xmlfunc._remove_wierd_char(''), '')

    def test_dict2xml_str(self):
        # simple dictionary
        mydict = {'dieconfig': 123, 'fuseconfig': "456"}
        self.assertEqual(xmlfunc.dict2xml_str(mydict),
                         '<dieconfig dieconfig="123" />\n<fuseconfig fuseconfig="456" />\n')

        # mixed case with list
        mydict = OrderedDict()
        mydict['listm'] = ['a', 123, {'a': 1, 'b': 2}]
        mydict['dieconfig'] = 123
        mydict['top'] = {'abc': 123, 'def': 'a'}
        print("\n", xmlfunc.dict2xml_str(mydict))
        self.assertEqual(xmlfunc.dict2xml_str(mydict),
                         '<listm listm="a" />\n<listm listm="123" />\n<listm>\n    <a a="1" />\n    <b b="2" />\n</listm>\n<dieconfig dieconfig="123" />\n<top>\n    <abc abc="123" />\n    <def def="a" />\n</top>\n')

    def test_dict_pretty_print(self):
        dd = ['a', 123, {'a': 1, 'b': 2}]
        expect = """[
   "a",
   123,
   {
      "a": 1,
      "b": 2
   }
]"""
        self.assertTextEqual(xmlfunc.dict_pretty_string(dd), expect)

    def test_xml_dict(self):
        with TempName(name=True) as tmp, TempName(name=True) as tmp2:

            with open(tmp, "w") as fh:
                fh.write('''<?xml version="1.0" encoding="utf-8" ?>
    <Trace_info>
        <trace_events>
            <EVENT romgen="0x186a1">
                <seinfo>
                    <state value="Overriding the fuses" />
                </seinfo>
            </EVENT>
            <EVENT romgen="0x186a2">
                <seinfo>
                    <state value="STROBE_PCU IO_GLOBAL_RESET read_0x186a2" />
                    <pin value="xxTDO" />
                    <instr value="LR_PCUDATAREAD" />
                    <drfield value="pcudata_data" />
                </seinfo>
            </EVENT>
        </trace_events>
    </Trace_info>
    ''')
            with open(tmp2, "w") as fh:
                fh.write('''<?xml version="1.0" encoding="utf-8" ?>
    <Trace_info>
        <trace_events>
            <EVENT romgen="0x186a1">
                <seinfo>
                    <state value="Overriding the fuses" />
                </seinfo>
            </EVENT>
            <EVENT romgen="0x186a2">
                <seinfo>
                    <state value="STROBE_PCU IO_GLOBAL_RESET read_0x186a2" />
                    <pin value="xxTDO" />
                    <instr value="LR_PCUDATAREAD" />
                    <drfield value="pcudata_data" />
                </seinfo>
            </EVENT>
            <EVENT romgen="0x186a3">
                <seinfo>
                    <state value="SOME STRING" />
                    <pin value="xxTDO" />
                </seinfo>
            </EVENT>
        </trace_events>
    </Trace_info>
    ''')

            res = xmlfunc.xml2dict(tmp)
            expect = {'Trace_info': {'trace_events': {'EVENT': [{'seinfo': {'state': {'value': 'Overriding the fuses'}}, 'romgen': '0x186a1'}, {'seinfo': {'state': {'value': 'STROBE_PCU IO_GLOBAL_RESET read_0x186a2'}, 'drfield': {'value': 'pcudata_data'}, 'pin': {'value': 'xxTDO'}, 'instr': {'value': 'LR_PCUDATAREAD'}}, 'romgen': '0x186a2'}]}}}
            self.assertEqual(res, expect)  # 1 - file to dict

            origxmlobj = ElementTree.parse(tmp).getroot()
            res = xmlfunc.xml2dict(origxmlobj)
            self.assertEqual(res, expect)  # 2 - xml obj to dict

            xmlobj = xmlfunc.dict2xml(res)
            self.assertEqual(type(xmlobj), type(origxmlobj))  # Check if type is xml obj
            res = xmlfunc.xml2dict(xmlobj)
            self.assertEqual(res, expect)  # 3 - dict2xml to dict

            self.assertEqual(res.Trace_info.trace_events.EVENT[1].romgen, "0x186a2")   # check for the "." access

            res = xmlfunc.xml2dict(xmlobj, dictclass=dict)
            self.assertEqual(res, expect)  # 4 - dict class

            # self.assertRaises(TypeError, xmlfunc.xml2dict, 123)

            xdic = xmlfunc.xml2dict(tmp)
            xmlobj_orig = xmlfunc.dict2xml(xdic)
            xdic.Trace_info.trace_events.EVENT[1].seinfo.state._text = xdic.Trace_info.trace_events.EVENT[1].seinfo.state.pop('value')
            xmlobj_w_txt = xmlfunc.dict2xml(xdic)
            expect = b'<Trace_info><trace_events><EVENT><romgen>0x186a1</romgen><seinfo><state><value>Overriding the fuses</value></state></seinfo></EVENT><EVENT><romgen>0x186a2</romgen><seinfo><state>STROBE_PCU IO_GLOBAL_RESET read_0x186a2</state><pin><value>xxTDO</value></pin><instr><value>LR_PCUDATAREAD</value></instr><drfield><value>pcudata_data</value></drfield></seinfo></EVENT></trace_events></Trace_info>'
            self.assertNotEqual(ElementTree.tostring(xmlobj_w_txt), ElementTree.tostring(xmlobj_orig))  # 5 - ConvertDictToXmlRecurse() xml node to '_txt'
            self.assertEqual(ElementTree.tostring(xmlobj_w_txt), expect)

            xdic = xmlfunc.xml2dict(tmp2)  # 6 - ConvertXmlToDictRecurse() - adding node to existing list (EVENT)
            self.assertEqual(xdic.Trace_info.trace_events.EVENT[0].romgen, "0x186a1")   # check for the "." access
            self.assertEqual(xdic.Trace_info.trace_events.EVENT[1].romgen, "0x186a2")   # check for the "." access
            self.assertEqual(xdic.Trace_info.trace_events.EVENT[2].romgen, "0x186a3")   # check for the "." access
            self.assertEqual(xdic.Trace_info.trace_events.EVENT[2].seinfo.state.value, "SOME STRING")   # check for the "." access

            for event in xmlobj_orig.iter('EVENT'):  # Adding element.text values to internal xml node
                event.text = "EVENT TEXT"
            xdic_w_txt = xmlfunc.xml2dict(xmlobj_orig)
            expect = {'Trace_info': {'trace_events': {'EVENT': [{'romgen': '0x186a1', 'seinfo': {'state': {'value': 'Overriding the fuses'}}, '_text': 'EVENT TEXT'}, {'romgen': '0x186a2', 'seinfo': {'state': {'value': 'STROBE_PCU IO_GLOBAL_RESET read_0x186a2'}, 'drfield': {'value': 'pcudata_data'}, 'pin': {'value': 'xxTDO'}, 'instr': {'value': 'LR_PCUDATAREAD'}}, '_text': 'EVENT TEXT'}]}}}
            self.assertEqual(xdic_w_txt, expect)  # 7 - ConvertXmlToDictRecurse() - converting text prop of none-leaf node

    def test_xml_dict_gz(self):
        with TempDir(name=True) as tdir:
            tmp = join(tdir, "file1.xml")

            with open(tmp, "w") as fh:
                fh.write('''<?xml version="1.0" encoding="utf-8" ?>
    <Trace_info>
        <trace_events>
            <EVENT romgen="0x186a1">
                <seinfo>
                    <state value="Overriding the fuses" />
                </seinfo>
            </EVENT>
            <EVENT romgen="0x186a2">
                <seinfo>
                    <state value="STROBE_PCU IO_GLOBAL_RESET read_0x186a2" />
                    <pin value="xxTDO" />
                    <instr value="LR_PCUDATAREAD" />
                    <drfield value="pcudata_data" />
                </seinfo>
            </EVENT>
        </trace_events>
    </Trace_info>
    ''')

            a1 = File(tmp).compress(File.gz)
            tmp = a1.get_name()
            self.assertTrue(tmp.endswith('.gz'))
            expect = {'Trace_info': {'trace_events': {'EVENT': [{'seinfo': {'state': {'value': 'Overriding the fuses'}}, 'romgen': '0x186a1'}, {'seinfo': {'state': {'value': 'STROBE_PCU IO_GLOBAL_RESET read_0x186a2'}, 'drfield': {'value': 'pcudata_data'}, 'pin': {'value': 'xxTDO'}, 'instr': {'value': 'LR_PCUDATAREAD'}}, 'romgen': '0x186a2'}]}}}

            # input file is gzipped
            res = xmlfunc.xml2dict(tmp)
            self.assertEqual(res, expect)

            # input file is a file handle
            res = xmlfunc.xml2dict(a1.fh())
            self.assertEqual(res, expect)


class INI_tests(TestCase):

    def test_dict2ini(self):
        dict1 = {'sectionname': {'key1': 'value1', 'key2': 'value2'}}
        dict2 = {'sectionname1': {'key1': 'value1'}, 'sectionname2': {'key1': 12, 'key2': 'value2'}}
        dict3 = {'key1': 'value', 'key2': 'value2'}
        dict4 = {'key1': 'value1', 'key2': [1, 2, 3]}
        dict5 = {'sectionname1': {'key1': 'value1'}, 'sectionname2': {'key1': 'value1', 'key2': {'key3': 'value'}}}

        with self.assertRaises(IOError):
            inifunc.dict2ini(dict1, '')

        with TempName(name=True) as tmp:
            with open(tmp, "w") as fh:
                fh.write('''''')
            self.assertEqual(inifunc.dict2ini(dict1, tmp),
                             '[sectionname]\nkey2 = value2\nkey1 = value1\n')

            self.assertEqual(inifunc.dict2ini(dict2, tmp),
                             '[sectionname1]\nkey1 = value1\n[sectionname2]\nkey2 = value2\nkey1 = 12\n')

            with self.assertRaises(ValueError):
                inifunc.dict2ini(dict3, tmp)

            with self.assertRaises(ValueError):
                inifunc.dict2ini(dict4, tmp)

            with self.assertRaises(ValueError):
                inifunc.dict2ini(dict5, tmp)

    def test_ini2dict(self):
        with TempName(name=True) as tmp:
            with open(tmp, "w") as fh:
                fh.write('''[sectionname]\nKey1 = value1\nkey2 = value2\n''')
            iniDict = inifunc.ini2dict(tmp)
            self.assertEqual(iniDict['sectionname']['Key1'], 'value1')
            self.assertEqual(iniDict['sectionname']['key2'], 'value2')

            with open(tmp, "w") as fh:
                fh.write('''Not an ini file\nvalid format''')
            with self.assertRaises(MissingSectionHeaderError):
                iniDict = inifunc.ini2dict(tmp)

            with open(tmp, "w") as fh:
                fh.write('''[sectionname]\nKey1 = value1\nkey2 = value2\nkey3 = something %(dumb)''')
            iniDict = inifunc.ini2dict(tmp)
            self.assertEqual(iniDict['sectionname']['key3'], 'something %(dumb)')

            with open(tmp, "w") as fh:
                fh.write('''[sectionname]\nKey1 = value1\nkey2 = value2\nkey3 = something %(self.dumb)''')
            iniDict = inifunc.ini2dict(tmp)
            self.assertEqual(iniDict['sectionname']['key3'], 'something %(self.dumb)')


class NamedSeq_tests(TestCase):

    def test_basic(self):
        filt = NamedSeq('name', 'regex')
        dd = filt('Pre', 'hsw_pre.*')
        self.assertEqual(dd.name, 'Pre')
        self.assertEqual(dd.regex, 'hsw_pre.*')
        self.assertDictEqual(dd, {'name': 'Pre', 'regex': 'hsw_pre.*'})

        self.assertRaises(ValueError, filt, 'one')
        self.assertRaises(ValueError, NamedSeq, 'one', 'a-')    # invalid - non-alphanum
        self.assertRaises(ValueError, NamedSeq, '0one')         # invalid - starts with 0
        self.assertRaises(ValueError, NamedSeq, 'if')           # invalid - keyword
        self.assertRaises(ValueError, NamedSeq, 'a b'.split())           # invalid - keyword

        filt = NamedSeq('name')
        dd = filt('Pre')
        self.assertEqual(dd, {'name': 'Pre'})

    def test_keyword(self):

        # test1: default
        filt = NamedSeq('name', 'regex', 'desc')
        filt.default(regex='rr', desc='any')
        dd = filt('test')
        self.assertDictEqual(dd, {'name': 'test', 'regex': 'rr', 'desc': 'any'})

        # test2: kwarg in call-100%
        filt = NamedSeq('name', 'regex', 'desc')
        dd = filt(name='test1', desc='any1', regex='rr1')
        self.assertDictEqual(dd, {'name': 'test1', 'regex': 'rr1', 'desc': 'any1'})

        # test2: kwarg in call-50%
        dd = filt('test2', desc='any2', regex='rr2')
        self.assertDictEqual(dd, {'name': 'test2', 'regex': 'rr2', 'desc': 'any2'})

        # test2: kwarg in call-0%
        dd = filt('test3', 'rr3', 'any3')
        self.assertDictEqual(dd, {'name': 'test3', 'regex': 'rr3', 'desc': 'any3'})

        # test3: error: over
        self.assertRaises(ValueError, filt, 'test3', 'any3', 'rr3', 'extra')

        # test4: error: missing
        filt.default(regex='rr')
        self.assertRaises(ValueError, filt, 'test3')

        # test5: extra kwargs
        dd = filt('a', 'b', 'c', extra='d')
        self.assertEqual(dd, {'regex': 'b', 'desc': 'c', 'name': 'a', 'extra': 'd'})

    def test_pickle_NamedSeq(self):
        filt = NamedSeq('name', 'regex', 'desc')
        filt.default(regex='rr', desc='any')

        c = pickle.dumps(filt)
        vv = pickle.loads(c)
        dd = vv('test')
        self.assertDictEqual(dd, {'name': 'test', 'regex': 'rr', 'desc': 'any'})

        c = pickle.dumps(dd)
        vv = pickle.loads(c)
        self.assertDictEqual(vv, {'name': 'test', 'regex': 'rr', 'desc': 'any'})


class DictDotRO_tests(TestCase):

    def test_basic(self):
        # Note: Cannot pickle DictDotRO
        orig = {'a': 123, 'b': 456}
        hh = DictDotRO(a=123, b=456)
        self.assertDictEqual(hh, orig)

        hh = DictDotRO(orig)
        self.assertDictEqual(hh, orig)

    def test_writes(self):
        hh = DictDotRO(a=123, b=456)
        with self.assertRaisesRegex(AttributeError, "readonly"):
            hh['a'] = 45
        with self.assertRaisesRegex(AttributeError, "readonly"):
            hh.a = 45
        with self.assertRaisesRegex(AttributeError, "readonly"):
            del hh['a']
        self.assertRaisesRegex(AttributeError, "readonly", hh.clear)
        self.assertRaisesRegex(AttributeError, "readonly", hh.popitem)
        self.assertRaisesRegex(AttributeError, "readonly", hh.update, {'a': 2})
        self.assertRaisesRegex(AttributeError, "readonly", hh.setdefault, 'c', 33)
        self.assertRaisesRegex(AttributeError, "readonly", hh.pop, 'a')

        self.assertDictEqual(hh, {'a': 123, 'b': 456})


class DictDot_tests(TestCase):

    def test_pickle_DictDot(self):
        hh = DictDot(a=123, b=456)
        hh['c'] = 12      # normal write
        hh.d = 789        # DOT write
        c = pickle.dumps(hh)
        vv = pickle.loads(c)
        self.assertDictEqual(recurse2dict(hh), recurse2dict(vv))

    def test_various_DictDot(self):
        def func():
            return hh.e

        hh = DictDot(a=123, b=456)
        hh['c'] = 12      # normal write
        hh.d = 789        # DOT write
        self.assertEqual(sorted(hh.keys()), ['a', 'b', 'c', 'd'])
        self.assertEqual(hh['a'], 123)      # normal read
        self.assertEqual(hh.a, 123)         # dot read
        self.assertEqual(hh['c'], 12)       # normal read
        self.assertEqual(hh.c, 12)          # dot read
        self.assertEqual(hh['d'], 789)      # normal read
        self.assertEqual(hh.d, 789)         # dot read

        self.assertRaises(KeyError, func)   # dot read. not found

        hh1 = DictDot(hh)
        hh1.b = 45
        self.assertEqual(hh1, {'a': 123, 'c': 12, 'b': 45, 'd': 789})

    def test_autoDictDot(self):
        hh = autoDictDot()
        hh.ky1.ky2 = 123
        hh['ky1']['ky3'] = 456
        self.assertEqual(hh.ky1.ky3, 456)
        self.assertEqual(hh['ky1']['ky2'], 123)

        # pickle test
        c = pickle.dumps(hh)
        vv = pickle.loads(c)
        self.assertEqual(vv.ky1.ky3, 456)
        self.assertEqual(vv['ky1']['ky2'], 123)


class DictValues_tests(TestCase):

    def test_pickle_DictValues(self):
        hh = DictValues(a=123, b=456)
        hh['c'] = 123
        hh['d'] = 789
        c = pickle.dumps(hh)
        vv = pickle.loads(c)
        self.assertDictEqual(recurse2dict(hh), recurse2dict(vv))
        self.assertEqual(sorted(vv.vkeys(123)), ['a', 'c'])  # 4

    def test_update_DictValues(self):
        # basic checks, new item
        hh = DictValues(a=123)
        dd = dict(b=456, c=123, d=789)
        hh.update(dd)
        self.assertEqual(sorted(hh.keys()), ['a', 'b', 'c', 'd'])  # 1
        self.assertEqual(sorted([x for x in hh]), ['a', 'b', 'c', 'd'])  # 2
        self.assertEqual(sorted([x for x in hh.uniq_values()]), [123, 456, 789])  # 3
        self.assertEqual(sorted([x for x in hh.vkeys(123)]), ['a', 'c'])  # 4

    def test_basic_DictValues(self):
        # basic checks, new item
        hh = DictValues(a=123, b=456)
        hh['c'] = 123
        hh['d'] = 789
        self.assertEqual(sorted(hh.keys()), ['a', 'b', 'c', 'd'])  # 1
        self.assertEqual(sorted([x for x in hh]), ['a', 'b', 'c', 'd'])  # 2
        self.assertEqual(sorted([x for x in hh.uniq_values()]), [123, 456, 789])  # 3
        self.assertEqual(sorted([x for x in hh.vkeys(123)]), ['a', 'c'])  # 4

        # same item reassign (value is gone)
        hh['d'] = 123
        self.assertEqual(sorted([x for x in hh]), ['a', 'b', 'c', 'd'])  # 5
        self.assertEqual(sorted([x for x in hh.uniq_values()]), [123, 456])  # 6
        self.assertEqual(sorted([x for x in hh.vkeys(123)]), ['a', 'c', 'd'])  # 7

        # same item reassign (value not gone)
        hh['a'] = 888
        self.assertEqual(sorted([x for x in hh]), ['a', 'b', 'c', 'd'])  # 8
        self.assertEqual(sorted([x for x in hh.uniq_values()]), [123, 456, 888])  # 9
        self.assertEqual(sorted([x for x in hh.vkeys(123)]), ['c', 'd'])  # 10

        # delete item (value not removed)
        del hh['c']
        self.assertEqual(sorted([x for x in hh]), ['a', 'b', 'd'])  # 11
        self.assertEqual(sorted([x for x in hh.uniq_values()]), [123, 456, 888])  # 12
        self.assertEqual(sorted([x for x in hh.vkeys(123)]), ['d'])  # 13

        # delete item (value removed)
        del hh['d']
        del hh['ee']    # non existent
        self.assertEqual(sorted([x for x in hh]), ['a', 'b'])  # 14
        self.assertEqual(sorted([x for x in hh.uniq_values()]), [456, 888])  # 15
        self.assertEqual(sorted([x for x in hh.vkeys(123)]), [])  # 16
        self.assertEqual(sorted([x for x in hh.vkeys(456)]), ['b'])  # 17

        self.assertEqual(sorted([x for x in hh.vkeys(45699)]), [])  # 18


class Func_tests(TestCase):

    def test_read_csv(self):
        with TempDir(name=True, chdir=True):
            File('a.csv').touch('''ProcessStep,LotType,Platform
COLD,*,HDMX1
HOT,*,HDMX2
''')
            result = read_csv('a.csv')
            self.assertEqual(result, [{'ProcessStep': 'COLD', 'LotType': '*', 'Platform': 'HDMX1'},
                                      {'ProcessStep': 'HOT', 'LotType': '*', 'Platform': 'HDMX2'}])

            result = read_csv('a.csv', False)
            self.assertEqual(result, [['ProcessStep', 'LotType', 'Platform'],
                                      ['COLD', '*', 'HDMX1'],
                                      ['HOT', '*', 'HDMX2']])

    def test_iter_levels(self):
        dd = {'A1': {'B1': {1: 1, 2: 2},
                     'B2': {3: 3}},
              'A2': {'B3': {4: 4},
                     'B4': {5: 5}}
              }
        result = [(x, y) for x, y in iter_levels(dd, 2)]
        self.assertEqual(result,
                         [('A1', 'B1'), ('A1', 'B2'), ('A2', 'B3'), ('A2', 'B4')])

        result = [(x, y, z) for x, y, z in iter_levels(dd, 3)]
        self.assertEqual(result,
                         [('A1', 'B1', 1),
                          ('A1', 'B1', 2),
                          ('A1', 'B2', 3),
                          ('A2', 'B3', 4),
                          ('A2', 'B4', 5)])

    def test_keys_atlevel(self):
        dd = {'A1': {'B1': {1: 1, 2: 2},
                     'B2': {3: 3}},
              'A2': {'B3': {4: 4},
                     'B4': ['a', 'b']},
              }
        self.assertEqual(set(keys_atlevel(dd, 0)), {'A1', 'A2'})
        self.assertEqual(set(keys_atlevel(dd, 1)), {'B1', 'B2', 'B3', 'B4'})
        self.assertEqual(set(keys_atlevel(dd, 2, error=True)), {1, 2, 3, 4, 'a', 'b'})

        with self.assertRaisesRegex(TypeError, '1 is not dictionary type of level=3 of 4'):
            set(keys_atlevel(dd, 4, error=True))

        # mixed set
        dd = {'A1': {'B1': 1,
                     'B2': '2'},
              'A2': '3',
              'A3': {'4', '5'},
              'A4': ['6', '7'],
              }
        self.assertEqual(set(keys_atlevel(dd, 0)), set('A1 A2 A3 A4'.split()))
        self.assertEqual(set(keys_atlevel(dd, 1)), set('B1 B2 3 4 5 6 7'.split()))
        self.assertEqual(set(keys_atlevel(dd, 2)), {1, '2'})

    def test_remove_none_values(self):
        dd = {'a': 1, 'b': None}
        self.assertEqual(remove_none_values(dd), {'a': 1})
        dd = {'a': 1, 'b': 2}
        self.assertEqual(remove_none_values(dd), {'a': 1, 'b': 2})
        dd = dict()
        self.assertEqual(remove_none_values(dd), dict())
        dd = {'a': None, 'b': None}
        self.assertEqual(remove_none_values(dd), dict())

    def test_various_getkeyfromval(self):
        hh = dict(a=123, b=456, c=759)
        self.assertEqual(getkeyfromval(hh, 456), 'b')
        self.assertEqual(getkeyfromval(hh, 999), None)

    def test_various_iterkeyfromval(self):
        hh = dict(a=123, b=456, c=123)
        self.assertEqual(','.join(sorted(iterkeyfromval(hh, 123))), "a,c")

    def test_various_iter_dot_items(self):
        d = {'a': [{'b': [0, 1], 'c':[2, 3]}, {'d': [4, 5]}], 'b': [{'e': 6}, {'f': 7}]}
        self.assertEqual(sorted([y for y in iter_dot_items(d)]), [('a.[0].b.[0]', 0),
                                                                  ('a.[0].b.[1]', 1),
                                                                  ('a.[0].c.[0]', 2),
                                                                  ('a.[0].c.[1]', 3),
                                                                  ('a.[1].d.[0]', 4),
                                                                  ('a.[1].d.[1]', 5),
                                                                  ('b.[0].e', 6),
                                                                  ('b.[1].f', 7)])

        self.assertEqual(sorted([y for y in iter_dot_items(d, listdot=False)]),
                         [('a', [{'c': [2, 3], 'b': [0, 1]}, {'d': [4, 5]}]),
                          ('b', [{'e': 6}, {'f': 7}])])

        d = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(sorted([y for y in iter_dot_items(d)]), [('a', 1), ('b', 2), ('c', 3)])
        d = [0, 1, 2]
        self.assertEqual(sorted([y for y in iter_dot_items(d)]), [('[0]', 0), ('[1]', 1), ('[2]', 2)])
        d = "abc"
        self.assertEqual(sorted([y for y in iter_dot_items(d)]), [("", "abc")])

        d = {'a': {'b': [1, 2]}}
        self.assertEqual(sorted([y for y in iter_dot_items(d, listdot=False)]),
                         [('a.b', [1, 2])])

    def test_find_dot_items(self):
        d = {'aa': {'bb': 'aa_bb', 'cc': 'aa_cc'}}
        self.assertEqual(find_dot_items(d, 'bb'), ['aa_bb'])
        self.assertEqual(find_dot_items(d, 'aa.bb'), ['aa_bb'])
        self.assertEqual(find_dot_items(d, 'aa.bb$', default='zz'), 'zz')
        self.assertEqual(find_dot_items(d, regex=r"\.bb$"), ['aa_bb'])

    def test_recurse2dict(self):
        with TempName(name=True) as tmp:
            fh = open(tmp, 'wb')

            arr = autodict()
            arr[1][11][123] = 'a'
            arr[1][11][456] = 'b'
            arr[2] = [1, 2, 3]
            arr[3] = set(('a', 'b', 'c'))
            arr[4][22][123] = 'a'
            res = recurse2dict(arr)
            self.assertEqual(res, arr)  # 1
            self.assertRaises(ValueError, marshal.dump, arr, fh)  # 2
            marshal.dump(res, fh)

            arr = defaultdict(int)
            arr['a'] += 400
            arr['b'] += 600
            res = recurse2dict(arr)
            self.assertEqual(res, arr)  # 3
            self.assertRaises(ValueError, marshal.dump, arr, fh)  # 4
            marshal.dump(res, fh)
            fh.close()

        # non-dictionary items
        self.assertEqual(recurse2dict("abc"), "abc")
        self.assertEqual(recurse2dict(25), 25)
        obj = object()
        self.assertIs(recurse2dict(obj), obj)

    def test_various_iterpartialkey(self):
        d = autoDictDot()
        d.par1.child.last1 = 123
        d.par2.child.last2 = 456
        d.par3.child.last3 = 789

        self.assertEqual([y for y in iterpartialkey(d, "par2.child")], [456])
        self.assertEqual([y for y in iterpartialkey(d, "par3.child.last3")], [789])
        self.assertEqual([y for y in iterpartialkey(d, "par3")], [789])
        self.assertEqual(sorted([y for y in iterpartialkey(d, "child.last")]), [123, 456, 789])
        self.assertEqual([x for x in iterpartialkey("abc", "bc")], [])

        d = autoDictDot()
        d.keyname1j = 123
        d.keyname2j = 456
        d.kewname2j = 789
        d.keyname3a = 890
        self.assertEqual(sorted([y for y in iterpartialkey(d, "name2j")]), [456, 789])

    def test_key_remap(self):
        d1 = {'one': 111, 'two': 222, 'any': 999}
        alias = {'one': 'First', 'two': 'Second'}
        self.assertDictEqual(key_remap(d1, alias), {'First': 111, 'Second': 222, 'any': 999})
        d2 = key_remap(d1, alias, dictclass=DictDot)
        self.assertDictEqual(key_remap(d1, alias), {'First': 111, 'Second': 222, 'any': 999})
        self.assertEqual(d2.__class__.__name__, "DictDot")

    def test_reverse_set(self):
        d1 = {'1': set('abc'), '2': set('def'), '3': set('ad')}
        self.assertEqual(reverse_set(d1), {'a': {'1', '3'},
                                           'b': {'1'},
                                           'c': {'1'},
                                           'd': {'2', '3'},
                                           'e': {'2'},
                                           'f': {'2'}})

        d1 = {'1': 'abc', '2': 'abc', '3': 'ghi'}
        self.assertEqual(reverse_set(d1), {'abc': {'2', '1'}, 'ghi': {'3'}})

    def test_reverse_keyval(self):
        d1 = {'a': 'a123', 'b': 'b456'}
        self.assertDictEqual(reverse_keyval(d1), {'a123': 'a', 'b456': 'b'})

        mydict = TVPVConfigDict()
        mydict.A.full = "a123"
        mydict.A.desc = "letterA"
        mydict.B.full = "b456"
        mydict.B.desc = "letterB"
        mydict.C.desc = "letterC"
        self.assertDictEqual(reverse_keyval(mydict, "full"), {'a123': 'A', 'b456': 'B'})

        d2 = reverse_keyval(mydict, "full", dictclass=DictDot)
        self.assertDictEqual(d2, {'a123': 'A', 'b456': 'B'})
        self.assertEqual(d2.__class__.__name__, "DictDot")

    def test_remove_quote_after_equal(self):
        self.assertEqual(dictmore._remove_quote_after_equal('abc = "123"'), 'abc = 123')
        self.assertEqual(dictmore._remove_quote_after_equal("abc = '123'"), 'abc = 123')
        self.assertEqual(dictmore._remove_quote_after_equal('abc = "123'), 'abc = "123')
        self.assertEqual(dictmore._remove_quote_after_equal('abc ="123"'), 'abc ="123"')
        self.assertEqual(dictmore._remove_quote_after_equal('abc = 22'), 'abc = 22')
        self.assertEqual(dictmore._remove_quote_after_equal('abc = "21"'), 'abc = 21')
        self.assertEqual(dictmore._remove_quote_after_equal('abc = 1'), 'abc = 1')
        self.assertEqual(dictmore._remove_quote_after_equal('abc = "1"'), 'abc = 1')
        self.assertEqual(dictmore._remove_quote_after_equal("abc = ''"), 'abc = ')

    def test_flatdict(self):
        dd = {'a': [{'b': 1, 'c': 'ab'}, {'d': 'ff'}], 'b': {'e': 'a', 'f': 7}}
        self.assertEqual(list(flatdict(dd)),
                         ['a.[0].b = 1',
                          'a.[0].c = ab',
                          'a.[1].d = ff',
                          'b.e = a',
                          'b.f = 7',
                          ''])

    def test_attr2dict(self):
        class Abc:
            ghi = "A"

            def __init__(self):
                self.abc = 123
                self.abc2 = True

            def foo(self):
                self.abc3 = "not executed"

        self.assertEqual(attr2dict(Abc()), {'abc': 123, 'abc2': True, 'ghi': "A"})
        self.assertEqual(attr2dict(Abc), {'ghi': "A"})
        self.assertEqual(attr2dict(dict), {})

    def test_dict2attr(self):
        oo = dict2attr({'abc': 123, 'ghi': 456})
        self.assertEqual(set(x for x in dir(oo) if not x.startswith('_')), {'abc', 'ghi'})
        self.assertEqual(oo.abc, 123)
        self.assertEqual(oo.ghi, 456)

    def test_copy_configdict(self):
        aa = TVPVConfigDict()
        aa.abc.a11 = 21
        aa.tyy.a45 = 22
        bb = copy_configdict(aa)
        self.assertEqual(recurse2dict(aa), recurse2dict(bb))
        aa.abc['a11'] = 23
        self.assertNotEqual(recurse2dict(aa), recurse2dict(bb))

    def test_delkeys(self):
        aa = {'a': 123, 'b': 456, 'c': 789}
        self.assertEqual(delkeys(aa, ['a', 'd']), {'b': 456, 'c': 789})
        self.assertEqual(aa, {'a': 123, 'b': 456, 'c': 789})   # untouched

    def test_firstitem(self):
        self.assertIs(firstitem([]), None)
        self.assertEqual(firstitem([123, 456, 789]), 123)
        self.assertEqual(firstitem([None, 123, 456, 789]), 123)
        self.assertEqual(firstitem({123}), 123)
        self.assertEqual(firstitem({123: 'value'}), 123)
        self.assertEqual(firstitem(x for x in (123, 456)), 123)

    def test_add_no_dup(self):
        dd = {}
        add_no_dup(dd, "a", 123)
        with self.assertRaisesRegex(Exception, "already exist in dictionary"):
            add_no_dup(dd, "a", 456)
        with self.assertRaisesRegex(Exception, "already exist in simode"):
            add_no_dup(dd, "a", 789, "simode")

    def test_key_exist(self):
        dd = TVPVConfigDict()
        dd['pat1']['vedb']['tracelist'] = 123
        self.assertTrue(key_exist(dd, 'pat1', 'vedb', 'tracelist'))
        self.assertTrue(key_exist(dd, 'pat1', 'vedb'))
        self.assertFalse(key_exist(dd, 'pat1', 'vedb', 'tracelista'))
        self.assertFalse(key_exist(dd, 'pat1', 'vedba', 'tracelista'))
        self.assertFalse(key_exist(dd, 'pat2', 'vedb', 'tracelista'))

    def test_get_multi_level(self):
        dd = TVPVConfigDict()
        dd['pat1']['vedb']['tracelist'] = 123
        self.assertEqual(get_multi_level(dd, 'pat1', 'vedb', 'tracelist'), 123)
        self.assertEqual(get_multi_level(dd, 'pat1', 'vedb'), {'tracelist': 123})
        dd['pat1']['vedb2'] = [123, 456]
        self.assertEqual(get_multi_level(dd, 'pat1', 'vedb2', 0), 123)

    def test_assign_multi_level(self):
        # new key - one level, fresh
        dd = DictDot()
        assign_multi_level(dd, ['key1'], 111)
        self.assertEqual(dd, {'key1': 111})

        # new key - multi-level, fresh
        dd = DictDot()
        assign_multi_level(dd, 'a b c d'.split(), 111)
        self.assertEqual(dd, {'a': {'b': {'c': {'d': 111}}}})

        # new key - one level
        dd = DictDot(key0=222)
        assign_multi_level(dd, ['key1'], 111)
        self.assertEqual(dd, {'key0': 222,
                              'key1': 111})

        # 1. new key - multi-level
        dd = DictDot(key0=222)
        assign_multi_level(dd, 'a b c d'.split(), 111)
        self.assertEqual(dd, {'key0': 222,
                              'a': {'b': {'c': {'d': 111}}}})

        # 2. existing
        assign_multi_level(dd, 'a b c e'.split(), 222)
        self.assertEqual(dd, {'key0': 222,
                              'a': {'b': {'c': {'d': 111,
                                                'e': 222}}}})

        # 3. existing
        assign_multi_level(dd, 'a b f f'.split(), 333)
        self.assertEqual(dd, {'key0': 222,
                              'a': {'b': {'c': {'d': 111,
                                                'e': 222},
                                          'f': {'f': 333}}}})

        # 4. existing
        assign_multi_level(dd, 'key1'.split(), 444)
        self.assertEqual(dd, {'key0': 222,
                              'key1': 444,
                              'a': {'b': {'c': {'d': 111,
                                                'e': 222},
                                          'f': {'f': 333}}}})

    def test_merge_and_check_unique(self):
        '''Logic test for merge_and_check_unique'''

        # basic functional case
        d1 = TVPVConfigDict()
        d1.key1a = 'value1a'
        d1.key1b = 'value1b'
        d2 = {'key2a': 'value2a', 'key2b': 'value2b'}
        act = merge_and_check_unique(d1, d2)
        exp = TVPVConfigDict()
        exp.key1a = 'value1a'
        exp.key1b = 'value1b'
        exp.key2a = 'value2a'
        exp.key2b = 'value2b'

        self.assertEqual(act, exp)
        self.assertEqual(type(act), type(TVPVConfigDict()))

        # case duplicate key (raise exception)
        d1 = TVPVConfigDict()
        d1.key1a = 'value1a'
        self.assertRaisesRegex(KeyError, 'Duplicate keys', merge_and_check_unique, d1, d1)

        # invalid type
        self.assertRaisesRegex(TypeError, 'Input argument:', merge_and_check_unique, d1, 'string')

    def test_chunkdict(self):
        # no chunk test
        orig = {1: 100, 2: 200, 3: 300}
        self.assertEqual(list(chunkdict(orig, 5)), [orig])
        self.assertEqual(list(chunkdict(orig, 3)), [orig])

        # two elements
        res = list(chunkdict(orig, 2))
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 2)
        self.assertEqual(len(res[1]), 1)
        res2 = res[0]
        res2.update(res[1])
        self.assertEqual(orig, res2)

        # one element
        res = list(chunkdict(orig, 1))
        self.assertEqual(len(res), 3)
        self.assertEqual(len(res[0]), 1)
        self.assertEqual(len(res[1]), 1)
        self.assertEqual(len(res[2]), 1)
        res2 = res[0]
        res2.update(res[1])
        res2.update(res[2])
        self.assertEqual(orig, res2)

    def test_dict_merge(self):
        dd = {'a': 1, 'b': 2}
        merge = {'c': 3, 'd': 4}
        expected = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        dict_merge(dd, merge)
        self.assertEqual(dd, expected, "Basic 1-level dictionary merging")

        dd = {'a': 1, 'b': 2}
        merge = {'a': 3, 'd': 4}
        expected = {'a': 3, 'b': 2, 'd': 4}
        dict_merge(dd, merge)
        self.assertEqual(dd, expected, "identical keys do get updates during dict_merge")

        dd = {'a': 1, 'b': 2, 'c': {'x': 9, 'y': 8}}
        merge = {'c': {'x': 7, 'z': 6}, 'd': 4}
        expected = {'a': 1, 'b': 2, 'c': {'x': 7, 'y': 8, 'z': 6}, 'd': 4}
        dict_merge(dd, merge)
        self.assertEqual(dd, expected, "2-level dictionary gets merged")

    def test_dfs(self):

        graph = {'A': set(['B', 'C']),
                 'B': set(['A', 'D', 'E']),
                 'C': set(['A', 'F']),
                 'D': set(['B']),
                 'E': set(['B', 'F']),
                 'F': set(['C', 'E'])}

        self.assertEqual({'A', 'C', 'B', 'E', 'D', 'F'}, dfs(graph, start_node='C'))
        self.assertEqual({'A', 'C', 'B', 'E', 'D', 'F'}, dfs(graph, start_node='D'))

        graph2 = {'A': set(['B', 'C']),
                  'B': set(),
                  'C': set()
                  }

        # Start node has no children, so just return the node.
        self.assertEqual({'B'}, dfs(graph2, start_node='B'))

        # Check correct parameter type.
        graph3 = {'A': 1}
        self.assertRaises(Exception, dfs, graph3, 'A')

    def test_bytes_dict_to_str(self):
        """
        Functional test for dict_to_str
        :return:
        """
        # test only changing values to strings (only strings will be converted, key2 of an int will be unchanged)
        str_dict = {b'key1': b'val1', b'key2': 2}
        self.assertEqual(bytes_dict_to_str(str_dict), {b'key1': 'val1', b'key2': 2})

        # test changing keys and values to strings
        self.assertEqual(bytes_dict_to_str(str_dict, keys_to_str=True), {'key1': 'val1', 'key2': 2})

        # plain string
        self.assertEqual(bytes_dict_to_str("abc"), "abc")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
