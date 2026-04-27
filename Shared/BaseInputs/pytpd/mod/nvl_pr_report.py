#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
from setenv import ROOT_ENV      # must be first in the imports
import sys
import os
from os.path import exists, basename, dirname, isdir
from subprocess import call, run
from gadget.files import File, TempName
import json
from datetime import datetime
from tp.testprogram import Env
from gadget.shell import SystemCall
from gadget.errors import confirm
import re
from gadget.pylog import log
from gadget.disk import Chdir
from gadget.getgit import GitHub


def get_prno(tag_or_sha):
    prev_tag_flag = False

    log.info('git fetch')
    SystemCall("git fetch").run_outtxt(False)

    log.info(f'Retrieving info for {tag_or_sha}...')
    with TempName(name=True) as fname:
        # Go back to 3 commits to find a PR associate with tag. In case of the tag was tagged to a manual commit.
        cmd = f'git log {tag_or_sha} -n 10'
        SystemCall(cmd).run_outfile(fname)
        with open(fname) as fh:
            fline = fh.readlines()
            for line in fline:
                log.info(line.strip())
                all_pr_numbers = [int(num) for num in re.findall(r'#(\d+)', line)]
                if all_pr_numbers:
                    prev_tag_flag = True
                    log.info(f'Found PR numbers: {all_pr_numbers}')
                    return all_pr_numbers

            if prev_tag_flag is False:
                log.info(f'Could NOT find the PR number associated with {tag_or_sha}')
                return []


def get_input_timestamp(input_data):
    """
    Get the timestamp of the input, which can be a branch name, tag, or SHA.
    """
    with TempName(name=True) as fname:
        # Go back to 3 commits to find a timestamp associated with Tag or SHA.
        cmd = f'git log {input_data} -n 10'
        SystemCall(cmd).run_outfile(fname)
        with open(fname) as fh:
            fline = fh.readlines()
        for line in fline:
            log.info(line.strip())
            if 'Date:' in line:
                # Extract the date and time from the line
                date_str = line.split('Date:')[1].strip()
                return date_str


def get_common_branches(branch, previous_TP_tag):
    """
    Get common branches that contain both the current branch (or tag or SHA) and the previous TP tag.
    Return the branch that is shared between both.
    1. If 'origin/main' is in the common branches, return 'main'.
    2. Otherwise, return the first branch that starts with 'origin/main'.
    3. If no common branches are found, return the original branch.
    """
    all_branches_cur_tag = []
    with TempName(name=True) as fname:
        cmd = f'git branch -r --contains {branch}'
        SystemCall(cmd).run_outfile(fname)
        with open(fname) as fh:
            fline = fh.readlines()
            all_branches_cur_tag = [line.strip() for line in fline if '->' not in line]
    all_branches_prev_tag = []
    with TempName(name=True) as fname:
        cmd = f'git branch -r --contains {previous_TP_tag}'
        SystemCall(cmd).run_outfile(fname)
        with open(fname) as fh:
            fline = fh.readlines()
            all_branches_prev_tag = [line.strip() for line in fline if '->' not in line]
    common_branches = list(set(all_branches_cur_tag) & set(all_branches_prev_tag))
    log.info(f'Common branches found: {common_branches}')
    if common_branches:
        if 'origin/main' in common_branches:
            branch = 'main'
        else:
            # Get the first item match origin/main*
            branch = next((b for b in common_branches if b.startswith('origin/main')), common_branches[0])
            branch = branch.replace('origin/', '')
        log.info(f'Using common branch: {branch} for PR analysis.')
    return branch


def return_report_file(current_tp, dielet_bit):
    """
    Return the PR report file path based on current TP and dielet bit.
    :param current_tp: Current TP name
    :param dielet_bit: Dielet bit extracted from TP name
    :return: Path to the PR report file
    """
    if dielet_bit[0] == 'S':
        return f'I:/engineering/dev/team_classtp/torch/PR_reports/{current_tp}.json'
    else:
        return f'I:/engineering/dev/team_classtp/torch/PR_reports/{dielet_bit}_{current_tp}.json'


