#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for db_ctp
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.dictmore import DictDot
from gadget.gizmo import MockVar, with_
from gadget.disk import Chdir
from gadget.helperclass import CaptureStdoutLog
from gadget.printmore import Dumper
from gadget.files import TempDir, File
from gadget.errors import ErrorInput
from gadget.gizmo import IS_WIN
from mod.db_ctp import *
from unittest.mock import Mock
import mod.db_ctp as db_ctp
from gadget.strmore import curtime
from os.path import basename
from mod.cci_list import CCI
import os
import re
import shutil
from pprint import pprint, pformat
from gadget.shell import SystemCall


@unittest.skipIf(IS_WIN, 'unix only')
class TestCgi(TestCase):
    """Call live url and make sure it works"""

    def atest_mock(self):
        # Print all the mock ww
        print()    # for unittest -v
        for ww in '2023.WW03.5 2023.WW04.1 2023.WW04.5 2023.WW05.5'.split():
            print(ww)
            result = call_json_api(f'https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi?ww={ww}&speedid=10043978')
            print(len(result))

    # @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='manual run only, may fail due to token', neg=False))
    @unittest.skip('Skip since we dont use hsd anymore')
    def test_basic_no_args(self):
        print()    # for unittest -v
        result = call_json_api('https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi')
        pprint(result)
        self.assertGreaterEqual(len(result['10047156']), 5)    # hsd always return 5 elements

    def test_basic_toc(self):
        print()    # for unittest -v
        result = call_json_api('https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi?toc=all')
        self.assertEqual(len(result), 1)    # always one element

    def test_basic_map(self):
        print()    # for unittest -v
        result = call_json_api('https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi?toc=map&speedid=10047156')
        self.assertEqual(len(result), 1)    # always one element

    def test_basic_ctp(self):
        print()    # for unittest -v
        result = call_json_api('https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi?toc=ww&speedid=10047156&socket=sds')
        self.assertEqual(len(result), 1)    # always one element

        # summary
        oneww = result[0]['contents'][0]['ww']
        result2 = call_json_api(f'https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi?ww={oneww}&speedid=10047156&override=True')
        self.assertGreater(len(result2), 0)
        self.assertNotIn('records', result2[0])
        self.assertNotIn('hsdrecords', result2[0])

        # detail
        oneww = result[0]['contents'][0]['ww']
        result2 = call_json_api(f'https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi?ww={oneww}&speedid=10047156&detail=True&socket=sds')
        self.assertIn('records', result2[0])       # CTP records
        self.assertIn('hsdrecords', result2[0])    # HSD records

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Different failure in nightly vs xterm", neg=False))
    def test_errorcase(self):
        print()
        with self.assertRaisesRegex(ErrorInput, '= Web output start ='):
            call_json_api('https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd_beta.cgi?ut=True&debug=True')


class Top:
    """Unittest Data for Top level record"""
    step = 'A'
    ww = '2023.ww12.3'
    socket = 'class'
    product = '123'
    tpname = 'MTLXXXXXXX37F0ASXXX'


class RecCtp:
    """Unittest Data for CTP Record"""
    module = 'ARR'
    testinstance = 't1'
    flags = 'Found'
    status = 'open'
    ErrorMessage = 'n/a'
    ContentExpect = 1
    ContentActual = 1
    ConditionComplete = False
    edc = False
    PorPlan = ''


class RecHsd:
    """Unittest Data for HSD Record"""
    title = 'title1'
    state = 'open'
    team = 'ARR'
    feature = 'somefeature'
    sd_plan = ''
    edc_plan = ''
    por_plan = ''
    socket = 'class'


class TestMain(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_ww_conditions(self):

        print('==== CASE1: speedid not found')
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.records = [RecCtp()]
        h1 = Top()
        h1.records = [RecHsd()]

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '1234',
                               'ww': '2023.ww12.3',
                               'socket': 'class'}, is_conn=False)
                result = obj.ww()

        expect = ''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

        print('==== CASE2: socket not found')
        CTPCache._data = None
        HSDCache._data = None
        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '123',
                               'ww': '2023.ww12.3',
                               'socket': 'sdt'}, is_conn=False)
                result = obj.ww()

        expect = ''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

        print('==== CASE3: detail')
        CTPCache._data = None
        HSDCache._data = None
        c1.socket = 'clasS'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '123',
                               'ww': '2023.ww12.3',
                               'socket': 'class',
                               'detail': 'True'}, is_conn=False)
                result = obj.ww()

        expect = '''[0].hsdrecords.[0].edc_plan = ''
[0].hsdrecords.[0].feature = 'somefeature'
[0].hsdrecords.[0].por_plan = ''
[0].hsdrecords.[0].sd_plan = ''
[0].hsdrecords.[0].state = 'open'
[0].hsdrecords.[0].team = 'ARR'
[0].hsdrecords.[0].title = 'title1'
[0].last_update = '2023.ww12.3'
[0].product = '123'
[0].records.[0].ConditionComplete = False
[0].records.[0].ContentActual = 1
[0].records.[0].ContentExpect = 1
[0].records.[0].ErrorMessage = 'n/a'
[0].records.[0].PorPlan = ''
[0].records.[0].edc = False
[0].records.[0].flags = 'Found'
[0].records.[0].module = 'ARR'
[0].records.[0].status = 'open'
[0].records.[0].testinstance = 't1'
[0].socket = 'clasS'
[0].step = 'A'
[0].summary.[0].POR = 0.0
[0].summary.[0].edc = 0.0
[0].summary.[0].edc_plan = 1.0
[0].summary.[0].enabled = 0.0
[0].summary.[0].feature = 'somefeature'
[0].summary.[0].por_plan = 1.0
[0].summary.[0].sd_plan = 1.0
[0].summary.[0].source = 'hsd'
[0].summary.[0].team = 'ARR'
[0].summary.[1].condition POR = 0.0
[0].summary.[1].condition edc = 1.0
[0].summary.[1].content POR = 0.0
[0].summary.[1].content edc = 1.0
[0].summary.[1].module = 'ARR'
[0].summary.[1].por_plan = 1.0
[0].summary.[1].source = 'codify'
[0].tpname = '37F0'
[0].ww = '2023.ww12.3'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_ww_multi(self):

        print('==== CASE1: 2 records match ww')
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.tpname = 'CRNT'
        c1.records = [RecCtp()]
        c2 = Top()
        c2.tpname = 'MTLXXXXXXX23E0DSXXX'
        c2.records = [RecCtp()]
        c3 = Top()
        c3.tpname = 'MTLXXXXXXX24E0DSXXX'
        c3.ww = '2023.ww12.4'
        c3.records = [RecCtp()]
        h1 = Top()
        h1.records = [RecHsd()]

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1, c2, c3])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '123',
                               'ww': '2023.ww12.3',
                               'socket': 'class'}, is_conn=False)
                result = obj.ww()
        self.assertEqual([x['tpname'] for x in result], ['CRNT', '23E0'])

        print('==== CASE2: 1 records match ww')
        CTPCache._data = None
        HSDCache._data = None
        with MockVar(CTP.objects, 'all', Mock(return_value=[c1, c2, c3])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '123',
                               'ww': '2023.ww12.4',
                               'socket': 'class'}, is_conn=False)
                result = obj.ww()
        self.assertEqual([x['tpname'] for x in result], ['24E0'])

        print('==== CASE3: today match')
        CTPCache._data = None
        HSDCache._data = None
        with MockVar(CTP.objects, 'all', Mock(return_value=[c1, c2, c3])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '123',
                               'ww': '2023.ww13.1',
                               'socket': 'class'}, is_conn=False)
                result = obj.ww()
        self.assertEqual([x['tpname'] for x in result], ['CRNT'])

        print('==== CASE4: not today')
        CTPCache._data = None
        HSDCache._data = None
        with MockVar(CTP.objects, 'all', Mock(return_value=[c2, c3])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '123',
                               'ww': '2023.ww13.1',
                               'socket': 'class'}, is_conn=False)
                result = obj.ww()
        self.assertEqual([x['tpname'] for x in result], ['24E0'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_ww_basic(self):

        print('==== CASE1: both ww are matched')
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.records = [RecCtp()]
        h1 = Top()
        h1.records = [RecHsd()]

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1])):
                obj = MainCgi({'speedid': '123',
                               'ww': '2023.ww12.3',
                               'socket': 'class'}, is_conn=False)
                result = obj.ww()

        expect = '''[0].last_update = '2023.ww12.3'
