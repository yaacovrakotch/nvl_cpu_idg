# PKG TPI Flow Flag Module pymtpl source code.
# Output for prime13 and TOS4.
from email.policy import default
import sys
import glob
import os
import csv
import shutil
from pymtpl.por_methods import AuxiliaryTC
from gadget.strmore import sha1
from gadget.errors import confirm
from importlib.machinery import SourceFileLoader
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  MultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow
from pymtpl.helpers import NVLProgramFlows


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


def is_new_csv(FlwflgMap, subflw_list):
    """Writing into a CSV file. Subflow only without values. One time work when blueprint create."""
    if not os.path.exists(FlwflgMap):
        with open(FlwflgMap, 'w', newline ='') as file:
            writer = csv.writer(file)
            for item in subflw_list:
                writer.writerow([item])
            print(f'{FlwflgMap} is created. Pls update this file with values before we can proceed')
            exit(1)


def is_csv_need_update(FlwflgMap, FlwflgMap_Orig, subflw_list):
    """update csv"""
    # When .csv exist, check if it needs update.
    shutil.copy(FlwflgMap, FlwflgMap_Orig)
    # Update the CSV file when blueprint updates. PDE needs to update value accordingly.
    with open(FlwflgMap, 'r', newline ='') as file:
        read_rows = list(csv.reader(file))

    # Locate cell A2 and clear column A. Update with new subflow names.
    if len(read_rows) > 1:
        for i in range(1, len(read_rows)):
            read_rows[i][0] = ''
        for i in range(1, min(len(read_rows), len(subflw_list) + 1)):
            read_rows[i][0] = subflw_list[i - 1]

    # Save back the update to Flwflg csv file
    with open(FlwflgMap, 'w', newline ='') as file:
        writer = csv.writer(file)
        writer.writerows(read_rows)

    # Routine to open csv files.
    def csv_to_diff(path):
        with open(path, newline='') as file:
            return set(tuple(row) for row in csv.reader(file))

    if csv_to_diff(FlwflgMap) != csv_to_diff(FlwflgMap_Orig):
        print('Flwflg logic map updated to match with recent Blueprints update. '
              'Please audit Flwflg logic map and perform needed updates.')
        exit(1)

    else:
        print('No change in Flwflg logic map. Continue for .mtpl generation.')


################### Start of pymtpl ###################
    
module_name = 'TPI_FLWFLGS_XXX'

# Define the counter
FLWSKPCTR = 44400000
FLWFLGCTR = 54400000

subfolder = 'InputFiles'
FlwflgMap = os.path.join(subfolder, 'Flwflg_Logic_Map.csv')
FlwflgMap_Orig = os.path.join(subfolder, 'Flwflg_Logic_Map_orig.csv')

# 1. Read programflow pymtpl
subflw_list = read_programflows()

# 2. Check if .csv does not exist, if so create it and exit
is_new_csv(FlwflgMap, subflw_list)

# 3. Check if .csv needs update
is_csv_need_update(FlwflgMap, FlwflgMap_Orig, subflw_list)

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass(module_name,  module_name,tosversion="tos4",  binrange = (9340, 9340),
                   defaultrm2bin = (99930000, 99931999),
                   defaultrm1bin=(98930000, 98931999))

# Read recent update CSV file.
with open(FlwflgMap, 'r', newline ='') as file:
    read_rows = list(csv.reader(file))
  
# Define Test Instance and Flowitems and start the loop but skip all PRL-flows
for subflw in subflw_list:
    if "PRL" in subflw and "PRE" not in subflw:
       continue
    for row in read_rows:
       if row and row[0] == subflw:
            output = []
            for cell in row[1:]:
                if cell == '':
                    break
                output.append(cell)
            convert_str = ','.join(output)
            #finish grab the BypassPort logic from csv map file.
            FLW_SKP = AuxiliaryTC(
                name = f"CTRL_X_AUX_K_{subflw}_X_X_X_X_FLWSKP", 
                DataType = "Integer", 
                Expression = "1", 
                ResultPort = "1", 
                BypassPort = Spec(f"__shared__::FlwSkpCollect.FlwSkpRule({convert_str})"),
                _fitem = Fitem('SAME',  r0=pFail(setbin=AUTO, ret = 0),  r2=pPass(ret = 2))
                )
                 # Once the test is defined,  uprev the counter
     
    # Set PreInstance based on subflw value
    if subflw in ["STARTCPUPATMODSPKG", "HVBICPUPKG", "BEGINCPUPKG", "ENDCPUPKG", "ENDCPUVMAXPKG", "LTTCCPUPKG", "CPUIPFF", "CPUPKGFF"]:
        pre_instance_value = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")'
        post_instance = Spec('__shared__::TpRule.If_CLASS_NVL_S52C("PrimeSetAdditionalCurrentDieIds("+__shared__::DFFVars.DIEID_CPU1+")","")')
    elif subflw in ["STARTGCDPATMODSPKG", "HVBIGCDPKG", "BEGINGCDPKG", "ENDGCDPKG", "ENDGCDVMAXPKG", "LTTCGCDPKG", "GCDIPFF", "GCDPKGFF"]:
        pre_instance_value = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_GPU+")'
        post_instance = None
    elif subflw in ["STARTHUBPATMODSPKG", "HVBIHUBPKG", "BEGINHUBPKG", "ENDHUBPKG", "ENDHUBVMAXPKG", "LTTCHUBPKG", "HUBIPFF", "HUBPKGFF"]:
        pre_instance_value = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_HUB+")'
        post_instance = None
    elif subflw in ["STARTPCDPATMODSPKG", "HVBIPCDPKG", "BEGINPCDPKG", "ENDPCDPKG", "ENDPCDVMAXPKG", "LTTCPCDPKG", "PCDIPFF", "PCDPKGFF"]:
        pre_instance_value = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_PCD+")'
    else:
        pre_instance_value = "SetCurrentDieId(PKG)"
        post_instance = None

    # Define next test instance in DUT flow
    FLW_FLG = AuxiliaryTC(
    name = f"CTRL_X_AUX_K_{subflw}_X_X_X_X_FLWFLG", 
    DataType = "Integer",     
    Expression = "1", 
    ResultPort = "1",
    PreInstance = pre_instance_value,
    PostInstance = post_instance,  
    _fitem = Fitem('SAME',  r0=pFail(setbin=AUTO, ret = 0))
    )
            
    # Define above tests in subflows
    Flow(f'TPI_FLWFLGS_XXX_{subflw}',  FLW_SKP,  FLW_FLG)
