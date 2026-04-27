#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Create Pull Request Script

This script automates the process of updating submodules in specified repositories
and creating pull requests for those updates.

Usage:
    create_pr.py <top_level_arg>
    Need to Pair with a YAML GitHub WorkFlow
    https://github.com/intel-restricted/nvl.common/pull/90
    add in with scheduled + mailing feature
    https://github.com/intel-restricted/nvl.common/pull/421
    change PR title shorter [AutoPR] - {dielet} {newsha} common sha from {oldsha}
    https://github.com/intel-restricted/nvl.common/pull/685

Arguments:
    <top_level_arg>  The top-level argument specifying the type of repositories to process.
                     Valid options are:
                     - NVL
                     - NVLPOC

Environment Variables:
    CPU          : Set to 'true' to include the CPU repository.
    HUB          : Set to 'true' to include the HUB repository.
    PCD          : Set to 'true' to include the PCD repository.
    GCD          : Set to 'true' to include the GCD repository.
    ALL          : Set to 'true' to include all NVL-related repositories.
    *_BRANCH     : [1] (NVL/NVLPOC) (main* | TP/* | <not check>)
                           Read the Branch Name Provided  -->   create branch   -->  commit with new branch  -->  PR to branch name Provided
                   [2] (NVL/NVLPOC) [branch name != (main* | TP/* | <not check>)]
                           Checkout to branch provided    -->   commit changes  -->  push
    Enable_Mail  : Set to 'true' to enable mailing functionality.
                   During Schedule Run Default == 'true'

Environment Variables (Fixed):
    CPU_OWNER    : Email address of the CPU repository owner.
    HUB_OWNER    : Email address of the HUB repository owner.
    PCD_OWNER    : Email address of the PCD repository owner.
    GCD_OWNER    : Email address of the GCD repository owner.
    CC_LIST      : list of email addresses to CC on the notification email.

Example:
    create_pr.py NVL                #  with additional arguments & User Input Branch Name
    create_pr.py NVLPOC             #  with additional arguments & User Input Branch Name
"""

import setenv      # must be first in the imports
from gadget.getgit import GitOperations
from gadget.disk import rmtree, mkdirs
from gadget.pylog import log  # Use VepLog for logging
from gadget.files import TempDir
from gadget.shell import IS_UNIX, IS_WIN
from gadget.gizmo import send_mail
from gadget.data_host import DataHost
from datetime import datetime
import sys
import os

# This is needed for windows urllib3 and requests import
if IS_WIN:
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/lib/python3.8-pyston2.3/site-packages')

import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def setup_logging():
    """Configure logging to output only to the console."""
    log.stdout(string_level="INFO")  # Set up console logging with the desired log level
    log.info("Logging configured to output to console with INFO level.")


def determine_target_branch(repo_key, local_path):
    """Determine the target branch for a given repository."""
    branch_env_var = f"{repo_key}_BRANCH"
    branch_name = os.environ.get(branch_env_var, '').strip()

    if branch_name.lower() == 'default':
        default_branch, _ = GitOperations.get_default_branch_and_sha(local_path)
        log.info(f"Using default branch for {repo_key}: {default_branch}")
        return default_branch
    else:
        log.info(f"Using user-provided branch for {repo_key}: {branch_name}")
        return branch_name


def process_repository_rules(top_level_arg, target_branch):
    """Determine if a new branch should be created based on the top-level argument and target branch."""
    if top_level_arg == 'NVL' and target_branch.startswith("main"):
        return True
    elif top_level_arg == 'NVLPOC':
        return True
    return False


def transform_repo_name(repo_url):
    """Transform a repository URL into a formatted name."""
    repo_name = '/'.join(repo_url.split('/')[-2:]).replace('.git', '')
    return repo_name.replace('intel-restricted/', '').replace('.', '_').upper()


class RepoSelector:
    """Class to handle repository selection and global declarations."""

    @classmethod
    def global_declare(cls, top_level_arg, additional_args, base_path):
        """Declare global constants and variables based on the top-level argument and additional arguments."""
        if top_level_arg == 'NVL':
            common_repo_url = 'https://github.com/intel-restricted/nvl.common.git'
            submodule_path = './Shared'
            target_repo_urls = cls.get_nvl_repos(additional_args)
        elif top_level_arg == 'NVLPOC':
            common_repo_url = 'https://github.com/intel-restricted/nvl.poccommon.git'
            submodule_path = './Shared'
            target_repo_urls = cls.get_nvlpoc_repos(additional_args)
        else:
            raise ValueError(f"Unknown top-level argument: {top_level_arg}")

        shared_repo_name = transform_repo_name(common_repo_url)
        return common_repo_url, base_path, target_repo_urls, submodule_path, shared_repo_name

    @staticmethod
    def get_nvl_repos(additional_args):
        """Get NVL-related repositories based on additional arguments."""
        target_repo_urls = []

        repo_urls = {
            'CPU': "https://github.com/intel-restricted/nvl.cpu.git",
            'HUB': "https://github.com/intel-restricted/nvl.hub.git",
            'PCD': "https://github.com/intel-restricted/nvl.pcd.git",
            'GCD': "https://github.com/intel-restricted/nvl.gcd.git"
        }

        if 'ALL' in additional_args:
            target_repo_urls.extend(repo_urls.items())
        else:
            for repo_key, repo_url in repo_urls.items():
                if repo_key in additional_args:
                    target_repo_urls.append((repo_key, repo_url))

        if not target_repo_urls:
            raise ValueError("No valid target repositories specified for NVL.")
        return target_repo_urls

    @staticmethod
    def get_nvlpoc_repos(additional_args):
        """Get NVLPOC-related repositories based on additional arguments."""
        target_repo_urls = []

        repo_urls = {
            'CPU': "https://github.com/intel-restricted/nvl.poccpu.git",
            'HUB': "https://github.com/intel-restricted/nvl.pochub.git",
            'PCD': "https://github.com/intel-restricted/nvl.pocpcd.git",
            'GCD': "https://github.com/intel-restricted/nvl.pocgcd.git"
        }

        if 'ALL' in additional_args:
            target_repo_urls.extend(repo_urls.items())
        else:
            for repo_key, repo_url in repo_urls.items():
                if repo_key in additional_args:
                    target_repo_urls.append((repo_key, repo_url))

        if not target_repo_urls:
            raise ValueError("No valid target repositories specified for NVLPOC.")
        return target_repo_urls


class AutoPR_Mode:
    """Class to handle different modes of creating pull requests."""

    @staticmethod
    def default_mode(local_path, repo_key, repo_name_transformed, submodule_path, submodule_sha, common_sha, api_repo_name, github_token, created_branches, created_prs, shared_repo_name):
        """Handle the default mode where a new branch is created."""
        def generate_commit_message(repo_name_transformed, submodule_sha, common_sha):
            """Generate a standardized commit message for updating submodule SHA."""
            dielet_sha = submodule_sha[:7]
            commonrepo_sha = common_sha[:7]
            return f"[AutoPR] Update SubModule SHA for {repo_name_transformed} from {dielet_sha} to {commonrepo_sha} so that dielet has latest sha pointer"

        def generate_pr_title(repo_key, dielet_sha, commonrepo_sha):
            """Generate a standardized PR title for updating submodule SHA."""
            return f"[AutoPR] - {repo_key} {commonrepo_sha} common sha updated from {dielet_sha}"

        current = datetime.now()
        year, week, weekday = current.isocalendar()
        workweek = f"Y{str(year)[-1]}W{week}D{weekday}"
        branch_name = f"SubModule/Update_{repo_name_transformed}"
        log.info(f"Workweek for this operation: {workweek}")

        # Check if the branch already exists
        existing_branches = GitOperations.get_all_branches(local_path)
        if branch_name in existing_branches:
            # If the branch exists, check if the submodule SHA is up-to-date
            if submodule_sha == common_sha:
                log.info(f"[{branch_name}] is up to date compared to latest Common Repo SubModule {common_sha}.")
                return
            else:
                # If the SHA is outdated, update the branch
                GitOperations.checkout_branch(local_path, branch_name)
                GitOperations.update_submodule(local_path, submodule_path)
                commit_message = generate_commit_message(repo_name_transformed, submodule_sha, common_sha)
                GitOperations.commit_changes(local_path, submodule_path, commit_message)
                GitOperations.pull_branch(local_path, branch_name)  # Pull latest changes before pushing
                GitOperations.push_branch(local_path, branch_name)
                log.info(f"[{repo_name_transformed}] Branch {branch_name} updated with new submodule SHA.")

                # Check if a PR for this branch already exists
                if not GitOperations.is_pr_open(api_repo_name, branch_name, github_token):
                    # Create a pull request to the default branch
                    default_branch, _ = GitOperations.get_default_branch_and_sha(local_path)
                    pr_title = generate_pr_title(repo_key, submodule_sha[:7], common_sha[:7])
                    pr_url = GitOperations.create_pull_request(api_repo_name, branch_name, pr_title, default_branch, github_token, local_path, commit_message)
                    created_prs.append((pr_title, pr_url))
                return
        else:
            # If the branch does not exist, create it and update the submodule SHA
            GitOperations.create_branch(local_path, branch_name)
            log.info(f"[{repo_name_transformed}] Created new branch {branch_name} for changes.")
            created_branches.append(branch_name)

        GitOperations.update_submodule(local_path, submodule_path)

        # Get git status before committing
        GitOperations.get_status(local_path)

        commit_message = generate_commit_message(repo_name_transformed, submodule_sha, common_sha)

        try:
            GitOperations.commit_changes(local_path, submodule_path, commit_message)
            GitOperations.push_branch(local_path, branch_name)
            log.info(f"[{repo_name_transformed}] Branch {branch_name} created and pushed successfully.")

            # Create a pull request to the default branch
            default_branch, _ = GitOperations.get_default_branch_and_sha(local_path)
            log.info(f"[{repo_name_transformed}] Current branch: {branch_name}, Default branch: {default_branch}")

            pr_title = generate_pr_title(repo_key, submodule_sha[:7], common_sha[:7])
            log.info(f"[{repo_name_transformed}] Creating pull request with title: {pr_title}, head: {branch_name}, base: {default_branch}")
            pr_url = GitOperations.create_pull_request(api_repo_name, branch_name, pr_title, default_branch, github_token, local_path, commit_message)
            created_prs.append((pr_title, pr_url))
        except Exception as e:
            CreatePR.error_log(f"[{repo_name_transformed}] No changes to commit for {branch_name}. Error: {e}")

    @staticmethod
    def user_input_mode(local_path, target_branch, submodule_path, repo_url, submodule_sha, common_sha, api_repo_name, github_token, created_prs, repo_key, repo_name_transformed, shared_repo_name, shared_branch_name):
        """Handle the user input mode where changes are committed directly to the user-provided branch."""
        branch_name = target_branch
        log.info(f"[{repo_name_transformed}] Using existing branch {branch_name} for changes.")
        GitOperations.checkout_branch(local_path, branch_name)

        GitOperations.update_submodule(local_path, submodule_path)

        # Get git status before committing
        GitOperations.get_status(local_path)

        dielet_sha = submodule_sha[:7]
        commonrepo_sha = common_sha[:7]
        commit_message = f"[AutoPR] Update SubModule SHA for {branch_name} from {dielet_sha} to {commonrepo_sha} so that dielet has latest sha pointer"

        try:
            GitOperations.commit_changes(local_path, submodule_path, commit_message)
            GitOperations.pull_branch(local_path, branch_name)  # Pull latest changes before pushing
            GitOperations.push_branch(local_path, branch_name)
            log.info(f"[{repo_name_transformed}] Branch {branch_name} updated and pushed successfully.")
        except Exception as e:
            CreatePR.error_log(f"[{repo_name_transformed}] No changes to commit for {branch_name}. Error: {e}")

        # Compare with default branch after attempting to commit
        AutoPR_Mode.compare_with_default_branch(local_path, repo_url, submodule_path, common_sha, branch_name, api_repo_name, github_token, created_prs, repo_key, repo_name_transformed, shared_repo_name, shared_branch_name)

    @staticmethod
    def compare_with_default_branch(local_path, repo_url, submodule_path, common_sha, branch_name, api_repo_name, github_token, created_prs, repo_key, repo_name_transformed, shared_repo_name, shared_branch_name):
        """Compare the submodule SHA with the default branch and create a PR if they differ."""
        try:
            # Determine the default branch
            default_branch, _ = GitOperations.get_default_branch_and_sha(local_path)
            log.info(f"[{repo_name_transformed}] Current branch: {branch_name}, Default branch: {default_branch}")

            # Re-clone the repository to ensure we have the latest default branch state
            GitOperations.clone_repository(repo_url, local_path)
            default_submodule_sha = GitOperations.get_submodule_sha(local_path, submodule_path)

            if default_submodule_sha != common_sha:
                dielet_sha = default_submodule_sha[:7]
                commonrepo_sha = common_sha[:7]
                commit_message = f"[AutoPR] Update SubModule SHA for {repo_name_transformed} from {dielet_sha} to {commonrepo_sha} so that dielet has latest sha pointer"

                pr_title = f"[AutoPR] - {repo_key} {commonrepo_sha} common sha updated from {dielet_sha}"
                log.info(f"[{repo_name_transformed}] Creating pull request with title: {pr_title}, head: {branch_name}, base: {default_branch}")
                pr_url = GitOperations.create_pull_request(api_repo_name, branch_name, pr_title, default_branch, github_token, local_path, commit_message)
                created_prs.append((pr_title, pr_url))
            else:
                log.info(f"No changes detected between [{shared_repo_name}] {shared_branch_name} and [{repo_name_transformed}] {default_branch}.")
                created_prs.append(None)
        except Exception as e:
            CreatePR.error_log(f"[{repo_name_transformed}] Error comparing with default branch for {branch_name}. Error: {e}")


class GitHandler:
    """Class to handle Git operations."""

    @staticmethod
    def clone_and_get_sha(repo_url, local_path):
        """Clone a repository and get its default branch SHA."""
        try:
            GitOperations.clone_repository(repo_url, local_path)
            default_branch, sha = GitOperations.get_default_branch_and_sha(local_path)
            return default_branch, sha
        except Exception as e:
            CreatePR.error_log(f"Error cloning repository {repo_url}. Error: {e}")
            return None, None

    @staticmethod
    def process_repository(repo_key, repo_url, common_sha, github_token, submodule_path, base_path, top_level_arg, created_branches, created_prs, shared_repo_name, shared_branch_name):
        """Process each repository to update submodules and create PRs."""
        repo_name = '/'.join(repo_url.split('/')[-2:]).replace('.git', '')
        api_repo_name = repo_name
        repo_name_transformed = transform_repo_name(repo_url)

        local_path = os.path.join(base_path, repo_name_transformed)
        mkdirs(local_path)

        try:
            log.info(f"Processing repository: {repo_name}")
            GitOperations.clone_repository(repo_url, local_path)
            submodule_sha = GitOperations.get_submodule_sha(local_path, submodule_path)

            # Determine the target branch before any conditional logic
            target_branch = determine_target_branch(repo_key, local_path)
            log.info(f"[{repo_name_transformed}] Using branch {target_branch} for repository: {repo_key}")

            if submodule_sha != common_sha:
                create_new_branch = process_repository_rules(top_level_arg, target_branch)

                if create_new_branch:
                    AutoPR_Mode.default_mode(local_path, repo_key, repo_name_transformed, submodule_path, submodule_sha, common_sha, api_repo_name, github_token, created_branches, created_prs, shared_repo_name)
                else:
                    AutoPR_Mode.user_input_mode(local_path, target_branch, submodule_path, repo_url, submodule_sha, common_sha, api_repo_name, github_token, created_prs, repo_key, repo_name_transformed, shared_repo_name, shared_branch_name)
            else:
                log.info(f"[{repo_name_transformed}] Submodule in {repo_name_transformed} is already up-to-date.")
                AutoPR_Mode.compare_with_default_branch(local_path, repo_url, submodule_path, common_sha, target_branch, api_repo_name, github_token, created_prs, repo_key, repo_name_transformed, shared_repo_name, shared_branch_name)
        except Exception as e:
            CreatePR.error_log(f"[{repo_name_transformed}] An error occurred while processing {repo_name_transformed}: {e}")


class EmailToOwner:
    """Class to handle sending emails to repository owners."""

    def __init__(self, enable_mailing, cpu_owner, hub_owner, pcd_owner, gcd_owner, cc_list, created_branches, created_prs, error_list):
        self.enable_mailing = enable_mailing.lower() == 'true'
        self.cpu_owner = self.parse_emails(cpu_owner)
        self.hub_owner = self.parse_emails(hub_owner)
        self.pcd_owner = self.parse_emails(pcd_owner)
        self.gcd_owner = self.parse_emails(gcd_owner)
        self.cc_list = self.parse_emails(cc_list)
        self.created_branches = created_branches
        self.created_prs = created_prs
        self.error_list = error_list

    def parse_emails(self, email_string):
        """Parse a string of emails separated by commas into a list."""
        if email_string:
            return [email.strip() for email in email_string.split(',')]
        return []

    def send_email(self):
        """Send an email with the created branches, PRs, and errors."""
        if not self.enable_mailing:
            log.info("Mailing is disabled.")
            return

        # Combine all owner emails into the to_list
        to_list = self.cpu_owner + self.hub_owner + self.pcd_owner + self.gcd_owner

        # Concatenate to_list and cc_list into a single string
        recipients = ', '.join(to_list + self.cc_list)

        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        subject = f"[NVL][Common][TPDA] - Common Submodule Updated to DIELET Repo {current_time}"

        body = "Hello Dielet Repo Owner,\n\n"
        body += "Please be informed that the following PR has been committed into your Dielet Repo,\n"
        body += "\nPlease help to approve and merge it.\n"
        body += "These PR's are important to maintain all Dielet having the same common submodule and to ensure it's up to date.\n\n"

        body += "Branches Created:\n"
        for branch in self.created_branches:
            body += f"- {branch}\n"

        body += "\nPull Requests Created:\n"
        for pr in self.created_prs:
            if pr:
                pr_title, pr_url = pr
                body += f"- Title: {pr_title}, URL: {pr_url}\n"
            else:
                body += "- None\n"

        if self.error_list:
            body += "\nErrors Encountered:\n"
            for error in self.error_list:
                body += f"- {error}\n"

        body += "\n\n***This is an auto-generated email***\n"
        body += "***Please Do Not Reply***\n\n"
        body += "\n\nThanks."

        # Use DataHost to send the email with recipients as a single string
        data_host = DataHost()
        try:
            # Pass a tuple with three elements: (recipients, subject, body)
            data_host.central('sendmail', (recipients, subject, body), check=True)
            log.info(f"Email sent to {recipients}")
        except Exception as e:
            log.error(f"Failed to send email: {e}")


class CreatePR:
    """Class to handle the creation of pull requests."""
    error_list = []

    @classmethod
    def error_log(cls, message):
        """Log an error message and add it to the error list."""
        log.error(message)
        cls.error_list.append(message)

    def __init__(self):
        if len(sys.argv) < 2:
            self.error_log("A top-level argument is required.")
        self.top_level_arg = sys.argv[1]
        self.additional_args = self.get_additional_args()
        self.current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        self.github_token = GitOperations.get_gh_token()

    def get_additional_args(self):
        """Retrieve additional arguments from environment variables."""
        additional_args = []
        if os.environ.get('ALL', 'False').lower() == 'true':
            additional_args.extend(['CPU', 'HUB', 'PCD', 'GCD'])
        else:
            if os.environ.get('CPU', 'False').lower() == 'true':
                additional_args.append('CPU')
            if os.environ.get('HUB', 'False').lower() == 'true':
                additional_args.append('HUB')
            if os.environ.get('PCD', 'False').lower() == 'true':
                additional_args.append('PCD')
            if os.environ.get('GCD', 'False').lower() == 'true':
                additional_args.append('GCD')
        return additional_args

    def main(self):
        """Main entry point for creating pull requests."""
        setup_logging()
        log.info(f"Top Level Args : {self.top_level_arg}")
        log.info(f"Additional Args: {self.additional_args}")

        created_branches = []
        created_prs = []

        with TempDir(name=True) as base_path:
            log.info("Starting global declaration.")
            common_repo_url, base_path, target_repo_urls, submodule_path, shared_repo_name = RepoSelector.global_declare(
                self.top_level_arg, self.additional_args, base_path
            )
            log.info("Global declaration completed.")

            # Ensure the common repository is cloned
            common_local_path = os.path.join(base_path, 'common_repo')
            if not os.path.exists(common_local_path):
                log.info(f"Cloning common repository from {common_repo_url} to {common_local_path}.")
                mkdirs(common_local_path)
                shared_branch_name, common_sha = GitHandler.clone_and_get_sha(common_repo_url, common_local_path)
                log.info(f"Common repository cloned. SHA: {common_sha}, Default branch: {shared_branch_name}")
            else:
                log.info(f"Common repository already exists at {common_local_path}. Retrieving SHA.")
                shared_branch_name, common_sha = GitOperations.get_default_branch_and_sha(common_local_path)
                log.info(f"Retrieved SHA: {common_sha}, Default branch: {shared_branch_name}")

            for repo_key, repo_url in target_repo_urls:
                local_path = os.path.join(base_path, repo_key)
                mkdirs(local_path)
                log.info(f"Cloning repository: {repo_key}")
                GitOperations.clone_repository(repo_url, local_path)

                log.info(f"Checking branch for repository: {repo_key}")
                target_branch = determine_target_branch(repo_key, local_path)
                log.info(f"[{repo_key}] Using branch {target_branch} for repository: {repo_key}")
                GitHandler.process_repository(repo_key, repo_url, common_sha, self.github_token, submodule_path, base_path, self.top_level_arg, created_branches, created_prs, shared_repo_name, shared_branch_name)
                log.info(f"[{repo_key}] Completed processing for repository: {repo_url}")

        log.info("Cleanup completed.")

        # Print the created branches and PRs
        print("\nBranches Created:")
        for branch in created_branches:
            print(f"- {branch}")

        print("\nPull Requests Created:")
        for pr in created_prs:
            if pr:
                pr_title, pr_url = pr
                print(f"- Title: {pr_title}, URL: {pr_url}")
            else:
                print("- None")

        # Print errors and exit if any occurred
        if self.error_list:
            print("\nErrors Encountered:")
            for error in self.error_list:
                print(f"- {error}")
            sys.exit(1)

        # After processing, send email
        email_to_owner = EmailToOwner(
            enable_mailing=os.environ.get('ENABLE_MAILING', 'false'),
            cpu_owner=os.environ.get('CPU_OWNER', ''),
            hub_owner=os.environ.get('HUB_OWNER', ''),
            pcd_owner=os.environ.get('PCD_OWNER', ''),
            gcd_owner=os.environ.get('GCD_OWNER', ''),
            cc_list=os.environ.get('CC_LIST', ''),
            created_branches=created_branches,
            created_prs=created_prs,
            error_list=self.error_list
        )
        email_to_owner.send_email()


if __name__ == "__main__":
    create_pr = CreatePR()
    create_pr.main()
