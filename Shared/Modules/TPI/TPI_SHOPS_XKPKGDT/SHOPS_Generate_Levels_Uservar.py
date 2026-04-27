import pandas as pd
import re
import os

"""
Script Summary:
This script is designed to process hardware configuration data and generate output files for level sequences and user variables for SHOPS.
It reads data from a CSV file containing SHOPS limits and configurations, and produces two output files: one for level sequences and another for user variable definitions.

Key Components:
- **Setup**: Initializes module name, hardware configuration columns, user variable suffix mappings, and other constants.
- **Levels**: Functions to print headers, test modes, force voltage settings, and pin measurements. It processes each row of the input data to generate level sequences.
- **Pingroups**: Functions to write pin group configurations based on hardware configurations and levels.
- **Limits**: Functions to parse voltage limits, apply guardbands, and write limit configurations for different temperature conditions.
- **MTPL UserVars**: Functions to write user variable definitions for different test configurations.
- **TOS Rules**: Functions to write selector rules for various conditions and process types.

Usage:
- The script reads from a CSV file named "SHOPS_limits.csv" and generates two output files: "LevelsSequences_SHOPS.lvl" and "TPI_SHOPS_XKPKGMB.usrv".
- Ensure the input CSV file is formatted correctly with the expected columns for proper processing.

Dependencies:
- Requires the `pandas` library for data manipulation.

Author:
- Leo Huang
- 7/14/2025

Changelog:
v1.0 (7/14/2025) - Initial version
- Basic functionality for processing SHOPS limits and generating output files


v1.1 - Enhanced Hardware Configuration Support
- **BREAKING CHANGE**: Modified CSV structure to use separate columns for each HW config limit
- Added support for hardware-specific limit overrides using separate columns
- Replaced single HW config columns with 4 columns each for LoHot, HiHot, LoCold, HiCold
- Added support for 'X' values to use default limits from base columns

v1.2 (1/5/2026) - Extended Hardware Configuration Support
- Added support for new hardware configurations:
  - S16C_HVM (16-core HVM)
  - S16C_FC (16-core Full Connect)
  - DS28C_HVM (Dual Socket 28-core HVM)
  - DS28C_FC (Dual Socket 28-core Full Connect)
- Enhanced TpRule selector to automatically handle all hardware configurations
- Updated MTPL UserVars to dynamically generate rules for all HW configs
- Improved scalability for future hardware configuration additions
- Add feature in csv file to float pins before measurement (used for grcomp pins)
  - set "VM" in the iForce column to float the pin

V1.3 (2/4/2026) - added grouping processing - Alexander Meadows
V1.4 (2/23/2026)- added iforce,vclamp product patching - Echezona Ezeodili

V1.5 (3/3/2026) - Clamp Limit Check Enhancement
- Added clamp guardband checking for all limit arrays (lo_limit_hot, hi_limit_hot, lo_limit_cold, hi_limit_cold, lo_limit_phmhot, hi_limit_phmhot, lo_limit_phmcold, hi_limit_phmcold)
- Clamp guardband logic: subtract 100mV from positive clamps, add 100mV to negative clamps
- All limit checks now compare against clamp ±100mV as appropriate
- Violations are collected in CLAMP_VIOLATIONS for reporting and file cleanup
- Clamp check can be skipped for specific pins/levels using SKIP_VCLAMP_CHECK as defined in the config file

Expected CSV Format:
- Pin: Pin name
- LevelsName: Level sequence name
- LoLimit (HOT), HiLimit (HOT), LoLimit (COLD), HiLimit (COLD): Default limit values
- VClampHi, VClampLo: Clamp values
- iForce, PreMeasDelay, SequenceBreak: Test parameters
- HW Config Columns: 32 columns for hardware-specific limit overrides (8 configs * 4 limits each)
  - Use 'X' to apply default limits
  - Use specific values (e.g., '1.2V') for custom limits
  - Leave blank to exclude pin from that hardware configuration


To-Do:
- Create function to generate levels tcg file
- Create a chz levels to set all pins to 0V
- Check that clamps are within HPCC spec
- Check that SequenceBreaks are longer than Premeas delay
"""

#########################
# Setup
#########################

# Module name
MODULE_NAME = "TPI_SHOPS_XKPKGDT"

NUM_TMUX = 8
HVM_TESTMODE = True

# Define the hardware configurations with their limit columns
HW_CONFIGS = {
    "Dummy": {"Dummy": "woops" }
}

# Levels to usrvar suffix mapping
USRVAR_SUFFIX = {
    "usrdummy": "UPPER_T012345"
}

# PHM guardband multiplier
PHM_GB_HI = 1
PHM_GB_LO = 1

# Define the COMPACT variable
COMPACT = True  # Set to True for compact format, False for detailed format

pingroups_ec_force_0V = []
pingroups_hpc_force_0V = []
pingroups_hpcdif_force_0V = []
pingroups_dpins_force_0V = []
pingroups_other_force_0V = []

pingroup_list = [
    pingroups_ec_force_0V,
    pingroups_hpc_force_0V,
    pingroups_hpcdif_force_0V,
    pingroups_dpins_force_0V,
    pingroups_other_force_0V
]
#Global variables for settings pins to float or running in parallel or serial execution
FLOATB4 = {}

# Skip limit vs Vclamp check
# Syntax - {level: {pin}}
SKIP_VCLAMP_CHECK = {}
VCLAMP_GB = "0.01V"


PARALLEL = False
INPUTFILENAME = "SHOPS_limits.csv"
# Global mapping used by level generation:
# key   -> (LevelsName, Pin)
# value -> IFORCE symbol name generated in .usrv
IFORCE_SYMBOL_MAP = {}
VCLAMPHI_SYMBOL_MAP = {}
VCLAMPLO_SYMBOL_MAP = {}
SELECTOR_ARGS = []
CLAMP_VIOLATIONS = {}

def setup(file_path):
    """setup the global variables from an external file"""
    variable_names = ["MODULE_NAME","NUM_TMUX","HVM_TESTMODE","HW_CONFIGS","USRVAR_SUFFIX","PHM_GB_HI","PHM_GB_LO","COMPACT","pingroups_ec_force_0V","pingroups_hpc_force_0V","pingroups_hpcdif_force_0V","pingroups_dpins_force_0V","pingroups_other_force_0V","pingroup_list","FLOATB4","PARALLEL","INPUTFILENAME","SKIP_VCLAMP_CHECK","VCLAMP_GB"]
    globals().update(load_variables_from_file(file_path, variable_names))
    for x in variable_names:
        print(f"-INFO- global value {x} updated to {globals()[x]}")
    return


