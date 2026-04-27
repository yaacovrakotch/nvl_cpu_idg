#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
nvl regres - Nov 11 - ES program
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
    def test_nvl(self):
        cmd = f'tp_audit.py /intel/hdmxprogs/nvl/NVLXXXXA0H01U40S545/POR_TP/Class_NVL_S28C/EnvironmentFile.env -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
                MockVar(sys, "argv", cmd), CaptureStdout() as p,\
                Chdir(UT_DIR):
            TPInfo().main()
        result = '\n'.join(trimut(p.getvalue()))
        expect = '''
Total:  41692 patterns
Total:  24627 GlobalPlists
Total:   7942 testinstances
Total:   4580 testinstances with patlist
Total:   3972 testinstances connected
Total:   2898 testinstances non-bypass
Total:      0 mtpl files
Total:   6856 flows total
Total:   5255 flows pass
Total:    418 timing test condition
Total:    694 level test condition
Total:  23895 uservars
Total:      0 pgmrule lines
Total:      0 pgmrule applied
'''
        self.assertTextEqual(result, expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
