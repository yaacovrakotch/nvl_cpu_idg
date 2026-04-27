#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tp_plans.py
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.tputil import trimut
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.errors import ErrorInput
from main.tp_plans import *
from mod.test.test_plans import TestTPAuditPlan    # Do not remove, needed for coverage
from os.path import join
import sys


class TestTp(TestCase):

    def test_basic_json1(self):
        Plan.clear()
        TP.set_tp(None)
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'

        with TempDir(name=True) as tdir:
            cmd = f'tp_plans.py -tp {tp} {UT_DIR_REPO}/plans/fun_de_14Pd.json -out {tdir}/out.csv'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()
            self.assertEqual(len(File(f'{tdir}/out.csv').raw()), 26)

    def test_basic_json2(self):
        # with multiple_match
        Plan.clear()
        TP.set_tp(None)
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'

        with TempDir(name=True) as tdir:
            cmd = f'tp_plans.py -tp {tp} {UT_DIR_REPO}/plans/fun_de_14Pc.json -out {tdir}/out.csv -flows MAIN'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()
            expect = '''
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR,ARR,0,2,1,2,0,1,1,1
SummaryTotal,,,0,2,1,2,0,1,1,1
WeightedPct,,,,0.0%,,0.0%,,0.0%,,0.0%

HeadMod,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect,IP
ModSummary,ARR,ARR,0,2,1,2,0,1,1,1,ARR

HeadFound,Module,Team,tid_count,tid_expect,PorEn,POR_plan,TestName
FoundPlan,ARR,ARR,1,2,En,,CCB

HeadMissMod,Module,Team,tid_count,X,TestInsCount
MissingModule,SCN,SCN,6,,2
'''
            self.assertPartialText(File(f'{tdir}/out.csv').read(), expect)

    def test_basic_invalid(self):
        TP.set_tp(None)
        # invalid input env arguments
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        cmd = f'tp_plans.py -tp {tp}'.split()
        with MockVar(sys, "argv", cmd):
            with self.assertRaises(SystemExit):
                TPPlans().main()

        with TempDir(name=True) as tdir:
            File(f'{tdir}/a.xls').touch()
            cmd = f'tp_plans.py -tp {tp} {tdir}/a.xls'.split()
            with MockVar(sys, "argv", cmd):
                with self.assertRaisesRegex(ErrorUser, 'Unknown input file type'):
                    TPPlans().main()

    def test_ctp2_csv(self):
        Plan.clear()
        TP.set_tp(None)
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'

        with TempDir(name=True) as tdir:
            cmd = f'tp_plans.py -tp {tp} {UT_DIR_REPO}/plans/fun_de_14Pa.py -ctp2 {tdir}/out.csv'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()
            expect = '''name,id_lno,module,content_expect,multiple_match,voltage
CHK*F1,18,FUN_DE,613,1,
CHK*F3,22,FUN_DE,500,1,
CHK*F4,5,FUN_DE,600,1,
CHKX,21,FUN_DE,500,1,
DEFUNC_DE_FUNC_E_BEGIN_X_X_CD312_CTRL_BABY,25,FUN_DE,100,1,
DEFUNC_X_SCREEN_K_SRHSACDF1_F1_X_X_X_FORK_DE0,15,FUN_DE,,1,
VMIN*CHK*F1,12,FUN_DE,700,1,"p_vccddq_spec={CR_LFM_VMIN_RAIN_KILL},{VX1}"
'''
            self.assertTextEqual(File(f'{tdir}/out.csv').read(), expect)

    def test_csv(self):
        with TempDir(name=True) as tdir:
            cfile = join(tdir, 'a.csv')
            File(cfile).touch('''
HeadSummary,Module,Team,C_POR_Actual,C_POR_Expect,C_En_Actual,C_En_Expect,F_POR_Actual,F_POR_Expect,F_En_Actual,F_En_Expect
Summary,ARR_GT_GXX,ARR,3,548,431,548,3,31,24,31
Summary,CLK_MAIN_GXX,CLK,0,0,0,0,0,4,4,4
Summary,FUN_GT_GMD,FUN,15,92,92,92,0,9,2,9
Summary,MIO_FBIST_GXX,MIO,0,24,24,24,0,3,3,3
Summary,PTH_BGCEP_GXX,PTH,0,0,0,0,0,5,4,5

HeadMissingPlan,Module,Team,corner,tid_count,Detail
MissingFromPlan,ARR_GT_GXX,ARR,nom,39,LSA_ALL_GFXSB_K_END_TITO_X_VMAX_X_F1_KS_P1
MissingFromPlan,ARR_GT_GXX,ARR,nom,85,RAM_ALL_GFXSB_K_END_TITO_X_VMAX_X_F1_KS_P0
''')
            cmd = f'tp_plans.py {cfile} -csv'.split()
            with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
                TPPlans().main()
        expect = """
HeadSummary Module        Team C_POR_Actual C_POR_Expect C_En_Actual C_En_Expect F_POR_Actual F_POR_Expect F_En_Actual F_En_Expect
Summary     ARR_GT_GXX    ARR  3            548          431         548         3            31           24          31
Summary     CLK_MAIN_GXX  CLK  0            0            0           0           0            4            4           4
Summary     FUN_GT_GMD    FUN  15           92           92          92          0            9            2           9
Summary     MIO_FBIST_GXX MIO  0            24           24          24          0            3            3           3
Summary     PTH_BGCEP_GXX PTH  0            0            0           0           0            5            4           5

HeadMissingPlan Module     Team corner tid_count Detail
MissingFromPlan ARR_GT_GXX ARR  nom    39        LSA_ALL_GFXSB_K_END_TITO_X_VMAX_X_F1_KS_P1
MissingFromPlan ARR_GT_GXX ARR  nom    85        RAM_ALL_GFXSB_K_END_TITO_X_VMAX_X_F1_KS_P0

"""
        self.assertTextEqual(p.getvalue(), expect)

    def test_glob_github(self):
        with TempDir(name=True, chdir=True):
            File('a.csv').touch()
            File('b.csv').touch()
            cmd = f'tp_plans.py *.csv -csv'.split()
            with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
                with MockVar(TPPlans, 'do_csv', Mock()):
                    TPPlans().main()
                self.assertEqual(sorted(OPT.all), ['a.csv', 'b.csv'])

    def test_check(self):
        # Pass case #1
        Plan.clear()
        cmd = f'tp_plans.py -check'
        modfiles = [f'./fun_de_14Pa.json', 'ProductConfig/123.json']
        with MockVar(sys, "argv", cmd.split()), \
                Chdir(f'{UT_DIR_REPO}/plans'), \
                CaptureStdoutLog() as p,\
                MockVar(GitHub, 'get_modfiles', Mock(return_value=modfiles)):
            # with self.assertRaisesRegex(AssertionError, 'not found in any TestCondition'):
            TPPlans().main()

        result = [x for x in p.getvalue().split('\n') if 'Check json syntax' in x]
        self.assertEqual(len(result), 2)
        result = [x for x in p.getvalue().split('\n') if '-i- found' in x]
        self.assertEqual(len(result), 7)
        result = [x for x in p.getvalue().split('\n') if 'CHECKING:' in x]
        self.assertEqual(len(result), 1)

        # Pass case
        Plan.clear()
        cmd = f'tp_plans.py -check'
        modfiles = [f'./fun_de_14Pa.json', './fun_de_14b.json']
        with MockVar(sys, "argv", cmd.split()), \
                Chdir(f'{UT_DIR_REPO}/plans/pass_case'), \
                CaptureStdoutLog() as p,\
                MockVar(GitHub, 'get_modfiles', Mock(return_value=modfiles)):
            TPPlans().main()
        result = [x for x in p.getvalue().split('\n') if 'Check json syntax' in x]
        self.assertEqual(len(result), 2)
        result = [x for x in p.getvalue().split('\n') if '-i- found' in x]
        self.assertEqual(len(result), 9)
        result = [x for x in p.getvalue().split('\n') if 'CHECKING:' in x]
        self.assertEqual(len(result), 2)

    def test_check_nothing(self):
        Plan.clear()
        with TempDir(name=True, chdir=True) as tdir:
            cmd = f'tp_plans.py -check'
            File('ProductConfig/123.json').touch(File(f'{UT_DIR_REPO}/plans/fun_de_14Pa.json').read(), mkdir=True)
            modfiles = [f'{UT_DIR_REPO}/plans/fun_de_14Pa.xls']
            with MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p,\
                    MockVar(GitHub, 'get_modfiles', Mock(return_value=modfiles)):
                TPPlans().main()
            print(p.getvalue())
            self.assertTrue('Nothing to check' in p.getvalue())


