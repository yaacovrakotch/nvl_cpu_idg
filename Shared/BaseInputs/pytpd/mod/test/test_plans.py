#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for plans.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from mod.plans import *
lno_test = Plan('CHK*F3', module='ARR')       # Do not change location since line number is checked
from tp.testprogram import TestProgram, Env
from main.tp_plans import TPPlans
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.tputil import trimut
from gadget.dictmore import DictDot
from gadget.printmore import Dumper
from unittest.mock import Mock
from mod.setting import cfg
from os.path import join, normpath
import mod.plans as plans
import sys
from pprint import pprint
from collections import OrderedDict


def modwaiver():
    modwaiver = DictDot()
    modwaiver.weight_content = {'SCN': 10}
    modwaiver.weight_feature = {'SCN': 5}
    modwaiver.buckets = {}
    modwaiver.trust_locations = {'chot': 'CLASSHOT'}
    return modwaiver


class TestPlans(TestCase):

    def test_repr(self):
        ModuleName('ARR_FUN')
        obj = Plan('CHK*F3', voltage_corner='min', freq='1000', _utlno=1)
        self.assertEqual(f'{obj}', "Plan('CHK*F3', id_lno=1, module=ARR_FUN, voltage_corner=min, freq=1000)")
        self.assertEqual(f'{lno_test}', "Plan('CHK*F3', id_lno=7, module=ARR)")
        obj1 = Plan('CHK*F3', voltage_corner='min', something=23, content_expect=2, _utlno=1)
        self.assertEqual(f'{obj1}', "Plan('CHK*F3', id_lno=1, module=ARR_FUN, voltage_corner=min, something=23)")
        self.assertEqual(list(OrderedDict(obj1.items())),     # make sure that items() work with OrderDict()
                         ['name', 'id_lno', 'module', 'content_expect', 'multiple_match', 'voltage_corner', 'something'])

    def test_module_conditional(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        TP.set_tp(TestProgram(tpf).pickle_init())
        self.assertEqual(TP.get_tp().get_name(), 'Simple1Real')
        # default
        ModuleName('ARR_FUN')
        self.assertEqual(ModuleName.get_name(), 'ARR_FUN')
        # conditional
        print(TP.loc())
        ModuleName('ARR_FUN', {'BORING': TP.loc() == 'CLASSHOT'})
        self.assertEqual(ModuleName.get_name(), 'BORING')
        ModuleName('ARR_FUN', {'BORING': TP.loc() == 'CLASSCOLD'})
        self.assertEqual(ModuleName.get_name(), 'ARR_FUN')

    def test_binmatrix_lowest(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        bindata = {'2001': {'ATOMC_CORE_SELECT': 'A1'},
                   '2002': {'ATOMC_CORE_SELECT': 'A2'},
                   '2003': {'ATOMC_CORE_SELECT': 'A3'},
                   '2004': {'ATOMC_CORE_SELECT': 'A4'}}

        with MockVar(tp, 'bin_matrix', Mock(return_value=bindata)):
            planobj = PlanReport(tp)
            obj = Plan('CHK*F3', content_expect=1, _utlno=1, module='ARR', TestMode='{ATOMC_CORE_SELECT}')
            data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {}, 'TestMode': 'Q'}
            self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                             "Plan('CHK*F3', id_lno=1, module=ARR): TestMode mismatch [A4] vs tp:[Q]")

            obj = Plan('CHK*F3', content_expect=1, _utlno=1, module='ARR', TestMode='{ATOMC_CORE_SELECT}')
            data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'speedflow': '2002'}, 'TestMode': 'Q'}
            self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                             "Plan('CHK*F3', id_lno=1, module=ARR): TestMode mismatch [A2] vs tp:[Q]")

    def test_feature_eval_mtt(self):
        # tests the eval portion. olb_bin_type is from binmatrix - Mocked
        # bug found by Sudheer 6/18
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        planobj = PlanReport(tp)

        bmd = {'1001': {'BOMGroupName': 'CLASS_TGLH81', 'FlowIndex': '1', 'olb_bin': '1', 'olb_bin_type': 'Y'},
               '1002': {'BOMGroupName': 'CLASS_TGLH81', 'FlowIndex': '1', 'olb_bin': '1', 'olb_bin_type': 'R'}}
        with MockVar(planobj.tpobj, 'bin_matrix', Mock(return_value=bmd)):

            # with speedflow
            obj = Plan('CHK*F3', content_expect=1, _utlno=1, module='ARR', TestMode='{olb_bin_type}')
            data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'speedflow': '1001'}, 'TestMode': 'Q'}
            self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                             "Plan('CHK*F3', id_lno=1, module=ARR): TestMode mismatch [Y] vs tp:[Q]")

            # another speedflow, same object
            data = {'_CORNER': 'nom', '_FREQ': '1002', 'namefield': {'speedflow': '1002'}, 'TestMode': 'Q'}
            self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                             "Plan('CHK*F3', id_lno=1, module=ARR): TestMode mismatch [R] vs tp:[Q]")

    def test_feature_eval(self):
        # tests the eval portion. olb_bin_type is from binmatrix
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        planobj = PlanReport(tp)
        print("Bom info: ====")
        print(planobj.tpobj.bin_matrix(planobj.tpobj.get_bom()))

        # with speedflow
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, module='ARR', TestMode='{olb_bin_type}')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'speedflow': '1001'}, 'TestMode': 'Q'}
        self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): TestMode mismatch [B] vs tp:[Q]")

        # no speedflow
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, module='ARR', TestMode='{olb_bin_type}')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'speedflow': ''}, 'TestMode': 'Q'}
        self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): TestMode mismatch [B] vs tp:[Q]")

        # speedflow not found in binmatrix
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, module='ARR', TestMode='{olb_bin_type}')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'speedflow': '1002'}, 'TestMode': 'Q'}
        self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): TestMode mismatch [VARIABLE_NOT_DEFINED 'olb_bin_type' in '{olb_bin_type}'] vs tp:[Q]")

        # attribute
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, module='ARR', corner='{olb_bin_type}')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'corner': 'Z'}}
        self.assertEqual(obj.feature_match('blah', data, {}, planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): corner mismatch [B] vs tp:[Z]")

    def test_feature_match(self):
        ModuleName('ARR_FUN')
        # freq
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, freq='1000')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'freq': '1000'}}
        self.assertEqual(obj.feature_match('*', data, {}), 'MATCH')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'freq': '1001'}}
        self.assertEqual(obj.feature_match('*', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): freq mismatch [1000] vs tp:[1001]")

        # corner
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, corner='F1')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'corner': 'F1'}}
        self.assertEqual(obj.feature_match('*', data, {}), 'MATCH')
        data = {'_CORNER': 'nom', '_FREQ': '1001', 'namefield': {'corner': 'F2'}}
        self.assertEqual(obj.feature_match('*', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): corner mismatch [F1] vs tp:[F2]")

        # voltage
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, voltage_corner='nom')
        data = {'_CORNER': 'nom', '_FREQ': '1001'}
        self.assertEqual(obj.feature_match('*', data, {}), 'MATCH')
        data = {'_CORNER': 'max', '_FREQ': '1000'}
        self.assertEqual(obj.feature_match('*', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): voltage_corner mismatch [nom] vs tp:[max]")

        # ifpm_modifygroups
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, ifpm_modifygroups='*VAL_0_4GHz!0.5G')
        data = {'ifpm_modifygroups': "bt!core_ratio_VAL_0_4GHz!0.5G"}
        self.assertEqual(obj.feature_match('ABC', data, {}), 'MATCH')
        data = {'ifpm_modifygroups': "bt!core_ratio_VAX_0_4GHz!0.5G"}
        self.assertEqual(obj.feature_match('ABC', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): ifpm_modifygroups mismatch [*VAL_0_4GHz!0.5G] vs tp:[bt!core_ratio_VAX_0_4GHz!0.5G]")

        # Exact match but not a match by Dhanya
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, ifpm_modifygroups='bt(abc)')
        data = {'ifpm_modifygroups': "bt(abc)"}
        self.assertEqual(obj.feature_match('ABC', data, {}), 'MATCH')

        # numeric param - 9/7/23
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, nparam='-1')
        data = {'nparam': -1}
        self.assertEqual(obj.feature_match('ABC', data, {}), 'MATCH')

        # number comparison - 9/7/23
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, nparam='1.0', mparam='1.00')
        data = {'nparam': '1', 'mparam': 1}
        self.assertEqual(obj.feature_match('ABC', data, {}), 'MATCH')

        # not set - 9/7/23
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, nparam='NOT_SET')
        data = {'Xparam': '1'}
        self.assertEqual(obj.feature_match('ABC', data, {}), 'MATCH')
        data = {'nparam': ''}
        self.assertEqual(obj.feature_match('ABC', data, {}), 'MATCH')
        data = {'nparam': '1'}
        self.assertEqual(obj.feature_match('ABC', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): nparam mismatch [NOT_SET] vs tp:[1]")

        # level (special map to levels)
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, level='*DIS*4')
        data = {'levels': "CRX3_F6:MULTIPASSDISABLECORE_4"}
        self.assertEqual(obj.feature_match('', data, {}), 'MATCH')
        data = {'levels': "CRX3_F6:MULTIPASSDISABLECORE_5"}
        self.assertEqual(obj.feature_match('', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): level mismatch [*DIS*4] vs tp:[CRX3_F6:MULTIPASSDISABLECORE_5]")

        # SetPointsPreInstance
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, SetPointsPreInstance='*cde*')
        data = {'SetPointsPreInstance': "abcdef"}
        self.assertEqual(obj.feature_match('', data, {}), 'MATCH')
        data = {'SetPointsPreInstance': "c.*f"}
        self.assertEqual(obj.feature_match('', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): SetPointsPreInstance mismatch [*cde*] vs tp:[c.*f]")

        # SetPointsPreInstance - partial match, should fail
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, SetPointsPreInstance='cde')
        data = {'SetPointsPreInstance': "abcdef"}
        self.assertEqual(obj.feature_match('', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): SetPointsPreInstance mismatch [cde] vs tp:[abcdef]")

        # TestMode - temporary because of default
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, TestMode='SingleVmin')
        data = {}
        self.assertEqual(obj.feature_match('', data, {}), 'MATCH')
        data = {'TestMode': "other"}
        self.assertEqual(obj.feature_match('', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): TestMode mismatch [SingleVmin] vs tp:[other]")

        # lowercase / uppercase by MikeR
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, ifpm_modifyGRoups='bt(abc)')
        data = {'ifpm_modifygrouPS': "bt(abc)"}
        self.assertEqual(obj.feature_match('ABC', data, {}), 'MATCH')

        # LEvel (special map to levels)
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, LEvel='*DIS*4')
        data = {'levels': "CRX3_F6:MULTIPASSDISABLECORE_4"}
        self.assertEqual(obj.feature_match('', data, {}), 'MATCH')

        # regex issue, gating TP
        obj = Plan('CHK*F3', content_expect=1, _utlno=1, ifpm_modifyGRoups='bt(abc')
        data = {'ifpm_modifygrouPS': "bt(abc)"}
        self.assertEqual(obj.feature_match('ABC', data, {}),
                         "Plan('CHK*F3', id_lno=1, module=ARR_FUN): ifpm_modifyGRoups mismatch [bt(abc] vs tp:[bt(abc)]")

        # content_expect missing
        # obj = Plan('CHK*F3', _utlno=1)
        # data = {'SetPointsPreInstance': "abcdef", 'patlist': 'something'}
        # self.assertEqual(obj.feature_match('', data, {}),
        #                  "Plan('CHK*F3', id_lno=1, module=ARR_FUN): has no content_expect")

    def test_failflow(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        passfail = {('ARR', 'CCA'): 'P',     # pass flow
                    ('ARR', 'CCB'): 'F',
                    ('ARR', 'TPIE_PgmRules'): 'B'}
        planobj = PlanReport(tp, passfail=passfail)

        # plan is passflow
        obj1 = Plan('CCA', content_expect=1, _utlno=1, module='ARR')
        obj2 = Plan('CCB', content_expect=1, _utlno=1, module='ARR')
        obj3 = Plan('TPIE_PgmRules', _utlno=1, module='ARR')
        self.assertEqual(obj1.feature_match('CCA', {}, {}, planobj), 'MATCH')
        self.assertEqual(obj2.feature_match('CCB', {}, {}, planobj),
                         "Plan('CCB', id_lno=1, module=ARR): is in failflow of testprogram")
        self.assertEqual(obj3.feature_match('TPIE_PgmRules', {}, {}, planobj),
                         "Plan('TPIE_PgmRules', id_lno=1, module=ARR): is bypassed")

        # plan is failflow
        obj1 = Plan('CCA', content_expect=1, _utlno=1, module='ARR', failflow=True)   # this is passflow in TP
        obj2 = Plan('CCB', content_expect=1, _utlno=1, module='ARR', failflow=True)
        self.assertEqual(obj1.feature_match('CCA', {}, {}, planobj), 'MATCH')
        self.assertEqual(obj2.feature_match('CCB', {}, {}, planobj), 'MATCH')

    def test_analyze_voltage_usrv(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        planobj = PlanReport(tp)
        obj = Plan('CHK*F3', _utlno=1, voltage='p_vccio_spec=1.20', module='ARR')
        self.assertEqual(obj.analyze_voltage('MATCH', 'BASE::tc2', planobj),
                         'MATCH')
        obj = Plan('CHK*F3', _utlno=1, voltage='p_vccio_spec=1.40', module='ARR')
        self.assertEqual(obj.analyze_voltage('MATCH', 'BASE::tc2', planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): voltage mismatch [1.4] vs tp:[1.2]")
        self.assertEqual(obj.feature_match('CCA', {'level': 'BASE::tc2'}, {}, planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): voltage mismatch [1.4] vs tp:[1.2]")
        obj = Plan('CHK*F3', _utlno=1, voltage='p_vccio_spec=1.2V', module='ARR')
        self.assertEqual(obj.analyze_voltage('MATCH', 'BASE::tc2', planobj),
                         'MATCH')
        obj = Plan('CHK*F3', _utlno=1, voltage='p_vccio_specx=1.2V', module='ARR')
        self.assertEqual(obj.analyze_voltage('MATCH', 'BASE::tc2', planobj),
                         'EXCEPTION on get_tc_value(): param [p_vccio_specx] not found in [BASE::STF_univ_lvl_BFUNC] SpecificationSet')

        # usrv
        obj = Plan('CHK*F3', _utlno=1, usrv='SCVars.SC_FABID=X', module='ARR')
        self.assertEqual(obj.feature_match('CCA', {}, {}, planobj),
                         'MATCH')
        obj = Plan('CHK*F3', _utlno=1, usrv='SCVars.SC_FABID=Y', module='ARR')
        self.assertEqual(obj.feature_match('CCA', {}, {}, planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): usrv mismatch SCVars.SC_FABID=[Y] vs tp:[X]")
        obj = Plan('CHK*F3', _utlno=1, usrv='SCVars.SC_FABXX=Y', module='ARR')
        self.assertEqual(obj.feature_match('CCA', {}, {}, planobj),
                         "Plan('CHK*F3', id_lno=1, module=ARR): usrv mismatch SCVars.SC_FABXX=[Y] vs tp:[<NOT_IN_INSTANCE>]")


class TestWaiver(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', voltage_corner='nom', content_expect=5, module='SCN', _utlno=2)
        wv = Waiver('SCN', 'C*B', reason='testing')
        with CaptureStdoutLog() as p:
            pr.main()

        self.assertEqual(f'{wv}', "Waiver('C*B', module=SCN, name=C*B, reason=testing)")
        expect = f"""TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for SCN:
   Content rollup POR:     0/15
   Content rollup Enabled: 6/15
   Feature rollup POR:     0/2
   Feature rollup Enabled: 2/2
   Feature found  Total:   2/2
Result w/ waiver:
   Content rollup POR:     0/10
   Content rollup Enabled: 3/10
   Feature rollup POR:     0/1
   Feature rollup Enabled: 1/1
Missing from testprogram:
   None
Missing from testplan:
   None
Feature misses:
   None"""

        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

        # Write the initial .csv to be read
        initial = """
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR,ARR,0,25,26,25,0,22,22,22

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,ARR,ARR,0,25,26,25,0,22,22,22,ARR
"""
        File(csvfile).touch(initial)

        # Write the csv
        csv.write(True)
        expect = """
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR,ARR,0,25,26,25,0,22,22,22
Summary,SCN,SCN,0,15,6,15,0,2,2,2
SummaryTotal,,,0,40,32,40,0,24,24,24
WeightedPct,,,,0.0%,,4.0%,,0.0%,,5.0%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,ARR,ARR,0,25,26,25,0,22,22,22,ARR
ModSummary,SCN,SCN,0,15,6,15,0,2,2,2,SCN

HeadModW,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModWaived,ARR,ARR,0,25,26,25,0,22,22,22,ARR
ModWaived,SCN,SCN,0,10,3,10,0,1,1,1,SCN

HeadFound,Module,Team,tid_count,tid_expect,PorEn,POR_plan,TestName
FoundPlan,SCN,SCN,3,10,En,,CCA
FoundPlan,SCN,SCN,3,5,En,,CCB
"""
        self.assertTextEqual(File(csvfile).read(), expect)

    def test_miss(self):
        plans.BasePlans.clear()
        Waiver.wobj_list.clear()
        obj1 = Plan('CHK*F3', module='ARR_FUN')
        obj2 = Plan('CHK*F4', module='ARR_FUN', edc=True)
        obj3 = Plan('CHK*F3', module='ARR_X1')
        Waiver('ARR_FUN', 'CHK*F3', reason='valid')
        Waiver('ARR_FUN', 'CHK*F5', reason='not found in testplan')

        self.assertEqual(Waiver.is_waived(obj1), True)
        self.assertEqual(Waiver.is_waived(obj2), False)
        self.assertEqual(Waiver.is_waived(obj3), False)

        with CaptureStdoutLog() as p:
            Waiver.check_waivers()
        print(p.getvalue())
        expect = '''Waivers not found in this testplan:
   1. Waiver('CHK*F5', module=ARR_FUN, name=CHK*F5, reason=not found in testplan)

'''
        self.assertTextEqual(p.getvalue(), expect)

        # repr
        obj = Waiver('ARR_FUN', 'CHK*F3', reason='valid')
        self.assertEqual(str(obj), "Waiver('CHK*F3', module=ARR_FUN, name=CHK*F3, reason=valid)")

    def test_eta(self):
        Waiver.wobj_list.clear()
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1, por_plan='PO', eta=203052)
        Plan(name='C*B', voltage_corner='nom', content_expect=20, module='SCN', _utlno=2, eta=202101)
        pr.main()

        Dumper(csv.items)
        self.assertEqual(csv.items, [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', 'PO', 'CCA'],
                                     ['FoundPlan', 'SCN', 'SCN', 3, 20, 'En', '', 'CCB'],
                                     ['ModWaived', 'SCN', 'SCN', 0, 20, 3, 20, 0, 1, 1, 1, 'SCN'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 30, 6, 30, 0, 2, 2, 2, 'SCN']])


class TestCsv(TestCase):
    """Contain unitttests specific to csv. See test_plan() for integration."""

    def test_module(self):
        csv = CsvPlan()
        csv.write(True)   # Should not fail
        self.assertEqual(csv.get_module("Plan('D*C', id_lno=1, module=SCN_AR)"), 'SCN_AR')
        self.assertEqual(csv.get_module("Plan()"), 'CANT_DERIVE_MODULE')

    def test_timestamp(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'a')).touch(mtime=1631760960)
            f2 = File(join(tdir, 'b')).touch(mtime=1631761970)
            final = [['Summary', 'SCN_ABC', 'SCN'] + list(range(8)),
                     ['Summary', 'SCN_GHI', 'SCN'] + list(range(8)),
                     ['Summary', 'SCN_JKL', 'SCN'] + list(range(8)),
                     ['TimeStamp', 'SCN_ABC', 'SCN', 1, 1, 1, 2],
                     ['TimeStamp', 'SCN_JKL', 'SCN', 2, 2, 1, 2]]

            csv.items = [['Summary', 'SCN_ABC', 'SCN'] + list(range(8)),
                         ['Summary', 'SCN_GHI', 'SCN'] + list(range(8))]
            csv.mod2fname = {'SCN_ABC': f1.get_name(),
                             'SCN_GHI': f2.get_name()}
            csv.timestamp_update(final)
            self.assertEqual([x[0] for x in csv.headers(final)], 'HeadSummary HeadTimeStamp'.split())
            pprint(final)
            self.assertEqual(len([x for x in final if x[0] == 'TimeStamp']), 5)

    def test_compute_summary(self):
        csv = CsvPlan()
        final = []
        final.append('Summary,mod,mod,1,2,3,4,5,6,7,8'.split(','))
        final.append('Summary,mod2,mod2,1,1,1,1,1,1,1,1'.split(','))
        final.append('HeadMissingTP,Module,Team,is_waive,X,Detail'.split(','))
        with CaptureStdoutLog() as p:
            #                                     content     feature
            result = csv.compute_summary(final, {'mod': 10}, {'mod2': 20})
        expect = """-w- [mod] does not exist in weight_feature.
-w- [mod2] does not exist in weight_content.
-w- weight_content sum does not equal to 100: [10]
-w- weight_feature sum does not equal to 100: [20]
"""
        self.assertTextEqual(p.getvalue(), expect)
        self.assertEqual(result, [['SummaryTotal', None, None, 2, 3, 4, 5, 6, 7, 8, 9],
                                  ['WeightedPct', None, None, None, '5.0%', None, '7.5%', None, '20.0%', None, '20.0%']])

        with CaptureStdoutLog() as p:
            result = csv.compute_summary(final, {'mod': 50, 'mod2': 50}, {'mod': 50, 'mod2': 50})
        self.assertTextEqual(p.getvalue(), "")
        self.assertEqual(result, [['SummaryTotal', None, None, 2, 3, 4, 5, 6, 7, 8, 9],
                                  ['WeightedPct', None, None, None, '75.0%', None, '87.5%', None, '91.7%', None, '93.8%']])

        # None defined
        result = csv.compute_summary(final, {}, {})
        self.assertEqual(result, [['SummaryTotal', None, None, 2, 3, 4, 5, 6, 7, 8, 9],
                                  ['WeightedPct', None, None, None, '0.0%', None, '0.0%', None, '0.0%', None, '0.0%']])

    def test_derive_summary(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        final = ['ModSummary ARR1 ARR 1 2 3 4 5 6 7 8 A'.split(),
                 'ModSummary ARR2 ARR 1 1 1 1 1 1 1 1 A'.split(),
                 'ModSummary SCN1 SCN 2 2 2 2 2 2 2 2 A'.split(),
                 'MissingModule ARR1 ARR 1 1'.split(),
                 ]
        result = csv.derive_summary(final, buckets={'Ary': {'ARR1', 'ARR2'}})
        self.assertEqual(result, [['Summary', 'Ary', 'Ary', 2, 3, 4, 5, 6, 7, 8, 9],
                                  ['Summary', 'SCN1', 'SCN1', 2, 2, 2, 2, 2, 2, 2, 2]])

    def test_missing_module(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)

        final = ['Summary QQQ 1 2'.split()]     # QQQ is not a valid module in Simple1
        passfail = {('ARR', 'CCA'): 'F',
                    ('ARR', 'CCB'): 'B',
                    ('ARR', 'TPIE_PgmRules'): 'P',
                    ('SCN', 'CCA'): 'P',
                    ('SCN', 'CCB'): 'F',
                    }
        result = csv.missing_modules(final, passfail)

        self.assertEqual(result,
                         [['MissingModule', 'ARR', 'ARR', 0, None, 1],
                          ['MissingModule', 'SCN', 'SCN', 3, None, 1]])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, Waiver, 'wobj_list', [])
    def test_basic(self):
        tpf = f'{UT_DIR}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()

        # correct area and correct filename?
        csv = CsvPlan(tp)
        self.assertEqual(csv.get_fname(), f'{dirname(cfg.plan_waivers)}/outputs/477937_Simple1Real_CLASSHOT.csv')

        # check the output
        with TempDir(name=True) as tdir:
            csv = CsvPlan(tp, modwaiver=modwaiver(), outfile=join(tdir, 'a.csv'))

            # case1 - new file
            csv.add('ModSummary', 'SCN_ABC', *range(1, 10))
            csv.add('ModSummary', 'ARR_ABC', *[1 for _ in range(1, 10)])
            csv.add('ModSummary', 'BLAH', *[0 for _ in range(1, 10)])
            csv.add('MissingFromTP', 'SCN_ABC', '1', None, None, '2')
            csv.add('MissingFromTP', 'ARR_ABC', '2', None, None, '3')
            csv.add('MissingFromPlan', 'SCN_ABC', '3', None, '4', '5')
            csv.write(True)

            expect = """

HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR,ARR,1,1,1,1,1,1,1,1
Summary,SCN,SCN,1,2,3,4,5,6,7,8
SummaryTotal,,,2,3,4,5,6,7,8,9
WeightedPct,,,,5.0%,,7.5%,,4.2%,,4.4%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,ARR_ABC,ARR,1,1,1,1,1,1,1,1,1
ModSummary,SCN_ABC,SCN,1,2,3,4,5,6,7,8,9

HeadMissingTP,Module,Team,X,tid_expect,is_waive,Detail
MissingFromTP,ARR_ABC,ARR,2,,,3
MissingFromTP,SCN_ABC,SCN,1,,,2

HeadMissingPlan,Module,Team,tid_count,X,corner,Detail
MissingFromPlan,SCN_ABC,SCN,3,,4,5
"""
            self.assertTextEqual('\n' + File(csv.get_fname()).read(), expect)

            # case 2 - update
            csv = CsvPlan(tp, modwaiver=modwaiver(), outfile=join(tdir, 'a.csv'))
            csv.add('ModSummary', 'SCN_ABC', *range(2, 11))   # new value
            csv.add('MissingFromTP', 'SCN_ABC', '7', None, None, '8')
            csv.add('MissingFromTP', 'PTH_NEW', '2a', None, None, '3')
            csv.add('MissingFromPlan', 'SCN_ABC', '9', None, '10', '11')
            csv.add('FeatureMiss', 'SCN_ABC', '13', '14', '15', '16')   # New section
            csv.write(True)

            expect = """

HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR,ARR,1,1,1,1,1,1,1,1
Summary,SCN,SCN,2,3,4,5,6,7,8,9
SummaryTotal,,,3,4,5,6,7,8,9,10
WeightedPct,,,,6.7%,,8.0%,,4.3%,,4.4%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,ARR_ABC,ARR,1,1,1,1,1,1,1,1,1
ModSummary,SCN_ABC,SCN,2,3,4,5,6,7,8,9,10

HeadMissingTP,Module,Team,X,tid_expect,is_waive,Detail
MissingFromTP,ARR_ABC,ARR,2,,,3
MissingFromTP,PTH_NEW,PTH,2a,,,3
MissingFromTP,SCN_ABC,SCN,7,,,8

HeadFeatureMiss,Module,Team,X,X,TestName,Detail
FeatureMiss,SCN_ABC,SCN,13,14,15,16

HeadMissingPlan,Module,Team,tid_count,X,corner,Detail
MissingFromPlan,SCN_ABC,SCN,9,,10,11
"""
            self.assertTextEqual('\n' + File(csv.get_fname()).read(), expect)

            # Nothing to write
            self.assertEqual(csv.write(False), 2)
            csv.items = []
            self.assertEqual(csv.write(True), 1)


class TestIntegration(TestCase):

    def test_case1(self):
        # good template... just modify data, Plan() and expect for various TP scenarios
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()   # only patlist are used in this TP, everything else is data
        csv = CsvPlan(tp)

        # valid patlist: shops_L_list, shops_H_list, cpu_fuse_read_hvm_x, cpu_fuse_read_special_x
        data = [('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400', {'patlist': 'shops_L_list',
                                                                           'passfail': 'P'}),
                ('ARR', 'SSA_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX', {'patlist': 'shops_H_list',
                                                                     'passfail': 'F'}),
                ('ARR', 'BYP_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX', {'patlist': 'invalid_ignored',
                                                                     'passfail': 'B'}),
                ('SCN', 'SSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL', {'patlist': 'invalid_unused_module',
                                                                      'passfail': 'P'})]

        pr = PlanReport(tp, passfail={(k[0], k[1]): k[2]['passfail'] for k in data}, csv=csv)
        Plan('LSA', _utlno=1, content_expect=1, module='ARR')
        Plan('SSA', _utlno=1, content_expect=10, module='ARR')
        Plan('BYP', _utlno=1, content_expect=100, module='ARR')
        Plan('NFD', _utlno=1, content_expect=200, module='ARR')   # not found plan

        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=data)):
            pr.main()

        pprint(csv.items)
        expect = [['FoundPlan', 'ARR', 'ARR', 1, 1, 'En', '', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400'],
                  ['FoundPlan', 'ARR', 'ARR', 1, 10, 'En', '', 'SSA_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX'],
                  ['FoundPlan', 'ARR', 'ARR', 0, 100, 'En', '', 'BYP_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX'],
                  ['ModSummary', 'ARR', 'ARR', 0, 311, 2, 311, 0, 4, 1, 4, 'ARR'],
                  ['MissingFromTP', 'ARR', 'ARR', None, 200, '', "Plan('NFD', id_lno=1, module=ARR)"],
                  ['FeatureMiss', 'ARR', 'ARR', None, None, 'SSA_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX', "Plan('SSA', id_lno=1, module=ARR): is in failflow of testprogram"],
                  ['FeatureMiss', 'ARR', 'ARR', None, None, 'BYP_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX', "Plan('BYP', id_lno=1, module=ARR): is bypassed"]]
        self.maxDiff = None
        self.assertEqual(csv.items, expect)

    def test_case_namevar(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()   # only patlist are used in this TP, everything else is data
        csv = CsvPlan(tp)

        # valid patlist: shops_L_list, shops_H_list, cpu_fuse_read_hvm_x, cpu_fuse_read_special_x
        data = [('ARR', 'LSAB_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400', {'patlist': 'shops_L_list',
                                                                            'passfail': 'P',
                                                                            '_CORNER': 'min',
                                                                            '_FREQ': 'FF'}),
                ('ARR', 'SSA4000_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX', {'patlist': 'shops_H_list',
                                                                         'passfail': 'F',
                                                                         '_CORNER': 'min',
                                                                         '_FREQ': 'FF'}),
                ('ARR', 'BYP_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX', {'patlist': 'invalid_ignored',
                                                                     'passfail': 'B',
                                                                     '_CORNER': 'min',
                                                                     '_FREQ': 'FF'}),
                ('SCN', 'SSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL', {'patlist': 'invalid_unused_module',
                                                                      'passfail': 'P',
                                                                      '_CORNER': 'min',
                                                                      '_FREQ': 'FF'})]

        pr = PlanReport(tp, passfail={(k[0], k[1]): k[2]['passfail'] for k in data}, csv=csv)
        Plan('LSA{olb_bin_type}', _utlno=1, content_expect=1, module='ARR')
        Plan('SSA{GT_FREQ}', _utlno=1, content_expect=10, module='ARR')

        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=data)),\
                MockVar(PlanReport, "get_inputdict", Mock(return_value={'olb_bin_type': 'B', 'GT_FREQ': '4GHz'})):
            pr.main()

        Dumper(csv.items)
        expect = [['FoundPlan', 'ARR', 'ARR', 1, 1, 'En', '', 'LSAB_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400'],
                  ['FoundPlan', 'ARR', 'ARR', 1, 10, 'En', '', 'SSA4000_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX'],
                  ['ModSummary', 'ARR', 'ARR', 0, 11, 2, 11, 0, 2, 1, 2, 'ARR'],
                  ['FeatureMiss', 'ARR', 'ARR', None, None, 'SSA4000_GT_VMAX_K_STRESS_X_VCCGT_F1_0400_XXX', "Plan('SSA4000', id_lno=1, module=ARR): is in failflow of testprogram"]]
        self.maxDiff = None
        self.assertEqual(csv.items, expect)

        # error case
        Plan('LSA{notfound}', _utlno=1, content_expect=1, module='ARR')
        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=data)):
            with self.assertRaisesRegex(ErrorInput, 'Variable not defined'):
                pr.main()


