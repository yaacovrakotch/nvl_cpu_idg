import subprocess
import sys
import os
import shutil
import glob
import json
from gadget.helperclass import OPT
from gadget.pylog import log
from gadget.errors import confirm, ErrorUser, ErrorInput
from gadget.files import check_and_del, TempDir
from gadget.getgit import GitOperations
from gadget.shell import SystemCall
from gadget.disk import mkdirs
from os.path import join, exists, isdir, basename, dirname, relpath

##############################################################
# Configuration
# region
##############################################################

# Repository URLs (used for cloning)
pytpd_repo_url = "https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd.git"
module_agent_repo_url = "https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.module-agent.git"

# Separator width for consistent formatting
SEP_WIDTH = 70

##############################################################
# endregion Configuration
##############################################################

##############################################################
# Git Operations Class
# region
##############################################################


class LocalGitHelper:
    """Class for managing local Git operations using gadget utilities."""

    @staticmethod
    def is_git_repo(repo_path):
        """Check if the given path is a git repository."""
        git_dir = os.path.join(repo_path, ".git")
        return os.path.exists(git_dir)

    @staticmethod
    def has_clean_working_directory(repo_path):
        """Check if the repository has a clean working directory."""
        status_output = GitOperations.get_status(repo_path, print_status=False)
        # Check for "working tree clean" or "nothing to commit" in status
        return "working tree clean" in status_output or "nothing to commit" in status_output

    @staticmethod
    def get_current_branch(repo_path):
        """Get the current branch name."""
        ecode, output = SystemCall(['git', 'branch', '--show-current'], cwd=repo_path).run_outtxt()
        if ecode == 0 and output.strip():
            return output.strip()
        return None

    @staticmethod
    def pull_latest_changes(repo_path):
        """Pull latest changes from origin."""
        current_branch = LocalGitHelper.get_current_branch(repo_path)
        confirm(current_branch, "Could not determine current branch", "Ensure you are in a git repository with a valid branch")

        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Pulling latest changes from git")
        log.info("-i- " + "-" * SEP_WIDTH)

        try:
            GitOperations.pull_branch(repo_path, current_branch)
            log.info(f"-i- Pulled latest changes from origin/{current_branch}")
            return True
        except Exception as e:
            raise ErrorUser(f"Git pull failed: {e}")

    @staticmethod
    def get_commit_info(repo_path):
        """Get the latest commit info (short SHA and message)."""
        ecode_sha, sha_output = SystemCall(['git', 'rev-parse', '--short', 'HEAD'], cwd=repo_path).run_outtxt()
        ecode_msg, msg_output = SystemCall(['git', 'log', '-1', '--pretty=%B'], cwd=repo_path).run_outtxt()

        short_sha = sha_output.strip() if ecode_sha == 0 else "unknown"
        commit_msg = msg_output.strip() if ecode_msg == 0 else "unknown"

        return short_sha, commit_msg

##############################################################
# endregion Git Operations Class
##############################################################

##############################################################
# Repository Cloning Class
# region
##############################################################


class RepositoryCloner:
    """Class for cloning repositories to temporary directories."""

    @staticmethod
    def clone_module_agent_repo():
        """Clone Module Agent repo to a temporary directory using TempDir."""
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Cloning Module Agent Repository")
        log.info("-i- " + "-" * SEP_WIDTH)

        temp_dir = TempDir(samename="module_agent")
        module_agent_path = temp_dir.name()
        log.info(f"-i- Destination: {module_agent_path}")

        try:
            GitOperations.clone_repository(module_agent_repo_url, module_agent_path)
            return temp_dir  # Return TempDir object for cleanup management
        except Exception as e:
            temp_dir.close()  # Clean up on error
            return None

    @staticmethod
    def clone_pytpd_repo():
        """Clone pytpd repo to a temporary directory using TempDir."""
        log.info("-i- " + "-" * SEP_WIDTH)

        temp_dir = TempDir(samename="pytpd")
        pytpd_path = temp_dir.name()

        try:
            GitOperations.clone_repository(pytpd_repo_url, pytpd_path)
            return temp_dir  # Return TempDir object for cleanup management
        except Exception as e:
            temp_dir.close()  # Clean up on error
            return None

##############################################################
# endregion Repository Cloning Class
##############################################################

##############################################################
# Module Agent Instructions Class
# region
##############################################################


