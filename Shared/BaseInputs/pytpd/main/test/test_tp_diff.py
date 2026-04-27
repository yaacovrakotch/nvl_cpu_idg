#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tp_diff.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, patch, Mock
from main.tp_diff import *
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


class TestArgs(TestCase):

    def test_basic(self):
        # Run full tpdiff, no pickle
        cmd = f'tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env -nopickle'
        with MockVar(sys, "argv", cmd.split()), \
                CaptureStdoutLog() as p:
            TPDiff().main()
        result = p.getvalue()
        print(result)

        # with pickle
        cmd = f'tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env'
        with MockVar(sys, "argv", cmd.split()), \
                CaptureStdoutLog() as p:
            TPDiff().main()
        self.assertEqual(sha1(trimut(p.getvalue())), sha1(trimut(result)))    # If this fails it means saved pickle is not correct. May need to delete all pickle files

        # error case - invalid args - missing 2nd tp
        cmd = f'tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env'
        with MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                TPDiff().main()
        self.assertIn('Error:', p.getvalue())

        # -flows
        cmd = f'tp_diff.py -flows'
        with MockVar(sys, "argv", cmd.split()), \
                CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                TPDiff().main()
        self.assertIn('Flows in order', p.getvalue())

    def test_skip_only(self):
        # skip all
        with MockVar(OPT, 'only', None), MockVar(OPT, 'skip', None):   # This is needed so that other tests will not be affected
            cmd = f'tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env -only 9a -skip 9a'
            with MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                TPDiff().main()
            # print(p.getvalue())
            self.assertEqual(len(trimut(p.getvalue())), 4)

    def test_nochange(self):
        total = 16

        # specify a module that does not exist, so everything is no change
        with MockVar(OPT, 'module', None):
            cmd = f'tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env -module JDR'
            with MockVar(sys, "argv", cmd.split()), \
                    CaptureStdoutLog() as p:
                TPDiff().main()
            print(p.getvalue())
            self.assertEqual(len([x for x in p.getvalue().split('\n') if x == 'No change']), total - 1)    # minus 1 because of Top level files skipped

        # without pickle, same input
        cmd = f'tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env -nopickle'
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
        cmd = f'tp_diff.py f1 f2 -sdiff -W 10'
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

    @with_(TempDir, chdir=True)
    def test_otpl(self):
        File('f1').touch('a;\nb;\nc;\ne;\n')
        File('f2').touch('a;\nB;\ne;\n')
        cmd = f'tp_diff.py f1 f2 -otpl diff'
        with MockVar(sys, "argv", cmd.split()), CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                print()
                TPDiff().main()

        expect = '''
2,3c2
< b;
< c;
---
> B;
'''
        self.assertTextEqual(p.getvalue(), expect)


class TestMain(TestCase):

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
        cmd = f'tp_diff.py {UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1b/TPL/EnvironmentFile.env -lvl BASE::tc1 -value'
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

    def test_patreorder_diff(self):
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

    def test_fullpat_diff(self):
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

    def test_plb_diff(self):
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

    def test_ctrbin_diff(self):
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

    def test_port_diff(self):
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

    def test_passfail_diff(self):
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

    def test_allports_diff(self):
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

    def test_ins_diff(self):
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

    def test_lvl_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).lvl_diff()
        expect = '''
Added:   BASE::tc3
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tim_diff(self):
        tp = [TestProgram(UT_DIR + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).tim_diff()
        expect = '''
Changed: BASE::tc2
  UseBy: ARR  CCB
   p_vcc_gb_type = 0.1                                          + p_vcc_gb_type = 0.4
   tester_gb_hc = 5.5                                           + tester_gb_hc = 22.0
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_ins_detail(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).ins_detail()
        expect = '''
1st line is TP1: Simple1a
2nd line is TP2: Simple1b

ARR CCA:
     _CORNER = max
   + _CORNER = nom
     level = BASE::DDR_univ_lvl_max_lvl
   + level = BASE::DDR_univ_lvl_nom_lvl
     timings = BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100
   + timings = BASE::tc1

ARR CCB:
     base_number = 2161
   + base_number = 2162
     timings = BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100
   + timings = BASE::tc2
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_basenumber_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).basenumber_diff()
        expect = '''
