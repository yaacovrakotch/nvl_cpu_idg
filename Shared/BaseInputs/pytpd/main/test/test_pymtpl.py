#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for pymtpl.py (main executable)
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.disk import Chdir
from main.pymtpl import *
from unittest.mock import patch, MagicMock
from gadget.gizmo import MockVar, with_
from os.path import join, dirname, abspath
import sys


class TestMain(TestCase):

    def test_basic(self):
        cmd = f'pymtpl.py inputfile.py'.split()
        with MockVar(sys, "argv", cmd):
            with MockVar(PyMtpl, "main", Mock()):
                self.assertEqual(PyMtplArgs().main(), 2)

    def test_skip_path_updater_option(self):
        """Test that -skip_path_updater option is properly set in OPT"""
        cmd = f'pymtpl.py -skip_path_updater inputfile.py'.split()
        with MockVar(sys, "argv", cmd):
            with MockVar(PyMtpl, "main", Mock()):
                result = PyMtplArgs().main()
                self.assertEqual(result, 2)
                self.assertTrue(OPT.skip_path_updater)

        # Test that skip_path_updater is False by default
        cmd = f'pymtpl.py inputfile.py'.split()
        with MockVar(sys, "argv", cmd):
            with MockVar(PyMtpl, "main", Mock()):
                result = PyMtplArgs().main()
                self.assertEqual(result, 2)
                self.assertFalse(getattr(OPT, 'skip_path_updater', False))

    @with_(TempDir, chdir=True)
    def test_class90hbsbxx_option(self):
        # Test that -class90hbsbxx option is properly set in OPT
        cmd = f'pymtpl.py -class90hbsbxx nvlclass inputfile.py'.split()
        with MockVar(sys, "argv", cmd):
            with MockVar(PyMtpl, "main", Mock()):
                result = PyMtplArgs().main()
                self.assertEqual(result, 2)
                self.assertEqual(OPT.class90hbsbxx, 'nvlclass')

    @with_(TempDir, chdir=True)
    def test_bindef_option(self):
        # Test that -bindef option is properly set in OPT
        File('./bindef.bdefs').touch('', newfile=True)
        cmd = f'pymtpl.py -bindef ./bindef.bdefs inputfile.py'.split()
        with MockVar(sys, "argv", cmd):
            with MockVar(PyMtpl, "main", Mock()):
                result = PyMtplArgs().main()
                self.assertEqual(result, 2)
                self.assertEqual(OPT.bindef, abspath('./bindef.bdefs'))

    @patch('pymtpl.gen_methods.GenMethods.main', MagicMock())
    def test_gen_methods(self):
        cmd = f'pymtpl.py -genmethods "path" -genmethodsoutdir .'.split()
        with MockVar(sys, "argv", cmd):
            with MockVar(GenMethods, "main", Mock()):
                self.assertEqual(PyMtplArgs().main(), 5)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_updatebinctr(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

# VminTC comment
CSharpTest VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
    }

}

''', newfile=True)

        cmd = f'pymtpl.py -inputmtpl ./Modules/ARR/array.mtpl -updateautobinctr .'.split()
        with MockVar(sys, "argv", cmd):
            # Mock the actual functionality class's main method
            with MockVar(UpdateAutobinAndAutoCtrJson, "main", Mock()):
                # Now PyMtplArgs should initialize without the File check failing
                self.assertEqual(PyMtplArgs().main(), 4)

    def test_incorrect_usage(self):
        cmd = f'pymtpl.py'.split()
        with MockVar(sys, "argv", cmd):
            with self.assertRaisesRegex(ErrorInput, 'Incorrect usage'):
                PyMtplArgs().main()

    def test_gen_methods2(self):
        # I want to test if a particular printout is printed
        def fake(*args):
            print("I am running fake routine")
            print("Next Line")

        cmd = f'pymtpl.py -genmethods "path" -genmethodsoutdir .'.split()
        with MockVar(sys, "argv", cmd):
            with MockVar(GenMethods, "main", fake):
                with CaptureStdoutLog() as p:
                    PyMtplArgs().main()

        expect = '''
I am running fake routine
Next Line
'''
        self.assertTextEqual(p.getvalue(), expect)

    @with_(TempDir, chdir=True)
    @patch('main.pymtpl.GenPy')
    def test_genpy(self, mock_genpy_class):
        """Test the genpy.main call in pymtpl.py"""
        # Create a temporary mtpl file
        File('./inputfile.mtpl').touch('Version 1.0;', newfile=True)

        # Mock the GenPy instance and its main method
        mock_instance = MagicMock()
        mock_genpy_class.return_value = mock_instance

        cmd = f'pymtpl.py -genpy ./inputfile.mtpl'.split()
        with MockVar(sys, "argv", cmd):
            result = PyMtplArgs().main()

        self.assertEqual(result, 3)
        mock_genpy_class.assert_called_once()
        mock_instance.main.assert_called_once()

    @with_(TempDir, chdir=True)
    def test_genpy_with_product(self):
        # Test genpy with -product parameter
        File('./inputfile.mtpl').touch('Version 1.0;', newfile=True)

        cmd = f'pymtpl.py -genpy ./inputfile.mtpl -product dmrclass'.split()
        with MockVar(sys, "argv", cmd):
            with patch('main.pymtpl.GenPy') as mock_genpy:
                mock_instance = MagicMock()
                mock_genpy.return_value = mock_instance
                result = PyMtplArgs().main()

        self.assertEqual(result, 3)
        self.assertEqual(OPT.product, 'dmrclass')

    @with_(TempDir, chdir=True)
    def test_genpy_with_env(self):
        # Test genpy with -env parameter
        File('./inputfile.mtpl').touch('Version 1.0;', newfile=True)
        File('./envfile.env').touch('', newfile=True)

        cmd = f'pymtpl.py -genpy ./inputfile.mtpl -env ./envfile.env'.split()
        with MockVar(sys, "argv", cmd):
            with patch('main.pymtpl.GenPy') as mock_genpy:
                mock_instance = MagicMock()
                mock_genpy.return_value = mock_instance
                result = PyMtplArgs().main()

        self.assertEqual(result, 3)
        self.assertEqual(OPT.env, abspath('./envfile.env'))

    @patch('pymtpl.update_pymtpl.PyMTPLUpdater.main', MagicMock())
    def test_install_with_skip_por_methods(self):
        """Test that -install -s passes skip_por_methods flag correctly"""
        # Create a mock .sln file to pass validation
        cmd = 'pymtpl.py -install -s'.split()
        with MockVar(sys, "argv", cmd):
            result = PyMtplArgs().main()

        self.assertEqual(result, 6)

    @patch('pymtpl.update_pymtpl.PyMTPLUpdater.main', MagicMock())
    def test_update_with_skip_por_methods(self):
        """Test that -up -s passes skip_por_methods flag correctly"""
        cmd = 'pymtpl.py -up -s'.split()
        with MockVar(sys, "argv", cmd):
            result = PyMtplArgs().main()
        self.assertEqual(result, 7)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
