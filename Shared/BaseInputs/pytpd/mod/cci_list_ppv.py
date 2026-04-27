#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Procedure to add new repo (no code change needed).
1. git clone <repo> using your username in some temp folder
2. as p6vector, copy the cloned repo (step1 above) using:
   cp -pdr <source> /nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts
3. edit config.json file and put the repo path in step2
4. Test cgi make sure it works well

TODO:
Show the last PR number from git log of table.
Correct order on bundle
Redo query so it will just call twice only!
gh pr list --json number,reviews,state,isDraft -B TP/21G -s closed
gh pr list --json number,reviews,state,isDraft -B TP/21G -s open
"""
import os
import json
import time
from datetime import datetime
from gadget.shell import SystemCall
from gadget.files import File, TempName
from gadget.printmore import disp
from gadget.strmore import to_str, utc2local, curtime
from gadget.errors import confirm
from gadget.lockfile import force_refresh, Lock
from gadget.getgit import GetCmd
from gadget.disk import mkdirs, Chdir
from gadget.tputil import OtplFile, get_modulename
from tp.testprogram import TestProgram, Env
from collections import OrderedDict, defaultdict
from pprint import pprint, pformat
import re
import glob


class DivHide:
    """Create a div wrapper and hide it at end"""
    def __init__(self, default='', pre=False):
        self.default = f'status{default}'
        self.pre = pre

    def __enter__(self):
        """Executed upon entry to with block"""
        print(f'<div id="{self.default}">')
        if self.pre:
            print('<pre>')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Executed upon closure of with block"""
        self.close()

    def close(self):
        """closure code - Hide the status"""
        if self.pre:
            print('</pre>')
        print(f"""
</div>
<script>
    var myDiv = document.getElementById("{self.default}");
    myDiv.style.display = "none";
</script>
        """)


