#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Atomic Revision Consistency Checker

Validates atomic revision consistency across multiple repositories during test program build.
Ensures all repos are using compatible atomic versions for the BOM being built.

Exit Codes:
    0: Success - All atomic revisions are consistent
    1: Failure - Atomic version mismatch detected

Usage:
    atomic_rev_check.py <BOM_name>

Example:
    atomic_rev_check.py Class_NVL_S28C

Environment Variables:
    BASE_REF: Branch name for atomic version lookup (default: main)

Design:
    - Runs during nvl_buildtp workflow (before actual build)
    - Detects which repos are involved (nvl.common + any dielets)
    - Gets current git commit SHA for each repo
    - Looks up PR number from SHA using gh CLI
    - Validates atomic revision consistency (major + minor versions)
    - Performs BOM-aware compatibility checking
"""
import sys
import os
import re
import shutil
import setenv

from gadget.pylog import log
from gadget.shell import SystemCall
from gadget.disk import Chdir
from gadget.data_host import DataHost
from gadget.errors import ErrorUser
from mod.cci_list import AtomicRevisionManager
from main.tprobot import AtomicChange
from tp.testprogram import Env
import json


class AtomicConsistencyChecker:
    """
    Standalone atomic revision consistency checker for test program builds.
    """

    def __init__(self, bom_name):
        """
        Initialize checker.

        :param bom_name: BOM name being built (e.g., 'Class_NVL_S28C')
        """
        self.bom_name = bom_name
        self.branch_name = self._resolve_branch_name()
        self.self_repo_name = None
        self.repo_info = {}
        self.errors = []

    def _resolve_branch_name(self):
        """
        Determine the correct branch name for atomic JSON lookup.

        Strategy:
        1. Read BASE_REF from environment (set by GitHub Actions workflow)
        2. Query git for the actual branch name of the current checkout
        3. If the git branch starts with the BASE_REF prefix (e.g. main_*)
           AND a matching JSON file exists, use the git branch name
        4. If git branch is a feature branch but has no JSON, exit with error

        This handles main_* feature branches that have their own atomic JSON
        (e.g. main_atomic_automation.json) while still defaulting to 'main'
        for normal main-branch builds.

        :return: Branch name string (e.g. 'main', 'main_atomic_automation')
        """
        base_ref = os.environ.get('BASE_REF', 'main')

        # Ask git for the current branch name
        exitcode, output = SystemCall('git rev-parse --abbrev-ref HEAD').run_outtxt()
        if exitcode != 0 or not output or not output.strip():
            log.info(f'-i- Could not detect git branch, using BASE_REF={base_ref}')
            return base_ref

        git_branch = output.strip()

        # If git branch matches BASE_REF exactly, use it directly
        if git_branch == base_ref:
            return base_ref

        # If git branch starts with BASE_REF prefix (e.g. main_*),
        # check whether a matching atomic JSON file exists
        if git_branch.startswith(f'{base_ref}_'):
            atomic_file = Env.xpath(
                os.path.join(AtomicRevisionManager.ATOMIC_DIR, f'{git_branch}.json')
            )
            if os.path.exists(atomic_file):
                log.info(f'-i- Detected feature branch {git_branch} with its own atomic JSON')
                return git_branch
            else:
                log.info(
                    f'-e- Feature branch {git_branch} has no atomic JSON, '
                    f'please create one or bypass atomic_consistency_check'
                )
                sys.exit(1)

        return base_ref

    def main(self):
        """
        Execute atomic consistency check.

        Raises ``ErrorUser`` on failure so the calling workflow sees a clear
        error message.

        :return: Tuple of (True, details: dict) on success
        :raises ErrorUser: When atomic revisions are inconsistent
        """
        log.info('-i- Starting Atomic Consistency Check')
        log.info(f'-i- Branch: {self.branch_name}')
        log.info(f'-i- BOM: {self.bom_name}')

        repos_to_check = self._get_repos_to_check()
        log.info(f'-i- Found {len(repos_to_check)} repositories involved in this build')
        log.info(f'-i- Repos: {", ".join(repos_to_check.keys())}')
        log.info('-i-')

        atomic_resolution_failed = self._resolve_all_repo_info(repos_to_check)

        bypass_result = self._check_unmerged_pr_bypass()
        if bypass_result is not None:
            return bypass_result

        self._log_repo_summary()

        _fail_msg = (
            'ATOMIC_rev are incompatible between common and dielet repo.',
            'Review CCI page for compatibility. '
            'If this is a false positive (or MV builds), contact TPTeam (sgourshe and/or jqdelosr). '
            'To proceed manually, rename POR_TP_FAILED back to POR_TP in TP_OUTPUT_PATH.'
        )

        if atomic_resolution_failed:
            log.info('-i- FAIL: atomic revision unresolvable for one or more repos')
            self.rename_por_tp_on_failure()
            raise ErrorUser(*_fail_msg)

        log.info('-i-')
        log.info('-i- ===== ATOMIC CONSISTENCY CHECK =====')
        consistency_ok = self._check_atomic_consistency(self.repo_info, self.bom_name)

        if consistency_ok:
            log.info('-i- PASS: All repositories have consistent atomic versions')
            return True, self.repo_info
        else:
            log.info('-i- FAIL: Atomic version mismatch detected')
            self.rename_por_tp_on_failure()
            raise ErrorUser(*_fail_msg)

    def _resolve_all_repo_info(self, repos_to_check):
        """
        Resolve SHA, PR number, branch, and atomic revision for every repo.

        Populates ``self.repo_info`` for each repo and appends to
        ``self.errors`` for any repo that cannot be fully resolved.

        :param repos_to_check: Dict of {repo_name: repo_path}
        :return: True if any repo's atomic revision could not be resolved,
                 False if all repos resolved successfully
        """
        atomic_resolution_failed = False
        for repo, repo_path in repos_to_check.items():
            log.info(f'-i- Processing {repo}...')

            commit_sha = self._get_git_sha(repo_path)
            if not commit_sha:
                error_msg = f'Cannot determine git commit SHA for {repo} at path [{repo_path}]'
                log.info(f'-i-   ERROR: Could not get SHA')
                self.errors.append(error_msg)
                continue

            log.info(f'-i-   SHA: {commit_sha[:8]}... (full: {commit_sha})')

            # Detect this repo's own branch for PR base-branch lookup.
            # First try auto-discovering from the SHA via gh CLI; this also
            # gives us the PR number and the actual trunk name the PR was
            # merged into (resolving repos with non-standard trunk names).
            pr_number, discovered_branch, is_merged = self._discover_branch_from_sha(commit_sha, repo)

            if discovered_branch:
                repo_branch = discovered_branch
                log.info(f'-i-   Branch (from PR): {repo_branch}')
            else:
                # Fallback: read the git checkout's branch directly
                repo_branch = self._get_git_branch(repo_path)
                log.info(f'-i-   Branch (from git): {repo_branch}')

            if not pr_number:
                # Discovery didn't find a PR — try the explicit branch lookup
                pr_number = self._get_pr_from_sha(commit_sha, repo_branch, repo)
                if pr_number:
                    is_merged = True  # _get_pr_from_sha uses --state merged
            log.info(f'-i-   PR: #{pr_number}')

            # Bypass: SHA has no associated merged PR — skip atomic resolution for this repo
            if not pr_number:
                log.info(f'-i-   No merged PR found for {repo} (SHA {commit_sha[:8]}); skipping atomic resolution')
                self.repo_info[repo] = {
                    'sha': commit_sha,
                    'pr': None,
                    'status': 'not_merged',
                    'atomic_rev': None,
                    'atomic_bom': None,
                    'inherited_atomic_pr': None,
                    'atomic_branch': discovered_branch or self.branch_name,
                }
                log.info('-i-')
                continue

            # Bypass: SHA resolves to an open (not yet merged) PR — skip atomic resolution
            if not is_merged:
                log.info(f'-i-   PR #{pr_number} is open (not merged); skipping atomic resolution')
                self.repo_info[repo] = {
                    'sha': commit_sha,
                    'pr': pr_number,
                    'status': 'not_merged',
                    'atomic_rev': None,
                    'atomic_bom': None,
                    'inherited_atomic_pr': None,
                    'atomic_branch': discovered_branch or self.branch_name,
                }
                log.info('-i-')
                continue

            # Each repo uses its own trunk's JSON for the atomic revision lookup
            # (e.g. nvl.hub -> main_atomic_automation.json, nvl.common -> main.json).
            # Use the branch discovered from the SHA/PR; fall back to self.branch_name
            # only as a last resort (e.g. gh CLI unavailable).
            atomic_branch = discovered_branch or self.branch_name
            atomic_rev, atomic_bom, inherited_pr = self._get_atomic_revision_for_pr(pr_number, atomic_branch, repo)
            if atomic_rev:
                log.info(f'-i-   Atomic Rev: {atomic_rev}')
                log.info(f'-i-   BOM Impact: {atomic_bom}')
                log.info(f'-i-   Inherited Atomic PR: #{inherited_pr}')
            else:
                log.info(f'-i-   Atomic Rev: Not tracked')
                if inherited_pr is None:
                    error_msg = (
                        f'{repo}: could not determine inherited atomic PR '
                        f'(SHA {commit_sha[:8]}, PR #{pr_number})'
                    )
                    log.info(f'-i-   ERROR: {error_msg}')
                    self.errors.append(error_msg)
                    atomic_resolution_failed = True

            self.repo_info[repo] = {
                'sha': commit_sha,
                'pr': pr_number,
                'status': 'merged',
                'atomic_rev': atomic_rev,
                'atomic_bom': atomic_bom,
                'inherited_atomic_pr': inherited_pr,
                'atomic_branch': atomic_branch,
            }

            log.info('-i-')

        return atomic_resolution_failed

    def _check_unmerged_pr_bypass(self):
        """
        Check whether any repo in the atomic check has no merged PR.

        If any SHA in the atomic check resolves to no merged PR, the atomic
        consistency check cannot run and is skipped.

        ``self.repo_info`` must be populated before calling this.

        :return: Tuple (True, self.repo_info) if bypass is triggered,
                 None if no bypass is needed
        """
        repos_without_merged_pr = [
            repo for repo, info in self.repo_info.items()
            if info.get('status') == 'not_merged'
        ]
        if not repos_without_merged_pr:
            return None

        log.info('-i-')
        log.info('-i- ************************************************************')
        log.info('-i- ** ATOMIC_REV CHECK SKIPPED                              **')
        log.info('-i- ************************************************************')
        log.info('-i- Reason: The following repo SHA(s) do not resolve to a merged PR,')
        log.info('-i-          so Atomic_rev_check cannot run:')
        for _repo in repos_without_merged_pr:
            _sha = self.repo_info[_repo]['sha'] or 'unknown'
            _pr = self.repo_info[_repo].get('pr')
            _pr_note = f' (open PR #{_pr})' if _pr else ' (no PR found)'
            log.info(f'-i-     {_repo}: SHA {_sha[:8]}{_pr_note}')
        log.info('-i- Please verify that the supplied ref belongs to a merged PR')
        log.info('-i- before relying on atomic revision consistency.')
        log.info('-i- ************************************************************')
        return True, self.repo_info

    def _log_repo_summary(self):
        """
        Log a one-line summary for every resolved repo (SHA, PR, atomic rev).

        ``self.repo_info`` must be populated before calling this.
        """
        log.info('-i- ===== REPOSITORY SUMMARY =====')
        for repo, info in sorted(self.repo_info.items()):
            pr_display = f"PR#{info['pr']}" if info['pr'] else 'no PR'
            atomic_display = info.get('atomic_rev', '') or 'N/A'
            log.info(f'-i- {repo:15s} SHA: {info["sha"][:8]}  {pr_display:20s}  Atomic: {atomic_display}')

    def _get_self_repo_name(self):
        """
        Detect which repository the current working directory belongs to by
        parsing the git remote URL.

        :return: Repo name string (e.g. 'nvl.common', 'nvl.hub') or
                 basename of cwd as fallback
        """
        exitcode, output = SystemCall('git remote get-url origin').run_outtxt()
        if exitcode == 0 and output and output.strip():
            url = output.strip()
            # e.g. https://github.com/intel-restricted/nvl.hub.git  ->  nvl.hub
            match = re.search(r'/([^/]+?)(?:\.git)?$', url)
            if match:
                return match.group(1)
        # Fallback: dirname of cwd (mirrors GitHub Actions checkout path)
        return os.path.basename(os.getcwd())

    def _get_repos_to_check(self):
        """
        Determine which repos to check based on build context.

        Rules:
          - If running from a dielet repo: check [self, nvl.common] only.
            nvl.common is expected to already be cloned at root/nvl.common by
            nvl_buildtp.py (TP Build step). This avoids picking up stale repos
            left behind by previous runner runs.
          - If running from nvl.common: check nvl.common + only the dielets
            whose branch env vars are explicitly set (CPU_Branch, GCD_Branch,
            PCD_Branch, HUB_Branch). This matches exactly what the user
            requested in the workflow inputs.

        Root path follows the same logic as nvl_buildtp.py:
          - Inside GitHub Actions runner (_work dir present): root = ../../../
          - Outside runner (local/dev):                       root = ../

        :return: Dictionary of {repo_name: repo_path} to check
        """
        self_repo = self._get_self_repo_name()
        log.info(f'-i- Self repo detected as: {self_repo}')
        self.self_repo_name = self_repo

        # Same root logic as nvl_buildtp.py
        root = '../../../' if os.path.isdir('../../../_work') else '../'

        repos_to_check = {self_repo: '.'}

        if self_repo == 'nvl.common':
            # Common repo workflow: include only explicitly requested dielets
            dielet_env_map = {
                'nvl.cpu': 'CPU_Branch',
                'nvl.gcd': 'GCD_Branch',
                'nvl.pcd': 'PCD_Branch',
                'nvl.hub': 'HUB_Branch',
            }
            for repo, env_var in dielet_env_map.items():
                branch_val = os.environ.get(env_var, '').strip().lower()
                if branch_val and branch_val != 'none':
                    repo_path = os.path.join(root, repo)
                    if os.path.isdir(repo_path):
                        log.info(f'-i- Including dielet {repo} ({env_var}={os.environ[env_var]})')
                        repos_to_check[repo] = repo_path
                    else:
                        log.info(f'-i- Dielet {repo} requested via {env_var} but not found at {repo_path}')
                else:
                    log.info(f'-i- Skipping {repo}: {env_var} not set or is "none" ({os.environ.get(env_var, "")})')
        else:
            # Dielet repo workflow: nvl.common is the Shared/ submodule inside
            # the dielet checkout (populated by TP Build / update_shared_sha_latest)
            if os.path.isdir('Shared'):
                log.info('-i- Found nvl.common at Shared/ (submodule)')
                repos_to_check['nvl.common'] = 'Shared'
            else:
                log.info(
                    '-i- nvl.common (Shared/) not found. '
                    'Atomic check must run AFTER TP Build in dielet workflow.'
                )

        return repos_to_check

    def _get_git_sha(self, repo_path):
        """
        Get current git commit SHA for a repository.

        :param repo_path: Path to repository (relative or absolute)
        :return: Full commit SHA string, or None if error
        """
        with Chdir(repo_path):
            cmd = 'git rev-parse HEAD'
            exitcode, output = SystemCall(cmd).run_outtxt()
            if exitcode == 0 and output:
                sha = output.strip()
                return sha
            else:
                log.info(f'-i- Failed to get SHA for {repo_path}: exitcode={exitcode}')
                return None

    def _discover_branch_from_sha(self, commit_sha, repo_name):
        """
        Discover the PR number AND base branch name from a commit SHA.

        The SHA provided by the build workflow may be associated with multiple
        PRs (e.g. a feature branch merged first into an integration branch,
        then into main).  ``gh pr list --search sha:`` returns all matching
        PRs and the ordering is non-deterministic, so it can return the
        integration-branch PR before the mainline one.

        The ``/commits/{sha}/pulls`` REST endpoint is more reliable: it returns
        only the PR(s) that directly contain this commit on their base branch,
        which for a mainline build will be the trunk PR (main or
        main_atomic_automation).

        Strategy:
        1. Use ``gh api /commits/{sha}/pulls`` REST endpoint first.
           This unambiguously resolves the PR and base branch for the commit.
           The ``merged_at`` field is checked to detect open vs merged PRs.
        2. If that returns nothing, fall back to ``gh pr list --search sha:``.
           This handles squash/rebase merges where the search index may
           return a result when the REST endpoint does not.
        3. Return (pr_number, baseRefName, is_merged) on success,
           (None, None, False) otherwise.

        :param commit_sha: Full or abbreviated git commit SHA (merge or head)
        :param repo_name:  Repository name (e.g. 'nvl.common', 'nvl.cpu')
        :return: Tuple of (pr_number: int | None, base_branch: str | None,
                           is_merged: bool)
        """
        gh = self._gh_cmd()

        # --- attempt 1: use /commits/{sha}/pulls REST endpoint ---
        # Returns PRs associated with this commit regardless of PR state.
        # Check merged_at to distinguish open from merged PRs.
        api_cmd = (f'{gh} api repos/intel-restricted/{repo_name}'
                   f'/commits/{commit_sha}/pulls '
                   f'--header "Accept: application/vnd.github+json"')
        ec, out = SystemCall(api_cmd).run_outtxt()
        if ec == 0 and out.strip():
            data = json.loads(out)
            if data:
                pr_number = data[0]['number']
                base_branch = data[0].get('base', {}).get('ref', None)
                is_merged = data[0].get('merged_at') is not None
                log.info(f'-i- Found via commits/pulls API: PR #{pr_number} on {base_branch} '
                         f'(merged={is_merged})')
                return pr_number, base_branch, is_merged

        # --- attempt 2: fall back to gh pr list --search sha: ---
        # Handles squash/rebase merges where the trunk commit IS the PR head.
        # --state merged guarantees all returned PRs are merged.
        # May return multiple PRs when the commit was in an integration branch
        # first; take data[0] as a best-effort result.
        log.info(f'-i- commits/pulls API found nothing for {commit_sha[:8]}, '
                 f'falling back to sha: search for {repo_name}')
        cmd = (f'{gh} pr list --search sha:{commit_sha} --state merged '
               f'--json number,baseRefName --repo intel-restricted/{repo_name}')
        ec, out = SystemCall(cmd).run_outtxt()
        if ec == 0 and out.strip():
            data = json.loads(out)
            if data:
                pr_number = data[0]['number']
                base_branch = data[0].get('baseRefName', None)
                log.info(f'-i- Found via sha: search: PR #{pr_number} on {base_branch}')
                return pr_number, base_branch, True

        log.info(f'-i- No PR found for {repo_name} '
                 f'(tried commits/pulls API and sha: search for {commit_sha[:8]})')
        return None, None, False

    def _get_git_branch(self, repo_path):
        """
        Get the current branch name for a repository.

        :param repo_path: Path to repository (relative or absolute)
        :return: Branch name string, or 'main' as fallback
        """
        with Chdir(repo_path):
            exitcode, output = SystemCall('git rev-parse --abbrev-ref HEAD').run_outtxt()
            if exitcode == 0 and output and output.strip() not in ('HEAD', ''):
                return output.strip()
            log.info(f'-i- Could not detect branch for {repo_path}, using main')
            return 'main'

    def _get_pr_from_sha(self, commit_sha, branch_name, repo_name):
        """
        Look up PR number from commit SHA using GitHub CLI.
        Uses the same pattern as get_pr_view_closed() in tprobot.py.

        :param commit_sha: Git commit SHA
        :param branch_name: Branch name for search scope
        :param repo_name: Repository name (e.g., 'nvl.common', 'nvl.cpu')
        :return: PR number (int) or None if not found
        """
        gh = self._gh_cmd()

        # Search for merged PR with this SHA using gh CLI
        # Pattern from cci_list.py line 491 and tprobot.py get_pr_view_closed()
        # Must specify --repo to query the correct repository
        cmd = f'{gh} pr list --search sha:{commit_sha} --state merged --json number -B {branch_name} --repo intel-restricted/{repo_name}'

        exitcode, output = SystemCall(cmd).run_outtxt()

        if exitcode == 0 and output.strip():
            data = json.loads(output)
            if data and len(data) > 0:
                pr_number = data[0]['number']
                return pr_number

        log.info(f'-i- No PR found for SHA {commit_sha[:8]} on branch {branch_name}')
        return None

    def _get_atomic_revision_for_pr(self, pr_number, branch_name, repo_name):
        """
        Get the atomic revision for a PR, handling inheritance from previous PRs.
        If the PR is not explicitly tracked in atomic JSON, it inherits from the most recent atomic PR
        from the SAME REPO that merged BEFORE this one (by merge timestamp).

        Optimized approach:
        1. Filter JSON to only this repo's atomic PRs
        2. Walk in REVERSE (newest→oldest) - more efficient for recent PRs
        3. Return the first atomic PR that merged before target

        :param pr_number: PR number to look up
        :param branch_name: Branch name
        :param repo_name: Repository name (e.g., 'nvl.common')
        :return: Tuple of (atomic_rev, atomic_bom, inherited_pr) or ('', '', None) if not found
        """
        repo_short_name = repo_name.replace('.', '')  # nvl.common -> nvlcommon
        atomic_mgr = AtomicRevisionManager(repo_short_name, branch_name,
                                           AtomicRevisionManager.REPO_MAP)

        # AtomicRevisionManager._load_atomic_json() uses a raw /intel/ path without
        # Windows path translation.  Pre-populate its cache here using DataHost
        # so all subsequent calls (_get_atomic_info, _load_atomic_json) use the
        # correctly loaded data.
        atomic_filename = f'{AtomicRevisionManager.ATOMIC_DIR}/{branch_name}.json'
        log.info(f'-i-   JSON: {atomic_filename}')
        full_json = self._read_atomic_json(branch_name)
        if full_json is not None:
            repo_key = AtomicRevisionManager.REPO_MAP.get(repo_short_name, repo_short_name)
            atomic_mgr._atomic_json_cache = full_json.get(repo_key, {})
        else:
            log.info(f'-i-   JSON file not found: {atomic_filename}')
            atomic_mgr._atomic_json_cache = {}

        # Try direct lookup first
        atomic_rev, atomic_bom = atomic_mgr._get_atomic_info(pr_number)
        if atomic_rev:
            log.info(f'-i-   Direct lookup hit: PR #{pr_number} -> {atomic_rev}')
            # This PR is explicitly tracked as an atomic change
            return atomic_rev, atomic_bom, pr_number
        log.info(f'-i-   Direct lookup miss for PR #{pr_number}, checking inheritance')

        # Not explicitly tracked - need to find inherited value by merge time
        # Get merge time for this PR (only 1 API call)
        pr_merge_time = self._get_pr_merge_time(pr_number, branch_name, repo_name)
        if not pr_merge_time:
            return '', '', None

        # Load the JSON to see all atomic PRs (already ordered by merge sequence)
        repo_data = atomic_mgr._load_atomic_json()
        if not repo_data:
            log.info(f'-i-   No repo data found in JSON for {repo_name} (key={atomic_mgr.repo_map.get(repo_short_name, repo_short_name)})')
            return '', '', None

        # repo_data is already filtered to this repo by _load_atomic_json()
        # Just extract PR numbers and walk in REVERSE (newest→oldest)
        atomic_prs_this_repo = []
        for pr_str in repo_data.keys():
            if pr_str.isdigit():
                atomic_prs_this_repo.append(int(pr_str))
        log.info(f'-i-   Found {len(atomic_prs_this_repo)} atomic PRs for {repo_name} in JSON')

        # Walk in reverse order (newest→oldest) through list
        # JSON is ordered oldest→newest, so reverse to start from newest
        for atomic_pr in reversed(atomic_prs_this_repo):
            # Get merge time for this atomic PR
            atomic_merge_time = self._get_pr_merge_time(atomic_pr, branch_name, repo_name)
            if not atomic_merge_time:
                continue

            if atomic_merge_time < pr_merge_time:
                # Found it! This atomic PR merged before our target
                # This is the one to inherit from
                atomic_rev, atomic_bom = atomic_mgr._get_atomic_info(atomic_pr)
                return atomic_rev, atomic_bom, atomic_pr

        # No atomic PR from this repo merged before this one
        return '', '', None

    def _get_pr_merge_time(self, pr_number, branch_name, repo_name):
        """
        Get the merge timestamp for a PR.

        :param pr_number: PR number
        :param branch_name: Branch name
        :param repo_name: Repository name
        :return: Unix timestamp (float) or None if not found
        """
        gh = self._gh_cmd()
        cmd = f'{gh} pr view {pr_number} --json mergedAt --repo intel-restricted/{repo_name}'
        exitcode, output = SystemCall(cmd).run_outtxt()

        if exitcode == 0 and output.strip():
            data = json.loads(output)
            merged_at = data.get('mergedAt')
            if merged_at:
                # Convert ISO 8601 to Unix timestamp
                from gadget.strmore import utc2local
                return utc2local(merged_at, is_secs=True)

        return None

    def _check_atomic_consistency(self, repo_info, bom_name):
        """
        Matrix-based atomic revision consistency check.

        Builds a per-repo compatibility matrix from the global atomic version
        timeline, using each repo's inherited atomic PR as the cutoff point.
        Checks whether nvl.common's pinned version for the target BOM bit is
        present in every other repo's compatible set.

        Three-way PIN/SKIP/ADD rule applied per version event per flagged bit:
          PIN  - repo's first-entry PR <= cutoff (contributed, has landed)
          SKIP - repo's first-entry PR >  cutoff (contributed but not yet landed)
          ADD  - version never a first-entry for this repo (always compatible)

        nvl.common is the anchor because it contributes to every atomic version
        event and is therefore always pinned to a single value per bit.

        :param repo_info: Dict of {repo_name: {sha, pr, inherited_atomic_pr, ...}}
        :param bom_name: BOM being built (e.g., 'Class_NVL_S28C')
        :return: True if consistent, False if mismatch
        """
        # Map bom_name to bit position using BOM_MAPPING
        bom_short = bom_name[6:] if bom_name.startswith('Class_') else bom_name
        bom_names = [display for _, display in AtomicChange.BOM_MAPPING]
        if bom_short not in bom_names:
            log.info(f'-i- ERROR: BOM {bom_short} not found in BOM_MAPPING')
            self.errors.append(f'BOM {bom_short} not in BOM_MAPPING')
            return False
        bit_pos = bom_names.index(bom_short)
        log.info(f'-i- Target BOM: {bom_short} (bit {bit_pos})')

        # Derive the primary JSON branch from the self-repo's already-discovered
        # atomic_branch so we never rely on self.branch_name (which may be a
        # raw tag or SHA when the user supplied one instead of a branch name).
        # Fall back to nvl.common's branch (always the anchor repo) then to
        # self.branch_name if self_repo_name was not set (e.g. in unit tests).
        primary_branch = (
            repo_info.get(getattr(self, 'self_repo_name', None) or '', {}).get('atomic_branch')
            or repo_info.get('nvl.common', {}).get('atomic_branch')
            or self.branch_name
        )

        # Load full JSON (all repos, unfiltered)
        json_data = self._read_atomic_json(primary_branch)
        if not json_data:
            log.info('-i- ERROR: Could not load atomic JSON')
            self.errors.append('Could not load atomic JSON')
            return False

        # Build global version timeline sorted by (major, minor)
        timeline = self._build_global_timeline(json_data)

        # Collect inherited atomic PR per repo as matrix cutoff
        repo_cutoffs = {
            repo: info['inherited_atomic_pr']
            for repo, info in repo_info.items()
            if info.get('inherited_atomic_pr')
        }

        if 'nvl.common' not in repo_cutoffs:
            log.info('-i- ERROR: nvl.common has no resolvable inherited atomic PR')
            self.errors.append('nvl.common not resolvable in atomic JSON')
            return False

        # Build per-repo native version sets for ADD-compatibility filtering.
        # A version V is ADD-compatible for repo R only if V appears in R's own
        # branch JSON at or before R's cutoff (inherited_atomic_pr).
        #
        # Two separate issues are guarded against:
        #   1. Cross-branch leak: a version exclusive to main_atomic_automation.json
        #      must not be ADD-compatible for repos on main.json.
        #   2. Same-branch future leak: a version added to main.json by a PR that
        #      merged AFTER the current build's branch point (e.g. PR 1713 → 5.1
        #      landing after nvl.pcd PR 1714 branched off) must NOT be considered
        #      native — scanning all of main.json would incorrectly include it.
        #
        # Fix: only scan each repo's JSON up to and including its cutoff PR
        # (inherited_atomic_pr), stopping at the same boundary used by
        # contributed_before in _build_repo_matrix.
        repo_native_versions = {}
        # Pre-seed cache with every branch already known from the per-repo loop
        # so each repo's JSON is read at most once regardless of how many repos
        # share the same branch (e.g. all dielets on main.json).
        _json_cache = {primary_branch: json_data}
        for _r, _i in repo_info.items():
            _b = _i.get('atomic_branch')
            if _b and _b not in _json_cache:
                _json_cache[_b] = self._read_atomic_json(_b) or {}
        for repo, info in repo_info.items():
            branch = info.get('atomic_branch') or primary_branch
            if branch not in _json_cache:  # should already be pre-seeded, but guard anyway
                _json_cache[branch] = self._read_atomic_json(branch) or {}
            branch_json = _json_cache[branch]
            native = set()
            # Determine the cutoff PR for this repo (as int for comparison).
            cutoff_raw = info.get('inherited_atomic_pr')
            cutoff_pr_int = None
            if cutoff_raw is not None:
                try:
                    cutoff_pr_int = int(cutoff_raw)
                except (ValueError, TypeError):
                    pass
            # Only look at THIS repo's section up to and including the cutoff PR.
            # PRs that landed after the cutoff are unknown to this build and must
            # not contribute to the native set (same-branch future-leak guard).
            repo_data = branch_json.get(repo, {})
            past_cutoff = False
            if isinstance(repo_data, dict):
                for pr_str, ver_list in repo_data.items():
                    if past_cutoff:
                        break
                    if not pr_str.isdigit():
                        continue
                    for v in ver_list:
                        parts = v.split('.')
                        if len(parts) >= 2:
                            try:
                                native.add((int(parts[0]), int(parts[1])))
                            except ValueError:
                                pass
                    # Mark cutoff after processing this PR's versions
                    if cutoff_pr_int is not None and int(pr_str) == cutoff_pr_int:
                        past_cutoff = True
            repo_native_versions[repo] = native

        # Build compatibility matrix
        state = self._build_repo_matrix(json_data, timeline, repo_cutoffs, repo_native_versions)

        # Get anchor from nvl.common — always a single pinned value
        common_cell = state.get('nvl.common', {}).get(bit_pos)
        if not common_cell:
            log.info(f'-i- ERROR: nvl.common has no matrix entry for {bom_short} (bit {bit_pos})')
            self.errors.append(f'nvl.common has no data for {bom_short}')
            return False

        anchor = next(iter(common_cell))
        anchor_str = f'{anchor[0]}.{anchor[1]}'
        log.info(f'-i- Anchor: nvl.common pinned at {anchor_str} for {bom_short}')
        log.info('-i-')

        # Check each other repo against the anchor
        all_pass = True
        for repo in sorted(repo_cutoffs.keys()):
            if repo == 'nvl.common':
                continue
            cell = state[repo].get(bit_pos)
            if not cell:
                log.info(f'-i-   {repo:15s} SKIP  (no matrix entry for {bom_short})')
                continue
            compat_str = ', '.join(f'{v[0]}.{v[1]}' for v in sorted(cell))
            if anchor in cell:
                kind = 'pinned at' if len(cell) == 1 else 'compatible'
                log.info(f'-i-   {repo:15s} PASS  {kind} [{compat_str}]')
            else:
                log.info(f'-i-   {repo:15s} FAIL  at [{compat_str}], needs {anchor_str}')
                self.errors.append(
                    f'{repo} incompatible: at [{compat_str}], needs {anchor_str} for {bom_short}'
                )
                all_pass = False

        return all_pass

    @staticmethod
    def _read_atomic_json(branch):
        """
        Load the complete atomic JSON for the given branch (all repos, unfiltered)
        via DataHost central server.

        :param branch: Branch name (e.g. 'main', 'main_atomic_automation')
        :return: Full JSON dict, or None if file not found or error
        """
        filename = f'{AtomicRevisionManager.ATOMIC_DIR}/{branch}.json'
        try:
            return DataHost().central("read_json", filename, check=True, site='JF')
        except Exception:
            log.info(f'-i- Atomic JSON not found: {filename}')
            return None

    @staticmethod
    def _build_global_timeline(json_data):
        """
        Collect every unique atomic version event from all repos in the JSON
        and return them sorted chronologically by (major, minor).

        :param json_data: Full atomic JSON dict
        :return: List of (major, minor, bitmask_str) tuples sorted by (major, minor)
        """
        versions = {}  # (major, minor) -> bitmask_str
        for repo_key, repo_data in json_data.items():
            if repo_key == 'latest':
                continue
            if not isinstance(repo_data, dict):
                continue
            for pr_str, ver_list in repo_data.items():
                if not pr_str.isdigit():
                    continue
                for v in ver_list:
                    parts = v.split('.')
                    if len(parts) == 3:
                        key = (int(parts[0]), int(parts[1]))
                        versions[key] = parts[2]
        return [(maj, mn, versions[(maj, mn)]) for maj, mn in sorted(versions.keys())]

    @staticmethod
    def _build_repo_matrix(json_data, timeline, repo_cutoffs, repo_native_versions=None):
        """
        Build the compatibility matrix: state[repo][bit_index] -> set of (major, minor).

        For each version event in the timeline and each flagged BOM bit, the
        three-way PIN/SKIP/ADD rule is applied per repo:
          PIN  - version is a first-entry in a PR <= cutoff in JSON/merge order
          SKIP - version is a first-entry in a PR >  cutoff (not yet landed)
          ADD  - version is never a first-entry for this repo AND exists in
                 the repo's native set (versions the repo knew about at its
                 branch point).  Cross-branch and same-branch future versions
                 are both suppressed from ADD.

        :param json_data: Full atomic JSON dict (anchor branch)
        :param timeline: Sorted list of (major, minor, bitmask_str)
        :param repo_cutoffs: Dict of {repo_name: inherited_atomic_pr_number}
        :param repo_native_versions: Optional dict {repo_name: set of (major,minor)}
               representing versions from each repo's own branch JSON up to and
               including the cutoff (inherited_atomic_pr).  ADD is suppressed
               for any version absent from this set.
        :return: Dict state[repo][bit_index] = set of (major, minor) tuples
        """
        # For each repo walk JSON keys in insertion (merge) order up to and
        # including the cutoff PR, collecting first-entry versions into two sets.
        contributed_before = {}  # repo -> set of (major, minor) first-entries <= cutoff
        contributed_after = {}   # repo -> set of (major, minor) first-entries >  cutoff

        for repo, cutoff_pr in repo_cutoffs.items():
            repo_data = json_data.get(repo, {})
            before = set()
            after = set()
            past_cutoff = False
            cutoff_str = str(cutoff_pr)
            for pr_str, ver_list in repo_data.items():
                if not pr_str.isdigit():
                    continue
                first_ver = ver_list[0]
                parts = first_ver.split('.')
                if len(parts) >= 2:
                    ver_key = (int(parts[0]), int(parts[1]))
                    if not past_cutoff:
                        before.add(ver_key)
                    else:
                        after.add(ver_key)
                if pr_str == cutoff_str:
                    past_cutoff = True
            contributed_before[repo] = before
            contributed_after[repo] = after

        # Walk the timeline and apply PIN/SKIP/ADD to build the state matrix
        state = {repo: {} for repo in repo_cutoffs}
        for major, minor, bitmask_str in timeline:
            ver_key = (major, minor)
            for repo in state:
                for i, flag in enumerate(bitmask_str):
                    if flag != '1':
                        continue
                    if ver_key in contributed_before[repo]:
                        # PIN: contributed and landed — replace cell with singleton
                        state[repo][i] = {ver_key}
                    elif ver_key in contributed_after[repo]:
                        # SKIP: contributed but not yet landed — do not update cell
                        pass
                    else:
                        # ADD: never contributed — compatible only if this version
                        # exists in the repo's own branch JSON.  A version that
                        # was introduced exclusively in a different branch (e.g.
                        # main_atomic_automation) is unknown to repos on 'main'
                        # and must not be assumed backward-compatible.
                        native = repo_native_versions.get(repo) if repo_native_versions else None
                        if native is None or ver_key in native:
                            state[repo].setdefault(i, set()).add(ver_key)

        return state

    def rename_por_tp_on_failure(self):
        """
        Rename POR_TP to POR_TP_FAILED in the user-supplied output destination.

        Reads the TP_OUTPUT_PATH environment variable (set in the workflow step
        env block to ``${{ github.event.inputs.destination }}``).  If the
        variable is not set or the directory does not exist, logs a warning and
        returns without error.

        :raises OSError: If the rename fails for an unexpected filesystem reason
        """
        tp_output_path = os.environ.get('TP_OUTPUT_PATH', '').strip()
        if not tp_output_path:
            log.info('-w- TP_OUTPUT_PATH not set; skipping POR_TP rename')
            return
        por_tp = os.path.join(tp_output_path, 'POR_TP')
        por_tp_failed = os.path.join(tp_output_path, 'POR_TP_FAILED')
        if os.path.isdir(por_tp):
            os.rename(por_tp, por_tp_failed)
            log.info(f'-w- Renamed {por_tp} -> {por_tp_failed}')
        else:
            log.info(f'-w- {por_tp} not found in output path; skipping rename')

    @staticmethod
    def _gh_cmd():
        """
        Return the platform-appropriate path to the GitHub CLI binary.

        :return: gh command string
        """
        import platform
        if platform.system() == 'Windows':
            return 'gh'
        return '/usr/intel/bin/gh'

    @staticmethod
    def seed_atomic_json(branch_name):
        """
        Seed a new RC branch JSON file by copying main.json.

        Called when a new main_* branch is created via the branch_management
        GitHub Actions workflow. Ensures check_atomic_consistency has a valid
        JSON baseline from the moment the branch is cut, before any atomic PR
        lands on it.

        :param branch_name: New RC branch name (e.g. 'main_42')
        :type branch_name: str
        """
        # Source branch is controlled by BASE_REF env var (default: 'main').
        # In production BASE_REF=main; for dev/testing point it to another branch.
        source_branch = os.environ.get('BASE_REF', 'main')
        src = Env.xpath(
            os.path.join(AtomicRevisionManager.ATOMIC_DIR, f'{source_branch}.json')
        )
        dst = Env.xpath(
            os.path.join(AtomicRevisionManager.ATOMIC_DIR, f'{branch_name}.json')
        )

        if os.path.exists(dst):
            print(f'-i- JSON already exists: {dst}. Skipping seed.')
            return

        if not os.path.exists(src):
            print(f'-e- Source {source_branch}.json not found: {src}. Cannot seed.')
            sys.exit(1)

        shutil.copy2(src, dst)
        print(f'-i- Seeded {dst} from {src}')


if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv) == 2 and sys.argv[1] == 'SEED_ATOMIC_JSON':
        print('Usage: atomic_rev_check.py SEED_ATOMIC_JSON <branch_name>')
        sys.exit(1)

    if len(sys.argv) == 3 and sys.argv[1] == 'SEED_ATOMIC_JSON':
        AtomicConsistencyChecker.seed_atomic_json(sys.argv[2])
        sys.exit(0)

    if len(sys.argv) == 2:
        checker = AtomicConsistencyChecker(sys.argv[1])
        checker.main()
        sys.exit(0)
    else:
        print('Usage:')
        print('  atomic_rev_check.py <BOM_name>')
        print('    Example: atomic_rev_check.py Class_NVL_S28C')
        sys.exit(1)
