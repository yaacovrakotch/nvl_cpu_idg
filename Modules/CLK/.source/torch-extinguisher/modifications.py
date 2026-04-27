#!/usr/bin/python
#------------------------------------------------------------------------------
# Name:        Torch Extinguisher
# Purpose:     Wrapper script to output module folders for multiple TORCH repos
#
# Author:      milespac
#
# Created:     06/2022
# Copyright:   (c) Miles Pacheco 2022
#
# Required Packages: n/a
#------------------------------------------------------------------------------
import utilities as utilities
import otpl_parser as otpl_parser
import bincounter_generator as bincounter_generator
import re
import shutil
import os
import json
import xml.etree.ElementTree as ET

def fMod1(sOutputDir, sModuleName, sInputDir, sInputFileMTPL, dReplacements, bEoLSwitch):
    # Modification 1a - direct replacement of text from one file to the next
    # for sField in dTP[sModuleFolderName].keys():
    #     # print(sField)
    #     utilities.fReplaceTextInFileSingle(sNewFile, '`'+sField+'`', dTP[sModuleFolderName][sField])  # don't need scope in plist file
    sNewFile = f"{sOutputDir}/{sModuleName}.mtpl"
    shutil.copy(f"{sInputDir}/{sInputFileMTPL}", sNewFile)
    utilities.fReplaceTextInFileFull(sNewFile, dReplacements)

    # Modification 1a' - re-apply "Switch" logic
    if not bEoLSwitch:
        utilities.fReplaceTextInFileSingle(sNewFile, '@EOL-REMOVE', '')

    # Modification 1b - direct replacement for params, after 1a is done
    utilities.fReplaceTagInFile(sNewFile, "@REPLACE")

    return sNewFile

def fMod2(dTests):
    # Modification 2 - check for Duplicate tests to multiple subflows!
    dTempTests = {}  # this is a change to make sure duplicate tests are added in-line, instead of at the end.
    for keyTests in list(dTests):
        dTempTests[keyTests] = dTests[keyTests].copy()
        if "@DUPLICATE" in keyTests:
            match = re.search(r'@DUPLICATE-([A-Z]+)\s*', keyTests)  # find "DUPLICATE-<>" string
            sNewSubflow = match.group(1)  # find new subflowname
            sNewTest = keyTests.replace(f"@DUPLICATE-{sNewSubflow}", '')  # remove special tag
            lNewTestSplit = sNewTest.split('_')
            lNewTestSplit[4] = sNewSubflow  # FIELD 5 is ALWAYS SUBFLOW.
            sNewTest = '_'.join(lNewTestSplit)
            dTempTests[sNewTest] = dTests[keyTests].copy()

    return dTempTests

def fMod3(dFlows):
    # Modification 3 - check for @LINKED subflow to duplicate composites.
    dTempFlows = {}
    for keyFlow in list(dFlows):
        dTempFlows[keyFlow] = dFlows[keyFlow].copy()
        if "@LINKED" in keyFlow:
            match = re.search(r'@LINKED-([A-Z]+)-([A-Z]+)\s*', keyFlow)
            sOldSubflow = match.group(1)
            sNewSubflow = match.group(2)
            sNewFlow = keyFlow.replace(f"@LINKED-{sOldSubflow}-{sNewSubflow}", '')  # remove special tag
            sNewFlow = sNewFlow.replace(sOldSubflow, sNewSubflow)  # rename flow
            dTempFlows[sNewFlow] = dFlows[keyFlow].copy()
            for keyItem in list(dTempFlows[sNewFlow]):
                sNewItem = keyItem.replace(sOldSubflow, sNewSubflow)
                dTempFlows[sNewFlow][sNewItem] = dTempFlows[sNewFlow][keyItem].copy()
                del dTempFlows[sNewFlow][keyItem]
                for keyPort in dTempFlows[sNewFlow][sNewItem]:
                    dTempFlows[sNewFlow][sNewItem][keyPort] = dTempFlows[sNewFlow][sNewItem][keyPort].copy()
                    for key in dTempFlows[sNewFlow][sNewItem][keyPort]:
                        sNewValue = dTempFlows[sNewFlow][sNewItem][keyPort][key].replace(sOldSubflow, sNewSubflow)
                        dTempFlows[sNewFlow][sNewItem][keyPort][key] = sNewValue

    return dTempFlows

