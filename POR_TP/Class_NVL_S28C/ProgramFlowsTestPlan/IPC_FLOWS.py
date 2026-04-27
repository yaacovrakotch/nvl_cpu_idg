from pymtpl.core import Initialize
from pymtpl.helpers import ProgramFlows 
Initialize('IPC_FLOWS', 'IPC_FLOWS',tosversion="tos4")

ipc_stdports = 'rm2fm2 rm1fm1 r0f20'
ipc_stdports_S28_B0_PO = 'rm2fm2 rm1fm1 r0f20 r1p1'
ipcflwflgs_stdports = 'rm2fm2 rm1fm1 r0f20 r2p1'
ipcflwflgs_stdports_S28_B0_PO = 'rm2fm2 rm1fm1 r0f20 r1p1 r2p1'

# TODO : Currently skipping LTCC for S28C B0 PO
# To enable replace all _S28_B0_PO with the other standard versions of the ports
# So replace ipc_stdports_S28_B0_PO with ipc_stdports and ipcflwflgs_stdports_S28_B0_PO with ipcflwflgs_stdports
# Also replace pkg_stdports_S28_B0_PO with pkg_stdports in the ProgramFlowsCPU.py file to enable LTTC in the PKG subflows

MAIN_code = f'''
STARTCPUNOM_SubFlow       TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
STARTCPUNOM_SubFlow       FUS_FUSECFG_CXX      {ipc_stdports}
STARTCPUNOM_SubFlow       FUS_UNITINFO_CXX     {ipc_stdports}
STARTCPUNOM_SubFlow       FUS_FUSEREAD_CXX     {ipc_stdports}
STARTCPUNOM_SubFlow       TPI_PWRCTRL_CXX      rm2fm2 rm1fm1 r0f20 r2p1
STARTCPUNOM_SubFlow       IPC::DRV_RESET_CXX::DRV_BASIC_CXX_STARTCPUNOM        {ipc_stdports}
STARTCPUNOM_SubFlow       MIO_HPTP_CXPKGS7     {ipc_stdports}
STARTCPUNOM_SubFlow       IPC::DRV_RESET_CXX::DRV_RESET_CXX_STARTCPUNOM        {ipc_stdports}
STARTANA0CPU_SubFlow      TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
STARTANA0CPU_SubFlow      PTH_BGR_CXPKGS7      rm2fm2 rm1fm1 r0f20 r2p1
STARTANA0CPU_SubFlow      PTH_DTS_CX816      rm2fm2 rm1fm1 r0f20 r2p1
STARTANA1CPU_SubFlow      TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
STARTANA1CPU_SubFlow      CLK_BASE_CXXX        {ipc_stdports} 
STARTANA1CPU_SubFlow      PTH_DLVR_CXPKGS7     rm2fm2 rm1fm1 r0f20 r2p1
STARTPWRCPU_SubFlow       TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
STARTPWRCPU_SubFlow       PTH_BGR_CXPKGS7    rm2fm2 rm1fm1 r0f20 r2p1
STARTPWRCPU_SubFlow       PTH_POWER_CXPKGS7    rm2fm2 rm1fm1 r0f20 r2p1
STARTHPTPDRVCPU_SubFlow   TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}

HVBICPU_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}

BEGINCPU_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
BEGINCPU_SubFlow          TPI_DIERCVRY_CXX     {ipc_stdports}
BEGINCPU_SubFlow          CLK_MAIN_CXXX        {ipc_stdports}
BEGINCPU_SubFlow          SCN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPU_SubFlow          SCN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPU_SubFlow          SCN_UNCORE_CX816     rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPU_SubFlow          TPI_DAS_CXX          rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPUNOM_SubFlow       TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
BEGINCPUNOM_SubFlow       ARR_CORE_CXX       rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPUNOM_SubFlow       ARR_UNCORE_CXX      rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPUNOM_SubFlow       ARR_CCF_CXX        rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPUNOM_SubFlow      ARR_ATOM_CXX      rm2fm2 rm1fm1 r0f20 r2p1
BEGINCPUNOM_SubFlow       CLK_MAIN_CXXX        {ipc_stdports}
BEGINCPUMAX_SubFlow       TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
BEGINCPUMAX_SubFlow       CLK_MAIN_CXXX        {ipc_stdports}
               
F1XCCF_SubFlow            TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F1XCCF_SubFlow            ARR_CCF_CXX        rm2fm2 rm1fm1 r0f20 r2p1
F1XCCF_SubFlow            SCN_UNCORE_CX816     rm2fm2 rm1fm1 r0f20 r2p1
F1XCCF_SubFlow            FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
F1XAT_SubFlow             TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F1XAT_SubFlow             ARR_ATOM_CXX       rm2fm2 rm1fm1 r0f20 r2p1
F1XAT_SubFlow             SCN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F1XAT_SubFlow             FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F1XATCCF_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F1XATCCF_SubFlow          FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F1XCR_SubFlow             TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F1XCR_SubFlow             ARR_CORE_CXX       rm2fm2 rm1fm1 r0f20 r2p1
F1XCR_SubFlow             SCN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F1XCR_SubFlow             FUN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1

F5XCCFLO_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F5XCCFLO_SubFlow          ARR_CCF_CXX           rm2fm2 rm1fm1 r0f20 r2p1
F5XCCFLO_SubFlow          SCN_UNCORE_CX816    rm2fm2 rm1fm1 r0f20 r2p1
F5XCCFLO_SubFlow          FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
F5XATLO_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F5XATLO_SubFlow           ARR_ATOM_CXX       rm2fm2 rm1fm1 r0f20 r2p1
F5XATLO_SubFlow           SCN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
F5XATCCFLO_SubFlow        TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F5XCRLO_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F5XCRLO_SubFlow           ARR_CORE_CXX      rm2fm2 rm1fm1 r0f20 r2p1
F5XCRLO_SubFlow           SCN_CORE_CX816      rm2fm2 rm1fm1 r0f20 r2p1
             
F5TEMPDOWN_SubFlow        TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F5XCCF_SubFlow            TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F5XAT_SubFlow             TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F5XAT_SubFlow             FUN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
F5XATCCF_SubFlow          TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F5XATCCF_SubFlow          FUN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
F5XCR_SubFlow             TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F5XCR_SubFlow             FUN_CORE_CX816      rm2fm2 rm1fm1 r0f20 r2p1
F5XCR_SubFlow             TPI_SKUCTRL_CXX     rm2fm2 rm1fm1 r0f20 r2p1
VMAXXCCF_SubFlow          TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
VMAXXAT_SubFlow           TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
VMAXXAT_SubFlow           FUN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
VMAXXATCCF_SubFlow        TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
VMAXXATCCF_SubFlow        FUN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
VMAXXCR_SubFlow           TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
VMAXXCR_SubFlow           FUN_CORE_CX816      rm2fm2 rm1fm1 r0f20 r2p1
F4XCCF_SubFlow            TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F4XAT_SubFlow             TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F4XAT_SubFlow             FUN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
F4XATCCF_SubFlow          TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F4XATCCF_SubFlow          FUN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
F4XCR_SubFlow             TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}
F4XCR_SubFlow             FUN_CORE_CX816      rm2fm2 rm1fm1 r0f20 r2p1
RESUMETEMP_SubFlow        TPI_FLWFLGS_CXX     {ipcflwflgs_stdports}

VMAXXCCFLO_SubFlow        TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
VMAXXCCFLO_SubFlow        ARR_CCF_CXX       rm2fm2 rm1fm1 r0f20 r2p1
VMAXXCCFLO_SubFlow        SCN_UNCORE_CX816     rm2fm2 rm1fm1 r0f20 r2p1
VMAXXCCFLO_SubFlow        FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
VMAXXATLO_SubFlow         TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
VMAXXATLO_SubFlow         ARR_ATOM_CXX       rm2fm2 rm1fm1 r0f20 r2p1
VMAXXATLO_SubFlow         SCN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
VMAXXATCCFLO_SubFlow      TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
VMAXXCRLO_SubFlow         TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
VMAXXCRLO_SubFlow         ARR_CORE_CXX       rm2fm2 rm1fm1 r0f20 r2p1
VMAXXCRLO_SubFlow         SCN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1

F3XCCF_SubFlow            TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F3XCCF_SubFlow            ARR_CCF_CXX        rm2fm2 rm1fm1 r0f20 r2p1
F3XCCF_SubFlow            SCN_UNCORE_CX816     rm2fm2 rm1fm1 r0f20 r2p1
F3XCCF_SubFlow            FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
F3XAT_SubFlow             TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F3XAT_SubFlow             ARR_ATOM_CXX       rm2fm2 rm1fm1 r0f20 r2p1
F3XAT_SubFlow             SCN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1

F3XAT_SubFlow             FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F3XATCCF_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F3XATCCF_SubFlow          FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F3XCR_SubFlow             TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F3XCR_SubFlow              ARR_CORE_CXX      rm2fm2 rm1fm1 r0f20 r2p1
F3XCR_SubFlow             SCN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F3XCR_SubFlow             FUN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1

F4XCCFLO_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F4XCCFLO_SubFlow          ARR_CCF_CXX    rm2fm2 rm1fm1 r0f20 r2p1
F4XCCFLO_SubFlow          SCN_UNCORE_CX816    rm2fm2 rm1fm1 r0f20 r2p1
F4XCCFLO_SubFlow          FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
F4XATLO_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F4XATLO_SubFlow           ARR_ATOM_CXX      rm2fm2 rm1fm1 r0f20 r2p1
F4XATLO_SubFlow           SCN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F4XATCCFLO_SubFlow        TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}  
F4XCRLO_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F4XCRLO_SubFlow           ARR_CORE_CXX       rm2fm2 rm1fm1 r0f20 r2p1
F4XCRLO_SubFlow           SCN_CORE_CX816      rm2fm2 rm1fm1 r0f20 r2p1

F2XCCF_SubFlow            TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F2XCCF_SubFlow            ARR_CCF_CXX        rm2fm2 rm1fm1 r0f20 r2p1
F2XCCF_SubFlow            SCN_UNCORE_CX816     rm2fm2 rm1fm1 r0f20 r2p1
F2XCCF_SubFlow            FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
F2XAT_SubFlow             TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F2XAT_SubFlow             ARR_ATOM_CXX       rm2fm2 rm1fm1 r0f20 r2p1
F2XAT_SubFlow             SCN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F2XAT_SubFlow             FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1

F2XATCCF_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F2XATCCF_SubFlow          FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F2XCR_SubFlow             TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F2XCR_SubFlow               ARR_CORE_CXX      rm2fm2 rm1fm1 r0f20 r2p1
F2XCR_SubFlow             SCN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1
F2XCR_SubFlow             FUN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1
FMINXCCF_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
FMINXCCF_SubFlow          ARR_CCF_CXX        rm2fm2 rm1fm1 r0f20 r2p1
FMINXCCF_SubFlow          SCN_UNCORE_CX816     rm2fm2 rm1fm1 r0f20 r2p1
FMINXCCF_SubFlow            FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
FMINXAT_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
FMINXAT_SubFlow           ARR_ATOM_CXX       rm2fm2 rm1fm1 r0f20 r2p1
FMINXAT_SubFlow           SCN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1

FMINXAT_SubFlow           FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
FMINXATCCF_SubFlow        TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
FMINXATCCF_SubFlow        FUN_ATOM_CX816       rm2fm2 rm1fm1 r0f20 r2p1
FMINXCR_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
FMINXCR_SubFlow           ARR_CORE_CXX	   rm2fm2 rm1fm1 r0f20 r2p1
FMINXCR_SubFlow           FUN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1
FMINXCR_SubFlow           SCN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1


SPEEDCPUEMPTY0_SubFlow   TPI_FLWFLGS_CXX   {ipcflwflgs_stdports}
SPEEDCPUEMPTY1_SubFlow   TPI_FLWFLGS_CXX   {ipcflwflgs_stdports}
SPEEDCPUEMPTY2_SubFlow   TPI_FLWFLGS_CXX   {ipcflwflgs_stdports}        

BEGINPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_BEGINPRL0CPU        rm2fm2 rm1fm1 r0f20
BEGINPRL0CPU_SubFlow         BEGINCPU_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
BEGINPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_BEGINPRL0CPU        rm2fm2 rm1fm1 r0f20
BEGINPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_BEGINPRL1CPU        rm2fm2 rm1fm1 r0f20
BEGINPRL1CPU_SubFlow         BEGINCPUMAX_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
BEGINPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_BEGINPRL1CPU        rm2fm2 rm1fm1 r0f20
BEGINPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_BEGINPRL2CPU        rm2fm2 rm1fm1 r0f20
BEGINPRL2CPU_SubFlow         BEGINCPUNOM_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
BEGINPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_BEGINPRL2CPU        rm2fm2 rm1fm1 r0f20

ENDCPU_SubFlow            TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
ENDCPU_SubFlow            ARR_ATOM_CXX        rm2fm2 rm1fm1 r0f20 r2p1
ENDCPU_SubFlow            FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1
ENDCPU_SubFlow            ARR_CCF_CXX        rm2fm2 rm1fm1 r0f20 r2p1

ENDCPUNOM_SubFlow         TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
ENDCPUNOM_SubFlow         ARR_CORE_CXX       rm2fm2 rm1fm1 r0f20 r2p1
ENDCPUNOM_SubFlow         ARR_UNCORE_CXX       rm2fm2 rm1fm1 r0f20 r2p1
ENDCPUNOM_SubFlow         ARR_ATOM_CXX      rm2fm2 rm1fm1 r0f20 r2p1
ENDCPUMAX_SubFlow         TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
ENDCPUMAX_SubFlow          ARR_CORE_CXX      rm2fm2 rm1fm1 r0f20 r2p1
ENDCPUMAX_SubFlow          ARR_UNCORE_CXX      rm2fm2 rm1fm1 r0f20 r2p1
ENDCPUMAX_SubFlow          SCN_ATOM_CX816      rm2fm2 rm1fm1 r0f20 r2p1
ENDYBSCPU_SubFlow         TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
ENDPOSTYBSCPU_SubFlow     TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}

ENDPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_ENDPRL0CPU        rm2fm2 rm1fm1 r0f20
ENDPRL0CPU_SubFlow         ENDCPU_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
ENDPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_ENDPRL0CPU        rm2fm2 rm1fm1 r0f20
ENDPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_ENDPRL1CPU        rm2fm2 rm1fm1 r0f20
ENDPRL1CPU_SubFlow         ENDCPUNOM_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
ENDPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_ENDPRL1CPU        rm2fm2 rm1fm1 r0f20
ENDPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_ENDPRL2CPU        rm2fm2 rm1fm1 r0f20
ENDPRL2CPU_SubFlow         ENDCPUMAX_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
ENDPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_ENDPRL2CPU        rm2fm2 rm1fm1 r0f20
ENDPRL3CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_ENDPRL3CPU        rm2fm2 rm1fm1 r0f20
ENDPRL3CPU_SubFlow         ENDYBSCPU_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
ENDPRL3CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_ENDPRL3CPU        rm2fm2 rm1fm1 r0f20
ENDPRL4CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_ENDPRL4CPU        rm2fm2 rm1fm1 r0f20
ENDPRL4CPU_SubFlow         ENDPOSTYBSCPU_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
ENDPRL4CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_ENDPRL4CPU        rm2fm2 rm1fm1 r0f20

LTTCCPU_SubFlow           TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
LTTCCPU_SubFlow           PTH_BGR_CXPKGS7      {ipc_stdports}
LTTCCPU_SubFlow           PTH_DTS_CX816      {ipc_stdports}
LTTCCPU_SubFlow           PTH_DLVR_CXPKGS7      {ipc_stdports}
LTTCCPU_SubFlow           FUN_ATOM_CX816      {ipc_stdports}
LTTCCPU_SubFlow           FUN_CORE_CX816      {ipc_stdports}
LTTCCPU_SubFlow           ARR_ATOM_CXX      {ipc_stdports}
LTTCCPU_SubFlow           ARR_CCF_CXX      {ipc_stdports}
LTTCCPU_SubFlow           ARR_CORE_CXX      {ipc_stdports}
LTTCCPU_SubFlow           SCN_UNCORE_CX816      {ipc_stdports}
LTTCCPUMAX_SubFlow        TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
LTTCCPUMAX_SubFlow           SCN_ATOM_CX816      {ipc_stdports}
FACTFUSBUILDCPUNOM_SubFlow   TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
FACTFUSBUILDCPUNOM_SubFlow   FUS_FSG_CXX      {ipc_stdports}
FACTFUSBUILDCPUNOM_SubFlow   FUS_FUSEBURN_CXX      {ipc_stdports}
FACTFUSBURNCPUNOM_SubFlow    TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
FACTFUSBURNCPUNOM_SubFlow    FUS_FUSEBURN_CXX      {ipc_stdports}

FACTPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_FACTPRL0CPU        rm2fm2 rm1fm1 r0f20
FACTPRL0CPU_SubFlow       FACTFUSBUILDCPUNOM_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
FACTPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_FACTPRL0CPU        rm2fm2 rm1fm1 r0f20

FACTPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_FACTPRL1CPU        rm2fm2 rm1fm1 r0f20
FACTPRL1CPU_SubFlow       FACTFUSBURNCPUNOM_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
FACTPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_FACTPRL1CPU        rm2fm2 rm1fm1 r0f20

HVBIPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_HVBIPRL0CPU        rm2fm2 rm1fm1 r0f20
HVBIPRL0CPU_SubFlow       HVBICPU_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
HVBIPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_HVBIPRL0CPU        rm2fm2 rm1fm1 r0f20

LTTCPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_LTTCPRL0CPU        rm2fm2 rm1fm1 r0f20
LTTCPRL0CPU_SubFlow       LTTCCPU_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
LTTCPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_LTTCPRL0CPU        rm2fm2 rm1fm1 r0f20

LTTCPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_LTTCPRL1CPU        rm2fm2 rm1fm1 r0f20
LTTCPRL1CPU_SubFlow       LTTCCPUMAX_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
LTTCPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_LTTCPRL1CPU        rm2fm2 rm1fm1 r0f20

SPEEDPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_SPEEDPRL0CPU        rm2fm2 rm1fm1 r0f20
SPEEDPRL0CPU_SubFlow   F1XCCF_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow   F1XAT_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow   F1XATCCF_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow   F1XCR_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow   F5XCCFLO_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow   F5XATLO_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow   F5XATCCFLO_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow   F5XCRLO_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_SPEEDPRL0CPU        rm2fm2 rm1fm1 r0f20

SPEEDPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_SPEEDPRL1CPU        rm2fm2 rm1fm1 r0f20
SPEEDPRL1CPU_SubFlow   F5TEMPDOWN_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F5XCCF_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F5XAT_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F5XATCCF_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F5XCR_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   VMAXXCCF_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   VMAXXAT_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   VMAXXATCCF_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   VMAXXCR_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F4XCCF_SubFlow         rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F4XAT_SubFlow          rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F4XATCCF_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   F4XCR_SubFlow          rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow   RESUMETEMP_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_SPEEDPRL1CPU        rm2fm2 rm1fm1 r0f20

SPEEDPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_SPEEDPRL2CPU        rm2fm2 rm1fm1 r0f20
SPEEDPRL2CPU_SubFlow   VMAXXCCFLO_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   VMAXXATLO_SubFlow      rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   VMAXXATCCFLO_SubFlow   rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   VMAXXCRLO_SubFlow      rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F3XCCF_SubFlow         rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F3XAT_SubFlow          rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F3XATCCF_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F3XCR_SubFlow          rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F4XCCFLO_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F4XATLO_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F4XATCCFLO_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F4XCRLO_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F2XCCF_SubFlow         rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F2XAT_SubFlow          rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F2XATCCF_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   F2XCR_SubFlow          rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   FMINXCCF_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   FMINXAT_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   FMINXATCCF_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow   FMINXCR_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_SPEEDPRL2CPU        rm2fm2 rm1fm1 r0f20


#Dummy flow PRL14/15/16, maybe they cannot be void -Maroon
SPEEDPRL3CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_SPEEDPRL3CPU        rm2fm2 rm1fm1 r0f20
SPEEDPRL3CPU_SubFlow   SPEEDCPUEMPTY0_SubFlow  rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL3CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_SPEEDPRL3CPU        rm2fm2 rm1fm1 r0f20

SPEEDPRL4CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_SPEEDPRL4CPU        rm2fm2 rm1fm1 r0f20
SPEEDPRL4CPU_SubFlow   SPEEDCPUEMPTY1_SubFlow  rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL4CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_SPEEDPRL4CPU        rm2fm2 rm1fm1 r0f20

SPEEDPRL5CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_SPEEDPRL5CPU        rm2fm2 rm1fm1 r0f20
SPEEDPRL5CPU_SubFlow   SPEEDCPUEMPTY2_SubFlow  rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL5CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_SPEEDPRL5CPU        rm2fm2 rm1fm1 r0f20


STARTPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_STARTPRL0CPU        rm2fm2 rm1fm1 r0f20
STARTPRL0CPU_SubFlow      STARTCPUNOM_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
STARTPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_STARTPRL0CPU        rm2fm2 rm1fm1 r0f20

STARTPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_STARTPRL1CPU        rm2fm2 rm1fm1 r0f20
STARTPRL1CPU_SubFlow      STARTANA0CPU_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
STARTPRL1CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_STARTPRL1CPU        rm2fm2 rm1fm1 r0f20

STARTPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_STARTPRL2CPU        rm2fm2 rm1fm1 r0f20
STARTPRL2CPU_SubFlow      STARTANA1CPU_SubFlow       rm2fm2 rm1fm1 r0f20 r20f20
STARTPRL2CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_STARTPRL2CPU        rm2fm2 rm1fm1 r0f20

STARTPRL3CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_STARTPRL3CPU        rm2fm2 rm1fm1 r0f20
STARTPRL3CPU_SubFlow      STARTPWRCPU_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
STARTPRL3CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_STARTPRL3CPU        rm2fm2 rm1fm1 r0f20

STARTPRL4CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_STARTPRL4CPU        rm2fm2 rm1fm1 r0f20
STARTPRL4CPU_SubFlow      STARTHPTPDRVCPU_SubFlow    rm2fm2 rm1fm1 r0f20 r20f20
STARTPRL4CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_STARTPRL4CPU        rm2fm2 rm1fm1 r0f20

'''
ProgramFlows().main(MAIN_code, 'CPU_ProgramFlows', ip=False)
