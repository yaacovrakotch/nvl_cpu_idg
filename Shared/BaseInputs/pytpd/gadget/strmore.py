#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Helper and Additional (fast) string functions not provided in standard library.

String:
  str_findn(string, sub, nth_occurence)
  str_isword(string, chr_replace=None)
  str_startword(string, sub)
  str_replace(string, start, replace_length, new)
  str_between(input, start, end)
  str_index_expander(string)
  str_repeat(length, char=' ')
  compare_print(string1, string2)     # print diffs
  nsplit(string, maxplit)
  multi_replace(string, sequence, replacement)
  wordgen(length)                     # iterator: returns combination of chars for regex
  md5(string)                         # returns md5 hex string
  sha1(string)                        # returns sha1 hex string
  essm_hash_name(string_pages)        # returns the essm hash name
  indent(n, string|sequence)          # indents string or sequence by n characters
  split_spacetab(text)                # returns a list with space and tab reduced to single space
  separate_chars(n, string)           # returns a list, n characters splitted
  comma_key_value(somedict)           # returns a comma delimited string, key=value
  nospace_comment(text_or_arr)        # iterator, yields lines which are not empty or starts with comment char
  subdivide(arr, maxlen)              # iterator, returns chunks of maxlen
  line_word_wrap(arr, maxlen)         # iterator, returns lines with maxlen, and don't break in word boundary
  is_ascii(string)                    # returns True if string is pure ascii / printable
  to_ascii(string)                    # returns ascii only (ie, strips non-ascii chars)
  dict_to_args(dict)                  # returns 'key=value, <etc>' string, given dictionary
  to_list(string|list|tuple)          # returns list|tuple, converts string to a tuple of one element
  join_seq(seq)                       # returns a string joined by '\n'.join(seq) with a newline at end

Time Related:
  curtime()
  age_string(age):                    # Returns 'n secs|mins|hours|days|years' string based on the given age seconds
  utc2local(utc_date_string)          # Returns datestring given UTC

Regex related:
  regex(regx, line, flags=0, pre=None, [name])
  regex.group(grp, [name])
  robj = regex.compile(regx)
  regex.key_compile_regex(dd, regex_keys)

  regex.join_make_regex(seq, isexactmatch=False)      # return a joined regex string
  regex.to_non_capture_group(rx)                      # convert a capturing group to non-capture group

Normal regex usage:
  1. Search, basic:
       if regex('<regex>', line):
  2. Search with pre-string:
       if regex('<regex>', line, pre='<presearch>'):
  3. Search, fully optimized:
       reobj = regex.compile('<regex>')
       for line in fh:
          if reobj.search(line):
  4. Search, if found, get group
       if regex('<regex>', line):
          gr1 = regex.group(1)
          gr2 = regex.group(2)
  5. Search and get group directly (will raise error if not found)
       gr1 = regex('<regex>', line).group(1)
       gr2 = regex.group(2)
  6. Search and replace
       resline = regex.compile('<regex>').sub('<newstring\1 and \2>', line)

Misc/Memory Related:
     printWithUnits(memory)     # returns memory with units i.e. B, KB, MB, GB
     PinHeader()                # class, returns pinheader
