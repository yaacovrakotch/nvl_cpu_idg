#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.disk import Chdir
from main.tpenvreorder import *
from os.path import join, dirname, abspath


class TestTpPost(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_envreorder(self):
        with TempDir(name=True, chdir=True, delete=True):
            # get tpl dir and then use later to chdir to it
            tpl = UT_DIR + '/MTLenvreorder/TPL/'
            with Chdir(tpl):  # use Chdir(<dir>) so code returns to tmp once done
                obj = TpPost()
                obj.envreorder()


LOC = join(dirname(abspath(__file__)))
if __name__ == '__main__':  # pragma: no cover
    unittest.main()
