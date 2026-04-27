#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Connect to each tester and determine last usage.

Usage:
log_tester_usage.py <path_to_config.json> [-x10|-once]

config.json content as follows:
    {
     "logfiles": ["/HDMT3/logs/commonhdmt/hdmtOScommon.log",
                  "/HDMT3/logs/HdmtApp.log"],
     "output_file": "\\RP1SSTTD001\\Telemetry/pdelnew.json",
     "allinfo_file": "\\ra4ssttdsdsdx24\\JF_TesterStatus\\CurrentStatus.txt"
    }

Options:
-x10: Run this script from a x10 DPC machine
-once: Run this script once
"""
from datetime import datetime
from pprint import pprint
import time
import os
import re
import json
import sys
import getpass
import socket


class LogUsage:
    """Log tester usage"""
    # Revision history (This is written in json output) ====================
    # VERSION = '1.0'        # Initial version
    # VERSION = '1.1'        # with -x10 option
    # VERSION = '1.2'        # Fix empty data, use previous
    # VERSION = '1.3'        # Make _INFO to be structured. Feedback by Niels.
    # VERSION = '1.4'        # Fix corner case on 0-10-2023 date due to truncation. Feedback by Rich.
    VERSION = '1.5'          # Add new date format 2025-07-01T11:00:01.580808-07:00

    def __init__(self):
        """Initialize vars"""
        self.logfiles = []    # list of path of log files, relative to the <tester>/<path-of-log-files>
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.output_file = None     # output json file
        self.allinfo_file = None    # Input json file
        self.message = []     # debug messages when something is not right - per machine
        self.data = {}        # {shortname: dict_per_tester}
        self.info = []        # info for machines not running
        self.prev = {}        # {shortname: line}
        self.prevdata = {}    # same as self.data, previous file
        self.sw = time.time()
        self.x10 = False

    def main(self, configjson, maxloop=10000000, nap=60, x10=False, once=False):
        """
        Entry point - infinite loop

        :param configjson: Input configuration file
        :param maxloop: maximum loops - 10000000 is 19 years at 60 sec nap
        :param nap: sleep in seconds between each run
        :param x10: Set to True for x10
        :param once: Set to True for once
        :return: None
        """
        self.x10 = x10
        self.read_configjson(configjson)
        for _ in range(maxloop):
            try:
                self.run()
            except Exception as e:    # pragma: no cover
                print(e)

            if once or self.x10:
                return -1

            print("Sleeping...")
            time.sleep(nap)
        return maxloop

    def read_configjson(self, configjson):
        """Read the config json file"""
        assert os.path.exists(configjson), '[%s] does not exist. First argument must be an existing config json file.' % configjson
        with open(configjson, 'r') as fh:
            data = json.load(fh)
        assert 'logfiles' in data, '[logfiles] is a required key in config file'
        assert 'output_file' in data, '[output_file] is a required key in config file'
        assert 'allinfo_file' in data, '[allinfo_file] is a required key in config file'
        self.logfiles = data['logfiles']
        self.output_file = data['output_file']
        self.allinfo_file = data['allinfo_file']

        if self.x10:
            self.output_file = '%s/%s.json' % (os.path.dirname(self.output_file), socket.gethostname())

    def run(self):
        """Execute one run, all machines"""
        self.data = {}
        self.info = []

        # Read previous data
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as fh:
                prevdata = json.load(fh)
                self.prevdata = prevdata
                self.prev = prevdata.get('_PREV_', {})
        else:
            self.prev = {}
            self.prevdata = {}

        swtop = time.time()
        cnt = 0
        for tester, tiu, location, msglist in self.get_all_testers():
            cnt += 1
            self.sw = time.time()
            key = tester.split(".")[0]
            sys.stderr.write('%s: Contacting %s...\r' % (self.curtime(), key))
            self.message = msglist

            # Run one machine
            try:
                self.run_machine(tester, tiu, location)
                sys.stderr.write('%s: %s: Elapsed: %.3f secs. Last Touch: %s\n' %
                                 (self.curtime(), key, time.time() - self.sw, self.data.get(key, {}).get("last_touch")))
            except Exception as e:
                self.info.append('%s: EXCEPTION: %s' % (tester, e))
                sys.stderr.write('%s\n' % e)

        # Write
        self.data['_INFO_'] = self.build_info(Tester_Count=cnt, Elapsed=int(time.time() - swtop))
        self.data['_PREV_'] = self.prev
        with open(self.output_file, 'w') as fh:
            json.dump(self.data, fh, indent=3)
        print('Elapsed: %.3f Secs. Count=%s. Written: %s' % (time.time() - swtop, cnt, self.output_file))

    def build_info(self, **kwargs):
        """Return dictionary for _INFO_"""
        final = dict(kwargs)
        final['Version'] = self.VERSION
        final['Message'] = self.info
        return final

    def run_machine(self, tester, tiu, location):
        """Run one tester"""
        if self.x10:
            shortname = tester
        else:
            shortname = tester.split('.')[0]
        lastlines = {}      # {fname: lastline}
        sass_cnt = 0
        foundfile = 0

        # Get the valid lastline
        for partialname in self.logfiles:
            fname = self._get_path_file(tester, partialname)
            validline = None
            if os.path.exists(fname):
                foundfile += 1

                # process the log file
                for line in self.get_tail(fname):
                    if '[SASS Alarm]' in line:
                        if validline:    # Ignore if there is a validline already. First SASS Alarm is taken
                            sass_cnt += 1
                            continue
                        else:
                            line = self.prev.get(shortname, '')    # replace the sass line
                    if Deyt.secs(line):
                        validline = line.rstrip()

                if validline:
                    lastlines[os.path.basename(fname)] = validline
                    self.message.append('[%s]: %s' % (os.path.basename(fname), validline))
                else:
                    self.message.append('[%s] No valid date found' % os.path.basename(fname))
            else:
                self.message.append('%s does not exist.' % fname)

        if not foundfile:
            self._append_info_message(shortname)
            self.info.append('%s: None of the logfiles exist' % shortname)
            return
        if not lastlines:
            self._append_info_message(shortname)
            self.info.append('%s: None of the logfiles read (count: %d) has valid date'
                             '' % (shortname, foundfile))
            return

        # Get the latest date
        latest = {}
        latestline = {}
        for fname, line in lastlines.items():
            latest[Deyt.secs(line)] = fname
            latestline[Deyt.secs(line)] = line

        offset = self.get_offset(self._get_path_file(tester, '/HDMT3/logs'))
        latest_sec = max(latest)
        self.set_data(shortname,
                      secs=latest_sec,
                      fname=latest[latest_sec],
                      tiu=tiu,
                      location=location,
                      tester=tester,
                      offset=offset,
                      sass_cnt=sass_cnt)
        # Update the prev line
        if '[PREV:' in latestline[latest_sec]:
            self.prev[shortname] = latestline[latest_sec]
        else:
            self.prev[shortname] = latestline[latest_sec] + (' [PREV:%s] ' % latest[latest_sec])

    def set_data(self, testername, secs, fname, tiu, location, tester, offset, sass_cnt):
        """
        Write one tester data into the data structure
        Make sure data structure is consistent
        """
        data = {}
        data['last_update'] = self.curtime()
        data['message'] = self.message
        data['tester'] = tester
        data['tiu'] = tiu
        data['location'] = location
        data['process_time_secs'] = time.time() - self.sw
        data['offset'] = offset
        data['sass_alarm_count'] = sass_cnt
        data['logfile_source'] = fname
        data['last_touch'] = datetime.fromtimestamp(secs).strftime(self.date_format)

        # pprint(data)
        self.data[testername] = data

    def _append_info_message(self, shortname):
        """Add messages into self.info"""
        for item in self.message:
            self.info.append('%s: %s' % (shortname, item))

    @classmethod
    def _get_path_file(cls, tester, partialname, _b='\\'):
        """
        Return the windows full path of the log file to read
        Mainly intended for easy unittesting

        :param tester: host name
        :param partialname: path to the log file (absolute), starts with /
        :param _b: Fixed string - do not change
        :return: windows full path
        """
        return '%s%s%s%sD$%s' % (_b, _b, tester, _b, partialname)

    def curtime(self):
        """Return the current time"""
        return datetime.now().strftime(self.date_format)

    @classmethod
    def get_tail(cls, file_path, size=4096):
        """
        Efficient way of getting tail of file: grab last 4096 bytes of the file
        Return list of lines
        """
        with open(file_path, 'rb') as file:
            firstblock = file.read(size)
            if len(firstblock) < size:
                block = firstblock.decode('utf-8')
            else:
                file.seek(-size, 2)    # This does not work if size go beyond file size
                block = file.read(size * 2).decode('utf-8')
            # Handle both Windows (\r\n) and Unix (\n) line endings
            return block.replace('\r\n', '\n').split('\n')

    def get_all_testers(self):
        """Iterator: Return list of (testers, tiu, location, [message])"""
        if self.x10:
            for x in range(1, 11):
                ip = '10.250.0.%s' % x
                yield ip, 'tbd', ip, []
            return

        if not os.path.exists(self.allinfo_file):
            self.info.append('Not Exist %s' % self.allinfo_file)
            for item in self._prev_data():
                yield item
            return  # Done

        with open(self.allinfo_file) as fh:
            alltext = list(x.strip() for x in fh)

        found = False
        for line in alltext:
            elems = line.split(',')
            if len(elems) > 4:
                if 'X10HDMT' in elems[1] or 'ICDC' in elems[1]:
                    continue
                if elems[4] != 'DOWN':
                    found = True
                    yield elems[0], elems[2], elems[1], []

        if not found:
            self.info.append('%s is EMPTY' % self.allinfo_file)
            for item in self._prev_data():
                yield item

    def _prev_data(self):
        """Return all previous/existing tester metadata"""
        for key, item in self.prevdata.items():
            if key.startswith('_'):
                continue
            yield item['tester'], item['tiu'], item['location'], ['Using previous tester metadata']

    @classmethod
    def get_offset(cls, path):
        """
        Return the host offset time in seconds
        :param path: root folder, without filename
        :return: offset in seconds. Positive is host is delayed
        """
        try:
            fname = '%s/touchfile_offset_%s.txt' % (path, getpass.getuser())

            starttime = time.time()
            with open(fname, 'w'):
                pass
            endtime = time.time()
            roundtripdelay = endtime - starttime

            mtime = os.path.getmtime(fname)
            os.unlink(fname)

            return time.time() - mtime - roundtripdelay
        except Exception:
            return -1.2345    # special number when things don't work


class Deyt:

    ROBJ1 = re.compile(r"(\d{1,2}\-\d{1,2}\-202\d \d+:\d+:\d+)")    # format1 - fixed to be more specific
    ROBJ2 = re.compile(r"(\d{4}-\w{3}-\d{2} \d+:\d+:\d+)")    # format2 - fixed to handle month names like "Jun"
    ROBJ3 = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[-+]\d{2}:\d{2})")  # format3

    @classmethod
    def secs(cls, line):
        """Returns the secs from the line. Returns 0 if None found"""

        # format1 - removed the problematic condition that skipped 0- dates
        res1 = cls.ROBJ1.search(line)
        if res1:
            return cls.convert1(res1.group(1))

        # format2
        res2 = cls.ROBJ2.search(line)
        if res2:
            return cls.convert2(res2.group(1))

        # format3
        res3 = cls.ROBJ3.search(line)
        if res3:
            return cls.convert3(res3.group(1))

        return 0

    @classmethod
    def convert1(cls, datestr):
        """Convert datestr, in format '06-23-2023 08:13:47' to sec"""
        try:
            # First try standard MM-DD-YYYY format
            obj = datetime.strptime(datestr, '%m-%d-%Y %H:%M:%S')
            return obj.timestamp()
        except ValueError:
            # Handle edge case where leading zero is missing
            # like "0-10-2023" which should be interpreted as "10-10-2023" (October 10)
            parts = datestr.split(' ')
            if len(parts) == 2:
                date_part = parts[0]
                time_part = parts[1]
                date_components = date_part.split('-')
                if len(date_components) == 3:
                    month_str, day_str, year = date_components
                    month = int(month_str) if month_str != '0' else 10  # If month is 0, assume it means October (month 10)
                    day = int(day_str) if day_str != '0' else 10       # If day is 0, assume it means day 10
                    fixed_datestr = f'{month:02d}-{day:02d}-{year} {time_part}'
                    obj = datetime.strptime(fixed_datestr, '%m-%d-%Y %H:%M:%S')
                    return obj.timestamp()
            raise  # Re-raise if we can't fix it

    @classmethod
    def convert2(cls, datestr):
        """Convert datestr in format '2023-Jun-23 08:17:35' to sec"""
        obj = datetime.strptime(datestr, '%Y-%b-%d %H:%M:%S')
        return obj.timestamp()

    @classmethod
    def convert3(cls, datestr):
        """Convert datestr in format '2025-07-01T11:00:01.580808-07:00' to sec"""
        obj = datetime.fromisoformat(datestr)
        return obj.timestamp()


if __name__ == '__main__':  # pragma: no cover
    if '-help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        exit(0)

    assert len(sys.argv) >= 2, 'Incorrect usage!\n\n%s' % __doc__
    LogUsage().main(sys.argv[1],
                    x10='-x10' in sys.argv,
                    once='-once' in sys.argv)
