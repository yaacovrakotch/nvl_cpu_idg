#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for lockfile
"""
from setenv_unittest import ROOT_ENV     # must be first import for unittests
import sys
from gadget.files import TempDir, TempName, File
from gadget.gizmo import Elapsed, MockVar
from gadget.lockfile import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.shell import IS_UNIX
from gadget.shell import RunChild
from unittest.mock import Mock
from gadget.sepshelve import SqlDict
import multiprocessing
import random
import string


class LockTest(TestCase):
    """Unittest for Lock"""

    def test_basic(self):
        with TempDir(name=True) as tdir:
            with Lock(f'{tdir}/mylock'):
                self.assertEqual(os.listdir(tdir), ['mylock.lock'])
            self.assertEqual(os.listdir(tdir), [])

    def test_removed_lock(self):
        # lockdir was deleted, so close() should not error out
        with TempDir(name=True) as tdir:
            with Lock(f'{tdir}/mylock'):
                os.rmdir(join(tdir, 'mylock.lock'))
            self.assertEqual(os.listdir(tdir), [])

    def test_mkdir_errored(self):
        # lockdir was deleted, so close() should not error out
        with TempDir(name=True) as tdir:
            File(join(tdir, 'mylock.lock')).touch()
            with MockVar(os, 'listdir', Mock(return_value=[])):
                with self.assertRaisesRegex(ErrorEnv, 'timeout in acquiring'):
                    with Lock(f'{tdir}/mylock', sleepsec=0.01, timeout=0.1):
                        pass
            self.assertEqual(os.listdir(tdir), ['mylock.lock'])   # this should not be deleted since it's a file

    def test_locked(self):
        with TempDir(name=True) as tdir:
            with Lock(f'{tdir}/mylock'):

                # This should timeout
                with self.assertRaisesRegex(ErrorEnv, 'timeout in acquiring'):
                    with Lock(f'{tdir}/mylock', sleepsec=0.01, timeout=0.1) as p:
                        pass

                # lock should still exist
                self.assertEqual(os.listdir(tdir), ['mylock.lock'])

            # lock is deleted
            self.assertEqual(os.listdir(tdir), [])

    def test_force_refresh(self):
        # readonly dir
        if IS_UNIX:
            force_refresh('/')
        else:
            force_refresh('I:\\')

        # writeable dir
        with TempDir(name=True) as tdir:
            force_refresh(tdir)
            self.assertEqual(os.listdir(tdir), [])

    def test_check_lock(self):
        with TempDir() as tdir:
            lfile = os.path.join(tdir.name(), "somefile")
            self.assertFalse(Lock(lfile).check_lock(), "Lockfile should not exist")
            open(f'{lfile}.lock', "w").close()
            self.assertTrue(Lock(lfile).check_lock(), "Lockfile should not exist")
        self.assertRaisesRegex(Exception, 'does not exist', Lock, lfile)

    def test_check_lock_wait(self):
        with TempDir() as tdir:
            lfile = os.path.join(tdir.name(), "somefile")
            # pass case
            self.assertTrue(Lock(lfile, sleepsec=0.01, timeout=0.1).check_lock_wait(), "Success check_lock_wait()")

            # fail case
            File(lfile + ".lock").touch(mtime=time.time() + 3600)
            self.assertFalse(Lock(lfile, sleepsec=0.01, timeout=0.1).check_lock_wait(), "Fail check_lock_wait()")
            self.assertTrue(exists(lfile + ".lock"))

            # timeout case
            File(lfile + ".lock").unlink()
            os.mkdir(lfile + ".lock")
            self.assertTrue(Lock(lfile, sleepsec=0.01, timeout=0.1, maxlocktime=-1).check_lock_wait(), "Fail check_lock_wait() timeout")
            self.assertFalse(exists(lfile + ".lock"))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
