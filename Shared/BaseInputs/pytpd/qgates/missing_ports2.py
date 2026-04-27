#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures ports defined in input files (xml or json) are also defined in the mtpl.

Problem was found:
    Sent: Friday, June 2, 2023 11:09 AM
    Subject: CLK_MAIN_CXX is causing B9804 @ PHMROOM
    We have issue with CLK main causing B9804 INVALID_MISSING_PORT
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import JsonRead
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json
import re


class MissingPorts(QGateBase):

    def main(self):
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'config_file' in params and 'config_set' in params:
                filename = params['config_file']
                set = params['config_set']
                if '~' not in filename:
                    self.read_xml_failport(f'{self.tpobj.tpldir}/{filename}', set, ports, mod, item)

            elif 'ConfigFile' in params and 'ConfigSet' in params:
                filename = params['ConfigFile']
                set = params['ConfigSet']

                with open(f'{self.tpobj.tpldir}/{filename}', 'r', errors='replace') as f:
                    try:
                        json_object = json.load(f)
                    except BaseException:
                        log.info(
                            f"-w- Invalid {filename}, please fix json file syntax issue. Hint: A comma is not allowed "
                            f"at the end of a JSON object or array")
                        continue
                self.read_json_failport(f'{self.tpobj.tpldir}/{filename}', set, json_object, ports, mod, item)

            elif 'ScreenTestsFile' in params and ('ScreenTestSet' in params or 'ScreenTestName' in params):
                stfilename = params['ScreenTestsFile']
                sfilename = f'{self.tpobj.tpldir}/{stfilename}'
                if 'ScreenTestSet' in params:
                    sset = params['ScreenTestSet']
                else:
                    sset = params['ScreenTestName']

                if 'json' in sfilename:
                    try:
                        json_object = JsonRead(sfilename).load()
                    except BaseException:
                        log.info(
                            f"-w- Invalid {sfilename}, please fix json file syntax issue. Hint: A comma is not allowed "
                            f"at the end of a JSON object or array")
                        continue
                    self.read_screen_json_failport(sfilename, sset, ports, mod, item, json_object)
                else:
                    self.read_screen_failport(sfilename, sset, ports, mod, item)

            elif 'screen_tests_file' in params and 'screen_test_set' in params:
                stfilename = params['screen_tests_file']
                sfilename = f'{self.tpobj.tpldir}/{stfilename}'
                sset = params['screen_test_set']
                self.read_screen_failport(sfilename, sset, ports, mod, item)

    def read_screen_json_failport(self, ff, configset, ports, mod, item, json_object):
        fports = set()
        for keys, values in (json_object.items()):
            for keyval in values:
                if keyval['TestName'].lower() == configset.lower():
                    for row in keyval['TestConfig']:
                        if not (len(row) == 9):
                            continue
                        true = row[7]
                        false = row[8]
                        if true.isnumeric():
                            fports.add(true)
                        if false.isnumeric():
                            fports.add(false)

                    flag = 3
                    self.compare_port(fports, ff, configset, ports, mod, item, flag)
                    return fports

    def read_json_failport(self, ff, configset, json_object, ports, mod, item):
        failport_values = []

        for contents in json_object:
            if contents == configset:
                for iter in json_object[configset]:
                    for equation in json_object[configset][iter]:
                        if "FAILPORT" in equation:
                            failport_values.append(equation["FAILPORT"])
        fports = [i for n, i in enumerate(failport_values) if i not in failport_values[:n]]
        flag = '1'
        self.compare_port(fports, ff, configset, ports, mod, item, flag)
        return fports

    def read_xml_failport(self, ff, configset, ports, mod, instance):
        """
        Find FailPortLow, FailPortHigh given configset
        ('analog_config.ConfigList.[0].name', 'ANAPRB'),
        ('analog_config.ConfigList.[0].Config.Cores.Core.[3].FailPortLow', '8'),
        pprint(list(iter_dot_items(result)))

        :param ff: Given the xml
        :param configset: Specific ConfigSet value from TestInstance
        :return: set of port numbers
        """
        fports = set()
        try:
            result = xmlfunc.xml2dict(ff)
        except ElementTree.ParseError as e:
            self.add_error(213, mod,
                           f"Input xml for {mod} has error: {e}; Fix {basename(ff)}")
            return
        self.add_pass(213, mod)

        for top in result:
            for keyr, valuer in result.items():
                if 'ConfigList' in valuer:
                    for item in result[top]['ConfigList']:
                        if (len(item) < 4):
                            if item['name'] == configset:
                                # at this point we are in the specific ConfigList (eg. ANAPRB)
                                # pprint(list(iter_dot_items(item)))
                                for key in ('FailPortLow', 'FailPortHigh'):
                                    for res in find_dot_items(item, key, default=[]):
                                        fports.add(res)
        flag = '2'
        self.compare_port(fports, ff, configset, ports, mod, instance, flag)
        return fports

    def read_screen_failport(self, sfilename, sset, ports, mod, item):
        fports = set()
        found = 0
        with open(sfilename, "r", errors='replace') as sfile:
            for sfilelinev in sfile:
                sfileline = sfilelinev.rstrip()
                if 'START_SCREEN' in sfileline:
                    controlset = sfileline.split(':')[1].strip()
                    if sset.lower() == controlset.lower():
                        found = 1
                if found == 1 and '#' not in sfileline:
                    if ':' in sfileline and 'IP' not in sfileline:
                        if len(sfileline.split(':')) > 10:
                            sfileline1 = sfileline.split(':')[9].strip()
                            sfileline2 = sfileline.split(':')[10].strip()
                            if sfileline1.isnumeric():
                                # if not (sfileline1 in fports):
                                fports.add(sfileline1)
                            if sfileline2.isnumeric():
                                # if not (sfileline2 in fports):
                                fports.add(sfileline2)
                    if ';' in sfileline:
                        if len(sfileline.split(';')) > 10:
                            sfileline1 = sfileline.split(';')[9].strip()
                            sfileline2 = sfileline.split(';')[10].strip()
                            if sfileline1.isnumeric():
                                # if not (sfileline1 in fports):
                                fports.add(sfileline1)
                            if sfileline2.isnumeric():
                                # if not (sfileline2 in fports):
                                fports.add(sfileline2)
                if 'END_SCREEN' in sfileline and found == 1:
                    found = 0
                    flag = '3'
                    self.compare_port(fports, sfilename, sset, ports, mod, item, flag)
        return fports

    def compare_port(self, fports, file, cset, ports, mod, instance, flag):
        y = None
        ifile = file.split('/')[-1]
        for z in sorted(fports):
            if int(z) in ports:
                # pass case
                if flag == '1':
                    self.add_pass(211, mod)
                elif flag == '2':
                    self.add_pass(212, mod)
                else:
                    self.add_pass(213, mod)

            else:
                # fail case
                if flag == '1':
                    self.add_error(211, mod,
                                   (f"Input json file vs mtpl file mismatch: "
                                    f"Port{z} defined in json file but Not defined in mtpl file. "
                                    f"TestName: {mod}/{instance}, ConfigFile: {ifile} ConfigSet: {cset}"))

                elif flag == '2':
                    self.add_error(212, mod,
                                   (f"Input xml file vs mtpl file mismatch: "
                                    f"Port{z} defined in xml file but Not defined in mtpl file. "
                                    f"TestName: {mod}/{instance}, ConfigFile: {ifile} ConfigSet: {cset}"))

                else:
                    self.add_error(213, mod,
                                   (f"ScreenTest file vs mtpl file mismatch: "
                                    f"Port{z} defined in screentest file but Not defined in mtpl file. "
                                    f"TestName: {mod}/{instance}, ScreentestFile: {ifile} ScreentestSet: {cset}"))
                y = z  # for unittest
        if y:  # for unittest
            return y  # for unittest


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    MissingPorts(TestProgram(sys.argv[1]).pickle_init()).run()