class TestReport(TestCase):

    def test_debug(self):
        # with namefield, match failure.
        # See also TestTPAuditPlan.test_debugplan for MATCH case
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pr = PlanReport(tp)
        Plan(name='D*C', freq='0563', content_expect=10, module='SCN', _utlno=1)
        Plan(name='D*C', freq='0564', content_expect=10, module='SCN', _utlno=2)
        data = {'ifpm_modifygroups': 'somevalue',
                'namefield': {'corner': 'F3',
                              'freq': '0562'}}
        tn_data = {('SCN', 'DEFUNC_X_VMIN_K_CHKSACDF3_X_DE_F3_0562_*'): (2, data)}
        with CaptureStdoutLog() as p, MockVar(pr, 'read_tp', Mock(return_value=tn_data)):
            pr.do_debug({'1': 'DEFUNC_X_VMIN_K_CHKSACDF3_X_DE_F3_0562'})
        expect = f"""Start debug ======
Debug for: Plan('D*C', id_lno=1, module=SCN, freq=0563)
Namefield for DEFUNC_X_VMIN_K_CHKSACDF3_X_DE_F3_0562_*:
   corner     = 'F3'
   freq       = '0562'
Data for DEFUNC_X_VMIN_K_CHKSACDF3_X_DE_F3_0562_*:
   ifpm_modifygroups = 'somevalue'
Match Result: Plan('D*C', id_lno=1, module=SCN): freq mismatch [0563] vs tp:[0562]"""
        self.assertTextEqual('\n'.join(trimut(p.getvalue())), expect)

    def test_analyze_tid_expect(self):
        qbox.root = f'{UT_DIR_REPO}/qbox'    # unittest only
        SetProdStep('ut05', 'a0')

        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pr = PlanReport(tp)

        q1 = QueryTid(attributes='west')
        t1 = Plan(name='C*A', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1)
        t2 = Plan(name='C*A', voltage_corner='nom', content_expect=100, module='SCN', _utlno=1,
                  tid_expect=q1)
        _ = Plan(name='C*A', voltage_corner='nom', content_expect=3, module='SCN', _utlno=1,
                 tid_expect=q1)   # This should not be printed
        qbox.process()

        self.assertEqual(t2.analyze_tid_expect({'0153425', '0317275', '0153426'}, 'q'), 'q')
        self.assertEqual(t2.analyze_tid_expect({'0153424', '0317275', '0153426'}, 'q'),
                         "Plan('C*A', id_lno=1, module=SCN): tid_expect extra_count=1, Extra tid: 0153424")
        self.assertEqual(t1.analyze_tid_expect({'0153424', '0317275', '0153426'}, 'q'), 'q')

        self.assertEqual(t2.feature_match('', {'_CORNER': 'nom'}, {str(x) for x in range(20)}),
                         "Plan('C*A', id_lno=1, module=SCN): tid_expect extra_count=20, Extra tid: 0,1,10,11,12,13,14,15,16,17")

        # summary_tid_expect
        with CaptureStdoutLog() as p:
            print()
            pr.summary_tid_expect()
        expect = """
Large variation of tid_expect vs content_expect:
   1. Plan(id_lno=1, content_expect=100): tid_expect count=3

"""
        self.assertTextEqual(p.getvalue(), expect)
        qbox.__init__()    # clear stuff for unittests

    def test_contentzero(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pr = PlanReport(tp)
        Plan(name='C*A', voltage_corner='nom', module='SCN', _utlno=1)
        Plan(name='C*B', voltage_corner='nom', content_expect=0, module='SCN', _utlno=1)
        Plan(name='TPIE_PgmRules', module='ARR', _utlno=1)
        with CaptureStdoutLog() as p:
            pr.main()

        expect = f"""TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for ARR:
   Content rollup POR:     0/0
   Content rollup Enabled: 0/0
   Feature rollup POR:     0/1
   Feature rollup Enabled: 1/1
   Feature found  Total:   1/1
Missing from testprogram:
   None
Missing from testplan:
   1. ARR CCA: voltage_corner=nom freq=NONE tid=1
   2. ARR CCB: voltage_corner=nom freq=NONE tid=1
Feature misses:
   None
Result for SCN:
   Content rollup POR:     0/0
   Content rollup Enabled: 0/0
   Feature rollup POR:     0/2
   Feature rollup Enabled: 1/2
   Feature found  Total:   2/2
Missing from testprogram:
   None
Missing from testplan:
   None
Feature misses:
   1. Plan('C*B', id_lno=1, module=SCN): found tid 3 > content_expect 0"""

        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

    def test_invalidTP(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pr = PlanReport(tp)
        TPName('oopsie')
        Plan(name='C*A', voltage_corner='nom', module='SCN', _utlno=1)
        Plan(name='C*B', voltage_corner='nom', content_expect=0, module='SCN', _utlno=1)
        Plan(name='TPIE_PgmRules', module='ARR', _utlno=1)
        with CaptureStdoutLog() as p:
            pr.main()

        expect = ''
        self.assertTextEqual('\n'.join(trimut(p.getvalue())), expect)

    def test_ignore_nonpat(self):
        # content_expect=1 means 'patlist' must exist in instance. In below case, TPIE_PgmRules does not have 'patlist'
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pr = PlanReport(tp)
        Plan(name='TPIE_PgmRules', content_expect=1, module='ARR', _utlno=1)
        with CaptureStdoutLog() as p:
            pr.main()

        expect = f"""TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for ARR:
   Content rollup POR:     0/1
   Content rollup Enabled: 0/1
   Feature rollup POR:     0/1
   Feature rollup Enabled: 0/1
   Feature found  Total:   0/1
Missing from testprogram:
   1. Plan('TPIE_PgmRules', id_lno=1, module=ARR)
Missing from testplan:
   1. ARR CCA: voltage_corner=nom freq=NONE tid=1
   2. ARR CCB: voltage_corner=nom freq=NONE tid=1
Feature misses:
   None"""
        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

    def test_location(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()

        # case1 - SetLocation
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        SetLocation('COLD')
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, loc='CLASSHOT')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'],
                         [['FoundPlan', 'SCN', 'SCN', 3, 20, 'En', '', 'CCB']])   # expect one item found only

        # case2 - default (Also tests if SetLocation is cleared)
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, loc='COLD')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'],
                         [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCA']])   # expect one item found only

        # case3 - regex
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        SetLocation('COLD')
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, loc='C.*T')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'],
                         [['FoundPlan', 'SCN', 'SCN', 3, 20, 'En', '', 'CCB']])   # expect one item found only

        # case4 - negative location and regex
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, loc='!CLASSHOT')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'],
                         [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCA']])   # expect one item found only

        # case5 - capital LOC
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        obj = Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, LOC='!CLASSHOT',
                   owner='blah', comment='blah', cfgx='q')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'],
                         [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCA']])   # expect one item found only
        self.assertEqual(obj.kwargs, {'cfgx': 'q'})

    def test_tpname(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()    # get_name(): Simple1Real

        # case1 - TPName, including regex
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        TPName('NotMatch')
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, tp='.imple1Real')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'], [])

        # case2a - TPName, including regex
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        TPName('.imple1Real')
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, tp='.imple1Real')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'],
                         [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCA'],
                          ['FoundPlan', 'SCN', 'SCN', 3, 20, 'En', '', 'CCB']])

        # case2 - default (Also tests if TPName is cleared)
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        Plan(name='C*A', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', content_expect=20, module='SCN', _utlno=2, tp='FakeProg')
        pr.main()
        self.assertEqual([x for x in csv.items if x[0] == 'FoundPlan'],
                         [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCA']])   # expect one item found only

    def test_basic(self):
        # Tests one module only
        # Tests single match in TP only
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*A', voltage_corner='nom', content_expect=5, module='SCN', _utlno=2)
        with CaptureStdoutLog() as p:
            pr.main()

        expect = f"""TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for SCN:
   Content rollup POR:     0/15
   Content rollup Enabled: 6/15
   Feature rollup POR:     0/2
   Feature rollup Enabled: 2/2
   Feature found  Total:   2/2
Missing from testprogram:
   None
Missing from testplan:
   1. SCN CCB: voltage_corner=nom freq=NONE tid=3
Feature misses:
   None"""

        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)
        self.assertEqual(csv.items, [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCA'],
                                     ['FoundPlan', 'SCN', 'SCN', 3, 5, 'En', '', 'CCA'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 15, 6, 15, 0, 2, 2, 2, 'SCN'],
                                     ['MissingFromPlan', 'SCN', 'SCN', 3, None, 'nom', 'CCB']])
        self.assertEqual(csv.missing_modules(csv.items, tp.mtpl.dict_flows()),
                         [['MissingModule', 'ARR', 'ARR', 2, None, 3]])

        # failflow - should find CCA correctly, and should identify bypassed
        passfail = {('ARR', 'CCA'): 'P',     # pass flow
                    ('ARR', 'CCB'): 'F',    # fail flow
                    ('ARR', 'TPIE_PgmRules'): 'B'}
        pr = PlanReport(tp, passfail=passfail)
        Plan(name='CC*', module='ARR', failflow=True)      # NOTE: This will not be flagged for now. It is found in passflow.
        Plan(name='CCB', module='ARR')
        Plan(name='TPIE', module='ARR')
        with CaptureStdoutLog() as p:
            pr.main()   # This should not raise Exception
        print("failflow case ================")
        print(p.getvalue())
        self.assertIn('is in failflow of testprogram', p.getvalue())
        self.assertIn('is bypassed', p.getvalue())

    def test_check(self):
        tpf = f'{UT_DIR_REPO}/Simple2/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)

        Plan(name='NOTFOUND', ip='VPU', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1)
        with MockVar(OPT, 'check', True):
            pr.main()
        pprint(csv.items)
        self.assertEqual(csv.items, [['FoundPlan', 'SCN (VPU)', 'SCN (VPU)', 3, 10, 'En', '', 'CCB'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 10, 3, 10, 0, 1, 1, 1, 'VPU'],
                                     ['MissingFromPlan', 'SCN', 'SCN', 2, None, 'nom', 'CCA'],
                                     ['MissingFromPlan', 'SCN', 'SCN', 3, None, 'nom', 'CCB']])

    def test_ip(self):
        tpf = f'{UT_DIR_REPO}/Simple2/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', ip='VPU', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1)
        Trust('activity1', chot=DONE, ip='MCU', module='SCN', _utlno=1)
        with CaptureStdoutLog() as p:
            pr.main()

        self.assertTrue('Nothing to display for SCN' in p.getvalue(), 'Refer to stdout')
        pprint(csv.items)
        self.assertEqual(csv.items, [['FoundPlan', 'SCN (VPU)', 'SCN (VPU)', 2, 10, 'En', '', 'CCA'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 10, 2, 10, 0, 1, 1, 1, 'VPU'],
                                     ['MissingFromPlan', 'SCN', 'SCN', 3, None, 'nom', 'CCB']])

    def test_var_not_found(self):
        tpf = f'{UT_DIR_REPO}/Simple2/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', ip='VPU', testpreinstance='{F1_notfound}', content_expect=10, module='SCN', _utlno=1)
        with MockVar(OPT, "write", True):
            pr.main()
        Dumper(csv.items)
        self.assertEqual(csv.items, [['FoundPlan', 'SCN (VPU)', 'SCN (VPU)', 2, 10, 'En', '', 'CCA'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 10, 2, 10, 0, 1, 0, 1, 'VPU'],
                                     ['MissingFromPlan', 'SCN', 'SCN', 3, None, 'nom', 'CCB'],
                                     ['FeatureMiss', 'SCN', 'SCN', None, None, 'CCA', "Plan('C*A', id_lno=1, module=SCN): testpreinstance mismatch [VARIABLE_NOT_DEFINED 'F1_notfound' in '{F1_notfound}'] vs tp:[<NOT_IN_INSTANCE>]"]])

        # There is a real exception
        def fake(*args):
            raise Exception('some error')

        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)
        Plan(name='C*A', ip='VPU', testpreinstance='someerror', content_expect=10, module='SCN', _utlno=1)
        with MockVar(Plan, 'eval_vars', Mock(side_effect=fake)):
            with MockVar(OPT, "write", True):
                pr.main()    # no exception
            Dumper(csv.items)
            self.assertEqual(csv.items, [['FoundPlan', 'SCN (VPU)', 'SCN (VPU)', 2, 10, 'En', '', 'CCA'],
                                         ['ModSummary', 'SCN', 'SCN', 0, 10, 2, 10, 0, 1, 0, 1, 'VPU'],
                                         ['MissingFromPlan', 'SCN', 'SCN', 3, None, 'nom', 'CCB'],
                                         ['FeatureMiss', 'SCN', 'SCN', None, None, 'CCA', "Plan('C*A', id_lno=1, module=SCN): EXCEPTION: some error"]])

            # No -write
            with MockVar(OPT, "write", False):
                with self.assertRaisesRegex(Exception, 'some error'):
                    pr.main()

    def test_subplist1(self):
        # subplist in two different IP, basic
        tpf = f'{UT_DIR_REPO}/Simple2/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', ip='VPU', subplist='csi_hs_vil_csireset', content_expect=1, module='SCN', _utlno=1)
        Plan(name='C*A', ip='IPU', subplist='csi_hs_vih_csireset', content_expect=1, module='SCN', _utlno=2)
        with CaptureStdoutLog() as p:
            pr.main()
        expect = f"""TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for SCN, IP=IPU:
   Content rollup POR:     0/1
   Content rollup Enabled: 1/1
   Feature rollup POR:     0/1
   Feature rollup Enabled: 1/1
   Feature found  Total:   1/1
Missing from testprogram:
   None
Missing from testplan:
   None
Feature misses:
   None
Result for SCN, IP=VPU:
   Content rollup POR:     0/1
   Content rollup Enabled: 1/1
   Feature rollup POR:     0/1
   Feature rollup Enabled: 1/1
   Feature found  Total:   1/1
Missing from testprogram:
   None
Missing from testplan:
   1. SCN CCB: voltage_corner=nom freq=NONE tid=3
Feature misses:
   None"""
        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

        pprint(csv.items)
        self.assertEqual(csv.items, [['FoundPlan', 'SCN (IPU)', 'SCN (IPU)', 1, 1, 'En', '', 'CCA'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 1, 1, 1, 0, 1, 1, 1, 'IPU'],
                                     ['FoundPlan', 'SCN (VPU)', 'SCN (VPU)', 1, 1, 'En', '', 'CCA'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 1, 1, 1, 0, 1, 1, 1, 'VPU'],
                                     ['MissingFromPlan', 'SCN', 'SCN', 3, None, 'nom', 'CCB']])

    def test_subplist2(self):
        # subplist in two different IP
        Waiver.wobj_list.clear()
        tpf = f'{UT_DIR_REPO}/Simple2/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        passfail = {('ARR', 'CCA'): 'P',
                    ('ARR', 'CCB'): 'P',
                    ('ARR', 'TPIE_PgmRules'): 'P',
                    ('SCN', 'CCA'): 'P',
                    ('SCN', 'CCB'): 'B'}
        pr = PlanReport(tp, passfail=passfail, csv=csv)

        # subplist is not found
        Plan(name='C*B', ip='VPU', subplist='csi_hs_vil_csiresetx', content_expect=1, module='ARR', _utlno=1)
        # No patlist in testinstance
        Plan(name='C*A', ip='IPU', subplist='csi_hs_vih_csireset', content_expect=1, module='ARR', _utlno=2)
        # multiple match case
        Plan(name='C*A', ip='IPU', subplist='csi', content_expect=1, module='SCN', _utlno=3)
        # bypassed
        Plan(name='C*B', ip='IPU', subplist='csi', content_expect=1, module='SCN', _utlno=4)

        # Make sure VPU does not show up in SCN
        with CaptureStdoutLog() as p:
            pr.main()
        expect = """Result for ARR, IP=IPU:
Result for ARR, IP=VPU:
Result for SCN, IP=IPU:"""
        result = [x for x in trimut(p.getvalue()) if x.startswith('Result for')]
        self.assertTextEqual('\n'.join(result), expect)

        Dumper(csv.items)
        self.assertEqual(csv.items, [['ModSummary', 'ARR', 'ARR', 0, 1, 0, 1, 0, 1, 0, 1, 'IPU'],
                                     # Below is missing because CCA does not have patlist in testinstance
                                     ['MissingFromTP', 'ARR', 'ARR', None, 1, '', "Plan('C*A', id_lno=2, module=ARR, ip=IPU, subplist=csi_hs_vih_csireset)"],
                                     ['FoundPlan', 'ARR (VPU)', 'ARR (VPU)', 0, 1, 'En', '', 'CCB'],
                                     ['ModSummary', 'ARR', 'ARR', 0, 1, 0, 1, 0, 1, 1, 1, 'VPU'],
                                     ['FoundPlan', 'SCN (IPU)', 'SCN (IPU)', 0, 1, 'En', '', 'CCA'],
                                     ['FoundPlan', 'SCN (IPU)', 'SCN (IPU)', 0, 1, 'En', '', 'CCB'],
                                     ['ModSummary', 'SCN', 'SCN', 0, 2, 0, 2, 0, 2, 1, 2, 'IPU'],
                                     ['FeatureMiss', 'SCN', 'SCN', None, None, 'CCB', "Plan('C*B', id_lno=4, module=SCN): is bypassed"]])

    def test_por_true(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csv = CsvPlan(tp)
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1, por=True)
        Plan(name='C*B', voltage_corner='nom', content_expect=5, module='SCN', _utlno=2)
        with CaptureStdoutLog() as p:
            pr.main()

        expect = f"""TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for SCN:
   Content rollup POR:     3/15
   Content rollup Enabled: 6/15
   Feature rollup POR:     1/2
   Feature rollup Enabled: 2/2
   Feature found  Total:   2/2
Missing from testprogram:
   None
Missing from testplan:
   None
Feature misses:
   None"""

        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

    @with_(TempDir, chdir=True)
    def test_blocked(self):
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)
        Plan(name='CCA', module='ARR', content_expect=2, blocked=True, _utlno=1)
        Plan(name='CCB', module='ARR', content_expect=2, blocked=False, _utlno=1)
        with CaptureStdoutLog() as p:
            pr.main()
        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
