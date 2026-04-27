#!/usr/bin/python
#------------------------------------------------------------------------------
# Name:        OTPL Parser
# Purpose:     Helper script for Torch Extinguisher to parse OTPL
#
# Author:      milespac
#
# Created:     06/2022
# Copyright:   (c) Miles Pacheco 2022
#
# Required Packages: n/a
#------------------------------------------------------------------------------

#Standard Packages
import sys,os,re,datetime
import utilities as utilities

#credit to this method: https://www.vipinajayakumar.com/parsing-text-with-python

rx_dict = {
    'timestamp': re.compile(r'^\s*(# Module Revision.*)'),
    'version': re.compile(r'^\s*Version\s+(\d+\.\d+;)'),
    'programstyle': re.compile(r'^\s*ProgramStyle\s*=\s*Modular.*'),
    'testplan': re.compile(r'^\s*TestPlan\s+(\w+;)'),
    'import': re.compile(r'^\s*Import\s+(\w+\.\w+;)'),
    'counters': re.compile(r'^\s*(\w)(\d{2})(\d{2})(\d{4}.*,?)'),
    'test': re.compile(r'^\s*((?:CSharp)*Test)\s+(\w+)\s+(\w+.*)'),
    'parameters': re.compile(r'^\s+(\w+)\s+=\s+(.*;)'),
    'flow': re.compile(r'^\s*((?:DUT)*Flow)\s+(.*)'),
    'flowitem': re.compile(r'^\s*((?:DUT)*FlowItem)\s+(\w+)\s+(\w+.*)'),
    'compressedresult': re.compile(r'^\s*Result\s+([-\d]+)\s*{\s*Property\s+PassFail\s+=\s+(.*;)\s*(Return|GoTo)\s+(.*;)\s*}\s*'),
    'result': re.compile(r'^\s*Result\s+(.*)'),
    'property': re.compile(r'^\s*Property\s+PassFail\s+=\s+(.*;)'),
    'setbin': re.compile(r'^\s*SetBin\s+(.*)(\d{2})(\d{2})(\d{4})(.*;)'),
    'flowcounter': re.compile(r'^\s*IncrementCounters\s+(.*)(\d{2})(\d{2})(\d{4}.*;)'),
    'goto': re.compile(r'^\s*GoTo\s+(.*;)'),
    'return': re.compile(r'^\s*Return\s+(.*;)'),
    'gitlog': re.compile(r'^\s*[0-9a-fA-F]{40}\s*([0-9a-fA-F]{40})\s*(.*)\s*\s<.*>\s*(\d{10}).*'),
    'fsm': re.compile(r'^\s+(\#\s+FSM.+)'),
}

