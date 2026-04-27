from mod.tpswitch import TPSwitch2, TPSwitch
from gadget.shell import LAUNCH_CWD
import os
import shutil

POR_TP = ['CLASS_AHMTFC_POR']         # The list of new POR_TP folder

# needed for one-click-build, only one torch_exe_version.txt is allowed
# obj = TPSwitch2('POR_TP/Class_*/InputFiles/torch_exe_version.txt')
# obj.delete()

inputbom = TPSwitch.tpobj[0].get_bomfolder()   
obj = TPSwitch2(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPH_FLOWS.mtpl')   
obj.overwrite_with(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPH_FLOWS_{inputbom.upper()}.mtpl')
obj = TPSwitch2(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPC_FLOWS.mtpl')   
obj.overwrite_with(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPC_FLOWS_{inputbom.upper()}.mtpl')
obj = TPSwitch2(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPP_FLOWS.mtpl')   
obj.overwrite_with(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPP_FLOWS_{inputbom.upper()}.mtpl')
obj = TPSwitch2(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPG_FLOWS.mtpl')   
obj.overwrite_with(f'POR_TP/{inputbom}/ProgramFlowsTestPlan/IPG_FLOWS_{inputbom.upper()}.mtpl')

obj = TPSwitch2('POR_TP/{INPUTBOM}/SubTestPlan.stpl')
obj.search_replace('CLK_ISCLK_PXH/CLK_ISCLK_PXH.mtpl', 'CLK_ISCLKAHMT_PXH/CLK_ISCLK_PXH.mtpl')
obj.search_replace('PTH_LDO_PXH/PTH_LDO_PXH.mtpl', 'PTH_LDOAHMT_PXH/PTH_LDO_PXH.mtpl')
obj.search_replace('SIO_TFR_PXH/SIO_TFR_PXH.mtpl', 'SIO_TFRAHMT_PXH/SIO_TFR_PXH.mtpl')
obj.search_replace('SIO_LEAKAGE_PXH/SIO_LEAKAGE_PXH.mtpl', 'SIO_LEAKAGEAHMT_PXH/SIO_LEAKAGE_PXH.mtpl')
obj.search_replace('SIO_CSI_PXH/SIO_CSI_PXH.mtpl', 'SIO_CSIAHMT_PXH/SIO_CSI_PXH.mtpl')
obj.search_replace('MIO_BSCAN_HXX/MIO_BSCAN_HXX.mtpl', 'MIO_BSCANAHMTFC_HXX/MIO_BSCAN_HXX.mtpl')
obj.write()

#obj = TPSwitch2('BaseInputs/Common/Common_Files/common.usrv')
#obj.search_replace('String Type        = "";', 'String Type        = "FULL";')
#obj.write()

# copy the AHMT modules since they dont exist in output folder
TPSwitch2(f'Modules/PCDH/CLK_ISCLKAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/CLK_ISCLKAHMT_PXH')
TPSwitch2(f'Modules/PCDH/PTH_LDOAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/PTH_LDOAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_TFRAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_TFRAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_LEAKAGEAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_LEAKAGEAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_CSIAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_CSIAHMT_PXH')
TPSwitch2(f'Modules/MIO_BSCAN/MIO_BSCANAHMTFC_HXX').copy_dir(f'{LAUNCH_CWD}/../../../nvl.hub/Modules/MIO_BSCAN/MIO_BSCANAHMTFC_HXX')


# Set the MV setting
os.environ['IN1'] = 'HX_AHMT_FC'           # this is the AHMT.json
