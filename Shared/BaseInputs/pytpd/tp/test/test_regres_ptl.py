#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
ptl regres - 04/09/24
100% prime
.tpl in POR folder
uservar has __ in name
nonstandard IP names
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
    def test_ptl_torch(self):
        cmd = f'tp_audit.py ptl-class/POR_TP/PTL_P_CLASS/EnvironmentFile.env -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
                MockVar(sys, "argv", cmd), CaptureStdout() as p,\
                Chdir(UT_DIR):
            TPInfo().main()
        result = '\n'.join(trimut(p.getvalue()))
        expect = '''
Total:  10172 patterns
Total:  37753 GlobalPlists
Total:   2721 testinstances
Total:   1825 testinstances with patlist
Total:      0 testinstances connected
Total:      0 testinstances non-bypass
Total:     84 mtpl files
Total:      1 flows total
Total:      1 flows pass
Total:    207 timing test condition
Total:   1046 level test condition
Total:   2992 uservars
Total:      0 pgmrule lines
Total:      0 pgmrule applied
'''
        self.assertTextEqual(result, expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
