#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Various helper classes that are not complex

PrivClass()    - Private Base Class
Enum()         - Enumerated Class
Flow()         - Flow Class
ConfigAssign() - Config Assignment helper for eclipse outline pane
TagOnce()      - Helper on once-only logic (Tagging once)
OnceADay()     - Helper on once a day logic (If the hour is met)
Increment()    - Returns a sequential number (starting with 1)
NoneLikeClass()- Creates a nonelike variable.
OPT            - Instantiated OptArgs() - Singleton - Dictionary-like Tool Arguments
"""

import sys
import time
import os
from .dictmore import DictDot, TVPVConfigDict
from .gizmo import MockVar
from itertools import chain
from io import StringIO


class NoneLikeClass:
    """
    None-Like class, for use with a None-like variable (once instantiated).
    Need to instantiate to be used.

    Example:
        required = NoneLikeClass()
        optional = NoneLikeClass()

        def MyFunc(timer=required, split=optional):
            pass

        # Then use required and optional like a None. Both are bool() False.
    """

    def __bool__(self):
        return False


class Flow:
    """Flow control of diff sections"""

    def __init__(self, only, skip, add):
        from collections import OrderedDict

        self.only = set()
        self.skip = set()
        self.add = set()
        self.items = []
        self.code_desc = OrderedDict()   # {code: description}

        if only:
            self.only = {x.lower() for x in only}

        if skip:
            self.skip = {x.lower() for x in skip}

        if add:
            self.add = {x.lower() for x in add}

    def check_inputs(self):
        """Checks only, skip, add"""
        for item in self.only:
            text = f'Error: [-only {item}] is not a valid flow. Run -flows for list.'
            assert item in self.code_desc, text
        for item in self.skip:
            text = f'Error: [-skip {item}] is not a valid flow. Run -flows for list.'
            assert item in self.code_desc, text
        for item in self.add:
            text = f'Error: [-add {item}] is not a valid flow. Run -flows for list.'
            assert item in self.code_desc, text

    def append(self, func, desc, args=[], kwargs={}, skip=False):
        """
        Add a routine

        :param func: callable
        :param desc: code for this callable, used in OPT
        :param args: optional positional args
        :param kwargs: optional kwargs
        :param skip: Set to True to skip by default, enable by add or only
        """
        code, txt = desc.split(' ', 1)
        if skip:
            txt = f'{txt} (Skipped, enable via -add)'
        self.code_desc[code] = txt

        self.items.append((func, code, args, kwargs, skip))

    def disp_flows(self, is_display):
        """
        Display the flow help

        :param is_display: True then display flow then exit
        """
        if not is_display:
            return

        print("Flows in order:")
        for code, txt in self.code_desc.items():
            print(f'{code:2} - {txt}')
        exit(0)

    def run(self, disp=True):
        """Call the items, given only, skip, add"""
        from .pylog import log
        self.check_inputs()    # Can only call this when all items are appended

        for func, code, args, kwargs, skip in self.items:
            # process skip
            if skip:
                if code in self.only:
                    pass    # let this run
                elif code in self.add:
                    pass    # let this run
                else:
                    continue      # pragma: no cover - python optimization

            # skip this
            if code in self.skip:
                continue

            if self.only and (code not in self.only):
                continue

            # call it
            if disp:
                head = f'#{code} {self.code_desc[code]}'
                log.info('')
                log.info(head)
                log.info('=' * len(head))

            func(*args, **kwargs)


class PrivClass:
    """
    A Base class that will Error out if Direct write to a private attribute has been done.
    All attributes are private by default.

    Uses __setattr__ and caller frame. Assumes that 'self' is the naming convention of classes.
    """
    # Performance: 1.2 seconds for 1000000 attribute writes. (typical machine)
    # Read is unaffected (fast)

    def __setattr__(self, item, value, setattr=object.__setattr__, getframe=sys._getframe):
        """Add check (only the class can write) to class attribute"""
        cf = getframe(1).f_locals  # caller frame's f_locals
        if 'self' in cf and (self is cf['self'] or
                             cf['self'].__class__.__name__ in ('MockVar', '_patch')):
            setattr(self, item, value)
        else:
            raise KeyError("Cannot write to {} directly".format(item))

    def __init__(self, *args, **kwargs):
        """
        auto-attribute register
        default kwargs registering into the object attributes in constructor
        """
        self.__dict__.update(kwargs)


class Enum:
    """
    ******DEPRICATED: Use EnumType Instead ************

    This is a helper class to create functionality of a C++ enumeration. Read more about the concept
    at http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python.
    One example usage was in state equations for DRIVING, STROBING, STROBINGX, DRIVINGZ, etc.
    Once the object is setup, keys cannot be changed. Expected access is like a constant.
    Example:
       Tap_enum =  Enum('IDLE','SHIFTIR,'SHIFTDR')
       if somestate == Tap_enum.SHIFTDR:      # <-- accessed as a constant.

    Two ways to initialize:
      enumvar = Enum(key=value, key2=value, keyN=value)
      enumvar = Enum (key0, key1, key2, key3)   # will automatically create sequential values for each key
    Mixed is OK as well, but sequential entries go before keyed entries.

    On your code, to check if a variable/argument is enumerated type:
        enumvar.check_valid(var)
    To hide the interval value of enum, use the following as example:
        enumvar = Enum(PASS=hash('PASS'), FAIL=hash('FAIL'), WIP=hash('WIP'))
    To get the reverse mapping:
        print enumvar.reverse_mapping[enumvar.PASS]   # returns 'PASS'
    """

    def __init__(self, *args, **kwargs):

        # arguments and keys must be string or integer
        for key in chain(args, list(kwargs.keys())):
            if not isinstance(key, (str, bytes)):
                raise TypeError("enum key %r is not a string. It must be a string")

        # Takes care of plain arguments
        self.__dict__ = dict(list(zip(args, args)))

        # Check if any duplicates and extract kwargs
        for k, v in list(kwargs.items()):
            if hasattr(self, k):
                raise AttributeError("Duplicate Enum attribute found: " + k)
            else:
                setattr(self, k, v)

        # make a reverse lookup.dictionary.
        reverse = dict((value, key) for key, value in self.__dict__.items())
        setattr(self, 'reverse_mapping', reverse)
        setattr(self, '_locked', True)

    def __setattr__(self, item, value, setattr=object.__setattr__):

        if '_locked' in self.__dict__:
            raise Exception("Enum Class, cannot set attributes after the Enum object is created")

        # set the attribute if not raised
        else:
            if item == '__dict__' and value:    # this code allows for dot lookup of bytes keys with string representation (py3)
                for entry in value:
                    setattr(self, strmore.to_str(entry), value[entry])
            else:
                setattr(self, item, value)

    def __getitem__(self, item):
        return self.__dict__[strmore.to_str(item)]  # If fail, raise KeyError. Using getattr(self, item) will raise AttributeError

    def __contains__(self, item):
        return hasattr(self, item)

    def keys(self):
        """Return the set of enums (in any order)"""
        return set(k for k in list(self.__dict__.keys()) if k not in ('_locked', 'reverse_mapping'))

    def indices(self):
        """Return the set of valid indices"""
        return set(v for k, v in list(self.__dict__.items()) if k not in ('_locked', 'reverse_mapping'))

    def check_valid(self, item, message="[{item}] is not a valid enumerated value"):
        """Raise exception if item is not a valid enumerated item"""
        if item not in self.indices():
            raise Exception(message.format(item=item))


class EnumElement:
    """
    This element class provides a printable implementation of Enum Elements so that unit tests
    and other prints will report out human readable versions of the Enum values.  See 'EnumType' below
    for usage examples.
    """

    def __init__(self, e_type):
        self.e_type = e_type

    def __repr__(self):
        return 'EnumElement(%r)' % self.e_type


class EnumType:
    """
    A better way of using enums - IDE friendly
    It is compatible with previous Enum() definition

    # Usage: Define the enum as a class
    class TapState(EnumType):
        IDLE = EnumElement('IDLE')
        SHIFTIR = EnumElement('SHIFTIR')
        SHIFTDR = EnumElement('SHIFTDR')
    tapstate = TapState()

    # Access by:
    currentstate = tapstate.IDLE

    # To check if a variable/argument is enumerated type:
    if currentstate in tapstate.indices():
        <code>

    # To get the reverse mapping:
    print tapstate.index_name(tapstate.IDLE)   # returns 'IDLE'

    # To iterate all items in enums:
    for items in tapstate.indices():
        <code, item is <unique number>

    # To iterate all string keys in enum:
    for item in tapstate:
        <code, item is 'IDLE'>

    # Check if string exist:
    if 'IDLE' in tapstate:
        <code>

    # To convert a string index to the enum value
    currentstate = tapstate['IDLE']
    """

    def __init__(self):
        # these are the method names for the class
        methods = {'reverse_mapping', 'indices', 'check_valid', 'index_name', 'keys'}

        # all items, example: {'IDLE':<value>}
        self._dict_all_items = {k: getattr(self, k) for k in dir(self)
                                if ((not k.startswith('_')) and
                                    k not in methods)}

        # example: {<value>:'IDLE'}
        self.reverse_mapping = {v: k for k, v in self._dict_all_items.items()}

        # check for duplicate values, and display error message
        if len(self.reverse_mapping) != len(self._dict_all_items):
            res = {}
            for key, value in self._dict_all_items.items():
                if value in res:
                    raise Exception("[%s] and [%s] has same value [%s]. Values must be unique."
                                    "" % (res[value], key, value))
                res[value] = key
            else:  # pragma: no cover - unreachable code
                raise Exception("Cockpit Error: This code should be unreachable!")

        self._locked = True

    def __contains__(self, item):
        """Return True if item exist in enum"""
        return item in self._dict_all_items

    def __iter__(self):
        """Return all the string names"""
        for item in self._dict_all_items:
            yield item

    def index_name(self, item):
        """
        Return index name of this enum item
        Example:
        current_state = tapstate.IDLE
        print tapstate.index_name(current_state)    # 'IDLE'

        """
        if item in self.reverse_mapping:
            return self.reverse_mapping[item]
        raise ValueError('[%s] is not a valid enum item for %s' % (item, self.__class__.__name__))

    def __getitem__(self, item):
        """
        Return name of this enum item
        print tapstate['IDLE']   # <unique_number|value>
        """
        if item in self._dict_all_items:
            return self._dict_all_items[item]
        raise ValueError('[%s] is not a valid enum index for %s' % (item, self.__class__.__name__))

    def __setattr__(self, item, value, setattr=object.__setattr__):
        """Prevent addition of other attributes"""
        if hasattr(self, '_locked'):
            raise Exception("EnumType Class, cannot set attributes after the EnumType object is created")

        # set the attribute if not raised
        else:
            setattr(self, item, value)

    def indices(self):
        """
        Return the sequence of valid indices.
        e.g. <unique_numbers>
        """
        return set(self.reverse_mapping)

    def keys(self):
        """
        Return the set of enums string (in any order)
        e.g. 'IDLE'
        """
        return set(self._dict_all_items)

    def check_valid(self, item, message="[{item}] is not a valid enumerated value"):
        """Raise exception if item is not a valid enumerated item"""
        if item not in self.reverse_mapping:
            raise Exception(message.format(item=item))


class TagOnce:
    """
    Simple class for tagging & checking a particular key.

    Consider below code:
       onceset = set()
       for id in somearray:
           if not id in onceset:
               <do something with id>
               onceset.add(id)

    Above code can be replcaed with:
       onceset = TagOnce()
       for id in somearray:
           if onceset(id):
               <do something with id>
    """
    __slots__ = ['tags']

    def __init__(self):
        self.tags = set()

    def __call__(self, key):
        """
        Returns True if key is not in set, then add it in the set.
        Returns False otherwise.
        """
        if key in self.tags:
            return False

        self.tags.add(key)
        return True


class OnceADay:
    """
    Returns true, if the hour is met (Once a Day).
    Usage:
        istime = OnceADay(21)  # 9pm
        while True:
            if istime():
                # some code
            time.sleep(1)
    """

    def __init__(self, hr):
        """hr is in 24 hr format"""
        self.hr = hr
        self.prev = 30
        self.time = time.time()

    def __call__(self, _hr=None):
        """Returns true if time equals set hr"""
        if _hr is None:
            _hr = time.localtime(time.time()).tm_hour

        if _hr != self.prev and _hr == self.hr:
            self.prev = _hr
            self.time = time.time()
            return True

        self.prev = _hr

        if time.time() - self.time > 3600 * 25:  # 25 hrs
            self.prev = _hr
            self.time = time.time()
            return True

        return False


class ConfigAssign:
    """
    A configuration helper so that it is easy to find configuration in
    IDE editor (located in Outline pane).

    # Example:

    @ConfigAssign.direct_to_var()
    class vrev(ConfigAssign):
        '''vrev will automatically become a dictionary, via direct_to_var() decorator'''
        def DEFINE(self):
            vrev = TVPVConfigDict()
            self.args = [vrev]

        def vrevPQ3(self, cfg):
            v = cfg.vrevPQ3
            v.description = '1st silicon vrev'
            v.valid       = True
            v.valid_modes = ['somemodes']

    print '# Output:', vrev      # vrev is a TVPVConfigDict dictionary
    # Output: {'vrevPQ3': {'valid_modes': ['somemodes'], 'valid': True, 'description': '1st silicon vrev'}}
    """
    # Note: Cannot use ABC here since decorator won't work well

    def __init__(self):
        # execute DEFINE to get self.args
        self.DEFINE()  # execute it

        # Check if args exist
        if not hasattr(self, "args"):
            raise Exception("Error: args attribute is not defined in DEFINE() method")

        # Check if type of args is correct (must be list)
        if not isinstance(self.args, list):
            raise Exception("Error: args attribute is not a list. It must be a list")

        # get all attributes and execute them
        ignore_self_methods = {'DEFINE', 'RUN', 'args', 'direct_to_var'}
        for funcs in sorted(dir(self)):  # small case zz is bottom
            if funcs.startswith('_'):
                continue
            if funcs in ignore_self_methods:
                continue
            getattr(self, funcs)(*self.args)

    def DEFINE(self):
        """
        This method must be overridden in subclass, then, assign value to self.args.
        self.args is the arguments to all the functions
        """
        raise Exception("DEFINE() method must be implemented in %s() class" % self.__class__.__name__)

    def RUN(self):
        """
        Return the attributes/result
        """
        return self.args

    @classmethod
    def direct_to_var(cls, *args):
        """
        Decorator, used together with ConfigAssign, to assign the dictionary variable directly
        to the class name.

        See ConfigAssign() docstring for Example usage

        """
        # This routine is patterned from singleton() decorator

        # error out if () is forgotten by user
        if len(args) == 1 and isinstance(args[0], type):
            raise Exception("direct_to_var() decorator must be called as a function, "
                            "ie. '@direct_to_var()'")

        if not (isinstance(args, tuple) and args == tuple()):
            raise Exception("direct_to_var() decorator must not have any arguments.")

        def getinstance(cls1):
            if not issubclass(cls1, cls):
                raise Exception("direct_to_var() decorator only works with ConfigAssign classes")
            obj = cls1().RUN()[0]  # this is executed once upon python bootup
            return obj

        return getinstance


class ConfigAssignDict(ConfigAssign):
    """
    A variant of ConfigAssign in which TVPVConfigDict will be used and AUTO_OFF will be called.
    This class is intended to be used directly with @ConfigAssignDict.direct_to_var()

    Example:
    @ConfigAssignDict.direct_to_var()
    class sdb(ConfigAssign):
        def sdb_r21(self, sdb):
            v = sdb.r21
            v.description = 'SDB XTOS_Linux_Pattern_Compiler_2.1 (NHM)'
            v.dir         = join(veppaths.get_item('sdb_compiler_dir'),'XTOS_Linux_Pattern_Compiler_2.1')
    """

    def DEFINE(self):
        cfg = TVPVConfigDict()
        self.args = [cfg]

    def zzzz_AUTO_OFF(self, cfg):  # this is executed last
        cfg.AUTO_OFF()


class AssignDict(ConfigAssign):
    """
    Improved Version of ConfigAssign/ConfigAssignDict, with key defaulted to the name of the function.

    # Example:

    @AssignDict.direct_to_var()
    class vrev(AssignDict):
        '''vrev will automatically become a dictionary, via direct_to_var() decorator'''
        def DEFINE(self):
            vrev = TVPVConfigDict()
            self.args = [vrev]

        def vrevPQ3(self, cfg):
            cfg.description = '1st silicon vrev'
            cfg.valid       = True
            cfg.valid_modes = ['somemodes']

    print '# Output:', vrev      # vrev is a TVPVConfigDict dictionary
    # Output: {'vrevPQ3': {'valid_modes': ['somemodes'], 'valid': True, 'description': '1st silicon vrev'}}
    """

    def __init__(self):
        # execute DEFINE to get self.args
        cfg = TVPVConfigDict()
        self.args = [cfg]

        # get all attributes and execute them
        ignore_self_methods = {'DEFINE', 'RUN', 'args', 'direct_to_var'}
        for funcs in sorted(dir(self)):  # small case zz is bottom
            if funcs.startswith('_'):
                continue
            if funcs in ignore_self_methods:
                continue
            getattr(self, funcs)(self.args[0][funcs])

        cfg.AUTO_OFF()  # turn it off


class Increment:
    """
    Simple object incrementer. This is used in TraceNaming Priority attribute()

    Usage:
       inc = Increment()
       >>> print inc()
       1
       >>> print inc()
       2
       >>> print inc()
       3
       >>> print inc.val()    # display the value
       3
    """
    __slots__ = ['value', 'step']  # for performance

    def __init__(self, step=1, start=0):
        """Set object value to zero"""
        self.value = start
        self.step = step

    def val(self):
        """Return the object value"""
        return self.value

    def __call__(self):
        """Increment object value and return it"""
        self.value += self.step
        return self.value


class ContextList:
    """
    A context manager that takes in context-manager-objects in arguments and
    execute their __enter__ and __exit__

    This is used when python limit of 21 is met:
    SystemError: too many statically nested blocks

    Usage:
    c_list = [MockVar(something),
              MockVar(something)]
    with ContextList(*c_list):
        <code>
    """

    def __init__(self, *args):
        self.args = args

    def __enter__(self):
        """Execute all __enter__ of the objects"""
        for item in self.args:
            item.__enter__()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Execute all __exit__ of the objects"""
        for item in self.args:
            item.__exit__(exc_type, exc_value, traceback)


class ContextLog:
    """A Context manager base class that has __enter__() and __exit__() and calls close()"""

    def __enter__(self):
        """Override this method in subclass, if needed"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Do not override this method. Instead, implement close() method"""
        if exc_value is not None and not isinstance(exc_value, SystemExit):
            from .pylog import log    # to support py3 imports

            log.debug("Exception Occurred within %s block: %s" % (self.__class__.__name__, exc_value))
        self.close()

    def close(self):
        """Override this method in your subclass"""
        # Note: abstractmethod is not implemented here for simplicity
        raise Exception("close() must be implemented in %s" % self.__class__.__name__)


class EmptyContext:
    """Empty Context Manager - starting template class"""

    def __enter__(self):
        """Executed upon entry to with block"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Executed upon closure of with block"""
        self.close()

    def close(self):
        """closure code"""
        pass


class Alias:
    """
    Simple Config-dictonary assign block.
    Example:
      with Alias(cfg.vrev) as v:
          v.name  = 'vrevAA1'
          v.valid = True

    # Above is the same as:
    cfg.vrev.name  = 'vrevAA1'
    cfg.vrev.valid = True
    """

    def __enter__(self):
        """Return the object"""
        return self.obj

    def __exit__(self, exc_type, exc_value, traceback):
        """Do nothing upon exit"""
        pass

    def __init__(self, obj):
        """obj is any object"""
        self.obj = obj


class OptArgs(DictDot):
    """
    Dictionary-like class that holds the tool arguments.
    Must use argparse module.
    Singleton design. Instantiated as OPT.

    Rationale on why this class exist, as compared to direct argparse object:
    1. argparse object cannot be accessed by '[]' or 'in' operation.
       This class will makes it dictionary-like.
    2. So that executable arguments are stored and encapsulated in OPT which is easily
       accessible without the need for passing argparse object everytime (making OPT a singleton).
    3. This object returns None if the key does not exist (rather than raise KeyError).
       This makes it easy for 'if OPT.noprune:' on unittests / module-use.
       This is patterned from argparse, which returns None for options that is not specified.

    Usage (from main executable):
       from helperclass import OPT
       # assign parser which is argparse module
       OPT.initialize(parser.parse_args())

    To access:
       if OPT.verbose:     # eg. -verbose is defined
           <some code>

    Note: It is possible to access 'verbose' even if it is not defined early on.
          It will return None
    """

    def initialize(self, parseobj):
        """
        Initialize the dictionary. This class is a dictionary.
        """
        for x in vars(parseobj):
            self[x] = getattr(parseobj, x)

    def __getitem__(self, item, dict_getitem=dict.__getitem__):
        """
        Return the dictionary item.
        If item is not found, return None - special for OptArgs
        """
        if item in self:
            return dict_getitem(self, item)
        else:
            if len(self) == 0 and item in ('vrev', 'mode', 'vectype', 'tester'):
                from .shell import CALLERBIN

                if 'make_pattern.py' in CALLERBIN:  # only for this executable
                    # At this point, error out since OPT is being accessed during imports
                    message = ("Cockpit Error: OPT.%s is being accessed but OPT is not populated "
                               "yet. This is an import order problem. Check the imports that "
                               "changed and see if it can be moved out of top-level import. "
                               "Example: https://tvpv.pdx.intel.com/cgi-bin/fossil/fast_vep2.cgi/fdiff?sbs=1&v1="
                               "5fbe26cc3c5ba435f7c4a9af1c20aa6c0b573a6d&v2=c570a475e0b0c9cd0c5d51f5d3099d7b8f424a32"
                               "" % item)
                    raise Exception(message)
            return None

    def __getattr__(self, item):
        """
        Return the dictionary item
        """
        return self[item]

    def TAOBJ_set(self, key, value):
        """
        assign the TAOBJ value
        """
        dict.__setattr__(self, "_TAOBJ_" + key, value)

    def TAOBJ_get(self, key):
        """
        assign the TAOBJ value
        """
        return getattr(self, "_TAOBJ_" + key)

    def clear(self):
        """
        clear the object
        """
        # clear the dict space
        dict.clear(self)

        # clear the attributes
        for attr in dir(self):
            if attr.startswith('_TAOBJ_'):
                self.__delattr__(attr)

    def OPT_deepcopy(self):
        """make a deep copy of self"""
        from copy import deepcopy
        return OptArgs(deepcopy(dict(self)))


# def empty(self):
#        '''Use OPT.clear() to clear values - builtin'''

class OptArgsCustom(OptArgs):
    """singleton: instantiated OptArgs(). See OptArgs() for usage."""

    def from_sysargv_key(self, key):
        """
        Return the value of key from sys.argv. Returns None if not found
        This is used when argparse is not yet called and command argument is needed
        Note: this is limited capability, only TA_Store like
        >>> OPT.from_sysargv_key('server')
        None
        """
        for n, item in enumerate(sys.argv):
            if item == "-" + key:
                try:
                    return sys.argv[n + 1]
                except BaseException:
                    return None
        return None

    def from_sysargv_exist(self, key):
        """
        Return True if key exist in sys.argv
        >>> OPT.from_sysargv_exist('server')
        False
        """
        return bool("-" + key in sys.argv)


OPT = OptArgsCustom()


class Timeout:
    """
    Context manager timeout. Raises Exception if timeout happens.
    UNIX only: There is no signal.SIGALRM in windows.

    Usage:
        try:
            with Timeout(2, MyException):
              # normal code
        except MyException:
            # code if timeout
    """

    def __init__(self, timeout, exception_class, message="Timeout exceeded"):
        self.timeout = timeout
        self.ec = exception_class
        self.message = message

    def __exit__(self, *arg):
        self.close()

    def __enter__(self):
        """Set the signal alarm"""
        import signal
        self.current = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, self.handler)  # Setup the Signal alarm handler
        self.whatsleft = signal.alarm(self.timeout)  # returns zero if none
        return self

    def handler(self, signum, frame):
        """Raise the exception"""
        raise self.ec(self.message)     # pragma: no cover

    def close(self):
        """Disable the alarm, and put back the alarm before it"""
        import signal
        signal.alarm(self.whatsleft)  # disable the alarm.
        if not isinstance(self.current, int):
            signal.signal(signal.SIGALRM, self.current)  # Put it back


