#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Various routines on files and iterating on the contents of the files
"""

import sys
import os
import bz2
import gzip
import shutil
import io
import atexit
import time
import hashlib
import re
import os.path as op
from collections import deque
from .gizmo import count_iter, Elapsed
from .strmore import regex, sha1, indent, to_str, to_bytes, uniq_sha
from os.path import basename, dirname, isdir, exists, join, realpath, islink
from .helperclass import Enum, ExceptionEnv, IS_UT


def strmode_to_int(mode):
    """
    Given the permission mode in string (either '0750' or '750')
    it will return the int value for use in os commands that use mode (mkdir, chmod, etc)
    """
    if not isinstance(mode, str):
        raise Exception("Mode needs to be a string. Provided mode is a %r" % type(mode))
    mode = mode.replace('o', '')   # in python3: oct(0o750) will return '0o750'
    if not mode.isdigit():
        raise Exception("chmod mode %r must be digits" % (mode))

    if len(mode) == 4:     # e.g. 0770
        if not mode.startswith('0'):
            raise Exception("chmod mode %s is 4 characters, must start with leading 0!" % (mode))
    elif len(mode) == 3:   # e.g. 770
        mode = '0' + mode   # add leading 0
    elif len(mode) == 5:   # e.g. 02750
        if not mode.startswith('0'):
            raise Exception("chmod mode %s is 5 characters, must start with leading 0!" % (mode))
    else:
        raise Exception("chmod mode %r should be 3-4 characters long" % (mode))

    return int(mode, base=8)


def strip(iter_or_arr, left=False, right=False):
    """
    Iterator to return the strip() of iter_or_arr.
    Set left=True  for lstrip()
    Set right=True for rstrip()
    Example:
    >>> for line in strip(['  a  ', 'b ', ' c']): print '%r' % line
    'a'
    'b'
    'c'
    """
    if left and right:
        raise Exception("Cannot specify both left and right to be True")
    elif left:
        for line in iter_or_arr:
            yield line.lstrip()
    elif right:
        for line in iter_or_arr:
            yield line.rstrip()
    else:
        for line in iter_or_arr:
            yield line.strip()


def grep(searchtext, iter_or_arr, strip=False, r=False):
    r"""
    grep-like functionality given an iterator or array.

    '^<text>' and '<text>$' are implemented via python strings (efficient).

    Options:
       r=True: Use Standard regex
       strip=True: strip() the line before comparison

    Examples:
       >> for line in grep('Pat', fh):                # 'Pat' anywhere in the line
       >> for line in grep('^Pat', fh):               # starts with Pat
       >> for line in grep('Pat$', fh):               # ends with Pat
       >> for line in grep('Pat$', fh, strip=True):   # ends with Pat after strip() is called
       >> for line in grep('Pat\s+\w+', fh, r=True):  # use regex
       >> arr.extend(grep('pat.gz',fh))               # use hash.update(grep()) for set or dict
       >> print '\n'.join(grep('pat.gz',fh))          # print the grep result
    """
    # CCO number is 21. It is implemented this way in favor of performance.
    # It is quite large, and this function cannot be broken up because of "yield" statement.

    if r:
        # use regex ==========================================
        reobj = regex.compile(searchtext)

        if strip:
            for line in iter_or_arr:
                if reobj.search(line.strip()):
                    yield line
        else:
            for line in iter_or_arr:
                if reobj.search(line):
                    yield line

    elif searchtext[0] == '^':
        # search start of string ==========================================
        searchtext = searchtext[1:]
        if strip:
            for line in iter_or_arr:
                if line.strip().startswith(searchtext):
                    yield line
        else:
            for line in iter_or_arr:
                if line.startswith(searchtext):
                    yield line

    elif searchtext[-1] == '$':
        # search end of string ==========================================
        searchtext = searchtext[:-1]
        if strip:
            for line in iter_or_arr:
                if line.strip().endswith(searchtext):
                    yield line
        else:
            for line in iter_or_arr:
                if line.endswith(searchtext):
                    yield line

    else:
        # search any string ==========================================
        for line in iter_or_arr:      # no need to put strip here (useless)
            if searchtext in line:
                yield line


def grepv(searchtext, iter_or_arr, strip=False, r=False):
    r"""
    'grep -v' functionality given an iterator or array.
    'grep -v' is a blacklist grep.

    '^<text>' and '<text>$' are implemented via python strings (efficient).

    Options:
       r=True: Use Standard regex
       strip=True: strip() the line before comparison

    Examples:
       >> for line in grepv('Pat', fh):                # lines without 'Pat'
       >> for line in grepv('^Pat', fh):               # not starts with Pat
       >> for line in grepv('Pat$', fh):               # not ends with Pat
       >> for line in grepv('Pat$', fh, strip=True):   # not ends with Pat after strip() is called
       >> for line in grepv('Pat\s+\w+', fh, r=True):  # use regex
       >> arr.extend(grepv('pat.gz',fh))               # use hash.update(grep()) for set or dict
       >> print '\n'.join(grepv('pat.gz',fh))          # print the grepv result
    """
    # The function implemented in favor of performance
    # It is quite large, and this function cannot be broken up because of "yield" statement.
    if r:
        # use regex ==========================================
        reobj = regex.compile(searchtext)

        if strip:
            for line in iter_or_arr:
                if not reobj.search(line.strip()):
                    yield line
        else:
            for line in iter_or_arr:
                if not reobj.search(line):
                    yield line

    elif searchtext[0] == '^':
        # search start of string ==========================================
        searchtext = searchtext[1:]
        if strip:
            for line in iter_or_arr:
                if not line.strip().startswith(searchtext):
                    yield line
        else:
            for line in iter_or_arr:
                if not line.startswith(searchtext):
                    yield line

    elif searchtext[-1] == '$':
        # search end of string ==========================================
        searchtext = searchtext[:-1]
        if strip:
            for line in iter_or_arr:
                if not line.strip().endswith(searchtext):
                    yield line
        else:
            for line in iter_or_arr:
                if not line.endswith(searchtext):
                    yield line

    else:
        # search any string ==========================================
        for line in iter_or_arr:      # no need to put strip here (useless)
            if searchtext not in line:
                yield line


def tempname(suffix=None, _cnt=[0]):          # unittested
    """
    Returns a temporary filename (in /tmp)
    This is an improved version of tempfile since tempfile uses random chars which has
    chance of same name (PCAR encountered this).
    This just returns the filename.
    It will not delete the file. Use TempName class for auto deletion.
    This adds the name of caller script (sys.argv[0]) and caller subroutine in tempname.
       example: fname=tempname()   # fname is /tmp/tmpbyxJvd.scriptname.callerfuncname
    """
    if len(sys.argv[0]) > 0:
        pyname = basename(sys.argv[0]).replace('.py', '').split()[0]   # remove .py extension
    else:
        pyname = "none"

    if suffix is None:
        suffix = sys._getframe(1).f_code.co_name.replace('<', '').replace('>', '')

    for ii in range(1000):  # max 1000 tries
        _cnt[0] += 1
        key = "{usha} {pid} {time} {ii} {cnt}".format(usha=uniq_sha(),
                                                      pid=os.getpid(),
                                                      time=str(time.time()),
                                                      ii=ii,
                                                      cnt=_cnt[0])
        uniq_key = sha1(key)[:12]   # 12 chars is 2^48 - huge compbination
        name = join(shell.tmpdir(), "tmp%s.%s.%s.%s" % (uniq_key, shell.USERNAME, pyname, suffix))
        if not exists(name):
            return name

    raise Exception('tempname(): Cannot get temporary name')


def check_and_del(fname, error=True, mv_on_error=False):
    """
    Checks existence then delete it (file or directory)

    :param fname: Required name
    :param error: Set to False if silent error
    :param mv_on_error: Rename the target if there is error
    :return: None
    """
    if not exists(fname):
        return    # Do nothing

    try:
        if isdir(fname):
            disk.rmtree(fname)
        else:
            os.unlink(fname)

    except BaseException:
        if mv_on_error:
            File(fname).rename_incremental()
        elif error:
            raise


def glob_one_only(wildcard):
    """
    Returns one file from wildcard, do check to make sure it is only one

    :param wildcard: string glob wildcard
    :return: string: First output of wildcard. Error if none or multiple.
    """

    import glob
    from .errors import confirm

    varlist = glob.glob(wildcard)
    confirm(len(varlist) >= 1,
            f'No file found in {wildcard}',
            f'Expecting 1 file.')
    confirm(len(varlist) == 1,
            f'Multiple files found: {sorted(basename(x) for x in varlist)}',
            f'Expecting one only for {wildcard}')
    return varlist[0]


class TarFolder:
    r"""
    Wrapper to tar.gz for testprogram transfers so it is fast.
    Ignore ".git" folders
    destinationfolder is assumed to be I:\ drive
    TarFolder(sourcefolder, destinationfolder)         # called in windows
    DataHost.do_untar(f'{destinationfolder}/tp.tar.gz')    # called in unix
    """

    def __init__(self, src, desttar):
        """Create the tar"""
        import tarfile
        assert desttar.endswith('.tar.gz'), f'tarname [{desttar}] must end with .tar.gz'
        disk.mkdirs(dirname(desttar), '02770')
        with tarfile.open(desttar, "w:gz") as tarfh:
            with disk.Chdir(src):
                tarfh.add('.', filter=self._ignore)

    def _ignore(self, obj):
        """Ignore .git filders"""
        fpath = obj.path
        if '/.git/' in fpath or fpath.endswith('/.git'):
            return None
        return obj


class TempName:
    """
    An object that will give temporary file name(s) (not a filehandle).
    It will delete the file name(s) if exist, upon object deletion.
    It can also be used with 'with' statement (This is the suggested usage)
    This differs with tempfile.NamedTemporaryFile where tempfile returns a filehandle (File is deleted after close())
    Sometimes you want to use/read the tempfile even if it closed after writing.
    If tmp file has .gz extension, it will also delete it.

    Set delete=False to keep the tempname(do not delete). Useful for debug.
    Set name=True for ContextManager to return the name of the directory.
    Set exe=<codestring> for temporary executable creation

    Usage:
       with TempName() as tobj:
            print tobj.name()        # Tempname (created at init)
            tname1 = tobj.fname()    # create additional new name
            tname2 = tobj.fname()    # create additional new name

    Usage2: Create a temporary executable (used with unittests):
       code='''import gadget.files as f
       # some code
       '''
       with TempName(exe=code) as tobj:
           os.system(tobj.name())

    Usage3: Contextmanager returns name
       with TempName(name=True) as tmp:
            print tmp        # /tmp/tmpsomething

    """

    def __init__(self, exe=None, name=False, delete=True, _callerfunc=None, samename=None):
        """
        Set exe to a string/lines-of-code and it will create an executable
        Set name to True and context-manager return will be the tempname
        Set samename to <name>, and tempname will be /tmp/<username>_<samename> (not a unique name)
        """
        self.names = set()           # set of temprary names created
        self.cmname = name            # bool to indicate context manager to return name or object
        self.closed = False
        self.delete = delete
        self.tname = None
        self.samename = samename

        if _callerfunc is None:
            self._callerfunc = sys._getframe(1).f_code.co_name.replace('<', '').replace('>', '')
        else:
            self._callerfunc = _callerfunc

        if exe is not None:
            self.write_exe(exe)

        # Need to store the functions since it is used in DESTROY. The modules may be gc'ed
        self.exists = exists
        self.unlink = os.unlink
        self.isdir = isdir
        self.rmtree = disk.rmtree

    def get_name(self):
        """Just for standardization"""
        return self.name()

    def name(self):
        """
        Returns a temporary name (not a filehandle).
        It will return the same temporary name for the object if called several times.
        """
        if self.tname is None and (not self.closed):
            self.tname = self.fname(callerfunc=self._callerfunc)

        # Extra routine to guarantee deletion upon python exit
        if self.delete and (not self.closed):
            atexit.register(check_and_del, self.tname, error=False)    # guarantee deletion upon exit

        return self.tname

    def write_exe(self, code):
        """
        Write a python executable (with shebang line), and change it's mode to executable
        """
        with open(self.name(), "w") as fh:
            fh.write('#!%s\n%s\n' % (sys.executable, code))
        os.chmod(self.name(), 0o775)

    def __enter__(self):
        """
        Context Manager enter
        This method should be very minimal for TempName, since TempName usage
        can be non-context-manager, e.g. See BgCmd()
        """
        if self.cmname:
            return self.name()

        return self

    def __exit__(self, *arg):
        """Context manager exit"""
        self.close()

    def close(self):
        """Deletes the temporary file names created, if existent"""
        if (not self.closed) and self.delete:
            for name in self.names:
                for ext in ("", ".gz"):
                    if self.exists(name + ext):
                        if self.isdir(name + ext):
                            try:
                                self.rmtree(name + ext)
                            except BaseException:   # suppress exception when rmtree fails (e.g. for "device or resource busy" during crons)
                                pass
                        else:
                            self.unlink(name + ext)

        self.closed = True
        self.tname = None
        self.names = set()

    def fname(self, callerfunc=None):
        """
        Returns a temporary file name (not a filehandle).
        Can be called multiple times (will give different names)
        """
        if callerfunc is None:
            callerfunc = sys._getframe(1).f_code.co_name.replace('<', '').replace('>', '')

        if self.samename:
            tname = "/tmp/%s_%s" % (shell.USERNAME, self.samename)
        else:
            tname = tempname(callerfunc)

        self.names.add(tname)

        # identify if delete or not
        if 'PYNODELTMP' in os.environ:
            if os.environ['PYNODELTMP'] in tname:
                self.delete = False
                self._addendprint(tname)

        return tname

    @classmethod
    def _addendprint(cls, tname, myset=set()):
        """
        1. Add this tempname for printout later
        2. Upon atexit, print the tempnames that were not deleted and change permission as well
        """
        # Register this tname
        if tname is not None:
            if len(myset) == 0:
                atexit.register(cls._addendprint, None)    # one time register only
            myset.add(tname)
            return

        # Display and chmod  -- this portion is executed upon python exit
        for ff in myset:
            if exists(ff):
                disk.chmodr(ff, "0770")
                print("##### TEMP not deleted: %s" % ff)

        return myset    # for unittest


class TempDir(TempName):
    """
    Creates a temporary directory, by using TempName capability.
    Context Manager friendly and guarantees deletion upon python exit.

    Always use TempDir as a context manager to guarantee directory deletion:
        with TempDir() as tdir:
            print('dir:', tdir.name())
    """
    set_display = 0     # global/class setting to display the number of files before deletion

    def __init__(self, chdir=False, delete=True, name=False, otherdir=None,
                 samename=None, display=False, copydir=None, startcopy=None):
        """
        :param chdir: Set to True to chdir to that tempdir (and will return back chdir upon close())
        :param delete: Set to False to keep the tempdir (do not delete). Useful for debug.
        :param name: Set to True to return the name of the directory.
        :param otherdir: <alternate_temp_dir> for a different dir, like tvpv/trashdir
        :param samename: <name>: tempname will be /tmp/<username>_<samename> (not a unique name)
        :param display: Set to True so that contents of tempdir is displayed during close()
        :param copydir: <emptydir>: to copy tempdir into <emptydir> during close()
        :param startcopy: <dirpath>: to copy <dirpath> at init time.
        """
        callerfunc = "_" + sys._getframe(1).f_code.co_name.replace('<', '').replace('>', '')
        TempName.__init__(self, name=name, delete=delete, _callerfunc=callerfunc, samename=samename)
        self.is_display = display
        self.copydir = copydir
        assert (not self.copydir) or (not exists(self.copydir)), f'TempDir() copydir: {self.copydir} must not exist.'

        # create the dir
        self._windows_d_drive()
        self._special_infra_folder()
        self._use_otherdir(otherdir)
        tdir = self.name()
        if not isdir(tdir):
            disk.mkdirs(tdir, '02770')

        # Copy a starting directory if specified
        if startcopy:
            from .disk import chmodr
            os.rmdir(tdir)
            shutil.copytree(startcopy, tdir)
            chmodr(tdir, '0770')

        # chdir
        self.origdir = None
        if chdir:
            try:
                self.origdir = os.getcwd()   # it's possible that cwd is a stale dir
            except BaseException:
                self.origdir = None
            self.chdir = os.chdir
            os.chdir(tdir)

        # store TempName so it won't be garbage collected
        self.class_tempname = TempName

    def _special_infra_folder(self, _folder='/infrastructure/p6vector/tmp'):
        """
        On unix, favor /infrastructure/p6vector/tmp folder vs /tmp folder, if it exist because of infra machine
        """
        if not shell.IS_UNIX:
            return 1     # do nothing for windows
        if not os.path.isdir(_folder):
            return 2

        if not self.name().startswith('/tmp'):
            return 3

        self.tname = f'{dirname(_folder)}{self.name()}'
        self.names.add(self.tname)
        return 4

    def _windows_d_drive(self):
        """
        On windows, favor D: drive, if exist since it has more space than C
        Fallback to Python built in C drive TempDir if D: is not writable
        """
        if shell.IS_UNIX:
            return 1     # do nothing for unix
        if not isdir("D:\\"):
            return 2     # D:\ drive does not exist
        from .errors import check, ErrorConfig
        try:
            check.is_dir_writable("D:\\TempDir")
        except ErrorConfig:
            return 4  # not writable
        self.tname = join("D:\\TempDir", basename(self.name()))
        self.names.add(self.tname)
        return 3

    def _use_otherdir(self, otherdir):
        """otherdir is an alternative directory like tvpv/trashdir"""
        if otherdir is None:
            return
        if not isdir(otherdir):
            raise Exception("Input [%s] is not a valid directory" % otherdir)
        self.tname = join(otherdir, basename(self.name()))
        self.names.add(self.tname)

    def close(self):
        """Delete the tempdir"""
        # copy first
        if self.copydir:
            from .pylog import log    # to support py3 imports
            sw = Elapsed()
            try:
                shutil.copytree(self.name(), self.copydir)     # self.dest_idrive directory must not exist
                log.info(f'-i- TempDir copytree to {self.copydir} in {sw}')
            except Exception as e:
                log.info(f'-e- TempDir copytree failed: {e}')

        # display the contents, if it is not a unittest
        if self.is_display:
            display_count = 100000  # display all files
        else:
            display_count = self.set_display

        if display_count > 0:
            from .pylog import log    # to support py3 imports
            content = File(self.name()).lsltrd('-ltr').split('\n')
            displaynum = content[-display_count:]
            log.debug("tempdir contents: %s\n%s" % (self.name(),
                                                    indent(3, displaynum)))

        # chdir specific
        if self.origdir is not None:
            if isdir(self.origdir):
                self.chdir(self.origdir)
            self.origdir = None

        self.class_tempname.close(self)    # call the base class close object

    @classmethod
    def cleanup(cls, daysold=7, disponly=False):
        """
        Deletes all tmp folders older than daysold
        Call this once at top of tool.
        """
        if IS_UT:
            return -1       # Do not run in unittests

        if shell.IS_UNIX:   # Do not run in unix, there might be some cron running in the machine.
            return -2

        # Get system rootdir
        with TempDir(name=True) as tdir:
            rootdir = dirname(tdir)

        todelete = []
        with os.scandir(rootdir) as fhdir:
            for entry in fhdir:
                if not (len(entry.name.split('.')) == 4 and entry.name.startswith('tmp')):
                    continue    # not created by TempDir()
                if (time.time() - entry.stat().st_mtime) > (daysold * 86400):
                    todelete.append(f'{rootdir}/{entry.name}')

        # delete them
        from .pylog import log
        for fname in todelete:
            log.info(f'-i- TempDir cleanup delete: {fname}')
            if not disponly:
                check_and_del(fname, error=False)

        return len(todelete)


def basename_delext(fname):
    """Returns the basename and removes any extension"""
    return basename(fname).split('.')[0]


def basename_n(fname, n):
    """
    Returns the name given n where n is elements starting at end
    :param fname: pathname
    :param n: 1 means Basename(), 2 means dirname() and basename()
    :return: oath
    """
    ap = os.path.abspath(fname)
    result = []
    newpath = ap
    for idx in range(n):
        newpath, bname = os.path.split(newpath)
        if not bname:
            break
        result.append(bname)
    return join(*reversed(result))


class File:
    """
    File object that knows compression and tracks it's location.
    Note: Filehandles are not meant to be written (aka, readonly).

    Usage examples:

    1. Iterate lines of a compressed file:
          for line in File('file.gz'):
              # some code to process line

          for line in File('file.gz', return_fh=True).fh():    # More-efficient version
              # some code to process line

    2. Iterate lines of a compressed file via with:
          with File('file', autofind=True, return_fh=True) as fh:    # will try 'file.gz' if 'file' does not exist.
             for line in fh:
                 # some code to process line

    3. Iterete lines of a file, remove newline char:
          for line in File('file.gz').chomp():
              # some code to process line, without newline

    4. Write to a compressed file directly (only possible with context manager):
          with File('myfile.gz', mode='a', return_fh=True) as fh:
              fh.write('I am appending this line')

    5. Compress a particular file:
          ff = File('myfile')
          ff.compress(File.gz)
          print ff.get_name()    # 'myfile.gz'

    More examples in the different methods.

    """

    # Compression types definition (class attribute)
    _comptypes = Enum(gzbz2='.gz.bz2', bz2gz='.bz2.gz', gz='.gz', bz2='.bz2', none='')
    gzbz2 = _comptypes.gzbz2    # shortcut
    bz2gz = _comptypes.bz2gz    # shortcut
    gz = _comptypes.gz       # shortcut
    bz2 = _comptypes.bz2      # shortcut
    none = _comptypes.none
    _comporder = [gzbz2, bz2gz, gz, bz2, none]    # none must be the last. double compresion first.
    assert set(_comptypes.indices()) == set(_comporder)   # check that comptypes and comporder is matching

    def __init__(self, filename=None, autofind=False, mode=None, fast=False, autoregex=False, return_fh=False):
        r"""
        Set autofind to True to find the file irregardless of compression.
           will raise exception if no file found.
        mode is used in context manager only, Append or Write directly to a compressed file

        Set fast=True for fast __init__, do not consider what kind of compression is it. autofind is also disabled.
        autoregex will assume that filename is a regex raise an IOError if more than one file matches the given regex:
            Example: /path/\w+\.txt

        By default it returns a file object (return_fh=False). Set return_fh to True to return a file handle
        instead of the file object.
        """
        if fast:
            self.name = filename
            self.origname = filename
            self.compression = self.none    # compression is a don't care for fast=True
        else:
            self.name = self._proc_name(filename, autofind, autoregex)  # filename - modified as File is manipulated.
            self.origname = self.name                             # Original name. This will not be changed.
            self.compression = self._get_compression(self.name)      # Compression type

        self._fh = None          # filehandle (to indicate if open or not)
        self._fh1 = None
        self.opsuccess = None    # unittest only attribute, to indicate if operation is successful
        self.mode = mode         # used in context manager. Append or Write directly to a compressed file
        self.return_fh = return_fh      # flag to return file handle (True) or File object (False, default)

    def _proc_name(self, filename, autofind, autoregex=False):
        """
        Set a random filename if filename is None (used with the other function like chomp(), etc)
        Process the autofind
        filename is assumed to be a fullpath containing a regex if autoregex is set
        pytpd: case insensitive by default
        """
        if filename is None:
            return "File.None." + str(time.time())   # any unique filename

        # case insensitive check
        if shell.IS_UNIX and (not exists(filename)):
            tryname = self.realname(filename)
            if exists(tryname):
                return tryname

        if not autofind and not autoregex:
            return filename

        # Handle Regex search
        if autoregex:
            fdir = dirname(filename) if dirname(filename) else "./"
            fname_regex = basename(filename)
            match_files = [f for f in os.listdir(fdir) if re.search(fname_regex, f)]
            if len(match_files) > 1:
                raise IOError("Multiple files (%d) in %s match regex %s. Cannot determine which to use. (%s)" %
                              (len(match_files), fdir, fname_regex, ','.join(match_files)))
            elif len(match_files):
                res = match_files[0] if fdir == "./" else join(fdir, match_files[0])
                return res
            else:
                raise IOError("No such file in %s matching regex: %s" % (fdir, fname_regex))

        # Process the autofind at this point ============================
        if exists(filename):
            return filename        # default filename
        noext = File(filename).del_ext()
        for ext in self._comporder:
            if exists(noext + ext):
                return noext + ext

        raise IOError("No such file with any compression combination: %r" % noext)

    def _get_compression(self, name):
        """
        Returns the compression type: .gz .bz2 .gz.bz2 .bz2.gz
        Returns '' (empty string) for no compresion
        """
        for ext in self._comporder:
            if name.endswith(ext):
                return ext
        else:  # pragma: no cover    (unreachable code - File.none will always true)
            raise Exception('This code should never be reached!')

    def safeopen(self):
        """
        Iterator, for opening files that may contain incorrect encoding.
        This will not check compression
        Will rstrip lines

        for line in File(fname).safeopen():
            <dosomething>

        :return: line with rstrip removed.
        """
        assert self.compression == '', "safeopen() cannot work with compressed files."
        with open(self.get_name(check_exist=True), 'rb') as fh:
            for line in fh:
                yield line.decode(errors='ignore').rstrip()

    @classmethod
    def realname(cls, fname):
        """
        Return fname (asis) if it exist, then try to see if case-insensitive name exist, then return that
        else, return fname (asis) if not found.
        :param fname:
        :return: updated fname
        """
        if exists(fname):
            return fname    # as-is, it already exist

        dname = dirname(fname)
        if not dname:
            dname = '.'
        if not exists(dname):
            return fname    # as-is
        mapfiles = {x.lower(): x for x in os.listdir(dname)}
        lowername = basename(fname).lower()
        if lowername in mapfiles:
            return f'{dname}/{mapfiles[lowername]}'
        else:
            return fname    # as-is, none found

    def raw(self, islist=True):
        """
        Open the file, return "raw" lines, with unicode checks
        Used with postprocess + rewrite() routines.

        :return: list of lines with line endings
        """

        with open(self.get_name(check_exist=True), errors='replace') as fh:
            if islist:
                return list(fh)
            else:
                return fh.read()

        # This is unreachable code, safety only
        raise IOError('Something went wrong with raw(%r)' % self.get_name())   # pragma: no cover

    def chomp(self, arr=None, strip=False, comment=None):
        """
        Iterator, removes newline (\\n and \\r) character, similar to perl chomp().
        arr, if provided, will be used as the source (any iterator/sequence that output a string)
             Default source is the file contents.
        comment=<char|string>, if provided lines that start with comment are stripped.
                 New lines are removed, leading and trailing space are removed (like strip=True)
                 Set comment='', if just want to get rid of empty lines.
        Set strip=True to do leading and trailing strip. By default it is False (rstrip only)

        Example:
            for line in File(file).chomp():     # line will not contain newline

        # Performance of multi-level call (clean code) vs single-level call (more complex code)
        # 10M iterator        py3      py11      pypy
        # one level:          0.87     0.69      2.6   (via count_iter())
        # one level:          1.33     1.43      0.07  (via for enumerate())
        # one level: (best)   0.87     0.68      0.07  (via best)
        # two level call:     1.29     1.00      0.14  (via best)
        # 3   level call:     1.70     1.34      0.27  (via best)
        # Summary per level:  0.41/10M 0.32/10M  0.1/10M
        """
        # Determine the source
        if arr is None:
            targ = self.fh()
        else:
            targ = arr

        # Do the comment
        try:
            if comment is not None:
                for line in targ:
                    res = line.strip()
                    if len(res) > 0:
                        if comment == "" or (not res.startswith(comment)):
                            yield res

            # Do the strip
            elif strip:
                for line in targ:
                    yield line.strip()        # this removes \n+,\r+; performance for one-line or two-lines is the same

            else:
                for line in targ:
                    yield line.rstrip()        # this removes \n+,\r+; performance for one-line or two-lines is the same

        except AttributeError:
            pass

        # Close if filehandle
        if arr is None:
            targ.close()   # close the file handle

    def get_name(self,
                 check_exist=False,
                 abspath=False,
                 realpath=False,
                 dirname=False,
                 basename=False,
                 basenoext=False):
        '''
        Returns the object filename
        Will not check existence by default. Set check_exist=True to check.

        >>> os.chdir("/tmp/mypath")
        >>> File("myfile").get_name()
        'myfile'
        >>> File("myfile").get_name(abspath=True)
        '/tmp/mypath/myfile'
        >>> File("myfile").get_name(abspath=True, dirname=True)
        '/tmp/mypath'
        >>> File("myfile").get_name(abspath=True, basename=True)
        'myfile'
        >>> File("myfile").get_name(abspath=True, dirname=True, basename=True)
        'mypath'
        >>> File("/tmp/mypath/myfile.gz").get_name(basename=True)
        'myfile.gz'
        >>> File("/tmp/mypath/myfile").get_name(dirname=True)
        '/tmp/mypath'
        >>> File("/tmp/mypath/myfile.pat.gz").get_name(basenoext=True)
        'myfile.pat'
        '''
        name = self.name
        if check_exist and (not exists(name)):
            raise IOError("No such file: %r" % name)

        if basenoext:
            name = op.basename(self.del_ext())     # removes compression only
        if abspath:
            name = op.abspath(name)
        if realpath:
            name = op.realpath(name)
        if dirname:
            if not (abspath or realpath):
                name = op.abspath(name)    # make it absolute path first
            name = op.dirname(name)
        if basename:
            name = op.basename(name)
        return name

    def fh(self, mode=None, is_text=True, check_exist=True):
        """
        Returns the opened filehandle of the file.

        :param mode: Specify mode during open of non-compressed file
        :param is_text: Set to False for binary files. True for text (default)
        :param check_exist: Check if file exist
        :return: file handle of file

        """

#    if file == 'stdin':      #pragma: no cover
#        pr = subprocess.Popen('cat', stdout = subprocess.PIPE, stderr = open("/dev/null","w"), universal_newlines=True)
#        return pr.stdout   # return file handle, context-api ok

        self.close()
        f = self.get_name(check_exist)

        # Get mode
        errors = {}
        if mode is not None:
            umode = mode
            umode1 = mode
        elif is_text:
            umode = 'rt'
            umode1 = 'r'
            errors = {'errors': 'replace'}
        else:   # not is_text
            umode = 'rb'
            umode1 = 'rb'

        # select which compression
        if self.compression == self.gzbz2:
            self._fh1 = bz2.BZ2File(f, mode=umode1)
            if is_text:
                self._fh = io.TextIOWrapper(gzip.GzipFile(fileobj=self._fh1, mode=umode1))
            else:
                self._fh = gzip.GzipFile(fileobj=self._fh1, mode=umode1)

        elif self.compression == self.gz:
            self._fh = gzip.open(f, mode=umode, **errors)

        elif self.compression == self.bz2:
            self._fh = bz2.open(f, mode=umode, **errors)

        elif self.compression == self.none:     # uncompressed
            self._fh = open(f, mode=umode, **errors)     # errors='replace' to ignore unicode

        else:
            raise Exception(f"File {f} with {self.compression} is unsupported")

        return self._fh

    def is_win_crlf(self):
        """
        Returns True if file is windows crlf.
        If file does not exist, return False (default to unix)

        :return: bool
        """
        if self.exists():
            with open(self.get_name(), 'rb') as f:
                return b'\r\n' in f.read(1024 * 4)
        return False

    def rewrite(self, final, where, keep=None, check=True):
        """
        Overwrite file with final text, with log and option to keep old.

        :param final: long string
        :param where: info on where is this coming from
        :param keep: string (extension name): If set, keep old file. Do not overwrite .old file since
                     rewrite() can be called many times on the same file.
        :param check: check if file is the same. Do nothing if they are the same
        :return: True if rewrite happened. False if not
        """
        from .pylog import log
        assert not self.compression, f'File({self.name}).rewrite() only works with no compression'
        oldname = 'old' if not keep else keep

        # Do nothing if exactly the same
        if check and self.exists():
            if self.read() == final:
                # if self.read().replace('\r\n', '\n') == final.replace('\r\n', '\n'):
                return False    # Nothing to rewrite!

        # make line endings the same as original
        is_win_crlf = self.is_win_crlf()
        if is_win_crlf and shell.IS_UNIX:
            final = final.replace('\n', '\r\n')

        # Rename file if it exists
        if self.exists() and not exists(f'{self.name}.{oldname}'):
            File(self.name).rename(f'{self.get_name(basename=True)}.{oldname}')    # Cannot use self.rename() here since we dont want to transfer object name

        # Write it. Test in windows via:
        # python /i/tpvalidation/jqdelosr/pytpd/gadget/test/test_files.py -v FileFH_tests.test_rewrite_crlf
        if (not is_win_crlf) and (not shell.IS_UNIX):
            self.unlink()
            with io.open(self.get_name(), 'w', newline='\n') as fh:
                fh.write(final)
        else:
            self.touch(final, newfile=True)

        # Delete .old file
        if not keep:
            File(f'{self.name}.{oldname}').unlink()

        log.info(f'-i- UPDATED: {self.name} is updated by {where}')
        return True

    def write(self, text):
        """
        Write text (one-time) to file and close the filehandle.
        This is a simple routine.
        It is not meant to replace self.fh().write() which can be called over and over again.

        # Usage: one time write:
        File(fname).write(text)

        # Usage: multiple write calls
        with File(fname, return_fh=True) as fh:
            fh.write(text)
            fh.write(text)
            fh.write(text)

        :param text: any string
        :return: self
        """
        if self._fh is None:
            if self.mode:
                mode = self.mode
            else:
                mode = 'w'
                if isinstance(text, bytes):
                    mode = 'wb'
            self.fh(mode=mode, check_exist=False)    # open file handle

        if self.compression in (self.none, self.gzbz2):
            self._fh.write(text)
        else:
            self._fh.write(to_bytes(text))

        self.close()
        return self

    def read(self, is_text=True):
        """
        Return the entire contents of uncompressed file.
        :param is_text: Set to False to return binary (bytes). True to return str (text)
        :return: entire contents of file (str if is_text=True, bytes otherwise)
        >>> data = File('myfile.gz').read()
        """

        if is_text:
            self.fh()
            result = to_str(self._fh.read())

        else:
            self.fh(mode='rb', is_text=False)
            result = self._fh.read()

        self.close()
        return result
        # builtin=True is always faster for bulk reads()

    def id_problem_unicode(self):
        """
        Raise exception and identify which line is problematic, if there is
        :return:
        """
        from .errors import ErrorUser
        with open(self.get_name(), 'rb') as fh:
            alltxt = fh.read()
            for lno, line in enumerate(alltxt.replace(b'\r\n', b'\n').split(b'\n'), start=1):
                try:
                    line.decode()
                except UnicodeDecodeError:
                    raise ErrorUser(f"File [{self.get_name()}] has unknown characters.",
                                    "Pls fix file above, line#%s content: %r" % (lno, line))

    def _uncompress(self, filename):
        """
        Uncompresses a file in place. Will call gunzip and bunzip2
        Supports .gz and .bz2 (any combination .gz.bz2, .bz2.gz)
        """
        aftername = filename
        if filename.endswith('.gz.bz2'):
            aftername = filename[:-7]   # remove extension
            check_and_del(aftername)
            self._un_gzbz2(aftername)

        elif filename.endswith('.bz2.gz'):
            raise Exception("uncompress(): .gz.bz2 is unsupported")

        elif filename.endswith('.gz'):
            aftername = filename[:-3]   # remove extension
            check_and_del(aftername)
            self._un_gz(aftername)

        elif filename.endswith('.bz2'):
            aftername = filename[:-4]   # remove extension
            check_and_del(aftername)
            self._un_bz2(aftername)

        return aftername

    def _to_gzbz2(self, fname):
        """compress fname to gz.bz2"""
        with open(fname, 'rb') as f_in:
            with bz2.BZ2File(f'{fname}.gz.bz2', 'wb') as f_out:
                with gzip.GzipFile(fileobj=f_out, mode='wb') as f_out2:
                    shutil.copyfileobj(f_in, f_out2)
        os.unlink(fname)

    def _un_gzbz2(self, fname):
        """uncompress fname.gz.bz2"""
        with open(fname, 'wb') as f_out:
            with bz2.BZ2File(f'{fname}.gz.bz2', 'rb') as f_in:
                with gzip.GzipFile(fileobj=f_in, mode='rb') as f_in2:
                    shutil.copyfileobj(f_in2, f_out)
        os.unlink(f'{fname}.gz.bz2')

    def _to_gz(self, fname):
        """compress fname to gz"""
        with open(fname, 'rb') as f_in:
            with gzip.open(f'{fname}.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.unlink(fname)

    def _un_gz(self, fname):
        """uncompress fname.gz"""
        with open(fname, 'wb') as f_out:
            with gzip.open(f'{fname}.gz', 'rb') as f_in:
                shutil.copyfileobj(f_in, f_out)
        os.unlink(f'{fname}.gz')

    def _to_bz2(self, fname):
        """compress fname to bz2"""
        with open(fname, 'rb') as f_in:
            with bz2.open(f'{fname}.bz2', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.unlink(fname)

    def _un_bz2(self, fname):
        """uncompress fname.bz2"""
        with open(fname, 'wb') as f_out:
            with bz2.open(f'{fname}.bz2', 'rb') as f_in:
                shutil.copyfileobj(f_in, f_out)
        os.unlink(f'{fname}.bz2')

    def _compress(self, filename, ctype):
        """
        Compresses a file in place. Will call gunzip and bunzip2.
        Supports .gz and .bz2 (any combination .gz.bz2, .bz2.gz)
        """
        if ctype == self.gz:
            newname = self._uncompress(filename)
            self._to_gz(newname)

        elif ctype == self.bz2:
            newname = self._uncompress(filename)
            self._to_bz2(newname)

        elif ctype == self.bz2gz:
            raise Exception('compress(): bz2gz is unsupported')

        elif ctype == self.gzbz2:
            if self.compression == self.gz:
                self._to_bz2(filename)
            else:
                newname = self._uncompress(filename)
                self._to_gzbz2(newname)

        else:
            raise Exception("compress(): Unknown compression type: %r" % ctype)

    def compress(self, ctype):
        """
        Compress / Recompress / or Uncompress the file
        ctype values are one of the following: File.gz, File.gzbz2, File.bz2gz, File.bz2
        Set ctype to File.none to uncompress
        Returns self
        Example:   File('file.gz.bz2').compress(File.bz2)
                   # will change compression of file.gz.bz2 to file.bz2
        """
        self.close()

        if ctype == self.compression:
            return self   # Do nothing, compression is the same

        self._comptypes.check_valid(ctype, ("Input compressiontype [{item}] is not valid. "
                                            "Use File.gz, File.bz2, etc, or File.none for "
                                            "no compression."))

        f = self.get_name(True)
        if islink(f):
            raise Exception("compress(): %r is a softlink. Cannot compress/uncompress a softlink." % f)
        if isdir(f):
            raise Exception("compress(): %r is a directory. Only files can be compressed/uncompressed." % f)

        # uncompress only
        if ctype == self.none:
            self._uncompress(f)

        # compress only
        else:
            self._compress(f, ctype)

        self.name = join(dirname(self.name), basename(self.del_ext()) + ctype)
        self.compression = ctype      # update the compression type
        return self

    def uncompress(self):
        """
        uncompress the file to no compression
        :return: self
        """
        return self.compress(self.none)

    def count_lines(self, ignore_empty_lines=False):
        """
        Returns the number of lines given a file (any compression).
        This is a fast routine using itertools.
        This is useful if you want to know upfront the number of lines for indicators (pct_indicator())
        """
        if ignore_empty_lines:
            return count_iter(self.chomp(comment=''))
        return count_iter(self.fh())

    def del_ext(self, ext=' '.join(_comporder)):
        """
        Return filename with ext removed given ext (list or string-separated-by-space)
        Default extensions are '.gz, .bz2, .gz.bz2, .bz2.gz' (compression extensions)
        Specify ext='.' to remove any extension
        Example:
           >>> File('pat1.pobj.gz').del_ext()
           'pat1.pobj'
           >>> File('pat1.pobj').del_ext('.pobj')
           'pat1'
        """
        filename = self.get_name(basename=True)
        dirn = dirname(self.get_name())   # cannot use self.get_name(dirname=True) here bec this returns abspath
        if isinstance(ext, str) and ext == ".":
            if '.' in filename:
                return join(dirn, filename[:filename.find('.')])
            else:
                return self.get_name()

        if isinstance(ext, str):
            extlist = ext.split()
        else:
            extlist = ext

        for e in extlist:
            if filename.endswith(e):
                return join(dirn, filename[:-len(e)])
        return self.get_name()

    def get_ext(self, nocompress=False):
        """
        Returns the extension, including the '.'
        Remove the compression extension if nocompress=True
        Example:
           >>> File('file.pat.data.gz').get_ext()
           '.pat.data.gz'
           >>> File('file.pat.gz').get_ext(nocompress=True)
           '.pat'
        """
        filename = basename(self.get_name())
        if filename.find('.') == -1:
            return ""

        ext = filename[filename.find('.'):]
        if nocompress:
            return ext.replace(self.compression, "")
        return ext

    def get_extlast(self, nocompress=False):
        """
        Returns the extension, including the '.'
        Remove the compression extension if nocompress=True
        Example:
           >>> File('file.pat.data.gz').get_extlast()
           '.data.gz'
           >>> File('file.pat.data.gz').get_extlast(nocompress=True)
           '.data'
        """
        filename = basename(self.get_name()).replace(self.compression, "")
        ro = re.search(r'(\.[^\.]+)$', filename)
        if ro:
            if nocompress:
                return ro.group(1)
            else:
                return ro.group(1) + self.compression
        if nocompress:
            return ""   # not found, no extension
        else:
            return self.compression

    def touch(self, appendtxt=None, mkdir=False, gid=0, mtime=None, newfile=False, mode=None):
        """
        Does the equivalent of a Unix touch command
        Works with any compression
        Add optional appendtxt to append a text to the file.
        Set mkdir=True to create the directory where file belong
        Set mtime to seconds (integer), e.g. (time.time()-120) for 2 mins old file
        The unix group of the touched file will be vep2 unix group by default (unless specified)
        """
        self.close()

        if mkdir:
            disk.mkdirs(self.get_name(dirname=True))

        name = self.get_name()

        if newfile:
            _mode = 'w'
        else:
            _mode = 'a'

        if self.compression == self.none:
            with open(name, _mode) as fh:
                if appendtxt is not None:
                    fh.write(to_str(appendtxt))
        else:
            with File(name, mode='%sb' % _mode) as fh:
                if appendtxt is not None:
                    fh.write(to_bytes(appendtxt))

        os.utime(name, None)   # set the time, this assumes file exists already

        try:
            self.chgrp(gid)
        except PermissionError:
            pass                  # ignore chgrp if it fails - because of pickle_tp folder and callerbin has different group

        if mtime is not None:
            os.utime(name, (mtime, mtime))

        if mode:
            self.chmod(mode)

        return self

    def chmod(self, mode, ignoreError=False):
        """
        Wrapper for os.chmod which makes sure that the mode leading 0 is intact (e.g. 0770).
        It must be a string.  Add in leading 0 if it doesn't exist.  Set ignoreError=True if
        you're running on files that you don't own and don't want that to be flagged.
        """
        # Python automatically converts 0777 to octal, which means that it has a different value from 777

        # This handles cases where you're running chmod when you're not the owner of a file
        self.close()
        if ignoreError:
            try:
                os.chmod(self.get_name(True), strmode_to_int(mode))
            except BaseException:  # pragma: no cover
                pass
        else:
            os.chmod(self.get_name(True), strmode_to_int(mode))

        return self

    def get_mode(self):
        """
        Wrapper for os.stat.st_mode which returns the mode in string format with leading 0 (e.g. "0770").
        The output of this function can be fed directly as the input to File.chmod function.
        """
        # Note: python oct returns a string, not an octal number.
        # The exact format of the resultant string varies between Python2 and Python3 due to how oct() works.
        #   Python2 example: "0770"
        #   Python3 example: "0o770"
        # For this reason, remove the 'o' from the string.
        return oct(os.stat(self.get_name(True)).st_mode & 0o777).replace("o", "")

    def chgrp(self, gid):
        """
        Change group of the file or dir, given gid
        set gid to None: do nothing
        set gid to zero: set to vep2 default
        set gid to <number>: set to this gid
        set gid to <string>: set to this group name
        """
        if gid is None:
            return self

        # if string, then convert it to number
        if isinstance(gid, str):
            import grp
            gid = grp.getgrnam(gid).gr_gid

        if gid == 0:
            gid = os.stat(shell.CALLERBIN).st_gid

        fname = self.get_name(True)
        stat_result = os.stat(fname)
        orig_mode = stat_result.st_mode & 0o77777
        if stat_result.st_gid != gid:       # only if it is different
            os.chown(fname, -1, gid)
            os.chmod(fname, orig_mode)    # put the orig_mode, since chown changes "sticky" bits
        return self

    def owner_name(self):
        """
        Return the owner name
        """
        import pwd
        uid = os.stat(self.get_name()).st_uid
        return pwd.getpwuid(uid).pw_name

    def unlink(self):
        """Deletes the file, if it exist"""
        if exists(self.get_name()) or islink(self.get_name()):   # islink() is for broken links - file does not exist but link exist
            os.unlink(self.get_name())
        return self

    def copy(self, dest, xfer=True):
        """
        Copy the file to dest. dest can be a directory or a file.
        Set xfer to False when the File obj name does not transfer to newly copied name.
        Will raise exception upon failure (uses shutil.copy2())
        Return self (so that fobj.copy().rename() can be used)
        Example:  File('a.pat').copy('b.pat')
        """
        self.close()
        self.opsuccess = False
        name = self.get_name()

        # destination is directory
        if isdir(dest):
            if realpath(dest) == realpath(dirname(name)):
                return self   # do nothing if copying on same dir

            shutil.copy2(name, dest)
            if xfer:
                self.name = join(dest, basename(name))

        # destination is new dir
        elif realpath(dirname(dest)) != realpath(dirname(name)):
            if not isdir(dirname(dest)):
                raise Exception("dest %r, directory %r does not exist." % (dest, dirname(dest)))

            if xfer:
                self.copy(dirname(dest))
                self.rename(basename(dest))
            else:
                F1 = File(self.get_name())
                F1.copy(dirname(dest))
                F1.rename(basename(dest))

        # destination is same dir
        else:
            # same name - do nothing
            if basename(dest) == basename(name):
                return self    # do nothing

            # Check if compression is the same
            otherfile = File(dest)
            if self.compression != otherfile.compression:
                raise Exception("dest %r does not match compression of existing name: %r" % (dest, basename(self.get_name())))

            # Do actual copy
            shutil.copy2(name, dest)
            if xfer:
                self.name = dest

        self.opsuccess = True
        return self

    def move(self, destdir, overwrite_rename=False):
        """
        Move the file to destdir
        Will raise exception upon failure (uses shutil.move())
        Return self (so that fobj.move().rename() can be used)
        Example:  File('a.pat').move(newdir)
        """
        self.close()
        self.opsuccess = False

        if not isdir(destdir):
            raise Exception("Destination Dir must be a valid Dir: %r" % destdir)

        name = self.get_name()
        if realpath(destdir) == realpath(dirname(name)):
            return self   # do nothing if copying on same dir

        # check if file already exist
        if exists(join(destdir, basename(name))) and overwrite_rename:
            File(join(destdir, basename(name))).rename_incremental()

        shutil.move(name, destdir)
        self.name = join(destdir, basename(name))
        self.opsuccess = True
        return self

    def safeunlink(self):
        """'A safe unlink wrapper method, Will not raise exceptions upwards but
        catch and print to stdout.
        @return: True for success. False for failure/exception
        @attention: no-write permissions, or none-existing files = failure!"""
        try:
            if not (exists(self.get_name()) or islink(self.get_name())):   # islink() is for broken links - file does not exist but link exist
                print("-E- failed to remove file {} because {}".format(self.get_name(), "file not found"))
                return False
            if not os.access(self.get_name(), os.W_OK):
                print("-E- failed to remove file {} because {}".format(self.get_name(), "no write permisions"))
                return False
            self.unlink()
        except Exception as e:
            print("-E- failed to remove file {} because {}".format(self.get_name(), e))
            return False
        return True

    def safecopy(self, dest, xfer=True):
        """A safe copy wrapper method, Will not raise exceptions upwards but
        catch and print to stdout.
        @return: True/False for success.
        @attention: Requires destination dir to exist"""
        try:
            self.copy(dest, xfer)
        except Exception as e:
            print("-E- failed to copy file {} to directory {} because {}".format(self.name, dest, e))
            return False
        return True

    def safemove(self, dest):
        """A safe move wrapper method, Will not raise exceptions upwards but
        catch and print to stdout.
        @return: True/False for success.
        @attention: Requires destination dir to exist"""
        try:
            self.move(dest)
        except Exception as e:
            print("-E- failed to move file {} to directory {} because {}".format(self.name, dest, e))
            return False
        return True

    def rename_incremental(self):
        """
        If file exist, then rename it with <filename>.<n>, where <n> is a number
        starting from 1. It will increment until the file does not exist
        This function works well with any compressed file
        """
        name = self.get_name()
        if File(name).autofind() is None:   # any compression
            return self  # do nothing

        ofile = File(name, autofind=True)
        base = basename(self.get_name(basenoext=True))   # this has no compression

        # get the real base without the number
        res = re.search(r'^(.*)(\.\d+)$', base)
        if res:
            base = res.group(1)

        dirn = dirname(name)
        for n in range(1, 10000):
            tryfile = "%s.%s" % (base, n)
            if File(join(dirn, tryfile)).autofind() is None:   # any compression
                ofile.rename(tryfile + ofile._get_compression(ofile.get_name()))
                return self

        else:  # pragma: no cover    - this should not be reached!
            raise Exception("Maximum iteration exceeded")

    def rename(self, newname):
        """
        Rename file to newname (this is not a move)
        Will raise exception upon failure.
        Return self (so that fobj.move().rename() can be used)
        Example:  File('a.pat').rename('b.pat')
        """
        self.close()
        self.opsuccess = False

        # newname must not contain paths - name only
        if basename(newname) != newname:
            raise Exception("newname %r must not contain any paths. It must only be the name" % newname)

        # same name - do nothing
        if newname == basename(self.name):
            return self    # do nothing

        # Check if compression is the same
        otherfile = File(newname)
        if self.compression != otherfile.compression:
            raise Exception("newname %r does not match compression of existing name: %r" % (newname, basename(self.name)))

        origname = self.get_name()
        self.name = join(dirname(origname), newname)   # abspath of new name

        # in unix, if file exist, os.rename() just override the file, but in windows, it will error, thus delete it first before "rename"
        if exists(self.name):
            File(self.name).unlink()

        os.rename(origname, self.name)
        self.opsuccess = True
        return self

    def exists(self, autofind=False, refresh=False):
        """
        Returns true if file exists
        Set autofind=True to find any compression extension
        Set refresh=True to refresh dir contents by running os.listdir()
        """
        if refresh:
            os.listdir(self.get_name(dirname=True))    # this will force filer refresh

        if autofind:
            try:
                File(self.get_name(), autofind=True)
                return True
            except IOError:
                return False

        else:
            return exists(self.get_name())

    def exists_remote(self, site):
        """
        Check for file existance from a remote site.  This is a slow operation, so be very careful about putting it
        into loops.
        :param site: remote site name to check
        :type site: str
        :return: True if file exists at the specified remote site
        :rtype: bool
        """
        from .shell import SystemCall, RsyncerBase  # Importing here to prevent circular imports at top of file
        machine = RsyncerBase(site).get_remote_machines()

        ssh_cmd = "ssh {machine} test -r {name}".format(name=self.name, machine=machine)
        ecode = SystemCall(ssh_cmd).run()
        return bool(ecode == 0)

    def stats_remote(self, site):
        """
        Run the Linux 'stat' command on the file at a remote site.  Convert results into a dictionary for return
        :param site: remote site name to check
        :type site: str
        :return: dictionary of file stats
        :rtype: dict
        """
        from .shell import SystemCall, RsyncerBase  # Importing here to prevent circular imports at top of file
        machine = RsyncerBase(site).get_remote_machines()
        print_format = "Filename::%n;User::%U;Modify::%y (epoch=%Y);Access::%x (epoch=%X);" \
                       "Change::%z (epoch=%Z);Size::%s;Permissions::%a/%A;Gid::%g/%G;Filetype::%F;"

        ssh_cmd = """ssh {machine} "stat {name} --printf '{pf}'" """.format(name=self.name, machine=machine,
                                                                            pf=print_format)
        ecode, sout, serr = SystemCall(ssh_cmd).run_sout_serr()

        if ecode:
            raise IOError("Cannot get remote stats for %s at %s. %s" % (self.name, site, serr))

        stats = {}
        for line in sout.split(';'):
            line = line.strip()
            fields = line.split('::')

            # Skip blank lines
            if len(fields) > 1:
                stats[fields[0].strip()] = fields[1].strip()
            else:    # pragma: no cover   - coverage only
                None

        return stats

    def another_remote(self, dest, srcsite, destsite, retries=1):
        """
        Copies a local file to remote dest site
        :param dest: remote site
        :type dest: str
        :param srcsite: source site
        :type srcsite: str
        :param destsite: dest site
        :type destsite: str
        :param retries: Number of times to try when failures occur during rsync
        :type retries: int
        :raises Exception: if cannot perform an rsync
        """
        # Importing here to prevent circular imports at the top of the file
        from .shell import RsyncerBase

        # pull first
        with TempDir(name=True) as tdir:
            result = RsyncerBase(srcsite).do_rsync(self.name, tdir, 'pull',
                                                   rsync_options="--recursive -avzL --partial",
                                                   retries=retries)
            assert result, 'rsync failed. See above for log.'

            # push next
            result = RsyncerBase(destsite).do_rsync(f'{tdir}/{basename(self.name)}', dest, 'push',
                                                    rsync_options="--recursive -avzL --partial",
                                                    retries=retries)
            assert result, 'rsync failed. See above for log.'

    def push_remote(self, dest, site, retries=1):
        """
        Copies a local file to remote dest site
        :param dest: remote site
        :type dest: str
        :param site: remote site name to copy from
        :type site: str
        :param retries: Number of times to try when failures occur during rsync
        :type retries: int
        :raises Exception: if cannot perform an rsync
        """
        # Importing here to prevent circular imports at the top of the file
        from .shell import RsyncerBase

        # -L option forces symlink files to be resolved to the actual file, the rest are the rsync defaults
        result = RsyncerBase(site).do_rsync(self.name, dest, 'push',
                                            rsync_options="--recursive -avzL --partial",
                                            retries=retries)
        assert result, 'rsync failed. See above for log.'

    def copy_remote(self, dest, site, retries=1):
        """
        Copies the file from the remote site to the current site with the destination path.
        :param dest: local site path where the file should be copied to
        :type dest: str
        :param site: remote site name to copy from
        :type site: str
        :param retries: Number of times to try when failures occur during rsync
        :type retries: int
        :raises Exception: if cannot perform an rsync
        """
        # Importing here to prevent circular imports at the top of the file
        from .shell import RsyncerBase
        from .disk import mkdirs

        # Create local destination if needed.
        dest_dir = dirname(dest)
        if not isdir(dest_dir):
            mkdirs(dest_dir)

        # -L option forces symlink files to be resolved to the actual file, the rest are the rsync defaults
        result = RsyncerBase(site).do_rsync(self.name, dest, 'pull', rsync_options="--recursive -avzL --partial",
                                            retries=retries)
        assert result, 'rsync failed. See above for log.'

    def autofind(self):
        """
        Returns the filename that exist with any compression.
        Returns None if none is found
        Use direct File(fname, autofind=True) if fname is expected to exist.

        Example:
        if File('abc').autofind() is None:
            # no file exist with any compression

        """
        try:
            res = File(self.get_name(), autofind=True)
            return res.get_name()
        except IOError:
            return None

    def realpath(self):
        """
        Returns realpath (absolutepath with links resolved) of the file
        Will not check file existence
        """
        return realpath(self.get_name())

    def existleaf(self, prev=False, new=False):
        """
        If prev==False: Returns the top leaf that is existing.
        If prev==True:  Returns the first leaf that is not existing.
        If new==True:   Returns a list of all new leafs
        Example:
           >>> File('/tmp/mydir/abc/def').existleaf()
           '/tmp/mydir'      # '/tmp/mydir' is existing dir
           >>> File('/tmp/mydir/abc/def').existleaf(prev=True)
           '/tmp/mydir/abc'
        """
        pt = self.get_name()
        ptprev = None
        newleaf = []
        while not exists(pt) and len(pt) > 1:
            newleaf.append(pt)
            ptprev = pt
            pt = os.path.split(pt)[0]

        if new:
            return newleaf
        if prev:
            return ptprev
        return pt

    def logprint(self, text, ignore_err=False):
        """
        Appends text to the File, with the timestamp info.
        """
        if self.compression != self.none:
            raise Exception("Cannot use logprint on compressed file")

        self.close()
        fileexist = self.exists()
        try:
            self._fh = open(self.get_name(), "a")
        except BaseException:
            if ignore_err:
                return
            else:
                raise       # re-raise

        self._fh.write("%s: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), text))
        self.close()    # Close it

        # change permission upon first creation
        if not fileexist:
            self.chmod("0660").chgrp(0)

    def onceaday(self, maxage=3600 * 24, mkdir=False):
        """
        Returns True if the file age is greater than 24 hrs or in age
        """
        if not self.exists():
            self.touch(mkdir=mkdir)
            self.chmod("0775")    # So that others can touch it
            return True

        if self.age() > maxage:
            self.unlink()         # delete first, since it can be owned by someone
            self.touch()
            self.chmod("0775")    # So that others can touch it
            return True

        return False

    def onceaweek(self, maxage=3600 * 24 * 7, mkdir=False):
        """
        Returnes True if file age is greater than 7 days (uses logic of onceaday)
        """
        return self.onceaday(maxage, mkdir)

    def age(self, error=True):
        """
        Returns the age of the file in seconds.

        :param error: Set to False to ignore error and return age=-1
        :return: age in seconds
        """
        try:
            return time.time() - os.path.getmtime(self.get_name())
        except OSError:
            if error:
                raise
            else:
                return -1

    def close(self):
        """Close the filehandle if open"""
        # close _fh
        if self._fh is not None:
            self._fh.close()
            self._fh = None

        # close _fh1
        if self._fh1 is not None:
            self._fh1.close()
            self._fh1 = None

    def newfile(self):
        """
        Returns a filename/dir that does not exist.
        Usage:
        >>> File('somepath').newfile()
        somepath.2     # returns somepath.2 if somepath and somepath.1 exist
        >>> File('somepath').newfile()
        somepath       # returns somepath if somepath does not exist
        """
        if not self.exists():
            return self.get_name()

        for ii in range(1, 10000):   # max of 10K tries
            res = "%s.%s" % (self.get_name(), ii)
            if not exists(res):
                return res
        else:
            raise Exception("10K tries exceeded to get non-existent file/dir for %s"
                            "" % self.get_name())

    def md5(self, readsize=1000000, maxiter=1000000):
        """
        Returns md5 checksum
        """
        md = hashlib.md5()
        with open(self.get_name(), "rb") as fh:
            for i in range(maxiter):
                res = fh.read(readsize)
                md.update(res)
                if len(res) != readsize:
                    break
            else:
                raise Exception("maximum iteration reached for md5()")

        return md.hexdigest()

    def sha1(self, binary=True, readsize=1000000, maxiter=1000000):
        """
        Returns sha1 checksum of raw file (with compression) by default (binary=True)
        Returns sha1 checksum of uncompressed file (binary=False)
        """
        sha = hashlib.sha1()

        if binary:
            obj = open
            args = [self.get_name(), "rb"]
            kwargs = {}
        else:
            obj = self.fh
            args = []
            kwargs = {'is_text': False}

        with obj(*args, **kwargs) as fh:
            for i in range(maxiter):
                res = fh.read(readsize)
                sha.update(res)
                if len(res) != readsize:
                    break
            else:
                raise Exception("maximum iteration reached for sha1()")

        self.close()
        return sha.hexdigest()

    def lsltrd(self, default='-ltrd'):
        """
        Returns the ls -ltrd output, for informational purposes on this file
        """
        if self.exists():
            return shell.SystemCall("ls %s %s" % (default, self.get_name())).run_outonly()
        return "%s is not found" % self.get_name(abspath=True)

    def is_text(self):
        """Returns True if file is a text file"""
        robj = re.compile(rb'[^\x20-\x7F\s\b\r]')

        # read the file, first 100 lines only
        for n, line in enumerate(self.fh(is_text=False)):
            if robj.search(line):
                return False         # non-text
            if n == 100:               # first 100 lines only
                self.close()
                break

        return True       # text

    def update_printable(self):
        """Overwrite the file and make it printable (remove special characters)"""
        robj = re.compile(r'[^\x20-\x7F\s]')
        res = []
        for line in self.chomp():
            out = line.replace('\r', '')
            out = robj.sub('', out)
            res.append(out)
        with open(self.get_name(), "w") as fho:
            fho.write('\n'.join(res))
            fho.write('\n')

        return self

    def get_between(self, start, end):
        """Returns the lines (list) between these two string"""
        result = []
        tag = False
        for line in self.chomp():
            if start in line:
                tag = True
                continue

            if end in line:
                tag = False

            if tag:
                result.append(line)

        return result

    def open_error_message(self):
        """
        Returns the error message when opening this file.
        This return a more detailed error like 'permission denied', 'not found', 'is a directory', etc.
        If no error, then return None
        Usage: print this during raise exception message so it is known what kind of error it is.
        """
        try:
            open(self.get_name()).close()
        except Exception as e:
            return str(e)

        return None     # Success

    def size_zero_unlink(self, timeout=120):
        """
        This will unlink the file if it has 0 size AND it's over the timeout specified.
        The timeout is in place to avoid deleteing filehandles that are just being written to
        :return: True if file was unlinked, False otherwise
        """
        if (os.path.getsize(self.name) == 0) and self.age() > timeout:
            self.unlink()
            return True
        return False

    def get_size_uncompresed(self):
        """
        :return: The size of the file when uncompressed
        """
        # uncompressed file, return size as-is
        if not self.compression:
            return os.path.getsize(self.name)

        # compressed file, copy to a TempDir so no memory is consumed
        with TempDir(name=True) as tdir:
            self.copy(tdir, xfer=False)
            newobj = File(join(tdir, self.get_name(basename=True)))
            newobj.uncompress()
            return os.path.getsize(newobj.get_name())

    def tail(self, lines=10):
        """
        :param lines: how many lines to tail
        :return: list of n lines
        """
        dd = deque(maxlen=lines)
        dd.extend(self)    # iterator
        return [x.rstrip() for x in dd]

    def __iter__(self):
        """
        Iterate on the contents of the file
        Usage:
          for line in File('file.gz'):
              # some code to process line

          for line in file('file.gz').fh():    # More-efficient version (use this if efficiency matters)
              # some code to process line... but .gzbz2 and .bz2 will return bytes while .gz and plain will return str
        """
        for line in self.fh():
            yield line

        self.close()

    def __exit__(self, *arg):
        """Context Manager exit routine - close filehandle and put back compression"""
        self.close()
        self.compress(self.origcompress)   # put compression back

    def __enter__(self):
        """
        Context Manager enter routine - return file object by default, filehandle if return_fh is True.
        Uncompress is mode is specified
        """
        self.origcompress = self.compression
        if self.mode is not None:
            if not self.exists():
                File(self.del_ext()).touch().compress(self.compression)  # create empty file
            self.compress(self.none)   # uncompress

        # default - return file object
        if not self.return_fh:
            return self

        # else (return_fh=True) return the file handle
        return self.fh(self.mode)     # return the filehandle

    def __str__(self):
        """Return the filename"""
        return self.get_name()


class SplitFile:
    """
    Class to split files into N components and put them together
    Used with copy_trace.py

    Usage:
    SplitFile(somefile, outdir)   # split somefile, output to outdir
    SplitFile(outdir, somefile)   # combine outdir, put to somefile
    """

    def __init__(self, inp, out, size=1000000, maxiter=1000000):
        """
        If inp is a file, then split the file given, directory as out
        If inp is a directory, then assemble it to out
        size is the split size
        """
        self.size = size
        self.maxiter = maxiter   # maximum files to create
        if isdir(inp):
            self._combine(inp, out)
        elif exists(inp):
            self._split(inp, out)
        else:
            raise Exception("Input %s is not a file or a directory" % inp)

    def _split(self, inpfile, outdir):
        """Given inpfile, split it into pieces"""
        if not isdir(outdir):
            raise Exception("outdir %s is not an existing directory" % outdir)

        with open(inpfile, "rb") as fh:
            for ctr in range(self.maxiter):   # max of 1M splits
                data = fh.read(self.size)
                with open(join(outdir, "file.%d" % ctr), "wb") as fhr:
                    fhr.write(data)
                File(join(outdir, "file.%d" % ctr)).chmod("0777")
                if len(data) != self.size:
                    break
            else:
                raise Exception("Maximum iteration reached for SplitFile()")

    def _combine(self, inpdir, outfile):
        """Given inpdir, combine all the files"""
        if isdir(outfile):
            raise Exception("outfile %s is a directory. It must be a file" % outfile)
        with open(outfile, "wb") as fh:
            for ctr in range(self.maxiter):
                target = join(inpdir, "file.%d" % ctr)
                if exists(target):
                    with open(target, "rb") as rfh:
                        fh.write(rfh.read())
                else:
                    break
            else:
                raise Exception("Maximum iteration reached for SplitFile()")
        File(outfile).chmod("0777")


def safeCreateFile(filepath, mode=0o660, is_text=True, text=""):
    """
    Method to create a file, and remain exception safe - on exception just print it to stdout
    @return: returns True/False on success/fail
    @note: returns True for an already existing file as well!
    """
    try:
        if os.path.exists(filepath):
            print("-I- file {} already exists. Not creating or touching it. Continue normally.".format(filepath))
            return True
        with os.fdopen(os.open(filepath, os.O_WRONLY | os.O_CREAT, mode), 'w') as fh:
            if is_text:
                fh.write(text)
                fh.write('\n')
            pass  # pragma: no cover   - coverage bug

    except Exception as e:
        print("-E- failed to create file {} because {}".format(filepath, e))
        return False

    return True


class MaxParallel:
    """
    Limits the maximum parallel running jobs

    Usage:
    @with_(MaxParallel, '/tmp/finder_api', data_arg="1 2 3")
    def func():
        # code
    """

    def __init__(self, tdir, data_arg="", proc_max=15, timeout_sec=3600, iterations=3600 * 6 // 5, sleep=5):
        """
        Warning: See reason for default values below.
        :param tdir: directory where touch files are stored. Will create it if it does not exist
        :param proc_max: maximum number of process. Default is 15. This is derated value of 20.
        :param timeout_sec: seconds before a touch file is considered stale. Default at 1 hr.
        :param iterations: number of iterations during wait. Default is 6 hrs.
        :param sleep: sleep in seconds when waiting. Default is 5 seconds. 1 second is too short.
        """
        disk.mkdirs(tdir, mode="02770")
        self.tdir = tdir
        self.name = basename(self.tdir)
        self.data_arg = data_arg
        self.logfile = os.path.join(self.tdir, '_denied.log')
        self.fname = None     # populated at __enter__
        self.iterations = -1
        self.sleep = sleep

        self.check_stale(timeout_sec)
        self.check_max_process(proc_max, iterations, sleep)

    def __enter__(self):
        """Executed upon entry to with block"""
        self.fname = os.path.join(self.tdir, '%s_%s' % (shell.HOSTNAME, os.getpid()))
        File(self.fname).touch("%s: %s" % (self.name, self.data_arg))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Executed upon closure of with block"""
        self.close()

    def close(self):
        """closure code"""
        File(self.fname).unlink()
        if self.iterations:
            File(self.logfile).logprint("%s, sleep_seconds: %s" % (self.name, self.iterations * self.sleep))

    def check_stale(self, timeout_sec):
        """
        Delete stale files if their mtime is > timeout_sec
        """
        for ff in os.listdir(self.tdir):
            if ff == basename(self.logfile):
                continue    # Do not delete this file
            fobj = File(os.path.join(self.tdir, ff), fast=True)
            try:
                if fobj.age() > timeout_sec:
                    fobj.unlink()
            except BaseException:
                pass    # do nothing

    def check_max_process(self, proc_max, iterations, sleep):
        """
        Raise exception if number of files which represent processes is > proc_max
        """
        from .pylog import log
        for idx in range(iterations):
            nfiles = len(os.listdir(self.tdir))
            if nfiles > proc_max:
                log.info("-i- %s sleeping, maximum number of parallel processes (%s>%s)."
                         "" % (self.name, nfiles, proc_max))
                time.sleep(sleep)
            else:
                self.iterations = idx
                return

        # When iteration is exhausted
        File(self.logfile).logprint("%s %s %s, error max_iterations"
                                    "" % (shell.USERNAME, basename(shell.CALLERBIN), self.name))
        raise Exception("Max number of iterations encountered for wait on max_processes for %s."
                        "" % self.name)


# this needs to be at bottom because of shell imports files as well
from . import shell
from . import disk
# if __name__ == '__main__':         #pragma: no cover
#    import doctest
#    doctest.testmod()
