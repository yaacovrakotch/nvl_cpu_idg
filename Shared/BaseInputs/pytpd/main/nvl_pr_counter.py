#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Automatic PR Counter
Will be run daily.
"""

import setenv        # must be first in the imports
from gadget.strmore import day_code
from gadget.disk import Chdir
from gadget.shell import SystemCall
from gadget.pylog import log
from gadget.getgit import GitHub
from gadget.errors import confirm
from gadget.strmore import workweek, utc2local, wwno
import os
import json
import re
import time
import sys
import csv

try:
    import win32com.client
except ImportError:
    pass


class PRCounter:

    def __init__(self):
        self.pr_counter_folder = '//amr/ec/proj/mdl/jf/intel/engineering/dev/team_classtp/dashboard/NVL/pr_counter'
        self.output_file = f'{self.pr_counter_folder}/all_prs_data.json'
        self.milestone_file = f'{self.pr_counter_folder}/milestone.json'
        self.main_repo_folder = '//amr/ec/proj/mdl/jf/intel/tpvalidation/engtools/tptools/mtl/infra/torch/repos'
        self.repos = ['nvl.cpu', 'nvl.gcd', 'nvl.pcd', 'nvl.hub', 'nvl.common']

    def get_changed_files(self, pr_number):
        """
        Get the list of changed files for a given PR number.
        """
        ecode, data = SystemCall(f"gh pr diff {pr_number} --name-only").run_outtxt(False)
        changed_files = data.splitlines()
        return changed_files

    def pr_sum(self, repo, milestone, save_output):
        """
        Summarize PRs for a given repository across all branches.
        """
        repo_folder = f'{self.main_repo_folder}/{repo}'
        with Chdir(repo_folder):
            log.info("Setup ENV proxy")
            os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
            log.info(f'Current directory: {os.getcwd()}')
            SystemCall('git reset --hard', disp=True)
            SystemCall('git fetch', disp=True)
            SystemCall('git pull', disp=True)
            allbr = []
            for br in sorted(GitHub.get_all_branches()):
                if re.search(f'^(main|main_RC_)', br):
                    allbr.append(br)

            # Collect all PR data from all branches
            all_prs = []
            team = ['ARR', 'SCN', 'FUN', 'DRV', 'PTH', 'MIO', 'CLK', 'TPI', 'FUS', 'YBS', 'BaseInputs', 'POR_TP']
            for branch in allbr:
                log.info(f'Processing {branch}')
                ecode, data = SystemCall(f"gh pr list -s merged -B {branch} -L 10000  --json mergedAt,number,title,url").run_outtxt(False)
                confirm(not ecode, "Script failed execution!", "pls check")
                data_json = json.loads(data)

                # Add branch information to each PR and merge into main list
                for pr in data_json:
                    pr['branch'] = branch  # Add branch info to each PR
                    pr['repo'] = repo  # Add repo info to each PR
                    pr['mergedAt'] = wwno(utc2local(pr['mergedAt']).timestamp(), year=True)
                    # Convert to string for comparison since milestone keys are strings
                    merged_at_str = str(pr['mergedAt'])
                    if merged_at_str in milestone:
                        pr['event'] = milestone[merged_at_str]

                    for item in save_output:
                        if pr['number'] == item['number'] and repo == item['repo']:
                            break
                    else:
                        changed_files = self.get_changed_files(pr['number'])
                        pr_team = []
                        for file in changed_files:
                            for t in team:
                                if t in file:
                                    pr_team.append(t)
                                    break
                        pr['teams'] = list(set(pr_team))  # Remove duplicates
                        log.info(f"PR {pr['number']} associated with teams: {pr['teams']}")
                        all_prs.append(pr)
            log.info(f"Total PRs collected from all branches: {len(all_prs)}")
            return all_prs

    def read_output_file(self, output_file):
        """
        Read existing output file if it exists.
        """
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                save_output = json.load(f)
                log.info(f"Loaded save_output data: {save_output}")
            return save_output
        return []

    def main(self):
        """
        Main entry point for the PR counter.
        """
        # repos = ['nvl.cpu']
        save_output = self.read_output_file(self.output_file)

        # Read milestone data and put it into milestone dict
        with open(self.milestone_file, 'r', encoding='utf-8') as f:
            milestone = json.load(f)
            log.info(f"Loaded milestone data: {milestone}")

        all_repos_data = []
        for repo in self.repos:
            repo_data = self.pr_sum(repo, milestone, save_output)
            all_repos_data.extend(repo_data)
        all_repos_data = all_repos_data + save_output
        # Write all collected data to JSON file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(all_repos_data, f, indent=4, sort_keys=True, ensure_ascii=False)
        log.info(f"Saved all PR data from {len(self.repos)} repos to: {self.output_file}")
        log.info(f"Total PRs collected: {len(all_repos_data)}")


if __name__ == '__main__':  # pragma: no cover
    obj = PRCounter()
    obj.main()
