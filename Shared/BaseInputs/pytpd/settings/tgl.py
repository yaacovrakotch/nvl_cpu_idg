#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
from gadget.dictmore import TVPVConfigDict
from gadget.shell import IS_UNIX
from gadget.files import TempDir
import os
import re
import sys

cfg = TVPVConfigDict()
cfg.unittest_sample = ['FlowControl', 'SetFlowInfo']

# Checker configurations
cfg.ipcpu_subflows = """HVBICPU BEGCPU SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6 PSTCRSRH CCRF6 CCRF4 CCRF1
SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6 PSTCLRSRH CCLRF6 CCLRF4 CCLRF1
SATF1 SATF2 SATF3 SATF4 SATF5 SATF6 PSTATSRH CATF6 CATF4 CATF1
MAXCR MAXCLR MAXAT EDCCR EDCCLR EDCAT ENDCPU SPKLCPU IPFFCPU
CCRF2 CCRF3 CCRF5
CCLRF2 CCLRF3 CCLRF5
CATF2 CATF3 CATF5
PRLMVCPU
""".split()
cfg.ippch_subflows = """HVBIGT BEGGT PREGTSRH SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6 PSTGTSRH CGTF6 CGTF4 CGTF1 MAXGT EDCGT ENDGT SPKLGT IPFFGT
BEGBS SBSF1 SBSF2 SBSF3 PSTBSSRH CBSF3 CBSF1 MAXBS EDCBS ENDBS SPKLBS IPFFBS
HVBIIOE BEGIOE SPKLIOE EDCIOE IPFFIOE
CGTF2 CGTF3 CGTF5
CBSF2
PRLMVGCD PRLMVIOE
""".split()
cfg.pkg_subflows = """START BEGIN HVBISOC BEGSOC SSHDCF1 SSNF1 SSNF2 SSNF3 PSTSOCSRH CSNF3 CSNF2 CSNF1 ENDSOC EDCSOC SPKLSOC BEGCPUPKG BEGGTPKG BEGIOEPKG BEGBSPKG
INFCPU INFGT INFBS INFIOE
INFCPUGT INFCPUIOE INFCPUBS INFFFCPU INFFFGT INFFFIOE INFFFBS
ENDCPUPKG ENDGTPKG ENDIOEPKG ENDBSPKG SPKLSCRN END LTTC FACT FINAL
FFPKG FFCPU FFGT FFIOE FFBS DCFF THRFF
DEDCPKG DEDCCPU DEDCGT DEDCIOE DEDC
MAIN ALARM INIT LOTSTARTFLOW LOTENDFLOW TESTPLANSTARTFLOW TESTPLANENDFLOW
PRLFLGCPU PRLFLGGCD PRLFLGIOE
DSCPU DSBS DSGT DSIOE DSMAIN
POSTPRLCPUGT POSTPRLCPUIOE PREPRLCPUGT PREPRLCPUIOE PRLDIV0
""".split()
cfg.srhchk_subflows = """BEGCPU SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6 CCRF6 CCRF4 CCRF1
SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6 CCLRF6 CCLRF4 CCLRF1
SATF1 SATF2 SATF3 SATF4 SATF5 SATF6 CATF6 CATF4 CATF1
MAXCR MAXCLR MAXAT EDCCR EDCCLR EDCAT ENDCPU SPKLCPU IPFFCPU
CCRF2 CCRF3 CCRF5
CCLRF2 CCLRF3 CCLRF5
CATF2 CATF3 CATF5
BEGGT PREGTSRH SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6 CGTF6 CGTF4 CGTF1 MAXGT EDCGT ENDGT SPKLGT IPFFGT
BEGBS SBSF1 SBSF2 SBSF3 PSTBSSRH CBSF3 CBSF1 MAXBS EDCBS ENDBS SPKLBS IPFFBS
BEGIOE SPKLIOE EDCIOE IPFFIOE
CGTF2 CGTF3 CGTF5
CBSF2
""".split()  # parallel subflows for testplacechk
cfg.ipmin_subflows = """BEGCPU SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6 CCRF6 CCRF4 CCRF1
SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6 CCLRF6 CCLRF4 CCLRF1
SATF1 SATF2 SATF3 SATF4 SATF5 SATF6 CATF6 CATF4 CATF1
MAXCR MAXCLR MAXAT EDCCR EDCCLR EDCAT ENDCPU SPKLCPU IPFFCPU
CCRF2 CCRF3 CCRF5
CCLRF2 CCLRF3 CCLRF5
CATF2 CATF3 CATF5
PREGTSRH SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6 CGTF6 CGTF4 CGTF1 MAXGT EDCGT ENDGT SPKLGT IPFFGT
BEGBS SBSF1 SBSF2 SBSF3 PSTBSSRH CBSF3 CBSF1 MAXBS EDCBS ENDBS SPKLBS IPFFBS
BEGIOE SPKLIOE EDCIOE IPFFIOE
CGTF2 CGTF3 CGTF5
CBSF2
""".split()  # parallel subflows min lvls only, same as srhchk_subflows but without BEGGT, BEGGT runs at nom
cfg.srh_subflows = """SSHDCF1 SSNF1 SSNF2 SSNF3
SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6
SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6
SATF1 SATF2 SATF3 SATF4 SATF5 SATF6
SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6
SBSF1 SBSF2 SBSF3
""".split()  # srh only subflow, no scoreboarding here
cfg.chk_subflows = """CSNF3 CSNF2 CSNF1
CCRF6 CCRF4 CCRF1
CCLRF6 CCLRF4 CCLRF1
CATF6 CATF4 CATF1
CGTF6 CGTF4 CGTF1
CCRF2 CCRF3 CCRF5
CCLRF2 CCLRF3 CCLRF5
CATF2 CATF3 CATF5
CGTF2 CGTF3 CGTF5
CBSF3 CBSF1
CBSF2
""".split()  # chk only subflow, scoreboarding here and  guardbanding reqd tests