[0].product = '123'
[0].socket = 'class'
[0].step = 'A'
[0].summary.[0].POR = 0.0
[0].summary.[0].edc = 0.0
[0].summary.[0].edc_plan = 1.0
[0].summary.[0].enabled = 0.0
[0].summary.[0].feature = 'somefeature'
[0].summary.[0].por_plan = 1.0
[0].summary.[0].sd_plan = 1.0
[0].summary.[0].source = 'hsd'
[0].summary.[0].team = 'ARR'
[0].summary.[1].condition POR = 0.0
[0].summary.[1].condition edc = 1.0
[0].summary.[1].content POR = 0.0
[0].summary.[1].content edc = 1.0
[0].summary.[1].module = 'ARR'
[0].summary.[1].por_plan = 1.0
[0].summary.[1].source = 'codify'
[0].tpname = '37F0'
[0].ww = '2023.ww12.3'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

        print('==== CASE2: today, nothing matched for ww. Expect HSD is today and CTP is previous')
        CTPCache._data = None
        HSDCache._data = None
        hrec = {x: getattr(RecHsd, x) for x in dir(RecHsd)}
        hrec['feature'] = 'TODAY'
        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])), \
                MockVar(Hsd.objects, 'all', Mock(return_value=[h1])), \
                MockVar(HsdRead, 'read_hsd', Mock(return_value={'data': [hrec]})):
            obj = MainCgi({'speedid': '123',
                           'ww': '2023.ww13.1',     # Today
                           'socket': 'class'}, is_conn=False)
            result = obj.ww()
        expectx = '''
[0].last_update = '2023.ww12.3'
[0].product = '123'
[0].socket = 'class'
[0].step = 'A'
[0].summary.[0].condition POR = 0.0
[0].summary.[0].condition edc = 1.0
[0].summary.[0].content POR = 0.0
[0].summary.[0].content edc = 1.0
[0].summary.[0].module = 'ARR'
[0].summary.[0].por_plan = 1.0
[0].summary.[0].source = 'codify'
[0].tpname = '37F0'
[0].ww = '2023.ww13.1'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(),
                             expectx.replace('somefeature', 'TODAY').replace("ww = '2023.ww12.3", "ww = '2023.ww13.1"))

        print('==== CASE3: nothing matched for ww')
        CTPCache._data = None
        HSDCache._data = None
        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])), \
                MockVar(Hsd.objects, 'all', Mock(return_value=[h1])), \
                MockVar(HsdRead, 'read_hsd', Mock(return_value={})):
            obj = MainCgi({'speedid': '123',
                           'ww': '2023.ww12.4',     # no match
                           'socket': 'class'}, is_conn=False)
            result = obj.ww()
        expect4 = '''[0].last_update = '2023.ww12.3'
