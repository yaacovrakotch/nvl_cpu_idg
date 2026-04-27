from setenv import ROOT_ENV      # must be first in the imports
from gadget.shell import SystemCall
from gadget.pylog import log
from tp.testprogram import Env
from gadget.shell import IS_UNIX, IS_WIN
from gadget.disk import Chdir
from gadget.data_host import DataHost
import os
from subprocess import call, run
import json
from datetime import datetime, date
import argparse
import shutil
import glob

try:
    import win32com.client
    import pythoncom
except ImportError:
    pass


def get_cleantp_report(TestProgram, tp_name):
    cleantp_json = f'{TestProgram}/Reports/Cleantp.json'
    cleantp_fullReport = f'{TestProgram}/Reports/Cleantp_fullreport.csv'
    if not os.path.exists(cleantp_json):
        return 0
    log.info(f'CleanTP: {cleantp_json}')
    if 'Class_NVL' in cleantp_json:
        cleantp_dashboard_dir = 'I:/tpvalidation/engtools/tptools/mtl/infra/dashboard/NVL/CleanTP'
        cleantp_path = f'{cleantp_dashboard_dir}/{tp_name}'
        if not os.path.exists(cleantp_path):
            os.mkdir(cleantp_path)
        cleantp_json_dest = f'{cleantp_path}/Cleantp.json'
        cleantp_fullReport_dest = f'{cleantp_path}/Cleantp_fullreport.csv'
        log.info(f'Copy cleanTP files to dashboard folder {cleantp_path}')
        shutil.copy(cleantp_json, cleantp_json_dest)
        shutil.copy(cleantp_fullReport, cleantp_fullReport_dest)


def get_handler_re_path(Handler_Re_path):
    # Handler_Re_path = "I:\\hdmx_rms\\module_recipe\\hdmx\\prod\\mtl\\mtl_p682_mz_ct"
    all_subdirs = []
    if(os.path.exists(Handler_Re_path)):
        for item in os.listdir(Handler_Re_path):
            item_path = f"{Handler_Re_path}\\{item}"
            if os.path.isdir(item_path):
                all_subdirs.append(item_path)
        latest_subdir = max(all_subdirs, key=os.path.getmtime)
        log.info(f"latest_subdir: {latest_subdir}")
        Handler_Rev = latest_subdir.split('\\')[-1].strip()
        log.info(f"Handler_Rev: {Handler_Rev}")
        return Handler_Rev

    else:
        log.info(f"{Handler_Re_path} does NOT exist!")
        exit(1)


def get_pup_release(PUP_PATTERNS_DIR):
    if PUP_PATTERNS_DIR != 'N/A':
        if os.path.exists(PUP_PATTERNS_DIR):
            latest_file = f'{PUP_PATTERNS_DIR}/latest.txt'
            if os.path.exists(latest_file):
                with open(latest_file, 'r') as f_pup:
                    version = f_pup.read().strip()
                    PUP_RELEASE = f'{PUP_PATTERNS_DIR}\\{version}'
                    log.info(f"PUP_PATTERNS_DIR: {PUP_RELEASE}")
                    return PUP_RELEASE
            else:
                return PUP_PATTERNS_DIR.replace('/', '\\')
        else:
            log.info(f"{PUP_PATTERNS_DIR} does NOT exist!")
            exit(1)
    else:
        return 'N/A'


def get_report_file(bomgroup, short_name):
    report_file = f"I:/tpvalidation/engtools/tptools/mtl/infra/dashboard/NVL/{bomgroup}/{short_name}.html"

    if os.path.exists(report_file):
        os.remove(report_file)

    return report_file


