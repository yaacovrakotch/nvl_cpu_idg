#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
print and display related routines

PrintAlign()         # Print an aligned table
PctIndicator()       # Print percent indicator
Dumper(var)          # Print the values of an object
disp(msg)            # Print msg as a debug with lineno, web aware
"""

from .gizmo import IS_UNIX
from itertools import chain
import sys
import os
import traceback
from gadget.gizmo import get_caller_lno


class PrintAlign:
    """
    Given an array or list, Align to its column width
    Usages:
    Example 1: print out string on screen
        aa = PrintAlign(sep='|')
        aa('somedata','moredata','data1')
        aa.disp()

    Example 2: return as a string
        aa = PrintAlign(canvas=mycanvas)
        aa.string()
    """
    # hardcoded string used to denote a line divider (will be replaced when table is printed in get_result)
    div = "{{divider}}"

    def __init__(self,
                 canvas=None,
                 sep='',
                 space=1,
                 header=True,
                 rjust=True,
                 col_header=False,
                 max_col_len=None
                 ):
        """
        canvas=<somearray>
        sep=character separator
        space=Number of spaces before and after separator
        header=bool, if True, print "====" header before after after
        rjust=bool, if True, right justify, else left justify
        col_header=bool, if True, add divider after first line of content (column headers)
        max_col_len is a tuple, containing length for each column. -1 value for dynamic.
        """
        if canvas is None:
            self.list = []
        else:
            self.list = canvas
        self.sep = sep
        self.header = header
        self.space = space
        self.extra = []         # extra print lines. See printline() for example
        self.rjust = rjust
        self.col_header = col_header
        self.max_col_len = max_col_len
        self.maxvalue = []

    def __call__(self, *args):
        """Callable to build the array one row at a time"""
        self.list.append(args)

    def printline(self, line):
        """
        Insert this line (as-is) into the buffer
        .
        Example:
        aa = PrintAlign()
        aa(1,22,333)
        aa(4,4,4)
        aa.printline('# extra print')
        aa(55,6,7)
        aa.disp()

        Output:
        1  22 333
        4   4   4
        # extra print
        55  6   7
        """
        self.extra.append((len(self.list), line))

    def get_max_length(self):
        """get the maximum length for each row """
        self.maxvalue = []

        # special case - str
        if isinstance(self.list, str):
            self.list = [self.list.split()]

        # make self.list a list, since it can be tuple sometimes
        for i in range(len(self.list)):
            self.list[i] = list(self.list[i])

        # get the longest length
        numitems = 0
        for i in range(len(self.list)):
            numitems = max(len(self.list[i]), numitems)

        # check the length of each row, make sure it is same for every row
        colwidth = []
        for i in range(len(self.list)):
            self.list[i].extend([" "] * (numitems - len(self.list[i])))
            colwidth.append([len(str(col)) for col in self.list[i]])

        zipcolwidth = list(zip(*colwidth))  # zip to get the largest value for each column

        for i in range(len(zipcolwidth)):
            maxlen = max(zipcolwidth[i])
            if self.max_col_len:
                if self.max_col_len[i] != -1:
                    maxlen = self.max_col_len[i]

            self.maxvalue.append(maxlen)

        return self.maxvalue

    def get_result(self):
        """return the result"""

        self.get_max_length()

        if not self.list:
            return ""

        totallength = 0
        output = []

        for n, row in enumerate(self.list):
            # process extra lines first
            for tagn, line in self.extra:
                if tagn == n:
                    output.append(line)

            # process the normal lines
            line = self.sep.join(self.as_output_field(value, width)
                                 for value, width in zip(row, self.maxvalue))
            output.append(line)

        # for the last extra-line
        for tagn, line in self.extra:
            if tagn == len(self.list):
                output.append(line)

        totallength = [(totallength + int(width) + (self.space * 2) + len(self.sep))
                       for width in self.maxvalue]
        divider = '=' * sum(totallength)
        if self.col_header:     # first check if a header needs to be inserted after first line
            output = list(chain([output[0]], [divider], output[1:]))
        if self.header:         # next check if dividers should be added to front/end of readout
            output = list(chain([divider], output, [divider]))

        # iterate over the output and replace any placeholders with actual divider lines
        i = 0
        for line in output:
            if self.div in line:
                output[i] = divider
            i += 1

        return output

    def disp(self, strip=False):
        """Display the result"""
        if strip:
            print('\n'.join(x.rstrip() for x in self.get_result()))
        else:
            print('\n'.join(self.get_result()))

    def string(self):
        """Return the result"""
        return '\n'.join(self.get_result()) + '\n'

    def as_output_field(self, value, width):
        """Return one field"""
        if value is None:
            value = ""
        if self.rjust:
            res = str(value).rjust(width)
        else:
            res = str(value).ljust(width)
        return '{space}{res}{space}'.format(space=''.ljust(self.space),
                                            res=res)


class PctIndicator:
    """
    Class to print the '%' status during processing.
    It is suggested to use Context Manager to guarantee removal of print indicators.
    Default is stderr.
       example:
          with PctIndicator(total_lines) as ind:     # total_lines is integer
              for lineno,line in enumerate(fh):
                  ind.disp(lineno)     # lineno is optional
                  <some code, print is ok as long as it's greater than 5 characters>
    """
    __slots__ = ('total', 'prev', 'active', 'out', 'count')

    def __init__(self, total, out=sys.stderr):
        self.total = total
        self.prev = -1
        self.active = False
        self.out = out
        self.count = -1

    def disp(self, n=None):
        """Display the status"""
        if n is None:
            self.count += 1
            n = self.count

        pct = n * 100 // self.total
        if self.prev != pct:
            self.prev = pct
            if self.prev > 100:
                self.prev = 100
            self.out.write("%3d%%\r" % self.prev)
            self.active = True

    def close(self):
        """Remove the indicator print"""
        if self.active:
            self.out.write("     \r")   # erase then go back
            self.active = False

    def __exit__(self, *arg):
        self.close()

    def __enter__(self):
        return(self)


class Dumper:
    """
    Data dumper for any type including objects

    Dumper vs pprint difference:
    1. Dumper will display object attributes. pprint can do simple types.
    2. There is no noise in Dumper for autodict and defaultdict
    3. Dumper has dot=True option

    Example:
    Dumper(var)                                         # Will print var dump
    Dumper(var,dot=True)                                # Display in dot notation
    print 'Dump:\\n'+Dumper(var,p=False).string()       # Return a string (do not print)
    var = Dumper(var,p=False).raw()                     # Returns the dict equivalent
    var = Dumper(globals(),deep=False,p=False).string() # Do not recurse

    >>> a = 12
    >>> print dumper(a, dot=True, p=False).string()
    = 12
    <BLANKLINE>

    >>> d = {'a':10, 'b':'somevalue'}
    >>> print dumper(d, dot=True, p=False).string()
    a = 10
    b = 'somevalue'
    <BLANKLINE>

    >>> mylist = [10, 20, 30]
    >>> print dumper(mylist, dot=True, p=False).string()
    [0] = 10
    [1] = 20
    [2] = 30
    <BLANKLINE>

    >>> from dictmore import autodict
    >>> dd = autodict()
    >>> dd['abc']['def']=10
    >>> dd['ghi']['klm']=20
    >>> print dumper(dd,dot=True,p=False).string()
    abc.def = 10
    ghi.klm = 20
    <BLANKLINE>
    """
    builtintypes = {str, str, bytearray, int, float, int, complex, bool}    # add future "scalar" built-in types here
    listtypes = {list, tuple, set, frozenset}                  # set will be displayed as list (w/ index). To simplify code.
    __slots__ = "deep objonce master dot dupok".split()

    def __init__(self, var, dot=False, deep=True, p=True, dupok=False):      # p is print
        """
        dot  = If True, the display is separated by '.'
        deep = If True, recursively dig into all the object details
        p    = If True, display the output during object creation
        """
        import pprint

        self.deep = deep
        self.objonce = {}
        self.dupok = dupok
        self.master = self._recurse(var, True, '')
        self.dot = dot

        if p:
            if dot:
                print(''.join(sorted(self._dotrecurse(self.master))))
            else:
                pprint.pprint(self.master, width=self.pprint_width())

    def _isdone(self, ivar, keylabel, _builtintypes=builtintypes):
        """stores and checks if object is processed already, avoid infinite recursive loop """
        if self.dupok:   # duplicates is ok
            return False
        if type(ivar) in _builtintypes:
            return False
        if ivar is None:
            return False
        if id(ivar) in self.objonce:
            return True
        self.objonce[id(ivar)] = keylabel
        return False

    def _recurse(self, ivar, top, keylabel, _builtintypes=builtintypes, _listtypes=listtypes):
        """
        Recurse any type of object, then create a simple dict/list = <string>.
        Returns either scalar, list or dict (objects are converted to dict).
        """
        if not self.deep and not top:
            return ivar
        if self._isdone(ivar, keylabel):
            return "DUPLICATE %s" % self.objonce[id(ivar)]
        if ivar is None:
            return ivar
        if type(ivar) in _builtintypes:
            return ivar
        if type(ivar) in _listtypes:                 # lists
            return [self._recurse(val, False, keylabel + ".[%s]" % n) for n, val in enumerate(ivar)]

        local = {}
        successitem = False

        try:
            for ky in sorted(list(ivar.keys()), key=str):
                val = ivar[ky]
                local[ky] = self._recurse(val, False, keylabel + "." + str(ky))
            successitem = True
        except BaseException:
            pass

        try:
            for ky in sorted(vars(ivar), key=str):
                val = vars(ivar)[ky]
                comment = " (obj)"
                if type(val) in _listtypes:
                    comment = ""
                if type(val) in _builtintypes:
                    comment = ""
                if isinstance(val, dict):
                    comment = ""
                local[ky + comment] = self._recurse(val, False, keylabel + "." + str(ky))
        except BaseException:
            if not successitem:
                local['UNKNOWN ' + repr(ivar)] = "Skipped"

        if len(local) == 0:    # when ivar is func/class/lambda/instancemethod, etc
            return ivar
        return local

    def _dotrecurse(self, ivar, _seqtypes=listtypes | {dict}):     # iterator, given a simple list/dict/<scalar>
        """ Create a dot-delimited data structure display """
        if isinstance(ivar, dict):
            for item in sorted(ivar, key=str):
                value = ivar[item]
                if type(value) in _seqtypes:
                    for nitem in sorted(self._dotrecurse(value)):
                        yield str(item) + "." + nitem
                else:
                    yield str(item) + " = " + repr(value) + "\n"
        elif type(ivar) in _seqtypes:
            ctr = 0
            for value in sorted(ivar, key=str):
                item = "[" + str(ctr).rjust(len(str(len(ivar)))) + "]"
                ctr += 1
                if type(value) in _seqtypes:
                    for nitem in sorted(self._dotrecurse(value)):
                        yield str(item) + "." + nitem
                else:
                    yield str(item) + " = " + repr(value) + "\n"
        else:
            yield "= " + repr(ivar) + "\n"

    def raw(self):
        """Returns the resulting dictionary"""
        return self.master

    def string(self):
        """Returns a string of output"""
        import pprint

        if self.dot:
            return ''.join(sorted(self._dotrecurse(self.master)))
        else:
            return pprint.pformat(self.master, width=self.pprint_width())

    def pprint_width(self):
        """
        Purpose:
            Return the width which should be passed to pprint, for the self.master dict.
        Reason:
            Python3 pprint will split strings by spaces if width is too small.
            To get pprint to split each key:value pair to a separate line, but to not split by spaces,
                set the width to the size of the string representation of the dictionary - 1
        :return: pprint width
        """
        return len(str(self.master)) - 1


def disp(msg):
    """
    Smart print() to Embed debug message in html or normal print for commandline
    note that this operation is expensive, so use sparingly!
    """
    lno = get_caller_lno()
    if IS_WEB:
        print(f'\n<!--- {msg} [from lno#{lno}]-->')
    else:
        print(f'{msg} [from lno#{lno}]')


IS_WEB = bool(('HOME' not in os.environ or 'WEBPYTPD' in os.environ) and IS_UNIX)
RED = '\033[31m'     # color red
NORED = '\033[0m'    # end of color red   eg. print(f'This is {RED} color red {NORED}, right?')
