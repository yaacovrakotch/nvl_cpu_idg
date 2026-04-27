import sys
import os
sys.path.append('../../../POR_TP/Class_NVL_HX28C/ProgramFlowsTestPlan')
try:
    from ProgramFlowsCPU import CPUDISAGG_SubFlow, INITCPU_SubFlow, INITCPUPKG_SubFlow
except:
    CPUDISAGG_SubFlow = ''
    INITCPU_SubFlow = ''
    INITCPUPKG_SubFlow = ''
    print('CPU Dielet is NOT existing.')
try:
    from ProgramFlowsGCD import GCDDISAGG_SubFlow, INITGCD_SubFlow, INITGCDPKG_SubFlow
except:
    GCDDISAGG_SubFlow = ''
    INITGCD_SubFlow = ''
    INITGCDPKG_SubFlow = ''
    print('GCD Dielet is NOT existing.')
try:
    from ProgramFlowsHUB import HUBDISAGG_SubFlow, INITHUB_SubFlow, INITHUBPKG_SubFlow
except:
    HUBDISAGG_SubFlow = ''
    INITHUB_SubFlow = ''
    INITHUBPKG_SubFlow = ''
    print('HUB Dielet is NOT existing.')
try:
    from ProgramFlowsPCD import PCDDISAGG_SubFlow, INITPCD_SubFlow, INITPCDPKG_SubFlow
except:
    PCDDISAGG_SubFlow = ''
    INITPCD_SubFlow = ''
    INITPCDPKG_SubFlow = ''
    print('PCD Dielet is NOT existing.')

topf_stdports = 'rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:PKGFF_SubFlow r2f:DCFF_SubFlow r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:HUBIPFF_SubFlow r50f:PCDIPFF_SubFlow r21f:CPUPKGFF_SubFlow r31f:GCDPKGFF_SubFlow r41f:HUBPKGFF_SubFlow r51f:PCDPKGFF_SubFlow'
pkg_stdports = 'rm2fm2 rm1fm1 r0f0'
dc_stdports = 'rm2fm2 rm1fm1 r0f2'
cpupkg_stdports = 'rm2fm2 rm1fm1 r0f21'
gcdpkg_stdports = 'rm2fm2 rm1fm1 r0f31'
hubpkg_stdports = 'rm2fm2 rm1fm1 r0f41'
pcdpkg_stdports = 'rm2fm2 rm1fm1 r0f51'
parallel_stdports = 'rm2fm2 rm1fm1 r20f20 r30f30 r40f40 r50f50'
flwflgs_stdports = 'rm2fm2 rm1fm1 r0f0 r2p1'

