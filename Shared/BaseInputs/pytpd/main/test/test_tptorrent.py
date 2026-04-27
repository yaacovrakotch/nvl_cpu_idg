#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
import os
import json
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
from gadget.shell import SystemCall
from gadget.getgit import GitHub
from main.nvl_pr_counter import *
from os.path import join, dirname, abspath
import sys
from unittest.mock import patch


class TestBasic(TestCase):

    def test_dummy(self):
        self.assertEqual("data", "data")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
