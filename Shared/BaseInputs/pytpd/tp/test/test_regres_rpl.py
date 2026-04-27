#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
tgl regres
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar
from gadget.tputil import trimut
from gadget.helperclass import CaptureStdout
from gadget.files import TempDir
from gadget.disk import Chdir
from gadget.printmore import Dumper
from main.tp_audit import *
from mod.setting import cfg
import sys


class TestRegress(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_rpl_torch(self):
        # Torch TP
        cmd = f'tp_audit.py RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
                MockVar(sys, "argv", cmd), CaptureStdout() as p,\
                Chdir(UT_DIR):
            TPInfo().main()
        result = '\n'.join(trimut(p.getvalue()))
        expect = '''Total:  66878 patterns
Total:  13672 GlobalPlists
Total:  11988 testinstances
Total:   8680 testinstances with patlist
Total:   4781 testinstances connected
Total:   3995 testinstances non-bypass
Total:     75 mtpl files
Total:   6634 flows total
Total:   5901 flows pass
Total:    130 timing test condition
Total:    278 level test condition
Total:   1325 uservars
Total:   1503 pgmrule lines
Total:    333 pgmrule applied'''
        self.assertTextEqual(result, expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