def load_variables_from_file(file_path, variable_names=None):
    """
    Load variables from a Python file using exec().

    Args:
        file_path: Path to the Python file containing variables
        variable_names: List of specific variable names to load (None = load all)

    Returns:
        Dictionary containing the loaded variables
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            file.close()

        # Create a namespace to execute the code in
        namespace = {}

        # Execute the file content in the namespace
        exec(file_content, namespace)

        # Remove built-in variables that exec() adds
        builtin_vars = ['__builtins__']
        for var in builtin_vars:
            namespace.pop(var, None)

        # If specific variables requested, filter them
        if variable_names:
            filtered_vars = {}
            for var_name in variable_names:
                if var_name in namespace:
                    filtered_vars[var_name] = namespace[var_name]
                else:
                    print(f"Warning: Variable '{var_name}' not found in {file_path}")
            return filtered_vars

        return namespace

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}
    except Exception as e:
        print(f"Error loading variables from {file_path}: {e}")
        return {}

#########################
# Levels
#########################

def write_header(file):
    file.write("Version 1.0;\n\n")

def print_delay(file):
    file.write("\tSequenceBreak 0.1ms;\n")

def print_test_hvm_testmode(file, iforce, pre_meas_delay, vclamp):
    file.write("\tHVM_TESTMODE\n\t{\n")
    file.write("\t\tOPMode = \"ISVM\";\n")
    file.write("\t\tPowerSequence = True;\n")
    file.write(f"\t\tVClamp = {vclamp};\n")
    file.write("\t\tIRange = \"IR2_56mA\";\n")
    file.write(f"\t\tIForce = {iforce};\n")
    file.write("\t\tStartMeasurement = True;\n")
    file.write(f"\t\tPreMeasurementDelay = {pre_meas_delay};\n")
    file.write("\t\tSamplingCount = 1;\n")
    file.write("\t\tSamplingRatio = 1;\n")
    file.write("\t\tSamplingMode = \"Trace\";\n")
    file.write("\t}\n")


def print_force_0V(file):
    global pingroup_list

    if HVM_TESTMODE:
        file.write("\tHVM_TESTMODE\n\t{\n")
        file.write("\t\tFreeDriveCurrentHi = 255uA;\n")
        file.write("\t\tFreeDriveCurrentLo = -255uA;\n")
        file.write("\t\tFreeDriveTime = 10ms;\n")
        file.write("\t\tIClampHi = 2.55mA;\n")
        file.write("\t\tIClampLo = -2.55mA;\n")
        file.write("\t\tIRange = \"IR2_56mA\";\n")
        file.write("\t\tOPMode = \"VSIM\";\n")
        file.write("\t\tPowerSequence = True;\n")
        file.write("\t\tVForce = 0V;\n")
        file.write("\t}\n")
        file.write(f"\tSequenceBreak 0.1ms;\n")


    for pingroups in pingroup_list:
        for pingroup in pingroups:
            file.write(f"\t{pingroup}\n\t{{\n")
            file.write("\t\tIClampHi = 0.04;\n")
            file.write("\t\tIClampLo = -0.04;\n")
            file.write("\t\tIRange = \"IR40mA\";\n")
            file.write("\t\tOPMode = \"VSIM\";\n")
            file.write("\t\tPinModeSel = \"PMU\";\n")
            file.write("\t\tVForce = 0V;\n")
            file.write("\t}\n")
        file.write("\tSequenceBreak 0ms;\n")


def print_pin_meas(file, pin, iforce, pre_meas_delay, vclamp_hi, vclamp_lo):
    if pin == "HVM_TESTMODE" and HVM_TESTMODE:
        iforce_value = float(re.findall(r'-?[\d.]+', iforce)[0])  # get the numeric part of iforce

        if iforce_value > 0:
            vclamp = vclamp_hi
        else:
            vclamp = vclamp_lo

        print_test_hvm_testmode(file, iforce, pre_meas_delay, vclamp)

    elif iforce == "VM":
        file.write(f"\t{pin}\n\t{{\n")
        file.write("\t\tOPMode = \"VM\";\n")
        file.write("\t\tPinModeSel = \"PMU\";\n")
        file.write("\t\tIClampHi = 0.04;\n")
        file.write("\t\tIClampLo = -0.04;\n")
        file.write("\t\tIRange = \"IR40mA\";\n")
        file.write("\t\tVForce = 0V;\n")
        file.write("\t}\n")

    else:
        file.write(f"\t{pin}\n\t{{\n")
        file.write("\t\tOPMode = \"ISVM\";\n")
        file.write("\t\tPinModeSel = \"PMU\";\n")
        file.write("\t\tIRange = \"IR1mA\";\n")
        file.write(f"\t\tIForce = {iforce};\n")
        file.write(f"\t\tVClampHi = {vclamp_hi};\n")
        file.write(f"\t\tVClampLo = {vclamp_lo};\n")
        file.write("\t\tStartMeasurement = True;\n")
        file.write(f"\t\tPreMeasurementDelay = {pre_meas_delay};\n")
        file.write("\t\tSamplingCount = 1;\n")
        file.write("\t\tSamplingRatio = 1;\n")
        file.write("\t\tSamplingMode = \"Trace\";\n")
        file.write("\t}\n")


def set_pins_to_0V(file, pinsin):
    test_list = [0,0]
    #print(f"pinsin is {pinsin} and len is {len(pinsin)}")
    if type(pinsin) == type(test_list) and len(pinsin) > 1:
        #print("a")
        for pins in pinsin:
            if "HVM" in pins:
                print(f"pins is {pins}")
            if ( pins == ["HVM_TESTMODE"] or pins == "HVM_TESTMODE" ) and HVM_TESTMODE:
                file.write("\tHVM_TESTMODE\n\t{\n")
                file.write("\t\tFreeDriveCurrentHi = 255uA;\n")
                file.write("\t\tFreeDriveCurrentLo = -255uA;\n")
                file.write("\t\tFreeDriveTime = 10ms;\n")
                file.write("\t\tIClampHi = 2.55mA;\n")
                file.write("\t\tIClampLo = -2.55mA;\n")
                file.write("\t\tIRange = \"IR2_56mA\";\n")
                file.write("\t\tOPMode = \"VSIM\";\n")
                file.write("\t\tPowerSequence = True;\n")
                file.write("\t\tVForce = 0V;\n")
                file.write("\t}\n")
            else:
                file.write(f"\t{pins}\n\t{{\n")
                file.write("\t\tOPMode = \"VSIM\";\n")
                file.write("\t\tPinModeSel = \"PMU\";\n")
                file.write("\t\tIClampHi = 0.04;\n")
                file.write("\t\tIClampLo = -0.04;\n")
                file.write("\t\tIRange = \"IR40mA\";\n")
                file.write("\t\tVForce = 0V;\n")
                file.write("\t}\n")
    else:
        #print("b")
        pins = pinsin[0]
        if (pins == ["HVM_TESTMODE"] or pins == "HVM_TESTMODE") and HVM_TESTMODE:
            file.write("\tHVM_TESTMODE\n\t{\n")
            file.write("\t\tFreeDriveCurrentHi = 255uA;\n")
            file.write("\t\tFreeDriveCurrentLo = -255uA;\n")
            file.write("\t\tFreeDriveTime = 10ms;\n")
            file.write("\t\tIClampHi = 2.55mA;\n")
            file.write("\t\tIClampLo = -2.55mA;\n")
            file.write("\t\tIRange = \"IR2_56mA\";\n")
            file.write("\t\tOPMode = \"VSIM\";\n")
            file.write("\t\tPowerSequence = True;\n")
            file.write("\t\tVForce = 0V;\n")
            file.write("\t}\n")
        else:
            file.write(f"\t{pins}\n\t{{\n")
            file.write("\t\tOPMode = \"VSIM\";\n")
            file.write("\t\tPinModeSel = \"PMU\";\n")
            file.write("\t\tIClampHi = 0.04;\n")
            file.write("\t\tIClampLo = -0.04;\n")
            file.write("\t\tIRange = \"IR40mA\";\n")
            file.write("\t\tVForce = 0V;\n")
            file.write("\t}\n")

def ensure_row(matrix, row_index):
    return matrix.extend([[] for _ in range(row_index + 1 - len(matrix))]) or matrix

def extend_matrix_rows(matrix_dict, key, new_data):
    """Extend existing rows or create new matrix"""
    existing_matrix = matrix_dict.setdefault(key, [])

    # If matrix doesn't exist, just add the new data
    if not existing_matrix:
        matrix_dict[key] = [list(row) for row in new_data]
    else:
        # Extend existing rows with new data
        for i, new_row in enumerate(new_data):
            if i < len(existing_matrix):
                existing_matrix[i].extend(new_row)
            else:
                # If new_data has more rows, add them as new rows
                existing_matrix.append(list(new_row))

def contains_number(string):
    return any(char.isdigit() for char in string)

def ifvcperprod(value,level,pin,ifvclh):
    row_key = (level, pin)
    output = "THERE IS AN ISSUE HERE!! ERROR!!"
    if ifvclh == "i":
        output = value
        if row_key in IFORCE_SYMBOL_MAP:
            output = f"{MODULE_NAME}::IFORCE.{IFORCE_SYMBOL_MAP[row_key]}"
    elif ifvclh == "vh":
        # Use generated VCLAMPHI/VCLAMPLO uservar symbols when available
        output = value
        if row_key in VCLAMPHI_SYMBOL_MAP:
            output = f"{MODULE_NAME}::VCLAMPHI.{VCLAMPHI_SYMBOL_MAP[row_key]}"
    elif ifvclh == "vl":
        output = value
        if row_key in VCLAMPLO_SYMBOL_MAP:
            output = f"{MODULE_NAME}::VCLAMPLO.{VCLAMPLO_SYMBOL_MAP[row_key]}"
    else:
        print("You made a typo, go fix it")
    return output

def write_level_sequence(shops_file, output_filename):
    # Read the Excel file into a DataFrame
    df = pd.read_csv(shops_file)
    empty = ""
    # Open the output file for writing
    with open(output_filename, "w") as file:
        write_header(file)
        product_missing_group_base = 30
        mod = "Na"
        sequence_break_time = 0
        current_level_name = None
        missedpin = []
        pins_to_reset = []
        group_to_pin = [[]]
        dict_to_group_to_pin = {}
        last_sequence_break_time = .1
        if PARALLEL:
            for index, row in df.iterrows():
                #print(f"{index} and level is {row['LevelsName']}")
                if row['LevelsName'] != current_level_name:
                    # If it's a new LevelsName, close the previous block (if any) and start a new one
                    if current_level_name is not None:
                        #file.write("}\n\n")
                        extend_matrix_rows(dict_to_group_to_pin, current_level_name, group_to_pin)
                        group_to_pin = [[]]
                    current_level_name = row['LevelsName']

                if "," not in str(row['Group']) and not pd.isna(row['Group'])and row['Group'] is not None:
                    group_to_pin = ensure_row(group_to_pin,int(row['Group']))
                    group_to_pin[int(row['Group'])].append(row['Pin'])
                elif not pd.isna(row['Group']) and row['Group'] is not None: # all_shops_upper_univ_x_x_pkg_level is config 0, so we should check for that
                    #print(row['LevelsName'])
                    #print(row['Pin'])
                    if contains_number(row['LevelsName']):
                        mod = int(re.search(r'\d+', row['LevelsName']).group())
                    else:
                        mod = 0
                    mod2 = row["Group"].split(",")
                    #print(f"mod2 = {mod2} from {row['Group']} mod is type {type(mod)}")
                    i = (int(mod))*4
                    try:
                        if int(mod2[mod]) == 0:
                            print(f"mod = {mod} and mod2 = {mod2} while {row['Group']} value is 0 value, so skipping")
                            continue
                        #print(f'a = {int(mod2[mod])+i}')
                        a=int(mod2[mod])+i
                        group_to_pin = ensure_row(group_to_pin,a)
                        #print(f'grouptopin = {group_to_pin}')
                        group_to_pin[a].append(row['Pin'])
                        #print(f"level is {row['LevelsName']} pin is {row["Pin"]} group is {a}")
                    except:
                        print(f"mod = {mod} and mod2 = {mod2} while {row['Group']} doesn't have a {mod} value")
                else:
                    missedpin.append(row['Pin'])
                    a = len(missedpin) + product_missing_group_base
                    print(f"missed: {current_level_name}'s pin: {row['Pin']} assigning to group {a}")
                    group_to_pin = ensure_row(group_to_pin,a)
                    group_to_pin[a].append(row['Pin'])
            # Iterate over each row in the DataFrame
            extend_matrix_rows(dict_to_group_to_pin, current_level_name, group_to_pin)
            #print(dict_to_group_to_pin)
            for level in dict_to_group_to_pin:
                if len(dict_to_group_to_pin[level]) > 1:
                    print(f"len is {len(dict_to_group_to_pin[level])} lvl is {level}")
                    file.write(f"Levels {level}\n{{\n")
                    print_force_0V(file)
                    #print(f"level is {level} content is {dict_to_group_to_pin[level]}")
                    group0 = True
                    for groupnum in dict_to_group_to_pin[level]:
                        #print(f"groupnum = {groupnum} in {dict_to_group_to_pin[level]} for level {level}")
                        if group0:
                            #print("skipping group 0")
                            group0 = False
                            continue
                        floatlist = False
                        if level in FLOATB4:
                            for x in groupnum:
                                if x in FLOATB4[level]:
                                    if floatlist == False:
                                        floatlist = []
                                    floatlist.append(empty.join(FLOATB4[level][x]))
                        if floatlist: #this is to enable setting floating pins before any execution of a specific level in a specific group
                            for x in floatlist:
                                print_pin_meas(file,x,"VM","NA","NA","NA")
                                pins_to_reset.append(x)
                                print(f"{level}: floating pin {x} for groupnum {groupnum}")
                            file.write(f"\tSequenceBreak {last_sequence_break_time}ms;\n")
                        for pinname in groupnum:
                            prerow = df[df['Pin']==pinname]
                            row = prerow[prerow['LevelsName']==level]
                            #print(f"bacon is good but row pin is {row['Pin']} of type {type(row['Pin'])} and len {len(row['Pin'])}")
                            if not pd.isna(row['Pin'].item()):
                                #print(f"pin = {row['Pin'].item()}")
                                print_pin_meas(
                                    file,
                                    row['Pin'].item(),
                                    ifvcperprod(row['iForce'].item(),level,row['Pin'].item(),"i"),#row['iForce'].item(),
                                    row['PreMeasDelay'].item(),
                                    ifvcperprod(row['VClampHi'].item(),level,row['Pin'].item(),"vh"),
                                    ifvcperprod(row['VClampLo'].item(),level,row['Pin'].item(),"vl")
                                    )
                                if row['iForce'].item() != "VM":
                                    pins_to_reset.append(row['Pin'].item())
                                    if float(row['SequenceBreak'].item().split('ms')[0]) > sequence_break_time:
                                        #print(f"sequence_break_time = {sequence_break_time} is changing due to {row['SequenceBreak'].item().split('ms')[0]} of pin {row['Pin'].item()} in level {level} ")
                                        sequence_break_time = float(row['SequenceBreak'].item().split('ms')[0])
                                        print(f"setting sequence break time to {sequence_break_time}")
                                        last_sequence_break_time = sequence_break_time
                        if len(pins_to_reset) > 0:
                            file.write(f"\tSequenceBreak {sequence_break_time}ms;\n")
                            #print(f"pinstoreset len is {len(pins_to_reset)} and value is{pins_to_reset} ")
                            set_pins_to_0V(file, pins_to_reset)
                            file.write(f"\tSequenceBreak {sequence_break_time}ms;\n")
                            pins_to_reset.clear()
                            sequence_break_time = 0
                    file.write("}\n\n")
                    sequence_break_time = 0
                else:
                    print(f"level {level} is {dict_to_group_to_pin[level]} is empty skipping it")
        else:
            for index, row in df.iterrows():
                # Check if the LevelsName has changed
                if row['LevelsName'] != current_level_name:
                    # If it's a new LevelsName, close the previous block (if any) and start a new one
                    if current_level_name is not None:
                        file.write("}\n\n")

                    current_level_name = row['LevelsName']
                    file.write(f"Levels {current_level_name}\n{{\n")

                    # Call print_force_0V at the beginning of each Levels block
                    print_force_0V(file)
                floatlist = False
                if current_level_name in FLOATB4:
                    if row['Pin'] in FLOATB4[current_level_name]:
                        if floatlist == False:
                            floatlist = []
                        floatlist.append(empty.join(FLOATB4[current_level_name][row['Pin']]))
                if floatlist: #this is to enable setting floating pins before any execution of a specific level in a specific group
                    for x in floatlist:
                        print_pin_meas(file,x,"VM","NA","NA","NA")
                        pins_to_reset.append(x)
                        print(f"-INFO- {current_level_name}: floating pin {x} for nonparallel")
                    file.write(f"\tSequenceBreak {last_sequence_break_time}ms;\n")
                # Write the pin measurement details
                print_pin_meas(
                    file,
                    row['Pin'],
                    ifvcperprod(row['iForce'],current_level_name,row['Pin'],"i"),
                    row['PreMeasDelay'],
                    ifvcperprod(row['VClampHi'],current_level_name,row['Pin'],"vh"),
                    ifvcperprod(row['VClampLo'],current_level_name,row['Pin'],"vl")
                )

                # Collect pins to reset
                # Do not add pins that are floated (VM) to the reset list
                if row['iForce'] != "VM":
                    pins_to_reset.append(row['Pin'])

                # If there's a sequence break, reset all collected pins to 0V
                if row['SequenceBreak']:
                    if row['iForce'] != "VM":
                        file.write(f"\tSequenceBreak {row['SequenceBreak']};\n")
                    set_pins_to_0V(file, pins_to_reset)
                    file.write(f"\tSequenceBreak {row['SequenceBreak']};\n")
                    pins_to_reset.clear()
                    last_sequence_break_time = float(row['SequenceBreak'].split('ms')[0])
                    #print(f"setting sequence break time to {sequence_break_time}")

        # Close the last block
        if current_level_name is not None:
            file.write("}\n")

#########################
# Pingroups
#########################

def get_limit_value_from_columns(row, hw_config, limit_type):
    """Get limit value from separate columns, with 'X' meaning use default."""
    # Map limit_type to column keys and default columns
    limit_mappings = {
        0: ("lo_hot", "LoLimit (HOT)"),
        1: ("hi_hot", "HiLimit (HOT)"),
        2: ("lo_cold", "LoLimit (COLD)"),
        3: ("hi_cold", "HiLimit (COLD)")
    }

    column_key, default_column = limit_mappings[limit_type]
    hw_column = HW_CONFIGS[hw_config][column_key]

    # Get the value from the HW-specific column
    hw_value = row[hw_column]

    # If empty or NaN, return None (will use default)
    if pd.isna(hw_value) or hw_value == '':
        return row[default_column]

    # If 'X', use the default column value
    if str(hw_value).strip().upper() == 'X':
        return row[default_column]

    # Otherwise use the custom value
    return hw_value


def write_pingroup(file, df, levels_name, pingroup_name):
    for hw_config in HW_CONFIGS.keys():
        pins = []
        for _, row in df[df['LevelsName'] == levels_name].iterrows():
            # Check if any of the 4 limit columns for this HW config have values (including 'X')
            has_values = False
            for limit_type in range(4):
                column_key = ["lo_hot", "hi_hot", "lo_cold", "hi_cold"][limit_type]
                hw_column = HW_CONFIGS[hw_config][column_key]
                hw_value = row[hw_column]
                if pd.notna(hw_value) and hw_value != '':
                    has_values = True
                    break

            if has_values:
                pins.append(row['Pin'])

        pin_string = ",".join(pins)
        if pin_string:
            file.write(f"\tString {hw_config}_{pingroup_name} = \"{pin_string}\";\n")
    file.write("\n")


def write_pingroups(file, df):
    # header
    file.write("UserVars PINGROUPS\n{\n")

    for level, suffix in USRVAR_SUFFIX.items():
        write_pingroup(file, df, level, suffix)

    # closing bracket
    file.write("}\n\n")

#########################
# Limits
#########################

def parse_voltage_list(voltage_list):
    """Extract the numeric part of the voltage and its unit for multiple entries."""
    parsed_entries = []
    for limit in voltage_list:
        if not limit:  # Skip empty entries
            continue
        limit_text = str(limit).strip()
        # Support selector-style entries by taking base token only, e.g. "-1.5V, S28C=-3V" -> "-1.5V"
        if ',' in limit_text and '=' in limit_text:
            limit_text = limit_text.split(',', 1)[0].strip()

        if 'mV' in limit_text:
            parsed_entries.append((float(limit_text.replace('mV', '')), 'mV'))
        elif 'V' in limit_text:
            parsed_entries.append((float(limit_text.replace('V', '')), 'V'))
        else:
            print(f"Debug: Problematic limit: '{limit}'")  # Debugging information
            raise ValueError(f"Unknown unit in value: {limit}")
    return parsed_entries


def apply_guardband(value, unit, factor):
    """Apply guardband to the voltage value."""
    if unit == 'mV':
        return value * factor, 'mV'
    elif unit == 'V':
        return value * factor, 'V'
    else:
        raise ValueError(f"Unknown unit: {unit}")

def clamp_gb(val, unit):
    """
    Adjust clamp value for guardband:
    - If positive, subtract 100mV (0.1V or 100mV)
    - If negative, add 100mV (0.1V or 100mV)
    """
    try:
        gb_value, gb_unit = parse_voltage_list([VCLAMP_GB])[0]
    except Exception:
        gb_value, gb_unit = 0.01, 'V'  #default 10mV

    if unit == 'V':
        gb_in_unit = gb_value if gb_unit == 'V' else gb_value / 1000.0
        return val - gb_in_unit if val >= 0 else val + gb_in_unit
    elif unit == 'mV':
        gb_in_unit = gb_value if gb_unit == 'mV' else gb_value * 1000.0
        return val - gb_in_unit if val >= 0 else val + gb_in_unit
    else:
        return val

def format_voltage(value, unit):
    """Format voltage float to a string with unit."""
    return f"{value:.2f}{unit}"


def convert_to_volts(value, unit):
    """Convert the value to volts if necessary."""
    if unit == 'mV':
        return value / 1000.0
    return value


def should_check_vclamp(level, pin):
    return not (level in SKIP_VCLAMP_CHECK and pin in SKIP_VCLAMP_CHECK.get(level, set()))


def check_limits_vs_clamp(levels, pins, hw_config, check_name, limits_with_units, clamp_with_units, is_low_limit):
    for lvl, pin, limit_pair, clamp_pair in zip(levels, pins, limits_with_units, clamp_with_units):
        if not should_check_vclamp(lvl, pin):
            continue

        limit_value, limit_unit = limit_pair
        clamp_value, clamp_unit = clamp_pair
        limit_v = convert_to_volts(limit_value, limit_unit)
        clamp_gb_value = clamp_gb(clamp_value, clamp_unit)
        clamp_v = convert_to_volts(clamp_gb_value, clamp_unit)

        violation = (limit_v < clamp_v) if is_low_limit else (limit_v > clamp_v)
        if violation:
            key = f"-ERROR- {lvl}|{pin}|{hw_config}|{check_name}"
            CLAMP_VIOLATIONS[key] = (
                f"{check_name} limit={safe_round(limit_value)}{limit_unit} "
                f"clamp_gb={safe_round(clamp_gb_value)}{clamp_unit} (raw={safe_round(clamp_value)}{clamp_unit})"
            )


def get_limit_values_for_config(df, hw_config, levels_name, limit_type):
    """Get limit values using separate columns approach."""
    matching_rows = df[df['LevelsName'] == levels_name]
    limit_values = []

    for _, row in matching_rows.iterrows():
        # Check if this pin should be included for this HW config
        has_any_hw_values = False
        for lt in range(4):
            column_key = ["lo_hot", "hi_hot", "lo_cold", "hi_cold"][lt]
            hw_column = HW_CONFIGS[hw_config][column_key]
            if pd.notna(row[hw_column]) and row[hw_column] != '':
                has_any_hw_values = True
                break

        if has_any_hw_values:
            limit_value = get_limit_value_from_columns(row, hw_config, limit_type)
            if limit_value is not None:
                limit_values.append(limit_value)

    return limit_values


def write_limit(file, df, levels_name, limit_name):
    # Initialize lists to store the results
    lo_limit_phmhot_with_units = []
    hi_limit_phmhot_with_units = []
    lo_limit_phmcold_with_units = []
    hi_limit_phmcold_with_units = []
    lo_limit_loose_with_units = []
    hi_limit_loose_with_units = []

    for hw_config in HW_CONFIGS.keys():
        # Use the new function to get limit values for each limit type
        lo_limit_hot = get_limit_values_for_config(df, hw_config, levels_name, 0)  # LoLimit_HOT
        hi_limit_hot = get_limit_values_for_config(df, hw_config, levels_name, 1)  # HiLimit_HOT
        lo_limit_cold = get_limit_values_for_config(df, hw_config, levels_name, 2)  # LoLimit_COLD
        hi_limit_cold = get_limit_values_for_config(df, hw_config, levels_name, 3)  # HiLimit_COLD

        # For clamps, we still use the original columns since they're not part of the HW config
        matching_rows = df[df['LevelsName'] == levels_name]
        # Only include rows that have values for this HW config
        filtered_rows = []
        for _, row in matching_rows.iterrows():
            has_any_hw_values = False
            for lt in range(4):
                column_key = ["lo_hot", "hi_hot", "lo_cold", "hi_cold"][lt]
                hw_column = HW_CONFIGS[hw_config][column_key]
                if pd.notna(row[hw_column]) and row[hw_column] != '':
                    has_any_hw_values = True
                    break
            if has_any_hw_values:
                filtered_rows.append(row)
        pins = [row['Pin'] for row in filtered_rows]
        level = [row['LevelsName'] for row in filtered_rows]
        lo_clamp = [row['VClampLo'] for row in filtered_rows]
        hi_clamp = [row['VClampHi'] for row in filtered_rows]
        lo_limit_hot_string = ",".join(str(x) for x in lo_limit_hot)
        hi_limit_hot_string = ",".join(str(x) for x in hi_limit_hot)
        lo_limit_cold_string = ",".join(str(x) for x in lo_limit_cold)
        hi_limit_cold_string = ",".join(str(x) for x in hi_limit_cold)

        # Convert limits to limit/unit tuple
        lo_limit_hot_with_units = parse_voltage_list(lo_limit_hot)
        hi_limit_hot_with_units = parse_voltage_list(hi_limit_hot)
        lo_limit_cold_with_units = parse_voltage_list(lo_limit_cold)
        hi_limit_cold_with_units = parse_voltage_list(hi_limit_cold)

        # Convert clamp to tuple
        lo_clamp_parsed = parse_voltage_list(lo_clamp)
        hi_clamp_parsed = parse_voltage_list(hi_clamp)

        # Determine if the level is upper or lower based on levels_name
        is_upper = 'upper' in levels_name.lower()

        # --- Limit vs Clamp ---
        # Process limits and create tuple list (limit, unit)
        for value, unit in lo_limit_hot_with_units:
            result = apply_guardband(value, unit, PHM_GB_LO) if is_upper else apply_guardband(value, unit, PHM_GB_HI)
            lo_limit_phmhot_with_units.append(result)

        for value, unit in hi_limit_hot_with_units:
            result = apply_guardband(value, unit, PHM_GB_HI) if is_upper else apply_guardband(value, unit, PHM_GB_LO)
            hi_limit_phmhot_with_units.append(result)

        for value, unit in lo_limit_cold_with_units:
            result = apply_guardband(value, unit, PHM_GB_LO) if is_upper else apply_guardband(value, unit, PHM_GB_HI)
            lo_limit_phmcold_with_units.append(result)

        for value, unit in hi_limit_cold_with_units:
            result = apply_guardband(value, unit, PHM_GB_HI) if is_upper else apply_guardband(value, unit, PHM_GB_LO)
            hi_limit_phmcold_with_units.append(result)

        check_limits_vs_clamp(level, pins, hw_config, "lo_limit_hot", lo_limit_hot_with_units, lo_clamp_parsed, True)
        check_limits_vs_clamp(level, pins, hw_config, "hi_limit_hot", hi_limit_hot_with_units, hi_clamp_parsed, False)
        check_limits_vs_clamp(level, pins, hw_config, "lo_limit_cold", lo_limit_cold_with_units, lo_clamp_parsed, True)
        check_limits_vs_clamp(level, pins, hw_config, "hi_limit_cold", hi_limit_cold_with_units, hi_clamp_parsed, False)
        check_limits_vs_clamp(level, pins, hw_config, "lo_limit_phmhot", lo_limit_phmhot_with_units, lo_clamp_parsed, True)
        check_limits_vs_clamp(level, pins, hw_config, "hi_limit_phmhot", hi_limit_phmhot_with_units, hi_clamp_parsed, False)
        check_limits_vs_clamp(level, pins, hw_config, "lo_limit_phmcold", lo_limit_phmcold_with_units, lo_clamp_parsed, True)
        check_limits_vs_clamp(level, pins, hw_config, "hi_limit_phmcold", hi_limit_phmcold_with_units, hi_clamp_parsed, False)


        if lo_limit_phmhot_with_units and lo_limit_phmcold_with_units:
            lo_limit_loose_with_units = [(min(hot[0], cold[0]), hot[1]) for hot, cold in zip(lo_limit_phmhot_with_units, lo_limit_phmcold_with_units)]
        if hi_limit_phmhot_with_units and hi_limit_phmcold_with_units:
            hi_limit_loose_with_units = [(max(hot[0], cold[0]), hot[1]) for hot, cold in zip(hi_limit_phmhot_with_units, hi_limit_phmcold_with_units)]

        lo_limit_phmhot_string = ','.join(f"{safe_round(value)}{unit}" for value, unit in lo_limit_phmhot_with_units)
        hi_limit_phmhot_string = ','.join(f"{safe_round(value)}{unit}" for value, unit in hi_limit_phmhot_with_units)
        lo_limit_phmcold_string = ','.join(f"{safe_round(value)}{unit}" for value, unit in lo_limit_phmcold_with_units)
        hi_limit_phmcold_string = ','.join(f"{safe_round(value)}{unit}" for value, unit in hi_limit_phmcold_with_units)
        lo_limit_loose_string = ','.join(f"{safe_round(value)}{unit}" for value, unit in lo_limit_loose_with_units)
        hi_limit_loose_string = ','.join(f"{safe_round(value)}{unit}" for value, unit in hi_limit_loose_with_units)

        # Write the configuration to the file
        if lo_limit_hot_string and hi_limit_hot_string and lo_limit_cold_string and hi_limit_cold_string:
            file.write(f"\tString {hw_config}_{limit_name}_LOLIMIT_CHOT = \"{lo_limit_hot_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_HILIMIT_CHOT = \"{hi_limit_hot_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_LOLIMIT_CCOLD = \"{lo_limit_cold_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_HILIMIT_CCOLD = \"{hi_limit_cold_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_LOLIMIT_PHMHOT = \"{lo_limit_phmhot_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_HILIMIT_PHMHOT = \"{hi_limit_phmhot_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_LOLIMIT_PHMCOLD = \"{lo_limit_phmcold_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_HILIMIT_PHMCOLD = \"{hi_limit_phmcold_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_LOLIMIT_LOOSE = \"{lo_limit_loose_string}\";\n")
            file.write(f"\tString {hw_config}_{limit_name}_HILIMIT_LOOSE = \"{hi_limit_loose_string}\";\n")
            file.write("\n")

        # Clear the lists after processing each hardware configuration
        lo_limit_phmhot_with_units.clear()
        hi_limit_phmhot_with_units.clear()
        lo_limit_phmcold_with_units.clear()
        hi_limit_phmcold_with_units.clear()
        lo_limit_loose_with_units.clear()
        hi_limit_loose_with_units.clear()

def safe_round(value, places=3):
    """Safely round a value, handling various input types"""
    try:
        if isinstance(value, str):
            value = float(value)
        return round(float(value), places)
    except (ValueError, TypeError):
        return value

def write_limits(file, df):
    # Write UserVars LIMITS section
    file.write("UserVars LIMITS\n{\n")

    for level, suffix in USRVAR_SUFFIX.items():
        write_limit(file, df, level, suffix)

    file.write("}\n\n")

#########################
# MTPL usrvars
#########################

def generate_hw_config_selector(hw_configs, pingroup_or_limit, test, tmux_suffix):
    """Generate a dynamic hardware configuration selector based on available configs. UNUSED!!!!"""
    # Create the selector arguments dynamically
    args = []
    global SELECTOR_ARGS
    for hw_config in hw_configs:
        if pingroup_or_limit == "PINGROUPS":
            args.append(f"{pingroup_or_limit}.{hw_config}_{test}{tmux_suffix}")
        else:  # LIMITS
            args.append(f"{pingroup_or_limit}.{hw_config}_{test}{tmux_suffix}")

    # Pad with empty strings if needed (TpRule expects specific number of arguments)
    while len(args) < 8:  # Assuming max 8 HW configs for now
        args.append('""')

    # Create the selector call
    SELECTOR_ARGS = ", ".join(args)
    return f"{MODULE_NAME}_Rules.If_HW_CONFIG({SELECTOR_ARGS})"


def write_mtpl_usrvars(file):
    # Write UserVars TPI_SHOPS_XKPKGMB section
    file.write(f"UserVars {MODULE_NAME}\n{{\n")

    tests = ["UPPER", "LOWER"]
    hw_configs = list(HW_CONFIGS.keys())

    # HVM and FC configs
    hvm_configs = [config for config in hw_configs if "HVM" in config]
    fc_configs = [config for config in hw_configs if "FC" in config]

    # Generate HVM rules
    for test in tests:
        for i in range(0, NUM_TMUX):
            tmux_suffix = f"_T{i}"
            file.write(f"    # {test} TMUX{tmux_suffix}\n")

            # Generate pingroup selector for HVM configs
            hvm_pingroup_args = ", ".join([f"PINGROUPS.{config}_{test}{tmux_suffix}" for config in hvm_configs])

            # default case will be hw_config[0]
            hvm_pingroup_args += (f", PINGROUPS.{hvm_configs[0]}_{test}{tmux_suffix}")

            file.write(f"    String {test}_PINS{tmux_suffix} = {MODULE_NAME}_Rules.If_HW_CONFIG({hvm_pingroup_args});\n")

            # Generate limit selectors for HVM configs
            limit_types = [
                "LOLIMIT_CHOT", "HILIMIT_CHOT", "LOLIMIT_CCOLD", "HILIMIT_CCOLD",
                "LOLIMIT_PHMHOT", "HILIMIT_PHMHOT", "LOLIMIT_PHMCOLD", "HILIMIT_PHMCOLD",
                "LOLIMIT_LOOSE", "HILIMIT_LOOSE"
            ]

            for limit_type in limit_types:
                hvm_limit_args = ", ".join([f"LIMITS.{config}_{test}{tmux_suffix}_{limit_type}" for config in hvm_configs])
                # default case will be hw_config[0]
                hvm_limit_args += (f", LIMITS.{hvm_configs[0]}_{test}{tmux_suffix}_{limit_type}")
                file.write(f"    String {test}_{limit_type}{tmux_suffix} = {MODULE_NAME}_Rules.If_HW_CONFIG({hvm_limit_args});\n")

            file.write("\n")

    # Generate FC rules
    file.write(f"    # Full Connect\n")
    for test in tests:
        for i in range(0, NUM_TMUX):
            tmux_suffix = f"_T{i}"
            file.write(f"    # {test} TMUX{tmux_suffix}\n")

            # Generate pingroup selector for FC configs
            fc_pingroup_args = ", ".join([f"PINGROUPS.{config}_{test}{tmux_suffix}" for config in fc_configs])

            # default case will be hw_config[0]
            fc_pingroup_args += (f", PINGROUPS.{hvm_configs[0]}_{test}{tmux_suffix}")

            file.write(f"    String FC_{test}_PINS{tmux_suffix} = {MODULE_NAME}_Rules.If_HW_CONFIG({fc_pingroup_args});\n")

            # Generate limit selectors for FC configs
            for limit_type in limit_types:
                fc_limit_args = ", ".join([f"LIMITS.{config}_{test}{tmux_suffix}_{limit_type}" for config in fc_configs])
                # default case will be hw_config[0]
                fc_limit_args += (f", LIMITS.{fc_configs[0]}_{test}{tmux_suffix}_{limit_type}")
                file.write(f"    String FC_{test}_{limit_type}{tmux_suffix} = {MODULE_NAME}_Rules.If_HW_CONFIG({fc_limit_args});\n")

            file.write("\n")

    file.write("}\n")

#########################
# TOS Rules
#########################

def write_tos_rules(file):
    # Write SelectorRuleCollection section
    global SELECTOR_ARGS
    file.write(f"\nSelectorRuleCollection {MODULE_NAME}_Rules\n{{\n")
    file.write("    SelectorRule If_HOT_PHMHOT_COLD_PHMCOLD_FUSE(HOT, PHMHOT, COLD, PHMCOLD, FUSE, default)\n")
    file.write("    {\n")
    file.write("        HOT => contains(__shared__::LocationSets.CHOT, \"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\") || contains(__shared__::LocationSets.RCHOT,\"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\");\n")
    file.write("        PHMHOT => contains(__shared__::LocationSets.PHMHOT, \"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\");\n")
    file.write("        COLD => contains(__shared__::LocationSets.CCOLD,\"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\") || contains(__shared__::LocationSets.RCCOLD,\"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\");\n")
    file.write("        PHMCOLD => contains(__shared__::LocationSets.PHMCOLD, \"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\");\n")
    file.write("        FUSE => contains(__shared__::LocationSets.FUSE, \"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\");\n")
    file.write("        default;\n")
    file.write("    }\n")
    file.write("    SelectorRule If_SAMPLING(ON, OFF)\n")
    file.write("    {\n")
    file.write("        ON => contains(__shared__::LocationSets.PHM, \"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\") || contains(__shared__::LocationSets.FUSE,\"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\") || contains(__shared__::SCVars.SC_ENGID, \"Q*\");\n")
    file.write("        OFF;\n")
    file.write("    }\n")
    file.write("    SelectorRule If_HOT_COLD(HOT, COLD, default)\n")
    file.write("    {\n")
    file.write("        HOT => contains(__shared__::LocationSets.HOT,\"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\");\n")
    file.write("        COLD => contains(__shared__::LocationSets.COLD,\"[\" + __shared__::SCVars.SC_LOCN + \":\" + __shared__::SCVars.SC_CURRENT_PROCESS_TYPE + \"]\");\n")
    file.write("        default;\n")
    file.write("    }\n")
    file.write("    SelectorRule If_BENCHTOP(YES, NO)\n")
    file.write("    {\n")
    file.write("        YES => __shared__::SCVars.SC_BENCHTOP == 1;\n")
    file.write("        NO => __shared__::SCVars.SC_BENCHTOP == -1;\n")
    file.write("    }\n")
    file.write("    SelectorRule If_HVM_FULL(HVM, FULL, default)\n")
    file.write("    {\n")
    file.write("        HVM => __shared__::TIU.Type == \"HVM\";\n")
    file.write("        FULL => __shared__::TIU.Type == \"FULL\";\n")
    file.write("        default;\n")
    file.write("    }\n")

    # Add dynamic hardware configuration selector (base names only)
    base_hw_keys = []
    seen = set()
    for k in HW_CONFIGS.keys():
        base = k.replace('_HVM', '').replace('_FC', '')
        if base not in seen:
            base_hw_keys.append(base)
            seen.add(base)
    base_hw_keys.append("default")
    SELECTOR_ARGS = ", ".join(base_hw_keys)
    file.write(f"    SelectorRule If_HW_CONFIG({SELECTOR_ARGS})\n")
    file.write("    {\n")
    for key in base_hw_keys:
        if key != "default":
            if key == "DS28C":
                file.write(f"        {key} => __shared__::GlobalBomGroupName.ActiveBomGroup == \"CLASS_DNL_S28C\";\n")
            else:
                file.write(f"        {key} => __shared__::GlobalBomGroupName.ActiveBomGroup == \"CLASS_NVL_{key}\";\n")
        else:
            file.write(f"        default;\n")
    file.write("    }\n")
    file.write("}\n\n")

def write_bom_selector_usrv(file, df, module_name, source_column, block_name, symbol_prefix, value_type,
                            selector_order=("S28C", "S52C", "S16C", "DS28C", "default")):
    # row_symbol_map: (LevelsName, Pin) -> symbol name
    # Used later by write_level_sequence to decide when to emit MODULE::<block_name>.<symbol>
    row_symbol_map = {}
    global SELECTOR_ARGS
    # pin_config_map: (scope, pin) -> (ordered_values_tuple, symbol_name)
    # Used to avoid duplicate writes and detect conflicting definitions per pin
    pin_config_map = {}

    # preserve first-seen pin order so output is deterministic/readable
    pin_order = []
    selector_order = SELECTOR_ARGS.split(",")
    selector_order_new = selector_order.copy()
    x = 0
    for i in selector_order:
        selector_order_new[x]=i.strip()
        x=x+1
    selector_order = selector_order_new
    for row_index, row in df.iterrows():
        raw_value = row.get(source_column, None)
        if pd.isna(raw_value):
            continue

        raw_text = str(raw_value).strip()

        # Skip empty and VM rows
        if raw_text == "" or raw_text == "VM":
            continue

        # Only process BOM-style multi-value entries, e.g. "0.001A, S52C=0.002A"
        # Single-value rows keep normal level behavior and do not get selector symbols.
        if "," not in raw_text or "=" not in raw_text:
            continue

        parts = [p.strip() for p in raw_text.split(",") if p.strip()]
        if not parts:
            continue

        # First token is base/default current for all selector keys
        base_value = parts[0].replace(" ", "")
        values = {key: base_value for key in selector_order}

        # Parse overrides like KEY=VALUE
        for token in parts[1:]:
            if "=" not in token:
                raise ValueError(f"Malformed {source_column} override '{token}' at CSV row {row_index + 2}")

            key, value = token.split("=", 1)
            key = key.strip()
            value = value.strip().replace(" ", "")

            # KEY must exist in selector order
            if key not in values:
                raise ValueError(
                    f"Unknown {source_column} selector key '{key}' at CSV row {row_index + 2}. "
                    f"Allowed: {', '.join(selector_order)}"
                )

            values[key] = value

        # Build ordered argument list for If_HW_CONFIG in exact selector order
        ordered_values = tuple(values[key] for key in selector_order)

        pin_name = str(row["Pin"]).strip()
        levels_name = str(row["LevelsName"]).strip().lower()
        if "upper" in levels_name:
            scope = "UPPER"
        elif "lower" in levels_name:
            scope = "LOWER"
        else:
            scope = "GEN"
        if contains_number(levels_name):
            scope = scope + "_" + str(re.search(r'\d+', levels_name).group())


        # Sanitize pin text for valid symbol usage
        pin_name_sanitized = re.sub(r"[^A-Za-z0-9_]", "_", pin_name)

        # Example: IFORCE_UPPER_PCD_PCIE5_00_RXN
        symbol_name = f"{symbol_prefix}_{scope}_{pin_name_sanitized}"

        # Ensure one pin has one consistent multi-value IFORCE definition
        pin_key = (scope, pin_name)
        if pin_key in pin_config_map:
            prev_values, prev_symbol = pin_config_map[pin_key]
            if prev_values != ordered_values or prev_symbol != symbol_name:
                raise ValueError(
                    f"Pin '{pin_name}' ({scope}) has conflicting multi-value {source_column} definitions in CSV. "
                    f"Please use one multi-value {source_column} definition per pin."
                )
        else:
            pin_config_map[pin_key] = (ordered_values, symbol_name)
            pin_order.append(pin_key)

        # Map this specific row so .lvl can reference symbol
        row_symbol_map[(row["LevelsName"], row["Pin"])] = symbol_name

    # Emit selector block only if at least one multi-value entry exists
    if pin_order:
        file.write(f"UserVars {block_name}\n\n{{\n")
        for pin_key in pin_order:
            ordered_values, symbol_name = pin_config_map[pin_key]
            args = ", ".join(ordered_values)
            file.write(f"\t{value_type} {symbol_name} = {module_name}_Rules.If_HW_CONFIG({args});\n")
        file.write("}\n\n")

    return row_symbol_map

def write_usrvar_file(shops_infile, output_filename):
    # We intentionally write to module-level map so write_level_sequence can reuse it
    global IFORCE_SYMBOL_MAP
    global VCLAMPHI_SYMBOL_MAP
    global VCLAMPLO_SYMBOL_MAP
    # Read the CSV file into a DataFrame
    df = pd.read_csv(shops_infile, quotechar='"', skipinitialspace=True)

    # Open the output file for writing
    with open(output_filename, "w") as file:
        # Write header
        write_header(file)

        # Write TOS rules
        write_tos_rules(file)

        # Write UserVars section for pin groups
        write_pingroups(file, df)

        # Write limits for each configuration
        write_limits(file, df)
        # Write BOM-driven selector uservars for multi-value rows
        # and store per-row symbol mapping for .lvl generation
        IFORCE_SYMBOL_MAP = write_bom_selector_usrv(file, df, MODULE_NAME, "iForce", "IFORCE", "IFORCE", "Current")
        VCLAMPHI_SYMBOL_MAP = write_bom_selector_usrv(file, df, MODULE_NAME, "VClampHi", "VCLAMPHI", "VCLAMPHI", "Voltage")
        VCLAMPLO_SYMBOL_MAP = write_bom_selector_usrv(file, df, MODULE_NAME, "VClampLo", "VCLAMPLO", "VCLAMPLO", "Voltage")

        # Write MTPL UserVars
        write_mtpl_usrvars(file)

#########################
# Main
#########################
setup("SHOPS_Config.conf")
write_usrvar_file(INPUTFILENAME, f"{MODULE_NAME}.usrv")
write_level_sequence(INPUTFILENAME, "LevelsSequences_SHOPS.lvl")
if CLAMP_VIOLATIONS != {}:
    print("ERROR ERROR ERROR ERROR!")
    os.remove(f"{MODULE_NAME}.usrv")
    os.remove(f"LevelsSequences_SHOPS.lvl")
    print("The Following Clamp violations need to be resolved!!!")
    for n in CLAMP_VIOLATIONS:
        print(f"{n} => {CLAMP_VIOLATIONS[n]}")
    input("Press Enter to exit...")