from setenv import ROOT_ENV      # must be first in the imports
import sys
import os
from subprocess import call, run
import json
from datetime import datetime, date
from gadget.shell import SystemCall
from gadget.pylog import log
import shutil
import glob
from gadget.shell import IS_UNIX, IS_WIN
import argparse

try:
    import win32com.client
except ImportError:
    pass


def isGitrepo(current_directory):
    print(f'Current directory: {current_directory}')
    git_path = os.path.join(current_directory, '.git')
    if os.path.exists(git_path):
        return 1
    else:
        return 0


def get_TP_Path(TestProgram):
    if 'MTL' in TestProgram:
        if TestProgram[7:10] == 'XXX':
            TP_path = f'I:/tpvalidation/hdmxprogs/mtl/{TestProgram}'
        else:
            TP_path = f"I:/hdmxprogs/mtl/{TestProgram}"
        return TP_path

    elif 'ARL' in TestProgram:
        if TestProgram[7:10] == 'XXX':
            TP_path = f'I:/tpvalidation/hdmxprogs/arl/{TestProgram}'
        else:
            TP_path = f"I:/hdmxprogs/arl/{TestProgram}"
        return TP_path

    else:
        print(f'Cannot find the test program path for TestProgram')
        return 0


def prime_EVG_indicator(TP_path, BOM_folder, TestProgram):
    if 'ARL' in TP_path and 'S68' in BOM_folder:
        # Generate Prime vs EVG indicator
        cmd = f'python -u I:/engtools/tptools/mtl/beta/latest/main/tp_audit.py {TP_path} -evg -out I:/engineering/dev/team_classtp/dashboard/ARL_S68/PRIME_indicator/{TestProgram}.json'
        log.info(f'CMD: {cmd}')
        code, out = SystemCall(cmd).run_outtxt()
        log.info(out)

        # Generate the Prime vs EVG details indicator
        cmd = f'python -u I:/engtools/tptools/mtl/beta/latest/main/tp_audit.py {TP_path} -evg -detail -out I:/engineering/dev/team_classtp/dashboard/ARL_S68/primedetail_indicator/{TestProgram}.json'
        log.info(f'CMD: {cmd}')
        code, out = SystemCall(cmd).run_outtxt()
        log.info(out)

    elif 'ARL' in TP_path and 'H68' in BOM_folder:
        # Generate Prime vs EVG indicator
        cmd = f'python -u I:/engtools/tptools/mtl/beta/latest/main/tp_audit.py {TP_path} -evg -out I:/engineering/dev/team_classtp/dashboard/ARL_H68_N3B/PRIME_indicator/{TestProgram}.json'
        log.info(f'CMD: {cmd}')
        code, out = SystemCall(cmd).run_outtxt()
        log.info(out)

        # Generate the Prime vs EVG details indicator
        cmd = f'python -u I:/engtools/tptools/mtl/beta/latest/main/tp_audit.py {TP_path} -evg -detail -out I:/engineering/dev/team_classtp/dashboard/ARL_H68_N3B/primedetail_indicator/{TestProgram}.json'
        log.info(f'CMD: {cmd}')
        code, out = SystemCall(cmd).run_outtxt()
        log.info(out)


def get_cleantp_report(TP_path):
    cleantp_json = glob.glob(f'{TP_path}/*/*/Reports/Cleantp.json')
    cleantp_fullReport = glob.glob(f'{TP_path}/*/*/Reports/Cleantp_fullreport.csv')
    if cleantp_json and cleantp_fullReport:
        cleantp_json_file = cleantp_json[0]
        print(f'CleanTP: {cleantp_json_file}')
        cleantp_fullReport_file = cleantp_fullReport[0]
        if 'ARL_U28' in cleantp_json_file:
            cleantp_dashboard_dir = 'I:/engineering/dev/team_classtp/dashboard/ARL_U28/CleanTP'
            cleantp_path = f'{cleantp_dashboard_dir}/{os.path.basename(TP_path)}'
            if not os.path.exists(cleantp_path):
                os.mkdir(cleantp_path)
            cleantp_json_dest = f'{cleantp_path}/Cleantp.json'
            cleantp_fullReport_dest = f'{cleantp_path}/Cleantp_fullreport.csv'
            print(f'Copy cleanTP files to dashboard folder {cleantp_path}')
            shutil.copy(cleantp_json_file, cleantp_json_dest)
            shutil.copy(cleantp_fullReport_file, cleantp_fullReport_dest)
    else:
        print(f'Cleantp.json and/or Cleantp_fullreport.csv DO NOT EXIST. Skip copying cleantp files.')


def get_handler_re_path(Handler_Re_path):
    # Handler_Re_path = "I:\\hdmx_rms\\module_recipe\\hdmx\\prod\\mtl\\mtl_p682_mz_ct"
    all_subdirs = []
    if(os.path.exists(Handler_Re_path)):
        for item in os.listdir(Handler_Re_path):
            item_path = f"{Handler_Re_path}\\{item}"
            if os.path.isdir(item_path):
                all_subdirs.append(item_path)
        latest_subdir = max(all_subdirs, key=os.path.getmtime)
        print(f"latest_subdir: {latest_subdir}")
        Handler_Rev = latest_subdir.split('\\')[-1].strip()
        print(f"Handler_Rev: {Handler_Rev}")
        return Handler_Rev

    else:
        print(f"{Handler_Re_path} does NOT exist!")
        exit(1)


