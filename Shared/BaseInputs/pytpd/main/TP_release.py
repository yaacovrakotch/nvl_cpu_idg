from setenv import ROOT_ENV      # must be first in the imports
import sys
import os
from subprocess import call, run
from gadget.shell import SystemCall
from gadget.pylog import log
from datetime import date
import shutil
import glob
from gadget.shell import IS_UNIX, IS_WIN

try:
    import win32com.client
except ImportError:
    pass


def input_release_note():
    TP_release_note = "TP_release_note.txt"
    return TP_release_note


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


def get_TP_path(TestProgram):

    if 'ARL' in TestProgram:
        TP_path = f"I:/hdmxprogs/arl/{TestProgram}"
        prime_EVG_indicator(TP_path)
    elif 'MTL' in TestProgram:
        TP_path = f"I:/hdmxprogs/mtl/{TestProgram}"
    else:
        print(f'Cannot find the Test Program Path associated with the {TestProgram}')
        exit(1)

    return TP_path


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


def get_report_file(BOM_Groups, TestProgram_short):
    if 'P28' in BOM_Groups:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP281\\DAILY\\TPReleaseNotes\\{TestProgram_short}.html"

    elif 'P68' in BOM_Groups:
        report_file = f"I:\\engineering\\dev\\sctp\\users\\SmartTP\\MTLP682\\DAILY\\TPReleaseNotes\\{TestProgram_short}.html"

    elif 'H68' in BOM_Groups:
        report_file = f'I:\\engineering\\dev\\team_classtp\\dashboard\\TP_Releases\\{TestProgram_short}.html'

    else:
        print(f'The {BOM_Groups} is NOT associated with {TestProgram_short}. Please check the test program.')
        exit(1)

    if os.path.exists(report_file):
        os.remove(report_file)

    return report_file


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


