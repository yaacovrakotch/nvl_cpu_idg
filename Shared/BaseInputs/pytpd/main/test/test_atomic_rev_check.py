#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit tests for atomic_rev_check.py

Tests cover the pure matrix-building static methods and the full consistency
check logic using in-memory JSON data that mirrors the real main.json structure.
No file I/O or GitHub API calls are made.
"""
from setenv_unittest import ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest
from main.atomic_rev_check import AtomicConsistencyChecker
from gadget.errors import ErrorUser
from unittest.mock import patch
from gadget.shell import SystemCall
import json
import os

# ---------------------------------------------------------------------------
# In-memory JSON matching the real main.json structure (11-bit bitmasks).
# JSON key insertion order = merge order (not PR-number order), matching the
# real file where e.g. nvl.hub PR 1568 merged before PR 1548.
# ---------------------------------------------------------------------------
SAMPLE_JSON = {
    "latest": "5.1.11000000000",
    "nvl.hub": {
        "15": ["1.0.11000000000"],
        "1295": ["2.0.11111111111"],
        "1322": ["3.0.11111111111"],
        "1387": ["3.1.00000011100"],
        "1504": ["3.4.10100000000", "3.5.00000010100"],
        "1543": ["4.0.11111111111"],
        "1568": ["5.0.11111111111"],
        "1548": ["5.1.11000000000"],
    },
    "nvl.cpu": {
        "151": ["1.0.11000000000"],
        "2422": ["2.0.11111111111"],
        "2442": ["3.0.11111111111", "3.1.00000011100"],
        "2895": ["3.4.10100000000"],
        "2850": ["3.5.00000010100"],
        "2972": ["4.0.11111111111"],
        "3008": ["5.0.11111111111", "5.1.11000000000"],
    },
    "nvl.pcd": {
        "15": ["1.0.11000000000"],
        "1392": ["2.0.11111111111"],
        "1414": ["3.0.11111111111", "3.1.00000011100"],
        "1660": ["3.4.10100000000", "3.5.00000010100"],
        "1701": ["4.0.11111111111"],
        "1713": ["5.0.11111111111", "5.1.11000000000"],
    },
    "nvl.gcd": {
        "15": ["1.0.11000000000"],
        "1095": ["2.0.11111111111"],
        "1116": ["3.0.11111111111", "3.1.00000011100"],
        "1276": ["3.4.10100000000"],
        "1285": ["3.5.00000010100"],
        "1306": ["4.0.11111111111"],
        "1318": ["5.0.11111111111", "5.1.11000000000"],
    },
    "nvl.common": {
        "15": ["1.0.11000000000"],
        "1605": ["2.0.11111111111"],
        "1645": ["3.0.11111111111"],
        "1681": ["3.1.00000011100"],
        "2021": ["3.4.10100000000"],
        "1954": ["3.5.00000010100"],
        "2079": ["4.0.11111111111"],
        "2116": ["5.0.11111111111"],
        "2082": ["5.1.11000000000"],
    },
}

BIT_S28C = 0    # NVL_S28C  -> bitmask index 0
BIT_AX16C = 10  # NVL_AX16C -> bitmask index 10


def _make_repo_info(cutoffs):
    # Helper: build a repo_info dict from {repo: inherited_atomic_pr}
    return {
        repo: {
            'sha': 'abc123',
            'pr': pr,
            'status': 'merged',
            'atomic_rev': '1.0',
            'atomic_bom': 'All_BOM',
            'inherited_atomic_pr': pr,
        }
        for repo, pr in cutoffs.items()
    }


class TestBuildGlobalTimeline(TestCase):

    def test_timeline_sorted_chronologically(self):
        # Verify every (major, minor) pair is in ascending order
        timeline = AtomicConsistencyChecker._build_global_timeline(SAMPLE_JSON)
        versions = [(maj, mn) for maj, mn, _ in timeline]
        self.assertEqual(versions, sorted(versions))

    def test_timeline_correct_length(self):
        # SAMPLE_JSON has exactly 9 unique version events
        timeline = AtomicConsistencyChecker._build_global_timeline(SAMPLE_JSON)
        self.assertEqual(len(timeline), 9)

    def test_timeline_bitmask_values(self):
        # Verify known version bitmasks are extracted correctly
        timeline = AtomicConsistencyChecker._build_global_timeline(SAMPLE_JSON)
        by_ver = {(maj, mn): bm for maj, mn, bm in timeline}
        self.assertEqual(by_ver[(1, 0)], '11000000000')
        self.assertEqual(by_ver[(3, 1)], '00000011100')
        self.assertEqual(by_ver[(3, 4)], '10100000000')
        self.assertEqual(by_ver[(5, 1)], '11000000000')
        self.assertEqual(by_ver[(4, 0)], '11111111111')

    def test_timeline_ignores_latest_key(self):
        # 'latest' key must never contribute version events
        data = {'latest': '3.0.11111111111', 'nvl.common': {'100': ['3.0.11111111111']}}
        timeline = AtomicConsistencyChecker._build_global_timeline(data)
        self.assertEqual(len(timeline), 1)

    def test_timeline_deduplicates_across_repos(self):
        # Same version appearing in multiple repos must produce only one timeline entry
        data = {
            'nvl.common': {'1': ['2.0.11111111111']},
            'nvl.cpu': {'2': ['2.0.11111111111']},
        }
        timeline = AtomicConsistencyChecker._build_global_timeline(data)
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0], (2, 0, '11111111111'))


class TestBuildRepoMatrix(TestCase):

    def _timeline(self):
        # Build timeline once for reuse in all matrix tests
        return AtomicConsistencyChecker._build_global_timeline(SAMPLE_JSON)

    def test_common_pinned_at_cutoff_version_s28c(self):
        # nvl.common contributes to every version — bit 0 must be pinned at 3.4 when cutoff=2021
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.common': 2021}
        )
        self.assertEqual(state['nvl.common'][BIT_S28C], {(3, 4)})

    def test_hub_skip_when_future_5_1_not_yet_landed(self):
        # hub contributed 5.1 via PR 1548, which comes AFTER PR 1568 in merge order
        # cutoff=1568 means 5.1 is SKIP — bit 0 stays at last PIN which is 5.0
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.hub': 1568}
        )
        self.assertEqual(state['nvl.hub'][BIT_S28C], {(5, 0)})

    def test_hub_pin_when_5_1_landed(self):
        # hub at cutoff=1548 (5.1 is the cutoff PR itself) — bit 0 must PIN at 5.1
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.hub': 1548}
        )
        self.assertEqual(state['nvl.hub'][BIT_S28C], {(5, 1)})

    def test_cpu_add_for_never_contributed_5_1(self):
        # cpu never has 5.1 as a first-entry (bundled as second entry in PR 3008)
        # so 5.1 is ADD regardless of cutoff — bit 0 must contain both 5.0 and 5.1
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.cpu': 3008}
        )
        self.assertIn((5, 0), state['nvl.cpu'][BIT_S28C])
        self.assertIn((5, 1), state['nvl.cpu'][BIT_S28C])

    def test_pcd_before_3_4_misses_s28c_anchor(self):
        # pcd cutoff=1414 means 3.4 is SKIP (future) — bit 0 stuck at 3.0 plus 5.1 ADD
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.pcd': 1414}
        )
        self.assertIn((3, 0), state['nvl.pcd'][BIT_S28C])
        self.assertIn((5, 1), state['nvl.pcd'][BIT_S28C])
        self.assertNotIn((3, 4), state['nvl.pcd'][BIT_S28C])
        self.assertNotIn((5, 0), state['nvl.pcd'][BIT_S28C])

    def test_gcd_bit_ax16c_always_compatible(self):
        # AX16C (bit 10) is never touched by partial uprevs — gcd always stays at last all-BOM version
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.gcd': 1276}
        )
        # At cutoff 1276 gcd has seen 1.0(no bit10), 2.0(PIN), 3.0(PIN), 3.4(PIN, but bit10=0)
        # bit 10 (AX16C): 2.0→PIN, 3.0→PIN, 4.0→SKIP, 5.0→SKIP → {(3,0)}
        self.assertEqual(state['nvl.gcd'][BIT_AX16C], {(3, 0)})

    def test_add_suppressed_for_cross_branch_version(self):
        # Simulates the real-world bug: nvl.pcd is on branch 'main' where 5.1 was introduced
        # exclusively in 'main_atomic_automation'.  pcd's native version set stops at 5.0.
        # Without repo_native_versions, (5,1) would be ADD-compatible for pcd (wrong).
        # With repo_native_versions provided, ADD is suppressed for (5,1) because it is
        # absent from pcd's native set.
        pcd_native = {(1, 0), (2, 0), (3, 0), (3, 1), (3, 4), (3, 5), (4, 0), (5, 0)}
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.pcd': 1414},
            repo_native_versions={'nvl.pcd': pcd_native}
        )
        # 3.0 is PIN (first-entry for cutoff PR 1414) → must remain in set
        self.assertIn((3, 0), state['nvl.pcd'][BIT_S28C])
        # 5.1 is ADD-candidate but NOT in pcd's native set → must be suppressed
        self.assertNotIn((5, 1), state['nvl.pcd'][BIT_S28C])

    def test_add_still_works_when_native_set_includes_version(self):
        # When a version IS in the repo's native set, ADD still fires normally.
        # Use same pcd cutoff but include 5.1 in the native set.
        pcd_native = {(1, 0), (2, 0), (3, 0), (3, 1), (3, 4), (3, 5), (4, 0), (5, 0), (5, 1)}
        state = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.pcd': 1414},
            repo_native_versions={'nvl.pcd': pcd_native}
        )
        # 5.1 is ADD-candidate AND in native set → must be present
        self.assertIn((5, 1), state['nvl.pcd'][BIT_S28C])

    def test_add_unchanged_when_repo_native_versions_is_none(self):
        # Backward-compatibility: repo_native_versions=None (default) must behave
        # identically to the old code — ADD is never suppressed.
        state_no_native = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.pcd': 1414}
        )
        state_none = AtomicConsistencyChecker._build_repo_matrix(
            SAMPLE_JSON, self._timeline(), {'nvl.pcd': 1414},
            repo_native_versions=None
        )
        self.assertEqual(state_no_native['nvl.pcd'][BIT_S28C], state_none['nvl.pcd'][BIT_S28C])
        self.assertIn((5, 1), state_none['nvl.pcd'][BIT_S28C])


class TestCheckAtomicConsistency(TestCase):

    def _make_checker(self, bom_name, cutoffs):
        # Build a checker instance and populate repo_info
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.bom_name = bom_name
        checker.branch_name = 'main'
        checker.errors = []
        checker.repo_info = _make_repo_info(cutoffs)
        return checker

    def _run(self, checker):
        # Monkey-patch _read_atomic_json on the instance to return in-memory data
        checker._read_atomic_json = lambda branch: SAMPLE_JSON
        return checker._check_atomic_consistency(checker.repo_info, checker.bom_name)

    def test_scenario1_pcd_behind_anchor_fails(self):
        # Anchor(common)=3.4, gcd at 1276 passes (3.4 compatible), pcd at 1414 fails (3.0, missing 3.4)
        checker = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2021,
            'nvl.gcd': 1276,
            'nvl.pcd': 1414,
        })
        self.assertFalse(self._run(checker))
        self.assertTrue(any('nvl.pcd' in e for e in checker.errors))

    def test_scenario2_gcd_ahead_of_anchor_fails(self):
        # gcd at 1318 gives bit 0 = {(5,0)}, anchor is (3,4) — 3.4 not in set → FAIL
        checker = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2021,
            'nvl.gcd': 1318,
            'nvl.pcd': 1414,
        })
        self.assertFalse(self._run(checker))

    def test_scenario3_ax16c_all_repos_pass(self):
        # AX16C (bit 10) not touched by partial uprevs — all repos at (3,0) → PASS
        checker = self._make_checker('Class_NVL_AX16C', {
            'nvl.common': 2021,
            'nvl.gcd': 1276,
            'nvl.pcd': 1414,
        })
        self.assertTrue(self._run(checker))
        self.assertEqual(checker.errors, [])

    def test_s28c_pcd_catches_up_passes(self):
        # pcd at 1660 means 3.4 has landed — all repos now consistent for S28C
        checker = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2021,
            'nvl.gcd': 1276,
            'nvl.pcd': 1660,
        })
        self.assertTrue(self._run(checker))
        self.assertEqual(checker.errors, [])

    def test_hub_before_5_1_fails_s28c(self):
        # hub cutoff=1568 (before 1548 in merge order) means 5.1 is SKIP for hub
        # hub bit 0 = {(5,0)}, anchor (5,1) not in set → FAIL
        checker = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2082,
            'nvl.hub': 1568,
        })
        self.assertFalse(self._run(checker))
        self.assertTrue(any('nvl.hub' in e for e in checker.errors))

    def test_hub_at_5_1_passes_s28c(self):
        # hub cutoff=1548 (5.1 landed) — hub bit 0 = {(5,1)}, anchor (5,1) matches → PASS
        checker = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2082,
            'nvl.hub': 1548,
        })
        self.assertTrue(self._run(checker))
        self.assertEqual(checker.errors, [])

    def test_invalid_bom_name_returns_false(self):
        # BOM name not in BOM_MAPPING must return False and record an error
        checker = self._make_checker('Class_NVL_UNKNOWN_BOM', {
            'nvl.common': 2021,
        })
        self.assertFalse(self._run(checker))
        self.assertTrue(any('BOM_MAPPING' in e for e in checker.errors))

    def test_class_prefix_stripped_correctly(self):
        # 'Class_NVL_S28C' and 'NVL_S28C' must resolve identically
        checker_with = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2021,
            'nvl.pcd': 1660,
        })
        checker_without = self._make_checker('NVL_S28C', {
            'nvl.common': 2021,
            'nvl.pcd': 1660,
        })
        result_with = self._run(checker_with)
        result_without = self._run(checker_without)
        self.assertEqual(result_with, result_without)

    def test_json_load_failure_returns_false(self):
        # _read_atomic_json returns None → 'Could not load atomic JSON' error → False
        checker = self._make_checker('Class_NVL_S28C', {'nvl.common': 2021})
        checker._read_atomic_json = lambda branch: None
        result = checker._check_atomic_consistency(checker.repo_info, checker.bom_name)
        self.assertFalse(result)
        self.assertTrue(any('atomic JSON' in e for e in checker.errors))

    def test_nvl_common_missing_inherited_pr_returns_false(self):
        # nvl.common inherited_atomic_pr=None → not in repo_cutoffs → returns False
        checker = self._make_checker('Class_NVL_S28C', {'nvl.pcd': 1660})
        info = _make_repo_info({'nvl.common': 2021, 'nvl.pcd': 1660})
        info['nvl.common']['inherited_atomic_pr'] = None
        checker.repo_info = info
        checker._read_atomic_json = lambda branch: SAMPLE_JSON
        result = checker._check_atomic_consistency(checker.repo_info, checker.bom_name)
        self.assertFalse(result)
        self.assertTrue(any('nvl.common not resolvable' in e for e in checker.errors))

    def test_nvl_common_no_cell_for_bom_returns_false(self):
        # nvl.common at cutoff=15 has no S28C_BLLC (bit 2) contributions → common_cell None → False
        checker = self._make_checker('Class_NVL_S28C_BLLC', {'nvl.common': 15})
        checker._read_atomic_json = lambda branch: SAMPLE_JSON
        result = checker._check_atomic_consistency(checker.repo_info, checker.bom_name)
        self.assertFalse(result)
        self.assertTrue(any('nvl.common has no data' in e for e in checker.errors))

    def test_repo_with_no_cell_for_bom_is_skipped(self):
        # nvl.cpu has no S28C_BLLC (bit 2) coverage in its native set → silently skipped → PASS
        mini_json = {
            'nvl.common': {'100': ['2.0.11100000000'], '200': ['3.0.11100000000']},
            'nvl.cpu': {'150': ['2.5.11000000000']},
        }
        checker = self._make_checker('Class_NVL_S28C_BLLC', {'nvl.common': 200, 'nvl.cpu': 150})
        checker._read_atomic_json = lambda branch: mini_json
        result = checker._check_atomic_consistency(checker.repo_info, checker.bom_name)
        self.assertTrue(result)
        self.assertEqual(checker.errors, [])

    def test_cpu_compatible_with_anchor_passes(self):
        # nvl.cpu at cutoff=3008 has {(5,0),(5,1)} for S28C via ADD — anchor (5,1) in set → PASS
        checker = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2082,
            'nvl.cpu': 3008,
        })
        self.assertTrue(self._run(checker))
        self.assertEqual(checker.errors, [])

    def test_scenario2_gcd_error_recorded(self):
        # gcd ahead of anchor → error message must reference nvl.gcd
        checker = self._make_checker('Class_NVL_S28C', {
            'nvl.common': 2021,
            'nvl.gcd': 1318,
            'nvl.pcd': 1414,
        })
        self.assertFalse(self._run(checker))
        self.assertTrue(any('nvl.gcd' in e for e in checker.errors))


class TestDiscoverBranchFromSha(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance for testing discovery methods
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.branch_name = 'main'
        checker.errors = []
        return checker

    def test_discover_returns_pr_and_branch(self):
        # REST API (attempt 1) succeeds: returns PR number, base branch, and is_merged
        mock_response = json.dumps([{"number": 42, "base": {"ref": "main_feature"}, "merged_at": "2026-01-01T00:00:00Z"}])
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, mock_response)):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('abc123', 'nvl.common')
            self.assertEqual(pr, 42)
            self.assertEqual(branch, 'main_feature')
            self.assertTrue(is_merged)

    def test_discover_returns_main_branch(self):
        # REST API (attempt 1) returns main-branch PR
        mock_response = json.dumps([{"number": 100, "base": {"ref": "main"}, "merged_at": "2026-01-01T00:00:00Z"}])
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, mock_response)):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('def456', 'nvl.cpu')
            self.assertEqual(pr, 100)
            self.assertEqual(branch, 'main')
            self.assertTrue(is_merged)

    def test_discover_no_pr_found_both_searches_empty(self):
        # REST API empty, sha: search also empty -> (None, None, False)
        empty_api = json.dumps([])
        empty_search = json.dumps([])
        with patch.object(SystemCall, 'run_outtxt', side_effect=[
            (0, empty_api),     # attempt 1: commits/pulls REST API
            (0, empty_search),  # attempt 2: sha: search
        ]):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('deadbeef', 'nvl.hub')
            self.assertIsNone(pr)
            self.assertIsNone(branch)
            self.assertFalse(is_merged)

    def test_discover_command_failure_first_then_second_fails(self):
        # commits/pulls REST API fails, sha: search also fails -> (None, None, False)
        with patch.object(SystemCall, 'run_outtxt', side_effect=[
            (1, ''),  # attempt 1: commits/pulls REST API fails
            (1, ''),  # attempt 2: sha: search fails
        ]):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('xyz789', 'nvl.gcd')
            self.assertIsNone(pr)
            self.assertIsNone(branch)
            self.assertFalse(is_merged)

    def test_discover_missing_base_ref_key(self):
        # REST API response with no 'base' key → PR number returned but branch is None
        mock_response = json.dumps([{"number": 55, "merged_at": None}])
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, mock_response)):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('aaa111', 'nvl.pcd')
            self.assertEqual(pr, 55)
            self.assertIsNone(branch)
            self.assertFalse(is_merged)

    def test_discover_multiple_results_uses_first(self):
        # REST API returns multiple PRs; first result is used
        mock_response = json.dumps([
            {"number": 10, "base": {"ref": "main_a"}, "merged_at": "2026-01-01T00:00:00Z"},
            {"number": 20, "base": {"ref": "main_b"}, "merged_at": "2026-01-01T00:00:00Z"}
        ])
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, mock_response)):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('bbb222', 'nvl.common')
            self.assertEqual(pr, 10)
            self.assertEqual(branch, 'main_a')
            self.assertTrue(is_merged)

    def test_discover_merge_commit_found_via_commits_pulls_api(self):
        # commits/pulls REST API (attempt 1) succeeds directly
        api_response = json.dumps([{"number": 77, "base": {"ref": "main"}, "merged_at": "2026-01-01T00:00:00Z"}])
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, api_response)):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('mergecomm1234', 'nvl.common')
            self.assertEqual(pr, 77)
            self.assertEqual(branch, 'main')
            self.assertTrue(is_merged)

    def test_discover_merge_commit_both_searches_fail(self):
        # commits/pulls REST API empty, sha: search also empty -> (None, None, False)
        empty = json.dumps([])
        with patch.object(SystemCall, 'run_outtxt', side_effect=[
            (0, empty),  # attempt 1: commits/pulls REST API
            (0, empty),  # attempt 2: sha: search
        ]):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('mergecomm5678', 'nvl.cpu')
            self.assertIsNone(pr)
            self.assertIsNone(branch)
            self.assertFalse(is_merged)

    def test_discover_sha_search_fallback_finds_pr(self):
        # commits/pulls REST API empty; gh pr list --search sha: fallback succeeds
        empty_api = json.dumps([])
        search_response = json.dumps([{"number": 99, "baseRefName": "main"}])
        with patch.object(SystemCall, 'run_outtxt', side_effect=[
            (0, empty_api),        # attempt 1: commits/pulls REST API returns empty
            (0, search_response),  # attempt 2: sha: search finds the PR
        ]):
            checker = self._make_checker()
            pr, branch, is_merged = checker._discover_branch_from_sha('abc123full', 'nvl.common')
            self.assertEqual(pr, 99)
            self.assertEqual(branch, 'main')
            self.assertTrue(is_merged)


class TestGhCmd(TestCase):

    def test_gh_cmd_returns_string(self):
        # _gh_cmd must return a non-empty string
        result = AtomicConsistencyChecker._gh_cmd()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestResolveBranchName(TestCase):

    def _make_checker_no_init(self):
        # Bypass __init__ so _resolve_branch_name can be called in isolation
        return AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)

    def test_returns_base_ref_when_git_branch_matches(self):
        # BASE_REF=main and git branch=main → returns 'main'
        with patch.dict('os.environ', {'BASE_REF': 'main'}):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'main\n')):
                checker = self._make_checker_no_init()
                result = checker._resolve_branch_name()
                self.assertEqual(result, 'main')

    def test_falls_back_to_base_ref_on_git_failure(self):
        # git command fails → falls back to BASE_REF value
        with patch.dict('os.environ', {'BASE_REF': 'main'}):
            with patch.object(SystemCall, 'run_outtxt', return_value=(1, '')):
                checker = self._make_checker_no_init()
                result = checker._resolve_branch_name()
                self.assertEqual(result, 'main')

    def test_falls_back_to_base_ref_on_empty_git_output(self):
        # git returns exit 0 but empty output → falls back to BASE_REF
        with patch.dict('os.environ', {'BASE_REF': 'develop'}):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, '')):
                checker = self._make_checker_no_init()
                result = checker._resolve_branch_name()
                self.assertEqual(result, 'develop')

    def test_feature_branch_with_json_returns_git_branch(self):
        # main_feature branch + matching JSON exists → returns the git branch name
        with patch.dict('os.environ', {'BASE_REF': 'main'}):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'main_feature\n')):
                with patch('main.atomic_rev_check.Env.xpath', return_value='/some/path/main_feature.json'):
                    with patch('os.path.exists', return_value=True):
                        checker = self._make_checker_no_init()
                        result = checker._resolve_branch_name()
                        self.assertEqual(result, 'main_feature')

    def test_feature_branch_without_json_exits(self):
        # main_feature branch + no matching JSON file → sys.exit(1)
        with patch.dict('os.environ', {'BASE_REF': 'main'}):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'main_feature\n')):
                with patch('main.atomic_rev_check.Env.xpath', return_value='/some/path/main_feature.json'):
                    with patch('os.path.exists', return_value=False):
                        checker = self._make_checker_no_init()
                        with self.assertRaises(SystemExit):
                            checker._resolve_branch_name()

    def test_non_feature_branch_returns_base_ref(self):
        # git branch 'hotfix' does not start with BASE_REF prefix → returns BASE_REF
        with patch.dict('os.environ', {'BASE_REF': 'main'}):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'hotfix\n')):
                checker = self._make_checker_no_init()
                result = checker._resolve_branch_name()
                self.assertEqual(result, 'main')


class TestGetSelfRepoName(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance bypassing __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.errors = []
        return checker

    def test_parses_https_url_with_git_suffix(self):
        # HTTPS remote URL ending in .git → extracts repo name without .git
        with patch.object(SystemCall, 'run_outtxt',
                          return_value=(0, 'https://github.com/intel-restricted/nvl.hub.git\n')):
            checker = self._make_checker()
            result = checker._get_self_repo_name()
            self.assertEqual(result, 'nvl.hub')

    def test_parses_https_url_without_git_suffix(self):
        # HTTPS URL without .git suffix is parsed correctly
        with patch.object(SystemCall, 'run_outtxt',
                          return_value=(0, 'https://github.com/intel-restricted/nvl.common\n')):
            checker = self._make_checker()
            result = checker._get_self_repo_name()
            self.assertEqual(result, 'nvl.common')

    def test_parses_ssh_url(self):
        # SSH-style remote URL is parsed correctly
        with patch.object(SystemCall, 'run_outtxt',
                          return_value=(0, 'git@github.com:intel-restricted/nvl.cpu.git\n')):
            checker = self._make_checker()
            result = checker._get_self_repo_name()
            self.assertEqual(result, 'nvl.cpu')

    def test_falls_back_to_cwd_basename_on_git_failure(self):
        # git command fails → returns basename of the current working directory
        with patch.object(SystemCall, 'run_outtxt', return_value=(1, '')):
            with patch('os.getcwd', return_value='/some/path/nvl.pcd'):
                checker = self._make_checker()
                result = checker._get_self_repo_name()
                self.assertEqual(result, 'nvl.pcd')

    def test_falls_back_to_cwd_basename_on_empty_url(self):
        # git exits 0 but empty output → falls back to cwd basename
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, '')):
            with patch('os.getcwd', return_value='/runner/nvl.gcd'):
                checker = self._make_checker()
                result = checker._get_self_repo_name()
                self.assertEqual(result, 'nvl.gcd')


class TestGetGitSha(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance bypassing __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.errors = []
        return checker

    def test_returns_sha_on_success(self):
        # git rev-parse succeeds → returns stripped SHA string
        with patch('main.atomic_rev_check.Chdir'):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'abc123def456\n')):
                checker = self._make_checker()
                result = checker._get_git_sha('.')
                self.assertEqual(result, 'abc123def456')

    def test_returns_none_on_git_failure(self):
        # git command exits non-zero → returns None
        with patch('main.atomic_rev_check.Chdir'):
            with patch.object(SystemCall, 'run_outtxt', return_value=(1, '')):
                checker = self._make_checker()
                result = checker._get_git_sha('.')
                self.assertIsNone(result)

    def test_returns_none_on_empty_output(self):
        # git exits 0 but empty output → returns None
        with patch('main.atomic_rev_check.Chdir'):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, '')):
                checker = self._make_checker()
                result = checker._get_git_sha('.')
                self.assertIsNone(result)


class TestGetGitBranch(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance bypassing __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.errors = []
        return checker

    def test_returns_branch_name_on_success(self):
        # git rev-parse returns branch name → returned directly
        with patch('main.atomic_rev_check.Chdir'):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'main_feature\n')):
                checker = self._make_checker()
                result = checker._get_git_branch('.')
                self.assertEqual(result, 'main_feature')

    def test_falls_back_to_main_on_git_failure(self):
        # git command fails → returns 'main' as fallback
        with patch('main.atomic_rev_check.Chdir'):
            with patch.object(SystemCall, 'run_outtxt', return_value=(1, '')):
                checker = self._make_checker()
                result = checker._get_git_branch('.')
                self.assertEqual(result, 'main')

    def test_falls_back_to_main_on_detached_head(self):
        # git returns 'HEAD' (detached HEAD state) → returns 'main'
        with patch('main.atomic_rev_check.Chdir'):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'HEAD\n')):
                checker = self._make_checker()
                result = checker._get_git_branch('.')
                self.assertEqual(result, 'main')

    def test_returns_main_branch_correctly(self):
        # git returns 'main' exactly → returned as-is (not treated as HEAD)
        with patch('main.atomic_rev_check.Chdir'):
            with patch.object(SystemCall, 'run_outtxt', return_value=(0, 'main\n')):
                checker = self._make_checker()
                result = checker._get_git_branch('.')
                self.assertEqual(result, 'main')


class TestGetReposToCheck(TestCase):

    def _make_checker(self):
        # Build a checker instance that bypasses __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.bom_name = 'Class_NVL_S28C'
        checker.branch_name = 'main'
        checker.self_repo_name = None
        checker.repo_info = {}
        checker.errors = []
        return checker

    def test_common_repo_includes_dielets_from_env(self):
        # nvl.common workflow: CPU_Branch and HUB_Branch set, GCD/PCD absent → only cpu + hub included
        checker = self._make_checker()
        with patch.object(checker, '_get_self_repo_name', return_value='nvl.common'):
            with patch.dict('os.environ', {'CPU_Branch': 'main', 'HUB_Branch': 'main',
                                           'GCD_Branch': '', 'PCD_Branch': ''}):
                def isdir_se(p):
                    if '_work' in p:
                        return False
                    return True
                with patch('os.path.isdir', side_effect=isdir_se):
                    result = checker._get_repos_to_check()
                    self.assertIn('nvl.common', result)
                    self.assertIn('nvl.cpu', result)
                    self.assertIn('nvl.hub', result)
                    self.assertNotIn('nvl.gcd', result)
                    self.assertNotIn('nvl.pcd', result)

    def test_common_repo_skips_dielet_with_none_branch(self):
        # Dielet with env var set to 'none' (case-insensitive) must be excluded
        checker = self._make_checker()
        with patch.object(checker, '_get_self_repo_name', return_value='nvl.common'):
            with patch.dict('os.environ', {'CPU_Branch': 'None', 'HUB_Branch': '',
                                           'GCD_Branch': '', 'PCD_Branch': ''}):
                with patch('os.path.isdir', return_value=False):
                    result = checker._get_repos_to_check()
                    self.assertIn('nvl.common', result)
                    self.assertNotIn('nvl.cpu', result)

    def test_common_repo_excludes_dielet_dir_not_found(self):
        # Dielet env var set but directory does not exist → excluded
        checker = self._make_checker()
        with patch.object(checker, '_get_self_repo_name', return_value='nvl.common'):
            with patch.dict('os.environ', {'CPU_Branch': 'main', 'HUB_Branch': '',
                                           'GCD_Branch': '', 'PCD_Branch': ''}):
                with patch('os.path.isdir', return_value=False):
                    result = checker._get_repos_to_check()
                    self.assertIn('nvl.common', result)
                    self.assertNotIn('nvl.cpu', result)

    def test_dielet_repo_with_shared_dir_includes_common(self):
        # Dielet workflow: Shared/ directory present → nvl.common added at 'Shared'
        checker = self._make_checker()
        with patch.object(checker, '_get_self_repo_name', return_value='nvl.cpu'):
            with patch('os.path.isdir', side_effect=lambda p: p == 'Shared'):
                result = checker._get_repos_to_check()
                self.assertIn('nvl.cpu', result)
                self.assertIn('nvl.common', result)
                self.assertEqual(result['nvl.common'], 'Shared')

    def test_dielet_repo_without_shared_dir_omits_common(self):
        # Dielet workflow: no Shared/ directory → nvl.common not added
        checker = self._make_checker()
        with patch.object(checker, '_get_self_repo_name', return_value='nvl.hub'):
            with patch('os.path.isdir', return_value=False):
                result = checker._get_repos_to_check()
                self.assertIn('nvl.hub', result)
                self.assertNotIn('nvl.common', result)

    def test_self_repo_name_is_recorded(self):
        # _get_repos_to_check must set self.self_repo_name
        checker = self._make_checker()
        with patch.object(checker, '_get_self_repo_name', return_value='nvl.pcd'):
            with patch('os.path.isdir', return_value=False):
                checker._get_repos_to_check()
                self.assertEqual(checker.self_repo_name, 'nvl.pcd')


class TestGetPrFromSha(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance bypassing __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.branch_name = 'main'
        checker.errors = []
        return checker

    def test_returns_pr_number_on_success(self):
        # gh CLI returns a non-empty JSON array → returns the first PR number
        mock_response = json.dumps([{'number': 123}])
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, mock_response)):
            checker = self._make_checker()
            result = checker._get_pr_from_sha('abc123', 'main', 'nvl.common')
            self.assertEqual(result, 123)

    def test_returns_none_when_empty_array(self):
        # gh CLI returns empty JSON array → returns None
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, json.dumps([]))):
            checker = self._make_checker()
            result = checker._get_pr_from_sha('abc123', 'main', 'nvl.common')
            self.assertIsNone(result)

    def test_returns_none_on_command_failure(self):
        # gh CLI exits non-zero → returns None
        with patch.object(SystemCall, 'run_outtxt', return_value=(1, '')):
            checker = self._make_checker()
            result = checker._get_pr_from_sha('abc123', 'main', 'nvl.cpu')
            self.assertIsNone(result)

    def test_returns_none_on_empty_output(self):
        # gh CLI exits 0 but produces no output → returns None
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, '')):
            checker = self._make_checker()
            result = checker._get_pr_from_sha('dead1234', 'main', 'nvl.hub')
            self.assertIsNone(result)


class TestGetPrMergeTime(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance bypassing __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.errors = []
        return checker

    def test_returns_timestamp_on_success(self):
        # gh CLI returns mergedAt ISO string → utc2local converts it to a float timestamp
        mock_response = json.dumps({'mergedAt': '2023-01-15T10:30:00Z'})
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, mock_response)):
            with patch('gadget.strmore.utc2local', return_value=1673778600.0):
                checker = self._make_checker()
                result = checker._get_pr_merge_time(123, 'main', 'nvl.common')
                self.assertEqual(result, 1673778600.0)

    def test_returns_none_on_command_failure(self):
        # gh CLI exits non-zero → returns None
        with patch.object(SystemCall, 'run_outtxt', return_value=(1, '')):
            checker = self._make_checker()
            result = checker._get_pr_merge_time(123, 'main', 'nvl.common')
            self.assertIsNone(result)

    def test_returns_none_when_merged_at_missing(self):
        # Response JSON has no mergedAt key → returns None
        mock_response = json.dumps({'title': 'my PR'})
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, mock_response)):
            checker = self._make_checker()
            result = checker._get_pr_merge_time(123, 'main', 'nvl.common')
            self.assertIsNone(result)

    def test_returns_none_on_empty_output(self):
        # gh CLI exits 0 with empty output → returns None
        with patch.object(SystemCall, 'run_outtxt', return_value=(0, '')):
            checker = self._make_checker()
            result = checker._get_pr_merge_time(456, 'main', 'nvl.cpu')
            self.assertIsNone(result)


class TestGetAtomicRevisionForPr(TestCase):

    def _make_checker(self):
        # Build a checker instance bypassing __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.branch_name = 'main'
        checker.errors = []
        return checker

    def test_direct_lookup_hit_returns_revision_and_pr(self):
        # PR found directly in atomic JSON → returns (atomic_rev, atomic_bom, pr_number)
        checker = self._make_checker()
        checker._read_atomic_json = lambda branch: SAMPLE_JSON
        with patch('main.atomic_rev_check.AtomicRevisionManager') as mock_mgr_cls:
            mock_mgr = mock_mgr_cls.return_value
            mock_mgr._get_atomic_info.return_value = ('3.4', 'S28C')
            mock_mgr._atomic_json_cache = {}
            result = checker._get_atomic_revision_for_pr(2021, 'main', 'nvl.common')
            self.assertEqual(result, ('3.4', 'S28C', 2021))

    def test_direct_miss_falls_back_to_inherited_pr(self):
        # PR not tracked directly → walks reverse timeline and inherits from prior atomic PR
        checker = self._make_checker()
        checker._read_atomic_json = lambda branch: SAMPLE_JSON
        with patch('main.atomic_rev_check.AtomicRevisionManager') as mock_mgr_cls:
            mock_mgr = mock_mgr_cls.return_value
            # First call: direct lookup misses; second call: inherited PR lookup hits
            mock_mgr._get_atomic_info.side_effect = [('', ''), ('3.0', 'All_BOM')]
            mock_mgr._load_atomic_json.return_value = {'2000': ['3.0.11111111111']}
            with patch.object(checker, '_get_pr_merge_time', side_effect=[1000.0, 500.0]):
                # target PR 2050 merged at t=1000; atomic PR 2000 merged at t=500 (before) → inherit
                result = checker._get_atomic_revision_for_pr(2050, 'main', 'nvl.common')
                self.assertEqual(result[0], '3.0')
                self.assertEqual(result[1], 'All_BOM')
                self.assertEqual(result[2], 2000)

    def test_no_merge_time_returns_empty_tuple(self):
        # Target PR merge time cannot be retrieved → returns ('', '', None)
        checker = self._make_checker()
        checker._read_atomic_json = lambda branch: SAMPLE_JSON
        with patch('main.atomic_rev_check.AtomicRevisionManager') as mock_mgr_cls:
            mock_mgr = mock_mgr_cls.return_value
            mock_mgr._get_atomic_info.return_value = ('', '')
            mock_mgr._load_atomic_json.return_value = {'2000': ['3.0.11111111111']}
            with patch.object(checker, '_get_pr_merge_time', return_value=None):
                result = checker._get_atomic_revision_for_pr(9999, 'main', 'nvl.common')
                self.assertEqual(result, ('', '', None))

    def test_no_prior_atomic_pr_returns_empty_tuple(self):
        # All atomic PRs merged AFTER the target PR → no inheritance possible → ('', '', None)
        checker = self._make_checker()
        checker._read_atomic_json = lambda branch: SAMPLE_JSON
        with patch('main.atomic_rev_check.AtomicRevisionManager') as mock_mgr_cls:
            mock_mgr = mock_mgr_cls.return_value
            mock_mgr._get_atomic_info.return_value = ('', '')
            mock_mgr._load_atomic_json.return_value = {'2200': ['5.0.11111111111']}
            # target merged at t=100; atomic PR 2200 merged at t=200 (after target)
            with patch.object(checker, '_get_pr_merge_time', side_effect=[100.0, 200.0]):
                result = checker._get_atomic_revision_for_pr(2050, 'main', 'nvl.common')
                self.assertEqual(result, ('', '', None))

    def test_empty_json_returns_empty_tuple(self):
        # _read_atomic_json returns None → load fails → repo_data empty → ('', '', None)
        checker = self._make_checker()
        checker._read_atomic_json = lambda branch: None
        with patch('main.atomic_rev_check.AtomicRevisionManager') as mock_mgr_cls:
            mock_mgr = mock_mgr_cls.return_value
            mock_mgr._get_atomic_info.return_value = ('', '')
            mock_mgr._load_atomic_json.return_value = {}
            with patch.object(checker, '_get_pr_merge_time', return_value=1000.0):
                result = checker._get_atomic_revision_for_pr(2050, 'main', 'nvl.common')
                self.assertEqual(result, ('', '', None))


class TestInit(TestCase):

    def test_init_sets_all_attributes(self):
        # Constructor must set bom_name, branch_name, self_repo_name, repo_info, errors
        with patch.object(AtomicConsistencyChecker, '_resolve_branch_name', return_value='main'):
            checker = AtomicConsistencyChecker('Class_NVL_S28C')
        self.assertEqual(checker.bom_name, 'Class_NVL_S28C')
        self.assertEqual(checker.branch_name, 'main')
        self.assertIsNone(checker.self_repo_name)
        self.assertEqual(checker.repo_info, {})
        self.assertEqual(checker.errors, [])


class TestReadAtomicJson(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance bypassing __init__
        return AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)

    def test_returns_json_on_success(self):
        # DataHost.central returns a dict → returned to caller
        expected = {'nvl.common': {'100': ['2.0.11111111111']}}
        checker = self._make_checker()
        with patch('main.atomic_rev_check.DataHost') as mock_dh:
            mock_dh.return_value.central.return_value = expected
            result = checker._read_atomic_json('main')
            self.assertEqual(result, expected)

    def test_exception_returns_none(self):
        # DataHost.central raises an exception → swallowed, returns None
        checker = self._make_checker()
        with patch('main.atomic_rev_check.DataHost') as mock_dh:
            mock_dh.return_value.central.side_effect = Exception('Connection error')
            result = checker._read_atomic_json('main')
            self.assertIsNone(result)


class TestRun(TestCase):

    def _make_checker(self):
        # Build a checker bypassing __init__ to avoid git/env side-effects
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.bom_name = 'Class_NVL_S28C'
        checker.branch_name = 'main'
        checker.self_repo_name = None
        checker.repo_info = {}
        checker.errors = []
        return checker

    def test_run_nvl_common_not_in_repos_raises(self):
        # repos_to_check has no nvl.common; SHA fails → all errors, atomic_resolution_failed → ErrorUser raised
        checker = self._make_checker()
        with patch.object(checker, '_get_repos_to_check', return_value={'nvl.cpu': '.'}):
            with patch.object(checker, '_get_git_sha', return_value=None):
                with patch.object(checker, 'rename_por_tp_on_failure'):
                    with self.assertRaises(ErrorUser):
                        checker.main()

    def test_run_sha_failure_appends_error_and_continues(self):
        # _get_git_sha returns None → error recorded for each repo without SHA, then ErrorUser raised
        checker = self._make_checker()
        repos = {'nvl.common': '.', 'nvl.cpu': 'cpu_path'}
        with patch.object(checker, '_get_repos_to_check', return_value=repos):
            with patch.object(checker, '_get_git_sha', return_value=None):
                with patch.object(checker, 'rename_por_tp_on_failure'):
                    with self.assertRaises(ErrorUser):
                        checker.main()
                    self.assertTrue(any('nvl.common' in e for e in checker.errors))
                    self.assertTrue(any('nvl.cpu' in e for e in checker.errors))

    def test_run_no_discovered_branch_falls_back_to_git_and_explicit_pr(self):
        # _discover_branch_from_sha returns (None, None, False) → _get_git_branch and _get_pr_from_sha called
        checker = self._make_checker()
        with patch.object(checker, '_get_repos_to_check', return_value={'nvl.common': '.'}):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(None, None, False)):
                    with patch.object(checker, '_get_git_branch', return_value='main') as mock_gb:
                        with patch.object(checker, '_get_pr_from_sha', return_value=100) as mock_gp:
                            with patch.object(checker, '_get_atomic_revision_for_pr', return_value=('3.0', 'All_BOM', 100)):
                                with patch.object(checker, '_read_atomic_json', return_value=SAMPLE_JSON):
                                    checker.main()
                                    mock_gb.assert_called_once_with('.')
                                    mock_gp.assert_called_once()

    def test_run_full_happy_path_returns_true(self):
        # All sub-calls succeed, consistency passes → (True, populated repo_info)
        checker = self._make_checker()
        repos = {'nvl.common': '.', 'nvl.cpu': 'cpu_path'}
        with patch.object(checker, '_get_repos_to_check', return_value=repos):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(100, 'main', True)):
                    with patch.object(checker, '_get_atomic_revision_for_pr', return_value=('3.0', 'All_BOM', 100)):
                        with patch.object(checker, '_check_atomic_consistency', return_value=True):
                            success, info = checker.main()
                            self.assertTrue(success)
                            self.assertIn('nvl.common', info)
                            self.assertIn('nvl.cpu', info)
                            self.assertEqual(info['nvl.common']['atomic_rev'], '3.0')

    def test_run_consistency_fails_raises(self):
        # _check_atomic_consistency returns False → ErrorUser raised
        checker = self._make_checker()
        with patch.object(checker, '_get_repos_to_check', return_value={'nvl.common': '.'}):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(100, 'main', True)):
                    with patch.object(checker, '_get_atomic_revision_for_pr', return_value=('3.0', 'All_BOM', 100)):
                        with patch.object(checker, '_check_atomic_consistency', return_value=False):
                            with patch.object(checker, 'rename_por_tp_on_failure'):
                                with self.assertRaises(ErrorUser):
                                    checker.main()

    def test_run_no_atomic_rev_repo_info_has_none_inherited_pr(self):
        # _get_atomic_revision_for_pr returns ('', '', None) → error recorded, ErrorUser raised
        checker = self._make_checker()
        with patch.object(checker, '_get_repos_to_check', return_value={'nvl.common': '.'}):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(100, 'main', True)):
                    with patch.object(checker, '_get_atomic_revision_for_pr', return_value=('', '', None)):
                        with patch.object(checker, 'rename_por_tp_on_failure'):
                            with self.assertRaises(ErrorUser):
                                checker.main()
                        self.assertIsNone(checker.repo_info['nvl.common']['inherited_atomic_pr'])
                        self.assertTrue(any('nvl.common' in e for e in checker.errors))

    def test_run_multiple_unresolvable_atomic_revs_all_errors_listed(self):
        # Two repos both return ('', '', None) → both errors recorded, ErrorUser raised
        checker = self._make_checker()
        repos = {'nvl.common': '.', 'nvl.cpu': 'cpu_path'}
        with patch.object(checker, '_get_repos_to_check', return_value=repos):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(100, 'main', True)):
                    with patch.object(checker, '_get_atomic_revision_for_pr', return_value=('', '', None)):
                        with patch.object(checker, 'rename_por_tp_on_failure'):
                            with self.assertRaises(ErrorUser):
                                checker.main()
                        self.assertTrue(any('nvl.common' in e for e in checker.errors))
                        self.assertTrue(any('nvl.cpu' in e for e in checker.errors))

    def test_run_no_pr_triggers_bypass_returns_true(self):
        # Both _discover_branch_from_sha and _get_pr_from_sha find nothing
        # → repo gets status: not_merged → bypass fires → main() returns (True, repo_info)
        checker = self._make_checker()
        with patch.object(checker, '_get_repos_to_check', return_value={'nvl.common': '.'}):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(None, None, False)):
                    with patch.object(checker, '_get_git_branch', return_value='main'):
                        with patch.object(checker, '_get_pr_from_sha', return_value=None):
                            success, info = checker.main()
                            self.assertTrue(success)  # bypass → skipped, not a failure
                            self.assertEqual(info['nvl.common']['status'], 'not_merged')
                            self.assertIsNone(info['nvl.common']['pr'])

    def test_run_open_pr_triggers_bypass_returns_true(self):
        # _discover_branch_from_sha finds an open (unmerged) PR
        # → repo gets status: not_merged with pr stored → bypass fires
        checker = self._make_checker()
        with patch.object(checker, '_get_repos_to_check', return_value={'nvl.common': '.'}):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(555, 'main', False)):
                    success, info = checker.main()
                    self.assertTrue(success)  # bypass → skipped, not a failure
                    self.assertEqual(info['nvl.common']['status'], 'not_merged')
                    self.assertEqual(info['nvl.common']['pr'], 555)


class TestRunIntegration(TestCase):

    def _make_checker(self):
        # Build a checker bypassing __init__ to avoid git/env side-effects
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.bom_name = 'Class_NVL_S28C'
        checker.branch_name = 'main'
        checker.self_repo_name = None
        checker.repo_info = {}
        checker.errors = []
        return checker

    def test_run_integration_all_repos_consistent_passes(self):
        # Full run() with real _check_atomic_consistency: nvl.common@2021, pcd@1660, gcd@1276
        # → all consistent at anchor (3,4) for S28C → True
        checker = self._make_checker()
        repos = {'nvl.common': '.', 'nvl.pcd': 'pcd_path', 'nvl.gcd': 'gcd_path'}
        atomic_prs = {'nvl.common': 2021, 'nvl.pcd': 1660, 'nvl.gcd': 1276}

        def atomic_rev_se(pr_number, branch, repo):
            return ('', '', atomic_prs[repo])

        with patch.object(checker, '_get_repos_to_check', return_value=repos):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(999, 'main', True)):
                    with patch.object(checker, '_get_atomic_revision_for_pr', side_effect=atomic_rev_se):
                        with patch.object(checker, '_read_atomic_json', return_value=SAMPLE_JSON):
                            success, info = checker.main()
                            self.assertTrue(success)
                            self.assertEqual(checker.errors, [])

    def test_run_integration_pcd_behind_anchor_fails(self):
        # Full run() with real _check_atomic_consistency: nvl.common@2021, pcd@1414
        # → pcd stuck at (3,0), anchor is (3,4) for S28C → ErrorUser raised with pcd error
        checker = self._make_checker()
        repos = {'nvl.common': '.', 'nvl.pcd': 'pcd_path'}
        atomic_prs = {'nvl.common': 2021, 'nvl.pcd': 1414}

        def atomic_rev_se(pr_number, branch, repo):
            return ('', '', atomic_prs[repo])

        with patch.object(checker, '_get_repos_to_check', return_value=repos):
            with patch.object(checker, '_get_git_sha', return_value='abc123def456full'):
                with patch.object(checker, '_discover_branch_from_sha', return_value=(999, 'main', True)):
                    with patch.object(checker, '_get_atomic_revision_for_pr', side_effect=atomic_rev_se):
                        with patch.object(checker, '_read_atomic_json', return_value=SAMPLE_JSON):
                            with patch.object(checker, 'rename_por_tp_on_failure'):
                                with self.assertRaises(ErrorUser):
                                    checker.main()
                            self.assertTrue(any('nvl.pcd' in e for e in checker.errors))


class TestRenamePorTp(TestCase):

    def _make_checker(self):
        # Build a minimal checker instance bypassing __init__
        checker = AtomicConsistencyChecker.__new__(AtomicConsistencyChecker)
        checker.errors = []
        return checker

    def test_rename_no_env_var_skips_rename(self):
        # TP_OUTPUT_PATH empty → method returns without touching filesystem
        checker = self._make_checker()
        with patch.dict('os.environ', {'TP_OUTPUT_PATH': ''}):
            with patch('os.path.isdir') as mock_isdir:
                with patch('os.rename') as mock_rename:
                    checker.rename_por_tp_on_failure()
                    mock_isdir.assert_not_called()
                    mock_rename.assert_not_called()

    def test_rename_por_tp_dir_exists_renames_to_failed(self):
        # POR_TP directory exists → renamed to POR_TP_FAILED
        checker = self._make_checker()
        with patch.dict('os.environ', {'TP_OUTPUT_PATH': '/output/path'}):
            with patch('os.path.isdir', return_value=True):
                with patch('os.rename') as mock_rename:
                    checker.rename_por_tp_on_failure()
                    mock_rename.assert_called_once_with(
                        os.path.join('/output/path', 'POR_TP'),
                        os.path.join('/output/path', 'POR_TP_FAILED')
                    )

    def test_rename_por_tp_dir_missing_skips_rename(self):
        # POR_TP directory does not exist → os.rename not called
        checker = self._make_checker()
        with patch.dict('os.environ', {'TP_OUTPUT_PATH': '/output/path'}):
            with patch('os.path.isdir', return_value=False):
                with patch('os.rename') as mock_rename:
                    checker.rename_por_tp_on_failure()
                    mock_rename.assert_not_called()


class TestSeedAtomicJson(TestCase):

    def test_seed_dst_exists_skips_copy(self):
        # dst JSON already exists → returns without copying
        with patch('os.path.exists', return_value=True):
            with patch('main.atomic_rev_check.shutil.copy2') as mock_copy:
                AtomicConsistencyChecker.seed_atomic_json('main_42')
                mock_copy.assert_not_called()

    def test_seed_src_missing_exits(self):
        # dst does not exist, src also missing → sys.exit(1)
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(SystemExit) as ctx:
                AtomicConsistencyChecker.seed_atomic_json('main_42')
            self.assertEqual(ctx.exception.code, 1)

    def test_seed_happy_path_copies_src_to_dst(self):
        # dst does not exist, src exists → shutil.copy2 called once
        def exists_se(p):
            return 'main_42' not in p  # src (main.json) exists, dst (main_42.json) does not
        with patch('os.path.exists', side_effect=exists_se):
            with patch('main.atomic_rev_check.shutil.copy2') as mock_copy:
                AtomicConsistencyChecker.seed_atomic_json('main_42')
                mock_copy.assert_called_once()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
