#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
tgl81 regres
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar
from gadget.tputil import trimut
from gadget.helperclass import CaptureStdout
from gadget.files import TempDir
from gadget.printmore import Dumper
from main.tp_audit import *
from mod.setting import cfg
import sys


class TestRegress(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tgl81(self):
        print(f'TP: {UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        cmd = f'tp_audit.py {UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
                MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        expect = '''Total:  56365 patterns
Total:  10798 GlobalPlists
Total:  12665 testinstances
Total:   8562 testinstances with patlist
Total:   5265 testinstances connected
Total:   3889 testinstances non-bypass
Total:     80 mtpl files
Total:   7611 flows total
Total:   6275 flows pass
Total:    155 timing test condition
Total:    268 level test condition
Total:  10418 uservars
Total:  12124 pgmrule lines
Total:   3215 pgmrule applied'''
        self.assertTextEqual('\n'.join(result), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
