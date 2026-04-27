#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for path_updater
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock, MagicMock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog, OPT
from gadget.files import TempDir
from tp.testprogram import Env
from pymtpl.path_updater import *
from unittest.mock import patch, MagicMock
from os.path import normcase


class TestPythonPathUpdater(TestCase):
    """
    Test the PythonPathUpdater class and all functions
    """

    def setUp(self):
        PythonPathUpdater.DEBUGPRINT = True

    def tearDown(self):
        PythonPathUpdater.DEBUGPRINT = False

    # ---------------- _get_site_packages tests -----------------
    def test_get_site_packages_string(self):
        """_get_site_packages returns the string when site.getusersitepackages returns a string."""
        with patch('pymtpl.path_updater.site.getusersitepackages', return_value='/tmp/fake_site'):
            self.assertEqual(PythonPathUpdater._get_site_packages(), '/tmp/fake_site')

    def test_get_site_packages_list(self):
        """_get_site_packages returns last element when a list is returned."""
        with patch('pymtpl.path_updater.site.getusersitepackages', return_value=['/a', '/b']):
            self.assertEqual(PythonPathUpdater._get_site_packages(), '/b')

    def test_get_site_packages_empty_list(self):
        """_get_site_packages returns None for empty list."""
        with patch('pymtpl.path_updater.site.getusersitepackages', return_value=[]):
            self.assertIsNone(PythonPathUpdater._get_site_packages())

    def test_get_site_packages_exception(self):
        """_get_site_packages returns None if site.getusersitepackages raises."""
        PythonPathUpdater.DEBUGPRINT = False

        def raiser():
            raise RuntimeError('boom')
        with patch('pymtpl.path_updater.site.getusersitepackages', side_effect=raiser):
            self.assertIsNone(PythonPathUpdater._get_site_packages())

    # ---------------- _find_tp_repo_root tests -----------------
    @with_(TempDir, chdir=True)
    def test_find_tp_repo_root_already_in_root(self):
        """_find_tp_repo_root returns repository root when already there"""
        os.makedirs(os.path.join(os.getcwd(), '.git'))  # we need a git folder in the root to mark it as git
        File('PRODUCT.sln').touch('')  # a solution file to find
        found = PythonPathUpdater._find_tp_repo_root('func')
        expected = os.path.normpath(os.getcwd())
        self.assertEqual(os.path.normpath(found), expected)

    # ---------------- _find_git_root tests -----------------
    @with_(TempDir, chdir=True)
    def test_find_git_root_none(self):
        """_find_git_root returns None when no .git exists in any parent."""
        sub = os.path.join('a', 'b', 'c')
        os.makedirs(sub)
        self.assertIsNone(PythonPathUpdater._find_git_root(sub))

    @with_(TempDir, chdir=True)
    def test_find_git_root_simple(self):
        """_find_git_root returns root when .git is in parent folder"""
        sub = os.path.join('repo', 'subfolder')
        os.makedirs(os.path.join(os.getcwd(), 'repo', '.git'))
        os.makedirs(sub)
        found = PythonPathUpdater._find_git_root(sub)
        expected = os.path.normpath(os.path.join(os.getcwd(), 'repo'))
        self.assertEqual(os.path.normpath(found), expected)

    @with_(TempDir, chdir=True)
    def test_find_git_root_cwd(self):
        """_find_git_root returns cwd when .git is there and no parent"""
        os.makedirs(os.path.join(os.getcwd(), '.git'))
        found = PythonPathUpdater._find_git_root()
        expected = os.path.normpath(os.getcwd())
        self.assertEqual(os.path.normpath(found), expected)

    @with_(TempDir, chdir=True)
    def test_find_git_root_simple_repo(self):
        """_find_git_root returns repository root with .git dir even if submodule .git file deeper."""
        repo = 'repo'
        nested = os.path.join(repo, 'x', 'y')
        os.makedirs(nested)
        os.makedirs(os.path.join(repo, '.git'))
        with open(os.path.join(nested, '.git'), 'w') as f:
            f.write('gitdir: ../../.git/modules/sub')
        found = PythonPathUpdater._find_git_root(nested)
        expected = os.path.normpath(os.path.join(os.getcwd(), repo))
        self.assertEqual(os.path.normpath(found), expected)

    # ---------------- _extract_pymtpl_repo_root tests -----------------
    @with_(TempDir, chdir=True)
    def test_extract_repo_root_missing_customcommand(self):
        """Returns None when CustomCommand.json absent."""
        self.assertIsNone(PythonPathUpdater._extract_pymtpl_repo_root(os.getcwd(), 'func'))

    @with_(TempDir, chdir=True)
    def test_extract_repo_root_no_pymtpl_command(self):
        """Returns None when no command references pymtpl."""
        File('CustomCommand.json').touch('{"commands": [{"ScriptPath": "scripts/other_tool.bat"}]}')
        os.makedirs('scripts')
        File('scripts/other_tool.bat').touch('python something_else.py\n')
        self.assertIsNone(PythonPathUpdater._extract_pymtpl_repo_root(os.getcwd(), 'func'))

    @with_(TempDir, chdir=True)
    def test_extract_repo_root_missing_bat(self):
        """Returns None when referenced bat file missing."""
        File('CustomCommand.json').touch('{"commands": [{"ScriptPath": "scripts/launch_pymtpl.bat"}]}')
        # scripts dir exists but no bat file
        os.makedirs('scripts')
        self.assertIsNone(PythonPathUpdater._extract_pymtpl_repo_root(os.getcwd(), 'func'))

    @with_(TempDir, chdir=True)
    def test_extract_repo_root_parse_fail(self):
        """Returns None when bat exists but _parse_pymtpl_bat_for_repo_root yields None (no pymtpl.py line)."""
        os.makedirs('scripts')
        File('CustomCommand.json').touch('{"commands": [{"ScriptPath": "scripts/launch_pymtpl.bat"}]}')
        File('scripts/launch_pymtpl.bat').touch('@echo off\npython something_else.py\n')
        self.assertIsNone(PythonPathUpdater._extract_pymtpl_repo_root(os.getcwd(), 'func'))

    @with_(TempDir, chdir=True)
    def test_extract_repo_root_happy_path(self):
        """Returns resolved pymtpl repo root on valid CustomCommand + bat."""
        # create directory structure with pymtpl/main/pymtpl.py
        pymtpl_py = os.path.join('repo', 'pymtpl', 'main', 'pymtpl.py')
        os.makedirs(os.path.dirname(pymtpl_py))
        File(pymtpl_py).touch('')
        os.makedirs('scripts')
        File('CustomCommand.json').touch('{"commands": [{"ScriptPath": "scripts/launch_pymtpl.bat"}]}')
        abs_pymtpl_py = os.path.abspath(pymtpl_py)
        File('scripts/launch_pymtpl.bat').touch(f'@echo off\npython {abs_pymtpl_py} --foo\n')
        found = PythonPathUpdater._extract_pymtpl_repo_root(os.getcwd(), 'func')
        self.assertEqual(os.path.normpath(found), os.path.normpath(os.path.join(os.getcwd(), 'repo', 'pymtpl')))

    @with_(TempDir, chdir=True)
    def test_extract_repo_root_dummy_path(self):
        """Returns resolved pymtpl repo root on valid CustomCommand + bat."""
        # create directory structure with pymtpl/main/pymtpl.py
        File('CustomCommand.json').touch('{"commands": [{"ScriptPath": "scripts/launch_pymtpl.bat"}]}')
        with patch('pymtpl.path_updater.PythonPathUpdater._parse_pymtpl_bat_for_repo_root', lambda *a, **k: "dummy/path"):
            found = PythonPathUpdater._extract_pymtpl_repo_root(os.getcwd(), 'func')
            self.assertEqual(found, None)

    @with_(TempDir, chdir=True)
    def test_extract_repo_root_no_commands(self):
        """Returns None when commands.json doesn't have any commands that match"""
        File('CustomCommand.json').touch('{"commands": []}')
        self.assertIsNone(PythonPathUpdater._extract_pymtpl_repo_root(os.getcwd(), 'func'))

    # ---------------- _parse_pymtpl_bat_for_repo_root tests -----------------
    @with_(TempDir, chdir=True)
    def test_parse_pymtpl_bat_happy_path(self):
        """_parse_pymtpl_bat_for_repo_root returns directory two levels up from pymtpl.py path."""
        base = os.getcwd()
        pymtpl_py = os.path.join(base, 'repo', 'pymtpl', 'main', 'pymtpl.py')
        os.makedirs(os.path.dirname(pymtpl_py))
        # create an empty pymtpl.py just to be realistic (not required by parser)
        File(pymtpl_py).touch('')
        bat_path = os.path.join(base, 'launch_pymtpl.bat')
        # first line ignored (@), second line parsed (no quotes so parser tokenization is simple)
        File(bat_path).touch(f'@echo off\npython {pymtpl_py} --foo\n')
        repo_root = PythonPathUpdater._parse_pymtpl_bat_for_repo_root(bat_path, base)
        self.assertEqual(os.path.normpath(repo_root), os.path.normpath(os.path.join(base, 'repo', 'pymtpl')))

    @with_(TempDir, chdir=True)
    def test_parse_pymtpl_bat_no_match(self):
        """Returns None when no line contains pymtpl.py."""
        bat_path = 'launch.bat'
        File(bat_path).touch('echo nothing here\npython something_else.py\n')
        self.assertIsNone(PythonPathUpdater._parse_pymtpl_bat_for_repo_root(bat_path, ''))

    @with_(TempDir, chdir=True)
    def test_parse_pymtpl_bat_missing_file(self):
        """Returns None when .bat file does not exist (OSError)."""
        self.assertIsNone(PythonPathUpdater._parse_pymtpl_bat_for_repo_root('missing_launcher.bat', ''))

    @with_(TempDir, chdir=True)
    def test_parse_pymtpl_bat_short_line(self):
        """Returns None when a matching line lacks a second token (len(parts) < 2)."""
        bat_path = 'bad_launcher.bat'
        # Line contains pymtpl.py but only one token so should be ignored -> None
        File(bat_path).touch('pymtpl.py\n')
        self.assertIsNone(PythonPathUpdater._parse_pymtpl_bat_for_repo_root(bat_path, ''))

    @with_(TempDir, chdir=True)
    def test_parse_pymtpl_bat_ignores_comments(self):
        """Commented lines containing pymtpl.py are ignored; subsequent valid line used."""
        base = os.getcwd()
        pymtpl_py = os.path.join(base, 'r', 'pymtpl', 'main', 'pymtpl.py')
        os.makedirs(os.path.dirname(pymtpl_py))
        File(pymtpl_py).touch('')
        bat_path = os.path.join(base, 'lp.bat')
        content = f'# python {pymtpl_py}\n@ echo still ignored {pymtpl_py}\npython {pymtpl_py}\n'
        File(bat_path).touch(content)
        repo_root = PythonPathUpdater._parse_pymtpl_bat_for_repo_root(bat_path, base)
        self.assertEqual(os.path.normpath(repo_root), os.path.normpath(os.path.join(base, 'r', 'pymtpl')))

    @with_(TempDir, chdir=True)
    def test_parse_pymtpl_bat_vscommander_variable(self):
        """Handles %1 variable replacement in pymtpl.py path."""
        base = os.getcwd()
        pymtpl_py = os.path.join('%1', 'pymtpl', 'main', 'pymtpl.py')
        bat_path = os.path.join(base, 'launch_pymtpl.bat')
        File(bat_path).touch(f'python {pymtpl_py}\n')
        repo_root = os.path.join(base, 'repo_root')
        # Should replace %1 with repo_root and return repo_root/pymtpl
        expected = os.path.normpath(os.path.join(repo_root, 'pymtpl'))
        result = PythonPathUpdater._parse_pymtpl_bat_for_repo_root(bat_path, repo_root)
        self.assertEqual(os.path.normpath(result), expected)

    # ---------------- _discover_por_methods_folder tests -----------------
    @with_(TempDir, chdir=True)
    def test_discover_por_methods_none(self):
        """_discover_por_methods_folder returns None when no candidate directories exist."""
        repo_root = os.getcwd()
        self.assertIsNone(PythonPathUpdater._discover_por_methods_folder(repo_root, 'func'))

    @with_(TempDir, chdir=True)
    def test_discover_por_methods_single(self):
        """Returns parent of single pymtpl directory containing por_methods.py."""
        repo_root = os.getcwd()
        target_dir = os.path.join(repo_root, 'Shared', 'BaseInputs', 'Scripts', 'pymtpl')
        os.makedirs(target_dir)
        File(os.path.join(target_dir, 'por_methods.py')).touch('')
        found = PythonPathUpdater._discover_por_methods_folder(repo_root, 'func')
        self.assertEqual(os.path.normpath(found), normcase(os.path.normpath(os.path.join(repo_root, 'Shared', 'BaseInputs', 'Scripts'))))

    @with_(TempDir, chdir=True)
    def test_discover_por_methods_multiple(self):
        """Returns None when multiple candidate parents are found."""
        repo_root = os.getcwd()
        d1 = os.path.join(repo_root, 'Shared', 'BaseInputs', 'Scripts', 'pymtpl')
        d2 = os.path.join(repo_root, 'UserCode', 'pymtpl')
        os.makedirs(d1)
        os.makedirs(d2)
        File(os.path.join(d1, 'por_methods.py')).touch('')
        File(os.path.join(d2, 'por_methods.py')).touch('')
        self.assertIsNone(PythonPathUpdater._discover_por_methods_folder(repo_root, 'func'))

    @with_(TempDir, chdir=True)
    def test_discover_por_methods_single_wrongname(self):
        """fails due to directory containing por_methods.py not being named pymtpl"""
        repo_root = os.getcwd()
        target_dir = os.path.join(repo_root, 'Shared', 'BaseInputs', 'Scripts')  # note absence of pymtpl
        os.makedirs(target_dir)
        File(os.path.join(target_dir, 'por_methods.py')).touch('')
        found = PythonPathUpdater._discover_por_methods_folder(repo_root, 'func')
        self.assertEqual(found, None)

    @with_(TempDir, chdir=True)
    def test_discover_por_methods_duplicate_paths_deduplication(self):
        """Returns single parent when POR_METHOD_SEARCH_PATHS contains duplicates that resolve to same path."""
        repo_root = os.getcwd()
        target_dir = os.path.join(repo_root, 'Shared', 'BaseInputs', 'Scripts', 'pymtpl')
        os.makedirs(target_dir)
        File(os.path.join(target_dir, 'por_methods.py')).touch('')

        # Mock POR_METHOD_SEARCH_PATHS to have duplicate paths (with/without trailing slash, different case on Windows)
        duplicate_paths = [
            'Shared/BaseInputs/Scripts/pymtpl/por_methods.py',
            'Shared/BaseInputs/Scripts/pymtpl/por_methods.py',  # exact duplicate
            'Shared/BaseInputs/Scripts/pymtpl\\por_methods.py',  # backslash variant
        ]

        with patch('pymtpl.por_methods.POR_METHOD_SEARCH_PATHS', duplicate_paths):
            found = PythonPathUpdater._discover_por_methods_folder(repo_root, 'func')
            # Should deduplicate and return the single parent path
            expected = os.path.normpath(os.path.join(repo_root, 'Shared', 'BaseInputs', 'Scripts'))
            self.assertEqual(os.path.normpath(found), normcase(expected))

    # ---------------- write_python_paths_for_VS tests -----------------
    @with_(TempDir, chdir=True)
    def test_write_python_paths_skips_UT(self):
        """Skips writing when IS_UT is True (default in UT)."""
        PythonPathUpdater.write_python_paths_for_VS()

    @with_(TempDir, chdir=True)
    def test_write_python_paths_skips_when_no_git_root(self):
        """Skips (no .git => _find_git_root None) so no .pth created."""
        # Force IS_UT False so function proceeds
        with MockVar(__import__('pymtpl.path_updater', fromlist=['IS_UT']), 'IS_UT', False), \
                MockVar(PythonPathUpdater, '_find_git_root', lambda *_: None):
            PythonPathUpdater.write_python_paths_for_VS()
        # Nothing created
        for root, dirs, files in os.walk('.'):
            self.assertNotIn(PYMTPL_PTH_NAME, files)

    @with_(TempDir, chdir=True)
    def test_write_python_paths_skips_when_no_sln(self):
        """Skips when repo root lacks .sln file."""
        # make fake git root
        os.makedirs('.git')
        with MockVar(__import__('pymtpl.path_updater', fromlist=['IS_UT']), 'IS_UT', False), \
                MockVar(PythonPathUpdater, '_find_git_root', lambda *_: os.getcwd()):
            PythonPathUpdater.write_python_paths_for_VS()
        for root, dirs, files in os.walk('.'):
            self.assertNotIn(PYMTPL_PTH_NAME, files)

    @with_(TempDir, chdir=True)
    def test_write_python_paths_integration(self):
        """Creates pymtpl.pth with por_methods path then repo root path when all prerequisites satisfied (using lambdas returning temp dir)."""
        tdir = os.getcwd()
        site_pkg_dir = os.path.join(tdir, 'parent', 'site-packages')  # This path does not exist yet, we will verify it gets created
        with patch('pymtpl.path_updater.PythonPathUpdater._find_tp_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._get_site_packages', lambda *a, **k: site_pkg_dir), \
                patch('pymtpl.path_updater.PythonPathUpdater._extract_pymtpl_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._discover_por_methods_folder', lambda *a, **k: tdir), \
                MockVar(__import__('pymtpl.path_updater', fromlist=['IS_UT']), 'IS_UT', False):
            PythonPathUpdater.write_python_paths_for_VS()
        pth_path = os.path.join(site_pkg_dir, PYMTPL_PTH_NAME)
        self.assertTrue(os.path.exists(pth_path))
        expect = f'{tdir}\n{tdir}\n'
        self.assertTextEqual(normcase(File(pth_path).read()), normcase(expect))

    @with_(TempDir, chdir=True)
    def test_write_python_paths_integration_repeat(self):
        """Creates pymtpl.pth with por_methods path then repo root path when all prerequisites satisfied (using lambdas returning temp dir)."""
        tdir = os.getcwd()
        # create a dummy file to verify overwrite
        pth_path = os.path.join(tdir, PYMTPL_PTH_NAME)
        File(pth_path).touch('old content\n', mkdir=True)
        # Run twice to verify overwrite
        with patch('pymtpl.path_updater.PythonPathUpdater._find_tp_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._get_site_packages', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._extract_pymtpl_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._discover_por_methods_folder', lambda *a, **k: tdir), \
                MockVar(__import__('pymtpl.path_updater', fromlist=['IS_UT']), 'IS_UT', False):
            PythonPathUpdater.write_python_paths_for_VS()
            PythonPathUpdater.write_python_paths_for_VS()
            PythonPathUpdater.write_python_paths_for_VS()
        self.assertTrue(os.path.exists(pth_path))
        expect = f'{tdir}\n{tdir}\n'
        self.assertTextEqual(normcase(File(pth_path).read()), normcase(expect))

    @with_(TempDir, chdir=True)
    def test_write_python_paths_skips_when_no_site_packages(self):
        """Check that we end gracefully when site packages returns none"""
        tdir = os.getcwd()
        with patch('pymtpl.path_updater.PythonPathUpdater._find_tp_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._get_site_packages', lambda *a, **k: None), \
                MockVar(__import__('pymtpl.path_updater', fromlist=['IS_UT']), 'IS_UT', False):
            PythonPathUpdater.write_python_paths_for_VS()
        for files in os.walk('.'):
            self.assertNotIn(PYMTPL_PTH_NAME, files)

    @with_(TempDir, chdir=True)
    def test_write_python_paths_skips_when_no_pymtpl_root(self):
        """Check that we end gracefully when site packages returns none"""
        tdir = os.getcwd()
        with patch('pymtpl.path_updater.PythonPathUpdater._find_tp_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._get_site_packages', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._extract_pymtpl_repo_root', lambda *a, **k: None), \
                MockVar(__import__('pymtpl.path_updater', fromlist=['IS_UT']), 'IS_UT', False):
            PythonPathUpdater.write_python_paths_for_VS()
        for files in os.walk('.'):
            self.assertNotIn(PYMTPL_PTH_NAME, files)

    @with_(TempDir, chdir=True)
    def test_write_python_paths_skips_when_no_por_methods_folder(self):
        """Check that we end gracefully when site packages returns none"""
        tdir = os.getcwd()
        with patch('pymtpl.path_updater.PythonPathUpdater._find_tp_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._get_site_packages', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._extract_pymtpl_repo_root', lambda *a, **k: tdir), \
                patch('pymtpl.path_updater.PythonPathUpdater._discover_por_methods_folder', lambda *a, **k: None), \
                MockVar(__import__('pymtpl.path_updater', fromlist=['IS_UT']), 'IS_UT', False):
            PythonPathUpdater.write_python_paths_for_VS()
        for files in os.walk('.'):
            self.assertNotIn(PYMTPL_PTH_NAME, files)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
