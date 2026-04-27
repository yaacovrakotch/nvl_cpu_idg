#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Procedure to add new repo (no code change needed).
1. git clone <repo> using your username in some temp folder
2. as p6vector, copy the cloned repo (step1 above) using:
   cp -pdr <source> /nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts
3. edit config.json file and put the repo path in step2
4. Test cgi make sure it works well

TODO:
Show the last PR number from git log of table.
Correct order on bundle
Redo query so it will just call twice only!
gh pr list --json number,reviews,state,isDraft -B TP/21G -s closed
gh pr list --json number,reviews,state,isDraft -B TP/21G -s open
"""
import os
import json
import time
from datetime import datetime
from gadget.shell import SystemCall
from gadget.files import File, TempName
from gadget.printmore import disp
from gadget.strmore import to_str, utc2local, curtime, workweek
from gadget.errors import confirm, ErrorUser
from gadget.lockfile import force_refresh, Lock
from gadget.getgit import GetCmd
from gadget.disk import mkdirs, Chdir
from gadget.tputil import OtplFile, get_modulename
from mod.indicators import TPBotFail
from tp.testprogram import TestProgram, Env
from main.tprobot import AtomicChange
from collections import OrderedDict, defaultdict
from os.path import basename, dirname, realpath, exists
from pprint import pprint, pformat
import re
import glob
import sys


class AtomicRevisionManager:
    """
    Manages atomic revision tracking and BOM impact analysis for PRs.
    Loads atomic version data from JSON files and provides lookup/formatting methods.
    """
    ATOMIC_DIR = '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/atomic_version_db'

    # Repo name mapping for atomic version lookups: URL format -> JSON key format
    REPO_MAP = {
        'nvlcommon': 'nvl.common',
        'nvlcpu': 'nvl.cpu',
        'nvlgcd': 'nvl.gcd',
        'nvlhub': 'nvl.hub',
        'nvlpcd': 'nvl.pcd'
    }

    # Color assignment based on atomic revision for cross-repo consistency
    # Using 8 colors for better distribution across versions
    COLORS = [
        '#E6E6FF',  # Light Purple
        '#FFFACD',  # Light Yellow
        '#FFE6F3',  # Light Pink
        '#E6FFE6',  # Light Green
        '#FFE6CC',  # Light Orange
        '#E6E6FA',  # Lavender
        '#FFE4E1',  # Misty Rose
        '#E0FFFF'   # Light Cyan
    ]

    def __init__(self, repo, base_branch, repo_map):
        """
        Initialize the atomic revision manager.

        :param repo: Repository name (e.g., 'mtlp68', 'nvlcommon')
        :param base_branch: Branch name (e.g., 'TP/37', 'main')
        :param repo_map: Dictionary mapping repo URL names to JSON keys
        """
        self.repo = repo
        self.base_branch = base_branch
        self.repo_map = repo_map
        self._atomic_json_cache = None

    def _load_atomic_json(self):
        """
        Load and cache the atomic version JSON file.
        Returns the repo_data for the current repo, or None if not found.
        """
        if self._atomic_json_cache is not None:
            return self._atomic_json_cache

        atomic_file = os.path.join(self.ATOMIC_DIR, f'{self.base_branch}.json')

        # Check if file exists
        if not os.path.exists(atomic_file):
            self._atomic_json_cache = {}
            return self._atomic_json_cache

        with open(atomic_file, 'r') as fh:
            content = fh.read()

        data = json.loads(content)

        repo_key = self.repo_map.get(self.repo, self.repo)
        self._atomic_json_cache = data.get(repo_key, {})
        return self._atomic_json_cache

    def _parse_bom_from_revisions(self, revisions):
        """
        Parse BOM flags from revision strings and return formatted atomic_rev and atomic_bom.

        :param revisions: List of revision strings in format "major.minor.bomflags"
        :return: Tuple of (formatted_atomic_rev, formatted_atomic_bom)
        """
        # Validate input is iterable
        if not isinstance(revisions, (list, tuple)):
            return '', ''

        if not revisions:
            return '', ''

        bom_names = [display_name for _, display_name in AtomicChange.BOM_MAPPING]
        formatted_revs = []
        bom_impacted_list = []

        for rev in revisions:
            parts = rev.split('.')

            # Standard format: major.minor.bomflags (3 parts)
            if len(parts) == 3:
                # Atomic revision: first 2 parts
                formatted_revs.append(f"{parts[0]}.{parts[1]}")

                # BOM flags: third part (string of 1s and 0s)
                bom_flags = parts[2]

                # Validate BOM flags format: only 1s and 0s, and at least
                # len(bom_names)-1 bits wide.  Entries shorter than that are
                # malformed anomalies (e.g. '2.0.1').  The -1 floor preserves
                # backward-compat with legacy (N-1)-bit entries written before
                # the most recent BOM was added to BOM_MAPPING.
                if not all(c in '01' for c in bom_flags) or len(bom_flags) < len(bom_names) - 1:
                    bom_impacted_list.append("NA")
                # Check if all 1s → All_BOM
                elif bom_flags == '1' * len(bom_flags):
                    bom_impacted_list.append("All_BOM")
                # Check if all 0s → NA
                elif bom_flags == '0' * len(bom_flags):
                    bom_impacted_list.append("NA")
                else:
                    # Parse each bit position and collect affected BOM names
                    affected_boms = []
                    for idx, flag in enumerate(bom_flags):
                        if flag == '1' and idx < len(bom_names):
                            affected_boms.append(bom_names[idx])

                    if affected_boms:
                        bom_impacted_list.append(', '.join(affected_boms))
                    else:
                        bom_impacted_list.append("NA")
            elif len(parts) >= 2:
                # Only major.minor, no BOM data
                formatted_revs.append(f"{parts[0]}.{parts[1]}")
            else:
                # Anomaly: unexpected format
                formatted_revs.append(rev)
                bom_impacted_list.append("NA")

        atomic_rev = ', '.join(formatted_revs)

        # Deduplicate BOM names if multiple revisions have overlapping BOMs
        unique_boms = set()
        has_all_bom = False
        for item in bom_impacted_list:
            if item == "All_BOM":
                has_all_bom = True
            elif item != "NA":
                unique_boms.update(item.split(', '))

        # Build final BOM output
        if has_all_bom:
            atomic_bom = "All_BOM"
        elif unique_boms:
            # Preserve original BOM order from BOM_MAPPING (don't sort alphabetically)
            ordered_boms = [b for b in bom_names if b in unique_boms]
            atomic_bom = ', '.join(ordered_boms)
        else:
            atomic_bom = "NA"

        return atomic_rev, atomic_bom

    def _get_atomic_info(self, pr, pr_data=None):
        """
        For a given PR identifier (string), look up atomic revision info from the branch JSON file.
        Returns (Atomic_rev, Atomic_bom_impacted) tuple.
        If not found or error, return ('', '').

        :param pr: PR number
        :param pr_data: Optional PR data dict (unused, kept for compatibility)
        """

        repo_data = self._load_atomic_json()
        if not repo_data:
            return '', ''

        pr_str = str(pr)
        if pr_str not in repo_data:
            return '', ''

        # Get list of revisions for this PR
        revisions = repo_data[pr_str]

        # Validate revisions is a list/tuple
        if not isinstance(revisions, (list, tuple)):
            return '', ''

        return self._parse_bom_from_revisions(revisions)

    def _get_initial_atomic_rev(self, closed_PR, pr_data_dict):
        """
        Find the atomic revision that should apply to PRs before the oldest displayed PR.
        This handles the case where the inflection point PR is not in the displayed range.
        Returns tuple (atomic_rev, atomic_bom) from most recent PR merged before the oldest displayed PR.
        Note: JSON data is already ordered by actual merge sequence, not PR number order.

        :param closed_PR: List of closed PR numbers
        :param pr_data_dict: Dictionary with PR data (must have 'merge_age' key)
        """

        repo_data = self._load_atomic_json()
        if not repo_data:
            return '', ''

        if not closed_PR:
            return '', ''

        # Find the oldest displayed PR by merge time (highest merge_age since higher = older)
        oldest_displayed_pr = max(
            closed_PR, key=lambda pr: pr_data_dict[pr]['merge_age'])
        oldest_merge_age = pr_data_dict[oldest_displayed_pr]['merge_age']

        # Since JSON is ordered by merge sequence, find atomic PRs that merged before display range
        # Walk through JSON entries to find most recent merge before oldest displayed PR
        most_recent_pr_str = None
        for pr_str in repo_data.keys():
            if pr_str.isdigit():
                pr_num = int(pr_str)
                # Check if this atomic PR merged before oldest displayed PR
                if pr_num in pr_data_dict:
                    # PR is in display data - use merge_age comparison
                    if pr_data_dict[pr_num].get('merge_age', 0) > oldest_merge_age:
                        most_recent_pr_str = pr_str  # JSON order ensures this is most recent
                else:
                    # PR is not in display data - assume it's older than display range
                    most_recent_pr_str = pr_str  # JSON order ensures this is most recent

        if not most_recent_pr_str:
            return '', ''

        # Get the most recent (last in merge order) PR before display range
        most_recent = (int(most_recent_pr_str), most_recent_pr_str)
        revisions = repo_data[most_recent[1]]

        # Validate revisions is a list/tuple
        if not isinstance(revisions, (list, tuple)):
            return '', ''

        return self._parse_bom_from_revisions(revisions)

    def populate_pr_atomic_data(self, pr_data_dict, closed_prs, open_prs):
        """
        Populate PR data dictionary with computed atomic revision and BOM info.
        Computes inheritance chain for merged PRs and direct lookups for open PRs.
        This is used by NVL consolidated mode to compute inheritance per-repo before combining.
        Stores '_computed_atomic_rev' and '_computed_atomic_bom' in each PR's data.

        :param pr_data_dict: Dictionary of PR data (will be modified in-place)
        :param closed_prs: List of closed/merged PR numbers
        :param open_prs: List of open PR numbers
        """
        if not closed_prs:
            return

        # Get initial atomic revision for PRs before display range
        current_atomic_rev, current_atomic_bom = self._get_initial_atomic_rev(
            closed_prs, pr_data_dict)

        # Process oldest to newest (reverse=True means highest merge_age first = oldest)
        for pr in sorted(closed_prs, key=lambda x: pr_data_dict[x]['merge_age'], reverse=True):
            atomic_rev, atomic_bom = self._get_atomic_info(pr, pr_data_dict[pr])
            if atomic_rev:
                current_atomic_rev = atomic_rev
                current_atomic_bom = atomic_bom
            # Store computed values in PR data
            pr_data_dict[pr]['_computed_atomic_rev'] = current_atomic_rev
            pr_data_dict[pr]['_computed_atomic_bom'] = current_atomic_bom

        # Also compute for open PRs (they don't inherit, just show their own)
        for pr in open_prs:
            atomic_rev, atomic_bom = self._get_atomic_info(pr, pr_data_dict[pr])
            pr_data_dict[pr]['_computed_atomic_rev'] = atomic_rev
            pr_data_dict[pr]['_computed_atomic_bom'] = atomic_bom

    @classmethod
    def get_color_for_revision(cls, atomic_rev):
        """Get consistent color for atomic revision across all repos"""
        if not atomic_rev:
            return cls.COLORS[0]  # Default to blue if no revision

        # Handle multiple revisions (e.g., "2.0, 2.1") - use the highest one
        revisions = [rev.strip() for rev in atomic_rev.split(',')]

        try:
            # Find the highest revision by comparing as version numbers
            highest_rev = None
            highest_value = -1

            for rev in revisions:
                parts = rev.split('.')
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    # Convert "major.minor" to single number for comparison
                    version_value = int(parts[0]) * 10 + int(parts[1])
                    if version_value > highest_value:
                        highest_value = version_value
                        highest_rev = rev

            if highest_rev:
                # Use both major and minor for color assignment
                # With 8 colors, pattern repeats every 4 major versions
                parts = highest_rev.split('.')
                major, minor = int(parts[0]), int(parts[1])
                # Formula: major*2 + minor gives good distribution
                # 1.0->2, 1.1->3, 2.0->4, 2.1->5, 3.0->6, 3.1->7, 4.0->0, 4.1->1
                color_index = (major * 2 + minor) % len(cls.COLORS)
                return cls.COLORS[color_index]
        except (ValueError, IndexError):
            pass

        return cls.COLORS[0]  # Default to blue if parsing fails


class DivHide:
    """Create a div wrapper and hide it at end"""

    def __init__(self, default='', pre=False):
        self.default = f'status{default}'
        self.pre = pre

    def __enter__(self):
        """Executed upon entry to with block"""
        print(f'<div id="{self.default}">')
        if self.pre:
            print('<pre>')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Executed upon closure of with block"""
        self.close()

    def close(self):
        """closure code - Hide the status"""
        if self.pre:
            print('</pre>')
        print(f"""
</div>
<script>
    var myDiv = document.getElementById("{self.default}");
    myDiv.style.display = "none";
</script>
        """)


