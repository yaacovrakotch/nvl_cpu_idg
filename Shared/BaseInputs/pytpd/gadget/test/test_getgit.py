#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for getgit
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, MockVar, Mock
from gadget.printmore import Dumper
from gadget.gizmo import with_, MockVar
from gadget.disk import Chdir, rmtree, mkdirs
from gadget.helperclass import CaptureStdoutLog
from gadget.shell import SystemCall
from gadget.files import TempDir
import gadget.getgit as getgit_module
from gadget.getgit import *
from pprint import pprint
import os


class TestGitOperations(TestCase):

    def setUp(self):
        # Use TempDir for creating a temporary directory for tests
        self.temp_dir = TempDir(name=True)
        self.local_path = self.temp_dir.name()

    def tearDown(self):
        # Ensure the temporary directory is cleaned up
        self.temp_dir.close()

    def test_clone_repository(self):
        repo_url = "https://github.com/intel-restricted/nvl.common.git"

        with MockVar(os.path, 'exists', Mock(return_value=True)):
            # Mock SystemCall to ensure it's called with correct arguments
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
                GitOperations.clone_repository(repo_url, self.local_path)
                SystemCall.run_outtxt.assert_called_once_with()
        with MockVar(os.path, 'exists', Mock(return_value=False)):
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
                with self.assertRaisesRegex(Exception, 'Failed to clone repository'):
                    GitOperations.clone_repository(repo_url, self.local_path)

    def test_get_default_branch_and_sha(self):
        # Mock SystemCall to return expected branch and SHA
        with MockVar(SystemCall, 'run_outtxt', Mock(side_effect=[
            (0, "refs/remotes/origin/main"),  # symbolic-ref output
            (0, "abc123def456")               # rev-parse output
        ])):
            default_branch, latest_sha = GitOperations.get_default_branch_and_sha(self.local_path)
            self.assertEqual(default_branch, "main")
            self.assertEqual(latest_sha, "abc123def456")

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to get default branch'):
                default_branch, latest_sha = GitOperations.get_default_branch_and_sha(self.local_path)

        with MockVar(SystemCall, 'run_outtxt', Mock(side_effect=[
            (0, "refs/remotes/origin/main"),
            (1, '')
        ])):
            with self.assertRaisesRegex(Exception, 'Failed to get latest SHA'):
                default_branch, latest_sha = GitOperations.get_default_branch_and_sha(self.local_path)

    def test_get_submodule_sha(self):
        with TempDir(name=True) as submodule_dir:
            submodule_path = os.path.join(submodule_dir, "Shared")
            mkdirs(submodule_path)

            # Mock SystemCall to return expected SHA
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, "abc123def456"))):
                submodule_sha = GitOperations.get_submodule_sha(self.local_path, submodule_path)
                self.assertEqual(submodule_sha, "abc123def456")

            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
                with self.assertRaisesRegex(Exception, 'Failed to update submodule'):
                    submodule_sha = GitOperations.get_submodule_sha(self.local_path, submodule_path)

            with MockVar(SystemCall, 'run_outtxt', Mock(side_effect=[
                (0, "abc123def456"),  # symbolic-ref output
                (1, "")               # rev-parse output
            ])):
                with self.assertRaisesRegex(Exception, 'Failed to get submodule SHA'):
                    submodule_sha = GitOperations.get_submodule_sha(self.local_path, submodule_path)

    def test_create_branch(self):
        branch_name = "new-branch"

        # Mock SystemCall to ensure it's called with correct arguments
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.create_branch(self.local_path, branch_name)
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to create branch'):
                GitOperations.create_branch(self.local_path, branch_name)

    def test_checkout_branch(self):
        branch_name = "existing-branch"

        # Mock SystemCall to ensure it's called with correct arguments
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.checkout_branch(self.local_path, branch_name)
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to checkout branch'):
                GitOperations.checkout_branch(self.local_path, branch_name)

    def test_get_all_branches(self):
        # Mock SystemCall to ensure it's called with correct arguments
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, '\nremotes/origin/test-branch'))):
            self.assertEqual(GitOperations.get_all_branches(self.local_path), {'test-branch'})

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to get all branches'):
                GitOperations.get_all_branches(self.local_path)

    def test_update_submodule(self):
        submodule_path = "submodule/path"

        # Mock SystemCall to ensure it's called with correct arguments
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.update_submodule(self.local_path, submodule_path)
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to update submodule'):
                GitOperations.update_submodule(self.local_path, submodule_path)

    def test_get_status(self):
        # Mock SystemCall to return expected status output
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, "On branch main\nYour branch is up to date with 'origin/main'.\n"))):
            status_output = GitOperations.get_status(self.local_path)
            self.assertIn("On branch main", status_output)

    def test_get_status_no_print(self):
        # Test that print_status=False suppresses logging
        from gadget import pylog
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, "On branch main\nYour branch is up to date with 'origin/main'.\n"))):
            with MockVar(pylog.log, 'info', Mock()) as mock_log_info:
                # Call with print_status=False - should NOT log
                status_output = GitOperations.get_status(self.local_path, print_status=False)
                self.assertIn("On branch main", status_output)
                # Verify log.info was NOT called
                mock_log_info.assert_not_called()

            with MockVar(pylog.log, 'info', Mock()) as mock_log_info:
                # Call with print_status=True (default) - should log
                status_output = GitOperations.get_status(self.local_path, print_status=True)
                self.assertIn("On branch main", status_output)
                # Verify log.info WAS called (2 times: once for CMD display, once for status output)
                self.assertEqual(mock_log_info.call_count, 2)

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ""))):
            with self.assertRaisesRegex(Exception, 'Failed to get git status'):
                status_output = GitOperations.get_status(self.local_path)

    def test_commit_changes(self):
        submodule_path = "submodule/path"
        message = "Commit message"

        # Mock SystemCall to ensure it's called with correct arguments
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.commit_changes(self.local_path, submodule_path, message)
            self.assertEqual(SystemCall.run_outtxt.call_count, 2)

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to add changes'):
                GitOperations.commit_changes(self.local_path, submodule_path, message)

        with MockVar(SystemCall, 'run_outtxt', Mock(side_effect=[
            (0, ""),
            (1, "")
        ])):
            with self.assertRaisesRegex(Exception, 'Failed to commit changes'):
                GitOperations.commit_changes(self.local_path, submodule_path, message)

    def test_pull_branch(self):
        branch_name = "existing-branch"

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.pull_branch(self.local_path, branch_name)
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to pull branch'):
                GitOperations.pull_branch(self.local_path, branch_name)

    def test_push_branch(self):
        branch_name = "new-branch"

        # Mock SystemCall to ensure it's called with correct arguments
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.push_branch(self.local_path, branch_name)
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to push branch'):
                GitOperations.push_branch(self.local_path, branch_name)

    def test_get_gh_token(self):
        # Mock os.getenv to return a token
        with MockVar(os, 'getenv', Mock(return_value="mock_token")):
            token = GitOperations.get_gh_token()
            self.assertEqual(token, "mock_token")

        # Test case where token is not set
        with MockVar(os, 'getenv', Mock(return_value=None)):
            with self.assertRaises(ValueError):
                GitOperations.get_gh_token()

    def test_create_tag(self):
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.create_tag(self.local_path, 'new-tag', 'abc123d')
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to create tag'):
                GitOperations.create_tag(self.local_path, 'new-tag', 'abc123d')

    def test_push_tag(self):
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.push_tag(self.local_path, 'existing-tag')
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to push tag'):
                GitOperations.push_tag(self.local_path, 'existing-tag')

    def test_get_all_tags(self):
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitOperations.get_all_tags(self.local_path)
            SystemCall.run_outtxt.assert_called_once_with()

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
            with self.assertRaisesRegex(Exception, 'Failed to get tags'):
                GitOperations.get_all_tags(self.local_path)

    def test_create_pull_request_with_template(self):
        repo_name = "example/repo"
        branch_name = "new-branch"
        pr_title = "PR Title"
        base_branch = "main"
        github_token = "mock_token"
        local_path = self.local_path
        commit_message = "This is the commit message."

        # TODO:: add back with find and replace features

        # Mock requests.post to simulate API call
        import requests
        with MockVar(requests, 'post', Mock()) as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {'html_url': 'http://example.com/pr'}

            GitOperations.create_pull_request(repo_name, branch_name, pr_title, base_branch, github_token, local_path, commit_message)

            # Get the actual call to verify the body contains the new template
            call_args = mock_post.call_args
            pr_template_content = call_args[1]['json']['body']

            # Verify the new hardcoded template is used (not the file content)
            self.assertIn("### Why is this PR needed?", pr_template_content)
            self.assertIn(commit_message, pr_template_content)
            self.assertIn("- [X] Other, pls specify: auto update", pr_template_content)
            self.assertIn("- [X] Not applicable", pr_template_content)
            self.assertIn("Automated submodule update PR created by the submodule update script.", pr_template_content)

            # Verify other parameters are correct
            mock_post.assert_called_once_with(
                f"https://api.github.com/repos/{repo_name}/pulls",
                json={
                    "title": pr_title,
                    "head": branch_name,
                    "base": base_branch,
                    "body": pr_template_content  # Verify the template content is used
                },
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": f"token {github_token}"
                },
                verify=False
            )

            # Test case where PR creation fails
            mock_post.return_value.status_code = 422
            mock_post.return_value.json.return_value = {'message': 'Error message'}

            with CaptureStdoutLog() as log_capture:
                GitOperations.create_pull_request(repo_name, branch_name, pr_title, base_branch, github_token, local_path, commit_message)

            self.assertIn("Failed to create PR: 422", log_capture.getvalue())
            self.assertIn("Error message", log_capture.getvalue())

    def test_is_pr_open(self):
        repo_name = "example/repo"
        branch_name = "new-branch"
        github_token = "mock_token"
        import requests
        with MockVar(requests, 'get', Mock()) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'html_url': 'http://example.com/pr'}
            self.assertTrue(GitOperations.is_pr_open(repo_name, branch_name, github_token))

            mock_get.return_value.status_code = 404
            mock_get.return_value.json.return_value = {'html_url': 'Not found'}
            self.assertFalse(GitOperations.is_pr_open(repo_name, branch_name, github_token))


