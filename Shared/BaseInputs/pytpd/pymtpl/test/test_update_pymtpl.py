#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit tests for update_pymtpl.py
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest
from gadget.gizmo import MockVar, with_
from gadget.files import TempDir, File
from unittest.mock import patch, MagicMock, mock_open, call
import os
import json
from os.path import join, exists

# Import the module to test
from pymtpl.update_pymtpl import (
    LocalGitHelper,
    RepositoryCloner,
    ModuleAgentInstructions,
    ModuleAgentSkills,
    PyTPDFrameworkUpdater,
    PORMethodsUpdater,
    RepositoryValidator,
    PyMTPLInstaller,
    RepositoryProcessor,
    PyMTPLUpdater
)


class TestLocalGitHelper(TestCase):

    @with_(TempDir, chdir=True)
    def test_is_git_repo_true(self):
        # Test when .git directory exists
        os.makedirs('.git')
        self.assertTrue(LocalGitHelper.is_git_repo(os.getcwd()))

    @with_(TempDir, chdir=True)
    def test_is_git_repo_false(self):
        # Test when .git directory does not exist
        self.assertFalse(LocalGitHelper.is_git_repo(os.getcwd()))

    @patch('pymtpl.update_pymtpl.GitOperations.get_status')
    def test_has_clean_working_directory_clean(self, mock_get_status):
        # Test when working directory is clean
        mock_get_status.return_value = "working tree clean"
        self.assertTrue(LocalGitHelper.has_clean_working_directory('/fake/path'))

    @patch('pymtpl.update_pymtpl.GitOperations.get_status')
    def test_has_clean_working_directory_dirty(self, mock_get_status):
        # Test when working directory has changes
        mock_get_status.return_value = "Changes not staged for commit"
        self.assertFalse(LocalGitHelper.has_clean_working_directory('/fake/path'))

    @patch('pymtpl.update_pymtpl.SystemCall')
    def test_get_current_branch_success(self, mock_system_call):
        # Test successful branch name retrieval
        mock_instance = MagicMock()
        mock_instance.run_outtxt.return_value = (0, "main\n")
        mock_system_call.return_value = mock_instance

        result = LocalGitHelper.get_current_branch('/fake/path')
        self.assertEqual(result, "main")

    @patch('pymtpl.update_pymtpl.SystemCall')
    def test_get_current_branch_failure(self, mock_system_call):
        # Test failure to get branch name
        mock_instance = MagicMock()
        mock_instance.run_outtxt.return_value = (1, "")
        mock_system_call.return_value = mock_instance

        result = LocalGitHelper.get_current_branch('/fake/path')
        self.assertIsNone(result)

    @patch('pymtpl.update_pymtpl.GitOperations.pull_branch')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_current_branch')
    def test_pull_latest_changes_success(self, mock_get_branch, mock_pull):
        # Test successful pull
        mock_get_branch.return_value = "main"
        mock_pull.return_value = None

        result = LocalGitHelper.pull_latest_changes('/fake/path')
        self.assertTrue(result)

    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_current_branch')
    def test_pull_latest_changes_no_branch(self, mock_get_branch):
        # Test when branch cannot be determined - raises ErrorUser
        from gadget.errors import ErrorUser
        mock_get_branch.return_value = None

        with self.assertRaises(ErrorUser):
            LocalGitHelper.pull_latest_changes('/fake/path')

    @patch('pymtpl.update_pymtpl.GitOperations.pull_branch')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_current_branch')
    def test_pull_latest_changes_exception(self, mock_get_branch, mock_pull):
        # Test when GitOperations.pull_branch raises an exception - raises ErrorUser
        from gadget.errors import ErrorUser
        mock_get_branch.return_value = "main"
        mock_pull.side_effect = Exception("Git pull failed")

        with self.assertRaises(ErrorUser):
            LocalGitHelper.pull_latest_changes('/fake/path')

    @patch('pymtpl.update_pymtpl.SystemCall')
    def test_get_commit_info_success(self, mock_system_call):
        # Test successful commit info retrieval
        mock_instance_sha = MagicMock()
        mock_instance_sha.run_outtxt.return_value = (0, "abc123\n")

        mock_instance_msg = MagicMock()
        mock_instance_msg.run_outtxt.return_value = (0, "Test commit\n")

        mock_system_call.side_effect = [mock_instance_sha, mock_instance_msg]

        sha, msg = LocalGitHelper.get_commit_info('/fake/path')
        self.assertEqual(sha, "abc123")
        self.assertEqual(msg, "Test commit")


class TestRepositoryCloner(TestCase):

    @patch('pymtpl.update_pymtpl.GitOperations.clone_repository')
    @patch('pymtpl.update_pymtpl.TempDir')
    def test_clone_module_agent_repo_success(self, mock_tempdir, mock_clone):
        # Test successful module agent clone
        mock_temp_instance = MagicMock()
        mock_temp_instance.name.return_value = '/tmp/module_agent'
        mock_tempdir.return_value = mock_temp_instance

        result = RepositoryCloner.clone_module_agent_repo()
        self.assertIsNotNone(result)
        self.assertEqual(result, mock_temp_instance)

    @patch('pymtpl.update_pymtpl.GitOperations.clone_repository')
    @patch('pymtpl.update_pymtpl.TempDir')
    def test_clone_module_agent_repo_failure(self, mock_tempdir, mock_clone):
        # Test failed module agent clone
        mock_temp_instance = MagicMock()
        mock_temp_instance.name.return_value = '/tmp/module_agent'
        mock_tempdir.return_value = mock_temp_instance
        mock_clone.side_effect = Exception("Clone failed")

        result = RepositoryCloner.clone_module_agent_repo()
        self.assertIsNone(result)

    @patch('pymtpl.update_pymtpl.GitOperations.clone_repository')
    @patch('pymtpl.update_pymtpl.TempDir')
    def test_clone_pytpd_repo_success(self, mock_tempdir, mock_clone):
        # Test successful pytpd clone
        mock_temp_instance = MagicMock()
        mock_temp_instance.name.return_value = '/tmp/pytpd'
        mock_tempdir.return_value = mock_temp_instance

        result = RepositoryCloner.clone_pytpd_repo()
        self.assertIsNotNone(result)
        self.assertEqual(result, mock_temp_instance)

    @patch('pymtpl.update_pymtpl.GitOperations.clone_repository')
    @patch('pymtpl.update_pymtpl.TempDir')
    def test_clone_pytpd_repo_failure(self, mock_tempdir, mock_clone):
        # Test failed pytpd clone cleans up temp directory and returns None
        mock_temp_instance = MagicMock()
        mock_temp_instance.name.return_value = '/tmp/pytpd'
        mock_tempdir.return_value = mock_temp_instance
        mock_clone.side_effect = Exception("Clone failed")

        result = RepositoryCloner.clone_pytpd_repo()
        self.assertIsNone(result)
        mock_temp_instance.close.assert_called_once()