def get_pup_release(PUP_PATTERNS_DIR):
    if PUP_PATTERNS_DIR != 'N/A':
        if os.path.exists(PUP_PATTERNS_DIR):
            latest_file = f'{PUP_PATTERNS_DIR}/latest.txt'
            if os.path.exists(latest_file):
                with open(latest_file, 'r') as f_pup:
                    version = f_pup.read().strip()
                    PUP_RELEASE = f'{PUP_PATTERNS_DIR}\\{version}'
                    print(f"PUP_PATTERNS_DIR: {PUP_RELEASE}")
                    return PUP_RELEASE
            else:
                return PUP_PATTERNS_DIR.replace('/', '\\')
        else:
            print(f"{PUP_PATTERNS_DIR} does NOT exist!")
            exit(1)
    else:
        return 'N/A'


def get_report_file(BOM_Groups, short_name):
    if 'P28' in BOM_Groups:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP281\\DAILY\\TPReleaseNotes\\{short_name}.html"

    elif 'P68' in BOM_Groups:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP682\\DAILY\\TPReleaseNotes\\{short_name}.html"

    elif 'H68' in BOM_Groups:
        report_file = f'I:\\engineering\\dev\\team_classtp\\dashboard\\ARL_H68_N3B\\TP_Releases\\{short_name}.html'

    elif 'S68' in BOM_Groups:
        report_file = f'I:\\engineering\\dev\\team_classtp\\dashboard\\ARL_S68\\TP_Releases\\{short_name}.html'

    elif 'U28' in BOM_Groups:
        report_file = f'I:\\engineering\\dev\\team_classtp\\dashboard\\ARL_U28\\TP_Releases\\{short_name}.html'

    else:
        print(f'The {BOM_Groups} is NOT associated with {short_name}. Please check the test program.')
        exit(1)

    if os.path.exists(report_file):
        os.remove(report_file)

    return report_file


def get_daily_report_file(integration_report, short_name):
    if 'P28' in integration_report:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP281\\DAILY\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    elif 'P68' in integration_report:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP682\\DAILY\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    elif 'H68' in integration_report:
        report_file = f"I:\\engineering\\dev\\team_classtp\\dashboard\\ARL_H68_N3B\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    elif 'S68' in integration_report:
        report_file = f"I:\\engineering\\dev\\team_classtp\\dashboard\\ARL_S68\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    elif 'U28' in integration_report:
        report_file = f"I:\\engineering\\dev\\team_classtp\\dashboard\\ARL_U28\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    else:
        print('Cannot find the correct BOMGROUP to generate the daily report. Please contact script owner for the details.')
        return 0


def get_PR_report_file(short_name):
    report_file = f'I:/engineering/dev/team_classtp/torch/PR_reports/{short_name}.txt'
    return report_file


def get_list_PR_report(release_key):
    list_PR_report = glob.glob(f'I:/engineering/dev/team_classtp/torch/PR_reports/{release_key}*.txt')
    return list_PR_report


def get_repo_sha_id(repo_sha):
    if os.path.exists(repo_sha):
        with open(repo_sha) as f:
            data = f.readlines()
        for line in data:
            if 'Repo sha id:' in line:
                repo_sha_id = line.split(':', 1)[1]
                if 'not_available' in repo_sha_id:
                    repo_sha_id = 'N/A'
    else:
        repo_sha_id = 'N/A'

    return repo_sha_id


def setting_Tags(cur_TP, SHA):        # pragma: no cover  - Only system Call, no cover

    print("Setup ENV proxy")
    os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'

    print(f'CMD: git pull')
    data = SystemCall(f'git pull').run_outtxt(False)

    # Checking if current TAG exists
    cur_tag = f'TP_{cur_TP}'
    print(f'CMD: git tag -l {cur_tag}')
    data = SystemCall(f'git tag -l {cur_tag}').run_outtxt(False)
    if cur_tag in data:
        print(f'{cur_tag} exits. Remove the tag {cur_tag}')

        # Remove the tag locally
        data = SystemCall(f'git tag -d {cur_tag}').run_outtxt(False)
        print(data)

        # Remove the tag on the github
        data = SystemCall(f'git push --delete origin {cur_tag}').run_outtxt(False)
        print(data)

    # Adding a tag on the current SHA
    print(f'Adding new tag CMD: git tag {cur_tag} {SHA}')
    data = SystemCall(f'git tag {cur_tag} {SHA}').run_outtxt(False)
    print(data)
    data = SystemCall(f'git push origin {cur_tag}').run_outtxt(False)
    print(data)
    return cur_tag


def supersedes_list(TP_path):
    # Get all the supersedes
    supersedes = glob.glob(f'{TP_path}/Shared/BaseInputs/Supersedes/code/*.dll')
    supersedes_items = ''
    for supersede in supersedes:
        supersede = os.path.basename(supersede)
        if supersedes_items == '':
            supersedes_items = supersede
        else:
            supersedes_items = supersedes_items + ', ' + supersede
    print(f'Supersedes: {supersedes_items}')
    return supersedes_items