"""
import array
import re
import sys
from itertools import zip_longest
from time import localtime, strftime, time, timezone, altzone, mktime
from datetime import datetime
from .gizmo import isany
from .helperclass import EnumType, EnumElement
from .dictmore import NamedSeq
from collections import defaultdict, deque
import os
import hashlib
from functools import reduce


def utc2local(utc_date_string, is_secs=False, tzoffset=0):
    """
    Convert UTC string to datetime object (local)
    :param utc_date_string: string in this format "2023-05-13T15:40:53Z"
    :param tzoffset: seconds, timezone offset
    :return: datetime object or secs
    """
    # convert to datetime
    utc_date = datetime.strptime(utc_date_string, "%Y-%m-%dT%H:%M:%SZ")

    # Get the offset vs UTC
    secs = mktime(utc_date.timetuple())
    local_tz_offset_secs = timezone if (localtime(secs).tm_isdst == 0) else altzone

    # final time
    timestamp = mktime(utc_date.timetuple()) - local_tz_offset_secs
    timestamp += (tzoffset * 3600)
    if is_secs:
        return timestamp
    else:
        return datetime.fromtimestamp(timestamp)


def to_seconds(timestring):
    """
    Convert timestring (hh:mm:ss) to seconds

    :param timestring: string in hh:mm:ss format
    :return: seconds: float or 0 if invalid input
    """
    elem = timestring.split(':')
    if not len(elem) == 3:
        return 0
    return int(elem[0]) * 3600 + int(elem[1]) * 60 + float(elem[2])


def uniq_sha():
    """Returns a unique random sha"""
    import secrets
    txt = f'{secrets.randbits(256)} {time()} {os.getpid()}'
    return sha1(txt)


def putquotes(arr):
    """
    Iterator to put quotes if quotes are needed: space, ' and '
    If both ' and ' are in the string, then do nothing
    Usage:
       print ' '.join(putquotes(sys.argv[1:]))
    """
    for w in arr:
        if isany(''' ;\'"''', w):
            if "'" in w and '"' in w:
                yield w       # do nothing
            elif "'" in w:
                yield '"' + w + '"'
            else:
                yield "'" + w + "'"   # single quote for defaults
        else:
            yield w    # do nothing


def str_findn(string, sub, nth_occurence):    # unittested
    """
    Returns the location of sub in string for nth_occurence.
    Returns -1 if not found

    Usage:
    >>> print str_findn('abcabcabc','abc',2)
    3
    """
    loc = -1
    for i in range(nth_occurence):
        loc = string.find(sub, loc + 1)
        if loc == -1:
            return -1
    return loc


def str_isword(string, chr_replace=None):      # unittested
    """
    Similar to s.isalnum() but includes '_' character. This will match regex \\w.
    Additional characters to consider as 'word', specify in chr_replace. One character at a time

    Usage:
    >>> print str_isword('wrd_abc123_')
    True
    >>> print str_isword('a.b.c_d','.')
    True
    >>> print str_isword('a.b.c-a_d','.-')
    True
    """
    newstr = string
    if chr_replace is not None:
        newstr = reduce(lambda s, arg: s.replace(arg, 'a'), chr_replace, newstr)
#        for chr in chr_replace:
#            newstr = newstr.replace(chr_replace,"a")
    return newstr.replace("_", "a").isalnum()


def str_startword(string, sub):    # unittested
    r'''
    Returns location of sub in string (sub must start as a word).
    Similar to if($string=~/\b$sub/).
    returns -1 if not found

    Usage:
    >>> print str_startword('the quick brown', 'quick')
    4
    '''
    loc = string.find(sub)
    if loc <= 0:
        return loc
    if str_isword(string[loc - 1:loc]):
        return -1
    return loc


def str_replace(string, start, replace_length, new):     # unittested
    """
    A string function to replace [new] string in offset=start and replace_length
    Returns the replaced string.
    This is equivalent to perl: substr(var, start, len) = new

    Usage:
    >>> print str_replace('abcdef', 2, 1, 'Z')
    abZdef
    >>> print str_replace('abcdef', 3, 2, 'Y')
    abcYf
    >>> # Use in conjuction with string.find():
    >>> var = 'abcdefg'
    >>> print str_replace(var, var.find('cde'), 3, 'CDE')
    abCDEfg
    """
    # Performance (200000 iteration):  6.5x faster
    #   regex:       1.3 sec
    #   str_replace: 0.197 sec
    # Code:
    #   line = "NOP    { all_sbp_pin=1110101010 }"
    #   re1 = re.compile('(all_sbp_pin=...)(.)')
    #   for i in xrange(200000): nl = re1.sub(r'\1C',line)
    #   for i in xrange(200000): nl = str_replace(line, line.find('all_sbp_pin=')+15,1,'C')

    if(start == -1):
        return string
    if(start > len(string)):
        raise Exception("str_replace('" + string + "'," + str(start) + ") out of bounds")
    return string[:start] + new + string[start + replace_length:]


def str_between(input, start, end):
    """
    Fast (non-regex) string routine to return the string
    between the start and end character.
    Will return None if start and end is not found.
    Will only return the first occurrence.

    Usage:
    >>> print str_betwen('pat 'abc' #', ''', ''')
    abc
    """
    spos = input.find(start)
    if spos == -1:
        return None

    marker = spos + len(start)
    epos = input.find(end, marker)
    if epos == -1:
        return None
    return input[marker:epos]


def str_index_expander(string, msb2lsb=False):
    """
    Expand a shorthand formatted string of integers into a list of integers.

    Usage:
    >>> str_index_expander('3-0,5,8-10')
    [10,9,8,5,3,2,1,0]
    >>> str_index_expander('aa-ac')
    [100,101,102]
    """
    retlist = []
    lista = string.split(",")
    for entries in lista:
        if entries.find("-") >= 1:  # Can't have - in position 0.
            listb = []
            for num in entries.strip().split("-"):
                if num.isdigit():
                    listb.append(int(num))
                else:
                    listb.append(int(Base776.decode(num)))
            listb.sort()
            for entry in range(listb[0], listb[1] + 1, 1):
                retlist.append(entry)
        else:
            retlist.append(int(entries))
    retlist = sorted(set(retlist))
    if msb2lsb:
        retlist.sort(reverse=True)
    return retlist


def str_repeat(length, char=" "):
    """
    Returns a string of repeating <char> (default is ' '), of given length

    >>> print '%r' % str_repeat(5)
    '     '
    >>> str_repeat(10,'0')
    00000000000
    """
    if len(char) != 1:
        raise ValueError("str_repeat() can only take single character")

    return ''.zfill(length).replace('0', char)     # this is faster than ''.join(repeat(char, length))


def cjoin(seq, sep=', '):
    """
    Joins seq separated by sep.
    Used mainly inside of f'' strings.
    """
    return sep.join(str(x) for x in seq)


def space2comma(line: str, ncolumns: int, _robj=re.compile(r'\s+')) -> str:
    """
    Replace line with spaces to commas

    :param line: input string
    :param ncolumns: expected columns if line is empty
    :param _robj: compiled regex object
    :return: string comma delimited
    """
    result = _robj.sub(',', line.strip())
    cols = len(result.split(','))
    return '%s%s' % (result, ',' * (ncolumns - cols))


def sample_list(arr, n) -> str:
    """
    Returns comma separated sample list of n elements

    :param arr: input array
    :param n: number of elements
    :return: str, comma separated
    """
    if len(arr) > n:
        return '%s,...' % ','.join(arr[:n])
    return ','.join(arr)


def compare_print(string1, string2):
    """
    Displays string1 and string2 and shows characters which are different (via $ character)

    Usage:
    >>> compare_print('ABCDE','ABDDF')
    ABCDE
    ABDDF
      $ $
    """
    print(string1)
    print(string2)
    print(''.join([" " if x[0] == x[1] else "$" for x in zip_longest(string1, string2)]))


def nsplit(string, maxsplit):
    """
    Splits the string (using space) using maxsplit.
    Consecutive spaces will be reduced to single space for entire string.
    The built-in split() does not take maxsplit without specifying sepcharacter,' '.
    If sepcharacter,' ' is specified, then the split does not take consecutive spaces
    as one separator.

    Usage:
    >>> line='   a   b    c'
    >>> (x,y) = nsplit(line,2)
    >>> print 'x=%r y=%r' % (x,y)
    x='a' y='b c'
    """
    ss = string.split()
    res = ss[0:maxsplit - 1]                      # The elements minus 1
    res.append(' '.join(ss[maxsplit - 1:]))     # The last element
    return res


def multi_replace(string, seq, replacement):
    """
    Replace all occurrence of sequence with replacement.

    Usage:
    >>> print multi_replace('ab:d[e]f',':[]',' ')
    ab d e f
    >>> print '%r' % multi_replace('the quick of brown', ['the','of'], '')
    ' quick brown'
    """
    return reduce(lambda x, y: x.replace(y, replacement), seq, string)


def wordgen(length, chars="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"):
    r"""
    Generator: Generates 0-9A-Za-z_ combination, given length.
    For large regex length, then use: chars='0Aa_' this represents the usual letters for \w

    Usage:
    >>> print ''.join(wordgen(1))
    0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz
    >>> print ' '.join(wordgen(2))
    00 01 ... zy zz
    """
    if length == 1:
        for letter in chars:
            yield letter
    else:
        for res in wordgen(length - 1):
            for letter in chars:
                yield res + letter


def md5(obj):
    """
    Returns the md5 checksum string

    Usage:
    >>> print md5('Somestring')
    bf86eb1ceab2ad6540c873b18e9631a9
    """
    if not isinstance(obj, str):
        obj = repr(obj)          # convert to string representation
    if sys.version > '3':        # pragma: no cover
        obj = obj.encode('utf-8')
    return hashlib.md5(obj).hexdigest()    # maybe add [obj.encode('utf-8')] for python3 compatibility?


def sha1(obj):
    """
    Returns the sha1 checksum string

    Usage:
    >>> print sha1('Somestring')
    ac7e4265446aa47cd4c89b50ecba266831af9fac
    """
    if not isinstance(obj, (str, bytes)):
        obj = repr(obj)          # convert to string representation

    if isinstance(obj, str):
        obj = obj.encode()   # convert to bytes
    return hashlib.sha1(obj).hexdigest()    # maybe add [obj.encode('utf-8')] for python3 compatibility?

# Validation:
# (a) 10M HSW pattern names, [:11] is already unique
# (b) 1 to 1000000000:       [:15] is unique, using str(<number>)

# sha1 vs md5: Summary: almost same! They just differ in one char diff.
# for ii in xrange(100000): key = '%f' % time.time(); uniq = sha1(key)[:12]
# xrange(100000):   sha1: [:8] is ok
#                   md5:  [:9] is ok
# xrange(1000000):  sha1: [:11] is ok
#                   md5   [:10] is ok
# xrange(20000000): sha1: [:12] is ok
#                   md5:  [:12] is ok

# for ii in xrange(200000): key = '%s' % ii; uniq = sha1(key)[:12]
# xrange(200000):  md5:  [:9] is ok
#                  sha1: [:9] is ok
# xrange(1000000): md5:  [:11] is ok
#                  sha1: [:10] is ok
# xrange(5000000): md5:  [:11] is ok
#                  sha1: [:12] is ok


def essm_hash_name(string_pages):
    """
    Returns the essm hash name
    """
    return "E_" + sha1(string_pages)[:16]
    # Why 16? 16 hex digits is unique enough for essm pages.
    # 2^(16*4) =  18,446,744,073,709,551,616 combinations


def uniq_int(obj):
    """
    Returns a unique 60-bit integer given an object
    Usage:
    >>> print uniq_int('Somestring')
    776840314018507335
    """
    if not isinstance(obj, str):
        obj = repr(obj)          # convert to string representation
    if sys.version > '3':        # pragma: no cover
        obj = obj.encode('utf-8')
    sha_60bit = hashlib.sha1(obj).hexdigest()[:15]
    assert len(sha_60bit) == 15    # confirm it is 15 hex digits
    return int(sha_60bit, 16)


def strvalue(value):
    """
    Returns str(value) if value is not None
    :param value: int or string or None
    :return: str(value) or None
    """
    if value is None:
        return value
    else:
        return str(value)


def indent(n, str_seq):
    r'''
    Returns a long string, indented lines by n characters
    str_seq can be string (split by EOL) or sequence

    Usage:
    >>> print indent(3, ["aa","bb","cc"])
       aa
       bb
       cc
    >>> print indent(3, "aa\nbb\n")
       aa
       bb

    '''
    if not str_seq:
        return ""   # empty
    if isinstance(str_seq, str):
        str_seq = str_seq.split('\n')
    if n == 0:
        ind = ""
    elif n == 1:
        ind = " "
    else:
        ind = ("%" + str(n) + "s") % " "      # generate spaces of n length
    return ind + (("\n" + ind).join(str(x) for x in str_seq))


def split_spacetab(text) -> list:
    """
    Returns a list of newline separated, with space and tab reduced to single space.
    Used with unittests that involve output compares.
    """
    res = []
    for line in text.split('\n'):
        res.append(re.sub(r'\s+', ' ', line))
    return res


def separate_chars(n, string):
    """
    returns a list, n characters splitted
    Example:
    >>> separate_chars(2, '08080402')
    ['08','08','04','02']
    """
    return [string[start:start + n] for start in range(0, len(string), n)]


def comma_key_value(somedict):
    """returns a comma delimited string, key=value"""
    return ', '.join("%s=%r" % (k, somedict[k]) for k in sorted(somedict))


def nospace_comment(inp, commentchar='#'):
    """
    inp can be string or array
    iterator, yields lines which are not empty or starts with comment char

    Example:
    self.assertRegexpEachList(list(nospace_comment(pxr)), [<expect_list>])
    """
    if isinstance(inp, str):
        inp = inp.split('\n')

    for line in inp:
        stripped = line.strip()
        if stripped.startswith(commentchar):
            continue
        if len(stripped) == 0:
            continue
        yield line


def subdivide(arr, maxlen, limit=1000000):
    """subdivide an array by maxlen"""
    for ii in range(limit):
        yield arr[ii * maxlen:ii * maxlen + maxlen]
        if len(arr) <= ii * maxlen + maxlen:
            break


def line_word_wrap(line, maxlen, limit=1000000):
    """iterator, returns lines with maxlen, and don't break in word boundary"""
    start = 0
    for _ in range(limit):
        target = start + maxlen
        if target >= len(line):
            break
        while line[target].isalnum() and line[target - 1].isalnum():
            target -= 1
            if target == start:
                target = maxlen
                break
        if len(line[start:target].strip()) > 0:    # only lines with value
            yield line[start:target].strip()
        start = target

    yield line[start:].strip()   # last one

