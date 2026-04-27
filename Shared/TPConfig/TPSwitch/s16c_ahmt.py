from mod.tpswitch import TPSwitch2
from gadget.shell import LAUNCH_CWD
import os
import shutil
from mod.tpswitch import TPSwitch2, TPSwitch

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
obj.search_replace('MIO_DDR5AC_HXNVL/MIO_DDR5AC_HXNVL.mtpl', 'MIO_DDR5ACAHMT_HXNVL/MIO_DDR5AC_HXNVL.mtpl')
obj.search_replace('MIO_DDR5DC_HXNVL/MIO_DDR5DC_HXNVL.mtpl', 'MIO_DDR5DCAHMT_HXNVL/MIO_DDR5DC_HXNVL.mtpl')
obj.search_replace('CLK_ISCLK_PXS/CLK_ISCLK_PXS.mtpl', 'CLK_ISCLKAHMT_PXS/CLK_ISCLK_PXS.mtpl')
obj.search_replace('PTH_LDO_PXX/PTH_LDO_PXX.mtpl', 'PTH_LDOAHMT_PXX/PTH_LDO_PXX.mtpl')
obj.search_replace('SIO_LEAKAGE_PXS/SIO_LEAKAGE_PXS.mtpl', 'SIO_LEAKAGEAHMT_PXS/SIO_LEAKAGE_PXS.mtpl')
obj.search_replace('SIO_TFR_PXX/SIO_TFR_PXX.mtpl', 'SIO_TFRAHMT_PXX/SIO_TFR_PXX.mtpl')
obj.search_replace('SIO_DMI5_PXS/SIO_DMI5_PXS.mtpl', 'SIO_DMI5AHMT_PXS/SIO_DMI5_PXS.mtpl')
obj.search_replace('SIO_PCIE5_PCS/SIO_PCIE5_PCS.mtpl', 'SIO_PCIE5AHMT_PCS/SIO_PCIE5_PCS.mtpl')
obj.search_replace('SIO_TCSSDP_PCS/SIO_TCSSDP_PCS.mtpl', 'SIO_TCSSDPAHMT_PCS/SIO_TCSSDP_PCS.mtpl')
obj.write()

obj = TPSwitch2('POR_TP/{INPUTBOM}/EnvironmentFile.env')
obj.search_replace('"$MHDRV_PATMODIFY_PATH/merged_allplist_PatConfigSetpoints.json;" +', '"$MHDRV_PATMODIFY_PATH/merged_allplist_PatConfigSetpoints.json;" +\n "~HDMT_TP_BASE_DIR/Modules/MIO_DDR/MIO_DDR5ACAHMT_HXNVL/InputFiles/mio.nvlhub.reset.patmod.json;" +\n')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p10', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p18')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p9/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p17/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p8/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p16/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p7/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p15/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p6/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p14/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p5/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p13/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p4/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p12/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p3/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p11/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p2/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p10/pat/indv_bin')
obj.search_replace('I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p1/pat/indv_bin', 'I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p9/pat/indv_bin')
obj.search_replace('"I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.1/p0/pat/indv_bin;" +', '"I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p8/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p7/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p6/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p5/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p4/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p3/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p2/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p1/pat/indv_bin;" +\n "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p0/pat/indv_bin;" +\n')


obj.write()

# copy the AHMT modules since they dont exist in output folder
TPSwitch2(f'Modules/MIO_DDR/MIO_DDR5ACAHMT_HXNVL').copy_dir(f'{LAUNCH_CWD}/../../../nvl.hub/Modules/MIO_DDR/MIO_DDR5ACAHMT_HXNVL')
TPSwitch2(f'Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL').copy_dir(f'{LAUNCH_CWD}/../../../nvl.hub/Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL')
TPSwitch2(f'Modules/PCD/CLK_ISCLKAHMT_PXS').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/CLK_ISCLKAHMT_PXS')
TPSwitch2(f'Modules/PCD/PTH_LDOAHMT_PXX').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/PTH_LDOAHMT_PXX')
TPSwitch2(f'Modules/PCD/SIO_DMI5AHMT_PXS').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/SIO_DMI5AHMT_PXS')
TPSwitch2(f'Modules/PCD/SIO_LEAKAGEAHMT_PXS').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/SIO_LEAKAGEAHMT_PXS')
TPSwitch2(f'Modules/PCD/SIO_TFRAHMT_PXX').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/PCD/SIO_TFRAHMT_PXX')
TPSwitch2(f'Modules/SIO/SIO_PCIE5AHMT_PCS').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/SIO/SIO_PCIE5AHMT_PCS')
TPSwitch2(f'Modules/SIO/SIO_TCSSDPAHMT_PCS').copy_dir(f'{LAUNCH_CWD}/../../../nvl.pcd/Modules/SIO/SIO_TCSSDPAHMT_PCS')

# Set the MV setting
os.environ['IN1'] = 'S16C_AHMT'           # this is the AHMT.json
