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
logbook = "logbook.log"

# Remove previous warnings log
def fInitializeLog():
    import os
    if os.path.exists(logbook):
        os.remove(logbook)
    return

def fLog(sString):
    with open(logbook, "a") as file:
        file.write(sString+"\n")
    return

def fWarn(sString):
    from warnings import warn
    fLog(f"-W- {sString}")
    warn(sString, stacklevel=3)

def fError(sString):
    import sys
    fLog(sString.replace("ERROR:","-E-"))
    sys.exit(sString)

def fReport():
    import time
    import os

    if os.path.exists(logbook):
        with open(logbook, "r") as file:
            loglines = file.readlines()

        iErrors = 0
        iWarnings = 0
        iInformation = 0
        for line in loglines:
            if line.startswith('-I-'):
                iInformation = iInformation + 1
            elif line.startswith('-W-'):
                iWarnings = iWarnings + 1
            elif line.startswith('-E-'):
                iErrors = iErrors + 1
            else:
                continue

        print(f"Module Execution complete with {iErrors} Errors, {iWarnings} Warnings, {iInformation} Infos. "
              f"Please see logbook.log for all messages.")

        time.sleep(3)
    return

# debug function to monitor the time taken between successive calls
def fDebugTimer(sDescriptor,oTimer,bDebug):
    import timeit

    if bDebug:
        oTimeTaken = timeit.default_timer() - oTimer
        print(f"{sDescriptor} - {oTimeTaken * 1000} mS")

    return timeit.default_timer()

# iterate through every line and replace every occurrence of sOldText with sNewText
def fReplaceTextInFileSingle(sFile,sOldText,sNewText):
    # Read in the file
    with open(sFile, 'r') as file:
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(sOldText, sNewText)

    # Write the file out again
    with open(sFile, 'w',newline='\r\n') as file:
      file.write(filedata)

# This is a new version of replaceText which operates on the full dictionary of replacements. 
def fReplaceTextInFileFull(sFile,dStrings):
    # read file into list so we can go line by line
    with open(sFile, 'r') as file:
        lines = file.readlines()

    # use list comprehension to check for any existence in line before running .replace() code.
    modified = []
    for line in lines:
        if any(keys in line for keys in dStrings):
            for key in dStrings:
                line = line.replace(key,dStrings[key])
        modified.append(line)

    # write back modified code to file.
    with open(sFile, 'w',newline='\r\n') as file:
        file.writelines(modified)