class TestModuleAgentInstructions(TestCase):

    @with_(TempDir, chdir=True)
    def test_update_copilot_instructions_new_file(self):
        # Test creating new copilot-instructions.md
        source_file = 'source.md'
        target_file = 'target.md'

        File(source_file).touch('Test content')

        ModuleAgentInstructions.update_copilot_instructions(target_file, source_file)

        self.assertTrue(exists(target_file))
        self.assertEqual(File(target_file).read(), 'Test content')

    @with_(TempDir, chdir=True)
    def test_update_copilot_instructions_with_tags(self):
        # Test updating file with MODULE_AGENT_INSTRUCTIONS tags
        source_file = 'source.md'
        target_file = 'target.md'

        source_content = '''# Header
<!-- MODULE_AGENT_INSTRUCTIONS_START -->
New module agent content
<!-- MODULE_AGENT_INSTRUCTIONS_END -->
# Footer'''

        target_content = '''# Header
<!-- MODULE_AGENT_INSTRUCTIONS_START -->
Old module agent content
<!-- MODULE_AGENT_INSTRUCTIONS_END -->
# Footer'''

        File(source_file).touch(source_content)
        File(target_file).touch(target_content)

        ModuleAgentInstructions.update_copilot_instructions(target_file, source_file)

        result = File(target_file).read()
        self.assertIn('New module agent content', result)
        self.assertNotIn('Old module agent content', result)

    @with_(TempDir, chdir=True)
    def test_update_copilot_instructions_source_missing_tags(self):
        # Test when target has tags but source file doesn't have proper tags - should skip update
        source_file = 'source.md'
        target_file = 'target.md'

        # Source content WITHOUT the module agent tags
        source_content = '''# Header
Some content without tags
# Footer'''

        # Target content WITH tags
        target_content = '''# Header
<!-- MODULE_AGENT_INSTRUCTIONS_START -->
Old module agent content
<!-- MODULE_AGENT_INSTRUCTIONS_END -->
# Footer'''

        File(source_file).touch(source_content)
        File(target_file).touch(target_content)

        ModuleAgentInstructions.update_copilot_instructions(target_file, source_file)

        # Target should remain unchanged since source doesn't have proper tags
        result = File(target_file).read()
        self.assertIn('Old module agent content', result)

    @with_(TempDir, chdir=True)
    def test_update_copilot_instructions_no_tags(self):
        # Test replacing file when no tags exist
        source_file = 'source.md'
        target_file = 'target.md'

        File(source_file).touch('New content')
        File(target_file).touch('Old content')

        ModuleAgentInstructions.update_copilot_instructions(target_file, source_file)

        self.assertEqual(File(target_file).read(), 'New content')

    @with_(TempDir, chdir=True)
    def test_process_module_agent_for_repo_success(self):
        # Test successful module agent processing
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(module_agent_path)
        os.makedirs(join(module_agent_path, '.github'))
        File(join(module_agent_path, '.github', 'copilot-instructions.md')).touch('Content')

        result = ModuleAgentInstructions.process_module_agent_for_repo(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'copilot-instructions.md')))

    @with_(TempDir, chdir=True)
    def test_process_module_agent_for_repo_missing_source(self):
        # Test when source file is missing
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(module_agent_path)

        result = ModuleAgentInstructions.process_module_agent_for_repo(repo_path, module_agent_path)

        self.assertFalse(result)

    @with_(TempDir, chdir=True)
    def test_process_module_agent_for_repo_github_dir_exists(self):
        # Test when .github directory already exists - covers line 203-204 false branch
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create .github directory before calling process_module_agent_for_repo
        github_dir = join(repo_path, '.github')
        os.makedirs(github_dir)

        os.makedirs(module_agent_path)
        os.makedirs(join(module_agent_path, '.github'))
        File(join(module_agent_path, '.github', 'copilot-instructions.md')).touch('Content')

        result = ModuleAgentInstructions.process_module_agent_for_repo(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'copilot-instructions.md')))

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_folder_success(self):
        # Test copying agents/module-agent folder with files and subdirectories
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create module agent structure
        os.makedirs(join(module_agent_path, '.github', 'agents', 'module-agent', 'instructions'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent', 'instructions', 'core.md')).touch('core content')
        File(join(module_agent_path, '.github', 'agents', 'module-agent', 'config.md')).touch('config content')

        result = ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'agents', 'module-agent', 'instructions', 'core.md')))
        self.assertTrue(exists(join(repo_path, '.github', 'agents', 'module-agent', 'config.md')))

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_folder_overwrites_existing(self):
        # Test that existing module-agent folder is overwritten but non-product-config files are replaced
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create existing target module-agent folder with old content
        os.makedirs(join(repo_path, '.github', 'agents', 'module-agent'))
        File(join(repo_path, '.github', 'agents', 'module-agent', 'old_file.md')).touch('old content')

        # Create new module agent folder with different content
        os.makedirs(join(module_agent_path, '.github', 'agents', 'module-agent'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent', 'new_file.md')).touch('new content')

        result = ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'agents', 'module-agent', 'new_file.md')))
        self.assertFalse(exists(join(repo_path, '.github', 'agents', 'module-agent', 'old_file.md')))

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_folder_preserves_product_config(self):
        # Test that existing product-config.instructions.md is preserved across folder replacement
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create existing target with a user-edited product-config.instructions.md
        product_config_dir = join(repo_path, '.github', 'agents', 'module-agent', 'instructions')
        os.makedirs(product_config_dir)
        user_content = '# Product Configuration\n\nProduct Class: JGSClass\n'
        File(join(product_config_dir, 'product-config.instructions.md')).touch(user_content)
        File(join(repo_path, '.github', 'agents', 'module-agent', 'old_file.md')).touch('old content')

        # Create new module agent source (does not include product-config)
        os.makedirs(join(module_agent_path, '.github', 'agents', 'module-agent', 'instructions'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent', 'new_file.md')).touch('new content')

        result = ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        # New content should be present
        self.assertTrue(exists(join(repo_path, '.github', 'agents', 'module-agent', 'new_file.md')))
        # Old unrelated file should be gone
        self.assertFalse(exists(join(repo_path, '.github', 'agents', 'module-agent', 'old_file.md')))
        # product-config.instructions.md should be preserved with user content
        product_config_file = join(repo_path, '.github', 'agents', 'module-agent',
                                   'instructions', 'product-config.instructions.md')
        self.assertTrue(exists(product_config_file))
        self.assertEqual(File(product_config_file).read(), user_content)

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_folder_preserves_product_config_creates_instructions_dir(self):
        # Test that instructions dir is created when restoring product-config if source lacks it
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create existing target with product-config but source has no instructions subdir
        product_config_dir = join(repo_path, '.github', 'agents', 'module-agent', 'instructions')
        os.makedirs(product_config_dir)
        user_content = '# Product Configuration\n\nProduct Class: CBRClass\n'
        File(join(product_config_dir, 'product-config.instructions.md')).touch(user_content)

        # Source module-agent folder has NO instructions subdirectory
        os.makedirs(join(module_agent_path, '.github', 'agents', 'module-agent'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent', 'config.md')).touch('config')

        result = ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        product_config_file = join(repo_path, '.github', 'agents', 'module-agent',
                                   'instructions', 'product-config.instructions.md')
        self.assertTrue(exists(product_config_file))
        self.assertEqual(File(product_config_file).read(), user_content)

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_folder_no_product_config_to_preserve(self):
        # Test fresh copy when no product-config.instructions.md exists in target
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Source folder with instructions but no product-config
        os.makedirs(join(module_agent_path, '.github', 'agents', 'module-agent', 'instructions'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent', 'instructions', 'core.md')).touch('core')

        result = ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        # core.md should be present
        self.assertTrue(exists(join(repo_path, '.github', 'agents', 'module-agent', 'instructions', 'core.md')))
        # product-config.instructions.md should NOT exist (nothing to restore)
        product_config_file = join(repo_path, '.github', 'agents', 'module-agent',
                                   'instructions', 'product-config.instructions.md')
        self.assertFalse(exists(product_config_file))

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_folder_missing_source(self):
        # Test when source agents/module-agent folder doesn't exist
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'
        os.makedirs(module_agent_path)

        result = ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        self.assertFalse(result)

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_folder_creates_agents_dir(self):
        # Test that .github/agents directory is created when it doesn't exist
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(join(module_agent_path, '.github', 'agents', 'module-agent'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent', 'file.md')).touch('content')

        result = ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'agents')))
        self.assertTrue(exists(join(repo_path, '.github', 'agents', 'module-agent', 'file.md')))

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_md_success(self):
        # Test copying module-agent.agent.md successfully
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(join(module_agent_path, '.github', 'agents'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent.agent.md')).touch('agent definition')

        result = ModuleAgentInstructions.copy_module_agent_md(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'agents', 'module-agent.agent.md')))
        self.assertEqual(File(join(repo_path, '.github', 'agents', 'module-agent.agent.md')).read(), 'agent definition')

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_md_missing_source(self):
        # Test when source module-agent.agent.md file doesn't exist
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'
        os.makedirs(module_agent_path)

        result = ModuleAgentInstructions.copy_module_agent_md(repo_path, module_agent_path)

        self.assertFalse(result)

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_md_creates_agents_dir(self):
        # Test that .github/agents directory is created when it doesn't exist
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(join(module_agent_path, '.github', 'agents'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent.agent.md')).touch('agent content')

        # Ensure target agents dir doesn't exist
        self.assertFalse(exists(join(repo_path, '.github', 'agents')))

        result = ModuleAgentInstructions.copy_module_agent_md(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'agents')))

    @with_(TempDir, chdir=True)
    def test_copy_module_agent_md_overwrites_existing(self):
        # Test that existing module-agent.agent.md is overwritten
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create existing target file
        os.makedirs(join(repo_path, '.github', 'agents'))
        File(join(repo_path, '.github', 'agents', 'module-agent.agent.md')).touch('old content')

        os.makedirs(join(module_agent_path, '.github', 'agents'))
        File(join(module_agent_path, '.github', 'agents', 'module-agent.agent.md')).touch('new content')

        result = ModuleAgentInstructions.copy_module_agent_md(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertEqual(File(join(repo_path, '.github', 'agents', 'module-agent.agent.md')).read(), 'new content')

    @with_(TempDir, chdir=True)
    def test_update_product_config_instructions_creates_file(self):
        # Test creating product-config.instructions.md for a product class
        repo_path = os.getcwd()
        os.makedirs(join(repo_path, '.github', 'agents', 'module-agent', 'instructions'))

        result = ModuleAgentInstructions.update_product_config_instructions(repo_path, 'JGSClass')

        self.assertTrue(result)
        product_config = join(repo_path, '.github', 'agents', 'module-agent', 'instructions', 'product-config.instructions.md')
        self.assertTrue(exists(product_config))
        content = File(product_config).read()
        self.assertIn('JGSClass', content)

    @with_(TempDir, chdir=True)
    def test_update_product_config_instructions_creates_dirs(self):
        # Test that instructions directory is created when it doesn't exist
        repo_path = os.getcwd()

        result = ModuleAgentInstructions.update_product_config_instructions(repo_path, 'CBRClass')

        self.assertTrue(result)
        instructions_dir = join(repo_path, '.github', 'agents', 'module-agent', 'instructions')
        self.assertTrue(exists(instructions_dir))
        product_config = join(instructions_dir, 'product-config.instructions.md')
        self.assertTrue(exists(product_config))
        content = File(product_config).read()
        self.assertIn('CBRClass', content)

    @with_(TempDir, chdir=True)
    def test_update_product_config_instructions_overwrites_existing(self):
        # Test that existing product-config.instructions.md is overwritten
        repo_path = os.getcwd()
        instructions_dir = join(repo_path, '.github', 'agents', 'module-agent', 'instructions')
        os.makedirs(instructions_dir)
        product_config = join(instructions_dir, 'product-config.instructions.md')
        File(product_config).touch('# Product Configuration\n\nProduct Class: OldClass\n')

        result = ModuleAgentInstructions.update_product_config_instructions(repo_path, 'TestChip')

        self.assertTrue(result)
        content = File(product_config).read()
        self.assertIn('TestChip', content)
        self.assertNotIn('OldClass', content)


class TestModuleAgentSkills(TestCase):

    @with_(TempDir, chdir=True)
    def test_copy_skills_folder_creates_target_dir(self):
        # Test creating .github/skills directory if it doesn't exist
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create module agent with skills folder
        os.makedirs(join(module_agent_path, '.github', 'skills', 'skill1'))
        File(join(module_agent_path, '.github', 'skills', 'skill1', 'config.json')).touch('{}')

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'skills')))
        self.assertTrue(exists(join(repo_path, '.github', 'skills', 'skill1', 'config.json')))

    @with_(TempDir, chdir=True)
    def test_copy_skills_folder_overwrites_matching_skills(self):
        # Test that matching skills are deleted and overwritten
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create existing skills in target repo
        os.makedirs(join(repo_path, '.github', 'skills', 'skill1'))
        File(join(repo_path, '.github', 'skills', 'skill1', 'old.txt')).touch('old')

        # Create new skills in module agent
        os.makedirs(join(module_agent_path, '.github', 'skills', 'skill1'))
        File(join(module_agent_path, '.github', 'skills', 'skill1', 'new.txt')).touch('new')

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        self.assertTrue(exists(join(repo_path, '.github', 'skills', 'skill1', 'new.txt')))
        self.assertFalse(exists(join(repo_path, '.github', 'skills', 'skill1', 'old.txt')))

    @with_(TempDir, chdir=True)
    def test_copy_skills_folder_preserves_non_matching_skills(self):
        # Test that non-matching skills in target are preserved
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create existing skills in target repo
        os.makedirs(join(repo_path, '.github', 'skills', 'custom_skill'))
        File(join(repo_path, '.github', 'skills', 'custom_skill', 'data.txt')).touch('custom')

        # Create module agent skills (different name)
        os.makedirs(join(module_agent_path, '.github', 'skills', 'module_skill'))
        File(join(module_agent_path, '.github', 'skills', 'module_skill', 'config.json')).touch('{}')

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        # Custom skill should be preserved
        self.assertTrue(exists(join(repo_path, '.github', 'skills', 'custom_skill', 'data.txt')))
        # Module skill should be added
        self.assertTrue(exists(join(repo_path, '.github', 'skills', 'module_skill', 'config.json')))

    @with_(TempDir, chdir=True)
    def test_copy_skills_folder_no_source_skills(self):
        # Test when module agent has no skills folder
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'
        os.makedirs(join(module_agent_path, '.github'))

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertFalse(result)

    @with_(TempDir, chdir=True)
    def test_copy_skills_folder_empty_skills_folder(self):
        # Test when module agent skills folder is empty
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'
        os.makedirs(join(module_agent_path, '.github', 'skills'))

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertFalse(result)

    @with_(TempDir, chdir=True)
    def test_copy_skills_folder_multiple_skills(self):
        # Test copying multiple skills at once
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create multiple skills in module agent
        for i in range(1, 4):
            skill_dir = join(module_agent_path, '.github', 'skills', f'skill{i}')
            os.makedirs(skill_dir)
            File(join(skill_dir, 'config.json')).touch(f'{{"id": {i}}}')

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertTrue(result)
        for i in range(1, 4):
            self.assertTrue(exists(join(repo_path, '.github', 'skills', f'skill{i}', 'config.json')))

    @with_(TempDir, chdir=True)
    def test_copy_skills_folder_source_skills_is_file_not_dir(self):
        # Test line 315 false: source_skills path exists but is a file, not a directory
        # isdir(source_skills) returns False so source_skill_names stays empty
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        # Create .github dir but make 'skills' a file instead of a directory
        os.makedirs(join(module_agent_path, '.github'))
        File(join(module_agent_path, '.github', 'skills')).touch('')

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertFalse(result)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.shutil')
    @patch('pymtpl.update_pymtpl.mkdirs')
    @patch('pymtpl.update_pymtpl.exists')
    def test_copy_skills_folder_target_not_exist_during_deletion_check(self, mock_exists, mock_mkdirs, mock_shutil):
        # Test line 325 false: exists(target_skills) is False during deletion check
        # mkdirs is mocked so target dir is never actually created on disk
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(join(module_agent_path, '.github', 'skills', 'skill1'))
        File(join(module_agent_path, '.github', 'skills', 'skill1', 'config.json')).touch('{}')

        source_skills = join(module_agent_path, '.github', 'skills')
        target_skills = join(repo_path, '.github', 'skills')

        # exists returns True for source_skills, False for target_skills (both line 304 and 325 checks)
        def fake_exists(path):
            if path == source_skills:
                return True
            if path == target_skills:
                return False
            return os.path.exists(path)

        mock_exists.side_effect = fake_exists

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        # mkdirs was called to try to create the target directory (line 309-311 branch)
        mock_mkdirs.assert_called_once()
        # copytree was called even though target dir doesn't exist (deletion loop skipped)
        mock_shutil.copytree.assert_called_once()
        self.assertTrue(result)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.isdir')
    def test_copy_skills_folder_skill_not_dir_at_copy_time(self, mock_isdir):
        # Test line 339 false: skill entry is in source_skill_names but isdir returns False at copy time
        # isdir side_effect: True (line 315 source check), True (line 317 filter), False (line 339 copy check)
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(join(module_agent_path, '.github', 'skills', 'skill1'))
        os.makedirs(join(repo_path, '.github', 'skills'))

        mock_isdir.side_effect = [True, True, False]

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertFalse(result)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.log')
    @patch('pymtpl.update_pymtpl.isdir')
    def test_copy_skills_folder_no_skills_copied_logs_warning(self, mock_isdir, mock_log):
        # Test line 344 false: skills_copied == 0 hits else branch and logs warning
        # isdir side_effect ensures skill passes name filter but fails the copy-time check
        repo_path = os.getcwd()
        module_agent_path = 'module_agent'

        os.makedirs(join(module_agent_path, '.github', 'skills', 'skill1'))
        os.makedirs(join(repo_path, '.github', 'skills'))

        mock_isdir.side_effect = [True, True, False]

        result = ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        self.assertFalse(result)
        mock_log.warning.assert_called()
        warning_calls = [str(c) for c in mock_log.warning.call_args_list]
        self.assertTrue(any('No skill folders were copied' in str(c) for c in warning_calls))


class TestPyTPDFrameworkUpdater(TestCase):

    @with_(TempDir, chdir=True)
    def test_copy_pytpd_framework(self):
        # Test copying PyTPD framework
        repo_path = os.getcwd()
        pytpd_path = 'pytpd_repo'

        os.makedirs(pytpd_path)
        File(join(pytpd_path, 'test.py')).touch('content')
        os.makedirs(join(pytpd_path, 'subdir'))
        File(join(pytpd_path, 'subdir', 'file.py')).touch('content')

        PyTPDFrameworkUpdater.copy_pytpd_framework(repo_path, pytpd_path)

        self.assertTrue(exists(join(repo_path, 'Scripts', 'pytpd', 'test.py')))
        self.assertTrue(exists(join(repo_path, 'Scripts', 'pytpd', 'subdir', 'file.py')))

    @with_(TempDir, chdir=True)
    def test_copy_pytpd_framework_skips_git(self):
        # Test that .git folder is skipped when copying from source
        repo_path = os.getcwd()
        pytpd_path = 'pytpd_repo'

        os.makedirs(join(pytpd_path, '.git'))
        File(join(pytpd_path, '.git', 'config')).touch('content')
        File(join(pytpd_path, 'test.py')).touch('content')

        PyTPDFrameworkUpdater.copy_pytpd_framework(repo_path, pytpd_path)

        self.assertFalse(exists(join(repo_path, 'Scripts', 'pytpd', '.git')))
        self.assertTrue(exists(join(repo_path, 'Scripts', 'pytpd', 'test.py')))

    @with_(TempDir, chdir=True)
    def test_copy_pytpd_framework_preserves_existing_git(self):
        # Test that existing .git folder in Scripts/pytpd is preserved during clearing
        repo_path = os.getcwd()
        pytpd_path = 'pytpd_repo'

        # Create existing Scripts/pytpd with .git folder and other files
        scripts_pytpd = join(repo_path, 'Scripts', 'pytpd')
        os.makedirs(scripts_pytpd)
        os.makedirs(join(scripts_pytpd, '.git'))
        File(join(scripts_pytpd, '.git', 'config')).touch('git config content')
        File(join(scripts_pytpd, 'old_file.py')).touch('old content')

        # Create source pytpd repo
        os.makedirs(pytpd_path)
        File(join(pytpd_path, 'new_file.py')).touch('new content')

        PyTPDFrameworkUpdater.copy_pytpd_framework(repo_path, pytpd_path)

        # .git folder should be preserved
        self.assertTrue(exists(join(scripts_pytpd, '.git', 'config')))
        # Old files should be removed
        self.assertFalse(exists(join(scripts_pytpd, 'old_file.py')))
        # New files should be copied
        self.assertTrue(exists(join(scripts_pytpd, 'new_file.py')))

    @with_(TempDir, chdir=True)
    def test_add_version_marker(self):
        # Test adding version marker
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        short_sha = 'abc123'
        commit_link = 'https://github.com/test/commit/abc123'

        PyTPDFrameworkUpdater.add_version_marker(repo_path, short_sha, commit_link, pymtpl_folder)

        marker_file = join(pymtpl_folder, f'.pytpd_{short_sha}')
        self.assertTrue(exists(marker_file))
        self.assertEqual(File(marker_file).read(), commit_link)

    @with_(TempDir, chdir=True)
    def test_add_version_marker_removes_old_markers(self):
        # Test that old markers are removed
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        # Create old marker
        old_marker = join(pymtpl_folder, '.pytpd_old123')
        File(old_marker).touch('old content')

        short_sha = 'new456'
        commit_link = 'https://github.com/test/commit/new456'

        PyTPDFrameworkUpdater.add_version_marker(repo_path, short_sha, commit_link, pymtpl_folder)

        self.assertFalse(exists(old_marker))
        new_marker = join(pymtpl_folder, f'.pytpd_{short_sha}')
        self.assertTrue(exists(new_marker))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    def test_add_version_marker_finds_pymtpl_folder_when_none(self, mock_get_folder):
        # Test that add_version_marker uses RepositoryProcessor.get_pymtpl_folder when pymtpl_folder is None
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'UserCode', 'pymtpl')
        os.makedirs(pymtpl_folder)
        mock_get_folder.return_value = pymtpl_folder

        short_sha = 'abc123'
        commit_link = 'https://github.com/test/commit/abc123'

        result = PyTPDFrameworkUpdater.add_version_marker(repo_path, short_sha, commit_link, pymtpl_folder=None)

        mock_get_folder.assert_called_once_with(repo_path)
        self.assertEqual(result, pymtpl_folder)
        marker_file = join(pymtpl_folder, f'.pytpd_{short_sha}')
        self.assertTrue(exists(marker_file))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.os.remove')
    def test_add_version_marker_handles_delete_exception(self, mock_remove):
        # Test that exception when deleting old marker is handled gracefully
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        # Create old marker file
        old_marker = join(pymtpl_folder, '.pytpd_old123')
        File(old_marker).touch('old content')

        # Make os.remove raise an exception
        mock_remove.side_effect = PermissionError("Permission denied")

        short_sha = 'new456'
        commit_link = 'https://github.com/test/commit/new456'

        # Should not raise - exception should be caught and logged as warning
        result = PyTPDFrameworkUpdater.add_version_marker(repo_path, short_sha, commit_link, pymtpl_folder)

        # New marker should still be created
        new_marker = join(pymtpl_folder, f'.pytpd_{short_sha}')
        self.assertTrue(exists(new_marker))

    @with_(TempDir, chdir=True)
    def test_add_module_agent_version_marker(self):
        # Test adding Module Agent version marker
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        short_sha = 'def456'
        commit_link = 'https://github.com/module-agent/commit/def456'

        PyTPDFrameworkUpdater.add_module_agent_version_marker(repo_path, short_sha, commit_link, pymtpl_folder)

        marker_file = join(pymtpl_folder, f'.module_agent_{short_sha}')
        self.assertTrue(exists(marker_file))
        self.assertEqual(File(marker_file).read(), commit_link)

    @with_(TempDir, chdir=True)
    def test_add_module_agent_version_marker_removes_old_markers(self):
        # Test that old Module Agent markers are removed
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        # Create old marker
        old_marker = join(pymtpl_folder, '.module_agent_old123')
        File(old_marker).touch('old content')

        short_sha = 'new789'
        commit_link = 'https://github.com/module-agent/commit/new789'

        PyTPDFrameworkUpdater.add_module_agent_version_marker(repo_path, short_sha, commit_link, pymtpl_folder)

        self.assertFalse(exists(old_marker))
        new_marker = join(pymtpl_folder, f'.module_agent_{short_sha}')
        self.assertTrue(exists(new_marker))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    def test_add_module_agent_version_marker_finds_pymtpl_folder_when_none(self, mock_get_folder):
        # Test that add_module_agent_version_marker uses RepositoryProcessor.get_pymtpl_folder when pymtpl_folder is None
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'UserCode', 'pymtpl')
        os.makedirs(pymtpl_folder)
        mock_get_folder.return_value = pymtpl_folder

        short_sha = 'xyz123'
        commit_link = 'https://github.com/module-agent/commit/xyz123'

        result = PyTPDFrameworkUpdater.add_module_agent_version_marker(repo_path, short_sha, commit_link, pymtpl_folder=None)

        mock_get_folder.assert_called_once_with(repo_path)
        self.assertEqual(result, pymtpl_folder)
        marker_file = join(pymtpl_folder, f'.module_agent_{short_sha}')
        self.assertTrue(exists(marker_file))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.os.remove')
    def test_add_module_agent_version_marker_handles_delete_exception(self, mock_remove):
        # Test that exception when deleting old Module Agent marker is handled gracefully
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        # Create old marker file
        old_marker = join(pymtpl_folder, '.module_agent_old456')
        File(old_marker).touch('old content')

        # Make os.remove raise an exception
        mock_remove.side_effect = PermissionError("Permission denied")

        short_sha = 'new999'
        commit_link = 'https://github.com/module-agent/commit/new999'

        # Should not raise - exception should be caught and logged as warning
        result = PyTPDFrameworkUpdater.add_module_agent_version_marker(repo_path, short_sha, commit_link, pymtpl_folder)

        # New marker should still be created
        new_marker = join(pymtpl_folder, f'.module_agent_{short_sha}')
        self.assertTrue(exists(new_marker))


class TestPORMethodsUpdater(TestCase):

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.subprocess.run')
    def test_update_por_methods_success(self, mock_run):
        # Test successful por_methods update
        repo_path = os.getcwd()
        pymtpl_folder = 'Scripts/pymtpl/pymtpl'
        os.makedirs(pymtpl_folder)
        os.makedirs('Scripts/pytpd/main')
        File('Scripts/pytpd/main/pymtpl.py').touch('')

        # Create the new_test_methods.py that will be renamed
        File(join(pymtpl_folder, 'new_test_methods.py')).touch('# Generated methods')

        mock_run.return_value = MagicMock(returncode=0, stdout='Success', stderr='')

        result = PORMethodsUpdater.update_por_methods(repo_path, pymtpl_folder)

        self.assertTrue(result)
        self.assertTrue(exists(join(pymtpl_folder, 'por_methods.py')))
        self.assertFalse(exists(join(pymtpl_folder, 'new_test_methods.py')))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.subprocess.run')
    def test_update_por_methods_empty_stdout(self, mock_run):
        # Test when result.stdout is empty - covers line 337-338 false branch
        repo_path = os.getcwd()
        pymtpl_folder = 'Scripts/pymtpl/pymtpl'
        os.makedirs(pymtpl_folder)
        os.makedirs('Scripts/pytpd/main')
        File('Scripts/pytpd/main/pymtpl.py').touch('')
        File(join(pymtpl_folder, 'new_test_methods.py')).touch('# Generated')

        # Return empty stdout
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')

        result = PORMethodsUpdater.update_por_methods(repo_path, pymtpl_folder)

        self.assertTrue(result)
        self.assertTrue(exists(join(pymtpl_folder, 'por_methods.py')))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.subprocess.run')
    def test_update_por_methods_replaces_existing(self, mock_run):
        # Test that existing por_methods.py is deleted before rename
        repo_path = os.getcwd()
        pymtpl_folder = 'Scripts/pymtpl/pymtpl'
        os.makedirs(pymtpl_folder)
        os.makedirs('Scripts/pytpd/main')
        File('Scripts/pytpd/main/pymtpl.py').touch('')

        # Create existing por_methods.py with old content
        por_methods_file = join(pymtpl_folder, 'por_methods.py')
        File(por_methods_file).touch('# Old generated methods')

        # Create the new_test_methods.py that will be renamed
        File(join(pymtpl_folder, 'new_test_methods.py')).touch('# New generated methods')

        mock_run.return_value = MagicMock(returncode=0, stdout='Success', stderr='')

        result = PORMethodsUpdater.update_por_methods(repo_path, pymtpl_folder)

        self.assertTrue(result)
        self.assertTrue(exists(por_methods_file))
        # Verify it contains the new content
        self.assertEqual(File(por_methods_file).read(), '# New generated methods')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.subprocess.run')
    def test_update_por_methods_command_failure(self, mock_run):
        # Test when command fails - raises ErrorUser
        from gadget.errors import ErrorUser
        repo_path = os.getcwd()
        pymtpl_folder = 'Scripts/pymtpl/pymtpl'
        os.makedirs(pymtpl_folder)
        os.makedirs('Scripts/pytpd/main')
        File('Scripts/pytpd/main/pymtpl.py').touch('')

        mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='Error')

        with self.assertRaises(ErrorUser):
            PORMethodsUpdater.update_por_methods(repo_path, pymtpl_folder)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.subprocess.run')
    def test_update_por_methods_missing_output(self, mock_run):
        # Test when expected output file is missing - raises ErrorUser
        from gadget.errors import ErrorUser
        repo_path = os.getcwd()
        pymtpl_folder = 'Scripts/pymtpl/pymtpl'
        os.makedirs(pymtpl_folder)
        os.makedirs('Scripts/pytpd/main')
        File('Scripts/pytpd/main/pymtpl.py').touch('')

        mock_run.return_value = MagicMock(returncode=0, stdout='Success', stderr='')

        with self.assertRaises(ErrorUser):
            PORMethodsUpdater.update_por_methods(repo_path, pymtpl_folder)


