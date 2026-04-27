from pymtpl.por_methods import PowerSequenceHandler
from pymtpl.core import Flow,  Fitem,  pFail,  InitializeNVLClass,  Spec

module_name = 'TPI_PWRCTRL_CXX'

InitializeNVLClass(module_name,  module_name,tosversion="tos4")

IPC_powersequencehandler = PowerSequenceHandler (
    name = f"CTRL_X_PWR_K_STARTCPUNOM_X_X_X_X_PWRUPTCIPCPU",
    ApplyPowerDown = "Always",
	ApplyPowerOn = "Always",
	PowerDownTc = "CPU_IP_BASE::Power_dwn_IPC_xxx_pwrd_zerzer",
	PowerOnTc = "CPU_IP_BASE::Power_Up_TC_IPC_nom",
     _fitem = Fitem('SAME', r0=pFail(setbin=90931100, ret = 0))
)

STARTCPUNOM = Flow(f'{module_name}_STARTCPUNOM',IPC_powersequencehandler)