def get_email_list(release_type, TP_path):
    check_email_list = glob.glob(f'{TP_path}/*/*/Scripts/email_list.txt')
    if check_email_list:
        email_list_path = check_email_list[0]

        with open(email_list_path, 'r') as f:
            data = f.readlines()
        daily_flag = False
        prod_flag = False
        email_To = ''
        email_CC = ''
        if release_type == 'prod':
            print(f'Using PROD release email list from {email_list_path}')
            for line in data:
                if not line.strip().startswith('#') and line.strip() != "":
                    if '==Production Release' in line:
                        prod_flag = True
                    elif '--End of Production Release' in line:
                        prod_flag = False
                        break
                    elif prod_flag and 'Email_TO' in line:
                        email_To = line.split(':')[1].strip()
                    elif prod_flag and 'Email_CC' in line:
                        email_CC = line.split(':')[1].strip()
        else:
            print(f'Using DAILY release email list from {email_list_path}')
            for line in data:
                if not line.strip().startswith('#') and line.strip() != "":
                    if '==Daily Release' in line:
                        daily_flag = True
                    elif '--End of Daily Release' in line:
                        daily_flag = False
                        break
                    elif daily_flag and 'Email_TO' in line:
                        email_To = line.split(':')[1].strip()
                    elif daily_flag and 'Email_CC' in line:
                        email_CC = line.split(':')[1].strip()

    else:
        if release_type == 'prod':
            print('Using default PROD release email list.')
            email_To = "Boddy, Aaron J <aaron.j.boddy@intel.com>; PDQe_DDG_Lab_Ops&Maint <pdqe_ddg_lab_ops.maint@intel.com>; Adyani, Rod <rod.adyani@intel.com>; Papierski, Dennis J <dennis.j.papierski@intel.com>; Rodriguez, Jorge R <jorge.r.rodriguez@intel.com>; 'mpe-testprogram-cascade-release@eclists.intel.com'; 'sttdpde_client_graphics@intel.com'; MPE CRVLE Client Planning <mpe.crvle.client.planning@intel.com>; MPE CRVLE Planning Techs <mpe.crvle.planning.techs@intel.com>"
            email_CC = "MPE_DDG_PDE_10n_TP_TEAM <mpe_ddg_pde_10n_tp_team@intel.com>; 'mpe-mtl-tpd-team@eclists.intel.com'"
        else:
            print('Using default DAILY release email list.')
            email_To = "Boddy, Aaron J <aaron.j.boddy@intel.com>; PDQe_DDG_Lab_Ops&Maint <pdqe_ddg_lab_ops.maint@intel.com>; Adyani, Rod <rod.adyani@intel.com>; Papierski, Dennis J <dennis.j.papierski@intel.com>; Rodriguez, Jorge R <jorge.r.rodriguez@intel.com>; 'mpe-testprogram-cascade-release@eclists.intel.com'; MPE CRVLE Client Planning <mpe.crvle.client.planning@intel.com>; MPE CRVLE Planning Techs <mpe.crvle.planning.techs@intel.com>"
            email_CC = "MPE_DDG_PDE_10n_TP_TEAM <mpe_ddg_pde_10n_tp_team@intel.com>; Ravindran, Sathyajith <sathyajith.ravindran@intel.com>; 'mpe-mtl-tpd-team@eclists.intel.com'"

    return email_To, email_CC


