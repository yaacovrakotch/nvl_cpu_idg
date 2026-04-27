#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Indicators module - Everything about indicators and getting the data
"""
import re
from gadget.files import File
from gadget.errors import ErrorCockpit, confirm
from gadget.strmore import curtime
from gadget.disk import mkdirs, listdir_noerror
from gadget.pylog import log
from gadget.gizmo import Elapsed
from gadget.getgit import GitHub
from tp.testprogram import Env
from datetime import datetime
from os.path import basename, exists, dirname, isdir
import json
import os
import glob
import time


class Lit:
    """LIT - Load Init Testtime and others"""
    start_build = Elapsed()
    build_time = None

    def __init__(self, dbdir, robot, prno):
        self.dbdir = dbdir
        self.robot = robot
        self.prno = prno
        self.data = {}    # {'load|init|tt': <sec>}

    def one_log(self, logfile):
        """
        Given a load/init/ituff logfile, update self.data
        :param logfile: logfile, either log, init, tt
        :return: dictionary
        """
        if (not self.prno) or (not exists(self.dbdir)):
            return 1    # do nothing (e.g. mrobot)
        if basename(logfile).startswith('CLASSCOLD_'):
            return 2    # do nothing for optional COLD testing

        if 'loadLog_' in basename(logfile):
            category = 'load'
            secs = self.get_time_toslog(logfile)

        elif 'ituff_' in basename(logfile):
            self.data['ituffsize'] = os.path.getsize(logfile)
            category = 'tt'
            secs = self.get_ttime_ituff(logfile)

        elif 'initLog_' in basename(logfile):
            category = 'init'
            secs = self.get_time_toslog(logfile)

        elif 'TestUnitLog_' in basename(logfile):
            return 3    # Do nothing here

        else:
            raise ErrorCockpit(f'File {logfile} is unknown category.',
                               'Pls seek help to make sure logname starts with one of the following: '
                               '(loadLog|ituff|initLog|TestUnitLog)')

        self.data[category] = secs

    def write(self, code):
        """Write the json output file in designated directory"""
        if not self.data:
            log.info('PHI - no data, nothing to write')
            return 1

        if code:
            log.info(f'PHI - Failure [{code}], so not writing')
            return 2

        # add the build time
        confirm(self.build_time is not None, 'set_buildtime_end() was not called!', 'Call set_buildtime_end() first')
        self.data['buildtime'] = int(self.build_time)     # This is tprobot build time

        # Delete any existing PR first before writing (since this cause indicator issue). This happens during draft PR.
        gwild = f'{self.dbdir}/{self.robot}/*/{self.prno}.json'
        for fn in glob.glob(gwild):
            log.info(f'-i- Deleting duplicate: {fn} ')
            File(fn).unlink()

        # Write it
        fname = f'{self.dbdir}/{self.robot}/{curtime(dateonly=True)}/{self.prno}.json'
        mkdirs(dirname(fname), mode='02770')
        with open(fname, 'w') as fh:
            json.dump(self.data, fh, indent=3)

        # Display it
        for key, value in sorted(self.data.items()):
            log.info(f'PHI {key}: {value}')

    @classmethod
    def set_buildtime_end(cls):
        """
        Assign the buildtime
        Call this before running the bot (end of build)
        """
        cls.build_time = cls.start_build.elapsed(pretty=False)    # numeric value

    @classmethod
    def get_time_toslog(cls, logfile, _robj=re.compile(r'^\[(202[^\]\.]+)', re.MULTILINE)):
        """

        :param logfile: input file
        :param _robj: compiled object
        :return: time elapsed in seconds. Returns 0 if none found
        """
        result = _robj.findall(File(logfile).read())
        if len(result) > 1:
            return cls.age_tos_time(result[0], result[-1])
        return 0

    @classmethod
    def age_tos_time(cls, time1, time2):
        """
        Returns the age between two TOS time stamps, in this format: 2023-May-19 15:19:04
        This will error out if the expected format is incorrect (strict)
        """
        try:
            obj1 = datetime.strptime(time1, "%Y-%b-%d %H:%M:%S")
        except ValueError:
            obj1 = datetime.strptime(time1, "%Y-%m-%dT%H:%M:%S")

        try:
            obj2 = datetime.strptime(time2, "%Y-%b-%d %H:%M:%S")
        except ValueError:
            obj2 = datetime.strptime(time2, "%Y-%m-%dT%H:%M:%S")

        return obj2.timestamp() - obj1.timestamp()

    @classmethod
    def get_ttime_ituff(cls, filename):
        """Returns the value from ituff 3_ttime"""
        result = re.findall('^3_ttime_(.*)', File(filename).read(), re.MULTILINE)
        if not result:
            return 0
        return max(float(x) for x in result)


class TPBotFail:
    """
    TPBotFail logging and data extraction

    Dir structure / filename convention:
    {self.root}/{botname}/<prno>_<name>.open.json     # open tpbot fails
    {self.root}/{botname}/<prno>_<name>.json          # dispositioned tpbot fails
    {self.root}/{botname}/<reponame>.product          # product identifier. This is the reponame in cci_list

    Json structure:
    {prno: int,       # this is the type of cci_list's self.data[pr]
     logpath: string,
     time: number_seconds,
     comment: string,               # after disposition
     dispo: 'MV|TRUE|SETUP',        # after disposition
     user: username,                # after disposition
     }

    Strategy:
    1. buildtp Bot() routine will log failing tpbot, by calling one_log()
    2. cci_indicator and cci_cron will access the data
    3. There is mapping on botname to product (which input to cci_list). Print as comment if mapping does not exist.
    """
    ROOTDB = Env.xpath('/intel/tpvalidation/engtools/tptools/mtl/infra/torch/tpbot_fail_db')
    TESTERLOGS = Env.xpath('/intel/tpvalidation/engtools/tptools/mtl/infra/torch/testerload')

    def __init__(self):
        self.root = self.ROOTDB       # so unittest can easily change it

    def one_log(self, all_type_fname, priority, code, robot, prno):
        """
        Log one file. Note: if ituff file exist, then use it (for a tester fail)
        Called from Bot() of buildtp.py

        :param all_type_fname: (type, fname) tuple
        :param priority: list of types in priority
        :param code: boolean
        :param robot: robot name
        :param prno: pr number
        :return: nothing, unittest only
        """
        if not code:
            return 1    # Do not write passing tpbot run

        if not exists(self.root):
            log.info(f'-w- TPBotFail is ignored, root folder not exist: {self.root}')
            return 2

        if robot.startswith('mrobot'):
            return 4     # Do not log mrobot. Reason: I can submit pass or fail in mbot.

        if GitHub.get_pr_info('state') == 'DRAFT':
            log.info(f'-w- TPBotFail is ignored, PR is DRAFT')
            return 5

        for typestr in priority:
            for logtype, fname in all_type_fname:
                if logtype == typestr:    # first occurrence
                    self._log_this(fname, robot, prno)
                    return 4

        log.info(f'-w- TPBotFail.one_log(), no valid log found: {all_type_fname}')
        return 3

    def _log_this(self, fname, robot, prno):
        """
        Write the log file

        :param fname: log fname path
        :param robot: robot name
        :param prno: pr no
        :return:
        """
        rname = basename(fname).split('.')[0]
        targetname = f'{self.root}/{robot}/{prno}_{rname}.open.json'
        mkdirs(dirname(targetname), mode='02770')
        data = {'prno': prno,
                'logpath': fname,
                'time': time.time(),
                'author': GitHub.get_pr_info('author'),
                'title': GitHub.get_pr_info('title')}
        log.info(f'-i- TPBotFail: written: {targetname}')
        with open(targetname, 'w') as fh:
            json.dump(data, fh, indent=3)

    def get_list(self, repo):
        """
        Return "open" pr list
        Called from cci_list.py: tpbot_fails()

        :param repo: repo name from cci_list
        :return: list of {prno, logpath, time, filename: value}
        """
        final = []
        for robot in sorted(os.listdir(self.root)):
            if not isdir(f'{self.root}/{robot}'):
                continue   # look only at folders
            files = sorted(os.listdir(f'{self.root}/{robot}'))

            # check the product first
            skip = False
            found = False
            for ff in files:
                if ff.endswith('.product'):
                    found = True
                    reponame = ff.replace('.product', '')
                    if reponame != repo:
                        skip = True    # skip this folder

            if skip:
                continue

            if not found:   # folder without .product are reported in email (not in cci_list report)
                continue

            for ff in files:
                if not ff.endswith('.open.json'):
                    continue
                with open(f'{self.root}/{robot}/{ff}') as fh:
                    data = json.load(fh)
                data['filename'] = f'{robot}/{ff}'
                final.append(data)

        return final

    def write_dispo(self, fname, comment, dispo, user):
        """
        Rewrite the json with the disposition (and rename it)
        Called from cci_list.py

        :param fname: robot/name.json
        :param comment: string
        :param dispo: string
        :param user: string
        :return: newfname
        """
        # read and update json
        with open(f'{self.root}/{fname}') as fh:
            data = json.load(fh)
        data['comment'] = comment
        data['dispo'] = dispo
        data['user'] = user

        newname = fname.replace('.open.json', '.json')
        with open(f'{self.root}/{newname}', 'w') as fh:
            json.dump(data, fh, indent=3)
        File(f'{self.root}/{fname}').unlink()     # delete old one
        return newname

    def get_all_list(self, robot_list):
        """
        Iterator, yield a dictionary of one fail (open and close) given robot
        It is sorted according to time (latest will show first)
        Called from cci_list.py

        :param robot_list: robot name
        :return: iterator: one record of dict
        open record:          {robot, prno, logpath, time, author, title}
        dispositioned record: {robot, prno, logpath, time, author, title, comment, dispo, user}
        """
        dd = {}   # key is (time, fname)
        for robot in robot_list:
            root = f'{self.root}/{robot}'
            for fname in sorted(listdir_noerror(root)):
                if not fname.endswith('.json'):
                    continue
                with open(f'{root}/{fname}') as fh:
                    data = json.load(fh)
                data['robot'] = robot
                if 'time' in data:
                    dd[(data['time'], fname)] = data

        for key in sorted(dd, reverse=True):
            yield dd[key]
