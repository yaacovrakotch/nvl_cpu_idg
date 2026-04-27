"""
bins, counters and basenumber features for pymtpl
"""
from gadget.pylog import log
from gadget.errors import confirm, ErrorUser, ErrorInput, Check
from gadget.helperclass import OPT, IS_UT, is_none
from tp.testprogram import Env
from tp.testprogram import TestProgram
from tp.mtpl import BM
from pymtpl.core import Initialize, Flow, MultiTrial
import os
import json
import re
import random


class BaseMtplInfo:
    """
    Centralized class to hold all of the parsed mtpl information
    """
    mtpl_dutflow_map = {}
    mttinfodict = {}

    @classmethod
    def load_mtpl_dutflow_map(cls):
        mtplfilepath = os.path.join(os.path.dirname(Initialize.get_outfile()), Initialize.get_outfile() + ".mtpl")
        if os.path.exists(mtplfilepath):
            tpobj = TestProgram.dummy_tpobj()
            tpobj.mtpl.read_edc_setbin = True
            tpobj.mtpl.read_mtpl_specific([mtplfilepath], True)
            BaseMtplInfo.mtpl_dutflow_map = tpobj.mtpl.get_dutflow_map()
            BaseMtplInfo.mttinfodict = tpobj.mtpl._mttdata

    @classmethod
    def clear_base_mtpl_dutflowinfo(cls):
        BaseMtplInfo.mtpl_dutflow_map = {}
        BaseMtplInfo.mttinfodict = {}


class BaseBin:
    """
    Base class for binning strategies
    This class holds one module at a time (one per Initialize)
    """

    bin_registry = {}      # {8-digit: <name>}. We update <name> to <name_SHARED_BIN> if 8-digit is reused.
    mtt_bin_registry = {}  # {4-digit: <name>}.
    all_4digit = set()
    all_8digit = set()
    bin_range = []
    dig8_bin_range = []
    ignore_list = []       # hardcoded in class
    Shared_Index = 0
    autobindict = {}
    autobindict_internal = {}
    binctr_dict = {}
    sbdef_dict = {}
    sbdef_2dig_list = set()
    sbdef_4dig_list = set()
    thermal8digbin = None
    reset8digbin = None
    default_thermal_bin_dict = {}
    # Need below 4 list items for class HBSBXXXX binning
    usable_thermal_bins = []
    usable_reset_bins = []
    usable_rm2_bins = []
    usable_rm1_bins = []
    default_reset_bin_dict = {}
    sbdef_prohibited_hardbins = ['97', '98', '99']  # hardbins not allowed in sbdef file
    sbdef_prohibited_databins = ['98', '99']  # hardbins for databins not allowed in sbdef file
    ctrrangeforbins = []  # List of tuples defining counter ranges for bins

    @classmethod
    def set_default_thermal_reset_bins(cls):
        """
        Sets the default thermal and reset bins if defined in the Initialize call.
        """
        if Initialize.defaultthermalbin is None:
            cls.default_thermal_bin_dict = {}
        else:
            if isinstance(Initialize.defaultthermalbin, int):
                thermalkey = "-" + str(Initialize.defaultthermalbin)[4:6]
                cls.default_thermal_bin_dict[thermalkey] = Initialize.defaultthermalbin

            elif isinstance(Initialize.defaultthermalbin, tuple):
                for thermalbin in Initialize.defaultthermalbin:
                    thermalkey = "-" + str(thermalbin)[4:6]
                    confirm(thermalkey not in cls.default_thermal_bin_dict,
                            f"The default thermal bin for the HardBin {thermalkey} has already been assigned.",
                            f"You can only define one defaultthermal bin per HB. Please ensure all HBs in {Initialize.defaultthermalbin} are unique.")
                    cls.default_thermal_bin_dict[thermalkey] = thermalbin

        if Initialize.defaultresetbin is None:
            cls.default_reset_bin_dict = {}
        else:
            if isinstance(Initialize.defaultresetbin, int):
                resetkey = "-" + str(Initialize.defaultresetbin)[2:4]
                cls.default_reset_bin_dict[resetkey] = Initialize.defaultresetbin

            elif isinstance(Initialize.defaultresetbin, tuple):
                for resetbin in Initialize.defaultresetbin:
                    resetkey = "-" + str(resetbin)[2:4]
                    confirm(resetkey not in cls.default_reset_bin_dict,
                            f"The default reset bin for the HardBin {resetkey} has already been assigned.",
                            f"You can only define one defaultreset bin per HB. Please ensure all HBs in {Initialize.defaultresetbin} are unique.")
                    cls.default_reset_bin_dict[resetkey] = resetbin

    @classmethod
    def write_sbdef_file(cls):
        """
        Writes the sbdef file with the bin definitions
        """

        if not cls.sbdef_dict:
            return []

        # sort sbdef_dict by key
        sorted_bins = sorted(cls.sbdef_dict.items())

        # If the only hardbins present are not allowed in _get_bin2dig_match, skip writing sbdef
        hb_2dig_list = []
        db_2dig_list = []
        for setbinstring, _ in sorted_bins:
            # checking for allowed harbins
            bin_2dig = cls._get_hardbin_match(setbinstring)
            if bin_2dig:
                hb_2dig_list.append(bin_2dig)
            # checking for allowed databins
            bin_2dig_db = cls._get_hardbin_match(setbinstring, use_databin_prohibited_list=True)
            if bin_2dig_db:
                db_2dig_list.append(bin_2dig_db)
        if not hb_2dig_list and not db_2dig_list:  # no valid hardbins found
            return []

        yield 'Version 1.0;\n'
        yield 'SubBinDefs'
        yield '{\n'

        # HardBins section
        if (Initialize.write_hardbins_to_sbdef):
            yield '    BinGroup HardBins'
            yield '    {'
            for bin, name in sorted_bins:  # use sorted_bins
                bin_2dig = cls._get_hardbin_match(bin)
                if bin_2dig:
                    confirm(bin_2dig in Initialize.bindefdict, f"Unable to extract the bin classification for the bin {bin_2dig}. Please check the bin {bin} and ensure it follows the proper format.",
                            f"If everything looks good, please open a pymtpl ticket in the pytpd git repo. Check also bindef_dict.py definition")
                    bin_2dig_name = Initialize.bindefdict[bin_2dig]
                    parent_name = "Pass" if "pass" in name.lower() else "Fail"
                    if bin_2dig not in cls.sbdef_2dig_list:
                        # do not allow repeated bins.
                        cls.sbdef_2dig_list.add(bin_2dig)
                        yield f'        Bin {bin_2dig_name}    {bin_2dig}    : "{bin_2dig_name}",    {parent_name};'
            yield '    }\n'

        # Softbins section
        if (Initialize.write_softbins_to_sbdef):
            yield '    BinGroup SoftBins'
            yield '    {'
            if not Initialize.default_class.is_hdbi:
                yield from cls._write_softbin_lines(sorted_bins, leafbins_are_softbins=Initialize.leafbins_are_softbins)
            else:
                # For HDBI, write 4-digit softbin lines
                yield from cls._write_hdbi_softbin_lines(sorted_bins)
            if (Initialize.leafbins_are_softbins):
                yield from cls._write_databin_lines(sorted_bins)
            yield '    }\n'

        # DataBins section
        if (not Initialize.leafbins_are_softbins):
            yield '    BinGroup DataBins'
            yield '    {'
            yield from cls._write_databin_lines(sorted_bins)
            yield '    }\n'

        # close bindef
        yield '}'

    @classmethod
    def _write_softbin_lines(cls, sorted_bins, leafbins_are_softbins):
        binOrLeafBin = "LeafBin" if leafbins_are_softbins else "Bin"
        for bin, name in sorted_bins:  # use sorted_bins
            # Ignore bin 97s/98s/99s in the sbdef file
            bin_2dig = cls._get_hardbin_match(bin)
            bin_4dig = cls._get_softbin_match(bin)
            if bin_2dig and bin_4dig:
                bin_4dig_name = cls._get_softbin_name(bin_4dig)
                confirm(bin_2dig in Initialize.bindefdict, f"Unable to extract the bin classification for the bin {bin_2dig}. Please check the bin {bin} and ensure it follows the proper format.",
                        f"If everything looks good, please open a pymtpl ticket in the pytpd git repo. Check also bindef_dict.py definition")
                if bin_4dig not in cls.sbdef_4dig_list:
                    # SoftBins section does not allow repeated bins.
                    cls.sbdef_4dig_list.add(bin_4dig)
                    yield f'        {binOrLeafBin} b{bin_4dig_name}    {bin_4dig}    : "b{bin_4dig_name}",    {Initialize.bindefdict[bin_2dig]};'

    @classmethod
    def _write_hdbi_softbin_lines(cls, sorted_bins):
        """
        Write 4-digit softbin lines for HDBI class.
        For HDBI, we need to write both 4-digit and 8-digit bins in the SoftBins section.
        This method writes the 4-digit bins (extracted from 8-digit bins).
        """
        for setbinstring, bin in sorted_bins:
            bin_2dig = cls._get_hardbin_match(setbinstring, use_databin_prohibited_list=True)
            bin_4dig = cls._get_softbin_match(setbinstring, use_databin_prohibited_list=True)
            if bin_4dig:
                bin_classification = cls._get_bindefdict_match(bin_2dig)
                if bin_4dig not in cls.sbdef_4dig_list:
                    # Get the full bin name (e.g., "b90970200_fail_PTH_PRESOAK...")

                    full_bin_name = setbinstring[len(Initialize.tos_softbinstr):]
                    # Replace 7/8-digit bin with 4-digit bin in the name (e.g., "b90970200..." -> "b9702...")
                    # The full bin name starts with "b" followed by 7 or 8 digits
                    if full_bin_name.startswith('b'):
                        # Extract the actual bin number (7 or 8 digits)
                        actual_bin = cls._get_bin(full_bin_name)  # This already handles 7-8 digits
                        if actual_bin:
                            # Position after 'b' + bin digits
                            suffix_start = 1 + len(actual_bin)
                            bin_4dig_name = 'b' + bin_4dig + full_bin_name[suffix_start:]
                        else:
                            raise ErrorUser(f"Unable to extract the actual bin number from {full_bin_name}. Please check the bin format.",
                                            f"If everything looks good, please open a pymtpl ticket in the pytpd git repo.")
                    else:
                        raise ErrorUser(f"Full bin name {full_bin_name} does not start with 'b'. Please check the bin format.",
                                        f"If everything looks good, please open a pymtpl ticket in the pytpd git repo.")
                    # SoftBins section does not allow repeated bins.
                    cls.sbdef_4dig_list.add(bin_4dig)
                    yield f'        LeafBin {bin_4dig_name}    {bin_4dig}    : "{bin_4dig_name}",    {bin_classification};'

    @classmethod
    def _write_databin_lines(cls, sorted_bins):
        for bin, number in sorted_bins:
            bin_2dig = cls._get_hardbin_match(bin, use_databin_prohibited_list=True)
            bin_4dig = cls._get_softbin_match(bin, use_databin_prohibited_list=True)
            if bin_4dig:
                bin_4dig_name = cls._get_softbin_name(bin_4dig)
                # Remove prefix of Softbins. etc
                bin = bin[len(Initialize.tos_softbinstr):]
                # remove leading zeroes of bin numbers but pad with spaces on the left to 8 digits
                number = str(int(number)).rjust(8, ' ')
                if Initialize.default_class.is_hdbi:
                    bin_classification = cls._get_bindefdict_match(bin_2dig)
                    yield f'        LeafBin {bin}    {number}    : "{bin}",    {bin_classification};'
                else:
                    yield f'        LeafBin {bin}    {number}    : "{bin}",    b{bin_4dig_name};'

    @classmethod
    def _get_softbin_name(cls, softbin_4dig):
        """
        Returns the softbin name for a given 4 digit bin.
        :param softbin_4dig: 4 digit bin
        :return: softbin name
        """
        if softbin_4dig in Initialize.bindefdict:
            return Initialize.bindefdict[softbin_4dig]
        return softbin_4dig

    @classmethod
    def _get_hardbin_match(cls, bin, use_databin_prohibited_list=False):
        """
        Returns the 2 digit hardbin bin match for a given 8 digit bin.
        Skips hardbins in sbdef_prohibited_hardbins
        :param bin: 8 digit bin
        :return: 2 digit hardbin bin match or None if not found
        """
        if use_databin_prohibited_list and cls.sbdef_prohibited_databins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_databins)
            regex = rf'b90(?!{negative_lookahead})\d{{2}}'
        elif cls.sbdef_prohibited_hardbins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_hardbins)
            regex = rf'b90(?!{negative_lookahead})\d{{2}}'
        else:
            regex = r'b90\d{2}'
        bin_2dig_match = re.search(regex, bin)
        return bin_2dig_match.group(0)[3:] if bin_2dig_match else None

    @classmethod
    def _get_softbin_match(cls, bin, use_databin_prohibited_list=False):
        """
        Returns the 4 digit hbsb match for a given 8 digit bin.
        Skips hardbins in sbdef_prohibited_hardbins
        :param bin: 8 digit bin
        :return: 4 digit hbsb match or None if not found
        """
        if use_databin_prohibited_list and cls.sbdef_prohibited_databins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_databins)
            regex = rf'b90(?!{negative_lookahead})\d{{4}}'
        elif cls.sbdef_prohibited_hardbins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_hardbins)
            regex = rf'b90(?!{negative_lookahead})\d{{4}}'
        else:
            regex = r'b90\d{4}'
        bin_4dig_match = re.search(regex, bin)
        return bin_4dig_match.group(0)[3:] if bin_4dig_match else None

    @classmethod
    def _get_bindefdict_match(cls, bin_2dig):
        if bin_2dig in Initialize.bindefdict:
            return Initialize.bindefdict[bin_2dig]
        else:
            raise ErrorUser(f"Unable to extract the bin classification for the bin {bin_2dig}. Please check the bin {bin_2dig} and ensure it follows the proper format.",
                            f"Please open a pymtpl ticket in the pytpd git repo")

    @classmethod
    def load_autobinfile(cls):
        cls.autobindict = {}
        # Internal bindict is used to load the autobinner json info.
        # We need this because we want the non internal bin dict to be updated during the mtpl generation.
        # This way we can keep them both separate and make any un-used bins available again.
        autobindict_internal = {}
        autobinfilename = str(Initialize.get_modulename()) + "_AutoBinner.json"
        autobinfilepath = os.path.join(os.path.dirname(Initialize.get_outfile()), 'PymtplInputFiles', autobinfilename)
        cls.autobinfilepath = autobinfilepath
        if Initialize.usebinctrfrommtpl:
            autobindict_internal = cls.bindictfrommtpl
        else:
            if os.path.exists(autobinfilepath):
                with open(autobinfilepath, 'r') as f:
                    autobindict_internal = json.load(f)

        # Load the bins from the dictionary into the all_4digit and all_8digit sets so that they are not re-used.
        for v in autobindict_internal.values():
            if 'bin' in v:
                cls.all_4digit.add(v['bin'])
            for key, value in v.items():
                if key != "bin":
                    cls.all_8digit.add(value)

        cls.autobindict_internal = autobindict_internal

    @classmethod
    def load_autobininfo_from_mtpl(cls):
        """
        Load the bin and counter information from the mtpl instead of autobinner json file
        """

        for flow, fitem in BaseMtplInfo.mtpl_dutflow_map.items():
            for port, portdata in fitem.items():
                if isinstance(portdata, dict):
                    cls._update_autobin_json(portdata)
        for module_name, mtttestinfo in BaseMtplInfo.mttinfodict.items():
            cls._update_mtt_autobin_json(mtttestinfo)

    @classmethod
    def _update_autobin_json(cls, input_fitem_info):
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
                    if test_name not in cls.bindictfrommtpl:
                        cls.bindictfrommtpl[test_name] = {}
                        cls.bindictfrommtpl[test_name]["bin"] = "NA"

                    setbininfo = cls._get_bin(portdata["SetBin"])

                    if setbininfo is not None:
                        if port == 0:
                            if len(setbininfo) == 8:
                                bin_value = setbininfo[0:4]
                            elif len(setbininfo) == 7:
                                bin_value = setbininfo[0:3]
                            cls.bindictfrommtpl[test_name]["bin"] = bin_value

                        cls.bindictfrommtpl[test_name][portkey] = setbininfo

    @classmethod
    def _update_mtt_autobin_json(cls, input_mtt_info):
        """
        Update the bin dictionary with data from MTT info.

        Args:
            input_mtt_info (dict): MTT information containing TrialResult with port data
        """
        for test_name, test_data in input_mtt_info.items():
            if test_data is None or 'TrialResult' not in test_data:
                continue

            # Get the instance name from CSharpTrialTest or TrialTest
            instance_name = test_data.get('CSharpTrialTest') or test_data.get('TrialTest')
            if not instance_name:
                continue  # Skip if neither key exists

            trial_results = test_data['TrialResult']

            for port, portdata in trial_results.items():
                if port < 0:
                    portkey = f"r{str(port).replace('-', 'm')}"
                elif port >= 0:
                    portkey = f"r{port}"

                if "SetBin" in portdata:
                    if instance_name not in cls.bindictfrommtpl:
                        cls.bindictfrommtpl[instance_name] = {}

                    setbininfo = cls._get_mtt_bin(portdata["SetBin"])
                    if setbininfo is not None:
                        cls.bindictfrommtpl[instance_name][portkey] = setbininfo

    @classmethod
    def _get_bin(cls, setbinstring):
        """
        Extract the SetBin value from a bin string.

        Args:
            setbinstring (str): String containing bin information with format 'bXXXXXXX' or 'bXXXXXXXX'

        Returns:
            str: The extracted 7-digit or 8-digit bin number
        """
        pattern = r"b(\d{7,8})"
        matches = re.findall(pattern, setbinstring)
        if not matches:
            return None
        setbin = matches[0]

        return str(setbin)

    @classmethod
    def _get_mtt_bin(cls, setbinstring):
        """
        Extract the SetBin value from a bin string for MTT tests.

        Args:
            setbinstring (str): String containing bin information with format
                            '"b" + FlowMatrix.bin + "XXXX_fail_..."' or
                            '"b" + BinMatrix.bin + "XXXX_fail_..."'

        Returns:
            str: The extracted 4-digit bin number, or None if not found
        """
        # Pattern to match .bin + "XXXX where XXXX is 4 digits
        pattern = r'\.bin\s*\+\s*"(\d{4})'
        matches = re.findall(pattern, setbinstring)
        if not matches:
            return None

        return str(matches[0])

    @classmethod
    def load_ignore_bins(cls, autobinignorelist):
        """
        Loads the values from the Initialize autobinignorelist parameter into the 4 digit and 8 digit sets so that
        Autobinner does not use those bins when assigning bins
        """
        if autobinignorelist is None:
            return
        for bin in autobinignorelist:
            if len(str(bin)) in [3, 4]:
                cls.all_4digit.add(str(bin).zfill(4))
            elif len(str(bin)) in [7, 8]:
                cls.all_8digit.add(str(bin))
            else:
                raise ErrorInput(f"Invalid bin value in autobinignorelist: {bin}. Expecting 3/4 digit or 7/8 digit bin values.",)

    @classmethod
    def load_8dig_bins_from_common_bindef(cls):
        """
        Load the 8 digit data bins from the common bindef file.
        If OPT.bindef does not exist then do nothing
        """
        if OPT.bindef is None:
            return
        else:
            common_bindef = OPT.bindef

        in_bingroup_section = False

        # Check to see if common_bindef file exists
        confirm(os.path.exists(common_bindef),
                f"Unable to load bindef file: {common_bindef}. Please check the path and ensure the file exists.",
                f"Pls reach out to the TPI team to ensure the Pymtpl script points to a bindef file that exists.")

        with open(common_bindef, 'r') as file:
            for line in file:
                line = line.strip()

                # Check if we're entering a BinGroup DataBins section
                if "BinGroup" in line and "DataBins" in line:
                    in_bingroup_section = True
                    continue

                # Check if we're exiting the section (assuming sections end with '}')
                if in_bingroup_section and "}" in line:
                    in_bingroup_section = False
                    continue

                # Process lines within the BinGroup DataBins section
                if in_bingroup_section:
                    # Look for 7-digit or 8-digit numbers
                    matches_7_8_digits = re.findall(r'\b(\d{7,8})\b', line)
                    if matches_7_8_digits:
                        for match in matches_7_8_digits:
                            cls.all_8digit.add(str(match))

                    # Look for 9-digit numbers starting with 2, 3 or 4
                    # 9-digit bins will never start with 1
                    matches_9_digits = re.findall(r'\b([234]\d{8})\b', line)
                    if matches_9_digits:
                        for match in matches_9_digits:
                            # Remove the first digit and add the remaining 8 digits to the all 8 digit set
                            cls.all_8digit.add(str(match)[1:])

    @classmethod
    def get_unique_4dig_bin(cls, origbin, lno):
        # If negative bin
        usableBinranges = []
        for i in range(len(cls.bin_range)):
            # For a 3-digit bin range (e.g., 801–805), extract the first digit of the lower bound (e.g., '8' from '801') for comparison
            if len(str(cls.bin_range[i][0])) == 3:
                comparevalue = str(cls.bin_range[i][0])[0:1]
            # For a 4-digit bin range like (4400, 4405), extract the first 2 digits ('44') for comparison purposes
            else:
                comparevalue = str(cls.bin_range[i][0])[0:2]
            if len(origbin) > 3 and (origbin[1:]) == str(cls.bin_range[i][0])[0:]:
                usableBinranges.append(i)
            elif len(origbin) == 3 and (origbin[1:3]) == comparevalue:
                usableBinranges.append(i)
            elif origbin == "-1":
                usableBinranges.append(0)

        if usableBinranges == []:
            raise ErrorUser(f"Please check the definition of setbin in line # {lno}",
                            f"Either the binrange or setbin user specified are incorrect. Pls fix.")

        for binrange in usableBinranges:
            binrange = cls.bin_range[binrange]
            for target in range(binrange[0], binrange[1] + 1):
                digit4 = str(target).zfill(4)
                # Check if bin is not already in use by bins or counters
                if digit4 not in cls.all_4digit and (Initialize.nonmttctrstrategy is None or digit4 not in Initialize.nonmttctrstrategy.all_8digit_counter):
                    cls.all_4digit.add(digit4)
                    return int(digit4)     # this is our new bin

        # If all the bins are exhausted, we start the loop again
        # But this time we do not add the new bin to the all_4digit set
        # nor do we check if the bin is already in the all_4digit set
        for binrange in usableBinranges:
            binrange = cls.bin_range[binrange]
            for target in range(binrange[0], binrange[1] + 1):
                digit4 = str(target).zfill(4)
                return int(digit4)

    @classmethod
    def clear_bins(cls):
        """Initialize class variables"""
        cls.bin_registry = {}
        cls.mtt_bin_registry = {}
        cls.all_4digit.clear()
        cls.all_8digit.clear()
        cls.bin_range.clear()
        cls.dig8_bin_range.clear()
        cls.Shared_Index = 0
        cls.autobindict = {}
        cls.autobindict_internal = {}
        cls.binctr_dict = {}
        cls.sbdef_dict = {}
        cls.reset8digbin = None
        cls.thermal8digbin = None
        cls.sbdef_2dig_list.clear()
        cls.sbdef_4dig_list.clear()
        cls.default_thermal_bin_dict = {}
        cls.default_reset_bin_dict = {}
        cls.bindictfrommtpl = {}
        # Need below 4 list items for class HBSBXXXX binning
        cls.usable_thermal_bins = []
        cls.usable_reset_bins = []
        cls.usable_rm2_bins = []
        cls.usable_rm1_bins = []
        cls.ctrrangeforbins = []

    @classmethod
    def set_bin_range(cls, binrange):
        """Set the bin range value and check validity"""
        if isinstance(binrange, tuple):
            cls.bin_range.append(binrange)    # One range
        else:
            cls.bin_range.extend(binrange)    # multiple ranges

        # check bin_range correctness
        for item in cls.bin_range:
            confirm(isinstance(item, (list, tuple)) and len(item) == 2,
                    f'Expecting a tuple or a list of tuples as the binrange for: item "{item}"',
                    'Pls fix binrange so that it is binrange = (start, end) or [(start1, end1), (start2, end2), ...]')

            # Check if the values are 3/4 digits long
            start, end = item
            confirm(len(str(start)) in [3, 4] and len(str(end)) in [3, 4],
                    f'Expecting start and end values to be 3 or 4 digits long for binrange "{item}"',
                    'Pls fix binrange so that start and end values are 3 (For Bin 8/9) or 4 digits long - Ex - (4400,4401)')

    @classmethod
    def set_ctr_range_for_bins(cls, ctrrangeforbins):
        """Set the counter range for bins and validate input.

        This method defines the counter ranges used to generate unique 8-digit bins
        in the format HBSBXXXX, where HBSB is the 4-digit hardbin/softbin and XXXX
        is a counter value from the specified range.

        :param ctrrangeforbins: Single tuple (start, end) or list of tuples defining counter ranges.
                                Example: (0, 2000) or [(0, 1000), (2000, 3000)]

        The counter range constrains the XXXX portion of the 8-digit bin, allowing
        users to control bin allocation within specific numeric boundaries instead of
        using the default unlimited counter starting from 0.
        """
        if isinstance(ctrrangeforbins, tuple):
            cls.ctrrangeforbins.append(ctrrangeforbins)    # One range
        else:
            cls.ctrrangeforbins.extend(ctrrangeforbins)    # multiple ranges

        # check bin_range correctness
        for item in cls.ctrrangeforbins:
            confirm(isinstance(item, (list, tuple)) and len(item) == 2,
                    f'Expecting a tuple or a list of tuples as the ctrrangeforbins for: item "{item}"',
                    'Pls fix ctrrangeforbins so that it is ctrrangeforbins = (start, end) or [(start1, end1), (start2, end2), ...]')

            # Check if the values are 3/4 digits long
            start, end = item
            confirm(len(str(start)) <= 4 and len(str(end)) <= 4,
                    f'Expecting start and end values to be less than 4 digits long for ctrrangeforbins "{item}"',
                    'Pls fix ctrrangeforbins so that start and end values are less than 4 digits long - Ex - (0,2000)')

    @classmethod
    def separate_bin_ranges(cls):
        """
        Separate bin_range into 4-digit and 8-digit ranges
        Implement in your own sub-class if you support 8-digit ranges
        """
        pass

    @classmethod
    def _update_nonmtt_bin(cls, inputbin, dfi_name, portid, forceupdate=False):
        """
        Updates non-MTT bin_registry dictionary.

        :param inputbin: input setbin value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :forceupdate: Force update bin. Used by MTT where we want to update r4/r5.
                      DutFlowItem does not update r4/r5 as they are thermal/reset bins.
        :return: None
        """
        if len(str(inputbin)) != 8:
            digit8 = cls.convert_4digit_to_8digit(inputbin)
        else:
            digit8 = str(inputbin)

        if not forceupdate and digit8 not in cls.bin_registry:
            bin_name = f'{Initialize.tos_softbinstr}b{digit8}_fail_{Initialize.get_modulename()}_{dfi_name}'
            cls.bin_registry[digit8] = bin_name
        elif forceupdate:
            bin_name = f'{Initialize.tos_softbinstr}b{digit8}_fail_{Initialize.get_modulename()}_{dfi_name}'
            cls.bin_registry[digit8] = bin_name
        else:
            # this is shared bin
            if not cls.bin_registry[digit8].endswith('_SHARED_BIN'):
                cls.bin_registry[digit8] = f'{cls.bin_registry[digit8]}_SHARED_BIN'

    @classmethod
    def _get_non_mtt_bin_name(cls, setbin):
        """
        Helper method to get the bin name for non-MTT.

        :param setbin: eight digit bin or 4 digit bin
        :return: the bin name
        """
        if len(f'{setbin}') >= 7:
            return cls.bin_registry[setbin]
        else:
            digit8 = cls.convert_4digit_to_8digit(setbin)
            return cls.bin_registry[digit8]

    @classmethod
    def convert_4digit_to_8digit(cls, digit4):
        """
        Converts 4 digit to 8 digit
        :param digit4:
        :return:
        """
        raise Exception("Implement this in your subclass")

    @classmethod
    def convert_8digit_to_4digit(cls, digit8):
        """
        :param digit8: 8 digit: 90HBHBSB
        :return: 4 digit number: HBSB
        """
        raise Exception("Implement this in your subclass")

    @classmethod
    def get_var_name(cls):
        """Return the var name used in MultiTrial SetBin"""
        raise Exception("Implement this in your subclass")

    @classmethod
    def get_new_bin(cls, origbin, lno, all_4digit):
        """Return the var name used in MultiTrial SetBin"""
        raise Exception("Implement this in your subclass")

    @classmethod
    def _get_non_mtt_autosetbinstring(cls, setbin, name, updatesetbinstring, portid, lno):
        """
        Helper method to get the autosetbinstring for non-MTT.
        :param setbin (int): The current bin number.
        :param name (str): The name associated with the bin.
        :param updatesetbinstring (list): A list where the first element is a boolean indicating
                                          whether to update the bin string, and subsequent elements
                                          are used to store the new bin string.
        :param portid (str): The item for which the bin string is being determined.
        :param lno (int): The line number in the script where this method is called.
        :return str: The determined bin string for the given item.
        """
        # If present in the autobin dict, use the setbinstring from there
        if name in cls.autobindict_internal and portid not in cls.ignore_list and portid in cls.autobindict_internal[name]:
            return cls.autobindict_internal[name][portid]

        # If not update the dict and get the setbinstring
        if portid not in cls.ignore_list and updatesetbinstring[0]:
            updatesetbinstring[0] = False
            newbin = cls.get_new_bin(setbin, lno + 1)
            updatesetbinstring.append(newbin)
            cls._update_nonmtt_bin(newbin, name, portid)
            return cls._get_non_mtt_bin_name(str(newbin))

        if portid in cls.ignore_list and (portid == "r4" or portid == "r5"):
            cls._update_nonmtt_bin(setbin, name, portid, forceupdate=True)
            return cls._get_non_mtt_bin_name(str(setbin))

        setbin = updatesetbinstring[1]
        return cls._get_non_mtt_bin_name(str(setbin))

    @classmethod
    def update_autobindict(cls, bin, portid, tname, setbinstring):
        """Update the autobin dict to ensure sticky bins"""

        # Write the bin info to the autobin dict to save as Autobinner
        if tname in cls.autobindict:
            cls.autobindict[tname][portid] = setbinstring
            cls.autobindict[tname]["bin"] = bin
        else:
            cls.autobindict[tname] = {"bin": bin, portid: setbinstring}
        # Write the bin info to the autobin_internal dict to use internally.
        # Split is needed for both dicts as the bins were changing from run to run when they were being updated together.
        if tname in cls.autobindict_internal:
            cls.autobindict_internal[tname][portid] = setbinstring
            cls.autobindict_internal[tname]["bin"] = bin
        else:
            cls.autobindict_internal[tname] = {"bin": bin, portid: setbinstring}

    @classmethod
    def _get_mtt_bin_name(cls, setbin):
        """
        Helper method to get the bin name for MTT.

        :param setbin: eight digit bin or 4 digit bin
        :return: the bin name
        """
        if len(f'{setbin}') != 8:
            return cls.mtt_bin_registry[setbin]
        else:
            digit4 = cls.convert_8digit_to_4digit(setbin)
            return cls.mtt_bin_registry[digit4]

    @classmethod
    def _update_mtt_bin(cls, inputbin, dfi_name):
        """
        Updates MTT bin_registry dictionary.

        :param inputbin: input setbin value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :return: None
        """
        if len(str(inputbin)) == 8:
            digit4 = cls.convert_8digit_to_4digit(inputbin)
        else:
            digit4 = str(inputbin)
        bin_name = f'"{Initialize.tos_softbinstr}b" + {cls.get_var_name()} + "{digit4}_fail_{Initialize.get_modulename()}_{dfi_name}"'
        cls.mtt_bin_registry[digit4] = bin_name

    @classmethod
    def _get_mtt_autosetbinstring(cls, setbin, name, portid, lno, templatename):
        """
        Helper method to get autosetbinstring for MTT.
        Args:
        :param setbin (int): The setbin value.
        :param name (str): The name of the non-MTT template.
        :param portid (str): The item to be returned.
        :param lno (int): The line number.
        :param templatename (str): The name of the MTT template.
        :return str: The setbin string for the MTT.

        Notes:
            - This method assumes that Fitems are written first followed by BaseMethods.
            - Handles cases where Fitem only has ignore ports, ensuring MTT does not ignore certain ports.
        """
        # For MTT, we just get the setbinstring based on the MTT name that has bin matrix etc in it so we use templatename
        if templatename in cls.autobindict_internal and portid not in cls.mtt_ignore_list and portid in cls.autobindict_internal[templatename] and setbin < 0:
            return cls.autobindict_internal[templatename][portid]

        # For MTT when there is no value found in the loaded autobin dict, extract the information from Autobin dict updated during mtpl gen.
        # This will work as long as we write Fitems 1st and then BaseMethods because
        # we rely on the autobindict being populated 1st before moving on
        # This gets the setbin of the Fitem using the name of the non MTT template, and uses it for the MTT ports
        try:
            setbin = cls.autobindict_internal[name]["bin"]

        # Below code handles cases where Fitem only has ignore ports.
        # Since mtt does not ignore r4,r5, we need the handler code below - See test_autobin_ignore_ports_only()
        except KeyError:
            setbin = cls.get_new_bin(setbin, lno + 1)
            cls.autobindict_internal[name] = {"bin": setbin}

        cls._update_mtt_bin(setbin, name)
        return cls._get_mtt_bin_name(str(setbin))