class CCI:

    """CCI PR report"""
    tag_cache_dir = '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/tag_cache'
    configjson = '/p/pde/tvpv/tvpvweb/cgi-bin/pr-report/config2.json'   # see docstring for setup instructions
    CGINAME = 'cci_list.cgi' if not sys.argv[0].endswith('_beta.cgi') else 'cci_list_beta.cgi'
    URL = f'https://tvpv.pdx.intel.com/cgi-bin/pr-report/{CGINAME}'
    OPT = {}    # assigned by cgi

    def __init__(self, base_branch, rows, prtype=None, repo=None, disp=True):
        """
        :param base_branch: TP/37
        """
        self.base_branch = base_branch
        self.rows = rows
        self.prtype = prtype

        # main dictionary
        # {PRNO: {'openclose': 'draft|open|closed|merged',
        #         'approved': 'Approved|Need_Review',  # This field is optional, for open only
        #         'merge_age': seconds,
        #         'update_age': seconds,
        #         'labels': set_of_labels,
        #         'title': string,
        #         '<gh_output_attribute>': <value>
        self.data = None

        self.repo = repo if repo else 'mtlp68'    # default
        self.isdisp = disp
        self.cfg = None     # configuration dictionary. Set in read_config()

        # Initialize atomic revision manager for this repo
        self.atomic_mgr = AtomicRevisionManager(self.repo, self.base_branch, AtomicRevisionManager.REPO_MAP)

    def _precompute_atomic_info(self):
        """
        Pre-compute atomic revision info for all merged PRs and store in PR data.
        This is used by NVL consolidated mode to compute inheritance per-repo before combining.
        Stores '_computed_atomic_rev' and '_computed_atomic_bom' in each PR's data.
        """
        closed_PR = list(self.get_prs('merged'))
        open_PR = list(self.get_prs('open'))

        self.atomic_mgr.populate_pr_atomic_data(self.data, closed_PR, open_PR)

    def main_init(self):
        """Initialize self.data"""
        self._set_all_pr()
        self._set_tags_list()
        self._set_open_close()
        self._set_approved()
        # self._check_valid_branch()

    def disp_status(self, msg):
        """Display status if set"""
        if self.isdisp:
            print(f'{msg}<br>')

    def _check_valid_branch(self):      # pragma: no cover  - under development
        """
        Check if base_branch is valid, and display valid branches (and show also the last commit on RC branch)
        This require a repo that is up-to-date (git pull)

        :return:
        """
        if self.data:
            return    # good to go

        # check if base branch is valid
        _, out, serr = SystemCall('git branch -al').run_sout_serr()
        if f'origin/{self.base_branch}' in out:
            return     # valid

        print(f"Error: {self.base_branch} is not a valid branch name.<br>")
        exit(1)

    def _get_draft(self):
        """
        Return dictionary set of PR number that is draft
        :return:
        """
        self.disp_status("Reading drafts")
        cmd = f"/usr/intel/bin/gh pr list -L {self.rows} -B {self.base_branch} -s open"
        with TempName(name=True) as fname:
            SystemCall(cmd).run_outfile(fname)
            with open(fname, 'rb') as fh:
                data = to_str(fh.read())     # So that unicode are ignored

        result = set()
        for line in data.split('\n'):
            if line.strip().endswith('DRAFT'):
                result.add(int(line.split()[0]))
        return result

    def _set_approved(self):
        """
        Set the approved field
        :return:
        """
        self.disp_status(f"Getting all open PRs")
        for item in self._call_pr_list('open', fields='number,reviews'):
            pr = item['number']
            result = 'Need_Review'
            for review in item.get('reviews', []):
                if review.get('state') == 'APPROVED':
                    result = 'Approved'
            if pr in self.data:
                self.data[pr]['approved'] = result

    def _call_pr_list(self, prtype, fields='mergedAt,number,title,author,labels,closed,url,updatedAt,body'):
        """
        Call gh pr list
        Note: This is sorted according to PR number. If there is a PR that is old but recently merged,
        it may not show up if number of rows is small enough.

        :param prtype: open|all|merged
        :return: list
        """
        if self.OPT.get('PR_CNT') == 'DETAIL':      # pragma: no cover - used in PR_CNT only
            fields = f'{fields},changedFiles'
        if self.OPT.get('milestone'):
            fields = f'{fields},milestone'
        with TempName(name=True) as fname:
            cmd = (f"/usr/intel/bin/gh pr list -s {prtype} -B {self.base_branch} -L {self.rows} "
                   f"--json {fields}")
            SystemCall(cmd).run_outfile(fname)
            with open(fname, 'rb') as fh:
                try:
                    return json.loads(fh.read())
                except json.decoder.JSONDecodeError:
                    return []    # on cases of failure

    def _set_all_pr(self):
        """
        return dictionary (ordered): {pr#: {data}}

        :return: dictionary
        """
        result = OrderedDict()    # So that order is maintained
        curtime = self.get_curtime()

        self.disp_status(f"Getting all PR's {self.repo}")
        if self.prtype is None:
            data_json = self._call_pr_list('open')
        else:
            data_json = self._call_pr_list(self.prtype)

        # do with everything
        if self.prtype is None:
            tmp_json = self._call_pr_list('merged')
            data_json.extend(tmp_json)

        # Uncomment below to create testcase using real data
        # File('/nfs/pdx/disks/mpe_mtl_015/mtl/unittests/cci_pr/new_case.json').write(json.dumps(data_json, indent=3))

        for item in data_json:

            # redo labels
            labels = {x['name'] for x in item['labels']}
            item['_orig_labels'] = item['labels']
            item['labels'] = labels   # replace it

            # Add merge_age and update_age
            if 'mergedAt' in item and item['mergedAt']:
                item['merge_age'] = curtime - utc2local(item['mergedAt']).timestamp()
            item['update_age'] = curtime - utc2local(item['updatedAt']).timestamp()
            pr = item['number']

            result[pr] = item

        # assign
        self.data = result

    def _set_tags_list(self):
        """Getting the tag from the github and set it to the PR data."""
        list_tag = []
        tag_branch = self.cfg.get('tagstart', 'TP_')
        self.disp_status(f"Getting tag list...")
        with TempName(name=True) as fname:
            cmd = f'git tag --list \'{tag_branch}*\' --format \'%(refname:short) %(objectname) %(subject)\''
            SystemCall(cmd).run_outfile(fname)
            with open(fname, 'r') as fh:
                fline = fh.readlines()
            for line in fline:
                tag = self._get_tag_prno(line.strip())
                list_tag.append(tag)

        return list_tag   # unittest only

    def _add_tag(self, prno, tag):
        """Add the tag in self.data"""
        if 'tags' in self.data[prno]:
            self.data[prno]['tags'] += f'<br>{tag}'
        else:
            self.data[prno]['tags'] = tag

    def _get_tag_prno(self, line):
        """Get the tag from line and assign the prno"""
        if not line:
            return None

        tag = line.split()[0]
        found = False
        for prno in re.findall(r'#(\d+)', line):
            if int(prno) in self.data:
                self._add_tag(int(prno), tag)
            found = True

        if not found:
            # Try cache area
            tpath = f'{self.tag_cache_dir}/{self.repo}/{tag.replace("/", "_")}'
            if os.path.exists(tpath):
                found = True
                iprno = int(File(tpath).read().strip())
                if iprno in self.data:
                    self.disp_status(f'Found {tag} in {tpath} \n')
                    self._add_tag(iprno, tag)
                    return tag
            else:
                # Try looking for tag in log file
                cmd = f'git log {tag} -n 5'
                self.disp_status(f'{cmd}')

                with TempName(name=True) as fname:
                    SystemCall(cmd).run_outfile(fname)
                    with open(fname, 'rb') as fh:
                        tline = to_str(fh.read())     # So that unicode are ignored

                for prno in re.findall(r'#(\d+)', tline):
                    found = True
                    if int(prno) in self.data:
                        self._add_tag(int(prno), tag)
                        File(tpath).touch(prno, mkdir=True)    # Save to cache
                        return tag    # First one

        if not found:
            self.disp_status(f'tag={tag} has no pr-number. Pls manually assign pr-number in {tpath}')

        return tag

    def _set_open_close(self):
        """
        Set the openclose attribute: draft|open|closed|merged
        :return:
        """
        pr_draft = self._get_draft()

        for pr in self.data:
            if self.data[pr]['mergedAt'] is None:
                if not self.data[pr]['closed']:
                    if self.data[pr]['number'] in pr_draft:
                        # disp(f'draft: {pr}')
                        self.data[pr]['openclose'] = 'draft'
                    else:
                        self.data[pr]['openclose'] = 'open'
                else:
                    # disp(f'closed: {pr}')
                    self.data[pr]['openclose'] = 'closed'
            else:
                self.data[pr]['openclose'] = 'merged'

            confirm('openclose' in self.data[pr],
                    f'Missing openclose status for {pr}',
                    'set_open_close() algo error! contact jqdelosr.')

    def get_prs(self, state):
        """
        :param state: Either draft|open|closed|merged
        :return:
        """
        confirm(state in 'draft open closed merged'.split(),
                f'Invalid input: {state}', 'Fix input')
        for pr in self.data:
            if self.data[pr]['openclose'] == state:
                yield pr

    @classmethod
    def get_curtime(cls):
        """For unitest"""
        return time.time()

    def read_config(self, valid_list=False, repopath=None):
        """
        Set config

        :param: valid_list: Set to True to return entire data (all repos) instead of just one target repo data
        :return: unittest code only
        """
        if self.cfg:
            return 0    # Do nothing, it is already set

        if repopath:     # special - command line, current directory
            self.cfg = {"repopath": ".", "email": "adhoc@intel.com"}

            # make sure proxy is set to gh will work
            confirm('https_proxy' in os.environ,
                    'https_proxy is not set',
                    'source /intel/engineering/dev/team_classtp/torch/ctp_runner/proxy.cshrc')
            # make sure cwd is a repo
            confirm(os.path.isdir('.git'),
                    f'cwd is not a git repo: {os.getcwd()}',
                    'Make sure cwd is a git repo')
            return 2

        if not exists(self.configjson):
            self.configjson = self.configjson.replace('cgi-bin', 'cgi')    # idc non-standard

        with open(self.configjson) as fh:
            data = json.load(fh)
        if valid_list:
            return data
        if self.repo not in data:
            print('Error: %s is not valid repo. Valid are: <br>\n%s' %
                  (self.repo, '<br>\n'.join(sorted(data))))
            exit(1)

        self.cfg = data[self.repo]
        return 1

    def set_chdir(self):
        """Chdir to the repo. Note: Repo must be owned by p6vector since web is p6vector"""
        if exists(self.cfg['repopath']):
            os.chdir(self.cfg['repopath'])

    @classmethod
    def main_set_ready(cls, pr, repo='mtlp68'):      # pragma: no cover  - will test later
        """
        Add the ready label given pr number

        :param pr: number
        :param repo: repo
        :return:
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic'}
        proxy = {'http': '', 'https': ''}
        response = requests.get(f'https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?repo={repo}&br={pr}',
                                headers=headers, proxies=proxy, verify=False)
        print(f'Status: {response.status_code}')
        print(response.text)
        return response

    def _git_pull(self, submodule=False, interval=2 * 3600):
        """Do a git pull once every 2 hours"""
        cwd = os.getcwd()
        age = os.path.getmtime(cwd)
        if (time.time() - age) > interval or self.OPT.get('pull'):
            Lock.newline = '<br>'
            self.disp_status(f'Please wait... {self.repo}')
            with Lock(f'{cwd}/lock.txt', timeout=10 * 60, maxlocktime=5 * 60):
                self.disp_status('Performing git pull to get tags.')
                force_refresh(cwd)

                if submodule:
                    cmd = f"/usr/intel/pkgs/git/2.23.0/bin/git submodule update --init --recursive"
                    self.disp_status(cmd)
                    for line in SystemCall(cmd).run_stream():
                        self.disp_status(line)

                cmd = f"/usr/intel/pkgs/git/2.23.0/bin/git pull"
                for line in SystemCall(cmd).run_stream():
                    self.disp_status(line)

                cmd = f"/usr/intel/pkgs/git/2.23.0/bin/git fetch --tags --force"
                for line in SystemCall(cmd).run_stream():
                    self.disp_status(line)

                return 1

        return 0

    def _process_bundle(self):
        """Update self.data for bundle PR, force PASSED_Si so it does not show as manual"""
        for pr in self.get_prs('merged'):
            title = self.data[pr]['title']
            if title.startswith('bundle of'):
                _, prs = title.split(':')
                for bundle in prs.strip().split():
                    bno = int(bundle)
                    if bno in self.data:
                        # so that bundle will not show manual
                        self.data[bno]['labels'].add('PASSED_Si')
                        # So that child PR will go before bundle
                        self.data[bno]['merge_age'] = self.data[pr]['merge_age'] + 1

    def _ready_add(self):     # pragma: no cover  - will test later
        """
        Independent routine to add label via request call
        Usage: https://tvpv1.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=2451
        """
        if not self.base_branch.isdigit():       # base_branch is the cgi url input which is the pr number
            return

        pr_number = self.base_branch
        cmd = f"/usr/intel/bin/gh pr edit {pr_number} --remove-label READY"
        res1 = SystemCall(cmd).run_sout_serr()
        cmd = f"/usr/intel/bin/gh pr edit {pr_number} --add-label READY"
        res2 = SystemCall(cmd).run_sout_serr()
        print(f'{res1}<br>')
        print(f'{res2}<br>')
        print("Success!")
        exit(0)

    def _manual_status(self, labels):
        """
        :param labels: list of labels
        :return: manual status string
        """
        failtag = set()

        # determine manual
        manual = ' Manual'   # Default Manual
        if 'PASSED_Si' in labels:
            manual = ''      # Bot passed
        if 'I_AM_TPI_Skip_Bot' in labels:
            manual = ' BotSkip'
            failtag.add('BotSkip')

        # Based on FAILED and tprobot
        newmethod = False
        for label in labels:
            if 'tprobot_' in label:
                newmethod = True
            if label.startswith('FAILED_'):
                bom = label.replace('FAILED_', '')[:-1]
                if f'tprobot_{bom}' not in labels:
                    labelx = label.replace('FAILED_', 'FAIL_')
                    failtag.add(labelx)

        if newmethod:
            if failtag:
                manual = ' Manual,%s' % ','.join(sorted(failtag))
            else:
                manual = ''    # passing

        return manual

    def _diebins_status(self,
                        body,
                        milestone={}):    # dictionary with 'title' key
        if '### Why is this PR' in body:
            return self._diebins_status_nvl(body, milestone)
        else:
            return self._diebins_status_arl(body, milestone)

    def _diebins_status_nvl(self,
                            body,
                            milestone={}):    # dictionary with 'title' key
        """
        Returns the diebins string, based on PR description - nvl style
        The answer is on a separate line
        """
        # Die first
        final = []
        start = False
        for line in body.split('\n'):
            if line.startswith('### Which Die is'):
                start = True
                continue
            elif line.startswith('### '):
                start = False

            if start:
                if line.startswith('- [ ]'):
                    continue    # unchecked line
                if line.startswith('- ['):
                    final.append(line.split()[-1])   # get last element

        # special - if all die are affected
        if final == 'CPU GCD HUB PCD'.split():
            final = ['ALL']

        # bin next
        start = False
        for line in body.split('\n'):
            if line.startswith('### What Bin'):
                start = True
                continue
            elif line.startswith('### '):
                start = False

            if start:
                if line.startswith(('_List', 'e.g.')):
                    continue
                elif not line.strip():
                    continue    # empty
                final.append(line.replace(' ', '').strip()[:7])       # first 7 chars, no spaces, max 2 bins

        if milestone:
            final.append(milestone.get('title', ''))

        return ', '.join(final)

    def _diebins_status_arl(self,
                            body,
                            milestone={},    # dictionary with 'title' key
                            _r1=re.compile(r'Which Die is affected(.*?)\?(.*)', re.DOTALL),
                            _r2=re.compile(r'What Bin\S+ are affected(.*?)\?(.*)', re.DOTALL)
                            ):
        """
        Returns the diebins string, based on PR description - mtl/arl style
        The answer can be on the same line as question
        """
        final = []

        # Die
        res = _r1.search(body)
        if res:
            for line in res.group(2).split('\n'):
                line = line.strip()
                if not line:
                    continue
                if '?' in line:
                    break    # answer was not specified
                final.append(line.split()[0].strip()[:5])      # first 5 chars, no spaces
                break

        # bin
        res = _r2.search(body)
        if res:
            for line in res.group(2).split('\n'):
                line = line.strip()
                if not line:
                    continue
                if '?' in line:
                    break    # answer was not specified
                final.append(line.replace(' ', '').strip()[:7])       # first 7 chars, no spaces, max 2 bins
                break

        if milestone:
            final.append(milestone.get('title', ''))

        return ', '.join(final)

    def _title(self, title, labels,
               _ro=re.compile('(PORTP|Uservar|ProgramFlows|BinDefinitions|Env|TPConfig|Misc|Shared)')):
        """Returns the title, max of 80 chars, with additional info from labels"""
        info = set()
        for label in labels:
            if _ro.search(label):
                info.add(label.split('_')[0][:4])

        if info:
            final = ','.join(sorted(info))
            title = title[:80 - 3 - len(final)]
            return f'{title} [{final}]'

        title = title[:80]
        return title   # as-is

    def _module_status(self,
                       labels,
                       _ro=re.compile('(PORTP|Uservar|ProgramFlows|BinDefinitions|Env|TPConfig|Misc|Shared|'
                                      r"BUNDLE|BOMCNT\d+|FAILED|READY|PASSED|TEST_IN_PROGRESS|I_AM_TPI_Skip_Bot)")):
        """Returns the module column based on labels"""

        team = set()
        for label in labels:
            if _ro.search(label):
                continue
            if label.startswith('FB'):
                continue
            element = label.split('_')[0]
            if element == 'I':
                continue
            team.add(element[:4])

        # max of 3
        if len(team) > 3:
            final = sorted(team)[:3]
            final.append(f'+{len(team)-3}')
        else:
            final = sorted(team)

        return ','.join(final)

    def _label_status(self, status, labels):
        """Update status given labels"""
        passed = set()
        expect = 1
        for label in sorted(labels):
            # partial string matches
            if 'FAILED' in label or 'READY' in label or label.startswith('FB'):
                status.append(label)

            # exact string matches
            if label in ('TEST_IN_PROGRESS', 'PASSED_Si'):
                status.append(label)
                continue

            # renamed labels
            if label == 'I_AM_TPI_Skip_Bot':
                status.append('BotSkip')

            # passed
            if label.startswith('PASSED_'):
                passed.add(label)

            if label.startswith('BOMCNT'):
                expect = int(label.replace('BOMCNT', ''))

        if len(passed) == expect:
            pass
        elif len(passed) == 0:
            status.append('Missing_Chk')
        else:
            status.append('Partial_Chk')

    def _pr_cnt(self, cmd_prcnt):        # pragma: no cover - later. main()
        """
        PR_CNT=True
        Raw data (.csv) for excel plot: pr count per tp
        """
        if not self.OPT.get('PR_CNT'):
            return
        if cmd_prcnt:
            return
        from gadget.getgit import GitHub
        if not self.base_branch.isdigit():
            print('<pre>Error! br must be br=tp_series_number</pre>')
            exit(0)
        if not self.OPT['PR_CNT'] in ('SUM', 'DETAIL', 'TEAM'):
            print('<pre>Error! PR_CNT must either be SUM|DETAIL|TEAM</pre>')
            exit(0)

        # get all branches, including RC branches
        with DivHide('a'):
            self._git_pull()

        with DivHide('b', pre=True):
            ver = self.base_branch
            allbr = []
            for br in sorted(GitHub.get_all_branches()):
                if re.search(f'^(TP/|TP/RC_){ver}', br):
                    allbr.append(br)

        results = []
        for idx, br in enumerate(allbr):
            with DivHide(idx, pre=True):
                self.disp_status(f'Processing {br}: {idx} of {len(allbr)-1}:')
                cci = CCI(br, 10000, repo=self.repo)      # This works given one branch
                head, res = cci.main(cmd_prcnt=self.OPT['PR_CNT'])
                results.extend(res)

        # Display result
        print('<pre>')
        print(head)
        print('\n'.join(sorted(results, key=lambda x: x.split()[1])))
        print('</pre>')
        exit(0)

    def _pr_age(self):      # pragma: no cover  - coverage fail
        """
        PR_AGE=True
        Raw data (.csv) for excel plot: pr age or pr count
        """
        if not self.OPT.get('PR_AGE'):
            return

        _, out = SystemCall(GetCmd.exe(f'gh pr list -B {self.base_branch} --json mergedAt,number,createdAt,changedFiles -L 10000 -s merged')).run_outtxt()
        data = json.loads(out)
        print('<pre>')
        print('pr#,age_in_secs,merge_date,ww,changedFiles')
        for item in data:
            mergeat = utc2local(item['mergedAt'], is_secs=True)
            age = mergeat - utc2local(item['createdAt'], is_secs=True)
            deyt = curtime(seconds=mergeat, dateonly=True)
            print('%s,%s,%s,%s,%s' % (item['number'], age, deyt, workweek(secs=mergeat)[:-2], item['changedFiles']))
        print("</pre>")
        exit(0)

    def _evg(self):
        """Display prime status"""
        if not self.OPT.get('evg'):
            return

        is_detail = bool(self.OPT['evg'] == 'detail')

        with DivHide():
            self._git_pull(submodule=True)
            print(f'cwd: {os.getcwd()}')

        env = glob.glob('POR_TP/*/*.env')
        confirm(len(env) > 0, f'Expecting one env: {env}', f'Check {os.getcwd()}')
        tp = TestProgram(sorted(env)[0])
        d_evg = defaultdict(int)
        d_prime = defaultdict(int)
        l_all = []
        for mtpl in tp.get_all_mtpl_from_stpl():
            mod = get_modulename(mtpl)
            for lno, line in OtplFile(mtpl).readline():
                if not line.startswith(('Test ', 'TrialTest ', 'CSharpTest ', 'CSharpTrialTest ')):
                    continue
                tokens = line.split()
                template = tokens[1]
                tname = tokens[2]
                if template.startswith(('iC', 'OASIS_code')):
                    d_evg[mod] += 1
                    l_all.append(('EVG', template, mod, tname))
                else:
                    d_prime[mod] += 1
                    l_all.append(('Prime', template, mod, tname))

        print('<pre>')
        if is_detail:
            print('Type,Template,Module,tname')
            for item in sorted(l_all):
                print('%s,%s,%s,%s' % item)

        else:
            print('Module,EVG_count,Prime_count,Total')
            for item in sorted(d_evg.keys() | d_prime.keys()):
                print('%s,%s,%s,%s' % (item, d_evg[item], d_prime[item], d_evg[item] + d_prime[item]))
        print('</pre>')
        exit(0)

    def _sr(self):      # pragma: no cover - later. SuccessRate is fully unittested
        """Build success rate"""
        robot = self.OPT.get('sr')
        if not robot:
            return

        if robot == 'checkers':
            CheckerRate().main()
        else:
            SuccessRate(robot).main()
        exit(0)

    def _tpbotreport(self):      # pragma: no cover - later. SuccessRate is fully unittested
        """tpbot fail report"""
        robot = self.OPT.get('tbr')
        if not robot:
            return

        SuccessRate(robot).weekly()
        exit(0)

    def _viewlog(self):
        """Build success rate - look at checkers/ folder"""
        path = self.OPT.get('viewlog')
        if not path:
            return
        print('<pre>')
        print(File(f'{SuccessRate.LOGDIR}/{path}', autofind=True).read())
        print('</pre>')
        exit(0)

    def _viewlog2(self):
        """tester logs viewer"""
        path = self.OPT.get('viewlog2')
        if not path:
            return
        print('<pre>')
        print(File(f'{TPBotFail.TESTERLOGS}/{path}', autofind=True).read())
        print('</pre>')
        exit(0)

    def _tpbotsubmit(self):
        """tpbotfail submit page"""
        arg = self.OPT.get('botfailsubmit')
        if not arg:
            return

        dispo = self.OPT.get('dispo')
        comment = self.OPT.get('comment', '')
        user = self.OPT.get('_user')

        # Write the json
        newname = TPBotFail().write_dispo(fname=arg,
                                          comment=comment,
                                          dispo=dispo,
                                          user=user)

        # print status, receipt
        print(f'''
<html>
    <head><title>TPBOT Fail Dispo Receipt page</title></head>
<body>
<pre>
TPBot Fail Type is updated. Thank you.
   Disposition: {dispo} Fail
   Comment:     {comment}
   User:        {user}
   Status File: {newname}
</pre>
</body>
</html>
        ''')
        exit(0)

    def _tpbotfail(self):
        """tpbotfail disposition page"""
        arg = self.OPT.get('tpbotfail')
        if not arg:
            return
        repo = self.OPT.get('repo')
        dispo = self.OPT.get('dispo')
        confirm(dispo, 'dispo=<value> is required for tpbotfail', 'Contact jqdelosr', cls=ErrorUser)
        with open(f'{TPBotFail.ROOTDB}/{arg}') as fh:
            data = json.load(fh)
        text = File(Env.xpath(data['logpath']), autofind=True).read()

        print(f'''
<html>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <head>
        <title>TPBOT Fail Disposition</title>
    </head>
<body>
    <form action="{basename(sys.argv[0])}" method="get" target="_self">

    <!-- Hidden input arg input -->
    <input type="hidden" name="dispo" value="{dispo}">
    <input type="hidden" name="botfailsubmit" value="{arg}">
    <input type="hidden" name="repo" value="{repo}">
    <input type="hidden" name="br" value="x">

    <a id="top"></a>
    <table>
    <tr>
    <td align="left">Disposition:</td><td>{dispo} Fail</td>
    </tr>
    <tr>
        <td align="left">
        Short comment:
        </td>
        <td align="right">
            <input name='comment' id='comment' type="text" value="" title="Enter Comment" class="comment"
                    onFocus="window.status='Enter comment, press enter/Submit';return true"
                    style="width: 600px;"/>
        </td>
    </tr>
    <tr>
        <td></td>
        <td align="left">
            <input type="submit" value="Submit" class="submit" />
        </td>
    </tr>
    </table>

    <br>
    <br>
    File: {basename(data['logpath'])}<br>
    <a href="#bottom">Goto Bottom of page</a>
    <pre>{text}</pre>

    <a id="bottom"></a>
    <a href="#top">Goto top of page to disposition.</a>
</body>
</html>
''')
        exit(0)

    def tpbot_fails(self, stylerow, headerstyle):
        """Return the table html for tpbot fails"""
        # get tpbot open fail count
        faillist = TPBotFail().get_list(self.repo)
        if not faillist:
            return ''   # do nothing

        # return ''     # forced - not yet deployed

        # get common url so we can just append prno. Also, most pr is not in self.data anymore
        urlrepo = ''
        for xprno in self.data:
            urlrepo = self.data[xprno]['url'].replace(f'/{xprno}', '')

        # tpbot fails ==============================================
        table = f"{stylerow}TPBot Fails: {len(faillist)}</td></tr>\n"
        table += f"{headerstyle}\n"
        table += f"""
        <td>PR #</td>
        <td>PR Title of TPBOT fail</td>
        <td>Dispo &darr;</td>
        <td>Dispo &darr;</td>
        <td>Dispo &darr;</td>
        <td>Submitted By</td>
        <td>Fail date</td>
        </tr>\n"""

        # data  data[pr]['url']
        for item in faillist:
            pr = item['prno']
            filename = item['filename']
            logpath = item['logpath']
            timesec = item['time']
            url = f'{self.URL}?br=x&tpbotfail={filename}&repo={self.OPT.get("repo")}'
            url2 = f'{self.URL}?br=x&viewlog2=./{basename(dirname(logpath))}/{(basename(logpath))}'
            age = f'{(time.time()-timesec)/86400:.1f} days ago, {curtime(timesec, human="True")}'
            title = item['title']
            author = item['author'][:20]

            table += f"""<tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                    <td>{pr}</td>
                    <td><a href='{urlrepo}/{pr}'>{title}</a></td>
                    <td><a href='{url}&dispo=MV'>MV Fail</a></td>
                    <td><a href='{url}&dispo=TRUE'>TRUE Fail</a></td>
                    <td><a href='{url}&dispo=SETUP'>SETUP Fail</a></td>
                    <td>{author}</td>
                    <td><a href='{url2}'>{age}</a></td>
                </tr>\n"""

        return table

    def _common(self):       # pragma: no cover    # dev only
        """Display the table for all the dielets"""
        if not self.OPT.get('common'):
            return

        with DivHide():
            cmd = f'/usr/intel/bin/gh pr list -B {self.base_branch} --json mergedAt,number,title,createdAt,body -L 1000 -s merged'
            print(f"Pls wait, running: {cmd}")
            code, out, err = SystemCall(cmd).run_sout_serr()

        data = json.loads(out)
        result = {}   # {ww: (total, partial dielet cnt, 4 dielet cnt)}
        detail = defaultdict(list)   # {ww: <list>}

        for _, item in enumerate(sorted(data, key=lambda x: x['createdAt'], reverse=True)):

            # get ww
            ww = workweek(date=item['createdAt'][:10])[:9]
            wwfull = workweek(date=item['createdAt'][:10])
            if ww not in result:
                result[ww] = [0, 0, 0]

            result[ww][0] += 1    # this PR

            # type1
            body = item['body']
            res = re.findall(' BRANCH:', body, re.MULTILINE)

            if ' BRANCH:' in body:
                if len(res) == 4:
                    result[ww][2] += 1     # all dielets affected
                else:
                    result[ww][1] += 1     # partial dielet affected

                detail[wwfull].append(f'cnt={len(res)} pr={item["number"]:4d} title={item["title"]}')
                # print(ww, item['createdAt'][:10], 'cnt=', len(res), "pr=", item['number'], item['title'])

        print('<pre>')
        print('Workweek, Total, Partial, AllDielet')
        for ww in sorted(result):
            print('%s, %4d, %4d, %4d' % (ww, result[ww][0], result[ww][1], result[ww][2]))

        print('Workweek, Total, Partial, AllDielet')
        print()

        for ww in sorted(detail, reverse=True):
            for line in detail[ww]:
                print(ww, line)

        print('</pre>')
        exit(0)

    def _nvl(self):
        """Display the table for all the dielets"""
        if not self.OPT.get('nvl'):
            return

        # So it is not cyclic
        self.OPT['nvl'] = None

        # mapping
        rmap = {'nvlcommon': 'S',
                'nvlcpu': 'C',
                'nvlgcd': 'G',
                'nvlhub': 'H',
                'nvlpcd': 'P'}

        alldata = {}
        for repo in rmap:
            obj = CCI(self.base_branch, self.OPT.get('rows', 50), repo=repo)
            obj.main(noprint=repo)

            # Pre-compute atomic info for this repo's PRs before combining
            obj._precompute_atomic_info()

            # put in alldata with pre-computed atomic info
            for k in obj.data:
                alldata[f'{rmap[repo]}{k}'] = obj.data[k]

        # print it
        obj.data = alldata
        obj.repo = 'nvl'
        obj._allrepo_mode = True  # Flag to use pre-computed atomic info
        obj.print_table()
        exit(0)

    def _help(self):
        """Help if no args provided"""
        if self.base_branch:
            return

        repo_list = '\n   '.join(sorted(self.read_config(valid_list=True)))
        print(f"""<pre>
