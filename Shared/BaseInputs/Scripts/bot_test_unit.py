import sys
import os
import shutil
import re
from subprocess import call, run
import stat
from datetime import datetime, date
import time
import glob
import json
import socket

class BotTestUnit:
    """Class to handle test unit operations."""
    def __init__(self, config_data, job_input_data, checkname, bom):
        self.config_data = config_data
        self.job_input_data = job_input_data
        self.checkname = checkname
        self.bom = bom
        self.pbic_ube_update = False
        self.if_load_already_done = False

    def Polaris(self, base_tp, temp):
        """Set up temperature on the tester"""
        if temp == "":
            print("No temperature setting found. Skip Polaris setup.")
            return
        PolarisApps = f"{base_tp}\\UserCode\\lib\\Release\\net6.0\\SetTemperature.exe"
        if os.path.exists(f"{PolarisApps}"):
            print(f"set thermal to {temp}C")
            result = run(f"{PolarisApps} --temperature {temp} --timeout 300")
            # if result.returncode == 1:
            #     print('Thermal setup failed. Please check if Polaris is turning ON. Exit...')
            #     sys.exit(1)

    def polaris_set_feedback(self, base_tp, feedback, tester_prefix=None, test_unit='BIN1'):
        """ Set Polaris feedback"""
        if test_unit != 'BIN1':
            print(f"SetFeedback NOT supported on {test_unit}. Skipping.")
            return 0   # Do nothing, but return safely

        # If caller didn't pass tester_prefix, detect automatically
        if tester_prefix is None:
            tester_prefix = socket.gethostname()[:2]

        # Only JF/FM support SetFeedback
        if tester_prefix not in ['JF', 'FM']:
            print(f"SetFeedback not supported on tester prefix '{tester_prefix}'. Skipping.")
            return 0   # Do nothing, but return safely

        PolarisApps = f"{base_tp}\\UserCode\\lib\\Release\\net6.0\\SetTemperature.exe"

        if feedback == 'pf':
            result = run(f"{PolarisApps} --operation SetFeedback --feedback_source PowerFollowing --pf_slope 0.5 --pf_offset 10 --channels 0 1")
        elif feedback == 'tcase':
            result = run(f"{PolarisApps} --operation SetFeedback --feedback_source Tcase --channels 0")
        else:
            result = run(f"{PolarisApps} --operation SetFeedback --feedback_source Tcase --channels 0")

        if result.returncode == 1:
            print('Thermal setup failed. Please check if Polaris is turning ON. Exit...')
            sys.exit(1)

    def getting_current_time(self):
        """Get current time"""

        now = datetime.now()
        current_time = now.strftime("%H-%M-%S")
        today_date = date.today().strftime("%Y-%m-%d")
        print(f"Current time: {today_date}-{current_time}")
        return today_date, current_time

    def run_load_TP(self, today_date, current_time, SSCEXEPATH, log_folder, base_tp, tpl_file, stpl_file, env_file, plist_file, soc_file):
        """Load the test program"""

        # Start load
        load_file = f"loadLog_{today_date}-{current_time}.txt"
        print("Start Load Log...")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe startConsolidatedLogging {log_folder}/{load_file} true")

        print("Start loading...")
        print(f"Load log: {log_folder}/{load_file}")
        self.call_check_result(
            f"{SSCEXEPATH}/SingleScriptCmd.exe loadTP {base_tp} {tpl_file} {env_file} {stpl_file} {plist_file} {soc_file}")

        print("Stop Load Log...")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe stopConsolidatedLogging")
        print(f"Load log: {log_folder}/{load_file}")

        result = run(f"{SSCEXEPATH}/SingleScriptCmd.exe isTPloaded", capture_output=True)
        data = result.stdout.decode('utf-8', 'ignore')
        print(data)

        if "No TP loaded" in data:
            print("No TP loaded. Exit...")
            print(f"Please see the Load log: {log_folder}/{load_file}")
            return 'FAILED'
        else:
            print("Test Program is loaded successfully.")
            return 'PASSED'

    def run_INIT(self, base_tp, current_step, today_date, current_time, log_folder, SSCEXEPATH):
        """Run INIT on the tester"""

        init_file = f"{current_step}_initLog_{today_date}-{current_time}.txt"
        print(f"Start {current_step} INIT Log...")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe startConsolidatedLogging {log_folder}/{init_file} true")

        print(f"Start {current_step} INIT...")
        init_result = run(f"{SSCEXEPATH}/SingleScriptCmd.exe Init", capture_output=True)
        init_data = init_result.stdout.decode('utf-8', 'ignore')
        print(init_data)
        print(f"Stop {current_step} INIT Log...")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe stopConsolidatedLogging")
        print(f"{current_step} INIT log: {log_folder}/{init_file}")

        if "Processing command INIT was unsuccessful" in init_data:
            print(f"{current_step} INIT failed.")
            return 'FAILED'

        else:
            print(f"{current_step} INIT is successful.")

    def run_StartLot(self, base_tp, SSCEXEPATH):
        """Run StartLot on the tester"""

        print("Start StartLot...")
        startLot_result = run(f"{SSCEXEPATH}/SingleScriptCmd.exe startLot", capture_output=True)
        startLot_data = startLot_result.stdout.decode('utf-8', 'ignore')
        print(startLot_data)
        if "Processing command START_LOT was unsuccessful" in startLot_data:
            print("StartLot failed.")
            return 'FAILED'

        else:
            print("StartLot is successful.")

    def run_TestUnit(self, base_tp, current_step, today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS):
        """Run test unit on the tester"""

        testLog_file = f"{current_step}_TestUnitLog_{today_date}-{current_time}.txt"
        print(f"Start {current_step} Testing Log...")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe startLot")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe startConsolidatedLogging {log_folder}/{testLog_file} true")

        print(f"Start {current_step} unitTest...")
        test_result = run(f"{SSCEXEPATH}/SingleScriptCmd.exe testUnit", capture_output=True)
        test_data = test_result.stdout.decode('utf-8', 'ignore')
        print(test_data)
        print(f"Stop {current_step} Testing Log...")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe endLot")
        self.call_check_result(f"{SSCEXEPATH}/SingleScriptCmd.exe stopConsolidatedLogging")
        print(f"Test Unit log: {log_folder}/{testLog_file}")
        print("Copy ituff file...")
        shutil.copyfile(f"{HDMTTOS}/1A_11", f"{log_folder}/ituff_{testLog_file}")
        print(f"Ituff file: {log_folder}/ituff_{testLog_file}")

        if "PassFailStatus = Fail" in test_data:
            print("Test Unit failed.")

        else:
            print("Test Unit is successful.")

        return testLog_file

    # Call command to check the command error	 
    def call_check_result(self, command):
        """Call command and check the result"""

        result = call(command)
        if result:
            print("Script failed. Please scroll several lines above for the exact failure.")
            sys.exit(1)

    def check_test_result(self, result, log_file, current_step, allow_passed_bins=''):
        """Check the test result after run_TestUnit"""

        if os.path.exists(log_file):
            with open(log_file, 'r') as f_result:
                line_results = f_result.readlines()
        else:
            print(f'{log_file} does NOT exist. Please check if the unit was tested.')
            sys.exit(1)
        passed_bin = [bin.strip() for bin in allow_passed_bins.split(',') if bin.strip()]

        for line in line_results:
            if re.search(r"DUT\s+11:\s+DataBin\s+=\s+1.{2}1000,\s+SoftBin\s+=\s+1.{2},", line):
                print(line)
                print(f'Successfully test unit with Bin1 at {current_step}')
                result = 'PASSED_B1'
                return result, line

            if passed_bin:
                for allowed_bin in passed_bin:
                    allowed_bin = allowed_bin.strip()
                    if len(allowed_bin) == 2:
                        if re.search(rf"DUT\s+11:\s+DataBin\s+=\s+{allowed_bin}.{{6}},\s+SoftBin\s+=\s+.{{3,4}}.*PassFailBin\s+=\s+1", line):
                            print(line)
                            print(f'Unit passed with B{allowed_bin}XXXXXX at {current_step}')
                            result = 'PASSED'
                            return result, line
                    elif len(allowed_bin) == 4:
                        if re.search(rf"DUT\s+11:\s+DataBin\s+=\s+{allowed_bin}.{{4}},\s+SoftBin\s+=\s+.{{3,4}}.*PassFailBin\s+=\s+1", line):
                            print(line)
                            print(f'Unit passed with B{allowed_bin}XXXX at {current_step}')
                            result = 'PASSED'
                            return result, line
                    else:
                        print(f'Allowed bin {allowed_bin} is not valid. Please check the allow_passed_bins setting.')
                        return 'FAILED', f'Allowed bin {allowed_bin} is not valid. Please check the allow_passed_bins setting.'

            if re.search(r"DUT\s+11:\s+DataBin\s+=\s+.{7,8},\s+SoftBin\s+=\s+.{3,4}.*PassFailBin\s+=\s+1", line):
                print(line)
                print('Unit was tested, but FAILED')
                result = 'FAILED'
                return result, line

        print("Could NOT find the test result. Please check the unit was executed correctly")
        return 'FAILED', 'Could NOT find the test result. Please check the unit was executed correctly'

    def retest_if_failed_CLASSHOT(self, line, base_tp, today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS, allow_passed_bins='', json_data={}, workflow='None'):
        """
        Retest if it failed CLASSHOT TEST
        Retest up to 5 times if there is no 2 the same consecutive failed bin.
        
        """
        # Get FailModId
        fail_mod_id = json_data.get('FAILMODID', 'None').strip()
        failed_mod_list = {}
        if fail_mod_id.upper() == 'TRUE':
            print("FAILMODID is set to TRUE. Skip retest. Run FAILMODID check...")
            # Check config file exist
            config_file = f"{base_tp}/Shared/Modules/TPI/TPI_BASE_XXX/InputFiles/Failing_Module_Identification_Config.csv"
            if os.path.exists(config_file):
                print(f'Config file exists: {config_file}. Continue FAILMODID check.')
            else:
                print(f'Config file does NOT exist: {config_file}. Exit FAILMODID check.')
                print(line)
                return 'FAILED'
            fail_mod_id_flag = True
            count_fail = 0
            while fail_mod_id_flag:
                # restart the config input for failmodid
                print('Reload the modified config file on tester.')
                run(f"{SSCEXEPATH}/SingleScriptCmd.exe verifyTestInstance \"TPI_BASE_XXX::CTRL_X_BINRULES_K_LOTSTARTFLOW_X_X_X_X_FMI_BINRULES\"")
                # Run testUnit
                current_step = f'FAILMODID_{count_fail}'
                if count_fail == 99:
                    print('FailMod Identification has been running 99 times. Stop to avoid damaged unit.')
                    print(f'Failed Mod List: {failed_mod_list}')
                    return 'FAILED'
                testLog_file = self.run_TestUnit(base_tp, current_step, today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS)
                log_file = f"{log_folder}/{testLog_file}"
                result, line = self.check_test_result('FAILED', log_file, current_step, allow_passed_bins)
                if 'PASSED' in result:
                    print(line)
                    print(f'Failed Mod List: {failed_mod_list}')
                    return result
                else:
                    match = re.search(r'DataBin\s*=\s*(\d{8})', line)
                    if match:
                        databin = match.group(1)
                        print(f'DataBin = {databin}')
                    else:
                        print(line)
                        print('No DataBin found. Exit FAILMODID check.')
                        print(f'Failed Mod List: {failed_mod_list}')
                        return 'FAILED'
                    
                    # Read the log file and get the module name for the databin
                    with open(log_file, 'r') as f_result:
                        line_results = f_result.readlines()
                    count_line = 0
                    for line_result in line_results:
                        if f'Set Bin to {databin}' in line_result:
                            fail_line = line_results[count_line - 1]
                            mod_name = fail_line.split('::')[-2]
                            print(f'FailModId found: {mod_name} for DataBin: {databin}')
                            failed_mod_list[mod_name] = databin
                            break
                        count_line += 1
                    else:
                        print(line)
                        print(f'No module found for DataBin: {databin}. Exit FAILMODID check.')
                        print(f'Failed Mod List: {failed_mod_list}')
                        return 'FAILED'
                    
                    # Check if mod_name contains any critical modules that should cause FAILED
                    critical_modules = ['TPI_VCC', 'TPI_SHOP', 'TPI_EDM', 'TPI_DFF', 'TPI_BASE', 'DRV_RESET', 'FUS_UNITINFO', 'FUS_FUSECFG', 'FUS_FUSEREAD', 'PTH_DIODE']
                    if any(critical_mod in mod_name for critical_mod in critical_modules):
                        print(f'Critical module found: {mod_name}. Returning FAILED.')
                        print(f'Failed Mod List: {failed_mod_list}')
                        return 'FAILED'

                    # Update the config file to set the module to bypass.
                    with open(config_file, 'r') as f:
                        config_lines = f.readlines()
                    count = 0
                    for config_line in config_lines:
                        if mod_name in config_line:
                            # Split by comma, modify the [-2] item, then join back with commas
                            config_parts = config_line.strip().split(',')
                            config_parts[-2] = '1'
                            config_line = ','.join(config_parts) + '\n'
                            config_lines[count] = config_line
                            print(f'Modify the config line: {config_line}')
                            break
                        count += 1
                    else:
                        print(f'Module {mod_name} is NOT found in the config file. Exit FAILMODID check.')
                        print(f'Failed Mod List: {failed_mod_list}')
                        return 'FAILED'
                    # Write back to the config file
                    with open(config_file, 'w') as f:
                        f.writelines(config_lines)
                count_fail += 1
        else:
            if 'HardBin' in line:
                hardBin = line.split(",")[-3].split("=")[-1].strip()
                print(f'HardBin = {hardBin}')
                for i in range(4):
                    print(f"Retest {i + 1} with {hardBin}")
                    current_step = f'CLASSHOT_{i + 1}'
                    testLog_file = self.run_TestUnit(base_tp, current_step, today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS)
                    log_file = f"{log_folder}/{testLog_file}"
                    result, line = self.check_test_result('FAILED', log_file, current_step, allow_passed_bins)
                    if 'PASSED' in result:
                        return result

                    if 'HardBin' in line:
                        hardBin_new = line.split(",")[-3].split("=")[-1].strip()
                        print(f'HardBin = {hardBin_new}')
                        if hardBin == hardBin_new:
                            print("Retest failed the same hardbin.")
                            print(line)
                            if workflow == 'TPBot_schedule':
                                self.workflow_func(base_tp, f'FAILED_RETEST-HardBin={hardBin_new}', workflow)
                            return 'FAILED'
                        else:
                            hardBin = hardBin_new
                    else:
                        print(line)
                        print('Unit was tested, but FAILED. No hardBin found.')
                        return 'FAILED'

                print(line)
                print('Unit was tested, but FAILED retest')
                return 'FAILED'
            else:
                print(line)
                print('Unit was tested, but FAILED. No hardBin found.')
                return 'FAILED'

    def workflow_func(self, base_tp, status, workflow, current_socket='6248_CLASSHOT_AF'):
        """workflow function to create workflow_failed.json file when failed"""
        print(f"{workflow} function called with status: {status}")
        workflow_data = {
            'status': status,
            'repo': self.job_input_data.get('GITHUB_REPOSITORY', 'None'),
            'workflow': workflow,
            'current_socket': current_socket
        }

        with open(f'{base_tp}/workflow_failed.json', 'w') as f:
            json.dump(workflow_data, f, indent=4)

    def return_ube_file(self):
        """Return the ube file path for the product"""
        product = self.config_data.get('name', 'None').strip()
        ube_file = glob.glob(f'I:/tpvalidation/engtools/tptools/mtl/infra/torch/bot_ube/{product}/*.ube')
        # if length ube_file = 1
        if len(ube_file) == 1:
            ube = ube_file[0]
            return ube
        else:
            print("There is more than 1 ube file. Or there is no ube file."
                f"Please check the ube file in I:/tpvalidation/engtools/tptools/mtl/infra/torch/bot_ube/{product}")
            sys.exit(1)

    def return_vsid(self, ube):
        tester_name = socket.gethostname()
        print(f"Tester name: {tester_name}")
        tester_path = f'I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/testers/{tester_name}'
        vsid_file = glob.glob(f"{tester_path}/*.vsid")
        if len(vsid_file) == 1:
            vsid = os.path.basename(vsid_file[0]).split('.')[0]
            if vsid != 'NA':
                print(f"VSID: {vsid}")
                with open (ube, 'r', encoding='utf-8') as f:
                    ube_data = f.read()
                if vsid in ube_data:
                    print(f"VSID {vsid} found in UBE file: {ube}.")
                    return vsid
                else:
                    print(f"VSID {vsid} NOT found in UBE file: {ube}.")
                    sys.exit(1)
            else:
                print("VSID is NA. Not performing testing. Exit(1).")
                sys.exit(1)
        else:
            print("There is more than 1 vsid file. Or there is no vsid file."
                f"Please check the vsid file in I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/testers/{tester_name}")
            sys.exit(1)

    def set_socket_uservar(self, add_locn, add_step, add_engid, SSCEXEPATH):
        """ Set socket uservar for SC_LOCN, SC_CURRENT_PROCESS_STEP, SC_CURRENT_PROCESS_TYPE, SC_ENGID """
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_LOCN\" \"{add_locn}\"")
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_CURRENT_PROCESS_STEP\" \"{add_step}\"")
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_CURRENT_PROCESS_TYPE\" \"{add_step}\"")
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_ENGID\" \"{add_engid}\"")

    def TPload(self, base_tp, STPL, SOC, PLIST, ENV, current_socket='6248_CLASSHOT_AF'):
        """Start testing"""

        HDMTTOS = os.getenv('HDMTTOS')
        SSCEXEPATH = f"{HDMTTOS}/Runtime/Release"
        # Delete the old ituff file
        if os.path.exists(f"{HDMTTOS}/1A_11"):
            try:
                os.remove(f"{HDMTTOS}/1A_11")
            except Exception as exc:
                try:
                    with open(f"{HDMTTOS}/1A_11", "w", encoding="utf-8") as f:
                        f.write("")
                except Exception as write_exc:
                    print(f"Failed to clear {HDMTTOS}/1A_11 after remove error: {write_exc}")
                print(f"Remove failed for {HDMTTOS}/1A_11, cleared file instead: {exc}")

        # Getting time
        now = datetime.now()
        current_time = now.strftime("%H-%M-%S")
        today_date = date.today().strftime("%Y-%m-%d")
        print(f"Current time: {today_date}-{current_time}")

        log_folder = f"I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/{today_date}"

        if not self.if_load_already_done:
            tpl_file = 'BaseTestPlan.tpl'
            print(f'BASE_TP: {base_tp}')
            print(f'TPL file: {tpl_file}')
            print(f'STPL file: {STPL}')
            print(f'SOC file: {SOC}')
            print(f'ENV file: {ENV}')
            print(f'PLIST file: {PLIST}')

            # Check if file exist
            if not (os.path.exists(f"{base_tp}")):
                print(f"{base_tp} does NOT exist")
                sys.exit(1)
            if not (os.path.exists(f"{base_tp}/{tpl_file}")):
                print(f"{base_tp}/{tpl_file} does NOT exist")
                sys.exit(1)
            if not (os.path.exists(f"{base_tp}/{STPL}")):
                print(f"{base_tp}/{STPL} does NOT exist")
                sys.exit(1)
            if not (os.path.exists(f"{base_tp}/{SOC}")):
                print(f"{base_tp}/{SOC} does NOT exist")
                sys.exit(1)
            if not (os.path.exists(f"{base_tp}/{ENV}")):
                print(f"{base_tp}/{ENV} does NOT exist")
                sys.exit(1)
            if not (os.path.exists(f"{base_tp}/{PLIST}")):
                print(f"{base_tp}/{PLIST} does NOT exist")
                sys.exit(1)

            print("Restart the tester...")
            self.call_check_result(f"{SSCEXEPATH}/HdmtSupervisorService/hdmttosctrl restarttos")

            if os.path.exists(log_folder):
                print(log_folder)
            else:
                os.makedirs(log_folder)
                print(log_folder)

            # Start load
            result = self.run_load_TP(today_date, current_time, SSCEXEPATH, log_folder, base_tp, tpl_file, STPL, ENV, PLIST, SOC)

            if result == 'FAILED':
                sys.exit(1)
            # Set if_load_already_done = True after done loading TP.
            self.if_load_already_done = True

        # Check if TeamBot, if so, exit
        if TeamBot.check_is_teambot():
            print("It is TeamBot run. Exit 0.")
            sys.exit(0)

        # Get the die_indicator
        die_indicator = self.job_input_data.get('DIEINDICATOR', 'None').strip()
        if die_indicator in ['CPU', 'HUB', 'GCD', 'PCD']:
            print(f"Dielet found from job input data: {die_indicator}")
            dielet_data = self.config_data.get(die_indicator, {})
        else:
            print(f"No dielet found from job input data. using OTHER/default option")
            dielet_data = self.config_data.get('OTHER', {})

        temperature = dielet_data.get('temperature', 'None').strip()
        test_unit = dielet_data.get('test_unit', 'None').strip()
        allow_passed_bins = dielet_data.get('allow_passed_bins', 'None').strip()

        if test_unit == 'LOAD':
            print("Test unit is LOAD only. Exit 0 after loading TP.")
            return "PASSED"

        # Setup SC_FACILITYID and SC_SITEID uservars
        tester_name = socket.gethostname()
        # Get the first 2 letters of tester_name
        tester_prefix = tester_name[:2]
        if tester_prefix not in ['JF', 'PG', 'FM', 'BA', 'HA']:
            print(f"Tester prefix {tester_prefix} is not in the expected list JF, PG, FM, BA, HA.")
            if tester_prefix == 'SR':
                print("Tester prefix is SR, set tester_prefix to BA for uservars setting.")
                tester_prefix = 'BA'
            elif tester_prefix == 'HD':
                print("Tester prefix is HD, set tester_prefix to PG for uservars setting.")
                tester_prefix = 'PG'
            else:
                tester_prefix = 'JF'
        facility_id = f'GDL{tester_prefix}'
        site_id = f'{tester_prefix}lab'
        print(f"Setting uservars SC_FACILITYID: {facility_id}, SC_SITEID: {site_id}")
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_FACILITYID\" \"{facility_id}\"")
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_SITEID\" \"{site_id}\"")
        email = self.job_input_data.get('EMAIL', '')
        if email != '':
            print(f'User email: {email}')
            run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"_UserVars\" \"OWNREMAIL\" \"{email}\"")
        else:
            print('No user email is provided. Skip setting OWNREMAIL uservars')

        # Check before INIT setup
        before_init_batfiles = glob.glob(f'{base_tp}/Shared/POR_TP/{self.bom}/Scripts/before_init/*.bat')
        if before_init_batfiles:
            for bot_batfile in before_init_batfiles:
                print(f"Running before init bot bat file: {bot_batfile}")
                run(bot_batfile)
        else:
            print("No before init bot bat file found. Continue...")
        
        if self.checkname == 'initCheck':
            print("initCheck detected")
            run(f"{SSCEXEPATH}/SingleScriptCmd.exe setInstanceParam \"TPI_XIU_XXX::CTRL_X_TDRCAL_K_INIT_X_X_X_X_TDRCLIBRATION\" \"LoadDataFromFile\" \"FALSE\"")
            run(f"{SSCEXEPATH}/SingleScriptCmd.exe setInstanceParam \"TPI_XIU_XXX::CTRL_X_XIUPOWERSUPPLY_K_INIT_X_X_X_X_XIUCONTINUITY\" \"BypassPort\" -1")

        # Set ube file path
        print("Setting uservar ube...")
        ube = self.return_ube_file()
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_ULT_DOWNLOAD_PATH\" \"{ube}\"")

        # Set user bat file.
        batfile = self.job_input_data.get('BATFILE', 'None')
        if batfile != "None":
            print(f"Running user bat file: {batfile}")
            if os.path.exists(batfile):
                run(batfile)
            else:
                print(f'{batfile} does NOT exist. Skip running user bat file.')
        workflow = self.job_input_data.get('GITHUB_WORKFLOW', 'None')
        print(f'Workflow: {workflow}')

        # Set socket uservar
        add_locn = current_socket.split('_')[0]
        add_step = current_socket.split('_')[1]
        add_engid = current_socket.split('_')[2]
        self.set_socket_uservar(add_locn, add_step, add_engid, SSCEXEPATH)

        # Set temperature
        if test_unit != 'BIN1':
            # this set the default temp to 25 if not testing unit.
            temperature = "25"
        if temperature != "":
            print("Setting temperature uservar...")
            run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_TEMPERATURE\" \"{temperature}\"")
        else:
            print("Skip setting temperature uservar. Set SC_BENCHTOP to -1")
            run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_BENCHTOP\" -1")
        
        self.polaris_set_feedback(base_tp, 'pf', test_unit=test_unit)
        # Start INIT
        INIT_result = 'FAILED'
        INIT_result = self.run_INIT(base_tp, f'{add_locn}_{add_step}_{add_engid}', today_date, current_time, log_folder, SSCEXEPATH)
        if INIT_result == 'FAILED':
            if workflow == 'TPBOT_schedule' or workflow == 'SCHEDULER_INIT':
                print(f"{workflow} workflow detected. Exit 1 after INIT failure.")
                self.workflow_func(base_tp, 'FAILED_INIT', workflow, current_socket)
            sys.exit(1)
        if workflow == 'SCHEDULER_INIT':
            print("SCHEDULER_INIT workflow detected. INIT PASSED. Return PASSED.")
            return "PASSED"

        if self.checkname == 'initCheck':
            print("initCheck detected. Exit 0 after INIT.")
            return "PASSED"

        fail_mod_id = self.job_input_data.get('FAILMODID', 'None').strip()

        if test_unit == 'INIT' and fail_mod_id.upper() != 'TRUE':
            print("Test unit is INIT only. Exit 0 after INIT.")
            return "PASSED"

        # Check after INIT setup
        after_init_batfiles = glob.glob(f'{base_tp}/Shared/POR_TP/{self.bom}/Scripts/after_init/*.bat')
        if after_init_batfiles:
            for bot_batfile in after_init_batfiles:
                print(f"Running after init bot bat file: {bot_batfile}")
                run(bot_batfile)
        else:
            print("No after init bot bat file found. Continue...")

        # Set uservar SC_VISUALID
        vsid = self.return_vsid(ube)
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_VISUALID\" \"{vsid}\"")

        if test_unit == 'OFFLINE':
            # Check if the tester is offline or open socket tester.
            result = run(f'{SSCEXEPATH}/SingleScriptCmd.exe getTosStatus', capture_output=True)
            output = result.stdout.decode('utf-8', 'ignore')
            lines = output.splitlines()
            offline_flag = False
            for line in lines:
                if "OfflineLSM" in line:
                    print("OfflineLSM is running. ")
                    offline_flag = True
                    break
            else:
                print('Test Program passed INIT. Currently, only INIT is tested on a real tester.')
                return 'PASSED'
            # If offline is running, continue to test with quicksim.
            if offline_flag:
                quick_sim_file = f'{base_tp}/final_qs.xml'
                if os.path.exists(quick_sim_file):
                    run(f"{SSCEXEPATH}/SingleScriptCmd.exe LoadQuickSimResponseFile \"{quick_sim_file}\"")
                else:
                    print("No final_qs.xml file was provided. Skip Loading quicksim!")

                # Start testing
                testLog_file = self.run_TestUnit(base_tp, f'{add_locn}_{add_step}_{add_engid}', today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS)

                log_file = f'{log_folder}/{testLog_file}'
                result = 'FAILED'
                result, line = self.check_test_result(result, log_file, f'{add_locn}_{add_step}_{add_engid}', allow_passed_bins)
                # Check test result
                if result == 'FAILED':
                    # Retest if failed
                    result = self.retest_if_failed_CLASSHOT(line, base_tp, today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS, allow_passed_bins, self.job_input_data, workflow)
                    return result
                elif 'PASSED' in result:
                    return result
                else:
                    print(f'{result} is undefined. Please check the test program result')
                    exit(1)

        else:
            # Start testing
            if tester_prefix not in ['JF', 'FM']:
                self.Polaris(base_tp, temperature)
            else:
                print('Skip ramping up temperature because of power following')
            testLog_file = self.run_TestUnit(base_tp, f'{add_locn}_{add_step}_{add_engid}', today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS)

            log_file = f"{log_folder}/{testLog_file}"
            result = 'FAILED'
            result, line = self.check_test_result(result, log_file, f'{add_locn}_{add_step}_{add_engid}', allow_passed_bins)
            if result == 'FAILED':
                # Retest if failed CLASSHOT
                result = self.retest_if_failed_CLASSHOT(line, base_tp, today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS, allow_passed_bins, self.job_input_data, workflow)
                if result == 'FAILED':
                    self.polaris_set_feedback(base_tp, 'tcase', test_unit=test_unit)
                    self.Polaris(base_tp, '25')
                    sys.exit(1)
            self.polaris_set_feedback(base_tp, 'tcase', test_unit=test_unit)
            self.Polaris(base_tp, '25')
            return result

    def update_ube_for_PBIC_DAB(self, ube, vsid, ituff_file):
        """Update the ube file to add PBIC_DAB data from ituff file"""
        if self.pbic_ube_update:
            print("UBE has been updated with latest PBIC_DAB data. Skip update ube data")
            return 0
        with open(ube, 'r') as file:
            data = file.readlines()

        # Read data to fine the unit, extrace the data from UNIT,{unit} to the next UNIT,
        pattern = re.compile(rf"UNIT,{vsid}(.*?)(?=UNIT,|$)", re.DOTALL)
        match = pattern.search(''.join(data))
        if match:
            unit_data = match.group(1).strip().splitlines()
            for line in unit_data:
                if 'PBIC_DAB' in line:
                    # Remove lines containing 'PBIC_DAB'
                    unit_data.remove(line)
        else:
            print(f"No data found for unit {vsid}")
            sys.exit(1)

        dff_lines = []
        try:
            with open(ituff_file, 'r') as file:
                for line in file:
                    if line.strip().startswith('2_comnt_DFF_Data_'):
                        dff_lines.append(line.strip())
            print(f"Found {len(dff_lines)} lines starting with '2_comnt_DFF_Data_':")

        except FileNotFoundError:
            print(f"File not found: {ituff_file}")
            sys.exit(1)

        for content in dff_lines:
            if '2_comnt_DFF_Data_PKG_' in content:
                content = content.replace('2_comnt_DFF_Data_PKG_', 'PKG,PBIC_DAB,')
                # add content to the first line of unit_data
                unit_data.insert(0, f'{content},')

        # Collect insertions first to avoid modifying list while iterating
        insertions = []
        for i, line in enumerate(unit_data):
            if 'MDPOSITION=' in line:
                die_position = line.split('MDPOSITION=')[1].split(',')[0]

                # Search for die_position in dff_lines
                for dff_line in dff_lines:
                    if die_position in dff_line:
                        dff_line = dff_line.replace(f'2_comnt_DFF_Data_{die_position}_', f'{die_position},PBIC_DAB,')
                        insertions.append((i + 1, f'{dff_line},'))

        # Insert in reverse order to maintain correct indices
        for insert_index, dff_line in reversed(insertions):
            unit_data.insert(insert_index, dff_line)

        # Rewrite the unit_data back to the ube file
        new_unit_section = f"UNIT,{vsid}\n" + '\n'.join(unit_data) + '\n'

        # Replace the original unit section in the file
        original_data = ''.join(data)
        updated_data = re.sub(
            rf"UNIT,{vsid}(.*?)(?=UNIT,|$)",
            new_unit_section.rstrip() + '\n',
            original_data,
            flags=re.DOTALL
        )
        # Write back to file
        with open(ube, 'w') as file:
            file.write(updated_data)
        print(f"Updated unit {vsid} data in {ube}")
        self.pbic_ube_update = True

    def run_add_socket(self, base_tp, add_locn, add_step, add_engid, ube_data_required):
        """This will run additional socket testing"""
        print(f'Running additional socket testing for {add_locn}_{add_step}_{add_engid} with {ube_data_required} data...')
        HDMTTOS = os.getenv('HDMTTOS')
        SSCEXEPATH = f"{HDMTTOS}/Runtime/Release"
        # Getting time
        now = datetime.now()
        current_time = now.strftime("%H-%M-%S")
        today_date = date.today().strftime("%Y-%m-%d")
        print(f"Current time: {today_date}-{current_time}")

        log_folder = f"I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/{today_date}"
        # Set socket uservar
        self.set_socket_uservar(add_locn, add_step, add_engid, SSCEXEPATH)

        if add_step in ['CLASSCOLD', 'CSM', 'PHMCOLD']:
            temperature = '-5'
            print("Setting temperature uservar for CLASSCOLD/CSM/PHMCOLD...")
            run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_TEMPERATURE\" \"{temperature}\"")
        else:
            temperature = '70'
            run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_TEMPERATURE\" \"{temperature}\"")
        tester_name = socket.gethostname()
        tester_prefix = tester_name[:2]
        if tester_prefix not in ['JF', 'PG', 'FM', 'BA', 'HA']:
            print(f"Tester prefix {tester_prefix} is not in the expected list JF, PG, FM, BA, HA.")
            if tester_prefix == 'SR':
                print("Tester prefix is SR, set tester_prefix to BA for uservars setting.")
                tester_prefix = 'BA'
            elif tester_prefix == 'HD':
                print("Tester prefix is HD, set tester_prefix to PG for uservars setting.")
                tester_prefix = 'PG'
            else:
                tester_prefix = 'JF'
        facility_id = f'GDL{tester_prefix}'
        site_id = f'{tester_prefix}lab'
        print(f"Setting uservars SC_FACILITYID: {facility_id}, SC_SITEID: {site_id}")
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_FACILITYID\" \"{facility_id}\"")
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_SITEID\" \"{site_id}\"")
        self.polaris_set_feedback(base_tp, 'pf')
        INIT_result = 'FAILED'
        INIT_result = self.run_INIT(base_tp, f'{add_locn}_{add_step}_{add_engid}', today_date, current_time, log_folder, SSCEXEPATH)
        if INIT_result == 'FAILED':
            print(f'Additional socket {add_locn}_{add_step}_{add_engid} INIT failed. Exit 1.')
            sys.exit(1)

        # Get unit VSID
        print("Setting uservar ube...")
        ube = self.return_ube_file()
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_ULT_DOWNLOAD_PATH\" \"{ube}\"")
        vsid = self.return_vsid(ube)
        run(f"{SSCEXEPATH}/SingleScriptCmd.exe setUserVar \"SCVars\" \"SC_VISUALID\" \"{vsid}\"")
        
        # Update ube to have PBIC_DAB data
        ituff_file = f"{HDMTTOS}/1A_11"
        self.update_ube_for_PBIC_DAB(ube, vsid, ituff_file)

        # run test
        if tester_prefix not in ['JF', 'FM']:
            self.Polaris(base_tp, temperature)
        else:
            print('Skip ramping up temperature because of power following')
        testLog_file = self.run_TestUnit(base_tp, f'{add_locn}_{add_step}_{add_engid}', today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS)

        log_file = f"{log_folder}/{testLog_file}"
        result = 'FAILED'
        result, line = self.check_test_result(result, log_file, f'{add_locn}_{add_step}_{add_engid}')
        if result == 'FAILED':
            # Retest if failed CLASSHOT
            result = self.retest_if_failed_CLASSHOT(line, base_tp, today_date, current_time, log_folder, SSCEXEPATH, HDMTTOS)
            if result == 'FAILED':
                self.polaris_set_feedback(base_tp, 'tcase')
                self.Polaris(base_tp, '25')
                sys.exit(1)
        self.polaris_set_feedback(base_tp, 'tcase')
        self.Polaris(base_tp, '25')

    def main(self):
        """Main entry"""

        stpl_file = self.config_data.get('stpl_file', 'None').strip()
        soc_file = self.config_data.get('soc_file', 'None').strip()
        env_file = self.config_data.get('env_file', 'None').strip()
        plist_file = self.config_data.get('plist_file', 'None').strip()
        BaseTP = os.getcwd()
        STPL = glob.glob(f"*\\{self.bom}\\{stpl_file}")[0]
        SOC = glob.glob(f"*\\*\\*\\Common_{self.bom}\\{soc_file}")[0]
        ENV = glob.glob(f"*\\{self.bom}\\{env_file}")[0]
        PLIST = glob.glob(f"*\\{self.bom}\\{plist_file}")[0]

        # send email to teambot submitter if this is a teambot job submission
        TeamBot.send_mail_if_teambot()
        # if the job is team bot, wait for user to take over tester
        TeamBot.teambot_wait()

        special_socket_list = self.job_input_data.get('SPECIAL_SOCKET', 'NONE').strip()
        print(f'SPECIAL_SOCKET from job input data: {special_socket_list}')
        for special_socket in special_socket_list.split(','):
            print(f'Processing SPECIAL_SOCKET: {special_socket}')
            # Count number of '_' in socket, and set default values.
            if special_socket != 'NONE':
                underscore_count = special_socket.count('_')
                if underscore_count == 0:
                    add_locn = special_socket
                    add_step = 'CLASSHOT'
                    add_engid = 'AF'
                elif underscore_count == 1:
                    add_locn = special_socket.split('_')[0]
                    add_step = special_socket.split('_')[1]
                    add_engid = 'AF'
                elif underscore_count == 2:
                    add_locn = special_socket.split('_')[0]
                    add_step = special_socket.split('_')[1]
                    add_engid = special_socket.split('_')[2]
                else:
                    add_locn = '6248'
                    add_step = 'CLASSHOT'
                    add_engid = 'AF'
            else:
                add_locn = '6248'
                add_step = 'CLASSHOT'
                add_engid = 'AF'

            # Get the whick socket file data
            which_socket_file = 'Shared/BaseInputs/Common/Common_Files/Which_Socket.usrv'
            with open(which_socket_file, 'r') as file:
                which_socket_data = file.readlines()

            # Read which_socket_data to find the matching add_locn and add_step
            pattern = re.compile(rf"SelectorRule DffVars_ReadOptype(.*?)(?=SelectorRule|$)", re.DOTALL)
            match = pattern.search(''.join(which_socket_data))
            if match:
                dffVars_data = match.group(1).strip().splitlines()
            else:
                dffVars_data = []
            ube_data_required = ''
            for line in dffVars_data:
                if 'SORT' in line and add_locn in line and add_step in line:
                    ube_data_required = 'SORT'
                    break
                if 'PBIC_DAB' in line and add_locn in line and add_step in line:
                    ube_data_required = 'PBIC_DAB'
                    break
            else:
                print(f'No matching data found in Which_Socket.usrv for {special_socket} which matches SORT or PBIC_DAB. Exit 1.')
                sys.exit(1)
            wofkflow = self.job_input_data.get('GITHUB_WORKFLOW', 'None')
            print(f'Workflow: {wofkflow}')
            if ube_data_required == 'SORT' or wofkflow == 'SCHEDULER_INIT':
                current_socket = f'{add_locn}_{add_step}_{add_engid}'
                print(f'Running socket: {current_socket} which requires SORT data or SCHEDULER INIT workflow...')
                result = 'FAILED'
                result = self.TPload(BaseTP, STPL, SOC, PLIST, ENV, current_socket)
                if 'PASSED' in result and self.checkname != 'None':
                    result_file = f'{BaseTP}\\{self.checkname}_PASSED.txt'
                    with open (result_file, 'w') as f:
                        f.write('PASSED')
                        return 0
            
            elif ube_data_required == 'PBIC_DAB':
                if not self.pbic_ube_update:
                    print(f'Running 6248_CLASSHOT socket first to determine if additional socket {add_locn}_{add_step}_{add_engid} with PBIC_DAB data is required...')
                    result = self.TPload(BaseTP, STPL, SOC, PLIST, ENV)
                if 'PASSED_B1' in result or self.pbic_ube_update:
                    self.run_add_socket(BaseTP, add_locn, add_step, add_engid, ube_data_required)
                elif 'PASSED' in result:
                    print("Unit passed without B1. No need to run additional socket.")
                    sys.exit(1)
                else:
                    print("Unit failed in 6248 CLASSHOT socket. No need to run additional socket.")
                    sys.exit(1)


