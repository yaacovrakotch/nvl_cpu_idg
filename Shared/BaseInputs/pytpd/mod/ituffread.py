"""
There are three data structures in Ituff object:

ituff = Ituff(<what_to_query>)
ituff.lot   = {token:    <value, string or list>}               # Lot level info
ituff.data  = {visualid: {token: <value, string or list>}}      # Unit level info
ituff.tdata = {visualid: {testname: <value, string or list>}    # tname level info

ituff.data   # inputs: Ituff(single=[tokens] and/or multiple=[tokens])
             # tokens uses startswith, thus specify: single=['3_curfbin_']
ituff.tdata  # inputs: Ituff(tsingle=[tokens] or tmultiple=[tokens], tname=string_filter or retname=regex_string)
             # string_filter uses "python's in statement". Partial match.
             # regex_string is a regex string that will apply to tname
ituff.lot    # This is populated always. Only the first ituff file is read.

Usage1: Get simple data, default, no tnames
    itf = Ituff()       # default: single='3_curfbin_ 3_binn_ 3_ttime_'.split()
    itf.read_lot(lot, 'CLASSHOT')
    pprint(itf.data)
    {'81U27F9700992': {'binn': '90535391', 'curfbin': '5391', 'ttime': '7.9834'},
     '81U27F9701006': {'binn': '90535391', 'curfbin': '5391', 'ttime': '7.0723'} }

Usage2: Get tname data
    # Below means, Get all 0_mrslt_ of tname_CheckDieForce_TDAU_CH_CORE
    itf = Ituff(tsingle=['0_mrslt_'], tname='CheckDieForce_TDAU_CH_CORE')
    itf.read_lot(lot, 'CLASSHOT')
    pprint(itf.tdata)
    {'81U27F9700992': {'CheckDieForce_TDAU_CH_CORE': '99.5000'},
     '81U27F9701006': {'CheckDieForce_TDAU_CH_CORE': '99.9000'} }

Usage3: You can specify combination of single= and tsingle=
    itf = Ituff(single=['0_binn_'], tsingle=['0_mrslt_'], tname='CheckDieForce_TDAU_CH_CORE')
    pprint(itf.data)
    pprint(itf.tdata)

Usage4: To get endlot info:
    itf = Ituff(multiple='4_tsattrs_'.split())
    itf.read(file)
    result = list(keys_atlevel(itf.data, 2))     # That is, throw away visualid
"""
from gadget.files import File
from collections import defaultdict
import os
import re

# Strategy for cython:
# 1. Edit only ituffread.py (code in python)
# 2. Create cy_ituffread.pyx from unittest, by uncommenting cython lines or creating cdef lines automatically
# 4. Confirm Performance using J1230270_6261_1A_ALL (19.8M lines)

# 3.6sec - sha1, 19.8M lines
# 17.5sec - wc, 19.8M
# 8sec - open, for line, tot+=len()    # absolute min
# 7.4 sec - File.chomp() only
# 7.0 sec - open() and rstrip
# 5.7 sec - open() and read()
# 9.4 sec - open() and read().split()
# 9.7 sec - open() and read().splitlines()
# 5.8 sec - open() and rstrip() cython

# old code: 357 lines (vs 200 lines)
# itf = Ituffx('/tmp/try1/J1230270_6261_1A_ALL')
# itf.set_data()
# itf.get_unit_data()
# print(f"Proto1c: {sw}, len={len(itf._units)}")
# Proto1c: 62.060 Secs, len=292 vs 10.2 sec


