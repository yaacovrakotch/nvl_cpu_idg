#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Git api module - getgit
"""
from .errors import confirm, ErrorUser, ErrorInput
from .shell import SystemCall, HOSTNAME
from .disk import Chdir, rmtree, Allfiles
from .files import File
from .gizmo import Elapsed
from .pylog import log
from pprint import pprint
from collections import defaultdict
from datetime import datetime
import re
import os


class GitOperations:
    """Class to handle local Git operations and GitHub interactions."""

    @staticmethod
    def clone_repository(repo_url, local_path):
        """Clone a Git repository to a local path."""
        if os.path.exists(local_path):
            rmtree(local_path)  # Use rmtree from gadget.disk
        ecode, output = SystemCall(['git', 'clone', repo_url, local_path], disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to clone repository {repo_url} to {local_path}. Error: {output}")
        log.info(f"Repository {repo_url} cloned to {local_path}. Output: {output}")

    @staticmethod
    def get_default_branch_and_sha(local_path):
        """Get the default branch name and latest commit SHA of a repository."""
        with Chdir(local_path):  # Use Chdir from gadget.disk
            ecode, default_branch_ref = SystemCall(['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'], disp=True).run_outtxt()
            if ecode != 0:
                raise Exception(f"Failed to get default branch. Error: {default_branch_ref}")
            default_branch = default_branch_ref.replace('refs/remotes/origin/', '')
            ecode, latest_sha = SystemCall(['git', 'rev-parse', f'origin/{default_branch}'], disp=True).run_outtxt()
            if ecode != 0:
                raise Exception(f"Failed to get latest SHA. Error: {latest_sha}")
        return default_branch, latest_sha

    @staticmethod
    def get_submodule_sha(local_path, submodule_path):
        """Get the current SHA of a submodule."""
        with Chdir(local_path):  # Use Chdir from gadget.disk
            ecode, output = SystemCall(['git', 'submodule', 'update', '--init', '--recursive', '--force', submodule_path], disp=True).run_outtxt()
            if ecode != 0:
                raise Exception(f"Failed to update submodule. Error: {output}")
            with Chdir(submodule_path):
                ecode, submodule_sha = SystemCall(['git', 'rev-parse', 'HEAD'], disp=True).run_outtxt()
                if ecode != 0:
                    raise Exception(f"Failed to get submodule SHA. Error: {submodule_sha}")
        return submodule_sha

    @staticmethod
    def create_branch(local_path, branch_name):
        """Create a new branch in the repository."""
        ecode, output = SystemCall(['git', 'checkout', '-b', branch_name], cwd=local_path, disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to create branch {branch_name}. Error: {output}")

    @staticmethod
    def checkout_branch(local_path, branch_name):
        """Checkout an existing branch in the repository."""
        ecode, output = SystemCall(['git', 'checkout', branch_name], cwd=local_path, disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to checkout branch {branch_name}. Error: {output}")
        log.info(f"Checked out branch {branch_name} in {local_path}. Output: {output}")

    @staticmethod
    def get_all_branches(local_path):
        """Return a set of all branches in the repository."""
        with Chdir(local_path):  # Ensure the command is run in the correct directory
            ecode, output = SystemCall(['git', 'branch', '-a'], disp=True).run_outtxt()
            if ecode != 0:
                raise Exception(f"Failed to get all branches. Error: {output}")

            branches = set()
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('remotes/origin/'):
                    branches.add(line.replace('remotes/origin/', ''))
            return branches

    @staticmethod
    def update_submodule(local_path, submodule_path):
        """Update a submodule to the latest commit."""
        ecode, output = SystemCall(['git', 'submodule', 'update', '--remote', submodule_path], cwd=local_path, disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to update submodule {submodule_path}. Error: {output}")

    @staticmethod
    def get_status(local_path, print_status=True):
        """Get the status of the Git repository.

        :param local_path: Path to the local git repository
        :type local_path: str
        :param print_status: Whether to log the status output to screen (default: True)
        :type print_status: bool
        :return: Git status output
        :rtype: str
        """
        ecode, output = SystemCall(['git', 'status'], cwd=local_path, disp=print_status).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to get git status. Error: {output}")
        if print_status:
            log.info(f"Git status output:\n{output}")
        return output

    @staticmethod
    def commit_changes(local_path, submodule_path, message):
        """Commit changes in the repository."""
        ecode, output = SystemCall(['git', 'add', submodule_path], cwd=local_path, disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to add changes. Error: {output}")
        ecode, output = SystemCall(['git', 'commit', '-m', message], cwd=local_path, disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to commit changes. Error: {output}")

    @staticmethod
    def pull_branch(local_path, branch_name):
        """Pull the latest changes from the remote branch."""
        ecode, output = SystemCall(['git', 'pull', 'origin', branch_name], cwd=local_path, disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to pull branch {branch_name}. Error: {output}")

    @staticmethod
    def push_branch(local_path, branch_name):
        """Push a branch to the remote repository."""
        ecode, output = SystemCall(['git', 'push', 'origin', branch_name], cwd=local_path, disp=True).run_outtxt()
        if ecode != 0:
            raise Exception(f"Failed to push branch {branch_name}. Error: {output}")

    @staticmethod
    def get_gh_token():
        """Retrieve the GitHub token from environment variables."""
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is not set.")
        return token

    @staticmethod
    def create_tag(local_path, tag_name, sha):
        """Create a tag at a specific SHA in the repository."""
        with Chdir(local_path):  # Ensure the command is run in the correct directory
            ecode, output = SystemCall(['git', 'tag', tag_name, sha], disp=True).run_outtxt()
            if ecode != 0:
                raise Exception(f"Failed to create tag {tag_name} at {sha}. Error: {output}")
            log.info(f"Tag {tag_name} created at {sha}. Output: {output}")

    @staticmethod
    def push_tag(local_path, tag_name):
        """Push a tag to the remote repository."""
        with Chdir(local_path):  # Ensure the command is run in the correct directory
            ecode, output = SystemCall(['git', 'push', 'origin', tag_name], disp=True).run_outtxt()
            if ecode != 0:
                raise Exception(f"Failed to push tag {tag_name}. Error: {output}")
            log.info(f"Tag {tag_name} pushed to remote. Output: {output}")

    @staticmethod
    def get_all_tags(local_path):
        """Get all tags in the repository."""
        with Chdir(local_path):  # Ensure the command is run in the correct directory
            ecode, output = SystemCall(['git', 'tag'], disp=True).run_outtxt()
            if ecode != 0:
                raise Exception(f"Failed to get tags. Error: {output}")
            tags = output.split('\n')
            log.info(f"Tags in repository: {tags}")
            return tags

    @staticmethod
    def create_pull_request(repo_name, branch_name, pr_title, base_branch, github_token, local_path, commit_message):
        """Create a pull request on GitHub."""
        import requests

        # Use the new standardized template for all PRs
        pr_body = f"""### Why is this PR needed?
{commit_message}