cci_list.cgi?br=TP/tprev is required in url argument.

Options:
   repo=(reponame, see below for valid list)
   rows=(int, number of rows, default=50)
   pull=True          # Set to True to refresh repo, specially for newer tags
   PR_AGE=True        # Set to True to display raw data .csv PR age or PR count for excel plot
   PR_CNT=SUM|DETAIL|TEAM  # Set to TP Series to display raw data .csv of PR per testprogram (includes RC)
   evg=True           # Set to True to display evg template usage
   milestone=True     # Query milestone on normal PR report and print in Die,Bins column
   sr=(tprobot_name)  # Show tprobot success rate
   sr=checkers        # Show checker rate
   tz=16              # Set timezone to PG
   viewlog=(path)     # display contents of this file from log area
   common=True        # display common PR report per week (given br=main&repo=nvlcommon)
   tbr=(tprobot_name) # display tpbot weekly report
   nvl=True           # Consolidated nvl report. Does not need repo=(value)

Valid repo values:
   {repo_list}

</pre>""")
        exit(0)

    def main(self, cmd_prcnt=None, noprint=''):    # set cmd_prcnt='.'
        """Main entry point"""
        self._help()
        self.read_config(repopath=cmd_prcnt)
        self.set_chdir()
        self._pr_cnt(cmd_prcnt)   # independent routine
        self._ready_add()         # independent routine
        self._pr_age()            # independent routine
        self._evg()               # independent routine
        self._sr()                # independent routine
        self._tpbotreport()       # independent routine
        self._tpbotsubmit()       # independent routine
        self._tpbotfail()         # independent routine
        self._viewlog()           # independent routine
        self._viewlog2()          # independent routine
        self._nvl()               # independent routine
        self._common()            # independent routine

        with DivHide(noprint):
            self._git_pull()
            self.main_init()        # get all PR, set all attributes
            self._process_bundle()

        if noprint:
            return

        return self.print_table(cmd_prcnt)

    def print_table(self, cmd_prcnt=None):
        """Print the table"""
        data = self.data

        # Table ==============================
        today = datetime.now()
        header1 = f'{self.repo} {self.base_branch} CCI Report Status {today}'
        headerstyle = "<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>"
        stylerow = f"<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'>"
        table = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"
        table += f"<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'><pre>{header1}</pre></td></tr>"

        header = f"""
        <td>PR #</td>
        <td>Title</td>
        <td>Tags</td>
        <td><a href="https://wiki.ith.intel.com/x/zA_syQ" target="_blank">Atomic_rev</a></td>
        <td>Atomic_bom_impacted</td>
        <td>Submitted By</td>
        <td>Merged At</td>
        </tr>\n"""

        table += self.tpbot_fails(stylerow, headerstyle)

        # OPEN PR ==============================================
        open_PR = list(self.get_prs('open'))
        table += f"{stylerow}Total Open PRs: {len(open_PR)} </td></tr>\n"
        table += f"{headerstyle}\n"
        table += f"{header.replace('Merged At', 'Status')}\n"
        for pr in sorted(open_PR, key=lambda x: data[x]['update_age']):
            title = self._title(data[pr]['title'], data[pr]['labels'])
            owner = data[pr]['author']['login'][:20]
            url = data[pr]['url']
            tag = data[pr].get('tags', ' ')

            # Use pre-computed values in NVL mode, otherwise compute
            if getattr(self, '_allrepo_mode', False):
                atomic_rev = data[pr].get('_computed_atomic_rev', '')
                atomic_bom_impacted = data[pr].get('_computed_atomic_bom', '')
            else:
                atomic_rev, atomic_bom_impacted = self.atomic_mgr._get_atomic_info(pr, data[pr])

            # show also labels
            status = [f"{data[pr]['update_age']/86400:.1f} days old, {data[pr]['approved']}"]
            self._label_status(status, data[pr]['labels'])

            table += f"""<tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td>{pr}</td>
                <td><a href='{url}'>{title}</a></td>
                <td>{tag}</td>
                <td>{atomic_rev}</td>
                <td>{atomic_bom_impacted}</td>
                <td>{owner}</td>
                <td>{', '.join(status)}</td>
            </tr>\n"""

        # MERGED PR ==============================================
        closed_PR = list(self.get_prs('merged'))
        table += f"{stylerow}Merged PRs</td></tr>\n"
        table += headerstyle
        table += header
        prevtag = 'WIP'    # change this to self.base_branch for pre-CCI
        cnt_tag = defaultdict(list)
        cnt_date = {}

        # Determine the initial atomic revision and BOM for PRs before the oldest displayed PR
        current_atomic_rev, current_atomic_bom = self.atomic_mgr._get_initial_atomic_rev(
            closed_PR, data)

        # Check if we're in all-repo mode with pre-computed atomic info
        allrepo_mode = getattr(self, '_allrepo_mode', False)

        # First pass: compute atomic revisions for each PR in oldest-to-newest order
        # This ensures proper revision propagation (older PRs inherit until a new revision is found)
        pr_atomic_info = {}  # pr -> (atomic_rev, atomic_bom, row_color)

        if allrepo_mode:
            # Use pre-computed values from _precompute_atomic_info()
            for pr in closed_PR:
                pr_atomic_rev = data[pr].get('_computed_atomic_rev', '')
                pr_atomic_bom = data[pr].get('_computed_atomic_bom', '')
                row_color = self.atomic_mgr.get_color_for_revision(pr_atomic_rev)
                pr_atomic_info[pr] = (pr_atomic_rev, pr_atomic_bom, row_color)
        else:
            # Normal mode: compute atomic info with inheritance
            temp_atomic_rev = current_atomic_rev
            temp_atomic_bom = current_atomic_bom
            # oldest first
            for pr in sorted(closed_PR, key=lambda x: data[x]['merge_age'], reverse=True):
                atomic_rev, atomic_bom = self.atomic_mgr._get_atomic_info(pr, data[pr])
                if atomic_rev:
                    temp_atomic_rev = atomic_rev
                    temp_atomic_bom = atomic_bom
                row_color = self.atomic_mgr.get_color_for_revision(temp_atomic_rev)
                pr_atomic_info[pr] = (temp_atomic_rev, temp_atomic_bom, row_color)

        # Second pass: build rows in newest-first order for display and counting
        merged_rows = []

        for pr in sorted(closed_PR, key=lambda x: data[x]['merge_age']):  # newest first
            # Get pre-computed atomic info
            pr_atomic_rev, pr_atomic_bom, row_color = pr_atomic_info[pr]

            # Build the HTML row
            title = self._title(data[pr]['title'], data[pr]['labels'])
            owner = data[pr]['author']['login'][:20]
            url = data[pr]['url']
            date_var = data[pr]['mergedAt']
            merge_time = utc2local(date_var, tzoffset=int(self.OPT.get('tz', 0)))
            tag = data[pr].get('tags', ' ')
            manual = self._manual_status(data[pr]['labels'])
            age = f"{data[pr]['merge_age'] / 86400:.1f} days ago: {merge_time}"

            table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: {row_color}; color: #000000;'>
                <td>{pr}</td>
                <td><a href='{url}'>{title}</a></td>
                <td>{tag}</td>
                <td>{pr_atomic_rev}</td>
                <td>{pr_atomic_bom}</td>
                <td>{owner}</td>
                <td>{age}{manual}</td>
            </tr>\n"""

            # Do counting
            if tag.strip():
                prevtag = tag
                cnt_date[prevtag] = age
            cnt_tag[prevtag].append((pr, title, data[pr]['labels'], owner, data[pr].get('changedFiles')))

        table += "</table>\n"    # <td>{dt_local}</td>

        # To summarize above data, across multiple .csv (one .csv one product),
        # Run below code in demo.py to add the filename at the end, so that you can pivottable
        # for ff in sys.argv[1:]:
        #     for line in File(ff).chomp():
        #         print(f'{line}, {ff.replace(".csv", "")}')

        # cnt mode - called from pr_cnt
        if cmd_prcnt == 'SUM':
            result = []
            for tag in [x for x in sorted(cnt_tag) if x != 'WIP']:
                result.append(f"{tag}, {cnt_date.get(tag, 'None None').split()[-2]}, {len(cnt_tag[tag])}")
            return "TP, date, PR_count", result

        if cmd_prcnt == 'DETAIL':
            result = []
            for tag in [x for x in sorted(cnt_tag) if x != 'WIP']:
                for item in cnt_tag[tag]:
                    title = item[1].replace(',', ' ')
                    result.append(f"{tag}, {cnt_date.get(tag, 'None None').split()[-2]}, {item[0]}, {item[4]}, {item[3]}, {title}")
            return "TP, date, pr_no, changedFiles, author, title", result

        if cmd_prcnt == 'TEAM':
            result = []
            for tag in [x for x in sorted(cnt_tag) if x != 'WIP']:
                for item in cnt_tag[tag]:
                    title = item[1].replace(',', ' ')
                    for label in sorted(item[2]):
                        team = label.split('_')[0]
                        if team not in ('I', 'PASSED', 'FAILED', 'AAREADY', 'READY', 'BUNDLE'):
                            result.append(f"{tag}, {item[0]}, {team}, {label}, {title}")
            return "TP, pr_no, team, label, title", result

        # Display it!
        print(f"""
<html style="font-family: Calibri; font-size: 15px;">
<head>
<title>{header1}</title>
</head>
<body>
<h1>{table}</h1>
<h2 style = 'font-size: 15px;'>
To increase row count, add '&rows=100' in url. Default is {self.rows}.<br>
For more details, please contact: {self.cfg['email']}</h2>
</body></html>
""")


