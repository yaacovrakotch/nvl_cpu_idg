#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
mtlm regres
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar
from gadget.tputil import trimut
from gadget.helperclass import CaptureStdout
from gadget.dictmore import keys_atlevel
from gadget.files import TempDir
from gadget.printmore import Dumper
from main.tp_audit import *
from mod.setting import cfg
import sys


class TestRegress(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mtlp68_usrv(self):
        # tests pickling
        # tests value of uflat and ulocal (full dump)
        # tests _src_eval after pickle

        target = '/intel/hdmxprogs/mtl/MTLXXXXC0H17C00S346/POR_TP/Class_MTL_P68/EnvironmentFile.env'
        cmd = f'tp_audit.py {target} -stats'.split()
        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir),\
                MockVar(sys, "argv", cmd):
            with CaptureStdout() as p:
                TPInfo().main()
            result = trimut(p.getvalue())
            expect = '''
Total:  50373 patterns
Total:  12488 GlobalPlists
Total:  19506 testinstances
Total:  13834 testinstances with patlist
Total:  10935 testinstances connected
Total:   9435 testinstances non-bypass
Total:    177 mtpl files
Total:  15293 flows total
Total:  11605 flows pass
Total:    434 timing test condition
Total:    504 level test condition
Total:  21515 uservars
Total:   1787 pgmrule lines
Total:    705 pgmrule applied
'''

            self.assertTextEqual('\n'.join(result), expect)

            # check correctness of uflat and ulocal
            tp = TestProgram(target).pickle_init()
            with CaptureStdout() as p:
                # del tp.usrv.uflat['__builtins__']
                pprint(tp.usrv.uflat)
                pprint(tp.usrv.ulocal)
            File(f'{tdir}/res').touch(p.getvalue())
            self.assertGoldEqual(f'{tdir}/res', f'{UT_DIR_REPO}/misc_files/usrv_17c00.gold2')

            # check pickle src_eval is evaluated
            self.assertEqual(len(list(keys_atlevel(tp.usrv._src_eval, 2))), 405)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
