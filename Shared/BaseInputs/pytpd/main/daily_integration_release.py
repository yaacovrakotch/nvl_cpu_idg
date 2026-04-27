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

try:
    import win32com.client
except ImportError:
    pass


def input_daily_release_note():
    TP_release_note = "TP_release_note.txt"
    return TP_release_note


def isGitrepo(current_directory):
    print(f'Current directory: {current_directory}')
    git_path = os.path.join(current_directory, '.git')
    if os.path.exists(git_path):
        return 1
    else:
        return 0


def find_TP_Path(TestProgram):
    if 'MTL' in TestProgram:
        TP_path = f'I:/tpvalidation/hdmxprogs/mtl/{TestProgram}'
        return TP_path
    elif 'ARL' in TestProgram:
        TP_path = f'I:/tpvalidation/hdmxprogs/arl/{TestProgram}'
        prime_EVG_indicator(TP_path)
        return TP_path
    else:
        print(f'Cannot find the test program path for TestProgram')
        return 0


def prime_EVG_indicator(TP_path):
    # Generate Prime vs EVG indicator
    cmd = f'python -u I:/engtools/tptools/mtl/beta/latest/main/tp_audit.py {TP_path} -evg'
    log.info(f'CMD: {cmd}')
    code, out = SystemCall(cmd).run_outtxt()
    log.info(out)

    # Generate the Prime vs EVG details indicator
    cmd = f'python -u I:/engtools/tptools/mtl/beta/latest/main/tp_audit.py {TP_path} -evg -detail'
    log.info(f'CMD: {cmd}')
    code, out = SystemCall(cmd).run_outtxt()
    log.info(out)


def get_tp_report_file(integration_report, short_name):
    if 'P28' in integration_report:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP281\\DAILY\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    elif 'P68' in integration_report:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP682\\DAILY\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    elif 'H68' in integration_report:
        report_file = f"I:\\engineering\\dev\\team_classtp\\dashboard\\DailyReleaseNotes\\{short_name}.html"
        return report_file

    else:
        print('Cannot find the correct BOMGROUP to generate the daily report. Please contact script owner for the details.')
        return 0


def get_PR_report_file(short_name):
    report_file = f'I:/engineering/dev/team_classtp/torch/PR_reports/{short_name}.txt'
    return report_file


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


def release_email(daily_release_note_input_path):

    # Reading input file
    if os.path.exists(daily_release_note_input_path):
        print(f'Input file exists: {daily_release_note_input_path}')
        with open(daily_release_note_input_path, errors='ignore') as f:
            f_lines = f.readlines()
            for line in f_lines:
                if 'TestProgram' in line:
                    TestProgram = line.split(':')[1].strip()
                    print(f"TestProgram: {TestProgram}")
                if 'Notes:' in line:
                    Notes = line.split(':')[1].strip()
                    print(f"Notes: {Notes}")
                if 'Issue:' in line:
                    Issue = line.split(':')[1].strip()
                    print(f"Issue: {Issue}")
                if 'Validation_Result:' in line:
                    Validation_Result = line.split(':')[1].strip()
                    print(f"Validation_Result: {Validation_Result}")
    else:
        print(f'{daily_release_note_input_path} does NOT exist, please check the file path name.')
        exit(1)
    short_name = TestProgram[10:15]

    # Find TP Path
    TP_path = find_TP_Path(TestProgram)
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
        print(bomgroup)

    if 'P68' in bomgroup:
        BOM_folder = 'Class_MTL_P68'
    elif 'P28' in bomgroup:
        BOM_folder = 'Class_MTL_P28'
    elif 'H68' in bomgroup:
        BOM_folder = 'Class_ARL_H68'
    else:
        print(f'Could NOT find correct BOM in {bomgroup}')
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
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Validation Result</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px; font-weight: bold;'>{Validation_Result}</td>
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
FUSE_ROOT_DIR_SXM = "{FUSE_ROOT_DIR_SXM}"</pre>
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
    report_file = get_tp_report_file(integration_report, short_name)

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

    if IS_WIN:
        # Create the Email
        outlook = win32com.client.Dispatch('Outlook.Application')

        mail = outlook.CreateItem(0)
        mail.To = "Matheson, Don L <don.l.matheson@intel.com>; McGlothin, Darron <darron.mcglothin@intel.com>; Boddy, Aaron J <aaron.j.boddy@intel.com>; MPE_DDG_Lab_Ops&Maint <mpe_ddg_lab_ops.maint@intel.com>; Adyani, Rod <rod.adyani@intel.com>; Papierski, Dennis J <dennis.j.papierski@intel.com>; Rodriguez, Jorge R <jorge.r.rodriguez@intel.com>; 'mpe-testprogram-cascade-release@eclists.intel.com'; MPE CRVLE Client Planning <mpe.crvle.client.planning@intel.com>; MPE CRVLE Planning Techs <mpe.crvle.planning.techs@intel.com>"
        mail.CC = "MPE_DDG_PDE_10n_TP_TEAM <mpe_ddg_pde_10n_tp_team@intel.com>; Ravindran, Sathyajith <sathyajith.ravindran@intel.com>; Ruiwale, Sameer <sameer.ruiwale@intel.com>; 'mpe-mtl-tpd-team@eclists.intel.com'"
        mail.Subject = f"Test Program {TestProgram} {bomgroup} Daily Release Report"
        mail.HTMLBody = """
        <html style="font-family: Calibri; font-size:12px;">
        <body>
        <p>Hello Team,</p>
        <p>Here is the Daily Release Notes for test program """ + TestProgram + """.</p>
        """ + table + """<p>Thank you</p></body></html>"""
        mail.Display(False)


def main(daily_release_note_input_path):     # pragma: no cover
    current_directory = os.getcwd()
    git_directory = isGitrepo(current_directory)
    if git_directory == 1:
        print(f'{current_directory} is Git repository.')
    else:
        print(f'{current_directory} is NOT Git repository. Please run the daily_integration_release.py in a Git repo. Exit...')
        exit(1)

    release_email(daily_release_note_input_path)


if __name__ == "__main__":   # pragma: no cover
    main(sys.argv[1].strip())
