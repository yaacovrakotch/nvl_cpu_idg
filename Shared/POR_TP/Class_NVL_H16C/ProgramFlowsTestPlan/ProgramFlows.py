import sys
import os
sys.path.append('../../../Shared/POR_TP/Class_NVL_H16C/ProgramFlowsTestPlan')
from ProgramFlowsSharedPKG import MAIN_code, INIT_code
from pymtpl.core import Initialize, ConCurrentFlow, Flow, FlowDefs, ModuleFlow, pFail, Fitem
from pymtpl.helpers import ProgramFlows, NVLProgramFlows


Initialize('ProgramFlows', 'Flows', tosversion="tos4")

# <parallel_name>: <name_with_IP_in_it>
prl_dict = {
            'STARTPRL0_SubFlow': 'STARTPRL0%s_SubFlow',
            'STARTPRL1_SubFlow': 'STARTPRL1%s_SubFlow',
            'STARTPRL2_SubFlow': 'STARTPRL2%s_SubFlow',
            'STARTPRL3_SubFlow': 'STARTPRL3%s_SubFlow',
            'STARTPRL4_SubFlow': 'STARTPRL4%s_SubFlow',
            'HVBIPRL0_SubFlow': 'HVBIPRL0%s_SubFlow',
            'BEGINPRL0_SubFlow': 'BEGINPRL0%s_SubFlow',
            'BEGINPRL1_SubFlow': 'BEGINPRL1%s_SubFlow',
            'BEGINPRL2_SubFlow': 'BEGINPRL2%s_SubFlow',
            'SPEEDPRL0_SubFlow': 'SPEEDPRL0%s_SubFlow',
            'SPEEDPRL1_SubFlow': 'SPEEDPRL1%s_SubFlow',
            'SPEEDPRL2_SubFlow': 'SPEEDPRL2%s_SubFlow',
            'SPEEDPRL3_SubFlow': 'SPEEDPRL3%s_SubFlow',
            'SPEEDPRL4_SubFlow': 'SPEEDPRL4%s_SubFlow',
            'SPEEDPRL5_SubFlow': 'SPEEDPRL5%s_SubFlow',
            'ENDPRL0_SubFlow': 'ENDPRL0%s_SubFlow',
            'ENDPRL1_SubFlow': 'ENDPRL1%s_SubFlow',
            'ENDPRL2_SubFlow': 'ENDPRL2%s_SubFlow',
            'ENDPRL3_SubFlow': 'ENDPRL3%s_SubFlow',
            'ENDPRL4_SubFlow': 'ENDPRL4%s_SubFlow',
            'LTTCPRL0_SubFlow': 'LTTCPRL0%s_SubFlow',
            'LTTCPRL1_SubFlow': 'LTTCPRL1%s_SubFlow',
            'FACTPRL0_SubFlow': 'FACTPRL0%s_SubFlow',
            'FACTPRL1_SubFlow': 'FACTPRL1%s_SubFlow'}

# Fail port connection for each die let.
fail_port_dict = {'CPU': {'r20': pFail(ret=20)},
                  'GCD': {'r30': pFail(ret=30)},
                  'HUB': {'r40': pFail(ret=40)},
                  'PCD': {'r50': pFail(ret=50)}}

# Get die combination option from user input during building. Full/CPU/GCD/HUB/PCD
die_list_input = os.environ.get('DIE_LIST', 'CPU,GCD,HUB,PCD')      # comma separated, eg. CPU,GCD or CPU
die_combo = die_list_input.split(',')

# Write the ConCurrentFlow blocks 
for item in sorted(prl_dict.keys()):

    if len(die_combo) > 1:
        ConCurrentFlow(f'{item}', **NVLProgramFlows.get_flow_params(die_combo, prl_dict[item]))

    else:
        subf_res = NVLProgramFlows.get_subflow_name(die_combo, prl_dict[item])
        mod_res = NVLProgramFlows.get_module_flow_name(die_combo, prl_dict[item])
        Flow(f'{item}', [
        Fitem(f'{subf_res}', ModuleFlow(f'{mod_res}'),
              rm2=pFail(ret=-2), rm1=pFail(ret=-1), **fail_port_dict[die_combo[0]])
        ])

# Code to strip out nondielet lines in MAIN_code
final_MAIN_code = NVLProgramFlows.strip_dielets(MAIN_code, die_combo)
ProgramFlows().main(final_MAIN_code, 'MAIN')

# Code to strip out nondielet lines in INIT_code
strip_INIT_code = NVLProgramFlows.strip_dielets(INIT_code, die_combo)

# Code to strip out empty composite lines in INIT_code
final_INIT_code = NVLProgramFlows.ignore_emptycomp(strip_INIT_code, die_combo)
ProgramFlows().main(final_INIT_code, 'INIT')
 
LOTSTARTFLOW_code = '''

LOTSTARTFLOW   TPI_BASE_XXX::TPI_BASE_XXX_LOTSTARTFLOW rm2fm2 rm1fm1 r0f0
LOTSTARTFLOW   PTH_DIODE_XXX::PTH_DIODE_XXX_LOTSTARTFLOW rm2fm2 rm1fm1 r0f0

'''
ProgramFlows().main(LOTSTARTFLOW_code, 'LOTSTARTFLOW')

LOTENDFLOW_code = '''

LOTENDFLOW   TPI_BASE_XXX::TPI_BASE_XXX_LOTENDFLOW          rm2fm2 rm1fm1 r0f0
LOTENDFLOW   PTH_DIODE_XXX::PTH_DIODE_XXX_LOTENDFLOW          rm2fm2 rm1fm1 r0f0

'''
ProgramFlows().main(LOTENDFLOW_code, 'LOTENDFLOW')

TESTPLANSTARTFLOW_code = '''

TESTPLANSTARTFLOW   TPI_BASE_XXX::TPI_BASE_XXX_TESTPLANSTARTFLOW          rm2fm2 rm1fm1 r0f0
TESTPLANSTARTFLOW   PTH_DIODE_XXX::PTH_DIODE_XXX_TESTPLANSTARTFLOW          rm2fm2 rm1fm1 r0f0

'''
ProgramFlows().main(TESTPLANSTARTFLOW_code, 'TESTPLANSTARTFLOW')

TESTPLANENDFLOW_code = '''

TESTPLANENDFLOW   TPI_BASE_XXX::TPI_BASE_XXX_TESTPLANENDFLOW          rm2fm2 rm1fm1 r0f0
TESTPLANENDFLOW   PTH_DIODE_XXX::PTH_DIODE_XXX_TESTPLANENDFLOW          rm2fm2 rm1fm1 r0f0
TESTPLANENDFLOW   TPI_END_XXX::TPI_END_XXX_TESTPLANENDFLOW            rm2fm2 rm1fm1 r0f0
'''
ProgramFlows().main(TESTPLANENDFLOW_code, 'TESTPLANENDFLOW')

# Write the final FlowDefs
FlowDefs(InitFlow='INIT',
         MainFlow='MAIN',
         LotStartFlow='LOTSTARTFLOW',
         LotEndFlow='LOTENDFLOW',
         TestPlanStartFlow='TESTPLANSTARTFLOW',
         TestPlanEndFlow='TESTPLANENDFLOW')