# as far as I can tell this list is standardized, which is why it's hard-coded.
dDescriptors = {
    "b7":  "b7_FAIL_SLOW_FMAX_OR_IDV_OR_STHI_BENT_LEAD",
    "b07": "b7_FAIL_SLOW_FMAX_OR_IDV_OR_STHI_BENT_LEAD",
    "b8":  "b8_FAIL_VCCCONTINUITY",
    "b08": "b8_FAIL_VCCCONTINUITY",
    "b9":  "b9_FAIL_PIN_LEAKAGE",
    "b09": "b9_FAIL_PIN_LEAKAGE",
    "b10": "b10_FAIL_SHORTS",
    "b11": "b11_FAIL_VIL_VIH",
    "b12": "b12_FAIL_BASIC_FUNCTION",
    "b13": "b13_FAIL_VOL_VOH",
    "b14": "b14_FAIL_DYNAMIC_ICC",
    "b15": "b15_FAIL_OPENS_OR_EDM_OR_PEM",
    "b16": "b16_FAIL_IO_TIMING",
    "b17": "b17_FAIL_HVBI_STRESS",
    "b18": "b18_FAIL_STATIC_ICC",
    "b19": "b19_FAIL_RESET",
    "b20": "b20_FAIL_CACHE",
    "b21": "b21_FAIL_CELL_STABILITY_CACHE",
    "b22": "b22_FAIL_PUPD_KEEPERS_OR_MCP_MCH",
    "b23": "b23_FAIL_BIST",
    "b24": "b24_FAIL_LOW_FREQ_TEST",
    "b25": "b25_FAIL_BOUNDARY_SCAN",
    "b26": "b26_FAIL_HVQK_STRESS",
    "b27": "b27_FAIL_PGT_OR_FIVR",
    "b28": "b28_FAIL_PLL",
    "b29": "b29_FAIL_SPECIAL_OR_MP_PECI_OR_IO_SHORTS",
    "b30": "b30_FAIL_SORT_CONTACT_RESISTANCE",
    "b31": "b31_FAIL_FUSE_RW",
    "b32": "b32_FAIL_IMPEDANCE_COMP",
    "b33": "b33_FAIL_DAT_PBIST_FUNC",
    "b34": "b34_FAIL_MCP_MCH_DYNAMIC_ICC",
    "b35": "b35_FAIL_TAP_PORT_FUNC",
    "b36": "b36_FAIL_SPECIAL_TESTS",
    "b37": "b37_FAIL_TTR_MONITOR",
    "b38": "b38_FAIL_SPECIAL_OR_RTC_VREG_OR_MCH_ISB",
    "b39": "b39_FAIL_CLK_SKEW_COMP_OR_SERIAL_10GB",
    "b40": "b40_FAIL_SPECIAL_TESTS_OR_GAUI",
    "b41": "b41_FAIL_ISCAN_CHAIN",
    "b42": "b42_FAIL_ISCAN_ATPG",
    "b43": "b43_FAIL_SPECIAL_OR_SORT_ADTL",
    "b44": "b44_FAIL_SBFT",
    "b45": "b45_FAIL_FOXTON_TECH_OR_PCU_OR_XAUI",
    "b46": "b46_FAIL_LOGIC_BIST",
    "b47": "b47_FAIL_ATSPEED_SCAN_TRANSITION_FAULTS",
    "b48": "b48_FAIL_SPECIAL_OR_IDV",
    "b49": "b49_FAIL_FUSE_READ_MIXING",
    "b50": "b50_FAIL_EDRAM_KITCHEN_SINK",
    "b51": "b51_FAIL_ODT",
    "b52": "b52_FAIL_SPECIAL_OR_XSCALE",
    "b53": "b53_FAIL_UBE",
    "b54": "b54_FAIL_SPECIAL_OR_PCI_EXPRESS",
    "b55": "b55_FAIL_TIM_TOO_HIGH_THETA",
    "b56": "b56_FAIL_KLOT",
    "b57": "b57_FAIL_WAFER_LEVEL_INKING",
    "b58": "b58_FAIL_LOT_LEVEL_INKING",
    "b59": "b59_FAIL_WAFER_LEVEL_INKING_RAD",
    "b60": "b60_FAIL_L1_CACHE",
    "b61": "b61_FAIL_L1_CELL_STABILITY",
    "b62": "b62_FAIL_L2_CACHE",
    "b63": "b63_FAIL_L2_CACHE_CELL_STABILITY_OR_ADC",
    "b64": "b64_FAIL_THERMAL_SENSOR_CIRCUITS",
    "b65": "b65_FAIL_SMALL_ARRAYS",
    "b66": "b66_FAIL_GEYSERVILLE_ISP_FUNCTIONALITY_OR_DAC",
    "b67": "b67_FAIL_MISSING_VISUAL_ID_2D_MARK",
    "b68": "b68_FAIL_ANALOG_BASIC_FUNC_OR_EDRAM_DATA",
    "b69": "b69_FAIL_UNASSIGNED_PORT",
    "b70": "b70_FAIL_TEST_ACCESS_MECHANISM_OR_RX_GAIN",
    "b71": "b71_FAIL_GPIO_OR_RX_SNR",
    "b72": "b72_FAIL_HDMT_HOT_PASSED_TO_COLD_OR_UBE_DFF_OR_RX_MTPR",
    "b73": "b73_FAIL_ICLK_CLKIO_OR_RX_SFDR",
    "b74": "b74_FAIL_MIPI_CSI_OR_RX_FLATNESS",
    "b75": "b75_FAIL_DISPLAY_PORT_OR_RX_LO_LEAKAGE",
    "b76": "b76_FAIL_PCH_SCAN_CHAIN_OR_RX_IQ_BALANCE",
    "b77": "b77_FAIL_PCH_SCAN_CAPTURE_OR_RX_FFC",
    "b78": "b78_FAIL_DFG_PLL_OR_RX_FSLOP",
    "b79": "b79_FAIL_GENERIC_SORT_CLASS_OR_RX_DC_OFFSET",
    "b80": "b80_FAIL_DIE_RECOVERY_OR_TX_POWER",
    "b81": "b81_FAIL_GFX_SCAN_CHAIN_OR_TX_SNR",
    "b82": "b82_FAIL_GFX_SCAN_ATPG_OR_TX_MTPR",
    "b83": "b83_FAIL_UNIVERSAL_SERIAL_BUS_OR_TX_SFDR",
    "b84": "b84_FAIL_GENERIC_OR_FSB_CPV_OR_TX_FLATNESS",
    "b85": "b85_FAIL_GENERIC_OR_AGP_CPV_OR_LO_LEAKAGE",
    "b86": "b86_FAIL_GENERIC_OR_MEMORY_CPV",
    "b87": "b87_FAIL_RASUM",
    "b88": "b88_FAIL_GENERIC_OR_LINUX64_OR_HDMT_DOUBLE_STACK",
    "b89": "b89_FAIL_PUDL",
    "b90": "b90_FAIL_USER_FUNC",
    "b91": "b91_FAIL_WRONG_PRODUCT_OR_NTSC_CONFIG",
    "b92": "b92_FAIL_SECURITY_DATABASE_ERROR",
    "b93": "b93_FAIL_CL_OR_QA_DOWNBIN_1",
    "b94": "b94_FAIL_CL_OR_QA_DOWNBIN_2",
    "b95": "b95_FAIL_CL_OR_QA_DOWNBIN_3",
    "b96": "b96_FAIL_CL_OR_QA_DOWNBIN_4",
    "b97": "b97_FAIL_SORT_CHUCK_HANDLER_TEMP",
    "b98": "b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN",
    "b99": "b99_FAIL_HARDWARE_ALARM",
}

