#!/usr/intel/pkgs/python3/3.6.3a/modules/r1/bin/python3 -u
"""
Unit test for easyautopep8.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock, patch
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdout
import sys
import os
import subprocess


class TestEasyAutopep8(TestCase):

    def test_main_with_files_success(self):
        # Test successful execution with file arguments
        test_files = ['file1.py', 'file2.py']
        cmd = ['easyautopep8.py'] + test_files

        # Mock subprocess.run to return success
        mock_result = Mock()
        mock_result.returncode = 0

        with MockVar(sys, 'argv', cmd):
            with patch('subprocess.run', return_value=mock_result) as mock_run:
                with patch('os.path.exists', return_value=True):
                    with CaptureStdout() as output:
                        from main import easyautopep8
                        with self.assertRaises(SystemExit) as cm:
                            easyautopep8.main()

                        # Verify subprocess.run was called with correct arguments
                        self.assertEqual(mock_run.call_count, 1)
                        call_args = mock_run.call_args[0][0]

                        # Check that files are in the command
                        self.assertIn('file1.py', call_args)
                        self.assertIn('file2.py', call_args)

                        # Check that required autopep8 arguments are present
                        self.assertIn('-i', call_args)
                        self.assertIn('-r', call_args)
                        self.assertIn('--ignore=E402,E501,W503,W504,W605,E712', call_args)
                        self.assertIn('-aaa', call_args)
                        self.assertIn('-p', call_args)
                        self.assertIn('50', call_args)

                        # Check that check=True was passed
                        self.assertTrue(mock_run.call_args[1]['check'])

                        # Verify sys.exit was called with 0
                        self.assertEqual(cm.exception.code, 0)

                        # Verify output contains command
                        self.assertIn('Running:', output.getvalue())

    def test_main_no_files_error(self):
        # Test error when no files are provided
        cmd = ['easyautopep8.py']

        with MockVar(sys, 'argv', cmd):
            with patch('os.path.exists', return_value=True):
                with CaptureStdout() as output:
                    from main import easyautopep8
                    with self.assertRaises(SystemExit) as cm:
                        easyautopep8.main()

                    # Verify sys.exit was called with 1
                    self.assertEqual(cm.exception.code, 1)

                    # Verify usage message is printed
                    output_text = output.getvalue()
                    self.assertIn('Usage:', output_text)
                    self.assertIn('Example:', output_text)

    def test_main_autopep8_not_found(self):
        # Test error when autopep8.py is not found
        cmd = ['easyautopep8.py', 'test.py']

        with MockVar(sys, 'argv', cmd):
            with patch('os.path.exists', return_value=False):
                with CaptureStdout() as output:
                    from main import easyautopep8
                    with self.assertRaises(SystemExit) as cm:
                        easyautopep8.main()

                    # Verify sys.exit was called with 1
                    self.assertEqual(cm.exception.code, 1)

                    # Verify error message is printed
                    self.assertIn('Error: autopep8.py not found', output.getvalue())

    def test_main_subprocess_error(self):
        # Test handling of subprocess.CalledProcessError
        cmd = ['easyautopep8.py', 'test.py']

        # Create a CalledProcessError
        error = subprocess.CalledProcessError(2, 'autopep8')

        with MockVar(sys, 'argv', cmd):
            with patch('subprocess.run', side_effect=error):
                with patch('os.path.exists', return_value=True):
                    with CaptureStdout() as output:
                        from main import easyautopep8
                        with self.assertRaises(SystemExit) as cm:
                            easyautopep8.main()

                        # Verify sys.exit was called with error returncode
                        self.assertEqual(cm.exception.code, 2)

                        # Verify error message is printed
                        self.assertIn('Error running autopep8:', output.getvalue())

    def test_main_unexpected_error(self):
        # Test handling of unexpected exceptions
        cmd = ['easyautopep8.py', 'test.py']

        with MockVar(sys, 'argv', cmd):
            with patch('subprocess.run', side_effect=RuntimeError('Unexpected error')):
                with patch('os.path.exists', return_value=True):
                    with CaptureStdout() as output:
                        from main import easyautopep8
                        with self.assertRaises(SystemExit) as cm:
                            easyautopep8.main()

                        # Verify sys.exit was called with 1
                        self.assertEqual(cm.exception.code, 1)

                        # Verify error message is printed
                        self.assertIn('Unexpected error:', output.getvalue())

    def test_main_multiple_files(self):
        # Test with multiple file arguments
        test_files = ['file1.py', 'file2.py', 'file3.py', 'dir/file4.py']
        cmd = ['easyautopep8.py'] + test_files

        mock_result = Mock()
        mock_result.returncode = 0

        with MockVar(sys, 'argv', cmd):
            with patch('subprocess.run', return_value=mock_result) as mock_run:
                with patch('os.path.exists', return_value=True):
                    from main import easyautopep8
                    with self.assertRaises(SystemExit):
                        easyautopep8.main()

                    # Verify all files are in the command
                    call_args = mock_run.call_args[0][0]
                    for file in test_files:
                        self.assertIn(file, call_args)

    def test_main_uses_current_python(self):
        # Test that script uses current Python interpreter
        cmd = ['easyautopep8.py', 'test.py']

        mock_result = Mock()
        mock_result.returncode = 0

        with MockVar(sys, 'argv', cmd):
            with patch('subprocess.run', return_value=mock_result) as mock_run:
                with patch('os.path.exists', return_value=True):
                    from main import easyautopep8
                    with self.assertRaises(SystemExit):
                        easyautopep8.main()

                    # Verify sys.executable is the first argument
                    call_args = mock_run.call_args[0][0]
                    self.assertEqual(call_args[0], sys.executable)

    def test_main_nonzero_exit_code(self):
        # Test handling of nonzero exit code from subprocess
        cmd = ['easyautopep8.py', 'test.py']

        mock_result = Mock()
        mock_result.returncode = 3

        with MockVar(sys, 'argv', cmd):
            with patch('subprocess.run', return_value=mock_result):
                with patch('os.path.exists', return_value=True):
                    from main import easyautopep8
                    with self.assertRaises(SystemExit) as cm:
                        easyautopep8.main()

                    # Verify sys.exit was called with subprocess returncode
                    self.assertEqual(cm.exception.code, 3)

    def test_command_format(self):
        # Test that the command format matches expected structure
        # Expected: python autopep8.py file1.py file2.py -i -r --ignore=... -aaa -p 50
        cmd = ['easyautopep8.py', 'test1.py', 'test2.py']

        mock_result = Mock()
        mock_result.returncode = 0

        with MockVar(sys, 'argv', cmd):
            with patch('subprocess.run', return_value=mock_result) as mock_run:
                with patch('os.path.exists', return_value=True):
                    from main import easyautopep8
                    with self.assertRaises(SystemExit):
                        easyautopep8.main()

                    call_args = mock_run.call_args[0][0]

                    # Verify order: python, autopep8.py, files, then options
                    self.assertEqual(call_args[0], sys.executable)
                    self.assertTrue(call_args[1].endswith('autopep8.py'))
                    self.assertEqual(call_args[2], 'test1.py')
                    self.assertEqual(call_args[3], 'test2.py')

                    # Verify options come after files
                    files_end_index = call_args.index('test2.py') + 1
                    self.assertEqual(call_args[files_end_index], '-i')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
