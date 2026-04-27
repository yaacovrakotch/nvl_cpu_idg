#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Additional Dictionary Capabilities/Library

Derived Dictionary Objects:
   dd = DictConfig()       # Dot-like, no-duplicate-dot-assignment, SAME_AS() capability, no duplicate entry
   dd = TVPVConfigDict()   # Auto-vivification of DictConfig()
   dd = autodict()         # Auto-vivification of normal dict()
   dd = DictValues()       # dict() that stores the values in a dictionary for fast access
   dd = DictDot()          # dict() with Dot-like accessibility (one-level)
   dd = DictDotRO()        # DictDot() that is Read-Only
   dd = DefaultDictDot()   # defaultdict() with Dot-like accessibility (one-level)
   dd = autoDictDot()      # Auto-vivification of DefaultDictDot()
   dd = NamedSeq()         # Similar to namedtuple. Returns a DictConfig().

Helper functions: (d is some_dict)
   dd    = recurse2dict(d)               # Converts some_dict to built-in dictionary,
                                         #   for use in marshal
   dd    = attr2dict(obj)                # Converts attributes of a class to dict
   obj   = dict2attr(dd)                 # returns an object with attributes have values as dict
   key   = getkeyfromval(d, val)         # Returns the key of first occurrence found
                                         #   of val in some_dict
   iter  = iterkeyfromval(d, val)        # Iterator to get all keys, given some_dict
                                         #   and the val
   iter  = iterpartialkey(d, partialkey) # Iterator, Recursively find the partialkey,
                                         #   separate by dot, returns the value. Used in xmls.
   k,v   = iter_dot_items(d)               # Iterator, Recursively returns the key,value
                                         #   tuple of a multi-level dictionary. key is concat by dot.
   dd    = key_remap(d, alias_dict)      # Returns a dictionary, with key names remapped
                                         #   by alias_dictionary
   dd    = reverse_keyval(d, [keyindict]) # Reverses the key:value to value:key
   iter  = flatdict(d)                   # Iterator, Returns a dot-flattened dict output
   iter  = iter_levels(d, levels)        # Iterator levels
   dd    = copy_configdict(d)            # Returns a copy of d (TVPVConfigDict) with AUTO_OFF()
   dd    = delkeys(d, seq_of_keys_to_del) # Returns a dictionary with seq_of_keys_removed
   bool  = key_exist(d, *keys)           # returns if multi-level keys exist
   v     = get_multi_level(d, *keys)     # returns value of multi-level keys
   v     = firstitem(seq_or_dict)        # returns first item of seq or dict
   iter  = chunkdict(dict, limit)        # returns an iterator, splits dictionary if <limit> number of keys
   iter  = keys_atlevel(dd, n)           # returns an iterator, all keys at n level (multi-level)
   list  = find_dot_items(dd, key)       # returns sorted list of unique values given key. Useful for xml data.
   assign_multi_level(d, keys, val)      # assign d[level1][level2][etc] = val
   dict_merge(dct, merge_dct)            # recursively merge_dct keys to dct
   remove_none_values(d)                 # remove items which have None value

XML related:
   dd                 = xmlfunc.xml2dict('file'|elementtree_object)
   elementtree_object = xmlfunc.dict2xml(some_dict)
   stringout          = xmlfunc.dict2xml_str(some_dict)

It is suggested to import this as the last so that collections std lib are imported as *

Note1: On 'Dot' enabled dictionaries, methods/functions come in first.