[0].product = '123'
[0].socket = 'class'
[0].step = 'A'
[0].summary.[0].POR = 0.0
[0].summary.[0].edc = 0.0
[0].summary.[0].edc_plan = 1.0
[0].summary.[0].enabled = 0.0
[0].summary.[0].feature = 'somefeature'
[0].summary.[0].por_plan = 1.0
[0].summary.[0].sd_plan = 1.0
[0].summary.[0].source = 'hsd'
[0].summary.[0].team = 'ARR'
[0].summary.[1].condition POR = 0.0
[0].summary.[1].condition edc = 1.0
[0].summary.[1].content POR = 0.0
[0].summary.[1].content edc = 1.0
[0].summary.[1].module = 'ARR'
[0].summary.[1].por_plan = 1.0
[0].summary.[1].source = 'codify'
[0].tpname = '37F0'
[0].ww = '2023.ww12.4'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect4)

        print('==== CASE4: hsd match only')
        CTPCache._data = None
        HSDCache._data = None
        h2 = Top()
        h2.records = [RecHsd()]
        h2.ww = '2023.ww12.4'
        h2.records[0].feature = 'THU Feature'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])), \
                MockVar(Hsd.objects, 'all', Mock(return_value=[h2])), \
                MockVar(HsdRead, 'read_hsd', Mock(return_value={})):
            obj = MainCgi({'speedid': '123',
                           'ww': '2023.ww12.4',     # no match
                           'socket': 'class'}, is_conn=False)
            result = obj.ww()

        self.assertTextEqual(Dumper(result, dot=True).string(),
                             expect.replace('somefeature', 'THU Feature').replace("ww = '2023.ww12.3", "ww = '2023.ww12.4"))

        print('==== CASE5: ctp match only with hsd')
        CTPCache._data = None
        HSDCache._data = None
        h2 = Top()
        h2.records = [RecHsd()]
        h2.ww = '2023.ww12.1'
        h2.records[0].feature = 'THU Feature'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])), \
                MockVar(Hsd.objects, 'all', Mock(return_value=[h2])), \
                MockVar(HsdRead, 'read_hsd', Mock(return_value={})):
            obj = MainCgi({'speedid': '123',
                           'ww': '2023.ww12.3',
                           'socket': 'class'}, is_conn=False)
            result = obj.ww()

        expect5 = expect4.replace('2023.ww12.4', '2023.ww12.3')
        expect5 = expect5.replace('somefeature', 'THU Feature')
        self.assertTextEqual(Dumper(result, dot=True).string(), expect5)

        print('==== CASE6: ctp match only without hsd')
        CTPCache._data = None
        HSDCache._data = None
        h2 = Top()
        h2.records = [RecHsd()]
        h2.ww = '2023.ww12.4'     # case5 is earlier which match. case6 is later.
        h2.records[0].feature = 'THU Feature'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])), \
                MockVar(Hsd.objects, 'all', Mock(return_value=[h2])), \
                MockVar(HsdRead, 'read_hsd', Mock(return_value={})):
            obj = MainCgi({'speedid': '123',
                           'ww': '2023.ww12.3',
                           'socket': 'class'}, is_conn=False)
            result = obj.ww()

        expect6 = '''[0].last_update = '2023.ww12.3'
[0].product = '123'
[0].socket = 'class'
[0].step = 'A'
[0].summary.[0].condition POR = 0.0
[0].summary.[0].condition edc = 1.0
[0].summary.[0].content POR = 0.0
[0].summary.[0].content edc = 1.0
[0].summary.[0].module = 'ARR'
[0].summary.[0].por_plan = 1.0
[0].summary.[0].source = 'codify'
[0].tpname = '37F0'
[0].ww = '2023.ww12.3'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect6)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    @unittest.skip('HSD is obsolete')
    def test_ww_todayhsd_detail(self):
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.records = [RecCtp()]
        h1 = None

        hrec = {x: getattr(RecHsd, x) for x in dir(RecHsd) if not x.startswith('_')}
        hrec['feature'] = 'TODAY'
        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])), \
                MockVar(Hsd.objects, 'all', Mock(return_value=[h1])), \
                MockVar(HsdRead, 'read_hsd', Mock(return_value={'data': [hrec]})):
            obj = MainCgi({'speedid': '123',
                           'ww': '2023.ww13.1',     # Today
                           'socket': 'class',
                           'detail': 'True'}, is_conn=False)
            result = obj.ww()

        expect = '''[0].hsdrecords.[0].edc_plan = ''
[0].hsdrecords.[0].feature = 'TODAY'
[0].hsdrecords.[0].por_plan = ''
[0].hsdrecords.[0].sd_plan = ''
[0].hsdrecords.[0].socket = 'class'
[0].hsdrecords.[0].state = 'open'
[0].hsdrecords.[0].team = 'ARR'
[0].hsdrecords.[0].title = 'title1'
[0].last_update = '2023.ww12.3'
[0].product = '123'
[0].records.[0].ConditionComplete = False
[0].records.[0].ContentActual = 1
[0].records.[0].ContentExpect = 1
[0].records.[0].ErrorMessage = 'n/a'
[0].records.[0].PorPlan = ''
[0].records.[0].edc = False
[0].records.[0].flags = 'Found'
[0].records.[0].module = 'ARR'
[0].records.[0].status = 'open'
[0].records.[0].testinstance = 't1'
[0].socket = 'class'
[0].step = 'A'
[0].summary.[0].POR = 0.0
[0].summary.[0].edc = 0.0
[0].summary.[0].edc_plan = 1.0
[0].summary.[0].enabled = 0.0
[0].summary.[0].feature = 'TODAY'
[0].summary.[0].por_plan = 1.0
[0].summary.[0].sd_plan = 1.0
[0].summary.[0].source = 'hsd'
[0].summary.[0].team = 'ARR'
[0].summary.[1].condition POR = 0.0
[0].summary.[1].condition edc = 1.0
[0].summary.[1].content POR = 0.0
[0].summary.[1].content edc = 1.0
[0].summary.[1].module = 'ARR'
[0].summary.[1].por_plan = 1.0
[0].summary.[1].source = 'codify'
[0].tpname = '37F0'
[0].ww = '2023.ww13.1'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_product(self):
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.product = 'mtl'
        c1.socket = 'CLASS'
        c2 = Top()
        c2.product = 'cfl'
        c2.socket = 'sds'
        h1 = Top()
        h1.product = 'mtl'
        h1.socket = 'CLASS'
        h2 = Top()
        h2.product = 'tgl'
        h2.socket = 'class'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1, c2])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1, h2])):
                obj = MainCgi({}, is_conn=False)
                result = obj.product()

        self.assertEqual(result, [{'contents': [{'socket': 'sds', 'speedid': '10043978'}]}])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_toc(self):
        # CASE1 - basic
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.product = '123'
        c1.socket = 'CLASS'
        c2 = Top()
        c2.product = '456'
        c2.socket = 'sds'
        h1 = Top()
        h1.product = '123'
        h1.socket = 'CLASS'
        h2 = Top()
        h2.product = '789'
        h2.socket = 'class'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1, c2])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=[h1, h2])):
                obj = MainCgi({'speedid': '123',
                               'socket': 'class'}, is_conn=False)
                result = obj.toc()

        expect = '''[0].contents.[0].tpname = '37F0'
[0].contents.[0].ww = '2023.ww12.3'
[0].contents.[1].tpname = 'CRNT'
[0].contents.[1].ww = '2023.ww13.1'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

        # CASE2: today != current
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.product = '123'
        c1.socket = 'CLASS'
        c1.tpname = 'CRNT'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=None)):   # unused
                obj = MainCgi({'speedid': '123',
                               'socket': 'class'}, is_conn=False)
                result = obj.toc()

        expect = '''[0].contents.[0].tpname = 'CRNT'