MAIN_code = f'''
# FULLTPONLY: DRV_RESET_XXX
# FULLTPONLY: MIO_D2D_XKPKGHX

START_SubFlow                 TPI_FLWFLGS_XXX                                      {flwflgs_stdports} 
START_SubFlow                 TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_START   rm2fm2 rm1fm1 r0f0
START_SubFlow                 TPI_BASE_XXX                                         {pkg_stdports} 
START_SubFlow                 PTH_THRSOAK_XXX                                       {dc_stdports}                                               
START_SubFlow                 TPI_PWRCTRL_XXX::TPI_PWRCTRL_XXX_PWRCTRLDC_START           {dc_stdports} 
START_SubFlow                 TPI_VCC_XXX                                      rm2fm2 rm1fm1 r0f0 r2fm2
START_SubFlow                 TPI_SHOPS_XKPKGMB                                    rm2fm2 rm1fm1 r0f2 r2fm2
START_SubFlow                 TPI_EDM_XXX                                      rm2fm2 rm1fm1 r0f2 r2fm2
START_SubFlow                 PTH_DIODE_XXX                                         {dc_stdports}
START_SubFlow                 TPI_PWRCTRL_XXX::TPI_PWRCTRL_XXX_PWRCTRLPKG_START          {dc_stdports}
START_SubFlow                 TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_START   rm2fm2 rm1fm1 r0f0

STARTSHAREDRAILSNOM_SubFlow   TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_STARTSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0
STARTSHAREDRAILSNOM_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
STARTSHAREDRAILSNOM_SubFlow   FUS_ISEED_XXX::FUS_ISEED_XXX_START       rm2fm2 rm1fm1 r0f0 r2p1
STARTPREPRL0_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTSHAREDRAILSMIN_SubFlow   TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTSHAREDRAILSMIN_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
STARTSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_STARTSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0


STARTPREPRL1_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTPREPRL1_SubFlow          TPI_DFF_XXX          {pkg_stdports}
STARTPREPRL1_SubFlow          TPI_BASE_XXX         {pkg_stdports}
STARTPREPRL1_SubFlow          TPI_MIXDETCT_XXX     {pkg_stdports}
STARTPREPRL1_SubFlow          FUS_FACT_XXX         rm2fm2 rm1fm1 r0f0 r2p3
STARTPREPRL1_SubFlow          TPI_SKUCTRL_XXX      {pkg_stdports}
STARTPREPRL2_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTPREPRL2_SubFlow          TPI_PWRCTRL_XXX      {pkg_stdports}
STARTPWR_SubFlow              TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTSHAREDRAILSMIN1_SubFlow  TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTSHAREDRAILSMIN1_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_STARTSHAREDRAILSMIN1   rm2fm2 rm1fm1 r0f0
STARTSHAREDRAILSMIN1_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
STARTSHAREDRAILSMIN1_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_STARTSHAREDRAILSMIN1   rm2fm2 rm1fm1 r0f0

STARTPREPRL3_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTPREPRL4_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTPOST_SubFlow             TPI_FLWFLGS_XXX      {flwflgs_stdports}
STARTPOST_SubFlow             TPI_BASE_XXX::TPI_BASE_XXX_STARTPOST    {pkg_stdports}
 
HVBISHAREDRAILSMIN_SubFlow    TPI_FLWFLGS_XXX      {flwflgs_stdports}
HVBISHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_HVBISHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0
HVBISHAREDRAILSMIN_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
HVBISHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_HVBISHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0

HVBIPREPRL0_SubFlow           TPI_FLWFLGS_XXX      {flwflgs_stdports}

BEGIN_SubFlow                 TPI_FLWFLGS_XXX      {flwflgs_stdports}
BEGIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_BEGIN   rm2fm2 rm1fm1 r0f0
BEGIN_SubFlow                 TPI_BASE_XXX         rm2fm2 rm1fm1 r0f0
BEGIN_SubFlow                 FUS_FACT_XXX         rm2fm2 rm1fm1 r0f0 r2p3
BEGIN_SubFlow                 PTH_DIODE_XXX         rm2fm2 rm1fm1 r0f0
BEGIN_SubFlow                 DRV_RESET_XXX        {pkg_stdports}
BEGIN_SubFlow                 MIO_D2D_XKPKGHX          rm2fm2 rm1fm1 r0f4
BEGIN_SubFlow                 DRV_RESET_XXX::DRV_RESET_XXX_D2DPATMODS_BEGIN        {pkg_stdports}
BEGIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_BEGIN   rm2fm2 rm1fm1 r0f0
BEGINSHAREDRAILSMIN_SubFlow   TPI_FLWFLGS_XXX      {flwflgs_stdports}
BEGINSHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_BEGINSHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0
BEGINSHAREDRAILSMIN_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
BEGINSHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_BEGINSHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0

BEGINPREPRL0_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports} 
BEGINSHAREDRAILSMAX_SubFlow   TPI_FLWFLGS_XXX      {flwflgs_stdports}
BEGINSHAREDRAILSMAX_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_BEGINSHAREDRAILSMAX   rm2fm2 rm1fm1 r0f0
BEGINSHAREDRAILSMAX_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
BEGINSHAREDRAILSMAX_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_BEGINSHAREDRAILSMAX   rm2fm2 rm1fm1 r0f0

BEGINPREPRL1_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
BEGINSHAREDRAILSNOM_SubFlow   TPI_FLWFLGS_XXX      {flwflgs_stdports}
BEGINSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_BEGINSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0
BEGINSHAREDRAILSNOM_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
BEGINSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_BEGINSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0

BEGINPREPRL2_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
SPEEDSHAREDRAILSMIN_SubFlow   TPI_FLWFLGS_XXX      {flwflgs_stdports}
SPEEDSHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_SPEEDSHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0
SPEEDSHAREDRAILSMIN_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
SPEEDSHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_SPEEDSHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0

SPEEDPREPRL0_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
SPEEDPREPRL1_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
SPEEDPREPRL1_SubFlow          PTH_THRSOAK_XXX      {flwflgs_stdports}
SPEEDPREPRL2_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
SPEEDPREPRL2_SubFlow          PTH_THRSOAK_XXX      {flwflgs_stdports}
SPEEDPREPRL3_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
SPEEDPREPRL4_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
SPEEDPREPRL5_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}

ENDPREPRL0_SubFlow            TPI_FLWFLGS_XXX      {flwflgs_stdports}
ENDPREPRL0_SubFlow            YBS_UPSS_XXX         {pkg_stdports}
ENDSHAREDRAILSNOM_SubFlow     TPI_FLWFLGS_XXX      {flwflgs_stdports}
ENDSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_ENDSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0
ENDSHAREDRAILSNOM_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
ENDSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_ENDSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0

ENDPREPRL1_SubFlow            TPI_FLWFLGS_XXX      {flwflgs_stdports}
ENDSHAREDRAILSMAX_SubFlow     TPI_FLWFLGS_XXX      {flwflgs_stdports}
ENDSHAREDRAILSMAX_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_ENDSHAREDRAILSMAX   rm2fm2 rm1fm1 r0f0
ENDSHAREDRAILSMAX_SubFlow     TPI_PWRCTRL_XXX          {pkg_stdports}
ENDSHAREDRAILSMAX_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_ENDSHAREDRAILSMAX   rm2fm2 rm1fm1 r0f0

ENDPREPRL2_SubFlow            TPI_FLWFLGS_XXX      {flwflgs_stdports}
ENDPREPRL3_SubFlow            TPI_FLWFLGS_XXX      {flwflgs_stdports}
ENDSHAREDRAILSMIN_SubFlow     TPI_FLWFLGS_XXX      {flwflgs_stdports}
ENDSHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_ENDSHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0
ENDSHAREDRAILSMIN_SubFlow     TPI_PWRCTRL_XXX          {pkg_stdports}
ENDSHAREDRAILSMIN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_ENDSHAREDRAILSMIN   rm2fm2 rm1fm1 r0f0

ENDPREPRL4_SubFlow            TPI_FLWFLGS_XXX      {flwflgs_stdports}
END_SubFlow                   TPI_FLWFLGS_XXX      {flwflgs_stdports}
END_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_END   rm2fm2 rm1fm1 r0f0
END_SubFlow                   YBS_UPSS_XXX     {pkg_stdports}
END_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_END   rm2fm2 rm1fm1 r0f0
END_SubFlow                   PTH_THRSOAK_XXX     {pkg_stdports}

LTTCPREPRL0_SubFlow           TPI_FLWFLGS_XXX      {flwflgs_stdports}
LTTCPREPRL0_SubFlow           PTH_DIODE_XXX        {flwflgs_stdports}
LTTCRAMP_SubFlow              TPI_FLWFLGS_XXX      {flwflgs_stdports}
LTTCRAMP_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_LTTCRAMP   rm2fm2 rm1fm1 r0f0
LTTCRAMP_SubFlow              TPI_LTTC_XXX         {pkg_stdports}
LTTCRAMP_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_LTTCRAMP   rm2fm2 rm1fm1 r0f0
LTTCCOMMON_SubFlow            TPI_FLWFLGS_XXX      {flwflgs_stdports}
LTTCCOMMON_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_LTTCCOMMON   rm2fm2 rm1fm1 r0f0
LTTCCOMMON_SubFlow            MIO_D2D_XKPKGHX          {flwflgs_stdports}
LTTCCOMMON_SubFlow            DRV_RESET_XXX          {flwflgs_stdports}
LTTCCOMMON_SubFlow            TPI_PWRCTRL_XXX::TPI_PWRCTRL_XXX_PWRCTRLDC_LTTCCOMMON      {pkg_stdports}
LTTCCOMMON_SubFlow            TPI_VCC_XXX      rm2fm2 rm1fm1 r0f0 r2fm2 r3f0
LTTCCOMMON_SubFlow            TPI_VCCMIMS_XXX      {pkg_stdports}
LTTCCOMMON_SubFlow            TPI_PWRCTRL_XXX::TPI_PWRCTRL_XXX_SETPKGPWR_LTTCCOMMON      {pkg_stdports}
LTTCCOMMON_SubFlow            TPI_PWRCTRL_XXX::TPI_PWRCTRL_XXX_SETRAIL_LTTCCOMMON      {pkg_stdports}
LTTCCOMMON_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_LTTCCOMMON   rm2fm2 rm1fm1 r0f0


LTTCSHAREDRAILSMIN1_SubFlow   TPI_FLWFLGS_XXX      {flwflgs_stdports}
LTTCSHAREDRAILSMIN1_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_LTTCSHAREDRAILSMIN1   rm2fm2 rm1fm1 r0f0
LTTCSHAREDRAILSMIN1_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
LTTCSHAREDRAILSMIN1_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_LTTCSHAREDRAILSMIN1   rm2fm2 rm1fm1 r0f0

LTTCPREPRL1_SubFlow           TPI_FLWFLGS_XXX      {flwflgs_stdports}
LTTCSHAREDRAILSMAX_SubFlow    TPI_FLWFLGS_XXX      {flwflgs_stdports}
LTTCSHAREDRAILSMAX_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_LTTCSHAREDRAILSMAX   rm2fm2 rm1fm1 r0f0
LTTCSHAREDRAILSMAX_SubFlow    TPI_PWRCTRL_XXX          {pkg_stdports}
LTTCSHAREDRAILSMAX_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_LTTCSHAREDRAILSMAX   rm2fm2 rm1fm1 r0f0
LTTCPOST_SubFlow              TPI_FLWFLGS_XXX      {flwflgs_stdports}
LTTCPOST_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_LTTCPOST   rm2fm2 rm1fm1 r0f0
LTTCPOST_SubFlow              TPI_LTTC_XXX         {pkg_stdports}
LTTCPOST_SubFlow              YBS_UPSS_XXX         {pkg_stdports}
LTTCPOST_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_LTTCPOST   rm2fm2 rm1fm1 r0f0

FACTRAMP_SubFlow           TPI_FLWFLGS_XXX      {flwflgs_stdports}
FACTRAMP_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_FACTRAMP   rm2fm2 rm1fm1 r0f0
FACTRAMP_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_FACTRAMP   rm2fm2 rm1fm1 r0f0


FACT_SubFlow                  TPI_FLWFLGS_XXX      {flwflgs_stdports}
FACT_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_FACT   rm2fm2 rm1fm1 r0f0
FACT_SubFlow                  TPI_BASE_XXX         rm2fm2 rm1fm1 r0f0 r2pn
FACT_SubFlow                  FUS_FACT_XXX         rm2fm2 rm1fm1 r0f0 r2pn r3p3
FACT_SubFlow    FUS_ISEED_XXX::FUS_ISEED_XXX_FACT        rm2fm2 rm1fm1 r0f0 r2p1 r3p3
FACT_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_FACT   rm2fm2 rm1fm1 r0f0


FACTPREFUSEBURN_SubFlow       TPI_FLWFLGS_XXX      {flwflgs_stdports}
FACTPREFUSEBURN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_FACTPREFUSEBURN   rm2fm2 rm1fm1 r0f0
FACTPREFUSEBURN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_FACTPREFUSEBURN   rm2fm2 rm1fm1 r0f0


FACTSHAREDRAILSNOM_SubFlow    TPI_FLWFLGS_XXX      {flwflgs_stdports}
FACTSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_FACTSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0
FACTSHAREDRAILSNOM_SubFlow   TPI_PWRCTRL_XXX          {pkg_stdports}
FACTSHAREDRAILSNOM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_FACTSHAREDRAILSNOM   rm2fm2 rm1fm1 r0f0

FACTPREPRL0_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
FACTPREPRL1_SubFlow          TPI_FLWFLGS_XXX      {flwflgs_stdports}
FACTPOSTFUSEBURN_SubFlow      TPI_FLWFLGS_XXX      {flwflgs_stdports}
FACTPOSTFUSEBURN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_FACTPOSTFUSEBURN   rm2fm2 rm1fm1 r0f0
FACTPOSTFUSEBURN_SubFlow      FUS_ISEEDSET_XXX::FUS_ISEEDSET_XXX_FACT      {pkg_stdports}
FACTPOSTFUSEBURN_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_FACTPOSTFUSEBURN   rm2fm2 rm1fm1 r0f0

FINAL_SubFlow                 TPI_FLWFLGS_XXX      {flwflgs_stdports}
FINAL_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_FINAL   rm2fm2 rm1fm1 r0f0
FINAL_SubFlow                 TPI_BASE_XXX         rm2fm2 rm1fm1 r0f0 r2p:TPI_DFF_XXX
FINAL_SubFlow                 PTH_DIODE_XXX        rm2fm2 rm1fm1 r0f0
FINAL_SubFlow                 TPI_DFF_XXX          rm2fm2 rm1fm1 r0f0 r2p1
FINAL_SubFlow                 TPI_END_XXX          {pkg_stdports} 

DCFF_SubFlow                  TPI_FLWFLGS_XXX      {flwflgs_stdports}
DCFF_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_DCFF   rm2fm2 rm1fm1 r0f0
DCFF_SubFlow                  TPI_EDM_XXX          rm2fm2 rm1fm1 r0f0 r2f2
DCFF_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_DCFF   rm2fm2 rm1fm1 r0f0

PKGFF_SubFlow                 TPI_FLWFLGS_XXX      {flwflgs_stdports}
PKGFF_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_PKGFF   rm2fm2 rm1fm1 r0f0
PKGFF_SubFlow                 DRV_RESET_XXX        {pkg_stdports}
PKGFF_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_PKGFF   rm2fm2 rm1fm1 r0f0

ALARM_SubFlow                 TPI_FLWFLGS_XXX      {flwflgs_stdports}
ALARM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_FIRST_ALARM   rm2fm2 rm1fm1 r0f0
ALARM_SubFlow                 TPI_BASE_XXX         rm2fm2 rm1fm1 r0f0 r2p1
ALARM_SubFlow   TPI_TIMETRK_XXX::TPI_TIMETRK_XXX_LAST_ALARM   rm2fm2 rm1fm1 r0f0

{CPUDISAGG_SubFlow}
{GCDDISAGG_SubFlow}
{HUBDISAGG_SubFlow}
{PCDDISAGG_SubFlow}

START_TopFlow    START_SubFlow                  rm2fm2 rm1fm1 r0f0 r2f2
START_TopFlow    STARTSHAREDRAILSNOM_SubFlow    {pkg_stdports}
START_TopFlow    STARTPREPRL0_SubFlow           {pkg_stdports}
START_TopFlow    $STARTPRL0_SubFlow             {parallel_stdports}
START_TopFlow    STARTSHAREDRAILSMIN_SubFlow    {pkg_stdports}
START_TopFlow    STARTPREPRL1_SubFlow           rm2fm2 rm1fm1 r0f0 r3p3
START_TopFlow    $STARTPRL1_SubFlow             {parallel_stdports}
START_TopFlow    STARTPREPRL2_SubFlow           {pkg_stdports}
START_TopFlow    $STARTPRL2_SubFlow             {parallel_stdports}
START_TopFlow    STARTPWR_SubFlow               {pkg_stdports}
START_TopFlow    STARTSHAREDRAILSMIN1_SubFlow   {pkg_stdports}
START_TopFlow    STARTPREPRL3_SubFlow           {pkg_stdports}
START_TopFlow    $STARTPRL3_SubFlow             {parallel_stdports}
START_TopFlow    STARTPREPRL4_SubFlow           {pkg_stdports}
START_TopFlow    $STARTPRL4_SubFlow             {parallel_stdports}
START_TopFlow    STARTCPUPATMODSPKG_SubFlow     {cpupkg_stdports}
START_TopFlow    STARTGCDPATMODSPKG_SubFlow     {gcdpkg_stdports}
START_TopFlow    STARTHUBPATMODSPKG_SubFlow     {hubpkg_stdports}
START_TopFlow    STARTPCDPATMODSPKG_SubFlow     {pcdpkg_stdports}
START_TopFlow    STARTPOST_SubFlow              {pkg_stdports}

HVBI_TopFlow     HVBICPUPKG_SubFlow             {cpupkg_stdports}
HVBI_TopFlow     HVBIGCDPKG_SubFlow             {gcdpkg_stdports}
HVBI_TopFlow     HVBIHUBPKG_SubFlow             {hubpkg_stdports}
HVBI_TopFlow     HVBIPCDPKG_SubFlow             {pcdpkg_stdports}
HVBI_TopFlow     HVBISHAREDRAILSMIN_SubFlow     {pkg_stdports}
HVBI_TopFlow     HVBIPREPRL0_SubFlow            {pkg_stdports}
HVBI_TopFlow     $HVBIPRL0_SubFlow              {parallel_stdports}

BEGIN_TopFlow    BEGIN_SubFlow                  rm2fm2 rm1fm1 r0f4 r3p3 r4f0
BEGIN_TopFlow    BEGINCPUPKG_SubFlow            {cpupkg_stdports}
BEGIN_TopFlow    BEGINGCDPKG_SubFlow            {gcdpkg_stdports}
BEGIN_TopFlow    BEGINHUBPKG_SubFlow            {hubpkg_stdports}
BEGIN_TopFlow    BEGINPCDPKG_SubFlow            {pcdpkg_stdports}
BEGIN_TopFlow    BEGINSHAREDRAILSMIN_SubFlow    {pkg_stdports}
BEGIN_TopFlow    BEGINPREPRL0_SubFlow           {pkg_stdports}
BEGIN_TopFlow    $BEGINPRL0_SubFlow             {parallel_stdports}
BEGIN_TopFlow    BEGINSHAREDRAILSMAX_SubFlow    {pkg_stdports}
BEGIN_TopFlow    BEGINPREPRL1_SubFlow           {pkg_stdports}
BEGIN_TopFlow    $BEGINPRL1_SubFlow             {parallel_stdports}
BEGIN_TopFlow    BEGINSHAREDRAILSNOM_SubFlow    {pkg_stdports}
BEGIN_TopFlow    BEGINPREPRL2_SubFlow           {pkg_stdports}
BEGIN_TopFlow    $BEGINPRL2_SubFlow             {parallel_stdports}

SPEED_TopFlow    SPEEDSHAREDRAILSMIN_SubFlow    {pkg_stdports}
SPEED_TopFlow    SPEEDPREPRL0_SubFlow           {pkg_stdports}
SPEED_TopFlow    $SPEEDPRL0_SubFlow             {parallel_stdports}              
SPEED_TopFlow    SPEEDPREPRL1_SubFlow           {pkg_stdports}
SPEED_TopFlow    $SPEEDPRL1_SubFlow             {parallel_stdports}
SPEED_TopFlow    SPEEDPREPRL2_SubFlow           {pkg_stdports}
SPEED_TopFlow    $SPEEDPRL2_SubFlow             {parallel_stdports}
SPEED_TopFlow    SPEEDPREPRL3_SubFlow           {pkg_stdports}
SPEED_TopFlow    $SPEEDPRL3_SubFlow             {parallel_stdports}
SPEED_TopFlow    SPEEDPREPRL4_SubFlow           {pkg_stdports}
SPEED_TopFlow    $SPEEDPRL4_SubFlow             {parallel_stdports}
SPEED_TopFlow    SPEEDPREPRL5_SubFlow           {pkg_stdports}
SPEED_TopFlow    $SPEEDPRL5_SubFlow             {parallel_stdports}

END_TopFlow      ENDPREPRL0_SubFlow             {pkg_stdports}
END_TopFlow      $ENDPRL0_SubFlow               {parallel_stdports}
END_TopFlow      ENDSHAREDRAILSNOM_SubFlow      {pkg_stdports}
END_TopFlow      ENDPREPRL1_SubFlow             {pkg_stdports}
END_TopFlow      $ENDPRL1_SubFlow               {parallel_stdports}
END_TopFlow      ENDSHAREDRAILSMAX_SubFlow      {pkg_stdports}
END_TopFlow      ENDPREPRL2_SubFlow             {pkg_stdports}
END_TopFlow      $ENDPRL2_SubFlow               {parallel_stdports}
END_TopFlow      ENDPREPRL3_SubFlow             {pkg_stdports}
END_TopFlow      $ENDPRL3_SubFlow               {parallel_stdports}
END_TopFlow      ENDSHAREDRAILSMIN_SubFlow      {pkg_stdports}
END_TopFlow      ENDPREPRL4_SubFlow             {pkg_stdports}
END_TopFlow      $ENDPRL4_SubFlow               {parallel_stdports}
END_TopFlow      ENDCPUPKG_SubFlow              {cpupkg_stdports}
END_TopFlow      ENDGCDPKG_SubFlow              {gcdpkg_stdports}
END_TopFlow      ENDHUBPKG_SubFlow              {hubpkg_stdports}
END_TopFlow      ENDPCDPKG_SubFlow              {pcdpkg_stdports}
END_TopFlow      END_SubFlow                    {pkg_stdports}
END_TopFlow      ENDCPUVMAXPKG_SubFlow          {cpupkg_stdports}
END_TopFlow      ENDGCDVMAXPKG_SubFlow          {gcdpkg_stdports}
END_TopFlow      ENDHUBVMAXPKG_SubFlow          {hubpkg_stdports}
END_TopFlow      ENDPCDVMAXPKG_SubFlow          {pcdpkg_stdports}

LTTC_TopFlow     LTTCRAMP_SubFlow               {pkg_stdports}
LTTC_TopFlow     LTTCCOMMON_SubFlow             {pkg_stdports}
LTTC_TopFlow     LTTCCPUPKG_SubFlow             {cpupkg_stdports}
LTTC_TopFlow     LTTCGCDPKG_SubFlow             {gcdpkg_stdports}
LTTC_TopFlow     LTTCHUBPKG_SubFlow             {hubpkg_stdports}
LTTC_TopFlow     LTTCPCDPKG_SubFlow             {pcdpkg_stdports}
LTTC_TopFlow     LTTCSHAREDRAILSMIN1_SubFlow    {pkg_stdports}
LTTC_TopFlow     LTTCPREPRL0_SubFlow            {pkg_stdports}
LTTC_TopFlow     $LTTCPRL0_SubFlow              {parallel_stdports}
LTTC_TopFlow     LTTCSHAREDRAILSMAX_SubFlow     {pkg_stdports}
LTTC_TopFlow     LTTCPREPRL1_SubFlow            {pkg_stdports}
LTTC_TopFlow     $LTTCPRL1_SubFlow              {parallel_stdports}
LTTC_TopFlow     LTTCPOST_SubFlow               {pkg_stdports}

FACT_TopFlow     FACTRAMP_SubFlow               {pkg_stdports}
FACT_TopFlow     FACT_SubFlow                   rm2fm2 rm1fm1 r0f0 r3p:TPI_END_XXX_FACT
FACT_TopFlow     FACTPREFUSEBURN_SubFlow        {pkg_stdports}
FACT_TopFlow     FACTSHAREDRAILSNOM_SubFlow     {pkg_stdports}
FACT_TopFlow     FACTPREPRL0_SubFlow           {pkg_stdports}
FACT_TopFlow     $FACTPRL0_SubFlow              {parallel_stdports}
FACT_TopFlow     FACTPREPRL1_SubFlow           {pkg_stdports}
FACT_TopFlow     $FACTPRL1_SubFlow              {parallel_stdports}
FACT_TopFlow     FACTPOSTFUSEBURN_SubFlow       {pkg_stdports}
FACT_TopFlow     TPI_END_XXX::TPI_END_XXX_FACT      {pkg_stdports}

MAIN             START_TopFlow                  rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r2f:DCFF_SubFlow r3p:BEGIN_TopFlow r20f:FINAL_SubFlow r30f:FINAL_SubFlow r40f:FINAL_SubFlow r50f:FINAL_SubFlow r21f:FINAL_SubFlow r31f:FINAL_SubFlow r41f:FINAL_SubFlow r51f:FINAL_SubFlow
MAIN             HVBI_TopFlow                   {topf_stdports}
MAIN             BEGIN_TopFlow                  rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r2f:DCFF_SubFlow r3p:FACT_TopFlow r4f:PKGFF_SubFlow r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:HUBIPFF_SubFlow r50f:PCDIPFF_SubFlow r21f:CPUPKGFF_SubFlow r31f:GCDPKGFF_SubFlow r41f:HUBPKGFF_SubFlow r51f:PCDPKGFF_SubFlow
MAIN             SPEED_TopFlow                  {topf_stdports}
MAIN             END_TopFlow                    {topf_stdports}
MAIN             LTTC_TopFlow                   {topf_stdports}
MAIN             FACT_TopFlow                   rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r2f:DCFF_SubFlow r20f:FINAL_SubFlow r30f:FINAL_SubFlow r40f:FINAL_SubFlow r50f:FINAL_SubFlow r21f:FINAL_SubFlow r31f:FINAL_SubFlow r41f:FINAL_SubFlow r51f:FINAL_SubFlow
MAIN             FINAL_SubFlow                  rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f0 r1p1
MAIN             CPUIPFF_SubFlow                rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:CPUPKGFF_SubFlow r1f:CPUPKGFF_SubFlow
MAIN             GCDIPFF_SubFlow                rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:GCDPKGFF_SubFlow r1f:GCDPKGFF_SubFlow
MAIN             HUBIPFF_SubFlow                rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:HUBPKGFF_SubFlow r1f:HUBPKGFF_SubFlow
MAIN             PCDIPFF_SubFlow                rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:PCDPKGFF_SubFlow r1f:PCDPKGFF_SubFlow
MAIN             CPUPKGFF_SubFlow               rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r1f:FINAL_SubFlow
MAIN             GCDPKGFF_SubFlow               rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r1f:FINAL_SubFlow
MAIN             HUBPKGFF_SubFlow               rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r1f:FINAL_SubFlow
MAIN             PCDPKGFF_SubFlow               rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r1f:FINAL_SubFlow
MAIN             DCFF_SubFlow                   rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r1f:FINAL_SubFlow
MAIN             PKGFF_SubFlow                  rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:FINAL_SubFlow r1f:FINAL_SubFlow
MAIN             ALARM_SubFlow                  rm2fm2 rm1fm1 r0fm1
'''