"""

from collections import defaultdict
from collections.abc import Mapping
from keyword import iskeyword
from .printmore import Dumper
from functools import partial
import re

# --- built in types ---

BUILTIN_TYPES_SIMPLE = {str, str, bytearray, int, float, int, complex, bool}
BUILTIN_TYPES_LIST = {list, tuple, set, frozenset}
BUILTIN_TYPES_DICT = {dict}
BUILTIN_TYPES_ALL = BUILTIN_TYPES_SIMPLE | BUILTIN_TYPES_LIST | BUILTIN_TYPES_DICT

# --- classes ---


class DictConfig(defaultdict):
    """
    Adds object-like functionality to collections.defaultdict
    Object attributes and Dictionary are stored in the Dictionary space

    *Same as* usage example:
       vrev = TVPVConfigDict()
       vrev.vrevPA0.vectype = "Value"
       vrev.vrevPA1.SAME_AS(vrev.vrevPA0)   # Set vrevPA1 to be same_as vrevPA0
    """

    # Performance for 10,000,000 accesses via []:  Summary: Pretty good
    # TVPVConfigDict(): write:1.5-1.6 sec,   read=2.2 sec  [slower by half, it's ok, good enough]
    # {}:               write:1.5 sec,       read=1.2 sec
    #
    # Performance for 10,000,000 accesses via ".": Summary: Good enough
    # TVPVConfigDict(): write:7.6 sec,   read=1.6 sec
    # {}:               write:1.0 sec,   read=0.6 sec
    #
    # Performance using config_naming.py: 153K lines (python lines) per second on plxc5908.
    #                                     This is 2.7M interpreted lines total.
    #
    # Note: to make this object "lockable", add a "self.locked=True/False", then add
    #       if code in __setitem__() and __setattr__(). Also, recursively set self.locked
    #       to all the objects underneat.

    def __init__(self, initdict=None):
        defaultdict.__setattr__(self, "_configentry", set())
        defaultdict.__init__(self, initdict)

    def AUTO_OFF(self):
        """Disable autovivification - deep"""
        defaultdict.__setattr__(self, "default_factory", None)
        for value in self.values():
            tt = type(value)
            if tt is DictConfig:
                value.AUTO_OFF()

    def __getattr__(self, item):
        #        if item=="__setstate__":
        #            defaultdict.__getattr__(self, item)
        try:
            return self[item]    # This will raise KeyError if key is not found
        except KeyError:         # In python3, only AttributeError is used by hasattr().
            raise AttributeError("%r" % item)

    def OVERRIDE(self, item, value):
        """Given a key and value, override it. Useful for unittests"""
        self.__setitem__(item, value)

    def __setattr__(self, item, value):
        cfgentry = self._configentry
        if item in cfgentry:
            if self[item] is value:
                return                     # Do nothing, it is the same
            ErrMsg = "Key [" + item + "] already has value " + \
                     repr(repr(self[item]).rstrip().split('\n')) + \
                     ". This can be a config error. There should be no duplicate during assignment!"
            raise KeyError(ErrMsg)

        cfgentry.add(item)
        self[item] = value

    def _recursedict(self):   # iterator
        """Iterator for __repr__, returns a string"""
        for item, value in self.items():
            if isinstance(value, DictConfig):
                for nitem, nvalue in value._recursedict():
                    yield item + "." + nitem, nvalue
            else:
                yield item, value

    def __repr__(self):
        """Return the display, just like a dictionary display"""
        return repr(recurse2dict(self))

    def PRETTY(self):
        """
        Return the following string equivalent of dictionary:
           key1.key2.key3 = value1
           key4.key5.key6 = value2
           key7.key8 = value3
        """
        sorted_iter = sorted(self._recursedict(), key=lambda x: x[0])   # sort by keys (element 0)
        return '\n'.join(item + " = " + repr(value) for item, value in sorted_iter)

    def GETLEVEL(self, key):
        """Given a string key (separated by '.'), return the object with that heirarchy"""
        target = self
        for level in key.split('.'):
            if level in target:
                target = target[level]
            else:
                raise KeyError('key[%s] is not found' % key)
        return target

    def SAME_AS(self, target):
        """
        Recursively/make-a-deep-copy of target.
        This is also the proper way of doing a dictionary .update() for TVPVConfigDict().

        Example:
           VREV.vrevPA1.SAME_AS(VREV.vrevPA0)

        Cannot use simple copy.deep() since it will do infiniteloop on DictConfig.
        If you see an Exception 'TypeError: 'DictConfig' object is not callable',
        it means that the target does not exist.
        """
        from copy import deepcopy

        for item, value in target.items():
            tt = type(value)
            if tt in BUILTIN_TYPES_SIMPLE:
                self[item] = value
            elif tt is DictConfig:
                self[item].SAME_AS(value)
            elif tt is list:
                self[item] = list(value)   # make a copy
            else:
                self[item] = deepcopy(value)

    def merge(self, dict2, _d1=None):
        """
        combine/merge dict2 into self.
        dict2 will be untouched
        """
        dict2 = copy_configdict(dict2)   # make a copy first, since it will be modified
        if _d1 is None:
            _d1 = self
        for item, value in list(_d1.items()):
            if item in dict2:
                if isinstance(dict2[item], DictConfig):
                    _d1[item] = self.merge(dict2.pop(item), value)
            else:
                _d1[item] = value
        for item, value in list(dict2.items()):
            _d1[item] = value
        return _d1


def TVPVConfigDict():
    """
    Factory function used on TVPVConfigDict for autovivification
    """
    return DictConfig(TVPVConfigDict)


def autodict():
    """
    This makes auto hash assignment, autovivification.
       example: hh = autodict()
                hh['ky1']['ky2']['ky3'] = 123
    """
    return defaultdict(autodict)


def recurse2dict(inp):
    """
    Converts inp to a built-in dict type, for use in marshal.
    It will recursively traverse thru all values deeply.
    inp must be a dictionary-like type (collections.defaultdict, autovivication, DictDot, etc)
    For single level dictionary (e.g. defaultdict), use res=dict(<var>) directly.
      example:  res = recurse_to_dict(var)
    """
    try:
        res = dict(inp)
    except TypeError:
        return inp
    except ValueError:
        return inp

    for k, v in inp.items():
        if not type(v) in BUILTIN_TYPES_ALL:
            res[k] = recurse2dict(v)
    return res


def _remove_quote_after_equal(line):
    """Used by flatdict(). Removes the quotes after the equal sign, if exist"""
    a = line.find(' = ')
    quotes = "'\""
    if a > 0 and line[a + 3] in quotes and line[-1] in quotes and a + 4 != len(line):
        return line[:a + 3] + line[a + 4:-1]
    return line


def flatdict(dd):
    """
    Iterator: Converts inp (dictionary-like) to a flat string list:
       <key>.<key>.<key> = <value>
    for list, it will be:
       <key>[n] = <value>
    Calls Dumper(). Removes the quote after the '='
    """
    return map(_remove_quote_after_equal, Dumper(dd, dot=True, p=False).string().split('\n'))


def chunkdict(dd, limit):
    """
    Iterator: returns a dictionary of <limit> number of keys at a time
    """
    ctr = 0
    result = {}
    for k, v in dd.items():
        result[k] = v
        ctr += 1
        if ctr == limit:
            yield result
            result = {}
            ctr = 0

    # return what is left
    if ctr:
        yield result


def copy_configdict(dd):
    """
    Returns a copy of dd (TVPVConfigDict), and disables autovivification
    """
    newdd = TVPVConfigDict()
    newdd.SAME_AS(dd)
    newdd.AUTO_OFF()
    return newdd


def delkeys(d, seq_of_keys_to_del):
    """
    Returns a dctionary with seq_of_keys_removed
    Useful when comparing dictionaries during unittest and some key is a don't care
    """
    newdict = dict(d)  # make a copy
    for key in seq_of_keys_to_del:
        if key in newdict:
            del newdict[key]
    return newdict


class _EmptyClass:
    pass


def attr2dict(obj):
    """
    Gets all attributes of a class obj, puts it in a dict and returns the dict
    """
    ref = set(dir(_EmptyClass()))
    attr = partial(getattr, obj)   # getattr
    dd = {v: attr(v) for v in dir(obj) if (v not in ref and
                                           not callable(attr(v)))}
    return dd


def dict2attr(dd):
    """
    Returns an object with attribute values assign to values from dd dictionary
    This is useful for unittest, when mocking a class or a module object
    """
    obj = _EmptyClass()
    for key, val in dd.items():
        setattr(obj, key, val)
    return obj


def getkeyfromval(somedict, val):   # unittested
    """
    Simple wrapper to get a key from a dictionary given a value.
    It will return the first occurrence (not a list).
    For more efficient value to key mapping, use DictValues object
    Will return None if not found
       example:  key = getkeyfromval(dd, 'value')
    """
    for item, v in somedict.items():
        if val == v:
            return item


def iterkeyfromval(somedict, val):  # unittested
    """
    Iterator/generator to get all keys from dictionary given a value
    For more efficient value to key mapping, use DictValues() object
       example:  for keys in iterkeyfromval(dd, 'value')
    """
    for item, v in somedict.items():
        if val == v:
            yield item


def iter_dot_items(dd, listdot=True):
    """
    Iterator: Recursively returns the (key, value) pair where key is concatenated by '.'
    Assumes that dd is a dictionary-like structure (multi-level)
      Example:
        d.par1.child.last1 = 123
        d.par2.child.last2 = 456
        d.par3.child.last3 = 789
        for kk, val in iter_dot_items(d):
           print kk, val
               # par1.child.last1 123
               # par2.child.last2 456
               # par3.child.last3 789
    """
    if listdot and (type(dd) in BUILTIN_TYPES_LIST):
        for ctr, value in enumerate(dd):
            item = "[" + str(ctr) + "]"
            if type(value) in BUILTIN_TYPES_SIMPLE:
                yield str(item), value
            else:
                for nitem, fval in iter_dot_items(value, listdot):
                    yield str(item) + "." + nitem, fval
    elif isinstance(dd, dict):  # not type(dd) in BUILTIN_TYPES_SIMPLE:
        for item, value in sorted(dd.items()):
            if type(value) in BUILTIN_TYPES_SIMPLE:
                yield str(item), value
            else:
                for nitem, fval in iter_dot_items(value, listdot):
                    if nitem == "":
                        yield str(item), fval
                    else:
                        yield str(item) + "." + nitem, fval
    else:
        yield "", dd


def find_dot_items(dd, key=None, regex=None, default=None):
    """
    Given item, return the values
    :param dd: multi-level dictionary (usually from xml)
    :param key: key to find using python contains
    :param regex: key to find using regex
    :param default: default value to return
    :return: sorted list of unique values
    """
    assert key or regex, "find_dot_items(): one of key or regex is required in args"
    assert not (key and regex), "find_dot_items(): Cannot specify both key and regex"
    if regex:
        robj = re.compile(regex)
    result = set()
    for k, v in iter_dot_items(dd):
        if (key and key in k) or (regex and robj.search(k)):
            result.add(v)
    if not result:
        return default
    return sorted(result)


def key_exist(dd, *keys):
    """
    Return True if multi-level keys exist.

    Usage Example:
       if key_exist(mydict, 'name', 'vedbsrc', 'tracelist'):
          return mydict[name]['vedbsrc']['tracelist']
    """
    start = dd
    for item in keys:
        if item not in start:
            return False
        start = start[item]
    return True


def iter_levels(dd, levels, _n=0, _result=tuple()):
    """
    Iterate dictionary of multi-level in a flattened sorted fashion.

    This would save on python indents for multi-level dictionaries

    :param dd: Input dictionary
    :param levels: how many levels
    :param _n: internal, recursive counter
    :param _result: internal, _result accumulator
    :return: tuple depending on how many levels
    """
    assert levels >= 2, 'Error: invalid level value. Must be 2 or more'
    if levels - 1 == _n:
        for item in sorted(dd):
            yield _result + (item,)
    else:
        for item in sorted(dd):
            for output in iter_levels(dd[item], levels, _n + 1, _result + (item,)):
                yield output


def get_multi_level(dd, *keys):
    """
    Return value of multi-level keys

    Usage Example:
       print get_multi_level(mydict, 'name', 'vedbsrc', 'tracelist'):
    """
    start = dd
    for item in keys:
        start = start[item]
    return start


def iterpartialkey(dd, partialkey):
    """
    Iterator, Recursively finds the partialkey, separated by dot.
    Returns the dict value where partialkey partially matches key.
    Useful in xmls.
    example:
       for k in iterpartialkey(d, 'par2.child'):
    """
    for key, value in iter_dot_items(dd):
        if partialkey in key:
            yield value


def remove_none_values(d):
    """
    Remove items in d which have none values

    :param d: input dictionary
    :return: d
    """
    remove = {k for k in d if d[k] is None}
    for k in remove:
        del d[k]
    return d


def keys_atlevel(dd, n: int, error=False, _ll=0) -> str:
    """
    Iterator, Returns all keys at n level

    multi-level routine / recursive

    :param dd: Input dictionary
    :type dd: dict
    :param n: Level to display
    :type n: int
    :param error: Set to True to error out if that level is not dict
    :type error: bool
    :param _ll: Internal use only, recursion
    :return: keys of dictionary at n level
    :rtype: str
    """
    if n == _ll:
        if isinstance(dd, (dict, set, list)):
            for item in dd:
                yield item
        else:
            yield dd
        return

    if isinstance(dd, dict):
        for item in dd:
            for x in keys_atlevel(dd[item], n, error, _ll + 1):
                yield x
    else:
        if error:
            raise TypeError('%r is not dictionary type of level=%d of %d' % (dd, _ll, n))


class DictValues(dict):     # unittested
    """
    A derived dictionary that also stores the values also in another internal dictionary
    for fast access.
    >>> dd = DictValues(a=123, b=123, c=456)
    >>> list(dd.vkeys(123))
    ['a','b']
    >>> list(dd.uniq_values)
    [123,456]
    """

    # conditions to consider:
    #   new item assign
    #   same item assign, different value
    #   delete item
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._assign_vdict()

    def _assign_vdict(self):
        # Assign initial values to vdict
        self.vdict = defaultdict(set)
        for item, val in self.items():
            self.vdict[val].add(item)

    def __setitem__(self, item, value, setitem=dict.__setitem__):
        # below is for unpickle use
        if not hasattr(self, 'vdict'):
            self.vdict = defaultdict(set)

        # When item exist and reassign to different value
        if item in self and self[item] != value:
            self.vdict[self[item]].discard(item)

        # Add it
        self.vdict[value].add(item)

        # add it to normal dictionary
        setitem(self, item, value)

    def __delitem__(self, item, delitem=dict.__delitem__):
        if item in self:
            self.vdict[self[item]].discard(item)
            delitem(self, item)

    def vkeys(self, value):
        """
        Iterator: Return a list of keys given the value.
        Will get from internal parallel dictionary
        """
        if value in self.vdict:
            for keys in self.vdict[value]:
                yield keys

    def uniq_values(self):
        """
        Iterator: Return a list of unique values
        """
        for v in self.vdict:
            if len(self.vdict[v]) > 0:
                yield v

    def update(self, seq):
        """
        built-in update() override, to rebuild the internal dictionary
        """
        dict.update(self, seq)
        self._assign_vdict()


class DictDot(dict):
    """
    Adds object-like functionality to normal dictionary
    Object attributes and Dictionary are stored in the Dictionary space.
    Useful for pure-data/dictionary type container.
    Do not use for object that has *properties* since property vs data cannot be distinguished
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, item):
        if item.startswith("__"):
            return dict.__getattr__(self, item)
        return self[item]

    def __setattr__(self, item, value):
        self[item] = value