class BinSSB(BaseBin):
    """MTL binning method"""
    ignore_list = ['rm1', 'rm2', 'r1', 'r4', 'r5']
    mtt_ignore_list = ['rm1', 'rm2', 'r1']

    @classmethod
    def default_setbinstring_dict(cls):
        """Return the dictionary for default setbinstring"""
        return {"rm1": f"{Initialize.tos_softbinstr}b90989801_fail_FAIL_SYSTEM_SOFTWARE",
                "rm2": f"{Initialize.tos_softbinstr}b90999901_fail_FAIL_DPS_ALARM"}

    @classmethod
    def get_thermal_reset_bins(cls, origbin, lno):
        """For port4 and port5 default bin values because these are thermal/reset ports in MTL"""
        if origbin < 0:
            confirm(len(cls.bin_range) > 0, 'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin>')
        origbin = str(origbin)
        if len(cls.bin_range) == 1:
            # Set thermal and reset bins and add them to the all bin set so that they are not used.
            newthermalbin = int("97" + str(cls.bin_range[0])[1:3])
            newresetbin = int(str(cls.bin_range[0])[1:3] + "19")
        else:
            # Set thermal and reset bins and add them to the all bin set so that they are not used.
            newthermalbin = int("97" + origbin[1:3])
            newresetbin = int(origbin[1:3] + "19")

        return newthermalbin, newresetbin

    @classmethod
    def convert_4digit_to_8digit(cls, digit4):
        """
        :param digit4: 4 digit: HBSB
        :return: 8 digit number: 90HBHBSB
        """

        digit4 = str(digit4).zfill(4)
        digit8_bin = '90' + digit4[0:2] + digit4
        return digit8_bin

    @classmethod
    def populate_internal_bin_trackers(cls, flow_obj):
        """
        Populates internal bin trackers with setbin values from the given flow object.
        :param flow_obj (FlowObject): The flow object containing items with port objects to be processed.

        :return None
        """
        for fitem in flow_obj.get_items():
            for _, port_obj in fitem.ret_dict.items():
                if port_obj.setbin and port_obj.setbin > 0:
                    cls.all_8digit.add(cls.convert_4digit_to_8digit(port_obj.setbin))

        # get all the set of 4 digit
        for item in cls.all_8digit:
            cls.all_4digit.add(item[-4:])     # last 4 for SSB

    @classmethod
    def get_new_bin(cls, origbin, lno):
        """
        Return a new bin, given the range, and iterating to all the PortObjects
        :param origbin: either 0 or -44
        :return: New 4 digit
        """
        if origbin < 0:
            confirm(len(cls.bin_range) > 0, 'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} or anywhere in the input file if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin> in order to use Autobin feature when using multiple bin ranges')
        origbin = str(origbin)

        digit4_bin = cls.get_unique_4dig_bin(origbin, lno)
        return digit4_bin

    @classmethod
    def get_non_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid, lno, test_class=None):
        """
        Return the string to be used for non-MTT port
        We want the same bin across ports (eg. p0, p2, p3)

        :return: string: setbin
        """
        setbinstring = None

        if (portid not in cls.ignore_list) and updatesetbinstring[0]:
            updatesetbinstring[0] = False
            cls._update_nonmtt_bin(setbin, name, portid)
            setbinstring = cls._get_non_mtt_bin_name(str(setbin))
        else:
            try:
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))
            except KeyError:
                cls._update_nonmtt_bin(setbin, name, portid)
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))

        return setbinstring

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, test_class=None):

        setbinstring = None
        if portobj_type == "pPass":
            return ''
        if portid == "rm2":
            setbinstring = cls.default_setbinstring_dict()["rm2"]
        elif portid == "rm1":
            setbinstring = cls.default_setbinstring_dict()["rm1"]
        elif portid == "r4":
            # Moving the thermal_reset function inside here because if we want to use InitializeMTL and give -2/-1 port defs for free,
            # we need to use Autobin without specifying bin range. So moving it to here makes more sense.
            thermalbin, resetbin = cls.get_thermal_reset_bins(setbin, id_lno)
            # Add the thermal and reset bins to the all_4digit bin list so that they are not used for any of the tests
            cls.all_4digit.add(str(thermalbin))
            name = "THERMAL_" + str(tname)
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=thermalbin,
                                                             name=name,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
        elif portid == "r5":
            # Moving the thermal_reset function inside here because if we want to use InitializeMTL and give -2/-1 port defs for free,
            # we need to use Autobin without specifying bin range. So moving it to here makes more sense.
            thermalbin, resetbin = cls.get_thermal_reset_bins(setbin, id_lno)
            # Add the thermal and reset bins to the all_4digit bin list so that they are not used for any of the tests
            cls.all_4digit.add(str(resetbin))
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=resetbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
        # We have coded a conditional for all the portids in the ignore list - rm2, rm1, r4 and r5.
        # Un-comment this out if we add any new portids to the ignore list in the future.
        # elif portid in cls.ignore_list:
        #     setbinstring = ''
        else:
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=setbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)

        if portid not in cls.ignore_list and setbin:
            bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][-4:]
            cls.update_autobindict(bin, portid, tname, setbinstring)

        return setbinstring


class MTTBinSSB(BinSSB):
    """MTL binning method"""

    mtt_ignore_list = ['rm1', 'rm2', 'r1']

    @classmethod
    def convert_8digit_to_4digit(cls, digit8):
        """
        :param digit8: 8 digit: 90HBHBSB
        :return: 4 digit number: HBSB
        """

        digit4_bin = str(digit8)[-4:]
        return digit4_bin

    @classmethod
    def get_var_name(cls):
        return 'FlowMatrix.bin'

    @classmethod
    def convert_4digit_to_8digit(cls, digit4):
        """
        :param digit4: 4 digit: HBSB
        :return: 8 digit number: 90HBHBSB
        """

        digit4 = str(digit4).zfill(4)
        digit8_bin = '90' + digit4[0:2] + digit4
        return digit8_bin

    @classmethod
    def get_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid):
        """
        Return the string to be used for MTT port
        We want the same bin across ports (eg. p0, p2, p3)

        :return: string: setbin
        """
        setbinstring = None

        if (portid not in cls.ignore_list) and updatesetbinstring[0]:
            updatesetbinstring[0] = False
            cls._update_mtt_bin(setbin, name)
            setbinstring = cls._get_mtt_bin_name(str(setbin))
        else:
            try:
                setbinstring = cls._get_mtt_bin_name(str(setbin))
            except KeyError:
                cls._update_mtt_bin(setbin, name)
                setbinstring = cls._get_mtt_bin_name(str(setbin))

        return setbinstring

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, templatename=None):

        setbinstring = None
        if portobj_type == "pPass":
            return ''
        if updatesetbinstring[0] and portid not in cls.mtt_ignore_list:
            setbinstring = cls._get_mtt_autosetbinstring(setbin=setbin,
                                                         name=tname,
                                                         portid=portid,
                                                         lno=id_lno,
                                                         templatename=templatename)
        elif portid in cls.mtt_ignore_list:
            if portid == "rm2":
                setbinstring = ""
            elif portid == "rm1":
                setbinstring = ""

        # Update AutoBin dict
        if portid not in cls.mtt_ignore_list and setbin:
            # Write the bin info to the autobin dict to save as Autobinner
            if templatename in cls.autobindict:
                cls.autobindict[templatename][portid] = setbinstring
            else:
                cls.autobindict[templatename] = {portid: setbinstring}

            # Write the bin info to the autobin_internal dict to use internally.
            # Split is needed for both dicts as the bins were changing from run to run when they were being updated together.
            if templatename in cls.autobindict_internal:
                cls.autobindict_internal[templatename][portid] = setbinstring
            else:
                cls.autobindict_internal[templatename] = {portid: setbinstring}

        return setbinstring


class NVLClass8dig(BaseBin):
    """Binning strategy for NVL Class 8 digit bins which follows a 90HBSBXX format
    where HBSB is the 4 digit bin and XX is a unique 2-digit number for each HBSB.
    Refer to Pymtpl wiki for how the strategy"""

    ignore_list = ['rm1', 'rm2', 'r1', 'r5']
    default_thermal_reset_test_classes = ["VminTC", "MbistVminTC", "ApexTC"]

    @classmethod
    def default_setbinstring_dict(cls):
        """Return the dictionary for default setbinstring"""
        return {"rm1": f"{Initialize.tos_softbinstr}b90980101_fail_FAIL_SYSTEM_SOFTWARE",
                "rm2": f"{Initialize.tos_softbinstr}b90990101_fail_FAIL_DPS_ALARM"}

    @classmethod
    def get_thermal_or_reset_bin(cls, origbin, lno, bintype, tname):
        """For port4 and port5 default bin values because these are thermal/reset ports in MTL"""
        if origbin < 0:
            confirm(len(cls.bin_range) > 0, 'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin>')
            if cls.default_thermal_bin_dict:
                confirm(len(cls.default_thermal_bin_dict) == 1,
                        f'Cannot use setbin=AUTO in line# {lno} if there are multiple default thermal bins defined in Initialize',
                        f'Pls specify specific hardbin: setbin=-<hardbin> in line# {lno}.')
            if cls.default_reset_bin_dict:
                confirm(len(cls.default_reset_bin_dict) == 1,
                        f'Cannot use setbin=AUTO in line# {lno} if there are multiple default reset bins defined in Initialize',
                        f'Pls specify specific hardbin: setbin=-<hardbin> in line# {lno}.')

        origbin = str(origbin)

        if bintype == "thermal":
            if cls.default_thermal_bin_dict:
                if len(cls.default_thermal_bin_dict) == 1:
                    thermalbin = next(iter(cls.default_thermal_bin_dict.values()))
                    cls.all_4digit.add(str(thermalbin)[2:6])
                    return f"{Initialize.tos_softbinstr}b{thermalbin}_fail_PTH_DTS_XXX_{Initialize.get_modulename()}_THERMAL_PORT4_SHARED_BIN"
                else:
                    thermalbin = cls.default_thermal_bin_dict[origbin]
                    cls.all_4digit.add(str(thermalbin)[2:6])
                    return f"{Initialize.tos_softbinstr}b{thermalbin}_fail_PTH_DTS_XXX_{Initialize.get_modulename()}_THERMAL_PORT4_SHARED_BIN"
            else:
                if len(cls.bin_range) == 1:
                    # Set thermal and reset bins and add them to the all bin set so that they are not used.
                    newthermalbin = int("97" + str(cls.bin_range[0])[1:3])
                else:
                    # Set thermal and reset bins and add them to the all bin set so that they are not used.
                    newthermalbin = int("97" + origbin[1:3])

                cls.all_4digit.add(str(newthermalbin))
                return f"{Initialize.tos_softbinstr}b90{newthermalbin}00_fail_PTH_DTS_XXX_{Initialize.get_modulename()}_THERMAL_PORT4_SHARED_BIN"

        elif bintype == "reset":
            if cls.default_reset_bin_dict:
                if len(cls.default_reset_bin_dict) == 1:
                    resetbin = next(iter(cls.default_reset_bin_dict.values()))
                    cls.all_4digit.add(str(resetbin)[2:6])
                    return f"{Initialize.tos_softbinstr}b{resetbin}_fail_{Initialize.get_modulename()}_RESET_PORT5_SHARED_BIN"
                else:
                    resetbin = cls.default_reset_bin_dict[origbin]
                    cls.all_4digit.add(str(resetbin)[2:6])
                    return f"{Initialize.tos_softbinstr}b{resetbin}_fail_{Initialize.get_modulename()}_RESET_PORT5_SHARED_BIN"

            else:
                if len(cls.bin_range) == 1:
                    # Set thermal and reset bins and add them to the all bin set so that they are not used.
                    newresetbin = int(str(cls.bin_range[0])[1:3] + "19")
                else:
                    # Set thermal and reset bins and add them to the all bin set so that they are not used.
                    newresetbin = int(origbin[1:3] + "19")

                cls.all_4digit.add(str(newresetbin))
                return f"{Initialize.tos_softbinstr}b90{newresetbin}00_fail_{Initialize.get_modulename()}_RESET_PORT5_SHARED_BIN"

        else:
            raise ValueError("Invalid bintype. Expected 'thermal' or 'reset'.")

    @classmethod
    def _update_nonmtt_bin(cls, inputbin, dfi_name, portid):
        """
        Updates non-MTT bin_registry dictionary.

        :param inputbin: input setbin value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :forceupdate: Force update bin. Used by MTT where we want to update r4/r5.
                      DutFlowItem does not update r4/r5 as they are thermal/reset bins.
        :return: None
        """

        digit8 = str(inputbin)
        bin_name = f'{Initialize.tos_softbinstr}b{digit8}_fail_{Initialize.get_modulename()}_{dfi_name}'

        if digit8 not in cls.bin_registry:
            cls.bin_registry[digit8] = bin_name

        else:
            # this is shared bin if SHARED BIN tag is not added already or
            # if bin name is different from the one already stored. (Needed as 2 ports for the same test can
            # have the same bin which does not make it a shared bin)
            if not cls.bin_registry[digit8].endswith('_SHARED_BIN') and bin_name != cls.bin_registry[digit8]:
                cls.bin_registry[digit8] = f'{cls.bin_registry[digit8]}_SHARED_BIN'

    @classmethod
    def convert_4digit_to_8digit(cls, digit4):
        """
        :param digit4: 4 digit: HBSB
        :return: unique 8 digit number: 90HBSBXX
        """

        digit4 = str(digit4).zfill(4)
        digit6 = f"90{digit4}"
        # Create a unique key for each hard bin soft bin combo
        bincounter_value = "bincounter_start_" + digit6
        # For each HBSB, we want to start the counter from 0
        if bincounter_value not in cls.binctr_dict:
            cls.binctr_dict[bincounter_value] = 0
        loops = 0  # To prevent infinite loop
        while loops < 999:
            new_bincounter = int(digit6) * 100 + cls.binctr_dict[bincounter_value]
            new_bincounter = str(new_bincounter)
            # Check if bin is not already in use by bins or counters
            if new_bincounter not in cls.all_8digit and (Initialize.nonmttctrstrategy is None or new_bincounter not in Initialize.nonmttctrstrategy.all_8digit_counter):
                cls.all_8digit.add(new_bincounter)
                return new_bincounter
            cls.binctr_dict[bincounter_value] += 1
            loops += 1

    @classmethod
    def populate_internal_bin_trackers(cls, flow_obj):
        """
        Populates internal bin trackers with setbin values from the given flow object.
        :param flow_obj (FlowObject): The flow object containing items with port objects to be processed.

        :return None
        """
        for fitem in flow_obj.get_items():
            for portid, port_obj in fitem.ret_dict.items():
                if port_obj.setbin and port_obj.setbin > 0 and (len(str(port_obj.setbin)) in [7, 8]):
                    cls.all_8digit.add(str(port_obj.setbin))
                    cls.all_4digit.add(str(port_obj.setbin)[2:6])
                    # Also update the bin registry so that any shared bins are updated before generation of setbinstrings.
                    # This logic is being implemented in the NVLClass8dig strategy for the first time to close a potential gap/bug.
                    # Needs JDR review
                    # Previous logic for shared bin did not apply shared bin tag to the first test that uses the bin as we
                    # generated setbinstrings in a linear fashion. So the 1st test never had _SHARED_BIN tag
                    cls._update_nonmtt_bin(port_obj.setbin, fitem.ti.name, portid)

                # # Case when input setbin is 2/4 digit.
                elif port_obj.setbin and port_obj.setbin > 0:
                    raise ErrorUser(f"Invalid setbin value of {port_obj.setbin} in the Fitem definition of the test: {fitem.ti.name} in the line # {port_obj.id_lno}",
                                    "NVLClass8dig strategy requires 7 or 8-digit bin values in the form of 90HBSBXX as input for manual binning")

    @classmethod
    def update_autobindict(cls, bin, portid, tname, setbinstring):
        """Update the autobin dict to ensure sticky bins"""

        # Write the bin info to the autobin dict to save as Autobinner
        if tname in cls.autobindict:
            cls.autobindict[tname][portid] = bin
            cls.autobindict[tname]["bin"] = bin[2:6]
        else:
            cls.autobindict[tname] = {"bin": bin[2:6], portid: bin}
        # Write the bin info to the autobin_internal dict to use internally.
        # Split is needed for both dicts as the bins were changing from run to run when they were being updated together.
        if tname in cls.autobindict_internal:
            cls.autobindict_internal[tname][portid] = bin
            cls.autobindict_internal[tname]["bin"] = bin[2:6]
        else:
            cls.autobindict_internal[tname] = {"bin": bin[2:6], portid: setbinstring}

    @classmethod
    def _update_autobin_json(cls, input_fitem_info):
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
                    if test_name not in cls.bindictfrommtpl:
                        cls.bindictfrommtpl[test_name] = {}
                        cls.bindictfrommtpl[test_name]["bin"] = "NA"

                    setbininfo = cls._get_bin(portdata["SetBin"])
                    if setbininfo is not None:
                        if port == 0:
                            bin_value = setbininfo[2:6]
                            cls.bindictfrommtpl[test_name]["bin"] = bin_value

                        cls.bindictfrommtpl[test_name][portkey] = setbininfo

    @classmethod
    def _get_non_mtt_autosetbinstring(cls, setbin, name, updatesetbinstring, portid, lno):
        """
        Helper method to get the autosetbinstring for non-MTT.
        :param setbin (int): The current bin number.
        :param name (str): The name associated with the bin.
        :param updatesetbinstring (list): A list where the first element is a boolean indicating
                                          whether to update the bin string, and subsequent elements
                                          are used to store the new bin string.
        :param portid (str): The item for which the bin string is being determined.
        :param lno (int): The line number in the script where this method is called.
        :return str: The determined bin string for the given item.
        """
        # If present in the autobin dict, use the setbinstring from there
        if name in cls.autobindict_internal and portid in cls.autobindict_internal[name]:
            # If setbin is -1, we want to use the autobin dict value
            if setbin == -1 or setbin > 0:
                setbin = cls.autobindict_internal[name][portid]
                # Add it to internal 8 digit tracker so that this is not used again.
                cls.all_8digit.add(setbin)
                setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}'
                return setbinstring

            # If setbin is not -1, we need to account for changes - If previous setbin was -44 and new setbin is -45,
            # We need to use -45 to assign bin so that the binning is changed.
            # So the logic below to not blindly use what is in the cached autobin dict.
            if setbin < -1:
                newbin = str(setbin * -1)
                # Below check was added to handle cases where user gives 4 digit bin as input to autobinner
                # Test Case - test_class8dig_4dig_autobin_and_manual_then_repeat_auto in Class8dig tests
                # If user uses -4400 as the input bin then we only choose the first 2 digits.
                if len(newbin) == 4:
                    newbin = newbin[0:2]
                elif len(newbin) == 3:
                    # For 3-digit bins, pad with a leading zero and use only the first digit.
                    # This ensures the bin format is consistent with expected 2-digit representation.
                    newbin = "0" + newbin[0:1]
                oldbin = cls.autobindict_internal[name][portid][2:4]

                # If new bin is not in 97, 98 or 99 and old bin is 97, 98 or 99, that means we use 97HB/98HB/99HB
                # So our old bin is not first two digits but rather the 5th and 6th digits.
                if newbin not in ["97", "98", "99"] and oldbin in ["97", "98", "99"]:
                    oldbin = cls.autobindict_internal[name][portid][4:6]

                if newbin == oldbin:
                    setbin = cls.autobindict_internal[name][portid]
                    # Add it to internal 8 digit tracker so that this is not used again.
                    cls.all_8digit.add(setbin)
                    setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}'
                    return setbinstring

        if updatesetbinstring[0]:
            updatesetbinstring[0] = False
            newbin = cls.get_new_bin(setbin, lno + 1)
            dig8_newbin = cls.convert_4digit_to_8digit(newbin)
            updatesetbinstring.append(dig8_newbin)
            cls._update_nonmtt_bin(dig8_newbin, name, portid)
            return cls._get_non_mtt_bin_name(str(dig8_newbin))

        # Use the same 4 dig bin but get a unique 8-dig bin.
        setbin = updatesetbinstring[1]
        return cls._get_non_mtt_bin_name(str(setbin))

    @classmethod
    def get_new_bin(cls, origbin, lno):
        """
        Return a new bin, given the range, and iterating to all the PortObjects
        :param origbin: either 0 or -44
        :return: New 4 digit
        """
        if origbin < 0:
            confirm(len(cls.bin_range) > 0, 'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} or anywhere in the input file if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin> in order to use Autobin feature when using multiple bin ranges')
        origbin = str(origbin)

        digit4_bin = cls.get_unique_4dig_bin(origbin, lno)
        return digit4_bin

    @classmethod
    def get_non_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid, lno, test_class=None):
        """
        Return the string to be used for non-MTT port
        We want the same bin across ports (eg. p0, p2, p3)

        :return: string: setbin
        """
        setbinstring = None

        if updatesetbinstring[0]:
            updatesetbinstring[0] = False
            cls._update_nonmtt_bin(setbin, name, portid)
            setbinstring = cls._get_non_mtt_bin_name(str(setbin))
        else:
            try:
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))
            except KeyError:
                cls._update_nonmtt_bin(setbin, name, portid)
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))

        cls.sbdef_dict[setbinstring] = setbin   # Store the setbinstring and setbin in a dictionary
        return setbinstring

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, test_class=None):

        setbinstring = None
        if portobj_type == "pPass":
            return ''
        if portid == "rm2":
            setbinstring = cls.default_setbinstring_dict()["rm2"]
        elif portid == "rm1":
            setbinstring = cls.default_setbinstring_dict()["rm1"]
        elif portid == "r4" and test_class in cls.default_thermal_reset_test_classes:
            # Moving the thermal_reset function inside here because if we want to use InitializeMTL and give -2/-1 port defs for free,
            # we need to use Autobin without specifying bin range. So moving it to here makes more sense.
            setbinstring = cls.get_thermal_or_reset_bin(setbin, id_lno, "thermal", tname)

        elif portid == "r5" and test_class in cls.default_thermal_reset_test_classes:
            # Moving the thermal_reset function inside here because if we want to use InitializeMTL and give -2/-1 port defs for free,
            # we need to use Autobin without specifying bin range. So moving it to here makes more sense.
            setbinstring = cls.get_thermal_or_reset_bin(setbin, id_lno, "reset", tname)

        # We have coded a conditional for all the portids in the ignore list - rm2, rm1, r4 and r5.
        # Un-comment this out if we add any new portids to the ignore list in the future.
        # elif portid in cls.ignore_list:
        #     setbinstring = ''
        else:
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=setbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
            # Update autobindict only for non-thermal and non-reset bins
            bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
            cls.update_autobindict(bin, portid, tname, setbinstring)

        cls.sbdef_dict[setbinstring] = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
        return setbinstring


