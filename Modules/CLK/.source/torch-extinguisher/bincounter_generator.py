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
import os, sys, csv
import utilities as utilities


# import tests will read in the CSV, check the MTPL tests vs the CSV, and add any missing tests to the CSV for the user to fill in.
def fImportTests(dHeader, dTests, dFlow, sSourceDir, bAutoAlarms):
    # first generate list of tests in the CSV file
    import csv
    f = f"{sSourceDir}/bincounter.csv"
    lTests = []
    if os.path.exists(f):
        with open(f, 'r') as csv_file:
            reader = csv.DictReader(csv_file, dialect='excel')
            for row in reader:
                lTests.append(tuple([row["module"], row["instance"], row["port"]]))
    else:
        with open(f, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, dialect='excel')
            writer.writerow(["module", "instance", "port", "hardbin", "softbin", "counter", "bindesc"])
    # print(lTests)

    # now generate list of instances in the current mtpl file.
    module = dHeader["testplan"].split(" ")[1].replace(";", "").strip()
    # print(module)
    lInstances = []
    for keyInstance in dTests:
        lInstances.append(keyInstance.split(" ")[2])
    # print(lInstances)
    lKeys = []
    for keyFlow in dFlow:
        for keyFlowItem in dFlow[keyFlow]:
            instance = keyFlowItem.split(" ")[1]
            if instance in lInstances:
                for keyPort in dFlow[keyFlow][keyFlowItem]:
                    port = keyPort.split(" ")[-1]
                    if "\"Pass\"" in dFlow[keyFlow][keyFlowItem][keyPort]["property"]:
                        continue
                    if port in ["-1", "-2"]:
                        if bAutoAlarms:
                            port = port.replace("-", "n")
                        else:
                            continue
                    lKeys.append(tuple([module, instance, port]))
    # print(lKeys)

    # This will look for missing tests and then update the csv with those missing tests.
    lUpdates = []
    for key in lKeys:
        if key not in lTests:
            (module, instance, port) = key
            lTests.append(key)
            lUpdates.append([module, instance, port, "", "", "", ""])
    if len(lUpdates)>0:
        print("Adding the following instances to the CSV - this WILL cause the script to error out. Please update the CSV.")
        print(lUpdates)
        with open(f, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, dialect='excel')
            for row in lUpdates:
                writer.writerow(row)

    # return the instances and keys for making the extinguisher calls easier.
    return lInstances,lKeys

def fCounterAlgorithm(hardbin, softbin, counterlist, minimum=0000, maximum=9999):
    # this filters the full list of counters to just those matching the HBSB.
    locallist = []
    hbsb = "{}{:0>2}".format(hardbin, softbin)
    for item in counterlist:
        if item.startswith(hbsb):
            locallist.append(int(item[-4:]))
    locallist.sort()
    # print(locallist)

    # if the matching list is greater than 99, we need to use all 4 counter digits for uniqueness.
    if len(locallist)>99:
        counter = minimum
        upperbound = maximum+1
        while counter in locallist and counter < upperbound:
            # print(counter)
            counter = counter+1
        if counter == upperbound:
            utilities.fError(f"ERROR: Insufficient counters available for {hardbin}{softbin} - counter {counter} is out of range.")
    # if the matching list is less than 100, we can manage with just the bottom 2 digits so we can use the SB in the counter.
    else:
        counter = int(softbin) * 100
        upperbound = int(softbin) * 100 + 99
        # v4.2.0 - adding range function to algorithm, this logic makes sure that the sb range counters are valid
        if maximum < counter or minimum > upperbound:
            counter = minimum
            upperbound = maximum
        else:
            counter = max(counter, minimum)
            upperbound = min(upperbound, maximum)
        upperbound = upperbound + 1
        while counter in locallist and counter < upperbound:
            # print(counter)
            counter = counter+1
        if counter == upperbound:
            utilities.fError(f"ERROR: Insufficient counters available for {hardbin}{softbin} - counter {counter} is out of range.")

    return "{:0>4}".format(counter)