def get_PR_report_file(short_name, dielet_bit='EN', TestProgram='N/A'):
    """
    Get the pr report file.
    If the pr report does not exist inside the TestProgram/Reports folder. Use this file
    If not, Get the report in the backup folder I:/tpvalidation/engtools/tptools/mtl/infra/torch/PR_reports.

    :param short_name: tp current name
    :param dielet_bit: 2 digit dielet bit
    :param TestProgram: TP Path
    """
    tp_report_dir = f'{TestProgram}/Reports'
    if dielet_bit[0] == 'S':
        report_file = f'{tp_report_dir}/{short_name}.json'
        if os.path.exists(report_file):
            log.info(f'Found PR report file: {report_file}')
        else:
            report_file = f'I:/tpvalidation/engtools/tptools/mtl/infra/torch/PR_reports/{short_name}.json'
    else:
        report_file = f'{tp_report_dir}/{dielet_bit}_{short_name}.json'
        if os.path.exists(report_file):
            log.info(f'Found PR report file: {report_file}')
        else:
            report_file = f'I:/tpvalidation/engtools/tptools/mtl/infra/torch/PR_reports/{dielet_bit}_{short_name}.json'
    return report_file


def get_list_PR_report(release_key):
    list_PR_report = glob.glob(f'I:/tpvalidation/engtools/tptools/mtl/infra/torch/PR_reports/{release_key}*.txt')
    return list_PR_report


def get_repo_sha_id(data):
    """ Get repo SHA id"""
    NVL_CPU = data.get('nvl.cpu', 'N/A')
    NVL_GCD = data.get('nvl.gcd', 'N/A')
    NVL_HUB = data.get('nvl.hub', 'N/A')
    NVL_PCD = data.get('nvl.pcd', 'N/A')
    NVL_COMMON = data.get('nvl.common', 'N/A')
    repo_sha_id = {'nvl-cpu': NVL_CPU, 'nvl-gcd': NVL_GCD, 'nvl-hub': NVL_HUB, 'nvl-pcd': NVL_PCD, 'nvl-common': NVL_COMMON}
    return repo_sha_id


def setting_Tags(cur_TP, repo_name, SHA, dielet_bit='EN'):        # pragma: no cover  - Only system Call, no cover
    """
    Setting tag for 5 repos.
    """
    log.info("Setup ENV proxy")
    os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'

    repos_path = f"I:/tpvalidation/engtools/tptools/mtl/infra/torch/repos/{repo_name.replace('-', '.')}"

    with Chdir(f'{repos_path}'):

        log.info(f'Current directory: {os.getcwd()}')
        SystemCall('git reset --hard', disp=True).run_outtxt(False)
        SystemCall('git pull', disp=True).run_outtxt(False)
        SystemCall('git fetch', disp=True).run_outtxt(False)

        # Checking if current TAG exists
        if dielet_bit[0] == 'S':
            cur_tag = f'TP_{cur_TP}'
        else:
            cur_tag = f'{dielet_bit}_{cur_TP}'

        data = SystemCall(f'git tag -l {cur_tag}', disp=True).run_outtxt(False)
        if cur_tag in data:
            log.info(f'{cur_tag} exits. Remove the tag {cur_tag}')

            # Remove the tag locally
            data = SystemCall(f'git tag -d {cur_tag}', disp=True).run_outtxt(False)
            log.info(data)

            # Remove the tag on the github
            data = SystemCall(f'git push --delete origin {cur_tag}', disp=True).run_outtxt(False)
            log.info(data)

        # Adding a tag on the current SHA
        log.info(f'Adding new tag CMD: git tag {cur_tag} {SHA}')
        data = SystemCall(f'git tag {cur_tag} {SHA}').run_outtxt(False)
        log.info(data)
        data = SystemCall(f'git push origin {cur_tag}').run_outtxt(False)
        log.info(data)
        return cur_tag


def supersedes_list(tp_path):
    # Get all the supersedes
    supersedes = (glob.glob(f'{tp_path}/Shared/BaseInputs/Common/Supersedes/code/*.dll') +
                  glob.glob(f'{tp_path}/BaseInputs/*/*_Torch/Supersedes/code/*.dll'))
    all_supersedes = []
    for supersede in supersedes:
        supersede = supersede.replace(f'{tp_path}/', '')
        all_supersedes.append(supersede)
    log.info(f"Supersedes list: {all_supersedes}")
    return all_supersedes