class DictDotRO(DictDot):
    """
    DictDot - ReadOnly dictionary
    Useful when caching a dictionary and you don't want code to modify the entry
    """

    def __setattr__(self, *args):
        raise AttributeError("Cannot write, dictionary is readonly")

    def __setitem__(self, *args):
        raise AttributeError("Cannot write, dictionary is readonly")

    def update(self, *args):
        raise AttributeError("Cannot update, dictionary is readonly")

    def clear(self, *args):
        raise AttributeError("Cannot clear, dictionary is readonly")

    def setdefault(self, *args):
        raise AttributeError("Cannot setdefault, dictionary is readonly")

    def popitem(self, *args):
        raise AttributeError("Cannot popitem, dictionary is readonly")

    def pop(self, *args):
        raise AttributeError("Cannot pop, dictionary is readonly")

    def __delitem__(self, *args):
        raise AttributeError("Cannot delete, dictionary is readonly")


class DefaultDictDot(defaultdict):
    """
    Adds object-like (dot access) functionality to defaultdict
    Object attributes and Dictionary are stored in the Dictionary space.
    Useful for pure-data/dictionary type container.
    Do not use for object that has *properties* since property vs data cannot be distinguished
    """
    __repr__ = dict.__repr__

    def __init__(self, *args, **kwargs):
        defaultdict.__init__(self, *args, **kwargs)

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, item, value):
        self[item] = value


