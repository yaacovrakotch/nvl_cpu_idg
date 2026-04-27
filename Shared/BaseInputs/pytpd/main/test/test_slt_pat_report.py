#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for slt_pat_report.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO    # must be first import for unittests
from main.slt_pat_report import *
from gadget.ut import TestCase, unittest, Mock
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdout
from gadget.files import TempDir
from gadget.shell import IS_UNIX
import sys


class STest(TestCase):

    def test_wronginput(self):
        # execute
        cmd = f"slt_pat_report.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                with self.assertRaisesRegex(AssertionError, 'Incorrect input'):
                    SArgs().main()
        self.assertEqual(p.getvalue().strip(), '')

    def test_basic2(self):
        # execute
        cmd = f"slt_pat_report.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env -idrive"
        pats1 = {'g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH'}
        pats2 = pats1 | {'g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom'}
        with MockVar(sys, "argv", cmd.split()),\
                MockVar(ReadTvpv, 'read_all_pats', Mock(return_value=pats2)),\
                MockVar(ReadHdmxPats, 'read_all_pats', Mock(return_value=pats1)),\
                CaptureStdout() as p:
            print()
            SArgs().main()
        expect = '''
================================================
 Module | Total | TVPV_Disk | IDrive | ClassTP
    ARR |     2 |         1 |      1 |       2
    SCN |     6 |         1 |      0 |       6
================================================
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_basic(self):
        # execute
        cmd = f"slt_pat_report.py {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env {UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env"
        pats1 = {'g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH'}
        pats2 = pats1 | {'g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom'}
        with MockVar(sys, "argv", cmd.split()),\
                MockVar(ReadTvpv, 'read_all_pats', Mock(return_value=pats2)),\
                MockVar(ReadHdmxPats, 'read_all_pats', Mock(return_value=pats1)),\
                CaptureStdout() as p:
            print()
            SArgs().main()
        expect = '''
==============================================================================
 Module | tuple+tid Total | tid total | tuple+tid ClassTP | tid only ClassTP
    ARR |               2 |         2 |                 2 |                2
    SCN |               6 |         6 |                 6 |                6
==============================================================================
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_derive_root(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        obj = ReadHdmxPats(tpobj)
        if IS_UNIX:
            self.assertEqual(obj.roots, {'/intel/hdmxpats/tgl'})
        else:
            self.assertEqual(obj.roots, {'I:/hdmxpats/tgl'})

    def test_get_mod_pats(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        expct = {'ARR': {'g2294507W1466649I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSH',
                         'g2294511W1466650I_MD_VTR024T_Mnnm0000000o_n040816xx00022xxx1xxxalb_TR1XhhTC002J3li_LJx0A42x0nxx0000_SHOPSL'},
                 'SCN': {'g2026507W2371433I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_nom',
                         'g2026525W2371465I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_nom',
                         'g2026528W2371468I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m1',
                         'g2026529W2371469I_NI_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_SpecialRow_Read_m0',
                         'g2026530W2371470I_OM_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m1',
                         'g2026531W2371471I_Nt_VTR023T_Uonm070000fa_a040416xx00022xxx1xxxalb_TR1PThTC001J3fn_LJx0A42x0nxx0000_Fuse_HvmData_Read_m0'}}
        self.assertEqual(dict(SArgs.get_mod_pat(tpobj)), expct)

    def test_ReadHdmxPats(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env').pickle_init()
        with TempDir(name=True) as tdir:
            File(f'{tdir}/MfunIa/RevTTB3.0/p0/pat/indv_bin/a.pobj').touch(mkdir=True)
            File(f'{tdir}/MfunIa/RevTTB3.0/p0/pat/indv_bin/b.pobj').touch(mkdir=True)
            File(f'{tdir}/MfunIa/RevTTB3.0/p0/pat/common_files/c.pobj').touch(mkdir=True)
            File(f'{tdir}/MfunIa/RevTTB4.0/p0/pat/indv_bin/d.pobj').touch(mkdir=True)

            obj = ReadHdmxPats(tpobj)
            obj.roots = [tdir]     # override it
            self.assertEqual(obj.read_all_pats(), {'d.pobj', 'b.pobj', 'a.pobj'})

    def test_ReadTvpv(self):
        obj = ReadTvpv({'ARR': {'g2294507W1466649I_MD_VTR024T', 'g2294508W1466649I_MD_VTR024K'},
                        'FUN': {'g2294507W1466649I_MD_VTR024T'}})
        self.assertEqual(obj.tups, {'g2294508', 'g2294507'})
        output = '''
    INFO: '-echo bin' is interpreted as '-ek PAT -short_format_template "{bin} : [{status_tags}]"'
/p/pde/tvpv/mtl/hdmt2/central/vrevC28A6P/class/hvm/indv_bin19/g0115113W4144058A_Na_VC28xCA078_Xm023800xxx0a_dxxx0404041bxxxxxxxxx_cC28A6PxxATC039J051_x00_l2_tsp_pmovi_y_x.pinObj : [HTD_VER__cdie_mtlc_a0_21ww28a__eng_2021_ww21a,LI_atom_array_siso_ks_r4_stf100,VFREV_0_1]
/p/pde/tvpv/mtl/hdmt2/central/vrevC28A7P/sort/hvm/indv_bin13/g0115113W4144058A_Na_VC28xCA078_Xm023800xxx0a_dxxx0404041bxxxxxxxxx_cC28A7PxxATC007J06y_x00_l2_tsp_pmovi_y_x.pinObj : [HTD_VER__cdie_mtlc_a0_21ww28a__eng_2021_ww21a,LI_atom_array_siso_ks_r4_stf100,VFREV_0_1]
/p/pde/tvpv/mtl/hdmt2/central/vrevC28A7P/ippkg/hvm/indv_bin17/g0115113W4144058A_Na_VC28xCA078_Xm023800xxx0a_dxxx0404041bxxxxxxxxx_cC28A7PxxATC010J06y_x00_l2_tsp_pmovi_y_x.pinObj : [HTD_VER__cdie_mtlc_a0_21ww28a__eng_2021_ww21a,LI_atom_array_siso_ks_r4_stf100,VFREV_0_1]
'''
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))):
            self.assertEqual(len(obj.read_all_pats()), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