def fMod4(lInstances,lCounterKeys,dCounterBin,dHeader,dFlows,bAutoAlarms,iExitCode):
    # Modification 4 - counter and bin allocation via automated method.
    # Modification 4 - first we make sure CSV is updated, and then generate counters/bins for all tests in the mtpl.
    sTestplanName = dHeader['testplan'].replace("TestPlan ", "").strip().replace(";", "")

    dHeader['counters'] = []  # update header section.
    for iter in lCounterKeys:
        if iter not in dCounterBin:
            # This is special error code that is handling the initial csv case
            utilities.fLog(
                f"-E- detected test {iter} not in generated counter & bin definition. Did you update the bincounter.csv?")
            print(
                f"ERROR: detected test {iter} not in generated counter & bin definition. Did you update the bincounter.csv?")
            iExitCode = 1
        else:
            dHeader['counters'].append(dCounterBin[iter]['counter'].split(":")[-1] + ",")

    if iExitCode == 0:
        dHeader['counters'] = sorted(dHeader['counters'])
        dHeader['counters'][-1] = dHeader['counters'][-1].replace(",", "")

        for keyFlow in dFlows:  # now update all dutflowitems
            for keyFlowItem in dFlows[keyFlow]:
                instance = keyFlowItem.split(" ")[1]
                if instance in lInstances:
                    for keyPort in dFlows[keyFlow][keyFlowItem]:
                        port = keyPort.split(" ")[-1]
                        if dFlows[keyFlow][keyFlowItem][keyPort]["property"] == "Property PassFail = \"Pass\";":
                            continue
                        if port in ["-1", "-2"]:
                            if bAutoAlarms:
                                port = port.replace("-", "n")
                            else:
                                continue
                        tKey = tuple([sTestplanName, instance, port])
                        dFlows[keyFlow][keyFlowItem][keyPort][
                            "flowcounter"] = f"IncrementCounters {dCounterBin[tKey]['counter']};"
                        dFlows[keyFlow][keyFlowItem][keyPort]["setbin"] = f"SetBin {dCounterBin[tKey]['bin']};"

    return iExitCode, dHeader, dFlows

def fMod5(dFlows,sFlowType,lInstances):
    # Modification 5 - flow correction; this will look for "KILLRULE" to dynamically reroute Forceflow/stoponfail
    # Modification 5 - flow correction; if "EDCRULE" is found, it will act like TPIE EDC rules and reroute failports to port1
    # Modification 5 - flow correction; this will autodetect (and remove!) an issue where setbin is defined on EDC instance.
    for keyFlow in dFlows:
        for keyItem in dFlows[keyFlow]:
            instance = keyItem.split(" ")[1]
            for keyPort in dFlows[keyFlow][keyItem]:
                if ((keyPort not in ["Result -2", "Result -1"]) and
                        (dFlows[keyFlow][keyItem][keyPort]['property'].lower().strip() not in [
                            "property passfail = \"pass\";"])):
                    if ((sFlowType == 'forceflow' and '@KILLRULE' in keyItem) or '@EDCRULE' in keyItem):
                        dFlows[keyFlow][keyItem][keyPort]['connection'] = dFlows[keyFlow][keyItem]["Result 1"][
                            'connection']
                    if 'setbin' not in dFlows[keyFlow][keyItem][keyPort] and '@KILL' in keyItem:
                        utilities.fError(
                            f"ERROR: KILL assigned for test with no setbin definition - {keyItem} - port {keyPort}")
                    if 'setbin' in dFlows[keyFlow][keyItem][keyPort] and \
                            ('@EDC' in keyItem or '@EDCRULE' in keyItem):
                        del dFlows[keyFlow][keyItem][keyPort]['setbin']
                    if not any(tag in keyItem for tag in
                               ['@EDC', '@EDCRULE', '@KILL', '@KILLRULE']) and instance in lInstances:
                        utilities.fLog(
                            f"-W- Test {instance} does not contain any tags from [@EDC, @EDCRULE, @KILL, @KILLRULE], assuming that this test is supposed to be in kill")

    return dFlows