### What type of PR is this?
- [ ] New Planned Feature     (First PR to a planned item)
- [ ] New Unplanned Feature   (First PR to an unplanned item)
- [ ] Response to a Sighting  (First PR to a sighting/QE event/bug)
- [ ] Fix to a previous PR
- [X] Other, pls specify: auto update

### Who/Where is the source of this PR change?
- [ ] Planned item
- [ ] Sighting
- [ ] QE event, Paste url: _____
- [ ] Feedback/Request from: _____
- [X] Other, pls specify: automated update

### Does this PR come with a common PR?
- [X] No
- [ ] Yes. Pls specify common PR url: _____

### Which Bins are affected?
- [ ] Many bins (Can't tell specific since this change affect many downstream bins)
- [ ] Specific bins, Pls specify: _____
- [X] Not applicable (This PR does not affect bins)

### Socket(s) affected by this PR (HOT/COLD/PHM)?
- [ ] HOT
- [ ] COLD
- [ ] PHM
- [ ] Other Socket, Pls specify: _____
- [X] Non-tester file/Automation PR

### Which package(s) are affected?
- [X] Not applicable
- [ ] All packages
- [ ] Novalake S 28C
- [ ] Novalake S 52C
- [ ] Novalake S 28C BLLC
- [ ] Novalake S 16C
- [ ] Novalake UL 6C
- [ ] Novalake U 8C
- [ ] Novalake H 16C
- [ ] Novalake P 16C
- [ ] Novalake HX 28C
- [ ] Novalake AX 28C
- [ ] Novalake AX 16C
- [ ] Dunlow S 28C

### VALIDATION INFO:
- [X] No validation performed
- [ ] Load and init only or offline
- [ ] Standing die check. If MBOT, please provide URL log: _____
- [ ] VPO: Please specify VPO #: _____

### VALIDATION Temperature:
- [ ] VPO CLASS HOT
- [ ] VPO COLD (CSM/PHMCOLD/PHMROOM)
- [ ] VPO PHM HOT
- [ ] MBOT default temp
- [ ] Other, please specify Temp: _____
- [X] Not applicable (no validation performed or load/init only or offline)

### Other detail worth mentioning?
Automated submodule update PR created by the submodule update script.

---
**Instructions above: Put 'X' inside the square brackets if you have performed that validation. No space between brackets.**

**All the sections are required to pass checkers except "other details worth mentioning" section.**
    """

        url = f"https://api.github.com/repos/{repo_name}/pulls"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {github_token}"
        }
        data = {
            "title": pr_title,
            "head": branch_name,
            "base": base_branch,
            "body": pr_body
        }

        response = requests.post(url, json=data, headers=headers, verify=False)

        if response.status_code == 201:
            pr = response.json()
            log.info(f"Created PR: {pr['html_url']}")
            return pr['html_url']
        else:
            log.error(f"Failed to create PR: {response.status_code}")
            log.error(response.json().get('message', 'No message'))
            return None

    @staticmethod
    def is_pr_open(repo_name, branch_name, github_token):
        """Check if a PR is open for the given branch."""
        import requests

        url = f"https://api.github.com/repos/{repo_name}/pulls"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {github_token}"
        }
        params = {
            "state": "open",
            "head": f"{repo_name.split('/')[0]}:{branch_name}"
        }

        response = requests.get(url, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            prs = response.json()
            return len(prs) > 0
        else:
            log.error(f"Failed to check PR status: {response.status_code}")
            log.error(response.json().get('message', 'No message'))
            return False


class GitCheckout:
    """
    Robust way to checkout a branch or tag or sha with submodule for pipelines.

    Design:
    - main() contains unified checkout logic for all ref types
    - do_pull() only pulls for branches (tags/SHAs are immutable)
    - do_success() dispatches to type-specific success validation
    - fresh_clone() dispatches to type-specific fresh clone methods
    - Separate success validation methods for each type (do_branch_success, do_tag_success, do_sha_success)
    """

    def main(self, ref):
        """
        Main entry point for checkout. Identifies ref type and routes to appropriate handler.

        :param ref: branch name, tag name, or SHA to checkout
        :type ref: str
        :return: 1 for success on first try, 2 for success after forced cleanup, 3 for fresh clone
        :rtype: int
        """
        log.info(f'Start GitCheckout {ref}, cwd: {os.getcwd()}')

        # Identify what type of ref this is
        ref_type = self.identify_ref_type(ref)
        log.info(f'-i- Identified ref "{ref}" as type: {ref_type}')

        # Easy path - common cleanup
        self.del_lock()
        SystemCall(f'git merge --abort', disp=True).run_sout_serr()
        SystemCall(f'git reset --hard', disp=True).run_outtxt()
        SystemCall(f'git clean -xfd', disp=True).run_outtxt()

        # These two commands to remove duplicate case sensitive windows branches
        SystemCall(['git', 'submodule', 'foreach', '--recursive', 'git fetch --prune'], disp=True).run_outtxt()
        SystemCall(f'git fetch --prune', disp=True).run_outtxt()

        # Do the checkout
        self._checkout_ref(ref, ref_type)

        # Pull latest changes (only for branches)
        self.do_pull(ref_type)

        if self.do_success(ref, ref_type):       # pragma: no cover     (success is tested separately)
            return 1      # success

        # Do forced cleanup and retry
        SystemCall(f'git submodule deinit --force --all', disp=True).run_outtxt()
        self._checkout_ref(ref, ref_type)
        self.do_pull(ref_type)
        SystemCall(f'git submodule update --init --recursive --force', disp=True).run_outtxt()

        if self.do_success(ref, ref_type):       # pragma: no cover     (success is tested separately)
            return 2      # success

        # If not success, we delete and clone from scratch
        log.info(f'-i- Cannot checkout {ref_type} cleanly even after forced cleanup. Deleting and recloning repo:')

        if ref_type == 'branch':
            self.fresh_clone_branch(ref)
        elif ref_type == 'tag':
            self.fresh_clone_tag(ref)
        else:
            self.fresh_clone_sha(ref)

        return 3

    def identify_ref_type(self, ref):
        """
        Identify if ref is a branch, tag, or SHA by querying the remote.

        :param ref: reference name to identify
        :type ref: str
        :return: 'branch', 'tag', or 'sha'
        :rtype: str
        """
        # First check if it looks like a SHA
        if self.is_sha(ref):
            return 'sha'

        # Query remote to check if it's a branch or tag
        # git ls-remote output format: <sha>\trefs/heads/<branch> or <sha>\trefs/tags/<tag>
        ecode, output = SystemCall(f'git ls-remote origin {ref}', disp=True).run_outtxt()
        if ecode != 0:
            # If ls-remote fails, we'll try checkout anyway and let it fail there
            log.warning(f'-w- Could not query remote for ref {ref}, will attempt checkout')
            return 'branch'  # Default to branch behavior

        # Parse the output to determine ref type
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            # Format: <sha>\trefs/heads/<name> or <sha>\trefs/tags/<name>
            if f'refs/heads/{ref}' in line:
                return 'branch'
            if f'refs/tags/{ref}' in line:
                return 'tag'

        # If not found in remote, check local refs
        # This handles cases where the ref exists locally but not on remote
        ecode, output = SystemCall(f'git show-ref {ref}', disp=True).run_outtxt()
        for line in output.splitlines():
            line = line.strip()
            if f'refs/heads/{ref}' in line:
                return 'branch'
            if f'refs/tags/{ref}' in line:
                return 'tag'

        # Default to branch if we can't determine
        log.warning(f'-w- Could not determine ref type for {ref}, defaulting to branch')
        return 'branch'

    def _checkout_ref(self, ref, ref_type):
        """
        Execute git checkout for a ref and return success status.

        :param ref: reference to checkout
        :type ref: str
        :return: None
        """
        ecode, output = SystemCall(f'git checkout {ref}', disp=True).run_outtxt()
        if ecode != 0:
            repo_name = self._get_repo_name()
            raise ErrorInput(f'Failed to checkout {ref_type} "{ref}" in repo "{repo_name}". Error: {output}',
                             f'Please verify the {ref_type} name is correct for this repository')

    def _get_repo_name(self):
        """
        Get the repository name for error messages.

        :return: repository name
        :rtype: str
        """
        _, repo_root = SystemCall('git rev-parse --show-toplevel', disp=True).run_outtxt()
        return os.path.basename(repo_root.strip()) if repo_root else 'unknown'

    def do_pull(self, ref_type):
        """
        Pull latest changes for branches only. Tags and SHAs are immutable.

        :param ref_type: type of reference ('branch', 'tag', or 'sha')
        :type ref_type: str
        """
        if ref_type != 'branch':
            return
        SystemCall(f'git pull', disp=True).run_outtxt()

    def do_success(self, ref, ref_type):
        """
        Check if checkout was successful by dispatching to the appropriate success method.

        :param ref: reference that was checked out
        :type ref: str
        :param ref_type: type of reference ('branch', 'tag', or 'sha')
        :type ref_type: str
        :return: True if checkout was successful
        :rtype: bool
        """
        if ref_type == 'branch':
            return self.do_branch_success(ref)
        elif ref_type == 'tag':
            return self.do_tag_success(ref)
        else:
            return self.do_sha_success(ref)

    def do_branch_success(self, branch):
        """
        Check if branch checkout was successful.

        :param branch: branch name that was checked out
        :type branch: str
        :return: True if on the expected branch with clean working tree
        :rtype: bool
        """
        ecode, output = SystemCall(f'git status', disp=True).run_outtxt()

        # Check for clean working tree
        if 'working tree clean' not in output:
            return False

        # Check if on the expected branch
        if f'On branch {branch}' in output:
            log.info(f'-i- Successfully on branch {branch}')
            return True

        return False

    def do_tag_success(self, tag):
        """
        Check if tag checkout was successful.

        :param tag: tag name that was checked out
        :type tag: str
        :return: True if HEAD is detached at the expected tag with clean working tree
        :rtype: bool
        """
        ecode, output = SystemCall(f'git status', disp=True).run_outtxt()

        # Check for clean working tree
        if 'working tree clean' not in output:
            return False

        # Check if detached HEAD at the expected tag
        if f'HEAD detached at {tag}' in output:
            log.info(f'-i- Successfully on tag HEAD at {tag}')
            return True

        return False

    def do_sha_success(self, sha):
        """
        Check if SHA checkout was successful.

        :param sha: SHA that was checked out
        :type sha: str
        :return: True if HEAD is detached at the expected SHA with clean working tree
        :rtype: bool
        """
        ecode, output = SystemCall(f'git status', disp=True).run_outtxt()

        # Check for clean working tree
        if 'working tree clean' not in output:
            return False

        # Check if detached HEAD at the expected SHA
        if f'HEAD detached at {sha}' in output:
            log.info(f'-i- Successfully on SHA HEAD at {sha}')
            return True

        # Git may abbreviate SHA in status output, so check prefix matching
        if 'HEAD detached at' in output:
            match = re.search(r'HEAD detached at ([0-9a-f]+)', output, re.IGNORECASE)
            if match:
                displayed_sha = match.group(1).lower()
                sha_lower = sha.lower()
                # Check if either is a prefix of the other (handles abbreviated SHAs)
                if sha_lower.startswith(displayed_sha) or displayed_sha.startswith(sha_lower):
                    log.info(f'-i- Successfully on detached HEAD at SHA {displayed_sha}, matches {sha}')
                    return True

        return False

    def _fresh_clone_common(self, ref):
        """
        Common fresh clone operations: get URL, delete repo, clone fresh.

        :param ref: reference to checkout after clone
        :type ref: str
        :return: tuple of (clone_url, repo_name, parent_dir, repo_root)
        :rtype: tuple
        """
        log.info(f'Start fresh_clone {ref}, cwd: {os.getcwd()}')

        # 1. Get the clone URL via "git remote -v"
        ecode, output = SystemCall('git remote -v', disp=True).run_outtxt()
        confirm(not ecode, f'git remote -v failed: {output}',
                f'Check if cwd for ref {ref} is valid repo', cls=ErrorInput)

        # Parse the output to get the URL from the first valid line
        clone_url = None
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                clone_url = parts[1]
                log.info(f'Parsed clone URL: {clone_url}')
                break
        confirm(clone_url, 'Unable to parse git remote URL from `git remote -v` output.',
                f'Output was:\n{output}', cls=ErrorInput)

        # 2. Get the repo root directory
        ecode, repo_root = SystemCall('git rev-parse --show-toplevel', disp=True).run_outtxt()
        confirm(not ecode, f'git rev-parse --show-toplevel failed: {repo_root}',
                f'Check if cwd for ref {ref} is valid repo', cls=ErrorInput)
        repo_root = repo_root.strip()

        # 3. get parent directory (one level up from repo root)
        parent_dir = os.path.dirname(repo_root)
        repo_name = os.path.basename(repo_root)

        return clone_url, repo_name, parent_dir, repo_root

    def fresh_clone_branch(self, branch):
        """
        Deletes the entire folder and fresh clone, then checkout branch.

        :param branch: branch to checkout
        :type branch: str
        :return: None
        """
        clone_url, repo_name, parent_dir, repo_root = self._fresh_clone_common(branch)

        with Chdir(parent_dir):
            rmtree(repo_root)

            # Fresh clone
            ecode = SystemCall(f'git clone --recurse-submodules {clone_url} {repo_name}').run(disp=True)
            confirm(ecode == 0, f'Failed to clone repository {clone_url} into {repo_name}.',
                    f'Check that the repository URL is correct and accessible.', cls=ErrorInput)

            with Chdir(repo_name):
                # Verify branch exists on remote
                ecode, ref_info = SystemCall(f'git ls-remote origin {branch}', disp=True).run_outtxt()
                confirm(ecode == 0, f'Failed to query remote for branch {branch}: {ref_info}',
                        f'Check that remote "origin" is accessible and branch {branch} is spelled correctly.', cls=ErrorInput)

                # Check specifically for branch (refs/heads/)
                confirm(f'refs/heads/{branch}' in ref_info, f'Branch {branch} does not exist on remote "origin".',
                        f'Create the branch {branch} on the remote or choose an existing one.', cls=ErrorInput)

                # Checkout branch and pull
                ecode, output = SystemCall(f'git checkout {branch}', disp=True).run_outtxt()
                confirm(ecode == 0, f'Cannot checkout branch {branch} cleanly for the repo {repo_name}: {output}',
                        f'Ensure branch {branch} exists and can be checked out.', cls=ErrorInput)

                SystemCall(f'git pull', disp=True).run_outtxt()

    def fresh_clone_tag(self, tag):
        """
        Deletes the entire folder and fresh clone, then checkout tag.

        :param tag: tag to checkout
        :type tag: str
        :return: None
        """
        clone_url, repo_name, parent_dir, repo_root = self._fresh_clone_common(tag)

        with Chdir(parent_dir):
            rmtree(repo_root)

            # Fresh clone
            ecode = SystemCall(f'git clone --recurse-submodules {clone_url} {repo_name}').run(disp=True)
            confirm(ecode == 0, f'Failed to clone repository {clone_url} into {repo_name}.',
                    f'Check that the repository URL is correct and accessible.', cls=ErrorInput)

            with Chdir(repo_name):
                # Verify tag exists on remote
                ecode, ref_info = SystemCall(f'git ls-remote origin {tag}', disp=True).run_outtxt()
                confirm(ecode == 0, f'Failed to query remote for tag {tag}: {ref_info}',
                        f'Check that remote "origin" is accessible and tag {tag} is spelled correctly.', cls=ErrorInput)

                # Check specifically for tag (refs/tags/)
                confirm(f'refs/tags/{tag}' in ref_info, f'Tag {tag} does not exist on remote "origin".',
                        f'Create the tag {tag} on the remote or choose an existing one.', cls=ErrorInput)

                # Checkout tag (no pull - tags are immutable)
                ecode, output = SystemCall(f'git checkout {tag}', disp=True).run_outtxt()
                confirm(ecode == 0, f'Cannot checkout tag {tag} cleanly for the repo {repo_name}: {output}',
                        f'Ensure tag {tag} exists and can be checked out.', cls=ErrorInput)

    def fresh_clone_sha(self, sha):
        """
        Deletes the entire folder and fresh clone, then checkout SHA.

        :param sha: SHA to checkout
        :type sha: str
        :return: None
        """
        clone_url, repo_name, parent_dir, repo_root = self._fresh_clone_common(sha)

        with Chdir(parent_dir):
            rmtree(repo_root)

            # Fresh clone
            ecode = SystemCall(f'git clone --recurse-submodules {clone_url} {repo_name}').run(disp=True)
            confirm(ecode == 0, f'Failed to clone repository {clone_url} into {repo_name}.',
                    f'Check that the repository URL is correct and accessible.', cls=ErrorInput)

            with Chdir(repo_name):
                # For SHAs, fetch all refs to ensure we have the commit
                SystemCall(f'git fetch origin', disp=True).run_outtxt()

                # Checkout SHA (no pull - SHAs are immutable)
                ecode, output = SystemCall(f'git checkout {sha}', disp=True).run_outtxt()
                confirm(ecode == 0, f'Cannot checkout SHA {sha} cleanly for the repo {repo_name}: {output}',
                        f'Ensure SHA {sha} exists and can be checked out.', cls=ErrorInput)

    def del_lock(self):
        """Delete all .lock files in current dir"""
        for ff in Allfiles('.'):
            if '.git' in ff:    # this also match .github, but it's ok. remember unix vs windows / vs \\
                if ff.endswith('.lock'):
                    log.info(f'-i- del_lock: deleting {ff}')
                    File(ff).unlink()

    @staticmethod
    def is_sha(ref):
        """
        Check if ref looks like a git SHA (40 hex chars or abbreviated 7+ hex chars).

        :param ref: reference to check
        :type ref: str
        :return: True if ref looks like a SHA
        :rtype: bool
        """
        # Full SHA: 40 hex chars, or abbreviated: 7-40 hex chars
        return bool(re.match(r'^[0-9a-f]{7,40}$', ref.lower()))


class GitHub:
    """
    GH PR commandline
    This is like a singleton where all operations are class methods for caching purpose

    Example below of output of "gh pr view":

title:	ARRATOM/21G_SoC_SoCSRAM_removal to TP/21G Merge:Correction to bypass rule to make CLASSCOLD work correctly
state:	OPEN
author:	santhanakrishnan-balakrishnan-intel
labels:	ARR_ATOM_L2CXX
assignees:
reviewers:	chen3-chen-intel (Requested), damien-pena-intel (Requested), danny-phan-intel (Requested), ddharmar (Requested), iceylu (Requested), john-q-delos-reyes-intel (Requested), kenneth-j-anderson-intel (Requested), maria-luisa-ignacio-intel (Requested), nicholas-johansen-intel (Requested), shiv-gourshetty-intel (Requested), tai-pham-intel (Requested), victor-danielle-gatchalian-intel (Requested), vikram-mohite-intel (Requested), weilan-ladeau-intel (Requested)
projects:
milestone:	21G
number:	2495
url:	https://github.com/intel-restricted/mtlp68/pull/2495
additions:	2
deletions:	2
--
FROM:      Bypass rule bypassing test instance at CLASSCOLD
TO:        Removed bypass rule at CLASSCOLD on test instance
REASON:    to apply RWA correctly at CLASSCOLD
IMPACT:    yield
FBIN:      bin60xx
SOCKET:    P682
DETAILS:   <Other details worth mentioning not captured above>

VALIDATION INFO:
- [X] Load and init
- [X] Standing Die
- [X] VPO HOT: (NV307003MV)
- [X] VPO COLD: (NV307003MV)
- [ ] VPO PHM HOT: (Specify VPO number here)
- [ ] VPO PHM COLD: (Specify VPO number here)

<Instructions above: Put 'X' inside the square brackets if you have performed that validation. No space between brackets.>
    """
    modfiles = None
    pr_view_output = None
    br_name = None
    gh_all_labels = None

    @classmethod
    def clear(cls):
        """Clear all the cache variables - mainly for unittests"""
        cls.modfiles = None
        cls.pr_view_output = None
        cls.br_name = None
        cls.gh_all_labels = None     # this is not cleared by default

    @classmethod
    def _init_pr_view(cls):
        """Execute pr view and save"""
        if cls.pr_view_output:
            return    # Do nothing

        cmd = "gh pr view"
        _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()
        cls.pr_view_output = out

    @classmethod
    def _init_br_name(cls):
        """Initialize br name"""
        if cls.br_name:
            return

        cmd = "git rev-parse --abbrev-ref HEAD"
        _, out, _ = SystemCall(GetCmd.exe(cmd), disp=True).run_sout_serr()    # accept stdout only
        out = out.strip()
        confirm(out, f'Output of git, to get branch name is empty. See above.',
                'Contact TPI as this needs to be addressed')
        cls.br_name = out

    @classmethod
    def get_modfiles(cls):
        """
        Return the modified files for this checkout

        Problem with using "gh pr diff": It cannot process very long since it shows the actual diff

        Refactor this later to use:
        origin/TP/37B is base: ${{ github.event.pull_request.head.ref }}
        origin/JDR/multi_commit is the current branch
        git merge-base origin/TP/37B origin/JDR/multi_commit
        git diff --name-only bb44a6cdd784075fd69f526e760a794d51c9b8a7..origin/JDR/multi_commit
        """
        if cls.modfiles:
            return cls.modfiles

        cmd = "gh pr diff"
        _, out = SystemCall(GetCmd.exe(cmd)).run_outtxt()
        # print(f"output of {cmd} ===============:")
        # print(out)
        cls.modfiles = cls._proc_pr_diff(out)
        return cls.modfiles

    @classmethod
    def _proc_pr_diff(cls, out):
        """Process the output of 'gh pr diff' and return modified+add+removed files"""
        result = []
        r_mod = re.compile(r'diff --git a/(\S+)')   # This applies to modified, add and deleted
        empty = True

        if 'Sorry, this diff is taking too long to generate' in out:
            return []   # empty

        if 'Sorry, the diff exceeded the maximum number of' in out:
            return []   # empty

        for line in out.split('\n'):
            if not line.strip():   # ignore empty lines
                continue
            empty = False

            # modified / add / delete
            res = r_mod.search(line)
            if res:
                result.append(res.group(1))

        if empty:
            return []     # empty

        if not result:
            log.info('output of gh pr diff below:')
            log.info(out)
            if 'Gateway Timeout' in out:
                if 'I_REVIEWED_THE_MASSIVE_CHANGES' in cls.get_labels():
                    log.info('-i- I_REVIEWED_THE_MASSIVE_CHANGES is found. Returning empty modified files')
                    return []    # cannot derive diff
                raise ErrorUser('There are too many diffs found for this PR. Pls check if you intend to commit '
                                'this many changes.',
                                'Pls review the "Files changed" in the PR, and if the changes are expected, then '
                                'add this special label: I_REVIEWED_THE_MASSIVE_CHANGES')
            else:
                raise ErrorUser('Cannot find modified files. Seems like output of [gh pr diff] has changed?',
                                'See output above. Contact jqdelosr.')

        log.info(f'-i- Modified files, total={len(result)}, based on [gh pr diff]:')
        for ctr, item in enumerate(result, 1):
            log.info(f'   {ctr}. {item}')
        return result

    @classmethod
    def add_labels(cls, labels, check=True, branch=''):
        """
        Add labels to the PR
        :param labels: set of labels
        :param check: Set to False to not check
        :param branch: optional: which branch associated to the pr
        :return: Nothing
        """
        if check:
            # 1 - get all existing labels
            all_labels = cls._get_all_labels()

            # 2 - create labels
            for newlabel in (labels - all_labels):
                cmd = f'gh label create {newlabel} -c 0000ff'
                _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()
                cls.gh_all_labels = None    # clear it

        # 3 - add label to the PR
        label_all_comma = ','.join(sorted(labels))
        cmd = f'gh pr edit {branch} --add-label {label_all_comma}'
        _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()
        cls.pr_view_output = None   # so that labels are reset

    @classmethod
    def _get_all_labels(cls):
        """Return set of all labels"""
        if cls.gh_all_labels:
            return cls.gh_all_labels

        cmd = "gh label list -L 3000"
        _, out = SystemCall(GetCmd.exe(cmd)).run_outtxt()
        result = set()
        for line in out.split('\n'):
            if '#' in line:    # this identifies the color
                result.add(line.split()[0])

        if not result:
            print(f"output of {cmd} ===============:")
            print(out)
            raise ErrorUser(f'No valid label found from [{cmd}]',
                            'Check output above. Is gh version old?')
        cls.gh_all_labels = result
        return cls.gh_all_labels

    @classmethod
    def is_main_branch(cls, _robj=re.compile(r'^TP/\d+$')):
        r"""
        Returns true if current checkout is main branch
        Main branch: TP/<\d+>
        """
        return bool(_robj.search(cls.get_branch_name()))

    @classmethod
    def get_branch_name(cls):
        """
        Return the branch name. If it is not on a brach, it is 'HEAD'
        """
        cls._init_br_name()
        return cls.br_name

    @classmethod
    def get_prno(cls):
        """Return the pr number in string or empty if not found"""
        cls._init_pr_view()
        for line in cls.pr_view_output.split('\n'):
            if line.startswith('number:'):
                return line.split()[-1]
        return ''

    @classmethod
    def get_pr_info(cls, keyword):
        """
        Return the pr info (eg. DRAFT|OPEN for keyword='state')
        Return empty string if not found
        :param keyword: state|author|etc
        :return: string
        """
        cls._init_pr_view()
        _key = f'{keyword}:'
        for line in cls.pr_view_output.split('\n'):
            if line.startswith(_key):
                return line[len(_key):].strip()
        return ''

    @classmethod
    def get_labels(cls):
        """Return a set of labels of this PR"""
        cls._init_pr_view()
        for line in cls.pr_view_output.split('\n'):
            if line.startswith('labels:'):
                labels = set(line.replace(',', ' ').split())
                labels.remove('labels:')
                return labels
        return set()   # None

    @classmethod
    def get_pr_view_output(cls):
        """Return the pr view output"""
        cls._init_pr_view()
        return cls.pr_view_output

    @classmethod
    def get_all_branches(cls):
        """Return a set of all branches"""
        cmd = f'git branch -al'
        _, text = SystemCall(GetCmd.exe(cmd)).run_outtxt()
        result = set()
        for line in text.split('\n'):
            if 'HEAD ->' in line:
                continue
            if line.strip().startswith('remotes/origin/'):
                result.add(line.strip().replace('remotes/origin/', ''))
        return result

    @classmethod
    def get_submodules(cls):
        """Return list of submodules"""
        cmd = f'git submodule status'
        _, text = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()
        final = []
        for line in text.split('\n'):
            elems = line.strip().split()
            if not elems:
                continue
            if len(elems[0]) == 40:
                final.append(elems[1])
            else:
                log.info(f'-w- Unknown output from [git submodule status]: [{line}]')
        return final

    @classmethod
    def remove_labels(cls, labels):
        """
        Remove labels
        :param labels: list of labels to remove
        :return:
        """
        exist_labels = cls.get_labels()
        if bool(set(labels) & exist_labels):
            label_all_comma = ','.join(sorted(labels))
            cmd = f'gh pr edit --remove-label {label_all_comma}'
            SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()
            cls.pr_view_output = None      # so that labels are reset
            # log.info(f'-i- New labels: {cls.get_labels()}')


class GetCmd:
    """
    Wrapper for SystemCall cmd so that correct gh or other commands can be replaced
    In unix this is simple gh, but in windows, sometimes it is not installed
    """
    gh_alt = ['I:/engineering/dev/team_classtp/torch/bot_tpload/gh.exe',
              'J:/engineering/dev/team_classtp/torch/bot_tpload/gh.exe',     # for sort
              '/usr/intel/bin/gh',
              '/tmp']      # for unix unittest
    gh_final = None

    @classmethod
    def exe(cls, cmd):
        """
        Updates the command to full path

        :param cmd: command
        :return:
        """
        if cmd.startswith('gh '):
            return cls._gh(cmd)
        return cmd    # Do nothing

    @classmethod
    def _gh(cls, cmd):
        """Return the gh command"""
        if not cls.gh_final:
            try:
                SystemCall('gh --help').run_sout_serr()
                cls.gh_final = 'gh'
            except OSError:
                for apath in cls.gh_alt:
                    if os.path.exists(apath):
                        cls.gh_final = apath
                        break
                else:
                    raise ErrorUser('Cannot find gh.exe', 'Pls have this installed in the machine')

        return f'{cls.gh_final} {cmd[3:]}'


class Branches:
    """
    Class to manage github branches, specially deleting

    Plans/usage for this class:
    1. swiss_knife.py -branchprev    # Display all branches to be deleted
    2. swiss_knife.py -branchgo      # Execute deletion, save in a specific file, based on 'git remote -v', with date of deletion

    Commands:
    git branch -a --format='%(objectname) %(refname)' --merged | grep refs/remotes | grep -v /TP/ | grep -v HEAD | sed 's/refs/remotes/origin///g'
    git push --delete origin -d $ab   # actual delete
    git branch -a --format='%(refname:short) %(committerdate)'    # older branches

    location: /intel/tpvalidation/engtools/tptools/mtl/tp_reports/branch_delete/mtlp68/

    confirm:
    grep TP/ 2023_may_19.txt       # confirm no TP/
    grep HEAD 2023_may_19.txt      # confirm no HEAD
    git branch -a --merged | awk '{print $1}' | grep ' '        # confirm no spaces
    """

    @classmethod
    def commit_date_convert(cls, gitdate):
        """
        Convert comitterdate to datetime object.
        howto dates: https://intelpedia.intel.com/Tvpv/python#datetime

        :param gitdate: String "Apr 26 11:15:50 2023"
        :return: datetime object
        """
        return datetime.strptime(gitdate, "%b %d %H:%M:%S %Y")


class GetGit:    # pragma: no cover  - currently under developement - not used yet
    """
    Take care of git related operations
    Caller has to do "pull" to get latest info, then this class will work on the data structure
    """

    def __init__(self):
        self.revlist = {}   # { sha: {set of childs} }
        self.branch = {}    # { branch: sha}
        self.s2b = defaultdict(set)       # { sha: {set of main_branches} }

        # Derived data
        self.parent = defaultdict(set)    # { sha: {set of parents} }
        self.allsha = ''    # long string, concatenated by newline, all shas
        self.detail = {}      # {sha: {'desc': v, 'pr': v, 'Author': v}

        # constants
        self._gitcmd = 'git'

    def init(self):
        """Do basic initializations"""
        if self.revlist:
            return self   # do nothing

        sw = Elapsed()

        # check first if cwd is a git repo
        cmd = f'{self._gitcmd} rev-list --children --all'
        try:
            ecode, out = SystemCall(cmd).run_outtxt()     # special because of git repo check
        except OSError as e:
            raise ErrorUser(f'Error: {e}',
                            f'Seems like git is not installed in your system. Pls install git first.')

        if ecode:
            if 'not a git repository' in out:
                raise ErrorUser(f'Not a git repository: {os.getcwd()}',
                                f'Must be in a git repo to run the tool.')
            else:
                raise ErrorUser(f'Something went wrong for: {cmd}',
                                f'Output:\n{out}')

        # process the revlist
        for line in out.split('\n'):
            elem = line.split()
            self.revlist[elem[0]] = set(elem[1:])
        self.allsha = '\n'.join(sorted(self.revlist))

        # assign branch
        out = self._call('branch', '-a -v')
        for line in out.split('\n'):
            elem = line.replace('*', '').strip().split()   # if branch name has space, then it's screwed up
            if len(elem) >= 2 and elem[1] != '->':
                self.branch[elem[0]] = self.to_fullsha(elem[1])

        # assign parents
        for sha in self.revlist:    # sha is parent
            for child in self.revlist[sha]:
                self.parent[child].add(sha)

        # assign description and pr
        out = self._call('rev-list', '--all --pretty')
        self._logs_init(out)

        # print(f'_init: {sw}')    # normally 3.8 sec from unix
        return self

    def _logs_init(self, out):
        """
        assign self.detail given the output of git
        :param sha: starting sha
        :param max:
        """
        data = {}
        sha = None
        robj = re.compile(r'^(Author|Date|Merge):\s+(.*)')
        rpr = re.compile(r'Merge pull request (#\d+)')
        for line in out.split('\n'):
            if not line.strip():
                continue

            if line.startswith('commit '):
                if data:
                    self.detail[sha] = data
                sha = line.split()[1]
                data = {'pr': '',
                        'desc': ''}
                continue

            res = robj.search(line)
            if res:
                data[res.group(1).lower()] = res.group(2).strip()
                continue

            res = rpr.search(line)
            if res:
                data['pr'] = res.group(1)
            else:
                if data['desc']:
                    data['desc'] += f'; {line.strip()}'
                else:
                    data['desc'] = line.strip()

        if data:
            self.detail[sha] = data

    def flatten(self, sha, _seen=None):
        """
        Iterator
        :param sha: starting sha
        :param _seen: internal storage of seen sha
        :return: sha
        """
        if _seen is None:
            _seen = set()
        for _ in range(1000000):
            if sha in _seen:
                return
            yield sha
            _seen.add(sha)
            parents = self.parent[sha]
            if not parents:
                return
            sha = list(parents)[0]
            if len(parents) > 1:
                for parent in parents:
                    if sha != parent:
                        for item in self.flatten(parent, _seen):
                            yield item

    def pull(self):
        """Do a git pull and clear the vars"""
        self.__init__()     # clear all vars
        self._call('pull')

    def _call(self, cmd, args=''):
        """
        Call git from a system call with checks
        :param cmd: git command
        :param args: args
        :return: output
        """
        cmd = f'{self._gitcmd} {cmd} {args}'
        ecode, out = SystemCall(cmd).run_outtxt()
        confirm(not ecode, f'Error during git call: [{cmd}]', f'git output:\n{out}', cls=ErrorInput)
        return out

    def to_fullsha(self, shortsha, iserror=True):
        """
        Convert shortsha to full sha
        :param shortsha: sha
        :param iserror: if sha is not found, then raise exception, else return empty string
        :return: long sha or empty string
        """
        if not self.allsha:    # for performance
            raise ErrorUser('Incorrect usage to to_fullsha(). allsha is uninitialized.',
                            'Pls call _init() first.')

        if len(shortsha) == 40 and shortsha in self.revlist:
            return shortsha    # do nothing, it is already full sha

        result = re.findall(r'^(%s\w+)' % shortsha, self.allsha, re.MULTILINE)
        if not result:
            if iserror:
                raise ErrorUser(f'GetGit(): sha={shortsha} is not found.',
                                f'There are {len(self.revlist)} shas. Check: {os.getcwd()}')
            else:
                return ''

        confirm(len(result) == 1,
                f'GetGit(): sha={shortsha} is found more than once. Pls be more specific',
                f'Found: {result}')
        return result[0]

    def get_currentsha(self):
        """Return the current sha of cwd"""
        out = self._call('log', '-n 1')
        for line in out.split('\n'):
            if line.startswith('commit'):
                return line.split()[1]
        raise ErrorUser(f'Something went wrong with [git log -n 1].',
                        f'Output:\n{out}')

    def get_lineage(self, sha, mbranch='TP/'):
        """
        Prints the lineage of this branch up to the root
        :param sha: input sha
        :param mbranch: which root branch to check with
        :return: list of sorted branches
        """
        # initialization
        self.init()
        fullsha = self.to_fullsha(sha)
        result = set()
        self._get_root(fullsha, mbranch, result, lineage=1)
        return sorted(result)

    def integ_sha(self):
        """
        Return all integ sha in the root
        return: {sha: <list_of_integ_branches>}
        """
        ias = defaultdict(list)
        for br in sorted(self.branch):
            if not br.startswith('remotes/origin/Integ'):
                continue
            # found = False
            # res = re.search('Integ/(\w\w\w)', br)
            # if res:
            #     tpbranch = res.group(1)
            # else:
            #     continue
            rsha = self.get_root_pr(self.branch[br])
            ias[rsha].append(br.replace('remotes/origin/', ''))

            # for root in self.get_root(self.branch[br]):
            #     rsha, rootbranch = root.split()
            #     if rootbranch == f'TP/{tpbranch}':
            #         ias[rsha] = br.replace('remotes/origin/', '')
            #         found = True
            # if not found:
            #     continue   # wierd integ branches

        return ias

    def get_root_pr(self, sha):
        """
        returns the first parent sha which is PR
        :param sha: sha (normally integ sha)
        :return: parent sha which is a PR
        """
        for itemsha in list(self.flatten(sha)):
            if self.detail[itemsha]['pr']:
                return itemsha

    def get_root(self, sha, mbranch='TP/'):
        """
        Returns the root branch of sha
        :param sha: input sha
        :param mbranch: which root branch to check with
        :return: list of sorted branches
        """
        # initialization
        self.init()
        fullsha = self.to_fullsha(sha)
        result = set()
        self._get_root(fullsha, mbranch, result)
        return sorted(result)

    def _get_root(self, sha, mbranch, result, lineage=0):
        """
        recursive - return the root branches of a given sha
        :param sha: input full sha
        :param mbranch: which root branch to check with
        :param result: resulting set
        :param lineage: Set to 1 to display lineage
        :return: none
        """
        if lineage:
            print(f'lineage #{lineage}: {sha} {self.s2b.get(sha, "")}')
            lineage += 1

        # first-pass: is this sha main tp branch?
        done = False
        for branch in sorted(self.sha2branch(sha)):
            if branch.startswith(mbranch):
                result.add(f'{sha} {branch}')
                done = True
        if done:
            return

        # second-pass: recurse to each of the parent, until answer is found
        for parent in sorted(self.parent[sha]):
            self._get_root(parent, mbranch, result, lineage)

    def sha2branch(self, sha, mbranch='TP/'):
        """
        Given sha, return all main-branches associated to this sha
        :param sha: input full sha
        :return: set of main-branches
        """
        if self.s2b:
            return self.s2b.get(sha, set())

        # assign self.s2b first
        for branchlong in sorted(self.branch):
            xsha = self.branch[branchlong]
            branch = branchlong.replace('remotes/origin/', '')
            if branch.startswith(mbranch):
                self.s2b[xsha].add(branch)
                for parentsha in sorted(self.parent[xsha]):
                    self._s2b_recurse(parentsha, branch, mbranch)

        return self.s2b.get(sha, set())

    def _s2b_recurse(self, sha, branch, mbranch):
        """Assign self.s2b recursively"""
        if branch in self.s2b.get(sha, []):
            return    # Already seen
        self.s2b[sha].add(branch)
        for parentsha in sorted(self.parent[sha]):
            self._s2b_recurse(parentsha, branch, mbranch)