def get_email_list(classification):
    # Check for custom email list path from environment variable
    custom_email_list = os.environ.get('CUSTOM_EMAIL_LIST_PATH')
    if custom_email_list and os.path.exists(custom_email_list):
        email_list_path = custom_email_list
        log.info(f'Using custom email list from: {email_list_path}')
    else:
        # Use default path
        check_email_list = glob.glob('I:/tpvalidation/engtools/tptools/mtl/infra/torch/email_list/email_list.txt')
        if check_email_list:
            email_list_path = check_email_list[0]
            log.info(f'Using default email list from: {email_list_path}')
        else:
            email_list_path = None
            log.info('No email list file found, using hardcoded defaults')

    if email_list_path:
        with open(email_list_path, 'r') as f:
            data = f.readlines()
        daily_flag = False
        prod_flag = False
        email_to = ''
        email_cc = ''
        if classification == 'Production':
            log.info(f'Using PROD release email list from {email_list_path}')
            for line in data:
                if not line.strip().startswith('#') and line.strip() != "":
                    if '==Production Release' in line:
                        prod_flag = True
                    elif '--End of Production Release' in line:
                        prod_flag = False
                        break
                    elif prod_flag and 'Email_TO' in line:
                        email_to = line.split(':')[1].strip()
                    elif prod_flag and 'Email_CC' in line:
                        email_cc = line.split(':')[1].strip()
        else:
            log.info(f'Using Validation/Engineering release email list from {email_list_path}')
            for line in data:
                if not line.strip().startswith('#') and line.strip() != "":
                    if '==Daily Release' in line:
                        daily_flag = True
                    elif '--End of Daily Release' in line:
                        daily_flag = False
                        break
                    elif daily_flag and 'Email_TO' in line:
                        email_to = line.split(':')[1].strip()
                    elif daily_flag and 'Email_CC' in line:
                        email_cc = line.split(':')[1].strip()

    else:
        if classification == 'Production':
            log.info('Using default PROD release email list.')
            email_to = "Boddy, Aaron J <aaron.j.boddy@intel.com>; PDQe_DDG_Lab_Ops&Maint <pdqe_ddg_lab_ops.maint@intel.com>; Adyani, Rod <rod.adyani@intel.com>; Rodriguez, Jorge R <jorge.r.rodriguez@intel.com>; 'mpe-testprogram-cascade-release@eclists.intel.com'; 'sttdpde_client_graphics@intel.com'; MPE CRVLE Client Planning <mpe.crvle.client.planning@intel.com>; MPE CRVLE Planning Techs <mpe.crvle.planning.techs@intel.com>"
            email_cc = "MPE_DDG_PDE_TP_TEAM <mpe_ddg_pde_tp_team@intel.com>; 'mpe-mtl-tpd-team@eclists.intel.com'"
        else:
            log.info('Using default Validation/Engineering release email list.')
            email_to = "Boddy, Aaron J <aaron.j.boddy@intel.com>; PDQe_DDG_Lab_Ops&Maint <pdqe_ddg_lab_ops.maint@intel.com>; Adyani, Rod <rod.adyani@intel.com>; Rodriguez, Jorge R <jorge.r.rodriguez@intel.com>; 'mpe-testprogram-cascade-release@eclists.intel.com'; MPE CRVLE Client Planning <mpe.crvle.client.planning@intel.com>; MPE CRVLE Planning Techs <mpe.crvle.planning.techs@intel.com>"
            email_cc = "MPE_DDG_PDE_TP_TEAM <mpe_ddg_pde_tp_team@intel.com>; Ravindran, Sathyajith <sathyajith.ravindran@intel.com>; 'mpe-mtl-tpd-team@eclists.intel.com'"

    return email_to, email_cc