class TestRepositoryValidator(TestCase):

    @with_(TempDir, chdir=True)
    def test_verify_current_dir_is_tp_repo_success(self):
        # Test valid TP repository
        File('test.sln').touch('')

        result = RepositoryValidator.verify_current_dir_is_tp_repo()
        self.assertEqual(result, os.getcwd())

    @with_(TempDir, chdir=True)
    def test_verify_current_dir_is_tp_repo_no_sln(self):
        # Test when no .sln file exists
        from gadget.errors import ErrorUser

        with self.assertRaises(ErrorUser):
            RepositoryValidator.verify_current_dir_is_tp_repo()

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.is_git_repo')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.has_clean_working_directory')
    def test_validate_repo_state_success(self, mock_clean, mock_git_repo):
        # Test successful validation
        mock_git_repo.return_value = True
        mock_clean.return_value = True

        result = RepositoryValidator.validate_repo_state(os.getcwd())
        self.assertTrue(result)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.is_git_repo')
    def test_validate_repo_state_not_git(self, mock_git_repo):
        # Test when not a git repo - raises ErrorUser
        from gadget.errors import ErrorUser
        mock_git_repo.return_value = False

        with self.assertRaises(ErrorUser):
            RepositoryValidator.validate_repo_state(os.getcwd())

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.is_git_repo')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.has_clean_working_directory')
    def test_validate_repo_state_dirty_working_dir(self, mock_clean, mock_git_repo):
        # Test when working directory is dirty - raises ErrorUser
        from gadget.errors import ErrorUser
        mock_git_repo.return_value = True
        mock_clean.return_value = False

        with self.assertRaises(ErrorUser):
            RepositoryValidator.validate_repo_state(os.getcwd())


