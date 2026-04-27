#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for path_win_unix.py
"""
from setenv_unittest import UT_DIR    # must be first import for unittests
from main.path_win_unix import *
from gadget.ut import TestCase, unittest, Mock
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdout
from gadget.shell import IS_UNIX, IS_WIN
import sys


@unittest.skipIf(IS_WIN, 'unix only')
class PTest(TestCase):

    def test_convert(self):
        tw = ToWindows()

        # to logical
        self.assertEqual(tw.to_logical('/nfs/pdx/disks/mpe_mtl_015/mtl/unittests'),
                         '/intel/engtools/tptools/mtl/unittests')
        # direct
        self.assertEqual(tw.to_logical('/nfs/pdx/disks/mve_sctp_003'),
                         '/intel/engineering/dev/sctp')

        # to windows
        self.assertEqual(tw.to_win('/nfs/pdx/disks/mpe_mtl_015/mtl/unittests'),
                         r'I:\engtools\tptools\mtl\unittests')
        self.assertEqual(tw.to_win('/nfs/site/disks/pdel.intel11/tpvalidation/jqdelosr'),
                         r'I:\tpvalidation\jqdelosr')

        # cannot convert
        with self.assertRaisesRegex(ErrorUser, 'Cannot get logical path of'):
            tw.to_logical('/nfs/pdx/disks/mpe_tvpv_083/mtl')
        with self.assertRaisesRegex(ErrorUser, 'Cannot get logical path of'):
            tw.to_logical('/intel')

    def test_basic(self):
        # execute
        cmd = "path_win_unix.py /nfs/pdx/disks/mpe_mtl_015/mtl/unittests"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                PArgs().main()
        self.assertEqual(p.getvalue().strip(), r'I:\engtools/tptools/mtl/unittests')

        # Nothing to do
        cmd = "path_win_unix.py"
        with MockVar(sys, "argv", cmd.split()), MockVar(ToUnix, 'keyboard', Mock(return_value=r'I:\blah')):
            with CaptureStdout() as p:
                PArgs().main()
        self.assertEqual(p.getvalue().strip(), '/intel/blah')

    def test_to_unix(self):
        # I:\ drive path
        cmd = r"path_win_unix.py I:\engineering -unix"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                PArgs().main()
        self.assertEqual(p.getvalue().strip(), '/intel/engineering')

        # L:\ drive path
        cmd = r"path_win_unix.py L:\sctp -unix"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                PArgs().main()
        self.assertEqual(p.getvalue().strip(), '/intel/engineering/dev/sctp')

        # direct path - disk
        cmd = r"path_win_unix.py \\pdxcv14a-cifs.pdx.intel.com\mve_sctp_003\users -unix"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                PArgs().main()
        self.assertEqual(p.getvalue().strip(), '/nfs/site/disks/mve_sctp_003/users')

        # direct path - logical
        cmd = r"path_win_unix.py \\amr\ec\proj\mdl\jf\intel\hdmxprogs -unix"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                PArgs().main()
        self.assertEqual(p.getvalue().strip(), '/intel/hdmxprogs')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