ARR CCB = 2161                                               + ARR CCB = 2162
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_ins_detail_ut(self):
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

        with MockVar(tp[0].mtpl, 'iter_flows', Mock(return_value=data1)),\
                MockVar(tp[1].mtpl, 'iter_flows', Mock(return_value=data2)),\
                CaptureStdoutLog() as p:
            print()
            obj.ins_detail()
        expect = '''
1st line is TP1: Simple1a
2nd line is TP2: Simple1b

m1 test1:
m2 test2:
     diff = val1
   + diff = val1a
     unq1 = val2
   < (none)
     (none)
   > unq2 = val2

m3 test3:
     diff = val1
   + diff = val1a
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tid_diff(self):
        tp = [TestProgram(UT_DIR_REPO + '/Simple1a/TPL/EnvironmentFile.env'),
              TestProgram(UT_DIR_REPO + '/Simple1b/TPL/EnvironmentFile.env')]

        with CaptureStdoutLog() as p:
            print()
            Diff(tp).tid_diff()
        expect = '''
ARR,max,NONE,EDC tids = 1                                    <
ARR,nom,NONE,EDC tids = 1                                    + ARR,nom,NONE,EDC tids = 2
PTH,nom,1100,EDC tids = 3                                    <
PTH,nom,1200,EDC tids = 3                                    <
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # specific module
        obj = Diff(tp)
        obj.robj_mod = re.compile('^ARR')
        with CaptureStdoutLog() as p:
            print()
            obj.tid_diff()
        expect = '''
ARR,max,NONE,EDC tids = 1                                    <
ARR,nom,NONE,EDC tids = 1                                    + ARR,nom,NONE,EDC tids = 2
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tid_diff2(self):
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
            self.assertEqual(len(output.split('\n')), 34)
            output = open(join(tdir, 'Simple1b.tid.csv')).read()
            self.assertEqual(len(output.split('\n')), 26)

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
ARR,max,NONE,EDC tids = 1                                    <
ARR,nom,NONE,EDC tids = 1                                    + ARR,nom,NONE,EDC tids = 2
PTH,nom,1100,EDC tids = 3                                    <
PTH,nom,1200,EDC tids = 3                                    <
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
                                                             > ARR,max,NONE,EDC tids = 1
ARR,nom,NONE,EDC tids = 2                                    - ARR,nom,NONE,EDC tids = 1
                                                             > PTH,nom,1100,EDC tids = 3
                                                             > PTH,nom,1200,EDC tids = 3
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tp_files(self):
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

    def test_twolevel_diff(self):
        d1 = {'tc1': {'var1': 26,
                      'var2': 27,
                      'var3': 28},
              'tc2': {'var4': 29},
              }
        d2 = {'tc1': {'var1': 26,
                      'var2': 28,
                      'var5': 28},
              'tc3': {'var4': 29},
              }

        ref1 = {'tc1': {'Test1a'},
                'tc2': {'Test2a'},
                'tc3': {'Test3a'}}
        ref2 = {'tc1': {'Test1b'},
                'tc2': {'Test2b'},
                'tc3': {'Test3b'}}
        with CaptureStdoutLog() as p:
            Diff([]).twolevel_diff([d1, d2], [ref1, ref2])
        expect = '''Changed: tc1
  UseBy: Test1b
   var2 = 27                                                    + var2 = 28
   var3 = 28                                                    <
                                                                > var5 = 28
Removed: tc2
  UseBy: Test2a
Added:   tc3
  UseBy: Test3b
