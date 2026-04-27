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
from gadget.pylog import log


# Getting the log based on SHA
def git_log(SHA):
    data = SystemCall(f'git log {SHA} -n 1').run_outtxt(False)
    return data


def get_datetime():
    dt = datetime.now()
    date_string = dt.strftime("Date: %d/%m/%Y  time: %H:%M:%S")
    return date_string


def sanitize_pat_from_url(line, _reobj=re.compile(r'(https?://)ghp_[A-Za-z0-9]{36}@github\.com(/)')):
    """Strip GitHub Personal Access Tokens (PATs) from URLs.

    Replaces patterns like ``https://ghp_xxxx@github.com/...``
    with ``https://github.com/...`` so that tokens are not
    persisted in report files.

    :param line: A single line of text to sanitize
    :type line: str
    :return: The line with any embedded PATs removed
    :rtype: str
    """
    return _reobj.sub(r'\1github.com\2', line)


def new_integration_report_file(integration_report_path):
    return integration_report_path


def rewrite_integ_report(integration_report_path, data_dict):

    with open(integration_report_path, errors='ignore') as f:
        f_lines = f.readlines()

    integration_report_file = new_integration_report_file(integration_report_path)

    # integration_report_path = f'I:/engineering/dev/sctp/users/taipham/Integration_report.txt'
    with open(integration_report_file, 'w', errors='ignore') as f:
        record_flag = False
        for line in f_lines:
            line = sanitize_pat_from_url(line)
            if '<TP Modules>' in line:
                record_flag = True
            if record_flag:
                if '#---------' in line:
                    f.write(line)
                    continue
                elif '<TP Modules>' in line:
                    f.write(line)
                    continue
                elif 'TP Flow Structure' in line:
                    f.write(line)
                    record_flag = False
                else:
                    if ' -   ' in line:
                        raw_data = line.strip().replace(" -   ", "\"")
                        data = raw_data.split("\"")[0].replace("   ", "#").strip().split("#")
                        data_array = []
                        for item in data:
                            if item != '':
                                data_array.append(item.strip())
                        if len(data_array) == 3:
                            moduleName = data_array[0]
                            owner = data_array[1]
                            if owner == 'GitHub':
                                line = line.replace('GitHub', data_dict[moduleName][3])
                                f.write(line)
                            else:
                                f.write(line)
                        else:
                            f.write(line)
                    else:
                        f.write(line)
            else:
                f.write(line)


def change_description_report(base_tp, tpproj):

    POR_TP = os.path.dirname(tpproj)
    integration_report_path = f'{base_tp}/{POR_TP}/Reports/Integration_Report.txt'
    log.info(integration_report_path)

    if os.path.exists(integration_report_path):
        record_flag = False
        data_dict = {}

        # Read through the intergration report to get the report data
        with open(integration_report_path, errors='ignore') as f:
            f_lines = f.readlines()
        for line in f_lines:
            if '<TP Modules>' in line:
                record_flag = True
            if record_flag:
                if '#---------' in line:
                    continue
                elif '<TP Modules>' in line:
                    continue
                elif 'TP Flow Structure' in line:
                    record_flag = False
                    break
                else:
                    if ' -   ' in line:
                        raw_data = line.strip().replace(" -   ", "\"")
                        data = raw_data.split("\"")[0].replace("   ", "#").strip().split("#")
                        data_array = []
                        for item in data:
                            if item != '':
                                data_array.append(item.strip())
                        if len(data_array) == 3:
                            moduleName = data_array[0]
                            owner = data_array[1]
                            timeStamp = data_array[2].split(" ")[0]
                            SHA = data_array[2].split(" ")[1]
                            log_info = git_log(SHA)
                            author = '---'
                            for item in log_info:
                                if isinstance(item, str):
                                    if 'Author:' in item:
                                        author = item.split(':')[1].split('<')[0].strip()
                                        break
                            data_dict[moduleName] = [SHA, timeStamp, log_info, author]
                    else:
                        continue
    else:
        log.info(f"{integration_report_path} does NOT exist!")
        exit(1)

    change_description_report_file = f'{base_tp}/{POR_TP}/Reports/Changes_Description_Report.txt'
    # change_description_report_file = f'I:/engineering/dev/sctp/users/taipham/Changes_Description_Report.txt'
    # Getting date and time
    date_string = get_datetime()

    # Remove old file if exists
    if os.path.exists(change_description_report_file):
        log.info(f'Remove old file: {change_description_report_file}')
        os.remove(change_description_report_file)

    # Start writing data to a file
    with open(change_description_report_file, 'w', errors='replace') as f:
        log.info(f'Writing data to {change_description_report_file}...')
        f.write(f'Changes Description Report -- {date_string}\n\n\n')
        for module in data_dict:
            f.write(f'{module} -- {data_dict[module][1]}\n')
            data = data_dict[module][2][1].split('\n')
            for item in data:
                f.write(f'{item}\n')
            f.write(f'\n------------######--------------\n')

    # Rewrite integration report to have correct Author
    rewrite_integ_report(integration_report_path, data_dict)


if __name__ == "__main__":    # pragma: no cover
    # change_description_report('I:/tpvalidation/hdmxprogs/arl/ARLXXXXXXX75T0CSXXX', 'POR_TP\\Class_ARL_U28\\Class_ARL_U28.tpproj')
    change_description_report(sys.argv[1].strip(), sys.argv[2].strip())