def fMod6(dHeader,dTests,dFlows,bEoLSwitch):
    # Modification 6 - EoL Test removal; this will remove items from both dTests and dFlows prior to the fFormatMtpl
    # Modification 6 - Haven't yet figured out how to only copy needed input files and not "all"...
    lRemoveItems = []
    if bEoLSwitch:

        # This code removes instances from the "test definitions".
        lRemoveTests = []
        dTempTests = {}
        for keyTests in list(dTests):
            if "@EOL-REMOVE" in keyTests:
                # match = re.search(r'@EOL-REMOVE', keyTests)  # find "EOL-REMOVE" string
                lRemoveTests.append(keyTests.split()[2].replace('@EOL-REMOVE', ''))
                utilities.fLog(f"-I- Found Test to remove:{lRemoveTests[-1]}")
            else:
                dTempTests[keyTests] = dTests[keyTests].copy()
        dTests = dTempTests
        # print(lRemoveTests)

        # This code removes flows & flowitems from the "flow definitions".
        lRemoveFlows = []
        lRemoveItems = []
        dTempFlows = {}
        for keyFlow in list(dFlows):
            if "@EOL-REMOVE" in keyFlow:  # composite level removal
                # match = re.search(r'@EOL-REMOVE', keyFlow)  # find "EOL-REMOVE" string
                # print(keyFlow)
                # if match:  # if we match, by nature we do not copy the structure over to the dTempFlow
                lRemoveFlows.append(keyFlow.split()[1].replace('@EOL-REMOVE', ''))
                utilities.fLog(f"-I- Found DutFlow to remove:{lRemoveFlows[-1]}")
                for keyItem in list(dFlows[keyFlow]):
                    lRemoveItems.append(keyItem.split()[1].replace('@EOL-REMOVE', ''))
            else:
                dTempFlows[keyFlow] = dFlows[keyFlow].copy()
                for keyItem in list(dTempFlows[keyFlow]):
                    if "@EOL-REMOVE" in keyItem:  # instance level removal
                        # match = re.search(r'@EOL-REMOVE', keyItem)
                        # if match:
                        lRemoveItems.append(keyItem.split()[1].replace('@EOL-REMOVE', ''))
                        utilities.fLog(f"-I- Found DutFlowItem to remove:{lRemoveItems[-1]}")
                        del dTempFlows[keyFlow][keyItem]
                    else:
                        # New code to try to detect REMOVE tests which only have TAG in upper area (not lower).
                        if keyItem.split()[1] in lRemoveTests:
                            lRemoveItems.append(keyItem.split()[1].replace('@EOL-REMOVE', ''))
                            utilities.fLog(f"-I- Found DutFlowItem to remove:{lRemoveItems[-1]}")
                            del dTempFlows[keyFlow][keyItem]
                        else:
                            dTempFlows[keyFlow][keyItem] = dFlows[keyFlow][keyItem].copy()

        # this code re-checks for DutFlowItem copies of DutFlows that were removed.
        if len(lRemoveFlows) > 0:
            for keyFlow in list(dTempFlows):
                for keyItem in list(dTempFlows[keyFlow]):
                    for removed in lRemoveFlows:
                        # I'm adding a space here to make sure that we're matching with a whole DutFlowItem name, not a piece of one
                        removed = f" {removed} "
                        if removed in keyItem:
                            utilities.fLog(f"-I- Found copy of removed flow: {removed} in FlowItem:{keyItem}")
                            del dTempFlows[keyFlow][keyItem]
                            lRemoveItems.append(keyItem.split()[1].replace(' @EOL-REMOVE', ''))

        # this code re-checks the tests to remove tests which only have tags in flow area.
        if any((True for x in lRemoveItems if x not in lRemoveTests)):
            dTempTests = {}
            for keyTests in list(dTests):
                if keyTests.split()[2] in lRemoveItems:
                    lRemoveTests.append(keyTests.split()[2])
                    utilities.fLog(f"-I- Found Test to remove:{lRemoveTests[-1]}")
                else:
                    dTempTests[keyTests] = dTests[keyTests].copy()
            dTests = dTempTests

        # v4.2.0 we need to remove the counters from the header on removed tests
        lTempCounters = dHeader["counters"].copy()
        for keyCounters in dHeader["counters"]:
            if any(testname in "fail_" + keyCounters + "_" for testname in lRemoveTests):
                # print(f"found match! {keyCounters}")
                lTempCounters.remove(keyCounters)
        dHeader["counters"] = lTempCounters
        dHeader['counters'][-1] = dHeader['counters'][-1].replace(",", "")  # v4.3.0 bugfix to always remove the last comma in the counter list

        # print(lRemoveItems + lRemoveFlows)
        # This code iterates through and tries to "intelligently" re-route flow connections for removed items
        if len(lRemoveItems) > 0 or len(lRemoveFlows) > 0:
            for keyFlow in dTempFlows:
                for keyItem in dTempFlows[keyFlow]:
                    for keyPort in dTempFlows[keyFlow][keyItem]:
                        for removed in lRemoveFlows + lRemoveItems:
                            # I'm adding a space here to make sure that we're matching with a whole connection, not part of one.
                            removed = f" {removed};"
                            if removed in dTempFlows[keyFlow][keyItem][keyPort]['connection']:
                                utilities.fLog(
                                    f"-I- Found connection to removed item: {dTempFlows[keyFlow][keyItem][keyPort]['connection']}")
                                # print(removed)
                                dTempFlows[keyFlow][keyItem][keyPort]['connection'] = otpl_parser.fFindValidConnection(
                                    dFlows, lRemoveFlows + lRemoveItems, removed.replace(";", " "), keyPort)
                                break
            dFlows = dTempFlows

    return dHeader, dTests, dFlows, lRemoveItems

