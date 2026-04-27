#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
logger module / routines - base module

See VepLog class for Usage.
Refer to veplog.py for actual instantiation of Veplog
"""
import sys
import os
import time
import re
import logging
import functools
from inspect import getmembers, ismethod

from os.path import exists, dirname, basename
from .strmore import regex
from .helperclass import OPT, vepExceptionManager
from .gizmo import IS_UNIX
import atexit
import traceback

# loglevel STRING values and their numeric equivalent (source: Execute 'pydoc logging')
LOGLEVELS = {'NOTSET': 0,
             'DEBUG': 10,
             'INFO': 20,
             'WARN': 30,
             'WARNING': 30,
             'ERROR': 40,
             'FATAL': 50,
             'CRITICAL': 50
             }    # Correctness of these values are tested in test_loglevels()


class VepLog:
    """
    VEP logger Class. The design of this is a "singleton". The logger object
    is instantiated at import time (once only).

    Three ways to setup:
      1. log to screen only (various standalone scripts):
           log.stdout()   # -or- default behavior
      2. log to file only
           log.file(finaldest)
      3. log to screen and file  (for all log.info/log.debug)
           log.filestdout(finaldest)
      4. log to mixed - screen and file - used by vcf main
           log.filemixed(finaldest)
           # log.dev      -> both screen and file
           # log.debug    -> file only
           # log.info     -> both screen and file
           # log.warning  -> file only
           # log.error    -> file only
           # log.critical -> both screen and file
           # log.profile  -> file only   # Enabled with -print_profile
           # All the rest -> file only   # using log.file() setup


    To print log messages:
        print <text>         # log in screen only       ## Do not use!
        log.debug(<text>)    # Verbose debug messages
        log.dev(<text>)      # Call log.info only if -devdebug is invoked (aka, chatty verbose!)
        log.info(<text>)     # Usual info (Cannot use multi-args/comma delimited)
        log.warning(<text>)  # Important warnings, program still functioning (Cannot use multi-args/comma delimited)
        log.error(<text>)    # Used with Vep-Exception messages
        log.critical(<text>) # Critical error messages (Cannot use multi-args/comma delimited)
        log.profile(<text>, time, threshold)  # Profiling messages where ET > threshold
        log.nocommit(<text>) # For sandbox debugging only, to prevent accidental commit of these logs. Cannot commit .py files with log.nocommit()
        log.flush(<text>)    # Same as log.info(), and call sys.stdout.flush() so stdout is flushed.

    Example:
        from gadget.pylog import log
        log.filestdout(filelog, string_level="INFO")

    The format can be modified by replacing: before .file() or .stdout() init.
        log.fmt_stdout = "%(message)s"
        log.fmt_file   = "%(message)s"

    To capture stdout (log.info() or log.debug()) during unittest:
        with CaptureStdout() as p:
            log.stdout()       # needed to route to stdout
            # <call your function>
            self.assertEqual(p.getvalue(), '')

    Using decorators for logging/benchmarking - THESE ARE VERY USEFUL FOR DEVELOPMENT AND DEBUG

        EXAMPLE USAGES:
        ===============
        >>To have log.debug() calls stating when you enter/exit the func:
        EXAMPLE:
        @log.debug_wrap()
        my_func(*args,**kargs)

        RESULT:
        DEBUG   : method my_func - Starting...
        ...
        DEBUG   : method my_func,  - Done!"

        >>To have log.debug() calls stating when you enter/exit the func,
            AND log the params/return val of the function:
        EXAMPLE:
        @log.debug_wrap_more(?verbose)
        my_func(*args,**kargs)

        RESULT:
        DEBUG   : method my_func, args: (...),{...} - Starting...
        ...
        DEBUG   : method my_func, return_value=... - Done!"

        >>Logs entry/exit from method and timing of the method runtime. log_method configurable.
        EXAMPLE:
        @log.benchmark_wrap(log_method="info")
        my_func(*args,**kargs)

        RESULT:
        method my_func - Starting...
        ...
        method my_func, Elapsed in 0.23 secs - Done!"

        OTHER VARIANTS:
        ==============
        >>logs debug messages, without args+return_value, and with benchmark (timing) data.
        @log.debug_benchmark_wrap()
        my_func(*args,**kargs)

        >>Same as benchmark_wrap but logs args+return_val. log_method configurable.
        @log.benchmark_wrap_more(log_method="dev")
        my_func(*args,**kargs)

        >>Same as debug_wrap but you choose the log method/level.
            log_method=log.debug,log.info, log.warning,...
        @log.log_wrap(self, ?log_method)
        my_func(*args,**kargs)

        >>The most generic, prints args and return val, and can do benchmarks:
        @log.log_wrap_more(?log_method, ?verbose, ?timer)
        my_func(*args,**kargs)

        HINT: USE WRAPPERS TO DEBUG PERF BOTTLNECKS, AND TO ADD DEBUG MESSAGES WITHOUT
            TOO MUCH IN-CODE POLLUTION!

    VEP2 log usage is used as a singleton.
    """
    # We can not really do this "__slots__" stuff, because then we can't Mock these methods

    is_file_set_once = False     # Python logger is singleton. This identifies if file is set at least once.

    def __init__(self, log_exc=False):

        # Re-assign these to any desired format before stdout() or file()
        # The default stdout format for INFO level messages (clean)
        self.fmt_stdout_info = "%(message)s"
        # The default stdout format for all other levels (explicit level name)
        self.fmt_stdout = "%(levelname)-8s: %(message)s"
        self.funclen = 15
        self.fmt_file = "%(asctime)s %(funcName)-" + str(self.funclen) + "s %(message)s"

        self.cntcount = 0      # log identifier counter for unittest
        self.tmpname = None   # used with usetmp=True
        self.compresstype = None
        self.log = None
        self.logpath = None
        self._initvars()

        # Default setting for init:
        self.loglevel = self._get_and_set_loglevel(None)      # use default

        # Deprecated
        # self.set_log_methods_to_print()

        self.stdout(self.loglevel, log_exc=log_exc)

        atexit.register(self.close)

        # Additional formatting keywords below:
        # %(asctime)s    Time of log. Default format: '2003-07-08 16:49:45,896'
        # %(created)f    Time when the LogRecord was created (as returned by time.time()).
        # %(filename)s   Filename portion of pathname.
        # %(funcName)s   Name of function containing the logging call.
        # %(levelname)s  Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        # %(levelno)s    Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        # %(lineno)d     Source line number where the logging call was issued (if available).
        # %(message)s    The logged message, computed as msg % args. This is set when Formatter.format() is invoked.
        # %(module)s     Module (name portion of filename).
        # %(msecs)d      Millisecond portion of the time when the LogRecord was created.
        # %(name)s       Name of the logger used to log the call.
        # %(pathname)s   Full pathname of the source file where the logging call was issued (if available).
        # %(process)d    Process ID (if available).
        # %(processName)s        Process name (if available).
        # %(relativeCreated)d    Time in mSec the LogRecord was created, relative to when logging module was loaded.
        # %(thread)d        Thread ID (if available).
        # %(threadName)s    Thread name (if available).

    def get_logpath(self):
        return self.logpath

    def set_log_methods_to_print(self):
        """Set the log methods to normal print - deprecated in VepLog init.
        Only used when close() is called"""
        self.log = None
        self.debug = self._normal_print
        self.info = self._normal_print
        self.warning = self._normal_print
        self.error = self._normal_print
        self.critical = self._normal_print
        self.profile = self._normal_print

    def set_verbosity(self, string_level):
        """
        On-the-fly change the verbosity level of all handlers
        return the previous string_level
        """
        if string_level not in LOGLEVELS:
            raise Exception("Provided log information [%s] is not a valid log level. "
                            "Valid values are DEBUG,INFO,WARNING,ERROR,CRITICAL"
                            "" % string_level)

        orig = self.loglevel
        self.loglevel = string_level
        levelno = self._get_level(string_level)
        if isinstance(self.log, logging.Logger):
            for handler in self.log.parent.handlers:
                handler.setLevel(levelno)
        return orig

    def close(self):
        """
        Closes the logger file, gzip the file
        This routine is called upon python exit, via atexit(). See __init__()
        """
        if not self.s_setup:
            return
        logging.shutdown()
        self.set_log_methods_to_print()
        if self.__class__.is_file_set_once is True:
            self._close_inputfile()
        self._initvars()

    def _vep_info(self, msg, set_formatters=True, *args, **kwargs):
        """
        Log a message with severity 'INFO' on veplog.
        """

        if set_formatters:
            fmt_old = self.__set_formatters(self.fmt_stdout_info)
            self.log.info(msg, *args, **kwargs)
            self.__set_formatters(fmt_old)
        else:
            self.log.info(msg, *args, **kwargs)

    def _vep_dev(self, arg):
        """
        Print a message only if OPT.devdebug is set.
        Will call self.info()
        Used with common printout that is needed for dev purposes
        """
        if OPT.devdebug:
            # This is a conditional debug message - mocking "DEVDEBUG" %(levelname):
            old_fmts = self.__subs_formatters(r"%\(levelname\)[-]?\d*s", "DEVDEBUG")
            if self.info == self._vep_info:
                self.info(arg, set_formatters=False)
            else:
                self.info(arg)
            # Restore formats:
            self.__set_formatters(old_fmts)

    def _vep_profile(self, msg, time=0.0, threshold=0.0001):
        """
        Print a message only if OPT.print_profile is set.
        Will call self.info()
        Used with common printout that is needed for timing events
        time      : float value. Value passed, typically a delta from an earlier event
        threshold : float value. Only print when time is > than threshold (minimize logging of uninteresting events)
        Example: log.profile("After %-16s %s.%s: %s" % ('sipass', self._trunk, categoryname, sw(lastcall=True)), sw(lastcall=True, pretty=False), threshold=4.0)
        """
        if OPT.print_profile:
            if (time > threshold):
                # This is a conditional debug message - mocking "PROFILE" %(levelname):
                old_fmts = self.__subs_formatters(r"%\(levelname\)[-]?\d*s", "PROFILE ")
                if self.info == self._vep_info:
                    self.info(msg, set_formatters=False)
                else:
                    self.info(msg)
                # Restore formats:
                self.__set_formatters(old_fmts)

    def copy(self, pathfile):
        """
        Copy the log file to pathfile upon logger close.
        This can be called multiple times
        """
        self.copypath.add(pathfile)

    # --- Setup routines ---
    def stdout(self, string_level=None, log_exc=True):
        """Set-up logger to output on stdout."""
        string_level = self._get_and_set_loglevel(string_level)
        self.close()    # close it first
        self._config(filename=None, string_level=string_level, log_exc=log_exc)
        # Using self.fmt_stdout_info
        self.info = self._vep_info      # Using private wrapper to provide overriding in filemixed
        self.s_stdout = True
        self.s_setup = True
        # Why would we not init stdout log if file wasn't set?!?!?
        # if self.is_file_set_once:
        stdout_loglevel = self._get_level(string_level)
        soh = logging.StreamHandler(sys.stdout)
        soh.setLevel(stdout_loglevel)      # stdout, minimum level to be printed
        soh.setFormatter(logging.Formatter(self.fmt_stdout))
        self.log.parent.addHandler(soh)
        self.log.parent.handlers[0].stream = open("/dev/null" if IS_UNIX else "NUL", "a")

    def file(self, filename, string_level=None, usetmp=True, log_exc=True, secondary_logger=False):
        """
        Set-up logger to output on file.
        usetmp - bool. If True then use /tmp to write log first then transfer to filename later
            filename can be None
        secondary_logger - used for 2 cases:
            1. There's already a veplog logfile we were writing to.
                so diverting to secondary logger should not close the original logfile so it can be
            pointed back later on.
            In this case just use the new file, don't close existing or gzip, just write to the new one.
            2. Theres already a DIFFERENT process writing to the same logfile. so, do not do anything intrusive
            like closing the file, even after you're initializing this new "secondary" logger.
        """
        from .files import tempname

        string_level = self._get_and_set_loglevel(string_level)
        if secondary_logger:
            self.s_setup = False
        self.close()    # close it first
        self.input_file = filename
        targ = filename
        if usetmp:
            if self.tmpname is None:
                self.tmpname = tempname()
            targ = self.tmpname
        if not OPT.loglong:
            self.fmt_file = self.fmt_stdout    # Set the format to comply with stdout
        self._config(targ, string_level=string_level, log_exc=log_exc)
        self.__class__.is_file_set_once = True
        if not secondary_logger:
            self.s_setup = True

    def filemixed(self, filename, string_level=None, usetmp=True, secondary_logger=False):
        """
        Mixed output screen and file
        log.debug       -> file only
        log.dev         -> both screen and file
        log.info        -> both screen and file
        log.warning     -> file only
        log.error       -> file only (exception messages, exception is already displayed on screen)
        log.critical    -> both screen and file
        Set filename to None for tmp file logging (use with .copy())
        """
        string_level = self._get_and_set_loglevel(string_level)
        self.file(filename, string_level, usetmp=usetmp, secondary_logger=secondary_logger)
        # Redirected to wrappers (print + log)
        self.dev = self._devXPRIV
        self.info = self._infoXPRIV
        # self.error = self._errorXPRIV
        self.critical = self._criticalXPRIV
        self.profile = self._profileXPRIV

    def filestdout(self, filename, string_level=None, usetmp=True, secondary_logger=False):
        """Set-up logger to output on file and stdout"""
        string_level = self._get_and_set_loglevel(string_level)
        self.file(filename, string_level, usetmp, secondary_logger=secondary_logger)

        # Setup stdout (additional handler)
        stdout_loglevel = self._get_level(string_level)
        soh = logging.StreamHandler(sys.stdout)
        soh.setLevel(stdout_loglevel)      # stdout, minimum level to be printed
        soh.setFormatter(logging.Formatter(self.fmt_stdout))
        self.log.parent.addHandler(soh)
        self.s_stdout = True

    # Decorators:

    def log_wrap_more(self, log_method="debug", verbose=True, timer=False):
        """
        log func name when entering and exiting.
         optional:
         logging args and return_value
         logging benchmark of method runtime
        Usage:
        @log_wrap_more(log_method, ?verbose, ?timer)
        my_func(*args,**kargs)
        """
        def decorator(method):
            try:
                valid_member_names = [n for (n, f) in getmembers(self, predicate=ismethod) if not n.startswith("__")]
                # self.dev(valid_member_names)
                if isinstance(log_method, str) and log_method in valid_member_names:
                    log_method_f = getattr(self, log_method)
                elif callable(log_method) and log_method.__name__ in valid_member_names:
                    log_method_f = log_method
                else:
                    raise IOError
            except BaseException:
                log_method_f = self.debug

            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                pre_str = "method {}".format(method.__name__)
                if verbose:
                    pre_str += ", args: {},{}".format(args, kwargs)

                pre_str += " - Starting..."
                log_method_f(pre_str)
                start_time = time.time() if timer else None
                res = method(*args, **kwargs)

                post_str = "method {}".format(method.__name__)
                if verbose:
                    post_str += ", return_value={}".format(res)
                if start_time:
                    post_str += ", Elapsed in {0:.2f} secs".format(time.time() - start_time)

                post_str += " - Done!"
                log_method_f(post_str)

                return res
            return wrapper
        return decorator

    def log_wrap(self, log_method="debug"):
        """
        Simply log func name when entering and exiting
        Usage:
        @log_wrap(log_method)
        my_func(*args,**kargs)
        """
        return self.log_wrap_more(log_method=log_method, verbose=False)

    # Convenience methods:
    def benchmark_wrap_more(self, log_method="debug"):
        """ Like log_wrap_more() but with verbose=True, timer=True preconfigured """
        return self.log_wrap_more(log_method=log_method, timer=True, verbose=True)

    def benchmark_wrap(self, log_method="debug"):
        """ Like benchmark_wrap_more() but with verbose=False preconfigured """
        return self.log_wrap_more(log_method=log_method, timer=True, verbose=False)

    def debug_benchmark_wrap(self):
        """ Like benchmark_wrap() but with log_method=debug """
        return self.benchmark_wrap(log_method="debug")

    def debug_wrap(self):
        """ Like log_wrap() but with debug preconfigured """
        return self.log_wrap(log_method="debug")

    def debug_wrap_more(self, verbose=True):
        """ Like log_wrap_more() but with log_method=debug timer=False preconfigured """
        return self.log_wrap_more(log_method="debug", verbose=verbose, timer=False)

    def flush(self, text):
        """
        Wrapper to self.info, but call sys.stdout.flush() so that printouts are flushed in buffer.
        Used in streaming stdouts.
        Note that flush is slow()
        Why stdout? The logfile is written in temp, so no point of flushing file output as end-use cannot see
        """
        self.info(text)
        sys.stdout.flush()      # 0.0000015 average run (.0015 mSec)

    # --- Private methods ---

    def _config(self, filename, string_level, log_exc):
        """
        Routine to setup the logger object. Do not call directly.
        string_level is the minimum level of log. If set to "CRITICAL" then only
        critical information is displayed (aka, no display)
        """
        # Note - logging.basicConfig does nothing if a handler is already
        # configured (See logging doc). This cleanup enables to "re-config".
        rootlogger = logging.getLogger()
        # list copy ctor to avoid destructive iteration:
        for handler in list(rootlogger.handlers):
            rootlogger.removeHandler(handler)

        self.log = None

        loglevelno = self._get_level(string_level)
        self.loglevel = string_level
        if filename is None:
            logging.basicConfig(
                stream=sys.stdout,
                format=self.fmt_stdout,
                level=loglevelno    # Master level
            )
        else:
            logging.basicConfig(
                filename=filename,
                format=self.fmt_file,
                level=loglevelno    # Master level
            )

        self.cntcount += 1
        log = logging.getLogger("veplog%d" % self.cntcount)

        self.log = log
        self.logpath = filename
        self.debug = log.debug
        self.info = self.log.info
        # Those are using fmt_stdout
        self.dev = self._vep_dev        # Using private wrapper to provide overriding in filemixed
        self.warning = log.warning
        self.error = log.error
        self.critical = log.critical
        self.profile = self._vep_profile
        self.nocommit = self.log.info

        # Hook to catch and force log exceptions in logger:
        if log_exc:
            vepExceptionManager.register(self._my_excepthook)

    def _initvars(self):
        """Initialize the class variables"""
        self.input_file = None
        self.s_setup = False
        self.s_stdout = False
        self.copypath = set()  # used with .copy() set of paths to copy logfile to

    def _get_and_set_loglevel(self, user_specified):
        """Get loglevel and set it"""
        local_loglevel = self._get_default_loglevel(user_specified)

        if hasattr(self, "loglevel") and self.loglevel != local_loglevel:   # it changed
            self.set_verbosity(local_loglevel)

        return local_loglevel

    def _get_default_loglevel(self, user_specified):
        """Return the loglevel to use"""
        # first - if user specifies in -verbosity_level
        if OPT.verbosity_level:
            return OPT.verbosity_level

        # 2nd - if user specifies in code
        if user_specified is not None:
            return user_specified

        # 3rd - default
        return "DEBUG"

    def _my_excepthook(self, type, value, tb):     # pragma: no cover     (Cannot test this within unittest)
        """Exception handler hook to log Exception messages"""
        self.error("\n%s" % "".join(traceback.format_exception(type, value, tb)))

    def _get_level(self, string_level):
        """Check if the input string is valid or not, then return the numeric code"""
        if string_level not in LOGLEVELS:
            raise Exception("Provided log information [%s] is not a valid log level. "
                            "Valid values are DEBUG,INFO,WARNING,ERROR,CRITICAL"
                            "" % string_level)
        return LOGLEVELS[string_level]

    def _normal_print(self, args):
        """Default print, non-log module"""
        print(args)

    def _devXPRIV(self, args):
        """Display in screen then call _vep_dev' if devdebug is in OPT"""
        # Stdout output: (formatted)
        if OPT.devdebug:
            if isinstance(self.log, logging.Logger):
                old_fmts = self.__subs_formatters(r"%\(levelname\)[-]?\d*s", "DEVDEBUG")
                record = self._str_to_record(args, 'DEBUG')
                print(self.log.parent.handlers[0].format(record))
                self.__set_formatters(old_fmts)
            else:
                print(args)

        # Logger points to file:
        if OPT.loglong:
            self._vep_dev("%s %s" % (sys._getframe(1).f_code.co_name, args))
        else:
            self._vep_dev(args)

    def _profileXPRIV(self, msg, time=0.0, threshold=2.0):
        """Display in screen then call _vep_profile' if print_profile is in OPT"""
        # Stdout output: (formatted)
        if OPT.print_profile and (time > threshold):
            if isinstance(self.log, logging.Logger):
                old_fmts = self.__subs_formatters(r"%\(levelname\)[-]?\d*s", "PROFILE ")
                record = self._str_to_record(msg, 'PROFILE ')
                print(self.log.parent.handlers[0].format(record))
                self.__set_formatters(old_fmts)
            else:
                print(msg)

        # Logger points to file:
        if OPT.loglong:
            self._vep_profile("%s %s" % (sys._getframe(1).f_code.co_name, msg), time, threshold)
        else:
            self._vep_profile(msg, time, threshold)

    def _infoXPRIV(self, args):
        """
        Display in screen then call _vep_info
        """
        # Stdout output: (formatted)
        if isinstance(self.log, logging.Logger):
            old_fmt = self.__set_formatters(self.fmt_stdout_info)
            record = self._str_to_record(args, 'INFO')
            print(self.log.parent.handlers[0].format(record))
            self.__set_formatters(old_fmt)

            # Logger points to file:
            if OPT.loglong:
                self._vep_info("%s %s" % (sys._getframe(1).f_code.co_name, args))
            else:
                self._vep_info(args)
        else:
            print(args)

    def _errorXPRIV(self, args):
        """
        Display in screen then call log.error()
        """
        # Stdout output: (formatted)
        if isinstance(self.log, logging.Logger):
            record = self._str_to_record(args, 'ERROR')
            print(self.log.parent.handlers[0].format(record))
            # Logger points to file with filemixed:
            if OPT.loglong:
                self.log.error("%s %s" % (sys._getframe(1).f_code.co_name, args))
            else:
                self.log.error(args)
        # If using set_log_methods_to_print() no use to print twice
        else:
            print(args)

    def _criticalXPRIV(self, args):
        """
        Display in screen then call self.critical()
        """
        # Stdout output: (formatted)
        if isinstance(self.log, logging.Logger):
            record = self._str_to_record(args, 'CRITICAL')
            print(self.log.parent.handlers[0].format(record))
            # Logger points to file:
            if OPT.loglong:
                self.log.critical("%s %s" % (sys._getframe(1).f_code.co_name, args))
            else:
                self.log.critical(args)
        # If using set_log_methods_to_print() no use to print twice
        else:
            print(args)

    def _str_to_record(self, msg, level='INFO'):
        """
        Take a string message and valid level string and return a matching logging.LogRecord object
        """
        # Bug in logging getLevel mechanism when working with logging.makeLogRecord(msg_dict)
        return logging.LogRecord('_veplogXPRIV', LOGLEVELS[level], 'unavailable',
                                 'unavailable', msg, None, None, None)

    def __subs_formatters(self, pattern, subst):
        """
        Sustitutes pattern string with subst string in all formatters of all handlers of log.parent
        :return: Returns a list of the original format strings (for easy restore)
        """
        fmt_old = []
        if isinstance(self.log, logging.Logger):
            for idx, handler in enumerate(self.log.parent.handlers):
                fmt_old.insert(idx, handler.formatter._fmt)
                new_fmt = re.sub(pattern, subst, fmt_old[idx])
                handler.setFormatter(logging.Formatter(new_fmt))
        return fmt_old

    def __set_formatters(self, new_fmt=None):
        """
        Sets all log.parent.handlers formatters to the formatters in new_fmt_list
        If new_fmt_list is not string/list - does nothing, except returning the old formats
        :return: list of the original format strings (for easy restore)
        """
        fmt_old = []
        if isinstance(self.log, logging.Logger):
            for idx, handler in enumerate(self.log.parent.handlers):
                fmt_old.insert(idx, handler.formatter._fmt)
                if isinstance(new_fmt, str):
                    handler.setFormatter(logging.Formatter(new_fmt))
                elif isinstance(new_fmt, list) and len(new_fmt) > idx:
                    handler.setFormatter(logging.Formatter(new_fmt[idx]))

        return fmt_old

    def _postproc_XPRIV(self, fname):
        """
        Given file with lines containing:
           2013-12-05 18:55:32,187 _infoXPRIV      funcname This is info
        replace with:
           2013-12-05 18:55:32,187 funcname        This is info
        """
        from .files import File

        reg = regex.compile(r'(_infoXPRIV)(\s+)(\S+)')
        fname_w_orig = os.path.join(fname + ".orig")
        fread = File(fname).rename(basename(fname_w_orig))
        with open(fname, "w") as fho:
            for line in fread:
                res = reg.search(line)
                if res:
                    length = self.funclen - len(res.group(3))
                    line = line.replace(res.group(1) + res.group(2) + res.group(3),
                                        res.group(3) + ''.join(' ' for x in range(length)))
                fho.write(line)
        fread.close()
        File(fname_w_orig).unlink()

    def _close_inputfile(self):
        """close input file"""
        # If usetemp is True, then copy to real area then compress
        from .files import File

        # print " In veplog_base._close_inputfile"
        if self.compresstype is None:
            self.compresstype = File.gz
        if self.tmpname is not None and exists(self.tmpname):
            self._postproc_XPRIV(self.tmpname)
            ff = File(self.tmpname)
            # Do the copy, if specified
            for path in self.copypath:
                ff.copy(path, xfer=False)
            if self.input_file is None:
                ff.unlink()
            else:
                ff.move(dirname(self.input_file))
                try:
                    ff.rename(basename(self.input_file))
                    ff.compress(self.compresstype)
                except OSError as e:   # pragma: no cover    tested in test_file_exception2()
                    print(f"-i- Warning: Rename+compress failed: {e}")
            return

        if self.input_file is not None and exists(self.input_file):
            self._postproc_XPRIV(self.input_file)
            fh = File(self.input_file)
            fh.compress(self.compresstype).chmod("0755")
            fh.close()

#    def __call__(self, *args):   # Cannot use __call__ since log file (funcName) is screwed up (traceback info)
#        """As a callable, use .info"""
#        message = ' '.join(args)
#        self.info(message)


def logline(logfile, txt):
    """
    Given a logfile, append the line txt with log information added:
       username, machinename, time
    """
    from .shell import USERNAME, HOSTNAME

    text = "%-10s %-15s %s %s" % (USERNAME,
                                  HOSTNAME,
                                  time.strftime("%m-%d-%Y %H:%M:%S"),
                                  txt)
    if logfile is None:
        return text

    if not exists(logfile):
        raise Exception("Logfile %s must exist first. Pls create this file with 775 permissions." % logfile)

    with open(logfile, "a") as fh:
        fh.write("%s\n" % text)


log = VepLog()
