pkg_stdports = 'rm2fm2 rm1fm1 r0f0'
init_stdports = 'rm2fm2 rm1fm1 r0f0'

### Disaggregated Dielet PKG flow, please put your module in the correct Init section IP or PKG. 
CPUDISAGG_SubFlow = f'''
STARTCPUPATMODSPKG_SubFlow    TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1
STARTCPUPATMODSPKG_SubFlow    FUS_FUSECFG_CKX      {pkg_stdports}
STARTCPUPATMODSPKG_SubFlow    FUS_UNITINFO_CKX     {pkg_stdports}
STARTCPUPATMODSPKG_SubFlow    ARR_COMMON_CKPKGS9      {pkg_stdports}
STARTCPUPATMODSPKG_SubFlow    PTH_DLVR_CKPKGS9     {pkg_stdports}
STARTCPUPATMODSPKG_SubFlow    CLK_DEBUG_CKXX       {pkg_stdports}

HVBICPUPKG_SubFlow            TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1

BEGINCPUPKG_SubFlow           TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1
BEGINCPUPKG_SubFlow           ARR_CORE_CKPKGS9     rm2fm2 rm1fm1 r0f0 r2p1
BEGINCPUPKG_SubFlow           ARR_UNCORE_CKPKGS9     rm2fm2 rm1fm1 r0f0 r2p1
BEGINCPUPKG_SubFlow           SCN_UNCORE_CKPKGS9      rm2fm2 rm1fm1 r0f0 r2p1
BEGINCPUPKG_SubFlow           FUS_FUSEVLD_CKX      {pkg_stdports}
BEGINCPUPKG_SubFlow           CLK_DEBUG_CKXX       {pkg_stdports}

ENDCPUPKG_SubFlow             TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1
ENDCPUPKG_SubFlow             ARR_CORE_CKPKGS9     {pkg_stdports}
ENDCPUPKG_SubFlow             ARR_COMMON_CKPKGS9     {pkg_stdports}
ENDCPUPKG_SubFlow             TPI_DIERCVRY_CXX     {pkg_stdports}
ENDCPUPKG_SubFlow             PTH_DLVR_CKPKGS9     {pkg_stdports}

ENDCPUVMAXPKG_SubFlow         TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1

LTTCCPUPKG_SubFlow            TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1
LTTCCPUPKG_SubFlow			  ARR_UNCORE_CKPKGS9   rm2fm2 rm1fm1 r0f0 r2p1

CPUIPFF_SubFlow               TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1
CPUIPFF_SubFlow               IPC::DRV_RESET_CXX::DRV_RESET_CXX_CPUIPFF      rm2fm2 rm1fm1 r0f0
CPUIPFF_SubFlow               IPC::QNR_CARV_CXX::QNR_CARV_CXX_CPUIPFF      rm2fm2 rm1fm1 r0f0

CPUPKGFF_SubFlow              TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1
CPUPKGFF_SubFlow              QNR_CARV_CKX::QNR_CARV_CKX_CPUPKGFF      rm2fm2 rm1fm1 r0f0 r2p1
'''

### Disaggregated Init flow into dielet, please put your module in the correct Init section IP or PKG. 
INITCPU_SubFlow = f'''
INITCPU_SubFlow          IPC::TPI_DIERCVRY_CXX::TPI_DIERCVRY_CXX_INIT   {init_stdports}
INITCPU_SubFlow          IPC::FUS_FUSECFG_CXX::FUS_FUSECFG_CXX_INIT   {init_stdports}
INITCPU_SubFlow          IPC::FUS_UNITINFO_CXX::FUS_UNITINFO_CXX_INIT   {init_stdports}
INITCPU_SubFlow          IPC::FUS_FUSEREAD_CXX::FUS_FUSEREAD_CXX_INIT   {init_stdports}
INITCPU_SubFlow          IPC::FUS_FUSEBURN_CXX::FUS_FUSEBURN_CXX_INIT   {init_stdports}
INITCPU_SubFlow          IPC::PTH_VDAC_CXX::PTH_VDAC_CXX_INIT           {init_stdports}
INITCPU_SubFlow          IPC::PTH_DTS_CXPKGS9::PTH_DTS_CXPKGS9_INIT {init_stdports}
INITCPU_SubFlow          IPC::CLK_BASE_CXXX::CLK_BASE_CXXX_INIT   {init_stdports}
INITCPU_SubFlow          IPC::ARR_CORE_CXPKGS9::ARR_CORE_CXPKGS9_INIT   {init_stdports}
INITCPU_SubFlow          IPC::ARR_CCF_CXPKGS9::ARR_CCF_CXPKGS9_INIT   {init_stdports}
INITCPU_SubFlow          IPC::SCN_CORE_CXPKGS9::SCN_CORE_CXPKGS9_INIT   {init_stdports}
INITCPU_SubFlow          IPC::SCN_ATOM_CXPKGS9::SCN_ATOM_CXPKGS9_INIT   {init_stdports}
INITCPU_SubFlow          IPC::FUN_ATOM_CXPKGS9::FUN_ATOM_CXPKGS9_INIT  {init_stdports}
INITCPU_SubFlow          IPC::FUN_CCF_CXPKGS9::FUN_CCF_CXPKGS9_INIT   {init_stdports}
INITCPU_SubFlow          IPC::FUN_CORE_CXPKGS9::FUN_CORE_CXPKGS9_INIT  {init_stdports}
INITCPU_SubFlow          IPC::SCN_UNCORE_CXPKGS9::SCN_UNCORE_CXPKGS9_INIT  {init_stdports}
INITCPU_SubFlow          IPC::ARR_ATOM_CXPKGS9::ARR_ATOM_CXPKGS9_INIT  {init_stdports}
INITCPU_SubFlow          IPC::QNR_CARV_CXX::QNR_CARV_CXX_INIT   {init_stdports}
'''

### If your module is the 1st module of the section, please help remove the comment out to enable the section in the Init flow.
INITCPUPKG_SubFlow = f'''
INITCPUPKG_SubFlow   FUS_FUSECFG_CKX::FUS_FUSECFG_CKX_INIT        {init_stdports}
INITCPUPKG_SubFlow   FUS_UNITINFO_CKX::FUS_UNITINFO_CKX_INIT        {init_stdports}
INITCPUPKG_SubFlow   DRV_RESET_CKX::DRV_RESET_CKX_INIT        {init_stdports}
INITCPUPKG_SubFlow   CLK_DEBUG_CKXX::CLK_DEBUG_CKXX_INIT        {init_stdports}
INITCPUPKG_SubFlow   ARR_COMMON_CKPKGS9::ARR_COMMON_CKPKGS9_INIT        {init_stdports}
INITCPUPKG_SubFlow   SCN_UNCORE_CKPKGS9::SCN_UNCORE_CKPKGS9_INIT        {init_stdports}
INITCPUPKG_SubFlow   QNR_CARV_CKX::QNR_CARV_CKX_INIT   {init_stdports}

'''
