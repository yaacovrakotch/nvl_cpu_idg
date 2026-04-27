#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures ports defined in input files (xml or json) are also defined in the mtpl.

Problem was found:
    Sent: Friday, June 2, 2023 11:09 AM
    Subject: CLK_MAIN_CXX is causing B9804 @ PHMROOM
    We have issue with CLK main causing B9804 INVALID_MISSING_PORT
"""
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

                with open(f'{self.tpobj.tpldir}/{filename}', 'r') as f:
                    try:
                        json_object = json.load(f)
                    except BaseException:
                        log.info(f"-w- Invalid {filename}, please fix json file syntax issue. Hint: A comma is not allowed at the end of a JSON object or array")
                        continue
                self.read_json_failport(f'{self.tpobj.tpldir}/{filename}', set, json_object, ports, mod, item)
#            print("RETURN", filename, set)
#        yield(filename, set)
#        print("LAST", filename, set)
#        return(filename, set)

    def read_json_failport(self, ff, configset, json_object, ports, mod, item):
        failport_values = []

        for contents in json_object:
            if contents == configset:
                for iter in json_object[configset]:
                    for equation in json_object[configset][iter]:
                        if "FAILPORT" in equation:
                            failport_values.append(equation["FAILPORT"])
        fports = [i for n, i in enumerate(failport_values) if i not in failport_values[:n]]
        self.compare_port(fports, ff, configset, ports, mod, item)
        return(fports)

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

        self.compare_port(fports, ff, configset, ports, mod, instance)
        return fports

    def compare_port(self, fports, file, cset, ports, mod, instance):
        ifile = file.split('/')[-1]
        for z in fports:
            if int(z) in ports:
                # pass case
                if 'json' in ifile:
                    self.add_pass(211, mod)
                else:
                    self.add_pass(212, mod)

            else:
                # fail case
                if 'json' in ifile:
                    self.add_error(211, mod,
                                   (f"Input json file vs mtpl file mismatch: "
                                    f"Port{z} defined in json file but Not defined in mtpl file. "
                                    f"TestName: {mod}/{instance}, ConfigFile: {ifile} ConfigSet: {cset}"))

                if 'xml' in ifile:
                    self.add_error(212, mod,
                                   (f"Input xml file vs mtpl file mismatch: "
                                    f"Port{z} defined in json file but Not defined in mtpl file. "
                                    f"TestName: {mod}/{instance}, ConfigFile: {ifile} ConfigSet: {cset}"))
                return z   # for unittest


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    MissingPorts(TestProgram(sys.argv[1]).pickle_init()).run()