### Init flow has been seperated into dielet, this section is for common module in the Init flow.
### Please put your module in the correct Init section.
### If your module is the 1st module of the section, please help remove the comment out to enable the section in the Init flow.
init_stdports = 'rm2fm2 rm1fm1 r0f0'
INIT_code = f'''
INIT_SubFlow               TPI_BASE_XXX::TPI_BASE_XXX_INIT              {init_stdports}
INIT_SubFlow               TPI_XIU_XXX::TPI_XIU_XXX_INIT                {init_stdports}
INIT_SubFlow               FUS_FLE_XXX::FUS_FLE_XXX_INIT                {init_stdports}
INIT_SubFlow               FUS_FACT_XXX::FUS_FACT_XXX_INIT              {init_stdports}
INIT_SubFlow               FUS_ISEED_XXX::FUS_ISEED_XXX_INIT              {init_stdports}
INIT_SubFlow               PTH_DIODE_XXX::PTH_DIODE_XXX_INIT                {init_stdports}
INIT_SubFlow               TPI_DEDC_XXX::TPI_DEDC_XXX_INIT              {init_stdports}
INIT_SubFlow               TPI_SKUCTRL_XXX::TPI_SKUCTRL_XXX_INIT  {init_stdports}

{INITCPUPKG_SubFlow}
{INITGCDPKG_SubFlow}
{INITHUBPKG_SubFlow}
{INITPCDPKG_SubFlow}
{INITCPU_SubFlow}
{INITGCD_SubFlow}
{INITHUB_SubFlow}
{INITPCD_SubFlow}

INITLAST_SubFlow           TPI_PUP_XXX::TPI_PUP_XXX_INIT              {init_stdports}
INITLAST_SubFlow           TPI_END_XXX::TPI_END_XXX_INIT                {init_stdports}

INIT         INIT_SubFlow          {init_stdports}
INIT         INITCPUPKG_SubFlow    {init_stdports}
INIT         INITGCDPKG_SubFlow    {init_stdports}
INIT         INITPCDPKG_SubFlow    {init_stdports}
INIT         INITHUBPKG_SubFlow    {init_stdports}
INIT         INITCPU_SubFlow       {init_stdports}
INIT         INITGCD_SubFlow       {init_stdports}
INIT         INITPCD_SubFlow       {init_stdports}
INIT         INITHUB_SubFlow       {init_stdports}
INIT         INITLAST_SubFlow      {init_stdports}
'''
