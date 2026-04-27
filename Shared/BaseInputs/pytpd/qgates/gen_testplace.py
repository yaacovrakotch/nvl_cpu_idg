#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks for Module/Test instance placement in Flow
148: IP_CPU placed in PKG subflow
149: IP_PCH placed in PKG subflow
236: IP_PCU placed in IP_PCH subflow
237: IP_PCH placed in IP_CPU subflow
126: PKG test placed in subflow not valid for PKG
127: Test is inside an invalid Subflow
128: Test's subflow name does not match the subflow it is placed into
"""
import setenv      # must be first in the imports
import re
import glob
from os.path import dirname, basename, exists
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip, get_param, CheckerLog
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from itertools import chain
import sys
import json


class TestSFPlacement(QGateBase):

    def main(self):
        """
        Read each module+testname and check if testname subflow is matching to the subflow it is placed
        :param testtrace: {('mod', 'testname'): ['data1', 'data2] }
        :param ipcpuflows: ['BEGCPU', 'ENDCPU']
        :param ippchflows: ['BEGGT', 'BEGIOE']
        :param pkgflows: ['MAIN', 'ALARM']
        :param ipcpu: ['ARR_CORE_CXX', 'FUN_CORE_CXX']
        :param ippch: ['PSCN_SCN_IXX']
        :return: None
        """
        testtrace = {}
        ipcpu = set()  # set of ipcpu modules in all stpls
        ippch = set()  # set of ippch modules in all stpls
        ipcpu.update({basename(dirname(x)) for x in self.tpobj.get_all_mtpl_from_stpl('IP_CPU')})  # ipcpu modules
        ippch.update({basename(dirname(x)) for x in self.tpobj.get_all_mtpl_from_stpl('IP_PCH')})  # ippch modules
        idutmods = """IP_CPU_BASE IP_PCH_BASE IP_CPU_CONCURRENT_FLOWS IP_PCH_CONCURRENT_FLOWS""".split()
        ignore_tests = ('FlowControl', 'SetFlowInfo', 'TORCH_PgmRules')
        ipcpuflows = """HVBICPU BEGCPU SCRF1 SCRF2 SCRF3 SCRF4 SCRF5 SCRF6 PSTCRSRH CCRF6 CCRF4 CCRF1
        SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF5 SCLRF6 PSTCLRSRH CCLRF6 CCLRF4 CCLRF1
        SATF1 SATF2 SATF3 SATF4 SATF5 SATF6 PSTATSRH CATF6 CATF4 CATF1
        MAXCR MAXCLR MAXAT EDCCR EDCCLR EDCAT ENDCPU SPKLCPU IPFFCPU
        CCRF2 CCRF3 CCRF5
        CCLRF2 CCLRF3 CCLRF5
        CATF2 CATF3 CATF5
        PRLMVCPU
        PRL0CIFLGCPU
        SATCLR1 SATCLR2 SATCLR3 SATCLR4 SATCLR5 SATCLR6
        CATCLR1 CATCLR2 CATCLR3 CATCLR4 CATCLR5 CATCLR6
        MAXCRLO MAXATCLR
        PRL0CGFLGCPU PRL1CIFLGCPU PRL2CGFLGCPU PRL2CIFLGCPU PRL3CGFLGCPU PRL3CIFLGCPU PRL4CGFLGCPU PRL4CIFLGCPU PRL1CGFLGCPU
        CCRF6C01 CCRF6C23 CCRF6C45
        LTTCCPUIP
        PCCCLRF1 PCCCRF1 PCMAXCLR PCMAXCRLO
        LTTC HVBICPUF6
        """.split()
        ippchflows = """HVBIGT BEGGT PREGTSRH SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SGTF6 PSTGTSRH CGTF6 CGTF4 CGTF1 MAXGT EDCGT ENDGT SPKLGT IPFFGT
        BEGBS SBSF1 SBSF2 SBSF3 PSTBSSRH CBSF3 CBSF1 MAXBS EDCBS ENDBS SPKLBS IPFFBS
        HVBIIOE BEGIOE BEGIOE2 BEGIOE3  SPKLIOE EDCIOE IPFFIOE
        CGTF2 CGTF3 CGTF5
        CBSF2
        PRLMVGCD PRLMVIOE
        PRL0CIFLGIOE PRL0CGFLGGCD PRL1CIFLGIOE PRL2CIFLGIOE PRL3CIFLGIOE PRL4CIFLGIOE PRL1CGFLGGCD PRL2CGFLGGCD PRL3CGFLGGCD PRL4CGFLGGCD
        LTTCGTIP LTTCIOEIP
        LTTC
        """.split()
        pkgflows = """START BEGIN HVBISOC BEGSOC SSHDCF1 SSNF1 SSNF2 SSNF3 PSTSOCSRH CSNF3 CSNF2 CSNF1 ENDSOC EDCSOC SPKLSOC BEGCPUPKG BEGGTPKG BEGIOEPKG BEGBSPKG
        INFCPU INFGT INFBS INFIOE
        INFCPUGT INFCPUIOE INFCPUBS INFFFCPU INFFFGT INFFFIOE INFFFBS
        ENDCPUPKG ENDGTPKG ENDIOEPKG ENDBSPKG SPKLSCRN END LTTC FACT FINAL
        FFPKG FFCPU FFGT FFIOE FFBS DCFF THRFF
        DEDCPKG DEDCCPU DEDCGT DEDCIOE DEDC
        MAIN ALARM INIT LOTSTARTFLOW LOTENDFLOW TESTPLANSTARTFLOW TESTPLANENDFLOW
        PRLFLGCPU PRLFLGGCD PRLFLGIOE
        DSCPU DSBS DSGT DSIOE DSMAIN
        POSTPRLCPUGT POSTPRLCPUIOE PREPRLCPUGT PREPRLCPUIOE PRLDIV0
        SERDIV0 SERDIV1 PRLDIV12 PRLDIV11 PRLDIV10 PRLDIV9 PRLDIV3 PRLDIV2 PRLDIV1
        LTTCSOC LTTCGTPKG LTTCCPUPKG LTTCIOEPKG LTTCGTINF LTTCCPUINF LTTCIOEINF
        HVBICPUPKG HVBIIOE HVBIGT INFCPUPKG HVBIIOEPKG
        LTTC
        """.split()
        idutinfras = """DRV_RESET_SXN TPI_BASE_IPCPU TPI_BASE_IPPCH TPI_ENDIPCPU_XXX TPI_ENDIPPCH_XXX TPI_DIESLCT_XXX TPI_GFXAGG_GXX""".split()

        sf_148 = 'PASS'
        sf_149 = 'PASS'
        sf_236 = 'PASS'
        sf_237 = 'PASS'
        sf_126 = 'PASS'
        sf_127 = 'PASS'

        for mod, test, trc in self.tpobj.mtpl.iter_flows('MAIN', traceinfo=True):
            testtrace[(mod, test)] = trc
        for mod, test in testtrace:
            if not test.startswith(ignore_tests) and mod not in idutmods:
                sf = self.gen_subflow(test, mod)

                target = '%s::%s_%s' % (mod, mod, sf)  # TPIE specific mod::mod_subflow convention

                mod2 = '%s::%s_' % (mod, mod)
                if 'NYET' in target:  # this will get flagged in the _sfchk() routine
                    continue
                elif target in testtrace[mod, test]:  # test subflow param matches subflow placement in tpl
                    if mod in ipcpu and sf in ipcpuflows:  # pass: pure ipcpu
                        continue
                    elif mod in ippch and sf in ippchflows:  # pass: pure ippch
                        continue
                    elif mod not in ipcpu and mod not in ippch and sf in pkgflows:  # pass: pure pkg
                        continue
                    elif mod not in ipcpu and mod not in ippch and mod in idutinfras:  # and sf not in scf:
                        continue  # valid: TPI_ PKG module in IP subflows ex HVBI*
                    elif mod in ipcpu and sf in pkgflows and mod in idutinfras:  # and sf not in scf:
                        continue  # valid: TPI_ ipcpu module in PKG subflows
                    elif mod in ippch and sf in pkgflows and mod in idutinfras:  # and sf not in scf:
                        continue  # valid: TPI_ ippch module in PKG subflows
                    elif mod in ipcpu and sf in pkgflows and mod not in idutinfras:
                        self.add_error(148, mod, f'Test:{test} is IP_CPU scope but is placed in subflow:{sf} that is for PKG testing')
                        sf_148 = 'FAIL'

                    elif mod in ippch and sf in pkgflows and mod not in idutinfras:
                        self.add_error(149, mod, f'Test:{test} is IP_PCH scope but is placed in subflow:{sf} that is for PKG testing')
                        sf_149 = 'FAIL'

                    elif mod in ipcpu and sf in ippchflows:  # fail: ipcpu mod in ippch subflow
                        self.add_error(236, mod, f'Test:{test} is IP_CPU scope but is placed in subflow:{sf} that is for IP_PCH testing')
                        sf_236 = 'FAIL'

                    elif mod in ippch and sf in ipcpuflows:  # ippch: mod in ipcpu subflow
                        self.add_error(237, mod, f'Test:{test} is IP_PCH scope but is placed in subflow:{sf} that is for IP_CPU testing')
                        sf_237 = 'FAIL'

                    elif mod not in ipcpu and mod not in ippch and sf not in pkgflows:  # pkg: mod in ip_ subflow
                        self.add_error(126, mod, f'Test:{test} is PKG scope but is placed in subflow:{sf} that is not valid for PKG testing')
                        sf_126 = 'FAIL'

                    else:  # unlikely scenario: test subflow and current subflow match but subflow is not valid|approved
                        self.add_error(127, mod, f'Test:{test} inside invalid subflow:{sf} that might be currently in use for debug')
                        sf_127 = 'FAIL'

                else:  # test subflow param mismatch subflow placement in tpl
                    for i in testtrace[mod, test]:

                        if i.startswith(mod2):
                            csx = i.split(mod2)[1]  # current subflow
                            if "_" in csx:
                                cs = csx.split("_")[1]
                            else:
                                cs = csx
                            if cs in sf:
                                self.add_pass(128, mod)
                            else:
                                self.add_error(128, mod, f'Test:{test} with subflow:{sf} in tname is actually placed in subflow:{cs}')
                    continue
            if sf_148 == 'PASS':
                self.add_pass(148, mod)
            if sf_149 == 'PASS':
                self.add_pass(149, mod)
            if sf_236 == 'PASS':
                self.add_pass(236, mod)
            if sf_237 == 'PASS':
                self.add_pass(237, mod)
            if sf_126 == 'PASS':
                self.add_pass(126, mod)
            if sf_127 == 'PASS':
                self.add_pass(127, mod)
        return  # pragma: no cover

    def gen_subflow(self, test, mod):
        """
        This function reads the testname and returns the subflow portion; 5th field
        :param test: EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001
        :return: sf  # returns the subflow part of the testname, ex: SCRF1
        """
        ti_name3 = re.compile(r"^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_[A-Z0-9_]+)?_(\*|\d+)$")
        ti_name4 = re.compile(r"^([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(K|E|X)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(X|[VF]?MAX|[VF]?MIN|[VF]?NOM|F\d)_(X|[LHT]FM|\d+)(_\w+)?$")

        t3 = ti_name3.search(test)
        t4 = ti_name4.search(test)
        ts = re.compile(r"([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\S+)")  # relaxed SF check
        if t3:
            sf = t3.group(5)
        elif t4:
            sf = t4.group(5)
        elif re.search("[a-z]", test):
            sf = 'NYET'
            self.add_error(208, mod, f'Upper Case check failed for Test: {mod}::{test}')
        else:  # relaxed regex to discount tests that have correct subflow but wrong ti_name convention
            f = ts.search(test)
            if f:
                sf = f.group(5)
            else:
                sf = 'NYET'
        return sf


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TestSFPlacement(TestProgram(sys.argv[1]).pickle_init()).run()