-i- found EDC=1 of 2, Plan('CCA', id_lno=1, module=ARR, blocked=True) CCA
-i- found EDC=1 of 2, Plan('CCB', id_lno=1, module=ARR) CCB

Result for ARR:
   Content rollup POR:     0/4
   Content rollup Enabled: 2/4
   Feature rollup POR:     0/2
   Feature rollup Enabled: 2/2
   Feature found  Total:   2/2

Missing from testprogram:
   None

Missing from testplan:
   None

Feature misses:
   None

'''
        self.assertTextEqual(Env.xpath(p.getvalue()), expect)

        # check the csv
        csv.write(True, passfail=pr.passfail)
        expect = """
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR,ARR,0,4,2,4,0,2,2,2
SummaryTotal,,,0,4,2,4,0,2,2,2
WeightedPct,,,,0.0%,,0.0%,,0.0%,,0.0%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,ARR,ARR,0,4,2,4,0,2,2,2,ARR

HeadFound,Module,Team,tid_count,tid_expect,PorEn,POR_plan,TestName
FoundPlan,ARR,ARR,1,2,BLK,,CCA
FoundPlan,ARR,ARR,1,2,En,,CCB

HeadMissMod,Module,Team,tid_count,X,TestInsCount
"""
        result = File(csvfile).read()
        result = '\n'.join(x for x in result.split('\n') if not x.startswith(('TimeStamp', 'MissingModule')))
        self.assertTextEqual(result, expect)

    @with_(TempDir, chdir=True)
    def test_multiplematch1(self):
        # multiple match in TP - fail case
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)
        Plan(name='CC*', module='ARR', content_expect=2, _utlno=1)
        with CaptureStdoutLog() as p:
            pr.main()
        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR) CCB

Result for ARR:
   Content rollup POR:     0/2
   Content rollup Enabled: 1/2
   Feature rollup POR:     0/1
   Feature rollup Enabled: 0/1
   Feature found  Total:   1/1

Missing from testprogram:
   None

Missing from testplan:
   None

Feature misses:
   1. Plan('CC*', id_lno=1, module=ARR): multiple_match mismatch: 2 (Found) vs 1 (Plan): CCA,CCB

'''
        self.assertTextEqual(Env.xpath(p.getvalue()), expect)

        # check the csv
        csv.write(True, passfail=pr.passfail)
        expect = """
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR,ARR,0,2,1,2,0,1,0,1
SummaryTotal,,,0,2,1,2,0,1,0,1
WeightedPct,,,,0.0%,,0.0%,,0.0%,,0.0%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,ARR,ARR,0,2,1,2,0,1,0,1,ARR

HeadFeatureMiss,Module,Team,X,X,TestName,Detail
FeatureMiss,ARR,ARR,,,CCB,"Plan('CC*', id_lno=1, module=ARR): multiple_match mismatch: 2 (Found) vs 1 (Plan): CCA,CCB"

HeadFound,Module,Team,tid_count,tid_expect,PorEn,POR_plan,TestName
FoundPlan,ARR,ARR,1,2,En,,CCB

HeadMissMod,Module,Team,tid_count,X,TestInsCount
"""
        result = File(csvfile).read()
        result = '\n'.join(x for x in result.split('\n') if not x.startswith(('TimeStamp', 'MissingModule')))
        self.assertTextEqual(result, expect)

    @with_(TempDir, chdir=True)
    def test_multiplematch2(self):
        # multiple match in TP - pass case
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)
        Plan(name='CC*', module='ARR', content_expect=2, _utlno=1, multiple_match=2,
             patlist='shops*')
        with CaptureStdoutLog() as p:
            pr.main()
        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=2, patlist=shops*) CCB
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=2, patlist=shops*) CCA
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=2, patlist=shops*) CCB