def autoDictDot():
    """
    Factory auto-vivification for DictDot
      example: hh=autoDictDot()
               hh.ky1.ky2=123
    """
    return DefaultDictDot(autoDictDot)


class NamedSeq:
    """
    Similar to collections.namedtuple, This class returns a DictConfig dictionary given
    the tuple sequence. keys can be accessed by [].

    Contrast:
       namedtuple                  NamedSeq
    1) 'tuple'-like                'dict'-like
    2) implemented as a class      implemented as '__call__' and return DictConfig()
    3) [] is index number access   [] is key name access

    This is used in conjunction with Configuration files.
    Default values can be set via .default()

    Example:
       filter = NamedSeq('name', 'regex')
       dd  = filter('Pre', 'hsw_pre.*')
       print dd.name    # Returns 'Pre'
       print dd['name'] # Returns 'Pre'
       print dd.regex   # Returns 'hsw_pre.*'
    """

    __slots__ = ['listname', 'defval']

    def __init__(self, *listname):
        # check if name is ok
        for name in listname:
            if not isinstance(name, str):
                raise ValueError('Field name [%r] is not a string: %s' % (name, type(name)))
            if not all(c.isalnum() or c == '_' for c in name):
                raise ValueError('Field names can only contain alphanumeric characters and underscores: %r' % name)
            if iskeyword(name):
                raise ValueError('Field names and field names cannot be a keyword: %r' % name)
            if name[0].isdigit():
                raise ValueError('Field names and field names cannot start with a number: %r' % name)

        # assign it
        self.listname = listname
        self.defval = {}

    def __call__(self, *args, **kwargs):
        """
        Returns a DictConfig() dictionary given the input values
        This functional makes the name of the object callable (similar to namedtuple).
        """
        dd = DictConfig()
        dd.update(self.defval)    # Put default values

        # assign the sequence/args first
        if len(args) > len(self.listname):
            raise ValueError("Given number of elements %d is greater than required %d" % (len(args), len(self.listname)))

        for idx, val in enumerate(args):
            dd[self.listname[idx]] = val

        # assign the kwargs/dict next
        dd.update(kwargs)

        # check for problems
        for key in self.listname:
            if key not in dd:
                raise ValueError("key=[%s] is not set to any value" % key)

        return dd

    def default(self, **kwargs):
        """
        Sets a default value for the sequence
        """
        self.defval.update(kwargs)


