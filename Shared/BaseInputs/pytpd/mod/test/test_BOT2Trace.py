#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tiddb.py
"""
from setenv_unittest import UT_DIR_REPO    # must be first import for unittests
from mod.BOT2Trace import *
import mod.BOT2Trace as bot2trace
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar
from gadget.files import TempDir
from gadget.disk import mkdirs


class TestB2T(TestCase):

    def test_basic(self):
        # Run start to finish using a valid ituff
        with TempDir(name=True, delete=True) as tdir, \
                MockVar(bot2trace, 'get_dest', Mock(return_value=tdir)):
            traceIT(f'{UT_DIR_REPO}/ituff_files/bin1_mbot.txt')

            self.assertEqual(len(os.listdir(tdir)), 1)    # one file created

    def test_get_dest(self):
        with TempDir(name=True, delete=True) as tdir:
            self.assertEqual(get_dest(f'{tdir}/'), f'{tdir}/')
            mkdirs(f'{tdir}/trace/Ituffs')
            self.assertEqual(get_dest(f'{tdir}/'), f'{tdir}/trace/Ituffs/')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