Result for ARR:
   Content rollup POR:     0/2
   Content rollup Enabled: 1/2
   Feature rollup POR:     0/1
   Feature rollup Enabled: 1/1
   Feature found  Total:   1/1

Missing from testprogram:
   None

Missing from testplan:
   None

Feature misses:
   None

'''
        self.assertTextEqual(Env.xpath(p.getvalue()), expect)

    @with_(TempDir, chdir=True)
    def test_multiplematch2a(self):
        # multiple match in TP - pass case = -1
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)
        Plan(name='CC*', module='ARR', content_expect=2, _utlno=1, multiple_match=-1,
             patlist='shops*')
        with CaptureStdoutLog() as p:
            pr.main()
        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=-1, patlist=shops*) CCB
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=-1, patlist=shops*) CCA
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=-1, patlist=shops*) CCB

Result for ARR:
   Content rollup POR:     0/2
   Content rollup Enabled: 1/2
   Feature rollup POR:     0/1
   Feature rollup Enabled: 1/1
   Feature found  Total:   1/1

Missing from testprogram:
   None

Missing from testplan:
   None

Feature misses:
   None

'''
        self.assertTextEqual(Env.xpath(p.getvalue()), expect)

    @with_(TempDir, chdir=True)
    def test_multiplematch3(self):
        # multiple match in TP - mismatch param - CCB instance
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)
        Plan(name='CC*', module='ARR', content_expect=2, _utlno=1, multiple_match=2,
             patlist='shops_L_list')
        with CaptureStdoutLog() as p:
            pr.main()
        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=2, patlist=shops_L_list) CCB

