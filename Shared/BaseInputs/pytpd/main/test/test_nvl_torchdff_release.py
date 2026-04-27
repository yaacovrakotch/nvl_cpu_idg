#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_torchdff_release.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV  # must be first import for unittests
from main.nvl_torchdff_release import *
from gadget.ut import TestCase, unittest, patch, MagicMock, Mock
from gadget.pylog import log
from gadget.files import File, TempDir
from gadget.getgit import GitOperations
from gadget.shell import SystemCall
from gadget.disk import Chdir
import glob
import re
import sys
import os
import json
from os.path import basename, join
from datetime import datetime


class TestDffProc(TestCase):

    def setUp(self):
        """Set up test environment with mock product mapping."""
        # Mock the PRODUCT_MAPPING environment variable
        self.test_product_mapping = {
            "HX28C": "Product_HX_8+16+4+64EU_HX28C",
            "H16C": "Product_H_4+8+4+64EU_H16C",
            "P16C": "Product_P_4+8+4+192EU_P16C",
            "DNLS28C": "Product_S_8+16+4+32EU_DNLS28C",
            "S16C": "Product_S_4+8+4+32EU_S16C",
            "S28C": "Product_S_8+16+4+32EU_S28C",
            "S28C_A0": "Product_S_8+16+4+32EU_S28C_A0",
            "S52C": "Product_S_16+32+4+32EU_S52C"
        }

        # Patch the environment variable
        self.env_patcher = patch.dict(os.environ, {
            'PRODUCT_MAPPING': json.dumps(self.test_product_mapping)
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    def test_load_product_mapping_success(self):
        """Test successful loading of product mapping from environment."""
        obj = DffProc()
        self.assertEqual(obj.product_mapping, self.test_product_mapping)
        log.info("Product mapping loaded successfully")

    def test_load_product_mapping_missing_env(self):
        """Test that script exits when PRODUCT_MAPPING is missing."""
        # Temporarily remove the environment variable
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as cm:
                DffProc()
            self.assertEqual(cm.exception.code, 1)
        log.info("Missing environment variable test passed")

    def test_load_product_mapping_invalid_json(self):
        """Test that script exits when PRODUCT_MAPPING contains invalid JSON."""
        with patch.dict(os.environ, {'PRODUCT_MAPPING': 'invalid json'}):
            with self.assertRaises(SystemExit) as cm:
                DffProc()
            self.assertEqual(cm.exception.code, 1)
        log.info("Invalid JSON test passed")

    def test_cl2rc(self):
        with TempDir(name=True, chdir=True) as tdir:
            # Create sample XML files with specified names
            filenames = [
                'Product_S_8+16+4+32EU_S28C_B0_OLF.xml',
                'Product_S_8+16+4+32EU_S28C_B0_Class.xml',
                'Product_S_16+32+4+32EU_S52C_OLF.xml',
                'Product_S_16+32+4+32EU_S52C_Class.xml',
                'Product_HX_8+16+4+64EU_HX28C_OLF.xml',
                'Product_HX_8+16+4+64EU_HX28C_Class.xml'
            ]

            dffdata = """<Token>
                <dff_token_id>1</dff_token_id>
                <name>OLBCC2</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
                <MTL_Name>Product_HX_8+16+4+64EU_HX28C_Class</MTL_Name>
                <Created_By>samrenji</Created_By>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>OLBPC2</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
                <MTL_Name>Product_HX_8+16+4+64EU_HX28C_Class</MTL_Name>
                <Created_By>samrenji</Created_By>
            </Token>"""

            # Create files with sample data
            for filename in filenames:
                File(filename).touch(dffdata, mkdir=True, newfile=True)

            obj = DffProc()
            new_dir_path = obj.cl2rc(tdir)

            # Update <Created_By> tag with a test email
            test_email = "test.email@example.com"
            obj.update_created_by(new_dir_path, test_email)

            # Debugging: Print files in the new directory
            log.info(f"Files in new directory: {glob.glob(join(new_dir_path, '*.xml'))}")

            # Expected content for RAWCLASS.xml files
            expect_rc = f"""<Token>
                <dff_token_id>1</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
                <MTL_Name>Product_HX_8+16+4+64EU_HX28C_RawClass</MTL_Name>
                <Created_By>{test_email}</Created_By>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>OLBPC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
                <MTL_Name>Product_HX_8+16+4+64EU_HX28C_RawClass</MTL_Name>
                <Created_By>{test_email}</Created_By>
            </Token>"""

            # Expected content for CLASS.xml files
            dffclassdata = f"""<Token>
                <dff_token_id>1</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
                <MTL_Name>Product_HX_8+16+4+64EU_HX28C_Class</MTL_Name>
                <Created_By>{test_email}</Created_By>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>OLBPC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
                <MTL_Name>Product_HX_8+16+4+64EU_HX28C_Class</MTL_Name>
                <Created_By>{test_email}</Created_By>
            </Token>"""

            # Verify the content of the files in the new directory
            for filename in filenames:
                # Updated filename extraction logic - everything after third underscore
                parts = filename.split('_')
                if len(parts) > 3:
                    suffix_parts = parts[3:]
                    base_name = '_'.join(suffix_parts[:-1])  # Everything except the last part (Class/OLF)
                else:
                    base_name = parts[-2]  # Fallback to old logic

                if '_Class.xml' in filename:
                    # Check CLASS.xml content
                    class_filename = f"NVL_{base_name}_CLASS.xml"
                    if File(join(new_dir_path, class_filename)).exists():
                        log.info(f"File exists: {class_filename}")
                        self.assertTextEqual(File(join(new_dir_path, class_filename)).read(), dffclassdata)
                        log.info(f"Content check passed for: {class_filename}")
                    else:
                        log.error(f"File not found: {class_filename}")
                        self.fail(f"File not found: {class_filename}")

                    # Check RAWCLASS.xml content
                    raw_class_filename = f"NVL_{base_name}_RAWCLASS.xml"
                    if File(join(new_dir_path, raw_class_filename)).exists():
                        log.info(f"File exists: {raw_class_filename}")
                        self.assertTextEqual(File(join(new_dir_path, raw_class_filename)).read(), expect_rc)
                        log.info(f"Content check passed for: {raw_class_filename}")
                    else:
                        log.error(f"File not found: {raw_class_filename}")
                        self.fail(f"File not found: {raw_class_filename}")

                elif '_OLF.xml' in filename:
                    # Check OLF.xml existence
                    olf_filename = f"NVL_{base_name}_OLF.xml"
                    if File(join(new_dir_path, olf_filename)).exists():
                        log.info(f"File exists: {olf_filename}")
                    else:
                        log.error(f"File not found: {olf_filename}")
                        self.fail(f"File not found: {olf_filename}")

    def test_find_available_branch_name(self):
        """Test the new timestamp-based branch name generation."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Use create_patch from TestCase instead of patch context manager
            mock_datetime = self.create_patch('main.nvl_torchdff_release.datetime')
            mock_datetime.now.return_value.strftime.return_value = '241201_143022'

            branch_name = obj.find_available_branch_name(tdir)

            expected_branch = "NVLDFF/MTL_FilesUpdate_241201_143022"
            self.assertEqual(branch_name, expected_branch)
            log.info(f"Generated branch name: {branch_name}")

    def test_run_torch_commands_product_selection(self):
        """Test the improved product selection logic."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create mock directory structure
            mydffmgmt_dir = join(tdir, "MyDffMgmt")
            os.makedirs(mydffmgmt_dir)

            # Create product folders using the mapping
            product_folders = [
                "Product_HX_8+16+4+64EU_HX28C",
                "Product_H_4+8+4+64EU_H16C",
                "Product_S_4+8+4+32EU_S16C",
                "Product_S_8+16+4+32EU_S28C"
            ]

            for folder in product_folders:
                os.makedirs(join(mydffmgmt_dir, folder))

            # Create mock solution and project files
            File(join(tdir, "test.sln")).touch("mock solution", mkdir=True, newfile=True)
            File(join(mydffmgmt_dir, "test.dffproj")).touch("mock project", mkdir=True, newfile=True)

            # Use create_patch from TestCase
            mock_syscall = self.create_patch('main.nvl_torchdff_release.SystemCall')
            mock_syscall.return_value.run_outtxt.return_value = (0, "success")

            # Test single product selection
            processed_files = obj.run_torch_commands(
                repo_path=tdir,
                output_dir=tdir,
                product_selection="HX28C"
            )

            # Verify that SystemCall was called for the correct product
            self.assertTrue(mock_syscall.called, "SystemCall should have been called")

            # Check that the correct product folder was used
            found_hx28c = False
            for call in mock_syscall.call_args_list:
                command = call[0][0]  # First argument of the call
                if "Product_HX_8+16+4+64EU_HX28C" in ' '.join(command):
                    found_hx28c = True
                    break

            self.assertTrue(found_hx28c, "HX28C product should be processed")
            log.info("Product selection test passed")

    def test_run_torch_commands_multiple_products(self):
        """Test multiple product selection."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create mock directory structure
            mydffmgmt_dir = join(tdir, "MyDffMgmt")
            os.makedirs(mydffmgmt_dir)

            # Create product folders
            product_folders = [
                "Product_HX_8+16+4+64EU_HX28C",
                "Product_S_4+8+4+32EU_S16C",
                "Product_S_8+16+4+32EU_S28C"
            ]

            for folder in product_folders:
                os.makedirs(join(mydffmgmt_dir, folder))

            # Create mock solution and project files
            File(join(tdir, "test.sln")).touch("mock solution", mkdir=True, newfile=True)
            File(join(mydffmgmt_dir, "test.dffproj")).touch("mock project", mkdir=True, newfile=True)

            # Use create_patch from TestCase
            mock_syscall = self.create_patch('main.nvl_torchdff_release.SystemCall')
            mock_syscall.return_value.run_outtxt.return_value = (0, "success")

            # Test multiple product selection
            processed_files = obj.run_torch_commands(
                repo_path=tdir,
                output_dir=tdir,
                product_selection="HX28C,S16C"
            )

            # Verify that SystemCall was called for both products
            self.assertTrue(len(mock_syscall.call_args_list) >= 4, "Should have at least 4 calls (2 products 2 types)")

            # Check that both products were processed
            found_hx28c = False
            found_s16c = False

            for call in mock_syscall.call_args_list:
                command = call[0][0]
                command_str = ' '.join(command)
                if "Product_HX_8+16+4+64EU_HX28C" in command_str:
                    found_hx28c = True
                if "Product_S_4+8+4+32EU_S16C" in command_str:
                    found_s16c = True

            self.assertTrue(found_hx28c, "HX28C product should be processed")
            self.assertTrue(found_s16c, "S16C product should be processed")
            log.info("Multiple product selection test passed")

    def test_s28c_vs_s28c_a0_selection(self):
        """Test that S28C and S28C_A0 are selected correctly without confusion."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create mock directory structure
            mydffmgmt_dir = join(tdir, "MyDffMgmt")
            os.makedirs(mydffmgmt_dir)

            # Create both S28C and S28C_A0 folders
            product_folders = [
                "Product_S_8+16+4+32EU_S28C",
                "Product_S_8+16+4+32EU_S28C_A0"
            ]

            for folder in product_folders:
                os.makedirs(join(mydffmgmt_dir, folder))

            # Create mock solution and project files
            File(join(tdir, "test.sln")).touch("mock solution", mkdir=True, newfile=True)
            File(join(mydffmgmt_dir, "test.dffproj")).touch("mock project", mkdir=True, newfile=True)

            # Use create_patch from TestCase
            mock_syscall = self.create_patch('main.nvl_torchdff_release.SystemCall')
            mock_syscall.return_value.run_outtxt.return_value = (0, "success")

            # Test selecting only S28C
            processed_files = obj.run_torch_commands(
                repo_path=tdir,
                output_dir=tdir,
                product_selection="S28C"
            )

            # Verify that only S28C was processed, not S28C_A0
            found_s28c = False
            found_s28c_a0 = False

            for call in mock_syscall.call_args_list:
                command = call[0][0]
                command_str = ' '.join(command)
                if "Product_S_8+16+4+32EU_S28C" in command_str and "S28C_A0" not in command_str:
                    found_s28c = True
                if "Product_S_8+16+4+32EU_S28C_A0" in command_str:
                    found_s28c_a0 = True

            self.assertTrue(found_s28c, "S28C product should be processed")
            self.assertFalse(found_s28c_a0, "S28C_A0 product should NOT be processed when selecting S28C")
            log.info("S28C vs S28C_A0 selection test passed")

    def test_s28c_a0_selection(self):
        """Test that S28C_A0 can be selected independently."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create mock directory structure
            mydffmgmt_dir = join(tdir, "MyDffMgmt")
            os.makedirs(mydffmgmt_dir)

            # Create both S28C and S28C_A0 folders
            product_folders = [
                "Product_S_8+16+4+32EU_S28C",
                "Product_S_8+16+4+32EU_S28C_A0"
            ]

            for folder in product_folders:
                os.makedirs(join(mydffmgmt_dir, folder))

            # Create mock solution and project files
            File(join(tdir, "test.sln")).touch("mock solution", mkdir=True, newfile=True)
            File(join(mydffmgmt_dir, "test.dffproj")).touch("mock project", mkdir=True, newfile=True)

            # Use create_patch from TestCase
            mock_syscall = self.create_patch('main.nvl_torchdff_release.SystemCall')
            mock_syscall.return_value.run_outtxt.return_value = (0, "success")

            # Test selecting only S28C_A0
            processed_files = obj.run_torch_commands(
                repo_path=tdir,
                output_dir=tdir,
                product_selection="S28C_A0"
            )

            # Verify that only S28C_A0 was processed
            found_s28c = False
            found_s28c_a0 = False

            for call in mock_syscall.call_args_list:
                command = call[0][0]
                command_str = ' '.join(command)
                if "Product_S_8+16+4+32EU_S28C_A0" in command_str:
                    found_s28c_a0 = True
                elif "Product_S_8+16+4+32EU_S28C" in command_str:
                    found_s28c = True

            self.assertTrue(found_s28c_a0, "S28C_A0 product should be processed")
            self.assertFalse(found_s28c, "S28C product should NOT be processed when selecting S28C_A0")
            log.info("S28C_A0 selection test passed")

    def test_update_git_repo_branch_naming(self):
        """Test the git repository update with new branch naming."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create a mock new_dir_path with XML files
            new_dir_path = join(tdir, "test_files")
            os.makedirs(new_dir_path)
            File(join(new_dir_path, "test.xml")).touch("test content", mkdir=True, newfile=True)

            # Create a mock common_clone_dir
            common_clone_dir = join(tdir, "common_repo")
            os.makedirs(common_clone_dir)

            # Use create_patch from TestCase for multiple patches
            mock_git = self.create_patch('main.nvl_torchdff_release.GitOperations')
            mock_datetime = self.create_patch('main.nvl_torchdff_release.datetime')

            # Configure the mocks
            mock_datetime.now.return_value.strftime.side_effect = lambda fmt: {
                '%y%m%d_%H%M%S': '241201_143022',
                '%Y-%m-%d %H:%M:%S': '2024-12-01 14:30:22'
            }[fmt]

            # Mock environment variable
            with patch.dict(os.environ, {'DFFTOK': 'mock_token'}):
                # Test the update_git_repo method without product selection
                obj.update_git_repo(new_dir_path, common_clone_dir, "test@example.com")

                # Verify that create_branch was called with the correct branch name
                expected_branch = "NVLDFF/MTL_FilesUpdate_241201_143022"
                mock_git.create_branch.assert_called_once_with(common_clone_dir, expected_branch)

                # Verify other Git operations were called
                mock_git.commit_changes.assert_called_once()
                mock_git.push_branch.assert_called_once_with(common_clone_dir, expected_branch)
                mock_git.create_pull_request.assert_called_once()

                log.info("Git repository update test passed")

    def test_update_git_repo_with_product_prefix_single(self):
        """Test git repository update with single product prefix."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create a mock new_dir_path with XML files
            new_dir_path = join(tdir, "test_files")
            os.makedirs(new_dir_path)
            File(join(new_dir_path, "test.xml")).touch("test content", mkdir=True, newfile=True)

            # Create a mock common_clone_dir
            common_clone_dir = join(tdir, "common_repo")
            os.makedirs(common_clone_dir)

            # Use create_patch from TestCase for multiple patches
            mock_git = self.create_patch('main.nvl_torchdff_release.GitOperations')
            mock_datetime = self.create_patch('main.nvl_torchdff_release.datetime')

            # Configure the mocks
            mock_datetime.now.return_value.strftime.side_effect = lambda fmt: {
                '%y%m%d_%H%M%S': '241201_143022',
                '%Y-%m-%d %H:%M:%S': '2024-12-01 14:30:22'
            }[fmt]

            # Mock environment variable
            with patch.dict(os.environ, {'DFFTOK': 'mock_token'}):
                # Test with single product selection
                obj.update_git_repo(new_dir_path, common_clone_dir, "test@example.com", "HX28C")

                # Verify commit message has the correct prefix
                commit_call = mock_git.commit_changes.call_args
                commit_message = commit_call[0][2]  # Third argument is the commit message
                self.assertTrue(commit_message.startswith("[HX28C] "), f"Commit message should start with '[HX28C] ', got: {commit_message}")

                # Verify PR title has the correct prefix
                pr_call = mock_git.create_pull_request.call_args
                pr_kwargs = pr_call[1]  # Keyword arguments
                pr_title = pr_kwargs['pr_title']
                self.assertTrue(pr_title.startswith("[HX28C] "), f"PR title should start with '[HX28C] ', got: {pr_title}")

                log.info("Single product prefix test passed")

    def test_update_git_repo_with_product_prefix_multiple(self):
        """Test git repository update with multiple product prefix."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create a mock new_dir_path with XML files
            new_dir_path = join(tdir, "test_files")
            os.makedirs(new_dir_path)
            File(join(new_dir_path, "test.xml")).touch("test content", mkdir=True, newfile=True)

            # Create a mock common_clone_dir
            common_clone_dir = join(tdir, "common_repo")
            os.makedirs(common_clone_dir)

            # Use create_patch from TestCase for multiple patches
            mock_git = self.create_patch('main.nvl_torchdff_release.GitOperations')
            mock_datetime = self.create_patch('main.nvl_torchdff_release.datetime')

            # Configure the mocks
            mock_datetime.now.return_value.strftime.side_effect = lambda fmt: {
                '%y%m%d_%H%M%S': '241201_143022',
                '%Y-%m-%d %H:%M:%S': '2024-12-01 14:30:22'
            }[fmt]

            # Mock environment variable
            with patch.dict(os.environ, {'DFFTOK': 'mock_token'}):
                # Test with multiple product selection
                obj.update_git_repo(new_dir_path, common_clone_dir, "test@example.com", "HX28C,S28C")

                # Verify commit message has the correct prefix
                commit_call = mock_git.commit_changes.call_args
                commit_message = commit_call[0][2]  # Third argument is the commit message
                self.assertTrue(commit_message.startswith("[HX28C,S28C] "), f"Commit message should start with '[HX28C,S28C] ', got: {commit_message}")

                # Verify PR title has the correct prefix
                pr_call = mock_git.create_pull_request.call_args
                pr_kwargs = pr_call[1]  # Keyword arguments
                pr_title = pr_kwargs['pr_title']
                self.assertTrue(pr_title.startswith("[HX28C,S28C] "), f"PR title should start with '[HX28C,S28C] ', got: {pr_title}")

                log.info("Multiple product prefix test passed")

    def test_update_git_repo_with_product_prefix_all(self):
        """Test git repository update with ALL product prefix."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create a mock new_dir_path with XML files
            new_dir_path = join(tdir, "test_files")
            os.makedirs(new_dir_path)
            File(join(new_dir_path, "test.xml")).touch("test content", mkdir=True, newfile=True)

            # Create a mock common_clone_dir
            common_clone_dir = join(tdir, "common_repo")
            os.makedirs(common_clone_dir)

            # Use create_patch from TestCase for multiple patches
            mock_git = self.create_patch('main.nvl_torchdff_release.GitOperations')
            mock_datetime = self.create_patch('main.nvl_torchdff_release.datetime')

            # Configure the mocks
            mock_datetime.now.return_value.strftime.side_effect = lambda fmt: {
                '%y%m%d_%H%M%S': '241201_143022',
                '%Y-%m-%d %H:%M:%S': '2024-12-01 14:30:22'
            }[fmt]

            # Mock environment variable
            with patch.dict(os.environ, {'DFFTOK': 'mock_token'}):
                # Test with ALL product selection
                obj.update_git_repo(new_dir_path, common_clone_dir, "test@example.com", "ALL")

                # Verify commit message has the correct prefix
                commit_call = mock_git.commit_changes.call_args
                commit_message = commit_call[0][2]  # Third argument is the commit message
                self.assertTrue(commit_message.startswith("[ALL] "), f"Commit message should start with '[ALL] ', got: {commit_message}")

                # Verify PR title has the correct prefix
                pr_call = mock_git.create_pull_request.call_args
                pr_kwargs = pr_call[1]  # Keyword arguments
                pr_title = pr_kwargs['pr_title']
                self.assertTrue(pr_title.startswith("[ALL] "), f"PR title should start with '[ALL] ', got: {pr_title}")

                log.info("ALL product prefix test passed")

    def test_unknown_product_selection(self):
        """Test handling of unknown product selections."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create mock directory structure
            mydffmgmt_dir = join(tdir, "MyDffMgmt")
            os.makedirs(mydffmgmt_dir)

            # Create some product folders
            os.makedirs(join(mydffmgmt_dir, "Product_HX_8+16+4+64EU_HX28C"))

            # Create mock solution and project files
            File(join(tdir, "test.sln")).touch("mock solution", mkdir=True, newfile=True)
            File(join(mydffmgmt_dir, "test.dffproj")).touch("mock project", mkdir=True, newfile=True)

            # Test with unknown product
            processed_files = obj.run_torch_commands(
                repo_path=tdir,
                output_dir=tdir,
                product_selection="UNKNOWN_PRODUCT"
            )

            # Should return empty list for unknown products
            self.assertEqual(processed_files, [])
            log.info("Unknown product selection test passed")

    def test_update_created_by(self):
        """Test the update_created_by functionality."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create test XML file with original Created_By tag
            test_xml_content = """<Token>
                <dff_token_id>1</dff_token_id>
                <name>OLBCC</name>
                <Created_By>original@example.com</Created_By>
            </Token>"""

            test_file = join(tdir, "test.xml")
            File(test_file).touch(test_xml_content, mkdir=True, newfile=True)

            # Update the Created_By tag
            new_email = "updated@example.com"
            obj.update_created_by(tdir, new_email)

            # Verify the update
            updated_content = File(test_file).read()
            self.assertIn(f"<Created_By>{new_email}</Created_By>", updated_content)
            self.assertNotIn("original@example.com", updated_content)
            log.info("Update Created_By test passed")

    def test_move_xml_files(self):
        """Test the move_xml_files functionality."""
        with TempDir(name=True) as tdir:
            obj = DffProc()

            # Create test XML files
            test_files = []
            for i in range(3):
                test_file = join(tdir, f"test_{i}.xml")
                File(test_file).touch(f"content {i}", mkdir=True, newfile=True)
                test_files.append(test_file)

            # Mock datetime for predictable directory naming
            mock_datetime = self.create_patch('main.nvl_torchdff_release.datetime')
            mock_datetime.now.return_value.strftime.return_value = '241201'

            # Move the files
            new_dir_path = obj.move_xml_files(tdir, test_files)

            # Verify the new directory was created
            self.assertTrue(os.path.exists(new_dir_path))
            self.assertTrue("241201_A" in new_dir_path)

            # Verify files were moved
            for i in range(3):
                moved_file = join(new_dir_path, f"test_{i}.xml")
                self.assertTrue(os.path.exists(moved_file))
                self.assertEqual(File(moved_file).read(), f"content {i}")

            log.info("Move XML files test passed")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