def get_tp_type(dielet_bit):
    """ Get TP Type for full TP or dielet TP or multi-dielet TP"""
    if dielet_bit[0] == 'S':
        tp_type = 'Full'
    elif dielet_bit == 'CX':
        tp_type = 'CPU'
    elif dielet_bit == 'HX':
        tp_type = 'HUB'
    elif dielet_bit == 'PX':
        tp_type = 'PCD'
    elif dielet_bit == 'GX':
        tp_type = 'GCD'
    elif dielet_bit == 'HC':
        tp_type = 'HUB-CPU'
    elif dielet_bit == 'HP':
        tp_type = 'HUB-PCD'
    elif dielet_bit == 'HG':
        tp_type = 'HUB-GCD'
    elif dielet_bit == 'GC':
        tp_type = 'GCD-CPU'
    elif dielet_bit == 'GP':
        tp_type = 'GCD-PCD'
    elif dielet_bit == 'PC':
        tp_type = 'PCD-CPU'
    elif dielet_bit == 'NC':
        tp_type = 'HUB-PCD-GCD'
    elif dielet_bit == 'NH':
        tp_type = 'CPU-PCD-GCD'
    elif dielet_bit == 'NP':
        tp_type = 'CPU-HUB-GCD'
    elif dielet_bit == 'NG':
        tp_type = 'CPU-HUB-PCD'
    else:
        tp_type = 'None'
    return tp_type


def get_stepping_from_file(tp_path, bomgroup):
    """ Read stepping value from DieletStepping.txt file """
    stepping_file = f'{tp_path}/POR_TP/{bomgroup}/InputFiles/DieletStepping.txt'
    log.info(f"Looking for stepping file: {stepping_file}")

    if os.path.exists(stepping_file):
        try:
            with open(stepping_file, 'r', errors='ignore') as f:
                content = f.read().strip()
                log.info(f"Found stepping value: {content}")
                return content
        except Exception as e:
            log.warning(f"Error reading stepping file: {e}")
            return None
    else:
        log.warning(f"Stepping file not found: {stepping_file}")
        return None