# --- time related ---


def wwno(secs=None, year=False):
    """
    Return intel workweek integer (ww or yyyyww)
    https://phonebook.intel.com/cgi-bin/phonecal?mon=Jan&year=2027&add=+%3E+&mode=year&who=UNITED+STATES

    :param secs: Optional secs
    :param year: Set to True to add year
    :return: integer workweek (ww or yyyyww)
    """
    if secs is None:
        secs = time()
    dateobj = datetime.fromtimestamp(secs)
    if dateobj.year <= 2023 or dateobj.year >= 2027:
        ww = dateobj.isocalendar()[1] + 1
    else:
        ww = dateobj.isocalendar()[1]

    yearinc = 0
    if ww == 53:
        ww = 1
        yearinc = 1

    if year:
        return ((dateobj.year + yearinc) * 100) + ww
    else:
        return ww


def workweek(secs=None, date=None):    # ww routine to return YYYY.wwWW.D
    """
    Return the ww string given secs or date. If neither secs or date is given, then current time

    :param secs: epoch seconds
    :param date: string date in format 'YYYY-MM-DD'
    :return: string: YYYY.wwWW.D
    """
    # Get input
    if secs:
        _secs = secs
    elif date:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        _secs = int(date_obj.timestamp())
    else:
        _secs = time()   # current time

    # Process the ww
    dateobj = datetime.fromtimestamp(_secs)
    year, ww_int, day = dateobj.isocalendar()
    if year == 2022:
        ww_int += 1
    if day == 7:
        day = 0
        ww_int += 1
    ww = str(ww_int).zfill(2)

    return f'{year}.ww{ww}.{day}'


