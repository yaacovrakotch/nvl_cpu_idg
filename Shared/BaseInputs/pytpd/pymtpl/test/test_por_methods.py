#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for por_methods
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.shell import CALLERBIN, SystemCall
from unittest.mock import patch, MagicMock
from pymtpl.por_methods import *        # This is loading default por_methods, since there is no TP
import sys
import os
from pprint import pprint


class TestPorMethods(TestCase):

    def test_normal_import(self):
        # por_methods is imported at top of file, so it is using default por_defaults
        self.assertTrue(isinstance(VminTC('blah'), BaseMethod))

    @with_(TempDir, chdir=True)
    def test_tp_repo(self):
        pm = '''
from pymtpl.core import BaseMethod
class Intc(BaseMethod): pass
'''
        File('Shared/BaseInputs/Scripts/por_methods.py').touch(pm, mkdir=True)

        code = f'''
import sys
sys.path.insert(0, f'{ROOT_ENV}')
from pymtpl.por_methods import *
print(isinstance(Intc(), BaseMethod))
'''
        File('main.py').touch(code, mkdir=True)
        _, out = SystemCall(f'{sys.executable} main.py').run_outtxt()
        expect = '-i- por_methods: Shared/BaseInputs/Scripts/por_methods.py\nTrue'
        self.assertIn(expect, out)

    @with_(TempDir, chdir=True)
    def test_default(self):
        code = f'''
import sys
sys.path.insert(0, f'{ROOT_ENV}')
from pymtpl.por_methods import *
print(isinstance(VminTC('blah'), BaseMethod))
'''
        File('main.py').touch(code, mkdir=True)
        _, out = SystemCall(f'{sys.executable} main.py').run_outtxt()
        expect = '-i- Warning: using default por_methods\nTrue'
        self.assertIn(expect, out)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
