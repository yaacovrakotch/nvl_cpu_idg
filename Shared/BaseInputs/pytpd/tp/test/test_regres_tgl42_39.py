#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
tgl regres
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest
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
    def test_tgl42_39(self):
        # TOS3.9 + relative dir
        cmd = f'tp_audit.py TGLXXXXXXX14F9BSXXX/TPL/EnvironmentFile.env -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
            MockVar(sys, "argv", cmd), CaptureStdout() as p,\
                Chdir(UT_DIR):
            TPInfo().main()
        result = trimut(p.getvalue())
        expect = '''Total:  44831 patterns
Total:  10778 GlobalPlists
Total:  10837 testinstances
Total:   6737 testinstances with patlist
Total:   4804 testinstances connected
Total:   3868 testinstances non-bypass
Total:    238 mtpl files
Total:   7833 flows total
Total:   5822 flows pass
Total:    241 timing test condition
Total:    749 level test condition
Total:   1269 uservars
Total:  15819 pgmrule lines
Total:   3370 pgmrule applied'''
        self.assertTextEqual('\n'.join(result), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
