#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
disk and directory related libraries
"""
import os
import re
import stat
from os.path import join, exists, isdir, realpath, abspath, islink, basename, dirname, getsize
from .strmore import regex, sha1, uniq_sha    # to support py3 imports
from .helperclass import EnumType, ExceptionEnv    # to support py3 imports
from .errors import ErrorInput


class Chdir:
    """
    Context-manager Chdir, such that it will chdir back to original
    directory once 'with' is done.
    Returns the original directory on context manager.

    Example:
    >>> os.getcwd()
    '/somepath/origdir'
    >>> with Chdir('/tmp/newdir') as orig:
    ...    print orig
    '/somepath/origdir'
    ...    print os.getcwd()
    '/somepath/newdir'
    """

    def __init__(self, newdir):
        """Store the original dir"""
        if newdir == '':      # empty string, eg. dirname('file.txt')
            newdir = '.'

        self.orig = os.getcwd()
        os.chdir(newdir)

    def __exit__(self, *arg):
        """Go back to original dir"""
        if isdir(self.orig):
            os.chdir(self.orig)

    def __enter__(self):
        return(self.orig)


def listdir_nodot(dirname):
    """Returns fullpath of os.listdir(dirname)"""
    return [x for x in os.listdir(dirname) if not x.startswith('.')]


def listdir_fullpath(dirname):
    """Returns fullpath of os.listdir(dirname)"""
    return [join(dirname, x) for x in os.listdir(dirname)]


def listdir_noerror(dirname):
    """Returns the listdir() if dirname exists, otherwise return []"""
    if isdir(dirname):
        return os.listdir(dirname)
    else:
        return []


def get_diskroot(diskpath, username=None):
    """
    Attempt to determine which disk the path resides on and return the path to the disk root level.  If the disk root
    cannot be determined, an optional hint can be provided of the user name and it return the portion that occurs
    before the first instance of the username
    :param diskpath: path to use to find the diskroot it resides on
    :type diskpath: str
    :param username: Optional filter for "weird" disks that don't follow standard naming conventions
    :type username: str
    :return: disk root path
    :rtype: str
    """
    dpath = realpath(diskpath)

    # Handle the TMP case
    if dpath.startswith('/tmp'):
        return '/tmp'

    # Handle normal disks and HOME directory
    m = re.search(r'^(/nfs/\w+/(disks|home|proj)/[\w\.]+)', dpath)
    if m:
        return m.group(1)

    if username:
        return dpath.split('/%s' % username)[0]

    return dpath


def _on_rm_error(func, path, exc_info):
    """
    path contains the path of the file that couldn't be removed
    let's just assume that it's read-only and unlink it.
    Copied from: https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows
    """
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def rmtree(path, ignore_error=False):
    """
    Deletes the path - with chmod upon error
    :param path: path to delete
    :param ignore_error: True to ignore any errors
    :return: None
    """
    import shutil

    try:
        shutil.rmtree(path, onerror=_on_rm_error)
    except Exception as e:
        if ignore_error:
            pass
        else:
            raise ErrorInput(f'Error: {e}', f'Check {path}')      # raise ErrorInput with context


def copytree(source, dest):    # pragma: no cover
    """
    Copy the folder and it's subdirectories.
    Fast version for windows
    :param source: source folder
    :param dest: dest folder (must not exist)
    :return:
    """
    raise Exception("This is not validated yet")
    from .shell import IS_UNIX

    if IS_UNIX:
        import shutil
        shutil.copytree(source, dest)
    else:
        from .shell import SystemCall
        with TempDir(name=True) as tdir:
            ecode, out = SystemCall(f'robocopy {source} {outdir} /E /LOG:{tdir}/robocopy.log', disp=True).run_outtxt()
        assert not ecode, "Error during robocopy command. See above."


def get_disk_stats(diskpath):
    """
    Gather the disk space stats for the path passed in using the Linux 'df' command
    :param diskpath: path to the disk to get stats for.
    :type diskpath: str
    :return: Disk space stats in KB
    :rtype: dict
    """
    from .shell import SystemCall  # Must be here to prevent cov.py failures
    ecode, sout = SystemCall('/bin/df -P %s' % diskpath).run_outtxt()
    if ecode or not sout:
        raise ExceptionEnv("Cannot decode df output: (%s) %r" % (ecode, sout))

    for line in sout.split('\n'):
        if not line.startswith('Filesystem'):
            fields = line.split()
            if len(fields) >= 6:
                return {'total': int(fields[1]), 'used': int(fields[2]),
                        'avail': int(fields[3]), 'use%': int(fields[4].rstrip("%")),
                        'diskroot': fields[5], 'raw': sout}

    raise ExceptionEnv("No disk stats available. 'df' cannot interpret %s" % diskpath)


def get_free_space(diskpath, pct=False, debug=False):
    """
    Returns the free disk space in Kbytes
    Set pct=True to return the percentage free (integer) instead of Kb (e.g. 10 means 10% free)
    This is for UNIX only

    Originally code here is using os.statvfs(), however, using os.statvfs() causes hungup/very-slow
    in netbatch when machine load is high and filer is slow to respond.
    hungup can be several hours. using 'df' is more reliable for this case.
    see tvpvhelp 27522.
    """
    stats = get_disk_stats(diskpath)
    if pct:
        return 100 - stats['use%']
    else:
        if debug:
            return stats['avail'], stats['raw']
        else:
            return stats['avail']


def get_free_diskspace(diskpath):
    """
    Returns the free disk space in kbytes

    :param diskpath:
    :return: int kb or -1 on error
    """
    import shutil

    try:
        total, used, free = shutil.disk_usage(diskpath)  # or any drive/path
    except FileNotFoundError:
        return -1

    return int(free / 1024)


def get_percent_used(diskpath):  # pragma: no cover
    """
    Returns the percent used of the disk
    """
    return 100 - get_free_space(diskpath, pct=True)


def get_open_file_handles():
    """Return a list of open files, UNIX only"""
    fd = '/proc/self/fd'
    res = []
    for fh in os.listdir(fd):
        try:
            rf = os.readlink(os.path.join(fd, fh))
        except BaseException:
            rf = '/dev/'
        if not rf.startswith('/dev/'):
            res.append(rf)
    return res


def check_disk_threshold(path, threshold_gb=3, raise_on_insufficient=True):
    """
    Check if path has enough free space
    :param path: path to check disk space for
    :param threshold_gb: minimum required free space in GB (default 3GB)
    :param raise_on_insufficient: if True, raise exception when insufficient space (default True)
    :return: tuple (free_kb, free_gb, is_sufficient) or (None, None, True) if path is invalid
    """
    from gadget.pylog import log

    if not path or len(path) <= 3:  # Skip if path is empty or just drive letter
        return None, None, True

    # Ensure we check the directory, not a file
    check_path = path if isdir(path) else dirname(path)
    free_kb = get_free_diskspace(check_path)
    log.info(f"-i- DISKFREE_KB {check_path}: {free_kb}")
    if free_kb == -1:
        return None, None, True  # Can't determine, don't fail

    free_gb = free_kb / (1024 * 1024)
    threshold_kb = threshold_gb * 1024 * 1024
    is_sufficient = free_kb > threshold_kb

    if raise_on_insufficient and not is_sufficient:
        raise ErrorInput(f'Insufficient disk space on destination ({check_path}): {free_gb:.2f} GB available, minimum {threshold_gb} GB required, Free up disk space on {check_path}')

    return free_kb, free_gb, is_sufficient


def alldirs(startdir, skipsvn=False, rx=None):
    """
    Returns all dirs (fullpath) recursively as iterator starting from startdir.
    Set skipsvn to True to skip '.svn' directories
    Set rx to a compiled regex and only files that match regex will be returned

    Behaviors:
    It does not return directories
    It does not traverse to softlinks
    It returns unaccessible dir
    """
    for root, dirs, files in os.walk(startdir):
        if skipsvn and ".svn" in root:
            continue
        if rx is None or rx.search(root):
            yield root


def allfiles(startdir, skipsvn=False, rx=None):
    """
    Returns all files (fullpath) recursively as iterator starting from startdir.
    Set skipsvn to True to skip '.svn' directories
    Set rx to a compiled regex and only files that match regex will be returned

    Behaviors:
    It does not return directories
    It does not traverse to softlinks
    It returns broken softlink dirs (since it is a file)
    Wrapper to os.walk().
    """
    for root, dirs, files in os.walk(startdir):
        if skipsvn and ".svn" in root:
            continue
        for f in files:
            res = join(root, f)
            if rx is None or rx.search(res):
                yield res


def scandir_mtime(path):     # allfiles_mtime
    """
    Iterator recursive, to all files in path. Yields name and modified time

    Returns only files, not directories
    """
    with os.scandir(path) as fhdir:
        for entry in fhdir:
            if entry.is_dir():
                for result in scandir_mtime(f'{path}/{entry.name}'):
                    yield result
            else:
                yield f'{path}/{entry.name}', entry.stat().st_mtime


def delete_oldest(folder, keep=10, message='-i- Deleting', delete=True):    # oldest_files()
    """
    Delete the oldest files/folder, keeping only n
    Return oldest_files (if delete=False)

    :param folder: folder with files or '<folder>/*.txt' wildcard for targetted files
    :param keep: N, count of newest dir to keep
    :param message: string message or None for no log message
    :param delete: Set to False to not delete, for unitest and to return oldest files
    :return: List of deleted files
    """
    from gadget.files import check_and_del
    from gadget.pylog import log
    import glob

    wfiles = None
    if '*' in basename(folder):
        wfiles = {basename(x) for x in glob.glob(folder)}
        folder = dirname(folder)

    if not os.path.isdir(folder):
        return []     # Nothing to do

    with os.scandir(folder) as fhdir:
        dt = []
        for entry in fhdir:

            # wfiles logic
            if wfiles is not None:
                if entry.name not in wfiles:
                    continue

            dt.append((entry.name, entry.stat().st_mtime))

    sorted_age = sorted(dt, key=lambda x: x[1])

    deleted = []
    for ff, _ in sorted_age[:-keep]:
        deleted.append(f'{folder}/{ff}')
        if delete:
            if message:
                log.info(f'{message} {folder}/{ff}')
            check_and_del(f'{folder}/{ff}', mv_on_error=True)

    return deleted


def delete_oldest_age(folder, age=86400 * 7, message='-i- Deleting', delete=True):    # oldest_files()
    """
    Delete the oldest files/folder, keeping only n
    Return oldest_files (if delete=False)

    :param folder: folder with files
    :param age: seconds. Older than this is deleted
    :param message: string message or None for no log message
    :param delete: Set to False to not delete, for unitest and to return oldest files
    :return: List of deleted files
    """
    from gadget.files import check_and_del
    from gadget.pylog import log
    import time

    if not os.path.isdir(folder):
        return []     # Nothing to do

    with os.scandir(folder) as fhdir:
        dt = [(entry.name, entry.stat().st_mtime) for entry in fhdir]

    sorted_age = sorted(dt, key=lambda x: x[1])

    deleted = []
    curtime = time.time()
    for ff, mtime in sorted_age:
        current_age = curtime - mtime
        if current_age > age:
            deleted.append(f'{folder}/{ff}')
            if delete:
                if message:
                    log.info(f'{message} ({current_age:.0f} Secs Age) {folder}/{ff}')
                check_and_del(f'{folder}/{ff}', mv_on_error=True)
    return deleted


class SizeType(EnumType):
    B = hash("Byte")
    KB = hash("KByte")
    MB = hash("MByte")
    GB = hash("GByte")


Size = SizeType()


class Allfiles:
    """
    Iterator - return all files given a starting dir
    1. Directories are not returned
    2. Softlinks are followed, but will not return duplicate paths
    3. File existence will be checked (ie, broken links are not shown)

    Usage:
    for filepath in Allfiles('/nfs/disk'):
        # do_something_on(file_path)
    """

    def __init__(self, startdir, existcheck=True, skipsvn=False, rx=None, fullpath=False, skiplink=False):
        """
        startdir - directory path. If it is not a directory, then iterator is empty.
        existcheck - Set to False for fast iterator, that is, it will not check if file is existing.
                   - Broken softlink will be displayed if existcheck=False
        skipsvn    - Set to True to skip '.svn' directories
        rx         - a regex string. If specified, will return only if rx is true.
        fullpath   - Set to True, if iterator will always return fullpath.
                   - Useful when code inside for loop is doing chdir()
        skiplink   - Set to True to ignore softlink directories
        """
        if fullpath:
            self.startdir = abspath(startdir)
        else:
            self.startdir = startdir

        self.existcheck = existcheck
        self.skipsvn = skipsvn
        self.skiplink = skiplink
        self.cache = {}         # directories that is processed, so that it will not do recursive walk

        # compile the rx stirng, if provided
        if rx is not None:
            if isinstance(rx, str):
                rx = regex.compile(rx)
        self.rx = rx

    def __iter__(self):
        """iterator for this class - main entry point"""
        return self._recurse(self.startdir)

    def _recurse(self, startdir):
        """recurse thru all the directories"""
        rp = realpath(startdir)
        if rp not in self.cache:
            self.cache[rp] = True
            try:
                listing = os.listdir(startdir)
            except BaseException:
                listing = []

            for ff in listing:
                targ = f'{startdir}/{ff}'
                if isdir(targ):
                    if self.skiplink and islink(targ):
                        continue
                    if self.skipsvn and ff in (".svn", ".git"):
                        continue
                    for ff2 in self._recurse(targ):
                        yield ff2    # this is the result of recurse
                else:
                    if self.rx is None or self.rx.search(targ):
                        if (not self.existcheck) or exists(targ):
                            yield targ   # this are the files in the given startdir

    @staticmethod
    def _dir_size(directory_path, follow_links):
        from os import walk
        size_sum = 0
        for root, dirs, files in walk(directory_path, follow_links):
            for f in files:
                size_sum += Allfiles._file_size(f'{root}/{f}', follow_links)
        return size_sum

    @staticmethod
    def _file_size(file_path, follow_links):
        return os.stat(file_path).st_size

    def size(self, units=Size.MB):
        if os.path.isfile(self.startdir):
            size_in_bytes = self._file_size(self.startdir, not self.skiplink)
        else:
            size_in_bytes = self._dir_size(self.startdir, not self.skiplink)
        if units == Size.KB:
            converted_size = float(size_in_bytes) / 1024
        elif units == Size.MB:
            converted_size = float(size_in_bytes) / (1024 ** 2)
        elif units == Size.GB:
            converted_size = float(size_in_bytes) / (1024 ** 3)
        else:  # Size.B
            converted_size = size_in_bytes
        return converted_size


def size_dir(srcdir):
    """Return the size (in bytes) of the files under the srcdir directory"""
    return sum(os.path.getsize(f) for f in Allfiles(srcdir, skiplink=True))
    # Above code works even if broken softlink exist. Thanks to JayE for finding this


def chmodr(path, mode, ignoreError=False, gid=None):
    """
    Recursive chmod operation
    Will not chmod softlinks
    Will not traverse to softlink directories
    gid is optional, to chgrp the files
    """
    # dir_mode = "02" + mode[-3:]
    # log.dev(" D: mode %s, dir_mode: %s" %( mode, dir_mode ))

    for (filepath, _, files) in os.walk(path):
        File(filepath).chgrp(gid)                   # this is the directory, group first, then permissions
        File(filepath).chmod(mode, ignoreError)  # this is the directory, otherwise setid bits might get cleared
        for f in files:
            fullfile = join(filepath, f)
            if not islink(fullfile):
                File(fullfile).chgrp(gid)                   # this is the file, group first, then permissions
                File(fullfile).chmod(mode, ignoreError)     # this is the file, otherwise setid bits might get cleared


def _mkdir_parallel(targ):
    """parallel os.mkdir friendly - do not raise exception if directory is created successfully"""
    # for some reason, isdir() is cached, so even if isdir() is false, the actual dir may be created already
    try:
        os.mkdir(targ)
    except OSError:
        if not isdir(targ):
            raise


def mkdirs(path, mode="0o2750", gid=0, check_sticky=True, set_sticky=False):   # 750 is default os.mkdir() behavior as well
    """
    Recursively create directory given path and (optional mode)
    If directory already exist, it will ignore
    The mode is only applicable to newly created dir. Existing dir's mode is not touched
    Set gid to None to skip chgrp(), else, use default group from stage()
    """
    if not path:     # empty string or None
        return path

    if isdir(path):
        return path   # already existing

    if exists(path):
        raise Exception("mkdirs(): %r already exist as a file, so cannot make that directory." % path)

    if set_sticky:
        mode = oct(strmode_to_int(mode) | 0o2000)

    if mode.startswith('07') and check_sticky:
        raise Exception("mkdirs() mode=%s. Pls add sticky bit setting (02xxx). It's a good practice "
                        "to add sticky bit so that unix groups is propagated. If you intentionally "
                        "don't want sticky bit, then set check_sticky=False.")

    stack = []
    i_path = path
    for ii in range(200):
        if not i_path:
            break
        if not exists(i_path):
            stack.append(i_path)
            i_path = dirname(i_path)
        else:
            break
    else:   # pragma: no cover, safety check only
        raise Exception("Cockpit Error: loop is exhausted in mkdir! logic error.")

    # at this point i_path exist
    assert (not i_path) or exists(i_path), f"Cockpit error: {i_path} not exist after loop"

    for item in reversed(stack):
        _mkdir_parallel(item)
        File(item).chgrp(gid).chmod(mode)

    return path


def safemkdirs(path, mode="0o2770"):  # mode 0770 default only u+g can rwx
    """A safe wrapper to mkdirs, meaning no exceptions are thrown up. All are caught,
    printed to stdout and a True/False val indicates success
    @note: if the dir is existing - True (success), according to mkdirs behavior."""
    try:
        mkdirs(path, mode)
    except Exception as e:
        print("-E- failed to create directory {} because {}".format(path, e))
        return False
    return True


def cwd():
    """
    Returns the cwd. If exception occurs, returns '/not_available'
    Used during logging where exception is not desired
    """
    try:
        return os.getcwd()
    except BaseException:
        return "/not_available"


def copy_tree(src, dst, preserve_mode=1, preserve_times=1,
              preserve_symlinks=0, update=0, verbose=0):
    """
    Copy an entire directory tree 'src' to a new location 'dst'.
    kwchen1: This version works even if destination dir has files already.
    Original version fails if dest dir already exist, and if softlink exist in destination.
    """
    from shutil import copy, copy2

    if not os.path.isdir(src):
        raise Exception("cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    # TODO: Python3 has updated this code in distutils/dir_util.py --> copy_tree(). See if we can revert.
    except os.error as e:  # pragma: no cover
        (errno, errstr) = e.args  # pragma: no cover
        raise Exception("error listing files in '%s': %s" % (src, errstr))

    mkdirs(dst)  # kwchen1 - replaced this call

    outputs = []

    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if verbose >= 1:
                print("linking %s -> %s", dst_name, link_dest)
            if exists(dst_name) or islink(dst_name):   # delete first
                os.unlink(dst_name)
            os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os.path.isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose=verbose))
        else:
            if update and os.path.exists(dst_name):
                if os.path.getmtime(src_name) <= os.path.getmtime(dst_name):
                    continue
            if verbose >= 1:
                print("copying %s -> %s" % (src_name, dst_name))
            if preserve_times:
                copy2(src_name, dst_name)
            else:
                copy(src_name, dst_name)

            if not preserve_mode:
                try:
                    current_umask = os.umask(0)
                    os.umask(current_umask)
                    os.chmod(dst_name, 0o666 & ~current_umask)
                except OSError:
                    pass

            outputs.append(dst_name)

    return outputs


def comparedir(dir1, dir2):
    """Compare two directories and print them in stdout"""
    d1 = realpath(dir1)
    d2 = realpath(dir2)
    for ff in Allfiles(d1):
        basepath = ff.replace(d1 + "/", '')
        if not exists(join(d2, basepath)):
            print("[%s] not exist in %s" % (basepath, d2))
            continue
        if File(ff).md5() != File(join(dir2, basepath)).md5():
            print("[%s] is different" % ff)

    # Show missing files from d2
    for ff in Allfiles(d2):
        basepath = ff.replace(d2 + "/", '')
        if not exists(join(d1, basepath)):
            print("[%s] not exist in %s" % (basepath, d1))


def exclude_include_path(seq,
                         exclude_dirs=regex.compile('^___NOTEXIST123456'),      # regex object that does not match anything
                         exclude_files=regex.compile('^___NOTEXIST123456'),    # regex object that does not match anything
                         include_dirs=regex.compile('.'),                       # regex object that match anything
                         include_files=regex.compile('.')):                     # regex object that match anything
    '''Iterator given a seq of paths to filter exclude* and include*'''
    for ff in seq:
        # filters
        if exclude_dirs.search(dirname(ff)):
            continue
        if exclude_files.search(basename(ff)):
            continue
        if not include_dirs.search(dirname(ff)):
            continue
        if not include_files.search(basename(ff)):
            continue
        yield ff


def cmpdir(dir1, dir2,
           exclude_dirs=regex.compile('^___NOTEXIST123456'),      # regex object that does not match anything
           exclude_files=regex.compile('^___NOTEXIST123456'),    # regex object that does not match anything
           include_dirs=regex.compile('.'),                       # regex object that match anything
           include_files=regex.compile('.'),                     # regex object that match anything
           skiplink=False):
    '''
    Compare two directories
    Returns: (set_of_modfiles, set_of_addfiles, set_of_delfiles)

    exclude_dirs and exclude_files are optional, and must be a regex object
    exclude* specifies the blacklist (exclude these)
    include_dirs and include_files are optional, and must be a regex object
    include* specifies the whitelist (exclude these)

    skiplink   - Set to True to ignore softlink directories
    '''
    removed = set()
    added = set()
    diffed = set()

    d1 = realpath(dir1)
    d2 = realpath(dir2)
    for ff in exclude_include_path(Allfiles(d1, skiplink=skiplink),
                                   exclude_dirs=exclude_dirs,
                                   exclude_files=exclude_files,
                                   include_dirs=include_dirs,
                                   include_files=include_files):

        basepath = ff.replace(d1 + "/", '')
        if not exists(join(d2, basepath)):
            removed.add(basepath)
            continue

        if (getsize(ff) != getsize(join(dir2, basepath)) or     # size is different
                File(ff).md5() != File(join(dir2, basepath)).md5()):

            diffed.add(basepath)

    # Show missing files from d2
    for ff in exclude_include_path(Allfiles(d2, skiplink=skiplink),
                                   exclude_dirs=exclude_dirs,
                                   exclude_files=exclude_files,
                                   include_dirs=include_dirs,
                                   include_files=include_files):

        basepath = ff.replace(d2 + "/", '')
        if not exists(join(d1, basepath)):
            added.add(basepath)

    return (diffed, added, removed)


def is_dir_writeable(dirpath):
    """Returns True if dirpath is writeable. False otherwise"""
    tmp = join(dirpath, uniq_sha())
    try:
        with open(tmp, "w") as fh:
            fh.write("test")
        os.unlink(tmp)
        return True
    except BaseException:
        return False


def dir_sha1(dirpath):
    """Returns a unique sha1 for all the files in dirpath"""
    all_sha_files = []
    for ff in sorted(Allfiles(dirpath, skipsvn=True)):
        if not (ff.endswith('.pyc') or ff.endswith('.pyo')):
            all_sha_files.append("%s %s" % (ff.replace(dirpath, ''), File(ff).sha1()))
    return sha1(' '.join(all_sha_files))      # cumulative sha1 of all sha1


def check_tmp(limitkb=100000, var_limitkb=100):    # default is 100MB free for /tmp, 100kb free for /var/tmp
    """Checks tmp, if it has free space and is writable"""
    from .shell import tmpdir, HOSTNAME     # cannot put this in top of file bec cov.py will fail

    os.environ['SQLITE_TMPDIR'] = '/tmp'   # this forces sql temp db be written in /tmp instead of /var/tmp (tvpvhelp 28242)

    tmp = tmpdir()
    freespace = get_free_space(tmp)
    if freespace < limitkb:     # less than 1 MB free
        raise ExceptionEnv("{tmp} is full ({freespace}KB < {limitkb}KB). Need {tmp} to have some free space on host {host}."
                           "".format(tmp=tmp,
                                     freespace=freespace,
                                     limitkb=limitkb,
                                     host=HOSTNAME))

    if not is_dir_writeable(tmp):
        raise ExceptionEnv("{tmp} is readonly. Need {tmp} to be writeable."
                           "".format(tmp=tmp))

    # /var/tmp check - tvpvhelp 29200 - e.g. email will not work
    var_tmp = '/var/tmp'
    var_freespace = get_free_space(var_tmp)
    if var_freespace < var_limitkb:     # less than 1 MB free
        print(("{tmp} is full ({freespace}KB < {limitkb}KB). Need {tmp} to have some free space on host {host}."
               "".format(tmp=var_tmp,
                         freespace=var_freespace,
                         limitkb=var_limitkb,
                         host=HOSTNAME)))


def split_paths(path):
    '''returns a list of splitted paths starting at the top level - unix specific'''
    if not path.startswith('/'):
        path = abspath(path).replace("\\", "/")

    result = []
    cum_path = '/'
    for item in path.split('/'):
        if not item:  # first item
            continue
        cum_path = join(cum_path, item)
        result.append(cum_path)
    return result


class RecurseChgrp:
    """Recursively traverses through a directory (from given toplevel) and updates group ID to specified value (group)
       of all dirs and files owned by specified owner.

        Example input parameters:
            group = 'gdlusers'
            owner = 'p6vector'
    """

    def __init__(self, group, owner):
        import grp
        self.gid = grp.getgrnam(group).gr_gid
        self.owner = owner

    def recurse(self, toplevel):
        import pwd

        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(toplevel, followlinks=True):
            try:
                # check if the root belongs to the owner specified and exists (for links that might point to non-existing paths)
                # if exists, obtain mode of root and set sticky bit and update group and mode. Print dir path with mode.
                if(pwd.getpwuid(os.stat(root).st_uid).pw_name == self.owner and os.path.exists(root)):
                    root_stat = (os.stat(root).st_mode & 0o777) | 0o2000
                    path = root.split('/')
                    os.chown(root, -1, self.gid)
                    os.chmod(root, root_stat)
                    print((len(path) - 1) * '-', root, oct(os.stat(root).st_mode & 0o2777))
            except Exception as e:
                print(e)
                continue
            # iterate through files inside current directory and update the group. Print file path with mode.
            for file in files:
                full_path = root + '/' + file
                try:
                    if(pwd.getpwuid(os.stat(full_path).st_uid).pw_name == self.owner and os.path.exists(full_path)):
                        os.chown(full_path, -1, self.gid)
                        file_stat = (os.stat(full_path).st_mode & 0o777)
                        print(len(path) * '-', full_path, oct(file_stat))
                except Exception as e:
                    print(e)
                    continue


from .files import File, TempName, strmode_to_int, TempDir