class TestPipe(TestCase):

    @with_(MockVar, TPPlans, 'pr_comment', Mock())
    @with_(MockVar, TPPlans, 'do_tp', Mock())
    @with_(MockVar, GitHub, 'get_prno', Mock(return_value='21'))
    @with_(MockVar, GitHub, 'get_labels', Mock(return_value={'ok'}))
    def test_frompr(self):
        # Does not test pr_comment
        # using _PRNO_ in -tp and -out is a folder
        with TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/21/file.env').touch(mkdir=True)
            File('Modules/ARR/ctp.txt').touch('a.xlsx', mkdir=True)
            File('Modules/TPI/TPI_BASE/ctp.txt').touch('b.xls', mkdir=True)
            File('Modules/TPI/TPI_OTHER/ctp.txt').touch('c.json', mkdir=True)
            File('ctp-mtl/a.json').touch(mkdir=True)
            File('ctp-mtl/b.json').touch()
            File('ctp-mtl/c.json').touch()
            cmd = f'tp_plans.py {tdir} -tp {tdir}/POR_TP/_PRNO_/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()

            self.assertEqual(OPT.all, ['a.json', 'b.json', 'c.json'])
            self.assertEqual(OPT.tp, f'{tdir}/POR_TP/21/file.env')
            self.assertEqual(OPT.out, 'ctp-mtl/21.csv')

        # Simple case
        with TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/aa/file.env').touch(mkdir=True)
            File('Modules/ARR/ctp.txt').touch('a.xlsx', mkdir=True)
            File('Modules/TPI/TPI_BASE/ctp.txt').touch('b.xls', mkdir=True)
            File('Modules/TPI/TPI_OTHER/ctp.txt').touch('c.json', mkdir=True)
            File('ctp-mtl/a.json').touch(mkdir=True)
            File('ctp-mtl/b.json').touch()
            File('ctp-mtl/c.json').touch()
            cmd = f'tp_plans.py {tdir} -tp {tdir}/POR_TP/aa/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()

            self.assertEqual(OPT.all, ['a.json', 'b.json', 'c.json'])
            self.assertEqual(OPT.tp, f'{tdir}/POR_TP/aa/file.env')
            self.assertEqual(OPT.out, 'ctp-mtl/21.csv')

        # Simple case
        with MockVar(GitHub, 'get_prno', Mock(return_value='')), \
                TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/aa/file.env').touch(mkdir=True)
            File('Modules/ARR/ctp.txt').touch('a.xlsx', mkdir=True)
            File('Modules/TPI/TPI_BASE/ctp.txt').touch('b.xls', mkdir=True)
            File('Modules/TPI/TPI_OTHER/ctp.txt').touch('c.json', mkdir=True)
            File('ctp-mtl/a.json').touch(mkdir=True)
            File('ctp-mtl/b.json').touch()
            File('ctp-mtl/c.json').touch()
            cmd = f'tp_plans.py {tdir} -tp {tdir}/POR_TP/aa/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()

            self.assertEqual(OPT.all, ['a.json', 'b.json', 'c.json'])
            self.assertEqual(OPT.tp, f'{tdir}/POR_TP/aa/file.env')
            self.assertEqual(OPT.out, 'ctp-mtl/0.csv')

    def test_frompr_fail(self):
        # -frompr fail label

        def fake(*args):
            raise ErrorUser('blah', 'suggestion')

        # fail case - no special label
        with TempDir(name=True, chdir=True) as tdir:
            File('file.env').touch()
            File('ctp-mtl/a.txt').touch(mkdir=True)
            cmd = f'tp_plans.py {tdir} -tp POR_TP/_PRNO_/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd), \
                    MockVar(GitHub, 'get_labels', Mock(return_value={'ok'})), \
                    MockVar(TPPlans, '_frompr', fake):
                with self.assertRaisesRegex(ErrorUser, 'blah'):
                    TPPlans().main()

        # pass case - with special label
        with TempDir(name=True, chdir=True) as tdir:
            File('file.env').touch()
            File('ctp-mtl/a.txt').touch(mkdir=True)
            cmd = f'tp_plans.py {tdir} -tp POR_TP/_PRNO_/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd), \
                    MockVar(GitHub, 'get_labels', Mock(return_value={'CTP_Fail_Ignore'})), \
                    MockVar(TPPlans, '_frompr', fake), \
                    CaptureStdoutLog() as p:
                TPPlans().main()

            expect = '''
-i- labels: CTP_Fail_Ignore
-i- CTP Failed with error:    <<< Error Type
Error:      blah
Suggestion: suggestion
Rundir:     rundir_tbd
'''
            result = [x for x in p.getvalue().split('\n') if not x.startswith(('ErrorSig', '===='))]
            self.assertTextEqual('\n'.join(result), expect)

    @with_(MockVar, TPPlans, 'do_tp', Mock())
    @with_(MockVar, GitHub, 'get_prno', Mock(return_value='21'))
    @with_(MockVar, GetCmd, 'exe', Mock(return_value='ls'))
    def test_pr_comment(self):
        res = ['_ORIG_']

        def fake_prtext(_, arg):
            res[0] = arg
            return arg

        with TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/aa/file.env').touch(mkdir=True)
            File('Modules/ARR/ctp.txt').touch('a.xlsx', mkdir=True)
            File('Modules/TPI/TPI_BASE/ctp.txt').touch('b.xls', mkdir=True)
            File('Modules/TPI/TPI_OTHER/ctp.txt').touch('c.json', mkdir=True)
            File('ctp-mtl/a.json').touch(mkdir=True)
            File('ctp-mtl/b.json').touch()
            File('ctp-mtl/c.json').touch()
            cmd = f'tp_plans.py {tdir} -tp {tdir}/POR_TP/aa/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd), \
                    MockVar(GitHub, 'get_modfiles', Mock(return_value=['Modules/ARR/a.mtpl', 'Shared/x/a.usrv'])), \
                    MockVar(TPPlans, '_prtext', fake_prtext):
                TPPlans().main()

            self.assertEqual(res[0], '-i- pipeline: a.json\n')
            self.assertEqual(OPT.all, ['a.json'])
            self.assertEqual(OPT.tp, f'{tdir}/POR_TP/aa/file.env')
            self.assertEqual(OPT.out, None)   # must be no output

            # No modules
            res = ['_ORIG_']
            cmd = f'tp_plans.py {tdir} -tp {tdir}/POR_TP/aa/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd), \
                    MockVar(GitHub, 'get_modfiles', Mock(return_value=['Shared/BaseInputs/a.something'])), \
                    MockVar(TPPlans, '_prtext', fake_prtext):
                TPPlans().main()

            self.assertEqual(res[0], '_ORIG_')      # No output
            self.assertEqual(OPT.all, ['ctp-mtl'])
            self.assertEqual(OPT.tp, f'{tdir}/POR_TP/aa/file.env')
            self.assertEqual(OPT.out, None)   # must be no output

        # no found ctp file
        with TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/aa/file.env').touch(mkdir=True)
            File('ctp-mtl/a.txt').touch(mkdir=True)
            res = ['_ORIG_']
            cmd = f'tp_plans.py {tdir} -tp {tdir}/POR_TP/aa/file.env -frompr -out ctp-mtl'.split()
            with MockVar(sys, "argv", cmd), \
                    MockVar(GitHub, 'get_modfiles', Mock(return_value=['Modules/ARR/a.mtpl'])), \
                    MockVar(TPPlans, 'do_pipeline', Mock()), \
                    MockVar(TPPlans, '_prtext', fake_prtext):
                TPPlans().main()

            self.assertEqual(res[0], '')   # empty
            self.assertEqual(OPT.all, ['ctp-mtl'])
            self.assertEqual(OPT.tp, f'{tdir}/POR_TP/aa/file.env')
            self.assertEqual(OPT.out, None)   # must be no output

    @with_(MockVar, TPPlans, 'do_tp', Mock())
    def test_pipeline(self):
        # found ctp
        with TempDir(name=True, chdir=True) as tdir:
            File('file.env').touch()
            File('Modules/ARR/ctp.txt').touch('a.xlsx', mkdir=True)
            File('Modules/TPI/TPI_BASE/ctp.txt').touch('b.xls', mkdir=True)
            File('Modules/TPI/TPI_OTHER/ctp.txt').touch('c.json', mkdir=True)
            File('a.json').touch()
            File('b.json').touch()
            cmd = f'tp_plans.py {tdir} -tp file.env -pipeline'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()

            self.assertEqual(OPT.all, ['a.json', 'b.json'])

        # no found
        with TempDir(name=True, chdir=True) as tdir:
            File('a.json').touch()
            File('b.json').touch()
            File('c.json').touch()
            cmd = f'tp_plans.py {tdir} -tp file.env -pipeline'.split()
            File('file.env').touch()
            File('Modules/ARR').touch(mkdir=True)
            with MockVar(sys, "argv", cmd):
                TPPlans().main()

            self.assertEqual(OPT.all, [tdir])

    def test_prtext(self):
        # single line
        self.assertEqual(TPPlans._prtext('blah'), '<pre>blah<br></pre>')

        # multiline
        instr = '''something
-i- Registering Plan(blah)
-i- found Plan(blah)
hello'''
        self.assertEqual(TPPlans._prtext(instr), '<pre>something<br>hello<br></pre>')
        self.assertEqual(TPPlans._prtext(''), '')