class TestGitCheckout(TestCase):

    def test_basic(self):

        with TempDir(name=True, chdir=True) as tdir:
            # fail case - not a git checkout
            with self.assertRaisesRegex(ErrorInput, 'Failed to checkout branch|git remote -v failed'):
                GitCheckout().main('main')

            # delete .lock
            File('.git/abc.lock').touch(mkdir=True)
            File('.git/abc.txt').touch(mkdir=True)
            File('mods/something.lock').touch(mkdir=True)
            GitCheckout().del_lock()
            self.assertEqual(os.listdir('.git'), ['abc.txt'])
            self.assertEqual(os.listdir('mods'), ['something.lock'])

    def test_main_return_1(self):
        sha = 'abc123def456789'

        def mock_system_call(cmd_self):
            cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
            # call_count['count'] += 1
            sha_status_output = f'HEAD detached at {sha}\nworking tree clean'
            if 'git checkout' in cmd:
                return (0, sha)
            elif 'git status' in cmd:
                return (0, sha_status_output)
            else:
                return (0, '')

        with MockVar(SystemCall, 'run_outtxt', mock_system_call):
            GitCheckout().main(sha)

    def test_main_return_2(self):
        sha = 'abc123def456789'

        def mock_system_call(cmd_self):
            cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
            sha_status_output = 'blah'
            if 'git checkout' in cmd:
                return (0, sha)
            else:
                return (0, '')

        with MockVar(SystemCall, 'run_outtxt', mock_system_call):
            with MockVar(GitCheckout, 'do_success', Mock(side_effect=[False, True])):
                GitCheckout().main(sha)

    def test_main_return_3_branch(self):
        branch = 'feature-branch'
        remote_output = 'origin\thttps://github.com/intel-restricted/test-repo.git (fetch)\norigin\thttps://github.com/intel-restricted/test-repo.git (push)\n'
        branch_info_output = 'abc123def456\trefs/heads/feature-branch'

        def mock_system_call(cmd_self):
            cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
            sha_status_output = 'blah'
            if 'git checkout' in cmd:
                return (0, branch)
            elif 'git clone --recurse-submodules' in cmd:
                return (0, sha_status_output)
            elif 'git remote -v' in cmd:
                return (0, remote_output)
            elif f'git ls-remote origin {branch}' in cmd:
                return (0, branch_info_output)
            else:
                return (0, '')

        def mock_run(cmd_self, disp=False):
            # Mock for git clone command which uses .run() instead of .run_outtxt()
            return 0

        with MockVar(SystemCall, 'run_outtxt', mock_system_call):
            with MockVar(GitCheckout, 'do_success', Mock(side_effect=[False, False])):
                with MockVar(SystemCall, 'run', mock_run):
                    with MockVar(getgit_module, 'rmtree', Mock()):
                        GitCheckout().main(branch)

    def test_main_return_3_tag(self):
        tag = 'v1.0.0'
        remote_output = 'origin\thttps://github.com/intel-restricted/test-repo.git (fetch)\n'
        tag_info_output = 'abc123def456\trefs/tags/v1.0.0'

        def mock_system_call(cmd_self):
            cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
            sha_status_output = 'blah'
            if 'git checkout' in cmd:
                return (0, f'HEAD is now at abc123 {tag}')
            elif 'git clone --recurse-submodules' in cmd:
                return (0, sha_status_output)
            elif 'git remote -v' in cmd:
                return (0, remote_output)
            elif f'git ls-remote origin {tag}' in cmd:
                return (0, tag_info_output)
            else:
                return (0, '')

        def mock_run(cmd_self, disp=False):
            # Mock for git clone command which uses .run() instead of .run_outtxt()
            return 0

        with MockVar(SystemCall, 'run_outtxt', mock_system_call):
            with MockVar(GitCheckout, 'do_success', Mock(side_effect=[False, False])):
                with MockVar(SystemCall, 'run', mock_run):
                    with MockVar(getgit_module, 'rmtree', Mock()):
                        GitCheckout().main(tag)

    def test_main_return_3_sha(self):
        sha = 'abc123def456789'
        remote_output = 'origin\thttps://github.com/intel-restricted/test-repo.git (fetch)\norigin\thttps://github.com/intel-restricted/test-repo.git (push)\n'

        def mock_system_call(cmd_self):
            cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
            sha_status_output = 'blah'
            if 'git checkout' in cmd:
                return (0, sha)
            elif 'git clone --recurse-submodules' in cmd:
                return (0, sha_status_output)
            elif 'git remote -v' in cmd:
                return (0, remote_output)
            else:
                return (0, '')

        def mock_run(cmd_self, disp=False):
            # Mock for git clone command which uses .run() instead of .run_outtxt()
            return 0

        with MockVar(SystemCall, 'run_outtxt', mock_system_call):
            with MockVar(GitCheckout, 'do_success', Mock(side_effect=[False, False])):
                with MockVar(SystemCall, 'run', mock_run):
                    with MockVar(getgit_module, 'rmtree', Mock()):
                        GitCheckout().main(sha)

    def test_do_pull(self):
        self.assertEqual(GitCheckout().do_pull('tag'), None)

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, ''))):
            GitCheckout().do_pull('branch')
            SystemCall.run_outtxt.assert_called_once_with()

    def test_do_branch_success(self):
        # branch success
        msg = 'On branch main\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_branch_success('main'), True)
        # Fail case - not on branch
        msg = 'blah'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_branch_success('main'), False)
        msg = 'On branch blah\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_success('main', 'branch'), False)

    def test_do_tag_success(self):
        # tag success
        msg = 'HEAD detached at TPI/test\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_tag_success('TPI/test'), True)
        # Fail case - not detached at tag
        msg = 'blah'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_tag_success('TPI/test'), False)
        msg = 'HEAD detached at blah\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_success('TPI/test', 'tag'), False)

    def test_do_sha_success(self):
        # SHA success - abbreviated SHA in output, full SHA as parameter
        msg = 'HEAD detached at abc123d\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_sha_success('abc123def456789'), True)
        # SHA success - full SHA in output, abbreviated SHA as parameter
        msg = 'HEAD detached at abc123def456789\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_sha_success('abc123d'), True)
        # Fail case
        msg = 'blah'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_sha_success('abc123def456789'), False)
        msg = 'blah\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_sha_success('abc123d'), False)
        msg = 'HEAD detached at blah\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_sha_success('abc123d'), False)
        msg = 'HEAD detached at *\nworking tree clean'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, msg))):
            self.assertEqual(GitCheckout().do_success('abc123d', 'sha'), False)

    def test_fresh_clone_branch_success(self):
        # Test successful fresh clone workflow for branch
        branch = 'feature-branch'
        remote_output = 'origin\thttps://github.com/intel-restricted/test-repo.git (fetch)\norigin\thttps://github.com/intel-restricted/test-repo.git (push)\n'
        repo_root = '/tmp/test-repo'
        branch_info_output = 'abc123def456\trefs/heads/feature-branch'

        with TempDir(name=True, chdir=True) as tdir:
            # Create mock repo structure
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                call_count = {'count': 0}

                def mock_system_call(cmd_self):
                    # Track the sequence of git commands
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    call_count['count'] += 1

                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    elif f'git ls-remote origin {branch}' in cmd:
                        return (0, branch_info_output)
                    elif 'git checkout' in cmd:
                        return (0, f'Switched to branch {branch}')
                    elif 'git pull' in cmd:
                        return (0, 'Already up to date.')
                    else:
                        return (0, '')

                def mock_run(cmd_self, disp=False):
                    # Mock for git clone command which uses .run() instead of .run_outtxt()
                    return 0

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                GitCheckout().fresh_clone_branch(branch)

                # Verify git clone was called
                self.assertGreater(call_count['count'], 0)
            finally:
                os.chdir(original_dir)

    def test_fresh_clone_branch_git_remote_fails(self):
        # Test when git remote -v fails
        branch = 'test-branch'

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, 'fatal: not a git repository'))):
            with self.assertRaisesRegex(ErrorInput, 'git remote -v failed|Check if cwd for ref'):
                GitCheckout().fresh_clone_branch(branch)

    def test_fresh_clone_branch_unable_to_parse_remote_url(self):
        # Test when unable to parse git remote URL
        branch = 'test-branch'
        remote_output = '\n   \n'  # Empty output with whitespace

        def mock_system_call(cmd_self):
            cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
            if 'git remote -v' in cmd:
                return (0, remote_output)
            return (0, '')

        with MockVar(SystemCall, 'run_outtxt', mock_system_call):
            with self.assertRaisesRegex(ErrorInput, 'Unable to parse git remote URL'):
                GitCheckout().fresh_clone_branch(branch)

    def test_fresh_clone_branch_git_rev_parse_fails(self):
        # Test when git rev-parse --show-toplevel fails
        branch = 'test-branch'
        remote_output = 'origin\thttps://github.com/test/repo.git (fetch)\n'

        def mock_system_call(cmd_self):
            cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
            if 'git remote -v' in cmd:
                return (0, remote_output)
            elif 'git rev-parse --show-toplevel' in cmd:
                return (1, 'fatal: not a git repository')
            return (0, '')

        with MockVar(SystemCall, 'run_outtxt', mock_system_call):
            with self.assertRaisesRegex(ErrorInput, 'git rev-parse --show-toplevel failed|Check if cwd for ref'):
                GitCheckout().fresh_clone_branch(branch)

    def test_fresh_clone_branch_git_clone_fails(self):
        # Test when git clone fails
        branch = 'test-branch'
        remote_output = 'origin\thttps://github.com/test/repo.git (fetch)\n'
        repo_root = '/tmp/test-repo'

        with TempDir(name=True, chdir=True) as tdir:
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                def mock_system_call(cmd_self):
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    return (0, '')

                def mock_run_fails(cmd_self, disp=False):
                    # Mock git clone to return non-zero exit code
                    return 1

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run_fails):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                with self.assertRaisesRegex(ErrorInput, 'Failed to clone repository'):
                                    GitCheckout().fresh_clone_branch(branch)
            finally:
                os.chdir(original_dir)

    def test_fresh_clone_branch_branch_not_on_remote(self):
        # Test when branch does not exist on remote
        branch = 'nonexistent-branch'
        remote_output = 'origin\thttps://github.com/test/repo.git (fetch)\n'
        repo_root = '/tmp/test-repo'

        with TempDir(name=True, chdir=True) as tdir:
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                def mock_system_call(cmd_self):
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    elif f'git ls-remote origin {branch}' in cmd:
                        return (0, '')  # Empty output means branch doesn't exist
                    return (0, '')

                def mock_run(cmd_self, disp=False):
                    return 0

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                with self.assertRaisesRegex(ErrorInput, 'Branch.*does not exist on remote'):
                                    GitCheckout().fresh_clone_branch(branch)
            finally:
                os.chdir(original_dir)

    def test_fresh_clone_branch_git_ls_remote_fails(self):
        # Test when git ls-remote command fails
        branch = 'test-branch'
        remote_output = 'origin\thttps://github.com/test/repo.git (fetch)\n'
        repo_root = '/tmp/test-repo'

        with TempDir(name=True, chdir=True) as tdir:
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                def mock_system_call(cmd_self):
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    elif f'git ls-remote origin {branch}' in cmd:
                        return (1, 'fatal: unable to access remote')
                    return (0, '')

                def mock_run(cmd_self, disp=False):
                    return 0

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                with self.assertRaisesRegex(ErrorInput, 'Failed to query remote for branch'):
                                    GitCheckout().fresh_clone_branch(branch)
            finally:
                os.chdir(original_dir)

    def test_fresh_clone_branch_git_checkout_fails(self):
        # Test when final git checkout fails
        branch = 'test-branch'
        remote_output = 'test\norigin\thttps://github.com/test/repo.git (fetch)\n'
        repo_root = '/tmp/test-repo'
        branch_info_output = 'abc123\trefs/heads/test-branch'

        with TempDir(name=True, chdir=True) as tdir:
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                def mock_system_call(cmd_self):
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    elif f'git ls-remote origin {branch}' in cmd:
                        return (0, branch_info_output)
                    elif 'git checkout' in cmd:
                        return (1, 'error: pathspec did not match')
                    return (0, '')

                def mock_run(cmd_self, disp=False):
                    return 0

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                with self.assertRaisesRegex(ErrorInput, 'Cannot checkout branch.*cleanly for the repo'):
                                    GitCheckout().fresh_clone_branch(branch)
            finally:
                os.chdir(original_dir)

    def test_identify_ref_type(self):
        # Test identify_ref_type for SHA
        self.assertEqual(GitCheckout().identify_ref_type('abc123def456789'), 'sha')
        self.assertEqual(GitCheckout().identify_ref_type('abc123d'), 'sha')

        # Test identify_ref_type for branch
        branch_output = 'abc123\trefs/heads/feature-branch'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, branch_output))):
            self.assertEqual(GitCheckout().identify_ref_type('feature-branch'), 'branch')

        # Test identify_ref_type for tag
        tag_output = ' \nabc123\trefs/tags/v1.0.0'
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, tag_output))):
            self.assertEqual(GitCheckout().identify_ref_type('v1.0.0'), 'tag')

        # Test identify_ref_type when remote query fails - defaults to branch
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, 'fatal: not a git repo'))):
            self.assertEqual(GitCheckout().identify_ref_type('unknown-ref'), 'branch')

        # Test identify_ref_type in local refs for branch
        branch_output = 'abc123\trefs/heads/feature-branch'
        with MockVar(SystemCall, 'run_outtxt', Mock(side_effect=[
            (0, ''),
            (0, branch_output)
        ])):
            self.assertEqual(GitCheckout().identify_ref_type('feature-branch'), 'branch')

        # Test identify_ref_type in local refs for tag
        tag_output_local = ' \nabc123\trefs/tags/v1.0.0'
        with MockVar(SystemCall, 'run_outtxt', Mock(side_effect=[
            (0, ''),
            (0, tag_output_local)
        ])):
            self.assertEqual(GitCheckout().identify_ref_type('v1.0.0'), 'tag')

        # Test identify_ref_type when we can't determine - default to branch
        with MockVar(SystemCall, 'run_outtxt', Mock(side_effect=[
            (0, ''),
            (1, 'fatal: not a git repo')
        ])):
            self.assertEqual(GitCheckout().identify_ref_type('unknown-ref'), 'branch')

    def test_fresh_clone_tag_success(self):
        # Test successful fresh clone workflow for tag
        tag = 'v1.0.0'
        remote_output = 'origin\thttps://github.com/intel-restricted/test-repo.git (fetch)\n'
        tag_info_output = 'abc123def456\trefs/tags/v1.0.0'

        with TempDir(name=True, chdir=True) as tdir:
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                call_count = {'count': 0}

                def mock_system_call(cmd_self):
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    call_count['count'] += 1

                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    elif f'git ls-remote origin {tag}' in cmd:
                        return (0, tag_info_output)
                    elif 'git checkout' in cmd:
                        return (0, f'HEAD is now at abc123 {tag}')
                    else:
                        return (0, '')

                def mock_run(cmd_self, disp=False):
                    return 0

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                GitCheckout().fresh_clone_tag(tag)

                self.assertGreater(call_count['count'], 0)
            finally:
                os.chdir(original_dir)

    def test_fresh_clone_tag_not_on_remote(self):
        # Test when tag does not exist on remote
        tag = 'nonexistent-tag'
        remote_output = 'origin\thttps://github.com/test/repo.git (fetch)\n'

        with TempDir(name=True, chdir=True) as tdir:
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                def mock_system_call(cmd_self):
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    elif f'git ls-remote origin {tag}' in cmd:
                        return (0, '')  # Empty output means tag doesn't exist
                    return (0, '')

                def mock_run(cmd_self, disp=False):
                    return 0

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                with self.assertRaisesRegex(ErrorInput, 'Tag.*does not exist on remote'):
                                    GitCheckout().fresh_clone_tag(tag)
            finally:
                os.chdir(original_dir)

    def test_fresh_clone_sha_success(self):
        # Test successful fresh clone workflow for SHA
        sha = 'abc123def456789'
        remote_output = 'origin\thttps://github.com/intel-restricted/test-repo.git (fetch)\n'

        with TempDir(name=True, chdir=True) as tdir:
            test_repo = os.path.join(tdir, 'test-repo')
            mkdirs(test_repo)
            original_dir = os.getcwd()
            os.chdir(test_repo)

            try:
                call_count = {'count': 0}

                def mock_system_call(cmd_self):
                    cmd = ' '.join(cmd_self.cmd) if isinstance(cmd_self.cmd, list) else cmd_self.cmd
                    call_count['count'] += 1

                    if 'git remote -v' in cmd:
                        return (0, remote_output)
                    elif 'git rev-parse --show-toplevel' in cmd:
                        return (0, test_repo)
                    elif 'git fetch origin' in cmd:
                        return (0, '')
                    elif 'git checkout' in cmd:
                        return (0, f'HEAD is now at {sha[:7]}')
                    else:
                        return (0, '')

                def mock_run(cmd_self, disp=False):
                    return 0

                with MockVar(SystemCall, 'run_outtxt', mock_system_call):
                    with MockVar(SystemCall, 'run', mock_run):
                        with MockVar(getgit_module, 'rmtree', Mock()):
                            with MockVar(os, 'chdir', Mock()):
                                GitCheckout().fresh_clone_sha(sha)

                self.assertGreater(call_count['count'], 0)
            finally:
                os.chdir(original_dir)


