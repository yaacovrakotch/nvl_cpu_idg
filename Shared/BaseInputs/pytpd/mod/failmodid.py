#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
from tp.testprogram import TestProgram
from mod.update_mtpl import FlowUpdater
from collections import defaultdict
from gadget.pylog import log
import os
import sys
import glob


class FailModuleId:

    def __init__(self, TP_path):
        self.TP_path = TP_path
        self.tpobj = TestProgram(self.TP_path).init(light=True)
        self.module_dict = self.tpobj.mtpl.get_mod2fname()  # This will return {module_test_plan_name: mtpl_file_path}

    def main(self):
        if not (os.path.exists(self.TP_path)):
            log.info(f'{self.TP_path} does NOT exist. Please check the input path is valid.')
            exit(1)
        # Write the config file
        log.info('Start writing the failing module identification config file...')
        failed_mod_config = f'{self.TP_path}/Shared/Modules/TPI/TPI_BASE_XXX/InputFiles/Failing_Module_Identification_Config.csv'
        if os.path.exists(failed_mod_config):
            os.remove(failed_mod_config)

        self.write_config(failed_mod_config)
        # Getting all subflow from the test program
        all_subflow_dict = self.all_subflows()
        # Subflow modification for skip Bin
        self.skip_Bin_test_instance_add(all_subflow_dict, failed_mod_config)

    def write_config(self, outfile):
        """
        Read the testprogram and generate the config file

        :param outfile: output csv file config
        :return: None
        """

        kwargs = dict(bypass=False, pdict=True)
        results = defaultdict(set)  # {module: set_of_hardbin}
        # Get subbindef file
        for mod_name, mod_path in self.module_dict.items():
            log.info(f'Processing {mod_path}...')
            mod_subbindef = glob.glob(f'{os.path.dirname(mod_path)}/*.sbdefs')
            if mod_subbindef:
                bindef = mod_subbindef[0]
                log.info(f'Found subbindef file: {bindef}')
                with open(bindef, 'r') as f:
                    lines = f.readlines()
                mod_bin_list = []
                set_mod = False
                for line in lines:
                    if line.strip().startswith('Bin '):
                        modbin = line.strip().split()[2]
                        # Remove leading '0' if modbin is 4 characters and starts with '0'
                        if len(modbin) == 4 and modbin.startswith('0'):
                            modbin = modbin[1:]
                        mod_bin_list.append(modbin)
                        set_mod = True
                if set_mod:
                    log.info(f'Found module {mod_name}: bingroup {mod_bin_list}')
                    results[mod_name] = mod_bin_list

        # Write the config file
        with open(outfile, 'w') as fh:
            fh.write('#Set,IBin,FBin,DBin,Counter,Token,InitialValue,MatchValue\n')
            for module, set_hardbins in results.items():
                fh.write(f'Set1,,^{"$|^".join(sorted(set_hardbins))}$,,,G.L.S.FIM_{module},0,1\n')

    def add_text_to_file(self, file_path, line_number, text_to_add, numOfLine_overwrite):
        """This function will add text to the file given the line_number"""
        with open(file_path, 'r') as file:
            lines = file.readlines()
        # Ensure the line number is within the range of lines in the file
        if line_number < 1 or line_number > len(lines) + 1:
            raise IndexError("Line number is out of range.")

        # Split the text_to_add into lines.
        new_lines = text_to_add.split("\n")

        # Insert the new lines at the specified line number.
        lines[line_number - 1:line_number - 1 + numOfLine_overwrite] = [line + "\n" for line in new_lines]

        # Rename the old file
        file_path_old = file_path + '.oldmtpl'
        if not (os.path.exists(file_path_old)):
            os.rename(file_path, file_path_old)

        # log.info('writing the binrules test instance to the mtpl file...')
        with open(file_path, 'w') as file:
            file.writelines(lines)

    def get_line_number(self, file_path, text_to_get_line_number):
        """This method will return the line number where to insert the text"""
        with open(file_path, 'r') as file:
            lines = file.readlines()

        count = 0
        if text_to_get_line_number == 'CSharpTest ' or text_to_get_line_number == 'Import ':
            for line in lines:
                count += 1
                if line.strip().startswith(text_to_get_line_number):
                    line_number = count - 1
                    return line_number
        else:
            for line in lines:
                count += 1
                if text_to_get_line_number in line:
                    line_number = count
                    return line_number
        return 0

    def all_subflows(self):
        """
        Return all subflows for all modules
        returns: {module: set_of_subflows}
        """
        i2s = self.tpobj.mtpl.get_instance_to_subflows()
        kwargs = dict(bypass=False)
        result = defaultdict(set)  # {module: set_of_subflows}
        for mod, tname in self.tpobj.mtpl.iter_flows('MAIN', **kwargs):
            result[mod].update(i2s[(mod, tname)])

        # remove extra composites
        final = {}
        for mod in result:
            final[mod] = set()
            for item in result[mod]:
                if item.startswith(mod):
                    final[mod].add(item)
        return final

    def skip_Bin_test_instance_add(self, all_subflow_dict, failed_mod_config):
        """Add the Skip flow instance at the beginning of each subflow."""
        # Loop through the Failing_Module_Identification_Config.csv
        mod_list = []
        if os.path.exists(failed_mod_config):
            # find the module name from 'Set1,56|67|69,,,,G.L.S.FIM_TPI_BASE_XXX,0,1'
            log.info(f'Getting modules from {failed_mod_config}')
            with open(failed_mod_config, 'r') as f:
                lines = f.readlines()

            for line in lines:
                module = line.split(',')[5].split('.')[-1][4:]
                if module is not None:
                    mod_list.append(module)
        else:
            log.info(f'{failed_mod_config} does NOT exist.')

        # For mod in mod_list, look for modules in all_subflow_dict. module is module test plan name
        # if mod is in all_subflow_dict, get all the subflow and insert the test instances and DUT flow
        for module in mod_list:
            log.info(f'Modifying module: {module}')
            if module in all_subflow_dict:
                # Getting module path from module name (find key by value in self.module_dict)
                file_path = next((path for name, path in self.module_dict.items() if name == module), None)
                if file_path is None:
                    log.info(f"Module path not found for module: {module}")
                    continue

                subflows = all_subflow_dict[module]
                obj = FlowUpdater(self.tpobj, file_path, module)
                if 'TPI_BASE_XXX' in module:

                    log.info('Add Binrules test instance to the TPI_BASE_XXX module')
                    text_to_get_line_number = 'CSharpTest '
                    line_number = self.get_line_number(file_path, text_to_get_line_number)
                    line_number = line_number + 1  # Get a correct line number for the next test instance.
                    text_to_add = '''CSharpTest BinRulesTC CTRL_X_BINRULES_K_LOTSTARTFLOW_X_X_X_X_FMI_BINRULES\n{
                    \n\tInputFile = "./InputFiles/Failing_Module_Identification_Config.csv";\n}'''
                    self.add_text_to_file(file_path, line_number, text_to_add, 0)

                    # Adding the DUTFlowItem
                    insert_dict = {
                        -2: {'PassFail': 'Fail', 'SetBin': 'b90990101_fail_FAIL_DPS_ALARM', 'Return': '-2'},
                        -1: {'PassFail': 'Fail', 'SetBin': 'b90980101_fail_FAIL_SYSTEM_SOFTWARE',
                             'Return': '-1'},
                        0: {'PassFail': 'Fail', 'Return': '1'},
                        1: {'PassFail': 'Pass', 'PREVIOUS': True}}
                    obj.insert('TPI_BASE_XXX_LOTSTARTFLOW', 'CTRL_X_PRIMELOTSTART_K_LOTSTARTFLOW_X_X_X_X_PRIMESTARTLOTDATALOG', 1,
                               'CTRL_X_BINRULES_K_LOTSTARTFLOW_X_X_X_X_FMI_BINRULES',
                               'CTRL_X_BINRULES_K_LOTSTARTFLOW_X_X_X_X_FMI_BINRULES', insert_dict)

                if 'TPI_END_XXX' in module:
                    line_number = self.get_line_number(file_path, 'CSharpTest ')
                    line_number = line_number + 1  # Get a correct line number for the next test instance.

                    text_to_add = '''CSharpTest RunCallback CTRL_X_UF_E_TESTPLANENDFLOW_X_X_X_X_BINRULES
    {
    \tCallback ="ExecuteBinRules";
    \tLogLevel = "Enabled";
    \tParameters = "Set1";
    \tResultPort = "[R]=='1'?1:0";
    }'''
                    self.add_text_to_file(file_path, line_number, text_to_add, 0)

                    # Adding the DUTFlowItem
                    insert_dict = {
                        -2: {'PassFail': 'Fail', 'SetBin': 'b90990101_fail_FAIL_DPS_ALARM', 'Return': '-2'},
                        -1: {'PassFail': 'Fail', 'SetBin': 'b90980101_fail_FAIL_SYSTEM_SOFTWARE',
                             'Return': '-1'},
                        0: {'PassFail': 'Fail', 'Return': '1'},
                        1: {'PassFail': 'Pass', 'PREVIOUS': True}}
                    obj.insert('TPI_END_XXX_TESTPLANENDFLOW',
                               'CTRL_X_ODESEBINCONVERTERTC_E_TESTPLANENDFLOW_X_X_X_X_ODESEREMAP', 1,
                               'CTRL_X_UF_E_TESTPLANENDFLOW_X_X_X_X_BINRULES',
                               'CTRL_X_UF_E_TESTPLANENDFLOW_X_X_X_X_BINRULES', insert_dict)

                # Adding test instance
                text_to_get_line_number = 'CSharpTest '
                line_number = self.get_line_number(file_path, text_to_get_line_number)
                line_number = line_number + 1  # Get a correct line number for the next test instance.

                # Adding test instance name
                base_module_name = module.split('_')[0]
                test_name = f'{base_module_name}_X_AUX_K_FLOW_X_X_X_X_FMI_SKIP'
                expression = f'G.L.S.FIM_{module}'
                text_to_add = f"""CSharpTest AuxiliaryTC {test_name}
    {{
        Expression = "[{expression}]";
        DataType = "String";
        ResultPort = "[R]=='1'?2:1";
    }}
    """
                self.add_text_to_file(file_path, line_number, text_to_add, 0)

                for subflow in subflows:
                    subflow = subflow.split(':')[-1]
                    log.info(f'Checking {subflow}')

                    # Add DUTFlow for the test instance
                    insert_dict = {
                        -2: {'PassFail': 'Fail', 'SetBin': 'b90990101_fail_FAIL_DPS_ALARM', 'Return': '-2'},
                        -1: {'PassFail': 'Fail', 'SetBin': 'b90980101_fail_FAIL_SYSTEM_SOFTWARE',
                             'Return': '-1'},
                        0: {'PassFail': 'Fail', 'PREVIOUS': True},
                        1: {'PassFail': 'Pass', 'PREVIOUS': True},
                        2: {'PassFail': 'Pass', 'Return': '1'}}
                    obj.insert(f'{subflow}', None, 1, test_name, test_name, insert_dict)
                obj.write()