def daily_release_email(daily_release_note_input_path):

    # Reading input file
    if os.path.exists(daily_release_note_input_path):
        print(f'Input file exists: {daily_release_note_input_path}')
        with open(daily_release_note_input_path, errors='ignore') as f:
            f_lines = f.readlines()
            for line in f_lines:
                if 'TestProgram' in line:
                    TestProgram = line.split(':')[1].strip()
                    print(f"TestProgram: {TestProgram}")
                if 'Special_Notes:' in line:
                    Notes = line.split(':')[1].strip()
                    print(f"Special_Notes: {Notes}")
                if 'Issue:' in line:
                    Issue = line.split(':')[1].strip()
                    print(f"Issue: {Issue}")
    else:
        print(f'{daily_release_note_input_path} does NOT exist, please check the file path.')
        exit(1)
    short_name = TestProgram[10:15]

    # Find TP Path
    TP_path = get_TP_Path(TestProgram)
    if TP_path == 0:
        exit(1)

    # Checking if the TP exists in V drive:
    if os.path.exists(TP_path):
        print(f'Found the test program: {TP_path}')
    else:
        print(f'No Test Program found at {TP_path}')
        exit(1)

    # Checking BOM:
    for stpl_item in glob.glob(f'{TP_path}/*TP/*/*.stpl'):
        print(stpl_item)
        bomgroup = stpl_item.replace('/', '\\').split('\\')[-1].split('_')[2]
        BOM_folder = stpl_item.replace('/', '\\').split('\\')[-2]
        print(f'{BOM_folder}: {bomgroup}')

    # Prime vs EVG script
    prime_EVG_indicator(TP_path, BOM_folder, TestProgram)
    # Get and copy CleanTP report
    get_cleantp_report(TP_path)
    integration_report = f'.\\POR_TP\\{BOM_folder}\\Reports\\Integration_Report.txt'
    print(f'Integration Report: {integration_report}')

    # Getting ENV File variables
    ENV_path = f"{TP_path}/POR_TP/{BOM_folder}/EnvironmentFile.env"
    if(os.path.exists(ENV_path)):
        with open(ENV_path, errors='ignore') as f_env:
            f_env_lines = f_env.readlines()
            FUSE_ROOT_DIR_C28 = 'N/A'
            FUSE_ROOT_DIR_C68 = 'N/A'
            FUSE_ROOT_DIR_GLG = 'N/A'
            FUSE_ROOT_DIR_GMD = 'N/A'
            FUSE_ROOT_DIR_IOEP = 'N/A'
            FUSE_ROOT_DIR_SXM = 'N/A'
            FUSE_ROOT_DIR_SXS = 'N/A'
            FSM_FILE_PATH = 'N/A'
            PUP_PATTERNS_DIR = 'N/A'
            for line in f_env_lines:
                if 'FUSE_ROOT_DIR = ' in line:
                    FUSE_ROOT_DIR = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR: {FUSE_ROOT_DIR}")
                elif 'FUSE_ROOT_DIR_C68 = ' in line:
                    FUSE_ROOT_DIR_C68 = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_C68: {FUSE_ROOT_DIR_C68}")
                elif 'FUSE_ROOT_DIR_GLG = ' in line:
                    FUSE_ROOT_DIR_GLG = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_GLG: {FUSE_ROOT_DIR_GLG}")
                elif 'FUSE_ROOT_DIR_GMD = ' in line:
                    FUSE_ROOT_DIR_GMD = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_GMD: {FUSE_ROOT_DIR_GMD}")
                elif 'FUSE_ROOT_DIR_IOEP = ' in line:
                    FUSE_ROOT_DIR_IOEP = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_IOEP: {FUSE_ROOT_DIR_IOEP}")
                elif 'FUSE_ROOT_DIR_SXM = ' in line:
                    FUSE_ROOT_DIR_SXM = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_SXM: {FUSE_ROOT_DIR_SXM}")
                elif 'FUSE_ROOT_DIR_SXS = ' in line:
                    FUSE_ROOT_DIR_SXS = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_SXS: {FUSE_ROOT_DIR_SXS}")
                elif 'FUSE_ROOT_DIR_C28 = ' in line:
                    FUSE_ROOT_DIR_C28 = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_C28: {FUSE_ROOT_DIR_C28}")
                elif 'TP_TOS = ' in line:
                    TOS_Profile = line.split('\"')[1]
                    print(f"TOS_Profile: {TOS_Profile}")
                elif 'EVERGREEN_BASE = ' in line:
                    EVERGREEN_BASE = line.split('\"')[1]
                    print(f"EVERGREEN_BASE: {EVERGREEN_BASE}")
                elif 'PRIME_BASE = ' in line:
                    PRIME_BASE = line.split('\"')[1]
                    print(f"PRIME_BASE: {PRIME_BASE}")
                elif 'FSM_FILE_PATH = ' in line:
                    FSM_FILE_PATH = line.split('\"')[1]
                    print(f"FSM_FILE_PATH: {FSM_FILE_PATH}")
                elif 'PUP_PATTERNS_DIR = ' in line:
                    PUP_PATTERNS_DIR = line.split('\"')[1]
                    print(f"PUP_PATTERNS_DIR: {PUP_PATTERNS_DIR}")

    else:
        print(f"{ENV_path} does NOT exist!")
        exit(1)

    # Getting repo sha id
    repo_sha = f"{TP_path}/POR_TP/{BOM_folder}/Reports/RepoRev.txt"
    repo_sha_id = get_repo_sha_id(repo_sha)

    # Adding Tag to the test program:
    if repo_sha_id != 'N/A':
        cur_tag = setting_Tags(short_name, repo_sha_id)

    # Getting skipped modules
    skipped_modules_list = []
    skipped_modules_path = f"{TP_path}/POR_TP/{BOM_folder}/SkipModules"
    if os.path.exists(skipped_modules_path):
        for module in glob.glob(f'{skipped_modules_path}/*.txt'):
            module = module.split('\\')[-1].split('.')[0]
            print(module)
            skipped_modules_list.append(module)
    else:
        skipped_modules_list = ['None']

    skipped_modules = ''
    for item in skipped_modules_list:
        if item == 'None':
            skipped_modules = 'None'
        else:
            if skipped_modules == '':
                skipped_modules = item
            else:
                skipped_modules = skipped_modules + ', ' + item

    # Getting supersedes info
    supersedes = supersedes_list(TP_path)

    # Getting today date
    today = date.today()
    header1 = f"Test Program {TestProgram} {bomgroup} Daily Release Report"
    header2 = f"Release Date {today}"
    # Table
    table = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"

    table += f"""<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'><pre>{header1}
{header2}</pre></td></tr>"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Name</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TestProgram}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Path</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TP_path}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Integration Report</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{integration_report}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Special Notes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Notes}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Issues</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Issue}</td>
    </tr>\n"""

    # NOT PRINTING FSM and PUP for ARL
    if 'ARL' not in TestProgram:
        table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>FSM File Path</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{FSM_FILE_PATH}</td>
        </tr>\n"""
        table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>PUP Release</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{PUP_PATTERNS_DIR}</td>
        </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Fuse Path</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>
            <pre>FUSE_ROOT_DIR = "{FUSE_ROOT_DIR}"
FUSE_ROOT_DIR_C68 = "{FUSE_ROOT_DIR_C68}"
FUSE_ROOT_DIR_C28 = "{FUSE_ROOT_DIR_C28}"
FUSE_ROOT_DIR_GLG = "{FUSE_ROOT_DIR_GLG}"
FUSE_ROOT_DIR_GMD = "{FUSE_ROOT_DIR_GMD}"
FUSE_ROOT_DIR_IOEP = "{FUSE_ROOT_DIR_IOEP}"
FUSE_ROOT_DIR_SXM = "{FUSE_ROOT_DIR_SXM}"
FUSE_ROOT_DIR_SXS = "{FUSE_ROOT_DIR_SXS}"</pre>
        </td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>TOS Profile</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TOS_Profile}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>EVERGREEN BASE</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{EVERGREEN_BASE}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>PRIME BASE</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{PRIME_BASE}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Repo SHA ID</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{repo_sha_id}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Skipped Modules</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{skipped_modules}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Supersedes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{supersedes}</td>
    </tr>\n"""
    table += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>PR List Reports </td></tr>\n"
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>PR Number</td>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Title</td>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Submitted By</td>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>URL</td>
    </tr>\n"""
    PR_report_file = get_PR_report_file(short_name)
    if os.path.exists(PR_report_file):
        with open(PR_report_file) as f:
            f_lines = f.readlines()
        for line in f_lines:
            PR_num = line.split(',')[0].split(':')[1].strip()
            start = line.find('title: ') + 7
            end = line.find('MergedAt:')
            title = line[start:end - 2]
            start = line.find('Submitted by: ') + 14
            end = line.find('url: ')
            owner = line[start:end - 2]
            url = line.split(',')[-1].split(':', 1)[1].strip()
            table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td style='padding-right:15px; font-size:12px;'>{PR_num}</td>
            <td style='padding-right:15px; font-size:12px;'>{title}</td>
            <td style='padding-right:15px; font-size:12px;'>{owner}</td>
            <td style='padding-right:15px; font-size:12px;'>{url}</td>
        </tr>\n"""
        table += "</table>\n"
    else:
        print(f"PR report does NOT exist: {PR_report_file}")
        table += "</table>\n"

    # Create report file
    report_file = get_daily_report_file(integration_report, short_name)

    if report_file == 0:
        exit(1)

    if os.path.exists(report_file):
        os.remove(report_file)

    f = open(report_file, "a")

    f.write("<html style=\"font-family: Calibri; font-size: 12px;\">\n")
    f.write("<head>\n")
    f.write(f"<title>{header1}</title>\n")
    f.write("</head>")
    f.write("<body>\n")
    f.write(f"<h1>{table}</h1>\n \
           <h2 style = 'font-size: 12px;'>For more details, please contact: mpe_ddg_pde_10n_tp_team@intel.com</h2>\n</body></html>")

    f.close()
    # Getting email list from the test program
    email_to, email_cc = get_email_list('daily', TP_path)
    if IS_WIN:
        # Create the Email
        outlook = win32com.client.Dispatch('Outlook.Application')

        mail = outlook.CreateItem(0)
        mail.To = email_to
        mail.CC = email_cc
        mail.Subject = f"Test Program {TestProgram} {bomgroup} Daily Release Report"
        mail.HTMLBody = """
        <html style="font-family: Calibri; font-size:12px;">
        <body>
        <p>Hello Team,</p>
        <p>Here is the Daily Release Notes for test program """ + TestProgram + """.</p>
        """ + table + """<p>Thank you</p></body></html>"""
        mail.Display(False)


