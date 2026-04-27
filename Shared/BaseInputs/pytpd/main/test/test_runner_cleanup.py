#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
import os
import json
from setenv_unittest import UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.helperclass import CaptureStdoutLog
from main.runner_cleanup import *
from gadget.pylog import log
from unittest.mock import patch
import shutil


class TestBasic(TestCase):

    def test_cleanup_start(self):
        runner_cleanup = RunnerCleanUp()
        tempdir = f'{UT_DIR_REPO}/tempdir'
        with TempDir(name=True, delete=True) as tdir, TempDir(name=True, delete=True) as tdir2:
            cleanup_file_test = f'{tdir}/test_runner_2026-01-06_13-37-11_cleanup.txt'
            shutil.copytree(tempdir, f'{tdir2}/TempDir')
            with MockVar(runner_cleanup, 'runner_name', 'test_runner'), \
                    MockVar(runner_cleanup, 'now_str', '2026-01-06_13-37-11'), \
                    MockVar(runner_cleanup, 'cleanup_file', cleanup_file_test), \
                    MockVar(runner_cleanup, 'folder_to_cleanup', [f'{tdir2}/TempDir']):
                with CaptureStdoutLog() as p:
                    runner_cleanup.cleanup_start()
                self.assertIn("Successfully cleaned up folder", p.getvalue())

    def test_basic(self):
        runner_cleanup = RunnerCleanUp()
        tempdir = f'{UT_DIR_REPO}/tempdir'
        with TempDir(name=True, delete=True) as tdir, TempDir(name=True, delete=True) as tdir2:
            cleanup_file_test = f'{tdir}/test_runner_2026-01-06_13-37-11_cleanup.txt'
            shutil.copytree(tempdir, f'{tdir2}/TempDir')
            with MockVar(runner_cleanup, 'runner_name', 'test_runner'), \
                    MockVar(runner_cleanup, 'now_str', '2026-01-06_13-37-11'), \
                    MockVar(runner_cleanup, 'cleanup_file', cleanup_file_test), \
                    MockVar(runner_cleanup, 'folder_to_cleanup', [f'{tdir2}/TempDir']):
                with CaptureStdoutLog() as p:
                    runner_cleanup.main()
                self.assertRegex(p.getvalue(), "Finished cleaning up D:/ drive. Log file: .*test_runner_2026-01-06_13-37-11_cleanup.txt")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
