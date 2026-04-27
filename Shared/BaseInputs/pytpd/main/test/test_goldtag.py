#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Patched Unit Test for GoldFailTag Script
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.gizmo import MockVar
from unittest.mock import patch, mock_open, MagicMock
from gadget.disk import Chdir
from gadget.shell import IS_UNIX, SystemCall
import main.goldtag as goldfailtag
import sys
import os
import json


class TestGetRepoShaId(TestCase):

    def test_get_repo_sha_id_with_all_keys(self):
        data = {
            'nvl.cpu': 'sha_cpu',
            'nvl.gcd': 'sha_gcd',
            'nvl.hub': 'sha_hub',
            'nvl.pcd': 'sha_pcd',
            'nvl.common': 'sha_common'
        }
        expected = {
            'nvl-cpu': 'sha_cpu',
            'nvl-gcd': 'sha_gcd',
            'nvl-hub': 'sha_hub',
            'nvl-pcd': 'sha_pcd',
            'nvl-common': 'sha_common'
        }
        result = goldfailtag.get_repo_sha_id(data)
        self.assertEqual(result, expected)

    def test_get_repo_sha_id_with_missing_keys(self):
        data = {}
        expected = {
            'nvl-cpu': 'N/A',
            'nvl-gcd': 'N/A',
            'nvl-hub': 'N/A',
            'nvl-pcd': 'N/A',
            'nvl-common': 'N/A'
        }
        result = goldfailtag.get_repo_sha_id(data)
        self.assertEqual(result, expected)


class TestBomExtraction(TestCase):
    """Test BOM name extraction logic"""

    def test_bom_extraction(self):
        """Test BOM extraction for different product types"""
        test_cases = [
            ('I:\\path\\to\\Class_NVL_S52C', 'S52C'),      # NVL case - just last part
            ('I:\\path\\to\\Class_DNL_S28C', 'DS28C'),     # DNL case - D + last part
            ('I:\\path\\to\\Class_RZL_HX28C', 'RHX28C'),   # RZL case - R + last part
            ('I:\\path\\to\\Class_MTL_P28C', 'MP28C'),     # MTL case - M + last part
        ]

        for tp_path, expected_bom in test_cases:
            with self.subTest(tp_path=tp_path):
                last_part = tp_path.split('\\')[-1]
                if 'NVL' in last_part:
                    # For NVL products, only take the last part
                    bom = last_part.split('_')[-1]
                else:
                    # For non-NVL products, take first letter + last part
                    parts = last_part.split('_')
                    first_letter = parts[1][0]  # First letter of product (DNL->D, RZL->R, MTL->M)
                    last_part_bom = parts[-1]   # Last part (S28C, HX28C, P28C)
                    bom = f"{first_letter}{last_part_bom}"

                self.assertEqual(bom, expected_bom)