class ModuleAgentInstructions:
    """Class for managing Module Agent copilot instructions."""

    @staticmethod
    def update_copilot_instructions(target_file, source_file):
        """Update copilot-instructions.md, respecting MODULE_AGENT_INSTRUCTIONS tags if present."""
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()

        if not os.path.exists(target_file):
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(source_content)
            log.info(f"-i- Created new copilot-instructions.md")
            return

        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()

        start_tag = "<!-- MODULE_AGENT_INSTRUCTIONS_START -->"
        end_tag = "<!-- MODULE_AGENT_INSTRUCTIONS_END -->"

        if start_tag in target_content and end_tag in target_content:
            start_idx_source = source_content.find(start_tag)
            end_idx_source = source_content.find(end_tag)

            if start_idx_source == -1 or end_idx_source == -1:
                log.warning(f"-w- Source file doesn't have proper tags, skipping update")
                return

            module_agent_section = source_content[start_idx_source:end_idx_source + len(end_tag)]

            start_idx_target = target_content.find(start_tag)
            end_idx_target = target_content.find(end_tag)

            new_content = (target_content[:start_idx_target] +
                           module_agent_section +
                           target_content[end_idx_target + len(end_tag):])

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            log.info(f"-i- Updated Module Agent section in copilot-instructions.md")
        else:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(source_content)
            log.info(f"-i- Replaced copilot-instructions.md (no tags found)")

    # Relative path (within module-agent folder) of the product config file to preserve
    PRODUCT_CONFIG_RELPATH = join("instructions", "product-config.instructions.md")

    @staticmethod
    def copy_module_agent_folder(repo_path, module_agent_path):
        """
        Copy .github/agents/module-agent folder from module-agent repo to target repo.
        Deletes and recreates the target folder if it already exists, but preserves
        any user-edited product-config.instructions.md in the target.

        :param repo_path: Path to target repository
        :type repo_path: str
        :param module_agent_path: Path to module-agent repository
        :type module_agent_path: str
        :return: True if folder was copied, False otherwise
        :rtype: bool
        """
        source_folder = join(module_agent_path, ".github", "agents", "module-agent")
        target_folder = join(repo_path, ".github", "agents", "module-agent")

        if not exists(source_folder):
            log.warning(f"-w- Source .github/agents/module-agent folder missing from module-agent repo")
            return False

        # Create target agents directory if it doesn't exist
        agents_dir = join(repo_path, ".github", "agents")
        if not exists(agents_dir):
            mkdirs(agents_dir, mode="0o2770")
            log.info(f"-i- Created .github/agents directory")

        # Preserve product-config.instructions.md if it already exists
        product_config_path = join(target_folder, ModuleAgentInstructions.PRODUCT_CONFIG_RELPATH)
        preserved_content = None
        if exists(product_config_path):
            with open(product_config_path, 'r', encoding='utf-8') as f:
                preserved_content = f.read()

        # Remove existing module-agent folder if it exists, then copy
        if exists(target_folder):
            check_and_del(target_folder, error=False, mv_on_error=True)

        shutil.copytree(source_folder, target_folder)
        log.info(f"-i- Copied agents/module-agent folder")

        # Restore preserved product-config.instructions.md
        if preserved_content is not None:
            instructions_dir = join(target_folder, "instructions")
            if not exists(instructions_dir):
                mkdirs(instructions_dir, mode="0o2770")
            with open(product_config_path, 'w', encoding='utf-8') as f:
                f.write(preserved_content)
            log.info(f"-i- Preserved existing product-config.instructions.md")

        return True

    @staticmethod
    def copy_module_agent_md(repo_path, module_agent_path):
        """
        Copy .github/agents/module-agent.agent.md from module-agent repo to target repo.

        :param repo_path: Path to target repository
        :type repo_path: str
        :param module_agent_path: Path to module-agent repository
        :type module_agent_path: str
        :return: True if file was copied, False otherwise
        :rtype: bool
        """
        source_file = join(module_agent_path, ".github", "agents", "module-agent.agent.md")

        if not exists(source_file):
            log.warning(f"-w- Source .github/agents/module-agent.agent.md missing from module-agent repo")
            return False

        agents_dir = join(repo_path, ".github", "agents")
        if not exists(agents_dir):
            mkdirs(agents_dir, mode="0o2770")
            log.info(f"-i- Created .github/agents directory")

        target_file = join(agents_dir, "module-agent.agent.md")
        shutil.copy2(source_file, target_file)
        log.info(f"-i- Copied agents/module-agent.agent.md")
        return True

    @staticmethod
    def update_product_config_instructions(repo_path, product_class):
        """
        Create or update product-config.instructions.md with product-specific configuration.

        :param repo_path: Path to target repository
        :type repo_path: str
        :param product_class: Product class name (e.g., 'JGSClass', 'CBRClass', 'TestChip')
        :type product_class: str
        :return: True if file was created/updated, False otherwise
        :rtype: bool
        """
        instructions_dir = join(repo_path, ".github", "agents", "module-agent", "instructions")
        if not exists(instructions_dir):
            mkdirs(instructions_dir, mode="0o2770")
            log.info(f"-i- Created .github/agents/module-agent/instructions directory")

        product_config_file = join(instructions_dir, "product-config.instructions.md")
        content = f"# Product Configuration\n\nProduct Class: {product_class}\n"
        with open(product_config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        log.info(f"-i- Created product-config.instructions.md for product class: {product_class}")
        return True

    @staticmethod
    def process_module_agent_for_repo(repo_path, module_agent_path):
        """Process and update Module Agent instructions for a repository."""
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Updating Module Agent Instructions")
        log.info("-i- " + "-" * SEP_WIDTH)

        github_dir = join(repo_path, ".github")
        if not exists(github_dir):
            mkdirs(github_dir, mode="0o2770")
            log.info(f"-i- Created .github directory")

        source_file = join(module_agent_path, ".github", "copilot-instructions.md")
        target_file = join(github_dir, "copilot-instructions.md")

        if not os.path.exists(source_file):
            log.warning(f"-w- Source copilot-instructions.md not found in module-agent repo")
            return False

        ModuleAgentInstructions.update_copilot_instructions(target_file, source_file)

        # Copy agents/module-agent folder
        ModuleAgentInstructions.copy_module_agent_folder(repo_path, module_agent_path)

        # Copy agents/module-agent.agent.md
        ModuleAgentInstructions.copy_module_agent_md(repo_path, module_agent_path)

        log.info("-i- " + "-" * SEP_WIDTH)
        return True

##############################################################
# endregion Module Agent Instructions Class
##############################################################

##############################################################
# Module Agent Skills Class
# region
##############################################################


class ModuleAgentSkills:
    """Class for managing Module Agent GitHub skills."""

    @staticmethod
    def copy_skills_folder(repo_path, module_agent_path):
        """
        Copy .github/skills/* from module-agent repo to target repo.

        - Creates .github/skills folder if it doesn't exist
        - Deletes and overwrites skills folders with matching names
        - Preserves skills folders in target that don't match module-agent skills

        :param repo_path: Path to target repository
        :type repo_path: str
        :param module_agent_path: Path to module-agent repository
        :type module_agent_path: str
        :return: True if skills were copied, False otherwise
        :rtype: bool
        """
        source_skills = join(module_agent_path, ".github", "skills")
        target_skills = join(repo_path, ".github", "skills")

        if not exists(source_skills):
            log.info(f"-i- No .github/skills folder found in module-agent repo, skipping")
            return False

        # Create target skills folder if it doesn't exist
        if not exists(target_skills):
            mkdirs(target_skills, mode="0o2770")
            log.info(f"-i- Created .github/skills directory")

        # Get list of skills in source
        source_skill_names = set()
        if isdir(source_skills):
            source_skill_names = {item for item in os.listdir(source_skills)
                                  if isdir(join(source_skills, item))}

        if not source_skill_names:
            log.info(f"-i- No skills folders found in module-agent repo")
            return False

        # Delete matching skills in target before copying
        skills_deleted = 0
        if exists(target_skills):
            for skill_name in source_skill_names:
                target_skill_path = join(target_skills, skill_name)
                if exists(target_skill_path):
                    check_and_del(target_skill_path, error=False, mv_on_error=True)
                    skills_deleted += 1
                    log.info(f"-i- Removed existing skill folder: {skill_name}")

        # Copy skills from source to target
        skills_copied = 0
        for skill_name in source_skill_names:
            src_skill_path = join(source_skills, skill_name)
            dst_skill_path = join(target_skills, skill_name)

            if isdir(src_skill_path):
                shutil.copytree(src_skill_path, dst_skill_path)
                skills_copied += 1
                log.info(f"-i- Copied skill folder: {skill_name}")

        if skills_copied > 0:
            log.info(f"-i- Successfully copied {skills_copied} skill folder(s)")
            return True
        else:
            log.warning(f"-w- No skill folders were copied")
            return False

##############################################################
# endregion Module Agent Skills Class
##############################################################

##############################################################
# PyTPD Framework Update Class
# region
##############################################################


class PyTPDFrameworkUpdater:
    """Class for updating PyTPD framework files in repositories."""

    @staticmethod
    def copy_pytpd_framework(repo_path, pytpd_repo_path):
        """Copy PyTPD framework files to target repository."""
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Updating PyTPD Framework")
        log.info("-i- " + "-" * SEP_WIDTH)

        # Ensure Scripts/pytpd exists in selected repo, clear it, and copy contents from pytpd repo
        selected_scripts_pytpd = join(repo_path, "Scripts", "pytpd")
        mkdirs(selected_scripts_pytpd, mode="0o2770")

        log.info("-i- Clearing existing PyTPD installation...")

        # Delete everything in Scripts/pytpd except .git
        for item in os.listdir(selected_scripts_pytpd):
            if item == '.git':
                continue
            item_path = join(selected_scripts_pytpd, item)
            check_and_del(item_path, error=False, mv_on_error=True)

        log.info("-i- Copying new PyTPD contents...")

        # Copy all contents from pytpd_repo_path into Scripts/pytpd, skipping .vs, .vscode, and .git folders
        skip_folders = {'.vs', '.vscode', '.git'}
        for item in os.listdir(pytpd_repo_path):
            if item in skip_folders:
                continue
            src_path = join(pytpd_repo_path, item)
            dst_path = join(selected_scripts_pytpd, item)
            if isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        log.info(f"-i- Copied PyTPD contents to Scripts/pytpd")

    @staticmethod
    def add_version_marker(repo_path, short_sha, commit_link, pymtpl_folder=None):
        """Create version marker file in pymtpl folder with commit information."""
        # Use provided pymtpl_folder if given (for installations), otherwise find it
        if pymtpl_folder is None:
            selected_usercode_pymtpl = RepositoryProcessor.get_pymtpl_folder(repo_path)
            confirm(selected_usercode_pymtpl, f"No pymtpl folder found in repository: {repo_path}", "Expected one of: Shared/BaseInputs/Scripts/pymtpl, Scripts/pymtpl/pymtpl, UserCode/pymtpl/pymtpl, UserCode/pymtpl, or BaseInputs/Scripts/[Pp]ymtpl")
        else:
            selected_usercode_pymtpl = pymtpl_folder

        confirm(isdir(selected_usercode_pymtpl), f"-e- Required folder not found: {selected_usercode_pymtpl}", "Please ensure the pymtpl folder exists in the repository")

        # Remove any .pytpd_* file and create new .pytpd_SHORTSHA file with commit_link
        pytpd_pattern = join(selected_usercode_pymtpl, ".pytpd_*")
        for oldfile in glob.glob(pytpd_pattern):
            try:
                os.remove(oldfile)
            except Exception as e:
                log.warning(f"-w- Warning: Could not delete {oldfile}: {e}")

        newfile = join(selected_usercode_pymtpl, f".pytpd_{short_sha}")
        with open(newfile, "w") as f:
            f.write(commit_link)
        log.info(f"-i- Created version marker: .pytpd_{short_sha}")

        return selected_usercode_pymtpl

    @staticmethod
    def add_module_agent_version_marker(repo_path, short_sha, commit_link, pymtpl_folder=None):
        """
        Create Module Agent version marker file in pymtpl folder with commit information.

        :param repo_path: Path to target repository
        :type repo_path: str
        :param short_sha: Short SHA of Module Agent commit
        :type short_sha: str
        :param commit_link: Full URL to Module Agent commit
        :type commit_link: str
        :param pymtpl_folder: Optional pymtpl folder path (if None, will find it)
        :type pymtpl_folder: str
        :return: Path to pymtpl folder
        :rtype: str
        """
        # Use provided pymtpl_folder if given (for installations), otherwise find it
        if pymtpl_folder is None:
            selected_usercode_pymtpl = RepositoryProcessor.get_pymtpl_folder(repo_path)
            confirm(selected_usercode_pymtpl, f"No pymtpl folder found in repository: {repo_path}", "Expected one of: Shared/BaseInputs/Scripts/pymtpl, Scripts/pymtpl/pymtpl, UserCode/pymtpl/pymtpl, UserCode/pymtpl, or BaseInputs/Scripts/[Pp]ymtpl")
        else:
            selected_usercode_pymtpl = pymtpl_folder

        confirm(isdir(selected_usercode_pymtpl), f"-e- Required folder not found: {selected_usercode_pymtpl}", "Please ensure the pymtpl folder exists in the repository")

        # Remove any .module_agent_* file and create new .module_agent_SHORTSHA file with commit_link
        module_agent_pattern = join(selected_usercode_pymtpl, ".module_agent_*")
        for oldfile in glob.glob(module_agent_pattern):
            try:
                os.remove(oldfile)
            except Exception as e:
                log.warning(f"-w- Warning: Could not delete {oldfile}: {e}")

        newfile = join(selected_usercode_pymtpl, f".module_agent_{short_sha}")
        with open(newfile, "w") as f:
            f.write(commit_link)
        log.info(f"-i- Created Module Agent version marker: .module_agent_{short_sha}")

        return selected_usercode_pymtpl

##############################################################
# endregion PyTPD Framework Update Class
##############################################################

##############################################################
# POR Methods Update Class
# region
##############################################################


class PORMethodsUpdater:
    """Class for updating por_methods.py in repositories."""

    @staticmethod
    def update_por_methods(repo_path, pymtpl_folder_path):
        """Generate and update por_methods.py using pymtpl genmethods."""
        scripts_pytpd_path = join(repo_path, "Scripts", "pytpd")

        # Construct the genmethods command
        genmethods_script = join(scripts_pytpd_path, "main", "pymtpl.py")

        # Get relative path from repo root for outdir
        relative_pymtpl_path = relpath(pymtpl_folder_path, repo_path)

        cmd = [
            sys.executable,
            genmethods_script,
            "-genmethods",
            "Shared\\Common\\Supersedes\\code,UserCode",
            "-genmethodsoutdir",
            f".\\.\\{relative_pymtpl_path}"
        ]

        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Parsing Prime dlls to create por_methods.py (this will take a moment)...")
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info(f"  Command: {' '.join(cmd)}\n")

        # Run the command from the repo root directory
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)

        confirm(result.returncode == 0, f"Error generating methods: {result.stderr}", "Check that Prime dlls are accessible")

        if result.stdout:
            for line in result.stdout.splitlines():
                log.info(f"  {line}")

        # Rename new_test_methods.py to por_methods.py
        new_methods_file = join(pymtpl_folder_path, "new_test_methods.py")
        por_methods_file = join(pymtpl_folder_path, "por_methods.py")

        confirm(exists(new_methods_file), f"Expected output file not found: {new_methods_file}", "The genmethods command may have failed")

        # Remove old por_methods.py if it exists
        if exists(por_methods_file):
            check_and_del(por_methods_file, error=False)

        # Rename new_test_methods.py to por_methods.py
        os.rename(new_methods_file, por_methods_file)
        log.info(f"-i- Successfully updated por_methods.py")

        return True

