#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Common generic utilities/helpers, basic building-blocks that would make coding easier
"""

import os
import re
import sys
import time          # builtin
import itertools     # builtin
import platform
from functools import wraps, partial, reduce
from os.path import join
# DO NOT ADD NEW IMPORTS ==================================


# unix or not. This routine is here (and not in shell.py) since no extra import is needed (very basic)
system = platform.system()
IS_WIN = (system == 'Windows')
IS_UNIX = not IS_WIN


def _pyname():  # pragma: no cover    (unused)
    """
    Returns the name of this .py file.
    Copy this function to your module.py if you want to use it
    This function will always return the name of the module it on.

    Example:
    >>> print _pyname()
    utils
    """
    # Used in unittests
    if __name__ == '__main__':
        name = os.path.basename(sys.argv[0])
        name = name.replace(".pyc", "")
        name = name.replace(".py", "")
        return name
    else:
        return __name__  # pragma: no cover


def var_name(obj):
    """
    Returns the variable name of obj
    Example:
    >>> obj = 'abc'
    >>> var_name(obj)
    'obj'
    """
    frame = sys._getframe(1)                # caller frame.
    for area in (frame.f_globals, frame.f_locals):
        for name, value in area.items():
            if value is obj:    # identity test
                return name
    raise Exception("Cannot get variable name. It is not in locals or globals.")


class CpuElapsed:
    """
    Stopwatch for cpu-consumption that will take into consideration machine speed
    This will be used for performance benchmarks

    Usage:
    sw   = CpuElapsed()
    wall = Elapsed()
    <somecode>
    print 'sw   ', sw()
    print 'wall:', wall
    self.assertLess(sw(), 2)   # Change 2 to a number that should not exceed

    Note: The reference time is purely based on the code inside the '======' code.
    There are cases where reference time is inaccurate (see above code to check,
    by running the same test in two different machine, one slow and one fast).
    If reference time is quite off then, set reference=1.0 to remove Normalization.
    """
    reference = None      # class attribute, so that it is one time instantiate

    def __init__(self, reference=None):
        """
        Set reference=1.0 to remove Normalization
        """
        if CpuElapsed.reference is None:
            if reference is None:
                start = time.process_time()
                # =========== benchmark reference code start
                for i in range(1000):
                    j = {k: k + 1 for k in range(10000)}
                # =========== benchmark reference code end
                CpuElapsed.reference = time.process_time() - start
            else:
                CpuElapsed.reference = reference

        self.start = time.process_time()

    def elapsed(self):
        """
        Return the normalized elapsed cpu time, taking into consideration how fast machine is
        say cputime=10, reference=2 (slow machine) -> returns 5
        say cputime=5, reference=1 (fast machine)  -> returns 5 (equivalent)
        """
        return (time.process_time() - self.start) / CpuElapsed.reference  # , time.clock()-self.start, CpuElapsed.reference

    def __call__(self, *args, **kwargs):
        """to make object callable"""
        return self.elapsed()


class Elapsed:
    """
    Elapsed time / Stopwatch (Helper function on time.time())

    Example:
    sw=Elapsed()         # creates Elapsed() object
    print sw             # Displays formatted elapsed time since sw creation
    print sw(reset=True) # Displays formatted time and reset it
    secs = sw.elapsed()  # Returns the time elapsed since sw creation -or- last disp()/elapsed() call
    print sw(top=True)   # Use the time elapsed since object creation
    print sw(lastcall=True) # returns the elapsed time since last call, does not reset timer
    """
    _importstarttime = time.time()   # This is the time during import

    def __init__(self, name="", importtime=False):
        """
        Set name to a string for easy identification during disp()
        Set importtime=True to set the start time at import-time.
        """
        if importtime:
            self.start = self._importstarttime
        else:
            self.start = time.time()
        self.top = self.start
        self.last = self.start
        self.name = name

    def elapsed(self, pretty=False, reset=False, top=False, lastcall=False):
        """
        Returns elapsed time.
        Set reset=True to reset the timer.
        lastcall=True returns the elapsed time since last call, does not reset timer
        The very first timer (top) can also be accessed using top=True.
        Set pretty=True to return a formatted output

        Example:
        >>> sw1 = Elapsed()
        >>> time.sleep(1.5)
        >>> res = '%.3f' % sw1(pretty=False)
        >>> #print res =>1.501
        """
        if top and not lastcall:
            res = time.time() - self.top
        elif not top and lastcall:
            res = time.time() - self.last
        else:
            res = time.time() - self.start

        self.last = time.time()

        if reset:
            self.reset()

        if pretty:
            return "%.3f Secs" % res
        else:
            return res

    def disp(self, reset=False, top=False):
        r"""
        Prints the elapsed time.
        Set reset=True to reset the timer.
        The very first timer (top) can also be accessed using top=True.

        Example:
        >>> sw7=Elapsed(name='test')
        >>> time.sleep(0.001)
        >>> # print regex(r'test: 0.0[01]\d Secs')
        """
        if len(self.name):
            name = "%s: " % self.name
        else:
            name = ""
        print("%s%.3f Secs" % (name, self.elapsed(reset=reset, top=top)))

    def reset(self):
        """Resets the (local) timer

        Example:
        >>> sw1  = Elapsed()
        >>> time.sleep(1.5)
        >>> #sw1.reset()
        """
        self.start = time.time()
        self.last = self.start

    def __call__(self, *args, **kwargs):
        """
        Make the object callable, Returns elapsed time (pretty=True)
        Same args as elapsed()
        """
        if 'pretty' not in kwargs and len(args) == 0:
            kwargs['pretty'] = True
        return self.elapsed(*args, **kwargs)

    def __repr__(self):
        return self.elapsed(pretty=True)


class MockVar:
    """
    Context-manager that sets an attribute (or a key) to a value
    then puts it back upon __exit__()

    Example1: When Mocking an object (class or function), import the main module 'as':
        import veplb.rundir_base as rb
        with MockVar(vb, 'funcname', Mock(return_value=22)):
           # test code
        with MockVar(vb.someobj, 'methodname', Mock(side_effect=Exception)):
           # someobj.methodname() will raise exception

    Example2: change an object-attribute or dict-key and put it back once done
       lb.var1='oldvalue'
       with MockVar(lb, 'var1', 'newvalue'):
          <do something with lb.var1, it has 'newvalue'>
       # lb.var1 is back to 'oldvalue' here

    Example3: reroute stdout
       from cStringIO import StringIO
       with MockVar(sys, 'stdout', StringIO()) as p:
            print 'Hello'
            self.assertEqual(p.getvalue(), 'Hello\n')
       # To empty p:
       p.seek(0)
       p.truncate()

    Example4: reroute stdin
        input = '<string_you_want_to_type_in_keyboard_as_user_input>'
        with MockVar(sys, 'stdin', StringIO(input)):
            res = func_reads_from_stdin()    # function returns keyboard intake
            # test correctness of res

    Example5: To use as a decorator in a test function:
        @with_(MockVar, sys, 'argv', ['newvalue'])
        def test_mytest(test):
            # testcode

        # Above is the same as
        def test_mytest(test):
            with MockVar(sys, 'argv', ['newvalue']):
                # testcode

    Example6: To use mockif:
        def test_mytest(test):
            with MockVar(obj, "routine", Mock(return_value=98), mockif=lambda s,x,y: x==1):
                # testcase.   <s,x,y> above should be the same args as: routine(self,x,y)
    """
    __slots__ = "_obj _attr _isdict _value _orig _mockif".split()
    delete = dict()      # unique object. Used as value=MockVar.delete to identify delete this attribute

    def __init__(self, obj, attribute, value, isdict=None, isattr=None, mockif=None):  # Set value=MockVar.delete to delete that attribute/key
        """
        obj is the source object
        attribute is the attribute name or key name
        Set value=MockVar.delete to delete that attribute/key
        isdict=True will force obj to be a dictionary
        isattr=True will force obj to be an object
        mockif=lambda <args>: <expr>   # will Mock only if this is true.
            # <args> should be the same as <args> of Mocked routine.
            # This is conditional mock for cases where function to be mocked is called several times.
            # Do not use "*args, **kwargs" in lambda, since caller can either use positional or kwargs.
        If isdict and isattr is not specified, then autkomatic detection via dict isinstance
        """

        from .strmore import str_isword
        self._obj = obj
        self._attr = attribute
        self._isdict = self._id_isdict(obj, isdict, isattr)
        self._value = value
        self._orig = None    # populated in _assign_dict(), _assign_attr()
        self._mockif = mockif

        # check attribute, because this cause unnecessary code debug
        if not str_isword(attribute):
            raise ValueError("MockVar usage error: Attribute to mock [%s] contain non-alphanumeric char. "
                             "This should only contain the final attribute/variable name which is "
                             "alphanumeric only. Fix your MockVar code. See traceback." % attribute)

    def _assign_dict(self):
        """Dictionary - Store orig value and replace it"""
        # assign orig value
        if self._attr in self._obj:
            self._orig = self._obj[self._attr]
        else:
            self._orig = self.delete    # it does not exist

        # assign object
        if self._value is self.delete:
            if self._attr in self._obj:
                del self._obj[self._attr]
        else:
            self._obj[self._attr] = self._value

    def _assign_attr(self):
        """Dictionary - Store orig value and replace it"""
        # assign orig value
        if hasattr(self._obj, self._attr):
            if self._attr in self._obj.__dict__:
                self._orig = self._obj.__dict__[self._attr]      # needed for classmethod() attributes
            else:
                self._orig = getattr(self._obj, self._attr)
        else:
            self._orig = self.delete   # it does not exist

        # do conditional mock
        if self._mockif is not None:
            def wrap(*args, **kwargs):
                if not self._mockif(*args, **kwargs):
                    return self._orig(*args, **kwargs)   # do orig
                else:
                    return self._value(*args, **kwargs)
            overwrite = wrap
        else:
            overwrite = self._value

        # assign object
        if self._value is self.delete:
            if hasattr(self._obj, self._attr):
                delattr(self._obj, self._attr)
        else:
            setattr(self._obj, self._attr, overwrite)

    def _id_isdict(self, obj, isdict, isattr):
        # isdict autodetection
        if obj is os.environ:
            return True   # os.environ should be isdict=True

        if isdict is None and isattr is None:
            return isinstance(obj, dict)
        else:
            if isdict and isattr:
                raise Exception("Cannot set both isdict=True and isattr=True")
            if isdict:
                return True
            else:
                return False

    def __exit__(self, *arg):
        """Put back the original value"""
        if self._isdict:
            if self._orig is self.delete:           # does original key exist?
                if self._value is not self.delete:
                    if self._attr in self._obj:     # item must exist to be deleted
                        del self._obj[self._attr]
            else:
                self._obj[self._attr] = self._orig

        else:
            if self._orig is self.delete:                # does original attribute exist?
                if self._value is not self.delete:
                    if hasattr(self._obj, self._attr):   # item must exist to be deleted
                        delattr(self._obj, self._attr)
            else:
                setattr(self._obj, self._attr, self._orig)

    def __enter__(self):
        """Do the mocking"""
        if self._isdict:
            self._assign_dict()
        else:
            self._assign_attr()

        return(self._value)     # Do not return Mock object. Return the value, for use with stdout Mocks.


# Do not use below: use try: ... finally: ... block instead
# class AnyContext:
#    '''
#    Executes callable upon block exit.
#    Useful when you want to delete something or do some cleanup when with block is done.
#    Example:
#       with AnyContext(shutil.rmtree, dir_to_delete):
#           <somecode>
#    '''
#    def __init__(self, func, *args, **kwargs):
#        '''Store the callable and the args'''
#        self.func   = func
#        self.args   = args
#        self.kwargs = kwargs
#
#    def __exit__(self, *arg):
#        self.func(*self.args, **self.kwargs)
#
#    def __enter__(self):
#        return(self)


def israise(exc_class, func, *args, **kwargs):
    """
    Returns True if callable(*args, **kwargs) raises exc_class exception.
    False otherwise
    To catch all exceptions, use 'Exception' in exc_class.

    Example:
    >>> def foo(arg1):
    ...     raise IOError('some error')
    >>> print israise(IOError, foo, arg1=21)
    True
    """
    try:
        func(*args, **kwargs)
        return False
    except exc_class:
        return True


def raise_if(expr, exc_class, message):
    """
    raise exc_class(message) if expr is True.
    This is similar to assert statement, except that it is not affected by python optimization flag.
    This is useful on safety-checks where coverage on Exception case cannot be tested.
    This also checks validity of message specially with formattings (e.g. missing %s arguments).
    Use only when coverage is not needed on the expr.

    Example:
    >>> import re
    >>> print raise_if(False, Exception, 'message')
    None

    >>> #raise_if(False, Exception, 'message').str() => returns exception
    """
    if expr:
        raise exc_class(message)


def count_iter(iterable):
    """
    Count the number of items in an iterable. Returns the count
    Consume it by not reading it into memory.
    Pure-C implementation.
    Copied from: http://stackoverflow.com/questions/3345785/getting-number-of-elements-in-an-iterator-in-python

    Example:
    >>> print count_iter(iter(xrange(20)))
    20
    """
    from collections import deque

    counter = itertools.count()
    deque(zip(iterable, counter), maxlen=0)     # (consume at C speed)
    return next(counter)


def consume_iter(func, iterable):
    """
    Consume an iterable and feed it into func.
    This is pure-C implementation (very efficient) as long as iterable
    is built-in (filehandle or array or dict) and func is built-in.
    """
    from collections import deque

    deque(map(func, iterable), maxlen=0)


def uniqlist(seq):
    """
    Make a list unique, while preserving the order.
    It returns a unique list. It does not modify the original list.
    If order does not need to be preserved, then use:
       set(seq)

    Example:
    >>> print uniqlist([])
    []

    >>> print uniqlist([1])
    [1]

    >>> print uniqlist([10,5,1,4,2,1,2,10,4,5])
    [10, 5, 1, 4, 2]

    >>> print uniqlist([1,1,1,2,2,2,3,3,3])
    [1, 2, 3]
    """
    # Converting this function to cython (the entire function) is 25% faster
    myset = set()
    mysetadd = myset.add
    return [x for x in seq if x not in myset and not mysetadd(x)]


def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm.

    Example:
    >>> print gcd(2,6)
    2
    """
    while b:
        a, b = b, a % b
    return a