class MTTNVLClass8dig(NVLClass8dig):
    mtt_ignore_list = ['rm1', 'rm2', 'r1']

    @classmethod
    def convert_8digit_to_4digit(cls, digit8):
        """
        :param digit8: 8 digit: 90HBSBXX
        :return: 4 digit number: HBSB
        """

        digit4_bin = str(digit8)[2:6]
        return digit4_bin

    @classmethod
    def get_var_name(cls):
        return 'FlowMatrix.bin'

    @classmethod
    def _get_mtt_autosetbinstring(cls, setbin, name, portid, lno, templatename):
        """
        Helper method to get autosetbinstring for MTT.
        Args:
        :param setbin (int): The setbin value.
        :param name (str): The name of the non-MTT template.
        :param portid (str): The item to be returned.
        :param lno (int): The line number.
        :param templatename (str): The name of the MTT template.
        :return str: The setbin string for the MTT.

        Notes:
            - This method assumes that Fitems are written first followed by BaseMethods.
            - Handles cases where Fitem only has ignore ports, ensuring MTT does not ignore certain ports.
        """
        # For MTT, we just get the setbinstring based on the MTT name that has bin matrix etc in it so we use templatename
        if templatename in cls.autobindict_internal and portid not in cls.mtt_ignore_list and portid in cls.autobindict_internal[templatename] and setbin < 0:
            bin = cls.autobindict_internal[templatename][portid]
            setbinstring = f'"{Initialize.tos_softbinstr}b" + {cls.get_var_name()} + "{bin}_fail_{Initialize.get_modulename()}_{name}"'
            return setbinstring
        # For MTT when there is no value found in the loaded autobin dict, extract the information from Autobin dict updated during mtpl gen.
        # This will work as long as we write Fitems 1st and then BaseMethods because
        # we rely on the autobindict being populated 1st before moving on
        # This gets the setbin of the Fitem using the name of the non MTT template, and uses it for the MTT ports
        try:
            setbin = cls.autobindict_internal[name]["bin"]

        # Below code handles cases where Fitem only has ignore ports.
        # Since mtt does not ignore r4,r5, we need the handler code below - See test_autobin_ignore_ports_only()
        except KeyError:
            setbin = cls.get_new_bin(setbin, lno + 1)
            cls.autobindict_internal[name] = {"bin": setbin}

        cls._update_mtt_bin(setbin, name)
        return cls._get_mtt_bin_name(str(setbin))

    @classmethod
    def get_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid):
        """
        Return the string to be used for MTT port
        We want the same bin across ports (eg. p0, p2, p3)

        :return: string: setbin
        """
        setbinstring = None

        if (portid not in cls.ignore_list) and updatesetbinstring[0]:
            updatesetbinstring[0] = False
            cls._update_mtt_bin(setbin, name)
            setbinstring = cls._get_mtt_bin_name(str(setbin))
        else:
            try:
                setbinstring = cls._get_mtt_bin_name(str(setbin))
            except KeyError:
                cls._update_mtt_bin(setbin, name)
                setbinstring = cls._get_mtt_bin_name(str(setbin))

        return setbinstring

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, templatename=None):

        setbinstring = None
        if portobj_type == "pPass":
            return ''
        if updatesetbinstring[0] and portid not in cls.mtt_ignore_list:
            setbinstring = cls._get_mtt_autosetbinstring(setbin=setbin,
                                                         name=tname,
                                                         portid=portid,
                                                         lno=id_lno,
                                                         templatename=templatename)
            pattern = r'\b(\d{4})_fail_.*\b'
            # Extract bin from setbinstring to update the autobin dict
            mttbin = re.search(pattern, setbinstring)
            if mttbin is None:
                # You should always have the mttbin. Otherwise, there is an issue with the regex pattern.
                raise ErrorUser(f"Invalid setbinstring value of {setbinstring} for the MTT test: {tname} and port : {portid}",
                                "Please open a Pymtpl ticket to investigate this issue")
            else:
                mttbin = mttbin.group(1)
        elif portid in cls.mtt_ignore_list:
            if portid == "rm2":
                setbinstring = ""
            elif portid == "rm1":
                setbinstring = ""

        # Update AutoBin dict
        if portid not in cls.mtt_ignore_list and setbin:
            # Write the bin info to the autobin dict to save as Autobinner
            if templatename in cls.autobindict:
                cls.autobindict[templatename][portid] = mttbin
            else:
                cls.autobindict[templatename] = {portid: mttbin}

            # Write the bin info to the autobin_internal dict to use internally.
            # Split is needed for both dicts as the bins were changing from run to run when they were being updated together.
            if templatename in cls.autobindict_internal:
                cls.autobindict_internal[templatename][portid] = mttbin
            else:
                cls.autobindict_internal[templatename] = {portid: mttbin}

        return setbinstring


class ServerClass8dig(BaseBin):
    """Binning strategy for DMR Class 8 digit bins.
    Implements unique bins per port, matching counter.
    Unique bins on -2 and -1 ports too.
    """

    ignore_list = ['r1', 'r5']
    default_thermal_reset_test_classes = ["VminTC", "MbistVminTC"]
    sbdef_2dig_list = set()
    sbdef_prohibited_hardbins = []  # all hardbins are allowed in sbdef file
    sbdef_prohibited_databins = []  # all allowed

    @classmethod
    def clear_bins(cls):
        """Initialize class variables"""
        super().clear_bins()
        cls.sbdef_2dig_list.clear()

    @classmethod
    def _get_portstring(cls, portid):
        """
        Returns the port string for a given portid.
        :param portid: The port id (e.g., rm1, rm2, r4, r5, r0, r63, r102, etc.)
        :return: portstring (e.g., n1, n2, 4, 5, 63, 102, etc.)
        """
        # Use helper function to extract full port number
        port_number = BaseCounter._extract_port_number(portid)
        if "rm" in portid:
            return "n" + port_number  # n - negative port
        else:
            return port_number

    @classmethod
    def populate_internal_bin_trackers(cls, flow_obj):
        """
        Populates internal bin trackers with setbin values from the given flow object.
        :param flow_obj (FlowObject): The flow object containing items with port objects to be processed.

        :return None
        """
        for fitem in flow_obj.get_items():
            for portid, port_obj in fitem.ret_dict.items():
                # reserve any explicit 8 digit bins so that they can't be used by other ports
                if port_obj.setbin and port_obj.setbin > 0 and (len(str(port_obj.setbin)) == 8):
                    cls.all_8digit.add(str(port_obj.setbin))
                    cls.all_4digit.add(str(port_obj.setbin)[2:6])
                    # Also update the bin registry so that any shared bins are updated before generation of setbinstrings.
                    cls._update_nonmtt_bin(port_obj.setbin, fitem.ti.name, portid)
                elif port_obj.setbin and port_obj.setbin > 0:
                    raise ErrorUser(f"Invalid setbin value of {port_obj.setbin} in the Fitem definition of the test: {fitem.ti.name} in the line # {port_obj.id_lno}",
                                    "ServerClass8dig strategy requires setbin= 8-dig manual bin, 1 or 2 digit -HB, or 3 or 4 digit-HBSB (matched to left bound of bin range)")

    @classmethod
    def get_non_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid, lno, test_class=None):
        """
        Return the string to be used for non-MTT port
        We want a unique bin for every port

        :return: string: setbin
        """
        setbinstring = None

        # print("calling get_non_mtt_setbinstring for setbin:", setbin, "name:", name, "portid:", portid)
        setbin = str(setbin)

        if setbin not in cls.bin_registry:
            cls._update_nonmtt_bin(setbin, name, portid)
        setbinstring = cls._get_non_mtt_bin_name(setbin)

        cls.sbdef_dict[setbinstring] = setbin   # Store the setbinstring and setbin in a dictionary
        return setbinstring

    @classmethod
    def _get_non_mtt_bin_name(cls, setbin):
        """
        Helper method to get the bin name for non-MTT.
        :param setbin: eight digit bin
        :return: the bin name
        """
        return cls.bin_registry[setbin]

    @classmethod
    def _update_nonmtt_bin(cls, inputbin, dfi_name, portid):
        """
        Updates non-MTT bin_registry dictionary.

        :param inputbin: input setbin value which should be 8 digits
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :param portid: This is the portid (ex rm1, rm2, r4, r5)
        :forceupdate: Force update bin. Used by MTT where we want to update r4/r5.
                      DutFlowItem does not update r4/r5 as they are thermal/reset bins.
        :return: None
        """
        # print(f"ServerClass8dig._update_nonmtt_bin called with inputbin: {inputbin}, dfi_name: {dfi_name}, portid: {portid}")

        portstring = cls._get_portstring(portid)
        digit8 = str(inputbin)

        # create bin name
        bin_name = f'{Initialize.tos_softbinstr}b{digit8}_fail_{Initialize.get_modulename()}_{dfi_name}_{portstring}'

        if digit8 not in cls.bin_registry:
            cls.bin_registry[digit8] = bin_name
        else:
            # this is shared bin if SHARED BIN tag is not added already or
            # if bin name is different from the one already stored. (Needed as 2 ports for the same test can
            # have the same bin which does not make it a shared bin)
            if not cls.bin_registry[digit8].endswith('_SHARED_BIN') and bin_name != cls.bin_registry[digit8]:
                cls.bin_registry[digit8] = f'{cls.bin_registry[digit8]}_SHARED_BIN'

    @classmethod
    def _get_softbin_name(cls, softbin):
        """
        Returns the softbin name for a given 4 digit bin.
        :param softbin_4dig: 4 digit bin
        :return: softbin name
        """
        hardbin = softbin[0:2]
        confirm(hardbin in Initialize.bindefdict, f"Unable to extract the bin classification for the bin {hardbin}.", f"Please check the bin {softbin} exists in the bindefdict")

        # if softbin exists directly, use that
        if softbin in Initialize.bindefdict:
            return Initialize.bindefdict[softbin]

        # overriding some defaults for DMR
        if (hardbin == "98"):
            return "98xx_fail_FAIL_SYSTEM_SOFTWARE".replace("98xx", softbin)
        elif (hardbin == "99"):
            return "99xx_fail_FAIL_DPS_ALARM".replace("99xx", softbin)

        # default behavior: softbin is named like hardbin (1: means without the b at the start)
        return Initialize.bindefdict[hardbin].replace(hardbin, softbin)[1:]

    @classmethod
    def _get_non_mtt_autosetbinstring(cls, setbin, name, updatesetbinstring, portid, lno):
        """
        Helper method to get the autosetbinstring for non-MTT.
        :param setbin (int): The current bin number.
        :param name (str): The name associated with the bin.
        :param updatesetbinstring (list): A list where the first element is a boolean indicating
                                          whether to update the bin string, and subsequent elements
                                          are used to store the new bin string.
        :param portid (str): The item for which the bin string is being determined.
        :param lno (int): The line number in the script where this method is called.
        :return str: The determined bin string for the given item.
        """

        portstring = cls._get_portstring(portid)

        # print ("ServerClass8dig._get_non_mtt_autosetbinstring called with setbin: ", setbin, " name: ", name, " portid: ", portid)
        # If present in the autobin dict, use the setbinstring from there
        if name in cls.autobindict_internal and portid in cls.autobindict_internal[name]:
            # for setting from hardbin, reuse the autobin dict value IFF the setbin matches
            if setbin < -1:
                newbin = str(setbin * -1)
                # we can have anywhere from 1 to 4 digits here for HB or HBSB, e.g. 8, 68, 800, 6800
                # ensure len_newbin rounds up to 2 or 4 digits
                len_newbin = len(newbin)
                if len_newbin == 1:
                    newbin = newbin.zfill(2)
                elif len_newbin == 3:
                    newbin = newbin.zfill(4)
                len_newbin = len(newbin)

                oldbin = cls.autobindict_internal[name][portid][2:2 + len_newbin]  # we will need 2-4 digits depending on if it's HB or HBSB
                if int(newbin) == int(oldbin):
                    setbin = cls.autobindict_internal[name][portid]
                    setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}_{portstring}'
                    return setbinstring
            # for AUTO bins, make sure the hardbin hasn't changed
            elif setbin == -1:
                newbin = str(cls.bin_range[0][0]).zfill(4)[0:2]  # extract the hardbin from the only bin range
                oldbin = cls.autobindict_internal[name][portid][2:4]
                if int(newbin) == int(oldbin):
                    setbin = cls.autobindict_internal[name][portid]
                    setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}_{portstring}'
                    return setbinstring

        # default behavior when setting up a bin for the first time
        dig8_newbin = cls.get_new_bin_8dig(setbin, lno + 1)
        cls._update_nonmtt_bin(dig8_newbin, name, portid)
        return cls._get_non_mtt_bin_name(str(dig8_newbin))

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, test_class=None):
        setbinstring = None
        if portobj_type == "pPass":
            return ''
        # We have coded a conditional for all the ret items in the ignore list - rm2, rm1, r4 and r5.
        # Un-comment this out if we add any new portids to the ignore list in the future.
        # elif portid in cls.ignore_list:
        #     setbinstring = ''
        else:
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=setbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
            bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
            cls.update_autobindict(bin, portid, tname, setbinstring)

        cls.sbdef_dict[setbinstring] = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
        return setbinstring

    @classmethod
    def update_autobindict(cls, bin, portid, tname, setbinstring):
        """Update the autobin dict to ensure sticky bins"""
        # Write the bin info to the autobin dict to save as Autobinner
        if tname in cls.autobindict:
            cls.autobindict[tname][portid] = bin
        else:
            cls.autobindict[tname] = {portid: bin}
        if portid not in ["rm1", "rm2"]:
            cls.autobindict[tname]["bin"] = bin
        # Write the bin info to the autobin_internal dict to use internally.
        # Split is needed for both dicts as the bins were changing from run to run when they were being updated together.
        if tname in cls.autobindict_internal:
            cls.autobindict_internal[tname][portid] = bin
        else:
            cls.autobindict_internal[tname] = {portid: bin}
        if portid not in ["rm1", "rm2"]:
            cls.autobindict_internal[tname]["bin"] = bin

    @classmethod
    def get_new_bin_8dig(cls, origbin, lno):
        """
        Return a new bin, given the range
        :param origbin: either 0 or -44
        :return: New 8 digit
        """
        if origbin < 0:
            confirm(len(cls.bin_range) > 0, 'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} or anywhere in the input file if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin> in order to use Autobin feature when using multiple bin ranges')
        origbin = str(origbin)

        digit8_bin = cls.get_available_8dig_bin(origbin, lno)
        return digit8_bin

    @classmethod
    def get_available_8dig_bin(cls, origbin, lno):
        usableBinranges = []
        bin_str_len = len(str(origbin))
        for i in range(len(cls.bin_range)):
            if origbin == "-1":  # AUTO case
                usableBinranges.append(0)
            elif origbin[0] == '-' and bin_str_len in [2, 3]:  # -HB case - we want an auto-bin based on the HB.  2-3 length because of -8 or -68
                filled_origbin = origbin[1:].zfill(2)  # Fill with zeros to make it 2 digits
                filled_binrange = str(cls.bin_range[i][0]).zfill(4)  # fill with zeroes to make it 4 digits to compare
                if (filled_origbin == filled_binrange[0:2]):
                    usableBinranges.append(i)
            elif origbin[0] == '-' and bin_str_len in [4, 5]:  # -HBSB case - we want an auto-bin based on the HBSB.  4-5 length because of -810 or -6810
                filled_origbin = origbin[1:].zfill(4)  # Fill with zeros to make it 4 digits
                filled_binrange = str(cls.bin_range[i][0]).zfill(4)  # fill with zeroes to make it 4 digits to compare
                if (filled_origbin == filled_binrange[0:4]):
                    usableBinranges.append(i)

        if usableBinranges == []:
            bin98add = "" if origbin not in ['-98', '-99'] else " Please make sure bin 98/99 ranges are set."
            raise ErrorUser(f"Please check the definition of setbin={origbin} in line # {lno}",
                            f"Either the binrange or setbin are incorrect. Need 8-dig manual bin, 1 or 2 digit -HB, or 3 or 4 digit-HBSB (matched to left bound of bin range).{bin98add}")

        # note we are NOT updating the all_4digit dictionary because we want to reuse those categories
        for binrange in usableBinranges:
            binrange = cls.bin_range[binrange]
            for target in range(binrange[0], binrange[1] + 1):
                digit4 = str(target).zfill(4)
                for i in range(100):
                    digit8 = '90' + digit4 + str(i).zfill(2)
                    if digit8 not in cls.all_8digit and digit8 not in Initialize.nonmttctrstrategy.all_8digit_counter:
                        cls.all_8digit.add(digit8)
                        return int(digit8)

        raise ErrorUser(f"Unable to find a valid 8-digit bin in the specified range: {cls.bin_range} for setbin={origbin} in line# {lno}", lno)