cfg.socchk_subflows = """CSNF3 CSNF2 CSNF1""".split()  # soc CHK subflows
cfg.gdiechk_subflows = """CGTF6 CGTF4 CGTF1 CGTF2 CGTF3 CGTF5""".split()  # gdie CHK subflows
cfg.cdiechk_subflows = """CCRF6 CCRF4 CCRF1 CCLRF6 CCLRF4 CCLRF1
CATF6 CATF4 CATF1 CCRF2 CCRF3 CCRF5
CCLRF2 CCLRF3 CCLRF5 CATF2 CATF3 CATF5""".split()  # cdie CHK subflows
cfg.admchk_subflows = """CBSF3 CBSF1 CBSF2""".split()  # adm/base CHK subflows

cfg.cdiebnmstart = '1'
cfg.gdiebnmstart = '2'
cfg.ioebnmstart = '3'
cfg.socbnmstart = '4'
cfg.admbnmstart = '5'

cfg.sccttrflows = """SSHDCF1 SSNF1 SSNF2 SSNF3 CSNF3 CSNF2 CSNF1
SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6 CCRF6 CCRF4 CCRF1
SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6 CCLRF6 CCLRF4 CCLRF1
SATF1 SATF2 SATF3 SATF4 SATF5 SATF6 CATF6 CATF4 CATF1
CCRF2 CCRF3 CCRF5
CCLRF2 CCLRF3 CCLRF5
CATF2 CATF3 CATF5
SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6 CGTF6 CGTF4 CGTF1
SBSF1 SBSF2 SBSF3 PSTBSSRH CBSF3 CBSF1
CGTF2 CGTF3 CGTF5
CBSF2
""".split()  # srh/chk cttr subflows for naming compliance

cfg.cdiesubflows = []
cfg.cdiesubflows.extend(cfg.ipcpu_subflows)
cfg.cdiesubflows.extend(['BEGCPUPKG', 'FFCPU', 'DEDCCPU'])

cfg.subflows = []
cfg.subflows.extend(cfg.ipcpu_subflows)
cfg.subflows.extend(cfg.ippch_subflows)
cfg.subflows.extend(cfg.pkg_subflows)

