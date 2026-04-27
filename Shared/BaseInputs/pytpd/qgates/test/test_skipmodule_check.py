#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for skipmodule_check.py

"""
import sys
try:
    from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.skipmodule_check import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.gizmo import with_
from gadget.helperclass import CaptureStdoutLog
from tp.testprogram import Env
from unittest.mock import Mock


class TestSkipModule(TestCase):

    def test_non_pr(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple5a/POR_TP/TGLH81/EnvironmentFile.env')
        self.assertEqual(SkipModuleCheck(tpobj).main(), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    @with_(MockVar, os.environ, 'FROM_PR', 'TRUE')
    def test_fail1(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        File('POR_TP/TGLH81/SkipModules/ARRX.permanent').touch(mkdir=True)
        obj = SkipModuleCheck(tpobj)
        with MockVar(GitHub, 'get_labels', Mock(return_value={'LABEL1'})), \
                MockVar(GitHub, 'get_modfiles', Mock(return_value={'Modules/ARRX/abc.mtpl'})):
            obj.main()

        print(obj.result)
        expect = [{'message': ('Module=[ARRX] is skipped, but [Modules/ARRX/abc.mtpl] is part of commit Pls '
                               'delete [POR_TP/TGLH81/SkipModules/ARRX.permanent] first in your branch. '
                               'This will enable ARRX. Or add FORCED_MODULESKIP label to keep this module skipped.'),
                   'id': 256,
                   'module': 'ARRX'}]
        result = obj.result
        result[0]['message'] = Env.xpath(obj.result[0]['message'])
        self.assertEqual(result, expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    @with_(MockVar, os.environ, 'FROM_PR', 'TRUE')
    def test_fail2(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        File('POR_TP/TGLH81/SkipModules/SCN.txt').touch(mkdir=True)
        obj = SkipModuleCheck(tpobj)
        with MockVar(GitHub, 'get_labels', Mock(return_value={'LABEL1'})), \
                MockVar(GitHub, 'get_modfiles', Mock(return_value={'Modules/ARRX/abc.mtpl'})):
            obj.main()

        print(obj.result)
        expect = [{'message': ("Cannot have temporary SkipModules in main branch. Temporary list: "
                               "{'POR_TP/TGLH81/SkipModules/SCN.txt'} Either fix these modules or "
                               "request approval to make these permanent"),
                   'id': 255,
                   'module': 'BASE'}]
        result = obj.result
        result[0]['message'] = Env.xpath(obj.result[0]['message']).replace('//', '/')
        self.assertEqual(result, expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    @with_(MockVar, os.environ, 'FROM_PR', 'TRUE')
    def test_pass_forced(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        File('POR_TP/TGLH81/SkipModules/ARRX.permanent').touch(mkdir=True)
        obj = SkipModuleCheck(tpobj)
        with MockVar(GitHub, 'get_labels', Mock(return_value={'FORCED_MODULESKIP', 'LABEL1'})), \
                MockVar(GitHub, 'get_modfiles', Mock(return_value={'Modules/ARRX/abc.mtpl'})):
            self.assertEqual(obj.main(), 2)

        self.assertEqual(obj.result, [])

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    @with_(MockVar, os.environ, 'FROM_PR', 'TRUE')
    def test_pass(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        File('POR_TP/TGLH81/SkipModules/ARRX.permanent').touch(mkdir=True)
        obj = SkipModuleCheck(tpobj)
        with MockVar(GitHub, 'get_labels', Mock(return_value={'LABEL1'})), \
                MockVar(GitHub, 'get_modfiles', Mock(return_value={'Modules/SCN/abc.mtpl'})):
            obj.main()

        self.assertEqual(obj.result, [])

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    @with_(MockVar, os.environ, 'FROM_PR', 'TRUE')
    def test_corner_readme(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        File('POR_TP/TGLH81/SkipModules/Readme.txt').touch(mkdir=True)
        obj = SkipModuleCheck(tpobj)
        with MockVar(GitHub, 'get_labels', Mock(return_value={'LABEL1'})), \
                MockVar(GitHub, 'get_modfiles', Mock(return_value={})):
            obj.main()

        self.assertEqual(obj.result, [])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