def key_remap(d, alias_dict, dictclass=dict):
    """
    Returns a dictionary, with key names remapped by alias_dictionary
    Example:
      d1 = {'one': 111, 'two': 222, 'any':999}
      alias = {'one':'First', 'two':'Second'}
      print key_remap(d1, alias)
      # Result: {'First':111, 'Second':222, 'any':999}
    """
    res = dictclass()
    for k in d:
        if k in alias_dict:
            res[alias_dict[k]] = d[k]
        else:
            res[k] = d[k]
    return res


def reverse_set(d):
    """
    Reverses a dictionary where value is a sequence or string

    :param d: {key: sequence}
    :return: {sequence_value: set_of_keys}
    """
    result = defaultdict(set)
    for k, v in d.items():
        if isinstance(v, str):
            result[v].add(k)
        else:
            for item in v:
                result[item].add(k)
    return dict(result)


def reverse_keyval(d, keyindict=None, dictclass=dict):
    """
    Returns a standard dictionary (or specified dictclass)
    with reversed key:value to value:key. Duplicate value will be overwritten randomly.
    If keyindict is specified, then grab that key.

    Example:
       print reverse_keyval({'a':'a123', 'b':'b456'})
       # result: {'a123':'a', 'b456':'b'}.

       mydict = TVPVConfigDict()
       mydict.A.full = 'a123'
       mydict.A.desc = 'letterA'
       mydict.B.full = 'b456'
       mydict.B.desc = 'letterB'
       print reverse_keyval(mydict, 'full')
       # result: {'a123':'A', 'b456':'B'}
    """
    if keyindict is None:
        return dictclass({v: k for k, v in d.items()})

    return dictclass({v[keyindict]: k for k, v in d.items() if keyindict in v})