def fParseLine(line):
    for key,rx in rx_dict.items():
        match = rx.search(line)
        if match:
            return key, match
    return None, None

def fParseFile(sFile,sCounterStandard,sBinStandard,sBaseDir):
    dHeader = {}
    dTests = {}
    dFlow = {}
    with open(sFile,'r') as file:
        line = file.readline()
        while line:
            # print(line)
            key,match = fParseLine(line)

            # header management
            if key == 'timestamp':
                if os.path.exists(f"{sBaseDir}\..\..\.git\logs\HEAD"):
                    sGitDir = f"{sBaseDir}\..\..\.git\logs\HEAD"
                elif os.path.exists(f"{sBaseDir}\..\..\..\..\.git\logs\HEAD"):
                    sGitDir = f"{sBaseDir}\..\..\..\..\.git\logs\HEAD"
                else:
                    utilities.fError('ERROR: Cant find the git log directory, unable to generate timestamp')
                with open(sGitDir) as f:
                    for line in f:
                        pass
                    last_line = line

                if last_line == '':
                    timestamp = match.group(1)
                else:
                    gitkey,gitmatch = fParseLine(last_line)
                    if gitkey == 'gitlog':
                        githash = gitmatch.group(1)[0:8]
                        person = gitmatch.group(2)
                        unixtime = gitmatch.group(3)
                        truetime = datetime.datetime.fromtimestamp(int(unixtime))