def fMod7(bEoLSwitch,dReplacements,lRemoveItems,sInputFileFLW,sOutputDir,sModuleName,sInputDir):
    # Modification 7 - FLW correction only need to do the first step for FLW files
    if sInputFileFLW != "":
        sNewFile = f"{sOutputDir}/{sModuleName}.flw"
        shutil.copy(f"{sInputDir}/{sInputFileFLW}", sNewFile)
        utilities.fReplaceTextInFileFull(sNewFile, dReplacements)

        # Modification 7a - remove instances which were removed by @EOL tag from the FLW file.
        if bEoLSwitch:
            utilities.fRemoveLineInFile(sNewFile, '@EOL-REMOVE')
            for sItemName in lRemoveItems:
                # FlowItem have syntax "<Module>::<FLOW>.<FLOWITEM>", so trying to make sure we're only matching a full flowitem.
                sItemName = f".{sItemName}\""
                utilities.fRemoveLineInFile(sNewFile, sItemName)
        else:
            utilities.fReplaceTextInFileSingle(sNewFile, '@EOL-REMOVE', '')

    return

def fMod8(bEoLSwitch,sInputPMconfig,sOutputDir,sInputDir,dReplacements):
    # Modification 8 - pconfig/mconfig update, largely the same as FLW, with some custom code.
    # v4.1.0 - removing special idut code, as it's not cohesive to rest of script.
    if sInputPMconfig != "":
        sNewFile = f"{sOutputDir}/module.mconfig"
        shutil.copy(f"{sInputDir}/{sInputPMconfig}", sNewFile)
        utilities.fReplaceTextInFileFull(sNewFile, dReplacements)

        # Modification 8a - update mconfig if @EOL-REMOVE is present
        if bEoLSwitch:
            utilities.fRemoveLineInFile(sNewFile, '@EOL-REMOVE')
        else:
            utilities.fReplaceTextInFileSingle(sNewFile, '@EOL-REMOVE', '')

    return

def fMod9(sModuleName,sOutputDir,sInputDir,dReplacements,lInputFileGeneric):
    # Modification 9 - generic input file update, allows mod1 changes.
    for sFile in lInputFileGeneric:
        sNewFile = f"{sOutputDir}/{sModuleName}.{sFile.split('.')[-1]}"
        shutil.copy(f"{sInputDir}/{sFile}", sNewFile)
        utilities.fReplaceTextInFileFull(sNewFile, dReplacements)

    return


def fMod10(lInputCollateral,sInputDir,sOutputDir,dFileCopyChecker):
    # Modification 10 - copy other TP-related files. Only include files with current BOM in it (or BOM agnostic)
    for sFile in lInputCollateral:
        utilities.fFileCopy(sFile, sInputDir, sOutputDir, dFileCopyChecker)

    return