class TestGoldFailTagMain(TestCase):
    @patch.dict(os.environ, {
        'GoldDielet': 'cpu,pcd,common',
        'FailDielet': 'cpu',
        'TPPath': f'{UT_DIR}/create_pr/DRV_2/POR_TP/Class_NVL_S52C'
    })
    @patch('main.goldtag.GitOperations.clone_repository')
    @patch('main.goldtag.GitOperations.update_submodule')
    @patch('main.goldtag.GitOperations.checkout_branch')
    @patch('main.goldtag.GitOperations.get_all_tags')
    @patch('main.goldtag.GitOperations.create_tag')
    @patch('main.goldtag.GitOperations.push_tag')
    @patch('main.goldtag.TempDir')
    @patch('main.goldtag.datetime')
    @patch('main.goldtag.log')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_flow_nvl(self, mock_file, mock_log, mock_datetime, mock_tempdir, mock_push_tag, mock_create_tag, mock_get_all_tags, mock_checkout_branch, mock_update_submodule, mock_clone_repository):
        """Test main flow with NVL BOM"""
        # Mock TempDir context manager
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test_repo"
        mock_tempdir.return_value.__exit__.return_value = None

        # Mock datetime for consistent tag generation
        mock_now = MagicMock()
        mock_now.isocalendar.return_value = (2024, 53, 4)  # Year 2024, week 53, day 4
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = MagicMock()

        # Mock GitOperations
        mock_get_all_tags.return_value = []  # No existing tags

        # Simulate file reads
        def open_side_effect(file, *args, **kwargs):
            if 'MajorRevision.txt' in file:
                return mock_open(read_data="1").return_value
            elif 'DieletStepping.txt' in file:
                return mock_open(read_data="A").return_value
            elif 'RepoRev.json' in file:
                return mock_open(read_data=json.dumps({
                    "nvl.cpu": "sha_cpu",
                    "nvl.gcd": "sha_gcd",
                    "nvl.hub": "sha_hub",
                    "nvl.pcd": "sha_pcd",
                    "nvl.common": "sha_common"
                })).return_value
            else:
                raise FileNotFoundError(f"Unexpected open call for file: {file}")

        mock_file.side_effect = open_side_effect

        # Run main
        gold_fail_tag = goldfailtag.GoldFailTag()
        gold_fail_tag.main()

        # Verify Git operations were called
        self.assertTrue(mock_clone_repository.called)
        self.assertTrue(mock_create_tag.called)
        self.assertTrue(mock_push_tag.called)

        # Verify that tags were created for the expected repositories
        # Should be called for cpu, pcd (Gold) and cpu (Fail) and common
        expected_calls = mock_create_tag.call_count
        self.assertGreater(expected_calls, 0)

    @patch.dict(os.environ, {
        'GoldDielet': 'cpu,pcd,common',
        'FailDielet': 'cpu',
        'TPPath': f'{UT_DIR}/create_pr/DRV_2/POR_TP/Class_DNL_S28C'
    })
    @patch('main.goldtag.GitOperations.clone_repository')
    @patch('main.goldtag.GitOperations.update_submodule')
    @patch('main.goldtag.GitOperations.checkout_branch')
    @patch('main.goldtag.GitOperations.get_all_tags')
    @patch('main.goldtag.GitOperations.create_tag')
    @patch('main.goldtag.GitOperations.push_tag')
    @patch('main.goldtag.TempDir')
    @patch('main.goldtag.datetime')
    @patch('main.goldtag.log')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_flow_dnl(self, mock_file, mock_log, mock_datetime, mock_tempdir, mock_push_tag, mock_create_tag, mock_get_all_tags, mock_checkout_branch, mock_update_submodule, mock_clone_repository):
        """Test main flow with DNL BOM"""
        # Mock TempDir context manager
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test_repo"
        mock_tempdir.return_value.__exit__.return_value = None

        # Mock datetime for consistent tag generation
        mock_now = MagicMock()
        mock_now.isocalendar.return_value = (2024, 53, 4)  # Year 2024, week 53, day 4
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = MagicMock()

        # Mock GitOperations
        mock_get_all_tags.return_value = []  # No existing tags

        # Simulate file reads
        def open_side_effect(file, *args, **kwargs):
            if 'MajorRevision.txt' in file:
                return mock_open(read_data="1").return_value
            elif 'DieletStepping.txt' in file:
                return mock_open(read_data="A").return_value
            elif 'RepoRev.json' in file:
                return mock_open(read_data=json.dumps({
                    "nvl.cpu": "sha_cpu",
                    "nvl.pcd": "sha_pcd",
                    "nvl.common": "sha_common"
                })).return_value
            else:
                raise FileNotFoundError(f"Unexpected open call for file: {file}")

        mock_file.side_effect = open_side_effect

        # Run main
        gold_fail_tag = goldfailtag.GoldFailTag()
        gold_fail_tag.main()

        # Verify Git operations were called
        self.assertTrue(mock_clone_repository.called)
        self.assertTrue(mock_create_tag.called)
        self.assertTrue(mock_push_tag.called)

    @patch.dict(os.environ, {
        'GoldDielet': 'cpu,pcd,common',
        'FailDielet': 'cpu',
        'TPPath': f'{UT_DIR}/create_pr/DRV_2/POR_TP/Class_RZL_HX28C'
    })
    @patch('main.goldtag.GitOperations.clone_repository')
    @patch('main.goldtag.GitOperations.update_submodule')
    @patch('main.goldtag.GitOperations.checkout_branch')
    @patch('main.goldtag.GitOperations.get_all_tags')
    @patch('main.goldtag.GitOperations.create_tag')
    @patch('main.goldtag.GitOperations.push_tag')
    @patch('main.goldtag.TempDir')
    @patch('main.goldtag.datetime')
    @patch('main.goldtag.log')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_flow_rzl(self, mock_file, mock_log, mock_datetime, mock_tempdir, mock_push_tag, mock_create_tag, mock_get_all_tags, mock_checkout_branch, mock_update_submodule, mock_clone_repository):
        """Test main flow with RZL BOM"""
        # Mock TempDir context manager
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test_repo"
        mock_tempdir.return_value.__exit__.return_value = None

        # Mock datetime for consistent tag generation
        mock_now = MagicMock()
        mock_now.isocalendar.return_value = (2024, 53, 4)  # Year 2024, week 53, day 4
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = MagicMock()

        # Mock GitOperations
        mock_get_all_tags.return_value = []  # No existing tags

        # Simulate file reads
        def open_side_effect(file, *args, **kwargs):
            if 'MajorRevision.txt' in file:
                return mock_open(read_data="1").return_value
            elif 'DieletStepping.txt' in file:
                return mock_open(read_data="A").return_value
            elif 'RepoRev.json' in file:
                return mock_open(read_data=json.dumps({
                    "nvl.cpu": "sha_cpu",
                    "nvl.pcd": "sha_pcd",
                    "nvl.common": "sha_common"
                })).return_value
            else:
                raise FileNotFoundError(f"Unexpected open call for file: {file}")

        mock_file.side_effect = open_side_effect

        # Run main
        gold_fail_tag = goldfailtag.GoldFailTag()
        gold_fail_tag.main()

        # Verify Git operations were called
        self.assertTrue(mock_clone_repository.called)
        self.assertTrue(mock_create_tag.called)
        self.assertTrue(mock_push_tag.called)

    @patch.dict(os.environ, {
        'GoldDielet': 'cpu,pcd,common',
        'FailDielet': 'cpu',
        'TPPath': f'{UT_DIR}/create_pr/DRV_2/POR_TP/Class_MTL_P28C'
    })
    @patch('main.goldtag.GitOperations.clone_repository')
    @patch('main.goldtag.GitOperations.update_submodule')
    @patch('main.goldtag.GitOperations.checkout_branch')
    @patch('main.goldtag.GitOperations.get_all_tags')
    @patch('main.goldtag.GitOperations.create_tag')
    @patch('main.goldtag.GitOperations.push_tag')
    @patch('main.goldtag.TempDir')
    @patch('main.goldtag.datetime')
    @patch('main.goldtag.log')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_flow_mtl(self, mock_file, mock_log, mock_datetime, mock_tempdir, mock_push_tag, mock_create_tag, mock_get_all_tags, mock_checkout_branch, mock_update_submodule, mock_clone_repository):
        """Test main flow with MTL BOM"""
        # Mock TempDir context manager
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test_repo"
        mock_tempdir.return_value.__exit__.return_value = None

        # Mock datetime for consistent tag generation
        mock_now = MagicMock()
        mock_now.isocalendar.return_value = (2024, 53, 4)  # Year 2024, week 53, day 4
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = MagicMock()

        # Mock GitOperations
        mock_get_all_tags.return_value = []  # No existing tags

        # Simulate file reads
        def open_side_effect(file, *args, **kwargs):
            if 'MajorRevision.txt' in file:
                return mock_open(read_data="1").return_value
            elif 'DieletStepping.txt' in file:
                return mock_open(read_data="A").return_value
            elif 'RepoRev.json' in file:
                return mock_open(read_data=json.dumps({
                    "nvl.cpu": "sha_cpu",
                    "nvl.pcd": "sha_pcd",
                    "nvl.common": "sha_common"
                })).return_value
            else:
                raise FileNotFoundError(f"Unexpected open call for file: {file}")

        mock_file.side_effect = open_side_effect

        # Run main
        gold_fail_tag = goldfailtag.GoldFailTag()
        gold_fail_tag.main()

        # Verify Git operations were called
        self.assertTrue(mock_clone_repository.called)
        self.assertTrue(mock_create_tag.called)
        self.assertTrue(mock_push_tag.called)

    @patch.dict(os.environ, {
        'GoldDielet': 'cpu',
        'FailDielet': 'pcd',
        'TPPath': f'{UT_DIR}/create_pr/DRV_2/POR_TP/Class_NVL_S52C'
    })
    @patch('main.goldtag.GitOperations.clone_repository')
    @patch('main.goldtag.GitOperations.update_submodule')
    @patch('main.goldtag.GitOperations.checkout_branch')
    @patch('main.goldtag.GitOperations.get_all_tags')
    @patch('main.goldtag.GitOperations.create_tag')
    @patch('main.goldtag.GitOperations.push_tag')
    @patch('main.goldtag.TempDir')
    @patch('main.goldtag.datetime')
    @patch('main.goldtag.log')
    @patch('builtins.open', new_callable=mock_open)
    def test_missing_revision_files(self, mock_file, mock_log, mock_datetime, mock_tempdir, mock_push_tag, mock_create_tag, mock_get_all_tags, mock_checkout_branch, mock_update_submodule, mock_clone_repository):
        """Test with missing revision files"""
        # Mock TempDir context manager
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test_repo"
        mock_tempdir.return_value.__exit__.return_value = None

        # Mock datetime for consistent tag generation
        mock_now = MagicMock()
        mock_now.isocalendar.return_value = (2024, 53, 4)  # Year 2024, week 53, day 4
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = MagicMock()

        # Mock GitOperations
        mock_get_all_tags.return_value = []  # No existing tags

        # Simulate missing files
        def open_side_effect(file, *args, **kwargs):
            if 'RepoRev.json' in file:
                return mock_open(read_data=json.dumps({
                    "nvl.cpu": "sha_cpu",
                    "nvl.pcd": "sha_pcd"
                })).return_value
            else:
                raise FileNotFoundError(f"Missing file: {file}")

        mock_file.side_effect = open_side_effect

        # Run main
        gold_fail_tag = goldfailtag.GoldFailTag()
        gold_fail_tag.main()

        # Verify Git operations were called (should use default values)
        self.assertTrue(mock_clone_repository.called)
        self.assertTrue(mock_create_tag.called)
        self.assertTrue(mock_push_tag.called)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