class MultiReturn:
    """
    Returns a sequence of value when called multiple times
    Useful on unittests where you Mock something and it is called multiple times

    Example:
    with MockVar(obj, 'somefunc', Mock(side_effect=MultiReturn(1,2,3))):
        print obj.somefunc()  # 1
        print obj.somefunc()  # 2
        print obj.somefunc()  # 3
    """

    def __init__(self, *args):
        """args is the input list of sequences"""
        self.value_list = args
        self.ctr = -1

    def __call__(self, *args, **kwargs):
        """
        Return one value from self.value_list
        *args and **kwargs are thrown away. These are used with mock()
        """
        self.ctr += 1
        if self.ctr >= len(self.value_list):
            raise ValueError("Call to MultiReturn() exceeded the input values. "
                             "There are only %d input values, but call is happening %d times."
                             "" % (len(self.value_list), self.ctr + 1))

        return self.value_list[self.ctr]


class CaptureStdout(MockVar):
    """
    Captures (or suppresses) stdout.

    # Capture Usage:
    with CaptureStdout() as p:
        # code
    print p.getvalue()

    # Suppress stdout usage:
    with CaptureStdout() as p:
        # code, stdout is suppressed
    """

    def __init__(self):
        MockVar.__init__(self, sys, "stdout", StringIO())