class Sort8dig(BaseBin):
    """Binning strategy for Sort 8 digit bins which follows a HBSBXXXX format
    where HBSB is the 4 digit bin and XXXX is a unique number for each HBSB"""
    ignore_list = ['rm1', 'rm2', 'r1', 'r5']

    @classmethod
    def set_bin_range(cls, binrange):
        """Set the bin range value and check validity"""
        if isinstance(binrange, tuple):
            cls.bin_range.append(binrange)    # One range
        else:
            cls.bin_range.extend(binrange)    # multiple ranges

        # check bin_range correctness
        for item in cls.bin_range:
            confirm(isinstance(item, (list, tuple)) and len(item) == 2,
                    f'Expecting a tuple or a list of tuples as the binrange for: item "{item}"',
                    'Pls fix binrange so that it is binrange = (start, end) or [(start1, end1), (start2, end2), ...]')

            # Check if the values are 3/4/5/6/7/8 digits long
            start, end = item
            confirm(len(str(start)) in (3, 4, 5, 6, 7, 8) and len(str(end)) in (3, 4, 5, 6, 7, 8),
                    f'Expecting start and end values to be 3, 4, 5, 6, 7, or 8 digits long for binrange "{item}"',
                    'Pls fix binrange so that start and end values are 3-8 digits long - Ex - (4400,4401) for 4-digit, (986800,986849) for 6-digit')

    @classmethod
    def get_default_port_bin_counter_start(cls):
        """
        Function to get the starting counter for default ports
        :return: Starting counter for default ports
        """

        if cls.bin_range:
            seed = cls.bin_range[0][0]
        else:
            seed = int(next(iter(cls.all_4digit)))

        random.seed(seed)
        base_value = random.randint(0, 7000)

        return base_value

    @classmethod
    def get_default_bins(cls, origbin, lno, bin_type, portid, tname):
        """For port minus 2, minus 1, port4 and port5 default bin values """
        if origbin < 0:
            confirm(len(cls.bin_range) > 0,
                    f'No binrange specified while AutoBin is trying to be used in line no# {lno} for the test {tname} and port {portid} with setbin={origbin}',
                    f'Pls specify binrange in your Initialize call so that Autobin can be used')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin>')
        origbin = str(origbin)
        if len(cls.bin_range) == 1 and origbin == "-1":
            if len(str(cls.bin_range[0][0])) == 3:
                binstring_value = str(cls.bin_range[0][0])[0:1].zfill(2)
            else:
                binstring_value = str(cls.bin_range[0][0])[0:2]
            # Set thermal and reset bins and add them to the all bin set so that they are not used.
            newthermalbin = int("97" + binstring_value)
            newresetbin = int(binstring_value + "19")
            newsftwrbin = int("98" + binstring_value)
            newclmpbin = int("99" + binstring_value)
        else:
            if len(origbin) == 2:
                binstring_value = origbin[1:2].zfill(2)
            else:
                binstring_value = origbin[1:3]
            # Set thermal and reset bins and add them to the all bin set so that they are not used.
            newthermalbin = int("97" + binstring_value)
            newresetbin = int(binstring_value + "19")
            newsftwrbin = int("98" + binstring_value)
            newclmpbin = int("99" + binstring_value)

        if bin_type == "software":
            return newsftwrbin
        elif bin_type == "reset":
            return newresetbin
        elif bin_type == "clamp":
            return newclmpbin
        else:
            raise ValueError("Invalid bin_type. Expected 'software', 'clamp' or 'reset'.")

    @classmethod
    def load_autobinfile(cls):
        cls.autobindict = {}
        # Internal bindict is used to load the autobinner json info.
        # We need this because we want the non internal bin dict to be updated during the mtpl generation.
        # This way we can keep them both separate and make any un-used bins available again.
        autobindict_internal = {}
        autobinfilename = str(Initialize.get_modulename()) + "_AutoBinner.json"
        filepath = os.path.join(os.path.dirname(Initialize.get_outfile()), 'PymtplInputFiles', autobinfilename)
        cls.autobinfilepath = filepath
        if Initialize.usebinctrfrommtpl:
            autobindict_internal = cls.bindictfrommtpl
        else:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    autobindict_internal = json.load(f)
        # Load the bins from the dictionary into the all_4digit set so that they are not re-used.
        for k, v in autobindict_internal.items():
            try:
                cls.all_4digit.add(v['bin'])
                for k, value in v.items():
                    if k != "bin":
                        cls.all_8digit.add(value)
            except KeyError:
                pass

        cls.autobindict_internal = autobindict_internal

    @classmethod
    def convert_4digit_to_8digit(cls, digit4):
        """
        :param digit4: 4 digit: HBSB
        :return: unique 8 digit number: HBSBXXXX
        """
        if len(str(digit4)) == 3:
            dig4_zfill = 3
            dig8_zfill = 7
        elif len(str(digit4)) == 4:
            dig4_zfill = 4
            dig8_zfill = 8

        digit4 = str(digit4).zfill(dig4_zfill)
        # Create a unique key for each hard bin soft bin combo
        bincounter_value = "bincounter_start_" + digit4
        # For each HBSB, we want to start the counter from 0
        if bincounter_value not in cls.binctr_dict:
            cls.binctr_dict[bincounter_value] = 0
        for _ in range(1000000):
            new_bincounter = int(digit4) * 10000 + cls.binctr_dict[bincounter_value]
            new_bincounter = str(new_bincounter).zfill(dig8_zfill)
            if new_bincounter not in cls.all_8digit:
                cls.all_8digit.add(new_bincounter)
                return new_bincounter
            cls.binctr_dict[bincounter_value] += 1

    @classmethod
    def convert_4digit_to_8digit_default_ports(cls, digit4):
        """
        :param digit4: 4 digit: HBSB
        :return: unique 8 digit number: HBSBXXXX
        """

        digit4 = str(digit4)
        # Create a unique key for each hard bin soft bin combo
        bincounter_value = "bincounter_start_" + digit4
        # For each HBSB, we want to start the counter from 0
        if bincounter_value not in cls.binctr_dict:
            cls.binctr_dict[bincounter_value] = cls.get_default_port_bin_counter_start()
        for _ in range(1000000):
            new_bincounter = int(digit4) * 10000 + cls.binctr_dict[bincounter_value]
            new_bincounter = str(new_bincounter)
            if new_bincounter not in cls.all_8digit:
                cls.all_8digit.add(new_bincounter)
                return new_bincounter
            cls.binctr_dict[bincounter_value] += 1

    @classmethod
    def _update_nonmtt_bin(cls, inputbin, dfi_name, portid, portobj_type='pFail'):
        """
        Updates non-MTT bin_registry dictionary.

        :param inputbin: input setbin value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :param portobj_type: Port type ('pPass' or 'pFail'), used to set pass/fail in bin name
        :forceupdate: Force update bin. Used by MTT where we want to update r4/r5.
                      DutFlowItem does not update r4/r5 as they are thermal/reset bins.
        :return: None
        """
        # Use helper function to extract full port number
        port_number = BaseCounter._extract_port_number(portid)
        if "rm" in portid:
            poststring = "n" + port_number  # n - negative port
        else:
            poststring = port_number
        digit8 = str(inputbin)
        passfail = 'pass' if portobj_type == 'pPass' else 'fail'
        if digit8 not in cls.bin_registry:

            bin_name = f'{Initialize.tos_softbinstr}b{digit8}_{passfail}_{Initialize.get_modulename()}_{dfi_name}_{poststring}'
            cls.bin_registry[digit8] = bin_name
        else:
            # this is shared bin
            if not cls.bin_registry[digit8].endswith('_SHARED_BIN'):
                cls.bin_registry[digit8] = f'{cls.bin_registry[digit8]}_SHARED_BIN'

    @classmethod
    def _get_non_mtt_autosetbinstring(cls, setbin, name, updatesetbinstring, portid, lno):
        """
        Helper method to get the autosetbinstring for non-MTT.
        :param setbin (int): The current bin number.
        :param name (str): The name associated with the bin.
        :param updatesetbinstring (list): A list where the first element is a boolean indicating
                                          whether to update the bin string, and subsequent elements
                                          are used to store the new bin string.
        :param portid (str): The item for which the bin string is being determined.
        :param lno (int): The line number in the script where this method is called.
        :return str: The determined bin string for the given item.
        """
        # Use helper function to extract full port number
        port_number = BaseCounter._extract_port_number(portid)
        # If present in the autobin dict, use the setbinstring from there
        if name in cls.autobindict_internal and portid in cls.autobindict_internal[name]:
            if "rm" in portid:
                poststring = "n" + port_number  # n - negative port
            else:
                poststring = port_number

            # If setbin is -1, we want to use the autobin dict value
            if setbin == -1 or setbin > 0:
                setbin = cls.autobindict_internal[name][portid]
                setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                return setbinstring

            # If setbin is not -1, we need to account for changes - If previous setbin was -44 and new setbin is -45,
            # We need to use -45 to assign bin so that the binning is changed.
            # So the logic below to not blindly use what is in the cached autobin dict.
            if setbin < -1:
                newbin = str(setbin * -1)
                oldbin = cls.autobindict_internal[name][portid][0:2]
                # If new bin is not in 97, 98 or 99 and old bin is 97, 98 or 99, that means we use 97HB/98HB/99HB
                # So our old bin is not first two digits but rather the 3rd and 4th digits.
                if newbin not in ["97", "98", "99"] and oldbin in ["97", "98", "99"]:
                    oldbin = cls.autobindict_internal[name][portid][2:4]

                if newbin == oldbin:
                    setbin = cls.autobindict_internal[name][portid]
                    setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                    return setbinstring

        if portid not in cls.ignore_list and updatesetbinstring[0]:

            updatesetbinstring[0] = False
            newbin = cls.get_new_bin(setbin, lno + 1)
            updatesetbinstring.append(newbin)
            dig8_newbin = cls.convert_4digit_to_8digit(newbin)
            cls._update_nonmtt_bin(dig8_newbin, name, portid)
            return cls._get_non_mtt_bin_name(str(dig8_newbin))

        elif portid in cls.ignore_list:
            dig8_newbin = cls.convert_4digit_to_8digit_default_ports(setbin)
            cls._update_nonmtt_bin(dig8_newbin, name, portid)
            return cls._get_non_mtt_bin_name(str(dig8_newbin))

        # Use the same 4 dig bin but get a unique 8-dig bin.

        setbin = updatesetbinstring[1]
        dig8_newbin = cls.convert_4digit_to_8digit(setbin)
        cls._update_nonmtt_bin(dig8_newbin, name, portid)
        return cls._get_non_mtt_bin_name(str(dig8_newbin))

    @classmethod
    def populate_internal_bin_trackers(cls, flow_obj):
        """
        Populates internal bin trackers with setbin values from the given flow object.
        :param flow_obj (FlowObject): The flow object containing items with port objects to be processed.

        :return None
        """
        for fitem in flow_obj.get_items():
            for _, port_obj in fitem.ret_dict.items():
                if port_obj.setbin and port_obj.setbin > 0 and len(str(port_obj.setbin)) >= 7:
                    cls.all_8digit.add(str(port_obj.setbin))
                if port_obj.setbin and port_obj.setbin > 0 and (len(str(port_obj.setbin)) == 3 or len(str(port_obj.setbin)) == 4):
                    cls.all_4digit.add(str(port_obj.setbin))

    @classmethod
    def get_new_bin(cls, origbin, lno):
        """
        Return a new bin, given the range, and iterating to all the PortObjects
        :param origbin: either 0 or -44
        :return: New 4 digit
        """
        if origbin < 0:
            confirm(len(cls.bin_range) > 0, 'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} or anywhere in the input file if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin> in order to use Autobin feature when using multiple bin ranges')
        origbin = str(origbin)
        # iterate all port objects and get all setbin

        digit4_bin = cls.get_unique_4dig_bin(origbin, lno)

        return digit4_bin

    @classmethod
    def get_non_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid, lno, test_class=None):
        """
        Return the string to be used for non-MTT port
        We want different bins across ports (eg. p0, p2, p3)

        :return: string: setbin
        """
        setbinstring = None

        if (len(str(setbin)) == 3 or len(str(setbin)) == 4):
            # Check if the setbin is in the autobin dict - Needed at Sort because same 4 digit bin can be used by different 8-digit bins.
            # Artifact of allowing 4 digit bin usage in Sort
            if name in cls.autobindict_internal and portid in cls.autobindict_internal[name]:
                # Use helper function to extract full port number
                port_number = BaseCounter._extract_port_number(portid)
                if "rm" in portid:
                    poststring = "n" + port_number  # n - negative port
                else:
                    poststring = port_number
                previous_setbin = cls.autobindict_internal[name][portid]
                # Bin like 8000000 should be compared as 800
                if len(previous_setbin) == 7:
                    prev_setbin_for_compare = previous_setbin[0:3]
                # Bins like 44000000 should be compared as 4400
                elif len(previous_setbin) == 8:
                    prev_setbin_for_compare = previous_setbin[0:4]

                new_setbin = str(setbin)
                # If the new setbin is the same as old then use the cached version.
                if prev_setbin_for_compare == new_setbin:
                    setbinstring = f'{Initialize.tos_softbinstr}b{previous_setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                    cls.update_autobindict(str(previous_setbin), portid, name, setbinstring)
                    return setbinstring
                elif portid in ["rm2", "rm1"]:
                    # For -2, -1 we only check the 2 digit hard bin and not the entire 4 digits.
                    if previous_setbin[2:4] == new_setbin[2:4]:
                        setbinstring = f'{Initialize.tos_softbinstr}b{previous_setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                        return setbinstring
                    else:
                        setbin = cls.convert_4digit_to_8digit_default_ports(new_setbin)
                # If new setbin is not the same, then get a new 8 digit bin.
                else:
                    setbin = cls.convert_4digit_to_8digit(setbin)
            elif portid in ["rm2", "rm1"]:
                setbin = cls.convert_4digit_to_8digit_default_ports(setbin)
            # If the setbin is not in the autobin dict, then get a new 8 digit bin.
            else:
                setbin = cls.convert_4digit_to_8digit(setbin)

            # Only update the autobin dict if the bin is 3 or 4 dig long as autobinner is taking over in that case.
            cls.update_autobindict(str(setbin), portid, name, setbinstring)

        if (portid not in cls.ignore_list) and updatesetbinstring[0]:
            updatesetbinstring[0] = True
            cls._update_nonmtt_bin(setbin, name, portid)
            setbinstring = cls._get_non_mtt_bin_name(str(setbin))
        else:
            try:
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))
            except KeyError:
                cls._update_nonmtt_bin(setbin, name, portid)
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))

        return setbinstring

    @classmethod
    def update_autobindict(cls, bin, portid, tname, setbinstring):
        """Update the autobin dict to ensure sticky bins"""

        # Write the bin info to the autobin dict to save as Autobinner
        if tname in cls.autobindict:
            cls.autobindict[tname][portid] = bin
            if portid not in cls.ignore_list:  # Do not update bin for ignore ports
                cls.autobindict[tname]["bin"] = bin[0:4]
        else:
            if portid not in cls.ignore_list:
                cls.autobindict[tname] = {"bin": bin[0:4], portid: bin}
            elif portid in cls.ignore_list:
                cls.autobindict[tname] = {"bin": "NA", portid: bin}
        # Write the bin info to the autobin_internal dict to use internally.
        # Split is needed for both dicts as the bins were changing from run to run when they were being updated together.
        if tname in cls.autobindict_internal:
            cls.autobindict_internal[tname][portid] = bin
            if portid not in cls.ignore_list:  # Do not update bin for ignore ports
                cls.autobindict_internal[tname]["bin"] = bin[0:4]
        else:
            if portid not in cls.ignore_list:
                cls.autobindict_internal[tname] = {"bin": bin[0:4], portid: setbinstring}
            elif portid in cls.ignore_list:
                cls.autobindict_internal[tname] = {"bin": "NA", portid: setbinstring}

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, test_class=None):

        setbinstring = None
        if portobj_type == "pPass":
            return ''
        if portid == "rm2":
            clampbin = cls.get_default_bins(setbin, id_lno, "clamp", portid, tname)
            cls.all_4digit.add(str(clampbin))
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=clampbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
        elif portid == "rm1":
            softwarebin = cls.get_default_bins(setbin, id_lno, "software", portid, tname)
            cls.all_4digit.add(str(softwarebin))
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=softwarebin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)

        elif portid == "r5":
            # Moving the thermal_reset function inside here because if we want to use InitializeMTL and give -2/-1 port defs for free,
            # we need to use Autobin without specifying bin range. So moving it to here makes more sense.
            resetbin = cls.get_default_bins(setbin, id_lno, "reset", portid, tname)
            # Add the thermal and reset bins to the all_4digit bin list so that they are not used for any of the tests
            cls.all_4digit.add(str(resetbin))

            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=resetbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
        # We have coded a conditional for all the ret items in the ignore list - rm2, rm1, r4 and r5.
        # Un-comment this out if we add any new portids to the ignore list in the future.
        # elif portid in cls.ignore_list:
        #     setbinstring = ''
        else:

            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=setbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)

        if setbin:

            bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
            cls.update_autobindict(bin, portid, tname, setbinstring)

        return setbinstring