class XmlFunc:
    """
    A class that holds various Xml routines.
    Instantiatiated as a singleton. xmlfunc is an instantiated object.
    Usage:
    >>> xmlobj = xmlfunc.dict2xml(dd)
    >>> dd     = xmlfunc.xml2dict(xmlfile)
    """

    def _ConvertDictToXmlRecurse(self, parent, dictitem):
        from xml.etree import cElementTree as ElementTree
        assert not isinstance(dictitem, type([]))

        if isinstance(dictitem, dict):
            for (tag, child) in dictitem.items():
                if str(tag) == '_text':
                    parent.text = str(child)
                elif isinstance(child, type([])):
                    # iterate through the array and convert
                    for listchild in child:
                        elem = ElementTree.Element(tag)
                        parent.append(elem)
                        self._ConvertDictToXmlRecurse(elem, listchild)
                else:
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    self._ConvertDictToXmlRecurse(elem, child)
        else:
            parent.text = str(dictitem)

    def dict2xml(self, xmldict):
        """
        Converts a dictionary to an XML ElementTree Element

        Example:
        >>> mydict = {'dieconfig':123,'fuseconfig':456}
        >>> x = xmlfunc.dict2xml({'top':mydict})
        >>> ElementTree.tostring(x)
        '<top><dieconfig>123</dieconfig><fuseconfig>456</fuseconfig></top>'

        """
        from xml.etree import cElementTree as ElementTree
        roottag = list(xmldict.keys())[0]
        root = ElementTree.Element(roottag)
        self._ConvertDictToXmlRecurse(root, xmldict[roottag])
        return root

    def _ConvertXmlToDictRecurse(self, node, dictclass):
        """
        Private recursive function to read the elementtree object and convert to dict
        """
        nodedict = dictclass()

        if len(list(node.items())) > 0:
            # if we have attributes, set them
            nodedict.update(dict(list(node.items())))

        for child in node:
            # recursively add the element's children
            newitem = self._ConvertXmlToDictRecurse(child, dictclass)
            if child.tag in nodedict:
                # found duplicate tag, force a list
                if isinstance(nodedict[child.tag], type([])):
                    # append to existing list
                    nodedict[child.tag].append(newitem)
                else:
                    # convert to list
                    nodedict[child.tag] = [nodedict[child.tag], newitem]
            else:
                # only one, directly set the dictionary
                nodedict[child.tag] = newitem

        if node.text is None:
            text = ''
        else:
            text = node.text.strip()

        if len(nodedict) > 0:
            # if we have a dictionary add the text as a dictionary value (if there is any)
            if len(text) > 0:
                nodedict['_text'] = text
        else:
            # if we don't have child nodes or attributes, just set the text
            nodedict = text

        return nodedict

    def _remove_wierd_char(self, text):
        """
        Returns the text that starts with '<', try to find on first 10 chars
        This is found on some .xml that cause error on windows
        """
        if len(text):
            for idx in range(10):
                if text[idx] == '<':
                    if idx == 0:
                        return text    # as is
                    else:
                        return text[idx:]
        return text   # as-is, do nothing

    def xml2dict(self, root, dictclass=DictDot):
        """
        Converts an XML file or ElementTree Element to a dictionary.
        Returns DictDot dictionary.
        """
        # Code originally from Eugene Koval. Modified by jqdelosr.
        from gadget.files import File
        from xml.etree import cElementTree as ElementTree
        from io import IOBase
        file_type = IOBase

        # If a string or file handle is passed in, try to open it as a file
        if isinstance(root, str):
            with File(root, autofind=True, return_fh=True, mode='rb') as fh:
                text = fh.read()
                root = ElementTree.fromstring(self._remove_wierd_char(text))
                # root = ElementTree.parse(fh).getroot()
        elif isinstance(root, file_type):
            root = ElementTree.parse(root).getroot()

        return dictclass({root.tag: self._ConvertXmlToDictRecurse(root, dictclass)})

    def dict_pretty_string(self, d):
        """
        Pretty dictionary string via json
        usage: print(xmlfunc.dict_pretty_string(d))
        """
        import json
        return json.dumps(d, indent=3)

    def _addDict(self, lines, node, offset):
        from xml.sax.saxutils import escape
        for name, value in node.items():
            if isinstance(value, dict):
                lines.append(offset + "<%s>" % name)
                self._addDict(lines, value, offset + " " * 4)
                lines.append(offset + "</%s>" % name)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        lines.append(offset + "<%s>" % name)
                        self._addDict(lines, item, offset + " " * 4)
                        lines.append(offset + "</%s>" % name)
                    else:
                        lines.append(offset + "<%s %s=\"%s\" />" % (name, name, escape(str(item))))
            else:
                lines.append(offset + "<%s %s=\"%s\" />" % (name, name, escape(str(value))))

    def dict2xml_str(self, d):
        """
        Converts a dictionary to a XML String output

        Example:
        >>> mydict = {'dieconfig':123,'fuseconfig':456}
        >>> print xmlfunc.dict2xml_str(mydict)
        <dieconfig dieconfig="123" />
        <fuseconfig fuseconfig="456" />
        """

        lines = []
        self._addDict(lines, d, "")
        lines.append("")
        return "\n".join(lines)