cfg.ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')
cfg.idutmods = """IP_CPU_BASE IP_PCH_BASE IP_CPU_CONCURRENT_FLOWS IP_PCH_CONCURRENT_FLOWS""".split()
# drv reset for hvbi infra, tpi modules for hvbi+idut infra: valid PKG modules in IP_ subflows that run ONLY in serial
cfg.idutinfras = """DRV_RESET_SXN TPI_BASE_IPCPU TPI_BASE_IPPCH TPI_ENDIPCPU_XXX TPI_ENDIPPCH_XXX TPI_DIESLCT_XXX TPI_GFXAGG_GXX""".split()
cfg.cttrchk_ignoremods = ('DUMMY SCN_CORE_C68 SCN_CORE_C68 SCN_CCF_C68 SCN_NONCCF_C68C SCN_NONCCF_C68K '
                          'SCN_ATOM_C68 SCN_CORE_C28 SCN_CCF_C28 SCN_NONCCF_C28C SCN_NONCCF_C28K '
                          'SCN_ATOM_C28 SCN_SOC_SXXK').split()


# valid SOC INFRA tests and infra module
cfg.socinfra = {'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'absent', 'p': '', 'l': '', 't': ''},
                'DRV_RESET_SXN::RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'absent', 'p': '', 'l': '', 't': ''},
                'DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE': {'att': 'absent', 'p': '', 'l': '', 't': ''},
                'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE': {'att': 'absent', 'p': '', 'l': '', 't': ''}  # ww2022_22.1
                # 'DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE': {'att': 'absent', 'p': '', 'l': '', 't': ''}
                # revert this after Astep
                }
cfg.simodule = 'DRV_RESET_SXN'

# important IP_CPU/IP_PCH DRV reset tests for PRL MV use, they must always exist in the TP
cfg.prlmvreqtest = {'DRV_RESET_CXX::RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_PHASE2': {'att': 'absent', 'p': '', 'l': '', 't': ''},
                    'DRV_RESET_GXX::RESET_X_FUNC_K_BEGGT_X_INF_X_X_LR_PHASE2_PRIME': {'att': 'absent', 'p': '', 'l': '', 't': ''}
                    }
cfg.prlmvdrvmods = ['DRV_RESET_CXX', 'DRV_RESET_GXX']

# valid DomainNames for MTL
cfg.fd_kill = """CORE ATOMC RING GT SOC""".split()
cfg.fd_edc = """CORE_EDC ATOMC_EDC RING_EDC GT_EDC SOC_EDC""".split()
cfg.fd = []
cfg.fd.extend(cfg.fd_kill)
cfg.fd.extend(cfg.fd_edc)

# boms to skip sherlock checkers
cfg.skipbom = """CLASS_MAGICBOM""".split()