def prod_release_email(TP_release_note):

    # Get UserInputs
    if (os.path.exists(TP_release_note)):
        with open(TP_release_note, errors='ignore') as f_note:
            f_note_lines = f_note.readlines()
            for line in f_note_lines:
                if 'TestProgram' in line:
                    TestProgram = line.split(':', 1)[1].strip()
                    print(f"TestProgram: {TestProgram}")
                elif 'Special_Notes' in line:
                    Special_Notes = line.split(':', 1)[1].strip()
                    print(f"Special_Notes: {Special_Notes}")
                elif 'sites' in line:
                    sites = line.split(':', 1)[1].strip()
                    print(f"sites: {sites}")
                elif 'Integrators' in line:
                    Integrators = line.split(':', 1)[1].strip()
                    print(f"Integrators: {Integrators}")
                elif 'TP_Owner' in line:
                    TP_Owner = line.split(':', 1)[1].strip()
                    print(f"TP_Owner: {TP_Owner}")
                elif 'Test_Operation' in line:
                    Test_Operation = line.split(':', 1)[1].strip()
                    print(f"Test_Operation: {Test_Operation}")
                elif 'Test_Temperature' in line:
                    Test_Temperature = line.split(':', 1)[1].strip()
                    print(f"Test_Temperature: {Test_Temperature}")
                elif 'Load_Time' in line:
                    Load_Time = line.split(':', 1)[1].strip()
                    print(f"Load_Time: {Load_Time}")
                elif 'Init_Time' in line:
                    Init_Time = line.split(':', 1)[1].strip()
                    print(f"Init_Time: {Init_Time}")
                elif 'TTG' in line:
                    TTG = line.split(':', 1)[1].strip()
                    print(f"TTG: {TTG}")
                elif 'Classification' in line:
                    Classification = line.split(':', 1)[1].strip()
                    print(f"Classification: {Classification}")

    else:
        print(f"{TP_release_note} does NOT exist!")
        exit(1)

    TP_path = get_TP_Path(TestProgram)

    # Checking BOM:
    for stpl_item in glob.glob(f'{TP_path}/*TP/*/*.stpl'):
        print(stpl_item)
        bomgroup = stpl_item.replace('/', '\\').split('\\')[-1].split('_')[2]
        BOM_folder = stpl_item.replace('/', '\\').split('\\')[-2]
        print(f'{BOM_folder}: {bomgroup}')

    # Prime vs EVG script
    prime_EVG_indicator(TP_path, BOM_folder, TestProgram)
    # Get and copy CleanTP report
    get_cleantp_report(TP_path)
    # Get BOM and Stepping
    if (os.path.exists(TP_path)):
        print(f"TP_path: {TP_path}")
        # BinMatrix_path = f"{TP_path}/Shared/BaseInputs/BinMatrix.flm.usrv"
        BinMatrix_path = glob.glob(f'{TP_path}/Shared/*/BinMatrix.flm.usrv')[0]
        if(os.path.exists(BinMatrix_path)):
            print(f"BinMatrix_path: {BinMatrix_path}")
            with open(BinMatrix_path, errors='ignore') as f_bm:
                f_bm_lines = f_bm.readlines()
                for line in f_bm_lines:
                    if bomgroup in line and 'TorchRulesVars.bom' in line:
                        BOM_Raw = line.split('\"')
                        BOM_list = []
                        Stepping = []
                        BOM = []
                        for item in BOM_Raw:
                            if len(item) == 10 or len(item) == 9:
                                BOM_list.append(item)
                        for item in BOM_list:

                            if item[8] == '_' or len(item) == 9:
                                rev = '0'
                            elif item[8] == 'A':
                                rev = '1'
                            elif item[8] == 'B':
                                rev = '2'
                            elif item[8] == 'C':
                                rev = '3'
                            elif item[8] == 'D':
                                rev = '4'
                            elif item[8] == 'E':
                                rev = '5'
                            elif item[8] == 'F':
                                rev = '6'
                            elif item[8] == 'G':
                                rev = '7'
                            elif item[8] == 'H':
                                rev = '8'
                            elif item[8] == 'I':
                                rev = '9'

                            if (len(item) == 9):
                                Stepping_temp = f"{item[8]}{rev}"
                            else:
                                Stepping_temp = f"{item[9]}{rev}"
                            BOM_temp = item[:6] + '*' + item[7:]
                            Stepping.append(Stepping_temp)
                            BOM.append(BOM_temp)
                        break

        else:
            print(f"{BinMatrix_path} does NOT exist!")
            exit(1)
    else:
        print(f"{TP_path} does NOT exist!")
        exit(1)

    BOM = list(dict.fromkeys(BOM))
    Stepping = list(dict.fromkeys(Stepping))
    BOM.sort()
    Stepping.sort()
    separator = ", "
    BOM = separator.join(BOM)
    Stepping = separator.join(Stepping)
    print(f'BOM: {BOM}')
    print(f'Stepping: {Stepping}')

    short_name = TestProgram[10:15]
    TP_Prod = TestProgram[0:3]
    today = date.today()

    # Set Release Note header
    header1 = f"{TestProgram} Release Memo"
    header2 = f"Class-{TP_Prod} {bomgroup} {Stepping} {short_name} Test Program"
    header3 = f"Release to {sites}"
    header4 = f"Release Date {today}"

    # Getting ENV File variables
    ENV_path = glob.glob(f"{TP_path}/*TP/*/EnvironmentFile.env")[0]

    if(os.path.exists(ENV_path)):
        with open(ENV_path, errors='ignore') as f_env:
            f_env_lines = f_env.readlines()
            FUSE_ROOT_DIR_C28 = 'N/A'
            FUSE_ROOT_DIR_C68 = 'N/A'
            FUSE_ROOT_DIR_GLG = 'N/A'
            FUSE_ROOT_DIR_GMD = 'N/A'
            FUSE_ROOT_DIR_IOEP = 'N/A'
            FUSE_ROOT_DIR_SXM = 'N/A'
            FUSE_ROOT_DIR_SXS = 'N/A'
            FSM_FILE_PATH = 'N/A'
            PUP_PATTERNS_DIR = 'N/A'
            for line in f_env_lines:
                if 'FUSE_ROOT_DIR = ' in line:
                    FUSE_ROOT_DIR = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR: {FUSE_ROOT_DIR}")
                elif 'FUSE_ROOT_DIR_C68 = ' in line:
                    FUSE_ROOT_DIR_C68 = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_C68: {FUSE_ROOT_DIR_C68}")
                elif 'FUSE_ROOT_DIR_GLG = ' in line:
                    FUSE_ROOT_DIR_GLG = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_GLG: {FUSE_ROOT_DIR_GLG}")
                elif 'FUSE_ROOT_DIR_GMD = ' in line:
                    FUSE_ROOT_DIR_GMD = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_GMD: {FUSE_ROOT_DIR_GMD}")
                elif 'FUSE_ROOT_DIR_IOEP = ' in line:
                    FUSE_ROOT_DIR_IOEP = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_IOEP: {FUSE_ROOT_DIR_IOEP}")
                elif 'FUSE_ROOT_DIR_SXM = ' in line:
                    FUSE_ROOT_DIR_SXM = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_SXM: {FUSE_ROOT_DIR_SXM}")
                elif 'FUSE_ROOT_DIR_SXS = ' in line:
                    FUSE_ROOT_DIR_SXS = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_SXS: {FUSE_ROOT_DIR_SXS}")
                elif 'FUSE_ROOT_DIR_C28 = ' in line:
                    FUSE_ROOT_DIR_C28 = line.split('\"')[1]
                    print(f"FUSE_ROOT_DIR_C28: {FUSE_ROOT_DIR_C28}")
                elif 'TP_TOS = ' in line:
                    TOS_Profile = line.split('\"')[1]
                    print(f"TOS_Profile: {TOS_Profile}")
                elif 'EVERGREEN_BASE = ' in line:
                    EVERGREEN_BASE = line.split('\"')[1]
                    print(f"EVERGREEN_BASE: {EVERGREEN_BASE}")
                elif 'PRIME_BASE = ' in line:
                    PRIME_BASE = line.split('\"')[1]
                    print(f"PRIME_BASE: {PRIME_BASE}")
                elif 'FSM_FILE_PATH = ' in line:
                    FSM_FILE_PATH = line.split('\"')[1]
                    print(f"FSM_FILE_PATH: {FSM_FILE_PATH}")
                elif 'PUP_PATTERNS_DIR = ' in line:
                    PUP_PATTERNS_DIR = line.split('\"')[1]
                    print(f"PUP_PATTERNS_DIR: {PUP_PATTERNS_DIR}")

    else:
        print(f"{ENV_path} does NOT exist!")
        exit(1)
    # Getting repo sha id
    repo_sha = f"{TP_path}/POR_TP/{BOM_folder}/Reports/RepoRev.txt"
    repo_sha_id = get_repo_sha_id(repo_sha)

    # Adding Tag to the test program:
    if repo_sha_id != 'N/A':
        cur_tag = setting_Tags(short_name, repo_sha_id)

    if 'ARL' not in TestProgram:
        if 'HDMT_TPL_DIR' in PUP_PATTERNS_DIR:
            temp_pup = '\\'.join(PUP_PATTERNS_DIR.split('\\')[1:])
            PUP_PATTERNS_DIR = f'{TP_path}\\{temp_pup}'
            print(PUP_PATTERNS_DIR)
        PUP_RELEASE = get_pup_release(PUP_PATTERNS_DIR)

        # Get Usercode
        userCode_path = f"{TP_path}/UserCode/dlls/ReleaseNote.html"
        if(os.path.exists(userCode_path)):
            with open(userCode_path, errors='ignore') as f_usr:
                f_usr_lines = f_usr.readlines()
                for line in f_usr_lines:
                    if 'prime_v' in line:
                        User_Code_rev = line.split('>')[2].split('<')[0]
                        print(f"User_Code_rev: {User_Code_rev}")
                        User_Code = f"I:\\tpapps\\userlibs\\mtl\\{User_Code_rev}"
                        print(f"User_Code: {User_Code}")
        else:
            print(f"{userCode_path} does NOT exist!")
            exit(1)

    # Getting skipped modules
    skipped_modules_list = []
    skipped_modules_path = f"{TP_path}/POR_TP/{BOM_folder}/SkipModules"
    if os.path.exists(skipped_modules_path):
        for module in glob.glob(f'{skipped_modules_path}/*.txt'):
            module = module.split('\\')[-1].split('.')[0]
            print(module)
            skipped_modules_list.append(module)
    else:
        skipped_modules_list = ['None']

    skipped_modules = ''
    for item in skipped_modules_list:
        if item == 'None':
            skipped_modules = 'None'
        else:
            if skipped_modules == '':
                skipped_modules = item
            else:
                skipped_modules = skipped_modules + ', ' + item

    # Getting supersedes info
    supersedes = supersedes_list(TP_path)

    # Get Handler recipe
    if 'ARL' in TestProgram:
        Handler_Re_path = "I:\\hdmx_rms\\module_recipe\\hdmx\\prod\\mtl\\mtl_p682_mz_ct_arlp_20a"
    elif 'MTL' in TestProgram:
        Handler_Re_path = "I:\\hdmx_rms\\module_recipe\\hdmx\\prod\\mtl\\mtl_p682_mz_ct"
    else:
        print(f'Could NOT find the Handler recipe in {TestProgram}. Please check the test program name is correct.')
        exit(1)
    Handler_Rev = get_handler_re_path(Handler_Re_path)

    # Test Program Summary Information
    Products = f"{TP_Prod} {bomgroup} {Stepping}"

    # Test Program Files for Loadings
    TP_Base_Dir = TP_path.replace('/', '\\')
    TPL = "BaseTestPlan.tpl"
    STPL = f"POR_TP\\{BOM_folder}\\SubTestPlan_CLASS_{bomgroup}_g.stpl"
    Plist = f"POR_TP\\{BOM_folder}\\PLIST_ALL_CLASS_{bomgroup}.plist.xml"
    if 'ARL' in TestProgram:
        SOC = f"Shared\\BaseInputs\\CLASS_{bomgroup}_HDMT_1.soc"
    elif 'MTL' in TestProgram:
        SOC = f"Shared\\BaseInputs\\{TP_Prod}_{bomgroup}_HDMT_1.soc"
    else:
        print("Could NOT find the SOC file in the test program.")
        exit(1)
    ENV = f"POR_TP\\{BOM_folder}\\EnvironmentFile.env"
    BOM_Groups = f"CLASS_{bomgroup}"
    DLCP = ""
    record_flag = False
    data_dict = {}
    Integ_report = f"{TP_path}/POR_TP/{BOM_folder}/Reports/Integration_Report.txt"

    if(os.path.exists(Integ_report)):
        with open(Integ_report, errors='ignore') as f:
            f_lines = f.readlines()
            for line in f_lines:
                if '<TP Modules>' in line:
                    record_flag = True
                if (record_flag):
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
                            comment = raw_data.split("\"")[1].strip()
                            data = raw_data.split("\"")[0].replace("   ", "#").strip().split("#")
                            data_array = []
                            for item in data:
                                if item != '':
                                    data_array.append(item.strip())
                            if (len(data_array) == 3):
                                moduleName = data_array[0]
                                owner = data_array[1]
                                timeStamp = data_array[2].split(" ")[0]

                            data_dict[moduleName] = [owner, timeStamp, comment]
                        else:
                            continue
    else:
        print(f"{Integ_report} does NOT exist!")
        exit(1)

    table1 = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"

    table1 += f"""<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'><pre>{header1}
{header2}
{header3}
{header4}</pre></td></tr>"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Objective/Special Notes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Special_Notes}</td>
    </tr>\n"""
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Summary Information</td></tr>\n"
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Name</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TestProgram}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Short Name [Nick Name]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{short_name}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Products/Subfamily</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Products}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Integrator</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Integrators}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Product Owner</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TP_Owner}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Fuse Path</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>
            <pre>FUSE_ROOT_DIR = "{FUSE_ROOT_DIR}"