class TeamBot:
    """Class to handle TeamBot specific operations."""

    @classmethod
    def check_is_teambot(cls):
        """Check if the job is a TeamBot job by looking for 'D' in the job type."""

        # Get the full file path from the environment variable
        file_path = os.environ.get("_BOT_EMAIL_FNAME", "")
        if file_path:
            # Extract the directory path and file folder
            directory, file_name = os.path.split(file_path)  # Splits into directory and file name
            testerpath, testerdir = os.path.split(directory)  # Splits into parent path and folder name

            # Print the results
            print(f"Path = {testerpath}")
            print(f"Folder = {testerdir}")

            for file in os.listdir(directory):
                if file.endswith(".tar.gz"):
                    name_parts = file.split('_')
                    if len(name_parts) == 3:
                        job_type = name_parts[2].split('.')[0]
                        # Check if job contains "D" (case-insensitive)
                        if 'D' in job_type.upper():
                            print(f"job_type '{job_type}' contains 'D' which represents TeamBot job.")
                            return True
            
            return False

    @classmethod
    def send_mail_if_teambot(cls):
        """Send an email if this is a TeamBot job submission."""
    
        if cls.check_is_teambot():
            file_path = os.environ.get("_BOT_EMAIL_FNAME","")
            if file_path:
                print(f'Writing to: {file_path}')
                with open(file_path, 'w'):
                    pass

    @classmethod
    def teambot_wait(cls):
        """Wait for TeamBot to take over the tester."""
        if not cls.check_is_teambot():
            return

        # Get the full file path from the environment variable
        file_path = os.environ.get("_BOT_EMAIL_FNAME", "")

        # Extract the directory path and file folder
        if file_path:
            directory, file_name = os.path.split(file_path)  # Splits into directory and file name
            print(f'Writing to: {directory}/teambot_wait.txt')
            with open(f'{directory}/teambot_wait.txt', 'w') as fh:
                fh.close()

            print('TeamBot Wait starts.')