def curtime(seconds=None, number=False, iso=False, dateonly=False, human=False):
    """
    :return: current time (or from seconds if specified) in the format:
    default:       2013-12-18_15:15:01
    number=True:   20140830_100333_134628
    iso=True:      2013-12-18T09:20:33.095844
    dateonly=True: 2013-12-18
    human=True:    2013-12-18 15:15:01

    :param seconds: Optional input, in seconds, for time to use. If not set, use current time
    :param number: if True, set format to 20140830_100333_134628
    :param iso: if True, set format to 2013-12-18T09:20:33.095844
    :param dateonly: if True, return date only in format 2013-12-18
    :param human: if True, return '2013-12-18 15:15:01'
    """
    if seconds:
        dt = datetime.fromtimestamp(seconds)
    else:
        dt = datetime.now()

    # Display options
    result = None
    if number:
        assert not result, 'Invalid usage on curtime(): can only set one display option'
        result = dt.strftime("%Y%m%d_%H%M%S_%f")
    if iso:
        assert not result, 'Invalid usage on curtime(): can only set one display option'
        result = dt.isoformat()
    if dateonly:
        assert not result, 'Invalid usage on curtime(): can only set one display option'
        result = dt.strftime("%Y-%m-%d")
    if human:
        assert not result, 'Invalid usage on curtime(): can only set one display option'
        result = dt.strftime("%Y-%m-%d %H:%M:%S")
    if not result:
        result = dt.strftime("%Y-%m-%d_%H:%M:%S")
    return result


def day_code(seconds=None):
    """Returns a unique 5-char day-code, for use with various skips"""
    day = curtime(seconds=seconds)[:10]
    return sha1(day)[:5]


def is_ascii(string, _robj=re.compile(r'[^\x20-\x7F\s]')):     # is_printable
    r"""
    Return True if string is pure ascii characters / printable chars

    Common usage:

        if not is_ascii(input):
            raise ErrorUser("The input string %r contain special characters." % input,
                            "Pls replace (aka retype) the special character in your xterm. "
                            r"The special character has \x something. "
                            "This usually happens when you cut&paste command from windows.")
    """
    return (not _robj.search(string))


def to_ascii(string, _robj=re.compile(r'[^\x20-\x7F\s]')):
    """
    returns ascii only (ie, strips non-ascii chars).
    This routine will not remove newline char
    """
    return _robj.sub(' ', string)


def to_alpha_numeric(str):
    """
    Returns only alpha numeric characters in the input string
    e.g. ab#c$12$4 -> abc124
    :param string:
    :return:
    """
    return ''.join(c for c in str if c.isalnum())


def age_string(age):
    """
    Returns 'n secs|mins|hours|days|years' string based on the given age seconds
    """
    if age < 60:
        return "%d secs" % (age)
    if age < 3600:
        return "%d mins" % (age / 60)
    if age < 3600 * 24:
        return "%d hours" % (age / 3600)
    if age < (3600 * 24 * 30):
        return "%d days" % (age / (3600 * 24))
    if age < (3600 * 24 * 365):
        return "%d months" % (age / (3600 * 24 * 30))
    else:
        return "%d years" % (age / (3600 * 24 * 365))


def dict2sorted_string(dictionary, sort_by_keys=True):
    """
    Return a string representation of the passed in dict sorted by either keys or values
    :param dictionary: dict to sort and print
    :type dictionary: dict
    :param sort_by_keys: True to sort by keys, False to sort by value
    :type sort_by_keys: bool
    :return: string of the sorted dict ready for printing.
    :rtype: str
    """
    if not isinstance(dictionary, dict):
        raise TypeError("Input is not a dict: (%s)" % type(dictionary))

    result = '{'
    first = True
    for (key, val) in sorted(list(dictionary.items()), key=lambda x: x[0] if sort_by_keys else x[1]):
        if not first:
            result += ", "
        first = False
        result += "'{key}': {val}".format(key=key, val=val)

    result += '}'
    return result


def zlib_compress(txt):
    """
    :param txt: string (either unicode or bytes)
    :return: gzipped bytes
    """
    import zlib

    if isinstance(txt, bytes):
        return zlib.compress(txt)

    elif isinstance(txt, str):
        return zlib.compress(txt.encode('utf-8'))

    else:
        raise ValueError('Can only compress str or bytes, not a %s' % type(txt))


def zlib_uncompress(txt):
    """
    :param txt: gzipped bytes
    :return: unzipped string (unicode)
    """
    import zlib
    return zlib.decompress(txt)


def dict_to_args(dd):
    """
    returns 'key=value, <etc>' string for pretty printouts

    :param dd: dict input
    :return: string
    """
    return ', '.join('%s=%r' % (k, dd[k]) for k in sorted(dd))


