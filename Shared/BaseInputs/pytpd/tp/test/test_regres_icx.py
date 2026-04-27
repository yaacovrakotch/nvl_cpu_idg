#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
icx regres
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
    def test_icx(self):
        cmd = f'tp_audit.py {UT_DIR}/ICXXXXXAXH10G10S922/EnvironmentFile_CLASS_HCCSP.env -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
                MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        expect = '''Total:  55402 patterns
Total:  18981 GlobalPlists
Total:   4897 testinstances
Total:   2860 testinstances with patlist
Total:   2264 testinstances connected
Total:   1601 testinstances non-bypass
Total:    147 mtpl files
Total:   3884 flows total
Total:   3358 flows pass
Total:     54 timing test condition
Total:    351 level test condition
Total:   2763 uservars
Total:   1146 pgmrule lines
Total:    219 pgmrule applied'''
        self.assertTextEqual('\n'.join(result), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