class CaptureStderr(MockVar):
    """
    Captures (or suppresses) stderr.

    # Capture Usage:
    with CaptureStderr() as p:
        # code
    print p.getvalue()
    """

    def __init__(self):
        MockVar.__init__(self, sys, "stderr", StringIO())


class CaptureStdoutLog(MockVar):
    """
    Captures (or suppresses) stdout and veplogger.

    # Capture Usage:
    with CaptureStdoutLog() as p:
        # code

    # Suppress stdout usage:
    with CaptureStdoutLog(disp=false) as p:
        # code, stdout is suppressed
    """
    old_level = None
    _log_change = False

    def __init__(self, disp=True):
        """
        :param disp: Set to False to suppress printout at end
        """
        self.disp = disp
        self.p = None
        MockVar.__init__(self, sys, "stdout", StringIO())

    def __enter__(self):
        ret = MockVar.__enter__(self)
        from .pylog import log    # to support py3 imports

        if log.s_stdout is True:
            self.old_level = log.loglevel
            self._log_change = True
            log.stdout(self.old_level)

        self.p = ret
        return ret

    def __exit__(self, *arg):
        MockVar.__exit__(self, *arg)
        from .pylog import log    # to support py3 imports

        if self._log_change is True:
            log.stdout(self.old_level)

        # Print what was captured at end
        if self.disp:
            print(self.p.getvalue())