def fMod11(sPrimeVersion,sTosVersion,sSourceDir,sModuleName,sOutputDir,dFileCopyChecker,sInputFileDir,lInputFilesNeeded,sAlephFileDir,lAlephFilesNeeded):
    # Modification 11 - setting up Prime variable properly, and doing another pass for specific text replacements.
    if sPrimeVersion:
        sPrimeVersion = sPrimeVersion.lower()
        if not re.search(r'^prime_v[\d\.]+$', sPrimeVersion):
            if re.search(r'^[\d\.]+$', sPrimeVersion):
                sPrimeVersion = 'prime_v' + sPrimeVersion
            elif re.search(r'^prime[\d\.]+$', sPrimeVersion):
                sPrimeVersion = sPrimeVersion.replace('prime', 'prime_v')
            elif re.search(r'^prime_v[\d\.]+_.*$', sPrimeVersion):
                sPrimeVersion = 'prime_' + (sPrimeVersion.split('_')[1])
            else:
                utilities.fError(
                    f'ERROR: Could not determine proper prime version in config.json, please format such as prime_v12.01.02:{sPrimeVersion}')

        if not re.search(r'^prime_v\d+\.\d+\.\d+$', sPrimeVersion):
            if len(sPrimeVersion.split('.')) == 1:
                sRelease = sPrimeVersion
                sPatch = sPrimeVersion
            elif len(sPrimeVersion.split('.')) == 2:
                sRelease = sPrimeVersion.split('.')[0]
                sPatch = sPrimeVersion
            else:
                utilities.fError(
                    f'ERROR: How did you get here? Your Prime version should match prime_v12.01.01 format, it was {sPrimeVersion}')
        else:
            sRelease = sPrimeVersion.split('.')[0]
            sPatch = sRelease + sPrimeVersion.split('.')[1]

        # Modification 11a - check for overrides file and apply ALL matching versions, whether prime_v12, prime_v12.01, or prime_v12.01.02
        # mainly targeting mtpl, can bugfix this to additional updates later.
        if os.path.exists(f"{sSourceDir}/prime_overrides.json"):
            sConfigFile = open(f"{sSourceDir}/prime_overrides.json", 'r').read()
            dPrimeEdits = json.loads(sConfigFile)
            for key in [sRelease, sPatch, sPrimeVersion]:
                if key in dPrimeEdits:
                    utilities.fReplaceRegexInFileFull(f"{sOutputDir}/{sModuleName}.mtpl", dPrimeEdits[key])

        # Modification 11b - check for existence of Prime subdirs in the InputFiles and AlephFiles
        if sInputFileDir:
            lInputFileDir = os.listdir(sInputFileDir)
            for sPrimeDir in lInputFileDir:
                if re.search('prime', sPrimeDir):
                    if os.path.isdir(f"{sInputFileDir}/{sPrimeDir}") and any(
                            ver == sPrimeDir for ver in [sRelease, sPatch, sPrimeVersion]):
                        for sSubFile in os.listdir(f"{sInputFileDir}/{sPrimeDir}"):
                            if sSubFile in lInputFilesNeeded:
                                utilities.fFileCopy(sSubFile, f"{sInputFileDir}/{sPrimeDir}",
                                                    f"{sOutputDir}/InputFiles", dFileCopyChecker)
                            # else:
                            #     utilities.fLog(f"-W- NOT COPYING FILE {sFile}")

        if sAlephFileDir:
            lAlephFileDir = os.listdir(sAlephFileDir)
            for sPrimeDir in lAlephFileDir:
                if re.search('prime', sPrimeDir):
                    if os.path.isdir(f"{sAlephFileDir}/{sPrimeDir}") and any(
                            ver == sPrimeDir for ver in [sRelease, sPatch, sPrimeVersion]):
                        for sSubFile in os.listdir(f"{sAlephFileDir}/{sPrimeDir}"):
                            if sSubFile in lAlephFilesNeeded:
                                utilities.fFileCopy(sSubFile, f"{sAlephFileDir}/{sPrimeDir}",
                                                    f"{sOutputDir}/AlephFiles", dFileCopyChecker)
                            # else:
                            #     utilities.fLog(f"-W- NOT COPYING FILE {sFile}")

    if sTosVersion:
        sTosVersion = sTosVersion.lower()
        if not re.search(r'^tos_[\d\.]+$', sTosVersion):
            if re.search(r'^[\d\.]+$', sTosVersion):
                sTosVersion = f"tos_{sTosVersion}"
            elif re.search(r'^tos[\d\.]+$', sTosVersion):
                sTosVersion = sTosVersion.replace('tos', 'tos_')
            elif re.search(r'^tos_[\d\.]+_.*$', sTosVersion):
                sTosVersion = f"tos_{sTosVersion.split('_')[1]}"
            else:
                utilities.fError(
                    f'ERROR: Could not determine proper TOS version, please format such as tos_3.10.06:{sTosVersion}')

        if not re.search(r'^tos_\d+\.\d+\.\d+$', sTosVersion):
            if len(sTosVersion.split('.')) == 1:
                sRelease = sTosVersion
                sPatch = sTosVersion
            elif len(sTosVersion.split('.')) == 2:
                sRelease = sTosVersion.split('.')[0]
                sPatch = sTosVersion
            else:
                utilities.fError(
                    f'ERROR: How did you get here? Your TOS version should match tos_3.10.06 format, it was {sTosVersion}')
        else:
            sRelease = sTosVersion.split('.')[0]
            sPatch = sRelease + sTosVersion.split('.')[1]

        # Modification 11c - check for overrides file and apply ALL matching versions, whether prime_v12, prime_v12.01, or prime_v12.01.02
        # mainly targeting mtpl, can bugfix this to additional updates later.
        if os.path.exists(f"{sSourceDir}/tos_overrides.json"):
            sConfigFile = open(f"{sSourceDir}/tos_overrides.json", 'r').read()
            dTosEdits = json.loads(sConfigFile)
            for key in dTosEdits:
                if key in [sRelease, sPatch, sTosVersion]:
                    utilities.fReplaceRegexInFileFull(f"{sOutputDir}/{sModuleName}.mtpl", dTosEdits[key])

    return