# valid module/tests that can be ignored on dlvrchk() due to core-less resets
cfg.dlvrmodxcare = ['DRV_RESET_CXX', 'DRV_RESET_SXN']
cfg.dlvrtestxcare = """RESET_X_FUNC_E_BEGCPU_X_INF_X_X_BASIC_RESET_BBS RESET_X_FUNC_E_BEGCPU_X_INF_X_X_BOOTFSM_BBS
RESET_X_FUNC_E_BEGCPU_X_INF_X_X_LR_FUSE_OVERRIDE RESET_X_FUNC_E_BEGCPU_X_INF_X_X_LR_INFRA
RESET_X_FUNC_E_BEGCPU_X_INF_X_X_LR_INFRA_SPECKLE RESET_X_FUNC_E_BEGCPU_X_INF_X_X_LR_PHASE2_CORELESS
RESET_X_FUNC_E_BEGCPU_X_INF_X_X_MAINTAP_BBS RESET_X_FUNC_E_BEGCPU_X_INF_X_X_PHASE1_BBS
RESET_X_FUNC_E_BEGCPU_X_INF_X_X_TAPIDCODE_BBS RESET_X_FUNC_E_BEGCPU_X_INF_X_X_TAPLINK_BBS
RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_FUSE_OVERRIDE RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_INFRA
RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_PHASE2_CORELESS RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_PHASE2_PLACEHOLDER
RESET_X_FUNC_K_BEGCPU_X_INF_X_X_PHASE2_CORELESS_2D_SHMOO RESET_X_FUNC_K_BEGCPU_X_INF_X_X_PHASE2_CORELESS_2D_SHMOO_TIMING
RESET_X_FUNC_K_BEGCPU_X_INF_X_X_SHMOOTC RESET_X_FUNC_K_IPFFCPU_X_INF_X_X_LR_FUSE_OVERRIDE
RESET_X_FUNC_K_IPFFCPU_X_INF_X_X_LR_INFRA RESET_X_FUNC_K_IPFFCPU_X_INF_X_X_LR_PHASE2_CORELESS
RESET_X_FUNC_K_IPFFCPU_X_INF_X_X_PHASE2_CORELESS_2D_SHMOO RESET_X_FUNC_K_IPFFCPU_X_INF_X_X_PHASE2_CORELESS_2D_SHMOO_TIMING
RESET_X_FUNC_K_IPFFCPU_X_INF_X_X_SHMOOTC RESET_X_SB_E_BEGCPU_X_INF_X_X_DFX_BABYSTEPS_TAPLINK
RESET_X_SB_E_BEGCPU_X_INF_X_X_PH0_MAINTAP_BABYSTEPS RESET_X_SB_E_BEGCPU_X_INF_X_X_PH0_UNLOCK_BABYSTEPS
RESET_X_SB_E_BEGCPU_X_INF_X_X_PH1A_BOOTFSM_BABYSTEPS RESET_X_SB_E_BEGCPU_X_INF_X_X_PH1_BABYSTEPS
RESET_X_FUNC_K_HVBICPU_X_VNNAON_X_X_SOCINFRA_CPUGT RESET_X_FUNC_K_BEGCPUPKG_X_VNNAON_X_X_FELB_C68_MAX
RESET_X_FUNC_K_BEGCPUPKG_X_VNNAON_X_X_FELB_C68_MIN RESET_X_FUNC_K_BEGCPUPKG_X_VNNAON_X_X_FELB_C68_NOM
""".split()

# Required files to be checked, trigger if missing
cfg.reqdfiles = """./Reports/LTL_Files.zip""".split()

# vminTC truth table string for kill and edc settings
# field chart   f+0123456789
cfg.vminttstr = ['1111111111',  # srh/chk vmin kill under CDIE, non-CLR subflow, must care about Recovery* params, rmd!=NoRecovery
                 '1111211111',  # srh/chk vmin kill under CDIE, non-CLR subflow, must care about Recovery* params, rmd==NoRecovery
                 '1111111112',  # srh/chk vmin kill under CDIE, CLR subflow, must care about Recovery* params, rmd!=NoRecovery
                 '1111211112',  # srh/chk vmin kill under CDIE, CLR subflow, must care about Recovery* params, rmd==NoRecovery
                 '1111000012',  # srh/chk vmin kill under CDIE, this is empty Recovery* params and in CLR subflows
                 '1111000010',  # srh/chk vmin kill under GDIE/SOC, dont have Recovery* params
                 '1011111111',  # begcpu vmin kill under CDIE, non-CLR subflow, must care about Recovery* params, rmd!=NoRecovery
                 '0020111111',  # edc vmin #1 CDIE non-CLR subflow fmd=Input rmd=!NoRecovery scenario
                 '0020211111',  # edc vmin #1 CDIE non-CLR subflow fmd=Input rmd==NoRecovery scenario
                 '0000111111',  # edc vmin #1 CDIE non-CLR subflow fmd=None rmd=!NoRecovery scenario
                 '0000211111',  # edc vmin #1 CDIE non-CLR subflow fmd=None rmd==NoRecovery scenario
                 '0020111112',  # edc vmin #1 CDIE CLR subflow fmd=Input rmd=!NoRecovery scenario
                 '0020211112',  # edc vmin #1 CDIE CLR subflow fmd=Input rmd==NoRecovery scenario
                 '0000111112',  # edc vmin #1 CDIE CLR subflow fmd=None rmd=!NoRecovery scenario
                 '0000211112',  # edc vmin #1 CDIE CLR subflow fmd=None rmd==NoRecovery scenario
                 '0000000012',  # edc vmin #1 CDIE CLR subflow fmd=None scenario
                 '0000000011',  # edc vmin #1 CDIE non-CLR subflow fmd=None scenario
                 '0000000010',  # edc vmin #1 GDIE/SOC fmd=None scenario
                 '0121111111',  # edc vmin #2 scenario under CDIE non-CLR subflow, must care about Recovery* params !NoRecovery
                 '0121111112',  # edc vmin #2 scenario under CDIE CLR subflow, must care about Recovery* params !NoRecovery
                 '0121211111',  # edc vmin #2 scenario under CDIE non-CLR subflow, must care about Recovery* params NoRecovery
                 '0121211112',  # edc vmin #2 scenario under CDIE CLR subflow, must care about Recovery* params NoRecovery
                 '0121000012',  # edc vmin #2 scenario under CDIE, dont have Recovery* params and in CLR subflows
                 '0121000010',  # edc vmin #2 scenario under GDIE/SOC, dont have Recovery* params
                 '1021211101',  # max kill #1 scenario under CDIE non-CLR subflow, must care about Recovery* params
                 '1021211102',  # max kill #1 scenario under CDIE CLR subflow, must care about Recovery* params
                 '1001000002',  # max kill #1 scenario under CDIE CLR subflow, dont have Recovery* params
                 '1001000000',  # max kill #1 scenario under GDIE/SOC, dont have Recovery* params
                 '0020211101',  # max edc #1 scenario under CDIE non-CLR subflow, must care about Recovery* params
                 '0020211102',  # max edc #1 scenario under CDIE CLR subflow, must care about Recovery* params
                 '0000000002',  # max edc #1 scenario under CDIE CLR subflow, dont have Recovery* params
                 '0000000000'   # max edc #1 scenario under GDIE/SOC, dont have Recovery* params
                 ]