def soc_sha(fname, debug=False):
    """
    Determine the 12-char sha of cleaned up .soc files
    Clean up is:
    1. removal of empty lines
    2. removal of leading and trailng spaces
    3. replacement of 2 or more contiguous spaces to 1
    Why 12-char? 40-char is too long. 12-char is good enough for unique soc file handling.
    This 12-char is used as a subdirectory name in ci_plist.
    """
    robj = re.compile(r'\s\s+')
    result = []
    with open(fname) as fh:
        for line in fh:
            line = line.strip()    # remove both leading and trailing space
            if line:               # only non-empty lines
                line = robj.sub(' ', line)  # remove extra spaces
                result.append(line)

    finaltext = '\n'.join(result)
    if debug:
        return finaltext
    return sha1(finaltext)[:12]


def to_char_array(str):
    """
    For Python3 there is no longer array of chars supported, so make an array of unicode of each char instead
    :param str:
    :return:
    """
    return array.array('u', list(str))


def to_py3_oct(str):
    """
    Convert python 3 octal string to python2 format
    e.g. 0550 -> 0o550, used for tests written in python 2 that are being ported to py3
    :param str:
    :return:
    """
    assert str[0] == '0', 'Input %r is expecting octal, thus must start with 0' % str

    return '0o%s' % str[1:]


def to_str(str_or_bytes):
    """
    Convert str|bytes to str

    :param str_or_bytes: either str or bytes
    :return: str
    """
    if isinstance(str_or_bytes, bytes):
        return str_or_bytes.decode(errors='ignore')
    else:
        return str_or_bytes


def to_bytes(str_or_bytes):
    """
    Convert str|bytes to str

    :param str_or_bytes: either str or bytes
    :return: str
    """
    if isinstance(str_or_bytes, str):
        return str_or_bytes.encode()
    else:
        return str_or_bytes


def to_bytes_list(list_str):
    """
    Convert a list of strings into a list of bytes (for python 3 porting)
    :param list_str:
    :return:
    """
    bytes_list = []
    for str in list_str:
        bytes_list.append(to_bytes(str))

    return bytes_list


def to_list_of_bytes(bytes_str):
    """
    Convert a string or bytes string into a list of each byte character (for py3/state equations)
    e.g. to_list_of_bytes(b'ABC1') -> [b'A', b'B', b'C', b'1']
    Two options were considered:
    1) start with byte string and encode each character to bytes
    2) ecode byte string to string and encode each string character to bytes (this one was faster)
    Method 1/results
    >>> timeit.timeit(lambda:[chr(x).encode() for x in aa], number=1000000)
    1.1887179240584373
    >>> timeit.timeit(lambda:[chr(x).encode() for x in aa], number=1000000)
    1.2292228639125824
    Method 2/results
    >>> timeit.timeit(lambda:[x.encode() for x in aa.decode()], number=1000000)
    0.9501874335110188
    >>> timeit.timeit(lambda:[x.encode() for x in aa.decode()], number=1000000)
    0.957287285476923
    :param bytes_str:
    :return:
    """
    return [x.encode() for x in to_str(bytes_str)]


def dict_to_byte_dict(var):
    """
    Convert two level dict to dictionary with byte index/values
    :param var:
    :return:
    """
    byte_dict = {}
    for key in var:
        if isinstance(var[key], str):
            byte_dict[to_bytes(key)] = to_bytes(var[key])
        elif isinstance(var[key], int):
            byte_dict[to_bytes(key)] = var[key]
        elif isinstance(var[key], (defaultdict, dict)):
            byte_dict[to_bytes(key)] = dict_to_byte_dict(var[key])
        elif isinstance(var[key], (bytes, bytearray)):
            byte_dict[to_bytes(key)] = var[key]
        elif isinstance(var[key], list):
            byte_dict[to_bytes(key)] = to_list_of_bytes(var[key])
        else:
            byte_dict[to_bytes(key)] = var[key]            # else just pass through

    return byte_dict


def to_list(obj):
    """
    Return a list given obj

    :param obj: list, tuple or any object
    :return: a tuple or list of obj
    """

    # Make object a sequence
    if isinstance(obj, (list, tuple)):
        return obj     # as-is, it is already a list/tuple
    elif isinstance(obj, deque):
        return list(obj)
    else:
        return obj,    # make it a tuple


def join_seq(seq, joinstr='\n'):
    """
    Returns a string joined by '\n'.join(seq) with a newline at end

    :param seq: Any seq (list, dict, tuple, set, etc)
    :param joinstr: join string (optional)
    :return: a string
    """
    return "%s%s" % (joinstr.join(str(x) for x in seq), joinstr)