class NVLClassHBSBXXXX(Sort8dig):
    """Binning strategy for HBSBXXXX format
    where HBSB is the 4 digit bin and XXXX is a unique number for each HBSB
    This is a derivative of Sort8dig with specific requirements for NVL Class:
    - Every port does not need a counter
    - VminTC/MBistVminTC Port 4 is 97HBXXXX (thermal)
    - VminTC/MBistVminTC Port 5 is HB19XXXX (reset)
    """
    ignore_list = ['rm1', 'rm2', 'r1']
    default_thermal_reset_test_classes = ["VminTC", "MbistVminTC", "ApexTC"]
    sbdef_prohibited_hardbins = []  # all hardbins are allowed in sbdef file
    sbdef_prohibited_databins = []  # all allowed

    @classmethod
    def separate_bin_ranges(cls):
        """Separate bin_range into 4-digit and 8-digit ranges"""
        new_bin_range = []
        cls.dig8_bin_range = []
        for item in cls.bin_range:
            start, end = item
            if len(str(start)) in (7, 8) and len(str(end)) in (7, 8):
                cls.dig8_bin_range.append(item)
            else:
                new_bin_range.append(item)

        cls.bin_range = new_bin_range

    @classmethod
    def get_new_bin(cls, origbin, lno):
        """
        Return a new bin, given the range, and iterating to all the PortObjects
        :param origbin: either 0 or -44
        :return: New 4 digit
        """
        if origbin < 0:
            confirm(len(cls.bin_range) > 0 or len(cls.dig8_bin_range) > 0,
                    'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(
                (len(cls.bin_range) == 1) ^ (len(cls.dig8_bin_range) == 1),
                f'Cannot use setbin=AUTO in line# {lno} or anywhere in the input file if there are multiple bin_range: {cls.bin_range}',
                'Pls specify specific hardbin: setbin=-<hardbin> in order to use Autobin feature when using multiple bin ranges')
        origbin = str(origbin)
        # iterate all port objects and get all setbin

        digit4_bin = cls.get_unique_4dig_bin(origbin, lno)

        return digit4_bin

    @classmethod
    def get_unique_4dig_bin(cls, origbin, lno):
        # If negative bin
        usableBinranges = []
        usable8DigBinranges = []

        # First check 4-digit bin ranges
        for i in range(len(cls.bin_range)):
            # For a 3-digit bin range (e.g., 801–805), extract the first digit of the lower bound (e.g., '8' from '801') for comparison
            if len(str(cls.bin_range[i][0])) == 3:
                comparevalue = str(cls.bin_range[i][0])[0:1]
            # For a 4-digit bin range like (4400, 4405), extract the first 2 digits ('44') for comparison purposes
            else:
                comparevalue = str(cls.bin_range[i][0])[0:2]
            if len(origbin) == 2 and (origbin[1:]) == str(cls.bin_range[i][0])[0:1]:
                usableBinranges.append(i)
            elif len(origbin) > 3 and (origbin[1:]) == str(cls.bin_range[i][0])[0:]:
                usableBinranges.append(i)
            elif len(origbin) == 3 and (origbin[1:3]) == comparevalue:
                usableBinranges.append(i)
            elif origbin == "-1":
                usableBinranges.append(0)

        # Then check 8-digit bin ranges
        for i in range(len(cls.dig8_bin_range)):
            start_8dig = str(cls.dig8_bin_range[i][0])
            # Extract the 4-digit HBSB portion from the 8-digit bin
            if len(start_8dig) == 7:
                hbsb_from_8dig = start_8dig[0:3]  # For 7-digit: HBSXXXX -> HBS
            else:  # 8-digit
                hbsb_from_8dig = start_8dig[0:4]  # For 8-digit: HBSBXXXX -> HBSB

            # Compare with origbin
            if origbin == "-1":
                usable8DigBinranges.append(i)
            elif len(origbin) == 2 and origbin[1:] == hbsb_from_8dig[0:1]:  # Compare HB portion
                usable8DigBinranges.append(i)
            elif len(origbin) == 3 and origbin[1:3] == hbsb_from_8dig[0:2]:  # Compare HB portion
                usable8DigBinranges.append(i)
            elif len(origbin) == 4 and origbin[1:4] == hbsb_from_8dig[0:3]:  # Compare HBS for 7-digit
                usable8DigBinranges.append(i)
            elif len(origbin) == 5 and origbin[1:5] == hbsb_from_8dig[0:4]:  # Compare HBSB for 8-digit
                usable8DigBinranges.append(i)

        if usableBinranges == [] and usable8DigBinranges == []:
            raise ErrorUser(f"Please check the definition of setbin in line # {lno}",
                            f"Either the binrange or setbin user specified are incorrect. Pls fix.")

        # First try to find bins from 4-digit ranges
        for binrange in usableBinranges:
            binrange = cls.bin_range[binrange]
            for target in range(binrange[0], binrange[1] + 1):
                digit4 = str(target).zfill(4)
                if digit4 not in cls.all_4digit:
                    cls.all_4digit.add(digit4)
                    return int(digit4)     # this is our new bin

        # Then try to extract unique 4-digit bins from 8-digit ranges
        for binrange_idx in usable8DigBinranges:
            binrange = cls.dig8_bin_range[binrange_idx]
            # Extract all unique 4-digit prefixes from the 8-digit range
            start_8dig = str(binrange[0])
            end_8dig = str(binrange[1])

            if len(start_8dig) == 7:
                digit4 = start_8dig[0:3].zfill(4)  # Extract HBS and zero-fill to 4 digits
            else:  # 8-digit
                digit4 = start_8dig[0:4]  # Extract HBSB

            if digit4 not in cls.all_4digit:
                cls.all_4digit.add(digit4)
                return int(digit4)

        # If all the bins are exhausted, we start the loop again
        # But this time we do not add the new bin to the all_4digit set
        # nor do we check if the bin is already in the all_4digit set
        for binrange in usableBinranges:
            binrange = cls.bin_range[binrange]
            for target in range(binrange[0], binrange[1] + 1):
                digit4 = str(target).zfill(4)
                return int(digit4)

        # Also try 8-digit ranges again without checking
        for binrange_idx in usable8DigBinranges:
            binrange = cls.dig8_bin_range[binrange_idx]
            start_8dig = str(binrange[0])

            if len(start_8dig) == 7:
                digit4 = start_8dig[0:3].zfill(4)
            else:  # 8-digit
                digit4 = start_8dig[0:4]

            return int(digit4)

    @classmethod
    def _get_hardbin_match(cls, bin, use_databin_prohibited_list=False):
        """
        Returns the 2 digit hardbin bin match for a given 8 digit bin.
        Skips hardbins in sbdef_prohibited_hardbins
        :param bin: 8 digit bin (format: bHHXXXXXX where HH is the 2-digit hardbin or bHXXXXXX for 1-digit)
        :return: 2 digit hardbin bin match or None if not found
        """

        # First check for 8-digit bins (b followed by 8 digits)
        if use_databin_prohibited_list and cls.sbdef_prohibited_databins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_databins)
            regex_8dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{2}}(?=\d{{6}})'
        elif cls.sbdef_prohibited_hardbins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_hardbins)
            regex_8dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{2}}(?=\d{{6}})'
        else:
            regex_8dig = r'(?:SetBin.*)?b\d{2}(?=\d{6})'

        bin_2dig_match = re.search(regex_8dig, bin)
        if bin_2dig_match:
            return bin_2dig_match.group(0)[1:]

        # If no 8-digit match, check for 7-digit bins (b followed by 7 digits)
        if use_databin_prohibited_list and cls.sbdef_prohibited_databins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_databins)
            regex_7dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{1}}(?=\d{{6}})'
        elif cls.sbdef_prohibited_hardbins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_hardbins)
            regex_7dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{1}}(?=\d{{6}})'
        else:
            regex_7dig = r'(?:SetBin.*)?b\d{1}(?=\d{6})'

        bin_1dig_match = re.search(regex_7dig, bin)
        if bin_1dig_match:
            return bin_1dig_match.group(0)[1:].zfill(2)  # Pad single digit to 2 digits - Since bin dict looks for 07/08 etc

        return None

    @classmethod
    def _get_softbin_match(cls, bin, use_databin_prohibited_list=False):
        """
        Returns the 4 digit hbsb match for a given 8 digit bin or 3 digit for 7 digit bin.
        Skips hardbins in sbdef_prohibited_hardbins
        :param bin: 8 digit bin (format: bHHSBXXXXXX) or 7 digit bin (format: bHSBXXXXXX)
        :return: 4 digit hbsb match for 8-digit bins, 3 digit for 7-digit bins, or None if not found
        """
        # First check for 8-digit bins (b followed by 8 digits) - extract 4 digits after 'b'
        if use_databin_prohibited_list and cls.sbdef_prohibited_databins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_databins)
            regex_8dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{4}}(?=\d{{4}})'
        elif cls.sbdef_prohibited_hardbins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_hardbins)
            regex_8dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{4}}(?=\d{{4}})'
        else:
            regex_8dig = r'(?:SetBin.*)?b\d{4}(?=\d{4})'

        bin_4dig_match = re.search(regex_8dig, bin)
        if bin_4dig_match:
            return bin_4dig_match.group(0)[1:]  # Extract 4 digits after 'b'

        # If no 8-digit match, check for 7-digit bins (b followed by 7 digits) - extract 3 digits after 'b'
        if use_databin_prohibited_list and cls.sbdef_prohibited_databins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_databins)
            regex_7dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{3}}(?=\d{{4}})'
        elif cls.sbdef_prohibited_hardbins:
            negative_lookahead = '|'.join(cls.sbdef_prohibited_hardbins)
            regex_7dig = rf'(?:SetBin.*)?b(?!{negative_lookahead})\d{{3}}(?=\d{{4}})'
        else:
            regex_7dig = r'(?:SetBin.*)?b\d{3}(?=\d{4})'

        bin_3dig_match = re.search(regex_7dig, bin)
        if bin_3dig_match:
            return bin_3dig_match.group(0)[1:]  # Extract 3 digits after 'b'

        return None

    @classmethod
    def set_default_thermal_reset_bins(cls):
        """
        Sets the default thermal and reset bins if defined in the Initialize call.
        """

        if Initialize.defaultthermalbin is None:
            cls.usable_thermal_bins = []
        elif isinstance(Initialize.defaultthermalbin, tuple):
            cls.usable_thermal_bins.append(Initialize.defaultthermalbin)
        elif isinstance(Initialize.defaultthermalbin, list):
            cls.usable_thermal_bins.extend(Initialize.defaultthermalbin)
        elif isinstance(Initialize.defaultthermalbin, int):
            cls.usable_thermal_bins = Initialize.defaultthermalbin

        if Initialize.defaultresetbin is None:
            cls.usable_reset_bins = []
        elif isinstance(Initialize.defaultresetbin, tuple):
            cls.usable_reset_bins.append(Initialize.defaultresetbin)
        elif isinstance(Initialize.defaultresetbin, list):
            cls.usable_reset_bins.extend(Initialize.defaultresetbin)
        elif isinstance(Initialize.defaultresetbin, int):
            cls.usable_reset_bins = Initialize.defaultresetbin

        if Initialize.defaultrm1bin is None:
            cls.usable_rm1_bins = []
        elif isinstance(Initialize.defaultrm1bin, tuple):
            cls.usable_rm1_bins.append(Initialize.defaultrm1bin)
        elif isinstance(Initialize.defaultrm1bin, list):
            cls.usable_rm1_bins.extend(Initialize.defaultrm1bin)
        elif isinstance(Initialize.defaultrm1bin, int):
            cls.usable_rm1_bins = Initialize.defaultrm1bin

        if Initialize.defaultrm2bin is None:
            cls.usable_rm2_bins = []
        elif isinstance(Initialize.defaultrm2bin, tuple):
            cls.usable_rm2_bins.append(Initialize.defaultrm2bin)
        elif isinstance(Initialize.defaultrm2bin, list):
            cls.usable_rm2_bins.extend(Initialize.defaultrm2bin)
        elif isinstance(Initialize.defaultrm2bin, int):
            cls.usable_rm2_bins = Initialize.defaultrm2bin

    @classmethod
    def get_default_bins(cls, origbin, lno, bin_type, portid, tname):
        """For port minus 2, minus 1, port4 and port5 default bin values """
        if origbin < 0:
            confirm(len(cls.bin_range) > 0 or len(cls.dig8_bin_range) > 0,
                    f'No binrange specified while AutoBin is trying to be used in line no# {lno} for the test {tname} and port {portid} with setbin={origbin}',
                    f'Pls specify binrange in your Initialize call so that Autobin can be used')

        if origbin == -1:
            confirm(
                (len(cls.bin_range) == 1) ^ (len(cls.dig8_bin_range) == 1),
                f'Cannot use setbin=AUTO in line# {lno} if there are multiple bin_range: {cls.bin_range} or dig8_bin_range: {cls.dig8_bin_range}',
                'Pls specify exactly one bin range (either bin_range or dig8_bin_range) with length 1 to use setbin=AUTO'
            )
        origbin = str(origbin)
        if len(cls.bin_range) == 1 and origbin == "-1":
            if len(str(cls.bin_range[0][0])) == 3:
                binstring_value = str(cls.bin_range[0][0])[0:1].zfill(2)
            else:
                binstring_value = str(cls.bin_range[0][0])[0:2]
            # Set thermal and reset bins and add them to the all bin set so that they are not used.
            newthermalbin = int("97" + binstring_value)
            newresetbin = int(binstring_value + "19")
            newsftwrbin = int("98" + binstring_value)
            newclmpbin = int("99" + binstring_value)
        # Case when we use AUTO and only 8-digit range is specified
        elif len(cls.dig8_bin_range) == 1 and origbin == "-1":
            if len(str(cls.dig8_bin_range[0][0])) == 7:
                binstring_value = str(cls.dig8_bin_range[0][0])[0:1].zfill(2)
            else:
                binstring_value = str(cls.dig8_bin_range[0][0])[0:2]
            # Set thermal and reset bins and add them to the all bin set so that they are not used.
            newthermalbin = int("97" + binstring_value)
            newresetbin = int(binstring_value + "19")
            newsftwrbin = int("98" + binstring_value)
            newclmpbin = int("99" + binstring_value)
        else:
            if len(origbin) == 2:
                binstring_value = origbin[1:2].zfill(2)
            else:
                binstring_value = origbin[1:3]
            # Set thermal and reset bins and add them to the all bin set so that they are not used.
            newthermalbin = int("97" + binstring_value)
            newresetbin = int(binstring_value + "19")
            newsftwrbin = int("98" + binstring_value)
            newclmpbin = int("99" + binstring_value)

        if bin_type == "software":
            return newsftwrbin
        elif bin_type == "reset":
            return newresetbin
        elif bin_type == "clamp":
            return newclmpbin
        elif bin_type == "thermal":
            return newthermalbin
        else:
            raise ValueError("Invalid bin_type. Expected 'software', 'clamp', 'thermal' or 'reset'.")

    @classmethod
    def convert_4digit_to_8digit(cls, digit4):
        """
        Convert a 4-digit bin (HBSB) to a unique 8-digit bin (HBSBXXXX).

        :param digit4: 4-digit hardbin/softbin (HBSB)
        :return: Unique 8-digit bin in format HBSBXXXX

        This method uses multiple strategies to generate unique 8-digit bins:

        1. **8-digit bin ranges (dig8_bin_range)**: If defined, generates bins within
           the exact 8-digit ranges specified in Initialize(). This provides full control
           over the entire 8-digit bin space.

        2. **Counter ranges (ctrrangeforbins)**: If defined, generates bins by combining
           the 4-digit HBSB with a counter from the specified range. For example:
           - digit4=4400, ctrrangeforbins=(2000,2500) → generates 44002000, 44002001, etc.
           This constrains only the XXXX portion while allowing the HBSB to vary.
           The counter is persistent across calls for each unique HBSB.

        3. **Default counter**: If no ranges are defined, uses an unlimited counter
           starting from 0 for each unique HBSB (original behavior).

        The method tries strategies in order (1, 2, 3) and raises ErrorUser if all
        defined ranges are exhausted.
        """
        if len(str(digit4)) == 3:
            dig4_zfill = 3
            dig8_zfill = 7
        elif len(str(digit4)) == 4:
            dig4_zfill = 4
            dig8_zfill = 8

        digit4 = str(digit4).zfill(dig4_zfill)

        # NEW: If 8-digit ranges are defined, use them to constrain bin generation
        if cls.dig8_bin_range:
            # Find matching range for this HBSB
            for bin_range in cls.dig8_bin_range:
                start, end = bin_range
                confirm(start < end,
                        f"Invalid 8-digit bin range {bin_range} defined in Initialize()",
                        f"Please ensure that the start of the range is less than the end.")
                start_str = str(start).zfill(dig8_zfill)
                end_str = str(end).zfill(dig8_zfill)

                # Check if this range matches our HBSB (first 3 or 4 digits)
                if start_str[:dig4_zfill] == digit4:
                    # Generate bin within this specific range
                    for candidate in range(int(start_str), int(end_str) + 1):
                        candidate_str = str(candidate).zfill(dig8_zfill)
                        if candidate_str not in cls.all_8digit:
                            cls.all_8digit.add(candidate_str)
                            return candidate_str
                    # If range exhausted, raise error
                    raise ErrorUser(
                        f"8-digit bin range {bin_range} for HBSB {digit4} is exhausted",
                        f"Please expand the 8-digit binrange for {digit4} or review bin usage"
                    )

        if cls.ctrrangeforbins:
            # Find matching range for this HBSB
            for ctrrange in cls.ctrrangeforbins:
                start, end = ctrrange
                confirm(start <= end,
                        f"Invalid 4-digit ctr range {ctrrange} defined in Initialize()",
                        f"Please ensure that the start of the range is less than the end.")

                bincounter_value = "bincounter_start_" + digit4
                if bincounter_value not in cls.binctr_dict:
                    cls.binctr_dict[bincounter_value] = start
                # Iterate through counter values, not full 8-digit bins.
                # CRITICAL: Use max(saved_counter, range_start) to prevent counter from bleeding into gaps.
                # Example with ctrrangeforbins=[(56, 56), (58, 2000)]:
                #   - Call 1: range(56, 57) → counter 56, saved_counter becomes 57
                #   - Call 2: range(max(57, 56), 57) → exhausted (57 >= 57)
                #   - Call 2: range(max(57, 58), 2001) → starts at 58 (skips gap at 57!)
                #   - Call 3: range(max(59, 58), 2001) → continues at 59
                # Without max(), counter 57 would bleed into range (58, 2000) creating unwanted bin.
                for counter in range(max(cls.binctr_dict[bincounter_value], start), end + 1):
                    new_bincounter = int(digit4) * 10000 + counter
                    new_bincounter = str(new_bincounter).zfill(dig8_zfill)
                    if new_bincounter not in cls.all_8digit:
                        cls.all_8digit.add(new_bincounter)
                        cls.binctr_dict[bincounter_value] = counter + 1  # Save next counter
                        return new_bincounter

            # All ranges exhausted
            raise ErrorUser(
                f"All counter ranges for HBSB {digit4} are exhausted",
                f"Please expand ctrrangeforbins or review bin usage"
            )

        # EXISTING LOGIC: Original counter-based approach for when no 8-digit range is defined
        bincounter_value = "bincounter_start_" + digit4
        if bincounter_value not in cls.binctr_dict:
            cls.binctr_dict[bincounter_value] = 0
        for _ in range(1000000):
            new_bincounter = int(digit4) * 10000 + cls.binctr_dict[bincounter_value]
            new_bincounter = str(new_bincounter).zfill(dig8_zfill)
            if new_bincounter not in cls.all_8digit:
                cls.all_8digit.add(new_bincounter)
                return new_bincounter
            cls.binctr_dict[bincounter_value] += 1

    @classmethod
    def convert_4digit_to_8digit_default_ports(cls, digit4, portid, name):
        """
        :param digit4: 4 digit: HBSB
        :return: unique 8 digit number: HBSBXXXX
        """
        if portid == 'r4':
            binrangetouse = cls.usable_thermal_bins
            binrangetype = "defaultthermalbin"
            rangetouse = "-HB or (97HBXXXX, 97HBYYYY) or [(97HBXXXX, 97HBYYYY)]"
        elif portid == 'r5':
            binrangetouse = cls.usable_reset_bins
            binrangetype = "defaultresetbin"
            rangetouse = "-HB or (HB19XXXX, HB19YYYY) or [(HB19XXXX, HB19YYYY)]"
        elif portid == 'rm1':
            binrangetouse = cls.usable_rm1_bins
            binrangetype = "defaultrm1bin"
            rangetouse = "-HB or (98HBXXXX, 98HBYYYY) or [(98HBXXXX, 98HBYYYY)]"
        elif portid == 'rm2':
            binrangetouse = cls.usable_rm2_bins
            binrangetype = "defaultrm2bin"
            rangetouse = "-HB or (99HBXXXX, 99HBYYYY) or [(99HBXXXX, 99HBYYYY)]"

        usableBinranges = []
        origbin_str = str(digit4)

        if binrangetouse and not isinstance(binrangetouse, int):
            for i in range(len(binrangetouse)):
                # For a 3-digit bin range (e.g., 801–805), extract the first digit of the lower bound (e.g., '8' from '801') for comparison
                if len(str(binrangetouse[i][0])) == 7:
                    comparevalue = str(binrangetouse[i][0])[0:3]
                # For a 4-digit bin range like (4400, 4405), extract the first 2 digits ('44') for comparison purposes
                else:
                    comparevalue = str(binrangetouse[i][0])[0:4]
                if len(origbin_str) > 3 and (origbin_str) == str(binrangetouse[i][0])[0:4]:
                    usableBinranges.append(i)
                elif len(origbin_str) == 3 and (origbin_str) == comparevalue:
                    usableBinranges.append(i)
                elif len(origbin_str) == 3 and (origbin_str[1:3]) == comparevalue:
                    usableBinranges.append(i)
                # Future update : Commented below code as it is incorrect behavior.
                # No bin range match means error out instead use first range
                # Only append 0 if this is the last element and no matches have been found
                # elif i == len(binrangetouse) - 1 and not usableBinranges:
                #     usableBinranges.append(0)

        elif Initialize.default_counter_range:

            # Handle both single tuple and list of tuples
            counter_ranges = Initialize.default_counter_range
            if isinstance(counter_ranges[0], int):
                # Single tuple case: [1000, 2000]
                counter_ranges = [counter_ranges]

            # Iterate through all counter ranges
            for counter_range in counter_ranges:
                start, end = counter_range
                for i in range(start, end + 1):
                    digit8 = origbin_str + str(i).zfill(4)
                    if digit8 not in cls.all_8digit:
                        cls.all_8digit.add(digit8)
                        return digit8

        if not usableBinranges:
            raise ErrorUser(f"No HB match found for {portid} in test {name}. {digit4} in {binrangetype} is not in {binrangetouse} in Initialize.",
                            f"If using setbin=-HB, {binrangetype} must follow the convention of {rangetouse} ")

        for binrange in usableBinranges:
            binrange = binrangetouse[binrange]
            for target in range(binrange[0], binrange[1] + 1):
                digit8_common_bin_range_start = str(target).zfill(8)
                # Compose 8-digit bin, e.g., HBSBXXXX (you may want to adjust this logic for your format)
                for counter in range(1000):
                    digit8 = str(int(digit8_common_bin_range_start) + counter)
                    if digit8 not in cls.all_8digit:
                        cls.all_8digit.add(digit8)
                        return digit8  # this is our new 8-digit bin

    @classmethod
    def _get_non_mtt_autosetbinstring(cls, setbin, name, updatesetbinstring, portid, lno):
        """
        Helper method to get the autosetbinstring for non-MTT.
        :param setbin (int): The current bin number.
        :param name (str): The name associated with the bin.
        :param updatesetbinstring (list): A list where the first element is a boolean indicating
                                          whether to update the bin string, and subsequent elements
                                          are used to store the new bin string.
        :param portid (str): The item for which the bin string is being determined.
        :param lno (int): The line number in the script where this method is called.
        :return str: The determined bin string for the given item.
        """
        # If present in the autobin dict, use the setbinstring from there
        if name in cls.autobindict_internal and portid in cls.autobindict_internal[name]:
            # Use helper function to extract full port number
            port_number = BaseCounter._extract_port_number(portid)
            if "rm" in portid:
                poststring = "n" + port_number  # n - negative port
            else:
                poststring = port_number

            # If setbin is -1, we want to use the autobin dict value
            if setbin == -1 or setbin > 0:
                setbin = cls.autobindict_internal[name][portid]

                setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                cls.sbdef_dict[setbinstring] = setbin
                return setbinstring

            # If setbin is not -1, we need to account for changes - If previous setbin was -44 and new setbin is -45,
            # We need to use -45 to assign bin so that the binning is changed.
            # So the logic below to not blindly use what is in the cached autobin dict.
            if setbin < -1:
                newbin = str(setbin * -1)
                if len(newbin) != 2:
                    # Always use the HB portion for comparison
                    # Ex - If input is -7600, we will compare 76 to 76
                    newbin = newbin[0:2]
                oldbin = cls.autobindict_internal[name][portid][0:2]
                # If new bin is not in 97, 98 or 99 and old bin is 97, 98 or 99, that means we use 97HB/98HB/99HB
                # So our old bin is not first two digits but rather the 3rd and 4th digits.
                if newbin not in ["97", "98", "99"] and oldbin in ["97", "98", "99"]:
                    oldbin = cls.autobindict_internal[name][portid][2:4]
                if newbin == oldbin:
                    setbin = cls.autobindict_internal[name][portid]
                    setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                    cls.sbdef_dict[setbinstring] = setbin
                    return setbinstring

        if int(setbin) > 0:
            # TODO: Fix this for future Sort standard class.
            # This will only be true when the update_autosetbinstring passes 97HB or HB19
            # i.e. for VminTC, MBistVminTC and ApexTC test classes we want to use the default port 4 to 8 digit converter
            # This is a bug fix fron Sort8dig - Cannot change there as we are deep into execution
            dig8_newbin = cls.convert_4digit_to_8digit_default_ports(setbin, portid, name)
            cls._update_nonmtt_bin(dig8_newbin, name, portid)
            setbinstring = cls._get_non_mtt_bin_name(str(dig8_newbin))
            cls.sbdef_dict[setbinstring] = setbin
            return cls._get_non_mtt_bin_name(str(dig8_newbin))

        if portid not in cls.ignore_list and updatesetbinstring[0]:

            updatesetbinstring[0] = False
            newbin = cls.get_new_bin(setbin, lno + 1)
            updatesetbinstring.append(newbin)
            dig8_newbin = cls.convert_4digit_to_8digit(newbin)
            cls._update_nonmtt_bin(dig8_newbin, name, portid)
            setbinstring = cls._get_non_mtt_bin_name(str(dig8_newbin))
            cls.sbdef_dict[setbinstring] = setbin
            return cls._get_non_mtt_bin_name(str(dig8_newbin))

        # This will never be true
        # All cases for ignore list are handled above so this below code is not needed
        # elif portid in cls.ignore_list:
        #     dig8_newbin = cls.convert_4digit_to_8digit_default_ports(setbin, portid, name)
        #     cls._update_nonmtt_bin(dig8_newbin, name, portid)
        #     setbinstring = cls._get_non_mtt_bin_name(str(dig8_newbin))
        #     cls.sbdef_dict[setbinstring] = setbin
        #     return cls._get_non_mtt_bin_name(str(dig8_newbin))

        # Use the same 4 dig bin but get a unique 8-dig bin.
        setbin = updatesetbinstring[1]
        dig8_newbin = cls.convert_4digit_to_8digit(setbin)
        cls._update_nonmtt_bin(dig8_newbin, name, portid)
        setbinstring = cls._get_non_mtt_bin_name(str(dig8_newbin))
        cls.sbdef_dict[setbinstring] = setbin
        return cls._get_non_mtt_bin_name(str(dig8_newbin))

    @classmethod
    def _is_thermal_reset_port(cls, test_class, portid, setbin):
        """Check if this is a thermal port (r4, bin 97) or reset port (r5, bin XX19)"""
        if len(str(setbin)) == 3:
            resetbinchars = str(setbin)[1:3]
        else:
            resetbinchars = str(setbin)[2:4]
        if test_class not in cls.default_thermal_reset_test_classes:
            return False
        if portid == "r4" and str(setbin)[0:2] == "97":
            return True
        if portid == "r5" and resetbinchars == "19":
            return True
        return False

    @classmethod
    def get_non_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid, lno, test_class=None):
        """
        Return the string to be used for non-MTT port
        We want different bins across ports (eg. p0, p2, p3)

        :return: string: setbin
        """
        setbinstring = None

        if (len(str(setbin)) == 3 or len(str(setbin)) == 4):
            # Check if the setbin is in the autobin dict - Needed at Sort because same 4 digit bin can be used by different 8-digit bins.
            # Artifact of allowing 4 digit bin usage in Sort
            if name in cls.autobindict_internal and portid in cls.autobindict_internal[name]:
                # Use helper function to extract full port number
                port_number = BaseCounter._extract_port_number(portid)
                if "rm" in portid:
                    poststring = "n" + port_number  # n - negative port
                else:
                    poststring = port_number
                previous_setbin = cls.autobindict_internal[name][portid]
                # Bin like 8000000 should be compared as 800
                if len(previous_setbin) == 7:
                    prev_setbin_for_compare = previous_setbin[0:3]
                # Bins like 44000000 should be compared as 4400
                elif len(previous_setbin) == 8:
                    prev_setbin_for_compare = previous_setbin[0:4]

                new_setbin = str(setbin)
                # If the new setbin is the same as old then use the cached version.
                if prev_setbin_for_compare == new_setbin:
                    setbinstring = f'{Initialize.tos_softbinstr}b{previous_setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                    cls.update_autobindict(str(previous_setbin), portid, name, setbinstring)
                    # Update SBDef dict with the previous setbin which is the 7 or 8 digit bin
                    cls.sbdef_dict[setbinstring] = previous_setbin
                    return setbinstring
                elif portid in ["rm2", "rm1"]:
                    # For -2, -1 we only check the 2 digit hard bin and not the entire 4 digits.
                    if previous_setbin[2:4] == new_setbin[2:4]:
                        setbinstring = f'{Initialize.tos_softbinstr}b{previous_setbin}_fail_{Initialize.get_modulename()}_{name}_{poststring}'
                        # Update SBDef dict with the previous setbin which is the 7 or 8 digit bin
                        cls.sbdef_dict[setbinstring] = previous_setbin
                        return setbinstring
                    else:
                        setbin = cls.convert_4digit_to_8digit_default_ports(new_setbin, portid, name)
                # If new setbin is not the same, then get a new 8 digit bin.
                else:
                    setbin = cls.convert_4digit_to_8digit(setbin)
            elif portid in ["rm2", "rm1"]:
                if int(setbin) > 0:
                    if portid == "rm2" and str(setbin)[0:2] != "99":
                        raise ErrorUser(f"Trying to assign {setbin} to portid {portid} in test {name}.",
                                        f"For portid 'rm2', setbin must start with '99' when using manual bins.")
                    if portid == "rm1" and str(setbin)[0:2] != "98":
                        raise ErrorUser(f"Trying to assign {setbin} to portid {portid} in test {name}.",
                                        f"For portid 'rm1', setbin must start with '98' when using manual bins.")
                setbin = cls.convert_4digit_to_8digit_default_ports(setbin, portid, name)
            elif cls._is_thermal_reset_port(test_class, portid, setbin):
                setbin = cls.convert_4digit_to_8digit_default_ports(setbin, portid, name)
            # If the setbin is not in the autobin dict, then get a new 8 digit bin.
            else:
                setbin = cls.convert_4digit_to_8digit(setbin)

            # Only update the autobin dict if the bin is 3 or 4 dig long as autobinner is taking over in that case.
            cls.update_autobindict(str(setbin), portid, name, setbinstring)

        if (portid not in cls.ignore_list) and updatesetbinstring[0]:
            updatesetbinstring[0] = True
            cls._update_nonmtt_bin(setbin, name, portid)
            setbinstring = cls._get_non_mtt_bin_name(str(setbin))
        else:
            try:
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))
            except KeyError:
                cls._update_nonmtt_bin(setbin, name, portid)
                setbinstring = cls._get_non_mtt_bin_name(str(setbin))
        # Update SBDef dict with the new 8 digit setbin
        # This update handles the final 8-digit setbin after all conversions and reuse checks are complete, unlike the earlier updates which handle reused bins.
        cls.sbdef_dict[setbinstring] = setbin
        return setbinstring

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, test_class=None):

        setbinstring = None
        if portobj_type == "pPass":
            return ''
        if portid == "rm2":
            clampbin = cls.get_default_bins(setbin, id_lno, "clamp", portid, tname)
            cls.all_4digit.add(str(clampbin))
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=clampbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
        elif portid == "rm1":
            softwarebin = cls.get_default_bins(setbin, id_lno, "software", portid, tname)
            cls.all_4digit.add(str(softwarebin))
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=softwarebin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)

        elif portid == "r4" and test_class in cls.default_thermal_reset_test_classes:
            # Moving the thermal_reset function inside here because if we want to use InitializeMTL and give -2/-1 port defs for free,
            # we need to use Autobin without specifying bin range. So moving it to here makes more sense.
            thermalbin = cls.get_default_bins(setbin, id_lno, "thermal", portid, tname)
            # Add the thermal and reset bins to the all_4digit bin list so that they are not used for any of the tests
            cls.all_4digit.add(str(thermalbin))
            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=thermalbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)

        elif portid == "r5" and test_class in cls.default_thermal_reset_test_classes:
            # Moving the thermal_reset function inside here because if we want to use InitializeMTL and give -2/-1 port defs for free,
            # we need to use Autobin without specifying bin range. So moving it to here makes more sense.
            resetbin = cls.get_default_bins(setbin, id_lno, "reset", portid, tname)
            # Add the thermal and reset bins to the all_4digit bin list so that they are not used for any of the tests
            cls.all_4digit.add(str(resetbin))

            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=resetbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)
        # We have coded a conditional for all the ret items in the ignore list - rm2, rm1, r4 and r5.
        # Un-comment this out if we add any new portids to the ignore list in the future.
        # elif portid in cls.ignore_list:
        #     setbinstring = ''
        else:

            setbinstring = cls._get_non_mtt_autosetbinstring(setbin=setbin,
                                                             name=tname,
                                                             updatesetbinstring=updatesetbinstring,
                                                             portid=portid,
                                                             lno=id_lno)

        if setbin:

            bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
            cls.sbdef_dict[setbinstring] = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
            cls.update_autobindict(bin, portid, tname, setbinstring)

        return setbinstring


