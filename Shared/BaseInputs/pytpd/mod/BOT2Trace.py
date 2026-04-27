#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Script author/contact: mseguras

Modifies and moves BOT ituff to make it visible to TRACE.
The lot name in TRACE is something like: MB<timestamp><w|wo>PUP

BOT2Trace.py <MBOT ituff path>

Usage: Default: Modifies and moves BOT ituff to make it visible to TRACE
        When <MBOT ituff path> is populated

    Usage:   BOT2Trace.py <path>
    example: BOT2Trace.py I:/<path>
"""
from datetime import datetime
import sys
import os
import re
from zipfile import ZipFile


def get_dest(Trace_ituff_folder=r"I:/tpvalidation/engtools/tptools/mtl/cmtdata_prod/"):    # GLOBALS
    """Return the path"""
    sub_path = 'trace/Ituffs/'
    targ = f'{Trace_ituff_folder}{sub_path}'
    if os.path.exists(targ):    # default - backwards compatible
        print(f"-i- BOT2Trace: {targ}")
        return targ

    print(f"-i- BOT2Trace: {Trace_ituff_folder}")
    return Trace_ituff_folder


def traceIT(ituff_path):
    """
    Main entry point
    :param ituff_path: str: valid path
    :return: NA
    """
    if not os.path.exists(get_dest()):

        print(f"{get_dest()} does not exist. Skipping ituff upload to trace")
        return []    # Do nothing

    try:
        check_ituff(ituff_path)
        new_ituffs_per_unit = create_new_ituffs(ituff_path)
        write_zip_files(new_ituffs_per_unit)
    except Exception as e:
        print(f"-i- ERROR during BOT2Trace: {e}")

    return list(new_ituffs_per_unit)


def write_zip_files(new_ituffs_per_unit):
    for filename in new_ituffs_per_unit.keys():
        # Create the file
        filepath = os.path.join(get_dest(), filename)
        create_file(filepath, new_ituffs_per_unit[filename])

        # zip the file
        zipfilepath = filepath + ".zip"
        with ZipFile(zipfilepath, 'w') as zip:
            zip.write(filepath, os.path.basename(filepath))

        # Delete old file
        os.unlink(filepath)


def create_new_ituffs(ituff_path):
    """
    :param ituff_path: str: path to valid ituff file
    :return: arr of arr strings. Each unit has its own ituff
    """
    # Read
    ituff_contents = read_file(ituff_path)

    # Get lot run parameters
    lchars = get_lot_run_chars(ituff_contents)

    # New ituffs - one per unit
    ituffs_per_unit = calc_ituff_per_unit(ituff_contents)

    # Modify each ituff
    new_ituffs_per_unit = modify_each_unit_ituff(ituffs_per_unit, lchars, ituff_path)

    return new_ituffs_per_unit


def modify_each_unit_ituff(ituffs_per_unit, lchars, ituff_path):
    """
    Changes the lot # inside the ituff
    :param ituffs_per_unit: list of ituffs (arr of strs)
    :param lchars: tuple
        lotn: str
        tpl_path: str
        summ: str
        locn: str
        subflow: str
        owner: str
        viid: str
    :return: dict of ituff {itufffilename} = arr of strings
    """

    lotn, tpl_path, summ, locn, subflow, owner, viid = lchars

    new_ituffs_per_unit = {}
    for ituff in ituffs_per_unit:
        newlotnum = get_new_lot_num(owner, ituff, ituff_path)
        print(f"Lot number (as it will appear in TRACE): '{newlotnum}'")
        nituff = change_ituff_fields(newlotnum, viid, ituff)
        filename = newlotnum + "_" + locn + '_' + summ + "_ALL"
        new_ituffs_per_unit[filename] = nituff

    return new_ituffs_per_unit


def change_ituff_fields(newlotnum, viid, ituff):
    nituff = ituff.copy()

    lot_flag = False
    prtn_flag = False
    viid_flag = False
    for i in range(len(nituff)):
        if re.search(r"^6_lotid_", nituff[i], re.IGNORECASE):
            nituff[i] = f"6_lotid_{newlotnum}"
            lot_flag = True
        elif re.search(r"^3_prtnm_", nituff[i], re.IGNORECASE):
            nituff[i] = f"3_prtnm_1"
            prtn_flag = True
        elif re.search(r"^2_visualid_", nituff[i], re.IGNORECASE):
            nituff[i] = f"2_visualid_{viid}"
            viid_flag = True
        if lot_flag and prtn_flag and viid_flag:
            break

    return nituff


def get_new_lot_num(owner, ituff, ituff_path):
    """
    Aligns the lot number to the timestamp of the robot.
    :param owner: str
    :param ituff: arr of str
    :param ituff_path: str
    :return:
    """

    newlotnum = "MB"
    if owner != "NA":
        newlotnum += owner

    # Timestamp to match BOT run 'I:/..../2023-04-17/ituff_TestUnitLog_2023-04-17-16-06-29.txt'
    ts = ""
    if re.search(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}.txt$", ituff_path):
        ts = re.sub(r"\.txt", "", os.path.basename(ituff_path).split('_')[-1])
        ts = re.sub(r"-", "", ts, 1000)
    else:
        # ts = datetime.now().strftime("%Y-%m-%d-%I-%M-%S")
        ts = datetime.now().strftime("%Y%m%d%I%M%S")
    # newlotnum += ts + "-"
    newlotnum += ts

    if is_PUP_enabled(ituff):
        newlotnum += "wPUP"
    else:
        newlotnum += "woPUP"

    if re.search(r"_CLASSHOT_1_", ituff_path):
        newlotnum += "r1"

    return newlotnum


def is_PUP_enabled(ituff):
    flag = False
    for i in range(len(ituff)):
        line = ituff[i]
        if line == "2_tname_pup_configsets":
            flag = True
            break
    return flag


def calc_ituff_per_unit(ituff_contents):
    """
    Splits the ituff file into mulitple ituff files per unit
    :param ituff_contents: arr of str
    :return: arr of arr (strs)
    """
    ituffs_per_unit = []
    header, units_data = split_header_units_ituff(ituff_contents)
    if len(units_data) == 1:  # Single unit no need to split
        ituffs_per_unit.append(ituff_contents)
    else:
        for unit_data in units_data:
            unit_ituff = header.copy()
            unit_ituff.extend(unit_data)
            ituffs_per_unit.append(unit_ituff)
    return ituffs_per_unit


def split_header_units_ituff(ituff_contents):
    """
    :param ituff_contents: arr of strs
    :return: tuple
        header: arr of strs
        units_data = arr of arr
            inner arr: strings (just the ituff data for the actual unit)
    """
    header_idx = 0
    unit_start_idxs = []
    unit_end_idxs = []
    for i in range(len(ituff_contents)):
        line = ituff_contents[i]
        if re.search("^3_lbeg$", line, re.IGNORECASE):
            header_idx = i

        elif re.search("^3_lsep$", line, re.IGNORECASE):
            unit_start_idxs.append(i)
            if len(unit_end_idxs) == 0:
                unit_end_idxs.append(i - 1)

    header = ituff_contents[:header_idx + 1]
    units_data = []
    for i in range(len(unit_start_idxs)):
        si = unit_start_idxs[i]

        if i + 1 < len(unit_start_idxs):
            ei = unit_start_idxs[i + 1]
        else:
            ei = len(ituff_contents)

        unit_data = ituff_contents[si:ei]
        units_data.append(unit_data)

    return header, units_data


def get_lot_run_chars(ituff_contents):
    """
    Parses part of the ituff to get some key paramers
    :param ituff_contents: arr of strs
    :return: tuple
    """
    lotn = "NA"
    tpl_path = "NA"
    summ = "NA"
    locn = "NA"
    subflow = "NA"
    owner = "NA"
    viid = "NA"

    for l in ituff_contents:
        if re.search("^6_lotid_", l, re.IGNORECASE):
            lotn = "".join(l.split('_')[2:])
        elif re.search("^4_tsattrs_tplpath,", l, re.IGNORECASE):
            tpl_path = "".join(l.split(',')[1:])
        elif re.search("^4_smrynam_", l, re.IGNORECASE):
            summ = "".join(l.split('_')[2:])
        elif re.search("^5_lcode_", l, re.IGNORECASE):
            locn = "".join(l.split('_')[2:])
        elif re.search("^4_tsattrs_CURRENT_PROCESS_TYPE,", l, re.IGNORECASE):
            subflow = "".join(l.split(',')[1:])
        elif re.search("^2_visualid_", l, re.IGNORECASE):
            cvid = "".join(l.split('_')[2])
            if cvid != "0000":
                viid = cvid
        if lotn != "NA" and tpl_path != "NA" and summ != "NA" and locn != "NA" and subflow != "NA" and viid != "NA":
            break

    if re.search(r"users.(.+?)(\\|/)", tpl_path, re.IGNORECASE):
        owner = re.search(r"users.(.+?)(\\|/)", tpl_path, re.IGNORECASE).group(1)

    return lotn, tpl_path, summ, locn, subflow, owner, viid


def check_ituff(ituff_path):
    """
    Basic checks.. might be extended later
    :param ituff_path:
    :return:
    """
    if not os.path.exists(ituff_path):
        raise Exception(f"No ituff found at '{ituff_path}'")

    ituff_contents = read_file(ituff_path)
    if len(ituff_contents) == 0:
        raise Exception(f"Ituff file '{ituff_path}' is empty")


def read_file(filepath):
    """
    Simple file reading
    :param filepath:
    :return:
    """
    rcontents = []
    try:
        with open(filepath, "r") as fh:
            rcontents = fh.read().splitlines()
    except Exception as e:
        raise Exception(f"Unable to read file '{filepath}' due to '{e}")

    return rcontents


def create_file(filepath, contents):
    """
    :param: filepath: str
    :param: contents filepath: arr of strs
    :return:
    """
    try:
        print("Writing: ", filepath)
        with open(filepath, 'w') as f:
            for x in contents:
                f.write(x)
                f.write("\n")
    except Exception as e:
        raise Exception(f"Unable to write file '{filepath}' due to '{e}'")


if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv) != 2:
        raise Exception(f"Incorrect input args.\nUsage: BOT2Trace.py I:/<path>\nGot: '{len(sys.argv)}' args instead:\
                            '{sys.argv}'")
    traceIT(sys.argv[1])