class RunLater:
    """
    Store a function call so it can be called later.
    Similar concept to atexit, but execution is called at anytime, not just at python exit

    Usage:
    >>> park = RunLater()
    >>> park(log.info, "printme")
    >>> log.info("Do something")
    >>> park.run()
    """

    def __init__(self):
        self.data = []    # function data

    def __call__(self, func, *args, **kwargs):
        """
        Append func(*args, **kwargs) to a bucket called "name"
        """
        self.data.append((func, args, kwargs))

    def run(self):
        """
        Execute the list of functions
        """
        from .pylog import log    # to support py3 imports
        for func, args, kwargs in self.data:
            log.dev('Executing: func=%r args=%r kwargs=%r\n' % (func, args, kwargs))
            func(*args, **kwargs)
        self.data = []


class ExceptionEnv(Exception):
    """
    Errors raised by this class will be re-tried in netbatch (will have exit code 101)
    Why not use ErrorEnv? bec in utils.*, veplib is not imported
    """
    pass


class AutoRestart:
    """
    Daemon/infinite-loop AutoResart feature when code has changed.
    This class uses os.environ to tell if sentinel or client is running.

    sentinel: The process that just launches things. Sets os.environ.
              Writes stdout+stderr to a file.
    client:   Actual process.

    Usage:
    # In __main__ of executable:
        AutoRestart(path_to_file|None)
    # inside the infiniteloop:
        for i in range(_maxloop):
            AutoRestart()
            <daemon code>

    How to tell if code has changed? Store the getmtime() of sys.modules py files.
    """
    _mtimes = {}
    _maxloop = 100000000000
    _sleeptime = 1
    _flushtime = 1     # flush every second
    _is_ut = False

    def __init__(self, logfile=None):
        """
        :param logfile: Path to output logfile. None if not output
        """
        self.logfile = logfile
        self.tool = sys.argv[0]
        self.envname = 'AUTORS_%s' % os.path.basename(self.tool).upper().replace('.', '_')
        self.is_client = None

        # Check if initialized
        if self._mtimes:
            self.check_changed()       # client method, since mtimes is initialized
        else:
            self.initialize()          # top of script

    def initialize(self):
        """Called at top of the script"""
        # Determine if this is sentinel or client
        self.is_client = bool(self.envname in os.environ) or self._is_ut

        if self.is_client:
            self.init_client()
        else:
            self.main_sentinel()

    def init_client(self):
        """Client initializer"""
        for pyfile in self.get_py_files():
            self._mtimes[pyfile] = os.path.getmtime(pyfile)
        print(f'-i- AutoRestart() initialized: {len(self._mtimes)} py modules to track.')

    def check_changed(self):
        """Check if any of the pyfile have changed mtime. Exit if so."""
        sys.stdout.flush()    # force stdout flush upon check
        for pyfile, mtime in self._mtimes.items():
            if os.path.getmtime(pyfile) != mtime:
                print(f'-i- {self.tool} changed ({os.path.basename(pyfile)}. Exiting gracefully.')
                exit(0)

    def main_sentinel(self):
        """Infinite loop"""
        from gadget.shell import SystemCall
        from gadget.ut import Mock
        from gadget.files import File
        from gadget.disk import mkdirs
        from gadget.tputil import CheckerLog

        # set the environment file
        os.environ[self.envname] = str(os.getpid())
        version = CheckerLog.get_tool_sha()

        for _ in range(self._maxloop):

            # set the output file, if exist. This is safe way, so this will never error out.
            try:
                mkdirs(os.path.dirname(self.logfile))
                File(self.logfile).unlink()
                fh = open(self.logfile, 'w')   # This will get overwritten for every run
            except Exception:
                fh = Mock()

            # Save the version
            msg = f'-i- AutoRestart() Sentinel version: {version}'
            print(msg)
            fh.write(f'{msg}\n')

            # call it
            prev = time.time()
            for line in SystemCall([sys.executable, self.tool] + sys.argv[1:]).run_stream():
                print(line)    # always print stdout
                fh.write(f'{line}\n')
                if time.time() - prev > self._flushtime:      # flush every second of wall clock time so log is written in disk
                    fh.flush()
                    prev = time.time()

            fh.close()
            time.sleep(self._sleeptime)

    @classmethod
    def get_py_files(cls):
        """Iterator - return all python files used by this tool - relative to main/<caller>"""

        # get caller
        pyroot = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))     # <path>/main/<tool>

        # get all the py files
        for module in sys.modules:
            if hasattr(sys.modules[module], "__file__"):
                pyfile = sys.modules[module].__file__
                if pyfile and os.path.realpath(pyfile).startswith(pyroot):
                    yield os.path.abspath(pyfile)


