#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Template for checking PsuedoVmin forwarding is enabled for Qual Test:
https://wiki.ith.intel.com/display/ITSpdxtp/NVL+QUAL+Location+Implementation+Details
Checkes to make sure vmin templates have their StartVoltagesForRetry and StartVoltagesOffsets
set to uservars that point to a TOS rule to enable or disable appropriately

Algorithm:
    for each test in TP
        if template is a vmin template
            check if the test has one of the parameterts used for Psuedo Vmin Forwarding
            if parameter is present, but not set correctly -> add an error
            if parameter is present and set to the correct value -> add a pass

"""
import sys
import setenv
import re

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint


class PseudoVminChecker(QGateBase):
    WIKI_SITE = 'https://wiki.ith.intel.com/display/ITSpdxtp/NVL+QUAL+Location+Implementation+Details'
    SHARED = "__shared__::"
    USERVAR_COLLECTION = 'QNRTpRuleShared'
    USERVAR_COLLECTION_QNR = 'QNRUsrvShared'
    TEST_MODE_PARAM = 'TestMode'
    FORWARDING_MODE_PARAM = 'ForwardingMode'
    FREQUENCY_REGEX = r'\w*'
    REGEX_DOT = r'\.'
    REGEX_HVM_VALUE = r'\s*(""|\[(\s*""\s*,?)+\])'

    START_VOLTAGES_RETRY_PARAM = 'StartVoltagesForRetry'
    START_VOLTAGES_RETRY_VALUE = f'{SHARED}{USERVAR_COLLECTION}.If_PseudoVminForwarding({SHARED}{USERVAR_COLLECTION_QNR}.{START_VOLTAGES_RETRY_PARAM} , "")'
    START_VOLTAGES_RETRY_VALUE_REGEX = re.compile(rf'.*{USERVAR_COLLECTION}\.If_PseudoVminForwarding.*\(.*{USERVAR_COLLECTION_QNR}\.{START_VOLTAGES_RETRY_PARAM}{FREQUENCY_REGEX}.*,{REGEX_HVM_VALUE}.*\).*')
    START_VOLTAGES_RETRY_VALUE_F5 = f'{SHARED}{USERVAR_COLLECTION}.If_PseudoVminForwarding({SHARED}{USERVAR_COLLECTION_QNR}.{START_VOLTAGES_RETRY_PARAM}F5 , "")'
    START_VOLTAGES_RETRY_VALUE_MULTI = f'{SHARED}{USERVAR_COLLECTION}.If_PseudoVminForwarding({SHARED}{USERVAR_COLLECTION_QNR}.{START_VOLTAGES_RETRY_PARAM}F5 ,["","",""])'
    START_VOLTAGES_RETRY_VALUE_MO = '(_MTT(__shared__) :: QNRTpRuleShared.If_PseudoVminForwarding ( (_MTT(__shared__) :: _MTT(QNRUsrvShared.StartVoltagesForRetryF5)) , ([ "" , "" , "" ]) ))'

    START_VOLTAGES_OFFSETS_PARAM = 'StartVoltagesOffset'
    START_VOLTAGES_OFFSETS_VALUE = f'{SHARED}{USERVAR_COLLECTION}.If_PseudoVminForwarding({SHARED}{USERVAR_COLLECTION_QNR}.{START_VOLTAGES_OFFSETS_PARAM} , "")'
    START_VOLTAGES_OFFSETS_VALUE_REGEX = re.compile(rf'.*{USERVAR_COLLECTION}\.If_PseudoVminForwarding.*\(.*{USERVAR_COLLECTION_QNR}\.{START_VOLTAGES_OFFSETS_PARAM}{FREQUENCY_REGEX}.*,{REGEX_HVM_VALUE}.*\).*')
    START_VOLTAGES_OFFSETS_VALUE_F5 = f'{SHARED}{USERVAR_COLLECTION}.If_PseudoVminForwarding({SHARED}{USERVAR_COLLECTION_QNR}.{START_VOLTAGES_OFFSETS_PARAM}F5 , "")'
    START_VOLTAGES_OFFSETS_VALUE_MULTI = f'{SHARED}{USERVAR_COLLECTION}.If_PseudoVminForwarding({SHARED}{USERVAR_COLLECTION_QNR}.{START_VOLTAGES_OFFSETS_PARAM}F5 , ["","",""])'
    START_VOLTAGES_OFFSETS_VALUE_MO = '(_MTT(__shared__) :: QNRTpRuleShared.If_PseudoVminForwarding ( (_MTT(__shared__) :: _MTT(QNRUsrvShared.StartVoltagesOffsetF5)) , ([ "" , "" , "" ]) ))'

    def main(self):
        """Entry point of checker"""
        all_instances = self.tpobj.mtpl.iter_flows('MAIN', idict=True)

        for module, testname, params in all_instances:
            if 'VminTC' in params['TEMPLATE'] and ('_FMIN' in testname or '_ENDHUB_' in testname):
                continue
            if ("vmin" in params['TEMPLATE'].lower() and
                    self.TEST_MODE_PARAM in params.keys() and
                    (params[self.TEST_MODE_PARAM] == 'SingleVmin' or params[self.TEST_MODE_PARAM] == 'MultiVmin') and
                    self.FORWARDING_MODE_PARAM in params.keys() and
                    (params[self.FORWARDING_MODE_PARAM] == 'Input' or params[self.FORWARDING_MODE_PARAM] == 'InputOutput')):

                if self.START_VOLTAGES_RETRY_PARAM in params.keys():
                    match = self.START_VOLTAGES_RETRY_VALUE_REGEX.match(params[self.START_VOLTAGES_RETRY_PARAM])
                    if match:
                        self.add_pass(253, module)
                    else:
                        log.info(f'-i- QGate253: {testname} {self.START_VOLTAGES_RETRY_PARAM}:')
                        log.info(f'    From: [{params.get(self.START_VOLTAGES_RETRY_PARAM)}]')
                        log.info(f'    To:   [{self.START_VOLTAGES_RETRY_VALUE_REGEX}]')
                        self.add_error(253, module, f'{testname} needs to set {self.START_VOLTAGES_RETRY_PARAM} to {self.START_VOLTAGES_RETRY_VALUE} or with F* added to the end.')

                if self.START_VOLTAGES_OFFSETS_PARAM in params.keys():
                    match = self.START_VOLTAGES_OFFSETS_VALUE_REGEX.match(params[self.START_VOLTAGES_OFFSETS_PARAM])
                    if match:
                        self.add_pass(253, module)
                    else:
                        log.info(f'-i- QGate253: {testname} {self.START_VOLTAGES_OFFSETS_PARAM}:')
                        log.info(f'    From: [{params.get(self.START_VOLTAGES_OFFSETS_PARAM)}]')
                        log.info(f'    To:   [{self.START_VOLTAGES_OFFSETS_VALUE_REGEX}]')
                        self.add_error(253, module, f'{testname} needs to set {self.START_VOLTAGES_OFFSETS_PARAM} to {self.START_VOLTAGES_OFFSETS_VALUE} or with F* added to the end.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    PseudoVminChecker(TestProgram(sys.argv[1]).pickle_init()).run()