#                        truetime = datetime.datetime.fromtimestamp(int(unixtime),datetime.timezone.utc) if multiple timezones ever become a problem, force UTC
                        timestamp = " ".join(["# Module Revision:",person,'-',truetime.strftime("%m/%d/%y %I:%M:%S %p"),'-',githash])+'\n'
                    else:
                        timestamp = match.group(1)
                dHeader['timestamp'] = timestamp
            if key == 'version':
                version = f"Version {match.group(1)}"
                dHeader['version'] = version
            if key == 'programstyle':
                dHeader['programstyle'] = f"ProgramStyle = Modular;"
            if key == 'testplan':
                testplan = f"TestPlan {match.group(1)}"
                dHeader['testplan'] = testplan
            if key == 'import':
                importcode = f"Import {match.group(1)}"
                if 'import' in dHeader.keys():
                    dHeader['import'].append(importcode)
                else:
                    dHeader['import'] = [importcode]
            if key == 'counters':
                if sCounterStandard == 'skip' or sCounterStandard == 'hbsbcntr':
                    counters = f"{match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}"
                elif sCounterStandard == '90hbcntr':
                    counters = f"{match.group(1)}90{match.group(2)}{match.group(4)}"
                if 'counters' in dHeader.keys():
                    dHeader['counters'].append(counters)
                else:
                    dHeader['counters'] = [counters]

            #test management
            if key == 'test':
                test = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                dTests[test] = []
            if key == 'parameters':
                parameter = f"{match.group(1)} = {match.group(2)}"
                dTests[test].append(parameter)
            if key == 'fsm':
                fsm = f"{match.group(1)}"
                dTests[test].append(fsm)

            #flow management
            if key == 'flow':
                flow = f"{match.group(1)} {match.group(2)}"
                dFlow[flow] = {}
            if key == 'flowitem':
                flowitem = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                dFlow[flow][flowitem] = {}
            if key == 'result':
                result = f"Result {match.group(1)}"
                dFlow[flow][flowitem][result] = {}
            if key == 'property':
                property = f"Property PassFail = {match.group(1)}"
                dFlow[flow][flowitem][result]['property'] = property
            if key == 'setbin':
                if sBinStandard == 'hbsbcntr' or sBinStandard == 'skip' and sCounterStandard == 'hbsbcntr':  # 8 digit bins
                    setbin = f"SetBin {match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}{match.group(5)}"
                elif sBinStandard == '90hbsbzz':  # 6 digit bins
                    setbin = f"SetBin {match.group(1)}90{match.group(2)}{match.group(3)}{match.group(4)[2:4]}{match.group(5)}"
                elif sBinStandard == '90hbhbsb' or sBinStandard == 'skip' and sCounterStandard == '90hbcntr': # 4 digit bins
                    setbin = f"SetBin {match.group(1)}90{match.group(2)}{match.group(2)}{match.group(3)}{match.group(5)}"
                dFlow[flow][flowitem][result]['setbin'] = setbin
            if key == 'flowcounter':
                if sCounterStandard == 'skip' or sCounterStandard == 'hbsbcntr':
                    flowcounter = f"IncrementCounters {match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}"
                elif sCounterStandard == '90hbcntr':
                    flowcounter = f"IncrementCounters {match.group(1)}90{match.group(2)}{match.group(4)}"
                dFlow[flow][flowitem][result]['flowcounter'] = flowcounter
            if key == 'goto':
                connection = f"GoTo {match.group(1)}"
                dFlow[flow][flowitem][result]['connection'] = connection
            if key == 'return':
                connection = f"Return {match.group(1)}"
                dFlow[flow][flowitem][result]['connection'] = connection
            if key == 'compressedresult':
                result = f"Result {match.group(1)}"
                dFlow[flow][flowitem][result] = {}
                property = f"Property PassFail = {match.group(2)}"
                dFlow[flow][flowitem][result]['property'] = property
                connection = f"{match.group(3)} {match.group(4)}"
                dFlow[flow][flowitem][result]['connection'] = connection


            line = file.readline()
    return dHeader,dTests,dFlow