class CCI:
    """CCI PR report"""
    tag_cache_dir = '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/tag_cache'
    configjson = '/p/pde/tvpv/tvpvweb/cgi-bin/pr-report/config2.json'   # see docstring for setup instructions
    OPT = {}    # assigned by cgi

    def __init__(self, base_branch, rows, prtype=None, repo=None, disp=True):
        """
        :param base_branch: TP/37
        """
        self.base_branch = base_branch
        self.rows = rows
        self.prtype = prtype

        # main dictionary
        # {PRNO: {'openclose': 'draft|open|closed|merged',
        #         'approved': 'Approved|Need_Review',  # This field is optional, for open only
        #         'merge_age': seconds,
        #         'update_age': seconds,
        #         'labels': set_of_labels,
        #         'title': string,
        #         '<gh_output_attribute>': <value>
        self.data = None

        self.repo = repo if repo else 'mtlp68'    # default
        self.isdisp = disp
        self.cfg = None     # configuration dictionary. Set in read_config()

    def main_init(self):
        """Initialize self.data"""
        self._set_all_pr()
        self._set_tags_list()
        self._set_open_close()
        self._set_approved()
        # self._check_valid_branch()

    def disp_status(self, msg):
        """Display status if set"""
        if self.isdisp:
            print(f'{msg}<br>')

    def _check_valid_branch(self):      # pragma: no cover  - under development
        """
        Check if base_branch is valid, and display valid branches (and show also the last commit on RC branch)
        This require a repo that is up-to-date (git pull)

        :return:
        """
        if self.data:
            return    # good to go

        # check if base branch is valid
        _, out, serr = SystemCall('git branch -al').run_sout_serr()
        if f'origin/{self.base_branch}' in out:
            return     # valid

        print(f"Error: {self.base_branch} is not a valid branch name.<br>")
        exit(1)

    def _get_draft(self):
        """
        Return dictionary set of PR number that is draft
        :return:
        """
        self.disp_status("Reading drafts")
        cmd = f"/usr/intel/bin/gh pr list -L {self.rows} -B {self.base_branch} -s open"
        with TempName(name=True) as fname:
            SystemCall(cmd).run_outfile(fname)
            with open(fname, 'rb') as fh:
                data = to_str(fh.read())     # So that unicode are ignored

        result = set()
        for line in data.split('\n'):
            if line.strip().endswith('DRAFT'):
                result.add(int(line.split()[0]))
        return result

    def _set_approved(self):
        """
        Set the approved field
        :return:
        """
        self.disp_status(f"Getting all open PRs")
        for item in self._call_pr_list('open', fields='number,reviews'):
            pr = item['number']
            result = 'Need_Review'
            for review in item.get('reviews', []):
                if review.get('state') == 'APPROVED':
                    result = 'Approved'
            if pr in self.data:
                self.data[pr]['approved'] = result

    def _call_pr_list(self, prtype, fields='mergedAt,number,title,author,labels,closed,url,updatedAt,body'):
        """
        Call gh pr list
        Note: This is sorted according to PR number. If there is a PR that is old but recently merged,
        it may not show up if number of rows is small enough.

        :param prtype: open|all|merged
        :return: list
        """
        if self.OPT.get('PR_CNT') == 'DETAIL':      # pragma: no cover - used in PR_CNT only
            fields = f'{fields},changedFiles'
        if self.OPT.get('milestone'):
            fields = f'{fields},milestone'
        with TempName(name=True) as fname:
            cmd = (f"/usr/intel/bin/gh pr list -s {prtype} -B {self.base_branch} -L {self.rows} "
                   f"--json {fields}")
            SystemCall(cmd).run_outfile(fname)
            with open(fname, 'rb') as fh:
                try:
                    return json.loads(fh.read())
                except json.decoder.JSONDecodeError:
                    return []    # on cases of failure

    def _set_all_pr(self):
        """
        return dictionary (ordered): {pr#: {data}}

        :return: dictionary
        """
        result = OrderedDict()    # So that order is maintained
        curtime = self.get_curtime()

        self.disp_status("Getting all PR's")
        if self.prtype is None:
            data_json = self._call_pr_list('open')
        else:
            data_json = self._call_pr_list(self.prtype)

        # do with everything
        if self.prtype is None:
            tmp_json = self._call_pr_list('merged')
            data_json.extend(tmp_json)

        # Uncomment below to create testcase using real data
        # File('/nfs/pdx/disks/mpe_mtl_015/mtl/unittests/cci_pr/new_case.json').write(json.dumps(data_json, indent=3))

        for item in data_json:

            # redo labels
            labels = {x['name'] for x in item['labels']}
            item['_orig_labels'] = item['labels']
            item['labels'] = labels   # replace it

            # Add merge_age and update_age
            if 'mergedAt' in item and item['mergedAt']:
                item['merge_age'] = curtime - utc2local(item['mergedAt']).timestamp()
            item['update_age'] = curtime - utc2local(item['updatedAt']).timestamp()
            pr = item['number']

            result[pr] = item

        # assign
        self.data = result

    def _set_tags_list(self):
        """Getting the tag from the github and set it to the PR data."""
        list_tag = []
        tag_branch = self.cfg.get('tagstart', 'TP_')
        self.disp_status(f"Getting tag list...")
        with TempName(name=True) as fname:
            cmd = f'git tag --list \'{tag_branch}*\' --format \'%(refname:short) %(objectname) %(subject)\''
            SystemCall(cmd).run_outfile(fname)
            with open(fname, 'r') as fh:
                fline = fh.readlines()
            for line in fline:
                tag = self._get_tag_prno(line.strip())
                list_tag.append(tag)
        return list_tag

    def _get_tag_prno(self, line):
        """Get the tag from line and assign the prno"""
        if not line:
            return None

        tag = line.split()[0]
        found = False
        for prno in re.findall(r"#(\d+)", line):
            if int(prno) in self.data:
                self.data[int(prno)]['tags'] = tag
            found = True

        if not found:
            # Try cache area
            tpath = f'{self.tag_cache_dir}/{self.repo}/{tag.replace("/", "_")}'
            if os.path.exists(tpath):
                found = True
                iprno = int(File(tpath).read().strip())
                if iprno in self.data:
                    self.disp_status(f'Found {tag} in {tpath} \n')
                    self.data[iprno]['tags'] = tag
                    return tag
            else:
                # Try looking for tag in log file
                cmd = f'git log {tag} -n 5'
                self.disp_status(f'{cmd}')

                with TempName(name=True) as fname:
                    SystemCall(cmd).run_outfile(fname)
                    with open(fname, 'rb') as fh:
                        tline = to_str(fh.read())     # So that unicode are ignored

                for prno in re.findall(r"#(\d+)", tline):
                    found = True
                    if int(prno) in self.data:
                        self.data[int(prno)]['tags'] = tag
                        File(tpath).touch(prno, mkdir=True)    # Save to cache
                        return tag    # First one

        if not found:
            self.disp_status(f'tag={tag} has no pr-number. Pls manually assign pr-number in {tpath}')

        return tag

    def _set_open_close(self):
        """
        Set the openclose attribute: draft|open|closed|merged
        :return:
        """
        pr_draft = self._get_draft()

        for pr in self.data:
            if self.data[pr]['mergedAt'] is None:
                if not self.data[pr]['closed']:
                    if self.data[pr]['number'] in pr_draft:
                        # disp(f'draft: {pr}')
                        self.data[pr]['openclose'] = 'draft'
                    else:
                        self.data[pr]['openclose'] = 'open'
                else:
                    # disp(f'closed: {pr}')
                    self.data[pr]['openclose'] = 'closed'
            else:
                self.data[pr]['openclose'] = 'merged'

            confirm('openclose' in self.data[pr],
                    f'Missing openclose status for {pr}',
                    'set_open_close() algo error! contact jqdelosr.')

    def get_prs(self, state):
        """
        :param state: Either draft|open|closed|merged
        :return:
        """
        confirm(state in 'draft open closed merged'.split(),
                f'Invalid input: {state}', 'Fix input')
        for pr in self.data:
            if self.data[pr]['openclose'] == state:
                yield pr

    @classmethod
    def get_curtime(cls):
        """For unitest"""
        return time.time()

    def read_config(self, valid_list=False, repopath=None):
        """
        Set config

        :param: valid_list: Set to True to return entire data (all repos) instead of just one target repo data
        :return: unittest code only
        """
        if self.cfg:
            return 0    # Do nothing, it is already set

        if repopath:     # special - command line, current directory
            self.cfg = {"repopath": ".", "email": "adhoc@intel.com"}

            # make sure proxy is set to gh will work
            confirm('https_proxy' in os.environ,
                    'https_proxy is not set',
                    'source /intel/engineering/dev/team_classtp/torch/ctp_runner/proxy.cshrc')
            # make sure cwd is a repo
            confirm(os.path.isdir('.git'),
                    f'cwd is not a git repo: {os.getcwd()}',
                    'Make sure cwd is a git repo')
            return 2

        with open(self.configjson) as fh:
            data = json.load(fh)
        if valid_list:
            return data
        if self.repo not in data:
            print('Error: %s is not valid repo. Valid are: <br>\n%s' %
                  (self.repo, '<br>\n'.join(sorted(data))))
            exit(1)

        self.cfg = data[self.repo]
        return 1

    def set_chdir(self):
        """Chdir to the repo. Note: Repo must be owned by p6vector since web is p6vector"""
        os.chdir(self.cfg['repopath'])

    @classmethod
    def main_set_ready(cls, pr, repo='mtlp68'):      # pragma: no cover  - will test later
        """
        Add the ready label given pr number

        :param pr: number
        :param repo: repo
        :return:
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic'}
        proxy = {'http': '', 'https': ''}
        response = requests.get(f'https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?repo={repo}&br={pr}',
                                headers=headers, proxies=proxy, verify=False)
        print(f'Status: {response.status_code}')
        print(response.text)
        return response

    def _git_pull(self, submodule=False, interval=2 * 3600):
        """Do a git pull once every 2 hours"""
        cwd = os.getcwd()
        age = os.path.getmtime(cwd)
        if (time.time() - age) > interval or self.OPT.get('pull'):
            Lock.newline = '<br>'
            self.disp_status('Please wait...')
            with Lock(f'{cwd}/lock.txt', timeout=10 * 60, maxlocktime=5 * 60):
                self.disp_status('Performing git pull to get tags.')
                force_refresh(cwd)

                if submodule:
                    cmd = f"/usr/intel/pkgs/git/2.23.0/bin/git submodule update --init --recursive"
                    self.disp_status(cmd)
                    for line in SystemCall(cmd).run_stream():
                        self.disp_status(line)

                cmd = f"/usr/intel/pkgs/git/2.23.0/bin/git pull"
                for line in SystemCall(cmd).run_stream():
                    self.disp_status(line)

                cmd = f"/usr/intel/pkgs/git/2.23.0/bin/git fetch --tags --force"
                for line in SystemCall(cmd).run_stream():
                    self.disp_status(line)

                return 1

        return 0

    def _process_bundle(self):
        """Update self.data for bundle PR, force PASSED_Si so it does not show as manual"""
        for pr in self.get_prs('merged'):
            title = self.data[pr]['title']
            if title.startswith('bundle of'):
                _, prs = title.split(':')
                for bundle in prs.strip().split():
                    bno = int(bundle)
                    if bno in self.data:
                        # so that bundle will not show manual
                        self.data[bno]['labels'].add('PASSED_Si')
                        # So that child PR will go before bundle
                        self.data[bno]['merge_age'] = self.data[pr]['merge_age'] + 1

    def _manual_status(self, labels):
        """
        :param labels: list of labels
        :return: manual status string
        """
        # determine manual
        manual = ''   # Default Manual
        if 'PASSED_Si' in labels:
            manual = ''      # Bot passed
        if 'I_AM_TPI_Skip_Bot' in labels:
            manual = ' BotSkip'
        return manual

    def _diebins_status(self,
                        body,
                        milestone={},    # dictionary with 'title' key
                        _r1=re.compile(r"Which Die is affected(.*?)\?(.*)", re.DOTALL),
                        _r2=re.compile(r"What Bin\S+ are affected(.*?)\?(.*)", re.DOTALL)
                        ):
        """Returns the diebins string, based on PR description"""
        final = []

        # Die
        res = _r1.search(body)
        if res:
            for line in res.group(2).split('\n'):
                line = line.strip()
                if not line:
                    continue
                if '?' in line:
                    break    # answer was not specified
                final.append(line.split()[0].strip()[:5])      # first 5 chars, no spaces
                break

        # bin
        res = _r2.search(body)
        if res:
            for line in res.group(2).split('\n'):
                line = line.strip()
                if not line:
                    continue
                if '?' in line:
                    break    # answer was not specified
                final.append(line.replace(' ', '').strip()[:7])       # first 7 chars, no spaces, max 2 bins
                break

        if milestone:
            final.append(milestone.get('title', ''))

        return ', '.join(final)

    def _title(self, title, labels,
               _ro=re.compile('(PORTP|Uservar|ProgramFlows|BinDefinitions|Env|TPConfig|Misc|Shared)')):
        """Returns the title, max of 80 chars, with additional info from labels"""
        info = set()
        for label in labels:
            if _ro.search(label):
                info.add(label.split('_')[0][:4])

        if info:
            final = ','.join(sorted(info))
            title = title[:80 - 3 - len(final)]
            return f'{title} [{final}]'

        title = title[:80]
        return title   # as-is

    def _module_status(self,
                       labels,
                       _ro=re.compile('(PORTP|Uservar|ProgramFlows|BinDefinitions|Env|TPConfig|Misc|Shared|'
                                      'BUNDLE|FAILED|READY|PASSED|TEST_IN_PROGRESS|I_AM_TPI_Skip_Bot)')):
        """Returns the module column based on labels"""

        team = set()
        for label in labels:
            if _ro.search(label):
                continue
            if label.startswith('FB'):
                continue
            element = label.split('_')[0]
            if element == 'I':
                continue
            team.add(element[:4])

        # max of 3
        if len(team) > 3:
            final = sorted(team)[:3]
            final.append(f'+{len(team)-3}')
        else:
            final = sorted(team)

        return ','.join(final)

    def _label_status(self, status, labels):
        """Update status given labels"""
        for label in sorted(labels):
            # partial string matches
            if 'FAILED' in label or 'READY' in label or label.startswith('FB'):
                status.append(label)

            # exact string matches
            if label in ('TEST_IN_PROGRESS', 'PASSED_Si'):
                status.append(label)

            # renamed labels
            if label == 'I_AM_TPI_Skip_Bot':
                status.append('BotSkip')

        if 'PASSED_Chk' not in labels:
            status.append('Missing_Chk')

    def _help(self):
        """Help if no args provided"""
        if self.base_branch:
            return

        repo_list = '\n   '.join(sorted(self.read_config(valid_list=True)))
        print(f"""<pre>