[0].contents.[0].ww = '2023.ww13.1'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

        # CASE3: one record and today
        CTPCache._data = None
        HSDCache._data = None
        c1 = Top()
        c1.product = '123'
        c1.socket = 'CLASS'

        with MockVar(CTP.objects, 'all', Mock(return_value=[c1])):
            with MockVar(Hsd.objects, 'all', Mock(return_value=None)):   # unused
                obj = MainCgi({'speedid': '123',
                               'socket': 'class'}, is_conn=False)
                result = obj.toc()

        expect = '''[0].contents.[0].tpname = '37F0'
[0].contents.[0].ww = '2023.ww12.3'
[0].contents.[1].tpname = 'CRNT'
[0].contents.[1].ww = '2023.ww13.1'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)


class TestUpload(TestCase):

    def test_stepping(self):
        self.assertEqual(UploadCtp.get_stepping('xx', '10047575'), 'A')
        self.assertEqual(UploadCtp.get_stepping('ARHSDSCB0H70A002412', '10047575'), 'B')
        self.assertEqual(UploadCtp.get_stepping('ARHSDSCX0H70A002412', '10047575'), 'A')
        self.assertEqual(UploadCtp.get_stepping('CRNT', '90047575'), 'A')
        # self.assertEqual(UploadCtp.get_stepping('CRNT', '10047575'), 'A')

    def test_stepping_default(self):

        with TempDir(name=True) as tdir:
            fname = f'{tdir}/output_ctp/10047574_b_class/872.csv'
            File(fname).touch(mkdir=True)
            obj = UploadCtp(fname)
            self.assertEqual(obj.stepping, 'B')
            self.assertEqual(obj.socket, 'class')
            self.assertEqual(obj.main(), 1)    # empty

            fname = f'{tdir}/output_ctp/10047574_class/872.csv'
            File(fname).touch(mkdir=True)
            obj = UploadCtp(fname)
            self.assertEqual(obj.stepping, 'A')
            self.assertEqual(obj.socket, 'class')


class TestDates(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_ww(self):
        # current date
        self.assertIn('ww', WW.get_ww())
        # specific date
        self.assertEqual(WW.get_ww(secs=1679406334), '2023.ww12.2')
        # specific date - with leading zero
        self.assertEqual(WW.get_ww(secs=1676814334), '2023.ww08.0')
        # file
        self.assertEqual(WW.get_ww(f'{UT_DIR}/misc_files/timestamp_check.txt'), '2022.ww27.3')

        # to_int
        self.assertEqual(WW.to_int('2023.ww12.0'), WW.to_int('2023120'))

    def test_ispast(self):
        # justin give dates, say dictionary like below
        dd = {'PO': '2023.WW12.1',
              'ES1': '2023.WW13.1'
              }

        # I have a data in record
        today = '2023.ww12.2'    # hardcoded for unittest
        self.assertEqual(WW.ispast(today, dd['PO']), 1)
        self.assertEqual(WW.ispast(today, dd['ES1']), 0)

    def test_adder(self):
        self.assertEqual(WW.to_int('2023011'), 107220.1)
        self.assertEqual(WW.to_int('2023011+20'), 107240.1)
        self.assertEqual(WW.to_int('2023011-20'), 107200.1)
        self.assertEqual(WW.to_int('2023011-20W'), 107200.1)
        self.assertEqual(WW.to_int('2023011-20w'), 107200.1)

        with MockVar(WW, 'opt', {'PO': '2023125', 'PRQ': '2023132'}):
            self.assertEqual(WW.get_milestone('PO'), '2023125')
            self.assertEqual(WW.get_milestone('PO+1'), '2023125+1')
            self.assertEqual(WW.get_milestone('PO-1'), '2023125-1')


class TestCompass(TestCase):

    # default cmap
    CMAP = {"SDS Enabled Plan": "cps_en_plan",
            "SDS EDC Plan": "cps_edc_plan",
            "SDS Kill Plan": "cps_por_plan",
            "SDS Enabled Actual": "cps_en",
            "SDS EDC Actual": "cps_edc",
            "SDS Kill Actual": "cps_por",
            "SDT Enabled Plan": "cps_en_plan",
            "SDT EDC Plan": "cps_edc_plan",
            "SDT Kill Plan": "cps_por_plan",
            "SDT Enabled Actual": "cps_en",
            "SDT EDC Actual": "cps_edc",
            "SDT Kill Actual": "cps_por",
            }

    def test_basic(self):
        with open(f'{UT_DIR_REPO}/misc_files/compass.jun18.json') as fh:
            data = json.load(fh)
        cmap = {k.lower(): v for k, v in self.CMAP.items() if k.startswith('SDS')}
        result = Compas.one_ww('10047156', '2023.ww23.1', 'ARRAY', 'A0', data, cmap)
        self.assertEqual(result, {'cps_edc': 0.031100000000000017,
                                  'cps_edc_plan': 0,
                                  'cps_en': 0.01429999999999998,
                                  'cps_en_plan': 0.02080000000000004,
                                  'cps_por': 0.8519,
                                  'cps_por_plan': 0.963,
                                  'source': 'compass'})

    def test_get_cmap(self):
        compass_map = [
            {
                "cps_skt": "sds",
                "cps_en_plan": "SDS Enabled Plan",
                "cps_edc_plan": "SDS EDC Plan",
                "cps_por_plan": "SDS Kill Plan",
                "cps_en": ["SDS Enabled Actual", "PHI"],
                "cps_edc": "SDS EDC Actual",
                "cps_por": "SDS Kill Actual"
            },
            {
                "cps_skt": "sdt",
                "cps_en_plan": "SDT Enabled Plan",
                "cps_edc_plan": "SDT EDC Plan",
                "cps_por_plan": "SDT Kill Plan",
                "cps_en": "SDT Enabled Actual",
                "cps_edc": "SDT EDC Actual",
                "cps_por": "SDT Kill Actual"
            }
        ]
        expect = {'PHI': 'cps_en',
                  'SDS EDC Actual': 'cps_edc',
                  'SDS EDC Plan': 'cps_edc_plan',
                  'SDS Enabled Actual': 'cps_en',
                  'SDS Enabled Plan': 'cps_en_plan',
                  'SDS Kill Actual': 'cps_por',
                  'SDS Kill Plan': 'cps_por_plan'}
        self.assertEqual(Compas.get_cmap(compass_map, 'sds'), {x.lower(): y for x, y in expect.items()})

    def test_unit(self):
        data = [{"product_code_plc": 10029931,
                 "stepping": "C0",
                 "biz_group_name": "Client",
                 "stage_id": "Post-Si",
                 "team_name": "ALL",
                 "dataset": [
                     {'dynamic_column': [{'name': 'SDT Kill Plan', 'value': 1.0},
                                         {'name': 'SDT EDC Plan', 'value': 2.0},
                                         {'name': 'SDS Kill Plan', 'value': 3.0},
                                         {'name': 'SDS Enabled Actual', 'value': 4.0},
                                         {'name': 'SDS EDC Plan', 'value': 5.0},
                                         {'name': 'SDS Enabled Plan', 'value': 6.0},
                                         {'name': 'PHI Plan', 'value': 7.0},
                                         {'name': 'SDT KILL Plan', 'value': 8.0}],
                      'yyww': 2306},
                 ]}]

        cmap = {k.lower(): v for k, v in self.CMAP.items() if k.startswith('SDS')}
        cmap["PHI Plan".lower()] = "cps_en_plan"    # one-to-many map
        result = Compas.one_ww('10029931', '2023.ww06.1', 'ALL', 'C0', data, cmap)
        self.assertEqual(result, {'cps_por_plan': 3.0,
                                  'cps_en': 4.0,
                                  'cps_edc_plan': 2.0,
                                  'cps_en_plan': 1.5,
                                  'cps_por': 0,
                                  'cps_edc': 0,
                                  'source': 'compass'})

    def test_unit2(self):
        # compass gives 95(por) 90(edc) 89(sd) this should return 95/0/0
        data = [{"product_code_plc": 10029931,
                 "stepping": "C0",
                 "biz_group_name": "Client",
                 "stage_id": "Post-Si",
                 "team_name": "ALL",
                 "dataset": [
                     {'dynamic_column': [{'name': 'SDS Kill Actual', 'value': 95},
                                         {'name': 'SDS EDC Actual', 'value': 90},
                                         {'name': 'SDS Kill Plan', 'value': 93},
                                         {'name': 'SDS Enabled Plan', 'value': 90},
                                         {'name': 'SDS Enabled Actual', 'value': 89}],
                      'yyww': 2306},
                 ]}]

        cmap = {k.lower(): v for k, v in self.CMAP.items() if k.startswith('SDS')}
        result = Compas.one_ww('10029931', '2023.ww06.1', 'ALL', 'C0', data, cmap)
        pprint(result)
        self.assertEqual(result, {'cps_edc': 0,
                                  'cps_edc_plan': 0,
                                  'cps_en': 0,
                                  'cps_en_plan': 0,
                                  'cps_por': 95.0,
                                  'cps_por_plan': 93.0,
                                  'source': 'compass'})

    def test_unit3(self):
        # compass gives 95(por) 96(edc) 98(sd) this should return 95/1/2
        data = [{"product_code_plc": 10029931,
                 "stepping": "C0",
                 "biz_group_name": "Client",
                 "stage_id": "Post-Si",
                 "team_name": "ALL",
                 "dataset": [
                     {'dynamic_column': [{'name': 'SDS Kill Actual', 'value': 95},
                                         {'name': 'SDS EDC Actual', 'value': 96},
                                         {'name': 'SDS Enabled Actual', 'value': 98}],
                      'yyww': 2306},
                 ]}]

        cmap = {k.lower(): v for k, v in self.CMAP.items() if k.startswith('SDS')}
        result = Compas.one_ww('10029931', '2023.ww06.1', 'ALL', 'C0', data, cmap)
        pprint(result)
        self.assertEqual(result, {'cps_edc': 1.0,
                                  'cps_edc_plan': 0,
                                  'cps_en': 2.0,
                                  'cps_en_plan': 0,
                                  'cps_por': 95.0,
                                  'cps_por_plan': 0,
                                  'source': 'compass'})


class TestOwnerTP(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        with TempDir(name=True) as tdir, \
                MockVar(OwnerTP, 'path_list', [tdir]), \
                MockVar(SystemCall, 'run_outonly', Mock(return_value='ccMailName = delos Reyes, John Q')):

            shutil.copytree(f'{UT_DIR}/SimpleNVL6', f'{tdir}/SimpleNVL6')
            File(f'{tdir}/SimpleNVL6/Module/ARR/ARR1/owner.txt').touch('owner: blah Members\nmanager: blah2 Members', mkdir=True)
            File(f'{tdir}/SimpleNVL6/Module/SCN/SCN1/InputFiles/owner.txt').touch('owner: a\nmanager: b', mkdir=True)
            res = OwnerTP().main('SimpleNVL6')
            expect = '''
{'ARR1': {'manager': 'blah2 Members', 'owner': 'blah Members'},
 'SCN1': {'manager': 'delos Reyes, John Q', 'owner': 'delos Reyes, John Q'}}