xmlfunc = XmlFunc()


class IniFunc:
    """
    A class that holds various ini routines.
    Instantiatiated as a singleton. inifunc is an instantiated object.
    Usage:
    >>>          inifunc.dict2ini(dd, outinifile)
    >>> dd     = inifunc.ini2dict(inifile)
    """

    def dict2ini_str(self, inidict):
        """
        Converts a dictionary to an INI string

        Example:
        >>> mydict = {'sectionname':{'key1':'value1','key2':'value2'} }
        >>> ini_str = inifunc.dict2ini(mydict)

        ini_str:
        [sectionname]
        key1 = value1
        key2 = value2
        """

        iniList = []
        for section in sorted(inidict.keys()):
            iniList.append("[%s]\n" % (section))
            if isinstance(inidict[section], dict):
                for key in sorted(list(inidict[section].keys()), reverse=True):
                    if type(inidict[section][key]) in (str, int, float):
                        iniList.append("%s = %s\n" % (key, inidict[section][key]))
                    else:
                        raise ValueError('Value of [%s][%s] is not a string or int: %r' % (section, key, inidict[section][key]))
            else:
                raise ValueError('Value is not a dictionary. It is a: %s' % type(inidict[section]))

        ini_str = ''.join(iniList)
        return ini_str

    def dict2ini(self, inidict, outinifile):
        """
        Converts a dictionary to an INI file

        Example:
        >>> mydict = {'sectionname':{'key1':'value1','key2':'value2'} }
        >>> inifunc.dict2ini(mydict, outinifile)

        outinifile:
        [sectionname]
        key1 = value1
        key2 = value2
        """
        ini_str = self.dict2ini_str(inidict)

        # save the ini content to file
        text_file = open(outinifile, "w")
        text_file.write(ini_str)
        text_file.close()

        return ini_str

    def ini2dict(self, inifile):
        """
        Converts an INI file to a dictionary.
        Returns dictionary.
        """
        from configparser import ConfigParser

        config = ConfigParser(strict=False)
        config.optionxform = str  # make option names case sensitive, FOO, Foo and foo are all different names
        config.read(inifile)

        dictionary = {}
        for section in config.sections():
            dictionary[section] = {}
            for option in config.options(section):
                dictionary[section][option] = config.get(section, option, raw=True)

        return dictionary


inifunc = IniFunc()


def firstitem(seq):
    """
    Returns the first item of a sequence. It is a random item if set or dict.
    Returns a key if dictionary
    """
    for firstitem in seq:
        if firstitem is None:    # None does not count
            continue
        return firstitem
    return None    # if sequence is empty


