from mod.tpswitch import TPSwitch2
from gadget.shell import LAUNCH_CWD
import os
import shutil
from mod.tpswitch import TPSwitch2, TPSwitch

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
obj.search_replace('MIO_BSCAN_HXX/MIO_BSCAN_HXX.mtpl', 'MIO_BSCANAHMTFC_HXX/MIO_BSCAN_HXX.mtpl')
obj.search_replace('CLK_ISCLK_PXS/CLK_ISCLK_PXS.mtpl', 'CLK_ISCLKAHMT_PXS/CLK_ISCLK_PXS.mtpl')
obj.search_replace('PTH_LDO_PXX/PTH_LDO_PXX.mtpl', 'PTH_LDOAHMT_PXX/PTH_LDO_PXX.mtpl')
obj.search_replace('SIO_LEAKAGE_PXS/SIO_LEAKAGE_PXS.mtpl', 'SIO_LEAKAGEAHMT_PXS/SIO_LEAKAGE_PXS.mtpl')
obj.search_replace('SIO_TFR_PXX/SIO_TFR_PXX.mtpl', 'SIO_TFRAHMT_PXX/SIO_TFR_PXX.mtpl')
obj.write()

#obj = TPSwitch2('BaseInputs/Common/Common_Files/common.usrv')
#obj.search_replace('String Type        = "";', 'String Type        = "FULL";')
#obj.write()

# copy the AHMT modules since they dont exist in output folder
TPSwitch2(f'Modules/MIO_BSCAN/MIO_BSCANAHMTFC_HXX').copy_dir(f'{LAUNCH_CWD}/../../../nvl.hub/Modules/MIO_BSCAN/MIO_BSCANAHMTFC_HXX')
TPSwitch2(f'Modules/PCD/CLK_ISCLKAHMT_PXS').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/CLK_ISCLKAHMT_PXS')
TPSwitch2(f'Modules/PCD/PTH_LDOAHMT_PXX').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/PTH_LDOAHMT_PXX')
TPSwitch2(f'Modules/PCD/SIO_LEAKAGEAHMT_PXS').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/SIO_LEAKAGEAHMT_PXS')
TPSwitch2(f'Modules/PCD/SIO_TFRAHMT_PXX').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/SIO_TFRAHMT_PXX')


# Set the MV setting
os.environ['IN1'] = 'AHMT_FC'           # this is the AHMT_FC.json