'''
            self.assertTextEqual(pformat(res), expect)


class TestOverrides(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_save(self):
        with TempDir(name=True) as tdir:
            oo = Overrides(None)
            oo.root = tdir
            oo.save()
            self.assertGreater(len(os.listdir(tdir)), 0)

    def test_override_codify(self):
        # CODIFY case - update, new and non-match

        with TempDir(name=True) as tdir:
            with MockVar(CtpRepo, 'REPO_PATH', tdir):
                File(f'{tdir}/ProductConfig/123.json').touch('''
[{"overrides": [
         {
            "socket": "sds",
            "mteam": "Sort TPI",
            "mheader": "DRV_RESET_C816SDT",
            "source": "codify",
            "condition POR": 999,
            "condition edc": 998
         },
         {
            "socket": "sds",
            "mteam": "Sort TPI",
            "mheader": "NEWMOD",
            "source": "codify",
            "condition POR": 997,
            "condition edc": 996
         },
         {
            "socket": "sdt",
            "mteam": "Sort TPI",
            "mheader": "NOMATCH_SDT_SOCKET",
            "source": "codify",
            "condition POR": 997,
            "condition edc": 996
         }
]
}]
''', mkdir=True)

                result = [
                    {
                        "tpname": "CRNT",
                        "product": "123",
                        "step": "A",
                        "socket": "sds",
                        "ww": "2023.ww19.2",
                        "summary": [
                            {
                              "source": "codify",
                              "module": "DRV_RESET_C816SDT",
                                "content POR": 0,
                                "content edc": 0,
                                "condition POR": 0.9,
                                "condition edc": 0.0,
                                "por_plan": 0.7
                            }
                        ]
                    }
                ]
                Overrides('123').override(result)
                expect = '''[{'product': '123',
  'socket': 'sds',
  'step': 'A',
  'summary': [{'condition POR': 999,
               'condition edc': 998,
               'content POR': 0,
               'content edc': 0,
               'module': 'DRV_RESET_C816SDT',
               'override': 'True',
               'por_plan': 0.7,
               'source': 'codify'},
              {'condition POR': 997,
               'condition edc': 996,
               'mheader': 'NEWMOD',
               'mteam': 'Sort TPI',
               'override': 'True',
               'socket': 'sds',
               'source': 'codify'}],
  'tpname': 'CRNT',
  'ww': '2023.ww19.2'}]'''
                self.assertTextEqual(pformat(result), expect)

    def test_override_codify2(self):
        # CODIFY case - with comma

        with TempDir(name=True) as tdir:
            with MockVar(CtpRepo, 'REPO_PATH', tdir):
                File(f'{tdir}/ProductConfig/123.json').touch('''
