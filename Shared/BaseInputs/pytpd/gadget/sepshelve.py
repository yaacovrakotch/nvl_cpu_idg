#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Separate Shelve (SepShelve) module
"""
import os
import re
import sqlite3
import sys
from os.path import join, exists, isdir, basename, dirname, getmtime, abspath
from time import sleep, strftime, time
import pickle as pickle
from .disk import mkdirs
from .files import File, TempDir
from .lockfile import Lock
from .dictmore import firstitem
from .helperclass import Enum, IS_UT
from .shell import HOSTNAME
from .pylog import log
from .strmore import zlib_compress, zlib_uncompress, to_bytes, to_str
from .gizmo import Elapsed


class DummyWithClose:
    """
    A dummy class with close() method, to mimic shelve object.
    Used by SepShelve()
    """

    def close(self):    # pragma: no cover
        pass


class SepUT:
    """
    UnitTest only class, used to mock dictionary like of SepShelve classes.

    Usage:
    class MyUT(SepUT, MySepShelveClass):
       pass
    # Then, methods in MySepShelveClass can be easily tested without writing to a
    # physical shelve file. See test_patstatus_base.py: test_fromline() as example.
    """

    def __init__(self):
        """Initialize the internal dictionary"""
        self._dd = {}

    def __setitem__(self, k, v):
        self._dd[k] = v

    def __getitem__(self, k):
        return self._dd[k]

    def __contains__(self, k):
        return k in self._dd

    def __len__(self):
        return len(self._dd)

    def __iter__(self):
        for k in self._dd:
            yield k


class SqlDict:
    """
    A dictionary that stores its data persistantly in a file via sqlite
    Same interface as with sepshelve
    Keys are either string or integer only
    Once encoding is set as database creation, encoding cannot be changed anymore.
    Encoding can either be: PICKLE_NOGZ (default), PICKLE_GZ, TEXT_NOGZ, TEXT_GZ

    Read usage:
    1) Normal read:
        db = SqlDict('mydb.sql', gz=True)
        print db[<key>]
    2) Most of dictionary methods are available:
        print 'key' in db      # Existence
        print len(db)          # total keys
        for key in db.iterkeys() | db.keys() | db.viewkeys():
        for value in db.itervalues() | db.values() | db.viewvalues():
        for key,value in db.iteritems() | db.items() | db.viewitems()
    3) batched read:
        resultdict = db.fetch(<sequence_of_keys>)

    Write Usage (Always lock database when writing):
    1) Add a new single key, with lock and commit:
        db.update_withlock(key, value)
    2) Add many items, with lock, single commit:
        with db.batch():     # exclusive lock is set
            db[key1] = value1
            db[key2] = value2
            db.commit()        # do not foget to commit before exiting with()
    3) Updating value on the same key needs locking!
        with db.batch():
           <somevar> = db[<key>]     # do the read inside the lock
           <process somevar>
           db[<key>] = <somevar>     # write it and commit

    Note: No need to close() sqlite connection. close() will be called upon class destroy/python exit.
          Writes are written to disk during commit().
    """
    # Starting Baseline code originated from: filedict.py by Erez Shinan, Date: 24-May-2009

    _VAL_ENCODE = Enum(PICKLE_NOGZ=0,
                       PICKLE_GZ=1,
                       TEXT_NOGZ=2,
                       TEXT_GZ=3)

    _re_no_special_char = re.compile(r'^[\w \-\=\.\,\+\[\]\;\:\/\?\<\>`\~\!\@\#\$\%\^\&\*\(\)\{\}\|]+$')   # used in fetch()

    def __init__(self, dbfile, gz=None, chmod="0660", num_keys=False, text_only=None, iswrite=False):
        """
        Set gz to True for compressed encoding (via zlib) on values. Default is False.
        Set num_keys to True for integer-only keys stored in database. This is used only during initial table creation.
        Set text_only to True for non-pickle use. The value must be text only. Default is False.
        """
        self._check_isdir(dbfile)                            # Because of SqlParDict
        self._iswrite = iswrite                                # Sticky setting if class is being written
        self._dbfile = self._id_dbfile(dbfile)               # Name and path of database file
        self._dbfileorig = self._dbfile                      # Original name (used in RenameWrite())
        self._dbrootdir = dirname(self._dbfile)              # dir of dbfile
        self._journal = basename(self._dbfile) + "-journal"    # name of journal
        self._encoding = self._id_encoding(gz, text_only)    # Encoding setting
        self._cfg = self._set_knobs_config()                 # Configuration knob settings
        self._isfileexist = self._isexist(self._dbfile)      # New database checks / db existence flag
        self._check_hot_journal(dbfile)                      # Check for hot journal
        self._wait_journal()                             # Wait if journal exist
        self.reconnect(initial=True)
        self._create_table(chmod, num_keys)                  # Create the tables
        self._assign_encoding()                              # Assign encoding
        self._nocommit = False                               # indicator if sql commit will be made or not. Primarily used with context manager *batch* process
        self._numtype = self._id_key_type()                  # numeric key type flag
        self._more_inits()                                   # custom inits

    def _check_isdir(self, dbfile):
        """
        Checks if dbfile is a file or directory. Error out if directory.
        """
        if isdir(dbfile):
            raise Exception("SqlDict() cannot take in directory [%s]. Pls check code." % dbfile)

    def _id_dbfile(self, dbfile):
        """Return the dbfile to use - method override in mimic sepshelve"""
        return abspath(dbfile)

    def reconnect(self, initial=False):
        """Connect to db"""
        # around ~3500 reconnect() per second

        # Do not reconnect if journal exist (aka, write mode), unless initial connection
        #    reconnecting if journal exist without committing will lose written data
        if (not initial) and exists(self._dbfile + "-journal"):
            return 1

        for _ in range(10):   # try 10 times
            try:
                self._conn = sqlite3.connect(self._dbfile,           # open the sqlite connection
                                             timeout=self._cfg.sqlite_connection_timeout)
                self._conn.text_factory = str                        # set to str, since default is unicode for text
                self._conn_time = time()
                return 2  # success
            except BaseException:
                # print "oops open", _  #debug
                sleep(1)

        raise   # re-raise exception

    def check_and_connect(self):
        """
        Check if connection time has elapsed, reconnect
        This elapsed time is the sleep time during deletion of .sqlite.delete during Write
        used by getitem and contains only [common routine]
        """
        if (time() - self._conn_time) > self._cfg.rename_write_sleep:
            self.reconnect()
            return 1
        return 2

    def _id_encoding(self, gz, text_only):
        """
        Return the numeric encoding based on gz and text_only
        Override in subclass if subclass has specific encoding to use
        0 is PICKLE_NOGZ
        1 is PICKLE_GZ
        2 is TEXT_NOGZ
        3 is TEXT_GZ
        """
        if gz is None and text_only is None:
            return None   # default encoding
        if gz and text_only:
            return self._VAL_ENCODE.TEXT_GZ
        if (not gz) and text_only:
            return self._VAL_ENCODE.TEXT_NOGZ
        if gz and (not text_only):
            return self._VAL_ENCODE.PICKLE_GZ

        return self._VAL_ENCODE.PICKLE_NOGZ    # default encoding

    def _assign_encoding(self):
        """
        Determine the encoding - assign pack and unpack functions
        """
        # pickle overhead on a string: 2 million per sec
        # lambda overhead: 10M calls per sec (fast)

        # If pickled-keys are to be implemented, then use
        #      pickle_key encoding value to be 16+value_encoding

        if self._encoding == self._VAL_ENCODE.PICKLE_GZ:
            self._pack_value = lambda x: sqlite3.Binary(zlib_compress(pickle.dumps(x)))
            self._unpack_value = lambda x: pickle.loads(zlib_uncompress(to_bytes(x)))

        elif self._encoding == self._VAL_ENCODE.PICKLE_NOGZ:
            self._pack_value = lambda x: sqlite3.Binary(pickle.dumps(x))
            self._unpack_value = lambda x: pickle.loads(to_bytes(x))

        elif self._encoding == self._VAL_ENCODE.TEXT_GZ:
            self._pack_value = lambda x: sqlite3.Binary(zlib_compress(x))
            self._unpack_value = lambda x: to_str(zlib_uncompress(to_bytes(x)))

        elif self._encoding == self._VAL_ENCODE.TEXT_NOGZ:
            self._pack_value = lambda x: sqlite3.Binary(to_bytes(x))
            self._unpack_value = lambda x: to_str(x)

        else:
            raise Exception("Unknown encoding: [%s]" % self._encoding)

    def _isexist(self, dbfile):
        """
        Returns True if dbfile exists.
        This can be overridden in a custom subclass for various one time checks, say directory creation..
        """
        # root directory not existing
        if not isdir(dirname(dbfile)):
            return False

        files = set(os.listdir(dirname(dbfile)))
        bname = basename(dbfile)
        if len(files & {bname, bname + '.write', bname + '.delete'}) > 0:
            return True

        return False   # not exist

    def _check_hot_journal(self, dbfile):
        """
        Change permission of journal file if it exist.
        Reason: another user cannot open db if hot-journal is created by another user
        hot-journal is a journal file when a write transaction got killed
        """
        journal = dbfile + "-journal"
        if exists(journal):
            try:
                mtime = getmtime(journal)
            except BaseException:
                return 0

            if time() - mtime < self._cfg.lock_maxlock:
                return 1

            File(journal).chmod("0660", ignoreError=True)
            return 2
        return 3

    def _create_table(self, chmod, num_keys):
        """Create the table if it does not exist"""
        if not self._isfileexist:

            if num_keys:
                self._query('''
                    CREATE TABLE IF NOT EXISTS dict (
                        key INTEGER PRIMARY KEY,
                        value BLOB
                    );
                ''')

            else:
                self._query('''
                    CREATE TABLE IF NOT EXISTS dict (
                        key TEXT PRIMARY KEY,
                        value BLOB
                    );
                ''')

            self._conn.commit()

            # This table will only contain one record. if "value" is 1, then gz is set, 0 otherwise
            self._query('''
            CREATE TABLE IF NOT EXISTS gzset (
                value INTEGER PRIMARY KEY
            );
            ''')
            self._conn.commit()

            # set the right permissions
            File(self._dbfile).chmod(chmod)

        # Process the isgz =======================
        res = self._query('SELECT count(*) FROM gzset;',
                          func=lambda qry: qry.fetchone())[0]
        if res == 0:      # is there a value? if not, then write it
            if self._encoding is None:
                self._encoding = self._VAL_ENCODE.PICKLE_NOGZ       # default encoding
            self._conn.execute('INSERT INTO gzset VALUES (?)', (self._encoding,))
            self._conn.commit()

        # Check if input matches data
        res = self._query('SELECT max(value) FROM gzset;',
                          func=lambda qry: qry.fetchone())[0]
        if self._encoding is None:
            self._encoding = res         # use value from table
        else:
            if res != self._encoding:
                raise Exception("SQL file [%s] is already set to encoding=%s, "
                                "but object has encoding=%s specified"
                                "" % (self._dbfile,
                                      self._VAL_ENCODE.reverse_mapping[res],
                                      self._VAL_ENCODE.reverse_mapping[self._encoding]))

    def _id_key_type(self):
        """Identify if key is number or string"""
        res = self._query('pragma table_info(dict)',
                          func=lambda qry: qry.fetchall())[0]
        return bool(str(res[2]) == 'INTEGER')

    def _more_inits(self):
        """More initializations - for use in subclasses"""
        pass                 # empty for base class

    def _set_knobs_config(self):
        """Set various configuration knobs for the class"""

        class CfgObj:
            def __init__(self):
                self.query_retry_sleep = 0.2    # 200ms
                self.query_timeout = 10 * 60      # 10 mins retry
                self.lock_sleep = 0.5           # 500ms  (note: using 0.25 will be slower)
                self.lock_maxlock = 2 * 60        # 2 mins
                self.lock_timeout = 20 * 60       # 20 mins
                self.sqlite_connection_timeout = 5 * 60   # 5 mins. This is when db is locked and someone is reading or writing
                self.commit_timeout = 3600      # 1 hr before commit stops retrying
                self.max_read_time = 10 * 60      # maximum read time before read-touch is considered stale and will be deleted
                self.rename_write_sleep = 5     # some sleep time before sqlite.delete is removed

            def query_loopcount(self):
                # Used in _query() loop
                return int(float(self.query_timeout) / self.query_retry_sleep)

            def commit_loopcount(self):
                # used in commit() loop
                return int(float(self.commit_timeout) / self.sqlite_connection_timeout)

        return CfgObj()

    def _wait_journal(self, sleeptime=0.1, timeout=60 * 30):   # 30 mins
        """
        Wait for journal file to be released before proceeding during reads.
        """
        if self._iswrite:
            return 1   # no check for write operation

        for ctr in range(int(timeout / sleeptime)):
            files = os.listdir(self._dbrootdir)    # this will refresh filer always. This is relatively fast.
            if self._journal not in files:
                return 2     # normal case, journal file not exist
            sleep(sleeptime)
            if ctr == 20 and (not IS_UT):
                log.info("-i- Waiting for %s to finish (Pls submit tvpvhelp "
                         "if this go beyond 15 mins from %s)..."
                         "" % (join(self._dbrootdir, self._journal), strftime("%H:%M:%S")))

        return 3   # timeout occurred, proceed anyway

    # --- priv methods ---

    def _batch_enter(self):
        """batch() enter. Used by context manager _SqlLock()"""
        self._nocommit = True

    def _batch_exit(self, exc_value):
        """
        batch() exit. Used by context manager _SqlLock().
        This is called before lock is released.
        This code should not perform any operations
        The .commit() is intentionally not in here so that Ctrl+C will be captured correctly
        """
        self._nocommit = False   # set to default
        journal = self._dbfile + "-journal"
        if exists(journal):
            self.commit()
            if exc_value is not None:
                return exc_value
            else:
                return ("Incorrect usage of batch() - commit the data before exiting 'with' block: "
                        "[%s] exist" % journal)
            # NOTE: Above is needed to force usage of batch() to be committed. This is so Lock()
            # don't have transactions at __exit__(), so that it don't get killed during Ctrl+C

        if exc_value is not None:
            return None         # success
        else:
            return exc_value

    def _batchkeys(self, setkeys):
        """
        Compatibility with SqlParDict only - called by patinfo for counting purposes
        """
        return setkeys

    def _commit(self):
        """Commit the sql transactions to the file"""
        if self._nocommit:
            return

        self.commit()

    def _setitem(self, key, value):
        """Set one item without committing"""
        value_pickle = self._pack_value(value)

        self._iswrite = True
        res = self._conn.execute('INSERT OR REPLACE INTO dict VALUES (?, ?)', (key, value_pickle))
        if res.rowcount != 1:
            raise KeyError("update to database failed for %s" % key)

    def _query(self, *args, **kwargs):
        """
        Execute one READ query, retrying if there is OperationalError
        OperationalError happens during simultaneous read and somebody is writing
        Call only 'SELECT' lines in here. Do not call INSERT or UPDATES.
        """
        # uncomment below during unittest run to confirm all queries are good
        # assert "SELECT" in args[0] or "pragma" in args[0] or "CREATE TABLE IF NOT EXISTS" in args[0], "Query: %r" % args[0]    # make sure that queries are SELECT only

        for i in range(self._cfg.query_loopcount()):
            self._wait_journal()                                 # Wait if journal exist
            try:
                res = self._conn.execute(*args)
                if 'func' in kwargs:
                    return kwargs['func'](res)
                else:
                    return res

            except sqlite3.OperationalError:
                # log.debug("sqlite.OperationalError: iter=%s, query=%s" % (i, args[0][:100]))
                # print "%f oops len=%s" % (time(), len(args[0]))  #debug
                if exists(self._dbfile + "-journal"):
                    sleep(self._cfg.query_retry_sleep)
                else:
                    self._conn.close()
                    sleep(self._cfg.query_retry_sleep)
                    self.reconnect()

        else:
            raise Exception("Error: Unable to run query [%s] on %s" % (args[0], self.get_dbfile()))

    # --- dict write methods ---

    def __setitem__(self, key, value):
        """Set one dictionary item"""
        if key is None:
            raise KeyError("None Key is not allowed")
        self._setitem(key, value)
        self._commit()

    def __delitem__(self, key):
        """Delete one dictionary item"""
        self._iswrite = True
        res = self._conn.execute('DELETE FROM dict WHERE key=?;', (key,))
        if res.rowcount <= 0:
            raise KeyError(key)

        self._commit()

    def update(self, d, cnk=0):
        """
        Standard dict().update method
        cnk=0 is unused in this context, but required because of cross-testing with sqldb.py
        """
        for k, v in d.items():
            self._setitem(k, v)
        self._commit()

        # NOTE: using .executemany() is slower by up to 40%.
        # res = self._conn.executemany('INSERT OR REPLACE INTO dict VALUES (?, ?)',
        #                            ((k[0], self._pack_value(k[1])) for k in d.iteritems()))

#    def pop(self, key, default=None):
#        try:
#            value = self[key]    # will call __getitem__()
#        except KeyError:
#            if default is None:
#                raise
#            else:
#                value = self.get(key, default)
#        else:
#            del self[key]
#        return value

    # --- dict read methods ---

    def __getitem__(self, key):
        """Get one dictionary item"""
        # ~400 getitem() per second
        self.check_and_connect()
        res = self._query('SELECT value FROM dict WHERE key=?;', (key,),
                          func=lambda qry: qry.fetchone())

        if res is None:
            raise KeyError(key)

        return self._unpack_value(res[0])

    def get(self, key, default=None):
        """standard dict().get() method"""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def iterkeys(self):
        """Returns a list of keys"""
        return list(self.keys())

    def viewkeys(self):
        """Returns a set of keys"""
        return set(self.keys())

    def keys(self):
        """
        Returns iterator of keys.
        Use with caution since this will not create exclusive read lock!
        It is recommended to wrap this in 'with ReadTouchFile'
        """
        # Note: db will be locked (writes will wait) during iteration
        return (x[0] for x in self._query('SELECT key FROM dict;'))

    def itervalues(self):
        """Returns a list of values"""
        return list(self.values())

    def viewvalues(self):
        """Returns a set of values"""
        return set(self.values())

    def values(self):
        """
        Returns iterator of values
        Use with caution since this will not create exclusive read lock!
        It is recommended to wrap this in 'with ReadTouchFile'
        """
        # Note: db will be locked (writes will wait) during iteration
        return (self._unpack_value(x[0]) for x in self._query('SELECT value FROM dict;'))

    def iteritems(self):
        return list(self.items())

    def viewitems(self):
        return set(self.items())

    def items(self):
        """
        Returns iterator of (key,value) tuple
        Use with caution since this will not create exclusive read lock!
        It is recommended to wrap this in 'with ReadTouchFile'
        """
        # Note: db will be locked (writes will wait) during iteration
        # Performance: 1.4M iteritems() HSW TRC: 35 sec
        return ((x[0], self._unpack_value(x[1]))
                for x in self._query('SELECT key,value FROM dict;'))

    def has_key(self, key):
        return key in self    # this will call __contains__

    def __contains__(self, key):
        self.check_and_connect()
        res = self._query('SELECT key FROM dict WHERE key=?;', (key,),
                          func=lambda qry: qry.fetchone())
        return not bool(res is None)

    def __len__(self):
        return self._query('SELECT count(key) FROM dict;',
                           func=lambda qry: qry.fetchone())[0]

    def __del__(self):
        """Destroy object"""
        if hasattr(self, "_conn"):
            self._conn.close()   # close db

    def __str__(self):
        return str(dict(self))

    def __iter__(self):
        """object Iterator"""
        for key in list(self.keys()):    # with read-lock
            yield key

    # --- more public methods ---

    def commit(self):
        """Force commit. Database is still open."""
        for i in range(self._cfg.commit_loopcount()):
            try:
                self._conn.commit()   # commit
                return i              # return upon success
            except sqlite3.OperationalError:
                # print "oops commit", i  #debug
                sleep(0.5)
        else:
            raise Exception("Error: Unable to commit data")

    def query_startswith(self, key_startswith):
        """Returns a dictionary given key_startswith string. This is fast. Case-sensitive"""
        def func(qry):
            return {x[0]: self._unpack_value(x[1]) for x in qry}
        return self._query('SELECT key,value FROM dict where key GLOB "%s*";' % key_startswith,
                           func=func)

    def query_like(self, key_like):
        """Returns a dictionary given key_like string. Note: This is not indexed"""
        def func(qry):
            return {x[0]: self._unpack_value(x[1]) for x in qry}
        return self._query('SELECT key,value FROM dict where key LIKE "%s";' % key_like,
                           func=func)

    def batch(self):
        """
        Returns a context manager that will lock the database for batch writing.
        Don't forget to commit() before end of with() statement
        Usage:
            db = SqlDict('file.sql')
            with db.batch():            # Will lock the db for writing
                db['key'] = 'value'     # this is not committed yet to db.
                db.commit()             # Need to commit the database before exiting with!

        """
        return _SqlLock(self.dbfile(), self)

    def dbfile(self):
        """Returns the dbfile. This is also used as argument to Lock() class."""
        return self._dbfile

    def update_withlock(self, item, value):
        """Update one record with lock - recommended way to write"""
        with Lock(self.dbfile(),
                  sleepsec=self._cfg.lock_sleep,
                  timeout=self._cfg.lock_timeout,
                  maxlocktime=self._cfg.lock_maxlock):   # lock will be removed on next run
            self[item] = value    # this will commit to db

    # --- touch dir routines ---

    def _read_touch_dir(self):
        """Initialize the read_touch file and directory"""
        touchdir = join(self._dbrootdir, 'READTD_%s' % basename(self._dbfile))
        if not isdir(touchdir):
            try:
                mkdirs(touchdir, mode="02777")
            except BaseException:     # it's ok if dir can't be created
                pass

        if isdir(touchdir):
            uname = '%s_%s_%s' % (HOSTNAME, os.getpid(), basename(sys.argv[0])[:3])
            return join(touchdir, uname)

        return None     # None

    def set_max_read_time(self, value):
        """Set the max read time for wait_read_complete"""
        self._cfg.max_read_time = value

    def get_dbrootdir(self):
        """Return the db root dir"""
        return self._dbrootdir

    def get_dbfile(self):
        """Return the full path of db file"""
        return self._dbfile

    def get_dbdir(self):
        """Return the db directory"""
        return dirname(self._dbfile)

    # --- fetch routines ---

    def fetch(self, seqkeys):
        """
        Return a new (normal) dictionary of (key,value) given a sequence of keys (set,list,iterator)
        Missing keys are ignored
        """
        # performance: 2.1 sec to query 5000 records, still 2.7 seconds for 50k records
        #              5.6 sec to query 62K records on plxs071 (slow) for 1.1M records (traces)
        #              1.7 sec (cached) for same query as above on plxs070
        # using fetch2 is 6.2 seconds (slower)

        if len(seqkeys) == 0:
            return {}   # empty dict

        # determine the initial set
        firstkey = firstitem(seqkeys)
        if isinstance(firstkey, str) or isinstance(firstkey, str):
            seqkeys = {str(x) for x in seqkeys if x is not None}    # convert to non-unicode for py2 since unicode is slow in py2
            self._ut_plainset = {x for x in seqkeys if self._re_no_special_char.search(x)}   # no special char
        else:
            self._ut_plainset = {x for x in seqkeys if x is not None}   # make it a set, as-is

        self._ut_otherset = {x for x in set(seqkeys) - self._ut_plainset if x is not None}

        # plain strings - use string concat. This is "SQL injection" safe since special char are using _fetch2()
        sql_in = ','.join('%r' % x for x in self._ut_plainset)
        sql = 'SELECT key,value FROM dict where key in (%s);' % sql_in

        self.reconnect()

        def func(qry):
            return {x[0]: self._unpack_value(x[1]) for x in qry}
        res = self._query(sql, func=func)

        if len(self._ut_otherset):
            res.update(self._fetch2(self._ut_otherset))

        return res

    def _fetch2(self, setkeys, _maxn=999):
        """
        Return a new (normal) dictionary of (key,value) given a set of keys
        The keys here are keys with special characters as defined in self._re_no_special_char
        """
        # Algo below (excluding _proc_fetch()) is 10M setkeys in 1.3 secs
        chunk = []
        final = dict()
        for n, data in enumerate(setkeys, start=1):
            chunk.append(data)
            if n % _maxn == 0:
                final.update(self._proc_fetch(chunk))
                chunk = []

        if len(chunk):
            final.update(self._proc_fetch(chunk))

        return final

    def _proc_fetch(self, chunk):
        """Given a set of keys, return a dictionary of results"""
        # This is already wrapped in with ReadTouchFile
        sql = ('SELECT key,value FROM dict where key in (%s);'
               '' % ','.join('?' for i in chunk))

        def func(qry):
            return {x[0]: self._unpack_value(x[1]) for x in qry}
        return self._query(sql, list(chunk), func=func)


class PartialCache:
    """
    Partial object - for cache
    """
    _BASE = SqlDict
    _GETITEM = SqlDict.__getitem__
    _SETITEM = SqlDict.__setitem__
    _DELITEM = SqlDict.__delitem__
    _CONTAINS = SqlDict.__contains__

    def _more_inits(self):
        self._cache = {}

    def __getitem__(self, key):
        """Get one dictionary item - check cache first"""
        if key not in self._cache:
            # print "Getting", key
            self._cache[key] = self._GETITEM(key)

        return self._cache[key]

    def __setitem__(self, key, value):
        """Set one dictionary item - assign to cache"""
        self._SETITEM(key, value)
        self._cache[key] = value

    def __delitem__(self, key):
        """Delete one dictionary item - delete also in cache"""
        self._DELITEM(key)
        if key in self._cache:
            del self._cache[key]

    def __contains__(self, key):
        """<key> in obj method - check cache first"""
        if key in self._cache:
            return True
        return self._CONTAINS(key)

    def update(self, d, cnk=0):
        """Standard dict().update method"""
        self._BASE.update(self, d)
        self._cache.update(d)    # add to cache

    def fetch(self, seqkeys):
        """
        Return a new (normal) dictionary of (key,value) given a sequence of keys (set,list,iterator)
        Missing keys are ignored
        """
        res = self._BASE.fetch(self, seqkeys)
        self._cache.update(res)
        return res

    # --- cache methods ---

    def cache_count(self):
        """Return the count / length of cache dictionary"""
        return len(self._cache)

    def cache_clear(self):
        """Clear the cache"""
        self._cache = {}
        self.reconnect()

    def cache_delete(self, item):
        """Delete one entry in cache"""
        if item in self._cache:
            del self._cache[item]

    def cache_preread_or_init(self, item, initvalue):
        """
        Read the item. If item not in db, then assign initvalue to cache for future write
        initvalue is not written in db yet
        """
        try:
            self.__getitem__(item)
        except KeyError:
            self._cache[item] = initvalue


class SqlDictCached(PartialCache, SqlDict):
    """
    SqlDict with cache capability.
    That is, the values are cached when they are accessed.

    Note: it's possible that the database got updates from another process...
    With this class, those updates won't reflect since data is stored in memory
    The caching is not the same as shelve's writeback.

    """
    pass


# TODO: implement SqlDictWriteBack, inherit from SqlDictCached:
#    Strategy: Use _cache dictionary for records to writeback. Empty this upon sync()
#    1. on cache_clear(), then call sync() first
#    2. sync() will write all the data in _cache if md5() of pickle.dumps is different
#           also, call commit() and empty _cache={}
#    3. override _batch_exit() such that, if len(_cache)>0 then error out. User has to call sync
#       implicitly:
#            res = SqlDictCached._batch_exit(self)
#            <code to check syncmodified>
#            return res    # res is None for success
#    4. Add in __del__() to raise exception if len(_cache)>0 (Force user to add it).


class SqlOperation:
    """
    Various SQL operations
    """

    def __init__(self, sqlfile, disp=False):
        self.set_disp = disp
        self.sqlfile = sqlfile

    def disp(self, txt):
        """Display info"""
        if self.set_disp:
            log.info(txt)

    def get_used_pages(self):
        """Return the used pages"""
        tdb = sqlite3.connect(self.sqlfile, timeout=30)
        c = tdb.execute('pragma page_count')
        res = c.fetchone()
        total = res[0]

        c = tdb.execute('pragma freelist_count')
        res = c.fetchone()
        free = res[0]
        self.disp('Total page: {} free page: {}, Used page: {}'.format(total, free, total - free))
        del tdb

        return total - free

    def get_frag(self):
        """
        Return SQL fragmentation percentage (float)

        Get the fragmentation of a db by:
        1. get the used pages
        2. copy db to a tmp dir
        3. vacuum
        4. get the used pages
        """
        with TempDir(name=True) as tdir:
            self.disp("Copying db to tempdir: {}".format(tdir))
            f1 = File(self.sqlfile).copy(tdir)
            dbfile = f1.get_name()
            dbs = SqlOperation(dbfile)
            used_orig = dbs.get_used_pages()

            # vacuum
            self.disp("Vacuuming {}".format(dbfile))
            tdb = sqlite3.connect(dbfile, timeout=30)
            c = tdb.execute('vacuum')
            c.fetchone()
            del tdb     # close connection

            used_new = dbs.get_used_pages()
            return (1 - float(used_new) / used_orig) * 100.0

    def journal_exist(self):
        """
        returns True if journal file exist.
        This routine will refresh filer because of os.listdir() operation
        """
        journal = "%s-journal" % basename(self.sqlfile)
        return bool(journal in os.listdir(dirname(self.sqlfile)))


class _SqlLock(Lock):
    """Lock context manager used during SqlDict.batch()"""

    def __init__(self, lockfile, db):
        self._db = db
        Lock.__init__(self, lockfile,
                      sleepsec=db._cfg.lock_sleep,
                      timeout=db._cfg.lock_timeout,
                      maxlocktime=db._cfg.lock_maxlock)    # lock will be removed on next run

    def __enter__(self):
        """Start of context manager - set commit to false and lock the database"""
        self._db._batch_enter()
        Lock.__enter__(self)
        return self   # return lock object

    def __exit__(self, exc_type, exc_value, traceback):
        """
        End of context manager - just remove the lock
        """
        error_message = self._db._batch_exit(exc_value)
        if error_message is not None:
            Lock.__exit__(self, exc_type, exc_value, traceback)   # unlock it
            raise Exception(error_message)

        Lock.__exit__(self, exc_type, exc_value, traceback)    # unlock it
