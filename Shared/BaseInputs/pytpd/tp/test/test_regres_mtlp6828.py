#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
mtlp68 and p28 regres
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar
from gadget.tputil import trimut, MtplBlocks
from gadget.helperclass import CaptureStdout
from gadget.files import TempDir
from gadget.dictmore import keys_atlevel
from gadget.printmore import Dumper
from main.tp_audit import *
from mod.setting import cfg
from os.path import basename
import sys
import glob


class TestRegress(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mtl_p6828(self):
        tp = '/intel/hdmxprogs/mtl/MTLXXXXAXH19M00S219/POR_TP/Class_MTL_P68/EnvironmentFile.env'
        print(f'TP: {tp}')
        cmd = f'tp_audit.py {tp} -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
                MockVar(sys, "argv", cmd), CaptureStdout() as p:
            TPInfo().main()
        result = trimut(p.getvalue())
        expect = '''Total:  82852 patterns
Total:  18020 GlobalPlists
Total:  20207 testinstances
Total:  13400 testinstances with patlist
Total:  10685 testinstances connected
Total:   8708 testinstances non-bypass
Total:    186 mtpl files
Total:  15778 flows total
Total:  12527 flows pass
Total:    382 timing test condition
Total:    405 level test condition
Total:  21231 uservars
Total:   1291 pgmrule lines
Total:    237 pgmrule applied'''
        self.assertTextEqual('\n'.join(result), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_instance_to_subflows(self):
        env = '/intel/hdmxprogs/mtl/MTLXXXXAXH19M00S219/POR_TP/Class_MTL_P68/EnvironmentFile.env'
        tp = TestProgram(env).pickle_init()
        result = tp.mtpl.get_instance_to_subflows()
        self.assertEqual(len(result), 20173)
        self.assertEqual(len(list(keys_atlevel(result, 1))), 125604)

    def test_MtplBlocks(self):
        for fn in glob.glob(f'{UT_DIR_REPO}/torch_p6828_fixer/Modules/*/*.mtpl'):
            obj = MtplBlocks(fn)
            self.assertGreater(len(obj.head), 2)      # It is populated, and no errors
            self.assertGreater(len(obj.blocks), 1)    # It is populated, and no errors
            print(f'{basename(fn)}: lines: {len(list(keys_atlevel(obj.blocks, 1)))}')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