FUSE_ROOT_DIR_C68 = "{FUSE_ROOT_DIR_C68}"
FUSE_ROOT_DIR_C28 = "{FUSE_ROOT_DIR_C28}"
FUSE_ROOT_DIR_GLG = "{FUSE_ROOT_DIR_GLG}"
FUSE_ROOT_DIR_GMD = "{FUSE_ROOT_DIR_GMD}"
FUSE_ROOT_DIR_IOEP = "{FUSE_ROOT_DIR_IOEP}"
FUSE_ROOT_DIR_SXM = "{FUSE_ROOT_DIR_SXM}"
FUSE_ROOT_DIR_SXS = "{FUSE_ROOT_DIR_SXS}"</pre>
        </td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Handler Rev</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Handler_Rev}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>TOS Profile</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TOS_Profile}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>EVERGREEN BASE</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{EVERGREEN_BASE}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>PRIME BASE</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{PRIME_BASE}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Skipped Modules</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{skipped_modules}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Supersedes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{supersedes}</td>
    </tr>\n"""
    if 'ARL' not in TestProgram:
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>User Code</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{User_Code}</td>
        </tr>\n"""
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>FSM File Path</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{FSM_FILE_PATH}</td>
        </tr>\n"""
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>PUP Release</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{PUP_RELEASE}</td>
        </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Operations</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Test_Operation}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Temperature(s)</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Test_Temperature}</td>
    </tr>\n"""
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Files for Loadings</td></tr>\n"
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>TP Base Dir</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TP_Base_Dir}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Plan</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TPL}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Sub-Test Plan</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{STPL}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Plist Reference</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Plist}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Socket File</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{SOC}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Environment File</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{ENV}</td>
    </tr>\n"""
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Key Test Program Metrics </td></tr>\n"
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Load Time [mins]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Load_Time}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Init Time [mins]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Init_Time}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Time Good [min]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TTG}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>BOM Definition</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{BOM}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Stepping</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Stepping}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Classification</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Classification}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>BOM Groups</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{BOM_Groups}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Valid DLCP Characters</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{DLCP}</td>
    </tr>\n"""
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Change List</td></tr>\n"
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>PR Number</td>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Title</td>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Submitted By</td>
        <td style='padding-right:15px; font-weight: bold; font-size:12px;'>URL</td>
    </tr>\n"""
    release_key = short_name[0:4]
    # Find all the relevant report in report folder
    list_reports = get_list_PR_report(release_key)
    for report_file in list_reports:
        with open(report_file) as f:
            f_lines = f.readlines()
        for line in f_lines:
            PR_num = line.split(',')[0].split(':')[1].strip()
            start = line.find('title: ') + 7
            end = line.find('MergedAt:')
            title = line[start:end - 2]
            start = line.find('Submitted by: ') + 14
            end = line.find('url: ')
            owner = line[start:end - 2]
            url = line.split(',')[-1].split(':', 1)[1].strip()
            table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td style='padding-right:15px; font-size:12px;'>{PR_num}</td>
            <td style='padding-right:15px; font-size:12px;'>{title}</td>
            <td style='padding-right:15px; font-size:12px;'>{owner}</td>
            <td style='padding-right:15px; font-size:12px;'>{url}</td>
            </tr>\n"""
    table1 += "</table>\n"

    report_file = get_report_file(BOM_Groups, short_name)

    f = open(report_file, "a")

    f.write("<html style=\"font-family: Calibri; font-size: 12px;\">\n")
    f.write("<head>\n")
    f.write(f"<title>{header1}</title>\n")
    f.write("</head>")
    f.write("<body>\n")
    f.write(f"<h1>{table1}</h1>\n \
           <h2 style = 'font-size: 12px;'>For more details, please contact: mpe_ddg_pde_10n_tp_team@intel.com</h2>\n</body></html>")

    f.close()
    ctp_img = ''
    scn_coverage_img = ''
    if 'ARL' in TP_path and 'S68' in BOM_folder:
        ctp_img = glob.glob(f'I:/engineering/dev/team_classtp/dashboard/ARL_S68/ctp/*.jpg')[0]
        scn_coverage_img = glob.glob(f'I:/engineering/dev/team_classtp/dashboard/ARL_S68/scan_coverage/*.jpg')[0]

    # Getting email list from the test program
    email_to, email_cc = get_email_list('prod', TP_path)

    if IS_WIN:
        # Create the Email
        outlook = win32com.client.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)
        mail.To = email_to
        mail.CC = email_cc
        mail.Subject = f"{TP_Prod} {bomgroup} {Stepping} Class {TestProgram} TP Release Notes"

        if os.path.exists(ctp_img):
            mail.HTMLBody = """
            <html style="font-family: Calibri; font-size: 12px;">
            <body>
            <p>Hello Team,</p>
            <p>Here is the Test Program Release Notes for test program """ + TestProgram + """.</p>
            """ + table1 + """
            <p style="font-size: 16px; font-weight: bold">TP Content Enabling Status by Module Team</p>
            <p><img src=\"""" + ctp_img + """\" alt="TP Content Enabling Status by Module Team"></p>
            <p style="font-size: 16px; font-weight: bold">SCAN Coverage</p>
            <p><img src=\"""" + scn_coverage_img + """\" alt="Scan Coverage"></p>
            <p>Thank you</p></body></html>"""
        else:
            mail.HTMLBody = """
            <html style="font-family: Calibri; font-size: 12px;">
            <body>
            <p>Hello Team,</p>
            <p>Here is the Test Program Release Notes for test program """ + TestProgram + """.</p>
            """ + table1 + """
            <p>Thank you</p></body></html>"""

        mail.Display(False)