class TPBot:

    @classmethod
    def check_is_tpbot(cls):
        """Check if the job is a TPBot job by looking for 'B' in the job type."""

        # Get the full file path from the environment variable
        file_path = os.environ.get("_BOT_EMAIL_FNAME", "")
        if file_path:
            # Extract the directory path and file folder
            directory, file_name = os.path.split(file_path)  # Splits into directory and file name
            testerpath, testerdir = os.path.split(directory)  # Splits into parent path and folder name

            for file in os.listdir(directory):
                if file.endswith(".tar.gz"):
                    name_parts = file.split('_')
                    if len(name_parts) == 3:
                        job_type = name_parts[2].split('.')[0]
                        # Check if job contains "B" (case-insensitive)
                        if 'B' in job_type.upper():
                            print(f"job_type '{job_type}' contains 'B' which represents TPBot job.")
                            return True

            return False

if __name__ == "__main__":
    "Entry point for the script"

    checkname = 'None'
    if len(sys.argv) >= 2:
        print(f"Received argument: {sys.argv[1]}")
        checkname = sys.argv[1]

    # Getting the input for the config file
    ENVFile = glob.glob("*/*/EnvironmentFile.env")[0]
    print(f'ENV file: {ENVFile}')
    bom = ENVFile.split('\\')[-2]

    config_file = f'Shared/POR_TP/{bom}/Scripts/load_and_run_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            print(f'Loaded config file: {config_data}')
    else:
        print(f'{config_file} does NOT exist. Exit...')
        sys.exit(1)

    # Read job_input_json
    job_input_json = 'load_and_run.json'
    if os.path.exists(job_input_json):
        with open(job_input_json, 'r', encoding='utf-8') as f:
            job_input_data = json.load(f)
            print(f'Loaded job input json file: {job_input_data}')
    else:
        print(f'{job_input_json} does NOT exist. Continue with default parameters.')
        job_input_data = {}

    bot = BotTestUnit(config_data, job_input_data, checkname, bom)
    bot.main()