# valid MTL UPS domains
cfg.flowdomains = {'core': { 'name': 'CORE', 'domains': ['CR', 'CRX', 'CRU', 'CRUX'] },
                   'atom': { 'name': 'ATOMC', 'domains': ['AT', 'ATS'] },
                   'ring': { 'name': 'RING', 'domains': ['CLR', 'CLRS'] },
                   'gt': { 'name': 'GT', 'domains': ['GT'] },
                   'soc': { 'name': 'SOC', 'domains': ['SAQ', 'SAN', 'SACD', 'SAF', 'SAVPU', 'SAME', 'SAPS', 'SAIS', 'SAAT', 'SCDS', 'SVPUS', 'SMES', 'SATS'] }
                   }
cfg.upsvoltagetargets = """ATOM1 ATOM0 CCF CORE0 CORE1 CORE2 CORE3 CORE4 CORE5 VCCGT_HC VCCSA_HC""".split()

# approved PDEs to build ReleaseCandidate TPs for raw copy action
cfg.pdxpdes = """kjanders fecarpio chenchen mmcruz ddharmar vsgatcha sgourshe nhassanr mtignaci
njohanse wladeau oliverni damienpe taipham dannypha justintr vsgatcha srty holeary jsgarcia""".split()

# trace trc exe path
cfg.consoletrc = 'I:\\tpvalidation\\engtools\\tptools\\mtl\\trace_trc\\latest\\ConsoleTRC\\bin\\Debug\\ConsoleTRC.exe'

# windows to unix path conversion
cfg.win2unix['I:/program/1273/eng/hdmtpats'] = '/intel/hdmxpats'
cfg.win2unix['I:/program/1274/eng/hdmtpats'] = '/intel/hdmxpats'

cfg.win2unix['I:/program/1276/eng/hdmtpats/mtc'] = '/intel/hdmxpats/mtlcpu'
cfg.win2unix['I:/program/1276/prod/hdmtpats/mtc'] = '/intel/hdmxpats/mtlcpu'

cfg.win2unix['I:/program/1278/eng/hdmtpats/arh'] = '/intel/hdmxpats/arl_cpu'
cfg.win2unix['I:/program/1278/prod/hdmtpats/arh'] = '/intel/hdmxpats/arl_cpu'

cfg.win2unix['I:/program/1278/eng/hdmtpats/nvl_nhh'] = '/intel/hdmxpats/nvl_hub'
cfg.win2unix['I:/program/1278/prod/hdmtpats/nvl_nhh'] = '/intel/hdmxpats/nvl_hub'

