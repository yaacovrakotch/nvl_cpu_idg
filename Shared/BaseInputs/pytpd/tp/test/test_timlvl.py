#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for timlvl.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from tp.timlvl import *
from tp.testprogram import TestProgram
from main.tp_audit import TPInfo
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.files import TempDir, File
from gadget.dictmore import keys_atlevel
from gadget.tputil import volt_disp, time_disp
from gadget.helperclass import CaptureStdoutLog, OPT
from pprint import pprint
from mod.setting import cfg
from unittest.mock import Mock
import tp.timlvl as timlvl


class TestTL(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_regress(self):

        print("RPL Torch start========")
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        self.assertEqual(len(list(tp.timing.iter_tc())), 130)
        self.assertEqual(len(list(tp.levels.iter_tc())), 278)

        print('TGL81 start==========')
        tp = TestProgram(f'{UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        self.assertEqual(len(list(tp.timing.iter_tc())), 155)
        self.assertEqual(len(list(tp.levels.iter_tc())), 268)

        print("ICL start==========")
        tp = TestProgram(f'{UT_DIR}/ICLXXXXXXH58G2XS904/TPL/EnvironmentFile_CLASS_ICL_42_U.env',
                         stpl='SubTestPlan_CLASS_ICL_42_U.stpl')
        self.assertEqual(len(list(tp.timing.iter_tc())), 217)
        self.assertEqual(len(list(tp.levels.iter_tc())), 583)

        print("ICX start==========")
        tp = TestProgram(f'{UT_DIR}/ICXXXXXAXH10G10S922/EnvironmentFile_CLASS_HCCSP.env')
        self.assertEqual(len(list(tp.timing.iter_tc())), 54)
        self.assertEqual(len(list(tp.levels.iter_tc())), 351)   # this caught a bug

        print("TGL42 start==========")
        tp = TestProgram(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        self.assertEqual(len(list(tp.timing.iter_tc())), 266)
        self.assertEqual(len(list(tp.levels.iter_tc())), 784)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_realtp(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        obj = tp.timing
        self.assertEqual(len(list(obj.iter_tc())), 266)
        self.assertEqual(len(obj._specset), 54)
        self.assertEqual(set(obj._timing), {'IP_PCH_BASE::pch_mtd',
                                            'IP_PCH_BASE::pch_scan',
                                            'IP_PCH_BASE::pch_tam',
                                            'IP_CPU_BASE::cpu_func_stf_univ',
                                            'IP_CPU_BASE::mcp_func_univ',
                                            'IP_CPU_BASE::shops_timing',
                                            'IP_CPU_BASE::cpu_func_sdr_univ',
                                            '__main__::pch_mtd_pkg',
                                            '__main__::mcp_func_univ_pkg',
                                            '__main__::shops_timing_pkg',
                                            '__main__::cpu_func_stf_univ_pkg',
                                            '__main__::cpu_func_sdr_univ_pkg'})
        self.assertEqual(len(list(keys_atlevel(obj._timing['__main__::cpu_func_sdr_univ_pkg'], 1))), 69)
        self.assertEqual(len(list(keys_atlevel(obj._timing['__main__::cpu_func_sdr_univ_pkg'], 2))), 139)

        # signature based calculation
        sum = 0
        notexist = 0
        for tc in obj.iter_tc():
            try:
                sum += obj.get_tc_value(tc, 'c_bclk_per')
            except BaseException:
                notexist += 1

        self.assertEqual(time_disp(sum).strip(), '2.425uS')
        self.assertEqual(notexist, 48)  # These are pch

    def test_basic(self):
        # unittest on simple tim and tcg file
        # good template
        with TempDir(name=True) as tdir:
            code = """
Import bb.tcg
Import bb.tim
TestPlan ARR;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.tcg
Import aa.tim
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
# comment only
Timing shops_timing_pkg
{
        Domain ALL
        {
                PeriodTable
                {
                        Period = tper;
                }
                all_dmn
                {
                        drive = c_cpushops_drv;
                }
        }
} #End of Timing Block shops_timing_pkg
"""
            File('%s/aa.tim' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
ThermalControl ThermalControl_TDYN_9 {
    VCC_IN_HC     {
        PowerScale=factor;
    } VCC_INAUX_HC {
        PowerScale=factor;
    }
    TDYN_9 {
       #B1=0;
       SumScale = factor;  }
}

SpecificationSet STF_univ_lvl_BFUNC (aaa, bbb, ccc, ddd)
{
        Double tper = 1, toInteger(2), toDouble(3), 4;
        Double p_vcc_gb_type = 0.1,0.2,0.3, 1.0;
        Voltage p_vccio_spec = 1.2V;
        Voltage p_prim_1p8_spec = uv_prim_1p8_spec_nom;
        Voltage tester_gb_hc = hc_vcc_gb*p_vcc_gb_type*cl_qa_flag;
        Double ter1 = (tper==1?5V:6V);
}
TestConditionGroup STF_univ_lvl_TCG
{
        SpecificationSet = STF_univ_lvl_BFUNC ;
        Timing = __main__::shops_timing_pkg;
}
TestCondition tc1
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = bbb;
}
TestCondition tc2
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = aaa;
}
"""
            File('%s/aa.tcg' % tdir).touch(code, mkdir=True)
            code = code.replace('Timing =', 'Level =')
            File('%s/Modules/ARR/bb.tcg' % tdir).touch(code, mkdir=True)

            code = """
UserVars
{
        Integer uv_prim_1p8_spec_nom = 1;
        Double hc_vcc_gb = 0.1;
        Integer cl_qa_flag = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)
            File('%s/Modules/ARR/bb.tim' % tdir).touch(mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.timing
            obj.set_data()

            self.assertEqual(list(obj._timing), ['__main__::shops_timing_pkg'])
            self.assertEqual(len(obj._timing['__main__::shops_timing_pkg']), 1)

            expect = {'BASE::STF_univ_lvl_BFUNC': {'_SELECTOR': ['aaa', 'bbb', 'ccc', 'ddd'],
                                                   'p_prim_1p8_spec': 'uv_prim_1p8_spec_nom',
                                                   'tper': '1 toInteger(2) toDouble(3) 4'.split(),
                                                   'p_vcc_gb_type': ['0.1', '0.2', '0.3', '1.0'],
                                                   'p_vccio_spec': '1.2V',
                                                   'ter1': 'tper==1?5V:6V',
                                                   'tester_gb_hc': 'hc_vcc_gb*p_vcc_gb_type*cl_qa_flag'}}
            pprint(obj._specset)
            self.assertEqual(obj._specset, expect)
            self.assertEqual(len(obj._thermalcontrol['ARR::ThermalControl_TDYN_9']), 9)

            self.assertEqual(obj.get_tc_dict(),
                             {'BASE::tc1': {'Selector': 'bbb',
                                            'SpecificationSet': 'BASE::STF_univ_lvl_BFUNC',
                                            'TCG': 'STF_univ_lvl_TCG',
                                            'Inherit': None,
                                            'Timing': '__main__::shops_timing_pkg'},
                              'BASE::tc2': {'Selector': 'aaa',
                                            'SpecificationSet': 'BASE::STF_univ_lvl_BFUNC',
                                            'TCG': 'STF_univ_lvl_TCG',
                                            'Inherit': None,
                                            'Timing': '__main__::shops_timing_pkg'}})
            self.assertEqual(list(obj.iter_tc()), ['BASE::tc1', 'BASE::tc2'])
            self.assertEqual(list(x for x, y in obj.iter_params('BASE::tc1')),
                             'tper p_vcc_gb_type p_vccio_spec p_prim_1p8_spec tester_gb_hc ter1'.split())
            self.assertEqual(list(y for x, y in obj.iter_params('BASE::tc1')),
                             'toInteger(2) 0.2 1.2V uv_prim_1p8_spec_nom hc_vcc_gb*p_vcc_gb_type*'
                             'cl_qa_flag tper==1?5V:6V'.split())
            self.assertEqual(list(y for x, y in obj.iter_params('BASE::tc1', isvalue=True)),
                             [2.0, 0.2, 1.2, 1, 0.0, 6])

            self.assertEqual(obj.get_period_param('BASE::tc1'), {'tper': 2})
            self.assertEqual(obj.get_tc_value('BASE::tc1', 'p_vcc_gb_type'), 0.2)
            self.assertEqual(obj.get_tc_value('BASE::tc1', 'ter1'), 6)
            self.assertEqual(obj.get_tc_value('BASE::tc2', 'ter1'), 5)

            # set_param ==============================
            def raw_value(t_obj, tc, p):
                ss = t_obj._tc[tc]['SpecificationSet']
                return t_obj._specset[ss][p]

            # case1: param value
            testcondition = 'BASE::tc1'
            param = 'p_vccio_spec'
            self.assertEqual(obj.get_tc_param(testcondition, param), '1.2V')   # baseline
            self.assertEqual(raw_value(obj, testcondition, param), '1.2V')     # baseline
            result = list(obj.set_param(testcondition, param, '55V'))
            self.assertEqual(obj.get_tc_param(testcondition, param), '55V')
            # This is expected info
            self.assertEqual(raw_value(obj, testcondition, param), '55V')
            self.assertEqual(len(result), 1)   # only one result

            # case2-1: param list
            testcondition = 'BASE::tc1'
            param = 'p_vcc_gb_type'
            self.assertEqual(obj.get_tc_param(testcondition, param), '0.2')   # baseline
            self.assertEqual(raw_value(obj, testcondition, param), ['0.1', '0.2', '0.3', '1.0'])  # baseline
            result = list(obj.set_param(testcondition, param, '33'))
            self.assertEqual(obj.get_tc_param(testcondition, param), '33')
            # This is expected info
            self.assertEqual(raw_value(obj, testcondition, param), ['0.1', '33', '0.3', '1.0'])
            self.assertEqual(len(result), 1)   # only one result

            # case2-2: regex testcondition
            result = list(obj.set_param('t*', param, '33'))
            self.assertEqual(obj.get_tc_param(testcondition, param), '33')
            # This is expected info
            self.assertEqual(raw_value(obj, testcondition, param), ['33', '33', '0.3', '1.0'])
            self.assertEqual(len(result), 2)
            self.assertIn(None, [x[0] for x in result])   # one of them is None

            # case2-3: regex testcondition 2
            result = list(obj.set_param('t*', param, '44'))
            self.assertEqual(obj.get_tc_param(testcondition, param), '44')
            # This is expected info
            self.assertEqual(raw_value(obj, testcondition, param), ['44', '44', '0.3', '1.0'])
            self.assertEqual(len(result), 2)
            self.assertNotIn(None, [x[0] for x in result])

            # case3: regex testcondition not found
            result = list(obj.set_param('*c', param, '55'))
            self.assertEqual(obj.get_tc_param(testcondition, param), '44')
            # This is expected info
            self.assertEqual(raw_value(obj, testcondition, param), ['44', '44', '0.3', '1.0'])
            self.assertEqual(len(result), 0)   # none found

            # evaluate=False, used with PgmRule ==========================================
            tp = TestProgram(envfile)._ut_write_stpl()
            tp.timing.set_data(evaluate=False)
            self.assertEqual(tp.timing._ss_eval, None)

    def test_incorrect_length(self):
        # caught in arl build. See LOOK below.
        with TempDir(name=True) as tdir:
            code = """
Import bb.tcg
Import bb.tim
TestPlan ARR;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.tcg
Import aa.tim
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
# comment only
Timing shops_timing_pkg
{
        Domain ALL
        {
                PeriodTable
                {
                        Period = tper;
                }
                all_dmn
                {
                        drive = c_cpushops_drv;
                }
        }
} #End of Timing Block shops_timing_pkg
"""
            File('%s/aa.tim' % tdir).touch(code, mkdir=True)
            code = """Version 1.0;
ThermalControl ThermalControl_TDYN_9 {
    VCC_IN_HC     {
        PowerScale=factor;
    } VCC_INAUX_HC {
        PowerScale=factor;
    }
    TDYN_9 {
       #B1=0;
       SumScale = factor;  }
}

SpecificationSet STF_univ_lvl_BFUNC (aaa, bbb, ccc, ddd)
{
        Double tper = 1, toInteger(2), toDouble(3), 4;
        Double p_vcc_gb_type = 0.1,0.2,0.3;     # <<<< This does not match args. LOOK
        Voltage p_vccio_spec = 1.2V;
        Voltage p_prim_1p8_spec = uv_prim_1p8_spec_nom;
        Voltage tester_gb_hc = hc_vcc_gb*p_vcc_gb_type*cl_qa_flag;
        Double ter1 = (tper==1?5V:6V);
}
TestConditionGroup STF_univ_lvl_TCG
{
        SpecificationSet = STF_univ_lvl_BFUNC ;
        Timing = __main__::shops_timing_pkg;
}
TestCondition tc1
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = bbb;
}
TestCondition tc2
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = aaa;
}
"""
            File('%s/aa.tcg' % tdir).touch(code, mkdir=True)
            code = code.replace('Timing =', 'Level =')
            File('%s/Modules/ARR/bb.tcg' % tdir).touch(code, mkdir=True)

            code = """
UserVars
{
        Integer uv_prim_1p8_spec_nom = 1;
        Double hc_vcc_gb = 0.1;
        Integer cl_qa_flag = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)
            File('%s/Modules/ARR/bb.tim' % tdir).touch(mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.timing
            with self.assertRaisesRegex(ErrorInput, 'Error on .p_vcc_gb_type'):
                obj.set_data()

    def test_invalid_timing_line(self):
        # invalid tcg line =============================
        with TempDir(name=True) as tdir:
            code = """
Import aa.tcg
Import aa.tim
Import aa.usrv
TestPlan ABC;
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
# comment only
Timing shops_timing_pkg
{
        Domain ALL
        {
                PeriodTable
                {
                        Period = tper;
                }
        }
} #End of Timing Block shops_timing_pkg
"""
            File('%s/aa.tim' % tdir).touch(code, mkdir=True)
            code = """
SpecificationSet STF_univ_lvl_BFUNC (aaa, bbb, ccc, ddd)
{
        Double tper = 1, 2, 3, 4;
        Double p_vcc_gb_type = 0.1,0.2,0.3, 1.0;
        Voltage p_vccio_spec = 1.2V;
        Voltage p_prim_1p8_spec = uv_prim_1p8_spec_nom;
        Voltage tester_gb_hc = hc_vcc_gb*p_vcc_gb_type*cl_qa_flag;
        Double ter1 = (tper==1?5V:6V);
        Random line
}
"""
            File('%s/aa.tcg' % tdir).touch(code, mkdir=True)
            code = """
UserVars
{
        Integer uv_prim_1p8_spec_nom = 1;
        Double hc_vcc_gb = 0.1;
        Integer cl_qa_flag = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('TestPlan ARR;', mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.timing
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown tcg line'):
                obj.set_data()

            # invalid timing line - random line
            code = """
# comment only
Timing shops_timing_pkg
{
        Domain ALL
        {
                PeriodTable
                {
                        Period = tper;
                }
        }
} #End of Timing Block shops_timing_pkg
random line
"""
            File('%s/a1.tim' % tdir).touch(code, newfile=True, mkdir=True)
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown tim line'):
                obj._timing = {}
                obj._read_tim_file('%s/a1.tim' % tdir)

            # invalid timing line - extra }
            code = """
# comment only
Timing shops_timing_pkg
{
        Domain ALL
        {
                PeriodTable
                {
                        Period = tper;
                }
        }
} #End of Timing Block shops_timing_pkg
}
"""
            File('%s/a1.tim' % tdir).touch(code, newfile=True, mkdir=True)
            with self.assertRaisesRegex(ErrorInput, 'Mismatched closed parenthesis'):
                obj._timing = {}
                obj._read_tim_file('%s/a1.tim' % tdir)

            # invalid timing line - value
            code = """
# comment only
Timing shops_timing_pkg
{
        Domain ALL
        {
                PeriodTable
                {
                        Period = tper
                }
        }
} #End of Timing Block shops_timing_pkg
"""
            File('%s/a1.tim' % tdir).touch(code, newfile=True, mkdir=True)
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown tim line'):
                obj._timing = {}
                obj._read_tim_file('%s/a1.tim' % tdir)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_evaluate_mtt(self):
        # This also addres coverage inside _MTT lambda
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        tp.usrv.set_data()
        obj = tp.timing

        obj._specset = {'A': {'_SELECTOR': ['aa'],
                              'a': '[1, 2]',
                              'aa': '_MTT(a) + _MTT(2)',
                              }
                        }
        obj._ss_order = {'A': 'a aa'.split()}

        data = {}
        obj._evaluate_selector('A', 'aa', data, tp.usrv.uflat, usrv_local=tp.usrv.userv_local('A'))
        expect = {'a': [1, 2],
                  'aa': 3}
        self.assertEqual(data, expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_evaluate(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        obj = tp.timing
        usrv_nd = {'usrv': 1,
                   f'SA{SEP}bar1': 2}
        obj._specset = {'A': {'_SELECTOR': ['aa', 'bb'],
                              'var1': ['-0.1', '-0.2'],
                              'var2': '0.1',
                              'var3': '1nS+1nS',
                              'var4': '-2nS',
                              'var5': '4.6GHz + 2nS',
                              'var6a': '10nS*99GHz/99GHz',
                              'var6': '1',
                              'var7': '1+var6',
                              'var8': '1+var7',
                              'var9': '1+var8+var7',
                              'var': '100+SA.bar1+1',
                              'varA': 'usrv',
                              'varB': 'varA+1',
                              'varC': 'varB+1',
                              'varD': 'varC+1',
                              'varE': 'usrv'
                              }
                        }
        obj._ss_order = {'A': sorted([x for x in obj._specset['A'] if x != '_SELECTOR'])}
        # print(obj._ss_order['A'])

        data = {}
        obj._evaluate_selector('A', 'aa', data, usrv_nd)
        # Dumper(data)
        expect = {'var1': -0.1,
                  'var2': 0.1,
                  'var3': 2e-09,
                  'var4': -2e-09,
                  'var5': 2.2173913043478263e-09,
                  'var6a': 1e-08,
                  'var6': 1.0,
                  'var7': 2.0,
                  'var8': 3.0,
                  'var9': 6.0,
                  'var': 103,
                  'varE': 1.0,
                  'varD': 4.0,
                  'varC': 3.0,
                  'varB': 2.0,
                  'varA': 1.0
                  }
        self.assertEqual(data, expect)

        # case 2 ===================
        obj._specset = {'A': {'_SELECTOR': ['aa'],
                              'a': '1V+1V+aa+aaa+aaaa',
                              'aa': 'aaa+1+aaa+aaaa',
                              'aaa': '1+aaaa',
                              'aaaa': '1',
                              }
                        }
        obj._ss_order = {'A': 'aaaa aaa aa a'.split()}

        data = {}
        obj._evaluate_selector('A', 'aa', data, usrv_nd)
        expect = {'a': 11.0,
                  'aa': 6.0,
                  'aaa': 2.0,
                  'aaaa': 1.0
                  }
        self.assertEqual(data, expect)

        # case 3 ===================
        obj._specset = {'A': {'_SELECTOR': ['aa'],
                              'a': 'aa*aa',
                              'aa': '43*aaa+1',
                              'aaa': '1+aaaa',
                              'aaaa': '1',
                              }
                        }
        obj._ss_order = {'A': 'aaaa aaa aa a'.split()}

        data = {}
        obj._evaluate_selector('A', 'aa', data, usrv_nd)
        expect = {'a': 7569,
                  'aa': 87,
                  'aaa': 2.0,
                  'aaaa': 1.0
                  }
        self.assertEqual(data, expect)

        # invalid case1 ==================
        print("Start of invalid case1 ===============")
        obj._specset = {'A': {'_SELECTOR': ['aa'],
                              'var2': '1',
                              'var1': '1+1(1)',
                              }
                        }
        obj._ss_order = {'A': [x for x in obj._specset['A'] if x != '_SELECTOR']}
        with self.assertRaisesRegex(ErrorInput, 'Failed to evaluate'):
            obj._evaluate_selector('A', 'aa', {}, usrv_nd)

        # invalid case2 ==================
        print("Start of invalid case2 ===============")
        obj._specset = {'A': {'_SELECTOR': ['aa'],
                              'var1': '1+1+var2',
                              }
                        }
        obj._ss_order = {'A': [x for x in obj._specset['A'] if x != '_SELECTOR']}
        with self.assertRaisesRegex(ErrorInput, 'Failed to evaluate'):
            obj._evaluate_selector('A', 'aa', {}, usrv_nd)

        # case 4, double replace var bug ===================
        usrv_nd = {'usrv': 1,
                   f'SA{SEP}bar1': 2,
                   f'SA{SEP}bar2': 3}
        obj._specset = {'A': {'_SELECTOR': ['s1'],
                              'a': 'SA.bar1+SA.bar2',
                              }
                        }
        obj._ss_order = {'A': 'a'.split()}

        data = {}
        obj._evaluate_selector('A', 's1', data, usrv_nd)
        expect = {'a': 5,
                  }
        self.assertEqual(data, expect)

    def test_evaluate_scope(self):
        # case scoping1 - with scoping ==================
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        obj = tp.timing
        obj._specset = {'IP_CPU::ARR::A': {'_SELECTOR': ['aa'],
                                           'a': 'aa*aa',
                                           'aa': '43*aaa+1',
                                           'aaa': '1+aaaa',
                                           'aaaa': '1'}}
        obj._ss_order = {'IP_CPU::ARR::A': 'aaaa aaa aa a'.split()}

        tp.usrv.set_data()
        obj.evaluate()
        expect = {'a': 7569,
                  'aa': 87,
                  'aaa': 2.0,
                  'aaaa': 1.0
                  }
        self.assertEqual(obj._ss_eval, {'IP_CPU::ARR::A': {'aa': expect}})

        # case scoping2 - no scoping ==================
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        obj = tp.timing
        obj._specset = {'A': {'_SELECTOR': ['aa'],
                              'a': 'aa*aa',
                              'aa': '43*aaa+1',
                              'aaa': '1+aaaa',
                              'aaaa': '1'}}
        obj._ss_order = {'A': 'aaaa aaa aa a'.split()}

        tp.usrv.set_data()
        obj.evaluate()
        expect = {'a': 7569,
                  'aa': 87,
                  'aaa': 2.0,
                  'aaaa': 1.0
                  }
        self.assertEqual(obj._ss_eval, {'A': {'aa': expect}})


class TestTim(TestCase):

    def test_basic(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        self.assertEqual(set(tp.timing.get_timings()), {'__main__::shops_timing_pkg'})
        self.assertEqual(tp.timing.get_pingrps('__main__::shops_timing_pkg'), {'all_dmn': 'ALL'})


class TestLvl(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_realtp(self):
        tp = TestProgram(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        obj = tp.levels
        sw = Elapsed()
        obj.set_data()
        print(f"Total lvl+tcg+eval: {sw}")
        self.assertEqual(len(list(keys_atlevel(obj._levels, 2))), 44212)

    def test_basic(self):
        # unittest on simple lvl and tcg file
        with TempDir(name=True) as tdir:
            code = """
Import bb.tcg
Import bb.lvl
TestPlan ARR;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.tcg
Import aa.lvl
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """

# comment only
Levels DDR_univ_lvl_pkg
{
        clk
        {
                FixedDriveState = Off;
        }
        all_clock_pins_no_stf
        {
                FixedDriveState = Off;
                IRange = IR40mA;
                OPMode = VSIM;
                PinModeSel = PMU;
                VForce = 0V;
                VIH = 0V;
                VIL = 0V;
        }
        SequenceBreak 0ms;
        FIVR_VDDQ_VL_LC
        {
                FreeDriveTime = 1mS;
                IClampHi = 1.2A;
                IClampLo = -0.6A;
                IRange = IR1_2A;
                OPMode = VM;
                PowerSequence = FALSE;
                VForce = c_vccddq_vload_prog;
        }
}
"""
            File('%s/aa.lvl' % tdir).touch(code, mkdir=True)
            code = """
SpecificationSet STF_univ_lvl_BFUNC(aaa, bbb, ccc, ddd)
{
        Double tper = 1, 2, 3, 4;
        Double p_vcc_gb_type = 0.1,0.2,0.3, 1.0;
        Voltage p_vccio_spec = 1.2V;
        Voltage p_prim_1p8_spec = uv_prim_1p8_spec_nom;
        Voltage c_vccddq_vload_prog = hc_vcc_gb+p_vcc_gb_type+cl_qa_flag;
        Double ter1 = (tper==1?5V:6V);
}
TestConditionGroup STF_univ_lvl_TCG
{
        SpecificationSet = STF_univ_lvl_BFUNC;
        Level = __main__::DDR_univ_lvl_pkg;
}
TestCondition tc1
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = bbb;
}
TestCondition tc2
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = aaa;
}
"""
            File('%s/aa.tcg' % tdir).touch(code, mkdir=True)
            code = code.replace('Timing =', 'Level =')
            File('%s/Modules/ARR/bb.tcg' % tdir).touch(code, mkdir=True)

            code = """
UserVars
{
        Integer uv_prim_1p8_spec_nom = 1;
        Double hc_vcc_gb = 0.1;
        Integer cl_qa_flag = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            File('%s/Modules/ARR/bb.lvl' % tdir).touch(mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.levels
            obj.set_data()

            expect = {'FIVR_VDDQ_VL_LC': {'FreeDriveTime': '1mS',
                                          'IClampHi': '1.2A',
                                          'IClampLo': '-0.6A',
                                          'IRange': 'IR1_2A',
                                          'OPMode': 'VM',
                                          'PowerSequence': 'FALSE',
                                          'VForce': 'c_vccddq_vload_prog'},
                      'clk': {'FixedDriveState': 'Off'},
                      'all_clock_pins_no_stf': {'FixedDriveState': 'Off',
                                                'IRange': 'IR40mA',
                                                'OPMode': 'VSIM',
                                                'PinModeSel': 'PMU',
                                                'VForce': '0V',
                                                'VIH': '0V',
                                                'VIL': '0V'}}
            self.assertEqual(obj._levels['__main__::DDR_univ_lvl_pkg'], expect)
            self.assertEqual(len(list(obj.iter_params('BASE::tc1'))), 6)
            result = {x: volt_disp(y) for x, y in obj.get_lvl_param('BASE::tc1').items()}
            self.assertEqual(result, {'c_vccddq_vload_prog': '300mV    '})

            # display=True
            with CaptureStdoutLog() as p:
                print()
                obj.get_lvl_param('BASE::tc1', display=True)
            expect = '''
pin=FIVR_VDDQ_VL_LC        param=c_vccddq_vload_prog            val=0.300V eqn=hc_vcc_gb+p_vcc_gb_type+cl_qa_flag
'''
            self.assertTextEqual(p.getvalue(), expect)

            # get_lvl_pin_val
            self.assertEqual(obj.get_lvl_pin_val('BASE::tc1', 'VForce'),
                             {'FIVR_VDDQ_VL_LC': ('c_vccddq_vload_prog',
                                                  0.30000000000000004,
                                                  'hc_vcc_gb+p_vcc_gb_type+cl_qa_flag'),
                              'all_clock_pins_no_stf': ('0V', '', '')})

            # no evaluate, used with PgmRule
            tp = TestProgram(envfile)._ut_write_stpl()
            tp.levels.set_data(evaluate=False)
            self.assertEqual(tp.levels._ss_eval, None)

            # invalid case1
            File('%s/Modules/ARR/bb.lvl' % tdir).touch('}\n', newfile=True)
            tp = TestProgram(envfile)._ut_write_stpl()
            with self.assertRaisesRegex(ErrorCockpit, 'Invalid line in line#1'):
                tp.levels.set_data()

            # invalid case2
            File('%s/Modules/ARR/bb.lvl' % tdir).touch('somerandom line', newfile=True)
            tp = TestProgram(envfile)._ut_write_stpl()
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown levels line'):
                tp.levels.set_data()

    def test_inherit(self):
        # unittest on simple lvl and tcg file
        with TempDir(name=True) as tdir:
            code = """
Import bb.tcg
Import bb.lvl
TestPlan ARR;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.tcg
Import aa.lvl
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """

# comment only
Levels DDR_univ_lvl_pkg
{
        clk
        {
                FixedDriveState = Off;
        }
        all_clock_pins_no_stf
        {
                FixedDriveState = Off;
                IRange = IR40mA;
                OPMode = VSIM;
                PinModeSel = PMU;
                VForce = 0V;
                VIH = 0V;
                VIL = 0V;
        }
        SequenceBreak 0ms;
        FIVR_VDDQ_VL_LC
        {
                FreeDriveTime = 1mS;
                IClampHi = 1.2A;
                IClampLo = -0.6A;
                IRange = IR1_2A;
                OPMode = VM;
                PowerSequence = FALSE;
                VForce = c_vccddq_vload_prog;
        }
}
"""
            File('%s/aa.lvl' % tdir).touch(code, mkdir=True)
            code = """
SpecificationSet top(aaa, bbb, ccc, ddd)
{
        Double tper = 1, 2, 3, 4;
        Double p_vcc_gb_type = 0.1,0.2,0.3, 1.0;
        Voltage p_vccio_spec = 1.2V;
        Voltage p_prim_1p8_spec = uv_prim_1p8_spec_nom;
        Voltage c_vccddq_vload_prog = 1+hc_vcc_gb+p_vcc_gb_type+cl_qa_flag;
        Double ter1 = (tper==1?5V:6V);
}
"""
            File('%s/aa.tcg' % tdir).touch(code, mkdir=True)
            code = '''
SpecificationSet STF_univ_lvl_BFUNC(aaa, bbb, ccc, ddd) Inherits __main__::top
{
        Voltage c_vccddq_vload_prog = hc_vcc_gb+p_vcc_gb_type+cl_qa_flag;
}
# below is for coverage - unused - due to timing vs levels tcg thing
SpecificationSet STF_univ_lvl_BFUNCXX(aaa, bbb, ccc, ddd) Inherits __main__::top2
{
        Double tper = 11, 12, 13, 14;
}
TestConditionGroup STF_univ_lvl_TCG
{
        SpecificationSet = STF_univ_lvl_BFUNC;
        Level = __main__::DDR_univ_lvl_pkg;
}
TestCondition tc1
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = bbb;
}
TestCondition tc2
{
        TestConditionGroup  = STF_univ_lvl_TCG;
        Selector = aaa;
}
'''
            File('%s/Modules/ARR/bb.tcg' % tdir).touch(code, mkdir=True)

            code = """
UserVars
{
        Integer uv_prim_1p8_spec_nom = 1;
        Double hc_vcc_gb = 0.1;
        Integer cl_qa_flag = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            File('%s/Modules/ARR/bb.lvl' % tdir).touch(mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.levels
            obj.set_data()

            expect = {'FIVR_VDDQ_VL_LC': {'FreeDriveTime': '1mS',
                                          'IClampHi': '1.2A',
                                          'IClampLo': '-0.6A',
                                          'IRange': 'IR1_2A',
                                          'OPMode': 'VM',
                                          'PowerSequence': 'FALSE',
                                          'VForce': 'c_vccddq_vload_prog'},
                      'clk': {'FixedDriveState': 'Off'},
                      'all_clock_pins_no_stf': {'FixedDriveState': 'Off',
                                                'IRange': 'IR40mA',
                                                'OPMode': 'VSIM',
                                                'PinModeSel': 'PMU',
                                                'VForce': '0V',
                                                'VIH': '0V',
                                                'VIL': '0V'}}
            self.assertEqual(obj._levels['__main__::DDR_univ_lvl_pkg'], expect)
            self.assertEqual(len(list(obj.iter_params('ARR::tc1'))), 6)
            result = {x: volt_disp(y) for x, y in obj.get_lvl_param('ARR::tc1').items()}
            self.assertEqual(result, {'c_vccddq_vload_prog': '300mV    '})
            self.assertEqual(obj.get_tc_dict()['ARR::tc1'], {'Level': '__main__::DDR_univ_lvl_pkg',
                                                             'SpecificationSet': 'ARR::STF_univ_lvl_BFUNC',
                                                             'Selector': 'bbb',
                                                             'TCG': 'STF_univ_lvl_TCG',
                                                             'Inherit': 'BASE::top'})

            # display=True
            with CaptureStdoutLog() as p:
                print()
                obj.get_lvl_param('ARR::tc1', display=True)
            expect = '''
pin=FIVR_VDDQ_VL_LC        param=c_vccddq_vload_prog            val=0.300V eqn=hc_vcc_gb+p_vcc_gb_type+cl_qa_flag
'''
            self.assertTextEqual(p.getvalue(), expect)

            # get_lvl_pin_val
            self.assertEqual(obj.get_lvl_pin_val('ARR::tc1', 'VForce'),
                             {'FIVR_VDDQ_VL_LC': ('c_vccddq_vload_prog',
                                                  0.30000000000000004,
                                                  'hc_vcc_gb+p_vcc_gb_type+cl_qa_flag'),
                              'all_clock_pins_no_stf': ('0V', '', '')})


class TestEP(TestCase):

    def test_line_split(self):
        ep = ExprParser
        # basic
        self.assertEqual(ep._line_split('a = "b cd";'), ['a', '=', '"b cd"', ';'])
        self.assertEqual(ep._line_split('a=b+a_b+1.2;'), ['a', '=', 'b', '+', 'a_b', '+', '1.2', ';'])
        self.assertEqual(ep._line_split('a = b + a_b + 1.2 ;'), ['a', '=', 'b', '+', 'a_b', '+', '1.2', ';'])
        # no space
        self.assertEqual(ep._line_split('a="bcd";'), ['a', '=', '"bcd"', ';'])
        # mixed
        self.assertEqual(ep._line_split('a = "b a"+"g h"a;'), ['a', '=', '"b a"', '+', '"g h"', 'a', ';'])
        self.assertEqual(ep._line_split("a = 'b a'+'g h';"), ['a', '=', "'b a'", '+', "'g h'", ';'])
        self.assertEqual(ep._line_split("""a='b a"'+ 'g "h"'"""), ['a', '=', '\'b a"\'', '+', '\'g "h"\''])
        # lots of space
        self.assertEqual(ep._line_split('  a  =   "b\' c d"  ;'), ['a', '=', '"b\' c d"', ';'])
        self.assertEqual(ep._line_split('a="b\' c;d";'), ['a', '=', '"b\' c;d"', ';'])
        # parenthesis and comma
        self.assertEqual(ep._line_split('a=b+(a_b)+1.2;'),
                         ['a', '=', 'b', '+', '(', 'a_b', ')', '+', '1.2', ';'])
        self.assertEqual(ep._line_split('a=b+((a_b))+1.2;'),
                         ['a', '=', 'b', '+', '(', '(', 'a_b', ')', ')', '+', '1.2', ';'])
        self.assertEqual(ep._line_split('a=b+(a,b)+1.2;'),
                         ['a', '=', 'b', '+', '(', 'a', ',', 'b', ')', '+', '1.2', ';'])
        self.assertEqual(ep._line_split('a=("", "", "abc")'),
                         ['a', '=', '(', '""', ',', '""', ',', '"abc"', ')'])
        self.assertEqual(ep._line_split("a=('', '', 'abc')"),
                         ['a', '=', '(', "''", ',', "''", ',', "'abc'", ')'])

    def test_tokenize(self):
        ep = ExprParser
        # basic
        self.assertEqual(ep._tokenize('a==b+45')[0], ['a', '==', 'b', '+', '45'])
        self.assertEqual(ep._tokenize('a == b + .45')[0], ['a', '==', 'b', '+', '.45'])
        self.assertEqual(ep._tokenize('(a==b)'), (['a==b'], ['E']))
        self.assertEqual(ep._tokenize('((a==b))'), (['(a==b)'], ['E']))
        # expr
        self.assertEqual(ep._tokenize('a.c=b+(45)')[0],
                         ['a.c', '=', 'b', '+', '45'])
        self.assertEqual(ep._tokenize('a=b+(4+(4+(2+1 )))')[0],
                         ['a', '=', 'b', '+', '4+(4+(2+1))'])
        # function
        self.assertEqual(ep._tokenize('a=b(4+2,c)')[0],
                         ['a', '=', 'b', '(', '4+2', ',', 'c', ')'])
        self.assertEqual(ep._tokenize('a=b ((4+2),"a",c(1))')[0],
                         ['a', '=', 'b', '(', '(4+2)', ',', '"a"', ',', 'c(1)', ')'])
        self.assertEqual(ep._tokenize('b(1,b,"c",4+2)'),
                         (['b', '(', '1', ',', 'b', ',', '"c"', ',', '4+2', ')'],
                          ['W', 'P', 'W', 'C', 'W', 'C', 'Q', 'C', 'E', 'P']))
        # quotes
        self.assertEqual(ep._tokenize('a=b("4(,2)","c+1")')[0],
                         ['a', '=', 'b', '(', '"4(,2)"', ',', '"c+1"', ')'])
        self.assertEqual(ep._tokenize('a=("4(,2)","c+1")')[0],
                         ['a', '=', '"4(,2)","c+1"'])
        self.assertEqual(ep._tokenize('a=b("", "", "abc")')[0],
                         ['a', '=', 'b', '(', '""', ',', '""', ',', '"abc"', ')'])
        self.assertEqual(ep._tokenize('a=("", "", "abc")')[0],
                         ['a', '=', '"","","abc"'])
        self.assertEqual(ep._tokenize("a=b('', '', 'abc')")[0],
                         ['a', '=', 'b', '(', "''", ',', "''", ',', "'abc'", ')'])
        # combination
        self.assertEqual(ep._tokenize('a=4+foo(1+2,(3+4),foo("a+b","a(b)"))')[0],
                         ['a', '=', '4', '+', 'foo', '(', '1+2', ',', '(3+4)', ',', 'foo("a+b","a(b)")', ')'])
        # ternary
        self.assertEqual(ep._tokenize('a=a==b?"a:c":"d:e"')[0],
                         ['a', '=', 'a', '==', 'b', '?', '"a:c"', ':', '"d:e"'])
        self.assertEqual(ep._tokenize('a=a==b?("a:c"):("d:e")')[0],
                         ['a', '=', 'a', '==', 'b', '?', '"a:c"', ':', '"d:e"'])
        # numbers
        self.assertEqual(ep._tokenize('1.0+.1e-9,-1.2,1e+3'),
                         (['1.0', '+', '.1e-9', ',', '-1.2', ',', '1e+3'],
                          ['W', 'O', 'W', 'C', 'W', 'C', 'W']))
        self.assertEqual(ep._tokenize('1e-9v'), (['1e-9v'], ['W']))
        self.assertEqual(ep._tokenize('1e-'), (['1e', '-'], ['W', 'O']))   # make sure it does not error
        self.assertEqual(ep._tokenize('1e'), (['1e'], ['W']))              # make sure it does not error
        # minus sign and colon
        self.assertEqual(ep._tokenize('-1')[0], (['-1']))
        self.assertEqual(ep._tokenize('?-1')[0], (['?', '-1']))
        self.assertEqual(ep._tokenize('a:-1')[0], (['a', ':', '-1']))
        self.assertEqual(ep._tokenize('a::-1')[0], (['a', '::', '-1']))
        self.assertEqual(ep._tokenize('a::-e')[0], (['a', '::-', 'e']))
        self.assertEqual(ep._tokenize('a?-1')[0], (['a', '?', '-1']))
        self.assertEqual(ep._tokenize('a?-e')[0], (['a', '?', '-', 'e']))
        self.assertEqual(ep._tokenize('a?+e')[0], (['a', '?', '+', 'e']))

        # srf case, dot can have space and TOS accepts this
        self.assertEqual(ep._tokenize('a.b+1')[0], (['a.b', '+', '1']))
        self.assertEqual(ep._tokenize('a. b+1')[0], (['a.b', '+', '1']))
        self.assertEqual(ep._tokenize('a .b+1')[0], (['a.b', '+', '1']))
        self.assertEqual(ep._tokenize('a.+a.')[0], (['a.', '+', 'a.']))

        # LNL case
        self.assertEqual(ep._tokenize('(-1,1)')[0], ['-1,1'])
        self.assertEqual(ep._tokenize('[1,1]')[0], ['[', '1', ',', '1', ']'])
        self.assertEqual(ep._tokenize('[-1,1]')[0], ['[', '-1', ',', '1', ']'])

        # type check
        self.assertEqual(ep._tokenize('_a._b=b("4(,2)",(4+2),a.c_d==26,c(1))'),
                         (['_a._b', '=', 'b', '(', '"4(,2)"', ',', '(4+2)', ',', 'a.c_d==26', ',', 'c(1)', ')'],
                          ['W', 'O', 'W', 'P', 'Q', 'C', 'E', 'C', 'E', 'C', 'E', 'P']))

        with self.assertRaisesRegex(AssertionError, 'Mismatched parenthesis'):
            ep._tokenize('a=b+(4+(4+(2+1))')
        with self.assertRaisesRegex(AssertionError, 'Mismatched parenthesis'):
            ep._tokenize('a=b+(4+(4+(2+1))))')

    def test_rule2py(self):
        # case: 2
        self.assertEqual(EvalFuncs.rule2py(['e0', 'e1'], 'a'),
                         # 'lambda a0, a1: (a0 if (e0) else a1)')
                         'lambda a0, a1: (a0 if (e0) else (a1 if e1 else EvalFuncs.raise_("a outcome conditions are all False")))')
        # case: 3
        self.assertEqual(EvalFuncs.rule2py(['e0', 'e1', 'e2'], 'a'),
                         # 'lambda a0, a1, a2: (a0 if (e0) else (a1 if (e1) else a2))')
                         'lambda a0, a1, a2: (a0 if (e0) else (a1 if (e1) else (a2 if e2 else EvalFuncs.raise_("a outcome conditions are all False"))))')
        # case: 4
        self.assertEqual(EvalFuncs.rule2py(['e0', 'e1', 'e2', 'e3'], 'a'),
                         # 'lambda a0, a1, a2, a3: (a0 if (e0) else (a1 if (e1) else (a2 if (e2) else a3)))')
                         'lambda a0, a1, a2, a3: (a0 if (e0) else (a1 if (e1) else (a2 if (e2) else (a3 if e3 else EvalFuncs.raise_("a outcome conditions are all False")))))')

    def test_to_mtt(self):
        ep = ExprParser
        self.assertEqual(ep.to_mtt('a.q + "st" + c(1,2) + (1+2)'),
                         '(_MTT(a.q) + "st" + c ( _MTT(1) , _MTT(2) ) + (_MTT(1) + _MTT(2)))')

        self.assertEqual(ep.to_mtt('a.q + "st" + c(1,2) + (1+2)+a'),
                         '(_MTT(a.q) + "st" + c ( _MTT(1) , _MTT(2) ) + (_MTT(1) + _MTT(2)) + _MTT(a))')

        self.assertEqual(ep.to_mtt(''), '')
        self.assertEqual(ep.to_mtt(r'\"a\"'), r'(\" _MTT(a) \")')     # not sure about this!
        self.assertEqual(ep.to_mtt(r'''ab( "\\path\\" )'''),
                         r'''(ab ( "\\path\\" ))''')
        self.assertEqual(ep.to_mtt('a'), '(_MTT(a))')
        self.assertEqual(ep.to_mtt('a.q(b)'), '(a.q ( _MTT(b) ))')

    def test_to_py(self):
        ep = ExprParser
        # basic
        self.assertEqual(ep.to_py('a == "str"'), '(a == "str")')
        self.assertEqual(ep.to_py('f("", "", "")'), '(f ( "" , "" , "" ))')
        self.assertEqual(ep.to_py('ff("a", "b", "c")'), '(ff ( "a" , "b" , "c" ))')
        self.assertEqual(ep.to_py('12'), '(12)')
        self.assertEqual(ep.to_py('-1-2+3'), '(-1 -2 + 3)')
        self.assertEqual(ep.to_py('"a"'), '("a")')
        self.assertEqual(ep.to_py('''ab("'a'", '"b"', "")'''), '''(ab ( "'a'" , '"b"' , "" ))''')
        # backslash quote
        self.assertEqual(ep.to_py('''ab("a""b""c")'''), '''(ab ( ("a" "b" "c") ))''')
        self.assertEqual(ep.to_py(r'''ab( "\"aa\": \"cc\"")'''),
                         r'''(ab ( "\"aa\": \"cc\"" ))''')
        self.assertEqual(ep.to_py(r'''ab("a\"a", '"b"', a+"q\""-2)'''),
                         r'''(ab ( "a\"a" , '"b"' , (a + "q\"" -2) ))''')
        self.assertEqual(ep.to_py(r'''ab( "\\path\\" )'''),
                         r'''(ab ( "\\path\\" ))''')
        # ~=
        self.assertEqual(ep.to_py('SC_DEVICE ~= "....S."'),
                         '(bool(re.search ( "....S." , SC_DEVICE )))')
        self.assertEqual(ep.to_py('SC_DEVICE ~= "....S." || A~="BC"'),
                         '(bool(re.search ( "....S." , SC_DEVICE )) or bool(re.search ( "BC" , A )))')
        self.assertEqual(ep.to_py('SC_DEVICE ~= "....S." || (A~="BC")'),
                         '(bool(re.search ( "....S." , SC_DEVICE )) or (bool(re.search ( "BC" , A ))))')
        # || and &&
        self.assertEqual(ep.to_py('A || B && C || AA && DD'),
                         '(A or B and C or AA and DD)')
        self.assertEqual(ep.to_py('A||B&&(C||(AA&&DD))'),
                         '(A or B and (C or (AA and DD)))')
        self.assertEqual(ep.to_py('1^2+(5^-2)'),
                         '(1 ** 2 + (5 ** -2))')
        self.assertEqual(ep.to_py('!True&&!False'),
                         '(not True and not False)')
        self.assertEqual(ep.to_py('!True && !False != False||!True'),
                         '(not True and not False != False or not True)')
        self.assertEqual(ep.to_py('!True && (!False)'),
                         '(not True and (not False))')

        # UserVars
        self.assertEqual(ep.to_py('_UserVars.var1 + _UserVars.var2 + ARR.var3'),
                         f'(var1 + var2 + ARR{SEP}var3)')
        self.assertEqual(ep.to_py('_UserVars.var1'), '(var1)')
        self.assertEqual(ep.to_py('(ARR.var3)'), f'((ARR{SEP}var3))')
        # scoping
        self.assertEqual(ep.to_py('(AA::ARR.var3)'), f'((AA{SEPMOD}ARR{SEP}var3))')
        self.assertEqual(ep.to_py('(__shared__::ARR.var3)'), f'((ARR{SEP}var3))')
        self.assertEqual(ep.to_py('(__shared__::AA::ARR.var3)'), f'((AA{SEPMOD}ARR{SEP}var3))')
        self.assertEqual(ep.to_py('__shared__::SCVars.SC_DEVICE ~= "A."'),
                         f'(bool(re.search ( "A." , SCVars{SEP}SC_DEVICE )))')
        # numbers
        self.assertEqual(ep.to_py('1+1mv+1V-.1mv+(1+.1V)'),
                         '(1 + (1*0.001) + (1) -(.1*0.001) + (1 + (.1)))')
        # corner case
        self.assertEqual(ep.to_py(''), '""')
        # do not convert units of a literal string
        self.assertEqual(ep.to_py('"MaaaCdrv:ringfreq:"+"2"+"GHz,MCarrPbistCCF:ring_ratio:1.9GHz"'),
                         '("MaaaCdrv:ringfreq:" + "2" + "GHz,MCarrPbistCCF:ring_ratio:1.9GHz")')
        self.assertEqual(ep.to_py('"1+1mv+1V-.1mv+(1+.1V)"'),
                         '("1+1mv+1V-.1mv+(1+.1V)")')
        self.assertEqual(ep.to_py('foo("MaaaGdrv:gtfreq:2GHz")'), '(foo ( "MaaaGdrv:gtfreq:2GHz" ))')

        # normal number
        self.assertEqual(ep.to_py('-1.9073e+05'), '(-1.9073e+05)')
        self.assertEqual(ep.to_py('-1.9073e-05'), '(-1.9073e-05)')
        self.assertEqual(ep.to_py('1.9073e+05'), '(1.9073e+05)')
        self.assertEqual(ep.to_py('1.9073e-05'), '(1.9073e-05)')
        self.assertEqual(ep.to_py('.9073e+05'), '(.9073e+05)')
        self.assertEqual(ep.to_py('.9073e-05'), '(.9073e-05)')
        # list
        self.assertEqual(ep.to_py('AA([1,2,3], ["4","5","6"])'),
                         '(AA ( ([ 1 , 2 , 3 ]) , ([ "4" , "5" , "6" ]) ))')

    def test_to_py_ternary(self):
        ep = ExprParser
        self.assertEqual(ep.to_py('1+((1==1)?(3):(5.34))'),
                         '(1 + ((3) if (1 == 1) else (5.34)))')
        self.assertEqual(ep.to_py('1+(((1==1))?((3)):((5.34)))*2'),
                         '(1 + (((3)) if ((1 == 1)) else ((5.34))) * 2)')

        # wrapped in parenthesis - normal case
        self.assertEqual(ep.to_py('1+(1==1?3:5)'),
                         '(1 + (3 if 1 == 1 else (5)))')
        self.assertEqual(ep.to_py('(1==1?3:(5))'),
                         '((3 if 1 == 1 else (5)))')

        # bare
        self.assertEqual(ep.to_py('1==1?3:(5)'),
                         '(3 if 1 == 1 else (5))')

        # skx case
        self.maxDiff = None
        self.assertEqual(ep.to_py('((bck_param)/(tester_resolution_param*2))*tester_resolution_param*2+((1==1)?(guardband_en_param*tester_guardband_param):(-1*guardband_en_param*tester_guardband_param))'),
                         '(((bck_param) / (tester_resolution_param * 2)) * tester_resolution_param * 2 + ((guardband_en_param * tester_guardband_param) if (1 == 1) else (-1 * guardband_en_param * tester_guardband_param)))')

        # two replacements
        self.assertEqual(ep.to_py('1+(1==1?3:5)+(2==2?6:7)'),
                         '(1 + (3 if 1 == 1 else (5)) + (6 if 2 == 2 else (7)))')

        # RPL case
        self.assertEqual(ep.to_py('FlowMatrix.START_FLOW =="UX"?"CRSSA_F7:ARR_REC":"CRSSA_F7:ARR"'),
                         f'("CRSSA_F7:ARR_REC" if FlowMatrix{SEP}START_FLOW == "UX" else ("CRSSA_F7:ARR"))')

        # minus
        self.assertEqual(ep.to_py('TPG_QA==-1?-1:-1'),
                         '(-1 if TPG_QA == -1 else (-1))')

        # SPR 0601 case
        expr = 'TPG_QA==1?guardband_en_param*tester_guardband_param:TPG_COLD==1?0:-1*guardband_en_param*tester_guardband_param'
        expect = '(guardband_en_param * tester_guardband_param if TPG_QA == 1 else (0 if TPG_COLD == 1 else (-1 * guardband_en_param * tester_guardband_param)))'
        self.assertEqual(ep.to_py(expr), expect)

    def test_split(self):
        ep = ExprParser
        self.assertEqual(ep.split('1ns'), ['1ns'])
        self.assertEqual(ep.split('1,2V'), ['1', '2V'])
        self.assertEqual(ep.split('a(1,2),2'), ['a(1,2)', '2'])
        self.assertEqual(ep.split('"1,2",a(1,2)+4'), ['"1,2"', 'a(1,2)+4'])
        self.assertEqual(ep.split('1;2V', char=';'), ['1', '2V'])


class TestUsrv(TestCase):

    def test_basic(self):
        with TempDir(name=True) as tdir:
            code = """
TestPlan ARR;
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
        Integer v1 = -1 + 1 - (1);
        Const Current v2 = 0.3a;
        Current v3 = 3mA;
        Double v4 = -1.1 + 1 - (1);
        Double v5 = 1mA + 1ma;
        Boolean b1 = TRUE;
        Boolean b2 = false;
        Boolean b3 = "what";
        String bstr = "yeah byp";
        Double v6 = v5 + 1.0;
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = r"""
Version 1.0;

# comment only
Shared {
UserVars BYPASSVars
{
        Integer BYPASS_in_ENGINEERING_MODE = -1;
        Current A100OHM_ICLAMPHI_VAR = 0.3A;
}
}
UserVars
{
        String AvidLiportXmlPath = "~OASIS_TPL_DIR//Mod;ules//YBS_'UP'SS//InputFiles//BGA_ULX_1.xml";
        String sp1 = "12A" ;             # space before semicolon
        String abc = " 26 " + "a;b";     # expression with semicolon
        String uu1 = _UserVars.sp1 + ";";
        String SC_PPR_LUT_CONTENT = "{\r\n  \"LutTimeStamp\": \"20210421T010203004\",\r\n  \"PreEmphasisTimeOut\": 10\r\n}";
        Voltage ccf_gb_vlc = 20mV;
        cl_qa_flag = 0;
        Time tim_gb = 200pS;
        Double CLMOFFSETCF1 = __shared__::BYPASSVars.A100OHM_ICLAMPHI_VAR;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.usrv
            expect = {'ARR.v1': -1,
                      'ARR.v2': 0.3,
                      'ARR.v3': 0.003,
                      'ARR.v4': -1.1,
                      'ARR.v5': 0.002,
                      'ARR.v6': 1.002,
                      'ARR.b1': True,
                      'ARR.b2': False,
                      'ARR.b3': True,
                      'ARR.bstr': 'yeah byp',
                      'BYPASSVars.BYPASS_in_ENGINEERING_MODE': -1,
                      'BYPASSVars.A100OHM_ICLAMPHI_VAR': 0.3,
                      'AvidLiportXmlPath': "~OASIS_TPL_DIR//Mod;ules//YBS_'UP'SS//InputFiles//BGA_ULX_1.xml",
                      'ccf_gb_vlc': 0.02,
                      'cl_qa_flag': 0,
                      'tim_gb': 2e-10,
                      'CLMOFFSETCF1': 0.3,
                      'abc': ' 26 a;b',
                      'sp1': '12A',
                      'uu1': '12A;',
                      'SC_PPR_LUT_CONTENT': '{\r\n'
                                            '  "LutTimeStamp": "20210421T010203004",\r\n'
                                            '  "PreEmphasisTimeOut": 10\r\n'
                                            '}',
                      }

            pprint(obj.get_usrv_map())
            self.assertEqual(obj.get_usrv_map(), expect)
            self.assertEqual(obj.get_var('ARR.v1', 'ARR'), -1)   # with scope
            self.assertEqual(obj.get_var('ARR::ARR.v2'), 0.3)
            self.assertEqual(obj.get_var('_UserVars.cl_qa_flag'), 0)
            self.assertEqual(obj.get_var('ARR.b1', 'ARR'), True)

            # set_var - str
            obj.set_var('ARR.bstr', '1.3', 'line#0, file:blah', testplan='ARR')          # same type
            self.assertEqual(obj.get_var('ARR.bstr', 'ARR'), '1.3')
            obj.set_var('ARR.bstr', 1.3, 'line#0, file:blah', testplan='ARR')            # float to str
            self.assertEqual(obj.get_var('ARR.bstr', 'ARR'), '1.3')
            obj.set_var('ARR.bstr', 22, 'line#0, file:blah', testplan='ARR')             # int to str
            self.assertEqual(obj.get_var('ARR.bstr', 'ARR'), '22')

            # set_var - bool
            obj.set_var('ARR.b1', False, 'bool1', testplan='ARR')          # same type
            self.assertEqual(obj.get_var('ARR.b1', 'ARR'), False)
            obj.set_var('ARR.b1', 'True || False', 'bool1', testplan='ARR')    # expr
            self.assertEqual(obj.get_var('ARR.b1', 'ARR'), True)
            obj.set_var('ARR.b1', 'False || False', 'line#0, file:blah', testplan='ARR')   # expr
            self.assertEqual(obj.get_var('ARR.b1', 'ARR'), False)
            obj.set_var('ARR.b1', 1, 'line#0, file:blah', testplan='ARR')             # int to bool
            self.assertEqual(obj.get_var('ARR.b1', 'ARR'), True)
            obj.set_var('ARR.b1', 0, 'line#0, file:blah', testplan='ARR')             # int to bool
            self.assertEqual(obj.get_var('ARR.b1', 'ARR'), False)

            # set_var - float
            obj.set_var('ARR.v2', 1.3, 'line#0, file:blah', testplan='ARR')          # same type
            self.assertEqual(obj.get_var('ARR.v2', 'ARR'), 1.3)
            obj.set_var('ARR.v2', "1.3", 'line#0, file:blah', testplan='ARR')        # simple string
            self.assertEqual(obj.get_var('ARR.v2', 'ARR'), 1.3)
            obj.set_var('ARR.v2', "1300mv+1", 'line#0, file:blah', testplan='ARR')   # eval string
            self.assertEqual(obj.get_var('ARR.v2', 'ARR'), 2.3)
            obj.set_var('ARR.v2', 2, 'line#0, file:blah', testplan='ARR')            # int to float
            self.assertTrue(isinstance(obj.get_var('ARR.v2', 'ARR'), float))

            # set_var - int
            obj.set_var('_UserVars.cl_qa_flag', 2, 'line#0, file:blah')           # same type
            self.assertEqual(obj.get_var('_UserVars.cl_qa_flag'), 2)
            obj.set_var('_UserVars.cl_qa_flag', "3.3", 'line#0, file:blah')        # simple string
            self.assertEqual(obj.get_var('_UserVars.cl_qa_flag'), 3)
            obj.set_var('_UserVars.cl_qa_flag', "1300mv+1", 'line#0, file:blah')   # eval string
            self.assertEqual(obj.get_var('_UserVars.cl_qa_flag'), 2)
            obj.set_var('cl_qa_flag', 5.1, 'line#0, file:blah')          # int to float
            self.assertTrue(isinstance(obj.get_var('cl_qa_flag'), int))
            self.assertEqual(obj.get_var('cl_qa_flag'), 5)
            self.assertEqual(obj.get_var('_UserVars.cl_qa_flag'), 5)
            obj.set_var('cl_qa_flag', '3.3', 'line#0, file:blah', as_is=True)          # int to float
            self.assertEqual(obj.get_var('cl_qa_flag'), '3.3')

            # invalid set_var
            with MockVar(obj._userv[tp.testplan_base], 'uv', []):
                with self.assertRaisesRegex(TypeError, 'set_var.*uv=.*Unknown type'):
                    obj.set_var('uv', 2, 'invalid')
                with self.assertRaisesRegex(TypeError, 'set_var.*uv=.*Unknown type'):
                    obj.set_var('uv', '2', 'invalid')

            # User specified variable
            tp1 = TestProgram(envfile, vars={'BYPASSVars.A100OHM_ICLAMPHI_VAR': -9})._ut_write_stpl()
            tp1.usrv.set_data()
            self.assertEqual(tp1.usrv.get_var('BYPASSVars.A100OHM_ICLAMPHI_VAR'), -9)
            with self.assertRaisesRegex(ErrorInput, 'uservar is not defined'):
                tp1.usrv.get_var('ARR.v_notfound')
            self.assertEqual(tp1.usrv.get_var('ARR.v_notfound', default='_nf_'), '_nf_')

            # testplan checks - global var
            obj.set_var('cl_qa_flag', '3.4', 'line#0, file:blah', testplan='NOTFOUND')     # notfound testplan
            self.assertEqual(obj.get_var('cl_qa_flag', testplan='NOTFOUND'), '3.4')
            obj.set_var('cl_qa_flag', '3.5', 'line#0, file:blah', testplan='ARR')          # found testplan but not exit
            self.assertEqual(obj.get_var('cl_qa_flag', testplan='ARR'), '3.5')
            obj.set_var('cl_qa_flag', '3.6', 'line#0, file:blah', testplan=None)           # testplan base
            self.assertEqual(obj.get_var('cl_qa_flag'), '3.6')

            # testplan check - local var, does not exist
            with self.assertRaisesRegex(ErrorInput, 'does not exist'):
                obj.set_var('ARR.v2', 0.5, 'line#0, file:blah', testplan='NOTFOUND')

            # Unknown line
            File('%s/aa.usrv' % tdir).touch('  Doubles a = 0.2')
            obj._userv = None
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown usrv line'):
                obj.set_data()

    def test_scope(self):
        with TempDir(name=True) as tdir:
            code = """
TestPlan ARR;
Import arr.usrv;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import base.usrv;
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars Space
{
        Integer v1 = 1;
        Integer v2 = 2;
}
"""
            File('%s/Modules/ARR/arr.usrv' % tdir).touch(code, mkdir=True)
            code = r"""
Version 1.0;

UserVars Space
{
        Integer v1 = 100;
        Integer v2 = 200;
}
"""
            File('%s/base.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.usrv

            # pprint(obj.get_usrv_map(flat=False))
            # expect = {None: OrderedDict([('Space.v1', 100), ('Space.v2', 200)]),
            #           'ARR': OrderedDict([('Space.v1', 1), ('Space.v2', 2)])}
            # self.assertEqual(obj.get_usrv_map(flat=False), expect)

            self.assertEqual(obj.get_var('Space.v1'), 100)
            self.assertEqual(obj.get_var('Space.v1', 'ARR'), 1)
            self.assertEqual(obj.get_var('ARR::Space.v1'), 1)

            data = OrderedDict([('ARR', 2), ('SCN', 3), (tp.testplan_base, 1)])
            self.assertEqual(list(obj._iter_testplan(data)), [tp.testplan_base, 'ARR', 'SCN'])
            self.assertEqual(list(obj._iter_testplan(data, last=True)), ['ARR', 'SCN', tp.testplan_base])
            del data[tp.testplan_base]
            self.assertEqual(list(obj._iter_testplan(data)), ['ARR', 'SCN'])
            self.assertEqual(list(obj._iter_testplan(data, last=True)), ['ARR', 'SCN'])

    def test_error_eval(self):
        with TempDir(name=True) as tdir:
            # case1: invalid eval on uservar ==========================
            code = """
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
        Integer v1 = -1 + 'a';
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            with self.assertRaisesRegex(ErrorInput, 'Failed to evaluate'):
                tp.usrv.get_usrv_map()

            # case2: invalid eval on SelectorRuleCollection ==================
            code = """
SelectorRuleCollection RulesA
{
        SelectorRule AA (Outcome1, Outcome2)
        {
                Outcome2;   # default
                Outcome1 => unknownfunc("A");
        }
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, newfile=True, mkdir=True)
            tp = TestProgram(envfile)._ut_write_stpl()
            with self.assertRaisesRegex(ErrorInput, 'Failed to evaluate SelectorRuleCollection'):
                tp.usrv.get_usrv_map()

    def test_reevaluate(self):
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
        Integer v1 = _UserVars.var + 1;
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

UserVars
{
        Double var = 1;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            expect = {'ARR.v1': 2,
                      'var': 1.0}
            self.assertEqual(tp.usrv.get_usrv_map(), expect)
            self.assertEqual(tp.usrv._userv_orig, {'DEFAULTBASE': {'ARR.v1': ('_UserVars.var + 1', 'Integer')}})

            # re-evaluate
            tp.usrv.set_var('var', 2, '')
            tp.usrv.evaluate()
            expect = {'ARR.v1': 3,
                      'var': 2}
            self.assertEqual(tp.usrv.get_usrv_map(), expect)
            self.assertEqual(tp.usrv._userv_orig, {'DEFAULTBASE': {'ARR.v1': ('_UserVars.var + 1', 'Integer')}})

    def test_rule_list(self):
        # good template
        with TempDir(name=True) as tdir:
            code = """
TestPlan ARR;
Import bb.usrv;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String v1 = "ARFF";
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

SelectorRuleCollection RulesA
{
        SelectorRule AA (Outcome1, Outcome2)
        {
                Outcome2;   # default
                Outcome1 => contains(SCVars.SC_CURRENT_PROCESS_TYPE, "PHM");
        }
}

UserVars SCVars
{
      String SC_CURRENT_PROCESS_TYPE = "CLASSHOT";
}
UserVars
{
        Array<String> bin = RulesA.AA(["1001", "1002", "1003", "1004"], ["1501", "1502", "1503", "1504"]);
}
TrialVars FlowDomain
{
    Default = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            expect = {'ARR.v1': 'ARFF',
                      'SCVars.SC_CURRENT_PROCESS_TYPE': 'CLASSHOT',
                      'bin': ['1501', '1502', '1503', '1504'],
                      'FlowDomain.Default': 0
                      }

            dd = tp.usrv.get_usrv_map()
            pprint(dd)
            self.assertEqual(dd, expect)

    def test_rule_expr_list(self):
        # good template
        with TempDir(name=True) as tdir:
            code = """
TestPlan ARR;
Import bb.usrv;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String v1 = "ARFF";
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

SelectorRuleCollection RulesA
{
        SelectorRule AA (Outcome1, Outcome2)
        {
                Outcome2;   # default
                Outcome1 => contains(SCVars.SC_CURRENT_PROCESS_TYPE, "PHM");
        }
}

UserVars SCVars
{
      String SC_CURRENT_PROCESS_TYPE = "CLASSHOT";
}
UserVars
{
        Double offset_a = 0.01;
        Double offset_b = 0.02;
        Array<String> bin = ["1501", "1502", "1503", "1504"];
        Array<String> bin2 = ["1001", "1002", "1003", "1004"];
        Array<String> bin_aggr = [bin[0], bin2[0]];
        String RulesPrefix = "b_";
        String RulesSurfix = "_s";
        Array<Double> offsets = [offset_a, offset_b];
        Array<String> UserVarExpr_String_List = "[" + RulesPrefix + bin + "]";
        Array<String> UserVarExpr_List_String = "[" + bin + RulesSurfix + "]";
        Array<String> UserVarExpr_String_List_String = "[" + RulesPrefix + bin + RulesSurfix +"]";
}
TrialVars FlowDomain
{
    Default = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            expect = {"ARR.v1": "ARFF",
                      "SCVars.SC_CURRENT_PROCESS_TYPE": "CLASSHOT",
                      "offset_a": 0.01,
                      "offset_b": 0.02,
                      "RulesPrefix": "b_",
                      "RulesSurfix": "_s",
                      "FlowDomain.Default": 0,
                      "bin": ["1501", "1502", "1503", "1504"],
                      "bin2": ["1001", "1002", "1003", "1004"],
                      "bin_aggr": ["1501", "1001"],
                      "offsets": [0.01, 0.02],
                      "UserVarExpr_String_List": ["[b_1501]", "[b_1502]", "[b_1503]", "[b_1504]"],
                      "UserVarExpr_List_String": ["[1501_s]", "[1502_s]", "[1503_s]", "[1504_s]"],
                      "UserVarExpr_String_List_String": ["[b_1501_s]", "[b_1502_s]", "[b_1503_s]", "[b_1504_s]"]
                      }

            dd = tp.usrv.get_usrv_map()
            pprint(dd)
            self.assertEqual(dd, expect)

    def test_invalid_usrv_block(self):
        # There is extra bracket found - for coverage
        with TempDir(name=True) as tdir:
            code = """
TestPlan ARR;
Import bb.usrv;
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String v1 = "ARFF";
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

Shared {
SelectorRuleCollection RulesA
{
        SelectorRule AA (Outcome1, Outcome2)
        {
                Outcome2;   # default
                Outcome1 => contains(SCVars.SC_CURRENT_PROCESS_TYPE, "PHM");
        }
}
}
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            with self.assertRaisesRegex(ErrorUser, 'but no block found'):
                tp.usrv.get_usrv_map()

    def test_rule_inside_rule(self):
        # checks tos rule inside tos rule (usage)
        # checks tos rule inside tos rule (definition)
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String v1 = "ARFF";
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

SelectorRuleCollection RulesA
{
        SelectorRule TT(Outcome1, Outcome2)
        {
                Outcome2;   # default
                Outcome1 => True;
        }
        SelectorRule FF (Outcome1, Outcome2)
        {
                Outcome1 => RulesA.TT(False, True);     # This is False
                Outcome2;   # default
        }
}

UserVars SCVars
{
      String SC_CURRENT_PROCESS_TYPE = "CLASSHOT";
}
UserVars
{
        Array<String> a_2 = RulesA.TT( RulesA.FF(1, 2), 3);        # and, mid value
        Array<String> a_13 = RulesA.TT( RulesA.TT(13, 14), 15);    # and, first value
        Array<String> a_18 = RulesA.FF( RulesA.FF(16, 17), 18);    # and, last value
        Array<String> a_5 = RulesA.FF( 4, RulesA.TT(5, 6));        # or, mid value
        Array<String> a_9 = RulesA.FF( 7, RulesA.FF(8, 9));        # or, last value
        Array<String> a_10 = RulesA.TT( 10, RulesA.FF(11, 12));    # or, first value
}
TrialVars FlowDomain
{
    Default = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            expect = {'ARR.v1': 'ARFF',
                      'SCVars.SC_CURRENT_PROCESS_TYPE': 'CLASSHOT',
                      'a_2': 2,
                      'a_13': 13,
                      'a_18': 18,
                      'a_5': 5,
                      'a_9': 9,
                      'a_10': 10,
                      'FlowDomain.Default': 0
                      }
            dd = tp.usrv.get_usrv_map()
            self.assertEqual(dd, expect)

    def test_rule_no_valid(self):
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String v1 = "ARFF";
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

SelectorRuleCollection RulesA
{
        SelectorRule TT(Outcome1, Outcome2)
        {
                Outcome1 => False;
                Outcome2 => False;
        }
}

UserVars SCVars
{
      String SC_CURRENT_PROCESS_TYPE = "CLASSHOT";
}
UserVars
{
        Array<String> aa = RulesA.TT( 1, 2);
}
TrialVars FlowDomain
{
    Default = 0;
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            expect = {'ARR.v1': 'ARFF',
                      'SCVars.SC_CURRENT_PROCESS_TYPE': 'CLASSHOT',
                      'aa': 1,
                      'FlowDomain.Default': 0
                      }
            with self.assertRaisesRegex(ErrorInput, 'RulesA.TT outcome conditions are all False'):
                dd = tp.usrv.get_usrv_map()

    def test_tos_funcs(self):
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
    String v1 = "ARFF";
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

UserVars
{
        Boolean containT = contains("baar", "aa");
        Boolean containF = contains("bar", "aa");
        Boolean containN = contains(1234, 23);
        Boolean startT = startsWith("aa", "a");
        Boolean startF = startsWith("aa", "b");
        Boolean startN = startsWith(123, 12);
        Boolean endT = endsWith("aa", "a");
        Boolean endF = endsWith("aa", "b");
        Boolean endN = endsWith(123, 23);
        Boolean orT = FALSE || TRUE;
        Boolean orF = FALSE || FALSE;
        Boolean andT = TRUE && TRUE;
        Boolean andF = FALSE && TRUE;
        Boolean reT = ARR.v1 ~= "...F";
        Boolean reF = ARR.v1 ~= "...G";
        Boolean re_a = False && ARR.v1 ~= "...F";
        Boolean re_b = ARR.v1 ~= "...F" && ARR.v1 ~= "..F." && ARR.v1 ~= "..FF";
        Boolean re_c = ARR.v1 ~= "...F" && ARR.v1 ~= "..X." && ARR.v1 ~= "..FF";
        Boolean bb1 = toBoolean(1);
        String str1 = toString(12.1);
        String str2 = toUpper("abc");
        Double dob1 = toDouble("3");
        Integer int1 = toInteger(12.7);
        Array<String> list1 = toString(toInteger(toDouble(['1.01', '2.02'])));
        Array<String> list2 = toString([1, 2.1, 3]);
        Array<Integer> list3 = toInteger(['1', '2']);
        Array<Double> list4 = toDouble(['1.1', '2.2']);
        Double dob2 = ln(2);
        Double dob3 = exp(2);
        String varenv = GetEnvironmentVariable("PATMOD1");
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch('PATMOD1 = "/somepath";')
            tp = TestProgram(envfile)._ut_write_stpl()
            expect = {'ARR.v1': 'ARFF',
                      'andF': False,
                      'andT': True,
                      'bb1': True,
                      'containF': False,
                      'containT': True,
                      'containN': True,
                      'startT': True,
                      'startF': False,
                      'startN': True,
                      'endT': True,
                      'endF': False,
                      'endN': True,
                      'orF': False,
                      'orT': True,
                      'reT': True,
                      'reF': False,
                      're_a': False,
                      're_b': True,
                      're_c': False,
                      'str1': '12.1',
                      'str2': 'ABC',
                      'dob1': 3.0,
                      'int1': 12,
                      'list1': ['1', '2'],
                      'list2': ['1', '2.1', '3'],
                      'list3': [1, 2],
                      'list4': [1.1, 2.2],
                      'dob2': 0.6931471805599453,
                      'dob3': 7.38905609893065,
                      'varenv': '/somepath',
                      }
            dd = tp.usrv.get_usrv_map()
            self.assertEqual(dd, expect)
            self.assertTrue(isinstance(dd['dob1'], float))
            self.assertTrue(isinstance(dd['int1'], int))

    def test_rule_basic(self):
        with TempDir(name=True) as tdir:
            code = """
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
SelectorRuleCollection RulesA
{
        SelectorRule AA (Outcome1, Outcome2)
        {
                Outcome2;   # default
                Outcome1 => contains("[" + LocationSets.COLD + "]", LocationSets.COLD);
        }

        SelectorRule BB (Outcome1, Outcome2, Outcome3, LA)
        {
                Outcome1 => contains("[" + LocationSets.COLD + "]", LocationSets.HOT);   # yap comment
                Outcome2 => _UserVars.UFG_PgmRules_BomGroup=="SDT_ICL_42";
                Outcome3 => _UserVars.UFG_PgmRules_BomGroup=="CLASS_RPL8161S";
                LA;
        }
}

UserVars ARR
{
    Boolean mytrue = TRUE;
    Boolean myfalse = False;
    String Var1 = RulesA.AA("abc/def", "ghi/lkm");
}
"""
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
UserVars
{
        String UFG_PgmRules_BomGroup = "CLASS_RPL8161S";
}
UserVars LocationSets
{
     Const String HOT = "6163";
     Const String COLD = "6162";
}
"""
            File('%s/aa.usrv' % tdir).touch(code, mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            obj = tp.usrv
            expect = {'LocationSets.COLD': '6162',
                      'LocationSets.HOT': '6163',
                      'UFG_PgmRules_BomGroup': 'CLASS_RPL8161S',
                      'ARR.myfalse': False,
                      'ARR.mytrue': True,
                      'ARR.Var1': 'abc/def',
                      }
            pprint(obj.get_usrv_map())
            self.assertEqual(obj.get_usrv_map(), expect)

            expect = {'RulesA.AA': [True, True],
                      'RulesA.BB': [False,
                                    False,
                                    True,
                                    True]}
            self.assertEqual(obj.get_rule_map(), expect)
            self.assertEqual(obj.get_rule_map(flat=False), {obj.testplan_base: expect})

    def test_eval_list_param(self):
        with TempDir(name=True) as tdir:
            code = """
TestPlan FUN;
"""
            File('%s/Modules/FUN/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars FlowMatrix
{
        Array<String> CORE_SSE_RATIO_7 = ["ARY1", "ARY2"];
}
UserVars ModuleA
{
    String v1 = "Moduleee";
    Array<String> firstMTTVar = ["MTTa_", "MTTb_"];
    Array<String> secondMTTVar = ["_aaa", "_bbb"];
}
"""
            File('%s/bb.usrv' % tdir).touch(code, mkdir=True)
            code = """
Import bb.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()

            dd = tp.usrv.eval_param('(_MTT (ModuleA_ZQ_firstMTTVar) + "Prefix_TrialString_" + ["111", "222"] + _MTT (ModuleA_ZQ_secondMTTVar) + "_end")', tp.testplan_base, 'a')
            print(dd)
            self.assertEqual(dd, ["MTTa_Prefix_TrialString_111_aaa_end", "MTTa_Prefix_TrialString_222_aaa_end"])

            dd = tp.usrv.eval_param('"Prefix_TrialString_" + ["111", "222"]', tp.testplan_base, 'a')
            print(dd)
            self.assertEqual(dd, ["Prefix_TrialString_111", "Prefix_TrialString_222"])

            dd = tp.usrv.eval_param('["111", "222"] + "_Surfix_TrialString"', tp.testplan_base, 'a')
            print(dd)
            self.assertEqual(dd, ["111_Surfix_TrialString", "222_Surfix_TrialString"])

            dd = tp.usrv.eval_param('"Prefix_TrialString_" + ["111", "222"] + "_Surfix_TrialString"', tp.testplan_base, 'a')
            print(dd)
            self.assertEqual(dd, ["Prefix_TrialString_111_Surfix_TrialString",
                                  "Prefix_TrialString_222_Surfix_TrialString"])
            # List + List
            dd = tp.usrv.eval_param('["aaa", "bbb"] + "Prefix_TrialString_" + ["111", "222"] + "_end"', tp.testplan_base, 'a')
            pprint(dd)
            self.assertEqual(dd, ["aaaPrefix_TrialString_111_end",
                                  "bbbPrefix_TrialString_222_end"])
            # real expression list + list
            dd = tp.usrv.eval_param('"RST:IA:8,FBP:IA_DBA:"+FlowMatrix.CORE_SSE_RATIO_7+",TTR:FUNMLC:"+["W50","W120"]+",RST:DDR:"+",RST:CFC_CDIE:8,SBFT_DCF:RATIO:2"', tp.testplan_base, 'a')
            pprint(dd)
            self.assertEqual(dd, ["RST:IA:8,FBP:IA_DBA:ARY1,TTR:FUNMLC:W50,RST:DDR:,RST:CFC_CDIE:8,SBFT_DCF:RATIO:2",
                                  "RST:IA:8,FBP:IA_DBA:ARY2,TTR:FUNMLC:W120,RST:DDR:,RST:CFC_CDIE:8,SBFT_DCF:RATIO:2"])

            # extra parentheses
            dd = tp.usrv.eval_param('("RST:IA:8,FBP:IA_DBA:"+FlowMatrix.CORE_SSE_RATIO_7)', tp.testplan_base, 'a')
            pprint(dd)
            self.assertEqual(dd, ["RST:IA:8,FBP:IA_DBA:ARY1",
                                  "RST:IA:8,FBP:IA_DBA:ARY2"])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_realtp_eval_param(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        obj = tp.usrv
        self.assertEqual(len(obj.get_usrv_map()), 1299)
        self.assertEqual(len(obj.get_rule_map()), 0)

        # eval_param
        self.assertEqual(obj.eval_param('SCVars.SC_CURRENT_PROCESS_STEP', 'BASE', 'a'), 'CLASSHOT')
        self.assertAlmostEqual(obj.eval_param('LevelVars.A100OHM_ICLAMPHI_VAR + 1.1A', 'BASE', 'b'), 1.4)
        self.assertAlmostEqual(obj.eval_param('', 'BASE', 'b'), '')

        # error case
        with self.assertRaisesRegex(ErrorInput, 'Failed to evaluate'):
            obj.eval_param('1 1', 'BASE', 'c')
        with self.assertRaisesRegex(ErrorInput, 'Failed to evaluate'):
            obj.eval_param('1 1', 'BASE', 'c', is_print=False)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_realtp_torch(self):
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        self.assertEqual(len(tp.usrv.get_usrv_map()), 1325)
        self.assertEqual(len(tp.usrv.get_rule_map()), 734)


class TestScoped(TestCase):

    @with_(TempDir, chdir=True)
    @with_(MockVar, cfg, 'pickle_dir', '.')
    def test_pickle(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env').pickle_init()
        self.assertEqual(tp.usrv.get_var('BYPASSVars.bype'), 'ok_orig')
        self.assertEqual(len(list(keys_atlevel(tp.usrv._src_eval, 2))), 3)

    def test_initial(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env', vars={'BYPASSVars.bype': '"nn_orig"'})
        tp.usrv.set_data()
        self.assertEqual(tp.usrv.get_var('BYPASSVars.bype'), 'nn_orig')
        self.assertEqual(tp.usrv.get_var('ARR::BYPASSVars.bype'), 'okARR_arraybyp')
        self.assertEqual(tp.usrv.get_var('PTH::BYPASSVars.bype'), 'okPTH_pthbyp')

    @with_(MockVar, timlvl, 'SEP', '__')
    @with_(MockVar, timlvl, 'SEPMOD', '___')
    def test_scopes(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')
        tp.usrv.set_data()

        # read
        # global
        self.assertEqual(tp.usrv.get_var('ARR::BYPASSVars.bype'), 'okARR_arraybyp')
        self.assertEqual(tp.usrv.get_var('BYPASSVars.bype'), 'ok_orig')
        # scoped
        self.assertEqual(tp.usrv.get_var('BYPASSVars.bype', testplan='ARR'), 'okARR_arraybyp')
        self.assertEqual(tp.usrv.get_var('ARR::BYPASSVars.bype', testplan='ARR'), 'okARR_arraybyp')
        self.assertEqual(tp.usrv.get_var('PTH::BYPASSVars.bype', testplan='ARR'), 'okPTH_pthbyp')
        self.assertEqual(tp.usrv.get_var('BASE::BYPASSVars.bype', testplan='ARR'), 'ok_orig')
        self.assertEqual(tp.usrv.get_var(f'BASE___BYPASSVars.bype', testplan='ARR'), 'ok_orig')

        # write - local scope
        tp.usrv.set_var('ARR::BYPASSVars.bype', 'newval1', 'ut')
        self.assertEqual(tp.usrv.get_var('BYPASSVars.bype'), 'ok_orig')
        self.assertEqual(tp.usrv.get_var('ARR::BYPASSVars.bype'), 'newval1')
        self.assertEqual(tp.usrv.get_var('PTH::BYPASSVars.bype'), 'okPTH_pthbyp')
        with CaptureStdoutLog() as p:
            pprint({x: y for x, y in tp.usrv.uflat.items() if x != '__builtins__'})
            pprint(tp.usrv.ulocal)
        expect = '''
{'ARR___BYPASSVars__bype': 'newval1',
 'ARR___BYPASSVars__bypvar': 'arraybyp',
 'ARR___BYPASSVars__var2': 2,
 'BASE___BYPASSVars__BYPASS_in_ENGINEERING_MODE': -1,
 'BASE___BYPASSVars__bype': 'ok_orig',
 'BASE___BYPASSVars__bypvar': 'orig',
 'BASE___RunTimeLibraryVars__iCGL_TpAltName': 'Simple6',
 'BASE___SCVars__SC_DEVICE': '4TXNCV',
 'BASE___ccf_gb_vlc': 0.02,
 'BASE___cl_qa_flag': 1,
 'BASE___hc_vcc_gb': 1,
 'BYPASSVars__BYPASS_in_ENGINEERING_MODE': -1,
 'BYPASSVars__bype': 'ok_orig',
 'BYPASSVars__bypvar': 'orig',
 'BYPASSVars__var2': 2,
 'PTH___BYPASSVars__bype': 'okPTH_pthbyp',
 'PTH___BYPASSVars__bypvar': 'pthbyp',
 'RunTimeLibraryVars__iCGL_TpAltName': 'Simple6',
 'SCVars__SC_DEVICE': '4TXNCV',
 'ccf_gb_vlc': 0.02,
 'cl_qa_flag': 1,
 'hc_vcc_gb': 1}
{'ARR': {'BYPASSVars__bype': 'newval1',
         'BYPASSVars__bypvar': 'arraybyp',
         'BYPASSVars__var2': 2},
 'BASE': {'BYPASSVars__BYPASS_in_ENGINEERING_MODE': -1,
          'BYPASSVars__bype': 'ok_orig',
          'BYPASSVars__bypvar': 'orig',
          'RunTimeLibraryVars__iCGL_TpAltName': 'Simple6',
          'SCVars__SC_DEVICE': '4TXNCV',
          'ccf_gb_vlc': 0.02,
          'cl_qa_flag': 1,
          'hc_vcc_gb': 1},
 'PTH': {'BYPASSVars__bype': 'okPTH_pthbyp', 'BYPASSVars__bypvar': 'pthbyp'}}
'''
        self.assertTextEqual(p.getvalue(), expect)

        # write - global scope
        print("Case: global scope =======================")
        tp.usrv.set_var('BYPASSVars.bype', '11_orig', 'ut')
        self.assertEqual(tp.usrv.get_var('BYPASSVars.bype'), '11_orig')
        self.assertEqual(tp.usrv.get_var('ARR::BYPASSVars.bype'), 'newval1')
        self.assertEqual(tp.usrv.get_var('PTH::BYPASSVars.bype'), 'okPTH_pthbyp')
        with CaptureStdoutLog() as p:
            pprint({x: y for x, y in tp.usrv.uflat.items() if x != '__builtins__'})
            pprint(tp.usrv.ulocal)
        self.assertTextEqual(p.getvalue(), expect.replace('ok_orig', '11_orig'))


class TestSharedUsrv(TestCase):
    """This class is also run in test_tp_audit.py"""

    @with_(MockVar, OPT, 'vars', {})
    def test_usrv(self):
        with MockVar(OPT, 'all', [f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env']):
            with CaptureStdoutLog() as p:
                TPInfo.do_usrv()
            res = [x for x in p.getvalue().split('\n') if 'Elapsed:' not in x]    # remove Elapsed line
            expect = '''
-d- usrv [BASE] BYPASSVars.BYPASS_in_ENGINEERING_MODE = -1
-d- usrv [BASE] BYPASSVars.bype = ok_orig
-d- usrv [BASE] BYPASSVars.bypvar = orig
-d- usrv [BASE] RunTimeLibraryVars.iCGL_TpAltName = Simple6
-d- usrv [BASE] SCVars.SC_DEVICE = 4TXNCV
-d- usrv [BASE] ccf_gb_vlc = 0.02
-d- usrv [BASE] cl_qa_flag = 1
-d- usrv [BASE] hc_vcc_gb = 1
-d- usrv [ARR] BYPASSVars.bype = okARR_arraybyp
-d- usrv [ARR] BYPASSVars.bypvar = arraybyp
-d- usrv [ARR] BYPASSVars.var2 = 2
-d- usrv [PTH] BYPASSVars.bype = okPTH_pthbyp
-d- usrv [PTH] BYPASSVars.bypvar = pthbyp
-d- rule [BASE] BootUp.IfBom1 = [True, False]
-d- rule [ARR] BootUp.IfBom1 = [True, False, False]
-d- rule [PTH] BootUp.IfBom1 = [True, False, False, True]
'''
            self.assertTextEqual('\n'.join(res), expect)


class Val(TestCase):

    def compare(self):
        """Validation routine to compare uflat vs ulocal. They should be the same"""
        validation_tp = '/intel/tpvalidation/hdmxprogs/mtl/MTLXXXXXXX17D0USXXX/POR_TP/Class_MTL_P68/EnvironmentFile.env'

        tpobj = TestProgram(validation_tp).init()
        obj = tpobj.usrv
        del obj.uflat['__builtins__']
        for testplan in obj._iter_testplan(obj.ulocal, last=True):
            for varnd, val in obj.ulocal[testplan].items():
                # non-scoped variable
                target = varnd
                if target not in obj.uflat:
                    print(f'{testplan} {target} is not found in self.uflat')
                    continue
                if val != obj.uflat[target]:
                    print(f'{testplan} {target} has different value')
                    continue

                # scoped variable
                target = f'{testplan}___{varnd}'
                if target not in obj.uflat:
                    print(f'{testplan} {target} is not found in self.uflat')
                    continue
                if val != obj.uflat[target]:
                    print(f'{testplan} {target} has different value')
                    continue

    def test_update_usrv(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        with TempDir(name=True, chdir=True) as tdir:
            # Test Case 1, update uservar non-empty default value to desired value.
            usrv_path = 'Shared/BaseInputs/UservarDefinitions.usrv'
            usrv_name = 'DIELET_INDICATOR'
            usrv_value = 'CPU,GCD,HUB,PCD'
            original_cont = '''
    String XDIELET_INDICATORY = "CPU";
    String DIELET_INDICATOR = "CPU";     # blah
    String DIELET_INDICATOR1 = "CPU";
    String XDIELET_INDICATOR = "CPU";
    String    DIELET_INDICATOR="";
    String blah = "something";
'''
            expected_cont = '''
    String XDIELET_INDICATORY = "CPU";
    String DIELET_INDICATOR = "CPU,GCD,HUB,PCD";     # blah
    String DIELET_INDICATOR1 = "CPU";
    String XDIELET_INDICATOR = "CPU";
    String DIELET_INDICATOR = "CPU,GCD,HUB,PCD";
    String blah = "something";
'''
            File(usrv_path).touch(original_cont, mkdir=True)
            obj = Usrv(tp)
            obj.update_usrv(usrv_path, usrv_name, usrv_value)
            self.assertTextEqual(File(usrv_path).read(), expected_cont)

            # Test Case 2, update uservar with empty default value to desired value.
            usrv_path_1 = 'Shared/BaseInputs/UservarDefinitions1.usrv'
            usrv_value_1 = 'CPU,GCD'
            original_cont_1 = '''
    Const String DIELET_INDICATOR = "";
    Const String blah = "something";
            '''
            expected_cont_1 = '''
    Const String DIELET_INDICATOR = "CPU,GCD";
    Const String blah = "something";
            '''
            File(usrv_path_1).touch(original_cont_1, mkdir=True)
            obj = Usrv(tp)
            obj.update_usrv(usrv_path_1, usrv_name, usrv_value_1)
            self.assertTextEqual(File(usrv_path_1).read(), expected_cont_1)

            self.assertEqual(obj.update_usrv(usrv_path_1, usrv_name, None), 1)

    def test_derive_val_folder_name(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        obj = Usrv(tp)

        # Test Case 1, return V: drive folder name.
        tpname1 = 'NVLS356A0H01B00S528'
        isval1 = True
        ispart1 = False
        result1 = obj.derive_val_folder_name(tpname1, isval1, ispart1)
        expect1 = 'NVLXXXXXXX01B00SXXX'
        self.assertTextEqual(result1, expect1)

        # Test Case 3, return partial TP V: drive folder name.
        tpname3 = 'NVLS356A0H01B00HG28'
        isval3 = False
        ispart3 = True
        result3 = obj.derive_val_folder_name(tpname3, isval3, ispart3)
        expect3 = 'NVLXXXXXXX01B00HGXX'
        self.assertTextEqual(result3, expect3)

        # Test Case 2, return I: drive folder name.
        tpname2 = 'NVLS356A0H01B00S528'
        isval2 = False
        ispart2 = False
        result2 = obj.derive_val_folder_name(tpname2, isval2, ispart2)
        expect2 = 'NVLXXXXA0H01B00S528'
        self.assertTextEqual(result2, expect2)

        # None case
        self.assertEqual(obj.derive_val_folder_name(None, isval2, ispart2), None)


class TestTOSVar(TestCase):
    def test_init(self):
        # list type
        var = TOSVar(['a', 'b'])
        self.assertEqual(var.mytype, 'L')
        self.assertEqual(var.value, ['a', 'b'])
        # string type
        var = TOSVar('abc')
        self.assertEqual(var.mytype, 'S')
        self.assertEqual(var.value, 'abc')
        # float type
        var = TOSVar(1.23)
        self.assertEqual(var.mytype, 'F')
        self.assertEqual(var.value, 1.23)
        # TOSVar inside
        orig = TOSVar('abc')
        var = TOSVar(orig)
        self.assertEqual(var.mytype, 'S')
        self.assertEqual(var.value, 'abc')
        # invalid type
        with self.assertRaises(TypeError):
                TOSVar({"a": "A"})  # dict is not supported

    def test_addition(self):
        # str + str
        var1 = TOSVar('foo')
        var2 = TOSVar('bar')
        var3 = var1 + var2
        self.assertIsInstance(var3, TOSVar)
        self.assertEqual(var3.value, 'foobar')

        # str + float
        var1 = TOSVar('foo')
        var2 = TOSVar(1.5)
        var3 = var1 + var2
        self.assertEqual(var3.value, 'foo1.5')

        # str + list
        var1 = TOSVar('foo')
        var2 = TOSVar(['a', 'b'])
        var3 = var1 + var2
        self.assertEqual(var3.value, ['fooa', 'foob'])

        # list + str
        var1 = TOSVar(['a', 'b'])
        var2 = TOSVar('foo')
        var3 = var1 + var2
        self.assertEqual(var3.value, ['afoo', 'bfoo'])

        # list + float
        var1 = TOSVar(['a', 'b'])
        var2 = TOSVar(2.5)
        var3 = var1 + var2
        self.assertEqual(var3.value, ['a2.5', 'b2.5'])

        # list + list, raise expection
        var1 = TOSVar(['a', 'b'])
        var2 = TOSVar(['x', 'y'])
        var3 = var1 + var2
        self.assertEqual(var3.value, ['ax', 'by'])

        # list + list with unequal length, raise expection
        var1 = TOSVar(['a', 'b', 'c'])
        var2 = TOSVar(['x', 'y'])
        with self.assertRaises(TypeError):
                _ = var1 + var2

        # wrong mytype
        var1 = TOSVar('foo')
        var2 = TOSVar('bar')
        var2.mytype = "X"  # force wrong type
        with self.assertRaises(TypeError):
                _ = var1 + var2

        var1 = TOSVar(['a', 'b'])
        var2 = TOSVar(['x', 'y'])
        var2.mytype = "X"  # force wrong type
        with self.assertRaises(TypeError):
                _ = var1 + var2

    # UT setup for _wrap_tosvar
    def setUp(self):
        class MockTpObj:
            testplan_base = 'BASE'
        self.usrv = Usrv(MockTpObj())

    def test_wrap_tosvar(self):
        # basic
        expr = 'a + b + c'
        result = self.usrv._wrap_tosvar(expr)
        self.assertEqual(result, 'TOSVar(a) + TOSVar(b) + TOSVar(c)')

        # with parentheses
        expr = '(a + b + c)'
        result = self.usrv._wrap_tosvar(expr)
        self.assertEqual(result, 'TOSVar(a) + TOSVar(b) + TOSVar(c)')

        # single variable
        expr = 'foo'
        result = self.usrv._wrap_tosvar(expr)
        self.assertEqual(result, 'TOSVar(foo)')

        # single variable with parentheses
        expr = '(foo)'
        result = self.usrv._wrap_tosvar(expr)
        self.assertEqual(result, 'TOSVar(foo)')

        # spaces injected
        expr = '  x  +  y '
        result = self.usrv._wrap_tosvar(expr)
        self.assertEqual(result, 'TOSVar(x) + TOSVar(y)')

        # parentheses and spaces
        expr = ' ( a + b ) '
        result = self.usrv._wrap_tosvar(expr)
        self.assertEqual(result, 'TOSVar(a) + TOSVar(b)')

        # expression with numbers
        expr = '1 + 2 + var'
        result = self.usrv._wrap_tosvar(expr)
        self.assertEqual(result, 'TOSVar(1) + TOSVar(2) + TOSVar(var)')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