def fFormatMTPL(dHeader,dTests,dFlow,sFile):
    # this coding is a little bullshit, but hey, it works :)

    #this rebuilds the MTPL piece by piece, first written is header
    sFileOutput = ""
    for key in dHeader:
        if key == 'import':
            for token in dHeader[key]:
                sFileOutput += f'{token.strip()}\n'
        elif key == 'counters':
            sFileOutput += '\n'
            sFileOutput += '#Test Counter Definition\n'
            sFileOutput += 'Counters\n'
            sFileOutput += '{\n'
            for token in dHeader[key]:
                sFileOutput += f'\t{token.strip()}\n'
            sFileOutput += '}\n'
        else:
            sFileOutput += f'{dHeader[key].strip()}\n'
            sFileOutput += '\n'

    sFileOutput += '\n'

    #this writes the test definition, i.e. the parameters per test
    for keyTests in dTests:
        sTestName = keyTests
        match = re.search(r'@DUPLICATE-([A-Z]+)\s*', keyTests)
        if match:
            sNewSubflow = match.group(1)
            sTestName = sTestName.replace(f"@DUPLICATE-{sNewSubflow}",'')
        sFileOutput += f'{sTestName.strip()}\n'
        sFileOutput += '{\n'
        for key in dTests[keyTests]:
            sFileOutput += f'\t{key.strip()}\n'
        sFileOutput += '}\n'

    sFileOutput += '\n'

    #this writes the Flow/DutFlow portion of the file
    for keyFlow in dFlow:  # keyFlow is either subflow or composite name.
        try:
            assert len(dFlow[keyFlow]) > 0
        except AssertionError:
            utilities.fWarn(f"Empty! {keyFlow} contains no instances after modifications. Add correct tagging to also ")
            continue

        sFlow = keyFlow
        match = re.search(r'@LINKED-([A-Z]+)-([A-Z]+)\s*', keyFlow)
        if match:
            sFlow = sFlow.replace(match.group(0),'')
        sFileOutput += f'{sFlow.strip()}\n'
        sFileOutput += '{\n'
        for keyFlowItem in dFlow[keyFlow]:  # keyFlowItem is the nested flow item, either an instance or a composite.
            sFlowItem = keyFlowItem
            sFlowItem = sFlowItem.replace('@EDCRULE','@EDC')
            sFlowItem = sFlowItem.replace('@KILLRULE','')
            sFlowItem = sFlowItem.replace('@KILL','')
            sFileOutput += f'\t{sFlowItem.strip()}\n'
            sFileOutput += '\t{\n'
            for keyFlowPort in dFlow[keyFlow][keyFlowItem]:
                sFileOutput += f'\t\t{keyFlowPort.strip()}\n'
                sFileOutput += '\t\t{\n'
                for key in ['property','flowcounter','setbin','connection']:
                    if key in dFlow[keyFlow][keyFlowItem][keyFlowPort]:
                        sFileOutput += f'\t\t\t{str(dFlow[keyFlow][keyFlowItem][keyFlowPort][key]).strip()}\n'
                sFileOutput += '\t\t}\n'
            sFileOutput += '\t}\n'
        sFileOutput += '}\n'

    #write output string to file
    with open(sFile,'w',newline='\r\n') as writer:
        writer.write(sFileOutput)
    # return sFileOutput