class TestGitHub(TestCase):

    def test_proc_pr_diff(self):
        text = '''  gh pr diff
  shell: /usr/intel/bin/bash -e {0}
  env:
    GITHUB_TOKEN: ***
diff --git a/.github/workflows/checkers.yml b/.github/workflows/checkers.yml
index 65f3ccb3..e35a758c 100644
--- a/.github/workflows/checkers.yml
+++ b/.github/workflows/checkers.yml
@@ -26,6 +26,11 @@ jobs:
         git fetch
         git merge origin/master

+    - name: print_mod_files
+      run: gh pr diff
+      env:
+          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
+
     - name: remove_FAIL_label
       run: gh pr edit --remove-label FAILED
       env:
diff --git a/NEWFILE b/NEWFILE
new file mode 100644
index 00000000..7e175d15
--- /dev/null
+++ b/NEWFILE
@@ -0,0 +1,3 @@
+This is a new file
+new line
+new line
diff --git a/README.md b/README.md
index 987264fb..8333b7a8 100644
--- a/README.md
+++ b/README.md
@@ -15,6 +15,7 @@ block2
 line3
 line4
 line5
+line5a
 line6
 new
 new
diff --git a/ctp_simple_generic_3.xlsx b/ctp_simple_generic_3.xlsx
deleted file mode 100644
index eff2929d..00000000
Binary files a/ctp_simple_generic_3.xlsx and /dev/null differ
        '''
        expect = ['.github/workflows/checkers.yml',
                  'NEWFILE',
                  'README.md',
                  'ctp_simple_generic_3.xlsx']
        self.assertEqual(GitHub._proc_pr_diff(text), expect)

        # invalid diff
        self.assertEqual(GitHub._proc_pr_diff('\n   \n \n'), [])
        with self.assertRaisesRegex(ErrorUser, 'Cannot find modified files'):
            GitHub._proc_pr_diff('abc\n')

        timeout_text = 'could not find pull request diff: HTTP 504: 504 Gateway Timeout (https:/)\n'
        with self.assertRaisesRegex(ErrorUser, 'I_REVIEWED_THE_MASSIVE_CHANGES'):
            with MockVar(GitHub, 'get_labels', Mock(return_value={'blah'})):
                GitHub._proc_pr_diff(timeout_text)
        with MockVar(GitHub, 'get_labels', Mock(return_value={'I_REVIEWED_THE_MASSIVE_CHANGES'})):
            self.assertEqual(GitHub._proc_pr_diff(timeout_text), [])

        self.assertEqual(GitHub._proc_pr_diff('\nsomething\nsomething blah...Sorry, this diff is taking too long to generate\n'),
                         [])

        self.assertEqual(GitHub._proc_pr_diff('\nsomething\nsomething blah...Sorry, the diff exceeded the maximum number of files (300)\n'),
                         [])

    def test_get_modfiles(self):
        GitHub.clear()
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, 'diff --git a/abc b/abc'))):
            self.assertEqual(GitHub.get_modfiles(), ['abc'])

        # cached, outside of mockvar
        self.assertEqual(GitHub.get_modfiles(), ['abc'])

        # case2 - folder
        GitHub.clear()
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, 'diff --git a/folder/abc b/folder/abc'))):
            self.assertEqual(GitHub.get_modfiles(), ['folder/abc'])

    def test_add_labels(self):

        GetCmd.gh_final = 'gh'

        def fake_system_call(slf):
            cmd = ' '.join(slf.cmd)
            if 'label list' in cmd:
                return 0, 'AA   #0123\nCC   #0022\n'    # Existing labels
            if 'label create' in cmd:
                return 0, ''
            if 'pr edit' in cmd:
                return 0, ''
            if 'pr view' in cmd:
                return 0, 'labels: QQ'
            raise Exception(f'Unknown cmd: [{cmd}]')

        with MockVar(SystemCall, "run_outtxt", fake_system_call):
            with CaptureStdoutLog() as p:
                GitHub.add_labels({'AA', 'BB'})
        expect = '''CMD: gh label create BB -c 0000ff
CMD: gh pr edit --add-label AA,BB
'''
        self.assertTextEqual(p.getvalue(), expect)

        # no check
        with MockVar(SystemCall, "run_outtxt", fake_system_call):
            with CaptureStdoutLog() as p:
                GitHub.add_labels({'AA', 'BB'}, check=False)
        expect = '''CMD: gh pr edit --add-label AA,BB
'''
        self.assertTextEqual(p.getvalue(), expect)

        # remove label
        with MockVar(SystemCall, "run_outtxt", fake_system_call):
            with CaptureStdoutLog() as p:
                GitHub.remove_labels({'QQ', 'BB'})
        expect = '''CMD: gh pr view
CMD: gh pr edit --remove-label BB,QQ
'''
        self.assertTextEqual(p.getvalue(), expect)

        print("CASE label does not exist ========")
        GitHub.clear()
        with MockVar(SystemCall, "run_outtxt", fake_system_call):
            with CaptureStdoutLog() as p:
                GitHub.remove_labels({'WW'})
        print(p.getvalue())
        expect = '''CMD: gh pr view
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_get_all_labels(self):
        out = '''
