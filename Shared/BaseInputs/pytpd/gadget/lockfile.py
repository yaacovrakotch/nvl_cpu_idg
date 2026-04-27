#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
lock file related libraries (win and unix)
"""
import os
import time
from os.path import join, exists, dirname, basename
from .files import File
from .strmore import uniq_sha
from .disk import is_dir_writeable
from .errors import ErrorEnv


def force_refresh(dirn):
    """Force filer refresh of this directory. dirn can be readonly"""

    fname = f"checklock_{uniq_sha()}"
    targ = join(dirn, fname)
    try:
        open(targ, "w").close()   # touch the file
        os.unlink(targ)
        return fname    # for unittest
    except BaseException:
        pass   # do nothing
    return None


class Lock:
    """
    Locking context manager
    unix and windows

    Usage:
      with Lock('path/file') as lock:
          # do code that deals with path/file
          # path/file does not need to exist
    """
    newline = ''      # used with cgi message. This is replaced with '<br>'

    def __init__(self, path, sleepsec=0.2, timeout=3600 * 24, maxlocktime=3600 * 48):
        """
        path     should contain a dir/filename where dir is writable.
                 filename is not touched. filename.lock will be created as indicator of lock.
        sleepsec is the sleep time between ping of lock file existence
        timeout  is in seconds
                 Object will raise Exception if timeout is exceeded.
        maxlocktime is in seconds.
                 Object will grab the lock if maxlocktime is exceeded.
                 Use so that there is no stale lockfiles. Say set to 1 hour (3600)
        """
        self.path = path
        self.sleepsec = sleepsec
        self.timeout = timeout
        self.maxlocktime = maxlocktime
        self.lockpath = dirname(path)
        self.lockname = f'{basename(path)}.lock'
        self.lockdir = f'{self.lockpath}/{self.lockname}'
        self.cntloop = 0    # Used in performance and unittests
        self.errloop = 0    # Used in performance and unittests

        # assert path.startswith('/'), f"Error on Lock(). Input path must be absolute path: {path}"
        assert exists(self.lockpath), f"Lock: root path [{self.lockpath}] does not exist"

    def __exit__(self, *arg):
        """Context manager (with statement) exit"""
        self._remove_lockdir()

    def __enter__(self):
        """Context manager (with statement) enter"""
        assert is_dir_writeable(self.lockpath), f'Lock: root path [{self.lockpath}] is not writeable.'
        self._acquire_lock()
        return self

    def _remove_lockdir(self):
        """remove lockdir - guaranteed"""
        try:
            os.rmdir(self.lockdir)
        except Exception as e:
            print(f"-w- Lock(): Failed to rmdir {self.lockdir}: {e}{self.newline}")

    def _acquire_lock(self):
        """Acquire lock"""
        for idx in range(int(self.timeout / self.sleepsec)):

            force_refresh(self.lockpath)
            self._check_max_locktime()
            if self._get_lock():
                return    # success

            if idx == 0:
                print(f'-i- Waiting for {self.lockdir} to be released. Timeout in {self.timeout} Secs.{self.newline}')
            self.cntloop += 1
            time.sleep(self.sleepsec)

        raise ErrorEnv(f"Lock: timeout in acquiring [{self.lockdir}]")

    def _get_lock(self):
        """Get the lock - one loop. Return True if success"""

        # lockpath still exist. This will refresh the filer
        if self.lockname in os.listdir(self.lockpath):
            return False

        # make the directory
        try:
            os.mkdir(self.lockdir)
        except BaseException:
            self.errloop += 1
            return False

        return True

    def _check_max_locktime(self):
        """Remove the lockdir if it exceeds maxlocktime"""
        if File(self.lockdir).age(error=False) > self.maxlocktime:
            print(f"-i- Removing lock dir {self.lockdir} due to maxlocktime.{self.newline}")
            self._remove_lockdir()

    def check_lock(self):
        """
        Public function: Checks if the given lockfile exists by forcing refresh on directory filer
        """
        force_refresh(self.lockpath)
        return self.lockname in os.listdir(self.lockpath)    # to avoid caching

    def check_lock_wait(self):
        """
        Public function:
        Checks if the lockdir exist if so, then wait until it is released until timeout
        Returns False if timeout has reached, True if success
        """
        for _ in range(int(self.timeout / self.sleepsec)):
            self._check_max_locktime()
            if self.check_lock():
                time.sleep(self.sleepsec)
            else:
                return True
        return False


# =========== Validation Note ===============
# In addition to the unit-tests here, run the following in unix and windows
# windows: open 3 windows in parallel and run 'featuretest_lockfile_parallel.py 10' at the same time.
#          confirm output numbers are unique
# unix: Run the featuretest_lockfile_parallel.py in netbatch
#       Validation done: at least 10000 jobs run (~87 parallel runs, ~20 machines), no duplicate number, 100% good
# Settings: sleepsec=0.2, "featuretest_lockfile_parallel.py 50"
#
# Result:
# Total: 10000
# chunks    : 87
# count  ave: 114.94252873563218
# count  max: 200
# finish ave: 9.120082799999983
# finish max: 120.83699999999953
# loop   ave: 95.053
# loop   max: 1528
# loop_e ave: 20.0374
# loop_e max: 317