##############################################################
# endregion POR Methods Update Class
##############################################################

##############################################################
# Repository Validation Class
# region
##############################################################


class RepositoryValidator:
    """Class for validating repository state before updates."""

    @staticmethod
    def verify_current_dir_is_tp_repo():
        """Verify that the current directory is a TP repository."""
        current_dir = os.getcwd()

        sln_files = glob.glob(join(current_dir, "*.sln"))

        confirm(sln_files, "Current directory does not contain a .sln file", "Please run this script from the root of a TP repository")

        return current_dir

    @staticmethod
    def validate_repo_state(repo_path):
        """Validate that a repository exists, is a git repo, and has a clean working directory."""
        repo_name = basename(repo_path)

        confirm(exists(repo_path), f"{repo_name}: Repository path does not exist: {repo_path}", "Check the repository path is correct")
        confirm(LocalGitHelper.is_git_repo(repo_path), f"{repo_name}: Not a git repository: {repo_path}", "Ensure the path points to a valid git repository")
        confirm(LocalGitHelper.has_clean_working_directory(repo_path), f"{repo_name}: Working directory has uncommitted changes", "Please commit or stash your changes before running this script")

        log.info(f"-i- {repo_name}: Validation passed")
        log.info("-i- " + "-" * SEP_WIDTH)
        return True