def gcdm(a):
    """
    Get the gcd for a list of numbers
    :param a: list of numbers
    :return:
    """
    return reduce(gcd, a)


def lcm(a, b):
    """Return lowest common multiple.

    Example:
    >>> print lcm(2,3)
    6
    """
    return a * b // gcd(a, b)


def lcmm(a):
    """Return lcm of a list.

    Example:
    >>> print lcmm([1,2,6])
    6
    """
    return reduce(lcm, a)


def hex_to_bin(hex_data, hex_size=None):
    """Takes a string of hex characters and converts to binary

    Example:
    >>> print hex_to_bin('0FF15A')
    000011111111000101011010
    """
    # Saw a similar example on stackoverflow
    hex_data = hex_data.replace(" ", "")
    if not hex_size:
        hex_size = len(hex_data) * 4

    bin_data = bin(int(hex_data, 16))[2:].zfill(hex_size)
    return bin_data


def get_sec(time_str):
    """
    Convert a string string with 'h', 'm', or 's' in it to seconds.
    Example Input:
        1h:10m:10s  => 3600 + 600 + 10 => 4210
        2h          => 3600 * 2 => 7200
        1d          => 3600 * 24 => 86400
        2m:2s       => 60 * 2 + 2 => 122
    :param time_str:
    :type time_str: str
    :return: time in seconds
    :rtype: int
    """
    err_msg = "Unable to convert %s to seconds. Valid Formats: 1d, 2h, 1h:2m:3s, 2m:1s, etc" % time_str
    if not re.search(r'^[\dhdms:]+$', time_str):
        raise ValueError(err_msg)

    seconds = 0
    multiplier = {'d': 24 * 60 * 60, 'h': 60 * 60, 'm': 60, 's': 1}
    try:
        # See if each field contains a multiplier and sum up the number of seconds
        for field in time_str.split(':'):
            found_multiplier = False
            for hms in multiplier.keys():
                if hms in field:
                    found_multiplier = True
                    seconds += int(field.replace(hms, '')) * multiplier[hms]
                    break

            # No multiplier provided, assume just secounds
            if not found_multiplier:
                seconds += int(field)

    except (ValueError, KeyError):
        raise ValueError(err_msg)

    return seconds


