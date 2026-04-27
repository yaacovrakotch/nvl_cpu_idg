#!/usr/intel/pkgs/python3/3.6.3a/modules/r1/bin/python3
"""
Unit test for sort_class_tp_diff.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, patch, Mock
from main.sort_class_tp_diff import *
from gadget.gizmo import MockVar, singleton_instantiate
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.disk import Chdir, mkdirs
from gadget.tputil import trimut
from gadget.gizmo import with_
from gadget.strmore import sha1
from gadget.printmore import Dumper
import sys
import os
import gadget.helperclass as gadget_helperclass


class TestArgs(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        # Run full tpdiff, no pickle
        cmd = f'sort_class_tp_diff.py {UT_DIR}/Simple1a/TPL/EnvironmentFile.env {UT_DIR}/Simple1b/TPL/EnvironmentFile.env -nopickle'
        with MockVar(sys, "argv", cmd.split()), \
                CaptureStdoutLog() as p:
            TPDiff().main()
        result = p.getvalue()
        print(result)

        # with pickle
        cmd = f'sort_class_tp_diff.py {UT_DIR}/Simple1a/TPL/EnvironmentFile.env {UT_DIR}/Simple1b/TPL/EnvironmentFile.env'
        with MockVar(sys, "argv", cmd.split()), \
                CaptureStdoutLog() as p:
            TPDiff().main()
        with TempDir(name=True, delete=True) as tdir:
            File(f'{tdir}/pickle').touch(trimut(p.getvalue(), True))
            File(f'{tdir}/non-pickle').touch(trimut(result, True))

            self.assertGoldEqual(f'{tdir}/pickle', f'{UT_DIR}/compare_files/sort_class_diff.txt')
            self.assertGoldEqual(f'{tdir}/non-pickle', f'{UT_DIR}/compare_files/sort_class_diff.txt')

        # error case - invalid args - missing 2nd tp
        cmd = f'sort_class_tp_diff.py {UT_DIR}/Simple1a/TPL/EnvironmentFile.env'
        with MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                TPDiff().main()
        self.assertIn('Error:', p.getvalue())

        # -flows
        cmd = f'sort_class_tp_diff.py -flows'
        with MockVar(sys, "argv", cmd.split()), \
                CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                TPDiff().main()
        self.assertIn('Flows in order', p.getvalue())

    def test_skip_only(self):
        # skip all
        with MockVar(OPT, 'only', None), MockVar(OPT, 'skip', None):   # This is needed so that other tests will not be affected
            cmd = f'sort_class_tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env -only 9a -skip 9a'
            with MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                TPDiff().main()
            # print(p.getvalue())
            self.assertEqual(len(trimut(p.getvalue())), 4)

    def test_nochange(self):
        total = 15

        # specify a module that does not exist, so everything is no change
        with MockVar(OPT, 'module', None):
            cmd = f'sort_class_tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env -skip 6a -module JDR'
            with MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                TPDiff().main()
            print(p.getvalue())
            self.assertEqual(len([x for x in p.getvalue().split('\n') if x == 'No change']), total - 1)    # minus 1 because of Top level files skipped

        # without pickle, same input
        cmd = f'sort_class_tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env -nopickle -skip 6a'
        with MockVar(sys, "argv", cmd.split()), \
                CaptureStdoutLog() as p:
            TPDiff().main()
        result = p.getvalue()
        # print(result)
        no_change = [line for line in result.split('\n') if line.startswith('No change')]
        self.assertEqual(len(no_change), total)

        # check the sections
        sections = [line for line in result.split('\n') if line.startswith('===')]
        self.assertEqual(len(sections), total)

    @with_(TempDir, chdir=True)
    def test_sdiff(self):
        File('f1').touch('a\nb\nc\ne\n')
        File('f2').touch('a\nB\ne\n')
        cmd = f'sort_class_tp_diff.py f1 f2 -sdiff -W 10'
        with MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                print()
                TPDiff().main()

        expect = '''
a            a
b          | B
c          <
e            e

'''
        self.assertTextEqual(p.getvalue(), expect)


class TestMain(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_a_lvl_diff(self):

        tp = [TestProgram(UT_DIR + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/Simple1b/TPL/EnvironmentFile.env')]

        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.lvl_diff()
        expect = f'''
Added:   BASE::tc3
No change
  TP1_Module TP1_Test TP1_TestCond TP1_Param  TP1_Timlvl_value Diff  \\
0          N  (Blank)      (Blank)   (Blank)           (Blank)    >
1          N  (Blank)      (Blank)   (Blank)           (Blank)    >
2          N  (Blank)      (Blank)   (Blank)           (Blank)    >
3          N  (Blank)      (Blank)   (Blank)           (Blank)    >
4          N  (Blank)      (Blank)   (Blank)           (Blank)    >
5          N  (Blank)      (Blank)   (Blank)           (Blank)    >

  TP2_Module TP2_Test     TP2_TestCond            TP2_Param  \\
0       None     None  Added:BASE::tc3                 tper
1       None     None  Added:BASE::tc3                p_lvl
2       None     None  Added:BASE::tc3         p_vccio_spec
3       None     None  Added:BASE::tc3      p_prim_1p8_spec
4       None     None  Added:BASE::tc3  c_vccddq_vload_prog
5       None     None  Added:BASE::tc3                 ter1

   TP2_Timlvl_value   Count
0               3.00      1
1               0.30      1
2               1.20      1
3               0.02      1
4              56.30      1
5               6.00      1
Diff         >  Grand Total
TP1_Module
N            6            6
Grand Total  6            6
Diff         >  Grand Total
TP2_Module
None         6            6
Grand Total  6            6
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_a_tim_diff(self):
        tp = [TestProgram(UT_DIR + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/Simple1b/TPL/EnvironmentFile.env')]

        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.tim_diff()
        expect = f'''
Changed:BASE::tc2
  UseBy: ARR  CCB
   p_vcc_gb_type = 0.1                                          + p_vcc_gb_type = 0.4
   tester_gb_hc = 5.5                                           + tester_gb_hc = 22.0
  TP1_Module TP1_Test       TP1_TestCond        TP1_Param   TP1_Timlvl_value  \\
0        ARR      CCB  Changed:BASE::tc2  p_prim_1p8_spec               0.02
1        ARR      CCB  Changed:BASE::tc2    p_vcc_gb_type               0.10
2        ARR      CCB  Changed:BASE::tc2     p_vccio_spec               1.20
3        ARR      CCB  Changed:BASE::tc2             ter1               5.00
4        ARR      CCB  Changed:BASE::tc2     tester_gb_hc               5.50
5        ARR      CCB  Changed:BASE::tc2             tper               1.00

      Diff TP2_Module TP2_Test       TP2_TestCond        TP2_Param  \\
0  matched        ARR      CCB  Changed:BASE::tc2  p_prim_1p8_spec
1        +        ARR      CCB  Changed:BASE::tc2    p_vcc_gb_type
2  matched        ARR      CCB  Changed:BASE::tc2     p_vccio_spec
3  matched        ARR      CCB  Changed:BASE::tc2             ter1
4        +        ARR      CCB  Changed:BASE::tc2     tester_gb_hc
5  matched        ARR      CCB  Changed:BASE::tc2             tper

   TP2_Timlvl_value   Count
0               0.02      1
1               0.40      1
2               1.20      1
3               5.00      1
4              22.00      1
5               1.00      1
Diff         +  matched  Grand Total
TP1_Module
ARR          2        4            6
Grand Total  2        4            6
Diff         +  matched  Grand Total
TP2_Module
ARR          2        4            6
Grand Total  2        4            6
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_tid_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile2.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).tid_diff()
        expect = '''
ARR,max,NONE,EDC tids  = 1                                   <
ARR,nom,NONE,EDC tids  = 1                                   + ARR,nom,NONE,EDC tids  = 2
PTH,nom,1100,EDC tids  = 3                                   <
PTH,nom,1200,EDC tids  = 3                                   <
SCN,nom,NONE,EDC tids  = 6                                   + SCN,nom,NONE,EDC tids  = 7
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # specific module
        obj = Diff(tp)
        obj.robj_mod = re.compile('^ARR')
        with CaptureStdoutLog() as p:
            print()
            obj.tid_diff()
        expect = '''
ARR,max,NONE,EDC tids  = 1                                   <
ARR,nom,NONE,EDC tids  = 1                                   + ARR,nom,NONE,EDC tids  = 2
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky", neg=False))
    def test_a_tid_diff2(self):
        # with output, detail=True
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]
        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.is_detail = True
            df.tid_diff()

            output = open(join(tdir, 'Simple1a.tid.csv')).read()
            self.assertEqual(len(output.split('\n')), 17)
            output = open(join(tdir, 'Simple1b.tid.csv')).read()
            self.assertEqual(len(output.split('\n')), 11)

            expect = '''Module,corner,freq,edckill,tid_count,diff,Module,corner,freq,edckill,tid_count
ARR,max,NONE,EDC,1,<,,,,,
ARR,nom,NONE,EDC,1,+,ARR,nom,NONE,EDC,2
PTH,nom,1100,EDC,3,<,,,,,
PTH,nom,1200,EDC,3,<,,,,,
SCN,nom,NONE,EDC,6, ,SCN,nom,NONE,EDC,6
'''
            self.assertTextEqual(open(join(tdir, 'tid_diff.csv')).read(), expect)
        expect = '''
Detail:
   ARR,max,NONE,EDC tid#0 = 1466650_00                          <
   PTH,nom,1100,EDC tid#0 = 2371433_00                          <
   PTH,nom,1100,EDC tid#1 = 2371470_00                          <
   PTH,nom,1100,EDC tid#2 = 2371471_00                          <
   PTH,nom,1200,EDC tid#0 = 2371465_00                          <
   PTH,nom,1200,EDC tid#1 = 2371468_00                          <
   PTH,nom,1200,EDC tid#2 = 2371469_00                          <
                                                                > ARR,nom,NONE,EDC tid#1 = 1466650_00

Summary:
ARR,max,NONE,EDC tids  = 1                                   <
ARR,nom,NONE,EDC tids  = 1                                   + ARR,nom,NONE,EDC tids  = 2
PTH,nom,1100,EDC tids  = 3                                   <
PTH,nom,1200,EDC tids  = 3                                   <
Done: 0.000 Secs, 15
Done: 0.000 Secs, 9
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # detail=True, reversed
        tp = [TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env')]
        with CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.is_detail = True
            df.tid_diff()

        expect = '''
Detail:
                                                                > ARR,max,NONE,EDC tid#0 = 1466650_00
   ARR,nom,NONE,EDC tid#1 = 1466650_00                          <
                                                                > PTH,nom,1100,EDC tid#0 = 2371433_00
                                                                > PTH,nom,1100,EDC tid#1 = 2371470_00
                                                                > PTH,nom,1100,EDC tid#2 = 2371471_00
                                                                > PTH,nom,1200,EDC tid#0 = 2371465_00
                                                                > PTH,nom,1200,EDC tid#1 = 2371468_00
                                                                > PTH,nom,1200,EDC tid#2 = 2371469_00

Summary:
                                                             > ARR,max,NONE,EDC tids  = 1
ARR,nom,NONE,EDC tids  = 2                                   - ARR,nom,NONE,EDC tids  = 1
                                                             > PTH,nom,1100,EDC tids  = 3
                                                             > PTH,nom,1200,EDC tids  = 3
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_tidpat_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        # with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
        with TempDir(name=True) as tdir, \
                MockVar(gadget_helperclass, 'IS_UT', False):
            df = Diff(tp)
            df.out = tdir
            fn = df.tidpat_diff()

        # specific module(is_skip_module)
        obj = Diff(tp)
        obj.robj_mod = re.compile('^ARR')

        data1 = [{'SCN', 'CCA,nom,NONE,EDC', 'g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom'},
                 {'SCN', 'CCB,nom,NONE,EDC', 'g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1'},
                 ]
        data2 = [{'SCN', 'CCA,nom,NONE,EDC', 'g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom'},
                 {'SCN', 'CCB,nom,NONE,EDC', 'g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1'},
                 ]

        with MockVar(tp[0].mtpl, 'iter_flows', Mock(return_value=data1)), \
                MockVar(tp[1].mtpl, 'iter_flows', Mock(return_value=data2)), \
                MockVar(gadget_helperclass, 'IS_UT', False), CaptureStdoutLog() as p:
            print()
            obj.tidpat_diff()
        expect = '''
No change
Print output table to tidpat_diff_module.csv
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # specific input
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile2.env')]

        obj = Diff(tp)
        with CaptureStdoutLog() as p, MockVar(gadget_helperclass, 'IS_UT', False):
            print()
            obj.tidpat_diff()
        expect = '''
SCN CCA,nom,NONE,EDC 2371433_00 #0 = g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom <
                                                                                 > SCN CCA,nom,NONE,EDC 2371434_00 #0 = g2026508W2371434I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom
SCN CCA,nom,NONE,EDC 2371470_00 #0 = g2026530W2371470I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m1 + SCN CCA,nom,NONE,EDC 2371470_00 #0 = g2026530W2371470I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC011J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m1
SCN CCA,nom,NONE,EDC 2371471_00 #0 = g2026531W2371471I_Nt_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m0 + SCN CCA,nom,NONE,EDC 2371471_00 #0 = g2026532W2371471I_Nt_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m0
                                                                                 > SCN CCA,nom,NONE,EDC 9999991_fn #0 = tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0
Print output table to tidpat_diff_module.csv
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_a_ins_detail(self):
        tp = [TestProgram(UT_DIR + '/MTSSDSCA2H12A202241/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/MTLXXXXAXH19J20S218/POR_TP/Class_MTL_P68/EnvironmentFile.env')]

        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.ins_detail()

        time_now = datetime.datetime.now()
        outfile_name = str('TestInstanceParamDiff_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        matchfile_name = str('TestInstanceMatchParam_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        matchfile_name = matchfile_name + '.csv'
        output_filename = f'Test Instance Diff Parameter file: {output_file}'
        match_filename = f'Test Instance Match Parameter file: {matchfile_name}'
        final_test_info = f'''{output_filename}
{match_filename}
'''
        expect = '''
No change
No change
'''
        expect = expect
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_ins_detail_ut(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]
        obj = Diff(tp)

        data1 = [('m1', 'test1', {'patlist': 'a',
                                  'diff': 'val1',
                                  'unq1': 'val2'}),
                 ('m2', 'test2', {'patlist': 'a',
                                  'diff': 'val1',
                                  'unq1': 'val2'}),
                 ('m3', 'test3', {'patlist': 'a',
                                  'diff': 'val1'}),
                 ]
        data2 = [('m1', 'test1', {'patlist': 'a',
                                  'diff': 'val1a',
                                  'unq2': 'val2'}),
                 ('m2', 'test2', {'patlist': 'a',
                                  'diff': 'val1a',
                                  'unq2': 'val2',
                                  '_EDCKIL': 'val3'}),
                 ('m3', 'test3', {'patlist': 'a',
                                  'diff': 'val1a'}),
                 ]

        with MockVar(tp[0].mtpl, 'iter_flows', Mock(return_value=data1)), \
                MockVar(tp[1].mtpl, 'iter_flows', Mock(return_value=data2)), \
                TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            obj.out = tdir
            obj.ins_detail()

        time_now = datetime.datetime.now()
        outfile_name = str('TestInstanceParamDiff_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        matchfile_name = str('TestInstanceMatchParam_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        matchfile_name = matchfile_name + '.csv'
        output_filename = f'-i- Test Instance Diff Parameter file: {output_file}'
        match_filename = f'-i- Test Instance Match Parameter file: {matchfile_name}'
        expect = f'''
{output_filename}
{match_filename}
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_a_patreorder_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile2.env')]

        df = Diff(tp)
        with CaptureStdoutLog() as p:
            print()
            df.patreorder_diff()
        expect = '''
Reordered: SCN                  cpu_fuse_read_special_x, reordered=1 of 3: 2371468_00
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # with detail
        df.is_detail = True
        with CaptureStdoutLog() as p:
            print()
            df.patreorder_diff()
        expect = '''
Reordered: SCN                  cpu_fuse_read_special_x, reordered=1 of 3: 2371468_00
              R 2371468_00
   2371465_00   2371465_00
   2371469_00   2371469_00
   2371468_00 <

'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_fullpat_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile2.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).fullpat_diff()
        expect = '''

SCN cpu_fuse_read_hvm_x, 1 of 3:
   _TR1PThTC001J3fn_ vs g2026530W2371470I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC011J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m1
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_plb_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile2.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).plb_diff()
        expect = '''

TID count, +add/-del/chng Module               patlist
Total:    1, +0/-0/1      ARR                  shops_L_list
Total:    4, +1/-1/1      SCN                  cpu_fuse_read_hvm_x
Added                     SCN                  sublist
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # reverse the order
        df = Diff([tp[1], tp[0]])
        df.is_detail = True
        with CaptureStdoutLog() as p:
            print()
            df.plb_diff()
        expect = '''

TID count, +add/-del/chng Module               patlist
Total:    1, +0/-0/1      ARR                  shops_L_list
   1466650_00 tid = tuple 2294512                               - 1466650_00 tid = tuple 2294511
Total:    4, +1/-1/1      SCN                  cpu_fuse_read_hvm_x
   2371434_00 tid = tuple 2026508                               <
                                                                > 2371433_00 tid = tuple 2026507
   2371471_00 tid = tuple 2026532                               - 2371471_00 tid = tuple 2026531
Removed                   SCN                  sublist
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_ctrbin_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).ctrbin_diff()
        expect = '''
Changed ARR ARR::MAIN1 CCB:
   Port#1 IncrementCounters = 90450005 vs 90450004
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_port_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).port_diff()
        expect = '''
Changed ARR ARR::MAIN1 CCA:
     (none)
   > Port#2 connection Return 1
Changed ARR ARR::MAIN1 CCC:
     Port#1 connection GoTo CCD
   + Port#1 connection GoTo CCE
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_passfail_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).passfail_diff()
        expect = '''
Changed ARR ARR::MAIN1 CCA:
     Port#0 PassFail Fail
   + Port#0 PassFail Pass
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_allports_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).allports_diff('MAIN')
        expect = '''
Changed ARR ARR::MAIN1 CCA
     Port#0 PassFail Fail
   + Port#0 PassFail Pass
     (none)
   > Port#2 connection Return 1
Changed ARR ARR::MAIN1 CCB
     Port#1 IncrementCounters 90450005
   - Port#1 IncrementCounters 90450004
Changed ARR ARR::MAIN1 CCC
     Port#1 connection GoTo CCD
   + Port#1 connection GoTo CCE
Removed ARR ARR::MAIN1 CCD
Added   ARR ARR::MAIN1 CCE
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # The other way
        tp = [TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).allports_diff('MAIN')
        expect = '''
Changed ARR ARR::MAIN1 CCA
     Port#0 PassFail Pass
   - Port#0 PassFail Fail
     Port#2 connection Return 1
   < (none)
Changed ARR ARR::MAIN1 CCB
     Port#1 IncrementCounters 90450004
   + Port#1 IncrementCounters 90450005
Changed ARR ARR::MAIN1 CCC
     Port#1 connection GoTo CCE
   - Port#1 connection GoTo CCD
Removed ARR ARR::MAIN1 CCE
Added   ARR ARR::MAIN1 CCD
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_ins_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            Diff(tp).ins_diff()
        expect = '''
ARR: ======
   CCA                                                          EDC max NONE        + CCA                                                          EDC nom NONE
   CCD                                                          EDC nom NONE        <
                                                                                    > CCE                                                          EDC nom NONE

PTH: ==== NOT EXIST in 2nd TP
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # with output
        with TempDir(name=True) as tdir, MockVar(OPT, 'out', tdir):
            Diff(tp).ins_diff()
            expect = '''Module,instance,edckil,corner,freq,diff,Module,instance,edckil,corner,freq
ARR,CCA,EDC,max,NONE,+,ARR,CCA,EDC,nom,NONE
ARR,CCB,EDC,nom,NONE, ,ARR,CCB,EDC,nom,NONE
ARR,CCD,EDC,nom,NONE,<,,,,,
,,,,,>,ARR,CCE,EDC,nom,NONE
SCN,CCA,EDC,nom,NONE, ,SCN,CCA,EDC,nom,NONE
SCN,CCB,EDC,nom,NONE, ,SCN,CCB,EDC,nom,NONE
'''
            self.assertTextEqual(open(join(tdir, 'ins_diff.csv')).read(), expect)

    def test_a_basenumber_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).basenumber_diff()
        expect = '''
ARR CCB = 2161                                               + ARR CCB = 2162
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_a_tp_files(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        obj = Diff(tp)
        with CaptureStdoutLog() as p:
            print()
            obj.tp_files_top()
            obj.tp_files_mod()
        expect = '''
Legend: (+add_lines/-removed_lines/changed_lines)
Changed +5/-0/0              BaseLevels.tcg
Changed +0/-0/1              BaseTiming.tcg
Changed +0/-1/0              SubTestPlan_CLASS_TGLH81.stpl
Changed +0/-0/1              UservarDefinitions.usrv
Added                        EnvironmentFile2.env
Legend: (+add_lines/-removed_lines/changed_lines)
Changed +0/-0/1              ARR/InputFiles/input1.txt
Module Missing: PTH
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # no diff
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env')]

        obj = Diff(tp)
        with CaptureStdoutLog() as p:
            print()
            obj.tp_files_top()
            obj.tp_files_mod()
        expect = '''
No change
No change
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tc_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        df = Diff(tp)
        # tim, value=False, one tc
        with CaptureStdoutLog() as p:
            print()
            df.tc_tim_diff(tim=['BASE::tc1'], lvl=[], is_diffonly=False, is_value=False, col=60)
        expect = '''
tper                           toInteger(2)                    tper                           toInteger(2)
p_vcc_gb_type                  99V                             p_vcc_gb_type                  99V
p_vccio_spec                   1.2V                            p_vccio_spec                   1.2V
p_prim_1p8_spec                ccf_gb_vlc                      p_prim_1p8_spec                ccf_gb_vlc
  tester_gb_hc                   hc_vcc_gb*p_vcc_gb_type*cl_qa_flag
= tester_gb_hc                   hc_vcc_gb*p_vcc_gb_type*cl_qa_flag
ter1                           tper==1?5V:6V                   ter1                           tper==1?5V:6V
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # tim, value=True, two tc
        with CaptureStdoutLog() as p:
            print()
            df.tc_tim_diff(tim=['BASE::tc1', 'BASE::tc2'], lvl=[], is_diffonly=False, is_value=True, col=60)
        expect = '''
tper                             2S                          | tper                             1S
p_vcc_gb_type                   99S                          | p_vcc_gb_type                  400mS
p_vccio_spec                     1.2S                          p_vccio_spec                     1.2S
p_prim_1p8_spec                 20mS                           p_prim_1p8_spec                 20mS
tester_gb_hc                   5445S                         | tester_gb_hc                    22S
ter1                             6S                          | ter1                             5S
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # lvl, value=True, full command
        cmd = f'sort_class_tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env -lvl BASE::tc1 -value'
        with MockVar(sys, "argv", cmd.split()), \
                self.assertRaises(SystemExit), \
                CaptureStdoutLog() as p:
            print()
            TPDiff().main()
        expect = '''
tper                             2S                            tper                             2S
p_lvl                           88S                            p_lvl                           88S
p_vccio_spec                     1.2S                          p_vccio_spec                     1.2S
p_prim_1p8_spec                 20mS                           p_prim_1p8_spec                 20mS
c_vccddq_vload_prog            144S                            c_vccddq_vload_prog            144S
ter1                             6S                            ter1                             6S
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_lvl_diff1(self):
        tp = [TestProgram(UT_DIR + '/MTSSDSCA2H12A202241/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/MTLXXXXAXH19J20S218/POR_TP/Class_MTL_P68/EnvironmentFile.env')]

        OPT.userinputlist = UT_DIR + '/sort_class_mapping1.xlsx'
        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.lvl_diff()

        expect = '''
{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501', 'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU1': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1502', 'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503'}
Print output XYZ successfully!
Print output XYZ successfully!
'''
        result = trimut(p.getvalue(), True, True)
        result = re.sub(r"SortClassLvlPinDiff[\w\-\.]+", 'XYZ', result)
        self.assertTextEqual(result, expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky due to timestamp compare", neg=False))
    def test_tim_diff1(self):
        tp = [TestProgram(UT_DIR + '/MTSSDSCA2H12A202241/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/MTLXXXXAXH19J20S218/POR_TP/Class_MTL_P68/EnvironmentFile.env')]

        OPT.userinputlist = UT_DIR + '/sort_class_mapping1.xlsx'
        outcsv = 'Print output SortClasstimingDiff'
        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.tim_diff()
        time_now = datetime.datetime.now()
        outfile_name = str('{}_TimToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        outfile_name1 = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        output_file1 = outfile_name1 + '.csv successfully!'
        output_final = f'''{output_file}
{output_file1}
'''
        expect = '''
{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501', 'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU1': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1502', 'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503'}
'''
        expect = expect + output_final

        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_sortclass_level_diff(self):

        TP1_more_than_TP2 = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': {'BASE::soc_all_univ_1p8_x_die_lvl_nom_lvl': {'soc_vipr_eza_pins': '0', 'soc_edm_all': '0', 'XXVCCRTC': '1.5', 'HC03_0P77_VNNAON_PCIEPHY_2': '0.77', 'HC04_0P77_VNNAON_PCIEPHY_3': '0.77', 'HC05_0P77_VNNAON_USB2PHY': '0.77', 'HC07_0P77_VNNAON_QUIET2CLK': '0.97', 'HC08_0P77_VCCSA': '0.77', 'LC01_1P8_QUIET2': '1.8', 'LC02_1P8_QUIET2_FUSE': '1.8', 'LC03_1P8_GPCOM01345': '1.8', 'LC04_1P8_USB2PHY': '1.8', 'LC05_1P8_QUIET1_CLKPLL': '1.8', 'LC06_1P8_QUIET1_CNV': '1.8', 'LC07_0P77_VNNAON_CNVDPHY': '0.77', 'LC08_0P77_VNNAON_EDP': '0.77', 'LC09_0P77_VNNAON_UFSUSB3': '0.77', 'LC10_0P77_VNNAON_CNVPLL': '0.77', 'HV01_3P3_USB2PHY': '3.3', 'HV02_1P25_VCCIO': '1.55', 'HV03_1P25_VCCIO_PCIEPHY': '1.25', 'HV04_1P25_VCCIO_CNVISCLK': '1.25', 'HV05_1P25_VCCIO_GPCOM4': '1.25', 'HV06_5P5_VCCFUSE_SOC0': '0', 'HV07_5P5_VCCFUSE_SOC1': '0', 'HV08_1P05_VCCVDD2': '1.05', 'VLC01_1P04_VCCA_SENSE': '0', 'VLC02_1P0_BISRPGM2': '0', 'VLC03_1P0_BISRPGM1': '0', 'VLC04_1P0_BISRPGM3': '0', 'VLC05_1P0_BISRPGM4': '0', 'VLC06_1P0_BISRPGM5': '0', 'VLC07_1P0_BISRPGM6': '0', 'soc_all_clk_gnd': '0'}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501': {'BASE::soc_all_dft_x_x_pkg_lvl_nom_lvl': {'soc_allwoec_lvl': '0', 'soc_ec_lvl': '0', 'soc_hpc_lvl': '0', 'XXVCCRTC': '1.5', 'VCC1P8_LC': '1.8', 'VCC1P8_QUIET_1_LC': '1.8', 'VCC1P8_QUIET_2_LC': '1.8', 'VCC3P3_LC': '3.3', 'VNNAON_QUIET_1_HC': '0.77', 'VNNAON_QUIET_2_HC': '0.77', 'VCCIO_HC': '1.25', 'VCCFPGM_SOC_0_LC': '0.0', 'VCCFPGM_SOC_1_LC': '0.0', 'VCCFPGM_CPU_0_NOM_LC': '0.0', 'VCCFPGM_CPU_1_HV_LC': '0.0', 'VCCFPGM_GCD_LC': '0.0', 'VCCFPGM_IOE_LC': '0.0', 'VDD2_LC': '1.05', 'VCCSA_HC': '0.77', 'VCCIA_HC': '0.2', 'VCCGT_HC': '0.2', 'CORE_EXT_BGREF_VLC': '0.0'}}}]

        Dummy = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501',
                        }

        user_pin_comparison = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['HC07_0P77_VNNAON_QUIET2CLK|VCCSA_HC',
                                                             'HV08_1P05_VCCVDD2|VDD2_LC',
                                                             'HV02_1P25_VCCIO|VCCIO_HC']
                               }

        outcsv = 'Print output Sortclass_file_name'

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_level_diff(TP1_more_than_TP2, Dummy, user_pin_comparison, user_mapping)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_PinsToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        outfile_name1 = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        output_file1 = outfile_name1 + '.csv successfully!'
        expect = f'''
{output_file}
{output_file1}
'''
        self.assertTextEqual(p.getvalue(), expect)

        TP1_less_than_TP2 = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU1': {'BASE::soc_all_univ_1p8_x_die_lvl_nom_lvl1': {'soc_vipr_eza_pins': '0', 'soc_edm_all': '0', 'XXVCCRTC': '1.5', 'HC04_0P77_VNNAON_PCIEPHY_3': '0.77', 'HC05_0P77_VNNAON_USB2PHY': '0.77', 'HC07_0P77_VNNAON_QUIET2CLK': '0.67', 'LC01_1P8_QUIET2': '1.8', 'LC02_1P8_QUIET2_FUSE': '1.8', 'LC05_1P8_QUIET1_CLKPLL': '1.8', 'LC06_1P8_QUIET1_CNV': '1.8', 'LC07_0P77_VNNAON_CNVDPHY': '0.77', 'HV01_3P3_USB2PHY': '3.3', 'HV02_1P25_VCCIO': '1.05', 'HV03_1P25_VCCIO_PCIEPHY': '1.25', 'HV07_5P5_VCCFUSE_SOC1': '0', 'HV08_1P05_VCCVDD2': '1.00'}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1502': {'BASE::soc_all_dft_x_x_pkg_lvl_nom_lvl1': {'soc_allwoec_lvl': '0', 'soc_ec_lvl': '0', 'soc_hpc_lvl': '0', 'XXVCCRTC': '1.5', 'VCC1P8_LC': '1.8', 'VCC1P8_QUIET_1_LC': '1.8', 'VCC1P8_QUIET_2_LC': '1.8', 'VCC3P3_LC': '3.3', 'VNNAON_HC': '0.77', 'VNNAON_QUIET_1_HC': '0.77', 'VNNAON_QUIET_2_HC': '0.77', 'VCCIO_HC': '1.25', 'VCCFPGM_SOC_0_LC': '0.0', 'VCCFPGM_SOC_1_LC': '0.0', 'VCCFPGM_CPU_0_NOM_LC': '0.0', 'VCCFPGM_CPU_1_HV_LC': '0.0', 'VCCFPGM_GCD_LC': '0.0', 'VCCFPGM_IOE_LC': '0.0', 'VDD2_LC': '1.05', 'VCCGT_HC': '0.2', 'CORE_EXT_BGREF_VLC': '0.0'}}}]

        Dummy1 = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU1': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1502',
                        }

        user_pin_comparison = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['HC07_0P77_VNNAON_QUIET2CLK|VNNAON_QUIET_1_HC',
                                                             'HV08_1P05_VCCVDD2|VDD2_LC',
                                                             'HV02_1P25_VCCIO|VCCIO_HC']
                               }

        outcsv = 'Print output Sortclass_file_name'

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_level_diff(TP1_less_than_TP2, Dummy1, user_pin_comparison, user_mapping)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_PinsToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        outfile_name1 = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        output_file1 = outfile_name1 + '.csv successfully!'
        expect = f'''
{output_file}
{output_file1}
'''
        self.assertTextEqual(p.getvalue(), expect)

        TP_equal = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': {'BASE::soc_all_univ_1p8_x_die_lvl_nom_lvl2': {'soc_vipr_eza_pins': '0', 'soc_edm_all': '0', 'XXVCCRTC': '1.5', 'HC03_0P77_VNNAON_PCIEPHY_2': '0.77', 'HC04_0P77_VNNAON_PCIEPHY_3': '0.77', 'HC05_0P77_VNNAON_USB2PHY': '0.77', 'HC07_0P77_VNNAON_QUIET2CLK': '0.77', 'LC01_1P8_QUIET2': '1.8', 'LC02_1P8_QUIET2_FUSE': '1.8', 'LC03_1P8_GPCOM01345': '1.8', 'LC04_1P8_USB2PHY': '1.8', 'LC05_1P8_QUIET1_CLKPLL': '1.8', 'LC06_1P8_QUIET1_CNV': '1.8', 'LC07_0P77_VNNAON_CNVDPHY': '0.77', 'LC08_0P77_VNNAON_EDP': '0.77', 'HV01_3P3_USB2PHY': '3.3', 'HV02_1P25_VCCIO': '1.25', 'HV03_1P25_VCCIO_PCIEPHY': '1.25', 'HV04_1P25_VCCIO_CNVISCLK': '1.25', 'HV05_1P25_VCCIO_GPCOM4': '1.25', 'HV06_5P5_VCCFUSE_SOC0': '0', 'HV07_5P5_VCCFUSE_SOC1': '0', 'HV08_1P05_VCCVDD2': '1.05'}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503': {'BASE::soc_all_dft_x_x_pkg_lvl_nom_lvl2': {'soc_allwoec_lvl': '0', 'soc_ec_lvl': '0', 'soc_hpc_lvl': '0', 'XXVCCRTC': '1.5', 'VCC1P8_LC': '1.8', 'VCC1P8_QUIET_1_LC': '1.8', 'VCC1P8_QUIET_2_LC': '1.8', 'VCC3P3_LC': '3.3', 'VNNAON_HC': '0.77', 'VNNAON_QUIET_1_HC': '0.77', 'VNNAON_QUIET_2_HC': '0.77', 'VCCIO_HC': '1.25', 'VCCFPGM_SOC_0_LC': '0.0', 'VCCFPGM_SOC_1_LC': '0.0', 'VCCFPGM_CPU_0_NOM_LC': '0.0', 'VCCFPGM_CPU_1_HV_LC': '0.0', 'VCCFPGM_GCD_LC': '0.0', 'VCCFPGM_IOE_LC': '0.0', 'VDD2_LC': '1.05', 'VCCSA_HC': '0.77', 'VCCIA_HC': '0.2', 'VCCGT_HC': '0.2', 'CORE_EXT_BGREF_VLC': '0.0'}}}]

        Dummy2 = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503',
                        }

        user_pin_comparison = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['HC07_0P77_VNNAON_QUIET2CLK|VNNAON_QUIET_1_HC',
                                                             'HV08_1P05_VCCVDD2|VDD2_LC',
                                                             'HV02_1P25_VCCIO|VCCIO_HC']
                               }

        outcsv = 'Print output Sortclass_file_name'

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_level_diff(TP_equal, Dummy2, user_pin_comparison, user_mapping)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_PinsToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        outfile_name1 = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        output_file1 = outfile_name1 + '.csv successfully!'
        expect = f'''
{output_file}
{output_file1}
'''
        self.assertTextEqual(p.getvalue(), expect)

        # to complete the log.info special case
        TP_sc = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': {'BASE::soc_all_univ_1p8_x_die_lvl_nom_lvl2': {'soc_vipr_eza_pins': '0', 'soc_edm_all': '0', 'XXVCCRTC': '1.5', 'HC03_0P77_VNNAON_PCIEPHY_2': '0.77', 'HC04_0P77_VNNAON_PCIEPHY_3': '0.77', 'HC05_0P77_VNNAON_USB2PHY': '0.77', 'HC07_0P77_VNNAON_QUIET2CLK': '0.77', 'LC01_1P8_QUIET2': '1.8', 'LC02_1P8_QUIET2_FUSE': '1.8', 'LC03_1P8_GPCOM01345': '1.8', 'LC04_1P8_USB2PHY': '1.8', 'LC05_1P8_QUIET1_CLKPLL': '1.8', 'LC06_1P8_QUIET1_CNV': '1.8', 'LC07_0P77_VNNAON_CNVDPHY': '0.77', 'LC08_0P77_VNNAON_EDP': '0.77', 'HV01_3P3_USB2PHY': '3.3', 'HV02_1P25_VCCIO': '1.25', 'HV03_1P25_VCCIO_PCIEPHY': '1.25', 'HV04_1P25_VCCIO_CNVISCLK': '1.25', 'HV05_1P25_VCCIO_GPCOM4': '1.25', 'HV06_5P5_VCCFUSE_SOC0': '0', 'HV07_5P5_VCCFUSE_SOC1': '0', 'HV08_1P05_VCCVDD2': '1.05'}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503': {'BASE::soc_all_dft_x_x_pkg_lvl_nom_lvl2': {'soc_allwoec_lvl': '0', 'soc_ec_lvl': '0', 'soc_hpc_lvl': '0', 'XXVCCRTC': '1.5', 'VCC1P8_LC': '1.8', 'VCC1P8_QUIET_1_LC': '1.8', 'VCC1P8_QUIET_2_LC': '1.8', 'VCC3P3_LC': '3.3', 'VNNAON_HC': '0.77', 'VNNAON_QUIET_1_HC': '0.77', 'VNNAON_QUIET_2_HC': '0.77', 'VCCIO_HC': '1.25', 'VCCFPGM_SOC_0_LC': '0.0', 'VCCFPGM_SOC_1_LC': '0.0', 'VCCFPGM_CPU_0_NOM_LC': '0.0', 'VCCFPGM_CPU_1_HV_LC': '0.0', 'VCCFPGM_GCD_LC': '0.0', 'VCCFPGM_IOE_LC': '0.0', 'VDD2_LC': '1.05', 'VCCSA_HC': '0.77', 'VCCIA_HC': '0.2', 'VCCGT_HC': '0.2', 'CORE_EXT_BGREF_VLC': '0.0'}}}]

        Dummy2 = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503',
                        }

        user_pin_comparison = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['HC07_0P77_VNNAON_QUIET2CLK|2']
                               }

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_level_diff(TP_sc, Dummy2, user_pin_comparison, user_mapping)
        expect = '''
ERROR:Pin 2 not found in ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503. Please check your PinsToMatch tab
'''
        self.assertTextEqual(p.getvalue(), expect)

        TP_sc_1 = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': {'BASE::soc_all_univ_1p8_x_die_lvl_nom_lvl2': {'soc_vipr_eza_pins': '0', 'soc_edm_all': '0', 'XXVCCRTC': '1.5', 'HC03_0P77_VNNAON_PCIEPHY_2': '0.77', 'HC04_0P77_VNNAON_PCIEPHY_3': '0.77', 'HC05_0P77_VNNAON_USB2PHY': '0.77', 'HC07_0P77_VNNAON_QUIET2CLK': '0.77', 'LC01_1P8_QUIET2': '1.8', 'LC02_1P8_QUIET2_FUSE': '1.8', 'LC03_1P8_GPCOM01345': '1.8', 'LC04_1P8_USB2PHY': '1.8', 'LC05_1P8_QUIET1_CLKPLL': '1.8', 'LC06_1P8_QUIET1_CNV': '1.8', 'LC07_0P77_VNNAON_CNVDPHY': '0.77', 'LC08_0P77_VNNAON_EDP': '0.77', 'HV01_3P3_USB2PHY': '3.3', 'HV02_1P25_VCCIO': '1.25', 'HV03_1P25_VCCIO_PCIEPHY': '1.25', 'HV04_1P25_VCCIO_CNVISCLK': '1.25', 'HV05_1P25_VCCIO_GPCOM4': '1.25', 'HV06_5P5_VCCFUSE_SOC0': '0', 'HV07_5P5_VCCFUSE_SOC1': '0', 'HV08_1P05_VCCVDD2': '1.05'}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503': {'BASE::soc_all_dft_x_x_pkg_lvl_nom_lvl2': {'soc_allwoec_lvl': '0', 'soc_ec_lvl': '0', 'soc_hpc_lvl': '0', 'XXVCCRTC': '1.5', 'VCC1P8_LC': '1.8', 'VCC1P8_QUIET_1_LC': '1.8', 'VCC1P8_QUIET_2_LC': '1.8', 'VCC3P3_LC': '3.3', 'VNNAON_HC': '0.77', 'VNNAON_QUIET_1_HC': '0.77', 'VNNAON_QUIET_2_HC': '0.77', 'VCCIO_HC': '1.25', 'VCCFPGM_SOC_0_LC': '0.0', 'VCCFPGM_SOC_1_LC': '0.0', 'VCCFPGM_CPU_0_NOM_LC': '0.0', 'VCCFPGM_CPU_1_HV_LC': '0.0', 'VCCFPGM_GCD_LC': '0.0', 'VCCFPGM_IOE_LC': '0.0', 'VDD2_LC': '1.05', 'VCCSA_HC': '0.77', 'VCCIA_HC': '0.2', 'VCCGT_HC': '0.2', 'CORE_EXT_BGREF_VLC': '0.0'}}}]

        Dummy2 = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503',
                        }

        user_pin_comparison = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['1|VNNAON_QUIET_1_HC']
                               }

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_level_diff(TP_sc_1, Dummy2, user_pin_comparison, user_mapping)
        expect = '''
ERROR:Pin 1 not found in ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2. Please check your PinsToMatch tab
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_sortclass_timing_diff(self):

        TP_equal = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': {'BASE::soc_hvm_timing_perpin_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_fab_domain_per_resolved': 2.5e-09, 'c_tap_domain_per_resolved': 1e-08}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501': {'BASE::soc_hvm_timing_perpin_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_ssninclk_ec_per': 2.5e-09, 'c_tap_domain_per': 1e-08}}}]

        Any = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501'
                        }

        Freq_comparison_dict = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['c_fab_domain_per_resolved|c_ssninclk_ec_per']
                                }

        outcsv = 'Print output Sortclass_file_name'

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_timing_diff(TP_equal, Any, Freq_comparison_dict, user_mapping)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_TimToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        outfile_name1 = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        output_file1 = outfile_name1 + '.csv successfully!'
        expect = f'''
{output_file}
{output_file1}
'''
        self.assertTextEqual(p.getvalue(), expect)

        TP1_more_than_TP2 = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU1': {'BASE::soc_hvm_timing_perpin1_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_fab_domain_per_resolved': 2.5e-09, 'c_tap_domain_per_resolved': 2e-08, 'c_tap_domain_per': 1e-08}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1502': {'BASE::soc_hvm_timing_perpin1_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_ssninclk_ec_per': 1e-08, 'c_tap_domain_per': 1e-08}}}]

        Any1 = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU1': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1502'
                        }

        Freq_comparison_dict = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['c_fab_domain_per_resolved|c_ssninclk_ec_per']
                                }

        outcsv = 'Print output Sortclass_file_name'

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_timing_diff(TP1_more_than_TP2, Any1, Freq_comparison_dict, user_mapping)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_TimToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        outfile_name1 = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        output_file1 = outfile_name1 + '.csv successfully!'
        expect = f'''
{output_file}
{output_file1}
'''
        self.assertTextEqual(p.getvalue(), expect)

        TP1_less_than_TP2 = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': {'BASE::soc_hvm_timing_perpin2_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_fab_domain_per_resolved': 1e-08, 'c_tap_domain_per_resolved': 2e-08}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503': {'BASE::soc_hvm_timing_perpin2_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_tap_domain_per_resolved': 2e-08, 'c_ssninclk_ec_per': 2.5e-09, 'c_tap_domain_per': 1e-08}}}]

        Any2 = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU2': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1503'
                        }

        Freq_comparison_dict = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['c_fab_domain_per_resolved|c_ssninclk_ec_per']
                                }

        outcsv = 'Print output Sortclass_file_name'

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_timing_diff(TP1_less_than_TP2, Any2, Freq_comparison_dict, user_mapping)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_TimToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        outfile_name1 = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        output_file1 = outfile_name1 + '.csv successfully!'
        expect = f'''
{output_file}
{output_file1}
'''
        self.assertTextEqual(p.getvalue(), expect)

        # to complete the log.info special case
        TP_sc = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': {'BASE::soc_hvm_timing_perpin_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_fab_domain_per_resolved': 2.5e-09, 'c_tap_domain_per_resolved': 1e-08}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501': {'BASE::soc_hvm_timing_perpin_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_ssninclk_ec_per': 2.5e-09, 'c_tap_domain_per': 1e-08}}}]

        Any = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501'
                        }

        Freq_comparison_dict = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['c_fab_domain_per_resolved|2']
                                }

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_timing_diff(TP_sc, Any, Freq_comparison_dict, user_mapping)
        expect = '''
ERROR:Timing Param 2 not found in ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501. Please check your TimToMatch tab
'''
        self.assertTextEqual(p.getvalue(), expect)

        TP_sc_1 = [{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': {'BASE::soc_hvm_timing_perpin_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_fab_domain_per_resolved': 2.5e-09, 'c_tap_domain_per_resolved': 1e-08}}}, {'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501': {'BASE::soc_hvm_timing_perpin_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400': {'c_ssninclk_ec_per': 2.5e-09, 'c_tap_domain_per': 1e-08}}}]

        Any = 'Sortclass_file_name'

        user_mapping = {'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501'
                        }

        Freq_comparison_dict = {'ARR_ATOM_SXX|ARR_ATOM_SXN': ['1|c_ssninclk_ec_per']
                                }

        with CaptureStdoutLog() as p:
            print()
            Diff([]).sortclass_timing_diff(TP_sc_1, Any, Freq_comparison_dict, user_mapping)
        expect = '''
ERROR:Timing Param 1 not found in ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU. Please check your TimToMatch tab
'''
        self.assertTextEqual(p.getvalue(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_user_input(self):
        tp = [TestProgram(UT_DIR + '/MTSSDSCA2H12A202241/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/MTLXXXXAXH19J20S218/POR_TP/Class_MTL_P68/EnvironmentFile.env')]

        mydir = UT_DIR + '/sort_class_mapping.xlsx'
        with CaptureStdoutLog() as p:
            print()
            Diff(tp).read_userinputlist(mydir)
            # print(Diff(tp).read_userinputlist(mydir))
        expect = '''
{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501', 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_END_X_X_VMIN_3200_G2': 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_ENDSOC_X_X_VMIN_3200_G2', 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_END_X_X_VMAX_4000_G4': 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_ENDSOC_X_X_VMAX_4000_G4', 'NSIO_DP_SXM::ANELB_DP_VMIN_K_END_X_X_X_1620_LONGMV': 'NSIO_DP_SXM::ANELB_DP_VMIN_K_ENDSOC_X_X_X_1620_LONGMV'}
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_ins_detail(self):

        tp = [TestProgram(UT_DIR + '/MTSSDSCA2H12A202241/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/MTLXXXXAXH19J20S218/POR_TP/Class_MTL_P68/EnvironmentFile.env')]

        OPT.userinputlist = UT_DIR + '/sort_class_mapping.xlsx'
        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.ins_detail()

        time_now = datetime.datetime.now()
        outfile_name = str('TestInstanceParamDiff_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        matchfile_name = str('TestInstanceMatchParam_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        matchfile_name = matchfile_name + '.csv'
        output_filename = f'Test Instance Diff Parameter file: {output_file}'
        match_filename = f'Test Instance Match Parameter file: {matchfile_name}'
        final_test_info = f'''{output_filename}
{match_filename}
'''
        expect = '''
{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501', 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_END_X_X_VMIN_3200_G2': 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_ENDSOC_X_X_VMIN_3200_G2', 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_END_X_X_VMAX_4000_G4': 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_ENDSOC_X_X_VMAX_4000_G4', 'NSIO_DP_SXM::ANELB_DP_VMIN_K_END_X_X_X_1620_LONGMV': 'NSIO_DP_SXM::ANELB_DP_VMIN_K_ENDSOC_X_X_X_1620_LONGMV'}
'''
        expect = expect
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_twolevel_diff(self):

        result0 = {'tc1': {'var1': 26,
                           'var2': 27,
                           'var3': 28},
                   'tc2': {'var4': 29},
                   }
        result1 = {'tc1': {'var1': 26,
                           'var2': 28,
                           'var5': 28},
                   'tc3': {'var4': 29},
                   }

        ref0 = {'tc1': {'Test1a'},
                'tc2': {'Test2a'},
                }
        ref1 = {'tc1': {'Test1b'},
                'tc3': {'Test3b'},
                }

        outcsv = "timDiff"

        shnm = "timDiff"

        outcsv1 = "Print output timDiff"

        with MockVar(gadget_helperclass, 'IS_UT', False), \
                CaptureStdoutLog() as p:
            Diff([]).twolevel_diff([result0, result1], [ref0, ref1], outcsv, shnm)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_{}'.format(outcsv1, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        outnew = f'''{output_file}
'''
        expect = f'''Changed:tc1
  UseBy: Test1b
   var2 = 27                                                    + var2 = 28
   var3 = 28                                                    <
                                                                > var5 = 28
Removed: tc2
  UseBy: Test2a
Added:   tc3
  UseBy: Test3b
'''
        expect = expect + outnew
        self.assertTextEqual(p.getvalue(), expect)

        # to complete the log.info special case
        result0 = {'tc1': {'var1': 26,
                           'var2': 27,
                           'var3': 28},
                   'tc2': {'var4': 29},
                   }
        result1 = {'tc1': {'var1': 26,
                           'var2': 28,
                           'var5': 28},
                   'tc3': {'var4': 29},
                   }

        ref0 = {'tc1': {''},
                'tc2': {''},
                }
        ref1 = {'tc1': {''},
                'tc3': {''},
                }

        outcsv = "timDiff"

        shnm = "timDiff"

        outcsv1 = "Print output timDiff"

        with MockVar(gadget_helperclass, 'IS_UT', False), \
                CaptureStdoutLog() as p:
            Diff([]).twolevel_diff([result0, result1], [ref0, ref1], outcsv, shnm)
        time_now = datetime.datetime.now()
        outfile_name = str('{}_{}'.format(outcsv1, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv successfully!'
        outnew = f'''{output_file}
'''
        expect = f'''Changed:tc1
  UseBy: None
   var2 = 27                                                    + var2 = 28
   var3 = 28                                                    <
                                                                > var5 = 28
Removed: tc2
  UseBy: None
Added:   tc3
  UseBy: None
'''
        expect = expect + outnew
        self.assertTextEqual(p.getvalue(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tid_diff(self):
        tp = [TestProgram(UT_DIR + '/MTSSDSCA2H12A202241/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/MTLXXXXAXH19J20S218/POR_TP/Class_MTL_P68/EnvironmentFile.env')]

        OPT.userinputlist = UT_DIR + '/sort_class_mapping.xlsx'
        with TempDir(name=True) as tdir, CaptureStdoutLog() as p:
            print()
            df = Diff(tp)
            df.out = tdir
            df.tid_diff()
        outfile_name = f'Printing sort class tid diff report to: {df.out}.sort_class_tid_diff.csv'
        output_file = f'''{outfile_name}
'''
        expect = '''
{'ARR_ATOM_SXX::LSA_ATOM_VMIN_K_END_NITO_VCCSA_X_F1_L2LRU': 'ARR_ATOM_SXN::LSA_ATOM_VMIN_K_CSNF1_X_VCCSA_F1_1100_L2LRU_1501', 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_END_X_X_VMIN_3200_G2': 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_ENDSOC_X_X_VMIN_3200_G2', 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_END_X_X_VMAX_4000_G4': 'MIO_DDR5AC_SXM::CPGC_DDR5_FUNC_K_ENDSOC_X_X_VMAX_4000_G4', 'NSIO_DP_SXM::ANELB_DP_VMIN_K_END_X_X_X_1620_LONGMV': 'NSIO_DP_SXM::ANELB_DP_VMIN_K_ENDSOC_X_X_X_1620_LONGMV'}
'''
        expect = expect + output_file
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)


class TestDiff(TestCase):

    def test_uniqport_dict(self):
        d1 = {'Port#0 connection': 'GoTo1',
              'Port#1 connection': 'GoTo1',
              'Port#-2 connection': 'GoTo1',
              'Port#3 connection': 'blah',
              'Port#4 connection': 'blah',
              'Port#-1 connection': 'blah2'}
        d2 = {}
        r1 = Diff([]).uniqport_dict(d1, d2)
        self.assertEqual(r1, {'Port#-1 connection': 'blah2',
                              'Port#-2,0,1 connection': 'GoTo1',
                              'Port#3,4 connection': 'blah'})
        r1 = Diff([]).uniqport_dict(d1, d1)
        self.assertEqual(r1, d1)

    def test_is_skip_module(self):
        # default
        with MockVar(OPT, 'module', None):
            self.assertEqual(Diff([]).is_skip_module('AA'), False)

        with MockVar(OPT, 'module', 'ARR'):
            self.assertEqual(Diff([]).is_skip_module('  ARR_CCF'), False)
            self.assertEqual(Diff([]).is_skip_module('ARR_CCF'), False)
            self.assertEqual(Diff([]).is_skip_module('FUN_CCF'), True)
            self.assertEqual(Diff([]).is_skip_module('FUNARR_CCF'), True)

        with MockVar(OPT, 'module', 'ARR|SCN'):
            self.assertEqual(Diff([]).is_skip_module('  ARR_CCF'), False)
            self.assertEqual(Diff([]).is_skip_module('ARR_CCF'), False)
            self.assertEqual(Diff([]).is_skip_module('FUN_CCF'), True)
            self.assertEqual(Diff([]).is_skip_module('SCN_CCF'), False)

    def test_dict_skip_module(self):
        # default
        ind = {'ARR_CCF': 1,
               '   ARR_CCF': 2,
               'FUN_CCF': 3,
               'FUNARR_CCF': 4,
               'SCN_CCF': 5}
        with MockVar(OPT, 'module', None):
            self.assertEqual(Diff([]).dict_skip_module(ind), ind)

        with MockVar(OPT, 'module', 'ARR'):
            self.assertEqual(Diff([]).dict_skip_module(ind), {'ARR_CCF': 1,
                                                              '   ARR_CCF': 2})

        with MockVar(OPT, 'module', 'ARR|SCN'):
            self.assertEqual(Diff([]).dict_skip_module(ind), {'ARR_CCF': 1,
                                                              '   ARR_CCF': 2,
                                                              'SCN_CCF': 5})

    def atest_is_skip_flow(self):
        # default
        with MockVar(OPT, 'only', None), MockVar(OPT, 'skip', None):
            self.assertEqual(Diff([]).is_skip_flow('1'), False)
        with MockVar(OPT, 'only', None), MockVar(OPT, 'skip', None):
            self.assertEqual(Diff([]).is_skip_flow('1'), False)
        # only
        with MockVar(OPT, 'only', ['1A', '1B']), MockVar(OPT, 'skip', []):
            self.assertEqual(Diff([]).is_skip_flow('1a'), False)
            self.assertEqual(Diff([]).is_skip_flow('2'), True)
        # skip
        with MockVar(OPT, 'only', []), MockVar(OPT, 'skip', ['1A', '1B']):
            self.assertEqual(Diff([]).is_skip_flow('1a'), True)
            self.assertEqual(Diff([]).is_skip_flow('2'), False)
        # both
        with MockVar(OPT, 'only', ['1', '2']), MockVar(OPT, 'skip', ['2']):
            self.assertEqual(Diff([]).is_skip_flow('1'), False)
            self.assertEqual(Diff([]).is_skip_flow('2'), True)
            self.assertEqual(Diff([]).is_skip_flow('3'), True)

    def test_strip_tn(self):
        self.assertEqual(Diff.strip_tn('blah_blah_3600_X_1233', '3600'), 'blah_blah_*_X_*')
        self.assertEqual(Diff.strip_tn('blah_blah_3600_X_1233', None), 'blah_blah_3600_X_*')

    def test_show_dir_diff(self):
        with TempDir(name=True) as tdir1, TempDir(name=True) as tdir2:
            File(join(tdir1, 'file_same')).touch('line1\nline2\n')
            File(join(tdir2, 'file_same')).touch('line1\nline2\n')
            File(join(tdir1, 'file_diff')).touch('line1\nline2\n')
            File(join(tdir2, 'file_diff')).touch('line1a\nline2a\n')
            File(join(tdir1, 'file_uniqa')).touch('line1\nline2\n')
            File(join(tdir2, 'file_uniqb')).touch('line1a\nline2a\n')
            File(join(tdir1, 'TPIE.sig')).touch('line1\nline2\n')
            File(join(tdir2, 'TPIE.sig')).touch('line1a\nline2a\n')
            File(join(tdir1, 'main.flw')).touch('line1\nline2\n')
            File(join(tdir2, 'main.flw')).touch('line1a\nline2a\n')

            mkdirs(join(tdir1, 'Modules'))
            with CaptureStdoutLog() as p:
                Diff([]).show_dir_diff(tdir1, tdir2, '', ign={'TPIE.sig'})
            expect = '''Legend: (+add_lines/-removed_lines/changed_lines)
Changed +0/-0/2              file_diff
Missing                      file_uniqa
Added                        file_uniqb
'''
            self.assertTextEqual(p.getvalue(), expect)

    def test_smart_strip(self):
        with TempDir(name=True, chdir=True):
            # Normal file
            File('somefile.mtpl').touch('''
# comment
iCGL_TpAltName = 1
<Suite> = 1
someline
''')
            Diff.smart_strip('somefile.mtpl', 'somefile.mtpl2')

            expect = '''
iCGL_TpAltName = 1
<Suite> = 1
someline

'''
            self.assertTextEqual(File('somefile.mtpl2').read(), expect)

            # PGMRule_Base.txt file
            File('PGMRule_Base.txt').touch('''
# comment
iCGL_TpAltName = 1
<Suite> = 1
someline
''')
            Diff.smart_strip('PGMRule_Base.txt', 'PGMRule_Base.txt2')

            expect = '''
<Suite> = 1
someline

'''
            self.assertTextEqual(File('PGMRule_Base.txt2').read(), expect)

            # LIPORT file
            File('LIPORT_A.xml').touch('''
# comment
iCGL_TpAltName = 1
<Suite> = 1
someline
''')
            Diff.smart_strip('LIPORT_A.xml', 'LIPORT_A.xml2')

            expect = '''
iCGL_TpAltName = 1
someline

'''
            self.assertTextEqual(File('LIPORT_A.xml2').read(), expect)

    def test_diff_arc(self):
        with TempDir(name=True, chdir=True):
            File('a').touch('''
line1 This is very long abc def ghi the quick brown fox jumps
line2 torch line long abc def ghi the quick brown fox jumps
line3
line4 long abc def ghi the quick brown fox jumps
line5
line6 long abc def ghi the quick brown fox jumps
''')
            File('b').touch('''
line1 This is very long abc def ghi the quick brown fox jumps
line2a torch line long abc def ghi the quick brown fox jumps
line3
new line altogether long abc def ghi the quick brown fox jumps
new line altogether long abc def ghi the quick brown fox jumps
line5
''')
            res = Diff.diff_arc('a', 'b')
            self.assertEqual(res, '+1/-1/2')
            res = Diff.diff_arc('a', 'a')
            self.assertEqual(res, '+0/-0/0')
            File('c').touch()
            res = Diff.diff_arc('a', 'c')
            self.assertEqual(res, '+0/-7/0')

    def test_port_trace(self):
        data = ['MAIN', 'port=-2 of arr', 'subflow', 'port=1 of scan']
        self.assertEqual(Diff.port_trace(data), 'c-2c1')

    def test_filter_shared(self):
        data = {'ab': '12',
                '_EDCKIL': 'skip',
                'timing': 'VCCSA_max_SHARED_304548797EC27868A603555E4923',
                'levels': 'lvl_SHARED_304548797EC27868A603555E4923'}
        self.assertEqual(Diff.filter_shared(data),
                         {'ab': '12',
                          'timing': 'VCCSA_max_SHARED_',
                          'levels': 'lvl_SHARED_'})

    def test_port2dict(self):
        self.maxDiff = None
        data = {-2: {'GoTo': 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'SetBin': 'SoftBins.b90999901_fail_FAIL_DPS_ALARM', 'PassFail': 'Fail'},
                -1: {'GoTo': 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'SetBin': 'SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE', 'PassFail': 'Fail'},
                0: {'GoTo': 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE::n90930269_fail_CTRL_X_UF_E_ALARM_X_X_X_X_CHKFLOW_0', 'PassFail': 'Fail'},
                1: {'GoTo': 'CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN', 'IncrementCounters': 'TPI_BASE::p99930270_pass_CTRL_X_UF_E_ALARM_X_X_X_X_CHKFLOW_1', 'PassFail': 'Pass'},
                2: {'Return': '1', 'IncrementCounters': 'TPI_BASE::fail_CTRL_X_UF_E_ALARM_X_X_X_X_CHKFLOW_2', 'PassFail': 'Fail'},
                999: 'CTRL_X_UF_E_ALARM_X_X_X_X_CHKFLOW'}
        self.assertEqual(Diff.port2dict(data),
                         {'Port#-1 PassFail': 'Fail',
                          'Port#-1 SetBin': '90989801',
                          'Port#-1 connection': 'GoTo CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN',
                          'Port#-2 PassFail': 'Fail',
                          'Port#-2 SetBin': '90999901',
                          'Port#-2 connection': 'GoTo CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN',
                          'Port#0 IncrementCounters': '90930269',
                          'Port#0 PassFail': 'Fail',
                          'Port#0 connection': 'GoTo CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN',
                          'Port#1 IncrementCounters': '99930270',
                          'Port#1 PassFail': 'Pass',
                          'Port#1 connection': 'GoTo CTRL_X_SCREEN_K_ALARM_X_X_X_X_BIN',
                          'Port#2 IncrementCounters': 'TPI_BASE::fail_CTRL_X_UF_E_ALARM_X_X_X_X_CHKFLOW_2',
                          'Port#2 PassFail': 'Fail',
                          'Port#2 connection': 'Return 1',
                          'Test': 'CTRL_X_UF_E_ALARM_X_X_X_X_CHKFLOW'})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