##############################################################
# endregion Repository Validation Class
##############################################################

##############################################################
# Installation Class
# region
##############################################################


class PyMTPLInstaller:
    """Class for installing PyMTPL in a repository."""

    @staticmethod
    def prompt_product_class():
        """Prompt user to select the product class."""
        log.info("\n-i- Select the product class for this repository:")
        log.info("-i- 1. JGSClass (Sort-style HBSBxxxx binning)")
        log.info("-i- 2. CBRClass (Old style 90HBSBxxx binning)")
        log.info("-i- 3. TestChip (No bins, only counters)")
        log.info("-i- This can be changed later by editing the mtpl2py.bat file")

        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == "1":
                return "JGSClass"
            elif choice == "2":
                return "CBRClass"
            elif choice == "3":
                return "TestChip"
            else:
                log.error("Invalid choice. Please enter 1, 2, or 3.")

    @staticmethod
    def read_or_create_custom_command_json(repo_path):
        """Read existing CustomCommand.json or create a new structure."""
        custom_command_path = join(repo_path, "CustomCommand.json")

        if exists(custom_command_path):
            with open(custom_command_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"CustomCommands": []}

    @staticmethod
    def update_custom_command_json(repo_path, product_class):
        """Add or update PyMTPL commands in CustomCommand.json."""
        custom_command_data = PyMTPLInstaller.read_or_create_custom_command_json(repo_path)

        pymtpl_folder_absolute = RepositoryProcessor.get_pymtpl_folder(repo_path)
        confirm(pymtpl_folder_absolute, f"No pymtpl folder found in repository: {repo_path}", "Do you need to run -install first?")
        pymtpl_folder_relative = relpath(pymtpl_folder_absolute, repo_path)

        run_pymtpl_command = {
            "CommandName": "Run Pymtpl",
            "ScriptPath": join(pymtpl_folder_relative, "pymtpl.bat").replace("\\", "/"),
            "FileExtensions": [".py"],
            "Timeout": 30
        }

        create_pymtpl_command = {
            "CommandName": "Create PyMTPL from MTPL",
            "ScriptPath": join(pymtpl_folder_relative, "mtpl2py.bat").replace("\\", "/"),
            "FileExtensions": [".mtpl"],
            "Timeout": 30
        }

        commands = custom_command_data.get("Commands", [])

        run_pymtpl_exists = any("pymtpl" in cmd.get("CommandName").lower() for cmd in commands)
        if not run_pymtpl_exists:
            commands.append(run_pymtpl_command)
            log.info(f"-i- Added 'Run Pymtpl' command to CustomCommand.json")
        else:
            log.info(f"-i- 'Run Pymtpl' command already exists")

        create_pymtpl_exists = any("create pymtpl from mtpl" in cmd.get("CommandName").lower() for cmd in commands)
        if not create_pymtpl_exists:
            commands.append(create_pymtpl_command)
            log.info(f"-i- Added 'Create PyMTPL from MTPL' command to CustomCommand.json")
        else:
            log.info(f"-i- 'Create PyMTPL from MTPL' command already exists")

        custom_command_data["Commands"] = commands

        custom_command_path = join(repo_path, "CustomCommand.json")
        with open(custom_command_path, 'w', encoding='utf-8') as f:
            json.dump(custom_command_data, f, indent=2)

    @staticmethod
    def create_pymtpl_folder_structure(repo_path):
        """Create the pymtpl folder structure with __init__.py files."""
        # Create Scripts/pymtpl/pymtpl folder structure
        pymtpl_folder = join(repo_path, "Scripts", "pymtpl", "pymtpl")

        if exists(pymtpl_folder):
            log.info(f"-i- PyMTPL folder already exists: {pymtpl_folder}")
            return pymtpl_folder

        mkdirs(pymtpl_folder, mode="0o2770")

        init_file = join(pymtpl_folder, "__init__.py")
        with open(init_file, 'w') as f:
            f.write("# PyMTPL package initialization\n")

        parent_folder = dirname(pymtpl_folder)
        parent_init = join(parent_folder, "__init__.py")
        if not exists(parent_init):
            with open(parent_init, 'w') as f:
                f.write("# Package initialization\n")

        log.info(f"-i- Created pymtpl folder structure: {pymtpl_folder}")
        return pymtpl_folder

    @staticmethod
    def find_bdefs_file(repo_path):
        """Find the .bdefs file in the Shared folder."""
        shared_folder = join(repo_path, "Shared")
        if not exists(shared_folder):
            return None

        for root, dirs, files in os.walk(shared_folder):
            for file in files:
                if file.endswith('.bdefs'):
                    full_path = join(root, file)
                    relative_path = relpath(full_path, repo_path)
                    return relative_path.replace("\\", "/")

        return None

    @staticmethod
    def find_env_file(repo_path):
        """Find the first .env file in the POR_TP folder."""
        por_tp_folder = join(repo_path, "POR_TP")
        if not exists(por_tp_folder):
            return None

        for root, dirs, files in os.walk(por_tp_folder):
            for file in files:
                if file.endswith('.env'):
                    full_path = join(root, file)
                    relative_path = relpath(full_path, repo_path)
                    return relative_path.replace("\\", "/")

        return None

    @staticmethod
    def create_bat_files(repo_path, product_class, pymtpl_folder):
        """Create pymtpl.bat and mtpl2py.bat files with dynamic paths."""
        bdefs_path = PyMTPLInstaller.find_bdefs_file(repo_path)
        if not bdefs_path:
            log.warning(f"-w- Could not find .bdefs file in Shared folder")
            bdefs_path = "Shared/path/to/bindeffile.bdefs"

        env_path = PyMTPLInstaller.find_env_file(repo_path)
        if not env_path:
            log.warning(f"-w- Could not find .env file in POR_TP folder")
            env_path = "POR_TP/TestProgram/EnvironmentFile.env"

        pymtpl_bat_path = join(pymtpl_folder, "pymtpl.bat")
        pymtpl_bat_content = f"""@echo off
REM PyMTPL Execution Batch File
REM This file converts a .py to .mtpl using PyMTPL

python %1/Scripts/pytpd/main/pymtpl.py %3 -env %1/{env_path} -bindef %1/{bdefs_path}
"""

        with open(pymtpl_bat_path, 'w') as f:
            f.write(pymtpl_bat_content)

        log.info(f"-i- Created pymtpl.bat")

        mtpl2py_bat_path = join(pymtpl_folder, "mtpl2py.bat")
        mtpl2py_bat_content = f"""@echo off
REM MTPL to PyMTPL Conversion Batch File
REM This file converts MTPL files to PyMTPL format

python %1/Scripts/pytpd/main/pymtpl.py -genpy %3 -env %1/{env_path} -product {product_class}
"""

        with open(mtpl2py_bat_path, 'w') as f:
            f.write(mtpl2py_bat_content)

        log.info(f"-i- Created mtpl2py.bat")

    @staticmethod
    def install_pymtpl_in_repo(repo_path, pytpd_repo_path, module_agent_path, short_sha, commit_link, product_class, skip_por_methods):
        """Perform full PyMTPL installation in a repository."""
        repo_name = basename(repo_path)

        log.info("-i- " + "-" * SEP_WIDTH)
        log.info(f"-i- # Processing: {repo_name}")
        log.info("-i- " + "-" * SEP_WIDTH)

        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Installing PyMTPL")
        log.info("-i- " + "-" * SEP_WIDTH)

        pymtpl_folder = PyMTPLInstaller.create_pymtpl_folder_structure(repo_path)

        PyTPDFrameworkUpdater.copy_pytpd_framework(repo_path, pytpd_repo_path)
        PyTPDFrameworkUpdater.add_version_marker(repo_path, short_sha, commit_link, pymtpl_folder)

        PyMTPLInstaller.create_bat_files(repo_path, product_class, pymtpl_folder)

        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Updating CustomCommand.json")
        log.info("-i- " + "-" * SEP_WIDTH)
        PyMTPLInstaller.update_custom_command_json(repo_path, product_class)

        if not skip_por_methods:
            PORMethodsUpdater.update_por_methods(repo_path, pymtpl_folder)

        ModuleAgentInstructions.process_module_agent_for_repo(repo_path, module_agent_path)

        # Update product config instructions
        ModuleAgentInstructions.update_product_config_instructions(repo_path, product_class)

        # Copy GitHub skills from module-agent repo
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Updating Module Agent Skills")
        log.info("-i- " + "-" * SEP_WIDTH)
        ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        # Add Module Agent version marker
        module_agent_sha, module_agent_msg = LocalGitHelper.get_commit_info(module_agent_path)
        module_agent_link = f"https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.module-agent/commit/{module_agent_sha}"
        PyTPDFrameworkUpdater.add_module_agent_version_marker(repo_path, module_agent_sha, module_agent_link, pymtpl_folder)

        log.info(f"-i- Successfully installed PyMTPL in {repo_name}!")
        return True