[{"overrides": [
         {
            "socket": "sds",
            "mteam": "Sort TPI",
            "mheader": "ARR_C,ARR_M",
            "module": "ARR_CXY",
            "source": "codify",
            "condition POR": 999,
            "condition edc": 998
         }
]
}]
''', mkdir=True)

                result = [
                    {
                        "tpname": "CRNT",
                        "product": "123",
                        "step": "A",
                        "socket": "sds",
                        "ww": "2023.ww19.2",
                        "summary": [
                            {
                                "source": "codify",
                                "module": "ARR_CXX",
                                "content POR": 0,
                                "content edc": 0,
                                "condition POR": 0.9,
                                "condition edc": 0.0,
                                "por_plan": 0.7
                            },
                            {
                                "source": "codify",
                                "module": "ARR_CXZ",
                                "content POR": 0,
                                "content edc": 0,
                                "condition POR": 0.9,
                                "condition edc": 0.0,
                                "por_plan": 0.7
                            }
                        ]
                    }
                ]
                Overrides('123').override(result)
                expect = '''
[{'product': '123',
  'socket': 'sds',
  'step': 'A',
  'summary': [{'condition POR': 999,
               'condition edc': 998,
               'content POR': 0,
               'content edc': 0,
               'module': 'ARR_CXX',
               'override': 'True',
               'por_plan': 0.7,
               'source': 'codify'},
              {'condition POR': 0.9,
               'condition edc': 0.0,
               'content POR': 0,
               'content edc': 0,
               'module': 'ARR_CXZ',
               'por_plan': 0.7,
               'source': 'codify'}],
  'tpname': 'CRNT',
  'ww': '2023.ww19.2'}]
'''
                self.assertTextEqual(pformat(result), expect)

    def test_override_compass(self):
        # compass case - update, new and non-match

        with TempDir(name=True) as tdir:
            with MockVar(CtpRepo, 'REPO_PATH', tdir):
                File(f'{tdir}/ProductConfig/123.json').touch('''
[{"overrides": [
         {
            "socket": "sds",
            "mteam": "Sort TPI",
            "source": "compass",
            "condition POR": 999,
            "condition edc": 998
         },
         {
            "socket": "sds",
            "mteam": "NEWTEAM",
            "source": "compass",
            "condition POR": 997,
            "condition edc": 996
         },
         {
            "socket": "sdt",
            "mteam": "NON_MATCH",
            "source": "compass",
            "condition POR": 997,
            "condition edc": 996
         }
]
}]
''', mkdir=True)

                result = [
                    {
                        "tpname": "CRNT",
                        "product": "123",
                        "step": "A",
                        "socket": "sds",
                        "ww": "2023.ww19.2",
                        "summary": [
                            {
                              "source": "compass",
                              "mteam": "Sort TPI",
                                "content POR": 0,
                                "content edc": 0,
                                "condition POR": 0.9,
                                "condition edc": 0.0,
                                "por_plan": 0.7
                            }
                        ]
                    }
                ]
                Overrides('123').override(result)
                expect = '''[{'product': '123',
  'socket': 'sds',
  'step': 'A',
  'summary': [{'condition POR': 999,
               'condition edc': 998,
               'content POR': 0,
               'content edc': 0,
               'mteam': 'Sort TPI',
               'override': 'True',
               'por_plan': 0.7,
               'source': 'compass'},
              {'condition POR': 997,
               'condition edc': 996,
               'mteam': 'NEWTEAM',
               'override': 'True',
               'socket': 'sds',
               'source': 'compass'}],
  'tpname': 'CRNT',
  'ww': '2023.ww19.2'}]'''
                self.assertTextEqual(pformat(result), expect)

    def test_override_hsd(self):
        # HSD case - update, new and non-match

        with TempDir(name=True) as tdir:
            with MockVar(CtpRepo, 'REPO_PATH', tdir):
                File(f'{tdir}/ProductConfig/123.json').touch('''