def fFormatBindef(lSetBins,sTosVersion,sBinStandard,sFile):

    # need to know how to slice the setbin
    if sBinStandard == 'hbsbcntr':
        iHBIndex = 0
    elif sBinStandard == '90hbsbzz':
        iHBIndex = 2
    elif sBinStandard == '90hbhbsb':
        iHBIndex = 4

    # Initialize sbdef file
    sFileOutput = ''
    sFileOutput += "Version 1.0;\n"
    sFileOutput += "\n"
    sFileOutput += "SubBinDefs\n"
    sFileOutput += "{\n"

    # if sTosVersion == "tos_3":
    #     bDataBins = False
    #     sFileOutput +=  "\tBinGroup SoftBins\n" +\
    #                     "\t{\n"
    # else:
    #     bDataBins = True
    #     sFileOutput +=  "\tBinGroup DataBins\n" +\
    #                     "\t{\n"

    lHardBins = set([])
    lSoftBins = set([])
    lDataBins = set([])

    # loop through all setbins
    for sSetBin in sorted(lSetBins):
        sBin = sSetBin.split("_")[0]
        if len(sBin) == 9:
            sBinDigits = sBin[1:9]
            sHB = sBinDigits[iHBIndex:iHBIndex+2]
            sHBSB = sBinDigits[iHBIndex:iHBIndex+4]
        elif len(sBin) == 8:
            sBinDigits = sBin[1:8]
            sHB = sBinDigits[iHBIndex:iHBIndex+1]
            sHBSB = sBinDigits[iHBIndex:iHBIndex+3]
        else:
            utilities.fError(f"ERROR: Bin is not looking correct... please verify {sSetBin}")

        sbHB = f"b{sHB}"
        sbHBSB = f"b{sHBSB}"

        # Format the HardBins
        sHardBins = f"\t\tBin {dDescriptors[sbHB]}\t{sHB}\t: \"{dDescriptors[sbHB]}\",\tFail;\n"

        # Format the SoftBins
        if sTosVersion == "tos_3":
            sSoftBins = f"\t\tLeafBin {sbHBSB}\t{sHBSB}\t: \"{sbHBSB}_fail_SHARED_BIN\",\t{dDescriptors[sbHB]};\n"
        else:
            sSoftBins = f"\t\tBin {sbHBSB}\t{sHBSB}\t: \"{sbHBSB}\",\t{dDescriptors[sbHB]};\n"

        # Format the DataBins
        if sTosVersion == "tos_3":
            sDescriptor = f"{sHB}_FAIL_{dDescriptors[sbHB]}"
        else:
            sDescriptor = sbHBSB
        sDataBins = f"\t\tLeafBin {sSetBin}\t{sBinDigits}\t: \"{sSetBin}\",\t{sDescriptor};\n"

        lHardBins.add(sHardBins)
        lSoftBins.add(sSoftBins)
        lDataBins.add(sDataBins)

    sFileOutput += "\tBinGroup HardBins\n"
    sFileOutput += "\t{\n"
    sFileOutput += "".join(sorted(lHardBins))
    sFileOutput += "\t}\n"

    sFileOutput += "\tBinGroup SoftBins\n"
    sFileOutput += "\t{\n"
    sFileOutput += "".join(sorted(lSoftBins))
    if sTosVersion == "tos_3":
        sFileOutput += "".join(sorted(lDataBins))
        sFileOutput += "\t}\n"
    else:
        sFileOutput += "\t}\n"
        sFileOutput += "\tBinGroup DataBins\n"
        sFileOutput += "\t{\n"
        sFileOutput += "".join(sorted(lDataBins))
        sFileOutput += "\t}\n"

    sFileOutput += "}"

    with open(sFile,'w',newline='\r\n') as writer:
        writer.write(sFileOutput)

    return