def main_pr_integrate(cur_TP, prev_TP, pr_paths='/intel/engineering/dev/team_classtp/torch/PR_reports'):
    # cur_TP = '21F0C'
    # prev_TP = '21F0B'

    root_report = Env.xpath(pr_paths)
    log.info("Setup ENV proxy")
    os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'

    tpfullname = os.environ.get('DEST', 'None')
    # Set the dielet bit based on the TP fullname. So that we can name the dielet report file accordingly.
    if tpfullname != 'None':
        dielet_bit = basename(tpfullname)[15:17]
    else:
        log.info('TP fullname is not set in os.environ. Exit')
        return
    current_report = return_report_file(cur_TP, dielet_bit)
    if dielet_bit[0] == 'S':
        previous_TP_tag = f'TP_{prev_TP}'
    else:
        previous_TP_tag = f'{dielet_bit}_{prev_TP}'
    if os.path.exists(current_report):
        log.info("Remove current report to generate a new report...")
        os.remove(current_report)
    report = {}
    repo_checkout = Env.xpath('/intel/engineering/dev/team_classtp/torch/repos')

    # Check if is the common repo, if this is common repo, check the TP name to get the combination.
    is_pr_common = os.environ.get('IS_PR_COMMON', 'False').upper()
    if is_pr_common == 'TRUE':
        log.info('This is common repo. Checking the TP Name to get the dielet combination...')
        cpu_branch = os.environ.get('CPU_Branch', 'None')
        gcd_branch = os.environ.get('GCD_Branch', 'None')
        pcd_branch = os.environ.get('PCD_Branch', 'None')
        hub_branch = os.environ.get('HUB_Branch', 'None')
        common_branch = os.environ.get('CURRENT_BRANCH', 'None')
        log.info(f'CPU Branch: {cpu_branch}')
        log.info(f'GCD Branch: {gcd_branch}')
        log.info(f'PCD Branch: {pcd_branch}')
        log.info(f'HUB Branch: {hub_branch}')
        log.info(f'Common Branch: {common_branch}')
        branch_dict = {'nvl.common': common_branch, 'nvl.cpu': cpu_branch, 'nvl.gcd': gcd_branch, 'nvl.pcd': pcd_branch, 'nvl.hub': hub_branch}
    # If not common repo, check DIEINDICATOR
    else:
        die_indicator = os.environ.get('DIEINDICATOR', 'None').lower()
        log.info(f'DIEINDICATOR: {die_indicator}')
        common_branch = os.environ.get('COMMON_Branch', 'None')
        branch_dict = {'nvl.common': common_branch, f'nvl.{die_indicator}': os.environ.get('CURRENT_BRANCH', 'None')}

    for repo, branch in branch_dict.items():
        if branch.upper() == 'NONE':
            log.warning(f'Skipping {repo} as branch is not set')
            continue

        repo_dict = {}
        with Chdir(f'{repo_checkout}/{repo}'):

            log.info(f'Get PR list for {repo}:')
            SystemCall('git reset --hard', disp=True)
            SystemCall('git pull', disp=True)
            SystemCall(f'git fetch').run_outtxt(False)          # download latest info from server
            # Check if branch is a SHA (40 characters) or a branch name
            all_branches = GitHub.get_all_branches()
            built_from_sha = False
            built_from_tag = False
            tag_or_sha = ''
            if branch not in all_branches:
                if len(branch) == 40:
                    log.info(f'{branch} appears to be a SHA (40 characters). Getting the common branch for the sha and previous tag...')
                    built_from_sha = True
                    tag_or_sha = branch
                    branch = get_common_branches(branch, previous_TP_tag)
                    if branch == tag_or_sha:
                        date_str = get_input_timestamp(branch)
                        repo_dict['SHA'] = f'Built from SHA: {branch} -- Timestamp: {date_str}'
                        report[repo] = repo_dict
                        continue
                else:
                    log.info(f'{branch} appears to be a TAG. Getting the common branch for both current tag and previous tag...')
                    built_from_tag = True
                    tag_or_sha = branch
                    branch = get_common_branches(branch, previous_TP_tag)
                    if branch == tag_or_sha:
                        date_str = get_input_timestamp(branch)
                        repo_dict['TAG'] = f'Built from TAG: {branch} -- Timestamp: {date_str}'
                        report[repo] = repo_dict
                        continue

            log.info(f'Processing branch: {branch}')
            # Add branch information to repo_dict
            if built_from_tag:
                repo_dict['TAG'] = f'Built from tag: {tag_or_sha}'
            elif built_from_sha:
                repo_dict['SHA'] = f'Built from SHA: {tag_or_sha}'
            else:
                repo_dict['Branch'] = f'Built from branch: {branch}'
            ecode, data = SystemCall(f"gh pr list -s merged -B {branch} -L 200  --json mergedAt,number,title,author,url", disp=True).run_outtxt(False)
            data_json = json.loads(data)
            confirm(not ecode, "Script failed execution!", "pls check")
            dict_data = {}

            total_pr = len(data_json)
            for item in range(total_pr):
                time = data_json[item]['mergedAt'].replace('T', ' ').replace('Z', '')
                PR_num = data_json[item]['number']
                title = data_json[item]['title']
                author = data_json[item]['author']['login']
                url = data_json[item]['url']
                dict_data[PR_num] = [time, title, author, url]

            # If built from tag or sha, getting the current timestamp.
            cur_pr_flag = False
            if built_from_tag or built_from_sha:
                cur_pr = get_prno(tag_or_sha)
                for key, value in dict_data.items():
                    if key in cur_pr:
                        log.info(f'Found Current Tag PR number {key}')
                        date = value[0]
                        year = int(date.split('-')[0])
                        month = int(date.split('-')[1])
                        day = int(date.split('-')[2].split(' ')[0])
                        hour = int(date.split(' ')[1].split(':')[0])
                        mins = int(date.split(' ')[1].split(':')[1])
                        second = int(date.split(' ')[1].split(':')[2])
                        cur_pr_time = datetime(year, month, day, hour, mins, second)
                        log.info(f'Current integration merged PR: {cur_pr_time}')
                        cur_pr_flag = True
                        break

            # Checking previous Test Program Tag
            prev_pr = get_prno(previous_TP_tag)
            prev_pr_flag = False
            for key, value in dict_data.items():
                if key in prev_pr:
                    log.info(f'Found Previous Test Program PR number {key}')
                    date = value[0]
                    year = int(date.split('-')[0])
                    month = int(date.split('-')[1])
                    day = int(date.split('-')[2].split(' ')[0])
                    hour = int(date.split(' ')[1].split(':')[0])
                    mins = int(date.split(' ')[1].split(':')[1])
                    second = int(date.split(' ')[1].split(':')[2])
                    prev_pr_time = datetime(year, month, day, hour, mins, second)
                    log.info(f'Previous integration merged PR: {prev_pr_time}')
                    prev_pr_flag = True
                    break

            if (prev_pr_flag is True):
                remove_key = []
                # Getting the current merged PR time and sort out the old PR
                for key, value in dict_data.items():
                    date = value[0]
                    year = int(date.split('-')[0])
                    month = int(date.split('-')[1])
                    day = int(date.split('-')[2].split(' ')[0])
                    hour = int(date.split(' ')[1].split(':')[0])
                    mins = int(date.split(' ')[1].split(':')[1])
                    second = int(date.split(' ')[1].split(':')[2])
                    current_time = datetime(year, month, day, hour, mins, second)
                    if (cur_pr_flag is True):
                        if (current_time > cur_pr_time or current_time <= prev_pr_time):
                            remove_key.append(key)
                    else:
                        if (current_time <= prev_pr_time):
                            remove_key.append(key)

                for item in remove_key:
                    dict_data.pop(item)
            else:
                log.info(f'Could NOT find the PR number in the current {repo}')

            for pr, pr_info in dict_data.items():
                pr_info_dict = {}
                pr_info_dict["title"] = pr_info[1]
                pr_info_dict["MergedAt"] = pr_info[0]
                pr_info_dict["Submitted by"] = pr_info[2]
                pr_info_dict["url"] = pr_info[3]
                repo_dict[pr] = pr_info_dict

            report[repo] = repo_dict
    with open(current_report, 'w') as f:
        json.dump(report, f, indent=4)


if __name__ == "__main__":    # pragma: no cover
    main_pr_integrate(sys.argv[1].strip(), sys.argv[2].strip())