##############################################################
# endregion Installation Class
##############################################################

##############################################################
# Repository Processing Class
# region
##############################################################


class RepositoryProcessor:
    """Class for orchestrating repository update operations."""

    # Cache for pymtpl folder locations
    _pymtpl_folder_cache = {}

    @staticmethod
    def update_repo_git_state(repo_path):
        """Pull latest changes from git for a repository."""
        return LocalGitHelper.pull_latest_changes(repo_path)

    @staticmethod
    def get_pymtpl_folder(repo_path):
        """Check for pymtpl folder in order of precedence and return the first one found."""
        # Check cache first
        if repo_path in RepositoryProcessor._pymtpl_folder_cache:
            return RepositoryProcessor._pymtpl_folder_cache[repo_path]

        # Check folders in order of precedence (exact paths)
        potential_folders = [
            join(repo_path, "Shared", "BaseInputs", "Scripts", "pymtpl"),
            join(repo_path, "Scripts", "pymtpl", "pymtpl"),
            join(repo_path, "UserCode", "pymtpl", "pymtpl"),
            join(repo_path, "UserCode", "pymtpl")
        ]

        # Also search for NVL common repo path with case-insensitive [Pp]ymtpl
        nvl_glob_pattern = join(repo_path, "BaseInputs", "Scripts", "[Pp]ymtpl")
        potential_folders += sorted(glob.glob(nvl_glob_pattern))

        for folder in potential_folders:
            if exists(folder):
                # Check if folder is empty (ignore empty folders)
                if os.listdir(folder):
                    # Cache the result
                    RepositoryProcessor._pymtpl_folder_cache[repo_path] = folder
                    return folder

        # If none exist or all are empty, return None
        return None

    @staticmethod
    def process_single_repo(repo_path, pytpd_repo_path, short_sha, commit_link,
                            module_agent_path, skip_por_methods):
        """Process a single repository for updates."""
        repo_name = basename(repo_path)

        log.info("-i- " + "-" * SEP_WIDTH)
        log.info(f"-i- # Processing: {repo_name}")
        log.info("-i- " + "-" * SEP_WIDTH)

        RepositoryProcessor.update_repo_git_state(repo_path)

        PyTPDFrameworkUpdater.copy_pytpd_framework(repo_path, pytpd_repo_path)
        PyTPDFrameworkUpdater.add_version_marker(repo_path, short_sha, commit_link)

        pymtpl_folder_path = RepositoryProcessor.get_pymtpl_folder(repo_path)
        confirm(pymtpl_folder_path, f"No pymtpl folder found in repository: {repo_path}", "Do you need to run -install first?")

        if not skip_por_methods:
            PORMethodsUpdater.update_por_methods(repo_path, pymtpl_folder_path)

        success = ModuleAgentInstructions.process_module_agent_for_repo(repo_path, module_agent_path)
        if not success:
            log.warning(f"-w- Warning: Failed to update Module Agent for {repo_name}")

        # Copy GitHub skills from module-agent repo
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Updating Module Agent Skills")
        log.info("-i- " + "-" * SEP_WIDTH)
        ModuleAgentSkills.copy_skills_folder(repo_path, module_agent_path)

        # Add Module Agent version marker
        module_agent_sha, module_agent_msg = LocalGitHelper.get_commit_info(module_agent_path)
        module_agent_link = f"https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.module-agent/commit/{module_agent_sha}"
        PyTPDFrameworkUpdater.add_module_agent_version_marker(repo_path, module_agent_sha, module_agent_link, pymtpl_folder_path)