Result for ARR:
   Content rollup POR:     0/2
   Content rollup Enabled: 1/2
   Feature rollup POR:     0/1
   Feature rollup Enabled: 0/1
   Feature found  Total:   1/1

Missing from testprogram:
   None

Missing from testplan:
   None

Feature misses:
   1. Plan('CC*', id_lno=1, module=ARR): patlist mismatch [shops_L_list] vs tp:[shops_H_list] [CCB]

'''
        self.assertTextEqual(Env.xpath(p.getvalue()), expect)

    @with_(TempDir, chdir=True)
    def test_multiplematch4(self):
        # multiple match in TP - mismatch param - CCA instance
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)
        Plan(name='CC*', module='ARR', content_expect=2, _utlno=1, multiple_match=2,
             patlist='shops_H_list')
        with CaptureStdoutLog() as p:
            pr.main()
        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=2, patlist=shops_H_list) CCB
-i- found EDC=1 of 2, Plan('CC*', id_lno=1, module=ARR, multiple_match=2, patlist=shops_H_list) CCA

Result for ARR:
   Content rollup POR:     0/2
   Content rollup Enabled: 1/2
   Feature rollup POR:     0/1
   Feature rollup Enabled: 0/1
   Feature found  Total:   1/1

Missing from testprogram:
   None

Missing from testplan:
   None

Feature misses:
   1. Plan('CC*', id_lno=1, module=ARR): patlist mismatch [shops_H_list] vs tp:[shops_L_list] [CCA]

'''
        self.assertTextEqual(Env.xpath(p.getvalue()), expect)

    def test_readtp(self):
        # Checks chunks and namefield
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pf = {('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1401'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_XXX'): 'P',
              ('SCN', 'SSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL'): 'P'}

        pr = PlanReport(tp, passfail=pf)
        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='ARR', _utlno=1)
        data = [('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1401', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_XXX', {'patlist': 'shops_H_list'}),
                ('SCN', 'SSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL', {'patlist': 'shops_L_list'})]
        with MockVar(pr.tpobj.mtpl, 'iter_flows', Mock(return_value=data)):
            tn_data = pr.read_tp()

        # make sure keys are correct - remove speed flow
        self.assertEqual(tn_data.keys(), {('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400'),
                                          ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1401'),
                                          ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_XXX')})

        # make sure chunk is in place
        key = ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400')
        self.assertEqual(tn_data[key][0],
                         {'1466650_00'})

        # make sure namefield is there
        self.assertEqual(tn_data[key][1]['namefield']['subflow'], 'PREHVQK')

    def test_readtp_chunk(self):
        # Checks chunks and namefield
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pf = {('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1401'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_XXX'): 'P',
              ('SCN', 'SSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL'): 'P'}

        pr = PlanReport(tp, passfail=pf)
        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='ARR', _utlno=1, chunk=9)
        data = [('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1401', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_XXX', {'patlist': 'shops_H_list'}),
                ('SCN', 'SSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL', {'patlist': 'shops_L_list'})]
        with MockVar(pr.tpobj.mtpl, 'iter_flows', Mock(return_value=data)):
            tn_data = pr.read_tp()

        # make sure chunk is in place
        key = ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400')
        self.assertEqual(tn_data[key][0],
                         {'1466650_14'})
        TPName.chunk[0] = None    # put it back

    def test_readtp_maxfreq_keep(self):
        # Checks chunks and namefield
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        pf = {('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0500_ALL_1401'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0600_ALL_1402'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0700_ALL_1403'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0700_ALL_1400'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0600_ALL_1401'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0500_ALL_1402'): 'P',
              ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0300_ALL_1403'): 'P'}

        pr = PlanReport(tp, passfail=pf)
        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='ARR', _utlno=1)
        data = [('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0400_ALL_1400', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0500_ALL_1401', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0600_ALL_1402', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F1_0700_ALL_1403', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0700_ALL_1400', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0600_ALL_1401', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0500_ALL_1402', {'patlist': 'shops_L_list'}),
                ('ARR', 'LSA_GT_VMIN_K_PREHVQK_X_VCCGT_F2_0300_ALL_1403', {'patlist': 'shops_L_list'})]
        with MockVar(pr.tpobj.mtpl, 'iter_flows', Mock(return_value=data)):
            tn_data = pr.read_tp()
        pprint(tn_data.keys())
        self.assertEqual(tn_data.keys(), pf.keys())
        self.assertEqual(len(tn_data.keys()), 8)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="regression test, not needed for coverage"))
    @with_(MockVar, OPT, 'flows', 'MAIN')
    def test_regres(self):
        TP.set_tp(None)
        # Don't use this test for coverage (too slow)
        # This test should cover real tp stuff. Update plan file as needed
        tp = f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env'
        pf = f'{UT_DIR}/plans/fun_de_14P_r2.py'
        cmd = f'tp_plans.py -tp {tp} {pf} -write'.split()
        with MockVar(sys, "argv", cmd):
            TPPlans().main()

        csv = f'{UT_DIR}/../plan_waivers/outputs/477937_TGLUTH6B0H14P00S109_CLASSHOT.csv'
        self.assertLess(int(File(csv).age()), 10)    # file should be recent

        result = File(csv).read()
        # remove line numbers
        result = re.sub(r"id_lno=\d+", 'id_lno=1', result)
        # remove timestamps
        result = '\n'.join(x for x in result.split('\n') if not x.startswith(('TimeStamp', 'MissingModule')))
        expect = """
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,FUN,FUN,1824,3013,1824,3013,1,7,1,7
SummaryTotal,,,1824,3013,1824,3013,1,7,1,7
WeightedPct,,,,60.5%,,60.5%,,14.3%,,14.3%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,FUN_DE,FUN,1824,3013,1824,3013,1,7,1,7,FUN_DE

HeadModW,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModWaived,FUN_DE,FUN,1824,2513,1824,2513,1,6,1,6,FUN_DE

HeadMissingTP,Module,Team,X,tid_expect,is_waive,Detail
MissingFromTP,FUN_DE,FUN,,500,,"Plan('CHKX', id_lno=1, module=FUN_DE)"
MissingFromTP,FUN_DE,FUN,,500, (WAIVED),"Plan('CHK*F3', id_lno=1, module=FUN_DE)"

HeadFeatureMiss,Module,Team,X,X,TestName,Detail
FeatureMiss,FUN_DE,FUN,,,DEFUNC_X_VMIN_K_CHKSACDF4_X_DE_F4_CD662_1504,"Plan('CHK*F4', id_lno=1, module=FUN_DE): found tid 731 > content_expect 600 [DEFUNC_X_VMIN_K_CHKSACDF4_X_DE_F4_CD662_1504]"
FeatureMiss,FUN_DE,FUN,,,DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1504,"Plan('VMIN*CHK*F1', id_lno=1, module=FUN_DE): voltage mismatch [0.8V,1.9] vs tp:[1.2] [DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1504]"
FeatureMiss,FUN_DE,FUN,,,DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1504,"Plan('CHK*F1', id_lno=1, module=FUN_DE): multiple_match mismatch: 4 (Found) vs 1 (Plan): DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1501,DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1502,DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1503,DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1504"
FeatureMiss,FUN_DE,FUN,,,DEFUNC_DE_FUNC_E_BEGIN_X_X_CD312_CTRL_BABY,"Plan('DEFUNC_DE_FUNC_E_BEGIN_X_X_CD312_CTRL_BABY', id_lno=1, module=FUN_DE): is bypassed"

HeadMissingPlan,Module,Team,tid_count,X,corner,Detail
MissingFromPlan,FUN_DE,FUN,731,,max,DEFUNC_DE_FUNC_E_BEGIN_X_X_CD662_VMAX
MissingFromPlan,FUN_DE,FUN,120,,UNK,DEFUNC_DE_FUNC_E_BEGIN_X_X_STF_200
MissingFromPlan,FUN_DE,FUN,728,,vmin,DEFUNC_X_VMIN_K_CHKSACDF2_X_DE_F2_CD562_1501
MissingFromPlan,FUN_DE,FUN,728,,vmin,DEFUNC_X_VMIN_K_CHKSACDF2_X_DE_F2_CD562_1502
MissingFromPlan,FUN_DE,FUN,728,,vmin,DEFUNC_X_VMIN_K_CHKSACDF2_X_DE_F2_CD562_1503
MissingFromPlan,FUN_DE,FUN,728,,vmin,DEFUNC_X_VMIN_K_CHKSACDF2_X_DE_F2_CD562_1504
MissingFromPlan,FUN_DE,FUN,8,,vmin,DEFUNC_X_VMIN_K_SRHSACDF1_X_DE_F1_CD312_1501
MissingFromPlan,FUN_DE,FUN,8,,vmin,DEFUNC_X_VMIN_K_SRHSACDF1_X_DE_F1_CD312_1502
MissingFromPlan,FUN_DE,FUN,8,,vmin,DEFUNC_X_VMIN_K_SRHSACDF1_X_DE_F1_CD312_1503
MissingFromPlan,FUN_DE,FUN,8,,vmin,DEFUNC_X_VMIN_K_SRHSACDF1_X_DE_F1_CD312_1504

HeadFound,Module,Team,tid_count,tid_expect,PorEn,POR_plan,TestName
FoundPlan,FUN_DE,FUN,731,600,POR,,DEFUNC_X_VMIN_K_CHKSACDF4_X_DE_F4_CD662_1504
FoundPlan,FUN_DE,FUN,612,700,POR,,DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1504
FoundPlan,FUN_DE,FUN,0,,POR,,DEFUNC_X_SCREEN_K_SRHSACDF1_F1_X_X_X_FORK_DE0
FoundPlan,FUN_DE,FUN,612,613,POR,,DEFUNC_X_VMIN_K_CHKSACDF1_X_DE_F1_CD312_1504
FoundPlan,FUN_DE,FUN,0,100,POR,,DEFUNC_DE_FUNC_E_BEGIN_X_X_CD312_CTRL_BABY

HeadMissMod,Module,Team,tid_count,X,TestInsCount

HeadTimeStamp,Module,Team,Date_Run,Date_PlanFile,SHA_PlanFile,PlanFile
"""
        self.assertTextEqual(result, expect)


class TestTrust(TestCase):

    @with_(TempDir, chdir=True)
    def test_outputs(self):
        # tests display and final csv
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)

        Plan(name='C*A', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1)
        Plan(name='C*B', voltage_corner='nom', content_expect=10, module='SCN', _utlno=1)
        Trust("activity#1", chot=KILL, module='SCN')    # completed
        Trust("activity#2", chot=202130, module='SCN')      # not complete
        with CaptureStdoutLog() as p:
            pr.main()

        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for SCN:
   Content rollup POR:     0/20
   Content rollup Enabled: 6/20
   Feature rollup POR:     1/4
   Feature rollup Enabled: 3/4
   Feature found  Total:   2/2
Trust Result for CLASSHOT:
   Enabled Only: 0/2
   EDC Only:     0/2
   POR:          1/2
   WIP:          0/2
   BLOCKED:      0/2
Missing from testprogram:
   None
Missing from testplan:
   None
Feature misses:
   None'''
        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

        # check the final csv
        csv.write(True, passfail=pr.passfail)
        expect = """
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,SCN,SCN,0,20,6,20,1,4,3,4
SummaryTotal,,,0,20,6,20,1,4,3,4
WeightedPct,,,,0.0%,,3.0%,,1.2%,,3.8%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,SCN,SCN,0,20,6,20,0,2,2,2,SCN

HeadTrustSum,Module,Team,Total,Enabled,EDC,POR,WIP,Blocked,IP
TrustSummary,SCN,SCN,2,0,0,1,0,0,SCN

HeadFound,Module,Team,tid_count,tid_expect,PorEn,POR_plan,TestName
FoundPlan,SCN,SCN,3,10,En,,CCA
FoundPlan,SCN,SCN,3,10,En,,CCB

HeadMissMod,Module,Team,tid_count,X,TestInsCount

HeadTrustItem,Module,Team,Location,ETA,POR,Item,Enabled,EDC,Kill,WIP,Blocked
TrustItem,SCN,SCN,CLASSHOT,,1,activity#1,0,0,1,0,0
TrustItem,SCN,SCN,CLASSHOT,202130,0,activity#2,0,0,0,0,0
"""
        result = File(csvfile).read()
        result = '\n'.join(x for x in result.split('\n') if not x.startswith(('TimeStamp', 'MissingModule')))
        self.assertTextEqual(result, expect)

    @with_(TempDir, chdir=True)
    def test_basic(self):
        # tests display and csv
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)

        ModuleName('SCN')
        Plan(name='C*A', voltage_corner='nom', content_expect=10, _utlno=1)
        Plan(name='C*B', voltage_corner='nom', content_expect=10, _utlno=1, hsd='http:/a')
        # case loc - pass case
        Trust("activity#1", loc='CLASSHOT', chot=KILL)
        # case loc - skip case
        Trust("activity#2", loc='CLASSCOLD', chot=KILL)
        # case edc - por case
        Trust("activity#3", chot=EDC, edc=True, hsd='http:/b')
        # case edc - non por case
        Trust("activity#4", chot=EDC)
        # case unspecified loc
        Trust("activity#5", ccold=KILL)
        # case enabled
        Trust("activity#6", chot=ENABLED)
        # case future/uncompleted
        Trust("activity#7", chot=202201)
        # case basic - completed
        tt = Trust("activity#8", chot=KILL, ccold=202201, hsd=['http:/c', 'http:/d'], _utlno=10000)

        pr.main()

        pprint(csv.items)
        self.assertEqual(csv.items, [['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCA'],
                                     ['FoundPlan', 'SCN', 'SCN', 3, 10, 'En', '', 'CCB'],
                                     ['PlanHSD', 'SCN', 'SCN', 1, 1, '', 'C*B', 'http:/a'],
                                     ['TrustItem', 'SCN', 'SCN', 'CLASSHOT', '', 1, 'activity#1', 0, 0, 1, 0, 0],
                                     ['TrustItem', 'SCN', 'SCN', 'CLASSHOT', '', 1, 'activity#3', 0, 1, 0, 0, 0],
                                     ['TrustHSD', 'SCN', 'SCN', 'CLASSHOT', 1, 1, 'activity#3', 'http:/b'],
                                     ['TrustItem', 'SCN', 'SCN', 'CLASSHOT', '', 0, 'activity#4', 0, 1, 0, 0, 0],
                                     ['TrustItem', 'SCN', 'SCN', 'CLASSHOT', '', 0, 'activity#6', 1, 0, 0, 0, 0],
                                     ['TrustItem', 'SCN', 'SCN', 'CLASSHOT', 202201, 0, 'activity#7', 0, 0, 0, 0, 0],
                                     ['TrustItem', 'SCN', 'SCN', 'CLASSHOT', '', 1, 'activity#8', 0, 0, 1, 0, 0],
                                     ['TrustHSD', 'SCN', 'SCN', 'CLASSHOT', 1, 2, 'activity#8', 'http:/c'],
                                     ['TrustHSD', 'SCN', 'SCN', 'CLASSHOT', 2, 2, 'activity#8', 'http:/d'],
                                     ['TrustSummary', 'SCN', 'SCN', 6, 1, 1, 3, 0, 0, 'SCN'],  # Total Enabled EDC POR WIP Blocked
                                     ['ModSummary', 'SCN', 'SCN', 0, 20, 6, 20, 0, 2, 2, 2, 'SCN']])

        # check the final csv Summary
        csv.write(True, passfail=pr.passfail)
        result = File(csvfile).read()
        result = '\n'.join(x for x in result.split('\n') if x.startswith('Summary,'))
        self.assertTextEqual(result, 'Summary,SCN,SCN,0,20,6,20,3,8,6,8')
        self.assertEqual(f'{tt}', "Trust('activity#8', chot=-3, ccold=202201, id_lno=10000, module=SCN, hsd=['http:/c', 'http:/d'])")

    @with_(TempDir, chdir=True)
    def test_twomodule(self):
        # pure trust, two modules, one is arbitrary
        Waiver.wobj_list.clear()
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf).pickle_init()
        csvfile = './a.csv'
        csv = CsvPlan(tp, outfile=csvfile, modwaiver=modwaiver())
        pr = PlanReport(tp, csv=csv)

        Trust("activity#1", chot=KILL, module='SCN')    # completed
        Trust("activity#2", chot=202130, module='MYIDV')  # not complete
        with CaptureStdoutLog() as p:
            pr.main()

        expect = f'''TP: Simple1Real, {Env.xpath(normpath(tpf))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for MYIDV:
   Content rollup POR:     0/0
   Content rollup Enabled: 0/0
   Feature rollup POR:     0/1
   Feature rollup Enabled: 0/1
   Feature found  Total:   0/0
Trust Result for CLASSHOT:
   Enabled Only: 0/1
   EDC Only:     0/1
   POR:          0/1
   WIP:          0/1
   BLOCKED:      0/1
Missing from testprogram:
   None
Missing from testplan:
   None
Feature misses:
   None
Result for SCN:
   Content rollup POR:     0/0
   Content rollup Enabled: 0/0
   Feature rollup POR:     1/1
   Feature rollup Enabled: 1/1
   Feature found  Total:   0/0
Trust Result for CLASSHOT:
   Enabled Only: 0/1
   EDC Only:     0/1
   POR:          1/1
   WIP:          0/1
   BLOCKED:      0/1
Missing from testprogram:
   None
Missing from testplan:
   1. SCN CCA: voltage_corner=nom freq=NONE tid=3
   2. SCN CCB: voltage_corner=nom freq=NONE tid=3
Feature misses:
   None'''
        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

        # check the final csv
        csv.write(True, passfail=pr.passfail)
        expect = """
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,MYIDV,MYIDV,0,0,0,0,0,1,0,1
Summary,SCN,SCN,0,0,0,0,1,1,1,1
SummaryTotal,,,0,0,0,0,1,2,1,2
WeightedPct,,,,0.0%,,0.0%,,5.0%,,5.0%

HeadTrustSum,Module,Team,Total,Enabled,EDC,POR,WIP,Blocked,IP
TrustSummary,MYIDV,MYIDV,1,0,0,0,0,0,MYIDV
TrustSummary,SCN,SCN,1,0,0,1,0,0,SCN

HeadMissingPlan,Module,Team,tid_count,X,corner,Detail
MissingFromPlan,SCN,SCN,3,,nom,CCA
MissingFromPlan,SCN,SCN,3,,nom,CCB

HeadMissMod,Module,Team,tid_count,X,TestInsCount

HeadTrustItem,Module,Team,Location,ETA,POR,Item,Enabled,EDC,Kill,WIP,Blocked
TrustItem,MYIDV,MYIDV,CLASSHOT,202130,0,activity#2,0,0,0,0,0
TrustItem,SCN,SCN,CLASSHOT,,1,activity#1,0,0,1,0,0
"""
        result = File(csvfile).read()
        result = '\n'.join(x for x in result.split('\n') if not x.startswith(('TimeStamp', 'MissingModule')))
        self.assertTextEqual(result, expect)


class TestTPAuditPlan(TestCase):

    def test_plan(self):
        TP.set_tp(None)
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        pf = f'{ROOT_ENV}/main/test/simple1_testplan.py'
        with TempDir(name=True) as tdir:
            outfile = f'{tdir}/a.csv'
            cmd = f'tp_plan.py -tp {tp} {pf} -out {outfile}'.split()
            with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
                TPPlans().main()

            expect = f"""Plan file: {Env.xpath(normpath(pf))}
TP: Simple1Real, {Env.xpath(normpath(tp))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Result for ARR:
   Content rollup POR:     1/20
   Content rollup Enabled: 1/20
   Feature rollup POR:     1/2
   Feature rollup Enabled: 1/2
   Feature found  Total:   1/2
Result w/ waiver:
   Content rollup POR:     1/10
   Content rollup Enabled: 1/10
   Feature rollup POR:     1/1
   Feature rollup Enabled: 1/1
Missing from testprogram:
   1. Plan('Z*B', id_lno=8, module=ARR, voltage_corner=max) (WAIVED)
Missing from testplan:
   1. ARR CCB: voltage_corner=nom freq=NONE tid=1
Feature misses:
   None
Result for SCN:
   Content rollup POR:     0/21
   Content rollup Enabled: 4/21
   Feature rollup POR:     0/3
   Feature rollup Enabled: 0/3
   Feature found  Total:   2/3
Missing from testprogram:
   1. Plan('*D', id_lno=11, module=SCN, voltage_corner=nom)
Missing from testplan:
   None
Feature misses:
   1. Plan('C*A', id_lno=9, module=SCN): tid_expect extra_count=3, Extra tid: 2371433,2371470,2371471
   2. Plan('C*B', id_lno=12, module=SCN): TestMode mismatch [1.2/2.7] vs tp:[SingleVmin]
Large variation of tid_expect vs content_expect:
   1. Plan(id_lno=9, content_expect=10): tid_expect count=3"""

            self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)

            # Display the csv in friendly output, for visual purposes
            print("========== Start of csv output")
            cmd = f'tp_plans.py {outfile} -csv'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()

            # Check the number of lines. See test_regress() to check contents of .csv (more comprehensive)
            self.assertEqual(len(File(outfile).read().split('\n')), 40)   # number of lines in csv
            self.assertEqual(TP.loc(), 'CLASSHOT')
            self.assertEqual(TP.loc('CLASSH'), True)
            self.assertEqual(TP.loc('CLASSC'), False)
            self.assertEqual(TP.name('.*1'), True)
            self.assertEqual(TP.name('.*2'), False)
            self.assertEqual(TP.name(), 'Simple1Real')

    def test_debugplan(self):
        TP.set_tp(None)
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        pf = f'{ROOT_ENV}/main/test/simple1_testplan.py'
        cmd = f'tp_plan.py -tp {tp} {pf} -debugplan 7=CCA'.split()
        with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
            tpi = TPPlans()
            obj = tpi.do_tp()

        expect = f"""Plan file: {Env.xpath(normpath(pf))}
TP: Simple1Real, {Env.xpath(normpath(tp))}, SubTestPlan_CLASS_TGLH81.stpl, CLASSHOT
Start debug ======
Debug for: Plan('C*A', id_lno=7, module=ARR, voltage_corner=nom, edc=True)
Namefield for CCA:
Data for CCA:
   TEMPLATE   = 'iCSimpleScoreboardTest'
   _CORNER    = 'nom'
   _EDCKIL    = 'EDC'
   _FREQ      = 'NONE'
   bypass_global = 3
   level      = 'BASE::DDR_univ_lvl_nom_lvl'
   patlist    = 'shops_L_list'
   timings    = 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'
Match Result: MATCH"""

        self.assertTextEqual('\n'.join([Env.xpath(line) for line in trimut(p.getvalue())]), expect)
        self.assertEqual(obj.vars, {'F1_FLT': 1.2,
                                    'F1_INT': 12,
                                    'F1_STR': '1.2',
                                    'UNITTEST_V1': '2.7',
                                    'UT_DIR_REPO': f'{UT_DIR_REPO}'})


class Prototypes(TestCase):
    pass

    # See below for initial "spec" language. A -> B -> C -> D pass flow.

    # def nameA(ScreenTest):
    #     port2 = 'F'
    #
    # def nameB(Vmin, id='C'):
    #
    #     def nameF(Func):
    #         blah=1
    #
    # def nameC(Fast, id='D'):
    #     def nameG(Func):
    #         blah=2
    #
    #     def nameH(Func):
    #         port1 = 'E'
    #
    # def nameD(Fast):
    #     patlist = 'aa'


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
