#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
from setenv import ROOT_ENV      # must be first in the imports
import sys
import os
from subprocess import call, run
from gadget.files import File, TempName
import json
from datetime import datetime
from tp.testprogram import Env
from gadget.shell import SystemCall
from gadget.errors import confirm
import re


def get_prno(prev_TP):
    previous_TP_tag = f'TP_{prev_TP}'
    prev_tag_flag = False

    print('git fetch')
    SystemCall("git fetch").run_outtxt(False)

    print(f'Retrieving info for {previous_TP_tag}...')
    with TempName(name=True) as fname:
        cmd = f'git log {previous_TP_tag} -n 1'
        SystemCall(cmd).run_outfile(fname)
        with open(fname) as fh:
            fline = fh.readlines()
            for line in fline:
                result = re.search(r'#(\d+)', line)
                if result:
                    pr_tag_num = result.group(1).strip()
                    prev_tag_flag = True
                    return int(pr_tag_num)    # first occurrence

            if (prev_tag_flag is False):
                print(f'Could NOT find the PR number associated with {previous_TP_tag}')
                return 0


def main_pr_integrate(cur_TP, prev_TP, tp_branch, pr_paths='/intel/engineering/dev/team_classtp/torch/PR_reports'):
    # cur_TP = '21F0C'
    # prev_TP = '21F0B'

    root_report = Env.xpath(pr_paths)
    base_branch = tp_branch
    print(f"Base branch: {base_branch}")

    print("Setup ENV proxy")
    os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'

    print('Get PR list...')
    print(f'CMD: gh pr list -s merged -B {base_branch} -L 200  --json mergedAt,number,title,author,url')
    ecode, data = SystemCall(f"gh pr list -s merged -B {base_branch} -L 200  --json mergedAt,number,title,author,url").run_outtxt(False)
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

    # Checking previous Test Program Tag
    prev_pr = get_prno(prev_TP)
    prev_pr_flag = False
    for key in dict_data:
        if key == prev_pr:
            print(f'Found Previous Test Program PR number {key}')
            date = dict_data[key][0]
            year = int(date.split('-')[0])
            month = int(date.split('-')[1])
            day = int(date.split('-')[2].split(' ')[0])
            hour = int(date.split(' ')[1].split(':')[0])
            mins = int(date.split(' ')[1].split(':')[1])
            second = int(date.split(' ')[1].split(':')[2])
            prev_pr_time = datetime(year, month, day, hour, mins, second)
            print(f'Previous integration merged PR: {prev_pr_time}')
            prev_pr_flag = True

    current_report = f'{root_report}/{cur_TP}.txt'
    if (prev_pr_flag is True):
        remove_key = []

        # Getting the current merged PR time and sort out the old PR
        for key in dict_data:
            date = dict_data[key][0]
            year = int(date.split('-')[0])
            month = int(date.split('-')[1])
            day = int(date.split('-')[2].split(' ')[0])
            hour = int(date.split(' ')[1].split(':')[0])
            mins = int(date.split(' ')[1].split(':')[1])
            second = int(date.split(' ')[1].split(':')[2])
            current_time = datetime(year, month, day, hour, mins, second)
            if (current_time <= prev_pr_time):
                print(f"Remove PR {key}")
                remove_key.append(key)

        for item in remove_key:
            dict_data.pop(item)
    else:
        print(f'Could NOT find the PR number in the current {base_branch}')

    if os.path.exists(current_report):
        print("Remove current report to generate a new report...")
        os.remove(current_report)

    with open(current_report, 'a') as f_cur:
        for pr in dict_data:
            print(f"PR number: {pr}, title: {dict_data[pr][1]}, MergedAt: {dict_data[pr][0]}, Submitted by: {dict_data[pr][2]}, url: {dict_data[pr][3]}\n")
            f_cur.write(f"PR number: {pr}, title: {dict_data[pr][1]}, MergedAt: {dict_data[pr][0]}, Submitted by: {dict_data[pr][2]}, url: {dict_data[pr][3]}\n")

    print(f"Please check your PR report at: {current_report}")


if __name__ == "__main__":    # pragma: no cover
    main_pr_integrate(sys.argv[1].strip(), sys.argv[2].strip(), sys.argv[3].strip())
