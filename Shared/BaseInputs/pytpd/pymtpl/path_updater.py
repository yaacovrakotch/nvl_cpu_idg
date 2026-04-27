"""Lightweight Python path updater separated from helpers to avoid circular imports."""
import glob
import os
import site
from pathlib import Path
from gadget.files import File
from gadget.pylog import log
from gadget.tputil import JsonRead
from gadget.helperclass import IS_UT
from gadget.disk import mkdirs

# used for adding to the python path to get visual studio to recognize pymtpl
PYMTPL_PTH_NAME = "pymtpl.pth"


class PythonPathUpdater:
    """
    Updates the Python path for Visual Studio so that pymtpl objects can be inspected and source can be tracked down

    Attributes:
        DEBUGPRINT (bool): if True, enables debug print statements
    """

    #: whether to print debug messages
    DEBUGPRINT = False

    @classmethod
    def disp(cls, message):
        if cls.DEBUGPRINT:
            log.info(message)

    @classmethod
    def write_python_paths_for_VS(cls):
        """
        Write the Python paths for Visual Studio to user site packages file
        """

        if IS_UT:    # unittests does not call this function except explicitly
            return

        # saving the name of this function so we can exit out cleanly with why
        funcname = "write_python_paths_for_VS"

        # print out the current directory which will be a module directory like repo/Modules/PTH_PWR
        cls.disp(f'-i- Current directory: {os.getcwd()}')

        # get the repo root
        repo_root = cls._find_tp_repo_root(funcname, os.getcwd())
        if repo_root is None:
            log.info(f'-i- No git root found from {os.getcwd()}, skipping {funcname}.')
            return

        cls.disp(f'-i- Repository root directory: {repo_root}')

        # determine site-packages directory
        site_packages = cls._get_site_packages()
        if not site_packages:
            log.info(f'-i- Unable to determine site-packages directory, skipping {funcname}.')
            return

        # extract the pymtpl repo root (may early-return). Keep logic isolated for readability.
        pymtpl_repo_root = cls._extract_pymtpl_repo_root(repo_root, funcname)
        if not pymtpl_repo_root:  # helper already logged reason
            return

        # lines to write to the file
        pth_lines = []

        # discover por_methods location (ensures exactly one)
        por_methods_folder = cls._discover_por_methods_folder(repo_root, funcname)
        if not por_methods_folder:
            return
        pth_lines.append(os.path.abspath(os.path.normcase(por_methods_folder)))

        # append the repo root because you want to import por_methods locally first, then the rest of pymtpl. (abs/norm here to ensure maximum compatibility)
        pth_lines.append(os.path.abspath(os.path.normcase(pymtpl_repo_root)))

        # get the path to a .pth file in site-packages
        pth_file_path = os.path.join(site_packages, PYMTPL_PTH_NAME)

        # using this format to evaluate whether to write to file or not
        mkdirs(os.path.dirname(pth_file_path))
        File(pth_file_path).rewrite('\n'.join(pth_lines), 'PyMTPL Path Updater')

    @classmethod
    def _extract_pymtpl_repo_root(cls, repo_root, funcname):
        """Internal helper for write_python_paths_for_VS.

        Responsibilities:
        * Validate presence of CustomCommand.json in repo_root
        * Load and parse to locate first command whose ScriptPath references pymtpl
        * Resolve the corresponding .bat path and parse it to locate the path to pymtpl.py
        * Return the inferred pymtpl repository root path (directory containing the pymtpl package)

        Returns: absolute path to pymtpl repo root or None (on any validation / discovery failure)
        """
        # find the CustomCommand.json file in the repo_root directory and confirm it exists
        if not any(fname.endswith('CustomCommand.json') for fname in os.listdir(repo_root)):
            log.info(f'-i- No CustomCommand.json file found in {repo_root}, skipping {funcname}.')
            return None

        # load in CustomCommand.json and (optionally) log its contents
        custom_commands_path = os.path.join(repo_root, 'CustomCommand.json')
        custom_commands = JsonRead(custom_commands_path, suggestion=f"Please check json file structure {custom_commands_path}").load()
        cls.disp(f'-i- Custom commands: {custom_commands}')

        # Support both lower/upper-case key naming conventions
        commands_list = (custom_commands.get('commands') or custom_commands.get('Commands') or [])

        # Find first script path that references pymtpl
        script_path = None
        for cmd in commands_list:
            for key in ('scriptPath', 'ScriptPath'):
                if key in cmd and 'pymtpl' in str(cmd[key]).lower():
                    script_path = cmd[key]
                    break
            if script_path is not None:
                break

        if script_path is None:
            log.info(f'-i- No command found with ScriptPath containing "pymtpl" in {custom_commands_path}, skipping {funcname}.')
            return None

        script_path = os.path.normpath(script_path)  # normalize leading ./ etc.
        full_script_path = os.path.join(repo_root, script_path)
        cls.disp(f'-i- found pymtpl bat file: {full_script_path}')

        pymtpl_repo_root = cls._parse_pymtpl_bat_for_repo_root(full_script_path, repo_root)
        if pymtpl_repo_root is None:
            log.info(f'-i- Could not determine pymtpl repo root from bat file {full_script_path}. Skipping {funcname}.')
            return None

        if not (pymtpl_repo_root and os.path.exists(pymtpl_repo_root)):
            log.info(f'-i- Expected pymtpl repo root not found: {pymtpl_repo_root}. Skipping {funcname}.')
            return None

        return pymtpl_repo_root

    @classmethod
    def _parse_pymtpl_bat_for_repo_root(cls, full_script_path, repo_root):
        """Parse a launcher .bat file to discover the pymtpl repository root.

        Strategy:
        - Iterate non-comment lines until one containing 'pymtpl.py' is found
        - Assume the token immediately following the interpreter (2nd token) is the path to pymtpl.py
        - Return the directory two levels above that file (repo_root/pymtpl/main/pymtpl.py => pymtpl_repo_root)

        Returns absolute path string or None.
        """
        pymtpl_repo_root = None
        try:
            with open(full_script_path, 'r') as f:
                for raw in f:
                    line = raw.strip('\n')
                    if line.startswith('#') or line.startswith('@'):
                        continue
                    cls.disp(f'-i- {line}')
                    if 'pymtpl.py' not in line:
                        continue
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    pymtpl_path = parts[1].strip()
                    cls.disp(f'-i- Found pymtpl.py path: {pymtpl_path}')
                    pymtpl_repo_root = os.path.dirname(os.path.dirname(pymtpl_path))
                    cls.disp(f'-i- Found pymtpl repo path: {pymtpl_repo_root}')
                    break
        except OSError as e:
            cls.disp(f'-i- Failed reading bat file {full_script_path}: {e}')
            return None

        # replace when necessary
        pymtpl_repo_root = cls._replace_vscommander_variable(pymtpl_repo_root, repo_root)

        return pymtpl_repo_root

    @classmethod
    def _replace_vscommander_variable(cls, pymtpl_repo_root, repo_root):
        """ in CustomCommander, %1 is the repo root, so we need to do a find and replace for the pymtpl_repo_root """
        if pymtpl_repo_root is not None and '%1' in pymtpl_repo_root:
            pymtpl_repo_root = pymtpl_repo_root.replace('%1', repo_root)
            pymtpl_repo_root = os.path.abspath(os.path.normpath(pymtpl_repo_root))
        return pymtpl_repo_root

    @classmethod
    def _get_site_packages(cls):
        """Return the user site-packages directory handling list/tuple return types.

        Uses site.getusersitepackages() instead of sysconfig purelib (historically caused issues).
        Returns: absolute path string or None on failure.
        """
        try:
            _user_site_val = site.getusersitepackages()
        except Exception as e:
            cls.disp(f'-i- Failed to get user site-packages: {e}')
            return None
        if isinstance(_user_site_val, (list, tuple)):
            if not _user_site_val:
                cls.disp('-i- Empty user site-packages list returned')
                return None
            site_packages = _user_site_val[-1]
        else:
            site_packages = _user_site_val
        cls.disp(f'-i- Site packages directory: {site_packages}')
        return site_packages

    @classmethod
    def _discover_por_methods_folder(cls, repo_root, funcname):
        """Find and validate the single expected por_methods search root.

        Logic mirrors previous inline block:
          * Iterate POR_METHOD_SEARCH_PATHS wildcards
          * Collect unique normalized parent directories (one level above a 'pymtpl' directory containing por_methods.py)
          * Require exactly one; otherwise log and return None.

        Returns absolute normalized path or None.
        """
        from pymtpl.por_methods import POR_METHOD_SEARCH_PATHS  # local import to avoid side-effects at module import
        candidates = []
        seen = set()
        for wild in POR_METHOD_SEARCH_PATHS:
            for match in glob.glob(os.path.join(repo_root, wild)):
                abs_dir = os.path.dirname(os.path.abspath(match))
                norm = abs_dir.rstrip('\\/')
                if not os.path.isdir(abs_dir):
                    continue
                if not os.path.exists(os.path.join(abs_dir, 'por_methods.py')):
                    continue
                # If directory itself is named pymtpl, rise one level (repo layout variant)
                if os.path.basename(norm).lower() == 'pymtpl':
                    norm_parent = os.path.dirname(os.path.abspath(norm))
                else:
                    cls.disp(f"-i- Found por_methods.py but not in a directory called pymtpl. Can't load pymtpl module from directory {norm}")
                    continue  # Not a pymtpl directory; skip
                key = norm_parent.lower()
                if key not in seen:
                    candidates.append(os.path.abspath(os.path.normcase(norm_parent)))
                    seen.add(key)
        if len(candidates) != 1:
            log.info(f'-i- Expected exactly one por_methods path to be found! Instead we found {candidates}. Skipping {funcname}.')
            return None

        cls.disp(f'-i- por_methods folder resolved to: {candidates[0]}')
        return candidates[0]

    @classmethod
    def _find_tp_repo_root(cls, funcname, start_path=None):
        """
        Find the root directory of the TP repository based on git folders and the .sln file
        """
        if start_path is None:
            start_path = os.getcwd()

        # get the directory based on git
        tp_root = cls._find_git_root(start_path)
        if tp_root is None:
            log.info(f'-i- No git root found from {start_path}, skipping {funcname}.')
            return None

        cls.disp(f'-i- Repository root directory: {tp_root}')

        # verify that repo_root has a file ending in .sln in it and fail if not
        if not (any(fname.endswith('.sln') for fname in os.listdir(tp_root))):
            log.info(f'-i- No .sln file found in {tp_root}, skipping {funcname}.')
            return None

        return tp_root

    @classmethod
    def _find_git_root(cls, start_path=None):
        """
        Find the root directory of a git repository. Goes up parents. Accounts for submodules.
        """
        if start_path is None:
            start_path = os.getcwd()

        current_path = Path(start_path).resolve()
        git_roots = []

        # First, collect all git roots from current path up to filesystem root
        while current_path != current_path.parent:
            git_path = current_path / '.git'

            if git_path.exists():
                # Regular git repository (.git is a directory) or submodule (.git is a file)
                git_roots.append(current_path)

            current_path = current_path.parent

        if not git_roots:
            return None

        # Return the topmost (main repository) root
        return str(git_roots[-1])
