#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tp_audit.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.shell import IS_UNIX, SystemCall
from gadget.gizmo import MockVar, with_
from gadget.tputil import trimut
from gadget.helperclass import CaptureStdout, CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.printmore import Dumper
from pprint import pprint
from main.tp_audit import *
from tp.testprogram import Env
from tp.test.test_timlvl import TestSharedUsrv
from mod.setting import cfg
from os.path import join, normpath
import sys
import os
import shutil


class TestAudit(TestCase):

    def test_checks(self):
        # no arguments
        cmd = 'tp_audit.py -patrev'.split()
        with MockVar(sys, "argv", cmd):
            with self.assertRaises(SystemExit):
                TPInfo().main()

        # invalid input env arguments
        cmd = 'tp_audit.py /notfound.env -patrev'.split()
        with MockVar(sys, "argv", cmd):
            with self.assertRaisesRegex(ErrorUser, 'does not exist'):
                TPInfo().main()

    def test_pickle(self):
        envfile = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir):
            TestProgram(envfile).pickle_init()
            pfile = list(os.listdir(tdir))[0]

            cmd = f'tp_audit.py -pickle {tdir}/{pfile}'
            with MockVar(sys, "argv", cmd.split()), \
                    CaptureStdout() as p:
                with self.assertRaises(SystemExit):
                    print()
                    TPInfo().main()
            result = p.getvalue()
            expect = f'''
rev     : {TestProgram.pickle_rev()}
env     : {Env.xpath(normpath(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'))}
stpl    : {Env.xpath(normpath(f'{UT_DIR_REPO}/Simple1/TPL/SubTestPlan_CLASS_TGLH81.stpl'))}
soc     : None
tpl     : {Env.xpath(normpath(f'{UT_DIR_REPO}/Simple1/TPL/BaseTestPlan.tpl'))}
allplist: None
loc     : CLASSHOT
allpats : False
vars    :
'''
        # remove mtimes - problematic across branches
        result = '\n'.join(x for x in result.split('\n') if not x.startswith('mtimes'))
        self.assertTextEqual(Env.xpath(result), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_patrev(self):
        path = f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env'
        cmd = f'tp_audit.py {Env.xpath(path)} -patrev'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        print(p.getvalue())
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 190)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_vecmem(self):
        path = f'{UT_DIR}/MTLXXXXXXX39A0KSXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env'
        cmd = f'tp_audit.py {Env.xpath(path)} -vecmem'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        expect = '''
Patterns with no vecmem info: 0
Vecmem Summary per domain:
ALL_DPIN_MTL_P         1000
CPU_FAB          1708518144
GCD_FAB           339665650
IOE_FAB           638324369
SOC_FAB           740960747
IOEP_FAB_ALL          46240
CPU_TAP           234631885
GCD_TAP            33553154
IOE_TAP           322626548
SOC_TAP           447649642
IOEP_TAP_ALL         146850
'''
        self.assertTextEqual('\n'.join(result), expect)

        # missing pats
        path = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        cmd = f'tp_audit.py {Env.xpath(path)} -vecmem'.split()
        with MockVar(sys, "argv", cmd),\
                CaptureStdout() as p,\
                MockVar(Env, 'get_plist_paths', Mock(return_value=[])):
            TPInfo().main()
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 49)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, chdir=True)
    def test_fix(self):
        File('a.mtpl').touch('''
Increment AA:: b256;
Increment AA::b256;
''')
        path = f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env'
        cmd = f'tp_audit.py {Env.xpath(path)} -fix'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(TestProgram, 'get_all_mtpl_from_stpl', Mock(return_value=['a.mtpl'])):
            TPInfo().main()
        expect = '''
Increment AA::b256;
Increment AA::b256;
'''
        self.assertTextEqual(File('a.mtpl').read(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_plist(self):
        path = f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env'
        cmd = f'tp_audit.py {Env.xpath(path)} -plist'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        print(p.getvalue())
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 216)

        # -plist -out
        with TempDir(name=True) as tdir:
            cmd = f'tp_audit.py {Env.xpath(path)} -plist -out {tdir}'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()
            self.assertEqual(len(os.listdir(tdir)), 216)

    def test_soc(self):
        # list all groups
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -soc {UT_DIR_REPO}/Simple1/TPL/BGA.soc'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
AUDCLK 01.025     ALL
BUDCLK 01.026     ALL
CUDCLK 01.016 [U] _NO_DOMAIN_
'''
        self.assertTextEqual(p.getvalue(), expect)

        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/PinDefinitions.pin -soc {UT_DIR_REPO}/Simple1/TPL/BGA.soc'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        self.assertTextEqual(p.getvalue(), expect)

    def test_alttc(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -alttc'.split()
        with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
            print()
            TPInfo().main()
        self.assertIn('Skipping ALTTC', p.getvalue())

    def test_pin(self):
        # list all groups
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -pin list'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
Domain   ALL     1
Resource DPin    3
Group    all_dmn 2
'''
        self.assertTextEqual(p.getvalue(), expect)

        # list all resources and their domains
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -pin dpin'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
AUDCLK Domains:  ALL
BUDCLK Domains:  ALL
CUDCLK Domains:  _NO_DOMAIN_
'''
        self.assertTextEqual(p.getvalue(), expect)

        # given a pin list groups they belong
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -pin AUDCLK'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
AUDCLK Found in ALL
AUDCLK Found in all_dmn
'''
        self.assertTextEqual(p.getvalue(), expect)

        # given a group, display the flattened pins
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -pin all_dmn'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
AUDCLK Domains:  ALL
BUDCLK Domains:  ALL
'''
        self.assertTextEqual(p.getvalue(), expect)

        # input is .pin, same as above
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/PinDefinitions.pin -pin all_dmn'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        self.assertTextEqual(p.getvalue(), expect)

    def test_plbdependent(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -plbdependent'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        self.assertTextEqual(p.getvalue(), '{}\n')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_unused_pat(self):
        cmd = f'tp_audit.py {UT_DIR}/Simple5pat/POR_TP/TGLH81/EnvironmentFile.env -unused_pat'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        self.assertEqual(len(trimut(p.getvalue())), 37)

        # out to file
        with TempDir(name=True) as tdir:
            cmd = f'tp_audit.py {UT_DIR}/Simple5pat/POR_TP/TGLH81/EnvironmentFile.env -unused_pat -out {tdir}/a.csv'.split()
            with MockVar(sys, "argv", cmd), CaptureStdout() as p:
                TPInfo().main()
            self.assertEqual(len(trimut(p.getvalue())), 0)
            self.assertEqual(len(File(f'{tdir}/a.csv').read().split('\n')), 38)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_used_pat(self):
        cmd = f'tp_audit.py {UT_DIR}/Simple5pat/POR_TP/TGLH81/EnvironmentFile.env -used_pat'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        self.assertEqual(len(trimut(p.getvalue())), 8)

        # out to file
        with TempDir(name=True) as tdir:
            cmd = f'tp_audit.py {UT_DIR}/Simple5pat/POR_TP/TGLH81/EnvironmentFile.env -used_pat -out {tdir}/a.csv'.split()
            with MockVar(sys, "argv", cmd), CaptureStdout() as p:
                TPInfo().main()
            self.assertEqual(len(trimut(p.getvalue())), 0)
            self.assertEqual(len(File(f'{tdir}/a.csv').read().split('\n')), 9)

    def test_findplist(self):
        # given pattern
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -findplist g2026521W2371456I_NW_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_Ram_Stream_Wrrd'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        expect = f"""-i- Finding [g2026521W2371456I_NW_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_Ram_Stream_Wrrd] from all loaded plists...

File: {Env.xpath(normpath(f'{UT_DIR_REPO}/Simple1/TPL/plists/fuse.plist'))}
GlobalPList cpu_fuse_debug_babystep_stream [PreBurstPList list_fuse_tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0] [PostBurst tgl_pst_W9999993H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0] [Flatten]
FOUND >>> Pat g2026521W2371456I_NW_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_Ram_Stream_Wrrd;
"""
        self.assertTextEqual(p.getvalue(), expect)

        # given plist
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -findplist cpu_fuse_debug_babystep_stream'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        expect = f"""-i- Finding [cpu_fuse_debug_babystep_stream] from all loaded plists...

File: {Env.xpath(normpath(f'{UT_DIR_REPO}/Simple1/TPL/plists/fuse.plist'))}
FOUND >>> GlobalPList cpu_fuse_debug_babystep_stream [PreBurstPList list_fuse_tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0] [PostBurst tgl_pst_W9999993H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0] [Flatten]
"""
        self.assertTextEqual(p.getvalue(), expect)

    def test_catplist(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -catplist'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        self.assertEqual(len(trimut(p.getvalue())), 164)

    def test_checkpatlist(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -checkpatlist'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 0)

        #  not found
        from tp.plist import Plists
        with MockVar(Plists, 'get_plb_map', Mock(return_value={})):
            with MockVar(sys, "argv", cmd), CaptureStdout() as p:
                TPInfo().main()
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 4)

    def test_stats_fast(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -stats'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        print(p.getvalue())
        self.assertIn('pgmrule lines', p.getvalue())

        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -stats -nopickle'.split()
        with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
            TPInfo().main()
        print(p.getvalue())
        self.assertIn('Completed Levels equations evaluations', p.getvalue())
        self.assertIn('pgmrule lines', p.getvalue())

        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -stats2'.split()
        with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
            TPInfo().main()

    def test_lvl_list(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -lvl_list ANY'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
c_vccddq_vload_prog       = 144V      BASE::tc1
c_vccddq_vload_prog       =  56.1V    BASE::tc2
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_lvl_tc(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -lvl_tc BASE::tc1'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
pin=FIVR_VDDQ_VL_LC        param=c_vccddq_vload_prog            val=144.000V eqn=hc_vcc_gb+p_lvl+cl_qa_flag

Equations:
tper                        2V          2
p_lvl                      88V          88V
p_vccio_spec                1.2V        1.2V
p_prim_1p8_spec            20mV         ccf_gb_vlc
c_vccddq_vload_prog       144V          hc_vcc_gb+p_lvl+cl_qa_flag
ter1                        6V          tper==1?5V:6V
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tim_tc(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_tc BASE::tc1'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
tper                        2S          toInteger(2)
p_vcc_gb_type              99S          99V
p_vccio_spec                1.2S        1.2V
p_prim_1p8_spec            20mS         ccf_gb_vlc
tester_gb_hc              5445S         hc_vcc_gb*p_vcc_gb_type*cl_qa_flag
ter1                        6S          tper==1?5V:6V
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tim_list(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_list DISP'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 7)

        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_list tper'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 2)

        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_list tperx'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        self.assertIn('NOT_FOUND', p.getvalue())

        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_list ANY'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        self.assertEqual(len(result), 2)

    def test_lvl_ps(self):
        # display
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -lvl_ps VForce'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        expect = '''
Pin                       var/val                 VForce      Equation                TestCondition
FIVR_VDDQ_VL_LC           c_vccddq_vload_prog     144.000     hc_vcc_gb+p_lvl+cl_qa_flag BASE::tc1
all_clock_pins_no_stf     0V                       0.000                              BASE::tc1
FIVR_VDDQ_VL_LC           c_vccddq_vload_prog     56.100      hc_vcc_gb+p_lvl+cl_qa_flag BASE::tc2
all_clock_pins_no_stf     0V                       0.000                              BASE::tc2
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # outfile
        with TempDir(name=True) as tdir:
            cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -lvl_ps VForce,VIH -out {tdir}/a'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()
            expect = '''Pin,Var/Val,VForce,Equation,TestCondition
FIVR_VDDQ_VL_LC,c_vccddq_vload_prog,144.0,hc_vcc_gb+p_lvl+cl_qa_flag,BASE::tc1
all_clock_pins_no_stf,0V,0.0,,BASE::tc1
FIVR_VDDQ_VL_LC,c_vccddq_vload_prog,56.1,hc_vcc_gb+p_lvl+cl_qa_flag,BASE::tc2
all_clock_pins_no_stf,0V,0.0,,BASE::tc2'''
            self.assertTextEqual(File(f'{tdir}/a.VForce.csv').read(), expect)
            expect = '''Pin,Var/Val,VIH,Equation,TestCondition
all_clock_pins_no_stf,0V,0.0,,BASE::tc1
all_clock_pins_no_stf,0V,0.0,,BASE::tc2'''
            self.assertTextEqual(File(f'{tdir}/a.VIH.csv').read(), expect)

    def test_tid_find(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tid_find 2371469_00'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
Found 2371469_00 in: SCN,nom,NONE,EDC CCB cpu_fuse_read_special_x

patlist to filename map:
cpu_fuse_read_special_x {''' + "'" + Env.xpath(normpath(f'{UT_DIR_REPO}/Simple1/TPL/plists/fuse.plist')) + "'}\n"

        self.assertTextEqual(Env.xpath(trimut(p.getvalue(), True, True)), expect)
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tid_find 2371469_01'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
tid 2371469_01 is not found in flow
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tid(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tid ALL'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
Summary:
========
1. ARR,nom,NONE,EDC                       2 tids
2. SCN,nom,NONE,EDC                       6 tids

TestInstances:
==============
1. ARR,nom,NONE,EDC                       2 tids
      1 CCA                                                                              shops_L_list
      1 CCB                                                                              shops_H_list
2. SCN,nom,NONE,EDC                       6 tids
      3 CCA                                                                              cpu_fuse_read_hvm_x
      3 CCB                                                                              cpu_fuse_read_special_x

Patterns:
=========
1. ARR,nom,NONE,EDC                       2 tids
   1.1. shops_H_list:
      1.1.1. g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH
   1.2. shops_L_list:
      1.2.1. g2294511W1466650I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL
2. SCN,nom,NONE,EDC                       6 tids
   2.1. cpu_fuse_read_hvm_x:
      2.1.1. g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom
      2.1.2. g2026531W2371471I_Nt_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m0
      2.1.3. g2026530W2371470I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m1
   2.2. cpu_fuse_read_special_x:
      2.2.1. g2026525W2371465I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_nom
      2.2.2. g2026529W2371469I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m0
      2.2.3. g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # one module
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tid ARR'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
Summary:
========
1. ARR,nom,NONE,EDC                       2 tids

TestInstances:
==============
1. ARR,nom,NONE,EDC                       2 tids
      1 CCA                                                                              shops_L_list
      1 CCB                                                                              shops_H_list

Patterns:
=========
1. ARR,nom,NONE,EDC                       2 tids
   1.1. shops_H_list:
      1.1.1. g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH
   1.2. shops_L_list:
      1.2.1. g2294511W1466650I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # summary only
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tid ALL -summary'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
Summary:
========
1. ARR,nom,NONE,EDC                       2 tids
2. SCN,nom,NONE,EDC                       6 tids
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_flowall(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -flowall ALL'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
   0. PassFlow ARR                CCA Trace: ['MAIN', 'ARR::MAIN1']
   1. PassFlow ARR                CCB Trace: ['MAIN', 'ARR::MAIN1']
   2. PassFlow ARR                TPIE_PgmRules Trace: ['MAIN', 'ARR::MAIN1']
   3. PassFlow SCN                CCA Trace: ['MAIN', 'SCN::MAIN2']
   4. PassFlow SCN                CCB Trace: ['MAIN', 'SCN::MAIN2']
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # with ituff
        with TempDir(chdir=True):
            File('a.ituff').touch('''
2_tname_testtime_ARR::CCA
2_tname_testtime_ARR::CCB
''')
            cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -flowall ALL -ituff a.ituff'.split()
            with MockVar(sys, "argv", cmd), CaptureStdout() as p:
                print()
                TPInfo().main()
            expect = '''
   0. PassFlow ARR                CCA Trace: ['MAIN', 'ARR::MAIN1']
   1. PassFlow ARR                CCB Trace: ['MAIN', 'ARR::MAIN1']
'''
            self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_flow(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -flowpass ALL'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
   0. PassFlow ARR                CCA Trace: ['MAIN', 'ARR::MAIN1']
   1. PassFlow ARR                CCB Trace: ['MAIN', 'ARR::MAIN1']
   2. PassFlow ARR                TPIE_PgmRules Trace: ['MAIN', 'ARR::MAIN1']
   3. PassFlow SCN                CCA Trace: ['MAIN', 'SCN::MAIN2']
   4. PassFlow SCN                CCB Trace: ['MAIN', 'SCN::MAIN2']
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # unfortunately, Simple1 has no failflow
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -flowall ALL'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_param(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -flowpass ALL -param patlist'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
ARR PassFlow CCA shops_L_list
ARR PassFlow CCB shops_H_list
SCN PassFlow CCA cpu_fuse_read_hvm_x
SCN PassFlow CCB cpu_fuse_read_special_x
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_flatreset(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -flatreset tgl'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            print()
            TPInfo().main()
        expect = '''
mod,resetplb,patlist_name,testinstance_name
SCN,tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0,cpu_fuse_read_hvm_x,CCA
SCN,tgl_pst_W9999993H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0,cpu_fuse_read_hvm_x,CCA
SCN,tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0,cpu_fuse_read_special_x,CCB
SCN,tgl_pst_W9999993H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0,cpu_fuse_read_special_x,CCB
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # with ituff
        with TempDir(chdir=True):
            File('a.ituff').touch('''
2_tname_testtime_SCN::CCA
''')
            cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -flatreset tgl -ituff a.ituff'.split()
            with MockVar(sys, "argv", cmd), CaptureStdout() as p:
                print()
                TPInfo().main()
            expect = '''
mod,resetplb,patlist_name,testinstance_name
SCN,tgl_pre_W9999991H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0,cpu_fuse_read_hvm_x,CCA
SCN,tgl_pst_W9999993H_040416xxx10040x22xxalb0_T0xx2o_0700_Mfus_0_vrevTR1P_hdmt2_hvm_hdmt2_CXJ_cf3fn_0,cpu_fuse_read_hvm_x,CCA
'''
            self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    def test_tid_dump(self):
        with TempDir(name=True) as tdir:
            fname = join(tdir, 'a.csv')
            cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tid_dump ALL -out {fname}'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()
            result1 = len(open(fname).read().split('\n'))
            self.assertGreater(result1, 2)

            fname = join(tdir, 'b.csv')
            cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tid_dump ARR -out {fname}'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()
            result2 = len(open(fname).read().split('\n'))
            self.assertGreater(result1, result2)

    def test_skipjson(self):
        # Skip ARR from command line
        tpref = f'{UT_DIR_REPO}/Simple1/TPL'
        with TempDir(name=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            if IS_UNIX:
                SystemCall(f'chmod +w -R {tdir}').run_outonly()
            File(f'{tpref}/../ProgramFlows.mtpl.fixed').copy(f'{tdir}/TPL/ProgramFlowsTestPlan/ProgramFlows.mtpl')
            File(f'{tdir}/TPL/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)
            tpenv = f'{tdir}/TPL/EnvironmentFile.env'

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 5)

            # Do the skip
            cmd = f'tp_audit.py {tpenv} -skipjson'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()

            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 2)

    def test_skipmod(self):
        # Skip SCN from command line
        tpref = f'{UT_DIR_REPO}/Simple1/TPL'
        with TempDir(name=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            if IS_UNIX:
                SystemCall(f'chmod +w -R {tdir}').run_outonly()
            File(f'{tpref}/../ProgramFlows.mtpl.fixed').copy(f'{tdir}/TPL/ProgramFlowsTestPlan/ProgramFlows.mtpl')
            File(f'{tdir}/TPL/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)
            tpenv = f'{tdir}/TPL/EnvironmentFile.env'

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 5)

            # Do the skip
            cmd = f'tp_audit.py {tpenv} -skipmod SCN'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()

            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 3)

    def test_skipall(self):
        # Keep only ARR from command line
        tpref = f'{UT_DIR_REPO}/Simple1/TPL'
        with TempDir(name=True) as tdir:
            # setup first
            shutil.copytree(tpref, f'{tdir}/TPL')
            if IS_UNIX:
                SystemCall(f'chmod +w -R {tdir}').run_outonly()
            File(f'{tpref}/../ProgramFlows.mtpl.fixed').copy(f'{tdir}/TPL/ProgramFlowsTestPlan/ProgramFlows.mtpl')
            File(f'{tdir}/TPL/skip_modules.json').touch('{ "CLASS_TGLH81": ["ARR"] }', newfile=True)
            tpenv = f'{tdir}/TPL/EnvironmentFile.env'

            # Reference first before skip
            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 5)

            # Do the skip
            cmd = f'tp_audit.py {tpenv} -skipall ARR'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()

            result = len(list(TestProgram(tpenv).mtpl.iter_flows()))
            self.assertEqual(result, 3)

    def test_patlist(self):
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -patlist'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        self.assertEqual(len(trimut(p.getvalue())), 8)

    def unused_test_prcnt(self):
        # This unittest is mocked
        from mod.cci_list import CCI

        def fake(slf, cmd_prcnt):
            return [f'{slf.base_branch} RESULT']

        cmd = f'tp_audit.py . -prcnt 23 -repo mtlp68'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(CCI, "main", fake), \
                MockVar(GitHub, 'get_all_branches', Mock(return_value={'jdr', 'TP/23', 'TP/RC_23A', 'TP/32'})), \
                CaptureStdout() as p:
            TPInfo().main()
        expect = '''
Processing TP/23: 0 of 1:
Found: TP/23: 1
Processing TP/RC_23A: 1 of 1:
Found: TP/RC_23A: 1
===================
TP, date, PR_count
TP/23 RESULT
TP/RC_23A RESULT
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_reformat(self):
        with TempDir(name=True) as tdir:
            newfile = f'{tdir}/a.mtpl'
            File(newfile).touch('Test abc { a=1; b=2; c=3; Block A { line2; } }')
            cmd = f'tp_audit.py {newfile} -reformat'.split()
            with MockVar(sys, "argv", cmd):
                TPInfo().main()
            expect = """
Test abc
{
    a=1;
    b=2;
    c=3;
    Block A
    {
        line2;
    }
}
"""
            self.assertTextEqual(File(newfile).read().replace('\t', '    '), expect)

    def test_evg(self):
        with Chdir(f'{UT_DIR_REPO}/Simple4'):
            result = TPInfo.evg()

        expect = '''
[
   {
      "module": "ARRX",
      "team": "ARRX",
      "evg": 4,
      "prime": 0,
      "total": 4
   },
   {
      "module": "PTH",
      "team": "PTH",
      "evg": 3,
      "prime": 0,
      "total": 3
   },
   {
      "module": "SCNX",
      "team": "SCNX",
      "evg": 0,
      "prime": 3,
      "total": 3
   }
]
'''
        self.assertTextEqual(json.dumps(result, indent=3), expect)

    def test_evgdetail(self):
        with Chdir(f'{UT_DIR_REPO}/Simple4'), MockVar(OPT, 'detail', True):
            result = TPInfo.evg()

        expect = r'''
{
   "module": "ARRX",
   "team": "ARRX",
   "evg_or_prime": "EVG",
   "template": "iCFuncTest",
   "tiname": "\"CCB\""
}
'''
        self.assertTextEqual(json.dumps(result[0], indent=3), expect)
        self.assertEqual(len(result), 10)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_orderplist(self):
        cmd = f'tp_audit.py POR_TP/TGLH81/EnvironmentFile.env -orderplist'.split()
        with MockVar(sys, "argv", cmd), CaptureStdoutLog() as p:
            TPInfo().main()
        self.assertIn('Success', p.getvalue())


class TestContentSummary(TestCase):

    def test_basic_with_csv(self):
        tp = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        cmd = f'tp_audit.py -content {tp} -content {tp} {tp} {tp} -out a.csv'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p, TempDir(name=True, chdir=True):
            print()
            TPInfo().main()
            result = File('a.csv').read()

        expect = '''
R: Simple1Real
R: Simple1Real
A: Simple1Real
B: Simple1Real
==========================================================================================
 Module | R-Total | R-KILL | R-EDC | A-Total | A-KILL | A-EDC | B-Total | B-KILL | B-EDC
 ARR    | 2       | 0      | 2     | 2       | 0      | 2     | 2       | 0      | 2
 ARR-1  | 2       | 0      | 2     |         |        |       |         |        |
 SCN    | 6       | 0      | 6     | 6       | 0      | 6     | 6       | 0      | 6
 SCN-1  | 6       | 0      | 6     |         |        |       |         |        |
==========================================================================================
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        expect = '''Module,R-Total,R-KILL,R-EDC,A-Total,A-KILL,A-EDC,B-Total,B-KILL,B-EDC
ARR,2,0,2,2,0,2,2,0,2
ARR-1,2,0,2,,,,,,
SCN,6,0,6,6,0,6,6,0,6
SCN-1,6,0,6,,,,,,
'''
        self.assertTextEqual(result, expect)

    def test_process(self):
        obj = ContentSummary()
        # simple
        result = obj.process(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env', 'A')
        self.assertEqual(result, {'ARR': (0, 2), 'SCN': (0, 6)})

        # Real unittest data - mocked up
        data = {'SCN,nom,NONE,KIL': {0: {'1466649_00', '1466651_00'},
                                     1: {'COR': 'nom',
                                         'EKL': 'KIL',
                                         'FRQ': 'NONE',
                                         'MOD': 'SCN'},
                                     2: {'CCB', 'CCA'}},
                'SCN,max,NONE,KIL': {0: {'1466649_00', '1466650_00'},
                                     1: {'COR': 'nom',
                                         'EKL': 'KIL',
                                         'FRQ': 'NONE',
                                         'MOD': 'SCN'},
                                     2: {'CCB', 'CCA'}},
                'SCN,nom,NONE,EDC': {0: {'1466651_00',    # KIL
                                         '1466650_00',    # KIL
                                         '1466649_00',    # KIL
                                         '2371470_00',
                                         '2371471_00'},
                                     1: {'COR': 'nom',
                                         'EKL': 'EDC',
                                         'FRQ': 'NONE',
                                         'MOD': 'SCN'},
                                     2: {'CCB', 'CCA'}}}
        with MockVar(TidDb, 'summary_mod_tid', Mock(return_value=data)):
            result = obj.process(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env', 'A')
            self.assertEqual(result, {'SCN': (3, 2)})

    def test_display(self):
        obj = ContentSummary()
        dsort = {'ARR': (0, 0), 'SCN': (4, 4)}
        dprev = {'ARR': (1, 1), 'PTH': (5, 5), 'MIO': (9, 9)}
        dcurr = {'ARR': (3, 3), 'PTH': (7, 7), 'CLK': (8, 8)}
        with CaptureStdout() as p, MockVar(OPT, 'out', None):
            result = obj.display(dsort, dprev, dcurr)
            self.assertEqual(obj.write_csv(None), 1)
        expect = """==========================================================================================
 Module | R-Total | R-KILL | R-EDC | A-Total | A-KILL | A-EDC | B-Total | B-KILL | B-EDC
 ARR    | 0       | 0      | 0     | 2       | 1      | 1     | 6       | 3      | 3
 CLK    |         |        |       |         |        |       | 16      | 8      | 8
 MIO    |         |        |       | 18      | 9      | 9     |         |        |
 PTH    |         |        |       | 10      | 5      | 5     | 14      | 7      | 7
 SCN    | 8       | 4      | 4     |         |        |       |         |        |
==========================================================================================
-i- Specify -out <outfile.csv> to write .csv
"""
        self.assertTextEqual(p.getvalue(), expect)
        from pprint import pprint
        pprint(result)
        self.assertEqual(result, [['Module',
                                   'R-Total',
                                   'R-KILL',
                                   'R-EDC',
                                   'A-Total',
                                   'A-KILL',
                                   'A-EDC',
                                   'B-Total',
                                   'B-KILL',
                                   'B-EDC'],
                                  ['ARR', 0, 0, 0, 2, 1, 1, 6, 3, 3],
                                  ['CLK', '', '', '', '', '', '', 16, 8, 8],
                                  ['MIO', '', '', '', 18, 9, 9, '', '', ''],
                                  ['PTH', '', '', '', 10, 5, 5, 14, 7, 7],
                                  ['SCN', 8, 4, 4, '', '', '', '', '', '']])


class TestTimCheck(TestCase):

    def test_basic(self):
        # Display
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_pin DISP'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p, self.assertRaises(SystemExit):
            print()
            TPInfo().main()
        expect = '''
__main__::shops_timing_pkg
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # basic
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_pin .'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        expect = '''
Processing __main__::shops_timing_pkg ...
Clean:     __main__::shops_timing_pkg
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

        # specified domain
        cmd = f'tp_audit.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -tim_pin shops_timing_pkg -grp ALL'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        expect = '''
Processing __main__::shops_timing_pkg ...
Clean:     __main__::shops_timing_pkg
'''
        self.assertTextEqual(trimut(p.getvalue(), True, True), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_integration(self):
        # Integration test with fails, mtl
        cmd = f'tp_audit.py {UT_DIR}/mtl_P_integ6_TimIssue/EnvironmentFile_CLASS_P28G2_TRCFAILED.env -tim_pin .'.split()
        with MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()

        # Output
        print(p.getvalue())

        # check on the counts
        clean = 0
        def_twice = 0
        missing = 0
        for line in p.getvalue().split('\n'):
            if 'Clean:' in line:
                clean += 1
            if 'defined twice' in line:
                def_twice += 1
            if 'does not have' in line:
                missing += 1

        self.assertEqual(clean, 5)
        self.assertEqual(def_twice, 298)
        self.assertEqual(missing, 637)

    def test_checks(self):
        # fabricated testcases to confirm logic
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        tc = TimCheck(tp, 'shops_timing_pkg', [])

        # missing pin
        timgrp = {'all_dmn': 'ALL'}    # {pingrp: domain}
        refpin = {'AUDCLK': 'ALL',     # {pin: domain}
                  'CUDCLK': 'AXX'}
        with CaptureStdout() as p:
            errors = tc._tim_check('t1', timgrp, refpin)
        self.assertEqual(p.getvalue(), '-e- t1 does not have CUDCLK defined. Domain for this pin: AXX\n')
        self.assertEqual(errors, 1)

        # duplicated definition
        timgrp = {'all_dmn': 'ALL',
                  'BUDCLK': 'ALL'}
        with CaptureStdout() as p:
            errors = tc._tim_check('t1', timgrp, {})
        self.assertEqual(p.getvalue(), '-e- t1 has BUDCLK defined twice. In BUDCLK and in all_dmn\n')
        self.assertEqual(errors, 1)

        # wrong domain in timings
        timgrp = {'all_dmn': 'TAP'}
        with CaptureStdout() as p:
            errors = tc._tim_check('t1', timgrp, {})
        expect = '''-e- t1 has domain mismatch for AUDCLK: ALL (domain) vs TAP (timing)
-e- t1 has domain mismatch for BUDCLK: ALL (domain) vs TAP (timing)
'''
        self.assertEqual(p.getvalue(), expect)
        self.assertEqual(errors, 2)

        # pin not in domains
        timgrp = {'all_dmn': 'ALL'}
        tc.allpins = {'BUDCLK': {'ALL'}}     # AUDCLK is not in allpins
        with CaptureStdout() as p:
            errors = tc._tim_check('t1', timgrp, {})
        expect = '''-e- AUDCLK in all_dmn is not defined in any pattern domain.
'''
        self.assertEqual(p.getvalue(), expect)
        self.assertEqual(errors, 1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