class JGSClass(NVLClassHBSBXXXX):
    """Binning strategy for HBSBXXXX format
    where HBSB is the 4 digit bin and XXXX is a unique number for each HBSB
    - Every port needs a counter
    - We do not need a unique softbin per test
    """
    ignore_list = ['r1']
    default_thermal_reset_test_classes = []
    sbdef_prohibited_hardbins = []  # all hardbins are allowed in sbdef file
    sbdef_prohibited_databins = []  # all allowed
    sbdef_2dig_list = set()

    @classmethod
    def clear_bins(cls):
        """Initialize class variables"""
        super().clear_bins()
        cls.sbdef_2dig_list.clear()

    @classmethod
    def _get_portstring(cls, portid):
        """
        Returns the port string for a given portid.
        :param portid: The port id (e.g., rm1, rm2, r4, r5, r0, etc.)
        :return: portstring (e.g., n1, n2, 4, 5, etc.)
        """
        if "rm" in portid:
            return "n" + str(portid)[-1]  # n - negative port
        else:
            return str(portid)[-1]

    @classmethod
    def get_new_bin(cls, origbin, lno):
        """
        Return a new bin, given the range
        :param origbin: either 0 or -44
        :return: New 8 digit
        """
        confirm(len(cls.bin_range) > 0, 'No bin_range specified', 'Pls specify binrange in Initialize()')

        if origbin == -1:
            confirm(len(cls.bin_range) == 1,
                    f'Cannot use setbin=AUTO in line# {lno} or anywhere in the input file if there are multiple bin_range: {cls.bin_range}',
                    'Pls specify specific hardbin: setbin=-<hardbin> in order to use Autobin feature when using multiple bin ranges')
        origbin = str(origbin)

        digit8_bin = cls.get_available_8dig_bin(origbin, lno)
        return digit8_bin

    @classmethod
    def get_available_8dig_bin(cls, origbin, lno):
        ''' here we match the -HB/-HBSB/-HBSBXX to the left bound of the bin range
            and then check all possible 8-digit bins within that range
            until we find one that is not used yet.
        '''
        usableBinranges = []
        bin_str_len = len(str(origbin))
        for i in range(len(cls.bin_range)):
            if origbin == "-1":  # AUTO case
                usableBinranges.append(0)
            else:
                confirm(origbin[0] == '-' and bin_str_len >= 2,
                        f"Invalid setbin value: {origbin} in line# {lno}.", "Please provide a valid negative setbin value.")
                # Extract the numeric part of setbin (remove the minus sign)
                setbin_value = origbin[1:]
                num_digits = len(setbin_value)

                # Validate that setbin has reasonable length (1-8 digits)
                if num_digits < 1 or num_digits > 8:
                    raise ErrorUser(f"Invalid setbin value: {origbin} in line# {lno}.",
                                    f"setbin must have 1-8 digits after the minus sign.")

                # Compute the 8-digit representation of the range start
                # (mirrors the zfill + suffix logic used during bin generation)
                range_start = cls.bin_range[i][0]
                range_n = len(str(range_start))
                if range_n <= 4:
                    r_pad, r_suf = 4, 4
                elif range_n <= 6:
                    r_pad, r_suf = 6, 2
                else:
                    r_pad, r_suf = 8, 0
                bin8_range = str(range_start).zfill(r_pad) + "0" * r_suf

                # For odd-digit setbins (1, 3, 5, 7), the single-digit HB gets
                # zero-padded to 2 digits in the 8-digit format (e.g. HB=9 -> "09").
                # Round up to the next even length so the comparison always aligns
                # with the 8-digit representation of the range.
                expanded_len = num_digits + (num_digits % 2)
                setbin_expanded = setbin_value.zfill(expanded_len)

                # Compare the expanded setbin against the corresponding prefix of
                # the 8-digit range representation.
                # e.g. -9 -> "09" matches "09120000" (range 912) but NOT "99000000" (range 9900)
                if setbin_expanded == bin8_range[:expanded_len]:
                    usableBinranges.append(i)

        if usableBinranges == []:
            bin98add = "" if origbin not in ['-98', '-99'] else " Please make sure bin 98/99 ranges are set."
            raise ErrorUser(f"Please check the definition of setbin={origbin} in line # {lno}",
                            f"Either the binrange or setbin are incorrect. Need 8-dig manual bin, 1-8 digit -HB/-HBSB/-HBSBXX (matched to left bound of bin range).{bin98add}")

        # note we are NOT updating the all_4digit dictionary because we want to reuse those categories
        for binrange in usableBinranges:
            binrange = cls.bin_range[binrange]

            # Determine the format of the bin range to support different specificities
            # binrange can be (HBSB, HBSB) [4 digits], (HBSBXX, HBSBXX) [6 digits]
            range_start_len = len(str(binrange[0]))

            # Determine how many digits we need to pad and how many to iterate
            if range_start_len <= 4:
                # 4-digit HBSB format: pad to 4 digits, add 4 more (10000 possibilities)
                pad_len = 4
                suffix_len = 4
                suffix_range = 10000
            elif range_start_len <= 6:
                # 6-digit HBSBXX format: pad to 6 digits, add 2 more (100 possibilities)
                pad_len = 6
                suffix_len = 2
                suffix_range = 100
            else:
                # 8-digit HBSBXX format: pad to 8 digits, add 0 more (1 possibility)
                pad_len = 8
                suffix_len = 0
                suffix_range = 1

            for target in range(binrange[0], binrange[1] + 1):
                prefix = str(target).zfill(pad_len)
                for i in range(suffix_range):
                    if suffix_len > 0:
                        digit8 = prefix + str(i).zfill(suffix_len)
                    else:
                        digit8 = prefix
                    if digit8 not in cls.all_8digit and digit8 not in Initialize.nonmttctrstrategy.all_8digit_counter:
                        cls.all_8digit.add(digit8)
                        return digit8  # this is a string, so we get the preceding 0 for HB < 10

        raise ErrorUser(f"Unable to find a valid 8-digit bin in the specified range: {cls.bin_range} for setbin={origbin} in line# {lno}", lno)

    @classmethod
    def separate_bin_ranges(cls):
        """DON'T Separate bin_range into 4-digit and 8-digit ranges"""
        pass

    @classmethod
    def _get_non_mtt_autosetbinstring(cls, setbin, name, updatesetbinstring, portid, lno, portobj_type='pFail'):
        """
        Helper method to get the autosetbinstring for non-MTT.
        :param setbin (int): The current bin number.
        :param name (str): The name associated with the bin.
        :param updatesetbinstring (list): A list where the first element is a boolean indicating
                                          whether to update the bin string, and subsequent elements
                                          are used to store the new bin string.
        :param portid (str): The item for which the bin string is being determined.
        :param lno (int): The line number in the script where this method is called.
        :param portobj_type (str): Port type ('pPass' or 'pFail'), used to set pass/fail in bin name.
        :return str: The determined bin string for the given item.
        """

        portstring = cls._get_portstring(portid)
        passfail = 'pass' if portobj_type == 'pPass' else 'fail'

        # print ("_get_non_mtt_autosetbinstring called with setbin: ", setbin, " name: ", name, " portid: ", portid)
        # If present in the autobin dict, use the setbinstring from there
        if name in cls.autobindict_internal and portid in cls.autobindict_internal[name]:
            # for setting from hardbin, reuse the autobin dict value IFF the setbin matches
            if setbin < -1:
                newbin = str(setbin * -1)
                # we can have anywhere from 1 to 4 digits here for HB or HBSB, e.g. 8, 68, 800, 6800
                # ensure len_newbin rounds up to 2 or 4 digits
                len_newbin = len(newbin)

                if len_newbin == 1:
                    newbin = newbin.zfill(2)
                elif len_newbin == 3:
                    newbin = newbin.zfill(4)
                len_newbin = len(newbin)

                oldbin = cls.autobindict_internal[name][portid][0:len_newbin]  # we will need 2-4 digits depending on if it's HB or HBSB
                if int(newbin) == int(oldbin):
                    setbin = cls.autobindict_internal[name][portid]
                    setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_{passfail}_{Initialize.get_modulename()}_{name}_{portstring}'
                    return setbinstring
            # for AUTO bins, make sure the hardbin hasn't changed
            else:
                confirm(setbin == -1, f"Expected setbin to be -1 for AUTO bins, but got {setbin} in line# {lno}", "This should not be possible, please show this example to Garrett Cooper")
                newbin = str(cls.bin_range[0][0]).zfill(4)[0:2]  # extract the hardbin from the only bin range
                oldbin = cls.autobindict_internal[name][portid][0:2]
                if int(newbin) == int(oldbin):
                    setbin = cls.autobindict_internal[name][portid]
                    setbinstring = f'{Initialize.tos_softbinstr}b{setbin}_{passfail}_{Initialize.get_modulename()}_{name}_{portstring}'
                    return setbinstring

        # default behavior when setting up a bin for the first time
        dig8_newbin = cls.get_new_bin(setbin, lno + 1)
        cls._update_nonmtt_bin(dig8_newbin, name, portid, portobj_type=portobj_type)
        return cls._get_non_mtt_bin_name(str(dig8_newbin))

    @classmethod
    def get_non_mtt_setbinstring(cls, setbin, name, updatesetbinstring, portid, lno, test_class=None):
        """
        Return the string to be used for non-MTT port
        We want a unique bin for every port

        :return: string: setbin
        """
        setbinstring = None

        # print("calling get_non_mtt_setbinstring for setbin:", setbin, "name:", name, "portid:", portid)
        confirm(len(str(setbin)) in range(7, 9),
                f"Expected positive setbin to be 7 or 8-digit for non-MTT, but got {setbin} in line# {lno}",
                "Please provide a 7 or 8-digit bin for non-MTT tests.")
        setbin = str(setbin).rjust(8, '0')  # Ensure setbin is 8 digits for consistency

        confirm(setbin not in cls.bin_registry,
                f"Duplicate direct setbin={setbin} found in line# {lno} for non-MTT test {name}.",
                "Please ensure each non-MTT test has a unique 7 or 8-digit setbin.")
        cls._update_nonmtt_bin(setbin, name, portid)
        setbinstring = cls._get_non_mtt_bin_name(setbin)

        cls.sbdef_dict[setbinstring] = setbin  # Store the setbinstring and setbin in a dictionary
        return setbinstring

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, test_class=None):
        setbinstring = cls._get_non_mtt_autosetbinstring(setbin=setbin,
                                                         name=tname,
                                                         updatesetbinstring=updatesetbinstring,
                                                         portid=portid,
                                                         lno=id_lno,
                                                         portobj_type=portobj_type)
        bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
        cls.update_autobindict(bin, portid, tname, setbinstring)

        cls.sbdef_dict[setbinstring] = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0]
        return setbinstring

    @classmethod
    def update_autobindict(cls, bin, portid, tname, setbinstring):
        """Update the autobin dict to ensure sticky bins"""
        # Write the bin info to the autobin dict to save as Autobinner
        if tname in cls.autobindict:
            cls.autobindict[tname][portid] = bin
        else:
            cls.autobindict[tname] = {portid: bin}
        # Write the bin info to the autobin_internal dict to use internally.
        # Split is needed for both dicts as the bins were changing from run to run when they were being updated together.
        if tname in cls.autobindict_internal:
            cls.autobindict_internal[tname][portid] = bin
        else:
            cls.autobindict_internal[tname] = {portid: bin}


class TestChipNonMTTBin(JGSClass):
    """Binning strategy for Test Chip products - no bin assignment required.

    Returns empty setbin strings and '0000' placeholder bins. No complex bin categorization needed.
    """
    ignore_list = []
    default_thermal_reset_test_classes = []
    sbdef_prohibited_hardbins = []  # all hardbins are allowed in sbdef file
    sbdef_prohibited_databins = []  # all allowed

    @classmethod
    def update_autosetbinstring(cls, setbin, id_lno, portid, tname, updatesetbinstring, portobj_type, test_class=None):
        return ''

    @classmethod
    def _get_non_mtt_autosetbinstring(cls, setbin, name, updatesetbinstring, portid, lno):
        """
        No Setbins for Test Chips
        """
        return ''

    @classmethod
    def get_new_bin(cls, origbin, lno):
        """
        No bins for Test Chips
        """
        return '0000'


class BaseCounter:
    """
    Base class for Counter strategies
    This class holds one module at a time (one per Initialize)
    """
    mtt_ctr_registry = {}  # {8-digit/4-digit: <name>}. MTT ctr registry can have 8 or 4 digits.
    ctr_registry = {}      # {8-digit: <name>}.
    all_8digit_counter = set()
    ctr_dict = {}
    mtt_ctr_dict = {}
    mtt_ctr_start = 0
    thermal_ctr_start = 0
    reset_ctr_start = 0
    all_mtt_4digit_counter = set()
    autoctrdict = {}
    ctr_headers = set()
    mtt_flowmatrix_values = set()
    bm = None
    edc_pass_port_ctr_range = []
    default_thermal_reset_test_classes = ["VminTC", "MbistVminTC", "ApexTC"]
    ctrdictfrommtpl = {}
    ctr_start_offset = 5555  # integer to offset counters from bins so they don't overlap. must be below 9999, 0-5555 verified working

    @classmethod
    def _extract_port_number(cls, portid):
        """
        Extract the numeric port number from a port identifier.
        Handles both single-digit and multi-digit port numbers.

        :param portid: Port identifier (e.g., 'r0', 'r63', 'rm1', 'rm2', 'r102')
        :return: The numeric port number as a string (e.g., '0', '63', '1', '2', '102')

        Examples:
            'r0' -> '0'
            'r63' -> '63'
            'r102' -> '102'
            'rm1' -> '1'
            'rm2' -> '2'
        """
        if portid.startswith('rm'):
            # For negative ports like 'rm1', 'rm2', extract everything after 'rm'
            return portid[2:]
        elif portid.startswith('r'):
            # For positive ports like 'r0', 'r63', 'r102', extract everything after 'r'
            return portid[1:]
        else:
            # Fallback: return the last character (maintains backward compatibility)
            return portid[-1]

    @classmethod
    def init(cls):
        # We either need the user to specify the Env file in the inputs or run pymtpl from a valid TP dir.
        # This is because we want the env file to help expand the flowmatrix values for mtt counters.
        if IS_UT:    # unittests does not call this function
            return

        cls.bm = BM(Initialize.get_tpobj(), readmodules=False).init()
        if cls.bm.bm_file:
            try:
                for line in cls.bm.expand(f'SetBin "{Initialize.tos_softbinstr}b" + FlowMatrix.bin'):
                    line = line.strip(f'SetBin {Initialize.tos_softbinstr}b')
                    cls.mtt_flowmatrix_values.add(int(line))
            except ErrorInput as e:
                log.info(f'-i- Exception on BaseCounter().init(): {e}')
                pass     # in cases of pymtpl env using expanded

    @classmethod
    def load_autoctrfile(cls):
        # No internal autocounter dict as we want the counters to be permanently sticky.
        # Logic is when doing data pull we always want one counter to point to one test only.
        # If test counter changes, new counter will point to that test as well as old counter.
        autoctrfilename = str(Initialize.get_modulename()) + "_AutoCounter.json"
        filepath = os.path.join(os.path.dirname(Initialize.get_outfile()), 'PymtplInputFiles', autoctrfilename)
        cls.autoctrfilepath = filepath

        autoctrdict = {}
        if Initialize.usebinctrfrommtpl:
            autoctrdict = cls.ctrdictfrommtpl
        elif os.path.exists(filepath):
            with open(filepath, 'r') as f:
                autoctrdict = json.load(f)

        # Load the counters from the auto counter dict into the all_8digit_ctr set so that they are not re-used.
        for value in autoctrdict.values():
            for counter in value.values():
                cls.all_8digit_counter.add(counter)

        cls.autoctrdict = autoctrdict

    @classmethod
    def load_autoctrinfo_from_mtpl(cls):
        """
        Load the bin and counter information from the mtpl instead of autobinner json file
        """
        for flow, fitem in BaseMtplInfo.mtpl_dutflow_map.items():
            for port, portdata in fitem.items():
                if isinstance(portdata, dict):
                    cls._update_autoctr_json(portdata)

    @classmethod
    def _update_autoctr_json(cls, input_fitem_info):
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

                if "IncrementCounters" in portdata:
                    if test_name not in cls.ctrdictfrommtpl:
                        cls.ctrdictfrommtpl[test_name] = {}

                    ctrinfo = cls._get_counter(portdata["IncrementCounters"])
                    if ctrinfo is not None:
                        cls.ctrdictfrommtpl[test_name][portkey] = ctrinfo

    @classmethod
    def _get_counter(cls, counterstring):
        """
        Extract the counter value from a counter string.

        Args:
            counterstring (str): String containing counter information with format 'nXXXXXXXX' or 'pXXXXXXXX'

        Returns:
            str: The extracted 8-digit counter number

        Raises:
            ErrorUser: If the counter string does not match the expected format
        """
        pattern = r"[np](\d{7,8})"
        matches = re.findall(pattern, counterstring)
        if not matches:
            return None
        counter = matches[0]

        return str(counter)

    @classmethod
    def set_edc_pass_port_ctr_range(cls, ctr_range):
        """Set the counter range value for edc and pass ports and check validity"""
        if isinstance(ctr_range, tuple):
            cls.edc_pass_port_ctr_range.append(ctr_range)    # One range
        else:
            cls.edc_pass_port_ctr_range.extend(ctr_range)    # multiple ranges

        # check ctr_range correctness
        for item in cls.edc_pass_port_ctr_range:
            confirm(isinstance(item, (list, tuple)) and len(item) == 2,
                    f'Expecting a tuple or a list of tuples as the edcportctrbinrange for: item "{item}"',
                    'Pls fix edcportctrbinrange so that it is edcportctrbinrange = (start, end) or [(start1, end1), (start2, end2), ...]')

            # Check if the values are 8 digits long
            start, end = item
            confirm(len(str(start)) in [3, 4] and len(str(end)) in [3, 4],
                    f'Expecting start and end values to be 3 or 4 digits long for edcportctrbinrange "{item}"',
                    'Pls fix edcportctrbinrange so that start and end values are 3 (For Bin 8/9) or 4 digits long - Ex - (4400,4401)')

    @classmethod
    def get_unique_edc_ctr(cls):
        """
        This function returns a unique counter for edc and pass ports that is not present in the all_8digit_counter set.
        The range of values to check for the unique counter is specified by the edc_pass_port_ctr_range.
        Everytime this function is called, you get a unique counter that is not in the all_8digit_counter set and that counter is
        added to the all_8digit_counter set so that it is not re-used.
        """
        for ctr_range in cls.edc_pass_port_ctr_range:
            start, end = ctr_range
            start = (start * 10000) + cls.ctr_start_offset
            end = (end * 10000) + 9999
            for counter in range(start, end + 1):
                counter = str(counter)
                # Check if counter is not already in use by counters or bins
                if counter not in cls.all_8digit_counter and (Initialize.nonmttbinstrategy is None or counter not in Initialize.nonmttbinstrategy.all_8digit):
                    cls.all_8digit_counter.add(counter)
                    return counter
        raise ErrorUser("No unique counter available in the specified ranges",
                        "Please update the edcportctrbinrange so that it has a valid range of values")

    @classmethod
    def get_thermal_reset_port_counter_start(cls):
        """
        Function to get the starting counter for default ports
        :return: Starting counter for default ports
        """

        if Initialize.nonmttbinstrategy.bin_range:
            seed = Initialize.nonmttbinstrategy.bin_range[0][0]
        else:
            seed = int(next(iter(Initialize.nonmttbinstrategy.all_4digit)))

        random.seed(seed)
        base_value = random.randint(0, 7000)

        return base_value

    @classmethod
    def get_unique_thermal_counter(cls, bin):
        """
        Function to generate a new unique thermal counter
        :bin : Input bin in the form of HBSB
        :return: Unique 8 digit counter in the form of HBSBXXXX
        """

        cls.thermal_ctr_start = cls.get_thermal_reset_port_counter_start()
        count_val = 0
        while count_val < 9999:
            dig8_thermal_counter = str(bin) + str(cls.thermal_ctr_start).zfill(4)
            count_val = count_val + 1  # Arbitraty count val to make sure the while loop ends.
            # Check if counter is not already in use by counters or bins
            if dig8_thermal_counter not in cls.all_8digit_counter and (Initialize.nonmttbinstrategy is None or dig8_thermal_counter not in Initialize.nonmttbinstrategy.all_8digit):
                cls.all_8digit_counter.add(dig8_thermal_counter)
                return dig8_thermal_counter
            cls.thermal_ctr_start += 1

    @classmethod
    def get_unique_reset_counter(cls, bin):
        """
        Function to generate a new unique number for MTT tests
        :bin : Input bin in the form of HBSB
        :return: Unique 8 digit counter
        """

        cls.reset_ctr_start = cls.get_thermal_reset_port_counter_start()
        count_val = 0
        while count_val < 9999:
            dig8_reset_counter = str(bin) + str(cls.reset_ctr_start).zfill(4)
            count_val = count_val + 1  # Arbitraty count val to make sure the while loop ends.
            # Check if counter is not already in use by counters or bins
            if dig8_reset_counter not in cls.all_8digit_counter and (Initialize.nonmttbinstrategy is None or dig8_reset_counter not in Initialize.nonmttbinstrategy.all_8digit):
                cls.all_8digit_counter.add(dig8_reset_counter)
                return dig8_reset_counter
            cls.reset_ctr_start += 1

    @classmethod
    def clear_nonmtt_ctrs(cls):
        """Initialize class variables for non mtt tests"""
        cls.ctr_registry = {}
        cls.all_8digit_counter.clear()
        cls.ctr_dict = {}
        cls.autoctrdict = {}
        cls.ctr_headers.clear()
        cls.edc_pass_port_ctr_range = []
        cls.thermal_ctr_start = 0
        cls.reset_ctr_start = 0
        cls.ctrdictfrommtpl = {}

    @classmethod
    def clear_mtt_ctrs(cls):
        """Initialize class variables for mtt tests.
        MTT class updates some of the class variables.
        So need to clear them separately due to the split into mtt and non mtt counter classes"""
        # for subclass in cls.__subclasses__():
        #     subclass.mtt_ctr_start = 0

        cls.mtt_ctr_registry = {}
        cls.all_mtt_4digit_counter.clear()
        cls.mtt_ctr_dict = {}
        cls.mtt_ctr_start = 0
        cls.mtt_flowmatrix_values = set()

    @classmethod
    def get_psuedo_random_4dig_counter_start(cls):
        """
        Function to get the starting counter for MTT tests using a PRNG
        Checks if Initialize.module_name ARR/FUN/SCN or others and returns a starting MTT value based on a psuedo random number generator
        :return: Starting counter for MTT tests in form of XXXX
        """
        if BaseBin.bin_range:
            seed = BaseBin.bin_range[0][0]
        else:
            seed = int(next(iter(BaseBin.all_4digit)))
        if "ARR" in Initialize.get_modulename():
            range_start = 0   # start of random number
            range_end = 2000  # Maximum range of random number
        elif "FUN" in Initialize.get_modulename():
            range_start = 3001   # start of random number
            range_end = 5000  # Maximum range of random number
        elif "SCN" in Initialize.get_modulename():
            range_start = 6001   # start of random number
            range_end = 8000  # Maximum range of random number
        else:
            range_start = 9001   # start of random number
            range_end = 9099  # Maximum range of random number

        random.seed(seed)
        base_value = random.randint(range_start, range_end)

        return base_value

    @classmethod
    def _update_mtt_ctr(cls, inputctr, dfi_name, lno, portid, portstartstring, ctrpassfail):
        """
        Updates MTT counter registry.

        :param inputctr: input counter value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :return: None
        """
        port_number = cls._extract_port_number(portid)
        if len(str(inputctr)) <= 4:
            cls.all_mtt_4digit_counter.add(inputctr)  # Add counter to counter set so that it is not re-used.
            digit4 = str(inputctr).zfill(4)
            ctrstring = Initialize.mttbinstrategy.get_var_name() + '_' + digit4

            if ctrstring not in cls.mtt_ctr_registry:

                if '+' in dfi_name:
                    counter_name = f'IncrementCounters "{Initialize.get_modulename()}::{portstartstring}" + FlowMatrix.bin + "{digit4}_{ctrpassfail}_" + {dfi_name} + "_{port_number}"'
                else:
                    counter_name = f'IncrementCounters "{Initialize.get_modulename()}::{portstartstring}" + FlowMatrix.bin + "{digit4}_{ctrpassfail}_{dfi_name}_{port_number}"'
                cls.mtt_ctr_registry[ctrstring] = counter_name

            for flow in cls.mtt_flowmatrix_values:
                counterused = str(flow) + digit4

                if counterused not in cls.mtt_ctr_registry:
                    cls.mtt_ctr_registry[counterused] = counter_name
                else:
                    # this is shared counter
                    raise ErrorUser(f'Counter {digit4} is not unique as it is being used in {cls.mtt_ctr_registry[counterused]}',
                                    f'Please update the counter in line no# {lno}')
        else:
            raise ErrorUser(f'Counter {inputctr} is not a valid counter for MTT tests',
                            f'Input counter needs to be a 4 digit counter for MTT tests as otherwise they will not be unique')

    @classmethod
    def _update_non_mtt_ctr(cls, inputctr, dfi_name, lno, portid, portstartstring, ctrpassfail):
        """
        Updates non-MTT counter registry.

        :param inputctr: input counter value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :return: None
        """
        port_number = cls._extract_port_number(portid)
        digit8 = str(inputctr)
        if digit8 not in cls.ctr_registry:
            counter_name = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{digit8}_{ctrpassfail}_{dfi_name}_{port_number}'
            cls.ctr_registry[digit8] = counter_name
        else:
            # this is shared counter
            raise ErrorUser(f'Counter {digit8} is not unique as it is being used in {cls.ctr_registry[digit8].split("::")[1]}',
                            f'Please update the counter in line no# {lno}')

    @classmethod
    # TODO: Data structure will be "tname : {port: counter_number}"" Similar to bins
    # TODO: Always update the auto-bin and Auto-counter json output files so that users can delete stuff.
    # TODO: Allow users to not get counters for a port
    def get_portctrstring(cls, ctr, name, lno, portobj_type, portid, ismtt=False, manualctr=False):
        """
        Return the string to be used for this port
        We want the same counter across ports (eg. p0, p2, p3)

        :return: string: ctr
        """
        portctrstring = None
        if portobj_type == "pPass":
            portstartstring = "p"
            ctrpassfail = "pass"
        else:
            portstartstring = "n"
            ctrpassfail = "fail"

        if ismtt:
            portctrstring = cls._get_mtt_portctrstring(ctr, name, lno, portstartstring, ctrpassfail, portid)
        else:
            portctrstring = cls._get_non_mtt_portctrstring(ctr, name, lno, portstartstring, ctrpassfail, portid, manualctr=manualctr)

        return portctrstring

    @classmethod
    def _get_mtt_portctrstring(cls, ctr, name, lno, portstartstring, ctrpassfail, portid):
        port_number = cls._extract_port_number(portid)
        if name in cls.autoctrdict and portid in cls.autoctrdict[name]:
            ctr = str(cls.autoctrdict[name][portid]).zfill(4)
            if '+' in name:
                portctrstring = f'IncrementCounters "{Initialize.get_modulename()}::{portstartstring}" + FlowMatrix.bin + "{ctr}_{ctrpassfail}_" + {name} + "_{port_number}"'
            else:
                portctrstring = f'IncrementCounters "{Initialize.get_modulename()}::{portstartstring}" + FlowMatrix.bin + "{ctr}_{ctrpassfail}_{name}_{port_number}"'
        else:
            cls._update_mtt_ctr(ctr, name, lno, portid, portstartstring, ctrpassfail)
            portctrstring = cls.get_ctr_name(str(ctr), ismtt=True)
        return portctrstring

    @classmethod
    def _get_non_mtt_portctrstring(cls, ctr, name, lno, portstartstring, ctrpassfail, portid, manualctr=False):
        port_number = cls._extract_port_number(portid)
        if manualctr:
            portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{port_number}'
        else:
            # The below logic will not work for Sort so will need to define a new function in any class for Sort counters
            if name in cls.autoctrdict and portid in cls.autoctrdict[name]:
                previous_bin = str(cls.autoctrdict[name][portid])[:-4].zfill(4)
                new_bin = str(ctr)[:-4].zfill(4)
                if ctrpassfail == "fail":
                    # IF it is a fail port and If bin did not change, then use counter from bin dict
                    if previous_bin == new_bin:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{port_number}'
                    # If bin changed, we need to update the counter with the newer one
                    else:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{port_number}'
                elif ctrpassfail == "pass":
                    # If it is passing port, since there will be no bin for it, if previous counter exists, use it
                    portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{port_number}'

            else:
                if portid not in cls.ignore_ctr_list:
                    cls._update_non_mtt_ctr(ctr, name, lno, portid, portstartstring, ctrpassfail)
                    portctrstring = cls.get_ctr_name(str(ctr))
                else:
                    portctrstring = ''
        return portctrstring

    @classmethod
    def populate_internal_ctr_trackers(cls, flow_obj):
        """
        Populates internal counter trackers with counter values from the given flow object.
        :param flow_obj (FlowObject): The flow object containing items with port objects to be processed.

        :return None
        """
        for fitem in flow_obj.get_items():
            for _, port_obj in fitem.ret_dict.items():
                if port_obj.ctr and port_obj.ctr > 0:
                    confirm(len(str(port_obj.ctr)) in [7, 8],
                            f"Counter {port_obj.ctr} in {fitem.get_name()} port {_} is in an incorrect format for non MTT tests",
                            "Counter needs to be 7 or 8 digits long in the format of HBSBXXXX")
                    cls._confirm_no_duplicate_counters(_, port_obj, fitem)
                    BaseCounter.all_8digit_counter.add(str(port_obj.ctr))

    @classmethod
    def _confirm_no_duplicate_counters(cls, portid, port_obj, fitem):
        if cls.ctrdictfrommtpl and fitem.get_name() in cls.ctrdictfrommtpl:
            if portid in cls.ctrdictfrommtpl[fitem.get_name()]:
                if str(port_obj.ctr) == str(cls.ctrdictfrommtpl[fitem.get_name()][portid]):
                    return  # Skip uniqueness check if counter matches MTPL

        confirm(str(port_obj.ctr) not in cls.all_8digit_counter,
                f"Counter {port_obj.ctr} in {fitem.get_name()} port {portid} is not unique and is already being used",
                "Please use a different counter to ensure counter uniqueness")

    @classmethod
    def get_ctr_name(cls, ctr, ismtt=False):
        """
        This is called from FItem and MultiTrial write_lines()

        :param ctr: eight digit counter or 4 digit counter
        :return: the counter name
        """
        if ismtt:
            # user passes in the ctr with FlowMatrix added to get the key back
            ctrkey = Initialize.mttbinstrategy.get_var_name() + '_' + str(ctr).zfill(4)
            return cls.mtt_ctr_registry[ctrkey]
        else:
            return cls.ctr_registry[ctr]

    @classmethod
    def convert_4digit_to_8digit(cls, digit4):
        """
        Converts 4 digit to 8 digit
        :param digit4:
        :return:
        """
        raise Exception("Implement this in your subclass")

    @classmethod
    def get_unique_counter(cls, bin):
        """Return the var name used in MultiTrial ctr"""
        raise Exception("Implement this in your subclass")


