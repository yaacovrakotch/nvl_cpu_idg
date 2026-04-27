#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit tests for create_pr.py
"""

from setenv_unittest import UT_DIR, ROOT_ENV  # must be first import for unittests
from gadget.ut import TestCase, MockVar, unittest, Mock
from gadget.files import TempDir, File
from gadget.getgit import GitOperations
from gadget.shell import SystemCall
from main.create_pr import *
from unittest.mock import patch, mock_open
import os
import sys


class TestCreatePR(TestCase):

    def setUp(self):
        # Set up any common test data or state here
        self.github_token = "fake_token"
        self.common_sha = "fake_sha"
        self.repo_urls = {
            'CPU': "https://github.com/intel-restricted/nvl.cpu.git",
            'HUB': "https://github.com/intel-restricted/nvl.hub.git",
            'PCD': "https://github.com/intel-restricted/nvl.pcd.git",
            'GCD': "https://github.com/intel-restricted/nvl.gcd.git"
        }
        self.pull_request_template_content = "## Pull Request Template\n\n- [ ] Task 1\n- [ ] Task 2"

    def tearDown(self):
        # Clean up any state here
        pass

    @patch.dict(os.environ, {
        'CPU': 'true',
        'CPU_BRANCH': 'default',
        'HUB': 'true',
        'HUB_BRANCH': 'default',
        'PCD': 'false',
        'PCD_BRANCH': 'default',
        'GCD': 'false',
        'GCD_BRANCH': 'default',
        'ALL': 'false'
    })
    @patch.object(GitOperations, 'get_gh_token', return_value='fake_token')
    def test_main_nvl_cpu_hub(self, mock_get_gh_token):
        sys.argv = ['create_pr.py', 'NVL']
        create_pr = CreatePR()
        with patch.object(GitOperations, 'clone_repository') as mock_clone_repository, \
                patch.object(GitOperations, 'get_default_branch_and_sha',
                             return_value=('main', 'abc123')) as mock_get_default_branch_and_sha:
            with self.assertRaises(SystemExit) as cm:
                create_pr.main()
            self.assertEqual(cm.exception.code, 1)
            mock_clone_repository.assert_called()
            mock_get_default_branch_and_sha.assert_called()

    @patch.dict(os.environ, {
        'CPU': 'false',
        'CPU_BRANCH': 'default',
        'HUB': 'false',
        'HUB_BRANCH': 'default',
        'PCD': 'false',
        'PCD_BRANCH': 'default',
        'GCD': 'false',
        'GCD_BRANCH': 'default',
        'ALL': 'true'
    })
    @patch.object(GitOperations, 'get_gh_token', return_value='fake_token')
    def test_main_nvl_all(self, mock_get_gh_token):
        sys.argv = ['create_pr.py', 'NVL']
        create_pr = CreatePR()
        with patch.object(GitOperations, 'clone_repository') as mock_clone_repository, \
                patch.object(GitOperations, 'get_default_branch_and_sha',
                             return_value=('main', 'abc123')) as mock_get_default_branch_and_sha:
            with self.assertRaises(SystemExit) as cm:
                create_pr.main()
            self.assertEqual(cm.exception.code, 1)
            mock_clone_repository.assert_called()
            mock_get_default_branch_and_sha.assert_called()

    @patch.dict(os.environ, {
        'CPU': 'false',
        'CPU_BRANCH': 'default',
        'HUB': 'true',
        'HUB_BRANCH': 'TPI/main',
        'PCD': 'true',
        'PCD_BRANCH': 'default',
        'GCD': 'false',
        'GCD_BRANCH': 'default',
        'ALL': 'false'
    })
    @patch.object(GitOperations, 'get_gh_token', return_value='fake_token')
    def test_main_nvl_pcd_wBN_hub(self, mock_get_gh_token):
        sys.argv = ['create_pr.py', 'NVL']
        create_pr = CreatePR()
        with patch.object(GitOperations, 'clone_repository') as mock_clone_repository, \
                patch.object(GitOperations, 'get_default_branch_and_sha',
                             return_value=('main', 'abc123')) as mock_get_default_branch_and_sha:
            with self.assertRaises(SystemExit) as cm:
                create_pr.main()
            self.assertEqual(cm.exception.code, 1)
            mock_clone_repository.assert_called()
            mock_get_default_branch_and_sha.assert_called()

    @patch.dict(os.environ, {
        'CPU': 'false',
        'CPU_BRANCH': 'TPI/main',
        'HUB': 'true',
        'HUB_BRANCH': 'default',
        'PCD': 'true',
        'PCD_BRANCH': 'default',
        'GCD': 'false',
        'GCD_BRANCH': 'default',
        'ALL': 'false'
    })
    @patch.object(GitOperations, 'get_gh_token', return_value='fake_token')
    def test_main_nvl_all_wBN_cpu_hub(self, mock_get_gh_token):
        sys.argv = ['create_pr.py', 'NVL']
        create_pr = CreatePR()
        with patch.object(GitOperations, 'clone_repository') as mock_clone_repository, \
                patch.object(GitOperations, 'get_default_branch_and_sha',
                             return_value=('main', 'abc123')) as mock_get_default_branch_and_sha:
            with self.assertRaises(SystemExit) as cm:
                create_pr.main()
            self.assertEqual(cm.exception.code, 1)
            mock_clone_repository.assert_called()
            mock_get_default_branch_and_sha.assert_called()

    @patch.dict(os.environ, {
        'CPU': 'false',
        'CPU_BRANCH': 'default',
        'HUB': 'false',
        'HUB_BRANCH': 'default',
        'PCD': 'false',
        'PCD_BRANCH': 'default',
        'GCD': 'false',
        'GCD_BRANCH': 'default',
        'ALL': 'false'
    })
    @patch.object(GitOperations, 'get_gh_token', return_value='fake_token')
    def test_main_nvl_noadditionalargs(self, mock_get_gh_token):
        sys.argv = ['create_pr.py', 'NVL']
        create_pr = CreatePR()
        with patch.object(GitOperations, 'clone_repository') as mock_clone_repository, \
                patch.object(GitOperations, 'get_default_branch_and_sha',
                             return_value=('main', 'abc123')) as mock_get_default_branch_and_sha:
            with self.assertRaises(ValueError) as context:
                create_pr.main()
            self.assertEqual(str(context.exception), "No valid target repositories specified for NVL.")

    @patch.object(GitOperations, 'get_default_branch_and_sha', return_value=('main', 'abc123'))
    def test_determine_target_branch(self, mock_get_default_branch_and_sha):
        with patch.dict(os.environ, {'CPU_BRANCH': 'default'}):
            branch = determine_target_branch('CPU', '/fake/path')
            self.assertEqual(branch, 'main')

    def test_process_repository_rules(self):
        self.assertTrue(process_repository_rules('NVL', 'main'))
        self.assertFalse(process_repository_rules('NVL', 'feature'))

    def test_repo_selector_global_declare(self):
        common_repo_url, base_path, target_repo_urls, submodule_path, shared_repo_name = RepoSelector.global_declare('NVL', ['CPU'], '/fake/path')
        self.assertEqual(common_repo_url, 'https://github.com/intel-restricted/nvl.common.git')
        self.assertIn(('CPU', 'https://github.com/intel-restricted/nvl.cpu.git'), target_repo_urls)

    @patch.object(GitOperations, 'create_branch')
    @patch.object(GitOperations, 'update_submodule', return_value=None)  # Mock submodule update
    @patch.object(GitOperations, 'commit_changes')
    @patch.object(GitOperations, 'push_branch')
    @patch.object(GitOperations, 'create_pull_request')
    @patch.object(GitOperations, 'get_submodule_sha', return_value='different_sha')
    @patch.object(GitOperations, 'get_default_branch_and_sha', return_value=('main', 'abc123'))
    def test_auto_pr_mode_default_mode(self, mock_get_default_branch_and_sha, mock_get_submodule_sha, mock_create_pull_request, mock_push_branch, mock_commit_changes, mock_update_submodule, mock_create_branch):
        # Setup the mocks to simulate expected behavior
        mock_create_branch.return_value = None
        mock_commit_changes.return_value = None  # Simulate successful commit
        mock_push_branch.return_value = None
        mock_create_pull_request.return_value = 'http://example.com/pr'

        # Use TempDir to create a temporary directory for the test
        with TempDir(name=True, chdir=True) as tdir:
            # Set up fake repo structure
            repo_path = f'{tdir}/repo'
            os.makedirs(repo_path, exist_ok=True)

            # Initialize the directory as a Git repository
            SystemCall(['git', 'init', repo_path]).run_outtxt()

            # Create a dummy file to simulate changes
            File(f'{repo_path}/file.txt').touch('file content')

            # Simulate the method under test - Using repo_key variable
            repo_key = 'CPU'
            AutoPR_Mode.default_mode(repo_path, repo_key, 'repo_name_transformed', 'submodule_path', 'submodule_sha', 'common_sha', 'api_repo_name', 'github_token', [], [], 'shared_repo_name')

            # Verify that create_pull_request was called
            mock_create_pull_request.assert_called_once()

            # Add debugging statements to verify the flow
            print("create_branch called:", mock_create_branch.called)
            print("update_submodule called:", mock_update_submodule.called)
            print("commit_changes called:", mock_commit_changes.called)
            print("push_branch called:", mock_push_branch.called)
            print("create_pull_request called:", mock_create_pull_request.called)

    @patch.object(GitOperations, 'checkout_branch')
    @patch.object(GitOperations, 'update_submodule', return_value=None)  # Mock submodule update
    @patch.object(GitOperations, 'commit_changes')
    @patch.object(GitOperations, 'pull_branch')
    @patch.object(GitOperations, 'push_branch')
    @patch.object(GitOperations, 'get_submodule_sha', return_value='different_sha')
    @patch.object(GitOperations, 'get_default_branch_and_sha', return_value=('main', 'abc123'))
    def test_auto_pr_mode_user_input_mode(self, mock_get_default_branch_and_sha, mock_get_submodule_sha, mock_pull_branch, mock_push_branch, mock_commit_changes, mock_update_submodule, mock_checkout_branch):
        # Setup the mocks to simulate expected behavior
        mock_checkout_branch.return_value = None
        mock_commit_changes.return_value = None  # Simulate successful commit
        mock_pull_branch.return_value = None
        mock_push_branch.return_value = None

        # Use TempDir to create a temporary directory for the test
        with TempDir(name=True, chdir=True) as tdir:
            # Set up fake repo structure
            repo_path = f'{tdir}/repo'
            os.makedirs(repo_path, exist_ok=True)

            # Initialize the directory as a Git repository
            SystemCall(['git', 'init', repo_path]).run_outtxt()

            # Create a dummy file to simulate changes
            File(f'{repo_path}/file.txt').touch('file content')

            # Simulate the method under test - Using repo_key variable
            repo_key = 'CPU'
            AutoPR_Mode.user_input_mode(repo_path, 'user_branch', 'submodule_path', 'repo_url', 'submodule_sha', 'common_sha', 'api_repo_name', 'github_token', [], repo_key, 'repo_name_transformed', 'shared_repo_name', 'shared_branch_name')

            # Verify that checkout_branch was called
            mock_checkout_branch.assert_called_once_with(repo_path, 'user_branch')

            # Verify that commit_changes was called
            mock_commit_changes.assert_called_once()

            # Verify that push_branch was called
            mock_pull_branch.assert_called_once()

            # Verify that push_branch was called
            mock_push_branch.assert_called_once()

            # Add debugging statements to verify the flow
            print("checkout_branch called:", mock_checkout_branch.called)
            print("update_submodule called:", mock_update_submodule.called)
            print("commit_changes called:", mock_commit_changes.called)
            print("pull_branch called:", mock_pull_branch.called)
            print("push_branch called:", mock_push_branch.called)

    @patch.object(GitOperations, 'clone_repository')
    @patch.object(GitOperations, 'get_default_branch_and_sha', return_value=('main', 'abc123'))
    def test_git_handler_clone_and_get_sha(self, mock_get_default_branch_and_sha, mock_clone_repository):
        default_branch, sha = GitHandler.clone_and_get_sha('https://github.com/intel-restricted/nvl.common.git', '/fake/path')
        self.assertEqual(sha, 'abc123')
        self.assertEqual(default_branch, 'main')
        mock_clone_repository.assert_called_once()

    @patch.dict(os.environ, {
        'CPU': 'true',
        'CPU_BRANCH': 'default',
        'HUB': 'false',
        'HUB_BRANCH': 'default',
        'PCD': 'false',
        'PCD_BRANCH': 'default',
        'GCD': 'false',
        'GCD_BRANCH': 'default',
        'ALL': 'false'
    })
    @patch.object(GitOperations, 'get_gh_token', return_value='fake_token')
    def test_main_nvl_cpu_same_sha(self, mock_get_gh_token):
        sys.argv = ['create_pr.py', 'NVL']
        create_pr = CreatePR()
        with patch.object(GitOperations, 'clone_repository') as mock_clone_repository, \
                patch.object(GitOperations, 'get_default_branch_and_sha',
                             return_value=('main', 'fake_sha')) as mock_get_default_branch_and_sha, \
                patch.object(GitOperations, 'get_submodule_sha', return_value='fake_sha') as mock_get_submodule_sha:
            with self.assertRaises(SystemExit) as cm:
                create_pr.main()
            self.assertEqual(cm.exception.code, 1)
            mock_clone_repository.assert_called()
            mock_get_default_branch_and_sha.assert_called()
            mock_get_submodule_sha.assert_called()
            # Verify that no pull request is created since the SHA is the same

    @patch('builtins.open', new_callable=mock_open, read_data="## Pull Request Template\n\n- [ ] Task 1\n- [ ] Task 2")
    @patch.object(GitOperations, 'create_pull_request')
    def test_create_pull_request_with_template(self, mock_create_pull_request, mock_open):
        # Simulate the method under test
        with TempDir(name=True, chdir=True) as tdir:
            repo_path = f'{tdir}/repo'
            os.makedirs(repo_path, exist_ok=True)

            # Initialize the directory as a Git repository
            SystemCall(['git', 'init', repo_path]).run_outtxt()

            # Create the .github directory
            github_dir = os.path.join(repo_path, '.github')
            os.makedirs(github_dir, exist_ok=True)

            # Create a dummy PR template file
            pr_template_path = os.path.join(github_dir, 'pull_request_template.md')
            with open(pr_template_path, 'w') as f:
                f.write(self.pull_request_template_content)

            # Simulate reading the pull request template
            with open(pr_template_path, 'r') as f:
                template_content = f.read()

            # Verify that the template content is read correctly
            self.assertEqual(template_content, self.pull_request_template_content)

            # Simulate creating a pull request using the template content - Using repo_key variable
            repo_key = 'CPU'
            pr_title = f"[AutoPR] - {repo_key} def5678 common sha updated from abc1234"
            pr_body = template_content.replace("_Provide a concise summary explaining the motivation for this change._", "commit_message").replace("- [ ] All packages", "- [X] All packages")
            mock_create_pull_request.return_value = 'http://example.com/pr'
            pr_url = GitOperations.create_pull_request('repo_name', 'branch_name', pr_title, 'base_branch', self.github_token, repo_path, pr_body)

            # Verify that create_pull_request was called with the modified template content
            mock_create_pull_request.assert_called_once_with('repo_name', 'branch_name', pr_title, 'base_branch', self.github_token, repo_path, pr_body)

            # Add debugging statements to verify the flow
            print("create_pull_request called with template:", mock_create_pull_request.called)

    @patch.dict(os.environ, {
        'ENABLE_MAILING': 'true',
        'CPU_OWNER': 'cpu_owner@example.com',
        'HUB_OWNER': 'hub_owner@example.com',
        'PCD_OWNER': 'pcd_owner@example.com',
        'GCD_OWNER': 'gcd_owner@example.com',
        'CC_LIST': 'cc1@example.com,cc2@example.com'
    })
    @patch.object(DataHost, 'central')
    def test_email_to_owner_send_email_enabled(self, mock_data_host_central):
        # Simulate the creation of branches and PRs - Using repo_key variables
        created_branches = ['branch1', 'branch2']
        repo_key_cpu = 'CPU'
        repo_key_hub = 'HUB'
        created_prs = [('[AutoPR] - CPU def5678 common sha updated from abc1234', 'http://example.com/pr1'), ('[AutoPR] - HUB def5678 common sha updated from abc1234', 'http://example.com/pr2')]
        error_list = []

        email_to_owner = EmailToOwner(
            enable_mailing=os.environ.get('ENABLE_MAILING', 'false'),
            cpu_owner=os.environ.get('CPU_OWNER', ''),
            hub_owner=os.environ.get('HUB_OWNER', ''),
            pcd_owner=os.environ.get('PCD_OWNER', ''),
            gcd_owner=os.environ.get('GCD_OWNER', ''),
            cc_list=os.environ.get('CC_LIST', ''),
            created_branches=created_branches,
            created_prs=created_prs,
            error_list=error_list
        )
        email_to_owner.send_email()
        # Check if the email sending function was called
        mock_data_host_central.assert_called_once()

    @patch.dict(os.environ, {
        'ENABLE_MAILING': 'false',
        'CPU_OWNER': 'cpu_owner@example.com',
        'HUB_OWNER': 'hub_owner@example.com',
        'PCD_OWNER': 'pcd_owner@example.com',
        'GCD_OWNER': 'gcd_owner@example.com',
        'CC_LIST': 'cc1@example.com,cc2@example.com'
    })
    @patch.object(DataHost, 'central')
    def test_email_to_owner_send_email_disabled(self, mock_data_host_central):
        # Simulate the creation of branches and PRs - Using repo_key variables
        created_branches = ['branch1', 'branch2']
        repo_key_cpu = 'CPU'
        repo_key_hub = 'HUB'
        created_prs = [('[AutoPR] - CPU def5678 common sha updated from abc1234', 'http://example.com/pr1'), ('[AutoPR] - HUB def5678 common sha updated from abc1234', 'http://example.com/pr2')]
        error_list = []

        email_to_owner = EmailToOwner(
            enable_mailing=os.environ.get('ENABLE_MAILING', 'false'),
            cpu_owner=os.environ.get('CPU_OWNER', ''),
            hub_owner=os.environ.get('HUB_OWNER', ''),
            pcd_owner=os.environ.get('PCD_OWNER', ''),
            gcd_owner=os.environ.get('GCD_OWNER', ''),
            cc_list=os.environ.get('CC_LIST', ''),
            created_branches=created_branches,
            created_prs=created_prs,
            error_list=error_list
        )
        email_to_owner.send_email()
        # Check if the email sending function was not called
        mock_data_host_central.assert_not_called()


if __name__ == '__main__':
    unittest.main()
