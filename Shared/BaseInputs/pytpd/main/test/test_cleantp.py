#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for main cleantp
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock
from gadget.files import TempName, TempDir
from gadget.gizmo import MockVar
from mod.cleantp_mod import *
from gadget.errors import ErrorInput, ErrorUser
from gadget.gizmo import with_
from tp.testprogram import TestProgram
from pprint import pformat
from main.cleantp import *
import glob
import sys
from mod.test.test_cleantp_mod import TestIntegration


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