'''
        self.assertTextEqual(p.getvalue(), expect)

        # no change
        with CaptureStdoutLog() as p:
            Diff([]).twolevel_diff([d1, d1], [{}, {}])
        self.assertEqual(p.getvalue(), 'No change\n')

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


class TestPairModule(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tp1 = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        tp2 = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')

        # setup the data
        pat1 = {'list1': {'d0000136W0003667K',
                          'd0000137W0003668K',
                          'd0000138W0003669K'},
                'list3': {'d0000136W0001667K',
                          'd0000137W0001668K',
                          'd0000137W0001669K',
                          'd0000137W0001670K',
                          'd0000138W0001671K'},
                }

        pat2 = {'list1': {'d0000136W0000667K',
                          'd0000137W0000668K',
                          'd0000138W0000679K'},
                'list3a': {'d0000136W0001667K',
                           'd0000137W0001678K',
                           'd0000138W0001679K'},
                'list3b': {'d0000136W0001667K',
                           'd0000137W0001668K',
                           'd0000137W0002669K',
                           'd0000137W0001670K',
                           'd0000138W0001671K'},
                'list3c': {'d0000136W0001667K',   # most match
                           'd0000137W0001668K',
                           'd0000137W0001669K',
                           'd0000137W0001670K',
                           'd0000138W0001671K'},
                }

        data1 = [('FUN', 'test1', {'patlist': 'list1'}),
                 ('ARR', 'test1', {'patlist': 'list3'}),    # case1: same name
                 ('SIO', 'test3', {'patlist': 'list1', 'timing': 1}),    # pick best one
                 ]

        data2 = [('FUN', 'test1', {'patlist': 'list1'}),
                 ('AR1', 'test1', {'patlist': 'list3a'}),
                 ('AR2', 'test2', {'patlist': 'list3b', 'timing': 1}),
                 ('MIO', 'test3a', {'patlist': 'list1'}),
                 ]

        OPT.inspect = True   # Display messages
        with MockVar(tp1.plists, 'get_pats_from_plb', lambda x: pat1[x]),\
                MockVar(tp2.plists, 'get_pats_from_plb', lambda x: pat2[x]),\
                MockVar(tp1.mtpl, 'iter_flows', Mock(return_value=data1)),\
                MockVar(tp2.mtpl, 'iter_flows', Mock(return_value=data2)):

            # main case
            pm = PairModule(tp1, tp2)
            self.assertEqual(pm.map, {'FUN': {'FUN'},
                                      'ARR': {'AR2', 'AR1'}})
            self.assertEqual(pm.uniq[0], {'SIO'})
            self.assertEqual(pm.uniq[1], {'MIO'})


class TestPairInstance(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tp1 = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        tp2 = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')

        # setup the data
        pat1 = {'list1': {'d0000136W0000667K',
                          'd0000137W0000668K',
                          'd0000138W0000669K'},
                'list3': {'d0000136W0001667K',
                          'd0000137W0001668K',
                          'd0000137W0001669K',
                          'd0000137W0001670K',
                          'd0000138W0001671K'},
                }

        pat2 = {'list1': {'d0000136W0000667K',
                          'd0000137W0000668K',
                          'd0000138W0000679K'},
                'list3a': {'d0000136W0001667K',
                           'd0000137W0001678K',
                           'd0000138W0001679K'},
                'list3b': {'d0000136W0001667K',
                           'd0000137W0001668K',
                           'd0000137W0002669K',
                           'd0000137W0001670K',
                           'd0000138W0001671K'},
                'list3c': {'d0000136W0001667K',   # most match
                           'd0000137W0001668K',
                           'd0000137W0001669K',
                           'd0000137W0001670K',
                           'd0000138W0001671K'},
                }

        dat1 = [('ARR', 'test1', {'patlist': 'list1'}),    # case1: same name
                ('ARR', 'test2a', {'patlist': 'list3',
                                   'setting_values': 'a'}),   # case2: test2a w/ test2b collapsed
                ('ARR', 'test2b', {'patlist': 'list3',
                                   'corner_identifier': 'b'}),
                ('ARR', 'test3', {'patlist': 'list3', 'timing': 1}),    # pick best one
                ]

        dat2 = [('ARR', 'test1', {'patlist': 'list1'}),
                ('ARR', 'test2', {'patlist': 'list3a', 'timing': 1}),
                ('ARR', 'test3a', {'patlist': 'list3a'}),
                ('ARR', 'test3b', {'patlist': 'list3b'}),
                ('ARR', 'test3c', {'patlist': 'list3c'}),
                ]

        OPT.inspect = True   # Display messages
        with MockVar(tp1.plists, 'get_pats_from_plb', lambda x: pat1[x]),\
                MockVar(tp2.plists, 'get_pats_from_plb', lambda x: pat2[x]),\
                MockVar(tp1.mtpl, 'iter_flows', Mock(return_value=dat1)),\
                MockVar(tp2.mtpl, 'iter_flows', Mock(return_value=dat2)):

            # case1 - TP-TP (no auto)
            pi = PairInstance(tp1, tp2)
            self.assertEqual(pi.map, {('ARR', 'test1'): ('ARR', 'test1')})
            print(pi.remaining)
            self.assertEqual(pi.remaining, [{('ARR', 'test2a'),
                                             ('ARR', 'test3')},
                                            {('ARR', 'test2'),
                                             ('ARR', 'test3a'),
                                             ('ARR', 'test3b'),
                                             ('ARR', 'test3c')}])

            # case2 - auto pair
            with MockVar(OPT, 'auto', True):
                pi = PairInstance(tp1, tp2)
                self.assertEqual(pi.map, {('ARR', 'test1'): ('ARR', 'test1'),
                                          ('ARR', 'test2a'): ('ARR', 'test3c'),
                                          ('ARR', 'test3'): ('ARR', 'test3b')})
                print(pi.remaining)
                self.assertEqual(pi.remaining, [set(),
                                                {('ARR', 'test2'),
                                                 ('ARR', 'test3a'),
                                                 }])

            # case3 - specific setting


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
