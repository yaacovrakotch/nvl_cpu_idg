#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks if SOC INFRA tests are in the TP
"""
import setenv      # must be first in the imports
import re
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from mod.setting import cfg
import sys
import json


class SocInfra(QGateBase):

    def main(self):
        """
        SOC INFRA Check, Verify that all tests exist
        :param valid_si: {'DRV_RESET_SXN::INFCPU': {'att': 'absent', 'p': 'infcpugt_list', 'l': '', 't': ''},
                          'DRV_RESET_SXN::INFGT': {'att': 'absent', 'p': 'infcpugt_list', 'l': '', 't': ''},
                          'DRV_RESET_SXN::INFIOE': {'att': 'absent', 'p': 'infcpuioe_list', 'l': '', 't': ''}}
        :param locinfrachk: {'DRV_RESET_SXN::INFCPU': {'att': 'present', 'p': 'infcpugt_list', 'l': 'lvl', 't': 'tim'},
                             'DRV_RESET_SXN::INFGT': {'att': 'present', 'p': 'infcpugt_list', 'l': 'lvl', 't': 'tim'},
                             'DRV_RESET_SXN::INFIOE': {'att': 'present', 'p': 'infcpuioe_list', 'l': 'lvl', 't': 'tim'}}
        :return: None
        """

        simodule = 'DRV_RESET_SXN'
        socinfra = {
            'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'absent', 'p': '', 'l': '',
                                                                                 't': ''},
            'DRV_RESET_SXN::RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'absent', 'p': '', 'l': '',
                                                                                't': ''},
            'DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE': {'att': 'absent', 'p': '', 'l': '',
                                                                               't': ''},
            'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE': {'att': 'absent', 'p': '', 'l': '',
                                                                                     't': ''}  # ww2022_22.1
        }
        valid_si = socinfra  # valid PKG SOC Infra tests
        module_si = simodule  # valid PKG SOC Infra module
        for keys in valid_si.keys():
            f = 0
            m, t = keys.split('::')
            for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
                if m == mod and t == test:
                    f = 1
                    self.add_pass(133, mod)
                    continue
            if f == 0:
                self.add_error(133, m, f'Required Infra Test {t} BYPASSED OR NOT FOUND!')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    SocInfra(TestProgram(sys.argv[1]).pickle_init()).run()