cci_list.cgi?br=TP/tprev is required in url argument.

Options:
   repo=(reponame, see below for valid list)
   rows=(int, number of rows, default=50)
   pull=True          # Set to True to refresh repo, specially for newer tags
   tz=16              # Set timezone to PG

Valid repo values:
   {repo_list}

</pre>""")
        exit(0)

    def main(self, cmd_prcnt=None):    # set cmd_prcnt='.'
        """Main entry point"""
        self._help()
        self.read_config(repopath=cmd_prcnt)
        self.set_chdir()

        with DivHide():
            self._git_pull()
            self.main_init()        # get all PR, set all attributes
            self._process_bundle()
            data = self.data

        # Table ==============================
        today = datetime.now()
        header1 = f'{self.base_branch} CCI Report Status {today}'
        headerstyle = "<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>"
        stylerow = f"<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'>"
        table = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"
        table += f"<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'><pre>{header1}</pre></td></tr>"

        header = f"""
        <td>PR #</td>
        <td>Title</td>
        <td>Tags</td>
        <td>Submitted By</td>
        <td>Merged At</td>
        </tr>\n"""

        # OPEN PR ==============================================
        open_PR = list(self.get_prs('open'))
        table += f"{stylerow}Total Open PRs: {len(open_PR)} </td></tr>\n"
        table += f"{headerstyle}\n"
        table += f"{header.replace('Merged At', 'Status')}\n"
        for pr in sorted(open_PR, key=lambda x: data[x]['update_age']):
            title = self._title(data[pr]['title'], data[pr]['labels'])
            owner = data[pr]['author']['login'][:20]
            url = data[pr]['url']
            tag = data[pr].get('tags', ' ')
            module = self._module_status(data[pr]['labels'])
            diebins = self._diebins_status(data[pr].get('body', ''), data[pr].get('milestone', {}))

            # show also labels
            status = [f"{data[pr]['update_age']/86400:.1f} days old, {data[pr]['approved']}"]
            self._label_status(status, data[pr]['labels'])

            table += f"""<tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td>{pr}</td>
                <td><a href='{url}'>{title}</a></td>
                <td>{tag}</td>
                <td>{owner}</td>
                <td>{', '.join(status)}</td>
            </tr>\n"""

        # MERGED PR ==============================================
        closed_PR = list(self.get_prs('merged'))
        table += f"{stylerow}Merged PRs</td></tr>\n"
        table += headerstyle
        table += header
        prevtag = 'WIP'    # change this to self.base_branch for pre-CCI
        cnt_tag = defaultdict(list)
        cnt_date = {}
        for pr in sorted(closed_PR, key=lambda x: data[x]['merge_age']):
            title = self._title(data[pr]['title'], data[pr]['labels'])
            owner = data[pr]['author']['login'][:20]
            url = data[pr]['url']
            date_var = data[pr]['mergedAt']
            merge_time = utc2local(date_var, tzoffset=int(self.OPT.get('tz', 0)))
            tag = data[pr].get('tags', ' ')
            manual = self._manual_status(data[pr]['labels'])

            # Convert timezone of datetime from UTC to local
            age = f"{data[pr]['merge_age']/86400:.1f} days ago: {merge_time}"

            table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td>{pr}</td>
                <td><a href='{url}'>{title}</a></td>
                <td>{tag}</td>
                <td>{owner}</td>
                <td>{age}{manual}</td>
            </tr>\n"""

            # Do counting
            if tag.strip():
                prevtag = tag
                cnt_date[prevtag] = age
            cnt_tag[prevtag].append((pr, title, data[pr]['labels'], owner, data[pr].get('changedFiles')))

        table += "</table>\n"    # <td>{dt_local}</td>

        # To summarize above data, across multiple .csv (one .csv one product),
        # Run below code in demo.py to add the filename at the end, so that you can pivottable
        # for ff in sys.argv[1:]:
        #     for line in File(ff).chomp():
        #         print(f'{line}, {ff.replace(".csv", "")}')

        # cnt mode - called from pr_cnt
        if cmd_prcnt == 'SUM':
            result = []
            for tag in [x for x in sorted(cnt_tag) if x != 'WIP']:
                result.append(f"{tag}, {cnt_date.get(tag, 'None None').split()[-2]}, {len(cnt_tag[tag])}")
            return "TP, date, PR_count", result

        if cmd_prcnt == 'DETAIL':
            result = []
            for tag in [x for x in sorted(cnt_tag) if x != 'WIP']:
                for item in cnt_tag[tag]:
                    title = item[1].replace(',', ' ')
                    result.append(f"{tag}, {cnt_date.get(tag, 'None None').split()[-2]}, {item[0]}, {item[4]}, {item[3]}, {title}")
            return "TP, date, pr_no, changedFiles, author, title", result

        if cmd_prcnt == 'TEAM':
            result = []
            for tag in [x for x in sorted(cnt_tag) if x != 'WIP']:
                for item in cnt_tag[tag]:
                    title = item[1].replace(',', ' ')
                    for label in sorted(item[2]):
                        team = label.split('_')[0]
                        if team not in ('I', 'PASSED', 'FAILED', 'AAREADY', 'READY', 'BUNDLE'):
                            result.append(f"{tag}, {item[0]}, {team}, {label}, {title}")
            return "TP, pr_no, team, label, title", result

        # Display it!
        print(f"""
<html style="font-family: Calibri; font-size: 15px;">
<head>
<title>{header1}</title>
</head>
<body>
<h1>{table}</h1>
<h2 style = 'font-size: 15px;'>
To increase row count, add '&rows=100' in url. Default is {self.rows}.<br>
For more details, please contact: {self.cfg['email']}</h2>
</body></html>
""")