class SuccessRate:
    TESTERNAME = '*TXBT*'
    LOGDIR = '/intel/engtools/tptools/mtl/logs/checkers'
    CACHEDIR = '/intel/engtools/tptools/mtl/infra/torch/successrate_db'   # robot/date.json
    URL = CCI.URL

    def __init__(self, robot):
        """
        :param robot: robot name "tprobot_P68C0"
        """
        self.robot = robot

    def main(self):
        with DivHide():
            self.walk_folders()
        print("<pre>")
        print("Legend: F: Silicon Fail, i: Init Fail, L: Load Fail, C: Cancelled run, R: TPI_READY, *: Other Fail")
        print("")
        self.display()
        print("</pre>")

    def display(self):
        """Display tprobot build success rate"""
        for dd in sorted(os.listdir(f'{self.CACHEDIR}/{self.robot}'), reverse=True):
            if not dd.endswith('.json'):
                continue
            with open(f'{self.CACHEDIR}/{self.robot}/{dd}') as fh:
                data = json.load(fh)
                if data['total']:
                    deyt = dd.replace('.json', '')
                    pct = len(data["pass"]) * 100 / len(data["total"])
                    msg = [f'{deyt} {len(data["pass"]):3}/{len(data["total"]):3} = {pct:6.2f}%: ']
                    for item in data["total"]:
                        if item not in data["pass"]:
                            url = f'{self.URL}?br=x&viewlog={item}'
                            if item in data["failsi"]:
                                msg.append(f'<a href="{url}">F</a> ')
                            elif item in data["failinit"]:
                                msg.append(f'<a href="{url}">i</a> ')
                            elif item in data["failload"]:
                                msg.append(f'<a href="{url}">L</a> ')
                            elif item in data["cancelled"]:      # pragma: no cover  - backwards only. This letter does not exist (ignored)
                                msg.append(f'<a href="{url}">C</a> ')
                            elif item in data["rc"]:             # pragma: no cover  - backwards only. This letter does not exist (ignored)
                                msg.append(f'<a href="{url}">R</a> ')
                            else:
                                msg.append(f'<a href="{url}">*</a> ')
                    print(''.join(msg))

    @classmethod
    def today(cls):
        """Return today date"""
        return curtime(dateonly=True)

    def walk_folders(self):
        """
        Walk to all dates in LOGDIR
        Then save to CACHEDIR
        """
        mkdirs(f'{self.CACHEDIR}/{self.robot}', mode='02775')
        with Chdir(self.LOGDIR):
            for dd in sorted(os.listdir('.')):

                if '202' not in dd:
                    continue    # invalid folder

                # Do not process if date is already processed
                jsondd = f'{self.CACHEDIR}/{self.robot}/{dd}.json'
                if os.path.exists(jsondd):
                    continue

                # Do not process today - data can be incomplete
                if dd == self.today():
                    continue

                # start of process for the day ============
                print(f"Processing {dd}<br>")
                data = {'pass': [],
                        'total': [],
                        'failsi': [],
                        'failinit': [],
                        'failload': [],
                        'cancelled': [],
                        'rc': []}
                for ff in glob.glob(f'./{dd}/{self.TESTERNAME}'):
                    self.process_file(ff, data)

                # save to cache
                # print(f'{dd}: {data["pass"]}/{data["total"]}')
                with open(jsondd, 'w') as fh:
                    json.dump(data, fh, indent=3)

    def process_file(self, ff, data):
        """Process one file"""
        success = True
        ignore = False
        for lno, line in enumerate(File(ff).chomp()):
            if 'FULL CMD' in line:
                if self.robot not in line:
                    return    # Incorrect product, ignore this file

            if 'Traceback (most recent call last)' in line:
                success = False

            if line.startswith('Error'):
                if 'FAILED_Si' in line:
                    data['failsi'].append(ff)
                elif 'FAILED_Init' in line:
                    data['failinit'].append(ff)
                elif '[FAILED]' in line:
                    data['failload'].append(ff)
                elif 'TPI READY' in line:
                    ignore = True
                    # data['rc'].append(ff)

            if line.startswith('KeyboardInterrupt'):
                ignore = True
                # data['cancelled'].append(ff)

        if ignore:
            return    # Do nothing

        data['total'].append(ff)     # pass or fail
        if success:
            data['pass'].append(ff)

    def weekly(self, nweeks=5):    # 4 past + 1 current
        """
        Display weekly data
        :param nweeks: number of weeks
        :return:
        """
        input_robots = self.robot.split(',')

        dict_ww = defaultdict(list)

        # ============= get workweeks first (and jsons to read)
        for robot in input_robots:
            self.robot = robot      # this is used inside walk_folders()
            with DivHide():
                self.walk_folders()

            for fname in sorted(os.listdir(f'{self.CACHEDIR}/{robot}'), reverse=True):
                if not fname.endswith('.json'):
                    continue
                ww = workweek(date=basename(fname).split('.')[0])[:-2]
                dict_ww[ww].append(f'{robot}/{fname}')

        # ============== get fail count per ww based on files
        fail_ww_cnt = defaultdict(int)
        all_fail_list = list(TPBotFail().get_all_list(input_robots))
        for item in all_fail_list:
            ww = workweek(item['time'])[:-2]
            fail_ww_cnt[ww] += 1

        # ============= First table header
        header1 = 'TPBot Fail Summary'
        headerstyle = "<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>"
        table = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"
        table += f"<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'><pre>{header1}</pre></td></tr>"
        table += f"{headerstyle}\n"
        table += f"""
        <td>&nbsp Workweek</td>
        <td>&nbsp Fail &nbsp</td>
        <td>&nbsp Total &nbsp</td>
        <td>&nbsp Percent-Fail &nbsp</td>
        </tr>\n"""

        # ============= Display per workweek
        ww_cnt = set()

        for ww in sorted(dict_ww, reverse=True):
            if len(ww_cnt) == nweeks:    # pragma: no cover  - maybe later
                break
            ww_cnt.add(ww)

            fail = fail_ww_cnt[ww]
            total = fail
            for fname in dict_ww[ww]:
                with open(f'{self.CACHEDIR}/{fname}') as fh:
                    data = json.load(fh)
                    total += len(data.get("pass", []))

            if total:
                table += f"""<tr style='padding-left: 5px; text-align: right; background-color: #F0F8FF; color: #000000;'>
                        <td>&nbsp {ww} &nbsp</td>
                        <td>{fail} &nbsp</td>
                        <td>{total} &nbsp</td>
                        <td>{(fail * 100 / total):5.1f}% &nbsp</td>
                    </tr>\n"""

        print(f"{table}</table><br>")

        # ============= Table two is details per PR
        # WW, Fail-Count, PR, author, Disposition, Failtype, Comment
        header1 = 'TPBot Fail Details'
        headerstyle = "<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>"
        table = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"
        table += f"<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'><pre>{header1}</pre></td></tr>"
        table += f"{headerstyle}\n"
        table += f"""
        <td>&nbsp WW</td>
        <td>Fail-Count</td>
        <td>PR no</td>
        <td>PR Author</td>
        <td>FailType</td>
        <td>Comment</td>
        </tr>\n"""

        ctr = defaultdict(int)
        for item in all_fail_list:
            # open record:          {robot, prno, logpath, time, author, title}
            # dispositioned record: {robot, prno, logpath, time, author, title, comment, dispo, user}
            ww = workweek(item['time'])[:-2]
            if ww in ww_cnt:
                ctr[ww] += 1
                bot = item['robot'].replace('tprobot_', '')
                table += f"""<tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                        <td>&nbsp {ww} &nbsp</td>
                        <td>&nbsp {ctr[ww]} of {fail_ww_cnt[ww]}</td>
                        <td>{bot}: {item['prno']} &nbsp</td>
                        <td>&nbsp {item['author']}</td>
                        <td>&nbsp {item.get('dispo', 'open')}</td>
                        <td>&nbsp {item.get('comment', '')}</td>
                    </tr>\n"""
        table += "</table>\n"
        table += "<br>"
        table += 'TPBot Updates Journal: <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot+fail+journal">https://wiki.ith.intel.com/display/ITSpdxtp/TPBot+fail+journal</a>'
        print(table)