cfg.win2unix['I:/program/1278/eng/hdmtpats/nvl_ngs'] = '/intel/hdmxpats/nvl_gcd'
cfg.win2unix['I:/program/1278/prod/hdmtpats/nvl_ngs'] = '/intel/hdmxpats/nvl_gcd'

cfg.win2unix['I:/program/1278/eng/hdmtpats/nvl_ngh'] = '/intel/hdmxpats/nvl_gcd'
cfg.win2unix['I:/program/1278/prod/hdmtpats/nvl_ngh'] = '/intel/hdmxpats/nvl_gcd'

cfg.win2unix['I:/program/1278/eng/hdmtpats/nvl_ngp'] = '/intel/hdmxpats/nvl_gcd'
cfg.win2unix['I:/program/1278/prod/hdmtpats/nvl_ngp'] = '/intel/hdmxpats/nvl_gcd'

cfg.win2unix['I:/program/1278/eng/hdmtpats/nvl_ncx'] = '/intel/hdmxpats/nvl_cpu'
cfg.win2unix['I:/program/1278/prod/hdmtpats/nvl_ncx'] = '/intel/hdmxpats/nvl_cpu'

cfg.win2unix['I:/program/1278/eng/hdmtpats/ptl_ptu'] = '/intel/hdmxpats/ptl'
cfg.win2unix['I:/program/1278/prod/hdmtpats/ptl_ptu'] = '/intel/hdmxpats/ptl'

# cfg.win2unix['I:/program/1278/eng/hdmtpats/nvl_ngh'] = '/intel/hdmxpats/nvl_cpu'
# cfg.win2unix['I:/program/1278/prod/hdmtpats/nvl_ngh'] = '/intel/hdmxpats/nvl_cpu'

cfg.win2unix['I:/program/1001/prod/hdmtpats/mtg'] = '/intel/hdmxpats/mtlgcd'
cfg.win2unix['I:/program/1001/eng/hdmtpats/mtg'] = '/intel/hdmxpats/mtlgcd'

cfg.win2unix['I:/program/1001/prod/hdmtpats/arc'] = '/intel/hdmxpats/mtlacpu'
cfg.win2unix['I:/program/1001/eng/hdmtpats/arc'] = '/intel/hdmxpats/mtlacpu'

cfg.win2unix['I:/hdmxpats'] = '/intel/hdmxpats'
cfg.win2unix['I:/hbipats'] = '/intel/hbipats'
cfg.unix2win_sort['/intel/hdmxpats/tgl'] = 'I:/program/1274/eng/hdmtpats/tgl'
cfg.unix2win_sort['/intel/hdmxpats/tlp'] = 'I:/program/1273/eng/hdmtpats/tlp'
cfg.unix2win_class['/intel'] = 'I:'

# These are paths that contain softlinks to real disks. Used with path_win_unix.py.
cfg.path_root_links = {'/intel/engineering/dev': ['MIG'],   # MIG is excluded!
                       '/intel': [],
                       '/intel/engtools': [],
                       '/intel/engtools/tptools': [],
                       '/intel/hdmxpats': [],
                       '/intel/hdmxprogs': [],
                       }

# Other configurations
if IS_UNIX:
    cfg.root = '/intel/tpvalidation/engtools/tptools/mtl'
    if not os.path.exists(cfg.root):
        cfg['root'] = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
else:
    iroot = 'I:/tpvalidation/engtools/tptools/mtl'
    jroot = 'J:/tpvalidation/engtools/tptools/mtl'     # alternative for sort
    if os.path.exists(jroot):
        cfg.root = jroot
    else:
        cfg.root = iroot

# Testinstance naming convention: https://wiki.ith.intel.com/display/ITSpdxtp/MTL+Test+Instance+Naming+Convention
# class names is ti_name1 (w/ speedflow) and ti_name2 (w/o speedflow)
cfg.ti_name1 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E)_([A-Z0-9]+)_(X|\d+)_([A-Z0-9]+)_(X|MAX|MIN|NOM|F\d)_(X|\d{4})(_[A-Z0-9_]+)?_(\*|\d+)$')
cfg.ti_name2 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E)_([A-Z0-9]+)_(X|\d+)_([A-Z0-9]+)_(X|MAX|MIN|NOM|F\d)_(X|\d{4})(_[A-Z0-9_]+)?$')
#                                1           2         3          4         5         6        7               8             9          10         11
cfg.ti_elem = '              test_cat   partition   testtype   kill_edc   subflow patratio voltage_domain    corner         freq      userinput   speedflow'    # Do not change these names! The names here are key to dictionary used in code