def vr(string):                  # Unittested
    """
    vr-variable replace (local and global). Wrapper (save-on-typing) for embedding
    [local or global] variable in a text. Use vrlocal() for local variable only
    since it is faster.
    This is also known as 'variable interpolation'.
    Uses str.format syntax.
    NOTE: Do not use this in vep libraries since eclipse will not know the variable is used
          and Cython does not work with it.

    Example:
    print vrg('Pat {pattern}; {comment}')   # Print 'Pat '+pattern+'; '+comment
    res = vrg('Pat {pattern};')             # Returns a string

    >>> globalvar_a=123
    >>> globalvar_b=456
    >>> print vr('a={globalvar_a} b={globalvar_b}')
    a=123 b=456
    """
    # Performance: vrg() is ~250,000 per second (3 var replacements)
    # This is optimized. Adding the parse {} in text then conditionally get globals is slower (2.4 vs 1.3 sec)

    # Get the local and global variables of the frame
    frame = sys._getframe(1)                # caller frame.
    hh = {}
    hh.update(frame.f_globals)
    hh.update(frame.f_locals)     # f_locals is a dictionary

    return string.format(**hh)


def vrlocal(string):                  # Unittested
    """
    vr-variable replace local only.
    Faster version of vr() since it will only get local variables.
    See vr() for details.

    Example:
    >>> globalvar_a=123
    >>> globalvar_b=456
    >>> print vrlocal('a={globalvar_a} b={globalvar_b}')
    a=123 b=456

    >>> print vrlocal('{globalvar_a} {globalvar_a} {__name__}')
    123 123 utils

    >>> class foo:
    ...    def __init__(self,val):
    ...        self.val=val
    >>> obj = foo('FUN')
    >>> print vrlocal('{globalvar_a}={obj.val}')
    123=FUN
    """
    # Performance: vr() is ~800,000 per second (3 var replacements)

    # Get the local variables of the frame only
    frame = sys._getframe(1)                # caller frame.
    hh = frame.f_locals

    return string.format(**hh)