[{"overrides": [
         {
            "socket": "sds",
            "team": "Sort TPI",
            "mheader": "DRV_RESET_C816SDT",
            "source": "hsd",
            "condition POR": 999,
            "condition edc": 998
         },
         {
            "socket": "sds",
            "team": "Sort TPI New",
            "mheader": "NEWMOD",
            "source": "hsd",
            "condition POR": 997,
            "condition edc": 996
         },
         {
            "socket": "sdt",
            "team": "Sort TPI",
            "mheader": "NOMATCH_SDT_SOCKET",
            "source": "hsd",
            "condition POR": 997,
            "condition edc": 996
         }

]
}]
''', mkdir=True)

                result = [
                    {
                        "tpname": "CRNT",
                        "product": "123",
                        "step": "A",
                        "socket": "sds",
                        "ww": "2023.ww19.2",
                        "summary": [
                            {
                              "source": "hsd",
                              "team": "Sort TPI",
                                "content POR": 0,
                                "content edc": 0,
                                "condition POR": 0.9,
                                "condition edc": 0.0,
                                "por_plan": 0.7
                            }
                        ]
                    }
                ]
                Overrides('123').override(result)
                expect = '''[{'product': '123',
  'socket': 'sds',
  'step': 'A',
  'summary': [{'condition POR': 999,
               'condition edc': 998,
               'content POR': 0,
               'content edc': 0,
               'override': 'True',
               'por_plan': 0.7,
               'source': 'hsd',
               'team': 'Sort TPI'},
              {'condition POR': 997,
               'condition edc': 996,
               'mheader': 'NEWMOD',
               'override': 'True',
               'socket': 'sds',
               'source': 'hsd',
               'team': 'Sort TPI New'}],
  'tpname': 'CRNT',
  'ww': '2023.ww19.2'}]'''
                self.assertTextEqual(pformat(result), expect)

                # tpname is not CRNT, aka, historical
                result = [
                    {
                        "tpname": "20A",
                        "product": "123",
                        "step": "A",
                        "socket": "sds",
                        "ww": "2022.ww19.2",
                        "summary": [
                            {
                              "source": "hsd",
                              "team": "Sort TPI",
                                "content POR": 0,
                                "content edc": 0,
                                "condition POR": 0.9,
                                "condition edc": 0.0,
                                "por_plan": 0.7
                            }
                        ]
                    }
                ]
                Overrides('123').override(result)
                expect = '''[{'product': '123',
  'socket': 'sds',
  'step': 'A',
  'summary': [{'condition POR': 0.9,
               'condition edc': 0.0,
               'content POR': 0,
               'content edc': 0,
               'por_plan': 0.7,
               'source': 'hsd',
               'team': 'Sort TPI'}],
  'tpname': '20A',
  'ww': '2022.ww19.2'}]'''
                self.assertTextEqual(pformat(result), expect)


class TestSummary(TestCase):

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_tpname(self):
        self.assertEqual(Summary.tpname4('CRNT'), 'CRNT')
        self.assertEqual(Summary.tpname4('MTLXXXXXXX21G2CSXXX'), '21G2')
        self.assertEqual(Summary.tpname4('MTGSDSCB0H30B002309'), '30B0')

    def test_div_zero(self):
        self.assertEqual(Summary.div_zero(1, 1), 1)
        self.assertEqual(Summary.div_zero(1, 0), 0)
        self.assertEqual(Summary.div_zero(1, 0, True), None)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_ctp_blocked(self):
        with open(f'{UT_DIR_REPO}/xml_ut/ctp_2023.WW05.6.json') as fh:
            data = json.load(fh)
        result = Summary.ctp(data[0])
        expect = [{
            'product': 'Arrow Lake CPU-816 Die',
            'summary': [{'condition POR': 0.6666666666666666,
                         'condition blocked': 0.3333333333333333,
                         'condition edc': 0.0,
                         'content POR': 0.6666666666666666,
                         'content blocked': 0.3333333333333333,
                         'content edc': 0.0,
                         'module': 'ARR_ATOM_CXX',
                         'por_plan': 0.6666666666666666,
                         'source': 'codify'},
                        {'condition POR': 1.0,
                         'condition edc': 0.0,
                         'content POR': None,
                         'content edc': None,
                         'module': 'CLK',
                         'por_plan': 1.0,
                         'source': 'codify'},
                        {'condition POR': 0.5,
                         'condition edc': 0.5,
                         'content POR': 0.5,
                         'content edc': 0.25,
                         'module': 'SCN_CORE_C68',
                         'por_plan': 1.0,
                         'source': 'codify'}],
            'socket': 'sds',
            'step': 'A',
            'tpname': '21FX',
            'ww': '2023.ww5.5'}]
        self.maxDiff = None
        self.assertEqual(result, expect)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_ctp_noexpect(self):
        with open(f'{UT_DIR_REPO}/xml_ut/ctp_2023.WW33.1.json') as fh:
            data = json.load(fh)
        result = Summary.ctp(data[0])
        expect = [{
            'product': 'Arrow Lake CPU-816 Die',
            'summary': [{'condition POR': 1.0,
                         'condition edc': 0.0,
                         'content POR': 1.0,
                         'content edc': 0.0,
                         'module': 'ARR_ATOM_CXX',
                         'por_plan': 0.6666666666666666,
                         'source': 'codify'},
                        {'condition POR': 1.0,
                         'condition edc': 0.0,
                         'content POR': None,
                         'content edc': None,
                         'module': 'CLK',
                         'por_plan': 1.0,
                         'source': 'codify'},
                        {'condition POR': 0.5,
                         'condition edc': 0.5,
                         'content POR': 0.5,
                         'content edc': 0.25,
                         'module': 'SCN_CORE_C68',
                         'por_plan': 1.0,
                         'source': 'codify'}],
            'socket': 'sds',
            'step': 'A',
            'tpname': '21FX',
            'ww': '2023.ww5.5'}]
        self.maxDiff = None
        self.assertEqual(result, expect)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_ctp1(self):
        with open(f'{UT_DIR_REPO}/xml_ut/ctp_2023.WW05.5.json') as fh:
            data = json.load(fh)
        result = Summary.ctp(data[0])
        expect = [{
            'product': 'Arrow Lake CPU-816 Die',
            'summary': [{'condition POR': 1.0,
                         'condition edc': 0.0,
                         'content POR': 1.0,
                         'content edc': 0.0,
                         'module': 'ARR_ATOM_CXX',
                         'por_plan': 0.6666666666666666,
                         'source': 'codify'},
                        {'condition POR': 1.0,
                         'condition edc': 0.0,
                         'content POR': None,
                         'content edc': None,
                         'module': 'CLK',
                         'por_plan': 1.0,
                         'source': 'codify'},
                        {'condition POR': 0.5,
                         'condition edc': 0.5,
                         'content POR': 0.5,
                         'content edc': 0.25,
                         'module': 'SCN_CORE_C68',
                         'por_plan': 1.0,
                         'source': 'codify'}],
            'socket': 'sds',
            'step': 'A',
            'tpname': '21FX',
            'ww': '2023.ww5.5'}]
        self.maxDiff = None
        self.assertEqual(result, expect)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_ctp2(self):
        with open(f'{UT_DIR_REPO}/xml_ut/ctp_2023.WW04.5.json') as fh:
            data = json.load(fh)
        result = Summary.ctp(data[0])
        expect = [{
            'product': 'Arrow Lake CPU-816 Die',
            'summary': [{'condition POR': 0.3333333333333333,
                         'condition edc': 0.0,
                         'content POR': 0.3333333333333333,
                         'content edc': 0.0,
                         'module': 'ARR_ATOM_CXX',
                         'por_plan': 0.3333333333333333,
                         'source': 'codify'},
                        {'condition POR': 0.0,
                         'condition edc': 0.5,
                         'content POR': None,
                         'content edc': None,
                         'module': 'CLK',
                         'por_plan': 1.0,
                         'source': 'codify'},
                        {'condition POR': 0.5,
                         'condition edc': 0.5,
                         'content POR': 0.5,
                         'content edc': 0.25,
                         'module': 'SCN_CORE_C68',
                         'por_plan': 1.0,
                         'source': 'codify'}],
            'socket': 'sds',
            'step': 'A',
            'tpname': '21EX',
            'ww': '2023.ww4.5'}]
        self.maxDiff = None
        self.assertEqual(result, expect)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_hsd_blocked(self):
        with open(f'{UT_DIR_REPO}/xml_ut/hsd_2023.WW04.6.json') as fh:
            data = json.load(fh)
        result = Summary.hsd(data['data'])
        expect = '''[0].POR = 0.0