##############################################################
# endregion Repository Processing Class
##############################################################

##############################################################
# Main Application Class
# region
##############################################################


class PyMTPLUpdater:
    """Main application class for orchestrating PyMTPL updates and installations."""

    def __init__(self):
        """Initialize the updater with parsed arguments."""
        self.pytpd_tempdir = None  # TempDir object
        self.module_agent_tempdir = None  # TempDir object

    def run_installation_mode(self, repo_path, skip_por_methods):
        """Run installation mode for a single repository."""
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- PyMTPL Installation Mode")
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info(f"-i- Installing PyMTPL in: {repo_path}")

        # Validate repository state before proceeding
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Validating Repository")
        log.info("-i- " + "-" * SEP_WIDTH)
        RepositoryValidator.validate_repo_state(repo_path)

        # Check if pymtpl is already installed
        existing_folder = RepositoryProcessor.get_pymtpl_folder(repo_path)
        confirm(not existing_folder, f"PyMTPL appears to be already installed at: {existing_folder}", "Please run without -install to update an existing installation")

        log.info(f"-i- Repository validation passed!")

        # Prompt for product class before cloning repos
        product_class = PyMTPLInstaller.prompt_product_class()

        self.module_agent_tempdir = RepositoryCloner.clone_module_agent_repo()
        confirm(self.module_agent_tempdir, "Failed to clone Module Agent repository", "Check network connectivity and repository access")

        self.pytpd_tempdir = RepositoryCloner.clone_pytpd_repo()
        confirm(self.pytpd_tempdir, "Failed to clone PyTPD repository", "Check network connectivity and repository access")

        short_sha, commit_msg = LocalGitHelper.get_commit_info(self.pytpd_tempdir.name())
        commit_link = f"https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd/commit/{short_sha}"

        return PyMTPLInstaller.install_pymtpl_in_repo(
            repo_path,
            self.pytpd_tempdir.name(),
            self.module_agent_tempdir.name(),
            short_sha,
            commit_link,
            product_class,
            skip_por_methods
        )

    def run_update_mode(self, repo_path, skip_por_methods):
        """Run update mode for the current repository."""
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- PyMTPL Update Mode")
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info(f"-i- Updating repository: {basename(repo_path)}")

        # Validate repository state before proceeding
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info("-i- Validating Repository")
        log.info("-i- " + "-" * SEP_WIDTH)
        RepositoryValidator.validate_repo_state(repo_path)

        log.info(f"-i- Repository validation passed!")

        self.module_agent_tempdir = RepositoryCloner.clone_module_agent_repo()
        confirm(self.module_agent_tempdir, "Failed to clone Module Agent repository", "Check network connectivity and repository access")

        self.pytpd_tempdir = RepositoryCloner.clone_pytpd_repo()
        confirm(self.pytpd_tempdir, "Failed to clone PyTPD repository", "Check network connectivity and repository access")

        short_sha, commit_msg = LocalGitHelper.get_commit_info(self.pytpd_tempdir.name())
        commit_link = f"https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd/commit/{short_sha}"

        log.info("-i- " + "-" * SEP_WIDTH)
        log.info(f"-i- PyTPD Version: {short_sha}")
        log.info("-i- " + "-" * SEP_WIDTH)
        log.info(f"-i- Commit Link: {commit_link}")

        RepositoryProcessor.process_single_repo(
            repo_path,
            self.pytpd_tempdir.name(),
            short_sha,
            commit_link,
            self.module_agent_tempdir.name(),
            skip_por_methods
        )

        return True

    def main(self, install=False, skip_por_methods=False):
        """Main execution method."""
        try:
            repo_path = RepositoryValidator.verify_current_dir_is_tp_repo()

            if skip_por_methods:
                log.info("-i- " + "-" * SEP_WIDTH)
                log.info("-i- por_methods.py Generation Skipped (-s flag enabled)")
                log.info("-i- " + "-" * SEP_WIDTH)

            if install:
                success = self.run_installation_mode(repo_path, skip_por_methods)
            else:
                success = self.run_update_mode(repo_path, skip_por_methods)

            if success:
                log.info("-i- " + "-" * SEP_WIDTH)
                log.info("-i- Script completed successfully!")
                log.info("-i- " + "-" * SEP_WIDTH)

        finally:
            # TempDir objects automatically clean up when closed
            log.info("-i- " + "-" * SEP_WIDTH)
            log.info("-i- Cleaning up temporary directories...")
            log.info("-i- " + "-" * SEP_WIDTH)

            if self.module_agent_tempdir:
                self.module_agent_tempdir.close()
                log.info(f"-i- Cleaned up Module Agent temporary directory")

            if self.pytpd_tempdir:
                self.pytpd_tempdir.close()
                log.info(f"-i- Cleaned up PyTPD temporary directory")

##############################################################
# endregion Main Application Class
##############################################################
