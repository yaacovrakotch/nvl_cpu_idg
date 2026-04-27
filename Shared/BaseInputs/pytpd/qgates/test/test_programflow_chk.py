#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for programflow_chk.py

"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.programflow_chk import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import patch, Mock
from gadget.gizmo import with_, MockVar
from gadget.shell import TarAdd
from tp.testprogram import Env
import qgates.programflow_chk as pf


class TestProgramFlowChecker(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL5', chdir=True, delete=True)
    def test_integration(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        ut = ProgramFlowChecker(tpobj)
        # case: No complete.tar.gz file
        # Mock the File.read method to return predefined values
        with MockVar(os.environ, 'FROM_PR', 'True'):
            ut.main()

        expect = Env.xpath(f'270 FLOW complete_tp.tar.gz does not exist in {os.getcwd()}')
        self.assertTextEqual(Env.xpath(ut.ut_result()), expect)

        # case: with complete tar, there is diff as expected
        TarAdd('complete_tp.tar.gz', '.', exclude=['.git', 'temp'])
        ut = ProgramFlowChecker(tpobj)
        with MockVar(TestProgram, 'get_bom', Mock(return_value='TGLH81')), \
                MockVar(pf, 'CALLERBIN', f'{CALLERBIN.replace("test/", "")}'), \
                MockVar(os.environ, 'PYTEST_CURRENT_TEST', 'True'), \
                MockVar(os.environ, 'FROM_PR', 'True'):
            ut.main()

        expect = f'''
270 FLOW ProgramFlows.py does not match with ProgramFlows.mtpl!
'''
        self.assertTextEqual(ut.ut_result(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_programflow_match(self):
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.py').touch('''
''', mkdir=True)
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.mtpl').touch('''
something here
''', mkdir=True)
        File('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl').touch('''
''', mkdir=True)
        File('Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows_Config.py').touch('''
''', mkdir=True)

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        tpldir = tpobj.tpldir
        ut = ProgramFlowChecker(tpobj)
        ut.tpobjfull = ut.tpobj

        programflow_path = os.path.abspath(f'./POR_TP/TGLH81/ProgramFlowsTestPlan/')
        sharedflow_path = os.path.abspath(f'./Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/')

        ipc_original_lines = "IPC_FLOWS.mptl contents are the same"
        ipc_new_lines = "IPC_FLOWS.mptl contents are the same"

        pgmflow_original_lines = "ProgramFlow.mtpl contents are the same"
        pgmflow_new_lines = "ProgramFlow.mtpl contents are the same"

        # Mock the File.read method to return predefined values
        with patch('gadget.files.File.read', side_effect=[ipc_original_lines, ipc_new_lines, pgmflow_original_lines, pgmflow_new_lines]), \
                MockVar(PyMtpl, 'run', Mock()):
            ut.check_ip_flows(programflow_path)
            ut.check_programflow(programflow_path, sharedflow_path)

        # assert pass
        self.assertEqual(ut.passed, {(270, ProgramFlowChecker.ERROR_TYPE): 2})

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_ipflow_not_match(self):
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.py').touch('''
''', mkdir=True)
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.mtpl').touch('''
something here
''', mkdir=True)
        File('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl').touch('''
''', mkdir=True)
        File('Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows_Config.py').touch('''
''', mkdir=True)

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        tpldir = tpobj.tpldir
        ut = ProgramFlowChecker(tpobj)
        ut.tpobjfull = ut.tpobj

        programflow_path = os.path.abspath(f'./POR_TP/TGLH81/ProgramFlowsTestPlan/')
        sharedflow_path = os.path.abspath(f'./Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/')

        ipc_original_lines = "IPC_FLOWS.mptl contents are the same"
        ipc_new_lines = "IPC_FLOWS.mptl contents are NOT the same"

        # Mock the File.read method to return predefined values
        with patch('gadget.files.File.read', side_effect=[ipc_original_lines, ipc_new_lines]), \
                MockVar(PyMtpl, 'run', Mock()):
            ut.check_ip_flows(programflow_path)

        # assert fail
        expect = [{
            'message': 'IPC_FLOWS.py does not match with IPC_FLOWS.mtpl!',
            'id': 270,
            'module': ProgramFlowChecker.ERROR_TYPE}]
        self.assertEqual(ut.result, expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_programflow_not_match(self):
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.py').touch('''
''', mkdir=True)
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.mtpl').touch('''
something here
''', mkdir=True)
        File('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl').touch('''
''', mkdir=True)
        File('Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows_Config.py').touch('''
''', mkdir=True)

        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        tpldir = tpobj.tpldir
        ut = ProgramFlowChecker(tpobj)
        ut.tpobjfull = ut.tpobj

        programflow_path = os.path.abspath(f'./POR_TP/TGLH81/ProgramFlowsTestPlan/')
        sharedflow_path = os.path.abspath(f'./Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/')

        ipc_original_lines = "IPC_FLOWS.mptl contents are the same"
        ipc_new_lines = "IPC_FLOWS.mptl contents are the same"

        pgmflow_original_lines = "ProgramFlow.mtpl contents are the same"
        pgmflow_new_lines = "ProgramFlow.mtpl contents are NOT the same"

        # Mock the File.read method to return predefined values
        with patch('gadget.files.File.read', side_effect=[ipc_original_lines, ipc_new_lines, pgmflow_original_lines, pgmflow_new_lines]), \
                MockVar(PyMtpl, 'run', Mock()):
            ut.check_ip_flows(programflow_path)
            ut.check_programflow(programflow_path, sharedflow_path)

        # assert fail
        expect = [{
            'message': 'ProgramFlows.py does not match with ProgramFlows.mtpl!',
            'id': 270,
            'module': ProgramFlowChecker.ERROR_TYPE}]
        self.assertEqual(ut.result, expect)


if __name__ == '__main__':
    unittest.main()