class TestTpUT(TestCase):

    @with_(TempDir, chdir=True, delete=True)
    def test_json(self):
        Plan.clear()
        TP.set_tp(TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'))
        File('a.json').touch('''
{
    "CTP": [
        {
            "Name": "T1",
            "Module": "FUN_DE",
            "Content_Expect": "53 if TP.name(M282) else 60",
            "__placeholder__": "C68",
            "failflow" : "1.0"
        },
        {
            "name": "T2",
            "module": "FUN_GT",
            "content_expect": "500.0",
            "Voltage1": "'a' if TP.name(M282) else 'b'"
        },
        {
            "name": "name",
            "Module": "Module",
            "content_expect": "content_expect"
        }
        ]
}
''')
        TPPlans.json_load('a.json', {'M282': '.'})
        self.assertEqual(len(Plan.tiobj_list), 2)
        self.assertEqual(str(Plan.tiobj_list[0]), "Plan('T1', id_lno=1, module=FUN_DE, failflow=True)")
        self.assertEqual(Plan.tiobj_list[0].content_expect, 53)
        self.assertEqual(str(Plan.tiobj_list[1]), "Plan('T2', id_lno=2, module=FUN_GT, Voltage1=a)")
        self.assertEqual(Plan.tiobj_list[1].content_expect, 500)

    def test_isprint(self):
        res = TPPlans.isprint(['one'], False)
        self.assertEqual(res.__class__.__name__, 'EmptyContext')
        res = TPPlans.isprint(['one'], True)
        self.assertEqual(res.__class__.__name__, 'EmptyContext')
        res = TPPlans.isprint(['one', 'two'], False)
        self.assertEqual(res.__class__.__name__, 'CaptureStdoutLog')
        res = TPPlans.isprint(['one', 'two'], True)
        self.assertEqual(res.__class__.__name__, 'EmptyContext')

    def test_import_waiver(self):
        pf = f'{UT_DIR_REPO}/plans/fun_de_14P.py'
        res = TPPlans.import_waiver(pf)
        self.assertEqual(res.weight_content, {'mod': 11, 'FUN': 100})    # existing file
        res = TPPlans.import_waiver(UT_DIR_REPO)
        self.assertEqual(res.weight_content, {'mod': 10})    # default


class TestReverse(TestCase):

    def test_basic(self):
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'

        # one module
        cmd = f'tp_plans.py {tp} -gen ARR -flows MAIN'.split()
        with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
            TPPlans().main()
            expect = '''from mod.plans import Plan, ModuleName
ModuleName('ARR')
Plan(name='CCA$',                                                              content_expect=1, level='*nom*')   # found=1
Plan(name='CCB$',                                                              content_expect=1, level='*nom*')   # found=1
Plan(name='TPIE_PgmRules$',                                                    )'''
        self.assertTextEqual(trimut(p.getvalue(), True), expect)

        # all modules write to file
        with TempDir(name=True) as tdir:
            cmd = f'tp_plans.py {tp} -gen ALL -out {tdir} -flows MAIN'.split()
            with MockVar(sys, "argv", cmd):
                TPPlans().main()
                result = File(f'{tdir}/ARR.py').read() + File(f'{tdir}/SCN.py').read()
                expect = '''from mod.plans import Plan, ModuleName
ModuleName('ARR')
Plan(name='CCA$',                                                              content_expect=1, level='*nom*')   # found=1
Plan(name='CCB$',                                                              content_expect=1, level='*nom*')   # found=1
Plan(name='TPIE_PgmRules$',                                                    )
from mod.plans import Plan, ModuleName
ModuleName('SCN')
Plan(name='CCA$',                                                              content_expect=1, level='*nom*')   # found=3
Plan(name='CCB$',                                                              content_expect=1, level='*nom*')   # found=3'''
                self.assertTextEqual(trimut(result, True), expect)

    def test_vmintc(self):
        env = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(env)

        # case1 - SetPointsPreInstance
        data = {'TEMPLATE': 'VminTC',
                'SetPointsPreInstance': 'spp',
                'TestMode': 'tm'}
        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=[('M1', 'T1', data)])):
            result = TPPlans.gen_mod(tp, 'M1', {('M1', 'T1'): 'B'})
        print(result)
        self.assertEqual(result, ['from mod.plans import Plan, ModuleName',
                                  "ModuleName('M1')",
                                  '',
                                  "Plan(name='T1$',                                                               TestMode='tm', SetPointsPreInstance='spp')    # Bypassed",
                                  ''])

        # case2 - PreInstance
        data = {'TEMPLATE': 'VminTC',
                'PreInstance': '(ExecutePatConfigSetPoint(epx=2))'
                }
        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=[('M1', 'T1', data)])):
            result = TPPlans.gen_mod(tp, 'M1', {('M1', 'T1'): 'P'})
        print(result)
        self.assertEqual(result, ['from mod.plans import Plan, ModuleName',
                                  "ModuleName('M1')",
                                  '',
                                  "Plan(name='T1$',                                                               TestMode='SingleVmin', PreInstance='epx=2') ",
                                  ''])

        # case2 - PreInstance random
        data = {'TEMPLATE': 'VminTC',
                'PreInstance': 'val1'
                }
        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=[('M1', 'T1', data)])):
            result = TPPlans.gen_mod(tp, 'M1', {('M1', 'T1'): 'P'})
        print(result)
        self.assertEqual(result, ['from mod.plans import Plan, ModuleName',
                                  "ModuleName('M1')",
                                  '',
                                  "Plan(name='T1$',                                                               TestMode='SingleVmin', PreInstance='val1') ",
                                  ''])

        # case3 - VminTC
        data = {'TEMPLATE': 'VminTC',
                'patlist': 'abcdef'
                }
        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=[('M1', 'T1', data)])):
            result = TPPlans.gen_mod(tp, 'M1', {('M1', 'T1'): 'P'})
        print(result)
        self.assertEqual(result, ['from mod.plans import Plan, ModuleName',
                                  "ModuleName('M1')",
                                  '',
                                  "Plan(name='T1$',                                                               content_expect=1, TestMode='SingleVmin', SetPointsPreInstance='tbd')   # found=-1",
                                  ''])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