class Ituff:
    """
    Assumptions:
    1. Each file is <ituff>.itf.gz   (Class does not understand .zip)
    2. There is no 2A summary. Retest is in the same filename.
    """

    def __init__(self, single=None, multiple=None,
                 tname=None, retname=None, tsingle=None, tmultiple=None):
        """
        Ituff reader

        :param single: list of tokens for single occurence per part (e.g. '3_curfbin_'). Uses startswith.
        :param multiple: list of tokens for multiple occurence per part (e.g. '4_tsattrs_'). Uses startswith.
        :param tname: tname string filter (simple python: "if filter in line:"). For all tname, set to ''. This will trigger mode=2
        :param retname: tname regex filter. This will trigger mode=2
        :param tsingle: list of tokens for single occurence per tname
        :param tmultiple: list of tokens for multiple occurence per tname
        """
        # check mode2
        if tname is not None or retname:
            assert tsingle or tmultiple, "tsingle=<value> or tmultiple=<value> is required tname filtering"
            assert not (tname and retname), "tname and retname cannot be set at the same time for tname filtering"
            assert not (tsingle and tmultiple), "tsingle and tmultiple cannot be set at the same time. Use tmultiple only"

        if (single, multiple, tname, retname, tsingle, tmultiple) == (None, None, None, None, None, None):
            single = '3_curfbin_ 3_binn_ 3_ttime_'.split()    # default list of tokens to read

        # public data
        self.lot = {}          # {token: <value, string or list>}. Lot level info. Populated in read_lot_info()
        self.data = {}         # {visualid: {token: <value, string or list>}}. Unit level info. Populated in read()
        self.tdata = {}        # {visualid: {testname: <value, string or list>}. Tname level info. Populated in read()
        self.files = []        # list of ituff files read. populated in read()

        # class attributes
        self.single = single
        self.multiple = multiple
        self.tname = tname
        self.retname = retname
        self.tsingle = tsingle
        self.tmultiple = tmultiple

        # Do checks
        assert self.tsingle is None or isinstance(self.tsingle, list), f'tsingle=[{self.tsingle}] must be a list'
        assert self.single is None or isinstance(self.single, list), f'single=[{self.single}] must be a list'
        assert self.tmultiple is None or isinstance(self.tmultiple, list), f'tmultiple=[{self.tmultiple}] must be a list'
        assert self.multiple is None or isinstance(self.multiple, list), f'multiple=[{self.multiple}] must be a list'
        assert self.tname is None or isinstance(self.tname, str), f'tname=[{self.tname}] must be str'
        assert self.retname is None or isinstance(self.retname, str), f'retname=[{self.retname}] must be str'
        self.check_no_tname(self.single, 'single')
        self.check_no_tname(self.multiple, 'multiple')

    def check_no_tname(self, target, which):
        """
        Make sure single and multiple does not have tname.
        Reason: Logic in read() will not work if single or multiple has tname. tname must be in tname=<value>

        :return: None
        """
        to_check = target if target else []
        for item in to_check:
            assert '_tname' not in item, f"Cannot use {which}=[{item}]. Pls use tname=<testname> for this"

    def read_lot(self, path, location=''):
        """
        Read a lot. Given a path to a lot (directory), and location, then read those itf.gz

        :param path: directory path of lot
        :param location: location string, eg. 'CLASSHOT'
        :return: self.data
        """
        assert os.path.isdir(path), f'readlot({path}): is not a valid directory'
        for ff in sorted(os.listdir(path)):
            if location not in ff:    # location is in the filename
                continue
            fpath = f'{path}/{ff}'
            self.read(fpath)

        return self.data

    def read(self, fname):
        """
        Read one ituff file
        High performance ituff python reader

        :param fname: path to fname
        :return: self
        """
        # as of 11/15/21, /tmp/try1/J1230270_6261_1A_ALL
        # py3    - 11.1 sec   (from 10.2)
        # cython -  4.7 sec   (close to light speed: 3.6sec is light speed)

        # register this file
        self.files.append(fname)

        # setups - all variables initialized here and static typing
        fobj = File(fname)
        lot = defaultdict(list)
        line: str = ''
        key: str = ''
        data: dict = {}
        tdata: dict = {}
        token: str = ''
        tname: str = ''
        is_found: bool = False
        elems: tuple = tuple()

        is_single: bool = bool(self.single)
        single_tuple: tuple = tuple(self.single) if is_single else tuple()
        is_multiple: bool = bool(self.multiple)
        multiple_tuple: tuple = tuple(self.multiple) if is_multiple else tuple()
        is_tsingle: bool = bool(self.tsingle)
        tsingle_tuple: tuple = tuple(self.tsingle) if is_tsingle else tuple()
        is_tmultiple: bool = bool(self.tmultiple)
        tmultiple_tuple: tuple = tuple(self.tmultiple) if is_tmultiple else tuple()
        is_testname: bool = bool(self.tname is not None)
        _testname: str = str(self.tname) if is_testname else ''
        is_retname: bool = bool(self.retname)
        _retname = re.compile(self.retname) if is_retname else re.compile('')
        is_mode2: bool = bool(is_testname or is_retname)
        is_lot: bool = not bool(self.lot)                                    # once only per lot
        is_header: bool = is_lot                                             # yes, start as same

        # Start of fast loop
        for line in fobj.fh():
            if line.startswith('2_visualid_'):
                key = line[11:-1]
                data[key] = {}
                tdata[key] = {}

            elif is_lot and is_header:
                if line.startswith('3_prtnm_'):
                    is_header = False
                else:
                    elems = line[2:].partition('_')
                    if elems[1] != '_':
                        continue    # lsep or lbeg
                    token = elems[0]
                    value = line[len(token) + 3: -1]
                    lot[token].append(value)

            elif is_single and line.startswith(single_tuple):
                token = line[2:].partition('_')[0]
                data[key][token] = line[len(token) + 3: -1]

            elif is_multiple and line.startswith(multiple_tuple):
                token = line[2:].partition('_')[0]
                value = line[len(token) + 3: -1]
                if token in data[key]:
                    data[key][token].append(value)
                else:
                    data[key][token] = [value]

            elif is_mode2 and line[1:8] == '_tname_':
                tname = line[8:-1]
                if is_testname:
                    if _testname in tname:
                        is_found = True
                    else:
                        tname = ''
                        is_found = False
                else:
                    if _retname.search(tname):
                        is_found = True
                    else:
                        tname = ''
                        is_found = False

            elif is_found and is_tsingle and line.startswith(tsingle_tuple):
                token = line[2:].partition('_')[0]
                value = line[len(token) + 3: -1]
                tdata[key][tname] = value

            elif is_found and is_tmultiple and line.startswith(tmultiple_tuple):
                token = line[2:].partition('_')[0]
                value = line[len(token) + 3: -1]
                if tname in tdata[key]:
                    tdata[key][tname].append(value)
                else:
                    tdata[key][tname] = [value]

        fobj.close()

        # update to final storage
        self.data.update(data)
        self.tdata.update(tdata)

        # convert to string for single element and keep as list for multiple
        if is_lot:
            self.lot = {key: y if len(y) > 1 else y[0] for key, y in lot.items()}

        return self