class CheckerRate:
    LOGDIR = '/intel/engtools/tptools/mtl/logs/checkers'
    CACHEDIR = '/intel/engtools/tptools/mtl/infra/torch/successrate_db/checkers'   # date.json
    URL = CCI.URL

    def __init__(self):
        self.cats = {'Q': 'There are Quality Errors!',
                     'S': 'Sherlock has errors',
                     'G': 'GlobalPList',
                     'U': 'Unlocked pattern patch found',
                     'T': 'There are TRC errors',
                     'C': 'Cannot create a file when that file already exists',
                     'E': 'Torch export failed'}

    def main(self):
        with DivHide():
            self.walk_folders()
        print("<pre>")
        print("Legend:")
        for cat, text in sorted(self.cats.items()):
            print(f"   {cat}: {text}")
        print("")
        self.display()
        print("</pre>")

    def display(self):
        """Display tprobot build success rate"""
        for dd in sorted(os.listdir(self.CACHEDIR), reverse=True):
            if not dd.endswith('.json'):
                continue
            with open(f'{self.CACHEDIR}/{dd}') as fh:
                data = json.load(fh)
                if data['total']:
                    deyt = dd.replace('.json', '')
                    pct = len(data["pass"]) * 100 / len(data["total"])
                    msg = [f'{deyt} {len(data["pass"]):3}/{len(data["total"]):3} = {pct:6.2f}%: ']
                    for item in data["total"]:
                        if item not in data["pass"]:
                            url = f'{self.URL}?br=x&viewlog={item}'
                            for cat in self.cats:
                                if item in data[cat]:
                                    msg.append(f'<a href="{url}">{cat}</a> ')
                                    break
                            else:
                                msg.append(f'<a href="{url}">*</a> ')
                    print(''.join(msg))

    @classmethod
    def today(cls):
        """Return today date"""
        return curtime(dateonly=True)

    def walk_folders(self):
        """
        Walk to all dates in LOGDIR
        Then save to CACHEDIR
        """
        mkdirs(self.CACHEDIR, mode='02775')
        with Chdir(self.LOGDIR):
            for dd in sorted(os.listdir('.')):
                # if dd == '2023-03-01':
                #     break

                if '202' not in dd:
                    continue    # invalid folder

                # Do not process if date is already processed
                jsondd = f'{self.CACHEDIR}/{dd}.json'
                if os.path.exists(jsondd):
                    continue

                # Do not process today - data can be incomplete
                if dd == self.today():
                    continue

                # start of process for the day ============
                print(f"Processing {dd}<br>")
                data = {'pass': [],
                        'total': []}
                for cat in self.cats:
                    data[cat] = []
                for ff in sorted(glob.glob(f'./{dd}/buildtp*')):
                    self.process_file(ff, data)

                # save to cache
                # print(f'{dd}: {data["pass"]}/{data["total"]}')
                with open(jsondd, 'w') as fh:
                    json.dump(data, fh, indent=3)

    def process_file(self, ff, data):
        """Process one file"""
        success = True
        for lno, line in enumerate(File(ff).chomp()):
            if 'FULL CMD' in line:
                if not re.search(r'buildtp\.py FUL\w+ None$', line):
                    return    # Incorrect product, ignore this file

            if 'Traceback (most recent call last)' in line:
                success = False

            if line.startswith(('Error', 'FileExistsError')):
                for cat, text in self.cats.items():
                    if text in line:
                        data[cat].append(ff)

        data['total'].append(ff)     # pass or fail
        if success:
            data['pass'].append(ff)
