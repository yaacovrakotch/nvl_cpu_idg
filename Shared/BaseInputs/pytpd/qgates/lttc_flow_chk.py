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
        target = "LTTC_SubFlow"
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
        checks if Binnings are Bin9091
        Vmin test, VoltageConverter param must not have 'override'
        Vmin test that are not VMIN tests(MAX), allows override BUT ForwardingMode should be 'Input'
        checks for the following required VminTC params:
            ForwardingMode = None
            LimitGuardband = 31mv
            CornerIdentifiers = empty
            StartVoltages = D.RF
            EndVoltageLimits = D.RF
            ExecutionMode = SearchWithScoreboard
            if TestMode = MultiVmin, VoltageTargets > 1
                Testmode = SingleVmin, VoltageTargets = 1
        Error Code Guide:
        300:  Invalid LTTC test name (No LTTC in name)
        301:  LTTC test fail port not using Bin91
        302:  VMinTC test used as Static not as Speedflow
        303:  LTTC VminTC Min test not setting ForwardingMode to 'None'
        304:  LTTC VminTC Min test LimitGuardBand not set to 31mV
        305:  LTTC Test(Min/Max) CornerIdentifier is not empty
        306:  LTTC VminTC Min test is not using the DFF (D.RF) data as values for StartVoltages and EndVoltageLimit parameters
        307:  LTTC VminTC Test (Min/Max) is not setting ExecutionMode param to SearchWithScoreboard
        308:  LTTC VminTC Test (Min/Max) is in SingleVmin TestMode but has more than 1 VoltageTarget value
        309:  LTTC VminTC Max test not setting ForwardingMode to 'Input'
        310:  LTTC Test is not using a unique BaseNumber
        311:  LTTC Test is using the same plist as its CHK counterpart. It should be unique plist name
        312:  LTTC Speedflow is allowing downbins. No downbinning allowed
        313:  LTTC Singlepass tests that use GSDS tokens for Start and End Voltages is not  matching
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
                for i in range(len(valuemod)):
                    if item in valuemod[i]:
                        if not('LTTC' in item):
                            self.add_error(300, mod, f'Invalid LTTC test name, {item} has no LTTC in test name')
                        else:
                            self.add_pass(300, mod)
                            for port, bins in ports.items():
                                if port == -1 or port == -2 or port == 999:
                                    continue
                                else:
                                    if (ports[port]['PassFail']) == 'Fail' and 'SetBin' in bins:
                                        binname = ports[port]['SetBin'].split('.')[1]
                                        if not (binname.startswith('b909191') or binname.startswith('b909494')):
                                            if binname.startswith('b9097'):
                                                self.add_pass(301, mod)
                                            else:
                                                self.add_error(301, mod, f'{item}: {binname}: fail port {port}: is not using bin91/bin94')
                                        else:
                                            self.add_pass(301, mod)
                            if 'VminTC' == params['TEMPLATE']:
                                if 'VoltageConverter' in params and 'StartVoltages' in params and \
                                        'EndVoltageLimits' in params:
                                    sv = params['StartVoltages']
                                    ev = params['EndVoltageLimits']
                                    vc = params['VoltageConverter']
                                    if '--overrides' in vc or (sv == ev and not(sv.startswith('D.RF') or
                                                                                ev.startswith('D.RF'))):
                                        if sv.startswith('LTTC'):
                                            self.add_pass(313, mod)
                                        if 'ForwardingMode' in params:
                                            if params['ForwardingMode'].lower() == 'input':
                                                self.add_pass(309, mod)
                                            else:
                                                if sv.startswith('LTTC') or ev.startswith('LTTC'):
                                                    continue
                                                else:
                                                    self.add_error(309, mod,
                                                                   f'LTTC MAX test {item} is not setting ForwardingMode'
                                                                   f' to \'Input\'')
                                    elif sv.startswith('D.RF') and ev.startswith('D.RF'):
                                        if 'ForwardingMode' in params:
                                            if params['ForwardingMode'].lower() == 'none':
                                                self.add_pass(303, mod)
                                            else:
                                                self.add_error(303, mod,
                                                               f'LTTC MIN test {item} is not setting ForwardingMode '
                                                               f'to \'None\'')
                                    elif sv.startswith('LTTC') or ev.startswith('LTTC'):
                                        if ',' in sv:
                                            spltsv = sv.split(',')
                                        else:
                                            spltsv = sv

                                        if (',') in ev:
                                            spltev = ev.split(',')
                                        else:
                                            spltev = ev
                                        if spltsv == spltev:
                                            self.add_pass(313, mod)
                                        else:
                                            self.add_error(313, mod,
                                                           f'LTTC test: {item} are using GSDS tokens for Start '
                                                           f'and End Voltages that do not match. Please fix')

                                if 'LimitGuardband' in params:
                                    if params['LimitGuardband'].lower() == '31mv':
                                        self.add_pass(304, mod)
                                    else:
                                        lg = params['LimitGuardband']
                                        vc = params['VoltageConverter']
                                        if '--overrides' in vc:
                                            self.add_pass(304, mod)
                                        elif 'StartVoltages' in params and 'EndVoltageLimits' in params:
                                            sv = params['StartVoltages']
                                            ev = params['EndVoltageLimits']
                                            if sv == ev and not(sv.startswith('D.RF') or ev.startswith('D.RF')):
                                                self.add_pass(304, mod)
                                            else:
                                                self.add_error(304, mod,
                                                               f'LTTC test {item} LimitGuardband is set to \'{lg}\' '
                                                               f'not \'31mv\'')
                                if 'CornerIdentifiers' in params:
                                    if params['CornerIdentifiers'] == '':
                                        self.add_pass(305, mod)
                                    else:
                                        self.add_error(305, mod,
                                                       f'CornerIdentifiers param for LTTC test {item} is NOT EMPTY')
                                if 'StartVoltages' in params and 'EndVoltageLimits' in params:
                                    if params['StartVoltages'].startswith('D.RF') and \
                                            params['EndVoltageLimits'].startswith('D.RF'):
                                        self.add_pass(306, mod)
                                    else:
                                        lastfour = item[-4:]
                                        if lastfour.isdigit():
                                            sv = params['StartVoltages']
                                            ev = params['EndVoltageLimits']
                                            vc = params['VoltageConverter']
                                            if '--overrides' in vc:
                                                self.add_pass(306, mod)
                                            elif sv == ev and not(sv.startswith('D.RF') or ev.startswith('D.RF')):
                                                self.add_pass(306, mod)
                                            elif sv.startswith('LTTC') or ev.startswith('LTTC'):
                                                continue
                                            else:
                                                self.add_error(306, mod, f'LTTC test {item} \'StartVoltages\' set to {sv} and/or '
                                                               f'\'EndVoltageLimits\' set to {ev} '
                                                                         f'is/are NOT set to DFF value ')

                                if 'ExecutionMode' in params:
                                    if params['ExecutionMode'] == 'SearchWithScoreboard':
                                        self.add_pass(307, mod)
                                    else:
                                        self.add_error(307, mod, f'LTTC test {item} should set \'ExecutionMode\' '
                                                                 f'to \'SearchWithScoreboard\'')
                                if 'VoltageTargets' in params and 'TestMode' in params:
                                    if ',' in params['VoltageTargets']:
                                        vt = params['VoltageTargets']
                                        if params['TestMode'] == 'MultiVmin':
                                            self.add_pass(308, mod)
                                        elif params['TestMode'] == 'SingleVmin':
                                            self.add_error(308, mod, f'LTTC test {item} is using SingleVmin Testmode '
                                                                     f'but has more than 1 VoltageTarget value: {vt}')
                                    else:
                                        vt = params['VoltageTargets']
                                        if params['TestMode'] == 'SingleVmin':
                                            self.add_pass(308, mod)
                                        elif params['TestMode'] == 'MultiVmin':
                                            self.add_error(308, mod, f'LTTC test {item} is using MultiVmin Testmode '
                                                                     f'but only has 1 VoltageTarget value: {vt}')
                                """
                                if 'VoltageConverter' in params:
                                    vc = params['VoltageConverter']
                                    if '_VMIN_' in item:
                                        if not('--override' in vc):
                                            self.add_pass(309, mod)
                                        else:
                                            self.add_error(309, mod, f'LTTC VMIN test {item} is using overrides '

                                                                     f'on \'VoltageConverter\' param')
                                    else:
                                        if 'ForwardingMode' in params:
                                            fm = params['ForwardingMode']
                                            if 'input' == fm.lower():
                                                self.add_pass(309,mod)
                                            else:
                                                self.add_error(309, mod, f'LTTC Max test {item} \'ForwardingMode\' '
                                                                         f'should be set to \'Input\'')
                                """
                                if 'ScoreboardBaseNumber' in params:
                                    lbn = params['ScoreboardBaseNumber']
                                    lbasenum.setdefault(item, []).append([lbn])
        return lbasenum, fbasenum

    def basenum(self, modinst):
        """Base  number should be unique"""
        ftp_bn = dict()
        ltp_bn = dict()

        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'ScoreboardBaseNumber' in params and not('LTTC' in item):
                tsbn = params['ScoreboardBaseNumber']
                ftp_bn.setdefault(item, []).append(tsbn)
            if 'ScoreboardBaseNumber' in params and 'LTTC' in item:
                lsbn = params['ScoreboardBaseNumber']
                ltp_bn.setdefault(item, []).append(lsbn)

        for lkeys, lvalues in ltp_bn.items():
            if lvalues in ftp_bn.values():
                for i in range(len(modinst)):
                    if lkeys in modinst[i]:
                        module = str(modinst[i]).split(',')[0].split('\'')[1]
                        self.add_error(310, module, f'LTTC {lkeys} is using a NON-UNIQUE Base number: {lvalues}')
            else:
                for i in range(len(modinst)):
                    if lkeys in modinst[i]:
                        module = str(modinst[i]).split(',')[0].split('\'')[1]
                        self.add_pass(310, module)

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
                                            self.add_error(312, mod, f'LTTC test {item} port{port} is '
                                                                     f'downbinning to {goto}.'
                                                                     f'  LTTC Downbins are not allowed')
                                        else:
                                            self.add_pass(312, mod)

    def plistuniq(self, modinst):
        """CHK test counterpart should be unique plist with its LTTC counterpart"""

        lplist = dict()
        fplist = dict()

        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'VminTC' == params['TEMPLATE'] and 'patlist' in params:
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
                    if fsub.startswith('C'):
                        if fvalues == lvalues:
                            #print(fkeys, fvalues, lkeys, lvalues)
                            for i in range(len(modinst)):
                                if lkeys in modinst[i]:
                                    module = str(modinst[i]).split(',')[0].split('\'')[1]
                                    self.add_error(311, module, f'LTTC {lkeys} is using same plist {fvalues} as {fkeys}')
                        else:
                            for j in range(len(modinst)):
                                module = str(modinst[j]).split(',')[0].split('\'')[1]
                                self.add_pass(311, module)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    LTTCFlowChk(TestProgram(sys.argv[1]).pickle_init()).run()