def fFindValidConnection(dFlows,lAllRemoved,sRemoved,sPort):
    # Comments can help find issues in this code...
    for keyFlow in dFlows:
        for keyItem in dFlows[keyFlow]:
            match = re.search(sRemoved, keyItem)
            if match:
                if sPort not in dFlows[keyFlow][keyItem]:
                    sPort = "Result 1"
                if "GoTo" in dFlows[keyFlow][keyItem][sPort]['connection']:
                    sMatching = dFlows[keyFlow][keyItem][sPort]['connection'].split()[1].replace(';','')
                    # print("Is this item in removed?:"+sMatching)
                    if sMatching in lAllRemoved:
                        # print('Yes - We go again!')
                        return fFindValidConnection(dFlows,lAllRemoved,sMatching,sPort)
                    else:
                        # print('No - Found it!')
                        # print(dFlows[keyFlow][keyItem][sPort]['connection'])
                        return dFlows[keyFlow][keyItem][sPort]['connection']
                else:
                    # print('Found it!')
                    # print(dFlows[keyFlow][keyItem][sPort]['connection'])
                    return dFlows[keyFlow][keyItem][sPort]['connection']

def fFindEnvPaths(sFile,sText):
    with open(sFile, 'r') as file:
        line = file.readline()
        bLineFound = False
        lPathReturn = []
        while line:
            line = line.strip()
            # print(line)
            if sText in line:
                bLineFound = True
            if bLineFound:
                match = re.match(".*?\"+(.*?)[\";]+.*", line)  # this regex is extracting just the path, not the " ; or +
                if match:
                    lPathReturn.append(match.group(1))
                if line.endswith(";"): # means that the env file has rolled over to the next "variable"
                    break
            line = file.readline()
    return lPathReturn

def fFormatEnvPrint(lInputList):
    sReturnString = ''
    for index in range(len(lInputList)):
        if index < len(lInputList) - 1:
            sReturnString += f"\t\"{lInputList[index]};\" +\n"
        else:
            sReturnString += f"\t\"{lInputList[index]}\";\n"
    # print(sReturnString)
    return sReturnString


#main code - this is for testing code only

def main():
    sBaseDir = os.path.split(os.path.realpath(sys.argv[0]))[0]
    sFileName = sBaseDir+'/MTL/CLK_MAIN_GXX/output/CLK_MAIN_GXX_CLASS_M28G1/CLK_MAIN_GXX_CLASS_M28G1.mtpl'
    Header,Tests,Data = fParseFile(sFileName)

    for key in Header:
        if key == 'import':
            for token in Header[key]:
                print(token)
        elif key == 'counters':
            print('\n#Test Counter Definition')
            print('Counters')
            print('{')
            for token in Header[key]:
                print(token)
            print('}')
        else:
            print(Header[key])

    print("\n")

    for keyTests in Tests:
        print(keyTests)
        print("{")
        for key in Tests[keyTests]:
            print("\t"+key)
        print("}")

    print("\n")

    for keyFlow in Data:
        print(keyFlow)
        print("{")
        for keyFlowItem in Data[keyFlow]:
            print("\t"+keyFlowItem)
            print("\t{")
            for keyFlowPort in Data[keyFlow][keyFlowItem]:
                print("\t\t"+keyFlowPort)
                print("\t\t{")
                for key in list(Data[keyFlow][keyFlowItem][keyFlowPort]):
                    if key == "connection" and "@KILLRULE" in keyFlowItem and keyFlowPort not in ["Result -2","Result -1","Result 1"]:
                        Data[keyFlow][keyFlowItem][keyFlowPort][key] = Data[keyFlow][keyFlowItem]["Result 1"][key]
                    if key == "setbin" and "@EDC" in keyFlowItem and keyFlowPort not in ["Result -2","Result -1"]:
                        del Data[keyFlow][keyFlowItem][keyFlowPort][key]
                        continue
                    print("\t\t\t" + Data[keyFlow][keyFlowItem][keyFlowPort][key])
                print("\t\t}")
            print("\t}")
        print("}")


if __name__ == "__main__":
    main()