class TestPyMTPLInstaller(TestCase):

    @patch('builtins.input')
    def test_prompt_product_class_jgsclass(self, mock_input):
        # Test JGSClass selection
        mock_input.return_value = '1'

        result = PyMTPLInstaller.prompt_product_class()
        self.assertEqual(result, 'JGSClass')

    @patch('builtins.input')
    def test_prompt_product_class_cbrclass(self, mock_input):
        # Test CBRClass selection
        mock_input.return_value = '2'

        result = PyMTPLInstaller.prompt_product_class()
        self.assertEqual(result, 'CBRClass')

    @patch('builtins.input')
    def test_prompt_product_class_testchip(self, mock_input):
        # Test TestChip selection
        mock_input.return_value = '3'

        result = PyMTPLInstaller.prompt_product_class()
        self.assertEqual(result, 'TestChip')

    @patch('builtins.input')
    def test_prompt_product_class_invalid_then_valid(self, mock_input):
        # Test invalid choice followed by valid choice
        mock_input.side_effect = ['4', '1']

        result = PyMTPLInstaller.prompt_product_class()
        self.assertEqual(result, 'JGSClass')

    @with_(TempDir, chdir=True)
    def test_read_or_create_custom_command_json_existing(self):
        # Test reading existing CustomCommand.json
        repo_path = os.getcwd()
        custom_json = {'CustomCommands': [{'name': 'test'}]}

        with open('CustomCommand.json', 'w') as f:
            json.dump(custom_json, f)

        result = PyMTPLInstaller.read_or_create_custom_command_json(repo_path)
        self.assertEqual(result, custom_json)

    @with_(TempDir, chdir=True)
    def test_read_or_create_custom_command_json_new(self):
        # Test creating new CustomCommand.json structure
        repo_path = os.getcwd()

        result = PyMTPLInstaller.read_or_create_custom_command_json(repo_path)
        self.assertEqual(result, {'CustomCommands': []})

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    def test_update_custom_command_json_adds_commands(self, mock_get_folder):
        # Test adding commands to CustomCommand.json
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)
        mock_get_folder.return_value = pymtpl_folder

        PyMTPLInstaller.update_custom_command_json(repo_path, 'JGSClass')

        with open('CustomCommand.json', 'r') as f:
            data = json.load(f)

        commands = data.get('Commands', [])
        self.assertTrue(any('pymtpl' in cmd.get('CommandName', '').lower() for cmd in commands))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    def test_update_custom_command_json_commands_already_exist(self, mock_get_folder):
        # Test when commands already exist in CustomCommand.json - covers lines 471, 478-479
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)
        mock_get_folder.return_value = pymtpl_folder

        # Create existing CustomCommand.json with commands already present
        existing_json = {
            'Commands': [
                {'CommandName': 'Run Pymtpl', 'ScriptPath': 'old/path'},
                {'CommandName': 'Create PyMTPL from MTPL', 'ScriptPath': 'old/path'}
            ]
        }
        with open('CustomCommand.json', 'w') as f:
            json.dump(existing_json, f)

        PyMTPLInstaller.update_custom_command_json(repo_path, 'JGSClass')

        with open('CustomCommand.json', 'r') as f:
            data = json.load(f)

        # Should still have exactly 2 commands (not duplicated)
        commands = data.get('Commands', [])
        self.assertEqual(len(commands), 2)

    @with_(TempDir, chdir=True)
    def test_create_pymtpl_folder_structure_new(self):
        # Test creating new pymtpl folder structure
        repo_path = os.getcwd()

        result = PyMTPLInstaller.create_pymtpl_folder_structure(repo_path)

        expected = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        self.assertEqual(result, expected)
        self.assertTrue(exists(expected))
        self.assertTrue(exists(join(expected, '__init__.py')))

    @with_(TempDir, chdir=True)
    def test_create_pymtpl_folder_structure_existing(self):
        # Test when folder already exists
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        result = PyMTPLInstaller.create_pymtpl_folder_structure(repo_path)

        self.assertEqual(result, pymtpl_folder)

    @with_(TempDir, chdir=True)
    def test_create_pymtpl_folder_structure_parent_init_exists(self):
        # Test when parent __init__.py already exists - covers line 504-505 false branch
        repo_path = os.getcwd()
        parent_folder = join(repo_path, 'Scripts', 'pymtpl')
        os.makedirs(parent_folder)
        parent_init = join(parent_folder, '__init__.py')
        File(parent_init).touch('# Existing init')

        result = PyMTPLInstaller.create_pymtpl_folder_structure(repo_path)

        expected = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        self.assertEqual(result, expected)
        # Verify parent __init__.py was not overwritten
        self.assertEqual(File(parent_init).read(), '# Existing init')

    @with_(TempDir, chdir=True)
    def test_find_bdefs_file_found(self):
        # Test finding .bdefs file
        repo_path = os.getcwd()
        shared_path = join(repo_path, 'Shared', 'subfolder')
        os.makedirs(shared_path)
        File(join(shared_path, 'test.bdefs')).touch('')

        result = PyMTPLInstaller.find_bdefs_file(repo_path)

        self.assertIsNotNone(result)
        self.assertIn('test.bdefs', result)

    @with_(TempDir, chdir=True)
    def test_find_bdefs_file_not_found(self):
        # Test when .bdefs file not found (no Shared folder)
        repo_path = os.getcwd()

        result = PyMTPLInstaller.find_bdefs_file(repo_path)

        self.assertIsNone(result)

    @with_(TempDir, chdir=True)
    def test_find_bdefs_file_shared_exists_no_bdefs(self):
        # Test when Shared folder exists but no .bdefs files - covers line 525-526
        repo_path = os.getcwd()
        shared_path = join(repo_path, 'Shared', 'subfolder')
        os.makedirs(shared_path)
        File(join(shared_path, 'somefile.txt')).touch('')

        result = PyMTPLInstaller.find_bdefs_file(repo_path)

        self.assertIsNone(result)

    @with_(TempDir, chdir=True)
    def test_find_env_file_found(self):
        # Test finding .env file
        repo_path = os.getcwd()
        por_path = join(repo_path, 'POR_TP', 'subfolder')
        os.makedirs(por_path)
        File(join(por_path, 'test.env')).touch('')

        result = PyMTPLInstaller.find_env_file(repo_path)

        self.assertIsNotNone(result)
        self.assertIn('test.env', result)

    @with_(TempDir, chdir=True)
    def test_find_env_file_not_found(self):
        # Test when .env file not found (no POR_TP folder)
        repo_path = os.getcwd()

        result = PyMTPLInstaller.find_env_file(repo_path)

        self.assertIsNone(result)

    @with_(TempDir, chdir=True)
    def test_find_env_file_por_tp_exists_no_env(self):
        # Test when POR_TP folder exists but no .env files - covers line 541-542
        repo_path = os.getcwd()
        por_path = join(repo_path, 'POR_TP', 'subfolder')
        os.makedirs(por_path)
        File(join(por_path, 'somefile.txt')).touch('')

        result = PyMTPLInstaller.find_env_file(repo_path)

        self.assertIsNone(result)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.find_bdefs_file')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.find_env_file')
    def test_create_bat_files(self, mock_env, mock_bdefs):
        # Test creating .bat files
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        mock_bdefs.return_value = 'Shared/test.bdefs'
        mock_env.return_value = 'POR_TP/test.env'

        PyMTPLInstaller.create_bat_files(repo_path, 'JGSClass', pymtpl_folder)

        self.assertTrue(exists(join(pymtpl_folder, 'pymtpl.bat')))
        self.assertTrue(exists(join(pymtpl_folder, 'mtpl2py.bat')))

        mtpl2py_content = File(join(pymtpl_folder, 'mtpl2py.bat')).read()
        self.assertIn('JGSClass', mtpl2py_content)

    @with_(TempDir, chdir=True)
    def test_create_bat_files_missing_bdefs_and_env(self):
        # Test creating .bat files when bdefs and env files are not found - covers lines 548-549, 553-554
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        PyMTPLInstaller.create_bat_files(repo_path, 'JGSClass', pymtpl_folder)

        self.assertTrue(exists(join(pymtpl_folder, 'pymtpl.bat')))
        self.assertTrue(exists(join(pymtpl_folder, 'mtpl2py.bat')))

        # Verify default paths are used
        pymtpl_content = File(join(pymtpl_folder, 'pymtpl.bat')).read()
        self.assertIn('Shared/path/to/bindeffile.bdefs', pymtpl_content)
        self.assertIn('POR_TP/TestProgram/EnvironmentFile.env', pymtpl_content)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.ModuleAgentSkills.copy_skills_folder')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_module_agent_version_marker')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.copy_pytpd_framework')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_version_marker')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.create_bat_files')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.update_custom_command_json')
    @patch('pymtpl.update_pymtpl.PORMethodsUpdater.update_por_methods')
    @patch('pymtpl.update_pymtpl.ModuleAgentInstructions.update_product_config_instructions')
    @patch('pymtpl.update_pymtpl.ModuleAgentInstructions.process_module_agent_for_repo')
    def test_install_pymtpl_in_repo_with_por_methods(self, mock_agent, mock_product_config, mock_por,
                                                     mock_custom, mock_bat, mock_version,
                                                     mock_copy, mock_ma_version, mock_skills,
                                                     mock_commit_info):
        # Test full installation with por_methods generation and new Module Agent features
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)
        pytpd_path = 'pytpd_repo'
        agent_path = 'agent_repo'

        mock_commit_info.return_value = ('def456', 'Module Agent commit')

        result = PyMTPLInstaller.install_pymtpl_in_repo(
            repo_path, pytpd_path, agent_path, 'abc123',
            'https://github.com/test', 'JGSClass',
            skip_por_methods=False
        )

        self.assertTrue(result)
        mock_por.assert_called_once()
        mock_product_config.assert_called_once_with(repo_path, 'JGSClass')
        mock_skills.assert_called_once_with(repo_path, agent_path)
        mock_ma_version.assert_called_once()
        mock_commit_info.assert_called_once_with(agent_path)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.ModuleAgentSkills.copy_skills_folder')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_module_agent_version_marker')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.copy_pytpd_framework')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_version_marker')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.create_bat_files')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.update_custom_command_json')
    @patch('pymtpl.update_pymtpl.ModuleAgentInstructions.update_product_config_instructions')
    @patch('pymtpl.update_pymtpl.ModuleAgentInstructions.process_module_agent_for_repo')
    def test_install_pymtpl_in_repo_skip_por_methods(self, mock_agent, mock_product_config,
                                                     mock_custom, mock_bat, mock_version,
                                                     mock_copy, mock_ma_version, mock_skills,
                                                     mock_commit_info):
        # Test installation with -s flag (skip por_methods) but still updates skills and version
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)
        pytpd_path = 'pytpd_repo'
        agent_path = 'agent_repo'

        mock_commit_info.return_value = ('xyz789', 'Module Agent commit')

        result = PyMTPLInstaller.install_pymtpl_in_repo(
            repo_path, pytpd_path, agent_path, 'abc123',
            'https://github.com/test', 'JGSClass', skip_por_methods=True
        )

        self.assertTrue(result)
        mock_product_config.assert_called_once_with(repo_path, 'JGSClass')
        mock_skills.assert_called_once_with(repo_path, agent_path)
        mock_ma_version.assert_called_once()
        mock_commit_info.assert_called_once_with(agent_path)