class CheckMounts:
    """
    Called by make_pattern.py, since make_pattern is called at netbatch
    Will raise a special exception (ExceptionEnv) so that netbatch will retry if this exit code is set
    """

    def __init__(self):
        self.check_pylib()
        # more checks can be added in future. Just add it here

    def check_pylib(self):
        from .shell import HOSTNAME    # to support py3 imports

        try:
            result = os.listdir('/p/pde/tvpv/pylib')
        except Exception:
            print("Cannot read /p/pde/tvpv/pylib on this machine: %s" % HOSTNAME)
            exit(101)    # cannot use ExceptionEnv here since this is at import time

        numpy = 'numpy27-1.7.0'
        if numpy not in result:
            print("%s is not found in /p/pde/tvpv/pylib on this machine: %s" % (numpy, HOSTNAME))
            exit(101)    # cannot use ExceptionEnv here since this is at import time


class SysExceptionManager():
    """
    This class provides a way to group all of the functions that need to process an exception.  Different objects
    can add their own handlers via the register function of this class.  Each hook will be called with the
    arguments: etype, value, tb (see execute_hooks() for descriptions)
    Usage:  vepExceptionManager.register(myobj.my_exception_hook)
    """

    def __init__(self):
        self.exception_hook_list = []
        sys.excepthook = self.execute_hooks

    def register(self, func):
        """
        Provide a function that should be used to process exceptions that occur.  Since VEP has more than one object
        that needs to perform an operation, many hooks can be added. Each function will be passed the arguments:
        etype, value, tb.  See execute_hooks() documentation for explaination.
        :param func: Function object that should be called when an exception occurs
        """
        self.exception_hook_list.append(func)

    def execute_hooks(self, etype, value, tb):
        """
        Execute all of the exception hooks that have been registered.  Call the main system handler after.
        :param etype: exception object itself.
        :param value: list of strings that constitute the error messages of the exception
        :param tb: Traceback list if this was called from a real exception.  SystemExit doesn't have a Trace Back
        """
        for hook_func in self.exception_hook_list:
            hook_func(etype, value, tb)

        # Some simple exceptions only print the error message and leave off the traceback info.
        #  See <vep>/library/prod/errors.py for a list of exception types that use or don't use traceback
        # (Default Exceptions use trackback)
        if hasattr(etype, "without_traceback"):
            # The __excepthook__ code below works in Python2 as expected, but we cannot figure out how to get
            # Python3 to behave the same way.  Instead, it appears that this function is only doing a print (exit
            # codes are still be handled correctly) so we will just implement the print to stderr here.
            # sys.__excepthook__(etype, value, None)     # default (prints it to err)
            sys.stderr.write("%s: %s\n" % (etype.__name__, value))
        else:
            # Include the TraceBack
            sys.__excepthook__(etype, value, tb)       # default (prints it to err)


# To resolve circular reference with strmore.py
from . import strmore


def is_ut():
    """
    Detect if unit tests are running. Works with pytest, unittest, and Windows systems.
    Checks multiple indicators to ensure compatibility across different test runners and platforms.
    We want to be conservative (aka, default to False), only for exact thing we know it's unittest
    """
    # print('-d- is_ut() sys.argv value is %r' % sys.argv)      # uncomment this to see when there is new IDE

    # unix case
    if os.path.basename(sys.argv[0]).startswith('test_'):
        return True

    # pytest case
    if os.getenv('PYTEST_CURRENT_TEST', ''):
        return True

    # pycharm Chen's case
    if os.path.basename(sys.argv[-1]).startswith('_jb_unittest_'):
        return True

    return False


def is_cov():
    """Returns true if coverage is running"""
    return bool(sys.gettrace() is not None)


def is_none(var):
    """
    Returns True if var is None or NoneLikeClass object
    Used for easy replacement of "if var is None" to "if is_none(var)"

    :param var: object
    :return: bool
    """
    if var is None:
        return True
    if isinstance(var, NoneLikeClass):
        return True
    return False


vepExceptionManager = SysExceptionManager()
IS_UT = is_ut()  # Kept for legacy purposes, please use is_ut() going forward