def fMod12(sOutputDir,dFileCopyChecker,sInputFileDir,lInputFilesNeeded,sAlephFileDir,lAlephFilesNeeded):
    # Modification 12 - copy InputFiles/AlephFiles folder and related files. Only include files with current BOM in it (or BOM agnostic)
    if sInputFileDir:
        lInputFileDir = os.listdir(sInputFileDir)
        for sFile in lInputFileDir:
            if sFile in lInputFilesNeeded:
                utilities.fFileCopy(sFile, sInputFileDir, f"{sOutputDir}/InputFiles", dFileCopyChecker)
            # else:
            #     utilities.fLog(f"-W- NOT COPYING FILE {sFile}")

    if sAlephFileDir:
        lAlephFileDir = os.listdir(sAlephFileDir)
        for sFile in lAlephFileDir:
            if sFile in lAlephFilesNeeded:
                utilities.fFileCopy(sFile, sAlephFileDir, f"{sOutputDir}/AlephFiles", dFileCopyChecker)
            # else:
            #     utilities.fLog(f"-W- NOT COPYING FILE {sFile}")

    return

def fMod13(bModularBindef,sTosVersion,sModuleFolderName,dFlows,sOutputDir,sModuleName,sBinStandard):
    # Modification 13 - Modular Bindef Implementation
    if bModularBindef:
        if sTosVersion == '':
            utilities.fError(
                f"ERROR: Modular Bindef feature detected for config {sModuleFolderName}, but tos version not defined. Please add _TosVersion to config.json.")
        if not re.search(r'^tos_\d+\.\d+\.\d+$',sTosVersion):
            if len(sTosVersion.split('.')) == 1:
                sRelease = sTosVersion
            elif len(sTosVersion.split('.')) == 2:
                sRelease = sTosVersion.split('.')[0]
            else:
                utilities.fError(f'ERROR: How did you get here? Your TOS version should match tos_3.10.06 format, it was {sTosVersion}')
        else:
            sRelease = sTosVersion.split('.')[0]

        lSetBins = []
        for keyFlow in dFlows:
            for keyItem in dFlows[keyFlow]:
                for keyPort in dFlows[keyFlow][keyItem]:
                    if 'setbin' in dFlows[keyFlow][keyItem][keyPort]:
                        lSetBins.append(dFlows[keyFlow][keyItem][keyPort]['setbin'])
        unique = set()
        lSetBins = [item.split(' ')[1].split('.')[-1].split(';')[0] for item in lSetBins if
                    item not in unique and (unique.add(item) or True)]
        # print(lSetBins)
        sNewFile = f"{sOutputDir}/{sModuleName}_SubBinDefinitions.sbdefs"
        otpl_parser.fFormatBindef(lSetBins, sRelease, sBinStandard, sNewFile)

    return