def fGenerateCountersAndBins(sSourceDir, sCounterStandard, sBinStandard):
    counterlist = []

    # first we will parse the CSV file, generating a dictionary of tests that we are working on.
    # f = sSourceDir + '/_source/torch-extinguisher/bincounter.csv'
    f = f"{sSourceDir}/bincounter.csv"
    if os.path.exists(f):
        with open(f, "r") as csv_file:
            reader = csv.DictReader(csv_file, dialect='excel')
            dTest = {}
            for row in reader:
                if not (row["hardbin"].isdigit() and 1 <= len(row["hardbin"]) <= 2):
                    utilities.fLog(f"-E- Hardbin must be a number between 1 and 2 digits. Detected \"{row['hardbin']}\" for row {row}")
                    return {}
                if not (row["softbin"].isdigit() and 1 <= len(row["softbin"]) <= 2):
                    utilities.fLog(f"-E- Softbin must be a number between 1 and 2 digits. Detected \"{row['softbin']}\" for row {row}")
                    return {}
                if not ((row["counter"].isdigit() and 1 <= len(row["counter"]) <= 4) or (row["counter"] == "auto") or (":" in row["counter"] and 3 <= len(row["counter"]) <= 9)):
                    if ":" not in row["counter"] and 3 <= len(row["counter"]) <= 9:
                        utilities.fError(f"ERROR: valid configuration attempted in bincounter.csv, but malformed. Counter column must be number between 1 to 4 digits, the word 'auto', or a range 'M:N' of two 1 to 4 digit numbers. Detected \"{row['counter']}\" for row {row}")
                    utilities.fLog(f"-E- Counter must be a number between 1 and 4 digits, the word 'auto', or a range M:N. Detected \"{row['counter']}\" for row {row}")
                    return {}
                if row["bindesc"] == "":
                    row["bindesc"] = f"{row['module']}_{row['instance']}_{row['port']}"
                    utilities.fLog(f"-W- Bindesc not found in bincounter.csv. Trying to use module:instance:port, but this might fail load/checkers. row: {row}")
                tKey = tuple([row["module"],row["instance"],row["port"]])
                if tKey in dTest:
                    utilities.fError(f"ERROR: Duplicate definition found for module {row['module']} instance {row['instance']} port {row['port']}. Please remove duplicate.")
                dTest[tKey] = {"module": row["module"],
                                 "instance": row["instance"],
                                 "port": row["port"],
                                 "hardbin": "{}".format(row["hardbin"]),
                                 "softbin": "{:0>2}".format(row["softbin"]),
                                 "counter": "{}".format(row["counter"]),
                                 "bindesc": row["bindesc"]}
                if row["counter"] == "auto": dTest[tKey]["counter"] = "0000:9999"  # this is to make auto and range M:N act the same way
                if ":" not in dTest[tKey]["counter"]:
                    tempcounter = "{}{:0>2}{:0>4}".format(row['hardbin'],row['softbin'],row['counter'])
                    if tempcounter in counterlist:
                        utilities.fError(f"ERROR: Duplicate counter {tempcounter} found in csv file, please verify the following row: {row}")
                    else:
                        counterlist.append(tempcounter)
                # print("{} is processed".format(tKey))
        # prints data for all tests
        # for keyiter in dTest.keys():
        #     for dictiter in dTest[keyiter]:
        #         print("{}: {}".format(dictiter, dTest[keyiter][dictiter]))

    # This is a cache of all previously generated "auto" counters, it DOES NOT include the static counter values in the csv.
    dCache = {}
    lCache = []
    f = f"{sSourceDir}/bincounter.cache"
    if os.path.exists(f):
        with open(f, "r") as cache_file:
            reader = cache_file.read()
            lCache = reader.split("\n")
            while ("" in lCache):
                lCache.remove("")
        # print(templist)
        for item in lCache[:]: # creating a copy of the list since I will be removing un-needed counters
            # item format: CLK_MAIN_CXX::n28202000_fail_FLOWFORK_LJ_UF_K_END_X_X_X_X_HVM_FMAXCHECK_0
            tempcounter = item.split("::n")[1].split("_")[0]
            # print(tempcounter)
            if tempcounter in counterlist:
                utilities.fError(f"ERROR: Duplicate counter {tempcounter} found in counter list, please verify the following item: {item}. It could be duplicates in the cache, or same counter in both the cache and CSV")
            else:
                counterlist.append(tempcounter)

            module = item.split("::")[0]
            instance = "_".join(item.split("_fail_")[1].split("_")[:-1])
            port = item.split("_")[-1]
            hardbin = item.split("::n")[1].split("_")[0][:-6]
            softbin = item.split("::n")[1].split("_")[0][-6:-4]
            counter = item.split("::n")[1].split("_")[0][-4:]
            tKey = tuple([module,instance,port])
            if tKey in dTest:  # check if the cache key exists in the csv with different configuration, and if it does remove it
                if hardbin != dTest[tKey]['hardbin'] or softbin != dTest[tKey]['softbin']:
                    utilities.fLog(f"-I- Found old counter definition {hardbin}{softbin}{counter} in cache, removing from cache to regenerate auto counter for test {tKey}")
                    lCache.remove(item)
                    continue
            # v4.0.3 - removing due to inadvertently removing tokens from external modules which we were wanting to track with auto counters to avoid conflicts.
            # if tKey not in dTest:
            #     print("Found unused counter {}{}{} assigned to nonexistant test {}, removing from cache.".format(hardbin,softbin,counter,tKey))
            #     lCache.remove(item)
            #     continue
            if tKey in dCache:
                utilities.fError(f"ERROR: Multiple counters defined for the same module, instance, port combination. Please remove all excess counters from {tKey}")
            dCache[tKey] = {"hardbin":hardbin,
                           "softbin":softbin,
                           "counter":counter}
    # print(dCache)
    # print(counterlist)

    # now we do the bulk of the processing to return a list of valid counters and bins to extinguisher.
    dResult = {}
    for tKey in sorted(dTest.keys()):
        if ":" in dTest[tKey]['counter']:
            # v4.2.0 now adding logic to ensure that previous cached counter is in range
            val1, val2 = dTest[tKey]['counter'].split(':')
            tempmin = int(min(val1, val2))
            tempmax = int(max(val1, val2))
            if tKey in dCache and (not tempmin <= int(dCache[tKey]['counter']) <= tempmax):
                cachecounter = "{}{:0>2}{:0>4}".format(dCache[tKey]['hardbin'],dCache[tKey]['softbin'],dCache[tKey]['counter'])
                lCache.remove("{}::n{}_fail_{}_{}".format(dTest[tKey]['module'],cachecounter,dTest[tKey]['instance'],dTest[tKey]['port']))
                del dCache[tKey]
            # previous counter will take priority over generating a new one.
            if tKey in dCache:
                tempcounter = "{}{:0>2}{:0>4}".format(dCache[tKey]['hardbin'],dCache[tKey]['softbin'],dCache[tKey]['counter'])
            # otherwise generate a new counter
            else:
                utilities.fWarn(f"generating counter for test {dTest[tKey]}")
                tempcounter = fCounterAlgorithm(dTest[tKey]['hardbin'],dTest[tKey]['softbin'],counterlist,tempmin,tempmax)
                tempcounter = "{}{:0>2}{:0>4}".format(dTest[tKey]['hardbin'],dTest[tKey]['softbin'],tempcounter)
                counterlist.append(tempcounter)
                utilities.fLog(f"-I- Generated new counter {tempcounter} for module:instance:port {tKey}")
            fullcounter = "{}::n{}_fail_{}_{}".format(dTest[tKey]['module'],tempcounter,dTest[tKey]['instance'],dTest[tKey]['port'])
            lCache.append(fullcounter)
        else:
            if tKey in dCache:  # this will remove a previous "auto" counter that was converted to a set value
                cachecounter = "{}{:0>2}{:0>4}".format(dCache[tKey]['hardbin'],dCache[tKey]['softbin'],dCache[tKey]['counter'])
                lCache.remove("{}::n{}_fail_{}_{}".format(dTest[tKey]['module'],cachecounter,dTest[tKey]['instance'],dTest[tKey]['port']))
            tempcounter = "{}{:0>2}{:0>4}".format(dTest[tKey]['hardbin'],dTest[tKey]['softbin'],dTest[tKey]['counter'])
            fullcounter = "{}::n{}_fail_{}_{}".format(dTest[tKey]['module'],tempcounter,dTest[tKey]['instance'],dTest[tKey]['port'])
        # print(fullcounter)

        # now we will generate the bin, but we have to take into account the two binning schema.
        if sBinStandard == 'hbsbcntr' or sBinStandard == 'skip' and sCounterStandard == 'hbsbcntr':
            fullbin = "SoftBins.b{}_fail_{}_{}_{}".format(tempcounter,dTest[tKey]['module'],dTest[tKey]['instance'],dTest[tKey]['port'])
        elif sBinStandard == '90hbsbzz':
            tempbin = "90{:0>2}{:0>2}{:0>2}".format(dTest[tKey]['hardbin'],dTest[tKey]['softbin'],tempcounter[-2:])  # I'm re-using tempcounter from counter step
            fullbin = "SoftBins.b{}_fail_{}".format(tempbin,dTest[tKey]['bindesc'])
        elif sBinStandard == '90hbhbsb' or sBinStandard == 'skip' and sCounterStandard == '90hbcntr':
            tempbin = "90{:0>2}{:0>2}{:0>2}".format(dTest[tKey]['hardbin'],dTest[tKey]['hardbin'],dTest[tKey]['softbin'])
            fullbin = "SoftBins.b{}_fail_{}".format(tempbin,dTest[tKey]['bindesc'])
        else:
            utilities.fError(f"ERROR: How did you get in this corner case? {sBinStandard} & {sCounterStandard}")
        # print(fullbin)

        # save the final result into this dictionary, which will get returned to extinguisher.
        dResult[tKey] = {"bin":fullbin, "counter":fullcounter}

    # now we need to print the final list of counters back to the cache, clearing duplicates with set().
    lFinalCounters = sorted(set(lCache))
    f = f"{sSourceDir}/bincounter.cache"
    with open(f, "w") as cache_file:
        cache_file.write("\n".join(lFinalCounters))

    return dResult

def main():
    fGenerateCountersAndBins(os.path.split(os.path.realpath(sys.argv[0]))[0], 'skip')

if __name__ == "__main__":
    main()