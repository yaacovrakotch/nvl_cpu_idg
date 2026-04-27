from mod.tpswitch import TPSwitch2, TPSwitch
from gadget.shell import LAUNCH_CWD
import os
import shutil

POR_TP = ['CLASS_AHMT_POR']         # The list of new POR_TP folder

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
obj.search_replace('MIO_MIO_BSCAN_HXX/MIO_BSCAN_HXX.mtpl', 'MIO_BSCANAHMTFC_HXX/MIO_BSCAN_HXX.mtpl')
obj.search_replace('PTH_LDO_PXH/PTH_LDO_PXH.mtpl', 'PTH_LDOAHMT_PXH/PTH_LDO_PXH.mtpl')
obj.search_replace('SIO_TFR_PXH/SIO_TFR_PXH.mtpl', 'SIO_TFRAHMT_PXH/SIO_TFR_PXH.mtpl')
obj.search_replace('SIO_LEAKAGE_PXH/SIO_LEAKAGE_PXH.mtpl', 'SIO_LEAKAGEAHMT_PXH/SIO_LEAKAGE_PXH.mtpl')
obj.search_replace('SIO_CSI_PXH/SIO_CSI_PXH.mtpl', 'SIO_CSIAHMT_PXH/SIO_CSI_PXH.mtpl')
obj.search_replace('SIO_PCIE5_PCH/SIO_PCIE5_PCH.mtpl', 'SIO_PCIE5AHMT_PCH/SIO_PCIE5_PCH.mtpl')
obj.search_replace('SIO_TCSSDP_PCH/SIO_TCSSDP_PCH.mtpl', 'SIO_TCSSDPAHMT_PCH/SIO_TCSSDP_PCH.mtpl')
obj.search_replace('SIO_BGREF_PXH/SIO_BGREF_PXH.mtpl', 'SIO_BGREFAHMT_PXH/SIO_BGREF_PXH.mtpl')
obj.search_replace('SIO_CNVISTEP_PXH/SIO_CNVISTEP_PXH.mtpl', 'SIO_CNVISTEPAHMT_PXH/SIO_CNVISTEP_PXH.mtpl')
obj.search_replace('SIO_EUSB2_PXH/SIO_EUSB2_PXH.mtpl', 'SIO_EUSB2AHMT_PXH/SIO_EUSB2_PXH.mtpl')
obj.search_replace('SIO_PCIE4GBE_PXH/SIO_PCIE4GBE_PXH.mtpl', 'SIO_PCIE4GBEAHMT_PXH/SIO_PCIE4GBE_PXH.mtpl')
obj.search_replace('SIO_USB3_PXH/SIO_USB3_PXH.mtpl', 'SIO_USB3AHMT_PXH/SIO_USB3_PXH.mtpl')
obj.search_replace('SIO_UFS_PXH/SIO_UFS_PXH.mtpl', 'SIO_UFSAHMT_PXH/SIO_UFS_PXH.mtpl')
obj.write()

#obj = TPSwitch2('POR_TP/{INPUTBOM}/EnvironmentFile.env')
#obj.search_replace('"$MHDRV_PATMODIFY_PATH/merged_allplist_PatConfigSetpoints.json;" +', '"$MHDRV_PATMODIFY_PATH/merged_allplist_PatConfigSetpoints.json;" +\n "~HDMT_TP_BASE_DIR/Modules/MIO_DDR/MIO_DDR5ACAHMT_HXNVL/InputFiles/mio.nvlhub.reset.patmod.json;" +\n')
#obj.write()

# copy the AHMT modules since they dont exist in output folder
#TPSwitch2(f'Modules/MIO_DDR/MIO_DDR5ACAHMT_HXNVL').copy_dir(f'{LAUNCH_CWD}/../../../nvl.hub/Modules/MIO_DDR/MIO_DDR5ACAHMT_HXNVL')
#TPSwitch2(f'Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL').copy_dir(f'{LAUNCH_CWD}/../../../nvl.hub/Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL')
TPSwitch2(f'Modules/MIO_BSCAN/MIO_BSCANAHMTFC_HXX').copy_dir(f'{LAUNCH_CWD}/../../../nvl.hub/Modules/MIO_BSCAN/MIO_BSCANAHMTFC_HXX')
TPSwitch2(f'Modules/PCDH/PTH_LDOAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/PTH_LDOAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_TFRAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_TFRAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_LEAKAGEAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_LEAKAGEAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_CSIAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_CSIAHMT_PXH')
TPSwitch2(f'Modules/SIO/SIO_PCIE5AHMT_PCH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/SIO/SIO_PCIE5AHMT_PCH')
TPSwitch2(f'Modules/PCDH/SIO_BGREFAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_BGREFAHMT_PXH')
TPSwitch2(f'Modules/SIO/SIO_TCSSDPAHMT_PCH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/SIO/SIO_TCSSDPAHMT_PCH')
TPSwitch2(f'Modules/PCDH/SIO_CNVISTEPAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_CNVISTEPAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_EUSB2AHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_EUSB2AHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_PCIE4GBEAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_PCIE4GBEAHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_USB3AHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_USB3AHMT_PXH')
TPSwitch2(f'Modules/PCDH/SIO_UFSAHMT_PXH').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCDH/SIO_UFSAHMT_PXH')

# Set the MV setting
os.environ['IN1'] = 'H16_AHMT'           # this is the AHMT.json
