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

#Standard Packages
import sys,os,json,shutil,re,timeit
import utilities as utilities
import modifications as modifications
import otpl_parser as otpl_parser
import bincounter_generator as bincounter_generator
import xml.etree.ElementTree as ET

#Installed Packages

#main code

def main():
    start_time = timeit.default_timer()

    sBaseDir = os.path.split(os.path.realpath(sys.argv[0]))[0]
    sBaseModuleName = ''
    sProduct = ''
    sInputDir = ''
    sSourceDir = ''
    sRunDir = sBaseDir

    utilities.fInitializeLog()
    bDebugPrint = False

    if len(sys.argv) < 2:
        print('No arguments given, arguments are as follows (all are optional)')
        print('-r <>: Specify the Rundir, where the output folder should be held.')
        print('-p <>: Specify the Product Folder, where the the individual modules are contained.')
        print('-m <>: Specify the Module Folder, the folder with the .mtpl collateral inside it.')
        print('-d: Specify to enable debug printing for tracking usage times.')
        print('... Assuming python is running inside module directory for this run.')
        sInputDir = sBaseDir
    else:
        for index in range(len(sys.argv)):
            if sys.argv[index] == '-r': sRunDir = sys.argv[index+1]
            if sys.argv[index] == '-p': sProduct = sys.argv[index+1]
            if sys.argv[index] == '-m': sBaseModuleName = sys.argv[index+1]
            if sys.argv[index] == '-i': sSourceDir = sys.argv[index+1]
            if sys.argv[index] == '-d': bDebugPrint = True
        sInputDir = f"{sRunDir}/{sProduct}/{sBaseModuleName}" if sSourceDir == '' else f"{sSourceDir}/{sBaseModuleName}"
        # sInputDir = sBaseModuleName  # I changed this, it will not be backwards compatible
    if not os.path.exists(sInputDir): utilities.fError(f'ERROR: Could not find input folder {sInputDir}, please double check your arguments:{sys.argv}')
    # print(sBaseDir)
    # print(sRunDir)
    # print(sInputDir)
    if not os.path.exists(f"{sInputDir}/config.json"): utilities.fError(f'ERROR: config.json not defined, please double check input dir:{sInputDir}')
    sConfigFile = open(f"{sInputDir}/config.json",'r').read()

    # load config file
    dTP = json.loads(sConfigFile)

    # v4.0.2 - Check dTP typing
    for sModuleFolderName in dTP.keys():
        for sKey in dTP[sModuleFolderName].keys():
            if sKey in ["_ModularBindef", "_EoLSwitch", "_AutoAlarms", "_ModularEnv"]:
                if type(dTP[sModuleFolderName][sKey]) is not bool:
                    utilities.fError(f"ERROR: Please ensure that json key {sKey} is of boolean typing in the json syntax")
            else:
                if type(dTP[sModuleFolderName][sKey]) is not str:
                    utilities.fError(f"ERROR: Please ensure that json key {sKey} is of string typing in the json syntax")
        # v4.1.0 - adding check for required keys
        if '_BomGroupName' not in dTP[sModuleFolderName]: utilities.fError(f"ERROR: _BomGroupName is a required key in the config.json, refer to the PPT for instructions.")
        if '_CounterStandard' not in dTP[sModuleFolderName]: utilities.fError(f"ERROR: _CounterStandard is a required key in the config.json, refer to the PPT for instructions.")
        if dTP[sModuleFolderName]['_CounterStandard'] not in ["hbsbcntr", "90hbcntr"]: utilities.fError(f"ERROR: _CounterStandard key defined as {dTP[sModuleFolderName]['_BinStandard']}. The only supported counter standard values are hbsbcntr and 90hbcntr.")
        if '_BinStandard' not in dTP[sModuleFolderName]: utilities.fError(f"ERROR: _BinStandard is a required key in the config.json, refer to the PPT for instructions.")
        if dTP[sModuleFolderName]['_BinStandard'] not in ["hbsbcntr", "90hbhbsb", "90hbsbzz"]: utilities.fError(f"ERROR: _BinStandard key defined as {dTP[sModuleFolderName]['_BinStandard']}. The only supported bin standard values are hbsbcntr, 90hbhbsb, and 90hbsbzz.")
        if '_FlowType' not in dTP[sModuleFolderName]: utilities.fError(f"ERROR: _FlowType is a required key in the config.json, refer to the PPT for instructions.")
        if dTP[sModuleFolderName]["_FlowType"] not in ["stoponfail", "forceflow"]: utilities.fError(f"ERROR: _FlowType key defined as {dTP[sModuleFolderName]['_FlowType']}. The only supported flow type values are stoponfail and forceflow.")

    # v4.1.0 - not allowing keys starting with _ outside existing feature switches:
    lCommonConfigs = ["_BomGroupName", "_CounterStandard", "_BinStandard", "_FlowType", "_TcgProduct", "_PrimeVersion",
                      "_TosVersion", "_AutoAlarms", "_EoLSwitch", "_ModularBindef", "_Idrive", "_ModularEnv", "_SubmoduleFolder"]
    for sModuleFolderName in dTP.keys():
        for sKey in dTP[sModuleFolderName].keys():
            if sKey.startswith('_') and sKey not in lCommonConfigs:
                utilities.fError(f"ERROR: Keys starting with underscore are reserved for common features. Please rename key {sKey} in config {sModuleFolderName}.")

    # v4.1.0 - making sure that all keys in each ModuleFolderName match:
    lCheck = [tuple(sorted(dTP[sModuleFolderName])) for sModuleFolderName in dTP.keys()]
    if len(set(lCheck)) > 1:
        utilities.fError(f"ERROR: Not all keys in config.json are the same, please correct. Found unique sets {lCheck}.")

    lBOMs = [dTP[sModuleFolderName]['_BomGroupName'] for sModuleFolderName in dTP.keys()]
    lKeySize = [len(dTP[sModuleFolderName]) for sModuleFolderName in dTP.keys()]
    if not all(x==lKeySize[0] for x in lKeySize): utilities.fError('ERROR: The number of custom variables dont match in the config.json')

    lTCGPRODs = []
    lModuleFolderNames = []
    for sModuleFolderName in dTP.keys():
        lModuleFolderNames.append(sModuleFolderName)
        if '_TcgProduct' in dTP[sModuleFolderName]:
            lTCGPRODs.append(dTP[sModuleFolderName]['_TcgProduct'])

    # check if input and aleph exist in source dir
    lSourceFiles = os.listdir(sSourceDir)
    sInputFileDir = ''
    sAlephFileDir = ''
    for sFile in lSourceFiles:
        if sFile == 'InputFiles':
            sInputFileDir = f"{sSourceDir}/{sFile}"
        elif sFile == 'AlephFiles':
            sAlephFileDir = f"{sSourceDir}/{sFile}"
        else:
            continue

    # find all the TP-related files
    lDirFiles = os.listdir(sInputDir)
    sInputFileMTPL = ''
    sInputFileFLW = ''
    sInputFileENV = ''
    lInputFileGeneric = []
    lInputCollateral = []
    sInputPMconfig = ''
    for sFile in lDirFiles:
        # print(sFile) # - use this to debug if you've got something weird in the files
        if sFile == 'config.json' or sFile == 'output' or sFile == 'torch_extinguisher.py' \
                or sFile == 'otpl_parser.py' or sFile == 'compile.bat':
            continue
        elif sFile.endswith('.input.mtpl'):
            sInputFileMTPL = sFile if sInputFileMTPL == '' else utilities.fError('ERROR: There can only be a single MTPL, detected multiple.')
            if sBaseModuleName == '': sBaseModuleName = sInputFileMTPL.replace('.input.mtpl','')
        elif sFile.endswith('.input.flw'):
            sInputFileFLW = sFile if sInputFileFLW == '' else utilities.fError('ERROR: There can only be a single FLW, detected multiple.')
        elif sFile.lower().endswith('_envfile.input.env'):
            sInputFileENV = sFile if sInputFileENV == '' else utilities.fError('ERROR: There can only be a single ENV, detected multiple.')
        elif sFile == 'patterns.input.pconfig' or sFile == 'module.input.mconfig':
            sInputPMconfig = sFile if sInputPMconfig == '' else utilities.fError('ERROR: Please define either .pconfig or .mconfig, not both.')
        elif '.input.' in sFile:
            lInputFileGeneric.append(sFile)
        elif os.path.isfile(os.path.join(sInputDir,sFile)):
            lInputCollateral.append(sFile)
        elif sFile == 'InputFiles' and sInputFileDir == '':
            sInputFileDir = f"{sInputDir}/{sFile}"
        elif sFile == 'InputFiles' and sInputFileDir != '':
            utilities.fError("ERROR: Detected both InputFiles folder and centralized input files. Please remove InputFiles from inside Module folder, it will cause confusion.")
        elif sFile == 'AlephFiles' and sAlephFileDir == '':
            sAlephFileDir = f"{sInputDir}/{sFile}"
        elif sFile == 'AlephFiles' and sAlephFileDir != '':
            utilities.fError("ERROR: Detected both InputFiles folder and centralized input files. Please remove AlephFiles from inside Module folder, it will cause confusion.")
        else:
            continue

    if sInputFileMTPL == '':
        print('Either paste torch_extinguisher.py + otpl_parser.py into module directory, or run with arguments.')
        print('Two arguments are required to run this script.')
        print('-p <product> => this is the product git repo')
        print('-m <module> => this is the specific module folder to compile')
        sys.exit(1)

    middle_time = utilities.fDebugTimer("Setup",start_time,bDebugPrint)

    # modification time! generating a new output folder per-BOM
    iExitCode = 0
    for sModuleFolderName in dTP.keys():
        # Required
        sBOM = dTP[sModuleFolderName]['_BomGroupName']
        sCounterStandard = dTP[sModuleFolderName]['_CounterStandard']
        sBinStandard = dTP[sModuleFolderName]['_BinStandard']
        sFlowType = dTP[sModuleFolderName]['_FlowType']

        # Optional
        sTCGPROD = dTP[sModuleFolderName]['_TcgProduct'] if '_TcgProduct' in dTP[sModuleFolderName] else ''
        sPrimeVersion = dTP[sModuleFolderName]['_PrimeVersion'] if '_PrimeVersion' in dTP[sModuleFolderName] else ''
        sTosVersion = dTP[sModuleFolderName]['_TosVersion'] if '_TosVersion' in dTP[sModuleFolderName] else ''
        bAutoAlarms = dTP[sModuleFolderName]['_AutoAlarms'] if '_AutoAlarms' in dTP[sModuleFolderName] else False
        bEoLSwitch = dTP[sModuleFolderName]['_EoLSwitch'] if '_EoLSwitch' in dTP[sModuleFolderName] else False
        bModularBindef = dTP[sModuleFolderName]['_ModularBindef'] if '_ModularBindef' in dTP[sModuleFolderName] else False
        sIdrive = dTP[sModuleFolderName]['_Idrive'] if '_Idrive' in dTP[sModuleFolderName] else ''
        sSubmoduleFolder = dTP[sModuleFolderName]['_SubmoduleFolder'] if '_SubmoduleFolder' in dTP[sModuleFolderName] else 'n/a'

        # v4.3.0 - special case for ModularEnv backwards compatibility
        if '_ModularEnv' in dTP[sModuleFolderName]:
            bModularEnv = dTP[sModuleFolderName]['_ModularEnv']
        else:
            bModularEnv = True if sInputFileENV != '' else False

        # Special Case
        sModuleName = f"{sBaseModuleName}_{sModuleFolderName}" if sModuleFolderName == sBOM else sModuleFolderName
        dTP[sModuleFolderName]['_ModuleFolderName'] = sModuleName
        dFileCopyChecker = {sModuleFolderName: lModuleFolderNames, sBOM: lBOMs, sTCGPROD: lTCGPRODs}

        print(sBOM,'Module Name:',sModuleName)
        sOutputDir = f"{sRunDir}/{sModuleName}"
        if os.path.exists(sOutputDir): shutil.rmtree(sOutputDir)
        os.makedirs(sOutputDir)
        # Modification 0 - remove boolean feature switches to not cause string replace exceptions
        if '_AutoAlarms' in dTP[sModuleFolderName].keys(): del dTP[sModuleFolderName]['_AutoAlarms']
        if '_EoLSwitch' in dTP[sModuleFolderName].keys(): del dTP[sModuleFolderName]['_EoLSwitch']
        if '_ModularBindef' in dTP[sModuleFolderName].keys(): del dTP[sModuleFolderName]['_ModularBindef']
        if '_ModularEnv' in dTP[sModuleFolderName].keys(): del dTP[sModuleFolderName]['_ModularEnv']

        # v4.1.0 - create dictionary of all proper replacements
        dReplacements = {}
        for key in dTP[sModuleFolderName].keys():
            dReplacements[f"`{key}`"] = dTP[sModuleFolderName][key]

        sNewMtpl = modifications.fMod1(sOutputDir, sModuleName, sInputDir, sInputFileMTPL, dReplacements, bEoLSwitch)
        middle_time = utilities.fDebugTimer("Mod1", middle_time, bDebugPrint)

        dHeader,dTests,dFlows = otpl_parser.fParseFile(sNewMtpl, sCounterStandard, sBinStandard, sBaseDir)

        dTests = modifications.fMod2(dTests)
        middle_time = utilities.fDebugTimer("Mod2",middle_time,bDebugPrint)

        dFlows = modifications.fMod3(dFlows)
        utilities.fCheckIgnoredBinCounters(dFlows, bAutoAlarms)
        middle_time = utilities.fDebugTimer("Mod3", middle_time, bDebugPrint)

        lInstances, lCounterKeys = bincounter_generator.fImportTests(dHeader, dTests, dFlows, sSourceDir, bAutoAlarms)
        dCounterBin = bincounter_generator.fGenerateCountersAndBins(sSourceDir, sCounterStandard, sBinStandard)
        iExitCode, dHeader, dFlows = modifications.fMod4(lInstances, lCounterKeys, dCounterBin, dHeader, dFlows, bAutoAlarms, iExitCode)
        if iExitCode == 1: continue  # v4.2.3 this ensures that CSV generation will not error out, and will finish compiling all new tests into the csv.
        middle_time = utilities.fDebugTimer("Mod4",middle_time,bDebugPrint)

        dFlows = modifications.fMod5(dFlows, sFlowType, lInstances)
        middle_time = utilities.fDebugTimer("Mod5", middle_time, bDebugPrint)

        dHeader, dTests, dFlows, lRemoveItems = modifications.fMod6(dHeader, dTests, dFlows, bEoLSwitch)
        otpl_parser.fFormatMTPL(dHeader, dTests, dFlows, sNewMtpl)
        middle_time = utilities.fDebugTimer("Mod6",middle_time, bDebugPrint)

        modifications.fMod7(bEoLSwitch, dReplacements, lRemoveItems, sInputFileFLW, sOutputDir, sModuleName, sInputDir)
        middle_time = utilities.fDebugTimer("Mod7", middle_time, bDebugPrint)

        modifications.fMod8(bEoLSwitch, sInputPMconfig, sOutputDir, sInputDir, dReplacements)
        lInputFilesNeeded, lAlephFilesNeeded = utilities.fFindFilesNeeded(dTests, sOutputDir)
        middle_time = utilities.fDebugTimer("Mod8",middle_time,bDebugPrint)

        modifications.fMod9(sModuleName, sOutputDir, sInputDir, dReplacements, lInputFileGeneric)
        middle_time = utilities.fDebugTimer("Mod9",middle_time,bDebugPrint)

        modifications.fMod10(lInputCollateral, sInputDir, sOutputDir, dFileCopyChecker)
        middle_time = utilities.fDebugTimer("Mod10",middle_time,bDebugPrint)

        modifications.fMod11(sPrimeVersion, sTosVersion, sSourceDir, sModuleName, sOutputDir, dFileCopyChecker, sInputFileDir, lInputFilesNeeded, sAlephFileDir, lAlephFilesNeeded)
        middle_time = utilities.fDebugTimer("Mod11",middle_time,bDebugPrint)

        modifications.fMod12(sOutputDir, dFileCopyChecker, sInputFileDir, lInputFilesNeeded, sAlephFileDir, lAlephFilesNeeded)
        middle_time = utilities.fDebugTimer("Mod12",middle_time,bDebugPrint)

        modifications.fMod13(bModularBindef, sTosVersion, sModuleFolderName, dFlows, sOutputDir, sModuleName, sBinStandard)
        middle_time = utilities.fDebugTimer("Mod13", middle_time, bDebugPrint)

        modifications.fMod14(bModularEnv, sInputFileENV, sIdrive, sSubmoduleFolder, sModuleFolderName, sOutputDir, sModuleName, sInputDir, dReplacements)
        middle_time = utilities.fDebugTimer("Mod14", middle_time, bDebugPrint)

    # validation - create checksum file for entire runDir for github action.
    # v4.1.0 - removing checksum methodology in lieu for github runner that runs the compile.bat directly
    # fFindChecksum(sRunDir)

    print(f"Script executed in {timeit.default_timer() - start_time} seconds.")
    utilities.fReport()
    sys.exit(iExitCode)
    # return iExitCode  # this is needed for timeit execution below

if __name__ == "__main__":
    main()

    # import timeit
    # timeit.main(args=['-n','10','-s','from __main__ import main','main()'])