infra	infrastructure related file	#3BDBC2
showstopper		#EE32EB
blah
SCN_CCF_C68		#0000ff
'''
        GitHub.clear()
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, out))):
            self.assertEqual(GitHub._get_all_labels(), {'showstopper', 'SCN_CCF_C68', 'infra'})

        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, 'line1\nline2\n'))):
            # caching
            self.assertEqual(GitHub._get_all_labels(), {'showstopper', 'SCN_CCF_C68', 'infra'})

            GitHub.clear()
            with self.assertRaisesRegex(ErrorUser, 'No valid label found'):
                GitHub._get_all_labels()

    def test_get_prno(self):
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
number: 2459
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, ARR_ATOM_L2CXX
somekey:strx
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, out))):
            GitHub.clear()
            self.assertEqual(GitHub.get_prno(), '2459')
            self.assertEqual(GitHub.get_pr_info('state'), 'OPEN')
            self.assertEqual(GitHub.get_pr_info('somekey'), 'strx')
            self.assertEqual(GitHub.get_pr_info('notfound'), '')    # notfound keyword

    def test_get_labels(self):
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, ARR_ATOM_L2CXX
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, out))):
            GitHub.clear()
            self.assertEqual(GitHub.get_labels(), {'ARR_ATOM_L2CXX', 'ARR_ATOM_CXX'})
            self.assertEqual(GitHub.get_prno(), '')

        # cached
        self.assertEqual(GitHub.get_labels(), {'ARR_ATOM_L2CXX', 'ARR_ATOM_CXX'})

        # none found
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, out))):
            GitHub.clear()
            self.assertEqual(GitHub.get_labels(), set())

        self.assertTextEqual(GitHub.get_pr_view_output(), out)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_branch_name(self):
        # real
        GitHub.clear()
        with Chdir(f'{UT_DIR}/git_checkout_testing'):
            self.assertEqual(GitHub.get_branch_name(), 'HEAD')
            self.assertEqual(GitHub.is_main_branch(), False)

        # mocked
        GitHub.clear()
        with MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, 'TP/12', ''))):
            self.assertEqual(GitHub.get_branch_name(), 'TP/12')
            self.assertEqual(GitHub.is_main_branch(), True)

        # must be cached
        with MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, 'TP/13', ''))):
            self.assertEqual(GitHub.get_branch_name(), 'TP/12')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_all_branch(self):
        # real
        GitHub.clear()
        with Chdir(f'{UT_DIR}/git_checkout_testing'):
            self.assertEqual(GitHub.get_all_branches(),
                             {'tai_pytpd', 'jdr_slim', 'drforsey', 'jdr_branch', 'master', 'jdr_sharedbin',
                              'hanna_branch', 'jollibee'})

        # mocked
        GitHub.clear()
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, 'HEAD ->\nabc\nremotes/origin/test-branch'))):
            self.assertEqual(GitHub.get_all_branches(), {'test-branch'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_submodules(self):
        # real
        with Chdir(f'{UT_DIR}/git_checkout_testing'):
            self.assertEqual(GitHub.get_submodules(), [])

        with Chdir(f'{UT_DIR}/nvl.cpu'):
            self.assertEqual(GitHub.get_submodules(), ['Shared'])

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, 'blah'))):
            with Chdir(f'{UT_DIR}/git_checkout_testing'):
                self.assertEqual(GitHub.get_submodules(), [])

        # mocked
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, '\nblah'))):
            self.assertEqual(GitHub.get_submodules(), [])

        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, '\nblahblahblahblahblahblahblahblahblahblah blah'))):
            self.assertEqual(GitHub.get_submodules(), ['blah'])


class TestGetCmd(TestCase):

    def test_basic_gh(self):
        GetCmd.gh_final = 'gh'   # Assume this

        # as is
        self.assertEqual(GetCmd.exe('blah'), 'blah')

        with MockVar(GetCmd, 'gh_final', None):
            # gh - default "gh"
            with MockVar(SystemCall, 'run_sout_serr', Mock(return_value=(0, '', ''))):
                self.assertEqual(GetCmd.exe('gh pr'), 'gh pr')
                self.assertEqual(GetCmd.gh_final, 'gh')
            with MockVar(SystemCall, 'run_sout_serr', Mock(side_effect=Exception)):
                self.assertEqual(GetCmd.exe('gh pr'), 'gh pr')

        # gh - alt - none found
        with MockVar(GetCmd, 'gh_final', None):
            with MockVar(SystemCall, 'run_sout_serr', Mock(side_effect=OSError)):
                with MockVar(GetCmd, 'gh_alt', ['/notfound']):
                    with self.assertRaisesRegex(ErrorUser, 'Cannot find'):
                        GetCmd.exe('gh pr')

        # gh - alt
        with MockVar(GetCmd, 'gh_final', None):
            with MockVar(SystemCall, 'run_sout_serr', Mock(side_effect=OSError)):
                self.assertIn(GetCmd.exe('gh pr'), ['/tmp pr', '/usr/intel/bin/gh pr'])


class TestBranches(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_commit_date_convert(self):
        dobj = Branches.commit_date_convert('Apr 26 11:15:50 2023')
        self.assertEqual(dobj.timestamp(), 1682532950)


class TestGit(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(Chdir, f'{UT_DIR}/git_testcases/eng_tp')
    def test_basic(self):
        gg = GetGit()
        self.assertEqual(gg.get_currentsha(), '8aa007a1b13f673ade5761ac5d5938ebd47fbc23')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(Chdir, f'{UT_DIR}/git_testcases')
    def test_notrepo(self):
        gg = GetGit()

        # case1: not a repo
        with self.assertRaisesRegex(ErrorUser, 'Must be in a git repo to run the tool'):
            gg.init()

        # case2: something went wrong
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, 'blah'))):
            with self.assertRaisesRegex(ErrorUser, 'Something went wrong for'):
                gg.init()

        # case3: git executable not found
        gg._gitcmd = 'gitxxxxxx'
        with self.assertRaisesRegex(ErrorUser, 'Seems like git is not installed in your system'):
            gg.init()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(Chdir, f'{UT_DIR}/git_testcases/tp_root')
    def test_to_fullsha(self):
        gg = GetGit()
        with self.assertRaisesRegex(ErrorUser, 'Pls call _init.. first.'):
            gg.to_fullsha('dead')
        gg.init()
        self.assertEqual(gg.to_fullsha('aee'), 'aee87776442988984a22c6d5d86fc4baacd92072')
        self.assertEqual(gg.to_fullsha('beef', iserror=False), '')
        with self.assertRaisesRegex(ErrorUser, 'is not found'):
            gg.to_fullsha('beef')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(Chdir, f'{UT_DIR}/git_testcases/tp_root')
    def test_get_root(self):
        # tp_root:
        #  c1 -> c2 -> c3 TP/A
        #        v
        #        c4 -> c5 -> c6 TP/B
        #              v
        #              c7 -> c8 (feature)
        c1 = 'aee87776442988984a22c6d5d86fc4baacd92072'
        c2 = 'bc67dccfff2c1e7044aca3138ebce9c23b927b78'
        c3 = '79d88e2d6af2c0f5398b23c9c7781a87d5086711'
        c4 = 'b42c228af3888bc788eec4bf680c094f927120db'
        c5 = '0faeff585fa957c39c203cd7ca16b281336ce2dd'
        c6 = 'a03b358a389dd59a1e55d26dae1cdf57ad0d2088'
        c7 = '020a971539ccc5e42dcbdb8a57ef125bc5458b87'
        c8 = 'a6a153c20487fc2629539cdbdd2c81f57aa04949'
        gg = GetGit()
        self.assertEqual(gg.get_currentsha(), c8)
        gg.init()

        # Parent
        pprint(gg.parent)
        self.assertEqual(len(gg.parent), 7)
        self.assertEqual(gg.parent[c7], {c5})

        # get_root
        self.assertEqual(gg.get_root(c8), [f'{c5} TP/B'])
        self.assertEqual(gg.get_root(c7), [f'{c5} TP/B'])
        self.assertEqual(gg.get_root(c6), [f'{c6} TP/B'])
        self.assertEqual(gg.get_root(c5), [f'{c5} TP/B'])
        self.assertEqual(gg.get_root(c4), [f'{c4} TP/B'])
        self.assertEqual(gg.get_root(c3), [f'{c3} TP/A'])
        self.assertEqual(gg.get_root(c2), [f'{c2} TP/A', f'{c2} TP/B'])
        self.assertEqual(gg.get_root(c1), [f'{c1} TP/A', f'{c1} TP/B'])

        pprint(gg.s2b)
        self.assertEqual(gg.sha2branch(c1), {'TP/A', 'TP/B'})
        self.assertEqual(gg.sha2branch(c2), {'TP/A', 'TP/B'})
        self.assertEqual(gg.sha2branch(c3), {'TP/A'})
        self.assertEqual(gg.sha2branch(c4), {'TP/B'})
        self.assertEqual(gg.sha2branch(c5), {'TP/B'})
        self.assertEqual(gg.sha2branch(c6), {'TP/B'})
        self.assertEqual(gg.sha2branch(c7), set())
        self.assertEqual(gg.sha2branch(c8), set())

        self.assertEqual(gg.detail[c1]['desc'], 'one')
        self.assertEqual(len(gg.detail), len(gg.parent))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(Chdir, f'{UT_DIR}/git_testcases/tp_root')
    def test_flatten(self):
        c8 = 'a6a153c20487fc2629539cdbdd2c81f57aa04949'
        gg = GetGit().init()
        self.assertEqual(len(list(gg.flatten(c8))), 6)

    def test_log_init(self):
        text = '''