def isany(shortlist, longlist):  # unittested
    """
    Checks if any items in shortlist exists in longlist.
    This is more efficient (and less memory) version of:
       if any((True for ky in shortlist if ky in longlist))):

    Example:
       if isany('()<>[]', 'text(with)parenthesis')
    For very large set of data to check, use set() instead:
       if len(set(shortlist) & set(longlist))>0:

    >>> print  isany('abc', 'dddeeeb')
    True

    >>> print isany(['blue','green'], 'yellow_green')
    True

    >>> print isany('abc', 'dddeeef')
    False

    >>> print isany('a', 'f')
    False

    >>> print isany({str,int}, {str,int,long,object,None})
    True

    >>> print isany({int}, {str,long,object,None})
    False

    >>> dd = {'mappinglist':1, 'mappingbits':2, 'abc':3}
    >>> print isany('mappinglist mappingbits'.split(), dd)
    True

    >>> print isany('appinglist appingbits'.split(), dd)
    False
    """
    for ky in shortlist:
        if ky in longlist:
            return True
    return False

# ~350k calls per second - @timethis decorator


def timethis(func):
    """
    Decorator to time a particular function. Simply add '@timethis' before
    the function definition.

    Example:
    >>> @timethis
    ... def myfunc():
    ...   time.sleep(4.05)
    >>> #myfunc()   => utils.myfunc : 4.052 Secs
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        end = time.time()
        print('%s.%s : %.3f Secs' % (func.__module__, func.__name__, end - start))
        return r
    return wrapper


def with_(context, *c_args, **c_kwargs):
    """
    Decorator that acts just like a 'with' statement.
    The with block is applied to the entire function.
    Purpose is to reduces the *indent* associated to with-block inside the unittest func.
    This decorator only works if the context manager does not return anything.
    This decorator works only at function level, not on a class level.

    Example:
        @with_(Chdir, somedir)
        def test_myfunc(self):
            <somecode>

    # Above is the same as:
        def test_myfunc(self):
            with Chdir(somedir):
                <somecode>

    To use with TempDir:
        @with_(TempDir, chdir=True)
        def test_myfunc(self):
            tdir = os.getcwd()
    """
    def wrapper(f):
        def new_f(*args, **kwds):
            with context(*c_args, **c_kwargs):
                return f(*args, **kwds)
        new_f.__name__ = f.__name__
        return new_f
    return wrapper


def funclike(cls):
    """
    Class decorator to make the class act as a function.
    The class is instantiated everytime the *function* is called.

    Example:
       @funclike
       class someclass:
          def __init__(self, args):
              # some code
          def __call__(self):
              return <somevalue>

       print someclass(arg1)   # displays <somevalue>

       # Traditionionally, without this decorator:
       obj = someclass(arg1)   # instantiate first
       print obj()             # displays <somevalue>

    To inherit the original class:
       class InheritedClass(someclass(returnclass=True)):
           # code
    """
    # Check if given class has __call__(). This is required since __call__() returns the value.
    if '__call__' not in dir(cls):
        raise Exception("Class %s does not have __call__() method. "
                        "This is required for funclike() decorator." % cls)

    def getinstance(*args, **kwargs):
        if 'returnclass' in kwargs and kwargs['returnclass']:   # For inheritance
            return cls
        return cls(*args, **kwargs).__call__()

    return getinstance


def singleton_instantiate(*args, **kwargs):
    """
    Class decorator to *instantiate* the class as a singleton.
    The classname becomes the instantiated object

    Example:
       @singleton_instantiate(<args_to_init>)    # This will make class name below an instantiated object (singleton)
       class someclass:   # must be small-case (instantiated obj) naming convention
          def __init__(self, args):
              # some code
          def __call__(self):
              return <somevalue>
          def method1(self):
              # somecode

       print someclass(arg1)   # displays <somevalue>, calls __call__()
       print someclass.method1()

       # Traditionionally, without this decorator:
       someclass = SomeClass()    # instantiate first
       print someclass()          # displays <somevalue>

    Notes:
    1. To inherit the original class:
       class InheritedClass(someclass.__class__):   # since someclass is the instantiated obj
           # code
    2. To use @singleton_instantiate in which first argument is a class name:
       @singleton_instantiate(<classvar>, _nocheck=True)
       class MyClass:
          # code
    """
    # Code is copied from below link as a starting point, then enhanced.
    #    http://www.python.org/dev/peps/pep-0318/#examples as

    # error out if () is forgotten by user
    if not ('_nocheck' in kwargs and kwargs['_nocheck']):
        if len(kwargs) == 0 and len(args) == 1 and isinstance(args[0], type):
            raise Exception("singleton decorator must be used with arguments, "
                            "ie. '@singleton_instantiate()'")
    if '_nocheck' in kwargs:
        del kwargs['_nocheck']

    def getinstance(cls):
        obj = cls(*args, **kwargs)    # this is executed once upon python bootup
        return obj

    return getinstance


def check_slots(func):
    """
    Decorator to check if __slots__ is taking effect in a class.
    Decorate in __init__() in base and all sub-classes.
    This routine will raise exception if __slots__ is not implemented.
    Python requires that base class and all inherited classes must have __slots__
    defined for __slots__ to take effect.
    NOTE: Consider the performance hit when using this decorator.

    Usage:
       @check_slots
       def __init__():
           <code>
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        self = args[0]
        try:
            self._newattribute_SUREnotEXIST = True
            raise Exception("__slots__ is not defined in %s. __slots__ is required to be defined" %
                            self.__class__.__name__)
        except AttributeError:
            pass   # good

    return wrapper


