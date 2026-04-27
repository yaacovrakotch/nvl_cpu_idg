#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
VEP exception classes and error-check related routines

It is necessary to create VEP specific exception classes for unittesting and various
try..except block usages
"""
from functools import wraps
from os.path import basename, isdir, exists, join, islink, dirname
import traceback
import sys
import os
import re

# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


# do not change the line number of this code, since line number is hardcoded
EXPECTED_LINE_NUMBER = 29


def _checker_line_number_routine():
    from .gizmo import get_caller_lno

    def some_internal_subr():
        return get_caller_lno()

    return some_internal_subr()           # actual line number here is EXPECTED_LINE_NUMBER


class SuggestionBase:
    """
    This class is just definitions of usual suggestions during vep exception messages
    """

    def tvpvhelp_only(self):
        """
        :return: Suggestion message tvpvhelp only
        """
        return ("Pls read error message and do basic debug first. If error persist, then send email "
                "to jqdelosr and paste this error message including the traceback information.")

    def default_suggestion(self):
        """
        :return: Default suggestion message
        """
        # TODO: Update algo of default to be:
        # 1. If rel and vcf or make_pattern, then goto wiki page
        # 2. If sandbox, then "Check the traceback and do python debug"
        # 3. else, tvpvhelp_only()

        return self.tvpvhelp_only()


class ErrorVepBase(Exception):
    """
    Top level VEP Exception Class
    This adds a pretty printout message
    """

    def __init__(self, errormessage, suggestion=None, frameref=0):  # Error is normal 2nd argument
        # Call the base class constructor with the parameters it needs
        self._tbframe = 2 + frameref
        errmsg = self._errmsg(errormessage, suggestion)
        Exception.__init__(self, '\n'.join(errmsg))  # Do not use super() here. Specifically use Exception

        # Code here is executed during raise, even if "try block" exist. (It will not Exit though)

        # Below is commented, since it will display unnecessary message during try...except. Exceptions are displayed anyway.
        # log.critical("-e- From %s() lno#%d, %s" %
        #             (sys._getframe(1).f_code.co_name, sys._getframe(1).f_lineno, errormessage))

    def _errmsg(self, errormessage, suggestion):
        """Returns the errmsg array"""
        # Build the pretty error message
        errmsg = ['   <<< Error Type',  # 0
                  '=============================',  # 1
                  'Error:      %s' % errormessage,  # 2
                  'Suggestion: %s' % self.get_suggestion(suggestion),  # 3
                  'ErrorSig:   %s' % self.get_errorsig(sys._getframe(self._tbframe)),  # 4
                  'Rundir:     %s' % self.get_rundir(),  # 5
                  '=============================']  # 6
        errmsg[1] = errmsg[6] = '=' * min(120, max(len(x) for x in errmsg[2:5]))  # Make the "==" line match the length
        return errmsg

    def get_suggestion(self, msg=None):
        """Returns the suggestion message"""

        if msg is not None:
            return msg

        # Return the default suggestionn
        return suggestion.default_suggestion()

    def get_errorsig(self, fr):
        """Return the errorsignature. fr is frame object"""
        from .shell import HOSTNAME

        prodname = 'TBD'   # product name

        # build the error signature
        filename = basename(fr.f_code.co_filename)
        errorsig = ('{prod} {machine} {filename}:{func}() lno#{lno}'
                    '').format(prod=prodname,
                               machine=HOSTNAME,
                               filename=filename,
                               func=fr.f_code.co_name,
                               lno=fr.f_lineno)
        return errorsig

    def get_rundir(self):
        """Return the rundir string"""
        return "rundir_tbd"

    @classmethod
    def get_main_error(cls, text):
        """
        Given the ErrorVepBase error string, derive the main error message. See <main_error> below
           Error:      <main_error>
           Suggestion: <somestring>
           ErrorSig:   <somestring>
           Rundir:     <somestring>

        Usage:
            try:
                <some_code_that_raise_ErrorVep_exception>
            except Exception as e:
                log.debug('Error is: %s' % ErrorVep.get_main_error(e))
        """
        found = re.search(r"Error:\s+(.*)\n", str(text))
        if found:
            return found.group(1)
        else:
            return str(text)  # return as-is

    @classmethod
    def args(cls, obj):
        """
        Returns a list, depending on what the object is. See below for usage:
            raise ErrorInput(*ErrorInput.args('text'))
        or
            raise ErrorInput(*ErrorInput.args(('text','suggestion)))
        """
        if isinstance(obj, str):
            return [obj]
        else:
            return obj


def stage_owner_only(func):          # pragma: no cover   (unused for now)
    """
    Decorator. If applied to a method - checks if owner is stage
    Raises ErrorUser If caller of the method is not a stage owner.
    Usage:
        @stage_owner_only
        def myfunc():
            # some code which require p6vector only
    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        Check().is_stage_owner()
        return func(*args, **kwargs)

    return func_wrapper


def exc_source():
    """
    Returns the file, func and line number of last caller exception

    Used in try/except block. Example:
    try:
        some_code()
    except Exception as e:
        log.info("Exception happened at %s" % exc_source())

    :return: string: "file.py: line 5, in func()"
    """
    fname, lno, funcname, line = traceback.extract_tb(sys.exc_info()[2])[-1]
    return "%s, line %s, in %s()" % (fname, lno, funcname)


class _CheckOld:
    """
    Collection of various Check routines
    """

    def _get_defaultclass(self, errorclass, suggestedclass=None):
        """Return the default error class to use"""
        if errorclass is not None:
            if not issubclass(errorclass, ErrorVepBase):
                raise Exception("%r must be VEP error class type" % errorclass)
            return errorclass

        if suggestedclass is not None:
            if not issubclass(suggestedclass, ErrorVepBase):
                raise Exception("%r must be VEP error class type" % suggestedclass)
            return suggestedclass

        return ErrorConfig

    def required_valid(self, set_to_check, required=None, valid=None, message="Error:",
                       suggestion=None, errorclass=None):
        """
        Routine to check for REQUIRED and VALID keys given dictionary keys/set_to_check.
        "required" (optional) can be a string or a set. If string, it must be delimited by space
        "valid" (optional) can be string or a set. If string, it must be delimited by space
        "message" will be raised upon error. String below will be added:
             "Required key {field} does not exist" or
             "{field} is not a valid keyword"

        Example Usage:
                check.required_valid(cfg.CFG_sources[field].viewkeys(),
                                     required="file regex",
                                     valid   ="desc type file regex",
                                     message ="Config Error: CFG_source=%s." % field)
        """
        if isinstance(required, str):
            reqset = set(required.split())
        else:
            reqset = required

        if isinstance(valid, str):
            valset = set(valid.split())
        else:
            valset = valid

        # check required keywords
        if reqset is not None:
            for fieldreq in sorted(set(reqset) - set(set_to_check)):
                errorclass = self._get_defaultclass(errorclass)
                raise errorclass(message + " Required key %r does not exist." % fieldreq,
                                 suggestion=suggestion, frameref=1)

        # check valid keywords
        if valset is not None:
            for fieldval in sorted(set(set_to_check) - set(valset)):
                errorclass = self._get_defaultclass(errorclass)
                raise errorclass(message + " %r is not a valid keyword." % fieldval,
                                 suggestion=suggestion, frameref=1)

    def is_list(self, varlist,
                message="Input is not a list. It is a {type}",
                suggestion="Pls update config such that above is a list.", errorclass=None):
        """Checks if varlist is a list, raise Exception if not"""
        if not isinstance(varlist, list):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(message.format(type=type(varlist)),
                             suggestion=suggestion, frameref=1)
        return varlist

    def is_set(self, varset,
               message="Input is not a set. It is a {type}",
               suggestion="Pls update config such that above is a set.", errorclass=None):
        """Checks if varset is a set, raise Exception if not"""
        if not isinstance(varset, set):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(message.format(type=type(varset)),
                             suggestion=suggestion, frameref=1)
        return varset

    def is_list_or_set(self, varlistset,
                       message="Input is not a list|set. It is a {type}",
                       suggestion="Pls update config such that above is a sequence (set or list).",
                       errorclass=None):
        """Checks if varlistset is a list or set, raise Exception if not"""
        if not (isinstance(varlistset, set) or isinstance(varlistset, list)):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(message.format(type=type(varlistset)),
                             suggestion=suggestion, frameref=1)
        return varlistset

    def is_string(self, varstr,
                  message="Input is not a string. It is a {type}",
                  suggestion="Pls update config such that above is a string.",
                  errorclass=None):
        """Checks if varstr is a string, raise Exception if not"""
        if not isinstance(varstr, str):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(message.format(type=type(varstr)),
                             suggestion=suggestion, frameref=1)
        return varstr

    def is_dict(self, vardict,
                message="Input is not a dictionary type. It is a {type}",
                suggestion="Pls update config such that above is a dictionary.",
                errorclass=None,
                make_copy=False):
        """Checks if vardict is a dictionary/mapping type, raise Exception if not"""
        from .dictmore import copy_configdict

        if not isinstance(vardict, dict):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(message.format(type=type(vardict)),
                             suggestion=suggestion, frameref=1)
        if make_copy:
            return copy_configdict(vardict)

        return vardict

    def is_int(self, varint,
               message="Input is not integer. It is a {type}",
               suggestion="Pls update config such that above is int.",
               errorclass=None):
        """Checks if varint is integer, raise Exception if not"""
        if not isinstance(varint, int):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(message.format(type=type(varint)),
                             suggestion=suggestion, frameref=1)
        return varint

    def is_dir(self, vardir,
               message="Directory does not exist: [{dir}]",
               suggestion=None,
               errorclass=None):
        """Checks if vardir is a directory, raise Exception if not"""
        if not isdir(vardir):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(message.format(dir=vardir),
                             suggestion=suggestion, frameref=1)
        return vardir

    def is_broken_link(self, path,
                       message="{path} is a broken link (destination does not exist).",
                       suggestion=("File tvpvhelp and have vep admin investigate why it is a "
                                   "broken link."),
                       errorclass=None):
        """Checks if path is a broken link, raise ErrorEnv if so"""
        if (not exists(path)) and islink(path):  # broken link condition
            errorclass = self._get_defaultclass(errorclass, ErrorEnv)
            raise errorclass(message.format(path=path),
                             suggestion=suggestion, frameref=1)
        return path

    def is_exist(self, varfile,
                 message="File does not exist: [{file}]. Detail: {detail}",
                 suggestion=None,
                 errorclass=None):
        """Checks if varfile (string or list) exist. Raise Exception if not"""
        from gadget.files import File

        if isinstance(varfile, str):
            seq = [varfile]
        else:
            seq = varfile

        # varfile is a sequence
        for f in seq:
            if not exists(f):
                errorclass = self._get_defaultclass(errorclass)
                raise errorclass(message.format(file=f,
                                                detail=File(f).open_error_message()),
                                 suggestion=suggestion, frameref=1)
        return varfile

    def is_dir_writable(self, vardir,
                        message="Directory is not writable: {dir}",
                        suggestion=None,
                        errorclass=None,
                        testdata='test',
                        frameref=1):
        """Checks if vardir is a writable directory, raise Exception if not"""
        from .files import TempName, File

        if not vardir:    # empty
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass('Specified directory is empty.',
                             'Pls add "./" at the start of your path or provide full path.',
                             frameref=frameref)
        if not isdir(vardir):
            errorclass = self._get_defaultclass(errorclass)
            raise errorclass(f'Directory does not exist: [{vardir}]',
                             'Expecting this directory to exist. Pls check',
                             frameref=frameref)
        with TempName() as t:
            tmp = join(vardir, basename(t.name()))
            try:
                fh = open(tmp, "w")
                fh.write(testdata)
                fh.close()  # need implicit close here, seen during home dir quota, or disk full
            except BaseException:
                File(tmp).unlink()  # In cases where disk is full, tmp still exist
                errorclass = self._get_defaultclass(errorclass)
                raise errorclass(message.format(dir=vardir),
                                 suggestion=suggestion, frameref=frameref)
            os.unlink(tmp)
        return vardir

    def is_modifiable(self, vardir,
                      message="File or Directory cannot be modified/written: {path}",
                      suggestion=None,
                      errorclass=None):
        """
        Checks if vardir (file or dir) can be modified. It must be existing.
        """
        self.is_exist(vardir)
        if os.access(vardir, os.W_OK):
            return vardir  # success

        errorclass = self._get_defaultclass(errorclass, ErrorEnv)
        raise errorclass(message.format(path=vardir),
                         suggestion=suggestion, frameref=1)

    def is_auto_off(self, vardict,
                    message="Input dictionary has autovivification. Turn off by AUTO_OFF().",
                    suggestion="Update config file / dictionary and add '<dict_config_name>.AUTO_OFF()'",
                    errorclass=None):
        """Checks if vardict has autovivification turned off"""
        errorclass = self._get_defaultclass(errorclass)
        try:
            myvar = vardict['__SURENOTEXIST_key_']
            raise errorclass(message, suggestion=suggestion, frameref=1)
        except KeyError:
            pass
        return vardict

    def is_callable(self, vardict,
                    message="Input object is not callable.",
                    suggestion="Update config file / config dictionary entry must be callable",
                    errorclass=None):
        """Checks if vardict is callable"""
        errorclass = self._get_defaultclass(errorclass)
        if not callable(vardict):
            raise errorclass(message, suggestion=suggestion, frameref=1)
        return vardict

    def no_sles10(self, msg="Sles10 not supported for this command", suggestion="Please use a Sles11 machine"):
        """
        Check that the machine running the command is NOT sles10 (sles11 or higher needed for some functions)
        Throw an expception if Sles10, else return True
        :return:
        """
        from .shell import MachineInfo

        if MachineInfo().sles_version() == 10:
            raise ErrorUser(msg, suggestion)

        return True

    def is_ion_machine(self,
                       message="You cannot run {process} in a VNC Machine which is for interactivity only.\n"
                               "Please create a shell from ION machine pool using these instructions:\n"
                               "https://wiki.ith.intel.com/display/TVPV/VNC+and+ION#VNCandION-HowtocreateanIONTool"
                               "(work)session"):
        """
        Check that the machine running is an ION machine
        Throw an expception if it is a VNC machine, else return True
        :return:
        """
        from .shell import is_vnc_machine, CALLERBIN

        if is_vnc_machine():
            raise ErrorEnv(message.format(process=CALLERBIN))

        return True

    def is_dir_empty_writeable(self, dest):     # for shutil.copytree()
        """
        Check on destination dir for shutil.copytree
        Reason: shutil.copytree() requires destination to be non-existent
        1. must be writable
        2. must not exist, or if exist, it should be empty
        """
        # make sure parent dir is writable
        check.is_dir_writable(dirname(dest),
                              suggestion=f'Pls make sure [{dirname(dest)}] is writable.',
                              errorclass=ErrorUser,
                              frameref=2)

        # If existing, check if empty, writable
        if isdir(dest):
            result = os.listdir(dest)
            confirm(len(result) == 0,
                    f'Destination dir: [{dest}] is not empty. It contain {len(result)} files.',
                    f'Make sure destination dir is empty.',
                    frameref=2)

            try:
                os.rmdir(dest)
            except Exception as e:
                raise ErrorUser(f'Destination dir [{dest}] cannot be removed. Error: {e}',
                                f'Check permissions of [{dirname(dest)}]',
                                frameref=1)

        confirm(not isdir(dest),
                f'Destination dir [{dest}] Cannot be deleted. Pls delete first.',
                f'Pls specify a destination directory that does not exist.',
                frameref=2)

        confirm(not exists(dest),
                f'Destination dir [{dest}] seems to be a file',
                f'Pls specify a destination directory, or delete the file',
                frameref=2)
        return    # Success


def exit1(message, suggestion="try again"):
    """
    Display message and suggestion, and return exit code 1
    This differs from normal raise since error message is stdout.
    So that caller tool stdout processing is not messed up.

    :param message: Error message
    :param suggestion: suggestion message
    :return: None
    """
    print("==================================================")
    print(f"Error:      {message}")
    print(f"Suggestion: {suggestion}")
    print("==================================================")
    exit(1)


class ErrorVep(ErrorVepBase):
    """VEP Exception Error class with tracebacks"""
    pass


class ErrorVepNoTB(ErrorVepBase):
    """VEP Exception Error without any tracebacks - used for customer-facing errors"""
    without_traceback = True     # Used in SysExceptionManager

# Classes with tracebacks


class ErrorInput(ErrorVep):
    pass    # code developer error (not a user error)


class ErrorEnv(ErrorVep):
    pass    # something went wrong with env/disks


class ErrorExpect(ErrorVep):
    pass    # something expected is not happening


class ErrorCockpit(ErrorVep):
    pass    # cockpit errors

# tap errors


class ErrorTapChainMismatch(ErrorVep):
    pass     # too many ir/dr bits in a tap transaction


class ErrorTapOpcodeId(ErrorVep):
    pass     # opcode was not decoded

# classes without any traceback


class ErrorConfig(ErrorVepNoTB):
    pass           # Config Errors


class ErrorUser(ErrorVepNoTB):
    pass           # User Errors


class ErrorCheck(ErrorUser):
    pass           # Check Errors


class Check:
    """
    Function argument checks - newer
    """

    @classmethod
    def is_str(cls, field, var, lno=None, oknone=False):
        """
        Checks if var is string

        :param field: Name of variable
        :param var: variable
        :param lno: optional, line no
        :param oknone: Set to True if None isok
        :return:
        """
        return Check._is(field, var, str, lno, oknone, 'string')

    @classmethod
    def is_int(cls, field, var, lno=None, oknone=False):
        """
        Checks if var is int

        :param field: Name of variable
        :param var: variable
        :param lno: optional, line no
        :param oknone: Set to True if None isok
        :return:
        """
        return Check._is(field, var, int, lno, oknone, 'int')

    @classmethod
    def is_bool(cls, field, var, lno=None, oknone=False):
        """
        Checks if var is bool

        :param field: Name of variable
        :param var: variable
        :param lno: optional, line no
        :param oknone: Set to True if None isok
        :return:
        """
        return Check._is(field, var, bool, lno, oknone, 'bool')

    @classmethod
    def is_obj(cls, field, var, type_obj, lno=None, oknone=False):
        """
        Checks if var is of type_obj. type_obj can be tuple

        :param field: Name of variable
        :param var: variable
        :param type_obj: Classname or tuple of Classname
        :param lno: optional, line no
        :param oknone: Set to True if None isok
        :return: var
        """
        return Check._is(field, var, type_obj, lno, oknone, msg='%r' % (type_obj, ))

    @classmethod
    def _is(cls, field, var, type_obj, lno, oknone, msg):
        """
        Checks if var is of type_obj. type_obj can be tuple

        :param field: Name of variable
        :param var: variable
        :param type_obj: Classname or tuple of Classname
        :param lno: optional, line no
        :param oknone: Set to True if None isok
        :param msg: type message
        :return: var
        """

        if oknone and var is None:
            return var   # asis
        if isinstance(var, type_obj):
            return var   # Fast path: validation passed, no need for line number
        # Only get line number when we need to report an error
        if lno is None:
            # Use sys._getframe which is much faster than traceback.extract_stack()
            # especially in Python 3.11+ where traceback extraction is slower
            lno = sys._getframe(3).f_lineno     # assumed usage of arg checks on __init__
        raise ErrorUser(
            'On %s=%r, %s is expecting %s.' % (field, var, field, msg),
            'Pls fix value of %s in line# %d' % (field, lno))

    @classmethod
    def min_python_version(cls, major, minor, _ver=sys.version_info[:2]):
        """Raise exception if the system python version is less than major.minor"""
        if _ver < (major, minor):
            raise Exception("Python %d.%d or higher is required to run this code." % (major, minor))

    @classmethod
    def check_get_caller_lno(cls):
        """Make sure that internal python implementation works well with get_caller_lno implementation"""
        from platform import python_version
        lineno = _checker_line_number_routine()
        confirm(lineno == EXPECTED_LINE_NUMBER,
                f'Error! Implementation of get_caller_lno() for this python {python_version()} seems incorrect: {lineno}',
                'Pls use python 3.12.3 as this is proven.')


def confirm(condition, error, suggestion, cls=ErrorUser, frameref=1):
    """
    Make sure condition is True. If false, raise ErrorUser with error and suggestion.

    This is an improved "assert" version:
       1. with suggestion
       2. no-traceback (clean message to end user)
       3. The error and suggestion are *evaluated*
          unlike in assert, where it is not evaluated if condition is False.
          Example: assert some_condition, f'Error with {some_var_not_found}'

    :param condition: boolean
    :param error: Error message if condition is False
    :param suggestion: Suggestion if condition is False
    :param cls: Which class to use
    :param frameref: Set to 2 if this is called inside errors.py
    :return: None
    """
    if condition:
        return     # Do nothing
    raise cls(error, suggestion, frameref=frameref)


check = _CheckOld()
suggestion = SuggestionBase()
