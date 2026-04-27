#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
ArgsBase Module

This module instantiates argparse given configurable arguments (config() method)
Several executables can use this module for reuse.
The config is not in a <prod>/config_vepargs.py file since arguments usually involve code.
The configuration must stay within VepArgs class.

The actual executable arguments are in exe/*.py files

Reasons why ArgsBase is needed:
1. capability to share arguments between tools (e.g. vcf and make_pattern)
2. capability to add postprocessing (e.g. TA_AppendSC and TA_StoreFile)
3. More-configurability thru 'postprocess()'
4. Unittest friendly via the set_empty_opt()
"""
from .helperclass import OPT, Increment
from .files import File, basename_delext
from .shell import CALLERBIN
from .pylog import log
from .strmore import is_ascii, putquotes
from os.path import exists, isdir, abspath, basename, isfile
from collections import defaultdict
from .errors import ErrorCockpit, ErrorInput, check, ErrorUser
import argparse
import re
import sys


class _TA_TypeArgs:
    """
    Abstract Base Class for TA-TypeArgs.
    TypeArgs are the *kind* of Argument Options for Args() class (e.g. StoreTrue, Store, etc)

    Used together with Args() class

    Refer to library/training/ArgsExample.py and ArgsExample_groups.py for example usage.

    Refer to TA_* docstring for individual class use.
    Standard options for all TA_* classes:
      helpmsg=<string>      # Required. Printed during help
      metavar=<string>      # this is the help string displayed for StoreTrue type metavar
      default=<value>       # Set the default value of this argument
      mutex=<mutex_grpname> # only one argument should be true within the mutex_grpname.
      required=<required_grpname>  # at least one argument is required in the required_grpname.
      alias=[]|<name>       # list of other alias options (e.g. 't', when -t or -tuple mean the same thing)
      group=<tool_grpname>  # tool name. Value is 'default'. Used for multi-tool shared args.
      # NOTE: mutex_grpname, required_grpname and tool_grpname are not related to each other.
    """
    is_tack_arg = False
    _NoneArg = dict()  # unique class object

    def __init__(self,
                 helpmsg,
                 metavar=None,
                 default=_NoneArg,
                 mutex=None,
                 required=None,
                 alias=None,
                 group="default",
                 choices=None,  # list or seq. This is passed to argparse on TA_Store
                 validkeys=None,  # list or seq, For TA_KeyVal
                 regex=None):  # used with TA_Store* type
        '''Assign class attributes'''
        self.help = helpmsg
        self.metavar = metavar
        self.group = group  # This identifies which group/tool this belongs to
        self.order = self._order()
        self.default = default
        self.choices = choices
        self.mutex = mutex
        self.required = required
        self.regex = regex
        self.alias = alias
        self.validkeys = validkeys
        self.name = None  # assigned in set_name()

    def args(self):
        """Returns a dictionary for this type of Args"""
        raise Exception("args() must be implemented in sub-class!")

    @classmethod
    def check_isinstance(cls, obj):
        """Raise exception if obj is not a TypeArgs object"""
        if not isinstance(obj, _TA_TypeArgs):  # this must be base class
            raise ErrorInput("Input object is not from TypeArgs class: %r" % type(obj))
        return obj

    def postprocess(self, obj):
        """Postprocess the obj. Inherit and override in a different class"""
        return obj  # No postprocessing by default

    def arg1(self, name):
        """Returns the first argument to parser.add_argument()"""
        options = ["-" + name]  # default

        # add the alias
        if self.alias is None:
            self.alias = []
        if isinstance(self.alias, str):
            self.alias = [self.alias]  # convert to list

        for opt in self.alias:
            if opt.startswith('-'):
                options.append(opt)
            else:
                options.append('-' + opt)
        return options

    def empty(self):
        """Return the empty value"""
        return None

    def is_storetype(self):
        """Returns true if the type does not accept any value (ie, StoreTrue)"""
        return False

    def _order(self, incobj=Increment()):  # Increment() is instantiated once at python bootup
        """Return a unique ordered number as the TA_* class is instantiated"""
        return incobj()

    def set_name(self, name):
        """Assign the name option of the object"""
        self.name = name

    @classmethod
    def to_string(cls, obj, argname):
        """
        Given the OPT.name (obj) and argname, return a string that puts back OPT.name in a string
        Usage:
        >>> TA_Append.to_string(OPT.files, 'file')   # say OPT.files is ['file1.txt', 'file2.txt']
        '-file file1.txt -file file2.txt'
        """
        return '-%s %s' % (argname, obj)  # for simple Store


# --- Type Args classes ---
class TA_StoreTrue(_TA_TypeArgs):
    """
    StoreTrue type - OPT resulting to boolean
       CMD> script.py -verbose
       OPT.verbose==True

    If there is no option, OPT.verbose is False    # See .empty() method

    Code Usage:
    cfg.verbose = TA_StoreTrue('helpmessage')
    """

    def args(self):
        """Returns a dictionary for this type"""
        dd = {'help': self.help,
              'action': 'store_true'}
        if self.default is not self.__class__._NoneArg:
            dd['default'] = self.default
        return dd

    def empty(self):
        """Return the empty value"""
        return False

    def is_storetype(self):
        """Returns true if the type does not accept any value (ie, StoreTrue)"""
        return True

    def final_check(self, obj):
        """Do final checks of obj"""
        if self.choices is not None:
            raise Exception("Code Error: Cannot use choices on [-%s] since checking is "
                            "already in place" % self.name)
        if self.regex is not None:
            raise Exception("Code Error: Cannot use regex on [-%s] since checking is "
                            "already in place" % self.name)
        return obj

    @classmethod
    def to_string(cls, obj, argname):
        """
        Given the OPT.name (obj) and argname, return a string that puts back OPT.name in a string
        Usage:
        >>> TA_Append.to_string(OPT.files, 'file')   # say OPT.files is ['file1.txt', 'file2.txt']
        '-file file1.txt -file file2.txt'
        """
        if obj:
            return '-%s' % argname
        else:
            return ''  # return empty


class TA_Store(_TA_TypeArgs):
    """
    Store Type - Plain and simple
       CMD> script.py -t 123
       OPT.t=='123'

    Code Usage:
    cfg.t = TA_Store('helpmessage' [, metavar='tuple number'])
    """

    def args(self, _action="store"):
        """Returns a dictionary for this type"""
        dd = {'help': self.help,
              'action': _action,
              'metavar': self.metavar,
              'choices': self.choices}
        if self.metavar is None:
            del dd['metavar']
        if self.default is not self.__class__._NoneArg:
            dd['default'] = self.default
        return dd

    def final_check(self, obj):
        """Do final checks of obj"""
        # regex option
        if self.regex is not None:
            if not isinstance(self.regex, str):
                raise Exception("Code Error: regex option of [-%s <value>] is of type %s. It must be string"
                                "" % (self.name, type(self.regex)))

            if isinstance(obj, list):
                for item in obj:
                    self._check_regex_item(item)
            else:
                self._check_regex_item(obj)
        return obj

    def _check_regex_item(self, item):
        """Check this item if regex passes"""
        if item is None:
            return
        elif isinstance(item, str):
            if not re.search(self.regex, item):
                raise SystemExit("[-%s %s] is not a valid value based on valid regex: %r"
                                 "" % (self.name, item, self.regex))
        else:
            raise Exception("Code Error: Cannot use regex on [-%s %r] since it is not a string "
                            "or list" % (self.name, item))


class TA_StoreBool(TA_Store):
    """
    Store Type - Will store boolean values.
    Default value can be used safely here and user can disable it (unlike in StoreTrue where default value can't be unset)
       CMD> script.py -nodelete true
       OPT.nodelete is True
       CMD> script.py -nodelete yes
       OPT.nodelete is True
       CMD> script.py -nodelete no
       OPT.nodelete is False

    Code Usage:
    cfg.file = TA_StoreBool('helpmessage' [, default=True])
    """

    def args(self):
        dd = TA_Store.args(self)
        if 'default' not in dd:
            dd['default'] = False
        return dd

    def postprocess(self, obj):
        """check obj"""
        if isinstance(obj, bool):
            return obj
        if isinstance(obj, str):
            if re.search('^(y|yes|yep|yeps|sure|ok|true|1)$', obj, re.IGNORECASE):
                return True
            if re.search('^(n|no|nop|nops|false|0)$', obj, re.IGNORECASE):
                return False
        raise SystemExit("\nError: Input [-%s %s] is not a valid boolean string\n"
                         "" % (self.name, obj))

    def empty(self):
        """Return the empty value"""
        return False

    def final_check(self, obj):
        """Do final checks of obj"""
        if self.choices is not None:
            raise Exception("Code Error: Cannot use choices on [-%s] since checking is "
                            "already in place" % self.name)
        if self.regex is not None:
            raise Exception("Code Error: Cannot use regex on [-%s] since checking is "
                            "already in place" % self.name)
        return obj


class TA_StoreNumber(TA_Store):
    """
    Store Type - Stores as number (integer)
       CMD> script.py -num 123
       OPT.num==123

    Code Usage:
    cfg.num = TA_StoreNumber('helpmessage' [, metavar='number'])
    """

    def postprocess(self, obj):
        """check obj"""
        try:
            return int(obj)
        except BaseException:
            raise SystemExit("\nError: Input argument [-%s %s] is not a valid number\n"
                             "" % (self.name, obj))


class TA_StoreFloat(TA_Store):
    """
    Store Type - Stores as floating point number
       CMD> script.py -num 2.5
       OPT.num==2.5

    Code Usage:
    cfg.num = TA_StoreFloat('helpmessage' [, metavar='float'])
    """

    def postprocess(self, obj):
        """check obj"""
        try:
            return float(obj)
        except BaseException:
            raise SystemExit("\nError: Input argument [-%s %s] is not a valid floating point "
                             "number\n" % (self.name, obj))


class TA_StoreFile(TA_Store):
    """
    Store Type - Check if file exists and it is not a directory. Will make file abspath
       CMD> script.py -file file
       OPT.file=='/abspath/file'

    Code Usage:
    cfg.file = TA_StoreFile('helpmessage' [, metavar='filename'])
    """

    def postprocess(self, obj):
        """check obj"""
        if isdir(obj):
            raise SystemExit("\nError: Input [-%s %s] is a directory. It must be a file, "
                             "not a directory.\n" % (self.name, obj))
        try:
            fobj = File(obj, autofind=True)
        except BaseException:
            raise SystemExit("\nError: Input [-%s %s] does not exist. This file must exist.\n"
                             "" % (self.name, obj))

        return fobj.get_name(abspath=True)


class TA_StoreDir(TA_Store):
    """Store Type - Check if input is a directory"""

    def postprocess(self, obj):
        """check obj"""
        if not isdir(obj):
            raise SystemExit("\nError: Input [-%s %s] is not an existing directory\n"
                             "" % (self.name, obj))
        return abspath(obj)


class TA_StoreFileOrDir(TA_Store):
    """
    Store Type - Check if file or directory exists. Will make file abspath
       CMD> script.py -file file
       OPT.file=='/abspath/file'

    Code Usage:
    cfg.file = TA_StoreFileOrDir('helpmessage' [, metavar='filename'])
    """

    def postprocess(self, obj):
        """check obj"""
        try:
            fobj = File(obj, autofind=True)
        except BaseException:
            raise SystemExit("\nError: Input [-%s %s] does not exist. This file or dir must exist.\n"
                             "" % (self.name, obj))

        return fobj.get_name(abspath=True)


class TA_Append(TA_Store):
    """
    Append type, plain and simple, OPT resulting to an array
       CMD> script.py -t 21 -t 22
       OPT.t==['21','22']

    Code Usage:
    cfg.t = TA_Append('helpmessage' [, metavar='tuple number'])
    """

    def args(self):
        """Returns a dictionary for this type of Store"""
        return TA_Store.args(self, _action="append")

    @classmethod
    def to_string(cls, obj, argname):
        """
        Given the OPT.name (obj) and argname, return a string that puts back OPT.name in a string
        Usage:
        >>> TA_Append.to_string(OPT.files, 'file')   # say OPT.files is ['file1.txt', 'file2.txt']
        '-file file1.txt -file file2.txt'
        """
        return ' '.join('-%s %s' % (argname, val) for val in obj)

    def empty(self):
        """Return the empty value"""
        return []


class TA_Tack(TA_Append):
    """
    Special type, actual code is in RemoveTackArgs
       CMD> script.py -q BAB=foo BAC=bar BAD!=foo   BAE>foo BAF<=foo testid path --
       OPT.q==['BAB=foo', 'BAC=bar', 'BAD!=foo', 'BAE>foo', 'BAF<=foo', 'testid', 'path']
    """
    is_tack_arg = True


class TA_AppendPat(TA_Append):
    """
    Append type, with path or extension removal.
       CMD> script.py -pat abc.pobj
       OPT.pat==['abc']

       CMD> script.py -pat /path/abc.pobj
       OPT.pat==['abc']

    Code Usage:
    cfg.pat = TA_AppendPat('helpmessage' [, metavar='tuple number'])
    """

    def postprocess(self, obj):
        """Postprocess the obj (which is a list) to separate space and comma"""
        return [basename_delext(item) for item in obj]


class TA_AppendPatSC(TA_Append):
    """
    Append type, with path or extension removal.
       CMD> script.py -pat patname1.pobj,patname2.pobj,  patname3.pobj
       OPT.pat==['patname1', 'patname2', 'patname3' ]

       CMD> script.py -pat /path/patname1.pobj,/path/patname2.pobj,/path/patname3.pobj
       OPT.pat==['patname1', 'patname2', 'patname3' ]

    Code Usage:
    cfg.pat = TA_AppendPatSC('helpmessage' [, metavar='pattern name'])
    """

    def postprocess(self, obj):
        """Postprocess the obj (which is a list) to separate space and comma"""
        res = ' '.join(obj).replace(',', ' ').split()
        return [basename_delext(item) for item in res]


class TA_KeyVal(TA_Append):
    """
    Append type, resulting object is a dictionary
       CMD> script.py -serev Mft=00 -serev Mcache=02
       OPT.serev=={'Mft':'00', 'Mcache':'02'}

    Code Usage:
    cfg.serev = TA_KeyVal('helpmessage' [, metavar='<key>=<value>'])
    """

    def _separate(self, obj, help='<key>=<value>'):
        """
        Return a tuple of k,v from 'k=v'. Will raise error if = is not found
        ';' cannot be used inside the <value>.
        if '=' is used inside value, then don't use ';' (aka, multi-value)
        Space is ok in value as long as it is enclosed in quotes
        """
        import shlex
        for txt in obj:  # txt is one value of -arg <value>
            if ';' in txt:
                # multi-value separate by ';'
                expect_key = True
                for item in shlex.split(txt.replace('=', ' ').replace(';', ' ')):  # treat = and ; as space
                    if expect_key:
                        key = item
                    else:
                        yield key, item
                    expect_key = bool(not expect_key)  # toggke uit

                if not expect_key:
                    raise SystemExit("\nError: Input argument [-%s %s] must be [%s] format."
                                     "" % (self.name, txt, help))

            else:
                # simple case
                for txt in obj:
                    if '=' not in txt:
                        raise SystemExit("\nError: Input argument [-%s %s] must be [%s] format."
                                         "" % (self.name, txt, help))

                    yield tuple(txt.split('=', 1))

    def postprocess(self, obj):
        """Postprocess the obj (which is a list) to separate space and comma"""
        res = {k.lower(): v for k, v in self._separate(obj)}

        # Check for validity
        if self.validkeys is not None:
            validkeys = set(x.lower() for x in self.validkeys)
            for key in res:
                if key not in validkeys:
                    raise SystemExit("\nError: Input argument [-%s %s=%s] is not a valid key.\n"
                                     "Valid keys are: %s"
                                     "" % (self.name, key, res[key], ','.join(validkeys)))
        return res

    @classmethod
    def to_string(cls, obj, argname):
        """
        Given the OPT.name (obj) and argname, return a string that puts back OPT.name in a string
        Usage:
        >>> TA_KeyVal.to_string(OPT.serev, 'serev')   # say OPT.serev is {'Mft':'000.001', 'Mcache':'010.011'}
        '-serev Mft=000.001 -serev Mcache=010.011'
        """
        return ' '.join('-%s %s=%s' % (argname, key, list(putquotes([obj[key]]))[0]) for key in sorted(obj))

    def empty(self):
        """Return the empty value"""
        return {}


class TA_KeyValSERev(TA_KeyVal):
    """KeyVal derivative that allow latest and skip"""

    def _separate(self, obj):
        """Iterator: Return a tuple of k,v from 'k=v'. Will raise error if = is not found"""
        for i, txt in enumerate(obj):
            if txt in ('latest', 'skip', 'remove_default'):
                obj[i] = "%s=00" % txt

        # return the iterator of base class
        for res in super()._separate(obj, help='<module>=<serev#>'):
            if len(res[1]) != 2:
                raise SystemExit('\nError: serev value must be a two chars. Provided is [-%s %s]'
                                 '' % (self.name, res[1]))
            yield res


class TA_KeyVal_CaseSensitive(TA_KeyVal):
    # Inherited from TA_KeyVal
    # Remain the key as it is, not uppercas'ed or lowercas'ed
    def postprocess(self, obj):
        """Postprocess the obj (which is a list) to separate space and comma"""
        res = {k: v for k, v in self._separate(obj)}

        # Check for validity
        if self.validkeys is not None:
            validkeys = set(x for x in self.validkeys)
            for key in res:
                if key not in validkeys:
                    raise SystemExit("\nError: Input argument [-%s %s=%s] is not a valid key.\n"
                                     "Valid keys are: %s"
                                     "" % (self.name, key, res[key], ','.join(validkeys)))
        return res


class TA_AppendSC(TA_Append):
    """
    Append type, with space/comma/semicolon delimited considered as append
       CMD> script.py -t 21 -t 22
       CMD> script.py -t 21,22
       CMD> script.py -t '21; 22'
       CMD> script.py -t '21 22'
       OPT.t==['21','22']

    Code Usage:
    cfg.t = TA_AppendSC('helpmessage' [, metavar='tuple number'])
    """

    def postprocess(self, obj):
        """Postprocess the obj (which is a list) to separate space and comma/semicolon"""
        return ' '.join(obj).replace(',', ' ').replace(';', ' ').split()


class TA_AppendNumberSC(TA_AppendSC, TA_StoreNumber):
    """
    Append type, space/comma delimited, numbers only (will be converted to int)
       CMD> script.py -num 21 -num 22
       CMD> script.py -num 21,22
       OPT.num==[21,22]

    Code Usage:
    cfg.num = TA_AppendNumberSC('helpmessage' [, metavar='number])
    """

    def postprocess(self, obj):
        """Postprocess the obj (which is a list) to separate space and comma"""
        return [TA_StoreNumber.postprocess(self, item)  # make it a number
                for item in TA_AppendSC.postprocess(self, obj)]


class TA_FileAppendSC(TA_AppendSC, TA_StoreFile):
    """
    Append type, with space/comma delimited considered as append
    With File Existence checks. Also, files are converted to realpath()
       CMD> script.py -file file1 -file file2
       OPT.file==['/abspath/file1','/abspath/file2']

    Code Usage:
    cfg.file = TA_FileAppendSC('helpmessage' [, metavar='filename'])
    """

    def postprocess(self, obj):
        """
        Postprocess the obj (which is a list) to separate space and comma (using TA_AppendSC)
        Then check for file existence (TA_StoreFile)
        """
        import glob
        res = TA_AppendSC.postprocess(self, obj)
        final = list()
        for item in res:
            globresult = glob.glob(item)
            if globresult:
                for fname in globresult:
                    toadd = TA_StoreFile.postprocess(self, fname)
                    if toadd not in final:     # So that it is unique
                        final.append(toadd)
            else:
                TA_StoreFile.postprocess(self, item)  # this line will error out
        return final  # unique list


class TA_FileOrDirAppendSC(TA_AppendSC, TA_StoreFileOrDir):
    """
    Append type, with space/comma delimited considered as append
    With File Existence checks. Also, files are converted to realpath()
       CMD> script.py -file file1 -file file2
       OPT.file==['/abspath/file1','/abspath/file2']

    Code Usage:
    cfg.file = TA_FileOrDirAppendSC('helpmessage' [, metavar='filename'])
    """

    def postprocess(self, obj):
        """
        Postprocess the obj (which is a list) to separate space and comma (using TA_AppendSC)
        Then check for file existence (TA_StoreFile)
        """
        import glob
        res = TA_AppendSC.postprocess(self, obj)
        final = list()
        for item in res:
            globresult = glob.glob(item)
            if globresult:
                for fname in globresult:
                    toadd = TA_StoreFileOrDir.postprocess(self, fname)
                    if toadd not in final:     # So that it is unique
                        final.append(toadd)
            else:
                TA_StoreFileOrDir.postprocess(self, item)  # this line will error out
        return final  # unique list


class TA_DirAppendSC(TA_AppendSC, TA_StoreDir):
    """
    Append type, with space/comma delimited considered as append
    With Dir Existence check
       CMD> script.py -dir /somedir,/anotherdir
       OPT.dir==['/somedir','/anotherdir']

    Code Usage:
    cfg.dir = TA_DirAppendSC('helpmessage' [, metavar='dirname'])
    """

    def postprocess(self, obj):
        """
        Postprocess the obj (which is a list) to separate space and comma (using TA_AppendSC)
        Then check for dir existence (TA_StoreDir)
        """
        res = TA_AppendSC.postprocess(self, obj)
        return [TA_StoreDir.postprocess(self, ff) for ff in res]


class TA_All(TA_Store):
    """
    Used for positional arguments (aka, argv[0])
       CMD> script.py abc def
       OPT.all==['abc','def']

    Code Usage:
    cfg.all = TA_All('helpmessage' [, metavar='filename'])
    """

    def args(self):
        """Returns a dictionary for this type"""
        dd = {'help': self.help,
              'metavar': self.metavar,
              'nargs': '*'}
        if self.metavar is None:
            del dd['metavar']
        return dd

    def arg1(self, name):
        """Returns the first argument to parser.add_argument()"""
        return [name]

    def empty(self):
        """Return the empty value"""
        return []

    @classmethod
    def to_string(cls, obj, argname=None):
        """
        Given the OPT.name (obj) and argname, return a string that puts back OPT.name in a string
        Usage:
        >>> TA_All.to_string(OPT.all)   # say OPT.all is ['file1.txt', 'file2.txt']
        'file1.txt file2.txt'
        """
        return ' '.join(obj)


class TA_AllOne(TA_All):
    """
    Used for positional arguments (aka, argv[0])
       CMD> script.py abc
       OPT.all=='abc'

    Code Usage:
    cfg.all = TA_AllOne('helpmessage' [, metavar='filename'])
    """

    def args(self):
        """Returns a dictionary for this type"""
        dd = {'help': self.help,
              'metavar': self.metavar,
              'nargs': '?'}
        if self.metavar is None:
            del dd['metavar']
        return dd

    def empty(self):
        """Return the empty value"""
        return None

    @classmethod
    def to_string(cls, obj, argname=None):
        """
        Given the OPT.name (obj) and argname, return a string that puts back OPT.name in a string
        Usage:
        >>> TA_AllOne.to_string(OPT.all)   # say OPT.all is ['file1.txt', 'file2.txt']
        'file1.txt file2.txt'
        """
        return obj


class RemoveTackArgs:
    """
    Remove the tack arguments from sys.argv - since argparse does not understand tacks
    """

    def __init__(self, tacks):
        self.tacklist = tacks
        self.tack_args = dict()

    def __enter__(self):
        """Executed upon entry to with block"""

        self.original_value = list(sys.argv)
        for tackarg in self.tacklist:
            # iterate through and remove tack args
            is_tack = False
            argv_list = list(sys.argv)

            index = 0

            for arg in argv_list:
                # check if the current arg is this ta_ta
                # if tackarg == arg[1:]:
                if re.match(r'\-*' + tackarg + '$', arg):
                    is_tack = True
                    del sys.argv[index]
                    index -= 1
                elif is_tack and (arg == '--' or arg == "-" + tackarg + "-"):
                    is_tack = False
                    del sys.argv[index]
                    index -= 1
                elif is_tack:
                    # pulling args from inside the -arg and --
                    # add the arg to our list
                    del sys.argv[index]
                    index -= 1
                    self.tack_args.setdefault(tackarg, []).append(arg)
                index += 1

            if is_tack:
                raise SystemExit("\nError: No end token -- detected for %r.\n" % tackarg)

        return self.tack_args

    def __exit__(self, exc_type, exc_value, traceback):
        """Executed upon closure of with block"""
        sys.argv = list(self.original_value)


# --- ArgsBase ---
class ArgsBase:
    """
    Base class - Argument handler class

    Usage: Inherit this class and implement config() method

    a) Use all options:
    SubClassArgs(desc=__doc__)

    b) Subset of arguments:
    SubClassArgs(listopt=[list_of_valid_options],   # set to empty list to get default arguments
                desc=__doc__,
                listreq=[list_of_required_options],
                group=None)     # set this by default to get all arguments

    Arguments will go in OPT and uses argparse

    Refer to library/training/ArgsExample.py and ArgsExample_groups.py for example usage.
    Refer to docstring of _TA_TypeArgs for options available to TA* objects.
    """

    def __init__(self, listopt=None, desc="", listreq=[], group="default", execute=True, collect_stats=True):
        """
        listopts is a list of valid options to use. None to use all.
        desc is the main help description. Set this to __doc__.
        listreq is a list of required options for this tool.
        group specifies which gorup to use. It can be a string or a list or None.
              None means use all groups.
        collect_stats has the tool collect Usage Stats that will be uploaded to the central DB
        """
        self.cfg = self.config()
        self.desc = self.tool_description(desc)
        check.is_list_or_set(listreq)  # listreq is a readonly var

        if execute:
            self.execute(listopt, listreq, group)

    def execute(self, listopt, listreq, group):
        """
        Instantate argparse
        """
        self.check_unicode()  # do not allow unicode in argument
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=self.desc)

        # Do some checks
        if listopt is None:
            listopt = []
        else:
            check.is_list_or_set(listopt)
            if group is not None:
                raise ErrorInput("Cannot specify listopt and group at the same time.",
                                 "Pls set group=None.")

        if self.cfg is None:  # cfg not defined in caller
            raise ErrorInput("Config dictionary (cfg) is not defined.",
                             "Pls define cfg dictionary in config().")

        # Update confg arguments with default values.
        self.cfg.update({'nobulletin': TA_StoreTrue('Turns off VEP2 news message.'),
                         'devdebug': TA_StoreTrue('Print log.dev debug messages.')
                         })
        if 'verbosity_level' not in self.cfg:
            vl_choices = 'DEBUG INFO WARNING ERROR CRITICAL'.split()
            self.cfg.verbosity_level = TA_Store('set the verbosity level',
                                                metavar="<%s>" % '|'.join(vl_choices),
                                                choices=vl_choices)
        # Normal run: group=="default"
        if group is not None:  # reassign listopt if group is provided
            listopt = []
            for opt in sorted(self.cfg, key=lambda x: self.cfg[x].order):
                if self.cfg[opt].group == group:
                    listopt.append(opt)

        tacklist = []
        # call parser
        for opt in listopt:
            if opt not in self.cfg:
                raise ErrorCockpit('Option %r is not defined in VepArgs.config()' % opt)
            obj = self.cfg[opt]  # get the TypeArg obj
            _TA_TypeArgs.check_isinstance(obj)  # check that it's the correct
            obj.set_name(opt)  # put the name in there

            parser.add_argument(*obj.arg1(opt), **obj.args())
            if obj.is_tack_arg:
                tacklist.append(opt)

        self.modify_sysargs()
        OPT.clear()  # clear it initially
        with RemoveTackArgs(tacklist) as rta:
            try:
                OPT.initialize(parser.parse_args())
            except SystemExit:
                # Exception is caught both for '-help' and for incorrect arguments
                exit(0)

        OPT.update(rta)

        self._parser = parser
        # assign the objects back to OPT, so it can be accessed later
        for opt in listopt:
            OPT.TAOBJ_set(opt, self.cfg[opt])  # to access: OPT.TAOBJ_get('argname')

        # Check for postprocessing / empty
        for opt in listopt:
            if OPT[opt] is None:
                OPT[opt] = self.cfg[opt].empty()
            else:
                OPT[opt] = self.cfg[opt].postprocess(OPT[opt])

        # Check for final_check
        for opt in listopt:
            OPT[opt] = self.cfg[opt].final_check(OPT[opt])  # Note: even None go thru here

        # Check for required via listreq
        if self.isrequired(listreq) and not OPT.vr2help:
            print("Error: One of the following is required: %s\n" % ", ".join("-" + x for x in listreq))
            self.print_help()

        # Check for required via required
        onceset = defaultdict(list)
        oncelist = defaultdict(list)
        for opt in listopt:
            req_grp = self.cfg[opt].required
            if req_grp is not None:
                oncelist[req_grp].append(opt)
                if OPT[opt]:
                    onceset[req_grp].append(opt)
        for req_grp in oncelist:
            if len(onceset[req_grp]) == 0:
                raise SystemExit("Error: At least one argument in [%s] is required. Add -h for help and example usage."
                                 "" % ", ".join("-%s" % x for x in oncelist[req_grp]))

        # check for mutex
        onceset = {}
        for opt in listopt:
            if OPT[opt] and self.cfg[opt].mutex is not None:
                if self.cfg[opt].mutex in onceset:
                    raise SystemExit("Error: argument [-%s] is not allowed with [-%s]"
                                     "" % (onceset[self.cfg[opt].mutex], opt))
                else:
                    onceset[self.cfg[opt].mutex] = opt

        # override tvpvroot prodcode if needed
        self.override_tvpvroot_prodcode()

        # set verbosity level
        if OPT.verbosity_level:
            log.set_verbosity(OPT.verbosity_level)

        return listopt  # for unittest

    def modify_sysargs(self):
        """
        sys.args modify placeholder routine (before argparse is called)
        See vcf_base.py for example usage
        Used when "-h" needs to be overridden
        """
        pass  # none for base class

    @classmethod
    def override_tvpvroot_prodcode(cls, name=None):
        """One source environment but different tvpvroots"""
        pass  # do nothing for base class

    def print_help(self):
        """Display the parse args help message"""
        self._parser.parse_args(['-h'])

    def tool_description(self, desc):
        """
        Return the string to display during -h
        Default is to use the desc=<value>, from Args() initialization.
        Override this method if needed
        """
        return desc

    def isrequired(self, listreq):
        """
        Returns True if all given options are not specified (aka, invalid)
        This is 'OR'. Any one valid option will return False.
        """
        if len(listreq) == 0:
            return False

        invalid = True  # invalid by default
        for opt in listreq:
            if opt not in OPT:
                raise ErrorInput("required argument %r is not specified in configuration of arguments." % opt)
            if isinstance(OPT[opt], list):
                if len(OPT[opt]) > 0:
                    invalid = False  # if it is list then there is a value
            else:
                if OPT[opt]:
                    invalid = False
        return invalid

    @classmethod
    def set_empty_opt(cls, arglist=None):
        """
        Clear OPT and set OPT values to empty
        This is used for unittest
        If arglist is None then create all known options from config.
        otherwise, use arglist for the list of options
        """
        cfg = cls(execute=False).config()
        if arglist is None:
            arglist = cfg
        else:
            check.is_list_or_set(arglist)

        OPT.clear()  # Clear OPT
        for arg in arglist:
            if arg not in cfg:
                raise ErrorInput("arg %r is not configured in config()" % arg)
            OPT[arg] = cfg[arg].empty()

    def call_methods(self, listopts):
        """
        Call the methods based on listopts.
        The method name is do_<optname>()
        This is called from main() as a generic caller.
        """
        for routine in listopts:
            if OPT[routine]:
                method = getattr(self, "do_%s" % routine)
                # print " Calling: do_%s" % routine
                return method()
        else:
            log.dev(" no listopts passed to def call_methods, self.do_else()")
            self.do_else()

    def do_else(self):
        """Method to call when no valid command was found"""
        self.print_help()  # default is to print help

    def config(self):
        """
        Create and return the argument configuration data structure
        The order below will matter, it is the order of display during help.
        Returns a dictionary of TA_args
        """
        raise Exception("config() must be implemented in sub-class!")

    def main(self):
        """
        Main entry point
        """
        raise Exception("main() must be implemented in sub-class!")

    def check_unicode(self):
        """
        Check sys.arg, and will raise exception if unicode character exist
        """
        for item in sys.argv:
            if not is_ascii(item):
                raise ErrorUser("The input argument %r contain special characters." % ' '.join(sys.argv),
                                "Pls replace (aka retype) the special character in your xterm. "
                                r"The special character has \x something. "
                                "This usually happens when you cut&paste command from windows.")

    def is_upload(self):
        """
        This tells the TVPVUsageDB whether this tool's full stats should be uploaded or not.
        Override this method in your own tool if it should not be logged
        :return: True if all of the tool's stats should be uploaded.  False means that this run will only
                update the Counts table in the DB.
        """
        return True


class Args(ArgsBase):
    """Project specific Customization class"""
    pass    # replace this with project specific code