def iif(expr, trueval, falseval):
    """
    Simple ternary equivalent function: (expr ? trueval : falseval)
    WARNING: For quality/code-coverage reasons, avoid using this.
    WARNING2: Using this will force evaluation of trueval and falseval.
              Unlike in traditional if statement, trueval is only evaluated upon true statement.
              Example: iif(OPT.email, OPT.email.split(), ['username'])
              Above will fail on cases where OPT.email is None, since OPT.email.split() is still evaluated.

    Example:
    >>> iif(True,1,2)
    1

    >>> iif(False,1,2)
    2
    """
    if expr:
        return trueval
    else:
        return falseval


def ifnone(var, othervar):
    """Checks if var is None. if it is, then return othervar, else return var

    Example:
    >>> print ifnone(1,2)
    1
    >>> print ifnone(None,2)
    2
    """
    if var is None:
        return othervar
    else:
        return var


def switch(casevar, dd, default=None):
    """
    A Simple dictionary-based switch-like assignment helper.

    Example:
       var=<somevalue>
       if var=='a':
          action = 61
       elif var=='b':
          action = 95
       elif var=='c':
          action = myfunc(23)

    Above will translate to:
       dd = DictDot()
       dd.a = 6if(
       dd.b = 95
       dd.c = partial(myfunc, 23)   # partial is from functools
       action = switch(var, dd)

    >>> from dictmore import DictDot
    >>> dd = DictDot()
    >>> dd.a = 10
    >>> dd.b = 20
    >>> dd.c = partial(int, '30')
    >>> print switch('a', dd)
    10
    >>> print switch('b', dd)
    20
    >>> print switch('c', dd)
    30
    >>> print switch('d', dd)
    None
    >>> print switch('d', dd, default=100)
    100

    """
    if casevar not in dd:
        return default

    if isinstance(dd[casevar], partial):
        return dd[casevar]()    # function

    return dd[casevar]   # plain value


