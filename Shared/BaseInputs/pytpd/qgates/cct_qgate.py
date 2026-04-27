#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures cct modules are up to date (in cases where source modules are updated)
Contact Alan Richardson and Gustavo Zumbado
"""
import sys
import setenv

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import json
import re
from gadget.sepshelve import SqlDict
from gadget.strmore import indent
from os.path import exists


class CCTSync(QGateBase):

    def read_cct_cfg(self):
        """
        Read cct cfg - contains the grouping, module, instance, and params for checking
        :return: False if missing cfg
        """
        self.cfg = f'{self.tpobj.envdir}/InputFiles/cct_qgate_config.json'
        if not exists(self.cfg):
            return False
        with open(self.cfg) as fh:
            self.cct_cfg = json.load(fh)
        self.cct_list = []
        for group, mod_inst_param in self.cct_cfg.items():
            for module, inst_param in mod_inst_param.items():
                for instance, param_list in inst_param.items():
                    self.cct_list.append((group, module, instance))
        return True

    def main(self):
        """Entry point of checker"""

        # Get the module, instance, and params from the config file. If there's no params file, just return (cct must not be enabled)
        if not self.read_cct_cfg():
            #            self.add_error(218, module, f'{self.cfg} is missing! Contact cct module owner for this TP PR.')
            return
        # open the db
        bom = basename(self.tpobj.envdir)
        self.valid_dict_path = f'{self.tpobj.envdir}/InputFiles'

        self.db_cct = SqlDict(f'{self.valid_dict_path}/{bom}.cct.sqldict')   # This contains the params from the last "write" call - the valid values expected by cct
        # dict structure: {"group::module::instance": "multi-line-string-valid-params"}
        # "write" option
        # It must be run on the "new cct mv"
        #  Puts the parameters from the dependent modules into the dict, which then needs to be checked into the TP repo as part of the CCT PR
        if '-write' in sys.argv:
            write_mode = True
        else:
            write_mode = False

        # get all of the data from the program
        all_instances = self.tpobj.mtpl.iter_flows('MAIN', bypass=False, edict=True)
        # create a large regex first - get the module and name from the json and put into regex for comparing w/ mod/inst in program
        megaregex = {}
        robj = {}
        for group, mod, name in self.cct_list:
            if group in megaregex:
                megaregex[group] += f"|{mod}::({name})"
            else:
                megaregex[group] = f"{mod}::({name})"

            # add in check for mod and name from json in program - and error if not found
            if mod not in self.tpobj.mtpl.tdata:
                log.info(f'problem: {mod} not in TP - referenced in  cct json {group} for instance {name}')
                self.add_error(218, f'{group} - {mod}-{name}', f'{mod} specified in cct json for {group} - {name} not in program! Contact cct module owner for this TP PR.')

            elif name not in self.tpobj.mtpl.tdata[mod]:
                log.info(f'problem: {name} not in TP - referenced in  cct json {group} for module {mod}')
                self.add_error(218, f'{group} - {mod}-{name}', f'{name} specified in cct json for {group} - {mod} not in program! Contact cct module owner for this TP PR.')

        # make a compiled regex for each group's modules and instances from the json
        for group in megaregex:
            robj[group] = re.compile(f'({megaregex[group]})')

        # iterate through all of the instances in the program
        for module, instance, params in all_instances:
            key = f'{module}::{instance}'
            for group in robj:
                # program doesn't know about group - but the db file does
                db_key = f'{group}::{key}'
                if robj[group].search(key):
                    # build the multi-line string
                    param_list = []
                    # get the parameters for the module+instance to compare with the dictionary
                    for p in self.cct_cfg[group][module][instance]:
                        if p in params:
                            param_list.append(f"{p} = {params[p]}")
                        else:
                            # note - "Patlist" needs to be "patlist" in config file because it gets auto lc'd - "Patlist" in the config file will cause this error to be hit
                            log.info(f'problem: parameter {p} specified in the config filecheck for {module} {instance} does not exist in the program')
                            self.add_error(218, f'{group} - {module}-{instance}', f'{p} parameter specified in cct json for {group} - {module} - {instance} not in program! Contact cct module owner for this TP PR.')
                    multi_string = '\n'.join(param_list)

                    # Compare the parameter values in the program with the values stored in the dict
                    if self.db_cct.get(db_key) == multi_string:
                        log.info(f"passing check for {module},{instance}")
                        self.add_pass(218, f'{group} - {module} - {instance}')
                    # if they don't match, in write mode the db is updated to match the changes in the program, or erroring out.
                    else:
                        if write_mode:
                            log.info(f'Updating {db_key} to new value:')
                            log.info(indent(3, multi_string.split('\n')))
                            log.info("From:")
                            log.info(indent(3, self.db_cct.get(db_key, 'Not in DB').split('\n')))
                            self.db_cct[db_key] = multi_string
                        else:
                            log.info(f'failing check for {group}, {module}, {instance}')
                            #  error for case where the db_key isn't in the db at all - like new instance or module added to config file
                            if(self.db_cct.get(db_key) is None):
                                self.add_error(218, f'{group} - {module}-{instance}', f' No stored parameter values for {module} and {instance}. Contact cct module owner for this TP PR.')
                            else:
                                for par_val in self.db_cct.get(db_key).split('\n'):
                                    par, val = par_val.split(' = ')
                                    # params[par] is TP value)
                                    if(not (str(val) == str(params[par]))):
                                        log.info("Previous Value:")
                                        log.info(indent(3, (par, val)))
                                        log.info("Your program:")
                                        log.info(indent(3, (par, params[par])))
                                        self.add_error(218, f'{group} - {module}-{instance}', f'{instance} has changed! Contact cct module owner for this TP PR.')
                                # TODO - still missing an error for the case where a parameter was added that's not in the DB - CCT owner should always run save when modifying config


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) != 1, 'Usage Error!\n\nPls specify .env file as first args'
    CCTSync(TestProgram(sys.argv[1]).pickle_init()).run()
