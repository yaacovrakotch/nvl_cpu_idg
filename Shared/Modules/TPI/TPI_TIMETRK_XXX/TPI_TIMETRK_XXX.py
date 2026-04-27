# CPU IP TPI Flow Flag Module pymtpl source code.
# Output for prime13 and TOS4.
import sys
import glob
import os
import csv
import shutil
from pymtpl.por_methods import AuxiliaryTC, TimeTracker
from gadget.strmore import sha1
from gadget.errors import confirm
from importlib.machinery import SourceFileLoader
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow

def read_programflows():
    """Returns the list of subflw_list"""
    # Check that all the dielets are cloned in the right area
    original_sys_path = sys.path.copy()
    # print(os.getcwd())
    dielet_py_path = '../../../../POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/'
    dielet_py_list = [f'{dielet_py_path}ProgramFlowsCPU.py',
                      f'{dielet_py_path}ProgramFlowsGCD.py',
                      f'{dielet_py_path}ProgramFlowsHUB.py',
                      f'{dielet_py_path}ProgramFlowsPCD.py']
    for dieletpy in dielet_py_list:
        confirm(os.path.exists(dieletpy),
                f'{dieletpy} is not found in expecting path. ',
                'Please manual download and copy the file from its repo.')

    # Read subflow names from main programflow source code.
    subflw_list = []
    sys.path.append('../../../../POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan')
    for py in glob.glob('../../../POR_TP/*/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py'):      # this is the official location of the shared programflows.py
        Initialize.written = None         # Do not write
        pymodule = SourceFileLoader(sha1(py), py).load_module()
        main_code = getattr(pymodule, 'MAIN_code')
        for line in main_code.split('\n'):
            if line.strip():              # ignore empty lines
                res1 = line.split()[0]    # first element
                res2 = line.split()[1]    # second element
                if res2.startswith('TPI_FLWFLGS'):
                    subflw_list.append(res1.replace('_SubFlow', '').replace('_TopFlow', ''))
        return subflw_list
################### Start of pymtpl ###################

module_name = 'TPI_TIMETRK_XXX'

# Define the counter
TIMESTART = 93740000
TIMESTOP = 93740001

# subfolder = 'InputFiles'
# FlwflgMap = os.path.join(subfolder, 'Flwflg_Logic_Map.csv')
# FlwflgMap_Orig = os.path.join(subfolder, 'Flwflg_Logic_Map_orig.csv')

# 1. Read programflow pymtpl
subflw_list = read_programflows()

# 2. Check if .csv does not exist, if so create it and exit
# is_new_csv(FlwflgMap, subflw_list)

# 3. Check if .csv needs update
# is_csv_need_update(FlwflgMap, FlwflgMap_Orig, subflw_list)

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass(module_name,  module_name,tosversion="tos4", binrange = (9374, 9374),
                    defaultrm2bin=(99939000, 99939999),
                   defaultrm1bin=(98939000, 98939999))

# Read recent update CSV file.
# with open(FlwflgMap, 'r', newline ='') as file:
#     read_rows = list(csv.reader(file))

# PARALLEL SUBFLOWS THAT REQUIRE TIMETRACKER
ttsf = """STARTPRL0CPU STARTPRL1CPU STARTPRL2CPU STARTPRL3CPU STARTPRL4CPU HVBIPRL0CPU BEGINPRL0CPU BEGINPRL1CPU 
BEGINPRL2CPU SPEEDPRL0CPU SPEEDPRL1CPU SPEEDPRL2CPU SPEEDPRL3CPU SPEEDPRL4CPU SPEEDPRL5CPU ENDPRL0CPU ENDPRL1CPU 
ENDPRL2CPU ENDPRL3CPU ENDPRL4CPU LTTCPRL0CPU LTTCPRL1CPU FACTPRL0CPU FACTPRL1CPU STARTPRL0GCD STARTPRL1GCD STARTPRL2GCD 
STARTPRL3GCD STARTPRL4GCD HVBIPRL0GCD BEGINPRL0GCD BEGINPRL1GCD BEGINPRL2GCD SPEEDPRL0GCD SPEEDPRL1GCD SPEEDPRL2GCD 
SPEEDPRL3GCD SPEEDPRL4GCD SPEEDPRL5GCD ENDPRL0GCD ENDPRL1GCD ENDPRL2GCD ENDPRL3GCD ENDPRL4GCD LTTCPRL0GCD LTTCPRL1GCD 
FACTPRL0GCD FACTPRL1GCD STARTPRL0PCD STARTPRL1PCD STARTPRL2PCD STARTPRL3PCD STARTPRL4PCD HVBIPRL0PCD BEGINPRL0PCD 
BEGINPRL1PCD BEGINPRL2PCD SPEEDPRL0PCD SPEEDPRL1PCD SPEEDPRL2PCD SPEEDPRL3PCD SPEEDPRL4PCD SPEEDPRL5PCD ENDPRL0PCD 
ENDPRL1PCD ENDPRL2PCD ENDPRL3PCD ENDPRL4PCD LTTCPRL0PCD LTTCPRL1PCD FACTPRL0PCD FACTPRL1PCD STARTPRL0HUB STARTPRL1HUB 
STARTPRL2HUB STARTPRL3HUB STARTPRL4HUB HVBIPRL0HUB BEGINPRL0HUB BEGINPRL1HUB BEGINPRL2HUB SPEEDPRL0HUB SPEEDPRL1HUB 
SPEEDPRL2HUB SPEEDPRL3HUB SPEEDPRL4HUB SPEEDPRL5HUB ENDPRL0HUB ENDPRL1HUB ENDPRL2HUB ENDPRL3HUB ENDPRL4HUB LTTCPRL0HUB 
LTTCPRL1HUB FACTPRL0HUB FACTPRL1HUB""".split()

# Define Test Instance and Flowitems and start the loop
there = []
print("#####", subflw_list)
for subflw in subflw_list:
    # if subflw in ttsf:
    if 'PRL' not in subflw:
        if subflw in there:
            continue
        else:
            there.append(subflw)

        FIRST = TimeTracker(
            name=f"CTRL_X_TIMETRACK_K_{subflw}_X_X_X_X_TIMERSTART",
            TestMode="START",
            Argument=f'{subflw}',
            _fitem = Fitem('SAME', r0=pFail(setbin=AUTO, ret = 0, ctr=TIMESTART))
        )
        TIMESTART = TIMESTART + 2
        LAST = TimeTracker(
            name=f"CTRL_X_TIMETRACK_K_{subflw}_X_X_X_X_TIMERSTOP",
            TestMode="STOP",
            Argument=f'{subflw}',
            _fitem = Fitem('SAME', r0=pFail(setbin=AUTO, ret = 0, ctr=TIMESTOP))
        )
        TIMESTOP = TIMESTOP + 2
    else:
        continue

        # Define above tests in subflows
    Flow(f'TPI_TIMETRK_XXX_FIRST_{subflw}',  FIRST)
    Flow(f'TPI_TIMETRK_XXX_LAST_{subflw}',  LAST)

# Delete additional files since it does not belong in TPI_FLWFLGS
item_removal = [
    'IPC_FLOWS.mtpl',
    'IPC_FLOWS.flw']

for item in item_removal:
    try:
        os.remove(item)
    except Exception:
        print('Failed additional file removal')