def main():     # pragma: no cover
    """
    Usage 1 for nightly correlation release: testprogram_release.py -script daily -path path-to-testprogram_release_notes.txt
    Usage 2 for production test program release: testprogram_release.py -script prod -path path-to-testprogram_release_notes.txt
    """
    parser = argparse.ArgumentParser(description='Test Program release script')
    parser.add_argument('-script', '--script', help='Please choose \'daily\' or \'prod\' option for -script', required=True)
    parser.add_argument('-path', '--path', help='Path to your release/daily note', required=True)

    args = parser.parse_args()

    # Access the values using args.script and args.path
    script = args.script
    path = args.path
    print(f"Script: {script}, path: {path}")

    # Checking git repo
    current_directory = os.getcwd()
    git_directory = isGitrepo(current_directory)
    if git_directory == 1:
        print(f'{current_directory} is Git repository.')
    else:
        print(f'{current_directory} is NOT Git repository. Please run the testprogram_release.py in a Git repo. Exit...')
        exit(1)

    # Checking script option
    if script == 'daily':
        print('Calling daily integration release note.')
        daily_release_email(path)
    elif script == 'prod':
        print('Calling production test program release note.')
        prod_release_email(path)
    else:
        print(f'script is {script} which not an invalid option. Please choose \'daily\' or \'prod\'.')
        exit(1)


if __name__ == "__main__":   # pragma: no cover
    main()