# TODO: obsolete this, replace with strmore.md5()
# TODO: replace vcdread.py to use md5() also, instead of hash()
def hash_dig(string):
    """Return a 20 digit string on the hash() equivalent of string (no negative)

    Example:
    >>> print hash_dig(0)
    000000000000000000000

    >>> print hash_dig(10)
    000000000000000000010

    >>> print hash_dig(-10)
    100000000000000000010

    >>> print hash_dig('abc')
    001453079729188098211
    """
    hh = hash(string)
    if hh < 0:
        return "1" + str(abs(hh)).zfill(20)
    else:
        return "0" + str(hh).zfill(20)


def send_mail(fromemail, to_list, subject, message, html=False, _smtp=None, cc_list=None, text_file_attachment=None):
    """
    Send email function
    fromemail is the return email string.
    to_list and cc_list can be a string or a list. If string, delimited by space, comma or semi-colon
    to_list can either be username or full email.
    message is the message text.
    text_file_attachment is a list of text file paths. These files will be attached to mail.

    Example:
    >>> #send_mail('from_me@abc.com', 'to_you@def.com', 'subject from me', 'mesg')
    >>> #send_mail('from_me@abc.com', ['to_you@def.com', 'to_them@def.com'], 'subject from me', 'test message')
    """
    from gadget.helperclass import IS_UT  # do not put this at top of file.    # to support py3 imports
    from socket import error
    from smtplib import SMTP
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    if _smtp is None:
        _smtp = SMTP
    if isinstance(to_list, str):
        to_list = to_list.replace(',', ' ').replace(';', ' ').split()

    if cc_list is None:
        cc_list = list()
    elif isinstance(cc_list, str):
        cc_list = cc_list.replace(',', ' ').replace(';', ' ').split()

    if not to_list:  # empty(None or []), so do nothing. Used in unittests
        return to_list

    if html:
        msg = MIMEText(message, 'html')
    elif text_file_attachment:
        msg = MIMEMultipart('related')
        msg_text = MIMEText(message, 'plain')
        msg.attach(msg_text)
        _attach_files(msg, text_file_attachment)
    else:
        msg = MIMEText(message)

    msg['Subject'] = subject
    msg['To'] = ", ".join(to_list)
    msg['From'] = fromemail
    if len(cc_list) > 0:
        msg['Cc'] = ", ".join(cc_list)

    # do not proceed if it is unittests
    if IS_UT:
        return to_list + cc_list

    # send the real mail
    # NOTE:  The underlying mail object only creates a mail for addresses passed in the "to_addrs" input. Addresses
    #   in the CC list of the body of the message are not actually included in the people sent to.  They are simply
    #   reported as a list of CC addresses in the final email, but they never receive a copy of the mail themselves.
    #   This is why the to_list and cc_list need to be combined at this stage.  This will not affect how the mail
    #   appears in the inbox (To: only contains to_list addrs, CC: properly shows cc_list) but it will ensure that
    #   all intended recipients get the mail as expected.
    try:
        mail = _smtp("localhost")
        mail.sendmail(fromemail, to_list + cc_list, msg.as_string())
        mail.quit()
    except error as e:
        raise error("send_mail() failed. To: %r Subject: %r Error: %s\nSuggestion: Try another machine."
                    "" % (to_list, subject, e))

    return to_list + cc_list  # used by unittest