class CtrNVLClass8dig(BaseCounter):
    ignore_ctr_list = ['rm1', 'rm2']
    autocounterset = set()

    @classmethod
    def get_counter_from_bin(cls, bin):
        if len(f'{bin}') >= 4:
            bin_for_counter = str(bin)[0:]
            counter = cls.get_unique_counter(bin_for_counter)
        return counter

    @classmethod
    def get_unique_counter(cls, bin):
        """
        Function to generate a new unique number
        :bin : Input bin in the form of HBSB
        :return: Unique 8 digit counter
        """
        # Create a unique key for each hard bin soft bin combo
        counter_value = "counter_start_" + str(bin)
        loop_count = 0
        # For each HBSB, we want to start the counter from 0
        if counter_value not in cls.ctr_dict:
            cls.ctr_dict[counter_value] = 0
        while loop_count < 9999:
            new_counter = int(bin) * 10000 + cls.ctr_dict[counter_value]
            new_counter = str(new_counter)
            # Check if counter is not already in use by counters or bins
            if new_counter not in cls.all_8digit_counter and (Initialize.nonmttbinstrategy is None or new_counter not in Initialize.nonmttbinstrategy.all_8digit):
                cls.all_8digit_counter.add(new_counter)
                return new_counter
            cls.ctr_dict[counter_value] += 1
            loop_count += 1

    @classmethod
    def get_ctrstring_update_counterdict(cls, portid, tname, ctr, id_lno, setbinstring, portobj_type, test_class=None, port0_setbin=None, custom_setbinstring=False):
        portctrstring = ''

        if portid not in cls.ignore_ctr_list and ctr != 0:
            if ctr:
                confirm(ctr not in cls.all_8digit_counter,
                        f"The counter {ctr} you are trying to use in the test {tname} for the port {portid} is already being used by autocounter",
                        f"Please try to use another counter that is not being used in order to make sure all the counters are unique")
                portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, manualctr=True)
                counter = ctr
            elif not ctr and setbinstring != '':
                if portid == "r4" and test_class in cls.default_thermal_reset_test_classes:
                    bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][2:6]
                    counter = cls.get_unique_thermal_counter(bin)
                    portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
                elif portid == "r5" and test_class in cls.default_thermal_reset_test_classes:
                    bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][2:6]
                    counter = cls.get_unique_reset_counter(bin)
                    portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
                else:
                    bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][2:6]
                    counter = cls.get_counter_from_bin(bin)
                    portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            elif not ctr and cls.edc_pass_port_ctr_range:
                # This logic of getting counter from autoctr dict is only valid for edc tests where there is no setbinstring
                # If we have a setbinstring, we will use the bin to get the counter always
                # So logic below only applies for edc tests with no binning information
                # This logic below will not cause counter switching from run to run at class since we compare the 4 dig bin value for class
                # Making the change nonetheless to be consistent with the rest of the code

                if tname in cls.autoctrdict and portid in cls.autoctrdict[tname]:
                    counter = cls.autoctrdict[tname][portid]
                else:
                    counter = cls.get_unique_edc_ctr()
                portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            else:
                portctrstring = ''
        else:
            portctrstring = ''

        if portctrstring != '':
            cls.ctr_headers.add(portctrstring.split("::")[1])
            if ctr is None:
                if tname not in cls.autoctrdict:
                    cls.autoctrdict[tname] = {}
                # Extract counter from portctrstring and update the autoctrdict
                counter_for_dict = portctrstring.split("::")[1].split("_")[0]
                cls.autoctrdict[tname][portid] = str(counter_for_dict)[1:]

        return portctrstring


class MTTCtrNVLClass8dig(CtrNVLClass8dig):
    ignore_ctr_list = ['rm1', 'rm2', 'r1']

    @classmethod
    def get_unique_mtt_counter(cls):
        """
        Function to generate a new unique number for MTT tests
        :bin : Input bin in the form of HBSB
        :return: Unique 8 digit counter
        """
        cls.mtt_ctr_start = cls.get_psuedo_random_4dig_counter_start()
        count_val = 0
        while count_val < 9999:
            count_val = count_val + 1  # Arbitraty count val to make sure the while loop ends.
            if cls.mtt_ctr_start not in cls.all_mtt_4digit_counter:
                new_counter = cls.mtt_ctr_start
                cls.all_mtt_4digit_counter.add(new_counter)
                return new_counter
            cls.mtt_ctr_start += 1

    @classmethod
    def get_ctrstring_update_counterdict(cls, portid, tname, ctr, id_lno, setbinstring, portobj_type, test_class=None, port0_setbin=None, custom_setbinstring=False):

        portctrstring = ''
        if portid not in cls.ignore_ctr_list and ctr != 0:
            if ctr and ctr > 0:
                portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, ismtt=True)
            else:
                ctr = cls.get_unique_mtt_counter()
                portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, ismtt=True)
        else:
            portctrstring = ''

        if portctrstring != '' and len(str(ctr)) <= 4:
            expandstring = portctrstring.replace('IncrementCounters', f'SetBin "{Initialize.tos_softbinstr}b"  +')
            for line in cls.bm.expand(expandstring):
                cls.ctr_headers.add(line.split("::")[1])
            if tname not in cls.autoctrdict:
                cls.autoctrdict[tname] = {}
            cls.autoctrdict[tname][portid] = str(ctr)

        return portctrstring


class CtrHBSB(BaseCounter):
    ignore_ctr_list = ['rm1', 'rm2', 'r1']
    autocounterset = set()

    @classmethod
    def get_counter_from_bin(cls, bin):
        if len(f'{bin}') >= 4:
            bin_for_counter = str(bin)[-4:]
            counter = cls.get_unique_counter(bin_for_counter)
        return counter

    @classmethod
    def get_unique_counter(cls, bin):
        """
        Function to generate a new unique number
        :bin : Input bin in the form of HBSB
        :return: Unique 8 digit counter
        """
        # Create a unique key for each hard bin soft bin combo
        counter_value = "counter_start_" + str(bin)

        # For each HBSB, we want to start the counter from 0
        if counter_value not in cls.ctr_dict:
            cls.ctr_dict[counter_value] = 0

        for _ in range(1000000):
            cls.ctr_dict[counter_value] += 1
            new_counter = int(bin) * 10000 + cls.ctr_dict[counter_value]
            # Check if counter is not already in use by counters or bins
            if new_counter not in cls.all_8digit_counter and (Initialize.nonmttbinstrategy is None or str(new_counter) not in Initialize.nonmttbinstrategy.all_8digit):
                cls.all_8digit_counter.add(new_counter)
                return new_counter

    @classmethod
    def get_ctrstring_update_counterdict(cls, portid, tname, ctr, id_lno, setbinstring, portobj_type, test_class=None, port0_setbin=None, custom_setbinstring=False):
        portctrstring = ''
        if portid not in cls.ignore_ctr_list and ctr != 0:
            if ctr:
                confirm(ctr not in cls.all_8digit_counter,
                        f"The counter {ctr} you are trying to use in the test {tname} for the port {portid} is already being used by autocounter",
                        f"Please try to use another counter that is not being used in order to make sure all the counters are unique")
                portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid)
                counter = ctr
            elif not ctr and setbinstring != '':
                if tname in cls.autoctrdict and portid in cls.autoctrdict[tname]:
                    counter = cls.autoctrdict[tname][portid]
                else:
                    bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][-4:]
                    counter = cls.get_counter_from_bin(bin)
                portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            else:
                portctrstring = ''
        else:
            portctrstring = ''

        if portctrstring != '':
            cls.ctr_headers.add(portctrstring.split("::")[1])
            if ctr is None:
                # Use helper function to extract full port number
                port_number = cls._extract_port_number(portid)
                ctrkey = str(tname) + '_' + port_number
                if tname not in cls.autoctrdict:
                    cls.autoctrdict[tname] = {}
                # Extract counter from portctrstring and update the autoctrdict
                counter_for_dict = portctrstring.split("::")[1].split("_")[0]
                cls.autoctrdict[tname][portid] = str(counter_for_dict)[1:]

        return portctrstring


class MTTCtrHBSB(CtrHBSB):

    @classmethod
    def get_unique_mtt_counter(cls):
        """
        Function to generate a new unique number for MTT tests
        :bin : Input bin in the form of HBSB
        :return: Unique 8 digit counter
        """

        count_val = 0
        while count_val < 9999:
            count_val = count_val + 1  # Arbitraty count val to make sure the while loop ends.
            if cls.mtt_ctr_start not in cls.all_mtt_4digit_counter:
                new_counter = cls.mtt_ctr_start
                cls.all_mtt_4digit_counter.add(new_counter)
                return new_counter
            cls.mtt_ctr_start += 1

    @classmethod
    def get_ctrstring_update_counterdict(cls, portid, tname, ctr, id_lno, setbinstring, portobj_type, test_class=None, port0_setbin=None, custom_setbinstring=False):

        portctrstring = ''
        if portid not in cls.ignore_ctr_list and ctr != 0:
            if ctr and ctr > 0:
                portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, ismtt=True)
            elif not ctr and setbinstring != '':
                ctr = cls.get_unique_mtt_counter()
                portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, ismtt=True)
            else:
                portctrstring = ''
        else:
            portctrstring = ''

        if portctrstring != '' and len(str(ctr)) <= 4:
            expandstring = portctrstring.replace('IncrementCounters', f'SetBin "{Initialize.tos_softbinstr}b"  +')
            for line in cls.bm.expand(expandstring):
                cls.ctr_headers.add(line.split("::")[1])
            if tname not in cls.autoctrdict:
                cls.autoctrdict[tname] = {}
            cls.autoctrdict[tname][portid] = str(ctr)

        return portctrstring


class CtrSort8dig(BaseCounter):
    ignore_ctr_list = ['rm1', 'rm2']
    autocounterset = set()

    @classmethod
    def _get_non_mtt_portctrstring(cls, ctr, name, lno, portstartstring, ctrpassfail, portid, manualctr=False):
        port_number = cls._extract_port_number(portid)
        if manualctr:
            portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{port_number}'
        else:
            if name in cls.autoctrdict and portid in cls.autoctrdict[name]:
                # At sort the bin is the entire 8 dig so we do not check the 4-dig only like in the basecounter class.
                previous_bin = str(cls.autoctrdict[name][portid])
                new_bin = str(ctr)
                if ctrpassfail == "fail":
                    # If bin did not change, then use counter from bin dict
                    if previous_bin == new_bin:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{port_number}'
                    # If bin changed, we need to update the counter with the newer one
                    else:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{port_number}'
                elif ctrpassfail == "pass":
                    portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{port_number}'
            else:
                if portid not in cls.ignore_ctr_list:
                    cls._update_non_mtt_ctr(ctr, name, lno, portid, portstartstring, ctrpassfail)
                    portctrstring = cls.get_ctr_name(str(ctr))
                else:
                    portctrstring = ''
        return portctrstring

    @classmethod
    def get_ctrstring_update_counterdict(cls, portid, tname, ctr, id_lno, setbinstring, portobj_type, ismtt=False, test_class=None, port0_setbin=None, custom_setbinstring=False):

        portctrstring = ''

        if portid not in cls.ignore_ctr_list and ctr != 0:
            # Use case when user is defining a counter
            if ctr:
                # Check if user defined counter is being used by Auto Counter already.
                confirm(ctr not in cls.all_8digit_counter,
                        f"The counter {ctr} you are trying to use in the test {tname} for the port {portid} is already being used by autocounter",
                        f"Please try to use another counter that is not being used in order to make sure all the counters are unique")
                portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, manualctr=True)
                counter = ctr
            # Use case when user wants help of auto-counter - i.e. we have a bin but no counter defined and ctr != None
            elif not ctr and setbinstring != '':
                bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][0:8]
                counter = bin
                portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            elif not ctr and cls.edc_pass_port_ctr_range:
                # This logic of getting counter from autoctr dict is only valid for edc tests where there is no setbinstring
                # If we have a setbinstring, we will use the bin to get the counter always
                # So logic below only applies for edc tests with no binning information
                if tname in cls.autoctrdict and portid in cls.autoctrdict[tname]:
                    counter = cls.autoctrdict[tname][portid]
                else:
                    counter = cls.get_unique_edc_ctr()
                portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)

            else:
                portctrstring = ''
        else:
            portctrstring = ''

        if portctrstring != '':
            cls.ctr_headers.add(portctrstring.split("::")[1])
            if ctr is None:
                # Update autocounter dict to ensure sticky counters
                if tname not in cls.autoctrdict:
                    cls.autoctrdict[tname] = {}
                # We always update the counter in the auto-counter dict.
                # Extract counter from portctrstring and update the autoctrdict
                counter_for_dict = portctrstring.split("::")[1].split("_")[0]
                cls.autoctrdict[tname][portid] = str(counter_for_dict)[1:]

        return portctrstring


