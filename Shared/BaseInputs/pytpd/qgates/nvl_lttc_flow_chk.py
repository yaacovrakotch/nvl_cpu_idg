#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Various LTTC related checks. See docstring of each of the routines
"""
import os

import setenv      # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json


class LTTCFlowChk(QGateBase):

    def main(self):
        lttc_conts = dict()
        modinst = []
        progflow = self.tpobj.get_final_mtpl()
        dd = self.tpobj.mtpl.get_instance_to_subflows()
        target = "LTTC_TopFlow"
        for module_instance, subflows in dd.items():
            if target in subflows:
                lttc_conts.setdefault(module_instance[0], []).append([module_instance[1]])
                modinst.append(module_instance)
        self.vmintc(lttc_conts)
        self.basenum(modinst)
        self.plistuniq(modinst)
        self.downbin(modinst)

    def vmintc(self, lttc_conts):
        """Bin91 for TPI_VCC_MIMS and Digitalcontents/VminTC
        checks if SCN, ARR and FUN LTTC contents are using VminTC
        checks if these tests in  the LTTC subflow have LTTC in name
        checks TPI_VCC_MIMS test in LTTC subflow has LTTC in name
        checks if Binnings are Bin9094
        Vmin test, VoltageConverter param must not have 'override'
        Vmin test that are not VMIN tests(MAX), allows override BUT ForwardingMode should be 'Input'
        checks for the following required VminTC params:
            ForwardingMode = Input
            LimitGuardband = 31mv
            CornerIdentifiers = empty
            StartVoltages = D.RF
            EndVoltageLimits = D.RF
            ExecutionMode = SearchWithScoreboard
            if TestMode = MultiVmin, VoltageTargets > 1
                Testmode = SingleVmin, VoltageTargets = 1
        Error Code Guide:
        350:  Invalid LTTC test name (No LTTC in name)
        351:  LTTC test fail port not using Bin91
        352:  VMinTC test used as Static not as Speedflow
        353:  LTTC VminTC Min test not setting ForwardingMode to 'Input'
        354:  LTTC VminTC Min test LimitGuardBand not set to 31mV
        355:  LTTC Test(Min/Max) CornerIdentifier is not empty
        356:  LTTC VminTC Min test is not using the DFF (D.RF) data as values for StartVoltages and EndVoltageLimit parameters and must be equal
              Updated 10/10/2025 based from Inputs of MO that these params does not apply to Static Tests (Functional/Scoreboard)
        357:  LTTC VminTC Test (Min/Max) is not setting ExecutionMode param to SearchWithScoreboard
        358:  LTTC VminTC Test (Min/Max) is in SingleVmin TestMode but has more than 1 VoltageTarget value
        359:  LTTC VminTC Max test not setting ForwardingMode to 'Input' or Vmin Test should not use --override
        360:  LTTC Test is not using a unique BaseNumber
        361:  LTTC Test is using the same plist as its CHK counterpart. It should be unique plist name
        362:  LTTC Speedflow is allowing downbins. No downbinning allowed
        363:  LTTC test should have RecoveryMode to 'NoRecovery'
              Updated 10/10/2025 based on MO feedback that Default is also a valid Recoverymode for LTTC VminTC tests
        """
        lbasenum = dict()
        fbasenum = dict()
        spltsv = []
        spltev = []
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'ScoreboardBaseNumber' in params and not('LTTC' in item):
                tbn = params['ScoreboardBaseNumber']
                fbasenum.setdefault(item, []).append([tbn])

            if (mod in lttc_conts.keys() and 'VminTC' == params['TEMPLATE']) or (mod in lttc_conts.keys() and mod.startswith('TPI_VCC_MIMS')):
                valuemod = lttc_conts[mod]
                if 'X_FFSEARCH' in item:
                    continue
                for i in range(len(valuemod)):
                    if item in valuemod[i]:
                        if not('LTTC' in item):
                            self.add_error(350, mod, f'Invalid LTTC test name, {item} has no LTTC in test name')
                        else:
                            self.add_pass(350, mod)
                            for port, bins in ports.items():
                                if port == -1 or port == -2 or port == 999:
                                    continue
                                else:
                                    if (ports[port]['PassFail']) == 'Fail' and 'SetBin' in bins:
                                        binname = ports[port]['SetBin']
                                        if not binname.startswith('b94'):
                                            if binname.startswith('b97'):
                                                self.add_pass(351, mod)
                                            else:
                                                self.add_error(351, mod, f'{item}: {binname}: fail port {port}: is not using bin94')
                                        else:
                                            self.add_pass(351, mod)
                                    else:
                                        self.add_pass(351, mod)

                            if 'VminTC' == params['TEMPLATE']:
                                tm = params['TestMode']
                                if 'ForwardingMode' in params:
                                    if params['ForwardingMode'].lower() == 'input' and 'output' not in params[
                                            'ForwardingMode'].lower():
                                        self.add_pass(353, mod)
                                    else:
                                        self.add_error(353, mod,
                                                       f"LTTC MIN test {item} is not setting ForwardingMode to 'Input' but set to {params['ForwardingMode']}")

                                else:
                                    if not(tm == 'Functional' or tm == 'Scoreboard'):
                                        self.add_error(353, mod, f'LTTC test {item} is missing ForwardingMode param.  Please follow LTTC Guidelines')

                                if 'VoltageConverter' in params and 'StartVoltages' in params and \
                                        'EndVoltageLimits' in params:
                                    sv = params['StartVoltages']
                                    ev = params['EndVoltageLimits']
                                    vc = params['VoltageConverter']
                                    # if '--overrides' in vc or (sv == ev and not(sv.startswith('D.RF') or ev.startswith('D.RF'))):
                                    if '--overrides' in vc:
                                        if 'VMAX' in item or 'MAX' in item:
                                            self.add_pass(359, mod)
                                        else:
                                            tm = params['TestMode']
                                            if not ('Functional' == tm or 'Scoreboard' == tm):
                                                self.add_error(359, mod, f'LTTC VMIN test {item} is using override in VoltageTarget param value')
                                            else:
                                                self.add_pass(359, mod)

                                if 'LimitGuardband' in params and 'ForwardingMode' in params:
                                    if params['LimitGuardband'].lower() == '31mv' or params['LimitGuardband'].lower() == '0.031':
                                        if params['ForwardingMode'].lower() == 'input':
                                            self.add_pass(354, mod)
                                    else:
                                        tm = params['TestMode']
                                        if not('Functional' == tm or 'Scoreboard' == tm):
                                            lg = params['LimitGuardband']
                                            self.add_error(354, mod, f'LTTC test {item} LimitGuardband is set to \'{lg}\' not \'31mv\'')
                                        else:
                                            self.add_pass(354, mod)
                                else:
                                    if 'LimitGuardband' not in params and not (tm == 'Scoreboard' or tm == 'FUnctional'):
                                        self.add_error(354, mod, f'LTTC test {item} is missing the LimitGuardband parameter.  Please follow LTTC Guidelines')

                                if 'CornerIdentifiers' in params:
                                    if params['CornerIdentifiers'] == '':
                                        self.add_pass(355, mod)
                                    else:
                                        self.add_error(355, mod,
                                                       f'CornerIdentifiers param for LTTC test {item} is NOT EMPTY')

                                if 'StartVoltages' in params and 'EndVoltageLimits' in params:
                                    if params['StartVoltages'].startswith('D.RF') and \
                                            params['EndVoltageLimits'].startswith('D.RF'):
                                        if params['StartVoltages'] == params['EndVoltageLimits']:
                                            self.add_pass(356, mod)
                                        else:
                                            tm = params['TestMode']
                                            if 'Functional' == tm or 'Scoreboard' == tm:
                                                self.add_pass(356, mod)
                                            else:
                                                self.add_error(356, mod, f"The DFF values used by {item} for StartVoltage: {params['StartVoltages']} and EndVoltageLimits: {params['EndVoltageLimits']} are not the same")
                                    else:
                                        if 'RF' in params['StartVoltages'] and 'RF' in params['StartVoltages']:
                                            if params['StartVoltages'] == params['EndVoltageLimits']:
                                                self.add_pass(356, mod)
                                            else:
                                                tm = params['TestMode']
                                                if 'Functional' == tm or 'Scoreboard' == tm:
                                                    self.add_pass(356, mod)
                                                else:
                                                    self.add_error(356, mod, f"The DFF values used by {item} for StartVoltage: {params['StartVoltages']} and EndVoltageLimits: {params['EndVoltageLimits']} are not the same")
                                        else:
                                            tm = params['TestMode']
                                            if 'Functional' == tm or 'Scoreboard' == tm:
                                                self.add_pass(356, mod)
                                            else:
                                                self.add_error(356, mod,
                                                               f"LTTC test {item} \'StartVoltages\' set to {params['StartVoltages']} and/or "
                                                               f"\'EndVoltageLimits\' set to {params['EndVoltageLimits']} "
                                                               f'is/are NOT set to DFF value ')
                                else:
                                    if not(tm == 'Scoreboard' or tm == 'Functional') and ('StartVoltages' not in params or 'EndVoltageLimits' not in params):
                                        self.add_error(356, mod, f'LTTC test {item} is either missing the StartVoltages or(both) EndVoltageLimits params.  Please follow LTTC Guidelines')

                                if 'ExecutionMode' in params:
                                    if params['ExecutionMode'] == 'SearchWithScoreboard':
                                        self.add_pass(357, mod)
                                    else:
                                        self.add_error(357, mod, f'LTTC test {item} should set \'ExecutionMode\' '
                                                                 f'to \'SearchWithScoreboard\'')
                                else:
                                    if not(tm == 'Scoreboard' or tm == 'Functional'):
                                        self.add_error(357, mod, f'LTTC test {item} is missing the ExecutionMode param.  Please follow LTTC Guidelines')

                                if 'VoltageTargets' in params and 'TestMode' in params:
                                    if ',' in params['VoltageTargets']:
                                        vt = params['VoltageTargets']
                                        if params['TestMode'] == 'MultiVmin':
                                            self.add_pass(358, mod)
                                        elif params['TestMode'] == 'SingleVmin':
                                            self.add_error(358, mod, f'LTTC test {item} is using SingleVmin Testmode '
                                                                     f'but has more than 1 VoltageTarget value: {vt}')
                                    else:
                                        vt = params['VoltageTargets']
                                        if params['TestMode'] == 'SingleVmin':
                                            self.add_pass(358, mod)
                                        elif params['TestMode'] == 'MultiVmin':
                                            self.add_error(358, mod, f'LTTC test {item} is using MultiVmin Testmode '
                                                                     f'but only has 1 VoltageTarget value: {vt}')

                                if 'VoltageConverter' in params:
                                    tm = params['TestMode']
                                    if not('Functional' == tm or 'Scoreboard' == tm):
                                        vc = params['VoltageConverter']
                                        if 'VMAX' in item or 'MAX' in item:
                                            if '--override' in vc:
                                                self.add_pass(359, mod)
                                            else:
                                                self.add_error(359, mod, f'LTTC MAX test {item} should be using overrides '

                                                                         f'on \'VoltageConverter\' param')
                                        # else:
                                            if 'ForwardingMode' in params:
                                                fm = params['ForwardingMode']
                                                if 'input' == fm.lower() and 'output' not in fm.lower():
                                                    self.add_pass(359, mod)
                                                else:
                                                    self.add_error(359, mod, f'LTTC Max test {item} \'ForwardingMode\' '
                                                                             f'should be set to \'Input\'')
                                if 'RecoveryMode' in params:
                                    rcv = params['RecoveryMode']
                                    if 'norecovery' == rcv.lower() or 'default' == rcv.lower():
                                        self.add_pass(363, mod)
                                    else:
                                        self.add_error(363, mod, f'LTTC test {item} is not setting RecoveryMode to "NoRecovery" or "Default" ')
                                else:
                                    if not(tm == 'Scoreboard' or tm == 'Functional'):
                                        self.add_error(365, mod, f'LTTC test {item} is missing the RecoveryMode parameter.  Please follow LTTC Guidelines')

                                if 'ScoreboardBaseNumber' in params:
                                    lbn = params['ScoreboardBaseNumber']
                                    lbasenum.setdefault(item, []).append([lbn])

        return lbasenum, fbasenum

    def basenum(self, modinst):
        """Base  number should be unique"""
        ftp_bn = dict()
        ltp_bn = dict()

        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            # if 'ScoreboardBaseNumber' in params and not('LTTC' in item):
            if 'BaseNumbers' in params and not ('LTTC' in item):
                # tsbn = params['ScoreboardBaseNumber']
                tsbn = params['BaseNumbers']
                ftp_bn.setdefault(item, []).append(tsbn)
            # if 'ScoreboardBaseNumber' in params and 'LTTC' in item:
            if 'BaseNumbers' in params and 'LTTC' in item:
                # lsbn = params['ScoreboardBaseNumber']
                lsbn = params['BaseNumbers']
                ltp_bn.setdefault(item, []).append(lsbn)

        for lkeys, lvalues in ltp_bn.items():
            if lvalues in ftp_bn.values():
                for i in range(len(modinst)):
                    if lkeys in modinst[i]:
                        module = str(modinst[i]).split(',')[0].split('\'')[1]
                        self.add_error(360, module, f'LTTC {lkeys} is using a NON-UNIQUE Base number: {lvalues}')
            else:
                for i in range(len(modinst)):
                    if lkeys in modinst[i]:
                        module = str(modinst[i]).split(',')[0].split('\'')[1]
                        self.add_pass(360, module)

    def downbin(self, modinst):
        """TrialAction"""

        lsflow = dict()
        fsflow = dict()
        i = 1
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'VminTC' == params['TEMPLATE']:
                if'LTTC' in item:
                    last4 = item[-4:]
                    if last4.isdigit():
                        genname = item[:-5]
                        for port, bin in ports.items():
                            if port == 0 or port == 2 or port == 3:
                                if 'GoTo' in bin:
                                    goto = ports[port]['GoTo']
                                    nlast4 = goto[-4:]
                                    if nlast4.isdigit():
                                        ngenname = goto[:-5]
                                        if genname == ngenname:
                                            self.add_error(362, mod, f'LTTC test {item} port{port} is '
                                                                     f'downbinning to {goto}.'
                                                                     f'  LTTC Downbins are not allowed')
                                        else:
                                            self.add_pass(362, mod)
                    else:
                        self.add_pass(362, mod)

    def plistuniq(self, modinst):
        """CHK test counterpart should be unique plist with its LTTC counterpart"""

        lplist = dict()
        fplist = dict()

        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'VminTC' == params['TEMPLATE'] and ('patlist' in params or 'Patlist' in params):
                if 'LTTC' in item:
                    plist = params['patlist']
                    lplist.setdefault(item, []).append(plist)
                else:
                    plist2 = params['patlist']
                    fplist.setdefault(item, []).append(plist2)

        for lkeys, lvalues in lplist.items():
            first4 = '_'.join(lkeys.split('_', 4)[:4])
            rest4 = lkeys.split('_', 5)[5]
            for fkeys, fvalues in fplist.items():
                if first4 in fkeys and rest4 in fkeys:
                    fsub = fkeys.split('_')[4]
                    # if fsub.startswith('C'):
                    # if fvalues == lvalues:
                    if fvalues and lvalues and fvalues[0] == lvalues[0]:
                        # print(fkeys, fvalues, lkeys, lvalues)
                        for i in range(len(modinst)):
                            if lkeys in modinst[i]:
                                module = str(modinst[i]).split(',')[0].split('\'')[1]
                                self.add_error(361, module, f'LTTC {lkeys} is using same plist {fvalues} as {fkeys}')
                    else:
                        for j in range(len(modinst)):
                            module = str(modinst[j]).split(',')[0].split('\'')[1]
                            if 'TPI_' in module or 'YBS' in module:
                                continue
                            self.add_pass(361, module)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    LTTCFlowChk(TestProgram(sys.argv[1]).pickle_init()).run()