def _attach_files(msg, text_files):
    from email.mime.text import MIMEText
    for txt_file in text_files:
        try:
            file_name = os.path.basename(txt_file)
            text_file = open(txt_file, 'r')
            attachment = MIMEText(text_file.read())
            text_file.close()
            attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
            msg.attach(attachment)
        except IOError as e:
            raise IOError("Failed to attach file at {}.\nError: {}".format(txt_file, e))


def testonly_func(which):
    """Test only routine for MockVar"""
    if which == 0:
        return "RESULT" + join("A")
    if which == 1:
        return "RESULT" + os.path.join("A")
    if which == 2:
        return "RESULT%s" % Elapsed()


def get_free_port():
    """
    Finds open port on localhost.
    @rtype: int
    @return: port number
    """
    import socket
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind(("", 0))
    port = temporary_socket.getsockname()[1]
    temporary_socket.close()
    return port


def chunker(sequence, chunk_size):
    """
    Iterate over <sequence> in <chunk_size> batches.

    Ex. for item in chunker('ABCDEF', 3):
        print item
    >> 'ABC'
    >> 'DEF'

    :param sequence: Any string, list, set, or tuple.
    :param chunk_size: A positive integer.
    :returns: The next <chunk_size> elements of <sequence>.
    """

    if chunk_size < 1:
        raise Exception('Given chunk_size must be a positive integer!')

    return (sequence[position:position + chunk_size] for position in range(0, len(sequence), chunk_size))


def convert_to_utc(date):
    """
    Convert a local time datetime object into a UTC datetime object.
    :param date: A datetime object in local time to be converted to a UTC version of datetime
    :return: a new datetime object representing the UTC version of the local time given
    :raises: Exception() if a non-datetime object is passed in

    Usage:
    date_format = "%Y-%m-%d %H:%M:%S"                               # input_date_string is in this format
    run_date = datetime.strptime(input_str_localtime, date_format)  # convert to datetime object
    utc_date = convert_to_utc(run_date)
    output_str_utc = utc_date.strftime(date_format)                 # convert to string
    """
    import datetime
    if not isinstance(date, datetime.datetime):
        raise Exception('Cannot convert non-datetime object to UTC')

    # convert the structure to a time_tuple structure
    t_day = date.timetuple()

    # convert time_tuple to local seconds (int)
    today_s = time.mktime(t_day)

    # convert local seconds to gm time tuple to gm seconds
    gm_sec = time.mktime(time.gmtime(today_s))

    # then finally, convert gm seconds to datetime
    gm_date = datetime.datetime.fromtimestamp(gm_sec)

    return gm_date


def all_match_except(object1, object2, equal, non_equal):
    """
    Given two objects, return True if the value of attributes specified in 'all_equal'
    are equal to each other and the value of attributes specified in 'non_equal' are
    all different.

    :param non_equal: Iterable (list, tuple, set) containing attribute names that must be non-equal.
    :param object1: Any valid class instance with public attributes.
    :type object1: Any valid class object with public attributes.
    :param object2: Any valid class instance with public attributes.
    :type object2: Any valid class object with public attributes.
    :param equal: Iterable (list, tuple, set) containing attribute names that must be equal.
    :type equal: Iterable type (list, tuple, set, etc.)
    :param non_equal: Iterable containing attribute names that must be non-equal.
    :type non_equal: Iterable type (list, tuple, set, etc.)
    :return: True if attributes specified in all_equal are equivalent, and
    the attributes in all_false are not equal.
    :rtype: Boolean
    """

    all_required_true = all(getattr(object1, attr) == getattr(object2, attr) for attr in equal)
    all_required_false = all(getattr(object1, attr) != getattr(object2, attr) for attr in non_equal)

    return all_required_true and all_required_false


def py2_cmp(x, y):
    """
    Implements Python 2 version of cmp() function. For Py2 -> Py3
    compatibility
    :param x:
    :param y:
    :return:
    """

    return (x > y) - (x < y)