commit 3b0605
Author: Weilan Ladeau <109176455+weilan-ladeau-intel@users.noreply.github.com>
Date:   Wed Oct 26 17:48:07 2022 -0700

    Merge pull request #1075 from intel-restricted/TPI/P28G1_DFF

    added P28G1 DFF only

commit 6697bc
Merge: bd5750837 1149409e7
Author: Weilan Ladeau <109176455+weilan-ladeau-intel@users.noreply.github.com>
Date:   Wed Oct 26 17:41:30 2022 -0700

    Merge pull request #1089 from intel-restricted/FUS/36A_BASE_FFR

    line1
    line2

commit 114940
Merge: 308779ab7 bd5750837
Author: Pham, Tai <tai.pham@intel.com>
Date:   Wed Oct 26 17:36:58 2022 -0700

    Merge remote-tracking branch 'origin/TP/36A' into FUS/36A_BASE_FFR

        '''
        gg = GetGit()
        gg._logs_init(text)
        pprint(gg.detail)
        expct = {'114940': {'author': 'Pham, Tai <tai.pham@intel.com>',
                            'date': 'Wed Oct 26 17:36:58 2022 -0700',
                            'desc': "Merge remote-tracking branch 'origin/TP/36A' into "
                                    'FUS/36A_BASE_FFR',
                            'merge': '308779ab7 bd5750837',
                            'pr': ''},
                 '3b0605': {'author': 'Weilan Ladeau '
                                      '<109176455+weilan-ladeau-intel@users.noreply.github.com>',
                            'date': 'Wed Oct 26 17:48:07 2022 -0700',
                            'desc': 'added P28G1 DFF only',
                            'pr': '#1075'},
                 '6697bc': {'author': 'Weilan Ladeau '
                                      '<109176455+weilan-ladeau-intel@users.noreply.github.com>',
                            'date': 'Wed Oct 26 17:41:30 2022 -0700',
                            'desc': 'line1; line2',
                            'merge': 'bd5750837 1149409e7',
                            'pr': '#1089'}}

        self.assertEqual(gg.detail, expct)

    def manual(self):
        gg = GetGit()
        result = set()
        gg.get_root(gg.get_currentsha(), result)
        print(result)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