def release_email():

    # Get UserInputs
    TP_release_note = input_release_note()
    if (os.path.exists(TP_release_note)):
        with open(TP_release_note, errors='ignore') as f_note:
            f_note_lines = f_note.readlines()
            for line in f_note_lines:
                if 'TestProgram' in line:
                    TestProgram = line.split(':', 1)[1].strip()
                    print(f"TestProgram: {TestProgram}")
                elif 'BOMGROUP' in line:
                    BOMGROUP = line.split(':', 1)[1].strip()
                    print(f"BOMGROUP: {BOMGROUP}")
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

    TP_path = get_TP_path(TestProgram)

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
                    if BOMGROUP in line and 'TorchRulesVars.bom' in line:
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

    TestProgram_short = TestProgram[10:15]
    TP_Prod = TestProgram[0:3]
    today = date.today()

    # Set Release Note header
    header1 = f"{TestProgram} Release Memo"
    header2 = f"Class-{TP_Prod} {BOMGROUP} {Stepping} {TestProgram_short} Test Program"
    header3 = f"Release to {sites}"
    header4 = f"Release Date {today}"

    # Get MTL folder
    if BOMGROUP == 'P68G2':
        BOM_folder = 'Class_MTL_P68'
    elif BOMGROUP == 'P28G2' or BOMGROUP == 'P28G1':
        BOM_folder = 'Class_MTL_P28'
    elif BOMGROUP == 'H68G2' or BOMGROUP == 'H68G1':
        BOM_folder = 'Class_ARL_H68'
    else:
        print(f'Provided {BOMGROUP} is NOT available. Please check the Test Program.')

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
    Products = f"{TP_Prod} {BOMGROUP} {Stepping}"

    # Test Program Files for Loadings
    TP_Base_Dir = TP_path.replace('/', '\\')
    TPL = "BaseTestPlan.tpl"
    STPL = f"POR_TP\\{BOM_folder}\\SubTestPlan_CLASS_{BOMGROUP}_g.stpl"
    Plist = f"POR_TP\\{BOM_folder}\\PLIST_ALL_CLASS_{BOMGROUP}.plist.xml"
    if 'ARL' in TestProgram:
        SOC = f"Shared\\BaseInputs\\CLASS_{BOMGROUP}_HDMT_1.soc"
    elif 'MTL' in TestProgram:
        SOC = f"Shared\\BaseInputs\\{TP_Prod}_{BOMGROUP}_HDMT_1.soc"
    else:
        print("Could NOT find the SOC file in the test program.")
        exit(1)
    ENV = f"POR_TP\\{BOM_folder}\\EnvironmentFile.env"
    BOM_Groups = f"CLASS_{BOMGROUP}"
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

    # Table
    table = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"

    table += f"""<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:12px;'><pre>{header1}
{header2}
{header3}
{header4}</pre></td></tr>"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Objective/Special Notes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Special_Notes}</td>
    </tr>\n"""
    table += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:12px;'>Test Program Summary Information</td></tr>\n"
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Name</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TestProgram}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Short Name [Nick Name]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TestProgram_short}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Products/Subfamily</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Products}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Integrator</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Integrators}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Product Owner</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TP_Owner}</td>
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
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Handler Rev</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Handler_Rev}</td>
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
    if 'ARL' not in TestProgram:
        table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>User Code</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{User_Code}</td>
        </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Skipped Modules</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{skipped_modules}</td>
    </tr>\n"""
    if 'ARL' not in TestProgram:
        table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>FSM File Path</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{FSM_FILE_PATH}</td>
        </tr>\n"""
        table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td colspan ='2' style='padding-right:15px; font-size:12px;'>PUP Release</td>
            <td colspan ='2' style='padding-right:5px; font-size:12px;'>{PUP_RELEASE}</td>
        </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Operations</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Test_Operation}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Temperature(s)</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Test_Temperature}</td>
    </tr>\n"""
    table += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:12px;'>Test Program Files for Loadings</td></tr>\n"
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>TP Base Dir</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TP_Base_Dir}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Plan</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TPL}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Sub-Test Plan</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{STPL}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Plist Reference</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Plist}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Socket File</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{SOC}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Environment File</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{ENV}</td>
    </tr>\n"""
    table += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:12px;'>Key Test Program Metrics </td></tr>\n"
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Load Time [mins]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Load_Time}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Init Time [mins]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Init_Time}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Time Good [min]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TTG}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>BOM Definition</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{BOM}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Stepping</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Stepping}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Classification</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Classification}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>BOM Groups</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{BOM_Groups}</td>
    </tr>\n"""
    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Valid DLCP Characters</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{DLCP}</td>
    </tr>\n"""
    table += "</table>\n"

    report_file = get_report_file(BOM_Groups, TestProgram_short)

    f = open(report_file, "a")

    f.write("<html style=\"font-family: Calibri; font-size: 12px;\">\n")
    f.write("<head>\n")
    f.write(f"<title>{header1}</title>\n")
    f.write("</head>")
    f.write("<body>\n")
    f.write(f"<h1>{table}</h1>\n \
           <h2 style = 'font-size: 12px;'>For more details, please contact: mpe_ddg_pde_10n_tp_team@intel.com</h2>\n</body></html>")

    f.close()

    table1 = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"

    table1 += f"""<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4'><pre>{header1}
{header2}
{header3}
{header4}</pre></td></tr>"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Objective/Special Notes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{Special_Notes}</td>
    </tr>\n"""
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4'>Test Program Summary Information</td></tr>\n"
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Name</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TestProgram}</td>
    </tr>\n"""
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Short Name [Nick Name]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>{TestProgram_short}</td>
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
FUSE_ROOT_DIR_SXM = "{FUSE_ROOT_DIR_SXM}"</pre>
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
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4'>Test Program Files for Loadings</td></tr>\n"
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
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4'>Key Test Program Metrics </td></tr>\n"
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
    table1 += "<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4'>Test Program Change List</td></tr>\n"
    table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right:15px; font-weight: bold'>Module Name</td>
        <td style='padding-right:15px; font-weight: bold'>Owner</td>
        <td style='padding-right:15px; font-weight: bold'>Timestamp</td>
        <td style='padding-right:15px; font-weight: bold'>Comment</td>
    </tr>\n"""
    for key in data_dict:
        table1 += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td style='padding-right:15px; font-size:12px;'>{key}</td>
            <td style='padding-right:15px; font-size:12px;'>{data_dict[key][0]}</td>
            <td style='padding-right:15px; font-size:12px;'>{data_dict[key][1]}</td>
            <td style='padding-right:15px; font-size:12px;'>{data_dict[key][2]}</td>
        </tr>\n"""

    table1 += "</table>\n"

    if IS_WIN:
        # Create the Email
        outlook = win32com.client.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)
        mail.To = "Matheson, Don L <don.l.matheson@intel.com>; McGlothin, Darron <darron.mcglothin@intel.com>; Boddy, Aaron J <aaron.j.boddy@intel.com>; MPE_DDG_Lab_Ops&Maint <mpe_ddg_lab_ops.maint@intel.com>; Adyani, Rod <rod.adyani@intel.com>; Papierski, Dennis J <dennis.j.papierski@intel.com>; Rodriguez, Jorge R <jorge.r.rodriguez@intel.com>; 'mpe-testprogram-cascade-release@eclists.intel.com'; MPE CRVLE Client Planning <mpe.crvle.client.planning@intel.com>; MPE CRVLE Planning Techs <mpe.crvle.planning.techs@intel.com>"
        mail.CC = "MPE_DDG_PDE_10n_TP_TEAM <mpe_ddg_pde_10n_tp_team@intel.com>; 'mpe-mtl-tpd-team@eclists.intel.com'"
        mail.Subject = f"{TP_Prod} {BOMGROUP} {Stepping} Class {TestProgram} TP Release Notes"
        mail.HTMLBody = """
        <html style="font-family: Calibri; font-size: 12px;">
        <body>
        <p>Hello Team,</p>
        <p>Here is the Test Program Release Notes for test program """ + TestProgram + """.</p>
        """ + table1 + """<p>Thank you</p></body></html>"""
        mail.Display(False)


# This py script should be run on the same folder as the TP_release_note.txt
def main():     # pragma: no cover
    release_email()


if __name__ == "__main__":      # pragma: no cover
    main()