#
# Below are routines copied from python3.3 standard lib:
# /usr/intel/pkgs/python/3.3.1/lib/python3.3/types.py
# Remove this once we move to python3.3. It is used to create a class dynamically.
#

# --- from python3 ---


def new_class(name, bases=(), kwds=None, exec_body=None):  # pragma: no cover - standard lib
    """
    Create a class object dynamically using the appropriate metaclass.
    Usage:
        listclass = [One,Two]
        Three = new_class("Three", tuple(listclass))
        # Note: The variable name and the first argument string must match for consistency.
        # Above is equilvalent to:  class Three(One,Two): pass
    """
    meta, ns, kwds = prepare_class(name, bases, kwds)
    if exec_body is not None:
        exec_body(ns)
    return meta(name, bases, ns, **kwds)


def prepare_class(name, bases=(), kwds=None):  # pragma: no cover - standard lib
    """Call the __prepare__ method of the appropriate metaclass.

    Returns (metaclass, namespace, kwds) as a 3-tuple

    *metaclass* is the appropriate metaclass
    *namespace* is the prepared class namespace
    *kwds* is an updated copy of the passed in kwds argument with any
    'metaclass' entry removed. If no kwds argument is passed in, this will
    be an empty dict.
    """
    if kwds is None:
        kwds = {}
    else:
        kwds = dict(kwds)  # Don't alter the provided mapping
    if 'metaclass' in kwds:
        meta = kwds.pop('metaclass')
    else:
        if bases:
            meta = type(bases[0])
        else:
            meta = type
    if isinstance(meta, type):
        # when meta is a type, we first determine the most-derived metaclass
        # instead of invoking the initial candidate directly
        meta = _calculate_meta(meta, bases)
    if hasattr(meta, '__prepare__'):
        ns = meta.__prepare__(name, bases, **kwds)
    else:
        ns = {}
    return meta, ns, kwds


def _calculate_meta(meta, bases):  # pragma: no cover - standard lib
    """Calculate the most derived metaclass."""
    winner = meta
    for base in bases:
        base_meta = type(base)
        if issubclass(winner, base_meta):
            continue
        if issubclass(base_meta, winner):
            winner = base_meta
            continue
        # else:
        raise TypeError("metaclass conflict: "
                        "the metaclass of a derived class "
                        "must be a (non-strict) subclass "
                        "of the metaclasses of all its bases")
    return winner

#
# End of Copy
#


class CacheThis:
    """
    Generic decorator class to cache functions. In the example below, the calls to myFunc will be cahced by this class.
    The first time myFunc is called the normal algorithm inside myFunc will be called. Each subsequent call to myFunc
    (with the same parameters supplied) will return the cached value, saving the runtime from redundant calls to myFunc.

    Usage:
        Inside the target class, create an instance of this (can be a class var):
            my_cache = CacheThis()

        For functions inside the class that you want to cache, decorate with the instance:
            @my_cache
            def my_func(self, arg1, arg2):
                # my_func algo, can return anything (single value, tuple, dictionary, list etc)
                # redundant calls to my_func will be returned from my_cache
                return my_func_return_value

        To clear the cache:
            my_cache.clear_cache()
    """

    def __init__(self):
        self.cache = {}         # key = func name + args/kwargs, value = return value of function

    def _build_key(self, func, *args, **kwargs):
        """Build cache key name using function and args/kwargs"""
        key1 = str(func)
        key2 = str(args)
        key3 = ','.join("%s=%s" % (x, kwargs[x]) for x in sorted(kwargs))
        return (key1, key2, key3)

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            key = self._build_key(f, args, kwargs)

            # if call has been cached, return value from each
            if key in self.cache:
                return self.cache[key]

            # else run the real function, set cache entry and return function value
            value = f(*args, **kwargs)
            self.cache[key] = value
            return value

        return wrapper

    def clear_cache(self):
        self.cache = {}


class NULL:
    """
    NULL / dummy object
    Usage: Similar to None, use NULL when you want to differentiate between None vs NULL
           if some_var is NULL:
               <code>
    """
    pass


def h():  # pragma: no cover  - this is not unittested
    """Display the history in python IDE"""
    import readline
    for i in range(readline.get_current_history_length()):
        print(readline.get_history_item(i))


def get_caller_lno(frame_offset=2):
    """
    Get the line number of the calling function using sys._getframe (faster than traceback).

    :param frame_offset: How many frames back to look (default 2 = caller's caller)
    :return: Line number (int)

    Example:
        # In __init__, get caller's line number (2 frames back):
        self.id_lno = get_caller_lno()  # equivalent to sys._getframe(2).f_lineno

        # 1 frame back (immediate caller):
        lno = get_caller_lno(1)  # equivalent to sys._getframe(1).f_lineno
    """
    return sys._getframe(frame_offset).f_lineno
