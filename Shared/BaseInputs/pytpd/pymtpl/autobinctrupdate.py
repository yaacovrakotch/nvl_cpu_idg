"""
MTPL to AutoBinner and AutoCounter JSON updater.
Script for running in the Cake workflow to generate and update
bin and counter configuration files.
Works for Sort only currently.
"""
from gadget.errors import confirm, ErrorUser, ErrorInput, Check
from gadget.files import File
from gadget.disk import mkdirs
from gadget.helperclass import OPT
import re
import os
import json
from tp.testprogram import Env
from tp.testprogram import TestProgram


class UpdateAutobinAndAutoCtrJson:
    """
    Updates the autobin and autoctr JSON files for the provided MTPL file.

    This class parses MTPL files and extracts bin and counter information,
    then updates the corresponding JSON configuration files.
    """

    def __init__(self, mtplfile):
        """
        Initialize the updater with an MTPL file.

        Args:
            mtplfile (str): Path to the MTPL file to process
        """
        self.mtplfile = mtplfile
        print("Starting Pymtpl Auto Bin and Ctr update Script Execution")
        self.existingbindict = {}
        self.existingctrdict = {}
        self.bindict = {}
        self.ctrdict = {}
        self.mtplmoduleinfo = {}
        self.tpobj = TestProgram.dummy_tpobj()
        self.moduledir = os.path.dirname(mtplfile)
        self.tpobj.mtpl.read_mtpl_specific([self.mtplfile], True)
        self.df = self.tpobj.mtpl.get_dutflow_map()
        self.mtplmoduleinfo = self.tpobj.mtpl.get_mod2fname()
        self.commentdict, self.eoldict = self.tpobj.mtpl.read_dutflow_comments(mtplfile)
        self.load_existing_bin_info_from_file()
        self.load_existing_ctr_info_from_file()

    def main(self):
        """
        Main entry point to process MTPL data and update configuration files.

        Parses the DUT flow map and updates bin and counter information,
        then saves the updated dictionaries to JSON files if changed.
        """
        # Check if PymtplInputFiles directory exists
        pymtpl_input_dir = None
        for module, mtplfilepath in self.mtplmoduleinfo.items():

            pymtpl_input_dir = os.path.join(os.path.dirname(mtplfilepath), 'PymtplInputFiles')
            break  # Just need to get the directory from any module

        if not pymtpl_input_dir or not os.path.isdir(pymtpl_input_dir):
            print(f"PymtplInputFiles directory not found. Skipping processing.")
            return

        for flow, fitem in self.df.items():
            for port, portdata in fitem.items():
                if isinstance(portdata, dict):
                    self.update_autobin_json(portdata)

        self.update_edc_autobin_json()

        if self.bindict != self.existingbindict:
            self.save_dict_to_json(self.bindict, self.autobinner_file)
            print(f"AutoBinner file is updated with new bin information.")
        else:
            print(f"AutoBinner file is already up to date so no changes were made.")
        if self.ctrdict != self.existingctrdict:
            self.save_dict_to_json(self.ctrdict, self.autoctr_file)
            print(f"AutoCounter file is updated with new counter information.")
        else:
            print(f"AutoCounter file is already up to date so no changes were made.")

    def load_existing_bin_info_from_file(self):
        """
        Load existing bin information from the AutoBinner JSON file.

        The AutoBinner file is located in mtplfile/PymtplInputFiles
        with a filename pattern of {module}_AutoBinner.json
        """
        for module, mtplfilepath in self.mtplmoduleinfo.items():
            mtplfolder = os.path.dirname(mtplfilepath)
            autobinner_filename = f"{module}_AutoBinner.json"
            self.autobinner_file = os.path.join(mtplfolder, 'PymtplInputFiles', autobinner_filename)

        if os.path.exists(self.autobinner_file):
            with open(self.autobinner_file, 'r') as f:
                self.existingbindict = json.load(f)

    def load_existing_ctr_info_from_file(self):
        """
        Load existing counter information from the AutoCounter JSON file.

        The AutoCounter file is located in mtplfile/PymtplInputFiles
        with a filename pattern of {module}_AutoCounter.json
        """
        for module, mtplfilepath in self.mtplmoduleinfo.items():
            mtplfolder = os.path.dirname(mtplfilepath)
            autoctr_filename = f"{module}_AutoCounter.json"
            self.autoctr_file = os.path.join(mtplfolder, 'PymtplInputFiles', autoctr_filename)

        if os.path.exists(self.autoctr_file):
            with open(self.autoctr_file, 'r') as f:
                self.existingctrdict = json.load(f)

    def save_dict_to_json(self, dictionary, file_path):
        """
        Save a dictionary to a JSON file with 'bin' key always first.

        Args:
            dictionary (dict): The dictionary to save
            file_path (str): Path to the output JSON file
        """
        # Create a reordered dictionary to ensure 'bin' appears first
        reordered_dict = {}

        for test_name, test_data in dictionary.items():
            reordered_dict[test_name] = {}

            # Add 'bin' first if it exists
            if 'bin' in test_data:
                reordered_dict[test_name]['bin'] = test_data['bin']

            # Add all other keys in their original order
            for key, value in test_data.items():
                if key != 'bin':
                    reordered_dict[test_name][key] = value

        # Save the reordered dictionary
        with open(file_path, 'w') as f:
            json.dump(reordered_dict, f, indent=4)  # indent for pretty formatting

    def update_edc_autobin_json(self):
        """Load EDC bins from the mtpl file and extract numeric identifiers."""

        for test_name, bininfolist in self.commentdict.items():
            if test_name not in self.bindict:
                self.bindict[test_name] = {}
                self.bindict[test_name]["bin"] = "NA"

            for bininfo in bininfolist:
                if "##EDC##" in bininfo:
                    clean_bininfo = bininfo.replace("##EDC##", "").strip()
                    setbininfo = self.get_bin(clean_bininfo)

                    port = self.get_port_info(clean_bininfo)
                    if port is None:
                        continue
                    if port < 0:
                        portkey = f"r{str(port).replace('-', 'm')}"
                    elif port >= 0:
                        portkey = f"r{port}"
                    if port == 0:
                        bin_value = setbininfo[0:4]
                        self.bindict[test_name]["bin"] = bin_value

                    self.bindict[test_name][portkey] = setbininfo

    def get_port_info(self, setbininfo):
        identifier = None
        id_match = re.search(r'_([n]?)(\d+);', setbininfo)
        if id_match:
            prefix = id_match.group(1)
            number = id_match.group(2)

            # Process the identifier
            if prefix == 'n':
                identifier = -int(number)  # Convert to negative
            else:
                identifier = int(number)  # Keep as positive

        return identifier

    def update_autobin_json(self, input_fitem_info):
        """
        Update the bin and counter dictionaries with data from the flow item.

        Args:
            input_fitem_info (dict): Flow item information containing test and port data
        """
        test_name = input_fitem_info[999]
        for port, portdata in input_fitem_info.items():
            if port != 999:
                if port < 0:
                    portkey = f"r{str(port).replace('-', 'm')}"
                elif port >= 0:
                    portkey = f"r{port}"

                if "SetBin" in portdata:
                    if test_name not in self.bindict:
                        self.bindict[test_name] = {}
                        self.bindict[test_name]["bin"] = "NA"

                    setbininfo = self.get_bin(portdata["SetBin"])
                    if setbininfo is not None:
                        if port == 0:
                            bin_value = setbininfo[0:4]
                            self.bindict[test_name]["bin"] = bin_value

                        self.bindict[test_name][portkey] = setbininfo

                if "IncrementCounters" in portdata:
                    if test_name not in self.ctrdict:
                        self.ctrdict[test_name] = {}

                    ctrinfo = self.get_counter(portdata["IncrementCounters"])
                    if ctrinfo is not None:
                        self.ctrdict[test_name][portkey] = ctrinfo

    def get_bin(self, setbinstring):
        """
        Extract the SetBin value from a bin string.

        Args:
            setbinstring (str): String containing bin information with format 'bXXXXXXXX'

        Returns:
            str: The extracted 8-digit bin number
        """
        pattern = r"b(\d{8})"
        matches = re.findall(pattern, setbinstring)
        if not matches:
            return None
        setbin = matches[0]

        return str(setbin)

    def get_counter(self, counterstring):
        """
        Extract the counter value from a counter string.

        Args:
            counterstring (str): String containing counter information with format 'nXXXXXXXX' or 'pXXXXXXXX'

        Returns:
            str: The extracted 8-digit counter number

        Raises:
            ErrorUser: If the counter string does not match the expected format
        """
        pattern = r"[np](\d{8})"
        matches = re.findall(pattern, counterstring)
        if not matches:
            return None
        counter = matches[0]

        return str(counter)