[0].edc = 0.0
[0].edc_plan = 0.0
[0].enabled = 1.0
[0].feature = 'LJPLL - SOC - CMT'
[0].por_plan = 0.0
[0].sd_plan = 0.0
[0].source = 'hsd'
[0].team = 'clock'
[1].POR = 0.3333333333333333
[1].edc = 0.3333333333333333
[1].edc_plan = 0.0
[1].enabled = 0.0
[1].feature = ''
[1].por_plan = 1.0
[1].sd_plan = 0.0
[1].source = 'hsd'
[1].team = 'scan'
[2].POR = 0.3333333333333333
[2].edc = 0.3333333333333333
[2].edc_plan = 0.0
[2].enabled = 0.0
[2].feature = 'LNC'
[2].por_plan = 0.0
[2].sd_plan = 0.0
[2].source = 'hsd'
[2].team = 'array'
[3].POR = 0.5
[3].blocked = 0.5
[3].edc = 0.0
[3].edc_plan = 0.0
[3].enabled = 0.0
[3].feature = 'LJPLL - RWC'
[3].por_plan = 1.0
[3].sd_plan = 0.0
[3].source = 'hsd'
[3].team = 'clock'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_hsd(self):
        with open(f'{UT_DIR_REPO}/xml_ut/hsd_2023.WW04.5.json') as fh:
            data = json.load(fh)
        result = Summary.hsd(data['data'])
        expect = '''[0].POR = 0.0
[0].edc = 0.0
[0].edc_plan = 0.0
[0].enabled = 1.0
[0].feature = 'LJPLL - SOC - CMT'
[0].por_plan = 0.0
[0].sd_plan = 0.0
[0].source = 'hsd'
[0].team = 'clock'
[1].POR = 0.3333333333333333
[1].edc = 0.3333333333333333
[1].edc_plan = 0.0
[1].enabled = 0.0
[1].feature = ''
[1].por_plan = 1.0
[1].sd_plan = 0.0
[1].source = 'hsd'
[1].team = 'scan'
[2].POR = 0.3333333333333333
[2].edc = 0.3333333333333333
[2].edc_plan = 0.0
[2].enabled = 0.0
[2].feature = 'LNC'
[2].por_plan = 0.0
[2].sd_plan = 0.0
[2].source = 'hsd'
[2].team = 'array'
[3].POR = 0.5
[3].edc = 0.5
[3].edc_plan = 0.0
[3].enabled = 0.0
[3].feature = 'LJPLL - RWC'
[3].por_plan = 1.0
[3].sd_plan = 0.0
[3].source = 'hsd'
[3].team = 'clock'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)

    @with_(MockVar, WW, 'today', Mock(return_value=1679953853))    # ww13.1
    def test_hsd_date(self):
        with open(f'{UT_DIR_REPO}/xml_ut/hsd_2023.WW04.5_date.json') as fh:
            data = json.load(fh)
        with MockVar(WW, 'opt', {'PO': '2023125', 'PRQ': '2023132'}):
            result = Summary.hsd(data['data'])
        expect = '''[0].POR = 0.0
[0].edc = 0.0
[0].edc_plan = 0.0
[0].enabled = 1.0
[0].feature = 'LJPLL - SOC - CMT'
[0].por_plan = 0.0
[0].sd_plan = 0.0
[0].source = 'hsd'
[0].team = 'clock'
[1].POR = 0.3333333333333333
[1].edc = 0.3333333333333333
[1].edc_plan = 0.0
[1].enabled = 0.0
[1].feature = ''
[1].por_plan = 1.0
[1].sd_plan = 0.0
[1].source = 'hsd'
[1].team = 'scan'
[2].POR = 0.3333333333333333
[2].edc = 0.3333333333333333
[2].edc_plan = 0.0
[2].enabled = 0.0
[2].feature = 'LNC'
[2].por_plan = 0.0
[2].sd_plan = 0.6666666666666666
[2].source = 'hsd'
[2].team = 'array'
[3].POR = 0.5
[3].edc = 0.5
[3].edc_plan = 0.0
[3].enabled = 0.0
[3].feature = 'LJPLL - RWC'
[3].por_plan = 1.0
[3].sd_plan = 0.5
[3].source = 'hsd'
[3].team = 'clock'
'''
        self.assertTextEqual(Dumper(result, dot=True).string(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
