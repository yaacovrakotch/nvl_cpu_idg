#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for fuse_diff
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.disk import Chdir
from main.fuse_diff import *
from os.path import join, dirname, abspath


class TestFD(TestCase):

    @with_(TempDir, chdir=True)
    def test_read_sspec(self):
        text = """
# Register: CPU28
#                             43210

Visibility:  CPU28:           00000
FUSEDATA:    CPU28:  Q1P6: n: 01230
FUSEDATA:    CPU28:  Q1VN: n: 02245

QDF_SSPEC_DEF: Q1P6: Q1P6
QDF_SSPEC_DEF: Q1VN: Q1VN
"""
        File('sspec.txt').touch(text)

        expect = {'Q1P6': {0: '0', 1: '3', 2: '2', 3: '1', 4: '0'},
                  'Q1VN': {0: '5', 1: '4', 2: '2', 3: '2', 4: '0'}}
        self.assertEqual(FuseDiff().read_sspec('.'), expect)

    @with_(TempDir, chdir=True)
    def test_read_fusedef(self):
        text = """
########################################
#register:  Register:  Data Type:  Size
########################################
register:   CPU28:     Binary:     49152

#################################################################################
#fusedef:  Register:  Address:          Fuse Type:  Setting:           Fuse Group
#################################################################################
fusedef:   CPU28:     3-0:              senr:       DD:                A
fusedef:   CPU28:     4:                senr:       EE:                B
fusedef:   CPU28:     8-6,5-5:          senr:       FF:                C
"""
        File('fusedef.txt').touch(text)
        expect = {0: 'DD: A',
                  1: 'DD: A',
                  2: 'DD: A',
                  3: 'DD: A',
                  4: 'EE: B',
                  5: 'FF: C',
                  6: 'FF: C',
                  7: 'FF: C',
                  8: 'FF: C'}
        self.assertEqual(FuseDiff().read_fusedef('.'), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