# iterate through every line and replace occurrences of text using regex
def fReplaceRegexInFileSingle(sFile,sOldExpression,sNewExpression):
    import re

    # Read in the file
    with open(sFile, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = re.sub(sOldExpression,sNewExpression,filedata)

    # Write the file out again
    with open(sFile, 'w', newline="\r\n") as file:
        file.write(filedata)

# iterate through every line and replace occurrences of text using regex
def fReplaceRegexInFileFull(sFile,dExpressions):
    import re

    # Read in the file
    with open(sFile, 'r') as file:
        filedata = file.read()

    for key in dExpressions.keys():
        regex = re.compile(key)
        filedata = regex.sub(dExpressions[key],filedata)

    # Write the file out again
    with open(sFile, 'w', newline="\r\n") as file:
        file.write(filedata)

# iterate through every line and search-replace lines with @REPLACE tag
def fReplaceTagInFile(sFile,sTag):
    import re

    # with fileinput.FileInput(sFile, inplace=True) as file:
    #     for line in file:
    #         if sTag in line:
    #             match = re.search(sTag+r'-(\w+)-(\w+)\s*',line)
    #             updated = line.replace(match.group(1),match.group(2))
    #             updated = updated.replace(sTag+'-'+match.group(1)+'-'+match.group(2),'')
    #             print(updated,end='')
    #         else:
    #             print(line, end='')

    with open(sFile,'r') as file:
        filedata = file.readlines()

    updatedata = []
    for line in filedata:
        if sTag in line:
            match = re.search(sTag+r'-(\w+)-(\w+)\s*',line)
            line = line.replace(match.group(1), match.group(2))
            line = line.replace(sTag+'-'+match.group(1)+'-'+match.group(2), '')
        updatedata.append(line)

    with open(sFile, 'w', newline='\r\n') as file:
        file.write("\n".join(updatedata))

# iterate through every line and remove lines which have a certain text string
def fRemoveLineInFile(sFile,sFindText):
    # Read in the file
    with open(sFile, 'r') as file :
        lFileLines = file.readlines()

    # BKM is to pop lines from bottom to top, otherwise list indexes can get funky
    for i in range(len(lFileLines)-1,0,-1):
        if sFindText in lFileLines[i]:
            lFileLines.pop(i)

    # Write the file out again
    with open(sFile, 'w',newline='\r\n') as file:
        file.writelines(lFileLines)

def fFileCopy(sFile,sOldDir,sNewDir,dFileCopyChecker):
    import os,shutil
    if os.path.isdir(sOldDir + '/' + sFile): return
    for sKey in dFileCopyChecker.keys():  # this dictionary is full of str:list entries with BOM, TCG, and OutputFolder names
        if any(text in sFile for text in dFileCopyChecker[sKey]):
            if sKey not in sFile: return
    # if any(bom in sFile for bom in lBOMs):
    #     if sBOM not in sFile: return
    # if any(tcgprod in sFile for tcgprod in lTCGPRODs):
    #     if sTCGPROD not in sFile: return
    if not os.path.exists(sNewDir): os.makedirs(sNewDir)
    shutil.copy(sOldDir + '/' + sFile, sNewDir + '/' + sFile)
    return

# shamelessly ripped from chatgpt :D hehehe
def fFindChecksum(sRunDir):
    import hashlib,os
    dMD5sums = {}
    for sRoot, sDirs, lFiles in os.walk(sRunDir):
        if ".git" not in sRoot and "__pycache__" not in sRoot:
            for sFile in lFiles:
                if ".git" not in sFile and "README" not in sFile:
                    sFilePath = os.path.join(sRoot,sFile)
                    sLinuxPath = sFilePath.replace(sRunDir,".").replace('\\','/')
                    with open(sFilePath, 'rb') as f:
                        file_hash = hashlib.md5()
                        chunk = f.read(8192)
                        while chunk:
                            file_hash.update(chunk)
                            chunk = f.read(8192)
                        dMD5sums[sLinuxPath] = file_hash.hexdigest()

    sChecksumFile = sRunDir + "/.github/workflows/compiled_checksums.txt"
    with open(sChecksumFile, 'w') as f:
        for key in sorted(dMD5sums.keys()):
            f.write("{}  {}\n".format(dMD5sums[key],key))

def fCheckIgnoredBinCounters(dFlows, bAutoAlarms):
    # v4.1.0 - adding warning for bins and counters that will be ignored
    for keyFlow in list(dFlows):
        for keyItem in list(dFlows[keyFlow]):
            # print(dFlows[keyFlow][keyItem])
            instance = keyItem.split()[1]
            if bAutoAlarms:
                if any('setbin' in portdict.keys() for portdict in dFlows[keyFlow][keyItem].values()):
                    fLog(
                        f"-W- Bins are governed by the bincounter.csv. All bins for {instance} in mtpl will be ignored.")
            if not bAutoAlarms:
                filtereddict = []
                for subkey in dFlows[keyFlow][keyItem].keys():
                    if subkey.strip() not in ['Result -2', 'Result -1']: filtereddict.append(
                        dFlows[keyFlow][keyItem][subkey])
                if any('setbin' in portdict.keys() for portdict in filtereddict):
                    fLog(
                        f"-W- Bins are governed by the bincounter.csv. All non-alarm bins for {instance} in mtpl will be ignored.")
            if any('flowcounter' in portdict.keys() for portdict in dFlows[keyFlow][keyItem].values()):
                fLog(
                    f"-W- Counters are governed by the bincounter.csv. All counters for {instance} in mtpl will be ignored.")

def fFindFilesNeeded(dTests, sOutputDir):
    import xml.etree.ElementTree as ET
    import re

    # Had to move AlephFile parsing to after mconfig code.
    lInputFilesNeeded = []
    lAlephFilesNeeded = []
    for keyTests in dTests:
        for keyParams in dTests[keyTests]:
            if '/' in keyParams or '\\' in keyParams:
                if 'InputFiles' in keyParams:
                    lInputFilesNeeded += re.findall("[/\\\]InputFiles[/\\\](.+?\.[a-zA-Z0-9]+?)[\s\",]", keyParams)
                    # lInputFilesNeeded.append(keyParams.split('/')[-1].replace('"','').replace(";",'').split(' ')[0])
                if 'AlephFiles' in keyParams:
                    lAlephFilesNeeded += re.findall("[/\\\]AlephFiles[/\\\](.+?\.[a-zA-Z0-9]+?)[\s\",]", keyParams)
                    # lAlephFilesNeeded.append(keyParams.split('/')[-1].replace('"', '').replace(";", '').split(' ')[0])

    tree = ET.parse(f"{sOutputDir}/module.mconfig")
    root = tree.getroot()  # ModuleConfiguration
    for child in root:
        if child.tag == 'AlephFiles':  # this is targeting files in the TP directly.
            for aleph in child:
                if "/" in aleph.text or "\\" in aleph.text:
                    if 'InputFiles' in aleph.text:
                        lInputFilesNeeded += re.findall("InputFiles[/\\\](.+\.[a-zA-Z0-9]+)", aleph.text)
                    if 'AlephFiles' in aleph.text:
                        lAlephFilesNeeded += re.findall("AlephFiles[/\\\](.+\.[a-zA-Z0-9]+)", aleph.text)
    # print(lInputFilesNeeded)
    # print(lAlephFilesNeeded)

    return lInputFilesNeeded, lAlephFilesNeeded