def release_email(TP_release_note):
    """ This will generate the release email for the TP release note.
    Args:
        TP_release_note: Path to the release note file
    """

    # Initialize variables
    special_notes = ''
    issue = ''
    sites = ''
    Integrators = ''
    TP_Owner = ''
    Test_Operation = ''
    Test_Temperature = ''
    Load_Time = ''
    Init_Time = ''
    TTG = ''
    HRI_MRV = ''

    # Get UserInputs
    if (os.path.exists(TP_release_note)):
        with open(TP_release_note, errors='ignore') as f_note:
            f_note_lines = f_note.readlines()
            for line in f_note_lines:
                if 'TestProgram_Full_Path' in line:
                    TestProgram = line.split(':', 1)[1].strip()
                    log.info(f"TestProgram: {TestProgram}")
                elif 'Special_Notes' in line:
                    special_notes = line.split(':', 1)[1].strip()
                    log.info(f"Special_Notes: {special_notes}")
                elif 'Issue' in line:
                    issue = line.split(':', 1)[1].strip()
                elif 'sites' in line:
                    sites = line.split(':', 1)[1].strip()
                    log.info(f"sites: {sites}")
                elif 'Integrators' in line:
                    Integrators = line.split(':', 1)[1].strip()
                    log.info(f"Integrators: {Integrators}")
                elif 'TP_Owner' in line:
                    TP_Owner = line.split(':', 1)[1].strip()
                    log.info(f"TP_Owner: {TP_Owner}")
                elif 'Test_Operation' in line:
                    Test_Operation = line.split(':', 1)[1].strip()
                    log.info(f"Test_Operation: {Test_Operation}")
                elif 'Test_Temperature' in line:
                    Test_Temperature = line.split(':', 1)[1].strip()
                    log.info(f"Test_Temperature: {Test_Temperature}")
                elif 'Load_Time' in line:
                    Load_Time = line.split(':', 1)[1].strip()
                    log.info(f"Load_Time: {Load_Time}")
                elif 'Init_Time' in line:
                    Init_Time = line.split(':', 1)[1].strip()
                    log.info(f"Init_Time: {Init_Time}")
                elif 'TTG' in line:
                    TTG = line.split(':', 1)[1].strip()
                    log.info(f"TTG: {TTG}")
                elif 'HRI/MRV' in line:
                    HRI_MRV = line.split(':', 1)[1].strip()
                    log.info(f"HRI/MRV: {HRI_MRV}")
    else:
        log.info(f"{TP_release_note} does NOT exist!")
        exit(1)

    # If Auto Release, get the path from the github workflow
    if 'AUTO_RELEASE_NOTE' in os.environ:
        destination_folder = os.environ.get('DEST', 'None')
        target_bom = os.environ.get('TARGETBOM', 'None')
        TestProgram = f'{destination_folder}/POR_TP/{target_bom}'
        log.info(f'Found Auto Release workflow. Update the TestProgram path to: {TestProgram}')

    if '\\' in TestProgram:
        get_drive = TestProgram.split('\\')[1]
    else:
        get_drive = TestProgram.split('/')[1]

    if get_drive == 'hdmxprogs':
        classification = 'Production'
    elif get_drive == 'tpvalidation':
        classification = 'Validation'
    else:
        classification = 'Engineering'

    tp_path = Env.xpath(os.path.dirname(os.path.dirname(TestProgram)))
    tp_name = os.path.basename(tp_path)
    bomgroup = os.path.basename(TestProgram)

    # Auto-read stepping from DieletStepping.txt
    filter_stepping = get_stepping_from_file(tp_path, bomgroup)
    if filter_stepping:
        log.info(f"Auto-detected stepping from file: {filter_stepping}")
    else:
        log.info("No stepping filter applied - showing all BOM definitions")

    # Get and copy CleanTP report
    if os.path.exists('I:/tpvalidation/engtools/tptools/mtl/infra/dashboard/NVL/CleanTP'):
        get_cleantp_report(TestProgram, tp_name)

    # Get BOM and Stepping
    if (os.path.exists(tp_path)):
        log.info(f"tp_path: {tp_path}")
        BinMatrix_path = glob.glob(f'{tp_path}/Shared/BaseInputs/Common/Common_{bomgroup}/BinMatrix.flm.usrv')[0]
        log.info(f"BinMatrix_path: {BinMatrix_path}")
        with open(BinMatrix_path, errors='ignore') as f_bm:
            f_bm_lines = f_bm.readlines()
            for line in f_bm_lines:
                if bomgroup.upper() in line and 'TorchRulesVars.bom' in line:
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

                        # Filter by stepping if specified
                        if filter_stepping is None or Stepping_temp == filter_stepping:
                            Stepping.append(Stepping_temp)
                            BOM.append(BOM_temp)
                    break

    else:
        log.info(f"{tp_path} does NOT exist!")
        exit(1)

    BOM = list(dict.fromkeys(BOM))
    Stepping = list(dict.fromkeys(Stepping))
    BOM.sort()
    Stepping.sort()
    separator = ", "
    BOM = separator.join(BOM)
    Stepping = separator.join(Stepping)

    if filter_stepping:
        log.info(f'BOM (filtered by stepping {filter_stepping}): {BOM}')
        log.info(f'Stepping (filtered): {Stepping}')
    else:
        log.info(f'BOM: {BOM}')
        log.info(f'Stepping: {Stepping}')

    short_name = tp_name[10:15]
    TP_Prod = tp_name[0:3]
    dielet_bit = tp_name[15:17]
    tp_type = get_tp_type(dielet_bit)

    today = date.today()
    log.info(f'This is {tp_type} TP Release.')

    # Getting ENV File variables
    ENV_path = glob.glob(f"{TestProgram}/EnvironmentFile.env")[0]
    with open(ENV_path, errors='ignore') as f_env:
        f_env_lines = f_env.readlines()

        FSM_FILE_PATH = 'N/A'
        PUP_PATTERNS_DIR = 'N/A'
        fuse_root_dirs = []
        prime_base = []
        count = -1
        for line in f_env_lines:
            count = count + 1
            if line.strip().startswith('#'):
                continue
            if 'FUSE_ROOT_DIR' in line and line.strip().startswith('FUSE'):
                FUSE_ROOT_DIR = line.split('\"')[1]
                log.info(f"Found Fuse Root DIR: {FUSE_ROOT_DIR}")
                fuse_root_dirs.append(FUSE_ROOT_DIR)

            elif 'TP_TOS = ' in line:
                TOS_Profile = line.split('\"')[1]
                log.info(f"TOS_Profile: {TOS_Profile}")
            elif 'PRIME_DLL_PATH = ' in line:
                PRIME_DLL_PATH = []
                for i in range(10):
                    if f_env_lines[count + i].strip().endswith('+'):
                        temp = f_env_lines[count + i].split('\"')[1]
                        PRIME_DLL_PATH.append(temp.replace(';', ''))
                    elif f_env_lines[count + i].strip().endswith('\";'):
                        temp = f_env_lines[count + i].split('\"')[1]
                        PRIME_DLL_PATH.append(temp.replace(';', ''))
                        break
                log.info(f"PRIME_DLL_PATH: {PRIME_DLL_PATH}")
            elif 'FSM_FILE_PATH = ' in line and not line.startswith('#'):
                FSM_FILE_PATH = line.split('\"')[1]
                log.info(f"FSM_FILE_PATH: {FSM_FILE_PATH}")
            elif 'PUP_PATTERNS_DIR = ' in line and not line.startswith('#'):
                PUP_PATTERNS_DIR = line.split('\"')[1]
                log.info(f"PUP_PATTERNS_DIR: {PUP_PATTERNS_DIR}")

    # Expand the variable in the PRIME_DLL_PATH, ex: $BINNING_USERCODE_PATH
    if PRIME_DLL_PATH:
        for i, item in enumerate(PRIME_DLL_PATH):
            if '$' in item:
                item_to_replace = item.split('$')[1]
                for line in f_env_lines:
                    if item_to_replace in line and not line.startswith('#') and '$' not in line:
                        new_item = line.split('=')[1].strip().replace('"', '').replace(';', '')
                        log.info(f"Replacing {item_to_replace} with {new_item}")
                        PRIME_DLL_PATH[i] = item.replace(f'${item_to_replace}', new_item)
                        break
    log.info(f"PRIME_DLL_PATH: {PRIME_DLL_PATH}")

    # Getting repo sha id
    repo_sha = f"{TestProgram}/Reports/RepoRev.json"
    with open(repo_sha, "r") as json_file:
        data = json.load(json_file)

    # Return a dict for repo_sha_id = {nvl-cpu: SHA,...}
    repo_sha_id = get_repo_sha_id(data)

    # Adding Tag to the test program:
    for key, value in repo_sha_id.items():
        if value != 'N/A':
            cur_tag = setting_Tags(short_name, key, value, dielet_bit)

    if PUP_PATTERNS_DIR != 'N/A':
        if 'HDMT_TPL_DIR' in PUP_PATTERNS_DIR:
            temp_pup = '\\'.join(PUP_PATTERNS_DIR.split('\\')[1:])
            PUP_PATTERNS_DIR = rf'{tp_path}\{temp_pup}'
            log.info(PUP_PATTERNS_DIR)
        PUP_RELEASE = get_pup_release(PUP_PATTERNS_DIR)
    else:
        PUP_RELEASE = 'N/A'

    # Getting skipped modules
    skipped_modules_list = []
    skipped_modules_path = f"{TestProgram}/SkipModules"
    if os.path.exists(skipped_modules_path):
        for module in glob.glob(f'{skipped_modules_path}/*.txt'):
            if 'Readme' in module:
                continue
            module = module.split('\\')[-1].split('.')[0]
            log.info(module)
            skipped_modules_list.append(module)

    skipped_modules = 'None'
    if skipped_modules_list:
        skipped_modules = ', '.join(skipped_modules_list)

    # Getting supersedes info
    supersedes = supersedes_list(tp_path)

    # Get Handler recipe
    # Handler_Rev = get_handler_re_path(Handler_Re_path)
    Handler_Rev = 'N/A'

    # Test Program Summary Information
    Products = f"{TP_Prod} {bomgroup} {Stepping}"

    # Test Program Files for Loadings
    TP_Base_Dir = tp_path.replace('/', '\\')
    TPL = "BaseTestPlan.tpl"
    STPL = f"POR_TP\\{bomgroup}\\SubTestPlan.stpl"
    Plist_path = glob.glob(f"{TestProgram}/PLIST_ALL_CLASS_*.plist.xml")[0]
    Plist = f"POR_TP\\{bomgroup}\\{os.path.basename(Plist_path)}"
    SOC = f"Shared\\BaseInputs\\Common\\Common_{bomgroup}\\HVM.soc"

    ENV = f"POR_TP\\{bomgroup}\\EnvironmentFile.env"

    # Set Release Note header
    if classification == 'Production':
        header1 = f"{tp_name} {tp_type} TP Release Memo"
        header2 = f"{bomgroup} {Stepping} {short_name} Test Program"
        header3 = f"Release to {sites}"
        header4 = f"Release Date {today}"
        email_subject = f"{tp_name} {tp_type} TP Release Memo - {bomgroup} {Stepping} {short_name}"
        email_body = f"Here is the Test Program Release Notes for test program {tp_name} {tp_type}."
    else:
        header1 = f"{tp_name} {tp_type} Daily Build Report"
        header2 = f"{bomgroup} {Stepping} {short_name} Test Program"
        header3 = f"Built to {sites}"
        header4 = f"Built Date {today}"
        email_subject = f"{tp_name} {tp_type} Daily Build Report - {bomgroup} {Stepping} {short_name}"
        email_body = f"Here is the Daily Build Report for test program {tp_name} {tp_type}."

    table1 = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"

    table1 += f"""<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'><pre>{header1}
{header2}
{header3}
{header4}</pre></td></tr>"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Objective/Special Notes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{special_notes}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Issues</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{issue}</td>
    </tr>\n"""
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Summary Information</td></tr>\n"
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Name</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{tp_name}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Short Name [Nick Name]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{short_name} {tp_type}</td>
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
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{'<br>'.join(fuse_root_dirs)}</td>
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
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>PRIME_DLL_PATH</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{'<br>'.join(PRIME_DLL_PATH)}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Skipped Modules</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{skipped_modules}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Supersedes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{'<br>'.join(supersedes)}</td>
    </tr>\n"""
    if FSM_FILE_PATH != 'N/A':
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>FSM File Path</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{FSM_FILE_PATH}</td>
        </tr>\n"""
    if PUP_RELEASE != 'N/A':
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>PUP_RELEASE</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{PUP_RELEASE}</td>
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
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{classification}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>BOM Groups</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{bomgroup}</td>
    </tr>\n"""
    if HRI_MRV:
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>HRI/MRV</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{HRI_MRV}</td>
        </tr>\n"""
    if classification == 'Production':
        table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Key Test Program Metrics </td></tr>\n"
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Operations</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Test_Operation}</td>
        </tr>\n"""
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Temperature(s)</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Test_Temperature}</td>
        </tr>\n"""
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

    report_file = get_PR_report_file(short_name, dielet_bit, TestProgram)
    if os.path.exists(report_file):
        table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Change List</td></tr>\n"
        table1 += """  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>PR Number</td>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Title</td>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Submitted By</td>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>URL</td>
        </tr>\n"""
        with open(report_file) as f:
            data = json.load(f)
        for repo, pr_info in data.items():
            # Extract build information (Branch, SHA, or TAG) from the first item
            build_info = ""
            for key, value in pr_info.items():
                if key in ['Branch', 'SHA', 'TAG']:
                    build_info = f" - {value}"
                    break
            table1 += f"<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>REPO: {repo}{build_info}</td></tr>\n"
            # Process only PR items (skip Branch, SHA, TAG keys)
            for pr, pr_items in pr_info.items():
                if pr in ['Branch', 'SHA', 'TAG']:
                    continue  # Skip the build info items

                title = pr_items.get('title')
                owner = pr_items.get('Submitted by')
                url = pr_items.get('url')
                table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>{pr}</td>
                <td style='padding-right:15px; font-size:12px;'>{title}</td>
                <td style='padding-right:15px; font-size:12px;'>{owner}</td>
                <td style='padding-right:15px; font-size:12px;'>{url}</td>
                </tr>\n"""
    table1 += "</table>\n"

    report_file = get_report_file(bomgroup, short_name)

    f = open(report_file, "a")

    f.write("<html style=\"font-family: Calibri; font-size: 12px;\">\n")
    f.write("<head>\n")
    f.write(f"<title>{header1}</title>\n")
    f.write("</head>")
    f.write("<body>\n")
    f.write(f"<h1>{table1}</h1>\n \
           <h2 style = 'font-size: 12px;'>For more details, please contact: mpe_ddg_pde_tp_team@intel.com</h2>\n</body></html>")

    f.close()

    # Getting email list from the test program
    send_email(classification, issue, email_subject, email_body, special_notes, table1, TP_release_note)


def send_email(classification, issue, email_subject, email_body, special_notes, table1, TP_release_note):
    """
    This function will send the email.
    """
    email_to, email_cc = get_email_list(classification)
    if issue != 'None' and issue != '':
        issue_note = f"<p style=\"color: #FF0000; font-size: 18px;\">Issue: {issue}</p>"
    else:  # issue is None or empty
        issue_note = ''

    if IS_WIN:
        if 'AUTO_RELEASE_NOTE' in os.environ:
            vpo_release_email = f'{os.path.dirname(TP_release_note)}/release_vpo_email.html'
            if os.path.exists(vpo_release_email):
                log.info(f'VPO release email exists: {vpo_release_email}')
                with open(vpo_release_email, 'r') as f:
                    vpo_body = f.read()
            else:
                vpo_body = ''
            # Create the Email
            log.info(f"submitter: {os.environ.get('SUBMITTER_EMAIL', 'None')}")
            submitter_email = os.environ.get("SUBMITTER_EMAIL", 'None')
            if submitter_email == 'None':
                submitter_email = os.environ.get("GITHUB_ACTOR", "sys_tprobot")
            msg = {'to_list': email_to,
                   'cc_list': email_cc,
                   'fromemail': submitter_email,
                   'html': True,
                   'subject': email_subject,
                   'message': f"""
            <html style="font-family: Calibri; font-size: 12px;">
            <body>
            <p>Hello Team,</p>
            <p>{vpo_body}</p>
            <p>{email_body}</p>
            <p><span style="color: #000000; background-color: #FFFF00; font-size: 18px;">Notes: {special_notes}</span></p>
            {issue_note}
            {table1}
            <p>Thank you</p></body></html>"""}
            log.info(msg)
            DataHost().central('sendmail', msg, check=True)
            log.info("Release email sent successfully.")
            if os.path.exists(vpo_release_email):
                log.info('Remove vpo release email file.')
                os.remove(vpo_release_email)

        else:
            # Create the Email
            pythoncom.CoInitialize()
            try:
                outlook = win32com.client.GetActiveObject("Outlook.Application")
            except Exception:
                outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)
            mail.To = email_to
            mail.CC = email_cc
            mail.Subject = f"{email_subject}"
            mail.HTMLBody = f"""
            <html style="font-family: Calibri; font-size: 12px;">
            <body>
            <p>Hello Team,</p>
            <p>{email_body}</p>
            <p><span style="color: #000000; background-color: #FFFF00; font-size: 18px;">Notes: {special_notes}</span></p>
            {issue_note}
            {table1}
            <p>Thank you</p></body></html>"""

            mail.Display(False)


def main():     # pragma: no cover
    """
    Usage: nvl_testprogram_release.py -path path-to-testprogram_release_notes.txt
    """

    parser = argparse.ArgumentParser(description='Test Program release script')
    parser.add_argument('-path', '--path', help='Path to your release/daily note', required=True)

    args = parser.parse_args()

    # Access the values using args.path
    path = args.path
    log.info(f"Path: {path}")

    log.info('Running test program release...')
    release_email(path)


if __name__ == "__main__":   # pragma: no cover
    main()