def add_no_dup(dictobj, key, val, dictname="dictionary"):
    """
    Add key:val to dictobj, if key does not exist yet.
    Raise Exception if it already exist
    """
    if key in dictobj:
        raise Exception("Key=[%s] already exist in %s. Duplicate key is not allowed"
                        "" % (key, dictname))
    dictobj[key] = val


def assign_multi_level(dd, keys, val, dictclass=DictDot):
    """
    seq_levels = [level1, level2, level3]
    assign d[level1][level2][level3] = val
    """
    start = dd
    for ii in range(len(keys)):
        item = keys[ii]
        if ii == len(keys) - 1:
            start[item] = val
            return

        if item not in start:
            start[item] = dictclass()
        start = start[item]

    else:  # pragma: no cover
        raise Exception("Unreachable code")


def merge_and_check_unique(*args):
    """
    Copy N dictionaries into one, check for duplicate keys
    args - dictionary objects
    returns a new object dictionary (dict type is from the first argument) with all keys combined
    from args
    """

    result = type(args[0])()  # result type should match the type of the first paramter

    # combine all keys in first level of dictionary, raise exception if any duplicate keys are found
    for arg in args:
        if not isinstance(arg, dict):
            raise TypeError("Input argument: %r does not seem to be a dictionary type" % type(arg))

        for key in arg:
            if key in result:
                raise KeyError('Duplicate keys found (%s) when joining dictionaries' % key)
            result[key] = arg[key]

    return result


def dict_merge(dct, merge_dct):
    """
    Recursive dict merge. Instead of upating only top-level keys, dict_merge recurses
    down into dicts nested to an arbitrary depth, updating keys. The ``merge_dct`` is
    merged into ``dct``.  If the same keys exist in both, ``dct`` is updated to match
    ``merge_dct`` value.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def dfs(graph, start_node):
    """
    Executes a depth first search: https://en.wikipedia.org/wiki/Depth-first_search.

    :param graph: An adjacency list (https://en.wikipedia.org/wiki/Adjacency_list)
    representing a graph.

    How to represent an adj in Python?

                 A
                /  \
               B    C

    graph = {'A': ['B', 'C'],
             'B': []],
             'C': []}

    Futher info: https://www.python.org/doc/essays/graphs/

    Node A has two children, B and C. B and C have no children.
    Children must be represented as a sequence (ideally set or list).

    :param start_node: Node in adjacency list (corrosponding
    to a key in the dictionary). The DFS will begin from this
    node.

    :return: A list detailing the path from start_node to the
    end of the graph.
    """

    for node, sequence in graph.items():
        if not isinstance(sequence, (list, set)):
            raise Exception("Nodes defined in input graph are not iterable. Please provide a set() or list() "
                            "stucture.")

    visted, stack = set(), [start_node]

    while stack:
        vertex = stack.pop()

        if vertex not in visted:
            visted.add(vertex)
            stack.extend(graph[vertex] - visted)

    return visted


def bytes_dict_to_str(str_or_bytes_dict, keys_to_str=False):
    """
    Convert a dictionary with string/bytes values to have string values (only bytes are converted, ints/floats/dicts are unchanged)
    Option to make keys strings as well (default is to leave keys as is)

    :param str_or_bytes_dict: dicitonary with strings/bytes values
    :param keys_to_str: Set to True to ensure keys are bytes (default False leaves keys as is)
    :return: str
    """
    if isinstance(str_or_bytes_dict, dict):
        from . import strmore
        bytes_dict = {}
        for key, value in list(str_or_bytes_dict.items()):
            orig_key = key
            if keys_to_str:
                key = strmore.to_str(key)
            value = strmore.to_str(value)           # will converty bytes to strings, leave all others untouched
            bytes_dict[key] = value
        return bytes_dict
    else:
        return str_or_bytes_dict


def read_csv(csvfile, return_dict=True):
    """
    Read a csv file and return a list

    :param csvfile: Input csv file
    :param return_dict: Set to True to return dictionary given the header
                        Set to False to return list including headers
    :return: list of (dict or list)
    """
    import csv as csv_module
    header = None
    allcsv = []
    with open(csvfile) as fh:
        reader = csv_module.reader(fh)
        for lno, row in enumerate(reader):
            if return_dict:
                if not header:
                    header = row
                    continue
                r_row = {}
                msg = f'Error on {csvfile} row#{lno+1}: expecting {len(header)} columns based on header'
                assert len(header) == len(row), msg
                for idx, item in enumerate(row):
                    r_row[header[idx]] = item
            else:
                r_row = row

            allcsv.append(r_row)

    return allcsv