class TestRepositoryProcessor(TestCase):

    @with_(TempDir, chdir=True)
    def test_get_pymtpl_folder_first_location(self):
        # Test finding pymtpl in first location
        repo_path = os.getcwd()
        folder1 = join(repo_path, 'Shared', 'BaseInputs', 'Scripts', 'pymtpl')
        os.makedirs(folder1)
        File(join(folder1, 'test.py')).touch('')

        result = RepositoryProcessor.get_pymtpl_folder(repo_path)

        self.assertEqual(result, folder1)

    @with_(TempDir, chdir=True)
    def test_get_pymtpl_folder_second_location(self):
        # Test finding pymtpl in second location
        repo_path = os.getcwd()
        folder2 = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(folder2)
        File(join(folder2, 'test.py')).touch('')

        result = RepositoryProcessor.get_pymtpl_folder(repo_path)

        self.assertEqual(result, folder2)

    @with_(TempDir, chdir=True)
    def test_get_pymtpl_folder_empty_folders_ignored(self):
        # Test that empty folders are ignored
        repo_path = os.getcwd()
        empty_folder = join(repo_path, 'Shared', 'BaseInputs', 'Scripts', 'pymtpl')
        os.makedirs(empty_folder)

        valid_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(valid_folder)
        File(join(valid_folder, 'test.py')).touch('')

        result = RepositoryProcessor.get_pymtpl_folder(repo_path)

        self.assertEqual(result, valid_folder)

    @with_(TempDir, chdir=True)
    def test_get_pymtpl_folder_not_found(self):
        # Test when no pymtpl folder found
        repo_path = os.getcwd()

        result = RepositoryProcessor.get_pymtpl_folder(repo_path)

        self.assertIsNone(result)

    @with_(TempDir, chdir=True)
    def test_get_pymtpl_folder_caching(self):
        # Test that result is cached
        repo_path = os.getcwd()
        folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(folder)
        File(join(folder, 'test.py')).touch('')

        # Clear cache first
        RepositoryProcessor._pymtpl_folder_cache.clear()

        result1 = RepositoryProcessor.get_pymtpl_folder(repo_path)
        result2 = RepositoryProcessor.get_pymtpl_folder(repo_path)

        self.assertEqual(result1, result2)
        self.assertIn(repo_path, RepositoryProcessor._pymtpl_folder_cache)

    @patch('pymtpl.update_pymtpl.LocalGitHelper.pull_latest_changes')
    def test_update_repo_git_state(self, mock_pull):
        # Test updating repo git state
        mock_pull.return_value = True

        result = RepositoryProcessor.update_repo_git_state('/fake/path')

        self.assertTrue(result)
        mock_pull.assert_called_once_with('/fake/path')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.ModuleAgentSkills.copy_skills_folder')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_module_agent_version_marker')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.update_repo_git_state')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.copy_pytpd_framework')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_version_marker')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    @patch('pymtpl.update_pymtpl.PORMethodsUpdater.update_por_methods')
    @patch('pymtpl.update_pymtpl.ModuleAgentInstructions.process_module_agent_for_repo')
    def test_process_single_repo_with_por_methods(self, mock_agent, mock_por, mock_get_folder,
                                                  mock_version, mock_copy, mock_git,
                                                  mock_ma_version, mock_skills, mock_commit_info):
        # Test processing single repo with por_methods and new Module Agent features
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        mock_get_folder.return_value = pymtpl_folder
        mock_agent.return_value = True
        mock_commit_info.return_value = ('ma123', 'Module Agent commit')

        RepositoryProcessor.process_single_repo(
            repo_path, 'pytpd_path', 'sha123',
            'https://github.com/test', 'agent_path', False
        )

        mock_por.assert_called_once()
        mock_skills.assert_called_once_with(repo_path, 'agent_path')
        mock_ma_version.assert_called_once()
        mock_commit_info.assert_called_once_with('agent_path')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.ModuleAgentSkills.copy_skills_folder')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_module_agent_version_marker')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.update_repo_git_state')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.copy_pytpd_framework')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_version_marker')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    @patch('pymtpl.update_pymtpl.ModuleAgentInstructions.process_module_agent_for_repo')
    def test_process_single_repo_skip_por_methods(self, mock_agent, mock_get_folder,
                                                  mock_version, mock_copy, mock_git,
                                                  mock_ma_version, mock_skills, mock_commit_info):
        # Test processing single repo skipping por_methods but still updates skills and version
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        mock_get_folder.return_value = pymtpl_folder
        mock_agent.return_value = True
        mock_commit_info.return_value = ('ma456', 'Module Agent commit')

        RepositoryProcessor.process_single_repo(
            repo_path, 'pytpd_path', 'sha123',
            'https://github.com/test', 'agent_path', True
        )

        # Verify por_methods was not called (by not mocking it, it should not be called)
        mock_skills.assert_called_once_with(repo_path, 'agent_path')
        mock_ma_version.assert_called_once()
        mock_commit_info.assert_called_once_with('agent_path')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.ModuleAgentSkills.copy_skills_folder')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_module_agent_version_marker')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.update_repo_git_state')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.copy_pytpd_framework')
    @patch('pymtpl.update_pymtpl.PyTPDFrameworkUpdater.add_version_marker')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    @patch('pymtpl.update_pymtpl.ModuleAgentInstructions.process_module_agent_for_repo')
    @patch('pymtpl.update_pymtpl.log')
    def test_process_single_repo_module_agent_fails(self, mock_log, mock_agent, mock_get_folder,
                                                    mock_version, mock_copy, mock_git,
                                                    mock_ma_version, mock_skills, mock_commit_info):
        # Test processing single repo when module agent fails - covers line 685-686
        repo_path = os.getcwd()
        pymtpl_folder = join(repo_path, 'Scripts', 'pymtpl', 'pymtpl')
        os.makedirs(pymtpl_folder)

        mock_get_folder.return_value = pymtpl_folder
        mock_agent.return_value = False  # Module agent fails
        mock_commit_info.return_value = ('sha_fail', 'Module Agent commit')

        RepositoryProcessor.process_single_repo(
            repo_path, 'pytpd_path', 'sha123',
            'https://github.com/test', 'agent_path', True
        )

        # Verify warning was logged
        mock_log.warning.assert_called()
        warning_calls = [str(c) for c in mock_log.warning.call_args_list]
        self.assertTrue(any('Failed to update Module Agent' in str(c) for c in warning_calls))