# sort&class names is ti_name3 (w/ speedflow) and ti_name4 (w/o speedflow)
cfg.ti_name3 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$')
cfg.ti_name4 = re.compile(r'^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_\w+)?$')
#                                1           2         3           4         5            6         7                     8                         9            10 (no speedflow at sort)
# notes: element 10: sort does not have speedflow

cfg.testname_pos = 91       # starting position where _ is for pattern testname (This works for both MTL and TGL)
if not os.path.exists(cfg.root):
    pickle_dir = TempDir(samename='pickle_tp', delete=False).name()       # create the pickle_tp dir one time in temp folder (sticky)
    cfg.pickle_dir = os.path.realpath(pickle_dir)
else:
    cfg.pickle_dir = f'{cfg.root}/pickle_tp'
cfg.ut_dir = f'{cfg.root}/unittests'
cfg.log_dir = f'{cfg.root}/logs'
cfg.pingroup = '/p/pde/tvpv/tgl/db/tp_pingroups'
cfg.plan_waivers = f'{cfg.root}/plan_waivers/waiver_tgl.py'
cfg.pcar3_root = '/p/pde/tvpv/mtl/pcar3'     # Needed for querytid

# Below is per-module to levels-pin-name mapping for TidDb
cfg.module2power_map = '''
ARR_CCF:             FIVR_SA_VT_VLC, FIVR_CCF_VT_VLC
ARR_CCF_RAMPDOWN:    FIVR_CCF_VT_VLC
ARR_CORE:            FIVR_C0_VT_VLC
ARR_CORE_RAMPDOWN:   FIVR_C0_VT_VLC, FIVR_CCF_VT_VLC
ARR_DE:              FIVR_SA_VT_VLC
ARR_GT1:             FIVR_GT_VT_VLC
ARR_IPU:             FIVR_SA_VT_VLC
ARR_MBIST:           VCC_ST_HC, FIVR_SA_VT_VLC, FIVR_IOE_VT_VLC, FIVR_ION_VT_VLC
ARR_MBIST_VMAX:      VCC_ST_HC, FIVR_SA_VT_VLC
CLK_ADPLL_ALL:       FIVR_ION_VT_VLC, FIVR_IOE_VT_VLC
CLK_DLCPLL_ALL:      FIVR_ION_VT_VLC, FIVR_IOE_VT_VLC
CLK_FLL_ALL:         FIVR_ION_VT_VLC, FIVR_IOE_VT_VLC
CLK_LJPLL_ALL:       FIVR_ION_VT_VLC,FIVR_IOE_VT_VLC
FUN_CORE:            FIVR_C0_VT_VLC
FUN_CORE_RAMPDOWN:   FIVR_C0_VT_VLC
FUN_DE:              FIVR_SA_VT_VLC
FUN_GT:              FIVR_GT_VT_VLC
FUN_GT_THR:          FIVR_GT_VT_VLC
FUN_SA:              FIVR_SA_VT_VLC, FIVR_CCF_VT_VLC, FIVR_SA_VT_VLC, FIVR_CCF_VT_VLC
MIO_DDR_AC:          FIVR_SA_VT_VLC
PFUS_UNITINFO:       c_vccprimfuse_1p05_prog
PTH_FIVR_OPSC:       FIVR_SA_VT_VLC
PTH_FIVR_TRIMC:      VCC_IN_HC
SCN_CCF:             FIVR_CCF_VT_VLC
SCN_CORE:            FIVR_C0_VT_VLC
SCN_DE:              FIVR_SA_VT_VLC
SCN_GT:              FIVR_GT_VT_VLC, FIVR_SA_VT_VLC, FIVR_CCF_VT_VLC
SCN_IPU:             FIVR_SA_VT_VLC
SCN_SOC:             FIVR_SA_VT_VLC
'''

cfg.AUTO_OFF()