def eval_expr(expr):
    """
    Evaluates mathematical expressions.

    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    # Performance: expr = '%s*0.000001/(50*100)' % i   # for i in range(100000)
    #    eval_expr(expr)   # 1.8 sec
    #    eval(expr)        # 1.0 sec   << faster
    import ast
    return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
    """
    Traverses abstract syntax tree representing mathematical expression,
    evaluating expressions along the way.
    :param node: Node in AST representing a single value, unary or binary expression.
    :return: Evaluated node.
    """
    import ast
    import operator

    # supported operators
    operators = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                 ast.Div: operator.truediv, ast.Pow: operator.pow, ast.BitXor: operator.xor,
                 ast.USub: operator.neg}

    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


def regex_with_not(rstr, txt):
    """
    Process rstr (regex string) with special "!" on first character for not

    :param rstr: regex string with not
    :param txt: any string
    :return: regex result
    """
    try:
        if rstr.startswith('!'):
            fstr = rstr[1:]
            return not re.search(fstr, txt)
        else:
            fstr = rstr
            return re.search(fstr, txt)
    except re.error as e:
        raise re.error(f'Error on Input Regex: "{fstr}": {e}')


def truncate(seq_or_str, n=10, message='   ... {len} more lines not displayed.'):
    """
    Truncate list_or_str depending on n
    Returns concatenated string
    :param seq_or_str: Input string or list or seq
    :param n: Maximum n lines
    :param message: Optional message
    :return: concatenated string
    """
    if isinstance(seq_or_str, str):
        inlist = seq_or_str.split('\n')
    else:
        inlist = [x.rstrip() for x in seq_or_str]    # this can be an iterator or set or whatever

    if len(inlist) > n:
        total = len(inlist)
        inlist = inlist[:n]   # truncate
        inlist.append(message.format(len=total - n))

    return '\n'.join(inlist)


def baseN(num, n, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    """
    Change int to a base-n string.
    Up to base-36 is supported without special notation.
    For base 2 and base 16, use built-in bin() and hex().

    Example:
    >>> print baseN(34, 36)
    y
    """
    # Below are special if statements for performance. "if" is very fast.
    if num == 0:
        return numerals[0]
    if num == 1:
        return numerals[1]

    new_num_string = ''
    current = num
    while current != 0:
        new_num_string = numerals[current % n] + new_num_string
        current = current // n
    return new_num_string
    # based from: http://code.activestate.com/recipes/65212 and http://stackoverflow.com/questions/2267362/convert-integer-to-a-string-in-a-given-numeric-base-in-python
    # This is faster than a recursive function (recursive: 4.8 sec vs while: 2.6sec) for 1000000 execs
    # Maximum base is 36: int(n, base): int() base must be >= 2 and <= 36
    # Performance: 1000000 operation on >64 bit number:  31.3 secs   32K op/sec
    # Performance: 1000000 operation on <32 bit number:   3.8 sec:   263K op/sec
    # Performance: 1000000 operation on 32-64 bit number: 4.4 sec:   227K op/sec
    # int() performance: <32 bit:   2.1M op/sec
    # int() performance: 32-64 bit: (same)
    # int() performance: >64 bit:   1.9 op/sec
    #
    # Compare above code vs: https://bitbucket.org/semente/baseconv/src/1a9a7eb8428522465bc70281ec682637def4eb9b/src/baseconv.py?at=default
    # Above is an example of good comparison for *complicated* code vs simple

# from http://stackoverflow.com/questions/147515/least-common-multiple-for-3-or-more-numbers


class Base776:
    """
    Encode a number based on 00->99, aa->zz mapping
    Max of 100+26*26=776 combinations
    """
    @classmethod
    def encode(cls, ctr):
        """Return the 2-character encoding, given the integer value"""
        if ctr >= 776 or ctr < 0:
            raise Exception("Cannot Base776.encode(%r). Max of 775" % ctr)
        if ctr > 99:
            return baseN(ctr - 100, 26, numerals='abcdefghijklmnopqrstuvwxyz').zfill(2).replace('0', 'a')

        return str(ctr).zfill(2)  # plain decimal

    @classmethod
    def decode(cls, chars, mapchar={'a': '0', 'b': '1', 'c': '2', 'd': '3', 'e': '4',
                                    'f': '5', 'g': '6', 'h': '7', 'i': '8', 'j': '9',
                                    'k': 'a', 'l': 'b', 'm': 'c', 'n': 'd', 'o': 'e',
                                    'p': 'f', 'q': 'g', 'r': 'h', 's': 'i', 't': 'j',
                                    'u': 'k', 'v': 'l', 'w': 'm', 'x': 'n', 'y': 'o',
                                    'z': 'p'}):
        '''Return the integer value, given the encoded 2-char string'''
        if len(chars) != 2:
            raise Exception("Base776.decode can only take two char to decode: [%s]" % chars)

        if chars.isdigit():
            return int(chars)
        else:
            try:
                serev_transpose = "%s%s" % (mapchar[chars[0]], mapchar[chars[1]])
            except BaseException:
                raise Exception("Invalid input [%s] to Base776.decode(). Must be 00->99, aa->zz"
                                "" % chars)
            return int(serev_transpose, 26) + 100


class Base3844:
    """
    Encode a number based on 00->99, aa-zz (100-775), aA-z9 (776 - 1711), Aa-Z9 (1712 - 3323), 0a-9Z (3324 - 3843) mapping
    BASE62 - 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    Max of 62*62 = 3844 combinations
    """

    BASE62 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    @classmethod
    def encode(cls, ctr):
        """Return the 2-character encoding, given the integer value"""
        if ctr >= 3844 or ctr < 0:
            raise Exception("Cannot Base3844.encode({}). Max of 3844".format(ctr))
        if ctr > 99:
            index = ctr - 100
            offset = cls._get_offset_encode(ctr)

            return cls._encode_num(index + offset)

        return str(ctr).zfill(2)  # plain decimal

    @classmethod
    def decode(cls, chars):
        """Return the integer value, given the encoded 2-char string"""
        if len(chars) != 2:
            raise Exception("Base3844.decode can only take two char to decode: [%s]" % chars)
        if chars.isdigit():
            return int(chars)
        else:
            offset = cls._get_offset_decode(chars)

            return cls._decode_char(chars) + offset

    @classmethod
    def _encode_num(cls, num):
        return cls.BASE62[num // 62] + cls.BASE62[num % 62]

    @classmethod
    def _char_to_base62_value(cls, char):
        if ord('a') <= ord(char) <= ord('z'):
            return ord(char) - ord('a')
        elif ord('A') <= ord(char) <= ord('Z'):
            return ord(char) - ord('A') + 26
        elif ord('0') <= ord(char) <= ord('9'):
            return int(char) + 52
        else:
            return -1

    @classmethod
    def _decode_char(cls, chars):
        decoded_value = cls._char_to_base62_value(chars[0]) * 62 + cls._char_to_base62_value(chars[1])
        return decoded_value

    @classmethod
    def _get_offset_encode(cls, ctr):
        # Return only aa-zz. Skip [a-z][A-9] combinations.
        if 100 <= ctr <= 775:
            offset = ((ctr - 100) // 26) * 36
        # Return [a-z][A-9].
        elif 776 <= ctr <= 1711:
            offset = ((ctr - 776) // 36 * 26) - 650
        # Return [A-Z][a-9].
        elif 1712 <= ctr <= 3375:
            offset = 0
        # Return [0-9][a-Z]. Skip [0-9][0-9] - all numbers combinations
        elif 3376 <= ctr <= 3843:
            offset = (((ctr - 3376) // 52) + 1) * 10
        else:
            raise Exception('Base3844 is up to 3843. instead got {}'.format(ctr))

        return offset

    @classmethod
    def _get_offset_decode(cls, chars):
        offset = 100

        first_char = chars[0]
        second_char = chars[1]
        first_char_value = cls._char_to_base62_value(first_char)
        second_char_value = cls._char_to_base62_value(second_char)

        if first_char_value == -1 or second_char_value == -1:
            raise Exception("Invalid input [%s] to Base3844.decode(). Must be 00->99, aa->zz, aA->9Z" % chars)

        # aa-zz : 100 - 775
        if first_char_value <= 25 and second_char_value <= 25:
            offset += first_char_value * -36
        # aA-z9 : 776 - 1711
        elif first_char_value <= 25:
            offset += 650 - first_char_value * 26
        # Aa-Z9 : 1712 - 3323
        elif 26 <= first_char_value <= 51:
            offset = 100
        # 0a-9Z : 3324 - 3843
        else:
            try:
                first_digit = int(first_char)
                offset -= first_digit * 10
            except ValueError:
                raise ValueError("Cannot decode %s in Base3844.decode(). first char should be a number" % chars)

        return offset


class RegexCompile:
    __slots__ = ['obj', 'totalcalls', 'objf', 'last_re']
    r"""
    Regex compile-related Class/functions

    Store all compiled regex objects for the script/tool.
    Keeps count of total objects and total calls.
    Python's re builtin module only retains 100 max cached compiled objects.

    Usages:
    1) from gadget.strmore import regex
       myobj = regex.compile('.*\w+')
    2) See __call__()           (regex())
    3) See group()              (regex.group())
    4) See key_compile_regex()  (regex.key_compile_regex())
    """

    def __init__(self):
        self.obj = {}     # dictionary of compiled objects
        self.objf = {}     # dictionary of compiled objects with flags
        self.totalcalls = 0      # counter of total calls
        self.last_re = {'previous': None}     # The last regex run

    def compile(self, regex):
        """Given the regex string, return the regex object"""
        self.totalcalls += 1
        if regex not in self.obj:
            # Cannot use re.X here since some code uses "^"+regex+"$". Use multiline with comment ('regex' 'regex')
            self.obj[regex] = re.compile(regex)
        return self.obj[regex]

    def compilef(self, regex, flags):
        """Given the regex string, return the regex object"""
        self.totalcalls += 1
        regexkey = (regex, flags)
        if regexkey not in self.objf:
            self.objf[regexkey] = re.compile(regex, flags)
        return self.objf[regexkey]

    def count(self):
        """Return the count of total regex objects"""
        return len(self.obj) + len(self.objf)

    def get_totalcalls(self):
        """Return the total number of calls"""
        return self.totalcalls

    def key_compile_regex(self, dd, regex_keys):
        r"""
        Given a dictionary (dd), and list of regex_keys, it will compile the regex_keys.
        The result will be appended on the keyname. '_robj' will be appended

        Example:
           dd = TVPVConfigDict()
           dd.xml = '\w+\.xml'
           dd.rpt = '\w+\.rpt'
           regex.key_compile_regex(dd, dd.keys())
           # dd will become:
           # dd.xml = '\w+\.xml'
           # dd.rpt = '\w+\.rpt'
           # dd.xml_robj = <regexobject>
           # dd.rpt_robj = <regexobject>
        """
        for key in regex_keys:
            if not key.endswith("_robj"):
                dd[key + "_robj"] = self.compile(dd[key])

    def __call__(self, regx, line, flags=0, pre=None, name='previous'):
        r"""
        re.search with optional 'pre' pre-search string (non-regex) for performance.
        It will also save last regex search for group() use later.
        name is optional, for use in group().
        Examples:
           if regex('Pat\s+', line, pre='Pat'):
              <some code>
           if regex('Pat\s+(\w+)', line, name='patregex'):   # name is the name of this regex
              print group(1, 'patregex')
        """
        if pre is not None:
            if pre not in line:
                self.last_re[name] = None
                return False

        if flags == 0:
            self.last_re[name] = self.compile(regx).search(line)
        else:
            self.last_re[name] = self.compilef(regx, flags).search(line)
        return self.last_re[name]

    def group(self, grp, name='previous'):
        r"""
        Access the last regex group results (or the specified regex name)
          example: if regex('Pat\s+(\w+)', line):
                      pat=regex.group(1)
        """
        if not self.last_re[name] is None:
            return self.last_re[name].group(grp)
        else:
            raise AttributeError("[%s] regex does not have re.group()" % name)

    def join_make_regex(self, seq, isexactmatch=False, reverse_sort=False):
        """
        A generic function to generate the regex given an iterable.
        If iterable is all one character, then use '[abc]' else '(a|bc|d)'
        Set reverse_sort to True, to avoid aliasing:
           Correct: _(regult|reg)_
           aliasing problem: _(reg|regult)_

        Usage:
        >>> join_make_regex(['a','b','c'])
        [abc]
        >>> join_make_regex(['a','bb','c'])
        (a|bb|c)
        >>> join_make_regex(['a','b','c'], True)
        ^[abc]$
        >>> join_make_regex(['aa'])
        aa
        """
        if len(seq) == 1:
            regex = ''.join(seq)
        elif max([len(x) for x in seq]) == 1:
            regex = "[" + ''.join(sorted(seq, reverse=reverse_sort)) + "]"
        else:
            regex = "(" + '|'.join(sorted(seq, reverse=reverse_sort)) + ")"

        if isexactmatch:
            return "^%s$" % regex

        return regex

    def to_non_capture_group(self, rx):
        """
        Given rx (regular expression string), convert it to non-capturing group.
        >>> regex.to_non_capture_group('(abc|def)')
        (?:abc|def)
        >>> regex.to_non_capture.group('abc|def')
        abc|def
        """
        if rx.startswith('('):
            return str_replace(rx, 0, 1, "(?:")
        return rx


regex = RegexCompile()    # "singleton", instantiated RegexCompile Class
group = regex.group       # backwards compatibility


def printWithUnits(memory):
    """
    Takes in any memory size and converts it into appropriate units.
    Returns the string containing memory size in B, KB, MB or GB
    Usage:
      >>> printWithUnits(25123)
      '25 KB'
    """
    if memory < 1024:  # To return bytes
        return str(memory) + " B"
    elif memory < (1024 * 1024):  # To return KiloBytes
        return str(round(float(memory) / 1024, 2)) + " KB"
    elif memory < (1024 * 1024 * 1024):  # To return MegaBytes
        return str(round(float(memory) / (1024 * 1024), 2)) + " MB"
    else:  # To return GigaBytes
        return str(round(float(memory) / (1024 * 1024 * 1024), 2)) + " GB"


class PinHeader:
    """
    Class to create a patternheader given a list of pins. This is separate from any
    specific tester PatternFile class because it may be useful to create this object
    and call from scripts that might utilize libraries within VEP2
    """

    def __init__(self, pinlist):
        self._list = pinlist

    def getHeaderString(self, comment_char="#", spaces=31):
        """
        Function to return a string of the pattern header
        """
        maxl = max(len(s) for s in self._list)  # Get max length of pin
        pins = [s.rjust(maxl) for s in self._list]  # adjust to maxlength
        header = ''
        spc = to_str(comment_char) + ' ' * spaces  # (spaces-len(comment_char))
        for i in zip(*pins):
            header = header + spc + ''.join(i) + '\n'
        return header


class HtmlLinker:
    """
    This class provides methods to create properly fomatted HTML and Wiki links that can be used
     to display content through web browsers.  This class will also provide features to scan text strings and
     replace known ID values with links to the actual webpages for Rally, TVPV Help, and JitBit
    """
    # Declare a new Enum to track the ticket types allowed.
    class TicketType(EnumType):
        RALLY = EnumElement('RALLY')
        TVPVHELP = EnumElement('TVPVHELP')
        JITBIT = EnumElement('JITBIT')
        WIKI = EnumElement('WIKI')

    ticket_types = TicketType()
    LinkData = NamedSeq('l_type', 'l_id', 'l_url')  # a 'named tuple' variant ... kind of like a struct in C
    linker_types = {ticket_types.RALLY: {'name': 'Rally Story',
                                         'id_regex': r'\b(?P<ID>US\d{5,10})\b',
                                         'base_url': 'https://rally1.rallydev.com/#',
                                         'id_url_extension': '/search?keywords=%s'},

                    # Replaced URL with the JitBit one now that we have officially switched over
                    #      Old URL: 'https://vthsd.intel.com/hsd/pde_oap/#tvpvhelp'
                    #   Old Extens: 'id_url_extension': '/default.aspx?tvpvhelp_id=%s'
                    ticket_types.TVPVHELP: {'name': 'TVPV Help',
                                            'id_regex': r'\b((tvpvhelp)|(help)|(HSD))[:\s#]*(?P<ID>\d{4,8})\b',
                                            'base_url': 'http://htd_tvpv_help.intel.com',
                                            'id_url_extension': '/Ticket/%s'},

                    ticket_types.JITBIT: {'name': 'JitBit Ticket',
                                          'id_regex': r'\b((ticket)|(jitbit))[:\s#]*(?P<ID>\d{3,8})\b',
                                          'base_url': 'http://htd_tvpv_help.intel.com',
                                          'id_url_extension': '/Ticket/%s'},

                    ticket_types.WIKI: {'name': 'Wiki',
                                        'id_regex': r'\bwiki\s*[:]\s*(?P<ID>[^:]+?)\s*[:]',
                                        'base_url': 'https://wiki.ith.intel.com/display/TVPV',
                                        'id_url_extension': '/%s'}}

    @staticmethod
    def create_link(url, link_text, link_format='html'):
        """
        Creates a well formatted HTML or Wiki link that can resolved by a browser
        :param url: Full URL to the webpage to be linked to
        :param link_text: Visible text for the user to click on
        :param link_format: 'html' or 'wiki'. Determines the type of link to be returned
        :return: a text string that is a well formatted HTML or Wiki link to the URL provided
        :return: empty string if unkown format is passed in
        """
        if link_format == 'html':
            return '<a href="%s">%s</a>' % (url, link_text)
        elif link_format == 'wiki':
            return '[%s | %s]' % (url, link_text)
        else:
            return ''

    def get_ids(self, body, id_type=None):
        """
        Scans the text of the input body to find all Link IDs and return a list of LinkData for each ID found
        :param body: text string to scan for Ticket/Story IDs
        :param id_type: limit to a single ticket_type. Default will return all known link types found
        :return: a dict of LinkData tuples for each ID found, key is the ID as well.
        """
        res = {}
        for link_type, link_dict in sorted(iter(self.linker_types.items()), key=lambda x: str(x[0])):
            link_regex = link_dict['id_regex']
            base_url = link_dict['base_url']
            id_url = link_dict['id_url_extension']
            ids = [m.group('ID') for m in re.finditer(link_regex, body, re.IGNORECASE)]

            # Only grab types requested by caller
            for link_id in ids:
                if id_type is None or id_type == link_type:
                    res[link_id] = (self.LinkData(l_type=link_type, l_id=link_id, l_url=base_url + id_url % link_id))
        return res

    def replace_ids(self, body, link_format='html'):
        """
        Scan the text of body to identify Rally/TVPVHelp/JitBit IDs and replace them with appropriate web links
        :param body: text string to replace Ticket/Story IDs with actual links
        :param link_format: 'html' or 'wiki'. Determines the type of link to be returned
        :returns: a copy of the body message with IDs replaced with web links
        """
        # For safety, use HTML single/double quote char value. Was a problem for fs commit messages when passed to
        # the shell when mixed with other HTML links and tags. This is safe to do b/c the fact that we are putting links
        # here already means that we can rely on HTML interpreters.
        res = body.replace("'", "&#39;")
        res = res.replace('"', "&#34;")

        for link_id, link_data in self.get_ids(res).items():
            full_link = self.create_link(link_data.l_url, link_data.l_id, link_format)
            res = res.replace(link_id, full_link)

        return res