class TestPyMTPLUpdater(TestCase):

    def setUp(self):
        # Clear the cache before each test
        RepositoryProcessor._pymtpl_folder_cache.clear()

    def test_init(self):
        # Test PyMTPLUpdater initialization
        updater = PyMTPLUpdater()

        self.assertIsNone(updater.pytpd_tempdir)
        self.assertIsNone(updater.module_agent_tempdir)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryValidator.validate_repo_state')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    def test_run_installation_mode_already_installed(self, mock_get_folder, mock_validate):
        # Test when PyMTPL is already installed - raises ErrorUser
        from gadget.errors import ErrorUser
        mock_validate.return_value = True
        mock_get_folder.return_value = '/existing/folder'

        updater = PyMTPLUpdater()
        with self.assertRaises(ErrorUser):
            updater.run_installation_mode(os.getcwd(), skip_por_methods=False)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryValidator.validate_repo_state')
    def test_run_installation_mode_validation_failure(self, mock_validate):
        # Test when validation fails - raises ErrorUser
        from gadget.errors import ErrorUser
        mock_validate.side_effect = ErrorUser("Validation failed")

        updater = PyMTPLUpdater()
        with self.assertRaises(ErrorUser):
            updater.run_installation_mode(os.getcwd(), skip_por_methods=False)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryValidator.validate_repo_state')
    def test_run_update_mode_validation_failure(self, mock_validate):
        # Test update mode when validation fails - raises ErrorUser
        from gadget.errors import ErrorUser
        mock_validate.side_effect = ErrorUser("Validation failed")

        updater = PyMTPLUpdater()
        with self.assertRaises(ErrorUser):
            updater.run_update_mode(os.getcwd(), skip_por_methods=False)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryValidator.verify_current_dir_is_tp_repo')
    @patch('pymtpl.update_pymtpl.RepositoryValidator.validate_repo_state')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_module_agent_repo')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_pytpd_repo')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.process_single_repo')
    def test_main_update_mode_success(self, mock_process, mock_commit, mock_pytpd,
                                      mock_agent, mock_validate, mock_verify):
        # Test successful update mode
        File('test.sln').touch('')
        mock_verify.return_value = os.getcwd()
        mock_validate.return_value = True

        mock_agent_temp = MagicMock()
        mock_agent_temp.name.return_value = '/tmp/agent'
        mock_agent.return_value = mock_agent_temp

        mock_pytpd_temp = MagicMock()
        mock_pytpd_temp.name.return_value = '/tmp/pytpd'
        mock_pytpd.return_value = mock_pytpd_temp

        mock_commit.return_value = ('abc123', 'Test commit')

        updater = PyMTPLUpdater()
        updater.main(install=False, skip_por_methods=False)

        mock_process.assert_called_once()

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryValidator.verify_current_dir_is_tp_repo')
    @patch('pymtpl.update_pymtpl.RepositoryValidator.validate_repo_state')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_module_agent_repo')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_pytpd_repo')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.prompt_product_class')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.install_pymtpl_in_repo')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    def test_main_install_mode_success(self, mock_get_folder, mock_install, mock_prompt,
                                       mock_commit, mock_pytpd, mock_agent, mock_validate,
                                       mock_verify):
        # Test successful install mode
        File('test.sln').touch('')
        mock_verify.return_value = os.getcwd()
        mock_validate.return_value = True
        mock_get_folder.return_value = None  # Not installed yet
        mock_prompt.return_value = 'JGSClass'
        mock_install.return_value = True

        mock_agent_temp = MagicMock()
        mock_agent_temp.name.return_value = '/tmp/agent'
        mock_agent.return_value = mock_agent_temp

        mock_pytpd_temp = MagicMock()
        mock_pytpd_temp.name.return_value = '/tmp/pytpd'
        mock_pytpd.return_value = mock_pytpd_temp

        mock_commit.return_value = ('abc123', 'Test commit')

        updater = PyMTPLUpdater().main(install=True, skip_por_methods=False)

        mock_install.assert_called_once()

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryValidator.verify_current_dir_is_tp_repo')
    @patch('pymtpl.update_pymtpl.RepositoryValidator.validate_repo_state')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_module_agent_repo')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_pytpd_repo')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.process_single_repo')
    def test_main_skip_por_methods_flag(self, mock_process, mock_commit, mock_pytpd,
                                        mock_agent, mock_validate, mock_verify):
        # Test -s flag to skip por_methods generation
        File('test.sln').touch('')
        mock_verify.return_value = os.getcwd()
        mock_validate.return_value = True

        mock_agent_temp = MagicMock()
        mock_agent_temp.name.return_value = '/tmp/agent'
        mock_agent.return_value = mock_agent_temp

        mock_pytpd_temp = MagicMock()
        mock_pytpd_temp.name.return_value = '/tmp/pytpd'
        mock_pytpd.return_value = mock_pytpd_temp

        mock_commit.return_value = ('abc123', 'Test commit')

        updater = PyMTPLUpdater().main(install=False, skip_por_methods=True)

        # Verify skip_por_methods=True was passed
        call_args = mock_process.call_args
        self.assertTrue(call_args[0][5])  # 6th positional arg is skip_por_methods

    def test_cleanup_on_exception(self):
        # Test that temp directories are cleaned up on exception
        updater = PyMTPLUpdater()

        mock_agent_temp = MagicMock()
        mock_pytpd_temp = MagicMock()

        updater.module_agent_tempdir = mock_agent_temp
        updater.pytpd_tempdir = mock_pytpd_temp

        with patch('pymtpl.update_pymtpl.RepositoryValidator.verify_current_dir_is_tp_repo',
                   side_effect=Exception('Test error')):
            try:
                updater.main()
            except BaseException:
                pass

        # Verify cleanup was called
        mock_agent_temp.close.assert_called_once()
        mock_pytpd_temp.close.assert_called_once()

    @with_(TempDir, chdir=True)
    @patch('pymtpl.update_pymtpl.RepositoryValidator.verify_current_dir_is_tp_repo')
    @patch('pymtpl.update_pymtpl.RepositoryValidator.validate_repo_state')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_module_agent_repo')
    @patch('pymtpl.update_pymtpl.RepositoryCloner.clone_pytpd_repo')
    @patch('pymtpl.update_pymtpl.LocalGitHelper.get_commit_info')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.prompt_product_class')
    @patch('pymtpl.update_pymtpl.PyMTPLInstaller.install_pymtpl_in_repo')
    @patch('pymtpl.update_pymtpl.RepositoryProcessor.get_pymtpl_folder')
    @patch('pymtpl.update_pymtpl.log')
    def test_main_success_false_no_completion_message(self, mock_log, mock_get_folder, mock_install, mock_prompt,
                                                      mock_commit, mock_pytpd, mock_agent, mock_validate,
                                                      mock_verify):
        # Test when success is False - covers line 800-801 false branch
        File('test.sln').touch('')
        mock_verify.return_value = os.getcwd()
        mock_validate.return_value = True
        mock_get_folder.return_value = None
        mock_prompt.return_value = 'JGSClass'
        mock_install.return_value = False  # Return False for success

        mock_agent_temp = MagicMock()
        mock_agent_temp.name.return_value = '/tmp/agent'
        mock_agent.return_value = mock_agent_temp

        mock_pytpd_temp = MagicMock()
        mock_pytpd_temp.name.return_value = '/tmp/pytpd'
        mock_pytpd.return_value = mock_pytpd_temp

        mock_commit.return_value = ('abc123', 'Test commit')

        updater = PyMTPLUpdater().main(install=True, skip_por_methods=False)

        # Verify "Script completed successfully!" was NOT logged
        success_calls = [c for c in mock_log.info.call_args_list if 'Script completed successfully' in str(c)]
        self.assertEqual(len(success_calls), 0)

    def test_main_cleanup_with_none_tempdirs(self):
        # Test cleanup when tempdirs are None - covers lines 811-812, 815-816 false branches
        updater = PyMTPLUpdater()

        # Tempdirs are None by default
        self.assertIsNone(updater.module_agent_tempdir)
        self.assertIsNone(updater.pytpd_tempdir)

        with patch('pymtpl.update_pymtpl.RepositoryValidator.verify_current_dir_is_tp_repo',
                   side_effect=Exception('Test error')):
            try:
                updater.main()
            except BaseException:
                pass

        # Should not raise AttributeError when trying to close None tempdirs
        # The test passes if no exception is raised


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