def fMod14(bModularEnv,sInputFileENV,sIdrive,sSubmoduleFolder,sModuleFolderName,sOutputDir,sModuleName,sInputDir,dReplacements):
    # Modification 14 - Modular Env Implementation
    if bModularEnv:
        if not sInputFileENV: utilities.fError(
            f"ERROR: Modular ENV feature detected for config {sModuleFolderName}, but *_EnvFile.input.env not detected. Please check source folder and add if missing."
        )
        if not sIdrive: utilities.fError(
            f"ERROR: Modular Env feature detected for config {sModuleFolderName}, but I:\\ drive not defined. Please add _Idrive to config.json."
        )
        if sSubmoduleFolder == "n/a": utilities.fError(
            f"ERROR: Modular Env feature detected for config {sModuleFolderName}. v4.4.0 and above now requires that _SubmoduleFolder add to config.json. Set the name of the folder inside /Modules/ folder which points to submodule, or blank for no TP submodule usage."
        )

        sNewFile = f"{sOutputDir}/{sModuleName}_EnvFile.env"
        shutil.copy(f"{sInputDir}/{sInputFileENV}", sNewFile)
        utilities.fReplaceTextInFileFull(sNewFile, dReplacements)

        # Deal with ALEPH Files
        lEnvAlephFiles = []
        tree = ET.parse(f"{sOutputDir}/module.mconfig")
        root = tree.getroot()  # ModuleConfiguration
        for child in root:
            # print(child.tag, child.attrib)
            if child.tag == 'AlephFiles':  # TP level aleph files
                for aleph in child:
                    lEnvAlephFiles.append(f"~HDMT_TP_BASE_DIR/Modules/{sSubmoduleFolder}/{sModuleName}/{aleph.text}")
            else:
                for patroot in child:
                    sPatchPath = patroot.attrib['Path'].replace('\\', '/') + patroot.attrib['Rev'] + '/' + \
                                 patroot.attrib['Patch']
                    for subchild in patroot:
                        if subchild.tag == 'AlephFiles':
                            for aleph in subchild:
                                lEnvAlephFiles.append(f"{sPatchPath}/{aleph.text}")

        # Deal with env paths
        lPlistPaths = []
        lPatPaths = []
        for child in root:
            if child.tag == "Patterns":
                for patroot in child:
                    sPatchPath = patroot.attrib['Path'].replace('\\', '/') + patroot.attrib['Rev'] + '/' + \
                                 patroot.attrib['Patch']
                    sEnvFile = sPatchPath.replace("I:", sIdrive) + '/env/env.env'
                    # print(sEnvFile)
                    lPlistPaths += otpl_parser.fFindEnvPaths(sEnvFile, "HDST_PLIST_PATH")
                    lPatPaths += otpl_parser.fFindEnvPaths(sEnvFile, "HDST_PAT_PATH")

        # print(lEnvAlephFiles)
        # print(lPlistPaths)
        # print(lPatPaths)

        utilities.fReplaceTextInFileSingle(sNewFile, "<ALEPH_FILES>",
                                           "\n" + otpl_parser.fFormatEnvPrint(lEnvAlephFiles))
        utilities.fReplaceTextInFileSingle(sNewFile, "<PLIST_PATH>", "\n" + otpl_parser.fFormatEnvPrint(lPlistPaths))
        utilities.fReplaceTextInFileSingle(sNewFile, "<PAT_PATH>", "\n" + otpl_parser.fFormatEnvPrint(lPatPaths))

    return