class CtrJGS8dig(CtrSort8dig):
    ignore_ctr_list = []  # we want counters on alarm ports
    ctr_start_offset = 0  # pass counters should fill all available space
    skip_pass_counters = False  # If True, will not generate pass counters for pass ports

    @classmethod
    def _get_portstring(cls, portid):
        """
        Returns the port string for a given portid.
        :param portid: The port id (e.g., rm1, rm2, r4, r5, r0, r63, r102, etc.)
        :return: portstring (e.g., n1, n2, 4, 5, 63, 102, etc.)
        """
        port_number = cls._extract_port_number(portid)
        if "rm" in portid:
            return "n" + port_number  # n - negative port
        else:
            return port_number

    @classmethod
    def _get_non_mtt_portctrstring(cls, ctr, name, lno, portstartstring, ctrpassfail, portid, manualctr=False):
        portstring = cls._get_portstring(portid)
        if manualctr:
            portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{str(ctr).zfill(8)}_{ctrpassfail}_{name}_{portstring}'
        else:
            if name in cls.autoctrdict and portid in cls.autoctrdict[name]:
                # At sort the bin is the entire 8 dig so we do not check the 4-dig only like in the basecounter class.
                previous_bin = str(cls.autoctrdict[name][portid])
                new_bin = str(ctr)
                if ctrpassfail == "fail":
                    # If bin did not change, then use counter from bin dict
                    if previous_bin == new_bin:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{portstring}'
                    # If bin changed, we need to update the counter with the newer one
                    else:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{portstring}'
                else:  # pass counter
                    portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{portstring}'
            else:
                cls._update_non_mtt_ctr(ctr, name, lno, portid, portstartstring, ctrpassfail)
                portctrstring = cls.get_ctr_name(str(ctr))
        return portctrstring

    @classmethod
    def _update_non_mtt_ctr(cls, inputctr, dfi_name, lno, portid, portstartstring, ctrpassfail):
        """
        Updates non-MTT counter registry using the correct port string for negative ports.

        :param inputctr: input counter value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :return: None
        """
        portstring = cls._get_portstring(portid)
        digit8 = str(inputctr)
        if digit8 not in cls.ctr_registry:
            counter_name = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{digit8}_{ctrpassfail}_{dfi_name}_{portstring}'
            cls.ctr_registry[digit8] = counter_name
        else:
            # this is shared counter
            raise ErrorUser(f'Counter {digit8} is not unique as it is being used in {cls.ctr_registry[digit8].split("::")[1]}',
                            f'Please update the counter in line no# {lno}')

    @classmethod
    def get_ctrstring_update_counterdict(cls, portid, tname, ctr, id_lno, setbinstring, portobj_type, ismtt=False, test_class=None, port0_setbin=None, custom_setbinstring=False):
        portctrstring = ''
        if ctr != 0:
            # Use case when user is defining a counter
            if ctr:
                # Check if user defined counter is being used by Auto Counter already.
                confirm(ctr not in cls.all_8digit_counter,
                        f"The counter {ctr} you are trying to use in the test {tname} for the port {portid} is already being used by autocounter",
                        f"Please try to use another counter that is not being used in order to make sure all the counters are unique")
                counter = ctr
                # If we are using defaultrm1bin or defaultrm2bin, we want the counter name to equal the bin name
                if (cls._counter_should_match_bin(portid, setbinstring)):
                    portctrstring = cls._get_counter_from_defaultrm12bin(setbinstring)
                else:  # normal counter
                    portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, manualctr=True)
            # Use case when user wants help of auto-counter - i.e. we have a bin but no counter defined. Skip pass ports if skip_pass_counters
            elif not ctr and setbinstring != '' and (not cls.skip_pass_counters or portobj_type == 'pFail'):
                bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][0:8]
                counter = bin
                # right here, we can't check that counter is not in all_8digit_counter because it might be, from the autobindict
                cls.all_8digit_counter.add(counter)
                # If the user specified a setbinstring that is a shared bin, derive the counter string from the bin string
                if custom_setbinstring and '_SHARED_BIN' in setbinstring:
                    portctrstring = cls._get_counter_from_defaultrm12bin(setbinstring)
                else:
                    # we don't need to check for matching counter to bin because a counter is always defined already in that case
                    portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            elif not ctr and cls.edc_pass_port_ctr_range and (not cls.skip_pass_counters or portobj_type == 'pFail'):
                # This logic of getting counter from autoctr dict is only valid for edc tests where there is no setbinstring
                # If we have a setbinstring, we will use the bin to get the counter always
                # So logic below only applies for edc tests with no binning information
                # skips pass ports if skip_pass_counters
                if tname in cls.autoctrdict and portid in cls.autoctrdict[tname]:
                    counter = cls.autoctrdict[tname][portid]
                else:
                    counter = cls.get_unique_edc_ctr(port0_setbin, id_lno)
                portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            else:
                portctrstring = ''
        else:
            portctrstring = ''

        if portctrstring != '':
            cls.ctr_headers.add(portctrstring.split("::")[1])
            if ctr is None:
                # Update autocounter dict to ensure sticky counters
                if tname not in cls.autoctrdict:
                    cls.autoctrdict[tname] = {}
                # We always update the counter in the auto-counter dict.
                # Extract counter from portctrstring and update the autoctrdict
                counter_for_dict = portctrstring.split("::")[1].split("_")[0]
                cls.autoctrdict[tname][portid] = str(counter_for_dict)[1:]

        return portctrstring

    @classmethod
    def _counter_should_match_bin(cls, portid, setbinstring):
        """
        Checks if the counter should match the bin string for the given port id.
        :param portid: The port id (rm1 or rm2)
        :param setbinstring: The bin string to be used
        :return: True if the counter should match the bin, False otherwise
        """
        # we can't match the binstring if it doesn't exist
        if (not setbinstring or setbinstring == ''):
            return False
        # if we're using some sort of default for rm1 or rm2, copy it to the counter
        return ((portid == 'rm1' and Initialize.defaultrm1bin is not None)
                or (portid == 'rm2' and Initialize.defaultrm2bin is not None))

    @classmethod
    def _get_counter_from_defaultrm12bin(cls, setbinstring):
        """
        Returns the counter from defaultrm1bin or defaultrm2bin if applicable.
        :param portid: The port id (rm1 or rm2)
        :param setbinstring: The bin string to be used
        :return: The counter string
        """
        # it's the same except b is replaced with n. always a fail port
        # bin -> counter and BIN -> COUNTER
        return f"IncrementCounters {Initialize.get_modulename()}::{setbinstring.replace('b', 'n', 1).replace('BIN', 'COUNTER', 1).replace('bin', 'counter', 1)}"

    @classmethod
    def _confirm_no_duplicate_counters(cls, portid, port_obj, fitem):
        allow_duplicate = False
        if (portid == 'rm1' and Initialize.defaultrm1bin is not None) or (portid == 'rm2' and Initialize.defaultrm2bin is not None):
            allow_duplicate = True
        if not allow_duplicate and cls.ctrdictfrommtpl and fitem.get_name() in cls.ctrdictfrommtpl:
            if portid in cls.ctrdictfrommtpl[fitem.get_name()]:
                if str(port_obj.ctr) == str(cls.ctrdictfrommtpl[fitem.get_name()][portid]):
                    allow_duplicate = True
        confirm(allow_duplicate or str(port_obj.ctr) not in cls.all_8digit_counter,
                f"Counter {port_obj.ctr} in {fitem.get_name()} port {portid} is not unique and is already being used",
                "Please use a different counter to ensure counter uniqueness")

    @classmethod
    def set_edc_pass_port_ctr_range(cls, ctr_range):
        """Set the counter range value for edc and pass ports and check validity.
        Supports 3, 4, 5, 6, 7, or 8 digit range values to match JGSClass binrange support.

        :param ctr_range: A tuple (start, end) or list of tuples for the counter range
        :type ctr_range: tuple or list
        :raises ErrorUser: When range values are not 3-8 digits long
        """
        if isinstance(ctr_range, tuple):
            cls.edc_pass_port_ctr_range.append(ctr_range)    # One range
        else:
            cls.edc_pass_port_ctr_range.extend(ctr_range)    # Multiple ranges

        # check ctr_range correctness
        for item in cls.edc_pass_port_ctr_range:
            confirm(isinstance(item, (list, tuple)) and len(item) == 2,
                    f'Expecting a tuple or a list of tuples as the edcportctrbinrange for: item "{item}"',
                    'Pls fix edcportctrbinrange so that it is edcportctrbinrange = (start, end) or [(start1, end1), (start2, end2), ...]')

            start, end = item
            confirm(len(str(start)) in (3, 4, 5, 6, 7, 8) and len(str(end)) in (3, 4, 5, 6, 7, 8),
                    f'Expecting start and end values to be 3-8 digits long for edcportctrbinrange "{item}"',
                    'Pls fix edcportctrbinrange so that start and end values are 3-8 digits long - Ex - (4400,4401) for 4-digit, (992900,992999) for 6-digit')

    @classmethod
    def get_unique_edc_ctr(cls, port0_setbin=None, id_lno=None):
        """
        Returns a unique counter for edc and pass ports not present in the all_8digit_counter set.

        Supports 3-8 digit range values.  3 and 5-digit ranges are for hard bins where HB < 10.
        Digit grouping (mirrors JGSClass.get_available_8dig_bin):

        - 3 and 4-digit (HBSB): pad to 4 digits, append 4-digit suffix -> 0HSBxxxx or HBSBxxxx
        - 5 and 6-digit (HBSByy): pad to 6 digits, append 2-digit suffix -> 0HSByyxx or HBSByyxx
        - 7 and 8-digit: pad to 8 digits, no suffix -> 1 possibility per target

        Every call returns a counter not already in all_8digit_counter, and adds it to prevent reuse.
        """
        # if we can, get a counter for this based on the port0 setbin
        if port0_setbin is not None:
            counter = Initialize.nonmttbinstrategy.get_new_bin(port0_setbin, id_lno)
            cls.all_8digit_counter.add(counter)
            return counter

        for ctr_range in cls.edc_pass_port_ctr_range:
            start, end = ctr_range
            range_start_len = len(str(start))

            # Mirror the same grouping logic used in JGSClass.get_available_8dig_bin:
            # - 3 and 4 digit: treat as HBSB, pad to 4, add 4 suffix digits (10000 possibilities each)
            #   3-digit HSB (HB is one digit) -> 0HSBxxxx  (leading zero from zfill)
            #   4-digit HBSB                  -> HBSBxxxx
            # - 5 and 6 digit: treat as HBSByy, pad to 6, add 2 suffix digits (100 possibilities each)
            #   5-digit HSByy (HB is one digit) -> 0HSByyxx  (leading zero from zfill)
            #   6-digit HBSByy                  -> HBSByyxx
            # - 7 and 8 digit: already fully specified, pad to 8, no suffix (1 possibility each)
            if range_start_len <= 4:
                pad_len = 4
                suffix_len = 4
            elif range_start_len <= 6:
                pad_len = 6
                suffix_len = 2
            else:
                pad_len = 8
                suffix_len = 0

            suffix_count = 10 ** suffix_len if suffix_len > 0 else 1

            for target in range(start, end + 1):
                # zfill pads with leading zeros, so a 3-digit 900 becomes "0900" with pad_len=4
                prefix = str(target).zfill(pad_len)
                for i in range(suffix_count):
                    counter = prefix + str(i).zfill(suffix_len) if suffix_len > 0 else prefix
                    if counter not in cls.all_8digit_counter and counter not in Initialize.nonmttbinstrategy.all_8digit:
                        cls.all_8digit_counter.add(counter)
                        return counter
        raise ErrorUser("No unique counter available in the specified ranges",
                        "Please update the edcportctrbinrange so that it has a valid range of values")


class CtrServerClass8dig(BaseCounter):
    ignore_ctr_list = []
    autocounterset = set()
    skip_pass_counters = False  # If True, will not generate pass counters for pass ports

    @classmethod
    def _get_portstring(cls, portid):
        """
        Returns the port string for a given portid.
        :param portid: The port id (e.g., rm1, rm2, r4, r5, r0, r63, r102, etc.)
        :return: portstring (e.g., n1, n2, 4, 5, 63, 102, etc.)
        """
        if "rm" in portid:
            return "n" + cls._extract_port_number(portid)  # n - negative port
        else:
            return cls._extract_port_number(portid)

    @classmethod
    def _get_non_mtt_portctrstring(cls, ctr, name, lno, portstartstring, ctrpassfail, portid, manualctr=False):
        portstring = cls._get_portstring(portid)

        if manualctr:
            portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{portstring}'
        else:
            if name in cls.autoctrdict and portid in cls.autoctrdict[name]:
                # At sort the bin is the entire 8 dig so we do not check the 4-dig only like in the basecounter class.
                previous_bin = str(cls.autoctrdict[name][portid])
                new_bin = str(ctr)
                if ctrpassfail == "fail":
                    # If bin did not change, then use counter from bin dict
                    if previous_bin == new_bin:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{portstring}'
                    # If bin changed, we need to update the counter with the newer one
                    else:
                        portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{portstring}'
                elif ctrpassfail == "pass":
                    portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{cls.autoctrdict[name][portid]}_{ctrpassfail}_{name}_{portstring}'
            else:
                cls._update_non_mtt_ctr(ctr, name, lno, portid, portstartstring, ctrpassfail)
                portctrstring = cls.get_ctr_name(str(ctr))
        return portctrstring

    @classmethod
    def get_ctrstring_update_counterdict(cls, portid, tname, ctr, id_lno, setbinstring, portobj_type, ismtt=False, test_class=None, port0_setbin=None, custom_setbinstring=False):
        portctrstring = ''
        if ctr != 0:
            # Use case when user is defining a counter
            if ctr:
                # Check if user defined counter is being used by Auto Counter already.
                confirm(ctr not in cls.all_8digit_counter,
                        f"The counter {ctr} you are trying to use in the test {tname} for the port {portid} is already being used by autocounter",
                        f"Please try to use another counter that is not being used in order to make sure all the counters are unique")
                counter = ctr
                # If we are using defaultrm1bin or defaultrm2bin, we want the counter name to equal the bin name
                if (cls._counter_should_match_bin(portid, setbinstring)):
                    portctrstring = cls._get_counter_from_defaultrm12bin(setbinstring)
                else:  # normal counter
                    portctrstring = cls.get_portctrstring(ctr, tname, id_lno, portobj_type, portid=portid, manualctr=True)
            # Use case when user wants help of auto-counter - i.e. we have a bin but no counter defined. Skip pass ports if skip_pass_counters
            elif not ctr and setbinstring != '' and (not cls.skip_pass_counters or portobj_type == 'pFail'):
                bin = setbinstring.split(f'{Initialize.tos_softbinstr}b')[1].split('_')[0][0:8]
                counter = bin
                # right here, we can't check that counter is not in all_8digit_counter because it might be, from the autobindict
                cls.all_8digit_counter.add(counter)
                # If the user specified a setbinstring that is a shared bin, derive the counter string from the bin string
                if custom_setbinstring and '_SHARED_BIN' in setbinstring:
                    portctrstring = cls._get_counter_from_defaultrm12bin(setbinstring)
                else:
                    # we don't need to check for matching counter to bin because a counter is always defined already in that case
                    portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            elif not ctr and cls.edc_pass_port_ctr_range and (not cls.skip_pass_counters or portobj_type == 'pFail'):
                # This logic of getting counter from autoctr dict is only valid for edc tests where there is no setbinstring
                # If we have a setbinstring, we will use the bin to get the counter always
                # So logic below only applies for edc tests with no binning information
                # skips pass ports if skip_pass_counters
                if tname in cls.autoctrdict and portid in cls.autoctrdict[tname]:
                    counter = cls.autoctrdict[tname][portid]
                else:
                    counter = cls.get_unique_edc_ctr(portobj_type=portobj_type)
                portctrstring = cls.get_portctrstring(counter, tname, id_lno, portobj_type, portid=portid)
            else:
                portctrstring = ''
        else:
            portctrstring = ''

        if portctrstring != '':
            cls.ctr_headers.add(portctrstring.split("::")[1])
            if ctr is None:
                # Update autocounter dict to ensure sticky counters
                if tname not in cls.autoctrdict:
                    cls.autoctrdict[tname] = {}
                # We always update the counter in the auto-counter dict.
                # Extract counter from portctrstring and update the autoctrdict
                counter_for_dict = portctrstring.split("::")[1].split("_")[0]
                cls.autoctrdict[tname][portid] = str(counter_for_dict)[1:]

        return portctrstring

    @classmethod
    def _counter_should_match_bin(cls, portid, setbinstring):
        """
        Checks if the counter should match the bin string for the given port id.
        :param portid: The port id (rm1 or rm2)
        :param setbinstring: The bin string to be used
        :return: True if the counter should match the bin, False otherwise
        """
        # we can't match the binstring if it doesn't exist
        if (not setbinstring or setbinstring == ''):
            return False
        # if we're using some sort of default for rm1 or rm2, copy it to the counter
        return ((portid == 'rm1' and Initialize.defaultrm1bin is not None)
                or (portid == 'rm2' and Initialize.defaultrm2bin is not None))

    @classmethod
    def _get_counter_from_defaultrm12bin(cls, setbinstring):
        """
        Returns the counter from defaultrm1bin or defaultrm2bin if applicable.
        :param portid: The port id (rm1 or rm2)
        :param setbinstring: The bin string to be used
        :return: The counter string
        """
        # it's the same except b is replaced with n. always a fail port
        # bin -> counter and BIN -> COUNTER
        return f"IncrementCounters {Initialize.get_modulename()}::{setbinstring.replace('b', 'n', 1).replace('BIN', 'COUNTER', 1).replace('bin', 'counter', 1)}"

    @classmethod
    def _update_non_mtt_ctr(cls, inputctr, dfi_name, lno, portid, portstartstring, ctrpassfail):
        """
        Updates non-MTT counter registry.

        :param inputctr: input counter value
        :param dfi_name: This is MultiTrial Name or DUTFlowItem name
        :return: None
        """
        portstring = cls._get_portstring(portid)

        digit8 = str(inputctr)
        if digit8 not in cls.ctr_registry:
            counter_name = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{digit8}_{ctrpassfail}_{dfi_name}_{portstring}'
            cls.ctr_registry[digit8] = counter_name
        else:
            # this is shared counter
            raise ErrorUser(f'Counter {digit8} is not unique as it is being used in {cls.ctr_registry[digit8].split("::")[1]}',
                            f'Please update the counter in line no# {lno}')

    @classmethod
    def get_unique_edc_ctr(cls, portobj_type):
        """
        This function returns a unique counter for edc and pass ports that is not present in the all_8digit_counter set.
        The range of values to check for the unique counter is specified by the edc_pass_port_ctr_range.
        Everytime this function is called, you get a unique counter that is not in the all_8digit_counter set and that counter is
        added to the all_8digit_counter set so that it is not re-used.
        """
        base = 90000000  # Base value for the counter
        if portobj_type == "pPass":
            base = 99000000  # Base value for the pass port counter

        for ctr_range in cls.edc_pass_port_ctr_range:
            start, end = ctr_range
            start = base + (start * 100) + 00
            end = base + (end * 100) + 99
            for counter in range(start, end + 1):
                counter = str(counter)
                if counter not in cls.all_8digit_counter and counter not in Initialize.nonmttbinstrategy.all_8digit:
                    cls.all_8digit_counter.add(counter)
                    return counter
        raise ErrorUser("No unique counter available in the specified ranges",
                        "Please update the edcportctrbinrange so that it has a valid range of values")

    @classmethod
    def _confirm_no_duplicate_counters(cls, portid, port_obj, fitem):
        allow_duplicate = False
        if (portid == 'rm1' and Initialize.defaultrm1bin is not None) or (portid == 'rm2' and Initialize.defaultrm2bin is not None):
            allow_duplicate = True
        if not allow_duplicate and cls.ctrdictfrommtpl and fitem.get_name() in cls.ctrdictfrommtpl:
            if portid in cls.ctrdictfrommtpl[fitem.get_name()]:
                if str(port_obj.ctr) == str(cls.ctrdictfrommtpl[fitem.get_name()][portid]):
                    allow_duplicate = True
        confirm(allow_duplicate or str(port_obj.ctr) not in cls.all_8digit_counter,
                f"Counter {port_obj.ctr} in {fitem.get_name()} port {portid} is not unique and is already being used",
                "Please use a different counter to ensure counter uniqueness")


class CtrDMRClass8dig(CtrServerClass8dig):
    """Counter strategy for DMR Class
    Deltas from CtrServerClass8dig:
        - No pass counters automatically added
        - If using defaultrm1bin or defaultrm2bin, counter name should equal bin name (b->n)
    """
    skip_pass_counters = True  # No pass counters automatically added


class CtrTestChip(CtrJGS8dig):
    """Counter strategy for Test Chip products - simplified counter format.

    Uses simple counter naming: manual counters use ``{ctr}_{pass|fail}_{TESTNAME}_{PORTNUM}``,
    auto counters use ``{pass|fail}_{TESTNAME}_{PORTNUM}``. Port identifiers: rm1→n1, rm2→n2, r0→0, r1→1.
    Returns '00000000' for bin requests.
    """

    @classmethod
    def _get_portstring(cls, portid):
        """
        Returns the port string for a given portid.
        :param portid: The port id (e.g., rm1, rm2, r4, r5, r0, r63, r102, etc.)
        :return: portstring (e.g., n1, n2, 4, 5, 63, 102, etc.)
        """
        if "rm" in portid:
            return "n" + cls._extract_port_number(portid)  # n - negative port
        else:
            return cls._extract_port_number(portid)

    @classmethod
    def _get_non_mtt_portctrstring(cls, ctr, name, lno, portstartstring, ctrpassfail, portid, manualctr=False):
        port_number = cls._get_portstring(portid)
        if manualctr:
            portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{portstartstring}{ctr}_{ctrpassfail}_{name}_{port_number}'
        else:
            # If it is passing port, since there will be no bin for it, if previous counter exists, use it
            portctrstring = f'IncrementCounters {Initialize.get_modulename()}::{ctrpassfail}_{name}_{port_number}'
        return portctrstring

    @classmethod
    def get_new_bin(cls, origbin, lno):
        """
        Return a new bin, given the range
        :param origbin: either 0 or -44
        :return: New 8 digit
        """
        return '00000000'  # TC does not need binning


class BaseNumber:
    """
    Base class for Basenumber strategies
    This class holds one module at a time (one per Initialize)
    """
    all_base_numbers = set()
    basenumrange = []

    @classmethod
    def init(cls, basenumrange):

        if isinstance(basenumrange, tuple):
            cls.basenumrange.append(basenumrange)    # One range
        else:
            cls.basenumrange.extend(basenumrange)    # multiple ranges

        for item in cls.basenumrange:
            confirm(isinstance(item, (list, tuple)) and len(item) == 2,
                    f'Expecting exactly two elements for basenumrange: item "{item}"',
                    'Pls fix basenumrange - Use basenumrange = (X,Y) or ([A,B], [C,D])')

    @classmethod
    def load_autobasenumfile(cls):
        autobasenumdict = {}
        autobasenumfilename = str(Initialize.get_modulename()) + "_AutoBasenumber.json"
        filepath = os.path.join(os.path.dirname(Initialize.get_outfile()), 'PymtplInputFiles', autobasenumfilename)
        cls.autobasenumfilepath = filepath
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                autobasenumdict = json.load(f)
            # Load the base nums from the auto basenumber dict into the all_base_numbers set so that they are not re-used.
            for k, v in autobasenumdict.items():
                BaseNumber.all_base_numbers.add(int(v))

        else:
            autobasenumdict = {}
        cls.autobasenumdict = autobasenumdict

    @classmethod
    def clear_base_numbers(cls):
        """Initialize class variables"""
        cls.all_base_numbers.clear()
        cls.basenumrange.clear()

    @classmethod
    def update_basenumbers(cls, fitem):
        """Update all_base_numbers set with existing basenumbers in mtpl so that they are not used"""

        if isinstance(fitem.ti, MultiTrial):
            for param in fitem.ti.template.params:
                if "basenumber" in param.lower() and not is_none(fitem.ti.template.params[param]):
                    BaseNumber.all_base_numbers.add(int(fitem.ti.template.params[param]))
        elif not isinstance(fitem.ti, Flow):
            for param in fitem.ti.params:
                if "basenumber" in param.lower() and not is_none(fitem.ti.params[param]):
                    BaseNumber.all_base_numbers.add(int(fitem.ti.params[param]))

    @classmethod
    def get_new_base_num(cls, origbase, lno):
        """
        Return a new base number that is unique and not in use in the mtpl
        :return: New Basenumber as string
        """

        # Same checks as in the binning strategy.
        if origbase < 0:
            confirm(len(cls.basenumrange) > 0, 'No basenumrange specified', 'Pls specify basenumrange in Initialize()')

        if origbase == -1:
            confirm(len(cls.basenumrange) == 1,
                    f'Cannot use BaseNumbers=AUTO in line# {lno} or anywhere in the input file if there are multiple basenumrange: {cls.basenumrange}',
                    'Pls specify specific basenumrange: BaseNumbers=-<ABC> in order to use Auto Basenumber feature when using multiple basenum ranges')
        # iterate all Flow objects and get all basenumbers
        for flow_obj in Flow.get_registry():
            for fitem in flow_obj.get_items():
                cls.update_basenumbers(fitem)

        origbase = str(origbase)  # Convert to string to split and compare the basenumber
        # If negative bin
        usableBasenumranges = []
        for i in range(len(cls.basenumrange)):
            if (origbase[1:4]) == str(cls.basenumrange[i][0])[0:3]:
                usableBasenumranges.append(i)
            elif origbase == "-1":
                usableBasenumranges.append(0)

        for basenumrange in usableBasenumranges:
            basenumrange = cls.basenumrange[basenumrange]
            for target in range(basenumrange[0], basenumrange[1] + 1):
                if target not in BaseNumber.all_base_numbers:
                    BaseNumber.all_base_numbers.add(target)
                    return target

        # Future what is the right automation if everything is exhausted?
        raise ErrorUser(f"All basenumber range is exhausted {cls.basenumrange} for line# {lno}",
                        f"Pls specify basenumber manually in line# {lno}")

    @classmethod
    def get_auto_basenumber(cls, origbase, tname, lno):
        """
        Return the basenumber for a test instance
        :return: New Basenumber as string
        """
        # If tname already exists in the basenumber dict, we use that
        if tname in BaseNumber.autobasenumdict:
            basenumber = BaseNumber.autobasenumdict[tname]
        # If not, we generate a new basenumber and return that
        else:
            basenumber = cls.get_new_base_num(origbase, lno)

        return str(basenumber)

    @classmethod
    def update_autobasedict(cls, basenum, tname):
        """Update the autobasenum dict to ensure sticky base numbers"""

        # Write the base number info to the autobasenumdict dict to save as autobasenumdict
        BaseNumber.autobasenumdict[tname] = basenum
